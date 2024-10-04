import logging
import re

import global_value as g
from cls.search import CommandCheck
from lib import command as c
from lib import database as d
from lib import function as f


def import_only():
    pass


# イベントAPI
@g.app.event("message")
def handle_message_events(client, body):
    """
    ポストされた内容で処理を分岐
    """

    logging.trace(body)  # type: ignore
    g.msg.parser(body)
    g.msg.client = client

    # 許可されていないユーザのポストは処理しない
    if g.msg.user_id in g.cfg.setting.ignore_userid:
        logging.trace(f"event skip[ignore user]: {g.msg.user_id}")  # type: ignore
        return

    logging.info(f"{vars(g.msg)}")

    match g.msg.keyword:
        # ヘルプ
        case x if re.match(rf"^{g.cfg.cw.help}$", x):
            # ヘルプメッセージ
            f.slack_api.post_message(f.message.help_message(), g.msg.event_ts)
            # メンバーリスト
            title, msg = c.member.Getmemberslist()
            f.slack_api.post_text(g.msg.event_ts, title, msg)

        # 成績管理系コマンド
        case x if re.match(rf"^{g.cfg.cw.results}", x):
            c.results.slackpost.main()
        case x if re.match(rf"^{g.cfg.cw.graph}", x):
            c.graph.slackpost.main()
        case x if re.match(rf"^{g.cfg.cw.ranking}", x):
            c.ranking.slackpost.main()
        case x if re.match(rf"^{g.cfg.cw.report}", x):
            c.report.slackpost.main()

        # データベース関連コマンド
        case x if re.match(rf"^{g.cfg.cw.check}", x):
            d.comparison.main()
        case x if re.match(rf"^Reminder: {g.cfg.cw.check}$", g.msg.text):  # Reminderによる突合
            logging.info(f'Reminder: {g.cfg.cw.check}')
            d.comparison.main()

        # メンバーリスト/チームリスト
        case x if re.match(rf"^{g.cfg.cw.member}", x):
            title, msg = c.member.Getmemberslist()
            f.slack_api.post_text(g.msg.event_ts, title, msg)
        case x if re.match(rf"^{g.cfg.cw.team}", x):
            title = "チーム一覧"
            msg = c.team.list()
            f.slack_api.post_text(g.msg.event_ts, title, msg)

        # 追加メモ
        case x if re.match(rf"^{g.cfg.cw.remarks_word}", x) and g.msg.thread_ts:
            if d.common.ExsistRecord(g.msg.thread_ts) and g.msg.updatable:
                f.score.check_remarks()

        # 結果報告フォーマットに一致したポストの処理
        case _:
            detection = f.search.pattern(g.msg.text)
            match g.msg.status:
                case "message_append":
                    if detection:
                        f.score.check_score(detection)
                        if g.msg.updatable:
                            d.common.resultdb_insert(detection, g.msg.event_ts)
                        else:
                            f.slack_api.post_message(f.message.restricted_channel(), g.msg.event_ts)
                case "message_changed":
                    print(f"DEBUG> {body=}")  # todo: エラー解析用
                    if detection:
                        f.score.check_score(detection)
                        if g.msg.updatable:
                            if d.common.ExsistRecord(g.msg.event_ts):
                                d.common.resultdb_update(detection, g.msg.event_ts)
                            else:
                                d.common.resultdb_insert(detection, g.msg.event_ts)
                        else:
                            f.slack_api.post_message(f.message.restricted_channel(), g.msg.event_ts)
                    else:
                        f.slack_api.call_reactions_remove()
                        if d.common.ExsistRecord(g.msg.event_ts):
                            d.common.resultdb_delete(g.msg.event_ts)
                case "message_deleted":
                    if d.common.ExsistRecord(g.msg.event_ts):
                        d.common.resultdb_delete(g.msg.event_ts)


@g.app.command(g.cfg.setting.slash_command)
def slash_command(ack, body, client):
    """
    スラッシュコマンド
    """

    ack()
    logging.trace(f"{body}")  # type: ignore
    g.msg.parser(body)
    g.msg.client = client

    if g.msg.text:
        match CommandCheck(g.msg.keyword):
            # 成績管理系コマンド
            case "results":
                c.results.slackpost.main()
            case "graph":
                c.graph.slackpost.main()
            case "ranking":
                c.ranking.slackpost.main()
            case "report":
                c.report.slackpost.main()

            # データベース関連コマンド
            case "check":
                d.comparison.main()
            case "download":
                f.slack_api.post_fileupload("resultdb", g.cfg.db.database_file)

            # メンバー管理系コマンド
            case "member":
                title, msg = c.member.Getmemberslist()
                f.slack_api.post_text(g.msg.event_ts, title, msg)
            case "add":
                f.slack_api.post_message(c.member.MemberAppend(g.msg.argument))
            case "del":
                f.slack_api.post_message(c.member.MemberRemove(g.msg.argument))

            # チーム管理系コマンド
            case "team_create":
                f.slack_api.post_message(c.team.create(g.msg.argument))
            case "team_del":
                f.slack_api.post_message(c.team.delete(g.msg.argument))
            case "team_add":
                f.slack_api.post_message(c.team.append(g.msg.argument))
            case "team_remove":
                f.slack_api.post_message(c.team.remove(g.msg.argument))
            case "team_list":
                f.slack_api.post_message(c.team.list())
            case "team_clear":
                f.slack_api.post_message(c.team.clear())

            # その他
            case _:
                f.slack_api.post_message(f.message.help(body["command"]))


@g.app.event("reaction_added")
def handle_reaction_added_events():
    pass  # reaction_added はすべて無視する


@g.app.event("reaction_removed")
def handle_reaction_removed_events():
    pass  # reaction_removed はすべて無視する
