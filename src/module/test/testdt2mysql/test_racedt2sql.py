# python 3.7.5
# coding: utf-8
"""
dt2sqlモジュール用単体テスト
"""
import pytest

from module.dt2sql import RaceData2sql
from module import const
from module.connect import MysqlConnector
from .common import CommonMethod


class TestRaceInfo2sql(CommonMethod):

    __rd2sql = RaceData2sql()

    ri_col_set = {'raceinfo_id', 'datejyo_id', 'holddate',
                  'jyo_cd', 'race_no', 'taikai_name',
                  'grade', 'race_type', 'race_kyori',
                  'is_antei', 'is_shinnyukotei'}
    pr_col_set = {'wakuinfo_id', 'raceinfo_id',
                  'p_name', 'p_id', 'p_level', 'p_home',
                  'p_birthplace', 'p_age', 'p_weight',
                  'p_num_f', 'p_num_l', 'p_avg_st',
                  'p_all_1rate', 'p_all_2rate', 'p_all_3rate',
                  'p_local_1rate', 'p_local_2rate', 'p_local_3rate',
                  'motor_no', 'motor_2rate', 'motor_3rate',
                  'boat_no', 'boat_2rate', 'boat_3rate'}

    @pytest.mark.parametrize("tb_type, tb_name, col_set", [
        ('raceinfo', 'raceinfo_tb', ri_col_set),
        ('program', 'program_tb', pr_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_type, tb_name, col_set):
        self.__rd2sql.create_table_if_not_exists(tb_type=tb_type)
        # カラム名の一致でテスト
        get_set = super().get_columns2set(tb_name)
        assert get_set == col_set

    def test_insert2table(self):
        target_date = 20200512
        jyo_cd = 21
        race_no = 1
        # 指定日の情報を挿入する
        self.__rd2sql.insert2table(
            date=target_date,
            jyo_cd=jyo_cd,
            race_no=race_no)
        # idの情報を一つ取ってきて調べる
        try:
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                sql = f'''
                    select
                      raceinfo_id,
                      datejyo_id,
                      taikai_name,
                      grade,
                      race_type,
                      race_kyori,
                      is_antei,
                      is_shinnyukotei
                    from
                      raceinfo_tb
                    where
                      raceinfo_id = {target_date}{jyo_cd:02}{race_no:02}
                '''
                cursor.execute(sql)
                res_list = cursor.fetchall()
                res_tpl = res_list[0]
        except Exception:
            res_tpl = None
        expected_tpl = (
            int(f'{target_date}{jyo_cd:02}{race_no:02}'),
            int(f'{target_date}{jyo_cd:02}'),
            '読売新聞社杯　全日本王座決定戦　開設６８周年記念',
            'is-G1b',
            '予選',
            1800,
            0,
            0
        )
        assert res_tpl == expected_tpl
