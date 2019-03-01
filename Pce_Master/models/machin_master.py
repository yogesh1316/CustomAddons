from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime

class machin_master(models.Model):
    _name='machin.master'
    
    #Updated-By:Pradip | Updated-Date:17-1-19|Info: String Updated(Machine)
    machin_number = fields.Char(string='Machine Number',required=True,)
    work_center = fields.Many2one('mrp.workcenter',string='Work Center', required=True,)

    
    machin_name=fields.Char(string='Machine Name',required=True,)
    work_center_description=fields.Char(string='WorkCenter Description',required=True,)
    location=fields.Char(string='Location',required=True,)
    shift_factor=fields.Selection([('1', '1'), ('2', '2'), ('3', '3')],required=True,)
    description=fields.Char(string='Description',required=True,)
        
    utilization_factor=fields.Char(string='Utilization Factor%',required=True,)
    fixed_overhead=fields.Char(string='Fixed Overhead',required=True,)
    capacity_factor=fields.Char(string='Capacity Factor%',required=True,)
    variable_overhead=fields.Char(string='Variable Overhead',required=True,)

    @api.onchange('work_center')
    def get_selection(self) :
        print('work center',self.work_center.note)
        self.work_center_description=self.work_center.note

    
    
    
