# -*- coding: utf-8 -*-
from odoo import http

# class ImportPurchaseReport(http.Controller):
#     @http.route('/import_purchase_report/import_purchase_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_purchase_report/import_purchase_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_purchase_report.listing', {
#             'root': '/import_purchase_report/import_purchase_report',
#             'objects': http.request.env['import_purchase_report.import_purchase_report'].search([]),
#         })

#     @http.route('/import_purchase_report/import_purchase_report/objects/<model("import_purchase_report.import_purchase_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_purchase_report.object', {
#             'object': obj
#         })