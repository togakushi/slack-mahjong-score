import os
import sqlite3
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, TableStyle, LongTable, Image
from reportlab.platypus import Paragraph, PageBreak, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.units import mm

import pandas as pd
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

import lib.function as f
import lib.command.report._query as query
from lib.function import global_value as g

mlogger = g.logging.getLogger("matplotlib")
mlogger.setLevel(g.logging.WARNING)


def get_game_results(argument, command_option, flag = "M"):
    resultdb = sqlite3.connect(g.database_file, detect_types = sqlite3.PARSE_DECLTYPES)
    resultdb.row_factory = sqlite3.Row

    ret = query.for_report_personal_data(argument, command_option, flag = flag)
    rows = resultdb.execute(ret["sql"], ret["placeholder"])

    # --- データ収集
    results = [
        [
            "",
            "ゲーム数",
            "累積\nポイント",
            "平均\nポイント",
            "1位", "",
            "2位", "",
            "3位", "",
            "4位", "",
            "平均\n順位",
            "トビ", "",
            "最初", "最後",
        ]
    ]

    for row in rows.fetchall():
        if row["ゲーム数"] == 0:
            break

        results.append(
            [
                row["集計"],
                row["ゲーム数"],
                str(row["累積ポイント"]).replace("-", "▲") + "pt",
                str(row["平均ポイント"]).replace("-", "▲") + "pt",
                row["1位"], f"{row['1位率']:.2f}%",
                row["2位"], f"{row['2位率']:.2f}%",
                row["3位"], f"{row['3位率']:.2f}%",
                row["4位"], f"{row['4位率']:.2f}%",
                f"{row['平均順位']:.2f}",
                row["トビ"], f"{row['トビ率']:.2f}%",
                row["最初"], row["最後"],
            ]
        )
    g.logging.info(f"return record: {len(results)}")
    resultdb.close()

    if len(results) == 1: # ヘッダのみ
        return(False)

    return(results)


def get_count_results(argument, command_option, game_count):
    resultdb = sqlite3.connect(g.database_file, detect_types = sqlite3.PARSE_DECLTYPES)
    resultdb.row_factory = sqlite3.Row

    ret = query.for_report_count_data(argument, command_option, game_count)
    rows = resultdb.execute(ret["sql"], ret["placeholder"])

    # --- データ収集
    results = [
        [
            "開始",
            "終了",
            "ゲーム数",
            "累積\nポイント",
            "平均\nポイント",
            "1位", "",
            "2位", "",
            "3位", "",
            "4位", "",
            "平均\n順位",
            "トビ", "",
        ]
    ]

    for row in rows.fetchall():
        if row["ゲーム数"] == 0:
            break

        results.append(
            [
                row["開始"],
                row["終了"],
                row["ゲーム数"],
                str(row["累積ポイント"]).replace("-", "▲") + "pt",
                str(row["平均ポイント"]).replace("-", "▲") + "pt",
                row["1位"], f"{row['1位率']:.2f}%",
                row["2位"], f"{row['2位率']:.2f}%",
                row["3位"], f"{row['3位率']:.2f}%",
                row["4位"], f"{row['4位率']:.2f}%",
                f"{row['平均順位']:.2f}",
                row["トビ"], f"{row['トビ率']:.2f}%",
            ]
        )
    g.logging.info(f"return record: {len(results)}")
    resultdb.close()

    if len(results) == 1: # ヘッダのみ
        return(False)

    return(results)



def get_count_moving(argument, command_option, game_count):
    resultdb = sqlite3.connect(g.database_file, detect_types = sqlite3.PARSE_DECLTYPES)
    resultdb.row_factory = sqlite3.Row

    ret = query.for_report_count_moving(argument, command_option, game_count)
    rows = resultdb.execute(ret["sql"], ret["placeholder"])

    # --- データ収集
    results = []
    for row in rows.fetchall():
        results.append(dict(row))

    g.logging.info(f"return record: {len(results)}")
    resultdb.close()

    if len(results) == 0:
        return(False)

    return(results)

def count_report(data, title):
        tt = LongTable(data, repeatRows = 1)
        ts = TableStyle([
            ("FONT", (0, 0), (-1, -1), "ReportFont", 10),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ('SPAN', (5, 0), (6, 0)),
            ('SPAN', (7, 0), (8, 0)),
            ('SPAN', (9, 0), (10, 0)),
            ('SPAN', (11, 0), (12, 0)),
            ('SPAN', (14, 0), (15, 0)),
            # ヘッダ行
            ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ])
        if len(data) > 4:
            for i in range(len(data) - 2):
                if i % 2 == 0:
                    ts.add("BACKGROUND",(0, i + 2), (-1, i + 2), colors.lightgrey)
        tt.setStyle(ts)

        gdata = pd.DataFrame({
            "1位率": [float(data[x + 1][6].replace("%", "")) for x in range(len(data) - 1)],
            "2位率": [float(data[x + 1][8].replace("%", "")) for x in range(len(data) - 1)],
            "3位率": [float(data[x + 1][10].replace("%", "")) for x in range(len(data) - 1)],
            "4位率": [float(data[x + 1][12].replace("%", "")) for x in range(len(data) - 1)],
            }, index = [f"{str(data[x + 1][0])} - {str(data[x + 1][1])}" for x in range(len(data) - 1)]
        )

        imgdata = BytesIO()
        gdata.plot(
            kind = "bar",
            stacked = True,
            figsize = (12, 8),
            fontsize = 14,
        )
        plt.title(title, fontsize = 18)
        plt.yticks([0, 25, 50, 75, 100])
        for ax in plt.gcf().get_axes(): # グリッド線を背後にまわす
            ax.set_axisbelow(True)
            plt.grid(axis = "y")
        plt.xticks(rotation = 45)
        plt.legend(bbox_to_anchor = (0.5, 0), loc = "lower center", ncol = 4, fontsize = 12)
        plt.savefig(imgdata, format = "jpg")
        plt.close()

        return(tt, imgdata)


def gen_pdf(argument, command_option):
    _, target_player, _, command_option = f.common.argument_analysis(argument, command_option)

    font_path = os.path.join(os.path.realpath(os.path.curdir), g.font_file)

    # --- レポート作成
    pdf_path = os.path.join(os.path.realpath(os.path.curdir), "Results.pdf")
    pdfmetrics.registerFont(TTFont("ReportFont", font_path))

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize = landscape(A4),
        topMargin = 10.0*mm,
        bottomMargin = 10.0*mm,
        #leftMargin = 1.5*mm,
        #rightMargin = 1.5*mm,
    )
    style = {}
    style["Title"] = ParagraphStyle(name = "Title", fontName = "ReportFont", fontSize = 24)
    style["Normal"] = ParagraphStyle(name = "Normal", fontName = "ReportFont", fontSize = 14)
    style["Left"] = ParagraphStyle(name = "Left", fontName = "ReportFont", fontSize = 14, alignment = TA_LEFT)
    style["Right"] = ParagraphStyle(name = "Right", fontName = "ReportFont", fontSize = 14, alignment = TA_RIGHT)


    # グラフフォント設定
    fm.fontManager.addfont(font_path)
    font_prop = fm.FontProperties(fname = font_path)
    plt.rcParams["font.family"] = font_prop.get_name()

    elements = []
    # 全体のデータ
    tmp_data = get_game_results(argument, command_option, flag = "A") # 0件のときはFalseが返る
    if not tmp_data:
        return(False)

    total_game_count = int(tmp_data[1][1]) # トータルゲーム数
    game_first = tmp_data[1][15] # 最初のゲーム日時
    game_last = tmp_data[1][16] # 最後のゲーム日時
    g.logging.info(f"total: {total_game_count}, first: {game_first}, last: {game_last}")

    # タイトル
    elements.append(Spacer(1, 40*mm))
    elements.append(Paragraph(f"成績レポート：{target_player[0]}", style["Title"]))
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(f"集計期間：{game_first} - {game_last}", style["Normal"]))
    elements.append(Spacer(1, 100*mm))
    elements.append(Paragraph(f"作成日：{datetime.now().strftime('%Y-%m-%d')}", style["Right"]))
    elements.append(PageBreak())

    # 全期間
    elements.append(Paragraph("全期間", style["Normal"]))
    elements.append(Spacer(1, 5*mm))
    data = []
    for x in range(len(tmp_data)): # ゲーム数と日時を除外
        data.append(tmp_data[x][1:15])
    tt = LongTable(data, repeatRows = 1)
    tt.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "ReportFont", 10),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ('SPAN', (3, 0), (4, 0)),
        ('SPAN', (5, 0), (6, 0)),
        ('SPAN', (7, 0), (8, 0)),
        ('SPAN', (9, 0), (10, 0)),
        ('SPAN', (12, 0), (13, 0)),
        # ヘッダ行
        ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ]))
    elements.append(tt)

    imgdata = BytesIO()
    gdata = pd.DataFrame({
        "順位分布": [
            float(data[1][4].replace("%", "")),
            float(data[1][6].replace("%", "")),
            float(data[1][8].replace("%", "")),
            float(data[1][10].replace("%", "")),
            ],
        }, index = ["1位率", "2位率", "3位率", "4位率"]
    )
    gdata.plot(
        kind = "pie",
        y = "順位分布",
        labels = None,
        figsize = (8, 6),
        fontsize = 14,
        autopct = "%.2f%%",
    )
    plt.title("順位分布", fontsize = 18)
    plt.ylabel(None)
    plt.legend(list(gdata.index), bbox_to_anchor = (0.5, -0.1), loc = "lower center", ncol = 4, fontsize = 12)
    plt.savefig(imgdata, format = "jpg")

    elements.append(Spacer(1, 5*mm))
    elements.append(
        Image(imgdata,
        width = 800 * 0.5,
        height = 600 * 0.5,
    ))
    plt.close()
    elements.append(PageBreak())

    # 期間集計
    pattern = [ # 表タイトル, グラフタイトル, フラグ
        ("月別集計", "順位分布(月別)", "M"),
        ("年別集計", "順位分布(年別)", "Y"),
    ]
    for table_title, graph_title, flag in pattern:
        elements.append(Paragraph(table_title, style["Left"]))
        elements.append(Spacer(1, 5*mm))

        data = []
        tmp_data = get_game_results(argument, command_option, flag)
        for x in range(len(tmp_data)): # 日時を除外
            data.append(tmp_data[x][:15])

        tt = LongTable(data, repeatRows = 1)
        ts = TableStyle([
            ("FONT", (0, 0), (-1, -1), "ReportFont", 10),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ('SPAN', (4, 0), (5, 0)),
            ('SPAN', (6, 0), (7, 0)),
            ('SPAN', (8, 0), (9, 0)),
            ('SPAN', (10, 0), (11, 0)),
            ('SPAN', (13, 0), (14, 0)),
            # ヘッダ行
            ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ])
        if len(data) > 4:
            for i in range(len(data) - 2):
                if i % 2 == 0:
                    ts.add("BACKGROUND",(0, i + 2), (-1, i + 2), colors.lightgrey)
        tt.setStyle(ts)
        elements.append(tt)
        elements.append(Spacer(1, 10*mm))

        imgdata = BytesIO()
        gdata = pd.DataFrame({
            "1位率": [float(data[x + 1][5].replace("%", "")) for x in range(len(data) - 1)],
            "2位率": [float(data[x + 1][7].replace("%", "")) for x in range(len(data) - 1)],
            "3位率": [float(data[x + 1][9].replace("%", "")) for x in range(len(data) - 1)],
            "4位率": [float(data[x + 1][11].replace("%", "")) for x in range(len(data) - 1)],
            }, index = [data[x + 1][0] for x in range(len(data) - 1)]
        )

        gdata.plot(
            kind = "bar",
            stacked = True,
            figsize = (12, 7),
            fontsize = 14,
        )
        plt.title(graph_title, fontsize = 18)
        plt.yticks([0, 25, 50, 75, 100])
        for ax in plt.gcf().get_axes(): # グリッド線を背後にまわす
            ax.set_axisbelow(True)
            plt.grid(axis = "y")
        plt.xticks(rotation = 45)
        plt.legend(bbox_to_anchor = (0.5, 0), loc = "lower center", ncol = 4, fontsize = 12)
        plt.savefig(imgdata, format = "jpg")

        elements.append(Spacer(1,5*mm))
        elements.append(Image(imgdata, width = 1200 * 0.5, height = 700 * 0.5))
        plt.close()
        elements.append(PageBreak())

    # 区間集計
    pattern = [ # 区切り回数, 閾値, タイトル
        (80, 100, "短期"),
        (200, 240, "中期"),
        (400, 500, "長期"),
    ]
    for count, threshold, title in pattern:
        if total_game_count > threshold:
            elements.append(Paragraph(f"区間集計({title})", style["Normal"]))
            elements.append(Spacer(1,5*mm))
            data = get_count_results(argument, command_option, count)
            tt, imgdata = count_report(data, f"順位分布(区間 {title})")
            elements.append(tt)
            elements.append(Spacer(1, 5*mm))
            elements.append(Image(imgdata, width = 1200 * 0.5, height = 800 * 0.5,))

            # 累積
            data = get_count_moving(argument, command_option, count)
            tmp_df = pd.DataFrame.from_dict(data)
            df = pd.DataFrame()
            for i in sorted(tmp_df["interval"].unique().tolist()):
                list_data = tmp_df[tmp_df.interval == i]["point_sum"].to_list()
                game_count = tmp_df[tmp_df.interval == i]["total_count"].to_list()
                df[f"{min(game_count)} - {max(game_count)}"] = [None] * (count - len(list_data)) + list_data

            imgdata = BytesIO()
            df.plot(
                kind = "line",
                figsize = (12, 8),
                fontsize = 14,
            )
            plt.grid(axis = "y")
            plt.title(f"累積ポイント推移(区間 {title})", fontsize = 18)
            plt.legend(title="開始 - 終了", ncol = int(len(tmp_df["interval"].unique().tolist())) / 5 + 1)
            plt.ylabel("獲得ポイント(累積)", fontsize = 14)
            plt.xlabel("ゲーム数", fontsize = 14)

            # Y軸修正
            ylocs, ylabs = plt.yticks()
            new_ylabs = [ylab.get_text().replace("−", "▲") for ylab in ylabs]
            plt.yticks(ylocs[1:-1], new_ylabs[1:-1])

            plt.savefig(imgdata, format = "jpg")
            elements.append(Image(imgdata, width = 1200 * 0.5, height = 800 * 0.5,))
            plt.close()

            # 平均順位
            df = pd.DataFrame()
            for i in sorted(tmp_df["interval"].unique().tolist()):
                list_data = tmp_df[tmp_df.interval == i]["rank_avg"].to_list()
                game_count = tmp_df[tmp_df.interval == i]["total_count"].to_list()
                df[f"{min(game_count)} - {max(game_count)}"] = [None] * (count - len(list_data)) + list_data

            imgdata = BytesIO()
            df.plot(
                kind = "line",
                figsize = (12, 5),
                fontsize = 14,
            )
            plt.grid(axis = "y")
            plt.title(f"平均順位推移(区間 {title})", fontsize = 18)
            plt.legend(title="開始 - 終了")
            plt.yticks([4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0])
            plt.ylabel("平均順位", fontsize = 14)
            plt.xlabel("ゲーム数", fontsize = 14)
            plt.legend(title="開始 - 終了", ncol = int(len(tmp_df["interval"].unique().tolist())) / 5 + 1)

            # Y軸修正
            for ax in plt.gcf().get_axes(): # 逆向きにする
                ax.invert_yaxis()

            plt.savefig(imgdata, format = "jpg")
            elements.append(Image(imgdata, width = 1200 * 0.5, height = 500 * 0.5,))
            plt.close()


            elements.append(PageBreak())

    doc.build(elements)
    return(pdf_path)
