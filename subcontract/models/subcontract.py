# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#Today changes 14/03/2019


from odoo import fields, models, api, _
from odoo.exceptions import UserError
import itertools
from operator import itemgetter
import datetime
from odoo.exceptions import ValidationError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    @api.multi
    def open_produce_product(self):
        res = super(MrpProduction, self).open_produce_product()        
        return res       

    @api.multi
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        if self.purchase_ids:
            for po in self.purchase_ids:
                for mo in self.finished_move_line_ids:
                    for po_line in po.order_line:
                        if not po_line.qty_received == mo.qty_done and not self.env.user.has_group('mrp.group_mrp_manager'):
                            raise UserError(_('Quantity to produce and Produced Qty Should be same for validation by user.'))
        return res

    @api.multi
    def action_purchase_view(self):
        action = self.env.ref('purchase.purchase_rfq')
        result = action.read()[0]
        result['domain'] = "[('id', 'in', " + str(self.purchase_ids.ids) + ")]"
        return result

    @api.onchange('vendor')
    def onchange_picking_type(self):
        if self.subcontract_prod:
            location = self.env.ref('stock.stock_location_stock')
            self.location_src_id = self.picking_type_id.default_location_src_id.id or location.id
            self.location_dest_id = self.vendor.property_stock_supplier.id

    @api.depends('purchase_ids')
    def _purchase_count(self):
        for order in self:
            order.purchase_count = len(order.purchase_ids)

    purchase_count = fields.Integer(compute='_purchase_count', string='# Purchases')
    purchase_ids = fields.One2many('purchase.order', 'mrp_id', string='Pickings')

    # Update : find vendor witch property_stock_supplier is Subcontract location 
    @api.multi
    def _compute_subcontractvendor(self):        
        con=[]
        res_partner_obj = self.env['res.partner']
        ids=res_partner_obj.search([('property_stock_supplier.id','=',18)])      #22 Subcontract location 
        for i in ids:
            con.append(i.id)       
        return [('id','in',con)]

    vendor = fields.Many2one('res.partner', string="Vendor",domain=_compute_subcontractvendor,help='Select Subcontract vendor')

    subcontract_prod = fields.Boolean(string="Subcontract")
    # Update : Add subcontract type to send subcontractor
    subcontract_parentchildprod = fields.Selection([
        ('1', 'Component job send'),
        ('2', 'Assembly'),
        ('3', 'Component')], string='Subcontract send')

class Location(models.Model):
    _inherit = "stock.location"

    def should_bypass_reservation(self):
        res = super(Location, self).should_bypass_reservation()
        action = self.usage in ('customer', 'inventory', 'production') or self.scrap_location
        return action


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    
    mrp_id = fields.Many2one('mrp.production', string="Manufacturing Order")

    # Add Field to know which Operation is done on PO report for subcontract
    subcontract_operation= fields.Char(string='Operation in PO')  

    delivery_count = fields.Integer(compute="_compute_dc", string='Delivery Challan', copy=False, default=0, store=True)
    delivery_ids = fields.Many2many('stock.picking', compute="_compute_dc", string='Bills', copy=False, store=True)
    
    # Update : set all Open purchase order 
    @api.onchange('po_categ_id')
    def OpenPOnumber(self):
        con=[]
        domain={}
        po_obj = self.env['purchase.order']
        po_cat = self.env['category.purchase.master']
        pc_data=po_cat.search([('po_category', '=', 'OP')])  
        po_ids=po_obj.search([('po_categ_id','=',pc_data.id)])  
        for i in po_ids:
            con.append(i.id)             
        domain['openpo_id']=[('id','in',con)]
        return {'domain':domain}


    openpo_id = fields.Many2one('purchase.order',string='Open PO Number',change_default=True,help='Only Confirm state PO are available')

    # update : Set price from Open purchase order 
    @api.onchange('openpo_id')
    def updateunitprice(self):
        id=0
        for i in self.openpo_id.order_line:
            for l in self.order_line:
                if i.product_id==l.product_id:
                    l.price_unit = i.price_unit
                    id+=1                

                if id==0:
                    l.price_unit = 0

    @api.multi
    def _compute_dc(self):
        for order in self:
            stock_picking_obj = self.env['stock.picking']
            poid = stock_picking_obj.search([('po_number','=',order.id)])    
            order.delivery_ids = poid       
            order.delivery_count = len(poid)

    @api.multi
    def action_deliveryorder_view(self):
        '''
        This function returns an action that display existing Delivery Challan of given subcontract purchase order ids.
        When only one found, show the Delivery Challan immediately.
        '''
        action = self.env.ref('subcontract.action_delivery_order_subcontract')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {'state': 'draft', 'default_po_number': self.id,'default_partner_id': self.partner_id.id}
        return result

class Picking(models.Model):
    _inherit = 'stock.picking'

    subcontract = fields.Boolean(string="Subcontract", help="If subcontract Delivery Challan is there check it")        
    flag = fields.Boolean(string="Flag", default=False)

    # Add this function to set location on subcontract selection
    @api.onchange('subcontract')
    def onchange_picking_type(self):     
       
            if self.subcontract:
                if self.partner_id:                    
                    self.location_id =  self.po_number.mrp_id.location_src_id.id or 15      # WH/Stock location
                    self.location_dest_id = self.partner_id.property_stock_supplier.id      # Subcontract location
                    self.picking_type_id = self.env['stock.picking.type'].search([('code','=','outgoing')]).id 
                else:
                    raise UserError(_('Select partner'))
            else:
                print('in',self.subcontract)
                if self.picking_type_id:
                    if self.picking_type_id.default_location_src_id:
                        location_id = self.picking_type_id.default_location_src_id.id
                    elif self.partner_id:
                        location_id = self.partner_id.property_stock_supplier.id
                    else:
                        customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

                    if self.picking_type_id.default_location_dest_id:
                        location_dest_id = self.picking_type_id.default_location_dest_id.id
                    elif self.partner_id:
                        location_dest_id = self.partner_id.property_stock_customer.id
                    else:
                        location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

                    self.location_id = location_id                                                      # WH/Output location
                    self.location_dest_id = location_dest_id                                            # Customer location
        
    # Add computed field for selecting as-per screen
    @api.multi
    def _compute_DCnumber(self):
        con=[]
        stock_picking_obj = self.env['stock.picking']
        con_ids=stock_picking_obj.search([('subcontract','=',True),('state','!=','done')])
        for i in con_ids:
            con.append(i.id)       
        return [('id','in',con)]


    @api.multi
    def _compute_POnumber(self):
        con=[]
        purchase_order_obj = self.env['purchase.order']
        po_ids=purchase_order_obj.search([('mrp_id','!=',None),('state','=','purchase')])
        for i in po_ids:
            con.append(i.id)       
        return [('id','in',con)]
    
    # Add field to show DC number on PO GRN
    dc_number  = fields.Many2one('stock.picking',string='DC Number',domain=_compute_DCnumber,help='DC come only state is not done and subcontract')
    
    # Add field to show PO number on DC creation
    po_number = fields.Many2one('purchase.order',string='PO Number',domain=_compute_POnumber,help='Only Confirm state PO are available')
    
    # This function return operation for subcontract on DC report
    @api.multi
    def set_operation(self,mo): 
        if mo:                
            op_ary =[]            
            mrp_workorder_obj = self.env['mrp.workorder']             
            mrp_work_data = mrp_workorder_obj.search([('production_id','=',mo.id),('subcontract_operation','=','t')])
            i=1
            strg =''
            for item in mrp_work_data:
                strg = str(i) +" - "+ item.name
                op_ary.append(strg)
                i+=1
            
            op_name = ", ".join(str(s) for s in op_ary)
            print('op_name',op_name)                
            return op_name
    
    @api.model
    def create(self, vals):
        # Update : subcontract GRN sequence generate on GRN validation, for that code comment 
        
        # TDE FIXME: clean that brol
        # name =''
        # pdata = self.env['purchase.order']
        # if vals['origin']:                
        #     podata = pdata.search([('name','=',vals['origin'])])   
        # name = vals['origin']
        
        # if not podata.mrp_id:
        #     defaults = self.default_get(['name', 'picking_type_id'])
        #     if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
        #         vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
        # else:            
        #     vals['name'] = self.env['ir.sequence'].next_by_code('grn.sub.seq') or '/'

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
        self.mrp_validation()        
        # if self.picking_type_code in ('outgoing', 'internal'):
        #     for ml in self.move_lines:
        #         sq = self.env['stock.quant'].search([('product_id', '=', ml.product_id.id), ('location_id', '=', self.location_id.id)])
        #         print('sq',sq,ml.product_id.id,self.location_id.id)
        #         if sq.id == False:
        #             raise UserError(_('There is no stock available for the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) in the stock location. Kindly add the required stock.'))
        #         else:
        #             for i in sq:                        
        #                 if ml.quantity_done > i.quantity:
        #                     raise UserError(_('You cannot validate this stock operation because the stock level of the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) would become negative on the stock location and negative stock is not allowed for this product.'))
        res = super(Picking, self).button_validate()
        return res
 
    @api.multi
    def mrp_validation(self):
        total_qty = 0 
        if self.purchase_id.mrp_id.product_id:
            for line in self.move_lines:
                if line.product_id == self.purchase_id.mrp_id.product_id:                    
                    if self.purchase_id.mrp_id.finished_move_line_ids: 
                        for mrp in self.purchase_id.mrp_id.finished_move_line_ids:
                            mrp.write({'done_move': 't','qty_done':self.purchase_id.mrp_id.product_qty}) 
                            if mrp.done_move:
                                total_qty += mrp.qty_done                                
                        
                        if not line.purchase_line_id.qty_received:
                            if line.quantity_done > total_qty:
                                raise UserError(_('Quantity should not be greater than the Processed Mrp Qty. (or) There is no or less Processed Qty in Stock Move.'))
                        else:
                            curr_qty_done = line.purchase_line_id.qty_received + line.quantity_done
                            if curr_qty_done > total_qty:
                                raise UserError(_('Quantity should not be greater than the processed Mrp Qty .Few of the quantities may be Received'))
                        if self.purchase_id.mrp_id.product_qty == total_qty:                           
                            self.DC_close()    # Close DC of subcontract
                            
                            # self.purchase_id.mrp_id.button_mark_done()  #call mrp button_mark_done function when PO receive done
                            
                    else:
                        raise UserError(_('Kindly Process the respective MRP / Work Order for Qty.'))

            self.DC_close()    
        return True

    # Update : Restrict, quantity_done not more then initial_qty
    @api.onchange('move_lines.product_id')
    def qty_done_restrict(self):
        self.move_lines.product_uom_qty
        self.move_lines.quantity_done
        if self.move_lines.product_uom_qty < self.move_lines.quantity_done:
            raise UserError(_('Can not enter more then initial quantity'))

    # This function is close the DC as per the Product and Product Qty on subcontract category 
    @api.multi
    def DC_close(self):
        print('------',self.dc_number)
        mrp_workorder_obj = self.env['mrp.workorder'] 
        wo_data = {}
        workorder_pdir_generate_obj = self.env['workorder.pdir.generate']
        if self.dc_number:      
            data = self.env['mrp.product.produce'].search([('production_id','=',self.purchase_id.mrp_id.id)])
            mrp_work_data = mrp_workorder_obj.search([('production_id','=',self.purchase_id.mrp_id.id),('subcontract_operation','=','t'),('state','!=','done')])
            if self.purchase_id.mrp_id.subcontract_parentchildprod =='1': 
                done_qty=0
                initial_qty=0
                for line in self.move_line_ids:
                    done_qty +=line.qty_done                    
                initial_qty =self.purchase_id.order_line.product_qty
                if initial_qty == done_qty:                    
                    for woline in mrp_work_data:
                        if not woline.next_work_order_id:    
                            woline.production_id.write({'produced_qty': 0})

                        woline.write({'state': 'done','qty_produced': data[0].product_qty,'qty_producing': 0,'date_start': fields.Datetime.now(),'date_finished': fields.Datetime.now()})
                        
                        if not woline.next_work_order_id:                                
                            wo_data ={'production_id':woline.production_id.id,
                                    'product_id': woline.product_id.id,
                                    'qty_produced':data[0].product_qty, #if line.product_id.description_sale else 'NA',
                                    'workorder_id': woline.id,
                                    }
                            
                            ids = workorder_pdir_generate_obj.create(wo_data)
                    self.dc_number.button_validate()   
            elif self.purchase_id.mrp_id.subcontract_parentchildprod  =='2':
                for dline in self.dc_number.move_lines:
                    for line in self.move_lines:
                        curr_qty_done = line.purchase_line_id.qty_received + line.quantity_done
                        if dline.product_id == line.product_id:
                            if dline.quantity_done == curr_qty_done:
                                for woline in mrp_work_data:
                                    if not woline.next_work_order_id:    
                                        woline.production_id.write({'produced_qty': 0})

                                    woline.write({'state': 'done','qty_produced': data[0].product_qty,'qty_producing': 0,'date_start': fields.Datetime.now(),'date_finished': fields.Datetime.now()})
                                    if not woline.next_work_order_id:                
                                        wo_data ={'production_id':woline.production_id.id,
                                                'product_id': woline.product_id.id,
                                                'qty_produced':data[0].product_qty, #if line.product_id.description_sale else 'NA',
                                                'workorder_id': woline.id,
                                                }
                            
                                        ids = workorder_pdir_generate_obj.create(wo_data)                                       
                                self.dc_number.button_validate()        
            elif self.purchase_id.mrp_id.subcontract_parentchildprod  =='3':
                for dline in self.dc_number.move_lines:
                    for line in self.move_lines:
                        curr_qty_done = line.purchase_line_id.qty_received + line.quantity_done                        
                        if dline.product_id == line.product_id:
                            print('curr_qty_done,dline.product_id',curr_qty_done,dline.product_id)
                            if dline.quantity_done == curr_qty_done:
                                dline.write({'state': 'done', 'is_done':True}) 

                for mrp in self.purchase_id.mrp_id.finished_move_line_ids:
                    mrp.write({'done_move': 't','qty_done':self.purchase_id.mrp_id.product_qty})     

                dcount=0
                mcount=0
                for dline in self.dc_number.move_lines.filtered(lambda x: x.state in ('done')):
                    dcount+=1

                mcount=self.dc_number.move_lines.search_count([('reference','=',self.dc_number.name)])
                print('dcount,mcount',dcount,mcount)
                if dcount == mcount:      
                    for woline in mrp_work_data:
                        if not woline.next_work_order_id:    
                            woline.production_id.write({'produced_qty': 0})
                            self.dc_number.button_validate()
                            
                        woline.write({'state': 'done','qty_produced': data[0].product_qty,'qty_producing': 0,'date_start': fields.Datetime.now(),'date_finished': fields.Datetime.now()})
                        if not woline.next_work_order_id:                
                            wo_data ={'production_id':woline.production_id.id,
                                    'product_id': woline.product_id.id,
                                    'qty_produced':data[0].product_qty, #if line.product_id.description_sale else 'NA',
                                    'workorder_id': woline.id,
                                    }
                            
                            ids = workorder_pdir_generate_obj.create(wo_data)
                    #self.dc_number.button_validate()
        else:
            raise UserError(_('Select DC number'))           
     
    
    # This function is create DC on PO and subcontract category
    @api.multi
    def get_bom_materials(self):
        list_prod = []        
        count=0
        if not self.po_number:
            raise UserError(_('PO number select'))
        if self.po_number:  
            self.location_id =  self.po_number.mrp_id.location_src_id.id             
            self.origin =  self.po_number.name
            create_vals = {}
            if self.po_number.mrp_id.subcontract_parentchildprod =='1':
                for line_id in self.po_number.mrp_id.move_raw_ids:                    
                    create_vals = {
                        'name': line_id.product_id.name,
                        'product_id': line_id.product_id.id,
                        'product_uom': line_id.product_uom.id,
                        'product_uom_qty': line_id.product_qty,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'picking_id': self.id,
                    }
                    list_prod.append(create_vals)
            elif self.po_number.mrp_id.subcontract_parentchildprod in ('2','3') :
                for line_id in self.po_number.order_line:
                    create_vals = {
                        'name': line_id.product_id.name,
                        'product_id': line_id.product_id.id,
                        'product_uom': line_id.product_uom.id,
                        'product_uom_qty': line_id.product_qty,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'picking_id': self.id,
                    }
                    list_prod.append(create_vals)

        list_prod.sort(key=itemgetter('product_id'))
        move_temp = []
        for key, items in itertools.groupby(list_prod, key=itemgetter('product_id', 'name', 'product_uom', 'location_id', 'location_dest_id')):
            move_temp.append({
                'product_id': key[0],
                'name': key[1],
                'product_uom': key[2],
                'location_id': key[3],
                'location_dest_id': key[4],
                'product_uom_qty': sum([item["product_uom_qty"] for item in items])
            })
        print('move_temp',move_temp)
        for new_line in move_temp:
            move_id = self.env['stock.move'].create(new_line)
            move_id.update({'picking_id': self.id})
        self.flag = True
        #count = self.search_count([('po_number','=',self.po_number.id)])
        # self.po_number.delivery_count = count
        #self.po_number.write({'delivery_count': count}) 
        return True


# class BomMaterials(models.Model):
#     _name = 'bom.materials'

#     picking_id = fields.Many2one('stock.picking', string="Picking")
#     product_id = fields.Many2one('mrp.bom', string="BoM Product")
#     produce_qty = fields.Float(string="Quantity")

# create_by | create_date | update_by | update_date
# Ganesh      24/12/2018 

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    #Add field for check which operation send for subcontract
    subcontract_operation=fields.Boolean('Operation send for Subcontract',default=False)

    # Delete operation on mrp subcontract
    @api.multi
    def delete(self):
        print('delete ---------',self.id)
        super(MrpWorkorder, self).unlink()
        return { "type": "ir.actions.do_nothing", }
        


        
