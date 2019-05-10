from odoo import api, fields, models, _

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

# Created By | Created Date |Info.
# Pradip    |09-05-19 | if user has manager group the qty_producing field editable else non-editable

    id_check=fields.Boolean(string='id_check',compute='_id_check_user_group')

    @api.depends('id_check')
    def _id_check_user_group(self):
        # print("==============96===========>>res_user_group",res_user_group)
        for i in self:
            print("===================>>>>",i.workcenter_id.res_grp.name)
            if i.workcenter_id.res_grp.name=='User':
                print(i.workcenter_id.res_grp.name)
                i.id_check=True
            else:
                i.id_check=False
    
  
