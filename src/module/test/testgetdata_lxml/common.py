# python 3.7.5
# coding: utf-8
from pathlib import Path

import lxml.html as lxml


class CommonMethodForTest:

    def htmlfile2lxcontent(self, filename: str) -> lxml.HtmlElement:
        currentdir = Path(__file__).resolve().parent
        filepath = currentdir.joinpath('test_html', filename)

        with open(filepath, 'r') as f:
            html_content = f.read()
        lx_content = lxml.fromstring(html_content)

        return lx_content
