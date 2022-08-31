# -*- coding: utf-8 -*-
# from odoo import http


# class CallingData(http.Controller):
#     @http.route('/calling_data/calling_data', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/calling_data/calling_data/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('calling_data.listing', {
#             'root': '/calling_data/calling_data',
#             'objects': http.request.env['calling_data.calling_data'].search([]),
#         })

#     @http.route('/calling_data/calling_data/objects/<model("calling_data.calling_data"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('calling_data.object', {
#             'object': obj
#         })
