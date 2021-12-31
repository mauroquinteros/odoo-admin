# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Profile_AccountBank(models.Model):
    _name = "res.partner.bank.profile"
    _description = "Lista de funciones que tiene una cuenta bancaria"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    value = fields.Char(string=u"Valor")
    name = fields.Char(string=u"Nombre")
    type = fields.Selection(
        string="Tipo", selection=[("operative", "Operativo"), ("personal", "Personal")]
    )
    foreign_code = fields.Char(string=u"Código Foráneo")
    description = fields.Char(string=u"Descripción")
    company_id = fields.Many2one(
        "res.company",
        string=u"Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    active = fields.Boolean(string=u"active", default=True)
