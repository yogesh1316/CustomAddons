from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

# create_by | create_date | update_by | update_date
# Ganesh      26/10/2018    
# Info : This master is item type for using in Product creation 

class item_type_master(models.Model):
    _name='item.type.master'   
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name='complete_name'    
    _description='Item Type Master'
         
    _sql_constraints=[('Unique Item Name','unique(unique_item_name)','Please Enter Unique Item Type Name.'),
                      ('Unique Item Code','unique(item_type_code)','Please Enter Unique Item Type Code.')]
    
    #Updated-By:Pradip|Updated-Date:12-3-19|Info.all fields added in chatter Box 

    item_type_name=fields.Char(string='Item Type Name',required=True,track_visibility='onchange',help='Item Type Description.')
    unique_item_name=fields.Char('Unique Item type name' ,compute='item_name_fun',store=True)
    # activeflag=fields.Selection([('Y','Yes'),('N','No')],default='Y', track_visibility='onchange' ,help="Hide or Show Item Type.")
    item_type_code=fields.Integer(string='Item Type Code', track_visibility='onchange' ,help="Unique Item Type Code.")
    complete_name=fields.Char(string='Complete Name',compute='_compute_fields_combination')

    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Flag
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Inactive Item Type Records")


    # Create-By | Created-Date |Info.
    # Pradip    |  7/3/2019    
    # Info : This method is item_type_name + item_type_code shows _rec_name
    
    @api.depends('item_type_name', 'item_type_code')
    def _compute_fields_combination(self):
        for test in self:
            test.complete_name = test.item_type_name + ' \t' + '[' + str(test.item_type_code) + ']'
    
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Item Type Name Uniqueness
    
    @api.depends('item_type_name')
    def item_name_fun(self):
        for i in self:
            desc_str_data=str(i.item_type_name).lower()
            testt=desc_str_data.replace(' ','')
            i.unique_item_name=testt.strip()   #Updated-By:Pradip|Updated-Date:11-Feb-2019|Info.Copy-Paste Test Case (Space Remove)

    # Created By | Created Date |Info.
    # Pradip    |11-3-19 | Item Type Desc.(Uppercase)        
            
    @api.onchange('item_type_name')
    def set_upper(self):    
        if self.item_type_name:
            self.item_type_name = str(self.item_type_name).upper()   
        return  
    
        
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Remove Blank Spaces        
    @api.model
    def create(self,values):
        if 'item_type_name' in values:
            if values['item_type_name'].replace(' ','')=='':
                raise UserError(_("Please Enter Item Type Name."))
        return super(item_type_master,self).create(values)
         
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Remove Blank Spaces      
    @api.multi
    def write(self,values):
        if 'item_type_name' in values:
            if values['item_type_name'].replace(' ','')=='':
                # or values['item_type_name'].strip():
                raise UserError(_("Please Enter Item Type Name."))
             
        return super(item_type_master,self).write(values)
    
