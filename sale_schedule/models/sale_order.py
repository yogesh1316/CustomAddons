from odoo import api, fields, models,_
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError
from datetime import datetime, timedelta




class SaleOrder(models.Model):
    _inherit="sale.order"

    sale_order_released = fields.Boolean(string="Order Released",default=False)
    
    """
    Flag for Confirm Sale Button. Once all the sale_order_schedule lines are closed this flag will
    will be set to true and then the button will be invisible.
    Changes by Jeevan Gangarde March 2019
    """
    @api.multi
    def _action_confirm(self):
        super(SaleOrder, self)._action_confirm()
        for order in self:
            for line in order.order_line:
                for schedule_line in line.schedule_lines:
                    if schedule_line.state == 'close':
                        self.write({
                            'sale_order_release': True
                        })
                    else:
                        self.write({
                            'sale_order_release': False
                        })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    schedule_lines=fields.One2many('sale.order.schedule','order_line_id')
    released_qty=fields.Float(string="Released Quantity")

    @api.multi
    def view_sale_order_schedule(self):
        """
        Returns the Schedule form
        Changes by Jeevan Gangarde March 2019
        """
        view=self.env.ref('sale_schedule.sale_order_line_view_form')
        #print("OKK")
        return {
            'name': _('Schedule Orders'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }
    
    @api.multi
    def _action_launch_procurement_rule(self):
        """
        This method is the entry point function for Sales Order Simulation .
        The method earlier took the quantity of from the sale_order_line but now its takes from the 
        sale_order_schedule only for which the flag (open(default),release,close) is release.
        Changes by Jeevan Gangarde March 2019.
        """
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_move', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            for schedule_line in line.schedule_lines:
                if schedule_line.state == 'release' :
                    if line.state != 'sale' or not line.product_id.type in ('consu','product'):
                        continue
                    qty = line._get_qty_procurement()
                    
                    if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                        continue
                    # group_id=False
                    # group_id = line.order_id.procurement_group_id
                    #for schedule_line in line.schedule_lines:
                    group_id = schedule_line.procurement_group_id
                    if not group_id:
                        group_id = self.env['procurement.group'].create({
                            'name': schedule_line.order_line_id.name_get()[0][1], 'move_type': line.order_id.picking_policy,
                            'sale_id': line.order_id.id,
                            'partner_id': line.order_id.partner_shipping_id.id,
                        })
                        schedule_line.procurement_group_id = group_id
                    else:
                        # In case the procurement group is already created and the order was
                        # cancelled, we need to update certain values of the group.
                        updated_vals = {}
                        if group_id.partner_id != line.order_id.partner_shipping_id:
                            updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                        if group_id.move_type != line.order_id.picking_policy:
                            updated_vals.update({'move_type': line.order_id.picking_policy})
                        if updated_vals:
                            group_id.write(updated_vals)

                    values = line._prepare_procurement_values(group_id=group_id)
                    values['sale_order_schedule_id']=schedule_line.id
                    product_qty = line.product_uom_qty - qty
                    procurement_uom = line.product_uom
                    quant_uom = line.product_id.uom_id
                    get_param = self.env['ir.config_parameter'].sudo().get_param
                    if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                        product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                        procurement_uom = quant_uom
                    #for schedule_line in line.schedule_lines:
                    product_qty=0
                    if schedule_line.state=='release':
                        print("_____-----^^^--^^^-----_____")
                        product_qty=schedule_line._get_qty_procurement()
                        date_planned= datetime.strptime(schedule_line.release_date, DEFAULT_SERVER_DATETIME_FORMAT)\
                    + timedelta(days=self.customer_lead or 0.0) - timedelta(days=self.order_id.company_id.security_lead)
                        values.update({
                            'date_planned' :date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        })
                        try:
                            self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
                        except UserError as error:
                            errors.append(error.name)
                        
                    if errors:
                        raise UserError('\n'.join(errors))
        return True




 

class SaleOrderSchedule(models.Model):
    _name = 'sale.order.schedule'
    _description = 'Sales Order Line Schedule'

    name = fields.Char(string='Name')
    mo_lines= fields.Many2many('mrp.production', 'sale_order_schedule_mo_rel','sale_order_schedule_id','mo_id', copy=False)
    order_line_id=fields.Many2one('sale.order.line')
    product_id=fields.Many2one('product.product',string="Product")
    product_uom_id=fields.Many2one('product.uom', string='Unit of Measure')
    product_qty=fields.Float('Quantity',store=True)
    state=fields.Selection([('release','Release'),('open','Open'),('close','Close')])
    qty_release=fields.Float(string="Release Quantity")
    release_date = fields.Datetime(string='Release Date')
    procurement_group_id=fields.Many2one('procurement.group')
    
    @api.multi
    def _get_qty_procurement(self):
        """
        Called in action_launch_procurement_rule to get the released quantity
        Changes by Jeevan Gangarde March 2019
        """
        for schedule_line in self:
            return schedule_line.qty_release