from odoo import api, fields, models


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
