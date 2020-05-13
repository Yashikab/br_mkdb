# python 3.7.5
# coding: utf-8
"""
HTMLから情報をスクレイピングするためのモジュール
"""

import sys

import re
from urllib.request import urlopen
from logging import getLogger
from datetime import datetime, timedelta

import bs4
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd

from module.connect import MySQL
from module import const


class CommonMethods4Official:
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def url2soup(self, url):
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        __html_content = urlopen(url).read()

        soup = bs(__html_content, 'html.parser')

        return soup

    def getplayertable2list(self,
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
        __target_table_html = soup.select_one(table_selector)
        player_html_list = __target_table_html.select('tbody')
        assert len(player_html_list) == 6, \
            f"lengh is not 6:{len(player_html_list)}"
        return player_html_list

    def getSTtable2tuple(self,
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
        __target_table_html = soup.select_one(table_selector)
        __st_html = __target_table_html.select_one('tbody')
        st_html_list = __st_html.select('tr')
        assert len(st_html_list) == 6, \
            f"lengh is not 6:{len(st_html_list)}"
        # コース抜き出し
        # コースがキーで，号がvalueなので全て抜き出してから逆にする
        __waku_list = list(
            map(lambda x: int(x.select('div > span')[0].text),
                st_html_list))
        # 0~5のインデックスなので1~6へ変換のため+1
        __C_idx = __waku_list.index(waku)
        course = __C_idx + 1

        # 展示ST抜き出し
        __st_time_list = list(
            map(lambda x: x.select('div > span')[2].text,
                st_html_list))
        # Fをマイナスに変換し，少数化
        # listのキーはコースであることに注意
        st_time = __st_time_list[__C_idx]
        st_time = self.rmletter2float(st_time.replace('F', '-'))
        return (course, st_time)

    def getweatherinfo2dict(self,
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
        __target_table_html = soup.select_one(table_selector)
        condinfo_html_list = __target_table_html.select('div')
        assert len(condinfo_html_list) == 12, \
            f"lengh is not 12:{len(condinfo_html_list)}"
        # 気温は2番目のdiv
        __tmp_info_html = condinfo_html_list[1]
        # spanで情報がとれる (1番目： '気温', 2番目: 数字℃)
        __tmp_info = __tmp_info_html.select('span')
        temp = __tmp_info[1].text
        temp = self.rmletter2float(temp)
        # 天気は2番目のdiv
        __weather_info_html = condinfo_html_list[2]
        # spanのなか（1個しかない)
        weather = __weather_info_html.select_one('span').text
        weather = weather.replace('\n', '')\
                         .replace('\r', '')\
                         .replace(' ', '')
        # 風速は5番目のdiv
        wind_v = self.choose_2nd_span(condinfo_html_list[4])
        wind_v: int = self.rmletter2int(wind_v)

        # 水温は8番目のdiv
        w_temp = self.choose_2nd_span(condinfo_html_list[7])
        w_temp = self.rmletter2float(w_temp)

        # 波高は10番目のdiv
        wave = self.choose_2nd_span(condinfo_html_list[9])
        wave = self.rmletter2int(wave)

        # 風向きは7番目のdiv
        # 画像のみの情報なので，16方位の数字（画像の名前）を抜く
        # p中のクラス名2番目にある
        wind_dr = condinfo_html_list[6].select_one('p')['class'][1]
        wind_dr = self.rmletter2int(wind_dr)

        content_dict = {
            'temp': temp,
            'weather': weather,
            'wind_v': wind_v,
            'w_temp': w_temp,
            'wave': wave,
            'wind_dr': wind_dr
        }
        return content_dict

    def text2list_rn_split(self,
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
        output_list = input_content.text.replace(' ', '')\
                                        .split('\r\n')[1:-1]
        assert len(output_list) == expect_length,\
            f"lengh is not {expect_length}:{len(output_list)}"
        return output_list

    def choose_2nd_span(self, target_html: str) -> str:
        """
        風速・水温・波高ぬきだし用関数\n
        spanの2つめの要素をstr で返却
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        return target_html.select('span')[1].text

    def rmletter2float(self, in_str: str) -> float:
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

    def rmletter2int(self, in_str: str) -> int:
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

    def getonlyzenkaku2str(self, in_str: str) -> str:
        try:
            # 全角の抽出
            return re.search(r'[^\x01-\x7E]+', in_str).group(0)
        except ValueError:
            return None


class OfficialProgram(CommonMethods4Official):
    def __init__(self,
                 race_no: int,
                 jyo_code: int,
                 day: int) -> None:
        """
        競艇公式サイトの番組表からのデータ取得
        レース番，場コード，日付を入力し公式サイトへアクセス

        Parameters
        ----------
            race_no : int
                何レース目か
            jyo_code : int
                会場コード
            day : int
                yyyymmdd形式で入力

        """
        # logger設定
        self.logger = getLogger(self.__class__.__name__)

        # htmlをload
        base_url = 'https://boatrace.jp/owpc/pc/race/racelist?'
        target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={day}'
        self.logger.info(f'get html: {target_url}')
        self.__soup = super().url2soup(target_url)
        self.logger.info('get html completed.')

    def getplayerinfo2dict(self, waku: int) -> dict:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        # 番組表を選択 css selectorより
        self.logger.debug('get table html from target url')
        __target_table_selector = \
            'body > main > div > div > '\
            'div > div.contentsFrame1_inner > '\
            'div.table1.is-tableFixed__3rdadd > table'
        __player_info_html_list = \
            super().getplayertable2list(
                self.__soup,
                __target_table_selector
            )
        self.logger.debug('get table html completed.')

        # waku は1からなので-1
        self.logger.debug(f'get target player info (waku : {waku})')
        __player_html = __player_info_html_list[waku - 1]
        # 選手情報は1番目のtr
        __player_info = __player_html.select_one("tr")
        __player_info_list = __player_info.select("td")

        # 名前，登録番号などの欄は3番目
        player_name_list = __player_info_list[2].select("div")
        assert len(player_name_list) == 3, \
            f'elements of player name info is not 3: {len(player_name_list)}'
        # list 登録番号・級，名前，出身・年齢，体重
        __player_no_level, name, __place_age_weight = \
            list(map(lambda elements: elements.text, player_name_list))
        # 名前の取り出し
        name = name.replace('\n', '').replace('\u3000', '')
        player_id, player_level = __player_no_level.replace('\r', '')\
                                                   .replace('\n', '')\
                                                   .replace(' ', '')\
                                                   .split('/')
        # 登録番号の取り出し
        player_id = int(player_id)

        # 出身地, 年齢, 体重の取り出し
        __place, __age_weight = __place_age_weight.replace(' ', '')\
                                                  .replace('\r', '')\
                                                  .split('\n')[1:-1]
        # 支部：home, 出身地: birth_place
        home, birth_place = __place.split('/')
        # 年齢:age，体重:weight
        age, weight = __age_weight.split('/')
        # 数字だけ抜く
        age = re.match(r'[0-9]+', age)
        age = int(age.group(0))
        weight = super().rmletter2float(weight)

        # F/L/ST平均は4番目
        __flst = __player_info_list[3]
        __flst_list = super().text2list_rn_split(__flst, 3)
        # 数字のみ抜き出してキャスト
        num_F = int(re.sub(r'[a-z, A-Z]', '', __flst_list[0]))
        num_L = int(re.sub(r'[a-z, A-Z]', '', __flst_list[1]))
        avg_ST = float(re.sub(r'[a-z, A-Z]', '', __flst_list[2]))

        # 全国勝率・連対率は5番目
        __all_123_rate = __player_info_list[4]
        __all_123_list = super().text2list_rn_split(__all_123_rate, 3)
        all_1rate, all_2rate, all_3rate = \
            list(map(lambda x: float(x), __all_123_list))

        # 当地勝率・連対率は6番目
        __local_123_rate = __player_info_list[5]
        __local_123_list = super().text2list_rn_split(__local_123_rate, 3)
        local_1rate, local_2rate, local_3rate = \
            list(map(lambda x: float(x), __local_123_list))

        # モーター情報は7番目
        __motor_info = __player_info_list[6]
        __motor_info_list = super().text2list_rn_split(__motor_info, 3)
        motor_no = int(__motor_info_list[0])
        motor_2rate = float(__motor_info_list[1])
        motor_3rate = float(__motor_info_list[2])

        # ボート情報は8番目
        __boat_info = __player_info_list[7]
        __boat_info_list = super().text2list_rn_split(__boat_info, 3)
        boat_no = int(__boat_info_list[0])
        boat_2rate = float(__boat_info_list[1])
        boat_3rate = float(__boat_info_list[2])

        self.logger.debug(f'get target player info completed.')

        content_dict = {
            'name': name,
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

    def raceinfo(self) -> dict:
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')
        __table_selector = \
            'body > main > div > div > div > '\
            'div.heading2 > div > div.heading2_title'
        __raceinfo_html = self.__soup.select_one(__table_selector)
        taikai_name = __raceinfo_html.select_one('h2').text

        # SG, G1, G2, G3 一般
        grade = __raceinfo_html['class'][1]

        # race_type : 予選 優勝戦など
        __race_str = __raceinfo_html.select_one('span').text
        __race_str = __race_str.replace('\u3000', '')
        race_type = super().getonlyzenkaku2str(__race_str)

        # レース距離
        try:
            race_kyori = re.search(r'[0-9]+m', __race_str).group(0)
            race_kyori = int(race_kyori.replace('m', ''))
        except ValueError:
            race_kyori = None

        # 安定版or進入固定の有無
        other_labels_list = __raceinfo_html.select('span.label2')
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
                 day: int) -> None:
        """
        競艇公式サイトの直前情報からのデータ取得
        レース番，場コード，日付を入力し公式サイトへアクセス

        Parameters
        ----------
        race_no : int
            何レース目か
        jyo_code : int
            会場コード
        day : int
            yyyymmdd形式で入力

        """
        self.logger = getLogger(self.__class__.__name__)
        # htmlをload
        base_url = 'https://boatrace.jp/owpc/pc/race/beforeinfo?'
        target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={day}'
        self.__soup = super().url2soup(target_url)

    def getplayerinfo2dict(self, waku: int) -> dict:
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # 選手直前情報を選択 css selectorより
        __target_p_table_selector = \
            'body > main > div > div > div > div.contentsFrame1_inner > '\
            'div.grid.is-type3.h-clear > div:nth-child(1) > div.table1 > table'
        __p_chokuzen_html_list = \
            super().getplayertable2list(
                self.__soup,
                __target_p_table_selector
            )

        __p_html = __p_chokuzen_html_list[waku - 1]
        # 選手情報は1番目のtr
        __p_chokuzen = __p_html.select_one("tr")
        __p_chokuzen_list = __p_chokuzen.select("td")

        # 名前の欄は3番目
        name = __p_chokuzen_list[2].text.replace('\u3000', '')

        # 体重は4番目
        weight = __p_chokuzen_list[3].text
        # 'kg'を取り除く
        weight = super().rmletter2float(weight)
        # 調整体重だけ3番目のtr, 1番目td
        __p_chokuzen4chosei = __p_html.select("tr")[2]
        chosei_weight = __p_chokuzen4chosei.select_one("td").text
        chosei_weight = super().rmletter2float(chosei_weight)
        # 展示タイムは5番目td (調整体重の方じゃないので注意)
        tenji_T = __p_chokuzen_list[4].text
        tenji_T = super().rmletter2float(tenji_T)
        # チルトは6番目
        tilt = __p_chokuzen_list[5].text
        tilt = super().rmletter2float(tilt)

        # スタート展示テーブルの選択
        __target_ST_table_selector = \
            'body > main > div > div > div > div.contentsFrame1_inner '\
            '> div.grid.is-type3.h-clear > div:nth-child(2) '\
            '> div.table1 > table'
        tenji_C, tenji_ST = super().getSTtable2tuple(
            self.__soup,
            __target_ST_table_selector,
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

    def getcondinfo2dict(self) -> dict:
        """
        直前情報の水面気象情報を抜き出し，辞書型にする
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        table_selector = \
            'body > main > div > div > div > div.contentsFrame1_inner > '\
            'div.grid.is-type3.h-clear > div:nth-child(2) > div.weather1 > '\
            'div.weather1_body'
        content_dict = super().getweatherinfo2dict(
            soup=self.__soup,
            table_selector=table_selector
        )

        return content_dict


class OfficialOdds(CommonMethods4Official):
    def __init__(self,
                 race_no: int,
                 jyo_code: int,
                 day: int):

        self.logger = getLogger(self.__class__.__name__)
        # 賭け方によりURLが違うので，関数ごとでURLを設定する
        self.race_no = race_no
        self.jyo_code = jyo_code
        self.day = day

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

        # htmlをload
        base_url = f'https://boatrace.jp/owpc/pc/race/'\
                   f'odds{num}{html_type}?'
        target_url = f'{base_url}rno={self.race_no}&' \
                     f'jcd={self.jyo_code:02}&hd={self.day}'
        __soup = super().url2soup(target_url)
        # 3連単と共通--------------------
        # oddsテーブルの抜き出し
        if num == 2 and kake == 'renfuku':
            __target_table_selector = \
                'body > main > div > div > div > '\
                'div.contentsFrame1_inner > div:nth-child(8) '\
                '> table > tbody'
        else:
            __target_table_selector = \
                'body > main > div > div > div > '\
                'div.contentsFrame1_inner > div:nth-child(6) > '\
                'table > tbody'
        odds_table = __soup.select_one(__target_table_selector)
        # 1行ごとのリスト
        yoko_list = odds_table.select('tr')

        # oddsPointクラスを抜き，要素を少数に変換してリストで返す
        def _getoddsPoint2floatlist(odds_tr):
            __html_list = odds_tr.select('td.oddsPoint')
            __text_list = list(map(lambda x: x.text, __html_list))
            float_list = list(map(
                lambda x: float(x), __text_list))
            return float_list

        odds_matrix = list(map(
            lambda x: _getoddsPoint2floatlist(x),
            yoko_list
        ))
        return odds_matrix

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

    # 3連単を集計
    def three_rentan(self) -> dict:
        """
        3連単オッズを抜き出し辞書型で返す
        1-2-3のオッズは return_dict[1][2][3]に格納される
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # 連単・連複の共通メソッドを使ってoddsテーブルを抜く
        odds_matrix = self._tanfuku_common(3, 'rentan')
        odds_list = self._rentan_matrix2list(odds_matrix)

        # 辞書で格納する
        content_dict = {}
        for fst in range(1, 7):
            if fst not in content_dict.keys():
                content_dict[fst] = {}
            for snd in range(1, 7):
                if snd != fst:
                    if snd not in content_dict[fst].keys():
                        content_dict[fst][snd] = {}
                    for trd in range(1, 7):
                        if trd != fst and trd != snd:
                            content_dict[fst][snd][trd] = \
                                odds_list.pop(0)

        return content_dict

    # 3連複を集計
    def three_renfuku(self) -> dict:
        """
        3連複オッズを抜き出し辞書型で返す
        1=2=3のオッズは return_dict[1][2][3]に格納される
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # 連単・連複の共通メソッドを使ってoddsテーブルを抜く
        odds_matrix = self._tanfuku_common(3, 'renfuku')
        odds_list = self._renfuku_matrix2list(odds_matrix)
        # 辞書で格納する
        content_dict = {}
        for fst in range(1, 5):
            if fst not in content_dict.keys():
                content_dict[fst] = {}
            for snd in range(fst+1, 6):
                if snd not in content_dict[fst].keys():
                    content_dict[fst][snd] = {}
                for trd in range(snd+1, 7):
                    content_dict[fst][snd][trd] = \
                        odds_list.pop(0)

        return content_dict

    # 2連単を集計
    def two_rentan(self):
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # 共通メソッドを使える
        odds_matrix = self._tanfuku_common(2, 'rentan')
        odds_list = self._rentan_matrix2list(odds_matrix)

        # 辞書で格納する
        content_dict = {}
        for fst in range(1, 7):
            if fst not in content_dict.keys():
                content_dict[fst] = {}
            for snd in range(1, 7):
                if snd != fst:
                    if snd not in content_dict[fst].keys():
                        content_dict[fst][snd] = odds_list.pop(0)
        return content_dict

    # 2連複を集計
    def two_renfuku(self):
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        odds_matrix = self._tanfuku_common(2, 'renfuku')
        odds_list = self._renfuku_matrix2list(odds_matrix)
        # 辞書で格納する
        content_dict = {}
        for fst in range(1, 6):
            if fst not in content_dict.keys():
                content_dict[fst] = {}
            for snd in range(fst+1, 7):
                if snd not in content_dict[fst].keys():
                    content_dict[fst][snd] = odds_list.pop(0)
        return content_dict

    # 拡連複を集計
    def kakurenfuku(self):
        pass

    # 単勝
    def tansho(self):
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # htmlをload
        base_url = f'https://boatrace.jp/owpc/pc/race/'\
                   f'oddstf?'
        target_url = f'{base_url}rno={self.race_no}&' \
                     f'jcd={self.jyo_code:02}&hd={self.day}'
        __soup = super().url2soup(target_url)
        __target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div.grid.is-type2.h-clear '\
            '> div:nth-child(1) > div.table1 > table'
        __odds_table = __soup.select_one(__target_table_selector)
        __odds_html_list = __odds_table.select('tbody tr td.oddsPoint')
        odds_list = list(map(lambda x: float(x.text), __odds_html_list))

        content_dict = {}
        for fst in range(1, 7):
            content_dict[fst] = odds_list.pop(0)

        return content_dict

    # 複勝
    def fukusho(self):
        pass


class OfficialResults(CommonMethods4Official):
    def __init__(self,
                 race_no: int,
                 jyo_code: int,
                 day: int):
        """
        競艇公式サイトの結果からのデータ取得
        レース番，場コード，日付を入力し公式サイトへアクセス

        Parameters
        ----------
            race_no : int
                何レース目か
            jyo_code : int
                会場コード
            day : int
                yyyymmdd形式で入力

        """
        self.logger = getLogger(self.__class__.__name__)
        # htmlをload
        base_url = 'http://boatrace.jp/owpc/pc/race/raceresult?'
        target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={day}'
        self.__soup = super().url2soup(target_url)
        # 結果テーブルだけ最初に抜く
        self.waku_dict = self._getresulttable2dict()

    def getplayerresult2dict(self, waku: int) -> dict:
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
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # 結果テーブルのキーを選択 1~6
        content_dict = self.waku_dict[waku]

        # 結果STテーブルの情報を取得
        __target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > '\
            'div.grid.is-type2.h-clear.h-mt10 > '\
            'div:nth-child(2) > div > table'
        course, st_time = super().getSTtable2tuple(
            soup=self.__soup,
            table_selector=__target_table_selector,
            waku=waku)
        content_dict['course'] = course
        content_dict['st_time'] = st_time

        return content_dict

    def getraceresult2dict(self) -> dict:
        """
        水面気象情報と決まり手，返還挺の有無などの選手以外のレース結果情報
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # 水面気象情報の取得
        table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div:nth-child(5) > '\
            'div:nth-child(2) > div.grid.is-type6.h-clear > '\
            'div:nth-child(1) > div > div.weather1_body.is-type1__3rdadd'
        content_dict = \
            super().getweatherinfo2dict(
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
        __henkantei_html_list = self.__soup.select(table_selector)

        # 返還艇をint型に直す，変なやつはNoneでハンドル（あんまりないけど）
        def teistr2int(tei_str):
            tei = re.search(r'[1-6]', tei_str)
            if tei is not None:
                return int(tei.group(0))
            else:
                return None

        # 返還艇があればリスト長が1以上になる
        if len(__henkantei_html_list) != 0:
            henkantei_list = list(map(
                lambda x: teistr2int(x.text), __henkantei_html_list))
            is_henkan = True
        else:
            henkantei_list = []
            is_henkan = False
        content_dict['henkantei'] = henkantei_list
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
                   .replace(' ', '')
        content_dict['biko'] = biko

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
        __target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div.grid.is-type2.h-clear.h-mt10 > '\
            'div:nth-child(1) > div > table'
        __player_res_html_list = \
            super().getplayertable2list(self.__soup, __target_table_selector)
        # rank_p_html : 各順位の選手情報
        # waku_dict : 枠をキーとしテーブル内容を入れ替える
        waku_dict = {}
        for rank_p_html in __player_res_html_list:
            rank, waku, name, racetime = \
                list(map(lambda x: x.text, rank_p_html.select('td')))
            # rankはF,L欠などが存在するためエラーハンドルがいる
            try:
                rank = int(rank)
            except ValueError:
                rank = -1

            # レースタイムは秒に変換する
            try:
                __t = datetime.strptime(racetime, '%M\'%S"%f')
                __delta = timedelta(
                    seconds=__t.second,
                    microseconds=__t.microsecond,
                    minutes=__t.minute,
                )
                racetime_sec = __delta.total_seconds()
            except ValueError:
                racetime_sec = -1

            waku = int(waku)
            name = name.replace('\n', '')\
                       .replace('\u3000', '')\
                       .replace(' ', '')
            no, name = name.split('\r')
            no = int(no)

            __content_dict = {
                'rank': rank,
                'name': name,
                'no': no,
                'racetime': racetime_sec
            }

            waku_dict[waku] = __content_dict
        return waku_dict


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
        self.logger = getLogger(self.__class__.__name__)
        # htmlをload
        base_url = 'https://www.boatrace.jp/owpc/pc/race/index?'
        target_url = f'{base_url}hd={target_date}'
        self.logger.debug(f'access: {target_url}')
        self.__soup = super().url2soup(target_url)

        # 抜き出すテーブルの選択
        __target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div.table1 > table'
        __target_table_html = self.__soup.select_one(__target_table_selector)
        __tbody_list = __target_table_html.select('tbody')

        self.place_name_list = \
            list(map(lambda x: self._getplacename(x), __tbody_list))
        self.shinko_info_list = \
            list(map(lambda x: self._getshinkoinfo(x), __tbody_list))

    def holdplace2strset(self) -> set:
        """
        会場名のままset型で返す
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        return set(self.place_name_list)

    def holdplace2cdset(self) -> set:
        """
        会場コードをset型で返す．
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        # MySQLへ接続
        self.logger.debug(f'connecting mysql server.')
        mysql = MySQL(const.MYSQL_CONFIG)
        self.logger.debug(f'done.')
        # load jyo master 場マスタのロード
        self.logger.debug(f'loading table to df.')
        sql = """
            SELECT
                *
            FROM
                jyo_master
        """
        jyo_master = pd.read_sql(sql, mysql.conn)
        self.logger.debug(f'loading table to df done.')
        # 会場名をインデックスにする
        jyo_master.set_index('jyo_name', inplace=True)
        # コードへ返還
        code_name_set = \
            set(map(
                lambda x: jyo_master.at[x, 'jyo_code'], self.place_name_list))
        return code_name_set

    def shinkoinfodict(self) -> dict:
        """
        レースの進行状況（中止など)を会場名をキーとしたdictで返す
        """
        shinkoinfo_dict = dict(
            zip(self.place_name_list, self.shinko_info_list))
        return shinkoinfo_dict

    def holdracedict(self) -> dict:
        """
        会場名をキーとして，開催されるレース番号リストを出力
        何もなければ list(range(1,13))
        中止ならば空リスト
        xR以降中止ならば[1, , x-1]
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')

        def possibleraces(msg: str) -> list:
            if re.search(r'1?[1-9]R以降中止', msg) is not None:
                end_race = int(re.search(r'1?[1-9]', msg).group(0))
                race_list = list(range(1, end_race))
            elif '中止' in msg:
                race_list = []
            else:
                race_list = list(range(1, 13))
            return race_list

        race_listoflist = list(
            map(lambda x: possibleraces(x), self.shinko_info_list))
        possiblerace_dict = dict(zip(self.place_name_list, race_listoflist))
        return possiblerace_dict

    def _getplacename(self, row_html) -> str:
        """
        行htmlから会場名を抜き出す
        """
        place_name = row_html.select_one('tr > td > a > img')['alt']
        place_name = super().getonlyzenkaku2str(place_name)
        return place_name

    def _getshinkoinfo(self, row_html) -> str:
        """
        中止などの情報を抜き出す
        """
        return row_html.select('tr > td')[1].text


class DateList:
    """
    ある日付からある日付までのyyyymmdd型の日付リストを返す
    """
    def datelist(self,
                 st_date: datetime,
                 ed_date: datetime) -> list:
        """
        開始日から終了日までの日付リストを返す

        Parameters
        ----------
            st_date: datetime
                開始日
            ed_date: datetime
                終了日
        """
        date_list = []
        # +1することでeddateも含める
        for n in range((ed_date - st_date).days + 1):
            __ap_date = st_date + timedelta(n)
            __ap_date_int = int(__ap_date.strftime('%Y%m%d'))
            date_list.append(__ap_date_int)
        return date_list
