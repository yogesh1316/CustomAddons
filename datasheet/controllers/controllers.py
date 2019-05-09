# -*- coding: utf-8 -*-
from odoo import http

# class Datasheet(http.Controller):
#     @http.route('/datasheet/datasheet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/datasheet/datasheet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('datasheet.listing', {
#             'root': '/datasheet/datasheet',
#             'objects': http.request.env['datasheet.datasheet'].search([]),
#         })

#     @http.route('/datasheet/datasheet/objects/<model("datasheet.datasheet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('datasheet.object', {
#             'object': obj
#         })