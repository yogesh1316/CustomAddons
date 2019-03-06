from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from datetime import datetime

class purchase_model_inhe(models.Model):
    _inherit = 'purchase.order'
    date_planned = fields.Date(string='Expected Delivery Date', compute='_compute_date_planned', store=True, index=True)
    dr_lines=fields.One2many('upload_tab.info', 'pur_order_dr_id', string='Order Lines')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        if self.origin:
            sale_order_obj = self.env['sale.order']
            so_no=sale_order_obj.search([('opf_name','=',self.origin)])
            stock_picking_obj=self.env['stock.picking']
            pick_id=stock_picking_obj.search([('origin','=',so_no.name)])
            #print('pick_id',pick_id)
            #for order in pick_id:
            self.delivery_count = len(pick_id)

    @api.multi
    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        sale_order_obj = self.env['sale.order']
        so_no=sale_order_obj.search([('opf_name','=',self.origin)])
        stock_picking_obj=self.env['stock.picking']
        pick_id=stock_picking_obj.search([('origin','=',so_no.name)])
        action = sale_order_obj.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = pick_id
        #pickings = sale_order_obj.mapped('picking_ids')
        print('*pickings.ids',pickings.ids)
        #print('action',action)
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(sale_order_obj.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action

class upload_file_purchase(models.Model):
    _inherit = 'upload_tab.info'
    pur_order_dr_id = fields.Many2one('purchase.order',string='Order DR Reference', ondelete='cascade',
     index=True, copy=False,default=0)
    