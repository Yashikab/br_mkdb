from datetime import date
from pathlib import Path
from typing import Tuple

import pytest
from domain.model.info import ProgramCommonInfo, ProgramPlayerInfo

from infrastructure.factory import ProgramInfoFactoryImpl
from infrastructure.getter import GetParserContent

FILEPATH = Path(__file__).resolve().parents[1] / "test_html"


class TestProgramFactoryImpl:

    common1 = ProgramCommonInfo(
        "スポーツ報知　ビクトリーカップ",
        "is_ippan",
        "予選",
        1800,
        False,
        False
    )
    player1_1 = (None, 0)
    player1_2 = (None, 1)

    @pytest.mark.parametrize(
        ("target_date, target_jyo, race_no, ex_common, ex_p1, ex_p2"), [
            (date(2020, 4, 8), 6, 3, common1, player1_1, player1_2),
        ])
    def test_raceinfo(self,
                      target_date: date,
                      target_jyo: int,
                      race_no: int,
                      ex_common: ProgramCommonInfo,
                      ex_p1: Tuple[ProgramPlayerInfo, int],
                      ex_p2: Tuple[ProgramPlayerInfo, int],
                      mocker):
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
        programinfo = pif._raceinfo(target_date, target_jyo, race_no)

        assert programinfo.common == ex_common
        assert programinfo.player[ex_p1[1]] == ex_p1[0]
        assert programinfo.player[ex_p2[1]] == ex_p2[0]
