import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp

from odoo.tools import float_compare, pycompat

class ProductProduct(models.Model):
    _inherit = "product.product"
#     _description = "Product"
    _inherits = {'product.template': 'product_tmpl_id'}
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'default_code, name, id'
      

        
     
     
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(ProductProduct, self).name_search(name=name, args=args, operator='ilike', limit=100)
        ids = self.search([('mf_part_no', '=', name)])
#         make_desc_ids=self.env['make_master.info'].search([('make_description','=',name)])
        make_desc_ids=self.search([('manufacturer.make_description',operator,name)])
        #print("make_desc_ids===========",make_desc_ids,make_desc_ids.name_get(),len(make_desc_ids.name_get()))
#         manufacturer_ids=self.search([('manufacturer','=',make_desc_ids.id)])
        
        if ids:
            return ids.name_get()
        elif make_desc_ids:
            return make_desc_ids.name_get()
        else:
            return res   
