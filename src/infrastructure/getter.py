import time
from enum import Enum
from pathlib import Path
from typing import Union
from urllib.request import urlopen

import lxml.html as lxml
from bs4 import BeautifulSoup as bs

# URLの取得を行う
# lxml or bs4で返す(一旦lxmlのみ)
# SRP単一責任の法則(報告先が一緒)


class ContentTypes(str, Enum):
    bs4 = "soup"
    lxml = "lxml"

    @classmethod
    def get_content(self):
        return Union[bs, lxml.HtmlElement]


class GetParserContent:
    # report先はlxmlを使った各種parser
    @classmethod
    def url_to_content(cls,
                       url: str,
                       content_type: ContentTypes
                       ) -> ContentTypes.get_content():
        """urlを読み込んで指定した種類のparser contentを返す

        Parameters
        ----------
        url : str

        content_type : ContentTypes
            "soup" or "lxml"

        Returns
        -------
        content : bs4.BeautifulSoup or lxml.HtmlElement
            htmlをparserように変更したcontent

        Raises
        ------
        NameError
            content_typeが指定外のときエラーとなる．
        """
        html_content = cls._get_html_from_url(cls, url)
        content = cls._html_to_content(cls, html_content, content_type)
        return content

    @classmethod
    def file_to_content(cls,
                        filepath: Path,
                        content_type: ContentTypes
                        ) -> ContentTypes.get_content():
        """HTMLファイルを読み込んで指定した種類のparser contentを返す

        Parameters
        ----------
        filepath : Path
            読み込むHTMLファイル

        content_type : ContentTypes
            "soup" or "lxml"

        Returns
        -------
        content : bs4.BeautifulSoup or lxml.HtmlElement
            htmlをparserように変更したcontent

        Raises
        ------
        NameError
            content_typeが指定外のときエラーとなる．
        """
        with open(filepath, "r") as f:
            html_content = f.read()
        content = cls._html_to_content(cls, html_content, content_type)
        return content

    def _get_html_from_url(self, url: str, num_retry: int = 5) -> bytes:
        success_flg = False
        html_content = None
        for i in range(num_retry):
            with urlopen(url, timeout=10.) as f:
                if f.status == 200:
                    html_content = f.read()
                    success_flg = True
                else:
                    self.logger.warning(f"Not completed to download: {url}")
                    self.logger.warning(f"{f.status}: {f.reason}")
            if success_flg:
                break
            self.logger.debug("retry")
            time.sleep(0.5)
        if not success_flg:
            raise self.logger.error(
                f"Didn't succeed in {num_retry} times retry.")
        return html_content

    def _html_to_content(self, html_content: str,
                         content_type: ContentTypes
                         ) -> ContentTypes.get_content():
        if content_type == ContentTypes.bs4:
            content = bs(html_content, "lxml")
        elif content_type == ContentTypes.lxml:
            content = lxml.fromstring(html_content)
        else:
            raise NameError(f"Unavailable content_type: {content_type}")
        return content
