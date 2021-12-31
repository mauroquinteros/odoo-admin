# -*- coding: utf-8 -*-
    ###############################################################################
    #    License, author and contributors information in:                         #
    #    __manifest__.py file at the root folder of this module.                  #
    ###############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta
import pytz
import operator

class InheritIrSequence(models.Model):
    _inherit = ['ir.sequence']

    implementation = fields.Selection(selection_add=[
        ('custom', 'Personalizado'),
        ('regular', 'Regular'),
        ('CustomSequence', 'Secuencia Personalizada'),
        ('CustomSerie', 'Serie Personalizada')
        ])

class InheritIrCron(models.Model):
    _inherit = ['ir.cron']

    module_ext_id = fields.Many2one('ir.modules.extension',string=u'Módulo General')


class ModulesForCron(models.Model):
    _name = 'ir.modules.extension'
    _description = 'Tabla de Módulos para a identificación de Tareas Automatizadas'

    name = fields.Char(string=u'Nombre')
    default = fields.Boolean(string=u'Por Defecto')
    company_id = fields.Many2one('res.company',string=u'Compañia',required=True,
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string=u'active')