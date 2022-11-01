from odoo import models, fields, api

from ..common.we_request import WeRequest


class App(models.Model):
    _name = 'wechat.enterprise.app'
    _description = 'Wechat Enterprise App'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    corp_id = fields.Char(string='Corp ID', required=True)
    corp_secret = fields.Char(string='Corp Secret', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)

    def sync_organization(self):
        we_request = WeRequest(self.corp_id, self.corp_secret)
        token = we_request.get_token()
        print(token)