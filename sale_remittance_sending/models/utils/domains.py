# -*- coding: utf-8 -*-
from . import values as sale_values
from odoo.addons.l10n_pe_currency.models.utils import values as curval

def domain_agencies_by_country(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener las agencias según el país seleccionado y se encuentran activos
    """
    res = {
        "domain": {}
    }
    default_domain = ["&", ("state", "=", "activo"), ("correspondent_id.correspondent_type", "in", sale_values.correspondent_type)]
    if self.destination_country_id.id != False:
        domain = [*default_domain, ("country_id", "=", self.destination_country_id.id)]
        res["domain"] = {
            "destination_agency_id": domain
        }
    else:
        res["domain"] = {
            "destination_agency_id": default_domain
        }
    return res

def domain_currencies_by_agency(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener los tipos de servicios disponibles y las monedas aceptadas y de pagos por agencia
    """
    res = {
        "domain": {}
    }
    default_domain = ["&", ("active", "=", True)]
    if self.destination_agency_id.id != False:
        send_currencies = self.destination_agency_id.send_currency_ids
        destination_currencies = self.destination_agency_id.pay_currency_ids

        send_currency_ids = [int(currency.id) for currency in send_currencies]
        destination_currency_ids = [int(currency.id) for currency in destination_currencies]

        send_domain = [*default_domain, ("id", "in", send_currency_ids)]
        destination_domain = [*default_domain, ("id", "in", destination_currency_ids)]
        res["domain"] = {
            "origin_currency_id": send_domain,
            "destination_currency_id": destination_domain,
        }
    else:
        domain = [*default_domain, ("name", "in", curval.principals)]
        res["domain"] = {
            "origin_currency_id": domain,
            "destination_currency_id": domain
        }
    return res
