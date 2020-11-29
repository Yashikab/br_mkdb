# python 3.7.5
# coding: utf-8
"""
chokuseninfoo2sqlテスト
"""
import pytest
import time

from module.dt2sql import ChokuzenData2sql
from module.getdata import CommonMethods4Official
from ..common import CommonMethod

WAIT = 0.5


@pytest.mark.run(order=4)
class TestChokuzenInfo2sql(CommonMethod):
    __target_date = 20200512
    __jyo_cd = 21
    __race_no = 1
    __ci2sql = ChokuzenData2sql()

    @pytest.fixture(autouse=True)
    def insertdata(self, mocker):
        # mocking
        soup_content = super().htmlfile2bs4(
            f"choku_{self.__target_date}{self.__jyo_cd}{self.__race_no}.html"
        )
        mocker.patch.object(CommonMethods4Official,
                            '_url2soup',
                            return_value=soup_content)

        self.__ci2sql.create_table_if_not_exists()
        self.__ci2sql.insert2table(
            date=self.__target_date,
            jyo_cd_list=[self.__jyo_cd],
            raceno_dict={
                self.__jyo_cd: range(self.__race_no, self.__race_no+1)},
        )
        time.sleep(WAIT)

    cc_col_set = {'race_id', 'datejyo_id',
                  'temp', 'weather', 'wind_v',
                  'w_temp', 'wave', 'wind_dr'}
    cp_col_set = {'waku_id', 'race_id', 'p_name',
                  'p_weight', 'p_chosei_weight',
                  'p_tenji_time', 'p_tilt',
                  'p_tenji_course', 'p_tenji_st'}

    @pytest.mark.parametrize("tb_name, col_set", [
        ('chokuzen_cond_tb', cc_col_set),
        ('chokuzen_player_tb', cp_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns2set(tb_name)
        assert get_set == col_set

    race_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}"
    cond_col_list = ["race_id", "temp", "weather", "wave"]
    cond_expected = (
        int(race_id),
        24.0,
        '晴',
        5
    )
    waku_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}1"
    waku_col_list = ["waku_id", "p_chosei_weight", "p_tenji_time",
                     "p_tilt", "p_tenji_course", "p_tenji_st"]
    waku_ex = (
            int(waku_id),
            0.0,
            6.91,
            -0.5,
            2,
            0.11
        )

    @pytest.mark.parametrize("tb_nm, id_nm, t_id, col_list, expected", [
        ("chokuzen_cond_tb", "race_id", race_id, cond_col_list, cond_expected),
        ("chokuzen_player_tb", "waku_id", waku_id, waku_col_list, waku_ex)
    ])
    def test_insert2table(self, tb_nm, id_nm, t_id, col_list, expected):
        res_tpl = super().getdata2tuple(
            tb_nm,
            id_nm,
            t_id,
            col_list
        )
        assert res_tpl == expected
