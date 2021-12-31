# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################

from odoo import api, fields, models
from datetime import datetime,timedelta
from odoo.exceptions import UserError, AccessError, ValidationError

from odoo.addons.base_company.models.utils import values as val, functions as bcompay_methods

class PartnerToClient(models.TransientModel):
    _name="partner.convert.client"
    _description="Wizard para asignar un contacto a cliente"

    partner_id = fields.Many2one(comodel_name='res.partner', string='Contacto')

    rank_customer_current = fields.Integer(string="Rango Cliente",related='partner_id.customer_rank',readonly=True,store=True)
    rank_supplier_current = fields.Integer(string="Rango Proveedor",related='partner_id.supplier_rank',readonly=True,store=True)

    def action_set_rank(self, data = {}):
        key = self.env.context.get('keys', False).split(',')
        for k in key:
            data.update({k: '1'})
        self.partner_id.write(data)
        bcompay_methods.open_current(self,'base_config.convert_to_client_form_view')