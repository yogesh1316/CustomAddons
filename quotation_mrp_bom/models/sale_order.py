from odoo import api, fields, models, _
import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quote_bom_number = fields.Integer(compute='_compute_bom_nos', string="Number of Quotation BOM")
    # quote_bom_number = fields.Integer(compute='_compute_bom_nos', string="Number of Quotation BOM")
    order_quotation_bom_ids=fields.One2many('quotation.mrp_bom','order_id')

    # Added By Ganesh May-2019
    cust_inspection_req = fields.Selection([('1', 'Yes'),('2', 'No')], string='Customer Inspection Required')
    cust_inspection_site_req = fields.Selection([('1', 'Yes'),('2', 'No')], string='Customer Inspection At Site')
    cust_po_date = fields.Datetime(string="Customer PO Date") 
    client_order_ref = fields.Char(string='Customer PO Reference', copy=False)
    cust_note = fields.Char(string='Customer Note')
    so_type_id = fields.Many2one("saleorder.type.master",string="Sale Order Type",help="Select Sale Order Type",required=True,)
    transport_id =fields.Many2one("transport_mode.master")
    
    @api.depends('order_line.quotation_bom_ids')
    def _compute_bom_nos(self):
        for order in self:
            if order.order_line:
                for line in order.order_line:
                    nbr = 0
                    if line.quotation_bom_ids:
                        for bom in line.quotation_bom_ids:
                            if bom.id:
                                nbr += 1
                        order.quote_bom_number = nbr
    # @api.depends('pricelist_id')
    # def _set_pricelist_id(self):
    #     for order in self:
    #         if order.pricelist_id:
    #             for line in order.order_line:
    #                 line.pricelist_id=order.pricelist_id

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            date=datetime.datetime.now()
            a=(date.strftime('%y'))
            b=int(a)+1
            p=' '
            c='-'
            p=str(a)+c+str(b)
            bom = self.env['saleorder.type.master'].search([('id','=',vals['so_type_id'])])
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order').replace('L',bom.so_type).replace('x',p) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New').replace('L',bom.so_type).replace('x',p)

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(SaleOrder, self).create(vals)
        return result

class SaleOrderLine(models.Model):
    _inherit="sale.order.line"
    
    quotation_bom_ids=fields.One2many('quotation.mrp_bom','order_line_id')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict',required=False)
    pricelist_id = fields.Many2one(related="order_id.pricelist_id", string='Pricelist' , help="Pricelist for current sales order.")
    currency_id = fields.Many2one("res.currency", related='order_id.currency_id', string="Currency")

    # Added By Ganesh May-2019
    cust_item_code = fields.Char(string="Customer Item Code")
    drawing_req = fields.Selection([('1', 'Yes'),('2', 'No')], string='Drawing required (Y/N)')  
    drawing_req_date = fields.Datetime(string="Drawing Required by Date")  
    drawing_req_days = fields.Integer(string="Drawing Required in Days")  

    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        
        help="Bill of Materials allow you to define the list of required raw materials to make a finished product.")

    @api.onchange('product_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        con=[]
        domain={}
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom'].search([('product_id','=',self.product_id.id),('company_id','=',self.company_id.id)])
            for i in bom:
                if i.type == 'normal':
                    con.append(i.id)      
                else:
                    con = []
                   
            domain['bom_id']=[('id','in',con)]
            return {'domain':domain}
            
