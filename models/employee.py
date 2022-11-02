from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    we_id = fields.Char(string='Wechat Enterprise User ID')

    async def sync_user(self, we_request, we_department, server_dep_info):
        user_list = await we_request.department_users(server_dep_info['id'])
        print(user_list)
        print('sync_user complete')
