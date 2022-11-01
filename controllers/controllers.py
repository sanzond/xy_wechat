# -*- coding: utf-8 -*-
# from odoo import http


# class EnterpriseWechat(http.Controller):
#     @http.route('/wechat_enterprise/wechat_enterprise', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wechat_enterprise/wechat_enterprise/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('wechat_enterprise.listing', {
#             'root': '/wechat_enterprise/wechat_enterprise',
#             'objects': http.request.env['wechat_enterprise.wechat_enterprise'].search([]),
#         })

#     @http.route('/wechat_enterprise/wechat_enterprise/objects/<model("wechat_enterprise.wechat_enterprise"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wechat_enterprise.object', {
#             'object': obj
#         })
