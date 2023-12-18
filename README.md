# slack-mahjong-score-management

## 概要

slackに投稿された麻雀のスコアを記録、集計するツール

## 主な機能

### スコア記録（[詳細](docs/functions/score_record.md)）

以下のフォーマットに一致した投稿をデータベースに取り込む
```
<指定キーワード>
東家プレイヤー名 東家素点
南家プレイヤー名 南家素点
西家プレイヤー名 西家素点
北家プレイヤー名 北家素点
```

### 成績サマリ出力機能（[詳細](docs/functions/summary.md)）

記録されているスコアを集計し、一覧で出力する。
  
### グラフ生成機能（[詳細](docs/functions/graph.md)）

記録されているスコアを集計し、グラフで出力する。

### ランキング出力機能（[詳細](docs/functions/ranking.md)）

記録されているスコアを集計し、ランキング形式で出力する。

### スラッシュコマンド（[使い方](docs/functions/command.md)）

出力結果をボットから直接DMで受け取る。

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

引数についての[詳細](docs/functions/argument_keyword.md)
