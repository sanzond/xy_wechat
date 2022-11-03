import asyncio
import threading
import time

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

    @property
    def we_request_class(self):
        return WeRequest

    def run_sync(self):
        # create a threading to avoid odoo ui blocking
        def _sync():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(self.sync_organization())

        thread = threading.Thread(target=_sync)
        thread.start()

    async def sync_organization(self):
        start = time.time()
        uid = self.env.uid
        with self.env.registry.cursor() as new_cr:
            self.env = api.Environment(new_cr, uid, self.env.context)
            we_request = self.we_request_class(self.corp_id, self.corp_secret)
            config = self.env['res.config.settings'].sudo().get_values()

            await self.env['hr.department'].with_context(
                self.env.context, we_app=self, we_request=we_request,
                sync_user=config['we_sync_user']
            ).sync_department()

            print(f'sync complete, cost {time.time() - start}s')
