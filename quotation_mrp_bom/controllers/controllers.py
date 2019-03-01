# -*- coding: utf-8 -*-
from odoo import http

# class QutationMrpBom(http.Controller):
#     @http.route('/qutation_mrp_bom/qutation_mrp_bom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/qutation_mrp_bom/qutation_mrp_bom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('qutation_mrp_bom.listing', {
#             'root': '/qutation_mrp_bom/qutation_mrp_bom',
#             'objects': http.request.env['qutation_mrp_bom.qutation_mrp_bom'].search([]),
#         })

#     @http.route('/qutation_mrp_bom/qutation_mrp_bom/objects/<model("qutation_mrp_bom.qutation_mrp_bom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('qutation_mrp_bom.object', {
#             'object': obj
#         })