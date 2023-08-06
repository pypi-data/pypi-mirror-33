#coding:utf-8
# write  by  zhou
# 获取 adsl 代理ip资源(代理均为高匿代理)
import redis


_redis_conn = redis.Redis("192.168.14.40",6379)


def get_proxy_list(dynamic=False):
    "获取代理IP列表"
    if not dynamic:
        return ["192.168.14.%s:3128"%i for i in range(120,126)]
    else:
        return [i[12:] + ":3128" for i in _redis_conn.keys("*") if i.startswith("adsl-centos")]
