from domain.repository import JyocdMasterRepository


class MysqlJyoMasterRepositoryImpl(JyocdMasterRepository):
    @classmethod
    def create_table_if_not_exists(cls):
        pass