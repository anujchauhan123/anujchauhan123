# -*- coding: utf-8 -*-
{
    'name': "capwise_crm",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
        'security/crm_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/invoice_view.xml',
        'views/invoice_template.xml',
        'demo/mail_data.xml',
        'demo/schedular_mis_report.xml',
        'views/credit_report.xml'
        

    ],
    'assets': {
        'web.assets_qweb': [
            'capwise_crm/static/src/xml/kanban.xml',
        ],
        'web.assets_backend': [
            ('remove', 'web/static/src/legacy/js/views/kanban/kanban_controller.js'),
            'capwise_crm/static/src/js/kanban_controller.js'
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
