from odoo import api,fields,models,_
from odoo.exceptions import UserError,ValidationError


# Created By | Created Date |Info.
# Pradip    |14-03-19 | take operation.master dropdown from master

class MrpRoutingWorkcenter_inherit(models.Model):
    _inherit= 'mrp.routing.workcenter'

    _sql_constraints = [('constraint name', 'unique(name,routing_id)', 'Please Enter Unique Combination of Routing Name	and Operation'),]

    name = fields.Many2one('operation.master','Operation', required=True)

  

