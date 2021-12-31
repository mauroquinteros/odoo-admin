# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                   #
###############################################################################

from odoo import api, fields, models
from datetime import datetime,timedelta
from odoo.exceptions import UserError, AccessError, ValidationError
    
class OERWizard(models.TransientModel):
    _name="copy.tc.oer"
    _description="Wizard para el tipo de cambio de divisas según agencia"

    def _default_agency(self):
        oer_obj = self.env['res.currency.rate.oer']
        oer_ids = self._context.get('active_ids')
        if(len(oer_ids) > 1):
            raise ValidationError('Seleccione solo un tipo de cambio por agencia')
        else:    
            oer_records  = oer_obj.browse(oer_ids)
            agency_id = oer_records.agency_id.id
            return agency_id

    def _default_agency_copy(self):
        oer_obj = self.env['res.currency.rate.oer']
        oer_ids = self._context.get('active_ids')
        if(len(oer_ids) > 1):
            raise ValidationError('Seleccione solo un tipo de cambio por agencia')
        else:
            oer_records  = oer_obj.browse(oer_ids)
            agency_id = oer_records.agency_id.id
            agency_ids = self.env['res.partner.agency'].search([('id','!=',agency_id)])
            return agency_ids

    agency_id = fields.Many2one(comodel_name='res.partner.agency', string='Agencia', required=True,default=_default_agency)
    agency_copy_ids = fields.Many2many(comodel_name='res.partner.agency', string='Copiar a agencias',required=True,default=_default_agency_copy)
         
    @api.onchange('agency_id')
    def _onchange_price_orpDOL(self):
        value = self._get_oer_obj(self.env.ref('base.USD').id,self.env.ref('base.PEN').id)
        self.price_orpdol = value.price_orp

    @api.onchange('agency_id')
    def _onchange_price_drsDOL(self):
        value = self._get_oer_obj(self.env.ref('base.USD').id,self.env.ref('base.PEN').id)
        self.price_drsdol = value.price_drs

    @api.onchange('agency_id')
    def _onchange_price_orpEUR(self):
        value = self._get_oer_obj(self.env.ref('base.EUR').id,self.env.ref('base.PEN').id)
        self.price_orpeur = value.price_orp

    @api.onchange('agency_id')
    def _onchange_price_drsEUR(self):
        value = self._get_oer_obj(self.env.ref('base.EUR').id,self.env.ref('base.PEN').id)
        self.price_drseur = value.price_drs

    @api.onchange('agency_id')
    def _onchange_factorprice_orp(self):
        value = self._get_oer_obj(self.env.ref('base.EUR').id,self.env.ref('base.USD').id)
        self.factorprice_orp = value.price_orp
    
    @api.onchange('agency_id')
    def _onchange_factorprice_drs(self):
        value = self._get_oer_obj(self.env.ref('base.EUR').id,self.env.ref('base.USD').id)
        self.factorprice_drs = value.price_drs


    def _get_oer_obj(self,origin,destination):
        agency = 1
        obj_oer = self.env['res.currency.rate.oer'].search(['|','&',('origin_currency_id','=',origin),'&',('agency_id','=',agency),
        '&',('destination_currency_id','=',destination),('currentactive','=','True'),'&',('origin_currency_id','=',destination),
        '&',('agency_id','=',agency),'&',('destination_currency_id','=',origin),('currentactive','=','True')])  
        return obj_oer

    price_orpdol = fields.Float(string='Compra',digits=(9,4))
     
    price_drsdol = fields.Float(string='Venta',digits=(9,4))

    price_orpeur = fields.Float(string='Compra',digits=(9,4))

    price_drseur = fields.Float(string='Venta',digits=(9,4))

    factorprice_orp = fields.Float(string='Factor Compra',digits=(9,4))

    factorprice_drs = fields.Float(string='Factor Venta',digits=(9,4))
  
    def action_copy_agencies(self):
        for agency in self.agency_copy_ids:
            if(self.price_orpdol != 0 and self.price_orpdol != 0):
                #Dólares/Soles
                self.env['res.currency.rate.oer'].create({
                    'business_partner_id':self.env.ref('base.main_partner').id,
                    'agency_id' : agency.id,
                    'origin_currency_id' : self.env.ref('base.USD').id,
                    'destination_currency_id' : self.env.ref('base.PEN').id,
                    'price_orp' : self.price_orpdol,
                    'price_drs' : self.price_drsdol
                    })
            if(self.price_orpeur != 0 and self.price_orpeur != 0):
                #Euros/Soles
                self.env['res.currency.rate.oer'].create({
                    'business_partner_id':self.env.ref('base.main_partner').id,
                    'agency_id' : agency.id,
                    'origin_currency_id' : self.env.ref('base.EUR').id,
                    'destination_currency_id' : self.env.ref('base.PEN').id,
                    'price_orp' : self.price_orpeur,
                    'price_drs' : self.price_drseur
                    })
            if(self.factorprice_orp != 0 and self.factorprice_drs !=0):
                #Dólares/Euros
                self.env['res.currency.rate.oer'].create({
                    'business_partner_id':self.env.ref('base.main_partner').id,
                    'agency_id' : agency.id,
                    'origin_currency_id' : self.env.ref('base.EUR').id,
                    'destination_currency_id' : self.env.ref('base.USD').id,
                    'price_orp' : self.factorprice_orp,
                    'price_drs' : self.factorprice_drs
                    })