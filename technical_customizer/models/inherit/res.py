# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.addons.technical_customizer.models.utils import values as teval


class InheritResUsers(models.Model):
    _inherit = ['res.users']

    pos_ids = fields.Many2many(
        comodel_name='pos.config', string='Ptos de Venta')

    function = fields.Selection(
        string=u'Función a Cumplir', selection=teval.function_use, default='front')
    agency_id = fields.Many2one(
        'res.partner.agency', string=u'Agencia Asignada')
    profile_id = fields.Many2one('profile.config', string=u'Perfil Operador')

    @api.onchange('function')
    def _onchange_function(self):
        self.agency_id = False
        self.profile_id = False
        self.pos_ids = []
        ftype = self.function
        return {
            'domain': {
                'profile_id': [
                    ('type_pt_use', 'in', [ftype]
                     if ftype != 'both' else ['Pto', 'Ptv'])
                ]
            }
        }

    @api.onchange('agency_id')
    def onchange_agency_id(self):
        if self.function != 'both':
            conditional = [
                '&',
                ('profile_id', '=', self.profile_id.id),
                ('agency_id', '=', self.agency_id.id)
            ]
        else:
            conditional = [('agency_id', '=', self.agency_id.id)]
        self.pos_ids = self.pos_ids.search(conditional)

    @api.model
    def change_agency_get(self):
        if self.env.user.employee_id:
            return self.sudo().env.ref('technical_customizer.action_config_res_user_agency').read()[0]
