# -*- coding: utf-8 -*-

from odoo import models, fields, api

class inherit_stock_inventory(models.Model):
    _inherit="stock.inventory"

    # To set the inventory_flag True against the selected product in inventory adjustment
    def action_start(self):
        if self.filter == 'none':
            product_obj = self.env['product.product'].search([])
            for i in product_obj:   
                i.inventory_flag = True
        elif self.filter == 'category': 
            self.ensure_one() 
            category_obj = self.env['product.template'].search([('categ_id','=',self.category_id.id)])
            print("Category id",category_obj)
            for i in category_obj:
                product_obj = i.env['product.product'].search([('product_tmpl_id','=',i.id)])
                print("product_obj",product_obj)
                for j in product_obj:
                    j.inventory_flag = True
                    print("Flag ",j.inventory_flag)
        elif self.filter == 'product':
            product_obj = self.env['product.product'].search([('id','=',self.product_id.id)])
            if product_obj:
                product_obj.inventory_flag = True
        # elif self.filter == 'partial':
        #     pass
        for inventory in self.filtered(lambda x: x.state not in ('done','cancel')):
            vals = {'state': 'confirm', 'date': fields.Datetime.now()}
            if (inventory.filter != 'partial') and not inventory.line_ids:
                vals.update({'line_ids': [(0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
            inventory.write(vals)
        return True

     # To set the inventory_flag false against the selected product in inventory adjustment
    def action_done(self):
        for i in self.line_ids:    
            if self.env['product.product'].search([('id','=',i.product_id.id)]):
                # for j in self.line_ids:
            #     if i.id == j.product_id:
            #         print("Product line id",i.inventory_flag)
                if i.product_id.inventory_flag == True:
                    i.product_id.inventory_flag = False
        negative = next((line for line in self.mapped('line_ids') if line.product_qty < 0 and line.product_qty != line.theoretical_qty), False)
        if negative:
            raise UserError(_('You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s') % (negative.product_id.name, negative.product_qty))
        self.action_check()
        self.write({'state': 'done'})
        self.post_inventory()
        return True

    def action_cancel_draft(self):
        for i in self.line_ids:    
            if self.env['product.product'].search([('id','=',i.product_id.id)]):
                # for j in self.line_ids:
            #     if i.id == j.product_id:
            #         print("Product line id",i.inventory_flag)
                if i.product_id.inventory_flag == True:
                    i.product_id.inventory_flag = False
        self.mapped('move_ids')._action_cancel()
        self.write({
            'line_ids': [(5,)],
            'state': 'draft'
        })

    @api.multi
    def write(self, values):
        res = super(inherit_stock_inventory, self).write(values)
        if self.line_ids:
            for i in self.line_ids:
                i.product_id.inventory_flag=True
        values.pop('product_name', False)
        return res