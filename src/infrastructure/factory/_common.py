import re
import sys
from logging import getLogger
from typing import Optional

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
