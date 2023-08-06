import json
import requests
import logging
import time
import hashlib
import random
import string

API_URL = 'https://api.2808proxy.com'

logger = logging.getLogger(__file__)


class Client(object):
    def __init__(self, username=None, password=None, token_change_on_login=False, enhanced_auth=False):
        """
        2808 proxy client class
        :param username: username
        :param password: password
        :param token_change_on_login: if change the token when re-register,default is False
        :param enhanced_auth: whether open authentication,default is False
        """
        self.username = username
        self.password = password
        self.token = None
        self.enhanced_auth = False
        self.token_change_on_login = False
        self.__get_token()

    def get_proxies(self, amount=1, expire_seconds=None):
        """
        get http/socks5 proxy address
        :param amount: The number of IP extracted
        :param expire_seconds: Expiration time (seconds)
        :return: data list,for instance [{'id': 'qwe', 'http_port': 6666, 'ip': '192.168.1.10', 's5_port': 2081},
                                        {'id': 'wer', 'http_port': 6666, 'ip': '192.168.1.11', 's5_port': 2081}]
        """
        url = API_URL + '/proxy/get'
        params = {'amount': amount, 'expire': expire_seconds}
        jso = self.__handle_request(url, self.__build_auth_params(params))
        return jso

    def release_proxy(self, proxy):
        """
        release proxy
        :param proxy: data dict, for instance {'id': 'qwe', 'http_port': 6666, 'ip': '192.168.1.10', 's5_port': 2081}
        :return: response whether release success
        """
        url = API_URL + '/proxy/release'
        params = {'id': proxy['id']}
        jso = self.__handle_request(url, self.__build_auth_params(params))
        return jso

    def list_proxies(self):
        url = API_URL + '/proxy/list'
        params = {}
        jso = self.__handle_request(url, self.__build_auth_params(params))
        return jso

    def release_proxies(self, proxies):
        if isinstance(proxies, list):
            for p in proxies:
                self.release_proxy(p)
        else:
            self.release_proxy(proxies)

    def release_all(self):
        self.release_proxies(self.list_proxies())

    def __get_token(self):
        if self.password is None:
            logger.warning("cannot login without password.")
            return
        url = API_URL + "/login"
        params = {'username': self.username, 'password': self.password, 'change_token': self.token_change_on_login}
        login_resp = self.__handle_request(url, params)
        self.token = login_resp['token']
        logger.info("connect to 2808 successful, token is :" + self.token)

    def __build_auth_params(self, params):
        if not self.enhanced_auth:
            params['token'] = self.token
        else:
            ts = int(time.time())
            nonce = ''.join(random.sample(string.ascii_letters + string.digits, 32))
            params['username'] = self.username
            params['timestamp'] = ts
            params['nonce'] = nonce
            params['sign'] = hashlib.md5((str(ts) + self.token + nonce).encode(encoding='utf-8')).hexdigest()
        return params

    @staticmethod
    def __handle_request(url, params=None):
        logger.info("Request URL:" + url)
        logger.info("Request params:" + str(params))
        resp = requests.get(url, params=params)
        rsp = json.loads(resp.text)
        logger.info("response json:{}".format(rsp))
        if rsp["status"] != 0:
            raise Exception(rsp['msg'])
        return rsp['data']
