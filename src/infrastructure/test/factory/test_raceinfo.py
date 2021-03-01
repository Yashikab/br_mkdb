from datetime import date
from pathlib import Path

import pytest

FILEPATH = Path(__file__).resolve().parents[2] / "test_html"


class TestRaceInfoFactory:

    @pytest.mark.parametrize("date", [
        (date(2020, 4, 8)),
    ])
    def test_getinfo(self, date: date):
        filename = FILEPATH / f"ghp_{date.strftime('%Y%d%m')}.html"
        # 続きは明日
