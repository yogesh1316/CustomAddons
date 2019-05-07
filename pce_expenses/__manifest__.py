# -*- coding: utf-8 -*-
{
    'name': "Pce_Expenses",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense','sale_expense','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pce_expense_view.xml',
        'views/create_type_expense.xml',
        'views/templates.xml',
        'report/pce_expense_menu.xml',
        'report/pce_expense_report_body.xml',
        'report/template.xml',
        'wizard/pce_expense_payment_wizard.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}