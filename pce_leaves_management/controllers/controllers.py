# -*- coding: utf-8 -*-
from odoo import http

# class PceLeavesManagement(http.Controller):
#     @http.route('/pce_leaves_management/pce_leaves_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pce_leaves_management/pce_leaves_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pce_leaves_management.listing', {
#             'root': '/pce_leaves_management/pce_leaves_management',
#             'objects': http.request.env['pce_leaves_management.pce_leaves_management'].search([]),
#         })

#     @http.route('/pce_leaves_management/pce_leaves_management/objects/<model("pce_leaves_management.pce_leaves_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pce_leaves_management.object', {
#             'object': obj
#         })