import re
from datetime import date, datetime, timedelta
from logging import getLogger
from typing import Iterator

import lxml.html as lxml

from domain.factory import ResultInfoFactory
from domain.model.info import ResultCommonInfo, ResultInfo, ResultPlayerInfo
from infrastructure.const import MODULE_LOG_NAME
from infrastructure.getter import GetParserContent

from ._common import CommonMethods


class ResultInfoFactoryImpl(ResultInfoFactory):
    def __init__(self):
        self.logger = getLogger(MODULE_LOG_NAME).getChild(
            self.__class__.__name__
        )
        self.__common_methods = CommonMethods()

    def each_jyoinfo(
        self, target_date: date, jyo_cd: int, ed_race_no: int
    ) -> Iterator[ResultInfo]:
        for race_no in range(1, ed_race_no + 1):
            yield self._raceinfo(target_date, jyo_cd, race_no)

    def _raceinfo(
        self, target_date: date, jyo_cd: int, race_no: int
    ) -> ResultInfo:
        target_url = (
            f"http://boatrace.jp/owpc/pc/race/raceresult?"
            f"rno={race_no}&"
            f"jcd={jyo_cd:02}&"
            f"hd={target_date.strftime('%Y%m%d')}"
        )
        self.logger.debug(f"Get result from {target_url}.")
        lx_content = GetParserContent.url_to_content(
            url=target_url, content_type="lxml"
        )
        common = self._commoninfo(lx_content)
        players = list(self._playerinfo(lx_content))
        self.logger.debug("Completed.")
        return ResultInfo(common, players)

    def _commoninfo(self, lx_content: lxml.HtmlElement) -> ResultCommonInfo:
        """
        水面気象情報と決まり手，返還挺の有無などの選手以外のレース結果情報
        """
        # これに情報を格納し最後に型に入れる。
        content_dict = {}
        # 水面気象情報の取得
        table_xpath = (
            "/html/body/main/div/div/div/div[2]"
            "/div[5]/div[2]/div[1]/div[1]/div/div[1]"
        )
        content_dict["weather_info"] = self.__common_methods.getweatherinfo(
            lx_content=lx_content, table_xpath=table_xpath
        )

        # 返還テーブルを抜く
        # 返還挺はリストのまま辞書に入れる
        # 返還艇がなければ空リスト
        table_xpath = (
            "/html/body/main/div/div/div/div[2]"
            "/div[5]/div[2]/div[1]/div[2]/div[1]"
            "/table/tbody/tr/td/div/div/span"
        )
        henkantei_list = lx_content.xpath(table_xpath)

        # 返還艇をint型に直す，変なやつはNoneでハンドル（ないと思う）
        def teistr2str(tei_str):
            tei = re.search(r"[1-6]", tei_str)
            if tei is not None:
                return str(tei.group(0))
            else:
                return None

        henkantei_list = list(
            map(lambda x: teistr2str(x.text), henkantei_list)
        )

        # 返還艇があればリスト長が1以上になる
        if len(henkantei_list) > 0:
            is_henkan = True
        else:
            is_henkan = False
        henkantei_str = ",".join(henkantei_list)
        content_dict["henkantei_list"] = henkantei_str
        content_dict["is_henkan"] = is_henkan

        # 決まりて
        table_xpath = (
            "/html/body/main/div/div/div/div[2]/div[5]"
            "/div[2]/div[1]/div[2]/div[2]/table/tbody/tr/td"
        )
        kimarite = lx_content.xpath(table_xpath)[0].text.strip()
        content_dict["kimarite"] = kimarite

        # 備考
        table_xpath = (
            "/html/body/main/div/div/div/div[2]/div[5]"
            "/div[2]/div[2]/table/tbody/tr/td"
        )
        biko = lx_content.xpath(table_xpath)[0].text.strip()
        content_dict["biko"] = biko

        # 払い戻し
        table_xpath = (
            "/html/body/main/div/div/div/div[2]"
            "/div[5]/div[1]/div/table/tbody/tr[1]/td[3]/span"
        )
        pay_contents = lx_content.xpath(table_xpath)
        pay_list = list(
            map(lambda x: int(re.sub(r"[^\d]", "", x.text)), pay_contents)
        )

        # 人気
        # TODO 順番問題でうまくいってない可能性大
        table_xpath = (
            "/html/body/main/div/div/div/div[2]"
            "/div[5]/div[1]/div/table/tbody/tr[1]/td[4]"
        )
        popular_contents = lx_content.xpath(table_xpath)
        popular_list = list(map(lambda x: x.text.strip(), popular_contents))
        content_dict["payout_3tan"] = pay_list[0]
        content_dict["popular_3tan"] = self.__common_methods.rmletter2int(
            popular_list[0]
        )
        content_dict["payout_3fuku"] = pay_list[1]
        content_dict["popular_3fuku"] = self.__common_methods.rmletter2int(
            popular_list[1]
        )
        content_dict["payout_2tan"] = pay_list[2]
        content_dict["popular_2tan"] = self.__common_methods.rmletter2int(
            popular_list[2]
        )
        content_dict["payout_2fuku"] = pay_list[3]
        content_dict["popular_2fuku"] = self.__common_methods.rmletter2int(
            popular_list[3]
        )
        content_dict["payout_1tan"] = pay_list[5]

        return ResultCommonInfo(**content_dict)

    def _playerinfo(
        self, lx_content: lxml.HtmlElement
    ) -> Iterator[ResultPlayerInfo]:
        target_table_xpath = (
            "/html/body/main/div/div/div/div[2]/div[4]/div[1]/div/table/tbody"
        )
        rank_xpath = "/".join([target_table_xpath, "/tr/td[1]"])
        rank_el_list = lx_content.xpath(rank_xpath)
        rank_list = list(
            map(
                lambda x: int(x.text) if x.text.isdecimal() else -1,
                rank_el_list,
            )
        )

        waku_xpath = "/".join([target_table_xpath, "/tr/td[2]"])
        waku_el_list = lx_content.xpath(waku_xpath)
        waku_list = list(
            map(
                lambda x: int(x.text) if x.text.isdecimal() else -1,
                waku_el_list,
            )
        )

        name_xpath = "/".join([target_table_xpath, "/tr/td[3]/span[2]"])
        name_el_list = lx_content.xpath(name_xpath)
        name_list = list(
            map(lambda x: x.text.replace("\u3000", "").strip(), name_el_list)
        )

        reg_no_xpath = "/".join([target_table_xpath, "/tr/td[3]/span[1]"])
        reg_el_list = lx_content.xpath(reg_no_xpath)
        reg_no_list = list(
            map(
                lambda x: int(x.text) if x.text.isdecimal() else -1,
                reg_el_list,
            )
        )

        racetime_xpath = "/".join([target_table_xpath, "/tr/td[4]"])
        racetime_el_list = lx_content.xpath(racetime_xpath)
        racetime_list = list(
            map(lambda x: self._racetime_str_to_sec(x.text), racetime_el_list)
        )

        waku_dict = {}
        for i, waku in enumerate(waku_list):
            waku_dict[waku] = {
                "rank": rank_list[i],
                "name": name_list[i],
                "no": reg_no_list[i],
                "racetime": racetime_list[i],
            }

        for waku in range(1, 7):
            # # 結果STテーブルの情報を取得
            tbody_xpath = (
                "/html/body/main/div/div/div/"
                "div[2]/div[4]/div[2]/div/table/tbody"
            )
            course, st_time = self.__common_methods.getSTtable(
                lx_content=lx_content,
                tbody_xpath=tbody_xpath,
                waku=waku,
                table_type="result",
            )

            yield ResultPlayerInfo(
                waku_dict[waku]["rank"],
                waku_dict[waku]["name"],
                waku_dict[waku]["no"],
                waku_dict[waku]["racetime"],
                course,
                st_time,
            )

    def _racetime_str_to_sec(self, str_racetime) -> float:

        # レースタイムは秒に変換する
        try:
            t = datetime.strptime(str_racetime, "%M'%S\"%f")
            delta = timedelta(
                seconds=t.second,
                microseconds=t.microsecond,
                minutes=t.minute,
            )
            racetime_sec = delta.total_seconds()
        except ValueError:
            racetime_sec = -1.0

        return racetime_sec
