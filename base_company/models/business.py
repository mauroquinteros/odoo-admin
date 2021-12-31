# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

from odoo.addons.base_company.models.utils import (
    values as val,
    functions as bcompay_methods,
)


class BusinessLine(models.Model):
    _name = "business.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Lineas de Negocio de la Empresa"
    _rec_name = "name"
    _order = "id ASC"

    name = fields.Char(
        string=u"Nombre", required=True, help="Nombre de la Linea de Negocio"
    )
    foreign_code = fields.Char(string=u"Código Foráneo", required=True)
    active = fields.Boolean(string=u"active", default=True)

    def action_open_document(self):
        view = bcompay_methods.open_current(
            self, "base_company.business_line_view_form"
        )
        return view


class Channel(models.Model):
    _name = "business.channel"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Canales de Venta /Pago/ Entrega"
    _rec_name = "name"
    _order = "id ASC"

    name = fields.Char(string=u"Nombre Canal", required=True)
    name_code = fields.Char(string=u"Nombre Global")
    channel_type = fields.Selection(string=u"Tipo de Canal", selection=val.channel_type)
    foreign_code = fields.Char(string=u"Código Foráneo", size=10)
    plaftrisk_id = fields.Many2one("plaft.risk", string=u"Riesgo LA/FT")
    company_id = fields.Many2one(
        "res.company",
        string=u"Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    active = fields.Boolean(string=u"active", default=True)

    def action_open_document(self):
        view = bcompay_methods.open_current(
            self, "base_company.business_channel_view_form"
        )
        return view


class Event(models.Model):
    _name = "business.event"
    _description = "Registro de Eventos"
    _rec_name = "name"
    _order = "id ASC"

    name = fields.Char(
        string=u"Nombre", help="Nombre del canal de venta", required=True
    )
    foreign_code = fields.Char(
        string=u"Código de la empresa",
        required=True,
        help="Es el código propio de la empresa asignado al canal",
    )
    company_id = fields.Many2one(
        "res.company",
        string=u"company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    active = fields.Boolean(string=u"active", default=True)

    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id, ("%s %s") % (record.c_reference_code, record.name))
            )
        return result
