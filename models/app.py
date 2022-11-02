import threading

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

    def run_sync(self):
        # create a threading to avoid odoo ui blocking
        thread = threading.Thread(target=self.sync_organization)
        thread.start()

    def sync_organization(self):
        uid = self.env.uid
        with self.env.registry.cursor() as new_cr:
            self.env = api.Environment(new_cr, uid, {})
            we_request = WeRequest(self.corp_id, self.corp_secret)
            print(we_request)
            departments = we_request.department_simplelist()
            for dep in departments:
                self.env['hr.department'].sync_department(we_request, self, dep)
            print('finish sync')

