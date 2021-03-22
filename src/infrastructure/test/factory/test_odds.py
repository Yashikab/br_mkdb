from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import List, Tuple

import pytest
from domain.model.info import OddsInfo

from infrastructure.factory import OddsInfoFactoryImpl
from infrastructure.getter import GetParserContent

FILEPATH = Path(__file__).resolve().parents[1] / "test_html"


class TestOddsInfoFactoryImpl:

    ex_three_rentans1 = [
        (1, 2, 3, 6.5),
        (3, 4, 5, 1621.0),
        (4, 5, 6, 2555.0),
        (6, 5, 4, 810.9),
    ]
    ex_three_rentans2 = [
        (1, 2, 3, 30.1),
        (1, 2, 5, -9999.0),
        (3, 1, 4, 30.2),
    ]

    @pytest.mark.parametrize(
        "target_date, target_jyo, race_no, ex_three_rentans",
        [
            (date(2020, 4, 8), 6, 9, ex_three_rentans1),
            (date(2019, 1, 3), 22, 2, ex_three_rentans2),
        ],
    )
    def test_three_rentan(
        self,
        target_date: date,
        target_jyo: int,
        race_no: int,
        ex_three_rentans: List[Tuple[int, int, int, float]],
        mocker,
    ):
        filepath = (
            FILEPATH
            / f"odds_3tan_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(
            GetParserContent, "url_to_content", return_value=lx_content
        )
        oif = OddsInfoFactoryImpl()
        three_rentans = oif._three_rentan(target_date, target_jyo, race_no)
        three_rentans = asdict(three_rentans)
        for ex_three_rentan in ex_three_rentans:
            fst = ex_three_rentan[0]
            snd = ex_three_rentan[1]
            trd = ex_three_rentan[2]
            expected = ex_three_rentan[3]
            assert three_rentans[f"comb_{fst}{snd}{trd}"] == expected

    ex_three_renfukus1 = [
        (1, 2, 3, 2.9),
        (2, 3, 4, 160.2),
        (3, 4, 5, 200.3),
        (4, 5, 6, 228.9),
    ]

    @pytest.mark.parametrize(
        "target_date, target_jyo, race_no, ex_three_renfukus",
        [(date(2020, 4, 8), 6, 9, ex_three_renfukus1)],
    )
    def test_three_renfuku(
        self,
        target_date: date,
        target_jyo: int,
        race_no: int,
        ex_three_renfukus: List[Tuple[int, int, int, float]],
        mocker,
    ):
        filepath = (
            FILEPATH
            / f"odds_3fuku_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(
            GetParserContent, "url_to_content", return_value=lx_content
        )
        oif = OddsInfoFactoryImpl()
        three_renfukus = oif._three_renfuku(target_date, target_jyo, race_no)
        three_renfukus = asdict(three_renfukus)
        for ex_three_renfuku in ex_three_renfukus:
            fst = ex_three_renfuku[0]
            snd = ex_three_renfuku[1]
            trd = ex_three_renfuku[2]
            expected = ex_three_renfuku[3]
            assert three_renfukus[f"comb_{fst}{snd}{trd}"] == expected

    ex_two_rentans1 = [
        (1, 2, 2.7),
        (2, 3, 101.3),
        (3, 4, 238.5),
        (6, 5, 135.1),
    ]

    @pytest.mark.parametrize(
        "target_date, target_jyo, race_no, ex_two_rentans",
        [(date(2020, 4, 8), 6, 9, ex_two_rentans1)],
    )
    def test_two_rentan(
        self,
        target_date: date,
        target_jyo: int,
        race_no: int,
        ex_two_rentans: List[Tuple[int, int, float]],
        mocker,
    ):
        filepath = (
            FILEPATH
            / f"odds_2tanfuku_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(
            GetParserContent, "url_to_content", return_value=lx_content
        )
        oif = OddsInfoFactoryImpl()
        two_rentans = oif._two_rentan(target_date, target_jyo, race_no)
        two_rentans = asdict(two_rentans)
        for ex_two_rentan in ex_two_rentans:
            fst = ex_two_rentan[0]
            snd = ex_two_rentan[1]
            expected = ex_two_rentan[2]
            assert two_rentans[f"comb_{fst}{snd}"] == expected

    ex_two_renfukus1 = [
        (1, 2, 2.0),
        (2, 3, 25.7),
        (3, 4, 47.1),
    ]

    @pytest.mark.parametrize(
        "target_date, target_jyo, race_no, ex_two_renfukus",
        [(date(2020, 4, 8), 6, 9, ex_two_renfukus1)],
    )
    def test_two_renfuku(
        self,
        target_date: date,
        target_jyo: int,
        race_no: int,
        ex_two_renfukus: List[Tuple[int, int, float]],
        mocker,
    ):
        filepath = (
            FILEPATH
            / f"odds_2tanfuku_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(
            GetParserContent, "url_to_content", return_value=lx_content
        )
        oif = OddsInfoFactoryImpl()
        two_renfukus = oif._two_renfuku(target_date, target_jyo, race_no)
        two_renfukus = asdict(two_renfukus)
        for ex_two_renfuku in ex_two_renfukus:
            fst = ex_two_renfuku[0]
            snd = ex_two_renfuku[1]
            expected = ex_two_renfuku[2]
            assert two_renfukus[f"comb_{fst}{snd}"] == expected

    ex_tanshos1 = [(1, 1.0), (2, 6.1), (3, 12.2), (6, 9.1)]

    @pytest.mark.parametrize(
        "target_date, target_jyo, race_no, ex_tanshos",
        [(date(2020, 4, 8), 6, 9, ex_tanshos1)],
    )
    def test_tansho(
        self,
        target_date: date,
        target_jyo: int,
        race_no: int,
        ex_tanshos: List[Tuple[int, float]],
        mocker,
    ):
        filepath = (
            FILEPATH
            / f"odds_1tan_{target_date.strftime('%Y%m%d')}{target_jyo}{race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(
            GetParserContent, "url_to_content", return_value=lx_content
        )
        oif = OddsInfoFactoryImpl()
        tanshos = oif._tansho(target_date, target_jyo, race_no)
        tanshos = asdict(tanshos)
        for ex_tansho in ex_tanshos:
            fst = ex_tansho[0]
            expected = ex_tansho[1]
            assert tanshos[f"comb_{fst}"] == expected

    def test_call_raceinfo(self, mocker):

        oif = OddsInfoFactoryImpl()
        oddsinfo = oif._raceinfo(date(2020, 4, 8), 6, 9)
        assert type(oddsinfo) == OddsInfo

    @pytest.mark.parametrize("ed_race_no", [(12), (0), (8)])
    def test_each_jyoinfo(self, ed_race_no, mocker):
        raceinfo_func = mocker.patch.object(OddsInfoFactoryImpl, "_raceinfo")
        oif = OddsInfoFactoryImpl()
        list(oif.each_jyoinfo(date(2020, 4, 8), 6, ed_race_no))
        assert raceinfo_func.call_count == ed_race_no
