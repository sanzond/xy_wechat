from odoo import models
from odoo.exceptions import AccessDenied

from ..common.custom_encrypt import CustomEncrypt


class ResUsers(models.Model):
    _inherit = 'res.users'
    _we_auth_secret = 'RZDeROZp'

    def _check_credentials(self, password, env):
        # if password is dict and the key of Non password authentication(npa) is True, then authentication by custom
        if isinstance(password, dict) and password.get('npa', False) is True:
            if not self.authentication_by_non_password(password, env):
                raise AccessDenied()
        else:
            super()._check_credentials(password, env)

    def authentication_by_non_password(self, secret_dict, env):
        real_password = secret_dict.get('password', None)
        if secret_dict.get('type', None) == 'we':
            return CustomEncrypt.is_equal(ResUsers._we_auth_secret, real_password)
        return False
