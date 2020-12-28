from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List

# TODO 先にgetdataのほうでdt2sqlへの受け渡しに対するドメイン化を行う．
# 単一のユーザーに対して責任を追う．（SRP単一責任の法則）
# ここではURLの取得は行わない
# 番組表，直前，結果，オッズを作る(抽象化)


class HoldPlaceParser(meta=ABCMeta):

    @abstractmethod
    def holdplace2list(self) -> List[str]:
        pass

    @abstractmethod
    def holdplace2cdlist(self) -> List[int]:
        pass

    @abstractmethod
    def holdinfo2dict(self, hp_name: str) -> Dict[str, Any]:
        pass


class ProgramParser(meta=ABCMeta):

    @abstractmethod
    def getplayerinfo2dict(self, waku) -> Dict[str, Any]:
        pass

    @abstractmethod
    def getcommoninfo2dict(self) -> Dict[str, Any]:
        pass


class ChokuzenParser(meta=ABCMeta):

    @abstractmethod
    def getplayerinfo2dict(self, waku: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def getcommoninfo2dict(self) -> Dict[str, Any]:
        pass


class ResultsParser(meta=ABCMeta):

    @abstractmethod
    def getplayerinfo2dict(self, waku: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def getcommoninfo2dict(self) -> Dict[str, Any]:
        pass


class OddsParser(meta=ABCMeta):

    @abstractmethod
    def three_rentan(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def three_renfuku(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def two_rentan(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def two_renfuku(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def tansho(self) -> Dict[str, float]:
        pass
