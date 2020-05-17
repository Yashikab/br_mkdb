# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""
from module.dt2sql import RaceData2sql
from module import const
from module.connect import MysqlConnector


class TestRaceInfo2sql:

    __rd2sql = RaceData2sql()

    def test_exist_table(self):
        self.__rd2sql.create_table_if_not_exists(tb_type='raceinfo')
        # カラム名の一致でテスト
        try:
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                sql = 'show columns from raceinfo_tb'
                cursor.execute(sql)
                get_set = set(map(lambda x: x[0], cursor.fetchall()))
                cursor.close()
        except Exception:
            get_set = {}

        expected_set = {'raceinfo_id', 'datejyo_id', 'holddate',
                        'jyo_cd', 'race_no', 'taikai_name',
                        'grade', 'race_type', 'race_kyori',
                        'is_antei', 'is_shinnyukotei'}
        assert get_set == expected_set

    # def test_insert2table(self):
    #     target_date = 20200512
    #     jyo_cd = 20
    #     # 指定日の情報を挿入する
    #     self.__jd2sql.insert2table(date=target_date)
    #     # idの情報を一つ取ってきて調べる
    #     try:
    #         with MysqlConnector(const.MYSQL_CONFIG) as conn:
    #             cursor = conn.cursor()
    #             sql = f'''
    #                 select
    #                   datejyo_id,
    #                   jyo_cd,
    #                   shinko,
    #                   ed_race_no
    #                 from
    #                   holdjyo_tb
    #                 where
    #                   datejyo_id = {target_date}{jyo_cd:02}
    #             '''
    #             cursor.execute(sql)
    #             res_list = cursor.fetchall()
    #             res_tpl = res_list[0]
    #     except Exception:
    #         res_tpl = None
    #     expected_tpl = (
    #         int(f'{target_date}{jyo_cd:02}'),
    #         jyo_cd,
    #         '中止順延',
    #         0
    #     )
    #     assert res_tpl == expected_tpl
