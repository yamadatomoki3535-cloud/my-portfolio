# 個人ポートフォリオ

Hugo と PaperMod を使った日本語のポートフォリオです。記事本文と記事専用の画像は `content/`、共通プロフィールは `hugo.toml` で管理します。Markdown と画像を追加・編集すれば、一覧やトップページに反映されます。日常の更新で HTML や CSS を編集する必要はありません。

既存の「ECサイトの購入予測モデル」は入力例です。実際の完成・発表・性能を示すものではなく、日付も登録例です。研究成果・受賞歴・論文・実験結果には確認済みの事実を記入し、未提供の内容は下書きの入力用文言として扱ってください。

## どのファイルを編集するか

| 編集する場所 | 変わる内容 |
| --- | --- |
| `content/projects/記事のURL名/index.md` | プロジェクトのタイトル・概要・本文・公開状態 |
| `content/research/記事のURL名/index.md` | 研究のタイトル・概要・本文・公開状態 |
| 記事の `index.md` と同じフォルダー | その記事のサムネイル・図・写真 |
| `content/projects/_index.md` など | 各一覧ページのタイトルと説明文 |
| `content/about/index.md` | About の追加説明・経歴などの文章 |
| `content/contact/index.md` | Contact の説明文 |
| `hugo.toml` の `[params.profile]` | Home・About・Contact で使う氏名・所属・自己紹介・GitHub などの共通情報 |
| `hugo.toml` の `[params.home]` | Home の見出し `headline`、導入文 `tagline` など |
| `hugo.toml` の `title`・`baseURL`・`[params]`・`menu.main` | サイト名・公開 URL・全体設定・メニュー |
| `archetypes/` | 次に作る記事の初期テンプレート。作成済みの記事は変わりません |
| `layouts/` | Home・一覧・記事詳細などの表示レイアウト |
| `assets/css/extended/` | 色・文字サイズ・余白・スマートフォン向けのデザイン調整 |
| `static/images/` | 複数ページで共有する画像 |
| `static/files/` | 公開する PDF などの共有資料 |

ファイル構成は次のとおりです。記事ごとのフォルダーに本文と画像をまとめる構成を「ページバンドル」と呼びます。

```text
my-portfolio/
  hugo.toml
  content/
    about/index.md
    contact/index.md
    projects/
      _index.md
      記事のURL名/
        index.md
        thumbnail.jpg
        diagram.png
    research/
      _index.md
      記事のURL名/
        index.md
        diagram.png
    awards/
    publications/
  archetypes/
    projects.md
    research.md
    awards.md
    publications.md
  layouts/
  assets/css/extended/
  static/
    images/
    files/
  scripts/verify_site.py
  themes/PaperMod/
  .github/workflows/hugo.yml
```

画像が不要な記事には画像ファイルを置く必要はありません。既存の入力例は `content/projects/ec-purchase-prediction/index.md` と同じフォルダーの `diagram.svg` で管理しています。`_index.md` は一覧ページ、`index.md` は個別記事です。

`public/` はビルドで生成されるため直接編集せず、Git にも含めません。PaperMod 本体を変更する場合は、テーマを直接編集するより `layouts/` と `assets/css/extended/` でサイト側の調整を行ってください。

## 開発環境の準備（Windows PowerShell）

Hugo 0.147.9 の標準版と、リポジトリでコミットを固定した PaperMod サブモジュールを使用します。Extended 版は必須ではありません。以下のコマンドは Windows PowerShell で実行できます。

### 1. Git を用意する

Git がない場合は [Git for Windows](https://git-scm.com/download/win) からインストールするか、PowerShell で次を実行します。

```powershell
winget install --id Git.Git --exact --source winget
```

インストール後は PowerShell を開き直し、確認します。

```powershell
git --version
```

### 2. Hugo 0.147.9 を用意する

以下は 64 bit の Windows（x64）向けです。[公式リリース](https://github.com/gohugoio/hugo/releases/tag/v0.147.9) の ZIP とチェックサムをダウンロードし、SHA-256 を確認してから展開します。

```powershell
$HugoVersion = "0.147.9"
$HugoFile = "hugo_${HugoVersion}_windows-amd64.zip"
$HugoRelease = "https://github.com/gohugoio/hugo/releases/download/v${HugoVersion}"
$HugoZip = Join-Path $env:TEMP $HugoFile
$HugoChecksums = Join-Path $env:TEMP "hugo_${HugoVersion}_checksums.txt"
$HugoDir = Join-Path $env:LOCALAPPDATA "Programs\Hugo"

Invoke-WebRequest "$HugoRelease/$HugoFile" -OutFile $HugoZip
Invoke-WebRequest "$HugoRelease/hugo_${HugoVersion}_checksums.txt" -OutFile $HugoChecksums
$ChecksumPattern = "^[0-9a-fA-F]{64}\s+" + [regex]::Escape($HugoFile) + "$"
$ChecksumLines = @(Get-Content $HugoChecksums | Where-Object { $_ -match $ChecksumPattern })
if ($ChecksumLines.Count -ne 1) { throw "対象のチェックサムを一意に取得できませんでした。" }
$ExpectedHash = ($ChecksumLines[0] -split '\s+')[0]
$ActualHash = (Get-FileHash $HugoZip -Algorithm SHA256).Hash
if ($ActualHash -ne $ExpectedHash) { throw "チェックサムが一致しません。展開を中止します。" }

New-Item -ItemType Directory -Force $HugoDir | Out-Null
Expand-Archive -Path $HugoZip -DestinationPath $HugoDir -Force
$env:Path = "$HugoDir;$env:Path"
hugo version
```

最後の PATH 設定はその PowerShell で有効です。次回も使う場合は Windows の「環境変数」からユーザーの `Path` に `%LOCALAPPDATA%\Programs\Hugo` を追加し、PowerShell を開き直してください。ARM64 の Windows では公式リリースの対応 ZIP を選び、同じ方法でチェックサムを確認してください。

### 3. リポジトリを取得する

```powershell
git clone --recurse-submodules https://github.com/yamadatomoki3535-cloud/my-portfolio.git
Set-Location my-portfolio
git submodule update --init --recursive
```

すでに取得済みなら、その `my-portfolio` フォルダーで最後のコマンドを実行してください。以降のコマンドはすべて `hugo.toml` があるフォルダーで実行します。

## プロフィールと全体設定を編集する

共通プロフィールは `hugo.toml` の既存の `[params.profile]` を編集します。Home の所属・関心分野、About の自己紹介、Contact の GitHub リンクはこの設定を参照するため、各ページで同じ情報を書き直す必要はありません。

```toml
[params.profile]
name = "あなたの氏名"
affiliation = "あなたの所属"
bio = "ここに自己紹介を入力します。"
github = "https://github.com/あなたのユーザー名"
interests = ["関心のある分野"]
skills = ["実際に使用している技術"]
skillsNote = ""
```

これは記入例です。既存の値を自分の情報に書き換えてください。任意の GitHub URL や文字列は `""`、リストは `[]` にすると表示されません。`skillsNote` はスキルの補足文で、必要なときだけ記入します。

`content/about/index.md` の `{{< profile >}}` が共通の自己紹介を表示します。追加の経歴や文章は、その下に Markdown で記入します。Contact の文章は `content/contact/index.md` で編集してください。

Home の大きな見出しは `hugo.toml` の `[params.home]` の `headline` です。サイト名は先頭の `title`、サイト全体の説明は `[params]` の `description` で変更します。

```toml
[params.home]
eyebrow = "RESEARCH & DEVELOPMENT"
headline = "あなたの見出し"
tagline = "トップページの導入文"
```

既存の `[params]` の `showEmptySections` を `false` にすると、記事未登録の Research / Awards / Publications のナビゲーションと Home の空セクションを非表示にできます。初期設定は `true` です。同じ `[params]` や `[params.profile]` を末尾に追加せず、既存の項目を編集してください。

## 新しい記事を追加する

### 1. テンプレートから下書きを作る

プロジェクトの記事なら次を実行します。`my-project` は記事の URL 用の名前です。英小文字・数字・ハイフンを使い、別の記事では別の名前にしてください。

```powershell
hugo new content projects/my-project/index.md
```

研究記事の場合は次を使います。

```powershell
hugo new content research/my-research/index.md
```

それぞれ `archetypes/projects.md`・`archetypes/research.md` を使って作成され、初期状態は `draft: true`（下書き）です。`content/projects/my-project/index.md` または `content/research/my-research/index.md` をエディターで開きます。タイトルの初期値は URL 名から生成されるので、実際の日本語タイトルに書き換えてください。

### 2. 設定と本文を埋める

先頭の `---` と `---` に挟まれた部分が front matter（記事の設定）です。その下が Markdown の本文です。次は、画像をまだ追加していない状態でも使えるコピー用の例です。日付は実際の記事の日付に置き換えてください。

```markdown
---
title: "記事のタイトルを入力"
date: 2026-10-11
description: "記事の概要を1〜2文で入力します。"
draft: true
featured: false
categories: []
tags: []
technologies: []
github: ""
materials: []
cover:
  image: ""
  alt: ""
  caption: ""
---

## 概要

取り組んだ内容を入力してください。

## 背景と目的

課題と目的を入力してください。

## 取り組みの内容

実際に行った制作・研究の内容を入力してください。

## 結果と考察

確認済みの結果を入力してください。未実施なら、その旨を記載してください。
```

YAML の `:` の後には半角スペースが必要です。`cover` の内側などは半角スペース2個で字下げします。`true`・`false` は引用符で囲まず、文字列は `"..."`、リストは `["項目1", "項目2"]` と書いてください。ファイルは UTF-8 で保存します。

### 3. 画像を同じフォルダーに置く

記事専用の画像は `index.md` と同じフォルダーへコピーします。コピー元のパスは実際の画像に置き換えてください。

```powershell
Copy-Item -LiteralPath "C:\Users\あなた\Pictures\thumbnail.jpg" -Destination ".\content\projects\my-project\thumbnail.jpg"
Copy-Item -LiteralPath "C:\Users\あなた\Pictures\diagram.png" -Destination ".\content\projects\my-project\diagram.png"
```

サムネイルは front matter の `cover` を次のように編集します。

```yaml
cover:
  image: "thumbnail.jpg"
  alt: "画像に写っている内容の説明"
  caption: "サムネイルの補足説明"
```

本文の図は次のように書きます。

```markdown
![図の内容を説明する文章](diagram.png)
```

画像を使わない場合は、`cover:` 内の `image: ""` のままで構いません。サムネイル・キャプションは未入力なら表示されません。`alt` は画像が読み込めない場合や読み上げ時に使う説明なので、画像を設定するときは内容を記入してください。

### 4. 下書きを確認して公開する

```powershell
hugo server --buildDrafts
```

ターミナルに表示された URL（通常 `http://localhost:1313/my-portfolio/`）をブラウザーで開きます。保存すると表示が更新され、停止は `Ctrl+C` です。この起動方法では下書きも表示されます。

タイトル・概要・画像・本文を確認したら、記事の `draft: true` を `draft: false` に変更します。入力用の文章は実際の内容に置き換え、不要な本文見出しも削除します。

公開時の表示を確認するには、下書き確認用サーバーを `Ctrl+C` で停止して次を実行します。

```powershell
hugo server
```

`draft: true` の記事は一覧・Home・記事詳細に公開されません。日付が未来の記事も通常のビルドでは公開されないため、プレビューに出ない場合は `date` を確認してください。未来の日付も含めて確認するときは `hugo server --buildDrafts --buildFuture` を使います。

Markdown を追加すると、各一覧は `date` の新しい順に自動更新されます。`featured: true` の Projects / Research は Home の注目記事にも表示されます。一覧用 HTML や `hugo.toml` に記事を登録する作業は不要です。ローカルで設定を変更しただけでは GitHub Pages の内容は変わらず、後述の GitHub への反映後に公開されます。

## front matter の各項目

### 必須項目

以下は、この記事テンプレートを使うときに必ず確認する項目です。

| 項目 | 意味 | 記入例 |
| --- | --- | --- |
| `title` | 一覧・記事詳細に表示するタイトル | `title: "制作物のタイトル"` |
| `date` | 記事の日付。新しい順に並べる基準 | `date: 2026-10-11` |
| `description` | 一覧・記事詳細・検索向けの短い概要 | `description: "取り組みの概要です。"` |
| `draft` | 下書きなら `true`、公開なら `false` | `draft: true` |

### 任意項目

使わない文字列は `""`、リストは `[]`、表示指定は `false` にするか、項目自体を省略します。空の情報の見出しやリンクは表示されません。本文に自分で書いた見出しは自動では消えないため、不要な見出しは本文から削除してください。

| 項目 | 意味 | 記入例 |
| --- | --- | --- |
| `featured` | Home の Projects / Research 注目記事へ表示 | `featured: true` |
| `categories` | 大きな分類 | `categories: ["制作記録"]` |
| `tags` | より細かいキーワード | `tags: ["Hugo", "Web"]` |
| `technologies` | 実際に使った技術の一覧 | `technologies: ["Python", "Hugo"]` |
| `github` | その記事の公開 GitHub リポジトリ | `github: "https://github.com/ユーザー名/リポジトリ名"` |
| `cover.image` | サムネイル。記事内の画像名、共有画像のパス、外部 URL | `image: "thumbnail.jpg"`（`cover:` の内側） |
| `cover.alt` | サムネイルの画像内容の説明 | `alt: "アプリの一覧画面"` |
| `cover.caption` | サムネイルの下に表示する補足 | `caption: "試作版の画面"` |
| `materials` | 関連資料のリスト。各資料に `label` と `url` を設定 | 下の記入例を参照 |
| `models` | 研究で実際に使ったモデルの一覧 | `models: ["使用したモデル名"]` |
| `sample` | 入力例であることを示す表示 | `sample: true` |

`sample: true` の記事は入力例の注記を付けて表示され、Home の最新の成果・発表には含まれません。実際の記事は `sample: false` または省略します。

関連資料は、同じ front matter 内に次のように追加します。URL は実際の公開可能な資料に置き換えてください。未登録なら `materials: []` にします。`label` または `url` が空の資料は表示されません。

```yaml
materials:
  - label: "発表スライド"
    url: "https://example.com/slides"
  - label: "補足資料 PDF"
    url: "files/supplement.pdf"
```

## Markdown の書き方

次の例を記事の本文にコピーして使えます。タイトルは front matter に設定するため、本文の大見出しは `##` から始めます。

````markdown
## 見出し

段落の間には空行を入れます。**太字**で強調できます。

### 小見出し

- 箇条書きの項目1
- 箇条書きの項目2

1. 手順1
2. 手順2

[外部サイトを開く](https://example.com/)

[プロジェクト一覧へ](/projects/)

[別のプロジェクト記事へ](/projects/my-project/)

![図の内容を説明する文章](diagram.png)

本文中の短いコードは `print("Hello")` のように書きます。

```python
message = "Hello"
print(message)
```
````

サイト内リンクは例のようにサイト内のパスを使うと、表示時に `/my-portfolio/` を考慮します。別の記事へのリンクは、その記事を公開してから公開サイトで確認してください。見本の `my-project` は実際の記事の URL 名に置き換えます。Markdown に Windows の `C:\...` や `\` の区切りを記入せず、URL の `/` を使用します。

本文の図に補足文を付ける場合は figure ショートコードも使えます。

```markdown
{{< figure src="diagram.png" alt="図の内容を説明する文章" caption="図の補足説明" >}}
```

## 共有画像・PDF を追加する

複数ページで使う画像は `static/images/`、共有 PDF は `static/files/` に置きます。記事専用の画像は、その記事の `index.md` と同じフォルダーに置くのを基本にしてください。

```powershell
New-Item -ItemType Directory -Force -Path ".\static\images" | Out-Null
New-Item -ItemType Directory -Force -Path ".\static\files" | Out-Null
Copy-Item -LiteralPath "C:\Users\あなた\Pictures\shared-diagram.png" -Destination ".\static\images\shared-diagram.png"
Copy-Item -LiteralPath "C:\Users\あなた\Documents\slides.pdf" -Destination ".\static\files\slides.pdf"
```

Markdown には `static/` を付けず、次のように書きます。

```markdown
![共有の構成図](images/shared-diagram.png)

[スライド PDF](files/slides.pdf)
```

front matter の共有サムネイルは `cover:` 内の `image` に `"images/shared-diagram.png"` を指定します。論文の PDF は `pdf: "files/slides.pdf"` と指定できます。ファイル名は英数字とハイフンを基本にし、大文字・小文字も実際の名前と一致させます。図や資料は、公開できるものを使ってください。

## 受賞歴・論文や発表を追加する

確認済みの実績がある場合に、次のテンプレートから作成します。どちらも下書きで作られます。

```powershell
hugo new content awards/my-award/index.md
hugo new content publications/my-publication/index.md
```

共通の必須項目と本文を編集し、必要に応じて次の任意項目を設定してください。未登録のまま、受賞・掲載されたように記入する必要はありません。

| 種類 | 項目 | 内容 |
| --- | --- | --- |
| 受賞歴 | `organization` | 主催団体 |
| 論文・発表 | `authors` | 著者名のリスト |
| 論文・発表 | `venue` | 学会名・掲載先 |
| 論文・発表 | `presentation` | 口頭発表・ポスターなどの形式 |
| 論文・発表 | `pdf` | 公開可能な PDF の URL または `files/paper.pdf` のような共有資料パス |
| 共通 | `materials` | `label` / `url` の組による関連リンク |

## 記事や画像を削除する

記事を一時的に非公開にする場合は、その記事の `draft` を `true` に戻します。完全に削除する場合は、記事のフォルダーを画像ごと削除します。別の記事からその記事にリンクしている場合は、リンクも編集してください。

次は `content/projects/my-project/` を削除する例です。`my-project` を削除したい記事の URL 名に置き換え、表示される絶対パスが対象の記事フォルダーであることを確認してください。最後のコマンドで削除確認が表示されます。

```powershell
$Article = Get-Item -LiteralPath ".\content\projects\my-project" -ErrorAction Stop
$ProjectsRoot = (Resolve-Path -LiteralPath ".\content\projects").Path.TrimEnd('\') + '\'
if (-not $Article.FullName.StartsWith($ProjectsRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "削除対象が projects フォルダーの外にあります。"
}
$Article.FullName
Remove-Item -LiteralPath $Article.FullName -Recurse -Confirm
```

研究記事なら上のパスの `projects` をすべて `research` に置き換えてください。

画像だけを削除するときは、まず Markdown 内の `![...](画像名)`、figure、front matter の `cover` などから参照を削除します。その後、対象画像だけを削除します。

```powershell
Get-Item -LiteralPath ".\content\projects\my-project\diagram.png"
Remove-Item -LiteralPath ".\content\projects\my-project\diagram.png" -Confirm
```

共有画像や PDF は他の記事でも使っている場合があるため、エディターの全体検索でファイル名の参照を確認してから削除してください。削除後もローカルで確認し、GitHub に変更を反映します。

## ローカルでビルド・確認する

公開用ビルドは次を実行します。下書きと未来の日付の記事は含まれません。

```powershell
hugo --gc --minify
```

生成先は `public/` です。`public/index.html` を直接開くと公開時と URL の条件が異なるため、画面確認には `hugo server` を使用します。

Python 3.10 以上がある場合は、次の自動チェックも利用できます。追加パッケージは不要で、Python はサイトの起動・記事更新・公開には必要ありません。

```powershell
python scripts/verify_site.py --hugo hugo
```

一時フォルダーで記事を追加して確認するため、元の Markdown と `public/` は変更しません。ナビゲーション、SEO、404、`/my-portfolio/` 配下のリンク、記事の画像・PDF、テンプレート、日付順、ページ送り、下書き、空セクションの表示を確認します。

公開前には、次の点をブラウザーでも確認してください。

- `hugo server --buildDrafts` で新しい記事と画像が表示される。
- `hugo server` では下書きの記事が一覧・Home・記事詳細に出ない。
- 一覧の記事が新しい日付から並び、`featured: true` の記事が Home に表示される。
- スマートフォン相当の幅（320 / 390 px など）で本文・画像・ナビゲーションが画面内に収まる。ブラウザーの開発者ツールで幅を変更できる。
- ライト・ダーク両方で本文を読みやすく、長いコードや表も操作できる。
- `/my-portfolio/` の下で画像・記事・一覧・PDF のリンクを開ける。
- 入力用の文章や未確認の実績が公開されない。

## GitHub に変更を反映する

作業を始める前にブランチと変更の状態を確認します。未コミットの変更がなく、`main` で作業しているときに最新の変更を取得してください。

```powershell
git status
git branch --show-current
git pull --ff-only origin main
```

編集とローカル確認を終えたら差分を確認し、変更を commit・push します。`git status` と `git diff` で、公開したいファイルだけが変更されていることを確認してください。

```powershell
git status
git diff
git add .
git commit -m "Update portfolio content"
git push origin main
```

最初の commit で氏名・メールの Git 設定を求められた場合は、自分の GitHub アカウントの設定を確認して設定します。GitHub の非公開用 noreply アドレスも使用できます。Git 設定用メールを Contact に掲載する必要はありません。

`main` 以外の作業ブランチでは、変更を現在のブランチに push して GitHub 上で Pull Request を作り、`main` に merge します。

```powershell
git status
git branch --show-current
git add .
git commit -m "Update portfolio content"
git push -u origin HEAD
```

競合が出た場合は、変更内容を確認して解決してください。通常のコンテンツ更新で PaperMod サブモジュールを更新する必要はありません。

## GitHub Pages の公開設定

公開先は `https://yamadatomoki3535-cloud.github.io/my-portfolio/` です。初回は GitHub のリポジトリで **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に設定します。

`main` に push または merge すると **Actions → Deploy Hugo site to GitHub Pages** が動きます。成功したら公開サイトを開き、今回の記事・画像・リンクを確認してください。反映には時間がかかる場合があります。手動で実行する場合は同じ画面の **Run workflow** を使います。

Actions は Hugo 0.147.9 を公式チェックサムで検証して導入し、下書きを含めずに生成した `public/` を公開します。テーマも固定コミットのサブモジュールとして取得します。公開ジョブに必要な権限を設定しており、個人アクセストークンは不要です。

公開 URL を変更した場合は `hugo.toml` の `baseURL` を末尾 `/` まで含めて更新してください。GitHub Actions は Pages が返す URL を使ってビルドしますが、ローカル確認でも同じ設定を使えるよう、`baseURL` も実際の URL に合わせます。

```toml
baseURL = "https://yamadatomoki3535-cloud.github.io/my-portfolio/"
```

ワークフローが失敗したら Actions の該当ジョブを開き、エラーを確認します。Pages の Source、PaperMod のサブモジュール、Hugo のバージョンが確認箇所です。公開後にも `/my-portfolio/` 配下の CSS・画像・内部リンクを確認してください。
