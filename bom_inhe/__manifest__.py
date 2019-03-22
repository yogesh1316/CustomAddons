# -*- coding: utf-8 -*-
{
    'name': "MRP production",

    'summary': """
        We customize mrp prodcution model""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ganesh",
    'website': "http://www.saiaipl.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'MRP',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp','stock','Pce_Master'],

    # always loaded
    'data': [
        'views/mrp_rounting_inhe.xml',
        'views/mrp_production_view.xml',
        'views/mrp_workorder_view_inhe.xml',
        'views/mtn_view.xml',
        'report/mrp_pro_document_print.xml',
        'report/report_menu.xml',        
    ],   
}