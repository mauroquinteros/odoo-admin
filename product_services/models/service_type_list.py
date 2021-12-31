# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.addons.base_company.models.utils.functions import transform_internal_code


class ServiceTypeList(models.Model):
    _name="service.type.list"
    _description="Lista de tipo de servicios"

    internal_code = fields.Char(string='Código', required=True )
    name = fields.Char(string='Tipo del servicio')

    @api.model
    def create(self, values):
        """
        Desarrollador: Mauro Quinteros
        Cambios: Función para agregar el código de inicial para el tipo de servicios
        """
        len_service_type = self.env['service.type.list'].search_count([])
        id_service_type = transform_internal_code(str(len_service_type+1))

        values['internal_code'] = f'ST-{id_service_type}'
        result = super(ServiceTypeList, self).create(values)
        return result
