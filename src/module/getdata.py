# python 3.7.5
# coding: utf-8
# from module import const
import unittest
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


class OfficialProgram:
    def __init__(self, target_url: str) -> None:
        # htmlをload
        __html_content = urlopen(target_url).read()
        __soup = BeautifulSoup(__html_content, 'html.parser')
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
        # 名前，登録番号などの欄は2番目
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

        content_dict = {
            'name': name,
            'id': player_id,
            'level': player_level,
            'home': home,
            'birth_place': birth_place,
            'age': age,
            'weight': weight,
            'num_F': None
        }

        return content_dict


class GetDataTest(unittest.TestCase):
    '''
    http://boatrace.jp/owpc/pc/race/racelist?rno=3&jcd=06&hd=20200408 \n
    番組表
    '''
    # 選手情報の取得
    def test_getplayer_info(self):
        self.sample_url = 'http://boatrace.jp/owpc/pc/race/racelist?'\
                          'rno=3&jcd=06&hd=20200408'
        op = OfficialProgram(self.sample_url)
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
        # # F数
        # __test_content(0, 0, 'num_F')


if __name__ == '__main__':
    unittest.main()
