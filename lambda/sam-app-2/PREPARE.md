## プロジェクトの作成
```
sam init --runtime python3.6
```
## ライブラリのインストール
```
pip install pytest moto boto3 --user
```
## テスト実行
```
python -m pytest tests/unit/test_handler.py
```