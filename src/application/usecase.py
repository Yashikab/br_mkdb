from datetime import datetime, timedelta
from logging import getLogger
from typing import Iterator

from application.argument import DBType, Options
from domain.dbcontroller import DatabaseController  # sqlとはかぎらない
from domain.factory import (
    ChokuzenInfoFactory,
    OddsInfoFactory,
    ProgramInfoFactory,
    RaceInfoFactory,
    ResultInfoFactory,
)
from domain.repository import (
    ChokuzenInfoRepository,
    JyocdMasterRepository,
    OddsInfoRepository,
    ProgramInfoRepository,
    RaceInfoRepository,
    ResultInfoRepository,
)

# logger
logger = getLogger(__name__)


class DateRange:
    """
    ある日付からある日付までのyyyymmdd型の日付リストを返す
    """

    @classmethod
    def daterange(cls, st_date: datetime, ed_date: datetime) -> Iterator:
        """
        開始日から終了日までの日付のイテレータ

        Parameters
        ----------
            st_date: datetime
                開始日
            ed_date: datetime
                終了日
        """

        # +1することでeddateも含める
        for n in range((ed_date - st_date).days + 1):
            itr_date = st_date + timedelta(n)
            yield itr_date


class BoatRaceUsecase:
    def __init__(
        self,
        dbctl: DatabaseController,
        raceinfo_factory: RaceInfoFactory,
        program_factory: ProgramInfoFactory,
        choku_factory: ChokuzenInfoFactory,
        result_factory: ResultInfoFactory,
        odds_factory: OddsInfoFactory,
        jyocd_master_repo: JyocdMasterRepository,
        raceinfo_repo: RaceInfoRepository,
        program_repo: ProgramInfoRepository,
        choku_repo: ChokuzenInfoRepository,
        result_repo: ResultInfoRepository,
        odds_repo: OddsInfoRepository,
    ):
        self.__dbctl = dbctl
        self.__ri_factory = raceinfo_factory
        self.__pro_factory = program_factory
        self.__choku_factory = choku_factory
        self.__res_factory = result_factory
        self.__odds_factory = odds_factory
        self.__jm_repo = jyocd_master_repo
        self.__ri_repo = raceinfo_repo
        self.__pro_repo = program_repo
        self.__choku_repo = choku_repo
        self.__res_repo = result_repo
        self.__odds_repo = odds_repo

    def run(self, op: Options):
        logger.info("Connect MySQL server.")
        self.__dbctl.build()
        logger.info("Done")

        logger.info(f"Table Creating: {op.create_table}")
        if op.create_table:
            self.__jm_repo.create_table_if_not_exists()
            self.__ri_repo.create_table_if_not_exists()
            self.__pro_repo.create_table_if_not_exists()
            self.__choku_repo.create_table_if_not_exists()
            self.__res_repo.create_table_if_not_exists()
            self.__odds_repo.create_table_if_not_exists()
            logger.debug("Completed creating table.")

        for date in DateRange.daterange(op.start_date, op.end_date):
            logger.info(f"target date: {date}")
            holdraces = list(self.__ri_factory.getinfo(date))
            self.__ri_repo.save_info(holdraces)
            for hr in holdraces:
                logger.info(f"date: {hr.date}/ jyo: {hr.jyo_name}")
                try:
                    logger.info("Program Info")
                    self.__pro_repo.save_info(
                        self.__pro_factory.each_jyoinfo(
                            hr.date, hr.jyo_cd, hr.ed_race_no
                        )
                    )
                    logger.info(f"Chokuzen Info")
                    self.__choku_repo.save_info(
                        self.__choku_factory.each_jyoinfo(
                            hr.date, hr.jyo_cd, hr.ed_race_no
                        )
                    )
                    logger.info("Result Info")
                    self.__res_repo.save_info(
                        self.__res_factory.each_jyoinfo(
                            hr.date, hr.jyo_cd, hr.ed_race_no
                        )
                    )
                    logger.info("Odds Info")
                    self.__odds_repo.save_info(
                        self.__odds_factory.each_jyoinfo(
                            hr.date, hr.jyo_cd, hr.ed_race_no
                        )
                    )
                except Exception as e:
                    logger.error(f"{e}")

        # localは実験で落とすと消えてしまうので落とさない
        if op.db_type == DBType.gcs:
            logger.info("Down Server.")
            self.__dbctl.clean()

        logger.info("All completed.")
