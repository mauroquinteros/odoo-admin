# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import models, fields

class AccountPaymentMethodInherit(models.Model):
    _inherit = ['account.payment.method']

    plaftrisk_id = fields.Many2one('plaft.risk', string=u'Riesgo LA/FT', help="Riesgo asignado al factor de riesgo posición")
    business_line_ids = fields.Many2many("business.line", string=u"Lineas de Negocio")
    s_fundtype_code = fields.Selection(string=u"Tipo",selection=[("cash", "Efectivo"), ("other", "Otros")])
    channel_id = fields.Many2one("business.channel", string=u"Canal de Pago")
    description = fields.Char(string='Descripción')
    active = fields.Boolean(string=u"active", default=True)

class ResBank(models.Model):
    _inherit = ['res.bank']

    paymethod_id = fields.Many2one('account.payment.method',string=u'Métodos de Pago',
        domain=[('code','in',[14789,54725,75395])])