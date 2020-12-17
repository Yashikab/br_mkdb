# python 3.7.5
# coding: utf-8
"""
HTMLから情報をスクレイピングするためのモジュール
"""
from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
import re
import sys
import time
from typing import Iterator
from urllib.request import urlopen

import bs4
from bs4 import BeautifulSoup as bs
import lxml.html as lxml
import numpy as np
import pandas as pd

from module import const


class CommonMethods4Official:
    def __init__(self):
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)

    def _url2lxml(self, url) -> lxml.HtmlComment:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 5回リトライする
        success_flg = False
        html_content = None
        for i in range(5):
            with urlopen(url, timeout=10.) as f:
                if f.status == 200:
                    html_content = f.read()
                    success_flg = True
                else:
                    self.logger.warning(f"Not completed to download: {url}")
                    self.logger.warning(f"{f.status}: {f.reason}")
            if success_flg:
                break
            self.logger.debug("retry")
            time.sleep(0.5)
        if not success_flg:
            raise self.logger.error("Didn't succeed in 5 times retry.")

        lx_content = lxml.fromstring(html_content)

        return lx_content

    def _getplayertable2list(self,
                             soup: bs4.BeautifulSoup,
                             table_selector: str) -> list:
        """
        選手情報のテーブルを抜き出し, 行ごとのリストで返す．

        Parameters
        ----------
            soup : bs4.BeautifulSoup
            table_selector : str
                bs4用テーブルのセレクタ−

        Returns
        -------
            player_html_list : list
                選手ごとの行のhtmlを格納したリスト
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        target_table_html = soup.select_one(table_selector)
        player_html_list = target_table_html.select('tbody')
        assert len(player_html_list) == 6, \
            f"{self.__class__.__name__}:lengh is not 6:{len(player_html_list)}"
        return player_html_list

    def _getSTtable2tuple(self,
                          lx_content: lxml.HtmlComment,
                          tbody_xpath: str,
                          waku: int,
                          table_type: str = "default") -> tuple:
        """
        スタート情報のテーブルを抜き取り対象枠のコースとSTタイムを
        タプルにして返す.

        Parameters
        ----------
            soup : bs4.BeautifulSoup
            table_selector : str
                スタート情報のテーブル
            waku : int
                知りたい情報の枠
            table_type
                直前と結果で少し処理が違う

        Returns
        -------
            course st_time : tuple
                対象枠のコースとSTタイムをタプルで返す
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')

        tr_xpath = "/".join([tbody_xpath, "tr"])
        len_course = len(lx_content.xpath(tr_xpath))
        # 欠場挺があると6挺にならないときがあるので、assertをつかわない
        if len_course < 6:
            self.logger.warning("there are less than 6 boats.")
        # コース抜き出し
        # コースがキーで，号がvalueなので全て抜き出してから逆にする
        waku_list = []
        st_time_list = []
        for i in range(1, len_course + 1):
            try:
                waku_no_xpath = "/".join([
                    tbody_xpath, f"tr[{i}]/td/div/span[1]"])
                waku_no = lx_content.xpath(waku_no_xpath)[0].text
                waku_list.append(self._rmletter2int(waku_no))

                if table_type == "result":
                    st_time_xpath = "/".join([
                        tbody_xpath,
                        f"tr[{i}]/td/div/span[3]/span/text()"])
                    st_time = lx_content.xpath(st_time_xpath)[0].strip()
                else:
                    st_time_xpath = "/".join([
                        tbody_xpath, f"tr[{i}]/td/div/span[3]"])
                    st_time = lx_content.xpath(st_time_xpath)[0].text
                # Fをマイナスに変換し，少数化
                st_time = self._rmletter2float(st_time.replace('F', '-'))
                st_time_list.append(st_time)
            except IndexError as e:
                self.logger.error(e)

        # waku がwaku_listになければ
        if waku not in waku_list:
            return (None, None)

        # 0~5のインデックスなので1~6へ変換のため+1
        course_idx = waku_list.index(waku)
        course = course_idx + 1

        # listのキーはコースであることに注意
        st_time = st_time_list[course_idx]

        return (course, st_time)

    def _getweatherinfo2dict(self,
                             lx_content: lxml.HtmlElement,
                             table_xpath: str) -> dict:
        """
        水面気象情報テーブルのスクレイパー

        Parameters
        ----------
            lx_content: lxml.HtmlElement,
            table_selector : str

        Returns
        -------
            content_dict : dict
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')

        # 気温
        temp_xpath = "/".join([table_xpath, "div[1]/div/span[2]"])
        temp = lx_content.xpath(temp_xpath)[0].text.strip()
        temp = self._rmletter2float(temp)

        # 天気
        weather_xpath = "/".join([table_xpath, "div[2]/div/span"])
        weather = lx_content.xpath(weather_xpath)[0].text.strip()
        weather = self._getonlyzenkaku2str(weather)

        # 風速
        wind_v_xpath = "/".join([table_xpath, "div[3]/div/span[2]"])
        wind_v = lx_content.xpath(wind_v_xpath)[0].text.strip()
        wind_v = self._rmletter2int(wind_v)

        # 水温
        w_temp_xpath = "/".join([table_xpath, "div[5]/div/span[2]"])
        w_temp = lx_content.xpath(w_temp_xpath)[0].text.strip()
        w_temp = self._rmletter2float(w_temp)

        # 波高
        wave_xpath = "/".join([table_xpath, "div[6]/div/span[2]"])
        wave = lx_content.xpath(wave_xpath)[0].text.strip()
        wave = self._rmletter2int(wave)

        # 風向き
        # 画像のみの情報なので，16方位の数字（画像の名前）を抜く
        # p中のクラス名2番目にある
        wind_dr_xpath = "/".join([table_xpath, "div[4]/p"])
        wind_dr_class = lx_content.xpath(wind_dr_xpath)[0].attrib["class"]
        wind_dr = wind_dr_class.split()[1].strip()
        wind_dr = self._rmletter2int(wind_dr)

        content_dict = {
            'temp': temp,
            'weather': weather,
            'wind_v': wind_v,
            'w_temp': w_temp,
            'wave': wave,
            'wind_dr': wind_dr
        }
        return content_dict

    def _text2list_rn_split(self,
                            input_content: bs4.element.Tag,
                            expect_length: int) -> list:
        """
        スクレイピングしたときスペースと\\r\\nで区切られた文字列をリスト化する

        Parameters
        ----------
            input_content : beautifulsoup.element.Tag
                入力するパースした要素
            expect_length : int
                期待する返却リストの長さ

        Return
        ------
            output_list : list
                返却するリスト
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        edit_content = input_content.text.replace(' ', '')
        # /r/n, /rを/nに寄せる
        edit_content = edit_content.replace('\r\n', '\n')
        edit_content = edit_content.replace('\r', '\n')
        output_list = edit_content.split('\n')[1:-1]
        assert len(output_list) == expect_length,\
            f"lengh is not {expect_length}:{len(output_list)}"
        return output_list

    def _choose_2nd_span(self, target_html: str) -> str:
        """
        風速・水温・波高ぬきだし用関数\n
        spanの2つめの要素をstr で返却
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        return target_html.select('span')[1].text

    def _rmletter2float(self, in_str: str) -> float:
        """
        文字列から文字を取り除き少数で返す
        マイナス表記は残す
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        in_str = re.search(r'-{0,1}[0-9]*\.[0-9]+', in_str)
        if in_str is not None:
            out_float = float(in_str.group(0))
        else:
            out_float = None
        return out_float

    def _rmletter2int(self, in_str: str) -> int:
        """
        文字列から文字を取り除き整数で返す
        マイナス表記は残す
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        try:
            in_str = re.search(r'-{0,1}[0-9]+', in_str)
            out_int = int(in_str.group(0))
        except AttributeError as e:
            self.logger.error(f"in_str: {in_str}, error: {e}")
            out_int = None
        return out_int

    def _getonlyzenkaku2str(self, in_str: str) -> str:
        try:
            # 全角の抽出
            return re.search(r'[^\x01-\x7E]+', in_str).group(0)
        except ValueError:
            return None


class GetHoldPlacePast(CommonMethods4Official):
    """
    指定した日付での開催会場を取得する
    開催中のレースは無理
    """
    def __init__(self, target_date: int):
        """
        Parameters
        ----------
            target_date : int
                yyyymmdd型
        """
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        # htmlをload
        base_url = 'https://www.boatrace.jp/owpc/pc/race/index?'
        target_url = f'{base_url}hd={target_date}'
        self.logger.debug(f'access: {target_url}')
        self.__lx_content = super()._url2lxml(target_url)

        # 抜き出すテーブルのxpath
        target_table_xpath = "/html/body/main/div/div/div/div[2]/div[3]/table"

        # 会場名のパス
        place_name_xpath = "/".join([target_table_xpath,
                                     "tbody/tr/td[1]/a/img"])
        self.place_name_list = \
            list(map(self._getplacename,
                     self.__lx_content.xpath(place_name_xpath)))

        # 進行状況のパス
        shinko_info_xpath = "/".join([target_table_xpath, "tbody/tr/td[2]"])
        self.shinko_info_list = \
            list(map(self._getshinkoinfo,
                     self.__lx_content.xpath(shinko_info_xpath)))

    def holdplace2strlist(self) -> list:
        """
        会場名のままset型で返す
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        return self.place_name_list

    def holdplace2cdlist(self) -> list:
        """
        会場コードをset型で返す．
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # jyo master取得
        filepath = Path(__file__).parent.resolve().joinpath('jyo_master.csv')
        jyo_master = pd.read_csv(filepath, header=0)
        self.logger.debug('loading table to df done.')
        # 会場名をインデックスにする
        jyo_master.set_index('jyo_name', inplace=True)
        # コードへ返還
        code_name_list = \
            list(map(
                lambda x: jyo_master.at[x, 'jyo_cd'], self.place_name_list))
        return code_name_list

    def holdinfo2dict(self, hp_name: str) -> dict:
        """開催場の情報を辞書型で返す

        Parameters
        ----------
            hp_name: str
                開催場名
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        shinko = self.shinko_info_list[self.place_name_list.index(hp_name)]
        ed_race_no = self._get_end_raceno(shinko)

        content_dict = {
            'shinko': shinko,
            'ed_race_no': ed_race_no
        }
        return content_dict

    def _get_end_raceno(self, msg: str) -> int:
        """進行情報の欄をみて，その日の最終レースを返す"""
        if re.search(r'1?[1-9]R以降中止', msg) is not None:
            end_race = int(re.search(r'1?[1-9]', msg).group(0))
        elif '中止' in msg:
            end_race = 0
        else:
            # 通常
            end_race = 12
        return end_race

    def _getplacename(self, target_el: lxml.Element) -> str:
        """
        Elementから会場名を抜き出す
        """
        place_name = target_el.attrib["alt"]
        # 不要な文字を削除
        place_name = place_name.replace(">", "")
        place_name = super()._getonlyzenkaku2str(place_name)
        return place_name

    def _getshinkoinfo(self, target_el) -> str:
        """
        中止などの情報を抜き出す
        """
        return target_el.text


class OfficialProgram(CommonMethods4Official):
    def __init__(self,
                 race_no: int,
                 jyo_code: int,
                 date: int) -> None:
        """
        競艇公式サイトの番組表からのデータ取得
        レース番，場コード，日付を入力し公式サイトへアクセス

        Parameters
        ----------
            race_no : int
                何レース目か
            jyo_code : int
                会場コード
            date : int
                yyyymmdd形式で入力

        """
        # logger設定
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)

        # htmlをload
        base_url = 'https://boatrace.jp/owpc/pc/race/racelist?'
        target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={date}'
        self.logger.debug(f'get html: {target_url}')
        self.__lx_content = super()._url2lxml(target_url)
        self.logger.debug('get html completed.')

    def getplayerinfo2dict(self, waku: int) -> dict:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')

        target_tbody_xpath = \
            f"/html/body/main/div/div/div/div[2]/div[4]/table/tbody[{waku}]"

        self.logger.debug("Get player's informaiton.(id, level, name, etc)")
        # 登録番号
        player_id_xpath = "/".join([target_tbody_xpath, "tr[1]/td[3]/div[1]"])
        raw_player_id = self.__lx_content.xpath(player_id_xpath)[0].text
        player_id = super()._rmletter2int(raw_player_id)

        # 級
        player_level_xpath = "/".join([player_id_xpath, "span"])
        raw_player_level = self.__lx_content.xpath(player_level_xpath)[0].text
        # 級が取りうる値かチェックする
        try:
            player_level = re.search(r"[A,B][1,2]", raw_player_level).group(0)
        except AttributeError as e:
            self.logger.error(f"player_level: {raw_player_level} error: {e}")
            player_level = None

        # 名前
        player_name_xpath = "/".join([target_tbody_xpath,
                                      "tr[1]/td[3]/div[2]/a"])
        raw_player_name = self.__lx_content.xpath(player_name_xpath)[0].text
        player_name = raw_player_name.replace('\n', '').replace('\u3000', '')

        # 所属、出身地
        home_birth_xpath = "/".join([target_tbody_xpath,
                                     "tr[1]/td[3]/div[3]/text()[1]"])
        # xpathでtextまで指定されている
        # 出力例: '\n                          愛知/愛知\n                          '
        home_birth = self.__lx_content.xpath(home_birth_xpath)[0]
        home, birth_place = home_birth.strip().split("/")

        # 年齢、体重
        age_weight_xpath = "/".join([target_tbody_xpath,
                                     "tr[1]/td[3]/div[3]/text()[2]"])
        age_weight = self.__lx_content.xpath(age_weight_xpath)[0]
        raw_age, raw_weight = age_weight.strip().split("/")
        age = super()._rmletter2int(raw_age)
        weight = super()._rmletter2float(raw_weight)

        # F/L数 平均ST
        num_F_xpath = "/".join([target_tbody_xpath,
                                "tr[1]/td[4]/text()[1]"])
        raw_num_F = self.__lx_content.xpath(num_F_xpath)[0]
        raw_num_F, raw_num_L, raw_avg_ST = \
            self._box_to_three_element(target_tbody_xpath, column_no=4)
        num_F = super()._rmletter2int(raw_num_F.strip())
        num_L = super()._rmletter2int(raw_num_L.strip())
        avg_ST = super()._rmletter2float(raw_avg_ST.strip())

        # 全国勝率
        raw_all_1rate, raw_all_2rate, raw_all_3rate = \
            self._box_to_three_element(target_tbody_xpath, column_no=5)
        all_1rate = super()._rmletter2float(raw_all_1rate.strip())
        all_2rate = super()._rmletter2float(raw_all_2rate.strip())
        all_3rate = super()._rmletter2float(raw_all_3rate.strip())

        # 当地勝率
        raw_local_1rate, raw_local_2rate, raw_local_3rate = \
            self._box_to_three_element(target_tbody_xpath, column_no=6)
        local_1rate = super()._rmletter2float(raw_local_1rate.strip())
        local_2rate = super()._rmletter2float(raw_local_2rate.strip())
        local_3rate = super()._rmletter2float(raw_local_3rate.strip())

        # モーター情報は7番目
        raw_motor_no, raw_motor_2rate, raw_motor_3rate = \
            self._box_to_three_element(target_tbody_xpath, column_no=7)
        motor_no = super()._rmletter2int(raw_motor_no.strip())
        motor_2rate = super()._rmletter2float(raw_motor_2rate.strip())
        motor_3rate = super()._rmletter2float(raw_motor_3rate.strip())

        # ボート情報は8番目
        raw_boat_no, raw_boat_2rate, raw_boat_3rate = \
            self._box_to_three_element(target_tbody_xpath, column_no=8)
        boat_no = super()._rmletter2int(raw_boat_no.strip())
        boat_2rate = super()._rmletter2float(raw_boat_2rate.strip())
        boat_3rate = super()._rmletter2float(raw_boat_3rate.strip())

        self.logger.debug('get target player info completed.')

        content_dict = {
            'name': player_name,
            'id': player_id,
            'level': player_level,
            'home': home,
            'birth_place': birth_place,
            'age': age,
            'weight': weight,
            'num_F': num_F,
            'num_L': num_L,
            'avg_ST': avg_ST,
            'all_1rate': all_1rate,
            'all_2rate': all_2rate,
            'all_3rate': all_3rate,
            'local_1rate': local_1rate,
            'local_2rate': local_2rate,
            'local_3rate': local_3rate,
            'motor_no': motor_no,
            'motor_2rate': motor_2rate,
            'motor_3rate': motor_3rate,
            'boat_no': boat_no,
            'boat_2rate': boat_2rate,
            'boat_3rate': boat_3rate
        }

        return content_dict

    def getcommoninfo2dict(self) -> dict:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        target_table_xpath = "/html/body/main/div/div/div/div[1]/div/div[2]"

        # SG, G1, G2, G3 一般
        raw_grade = \
            self.__lx_content.xpath(target_table_xpath)[0].attrib["class"]
        grade = raw_grade.split()[1].strip()

        # 大会名
        taikai_xpath = "/".join([target_table_xpath, "h2"])
        taikai_name = self.__lx_content.xpath(taikai_xpath)[0].text
        taikai_name = super()._getonlyzenkaku2str(taikai_name)

        # race_type : 予選 優勝戦など/レース距離
        race_type_xpath = "/".join([target_table_xpath, "span"])
        race_str = self.__lx_content.xpath(race_type_xpath)[0].text
        race_list = re.sub("[\u3000\t]", "", race_str).split("\n")
        race_type, race_kyori = list(filter(lambda x: x != "", race_list))
        race_type = super()._getonlyzenkaku2str(race_type)
        race_kyori = super()._rmletter2int(race_kyori)

        # 安定版or進入固定の有無
        antei_shinyu_xpath = "/".join([target_table_xpath, "/div/span"])
        antei_shinyu_el_list = self.__lx_content.xpath(antei_shinyu_xpath)
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

        content_dict = {
            'taikai_name': taikai_name,
            'grade': grade,
            'race_type': race_type,
            'race_kyori': race_kyori,
            'is_antei': is_antei,
            'is_shinnyukotei': is_shinnyukotei
        }

        return content_dict

    def _box_to_three_element(self, root_xpath: str, column_no: int) -> list:
        el_list = []
        for i in range(1, 4):
            target_xpath = "/".join([root_xpath,
                                     f"tr[1]/td[{column_no}]/text()[{i}]"])
            el_list.append(self.__lx_content.xpath(target_xpath)[0])
        return el_list


class OfficialChokuzen(CommonMethods4Official):

    def __init__(self,
                 race_no: int,
                 jyo_code: int,
                 date: int) -> None:
        """
        競艇公式サイトの直前情報からのデータ取得
        レース番，場コード，日付を入力し公式サイトへアクセス

        Parameters
        ----------
        race_no : int
            何レース目か
        jyo_code : int
            会場コード
        date : int
            yyyymmdd形式で入力

        """
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        # htmlをload
        base_url = 'https://boatrace.jp/owpc/pc/race/beforeinfo?'
        target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={date}'
        self.__lx_content = super()._url2lxml(target_url)

    def getplayerinfo2dict(self, waku: int) -> dict:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 選手直前情報を選択 css selectorより
        target_p_table_xpath = f"/html/body/main/div/div/div/div[2]/div[4]"\
                               f"/div[1]/div[1]/table/tbody[{waku}]"

        # 名前
        p_name_xpath = "/".join([target_p_table_xpath, "tr[1]/td[3]/a"])
        name = self.__lx_content.xpath(p_name_xpath)[0].text
        name = name.replace('\u3000', '')

        # 体重
        p_weight_xpath = "/".join([target_p_table_xpath, "tr[1]/td[4]"])
        weight = self.__lx_content.xpath(p_weight_xpath)[0].text
        weight = super()._rmletter2float(weight)

        # 調整体重
        p_chosei_xpath = "/".join([target_p_table_xpath, "tr[3]/td[1]"])
        chosei_weight = self.__lx_content.xpath(p_chosei_xpath)[0].text
        chosei_weight = super()._rmletter2float(chosei_weight)

        # 展示タイムは5番目td (調整体重の方じゃないので注意)
        p_tenji_xpath = "/".join([target_p_table_xpath, "tr[1]/td[5]"])
        tenji_T = self.__lx_content.xpath(p_tenji_xpath)[0].text
        tenji_T = super()._rmletter2float(tenji_T)

        # チルトは6番目
        p_tilt_xpath = "/".join([target_p_table_xpath, "tr[1]/td[6]"])
        tilt = self.__lx_content.xpath(p_tilt_xpath)[0].text
        tilt = super()._rmletter2float(tilt)

        # スタート展示テーブルの選択
        target_ST_tbody = "/html/body/main/div/div/div/div[2]/"\
                          "div[4]/div[2]/div[1]/table/tbody"
        tenji_C, tenji_ST = super()._getSTtable2tuple(
            self.__lx_content,
            target_ST_tbody,
            waku
        )

        content_dict = {
            'name': name,
            'weight': weight,
            'chosei_weight': chosei_weight,
            'tenji_time': tenji_T,
            'tilt': tilt,
            'tenji_course': tenji_C,
            'tenji_st': tenji_ST
        }
        return content_dict

    def getcommoninfo2dict(self) -> dict:
        """
        直前情報の水面気象情報を抜き出し，辞書型にする
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        table_xpath = \
            "/html/body/main/div/div/div/div[2]"\
            "/div[4]/div[2]/div[2]/div[1]"
        content_dict = super()._getweatherinfo2dict(
            lx_content=self.__lx_content,
            table_xpath=table_xpath
        )

        return content_dict


class OfficialResults(CommonMethods4Official):
    def __init__(self,
                 race_no: int,
                 jyo_code: int,
                 date: int):
        """
        競艇公式サイトの結果からのデータ取得
        レース番，場コード，日付を入力し公式サイトへアクセス

        Parameters
        ----------
            race_no : int
                何レース目か
            jyo_code : int
                会場コード
            date : int
                yyyymmdd形式で入力

        """
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        # htmlをload
        base_url = 'http://boatrace.jp/owpc/pc/race/raceresult?'
        target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={date}'
        self.__lx_content = super()._url2lxml(target_url)
        # 結果テーブルだけ最初に抜く
        # xpathのインデックスで枠を取るより、最初に全部格納したほうがいい
        self.waku_dict = self._getresulttable2dict()

    def getplayerinfo2dict(self, waku: int) -> dict:
        """
        枠drivenでdictを作成する（サイトは順位drivenなのに注意)

        Parameters
        ----------
            waku : int
                枠

        Returns
        -------
            racerls : dict
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 結果テーブルのキーを選択 1~6
        content_dict = self.waku_dict[waku]

        # # 結果STテーブルの情報を取得
        tbody_xpath = \
            "/html/body/main/div/div/div/div[2]/div[4]/div[2]/div/table/tbody"
        course, st_time = super()._getSTtable2tuple(
            lx_content=self.__lx_content,
            tbody_xpath=tbody_xpath,
            waku=waku,
            table_type="result")
        content_dict['course'] = course
        content_dict['st_time'] = st_time

        return content_dict

    def getcommoninfo2dict(self) -> dict:
        """
        水面気象情報と決まり手，返還挺の有無などの選手以外のレース結果情報
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 水面気象情報の取得
        table_xpath = \
            "/html/body/main/div/div/div/div[2]"\
            "/div[5]/div[2]/div[1]/div[1]/div/div[1]"
        content_dict = \
            super()._getweatherinfo2dict(
                lx_content=self.__lx_content,
                table_xpath=table_xpath
            )

        # 返還テーブルを抜く
        # 返還挺はリストのまま辞書に入れる
        # 返還艇がなければ空リスト
        table_xpath = \
            "/html/body/main/div/div/div/div[2]"\
            "/div[5]/div[2]/div[1]/div[2]/div[1]"\
            "/table/tbody/tr/td/div/div/span"
        henkantei_list = self.__lx_content.xpath(table_xpath)

        # 返還艇をint型に直す，変なやつはNoneでハンドル（ないと思う）
        def teistr2str(tei_str):
            tei = re.search(r'[1-6]', tei_str)
            if tei is not None:
                return str(tei.group(0))
            else:
                return None

        henkantei_list = list(map(lambda x: teistr2str(x.text), henkantei_list))

        # 返還艇があればリスト長が1以上になる
        if len(henkantei_list) > 0:
            is_henkan = True
        else:
            is_henkan = False
        henkantei_str = ','.join(henkantei_list)
        content_dict['henkantei_list'] = henkantei_str
        content_dict['is_henkan'] = is_henkan

        # 決まりて
        table_xpath = "/html/body/main/div/div/div/div[2]/div[5]"\
                      "/div[2]/div[1]/div[2]/div[2]/table/tbody/tr/td"
        kimarite = self.__lx_content.xpath(table_xpath)[0].text.strip()
        content_dict['kimarite'] = kimarite

        # 備考
        table_xpath = "/html/body/main/div/div/div/div[2]/div[5]"\
                      "/div[2]/div[2]/table/tbody/tr/td"
        biko = self.__lx_content.xpath(table_xpath)[0].text.strip()
        content_dict['biko'] = biko

        # 払い戻し
        table_xpath = "/html/body/main/div/div/div/div[2]"\
                      "/div[5]/div[1]/div/table/tbody/tr[1]/td[3]/span"
        pay_contents = self.__lx_content.xpath(table_xpath)
        pay_list = list(map(lambda x: int(re.sub(r"[^\d]", "", x.text)),
                            pay_contents))
        content_dict['payout_3tan'] = pay_list[0]
        content_dict['payout_3fuku'] = pay_list[1]
        content_dict['payout_2tan'] = pay_list[2]
        content_dict['payout_2fuku'] = pay_list[3]
        content_dict['payout_1tan'] = pay_list[5]

        # 人気
        table_xpath = "/html/body/main/div/div/div/div[2]"\
                      "/div[5]/div[1]/div/table/tbody/tr[1]/td[4]"
        popular_contents = self.__lx_content.xpath(table_xpath)
        popular_list = list(map(lambda x: x.text.strip(),
                                popular_contents))
        content_dict['popular_3tan'] = super()._rmletter2int(popular_list[0])
        content_dict['popular_3fuku'] = super()._rmletter2int(popular_list[1])
        content_dict['popular_2tan'] = super()._rmletter2int(popular_list[2])
        content_dict['popular_2fuku'] = super()._rmletter2int(popular_list[3])

        return content_dict

    def _getresulttable2dict(self) -> dict:
        """
        結果テーブルをまとめてdict作成
        initで呼びだし，テーブル抜きを1回で済ませる

        Returns
        -------
            waku_dict : dict
                枠をキーとしてテーブル情報を抜く
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        target_table_xpath = \
            "/html/body/main/div/div/div/div[2]/div[4]/div[1]/div/table/tbody"
        rank_xpath = "/".join([target_table_xpath, "/tr/td[1]"])
        rank_el_list = self.__lx_content.xpath(rank_xpath)
        rank_list = list(map(
            lambda x: int(x.text) if x.text.isdecimal() else -1,
            rank_el_list))

        waku_xpath = "/".join([target_table_xpath, "/tr/td[2]"])
        waku_el_list = self.__lx_content.xpath(waku_xpath)
        waku_list = list(map(
            lambda x: int(x.text) if x.text.isdecimal() else -1,
            waku_el_list))

        name_xpath = "/".join([target_table_xpath, "/tr/td[3]/span[2]"])
        name_el_list = self.__lx_content.xpath(name_xpath)
        name_list = list(map(
            lambda x: x.text.replace('\u3000', '').strip(),
            name_el_list))

        reg_no_xpath = "/".join([target_table_xpath, "/tr/td[3]/span[1]"])
        reg_el_list = self.__lx_content.xpath(reg_no_xpath)
        reg_no_list = list(map(
            lambda x: int(x.text) if x.text.isdecimal() else -1,
            reg_el_list))

        racetime_xpath = "/".join([target_table_xpath, "/tr/td[4]"])
        racetime_el_list = self.__lx_content.xpath(racetime_xpath)
        racetime_list = list(map(
            lambda x: self._racetime_str_to_sec(x.text),
            racetime_el_list))

        waku_dict = {}
        for i, waku in enumerate(waku_list):
            waku_dict[waku] = {
                'rank': rank_list[i],
                'name': name_list[i],
                'no': reg_no_list[i],
                'racetime': racetime_list[i]
            }
        return waku_dict

    def _racetime_str_to_sec(self, str_racetime) -> float:

        # レースタイムは秒に変換する
        try:
            t = datetime.strptime(str_racetime, '%M\'%S"%f')
            delta = timedelta(
                seconds=t.second,
                microseconds=t.microsecond,
                minutes=t.minute,
            )
            racetime_sec = delta.total_seconds()
        except ValueError:
            racetime_sec = -1

        return racetime_sec


class OfficialOdds(CommonMethods4Official):
    def __init__(self,
                 date: int,
                 jyo_code: int,
                 race_no: int,):

        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        # 賭け方によりURLが違うので，関数ごとでURLを設定する
        self.race_no = race_no
        self.jyo_code = jyo_code
        self.date = date

    def _tanfuku_common(self, num: int, kake: str) -> list:
        """
        # 2 3連単，3連複共通部分を関数化

        Parameters
        ---------
            num: int
                2 or 3
            kake : str
                rentan or renfuku

        Returns
        -------
            odds_matrix : list
                oddsのリスト（htmlのテーブルと同配列）
                要素は少数型
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        assert kake in ['rentan', 'renfuku']
        assert num in [2, 3]
        # num = 2ならtypeによらずtype='tf'
        if num == 2:
            html_type = 'tf'
        elif kake == 'rentan':
            html_type = 't'
        elif kake == 'renfuku':
            html_type = 'f'
        else:
            html_type = 'tf'

        # htmlをload
        base_url = f'https://boatrace.jp/owpc/pc/race/'\
                   f'odds{num}{html_type}?'
        target_url = f'{base_url}rno={self.race_no}&' \
                     f'jcd={self.jyo_code:02}&hd={self.date}'
        lx_content = super()._url2lxml(target_url)
        # 3連単と共通--------------------
        # oddsテーブルの抜き出し
        if num == 2 and kake == 'renfuku':
            table_xpath = \
                'body > main > div > div > div > '\
                'div.contentsFrame1_inner > div:nth-child(8) '\
                '> table > tbody'
        else:
            table_xpath = \
                "/html/body/main/div/div/div/div[2]/div[6]/table/tbody"

        # 横優先のoddsリスト
        odds_el = lx_content.xpath("/".join([
            table_xpath, "tr/td[contains(@class, 'oddsPoint')]"]))
        odds_horizontals = list(map(
            lambda x: self._check_ketsujyo(x.text), odds_el))

        return odds_horizontals

#     # oddsPointクラスを抜き，要素を少数に変換してリストで返す
#     def _getoddsPoint2floatlist(self, odds_tr):
#         html_list = odds_tr.select('td.oddsPoint')
#         text_list = list(map(lambda x: x.text, html_list))
#         float_list = list(map(
#             lambda x: self._check_ketsujyo(x), text_list))
#         return float_list

    # 欠場をチェックする
    def _check_ketsujyo(self, float_str: str):
        try:
            return float(float_str)
        except ValueError:
            return -9999.0

    def _rentan_list(self, odds_holizontals: list) -> list:
        """
        2 3連単用処理
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # numpy array化
        num_rows = len(odds_holizontals) // 6
        odds_matrix = np.array(odds_holizontals).reshape(num_rows, 6)
        # 転置を取り，つなげてリスト化
        odds_list = list(odds_matrix.T.reshape(-1))
        return odds_list

#     def _renfuku_matrix2list(self, odds_matrix: list) -> list:
#         """
#         連複用処理
#         """
#         self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
#         # 1番目の要素から抜いていく -1で空を保管し，filterで除く
#         odds_list = []
#         # 最後のリストが空になるまで回す
#         # 要素があれば条件式は真
#         while odds_matrix[-1]:
#             odds_list += list(map(
#                 lambda x: x.pop(0) if len(x) != 0 else -1,
#                 odds_matrix))
#         odds_list = list(filter(lambda x: x != -1, odds_list))
#         return odds_list

    @classmethod
    def rentan_keylist(cls, rank: int) -> list:
        """連単用キーのリストを返す.

        Parameters
        ----------
            rank : int
                1 or 2 or 3 で単勝，2連単，3連単
        """
        rentan_key_list = []
        for fst in range(1, 7):
            if rank == 1:
                rentan_key_list.append(f'{fst}')
            else:
                for snd in range(1, 7):
                    if snd != fst and rank == 2:
                        rentan_key_list.append(f'{fst}-{snd}')
                    else:
                        for trd in range(1, 7):
                            if fst != snd and fst != trd and snd != trd:
                                rentan_key_list.append(f'{fst}-{snd}-{trd}')
        return rentan_key_list

    @classmethod
    def renfuku_keylist(cls, rank: int) -> list:
        renfuku_key_list = []
        if rank == 2:
            for fst in range(1, 6):
                for snd in range(fst+1, 7):
                    renfuku_key_list.append(f'{fst}-{snd}')
            return renfuku_key_list
        elif rank == 3:
            for fst in range(1, 5):
                for snd in range(fst+1, 6):
                    for trd in range(snd+1, 7):
                        renfuku_key_list.append(f'{fst}-{snd}-{trd}')
            return renfuku_key_list

    # 3連単を集計
    def three_rentan(self) -> dict:
        """
        3連単オッズを抜き出し辞書型で返す
        1-2-3のオッズは return_dict[1][2][3]に格納される
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 連単・連複の共通メソッドを使ってoddsテーブルを抜く
        odds_horizontal = self._tanfuku_common(3, 'rentan')
        odds_list = self._rentan_list(odds_horizontal)

        # 辞書で格納する
        content_dict = {}
        for key_name in self.rentan_keylist(3):
            content_dict[key_name] = odds_list.pop(0)

        return content_dict

#     # 3連複を集計
#     def three_renfuku(self) -> dict:
#         """
#         3連複オッズを抜き出し辞書型で返す
#         1=2=3のオッズは return_dict[1][2][3]に格納される
#         """
#         self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
#         # 連単・連複の共通メソッドを使ってoddsテーブルを抜く
#         odds_matrix = self._tanfuku_common(3, 'renfuku')
#         odds_list = self._renfuku_matrix2list(odds_matrix)
#         # 辞書で格納する
#         content_dict = {}
#         for key_name in self.renfuku_keylist(3):
#             content_dict[key_name] = odds_list.pop(0)

#         return content_dict

    # 2連単を集計
    def two_rentan(self):
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 共通メソッドを使える
        odds_hol_list = self._tanfuku_common(2, 'rentan')
        odds_list = self._rentan_list(odds_hol_list)

        # 辞書で格納する
        content_dict = {}
        for key_name in self.rentan_keylist(2):
            content_dict[key_name] = odds_list.pop(0)
        return content_dict

#     # 2連複を集計
#     def two_renfuku(self):
#         self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
#         odds_matrix = self._tanfuku_common(2, 'renfuku')
#         odds_list = self._renfuku_matrix2list(odds_matrix)
#         # 辞書で格納する
#         content_dict = {}
#         for key_name in self.renfuku_keylist(rank=2):
#             content_dict[key_name] = odds_list.pop(0)
#         return content_dict

#     # 単勝
#     def tansho(self):
#         self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
#         # htmlをload
#         base_url = 'https://boatrace.jp/owpc/pc/race/'\
#                    'oddstf?'
#         target_url = f'{base_url}rno={self.race_no}&' \
#                      f'jcd={self.jyo_code:02}&hd={self.date}'
#         soup = super()._url2lxml(target_url)
#         target_table_selector = \
#             'body > main > div > div > div > '\
#             'div.contentsFrame1_inner > div.grid.is-type2.h-clear '\
#             '> div:nth-child(1) > div.table1 > table'
#         odds_table = soup.select_one(target_table_selector)
#         odds_html_list = odds_table.select('tbody tr td.oddsPoint')
#         odds_list = list(
#             map(lambda x: self._check_ketsujyo(x.text), odds_html_list))

#         content_dict = {}
#         for key_name in self.rentan_keylist(1):
#             content_dict[key_name] = odds_list.pop(0)

#         return content_dict


class DateRange:
    """
    ある日付からある日付までのyyyymmdd型の日付リストを返す
    """
    @classmethod
    def daterange(cls,
                  st_date: datetime,
                  ed_date: datetime) -> Iterator:
        """
        開始日から終了日までの日付のイテレータ

        Parameters
        ----------
            st_date: datetime
                開始日
            ed_date: datetime
                終了日
        """

        # +1することでeddateも含める
        for n in range((ed_date - st_date).days + 1):
            itr_date = st_date + timedelta(n)
            itr_date_int = int(itr_date.strftime('%Y%m%d'))
            yield itr_date_int
