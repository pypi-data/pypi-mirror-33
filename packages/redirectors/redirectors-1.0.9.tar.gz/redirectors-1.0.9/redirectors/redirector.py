# -*- coding: utf-8 -*-

import hashlib
import json
import urllib


class BaseRedirector(object):
    def base_calculate_sign(self, signstr):
        return hashlib.md5(signstr).hexdigest()


class EgretRedirector(BaseRedirector):
    def calculate_signature(self, chanId=None, appKey=None, userid=None, **kwargs):
        signstr = 'chanId={chanId}&userid={userid}&{appKey}'.format(
            chanId=chanId,
            userid=userid,
            appKey=appKey
        )
        for k in sorted(kwargs):
            signstr += '&{0}={1}'.format(k, kwargs[k])
        return self.base_calculate_sign(signstr)

    def fill_signature(self, chanId=None, appKey=None, userid=None, sign=None, **kwargs):
        sign = self.calculate_signature(chanId=chanId, appKey=appKey, userid=userid, **kwargs)
        return dict(kwargs, **{
            'chanId': chanId,
            'userid': userid,
            'sign': sign,
        })

    def check_signature(self, chanId=None, appKey=None, userid=None, sign=None, **kwargs):
        return self.calculate_signature(chanId=chanId, appKey=appKey, userid=userid, **kwargs) == sign

    def login_url(self, chanId=None, appKey=None, login_url=None, userid=None, username=None, avatar=None, sex=None, sign=None, **kwargs):
        params = {
            'userid': userid,
            'username': username,
            'avatar': avatar,
            'sex': sex,
            'chanId': chanId,
            'sign': sign or self.calculate_signature(chanId=chanId, appKey=appKey, userid=userid, **kwargs),
            'params': json.dumps(kwargs)
        }
        return '{login_url}?{params}'.format(login_url=login_url, params=urllib.urlencode(params))


compet = egret = EgretRedirector()
