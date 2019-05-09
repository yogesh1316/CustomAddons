#0 -*- coding: utf-8 -*-

from odoo import models, fields, api,tools
from odoo.exceptions import ValidationError,UserError

class IndentTypeMaster(models.Model):
    _name="indent.type.master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="indent_type"
    indent_type=fields.Char()
    indent_name=fields.Char()
    product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),('product','Stockable Product')], string='Product Type',required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate")


    @api.onchange('indent_type')
    def _set_upper(self):
        if self.indent_type:
            self.indent_type=str(self.indent_type).upper()
        return