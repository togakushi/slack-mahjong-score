# slack-mahjong-score-management

## 概要
slackに投稿されたスコアを集計するツール

## Long description
「御無礼成績」で今月の成績（トータルポイント集計）
「御無礼記録」「御無礼結果」でスプレッドシート貼り付け用集計済みデータ
「御無礼グラフ」でその日のポイント推移グラフ

をチャンネル内に表示する。


【御無礼コマンド( /goburei )の使い方】
結果はアプリからDMで通知される。
　/goburei results						今月の成績を表示
　/goburei record						スプレッドシート貼り付け用集計済みデータ出力
　/goburei allrecord					集計済み全データ出力(名前ブレ修正なし)
　/goburei graph [引数]		ポイント推移グラフを表示
　/goburei details <登録名>	2ゲスト戦含む個人成績出力
　/goburei member					登録されているメンバーを表示
　/goburei userlist					登録されているメンバーを表示
　/goburei add <登録名>			メンバーの追加
　/goburei del <登録名>			メンバーの削除
　/goburei load							メンバーリストの再読み込み
　/goburei save							メンバーリストの保存

　[コマンドエイリアス]
　　results → 成績
　　record → 記録、結果
　　allrecord → 全記録、全結果
　　graph → グラフ
　　details → 詳細、個人成績
　　member → メンバー
　　userlist → リスト
　　add → 追加
　　del → 削除

【メンバーの追加削除について】
　・「/goburei add <登録名>」でメンバーの新規追加
　・「/goburei add <登録名> <別名>」で別名のニックネームを追加
　・「/goburei del <登録名>」でメンバーを削除(ゲスト扱い)
　・「/goburei del <登録名> <別名>」でニックネームを削除

　[注意事項]
　　・最大登録人数は255人です。
　　・登録できる名前は8文字以内です。
　　・ニックネームは16個まで登録できます。
　　・半角数字は登録時に全角へ置換されます。
　　・一部の記号は使用できません。
　　・addした時点で集計対象になります。
　　・saveを実行するまでファイルには書き込まれません（アプリ停止時に消えます）。

【グラフ表示機能】
引数未指定で当日のポイント推移グラフの表示。
YYYYMMDD形式の日付を引数に与えると過去の成績をグラフ化する。
「先々月」「先月」「今月」で一ヶ月分のグラフを表示する。

============================================================

【検索アルゴリズム】
　1. 過去ログから「御無礼」を含むすべてのメッセージを検索
　2. 実行月の1日午前12時以降のメッセージを抽出
　3. メッセージ内の改行を削除
　4. 下記のパターンにマッチするメッセージを抽出
　    '^御無礼 ?([^0-9+-]+ ?[0-9+-]+ ?){4}'
　    ' ?[^0-9+-]+ ?[0-9+-]+ ?){4}御無礼$'


【名前表記ブレ修正アルゴリズム】
　1. 検索で抽出されたメッセージからキーワード「御無礼」を削除
　2. すべての空白を削除
　3. 「([^0-9+-]+)([0-9+-]+)」を4回繰り返したパターンにマッチさせ、名前と素点を分離
　4. 敬称の「さん」を削除
　5. 登録リストと名前を順に比較し、一致したら名前を登録名と置き換える
　6. 登録リストと一致しない名前は「ゲスト１」に置き換える


【ポイント集計アルゴリズム】
　1. 素点に含まれる計算式を計算した結果で置き換える
　2. 同点があった場合に席順で差が出るように起家に「0.000004」点、南家に「0.000003」点・・・を北家まで加算していく
　3. 素点だけの配列を新しく作り、数値の大きい順にソートする
　4. 持ち点が素点の配列上の何番目にあるかを検索し、順位とする
　5. 取得した順位をもとにウマ・オカを素点に加え、獲得ポイントを算出し名前とポイント(小数点第1位で切り捨て)を記録する
　6. 集計対象の半荘内に「ゲスト１」が1名以下の場合、名前をキーにしてポイントを加算していく
　    ゲストが2名同卓した半荘は集計対象外となる