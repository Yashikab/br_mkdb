# python 3.7.5
# coding: utf-8
"""
master2sqlモジュール用単体テスト
"""
import pytest

from infrastructure.tablecreator import (JyoDataTableCreatorImpl,
                                         JyoMasterTableCreatorImpl,
                                         RaceDataTableCreatorImpl)

from .common import CommonMethod


@pytest.mark.run(order=1)
class TestJyoMasterTableCreatorImpl(CommonMethod):
    __table_name: str = 'jyo_master'

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        # jyomaster
        jmtc = JyoMasterTableCreatorImpl()
        jmtc.create_table()

    def test_exist_table(self):
        get_set = super().get_columns(self.__table_name)
        expected_set = {'jyo_name', 'jyo_cd'}
        # カラム名確認
        assert get_set == expected_set


@pytest.mark.run(order=2)
class TestJyoDataTableCreatorImpl(CommonMethod):

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        jdtc = JyoDataTableCreatorImpl()
        jdtc.create_table()

    def test_exist_table(self):
        # カラム名の一致でテスト
        get_set = super().get_columns('holdjyo_tb')

        expected_set = {'datejyo_id', 'holddate', 'jyo_cd',
                        'jyo_name', 'shinko', 'ed_race_no'}
        assert get_set == expected_set


@pytest.mark.run(order=3)
class TestRaceInfoTableCreatorImpl(CommonMethod):

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        rdtc = RaceDataTableCreatorImpl()
        rdtc.create_commoninfo_table()
        rdtc.create_playerinfo_table()

    ri_col_set = {'race_id', 'datejyo_id', 'taikai_name',
                  'grade', 'race_type', 'race_kyori',
                  'is_antei', 'is_shinnyukotei'}
    pr_col_set = {'waku_id', 'race_id',
                  'p_name', 'p_id', 'p_level', 'p_home',
                  'p_birthplace', 'p_age', 'p_weight',
                  'p_num_f', 'p_num_l', 'p_avg_st',
                  'p_all_1rate', 'p_all_2rate', 'p_all_3rate',
                  'p_local_1rate', 'p_local_2rate', 'p_local_3rate',
                  'motor_no', 'motor_2rate', 'motor_3rate',
                  'boat_no', 'boat_2rate', 'boat_3rate'}

    @pytest.mark.parametrize("tb_name, col_set", [
        ('raceinfo_tb', ri_col_set),
        ('program_tb', pr_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns(tb_name)
        assert get_set == col_set
