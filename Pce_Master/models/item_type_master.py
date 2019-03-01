from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


# create_by | create_date | update_by | update_date
# Ganesh      26/10/2018    
# Info : This master is item type for using in Product creation 

class item_type_master(models.Model):
    _name='item.type.master'   
    _rec_name='item_type_name'    
         
    _sql_constraints=[('Unique Item Name','unique(unique_item_name)','Please Enter Unique Item Type Name.')]
    item_type_name=fields.Char('Item Type Name',required=True,help="Item type name")    
    unique_item_name=fields.Char('Unique Item type name' ,compute='item_name_fun',store=True)
    activeflag=fields.Selection([('Y','Yes'),('N','No')],default='Y')
    
    # Created By | Created Date |Info.
    # Pradip    |17-1-19 | Item Type Name Convert into Uppercase
    @api.onchange('item_type_name')
    def item_type_name_uppercase(self):
        for i in self:
            if i.item_type_name:
                str_item_name=(i.item_type_name).upper()
                i.item_type_name=str_item_name
    
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Item Type Name Uniqueness
    @api.depends('item_type_name')
    def item_name_fun(self):
        for i in self:
            desc_str_data=str(i.item_type_name).lower()
            i.unique_item_name=desc_str_data.replace(' ','')
    
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Remove Blank Spaces        
    @api.model
    def create(self,values):
        if 'item_type_name' in values:
                pass
                if values['item_type_name'].replace(' ','')=='':
                    raise UserError(_("Please Enter Item Type Name."))
        return super(item_type_master,self).create(values)
         
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Remove Blank Spaces      
    @api.multi
    def write(self,values):
        if 'item_type_name' in values:
            if values['item_type_name'].replace(' ','')=='':
                raise UserError(_("Please Enter Item Type Name."))
             
        return super(item_type_master,self).write(values)
    
