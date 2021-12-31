# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

from odoo.addons.l10n_pe_currency.models.utils import values as curval
from odoo.addons.base_company.models.utils.functions import transform_internal_code
from datetime import datetime


class ServicePricelist(models.Model):
    _name = "service.pricelist"
    _description = "Tabla de tarifario general"
    _rec_name = "internal_code"

    """
        Desarrollador: Mauro Quinteros
        Cambios: Definir el modelo de service.pricelist para el manejo general de las tarifas.
    """
    internal_code = fields.Char(string="Código", required=True)
    register_date = fields.Date(
        string="Fecha de registro", default=fields.Datetime.now)

    country_id = fields.Many2one("res.country", string="País", required=True)

    service_pricelist_item_ids = fields.One2many(
        comodel_name="service.pricelist.item",
        inverse_name="service_pricelist_id",
        string="Rangos del tarifario",
    )

    @api.model
    def create(self, values):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para agregar un código interno al tarifario según el país al que pertenece el tarifario
        """
        country_id = values["country_id"]
        code_country = self.env["res.country"].search(
            [("id", "=", country_id)])
        len_pricelist = self.env["service.pricelist"].search_count(
            [("country_id", "=", country_id)]
        )

        id_pricelist = transform_internal_code(str(len_pricelist + 1))
        values["internal_code"] = f"TAR{id_pricelist}-{code_country.code}"
        result = super(ServicePricelist, self).create(values)
        return result


class ServicePricelistDetail(models.Model):
    _name = "service.pricelist.detail"
    _description = "Tabla de tarifario detalle"
    _rec_name = "internal_code"
    _inherits = {"service.pricelist": "service_pricelist_id"}

    """
        Desarrollador: Mauro Quinteros
        Cambios: Definir el modelo de service.pricelist.detail para el manejo del tarifario detallado por corresponsal
    """
    internal_code = fields.Char(string="Código", required=True)
    service_pricelist_id = fields.Many2one(
        string="Tarifario general",
        comodel_name="service.pricelist",
        required=True,
        domain="[('country_id', '=?', country_id)]",
    )

    correspondent_id = fields.Many2one(
        comodel_name="res.partner.correspondent",
        string="Corresponsal",
        required=True,
        domain="[('country_id', '=?', country_id)]",
    )
    opening_date = fields.Date(
        string="Inicio de vigencia", default=fields.Datetime.now)
    deadline_date = fields.Date(string="Fin de vigencia")

    @api.model
    def create(self, values):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para agregar un código interno al tarifario del corresponsal según el país al que pertenece el tarifario
        """
        correspondent_id = values["correspondent_id"]
        code_correspondent = self.env["res.partner.correspondent"].search(
            [("id", "=", correspondent_id)]
        )
        len_pricelist = self.env["service.pricelist.detail"].search_count(
            [("correspondent_id", "=", correspondent_id)]
        )

        id_pricelist_detail = transform_internal_code(str(len_pricelist + 1))

        values[
            "internal_code"
        ] = f"TAR{id_pricelist_detail}-{code_correspondent.internal_code}"
        result = super(ServicePricelistDetail, self).create(values)
        return result


class ServicePricelistItem(models.Model):
    _name = "service.pricelist.item"
    _description = "Tabla de rango de precios del tarifario"

    """
        Desarrollador: Mauro Quinteros
        Cambios: Definir el modelo de service.pricelist.item para el manejo de los rangos de precio del tarifario
    """
    service_pricelist_id = fields.Many2one(
        comodel_name="service.pricelist", string="Lista de Precios"
    )

    deposit_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda Depósito",
        domain=curval.domain,
        default=lambda self: self.env.ref("base.USD"),
    )
    payment_currency_id = fields.Many2one(
        comodel_name="res.currency", string="Moneda Pago"
    )

    initial_range = fields.Float(
        string="Rango Inicial", digits=(11, 2), default=1.00)
    final_range = fields.Float(
        string="Rango Final", digits=(11, 2), default=100.00)

    price_amount = fields.Float(string="Tarifa", digits=(11, 2))
    price_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda Tarifa",
        domain=curval.domain,
        default=lambda self: self.env.ref("base.PEN"),
    )
    price_expression = fields.Selection(
        string="Expresión",
        selection=[("porcentual", "Porcentual (%)"), ("nominal", "Nominal")],
        default="nominal",
    )
    service_type = fields.Many2one(
        comodel_name="service.type.list",
        string="Tipo de servicio",
        default=lambda self: self.env["service.type.list"].search(
            [("name", "=", "NORMAL")]
        ),
    )

    hide_tax_field = fields.Boolean(default=False)
    tax_included = fields.Boolean(string="IGV Incluido", default=True)

    @api.onchange("service_type")
    def _onchange_service_type(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para el ocultar elementos según el tipo de servicio seleccionado
        """
        if self.service_type.id is not False:
            if self.service_type.name != "NORMAL":
                self.tax_included = False
                self.hide_tax_field = True
            else:
                self.tax_included = True
                self.hide_tax_field = False

    @api.onchange("price_expression")
    def onchange_price_expression(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para eliminar el valor de la moneda en caso seleccione la expresión de 'porcentual'
        """
        if self.price_expression == "porcentual":
            self.price_currency_id = False
        else:
            self.price_currency_id = self.env.ref("base.PEN")

    @api.model
    def create(self, values):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para eliminar el valor de la moneda en caso seleccione la expresión de 'porcentual'
        """
        if values["price_expression"] == "porcentual":
            values["price_currency_id"] = False

        result = super(ServicePricelistItem, self).create(values)
        return result
