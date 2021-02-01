from abc import ABCMeta, abstractmethod


class DatabaseController(metaclass=ABCMeta):
    @abstractmethod
    def build(self):
        """build DB"""

    @abstractmethod
    def clean(self):
        """del DB"""
