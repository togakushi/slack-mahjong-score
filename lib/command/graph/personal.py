import os

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib import gridspec

import lib.function as f
import lib.database as d
from lib.function import global_value as g


mlogger = g.logging.getLogger("matplotlib")
mlogger.setLevel(g.logging.WARNING)


def plot(argument, command_option):
    """
    個人成績のグラフを生成する

    Parameters
    ----------
    argument : list
        slackから受け取った引数

    command_option : dict
        コマンドオプション

    Returns
    -------
    game_count : int
        グラフにプロットしたゲーム数

    text : text
        検索結果が0件のときのメッセージ or
        グラフ画像保存パス
    """

    # 検索動作を合わせる
    command_option["guest_skip"] = command_option["guest_skip2"]

    # --- データ収集 ToDo: 仮置き換え
    params = f.configure.get_parameters(argument, command_option)
    total_game_count, _, _ = d.aggregate.game_count(argument, command_option)
    df = d.aggregate.personal_gamedata(argument, command_option)

    if total_game_count == 0:
        return(total_game_count, f.message.no_hits(argument, command_option))

    ### グラフ生成 ###
    f.common.set_graph_font(plt, fm)
    save_file = os.path.join(g.work_dir, "graph.png")

    plt.style.use("ggplot")
    fig = plt.figure(figsize = (12, 8))

    if params["target_count"] == 0:
        title_text = f"『{params['player_name']}』の成績 ({params['starttime_hm']} - {params['endtime_hm']})"
    else:
        title_text = f"『{params['player_name']}』の成績 (直近 {total_game_count} ゲーム)"

    grid = gridspec.GridSpec(nrows = 2, ncols = 1, height_ratios = [3, 1])
    point_ax = fig.add_subplot(grid[0])
    rank_ax = fig.add_subplot(grid[1], sharex = point_ax)

    # ---
    df.filter(items = ["point_sum", "point_avg"]).plot.line(
        ax = point_ax,
        ylabel = "ポイント(pt)",
        marker = "." if len(df) < 50 else None,
    )
    df.filter(items = ["point"]).plot.bar(
        ax = point_ax,
        color = "blue",
    )
    point_ax.legend(
        ["累積ポイント", "平均ポイント", "獲得ポイント"],
        bbox_to_anchor = (1, 1),
        loc = "upper left",
        borderaxespad = 0.5,
    )
    point_ax.axhline(y = 0, linewidth = 0.5, ls = "dashed", color = "grey")

    # Y軸修正
    ylabs = point_ax.get_yticks()[1:-1]
    point_ax.set_yticks(ylabs)
    point_ax.set_yticklabels([str(int(ylab)).replace("-", "▲") for ylab in ylabs])

    # ---
    df.filter(items = ["rank", "rank_avg"]).plot.line(
        ax = rank_ax,
        marker = "." if len(df) < 50 else None,
        yticks = [1, 2, 3, 4],
        ylabel = "順位",
        xlabel = f"ゲーム終了日時（{total_game_count} ゲーム）",
    )
    rank_ax.legend(
        ["獲得順位","平均順位"],
        bbox_to_anchor = (1, 1),
        loc = "upper left",
        borderaxespad = 0.5,
    )

    rank_ax.set_xticks(list(df.index)[::int(len(df) / 25) + 1])
    rank_ax.set_xticklabels(list(df["playtime"])[::int(len(df) / 25) + 1], rotation = 45, ha = "right")
    rank_ax.axhline(y = 2.5, linewidth = 0.5, ls = "dashed", color = "grey")
    rank_ax.invert_yaxis()

    fig.suptitle(title_text, fontsize = 16)
    fig.tight_layout()
    plt.savefig(save_file, bbox_inches = "tight")

    return(total_game_count, save_file)
