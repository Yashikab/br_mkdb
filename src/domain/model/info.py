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
