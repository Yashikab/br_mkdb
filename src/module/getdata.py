# python 3.7.5
# coding: utf-8
"""
HTMLから情報をスクレイピングするためのモジュール
"""
from dataclasses import asdict
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
import numpy as np
import pandas as pd

from domain import const
from domain.model.info import ProgramPlayerInfo


class CommonMethods4Official:
    def __init__(self):
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)

    def _url2soup(self, url):
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

        soup = bs(html_content, 'lxml')

        return soup

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
                          soup: bs4.BeautifulSoup,
                          table_selector: str,
                          waku: int) -> tuple:
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

        Returns
        -------
            course st_time : tuple
                対象枠のコースとSTタイムをタプルで返す
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        target_table_html = soup.select_one(table_selector)
        st_html = target_table_html.select_one('tbody')
        st_html_list = st_html.select('tr > td')
        # 欠場挺があると6挺にならないときがあるので、assertをつかわない
        if len(st_html_list) < 6:
            self.logger.warning("there are less than 6 boats.")
        # コース抜き出し
        # コースがキーで，号がvalueなので全て抜き出してから逆にする
        waku_list = list(
            map(lambda x: int(x.select('div > span')[0].text),
                st_html_list))
        # 0~5のインデックスなので1~6へ変換のため+1
        course_idx = waku_list.index(waku)
        course = course_idx + 1

        # 展示ST抜き出し
        st_time_list = list(
            map(lambda x: x.select('div > span')[2].text,
                st_html_list))
        # Fをマイナスに変換し，少数化
        # listのキーはコースであることに注意
        st_time = st_time_list[course_idx]
        st_time = self._rmletter2float(st_time.replace('F', '-'))
        return (course, st_time)

    def _getweatherinfo2dict(self,
                             soup: bs4.BeautifulSoup,
                             table_selector: str) -> dict:
        """
        水面気象情報テーブルのスクレイパー

        Parameters
        ----------
            soup : bs4.BeautifulSoup
            table_selector : str

        Returns
        -------
            content_dict : dict
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        target_table_html = soup.select_one(table_selector)
        condinfo_html_list = target_table_html.select('div')
        assert len(condinfo_html_list) == 12, \
            f"{self.__class__.__name__}: "\
            f"lengh is not 12:{len(condinfo_html_list)}"
        # 気温は2番目のdiv
        tmp_info_html = condinfo_html_list[1]
        # spanで情報がとれる (1番目： '気温', 2番目: 数字℃)
        tmp_info = tmp_info_html.select('span')
        temp = tmp_info[1].text
        temp = self._rmletter2float(temp)
        # 天気は2番目のdiv
        weather_info_html = condinfo_html_list[2]
        # spanのなか（1個しかない)
        weather = weather_info_html.select_one('span').text
        weather = weather.replace('\n', '')\
                         .replace('\r', '')\
                         .replace(' ', '')
        # 風速は5番目のdiv
        wind_v = self._choose_2nd_span(condinfo_html_list[4])
        wind_v: int = self._rmletter2int(wind_v)

        # 水温は8番目のdiv
        w_temp = self._choose_2nd_span(condinfo_html_list[7])
        w_temp = self._rmletter2float(w_temp)

        # 波高は10番目のdiv
        wave = self._choose_2nd_span(condinfo_html_list[9])
        wave = self._rmletter2int(wave)

        # 風向きは7番目のdiv
        # 画像のみの情報なので，16方位の数字（画像の名前）を抜く
        # p中のクラス名2番目にある
        wind_dr = condinfo_html_list[6].select_one('p')['class'][1]
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
        in_str = re.search(r'-{0,1}[0-9]+', in_str)
        if in_str is not None:
            out_int = int(in_str.group(0))
        else:
            out_int = None
        return out_int

    def _getonlyzenkaku2str(self, in_str: str) -> str:
        try:
            # 全角の抽出
            return re.search(r'[^\x01-\x7E]+', in_str).group(0)
        except ValueError:
            return None


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
        self.__soup = super()._url2soup(target_url)
        self.logger.debug('get html completed.')

    def getplayerinfo2dict(self, waku: int) -> dict:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 番組表を選択 css selectorより
        self.logger.debug('get table html from target url')
        target_table_selector = \
            'body > main > div > div > '\
            'div > div.contentsFrame1_inner > '\
            'div.table1.is-tableFixed__3rdadd > table'
        player_info_html_list = \
            super()._getplayertable2list(
                self.__soup,
                target_table_selector
            )
        self.logger.debug('get table html completed.')

        # waku は1からなので-1
        self.logger.debug(f'get target player info (waku : {waku})')
        player_html = player_info_html_list[waku - 1]
        # 選手情報は1番目のtr
        player_info = player_html.select_one("tr")
        player_info_list = player_info.select("td")

        # 名前，登録番号などの欄は3番目
        player_name_list = player_info_list[2].select("div")
        assert len(player_name_list) == 3, \
            f'elements of player name info is not 3: {len(player_name_list)}'
        # list 登録番号・級，名前，出身・年齢，体重
        player_no_level, name, place_age_weight = \
            list(map(lambda elements: elements.text, player_name_list))
        # 名前の取り出し
        name = name.replace('\n', '').replace('\u3000', '')
        player_id, player_level = player_no_level.replace('\r', '')\
                                                 .replace('\n', '')\
                                                 .replace(' ', '')\
                                                 .split('/')
        # 登録番号の取り出し
        player_id = int(player_id)

        # 出身地, 年齢, 体重の取り出し
        place, age_weight = place_age_weight.replace(' ', '')\
                                            .replace('\r', '')\
                                            .split('\n')[1:-1]
        # 支部：home, 出身地: birth_place
        home, birth_place = place.split('/')
        # 年齢:age，体重:weight
        age, weight = age_weight.split('/')
        # 数字だけ抜く
        age = re.match(r'[0-9]+', age)
        age = int(age.group(0))
        weight = super()._rmletter2float(weight)

        # F/L/ST平均は4番目
        flst = player_info_list[3]
        flst_list = super()._text2list_rn_split(flst, 3)
        # 数字のみ抜き出してキャスト
        # num_F = int(re.sub(r'[a-z, A-Z]', '', flst_list[0]))
        # num_L = int(re.sub(r'[a-z, A-Z]', '', flst_list[1]))
        # avg_ST = float(re.sub(r'[a-z, A-Z]', '', flst_list[2]))
        num_F = super()._rmletter2int(flst_list[0])
        num_L = super()._rmletter2int(flst_list[1])
        avg_ST = super()._rmletter2float(flst_list[2])

        # 全国勝率・連対率は5番目
        all_123_rate = player_info_list[4]
        all_123_list = super()._text2list_rn_split(all_123_rate, 3)
        all_1rate, all_2rate, all_3rate = \
            list(map(lambda x: float(x), all_123_list))

        # 当地勝率・連対率は6番目
        local_123_rate = player_info_list[5]
        local_123_list = super()._text2list_rn_split(local_123_rate, 3)
        local_1rate, local_2rate, local_3rate = \
            list(map(lambda x: float(x), local_123_list))

        # モーター情報は7番目
        motor_info = player_info_list[6]
        motor_info_list = super()._text2list_rn_split(motor_info, 3)
        motor_no = int(motor_info_list[0])
        motor_2rate = float(motor_info_list[1])
        motor_3rate = float(motor_info_list[2])

        # ボート情報は8番目
        boat_info = player_info_list[7]
        boat_info_list = super()._text2list_rn_split(boat_info, 3)
        boat_no = int(boat_info_list[0])
        boat_2rate = float(boat_info_list[1])
        boat_3rate = float(boat_info_list[2])

        self.logger.debug('get target player info completed.')

        program_p_info = ProgramPlayerInfo(
            name,
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

        return asdict(program_p_info)

    def getcommoninfo2dict(self) -> dict:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        table_selector = \
            'body > main > div > div > div > '\
            'div.heading2 > div > div.heading2_title'
        raceinfo_html = self.__soup.select_one(table_selector)
        taikai_name = raceinfo_html.select_one('h2').text

        # SG, G1, G2, G3 一般
        grade = raceinfo_html['class'][1]

        # race_type : 予選 優勝戦など
        race_str = raceinfo_html.select_one('span').text
        race_str = race_str.replace('\u3000', '')
        race_type = super()._getonlyzenkaku2str(race_str)

        # レース距離
        try:
            race_kyori = re.search(r'[0-9]+m', race_str).group(0)
            race_kyori = int(race_kyori.replace('m', ''))
        except ValueError:
            race_kyori = None

        # 安定版or進入固定の有無
        other_labels_list = raceinfo_html.select('span.label2')
        if '安定板使用' in other_labels_list:
            is_antei = True
        else:
            is_antei = False
        if '進入固定' in other_labels_list:
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
        self.__soup = super()._url2soup(target_url)

    def getplayerinfo2dict(self, waku: int) -> dict:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 選手直前情報を選択 css selectorより
        target_p_table_selector = \
            'body > main > div > div > div > div.contentsFrame1_inner > '\
            'div.grid.is-type3.h-clear > div:nth-child(1) > div.table1 > table'
        p_chokuzen_html_list = \
            super()._getplayertable2list(
                self.__soup,
                target_p_table_selector
            )

        p_html = p_chokuzen_html_list[waku - 1]
        # 選手情報は1番目のtr
        p_chokuzen = p_html.select_one("tr")
        p_chokuzen_list = p_chokuzen.select("td")

        # 名前の欄は3番目
        name = p_chokuzen_list[2].text.replace('\u3000', '')

        # 体重は4番目
        weight = p_chokuzen_list[3].text
        # 'kg'を取り除く
        weight = super()._rmletter2float(weight)
        # 調整体重だけ3番目のtr, 1番目td
        p_chokuzen4chosei = p_html.select("tr")[2]
        chosei_weight = p_chokuzen4chosei.select_one("td").text
        chosei_weight = super()._rmletter2float(chosei_weight)
        # 展示タイムは5番目td (調整体重の方じゃないので注意)
        tenji_T = p_chokuzen_list[4].text
        tenji_T = super()._rmletter2float(tenji_T)
        # チルトは6番目
        tilt = p_chokuzen_list[5].text
        tilt = super()._rmletter2float(tilt)

        # スタート展示テーブルの選択
        target_ST_table_selector = \
            'body > main > div > div > div > div.contentsFrame1_inner '\
            '> div.grid.is-type3.h-clear > div:nth-child(2) '\
            '> div.table1 > table'
        tenji_C, tenji_ST = super()._getSTtable2tuple(
            self.__soup,
            target_ST_table_selector,
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
        table_selector = \
            'body > main > div > div > div > div.contentsFrame1_inner > '\
            'div.grid.is-type3.h-clear > div:nth-child(2) > div.weather1 > '\
            'div.weather1_body'
        content_dict = super()._getweatherinfo2dict(
            soup=self.__soup,
            table_selector=table_selector
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
        self.__soup = super()._url2soup(target_url)
        # 結果テーブルだけ最初に抜く
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

        # 結果STテーブルの情報を取得
        target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > '\
            'div.grid.is-type2.h-clear.h-mt10 > '\
            'div:nth-child(2) > div > table'
        course, st_time = super()._getSTtable2tuple(
            soup=self.__soup,
            table_selector=target_table_selector,
            waku=waku)
        content_dict['course'] = course
        content_dict['st_time'] = st_time

        return content_dict

    def getcommoninfo2dict(self) -> dict:
        """
        水面気象情報と決まり手，返還挺の有無などの選手以外のレース結果情報
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 水面気象情報の取得
        table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div:nth-child(5) > '\
            'div:nth-child(2) > div.grid.is-type6.h-clear > '\
            'div:nth-child(1) > div > div.weather1_body.is-type1__3rdadd'
        content_dict = \
            super()._getweatherinfo2dict(
                soup=self.__soup,
                table_selector=table_selector
            )

        # 返還テーブルを抜く
        # 返還挺はリストのまま辞書に入れる
        # 返還艇がなければ空リスト
        table_selector = \
            'body > main > div > div > div > div.contentsFrame1_inner > '\
            'div:nth-child(5) > div:nth-child(2) > '\
            'div.grid.is-type6.h-clear > '\
            'div:nth-child(2) > div:nth-child(1) > '\
            'table > tbody > tr > td > '\
            'div > div span.numberSet1_number'
        henkantei_html_list = self.__soup.select(table_selector)

        # 返還艇をint型に直す，変なやつはNoneでハンドル（あんまりないけど）
        def teistr2str(tei_str):
            tei = re.search(r'[1-6]', tei_str)
            if tei is not None:
                return str(tei.group(0))
            else:
                return None

        # 返還艇があればリスト長が1以上になる
        if len(henkantei_html_list) != 0:
            henkantei_list = list(map(
                lambda x: teistr2str(x.text), henkantei_html_list))
            henkantei_list = [n for n in henkantei_list if n is not None]
            is_henkan = True
        else:
            henkantei_list = []
            is_henkan = False
        henkantei_str = ','.join(henkantei_list)
        content_dict['henkantei_list'] = henkantei_str
        content_dict['is_henkan'] = is_henkan

        # 決まりて
        table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div:nth-child(5) > '\
            'div:nth-child(2) > div.grid.is-type6.h-clear > '\
            'div:nth-child(2) > div:nth-child(2) > table > tbody > tr > td'
        kimarite = self.__soup.select_one(table_selector).text
        content_dict['kimarite'] = kimarite

        # 備考
        table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div:nth-child(5) > '\
            'div:nth-child(2) > div.table1 > table > tbody > tr > td'
        biko = self.__soup.select_one(table_selector).text
        biko = biko.replace('\r', '')\
                   .replace('\n', '')\
                   .replace(' ', '')\
                   .replace('\xa0', '')
        content_dict['biko'] = biko

        # 払い戻し，人気
        table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div:nth-child(5) > '\
            'div:nth-child(1) > div > table'
        pay_pop_tb = self.__soup.select_one(table_selector)
        pay_pop_tb_list = pay_pop_tb.select('tbody')
        content_dict['payout_3tan'], content_dict['popular_3tan'] = \
            self._get_paypop(pay_pop_tb_list[0])
        content_dict['payout_3fuku'], content_dict['popular_3fuku'] = \
            self._get_paypop(pay_pop_tb_list[1])
        content_dict['payout_2tan'], content_dict['popular_2tan'] = \
            self._get_paypop(pay_pop_tb_list[2])
        content_dict['payout_2fuku'], content_dict['popular_2fuku'] = \
            self._get_paypop(pay_pop_tb_list[3])
        content_dict['payout_1tan'], _ = \
            self._get_paypop(pay_pop_tb_list[5])

        return content_dict

    def _get_paypop(self, element_tag: bs4.element.Tag) -> tuple:
        """払い戻し金額と人気を取得"""
        payout = element_tag.select_one('span.is-payout1').text
        payout = int(payout.replace('¥', '').replace(',', ''))
        popular = \
            element_tag.select_one('tr:nth-child(1) > td:nth-child(4)').text
        popular = super()._rmletter2int(popular)
        return (payout, popular)

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
        target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div.grid.is-type2.h-clear.h-mt10 > '\
            'div:nth-child(1) > div > table'
        player_res_html_list = \
            super()._getplayertable2list(self.__soup, target_table_selector)
        # rank_p_html : 各順位の選手情報
        # waku_dict : 枠をキーとしテーブル内容を入れ替える
        waku_dict = {}
        for rank_p_html in player_res_html_list:
            rank, waku, name, racetime = \
                list(map(lambda x: x.text, rank_p_html.select('td')))
            # rankはF,L欠などが存在するためエラーハンドルがいる
            try:
                rank = int(rank)
            except ValueError:
                rank = -1

            # レースタイムは秒に変換する
            try:
                t = datetime.strptime(racetime, '%M\'%S"%f')
                delta = timedelta(
                    seconds=t.second,
                    microseconds=t.microsecond,
                    minutes=t.minute,
                )
                racetime_sec = delta.total_seconds()
            except ValueError:
                racetime_sec = -1

            waku = int(waku)
            name = name.replace('\u3000', '')\
                       .replace(' ', '')\
                       .replace('\r', '')
            self.logger.debug(name)
            no, name = name.split('\n')[1:-1]
            no = int(no)

            content_dict = {
                'rank': rank,
                'name': name,
                'no': no,
                'racetime': racetime_sec
            }

            waku_dict[waku] = content_dict
        return waku_dict


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
        soup = super()._url2soup(target_url)
        # 3連単と共通--------------------
        # oddsテーブルの抜き出し
        if num == 2 and kake == 'renfuku':
            target_table_selector = \
                'body > main > div > div > div > '\
                'div.contentsFrame1_inner > div:nth-child(8) '\
                '> table > tbody'
        else:
            target_table_selector = \
                'body > main > div > div > div > '\
                'div.contentsFrame1_inner > div:nth-child(6) > '\
                'table > tbody'
        odds_table = soup.select_one(target_table_selector)
        # 1行ごとのリスト
        yoko_list = odds_table.select('tr')

        odds_matrix = list(map(
            lambda x: self._getoddsPoint2floatlist(x),
            yoko_list
        ))
        return odds_matrix

    # oddsPointクラスを抜き，要素を少数に変換してリストで返す
    def _getoddsPoint2floatlist(self, odds_tr):
        html_list = odds_tr.select('td.oddsPoint')
        text_list = list(map(lambda x: x.text, html_list))
        float_list = list(map(
            lambda x: self._check_ketsujyo(x), text_list))
        return float_list

    # 欠場をチェックする
    def _check_ketsujyo(self, float_str: str):
        try:
            return float(float_str)
        except ValueError:
            return -9999.0

    def _rentan_matrix2list(self, odds_matrix: list) -> list:
        """
        2 3連単用処理
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # numpy array化
        odds_matrix = np.array(odds_matrix)
        # 転置を取り，つなげてリスト化
        odds_list = list(odds_matrix.T.reshape(-1))
        return odds_list

    def _renfuku_matrix2list(self, odds_matrix: list) -> list:
        """
        連複用処理
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 1番目の要素から抜いていく -1で空を保管し，filterで除く
        odds_list = []
        # 最後のリストが空になるまで回す
        # 要素があれば条件式は真
        while odds_matrix[-1]:
            odds_list += list(map(
                lambda x: x.pop(0) if len(x) != 0 else -1,
                odds_matrix))
        odds_list = list(filter(lambda x: x != -1, odds_list))
        return odds_list

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
        odds_matrix = self._tanfuku_common(3, 'rentan')
        odds_list = self._rentan_matrix2list(odds_matrix)

        # 辞書で格納する
        content_dict = {}
        for key_name in self.rentan_keylist(3):
            content_dict[key_name] = odds_list.pop(0)
        # for fst in range(1, 7):
        #     if fst not in content_dict.keys():
        #         content_dict[fst] = {}
        #     for snd in range(1, 7):
        #         if snd != fst:
        #             if snd not in content_dict[fst].keys():
        #                 content_dict[fst][snd] = {}
        #             for trd in range(1, 7):
        #                 if trd != fst and trd != snd:
        #                     content_dict[fst][snd][trd] = \
        #                         odds_list.pop(0)

        return content_dict

    # 3連複を集計
    def three_renfuku(self) -> dict:
        """
        3連複オッズを抜き出し辞書型で返す
        1=2=3のオッズは return_dict[1][2][3]に格納される
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 連単・連複の共通メソッドを使ってoddsテーブルを抜く
        odds_matrix = self._tanfuku_common(3, 'renfuku')
        odds_list = self._renfuku_matrix2list(odds_matrix)
        # 辞書で格納する
        content_dict = {}
        for key_name in self.renfuku_keylist(3):
            content_dict[key_name] = odds_list.pop(0)

        return content_dict

    # 2連単を集計
    def two_rentan(self):
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 共通メソッドを使える
        odds_matrix = self._tanfuku_common(2, 'rentan')
        odds_list = self._rentan_matrix2list(odds_matrix)

        # 辞書で格納する
        content_dict = {}
        for key_name in self.rentan_keylist(2):
            content_dict[key_name] = odds_list.pop(0)
        return content_dict

    # 2連複を集計
    def two_renfuku(self):
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        odds_matrix = self._tanfuku_common(2, 'renfuku')
        odds_list = self._renfuku_matrix2list(odds_matrix)
        # 辞書で格納する
        content_dict = {}
        for key_name in self.renfuku_keylist(rank=2):
            content_dict[key_name] = odds_list.pop(0)
        return content_dict

    # 単勝
    def tansho(self):
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # htmlをload
        base_url = 'https://boatrace.jp/owpc/pc/race/'\
                   'oddstf?'
        target_url = f'{base_url}rno={self.race_no}&' \
                     f'jcd={self.jyo_code:02}&hd={self.date}'
        soup = super()._url2soup(target_url)
        target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div.grid.is-type2.h-clear '\
            '> div:nth-child(1) > div.table1 > table'
        odds_table = soup.select_one(target_table_selector)
        odds_html_list = odds_table.select('tbody tr td.oddsPoint')
        odds_list = list(
            map(lambda x: self._check_ketsujyo(x.text), odds_html_list))

        content_dict = {}
        for key_name in self.rentan_keylist(1):
            content_dict[key_name] = odds_list.pop(0)

        return content_dict


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
        self.__soup = super()._url2soup(target_url)

        # 抜き出すテーブルの選択
        target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div.table1 > table'
        target_table_html = self.__soup.select_one(target_table_selector)
        tbody_list = target_table_html.select('tbody')

        self.place_name_list = \
            list(map(lambda x: self._getplacename(x), tbody_list))
        self.shinko_info_list = \
            list(map(lambda x: self._getshinkoinfo(x), tbody_list))

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

    def _getplacename(self, row_html) -> str:
        """
        行htmlから会場名を抜き出す
        """
        place_name = row_html.select_one('tr > td > a > img')['alt']
        place_name = super()._getonlyzenkaku2str(place_name)
        return place_name

    def _getshinkoinfo(self, row_html) -> str:
        """
        中止などの情報を抜き出す
        """
        return row_html.select('tr > td')[1].text


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
