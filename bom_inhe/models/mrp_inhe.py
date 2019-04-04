from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


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


class Picking(models.Model):
    _inherit='stock.picking'


    country_of_final_dest=fields.Many2one('res.country',string="Country Of Final Destination")
    port_of_landing=fields.Char(string="Port Of Landing")
    port_of_discharge=fields.Char(string="Port Of Discharge")
    net_wt=fields.Float(string="Net Weight")
    gross_wt=fields.Float(string="Gross Weight")
    dimension=fields.Char(string="Dimension")
    material_description=fields.Char(string="Material Description")
    number_of_packages = fields.Integer(string='Number of Packages\n(Box Number)', copy=False)
    carrier_tracking_ref = fields.Char(string='Tracking Reference\n(Box Name)', copy=False)



    # vendor=fields.Char(string="Vendor")


    # @api.depends('origin')
    # def compute_vendor(self):
    #     for move in self:
    #         purchase_obj=self.env['purchase.order'].search([('name','=',move.origin)])
    #         if purchase_obj:
    #             move.vendor=purchase_obj.partner_id

    @api.model
    def create(self, vals):
        # TDE FIXME: clean that 
        

        defaults = self.default_get(['name', 'picking_type_id'])
        pick_type=self.env['stock.picking.type'].browse(vals['picking_type_id'])
        # if pick_type.name=='Receipts' or pick_type.name=='Internal Transfers' or pick_type.name=='Manufacturing':
        if pick_type.name=='Pick' or pick_type.name=='Pack' or pick_type.name=='Delivery Orders':
            # if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
            #     vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
            vals['name'] = False

        # TDE FIXME: what ?
        # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
        # As it is a create the format will be a list of (0, 0, dict)
        if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
            for move in vals['move_lines']:
                if len(move) == 3:
                    move[2]['location_id'] = vals['location_id']
                    move[2]['location_dest_id'] = vals['location_dest_id']
        res = super(Picking, self).create(vals)
        res._autoconfirm_picking()
        
        return res

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some lines to move'))
        if not self.name:
            # vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()

            self.name=self.picking_type_id.sequence_id.next_by_id()

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids)
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_('You cannot validate a transfer if you have not processed any quantity. You should rather cancel the transfer.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a lot/serial number for %s.') % product.display_name)
                    elif line.qty_done == 0:
                        raise UserError(_('You cannot validate a transfer if you have not processed any quantity for %s.') % product.display_name)

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        return



        

