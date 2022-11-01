from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    app_ids = fields.One2many('wechat.enterprise.app', 'company_id', string='Apps')
