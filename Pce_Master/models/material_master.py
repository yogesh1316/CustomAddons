from odoo import api,fields,models,_
from odoo.exceptions import UserError,ValidationError

# Created By | Created Date |Info.
# Pradip    |14-03-19 | Material Master  

class Material_master(models.Model):
    _name='material.master'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name='material_description'
    _description='Material Master'

    _sql_constraints=[('unique material description','unique(unique_material_description)','Please Enter Unique Material Description')]
    #('unique combination of material_description and material_group_description','unique(material_description,material_group_description)','Please Enter Unique Material Description and Material Group Description')]
    
    material_description=fields.Char(string="Material Description",required=True,track_visibility='onchange',help="Material Description")
    unique_material_description=fields.Char(compute='unique_material_description_fun',store=True)
    material_group_description=fields.Many2one('material_group.master',string='Group Description',required=True,track_visibility='onchange',help="Material Group Description")
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate")

    # Created By | Created Date |Info.
    # Pradip    |14-03-19 | material_description Unique  

    @api.depends('material_description')
    def unique_material_description_fun(self):
        for i in self:
            text=str(i.material_description).lower()
            text_str=text.replace(' ','')
            i.unique_material_description=text_str.strip()

    # Created By | Created Date |Info.
    # Pradip    |14-03-19 | material_description uppercase  

    @api.onchange('material_description')
    def _set_upper(self):
        if self.material_description:
            self.material_description=str(self.material_description).upper()
        return 

    # Created By | Created Date |Info.
    # Pradip    |14-03-19 | create method override  

    @api.model
    def create(self,values):
        if 'material_description' in values:
            if values['material_description'].replace(' ','')=='':
                raise UserError(_('Please Enter Material Description'))
        return super(Material_master,self).create(values)
    
    # Created By | Created Date |Info.
    # Pradip    |14-03-19 | write method override 

    @api.multi
    def write(self,values):
        if 'material_description' in values:
            if values['material_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Material Description"))
        return super(Material_master,self).write(values)

    
