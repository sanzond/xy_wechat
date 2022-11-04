import asyncio
import threading
import time
import datetime
import traceback

from odoo import models, fields, api

from ..common.we_request import WeRequest


def get_now_time_str():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


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
        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
            'title': 'Sync Start......',
            'message': f'Start sync organization now, please wait......',
            'warning': True
        })

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
        is_success = True
        with self.env.registry.cursor() as new_cr:
            self.env = api.Environment(new_cr, uid, self.env.context)

            detail_log = f'start sync at {get_now_time_str()}......'
            try:
                we_request = self.we_request_class(self.corp_id, self.corp_secret)
                config = self.env['res.config.settings'].sudo().get_values()

                await self.env['hr.department'].with_context(
                    self.env.context, we_app=self, we_request=we_request,
                    sync_user=config['we_sync_user']
                ).sync_department()
                detail_log += f'\nsync success!'
            except Exception:
                is_success = False
                detail_log += f'\nsync failed, error: \n{traceback.format_exc()}'
            finally:
                detail_log += f'\nsync end at {get_now_time_str()}, cost {round(time.time() - start, 2)}s'
                company_id = self.company_id.id
                self.env['wechat.enterprise.log'].create({
                    'company_id': company_id,
                    'we_app_id': self.id,
                    'detail': detail_log
                })
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'title': 'Sync End......',
                    'message': f'Sync organization end, {"success" if is_success else "failed"}',
                    'warning': True if is_success else False
                })
