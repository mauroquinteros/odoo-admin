
from odoo import models, fields, api, exceptions, _
from odoo.tools import image_process, ustr


class ResCountry_Inherit(models.Model):
    _inherit = ['res.country']

    plaftrisk_id = fields.Many2one('plaft.risk', string=u'Riesgo LA/FT')
    fiscal_paradise = fields.Boolean(string=u'Paraíso Fiscal', default=False)
    image_payment_form = fields.Binary(
        "Image displayed on the payment form", attachment=True, compute='_compute_image')

    def _compute_image(self):
        for vals in self:
            if vals.image_payment_form is False:
                image = ustr(vals.image or '').encode('utf-8')
                vals.image_payment_form = image_process(image, size=(45, 30))


class ResCountryState_Inherit(models.Model):
    _inherit = ['res.country.state']

    plaftrisk_id = fields.Many2one('plaft.risk', string=u'Riesgo LA/FT')


class ResCurrency(models.Model):
    _inherit = ['res.currency']

    plaftrisk_id = fields.Many2one('plaft.risk', string=u'Riesgo LA/FT')

    def name_get(self):
        """
            change the displayed value on m2os
        """
        result = []
        for record in self:
            result.append((record.id, ("%s-%s: (%s)") %
                          (record.name, record.currency_unit_label, record.symbol)))
        return result


class ResPartner_Inherit(models.Model):
    _inherit = ['res.partner']

    """
    Desarrollador: Mauro Quinteros
    Cambios: Todos los documentos deben ir dentro de di_document_ids. Eliminé la relación que hay entre res.partner y exp_document_ids porque ambos apuntan al mismo modelo, es mejor manejar todos los documentos, incluido el documento principal, en una sola relación.
    """
    di_document_ids = fields.One2many(
        comodel_name='res.partner.document.line',
        inverse_name='customer_id', string='Documentos de Identidad', track_visibility='always')

    exp_document_ids = fields.One2many(
        'res.partner.document.line', 'customer_id', 'Documentos de Identidad',
        track_visibility='always', domain=[('type_doc_id.documentcategory_ids.acronym', '=', 'EXP')])

    civil_status_id = fields.Many2one(
        comodel_name='plaft.status.civil.list', string='Estado Civil',
        default=lambda self: self.env.ref('legal_plaft.civ_stat_002', False), track_visibility='always')

    position_id = fields.Many2one(
        'plaft.position', string=u'Cargo', ondelete='restrict', track_visibility='always')

    regime_id = fields.Many2one(
        'plaft.regimen', string=u'Tipo de Régimen', ondelete='restrict', track_visibility='always')

    plaft_documentation_id = fields.Many2one(
        'plaft.documentation.type', string=u'Documentación', ondelete='restrict')

    @api.model
    def create(self, values):
        value = {
            'di_document_ids': [(0, False, {
                'type_doc_id': values.get('l10n_latam_identification_type_id', False),
                'number_document': values.get('vat', False),
                'date_expiration': values.get('date_expiration', False),
                'doc_main': True,
                'active': True
            })]
        }
        values.update(value)
        result = super(ResPartner_Inherit, self).create(values)
        return result
