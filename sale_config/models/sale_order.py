# -*- coding: utf-8 -*-
##########################################################################
#    License, author and contributors information in:                    #
#    __manifest__.py file at the root folder of this module.             #
#           models related to TRAYBOOK services                          #
##########################################################################

from datetime import datetime, timedelta
from collections import defaultdict

from odoo import api, fields, models, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round


class SaleOrderConfigTreasury(models.Model):
    _inherit = "sale.order"

    pcl_requirement_ids = fields.One2many(
        comodel_name='requirement.pcl', inverse_name='sale_order_id', string='Requerimientos PCL')

    def utr_action_cancel(self):
        # When a treasury person cancel a SO, he might not have the rights to write
        # on SO. But we need the system to create an activity on the SO (so 'write'
        # access), hence the `sudo`.
        if self.env.user.has_group('account_treasury.group_financial_treasury_assistant'):
            self.sudo().action_cancel()
        else:
            comment = self.env['ir.config_parameter'].sudo(
            ).get_param('exception.sale.111')
            treasury_group = self.env.ref(
                'account_treasury.group_financial_treasury_assistant')
            raise exceptions.ValidationError(comment % treasury_group.name)

    def action_multi_step(self):
        if self._context.get('state', False) == 'valid':
            self.sudo().write({'state': self._context.get('state')})
            return self.env.ref('sale_config.treasury_moex_quote_tc_online_action').read()[0]

    def trigger_generate_payorder(self):
        if self.env.user.agency_id.id != False:
            payorder = {
                'order_date': self.date_order,
                'payment_date': fields.Datetime.now(),
                'origin_currency_id': self.origin_currency_id.id,
                'destination_currency_id': self.destination_currency_id.id,
                'origin_amount': self.origin_import,
                'destination_amount': self.destination_import,

                'official_rate': 0.0,
                'operative_rate': self.operative_rate,
                'proposed_rate': self.proposed_rate,
                'approved_rate': self.approved_rate,

                'amount_equivalent_dol': self.origin_import,

                'business_line_id': self.env.ref('base_company.business_line_001').id,
                'channel_id': self.business_channel_id.id,
                'channel_type': self.business_channel_id.channel_type,
                'operative_agency_id': self.env.user.agency_id.id,
                'operation_ref': '%s,%s' % (self._name, self.id),

                'res_partner_id': self.partner_id.id,

                'state': 'searched'
            }
            self.env['pay.order.money.exchange'].create(payorder)
        else:
            raise exceptions.ValidationError(
                'Este usuario no tiene una agencia asignada')
