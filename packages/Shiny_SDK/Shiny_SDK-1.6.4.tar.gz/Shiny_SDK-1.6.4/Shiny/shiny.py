# !/usr/bin/env python

# -*- coding:utf-8 -*-
# Shiny Python SDK
import collections
import hashlib
import json

import requests


def md5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def sha1(text):
    m = hashlib.sha1()
    m.update(text)
    return m.hexdigest()

def throw_error(response):
    try:
        error = json.loads(response.text)
    except Exception as e:
        raise ShinyError('Network error: ' + str(response.status_code))
    raise ShinyError(
        'Shiny error: ' + str(error['error']['info']), code=str(error['error']['code']))


class ShinyError(Exception):
    def __init__(self, message, code='unknown_error'):
        self.message = message
        self.code = code


class Shiny:
    def __init__(self, api_key, api_secret_key, api_host='https://shiny.kotori.moe', spider_version='1.0'):
        self.API_KEY = api_key
        self.API_SECRET_KEY = api_secret_key
        self.API_HOST = api_host
        self.SPIDER_VERSION = spider_version

    def sign(self, payload={}):
        """ API 请求签名 """
        data = self.API_KEY + self.API_SECRET_KEY
        for key in sorted(payload.keys()):
            data += str(payload[key])
        return sha1(data.encode('utf-8'))

    def add(self, spider_name, level, data=None, hash=False):
        """添加数据项"""
        if data is None:
            data = {}

        url = self.API_HOST + '/Data/add'

        payload = {"api_key": self.API_KEY}

        event = {"level": int(level), "spiderName": spider_name}

        # 如果没有手动指定Hash，将会把data做一次md5生成hash
        try:
            if hash:
                event["hash"] = str(hash)
            else:
                event["hash"] = md5(json.dumps(collections.OrderedDict(
                    sorted(data.items()))).encode('utf-8'))
        except Exception as e:
            raise ShinyError('Fail to generate hash')

        event["data"] = data

        payload["sign"] = sha1(
            (self.API_KEY + self.API_SECRET_KEY + json.dumps(event)).encode('utf-8'))

        payload["event"] = json.dumps(event)

        response = requests.post(url, payload)

        if response.status_code != 200:
            throw_error(response)
        else:
            return json.loads(response.text)

    def add_many(self, events):
        """添加多个事件"""
        payload = {}
        url = self.API_HOST + '/Data/add'
        for event in events:
            if 'hash' not in event:
                if 'data' in event:
                    if 'hash' in event['data']:
                        event['hash'] = event['data']['hash']
                        event['data'].pop('hash')
                    else:
                        event['hash'] = md5(json.dumps(collections.OrderedDict(
                            sorted(event['data'].items()))).encode('utf-8'))
                else:
                    raise ShinyError('Missing data in some events')
            if 'level' not in event or 'spiderName' not in event:
                raise ShinyError('Missing parameters.')
            event['level'] = int(event['level'])

        payload["event"] = json.dumps(events)

        sign = self.sign(payload)

        payload["sign"] = sign
        payload["api_key"] = self.API_KEY

        response = requests.post(url, payload)

        if response.status_code != 200:
            throw_error(response)
        else:
            return json.loads(response.text)

    def recent(self):
        """获取最新项目"""
        url = self.API_HOST + '/Data/recent'
        response = requests.get(url)
        if response.status_code != 200:
            throw_error(response)
        return json.loads(response.text)

    def get_jobs(self):
        """获得任务列表"""
        url = self.API_HOST + \
            '/Job/query?api_key={}&sign={}'.format(self.API_KEY, self.sign())
        response = requests.get(url, headers={
            'X-SHINY-SPIDER-VERSION': self.SPIDER_VERSION
        })
        if response.status_code != 200:
            throw_error(response)
        return json.loads(response.text)

    def report(self, job_id, status):
        """回报任务状态"""
        url = self.API_HOST + '/Job/report'
        payload = {
            "jobId": job_id,
            "status": status
        }
        sign = self.sign(payload)
        payload["api_key"] = self.API_KEY
        payload["sign"] = sign
        response = requests.post(url, payload)
        if response.status_code != 200:
            throw_error(response)
        else:
            return response.json()
