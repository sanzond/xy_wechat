import aiohttp

from .token_store import TokenStore


def check_response_error(response, error_code=0, error_msg_key='errmsg'):
    pass
    # if response['errcode'] != error_code:
    #     raise Exception(response[error_msg_key])


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

    async def refresh_token(self):
        """
        refresh token if it expires
        :return:
        """
        current_token = self.token_store.get()
        if not current_token:
            token = await self.get_token()
            self.token_store.save(token['token'], token['expires_in'])

    async def latest_token(self):
        """
        get latest token
        :return:
        """
        await self.refresh_token()
        return self.token_store.get()

    @staticmethod
    async def get_response(url, params=None):
        """
        get response from url
        :param url: url join with url_prefix
        :param params:
        :return:
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    @staticmethod
    async def post_response(url, data=None):
        """
        post response from url
        :param url: url join with url_prefix
        :param data:
        :return:
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.json()

    async def get_token(self):
        """
        get token from url
        :return:
        """
        response = await self.get_response(f'{self.url_prefix}gettoken', {
            'corpid': self.corp_id,
            'corpsecret': self.corp_secret
        })
        check_response_error(response)
        return {
            'token': response['access_token'],
            'expires_in': response['expires_in']
        }

    async def department_simplelist(self, id=None):
        response = await self.get_response(f'{self.url_prefix}department/simplelist', {
            'access_token': await self.latest_token(),
            'id': id or ''
        })
        check_response_error(response)
        return response['department_id']

    async def department_detail(self, id):
        if not id:
            raise Exception('id is required')
        response = await self.get_response(f'{self.url_prefix}department/get', {
            'access_token': await self.latest_token(),
            'id': id
        })
        check_response_error(response)
        return response['department']
