# -*- coding: utf-8 -*-
{
    'name': "Pce_Master",
    'summary': """
        All Master Views and Models in this app
        """,
    'description': """
        Long description of module's purpose
    """,
    'author': "Hrishikesh S. Kulkarni,Pradip R.Yepure",
    'website': "http://www.saiaipl.com",
    'category': 'Master',
    'version': '1.1',
    # any module necessary for this one to work correctly
    'depends': ['sale','product','sale_margin','purchase','account','base','delivery','mrp','mail'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',        
        'views/shift_master.xml',
        'views/machin_master.xml',
        'views/factory_calendor.xml',
        'views/res_partner_views.xml',               
        'views/reason_master_view.xml',
        'views/item_type_master.xml',
        'views/pce_master_menu_views.xml',
        'views/sale_order_line_view.xml',
        'views/delivery_terms_master_view.xml',
        'views/transport_mode_master_view.xml',
        'views/transport_cost_master_view.xml',

        'views/material_group_master_view.xml',
        'views/material_master_view.xml',

        'views/operation_master_view.xml',
        'views/parameter_master_view.xml',

        'views/operation_parameter_master_view.xml',
        
        'views/mrp_routing_work_center_form_view.xml',

        'views/mrp_routing_work_center_form_view.xml',
        'security/pce_master_security.xml',
        'security/security_view.xml',

    ],
    # only loaded in demonstration mode
    
    'installable':True,
    'auto_install':False,
    'application':True,
}
