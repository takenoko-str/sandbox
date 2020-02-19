## HDDは空いてるのに　`no space left on device` でコンテナが動かない

### 現在起動中のコンテナに関わるものはそのまま残したい場合
```sh

docker system prune -af --volumes
```

### とりあえず全部消す場合
#### コンテナを全て消す
```sh

docker rm -f $(docker ps -aq)
```

#### コンテナイメージを全て消す
```sh

docker rmi -f $(docker images -q)
```

#### docker volumeを全て消す
```sh

docker volume rm -f $(docker volume ls -q)
```

[引用元](https://qiita.com/f-katkit/items/f4b4c5649b97258de5cb)