import sys
import sqlite3
import configparser

from lib.function import global_value as g


def parameter_load():
    # database読み込み
    resultdb = sqlite3.connect(g.database_file, detect_types = sqlite3.PARSE_DECLTYPES)
    resultdb.row_factory = sqlite3.Row

    rows = resultdb.execute("select name from member where id=0")
    g.guest_name = rows.fetchone()[0]

    g.member_list = {}
    rows = resultdb.execute("select name, member from alias")
    for row in rows.fetchall():
        if not row["member"] in g.member_list:
            g.member_list[row["member"]] = row["member"]
        if not row["name"] in g.member_list:
            g.member_list[row["name"]] = row["member"]

    resultdb.close()

    g.logging.info(f"guest_name: {g.guest_name}")
    g.logging.info(f"member_list: {set(g.member_list.values())}")


def command_option_initialization(command):
    """
    設定ファイルからコマンドのオプションのデフォルト値を読み込む

    Parameters
    ----------
    command : str
        読み込むコマンド名

    Returns
    -------
    option : dict
        初期化されたオプション
    """

    option = {
        "aggregation_range": [],
        "recursion": True,
        "all_player": False,
        "order": False,
        "verbose": False,
    }

    option["aggregation_range"].append(g.config[command].get("aggregation_range", "当日"))
    option["unregistered_replace"] = g.config[command].getboolean("unregistered_replace", True)
    option["guest_skip"] = g.config[command].getboolean("guest_skip", True)
    option["guest_skip2"] = g.config[command].getboolean("guest_skip2", True)
    option["score_comparisons"] = g.config[command].getboolean("score_comparisons", False)
    option["game_results"] = g.config[command].getboolean("game_results", False)
    option["versus_matrix"] = g.config[command].getboolean("versus_matrix", False)
    option["ranked"] = g.config[command].getint("ranked", 3)
    option["stipulated_rate"] = g.config[command].getfloat("stipulated_rate", 0.05)

    return(option)
