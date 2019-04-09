from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

# create_by | create_date | update_by | update_date
# Ganesh      15/10/2018    
# Info : mrp.bom inherite for customise the models

class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'
    
    # Set validation on BOM Line if same product appeare in BOM Line
    @api.constrains('product_id', 'product_tmpl_id', 'bom_line_ids')
    def _check_product_recursion(self):
        count = 0

        for bom in self:
            if bom.bom_line_ids.filtered(lambda x: x.product_id.product_tmpl_id == bom.product_tmpl_id):
                raise ValidationError(_('Duplicate Bom line item %s exists') % bom.display_name)
        
        product_ids =[]  
        product_id = False  
        for bol in bom.bom_line_ids:            
            product_id=bol.product_id.id 
            if not (product_id in product_ids) : 
                product_ids.append(product_id)
            else : 
                raise ValidationError(_('Duplicate Bom line item %s exists') % bol.display_name)
               