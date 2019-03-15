from collections import defaultdict
import math

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare
import datetime
from itertools import groupby
from operator import itemgetter
from odoo.tools.float_utils import float_compare, float_round, float_is_zero

# create_by | create_date | update_by | update_date
# Ganesh      27/10/2018    
# Info : mrp.production inherit to calculate start date and end date on lead time or cumulative time 

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order '

    # Field inherit for change the name and required rule
    date_planned_start = fields.Datetime(
        'Planned Start', copy=False, 
        index=True, required=False,
        states={'confirmed': [('readonly', False)]}, oldname="date_planned")
    date_planned_finished = fields.Datetime(
        'Planned End', copy=False,
        index=True, 
        states={'confirmed': [('readonly', False)]})

    cum_setup_time = fields.Float(string='Cumulative setup time', help="Setup time required for Operation")
    cum_ope_time = fields.Float(string='Cumulative operation time', help="Time required to perform Operation")
    cum_tran_time = fields.Float(string='Cumulative transfer time', help="Setup time required for Operation")
    statusflag = fields.Char('Status for tracking mrp_production O-Open, R-Release, D-Document print, I-Issues, C-Complete')
    produced_qty = fields.Float('Can be feedback',default=0.0, readonly=True)
    complete_qty = fields.Float('Completed quantity',default=0.0, readonly=True)
    balance_qty = fields.Float('Balance quantity',default=0.0, readonly=True)


    @api.constrains('complete_qty')
    def balance_qty_set(self):
        self.balance_qty = self.product_qty-self.complete_qty


    @api.constrains('produced_qty')
    def workorder_producing_qty_set(self):
        if self.workorder_ids:        
            for line in self.workorder_ids:
                line.qty_producing = self.produced_qty

    # Inherit create method for update Cumulative time
    @api.model
    def create(self, values): 
        
        mrp_bom_obj = self.env['mrp.bom']
        production = ''
        mrpdata = mrp_bom_obj.search([('id','=',values['bom_id'])])
        routing = mrpdata.routing_id.id        
        if routing:
            self._cr.execute("select cum_setup_time,cum_ope_time,cum_tran_time from mrp_routing_workcenter where routing_id =%s order by id desc limit 1",(routing,))
            cum_time= self.env.cr.fetchall() 
            print('data',cum_time)
            if cum_time:                
                cst = cum_time[0][0]
                cot = cum_time[0][1]
                ctt = cum_time[0][2]
            else:
                cst = 0
                cot = 0
                ctt = 0

            values['cum_setup_time']=cst
            values['cum_ope_time']=cot
            values['cum_tran_time']=ctt
            values['statusflag']='O'

            if not values.get('name', False) or values['name'] == _('New'):
                if values.get('picking_type_id'):
                    values['name'] = self.env['stock.picking.type'].browse(values['picking_type_id']).sequence_id.next_by_id()
                else:
                    values['name'] = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
            if not values.get('procurement_group_id'):
                values['procurement_group_id'] = self.env["procurement.group"].create({'name': values['name']}).id
            
            if not values['date_planned_start']:
                raise UserError(_('Select Planned Start date for create MRP order'))
            production = super(MrpProduction, self).create(values)
            #production._generate_moves()
        return production   

    # Calculate Planned end date on start date with lead or cumulative time
    @api.onchange('date_planned_start')    
    def date_planned_start_cal(self):        
        self.date_planned_finished=''        
        cum_time=''                    
        if self.date_planned_start:                          
            if self.product_id:
                day=self._day_cal()    
                planneddate = self._planneddatecal(self.date_planned_start,day,'S')
                
                self.date_planned_finished = planneddate
            
    # Calculate Planned start date on end date with lead or cumulative time
    @api.onchange('date_planned_finished')    
    def date_planned_finished_cal(self):       
        self.date_planned_start=''
        cum_time=''
        if self.date_planned_finished:  
            if self.product_id:                            
                day =self._day_cal()  
                planneddate = self._planneddatecal(self.date_planned_finished,day,'E')
                self.date_planned_start = planneddate  
                
    # Calculate day on item type and it's lead day or cumulative time
    def _day_cal(self):
        cst = 0.00
        cot = 0.00       
        ctt = 0.00  
        day = 0.00
        if self.routing_id:
            routing = self.routing_id.id            
        else:
            routing = self.bom_id.routing_id.id

        if self.product_id: 
            if self.product_id.item_type.id==1:            
                if self.product_id.produce_delay > 0:
                    day = self.product_id.produce_delay      #Manufacturing Lead Time
                else:
                    raise UserError(_('There is no Manufacturing lead time for item %s please add') %(self.product_id.name,))
            else:
                if routing:
                    self._cr.execute("select cum_setup_time,cum_ope_time,cum_tran_time from mrp_routing_workcenter where routing_id =%s order by id desc limit 1",(routing,))
                    cum_time= self.env.cr.fetchall() 
                    
                    cst = cum_time[0][0]
                    cot = cum_time[0][1]
                    ctt = cum_time[0][2]
                    
                    mins = (cst+(cot*self.product_qty)+(ctt*60))
                    
                    day = math.ceil((mins/60)/8)  
                else:
                    raise UserError(_('set cumulative time for Routing'))         
        return day 
    
    # Calculate date on sequnce no and day with S - Start or E - End date Flag
    @api.multi
    def _planneddatecal(self,date,day,flag ):       
        
        factory_calendor_obj =  self.env['factory.calendor']
        datelist = factory_calendor_obj.search([('ydate','=',date)])
        
        if datelist :
            if datelist.seq_no>0:
                if flag=='S':
                    seq_no = datelist.seq_no + day
                    date_data = factory_calendor_obj.search([('seq_no','=',seq_no)])
                elif flag=='E':            
                    seq_no = datelist.seq_no - day
                    date_data = factory_calendor_obj.search([('seq_no','=',seq_no)])
            else:
                raise UserError(_('Order date %s is declared as Holiday/Week day ') %(date,))
        else:
            raise UserError(_('Order date %s dose not exist in Factory Calendor') %(date,))        
        return date_data.ydate
    
    # On Release Button check Work Order/Operation create or not and update statusflag 
    @api.multi
    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. """

        stock_move_obj=self.env['stock.move']
        orders_to_plan = self.filtered(lambda order: order.routing_id and order.state == 'confirmed')
        if self.product_id.item_type.id >= 4:            
            
            for order in orders_to_plan:
                quantity = order.product_uom_id._compute_quantity(order.product_qty, order.bom_id.product_uom_id) / order.bom_id.product_qty
                boms, lines = order.bom_id.explode(order.product_id, quantity, picking_type=order.bom_id.picking_type_id)
                
                order._generate_workorders(boms)       
                return orders_to_plan.write({'state': 'planned','statusflag':'R'})     
        elif self.product_id.item_type.id <= 3:
            
            assigncount = stock_move_obj.search_count([('state','in',['assigned']),('raw_material_production_id','=',orders_to_plan.id)])  # Add if they want partial production then 'partially_available'
            totalcount = stock_move_obj.search_count([('raw_material_production_id','=',orders_to_plan.id)])
            
            if totalcount==assigncount:
                for order in orders_to_plan:
                    quantity = order.product_uom_id._compute_quantity(order.product_qty, order.bom_id.product_uom_id) / order.bom_id.product_qty
                    boms, lines = order.bom_id.explode(order.product_id, quantity, picking_type=order.bom_id.picking_type_id)
                    
                    order._generate_workorders(boms)
                    return orders_to_plan.write({'state': 'planned','statusflag':'R'})
            else:
                raise UserError(_('In sufficient stock for child items to Release Manufacturing Order'))        

    # This function is use to update statusflag after Document print
    @api.multi
    def print_document(self):
        self.write({'statusflag':'D'})
        return self.env.ref('bom_inhe.action_report_production_order_doc_print').report_action(self)

    # Update : Replace item with old item and pass old item for quality control
    @api.multi
    def action_replace(self):
        for line in self.move_raw_ids.filtered(lambda x: x.r_flag in('N','R')):
            vals={}
            if line.replace_product_id.id>0:
                
                if self.routing_id:
                    routing = self.routing_id
                else:
                    routing = self.bom_id.routing_id

                if routing and routing.location_id:
                    source_location = routing.location_id
                else:
                    source_location = self.location_src_id
                
                vals = {
                    'sequence': line.sequence,
                    'name': self.name,
                    'date': self.date_planned_start,
                    'date_expected': self.date_planned_start,
                    'bom_line_id': line.bom_line_id.id,
                    'product_id': line.replace_product_id.id,
                    'product_uom_qty': line.replace_qty, 
                    'issue_qty': line.replace_qty,                     
                    'product_uom': line.replace_product_id.uom_id.id,
                    'location_id': source_location.id,
                    'location_dest_id': self.location_dest_id.id,
                    'raw_material_production_id': self.id,
                    'company_id': self.company_id.id,
                    'operation_id': line.operation_id.id ,
                    'price_unit': line.product_id.standard_price,
                    'procure_method': 'make_to_stock',
                    'origin': self.name,
                    'warehouse_id': source_location.get_warehouse().id,
                    'group_id': self.procurement_group_id.id,
                    'propagate': self.propagate,
                    'unit_factor': line.replace_qty,
                    'state':'confirmed',
                    'r_flag':'R'
                }
                self.env['stock.move'].create(vals)
                line.write({'r_flag':'O'})

        self.tran_replaceitem_quality()

    #  Update : Take dynamic Internal location for quality control
    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
        return types[:1]

    # Update : Pass old item for quality control
    @api.multi
    def tran_replaceitem_quality(self):
        input_item = {}
        input_line_item = {}
        qua_item = {}
        qua_line_item = {}
        stock_move_obj = self.env['stock.move']
        stock_pick_obj = self.env['stock.picking']
        stock_loc_obj = self.env['stock.location']
        proc_group_obj = self.env['procurement.group']
        po_obj = self.env['purchase.order']
        idata=stock_loc_obj.search([('name','=','Input')])
        qdata=stock_loc_obj.search([('name','=','Quality Control')])
        sdata=stock_loc_obj.search([('name','=','Stock')])
        p_data=proc_group_obj.search([('name','=',self.name)])

        
        # Input move
        if idata :
            input_item = {
                 'origin': self.name,
                 'move_type': 'direct',
                 'state': 'assigned',
                 'scheduled_date': datetime.datetime.now(),
                 'date': datetime.datetime.now(),
                 'location_id': idata.id,
                 'location_dest_id': qdata.id,
                 'picking_type_id': self._default_picking_type().id,
                 'state': 'assigned',
                 'group_id': p_data.id                                
             }

            i_id = stock_pick_obj.create(input_item)
            
            for item in self.move_raw_ids.filtered(lambda x: x.r_flag in('O')):
                input_line_item = {
                 'name': item.product_id.name,
                 'origin': self.name,
                 'product_id': item.product_id.id,
                 'ordered_qty': item.replace_qty,
                 'product_uom_qty': item.replace_qty,
                 'location_id': idata.id,
                 'location_dest_id': qdata.id,
                 'picking_id': i_id.id,
                 'state': 'confirmed',
                 'procure_method':'make_to_stock',
                 'reference': i_id.name,                 
                 'push_rule_id': 1,
                 'product_uom': 1,
                 'group_id': p_data.id ,
                 'picking_type_id': self._default_picking_type().id,
                 'warehouse_id': item.warehouse_id.id
                 }
                i=stock_move_obj.create(input_line_item)                         
        
        # Quality move
        if qdata :
            qua_item = {
                 'origin': self.name,
                 'move_type': 'direct',
                 'state': 'assigned',
                 'scheduled_date': datetime.datetime.now(),
                 'date': datetime.datetime.now(),
                 'location_id': qdata.id,
                 'location_dest_id': sdata.id,
                 'picking_type_id': self._default_picking_type().id,
                 'state': 'assigned',
                 'group_id': p_data.id              
             }

            q_id = stock_pick_obj.create(qua_item)
           
            for item in self.move_raw_ids.filtered(lambda x: x.r_flag in('O')):
                qua_line_item = {
                 'name': item.product_id.name,
                 'origin': self.name,
                 'product_id': item.product_id.id,
                 'ordered_qty': item.replace_qty,
                 'product_uom_qty': item.replace_qty,
                 'location_id': qdata.id,
                 'location_dest_id': sdata.id,
                 'picking_id': q_id.id,
                 'state': 'confirmed',
                 'procure_method': 'make_to_stock',
                 'reference': q_id.name,                
                 'push_rule_id': 2,  
                 'group_id': p_data.id,
                 'product_uom': 1,
                 'picking_type_id': self._default_picking_type().id,
                 'warehouse_id': item.warehouse_id.id
                 }
                q=stock_move_obj.create(qua_line_item)
                item.write({'r_flag':'Q'})
                
        else:
             raise UserError(_('Quality control/Stock Location is not present'))

    # This function is use to update statusflag after Issue Quantity save
    @api.multi
    def action_issue(self):        
        stock_move_obj=self.env['stock.move'] 
       
        if self.product_id.item_type.id >= 4:            
            issuecount = stock_move_obj.search_count([('issue_qty','>',0),('raw_material_production_id','=',self.id)])
            
            if issuecount>=1:                
                self._post_inventory()               
                return self.write({'statusflag':'I'})
            else:
                raise UserError(_('At least 1 item can be Issue Quantity'))    
        elif self.product_id.item_type.id <= 3:
            
            issuecount = stock_move_obj.search_count([('issue_qty','>=',0),('raw_material_production_id','=',self.id)])
            totalcount = stock_move_obj.search_count([('raw_material_production_id','=',self.id)])
            
            if totalcount==issuecount:           
                self._post_inventory()
                return self.write({'statusflag':'I'})                
            else:
                raise UserError(_('All child item can be Issue Quantity'))

    # This Function use to create wizard for Issuing Quantity for Child Item
    @api.multi
    def issue_item_qty(self):        
        return {
            'name': _('Issue'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.production',     
            'res_id': self.id,
            'view_id': self.env.ref('bom_inhe.mrp_production_issue_form_view').id,
            'target': 'new',           
            'context': {'raw_material_production_id': self.id,  
                        'product_ids': (self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids,
                        },            
        }

    @api.multi
    def replace_item(self):        
        return {
            'name': _('Replace'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.production',     
            'res_id': self.id,
            'view_id': self.env.ref('bom_inhe.mrp_production_replace_item_view').id,
            'target': 'new',           
            'context': {'raw_material_production_id': self.id,  
                        'default_product_ids': (self.move_raw_ids.filtered(lambda x: x.state in ('done', 'cancel')) ).mapped('product_id').ids,
                        },            
        }


    # This Function is inherit for comment child item code and only update parent item state done
    @api.multi
    def post_inventory(self):        
        for order in self:            
            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')            

            # moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            
            # for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):                
            #     move.product_uom_qty = move.quantity_done            
            #moves_to_do._action_done()            
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
            order._cal_price(moves_to_do)    
            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done','cancel'))                        
            moves_to_finish._action_done()
            order.action_assign()

            # Logic change we get child item ids from stock move line table and set to consume_move_lines tuple
            stock_move_line_obj = self.env['stock.move.line']
            consume_move_lines = ()
            for ids in moves_not_to_do:
                stockmonveline_id=stock_move_line_obj.search([('move_id','=',ids.id)])
                consume_move_lines += (stockmonveline_id.id,)

            #consume_move_lines = moves_to_do.mapped('active_move_line_ids')
            for moveline in moves_to_finish.mapped('active_move_line_ids'):
                if moveline.product_id == order.product_id and moveline.move_id.has_tracking != 'none':
                    if any([not ml.lot_produced_id for ml in consume_move_lines]):
                        raise UserError(_('You can not consume without telling for which lot you consumed it'))
                    # Link all movelines in the consumed with same lot_produced_id false or the correct lot_produced_id
                    filtered_lines = consume_move_lines.filtered(lambda x: x.lot_produced_id == moveline.lot_id)
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
                else:
                    # Link with everything
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines])]})
                   
        return True

    # This fuction create for child item state done on issue
    @api.multi
    def _post_inventory(self):  
        self.ensure_one()      
        for order in self:
            minqty = 0
            produced_qty=0
            remqty = 0
            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            
            for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):            
                move.product_uom_qty = move.quantity_done
            
            # Logic change here
            # To Assign child item quantity_done which unit_factor * product_qty on tracking here we get code from mrp_workorder
            for move in self.move_raw_ids:
                temp = []
                if move.has_tracking == 'none' and (move.state not in ('done', 'cancel')) and move.bom_line_id\
                            and move.unit_factor and not move.move_line_ids.filtered(lambda ml: not ml.done_wo):
                    rounding = move.product_uom.rounding
                    if self.product_id.tracking != 'none':
                        qty_to_add = float_round(self.product_qty * move.unit_factor, precision_rounding=rounding)
                        move._generate_consumed_move_line(qty_to_add, self.final_lot_id)
                    else:                        
                        remqty = move.product_uom_qty - move.reserved_availability
                        if remqty == 0:
                            
                            if move.r_flag == 'R':
                                remqty=self.product_qty
                            else:
                                remqty = self.product_qty - (self.produced_qty+self.complete_qty)                                
                            move.quantity_done = float_round(remqty * move.unit_factor, precision_rounding=rounding)
                        else:
                            productqty = 0    
                            for qty in self.move_raw_ids.filtered(lambda x: x.state not in ('done','cancel')):       
                                productqty =   qty.reserved_availability / qty.unit_factor 
                                if math.floor(productqty) != 0:
                                    temp.append(math.floor(productqty))   
                            minqty = min(temp)
                            if minqty == 0:
                                raise UserError(_('In sufficient stock for child item') )                                
                            else:                         
                                move.quantity_done = float_round(minqty * move.unit_factor, precision_rounding=rounding)

            if minqty:
                if self.produced_qty < 0:
                    self.produced_qty = 0
                self.produced_qty += minqty                
            else:
                self.produced_qty+=remqty
            
            if move.r_flag=='N':
                self.write({'produced_qty': self.produced_qty})              

            moves_to_do._action_done()            
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
            order._cal_price(moves_to_do)    
            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done','cancel'))            
            order.action_assign()                       
                   
        return True

    # This function is inherit for update statusflag 'C'
    @api.multi
    def button_mark_done(self):       
        self.ensure_one()
        for wo in self.workorder_ids:
            if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
                raise UserError(_('Work order %s is still running') % wo.name)
        self.post_inventory()
        moves_to_cancel = (self.move_raw_ids | self.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_to_cancel._action_cancel()
        self.write({'state': 'done', 'date_finished': fields.Datetime.now(),'statusflag':'C'})       
        return self.write({'state': 'done'})

      
# create_by | create_date | update_by | update_date
# Ganesh      14/11/2018    
# Info : Inherit stock move adding new field to update Issue Quantity

class StockMove(models.Model):
    """ Stock Move inherit """
    _inherit = 'stock.move'
    _description = 'Stock Move' 

    issue_qty = fields.Float('Issue Quantity',digits=dp.get_precision('Product Unit of Measure'),
                required=True, track_visibility='onchange',default=0,)

    # Adding field replace product, replace qty and reason for replace product 04/03/2019 
    replace_product_id = fields.Many2one(
        'product.product', 'Replace Product',
        domain=[('type', 'in', ['product', 'consu'])],        
        states={'confirmed': [('readonly', False)]})
    
    replace_qty = fields.Float('Replace Quantity',digits=dp.get_precision('Product Unit of Measure'),track_visibility='onchange',default=0,)

    replace_reason=fields.Char('Reason for replace')

    r_flag = fields.Char('Replace flag N=New, O=Old, R=Replace and Q=Quality flag is update',default='N')


    # Validate Issue Qty can not enter more then Reserved Qty
    @api.onchange('issue_qty')    
    def issueqty_validate(self):

        if self.issue_qty > self.reserved_availability:
            raise UserError(_('Can not Issue more then Reserved Qty'))   

    # Code changes in _action_assign method
    def _action_assign(self):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `product_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        assigned_moves = self.env['stock.move']
        partially_available_moves = self.env['stock.move']
        for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
            
            if move.location_id.should_bypass_reservation()\
                    or move.product_id.type == 'consu':
                # create the move line(s) but do not impact quants
                if move.product_id.tracking == 'serial' and (move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                    for i in range(0, int(move.product_qty - move.reserved_availability)):
                        self.env['stock.move.line'].create(move._prepare_move_line_vals(quantity=1))
                else:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                            ml.location_id == move.location_id and
                                                            ml.location_dest_id == move.location_dest_id and
                                                            ml.picking_id == move.picking_id and
                                                            not ml.lot_id and
                                                            not ml.package_id and
                                                            not ml.owner_id)
                    if to_update:
                        to_update[0].product_uom_qty += move.product_qty - move.reserved_availability
                    else:
                        self.env['stock.move.line'].create(move._prepare_move_line_vals(quantity=move.product_qty - move.reserved_availability))
                assigned_moves |= move
            else:
                if not move.move_orig_ids:
                    if move.procure_method == 'make_to_order':
                        continue
                    # Reserve new quants and create move lines accordingly.
                    available_quantity = self.env['stock.quant']._get_available_quantity(move.product_id, move.location_id)
                    if available_quantity <= 0:                        
                        continue
                    need = move.product_qty - move.reserved_availability
                    taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id, strict=False)
                    
                    # update issue qty here as taken_quantity in stock_move, code change here 06/02/2019
                    move.write({'issue_qty': taken_quantity})
                    if float_is_zero(taken_quantity, precision_rounding=move.product_id.uom_id.rounding):
                        continue
                    if need == taken_quantity:
                        assigned_moves |= move
                    else:
                        partially_available_moves |= move
                else:
                    # Check what our parents brought and what our siblings took in order to
                    # determine what we can distribute.
                    # `qty_done` is in `ml.product_uom_id` and, as we will later increase
                    # the reserved quantity on the quants, convert it here in
                    # `product_id.uom_id` (the UOM of the quants is the UOM of the product).
                    move_lines_in = move.move_orig_ids.filtered(lambda m: m.state == 'done').mapped('move_line_ids')
                    keys_in_groupby = ['location_dest_id', 'lot_id', 'result_package_id', 'owner_id']

                    def _keys_in_sorted(ml):
                        return (ml.location_dest_id.id, ml.lot_id.id, ml.result_package_id.id, ml.owner_id.id)

                    grouped_move_lines_in = {}
                    for k, g in groupby(sorted(move_lines_in, key=_keys_in_sorted), key=itemgetter(*keys_in_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_in[k] = qty_done
                    move_lines_out_done = (move.move_orig_ids.mapped('move_dest_ids') - move)\
                        .filtered(lambda m: m.state in ['done'])\
                        .mapped('move_line_ids')
                    # As we defer the write on the stock.move's state at the end of the loop, there
                    # could be moves to consider in what our siblings already took.
                    moves_out_siblings = move.move_orig_ids.mapped('move_dest_ids') - move
                    moves_out_siblings_to_consider = moves_out_siblings & (assigned_moves + partially_available_moves)
                    reserved_moves_out_siblings = moves_out_siblings.filtered(lambda m: m.state in ['partially_available', 'assigned'])
                    move_lines_out_reserved = (reserved_moves_out_siblings | moves_out_siblings_to_consider).mapped('move_line_ids')
                    keys_out_groupby = ['location_id', 'lot_id', 'package_id', 'owner_id']

                    def _keys_out_sorted(ml):
                        return (ml.location_id.id, ml.lot_id.id, ml.package_id.id, ml.owner_id.id)

                    grouped_move_lines_out = {}
                    for k, g in groupby(sorted(move_lines_out_done, key=_keys_out_sorted), key=itemgetter(*keys_out_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_out[k] = qty_done
                    for k, g in groupby(sorted(move_lines_out_reserved, key=_keys_out_sorted), key=itemgetter(*keys_out_groupby)):
                        grouped_move_lines_out[k] = sum(self.env['stock.move.line'].concat(*list(g)).mapped('product_qty'))
                    available_move_lines = {key: grouped_move_lines_in[key] - grouped_move_lines_out.get(key, 0) for key in grouped_move_lines_in.keys()}
                    # pop key if the quantity available amount to 0
                    available_move_lines = dict((k, v) for k, v in available_move_lines.items() if v)

                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(lambda m: m.product_qty):
                        if available_move_lines.get((move_line.location_id, move_line.lot_id, move_line.result_package_id, move_line.owner_id)):
                            available_move_lines[(move_line.location_id, move_line.lot_id, move_line.result_package_id, move_line.owner_id)] -= move_line.product_qty
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        need = move.product_qty - sum(move.move_line_ids.mapped('product_qty'))
                        taken_quantity = move._update_reserved_quantity(need, quantity, location_id, lot_id, package_id, owner_id)
                        if float_is_zero(taken_quantity, precision_rounding=move.product_id.uom_id.rounding):
                            continue
                        if need - taken_quantity == 0.0:
                            assigned_moves |= move
                            break
                        partially_available_moves |= move
        partially_available_moves.write({'state': 'partially_available'})
        assigned_moves.write({'state': 'assigned'})
        self.mapped('picking_id')._check_entire_pack()
   
    

