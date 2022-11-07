from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    we_sync_user = fields.Boolean(string='Wechat Enterprise sync with res.user', default=True)

    @api.model
    def get_values(self):
        res = super().get_values()

        we_sync_user = bool(self.env['ir.config_parameter'].sudo().get_param("wechat_enterprise.we_sync_user"))
        res.update({
            'we_sync_user': we_sync_user
        })

        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param("wechat_enterprise.we_sync_user", self.we_sync_user)
