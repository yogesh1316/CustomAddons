from odoo import api,fields,models,_
from odoo.exceptions import UserError
        
# Created By | Created Date |Info.
# Pradip    |13-03-19 | Material Group Master   


class Material_group_master(models.Model):
    _name='material_group.master'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name='group_description'
    _description='Material Group Master'

    _sql_constraints=[('unique group description','unique(unique_group_description)','Please Enter Unique Group Description.')]

    group_description=fields.Char(string='Group Description',required=True,track_visibility='onchange',help='Group Description')
    unique_group_description=fields.Char('Unique Group Description',compute='unique_grp_desc_fun',store=True)
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate")
    
    # Created By | Created Date |Info.
    # Pradip    |13-03-19 | group_description  Unique   

    @api.depends('group_description')
    def unique_grp_desc_fun(self):
        for i in self:
            desc_text=str(i.group_description).lower()
            text=desc_text.replace(' ','')
            i.unique_group_description=text.strip()

    # Created By | Created Date |Info.
    # Pradip    |13-03-19 | group_description  Uppercase   


    @api.onchange('group_description')
    def set_upper(self):
        if self.group_description:
            self.group_description=str(self.group_description).upper()
        return
    
    # Created By | Created Date |Info.
    # Pradip    |13-03-19 | create  method override  

    @api.model
    def create(self,values):
        if 'group_description' in values:
            if values['group_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Group Description."))
        return super(Material_group_master,self).create(values)

    # Created By | Created Date |Info.
    # Pradip    |13-03-19 | write  method override  
    @api.multi
    def write(self,values):
        if 'group_description' in values:
            if values['group_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Group Description."))
        return super(Material_group_master,self).write(values)
