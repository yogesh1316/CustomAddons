from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"
    
    sale_order_schedule_id=fields.Many2one('sale.order.schedule',string="Sale Order Schedule Line")
    
    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return [
            'product_id', 'price_unit', 'product_packaging', 'procure_method',
            'product_uom', 'restrict_partner_id', 'scrapped', 'origin_returned_move_id'
        ]
    
    @api.model
    def _prepare_merge_move_sort_method(self, move):
        """
        Added date_expected so that moves are sorted according to date_expected.
        Changes by Jeevan Gangarde March 2019
        """
        move.ensure_one()
        return [
            move.product_id.id, move.price_unit, move.product_packaging.id, move.procure_method, 
            move.product_uom.id, move.restrict_partner_id.id, move.scrapped, move.origin_returned_move_id.id,
        ]
            #move.date_expected

    def _prepare_procurement_values(self):
        """
        Before gonig to run method this method is called to prepare values for searching rule ,etc.
        Added SaleOrderSchedule id. Which reflects in stock_move.
        Changes by Jeevan Gangarde March 2019
        """
        """ Prepare specific key for moves or other componenets that will be created from a procurement rule
        comming from a stock move. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        self.ensure_one()
        group_id = self.group_id or False
        if self.rule_id:
            if self.rule_id.group_propagation_option == 'fixed' and self.rule_id.group_id:
                group_id = self.rule_id.group_id
            elif self.rule_id.group_propagation_option == 'none':
                group_id = False
        return {
            'company_id': self.company_id,
            'date_planned': self.date_expected,
            'move_dest_ids': self,
            'group_id': group_id,
            'route_ids': self.route_ids,
            'warehouse_id': self.warehouse_id or self.picking_id.picking_type_id.warehouse_id or self.picking_type_id.warehouse_id,
            'priority': self.priority,
            'sale_order_schedule_id':self.sale_order_schedule_id.id
        }

    
    def _assign_picking(self):
        """
        Added scheduled date in search . So that the pickings are grouped according to the date_expected.
        Changes by Jeevan Gangarde March 2019
        """
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        for move in self:
            recompute = False
            picking = Picking.search([
                ('scheduled_date','=',move.date_expected),
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
            if picking:
                if picking.partner_id.id != move.partner_id.id or picking.origin != move.origin:
                    # If a picking is found, we'll append `move` to its move list and thus its
                    # `partner_id` and `ref` field will refer to multiple records. In this
                    # case, we chose to  wipe them.
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            move._assign_picking_post_process(new=recompute)
            # If this method is called in batch by a write on a one2many and
            # at some point had to create a picking, some next iterations could
            # try to find back the created picking. As we look for it by searching
            # on some computed fields, we have to force a recompute, else the
            # record won't be found.
            if recompute:
                move.recompute()
        return True