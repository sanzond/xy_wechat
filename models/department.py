import asyncio

from odoo import models, fields


class Department(models.Model):
    _inherit = 'hr.department'

    we_app_id = fields.Many2one('wechat.enterprise.app', string='Wechat Enterprise App')
    we_id = fields.Char(string='Wechat Enterprise Department ID')
    we_parent_id = fields.Char(string='Wechat Enterprise Parent Department ID')
    we_order = fields.Integer(string='Wechat Enterprise Department Order')
    '''because a Wechat Enterprise user can have multi departments, so we need a many2many field, 
    the department_id field is only main department'''
    we_employee_ids = fields.Many2many('hr.employee', 'we_employee_department_rel', 'department_id', 'employee_id',
                                       string='Wechat Enterprise Employees')

    async def get_server_depart_tree(self):
        """
        get Wechat Enterprise server department tree, root parentid is 1
        :return:
        """
        we_request = self.env.context.get('we_request')
        departments = await we_request.department_simplelist()

        def get_tree_data(arr, parent_id):
            tree = []
            for item in arr:
                if item['parentid'] == parent_id:
                    tree.append({
                        'id': item['id'],
                        'parentid': item['parentid'],
                        'order': item['order'],
                        'children': get_tree_data(arr, item['id'])
                    })

            return tree

        return get_tree_data(departments, 1)

    async def sync_department(self):
        """
        sync department from wechat enterprise
        :return:
        """
        we_request = self.env.context.get('we_request')
        we_app = self.env.context.get('we_app')

        depart_tree = await self.get_server_depart_tree()

        change_ids = []
        tasks = []

        async def _sync_dep(server_dep, parent_id):
            _tasks = []
            dep_detail = await we_request.department_detail(server_dep['id'])
            dep = self.search([('we_id', '=', dep_detail['id'])])
            # dep need commit to db because sync user need use it
            modify_data = {
                'company_id': we_app.company_id.id,
                'name': dep_detail['name'],
                'we_app_id': we_app.id,
                'we_id': dep_detail['id'],
                'parent_id': parent_id,
                'we_parent_id': dep_detail['parentid'],
                'we_order': dep_detail['order'],
                'manager_id': False,
                'we_employee_ids': [(5, 0, 0)]
            }

            if not dep:
                dep = self.create(modify_data)
            else:
                dep.write(modify_data)
            change_ids.append(dep.id)

            await self.env['hr.employee'].sync_user(dep, dep_detail['id'])

            if len(server_dep['children']) > 0:
                for child in server_dep['children']:
                    _tasks.append(_sync_dep(child, dep.id))
                await asyncio.gather(*_tasks)

        # change all the all's employee status to not active
        self.env['hr.employee'].search([('we_app_id', '=', we_app.id)]).write({'active': False})

        for department in depart_tree:
            tasks.append(_sync_dep(department, False))

        await asyncio.gather(*tasks)
        self.clean_needless_department(change_ids)

    def clean_needless_department(self, include_dep_ids=None):
        """
        clean needless department
        :return:
        """
        we_app = self.env.context.get('we_app')
        self.search([('we_app_id', '=', we_app.id), ('id', 'not in', include_dep_ids or [])]).unlink()
