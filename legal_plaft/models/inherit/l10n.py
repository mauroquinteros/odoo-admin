
from odoo import models, fields, api, exceptions, _

class l10n_latam_identification_type_inherit(models.Model):
    _inherit = ['l10n_latam.identification.type']
    
    nomenclature = fields.Char(size=5)
    shortletter = fields.Char(string=u'Letra Abreviatura')
    remark = fields.Text('Observaciones')
    sunat_code = fields.Char('Codigo SUNAT')
    acla_code = fields.Char('Codigo ACLA')
    sbs_code = fields.Char('Codigo de SBS')
    documentcategory_ids = fields.Many2many('plaft.document.category', string=u'Categorías')
    company_id = fields.Many2one('res.company', 'company', required=True, default=lambda self: self.env.user.company_id)

    _sql_constraints = [ 
        # parameters:
        # constraint unique identifier
        # constraint SQL sintax
        # validation message
        ('name_unique', 
        'UNIQUE (name)', 
        'Nombre del requisito debe ser único.')
    ]

    #@api.constrains('name')
    #def _check_name_is_lower(self):
    #    for req in self:
    #        if req.name.lower():
    #            raise ValidationError('Sólo se permiten mayúsculas.')

    # @api.onchange('name')
    # def onchange_name(self):
    #     self.name = self.name.lstrip(' ')
    #     self.name = self.name
    #     return