from datetime import date
from pathlib import Path

import pytest

from infrastructure.factory import RaceInfoFactoryImpl
from infrastructure.getter import GetParserContent

FILEPATH = Path(__file__).resolve().parents[2] / "test_html"


class TestRaceInfoFactoryImpl:

    names1 = ['江戸川', '浜名湖', '常滑', '津',
              '三国', '尼崎', '徳山', '下関',
              '若松', '福岡', '大村']
    codes1 = [3, 6, 8, 9, 10, 13, 18, 19, 20, 22, 24]
    shinkos1 = ["-" for i in range(len(names1))]
    ed_races1 = [12 for i in range(len(names1))]

    @pytest.mark.parametrize(
        "target_date, ex_names, ex_codes, ex_shinkos, ex_ed_races",
        [
            (date(2020, 4, 8), names1, codes1, shinkos1, ed_races1),
        ]
    )
    def test_getinfo(self,
                     target_date: date,
                     ex_names: list,
                     ex_codes: list,
                     ex_shinkos: list,
                     ex_ed_races: list,
                     mocker):
        filename = FILEPATH / f"ghp_{target_date.strftime('%Y%d%m')}.html"
        lx_content = GetParserContent.file_to_content(filename, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content",
                            return_value=lx_content)
        rif = RaceInfoFactoryImpl()
        holdrace_info_itr = rif.getinfo(target_date=target_date)
        names = list()
        codes = list()
        shinkos = list()
        ed_races = list()
        for hri in holdrace_info_itr:
            names.append(hri.jyo_name)
            codes.append(hri.jyo_cd)
            shinkos.append(hri.shinko)
            ed_races.append(hri.ed_race_no)

        assert names == ex_names
        assert codes == ex_codes
        assert shinkos == ex_shinkos
        assert ed_races == ex_ed_races
