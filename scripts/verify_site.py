#!/usr/bin/env python3
"""Hugo のビルドと記事追加を、一時ディレクトリで検証します。

Python の標準ライブラリのみ使用します。リポジトリのコンテンツや
public/ は変更しません。実行例: python scripts/verify_site.py --hugo hugo
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urljoin, urlsplit


BASE_URL = "https://USERNAME.github.io/my-portfolio/"
PREFIX = "/my-portfolio/"
MENU = {
    "Home": "",
    "About": "about/",
    "Projects": "projects/",
    "Research": "research/",
    "Awards": "awards/",
    "Publications": "publications/",
    "Contact": "contact/",
}
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 50"><rect width="80" height="50" fill="#ddd"/></svg>'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    children: list[Element | str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(
            child.text if isinstance(child, Element) else child
            for child in self.children
        )).strip()

    def elements(self):
        for child in self.children:
            if isinstance(child, Element):
                yield child
                yield from child.elements()

    def find(self, tag=None, *, class_name=None, id=None):
        return [element for element in self.elements()
                if (tag is None or element.tag == tag)
                and (id is None or element.attrs.get("id") == id)
                and (class_name is None or class_name in element.attrs.get("class", "").split())]


class Document(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.root = Element("document", {})
        self.stack = [self.root]
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        element = Element(tag, {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(element)
        if tag not in self.VOID:
            self.stack.append(element)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def run(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8",
                            errors="replace", capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}\n"
                           f"{result.stdout}{result.stderr}")


def build(hugo: str, source: Path, destination: Path, *, content: Path | None = None,
          config: Path | None = None, drafts: bool = False, fixtures: bool = False):
    command = [hugo, "--source", str(source), "--destination", str(destination),
               "--baseURL", BASE_URL, "--cacheDir", str(source / ".cache"),
               "--noBuildLock", "--quiet"]
    if content:
        command += ["--contentDir", str(content)]
    if config:
        command += ["--config", f"{source / 'hugo.toml'},{config}"]
    if drafts:
        command.append("--buildDrafts")
    if fixtures:
        # 検証専用の記事の日付を固定し、実行日による並び順の違いを防ぎます。
        command += ["--clock", "2100-01-01T00:00:00+09:00"]
    run(command, source)
    return {path.relative_to(destination).as_posix(): Document(path).root
            for path in destination.rglob("*.html")}


def page(documents, relative: str):
    filename = f"{relative.rstrip('/')}/index.html" if relative else "index.html"
    require(filename in documents, f"ページが生成されませんでした: {filename}")
    return documents[filename]


def menu_links(document: Element):
    menus = document.find(id="menu")
    require(len(menus) == 1, "メインナビゲーションが見つかりません")
    return {link.text: link.attrs.get("href") for link in menus[0].find("a")}


def check_local_references(documents, destination: Path):
    checked = 0
    for filename, document in documents.items():
        page_url = urljoin(BASE_URL, filename)
        for element in document.elements():
            for attr in ("href", "src"):
                value = element.attrs.get(attr, "")
                if not value or value.startswith("#"):
                    continue
                url = urlsplit(urljoin(page_url, value))
                if url.scheme not in ("http", "https") or url.netloc.lower() != "username.github.io":
                    continue
                require(url.path.startswith(PREFIX),
                        f"公開サブパスを外れる {attr}: {filename}: {value}")
                relative = unquote(url.path[len(PREFIX):])
                target = destination / relative
                if url.path.endswith("/") or target.is_dir():
                    target /= "index.html"
                require(target.is_file(), f"リンク先が未生成: {filename}: {value} ({target})")
                checked += 1
    return checked


def check_metadata(document: Element, expected_path: str):
    canonical = [e.attrs.get("href") for e in document.find("link")
                 if "canonical" in e.attrs.get("rel", "").split()]
    require(canonical == [BASE_URL + expected_path], f"canonical URL が不正: {expected_path}")
    metadata = {e.attrs.get("name", e.attrs.get("property")): e.attrs.get("content")
                for e in document.find("meta")}
    for name in ("description", "viewport", "og:title", "og:description", "og:url", "twitter:card"):
        require(bool(metadata.get(name)), f"SEO/viewport メタデータが不足: {expected_path}: {name}")


def write_fixture(content: Path, section: str, slug: str, title: str, date: str,
                  extra: str = "", body: str = "", draft: bool = False):
    directory = content / section / slug
    directory.mkdir(parents=True)
    (directory / "index.md").write_text(
        f'---\ntitle: "{title}"\ndate: {date}\n'
        f'description: "一時ディレクトリにのみ作成する動作確認用コンテンツ。"\n'
        f'draft: {str(draft).lower()}\nsample: false\n{extra}---\n\n'
        f'## 動作確認\n\n{body or "本文の表示を確認します。"}\n', encoding="utf-8")
    (directory / "cover.svg").write_text(SVG, encoding="utf-8")
    # PDF の内容を検証するテストではなく、公開先リンクとコピーを確認します。
    (directory / "support.pdf").write_bytes(b"%PDF-1.4\n% temporary link fixture\n%%EOF\n")
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hugo", default="hugo", help="Hugo 実行ファイルの名前またはパス")
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory(prefix="portfolio-verify-") as temporary:
        root = Path(temporary)
        source = root / "site"
        source.mkdir()
        shutil.copy2(repository / "hugo.toml", source / "hugo.toml")
        for name in ("content", "archetypes", "assets", "static", "layouts", "themes", "i18n"):
            if (repository / name).exists():
                shutil.copytree(repository / name, source / name,
                                ignore=shutil.ignore_patterns(".git"))

        # 記事を更新した後も、空のセクションと記事追加を独立して確認します。
        empty_content = root / "empty-content"
        empty_content.mkdir()
        if (repository / "content" / "_index.md").exists():
            shutil.copy2(repository / "content" / "_index.md", empty_content / "_index.md")
        for section in ("projects", "research", "awards", "publications"):
            (empty_content / section).mkdir()
            shutil.copy2(repository / "content" / section / "_index.md",
                         empty_content / section / "_index.md")
        for section in ("about", "contact"):
            shutil.copytree(repository / "content" / section, empty_content / section)
        show_empty = root / "show-empty.toml"
        show_empty.write_text("[params]\nshowEmptySections = true\n", encoding="utf-8")

        destination = root / "standard"
        documents = build(args.hugo, source, destination, config=show_empty)
        expected_menu = {label: PREFIX + relative for label, relative in MENU.items()}
        for relative in MENU.values():
            document = page(documents, relative)
            require(menu_links(document) == expected_menu, f"ナビゲーションが不正: {relative}")
            check_metadata(document, relative)
        home = page(documents, "")
        require(home.find("h1", id="hero-title"), "トップページの紹介領域がありません")
        require(home.find("button", id="theme-toggle"), "テーマ切替ボタンがありません")
        sample = documents.get("projects/ec-purchase-prediction/index.html")
        if sample is not None:
            require("ECサイトの購入予測モデル" in sample.text, "サンプルの詳細が表示されません")
            require("サンプルプロジェクト" in sample.text, "サンプルの明示がありません")
        require(not any(e.attrs.get("href") == PREFIX + "projects/ec-purchase-prediction/"
                        for e in home.find("a", class_name="update-row")),
                "サンプルが最新の成果・発表に含まれます")
        not_found = documents.get("404.html")
        require(not_found is not None, "カスタム404ページがありません")
        require(any("ホームに戻る" in e.text and e.attrs.get("href") == PREFIX
                    for e in not_found.find("a")), "404からホームに戻れません")
        references = check_local_references(documents, destination)
        print(f"PASS 標準ビルド・7ページのナビ・SEO・404・公開パス ({references} links)")

        for section in ("projects", "research", "awards", "publications"):
            run([args.hugo, "new", "content", f"{section}/archetype-check/index.md",
                 "--kind", section, "--source", str(source), "--noBuildLock"], source)
            markdown = (source / "content" / section / "archetype-check" / "index.md").read_text(encoding="utf-8")
            require("draft: true" in markdown and "## " in markdown,
                    f"記事テンプレートが正しく生成されません: {section}")
        print("PASS Hugo new で4種類のMarkdownテンプレートを生成")

        content = root / "fixture-content"
        shutil.copytree(empty_content, content)
        verification_image = source / "static" / "images" / "verification.svg"
        verification_image.parent.mkdir(parents=True, exist_ok=True)
        verification_image.write_text(SVG, encoding="utf-8")
        image_body = '\n'.join([
            '![バンドル画像](cover.svg)',
            '![静的画像](/images/verification.svg)',
            '{{< figure src="cover.svg" alt="バンドルの図" caption="図の説明" >}}',
            '{{< figure src="/images/verification.svg" alt="静的な図" >}}',
        ])
        write_fixture(content, "projects", "verify-newest", "検証プロジェクト・最新", "2099-01-20",
                      'featured: true\ncategories: ["検証カテゴリ"]\n'
                      'technologies: ["検証技術"]\ngithub: "https://github.com/example/example"\n'
                      'cover:\n  image: "cover.svg"\n  alt: "検証サムネイル"\n  relative: true\n'
                      'materials:\n  - label: "検証資料"\n    url: "support.pdf"\n', image_body)
        write_fixture(content, "research", "verify-research", "検証研究", "2099-01-19",
                      'featured: true\nmodels: ["検証モデル"]\ntechnologies: ["検証研究技術"]\n'
                      'materials:\n  - label: "検証研究資料"\n    url: "support.pdf"\n', image_body)
        write_fixture(content, "awards", "verify-award", "検証受賞", "2099-01-18",
                      'organization: "検証主催団体"\nmaterials:\n  - label: "検証受賞資料"\n    url: "support.pdf"\n')
        write_fixture(content, "publications", "verify-publication", "検証発表", "2099-01-17",
                      'authors: ["検証著者"]\nvenue: "検証学会"\npresentation: "検証発表形式"\n'
                      'pdf: "support.pdf"\nmaterials:\n  - label: "検証発表資料"\n    url: "support.pdf"\n')
        for index in range(12):
            write_fixture(content, "projects", f"verify-older-{index:02d}",
                          f"検証プロジェクト・過去{index:02d}", f"2099-01-{16-index:02d}")
        write_fixture(content, "projects", "verify-draft", "検証下書き", "2099-01-21", draft=True)

        destination = root / "fixtures"
        documents = build(args.hugo, source, destination, content=content, fixtures=True)
        require("projects/verify-draft/index.html" not in documents, "下書きが公開されます")
        project_list = page(documents, "projects/")
        cards = project_list.find("article", class_name="work-card")
        require(len(cards) == 12, "一覧ページのページサイズが不正です")
        require("検証プロジェクト・最新" in cards[0].text, "制作物が日付降順ではありません")
        dates = [card.find("time")[0].attrs["datetime"] for card in cards]
        require(dates == sorted(dates, reverse=True), "制作物の日時順が不正です")
        next_links = project_list.find("a", class_name="next")
        require(len(next_links) == 1 and next_links[0].attrs["href"] == PREFIX + "projects/page/2/",
                "一覧の次ページURLが不正です")
        require(page(documents, "projects/page/2/").find("a", class_name="prev"),
                "一覧の前ページリンクがありません")
        home = page(documents, "")
        updates = home.find("a", class_name="update-row")
        expected_latest = ["projects/verify-newest/", "research/verify-research/",
                           "awards/verify-award/", "publications/verify-publication/", "projects/verify-older-00/"]
        require([e.attrs.get("href") for e in updates] == [PREFIX + item for item in expected_latest],
                "トップの最新の成果・発表が日付降順ではありません")
        featured_links = [e.attrs.get("href") for e in home.find("a", class_name="card-image-link")]
        require(PREFIX + "projects/verify-newest/" in featured_links and
                PREFIX + "research/verify-research/" in featured_links and
                PREFIX + "projects/verify-older-00/" not in featured_links,
                "featuredによる注目のプロジェクトの選択が不正です")
        details = {
            "projects/verify-newest/": ["検証技術", "検証資料"],
            "research/verify-research/": ["検証モデル", "検証研究技術", "検証研究資料"],
            "awards/verify-award/": ["検証主催団体", "検証受賞資料"],
            "publications/verify-publication/": ["検証著者", "検証学会", "検証発表形式", "論文PDF", "検証発表資料"],
        }
        for relative, metadata in details.items():
            document = page(documents, relative)
            require(all(value in document.text for value in metadata),
                    f"front matterの関連情報が表示されません: {relative}")
            require(any(e.attrs.get("href") == PREFIX + relative.split("/")[0] + "/"
                        and "一覧に戻る" in e.text for e in document.find("a")),
                    f"一覧に戻るリンクがありません: {relative}")
        project = page(documents, "projects/verify-newest/")
        images = [e.attrs.get("src") for e in project.find("img")]
        require(images.count(PREFIX + "projects/verify-newest/cover.svg") >= 2 and
                images.count(PREFIX + "images/verification.svg") >= 2,
                "Markdown画像またはfigureのパスが不正です")
        references = check_local_references(documents, destination)
        print(f"PASS Markdown追加・日付順・注目記事・詳細情報・画像/PDF・ページ送り ({references} links)")

        draft_destination = root / "drafts"
        drafts = build(args.hugo, source, draft_destination, content=content, drafts=True, fixtures=True)
        require("下書き" in page(drafts, "projects/verify-draft/").text,
                "--buildDraftsによる下書きプレビューができません")
        require(page(drafts, "").find("a", class_name="update-row")[0].attrs["href"]
                == PREFIX + "projects/verify-draft/", "下書きプレビューの新着順が不正です")
        check_local_references(drafts, draft_destination)
        print("PASS 下書きは公開ビルドで非表示、--buildDraftsでプレビュー可能")

        override = root / "hide-empty.toml"
        override.write_text("[params]\nshowEmptySections = false\n", encoding="utf-8")
        destination = root / "hide-empty"
        documents = build(args.hugo, source, destination, content=empty_content, config=override)
        home = page(documents, "")
        require(menu_links(home) == {name: path for name, path in expected_menu.items()
                                    if name not in ("Research", "Awards", "Publications")},
                "未登録セクションを非表示にする設定が動作しません")
        require(not home.find(id="interests-title"), "空のResearchセクションがホームに表示されます")
        check_local_references(documents, destination)
        print("PASS showEmptySections=falseで未登録セクションを非表示")

    print("すべての検証に成功しました。元のコンテンツとpublic/は変更していません。")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, RuntimeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        sys.exit(1)
