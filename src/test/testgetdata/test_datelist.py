# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""

import pytest
from module import getdata


class TestDateList:

    @pytest.mark.parametrize("y, m, d, m2, d2, expected", [
        (2020, 4, 30, 5, 2, [20200430, 20200501, 20200502]),
        (2020, 2, 28, 3, 1, [20200228, 20200229, 20200301])
    ])
    def test_datelist(self, y, m, d, m2, d2, expected):
        dl = getdata.DateList()
        res_dl = dl.datelist(
            st_year=y,
            st_month=m,
            st_day=d,
            ed_year=y,
            ed_month=m2,
            ed_day=d2
        )
        assert res_dl == expected
