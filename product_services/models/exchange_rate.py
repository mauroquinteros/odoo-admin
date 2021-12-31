# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

from odoo.addons.l10n_pe_currency.models.utils import values as curval
from odoo.addons.base_company.models.utils.functions import transform_internal_code
from datetime import datetime


class ExchangeRateDetail(models.Model):
    _name = "remittance.exchange.rate"
    _description = "Tipo de Cambio de Remesas"
    _rec_name = "internal_code"
    _order = "currenly_active DESC"

    """
    Desarrollador: Mauro Quinteros
    Cambios: Crear el modelo para el manejo de los tipos de cambios entre Jet Peru y sus corresponsales según la moneda de origen y moneda de destino
    """
    internal_code = fields.Char(string="Código")
    country_id = fields.Many2one(comodel_name="res.country", string="País")
    correspondent_id = fields.Many2one(
        comodel_name="res.partner.correspondent",
        string="Corresponsal",
        domain="[('country_id', '=?', country_id)]",
    )
    agency_id = fields.Many2one(
        comodel_name="res.partner.agency",
        string="Agencia",
        domain="[('correspondent_id', '=', correspondent_id)]",
    )
    register_date = fields.Date(string="Fecha de registro", default=fields.Datetime.now)

    origin_currency_id = fields.Many2one(
        "res.currency",
        string="Moneda Origen",
        default=lambda self: self.env["res.currency"].search([("name", "=", "USD")]),
        domain=curval.domain,
    )
    destination_currency_id = fields.Many2one(
        "res.currency",
        string="Moneda Destino",
        default=lambda self: self._get_default_destination_currency(),
    )
    exchange_rate_value = fields.Float(string="Tipo de Cambio", digits=(9, 4))

    currenly_active = fields.Boolean("Activo", default=True)

    def _get_default_destination_currency(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para obtener la moneda local del país por defecto
        """
        if self.country_id.id is not False:
            currency_id = self.country_id.currency_id.id
            default_currency = self.env["res.currency"].search(
                [("id", "=", currency_id)]
            )
            return default_currency
        else:
            return self.env["res.currency"].search([("name", "=", "USD")])

    @api.onchange("country_id")
    def _onchange_correspondent_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para actualizar la moneda local del país
        """
        if self.country_id.id is not False:
            currency_id = self.country_id.currency_id.id
            currency_by_correspondent = self.env["res.currency"].search(
                [("id", "=", currency_id)]
            )
            self.destination_currency_id = currency_by_correspondent

    @api.model
    def create(self, values):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para agregar un código interno según el corresponsal al que pertenece el tipo de cambio
        """
        correspondent_id = values["correspondent_id"]
        code_correspondent = self.env["res.partner.correspondent"].search(
            [("id", "=", correspondent_id)]
        )
        len_exchange_rate = self.env["remittance.exchange.rate"].search_count(
            [("correspondent_id", "=", correspondent_id)]
        )
        id_exchange_rate = transform_internal_code(str(len_exchange_rate + 1))

        values[
            "internal_code"
        ] = f"TC{id_exchange_rate}-{code_correspondent.internal_code}"
        result = super(ExchangeRateDetail, self).create(values)
        return result
