from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round


# create_by | create_date | update_by | update_date
# Ganesh      13/10/2018    
# Info : Add reason for scrap 


class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    _order = 'id desc'

    reason_desc=fields.Many2one('reason.master','Reason')

    def _move_values(self):
        vals={}
        mrpdata = self.env['mrp.production'].search([('id','=',self.production_id.id )])
        for data in mrpdata:
            vals = {
                    'bom_id': data.bom_id.id,
                    'company_id': data.company_id.id,
                    'cum_ope_time': data.cum_ope_time,
                    'cum_setup_time': data.cum_setup_time,
                    'cum_tran_time': data.cum_tran_time,
                    'date_planned_finished': data.date_planned_finished,
                    'date_planned_start': data.date_planned_start,
                    'is_locked': data.is_locked,
                    'location_dest_id': data.location_dest_id.id,
                    'location_src_id': data.location_src_id.id,
                    'name': self.env['ir.sequence'].next_by_code('mrp.production') or _('New'),
                    'origin': data.origin,
                    'picking_type_id': data.picking_type_id.id,
                    'procurement_group_id': data.procurement_group_id.id,
                    'product_id': data.product_id.id,
                    'product_qty': self.scrap_qty,                    
                    'product_uom_id': data.product_uom_id.id,
                    'state': 'confirmed',
                    'statusflag': 'O',
                    'subcontract_parentchildprod': data.subcontract_parentchildprod,
                    'subcontract_prod': data.subcontract_prod,
                    'user_id': self.env.uid,
                    'vendor': data.vendor.id                
                }        
        return vals

    # Update : At the time of manufactured item get scrap then create new MO of that item with scrap quantity 27/02/2019
    def _prepare_move_values(self):
        vals = super(StockScrap, self)._prepare_move_values()
        if self.production_id:
            vals['origin'] = vals['origin'] or self.production_id.name
            if self.product_id in self.production_id.move_finished_ids.mapped('product_id'):
                vals.update({'production_id': self.production_id.id})
                move = self.env['mrp.production'].create(self._move_values())               
            else:
                vals.update({'raw_material_production_id': self.production_id.id})
        return vals
    
    # Set location on product stock move location_dest_id
    # @api.onchange('product_id')
    # def onchange_picking_type(self):
    #     if self.production_id:      
    #         if self.product_id:                            
    #             stock_move_obj = self.env['stock.move'].search([('name','=',self.production_id.name),('product_id','=',self.product_id.id)])
    #             if stock_move_obj:
    #                 self.location_id = stock_move_obj.location_dest_id
    #             else:
    #                 raise UserError(_('Wrong product ( '  + (self.product_id.name) + ' ) is selected'))
    
    




