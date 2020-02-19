from flask import Flask
from datetime import datetime
import os
app = Flask(__name__)

@app.route("/")
def hello():
    image_name = os.getenv('IMAGE_NAME')
    image_tag = os.getenv('IMAGE_TAG')
    now = datetime.now()
    return f"Hello { image_name}:{ image_tag }! { now }"