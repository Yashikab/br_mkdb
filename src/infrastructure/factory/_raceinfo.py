import re
from datetime import date
from logging import getLogger
from pathlib import Path
from typing import Iterator, List

import lxml.html as lxml
import pandas as pd

from domain.factory import RaceInfoFactory
from domain.model.info import HoldRaceInfo
from infrastructure.const import MODULE_LOG_NAME
from infrastructure.getter import GetParserContent

from ._common import CommonMethods


class RaceInfoFactoryImpl(RaceInfoFactory):
    __base_url: str
    __common: CommonMethods

    def __init__(self):
        self.logger = getLogger(MODULE_LOG_NAME).getChild(self.__class__.__name__)
        self.__base_url = "https://www.boatrace.jp/owpc/pc/race/index"
        self.__common = CommonMethods()

    def getinfo(self, target_date: date) -> Iterator[HoldRaceInfo]:
        self.logger.debug(f"target_date: {date}")
        target_url = "?".join([self.__base_url, f"hd={target_date.strftime('%Y%m%d')}"])
        self.logger.debug(f"get info from {target_url}")
        __lx_content = GetParserContent.url_to_content(
            url=target_url, content_type="lxml"
        )

        # 抜き出すテーブルのxpath
        target_table_xpath = "/html/body/main/div/div/div/div[2]/div[3]/table"

        # 開催場名の取得
        place_name_xpath = "/".join([target_table_xpath, "tbody/tr/td[1]/a/img"])
        place_names = list(
            map(self._getplacename, __lx_content.xpath(place_name_xpath))
        )

        # 開催場コードの取得
        place_codes = self._conversion_to_codes(place_names)

        # 進行状況の取得
        shinko_info_xpath = "/".join([target_table_xpath, "tbody/tr/td[2]"])
        shinkos = list(map(self._getshinkoinfo, __lx_content.xpath(shinko_info_xpath)))

        # 終了レース番号の取得
        ed_races = [self._get_end_raceno(shinko) for shinko in shinkos]

        for p_name, p_code, shinko, ed_race in zip(
            place_names,
            place_codes,
            shinkos,
            ed_races,
        ):
            yield HoldRaceInfo(
                jyo_name=p_name,
                jyo_cd=p_code,
                shinko=shinko,
                ed_race_no=ed_race,
            )

    def _conversion_to_codes(self, place_names: List[str]) -> int:
        """会場名をコードに変換する"""
        # jyo master取得
        # TODO : jyo masterの場所を考える
        filepath = (
            Path(__file__).resolve().parents[2].joinpath("domain", "jyo_master.csv")
        )
        jyo_master = pd.read_csv(filepath, header=0)
        self.logger.debug("loading table to df done.")
        # 会場名をインデックスにする
        jyo_master.set_index("jyo_name", inplace=True)
        # コードへ返還
        code_names = list(map(lambda x: jyo_master.at[x, "jyo_cd"], place_names))
        return code_names

    def _getplacename(self, target_el: lxml.Element) -> str:
        """
        Elementから会場名を抜き出す
        """
        place_name = target_el.attrib["alt"]
        # 不要な文字を削除
        place_name = place_name.replace(">", "")
        place_name = self.__common.getonlyzenkaku2str(place_name)
        return place_name

    def _getshinkoinfo(self, target_el) -> str:
        """
        中止などの情報を抜き出す
        """
        return target_el.text

    def _get_end_raceno(self, shinko_msg: str) -> int:
        """進行情報の欄をみて，その日の最終レースを返す"""
        if re.search(r"1?[1-9]R以降中止", shinko_msg) is not None:
            # 以降なので、一個前のレースが最終レース
            end_race = int(re.search(r"1?[1-9]", shinko_msg).group(0)) - 1
        elif "中止" in shinko_msg:
            end_race = 0
        else:
            # 通常
            end_race = 12
        return end_race
