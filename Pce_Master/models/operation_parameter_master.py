from odoo import api,fields,models,_
from odoo.exceptions import UserError,ValidationError


# Created By | Created Date |Info.
# Pradip    |19-03-19 | operation.parameter.master  
    

class Operation_parameter_master(models.Model):
    _name='operation.parameter.master'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    _rec_name='oper_descr_id'
    _description='Operation Parameter Master'

    oper_descr_id=fields.Many2one('operation.master',required=True,string='Operation Description',help="Operation Description")
    #_sql_constraints=[('unique operation_description','unique(unique_operation_description)','Please Enter Unique Operation Description')]


    # operation_description=fields.Char(string='Operation Description',required=True,track_visibility='onchange',help="Operation Description")
    # unique_operation_description=fields.Char(compute='_unique_operation_description',store=True)
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate")
    
    oper_param_mst_line=fields.One2many('operation.parameter.master.line','oper_mst_id')


# Created By | Created Date |Info.
# Pradip    |19-03-19 | operation.parameter.master.line  

class Operation_parameter_master_line(models.Model):
    _name='operation.parameter.master.line'
    _description='Operation Parameter Master Line'

    oper_mst_id=fields.Many2one('operation.master')
    parm_mst_id=fields.Many2one('parameter.master',required=True)
    tolerance=fields.Char(string="Tolerance")
    re_mark=fields.Text('Rmrk')

