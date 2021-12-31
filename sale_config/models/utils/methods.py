# -*- coding: utf-8 -*-
from datetime import datetime
from . import values as sale_values


def get_operative_exchange_rate(agency):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener el tipo de cambio actual de la agencia
    """
    if agency.current_exchange_rate != 0:
        return agency.current_exchange_rate
    elif agency.current_exchange_rate == 0:
        return 0


def get_destination_amount_by_currency(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Calcular el monto que se va a pagar en la agencia destino según la moneda seleccionada
    """
    if self.destination_currency_id.name == self.destination_dollar_currency.name:
        self.destination_dollar_amount = self.origin_amount
        self.destination_local_amount = 0.0
        self.destination_euro_amount = 0.0
    elif self.destination_currency_id.name == self.destination_local_currency.name and self.agency_exchange_rate != 0:
        self.destination_local_amount = self.origin_amount * self.agency_exchange_rate
        self.destination_dollar_amount = 0.0
        self.destination_euro_amount = 0.0
    elif self.destination_currency_id.name == self.destination_euro_currency.name:
        self.destination_euro_amount = self.origin_amount
        self.destination_dollar_amount = 0.0
        self.destination_local_amount = 0.0
    else:
        self.destination_dollar_amount = 0.0
        self.destination_euro_amount = 0.0
        self.destination_local_amount = 0.0


def get_sended_amount_by_currency(self):
    if self.origin_currency_id.name == self.destination_dollar_currency.name:
        self.sended_dollar_amount = self.origin_amount
        self.sended_local_amount = 0.0
        self.sended_euro_amount = 0.0
    elif self.origin_currency_id.name == self.local_currency_id.name:
        self.sended_dollar_amount = self.origin_amount
        self.sended_local_amount = 0.0
        self.sended_euro_amount = 0.0
    elif self.origin_currency_id.name == self.destination_euro_currency.name:
        self.sended_dollar_amount = self.origin_amount
        self.sended_local_amount = 0.0
        self.sended_euro_amount = 0.0
    else:
        self.sended_dollar_amount = 0.0
        self.sended_local_amount = 0.0
        self.sended_euro_amount = 0.0


def validate_pricelist_range(pricelist_item, origin_amount, origin_currency, destination_currency, service_type_name=sale_values.default_service_type):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Validar que los campos de origin_amount, origin_currency y destination_currency se encuentren dentro del pricelist_item (devuelve True o False)
    """
    is_in_amount_range = True if origin_amount >= pricelist_item.initial_range and origin_amount <= pricelist_item.final_range else False
    # print("ESTA DENTRO DEL RANGO DE TARIFAS: ", is_in_amount_range)
    valid_currencies = True if origin_currency.id == pricelist_item.deposit_currency_id.id and destination_currency.id == pricelist_item.payment_currency_id.id else False
    # print("CONCUERDA CON LAS MONEDAS DE ORIGEN Y DESTINO: ", valid_currencies)
    is_service_type = True if service_type_name == pricelist_item.service_type.name else False
    # print("LOS SERVICIOS SON IGUALES: ", is_service_type)
    if is_in_amount_range and valid_currencies and is_service_type:
        return True
    else:
        return False


def get_pricelist_by_agency(self):
    """
    Desarrollador: Mauro Quinteros
    Cambios: Obtener el registro del rango del tarifario (service.pricelist.item) que coincida con los valores seleccionados
    """
    pricelist_id = self.destination_agency_id.pricelist_id
    pricelist_item_ids = self.destination_agency_id.pricelist_id.service_pricelist_item_ids

    today = datetime.now().strftime("%Y-%m-%d")
    deadline_date = pricelist_id.deadline_date.strftime('%Y-%m-%d')

    is_pricelist_founded = False
    pricelist_item_founded = {}

    if today <= deadline_date:
        # print("No supera el límite de vigencia")
        # print("Tarifario: ", pricelist_item_ids)
        for pricelist_item in pricelist_item_ids:
            if validate_pricelist_range(pricelist_item, self.origin_amount, self.origin_currency_id, self.destination_currency_id):
                pricelist_item_founded = pricelist_item
                is_pricelist_founded = True
                break
        if is_pricelist_founded == True:
            return pricelist_item_founded
        else:
            return False
    else:
        return False


def get_extra_service_pricelist(self, extra_service_id):
    """
    Desarrollador: Mauro Quinteros
    Cambios:
    """
    pricelist_item_ids = self.destination_agency_id.pricelist_id.service_pricelist_item_ids
    service_type_name = extra_service_id.name

    is_pricelist_founded = False
    pricelist_item_founded = {}

    for pricelist_item in pricelist_item_ids:
        # print("SERVICIO SELECCIONADO: ", service_type_name)
        # print("SERVICIO A COMPARAR: ", pricelist_item.service_type.name)
        if validate_pricelist_range(pricelist_item, self.origin_amount, self.origin_currency_id, self.destination_currency_id, service_type_name):
            # print("TARIFARIO ITEM CON UNO DE LOS SERVICIOS: ", pricelist_item)
            # print("SERVICIO ENCONTRADO: ", pricelist_item.service_type.name)
            pricelist_item_founded = pricelist_item
            is_pricelist_founded = True
            break
    if is_pricelist_founded == True:
        return pricelist_item_founded
    else:
        return False


def get_service_pricelist_amount(self, pricelist_item):
    if pricelist_item.price_expression == sale_values.price_expression_value.get("nominal"):
        return pricelist_item.price_amount
    if pricelist_item.price_expression == sale_values.price_expression_value.get("porcentual"):
        return self.origin_amount * pricelist_item.price_amount / 100


def calculate_with_tax_included(price_amount):
    base_amount = price_amount / 1.18
    igv_amount = price_amount - base_amount
    return {
        "base_amount": base_amount,
        "igv_amount": igv_amount
    }


def calculate_without_tax_included(price_amount):
    base_amount = price_amount
    igv_amount = base_amount * 0.18
    return {
        "base_amount": base_amount,
        "igv_amount": igv_amount
    }


def calculate_base_amount_igv(self, pricelist_item):
    price_amount = get_service_pricelist_amount(self, pricelist_item)
    if pricelist_item.tax_included is True:
        return calculate_with_tax_included(price_amount)
    else:
        return calculate_without_tax_included(price_amount)
