import time

token_temp = {}


class TokenStore(object):
    def __init__(self, secret):
        """
        secret is used to distinguish different WE apps
        :param secret: 
        """
        self.secret = secret

    def save(self, token, expires_in, create_time=None):
        """
        save token
        :param token: token
        :param expires_in: how long the token is valid, unit is second
        :param create_time: if create_time is None, use current time
        :return:
        """
        current_time = time.time()
        token_temp[self.secret] = {
            'token': token,
            'expires_in': expires_in,
            'update_time': current_time,
            'create_time': create_time or current_time
        }

    def get(self):
        """
        if token is expires, clear it and return None
        :return:
        """
        if self.secret in token_temp:
            token = token_temp[self.secret]
            if time.time() - token['update_time'] > token['expires_in']:
                token_temp.pop(self.secret)
                return None
            return token['token']
        return None

    def refresh(self, expires_in):
        """
        refresh token if it exists
        :param expires_in: how long the token is valid, unit is second
        :return:
        """
        if self.secret in token_temp:
            token_dict = token_temp[self.secret]
            self.save(token_dict['token'], expires_in, token_dict['create_time'])

    @staticmethod
    def clean(secret):
        """
        clean token by secret
        :param secret: string
        :return:
        """
        if secret in token_temp:
            token_temp.pop(secret)

    @staticmethod
    def clean_all():
        """
        clean all token
        :return: 
        """
        for key in token_temp:
            token_temp.pop(key)
