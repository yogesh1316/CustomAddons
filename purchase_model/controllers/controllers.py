# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseModel(http.Controller):
#     @http.route('/purchase_model/purchase_model/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_model/purchase_model/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_model.listing', {
#             'root': '/purchase_model/purchase_model',
#             'objects': http.request.env['purchase_model.purchase_model'].search([]),
#         })

#     @http.route('/purchase_model/purchase_model/objects/<model("purchase_model.purchase_model"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_model.object', {
#             'object': obj
#         })