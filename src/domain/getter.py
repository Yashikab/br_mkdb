from abc import ABCMeta, abstractmethod

from pathlib import PosixPath

import lxml.html as lxml
# URLの取得を行う
# lxml or bs4で返す(一旦lxmlのみ)


class GetUrl(meta=ABCMeta):

    @abstractmethod
    def url_to_lxml(self, url: str) -> lxml.HtmlComment:
        pass

    @abstractmethod
    def url_to_file(self, url: str, filepath: PosixPath) -> None:
        # TODO: 不要な場合消す
        pass

    @abstractmethod
    def file_to_lxml(self, filepath: PosixPath) -> lxml.HtmlComment:
        pass
