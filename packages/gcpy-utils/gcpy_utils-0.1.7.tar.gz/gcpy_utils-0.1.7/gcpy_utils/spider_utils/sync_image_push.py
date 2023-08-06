#coding:utf-8
# write  by  zhou
from celery import  Celery
import redis
import time
import hashlib
import urlparse
import urllib2
import urllib
from .. import  upyun


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


def image_push(page_url,img_url):
    '''图片推送到又拍云
    这是一个同步调用
    参数说明：
    page_url    图片所属页面的url
    img_url     图片的url
    返回值说明：
    new_url 图片转移到又拍云之后的新的地址,比如： //imgse.cn.gcim.net/test/a.jpg
    '''

    img_url = urlparse.urljoin(page_url.strip(), img_url.strip())
    request = urllib2.Request(img_url)
    request.add_header("User-Agent","Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X)\
     AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1")
    content = urllib2.urlopen(request,timeout=5).read()
    img_url = _img_url_handle(img_url)
    url_md5 = _md5(img_url)
    _ = urlparse.urlparse(img_url)
    img_url_path = _.path + _.query
    if "." in img_url_path:
        save_path = "/%s/%s/%s"%(url_md5[:4],url_md5[4:8],url_md5) + "." + img_url_path.split(".")[-1]
    else:
        save_path = "/%s/%s/%s"%(url_md5[:4],url_md5[4:8],url_md5)
    return upyun.up_to_upyun(save_path,content)