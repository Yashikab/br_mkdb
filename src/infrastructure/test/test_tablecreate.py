# python 3.7.5
# coding: utf-8
"""
master2sqlモジュール用単体テスト
"""
# TODO domainへ移動する。（impl必要ない)
import pytest

from domain.model.info import (
    ChokuzenPlayerInfo, ProgramCommonInfo,
    ProgramPlayerInfo, WeatherInfo
)
from infrastructure.tablecreator import (
    ChokuzenTableCreatorImpl,
    JyoDataTableCreatorImpl,
    JyoMasterTableCreatorImpl,
    RaceDataTableCreatorImpl
)

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

    ri_col_set = {'race_id', 'datejyo_id'}.union(
        set(ProgramCommonInfo.__annotations__.keys())
    )

    pr_col_set = {'waku_id', 'race_id'}.union(
        set(ProgramPlayerInfo.__annotations__.keys())
    )

    @pytest.mark.parametrize("tb_name, col_set", [
        ('raceinfo_tb', ri_col_set),
        ('program_tb', pr_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns(tb_name)
        assert get_set == col_set


@pytest.mark.run(order=4)
class TestChokuzenInfo2sql(CommonMethod):

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        chokutc = ChokuzenTableCreatorImpl()
        chokutc.create_commoninfo_table()
        chokutc.create_playerinfo_table()

    cc_col_set = {'race_id', 'datejyo_id'}.union(
        set(WeatherInfo.__annotations__.keys())
    )
    cp_col_set = {'waku_id', 'race_id'}.union(
        set(ChokuzenPlayerInfo.__annotations__.keys())
    )

    @ pytest.mark.parametrize("tb_name, col_set", [
        ('chokuzen_cond_tb', cc_col_set),
        ('chokuzen_player_tb', cp_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns(tb_name)
        assert get_set == col_set
