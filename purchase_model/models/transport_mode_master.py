from odoo import api, fields, models, _
from odoo.exceptions import UserError

   
# Created By | Created Date |Info.
# Pradip    |4-2-19 | Transport Mode Master

class transport_mode_master(models.Model):
    _name='transport_mode.master'
    _rec_name ="transport_mode_desc"  
    _description="Transport Mode Master"
    
    _sql_constraints = [('Unique Delivery Term','unique(unique_transport_mode_desc)','Please Enter Unique Transport Mode.')]
    transport_mode_code=fields.Char(string='Transport Mode Code',readonly=True,store=True)
    active_flag=fields.Selection([('yes','Yes'),('no','No')],default='yes')
    transport_mode_desc=fields.Char(string='Transport Mode Description',required=True)
    unique_transport_mode_desc=fields.Char(string='Unique Transport Mode Desc.',compute='transport_mode_desc_fun',store=True)
   
# Created By | Created Date |Info.
# Pradip    |4-2-19 | Transport Mode Description Convert into Uppercase  
 
    @api.onchange('transport_mode_desc')
    def transport_mode_desc_uppercase(self):
        for i in self:
            if i.transport_mode_desc:
                trs_desc=(i.transport_mode_desc).upper()
                i.transport_mode_desc=trs_desc

# Created By | Created Date |Info.
# Pradip    |4-2-19 | Transport Mode Unique Description   
     
    @api.depends('transport_mode_desc')
    def transport_mode_desc_fun(self):
        for i in self:
            text_str=str(i.transport_mode_desc).lower()
            i.unique_transport_mode_desc=text_str.replace(' ','')

# Created By | Created Date |Info.
# Pradip    |4-2-19 | Create Method Override     

# Updated By | Updated Date |Info. 
# Pradip    |8-2-19 |  transport_mode_code(Auto Sequence Code) incremented by one with no_gap               
    @api.model
    def create(self,val):
        if val:
            val['transport_mode_code'] = self.env['ir.sequence'].next_by_code('transport_mode.master') 
            if 'transport_mode_desc' in val:
                if val['transport_mode_desc'].replace(' ','')=='':
                    raise UserError('Please Enter Transport Mode Description.')
        return super(transport_mode_master,self).create(val)

# Created By | Created Date |Info.
# Pradip    |4-2-19 | write Method Override     
  
    @api.multi
    def write(self,val):
        if 'transport_mode_desc' in val:
            if val['transport_mode_desc'].replace(' ','')=='':
                raise UserError('Please Do not Save Empty Record.')
        return super(transport_mode_master,self).write(val)
        
    
                
        
            
            
            
    

     