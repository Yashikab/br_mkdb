from abc import ABCMeta, abstractmethod

from pathlib import PosixPath

import lxml.html as lxml
# URLの取得を行う
# lxml or bs4で返す(一旦lxmlのみ)
# SRP単一責任の法則(報告先が一緒)


class GetLxml(meta=ABCMeta):
    # report先はlxmlを使った各種parser

    @abstractmethod
    def url_to_lxml(self, url: str) -> lxml.HtmlComment:
        pass

    @abstractmethod
    def file_to_lxml(self, filepath: PosixPath) -> lxml.HtmlComment:
        pass
