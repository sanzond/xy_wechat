import asyncio

from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools.translate import _

from ..common.we_request import we_request_instance

USER_STATUS = {
    'active': [1, 4],
    'not_active': [2, 5]
}


def send_list_to_str(send_list):
    """
    convert send list to str
    :param send_list: wx_id list or string of @all
    :return:
    """
    if send_list == 'all' or send_list is None:
        return send_list
    return '|'.join(send_list)


class Employee(models.Model):
    _inherit = 'hr.employee'

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
        else:
            self.user_id.write({
                'name': val['name'],
                'active': val['active']
            })
        self.write(val)

    def create_with_user(self, val_list):
        for val in val_list:
            user = self.env['res.users'].search([('login', '=', val['we_id']), ('active', 'in', [True, False])])
            if user.id is False:
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
        sync_with_user = we_app.sync_with_user

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
                'company_id': we_app.company_id.id,
                'department_id': main_department.id,
                'we_department_ids': [(4, we_department.id)],
                'job_id': job.id,
                'we_extattr': user['extattr'],
                'active': user['status'] in USER_STATUS['active']
            }

            if employee.id is False:
                modify_data['marital'] = False
                modify_data['work_phone'] = False
                modify_data['parent_id'] = False
                create_users.append(modify_data)
            else:
                employee.write_with_user(modify_data) if sync_with_user else employee.write(modify_data)

            # set department manager
            if user['isleader'] == 1 and not manager_id:
                manager_id = user['userid']

        if len(create_users) > 0:
            # create users limit 500
            limit = 500
            for i in range(0, len(create_users), limit):
                create_vals = create_users[i:i + limit]
                # if config set not sync user, not create user
                self.create_with_user(create_vals) if sync_with_user else self.create(create_vals)
        if manager_id:
            we_department.write({'manager_id': self.search([('we_id', '=', manager_id)]).id})

    def send_we_message(self, app_id, to_users, to_departments=None, msgtype='text', **kwargs):
        """
        send message in Wechat Enterprise
        because sync's info has no tag, so we can't send message to tag, only can send to the single app,
        the existing parameters are 'to_users', 'to_departments', 'msgtype', 'agentid'
        :param app_id: wechat enterprise app id used to send message
        :param to_users: wechat enterprise user we_id list, if to all user, set to '@all'
        :param to_departments: wechat enterprise department we_id list, if to all department, set to '@all'
        :param msgtype: message type, reference https://developer.work.weixin.qq.com/document/path/90236
        :param kwargs: other parameters, reference https://developer.work.weixin.qq.com/document/path/90236
        :return:
        """
        assert app_id, 'app_id is required'
        if len(to_users) == 0 and len(to_departments) == 0:
            raise UserError(_('Please select the user or department to send the message!'))

        app = self.env['wechat.enterprise.app'].sudo().browse(int(app_id))
        we_request = we_request_instance(app.corp_id, app.secret)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        send_message_task = loop.create_task(we_request.send_message(dict(
            touser=send_list_to_str(to_users),
            toparty=send_list_to_str(to_departments),
            msgtype=msgtype,
            agentid=app.agentid,
            **kwargs
        )))
        loop.run_until_complete(send_message_task)
        loop.close()
