import time
from logging import getLogger

from application.argument import DBType, Options
from domain.dbcontroller import DatabaseController  # sqlとはかぎらない
from domain.sql.executer import SqlExecuter  # sqlとはかぎらない
from domain.tablecreator import create_table  # 多分domainじゃない
from infrastructure.const import MAIN_LOGNAME
from infrastructure.dt2sql import (
    ChokuzenData2sql,
    JyoData2sql,
    Odds2sql,
    RaceData2sql,
    ResultData2sql,
)
from domain.factory import (
    RaceInfoFactory,
    ProgramInfoFactory,
    ChokuzenInfoFactory,
    ResultInfoFactory,
    OddsInfoFactory,
)
from domain.repository import (
    RaceInfoRepository,
    ProgramInfoRepository,
    ChokuzenInfoRepository,
    ResultInfoRepository,
    OddsInfoRepository,
)
from infrastructure.getdata import DateRange as dr

# logger
logger = getLogger(MAIN_LOGNAME)


class BoatRaceUsecase:
    def __init__(
        self,
        dbctl: DatabaseController,
        raceinfo_factory: RaceInfoFactory,
        program_factory: ProgramInfoFactory,
        choku_factory: ChokuzenInfoFactory,
        result_factory: ResultInfoFactory,
        odds_factory: OddsInfoFactory,
        raceinfo_repo: RaceInfoRepository,
        program_repo: ProgramInfoRepository,
        choku_repo: ChokuzenInfoRepository,
        result_repo: ResultInfoRepository,
        odds_repo: OddsInfoRepository,
        sql_executer: SqlExecuter,
    ):
        self.__dbctl = dbctl
        self.__ri_factory = raceinfo_factory
        self.__pro_factory = program_factory
        self.__choku_factory = choku_factory
        self.__res_factory = result_factory
        self.__odds_factory = odds_factory
        self.__ri_repo = raceinfo_repo
        self.__pro_repo = program_repo
        self.__choku_repo = choku_repo
        self.__res_repo = result_repo
        self.__odds_factory = odds_repo
        self.__sql_executer = sql_executer

    def run(self, op: Options):
        logger.info("Connect MySQL server.")
        self.__dbctl.build()
        logger.info("Done")

        logger.info(f"Table Creating: {op.create_table}")
        logger.debug("load classes from dt2sql")
        jd2sql = JyoData2sql()
        rd2sql = RaceData2sql()
        cd2sql = ChokuzenData2sql()
        res2sql = ResultData2sql()
        odds2sql = Odds2sql()
        logger.debug("Completed loading classes.")

        if op.create_table:
            logger.debug("Create table if it does not exist.")
            create_table(self.__sql_executer)
            logger.debug("Completed creating table.")

        for date in dr.daterange(op.start_date, op.end_date):
            try:
                logger.debug(f"target date: {date}")
                jd2sql.insert2table(date)
                # jd2sqlで開催場と最終レース番を取得する
                logger.debug("insert race data: race chokuzen result odds")
                jyo_cd_list = jd2sql.map_raceno_dict.keys()
                start_time = time.time()
                logger.debug("Start to insert race data")
                rd2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
                logger.debug("Start to insert chokuzen data")
                cd2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
                logger.debug("Start to insert result data")
                res2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
                logger.debug("Start to insert odds data")
                odds2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)

                elapsed_time = time.time() - start_time
                logger.debug(f"completed in {elapsed_time}sec")
                logger.debug("insert race data completed.")
            except Exception as e:
                logger.error(f"{e}")

        # localは実験で落とすと消えてしまうので落とさない
        if op.db_type == DBType.gcs:
            logger.info("Down Server.")
            self.__dbctl.clean()

        logger.info("All completed.")

    @classmethod
    def localmysql(cls):
        from infrastructure.dbcontroller import LocalSqlController
        from infrastructure.mysql import MysqlExecuter

        return BoatRaceUsecase(LocalSqlController(), MysqlExecuter())

    @classmethod
    def gcpmysql(cls):
        from infrastructure.dbcontroller import CloudSqlController
        from infrastructure.mysql import MysqlExecuter

        return BoatRaceUsecase(CloudSqlController(), MysqlExecuter())
