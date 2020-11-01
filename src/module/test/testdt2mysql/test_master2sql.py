# python 3.7.5
# coding: utf-8
"""
master2sqlモジュール用単体テスト
"""
from .common import CommonMethod
from module.master2sql import JyoMaster2sql


class TestJyoMaster2sql(CommonMethod):
    __table_name: str = 'jyo_master'
    # __jm2sql = JyoMaster2sql()
    # __jm2sql.create_table_if_not_exists()

    def test_exist_table(self):
        get_set = super().get_columns2set(self.__table_name)
        expected_set = {'jyo_name', 'jyo_cd'}
        # カラム名確認
        assert get_set == expected_set

    def test_inserteddata(self):
        res_tpl = super().getdata2tuple(
            tb_name=self.__table_name,
            id_name='jyo_cd',
            target_id=1,
            col_list=['jyo_name', 'jyo_cd']
        )
        expected_tpl = ('桐生', 1)
        assert res_tpl == expected_tpl
