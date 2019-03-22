# -*- coding: utf-8 -*-
from openerp import models, fields, api

class confirm_bom(models.TransientModel):
    _name='mrp_bom.confirm'
    
    

    @api.multi
    def yes(self):
        mrp_id=self.env['mrp.bom'].browse(self._context['active_id'])
        mrp_id.write({'status':4})


    @api.multi
    def no(self):
        pass

