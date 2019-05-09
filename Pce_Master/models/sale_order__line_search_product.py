from odoo import models, fields, api, _



# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
    
#     _description = 'Sales Order Line'

class ProductProduct(models.Model):
    _inherit = "product.product"


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        print("Product_Search")
        if self.product_id.name:
            args = args if args else []
            args.extend(['|', ['name', 'ilike', name],
                        ])
            name = ''
        return super(ProductProduct, self).name_search(name=name,
                                                   args=args,
                                                   operator=operator,
                                                   limit=limit)