from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    we_corp_id = fields.Char(string='Corp ID', required=True, default='Wechat Enterprise corp id')
    app_ids = fields.One2many('wechat.enterprise.app', 'company_id', string='Apps')
