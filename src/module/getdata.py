# python 3.7.5
# coding: utf-8
# from module import const
import unittest
from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup as bs
import re


class OfficialProgram:
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
        __target_url = f'{base_url}rno={race_no}&jcd={jyo_code:02}&hd={day}'
        __html_content = urlopen(__target_url).read()
        __soup = bs(__html_content, 'html.parser')
        # 番組表を選択 css selectorより
        __target_table_selector = \
            'body > main > div > div > '\
            'div > div.contentsFrame1_inner > '\
            'div.table1.is-tableFixed__3rdadd > table'
        self.__target_table_html = __soup.select_one(__target_table_selector)

    def getplayerinfo2dict(self, row: int) -> dict:
        # 各選手の行を選択 -> list
        player_info_html_list = self.__target_table_html.select('tbody')
        assert len(player_info_html_list) == 6, \
            f"lengh is not 6:{len(player_info_html_list)}"
        # row は1からなので-1
        __player_html = player_info_html_list[row - 1]
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
        weight = re.match(r'[0-9]+\.[0-9]', weight)
        weight = float(weight.group(0))

        # F/L/ST平均は4番目
        __flst = __player_info_list[3]
        __flst_list = self.__text2list_rn_split(__flst, 3)
        # 数字のみ抜き出してキャスト
        num_F = int(re.sub(r'[a-z, A-Z]', '', __flst_list[0]))
        num_L = int(re.sub(r'[a-z, A-Z]', '', __flst_list[1]))
        avg_ST = float(re.sub(r'[a-z, A-Z]', '', __flst_list[2]))

        # 全国勝率・連対率は5番目
        __all_123_rate = __player_info_list[4]
        __all_123_list = self.__text2list_rn_split(__all_123_rate, 3)
        all_1rate, all_2rate, all_3rate = \
            list(map(lambda x: float(x), __all_123_list))

        # 当地勝率・連対率は6番目
        __local_123_rate = __player_info_list[5]
        __local_123_list = self.__text2list_rn_split(__local_123_rate, 3)
        local_1rate, local_2rate, local_3rate = \
            list(map(lambda x: float(x), __local_123_list))

        # モーター情報は7番目
        __motor_info = __player_info_list[6]
        __motor_info_list = self.__text2list_rn_split(__motor_info, 3)
        motor_no = int(__motor_info_list[0])
        motor_2rate = float(__motor_info_list[1])
        motor_3rate = float(__motor_info_list[2])

        # ボート情報は8番目
        __boat_info = __player_info_list[7]
        __boat_info_list = self.__text2list_rn_split(__boat_info, 3)
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

    def __text2list_rn_split(self,
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


class GetDataTest(unittest.TestCase):
    '''
    http://boatrace.jp/owpc/pc/race/racelist?rno=3&jcd=06&hd=20200408 \n
    番組表
    '''

    # 選手情報の取得
    def test_getplayer_info(self):
        # 3R
        self.race_no = 3
        # place : hamanako 06
        self.jyo_code = 6
        # day 2020/04/08
        self.day = 20200408

        op = OfficialProgram(self.race_no, self.jyo_code, self.day)
        # 1列目
        player_info1 = op.getplayerinfo2dict(row=1)
        # 2列目
        player_info2 = op.getplayerinfo2dict(row=2)

        def __test_content(ans1, ans2, key):
            """
            2行テストする

            Parameters
            ----------
                ans1: 1行目の答え
                ans2: 2行目の答え
                key: dictのkey
            """
            with self.subTest(info=f'row1 {key}'):
                data1 = player_info1[f'{key}']
                self.assertEqual(ans1, data1)
            with self.subTest(info=f'row2 {key}'):
                data2 = player_info2[f'{key}']
                self.assertEqual(ans2, data2)

        # name
        __test_content("鈴木裕隆", "小林晋", 'name')
        # 登録番号
        __test_content(4231, 4026, 'id')
        # 級
        __test_content('B1', 'B1', 'level')
        # 支部
        __test_content('愛知', '東京', 'home')
        # 出身地
        __test_content('愛知', '東京', 'birth_place')
        # 年齢
        __test_content(36, 42, 'age')
        # 体重
        __test_content(57.0, 53.9, 'weight')
        # F数
        __test_content(0, 0, 'num_F')
        # L数
        __test_content(0, 0, 'num_L')
        # 平均ST
        __test_content(0.21, 0.20, 'avg_ST')
        # 全国勝率
        __test_content(4.81, 4.24, 'all_1rate')
        # 全国2率
        __test_content(29.47, 20.34, 'all_2rate')
        # 全国3率
        __test_content(46.32, 32.20, 'all_3rate')
        # 当地勝率
        __test_content(5.00, 4.04, 'local_1rate')
        # 当地2率
        __test_content(33.33, 17.39, 'local_2rate')
        # 当地3率
        __test_content(60.00, 34.78, 'local_3rate')
        # モーターNo
        __test_content(23, 21, 'motor_no')
        # モーター2率
        __test_content(54.66, 27.00, 'motor_2rate')
        # モーター3率
        __test_content(72.46, 46.84, 'motor_3rate')
        # ボートNo
        __test_content(34, 73, 'boat_no')
        # ボート率
        __test_content(15.05, 32.32, 'boat_2rate')
        # ボート3率
        __test_content(33.33, 52.53, 'boat_3rate')

    # 直前情報の取得
    def test_chokuzen_info(self):
        # 3R
        self.race_no = 3
        # place : hamanako 06
        self.jyo_code = 6
        # day 2020/04/08
        self.day = 20200408


if __name__ == '__main__':
    unittest.main()
