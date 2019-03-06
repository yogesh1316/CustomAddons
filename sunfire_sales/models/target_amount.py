from odoo import api,fields,models
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

'''https://stackoverflow.com/questions/882712/sending-html-email-using-python
  <field name="domain">[('from_date','&gt;=',datetime.datetime.now())]</field>
  <field name="domain">[('from_date','&lt;=',datetime.datetime.now())]</field>
  <field name="domain">[('from_date','&gt;= ANd &lt;=',datetime.datetime.now())]</field>
'''
# create_by      | create_date | update_by | update_date
# Pradip Yenpure 5,Nov,2018     Pradip Yenpure  12,Nov,2018           
# Info : In this master model,Target amount calculate by Month wise  

class target_master(models.Model):
    _name='target.master'
    #_inherit='mail.thread'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name='year'
    
    users_name=fields.Many2one('res.users',string='Sales Person',required=True,help="User Name.",track_visibility='onchange')
    type=fields.Selection([('topline','Top Line'),('bottomline','Bottom Line')],'Type',required=True,help="Target Type.",track_visibility='onchange')
    year=fields.Selection([(num, str(num)) for num in range(datetime.now().year, (datetime.now().year)+8 )],'Year',required=True,help="Target Year.",track_visibility='onchange')
#     year=fields.Selection([(num, str(num)) for num in range(datetime.now() )],'Mnth',required=True,help="Target Mnth.",track_visibility='onchange')
    
    _sql_constraints=[('unique target','unique(users_name,type,year)','Data for such Combination Exists.')]

   # mont_name=fields.Selection([(num,str(num)) for num in range((datetime.now().month) )],"months") 
       
    quarter1=fields.Float(string="Quarter 1",help="Target For Quarter 1",track_visibility='onchange')
    quarter2=fields.Float(string="Quarter 2",help="Target For Quarter 2",track_visibility='onchange')
    quarter3=fields.Float(string="Quarter 3",help="Target For Quarter 3",track_visibility='onchange')
    quarter4=fields.Float(string="Quarter 4",help="Target For Quarter 4",track_visibility='onchange')
    
    
    monthly_target_quarter1=fields.Float(string="Monthly Target Quarter1",compute='quarter1_cal_',store=True,help="Calculated from Quarter1",track_visibility='onchange')
    monthly_target_quarter2=fields.Float(string="Monthly Target Quarter2",compute='quarter2_cal_',store=True,help="Calculated from Quarter2",track_visibility='onchange')
    monthly_target_quarter3=fields.Float(string="Monthly Target Quarter3",compute='quarter3_cal_',store=True,help="Calculated from Quarter3",track_visibility='onchange')
    monthly_target_quarter4=fields.Float(string="Monthly Target Quarter4",compute='quarter4_cal_',store=True,help="Calculated from Quarter4",track_visibility='onchange')
    
    #Cal Quarter1 month wise
    @api.depends('quarter1')
    def quarter1_cal_(self):
        print("==========================================")
        for q1 in self:
            if q1.quarter1:
                q1.monthly_target_quarter1=round(((q1.quarter1)/3.0),2) # .2 values after point
                print("Q1================",round(q1.monthly_target_quarter1,2))
    
    #Cal Quarter2 month wise
    @api.depends('quarter2')
    def quarter2_cal_(self):
        for q2 in self:
            if q2.quarter2:
                q2.monthly_target_quarter2=((q2.quarter2)/3.0)
    
    #Cal Quarter3 month wise
    @api.depends('quarter3')
    def quarter3_cal_(self):
        for q3 in self:
            if q3.quarter3:
                q3.monthly_target_quarter3=((q3.quarter3)/3.0)
     
    #Cal Quarter4 month wise       
    @api.depends('quarter4') 
    def quarter4_cal_(self): 
        for q4 in self:  
            if q4.quarter4:
                q4.monthly_target_quarter4=((q4.quarter4)/3.0)
                
    #validations for negative values {No negative number Accepted}            
    @api.onchange('quarter1','quarter2','quarter3','quarter4')
    def quarters_validations(self):
            if self.quarter1 < 0:
                raise UserError("Negative values not Allowed.")
            
            elif self.quarter2<0:
                raise UserError("Negative values not Allowed.")
            
            elif self.quarter3<0:
                raise UserError("Negative values not Allowed.")
            
            elif self.quarter4<0:
                raise UserError("Negative values not Allowed.")
            
                
   
