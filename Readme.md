# Let's revenge to the BoatRace

## jupyter labを使う場合(dockerを立ち上げる)

1. 下記makeの実行
2. ブラウザで，localhost:5000にアクセス．

```sh
# jupyter付きコンテナを立てる
make start
# docker内にbashでアクセス
make bash
# コンテナを止める
make stop
```

## pipenvによる実行

'''sh
pipenv install
pipenv run python src/hogehoge.py
'''
