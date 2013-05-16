#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import traceback
import json
import ConfigParser
import signal
import sys
import os
from string import Template
import httpUtil
from commondata import CommonData
from loggingUtil import LoggingUtil

CONFIG_FILE = os.path.dirname(os.path.abspath(__file__)) + "/settings.ini"
PER_COMMONDATA = os.path.dirname(os.path.abspath(__file__)) + "/commondata.json"
logger=LoggingUtil

#python -O hoge.pyと実行するとfalseになる
if __debug__:
    print "isDebug:" + str(__debug__)

class RestApiManager():
    def __init__(self, host=None, port=None, header=None):

        #設定ファイルの読み込み
        self.conf = ConfigParser.RawConfigParser()
        #itemsを使うとオプション名が小文字に変換されてしまうため
        self.conf.optionxform = str
        self.conf.read(CONFIG_FILE)

        #api_nameをセクション名のリストから構築する
        self.api_select = self.readConfigApis()

#        if __debug__:
#            print "api_select:" + str(self.api_select) 

        #ID情報を読み込む
        self.ids = self.readConfigIds()

        #クライアントの設定
        self.setConfigClient()

        #コンストラクタの引数で設定された場合はそれが優先される
        if not host is None:
            self.host = host
        if not port is None:
            self.port = str(port)
            
        #リクエストURLはホストとポートから作成する
        self.request_url = self.host + ":" + self.port

        if __debug__:
            print "url:" + self.request_url
            print "header:" + str(self.headers)

        #commondataの生成
        self.common = CommonData(PER_COMMONDATA)

    def set_config(self):
        #設定ファイルの読み込み
        self.conf = ConfigParser.RawConfigParser()
        #itemsを使うとオプション名が小文字に変換されてしまうため
        self.conf.optionxform = str

        self.conf.read(CONFIG_FILE)

        #api_nameをセクション名のリストから構築する
        self.api_select = self.readConfigApis()

        #ID情報を読み込む
        self.ids = self.readConfigIds()

        #クライアントの設定
        self.setConfigClient()

        #リクエストURLはホストとポートから作成する
        self.request_url = self.host + ":" + self.port

        if __debug__:
            print "url:" + self.request_url
            print "header:" + str(self.headers)
        

    def main(self):
        #Ctrl+Cを受け取った場合に例外keyboardInterruptを出さずに終了する
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            while True:
                print "---------------------------------"
                self.showApiSelection()
                self.showSelection("r","restart(reload config)")
                self.showSelection("a","add commondata")
                self.showSelection("s","set commondata from response")
                self.showSelection("q","quit")
                print "---------------------------------"
                number = raw_input("select:")
                print "---------------------------------"
                
                if number == "q":
                    print "%r exits..." % os.path.basename(__file__)
                    break
                if number == "a":
                    print "add commondata..."
                    self.set_commondata_from_stdin()
                    continue
                if number == "s":
                    print "set commondata from response..."
                    self.set_commondata_from_response()
                    continue
                if number == "r":
                    #設定ファイルの再読み込み
                    self.set_config()
                    continue
                if not number:
                    print "[WARNING] wrong select"
                    continue
                if not number.isdigit():
                    print "[WARNING] not number, enter api number"
                    continue
                if int(number)<0 or int(number)>len(self.api_select):
                    print "WARNING choose 'right' api number"
                    continue
                    
                self.api_name = self.api_select[int(number)]
                logger.info("execute api:%s",self.api_name)
                self.request4SyncAPI(self.api_name)

            self.before_finish()

        except Exception,e:
            print e
            traceback.print_exc()

            logger.error("[ERROR] some error occurs, but rerun this program...")

            self.main()

    #前のAPI呼び出しのresponseからcommondataに設定する
    def set_commondata_from_response(self):
        print "response key(oldkey):commondada key(newkey)"
        line = sys.stdin.readline()
        line = line.rstrip()
        data = line.split(":")
        response_entity = json.loads(self.response["entity"])
        if(response_entity.has_key(data[0])):
            self.common.add(data[1],response_entity[data[0]])
        else:
            logger.info("%s not exist in response",data[0])
        self.common.show()

    #標準入力からcommondataを設定する
    def set_commondata_from_stdin(self):
        print "key:value:type(str|int|float)"
        line = sys.stdin.readline()
        line = line.rstrip()
        data = line.split(":")
        if data[2] == "int":
            self.common.add(data[0],int(data[1]))
        elif data[2] == "long":
            self.common.add(data[0],long(data[1]))
        else:
            self.common.add(data[0],data[1])
        self.common.show()

    #終了処理を実行する
    def before_finish(self):
        self.common.save_data(PER_COMMONDATA)

    #コンフィグから値を読み取るだけでインスタンス変数に設定しないのでread
    def readConfigApis(self):
        api_select = {}
        api_names = self.conf.sections()
        api_names.sort()
        for api_name in api_names:
            if api_name == "id":
                continue
            if api_name == "client_config":
                continue
            api_select[len(api_select)+1] = api_name
        return api_select

    def setConfigClient(self):
        self.host = self.conf.get("client_config", "host")
        self.port = str(self.conf.get("client_config", "port"))
        header = self.conf.get("client_config","header")
        header = header.replace('\\','')
        #jsonであることを想定してエンコードする
        self.headers = json.loads(header)

    #コンフィグから値を読み取るだけでインスタンス変数に設定しないので、メソッド名をreadとする
    def readConfigIds(self):
        ids = self.conf.items("id")
        ids = dict(ids)
        if __debug__:
#            isFormatted = JsonUtil.printJsonFormatted(ids)
            print "id:" + str(ids)
        return ids

    def showApiSelection(self):
        for number in sorted(self.api_select.keys()):
            print "%3d : %-32s" % (number, self.api_select[number])

    def showIds(self):
        for id in sorted(self.ids.keys()):
            print "%-32s : %-64s" % (id, self.ids[id])
    
    def showSelection(self,key,value):
        if not isinstance(key,str):
            key = str(key)
        print "%3s : %-32s" % (key, value)
        
    def setHeaders(self,headers):
        self.headers = headers

    def request4SyncAPI(self, api_name):
        self.method = self.conf.get(api_name, "method")
        #request_bodyの構築と変数の整形
        if(self.conf.has_option(api_name,"request_body")):
            self.request_body = self.conf.get(api_name, "request_body")
            #reqeust bodyの整形
            self.request_body = self.request_body.replace('\\','')
            template_body = Template(self.request_body) #Temaplateによる識別子の変換
            self.request_body = template_body.safe_substitute(self.common.get_data())
            #commondataによる変換
            request_body_obj = json.loads(self.request_body)
            self.request_body = json.dumps(self.common.pull(request_body_obj))
        else: #request_bodyが指定されなかったときの情報
            self.request_body = ""
        #pathの構築と変数の整形
        if(self.conf.has_option(api_name,"path")):
            self.path = self.conf.get(api_name,"path")
            template_path = Template(self.path)
            self.path = template_path.safe_substitute(self.ids)
        else:
            self.path = ""

        self.showRequest()

        self.response = self.connect(self.method, self.request_url,self.path,self.request_body,self.headers)
        self.showResponse(self.response)
        
        #commondataへのデータの引き継ぎ
        self.push_commondata(json.loads(self.response["entity"]))
        self.common.show()

    #レスポンスからcommonデータへの引き継ぎ
    #sourceはオブジェクトで渡すこと
    def push_commondata(self,source):
        if self.conf.has_option(self.api_name,"commondata_push"):
            rule = self.conf.get(self.api_name,"commondata_push")

            rule = json.loads(rule)

            for key,afterkey in rule.items():
                if not key in source:
                    logger.info("%s not exist in response",key)
                    continue
                self.common.add(afterkey,source[key])

    def connect(self,method,url,path,body=None, headers={}):
        try:
#            conn = httplib.HTTPConnection(url)
#            conn.request(method, path, body, headers)
#            response = conn.getresponse()
            
            if(self.conf.has_option("client_config","proxy_url") and 
               self.conf.has_option("client_config","proxy_port")):
                self.proxy_url = self.conf.get("client_config", "proxy_url")
                self.proxy_port = self.conf.get("client_config", "proxy_port")
                response = httpUtil.request_with_httpproxy(self.proxy_url,
                                                       self.proxy_port,
                                                       url, method, 
                                                       path, body, headers)
            else:
                response = httpUtil.httpRequest2(url, method, path, body, headers)

            return response
        except Exception,e:
            print e
            traceback.print_exc()

    def showResponse(self,response):
        print ""
        logger.info("========= Response =========")
        status = response["status"]
        reason = response["reason"]
        logger.info("HTTP STATUS:%s %s" % (status,reason))
        body = response["entity"]
        logger.info("response_body:%s",body)
        isFormatted = JsonUtil.printJsonFormatted(body)
        if not isFormatted:
            logger.info("reponse body is not JSON:")
            logger.info(body)
        else:
            logger.info(json.dumps(json.loads(body),sort_keys=True, indent=4, separators=(',',': ')))
        logger.info("======== /Response =========")
        print ""

    def showRequest(self):
        print ""
        logger.info("========= Request ==========")
        logger.info("url:" + self.request_url)
        logger.info("path:" + self.path)
        logger.info("headers:" + str(self.headers))
        logger.info("request_body:" + self.request_body)
        if(self.request_body != "" or self.request_body is not None):
            logger.debug("isJsonFormat(request_body)?:" + str(JsonUtil.validateJson(self.request_body)))
        logger.info(json.dumps(json.loads(self.request_body),sort_keys=True, indent=4, separators=(',',': ')))
        logger.info("======== /Request ==========")
        print ""

class JsonUtil():

    @classmethod
    def validateJson(self,source):
        try :
            srcObj = json.loads(source)
            return True
        except Exception as e:
            print "EXCEPTION type:" + str(type(e))
            print "EXCEPTION args:" + str(e.args)
#            print "message:" + e.message
            print "EXCEPTION e:" + str(e)
            return False
    

    @classmethod
    def printJsonFormatted(self,source):
        if source is None:
            return False
        if isinstance(source, str):
            if not (source == "" or source.startswith("{")):
                return False
#            source = json.loads(source)
#        print json.dumps(source,sort_keys=True, indent=4, separators=(',',': '))

        return True

if __name__ == '__main__':
            
#    rm = RestApiManager(host="10.14.41.121",port="80")
    rm = RestApiManager()
    rm.main()