#0 -*- coding: utf-8 -*-

# create_by | create_date | update_by | update_date
# Yogeshwar Chaudahri                  
# Info : This model contain the information about purchase revision 

from odoo import models, fields, api,tools
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class purchase_model(models.Model):
    _inherit = "purchase.order"
    check_box=fields.Boolean(string="Revise Purchase Order")
    revise_count=fields.Integer(string="Revise Count")
    revise_name=fields.Char(string="name",readonly=True, store=True)
    purchase_line=fields.One2many("purchase.order.revise",'purchase_id')
    category=fields.Selection([('PO Import','PI'),('PO Local','PL'),('Free Stock Local','FSL'),('Free Stock Import','FSI')],'category',required=True)
    transport_id=fields.Many2one("transport_mode.master")

# update_by | update_date
# Yogeshwar Chaudhari | 1/3/2019 change sequnce of model using category field
    @api.model
    def create(self,vals):
        if vals.get('category') == 'PO Import':
            vals['name']=self.env['ir.sequence'].next_by_code('purchase.order').replace('PL','PI') or '/'
        elif vals.get('category') == 'PO Local':
            vals['name']=self.env['ir.sequence'].next_by_code('purchase.order').replace('PL','PL') or '/' 
        elif vals.get('category') == 'Free Stock Local':
            vals['name']=self.env['ir.sequence'].next_by_code('purchase.order').replace('PL','FSL') or '/'
        elif vals.get('category') == 'Free Stock Import':
            vals['name']=self.env['ir.sequence'].next_by_code('purchase.order').replace('PL','FSI') or '/'
        return super(purchase_model, self).create(vals)
    
    @api.multi
    def button_confirm(self):
        for order in self:
            if not order.order_line:
                raise UserError(" Please Select Product First Then Go For Confirm Order")
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True

              
    @api.multi
    def write(self,vals):
        if "check_box" in vals:
            if vals["check_box"]==True:
                for order in self: 
                    if order.state=='purchase':
                        self.create_revision()
                        self.revise_count=self.revise_count + 1
                        # self.revise_name="  - AMendment-" + (str(self.revise_count))
                        vals["check_box"]=False
                    else:
                        raise UserError("Please Discard First Then Confirm Order For Make Amendment")
        rec=super(purchase_model,self).write(vals)
        return rec

    @api.multi
    def create_revision(self):
        revise_vals={
            'purchase_id':self.id,
            'name':self.name,
            'partner_ref':self.partner_ref,
            'date_order':self.date_order,
            'picking_type_id':self.picking_type_id.id,
            'date_planned':self.date_planned, 
            'incoterm_id':self.incoterm_id.id,
            'transport_id':self.transport_id.id, 
            'invoice_status':self.invoice_status,
            'payment_term_id':self.payment_term_id.id,
            'fiscal_position_id':self.fiscal_position_id.id,
            'partner_id':self.partner_id.id,
            'state':self.state,
            'notes':self.notes,
            'currency_id':self.currency_id,
            'origin':self.origin,
            'amount_untaxed':self.amount_untaxed,
            'amount_tax':self.amount_tax,
            'amount_total':self.amount_total,
            'default_location_dest_id_usage':self.default_location_dest_id_usage,
            'dest_address_id':self.dest_address_id,
            'revise_count':self.revise_count,
            'currency_id':self.currency_id.id
            }
        purchase_order_revise_obj=self.env['purchase.order.revise'].create(revise_vals)
        purchase_order_revise_obj.purchase_id=self.id
        for y in self.order_line:
            revise_line_vals={
                'purchase_revise_id':purchase_order_revise_obj.id,
                'name':y.name,
                'product_id':y.product_id.id,
                'date_planned':y.date_planned,
                'product_qty':y.product_qty, 
                'qty_received':y.qty_received,
                'qty_invoiced':y.qty_invoiced,
                'product_uom':y.product_uom,
                'price_unit':y.price_unit,
                'taxes_id':y.taxes_id,
                'price_subtotal':y.price_subtotal 
             }
            purchase_order_revise_obj. purchase_revise_line=[(0,0,revise_line_vals)]
            purchase_order_revise_obj.purchase_id=self.id


class PurchaseOrderRevise(models.Model):
    _name="purchase.order.revise"
    purchase_revise_line=fields.One2many("purchase.order.line.revise",'purchase_revise_id')
    purchase_id=fields.Many2one("purchase.order")
    transport_id=fields.Many2one("transport_mode.master",store=True)
    revise_count=fields.Integer(string="Revise Count", readonly=True, Strore=True)
    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    origin = fields.Char('Source Document', copy=False,help="Reference of the document that generated this purchase order""request (e.g. a sales order)")
    partner_ref = fields.Char('Vendor Reference', copy=False,help="Reference of the sales order or bid sent by the vendor.""It's used to do the matching when you receive the""products as this reference is usually written on the""delivery order sent by your vendor.",store=True)
    date_order = fields.Datetime('Order Date', required=True, index=True, copy=False,store=True, default=fields.Datetime.now,help="Depicts the date where the Quotation should be validated and converted into a purchase order.")
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To',required=True,help="This will determine operation type of incoming shipment")
    date_planned = fields.Datetime(string='Scheduled Date', store=True, index=True)
    incoterm_id = fields.Many2one('stock.incoterms', 'Transport Cost/ Incoterm', states={'done': [('readonly', True)]}, help="International Commercial Terms are a series of predefined commercial terms used in international transactions.",store=True)
    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'No Bill to Receive'),
        ], string='Billing Status', store=True, readonly=True, copy=False, default='no')
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position')
    date_approve = fields.Date('Approval Date', readonly=1, index=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, change_default=True, track_visibility='always', store=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency','Currency', required=True,default=lambda self: self.env.user.company_id.currency_id.id)
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    notes = fields.Text('Terms and Conditions')
    default_location_dest_id_usage = fields.Selection(related='picking_type_id.default_location_dest_id.usage', string='Destination Location Type',help="Technical field used to display the Drop Ship Address", readonly=True)
    dest_address_id = fields.Many2one('res.partner', string='Drop Ship Address',help="Put an address if you want to deliver directly from the vendor to the customer.""Otherwise, keep empty to deliver to your own company.")


class PurchaseOrderLineRevise(models.Model):
    _name="purchase.order.line.revise"
    purchase_revise_id=fields.Many2one("purchase.order.revise", readonly=True, store=True) 
    name = fields.Text(string='Description', required=True,readonly=True, store=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True,readonly=True, store=True)
    date_planned = fields.Datetime(string='Scheduled Date', required=True, index=True,readonly=True, store=True)
    product_qty = fields.Float(string='Quantity', required=True,readonly=True, store=True)
    qty_received = fields.Float(string="Received Qty", store=True, compute_sudo=True,readonly=True)
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty",store=True,readonly=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True,readonly=True, store=True)
    price_unit = fields.Float(string='Unit Price', required=True,readonly=True, store=True)
    price_subtotal = fields.Monetary(string='Subtotal', store=True,readonly=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)],readonly=True, store=True)
    currency_id = fields.Many2one(related='purchase_revise_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='purchase_revise_id.date_order', string='Order Date', readonly=True,store=True)