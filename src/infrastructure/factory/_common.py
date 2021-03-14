import re
import sys
from logging import getLogger
from typing import Optional

import lxml.html as lxml
from domain.model.info import WeatherInfo

from infrastructure.const import MODULE_LOG_NAME


class CommonMethods:
    """Factoryで使う共通メソッド"""

    def __init__(self):
        self.logger = \
            getLogger(MODULE_LOG_NAME).getChild(self.__class__.__name__)

    def getonlyzenkaku2str(self, in_str: str) -> Optional[str]:
        try:
            # 全角の抽出
            return re.search(r'[^\x01-\x7E]+', in_str).group(0)
        except ValueError:
            return None

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
        try:
            in_str = re.search(r'-{0,1}[0-9]+', in_str)
            out_int = int(in_str.group(0))
        except AttributeError as e:
            self.logger.error(f"in_str: {in_str}, error: {e}")
            out_int = None
        return out_int

    def getweatherinfo(self,
                       lx_content: lxml.HtmlElement,
                       table_xpath: str) -> WeatherInfo:
        """
        水面気象情報テーブルのスクレイパー

        Parameters
        ----------
            lx_content: lxml.HtmlElement,
            table_selector : str

        Returns
        -------
            content_dict : dict
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')

        # 気温
        temp_xpath = "/".join([table_xpath, "div[1]/div/span[2]"])
        temp = lx_content.xpath(temp_xpath)[0].text.strip()
        temp = self.rmletter2float(temp)

        # 天気
        weather_xpath = "/".join([table_xpath, "div[2]/div/span"])
        weather = lx_content.xpath(weather_xpath)[0].text.strip()
        weather = self.getonlyzenkaku2str(weather)

        # 風速
        wind_v_xpath = "/".join([table_xpath, "div[3]/div/span[2]"])
        wind_v = lx_content.xpath(wind_v_xpath)[0].text.strip()
        wind_v = self.rmletter2int(wind_v)

        # 水温
        w_temp_xpath = "/".join([table_xpath, "div[5]/div/span[2]"])
        w_temp = lx_content.xpath(w_temp_xpath)[0].text.strip()
        w_temp = self.rmletter2float(w_temp)

        # 波高
        wave_xpath = "/".join([table_xpath, "div[6]/div/span[2]"])
        wave = lx_content.xpath(wave_xpath)[0].text.strip()
        wave = self.rmletter2int(wave)

        # 風向き
        # 画像のみの情報なので，16方位の数字（画像の名前）を抜く
        # p中のクラス名2番目にある
        wind_dr_xpath = "/".join([table_xpath, "div[4]/p"])
        wind_dr_class = lx_content.xpath(wind_dr_xpath)[0].attrib["class"]
        wind_dr = wind_dr_class.split()[1].strip()
        wind_dr = self.rmletter2int(wind_dr)

        return WeatherInfo(
            temp,
            weather,
            wind_v,
            w_temp,
            wave,
            wind_dr
        )

    def getSTtable(self,
                   lx_content: lxml.HtmlComment,
                   tbody_xpath: str,
                   waku: int,
                   table_type: str = "default") -> tuple:
        """
        スタート情報のテーブルを抜き取り対象枠のコースとSTタイムを
        タプルにして返す.

        Parameters
        ----------
            lx_content: lxml.HtmlComment
            table_selector : str
                スタート情報のテーブル
            waku : int
                知りたい情報の枠
            table_type
                直前と結果で少し処理が違う

        Returns
        -------
            course st_time : tuple
                対象枠のコースとSTタイムをタプルで返す
        """
        self.logger.debug(f'called {sys._getframe().f_code.co_name}.')

        tr_xpath = "/".join([tbody_xpath, "tr"])
        len_course = len(lx_content.xpath(tr_xpath))
        # 欠場挺があると6挺にならないときがあるので、assertをつかわない
        if len_course < 6:
            self.logger.warning("there are less than 6 boats.")
        # コース抜き出し
        # コースがキーで，号がvalueなので全て抜き出してから逆にする
        waku_list = []
        st_time_list = []
        for i in range(1, len_course + 1):
            try:
                waku_no_xpath = "/".join([
                    tbody_xpath, f"tr[{i}]/td/div/span[1]"])
                waku_no = lx_content.xpath(waku_no_xpath)[0].text
                waku_list.append(self.rmletter2int(waku_no))

                if table_type == "result":
                    st_time_xpath = "/".join([
                        tbody_xpath,
                        f"tr[{i}]/td/div/span[3]/span/text()"])
                    st_time = lx_content.xpath(st_time_xpath)[0].strip()
                else:
                    st_time_xpath = "/".join([
                        tbody_xpath, f"tr[{i}]/td/div/span[3]"])
                    st_time = lx_content.xpath(st_time_xpath)[0].text
                # Fをマイナスに変換し，少数化
                st_time = self.rmletter2float(st_time.replace('F', '-'))
                st_time_list.append(st_time)
            except IndexError as e:
                self.logger.error(e)

        # waku がwaku_listになければ
        if waku not in waku_list:
            return (None, None)

        # 0~5のインデックスなので1~6へ変換のため+1
        course_idx = waku_list.index(waku)
        course = course_idx + 1

        # listのキーはコースであることに注意
        st_time = st_time_list[course_idx]

        return (course, st_time)
