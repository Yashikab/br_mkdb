from logging import getLogger
from typing import List, Optional, Tuple

logger = getLogger(__name__)


class SqlCreator:

    @classmethod
    def sql_for_create_table(
        cls,
        tb_name: str,
        schemas: List[Tuple[str, ...]],
        foreign_keys: Optional[List[str]] = None,
        refs: Optional[List[str]] = None,
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
        foreign_keys: List[str]
            外部キーリスト （指定した場合refsで参照先がないとエラーになる）
        refs: List[str]
            外部キーリスト参照先テーブルのリスト
        replace : Optional[bool]
            テーブルが存在するとき置換するかどうか。

        Returns
        -------
        str
            テーブル作成のためのクエリ
        """
        schema_phrase = ", \n".join(list(map(lambda s: " ".join(s), schemas)))
        replace_txt = ""
        if replace:
            replace_txt = "IF NOT EXISTS"

        # foregin key(option)
        # schemaからつなぐカンマを入れておく
        foreign_phases = [", "]
        if foreign_keys:
            assert refs, "You have to set references, if foreign_keys are set."
            assert len(foreign_keys) == len(refs), \
                "Length between foreign_keys and references must be same."
            schema_names = set(map(lambda s: s[0], schemas))
            assert set(foreign_keys) <= schema_names, \
                "foregin key must be in the set of columns."
            for f, r in zip(foreign_keys, refs):
                foreign_phases.append(
                    f"FOREIGN KEY ({f}) REFERENCES {r} ({f})")

        if len(foreign_phases) > 1:
            foreign_phrase = " ".join(foreign_phases)
        else:
            foreign_phrase = ""

        sql = f"CREATE TABLE {replace_txt} {tb_name}"\
              f"( {schema_phrase} {foreign_phrase}) " \
              f"CHARACTER SET utf8;"
        logger.debug(sql)
        return sql
