from datetime import date
from dataclasses import asdict
from typing import Any, List


class CommonMethod:
    def to_query_phrase(self, value: Any) -> str:
        """ valueをsqlに挿入できる形にする"""
        if isinstance(value, str):
            # ''で囲む
            value = f"'{value}'"
        elif isinstance(value, date):
            value = value.strftime("%Y%m%d")

        elif value is None:
            value = "null"
        else:
            # "hoge" ならそれで統一する
            value = f"{value}"
        return value

    def get_insertlist(self, data_obj: Any, cols: List[str]) -> str:
        """データ挿入用に文字列を変換し、リストで返す。

        Parameters
        ----------
        data_obj : Any
            受け渡し用型(HoldRaceInfoとか)
        cols : List[str]
            挿入順のカラムリスト

        Returns
        -------
        List[str]
            変換したリスト(挿入順)
        """
        inserts = list()
        data_dict = asdict(data_obj)
        for col in cols:
            inserts.append(self.to_query_phrase(data_dict[col]))
        print(inserts)
        return inserts
