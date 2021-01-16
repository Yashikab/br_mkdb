from domain.tablecreator import JyoDataTableCreator, JyoMasterTableCreator


class JyoMasterTableCreatorImpl(JyoMasterTableCreator):

    def create_table(self):
        # TODO sqlテキストは使わずここで作成する.
        # TODO mysql用スキーマ組み立てがあるか調べる.
        pass


class JyoDataTableCreatorImpl(JyoDataTableCreator):

    def create_table(self):
        pass
