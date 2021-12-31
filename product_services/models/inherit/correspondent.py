# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Correspondent(models.Model):
    _inherit = "res.partner.correspondent"

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar una relación con el tipo de cambio para que se actualice a todas sus agencias
    """
    current_exchange_rate = fields.Many2one(
        comodel_name="remittance.exchange.rate",
        string="Tipo de cambio",
        domain="['&', ('correspondent_id', '=', id), ('currenly_active', '=', True)]",
    )

    def add_exchange_rate(self, agency, new_exchange_rate):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para agregar el tipo de cambio de las agencias del corresponsal
        """
        agency_selected = self.env["res.partner.agency"].search(
            [("id", "=", agency.id)]
        )
        query = "INSERT INTO exchange_rate_agency_rel(agency_id, exchange_rate_id) VALUES(%s, %s)"
        self._cr.execute(query, (agency.id, new_exchange_rate.id))
        agency_selected.write(
            {"current_exchange_rate": new_exchange_rate.exchange_rate_value}
        )

    def update_exchange_rate(self, agency, new_exchange_rate):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para actualizar el tipo de cambio de las agencias del corresponsal
        """
        is_duplicated = False
        for exchange_rate in agency.exchange_rate_ids:
            exchange_rate_selected = self.env["remittance.exchange.rate"].search(
                [("id", "=", exchange_rate.id)]
            )
            if exchange_rate_selected.id == new_exchange_rate.id:
                is_duplicated = True
                raise ValidationError("⚠️ Este tipo de cambio ya ha sido registrado!")
            else:
                exchange_rate_selected.write({"currenly_active": False})
        if is_duplicated is False:
            query = "INSERT INTO exchange_rate_agency_rel(agency_id, exchange_rate_id) VALUES(%s, %s)"
            self._cr.execute(query, (agency.id, new_exchange_rate.id))
            agency_selected = self.env["res.partner.agency"].search(
                [("id", "=", agency.id)]
            )
            agency_selected.write(
                {"current_exchange_rate": new_exchange_rate.exchange_rate_value}
            )

    @api.onchange("current_exchange_rate")
    def _onchange_current_exchange_rate(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para agregar o actualizar el tipo de cambio de las agencias que pueden pagar en moneda local
        """
        if self.current_exchange_rate.id is not False:
            new_exchange_rate = self.current_exchange_rate
            agency_validate = self.env["res.partner.agency"].search(
                [
                    "&",
                    ("correspondent_id", "=", self._origin.id),
                    ("accept_local_currency", "=", True),
                ]
            )
            for agency in agency_validate:
                origin_agency = agency._origin
                if len(agency.exchange_rate_ids) > 0:
                    self.update_exchange_rate(origin_agency, new_exchange_rate)
                else:
                    self.add_exchange_rate(origin_agency, new_exchange_rate)

    def open_wizard_to_add_pricelist(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para abrir wizard para agregar el tarifario pasándole valores por defecto a través del contexto
        """
        ctx = {
            "default_country_id": self.country_id.id,
            "default_correspondent_id": self.id,
        }
        result = {
            "name": "Tarifario por Agencias",
            "view_id": self.env.ref(
                "product_services.wizard_add_pricelist_agency_form_view"
            ).id,
            "view_mode": "form",
            "res_model": "add.pricelist.agency",
            "type": "ir.actions.act_window",
            "context": ctx,
            "target": "new",
        }
        return result
