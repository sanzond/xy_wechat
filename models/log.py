from odoo import models, fields


class WechatEnterpriseLog(models.Model):
    _name = 'wechat.enterprise.log'
    _description = 'Wechat Enterprise Log'
    _order = 'create_date desc'

    company_id = fields.Many2one('res.company', string='Company')
    we_app_id = fields.Many2one('wechat.enterprise.app', string='Wechat Enterprise App')
    detail = fields.Text(string='Detail')
