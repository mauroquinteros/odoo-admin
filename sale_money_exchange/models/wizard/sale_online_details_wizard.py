# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api,exceptions, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime as dt,timedelta as td
import time
import datetime
from dateutil.relativedelta import relativedelta

class SaleOrderDetailWizard(models.TransientModel):
    _name = 'so.detail.wizard'
    _description = 'Detalle de Ventas Online'

    start_date = fields.Date(string='Fecha Inicial',default=fields.Date.context_today)
    end_date = fields.Date(string='Fecha Final',default=fields.Date.context_today)

    agency_id = fields.Many2one(string='Agencia',comodel_name='res.partner.agency',default=lambda self: self.env.user.agency_id)
    partner_id = fields.Many2one(string='Cliente',comodel_name='res.partner')

    company_id = fields.Many2one(string='Company', comodel_name='res.company', required=True, default=lambda self: self.env.user.company_id)

    type_select = fields.Selection(string='Opciones', selection=[
        ('opeday', 'Operaciones del Día'),
        ('salecus', 'Ventas de Cliente'),
        ('rep_so', 'Reporte de Cambios Online'),
        ('rep_so_pen', 'Reporte de Cambios Online pendientes')], default='salecus')

    @api.onchange('type_select')
    def onchange_type_select(self):
        if self.type_select == 'opeday':
            self.start_date = fields.Date.context_today(self).strftime('%Y-%m-%d')
            self.end_date = fields.Date.context_today(self).strftime('%Y-%m-%d')

    def get_action_report(self):
        List = ['&',('date_order','>=',self.start_date.strftime('%Y-%m-%d 05:00:00')),('date_order','<=',self.end_date.strftime('%Y-%m-%d 23:00:00'))]
        if self.type_select == 'salecus':
            if self.env.context.get('type_pdf') == 'qweb-html':
                ide_report = 'sale_money_exchange.report_soopc_html'
            else:
                ide_report = 'sale_money_exchange.report_soopc_pdf'
            List.insert(0,'&',)
            List.insert(1,('partner_id','=',self.partner_id.id),)

        elif self.type_select == 'opeday':
            if self.env.context.get('type_pdf') == 'qweb-html':
                ide_report = 'sale_money_exchange.report_soday_html'
            else:
                ide_report = 'sale_money_exchange.report_soday_pdf'

        elif self.type_select == 'rep_so':
            if self.env.context.get('type_pdf') == 'qweb-html':
                ide_report = 'sale_money_exchange.report_somoex_html'
            else:
                ide_report = 'sale_money_exchange.report_somoex_pdf'

        elif self.type_select == 'rep_so_pen':
            if self.env.context.get('type_pdf') == 'qweb-html':
                ide_report = 'sale_money_exchange.report_sopending_html'
            else:
                ide_report = 'sale_money_exchange.report_sopending_pdf'

        data = {'ids': self.ids,'content': self.env['sale.order'].search(List).ids}
        return self.env.ref(ide_report).report_action(self, data=data)

class ReportSaleCustomer(models.AbstractModel):
    _name = 'report.sale_money_exchange.customer_ope_report_template'
    _description = 'Obtiene los datos de Sale.order para procesar el abstracto.'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'docs': self.env['so.detail.wizard'].browse(data['ids']),
            'Money_USD':self.env.ref('base.USD'),
            'Money_PEN':self.env.ref('base.PEN'),
            'results': self.env['sale.order'].browse(data['content'])
            }

class ReportSaleMoEx(models.AbstractModel):
    _name = 'report.sale_money_exchange.sale_ope_moex_report_template'
    _description = 'Obtiene los datos de Sale.order para procesar el abstracto.'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'docs': self.env['so.detail.wizard'].browse(data['ids']),
            'Money_USD':self.env.ref('base.USD'),
            'Money_PEN':self.env.ref('base.PEN'),
            'results': self.env['sale.order'].browse(data['content'])
            }

class ReportSaleOpeDay(models.AbstractModel):
    _name = 'report.sale_money_exchange.sale_ope_day_report_template'
    _description = 'Obtiene los datos de Sale.order para procesar el abstracto.'

    @api.model
    def _get_report_values(self, docids, data=None):
        sales = 0
        ingresos_dol = 0
        egresos_dol = 0
        ingresos_sol = 0
        egresos_sol = 0
        orders = self.env['sale.order'].browse(data['content'])
        for order in orders:
            if order.state == 'sale':
                sales +=1

        for order in orders:
            if order.state in ['deposit','sale'] and order.currency_id.name == 'USD':
                ingresos_dol +=order.origin_import
            elif order.state in ['cancel'] and order.currency_id.name == 'USD':
                egresos_dol +=order.origin_import

            elif order.state in ['deposit','sale'] and order.currency_id.name == 'PEN':
                ingresos_sol +=order.destination_import
            elif order.state in ['cancel'] and order.currency_id.name == 'PEN':
                egresos_sol +=order.destination_import

        return {
            'ingresos_dol':ingresos_dol,
            'egresos_dol':egresos_dol,
            'ingresos_sol':ingresos_sol,
            'egresos_sol':egresos_sol,
            'sale_total': sales,
            'ope_total': len(orders),
            'user': self.env.user,
            'docs': self.env['so.detail.wizard'].browse(data['ids']),
            'Money_USD':self.env.ref('base.USD'),
            'Money_PEN':self.env.ref('base.PEN'),
            'results': orders
            }

class ReportSaleOpeReportUSD(models.AbstractModel):
    _name = 'report.sale_money_exchange.pending_ope_report_template'
    _description = 'Obtiene los datos de Sale.order para procesar el abstracto.'

    @api.model
    def _get_report_values(self, docids, data=None):
        results=False
        sales = self.env['sale.order'].browse(data['content'])
        for sale in sales:
            if sale.state in ['draft','auth','valid','sent'] and sale.currency_id.name == 'USD':
                if datetime.datetime.now() - sale.date_order > datetime.timedelta(minutes=20):
                    if results != False:
                        results+=sale
                    else:
                        results = sale
        return {
            'datetime': datetime,
            'docs': self.env['so.detail.wizard'].browse(data['ids']),
            'Money_USD':self.env.ref('base.USD'),'Money_PEN':self.env.ref('base.PEN'),
            'results': results
            }