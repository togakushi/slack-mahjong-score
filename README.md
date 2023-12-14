# slack-mahjong-score-management

## 概要

slackに投稿されたスコアを集計するツール

以下のフォーマットに一致した投稿をデータベースに取り込む
```
<指定キーワード>
東家プレイヤー名 東家素点
南家プレイヤー名 南家素点
西家プレイヤー名 西家素点
北家プレイヤー名 北家素点
```
- 素点は半角数字、およびプラス記号とマイナス記号を使用して入力すること
- プレイヤー名と素点は区切られている必要はないが、区切る場合は空白文字で区切ること
- 各行末の改行は必要ない
- 指定キーワードは先頭、または末尾のどちらか一方に記載する

【注】必ず起家からの **席順で記入** すること。同点の場合、席順で順位が決められる。

## 主な機能

### 成績サマリ出力機能

- 指定期間内で獲得した合計ポイント順にプレイヤー名を出力する
- 引数でプレイヤー名を複数指定することで、対象のプレイヤーの比較を容易にする
- プレイヤー名を1名だけ指定した場合は、個人成績のサマリを出力する
  
### グラフ生成機能（[詳細](document/graph.md)）

- 獲得ポイントの推移グラフを出力する
- サマリと同様に複数名での比較などが可能

### ランキング出力機能（[詳細](document/ranking.md)）

- 連対率などの成績データをランキング形式で出力する

### スラッシュコマンド（[使い方](document/command.md)）

- 出力結果をボットから直接DMで受け取る

## 簡易マニュアル

設定ファイルに登録したキーワードでチャンネル内から集計結果を表示する

- 「麻雀成績」で今月の成績（トータルポイント集計）
- 「麻雀グラフ」でその日のポイント推移グラフ
- 「麻雀ランキング」で各成績の順位

### コマンド書式

- 麻雀成績 [集計範囲] [対象プレイヤー] [オプション]
- 麻雀グラフ [集計範囲] [対象プレイヤー] [オプション]
- 麻雀ランキング [集計範囲] [オプション]
- /mahjong 成績管理サブコマンド [集計範囲] [対象プレイヤー] [オプション]
- /mahjong メンバー管理サブコマンド [対象プレイヤー]

### 引数内容

- 集計範囲 ： [[当日|今日|昨日|今月|先月|先々月|全部|YYYYMMDD] ... ]
- オプション ： [[ゲストなし|ゲストあり|修正なし|戦績] ... ]
  - ゲストなし → 集計からゲストを除外（2ゲスト戦も計上する）
  - ゲストあり → 集計にゲストを含める（2ゲスト戦は計上しない）
- 対象プレイヤー ： [登録名|...]
  - 未指定 → 全員
  - 1名 → 個人成績
  - 複数名 → 絞り込み(比較用)

引数についての[詳細](document/argument_keyword.md)
