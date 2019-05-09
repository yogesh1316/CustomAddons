# -*- coding: utf-8 -*-

from odoo  import api,fields,models,_ 


class spec_attrib_master(models.Model):
    _name = 'spec.attrib.master'

    attribute_text=fields.Text(string="Attribute_Text")
    attribute_note=fields.Text(string="Attribute_Note")
    uom=fields.Float(string="UOM")
    master_id=fields.Many2one('spec.master')

    