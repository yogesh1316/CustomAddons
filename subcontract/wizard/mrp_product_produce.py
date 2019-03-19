from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'    
    

    workorder_ids = fields.One2many('mrp.workorder',readonly=False ,compute='_compute_workids',string='Work Orders')    

    # Showing Operation against Production on tree view
    @api.depends('production_id')
    def _compute_workids(self):                
        self.workorder_ids=self.production_id.workorder_ids


    # Create by : Ganesh , Create Date : 10/01/2019
    # Update Operation at the time of subcontract which operation is send to DC and PO Or create new Operation
    @api.onchange('workorder_ids')
    def onchange_subcontract_operation(self):         
        print('self.workorder_ids pro. prod.',self.workorder_ids)
        for line in self.workorder_ids:                  
            if line.subcontract_operation is True:
                print('id True',line.id)
                self.env.cr.execute("update mrp_workorder set subcontract_operation='t' where id= %s",(line.id,))      
            elif line.subcontract_operation is False:                 
                print('id False',line.id)
                if isinstance(line.id, models.NewId):                    
                    wo_data = {}
                    mrp_workorder_obj = self.env['mrp.workorder']
                    wo_data ={'name':line.name, 
                        'workcenter_id':self.workorder_ids[0].workcenter_id.id,                     
                        'production_id':self.production_id.id,
                        'product_id': self.production_id.product_id.id,
                        'production_availability': 'assigned',
                        'qty_produced':0,
                        'qty_producing':self.product_qty,
                        'state':'pending',
                        }
                    ids = mrp_workorder_obj.create(wo_data)  
                else:
                    self.env.cr.execute("update mrp_workorder set subcontract_operation='f' where id= %s",(line.id,))            
    
    @api.model
    def create(self, vals):        
        if self.production_id.product_qty < self.product_qty:
            raise UserError(_('You cannot produce more then production quantity'))
        else:                
            res = super(MrpProductProduce, self).create(vals)   
            return   res  

    @api.multi
    def do_produce(self):        
        self.create_po()     
        msg = _('For Subcontract Quantity Produced: ') + str(self.product_qty)
        self.production_id.message_post(body=msg)
        for ml in self.production_id.move_raw_ids:               
            total_qty = 0
            sq = self.env['stock.quant'].search([('product_id', '=', ml.product_id.id), ('location_id', '=', ml.location_dest_id.id)])
            
            if sq.id == False:
                raise UserError(_('There is no stock available for the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) in the stock location. Kindly add the required stock.'))
            else:
                for bom_line in self.production_id.bom_id.bom_line_ids:
                    if ml.product_id == bom_line.product_id:
                        total_qty = bom_line.product_qty * self.product_qty                                               
                        for i in sq:            
                            if total_qty > i.quantity:
                                raise UserError(_('You cannot validate this stock operation because the stock level of the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) would become negative on the stock location and negative stock is not allowed for this product.'))
        
        return {'type': 'ir.actions.act_window_close'}

    # Create by : Ganesh , Create Date : 22/01/2019
    # To create a purchase order while clicking on do_produce button:
    @api.multi
    def create_po(self):
        name=''
        vals_item = {}
        vals_line_item = {}
        sp_obj = self.env['stock.picking']
        po_obj = self.env['purchase.order']
        pol_obj = self.env['purchase.order.line']
        if self.production_id.subcontract_prod and not self.production_id.purchase_ids:

            # Update : Subcontract PO sequence no change as per ERP, start with 'OP' 15/03/2019
            name = self.env['ir.sequence'].next_by_code('purchase.order').replace('PL','OP') or '/'

            vals_item = {
                'partner_id': self.production_id.vendor.id,
                'state': 'draft',
                'mrp_id': self.production_id.id,
                'origin': self.production_id.name,
                'subcontract_operation':sp_obj.set_operation(self.production_id),
                'name': name
            }
            po_id = po_obj.create(vals_item)
            if self.production_id.subcontract_parentchildprod in ('1','2'):
                vals_line_item = {
                    'product_id': self.production_id.move_finished_ids.product_id.id,
                    'name': self.production_id.move_finished_ids.product_id.name,
                    'date_planned': self.production_id.date_planned_start,
                    'product_qty': self.production_id.move_finished_ids.product_qty,
                    'product_uom': self.production_id.move_finished_ids.product_id.uom_id.id,
                    'price_unit': 0.0,
                    'taxes_id': [(6, 0, self.production_id.move_finished_ids.product_id.supplier_taxes_id.ids)],
                    'order_id': po_id.id,
                }
                pol_obj.create(vals_line_item)
            elif self.production_id.subcontract_parentchildprod =='3':    
                # Update : taken move_raw_ids only those product which r_flag is in New and Replace         
                for line in self.production_id.move_raw_ids.filtered(lambda x: x.r_flag in('N','R')):                        
                    vals_line_item = {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'date_planned': self.production_id.date_planned_start,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_id.uom_id.id,
                        'price_unit': 0.0,
                        'taxes_id': [(6, 0, line.product_id.supplier_taxes_id.ids)],
                        'order_id': po_id.id,
                    }
                    pol_obj.create(vals_line_item)
