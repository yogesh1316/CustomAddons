from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
import time
class account_invoice_inhe(models.Model):
    _inherit = 'account.invoice.line'


    #opf_name = ields.Text(string='OPF Name', required=True,readonly=True)
    l10n_in_hsn_code = fields.Char(related='product_id.l10n_in_hsn_code',string="HSN Code")
    # hsn_code = fields.Char(related='l10n_in_hsn_code',string="HSN Code") 
    name = fields.Text(string='Description', required=True,store=True)
    price_subtotal = fields.Monetary(string='Amount',store=True, readonly=True, compute='_compute_price', help="Total amount without taxes")
    #added decimal precision 0 on Unit price by Jeevan on 23-Jan-19 
    price_unit = fields.Float(string='Unit Price', required=True)
    #added desription Sale on Invoice Form by Jeevan on 23-Jan-19
    description_opf=fields.Text(related="product_id.description_sale",string="Description")
    #Validation for received qty and entered qty
    @api.onchange('quantity')
    def _onchange_quantity_done(self):
        purqtysum =0
        invqtysum=0
        remqty=0

        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']
        account_invoice_line_obj = self.env['account.invoice.line']
        purchase_order_line_obj = self.env['purchase.order.line']

        #Get qty from sale order line
        sale_order_data=sale_order_obj.search([('name','=',self.origin)])
        print('SO ID--------------',sale_order_data.id)
        sale_order_line_data = sale_order_line_obj.search([('order_id','=',sale_order_data.id),('product_id','=',self.product_id.id)])
      
        #Get qty from account invoice line 
        account_invoice_line_data = account_invoice_line_obj.search([('origin','=',self.origin),('product_id','=',self.product_id.id)])
        for line in  account_invoice_line_data:
            invqtysum += line.quantity
      
        #print('invoice sum qty----',invqtysum)
        for line in  sale_order_line_data:
            remqty = line.qty_delivered - invqtysum
        #print('remain qty---------',remqty)
        if remqty < 0 :
            raise UserError(_('Can not enter more then received quantity'))
        # if remqty < self.quantity:
        #     raise UserError(_('Can not enter more then %d remain qty') %(remqty))       


class account_invoice_eway(models.Model):
    _inherit = 'account.invoice'  

    transmode = fields.Selection([('1','Road'),('2','Rail'),('3','Air'),('4','Ship')])
    transdistance = fields.Char(string='Distance (km)')
    transportername = fields.Char(string='Transporter Name')
    transporterid = fields.Char(string='Transporter ID')
    transdocno = fields.Char(string='Document No.')   
    vehicleno = fields.Char(string='Vehicle No.')
    vehicletype = fields.Selection([('R','Regular'),('O','ODC')])
    transdocdate = fields.Date(string='Transaction doc. date',index=True,help="Transaction date should be greater then invoice date", copy=False)
    upload_lines=fields.One2many('upload_tab.info', 'invoice_order_id', string='Order Lines')
    opf_origin=fields.Char("OPF Number")
    origin = fields.Char(string='Source Document',
    help="Reference of the document that produced this invoice.",
    readonly=True, states={'draft': [('readonly', False)]})
    
    #Method to write opf_origin for all existing records
    #@api.multi
    #def set_opf_name(self):
        #method_start=time.time()
        #for inv in self:
            #print("opf_origin=============>",inv.origin)
            #search_start=time.time()
            #sale_ord_obj=self.env['sale.order'].search([('name','=',inv.origin)])
            #search_end=time.time()
            #print("Time taken for search======>",search_end-search_start)
            #inv.opf_origin=sale_ord_obj.opf_name
            #print("inv.opf_origin=============>",inv.opf_origin)
        #method_end=time.time()
        #print("Time taken for method======>",method_end-method_start)
    
    
    #Validation for invoice_line_tax_id (Jeevan December 6th 2018) 
    def account_line_tax_validation(self):
        for order in self:
            if order.invoice_line_ids and order.type=="out_invoice":
                if order.partner_shipping_id:
                    #print("1234")
                    if order.partner_shipping_id.state_id.name=='Maharashtra':
                        for line in order.invoice_line_ids:
                            if line.invoice_line_tax_ids.tax_group_id.name=='IGST':
                                raise UserError(_('The tax specified for "{}" is incorrect'.format(line.name)))
                    else:
                        for line in order.invoice_line_ids:
                            if line.invoice_line_tax_ids.tax_group_id.name!='IGST':
                                raise UserError(_('The tax specified for {} is incorrect'.format(line.name)))
                else:
                    raise UserError(_("Should specify Shipping Address"))
    #Upload docs of sale_order and purchase_order(Jeevan December 6th 2018) 
    def upload_tab_info(self):
        sale_order_obj=self.env['sale.order'].search([('name','=',self.origin)])
        purchase_obj=self.env['purchase.order'].search([('origin','=',sale_order_obj.opf_name)])
        for order in self:
            if purchase_obj.dr_lines or sale_order_obj.order_upload_line:
                for line in purchase_obj.dr_lines if purchase_obj.dr_lines else sale_order_obj.order_upload_line:
                   line.invoice_order_id=self.id
            

    @api.multi
    def action_invoice_open(self):
        #Validation for invoice_line_tax_id
        #self.account_line_tax_validation()
        #Upload docs of sale_order and purchase_order
        #self.upload_tab_info()
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
            raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()


class upload_file_purchase(models.Model):
    _inherit = 'upload_tab.info'
    invoice_order_id = fields.Many2one('account.invoice',string='upload reference', ondelete='cascade',
     index=True, copy=False,default=0)
    


        

        
