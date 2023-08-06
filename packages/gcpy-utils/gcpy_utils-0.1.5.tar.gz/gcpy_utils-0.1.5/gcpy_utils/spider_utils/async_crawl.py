#coding:utf-8
# write  by  zhou
from celery import  Celery
import redis
import time
import hashlib
import urlparse


_app = Celery(broker="redis://192.168.14.40:6379/6")
_app.conf.task_ignore_result = True
_app.conf.task_queue_max_priority = 255
_redis_conn = redis.Redis('192.168.14.40',6379,6)


def _md5(str, hex=True):
    '获取字符串的md5校验'
    m = hashlib.md5()
    m.update(str)
    if hex == True:
        return m.hexdigest()
    else:
        return m.digest()


def _img_url_handle(img_url):
    try:
        _ = img_url.split(".")
        a, b = ".".join(_[:-1]), _[-1]
        if b.startswith("jpg"):
            return a + ".jpg"
        if b.startswith("jpeg"):
            return a + ".jpeg"
        if b.startswith("png"):
            return a + ".png"
        if b.startswith("gif"):
            return a + ".gif"
        if b.startswith("JPEG"):
            return a + ".JPEG"
        if b.startswith("JPG"):
            return a + ".JPG"
        raise Exception()
    except:
        return img_url


def crawl(url, charset="utf-8", post_data = None, headers = None, timeout = 10,
          save_hbase_name = None,save_hbase_column=None, save_hbase_rowkey=None, retries=3):
    '''
    异步抓取页面
    参数说明：
    url 所要采集的url
    charset 编码, utf-8或者 gbk  gb2312
    post_data post的数据
    headers   header头
    timeout   超时时间
    save_hbase_name 保存到hbase的表名
    save_hbase_column 保存到hbase的列名
    save_hbase_rowkey 保存到hbase的rowkey
    '''
    kwargs = locals()
    assert url.startswith("http")
    assert charset in ("utf-8","gbk","gb2312")
    if post_data!=None:
        assert isinstance(post_data,(str,unicode))
    if headers!=None:
        assert isinstance(headers,dict)
    timeout = int(timeout)
    assert timeout < 15
    if save_hbase_name:
        assert isinstance(save_hbase_name,(str,unicode))
    if save_hbase_column:
        assert isinstance(save_hbase_column,(str,unicode))
    if save_hbase_rowkey:
        assert isinstance(save_hbase_rowkey,(str,unicode))
    retries = int(retries)
    assert retries <= 15
    while 1:
        if _redis_conn.llen("rawhttp.html_spider") > 5000000:
            time.sleep(1)
        else:
            break
    kwargs["http_proxy"] = ["192.168.14.%s:3128"%i for i in range(120,126)]
    _app.send_task("rawhttp.html_spider.crawl", None, kwargs=kwargs,
                   queue="rawhttp.html_spider")


def crawl_by_adsl(url, charset="utf-8", post_data = None, headers = None, timeout = 10,
          save_hbase_name = None,save_hbase_column=None, save_hbase_rowkey=None, retries=3):
    '''
    通过adsl网络异步抓取页面
    参数说明：
    url 所要采集的url
    charset 编码, utf-8或者 gbk  gb2312
    post_data post的数据
    headers   header头
    timeout   超时时间
    save_hbase_name 保存到hbase的表名
    save_hbase_column 保存到hbase的列名
    save_hbase_rowkey 保存到hbase的rowkey
    '''
    kwargs = locals()
    assert url.startswith("http")
    assert charset in ("utf-8","gbk","gb2312")
    if post_data!=None:
        assert isinstance(post_data,(str,unicode))
    if headers!=None:
        assert isinstance(headers,dict)
    timeout = int(timeout)
    assert timeout < 15
    if save_hbase_name:
        assert isinstance(save_hbase_name,(str,unicode))
    if save_hbase_column:
        assert isinstance(save_hbase_column,(str,unicode))
    if save_hbase_rowkey:
        assert isinstance(save_hbase_rowkey,(str,unicode))
    retries = int(retries)
    assert retries <= 15
    while 1:
        if _redis_conn.llen("rawhttp.html_spider") > 5000000:
            time.sleep(1)
        else:
            break
    _app.send_task("rawhttp.html_spider.crawl_by_adsl", None, kwargs=kwargs,
                   queue="rawhttp.html_spider")


def crawl_gzip(url, charset="utf-8", post_data = None, headers = None, timeout = 10,
               save_hbase_name=None, save_hbase_column=None, save_hbase_rowkey=None, retries=3):
    '''
    异步抓取gzip压缩页面
    参数说明：
    url 所要采集的url
    charset 编码, utf-8或者 gbk  gb2312
    post_data post的数据
    headers   header头
    timeout   超时时间
    save_hbase_name 保存到hbase的表名
    save_hbase_column 保存到hbase的列名
    save_hbase_rowkey 保存到hbase的rowkey
    '''
    kwargs = locals()
    assert url.startswith("http")
    assert charset in ("utf-8","gbk","gb2312")
    if post_data!=None:
        assert isinstance(post_data,(str,unicode))
    if headers!=None:
        assert isinstance(headers,dict)
    timeout = int(timeout)
    assert timeout < 15
    if save_hbase_name:
        assert isinstance(save_hbase_name,(str,unicode))
    if save_hbase_column:
        assert isinstance(save_hbase_column,(str,unicode))
    if save_hbase_rowkey:
        assert isinstance(save_hbase_rowkey,(str,unicode))
    retries = int(retries)
    assert retries <= 15
    while 1:
        if _redis_conn.llen("rawhttp.html_spider") > 5000000:
            time.sleep(1)
        else:
            break
    kwargs["http_proxy"] = ["192.168.14.%s:3128"%i for i in range(120,126)]
    _app.send_task("rawhttp.html_spider.crawl_gzip", None, kwargs=kwargs,
                   queue="rawhttp.html_spider")


def crawl_gzip_by_adsl(url, charset="utf-8", post_data = None, headers = None, timeout = 10,
               save_hbase_name=None, save_hbase_column=None, save_hbase_rowkey=None, retries=3):
    '''
    通过adsl异步抓取gzip压缩页面
    参数说明：
    url 所要采集的url
    charset 编码, utf-8或者 gbk  gb2312
    post_data post的数据
    headers   header头
    timeout   超时时间
    save_hbase_name 保存到hbase的表名
    save_hbase_column 保存到hbase的列名
    save_hbase_rowkey 保存到hbase的rowkey
    '''
    kwargs = locals()
    assert url.startswith("http")
    assert charset in ("utf-8","gbk","gb2312")
    if post_data!=None:
        assert isinstance(post_data,(str,unicode))
    if headers!=None:
        assert isinstance(headers,dict)
    timeout = int(timeout)
    assert timeout < 15
    if save_hbase_name:
        assert isinstance(save_hbase_name,(str,unicode))
    if save_hbase_column:
        assert isinstance(save_hbase_column,(str,unicode))
    if save_hbase_rowkey:
        assert isinstance(save_hbase_rowkey,(str,unicode))
    retries = int(retries)
    assert retries <= 15
    while 1:
        if _redis_conn.llen("rawhttp.html_spider") > 5000000:
            time.sleep(1)
        else:
            break
    _app.send_task("rawhttp.html_spider.crawl_gzip_by_adsl", None, kwargs=kwargs,
                   queue="rawhttp.html_spider")