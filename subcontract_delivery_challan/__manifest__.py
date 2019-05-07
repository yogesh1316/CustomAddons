# -*- coding: utf-8 -*-
{
    'name': "subcontract_delivery_challan",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    
    'category': 'Uncategorized',
    'version': '0.1',

    #  any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'report/stock_picking_main_report.xml',
        'report/stock_picking_report_menu.xml',
        'report/template_demo.xml'
    ],
    
    
}