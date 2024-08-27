import re

import lib.database as d
import lib.function as f
from lib.function import global_value as g


def aggregation():
    """
    各チームの通算ポイントを表示

    Returns
    -------
    msg2 : text
        検索条件などの情報

    msg : dict
        集計結果

    file_list : dict
        ファイル出力用path
    """

    # データ収集
    game_info = d.aggregate.game_info()
    df_summary = d.aggregate.team_total()
    df_summary = df_summary.rename(
        columns={
            "team": "チーム名",
            "pt_total": "通算",
            "rank_distr": "順位分布",
            "count": "ゲーム数",
        }
    )

    # 表示
    msg = {}
    header = "*【チーム成績サマリ】*\n"
    header += f.message.header(game_info, vars(g.prm), "", 1)
    file_list = {}

    if not df_summary.empty:
        data = df_summary.to_markdown(
            index=False,
            tablefmt="simple",
            numalign="right",
            maxheadercolwidths=16,
            floatfmt=("", "+.1f", "", "")
        )
        data = re.sub(r" -([0-9]+)", r"▲\1", data)
        msg[0] = f"```\n{data}\n```"

    return (header, msg, file_list)
