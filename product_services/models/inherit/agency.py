# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class ResPartnerAgency(models.Model):
    _inherit = "res.partner.agency"

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar relación entre agencias y tarifarios detalle
    """
    pricelist_id = fields.Many2one(
        string="Tarifario",
        comodel_name="service.pricelist.detail",
        domain="['&', ('country_id', '=?', country_id), ('correspondent_id', '=?', correspondent_id)]",
    )

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar campos necesarios para la relación de agencias y tipo de cambio por corresponsal
    """
    current_exchange_rate = fields.Float(
        string="Tipo de cambio actual", digits=(9, 4), default=0.0)
    exchange_rate_ids = fields.Many2many(
        string="Tipo de cambio",
        comodel_name="remittance.exchange.rate",
        relation="exchange_rate_agency_rel",
        column1="agency_id",
        column2="exchange_rate_id",
        domain="[('correspondent_id', '=', correspondent_id), ('currenly_active', '=', True)]",
    )

    @api.onchange("exchange_rate_ids")
    def _onchange_current_exchange_rate_ids(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para agregar el tipo de cambio desde la vista de la agencia
        """
        if self._origin.id is not False:
            query = "SELECT exchange_rate_id FROM exchange_rate_agency_rel WHERE agency_id=%s"
            agency_id = self._origin.id
            self.env.cr.execute(query, [agency_id])
            response = self.env.cr.fetchall()
            old_exchange_rate_ids = [int(value[0]) for value in response]
            for exchange_rate in self.exchange_rate_ids:
                exchange_rate_origin = exchange_rate._origin
                if (
                    exchange_rate_origin.id in old_exchange_rate_ids
                    and exchange_rate.currenly_active
                ):
                    self.exchange_rate_ids = [(3, exchange_rate.id, 0)]
                elif (
                    exchange_rate_origin.id not in old_exchange_rate_ids
                    and exchange_rate._origin.currenly_active
                ):
                    self.current_exchange_rate = exchange_rate.exchange_rate_value
                    agency_selected = self.env["res.partner.agency"].search(
                        [("id", "=", agency_id)]
                    )
                    agency_selected.write(
                        {"current_exchange_rate": exchange_rate.exchange_rate_value}
                    )
