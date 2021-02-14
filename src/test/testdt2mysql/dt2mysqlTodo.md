# getdataからデータを取得し，mysqlに保存する

- リレーショナルDBの設計図をexelで作成する

## 共通項

以下は必ず実行される（抽象クラスを作り継承する）

### テーブル作成機構（テーブルがない場合）

主キーの設定を行う

- [x] 抽象クラス作成: create_table_if_not_exists

### テーブル挿入機構

対象とする期間の開始日と終了日を引数とする

- [x] 抽象クラス作成

## 開催会場のデータ

- テーブル名: holdjyo_tb
- カラム
  - [x] datejyo_id: yyyymmdd{jyo_code:02} primary key
  - [x] holddate: yyyymmdd
  - [x] jyo_cd: 会場コード
  - [x] jyo_name: 会場名
  - [x] shinko: 進行状況
  - [x] ed_race_no: 最終レースの番号（中止の場合は0)
- [x] テーブルの作成
  - [x] quaryフォルダからcreate_holdplace_table.sqlを読む
    - [x] MySQLにテーブルが存在することを確認
    - [x] カラムが存在することを確認
- [x] データ挿入部を作成
  - [x] 日付をyyyymmdd形式で取得し,getholdplaceから情報を取得
  - [x] データを挿入，重複は何もしない

## レース情報データ

どちらもgetdata.OfficialProgramにあるので,
共通のクラスで各メソッドif分岐で設計（リファクタいるかも)

### レース共通データ

- if分岐用の名前: 'raceinfo'

- テーブル名: raceinfo_tb
- カラム名:
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
- [x] テーブルの作成
- [x] データ挿入部の作成
  - 引数は日付，場コード，レース番号
  - getdata.OfficialProgram.raceinfo2dictからデータを取得

### 番組表データ

- 対象日+会場コード+レース番+枠番を主キーとする

- if分岐用の名前: 'program'

- テーブル名: program_tb
- カラム名:
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
- [x] テーブルの作成
- [x] データ挿入部の作成
  - 引数は日付，場コード，レース番号
  - getdata.OfficialProgram.raceinfo2dictからデータを取得

## 直前情報データ

### 会場コンディション（共通データ）

- 対象日+会場コード+レース番を主キーとする

- テーブル名: chokuzen_cond_tb
- カラム名:
  - race_id BIGINT: PRIMAR KEY 外部キー 参照先:race_info.race_id
  - datejyo_id INT
  - temp FLOAT: 気温
  - weather VARCHAR(10): 天気
  - wind_v INT: 風速
  - w_temp FLOAT: 水温
  - wave INT: 波高
  - wind_dr INT: 風向

- [x] テーブルの作成
- [x] データ挿入部の作成
  - 引数は日付，場コード
  - getdata.OfficialChokuzen.getcondinfo2dictからデータを取得

### 枠別直前データ（wakuごと)

- 対象日+会場コード+レース番+wakuを主キーとする
- テーブル名: chokuzen_player_tb
- カラム名:
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

- [x] テーブルの作成
- [x] データ挿入部の作成

## 結果データ

### レース共通結果データ

- race_idを主キーとする
- テーブル名: race_result_tb
- カラム名:
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

- [x] テーブルの作成
- [x] データ挿入部の作成

### 枠別結果データ

- waku_idを主キーとする
- テーブル名: p_result_tb
- カラム名
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

- [x] テーブルの作成
- [x] データ挿入部の作成

## オッズデータを格納する

- race_idを主キーとする
- カラム名は，枠番を1-2-3のように'-'でつなぐ
- 3連単，3連複，2連単，2連複，単勝
- テーブル名:
odds_3tan_tb, odds_3fuku_tb, odds_2tan_tb, odds_2fuku_tb, odds_1tan_tb
- カラム名:
  - race_id BIGINT: PrimaryKey
      外部キー 設定参照: raceinfo_tb race_id
  - `1-2-3` FLOAT: (3連単の例，自動挿入する)
    バッククオートで囲む

- [x] キーを生成してタプルで返す関数をgetdata.OfficialOddsに作成
- [x] テーブルの作成
- [x] データ挿入部の作成
