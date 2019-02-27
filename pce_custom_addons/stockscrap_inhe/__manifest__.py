# -*- coding: utf-8 -*-
{
    'name': "stock scrap inherit",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ganesh",
    'website': "",

    # Categories can be used to filter modules in modules listing   
    # for the full list
    'category': 'Stock Scrap',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stockscrap_views.xml',
       
    ],   
}