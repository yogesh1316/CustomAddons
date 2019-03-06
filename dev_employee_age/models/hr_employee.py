# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _
from datetime import date, datetime


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def calculate_employee_age(self):
        for emp in self:
            age = ''
            if emp.birthday:
                dob = datetime.strptime(emp.birthday, '%Y-%m-%d')
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            emp.employee_age = str(age)

    employee_age = fields.Char(string="Age", compute='calculate_employee_age')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
