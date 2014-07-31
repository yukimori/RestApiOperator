#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2013 Nippon Telegraph and Telephone Corporation.
# All rights reserved.

import json
import httplib
import urllib
import urllib2

from functools import partial

# HTTPリクエスト
def httpRequest(host, method, path, params, headers):

    conn = httplib.HTTPConnection( host )
    conn.request(method, path, params, headers)
    res = conn.getresponse()

    # HTTPレスポンスパース
    result = {}
    result["status"] = res.status
    result["reason"] = res.reason
    result["entity"] = res.read()
    conn.close()

    return result

def httpRequest2(host, method, path, params, headers):

#    proxy = {}
#    proxy_handler = urllib2.ProxyHandler(proxy)
#    opener = urllib2.build_opener(proxy_handler)
#    urllib2.install_opener(opener)
#    
    hh = urllib2.HTTPHandler(debuglevel=1)
    opener = urllib2.build_opener(hh)
    urllib2.install_opener(opener)
    return request("http", host, method, path, params, headers)

def request_with_httpproxy(proxy_url,proxy_port,host,method,path,params,headers):
    proxy = {'http' : proxy_url+':'+proxy_port+'/'}
    proxy_handler = urllib2.ProxyHandler(proxy)

    http_handler = urllib2.HTTPHandler(debuglevel=1)
    opener = urllib2.build_opener(proxy_handler, http_handler)
    urllib2.install_opener(opener)
    
    return request("http", host, method, path, params, headers)

def request(protocol,host, method, path, body, headers):

#    print "body:" + body

    uri = protocol+"://"+host+path
    request = urllib2.Request(uri, body, headers)
    request.get_method = lambda: method

    res = urllib2.urlopen(request)

    result = {}
    result["status"] = res.getcode()
    result["reason"] = res.msg
    result["entity"] = res.read()

    return result
    

def postRequest(host, path, params, headers):
    return httpRequest(host, "POST", path, params, headers)


def showResult(result):
    print ""
    print "========= Resutl ========="
    status = result["status"]
    reason = result["reason"]
    print "HTTP STATUS:%s %s" % (status,reason)
    body = result["entity"]
    isFormatted = JsonUtil.printJsonFormatted(body)
    if not isFormatted:
        print "reponse body is not JSON:"
        print body
    print "======== /Result ========="
    print ""
