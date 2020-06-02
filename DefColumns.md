# テーブルカラム定義

## jyo_master

競艇場のマスタテーブル

- jyo_cd : Primary key
- jyo_name

## holdjyo_id

- datejyo_id: yyyymmdd{jyo_code:02} primary key
- holddate: yyyymmdd
- jyo_cd: 会場コード
- jyo_name: 会場名
- shinko: 進行状況
- ed_race_no: 最終レースの番号（中止の場合は0)

## raceinfo_tb

- race_id: yyyymmdd{jyo_cd:02}{race_no:02} INT: Primary key
- datejyo_id: yyyymmdd{jyo_cd:02}: 外部キー 設定参照： holdjyo_tb.datejyo_id
- holddate DATE: yyyymmdd
- jyo_cd INT: 会場コード 外部キー 設定参照： jyo_master.jyo_code
- race_no INT: レース番号
- taikai_name varchar(400): 大会名
- grade varchar(100): G1G2G3,一般がある そのまま格納
- race_type varchar(100): 予選, 準優勝戦など そのまま格納
- race_kyori INT: レースの距離基本は1800mと思われる
- is_antei BOOL: 安定板使用の有無
- is_shinnyukotei BOOL: 進入固定レースの有無

## program_tb

- waku_id: yyyymmdd{jyo_cd:02}{race_no:02}{waku} BIGINT: Primary key
- race_id: yyyymmdd{jyo_cd:02}{race_no:02} INT: 外部キー 設定参照： raceinfo_tb.raceinfo_id
- p_name VARCHAR(100): 選手名
- p_id INT: 選手登録番号
- p_level VARCHAR(30): 選手級
- p_home VARCHAR(30): 支部
- p_birthplace: VARCHAR(30): 出身地
- p_age INT: 年齢
- p_weight FLOAT: 体重
- p_num_f INT: F数
- p_num_l INT: L数
- p_avg_st FLOAT: 平均ST
- p_all_1rate FLOAT: 全国勝率
- p_all_2rate FLOAT: 全国2連対率
- p_all_3rate FLOAT: 全国3連対率
- p_local_1rate FLOAT: 当地勝率
- p_local_2rate FLOAT: 当地2連対率
- p_local_3rate FLOAT: 当地3連対率
- motor_no INT: モーター番号
- motor_2rate FLOAT: モーター2連対率
- motor_3rate FLOAT: モーター3連対率
- boat_no INT: ボート番号
- boat_2rate FLOAT: ボート2連対率
- boat_3rate FLOAT: ボート3連対率

## chokuzen_cond_tb

- race_id BIGINT: PRIMAR KEY 外部キー 参照先:race_info.race_id
- datejyo_id INT
- temp FLOAT: 気温
- weather VARCHAR(10): 天気
- wind_v INT: 風速
- w_temp FLOAT: 水温
- wave INT: 波高
- wind_dr INT: 風向

## chokuzen_player_tb

- waku_id: yyyymmdd{jyo_cd:02}{race_no:02}{waku} BIGINT: Primary key
    外部キー 設定参照： program_tb.waku_id
- race_id: yyyymmdd{jyo_cd:02}{race_no:02} BIGINT:
    外部キー 設定参照： chokuzen_cond_tb.race_id
- p_name VARCHAR(100): 選手名
- p_weight FLOAT: 体重
- p_chosei_weight FLOAT: 調整体重
- p_tenji_time FLOAT: 展示タイム
- p_tilt FLOAT: チルト角度
- p_tenji_course INT: スタ展時の進入コース
- p_tenji_st FLOAT: 展示ST

## race_result_tb

- race_id BIGINT: yyyymmdd{jyo_cd:02}{race_no:02}
    Primary key & 外部キー参照元: raceinfo_tb.race_id
- datejyo_id INT,
- temp FLOAT: 気温
- weather VARCHAR(10): 天気
- wind_v INT: 風速
- w_temp FLOAT: 水温
- wave INT: 波高
- wind_dr INT: 風向
- henkantei_list VARCHAR(100): 返還艇のカンマ区切り文字列（リスト）
- is_henkan BOOL: 返還挺の有無
- kimarite VARCHAR(100): 決まりて
- biko VARCHAR(500): 備考
- payout_3tan INT: 3連単払戻金
- popular_3tan INT: 3連単人気
- payout_3fuku INT: 3連複払戻金
- popular_3fuku INT: 3連複人気
- payout_2tan INT: 2連単払戻金
- popular_2tan INT: 2連単人気
- payout_2fuku INT: 2連複払戻金
- popular_2fuku INT: 2連複人気
- payout_1tan INT: 単勝払戻金

## p_result_tb

- waku_id: yyyymmdd{jyo_cd:02}{race_no:02}{waku} BIGINT: Primary key
    外部キー 設定参照： program_tb.waku_id
- race_id: yyyymmdd{jyo_cd:02}{race_no:02} BIGINT:
    外部キー 設定参照： chokuzen_cond_tb.race_id
- p_rank INT: 着順 (F,L 転覆などは-1)
- p_name VARCHAR(100): 選手名
- p_id INT: 選手登録番号
- p_racetime FLOAT: レースタイム
- p_course INT: 進入コース
- p_st_time FLOAT: スタートタイム(フライングはマイナス)

## odds_{1,2,3}_{tan,fuku}_tb

- race_id BIGINT: PrimaryKey
    外部キー 設定参照: raceinfo_tb race_id
- `1-2-3` FLOAT: (3連単の例，自動挿入する)
  バッククオートで囲む
