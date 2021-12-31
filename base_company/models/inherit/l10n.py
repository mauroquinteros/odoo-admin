# -*- coding: utf-8 -*-
    ###############################################################################
    #    License, author and contributors information in:                         #
    #    __manifest__.py file at the root folder of this module.                   #
    ###############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta
import pytz
import operator

class CIIU_Sunat_Inherit(models.Model):
    _inherit = ['l10n_pe_sunat.anexo.01']

    plaftrisk_id = fields.Many2one('plaft.risk',string=u'Riesgo LA/FT',
        default=lambda self: self.env.ref('legal_plaft.plaft_risk_001',False).id,
        help="Riesgo asignado al factor de riesgo tipo de compañia")