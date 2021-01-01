from pydantic.dataclasses import dataclass


@dataclass
class ProgramPlayerInfo:
    """番組表記載の選手情報"""

    name: str
    id: int
    level: str
    home: str
    birth_place: str
    age: int
    weight: float
    num_F: int
    num_L: int
    avg_ST: float
    all_1rate: float  # 全国勝率
    all_2rate: float  # 全国2連帯率
    all_3rate: float  # 全国3連帯率
    local_1rate: float  # 当地勝率
    local_2rate: float  # 当地2連帯率
    local_3rate: float  # 当地3連帯率
    motor_no: int
    motor_2rate: float
    motor_3rate: float
    boat_no: int
    boat_2rate: float
    boat_3rate: float


@dataclass
class ProgramCommonInfo:
    taikai_name: str
    grade: str
    race_type: str
    race_kyori: int
    is_antei: bool
    is_shinnyukotei: bool


@dataclass
class ChokuzenPlayerInfo:
    name: str
    weight: float
    chosei_weight: float
    tenji_time: float
    tilt: float
    tenji_course: int
    tenji_st: float


@dataclass
class WeatherInfo:
    temp: float
    weather: str
    wind_v: int
    w_temp: float
    wave: int
    wind_dr: int


@dataclass
class ResultPlayerInfo:
    rank: int
    name: str
    no: int
    racetime: float
    course: int
    st_time: float


@dataclass
class ResultCommonInfo:
    temp: float
    weather: str
    wind_v: int
    w_temp: float
    wave: int
    wind_dr: int
    henkantei_list: str  # カンマ区切り
    is_henkan: bool
    kimarite: str
    biko: str
    payout_3tan: int
    popular_3tan: int
    payout_3fuku: int
    popular_3fuku: int
    payout_2tan: int
    popular_2tan: int
    payout_2fuku: int
    popular_2fuku: int
    payout_1tan: int
