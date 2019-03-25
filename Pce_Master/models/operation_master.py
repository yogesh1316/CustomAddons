from odoo import api,fields,models,_
from odoo.exceptions import UserError,ValidationError


# Created By | Created Date |Info.
# Pradip    |15-03-19 | operation.master  
    

class Operation_master(models.Model):
    _name='operation.master'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    _rec_name='operation_description'
    _description='Operation Master'

    _sql_constraints=[('unique operation_description','unique(unique_operation_description)','Please Enter Unique Operation Description')]


    operation_description=fields.Char(string='Operation Description',required=True,track_visibility='onchange',help="Operation Description")
    unique_operation_description=fields.Char(compute='_unique_operation_description',store=True)
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate")
    
  #  oper_mst_line=fields.One2many('operation.master.line','oper_mst_id')

    # Created By | Created Date |Info.
    # Pradip    |15-03-19 | operation_description unique  
    

    @api.depends('operation_description')
    def _unique_operation_description(self):
        for i in self:
            text=str(i.operation_description).lower()
            data=text.replace(' ','')
            i.unique_operation_description=data.strip()
    
    # Created By | Created Date |Info.
    # Pradip    |15-03-19 | operation_description uppercase  

    @api.onchange('operation_description')
    def _set_upper(self):
        if self.operation_description:
            self.operation_description=str(self.operation_description).upper()
        return

    # Created By | Created Date |Info.
    # Pradip    |15-03-19 | create method override  

    @api.model
    def create(self,values):
        if 'operation_description' in values:
            if values['operation_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Operation Description"))
        return super(Operation_master,self).create(values)


    # Created By | Created Date |Info.
    # Pradip    |15-03-19 | write method override

    @api.multi
    def write(self,values):
        if 'operation_description' in values:
            if values['operation_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Operation Description"))
        return super(Operation_master,self).write(values)


  