# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################

from odoo.addons.l10n_pe_currency.models.utils import values as curval
from odoo.exceptions import ValidationError

import string


def _objects_undermodel(self, origin=False, destination=False, agency=False):
    # receive always origin and destination currency object extended in self
    # receive always agency object of user uid
    agency = self.env.user.agency_id
    if self._name == 'sale.order':
        # model sale.order accept with fields for inherit
        origin = self.origin_currency_id
        destination = self.destination_currency_id
    if self._name == 'assistant.remittance.price':
        origin = self.origin_currency_id
        destination = self.local_currency_id
    return {'origin': origin, 'destination': destination, 'agency': agency}


def devolve_query_calculation(self, Constant='*', Number=0):
    obj = _objects_undermodel(self)
    SELECT_FROM = """SELECT %s FROM res_currency_moex_calculation """
    WHERE = """WHERE origin_currency_id=%s AND destination_currency_id=%s"""
    cr = self.env.cr
    cr.execute(SELECT_FROM % (Constant) + WHERE %
               (obj['origin'].id, obj['destination'].id))
    return cr.dictfetchall()[Number]


def devolve_query_exrate(self, Number=0):
    obj = _objects_undermodel(self)
    query = ['|',
             '&', ('currentactive', '=', True), '&', ('agency_id',
                                                      '=', obj['agency'].id),
             '&', ('origin_currency_id', '=', obj['origin'].id), (
                 'destination_currency_id', '=', obj['destination'].id),
             '&', ('currentactive', '=', True), '&', ('agency_id',
                                                      '=', obj['agency'].id),
             '&', ('origin_currency_id', '=', obj['destination'].id), ('destination_currency_id', '=', obj['origin'].id)]
    return self.env['res.currency.rate.oer'].search(query, limit=Number)


def devolve_query_approvement(self, bsln, chnl, amount):
    obj = _objects_undermodel(self)
    query = ['&', ('agency_id', '=', obj['agency'].id),
             '&', ('origin_currency_id', '=', obj['origin'].id), (
                 'destination_currency_id', '=', obj['destination'].id),
             '&', ('min_amount', '<=', amount), ('max_amount', '>=', amount),
             '&', ('autoapprovement_id.business_line_id.foreign_code', '=',
                   bsln), ('autoapprovement_id.sale_channel_ids', 'in', [c.id for c in chnl])
             ]
    return self.env['res.currency.moex.auto.approvement.line'].search(query)


def currency_rate_exchange(self, origin_currency, agency, destination_currency=False):
    origin = origin_currency
    destination = self.env.ref(
        'base.PEN').id if destination_currency is False else destination_currency
    obj_oer = self.env['res.currency.rate.oer'].search([
        '|', '&', ('origin_currency_id', '=',
                   origin), '&', ('agency_id', '=', agency),
        '&', ('destination_currency_id', '=',
              destination), ('currentactive', '=', True),
        '&', ('origin_currency_id', '=',
              destination), '&', ('agency_id', '=', agency),
        '&', ('destination_currency_id', '=',
              origin), ('currentactive', '=', True),
    ])
    if(obj_oer != False):
        return obj_oer
    raise ValidationError(
        "No existe un tipo de cambio de Dólares/Euros para esa agencia")
