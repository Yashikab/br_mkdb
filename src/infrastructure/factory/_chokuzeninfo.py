from datetime import date
from logging import getLogger
from typing import Iterator

import lxml.html as lxml

from domain.factory import ChokuzenInfoFactory
from domain.model.info import ChokuzenInfo, ChokuzenPlayerInfo, WeatherInfo
from infrastructure.const import MODULE_LOG_NAME
from infrastructure.getter import GetParserContent

from ._common import CommonMethods


class ChokuzenInfoFactoryImpl(ChokuzenInfoFactory):
    def __init__(self):
        self.logger = getLogger(MODULE_LOG_NAME).getChild(
            self.__class__.__name__
        )
        self.__common_methods = CommonMethods()

    def each_jyoinfo(
        self, target_date: date, jyo_cd: int, ed_race_no: int
    ) -> Iterator[ChokuzenInfo]:
        for race_no in range(1, ed_race_no + 1):
            yield self._raceinfo(target_date, jyo_cd, race_no)

    def _raceinfo(
        self, target_date: date, jyo_cd: int, race_no: int
    ) -> ChokuzenInfo:
        target_url = (
            f"https://boatrace.jp/owpc/pc/race/beforeinfo?"
            f"rno={race_no}&"
            f"jcd={jyo_cd:02}&"
            f"hd={target_date.strftime('%Y%m%d')}"
        )
        self.logger.debug(f"get html: {target_url}")
        lx_content = GetParserContent.url_to_content(
            url=target_url, content_type="lxml"
        )

        # common
        common = self._commoninfo(lx_content)
        players = list(self._playersinfo(lx_content))
        return ChokuzenInfo(common, players)

    def _commoninfo(self, lx_content: lxml.HtmlElement) -> WeatherInfo:
        self.logger.debug("get common info")
        table_xpath = (
            "/html/body/main/div/div/div/div[2]" "/div[4]/div[2]/div[2]/div[1]"
        )
        content = self.__common_methods.getweatherinfo(
            lx_content=lx_content, table_xpath=table_xpath
        )
        self.logger.debug("done.")

        return content

    def _playersinfo(
        self, lx_content: lxml.HtmlElement
    ) -> Iterator[ChokuzenPlayerInfo]:
        for waku in range(1, 7):
            # 選手直前情報を選択 css selectorより
            target_p_table_xpath = (
                f"/html/body/main/div/div/div/div[2]/div[4]"
                f"/div[1]/div[1]/table/tbody[{waku}]"
            )

            # 名前
            p_name_xpath = "/".join([target_p_table_xpath, "tr[1]/td[3]/a"])
            name = lx_content.xpath(p_name_xpath)[0].text
            name = name.replace("\u3000", "")

            # 体重
            p_weight_xpath = "/".join([target_p_table_xpath, "tr[1]/td[4]"])
            weight = lx_content.xpath(p_weight_xpath)[0].text
            weight = self.__common_methods.rmletter2float(weight)

            # 調整体重
            p_chosei_xpath = "/".join([target_p_table_xpath, "tr[3]/td[1]"])
            chosei_weight = lx_content.xpath(p_chosei_xpath)[0].text
            chosei_weight = self.__common_methods.rmletter2float(chosei_weight)

            # 展示タイムは5番目td (調整体重の方じゃないので注意)
            p_tenji_xpath = "/".join([target_p_table_xpath, "tr[1]/td[5]"])
            tenji_T = lx_content.xpath(p_tenji_xpath)[0].text
            tenji_T = self.__common_methods.rmletter2float(tenji_T)

            # チルトは6番目
            p_tilt_xpath = "/".join([target_p_table_xpath, "tr[1]/td[6]"])
            tilt = lx_content.xpath(p_tilt_xpath)[0].text
            tilt = self.__common_methods.rmletter2float(tilt)

            # スタート展示テーブルの選択
            target_ST_tbody = (
                "/html/body/main/div/div/div/div[2]/"
                "div[4]/div[2]/div[1]/table/tbody"
            )
            tenji_C, tenji_ST = self.__common_methods.getSTtable(
                lx_content, target_ST_tbody, waku
            )

            yield ChokuzenPlayerInfo(
                waku,
                name,
                weight,
                chosei_weight,
                tenji_T,
                tilt,
                tenji_C,
                tenji_ST,
            )
