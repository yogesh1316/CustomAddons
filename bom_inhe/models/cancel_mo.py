from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare
import datetime



class cancel_manufacture_order(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    @api.multi
    def mtn(self):
        self.product_id.location_dest_id="Quality_Control"
        print('self.id',self.id)
            # view_id = self.env.ref('bom_inhe.mrp_production_cancel_form_view').id
            # print('view_id',view_id)
        return {
            'name': _('Cancel Issue Material transfer to Quality Control'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.production',
            'res_id': self.id,
            'view_id': [self.env.ref('bom_inhe.mrp_production_cancel_form_view').id,'tree'],
            'target': 'new',
            'context': {'raw_material_production_id': self.id,
                            'product_ids': (self.move_raw_ids).mapped('product_id').ids,

                            },

            }

    @api.multi
    def action_transfer(self):

        vals_item = {}
        vals_line_item = {}
        stock_move_obj = self.env['stock.move']
        stock_pick_obj = self.env['stock.picking']
        stock_loc_obj = self.env['stock.location']
        proc_group_obj = self.env['procurement.group']

        qdata=stock_loc_obj.search([('name','=','Quality Control')])
        sdata=stock_loc_obj.search([('name','=','Stock')])
        p_data=proc_group_obj.search([('name','=',self.name)])



        print('qdata,sdata,p_data',qdata,sdata,p_data.id,)
        if qdata and sdata :
            vals_item = {
                 'origin':self.name,
                 'move_type':'direct',
                 'state':'assigned',
                 'scheduled_date':datetime.datetime.now(),
                 'date':datetime.datetime.now(),
                 'location_id':qdata.id,
                 'location_dest_id':sdata.id,
                 'picking_type_id':5,
                 'state': 'assigned',
                 'group_id':p_data.id,
                 'MTN':'Y'


             }
            p_id = stock_pick_obj.create(vals_item)
            print("p_id",p_id)

            for item in self.move_raw_ids:
                 vals_line_item = {
                 'name': item.product_id.name,
                 'product_id': item.product_uom_qty,
                 'ordered_qty':item.product_uom_qty,
                 'product_uom_qty':item.product_uom_qty,
                 'location_id':qdata.id,
                 'location_dest_id':sdata.id,
                 'picking_id':p_id.id,
                 'state': 'confirmed',
                 'procure_method':'make_to_stock',
                 'reference':p_id.name,
                 'product_uom':1,
                 }
                 d=stock_move_obj.create(vals_line_item)
                 print(d,".....................")

        else:
             raise UserError(_('Quality control/Stock Location is not present'))
