# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import UserError,ValidationError


class specification_mast(models.Model):
    _name = 'spec.master'
    _rec_name='specification_text'
    level=fields.Integer(string="Level")
    specification_text=fields.Text(string="Specification_Text")
    description=fields.Text(string="Description")
    # attrib_lines=fields.One2many('spec.rel','parent_id')
   



class spec_relation(models.Model):
    _name='spec.rel'
    

    level=fields.Integer(string="level")
    temp=fields.Integer(string="temp")
    parent_id=fields.Many2one('spec.master', string="parent")
    level1=fields.Many2one('spec.master',domain=[('level', '=',1)],string="level 1 ")
    level2=fields.Many2one('spec.master',domain=[('level', '=',2)],string="level 2 ")
    level3=fields.Many2one('spec.master',domain=[('level', '=',3)],string="level 3 ")   
   
   
    @api.onchange('level1')
    def spec_master_validation(self):
        if self.level1:
            spec_level1=self.search([])
            for i in spec_level1:
                if self.level1.id==i.level1.id:
                    raise UserError('spec item is already exist.')   

    @api.onchange('level')
    def spec_master_set(self):
        con=[]
        res={}
        res = {'value':{'level_id':False}}
        spec_master_obj = self.env['spec.master']
        if self.level>0:                
            if self.level==1:
                ids=spec_master_obj.search([('level','=',2)])
            elif self.level==2:
                ids=spec_master_obj.search([('level','=',3)])
            for i in ids:
                con.append(i.id) 
            res = {'value':{'level_id':con}}
            self.level_id=con
        

   

    @api.multi
    def _compute_subcontractvendor(self):        
        con=[]
        spec_master_obj = self.env['spec.master']
        ids=spec_master_obj.search([('level','=',2)])
        for i in ids:
            con.append(i.id)       
        return [('id','in',con)]
   

    level_id=fields.Many2one('spec.master')
    spec_rel_id=fields.Many2one('spec.rel')
    order_line = fields.One2many('spec.rel','spec_rel_id')         


                
# @api.onchange('po_to_be_placed')
#     def company_addr(self):
#         #print("Eureka#1",self)
#         con=[]
#         domain={}
#         res_company_obj = self.env['res.partner']
#         con_ids=res_company_obj.search([('parent_id','=',self.po_to_be_placed.id)])
#         for i in con_ids:
#             con.append(i.id)
#         domain['po_detail_address']=[('id','in',con)]
#         #print(domain)
#         return {'domain':domain}


    # @api.model
    # def create(self):
    #     # a=vals.get('order_line')
    
    #     head_val={}
    #     det_val={}
    #     spec_rel_obj=self.env['spec.rel']
    #     head_val={'level':self.level,
    #                 'level1':self.level1,
    #                 'level2':self.level2,
    #                 'level3':self.level3,
    #                 }
    #     head_ids=spec_rel_obj.create(head_val)
        
        # 
        # i=1
        # j=0
        # for li in a:            
        #     print(';;;;;;;;;;;;;;;;',a[j][i+1]['level'])
        #     print(';;;;;;;;;;;;;;;;',a[j][i+1]['level_id'])

        #     det_val={'level':a[j][i+1]['level'],
        #             'level_id':a[j][i+1]['level_id'],                    
        #             }
        #     det_ids=spec_rel_obj.create(det_val)
        #     j+=1
        # i+=1
        # return head_ids



    
class spec_relate_other(models.Model):
    _name='spec.relate.other'
    

 
   





