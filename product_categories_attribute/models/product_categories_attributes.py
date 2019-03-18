# -*- coding: utf-8 -*-

from odoo import models, fields, api

# create_by | create_date | update_by | update_date
# Chandrakant  1/03/2019   
# Info : create for  attribute of item


class product_categories_attribute(models.Model):
    _inherit = 'product.category'

    categories_attr = fields.One2many('category.attribute','product_category_id')


    
    

    
class product_categories_attribute(models.Model):
    _name = 'category.attribute'
    _rec_name='attribute'

    product_category_id=fields.Many2one('product.category')
    attribute = fields.Char(string='Attribute')
    attributes = fields.Many2one('category.attribute',string='Attributes')
    uom= fields.Many2one('product.uom',string='UOM')
    