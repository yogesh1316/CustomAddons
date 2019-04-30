# -*- coding: utf-8 -*-
from odoo import http

# class PceExpenses(http.Controller):
#     @http.route('/pce_expenses/pce_expenses/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pce_expenses/pce_expenses/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pce_expenses.listing', {
#             'root': '/pce_expenses/pce_expenses',
#             'objects': http.request.env['pce_expenses.pce_expenses'].search([]),
#         })

#     @http.route('/pce_expenses/pce_expenses/objects/<model("pce_expenses.pce_expenses"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pce_expenses.object', {
#             'object': obj
#         })