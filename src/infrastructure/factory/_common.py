import re
from typing import Optional


class CommonMethods:
    """Factoryで使う共通メソッド"""

    def __init__(self):
        pass

    def getonlyzenkaku2str(self, in_str: str) -> Optional[str]:
        try:
            # 全角の抽出
            return re.search(r'[^\x01-\x7E]+', in_str).group(0)
        except ValueError:
            return None
