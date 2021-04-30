"""場コードマスタテーブルをつくる"""
from abc import ABCMeta, abstractmethod


class JyocdMasterRepository(metaclass=ABCMeta):
    @abstractmethod
    def create_table_if_not_exists(clf):
        raise NotImplementedError()
