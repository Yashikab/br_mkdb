"""場コードマスタテーブルをつくる"""
from abc import ABCMeta, abstractclassmethod


class JyocdMasterRepository(metaclass=ABCMeta):
    @abstractclassmethod
    def create_table_if_not_exists(clf):
        raise NotImplementedError()
