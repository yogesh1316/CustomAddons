# -*- coding: utf-8 -*-

from odoo import models, fields, api

class inherit_product_product(models.Model):
    _inherit="product.product"

    inventory_flag=fields.Boolean()