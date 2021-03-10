# FactoryImplテストTODO

## raceinfo

- [x] 指定した日付におけるレース会場情報を取得する
  - [x] HoldRaceInfoに準拠した情報を返す
  - [x] イテレータで開催場順に帰ってくる
  - [x] 中止のハンドリング
    - [x] 中止情報の取得(進行状況)
    - [x] 開催されるレースリスト（何もなければrange(1,13))

## programinfo

- [x] 指定した開催場でレースぶんのイテレータが回る
- ピックアップした開催上のあるレースについて
  - [x] レース共通部分のデータが取れている（ProgramCommonInfoに従う)
  - [x] 選手個人の部分のデータが取れている(ProgramPlayerInfoに従う)

## chokuzeninfo

- [ ] 指定した開催場でレースぶんのイテレータが回る
- ピックアップした開催上のあるレースについて
  - [ ] レース共通部分のデータが取れている（ChokuzenCommonInfoに従う)
  - [ ] 選手個人の部分のデータが取れている(ChokuzenPlayerInfoに従う)