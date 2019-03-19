# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import Warning,UserError


# create_by | create_date | update_by | update_date
# Chandrakant   12/03/2019   
# Info : create for process_id change


class change_process_id(models.Model):
    _name='process_id.change'
    _rec_name='name'
    
    
   

    bom_id= fields.One2many('mrp.bom','change_process_id',string="bom_id")
    product_tmpl_id=fields.Many2one('product.template',string="Item Code" ,domain="[('bom_process_id', '!=',False)]")
    process_id=fields.Integer(string="New Process ID",store=True)
    old_pro_id=fields.Integer(string='Old Process ID',store=True)
    mrp_type_id=fields.Char(string='MRP Type',store=True)
    item_type_id=fields.Char(string='Item Type',store=True)
    text=fields.Char(string='Text',store=True)
    make=fields.Char(string='Make',store=True)
    process_dscp=fields.Char(string='Process Description',store=True)
    uom=fields.Char(string='UOM',store=True)
    name=fields.Char(default='Process ID Change')

    
    @api.onchange('product_tmpl_id')
    def change_process_id(self):
        obj=self.env['product.template'].search([('id','=',self.product_tmpl_id.id)])
        bom_obj=self.env['mrp.bom'].search([('product_tmpl_id','=',obj.id),('process_id','=',True)])
        bom_obj1=self.env['mrp.bom'].search([('product_tmpl_id','=',obj.id)])
        if obj:
            self.old_pro_id=obj.bom_process_id
            self.mrp_type_id=obj.mrp_type.mrp_description
            self.item_type_id=obj.item_type.item_type_name
            self.text=obj.text_master_id.text_description
            self.make=obj.manufacturer.make_description
            self.uom=obj.uom_id.name
            self.process_dscp=bom_obj.description


    @api.onchange('product_tmpl_id','bom_id')
    def select_new_process_id(self):
        if self.product_tmpl_id:
            self.bom_id=self.product_tmpl_id.bom_ids
            l=[]
            l1=[]
            for i in self.bom_id:
                if i.select_bom == True:
                    l.append(i.process_id)
                    self.process_id=i.process_id
                elif len(l)==0:
                    self.process_id=0
            if self.bom_id:
                for j in self.bom_id:
                    l1.append(j.process_id)
                if len(l1)==1:
                    raise UserError(_('This Product has only one Process Id'))

            if len(l)>1:
                raise UserError(_('Select only one Bom'))

            


   
    @api.model
    def create(self,vals):
        if vals['process_id']==0:
            raise Warning(_('Please select atleast one Bom'))
        id=super(change_process_id,self).create(vals)
        id.product_tmpl_id.write({'bom_process_id': id.process_id})
        return id

    @api.multi
    def write(self,vals):
        if vals['process_id']==0:
            raise Warning(_('Please select atleast one Bom'))
        self.product_tmpl_id.write({'bom_process_id': vals['process_id']})
        ids=super(change_process_id, self).write(vals)
        return ids
        
        
        

        
        


        
  