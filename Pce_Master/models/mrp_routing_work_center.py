from odoo import api,fields,models,_
from odoo.exceptions import UserError,ValidationError


# Created By | Created Date |Info.
# Pradip    |14-03-19 | take operation.master dropdown from master

class MrpRoutingWorkcenter_inherited(models.Model):
    _inherit= 'mrp.routing.workcenter'


    _sql_constraints = [('name valida', 'unique(name,routing_id)', 'Please Enter Unique Combination of Routing Name and Work Center Operation'),]

    name = fields.Char('Operation', compute='oper_desc_id_to_name_cpy',store=True)

    operation_descr_id = fields.Many2one('operation.master','Operation',required=True) # 1-4-2019updatedby-pradip required=true ,bcause-update-set issue to jeevan

  
   

    @api.depends('operation_descr_id','name')
    def oper_desc_id_to_name_cpy(self):
        for i in self:
            if i.operation_descr_id:
                i.name=str(i.operation_descr_id.operation_description)
      