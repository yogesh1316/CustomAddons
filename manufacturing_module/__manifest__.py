# -*- coding: utf-8 -*-
{
    'name': "Manufacturing Module",

    'summary': """
        We customize Manufacturing Security Related Access rights""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Pradip R. Yenpure",
    'website': "http://www.saiaipl.com",

  
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp',],

    # always loaded
    'data': [
        'views/mrp_workcenter_view.xml',
        'views/mrp_workorder_view.xml',
    ],   
}
