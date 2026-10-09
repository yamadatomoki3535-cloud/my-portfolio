# 個人ポートフォリオ

静岡大学 情報学部の学生向けに、制作物・研究・受賞歴・論文や発表を継続して公開できる日本語のポートフォリオです。Hugo と PaperMod を使用し、内容は Markdown、プロフィールや表示設定は `hugo.toml` で管理します。GitHub Pages の無料プランで公開できます。

初期の氏名や自己紹介は編集用のプレースホルダーです。「ECサイトの購入予測モデル」は入力例であり、実際の完成・発表・性能を示しません。サンプルの日付は登録例です。未提供の研究成果、受賞歴、論文、メールアドレスは登録していません。

## 使用技術とファイル構成

- **Hugo 0.147.9**：静的サイト生成。標準版で動作し、Extended 版は必須ではありません。
- **PaperMod**：Git サブモジュール `themes/PaperMod`。リポジトリで固定したコミットを使用します。
- **HTML / CSS**：最小限のレイアウト調整、レスポンシブ対応。ライト・ダーク切り替えは PaperMod の機能です。
- **Markdown**：プロフィールページ、各プロジェクト・研究・実績の記事。
- **GitHub Actions / GitHub Pages**：`main` への push で自動ビルド・公開。

```text
hugo.toml                     サイト・プロフィール・メニュー設定
content/about/index.md        自己紹介
content/contact/index.md      連絡先
content/projects/             プロジェクト一覧と詳細
content/research/             研究一覧と詳細
content/awards/               受賞歴一覧と詳細
content/publications/         論文・発表一覧と詳細
archetypes/                   記事追加時のテンプレート
layouts/                      ホーム・一覧・表示部品のカスタマイズ
assets/css/extended/          PaperModに追加するスタイル
scripts/verify_site.py        ビルド・記事追加・公開パスの自動確認
static/images/                サムネイルや図
themes/PaperMod/              固定バージョンのテーマ
.github/workflows/hugo.yml    GitHub Pagesへの公開処理
```

`public/` などのビルド成果物は Git に含めません。テーマ本体を直接編集せず、サイト固有の設定や `layouts/`、`assets/css/extended/` を変更してください。

## 開発環境の準備（Windows PowerShell）

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

実際の所有者に合わせて URL を変更してください。

```powershell
git clone --recurse-submodules https://github.com/yamadatomoki3535-cloud/my-portfolio.git
Set-Location my-portfolio
git submodule update --init --recursive
```

既に clone 済みの場合は最後のコマンドを実行してください。テーマは GitHub Actions でもサブモジュールとして取得するため、`.gitmodules` とテーマの固定コミットを Git に含めます。

## ローカルでの起動とビルド

`hugo.toml` のあるフォルダーで実行します。

```powershell
hugo server --buildDrafts
```

ターミナルに表示された URL（通常 `http://localhost:1313/my-portfolio/`）をブラウザーで開きます。編集するとプレビューが更新されます。停止は `Ctrl+C` です。`--buildDrafts` は `draft: true` の記事もプレビューに含めます。

公開と同じ設定でビルドするには次を実行します。公開用ビルドには下書きが含まれません。

```powershell
hugo --gc --minify
```

生成先は `public/` です。`public/index.html` を直接開くとパスの条件が異なるため、画面確認には `hugo server` を使ってください。

## GitHub Pages への公開

1. ファイル一式を自身の GitHub リポジトリ `my-portfolio` の `main` ブランチに反映します。テーマのサブモジュールも含めてください。
2. GitHub のリポジトリで **Settings → Pages → Build and deployment → Source** を **GitHub Actions** にします。
3. `main` に push すると **Actions → Deploy Hugo site to GitHub Pages** が動きます。必要なら同じ画面から **Run workflow** を実行します。
4. 成功後、`https://USERNAME.github.io/my-portfolio/` を開きます。初回の反映には時間がかかる場合があります。

Actions は Hugo 0.147.9 を公式のチェックサムで検証してインストールし、ビルドした `public/` を Pages に公開します。ビルドと公開のジョブを分け、公開ジョブだけに Pages の書き込み権限を与えています。個人アクセストークンや有料サービスは必要ありません。

`hugo.toml` の `baseURL` を実際の公開 URL に合わせます。末尾の `/` も含めてください。

```toml
baseURL = "https://USERNAME.github.io/my-portfolio/"
```

GitHub Actions では Pages が返す実際の URL を使用するため、所有者やリポジトリ名を変更しても公開ビルドの URL は追従します。ローカルビルド、プレビュー、サイト設定との整合のため `baseURL` も更新してください。内部リンクや画像は Hugo の URL 処理を通し、`/my-portfolio/` に対応します。GitHub Pages はルートに生成された `404.html` をエラーページとして使用します。

ワークフローが失敗したら Actions の該当ジョブを開いてエラーを確認してください。特に Pages の Source 設定、テーマのサブモジュール、Hugo のバージョンを確認します。組織の権限制限がある場合は管理者による Pages の有効化が必要なことがあります。

## プロフィールと全体設定の編集

`hugo.toml` の `[params.profile]` を編集します。

```toml
[params.profile]
name = "あなたの氏名"
affiliation = "静岡大学 情報学部"
bio = "ここに短い自己紹介を入力します。"
github = "https://github.com/USERNAME"
interests = ["機械学習・深層学習", "大規模言語モデル（LLM）", "Vision-Language Model（VLM）", "情報検索", "LoRA"]
skills = ["Python", "Git", "Hugo"]
skillsNote = ""
```

上記のスキルは記入例です。自分の内容に書き換えてください。初期設定の `skillsNote` は入力例である旨の注記です。実際のスキルに更新したら空文字にすると注記を非表示にできます。About に表示するプロフィールと Home の紹介はこの設定を利用します。追加の自己紹介文章は `content/about/index.md` で編集できます。Contact の説明は `content/contact/index.md` で編集します。公開したくない項目は空にし、未提供のメールアドレスなどを追記する必要はありません。

サイト名は `title`、検索エンジン向けの説明は `[params]` の `description`、Home の文言は `[params.home]` の `eyebrow`・`headline`・`tagline` で変更します。

空にした GitHub URL、スキルや興味分野のリストは About から非表示になります。Home の最新の成果・発表は実際の記事を登録したときだけ表示され、`sample: true` の入力例は含まれません。

```toml
[params]
showEmptySections = false
```

この設定で、記事未登録の Research / Awards / Publications のナビゲーションや Home の空セクションを非表示にできます。初期設定は `true` で、未登録であることを明示します。ページを見せたい場合は `true` に戻してください。設定ファイルに同じ `[params]` を重複追加せず、既存のキーを書き換えてください。

## 新しいプロジェクトの追加

1. 次のコマンドでテンプレートから記事を作成します。`my-project` は英数字とハイフンによる URL 用の名前です。

   ```powershell
   hugo new content projects/my-project/index.md
   ```

2. 作成した `content/projects/my-project/index.md` をテキストエディターで開き、先頭の `---` に挟まれた設定（front matter）と本文を編集します。

   ```yaml
   title: "プロジェクト名"
   date: 2026-10-10
   description: "一覧に表示する短い概要"
   draft: false
   featured: true
   sample: false
   categories: ["機械学習"]
   technologies: ["Python", "scikit-learn"]
   github: "https://github.com/USERNAME/REPOSITORY"
   cover:
     image: "images/projects/my-project.jpg"
     alt: "画像の内容を説明する文章"
   ```

3. 本文に「概要」「背景と目的」「使用技術」「システム構成」「実装内容」「実験結果や成果」などを Markdown で記入します。未実施の結果は空にするか、入力予定であることを明記してください。
4. `hugo server --buildDrafts` で確認してから GitHub に反映します。

`draft: true` の間は公開されません。公開時に `false` にします。`featured: true` は Home の注目項目への表示指定です。`sample: true` は実績と区別するためのサンプル表記を付けます。実際の制作物を登録する際は内容を確認して `sample: false` にしてください。

一覧は公開記事の日付が新しい順になります。未来の日付の記事は Hugo の標準動作で通常の公開ビルドに含まれないため、実際の登録日・制作日にしてください。画像や GitHub URL は省略できます。ファイルを追加するだけで一覧に反映され、一覧用の HTML 編集は必要ありません。

## 研究ページの追加

```powershell
hugo new content research/my-research/index.md
```

`content/research/my-research/index.md` のタイトル、日付、概要、`technologies`、画像、本文を編集します。テンプレートには研究概要・背景・目的・提案手法・実験内容・結果と考察などの項目があります。

関連資料は front matter の `materials` で設定できます。

```yaml
materials:
  - label: "発表スライド"
    url: "https://example.com/slides"
```

この URL は書式例です。実際の資料に置き換えるか、未登録なら `materials: []` にしてください。Markdown 本文から `[資料名](https://実際のURL)` と書いてもリンクできます。研究室の日記や活動記録の機能は含めていません。

## 受賞歴・論文や発表の追加

実際の実績ができた際に追加してください。記事未登録の一覧には未登録の案内が表示されます。

```powershell
hugo new content awards/my-award/index.md
hugo new content publications/my-publication/index.md
```

共通の `title`・`date`・`description`・`draft` と本文を編集し、次の項目を設定します。

| 種類 | 項目 | 内容 |
| --- | --- | --- |
| 受賞歴 | `organization` | 主催団体 |
| 受賞歴 | `materials` | 関連リンク（`label` / `url` のリスト） |
| 論文・発表 | `authors` | 著者名のリスト |
| 論文・発表 | `venue` | 学会名・掲載先 |
| 論文・発表 | `presentation` | 口頭発表・ポスターなどの形式 |
| 論文・発表 | `pdf` | 論文 PDF の URL または静的ファイルのパス |
| 論文・発表 | `materials` | 関連リンク（`label` / `url` のリスト） |

使用しない項目は空文字や空のリストにします。テンプレート内の入力用文言は公開前に書き換えてください。

## 画像・図・PDF の追加

### 複数の記事で共有する画像

`static/images/` の中に保存します。例えば `static/images/projects/my-project.jpg` は front matter では `images/projects/my-project.jpg` と指定します。`static/` 自体は URL に書きません。

```powershell
New-Item -ItemType Directory -Force static/images/projects | Out-Null
Copy-Item "C:\Users\あなた\Pictures\thumbnail.jpg" "static/images/projects/my-project.jpg"
```

本文には次のように書きます。

```markdown
![購入予測モデルのシステム構成](images/projects/system-diagram.png)
```

### 記事専用の画像（ページバンドル）

`index.md` と同じフォルダーに画像を置くと、記事とまとめて管理できます。

```text
content/projects/my-project/
  index.md
  thumbnail.jpg
  system-diagram.png
```

```yaml
cover:
  image: "thumbnail.jpg"
  alt: "画面の説明"
```

```markdown
![システム構成](system-diagram.png)
```

キャプションやサイズ指定には Hugo の標準 figure ショートコードも使えます。

```markdown
{{< figure src="system-diagram.png" alt="システム構成" caption="システムの構成図" >}}
```

ファイル名は英数字とハイフンを使い、パスは Windows の `\` ではなく `/` で記入します。先頭 `/` を付けないサイト内パスを推奨します。外部画像は `https://...` で指定できます。PDF は `static/files/` に保存し、`pdf: "files/paper.pdf"` のように記入します。公開する権利のある画像・資料を使用してください。

## GitHub への変更反映

通常は `main` ブランチの作業フォルダーで編集します。作業開始前に状態を確認し、未保存の変更がない場合に取得します。

```powershell
git status
git branch --show-current
git pull --ff-only origin main
```

編集とローカル確認後、差分を確認して反映します。

```powershell
git status
git diff
git add .
git commit -m "Update portfolio content"
git push origin main
```

最初の commit で氏名・メールの Git 設定を求められた場合は、GitHub のアカウント設定を確認して設定してください。GitHub の非公開用 noreply アドレスも使用できます。Git 設定のメールを Contact に掲載する必要はありません。

このクラウド作業のブランチが `work` など `main` 以外の場合、上の push は作業内容を自動で main に移しません。初回は変更を commit して作業ブランチを push し、GitHub 上で **Pull Request → main に merge** して公開します。

```powershell
git branch --show-current
git status
git add .
git commit -m "Create Japanese portfolio site"
git push -u origin HEAD
```

競合が出た場合は既存の変更を確認してください。`--force` を使って上書きする必要はありません。テーマの取得には `git submodule update --init --recursive` を使い、通常のコンテンツ更新ではテーマを更新しません。

## 公開前の確認

- `hugo --gc --minify` が成功する。
- Home と各ページ、プロジェクト詳細、ヘッダー・フッターのリンクを確認する。
- 狭い画面幅、スマートフォン、ライト・ダーク両方で表示を確認する。
- 追加した記事の `draft`・日付・画像パスを確認する。
- プレースホルダーや未確認の実績が公開されないよう確認する。
- Actions 成功後、`/my-portfolio/` の公開 URL で CSS・画像・内部リンクを確認する。

### 自動チェック（任意）

Python 3.10 以上がある場合、次の PowerShell コマンドでビルドと記事追加をまとめて確認できます。追加パッケージは不要です。Python はサイトの起動や公開には必要ありません。

```powershell
python scripts/verify_site.py --hugo hugo
```

一時フォルダー内で各種記事を作成して検証し、元の Markdown と `public/` は変更しません。ナビゲーション、SEO、404、`/my-portfolio/` 配下のリンク、画像、PDF、記事テンプレート、日付順、ページ送り、下書き、空セクションの非表示を確認します。

### この実装での確認結果

クラウド環境で Hugo 0.147.9 による公開用ビルドと上記の自動チェックに成功しました。Chromium でトップ・各ページ・詳細・404を確認し、320 / 390 / 768 / 1440 px の画面幅で横はみ出しがないこと、ナビゲーションと詳細から一覧への移動、画像の読み込み、ライト・ダークの切り替えと保存、キーボードの本文移動を確認しています。参考サイトは直接表示できなかったため、公開ソースから構成を確認しました。

GitHub Actions の実行と実際の GitHub Pages 公開は未実施です。上記の Settings 設定と main への反映後、公開 URL でも確認してください。Windows PowerShell と実機スマートフォンでの実行は、この Linux 環境では実施していません。

クラウド環境の Hugo は `/workspace/.local/bin/hugo` にあります。次回の作業用にインストール・起動手順を環境設定へ保存します。ローカルの Windows では、前述の準備手順で導入した `hugo` を使用します。

## デザインの参考

[参考サイト](https://yurokanada.github.io/my-portfolio/) と PaperMod の、余白を活かした情報整理やシンプルなナビゲーションを参考にした独自のサイトです。参考サイトの文章・画像・氏名・研究成果は使用していません。
