from odoo import api, fields, models, _

# create_by | create_date | update_by | update_date
# Chandrakant   25/03/2019   
# Info : diplay customer on manufacture oorder and ppurchase order  tree view.
class mrp_inhe(models.Model):
    _inherit='mrp.production'


    partner_id = fields.Many2one('res.partner', string='Customer',compute='compute_customer', readonly=True, index=True)


    @api.depends('origin')
    def compute_customer(self):
        for production in self:
            sale_obj=self.env['sale.order'].search([('name','=',production.origin)])
            if sale_obj:
                production.partner_id=sale_obj.partner_id

class mrp_order_inhe(models.Model):
    _inherit='mrp.workorder'
     # update:change string name

    production_id = fields.Many2one(
        'mrp.production', 'Work Order',
        index=True, ondelete='cascade', required=True, track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

class purchase_order_inhe(models.Model):
    _inherit='purchase.order'

    customer=fields.Char(string="Customer",compute='compute_po_customer')

    @api.depends('origin')
    def compute_po_customer(self):
        list=[]
        cust=''
        for order in self:
            if order.origin:
                li=[]
                li=[i for i in order.origin.split(',')]
                for i in li:
                    if ":" in i:
                        list=[j for j in i.split(':')]
                        a=str(list[0])
                        sale_obj=self.env['sale.order'].search([('name','=',a.strip())])
                        for i in sale_obj:
                            cust=cust+str(i.partner_id.display_name+',')
                            order.customer=cust
                    else:
                        sale_obj=self.env['sale.order'].search([('name','=',i.strip())])
                        for i in sale_obj:
                            cust=cust+str(i.partner_id.display_name+',')
                            order.customer=cust
                cust=""


# class stock_picking_inhe(models.Model):
#     _inherit='stock.picking'

#     vendor=fields.Char(string="Vendor")


#     @api.depends('origin')
#     def compute_vendor(self):
#         for move in self:
#             purchase_obj=self.env['purchase.order'].search([('name','=',move.origin)])
#             if purchase_obj:
#                 move.vendor=purchase_obj.partner_id

