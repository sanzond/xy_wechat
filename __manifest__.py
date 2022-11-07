# -*- coding: utf-8 -*-
{
    'name': "wechat_enterprise",

    'summary': """
        module for Wechat Enterprise""",

    'description': """
        Api and methods for Wechat Enterprise , which is used in Internal Enterprise Applications.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'external_dependencies': {
        'python': ['aiohttp'],
    },

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],
    'assets': {
        'web.assets_backend': [
            'wechat_enterprise/static/src/js/we_qrcode_widget.js',
        ]
    },
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/company.xml',
        'views/app.xml',
        'views/res_config_settings.xml',
        'views/log.xml',
    ],
    'application': True
}
