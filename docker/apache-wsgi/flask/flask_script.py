from flask import Flask
from datetime import datetime
app = Flask(__name__)

@app.route("/")
def hello():
    now = datetime.now()
    return f"Hello World! { now }"