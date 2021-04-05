from datetime import date
from typing import Any


class CommonMethod:
    def to_query_phrase(self, value: Any) -> str:
        """ valueをsqlに挿入できる形にする"""
        if value_type := type(value) is str:
            # ''で囲む
            value = f"'{value}'"
        elif value_type is date:
            value = value.strftime("%Y%m%d")

        elif value is None:
            value = "null"
        else:
            # "hoge" ならそれで統一する
            value = f"{value}"
        return value
