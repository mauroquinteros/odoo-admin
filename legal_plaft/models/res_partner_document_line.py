# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta
from decimal import Decimal
import calendar
import pytz
import re
from odoo.osv import expression


class CustomerDocument(models.Model):
    _name = 'res.partner.document.line'
    _description = 'Documentos de identidad asociados al cliente'
    _rec_name = "number_document"

    customer_id = fields.Many2one('res.partner', 'Cliente', ondelete='cascade')

    type_doc_id = fields.Many2one(
        comodel_name='l10n_latam.identification.type',
        string='Tipo de Documento', ondelete='restrict')
    number_document = fields.Char(string=u'Número de Documento')
    date_expiration = fields.Date(string=u'Fecha de Caducidad')
    image_document = fields.Binary(
        "Adjuntar Imagen",
        attachment=True, track_visibility='always')
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Adjuntar Archivo(s)',
        track_visibility='always')
    remark = fields.Text(string=u'Observaciones')
    doc_main = fields.Boolean(string=u'Documento Principal')
    active = fields.Boolean(string=u'active', default=True)

    @api.constrains('doc_main')
    def _check_doc_main(self):
        principaldoc = self.search(
            ['&', ('customer_id', '=', self.customer_id.id), ('doc_main', '=', 'True')])
        if len(principaldoc) > 1:
            raise ValidationError(
                'Solo se puede tener un documento principal! Por favor elimina uno')

    _sql_constraints = [
        ('number_document', 'UNIQUE (type_doc_id,number_document)', 'Número de Documento debe ser Único')]

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar el domain para que solo permita agregar documentos de tipo DI y EXP
    """
    @api.onchange("type_doc_id")
    def _onchange_di_document_ids(self):
        category_acronym = ["DI", "EXP"]
        res = {}

        res["domain"] = {
            "type_doc_id": [
                ("documentcategory_ids.acronym", "in", category_acronym)
            ]
        }
        return res

    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar la variable date_expiration para actualizarlo en el customer_id
    """
    @api.model
    def create(self, values):
        result = super(CustomerDocument, self).create(values)
        for record in result:
            if record.doc_main is True:
                record.customer_id.sudo().update({
                    'display_name': str(values['number_document']) + " - " + record.customer_id.name,
                    'l10n_latam_identification_type_id': values['type_doc_id'],
                    'vat': values['number_document'],
                    'date_expiration': values['date_expiration']
                })
        return result

    """
    Desarrollador: Mauro Quinteros
    Cambios: Modificar para que se considere primero el values.get('field') con la finalidad de que se pueda actualizar correctamente
    """

    def write(self, values):
        for record in self:
            if record.doc_main is True:
                record.customer_id.sudo().write({
                    'display_name': values.get('number_document', record.number_document) + " - " + record.customer_id.name,
                    'l10n_latam_identification_type_id': values.get('type_doc_id', record.type_doc_id.id),
                    'vat': values.get('number_document', record.number_document),
                    'date_expiration': values.get('date_expiration', record.date_expiration)
                })
        result = super(CustomerDocument, self).write(values)
        return result

    def unlink(self):
        for record in self:
            if record.doc_main is True:
                record.customer_id.sudo().write({
                    'display_name': record.customer_id.name,
                    'l10n_latam_identification_type_id': False,
                    'vat': False,
                    'date_expiration': False
                })
        res = super(CustomerDocument, self).unlink()
        return res
