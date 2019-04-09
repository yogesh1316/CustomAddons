# -*- coding: utf-8 -*-
from odoo import http

# class DeliveryPacking(http.Controller):
#     @http.route('/delivery_packing/delivery_packing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/delivery_packing/delivery_packing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('delivery_packing.listing', {
#             'root': '/delivery_packing/delivery_packing',
#             'objects': http.request.env['delivery_packing.delivery_packing'].search([]),
#         })

#     @http.route('/delivery_packing/delivery_packing/objects/<model("delivery_packing.delivery_packing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('delivery_packing.object', {
#             'object': obj
#         })