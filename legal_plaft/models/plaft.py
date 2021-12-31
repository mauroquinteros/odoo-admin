# -*- coding: utf-8 -*-
import base64
import calendar
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, AccessError, ValidationError

TYPE_PERSON = [('1','Natural con negocio'),('2','Natural sin negocio')]

class Risk(models.Model):
    _name='plaft.risk'
    _description='Valoración de riesgos para los factores de riesgo PLAFT'
    _rec_name = 'name'
    _order = 'id ASC'

    name = fields.Char('Nivel de Riesgo', track_visibility='onchange')
    risk_value = fields.Integer('Valor', track_visibility='onchange')
    remark = fields.Text('Observaciones / instrucciones', track_visibility='onchange')
    active = fields.Boolean('active', default=True, track_visibility='onchange')

class RiskAge(models.Model):
    _name='plaft.risk.age'
    _description='PLAFT Risk Age'

    ini_number = fields.Integer('Parámetro Inicial', track_visibility='onchange')
    end_number = fields.Integer('Parámetro Final', track_visibility='onchange')
    remark = fields.Text('Observaciones / instrucciones', track_visibility='onchange')
    plaftrisk_id = fields.Many2one('plaft.risk',string=u'Riesgo LA/FT', track_visibility='onchange')
    active = fields.Boolean('active', default=True, track_visibility='onchange')
    
class StatusCivilList(models.Model):
    _name = 'plaft.status.civil.list'
    _description = 'Lista de Estado Civil'
    _rec_name = 'name'
    _order = 'sequence ASC'

    sequence = fields.Char(string=u'Secuencia',default="/",readonly=True, track_visibility='onchange')
    name = fields.Char('Nombre de la Categoría',required=True, track_visibility='onchange')
    t_description = fields.Text('Descripción', track_visibility='onchange')
    risklevel_id = fields.Many2one('plaft.risk', 'Nivel de Riesgo', track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'company', required=True, default=lambda self: self.env.user.company_id, track_visibility='onchange')
    active = fields.Boolean('active', default=True, track_visibility='onchange')
    
    @api.model
    def create(self, values):
        seq = self.env["ir.sequence"]
        values["sequence"] = seq.next_by_code("plaft.status.civil.list.sequence") or "/"
            
        result = super(StatusCivilList, self).create(values)
        return result
    
class PlaftPosition(models.Model):
    _name = 'plaft.position'
    _description = 'Lista de Cargos y Posiciones'
    _rec_name = 'name'
    _order = 'sequence ASC'
    
    sequence = fields.Char(string=u'Secuencia',default="/",readonly=True, track_visibility='onchange')
    name = fields.Char('Nombre de la Categoría',required=True, track_visibility='onchange')
    foreign_code = fields.Char('Código Foráneo',required=True, track_visibility='onchange')
    executive = fields.Boolean(string='Ejecutivo')
    employee = fields.Boolean(string='Empleado')
    worker = fields.Boolean(string='Trabajador')
    selectable = fields.Boolean(string='Seleccionable')
    risklevel_id = fields.Many2one('plaft.risk', 'Nivel de Riesgo', track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'company', required=True, default=lambda self: self.env.user.company_id, track_visibility='onchange')
    active = fields.Boolean('active', default=True, track_visibility='onchange')
    
    @api.model
    def create(self, values):
        seq = self.env["ir.sequence"]
        values["sequence"] = seq.next_by_code("plaft.position.sequence") or "/"
        result = super(PlaftPosition, self).create(values)
        return result
    
class ControlListTag(models.Model):
    _name = 'plaft.control.category'
    _description = 'PLAFT Control List - Categories'
    _rec_name = 'name'
    _order = 'id ASC'

    name = fields.Char('Nombre de la Categoría',required=True, track_visibility='onchange')
    t_description = fields.Text('Descripción', track_visibility='onchange')
    risklevel_id = fields.Many2one('plaft.risk', 'Nivel de Riesgo', track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'company', required=True, default=lambda self: self.env.user.company_id, track_visibility='onchange')
    active = fields.Boolean('active', default=True, track_visibility='onchange')
    controllist_ids = fields.Many2many('plaft.control.list', string=u'Miembros de la Lista', track_visibility='onchange')

class ControlThreshold(models.Model):
    _name = 'plaft.control.threshold'
    _description = 'Control de Umbrales PLAFT'
    _rec_name = 'id'
    _order = 'id ASC'

    business_line_id = fields.Many2one('business.line', 'Linea de Negocio')
    origin_country_id = fields.Many2one('res.country', 'País Origen', required=True, track_visibility='onchange')
    origin_partner_id = fields.Many2one('res.partner','Empresa Origen',require=True,
        domain=['&',('is_company','=',True),('category_id.keycode','=','correspondent')], track_visibility='onchange')
    destination_country_id = fields.Many2one('res.country',string=u'País Destino',required=True, track_visibility='onchange')
    destination_partner_id = fields.Many2one('res.partner',string=u'Empresa Destino',required=True, track_visibility='onchange')
    threshold_type = fields.Selection([('obl','Obligatorio'),('fac','Facultativo')],'Tipo de Umbral',required=True, track_visibility='onchange')
    date_validity_period_start = fields.Date('Inicio de vigencia',default=lambda self: fields.Datetime.now(), track_visibility='onchange')
    control_type = fields.Selection([('U','Operación única'),('M','Operación múltiple o acumulada')],
        'Tipo de control',required=True, track_visibility='onchange')
    currency_id = fields.Many2one('res.currency',domain=[('name','in',['PEN','USD','EUR'])],
        string=u'Moneda',ondelete='restrict',required=True, track_visibility='onchange')
    amount_min = fields.Integer('Monto mínimo',default=0,required=True, track_visibility='onchange')
    amount_max = fields.Integer('Monto máximo',default=0,required=True, track_visibility='onchange')
    i_time_frame = fields.Integer('Periodo de tiempo',default=0, track_visibility='onchange')
    time_frame_type = fields.Selection(
        [
            ('cro', 'Cronológico'),
            ('cal_semana', 'Calendario Semana'), 
            ('cal_mes', 'Calendario Mes'), 
            ('cal_bimestral', 'Calendario Bimestral'), 
            ('cal_trimestral', 'Calendario Trimestral'), 
            ('cal_semestral', 'Calendario Semestral'), 
            ('cal_anual', 'Calendario Anual'), 
        ],
        'Tipo de periodo de tiempo',
        default='cal_semana')
    remark = fields.Text('Observaciones')
    authorization = fields.Boolean('Requiere Autorización',default=False)
    threshold_req_ids = fields.Many2many('plaft.document.category',string=u'Requisitos')
    company_id = fields.Many2one('res.company',string=u'company',required=True,default=lambda self: self.env.user.company_id)
    active = fields.Boolean('active',default=True)

    def checkComercialThreshold(self,finalamount):
        commercialthreshold = self.env['plaft.commercial.threshold']
        commercialthreshold.search([
            '&',
            '&',
            ('amount_minimum','<=',finalamount),
            ('amount_maximum','>=',finalamount),
            '&',
            ('active','=',True),
            ('authorization','=',True)
            ])
        if(commercialthreshold.id != False): 
            return True
        else:
            return False

class ControlList(models.Model):
    _name = 'plaft.control.list'
    _description = 'PLAFT Control List'
    _rec_name = 'name'
    _order = 'id ASC'
    _inherit = ["mail.thread","mail.activity.mixin"]

    name = fields.Char('Nombre Completo', readonly=True, compute='_compute_name', store=True)
    firstname = fields.Char('Nombres', required=True, default='')
    lastname = fields.Char('Apellido Paterno', required=True, default='')
    motherlastname = fields.Char('Apellido Materno', required=True, default='')
    documentcatalog_id = fields.Many2one('l10n_latam.identification.type', 'Tipo de Doc. Identidad', 
        domain=[('documentcategory_ids.name', 'ilike', 'Docs de Identidad')])
    id_number = fields.Char('Nro de Doc. de Identidad', required=True)
    family_relationship = fields.Selection(string=u'Relacion Parentesco', default='principal', required=True,
        selection=[('principal', 'Principal'), ('esposa', 'Esposo / Esposa'), 
            ('padre', 'Padre / Madre'), ('hermano', 'Hermano / Hermana'), ('hijo', 'Hijo / Hija')])
    public_office = fields.Char('Entidad Pública')
    title = fields.Char('Cargo')
    ofac_code = fields.Integer('OFAC Código')
    ofac_program = fields.Char('OFAC Programa')
    lock_description = fields.Char('Razones para el bloqueo de la cuenta')
    unlock_description = fields.Char('Razones para el desbloqueo de la cuenta')
    remark = fields.Text('Observaciones')
    category_ids = fields.Many2many('plaft.control.category', string=u'Categorias')
    parent_id = fields.Many2one('plaft.control.list', 'Pariente', ondelete='restrict', index=True)
    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent Right', index=True)
    child_ids = fields.One2many('plaft.control.list', 'parent_id', 'Familiares')
    company_id = fields.Many2one('res.company', 'company', required=True, default=lambda self: self.env.user.company_id)
    active = fields.Boolean('active',default=True)

    @api.depends('firstname','lastname','motherlastname')
    def _compute_name(self):
        name = ''
        for controllist in self:
            if len(self.lastname) > 0:
                name += self.lastname + ' '

            if len(self.motherlastname) > 0:
                name += self.motherlastname + ' '

            if len(self.firstname) > 0:
                name += self.firstname

            controllist.name = name

    @api.onchange('firstname')
    def onchange_firtname(self):
        self.firstname = (self.firstname).title()
        return

    @api.onchange('lastname')
    def onchange_lastname(self):    
        self.lastname = (self.lastname).title()
        return

    @api.onchange('motherlastname')
    def onchange_motherlastname(self):    
        self.motherlastname = (self.motherlastname).title()
        return

class DocumentationType(models.Model):
    _name='plaft.documentation.type'
    _description='Tipo de Documentación en la Tabla de Maestro de Clientes'
    _rec_name = 'name'
    _order = 'id ASC'

    name = fields.Char('Documentación')
    plaftrisk_id = fields.Many2one('plaft.risk', string=u'Riesgo LA/FT')
    remark = fields.Text('Observaciones / instrucciones')
    company_id = fields.Many2one('res.company', string=u'company', required=True, default=lambda self: self.env.user.company_id)
    active = fields.Boolean('active', default=True)

class DocumentCategory(models.Model):
    _name = 'plaft.document.category'
    _description = 'PLAFT Document Catalog - Categories'
    _rec_name = 'name'
    _order = 'id ASC'

    name = fields.Char('Nombre', required=True)
    acronym = fields.Char('Acrónimo / Abreviado', required=True, default='')
    description = fields.Char('Descripción', default='')
    code = fields.Char('Código Único')
    documentcatalog_ids = fields.Many2many('l10n_latam.identification.type', 'identi_rel', string=u'Documentos')
    company_id = fields.Many2one('res.company', string=u'company', required=True, default=lambda self: self.env.user.company_id)
    active = fields.Boolean('active',default=True)

    _sql_constraints = [ 
        # parameters:
        # constraint unique identifier
        # constraint SQL sintax
        # validation message
        ('name_unique', 
        'UNIQUE (code)', 
        'El código ingresado debe ser único.')
    ]

class Regimen(models.Model):
    _name='plaft.regimen'
    _description='Regimenes del Sistema de Prevención de LA/FT (PLAFT)'

    name = fields.Char('Regimen')
    remark = fields.Text('Observaciones / instrucciones')
    plaftrisk_id = fields.Many2one('plaft.risk', 'Riesgo LA/FT')
    active = fields.Boolean('active', default=True)

class CommercialThreshold(models.Model):
    _name = 'plaft.commercial.threshold'
    _description = 'Umbrales comerciales que requieren aprobación'

    partner_id = fields.Many2one('res.partner', 'Socio de Negocio Nacional', domain=['&',('category_id','=',1), ('country_id.code','=','PE')])
    currency_id = fields.Many2one('res.currency', 'Moneda', domain=[('name','in',['PEN','USD','EUR'])])
    amount_minimum = fields.Integer('Monto mínimo')
    amount_maximum = fields.Integer('Monto máximo')
    remark = fields.Text('Observaciones')
    authorization = fields.Boolean('Requiere autorización',default=False)
    active = fields.Boolean('active',default=True)
    
class Declaration_RO(models.Model):
    _name = 'plaft.ro.declaration'
    _description = 'Registro de Operaciones para multipes Servicios'
        
    sequence = fields.Char(string='sequence')

    record_row = fields.Integer(string=u'Fila de Registro')
    company = fields.Char(string=u'Codigo de Oficina')
    record_operation = fields.Char(string=u'Número Registro de Operaciones')
    internal_number = fields.Char(string=u'Registro de Numero Interno')
    reference_number = fields.Char(string=u'Serie & Correlativo')
    mode_operation = fields.Char(string=u'Modalidad de Operacion')
    ubigeo_agency = fields.Char(string=u'Ubigeo de Agencia')
    date_operation = fields.Char(string=u'Fecha de la O/P')
    time_operation = fields.Char(string=u'Hora de la O/P')

    payer_type_relationship = fields.Char(string=u'Tipo de Relacion Ordenante')
    payer_residence_condition = fields.Char(string=u'Condicion de Residencia Ordenante')
    payer_type_person = fields.Many2one(comodel_name='l10n_pe_sunat.anexo.02', string='Tipo de Persona Ordenante',track_visibility='onchange')
    payer_ide_document = fields.Many2one('l10n_latam.identification.type',string=u'Tipo Documento Ordenante',domain=[('documentcategory_ids.acronym','=','DI')])
    payer_document = fields.Char(string=u'Número Identidad - Natural Ordenante')
    payer_name_paternal = fields.Char(string=u'Apellido Paterno Ordenante')
    payer_name_maternal = fields.Char(string=u'Apellido Materno Ordenante')
    payer_name_client = fields.Char(string=u'Nombres Ordenante')
    payer_occupation_id = fields.Many2one('l10n_pe_sunat.anexo.02',string=u'Profesion Ordenante')
    payer_code_ciiu_id = fields.Many2one('l10n_pe_sunat.anexo.01',string=u'Actividad Economica Ordenante')
    payer_position_id = fields.Many2one('plaft.position',string=u'Cargo en la Empresa Ordenante')
    payer_legal_address = fields.Char(string=u'Direccion Legal Ordenante')
    payer_depaubigeo = fields.Many2one("res.country.state",string=u"Departamento Ordenante")
    payer_provubigeo = fields.Many2one("res.city",string=u"Provincia Ordenante")
    payer_distubigeo = fields.Many2one("l10n_pe.res.city.district",string=u"Distrito Ordenante")
    payer_movil_client = fields.Char(string=u'Telefono Movil Ordenante')

    performer_type_relationship = fields.Char(string=u'Tipo de Relacion Ejecutante')
    performer_residence_condition = fields.Char(string=u'Condicion de Residencia Ejecutante')
    performer_type_person = fields.Many2one(comodel_name='l10n_pe_sunat.anexo.02', string='Tipo de Persona Ejecutante',track_visibility='onchange')
    performer_ide_document = fields.Many2one('l10n_latam.identification.type',string=u'Tipo Documento Ejecutante',domain=[('documentcategory_ids.acronym','=','DI')])
    performer_document = fields.Char(string=u'Número Identidad -Natural Ejecutante')
    performer_name_paternal = fields.Char(string=u'Apellido Paterno Ejecutante')
    performer_name_maternal = fields.Char(string=u'Apellido Materno Ejecutante')
    performer_name_client = fields.Char(string=u'Nombres Ejecutante')
    performer_occupation_id = fields.Many2one('l10n_pe_sunat.anexo.02',string=u'Profesion Ejecutante')
    performer_code_ciiu_id = fields.Many2one('l10n_pe_sunat.anexo.01',string=u'Actividad Economica Ejecutante')
    performer_position_id = fields.Many2one('plaft.position',string=u'Cargo en la Empresa Ejecutante')
    performer_legal_address = fields.Char(string=u'Direccion Legal Ejecutante')    
    performer_depaubigeo = fields.Many2one("res.country.state",string=u"Departamento Ejecutante")
    performer_provubigeo = fields.Many2one("res.city",string=u"Provincia Ejecutante")
    performer_distubigeo = fields.Many2one("l10n_pe.res.city.district",string=u"Distrito Ejecutante")
    performer_movil_client = fields.Char(string=u'Telefono Movil Ejecutante')

    beneficiary_type_relationship = fields.Char(string=u'Tipo de Relacion Beneficiario')
    beneficiary_residence_condition = fields.Char(string=u'Condicion de Residencia Beneficiario')
    beneficiary_type_person = fields.Many2one(comodel_name='l10n_pe_sunat.anexo.02', string='Tipo de Persona Beneficiario',track_visibility='onchange')
    beneficiary_ide_document = fields.Many2one('l10n_latam.identification.type',string=u'Tipo Documento Beneficiario',domain=[('documentcategory_ids.acronym','=','DI')])
    beneficiary_document = fields.Char(string=u'Documento Identidad - Natural Beneficiario')
    beneficiary_name_paternal = fields.Char(string=u'Apellido Paterno Beneficiario')
    beneficiary_name_maternal = fields.Char(string=u'Apellido Materno Beneficiario')
    beneficiary_name_client = fields.Char(string=u'Nombres Beneficiario')
    beneficiary_occupation_id = fields.Many2one('l10n_pe_sunat.anexo.02',string=u'Profesion Beneficiario')
    beneficiary_code_ciiu_id = fields.Many2one('l10n_pe_sunat.anexo.01',string=u'Actividad Economica Beneficiario')
    beneficiary_position_id = fields.Many2one('plaft.position',string=u'Cargo en la Empresa Beneficiario')
    beneficiary_legal_address = fields.Char(string=u'Direccion Legal Beneficiario')
    beneficiary_depaubigeo = fields.Many2one("res.country.state",string=u"Departamento Beneficiario")
    beneficiary_provubigeo = fields.Many2one("res.city",string=u"Provincia Beneficiario")
    beneficiary_distubigeo = fields.Many2one("l10n_pe.res.city.district",string=u"Distrito Beneficiario")
    beneficiary_movil_client = fields.Char(string=u'Telefono Movil Beneficiario')

    # type_found = fields.Char(string=u'Tipo de Fondo')
    # type_operating = fields.Char(string=u'Tipo de Operacion')
    # description_operation = fields.Char(string=u'Descripcion de Operacion')
    # source_founds = fields.Char(string=u'Origen de Los Fondos')
    original_currency_id = fields.Many2one(comodel_name='res.currency',string='Moneda Original')
    # source_founds = fields.Char(string=u'Origen de Los Fondos')
    original_amount = fields.Float(string=u'Importe Original',digits=(9,2))
    exchange_rate = fields.Float(string=u'Tipo de Cambio',digits=(9,3))
    equivalent_amount = fields.Float(string=u'Monto Equivalente(USD)',digits=(9,4))
    
    # supervised_company_1 = fields.Char(string=u'Empresa Supervisada 1')
    # account_type_1 = fields.Char(string=u'Tipo de Cuenta Involucrada 1')
    # interbank_account_1 = fields.Char(string=u'Tipo de Cuenta Interbancaria 1')
    # foreig_identity_1 = fields.Char(string=u'Entidad Del Exterior 1')
    
    # supervised_company_2 = fields.Char(string=u'Empresa Supervisada 2')
    # account_type_2 = fields.Char(string=u'Tipo de Cuenta Involucrada 2')
    # interbank_account_2 = fields.Char(string=u'Tipo de Cuenta Interbancaria 2')
    # foreignentity_2 = fields.Char(string=u'Entidad Del Exterior 2')
    
    # operation_reach = fields.Char(string=u'Alcance de la Operacion')
    origin_country_id = fields.Many2one('res.country',string=u'Pais Origen')
    destination_country_id = fields.Many2one('res.country',string=u'Pais Destino')
    # intermediary_operation = fields.Char(string=u'Intermediario de la Operacion')
    # form_operation = fields.Char(string=u'Forma de la Operacion')
    # name_operation = fields.Char(string=u'Descripcion de la Forma de Operacion')
    
    state = fields.Selection(string='Estado', selection=[('aprobado', 'Aprobado'), ('anulado', 'Anulado'),])
    ro_type = fields.Selection(string='Tipo de RO', selection=[('unique', 'Operacion Unica'), ('multiple', 'Operacion Multible'),('both','Ambas')])
    
    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('plaft.ro.declaration.sequence') or '000'
        result = super(Declaration_RO, self).create(vals)
        return result