from odoo import models, fields

USER_STATUS = {
    'active': [1, 4],
    'not_active': [2, 5]
}


class Employee(models.Model):
    _inherit = 'hr.employee'

    we_app_id = fields.Many2one('wechat.enterprise.app', string='Wechat Enterprise App')
    we_id = fields.Char(string='Wechat Enterprise User ID')
    we_department_ids = fields.Many2many('hr.department', 'we_employee_department_rel', 'employee_id', 'department_id',
                                         string='Wechat Enterprise Departments')
    we_extattr = fields.Json(string='Wechat Enterprise User Extattr')

    def write_with_user(self, val):
        if self.user_id.id is False:
            user = self.env['res.users'].create({
                'name': val['name'],
                'login': val['we_id'],
                'company_id': val['company_id'],
                'company_ids': [(4, val['company_id'])],
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
                'active': val['active']
            })
            val['user_id'] = user.id
        self.write(val)

    def create_with_user(self, val_list):
        for val in val_list:
            user = self.env['res.users'].search([('login', '=', val['we_id']), ('active', 'in', [True, False])])
            if user.id is False:
                val['user_id'] = user.id
            else:
                user = self.env['res.users'].create({
                    'name': val['name'],
                    'login': val['we_id'],
                    'company_id': val['company_id'],
                    'company_ids': [(4, val['company_id'])],
                    'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
                    'active': val['active']
                })
                val['user_id'] = user.id
        return self.create(val_list)

    async def sync_user(self, we_department, server_dep_id):
        we_request = self.env.context.get('we_request')
        we_app = self.env.context.get('we_app')
        sync_user = self.env.context.get('sync_user')

        user_list = await we_request.department_users(server_dep_id)
        create_users = []
        manager_id = None

        for user in user_list:
            # job
            job = self.env['hr.job'].search(
                [('name', '=', user['position']), ('company_id', '=', we_app.company_id.id)])
            if job.id is False:
                job = self.env['hr.job'].create({
                    'name': user['position'],
                    'company_id': we_app.company_id.id
                })

            employee = self.search([('we_id', '=', user['userid']), ('active', 'in', [True, False])])
            main_department = we_department.search([('we_id', '=', user['main_department'])])

            modify_data = {
                'name': user['name'],
                'we_id': user['userid'],
                'we_app_id': we_app.id,
                'company_id': we_app.company_id.id,
                'department_id': main_department.id,
                'we_department_ids': [(4, we_department.id)],
                'job_id': job.id,
                'work_phone': False,
                'parent_id': False,
                'we_extattr': user['extattr'],
                'active': user['status'] in USER_STATUS['active']
            }

            if employee.id is False:
                modify_data['marital'] = False
                create_users.append(modify_data)
            else:
                employee.write_with_user(modify_data) if sync_user else employee.write(modify_data)
                if not sync_user and employee.user_id.id is not False:
                    employee.user_id.write({
                        'active': user['status'] in USER_STATUS['active']
                    })

            # set department manager
            if user['isleader'] == 1 and not manager_id:
                manager_id = user['userid']

        if len(create_users) > 0:
            # create users limit 500
            limit = 500
            for i in range(0, len(create_users), limit):
                create_vals = create_users[i:i + limit]
                # if config set not sync user, not create user
                self.create_with_user(create_vals) if sync_user else self.create(create_vals)
        if manager_id:
            we_department.write({'manager_id': self.search([('we_id', '=', manager_id)]).id})
