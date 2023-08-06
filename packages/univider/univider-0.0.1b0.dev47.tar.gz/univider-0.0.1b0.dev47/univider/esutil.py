# -*- coding: UTF-8 -*-
import json
import hashlib
from elasticsearch import Elasticsearch
from settings import es_host
es = Elasticsearch(es_host)

def md5(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

def save_yuqing_article(title="", mp_name="", content="", post_date="", link="", html="", mp_code="", mp_desc="", copyright_logo="", article_author="", crawl_time=""):

    data = {}
    data['title'] = title
    data['mp_name'] = mp_name
    data['content'] = content
    data['post_date'] = post_date
    data['link'] = link
    data['html'] = html
    data['mp_code'] = mp_code
    data['mp_desc'] = mp_desc
    data['copyright_logo'] = copyright_logo
    data['article_author'] = article_author
    data['crawl_time'] = crawl_time

    index = "yuqing_index"
    doc_type = "article"
    body = json.dumps(data, ensure_ascii=False)
    id = md5(title+mp_name)
    # print body

    es.index(index=index, doc_type=doc_type, body=body, id=id)



if __name__ == '__main__':
    save_yuqing_article(
        title="title"
        , mp_name="mp_name"
        , content="content"
        , post_date="2015-12-31"
        , link="http://www.baidu.com/xxxxx"
        , html="html"
        , mp_code="haha"
        , mp_desc="mp_desc"
        , copyright_logo="copyright_logo"
        , article_author="article_author"
        , crawl_time="2017-12-31 12:31:21"
    )