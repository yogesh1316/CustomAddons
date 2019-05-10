from odoo import api, fields, models, _

# Created By | Created Date |Info.
# Pradip     |09-05-19      |res_grp field added ,get groups
 
class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    res_grp=fields.Many2one('res.groups',string='Access Rights Groups')
    

