# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################

import base64
import calendar
from datetime import datetime as dt
from datetime import timedelta as td

import pytz
from dateutil.relativedelta import relativedelta
from odoo import _, api, exceptions, fields, models
from odoo.addons.l10n_pe_currency.models.utils import methods as currency_methods
from odoo.addons.l10n_pe_currency.models.utils import values as valcur
from odoo.addons.sale_money_exchange.models.utils import methods as sale_moex_methods
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrderMoEx(models.Model):
    _inherit = "sale.order"

    business_channel_id = fields.Many2one(
        comodel_name="business.channel",
        string="Canal de Atención",
        domain=[("channel_type", "=", "sale")],
        track_visibility="always",
    )
    validity_time = fields.Datetime(string="Tiempo de Expiración")

    @api.onchange("origin_currency_id")
    def _onchange_currency_list(self):
        if (self.env.context.get("business_line_key") == self.env.ref("base_company.business_line_001", False).foreign_code):
            self.currency_id = self.origin_currency_id
            self.pricelist_id = self.pricelist_id.search(
                [("currency_id", "=", self.origin_currency_id.id)], limit=1
            ).id

    origin_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Origin Currency",
        track_visibility="always",
        domain=lambda self: self._get_currency_domain(),
        default=lambda self: self._get_default_origin_currency()
    )

    def _get_default_origin_currency(self):
        if (self.env.context.get("business_line_key") == self.env.ref("base_company.business_line_001", False).foreign_code):
            return self.env.ref(self.env["ir.config_parameter"].sudo().get_param("default.origin.currency"))

    destination_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Destination Currency",
        track_visibility="always",
        domain=lambda self: self._get_currency_domain(),
        default=lambda self: self._get_default_destination_currency()
    )

    def _get_default_destination_currency(self):
        if (self.env.context.get("business_line_key") == self.env.ref("base_company.business_line_001", False).foreign_code):
            return self.env.ref(self.env["ir.config_parameter"].sudo().get_param("default.destination.currency"))

    def _get_currency_domain(self):
        names = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("currency.domain.parameter")
        )
        domain = [("name", "in", names.split(","))]
        return domain

    origin_import = fields.Float(
        string="Origin Import", digits=(10, 2), track_visibility="always"
    )
    destination_import = fields.Float(
        string="Destination Import", digits=(10, 2), track_visibility="always"
    )

    operative_rate = fields.Float(
        string="Operative Rate", digits=(1, 4), track_visibility="always"
    )
    proposed_rate = fields.Float(
        string="Proposed Rate", digits=(1, 4), track_visibility="always"
    )
    approved_rate = fields.Float(
        string="Approved Rate", digits=(1, 4), track_visibility="always"
    )

    operator = fields.Selection(
        [("*", "Compra"), ("/", "Venta")], track_visibility="always", default="*"
    )

    state = fields.Selection(
        selection_add=[
            ("auth", "Authorization T.C."),
            ("valid",),
            ("valid", "Validated Quote"),
            ("sent",),
            ("deposit", "Attach Deposit & Acredit"),
            ("sale",),
        ],
        track_visibility="always",
    )

    deposit_ids = fields.One2many(
        comodel_name="deposit.order",
        inverse_name="sale_order_id",
        string="Customer deposit",
        domain=[("type", "=", "A-I")],
        track_visibility="always",
    )
    total_deposit = fields.Float(
        string="Total amount deposit",
        digits=(9, 2),
        store=False,
        track_visibility="always",
        compute="_compute_total_deposit",
    )

    @api.depends("deposit_ids.amount_deposit")
    def _compute_total_deposit(self):
        total = 0
        for record in self.deposit_ids:
            total += record.amount_deposit
        self.total_deposit = round(total, 2)

    acredit_ids = fields.One2many(
        comodel_name="deposit.order",
        inverse_name="sale_order_id",
        string="Customer Accreditation",
        domain=[("type", "=", "B-E")],
        track_visibility="always",
    )
    total_acredit = fields.Float(
        string="Total amount acredit",
        digits=(9, 2),
        store=False,
        track_visibility="always",
        compute="_compute_total_acredit",
    )

    def action_cancel(self):
        res = super(SaleOrderMoEx, self).action_cancel()
        if self.env.context.get("cancel_with_deposits", False) == True:
            for rec in self:
                for dep in rec.deposit_ids + rec.acredit_ids:
                    if dep.state == "unchecked":
                        dep.write({"state": "cancel"})
        return res

    def _check_deposits_acredits(self):
        resp = ""
        if len(self.deposit_ids) > 0 and len(self.acredit_ids) > 0:
            resp = True
        else:
            resp = (
                "Algo ocurrió con el/los depósito(s) y/o abono(s) registrados, revisar"
            )
        return resp

    def action_confirm(self):
        if self.env.context.get("super_in_confirm", False) == True:
            resp = self._check_deposits_acredits()
            for dep in self.deposit_ids:
                if dep.state == "unchecked" or dep.state == False:
                    raise ValidationError(
                        "Para Confirmar la Orden de Venta primero se debe de revisar los depósitos del Cliente."
                    )
            if type(resp) is bool and resp == True:
                return super(SaleOrderMoEx, self).action_confirm()
            else:
                raise ValidationError(resp)

        return super(SaleOrderMoEx, self).action_confirm()

    def _check_import_deposit(self):
        if self.total_deposit == self.origin_import and round(
            self.total_acredit, 2
        ) == round(self.destination_import, 2):
            return True

    def _pass_to_pending(self):
        deps = self.deposit_ids + self.acredit_ids
        for d in deps:
            if d.state == False:
                d.write({"state": "unchecked"})

    def action_check_deposit(self):
        resp = self._check_deposits_acredits()
        if type(resp) is bool and resp == True:
            self._pass_to_pending()
            if self._check_import_deposit() == True:
                self.write({"state": "deposit"})
            else:
                self.env.user.notify_warning(
                    message="⚠️ Revisar los depósitos y abonos del Cliente."
                )
        else:
            self.env.user.notify_danger(message=resp)

    @api.depends("acredit_ids.amount_payable")
    def _compute_total_acredit(self):
        total = 0
        for record in self.acredit_ids:
            total += record.amount_payable
        self.total_acredit = round(total, 2)

    def _track_subtype(self, init_values):
        # OVERRIDE to add custom subtype depending of the state.
        self.ensure_one()
        if "state" in init_values and self.state == "auth":
            return self.env.ref("sale_money_exchange.mt_order_require_auth")
        elif "state" in init_values and self.state == "valid":
            return self.env.ref("sale_money_exchange.mt_order_grant_auth")
        elif "state" in init_values and self.state == "deposit":
            return self.env.ref("sale_money_exchange.mt_order_confirm_deposit")
        if "checker" in init_values:
            return self.env.ref("sale_money_exchange.mt_check_deposit_done")
        return super(SaleOrderMoEx, self)._track_subtype(init_values)

    def _check_both_currencies(self, response=False):
        if self.origin_currency_id.id == self.destination_currency_id.id:
            self.origin_import = 0
            self.destination_import = 0
            self.operator = False
            self.operative_rate = False
            self.proposed_rate = False
            self.approved_rate = False
        if len(self.origin_currency_id) + len(self.destination_currency_id) == 2:
            if self.origin_currency_id.id != self.destination_currency_id.id:
                response = True
        return response

    def _return_value_exrate(self, fields=""):
        self.ensure_one()
        value = currency_methods.devolve_query_calculation(self, Constant=fields)
        return value

    @api.onchange("origin_currency_id", "destination_currency_id")
    def onchange_actions(self):
        if self._check_both_currencies():
            if (self.env.context.get("business_line_key") == self.env.ref("base_company.business_line_001", False).foreign_code):
                value = self._return_value_exrate(fields="operator")
                self.operator = value["operator"]

    @api.onchange("operator")
    def onchange_operator(self):
        self.onchange_actions()
        if self._check_both_currencies() and self.operator != False:
            if (self.env.context.get("business_line_key") == self.env.ref("base_company.business_line_001", False).foreign_code):
                operator = self._return_value_exrate(fields="s_operationtype")[
                    "s_operationtype"
                ]
                tc = currency_methods.devolve_query_exrate(self, Number=1)
                self.operative_rate = tc.price_orp if operator == "com" else tc.price_drs

    def onchange_result_origin(self):
        bsln = self.env.context.get("business_line_key", False)
        chnl = self.business_channel_id
        amount = self.origin_import if self.operator == "*" else self.destination_import
        if self._check_both_currencies() and amount > 0:
            line = currency_methods.devolve_query_approvement(self, bsln, chnl, amount)
            if self.proposed_rate == self.approved_rate:
                self.proposed_rate = valcur.ops.get(line.operator)(
                    self.operative_rate, line.i_value
                )
                self.approved_rate = self.proposed_rate

    @api.onchange("approved_rate", "origin_import", "destination_import")
    def onchange_approved_rate(self):
        self.onchange_result_origin()
        if self._check_both_currencies():
            if self.operator == "*":
                self.destination_import = valcur.ops.get(self.operator)(
                    self.origin_import, self.approved_rate
                )
            else:
                self.origin_import = valcur.ops.get("*")(
                    self.destination_import, self.approved_rate
                )

    @api.model
    def create(self, values):
        param = self.env["ir.config_parameter"].sudo()
        origincurrency = self.env["res.currency"].browse(
            values.get("origin_currency_id")
        )
        destinationcurrency = self.env["res.currency"].browse(
            values.get("destination_currency_id")
        )

        if (
            self.env.context.get("business_line_key")
            == self.env.ref("base_company.business_line_001", False).foreign_code
        ):
            product_sMoExOnline = self.env.ref(
                "product_services.product_tmpl_service_moex_online"
            )
            product_sConvertline = self.env.ref(
                "product_services.product_tmpl_service_convert_online"
            )
            try:
                line = [
                    (
                        0,
                        False,
                        {
                            "product_id": sale_moex_methods.locate_product(
                                self, product_sMoExOnline
                            ).id,
                            "name": "["
                            + product_sMoExOnline.default_code
                            + "]"
                            + " "
                            + product_sMoExOnline.name,
                            "product_uom_qty": 1.0,
                            "price_unit": 0.0,
                            "tax_id": product_sMoExOnline.taxes_id.ids,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": sale_moex_methods.locate_product(
                                self, product_sConvertline
                            ).id,
                            "name": "["
                            + product_sConvertline.default_code
                            + "]"
                            + " "
                            + product_sConvertline.name,
                            "product_uom_qty": 1.0,
                            "price_unit": values["origin_import"],
                            "tax_id": product_sConvertline.taxes_id.ids,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "name": "Resumen:",
                            "display_type": "line_section",
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "name": param.get_param("scheme.terms.o2m.content")
                            % (
                                origincurrency.symbol,
                                values["origin_import"],
                                origincurrency.currency_unit_label,
                                destinationcurrency.symbol,
                                round(values["destination_import"], 2),
                                destinationcurrency.currency_unit_label,
                            ),
                            "display_type": "line_note",
                        },
                    ),
                ]
                values.update(
                    {
                        "order_line": line,
                    }
                )
                values["validity_time"] = values["validity_date"]
                values["require_payment"] = self.env.context.get(
                    "require_payment_key", False
                )
                values["payment_term_id"] = self.env.ref(
                    self.env.context.get("payment_term_key", False), False
                ).id
                values["note"] = param.get_param("scheme.terms.content")
                sale_moex_methods.target_sequence_pos(self, values)

                if values["proposed_rate"] != values["approved_rate"]:
                    values["state"] = "auth"
            except:
                raise ValidationError(
                    "Error, no se puede crear la cotización, contacte con su administrador."
                )

            if values["origin_import"] <= 0:
                raise ValidationError(
                    "Error, no debe de ingresar cantidades en cero en el importe."
                )
            if values["approved_rate"] <= 0:
                raise ValidationError(
                    "Error, no debe de ingresar tasa aprobada menor o igual a cero."
                )

            req = []
            docs = self.check_documents(
                values["origin_import"],
                values["origin_currency_id"],
                values["partner_id"],
            )

            for re in docs:
                req.append((0, 0, {"cat_document_id": re}))
        result = super(SaleOrderMoEx, self).create(values)
        return result

    def _find_mail_custom_template(self, force_confirmation_template=False):
        template_id = False

        if force_confirmation_template or (
            self.state == "sale" and not self.env.context.get("proforma", False)
        ):
            template_id = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("sale.default_confirmation_template")
            )
            template_id = (
                self.env["mail.template"].search([("id", "=", template_id)]).id
            )
            if not template_id:
                template_id = self.env["ir.model.data"].xmlid_to_res_id(
                    "sale.mail_template_sale_confirmation", raise_if_not_found=False
                )

        if not template_id:
            if self.env.context.get("mail", False) == "moex":
                template_id = self.env["ir.model.data"].xmlid_to_res_id(
                    "sale_money_exchange.email_template_notify_moex",
                    raise_if_not_found=False,
                )
            else:
                template_id = self.env["ir.model.data"].xmlid_to_res_id(
                    "sale.email_template_edi_sale", raise_if_not_found=False
                )

        return template_id

    def action_moex_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()
        template_id = self._find_mail_custom_template()
        lang = self.env.context.get("lang")
        template = self.env["mail.template"].browse(template_id)
        newsletter = self.env.ref("sale_money_exchange.report_quote_newsletter")
        template.update(
            {
                "attachment_ids": sale_moex_methods.attach_ro_send(
                    self, "Cartilla", newsletter, self.id
                )
            }
        )
        if template.lang:
            lang = template._render_template(template.lang, "sale.order", self.ids[0])

        ctx = {
            "default_model": "sale.order",
            "default_res_id": self.ids[0],
            "default_use_template": bool(template_id),
            "default_template_id": template_id,
            "default_composition_mode": "comment",
            "mark_so_as_sent": True,
            "custom_layout": "mail_layout_extra.mail_notification_paynow",
            "proforma": self.env.context.get("proforma", False),
            "force_email": True,
            "model_description": self.with_context(lang=lang).type_name,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get("mark_so_as_sent"):
            self.filtered(lambda o: o.state in ["draft", "valid"]).with_context(
                tracking_disable=True
            ).write({"state": "sent"})
            self.env.company.sudo().set_onboarding_step_done(
                "sale_onboarding_sample_quotation_state"
            )
            if self.validity_time == False:
                self.validity_time = dt.now() + relativedelta(minutes=45)
        return super(
            SaleOrderMoEx, self.with_context(mail_post_autofollow=True)
        ).message_post(**kwargs)

    def get_list_bank(self):
        result = self.env["res.partner.bank"].search(
            [
                "&",
                ("account_type", "=", "ctamoex"),
                "&",
                ("partner_id", "=", self.env.user.company_id.id),
                ("currency_id", "=", self.origin_currency_id.id),
            ]
        )
        return result

    def action_view_ro(self):
        invoices = self.mapped("invoice_ids")
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        if len(invoices) > 1:
            action["domain"] = [("id", "in", invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref("account.view_move_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = invoices.id
        else:
            action = {"type": "ir.actions.act_window_close"}

        context = {
            "default_type": "out_invoice",
        }
        if len(self) == 1:
            context.update(
                {
                    "default_partner_id": self.partner_id.id,
                    "default_partner_shipping_id": self.partner_shipping_id.id,
                    "default_invoice_payment_term_id": self.payment_term_id.id
                    or self.partner_id.property_payment_term_id.id
                    or self.env["account.move"]
                    .default_get(["invoice_payment_term_id"])
                    .get("invoice_payment_term_id"),
                    "default_invoice_origin": self.mapped("name"),
                    "default_user_id": self.user_id.id,
                }
            )
        action["context"] = context
        return action

    def get_list_bank(self):
        result = self.env["res.partner.bank"].search(
            [
                "&",
                ("account_type", "=", self.env.context.get("type_acc_company", False)),
                "&",
                ("partner_id", "=", self.env.user.company_id.id),
                ("currency_id", "=", self.origin_currency_id.id),
            ]
        )
        return result

    def check_documents(self, amount, currency, partner, docs=[]):
        total = 0

        orders = self.env["pay.order"].sudo().search([("res_partner_id", "=", partner)])
        total = sum(ite.amount_equivalent_dol for ite in orders)

        UniqThreshold = self.env["plaft.control.threshold"].search(
            [
                "&",
                ("business_line_id", "=", 1),
                "&",
                ("control_type", "=", "U"),
                ("currency_id", "=", currency),
                "&",
                ("amount_min", "<=", amount),
                ("amount_max", ">=", amount),
            ],
            limit=1,
        )
        MultiThreshold = self.env["plaft.control.threshold"].search(
            [
                "&",
                ("business_line_id", "=", 1),
                "&",
                ("control_type", "=", "M"),
                ("currency_id", "=", currency),
                "&",
                ("amount_min", "<=", int(round(total + amount, 2))),
                ("amount_max", ">=", int(round(total + amount, 2))),
            ]
        )

        total = sum(ite.amount_equivalent_dol for ite in orders)

        for requniq in UniqThreshold.threshold_req_ids:
            docs.append(requniq.id)

        for reqmulti in MultiThreshold.threshold_req_ids:
            if reqmulti.id not in docs:
                docs.append(reqmulti.id)

        return docs
