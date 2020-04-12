# python 3.7.5
# coding: utf-8
from module import const
import unittest


class OfficialProgram:
    def getname(self, row: int) -> str:
        return "鈴木裕隆"


class GetDataTest(unittest.TestCase):
    '''
    http://boatrace.jp/owpc/pc/race/racelist?rno=3&jcd=06&hd=20200408 \n
    番組表1行目参照
    '''
    # 選手情報-氏名の取得
    def test_getplayer_name(self):
        # 1列目
        with self.subTest(row=1):
            name = OfficialProgram().getname(row=1)
            self.assertEqual("鈴木裕隆", name)
        # # 2列目
        # with self.subTest(row=2):
        #     name = OfficialProgram().getname(row=2)
        #     self.assertEqual("小林晋", name)


if __name__ == '__main__':
    unittest.main()
