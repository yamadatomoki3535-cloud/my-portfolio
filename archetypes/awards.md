---
title: "{{ replace (path.Base (path.Dir .File.Path)) "-" " " | title }}"
date: {{ .Date }}
description: "実際に受賞した賞の概要を入力してください。"
categories: []
tags: []
organization: ""
materials: []
sample: false
draft: true
cover:
  image: ""
  alt: ""
  caption: ""
  relative: true
---

<!-- 必須: title・date・description・draft。その他は任意です。
空文字・空リストは表示されません。確認後に draft: false にすると公開されます。 -->

## 受賞について

受賞内容、対象となった取り組み、関連情報を入力してください。

<!-- date は実際の受賞日、title は賞の名前、organization は主催団体です。
関連リンクは materials に label と url の組で登録できます。
実際に受賞した実績のみを登録してください。
-->
