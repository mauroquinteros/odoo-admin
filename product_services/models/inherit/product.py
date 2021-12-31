# -*- coding: utf-8 -*-
    ###############################################################################
    #    License, author and contributors information in:                         #
    #    __manifest__.py file at the root folder of this module.                   #
    ###############################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError

class inherit_product_template(models.Model):
    _inherit = ['product.template']
    business_line_id = fields.Many2one(comodel_name='business.line', string='Línea de Negocio')