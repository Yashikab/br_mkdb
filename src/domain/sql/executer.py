from abc import ABCMeta, abstractclassmethod


class SqlExecuter(metaclass=ABCMeta):
    @abstractclassmethod
    def run_query(cls, query: str) -> None:
        """クエリを実行する"""
