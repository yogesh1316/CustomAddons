from odoo import models, fields, api,_
from odoo.exceptions import UserError

class inherit_mrp_production(models.Model):
    _inherit = 'mrp.production'


    # @api.multi
    # def action_issue(self):
        # stock_move_obj=self.env['stock.move']
        # for line in self.move_raw_id:
            # product_obj = self.env['product.product'].search([('id','=',self.product_id.id)])
            # if product_obj.inventory_flag == True:
                # raise UserError(_('Selected Product Is In Inventory Adjustment So Cannot Do Issue'))
        # else :
            # if self.product_id.item_type.id >= 4:            
                # issuecount = stock_move_obj.search_count([('issue_qty','>',0),('raw_material_production_id','=',self.id)])
            
                # if issuecount>=1:                
                    # self._post_inventory()               
                    # return self.write({'statusflag':'I'})
                # else:
                    # raise UserError(_('At least 1 item can be Issue Quantity'))    
            # elif self.product_id.item_type.id <= 3:
            
                # issuecount = stock_move_obj.search_count([('issue_qty','>=',0),('raw_material_production_id','=',self.id)])
                # totalcount = stock_move_obj.search_count([('raw_material_production_id','=',self.id)])
            
                # if totalcount==issuecount:           
                    # self._post_inventory()
                    # return self.write({'statusflag':'I'})                
                # else:
                    # raise UserError(_('All child item can be Issue Quantity'))


    @api.multi
    def issue_item_qty(self):
        product_obj = self.env['product.product'].search([('id','=',self.product_id.id)])
        #print("Product Id",product_obj)
        if product_obj.inventory_flag == True:
            raise UserError(_('Selected Product Is In Inventory Adjustment So Cannot Do Issue'))
        else:
            return {
            'name': _('Issue'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.production',     
            'res_id': self.id,
            'view_id': self.env.ref('bom_inhe.mrp_production_issue_form_view').id,
            'target': 'new',           
            'context': {'raw_material_production_id': self.id,  
                        'product_ids': (self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids,
                        },
            
        }