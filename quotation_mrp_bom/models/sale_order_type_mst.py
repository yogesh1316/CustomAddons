#0 -*- coding: utf-8 -*-

from odoo import models, fields, api,tools
from odoo.exceptions import ValidationError,UserError

class SaleorderCategoryMaster(models.Model):
    _name="saleorder.type.master"   
    _rec_name="so_type"

    so_type=fields.Char()
    so_type_name=fields.Char()
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate")
    
    @api.onchange('so_type')
    def _set_upper(self):
        if self.so_type:
            self.so_type=str(self.so_type).upper()
        return

  