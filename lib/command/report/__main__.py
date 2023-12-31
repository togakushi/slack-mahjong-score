import lib.function as f
from lib.function import global_value as g

from lib.command.report import monthly
from lib.command.report import personal


def slackpost(client, channel, argument, command_option):
    """
    xx

    Parameters
    ----------
    client : obj

    channel : str
        post先のチャンネルID or ユーザーID

    argument : list
        slackから受け取った引数
        解析対象のプレイヤー、検索範囲などが指定される

    command_option : dict
        コマンドオプション
    """

    g.logging.info(f"arg: {argument}")
    g.logging.info(f"opt: {command_option}")

    #report_file_path = monthly.plot(argument, command_option)
    #f.slack_api.post_fileupload(client, channel, "月別ゲーム統計", report_file_path)

    report_file_path = personal.plot(argument, command_option)
    f.slack_api.post_fileupload(client, channel, "個人成績", report_file_path)
