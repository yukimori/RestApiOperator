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

CONFIG_FILE = './settings.ini'
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

    def main(self):
        #Ctrl+Cを受け取った場合に例外keyboardInterruptを出さずに終了する
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            while True:
                print "---------------------------------"
                self.showApiSelection()
                self.showSelection(0,"reload IDs")
                print "\"q\" or Ctrl-c exits"
                print "---------------------------------"
                number = raw_input("select api number: ")
                print "---------------------------------"
                
                if number == "q":
                    print "%r exits..." % os.path.basename(__file__)
                    break
                if number == "0":
                    #設定ファイルの再読み込みが必要
                    print "READ config files..."
                    self.conf.read(CONFIG_FILE)
                    self.ids = self.readConfigIds()
                    continue
                if not number:
                    print "enter api number"
                    continue
                if not number.isdigit():
                    print "WARNING not number, enter api number"
                    continue
                if int(number)<0 or int(number)>len(self.api_select):
                    print "WARNING choose 'right' api number"
                    continue
                    
                self.request4SyncAPI(self.api_select[int(number)])

        except Exception,e:
            print "[ERROR] error occurs but reexecute..."
            self.main()

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
        print "%3d : %-32s" % (key, value)
        
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
            self.request_body = template_body.safe_substitute(self.ids)
        else: #request_bodyが指定されなかったときの情報
            self.request_body = ""
        #pathの構築と変数の整形
        if(self.conf.has_option(api_name,"path")):
            self.path = self.conf.get(api_name,"path")
            template_path = Template(self.path)
            self.path = template_path.safe_substitute(self.ids)
        else:
            self.path = ""

        if __debug__:
            print "======= Request Parameter BEGIN ======="
            self.showRequestParameter()
            print "======= Request Parameter END ========="

        response = self.connect(self.method, self.request_url,self.path,self.request_body,self.headers)
        print "========== Response BEGIN =========="
        print "HTTP STATUS:%s %s" % (response.status,response.reason)
        body = response.read()
        isFormatted = JsonUtil.printJsonFormatted(body)
        if not isFormatted:
            print "reponse body is not JSON:"
            print body
        print "========== Response END ============"


    def connect(self,method,url,path,body=None, headers={}):
        try:
            conn = httplib.HTTPConnection(url)

            conn.request(method, path, body, headers)
            response = conn.getresponse()

            return response
        except Exception,e:
            print e
            traceback.print_exc()

    def showRequestParameter(self):
        print "request_url:" + self.request_url
        print "headers:" + str(self.headers)
        if(self.request_body != "" or self.request_body is None):
            print "isJsonFormat(request_body)?:" + str(JsonUtil.validateJson(self.request_body))
        print "request_body:" + self.request_body

        print "path:" + self.path

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
            source = json.loads(source)
        print json.dumps(source,sort_keys=True, indent=4, separators=(',',': '))

        return True

if __name__ == '__main__':
            
#    rm = RestApiManager(host="10.14.41.121",port="80")
    rm = RestApiManager()
    rm.main()
