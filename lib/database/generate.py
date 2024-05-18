import lib.database as d
from lib.function import global_value as g


def game_count(argument, command_option):
    """
    ゲーム数をカウントするSQLを返す
    """

    params = d.common.placeholder_params(argument, command_option)
    sql = """
        select
            count() as count,
            min(playtime) as first_game,
            max(playtime) as last_game
        from (
            select
                playtime
            from
                individual_results
            where
                rule_version = :rule_version
                and playtime between :starttime and :endtime -- 検索範囲
                --[guest_not_skip] and playtime not in (select playtime from individual_results group by playtime having sum(guest) >= 2) -- ゲストあり
                --[player_name] and name in (<<player_list>>) -- 対象プレイヤー
            group by
                playtime
            order by
                playtime desc
            --[recent] limit :target_count
        )
    """

    if params["player_name"]:
        sql = sql.replace("--[player_name] ", "")
        sql = sql.replace("<<player_list>>", ":" + ", :".join([x for x in params["player_list"].keys()]))

    if command_option["unregistered_replace"]:
        sql = sql.replace("--[unregistered_replace] ", "")
        if command_option["guest_skip"]:
            sql = sql.replace("--[guest_not_skip] ", "")
        else:
            sql = sql.replace("--[guest_skip] ", "")
    else:
        sql = sql.replace("--[unregistered_not_replace] ", "")

    if params["target_count"] != 0:
        sql = sql.replace("and playtime between", "-- and playtime between")
        sql = sql.replace("--[recent] ", "")

    g.logging.trace(f"sql: {sql}") # type: ignore
    return(sql)


def record_count(argument, command_option):
    """
    連測連対などの記録をカウントするSQLを生成
    """

    params = d.common.placeholder_params(argument, command_option)
    sql = """
        select
            playtime,
            --[unregistered_replace] case when guest = 0 then name else :guest_name end as "プレイヤー名", -- ゲスト有効
            --[unregistered_not_replace] name as "プレイヤー名", -- ゲスト無効
            rank as "順位",
            point as "獲得ポイント",
            rpoint as "最終素点"
        from
            individual_results
        where
            rule_version = :rule_version
            and playtime between :starttime and :endtime
            --[guest_not_skip] and playtime not in (select playtime from individual_results group by playtime having sum(guest) >= 2) -- ゲストあり
            --[guest_skip] and guest = 0 -- ゲストなし
            --[player_name] and name in (<<player_list>>) -- 対象プレイヤー
        --[recent] limit :target_count
    """

    if params["player_name"]:
        sql = sql.replace("--[player_name] ", "")
        sql = sql.replace("<<player_list>>", ":" + ", :".join([x for x in params["player_list"].keys()]))

    if command_option["unregistered_replace"]:
        sql = sql.replace("--[unregistered_replace] ", "")
        if command_option["guest_skip"]:
            sql = sql.replace("--[guest_not_skip] ", "")
        else:
            sql = sql.replace("--[guest_skip] ", "")
    else:
        sql = sql.replace("--[unregistered_not_replace] ", "")

    if params["target_count"] != 0:
        sql = sql.replace("and playtime between", "-- and playtime between")
        sql = sql.replace("--[recent] ", "")

    return(sql)


def game_results(argument, command_option):
    """
    ゲーム結果を集計するSQLを生成
    """
    params = d.common.placeholder_params(argument, command_option)
    sql = """
        select
            name,
            count() as count,
            round(sum(point), 1) as pt_total,
            round(avg(point), 1) as pt_avg,
            count(rank = 1 or null) as "1st",
            count(rank = 2 or null) as "2nd",
            count(rank = 3 or null) as "3rd",
            count(rank = 4 or null) as "4th",
            round(avg(rank), 2) as rank_avg,
            count(rpoint < 0 or null) as flying
        from (
            select
                --[unregistered_replace] case when guest = 0 then name else :guest_name end as name, -- ゲスト有効
                --[unregistered_not_replace] name, -- ゲスト無効
                rpoint, rank, point, guest, rule_version
            from
                individual_results
            where
                rule_version = :rule_version
                and playtime between :starttime and :endtime -- 検索範囲
                --[guest_not_skip] and playtime not in (select playtime from individual_results group by playtime having sum(guest) >= 2) -- ゲストあり
                --[guest_skip] and guest = 0 -- ゲストなし
                --[player_name] and name in (<<player_list>>) -- 対象プレイヤー
            order by
                playtime desc
            --[recent] limit :target_count
        )
        group by
            name
        having
            count() >= :stipulated -- 規定打数
        order by
            pt_total desc
    """

    if params["player_name"]:
        sql = sql.replace("--[player_name] ", "")
        sql = sql.replace("<<player_list>>", ":" + ", :".join([x for x in params["player_list"].keys()]))

    if command_option["unregistered_replace"]:
        sql = sql.replace("--[unregistered_replace] ", "")
        if command_option["guest_skip"]:
            sql = sql.replace("--[guest_not_skip] ", "")
        else:
            sql = sql.replace("--[guest_skip] ", "")
    else:
        sql = sql.replace("--[unregistered_not_replace] ", "")

    if params["target_count"] != 0:
        sql = sql.replace("and playtime between", "-- and playtime between")
        sql = sql.replace("--[recent] ", "")

    g.logging.trace(f"sql: {sql}") # type: ignore
    return(sql)


def personal_results(argument, command_option):
    """
    個人成績を集計するSQLを生成
    """

    params = d.common.placeholder_params(argument, command_option)
    sql = """
        select
            name as プレイヤー名,
            count() as ゲーム数,
            count(point > 0 or null) as win,
            count(point < 0 or null) as lose,
            count(point = 0 or null) as draw,
            count(rank = 1 or null) as '1位',
            round(cast(count(rank = 1 or null) as real) / count() * 100, 2) as '1位率',
            count(rank = 2 or null) as '2位',
            round(cast(count(rank = 2 or null) as real) / count() * 100, 2) as '2位率',
            count(rank = 3 or null) as '3位',
            round(cast(count(rank = 3 or null) as real) / count() * 100, 2) as '3位率',
            count(rank = 4 or null) as '4位',
            round(cast(count(rank = 4 or null) as real) / count() * 100, 2) as '4位率',
            round(avg(rpoint) * 100, 1) as 平均最終素点,
            round(sum(point), 1) as 累積ポイント,
            round(avg(point), 1) as 平均ポイント,
            round(avg(rank), 2) as 平均順位,
            count(rpoint < 0 or null) as トビ,
            round(cast(count(rpoint < 0 or null) as real) / count() * 100, 2) as トビ率,
            ifnull(sum(gs_count), 0) as 役満和了,
            round(cast(ifnull(sum(gs_count), 0) as real) / count() * 100, 2) as 役満和了率,
            round((avg(rpoint) - :origin_point) * 100, 1) as 平均収支,
            round((avg(rpoint) - :return_point) * 100, 1) as 平均収支2,
            count(rank <= 2 or null) as 連対,
            round(cast(count(rank <= 2 or null) as real) / count() * 100, 2) as 連対率,
            count(rank <= 3 or null) as ラス回避,
            round(cast(count(rank <= 3 or null) as real) / count() * 100, 2) as ラス回避率,
            -- 座席順位分布
            count(seat = 1 and rank = 1 or null) as '東家-1位',
            count(seat = 1 and rank = 2 or null) as '東家-2位',
            count(seat = 1 and rank = 3 or null) as '東家-3位',
            count(seat = 1 and rank = 4 or null) as '東家-4位',
            round(avg(case when seat = 1 then rank end), 2) as '東家-平均順位',
            count(seat = 1 and matter != '' or null) as '東家-役満和了',
            count(seat = 1 and rpoint < 0 or null) as '東家-トビ',
            count(seat = 2 and rank = 1 or null) as '南家-1位',
            count(seat = 2 and rank = 2 or null) as '南家-2位',
            count(seat = 2 and rank = 3 or null) as '南家-3位',
            count(seat = 2 and rank = 4 or null) as '南家-4位',
            round(avg(case when seat = 2 then rank end), 2) as '南家-平均順位',
            count(seat = 2 and matter != '' or null) as '南家-役満和了',
            count(seat = 2 and rpoint < 0 or null) as '南家-トビ',
            count(seat = 3 and rank = 1 or null) as '西家-1位',
            count(seat = 3 and rank = 2 or null) as '西家-2位',
            count(seat = 3 and rank = 3 or null) as '西家-3位',
            count(seat = 3 and rank = 4 or null) as '西家-4位',
            round(avg(case when seat = 3 then rank end), 2) as '西家-平均順位',
            count(seat = 3 and matter != '' or null) as '西家-役満和了',
            count(seat = 3 and rpoint < 0 or null) as '西家-トビ',
            count(seat = 4 and rank = 1 or null) as '北家-1位',
            count(seat = 4 and rank = 2 or null) as '北家-2位',
            count(seat = 4 and rank = 3 or null) as '北家-3位',
            count(seat = 4 and rank = 4 or null) as '北家-4位',
            round(avg(case when seat = 4 then rank end), 2) as '北家-平均順位',
            count(seat = 4 and matter != '' or null) as '北家-役満和了',
            count(seat = 4 and rpoint < 0 or null) as '北家-トビ',
            min(playtime) as first_game,
            max(playtime) as last_game
        from (
            select
                playtime,
                --[unregistered_replace] case when guest = 0 then individual_results.name else :guest_name end as name, -- ゲスト有効
                --[unregistered_not_replace] individual_results.name, -- ゲスト無効
                rpoint,
                rank,
                point,
                seat,
                matter,
                gs_count
            from
                individual_results
            left outer join
                (select thread_ts, name, count() as gs_count, matter from remarks group by thread_ts, name) as remarks
                on individual_results.ts = remarks.thread_ts and individual_results.name = remarks.name
            where
                rule_version = :rule_version
                and playtime between :starttime and :endtime
                --[guest_not_skip] and playtime not in (select playtime from individual_results group by playtime having sum(guest) > 1) -- ゲストあり(2ゲスト戦除外)
                --[guest_skip] and guest = 0 -- ゲストなし
                --[player_name] and individual_results.name in (<<player_list>>) -- 対象プレイヤー
            order by
                playtime desc
            --[recent] limit :target_count * 4 -- 直近N(縦持ちなので4倍する)
        )
        group by
            name
        having
            count() >= :stipulated -- 規定打数
        order by
            sum(point) desc
    """

    if params["player_name"]:
        sql = sql.replace("--[player_name] ", "")
        sql = sql.replace("<<player_list>>", ":" + ", :".join([x for x in params["player_list"].keys()]))

    if command_option["unregistered_replace"]:
        sql = sql.replace("--[unregistered_replace] ", "")
        if command_option["guest_skip"]:
            sql = sql.replace("--[guest_not_skip] ", "")
        else:
            sql = sql.replace("--[guest_skip] ", "")
    else:
        sql = sql.replace("--[unregistered_not_replace] ", "")

    if params["target_count"] != 0:
        sql = sql.replace("and playtime between", "-- and playtime between")
        sql = sql.replace("--[recent] ", "")

    g.logging.trace(f"sql: {sql}") # type: ignore
    return(sql)


def game_details(argument, command_option):
    """
    ゲーム結果の詳細を返すSQLを生成
    """

    params = d.common.placeholder_params(argument, command_option)
    sql = """
        select * from (
            select
                playtime, ts,
                p1_guest + p2_guest + p3_guest + p4_guest as guest_count,
                p1_name, p1_rpoint * 100 as p1_rpoint, p1_rank, p1_point,
                p2_name, p2_rpoint * 100 as p2_rpoint, p2_rank, p2_point,
                p3_name, p3_rpoint * 100 as p3_rpoint, p3_rank, p3_point,
                p4_name, p4_rpoint * 100 as p4_rpoint, p4_rank, p4_point
            from
                game_results
            where
                rule_version = :rule_version
                and playtime between :starttime and :endtime
                --<<select player>>--
            order by
                playtime desc
            --[recent] limit :target_count
        )
        order by
            playtime
        """

    if params["player_list"]:
        rep_str = "--<<select player>>--"
        for pname in params["player_list"].keys():
            sql = sql.replace(
                rep_str,
                f"{rep_str}\nand :{pname} in (p1_name, p2_name, p3_name, p4_name)"
            )

    if params["target_count"] != 0:
        sql = sql.replace("and playtime between", "-- and playtime between")
        sql = sql.replace("--[recent] ", "")

    g.logging.trace(f"sql: {sql}") # type: ignore
    return(sql)
