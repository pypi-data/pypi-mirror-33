#coding:utf-8
# write  by  zhou
import redis
import time
import json
import urllib2
import urllib

_app = None
_redis_conn = redis.Redis('192.168.14.40',6379,6)


def dataflow_push(dataset,key,data):
    '''
    数据流---推送
    :param dataset: 数据集的名称，str, 如： hy88_product
    :param key:     数据的key， str,  如：http://www.huangye88.com/xinxi/11.html
    :param data:    数据的内容， dict 如: {"cate1":11,"cate2":111,"url":"xxxxx"}
    :return: True
    True
    '''
    api_url = _redis_conn.get("dataflow-api-url")
    assert isinstance(dataset, (str, unicode))
    assert isinstance(key, (str, unicode))
    assert isinstance(data, dict)
    data = json.dumps(data)
    post_data = urllib.urlencode({"dataset": dataset, "key": key, "data": data, "secret": "gc7232275"})
    request = urllib2.Request(api_url)
    request.data = post_data
    response = urllib2.urlopen(request,timeout=3)
    result = response.read()
    result = json.loads(result)
    if result["status"] == True:
        return True
    else:
        raise Exception(result["message"])