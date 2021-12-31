# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################
from odoo import models, fields, _


class ResPartnerBank_Inherit(models.Model):
    _inherit = ["res.partner.bank"]


class ResPartnerBank_Inherit(models.Model):
    _inherit = ["res.partner.bank"]

    businnes_line_id = fields.Many2one("business.line", string=u"Linea de Negocio")
    sale_channel_id = fields.Many2one(
        "business.channel",
        string=u"Canal de venta",
        domain=[("channel_type", "=", "ve")],
    )
