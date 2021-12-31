from odoo import api, fields, models
import datetime
import pytz
from odoo.tools import (
    DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT,
)

class AssistantQueryExchangeMoney(models.TransientModel):
    _name = "money.exchange.query"
    _description = "Asistente de Consulta de Tipo de Cambio"
    
    currency_id = fields.Many2one(comodel_name='res.currency', string='Moneda')
    agency_id = fields.Many2one('res.partner.agency',string='Agencia',default=lambda self: self.env.user.agency_id)
    date_query = fields.Date(string='Fecha de Consulta',default=fields.Date.context_today)
    
    exchange_import = fields.Float(string='Importe')
    
    result_official = fields.Html(string='Resultado')
    
    result_operative = fields.Html(string='Resultado')
    
    @api.onchange('currency_id','date_query','exchange_import')
    def onchange_set_front_query(self):
        not_found = self.env['ir.config_parameter'].sudo().get_param('not.found.404').replace('>"', '>')
        scheme = self.env['ir.config_parameter'].sudo().get_param('scheme.html.tc')
        texts = ['Compra','Venta']
        
        self.result_official = self.env['ir.config_parameter'].sudo().get_param('scheme.html.header')
        
        if len(self.currency_id.rate_ids) > 0:
            for rate in self.currency_id.rate_ids:
                rates = [rate.price_orp,rate.price_drs]
                if rate.name.strftime("%Y-%m-%d") <= self.date_query.strftime("%Y-%m-%d"):
                    for x, z in zip(rates,texts):
                        self.result_official += scheme % (
                            self.exchange_import,
                            x,
                            z,
                            str(self.env.ref('base.PEN').symbol) + " " + str(round(self.exchange_import * x,2)) if z == 'Compra' else str(self.env.ref('base.PEN').symbol) + " " + str(round(self.exchange_import / x,2)),
                            self.env.ref('base.PEN').currency_unit_label)
                    self.result_official += self.env['ir.config_parameter'].sudo().get_param('scheme.html.footer').replace('>"<', '><').replace('>"', '>')
                    self.result_official = self.result_official.replace('>"<', '><').replace('>"', '>')
                    
        else:
            self.result_official = not_found
        
        ope_rates = self.env['res.currency.rate.oer'].search(['&',('currentactive','=',True),'&',('agency_id','=',self.agency_id.id),('origin_currency_id','=',self.currency_id.id)])
        self.result_operative = self.env['ir.config_parameter'].sudo().get_param('scheme.html.header')
        if len(ope_rates) > 0:
            for rate in ope_rates:
                rates = [rate.price_orp,rate.price_drs]
                if rate.date_validity_period_start.strftime("%Y-%m-%d") <= self.date_query.strftime("%Y-%m-%d"):
                    for x, z in zip(rates,texts):
                        self.result_operative += scheme % (
                        self.exchange_import,
                        x,
                        z,
                        str(rate.destination_currency_id.symbol) + " " + str(round(self.exchange_import * x,2)) if z == 'Compra' else str(rate.destination_currency_id.symbol) + " " + str(round(self.exchange_import / x,2)),
                        rate.destination_currency_id.currency_unit_label)
                    self.result_operative += self.env['ir.config_parameter'].sudo().get_param('scheme.html.footer')
                    self.result_operative = self.result_operative.replace('>"<', '><').replace('>"', '>')
        else:
            self.result_operative = not_found