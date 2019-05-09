from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import datetime,re


# create_by | create_date | update_by | update_date
# Chandrakant   25/03/2019   
# Info : display customer on manufacture oorder and ppurchase order  tree view.
class mrp_inhe(models.Model):
    _inherit='mrp.production'

    partner_id = fields.Many2one('res.partner', string='Customer',compute='compute_customer', readonly=True, index=True)

    @api.depends('origin')
    def compute_customer(self):
        for production in self:
            sale_obj=self.env['sale.order'].search([('name','=',production.origin)])
            if sale_obj:
                production.partner_id=sale_obj.partner_id.id


class mrp_order_inhe(models.Model):
    _inherit='mrp.workorder'
     # update:change string name

    production_id = fields.Many2one(
        'mrp.production', 'Work Order',
        index=True, ondelete='cascade', required=True, track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})


class purchase_order_inhe(models.Model):
    _inherit='purchase.order'
    
    customer=fields.Char(string="Customer",compute='compute_po_customer',store=True)

    @api.depends('origin')
    def compute_po_customer(self):
        list=[]
        cust=''
        for order in self:
            if order.origin:
                li=[]
                li=[i for i in order.origin.split(',')]
                for i in li:
                    if ":" in i:
                        list=[j for j in i.split(':')]
                        a=str(list[0])
                        sale_obj=self.env['sale.order'].search([('name','=',a.strip())])
                        for i in sale_obj:
                            cust=cust+str(i.partner_id.display_name+',')
                            order.customer=cust
                    else:
                        sale_obj=self.env['sale.order'].search([('name','=',i.strip())])
                        for i in sale_obj:
                            cust=cust+str(i.partner_id.display_name+',')
                            order.customer=cust
                cust=""


class Picking(models.Model):
    _inherit='stock.picking'
    
    country_of_final_dest=fields.Many2one('res.country',string="Country Of Final Destination")
    port_of_landing=fields.Char(string="Port Of Landing")
    port_of_discharge=fields.Char(string="Port Of Discharge")
    net_wt=fields.Float(string="Net Weight")
    gross_wt=fields.Float(string="Gross Weight")
    dimension=fields.Char(string="Dimension")
    material_description=fields.Char(string="Material Description")
    number_of_packages = fields.Integer(string='Number of Packages\n(Box Number)', copy=False)
    carrier_tracking_ref = fields.Char(string='Tracking Reference\n(Box Name)', copy=False)
    awb_no=fields.Char(string="AWB No")
    boe_no=fields.Char(string="BOE No")
    boe_date=fields.Date(string="BOE Date")
    mode=fields.Selection([('cargo','Cargo'),('courier','Courier')],'mode')
    test=fields.Char(compute='compute_test',store=True)
    # vendor=fields.Char(string="Vendor",compute='compute_vendor')
    grn_name=fields.Char(string="GRN No")
    sale_customer=fields.Char(string="Customer",compute='assign_customer')
    invoice_status=fields.Char(default='N')
    invoice_no=fields.Char()
    invoice_date=fields.Date()

    @api.depends('origin')
    def assign_customer(self):
        for move in self:
            if move.sale_id:
                move.sale_customer=move.sale_id.partner_id.name
            
                   
    @api.depends('origin')
    def compute_vendor(self):
        for move in self:
            purchase_obj=self.env['purchase.order'].search([('name','=',move.origin)])
        if purchase_obj:
            move.vendor=purchase_obj.partner_id.name
        

    @api.depends('picking_type_id')
    def compute_test(self):
        for i in self:
            if i.picking_type_id:
                i.test=i.picking_type_id.name
                print(i.test,'.............................')


    # @api.model
    # def create(self, vals):
    #     # TDE FIXME: clean that 
        

    #     defaults = self.default_get(['name', 'picking_type_id'])
    #     pick_type=self.env['stock.picking.type'].browse(vals['picking_type_id'])
    #     # if pick_type.name=='Receipts' or pick_type.name=='Internal Transfers' or pick_type.name=='Manufacturing':
    #     if pick_type.name=='Pick' or pick_type.name=='Pack' or pick_type.name=='Delivery Orders':
    #         # if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
    #         #     vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
    #         vals['name'] = False

    #     # TDE FIXME: what ?
    #     # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
    #     # As it is a create the format will be a list of (0, 0, dict)
    #     if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
    #         for move in vals['move_lines']:
    #             if len(move) == 3:
    #                 move[2]['location_id'] = vals['location_id']
    #                 move[2]['location_dest_id'] = vals['location_dest_id']
    #     res = super(Picking, self).create(vals)
    #     res._autoconfirm_picking()
        
    #     return res

    # @api.multi
    # def button_validate(self):
    #     self.ensure_one()
    #     if not self.move_lines and not self.move_line_ids:
    #         raise UserError(_('Please add some lines to move'))
    #     date=datetime.datetime.now()
    #     a=(date.strftime('%y'))
    #     b=int(a)+1
    #     p=' '
    #     c='-'
    #     p=str(a)+c+str(b)
    #     if not self.name:
    #         # vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
    #         if self.picking_type_id.name=='Delivery Orders':
    #             self.name=self.picking_type_id.sequence_id.next_by_id().replace('x',p)
    #         elif self.picking_type_id.name=='Receipts':
    #             self.name=self.picking_type_id.sequence_id.next_by_id()
    #         else:
    #             self.name=self.picking_type_id.sequence_id.prefix


   

class StockMove(models.Model):
    _inherit='stock.move'
    
    test_pick=fields.Char(compute='assign_test_pick', store=True)
    challan_quantity=fields.Float(string="Challan Quantity",store=True)
    po_quantity=fields.Float(string="PO Quantity",compute='assign_value_to_po_qty',store=True)
    receive_quantity=fields.Float(string="Receive Quantity")
    inspected_quantity=fields.Float(string="Inspected Quantity")
    accepted_quantity=fields.Float(string="Accepted Quantity")
    dispatch_clerance=fields.Float(string="Dispatch Clearance",compute='assign_value_to_dispatched_clerance_qty',store=True)
    packing_quantity=fields.Float(string="Packing Quantity")
    sale_line_id=fields.Many2one('sale.order.line', 'Sale Line')

    # This Function Used For Assign Value  
    @api.depends('picking_type_id')
    def assign_test_pick(self):
        for i in self:
            if i.picking_type_id:
                i.test_pick=i.picking_type_id.name
    
    
    # This Function Used For Assign Value To PO Qty
    @api.depends('product_uom_qty')
    def assign_value_to_po_qty(self):
        for move in self:
            if move.product_uom_qty:
                move.po_quantity=move.product_uom_qty
    
    
    # This Function Used For Assign Challan Number To Receive
    @api.onchange('challan_quantity')
    def assign_number_to_receive(self):
        for move in self:
            move.receive_quantity = move.challan_quantity

    
    # This Function Used For Assign Reveive Qty To Done
    @api.onchange('receive_quantity')
    def assign_number_to_done(self):
        for move in self:
            if move.picking_type_id.name == 'Receipts':
                move.quantity_done = move.receive_quantity

    # This Function Used For Done To Assign Reveive Qty
    @api.onchange('quantity_done')
    def assign_number_to_reserv_quantity(self):
        for move in self:
            if move.picking_type_id.name == 'Receipts':
                move.receive_quantity = move.quantity_done
    
    
    @api.onchange('quantity_done')
    def assign_value_to_inspected_qty(self):
        for move in self:
            if move.picking_type_id.name == 'In To Quality':
                move.inspected_quantity = move.quantity_done
          

    # Auto Set Value From Inspected Quantity To Quantity Done
    @api.onchange('inspected_quantity')
    def assign_value_to_reserve_qty(self):
        for move in self:
            if move.picking_type_id.name == 'In To Quality':
                move.quantity_done=move.inspected_quantity

    
    # Validation On Inspected Quantity For PO
    @api.onchange('inspected_quantity')
    def validation_for_inspected_qty(self):
        for move in self:
            if move.inspected_quantity > move.reserved_availability:
                raise UserError(_("Please Enetr Valid Inspected Quantity")) 
    
    
    # Auto Set Value From Accepted Quantity To Quantity Done
    @api.onchange('accepted_quantity')
    def assign_value_to_reserve(self):
        for move in self:
            if move.picking_type_id.name == 'Quality To Stock':
                move.quantity_done=move.accepted_quantity
   
    
    # Auto Set Value From Quantity Done To Accepted Quantity
    @api.onchange('quantity_done')
    def assign_value_to_accepted(self):
        for move in self:
            if move.picking_type_id.name == 'Quality To Stock':
                move.accepted_quantity = move.quantity_done

    
    # Validation On Inspected Quantity For PO
    @api.onchange('accepted_quantity')
    def validation_for_acceped_qty(self):
        for move in self:
            if move.picking_type_id.name == 'Quality To Stock':
                if move.accepted_quantity > move.reserved_availability:
                    raise UserError(_("Please Enter Valid Accepted Quantity"))  

      
    # This Function Used For Assign Value To Dispatch Clerance Quantity
    @api.depends('reserved_availability')
    def assign_value_to_dispatched_clerance_qty(self):
        for move in self:
            if move.picking_type_id.name == 'Delivery Orders' or move.picking_type_id.name == 'Pick':
                if move.reserved_availability:
                    move.dispatch_clerance=move.reserved_availability

    
    # This Function Is For Set Auto Set Value To Dispatched Clearance
    @api.onchange('quantity_done')
    def assign_value_to_dispatch_qty(self):
        for move in self:
            if move.picking_type_id.name == 'Pick':
                move.dispatch_clerance = move.quantity_done

    
    # This Function Is For Set Auto Set Value To Quantity Done
    @api.onchange('dispatch_clerance')
    def assign_value_to_quantity_done(self):
        for move in self:
            if move.picking_type_id.name == 'Pick':
                move.quantity_done = move.dispatch_clerance 


    # This Function Is For Set Auto Set Value To Accepetd Quantity
    @api.onchange('quantity_done')
    def assign_value_to_accepted_qty(self):
        for move in self:
            if move.picking_type_id.name == 'Delivery Orders':
                move.packing_quantity = move.quantity_done
    
       
    # This Function Is For Set Auto Set Value To Quantity Done From Accepted Quantity
    @api.onchange('packing_quantity')
    def assign_value_from_packing_quantity_to_quantity_done(self):
        for move in self:
            if move.picking_type_id.name == 'Delivery Orders':
                 move.quantity_done = move.packing_quantity
    
    
    # Validation For Dispatched Clearance
    @api.onchange('dispatch_clerance')
    def validation_dispatch_clerance(self):
        for move in self:
            if move.picking_type_id.name == 'Pick':
                if move.dispatch_clerance > move.reserved_availability:
                    raise UserError(_("Please Enter Valid Dispatched Clearance"))


    # Validation For Packing Quantity
    @api.onchange('packing_quantity')
    def validation_for_packing_quantity(self):
        for move in self:
            if move.picking_type_id.name == 'Delivery Orders':
                if move.packing_quantity > move.reserved_availability:
                    raise UserError(_("Please Enter Valid Packing Quantity"))


    # @api.multi
    # def write(self,vals):
    #     for move in self:
    #         if move.picking_type_id.name == 'Delivery Orders':
    #             if vals["packing_quantity"] > vals["reserved_availability"]:
    #                 raise UserError(_("Please Enter Valid Packing Quantity"))

        


    
    



    



    
    



        

