# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo.addons.l10n_pe_currency.models.utils import (
    values as curval,
    methods as method,
)


class AutoApprovement(models.Model):
    _name = "res.currency.moex.auto.approvement"
    _description = (
        "Modelo de Aprobación automatica para cambio de divisas ventanilla y/o  online"
    )
    _inherit = ["mail.thread", "mail.activity.mixin"]

    business_line_id = fields.Many2one("business.line", string="Linea de Negocio")
    sale_channel_ids = fields.Many2many(
        string="Canal de Venta",
        comodel_name="business.channel",
        domain=[("channel_type", "=", "sale")],
    )
    remark = fields.Text(string="Observaciones")
    line_ids = fields.One2many(
        "res.currency.moex.auto.approvement.line",
        inverse_name="autoapprovement_id",
        string="Detalle de aprobaciones automaticas",
    )
    active = fields.Boolean(string="active", default=True)


class AutoApprovementLine(models.Model):
    _name = "res.currency.moex.auto.approvement.line"
    _description = "Detalle de aprobaciones automaticas"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    agency_id = fields.Many2one("res.partner.agency", string="Agencia")
    origin_currency_id = fields.Many2one(
        "res.currency", string="Moneda Origen", domain=curval.domain
    )
    destination_currency_id = fields.Many2one(
        "res.currency", string="Moneda Destino", domain=curval.domain
    )
    min_amount = fields.Float(string="Monto Mínimo")
    max_amount = fields.Float(string="Monto Máximo")
    operator = fields.Selection(
        string="Operador", selection=[("+", "(+) Positivo"), ("-", "(-) Negativo")]
    )
    i_value = fields.Float(string="Valor", digits=(6, 4))
    autoapprovement_id = fields.Many2one(
        "res.currency.moex.auto.approvement", string="Aprobaciones automaticas"
    )
    active = fields.Boolean(string="active", default=True)


class MoExCalculation(models.Model):
    _name = "res.currency.moex.calculation"
    _description = "Forma de cálculo de operaciones de cambio de dinero"

    name = fields.Char(string="Nombre de la operacion")
    origin_currency_id = fields.Many2one(
        "res.currency", domain=curval.domain, string="Moneda a recibir"
    )
    destination_currency_id = fields.Many2one(
        "res.currency", domain=curval.domain, string="Moneda a entregar"
    )
    s_operationtype = fields.Selection(
        string="Tipo de Operacion", selection=curval.type_operation
    )
    operator = fields.Selection(
        string="Operador Matemático", selection=curval.type_operator
    )
    amount_proposedexchangerate_adj = fields.Float(
        string="Ajuste Permitido al tipo de cambio propuesto", digits=(9, 4)
    )
    amount_approvedexchangerate_adj = fields.Float(
        string=u"Ajuste Permitido al tipo de cambio aprobado", digits=(9, 4)
    )
    product_id = fields.Many2one(
        "product.template", string="Producto/Servicio Relacionado"
    )
    active = fields.Boolean(string="active", default=True)


class MoExOER(models.Model):
    _name = "res.currency.rate.oer"
    _description = "Tipo de Cambio Operacional"
    _order = "date_validity_period_start desc"
    _rec_name = "agency_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    business_partner_id = fields.Many2one(
        "res.partner",
        string="Socio de Negocio Destino",
        required=True,
        default=lambda self: self.env.user.agency_id.partner_id,
    )
    agency_id = fields.Many2one(
        "res.partner.agency", string="Agencia", ondelete="restrict", required=True
    )
    date_validity_period_start = fields.Datetime(
        string="Inicio de vigencia", default=lambda self: fields.Datetime.now()
    )
    origin_currency_id = fields.Many2one(
        "res.currency", string="Moneda Origen", domain=curval.domain
    )
    destination_currency_id = fields.Many2one(
        "res.currency", string="Moneda Destino", domain=curval.domain
    )
    price_orp = fields.Float(string="Tipo de Cambio Compra", digits=(9, 4))
    price_drs = fields.Float(string="Tipo de Cambio Venta", digits=(9, 4))
    currentactive = fields.Boolean(string="Actualmente Activo", default=True)
    active = fields.Boolean(string="active", default=True)

    @api.model
    def create(self, vals):
        originvalue = vals.get("origin_currency_id", False)
        destinationvalue = vals.get("destination_currency_id", False)
        agencyvalue = vals.get("agency_id")
        obj = self.search(
            [
                "|",
                "&",
                ("origin_currency_id", "=", originvalue),
                "&",
                ("agency_id", "=", agencyvalue),
                "&",
                ("destination_currency_id", "=", destinationvalue),
                ("currentactive", "=", True),
                "&",
                ("origin_currency_id", "=", destinationvalue),
                "&",
                ("agency_id", "=", agencyvalue),
                "&",
                ("destination_currency_id", "=", originvalue),
                ("currentactive", "=", True),
            ]
        )
        if obj.id != False:
            obj.currentactive = False
        result = super(MoExOER, self).create(vals)
        return result

    @api.onchange("origin_currency_id", "destination_currency_id", "agency_id")
    def action_calculate_ratefactor(self):
        agencyvalue = self.agency_id.id
        if (
            self.origin_currency_id.id != False
            and self.destination_currency_id.id != False
        ):
            if (
                self.origin_currency_id.id != self.env.ref("base.PEN").id
                and self.destination_currency_id.id != self.env.ref("base.PEN").id
            ):
                obj_oer_usd = method.currency_rate_exchange(
                    self, self.env.ref("base.USD").id, agencyvalue
                )  # Dolares
                obj_oer_eur = method.currency_rate_exchange(
                    self, self.env.ref("base.EUR").id, agencyvalue
                )  # Euros

                comprausd = obj_oer_usd.price_orp
                ventausd = obj_oer_usd.price_drs
                compraeur = obj_oer_eur.price_orp
                ventaeur = obj_oer_eur.price_drs

                if (
                    comprausd != 0
                    and ventausd != 0
                    and compraeur != 0
                    and ventaeur != 0
                ):
                    self.price_orp = comprausd / ventaeur
                    self.price_drs = ventausd / compraeur
                else:
                    self.price_orp = 0
                    self.price_drs = 0
            else:
                self.price_orp = 0
                self.price_drs = 0
