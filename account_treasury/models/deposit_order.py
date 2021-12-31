# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api,exceptions, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime,timedelta
import pytz
import calendar
import base64

from odoo.addons.account_treasury.models.utils import methods as treasury_methods
from odoo.addons.technical_customizer.models.utils import methods as technical_methods

class SaleCustomerDeposit(models.Model):
    _name = 'deposit.order'
    _description = 'Orden de depósito'
    _rec_name = 'partner_id'
    _order = 'sale_order_id DESC'
    _inherit = ["mail.thread","mail.activity.mixin"]

    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta')
    pay_order_id = fields.Many2one('pay.order', string='Orden de Pago')

    partner_id = fields.Many2one('res.partner',string='Dirigido a',track_visibility='always')
    type = fields.Selection(string='Tipo',selection=[('A-I', 'Ingreso - Depósito'), ('B-E', 'Egreso - Abonar')],track_visibility='always')

    paymethod_id = fields.Many2one('account.payment.method', string=u'Forma de pago', domain=[('code','in',['54725','75395','14789','36475','98653'])],required=True, track_visibility='always',default=lambda self: self.env.ref('sale_config.rec_paymentmethod_2'))

    agency_id = fields.Many2one('res.partner.agency', string=u'Agencia',default=lambda self: self.env.user.agency_id,track_visibility='always')

    origin_account_bank_id = fields.Many2one('res.partner.bank',string=u'Origen Banco y Cta',track_visibility='always',
                                            domain=lambda self: self._get_acc_origin_bank_domain())
    origin_acc_holder_names = fields.Char(string="Titular(es)",related='origin_account_bank_id.acc_holders_name')

    destination_account_bank_id = fields.Many2one('res.partner.bank',string=u'Destino Banco y Cta',track_visibility='always',
                                            domain=lambda self: self._get_acc_destination_bank_domain())
    destination_acc_holder_names = fields.Char(string="Titular(es)",related='destination_account_bank_id.acc_holders_name')

    reference_deposit = fields.Char(string=u'N° Referencia',track_visibility='always')
    date_deposit = fields.Datetime(string=u'Fecha Operación',default=fields.Datetime.now,required=True,track_visibility='always')
    currency_id = fields.Many2one('res.currency',string='Moneda')
    amount_deposit = fields.Float(string=u'Monto depositado',digits=(11, 2),track_visibility='always')
    amount_payable = fields.Float(string=u'Monto a pagar', digits=(11, 2),track_visibility='always')
    image = fields.Binary("Adjuntar Imagen", attachment=True, track_visibility='always')
    attachment_ids = fields.Many2many('ir.attachment', string='Adjuntar Archivo(s)',track_visibility='always')
    block = fields.Boolean(string='Campo Blocker',default=False)
    state = fields.Selection(string='Estado', selection=[('unchecked', 'Pendiente'), ('deposit', 'Depósito Confirmado'), ('pre-acredit', 'Pre abono'), ('acredit', 'Abono Cliente'), ('cancel', 'Cancelado')],track_visibility='always')

    company_id = fields.Many2one(string='Company', comodel_name='res.company', required=True, default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string='active',default=True)

    @api.onchange('destination_account_bank_id')
    def _get_amount_deposit(self):
        if self.type == 'A-I':
            # self.amount_deposit = self.env.context['origin_import'] - self.env.context['total_deposit']
            import pdb; pdb.set_trace()
            return {"domain": {"account_bank_id": [
                '&',
                ("partner_id", "=", self.env.user.company_id.partner_id.id),
                ("currency_id.name", "=", self.currency_id.name)
                ]}}
        else:
            return {"domain": {"account_bank_id": [
                '&',
                ("partner_id", "=", self.sale_order_id.partner_id.id),
                ("currency_id.name", "=", self.currency_id.name)
                ]}}
            if self.env.context['origin_import'] != self.env.context['total_deposit']:
                self.amount_deposit = self.env.context['origin_import'] - self.env.context['total_deposit']

    @api.onchange('origin_account_bank_id')
    def _get_amount_payable(self):
        if self.type == 'B-E':
            if self.env.context['destination_import'] != self.env.context['total_acredit']:
                self.amount_payable = self.env.context['destination_import'] - self.env.context['total_acredit']

    def _get_acc_origin_bank_domain(self):
        """
        Descripción: Obtener las cuentas de banco origen según el tipo de deposito, moneda y persona titular de la cuenta
        """
        if self._context.get('default_type', False) == 'A-I':
            return [("partner_id", "=", self._context.get('default_partner_id', False)),("currency_id", "=", self._context.get('default_currency_id', False))]
        elif self._context.get('default_type', False) == 'B-E':
            return[("partner_id", "=", self.env.user.company_id.partner_id.id),("currency_id", "=", self._context.get('default_currency_id', False))]

    def _get_acc_destination_bank_domain(self):
        """
        Descripción: Obtener las cuentas de banco destino según el tipo de deposito, moneda y persona titular de la cuenta
        """
        if self._context.get('default_type', False) == 'A-I':
            return[("partner_id", "=", self.env.user.company_id.partner_id.id),("currency_id", "=", self._context.get('default_currency_id', False))]
        elif self._context.get('default_type', False) == 'B-E':
            return [("partner_id", "=", self._context.get('default_partner_id', False)),("currency_id", "=", self._context.get('default_currency_id', False))]


    @api.constrains('reference_deposit')
    def _check_reference_deposit(self,query=[('id','=',0)]):
        if self.reference_deposit is not False:
            query = ['&',('reference_deposit','=',self.reference_deposit),('origin_account_bank_id','=',self.origin_account_bank_id.bank_id.id)]
        if len(self.search(query))>1:
            raise ValidationError("Ya existe el numero de referencia '%s' asociado a una operación" %(self.reference_deposit))


    @api.onchange('account_bank_id')
    def _get_amount_payable(self):
        if self.type == 'B-E':
            self.amount_payable = self.env.context['destination_import'] - self.env.context['total_acredit']

    def action_open_deposit(self):
        comment = self._context.get("comment",False)
        mode = self._context.get("mode",False)
        if comment is not False and mode is not False:
            technical_methods.dynamic_notify(self,comment,mode)
        view = treasury_methods.open_current(self,'account_treasury.treasury_acredit_order_view_form')
        return view

    def action_open_document(self):
        view = treasury_methods.open_current(self.sale_order_id,'sale_money_exchange.moex_sale_order_view_form')
        return view

    def action_cancel_deposit(self):
        self.sudo().write({'state':'cancel'})

    def action_confirm_deposit(self,val={},msg=False,mode=False,display_msg= """"""):
        if self.type == 'A-I':
            if self.sale_order_id.state == 'deposit':
                if treasury_methods.PO_review_existing(self, self.sale_order_id):
                    self.sale_order_id.sudo().trigger_generate_payorder()
                    display_msg += self.env.ref('sale_money_exchange.mt_check_deposit_done').description
                    display_msg += """ <br/> """
                    display_msg += """de la orden %s el dinero está en la cuenta de %s""" %(self.sale_order_id.name,self.env.user.company_id.name)
            else:
                msg = '⚠️ La Cotización no está en etapa de revisión de depósitos, verificar con el vendedor porfavor.'
                mode = 'warning'
        elif self.type == 'B-E':
            if self.reference_deposit == False:
                msg = 'Primero debe de Ingresar el N° de Ref. de la Operación.'
                mode = 'info'
            orders = self.search(['&',('type','=','A-I'),('sale_order_id','=',self.sale_order_id.id)])
            display_msg += """ - Se ha realizado el pre-abono (primera firma)"""
            for order in orders:
                if order.state != 'deposit':
                    raise ValidationError ('Uno o más depósitos no han sido confirmados, revisar su bandeja de pendientes.')
        if type(msg) is bool and type(mode) is bool:
            val.update({'block': True,'state': self.env.context.get('statkey')})
            self.write(val)
            self.sale_order_id.sudo().message_post(body=display_msg)
        else:
            technical_methods.dynamic_notify(self,comment=msg,mode=mode)

    def do_mark_line(self,display_msg= """"""):
        if self.env.user.has_group('account_treasury.group_financial_treasury_payer'):
            self.sudo().write({"state": self._context.get("state")})
        else:
            self.write({"state": self._context.get("state")})
        if self._context.get("state") == 'acredit':
            display_msg= """Esta línea de pago ha sido confirmada para abonar"""
        elif self._context.get("state") == 'cancel':
            display_msg= """Esta línea de pago ha sido Cancelada"""
        self.pay_order_id.sudo().message_post(body=display_msg)

    # def action_confirm_acredit(self,val={},msg=False,mode=False,display_msg= """"""):
    #     if self.type == 'B-E':
    #         display_msg += """ - Se ha realizado el abono al cliente (segunda firma)"""
    #         self.sale_order_id.sudo().message_post(body=display_msg)
    def _track_subtype(self, init_values):
        # OVERRIDE to add custom subtype depending of the state.
        self.ensure_one()
        if 'state' in init_values and self.state == 'deposit' and self.type == 'A-I':
            return self.env.ref('account_treasury.mt_deposit_order_done')
        elif 'state' in init_values and self.state == 'pre-acredit' and self.type == 'B-E':
            return self.env.ref('account_treasury.mt_pre_acredit_order_done')
        return super(SaleCustomerDeposit, self)._track_subtype(init_values)
