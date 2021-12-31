# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, AccessError, ValidationError

class HRConditionLabor(models.Model):
    _name = "hr.contract.condition.labor"
    _description = "Tipo De Condicion Laboral Empleados"
    _rec_name = "sequence"
    
    sequence = fields.Char(string=u"Código de Secuencia",default="/",readonly=True)
    name = fields.Char(string='Nombre')
    company_id = fields.Many2one(string='company',comodel_name='res.company',required=True,default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string='active',default=True)
    
    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------
    @api.model
    def create(self, values):
        if values.get("sequence", "/") == "/":
            seq = self.env["ir.sequence"]
            values["sequence"] = (seq.next_by_code("hr.contract.condition.sequence") or "/")
        result = super(HRConditionLabor, self).create(values)
        return result