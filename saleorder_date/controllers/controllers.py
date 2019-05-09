# -*- coding: utf-8 -*-
from odoo import http

# class SaleorderDate(http.Controller):
#     @http.route('/saleorder_date/saleorder_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/saleorder_date/saleorder_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('saleorder_date.listing', {
#             'root': '/saleorder_date/saleorder_date',
#             'objects': http.request.env['saleorder_date.saleorder_date'].search([]),
#         })

#     @http.route('/saleorder_date/saleorder_date/objects/<model("saleorder_date.saleorder_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('saleorder_date.object', {
#             'object': obj
#         })