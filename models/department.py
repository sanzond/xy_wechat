from odoo import models, fields


class Department(models.Model):
    _inherit = 'hr.department'

    we_app_id = fields.Many2one('wechat.enterprise.app', string='Wechat Enterprise App')
    we_id = fields.Char(string='Wechat Enterprise Department ID')
    we_parent_id = fields.Char(string='Wechat Enterprise Parent Department ID')
    we_order = fields.Integer(string='Wechat Enterprise Department Order')

    async def sync_department(self, we_request, we_app, server_dep_info):
        """
        sync department from wechat enterprise
        :param we_request: WeRequest instance
        :param we_app: wechat enterprise app
        :param server_dep_info: single dep info from /department/simplelist api
        :return:
        """
        dep_detail = await we_request.department_detail(server_dep_info['id'])
        dep = self.search([('we_id', '=', dep_detail['id'])])
        # dep need commit to db because sync user need use it
        if not dep:
            dep = self.create({
                'company_id': we_app.company_id.id,
                'name': dep_detail['name'],
                'we_app_id': we_app.id,
                'we_id': dep_detail['id'],
                'we_parent_id': dep_detail['parentid'],
                'we_order': dep_detail['order']
            })
        else:
            dep.write({
                'company_id': we_app.company_id.id,
                'name': dep_detail['name'],
                'we_app_id': we_app.id,
                'we_id': dep_detail['id'],
                'we_parent_id': dep_detail['parentid'],
                'we_order': dep_detail['order']
            })

        await self.env['hr.employee'].sync_user(we_request, dep, dep_detail)
