#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os
sys.path.append(os.pardir)
import json
from loggingUtil import LoggingUtil

logger=LoggingUtil

class CommonData():
    def __init__(self, data_filepath=None):
        self.data = {}
        if data_filepath is not None:
            self.restore_data(data_filepath)
            self.show()

    def save_data(self, data_filepath):
        data = json.dumps(self.data)

        with open(data_filepath, 'w') as f:
            f.write(data)
            f.flush()

    def restore_data(self, data_filepath):
        with open(data_filepath, 'r') as f:
            data = f.read()
        if (self.is_json(data)):
            self.data = json.loads(data)

    #値がリストである場合に対応する
    def add(self,key,value):
        #値がリストである場合は代入ではなくリストに追加する
        if key in self.data and isinstance(self.data[key],list):
            self.data[key].append(value)
        else:
            self.data[key] = value

    def delete(self,key):
        del(self.data[key])

    def push(self,source):
        for key in self.data.keys():
            if key in source:
                self.data[key] = source[key]

    def pull(self,target):
        for key in self.data.keys():
            if key in target:
                target[key] = self.data[key]
        return target

    def show(self):
        print "=== commondata ==="
        print json.dumps(self.data, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
        print "=== /commondata ==="

    def is_json(self,data):
        try:
            data = json.loads(data)
            return True
        except:
            return False

    def get_data(self):
        return self.data
