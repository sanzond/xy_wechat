# -*- coding: utf-8 -*-
import asyncio

from odoo import http
from odoo.http import route, request
from ..common.we_request import WeRequest


class WechatEnterprise(http.Controller):

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
        # todo: login without password
        return request.redirect('/web')
