# -*- coding: utf-8 -*-
from openerp import models, fields, api

class invoice_type(models.TransientModel):
    _name='invoice.type'
    
    

    @api.multi
    def Original_For_Receipient(self):
        mrp_id=self.env['account.invoice'].browse(self._context['active_id'])
        mrp_id.write({'invoice_type':'Original For Receipient'})


    @api.multi
    def Duplicate_For_Transporter(self):
        mrp_id=self.env['account.invoice'].browse(self._context['active_id'])
        mrp_id.write({'invoice_type':'Duplicate For Transporter'})
    
    @api.multi
    def Triplicate_For_Assessee(self):
        mrp_id=self.env['account.invoice'].browse(self._context['active_id'])
        mrp_id.write({'invoice_type':'Triplicate For Assessee'})

    @api.multi
    def Extra_Copy(self):
        mrp_id=self.env['account.invoice'].browse(self._context['active_id'])
        mrp_id.write({'invoice_type':'Extra Copy'})

    @api.multi
    def All(self):
        mrp_id=self.env['account.invoice'].browse(self._context['active_id'])
        mrp_id.write({'invoice_type':'All'})
