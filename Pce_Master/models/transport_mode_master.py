from odoo import api, fields, models, _
from odoo.exceptions import UserError

   
# Created By | Created Date |Info.
# Pradip    |4-2-19 | Transport Mode Master

class transport_mode_master(models.Model):
    _name='transport_mode.master'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name ="transport_mode_desc"  
    _description="Transport Mode Master"
    
    _sql_constraints = [('Unique Delivery Term','unique(unique_transport_mode_desc)','Please Enter Unique Transport Mode.')]
   
    #Updated-By|Updated-Date|Info.
    #Pradip    |12-3-2019   | All fileds added in Chatter Box   
    
    transport_mode_code=fields.Char(string='Transport Mode Code',readonly=True,store=True,track_visibility='onchange',help='Transport Mode Code.')
    active_flag=fields.Selection([('yes','Yes'),('no','No')],default='yes',track_visibility='onchange',help='Activate/Deactivate')
    transport_mode_desc=fields.Char(string='Transport Mode Description',required=True,track_visibility='onchange',help='Transport Mode Description')
    unique_transport_mode_desc=fields.Char(string='Unique Transport Mode Desc.',compute='transport_mode_desc_fun',store=True)
   


    # Created By | Created Date |Info.
    # Pradip    |4-2-19 | Transport Mode Unique Description   
     
    @api.depends('transport_mode_desc')
    def transport_mode_desc_fun(self):
        for i in self:
            text_str=str(i.transport_mode_desc).lower()
            text=text_str.replace(' ','')
            i.unique_transport_mode_desc=text.strip() #Updated-By:Pradip |Updated-Date:11-3-2019|Info.Copy-Paste test case (Space remove)
            
    #Created-By|Created-Date|Info.
    #Pradip    |11-3-2019   |Transport Mode Desc.(Upper Case)        
            
    @api.onchange('transport_mode_desc')
    def set_upper(self):    
        if self.transport_mode_desc:
            self.transport_mode_desc = str(self.transport_mode_desc).upper()   
        return
    
    
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
            if val['transport_mode_desc'].replace(' ','')=='' :
                raise UserError('Please Do not Save Empty Record.')
        return super(transport_mode_master,self).write(val)
        
    
                
        
            
            
            
    

     