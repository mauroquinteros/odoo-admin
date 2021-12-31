# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import math
import re
import time
import datetime
import requests
import pytz
import locale

from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.tools import (
    DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT,
)

from odoo.addons.l10n_pe_currency.models.utils import values as valcur


class Currency(models.Model):
    _inherit = "res.currency"
    _description = "Currency"

    price_drs = fields.Float(
        compute="_compute_current_rate_pe",
        string="Peruvian format sale",
        digits=(12, 4),
        help="Currency rate sale in peruvian format.",
    )

    price_orp = fields.Float(
        compute="_compute_current_rate_pe",
        string="Peruvian format buy",
        digits=(12, 4),
        help="Currency rate buy in peruvian format.",
    )

    parameter_drs_id = fields.Many2one(
        comodel_name="ir.config_parameter", string="parameter code sale"
    )

    parameter_orp_id = fields.Many2one(
        comodel_name="ir.config_parameter", string="parameter code buy"
    )

    def _get_rates_pe_drs(self, company, date):
        self.env["res.currency.rate"].flush(
            ["price_drs", "currency_id", "company_id", "name"]
        )

        query = """SELECT c.id,
                          COALESCE((SELECT r.price_drs FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS rate_pe
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    def _get_rates_pe_orp(self, company, date):
        self.env["res.currency.rate"].flush(
            ["price_orp", "currency_id", "company_id", "name"]
        )

        query = """SELECT c.id,
                          COALESCE((SELECT r.price_orp FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS rate_pe
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    @api.depends("rate_ids.rate")
    def _compute_current_rate_pe(self):
        date = self._context.get("date") or fields.Date.today()
        company = (
            self.env["res.company"].browse(self._context.get("company_id"))
            or self.env.company
        )
        # the subquery selects the last rate before 'date' for the given currency/company
        for currency in self:
            currency.price_drs = (
                self._get_rates_pe_drs(company, date).get(currency.id) or 1.0
            )
            currency.price_orp = (
                self._get_rates_pe_orp(company, date).get(currency.id) or 1.0
            )

    # TODO: Get currency rate from BCRP
    def get_current_rate_pe(self, date=False, param=False, days=1):
        """
        PEN currency rate from 'Banco Central de Reserva del Peru'
        """
        conf = self.env["ir.config_parameter"].sudo()
        if not date:
            date = fields.Date.today()

        code_ws = conf.get_param(param)
        # The current currency rate from BCRP is always one day before
        """
            Agregar el valor de la fecha anterior y recorrer en un while hasta que lo encuentre y devolver el valor
        """
        date_str = (date - datetime.timedelta(days)).strftime("%Y-%m-%d")
        link = conf.get_param("url.api.sbs.query")
        url = link % (code_ws, date_str, date_str)
        res_drs = requests.get(url)
        res_drs.raise_for_status()
        data = res_drs.json()

        try:
            locale.setlocale(locale.LC_ALL, "en_US")
            rate_name = str(data["config"]["series"][0]["name"])
            date_rate = datetime.datetime.strptime(
                data["periods"][0]["name"], "%d.%b.%y"
            ).strftime(DATE_FORMAT)
            rate_pe = float(data["periods"][0]["values"][0])
            result = {
                "rate_name": rate_name,
                "date_rate": date_rate,
                "rate_pe": rate_pe,
                "url": url,
            }
            return result
        except:
            return False

    def action_query_exchange(self):
        ctx = {}
        if not self.parameter_orp_id or not self.parameter_drs_id:
            self.env.user.notify_warning(
                message="⚠️ No hay relaciones con las llaves de consulta API."
            )
        else:
            rate_orp = self.get_current_rate_pe(
                param=self.parameter_orp_id.key)
            rate_drs = self.get_current_rate_pe(
                param=self.parameter_drs_id.key)
            if rate_orp is not False and rate_drs is not False:
                ctx = {
                    "default_currency_id": self.id,
                    "default_api_date": (
                        datetime.datetime.now() - datetime.timedelta(1)
                    ).strftime(DATE_FORMAT),
                    "default_name_orp": str(rate_orp.get("rate_name")),
                    "default_value_orp": float(rate_orp.get("rate_pe")),
                    "default_period_orp": rate_orp.get("date_rate"),
                    "default_url_orp": str(rate_orp.get("url")),
                    "default_name_drs": str(rate_drs.get("rate_name")),
                    "default_value_drs": float(rate_drs.get("rate_pe")),
                    "default_period_drs": rate_orp.get("date_rate"),
                    "default_url_drs": str(rate_drs.get("url")),
                }
            else:
                ctx = {"default_currency_id": self.id,
                       "default_mode": "manual"}
                self.env.user.notify_danger(
                    message="❌ [API:404] No se está recibiendo la respuesta, revise conexión a internet o verifique las variables de Acceso al consumo de API, por último cambie la fecha de consulta."
                )

        result = {
            "name": "Asistente de Tipo de Cambio SBS",
            "view_id": self.env.ref(
                "l10n_pe_currency.assistant_api_exchange_rate_view_form"
            ).id,
            "view_mode": "form",
            "res_model": "assistant.api_exchange.rate",
            "type": "ir.actions.act_window",
            "context": ctx,
            "target": "new",
        }
        return result

    def process_remittance(self):
        today = datetime.datetime.now(
            pytz.timezone(self.env.user.tz or "America/Lima")
        ).strftime("%Y-%m-%d")
        rates = self.env.ref("base.USD").rate_ids
        for rate in rates:
            rate_orp = self.get_current_rate_pe(
                param=rate.currency_id.parameter_orp_id.key
            )
            rate_drs = self.get_current_rate_pe(
                param=rate.currency_id.parameter_drs_id.key
            )
            if (
                rate.name.strftime("%Y-%m-%d") != today
                and rate_orp
                and rate_drs is not False
            ):
                line = [
                    (
                        0,
                        False,
                        {
                            "name": today,
                            "currency_id": rate.id,
                            "price_drs": float(rate_drs.get("rate_pe")),
                            "price_orp": float(rate_orp.get("rate_pe")),
                        },
                    )
                ]
                rates.rate_ids.create(line)
            else:
                break


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"
    _description = "Currency Rate"

    rate = fields.Float(
        digits=0,
        default=1.0,
        help="The rate of the currency to the currency of rate 1",
        compute="get_rate",
        store=True,
    )

    price_drs = fields.Float(
        string="rate sale",
        digits=(12, 3),
        help="Currency rate sale in peruvian format. Ex: 3.25 when $1 = S/. 3.25",
    )

    price_orp = fields.Float(
        string="rate buy",
        digits=(12, 3),
        help="Currency rate buy in peruvian format. Ex: 3.25 when $1 = S/. 3.25",
    )

    @api.onchange("price_drs")
    def onchange_price_drs(self):
        if self.price_drs > 0:
            self.rate = 1 / self.price_drs
        else:
            raise UserError(_("The amount must be greater than zero"))

    @api.onchange("price_orp")
    def onchange_price_orp(self):
        if self.price_orp > 0:
            self.rate = 1 / self.price_orp
        else:
            raise UserError(_("The amount must be greater than zero"))

    @api.depends("price_drs")
    def get_rate(self):
        for record in self:
            if record.price_drs > 0.0 and type(record.rate) == float:
                record.rate = 1 / record.price_drs

    @api.constrains("price_orp", "price_drs")
    def _check_price_exchange(self):
        for rec in self:
            if rec.price_orp == 0.0 or rec.price_drs == 0.0:
                raise ValidationError(
                    "Debe ingresar los tipos de cambio del dia")

    @api.model
    def create(self, values):
        values["name"] = datetime.datetime.now(
            pytz.timezone(self.env.user.tz or "America/Lima")
        ).strftime("%Y-%m-%d")
        result = super(CurrencyRate, self).create(values)
        return result

    @api.constrains("price_orp", "price_drs")
    def _check_price_exchange(self):
        for rec in self:
            if rec.price_orp == 0.0 or rec.price_drs == 0.0:
                raise ValidationError(
                    "Debe ingresar los tipos de cambio del dia")

    def _define_tc_official(self, origin_currency):
        conditional = [
            "&",
            ("currency_id", "=", origin_currency.id),
            (
                "name",
                "<=",
                datetime.datetime.now(pytz.timezone("America/Lima")).strftime(
                    "%Y-%m-%d"
                ),
            ),
        ]
        tc_official = self.search(conditional, limit=1, order="id desc")
        return tc_official

    def deduct_rule_currency(self, origin_currency, destination_currency):
        calculation = (
            self.sudo()
            .env["res.currency.moex.calculation"]
            .search(
                [
                    "&",
                    ("origin_currency_id.name", "=", origin_currency),
                    ("destination_currency_id.name", "=", destination_currency),
                ]
            )
        )
        return calculation

    def _calculate_itf_with_rate(self, currency, amount):
        amount_percent = self.env.ref("product_services.sale_tax_itf_0050")
        tc_official = self._define_tc_official(currency)
        if amount >= 1000:
            import_exchange = amount * (amount_percent.amount / 100)
            if len(tc_official) == 1 and currency.name != "PEN":
                result = import_exchange * tc_official.price_orp
                return result
            elif currency.name == "PEN":
                result = import_exchange
                return result
            else:
                return "Error, No existe TC Sunat Configurado del día de hoy."
        else:
            return False

    def _calculate_tc_official_special(self, ocur, dcur, oimp):
        tc_official = self._define_tc_official(ocur)
        dictionary = {
            "current_rate": tc_official,
        }
        if dictionary["current_rate"].id is not False:
            objcalc = self.deduct_rule_currency(ocur.name, dcur.name)
            dictionary.update(
                {
                    "tc": dictionary["current_rate"].price_orp
                    if objcalc.s_operationtype == "com"
                    else dictionary["current_rate"].price_drs,
                }
            )
            if ocur.name == "USD":
                dictionary.update(
                    {
                        "amount_equivalent_dol": oimp,
                    }
                )
            elif ocur.name != "USD":
                if ocur.name == "EUR":
                    # to EUR -> PEN
                    eur_to_pen = valcur.ops.get(objcalc.operator)(
                        oimp,
                        dictionary["current_rate"].price_orp
                        if objcalc.s_operationtype == "com"
                        else dictionary["current_rate"].price_drs,
                    )
                    # to PEN -> USD
                    obj = self.deduct_rule_currency("PEN", "USD")
                    ext_rate = self._define_tc_official(
                        self.env.ref("base.USD"))
                    calculate = valcur.ops.get(obj.operator)(
                        eur_to_pen,
                        ext_rate.price_orp
                        if obj.s_operationtype == "com"
                        else ext_rate.price_drs,
                    )
                elif ocur.name == "PEN":
                    # to PEN -> USD
                    obj = self.deduct_rule_currency("PEN", "USD")
                    ext_rate = self._define_tc_official(
                        self.env.ref("base.USD"))
                    calculate = valcur.ops.get(obj.operator)(
                        oimp,
                        ext_rate.price_orp
                        if obj.s_operationtype == "com"
                        else ext_rate.price_drs,
                    )
                    dictionary.update(
                        {
                            "tc": ext_rate.price_orp
                            if obj.s_operationtype == "com"
                            else ext_rate.price_drs,
                        }
                    )
                else:
                    calculate = 0
                dictionary.update({"amount_equivalent_dol": calculate})
            return dictionary
        else:
            raise ValidationError("No Existe Tc Oficial.")
