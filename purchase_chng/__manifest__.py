# -*- coding: utf-8 -*-
{
    'name': "Purchase_chng",

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
    'depends': ['purchase','sale','sunfire_sales','purchase_inhe'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/Purchase_up.xml',
    ],
}