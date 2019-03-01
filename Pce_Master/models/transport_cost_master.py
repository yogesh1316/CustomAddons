from odoo import api, fields, models, _
from odoo.exceptions import UserError
   
# Created By | Created Date |Info.
# Pradip    |4-2-19 | Transport Cost Master

class transport_cost_master(models.Model):
    _name='transport_cost.master'
    _rec_name ="transport_cost_desc"  
    _description="Transport Cost Master"
    
    _sql_constraints = [('Unique Transport Cost Desc.','unique(unique_transport_cost_desc)','Please Enter Unique Transport Cost Description.')]
    transport_cost_desc=fields.Char(string='Transport Cost Desc.',required=True)
    unique_transport_cost_desc=fields.Char(string='Unique Transport Cost Desc.',compute='unique_transport_cost_desc_fun',store=True)
    transport_cost_code=fields.Char('Transport Cost Code',readonly=True)
    active_flag=fields.Selection([('yes','Yes'),('no','No')],string='Is Active',default='yes')

   
# Created By | Created Date |Info.
# Pradip    |4-2-19 | Transport Code Description Convert into Uppercase  

    @api.onchange('transport_cost_desc')
    def transport_cost_desc_uppercase(self):
        for i in self:
            if i.transport_cost_desc:
                text_tr_cst=(i.transport_cost_desc).upper()
                i.transport_cost_desc=text_tr_cst

# Created By | Created Date |Info.
# Pradip    |4-2-19 | Transport Cost Unique Description   
    
    @api.depends('transport_cost_desc')
    def unique_transport_cost_desc_fun(self):
        for i in self:
            if i.transport_cost_desc:
                text_str=str(i.transport_cost_desc).lower()
                i.unique_transport_cost_desc=text_str.replace(' ','')

# Created By | Created Date |Info.
# Pradip    |4-2-19 | Create Method Override     

# Updated By | Updated Date |Info. 
# Pradip    |8-2-19 |  transport_cost_code(Auto Sequence Code) incremented by one with no_gap     
           
    @api.model
    def create(self,val):
        if val:
            val['transport_cost_code'] = self.env['ir.sequence'].next_by_code('transport_cost.master') 
            if 'transport_cost_desc' in val:
                if val['transport_cost_desc'].replace(' ','')=='':
                    raise UserError('Please Enter Transport Cost Description.')
        return super(transport_cost_master,self).create(val)

# Created By | Created Date |Info.
# Pradip    |4-2-19 | write Method Override     
  
    @api.multi
    def write(self,val):
        if 'transport_cost_desc' in val:
            if val['transport_cost_desc'].replace(' ','')=='':
                raise UserError('Please Do Not Save Empty Record.')
        return super(transport_cost_master,self).write(val)
                
    

                
                
                
                
                
             
  
    
    
    
    