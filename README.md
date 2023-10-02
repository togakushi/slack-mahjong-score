# slack-mahjong-score-management

## 概要

slackに投稿されたスコアを集計するツール

「御無礼成績」で今月の成績（トータルポイント集計）
「御無礼記録」「御無礼結果」でスプレッドシート貼り付け用集計済みデータ
「御無礼グラフ」でその日のポイント推移グラフ
「御無礼ランキング」で各成績の順位

をチャンネル内に表示する。

## 簡易マニュアル

【コマンド書式】

- 御無礼成績 [集計範囲] [対象プレイヤー] [オプション]
- 御無礼グラフ [集計範囲] [対象プレイヤー] [オプション]
- 御無礼記録 [オプション]
- /goburei 成績管理サブコマンド [集計範囲] [対象プレイヤー] [オプション]
- /goburei メンバー管理サブコマンド [対象プレイヤー]

【引数内容】

- 集計範囲 ： [[当日|今日|昨日|今月|先月|先々月|全部|YYYYMMDD] ... ]
- オプション ： [[ゲストなし|ゲストあり|修正なし|戦績] ... ]
  - ゲストなし → 集計からゲストを除外（2ゲスト戦も計上する）
  - ゲストあり → 集計にゲストを含める（2ゲスト戦は計上しない）
  - 修正なし → 名前ブレを修正しない（ポストされた名前のまま出す）
- 対象プレイヤー ： [登録名|...]
  - 未指定 → 全員
  - 1名 → 個人成績
  - 複数名 → 絞り込み(比較用)

引数についての[詳細](document/argument_keyword.md)

### グラフ生成機能

獲得ポイントの推移グラフを出力する。

- [詳細](document/graph.md)

### 御無礼コマンド( /goburei )

- [使い方](document/command.md)
