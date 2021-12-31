# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

from odoo.addons.account_treasury.models.utils import values as val

class Glossary(models.Model):
        
    _name = 'ir.glossary'
    _description = 'Glosario para la transformación de datos'
    
    sequence = fields.Char(string=u'Secuencia',default="/",readonly=True)
    name = fields.Char(string='Nombre')
    state = fields.Selection(selection=[('simple', 'Simple'),('relational', 'Datos Relacionales')], string='Modo', required=True, readonly=False, copy=False, tracking=True,default='simple')
    model_id = fields.Many2one(string='Modelo Relacionado',comodel_name='ir.model',ondelete='set null',domain=[('model','in',val.models)])
    homologant_ids = fields.One2many(string='Glosario Homologante',comodel_name='ir.glossary.homologant',inverse_name='subglossary_id')
    company_id = fields.Many2one(string='Company',comodel_name='res.company',required=True,default=lambda self: self.env.user.company_id,)
    active = fields.Boolean(string='active',default=True)
    
    @api.model
    def create(self, values):
        if values.get("sequence", "/") == "/":
            seq = self.env["ir.sequence"]
            values["sequence"] = seq.next_by_code("ir.glossary.sequence") or "/"
        result = super(Glossary, self).create(values)
        return result
    
class SubGlossaryHomologant(models.Model):
    _name = 'ir.glossary.homologant'
    _description = 'Líneas para registros homologantes del Glosario'
    
    sequence = fields.Char(string=u'Código de Secuencia',default="/",readonly=True)
    subglossary_id = fields.Many2one(string='Relación al glosario',comodel_name='ir.glossary')
    init_key = fields.Char(string='Data Cruda')
    field_key = fields.Char(string='Campo Clave')    
    final_key = fields.Char(string='Data Codificada')
    model_id = fields.Many2one(string='Modelo Aplicado',comodel_name='ir.model',ondelete='set null',domain=[('model','in',val.models)])
    relation_id = fields.Reference(val.modelist,string="Resultado Homologado")
    company_id = fields.Many2one(string='Company',comodel_name='res.company',required=True,default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string='active',default=True)
    
    @api.model
    def create(self, values):
      if values.get("sequence", "/") == "/":
          seq = self.env["ir.sequence"]
          values["sequence"] = seq.next_by_code("ir.glossary.homologant.sequence") or "/"
      
      try:
        value = self.env.ref(values["final_key"],False)
        values.update({'relation_id':'%s,%s' % (value._name, value.id),})
      except:
        pass
      
      result = super(SubGlossaryHomologant, self).create(values)
      return result