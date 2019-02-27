from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    quotation_mrp_bom_id=fields.Many2one('quotation.mrp_bom','Quotation Mrp')

