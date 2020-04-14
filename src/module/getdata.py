# python 3.7.5
# coding: utf-8
# from module import const
import unittest
from urllib.request import urlopen
from bs4 import BeautifulSoup


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
        player_no_level, name, birthplace_age_weight = \
            list(map(lambda elements: elements.text, player_name_list))
        name = name.replace('\n', '').replace('\u3000', '')
        player_id, player_level = player_no_level.replace('\r', '')\
                                                 .replace('\n', '')\
                                                 .replace(' ', '')\
                                                 .split('/')
        player_id = int(player_id)

        content_dict = {
            'name': name,
            'id': player_id,
            'level': player_level
        }

        return content_dict


class GetDataTest(unittest.TestCase):
    '''
    http://boatrace.jp/owpc/pc/race/racelist?rno=3&jcd=06&hd=20200408 \n
    番組表
    '''
    # 選手情報-氏名の取得
    def test_getplayer_info(self):
        self.sample_url = 'http://boatrace.jp/owpc/pc/race/racelist?'\
                          'rno=3&jcd=06&hd=20200408'
        op = OfficialProgram(self.sample_url)
        # 1列目
        player_info = op.getplayerinfo2dict(row=1)
        # name
        with self.subTest(info='row1 name'):
            name = player_info['name']
            self.assertEqual("鈴木裕隆", name)
        with self.subTest(info='row1 id'):
            player_id = player_info['id']
            self.assertEqual(4231, player_id)
        with self.subTest(info='row1 level'):
            player_id = player_info['level']
            self.assertEqual('B1', player_id)

        # 2列目
        player_info = op.getplayerinfo2dict(row=2)
        with self.subTest(info='row2 name'):
            name = player_info['name']
            self.assertEqual("小林晋", name)
        with self.subTest(info='row2 id'):
            player_id = player_info['id']
            self.assertEqual(4026, player_id)
        with self.subTest(info='row2 level'):
            player_id = player_info['level']
            self.assertEqual('B1', player_id)


if __name__ == '__main__':
    unittest.main()
