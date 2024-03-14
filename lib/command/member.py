import re
import sqlite3

import lib.function as f
import lib.command as c
import lib.database as d
from lib.function import global_value as g


def NameReplace(pname, command_option, add_mark = False):
    """
    表記ブレ修正(正規化)

    Parameters
    ----------
    pname : str
        対象文字列（プレイヤー名）

    command_option : dict
        コマンドオプション

    Returns
    -------
    name : str
        表記ブレ修正後のプレイヤー名
    """

    pname = f.translation.HAN2ZEN(pname)
    check_list = list(set(g.member_list.keys()))

    if pname in check_list:
        return(g.member_list[pname])

    # 敬称削除
    honor = r"(くん|さん|ちゃん|クン|サン|チャン|君)$"
    if re.match(fr".*{honor}", pname):
        if not re.match(fr".*(っ|ッ){honor}", pname):
            pname = re.sub(fr"{honor}", "", pname)
    if pname in check_list:
        return(g.member_list[pname])

    # ひらがな、カタカナでチェック
    if f.translation.KANA2HIRA(pname) in check_list:
        return(g.member_list[f.translation.KANA2HIRA(pname)])
    if f.translation.HIRA2KANA(pname) in check_list:
        return(g.member_list[f.translation.HIRA2KANA(pname)])

    # メンバーリストに見つからない場合
    if command_option.get("unregistered_replace"):
        return(g.guest_name)
    else:
        if add_mark:
            return(f"{pname}({g.guest_mark})")
        else:
            return(pname)


def CountPadding(data):
    """
    """
    name_list = []

    if type(data) is list:
        name_list = data

    if type(data) is dict:
        for i in data.keys():
            for name in [data[i][x]["name"] for x in g.wind[0:4]]:
                if name not in name_list:
                    name_list.append(name)

    if name_list:
        return(max([f.translation.len_count(x) for x in name_list]))
    else:
        return(0)


def Getmemberslist():
    title = "登録済みメンバー一覧"
    padding = c.member.CountPadding(list(set(g.member_list.values())))
    msg = "# 表示名{}： 登録されている名前 #\n".format(" " * (padding - 8))

    for pname in set(g.member_list.values()):
        name_list = []
        for alias in g.member_list.keys():
            if g.member_list[alias] == pname:
                name_list.append(alias)
        msg += "{}{}： {}\n".format(
            pname,
            " " * (padding - f.translation.len_count(pname)),
            ", ".join(name_list),
        )

    return(title, msg)


def MemberAppend(argument):
    """
    メンバー追加

    Parameters
    ----------
    argument : list
        argument[0] = 登録するプレイヤー名
        argument[1] = 登録する別名

    Returns
    -------
    msg : text
        slackにpostする内容
    """

    resultdb = sqlite3.connect(g.database_file, detect_types = sqlite3.PARSE_DECLTYPES)
    resultdb.row_factory = sqlite3.Row

    ret = False
    dbupdate_flg = False
    msg = "使い方が間違っています。"

    if len(argument) == 1: # 新規追加
        new_name = f.translation.HAN2ZEN(argument[0])
        g.logging.notice(f"new member: {new_name}") # type: ignore

        rows = resultdb.execute("select count() from member")
        count = rows.fetchone()[0]
        if count > g.config["member"].getint("registration_limit", 255):
            msg = f"登録上限を超えています。"
        else: # 登録処理
            ret, msg = f.common.check_namepattern(new_name)
            if ret:
                resultdb.execute(f"insert into member(name) values (?)", (new_name,))
                resultdb.execute(f"insert into alias(name, member) values (?,?)", (new_name, new_name))
                msg = f"「{new_name}」を登録しました。"

    if len(argument) == 2: # 別名登録
        new_name = f.translation.HAN2ZEN(argument[0])
        nic_name = f.translation.HAN2ZEN(argument[1])
        g.logging.notice(f"alias: {new_name} -> {nic_name}") # type: ignore

        registration_flg = True
        rows = resultdb.execute("select count() from alias where member=?", (new_name,))
        count = rows.fetchone()[0]
        if count == 0:
            msg = f"「{new_name}」はまだ登録されていません。"
            registration_flg = False
        if count > g.config["member"].getint("alias_limit", 16):
            msg = f"登録上限を超えています。"
            registration_flg = False

        if registration_flg: # 登録処理
            ret, msg = f.common.check_namepattern(nic_name)
            if ret:
                resultdb.execute("insert into alias(name, member) values (?,?)", (nic_name, new_name))
                msg = f"「{new_name}」に「{nic_name}」を追加しました。"
                dbupdate_flg = True

        if dbupdate_flg:
            rows = resultdb.execute(
                """select count() from result
                    where ? in (p1_name, p2_name, p3_name, p4_name)
                    or ? in (p1_name, p2_name, p3_name, p4_name)
                    or ? in (p1_name, p2_name, p3_name, p4_name)
                """, (nic_name, f.translation.KANA2HIRA(nic_name), f.translation.HIRA2KANA(nic_name)))
            count = rows.fetchone()[0]
            if count != 0: # 過去成績更新
                msg += d.common.database_backup()
                for col in ("p1_name", "p2_name", "p3_name", "p4_name"):
                    resultdb.execute(f"update result set {col}=? where {col}=?", (new_name, nic_name))
                    resultdb.execute(f"update result set {col}=? where {col}=?", (new_name, f.translation.KANA2HIRA(nic_name)))
                    resultdb.execute(f"update result set {col}=? where {col}=?", (new_name, f.translation.HIRA2KANA(nic_name)))
                msg += "\nデータベースを更新しました。"

    resultdb.commit()
    resultdb.close()
    f.configure.read_memberslist()

    return(msg)


def MemberRemove(argument):
    """
    メンバー削除

    Parameters
    ----------
    argument : list
        argument[0] = 削除するプレイヤー名
        argument[1] = 削除する別名

    Returns
    -------
    msg : text
        slackにpostする内容
    """

    resultdb = sqlite3.connect(g.database_file, detect_types = sqlite3.PARSE_DECLTYPES)
    resultdb.row_factory = sqlite3.Row

    msg = "使い方が間違っています。"

    if len(argument) == 1: # メンバー削除
        new_name = f.translation.HAN2ZEN(argument[0])
        g.logging.notice(f"remove member: {new_name}") # type: ignore

        if new_name in g.member_list:
            resultdb.execute("delete from member where name=?", (new_name,))
            resultdb.execute("delete from alias where member=?",(new_name,))
            msg = f"「{new_name}」を削除しました。"
        else:
            msg = f"「{new_name}」は登録されていません。"

    if len(argument) == 2: # 別名削除
        new_name = f.translation.HAN2ZEN(argument[0])
        nic_name = f.translation.HAN2ZEN(argument[1])
        g.logging.notice(f"alias remove: {new_name} -> {nic_name}") # type: ignore

        if nic_name in g.member_list:
            resultdb.execute("delete from alias where name=? and member=?",(nic_name, new_name))
            msg = f"「{new_name}」から「{nic_name}」を削除しました。"
        else:
            msg = f"「{new_name}」に「{nic_name}」は登録されていません。"

    resultdb.commit()
    resultdb.close()
    f.configure.read_memberslist()

    return(msg)
