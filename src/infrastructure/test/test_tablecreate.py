# python 3.7.5
# coding: utf-8
"""
master2sqlモジュール用単体テスト
"""
import pytest

from infrastructure.tablecreator import JyoMasterTableCreatorImpl

from .common import CommonMethod


@pytest.mark.run(order=1)
class TestJyoMasterTableCreatorImpl(CommonMethod):
    __table_name: str = 'jyo_master'

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        # jyomaster
        jm2sql = JyoMasterTableCreatorImpl()
        jm2sql.create_table()

    def test_exist_table(self):
        get_set = super().get_columns(self.__table_name)
        expected_set = {'jyo_name', 'jyo_cd'}
        # カラム名確認
        assert get_set == expected_set
