# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta
import pytz
import operator

from odoo.tools import image_process, ustr

from odoo.addons.base_config.models.utils import values as baseval
from odoo.osv import expression


class ResPartner_Inherit(models.Model):
    _inherit = ['res.partner']

    type = fields.Selection(selection_add=[("supplier", "Proveedor"), ("enterprise", "Empresa"),
                                           ("agency", "Agencia"), ("agent", "Agente"), ("customer", "Cliente"), ("employee", "Empleado"), ("correspondent", "Corresponsal")])

    lastname = fields.Char(string=u'Apellido Paterno',
                           store=True, track_visibility='always', default='')
    motherlastname = fields.Char(
        string=u'Apellido Materno', store=True, track_visibility='always', default='')
    firstname = fields.Char(string=u'Nombres', store=True,
                            track_visibility='always', default='')

    country_id = fields.Many2one(
        comodel_name='res.country', string='Country',
        track_visibility='onchange',
        default=lambda self: self.env.user.country_id.id or self.env.ref('base.pe').id)
    state_id = fields.Many2one("res.country.state", string=u'State',
        ondelete='restrict', track_visibility='onchange',
        default=lambda self: self.env.user.partner_id.parent_id.state_id.id or self.env.user.partner_id.state_id.id or False)

    gender_id = fields.Many2one(
        comodel_name='l10n_pe_sunat.anexo.06', string='Género',
        default=lambda self: self.env.ref('l10n_pe_sunat.anexo06_1'))
    customer_state = fields.Selection(
        string=u'Estado del Cliente', selection=baseval.status_customer, track_visibility='always')

    date_birth = fields.Date(
        string=u'Fecha de Nacimiento', track_visibility='always')

    contrib_type_id = fields.Many2one(
        comodel_name='l10n_pe_sunat.anexo.02', string='Tipo de Contribuyente', track_visibility='always')
    work_company_customer = fields.Char(
        string=u'Lugar de Trabajo', track_visibility='always')
    stat_company_type = fields.Selection(
        string=u'Sector de Trabajo',
        selection=[('pri', 'Privado'), ('pub', 'Pública')], track_visibility='always')

    @api.onchange('stat_company_type')
    def _onchange_stat_company_type_wrapper(self):
        self.position_id = False

    position_details = fields.Char(
        string=u'Cargo detalles', track_visibility='always')

    occupation_id = fields.Many2one(
        'l10n_pe_sunat.anexo.11', string=u'Profesión/Ocupación', ondelete='restrict', track_visibility='always')

    @api.onchange('occupation_id')
    def _onchange_occupation_id_wrapper(self):
        self.occupation_detail = False

    occupation_detail = fields.Char(
        string=u'Ocupación detalles', track_visibility='always')
    residence_country_id = fields.Many2one(
        'res.country', string=u'Residencia',
        ondelete='restrict', track_visibility='always',
        default=lambda self: self.env.user.employee_id.country_id or self.env.company.country_id)
    residence_condition = fields.Selection(
        string=u'Condición de residencia',
        selection=[('1', 'Residente'), ('2', 'No residente')], track_visibility='always')

    code_ciiu_id = fields.Many2one(
        'l10n_pe_sunat.anexo.01', string=u'Codigo CIIU', ondelete='restrict', track_visibility='always')

    corporation_purpose = fields.Char(
        string=u'Objeto Social', track_visibility='always')
    remark = fields.Text(string=u'Observaciones', track_visibility='always')

    date_sunat_registration = fields.Date(
        string=u'F. Inscrip. Sunat', default=fields.Date.context_today)
    contrib_state = fields.Selection(
        string=u'Estado del Contribuyente',
        selection=[('Activo', 'Activo'), ('Baja', 'Baja'), ],)
    contrib_condition = fields.Selection(
        string=u'Condicion del Contribuyente',
        selection=[('SiHab', 'Habido'), ('NoHab', 'No Habido')])

    is_pep = fields.Boolean(string=u'PEPs')

    correspondent_rank = fields.Integer(default=0)

    @api.onchange('firstname', 'lastname', 'motherlastname')
    def get_complete_name(self):
        lis = list()
        for rec in self:
            lis.append(rec.lastname or '')
            lis.append(rec.motherlastname or '')
            lis.append(rec.firstname or '')
        rec.name = ' '.join(lis).title()

    def name_get(self):
        result = []
        for table in self:
            if table.customer_rank > 0 or table.supplier_rank > 0:
                result.append((table.id, "%s %s" %
                              (table.vat, table.name or '')))
            else:
                result.append((table.id, "%s" % (table.name or '')))
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

    @api.depends('vat', 'name')
    def name_get(self):
        result = []
        for table in self:
            if table.customer_rank > 0 or table.supplier_rank > 0:
                l_name = table.vat and table.vat + ' - ' or ''
                l_name += table.name or ''
            else:
                l_name = table.name or ''
            result.append((table.id, l_name))
        return result

    @api.model
    def create(self, values):
        values['firstname'] = (values.get('firstname', False) or '').title()
        values['lastname'] = (values.get('lastname', False) or '').title()
        values['motherlastname'] = (values.get(
            'motherlastname', False) or '').title()
        result = super(ResPartner_Inherit, self).create(values)
        return result

    """
    Desarrollador: Mauro Quinteros
    Cambios: Variable para la fecha de caducidad del documento
    """
    date_expiration = fields.Date(string="Fecha de Caducidad")

    """
    Desarrollador: Mauro Quinteros
    Cambios: Modificar la forma en como se genera el valor de la variable display_name
    """
    def write(self, values):
        for rec in self:
            if rec.customer_rank > 0 or rec.supplier_rank > 0:
                vat = rec.vat or ""
                name = values.get('name', rec.name).strip() or ""
                display_name = f"{vat} - {name}"
                values['display_name'] = display_name
        return super(ResPartner_Inherit, self).write(values)

    @api.onchange('is_company')
    def onchange_is_company_wrapper(self):
        for partner in self:
            partner.l10n_latam_identification_type_id = self.env.ref(
                'l10n_pe.it_DNI').id if partner.company_type == 'person' else self.env.ref('l10n_pe.it_RUC').id

    def _compute_company_type(self):
        for part in self:
            if part.company_type == False and part.id == False:
                part.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_DNI').id
        return super(ResPartner_Inherit, self)._compute_company_type()

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar relación y onchange para actualizar la vista de afiliación del cliente dependiendo del régimen de Jet Perú
    """
    regime_type = fields.Char(string="Régimen General/Simplificado")

    @api.onchange("regime_type")
    def check_regime_type(self):
        if self.env.company.regime_type == 'general':
            self.regime_type = self.env.company.regime_type
        elif self.env.company.regime_type == 'simplified':
            self.regime_type = self.env.company.regime_type
        else:
            self.regime_type = ""

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar relación para el histórico de beneficiarios
    """
    beneficiary_ids = fields.Many2many(
        comodel_name="res.partner.beneficiary",
        string="Histórico de Beneficiarios",
        relation="res_partner_beneficiary_rel",
        column1="res_partner_id",
        column2="res_partner_beneficiary_id"
    )


class ResCountry_Inherit(models.Model):
    _inherit = ['res.country']

    code_reference = fields.Char(string=u'Código de referencia')

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar funciones para buscar por el código o el nombre de un País
    """
    @api.depends("name", "code_reference")
    def name_get(self):
        result = []
        for record in self:
            code_reference = f"{record.code_reference} - " or ""
            name = record.name or ""
            display_name = code_reference + name
            result.append((record.id, display_name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('code_reference', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        ids = self._name_search(name, args, operator, limit=limit)
        return self.browse(ids).sudo().name_get()


class ResCountryState_Inherit(models.Model):
    _inherit = ['res.country.state']

    code_reference = fields.Char(string=u'Código de referencia', size=4)


class ResBank_Inherit(models.Model):
    _inherit = ['res.bank']

    name_complete = fields.Char(string=u'Nombre Completo')
    owner = fields.Char(string=u'Propietario')
    presence_in_ids = fields.Many2many('res.country', string=u'Presencia en')

    def name_get(self):
        """
            change the displayed value on m2o
        """
        result = []
        for record in self:
            result.append((record.id, ("%s - %s") %
                          (record.name, record.name_complete)))
        return result


class ResPartnerCategory_Inherit(models.Model):
    _inherit = ['res.partner.category']

    keycode = fields.Char(string=u'Palabra Clave')


class ResPartnerBank_Inherit(models.Model):
    _inherit = ['res.partner.bank']

    @api.model
    def _get_supported_account_types(self):
        return [('bank', _('Normal')), ('interbank', _('InterBancario'))]

    country_id = fields.Many2one(
        'res.country', string=u'Pais', default=lambda self: self.env.company.country_id)

    def get_list_profiles(self, type_acc=''):
        list = []
        for ox in self.env['res.partner.bank.profile'].search([('type', '=', type_acc)], order="id ASC"):
            list.append((ox.value, ox.name))
        return list

    account_type = fields.Selection(
        string=u'Tipo Cta Operaciones', selection=lambda x: x.env['res.partner.bank'].get_list_profiles('operative'))
    account_type_bank = fields.Selection(
        string=u'Tipo Cta Cliente', selection=lambda x: x.env['res.partner.bank'].get_list_profiles('personal'), default="acc_saving")
    acc_holders_name = fields.Char(string=u'Titulares de la cuenta')
    pool_account = fields.Boolean(string=u'Cuenta mancomunada', default=False)

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar campo para el número de cuenta interbancaria
    """
    cci_acc_number = fields.Char(string="Cuenta Interbancaria")

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, ("%s: (%s) %s") % (
                record.bank_id.name, record.currency_id.symbol, record.acc_number)))
        return result

    @api.onchange('pool_account')
    def onchange_pool_account(self):
        self.acc_holders_name = ', '.join(
            record.name for record in self.partner_id)

    @api.onchange('account_type')
    def _onchange_account_type_wrapper(self):
        self.businnes_line_id = ""
        self.sale_channel_id = ""

    @api.model
    def create(self, values):
        holder = self.partner_id.browse(values['partner_id']).name
        values['acc_holder_name'] = str(holder)
        result = super(ResPartnerBank_Inherit, self).create(values)
        return result


class ResCompany(models.Model):
    _inherit = ['res.company']

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar variable al res.company para el manejo del régimen general o simplificado
    """
    regime_type = fields.Selection(
        string="Régimen",
        selection=baseval.regime_type,
        default="general",
    )
