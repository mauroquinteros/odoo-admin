# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AddPricelistAgency(models.TransientModel):
    _name = "add.pricelist.agency"

    """
        Desarrollador: Mauro Quinteros
        Cambios: Definir el modelo de add.pricelist.agency que se mostrará al abrir el wizard
    """
    country_id = fields.Many2one(
        comodel_name="res.country", string="País de las agencias"
    )
    correspondent_id = fields.Many2one(
        comodel_name="res.partner.correspondent", string="Corresponsal"
    )

    pricelist_id = fields.Many2one(
        string="Tarifario",
        comodel_name="service.pricelist.detail",
        domain="['&', ('country_id', '=?', country_id), ('correspondent_id', '=?', correspondent_id)]",
    )
    agency_ids = fields.Many2many(
        string="Agencias",
        comodel_name="res.partner.agency",
        relation="wizard_correspondent_agency_rel",
        column1="correspondent_wizard_id",
        column2="agency_wizard_id",
    )
    pricelist_item_ids = fields.Many2many(
        string="Tarifas",
        comodel_name="service.pricelist.item",
        relation="wizard_agency_pricelist_items_rel",
        column1="correspondent_wizard_id",
        column2="pricelist_item_wizard_id",
    )
    pricelist_items_ids = []
    country_codes = []

    @api.onchange("correspondent_id")
    def _onchange_correspondent_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para filtrar los países en los cuales el corresponsal tiene presencia
        """
        if self.correspondent_id.id is not False:
            if len(self.correspondent_id.agency_ids) > 0:
                self.country_codes = []
                for agency_id in self.correspondent_id.agency_ids:
                    country_code = agency_id.country_id.code
                    if country_code not in self.country_codes:
                        self.country_codes.append(country_code)
                res = {}
                res["domain"] = {
                    "country_id": [
                        ("code", "in", self.country_codes),
                    ]
                }
                return res

    @api.onchange("country_id")
    def _onchange_country_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Comparar el país del tarifario y el país de las agencias con el país seleccionado, si son diferentes se reinicia el valor de todos los campos
        """
        if self.pricelist_id is not False:
            if self.pricelist_id.country_id != self.country_id:
                self.pricelist_id = False
                self.pricelist_item_ids = False
            if len(self.agency_ids) > 0:
                if self.agency_ids[0].country_id != self.country_id:
                    self.agency_ids = False

    @api.onchange("country_id", "correspondent_id")
    def _onchange_country_correspondent(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Actualizar la lista de agencias según el corresponsal y el país que se seleccione
        """
        if self.country_id.id is not False and self.correspondent_id.id is not False:
            agencies_filter = self.env["res.partner.agency"].search(
                [
                    "&",
                    ("correspondent_id", "=", self.correspondent_id.id),
                    ("country_id", "=", self.country_id.id),
                ]
            )
            agencies_ids = [agency.id for agency in agencies_filter]
            res = {}
            res["domain"] = {
                "agency_ids": [
                    "&",
                    ("id", "in", agencies_ids),
                    ("state", "=", "activo"),
                ]
            }
            return res

    def _convert_pricelist_item(self, pricelist_item):
        dict_pricelist_item = {
            "id": pricelist_item.id,
            "service_pricelist_id": pricelist_item.service_pricelist_id,
            "deposit_currency_id": pricelist_item.deposit_currency_id,
            "payment_currency_id": pricelist_item.payment_currency_id,
            "initial_range": pricelist_item.initial_range,
            "final_range": pricelist_item.final_range,
            "price_expression": pricelist_item.price_expression,
            "price_amount": pricelist_item.price_amount,
            "price_currency_id": pricelist_item.price_currency_id,
            "tax_included": pricelist_item.tax_included,
            "service_type": pricelist_item.service_type,
        }
        return dict_pricelist_item

    @api.onchange("pricelist_id")
    def _onchange_pricelist_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Actualizar la lista de rangos de precio según el tarifario que se seleccione
        """
        if self.pricelist_id is not False:
            self.pricelist_items_ids = [(5, 0, 0)]
            service_pricelist_id = self.env["service.pricelist"].search(
                [
                    (
                        "internal_code",
                        "=",
                        self.pricelist_id.service_pricelist_id.internal_code,
                    )
                ]
            )
            pricelist_items_filter = self.env["service.pricelist.item"].search(
                [("service_pricelist_id", "=", service_pricelist_id.id)]
            )
            for pricelist_item in pricelist_items_filter:
                val = self._convert_pricelist_item(pricelist_item)
                self.pricelist_items_ids.append((0, 0, val))
            self.pricelist_item_ids = self.pricelist_items_ids

    def add_pricelist_to_agencies(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para agregar el tarifario a cada una de las agencias del corresponsal según el pais destino
        """
        if len(self.agency_ids) > 0 and self.pricelist_id.id is not False:
            for agency in self.agency_ids:
                print("AGENCY: ", agency)
                print("AGENCY PRICELIST: ", agency.pricelist_id)
                print("PRICELIST SELECTED: ", self.pricelist_id)
                if agency.pricelist_id.id is not False:
                    if self.pricelist_id.id == agency.pricelist_id.id:
                        message = f"⚠️ La agencia {agency.name} ya tiene registrado este tarifario!"
                        self.env.user.notify_danger(message=message)
                    else:
                        agency.pricelist_id = self.pricelist_id
                        self.env.user.notify_success(
                            message="El tarifario fue registrado!"
                        )
                else:
                    agency.pricelist_id = self.pricelist_id
                    self.env.user.notify_success(
                        message="El tarifario fue registrado!")
        else:
            self.env.user.notify_warning(
                message="⚠️ Debe seleccionar las agencias y el tarifario que desea asignar!"
            )
            return False
