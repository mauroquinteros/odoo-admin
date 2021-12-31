# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.base_company.models.utils import (
    values as val,
    functions as bcompay_methods,
)


class Profile_Operator(models.Model):
    _name = "profile.config"
    _description = "Lista de Perfiles de Operaciones"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string=u"Nombre", required=True)
    module = fields.Char(string=u"Prefijo", required=True)
    module_type = fields.Char(string=u"Abreviado", required=True)
    type_pt_use = fields.Selection(
        string=u"Tipo de Uso", selection=val.s_type, required=True
    )
    foreign_code = fields.Char(string=u"Código Foráneo", required=True)
    company_id = fields.Many2one(
        "res.company",
        string=u"Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    active = fields.Boolean(string=u"active", default=True)

    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id, ("(%s) - %s") % (record.module_type, record.name))
            )
        return result

    def action_open_document(self):
        view = bcompay_methods.open_current(
            self, "base_company.profile_config_view_form"
        )
        return view


class Profile_AccountBank_Inherit(models.Model):
    _inherit = ["res.partner.bank.profile"]

    def action_open_document(self):
        view = bcompay_methods.open_current(
            self, "base_company.profile_account_bank_view_form"
        )
        return view
