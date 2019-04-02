# -*- coding: utf-8 -*-
from odoo import http

# class BomStatus(http.Controller):
#     @http.route('/bom_status/bom_status/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bom_status/bom_status/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bom_status.listing', {
#             'root': '/bom_status/bom_status',
#             'objects': http.request.env['bom_status.bom_status'].search([]),
#         })

#     @http.route('/bom_status/bom_status/objects/<model("bom_status.bom_status"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bom_status.object', {
#             'object': obj
#         })