# -*- coding: utf-8 -*-
import asyncio
import base64
from urllib import parse

from odoo import http
from odoo.http import route, request
from ..common.we_request import we_request_instance
from ..models.res_users import ResUsers
from ..common.custom_encrypt import CustomEncrypt


class WechatEnterprise(http.Controller):
    scan_oauth_url = 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid={corp_id}&agentid={agentid}&redirect_uri={redirect_uri}'
    web_oauth_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={corp_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&agentid={agentid}#wechat_redirect'

    @http.route('/WW_verify_<string:filename>.txt', type='http', auth="none", methods=['GET'])
    def load_file(self, filename=None):
        """
        load verify file, easily to verify wechat enterprise redirect url
        :param filename:
        :return:
        """
        app = request.env['wechat.enterprise.app'].sudo().search(
            [('verify_txt_filename', '=', f'WW_verify_{filename}.txt')],
            limit=1
        )
        if len(app) == 0:
            content = None
        else:
            content = base64.b64decode(app[0].verify_txt).decode('utf-8')
        return content

    @route('/we/oauth2/info', type='json', auth='public')
    def get_we_oauth2_info(self, app_id, redirect_uri=None):
        """
        get info for build Wechat Enterprise QRCode to login
        :param app_id:
        :param redirect_uri: redirect url after login, don't need host
        :return:
        """
        app = request.env['wechat.enterprise.app'].sudo().browse(int(app_id))
        host = request.httprequest.host_url
        return {
            'agentid': app.agentid,
            'corp_id': app.corp_id,
            'redirect_uri': parse.urljoin(host, f'we/oauth2/login/{app_id}') if redirect_uri is None else parse.urljoin(
                host, redirect_uri)
        }

    @route('/we/oauth2/login/<int:app_id>', type='http', auth='public')
    def login_by_oauth2(self, code, app_id):
        """
        login by wechat enterprise oauth2
        :param code:
        :param app_id:
        :return:
        """
        app = request.env['wechat.enterprise.app'].sudo().browse(int(app_id))
        we_request = we_request_instance(app.corp_id, app.secret)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        get_userid_task = loop.create_task(we_request.get_userid(code))
        loop.run_until_complete(get_userid_task)
        loop.close()
        we_id = get_userid_task.result()
        employee = request.env['hr.employee'].sudo().search([('we_id', '=', we_id)])
        if employee.user_id.id:
            secret_dict = {
                'npa': True,
                'type': 'we',
                'password': CustomEncrypt.encrypt(ResUsers.we_auth_secret)
            }
            request.session.authenticate(request.session.db, employee.user_id.login, secret_dict)
            return request.redirect('/web')

    @route('/we/oauth2/build/<string:oauth_type>/<int:app_id>', type='http', auth='public')
    def we_oauth2(self, oauth_type, app_id, scope='snsapi_base'):
        """
        build wechat enterprise oauth2 url
        :param oauth_type: scan or web, scan is build to qrcode, web is build to redirect url
        :param app_id: authenticate used app id
        :param scope: snsapi_base or snsapi_privateinfo
        :return:
        """
        oauth2_info = self.get_we_oauth2_info(app_id)
        corp_id = oauth2_info['corp_id']
        agentid = oauth2_info['agentid']
        redirect_uri = parse.quote(oauth2_info['redirect_uri'])

        _redirect_uri = ''
        if oauth_type == 'scan':
            _redirect_uri = WechatEnterprise.scan_oauth_url.format(
                corp_id=corp_id,
                agentid=agentid,
                redirect_uri=redirect_uri
            )
        elif oauth_type == 'web':
            _redirect_uri = WechatEnterprise.web_oauth_url.format(
                corp_id=corp_id,
                agentid=agentid,
                redirect_uri=redirect_uri,
                scope=scope
            )
        return request.redirect(_redirect_uri, 303, False)
