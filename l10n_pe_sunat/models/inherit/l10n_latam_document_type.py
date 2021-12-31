# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class L10nLatamDocumentType(models.Model):

    _inherit = 'l10n_latam.document.type'

    internal_type = fields.Selection(
        selection_add=[
            ('quoation', 'Quoation Order'),('invoice',),
            ('invoice_in', 'Purchase Invoices'),('debit_note',),
            ('receipt_invoice', 'Receipt Invoice'),('invoice_in',),
            ('payorder', 'Payment Order'),('receipt_invoice',),
            ])

    def _get_document_sequence_vals(self, journal):
        values = super(L10nLatamDocumentType, self)._get_document_sequence_vals(journal)
        if self.country_id != self.env.ref('base.pe'):
            return values
        values.update({
            'padding': 6,
            'implementation': 'no_gap',
            'l10n_latam_document_type_id': self.id,
            'prefix': None
        })
        return values

    # def _filter_taxes_included(self, taxes):
    #     """ In Chile we include taxes in line amounts depending on type of document.
    #     This serves just for document printing purposes """
    #     self.ensure_one()
    #     if self.country_id == self.env.ref('base.pe') and self.code in ['39', '41', '110', '111', '112', '34']:
    #         return taxes.filtered(lambda x: x.tax_group_id == self.env.ref('l10n_pe.tax_group_ivap'))
    #     return super()._filter_taxes_included(taxes)
