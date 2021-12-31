from odoo import api, fields, models
import datetime
from odoo.tools import (
    DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT,
)

class AssistantApiQueryExRate(models.TransientModel):
    _name = "assistant.api_exchange.rate"
    _description = "Asistente de Tipo de Cambio SBS"
    
    api_date = fields.Date(string='Fecha de la Consulta',default=fields.Date.context_today,)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Moneda')
    
    name_orp = fields.Char(string='Nombre Compra')
    value_orp = fields.Float(string='Valor Compra', digits=(1, 4))
    period_orp = fields.Date(string="Periodo Compra")
    url_orp = fields.Char(string="Link Compra")
    
    name_drs = fields.Char(string='Nombre Venta')
    value_drs = fields.Float(string='Valor Venta', digits=(1, 4))
    period_drs = fields.Date(string="Periodo Venta")
    url_drs = fields.Char(string='Link Venta')
    
    mode = fields.Selection(string='Modo',selection=[('auto', 'Automático'), ('manual', 'Manual')],default="auto")
    
    @api.onchange('api_date')
    def onchange_api_date(self):
        currency = self.currency_id
        values = {'name_orp': False,'value_orp': False,'period_orp': False,'url_orp': False,'name_drs': False,'value_drs': False,'period_drs': False,'url_drs': False}
        rate_orp = currency.get_current_rate_pe(date=self.api_date + datetime.timedelta(1),param=currency.parameter_orp_id.key)
        rate_drs = currency.get_current_rate_pe(date=self.api_date + datetime.timedelta(1),param=currency.parameter_drs_id.key)
        
        if rate_orp is not False and rate_drs is not False:
            values = {
                'name_orp': str(rate_orp.get('rate_name')),
                'value_orp': float(rate_orp.get('rate_pe')),
                'period_orp': rate_orp.get('date_rate'),
                'url_orp': str(rate_orp.get('url')),
                'name_drs': str(rate_drs.get('rate_name')),
                'value_drs': float(rate_drs.get('rate_pe')),
                'period_drs': rate_orp.get('date_rate'),
                'url_drs': str(rate_drs.get('url'))
                }
        self.update(values)