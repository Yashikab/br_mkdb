import json
from datetime import date
from pathlib import Path
from typing import List, Tuple

import pytest

from domain.model.info import ResultCommonInfo, ResultPlayerInfo
from infrastructure.factory import ResultInfoFactoryImpl
from infrastructure.getter import GetParserContent

FILEPATH = Path(__file__).resolve().parents[1] / "test_html"
SAMPLEPATH = Path(__file__).resolve().parent / "sample" / "result"


class TestResultFactoryImpl:

    with open(SAMPLEPATH / "common.json", "r") as f:
        common = ResultCommonInfo(**json.load(f))

    with open(SAMPLEPATH / "p1_1.json", "r") as f:
        p1_1 = (ResultPlayerInfo(**json.load(f)), 0)

    players = [p1_1]

    @pytest.mark.parametrize(
        ("target_date, target_jyo, race_no, ex_common, ex_players"),
        [(date(2020, 4, 10), 6, 9, common, players)],
    )
    def test_raceinfo(
        self,
        target_date: date,
        target_jyo: int,
        race_no: int,
        ex_common: ResultCommonInfo,
        ex_players: List[Tuple[ResultPlayerInfo, int]],
        mocker,
    ):
        filepath = (
            FILEPATH
            / f"res_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(
            GetParserContent, "url_to_content", return_value=lx_content
        )

        rif = ResultInfoFactoryImpl()
        resinfo = rif._raceinfo(target_date, target_jyo, race_no)

        assert resinfo.common == ex_common
        for ex_p, idx in ex_players:
            assert resinfo.players[idx] == ex_p

    @pytest.mark.parametrize("ed_race_no", [(12), (0), (8)])
    def test_each_jyoinfo(self, ed_race_no, mocker):
        raceinfo_func = mocker.patch.object(ResultInfoFactoryImpl, "_raceinfo")
        chif = ResultInfoFactoryImpl()
        list(chif.each_jyoinfo(date(2020, 4, 8), 6, ed_race_no))
        assert raceinfo_func.call_count == ed_race_no
