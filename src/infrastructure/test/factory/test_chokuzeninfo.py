import json
from datetime import date
from pathlib import Path
from typing import List, Tuple

import pytest

from infrastructure.factory import ChokuzenInfoFactoryImpl
from domain.model.info import ChokuzenPlayerInfo, WeatherInfo
from infrastructure.getter import GetParserContent

FILEPATH = Path(__file__).resolve().parents[1] / "test_html"
SAMPLEPATH = Path(__file__).resolve().parent / "sample" / "chokuzen"


class TestChokuzenFactoryImpl:

    with open(SAMPLEPATH / "common.json", "r") as f:
        common = WeatherInfo(**json.load(f))

    with open(SAMPLEPATH / "p1_1.json", "r") as f:
        p1_1 = (ChokuzenPlayerInfo(**json.load(f)), 0)
    with open(SAMPLEPATH / "p1_5.json", "r") as f:
        p1_5 = (ChokuzenPlayerInfo(**json.load(f)), 5)

    players = [p1_1, p1_5]

    @pytest.mark.parametrize(
        ("target_date, target_jyo, race_no, ex_common, ex_players"), [
            (date(2020, 4, 8), 6, 9, common, players)
        ]
    )
    def test_raceinfo(self,
                      target_date: date,
                      target_jyo: int,
                      race_no: int,
                      ex_common: WeatherInfo,
                      ex_players: List[Tuple[ChokuzenPlayerInfo, int]],
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
        for ex_p, idx in ex_players:
            assert chokuinfo.players[idx] == ex_p

    @pytest.mark.parametrize("ed_race_no", [
        (12), (0), (8)
    ])
    def test_each_jyoinfo(self, ed_race_no, mocker):
        raceinfo_func = mocker.patch.object(
            ChokuzenInfoFactoryImpl, "_raceinfo")
        chif = ChokuzenInfoFactoryImpl()
        list(chif.each_jyoinfo(date(2020, 4, 8), 6, ed_race_no))
        assert raceinfo_func.call_count == ed_race_no
