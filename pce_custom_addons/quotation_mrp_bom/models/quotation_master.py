
from odoo import api, fields, models
 
# ---------------------Make Master---------------------------------
class make_master_info(models.Model):
    _name="make_master.info"
    _rec_name='make_description'
    _sql_constraints=[('Unique Make No.','unique(unique_make_description)','Please Enter Unique Make Description.')]
    make_no=fields.Char('Make No.',readonly=True)
    make_description=fields.Char('Make Description',required=True)
    unique_make_description=fields.Char('Unique Make Description',compute='make_master_concat_fun',store=True)
    # master_line=fields.One2many("qutation_mrp_bom_line.info",'type_master_id')

      
#-----------------------MRP Type Master-----------------------------------        
class mrp_type_master_info(models.Model):
    _name='mrp_type_master.info'
    _rec_name='mrp_description'
    _sql_constraints=[('Unique MRP Type Code.','unique(unique_mrp_description)','Please Enter Unique MRP Type Description.')]
    mrp_type_code=fields.Char('MRP Type Code',required=True)
    mrp_description=fields.Char('MRP Type Description',required=True)
    unique_mrp_description=fields.Char('Unique MRP Type Description',compute='mrp_type_description_fun',store=True)