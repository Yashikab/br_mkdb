from dataclasses import make_dataclass
from datetime import date
from typing import List, Optional

from pydantic.dataclasses import dataclass


@dataclass
class HoldRaceInfo:
    date: date
    jyo_name: str
    jyo_cd: int
    shinko: str  # 進行状況
    ed_race_no: int  # 最終レース番号(中止とかに対応するため)


@dataclass
class ProgramPlayerInfo:
    """番組表記載の選手情報"""

    waku: int
    name: str
    id: int
    level: str
    home: str
    birth_place: str
    age: int
    weight: float
    num_F: Optional[int]
    num_L: Optional[int]
    avg_ST: Optional[float]  # 集計期間にデータがないと-になる
    all_1rate: Optional[float]  # 全国勝率
    all_2rate: Optional[float]  # 全国2連帯率
    all_3rate: Optional[float]  # 全国3連帯率
    local_1rate: Optional[float]  # 当地勝率
    local_2rate: Optional[float]  # 当地2連帯率
    local_3rate: Optional[float]  # 当地3連帯率
    motor_no: int
    motor_2rate: Optional[float]
    motor_3rate: Optional[float]
    boat_no: int
    boat_2rate: Optional[float]
    boat_3rate: Optional[float]


@dataclass
class ProgramCommonInfo:
    taikai_name: str
    grade: str
    race_type: str
    race_kyori: int
    is_antei: bool
    is_shinnyukotei: bool


@dataclass
class ProgramInfo:
    date: date
    jyo_cd: int
    race_no: int
    common: ProgramCommonInfo
    players: List[ProgramPlayerInfo]


@dataclass
class ChokuzenPlayerInfo:
    waku: int
    name: str
    weight: float
    chosei_weight: float
    tenji_time: Optional[float]
    tilt: Optional[float]
    tenji_course: Optional[int]
    tenji_st: Optional[float]


@dataclass
class WeatherInfo:
    temp: float
    weather: str
    wind_v: int
    w_temp: float
    wave: int
    wind_dr: int


@dataclass
class ChokuzenInfo:
    date: date
    jyo_cd: int
    race_no: int
    common: WeatherInfo
    players: List[ChokuzenPlayerInfo]


@dataclass
class ResultPlayerInfo:
    waku: int
    rank: int
    name: str
    no: int
    racetime: Optional[float]
    course: Optional[int]
    st_time: Optional[float]


@dataclass
class ResultCommonInfo:
    weather_info: WeatherInfo
    henkantei_list: str  # カンマ区切り
    is_henkan: bool
    kimarite: str
    biko: Optional[str]
    payout_3tan: Optional[int]
    popular_3tan: Optional[int]
    payout_3fuku: Optional[int]
    popular_3fuku: Optional[int]
    payout_2tan: Optional[int]
    popular_2tan: Optional[int]
    payout_2fuku: Optional[int]
    popular_2fuku: Optional[int]
    payout_1tan: Optional[int]


@dataclass
class ResultInfo:
    date: date
    jyo_cd: int
    race_no: int
    common: ResultCommonInfo
    players: List[ResultPlayerInfo]


# 連単キー生成
def rentan_keylist(rank: int) -> list:
    """連単用キーのリストを返す.

    Parameters
    ----------
        rank : int
            1 or 2 or 3 で単勝，2連単，3連単
    """
    rentan_key_list = []
    for fst in range(1, 7):
        if rank == 1:
            rentan_key_list.append(f"comb_{fst}")
        else:
            for snd in range(1, 7):
                if snd != fst and rank == 2:
                    rentan_key_list.append(f"comb_{fst}{snd}")
                else:
                    for trd in range(1, 7):
                        if fst != snd and fst != trd and snd != trd:
                            rentan_key_list.append(f"comb_{fst}{snd}{trd}")
    return rentan_key_list


ThreeRentan = make_dataclass(
    "ThreeRentan", [(key_name, float) for key_name in rentan_keylist(3)]
)
# pydanticに装着
ThreeRentan = dataclass(ThreeRentan)

TwoRentan = make_dataclass(
    "TwoRentan", [(key_name, float) for key_name in rentan_keylist(2)]
)
# pydanticに装着
TwoRentan = dataclass(TwoRentan)

Tansho = make_dataclass(
    "Tansho", [(key_name, float) for key_name in rentan_keylist(1)]
)
# pydanticに装着
Tansho = dataclass(Tansho)


# 連複キーリスト
def renfuku_keylist(rank: int) -> list:
    renfuku_key_list = []
    if rank == 2:
        for fst in range(1, 6):
            for snd in range(fst + 1, 7):
                renfuku_key_list.append(f"comb_{fst}{snd}")
        return renfuku_key_list
    elif rank == 3:
        for fst in range(1, 5):
            for snd in range(fst + 1, 6):
                for trd in range(snd + 1, 7):
                    renfuku_key_list.append(f"comb_{fst}{snd}{trd}")
        return renfuku_key_list


ThreeRenfuku = make_dataclass(
    "ThreeRenfuku", [(key_name, float) for key_name in renfuku_keylist(3)]
)
# pydanticに装着
ThreeRenfuku = dataclass(ThreeRenfuku)

TwoRenfuku = make_dataclass(
    "TwoRenfuku", [(key_name, float) for key_name in renfuku_keylist(2)]
)
# pydanticに装着
TwoRenfuku = dataclass(TwoRenfuku)


@dataclass
class OddsInfo:
    date: date
    jyo_cd: int
    race_no: int
    three_rentan: ThreeRentan
    three_renfuku: ThreeRenfuku
    two_rentan: TwoRentan
    two_renfuku: TwoRenfuku
    tansho: Tansho
