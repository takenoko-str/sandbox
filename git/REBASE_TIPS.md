#### 開発中にmasterブランチの変更を反映する際にはmergeよりもrebase
```
# マスターを更新
git checkout master
git pull origin master # or git pull
# マスターの変更を反映
git checkout feature/your-branch
git rebase master
# もしコンフリクトしたら(ex. conflict_file.txt)
# マージしたときと同じように差分解消後、
git add conflict_file.txt
git rebase --continue
# 以上を繰り返す。
# rebase直前の状態に戻す場合は
git rebase --abort
```
#### 参考
[Git開発でmasterの内容を開発ブランチに反映させる方法](http://sota1235.com/blog/2015/03/19/git-rebase.html)
