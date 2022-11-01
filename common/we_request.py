import requests

from .token_store import TokenStore


def check_response_error(response, error_code=0, error_msg_key='errmsg'):
    if response['errcode'] != error_code:
        raise Exception(response[error_msg_key])


class WeRequest(object):
    url_prefix = 'https://qyapi.weixin.qq.com/cgi-bin/'

    def __init__(self, corp_id, corp_secret):
        """
        set WE corp_id and corp_secret
        :param corp_id: WE app corp_id
        :param corp_secret: WE app corp_secret
        """
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.token_store = TokenStore(corp_secret)

    @staticmethod
    def get_response(url, params=None):
        """
        get response from url
        :param url: url join with url_prefix
        :param params:
        :return:
        """
        r = requests.get(url, params=params)
        return r.json()

    @staticmethod
    def post_response(url, data=None):
        """
        post response from url
        :param url: url join with url_prefix
        :param data:
        :return:
        """
        r = requests.post(url, json=data)
        return r.json()

    def get_token(self):
        """
        get token from url, token need save to token store
        :return:
        """
        response = self.get_response(f'{self.url_prefix}gettoken', {
            'corpid': self.corp_id,
            'corpsecret': self.corp_secret
        })
        check_response_error(response)
        token, expires_in = response['access_token'], response['expires_in']
        self.token_store.save(token, expires_in)
        return token

    def department_simplelist(self, token, id=None):
        response = self.get_response(f'{self.url_prefix}department/simplelist', {
            'access_token': token,
            'id': id
        })
        check_response_error(response)
        return response['department_id']
