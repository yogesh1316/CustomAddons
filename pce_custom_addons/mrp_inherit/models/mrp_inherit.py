# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class mrp_inherit(models.Model):
    _inherit="mrp.bom"
    revise_checkbox=fields.Boolean('Revise Order')
    mrp_line=fields.One2many("mrp.bom.revise",'mrp_bomrev_id')
    name_revise=fields.Char("name",readonly=True, store=True)
    count_revise=fields.Integer("Revise Count")

    @api.multi
    def write(self,vals):
        print("vals",vals)
        if "revise_checkbox" in vals:
            if vals["revise_checkbox"]==True:  
                print("I m in .........")
            self.create_revision()
            self.count_revise=self.count_revise + 1
            self.name_revise="REV-" + (str(self.count_revise))
            vals["revise_checkbox"]=False
        variable=super(mrp_inherit,self).write(vals)
        return variable

    @api.multi
    def create_revision(self):
        bom_revise_vals={
            'name_revise':self.name_revise,
            'mrp_bomrev_id':self.id,
            'code':self.code,
            'active':self.active,
            'type':self.type,
            'product_tmpl_id':self.product_tmpl_id.id,
            'product_qty':self. product_qty,
            'product_uom_id':self.product_uom_id.id,
            'sequence':self.sequence,
            'ready_to_produce':self.ready_to_produce,
            'picking_type_id':self. picking_type_id.id,
            'company_id':self.company_id.id,
            'routing_id':self.routing_id.id
        }
        mrpbomrevise_obj=self.env['mrp.bom.revise'].create(bom_revise_vals)
        mrpbomrevise_obj.mrp_bomrev_id=self.id
        for bom in self.bom_line_ids:
            bom_line_revise_vals={
                'mrp_bomlinerevise_id':mrpbomrevise_obj.id,
                'product_id':bom.product_id.id,
                'product_qty':bom.product_qty,
                'product_uom_id':bom.product_uom_id.id,
                'sequence':bom.sequence,
                'attribute_value_ids':bom.attribute_value_ids.id
            }
            mrpbomrevise_obj.mrp_bom_line_id=[(0,0,bom_line_revise_vals)]
            mrpbomrevise_obj.mrp_bomrev_id=self.id

class MrpBomRevise(models.Model):
    _name="mrp.bom.revise"
    name_revise=fields.Char("name",readonly=True, store=True)
    mrp_bomrev_id=fields.Many2one("mrp.bom")
    mrp_bom_line_id=fields.One2many("mrp.bom.line.revise",'mrp_bomlinerevise_id')
    code = fields.Char('Reference',store=True)
    active = fields.Boolean('Active', default=True,help="If the active field is set to False, it will allow you to hide the bills of material without removing it.")
    type = fields.Selection([('normal', 'Manufacture this product'),('phantom', 'Kit')], 'BoM Type',default='normal', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product',domain="[('type', 'in', ['product', 'consu'])]", required=True,store=True)
    product_qty = fields.Float('Quantity', default=1.0,required=True)
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure',oldname='product_uom', required=True,help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control",store=True)
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of bills of material.")
    ready_to_produce = fields.Selection([('all_available', 'All components available'),('asap', 'The components of 1st operation')], string='Manufacturing Readiness',default='asap', required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', domain=[('code', '=', 'mrp_operation')],
        help="When a procurement has a ‘produce’ route with a operation type set, it will try to create "
             "a Manufacturing Order for that product using a BoM of the same operation type. That allows "
             "to define procurement rules which trigger different manufacturing orders with different BoMs.")
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get('mrp.bom'),required=True)
    routing_id = fields.Many2one('mrp.routing', 'Routing',help="The operations for producing this BoM.  When a routing is specified, the production orders will "
             " be executed through work orders, otherwise everything is processed in the production order itself.",store=True)
    

    
class MrpBomLineRevise(models.Model):
    _name="mrp.bom.line.revise"
    mrp_bomlinerevise_id=fields.Many2one("mrp.bom.revise")
    product_id = fields.Many2one('product.product', 'Product', required=True,store=True)
    product_qty = fields.Float('Product Quantity', default=1.0,required=True,store=True)
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure',oldname='product_uom', required=True,help="Unit of Measure (Unit of Measure) is the unit",store=True)
    sequence = fields.Integer('Sequence', default=1,help="Gives the sequence order when displaying.")
    attribute_value_ids = fields.Many2many('product.attribute.value', string='Variants',help="BOM Product Variants needed form apply this line.")




    

