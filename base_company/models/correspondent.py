# -*- coding: utf-8 -
from datetime import datetime

from odoo import api, fields, models
from odoo.addons.base_company.models.utils import values as val
from odoo.addons.l10n_pe_currency.models.utils import values as curval
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression


class ResPartnerCorrespondent(models.Model):
    _name = "res.partner.correspondent"
    _description = "Tabla de Corresponsales"
    _inherits = {"res.partner": "partner_id"}

    """
    Desarrollador: Mauro Quinteros
    Cambios: Definir el modelo de res.partner.correspondent
    """
    partner_id = fields.Many2one(
        "res.partner", string="partner_id", required=True, ondelete="cascade"
    )
    internal_code = fields.Char(string="Código del corresponsal", required=True)
    short_name = fields.Char(string="Nombre abreviado")
    display_name = fields.Char(
        compute='_compute_display_name',
        string="Nombre",
        store=True
    )

    correspondent_type = fields.Selection(
        string="Tipo",
        selection=val.correspondent_type_use,
        default="pagador",
        track_visibility="onchange",
    )
    related_business = fields.Selection(
        string=u"Negocio vinculado",
        selection=val.linked,
        default="novin",
        track_visibility="onchange",
    )
    business_type = fields.Selection(
        string="Tipo de negocio",
        selection=val.business_type_use,
        default="corresponsal",
        track_visibility="onchange",
    )
    state = fields.Selection(
        string="Estado",
        default="activo",
        selection=val.state_use,
        store=True,
        track_visibility="on_change",
    )

    opening_date = fields.Date(string=u"Fecha de apertura", default=fields.Datetime.now)
    inactivity_date = fields.Date(string=u"Fecha de inactividad")
    deadline_date = fields.Date(string=u"Fecha de cierre")
    operation_observation = fields.Text(string="Observaciones")

    country_id = fields.Many2one("res.country", string="País")
    state_id = fields.Many2one(
        "res.country.state",
        string="Estado",
        domain="[('country_id', '=?', country_id)]",
    )
    agency_ids = fields.One2many(
        "res.partner.agency", inverse_name="correspondent_id", string="Agencias"
    )

    def write(self, values):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Agregar el valor del display_name formado pro el name y el internal_code
        """
        for rec in self:
            internal_code = values.get('internal_code', rec.internal_code) or ""
            name = values.get('name', rec.name).strip() or ""
            display_name = f"{internal_code} - {name}"
            values['display_name'] = display_name
        return super(ResPartnerCorrespondent, self).write(values)

    @api.depends("name", "internal_code")
    def name_get(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Agregar la estructura de código interno y nombre al buscar un corresponsal
        """
        result = []
        for record in self:
            internal_code = f"{record.internal_code} - " or ""
            name = record.name or ""
            display_name = internal_code + name
            result.append((record.id, display_name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Buscar por el código o el nombre de un corresponsal
        """
        args = list(args or [])
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('internal_code', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Retornar la función padre de búsqueda
        """
        ids = self._name_search(name, args, operator, limit=limit)
        return self.browse(ids).sudo().name_get()

    def update_correspondent_state(self, state):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Funciones para manejar los estados de un corresponsal y sus agencias (inactivo y cerrado)
        Argumentos: state (type string)
        """
        if state == "activo":
            self.inactivity_date = False
            self.deadline_date = False
            for agency in self.agency_ids:
                agency.state = "activo"
        elif state == "inactivo":
            self.inactivity_date = fields.Datetime.now
            for agency in self.agency_ids:
                agency.state = "inactivo"
        elif state == "cerrado":
            self.deadline_date = fields.Datetime.now
            for agency in self.agency_ids:
                agency.state = "cerrado"

    @api.onchange("state")
    def _onchange_state(self):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Actualizar el estado del corresponsal y sus agencias según el estado seleccionado
        """
        if self.state is not False:
            self.update_correspondent_state(self.state)
