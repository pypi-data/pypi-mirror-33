#coding:utf-8
# write  by  zhou
import datetime
import urllib2
import base64
import redis


_app = None
_redis_conn = redis.Redis('192.168.14.40',6379,6)


def up_to_upyun(key,content):
    '''上传图片到又拍云
    参数说明：
    key      保存到又拍云的路径 比如 /test/my.jpg
    content  文件的内容
    返回值：
    返回一个路径：
    比如：//imgse.cn.gcimg.net/test/my.jpg
    '''
    key = str(key)
    gmt = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    gmt = str(gmt)
    request = urllib2.Request("https://v0.api.upyun.com/gcseoimg%s"%key)
    request.add_header("Date",gmt)
    request.add_header('Authorization','Basic %s'%(str(base64.b64encode(":".join(_redis_conn.get("upyun-config")
                                                                                 .split("|"))))))
    request.add_header("Content-Length",'%s'%len(content))
    request.add_data(content)
    urllib2.urlopen(request)
    return "//imgse.cn.gcimg.net" + key