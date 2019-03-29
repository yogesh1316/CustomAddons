# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models,fields,_
from odoo.exceptions import UserError
import copy


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    #procure_flag=fields.Boolean(string="Procure Flag",default=False)
    
    sale_schedule_line_ids = fields.Many2many(
        'sale.order.schedule',
        'sale_order_schedule_mo_rel',
        'mo_id', 'sale_order_schedule_id', readonly=True, copy=False)
    
    def _mto_with_stock_condition(self, move):
        """Extensibility-enhancer method for modifying the scenarios when
        MTO/MTS method should apply."""
        return move.location_id in move.product_id.mrp_mts_mto_location_ids

    @api.multi
    def action_assign(self):
        """Reserves available products to the production order but also creates
        procurements for more items if we cannot reserve enough (MTO with
        stock).
        @returns True"""
        # reserve all that is available (standard behaviour):
        res = super(MrpProduction, self).action_assign()

        # try to create procurements only if the procure_flag is false:
        #if self.procure_flag == False:
        move_obj = self.env['stock.move']
        for production in self:
            warehouse = production.location_src_id.get_warehouse()
            mto_with_no_move_dest_id = warehouse.mrp_mto_mts_forecast_qty
            move_ids = copy.copy(self.move_raw_ids.ids)
            for move in move_obj.browse(move_ids):
                new_move = False
                qty_to_procure = 0.0
                if move.state in ('partially_available', 'confirmed') \
                        and move.procure_method == 'make_to_stock' \
                        and mto_with_no_move_dest_id and \
                        self._mto_with_stock_condition(move):
                    qty_to_procure = production.get_mto_qty_to_procure(move)
                    if qty_to_procure > 0.0:
                        new_move = move
                    else:
                        continue
                if new_move:
                    production.run_procurement(new_move, qty_to_procure,
                                                mto_with_no_move_dest_id)
        return res

    @api.multi
    def _adjust_procure_method(self):
        """When configured as MTO/MTS manufacturing location, if there is
        stock available unreserved, use it and procure the remaining."""
        res = super()._adjust_procure_method()
        warehouse = self.location_src_id.get_warehouse()
        mto_with_no_move_dest_id = warehouse.mrp_mto_mts_forecast_qty
        for move in self.move_raw_ids:
            if not self._mto_with_stock_condition(move):
                continue
            new_move = False
            qty_to_procure = 0.0
            if not mto_with_no_move_dest_id:
                # We have to split the move because we can't have
                # a part of the move that have ancestors and not the
                # other else it won't ever be reserved.
                qty_to_procure = min(
                    move.product_uom_qty -
                    move.product_id.qty_available_not_res,
                    move.product_uom_qty)
                if 0.0 < qty_to_procure < move.product_uom_qty:
                    # we need to adjust the unit_factor of the stock moves
                    # to split correctly the load of each one.
                    ratio = qty_to_procure / move.product_uom_qty
                    new_move = move.copy({
                        'product_uom_qty': qty_to_procure,
                        'procure_method': 'make_to_order',
                        'unit_factor': move.unit_factor * ratio,
                    })
                    move.write({
                        'product_uom_qty':
                            move.product_uom_qty - qty_to_procure,
                        'unit_factor': move.unit_factor * (1 - ratio),
                    })
                    move._action_confirm()
                    move._action_assign()
                elif qty_to_procure > 0.0:
                    new_move = move
                else:
                    # If we don't need to procure, we reserve the qty
                    # for this move so it won't be available for others,
                    # which would generate planning issues.
                    move._action_confirm()
                    move._action_assign()
            if new_move:
                self.run_procurement(
                    new_move, qty_to_procure, mto_with_no_move_dest_id)
        return res

    @api.multi
    def run_procurement(self, move, qty, mto_with_no_move_dest_id):
        self.ensure_one()
        errors = []
        values = move._prepare_procurement_values()
        # In that mode, we don't want any link between the raw material move
        # And the previous move generated now.
        if mto_with_no_move_dest_id:
            values.pop('move_dest_ids', None)
        origin = self.origin or move.origin
        values['route_ids'] = move.product_id.route_ids
        try:
            self.env['procurement.group'].run(
                move.product_id,
                qty,
                move.product_uom,
                move.location_id,
                origin,
                origin,
                values
            )
        except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.model
    def _get_incoming_qty_waiting_validation(self, move):
        """
        This method should be overriden in submodule to manage cases where
        we need to add quantities to the forecast quantity. Like draft
        purchase order, purchase request, etc...
        """
        return 0.0

    @api.multi
    def get_mto_qty_to_procure(self, move):
        self.ensure_one()
        stock_location_id = move.location_id.id
        move_location = move.with_context(location=stock_location_id)
        virtual_available = move_location.product_id.virtual_available
        qty_available = move.product_id.uom_id._compute_quantity(
            virtual_available, move.product_uom)
        draft_incoming_qty = self._get_incoming_qty_waiting_validation(move)
        qty_available += draft_incoming_qty
        if qty_available >= 0:
            return 0.0
        else:
            if abs(qty_available) < move.product_uom_qty:
                return abs(qty_available)
        return move.product_uom_qty

    @api.multi
    def _generate_moves(self,values):
        for production in self:
            production._generate_finished_moves(values)
            factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            production._generate_raw_moves(lines,values)
            # Check for all draft moves whether they are mto or not
            production._adjust_procure_method()
            production.move_raw_ids._action_confirm()
        return True

    def _generate_finished_moves(self,values):
        print("Generate finished move ids",values)
        move = self.env['stock.move'].create({
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.product_qty,
            'location_id': self.product_id.property_stock_production.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'origin': self.name,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'move_dest_ids': [(4, x.id) for x in self.move_dest_ids],
            'sale_order_schedule_id':values['sale_schedule_line_ids'][0][2][0] if 'sale_schedule_line_ids' in values else False
        })
        move._action_confirm()
        return move

    def _generate_raw_moves(self, exploded_lines,values):
        self.ensure_one()
        moves = self.env['stock.move']
        for bom_line, line_data in exploded_lines:
            moves += self._generate_raw_move(bom_line, line_data,values)
        return moves

    def _generate_raw_move(self, bom_line, line_data, values):
        quantity = line_data['qty']
        # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
        alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
        if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
            return self.env['stock.move']
        if bom_line.product_id.type not in ['product', 'consu']:
            return self.env['stock.move']
        if self.routing_id:
            routing = self.routing_id
        else:
            routing = self.bom_id.routing_id
        if routing and routing.location_id:
            source_location = routing.location_id
        else:
            source_location = self.location_src_id
        original_quantity = (self.product_qty - self.qty_produced) or 1.0
        #Create New procurement group for child components as their date for picking may be different then that of MO
        group_id = self.env['procurement.group'].create({
            'name': self.name, 'move_type': 'direct',
            'sale_id': self.procurement_group_id.sale_id.id,
            'partner_id': self.procurement_group_id.partner_id.id,
        })
        data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
            'sale_order_schedule_id':values['sale_schedule_line_ids'][0][2][0] if 'sale_schedule_line_ids' in values else False
        }
        return self.env['stock.move'].create(data)

class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'
    #action = fields.Selection(selection_add=[('manufacture', 'Manufacture')])

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if values.get('sale_line_id', False):
            result['sale_line_id'] = values['sale_line_id']
        if values.get('sale_order_schedule_id', False):
            result['sale_order_schedule_id'] = values['sale_order_schedule_id']
        return result

    def _run_move(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if not self.location_src_id:
            msg = _('No source location defined on procurement rule: %s!') % (self.name, )
            raise UserError(msg)

        # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
        # Search if picking with move for it exists already:
        group_id = False
        if self.group_propagation_option == 'propagate':
            group_id = values.get('group_id', False) and values['group_id'].id
        elif self.group_propagation_option == 'fixed':
            group_id = self.group_id.id
        print("_run_moves--------------->>>>.",values)
        data = self._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        # Since action_confirm launch following procurement_group we should activate it.
        move = self.env['stock.move'].sudo().with_context(force_company=data.get('company_id', False)).create(data)
        move._action_confirm()
        return True

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, values, bom):
        print("--------------_<<<>>>>------------",values)
        #sale_order_line_obj=self.env['sale.order.line'].browse(values['sale_line_id'])
        return {
            'sale_schedule_line_ids':[(6,0,[values['sale_order_schedule_id']])],
            'origin': origin,
            'product_id': product_id.id,
            'product_qty': product_qty,
            'product_uom_id': product_uom.id,
            'location_src_id': self.location_src_id.id or location_id.id,
            'location_dest_id': location_id.id,
            'bom_id': bom.id,
            'date_planned_start': fields.Datetime.to_string(self._get_date_planned(product_id, values)),
            'date_planned_finished': values['date_planned'],
            'procurement_group_id': values.get('group_id').id if values.get('group_id', False) else False,
            'propagate': self.propagate,
            'picking_type_id': self.picking_type_id.id or values['warehouse_id'].manu_type_id.id,
            'company_id': values['company_id'].id,
            'move_dest_ids': values.get('move_dest_ids') and [(4, x.id) for x in values['move_dest_ids']] or False,
        }
