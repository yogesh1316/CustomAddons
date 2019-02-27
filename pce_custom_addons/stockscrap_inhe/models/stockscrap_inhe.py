from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round


# create_by | create_date | update_by | update_date
# Ganesh      13/10/2018    
# Info : Add reason for scrap 


class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    _order = 'id desc'

    reason_desc=fields.Many2one('reason.master','Reason')

    def _prepare_move_values(self):
        vals = super(StockScrap, self)._prepare_move_values()
        if self.production_id:
            vals['origin'] = vals['origin'] or self.production_id.name
            if self.product_id in self.production_id.move_finished_ids.mapped('product_id'):
                vals.update({'production_id': self.production_id.id})
            else:
                vals.update({'raw_material_production_id': self.production_id.id})
        return vals




