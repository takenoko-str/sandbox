## グローバル設定のユーザではなく、リポジトリに対して設定する
```
git config --local user.name "takenoko-str"
git config --local user.email "xxx@gmail.com"
cat .git/config
```
## 直前のコミットの修正
```
git commit --amend --author="takenoko-str <xxx@gmail.com>"
```
## リモートプッシュが認証エラーになったとき
```
git remote set-url origin https://takenoko-str@github.com/takenoko-str/sandbox
```