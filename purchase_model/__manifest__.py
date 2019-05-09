# -*- coding: utf-8 -*-   
{
    'name': "Purchase_Custom_Model",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "SAIAIPL PVT LTD",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','subcontract','stock','Pce_Master'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_model_views.xml',
        'views/transport_mode_master_view.xml',
        'views/category_table_view.xml',
        'views/indent_type_master.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}