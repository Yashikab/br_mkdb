from pathlib import Path

import pandas as pd

from domain.repository import JyocdMasterRepository
from infrastructure.mysql import MysqlCreator, MysqlExecuter


class MysqlJyoMasterRepositoryImpl(JyocdMasterRepository):
    def create_table_if_not_exists(self):
        tb_name = "jyo_master"
        schema = [
            ("jyo_name", "VARCHAR(100)"),
            ("jyo_cd", "INT", "PRIMARY KEY"),
        ]
        sql_creator = MysqlCreator()
        query = sql_creator.sql_for_create_table(
            tb_name, schema, if_not_exists=True
        )
        MysqlExecuter.run_query(query)
        sql = f"INSERT IGNORE INTO {tb_name} VALUES"
        insert_value = ", ".join([val for val in self._csv2rows_generator()])
        query = " ".join([sql, insert_value])
        MysqlExecuter.run_query(query)

    def _csv2rows_generator(self):
        csv_filepath = (
            Path(__file__).parent.joinpath("jyo_master.csv").resolve()
        )
        jyomaster_df = pd.read_csv(csv_filepath, header=0)
        for name, cd in zip(jyomaster_df.jyo_name, jyomaster_df.jyo_cd):
            yield f'("{name}", {cd})'
