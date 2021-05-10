import traceback
from datetime import date
from typing import Iterator, Union

import numpy as np
from tqdm import tqdm

from domain.factory import OddsInfoFactory
from domain.model.info import (
    OddsInfo,
    Tansho,
    ThreeRenfuku,
    ThreeRentan,
    TwoRenfuku,
    TwoRentan,
)
from infrastructure.getter import GetParserContent


class OddsInfoFactoryImpl(OddsInfoFactory):
    def each_jyoinfo(
        self, target_date: date, jyo_cd: int, ed_race_no: int
    ) -> Iterator[OddsInfo]:
        for race_no in tqdm(range(1, ed_race_no + 1)):
            try:
                yield self._raceinfo(target_date, jyo_cd, race_no)
            except Exception:
                self.logger.error(traceback.format_exc())

    def _raceinfo(
        self, target_date: date, jyo_cd: int, race_no: int
    ) -> OddsInfo:
        return OddsInfo(
            target_date,
            jyo_cd,
            race_no,
            self._three_rentan(target_date, jyo_cd, race_no),
            self._three_renfuku(target_date, jyo_cd, race_no),
            self._two_rentan(target_date, jyo_cd, race_no),
            self._two_renfuku(target_date, jyo_cd, race_no),
            self._tansho(target_date, jyo_cd, race_no),
        )

    def _three_rentan(
        self, target_date: date, jyo_cd: int, race_no: int
    ) -> ThreeRentan:
        return self._rentan_common(target_date, jyo_cd, race_no, 3)

    def _three_renfuku(
        self, target_date: date, jyo_cd: int, race_no: int
    ) -> ThreeRenfuku:
        return self._renfuku_common(target_date, jyo_cd, race_no, 3)

    def _two_renfuku(
        self, target_date: date, jyo_cd: int, race_no: int
    ) -> TwoRenfuku:
        return self._renfuku_common(target_date, jyo_cd, race_no, 2)

    def _two_rentan(
        self, target_date: date, jyo_cd: int, race_no: int
    ) -> TwoRentan:
        return self._rentan_common(target_date, jyo_cd, race_no, 2)

    def _tansho(self, target_date: date, jyo_cd: int, race_no: int) -> Tansho:
        # htmlをload
        target_url = (
            f"https://boatrace.jp/owpc/pc/race/oddstf?"
            f"rno={race_no}&"
            f"jcd={jyo_cd:02}&"
            f"hd={target_date.strftime('%Y%m%d')}"
        )
        lx_content = GetParserContent.url_to_content(
            url=target_url, content_type="lxml"
        )
        target_xpath = (
            "/html/body/main/div/div/div/div[2]"
            "/div[5]/div[1]/div[2]/table/tbody/"
            "tr/td[contains(@class, 'oddsPoint')]"
        )

        odds_els = lx_content.xpath(target_xpath)
        odds_list = list(map(lambda x: self._check_ketsujyo(x.text), odds_els))

        content_dict = {}
        for key_name in Tansho.__annotations__.keys():
            content_dict[key_name] = odds_list.pop(0)
        return Tansho(**content_dict)

    def _rentan_common(
        self, target_date: date, jyo_cd: int, race_no: int, rank: int
    ) -> Union[Tansho, TwoRentan, ThreeRentan]:
        """
        2/3連単オッズを抜き出し辞書型で返す
        1-2-3のオッズは return_dict[1][2][3]に格納される
        """
        assert rank in [2, 3], "rank must be in 2 or 3 as integer."
        # 共通メソッドを使える
        odds_hol_list = self._tanfuku_common(
            target_date, jyo_cd, race_no, rank, "rentan"
        )
        odds_list = self._rentan_list(odds_hol_list)

        content_dict = {}
        if rank == 2:
            for key_name in TwoRentan.__annotations__.keys():
                content_dict[key_name] = odds_list.pop(0)
            return TwoRentan(**content_dict)
        elif rank == 3:
            for key_name in ThreeRentan.__annotations__.keys():
                content_dict[key_name] = odds_list.pop(0)
            return ThreeRentan(**content_dict)

    def _renfuku_common(
        self, target_date: date, jyo_cd: int, race_no: int, rank: int
    ) -> dict:
        """
        2/3連複オッズを抜き出し辞書型で返す
        1=2=3のオッズは return_dict[1][2][3]に格納される
        """
        assert rank in [2, 3], "rank must be 2 or 3 as integer."
        # 連単・連複の共通メソッドを使ってoddsテーブルを抜く
        odds_rv = self._tanfuku_common(
            target_date, jyo_cd, race_no, rank, "renfuku"
        )
        odds_rv.reverse()
        # 辞書で格納する
        content_rv_dict = {}
        for key_name in self._renfuku_keyrvlist(rank):
            content_rv_dict[key_name] = odds_rv.pop(0)

        # キーを並び替え
        content_dict = {}
        for key, value in sorted(content_rv_dict.items(), key=lambda x: x[0]):
            content_dict[key] = value

        if rank == 2:
            return TwoRenfuku(**content_dict)
        elif rank == 3:
            return ThreeRenfuku(**content_dict)

    def _tanfuku_common(
        self, target_date: date, jyo_cd: int, race_no: int, num: int, kake: str
    ) -> list:
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
        assert kake in ["rentan", "renfuku"]
        assert num in [2, 3]
        # num = 2ならtypeによらずtype='tf'
        if num == 2:
            html_type = "tf"
        elif kake == "rentan":
            html_type = "t"
        elif kake == "renfuku":
            html_type = "f"
        else:
            html_type = "tf"

        # htmlをload
        target_url = (
            f"https://boatrace.jp/owpc/pc/race/odds{num}{html_type}?"
            f"rno={race_no}&"
            f"jcd={jyo_cd:02}&hd={target_date.strftime('%Y%m%d')}"
        )
        lx_content = GetParserContent.url_to_content(
            url=target_url, content_type="lxml"
        )
        # 3連単と共通--------------------
        # oddsテーブルの抜き出し
        if num == 2 and kake == "renfuku":
            table_xpath = (
                "/html/body/main/div/div/div/div[2]/div[8]/table/tbody"
            )
        else:
            table_xpath = (
                "/html/body/main/div/div/div/div[2]/div[6]/table/tbody"
            )

        # 横優先のoddsリスト
        odds_el = lx_content.xpath(
            "/".join([table_xpath, "tr/td[contains(@class, 'oddsPoint')]"])
        )
        odds_horizontals = list(
            map(lambda x: self._check_ketsujyo(x.text), odds_el)
        )

        return odds_horizontals

    def _check_ketsujyo(self, float_str: str):
        """欠場をチェックする"""
        try:
            return float(float_str)
        except ValueError:
            return -9999.0

    def _rentan_list(self, odds_holizontals: list) -> list:
        """
        2 3連単用処理
        """
        # numpy array化
        num_rows = len(odds_holizontals) // 6
        odds_matrix = np.array(odds_holizontals).reshape(num_rows, 6)
        # 転置を取り，つなげてリスト化
        odds_list = list(odds_matrix.T.reshape(-1))
        return odds_list

    def _renfuku_keyrvlist(self, rank: int) -> list:
        """スクレイプ用順番"""
        renfuku_key_rv = []
        assert rank in [2, 3], "rank must be 2 or 3 as integer."
        if rank == 2:
            for snd in range(6, 0, -1):
                for fst in range(snd - 1, 0, -1):
                    renfuku_key_rv.append(f"comb_{fst}{snd}")
        elif rank == 3:
            # 2位起点にすると裏返せる
            for snd in range(5, 0, -1):
                for trd in range(6, snd, -1):
                    for fst in range(snd - 1, 0, -1):
                        renfuku_key_rv.append(f"comb_{fst}{snd}{trd}")
        return renfuku_key_rv
