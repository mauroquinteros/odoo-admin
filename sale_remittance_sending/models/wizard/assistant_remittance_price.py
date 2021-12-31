# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError, ValidationError

from odoo.addons.l10n_pe_currency.models.utils import values as curval
from odoo.addons.l10n_pe_currency.models.utils import methods as currency_methods
from odoo.addons.sale_config.models.utils import methods as sale_methods, values as sale_values


class AssistantRemittancePrice(models.TransientModel):
    _name = "assistant.remittance.price"

    """
    Desarrollador: Mauro Quinteros
    Cambios: Definir el modelo de assistant.remittance.price que se mostrará al abrir el wizard para calcular la tarifa de la remesa
    """
    destination_country_id = fields.Many2one(
        comodel_name="res.country", string="País destino"
    )
    destination_agency_id = fields.Many2one(
        comodel_name="res.partner.agency", string="Agencia Destino"
    )
    origin_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda a enviar",
        default=lambda self: self.env.ref("base.USD"),
    )
    origin_amount = fields.Monetary(
        string="Monto a enviar", currency_field="origin_currency_id", default=0.00
    )

    itf_tax_id = fields.Many2one(
        comodel_name="account.tax", string="ITF", default=lambda self: self._get_default_itf_tax())
    itf_percent = fields.Float(string="ITF", digits=(9, 4))

    destination_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda a pagar",
        default=lambda self: self.env.ref("base.USD"),
    )
    destination_local_currency = fields.Many2one(
        comodel_name="res.currency", string="Moneda local")
    destination_local_amount = fields.Monetary(string="Monto Local", digits=(
        9, 2), currency_field="destination_local_currency")
    destination_dollar_currency = fields.Many2one(
        comodel_name="res.currency", string="Moneda USD", default=lambda self: self.env.ref("base.USD"))
    destination_dollar_amount = fields.Monetary(string="Monto USD", digits=(
        9, 2), currency_field="destination_dollar_currency")
    destination_euro_currency = fields.Many2one(
        comodel_name="res.currency", string="Moneda EUR", default=lambda self: self.env.ref("base.EUR"))
    destination_euro_amount = fields.Monetary(string="Monto EUR", digits=(
        9, 2), currency_field="destination_euro_currency")

    operative_exchange_rate = fields.Float(
        string="T/C Jet Peru", digits=(9, 4), default=0.0)
    agency_exchange_rate = fields.Float(
        string="T/C Corresponsal", digits=(9, 4), default=0.0)

    show_result = fields.Boolean(string="Mostrar resultado", default=False)
    show_error = fields.Boolean(string='Mostrar error', default=False)

    local_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda local",
        default=lambda self: self.env.ref("base.PEN"),
    )
    service_type_list_ids = fields.Many2many(
        comodel_name="service.type.list",
        string="Servicios por cobrar",
        relation="wizard_remittance_service_type_rel",
        column1="sale_remittance_id",
        column2="service_type_id"
    )
    base_service_price_amount = fields.Monetary(
        string="Cargo", currency_field="local_currency_id", digits=(9, 2))
    service_extra_amount = fields.Monetary(
        string="T. servicios extra", currency_field="local_currency_id", digits=(9, 2))
    service_price_amount = fields.Monetary(
        string="T. servicios", currency_field="local_currency_id", digits=(9, 2))

    sended_local_amount = fields.Monetary(
        string="Monto PEN", currency_field="local_currency_id", digits=(9, 2))
    sended_dollar_amount = fields.Monetary(
        string="Monto USD", currency_field="destination_dollar_currency", digits=(9, 2))
    sended_euro_amount = fields.Monetary(
        string="Monto EUR", currency_field="destination_euro_currency", digits=(9, 2))

    total_igv_amount = fields.Monetary(
        string="IGV", currency_field="local_currency_id", digits=(9, 2))
    base_service_igv_amount = fields.Monetary(
        string="IGV del Cargo", currency_field="local_currency_id", digits=(9, 2))
    service_extra_igv_amount = fields.Monetary(
        string="IGV de los servicios extra", currency_field="local_currency_id", digits=(9, 2))
    itf_amount = fields.Monetary(
        string="ITF", currency_field="local_currency_id", digits=(9, 2))
    total_service_price_amount = fields.Monetary(
        string="Tarifa por cobrar", currency_field="local_currency_id", digits=(9, 2))

    def _get_default_itf_tax(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Obtener el record del ITF que se encuentra en la tabla de impuestos
        """
        itf_tax = self.env['account.tax'].search([('name', '=', 'ITF')])
        return itf_tax

    @api.onchange("itf_tax_id")
    def _onchange_itf_tax_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Agregar el valor en porcentaje del ITF que viene de la tabla de impuestos
        """
        if self.itf_tax_id.id is not False:
            self.itf_percent = self.itf_tax_id.amount

    @api.onchange("destination_country_id")
    def _onchange_destination_country_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Obtener el valor de la moneda local destino y las agencias activas según el valor del país seleccionado
        """
        correspondent_type = ["pagador", "recpag"]
        res = {}
        if self.destination_country_id.id is not False:
            self.destination_local_currency = self.destination_country_id.currency_id
            agencies_by_country = self.env["res.partner.agency"].search(
                ["&", ("country_id", "=", self.destination_country_id.id), ("state", "=", "activo"), ("correspondent_id.correspondent_type", "in", correspondent_type)])
            agency_ids = [int(agency.id) for agency in agencies_by_country]
            res["domain"] = {
                "destination_agency_id": [
                    ("id", "in", agency_ids)
                ]
            }
        else:
            res["domain"] = {
                "destination_agency_id": [
                    ("state", "=", "activo"),
                    ("correspondent_id.correspondent_type", "in", correspondent_type)
                ]
            }
        return res

    @api.onchange("destination_agency_id")
    def _onchange_destination_agency_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Obtener las monedas a enviar y las monedas a pagar disponibles que tiene la agencia (los campos son send_currency_ids y pay_currency_ids)
        """
        res = {}
        if self.destination_agency_id.id is not False:
            send_currency_ids = self.destination_agency_id.send_currency_ids
            destination_currency_ids = self.destination_agency_id.pay_currency_ids
            s_currency_ids = [int(currency.id)
                              for currency in send_currency_ids]
            d_currency_ids = [int(currency.id)
                              for currency in destination_currency_ids]
            res["domain"] = {
                "origin_currency_id": [
                    "&",
                    ("id", "in", s_currency_ids),
                    ("active", "=", True),
                ],
                "destination_currency_id": [
                    "&",
                    ("id", "in", d_currency_ids),
                    ("active", "=", True),
                ]
            }
        else:
            res["domain"] = {
                "origin_currency_id": [
                    "&",
                    ("name", "in", curval.principals),
                    ("active", "=", True),
                ],
                "destination_currency_id": [
                    "&",
                    ("name", "in", curval.principals),
                    ("active", "=", True),
                ]
            }
        return res

    @api.onchange("destination_currency_id", "origin_amount")
    def _onchange_destination_currency_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Calcular el monto a enviar según el valor de la moneda destino y el monto a enviar
        """
        if self.destination_currency_id.id is not False and self.origin_amount != 0:
            sale_methods.get_destination_amount_by_currency(self)

    @api.onchange("origin_currency_id", "origin_amount")
    def _onchange_origin_currency_id(self):
        if self.origin_currency_id.id is not False and self.origin_amount != 0:
            sale_methods.get_sended_amount_by_currency(self)

    @api.onchange("service_type_list_ids")
    def _onchange_service_type_list_ids(self):
        if len(self.service_type_list_ids) > 0:
            self.service_extra_amount = 0
            self.service_extra_igv_amount = 0
            for service_type_item in self.service_type_list_ids:
                if service_type_item.name != sale_values.default_service_type:
                    pricelist_item = sale_methods.get_extra_service_pricelist(
                        self, service_type_item)
                    if pricelist_item is not False:
                        amount_result = sale_methods.calculate_base_amount_igv(
                            self, pricelist_item)
                        self.service_extra_igv_amount += amount_result.get(
                            "igv_amount")
                        self.service_extra_amount += amount_result.get(
                            "base_amount")
                        print("--------- Calculando -------")
                        print("IGV DESPUES DE AGREGAR EL SERVICIO: ",
                              self.service_extra_igv_amount)
                        print("MONTO DEL SERVICIO EXTRA DESPUES DE SUMAR: ",
                              self.service_extra_amount)
                        print("MONTO DEL SERVICIO TOTAL DESPUES DE SUMAR: ",
                              self.service_price_amount)
                        # import pdb
                        # pdb.set_trace()

    @api.onchange("base_service_igv_amount", "service_extra_igv_amount")
    def _onchange_get_total_igv_amount(self):
        if self.base_service_igv_amount != 0:
            self.total_igv_amount = self.base_service_igv_amount + self.service_extra_igv_amount
            print("CALCULANDO LA SUMA DEL IGV TOTAL: ", self.total_igv_amount)

    @api.onchange(
        "base_service_price_amount",
        "service_extra_amount",
        "total_igv_amount",
        "itf_amount"
    )
    def _onchange_get_service_price_amount(self):
        if self.base_service_price_amount != 0 and self.total_igv_amount != 0:
            self.service_price_amount = self.base_service_price_amount + \
                self.service_extra_amount + self.total_igv_amount
            print("CALCULANDO LA SUMA DEL SERVICE_PRICE_AMOUNT: ",
                  self.service_price_amount)
            self.total_service_price_amount = self.service_price_amount + self.itf_amount
            print("CALCULANDO LA SUMA DEL TOTAL_SERVICE_PRICE_AMOUNT: ",
                  self.total_service_price_amount)

    def show_pricelist_amount(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Mostrar el resultado del cálculo de la tarifa
        """
        pricelist_item = sale_methods.get_pricelist_by_agency(self)
        if pricelist_item is not False:
            self.service_type_list_ids = [(4, pricelist_item.service_type.id)]
            amount_result = sale_methods.calculate_base_amount_igv(
                self, pricelist_item)
            self.base_service_price_amount = amount_result.get("base_amount")
            self.base_service_igv_amount = amount_result.get("igv_amount")
            print("MONTO BASE DEL ENVIO: ", self.base_service_price_amount)
            print("IGV BASE DEL ENVIO: ", self.base_service_igv_amount)
            self.show_result = True
            self.show_error = False
        else:
            self.show_result = False
            self.show_error = True

    def validate_all_wizard_fields(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Validar los campos necesarios para realizar el cálculo de la remesa
            - destination_country_id
            - destination_agency_id
            - origin_currency_id
            - origin_amount
        """
        country_validate = True if self.destination_country_id.id is not False else False
        agency_validate = True if self.destination_agency_id.id is not False else False
        origin_currency_validate = True if self.origin_currency_id.id is not False else False
        origin_amount_validate = True if self.origin_amount != 0 else False

        if (
            country_validate
            and agency_validate
            and origin_currency_validate
            and origin_amount_validate
        ):
            return True
        else:
            return False

    @api.onchange(
        "destination_country_id",
        "destination_agency_id",
        "origin_currency_id",
        "origin_amount",
        "destination_currency_id"
    )
    def _onchange_calculation_remittance(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función principal encargada de llamar a las otras funciones para que realicen el cálculo de la tarifa
        """
        if self.validate_all_wizard_fields() is True:
            if self.origin_currency_id.name == "USD" or self.origin_currency_id.name == "EUR":
                self.operative_exchange_rate = currency_methods.devolve_query_exrate(
                    self, Number=1).price_drs

            self.agency_exchange_rate = sale_methods.get_operative_exchange_rate(
                self.destination_agency_id)

            if self.destination_currency_id.id is not False:
                self.show_pricelist_amount()
