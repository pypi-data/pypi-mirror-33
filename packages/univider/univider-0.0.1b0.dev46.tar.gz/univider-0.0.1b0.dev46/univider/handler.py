# -*- coding: utf-8 -*-
import json

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/crawl", methods=['GET', 'POST'])
def crawl():

    # parse needs
    data = request.get_data()
    params = json.loads(data)

    # handle needs
    from univider.fetcher import Fetcher
    fetcher = Fetcher()
    result = fetcher.fetch_page_with_cache(params)

    # print result

    # return needs
    return jsonify(result)
    # return result["html"].decode('gbk')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5010,debug=False)

def main():
    app.run(host='0.0.0.0',port=5010,debug=False)