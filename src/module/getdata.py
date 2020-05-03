# python 3.7.5
# coding: utf-8
"""
HTMLから情報をスクレイピングするためのモジュール
"""

from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup as bs
import re
import numpy as np
from datetime import datetime, timedelta


class CommonMethods4Official:

    def url2soup(self, url):
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
        return target_html.select('span')[1].text

    def rmletter2float(self, in_str: str) -> float:
        """
        文字列から文字を取り除き少数で返す
        マイナス表記は残す
        """
        in_str = re.search(r'-{0,1}[0-9]*\.[0-9]+', in_str)
        out_float = float(in_str.group(0))
        return out_float

    def rmletter2int(self, in_str: str) -> int:
        """
        文字列から文字を取り除き整数で返す
        マイナス表記は残す
        """
        in_str = re.search(r'-{0,1}[0-9]+', in_str)
        out_int = int(in_str.group(0))
        return out_int


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

        # htmlをload
        base_url = 'https://boatrace.jp/owpc/pc/race/racelist?'
        target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={day}'
        self.__soup = super().url2soup(target_url)

    def getplayerinfo2dict(self, waku: int) -> dict:
        # 番組表を選択 css selectorより
        __target_table_selector = \
            'body > main > div > div > '\
            'div > div.contentsFrame1_inner > '\
            'div.table1.is-tableFixed__3rdadd > table'
        __player_info_html_list = \
            super().getplayertable2list(
                self.__soup,
                __target_table_selector
            )
        # waku は1からなので-1
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
        # htmlをload
        base_url = 'https://boatrace.jp/owpc/pc/race/beforeinfo?'
        target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={day}'
        self.__soup = super().url2soup(target_url)

    def getplayerinfo2dict(self, waku: int) -> dict:
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
        table_selector = \
            'body > main > div > div > div > div.contentsFrame1_inner > '\
            'div.grid.is-type3.h-clear > div:nth-child(2) > div.weather1 > '\
            'div.weather1_body'
        __target_table_html = self.__soup.select_one(table_selector)
        condinfo_html_list = __target_table_html.select('div')
        assert len(condinfo_html_list) == 12, \
            f"lengh is not 12:{len(condinfo_html_list)}"
        # 気温は2番目のdiv
        __tmp_info_html = condinfo_html_list[1]
        # spanで情報がとれる (1番目： '気温', 2番目: 数字℃)
        __tmp_info = __tmp_info_html.select('span')
        temp = __tmp_info[1].text
        temp = super().rmletter2float(temp)
        # 天気は2番目のdiv
        __weather_info_html = condinfo_html_list[2]
        # spanのなか（1個しかない)
        weather = __weather_info_html.select_one('span').text

        # 風速は5番目のdiv
        wind_v = super().choose_2nd_span(condinfo_html_list[4])
        wind_v: int = super().rmletter2int(wind_v)

        # 水温は8番目のdiv
        w_temp = super().choose_2nd_span(condinfo_html_list[7])
        w_temp = super().rmletter2float(w_temp)

        # 波高は10番目のdiv
        wave = super().choose_2nd_span(condinfo_html_list[9])
        wave = super().rmletter2int(wave)

        # 風向きは7番目のdiv
        # 画像のみの情報なので，16方位の数字（画像の名前）を抜く
        # p中のクラス名2番目にある
        wind_dr = condinfo_html_list[6].select_one('p')['class'][1]
        wind_dr = super().rmletter2int(wind_dr)

        content_dict = {
            'temp': temp,
            'weather': weather,
            'wind_v': wind_v,
            'w_temp': w_temp,
            'wave': wave,
            'wind_dr': wind_dr
        }
        return content_dict


class OfficialOdds(CommonMethods4Official):
    def __init__(self,
                 race_no: int,
                 jyo_code: int,
                 day: int):
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
        # numpy array化
        odds_matrix = np.array(odds_matrix)
        # 転置を取り，つなげてリスト化
        odds_list = list(odds_matrix.T.reshape(-1))
        return odds_list

    def _renfuku_matrix2list(self, odds_matrix: list) -> list:
        """
        連複用処理
        """
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

    def _getresulttable2dict(self) -> dict:
        """
        結果テーブルをまとめてdict作成
        initで呼びだし，テーブル抜きを1回で済ませる

        Returns
        -------
            waku_dict : dict
                枠をキーとしてテーブル情報を抜く
        """
        __target_table_selector = \
            'body > main > div > div > div > '\
            'div.contentsFrame1_inner > div.grid.is-type2.h-clear.h-mt10 > '\
            'div:nth-child(1) > div > table'
        player_res_html_list = \
            super().getplayertable2list(self.__soup, __target_table_selector)
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
