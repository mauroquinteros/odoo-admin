# -*- coding: utf-8 -*-
# from odoo import http


# class SaleRemittanceSending(http.Controller):
#     @http.route('/sale_remittance_sending/sale_remittance_sending/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_remittance_sending/sale_remittance_sending/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_remittance_sending.listing', {
#             'root': '/sale_remittance_sending/sale_remittance_sending',
#             'objects': http.request.env['sale_remittance_sending.sale_remittance_sending'].search([]),
#         })

#     @http.route('/sale_remittance_sending/sale_remittance_sending/objects/<model("sale_remittance_sending.sale_remittance_sending"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_remittance_sending.object', {
#             'object': obj
#         })
