from odoo import api,fields,models, _
from odoo.exceptions import UserError,ValidationError

#Text Master   
class text_master_information(models.Model):
    _name='text_master.info'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description='Text Master'
    _rec_name='text_description'
    
    _sql_constraints = [('Unique Text','unique(text_concat)','Please Enter Unique Text Description.')]   
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Active Flag,If Active Flag is Yes then Shows the Product else, Hide
   
    #updated-By|Updated-Date|Info.
    #Pradip    |12-03-19    |all fields added into chatter box
    
    #active_flag=fields.Selection([('Yes','Yes'),('No','No')],default='Yes' ,track_visibility='onchange',help='Activate/Deactivate.')
    text_code=fields.Char(string='Text Code' ,track_visibility='onchange',help='Text Code.')
    text_description = fields.Char('Text Description',required=True,track_visibility='onchange',help='Text Description.')
    text_concat = fields.Char("Text Concat",compute='text_concate_fun',store=True)
    
    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Button
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate Text Master Records")




    #Unique Text
    @api.depends('text_description')
    def text_concate_fun(self):
        for i in self:
            text_data_str=str(i.text_description).lower()
            itext=text_data_str.replace(' ','')
            i.text_concat=itext.strip()    #Updated-By-Pradip |Updated-Date:11-03-2019|Info.Copy Paste test case(space remove)
     
    #Created-By|Created-Date|Info.
    #Pradip    |11-3-19     |Text Desc.(upper case)
            
    @api.onchange('text_description')
    def set_upper(self):    
        if self.text_description:
            self.text_description = str(self.text_description).upper()   
        return  
    
# Updated By | Updated Date |Info. 
# Pradip    |8-2-19 |  text_code(Auto Sequence Code) incremented by one with no_gap    
    @api.model
    def create(self,values):
        if values:
            values["text_code"] = self.env['ir.sequence'].next_by_code('text_master.info')
            if 'text_description' in values:
                if values['text_description'].replace(' ','')=='':
                    raise UserError(_("Please Enter Text Description."))
                
        return super(text_master_information,self).create(values)
         
         
    @api.multi
    def write(self,values):
        if 'text_description' in values:
            if values['text_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Text Description."))
             
        return super(text_master_information,self).write(values)

            
        
            

#Effect Master
class effect_master_info(models.Model):
    _name='effect_master.info'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description='Effect Master'
    _rec_name='effect_description'
    
    #updated-By|Updated-Date|Info.
    #Pradip    |12-03-19    |all fields added into chatter box
    
    _sql_constraints =[('Unique Effect','unique(unique_effect_description)','Please Enter Unique Effect Description.'),
                       ('Effect Code','unique(effect_code_no)','Please Enter Unique Effect Code.')]
    #,
                       #('Effect Code','unique(effect_code_no)','Please Enter Unique Effect Code.')]
    effect_code_no =fields.Char(string='Effect Code.',required=True,track_visibility='onchange',help='Effect Code.') #Updated-By:Pradip|Updated-Date:07-03-2019Info.effect_code_no unique
                            
    effect_description=fields.Char(string='Effect Description',required=True,track_visibility='onchange',help='Effect Description.')
    unique_effect_description=fields.Char('Unique Effect Description',compute='effect_concate_compute' ,store=True)
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Active Flag,If Active Flag is Yes then Shows the Product else, Hide
    # active_flag=fields.Selection([('Yes','Yes'),('No','No')],default='Yes',track_visibility='onchange',help='Activate/Deactivate')

    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Flag
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate Effect Master Records")





    # Created By | Created Date | Info.
    # Pradip    |16-1-19 |Effect Description Convert into Uppercase
    
   #Unique Effect
    @api.depends('effect_description')
    def effect_concate_compute(self):
        for i in self:
            text_effe_data=str(i.effect_description).lower()
            tex=text_effe_data.replace(' ','')
            i.unique_effect_description=tex.strip()  #Updated-By-Pradip |Updated-Date:11-03-2019|Info.Copy Paste test case(space remove)

    
    #Created-By|Created-Date|Info.
    #Pradip    |11-3-19     |Effect Desc.(upper case)
    @api.onchange('effect_description')
    def set_upper(self):    
        if self.effect_description:
            self.effect_description = str(self.effect_description).upper()   
        return  
    
    @api.model    
    def create(self,values):
            if 'effect_description' in values:
                if values['effect_description'].replace(' ','')=='':
                    raise UserError(_("Please Enter Effect Description."))
            if 'effect_code_no' in values:
                if values['effect_code_no'].replace(' ','')=='':
                    raise UserError(_("Please Enter Effect Code."))
                    
            return super(effect_master_info,self).create(values)
  
    @api.multi    
    def write(self,values):
            if 'effect_description' in values:
                if values['effect_description'].replace(' ','')=='':
                    raise UserError(_("Please Enter Effect Description."))
            if 'effect_code_no' in values:
                if values['effect_code_no'].replace(' ','')=='':
                    raise UserError(_("Please Enter Effect Code."))
                    
            return super(effect_master_info,self).write(values)
  
        

 #ID Code Master
class id_code_master_info(models.Model):
    _name='id_code_master.info'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description='Id Code Master'
    _rec_name='id_code_description'
    
     #updated-By|Updated-Date|Info.
     #Pradip    |12-03-19    |all fields added into chatter box
    
    #sr_no=fields.Char(string='SrNo',readonly=True)
    _sql_constraints =[('id code num','unique(id_code_no)','Please Enter Unique Id Code'),
                       ('Unique Id Desc','unique(unique_id_code_description)','Please Enter Unique Id Description')]
    
    id_code_no =fields.Char(string='ID_NO.',required=True,track_visibility='onchange',help='ID_NO')
    
    id_code_description=fields.Char("Id Description",required=True,track_visibility='onchange',help='Id Description')
    unique_id_code_description=fields.Char("Unique Id Description",compute='id_decription_concat_fun' ,store=True)
    # Created By | Created Date |Info.
    # Pradip    |28-1-19 | Active Flag,If Active Flag is Yes then Shows the Product else, Hide
    # active_flag=fields.Selection([('Yes','Yes'),('No','No')],default='Yes',track_visibility='onchange',help='Activate/Deactivate')
    
    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Flag
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate Id Code Master Records")

    
    #Unique ID Code
    @api.depends('id_code_description')
    def id_decription_concat_fun(self):
        for i in self:
            id_code_data=str(i.id_code_description).lower()
            text=id_code_data.replace(' ','')
            i.unique_id_code_description=text.strip()  #Updated-By-Pradip |Updated-Date:11-03-2019|Info.Copy Paste test case(space remove)

   #Created-By|Created-Date|Info.
   #Pradip    |11-3-19     |Id Code Desc.(upper case)         
            
    @api.onchange('id_code_description')
    def set_upper(self):    
        if self.id_code_description:
            self.id_code_description = str(self.id_code_description).upper()   
        return    
    
    # Updated By | Updated Date | Info.
    # Pradip    |21-1-19 | Info. id_code_no columns remove blank space.(In Create and Write Method)    
    @api.model
    def create(self,values):
        if 'id_code_description' in values:
            if values['id_code_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Id Description."))
        if 'id_code_no' in values:
            if values['id_code_no'].replace(' ','')=='':
                raise UserError(_("Please Enter Id Code."))
        return super(id_code_master_info,self).create(values)

    @api.multi
    def write(self,values):
        if 'id_code_description' in values:
            if values['id_code_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Id Description."))
        if 'id_code_no' in values:
            if values['id_code_no'].replace(' ','')=='':
                raise UserError(_("Please Enter Id Code."))
        return super(id_code_master_info,self).write(values)
     
#Make Master
class make_master_info(models.Model):
    _name='make_master.info'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description='Make Master'
    _rec_name='make_description'
    
    _sql_constraints=[('Unique Make No.','unique(unique_make_description)','Please Enter Unique Make Description.')]
   
    #updated-By|Updated-Date|Info.
    #Pradip    |12-03-19    |all fields added into chatter box
   
    make_no=fields.Char('Make No.',readonly=True,track_visibility='onchange',help='Make No.')
    make_description=fields.Char('Make Description',required=True,track_visibility='onchange',help='Make Description')
    unique_make_description=fields.Char('Unique Make Description',compute='make_master_concat_fun',store=True)
# Created By | Created Date |Info.
# Pradip    |28-1-19 | Active Flag,If Active Flag is Yes then Shows the Product else, Hide
    # active_flag=fields.Selection([('yes','Yes'),('no','No')],default='yes',track_visibility='onchange',help='Activate/Deactivate')
    
    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Flag
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate Make Master Records")





    #Unique Make 
    @api.depends('make_description')
    def make_master_concat_fun(self):
        for i in self:
            make_data=str(i.make_description).lower()
            text=make_data.replace(' ','')
            i.unique_make_description=text.strip()  #Updated-By-Pradip |Updated-Date:11-03-2019|Info.Copy Paste test case(space remove)
            
   #Created-By|Created-Date|Info.
   #Pradip    |11-3-19     |Make Desc.(upper case)  
            
    @api.onchange('make_description')
    def set_upper(self):    
        if self.make_description:
            self.make_description = str(self.make_description).upper()   
        return    
    
    
    # Updated By | Updated Date |Info. 
    # Pradip    |8-2-19 |  make_no(Auto Sequence Code) incremented by one with no_gap 
    
    @api.model
    def create(self,values):
        if values:
            values['make_no']=self.env['ir.sequence'].next_by_code('make_master.info')
            if 'make_description' in values:
                if values['make_description'].replace(' ','')=='':
                    raise UserError(_("Please Enter Make Description."))
        return super(make_master_info,self).create(values)
            
    @api.multi
    def write(self,values):
        if 'make_description' in values:
            if values['make_description'].replace(' ','')=='':
                raise UserError(_("Please Enter Make Description."))
        return super(make_master_info,self).write(values)
        
#MRP Type Master        
class mrp_type_master_info(models.Model):
    _name='mrp_type_master.info'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description='MRP Type Master'
    _rec_name='mrp_description'
    
    #updated-By|Updated-Date|Info.
    #Pradip    |12-03-19    |all fields added into chatter box
    
    _sql_constraints=[('Unique MRP Type Code.','unique(unique_mrp_description)','Please Enter Unique MRP Type Description.'),
                      ('MRP Type Code Unique.','unique(mrp_type_code)','Please Enter Unique MRP Type Code.')]
    
    mrp_type_code=fields.Char('MRP Type Code',required=True,track_visibility='onchange',help='MRP Type Code')
    mrp_description=fields.Char('MRP Type Description',required=True,track_visibility='onchange',help='MRP Type Description')
    unique_mrp_description=fields.Char('Unique MRP Type Description',compute='mrp_type_description_fun',store=True)
    # active_flag=fields.Selection([('Yes','Yes'),('No','No')],default='Yes',track_visibility='onchange',help='Activate/Deactivate')
   
    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Flag
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate MRP Type Records")


    # Unique MRP Type
    @api.depends('mrp_description')
    def mrp_type_description_fun(self):
        for i in self:
            mrp_desc_str_data=str(i.mrp_description).lower()
            text=mrp_desc_str_data.replace(' ','')
            i.unique_mrp_description=text.strip()   #Updated-By-Pradip |Updated-Date:11-03-2019|Info.Copy Paste test case(space remove)
            
    
   #Created-By|Created-Date|Info.
   #Pradip    |11-3-19     |Mrp type Desc.(upper case) 
            
    @api.onchange('mrp_description')
    def set_upper(self):    
        if self.mrp_description:
            self.mrp_description = str(self.mrp_description).upper()   
        return    
    
    
    
    # Updated By | Updated Date | Info.
    # Pradip    |18-1-19 | Info. mrp_type_code columns remove blank space.(In Create and Write Method) 
    @api.model
    def create(self,values):
        if 'mrp_description' in values:
            if values['mrp_description'].replace(' ','')=='':
                raise UserError(_("Please Enter MRP Type Description."))
        if 'mrp_type_code' in values:
            if values['mrp_type_code'].replace(' ','')=='':
                raise UserError(_("Please Enter MRP Type Code."))
        return super(mrp_type_master_info,self).create(values)
    
    @api.multi   
    def write(self,values):
        if 'mrp_description' in values:
            if values['mrp_description'].replace(' ','')=='':
                raise UserError(_("Please Enter MRP Type Description."))
        if 'mrp_type_code' in values:
            if values['mrp_type_code'].replace(' ','')=='':
                raise UserError(_("Please Enter MRP Type Code."))
        return super(mrp_type_master_info,self).write(values)
    
   
#Source Master
class source_master_info(models.Model):
    _name='source_master.info'   
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description='Source Master'
    _rec_name='source_description'         
  
    #updated-By|Updated-Date|Info.
    #Pradip    |12-03-19    |all fields added into chatter box
  
    _sql_constraints=[('Unique Source Description','unique(unique_source_description)','Please Enter Unique Source Description.'),
                      ('Unique Source Code','unique(source_code)','Please Enter Unique Source Code.')]
   
    source_code=fields.Char('Source Code',required=True,track_visibility='onchange',help='Source Code')
    source_description=fields.Char('Source Description',required=True,track_visibility='onchange',help='Source Description')
    unique_source_description=fields.Char('Unique Source Description',compute='source_description_fun',store=True)
    # active_flag=fields.Selection([('Yes','Yes'),('No','No')],default='Yes',track_visibility='onchange',help='Activate/Deactivate')
   
    #Created By| Created Date|Info.
    #Pradip    | 21-3-2019  |Active /Deactivate Flag
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Inactive Source Master Records")


    # Unique Source 
    @api.depends('source_description')
    def source_description_fun(self):
        for i in self:
            sourc_desc_str_data=str(i.source_description).lower()
            text=sourc_desc_str_data.replace(' ','')
            i.unique_source_description=text.strip()       #Updated-By-Pradip |Updated-Date:11-03-2019|Info.Copy Paste test case(space remove)
     
     
   #Created-By|Created-Date|Info.
   #Pradip    |11-3-19     |Source Desc.(upper case) 
          
    @api.onchange('source_description')
    def set_upper(self):    
        if self.source_description:
            self.source_description = str(self.source_description).upper()   
        return        
            
    
    # Updated By | Updated Date | Info.
    # Pradip    |18-1-19 | Info. source_code columns remove blank space.(In Create and Write Method)     
    @api.model
    def create(self,values):
            if 'source_description' in  values:
                if values['source_description'].replace(' ','')=='':
                    raise UserError(_("Please Enter Source Description."))
            if 'source_code' in values:
                if values['source_code'].replace(' ','')=='':
                    raise UserError(_("Please Enter Source Code."))
            return super(source_master_info,self).create(values)
                
    @api.multi
    def write(self,values):
            if 'source_description' in values:
                if values['source_description'].replace(' ','')=='':
                    raise UserError("Please Enter Source Description.")
            if 'source_code' in values:
                if values['source_code'].replace(' ','')=='':
                    raise UserError("Please Enter Source Code.")
                    
            return super(source_master_info,self).write(values)
        

#HSN Master            
class hsn_master_info(models.Model):
    _name='hsn_master.info'
    
    _rec_name='hsn_no'
    hsn_no=fields.Char("HSN No.",required=True)
    _sql_constraints=[('Unique HSN No.','unique(hsn_no)','Please Enter Unique HSN No.')] #Unique HSN Number

    rate=fields.Char("Rate")
    in_state_sale=fields.Many2one('account.tax',string='In state sale')
    out_state_sale=fields.Many2one('account.tax',string='Out state sale')
    in_state_purchase=fields.Many2one('account.tax',string='In state purchase')
    out_state_purchase=fields.Many2one('account.tax',string='Out state purchase')
    
    #HSN Number only Numeric
    @api.constrains('hsn_no')
    def chk_hsn_number(self):
        if self.hsn_no.isdigit():
            pass
        else:
            raise ValidationError(_('Please Enter Only Number.'))
                
        
        
    @api.model
    def create(self,values):
        if values['hsn_no']:
            if values['hsn_no'].replace(' ','')=='':
                raise UserError(_("Please Enter HSN Number."))
        if values['rate']:
                if values['rate'] < str(0):
                    raise UserError(_("Do not Enter Negative Rate "))                
        return super(hsn_master_info,self).create(values)
    
    @api.multi
    def write(self,values):
        if "hsn_no" in values:
            if values['hsn_no']:
                if values['hsn_no'].replace(' ','')=='':
                    raise UserError(_("Please Enter HSN Number."))
                else:
                    return super(hsn_master_info,self).write(values)
    
    @api.onchange('rate')
    def hsn_master_rate(self):
        temp=""
        obj_acc_tax=self.env['account.tax']
        if self.rate:
            
            temp="GST "+self.rate+"%"
            search1=obj_acc_tax.search([('amount_type','=','group'),('type_tax_use','=','sale'),('name','=',temp)])
            self.in_state_sale=search1     
                   
            temp="IGST "+self.rate+"%"
            search2=obj_acc_tax.search([('amount_type','=','percent'),('type_tax_use','=','sale'),('name','=',temp)])
            self.out_state_sale=search2
            
            temp="GST "+self.rate+"%"
            search3=obj_acc_tax.search([('amount_type','=','group'),('type_tax_use','=','purchase'),('name','=',temp)])
            self.in_state_purchase=search3
            
            temp="IGST "+self.rate+"%"
            search4=obj_acc_tax.search([('amount_type','=','percent'),('type_tax_use','=','purchase'),('name','=',temp)])
            self.out_state_purchase=search4
    

     
    
    
    
    
    
    
    
    