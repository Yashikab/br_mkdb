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
  - raceinfo_id: yyyymmdd{jyo_cd:02}{race_no:02} INT: Primary key
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

## 直前情報データ

- 対象日+会場コード+レース番+枠番を主キーとする
