import re
from datetime import date
from logging import getLogger
from typing import Iterator

import lxml.html as lxml

from domain.factory import ProgramInfoFactory
from domain.model.info import ProgramCommonInfo, ProgramInfo, ProgramPlayerInfo
from infrastructure.const import MODULE_LOG_NAME
from infrastructure.getter import GetParserContent

from ._common import CommonMethods


class ProgramInfoFactoryImpl(ProgramInfoFactory):
    __common_methods: CommonMethods

    def __init__(self):
        self.logger = \
            getLogger(MODULE_LOG_NAME).getChild(self.__class__.__name__)
        self.__common_methods = CommonMethods()

    def each_jyoinfo(self,
                     target_date: date,
                     jyo_cd: int,
                     ed_race_no: int) -> Iterator[ProgramInfo]:
        for race_no in range(1, ed_race_no+1):
            yield self._raceinfo(target_date, jyo_cd, race_no)

    def _raceinfo(self, target_date: date,
                  jyo_cd: int,
                  race_no: int) -> ProgramInfo:
        # htmlをload
        target_url = (
            f"https://boatrace.jp/owpc/pc/race/racelist"
            f"?rno={race_no}"
            f"&jcd={jyo_cd:02}"
            f"&hd={target_date.strftime('%Y%m%d')}")
        self.logger.debug(f'get html: {target_url}')
        lx_content = GetParserContent.url_to_content(
            url=target_url,
            content_type="lxml"
        )
        self.logger.debug('get html completed.')
        common = self._commoninfo(lx_content)
        players = list(self._playersinfo(lx_content))

        return ProgramInfo(
            common,
            players
        )

    def _commoninfo(self,
                    lx_content: lxml.HtmlElement) -> ProgramCommonInfo:
        target_table_xpath = "/html/body/main/div/div/div/div[1]/div/div[2]"

        # SG, G1, G2, G3 一般
        raw_grade = \
            lx_content.xpath(target_table_xpath)[0].attrib["class"]
        grade = raw_grade.split()[1].strip()

        # 大会名
        taikai_xpath = "/".join([target_table_xpath, "h2"])
        taikai_name = lx_content.xpath(taikai_xpath)[0].text
        taikai_name = self.__common_methods.getonlyzenkaku2str(taikai_name)

        # race_type : 予選 優勝戦など/レース距離
        race_type_xpath = "/".join([target_table_xpath, "span"])
        race_str = lx_content.xpath(race_type_xpath)[0].text
        race_list = re.sub("[\u3000\t\r]", "", race_str).split("\n")
        race_type, race_kyori = list(filter(lambda x: x != "", race_list))
        race_type = self.__common_methods.getonlyzenkaku2str(race_type)
        race_kyori = self.__common_methods.rmletter2int(race_kyori)

        # 安定版or進入固定の有無
        antei_shinyu_xpath = "/".join([target_table_xpath, "/div/span"])
        antei_shinyu_el_list = lx_content.xpath(antei_shinyu_xpath)
        antei_shinyu_list = list(map(
            lambda x: x.text.strip(), antei_shinyu_el_list))

        if '安定板使用' in antei_shinyu_list:
            is_antei = True
        else:
            is_antei = False
        if '進入固定' in antei_shinyu_list:
            is_shinnyukotei = True
        else:
            is_shinnyukotei = False
        return ProgramCommonInfo(
            taikai_name,
            grade,
            race_type,
            race_kyori,
            is_antei,
            is_shinnyukotei
        )

    def _playersinfo(self,
                     lx_content: lxml.HtmlElement
                     ) -> Iterator[ProgramPlayerInfo]:
        for waku in range(1, 7):
            target_tbody_xpath = \
                f"/html/body/main/div/div/div/div[2]/div[4]/table/tbody[{waku}]"

            self.logger.debug(
                "Get player's informaiton.(id, level, name, etc)")
            # 登録番号
            player_id_xpath = "/".join([target_tbody_xpath,
                                        "tr[1]/td[3]/div[1]"])
            raw_player_id = lx_content.xpath(player_id_xpath)[0].text
            player_id = self.__common_methods.rmletter2int(raw_player_id)

            # 級
            player_level_xpath = "/".join([player_id_xpath, "span"])
            raw_player_level = lx_content.xpath(player_level_xpath)[0].text
            # 級が取りうる値かチェックする
            try:
                player_level = re.search(
                    r"[A,B][1,2]", raw_player_level).group(0)
            except AttributeError as e:
                self.logger.error(
                    f"player_level: {raw_player_level} error: {e}")
                player_level = None

            # 名前
            player_name_xpath = "/".join([target_tbody_xpath,
                                          "tr[1]/td[3]/div[2]/a"])
            raw_player_name = lx_content.xpath(player_name_xpath)[0].text
            player_name = raw_player_name.replace(
                '\n', '').replace('\u3000', '')

            # 所属、出身地
            home_birth_xpath = "/".join([target_tbody_xpath,
                                         "tr[1]/td[3]/div[3]/text()[1]"])
            # xpathでtextまで指定されている
            # 出力例: '\n                          愛知/愛知\n                          '
            home_birth = lx_content.xpath(home_birth_xpath)[0]
            home, birth_place = home_birth.strip().split("/")

            # 年齢、体重
            age_weight_xpath = "/".join([target_tbody_xpath,
                                         "tr[1]/td[3]/div[3]/text()[2]"])
            age_weight = lx_content.xpath(age_weight_xpath)[0]
            raw_age, raw_weight = age_weight.strip().split("/")
            age = self.__common_methods.rmletter2int(raw_age)
            weight = self.__common_methods.rmletter2float(raw_weight)

            # F/L数 平均ST
            num_F_xpath = "/".join([target_tbody_xpath,
                                    "tr[1]/td[4]/text()[1]"])
            raw_num_F = lx_content.xpath(num_F_xpath)[0]
            raw_num_F, raw_num_L, raw_avg_ST = \
                self._box_to_three_element(
                    lx_content, target_tbody_xpath, column_no=4)
            num_F = self.__common_methods.rmletter2int(raw_num_F.strip())
            num_L = self.__common_methods.rmletter2int(raw_num_L.strip())
            avg_ST = self.__common_methods.rmletter2float(raw_avg_ST.strip())

            # 全国勝率
            raw_all_1rate, raw_all_2rate, raw_all_3rate = \
                self._box_to_three_element(
                    lx_content, target_tbody_xpath, column_no=5)
            all_1rate = self.__common_methods.rmletter2float(
                raw_all_1rate.strip())
            all_2rate = self.__common_methods.rmletter2float(
                raw_all_2rate.strip())
            all_3rate = self.__common_methods.rmletter2float(
                raw_all_3rate.strip())

            # 当地勝率
            raw_local_1rate, raw_local_2rate, raw_local_3rate = \
                self._box_to_three_element(
                    lx_content, target_tbody_xpath, column_no=6)
            local_1rate = self.__common_methods.rmletter2float(
                raw_local_1rate.strip())
            local_2rate = self.__common_methods.rmletter2float(
                raw_local_2rate.strip())
            local_3rate = self.__common_methods.rmletter2float(
                raw_local_3rate.strip())

            # モーター情報は7番目
            raw_motor_no, raw_motor_2rate, raw_motor_3rate = \
                self._box_to_three_element(
                    lx_content, target_tbody_xpath, column_no=7)
            motor_no = self.__common_methods.rmletter2int(
                raw_motor_no.strip())
            motor_2rate = self.__common_methods.rmletter2float(
                raw_motor_2rate.strip())
            motor_3rate = self.__common_methods.rmletter2float(
                raw_motor_3rate.strip())

            # ボート情報は8番目
            raw_boat_no, raw_boat_2rate, raw_boat_3rate = \
                self._box_to_three_element(
                    lx_content, target_tbody_xpath, column_no=8)
            boat_no = self.__common_methods.rmletter2int(raw_boat_no.strip())
            boat_2rate = self.__common_methods.rmletter2float(
                raw_boat_2rate.strip())
            boat_3rate = self.__common_methods.rmletter2float(
                raw_boat_3rate.strip())

            self.logger.debug('get target player info completed.')

            yield ProgramPlayerInfo(
                player_name,
                player_id,
                player_level,
                home,
                birth_place,
                age,
                weight,
                num_F,
                num_L,
                avg_ST,
                all_1rate,
                all_2rate,
                all_3rate,
                local_1rate,
                local_2rate,
                local_3rate,
                motor_no,
                motor_2rate,
                motor_3rate,
                boat_no,
                boat_2rate,
                boat_3rate
            )

    def _box_to_three_element(self,
                              lx_content: lxml.HtmlElement,
                              root_xpath: str,
                              column_no: int) -> list:
        el_list = []
        for i in range(1, 4):
            target_xpath = "/".join([root_xpath,
                                     f"tr[1]/td[{column_no}]/text()[{i}]"])
            el_list.append(lx_content.xpath(target_xpath)[0])
        return el_list
