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
            'weight': weight
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
        # name
        with self.subTest(info='row1 name'):
            name = player_info1['name']
            self.assertEqual("鈴木裕隆", name)
        with self.subTest(info='row2 name'):
            name = player_info2['name']
            self.assertEqual("小林晋", name)

        # 登録番号
        with self.subTest(info='row1 id'):
            player_id = player_info1['id']
            self.assertEqual(4231, player_id)
        with self.subTest(info='row2 id'):
            player_id = player_info2['id']
            self.assertEqual(4026, player_id)

        # 級
        with self.subTest(info='row1 level'):
            player_level = player_info1['level']
            self.assertEqual('B1', player_level)
        with self.subTest(info='row2 level'):
            player_level = player_info2['level']
            self.assertEqual('B1', player_level)

        # 支部
        with self.subTest(info='row1 home'):
            player_home = player_info1['home']
            self.assertEqual('愛知', player_home)
        with self.subTest(info='row2 home'):
            player_home = player_info2['home']
            self.assertEqual('東京', player_home)

        # 出身地
        with self.subTest(info='row1 birth place'):
            player_bp = player_info1['birth_place']
            self.assertEqual('愛知', player_bp)
        with self.subTest(info='row2 birth place'):
            player_bp = player_info2['birth_place']
            self.assertEqual('東京', player_bp)

        # 年齢
        with self.subTest(info='row1 age'):
            player_age = player_info1['age']
            self.assertEqual(36, player_age)
        with self.subTest(info='row2 age'):
            player_age = player_info2['age']
            self.assertEqual(42, player_age)

        # 体重
        with self.subTest(info='row1 weight'):
            player_w = player_info1['weight']
            self.assertEqual(57.0, player_w)
        with self.subTest(info='row2 weight'):
            player_w = player_info2['weight']
            self.assertEqual(53.9, player_w)


if __name__ == '__main__':
    unittest.main()
