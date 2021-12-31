from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo.addons.account_treasury.models.utils import values as valtre
from odoo.addons.account_treasury.models.utils import methods as treasury_methods

class PayOrder(models.Model):
    _name = "pay.order"
    _description = "Ordenes de Pago"
    _rec_name = "sequence"
    _inherit = ["mail.thread","mail.activity.mixin"]

    sequence = fields.Char(string='Código Interno')

    order_date = fields.Datetime(string='F. Operación')
    payment_date = fields.Datetime(string='Fecha de Pago')

    origin_currency_id = fields.Many2one(comodel_name='res.currency',string='Moneda Origen/Enviar')
    destination_currency_id = fields.Many2one(comodel_name='res.currency',string='Moneda Destino/Pagar')
    origin_amount = fields.Float(string='Monto de Origen/Envío',digits=(9, 2))
    destination_amount = fields.Float(string='Monto de Destino/Pago',digits=(9, 2))

    amount_equivalent_dol = fields.Float(string='Monto Equivalente en Dólares',digits=(9, 2))

    official_rate = fields.Float(string='Tasa Oficial',digits=(1, 4),track_visibility='always')
    operative_rate = fields.Float(string='Tasa Operativa',digits=(1, 4),track_visibility='always')
    proposed_rate = fields.Float(string='Tasa Propuesta', digits=(1, 4),track_visibility='always')
    approved_rate = fields.Float(string='Tasa Aprobada', digits=(1, 4),track_visibility='always')

    business_line_id = fields.Many2one(string='Línea de Negocio',comodel_name='business.line')
    channel_id = fields.Many2one(string='Canal',comodel_name='business.channel')
    channel_type = fields.Selection(string='Tipo de Canal',selection=valtre.channel_type)
    operative_agency_id = fields.Many2one(string='Agencia',comodel_name='res.partner.agency')

    res_partner_id = fields.Many2one(comodel_name='res.partner', string='Cliente')

    remark = fields.Html(string='Observaciones')

    parent_id = fields.Many2one(comodel_name='pay.order',string='Recursiva/Op. Mixta Rel')

    operation_ref = fields.Reference(string='Operación',selection=[('sale.order', 'Ordenes de Ventas')])

    deposit_order_ids = fields.One2many(comodel_name='deposit.order', inverse_name='pay_order_id', string='Ordenes de Depósitos')

    state = fields.Selection(string='Estado', selection=[('draft', 'Borrador'), ('searched', 'Para pagar') , ('payed', 'Pagado'), ('cancel', 'Cancelado')],default='draft')
    company_id = fields.Many2one(string='Company', comodel_name='res.company', required=True, default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string='active', default=True)

    def action_open_document(self):
        if self.operation_ref._name == 'sale.order':
            view_name = 'sale_money_exchange.moex_sale_order_view_form'
        view = treasury_methods.open_current(self.operation_ref,view_name)
        return view

    def action_cancel(self):
        self.sudo().write({'state':'cancel'})
        if self.deposit_order_ids.ids != []:
            for dep in self.deposit_order_ids:
                if dep.state == 'pre-acredit':
                    dep.sudo().write({'state': 'cancel'})
                else:
                    raise ValidationError('⚠️ Hay un error con las líneas de pago no están en pre-abonar')
            self.operation_ref.sudo().action_cancel()

    def action_search_pay(self):
        for pay in self.operation_ref.acredit_ids:
            pay.sudo().write({'pay_order_id':self.id})
        if self.deposit_order_ids.ids != []:
            self.sudo().write({'state':'searched'})
        else:
            self.env.user.notify_warning(message='⚠️ No se encontrarón ordenes de depósito, consulte al vendedor si ha realizado los registros correspondientes.')

    def action_record_pay(self):
        num = 0
        for pay in self.operation_ref.acredit_ids:
            if pay.state not in self.env.context.get('state_key'):
                self.env.user.notify_warning(message='⚠️ Todas las líneas de los Pagos deben estar pre-abonadas o abonadas.')
                break
            else:
                num +=1
        if num == len(self.operation_ref.acredit_ids):
            self.ensure_one()
            template_id = self.env['ir.model.data'].xmlid_to_res_id('sale_config.treasury_email_template_edi_acredit', raise_if_not_found=False)
            lang = self.env.context.get('lang')
            template = self.env['mail.template'].browse(template_id)
            if template.lang:
                lang = template._render_template(template.lang, 'pay.order', self.ids[0])
            ctx = {
                'default_model': 'pay.order',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "mail_layout_extra.mail_notification_light",
                'force_email': True,
                'model_description': self.with_context(lang=lang)._description,
            }
            return {
                'name': 'Email de Pago Cliente',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, display_msg= """""", **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            if self.env.user.has_group('account_treasury.group_financial_treasury_payer'):
                for rs in self.deposit_order_ids:
                    rs.sudo().write({'state': 'acredit'})
            else:
                raise ValidationError('Error el usuario actual no puede cambiar las líneas de pago a "abonar", esto ocurre porque no se ha configurado correctamente el rol de usuario.')

            if self.operation_ref.state == 'deposit':
                self.operation_ref.sudo().action_confirm()
                self.operation_ref.sudo().with_context(mail_post_autofollow=False).message_post(**kwargs)
            self.filtered(lambda o: o.state in ['searched']).with_context(tracking_disable=True).sudo().write({'state':'payed'})
        return super(PayOrder,self)

    def _track_subtype(self, init_values):
        import pdb; pdb.set_trace()
        self.ensure_one()
        if 'state' in init_values and self.state == 'searched':
            return self.env.ref('account_treasury.mt_acredit_order_done')
        import pdb; pdb.set_trace()

        self.ensure_one()
        if 'state' in init_values and self.state == 'searched':
            return self.env.ref('account_treasury.mt_acredit_order_done')
        return super(PayOrder, self)._track_subtype(init_values)

    @api.model
    def create(self,values):
        sequence = self.env["ir.sequence"].next_by_code("pay.order.sequence")
        values['sequence'] = sequence
        result = super(PayOrder,self).create(values)
        return result


class PaymentOrderMoEx(models.Model):
    _name = "pay.order.money.exchange"
    _description = "Ordenes de Pago Cambio Divisas"
    _rec_name = "sequence"
    _inherit = ["mail.thread","mail.activity.mixin"]
    _inherits = {"pay.order": "pay_order_id"}

    sequence_moex = fields.Char(string='Código Interno')
    pay_order_id = fields.Many2one(string='Rel',comodel_name='pay.order',ondelete='cascade',required=True)
    moex_charges = fields.Float(string='Cargos/Comisiones', digits=(9, 2))
    moex_amount_round = fields.Float(string='Redondeo', digits=(2, 2))
    moex_finish_round = fields.Float(string='Importe Entregado', digits=(9, 2))

    @api.model
    def create(self,values):
        sequence = self.env["ir.sequence"].next_by_code("pay.order.money.exchange.sequence")
        values['sequence_moex'] = sequence
        result = super(PaymentOrderMoEx,self).create(values)
        return result
