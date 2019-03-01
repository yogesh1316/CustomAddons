# -*- coding: utf-8 -*-
from odoo import models, fields, api

class product_move(models.Model):
    _inherit= 'stock.move.line'

    issue = fields.Float(strings="Issue")
    receipt= fields.Float(strings="Receipt")
    available_quantity=fields.Float(string="Opening Stock")
    closing_quantity=fields.Float(string="Closing Stock")
    # tran_type=fields.Char(string="Move Type", help='Identify transaction type')
 

    @api.constrains('qty_done','location_id')
    def product_move_detail(self):

        print('location_id......',self.location_id)
        stock_quant_obj=self.env['stock.quant']
        data=stock_quant_obj.search([('product_id','=',self.product_id.id),('location_id','=',14)])
        #print('data.....',data,data[0].quantity)
        if data:
            self.available_quantity=data[0].quantity
                #self.env.cr.execute("update stock_move_line set available_quantity= %s where id= %s",(data[0].quantity,,))    
        
        print('location_id',self.location_id.name)
        if self.location_id.name=='Vendors':
            self.receipt=self.qty_done
            self.closing_quantity=self.available_quantity + self.qty_done
            print('location_id, Qty',self.location_id.name,self.qty_done)
        elif self.location_id.name=='Stock':
            self.issue=self.qty_done
            self.closing_quantity=self.available_quantity - self.issue
        elif self.location_id.name=='Production':
            print('in production...',self.qty_done)
            self.receipt=self.qty_done
            self.closing_quantity=self.available_quantity + self.qty_done        
        elif self.location_id.name=='Inventory adjustment':
            avl_qty=0
            avl_qty=self.available_quantity+self.qty_done
            print("................",avl_qty)
            
            if self.available_quantity<avl_qty:                
                self.receipt=self.qty_done
                self.closing_quantity=self.available_quantity + self.receipt

   
class product_template_inhe(models.Model):
    _inherit='product.template'

    stock_move_line_ids=fields.One2many('stock.move.line','product_id')


