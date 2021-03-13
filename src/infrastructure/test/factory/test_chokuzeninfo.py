import json
from datetime import date
from pathlib import Path
from typing import Tuple

import pytest

from infrastructure.factory import ChokuzenInfoFactoryImpl
from src.domain.model.info import ChokuzenPlayerInfo, WeatherInfo
from src.infrastructure.getter import GetParserContent

FILEPATH = Path(__file__).resolve().parents[1] / "test_html"
SAMPLEPATH = Path(__file__).resolve().parent / "sample" / "chokuzen"


class TestChokuzenFactoryImpl:

    with open(SAMPLEPATH / "common.json", "r") as f:
        common = WeatherInfo(**json.load(f))

    with open(SAMPLEPATH / "p1_1.json", "r") as f:
        p1_1 = (ChokuzenPlayerInfo(**json.load(f)), 0)
    with open(SAMPLEPATH / "p1_5.json", "r") as f:
        p1_5 = (ChokuzenPlayerInfo(**json.load(f)), 4)

    @pytest.mark.parametrize(
        ("target_date, target_jyo, race_no, ex_common, ex_p1, ex_p2"), [
            (date(20200, 4, 8), 6, 9, common, p1_1, p1_5)
        ]
    )
    def test_raceinfo(self,
                      target_date: date,
                      target_jyo: int,
                      race_no: int,
                      ex_common: WeatherInfo,
                      ex_p1: Tuple[ChokuzenPlayerInfo, int],
                      ex_p2: Tuple[ChokuzenPlayerInfo, int],
                      mocker
                      ):
        filepath = FILEPATH / \
            f"choku_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content",
                            return_value=lx_content)

        chif = ChokuzenInfoFactoryImpl()
        chokuinfo = chif._raceinfo(target_date, target_jyo, race_no)

        assert chokuinfo.common == ex_common
        assert chokuinfo.players[ex_p1[1]] == ex_p1[0]
        assert chokuinfo.players[ex_p2[1]] == ex_p2[0]
