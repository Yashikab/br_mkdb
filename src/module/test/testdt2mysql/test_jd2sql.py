# python 3.7.5
# coding: utf-8
"""
jyodata2sqlテスト
"""
import pytest

from module.dt2sql import JyoData2sql
from ..common import CommonMethod


@pytest.mark.run(order=2)
class TestJyoData2sql(CommonMethod):

    __target_date = 20200512
    __jyo_cd = 20
    __jd2sql = JyoData2sql()

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        self.__jd2sql.create_table_if_not_exists()
        self.__jd2sql.insert2table(date=self.__target_date)

    def test_exist_table(self):
        # カラム名の一致でテスト
        get_set = super().get_columns('holdjyo_tb')

        expected_set = {'datejyo_id', 'holddate', 'jyo_cd',
                        'jyo_name', 'shinko', 'ed_race_no'}
        assert get_set == expected_set

    def test_insert2table(self):
        # idの情報を一つ取ってきて調べる
        tb_name = "holdjyo_tb"
        id_name = "datejyo_id"
        target_id = f"{self.__target_date}{self.__jyo_cd:02}"
        col_list = ["datejyo_id", "jyo_cd", "shinko", "ed_race_no"]
        res_tpl = super().get_targetdata(
            tb_name,
            id_name,
            target_id,
            col_list
        )
        expected_tpl = (
            int(target_id),
            self.__jyo_cd,
            '中止順延',
            0
        )
        assert res_tpl == expected_tpl

    def test_map_raceno_dict(self):
        assert self.__jd2sql.map_raceno_dict[21] == range(1, 13)
