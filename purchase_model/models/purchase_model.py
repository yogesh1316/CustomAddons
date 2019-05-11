#0 -*- coding: utf-8 -*-

# create_by | create_date | update_by | update_date
# Yogeshwar Chaudahri
# Info : This model contain the information about purchase amendment

from odoo import models, fields, api,tools,_
from odoo.exceptions import ValidationError,UserError
from datetime import datetime
import datetime



class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    tax_line_id =fields.Many2many('account.tax', domain=['|', ('active', '=', False), ('active', '=', True)])
    revise =fields.Integer(string="Amendment Number", store=True ,track_visibility='onchange')
    purchase_line =fields.One2many("purchase.order.amendment",'purchase_id')
    transport_id =fields.Many2one("transport_mode.master")
    default_check_box =fields.Boolean(string="Select Default Taxes For Order Line",store=True,readonly=False)
    box_check =fields.Selection([('yes','Yes'),('no','No')],'box_check',default='no')
    ven_ref_date =fields.Date(string="Vendor Reference Date",store=True)
    internal_ref_no =fields.Char(string="Internal Reference Number")
    internal_ref_date =fields.Date(string="Internal Reference Date")
    po_categ_id =fields.Many2one("category.purchase.master",string="Category",help="Select Purchase Category")
    category_description =fields.Char(string="Description",compute="_category_purchase_description",store=True)
    indent_type_id=fields.Many2one("indent.type.master",string="Indent Type",help="Select Indent Document Type")
    

    #Set Default Taxes For Order Line
    @api.onchange('tax_line_id')
    def default_tax_id_for_child(self):
        for order in self:
            for line in order.order_line:
                line.taxes_id = order.tax_line_id


    #set default taxes to the order_line by item wise
    @api.onchange('order_line')
    def default_taxes_change(self):
        for order in self:
            if order.order_line:
                for line in order.order_line :
                    if line.product_id and order.default_check_box == True:
                        line.taxes_id = self.tax_line_id


    # In order Line Or Default Taxes user forgot to select taxes rise user error
    @api.constrains('order_line')
    def check_taxes_is(self):
        for order in self:
            if order.order_line:
                for line in order.order_line:
                    if not line.taxes_id:
                        raise ValidationError("Please Enter Taxes")


    # Add Unique Item For Order Line
    @api.onchange('order_line')
    def unique_product(self):
        list =[]
        product =False
        for order in self.order_line:
            product = order.product_id.id
            if not(product in list):
                list.append(product)
            else:
                raise UserError(('Duplicate Order Line Item %s Exists.') % order.product_id.name)


    # Description For Category
    @api.depends('po_categ_id','category_description')
    def _category_purchase_description(self):
        for order in self:
            order.category_description = order.po_categ_id.category_name


    # update_by | update_date
    # Yogeshwar Chaudhari | 1/3/2019 change sequnce of model using category field
    @api.model
    def create(self,vals):
        vals['name'] = ' '
        return super(PurchaseOrder, self).create(vals)

   
    # If user want to confirm order then check in order line has product is avaliable or not
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.po_categ_id:
                if not order.po_categ_id:
                    raise UserError(_(" Please Select Category"))
            if order.indent_type_id:
                if not order.indent_type_id:
                    raise UserError(_("Please Select Indent Type"))
            if order.indent_type_id: # Generate Sequence For Indent Type 
                self.name=self.env['ir.sequence'].next_by_code('indent.type.master')or'/'
            if order.po_categ_id:
                if self.po_categ_id.po_category:     # Generate Sequence For Purchasr Order Using Different Category  
                    self.name=self.env['ir.sequence'].next_by_code('purchase.order').replace('PL',self.po_categ_id.po_category) or '/'
            if order.order_line:
                for line in order.order_line:
                    if not line.taxes_id:
                        raise UserError(" Please Select Taxes")
            if order.po_categ_id:
                if not order.transport_id:
                    raise UserError("Please Select Transport Mode")
            if order.po_categ_id:
                if not order.incoterm_id:
                    raise UserError("Please Select Transport Cost")
            if order.po_categ_id:
                if not order.payment_term_id:
                    raise UserError("Please Select Payment Terms")
            if not order.order_line:
                raise UserError("Please Select Product")
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id)):
                    # or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True
        


    # To Create Amendment For Purchase Order
    @api.multi
    def write(self,vals):
        if vals:
            if 'state' not in vals and 'group_id' not in vals:
                for order in self:
                    if order.state == 'purchase':
                        if "box_check" in vals:
                            if vals["box_check"] == 'yes':
                                    self.create_revision()
                                    vals['revise']=self.revise + 1
                                    vals['box_check']='no'
                                    order.state = 'draft'
                        else:
                            raise UserError("Please Select Amendment Order Other Wise Discard")
        var=super(PurchaseOrder,self).write(vals)
        return var

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
            'currency_id':self.currency_id.id,
            'origin':self.origin,
            'amount_untaxed':self.amount_untaxed,
            'amount_tax':self.amount_tax,
            'amount_total':self.amount_total,
            'default_location_dest_id_usage':self.default_location_dest_id_usage,
            'dest_address_id':self.dest_address_id,
            'revise':self.revise,
            'ven_ref_date':self.ven_ref_date,
            'internal_ref_no':self.internal_ref_no,
            'internal_ref_date':self.internal_ref_date,
            'requisition_id':self.requisition_id.id,
            'indent_type_id':self.indent_type_id.id,
            'po_categ_id':self.po_categ_id.id
            }
        purchase_order_revise_obj=self.env['purchase.order.amendment'].create(revise_vals)
        purchase_order_revise_obj.purchase_id=self.id
        for i in self.order_line:
            revise_line_vals={
                'purchase_revise_id':purchase_order_revise_obj.id,
                'name':i.name,
                'product_id':i.product_id.id,
                'date_planned':i.date_planned,
                'product_qty':i.product_qty,
                'qty_received':i.qty_received,
                'qty_invoiced':i.qty_invoiced,
                'product_uom':i.product_uom,
                'price_unit':i.price_unit,
                'taxes_id':i.taxes_id,
                'price_subtotal':i.price_subtotal
             }
            purchase_order_revise_obj.purchase_revise_line=[(0,0,revise_line_vals)]
            purchase_order_revise_obj.purchase_id=self.id


class PurchaseOrderLine(models.Model):
    _inherit="purchase.order.line"

    indent_type_id=fields.Many2one("indent.type.master",string="Indent Type", store=True, related='order_id.indent_type_id')
    # po_categ_id = fields.Many2one("category.purchase",store=True, string="Category", related='order_id.po_categ_id')    
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True,readonly=True, store=True)      
    
    '''
    Below Code Is For Filter The Product On The Change OF Selected Category From Order
    '''   
    @api.multi
    @api.onchange('product_id')
    def display_product_category_selection(self):
        for order in self:
            if order.indent_type_id:
                if not order.indent_type_id:
                    raise UserError(_("Please Select Indent Type"))
        for order in self:
            if order.indent_type_id:
                pp=[]
                domain={}
                product_tmpl_obj=self.env['product.template'] #made object of product template
                ptmpl_ids=product_tmpl_obj.search([('type','=',self.indent_type_id.product_type)and('type','!=','product')]) #Search for type in order into product template 
                product_obj=self.env['product.product'] #made object for product product
                for i in ptmpl_ids:
                    pro_ids=product_obj.search([('product_tmpl_id','=',i.id)])
                    for pro in pro_ids:
                        pp.append(pro.id)
                domain['product_id']=[('id','in',pp)]
                return {'domain':domain}


class Picking(models.Model):
    _inherit="stock.picking"

    revise =fields.Integer(string="Amendment Number",track_visibility='onchange')
    challan_no=fields.Char(string="Challan Number",help="Challan Number")
    challan_date=fields.Date(string="Challan Date",help="Challan Date")
    scheduled_date = fields.Datetime(
        'Scheduled Date', compute='_compute_scheduled_date', inverse='_set_scheduled_date', store=True,
        index=True, track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},default=fields.Datetime.now)

    
    #Validation For Schedule Date raise user error if date is less than todays date
    # create_by | create_date | update_by | update_date
    # Yogeshwar Chaudahri | 29/04/2019
    @api.onchange('scheduled_date')
    def scheduled_date_check(self):
        today = datetime.datetime.now()
        if self.scheduled_date < str(today):
            raise UserError(_("Please Select Valid Scheduled Date"))


    @api.one
    @api.depends('move_lines.date_expected')
    def _compute_scheduled_date(self):
        if self.move_type == 'direct':
            self.scheduled_date = min(self.move_lines.mapped('date_expected') or [fields.Datetime.now()])
        else:
            self.scheduled_date = max(self.move_lines.mapped('date_expected') or [fields.Datetime.now()])

    
    @api.one
    def _set_scheduled_date(self):
        self.move_lines.write({'date_expected': self.scheduled_date})    
    
    
    @api.onchange('challan_no')
    def partner_challan_no_exist(self):
        for picking in self:
            stock_picking_obj=self.env['stock.picking']
        rect=stock_picking_obj.search([('origin','=',picking.origin),('challan_no','=',self.challan_no)])
        if picking.picking_type_id.name == 'Receipts':
            if rect:
                raise UserError(_("Challan Number Already Exists Re"))
        if picking.picking_type_id.name == 'In To Quality':
            if rect:
                raise UserError(_("Challan Number Already Exists ITQ"))
        if picking.picking_type_id.name == 'Quality To Stock':
            if rect:
                raise UserError(_("Challan Number Already Exists QTS"))

    
    @api.onchange('challan_date')
    def partner_challan_date_exist(self):
        for i in self:
            obj_stock_picking=self.env['stock.picking']
        rect1=obj_stock_picking.search([('origin','=',i.origin),('challan_date','=',self.challan_date)])
        if i.picking_type_id.name == 'Receipts':
            if rect1:
                raise UserError(_("Challan Date Already Exists In Receipts"))
        if i.picking_type_id.name == 'In To Quality':
            if rect1:
                raise UserError(_("Challan Date Already Exists In ITQ"))
        if i.picking_type_id.name == 'Quality To Stock':
            if rect1:
                raise UserError(_("Challan Date Already Exists In QTS"))
    
    
    @api.onchange('challan_date')
    def date_check(self):
        today = datetime.datetime.now()
        if self.challan_date > str(today):
            raise UserError(_("Please Select Valid Date "))

    
    @api.multi
    def button_validate(self):
        res=super(Picking,self).button_validate()
        po_obj=self.env['purchase.order']
        rect=po_obj.search([('name','=',self.origin)])
        if not self.challan_no and self.picking_type_id.name=='Receipts':
            raise UserError(_(" Please Enter Challan Number "))
        if not self.challan_date and self.picking_type_id.name=='Receipts':
            raise UserError (_(" Please Select Challan Date "))
        # for i in self.move_lines:#Generate Sequence For Product Type Is Consumable Or Service 
            # if i.product_id.product_tmpl_id.type == 'consu':
            #     self.name=self.env['ir.sequence'].next_by_code('grn.product.type.service')or'/'
        pdata = self.env['purchase.order'] #Make For To Generate Sequence As 'SG' On GRN At the time of Subcontract 
        if self.origin:                
            podata = pdata.search([('name','=',self.origin)])  
        for j in self:
            if 'GEN' in j.origin and j.picking_type_id.name == 'Receipts':#Generate Sequence For Indent Type Of GRN
                self.name=self.env['ir.sequence'].next_by_code('grn.indent.type.master')or'/'
        date=datetime.datetime.now()
        a=(date.strftime('%y'))
        b=int(a)+1
        p=' '
        c='-'
        p=str(a)+c+str(b)
        if not podata.mrp_id: # Make To Generate Sequence As 'SG'     
            if not self.name:
                if self.picking_type_id.name=='Delivery Orders':
                    self.name=self.picking_type_id.sequence_id.next_by_id().replace('x',p)
                elif self.picking_type_id.name=='Receipts':
                    self.name=self.picking_type_id.sequence_id.next_by_id()
                else:
                    self.name=self.picking_type_id.sequence_id.next_by_id()
        else:            
            self.name = self.env['ir.sequence'].next_by_code('grn.sub.seq') or '/'
        for order in self:
            if order.move_lines:
                for line in order.move_lines:
                    if not line.move_orig_ids:
                        move1=line
                        move2=move1.move_dest_ids
                        move3=move2.move_dest_ids
                        if move2:
                            move2.picking_id.partner_id=order.partner_id
                            move2.picking_id.grn_name=order.name
                            move2.challan_quantity=line.challan_quantity
                            move2.receive_quantity=line.receive_quantity  
                        if move3:
                            move3.picking_id.partner_id=order.partner_id
                            move3.picking_id.grn_name=order.name
                            move3.challan_quantity=line.challan_quantity
                            move3.receive_quantity=line.receive_quantity        
                    else:
                        if line.move_orig_ids:
                            move2=line
                            move3=move2.move_dest_ids
                            move4=line
                            move5=move4.move_dest_ids
                            if move3:
                                move3.inspected_quantity=line.inspected_quantity
                            if move5:
                                move5.dispatch_clerance=line.dispatch_clerance                            
        rect.button_done()
        return res



    @api.model
    def create(self, vals):
        # TDE FIXME: clean that brol
        # defaults = self.default_get(['name', 'picking_type_id'])
        pick_type=self.env['stock.picking.type'].browse(vals['picking_type_id'])

        # if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
        #     vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
        if pick_type.name=='Pick' or pick_type.name=='Delivery Orders' or pick_type.name == 'Receipts':
            vals['name']=False
        # TDE FIXME: what ?
        # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
        # As it is a create the format will be a list of (0, 0, dict)
        if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
            for move in vals['move_lines']:
                if len(move) == 3:
                    move[2]['location_id'] = vals['location_id']
                    move[2]['location_dest_id'] = vals['location_dest_id']
        res = super(Picking, self).create(vals)
        res._autoconfirm_picking()
        return res
    
  
        

class PurchaseOrderAmendment(models.Model):
    _name="purchase.order.amendment"

    po_categ_id =fields.Many2one("category.purchase.master",string="Category")
    indent_type_id=fields.Many2one("indent.type.master",string="Indent Type")
    requisition_id = fields.Many2one('purchase.requisition', string='Purchase Agreement', copy=False)
    purchase_revise_line=fields.One2many("purchase.order.line.amendment",'purchase_revise_id')
    purchase_id=fields.Many2one("purchase.order")
    transport_id=fields.Many2one("transport_mode.master",store=True)
    revise=fields.Integer(string="Amendment Count", readonly=True, Strore=True)
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
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, track_visibility='always')
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
    ven_ref_date = fields.Date(string="Vendor Reference Date",store=True)
    internal_ref_no = fields.Char(string="Internal Reference Number")
    internal_ref_date = fields.Date(string="Internal Reference Date")


class PurchaseOrderLineAmendment(models.Model):
    _name="purchase.order.line.amendment"
    purchase_revise_id=fields.Many2one("purchase.order.amendment", readonly=True, store=True)
    name = fields.Text(string='Description', required=True,readonly=True, store=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True,readonly=True, store=True)
    date_planned = fields.Datetime(string='Scheduled Date', required=True, index=True,readonly=True, store=True)
    product_qty = fields.Float(string='Quantity', required=True,readonly=True, store=True)
    qty_received = fields.Float(string="Received Qty", store=True, compute_sudo=True,readonly=True)
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty",store=True,readonly=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True,readonly=True, store=True)
    price_unit = fields.Float(string='Unit Price', required=True,readonly=True, store=True)
    price_subtotal = fields.Monetary(string='Subtotal', store=True,readonly=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)],readonly=True, store=True, track_visibility='onchange')
    currency_id = fields.Many2one(related='purchase_revise_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='purchase_revise_id.date_order', string='Order Date', readonly=True,store=True)