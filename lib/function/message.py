import random
import textwrap

import lib.function as f
from lib.function import global_value as g


def help(command):
    """
    スラッシュコマンド用ヘルプ
    """

    msg = "```使い方："
    msg += f"\n\t{command} help          このメッセージ"
    msg += "\n\t--- 成績管理 ---"
    msg += f"\n\t{command} results       成績出力"
    msg += f"\n\t{command} ranking       ランキング出力"
    msg += f"\n\t{command} graph         ポイント推移グラフを表示"
    msg += f"\n\t{command} report        レポート表示"
    msg += "\n\t--- データベース操作 ---"
    msg += f"\n\t{command} check         データ突合"
    msg += f"\n\t{command} download      データベースダウンロード"
    msg += "\n\t--- メンバー管理 ---"
    msg += f"\n\t{command} member        登録されているメンバー"
    msg += f"\n\t{command} add | del     メンバーの追加/削除"
    msg += "\n\t--- チーム管理 ---"
    msg += f"\n\t{command} team_create <チーム名>            チームの新規作成"
    msg += f"\n\t{command} team_del <チーム名>               チームの削除"
    msg += f"\n\t{command} team_add <チーム名> <メンバー名>  チームにメンバーを登録"
    msg += f"\n\t{command} team_remove <メンバー名>          指定したメンバーを未所属にする"
    msg += f"\n\t{command} team_list                         チーム名と所属メンバーを表示"
    msg += f"\n\t{command} team_clear                        チームデータをすべて削除"
    msg += "```"

    return (msg)


def help_message():
    """
    チャンネル内呼び出しキーワード用ヘルプ
    """

    results_option = g.command_option()
    results_option.initialization("results")
    graph_option = g.command_option()
    graph_option.initialization("graph")
    ranking_option = g.command_option()
    ranking_option.initialization("ranking")
    report_option = g.command_option()
    report_option.initialization("report")

    msg = textwrap.dedent(f"""
        *成績記録キーワード*
        \t{g.config["search"].get("keyword", "終局")}

        *機能呼び出し*
        \t`呼び出しキーワード [検索範囲] [対象メンバー] [オプション]`

        \t*成績サマリ*
        \t\t呼び出しキーワード： {g.commandword['results']}
        \t\t検索範囲デフォルト： {results_option.aggregation_range[0]}
        \t*成績グラフ*
        \t\t呼び出しキーワード： {g.commandword['graph']}
        \t\t検索範囲デフォルト： {graph_option.aggregation_range[0]}
        \t*ランキング*
        \t\t呼び出しキーワード： {g.commandword['ranking']}
        \t\t検索範囲デフォルト： {ranking_option.aggregation_range[0]}
        \t\t規定打数デフォルト： 全体ゲーム数 × {ranking_option.stipulated_rate} ＋ 1
        \t\t出力制限デフォルト： 上位 {ranking_option.ranked} 名
        \t*レポート*
        \t\t呼び出しキーワード： {g.commandword['report']}
        \t\t検索範囲デフォルト： {report_option.aggregation_range[0]}
        \t*メンバー一覧*
        \t\t呼び出しキーワード： {g.commandword['member']}
        \t*チーム一覧*
        \t\t呼び出しキーワード： {g.commandword['team']}

        *オプション*
        \t詳細説明： https://github.com/togakushi/slack-mahjong-score-management/blob/main/docs/functions/argument_keyword.md
    """).strip()

    if g.config.has_section("regulations"):
        additional_rule = "\n\n*追加ルール*\n"
        for word, ex_point in g.config.items("regulations"):
            additional_rule += f"\t{word}： {ex_point}pt\n"
        msg += additional_rule

    return (msg.strip())


def invalid_argument():
    """
    引数解析失敗時のメッセージ
    """

    msg = "使い方が間違っています。"

    if g.config.has_section("custom_message"):
        key_list = []
        for i in g.config["custom_message"]:
            if i.startswith("invalid_argument"):
                key_list.append(i)
        if key_list:
            msg = g.config["custom_message"][random.choice(key_list)]

    return (msg)


def restricted_channel():
    """
    制限チャンネルでキーワードを検出したときのメッセージ
    """

    msg = "この投稿はデータベースに反映されません。"

    if g.config.has_section("custom_message"):
        key_list = []
        for i in g.config["custom_message"]:
            if i.startswith("restricted_channel"):
                key_list.append(i)
        if key_list:
            msg = g.config["custom_message"][random.choice(key_list)]

    return (msg)


def invalid_score(user_id, rpoint_sum, correct_score):
    """
    ゲーム終了時の素点合計が配給原点合計と異なる場合の警告メッセージ
    """

    rpoint_diff = abs(correct_score - rpoint_sum)
    msg = f"素点合計： {rpoint_sum}\n点数差分： {rpoint_diff}"

    if g.config.has_section("custom_message"):
        key_list = []
        for i in g.config["custom_message"]:
            if i.startswith("invalid_score"):
                key_list.append(i)
        if key_list:
            msg = g.config["custom_message"][random.choice(key_list)]

    return (f"<@{user_id}> " + msg.format(
        rpoint_diff=rpoint_diff * 100,
        rpoint_sum=rpoint_sum * 100,
    ))


def no_hits():
    """
    指定範囲に記録用キーワードが見つからなかった場合のメッセージ
    """

    keyword = g.config["search"].get("keyword", "終局")
    start = g.prm.starttime_hm
    end = g.prm.endtime_hm
    msg = f"{start} ～ {end} に≪{keyword}≫はありません。"

    if g.config.has_section("custom_message"):
        key_list = []
        for i in g.config["custom_message"]:
            if i.startswith("no_hits"):
                key_list.append(i)
        if key_list:
            msg = g.config["custom_message"][random.choice(key_list)]

    return (msg.format(keyword=keyword, start=start, end=end))


def remarks():
    """
    引数で指定された集計方法を注記にまとめる
    """

    ret = ""
    remark = []

    if not g.opt.guest_skip:
        remark.append("2ゲスト戦の結果を含む")
    if not g.opt.unregistered_replace:
        remark.append("ゲスト置換なし(" + g.guest_mark + "：未登録プレイヤー)")
    if remark:
        ret = "特記：" + "、".join(remark)

    return (ret)


def header(game_info, params, add_text="", indent=1):
    msg = ""
    tab = "\t" * indent

    # 集計範囲
    game_range1 = f"{tab}最初のゲーム：{game_info['first_game']}\n".replace("-", "/")
    game_range1 += f"{tab}最後のゲーム：{game_info['last_game']}\n".replace("-", "/")
    if g.opt.search_word:  # コメント検索の場合はコメントで表示
        game_range2 = f"{tab}集計範囲： {game_info['first_comment']} ～ {game_info['last_comment']}\n"
    else:
        game_range2 = f"{tab}集計範囲： {game_info['first_game']} ～ {game_info['last_game']}\n".replace("-", "/")

    # ゲーム数
    if game_info["game_count"] == 0:
        msg += f"{tab}{f.message.no_hits()}"
    else:
        match g.opt.command:
            case "results":
                if params["target_count"]:  # 直近指定がない場合は検索範囲を付ける
                    msg += game_range1
                    msg += f"{tab}総ゲーム数：{game_info['game_count']} 回{add_text}\n"
                else:
                    msg += f"{tab}検索範囲： {params['starttime_hms']} ～ {params['endtime_hms']}\n"
                    msg += game_range1
                    msg += f"{tab}ゲーム数：{game_info['game_count']} 回{add_text}\n"
            case "ranking":
                msg += game_range2
                msg += f"{tab}集計ゲーム数：{game_info['game_count']} (規定数：{g.opt.stipulated} 以上)\n"
            case _:
                msg += game_range2
                msg += f"{tab}総ゲーム数：{game_info['game_count']} 回\n"
        msg += tab + f.message.remarks()

    return (msg)
