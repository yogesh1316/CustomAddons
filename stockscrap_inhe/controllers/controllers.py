# -*- coding: utf-8 -*-
from odoo import http

# class StockscrapInhe(http.Controller):
#     @http.route('/stockscrap_inhe/stockscrap_inhe/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stockscrap_inhe/stockscrap_inhe/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stockscrap_inhe.listing', {
#             'root': '/stockscrap_inhe/stockscrap_inhe',
#             'objects': http.request.env['stockscrap_inhe.stockscrap_inhe'].search([]),
#         })

#     @http.route('/stockscrap_inhe/stockscrap_inhe/objects/<model("stockscrap_inhe.stockscrap_inhe"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stockscrap_inhe.object', {
#             'object': obj
#         })