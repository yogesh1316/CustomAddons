# -*- coding: utf-8 -*-
from odoo import http

# class SaleReport(http.Controller):
#     @http.route('/sale_report/sale_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_report/sale_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_report.listing', {
#             'root': '/sale_report/sale_report',
#             'objects': http.request.env['sale_report.sale_report'].search([]),
#         })

#     @http.route('/sale_report/sale_report/objects/<model("sale_report.sale_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_report.object', {
#             'object': obj
#         })