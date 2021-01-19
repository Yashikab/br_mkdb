# python 3.7.5
# coding: utf-8
"""
master2sqlモジュール用単体テスト
"""
import pytest

from infrastructure.tablecreator import JyoMasterTableCreatorImpl, JyoDataTableCreatorImpl

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
