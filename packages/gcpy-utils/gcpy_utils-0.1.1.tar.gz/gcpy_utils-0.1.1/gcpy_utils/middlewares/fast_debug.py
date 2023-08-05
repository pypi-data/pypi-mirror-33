#coding:utf-8
# write  by  zhou
'''前后端快速调试'''
import os
from django.http import HttpResponse
from django.conf import  global_settings
import pyquery

with  os.path.join(os.path.dirname(__file__),"fastdebug.js") as _js_file:
    _js_content = _js_file.read()

class FastDebugMiddleware(object):
    def process_request(self,request):
        if request.path == "/fastdebug.js":
            return HttpResponse(_js_content,"application/javascript")


    def process_view(self):
        pass

    def process_response(self,request,response):
        if request.cookies.has_key("fastdebug"):
            fast_debug_host = response.cookies["fastdebug"]
            fast_debug_host = fast_debug_host.strip("/")
            if "text/html" in response.content_type and response.status_code == 200:
                try:
                    doc = pyquery.PyQuery(response.content)
                    for i in doc("link[rel='stylesheet']"):
                        _href = pyquery.PyQuery(i).attr("href")
                        if _href[0]=="/" and _href[1]!="/":
                            pyquery.PyQuery(i).attr("href","http://"+fast_debug_host+_href)
                    for s in doc("script[src]"):
                        _src = pyquery.PyQuery(s).attr("src")
                        if _src[0]=="/" and _src[1]!="/":
                            pyquery.PyQuery(s).attr("src","http://"+fast_debug_host+_src)
                    response.content = doc.html(method="html")
                except Exception as e :
                    print "fast_debug_middle:except ",str(e)
        return response