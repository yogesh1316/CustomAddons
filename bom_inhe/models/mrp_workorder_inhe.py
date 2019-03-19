
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp


# create_by | create_date | update_by | update_date
# Ganesh      27/10/2018
# Info : mrp.workorder inherit to adding following functionality

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    _description = 'Manufacturing Workorder inherite For calculate planned date and finished date on Cumulative time'

    workorder_ids = fields.One2many('workorder.pdir.generate', 'workorder_id', string='line ids')
   
    @api.constrains('qty_produced')
    def complete_qty(self):
        #print('self.qty_produced',self.qty_produced)
        self.production_id.complete_qty= self.qty_produced
        if self.qty_produced != 0:
            self.production_id.produced_qty -= self.qty_producing
            if self.production_id.produced_qty < 0:
                self.production_id.produced_qty=0
            

    # This Function use to upload PDIR report
    @api.multi
    def generate_pdir(self):
        
        view_id=self.env.ref('bom_inhe.workorder_generate_pdir_form_view').id
        ctx=dict(self.env.context)        
        return {
            'name': _('PDIR generate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.workorder',
            'res_id': self.id,
            'view_id': view_id,
            'target': 'new',
            'context': ctx

        }

    # Code inherite, Comment code for child item at the time of Mark_as_done button click  30/11/2018

    @api.multi
    def record_production(self):
        self.ensure_one()
        if self.qty_producing <= 0:
            raise UserError(_('Please set the quantity you are currently producing. It should be different from zero.'))

        if (self.production_id.product_id.tracking != 'none') and not self.final_lot_id and self.move_raw_ids:
            raise UserError(_('You should provide a lot/serial number for the final product'))

        # Update quantities done on each raw material line
        # For each untracked component without any 'temporary' move lines,
        # (the new workorder tablet view allows registering consumed quantities for untracked components)
        # we assume that only the theoretical quantity was used

        # Logic Change here we comment code for the Child item

        # for move in self.move_raw_ids:
        #     if move.has_tracking == 'none' and (move.state not in ('done', 'cancel')) and move.bom_line_id\
        #                 and move.unit_factor and not move.move_line_ids.filtered(lambda ml: not ml.done_wo):
        #         rounding = move.product_uom.rounding
        #         if self.product_id.tracking != 'none':
        #             qty_to_add = float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)
        #             move._generate_consumed_move_line(qty_to_add, self.final_lot_id)
        #         else:
        #             move.quantity_done += float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)

        wo_data = {}
        workorder_pdir_generate_obj = self.env['workorder.pdir.generate']

        if not self.next_work_order_id:                
            wo_data ={'production_id':self.production_id.id,
                    'product_id': self.production_id.product_id.id,
                    'qty_produced':self.qty_producing, #if line.product_id.description_sale else 'NA',
                    'workorder_id': self.ids[0],
                    }
            
            ids = workorder_pdir_generate_obj.create(wo_data)
                
        # Transfer quantities from temporary to final move lots or make them final
        for move_line in self.move_line_ids:
            # Check if move_line already exists
            if move_line.qty_done <= 0:  # rounding...
                move_line.sudo().unlink()
                continue
            if move_line.product_id.tracking != 'none' and not move_line.lot_id:
                raise UserError(_('You should provide a lot/serial number for a component'))
            # Search other move_line where it could be added:
            lots = self.move_line_ids.filtered(lambda x: (x.lot_id.id == move_line.lot_id.id) and (not x.lot_produced_id) and (not x.done_move) and (x.product_id == move_line.product_id))
            
            if lots:
                lots[0].qty_done += move_line.qty_done
                lots[0].lot_produced_id = self.final_lot_id.id
                move_line.sudo().unlink()
            else:
                move_line.lot_produced_id = self.final_lot_id.id
                move_line.done_wo = True

        # One a piece is produced, you can launch the next work order
        if self.next_work_order_id.state == 'pending':
            self.next_work_order_id.state = 'ready'

        self.move_line_ids.filtered(
            lambda move_line: not move_line.done_move and not move_line.lot_produced_id and move_line.qty_done > 0
        ).write({
            'lot_produced_id': self.final_lot_id.id,
            'lot_produced_qty': self.qty_producing
        })

        # If last work order, then post lots used
        # TODO: should be same as checking if for every workorder something has been done?
        if not self.next_work_order_id:

            # Update : When last operation is done then previous all operation get done if it is not done 28/02/2019
            mrp_work_data = self.search([('production_id','=',self.production_id.id),('state','!=','done'),('next_work_order_id','!=',False)])
            for woline in mrp_work_data:
                woline.write({'state': 'done','qty_produced': self.qty_producing,'qty_producing': 0,'date_start': fields.Datetime.now(),'date_finished': fields.Datetime.now()})

            production_move = self.production_id.move_finished_ids.filtered(
                                lambda x: (x.product_id.id == self.production_id.product_id.id) and (x.state not in ('done', 'cancel')))
            if production_move.product_id.tracking != 'none':
                move_line = production_move.move_line_ids.filtered(lambda x: x.lot_id.id == self.final_lot_id.id)
                if move_line:
                    move_line.product_uom_qty += self.qty_producing
                else:
                    move_line.create({'move_id': production_move.id,
                             'product_id': production_move.product_id.id,
                             'lot_id': self.final_lot_id.id,
                             'product_uom_qty': self.qty_producing,
                             'product_uom_id': production_move.product_uom.id,
                             'qty_done': self.qty_producing,
                             'workorder_id': self.id,
                             'location_id': production_move.location_id.id,
                             'location_dest_id': production_move.location_dest_id.id,
                    })
            else:                
                production_move.quantity_done += self.qty_producing
               

        if not self.next_work_order_id:
            for by_product_move in self.production_id.move_finished_ids.filtered(lambda x: (x.product_id.id != self.production_id.product_id.id) and (x.state not in ('done', 'cancel'))):
                if by_product_move.has_tracking != 'serial':
                    values = self._get_byproduct_move_line(by_product_move, self.qty_producing * by_product_move.unit_factor)
                    self.env['stock.move.line'].create(values)
                elif by_product_move.has_tracking == 'serial':
                    qty_todo = by_product_move.product_uom._compute_quantity(self.qty_producing * by_product_move.unit_factor, by_product_move.product_id.uom_id)
                    for i in range(0, int(float_round(qty_todo, precision_digits=0))):
                        values = self._get_byproduct_move_line(by_product_move, 1)
                        self.env['stock.move.line'].create(values)

        # Update workorder quantity produced
        self.qty_produced += self.qty_producing

        if self.final_lot_id:
            self.final_lot_id.use_next_on_work_order_id = self.next_work_order_id
            self.final_lot_id = False

        # Set a qty producing
        rounding = self.production_id.product_uom_id.rounding
        if float_compare(self.qty_produced, self.production_id.product_qty, precision_rounding=rounding) >= 0:
            self.qty_producing = 0
        elif self.production_id.product_id.tracking == 'serial':
            self._assign_default_final_lot_id()
            self.qty_producing = 1.0
            self._generate_lot_ids()
        else:
            self.qty_producing = float_round(self.production_id.product_qty - self.qty_produced, precision_rounding=rounding)
            self._generate_lot_ids()

        if self.next_work_order_id and self.production_id.product_id.tracking != 'none':
            self.next_work_order_id._assign_default_final_lot_id()

        if float_compare(self.qty_produced, self.production_id.product_qty, precision_rounding=rounding) >= 0:
            self.button_finish()
        return True

class PDIR_generate(models.Model):
    _name = "workorder.pdir.generate"

    report = fields.Binary('Prepared file')
    fname = fields.Char('File Name',store=True,size=32)

    production_id = fields.Many2one(
        'mrp.production', 'Manufacturing Order',
        index=True, ondelete='cascade', store=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        related='production_id.product_id', readonly=True,
        help='Technical: used in views only.', store=True)
    qty_produced = fields.Float(
        'Quantity', default=0.0,
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already handled by this work order")
    workorder_id = fields.Many2one(
        'mrp.workorder', string='work Order',
        index=True, ondelete='cascade', required=True,store=True)

