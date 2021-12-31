# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################

from pdb import set_trace
from odoo import models, fields, api,exceptions, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime as dt,timedelta as td
import time
import datetime
from dateutil.relativedelta import relativedelta

class TreasuryBankWizard(models.TransientModel):
    _name = 'treasury.bank.wizard'
    _description = 'Asistente de Cuentas Bancarias'

    start_date = fields.Datetime(string='Fecha Inicial',default=fields.Datetime.now)
    end_date = fields.Datetime(string='Fecha Final',default=fields.Datetime.now)

    options = fields.Selection(string='Opciones', selection=[('report1', 'Resumen de Bancos'), ('report2', 'Detalle de Ingresos Bancos'), ('report3', 'Detalle de Egresos Bancos')])
    currency_ids = fields.Many2many(comodel_name='res.currency', string='Monedas',domain=[('name','in',['USD','PEN'])])

    company_id = fields.Many2one(string='Company', comodel_name='res.company', required=True, default=lambda self: self.env.user.company_id)

    @api.onchange('options')
    def onchange_options(self):
        if self.options == 'report1':
            self.currency_ids = [self.env.ref('base.PEN').id, self.env.ref('base.USD').id]

    def get_action_report(self):
        tipe = False
        name = False
        List = ['&',('date_deposit','>=',self.start_date.strftime('%Y-%m-%d 00:00:00')),('date_deposit','<=',self.end_date.strftime('%Y-%m-%d 23:59:59'))]
        if self.options == 'report1':
            if self.env.context.get('type_pdf') == 'qweb-html':
                ide_report = 'account_treasury.report_treasury_resume_bank_html'
            else:
                ide_report = 'account_treasury.report_treasury_resume_bank_pdf'
        elif self.options == 'report2':
            tipe = 'A-I'
            if self.env.context.get('type_pdf') == 'qweb-html':
                ide_report = 'account_treasury.report_treasury_bank_html'
            else:
                ide_report = 'account_treasury.report_treasury_bank_pdf'
            name = 'Ingresos'
        elif self.options == 'report3':
            tipe = 'B-E'
            if self.env.context.get('type_pdf') == 'qweb-html':
                ide_report = 'account_treasury.report_treasury_bank_html'
            else:
                ide_report = 'account_treasury.report_treasury_bank_pdf'
            name = 'Salidas'

        data = {'ids': self.ids,'content': self.env['deposit.order'].search(List).ids, 'type': tipe, 'name': name, 'currency_ids':self.currency_ids.ids}
        return self.env.ref(ide_report).report_action(self, data=data)

class ReportBanks(models.AbstractModel):
    _name = 'report.account_treasury.treasury_bank_report_template'
    _description = 'Obtiene los datos de deposit.order para procesar el abstracto.'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'name':data['name'],
            'type':data['type'],
            'docs': self.env['treasury.bank.wizard'].browse(data['ids']),
            'Money_USD':self.env.ref('base.USD'),
            'Money_PEN':self.env.ref('base.PEN'),
            'results': self.env['deposit.order'].browse(data['content'])
            }

class ReportResumeBanks(models.AbstractModel):
    _name = 'report.account_treasury.treasury_resume_bank_report_template'
    _description = 'Obtiene los datos de deposit.order para procesar el abstracto.'

    @api.model
    def _get_report_values(self, docids, data=None):
        currencys = self.env['res.currency'].browse(data['currency_ids'])
        return {
            'docs': self.env['treasury.bank.wizard'].browse(data['ids']),
            'Money_USD':self.env.ref('base.USD'),
            'Money_PEN':self.env.ref('base.PEN'),
            'currencys': currencys,
            'results': self.env['deposit.order'].browse(data['content'])
            }