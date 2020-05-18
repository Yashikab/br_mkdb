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
