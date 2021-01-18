from typing import List, Tuple


class SqlCreator:

    @classmethod
    def sql_for_create_table(
        cls,
        tb_name: str,
        schemas: List[Tuple[str, ...]],
        replace: bool = True
    ) -> str:
        """テーブル作成のためのクエリ作成

        Parameters
        ----------
        tb_name : str
            テーブル名
        schemas : List[Tuple[str, ...]]
            スキーマのリスト ("変数名", "型", "外部キー(任意)")を1セットとし、
            テーブルに定義するスキーマをリストで入れる。
            各スキーマはスペースでjoinされ、スキーマ間は", \\n"でジョインする。
        replace : Optional[bool]
            テーブルが存在するとき置換するかどうか。

        Returns
        -------
        str
            テーブル作成のためのクエリ
        """
        schemas = ", \n".join(list(map(lambda s: " ".join(s), schemas)))
        replace_txt = ""
        if replace:
            replace_txt = "IF NOT EXISTS"

        sql = f"CREATE TABLE {replace_txt} {tb_name}( {schemas} ) " \
              f"CHARACTER SET utf8;"
        return sql
