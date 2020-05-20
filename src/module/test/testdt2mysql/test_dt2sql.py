# python 3.7.5
# coding: utf-8
"""
dt2sqlモジュール用単体テスト
実行順番があるので一つのファイルにまとめる
"""
import pytest

from module.dt2sql import JyoData2sql
from module import const
from module.connect import MysqlConnector
from module.dt2sql import RaceData2sql
from .common import CommonMethod


class TestJyoData2sql(CommonMethod):

    __jd2sql = JyoData2sql()

    def test_exist_table(self):
        self.__jd2sql.create_table_if_not_exists()
        # カラム名の一致でテスト
        get_set = super().get_columns2set('holdjyo_tb')

        expected_set = {'datejyo_id', 'holddate', 'jyo_cd',
                        'jyo_name', 'shinko', 'ed_race_no'}
        assert get_set == expected_set

    def test_insert2table(self):
        target_date = 20200512
        jyo_cd = 20
        # 指定日の情報を挿入する
        self.__jd2sql.insert2table(date=target_date)
        # idの情報を一つ取ってきて調べる
        try:
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                sql = f'''
                    select
                      datejyo_id,
                      jyo_cd,
                      shinko,
                      ed_race_no
                    from
                      holdjyo_tb
                    where
                      datejyo_id = {target_date}{jyo_cd:02}
                '''
                cursor.execute(sql)
                res_list = cursor.fetchall()
                res_tpl = res_list[0]
        except Exception:
            res_tpl = None
        expected_tpl = (
            int(f'{target_date}{jyo_cd:02}'),
            jyo_cd,
            '中止順延',
            0
        )
        assert res_tpl == expected_tpl


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
                      wakuinfo_id,
                      p_id,
                      p_all_1rate,
                      boat_2rate
                    from
                      program_tb
                    where
                      wakuinfo_id = {target_date}{jyo_cd:02}{race_no:02}1
                '''
                cursor.execute(sql)
                res_list = cursor.fetchall()
                res_tpl = res_list[0]
        except Exception:
            res_tpl = None
        expected_tpl = (
            int(f'{target_date}{jyo_cd:02}{race_no:02}1'),
            4713,
            6.72,
            18.18
        )
        assert res_tpl == expected_tpl
