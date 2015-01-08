# Copyright 2014 Andrew Melton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from datetime import datetime
from datetime import timedelta
import json
import ssl

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

VERSION = '0.0.4'
USER_AGENT = 'Burrow/{}'.format(VERSION)
LOGIN_URL = 'https://home.nest.com/user/login'


class TLSV1Adapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


class BurrowConfig(object):
    def __init__(self, location, config=None):
        self.location = location

        if config:
            self.config = config
        else:
            self.config = self._load(location)

    @staticmethod
    def _load(location):
        with open(location, 'r') as fp:
            return json.load(fp)

    def _save(self):
        with open(self.location, 'w') as fp:
            return json.dump(self.config, fp)

    def update(self, userid, token, expires_in, transport_url):
        self.config['userid'] = userid
        self.config['access_token'] = token
        self.config['expires_in'] = expires_in
        self.config['transport_url'] = transport_url
        self._save()

    @property
    def user(self):
        return 'user.{}'.format(self.userid)

    @property
    def has_token(self):
        return 'access_token' in self.config

    @property
    def expires_in(self):
        expires_in = self.config['expires_in']
        return datetime.strptime(expires_in, '%a, %d-%b-%Y %H:%M:%S %Z')

    @property
    def expires_soon(self):
        return self.expires_in - datetime.utcnow() < timedelta(days=1)

    def __getattr__(self, item):
        return self.config[item]


class NestClient():
    def __init__(self, config):
        self.session = requests.session()
        self.session.mount('https://', TLSV1Adapter())
        self.config = config
        if (not self.config.has_token or
                (self.config.has_token and self.config.expires_soon)):
            self._login()

    def _login(self):
        creds = dict(username=self.config.username,
                     password=self.config.password)
        headers = {'user-agent': USER_AGENT}
        resp = requests.post(LOGIN_URL, data=creds, headers=headers)
        login_dict = resp.json()
        self.config.update(login_dict['userid'],
                           login_dict['access_token'],
                           login_dict['expires_in'],
                           login_dict['urls']['transport_url'])

    def _session_get(self, path):
        headers = {
            'user-agent': USER_AGENT,
            'X-nl-user-id': self.config.userid,
            'Authorization': 'Basic {}'.format(self.config.access_token),
        }
        url = '{}{}'.format(self.config.transport_url, path)
        return self.session.get(url, headers=headers).json()

    def _get(self, path):
        resp = self._session_get(path)
        if 'cmd' in resp and resp['cmd'] == 'REINIT_STATE':
            # NOTE(ramielrowe) - API is telling us to re-login
            self._login()
            resp = self._session_get(path)
        return resp

    def get_stats(self):
        return self._get('/v2/mobile/{}'.format(self.config.user))


def main():
    parser = argparse.ArgumentParser('Burrow')
    parser.add_argument('config_path', type=str)
    args = parser.parse_args()

    config = BurrowConfig(args.config_path)
    client = NestClient(config)

    print(json.dumps(client.get_stats()))


if __name__ == '__main__':
    main()
