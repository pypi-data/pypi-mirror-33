# -*- coding: utf-8 -*-
import base64
import random
import socket
import re
import urllib
import urllib2
import urlparse
import cx_Oracle
import requests
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
import time
from elasticsearch import Elasticsearch

from univider.esutil import save_yuqing_article
from univider.logger import Logger
from univider.settings import es_host
from pyquery import PyQuery as pyq



class Fetcher():

    logger = Logger(__name__).getlogger()
    def persist(self,params,result):

        try:
            from univider.settings import landing
            if(landing):
                from univider.subprocessor import Subprocessor
                subprocessor = Subprocessor(landing,params,result)
                subprocessor.persist()
            else:
                pass
        except Exception,e:
            print Exception,":",e

    def fetch_page_with_cache(self,params):
        if(params.has_key("iscache") and params["iscache"] == "false"):
            iscache = False
        else:
            iscache = True

        if(iscache):
            params_c = params.copy()
            del params_c['uuid']
            from univider.encrypter import get_md5_value
            ckey = get_md5_value(str(params_c))
            try:
                from univider.cacher import Cacher
                cacher = Cacher()
                cvalue = cacher.get(ckey)
                if(cvalue!= None and cvalue!=''):
                    self.logger.info('got cache ' + params['url'])
                    result = eval(cvalue)
                    # self.persist(params,result)
                    return result
            except Exception,e:
                print Exception,":",e
        result = self.fetch_page(params)
        if(iscache):
            try:
                cacher.set(ckey,str(result))
                self.logger.info('cached source ' + params['url'])
            except Exception,e:
                print Exception,":",e
        self.persist(params,result)
        return result

    def fetch_page(self,params):
        date=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        uuid = params["uuid"]
        node = socket.gethostname()

        try:
            url = params["url"]
            if(params.has_key("headers")):
                headers = urlparse.parse_qs(params["headers"], False)
            else:
                headers = {}

            if(params.has_key("method") and params["method"] == "POST"):
                # POST
                if(params.has_key("post.params")):
                    data = params["post.params"]
                else:
                    data = None
                req = urllib2.Request(url=url, data=data, headers=headers)
            else:
                # GET
                if url.startswith("http://mp.weixin.qq.com") or url.startswith("https://mp.weixin.qq.com"):
                    url = url.replace(u"%3D","=",10)
                    if "chksm" in url:
                        url = url[:url.index("&chksm")]
                    es = Elasticsearch(es_host)
                    index = "yuqing_index"
                    doc_type = "article"
                    url = url.replace("https","http")
                    body = {
                          "query": {
                            "match_phrase": {
                              "link": url
                            }
                          }
                        }
                    resp = es.search(index=index, doc_type=doc_type, body=body)
                    if len(resp['hits']['hits'])>0:
                        print 'ES alreay exist'
                        html = resp['hits']['hits'][0]['_source']['html']
                        self.logger.info('get weixin cached source ' + url)
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(html, 'lxml')
                            title = soup.title.string
                        except Exception, e:
                            print Exception, ":", e
                            title = ""
                        status = "OK"

                        httpstatus=200
                        httpcontenttype="text/html; charset=UTF-8"

                        if (params.has_key("onlytitle") and params["onlytitle"] == "true"):
                            result = {
                                'uuid': uuid,
                                'status': status,
                                'node': node,
                                'httpstatus': httpstatus,
                                'httpcontenttype': httpcontenttype,
                                'title': title
                            }
                        else:
                            result = {
                                'uuid': uuid,
                                'status': status,
                                'node': node,
                                'httpstatus': httpstatus,
                                'httpcontenttype': httpcontenttype,
                                'html': html,
                            }
                        self.logger.info('fetched source ' + url)
                        return result

                    else:
                        import sys
                        reload(sys)
                        sys.setdefaultencoding('utf-8')
                        status = "OK"
                        httpstatus = 200
                        httpcontenttype = "text/html; charset=UTF-8"
                        db_conn = cx_Oracle.connect('spd_dm/spd_dm_1Q#@pdb_spider')
                        oreader = db_conn.cursor()
                        get_status = "select status from ip_pool_proxy"
                        oreader.execute(get_status)
                        status_result = oreader.fetchone()
                        oreader.close()
                        db_conn.close()
                        try:
                            if status_result[0] == 'False':
                                req = urllib2.Request(url=url, headers=headers)
                                html = urllib2.urlopen(req, timeout=5).read()
                            else:
                                db_conn = cx_Oracle.connect('spd_dm/spd_dm_1Q#@pdb_spider')
                                oreader = db_conn.cursor()
                                get_proxy = "select proxy from (select * from spd_dm.ip_pool order by data_date desc) a where rownum<5"
                                oreader.execute(get_proxy)
                                result = oreader.fetchall()
                                oreader.close()
                                db_conn.close()
                                proxy1 = random.choice(result)[0]
                                #proxy = Proxy(
                                #    {
                                #        'proxyType': ProxyType.MANUAL,
                                #        'httpProxy': proxy1  # 代理ip和端口
                                #    }
                                #)
                                #desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
                                ## 把代理ip加入到技能中
                                #proxy.add_to_capabilities(desired_capabilities)
                                #driver = webdriver.PhantomJS(executable_path="/home/spd/app/phantomjs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs",desired_capabilities=desired_capabilities)
                                #driver.get(url)
                                #driver.find_element_by_css_selector("#meta_content > em").click()
                                #html = driver.page_source
                                #driver.close()
                                #driver.quit()
                                #r = requests.get(url, proxies={"http": proxy1})
                                #html = r.text
                                proxy_handler = urllib2.ProxyHandler({"http": "%s" % proxy1, "https": "%s" % proxy1})
                                opener = urllib2.build_opener(proxy_handler)
                                html = opener.open(url, timeout=10).read()
                            py_html = pyq(html)
                            try:
                                error_message = py_html('.global_error_msg').text()
                                # print error_message
                                if "内容已被发布者删除" in error_message:
                                    result = {
                                        'uuid': uuid,
                                        'status': status,
                                        'node': node,
                                        'httpstatus': httpstatus,
                                        'httpcontenttype': httpcontenttype,
                                        'html': html,
                                    }
                                    return result
                            except Exception, e:
                                print e, '1'
                            try:
                                transfer_message = py_html('.weui-msg__title').text()
                                # print transfer_message
                                if "公众号已迁移" in transfer_message:
                                    result = {
                                        'uuid': uuid,
                                        'status': status,
                                        'node': node,
                                        'httpstatus': httpstatus,
                                        'httpcontenttype': httpcontenttype,
                                        'html': html,
                                    }
                                    return result
                            except Exception, e:
                                print e, '2'
                            try:
                                shield_message = py_html('.text_area>p').text()
                                # print shield_message
                                if "无法查看" in shield_message:
                                    result = {
                                        'uuid': uuid,
                                        'status': status,
                                        'node': node,
                                        'httpstatus': httpstatus,
                                        'httpcontenttype': httpcontenttype,
                                        'html': html,
                                    }
                                    return result
                            except Exception, e:
                                print e, '3'
                            try:
                                share_message = py_html('.text_area>p.tips').text()
                                # print share_message
                                if "分享" in share_message:
                                    result = {
                                        'uuid': uuid,
                                        'status': status,
                                        'node': node,
                                        'httpstatus': httpstatus,
                                        'httpcontenttype': httpcontenttype,
                                        'html': html,
                                    }
                                    return result
                            except Exception, e:
                                print e, '4'
                            title = py_html('#img-content>h2').text()
                            # print title
                            copyright_logo = py_html('#copyright_logo').text().split('：')[0]
                            # print copyright_logo
                            post_date = re.findall(r'var publish_time = "(.*?)"', str(html))[0]
                            # print post_date
                            if '-' not in post_date:
                                result = {
                                    'uuid': uuid,
                                    'status': status,
                                    'node': node,
                                    'httpstatus': httpstatus,
                                    'httpcontenttype': httpcontenttype,
                                    'html': html,
                                }
                                return result
                            if copyright_logo == '':
                                post_author = py_html('#meta_content > span.rich_media_meta.rich_media_meta_text').text()
                            else:
                                post_author = py_html('#meta_content > span:nth-child(2)').text()
                            if post_author == '':
                                post_author = 'null'

                            weixin_mp_name = py_html('#meta_content>span>a').text()
                            # print weixin_mp_name
                            weixin_mp_code = py_html('#js_profile_qrcode > div > p:nth-child(3) > span').text()
                            # print weixin_mp_code
                            weixin_mp_desc = py_html('#js_profile_qrcode > div > p:nth-child(4) > span').text()
                            content = py_html('#js_content').text()
                            if len(weixin_mp_name) == len(title) == len(weixin_mp_code) == len(post_date) == 0:
                                result = {
                                    'uuid': uuid,
                                    'status': status,
                                    'node': node,
                                    'httpstatus': httpstatus,
                                    'httpcontenttype': httpcontenttype,
                                    'html': html,
                                }
                                return result
                            try:
                                save_yuqing_article(title=title, mp_name=weixin_mp_name, content=content,
                                                    post_date=post_date, link=url,
                                                    html=html, mp_code=weixin_mp_code,
                                                    mp_desc=weixin_mp_desc,
                                                    copyright_logo=copyright_logo, article_author=post_author,
                                                    crawl_time=date)
                                result = {
                                    'uuid': uuid,
                                    'status': status,
                                    'node': node,
                                    'httpstatus': httpstatus,
                                    'httpcontenttype': httpcontenttype,
                                    'html': html,
                                }
                                return result
                            except Exception, e:
                                print e, '5'
                                return
                        except Exception, e:
                            print e, '6'
                else:
                    req = urllib2.Request(url=url, headers=headers)

            response = urllib2.urlopen(req,timeout=5)
            httpstatus = response.code
            httpcontenttype = response.info().getheader("Content-Type")

            if(params.has_key("ajax") and params["ajax"] == "true"):
                if(params.has_key("ajaxTimeout")):
                    ajaxTimeout = params["ajaxTimeout"]
                else:
                    ajaxTimeout = 8
                if(params.has_key("ajaxLoadImage")):
                    ajaxLoadImage = params["ajaxLoadImage"]
                else:
                    ajaxLoadImage = "false"
                from univider.render import Render
                render = Render()
                html = render.getDom(url,ajaxLoadImage,ajaxTimeout)
            else:
                html = response.read()

                gzipped = response.headers.get('Content-Encoding')

                if gzipped:
                    import zlib
                    html = zlib.decompress(html, 16+zlib.MAX_WBITS)

                if('GBK' in httpcontenttype or 'gbk' in httpcontenttype):
                    try:
                        html = html.decode('gbk')
                    except Exception,e:
                        print Exception,":",e

            # print 'html : ' + html

            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html,'lxml')
                title = soup.title.string
            except Exception,e:
                print Exception,":",e
                title = ""
            status = "OK"

            # print 'title : ' + title

        except Exception,e:
            httpstatus = 400
            httpcontenttype = ""
            title = ""
            html = ""
            status = str(Exception)+" : "+str(e)
            print Exception,":",e


        if(params.has_key("onlytitle") and params["onlytitle"] == "true"):
            result = {
                'uuid':uuid,
                'status':status,
                'node':node,
                'httpstatus':httpstatus,
                'httpcontenttype':httpcontenttype,
                'title':title
            }
        else:
            result = {
                'uuid':uuid,
                'status':status,
                'node':node,
                'httpstatus':httpstatus,
                'httpcontenttype':httpcontenttype,
                'html':html,
            }

        self.logger.info('fetched source ' + url)
        return result