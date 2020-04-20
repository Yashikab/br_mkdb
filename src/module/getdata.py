# python 3.7.5
# coding: utf-8
# from module import const
import pytest
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


class TestGetData:
    '''
    http://boatrace.jp/owpc/pc/race/racelist?rno=3&jcd=06&hd=20200408 \n
    番組表
    '''

    # 選手情報の取得
    @pytest.fixture(scope='class')
    def programinfo(self):
        # 3R
        self.race_no = 3
        # place : hamanako 06
        self.jyo_code = 6
        # day 2020/04/08
        self.day = 20200408

        op = OfficialProgram(self.race_no, self.jyo_code, self.day)
        # 1列目
        sample_info1 = op.getplayerinfo2dict(row=1)
        # 2列目
        sample_info2 = op.getplayerinfo2dict(row=2)

        return (sample_info1, sample_info2)

    # 公式番組表に関するテスト
    @pytest.mark.parametrize("target, idx, expected", [
        ('name', 0, "鈴木裕隆"),
        ('name', 1, "小林晋"),
        ('id', 0, 4231),
        ('id', 1, 4026),
        ('level', 0, 'B1'),
        ('level', 1, 'B1'),
        ('home', 0, '愛知'),
        ('home', 1, '東京'),
        ('birth_place', 0, '愛知'),
        ('birth_place', 1, '東京'),
        ('age', 0, 36),
        ('age', 1, 42),
        ('weight', 0, 57.0),
        ('weight', 1, 53.9),
        ('num_F', 0, 0),
        ('num_F', 1, 0),
        ('num_L', 0, 0),
        ('num_L', 1, 0),
        ('avg_ST', 0, 0.21),
        ('avg_ST', 1, 0.20),
        ('all_1rate', 0, 4.81),
        ('all_1rate', 1, 4.24),
        ('all_2rate', 0, 29.47),
        ('all_2rate', 1, 20.34),
        ('all_3rate', 0, 46.32),
        ('all_3rate', 1, 32.20),
        ('local_1rate', 0, 5.00),
        ('local_1rate', 1, 4.04),
        ('local_2rate', 0, 33.33),
        ('local_2rate', 1, 17.39),
        ('local_3rate', 0, 60.00),
        ('local_3rate', 1, 34.78),
        ('motor_no', 0, 23),
        ('motor_no', 1, 21),
        ('motor_2rate', 0, 54.66),
        ('motor_2rate', 1, 27.00),
        ('motor_3rate', 0, 72.46),
        ('motor_3rate', 1, 46.84),
        ('boat_no', 0, 34),
        ('boat_no', 1, 73),
        ('boat_2rate', 0, 15.05),
        ('boat_2rate', 1, 32.32),
        ('boat_3rate', 0, 33.33),
        ('boat_3rate', 1, 52.53)
    ])
    def test_name(self, target, idx, expected, programinfo):
        assert programinfo[idx][target] == expected

    # # 直前情報の取得
    # def test_chokuzen_info(self):
    #     # 3R
    #     self.race_no = 3
    #     # place : hamanako 06
    #     self.jyo_code = 6
    #     # day 2020/04/08
    #     self.day = 20200408
