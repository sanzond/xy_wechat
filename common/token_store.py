import time

token_temp = {}


class TokenStore(object):
    def __init__(self, corp_secret):
        """
        corp_secret is used to distinguish different WE apps
        :param corp_secret: 
        """
        self.corp_secret = corp_secret

    def save(self, token, expires_in, create_time=None):
        """
        save token
        :param token: token
        :param expires_in: how long the token is valid, unit is second
        :param create_time: if create_time is None, use current time
        :return:
        """
        token_temp[self.corp_secret] = {
            'token': token,
            'expires_in': expires_in,
            'create_time': create_time or time.time()
        }

    def get(self):
        """
        if token is expires, clear it and return None
        :return:
        """
        if self.corp_secret in token_temp:
            token = token_temp[self.corp_secret]
            if time.time() - token['create_time'] > token['expires_in']:
                token_temp.pop(self.corp_secret)
                return None
            return token['token']
        return None

    def refresh(self, expires_in):
        """
        refresh token if it exists
        :param expires_in: how long the token is valid, unit is second
        :return:
        """
        if self.corp_secret in token_temp:
            token_dict = token_temp[self.corp_secret]
            self.save(token_dict['token'], expires_in, token_dict['create_time'])

    @staticmethod
    def clean(corp_secret):
        """
        clean token by corp_secret
        :param corp_secret: string
        :return:
        """
        if corp_secret in token_temp:
            token_temp.pop(corp_secret)

    @staticmethod
    def clean_all():
        """
        clean all token
        :return: 
        """
        for key in token_temp:
            token_temp.pop(key)
