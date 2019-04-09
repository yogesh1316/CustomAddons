from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
   
# Created By | Created Date |Info.
# Pradip     |4-2-19        | Delivery Term Master

class delivery_term_master(models.Model):
    _name='delivery_term.master'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    _rec_name ="delivery_term"  
    _description="Delivery Term"
    
    _sql_constraints = [('Unique Delivery Term','unique(unique_delivery_term)','Please Enter Unique Delivery Term.')]
    
    #Updated-By:Pradip|Updated-Date:12-3-19|Info.all fields added in chatter Box 

    deliv_term_code=fields.Char(string='Delivery Term Code',store=True ,track_visibility='onchange',help='Delivery Term Code') 
    # active_flag=fields.Selection([('yes','Yes'),('no','No')],default='yes',track_visibility='onchange',help='Activate/Deactivate')
    delivery_term=fields.Char(string='Delivery Term',required=True,track_visibility='onchange',help='Delivery Term Description.')
    unique_delivery_term=fields.Char(string='Unique Delivery Term',compute='unique_delivery_term_fun',store=True)
    
    # sample_active=fields.Boolean(string="Sample Test Active")

    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Flag
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate Delivery Term Records")







# Created By | Created Date |Info.
# Pradip    |4-2-19 | Delivery Term Convert into Uppercase    
    

# Created By | Created Date |Info.
# Pradip    |4-2-19 | Delivery Term Unique        

    @api.depends('delivery_term')
    def unique_delivery_term_fun(self):
        for i in self:
            text_data_str=str(i.delivery_term).lower()
            ery_term=text_data_str.replace(' ','')
            i.unique_delivery_term=ery_term.strip() #Updated-By:Pradip|Updated-Date:11-Feb-2019|Info.Copy-Paste Test Case (Space Remove)
            

# Created By | Created Date |Info. 
# Pradip     |11-Feb-2019   |Delivery Term Description(Uppercase)            
    @api.onchange('delivery_term')
    def set_upper(self):    
        if self.delivery_term:
            self.delivery_term = str(self.delivery_term).upper()   
        return  

# Created By | Created Date |Info. 
# Pradip    |4-2-19 | Create Method Override     

# Updated By | Updated Date |Info. 
# Pradip    |8-2-19 |  deliv_term_code(Auto Sequence Code) incremented by one with no_gap

    @api.model
    def create(self,values):
        if values:
            values["deliv_term_code"] = self.env['ir.sequence'].next_by_code('delivery_term.master')
            if 'delivery_term' in values:
                if values['delivery_term'].replace(' ','')=='':
                    raise UserError(_("Please Enter Delivery Term."))
        return super(delivery_term_master,self).create(values)
          
# Created By | Created Date |Info.
# Pradip    |4-2-19 | write Method Override            
    @api.multi
    def write(self,values):
        if 'delivery_term' in values:
            if values['delivery_term'].replace(' ','')=='':
                raise UserError(_("Please Enter Delivery Term."))
        return super(delivery_term_master,self).write(values)
    
    