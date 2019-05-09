from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


# create_by | create_date | update_by | update_date
# Ganesh      11/10/2018    Pradip      28/1/2019            
# Info : This master model is use to identify why item get rejected for that reason is reqired 

class reason_master(models.Model):
    _name='reason.master'   
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description='Reason Master'
    _rec_name='reason_desc'    
         
    _sql_constraints=[('Unique Reason Description','unique(unique_reason_desc)','Please Enter Unique Reason Description.')]
   
    #Updated-By|Updated-Date|Info.
    #Pradip    |12-03-2019  |all fields Added into Chatter Box
    
    reason_desc=fields.Char('Reason Description',required=True,track_visibility='onchange',help="Please Enter Unique Description")
    unique_reason_desc=fields.Char('Unique Reason Description' ,compute='reason_description_fun',store=True)
    reason_code=fields.Char(string='Reason Code',track_visibility='onchange',help='Reason Code')
    # active_flag=fields.Selection([('yes','Yes'),('no','No')],default='yes',track_visibility='onchange',help='Activate/Deactivate')
    
    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Flag
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate Reason Master Records")


    
    # Update : Unique Reason Description
    @api.depends('reason_desc')
    def reason_description_fun(self):
        for i in self:
            desc_str_data=str(i.reason_desc).lower()
            text=desc_str_data.replace(' ','')
            i.unique_reason_desc=text.strip()  #Updated-By:Pradip|Updated-Date11-03-2019|Info.Copy-Paste test case(Space remove)
            
   #Created-By|Created-Date|Info.
   #Pradip    |11-03-2019  |Reason Desc. (Upper Case)
            
    @api.onchange('reason_desc')
    def set_upper(self):    
        if self.reason_desc:
            self.reason_desc = str(self.reason_desc).upper()   
        return
    
# create_by | create_date |Info.
# Pradip |28-1-19|| Unique and Require when Create Method Call and Auto Sequence Created   

# Updated By | Updated Date |Info. 
# Pradip    |8-2-19 |  reason_code(Auto Sequence Code) incremented by one with no_gap           
    @api.model
    def create(self,values):
        if values:
            values["reason_code"] = self.env['ir.sequence'].next_by_code('reason.master')
            if 'reason_desc' in values:
                if values['reason_desc'].replace(' ','')=='':
                    raise UserError(_("Please Enter Reason Description."))
        return super(reason_master,self).create(values)
    
# create_by | create_date |Info.
# Pradip |28-1-19|| Unique and Require when Write Method Call 
    @api.multi
    def write(self,values):
        if 'reason_desc' in values:
            if values['reason_desc'].replace(' ','')=='':
                raise UserError("Please Enter Reason Description.")
        return super(reason_master,self).write(values)
            
            
    
    
    
