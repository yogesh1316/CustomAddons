from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    quote_bom_number = fields.Integer(compute='_compute_bom_nos', string="Number of Quotation BOM")
    # quote_bom_number = fields.Integer(compute='_compute_bom_nos', string="Number of Quotation BOM")
    order_quotation_bom_ids=fields.One2many('quotation.mrp_bom','order_id')
    @api.depends('order_line.quotation_bom_ids')
    def _compute_bom_nos(self):
        for order in self:
            if order.order_line:
                nbr = 0
                for line in order.order_line:
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
    
    @api.multi
    def quotation_mrp_bom_new(self):
        form=self.env['ir.model.data'].xmlid_to_res_id('quotation_mrp_bom.qutation_mrp_bom_forms',raise_if_not_found=True)
        for order in self:
            product_id=order.product_id.id
            product_tmpl_id=order.product_id.product_tmpl_id.id
            product_uom_id=order.product_uom
            description=order.name
            quantity=order.product_uom_qty
            order_id=order.order_id.id
            order_line_id=order.id
        result={'name':'quotation_mrp_bom_form',
                'view_type':'form',
                'res_model':'quotation.mrp_bom',
                'view_id':form,
                'context':{ 'default_product_id':product_id,
                            'default_product_tmpl_id':product_tmpl_id,
                            'default_product_uom_id':product_uom_id.id,
                            'default_product_qty':quantity,
                            'default_order_id':order_id,
                            'default_order_line_id':order_line_id,
                            "default_description":description
                            },
                'type':'ir.actions.act_window',
                'view_mode':'form'
                }
        return result