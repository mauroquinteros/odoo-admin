# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import fields
from . import values as sale_values

import base64

def validate_business_line(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Verificar el tipo de negocio relacionado a la venta
    """
    if self.env.context.get("business_line_key") == self.env.ref("base_company.business_line_006", False).foreign_code:
        return True
    else:
        return False


def is_empty_fields(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Validar los campos necesarios para realizar el cálculo de la remesa
        - origin_currency_id
        - origin_amount
        - destination_country_id
        - destination_agency_id
        - destination_currency_id
    """
    country_validate = True if self.destination_country_id.id != False else False
    agency_validate = True if self.destination_agency_id.id != False else False
    origin_currency_validate = True if self.origin_currency_id.id != False else False
    origin_amount_validate = True if self.origin_amount != 0 else False
    destination_currency_validate = True if self.destination_currency_id.id != False else False

    if (
        country_validate
        and agency_validate
        and origin_currency_validate
        and origin_amount_validate
        and destination_currency_validate
    ):
        return True
    else:
        return False

def is_empty_fields_amount(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Validar los campos necesarios para calcular el monto total a cobrar
    """
    if self.base_service_amount != 0 and self.igv_service_amount != 0:
        return True
    else:
        return False

def add_res_partner_beneficiary(result, values):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Agregar al beneficiario con el se realizo la operación a la relación entre el remitente y su histórico de beneficiarios
    """
    if len(result.partner_id.beneficiary_ids) > 0:
        beneficiary_ids = [item.id for item in result.partner_id.beneficiary_ids]
        if values.get('partner_beneficiary_id') not in beneficiary_ids:
            for record in result:
                record.partner_id.sudo().write({
                    'beneficiary_ids': [(4, values.get('partner_beneficiary_id'), 0)]
                })
    else:
        for record in result:
            record.partner_id.sudo().write({
                'beneficiary_ids': [(4, values.get('partner_beneficiary_id'), 0)]
            })

def get_local_currency(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener la moneda local del Perú
    """
    local_currency = self.env['res.currency'].search([('name', '=', 'PEN')])
    return local_currency

def get_itf_tax(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener el ITF que se encuentra en la tabla de impuestos
    """
    itf_tax = self.env['account.tax'].search([('name', '=', 'ITF')])
    return itf_tax

def get_local_currency_by_country(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener la moneda local del país a donde se va enviar la remesa
    """
    if self.destination_country_id.id != False:
        local_currency = self.destination_country_id.currency_id
        return local_currency

def get_correspondent_by_agency(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener el corresponsal de la agencia seleccionada
    """
    correspondent_by_agency = self.env["res.partner.correspondent"].search([
        ("id", "=", self.destination_agency_id.correspondent_id.id)
    ])
    return correspondent_by_agency

def get_exchange_rate_by_agency(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener el tipo de cambio actual de la agencia
    """
    if self.destination_agency_id.current_exchange_rate != 0:
        return self.destination_agency_id.current_exchange_rate
    elif self.destination_agency_id.current_exchange_rate == 0:
        return 0

def get_sale_product_templates(self):
    product_deposit_line = self.env['product.template'].search([('default_code', '=', sale_values.order_line_deposit_code)])
    product_remittance_line = self.env['product.template'].search([('default_code', '=', sale_values.order_line_remittance_code)])

    return [
        {'product_line': product_deposit_line, 'is_service': False},
        {'product_line': product_remittance_line, 'is_service': True}
    ]

def get_product_line(self, product_id):
    return self.env['product.product'].search([('product_tmpl_id','=',product_id.id)])

def validate_pricelist_range(pricelist_item, origin_amount, origin_currency, destination_currency, service_type_name):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Validar que los campos de origin_amount, origin_currency, destination_currency, service_type_name se encuentren dentro del pricelist_item (devuelve True o False)
    """
    is_in_amount_range = True if origin_amount >= pricelist_item.initial_range and origin_amount <= pricelist_item.final_range else False

    valid_currencies = True if origin_currency.id == pricelist_item.deposit_currency_id.id and destination_currency.id == pricelist_item.payment_currency_id.id else False

    is_service_type = True if service_type_name == pricelist_item.service_type.name else False

    if is_in_amount_range and valid_currencies and is_service_type:
        return True
    else:
        return False

def get_pricelist_item_by_agency(self, extra_service = sale_values.default_service_type):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener el registro del rango del tarifario (service.pricelist.item) que coincida con los valores seleccionados
    """
    response = {}
    if self.destination_agency_id.pricelist_id.id != False:
        pricelist_item_ids = self.destination_agency_id.pricelist_id.service_pricelist_item_ids
        deadline_date = self.destination_agency_id.pricelist_id.deadline_date.strftime('%Y-%m-%d')
        today = fields.Datetime.now().strftime("%Y-%m-%d")

        is_pricelist_founded = False
        pricelist_item_founded = None

        if today <= deadline_date:
            for pricelist_item in pricelist_item_ids:
                if validate_pricelist_range(pricelist_item, self.origin_amount,self.origin_currency_id, self.destination_currency_id, extra_service):
                    pricelist_item_founded = pricelist_item
                    is_pricelist_founded = True
                    break
            if is_pricelist_founded == True:
                response.update({
                    'success': True,
                    'pricelist_item': pricelist_item_founded,
                    'error': False
                })
            else:
                response.update({
                    'success': False,
                    'message': "No se ha encontrado una tarifa para los campos seleccionados!",
                    'error': True
                })
        else:
            response.update({
                'success': False,
                'message': "La fecha de vigencia del tarifario de la agencia ha vencido!",
                'error': True
            })
    else:
        response.update({
            'success': False,
            'message': "La agencia seleccionada no tiene un tarifario!",
            'error': True
        })
    return response

def get_destination_amount_by_currency(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Calcular el valor del monto a enviar dependiendo desde el modelo en el que se llama
    """
    local_currency = get_local_currency_by_country(self)
    if self._name == "sale.order":
        destination_amount = get_amount_sale_order(self, local_currency)
        return destination_amount
    if self._name == "assistant.remittance.price":
        pass

def get_amount_sale_order(self, local_currency):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Calcular el valor del monto a enviar según la moneda seleccionada para el modelo de sale.order
    """
    if self.origin_currency_id.id == self.destination_currency_id.id:
        return self.origin_amount
    elif self.origin_currency_id.id != self.destination_currency_id.id and self.destination_currency_id.id == local_currency.id:
        return self.origin_amount * self.destination_exchange_rate
    else:
        return 0.00

def reset_extra_service_amounts(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Reiniciar los valores del monto base e IGV de los servicios extra
    """
    if self.base_extra_service_amount > 0 and self.igv_extra_service_amount > 0:
        self.base_extra_service_amount = 0
        self.igv_extra_service_amount = 0

def get_base_igv_amount(self, result, service_type = sale_values.default_service_type):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Calcular el monto base y el IGV según el tipo de servicio
    """
    pricelist = result['pricelist_item']
    amount_pricelist = calculate_base_amount_igv(self, pricelist, self.origin_amount)

    if service_type == sale_values.default_service_type:
        self.base_service_amount = amount_pricelist.get("base_amount")
        self.igv_service_amount = amount_pricelist.get("igv_amount")

    if service_type != sale_values.default_service_type:
        self.base_extra_service_amount += amount_pricelist.get("base_amount")
        self.igv_extra_service_amount += amount_pricelist.get("igv_amount")

def calculate_base_amount_igv(self, pricelist_item, origin_amount):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Calcular el monto base y el IGV
    """
    price_amount = get_service_pricelist_amount(self, pricelist_item, origin_amount)
    if pricelist_item.tax_included == True:
        return calculate_with_tax_included(price_amount)
    else:
        return calculate_without_tax_included(price_amount)

def get_service_pricelist_amount(self, pricelist_item, origin_amount = 0):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Calcular la tarifa del servicio (puede incluir o no el IGV) que se obtiene de los valores seleccionados y convertir de moneda extranjera a soles peruanos si es necesario
    """
    if pricelist_item.price_expression == sale_values.price_expression_value["nominal"] and pricelist_item.price_currency_id.id != False:
        if pricelist_item.price_currency_id.id != self.local_currency_id.id:
            get_operative_exchange_rates(self, pricelist_item.price_currency_id, self.local_currency_id)
            return pricelist_item.price_amount * self.orp_exchange_rate
        else:
            return pricelist_item.price_amount

    if pricelist_item.price_expression == sale_values.price_expression_value["porcentual"] and pricelist_item.price_currency_id.id == False:
        if pricelist_item.price_currency_id.id != self.local_currency_id.id:
            get_operative_exchange_rates(self, self.origin_currency_id, self.local_currency_id)
            converted_amount = origin_amount * pricelist_item.price_amount / 100
            return converted_amount * self.orp_exchange_rate
        else:
            return origin_amount * pricelist_item.price_amount / 100

def calculate_with_tax_included(price_amount):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Calcular el monto base y el igv si la tarifa obtenido ya tiene incluido el IGV
    """
    base_amount = price_amount / 1.18
    igv_amount = price_amount - base_amount
    return {
        "base_amount": base_amount,
        "igv_amount": igv_amount
    }

def calculate_without_tax_included(price_amount):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Calcular el monto base y el igv si tarifa obtenido no tiene incluido el IGV
    """
    base_amount = price_amount
    igv_amount = base_amount * 0.18
    return {
        "base_amount": base_amount,
        "igv_amount": igv_amount
    }

def get_operative_exchange_rates(self, origin_currency, destination_currency):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener el tipo de cambio según las monedas pasadas como parámetro
    """
    operative_exchange_rate = devolve_query_exrate(self, {
        'agency': self.env.user.agency_id,
        'origin': origin_currency,
        'destination': destination_currency
    })

    self.orp_exchange_rate = operative_exchange_rate.price_orp
    self.drs_exchange_rate = operative_exchange_rate.price_drs

def devolve_query_exrate(self, obj, Number=1):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener el tipo de cambio según la moneda origen, la moneda destino y la agencia
    """
    query = ['|',
             '&', ('currentactive', '=', True), '&', ('agency_id', '=', obj['agency'].id),
             '&', ('origin_currency_id', '=', obj['origin'].id), ('destination_currency_id', '=', obj['destination'].id),
             '&', ('currentactive', '=', True), '&', ('agency_id', '=', obj['agency'].id),
             '&', ('origin_currency_id', '=', obj['destination'].id), ('destination_currency_id', '=', obj['origin'].id)]
    return self.env['res.currency.rate.oer'].search(query, limit=Number)

def round_float(float_number):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Convertir un número flotante o entero a un número de 2 decimales
    """
    converted_float = format(float_number, ".2f")
    return converted_float

def get_order_line(self, values):
    product_templates = get_sale_product_templates(self)

    param = self.env["ir.config_parameter"].sudo()
    origin_currency = self.env["res.currency"].browse(values.get("origin_currency_id"))
    local_currency = self.env["res.currency"].browse(values.get("local_currency_id"))

    order_line = []
    converted_origin_amount = values['origin_amount']*values['orp_exchange_rate']

    for product in product_templates:
        product_line = get_product_line(self, product['product_line'])
        line = (0, 0, {
            "product_id": product_line.id,
            "name": product['product_line'].name,
            "product_uom_qty": 1.0,
            "price_unit": values['total_service_amount'] if product['is_service'] else converted_origin_amount,
            "tax_id": product['product_line'].taxes_id.ids,
        })
        order_line.append(line)

    order_line.extend([(
        0, 0, {
            "name": "Resumen",
            "display_type": "line_section"
        }
    ), (
        0, 0, {
            "name": param.get_param("summary.scheme.order.line") % (
                origin_currency.symbol,
                round_float(values['origin_amount']),
                origin_currency.currency_unit_label,
                local_currency.symbol,
                round_float(converted_origin_amount),
                local_currency.currency_unit_label,
                local_currency.symbol,
                round(values['orp_exchange_rate'], 4)
            ),
            "display_type": "line_note"
        }
    )])
    return order_line

def attach_pdf_mail(self, name, report_id, record_id):
    attachment = False
    pdf = report_id.render_qweb_pdf(record_id)
    b64_pdf = base64.b64encode(pdf[0])
    att_name = name + '.pdf'
    att_id = self.env['ir.attachment'].create({
        'name': att_name,
        'type': 'binary',
        'datas': b64_pdf,
        'store_fname': att_name,
        'res_model': self._name,
        'res_id': self.id,
        'mimetype': 'application/pdf'
    })

    attachment = att_id
    return attachment

"""
    Mover a otro archivo
"""
def create_summary_scheme(self, result, values):
    orp_exchange_rate = values.get('orp_exchange_rate')
    drs_exchange_rate = values.get('drs_exchange_rate')
    local_currency = values.get('local_currency')
    origin_currency = values.get('origin_currency')

    local_amounts = get_amounts_array(
        origin_currency,
        local_currency,
        values.get('origin_amount'),
        values.get('service_amount'),
        orp_exchange_rate,
    )
    exchange_amounts = get_amounts_array(
        origin_currency,
        local_currency,
        values.get('origin_amount'),
        values.get('service_amount'),
        drs_exchange_rate,
        False
    )

    scheme = ''
    body_scheme = ''
    header_scheme = '<section class="row">'
    footer_scheme = '</section>'

    scheme += header_scheme
    for i in range(2):
        if i == 0:
            title = "Monto Total en %s (%s)" % (local_currency.name, local_currency.symbol)
            body_scheme += create_section_scheme(title, local_currency.symbol, local_amounts)
        elif i == 1:
            title = "Monto Total en %s (%s)" % (origin_currency.name, origin_currency.symbol)
            body_scheme += create_section_scheme(title, origin_currency.symbol, exchange_amounts)
    scheme += body_scheme
    scheme += footer_scheme
    return scheme

def create_section_scheme(title, currency_symbol, amounts_array):
    scheme = ''

    header_scheme = '<section class="col-sm-6 col-md-6"><article><h4 class="summary_title_group">%s</h4><div>'
    footer_scheme = '</div></article></section>'
    body_scheme = ''

    scheme += header_scheme % (title)
    for amount in amounts_array:
        if "T/C" in amount['title']:
            body_scheme += '<div class="summary_input_group"><span class="summary_label">%s</span><span>%s</span></div>' % (amount['title'], amount['amount'])
        elif amount['title'].lower() == 'TOTAL'.lower():
            body_scheme += '<div class="mt-2 py-2 border-top border-primary summary_input_main_group"><span class="summary_label">%s</span><span>%s %s</span></div>' % (amount['title'], currency_symbol, amount['amount'])
        else:
            body_scheme += '<div class="summary_input_group"><span class="summary_label">%s</span><span>%s %s</span></div>' % (amount['title'], currency_symbol, amount['amount'])
    scheme += body_scheme
    scheme += footer_scheme
    return scheme

def get_amounts_array(origin_currency, local_currency, origin_amount, service_amount, exchange_rate, local=True):
    if origin_currency.id != local_currency.id:
        total_amount = 0
        converted_amount = 0
        exchange_rate = round(exchange_rate, 4)
        if local == True:
            converted_amount = origin_amount * exchange_rate
            total_amount = converted_amount + service_amount
            return [
                {
                    "title": "T/C Compra",
                    "amount": exchange_rate
                },
                {
                    "title": "Monto",
                    "amount": round_float(converted_amount)
                },
                {
                    "title": "Comisión",
                    "amount": round_float(service_amount)
                },
                {
                    "title": "Total",
                    "amount": round_float(total_amount)
                }
            ]
        else:
            origin_amount = origin_amount
            converted_amount = service_amount / exchange_rate
            total_amount = origin_amount + converted_amount
            return [
                {
                    "title": "T/C Venta",
                    "amount": exchange_rate
                },
                {
                    "title": "Monto",
                    "amount": round_float(origin_amount)
                },
                {
                    "title": "Comisión",
                    "amount": round_float(converted_amount)
                },
                {
                    "title": "Total",
                    "amount": round_float(total_amount)
                }
            ]

def create_detail_scheme(self):
    local_currency = self.local_currency_id.symbol
    dollar_currency = self.env.ref("base.USD").symbol
    euro_currency = self.env.ref("base.EUR").symbol

    scheme = ''
    body_scheme = ''
    header_scheme = '<section class="d-flex justify-content-center align-items-center p-2"><div class="card shadow border-primary"><div class="card-header"><h3 class="m-0 text-center summary_title_group"><span class="fa fa-money mr-2"/>Detalle de la Remesa</h3></div><div class="card-body">'
    header_body_scheme = '<div class="detail_group separator_group detail_submain_group"><p></p><p>Dolares</p><p>Euros</p><p>Soles</p></div>'

    scheme += header_scheme
    body_scheme += header_body_scheme
    scheme_array = get_detail_amounts_array(self)
    for item in scheme_array:
        if item['title'].lower() == "Impuesto".lower():
            body_scheme += '<div class="detail_group separator_group"><p>%s</p><p>%s %s</p><p>%s %s</p><p>%s %s</p></div>' % (
                item['title'], dollar_currency, item['dollar_amount'], euro_currency, item['euro_amount'], local_currency, item['local_amount']
            )
        elif item['title'].lower() == "Total Venta".lower():
            body_scheme += '<div class="detail_group detail_submain_group"><p>%s</p><p>%s %s</p><p>%s %s</p><p>%s %s</p></div>' % (
                item['title'], dollar_currency, item['dollar_amount'], euro_currency, item['euro_amount'], local_currency, item['local_amount']
            )
        elif item['title'].lower() == "ITF".lower():
            body_scheme += '<div class="detail_group separator_group"><p>%s</p><p>%s %s</p><p>%s %s</p><p>%s %s</p></div>' % (
                item['title'], dollar_currency, item['dollar_amount'], euro_currency, item['euro_amount'], local_currency, item['local_amount']
            )
        elif item['title'].lower() == "Total".lower():
            body_scheme += '<div class="detail_group detail_main_group"><p>%s</p><p>%s %s</p><p>%s %s</p><p>%s %s</p></div>' % (
                item['title'], dollar_currency, item['dollar_amount'], euro_currency, item['euro_amount'], local_currency, item['local_amount']
            )
        else:
            body_scheme += '<div class="detail_group"><p>%s</p><p>%s %s</p><p>%s %s</p><p>%s %s</p></div>' % (
                item['title'], dollar_currency, item['dollar_amount'], euro_currency, item['euro_amount'], local_currency, item['local_amount']
            )
    scheme += body_scheme
    footer_scheme = '</div></div></section>'
    scheme += footer_scheme
    return scheme

def get_detail_amounts_array(self):
    scheme_array =  [
        {
            "title": "Servicio",
            "dollar_amount": round_float(0.00),
            "euro_amount": round_float(0.00),
            "local_amount": round_float(self.total_base_service_amount)
        },
        {
            "title": "Impuesto",
            "dollar_amount": round_float(0.00),
            "euro_amount": round_float(0.00),
            "local_amount": round_float(self.total_igv_service_amount)
        },
        {
            "title": "Total Venta",
            "dollar_amount": round_float(0.00),
            "euro_amount": round_float(0.00),
            "local_amount": round_float(self.sub_total_service_amount)
        }
    ]
    scheme_array.append(get_remittance_amout_by_currency(self, "Remesa", self.origin_amount))
    scheme_array.append(
        {
            "title": "ITF",
            "dollar_amount": round_float(0.00),
            "euro_amount": round_float(0.00),
            "local_amount": round_float(self.itf_service_amount)
        }
    )
    scheme_array.append(get_total_amout_by_currency(self, "Total", self.origin_amount, self.total_service_amount))
    return scheme_array

def get_remittance_amout_by_currency(self, title, amount):
    item = {
        "title": title,
        "dollar_amount":round_float(0.00),
        "euro_amount": round_float(0.00),
        "local_amount": round_float(0.00)
    }
    amount = round_float(amount)
    if self.origin_currency_id.name == "USD":
        item['dollar_amount'] = amount
    elif self.origin_currency_id.name == "EUR":
        item['euro_amount'] = amount
    elif self.origin_currency_id.name == "PEN":
        item['local_amount'] = amount
    return item

def get_total_amout_by_currency(self, title, origin_amount, service_amount):
    item = {
        "title": title,
        "dollar_amount":round_float(0.00),
        "euro_amount": round_float(0.00),
        "local_amount": round_float(0.00)
    }
    converted_origin_amount = round_float(origin_amount)
    converted_service_amount = round_float(service_amount)
    if self.origin_currency_id.id == self.local_currency_id.id:
        item["local_amount"] = round_float(origin_amount + service_amount)
    elif self.origin_currency_id.name == "USD":
        item["dollar_amount"] = converted_origin_amount
        item["local_amount"] = converted_service_amount
    elif self.origin_currency_id.name == "EUR":
        item["euro_amount"] = converted_origin_amount
        item["local_amount"] = converted_service_amount
    return item
