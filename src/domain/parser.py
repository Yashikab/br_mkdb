from abc import ABCMeta, abstractmethod
from typing import Dict, Any

# TODO ここではURLの取得は行わない
# TODO htmlを読み込んでlxmlを使ってパースする．
# 番組表，直前，結果，オッズを作る(抽象化)


class ProgramParser(meta=ABCMeta):

    @abstractmethod
    def getplayerinfo2dict(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def getcommoninfo2dict(self) -> Dict[str, Any]:
        pass
