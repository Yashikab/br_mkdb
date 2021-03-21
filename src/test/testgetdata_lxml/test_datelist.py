# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""

from datetime import datetime

import pytest

from infrastructure import getdata_lxml


class TestDateList:
    @pytest.mark.parametrize(
        "st_date, ed_date, expected",
        [
            (
                datetime(2020, 4, 30),
                datetime(2020, 5, 2),
                [20200430, 20200501, 20200502],
            ),
            (
                datetime(2020, 2, 28),
                datetime(2020, 3, 1),
                [20200228, 20200229, 20200301],
            ),
        ],
    )
    def test_datelist(self, st_date, ed_date, expected):
        res_dl = [d for d in getdata_lxml.DateRange.daterange(st_date, ed_date)]
        assert res_dl == expected
