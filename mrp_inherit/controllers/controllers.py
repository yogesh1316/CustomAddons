# -*- coding: utf-8 -*-
from odoo import http

# class MrpInherit(http.Controller):
#     @http.route('/mrp_inherit/mrp_inherit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_inherit/mrp_inherit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_inherit.listing', {
#             'root': '/mrp_inherit/mrp_inherit',
#             'objects': http.request.env['mrp_inherit.mrp_inherit'].search([]),
#         })

#     @http.route('/mrp_inherit/mrp_inherit/objects/<model("mrp_inherit.mrp_inherit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_inherit.object', {
#             'object': obj
#         })