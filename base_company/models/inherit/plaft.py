# -*- coding: utf-8 -*-
import base64
import calendar
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, AccessError, ValidationError

class ControlThreshold_Inherit(models.Model):
    _inherit = ['plaft.control.threshold']

    business_line_id = fields.Many2one('business.line', 'Linea de Negocio')

    @api.onchange('destination_country_id')
    def _partner_domain(self):
        if(self.business_line_id.name == 'Transferencia de Fondos'):
            objagency = self.env['res.partner.agency'].search([('country_id','=',self.destination_country_id.id)])
            partnerList = []
            for item in objagency:
                if(item.correspondent_id.partner_id.id not in partnerList):
                    partnerList.append(item.correspondent_id.partner_id.id)
            return {'domain' : {'destination_partner_id' : [('id','in',partnerList)]}}

class CommercialThreshold_Inherit(models.Model):
    _inherit = ['plaft.commercial.threshold']

    business_line_id = fields.Many2one('business.line', 'Linea de Negocio')
    sale_channel_id = fields.Many2one('business.channel', 'Canal de Venta',domain=[('channel_type','ilike','ve')])

class Declaration_RO_Inherit(models.Model):
    _inherit = ['plaft.ro.declaration']

    business_line_id = fields.Many2one('business.line',string=u'Linea de Negocio',default=lambda self: self._context.get('businessline',False))
    payment_channel_id = fields.Many2one('business.channel',string=u'Canal de Pago',default=lambda self: self._context.get('channel',False))