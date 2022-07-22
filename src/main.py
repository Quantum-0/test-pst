from flask import Flask

import another_file

app = Flask(__name__)


@app.route("/")
def hello_world():
    return another_file.test()


app.run('127.0.0.1', port=33321)
