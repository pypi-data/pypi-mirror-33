#coding:utf-8
# write  by  zhou

import upyun
from django.db import  models
import upyun
from django.core.files.storage import Storage,FileSystemStorage
from django.utils.encoding import filepath_to_uri
import urlparse
import time
import  datetime
from django.core.files.base import ContentFile
import random
import time
from django.conf import  settings


class UpyunStorage(Storage):
    "upyun storage"

    def __init__(self,bucket_name,username,password,base_url):
        '''

        :param bucket_name: upyun的bucket_name
        :param username:    upyun的操作员账号
        :param password:    upyun的操作员密码
        :param base_url:    url前缀 比如： "https://upyun.gongchang.com"

        关于如何使用：
        比如相册相关的功能：
        class MyImage(models.Model):
            id = models.AutoField(primary_key=True)
            image = models.ImageField(max_length=100,upload_to="/media/userimgurl",
                                      storage=UpyunStorage("gongchang","admin","123456","https://image.gongchang.com")
                             )

        比如文件上传相关的功能：
        class MyFile(models.Model):
            id = models.AutoField(primary_key=True)
            file = models.FileField(max_length=100,upload_to="/media/userfiles",
                                      storage=UpyunStorage("gongchang","admin","123456","https://image.gongchang.com")
                             )

        '''
        self.up = upyun.UpYun(bucket_name, username, password, timeout=30,
                         endpoint=upyun.ED_AUTO)
        self.bask_url = base_url


    def _save(self, name, content):
        if  name[0] != '/':
            name = "/" + name
        try:
            res = self.up.put(name, content.read(), checksum=False)
            print res
        except Exception as e:
            raise
        return name

    def exists(self, name):
        try:
            self.up.getinfo(name)
        except Exception:
            return False
        return True

    def url(self, name):
        return self.bask_url+filepath_to_uri(name)

    def simple_upload(self,full_path_name,file_content):
        try:
            res = self.up.put(full_path_name, file_content, checksum=False)
            print res
        except Exception as e:
            raise
        return self.bask_url+filepath_to_uri(full_path_name)