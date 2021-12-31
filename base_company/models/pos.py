# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError

from odoo.addons.base_company.models.utils import values as val
from odoo.addons.l10n_pe_currency.models.utils import values as curval

class POS(models.Model):
    _inherit = ['pos.config']

    agency_id = fields.Many2one("res.partner.agency",string=u"Agencia",required=True)
    profile_id = fields.Many2one("profile.config","Tipo de Perfil",required=True)
    correlative_ids = fields.Many2many(comodel_name='pos.config.correlative', string='Numeros Correlativos')
    threshold_ids = fields.One2many("pos.config.threshold","pos_id",string=u"Montos maximos y minimos")

    aperture_user_id = fields.Many2one(string='Usuario que Apertura',comodel_name='res.users',ondelete='restrict')

    def name_get(self):
        result = []
        for record in self:
            if self.aperture_user_id.id is not False:
                result.append(
                    (
                        record.id,
                        ("(%s: - %s) %s")
                        % (
                            record.profile_id.name,
                            record.name,
                            record.aperture_user_id.name or "",
                        ),
                    )
                )
            else:
                result.append((record.id, ("%s") % (record.name)))
        return result

    @api.model
    def create(self, values):
        seq = self.env["ir.sequence"].next_by_code("pos.cashier") or "Pt000/"
        agency = self.agency_id.browse(values['agency_id'])
        profile = self.profile_id.browse(values['profile_id'])

        values['name'] = profile.type_pt_use + str(agency.name).title() + profile.module_type + str(seq)
        result = super(POS, self).create(values)
        return result

class POSCorrelative(models.Model):
    _name = "pos.config.correlative"
    _description = "Números Correlativos para la generación de números de documento"

    pos_id = fields.Many2one("pos.config", "Punto de venta")

    name = fields.Char("Nombre", readonly=True, store=True)
    ir_sequence_id = fields.Many2one("ir.sequence", "Relación Secuencia", ondelete="restrict", domain=[('implementation', '=', 'custom')])
    i_number = fields.Char("Numero Correlativo")
    commdocument_id = fields.Many2one("l10n_latam.document.type", "Tipo de documento", ondelete="restrict", required=True)
    pos_ids = fields.Many2many("pos.config", string=u"Puntos Relacionados")
    serie = fields.Char("Serie", default="000", readonly=True, store=True)
    company_id = fields.Many2one("res.company", "Company", required=True, default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string=u"active", default=True)

    @api.model
    def create(self, values):
        varshort = self.commdocument_id.search([("id", "=", values["commdocument_id"])])
        nomenclature = varshort.doc_code_prefix if varshort.id != False else ""
        shortletter = varshort.doc_code_prefix[0] if varshort.id != False else ""

        if values.get("serie", "000") == "000":
            seq = self.env["ir.sequence"]
            if "company_id" in values:
                seq = seq.with_context(force_company=values["company_id"])
            values["serie"] = (shortletter + seq.next_by_code("pos.config.correlative.serie") or "/")
            values["name"] = nomenclature + " - " + values["serie"]

        result = super(POSCorrelative, self).create(values)
        return result

    @api.constrains("commdocument_id")
    def _check_one_commdocument(self):
        for pos in self.pos_ids:
            poscorrelatives = self.env["pos.config.correlative"].search(
                ["&",("commdocument_id", "=", self.commdocument_id.id),("pos_ids", "=", pos.id)]
            )
            if len(poscorrelatives) > 1:
                raise ValidationError("Solo puede haber un Tipo documento asigando al punto de venta")

class POSThreshold(models.Model):
    _name = "pos.config.threshold"
    _description = "Registro de umbrales de Punto de ventas"

    currency_id = fields.Many2one("res.currency", string=u"moneda", domain=curval.domain, ondelete="restrict")
    amount_min = fields.Float(string=u"Monto minimo")
    amount_max = fields.Float(string=u"Monto maximo")
    remark = fields.Text(string=u"comentario")
    pos_id = fields.Many2one("pos.config", string=u"Punto de Venta", ondelete="restrict")
    active = fields.Boolean(string=u"active", default=True)
