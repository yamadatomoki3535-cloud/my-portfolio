---
title: "{{ replace (path.Base (path.Dir .File.Path)) "-" " " | title }}"
date: {{ .Date }}
description: "プロジェクトの概要を1〜2文で入力してください。"
categories: []
tags: []
technologies: []
github: ""
materials: []
sample: false
featured: false
draft: true
cover:
  image: ""
  alt: ""
  caption: ""
  relative: true
---

<!-- 必須: title（タイトル）・date（日付）・description（概要）・draft（下書き）。
その他は任意です。空文字・空リストは表示されません。
画像は index.md と同じフォルダーに保存し、cover.image: "thumbnail.jpg" と指定します。
cover.alt は画像の説明、cover.caption は表示するキャプションです。
確認後に draft: false にすると公開されます。featured: true でHomeの注目記事に表示します。
-->

## プロジェクト概要

制作したもの、対象とする人、できることを入力してください。

## 背景と目的

取り組んだ課題と、制作の目的を入力してください。

## 使用技術

実際に使用した技術と、それぞれの役割を入力してください。

## システム構成

入力、処理、出力や、コンポーネント間の関係を入力してください。

<!-- 同じフォルダーに diagram.png を保存したら: ![構成図の説明](diagram.png) -->

## 実装内容

実装した機能や工夫した点を入力してください。

## 実験結果や成果

実際に確認した結果を入力してください。未実施の場合は、その旨を記載してください。

## 画像や図

<!-- 例: ![画面の説明](screenshot.png) -->

## GitHubリンク

<!-- front matter の github に公開リポジトリのURLを入力すると、リンクが表示されます。 -->
