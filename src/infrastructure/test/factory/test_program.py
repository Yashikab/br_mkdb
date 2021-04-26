import json
from datetime import date
from pathlib import Path

import pytest

from domain.model.info import ProgramCommonInfo, ProgramPlayerInfo
from infrastructure.factory import ProgramInfoFactoryImpl
from infrastructure.getter import GetParserContent

FILEPATH = Path(__file__).resolve().parents[1] / "test_html"
SAMPLEPATH = Path(__file__).resolve().parent / "sample" / "program"


class TestProgramFactoryImpl:

    with open(SAMPLEPATH / "common1.json", "r") as f:
        common1 = ProgramCommonInfo(**json.load(f))

    # 選手情報と枠番のインデックス(0~5)
    with open(SAMPLEPATH / "p1_1.json", "r") as f:
        p1_1 = ProgramPlayerInfo(**json.load(f))
    with open(SAMPLEPATH / "p1_2.json", "r") as f:
        p1_2 = ProgramPlayerInfo(**json.load(f))

    @pytest.mark.parametrize(
        ("target_date, target_jyo, race_no, ex_common, ex_p1, ex_p2"),
        [
            (date(2020, 4, 8), 6, 3, common1, p1_1, p1_2),
        ],
    )
    def test_raceinfo(
        self,
        target_date: date,
        target_jyo: int,
        race_no: int,
        ex_common: ProgramCommonInfo,
        ex_p1: ProgramPlayerInfo,
        ex_p2: ProgramPlayerInfo,
        mocker,
    ):
        filepath = (
            FILEPATH
            / f"pro_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(
            GetParserContent, "url_to_content", return_value=lx_content
        )
        pif = ProgramInfoFactoryImpl()
        programinfo = pif._raceinfo(target_date, target_jyo, race_no)

        assert programinfo.common == ex_common
        assert programinfo.players[ex_p1.waku - 1] == ex_p1
        assert programinfo.players[ex_p2.waku - 1] == ex_p2

    @pytest.mark.parametrize("ed_race_no", [(12), (0), (8)])
    def test_each_jyoinfo(self, ed_race_no, mocker):
        raceinfo_func = mocker.patch.object(
            ProgramInfoFactoryImpl, "_raceinfo"
        )
        pif = ProgramInfoFactoryImpl()
        list(pif.each_jyoinfo(date(2020, 4, 8), 6, ed_race_no))
        assert raceinfo_func.call_count == ed_race_no
