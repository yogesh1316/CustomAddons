from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

   
# Created By | Created Date |Info.
# Pradip    |4-2-19 | Delivery Term Master

class delivery_term_master(models.Model):
    _name='delivery_term.master'
    _rec_name ="delivery_term"  
    _description="Delivery Term"
    
    _sql_constraints = [('Unique Delivery Term','unique(unique_delivery_term)','Please Enter Unique Delivery Term.')]
    deliv_term_code=fields.Char(string='Delivery Term Code',store=True) 
    active_flag=fields.Selection([('yes','Yes'),('no','No')],default='yes')
    delivery_term=fields.Char(string='Delivery Term',required=True)
    unique_delivery_term=fields.Char(string='Unique Delivery Term',compute='unique_delivery_term_fun',store=True)
    

# Created By | Created Date |Info.
# Pradip    |4-2-19 | Delivery Term Convert into Uppercase    
    
    @api.onchange('delivery_term')
    def delivery_term_upper_case(self):
        for i in self:
            if i.delivery_term:
                text_data_str=(i.delivery_term).upper() 
                i.delivery_term=text_data_str
# Created By | Created Date |Info.
# Pradip    |4-2-19 | Delivery Term Unique        

    @api.depends('delivery_term')
    def unique_delivery_term_fun(self):
        for i in self:
            text_data_str=str(i.delivery_term).lower()
            i.unique_delivery_term=text_data_str.replace(' ','')

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
    
    