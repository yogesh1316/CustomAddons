from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime
import time


class shift_master(models.Model):
    _name='shift.master'
    shift_name = fields.Char(string='Shift Name',required=True)
    from_hours = fields.Char(string='From Hours',required=True,default='00:00',)
    to_hours=fields.Char(string='To Hours',required=True,default='00:00',)
    total_hours=fields.Char(string='Total Hours',readonly=False,)

    ##This Function Developed by Hrishikesh S. Kulkarni 31-08-2018
    ## Calculating the total hours of two time
    @api.multi
    @api.onchange('from_hours','to_hours')
    def _onchange_from_hours(self):
        self.field = self.from_hours
        fh = self.from_hours
        th = self.to_hours
        FMT = '%H:%M'
        print(fh)
        print(th)
        #FMT = '%H:%M:%S'
        tdelta = datetime.strptime(th, FMT) - datetime.strptime(fh, FMT)
        print('****************************',tdelta)
        self.total_hours=tdelta