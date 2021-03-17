from pathlib import Path
import pytest

from datetime import date
from typing import Tuple

import pytest

FILEPATH = Path(__file__).resolve().parents[1] / "test_html"


class TestOddsInfoFactoryImpl:

    def test_three_rentan(self,
                          target_date: date,
                          target_jyo: int,
                          race_no: int,
                          ex_three_rentan: Tuple[int, int, int, float],
                          mocker):
        pass

    def test_three_renfuku(self,
                           target_date: date,
                           target_jyo: int,
                           race_no: int,
                           ex_three_renfuku: Tuple[int, int, int, float],
                           mocker):
        pass

    def test_two_rentan(self,
                        target_date: date,
                        target_jyo: int,
                        race_no: int,
                        ex_two_rentan: Tuple[int, int, float],
                        mocker):
        pass

    def test_two_renfuku(self,
                         target_date: date,
                         target_jyo: int,
                         race_no: int,
                         ex_two_renfuku: Tuple[int, int, float],
                         mocker):
        pass

    def test_tansho(self,
                    target_date: date,
                    target_jyo: int,
                    race_no: int,
                    ex_tansho: Tuple[int, float],
                    mocker):
        pass
