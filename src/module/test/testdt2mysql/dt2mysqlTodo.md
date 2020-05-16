# getdataからデータを取得し，mysqlに保存する

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
  - [x] データを挿入，重複は更新する

## レース情報データ

- 対象日+会場コード+レース番を主キーとする

## 番組表データ

- 対象日+会場コード+レース番+枠番を主キーとする

## 直前情報データ

- 対象日+会場コード+レース番+枠番を主キーとする
