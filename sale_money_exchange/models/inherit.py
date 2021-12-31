# -*- coding: utf-8 -*-
    ###############################################################################
    #    License, author and contributors information in:                         #
    #    __manifest__.py file at the root folder of this module.                   #
    ###############################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError

class inherit_users(models.Model):
    _inherit = ['res.users']
    
    @api.depends('name', 'ref')
    def name_get(self):
        result = []
        for record in self:
            if record.ref:
                name = '[' + record.ref + '] ' + record.name
            else:
                name = record.name
            result.append((record.id, name))
        return result