# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################
{
    'name': 'Employee Age',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'sequence': 1,
    'summary': 'Apps will help to add Employee Age on Employee screen',
    'description': """
         Apps will help to add Employee Age on Employee screen
         """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com/',
    'depends': ['hr'],
    'data': [
        'views/employee_view.xml'
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
