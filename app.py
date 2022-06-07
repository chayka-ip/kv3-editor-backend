import os
from flask import Flask, request
from flask_cors import CORS
from config import *

import parser_kv3 as parse


port = int(os.environ.get('PORT', 5000))

app = Flask(__name__)

# https://flask-cors.readthedocs.io/en/latest/
cors = CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})

data_key = 'data'


def create_response(d):
    return {data_key: d}


def get_data_from_response(d: dict):
    try:
        return d.get(data_key, "")
    except:
        return {data_key: ""}


@app.route("/")
def root_test():
    return "Server is running"


@app.route("/api/parse_raw_file", methods=['POST'])
def parse_raw_file():
    if request.method == 'POST':
        data = get_data_from_response(request.json)
        result = parse.kv3_file_string_to_json(data)
        return create_response(result)


@app.route("/api/json_to_kv3", methods=['POST'])
def route_json_to_kv3():
    if request.method == 'POST':
        data = get_data_from_response(request.json)
        result = parse.json_to_kv3(data)
        return create_response(result)


if __name__ == "__main__":
    app.run(threaded=True, port=port, debug=False)
    # app.run(host="0.0.0.0", port="5000", debug=True)
