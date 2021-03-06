from datetime import date
from pathlib import Path

import pytest

from infrastructure.factory import ProgramInfoFactoryImpl
from infrastructure.getter import GetParserContent

FILEPATH = Path(__file__).resolve().parents[1] / "test_html"


class TestProgramFactoryImpl:

    @pytest.mark.parametrize("target_date, target_jyo, race_no", [
        (date(2020, 4, 8), 6, 3),
    ])
    def test_raceinfo(self, target_date: date, target_jyo: int, race_no: int, mocker):
        filepath = FILEPATH / \
            f"pro_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        lx_content = GetParserContent.file_to_content(
            filepath, "lxml"
        )
        mocker.patch.object(
            GetParserContent, "url_to_content",
            return_value=lx_content
        )
        pif = ProgramInfoFactoryImpl()
        pif._raceinfo(target_date, target_jyo, race_no)
