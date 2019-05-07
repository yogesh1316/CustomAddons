#0 -*- coding: utf-8 -*-

from odoo import models, fields, api,tools
from odoo.exceptions import ValidationError,UserError

class CategoryPurchase(models.Model):
    _name="category.purchase"
    _rec_name="po_category"
    po_category=fields.Char()
    category_name=fields.Char()