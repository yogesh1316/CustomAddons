# -*- coding: utf-8 -*-
{
    'name': "qutation_mrp_bom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp','sale','product','sale_margin'],

    # always loaded
    'data': [
        'views/quotation_mrp_bom.xml',
        'views/sale_order_view.xml',
       'views/mrp_bom_views.xml',
       'views/sale_order_line_view.xml', #Created-By:Pradip Created-Date:07-03-2019,Info.Sale.order.line.views ,Column width Adjust
	    'views/purchase_view_order_form.xml', #Created-By:Pradip Created-Date:07-03-2019,Info.purchase.order.line.views ,Column width Adjust
        'views/mrp_bom_views_line.xml', #Created-By:Pradip Created-Date:07-03-2019,Info.mrp.bom.line.views ,Column width Adjust
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
