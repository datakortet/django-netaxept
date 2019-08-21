# -*- coding: utf-8 -*-
import os


class Credentials(object):
    def __init__(self, merchantid, token, rest_url):
        self._merchantid = merchantid
        self._token = token
        self.rest_query = rest_url + 'Query.aspx'
        self.rest_process = rest_url + 'Process.aspx'
        self.rest_register = rest_url + 'Register.aspx'

    @property
    def token(self):
        return self._token

    @property
    def merchantid(self):
        return self._merchantid


class EnvironmentCredentials(Credentials):
    def __init__(self, merchantid, token):
        super(EnvironmentCredentials, self).__init__(merchantid, token)

    @property
    def token(self):
        return os.environ[self._token]

    @property
    def merchantid(self):
        return os.environ[self._merchantid]
