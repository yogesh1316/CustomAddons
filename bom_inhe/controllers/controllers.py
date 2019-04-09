# -*- coding: utf-8 -*-
from odoo import http

# class BomInhe(http.Controller):
#     @http.route('/bom_inhe/bom_inhe/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bom_inhe/bom_inhe/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bom_inhe.listing', {
#             'root': '/bom_inhe/bom_inhe',
#             'objects': http.request.env['bom_inhe.bom_inhe'].search([]),
#         })

#     @http.route('/bom_inhe/bom_inhe/objects/<model("bom_inhe.bom_inhe"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bom_inhe.object', {
#             'object': obj
#         })