# -*- coding: utf-8 -*-
# from odoo import http


# class BaseConfig(http.Controller):
#     @http.route('/base_config/base_config/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_config/base_config/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_config.listing', {
#             'root': '/base_config/base_config',
#             'objects': http.request.env['base_config.base_config'].search([]),
#         })

#     @http.route('/base_config/base_config/objects/<model("base_config.base_config"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_config.object', {
#             'object': obj
#         })
