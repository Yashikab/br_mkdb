# python 3.7.5
# coding: utf-8
from bs4 import BeautifulSoup as bs
from pathlib import Path


class CommonMethodForTest:

    def htmlfile2bs4(self, filename: str) -> bs:
        currentdir = Path(__file__).resolve().parent
        filepath = currentdir.joinpath('test_html', filename)

        with open(filepath, 'r') as f:
            html_content = f.read()
        soup_content = bs(html_content, "lxml")

        return soup_content
