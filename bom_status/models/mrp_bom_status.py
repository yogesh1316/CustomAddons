# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import Warning,UserError
import requests

# create_by | create_date | update_by | update_date
# Chandrakant   12/03/2019   
# Info : create for  generate bom status and process_id


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    _rec_name='process_id'
    _order = "id"
    status = fields.Integer(string="Status")
    process_id= fields.Integer(string="Process Id")
    description=fields.Selection([('INHOUSE','INHOUSE')])
    change_process_id=fields.Many2one('process_id.change')
    select_bom=fields.Boolean(string="Selection")
    checkbox=fields.Selection([('1','1')])






    @api.constrains('product_tmpl_id','bom_line_ids','routing_id')
    def bom_status_assign(self):
        if self.bom_line_ids:
            for i in self.bom_line_ids:
                if self.product_tmpl_id and i.bom_id and self.routing_id:
                    self.status=3
                elif self.product_tmpl_id and i.bom_id:
                    self.status=2 
                elif self.product_tmpl_id:
                    self.status=1
        else:
            if self.product_tmpl_id and self.bom_line_ids.bom_id and self.routing_id:
                self.status=3
            elif self.product_tmpl_id and self.bom_line_ids.bom_id:
                self.status=2 
            elif self.product_tmpl_id:
                self.status=1

        
        
                
    @api.constrains('status')
    def process_id_assign(self):
        if self.status==4:
            product_tmpl_obj=self.search_count([('product_tmpl_id','=',self.product_tmpl_id.id)])
            if product_tmpl_obj>1:
                self.process_id=product_tmpl_obj
            else:
                self.process_id=1
                if self.process_id==1:
                    self.product_tmpl_id.bom_process_id=self.process_id      
                

    @api.onchange('product_tmpl_id')
    def parent_item_type(self):
        obj=self.env['mrp.bom'].search([('product_tmpl_id','=',self.product_tmpl_id.id)])
        if self.product_tmpl_id.item_type.id==1:
            raise Warning('Parent Item Type must be greater than 1')
        li=[]
        if obj:
            for i in obj:
                li.append(i.process_id)
            print(li)
            self.process_id=max(li)+1

        
    
    @api.onchange('bom_line_ids')
    def child_item_type(self):
        for i in self.bom_line_ids:
            if i.product_id.product_tmpl_id.item_type.id > self.product_tmpl_id.item_type.id:
                raise Warning('Child Item Type must equal to or less than Parent Item Type')
            


    @api.multi
    def write(self,vals):
        if self.env['mrp.production'].search([('bom_id', 'in', self.ids), ('state', 'not in', ['done'])]):
            raise UserError(_('You can not edit a Bill of Material with Manufacturing Orders in progress.'))
        return super(MrpBom, self).write(vals)

    # @api.onchange('bom_line_ids')
    # def bom_edit_validation(self):
    #     print(self.id)
    #     a=''
    #     i=0
    #     for l in self.bom_line_ids:
    #         print(l.id)
    #         i=l.id
    #     a=self.env['mrp.bom.line'].search([('id', '=', i)])
    #     print(a.bom_id)
    #     if self.env['mrp.production'].search([('bom_id', 'in', a.bom_id), ('state', 'not in', ['done'])]):
    #         print("''''''''''",self.id)
    #         raise UserError(_('You can not edit a Bill of Material with Manufacturing Orders in progress.'))
   


    @api.onchange('bom_line_ids','product_tmpl_id')
    def child_parent_different(self):
        for i in self.bom_line_ids:
            if self.product_tmpl_id.item_type.id == i.product_id.product_tmpl_id.item_type.id and self.product_tmpl_id.name== i.product_id.product_tmpl_id.name:
                 raise Warning('Child Item and Parent must not be same ')
                
                
           

    # @api.multi
    # def confirm_save(self):
    #     action = self.env.ref('bom_status.act_mrp_product_produce').read()[0]
    #     return action


    
        

class bom_process_id_assign(models.Model):
    _inherit='product.template'


    bom_process_id=fields.Integer()





       


        


   


   


       