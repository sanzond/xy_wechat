# -*- coding: utf-8 -*-
import asyncio
import base64

from odoo import http
from odoo.http import route, request
from ..common.we_request import WeRequest
from ..models.res_users import ResUsers
from ..common.custom_encrypt import CustomEncrypt


class WechatEnterprise(http.Controller):

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

    @route('/we/qrcode', type='json', auth='public')
    def get_we_qrcode_info(self, app_id):
        app = request.env['wechat.enterprise.app'].sudo().browse(int(app_id))
        return {
            'agentid': app.agentid,
            'corp_id': app.corp_id
        }

    @route('/we/qrcode/login/<int:app_id>', type='http', auth='public')
    def login_by_we_qrcode(self, code, app_id):
        app = request.env['wechat.enterprise.app'].sudo().browse(int(app_id))
        we_request = WeRequest(app.corp_id, app.corp_secret)
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
                'password': CustomEncrypt.encrypt(ResUsers._we_auth_secret)
            }
            request.session.authenticate(request.session.db, employee.user_id.login, secret_dict)
            return request.redirect('/web')
