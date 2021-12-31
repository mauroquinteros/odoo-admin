# -*- coding: utf-8 -*-
import base64
from decimal import Decimal
from datetime import datetime as dt,timedelta as td
from itertools import chain
import locale
import pytz
import operator
import string, random

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.modules.module import get_module_resource

from odoo.addons.data_migration.models.utils import armed_chains as chain
from odoo.addons.data_migration.models.utils import glosa as g
from odoo.addons.l10n_pe_currency.models.utils import values as valcur

class ChargeLoteUsersRaw(models.Model):
    _name = "lote.user.raw"
    _description = "Lote de Información de Usuarios"
    _rec_name = "sequence"

    sequence = fields.Char(string=u"Código de Secuencia",default="/",readonly=True)
    firstname = fields.Char(string='Nombres')
    flstname  = fields.Char(string='Apellido Paterno')
    mlstname  = fields.Char(string='Apellido Materno')
    name = fields.Char(string='Nombre Completo')
    gender = fields.Char(string='Sexo')
    birth = fields.Char(string='Nacimiento', required=False)
    ide_type = fields.Char(string='Identificador Oficial',required=True)
    ide_num = fields.Char(string='N° Identificador')
    phone = fields.Char(string='Teléfono')
    mobile = fields.Char(string='Celular')
    street = fields.Char(string='Domicilio')
    l10n_pe_district = fields.Char(string='Distrito')
    city = fields.Char(string='Provincia')
    state = fields.Char(string='Departamento')
    country = fields.Char(string='País',required=True)
    private_email = fields.Char(string='Correo Personal')
    login = fields.Char(string='Usuario/Mail')
    civil_status = fields.Char(string='Estado Civil')
    password = fields.Char(string='Contraseña', required=True, default="12345")
    parent_id = fields.Char(string='Relación a Partner')
    parent = fields.Char(string='Emparejado')
    codjet = fields.Char(string='Codigo Jet/Pin')
    status = fields.Selection(string='status',selection=[('tail', 'En Cola'), ('success', 'Procesado'), ('error', 'Error')],default='tail')
    situation = fields.Char(string="Situación Empleado")

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    image_1920 = fields.Image(default=_default_image)

    def action_create_employee(self):
        self.ensure_one()
        self.env['hr.employee'].create(dict(
            name=self.name,
            company_id=self.env.company.id,
            **self.env['hr.employee']._sync_user(self)
        ))

    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    @api.model
    def create(self, values):
        chain.assemble_mail(values)

        if values.get("sequence", "/") == "/":
            seq = self.env["ir.sequence"]
            values["sequence"] = (seq.next_by_code("user.warehouse.data.sequence") or "/")

        result = super(ChargeLoteUsersRaw, self).create(values)
        return result

    def process_users_DHW(self):
        locale.setlocale(locale.LC_ALL, "en_US")
        assemble_mail = False
        user = self.env['res.users']
        partner = self.env['res.partner']
        employee = self.env['hr.employee']

        recloop = self.search(['&',('status', '=', 'tail'),('situation', '!=', 'A')],order="situation desc", limit=100)
        for rec in recloop:
            s_user = user.search([('login','=',rec.login)])
            r_user = rec.search([('login','=',rec.login)])
            if len(s_user) + len(r_user) > 1:
                if len(rec.login.split("@")) > 1:
                    disassemble = rec.login.split("@")
                    assemble_mail = disassemble[0]+'_'+''.join(random.choice(string.hexdigits) for i in range(random.randint(1, 5))) + "@" + disassemble[1]
                else:
                    assemble_mail = rec.login +'-'+''.join(random.choice(string.hexdigits) for n in range(random.randint(2, 4)))
            else:
                assemble_mail = rec.login

            ObjUser = user.create({
                'name': (rec.name).title(),
                'firstname':(rec.firstname).title() if type(rec.firstname) is not bool else False,
                'lastname':(rec.flstname).title() if type(rec.flstname) is not bool else False,
                'motherlastname':(rec.mlstname).title() if type(rec.mlstname) is not bool else False,
                'login': assemble_mail,
                'password': rec.password,
                'active': True,
                'notification_type':'inbox',
                'image_1920': rec.image_1920,
                'tz': 'America/Lima',
                'employee': True,
                'is_company': False,
                'color': 2,
                'email': rec.private_email,
                'l10n_latam_identification_type_id': g.homologant(self,'hr.employee',rec.ide_type,'l10n_latam_identification_type_id').id,
                'vat': rec.ide_num,
                'l10n_pe_district': g.homologant(self,'l10n_pe.res.city.district',rec.l10n_pe_district).id if rec.l10n_pe_district is not False else False,
                'city_id': g.homologant(self,'res.city',rec.city).id if rec.city is not False else False,
                'state_id': g.homologant(self,'res.country.state',rec.state).id if rec.state is not False else False,
                'country_id': g.homologant(self,'res.country',rec.country).id if rec.country is not False else False,
                'phone': rec.phone,
                'mobile': rec.mobile,
                'company_id': self.env.company.id,
                'parent_id': False if rec.parent is False else g.homologant(self,'hr.employee',rec.parent).id,
                'street': rec.street,
                'type': 'employee',
                'customer_rank':0,
                'active': False if rec.situation == 'A' else True
            })

            employee.create(dict(
                name=(rec.name).title(),
                hr_firstname=(rec.firstname).title() if type(rec.firstname) is not bool else False,
                hr_lastname=(rec.flstname).title() if type(rec.flstname) is not bool else False,
                hr_motherlastname=(rec.mlstname).title() if type(rec.mlstname) is not bool else False,
                address_id=ObjUser.partner_id.parent_id.id,
                address_home_id=ObjUser.partner_id.id,
                birthday=False if rec.birth == '  -   -' else dt.strptime(rec.birth, '%d-%b-%y') - td(days=valcur.ops.get('*')(365,100)),
                country_id=g.homologant(self,'res.country',rec.country).id if rec.country is not False else False,
                country_of_birth=g.homologant(self,'res.country',rec.country).id if rec.country is not False else False,
                marital=g.homologant(self,'hr.employee',rec.civil_status,'marital') if rec.civil_status is not False else False,
                gender=g.homologant(self,'hr.employee',rec.gender),
                private_email=rec.private_email,
                mobile_phone=rec.mobile,
                work_phone=rec.phone,
                phone=rec.mobile,
                emergency_phone=rec.phone,
                identification_id=rec.ide_num,
                company_id=self.env.company.id,
                active=False if rec.situation == 'A' else True,
                **employee._sync_user(ObjUser)
            ))
            rec.update({'status': 'success'})

class AgentAgencyRaw(models.Model):
    _name = "agent.agency.external.raw"
    _description = "Tabla para Procesar datos de agentes y agencias ajenas a JP"
    _rec_name = "name"

    state = fields.Selection(string='Estado',default='to_process',selection=[('to_process', 'Por Procesar'), ('process', 'Procesado'), ('not_process', 'No Procesado')])

    sequence = fields.Char(string="Secuencia",default="/")
    code_agency = fields.Char(string="Código del Agente",size=10)
    name = fields.Char(string='Nombre',size=100)
    street = fields.Char(string='Dirección',size=300)
    phone = fields.Char(string='Teléfono',size=100)
    schedule = fields.Char(string='Horario',size=100)
    country = fields.Char(string='País',size=100)
    department = fields.Char(string='Departamento',size=100)
    province = fields.Char(string='Provincia',size=100)
    district = fields.Char(string='Distrito',size=100)
    latitude = fields.Char(string='Latitud',size=100)
    longitude = fields.Char(string='Longitud',size=100)
    type_brand = fields.Char(string='Tipo',size=100)
    send_currency = fields.Char(string='Moneda Envío',size=100)
    tc = fields.Char(string='Tipo Cambio',size=100)
    pay_currency = fields.Char(string='Moneda Pago',size=100)
    payer_name = fields.Char(string='Nombre Pagador',size=100)
    payer_code = fields.Char(string='Código Pagador',size=10)
    reference = fields.Char(string='Referencia',size=100)
    active = fields.Boolean(string='active',default=True)

    @api.model
    def create(self, values):
        if values.get("sequence", "/") == "/":
            seq = self.env["ir.sequence"]
            values["sequence"] = seq.next_by_code("agent.agency.external.sequence") or "/"
        return super(AgentAgencyRaw, self).create(values)

    def process_agent_agency(self):
        for loop in self.search(['&',('state','=','to_process'),('active','=',True)]):
            cor = self.env['res.partner.correspondent'].search([('internal_code','=',loop.payer_code)])
            if len(cor) > 1:
                loop.state = 'not_process'
                raise ValidationError('Hay más de dos corresponsales con el mismo código.')
            else:
                country = g.homologant(self,'res.country',loop.country)
                pay_currency = g.homologant(self,'res.currency',loop.pay_currency)
                send_currency = g.homologant(self,'res.currency',loop.send_currency)

                if loop.department == loop.province and loop.province == loop.district:
                    address = loop.street or '' +' '+ loop.department or ''
                else:
                    address = loop.street or '' +' '+ loop.department or '' +' '+ loop.province or '' +' '+ loop.district or ''

                agency = {
                    'name':loop.name,
                    'abbrevation_name': ' '.join([str(elem) for elem in loop.name.split(' ')[0:2]]),
                    'internal_code':loop.code_agency,
                    'agency_type':g.homologant(self,'res.partner.correspondent',loop.type_brand,'agency_type'),
                    'address_reference':address,
                    'longitude':loop.longitude,
                    'latitude':loop.latitude,
                    'office_hour':loop.schedule,
                    'f_oer_ids':[
                        (0, False, {
                            'origin_currency_id':send_currency.id,
                            'exchange_rate':float(loop.tc),
                            'destination_currency_id':pay_currency.id,
                            'local':True if country.currency_id.name == pay_currency.name else False,
                            'is_currency_payment':True})
                        ],
                    'correspondent_id':cor.id,
                    'payer':loop.payer_name,
                    'reference_payer':loop.payer_code,
                    'payment_channel_id':self.env.ref('base_company.business_channel_004').id,
                    'city':loop.province,
                    'country_id':country.id,
                    'street':loop.street,
                    'street2':loop.department or '' +' - '+ loop.province or '' +' - '+ loop.district or '',
                    'company_type':'company'
                    }
            self.env['res.partner.agency'].create(agency)
            loop.state = 'process'