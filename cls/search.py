import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

from lib.database.common import first_record
import global_value as g


class SearchRange():
    words = {}
    day_format = re.compile(r"^([0-9]{8}|[0-9/.-]{8,10})$")

    def __init__(self) -> None:
        self.first_record = first_record()
        self.update()

    def update(self) -> None:
        self.current_time = datetime.now()
        self.appointed_time = self.current_time + relativedelta(hours=-12)
        self.words["当日"] = [
            self.appointed_time,
        ]
        self.words["今日"] = [
            self.current_time,
        ]
        self.words["昨日"] = [
            self.current_time + relativedelta(days=-1),
        ]
        self.words["今月"] = [
            self.appointed_time + relativedelta(day=1, months=0),
            self.appointed_time + relativedelta(day=1, months=1, days=-1),
        ]
        self.words["先月"] = [
            self.appointed_time + relativedelta(day=1, months=-1),
            self.appointed_time + relativedelta(day=1, months=0, days=-1),
        ]
        self.words["先々月"] = [
            self.appointed_time + relativedelta(day=1, months=-2),
            self.appointed_time + relativedelta(day=1, months=-1, days=-1),
        ]
        self.words["今年"] = [
            self.current_time + relativedelta(day=1, month=1),
            self.current_time + relativedelta(day=31, month=12),
        ]
        self.words["去年"] = [
            self.current_time + relativedelta(day=1, month=1, years=-1),
            self.current_time + relativedelta(day=31, month=12, years=-1),
        ]
        self.words["昨年"] = self.words["去年"]
        self.words["一昨年"] = [
            self.current_time + relativedelta(day=1, month=1, years=-2),
            self.current_time + relativedelta(day=31, month=12, years=-2),
        ]
        self.words["最初"] = [
            self.first_record + relativedelta(days=-1),
        ]
        self.words["最後"] = [
            self.current_time + relativedelta(days=1),
        ]
        self.words["全部"] = [
            self.first_record + relativedelta(days=-1),
            self.current_time + relativedelta(days=1),
        ]

    def find(self, word: str) -> bool:
        if word in self.words.keys():
            return (True)
        else:
            if re.match(self.day_format, word):
                return (True)
            else:
                return (False)

    def range(self, word: str) -> list:
        self.update()
        if word in self.words.keys():
            return (self.words[word])
        else:
            if re.match(self.day_format, word):
                try_day = pd.to_datetime(word, errors="coerce").to_pydatetime()
                if pd.isna(try_day):
                    return ([])
                else:
                    return ([try_day])
            else:
                return ([])

    def list(self):
        ret = []
        for x in self.words.keys():
            days = []
            for v in self.words[x]:
                days.append(v.strftime("%Y/%m/%d"))
            ret.append(f"{x}： {' ～ '.join(days)}")

        return ("\n".join(ret))


class CommandCheck(str):
    """
    キーワードがサブコマンドかチェックする(match専用)
    """

    def __init__(self, command_name: str):
        self.command_name = command_name

    def __eq__(self, chk_pattern):
        commandlist = g.cfg.config["alias"].get(chk_pattern, "")
        commandlist = [chk_pattern] + [x for x in commandlist.split(",") if x]

        if self.command_name in commandlist:
            return (True)

        return (False)