# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.osv import expression


class ResPartnerBeneficiary(models.Model):
    _name = "res.partner.beneficiary"
    _description = "Historico de Beneficiarios"

    """
    Desarrollador: Mauro Quinteros
    Cambios: Definir el modelo de res.partner.beneficiary
    """
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Remitente",
        ondelete="cascade")

    display_name = fields.Char(
        compute='_compute_display_name',
        store=True)

    name = fields.Char(string="Nombre Completo")
    firstname = fields.Char(string="Nombres")
    lastname = fields.Char(string="Apellido Paterno")
    motherlastname = fields.Char(string="Apellido Materno")

    l10n_latam_identification_type_id = fields.Many2one(
        comodel_name="l10n_latam.identification.type",
        string="Tipo de documento", index=True,
        domain="[('documentcategory_ids.acronym', '=', 'DI')]",
        default=lambda self: self._default_identification_type_id())
    vat = fields.Char(string="Número de Documento")

    mobile = fields.Char(string="Teléfono móvil")
    phone = fields.Char(string="Teléfono fijo")

    street = fields.Char(string="Domicilio")
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="País")
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        domain="[('country_id', '=', country_id)]",
        string="Estado")

    bank_account = fields.Char(
        string="Cuenta Bancaria")
    bank_id = fields.Many2one(
        comodel_name="res.bank", string="Banco")
    account_type = fields.Selection(
        string="Tipo de Cuenta",
        selection=[("saving", "Ahorro"), ("stream", "Corriente")],
        default="saving")

    def _default_identification_type_id(self):
        return self.env["l10n_latam.identification.type"].search([("name", "=", "DNI")])

    @api.onchange("firstname", "lastname", "motherlastname")
    def get_complete_name(self):
        lastname = (self.lastname or "").title()
        motherlastname = (self.motherlastname or "").title()
        name = (self.firstname or "").title()
        self.name = f"{lastname} {motherlastname} {name}"

    @api.depends("name", "vat")
    def _compute_display_name(self):
        for record in self:
            name = (record.name or "").title()
            vat = record.vat or ""
            record.display_name = f"{vat} - {name}"

    @api.depends('vat', 'name')
    def name_get(self):
        result = []
        for record in self:
            vat = f"{record.vat} - " or ""
            name = record.name or ""
            display_name = vat + name
            result.append((record.id, display_name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        ids = self._name_search(name, args, operator, limit=limit)
        return self.browse(ids).sudo().name_get()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('vat', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    """
    Parameters:
    - @unique_identifier
    - @sql_sintax
    - @validation_message
    """
    _sql_constraints = [
        ('vat_unique',
         'UNIQUE (vat, l10n_latam_identification_type_id)',
         'El úmero de identidad debe ser único!')
    ]

    @api.constrains('l10n_latam_identification_type_id', 'vat')
    def _check_unique_vat(self):
        for record in self:
            is_beneficiary_exits = self.search_count([
                ('vat', '=', record.vat),
                ('l10n_latam_identification_type_id', '=', record.l10n_latam_identification_type_id.id)])
            if is_beneficiary_exits > 1:
                raise exceptions.ValidationError(
                    "El úmero de identidad debe ser único!")
