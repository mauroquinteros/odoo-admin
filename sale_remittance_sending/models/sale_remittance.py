# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.sale_remittance_sending.models.utils import methods as sale_methods, values as sale_values, domains as sale_domains
import base64

class SaleOrderRemittance(models.Model):
    _inherit = ["sale.order"]

    """
    Desarrollador: Mauro Quinteros
    Cambios: Definir el modelo de sale.remittance basado en sale.order

    Estados de la remesa
    1. draft (cotización)
    2. auth (autorizar precio especial)
    3. sent (presupuesto enviado) se valida si el cliente supera el umbral o las listas de control para agregarle en el correo los documentos que necesita.
    4. valid (aprobación de los documentos)
    5. deposit (validar el depósito del cliente desde tesorería)
    6. sale (ordenes de venta)
    """
    partner_beneficiary_id = fields.Many2one(
        comodel_name="res.partner.beneficiary",
        string="Beneficiario",
    )
    state = fields.Selection(
        selection_add=[
            ("sent",),
            ("valid",),
            ("deposit",)
        ],
        track_visibility="always",
    )
    local_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda Local de Jet Peru",
        default=lambda self: sale_methods.get_local_currency(self),
    )
    show_result = fields.Boolean(string="Mostrar resultado", default=False, compute="_can_show_result")
    business_line = fields.Char(string="Línea de Negocio")
    summary_operative = fields.Html(string="Resumen de la operación")
    detail_operative = fields.Html(string="Detalle de la operación")

    destination_country_id = fields.Many2one(
        comodel_name="res.country", string="País"
    )
    destination_agency_id = fields.Many2one(
        comodel_name="res.partner.agency", string="Ciudad"
    )
    destination_correspondent_id = fields.Many2one(
        comodel_name="res.partner.correspondent", string="Pagador"
    )

    origin_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda a depositar"
    )
    origin_amount = fields.Monetary(
        string="Monto a depositar", currency_field="origin_currency_id", default=0.00
    )

    destination_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda destino"
    )
    destination_amount = fields.Monetary(
        string="Monto destino", currency_field="destination_currency_id", default=0.00
    )
    destination_exchange_rate = fields.Float(
        string="T/C", digits=(9, 4), default=0.0
    )

    orp_exchange_rate = fields.Float(
        string="T/C Operativo de compra", digits=(9, 4), default=0.0
    )
    drs_exchange_rate = fields.Float(
        string="T/C Operativo de venta", digits=(9, 4), default=0.0
    )
    service_type_list_ids = fields.Many2many(
        comodel_name="service.type.list",
        string="Servicios por cobrar",
        relation="sale_order_remittance_service_type_rel",
        column1="sale_remittance_id",
        column2="service_type_id"
    )

    base_service_amount  = fields.Monetary(
        string="Monto base", digits=(9, 2),
        currency_field="local_currency_id"
    )
    base_extra_service_amount = fields.Monetary(
        string="Monto base de los servicios extra", digits=(9, 2),
        currency_field="local_currency_id"
    )
    total_base_service_amount = fields.Monetary(
        string="Comisión", digits=(9, 2),
        currency_field="local_currency_id"
    )
    igv_service_amount = fields.Monetary(
        string="IGV del monto", digits=(9, 2),
        currency_field="local_currency_id"
    )
    igv_extra_service_amount = fields.Monetary(
        string="IGV de los servicios extra", digits=(9, 2),
        currency_field="local_currency_id"
    )
    total_igv_service_amount = fields.Monetary(
        string="Impuestos", digits=(9, 2),
        currency_field="local_currency_id"
    )
    sub_total_service_amount = fields.Monetary(
        string="Total", digits=(9, 2),
        currency_field="local_currency_id"
    )
    itf_service_amount = fields.Monetary(
        string="ITF", digits=(9, 2),
        currency_field="local_currency_id"
    )
    total_service_amount = fields.Monetary(
        string="A cobrar", digits=(9, 2),
        currency_field="local_currency_id"
    )

    @api.depends(
        "origin_currency_id",
        "origin_amount",
        "destination_country_id",
        "destination_agency_id",
        "destination_currency_id"
    )
    def _can_show_result(self):
        if sale_methods.validate_business_line(self):
            if sale_methods.is_empty_fields(self):
                self.show_result = True
            else:
                self.show_result = False

    @api.depends("local_currency_id")
    def _get_sale_order_line_currency(self):
        if sale_methods.validate_business_line(self):
            self.currency_id = self.local_currency_id
            # self.pricelist_id = self.pricelist_id.search([("currency_id", "=", self.local_currency_id.id)], limit=1)

    @api.onchange("destination_country_id")
    def _onchange_destination_country_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Obtener las agencias activas según el valor del país seleccionado
        """
        if sale_methods.validate_business_line(self):
            res = {}
            domain = sale_domains.domain_agencies_by_country(self)
            res.update(domain)
            return res

    @api.onchange("destination_agency_id")
    def _onchange_destination_agency_id(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Obtener las monedas a enviar y las monedas a pagar disponibles que tiene la agencia (los campos son send_currency_ids y pay_currency_ids)
        """
        if sale_methods.validate_business_line(self):
            res = {}
            if self.destination_agency_id.id != False:
                self.destination_correspondent_id = sale_methods.get_correspondent_by_agency(self)
                self.destination_exchange_rate = sale_methods.get_exchange_rate_by_agency(self)
            domain = sale_domains.domain_currencies_by_agency(self)
            res.update(domain)
            return res

    @api.onchange("service_type_list_ids")
    def _onchange_service_type_list_ids(self):
        default_service_type = self.env['service.type.list'].search([('name', '=', sale_values.default_service_type)])
        self.service_type_list_ids = [(4, default_service_type.id, 0)]
        sale_methods.reset_extra_service_amounts(self)

        if sale_methods.validate_business_line(self) and len(self.service_type_list_ids) > 1:
            for service_type_item in self.service_type_list_ids:
                if service_type_item.name != sale_values.default_service_type:
                    result = sale_methods.get_pricelist_item_by_agency(self, service_type_item.name)
                    if result['success'] == True and result['error'] == False:
                        sale_methods.get_base_igv_amount(self, result, service_type_item.name)
                    else:
                        self.env.user.notify_warning(message=f"⚠️ {result['message']}")
                        self.service_type_list_ids =  [(3, service_type_item.id, 0)]
    @api.onchange(
        "base_service_amount",
        "base_extra_service_amount",
        "igv_service_amount",
        "igv_extra_service_amount",
        "itf_service_amount"
    )
    def _onchange_get_total_service_amount(self):
        if sale_methods.validate_business_line(self) and sale_methods.is_empty_fields_amount(self):
            self.total_base_service_amount = self.base_service_amount + self.base_extra_service_amount
            self.total_igv_service_amount = self.igv_service_amount + self.igv_extra_service_amount

            self.sub_total_service_amount = self.total_base_service_amount + self.total_igv_service_amount
            self.total_service_amount = self.sub_total_service_amount + self.itf_service_amount

            self.detail_operative = sale_methods.create_detail_scheme(self)

    @api.onchange(
        "origin_currency_id",
        "origin_amount",
        "destination_country_id",
        "destination_agency_id",
        "destination_currency_id"
    )
    def _onchange_calculate_remittance(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Obtener el monto que se recibirá en la agencia destino dependiendo de las monedas disponibles a pagar en destino
        """
        if sale_methods.validate_business_line(self) and sale_methods.is_empty_fields(self):
            result = sale_methods.get_pricelist_item_by_agency(self)
            if result['success'] == True and result['error'] == False:
                destination_amount = sale_methods.get_destination_amount_by_currency(self)
                self.destination_amount = destination_amount
                self.service_type_list_ids = [(5, 0, 0), (4, result['pricelist_item'].service_type.id, 0)]

                sale_methods.reset_extra_service_amounts(self)
                sale_methods.get_base_igv_amount(self, result)
                if self.drs_exchange_rate == 0.0 and self.orp_exchange_rate == 0.0:
                    sale_methods.get_operative_exchange_rates(self, self.origin_currency_id, self.local_currency_id)
            else:
                self.destination_currency_id = False
                self.env.user.notify_warning(message=f"⚠️ {result['message']}")

    def action_remittance_quotation_send(self):
        self.ensure_one()
        lang = self.env.context.get('lang')
        template_id = self.env.ref("sale_remittance_sending.email_template_notify_remsend").id
        template = self.env["mail.template"].browse(template_id)

        report_quote = self.env.ref("sale_remittance_sending.report_remittance_quote")
        attachment_id = sale_methods.attach_pdf_mail(self, "Cartilla-%s" % (self.name), report_quote, self.id)
        template.update({
            "attachment_ids": attachment_id
        })

        if template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.ids[0])

        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def get_list_remittance_banks(self):
        result = self.env["res.partner.bank"].search(
            [
                "&",
                ("account_type", "=", sale_values.account_type),
                "&",
                ("partner_id", "=", self.env.user.company_id.id),
                ("currency_id", "in", (self.local_currency_id.id, self.origin_currency_id.id)),
            ]
        )
        return result

    @api.model
    def create(self, values):
        if sale_methods.validate_business_line(self):
            values['business_line'] = self.env.context.get("business_line_key")

            order_line = sale_methods.get_order_line(self, values)
            values.update({
                "order_line": order_line
            })
        result = super(SaleOrderRemittance, self).create(values)

        if sale_methods.validate_business_line(self):
            sale_methods.add_res_partner_beneficiary(result, values)
            scheme = sale_methods.create_summary_scheme(self, result, {
                'orp_exchange_rate': result.orp_exchange_rate,
                'drs_exchange_rate': result.drs_exchange_rate,
                'service_amount': result.total_service_amount,
                'origin_amount': result.origin_amount,
                'local_currency': result.local_currency_id,
                'origin_currency': result.origin_currency_id
            })
            result.summary_operative = scheme
        return result

