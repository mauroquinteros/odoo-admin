# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

from odoo.addons.l10n_pe_currency.models.utils import values as curval
from odoo.addons.base_company.models.utils import values as val
from odoo.osv import expression
from datetime import datetime


class ResPartnerAgency(models.Model):
    _name = "res.partner.agency"
    _description = "Tabla de Agencias"
    _inherits = {"res.partner": "partner_id"}

    """
    Desarrollador: Mauro Quinteros
    Cambios: Definir el modelo de res.partner.agency
    """
    partner_id = fields.Many2one(
        "res.partner", string="partner_id", required=True, ondelete="cascade"
    )
    internal_code = fields.Char(string="Código de agencia", required=True)
    country_internal_code = fields.Char(
        string="Código de envío", compute="_get_country_internal_code", store=True
    )
    correspondent_id = fields.Many2one(
        "res.partner.correspondent",
        string="Corresponsal",
        required=True,
        domain="[('state', '=', 'activo')]",
    )
    country_id = fields.Many2one("res.country", string="País", required=True)
    state_id = fields.Many2one(
        "res.country.state",
        string="Estado",
        domain="[('country_id', '=?', country_id)]",
    )

    reference_payer = fields.Char(string="Pagador")
    code_reference = fields.Char(string="Código referencia")
    office_hour = fields.Char(string="Horario de atención")
    accept_local_currency = fields.Boolean(string="Moneda Local", default=True)

    state = fields.Selection(
        string="Estado",
        default="activo",
        selection=val.state_use,
        track_visibility="on_change",
    )
    send_currency_ids = fields.Many2many(
        string="Monedas aceptadas",
        comodel_name="res.currency",
        relation="send_currencies_agency_rel",
        column1="agency_id",
        column2="currency_id",
        domain=[("name", "in", curval.principals)],
    )
    pay_currency_ids = fields.Many2many(
        string="Monedas de pago",
        comodel_name="res.currency",
        relation="pay_currencies_agency_rel",
        column1="agency_id",
        column2="currency_id",
    )
    pos_ids = fields.One2many(
        string="Puntos de Venta", comodel_name="pos.config", inverse_name="agency_id"
    )
    previous_correspondent_name = fields.Char(
        string="Nombre previo del corresponsal")

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar funciones para buscar por el código o el nombre de una Agencia
    """
    @api.depends("name", "internal_code")
    def name_get(self):
        result = []
        for record in self:
            internal_code = f"{record.internal_code} - " or ""
            name = record.name or ""
            display_name = internal_code + name
            result.append((record.id, display_name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('internal_code', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        ids = self._name_search(name, args, operator, limit=limit)
        return self.browse(ids).sudo().name_get()

    @api.onchange("correspondent_id")
    def _onchange_correspondent_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para actualizar el pagador referencial
        """
        if self.correspondent_id.id is not False:
            if self.reference_payer is False or self.reference_payer is "":
                self.reference_payer = self.correspondent_id.name
                self.previous_correspondent_name = self.correspondent_id.name
            else:
                if self.reference_payer == self.previous_correspondent_name:
                    self.reference_payer = self.correspondent_id.name
                    self.previous_correspondent_name = self.correspondent_id.name

    @api.onchange("accept_local_currency", "country_id")
    def _onchange_accept_local_currency(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para validar que las monedas aceptadas puedan tener la moneda local o no
        """
        currencies_name = []
        currencies_name.extend(curval.principal_currencies)
        res = {}
        if self.country_id.id is not False:
            currency_id = self.country_id.currency_id.id
            local_currency = self.env["res.currency"].search(
                [("id", "=", currency_id)])

            if self.accept_local_currency is True:
                currencies_name.append(local_currency.name)
                res["domain"] = {
                    "pay_currency_ids": [
                        "&",
                        ("name", "in", currencies_name),
                        ("active", "=", True),
                    ]
                }
            else:
                res["domain"] = {
                    "pay_currency_ids": [
                        "&",
                        ("name", "in", currencies_name),
                        ("active", "=", True),
                    ]
                }
            return res
        else:
            res["domain"] = {
                "pay_currency_ids": [
                    "&",
                    ("name", "in", currencies_name),
                    ("active", "=", True),
                ]
            }
            return res

    @api.depends("country_id", "internal_code")
    def _get_country_internal_code(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para calcular el código interno formado por código del país y código de la agencia
        """
        for record in self:
            country_internal_code = ""
            if record.country_id.id:
                country_internal_code += f"{record.country_id.code_reference}-"
            if record.internal_code:
                country_internal_code += f"{record.internal_code}"
            record.country_internal_code = country_internal_code

    def unlink(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para eliminar y valida si la agencia contiene puntos de ventas
        """
        if len(self.pos_ids) > 0:
            raise exceptions.UserError(
                (
                    "⚠️ No puede Borrar Esta Agencia por que tiene Punto de Ventas Asociados"
                )
            )
        else:
            super(ResPartnerAgency, self).unlink()
