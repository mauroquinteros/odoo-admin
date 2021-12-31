# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2020.
#    Author      :  Carlos Enrique Paico
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import models, fields, api
from odoo.osv import expression

class AnexoTmpl(models.Model):
    _name = 'l10n_pe_sunat.anexo.tmpl'
    _description = 'Anexo Template'

    active = fields.Boolean(string='Active', default=True)
    code = fields.Char(string='Code', size=4, index=True, required=True)
    name = fields.Char(string='Description', index=True, required=True)

    def name_get(self):
        result = []
        for table in self:
            result.append((table.id, "%s %s" % (table.code, table.name or '')))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        ids = self._name_search(name, args, operator, limit=limit)
        return self.browse(ids).sudo().name_get()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('code', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name +=  table.name
            result.append((table.id, l_name ))
        return result

class anexo01(models.Model):
    _name = "l10n_pe_sunat.anexo.01"
    _description = 'TABLA ANEXA Nº 1: CIIU (CLASIFICACIÓN INDUSTRIAL INTERNACIONAL UNIFORME)'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'

    """
    La CIIU (Clasificación Industrial Internacional Uniforme) es una clasificación de actividades cuyo 
    alcance abarca a todas las actividades económicas, las cuales se refieren tradicionalmente a las actividades 
    productivas, es decir, aquellas que producen bienes y servicios. En el país, el Instituto Nacional de Estadística 
    e Informática (INEI) ha establecido oficialmente la adopción de la nueva revisión de la Clasificación Industrial 
    Internacional Uniforme de todas las actividades económicas (CIIU Revisión 4), lo cual permitirá establecer un esquema 
    conceptual uniforme a fin de contar con información más real a nivel de empresas y establecimientos productivos de 
    bienes y servicios. Es por ello que la SUNAT ha implementado la incorporación de la nueva CIUU Revisión 4 dentro de 
    sus registros del RUC (actualmente la actividad económica es un dato importante en el registro del RUC y constituye 
    una información obligatoria a declarar en el referido padrón). Cabe señalar que la anterior Clasificación del CIIU 
    (Revisión 3) no permitía generar un perfil adecuado del contribuyente, lo que dificulta la adecuada programación de las 
    acciones de la Administración Tributaria por tipo de actividad económica (lo cual incluye las acciones de inducción, 
    orientación y asistencia sectorial). La importancia de incorporar esta nueva clasificación CIUU (Revisión 4) radica en 
    que su uso permitirá contar con información actualizada y detallada que refleje de mejor manera la actividad económica, 
    lo cual se traduce en servicios más personalizados al conocer mejor la real actividad de los contribuyentes.
    """

    version_ciiu = fields.Selection(string='Version CIIU',selection=[('v1', 'CIIU 1.0'), ('v2', 'CIIU 2.0'), ('v3', 'CIIU 3.0'), ('v4', 'CIIU 4.0')])
    
    
class anexo02(models.Model):
    _name = "l10n_pe_sunat.anexo.02"
    _description = 'TABLA ANEXA Nº 2: TIPO DE CONTRIBUYENTE'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'

    """
    Los contribuyentes deben consignar el código de tipo de contribuyente de acuerdo a la 
    forma bajo la cual están constituidos, ya sea como persona natural, sociedad conyugal, 
    sucesión indivisa, personas jurídicas, sociedades irregulares o cualquier otra forma 
    colectiva de constitución
    """
    type = fields.Selection(string='Tipo', selection=[('person', 'Persona'), ('company', 'Compañía')])
    
class anexo03(models.Model):
    _name = "l10n_pe_sunat.anexo.03"
    _description = 'TABLA ANEXA Nº 3: TIPO DE ZONA'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'

    """
    Se refiere a la denominación que designa la zona en la que se ubica el domicilio fiscal del contribuyente.
    """
    
class anexo04(models.Model):
    _name = "l10n_pe_sunat.anexo.04"
    _description = 'TABLA ANEXA Nº 4: TIPO DE VIA'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'

    """
    Se refiere a la denominación establecida para la vía específica en la que se encuentra ubicado el domicilio fiscal del contribuyente.
    """
    
class anexo05(models.Model):
    _name = "l10n_pe_sunat.anexo.05"
    _description = 'TABLA ANEXA Nº 5: DOCUMENTO DE IDENTIDAD'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'

    """
    Documentos de identidad válidos para la identificación del contribuyente o del representante legal ante la SUNAT.
    """    
    
class anexo06(models.Model):
    _name = "l10n_pe_sunat.anexo.06"
    _description = 'TABLA ANEXA Nº 6: SEXO'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'

    """
    En el caso de personas naturales se consignará el sexo correspondiente al contribuyente.
    """
    
class anexo07(models.Model):
    _name = "l10n_pe_sunat.anexo.07"
    _description = 'TABLA ANEXA Nº 7: NACIONALIDAD'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'

class anexo08(models.Model):
    _name = "l10n_pe_sunat.anexo.08"
    _description = 'TABLA ANEXA Nº 8: CONDICION DE DOMICILIADO'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'

    """
    Los requisitos para considerar a una persona domiciliada o no domiciliada se encuentran en la Ley del Impuesto a la Renta.
    """

class anexo09(models.Model):
    _name = "l10n_pe_sunat.anexo.09"
    _description = 'TABLA ANEXA Nº 9: ORIGEN DE LA ENTIDAD'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'
    
    """
    Se debe consignar el origen de la entidad ya sea nacional, extranjera o esté conformada por capitales mixtos.
    """
    
class anexo10(models.Model):
    _name = "l10n_pe_sunat.anexo.10"
    _description = 'TABLA ANEXA Nº 10:  CODIFICACION DE TRIBUTOS'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'
    
    """
    La afectación de tributos está en función de la renta que genere o el régimen por el que decida 
    optar y de acuerdo al tipo de contribuyente establecido en la Tabla Anexa N° 2.
    """
    
    short_code = fields.Char(string='Short Code', size=10, required=True)
    
class anexo11(models.Model):
    _name = "l10n_pe_sunat.anexo.11"
    _description = 'TABLA ANEXA Nº 11:  CODIGOS DE PROFESION U OFICIO'
    _inherit = 'l10n_pe_sunat.anexo.tmpl'
    
    """
    Las profesiones y oficios han sido codificados según la siguiente tabla anexa. 
    Si su profesión u oficio no está comprendido dentro de lo establecido en ella, 
    se optará por el código '99' : Profesión u ocupación no especificada.
    """
    