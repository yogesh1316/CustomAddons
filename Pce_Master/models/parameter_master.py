from odoo import models,api,fields,_
from odoo.exceptions import ValidationError,UserError

# Created By | Created Date |Info.
# Pradip    |15-03-19 | parameter.master  

class Parameter_master(models.Model):
    _name='parameter.master'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    _rec_name='parameter_description'
    _description='Parameter Master'

    _sql_constraints=[('unique parameter_description','unique(unique_parameter_description)','Please Enter Unique Parameter Description')]

    parameter_description=fields.Char(string='Parameter Description',required=True,track_visibility='onchange',help="Parameter Description")
    unique_parameter_description=fields.Char(compute='_unique_parameter_description',store=True)
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate")

    # Created By | Created Date |Info.
    # Pradip    |15-03-19 | parameter_description unique  

    @api.depends('parameter_description')
    def _unique_parameter_description(self):
        for i in self:
            text=str(i.parameter_description).lower()
            text_data=text.replace(' ','')
            i.unique_parameter_description=text_data.strip()


    # Created By | Created Date |Info.
    # Pradip    |15-03-19 | parameter_description uppercase

    @api.onchange('parameter_description')
    def _set_upper(self):
        if self.parameter_description:
            self.parameter_description=str(self.parameter_description).upper()
        return
    

    # Created By | Created Date |Info.
    # Pradip    |15-03-19 | create method override

    @api.model
    def create(self,vals):
        if 'parameter_description' in vals:
            if vals['parameter_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Parameter Description"))
        return super(Parameter_master,self).create(vals)


    # Created By | Created Date |Info.
    # Pradip    |15-03-19 | write method override

    @api.multi
    def write(self,vals):
        if 'parameter_description' in vals:
            if vals['parameter_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Parameter Description"))
        return super(Parameter_master,self).write(vals)

