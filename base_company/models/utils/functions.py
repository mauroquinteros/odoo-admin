# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2020
#    Author      :  JetPERU
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

def transform_internal_code(id_pricelist):
        return f'0{id_pricelist}' if len(id_pricelist) == 1 else id_pricelist

def check_pos_and_agency(self, agency, point):
    """#Arguments:
    @agency: variable that expresses one object res.partner.agency
    @point: variable that expresses one object pos.config"""
    msg = ""
    if len(point) < 1:
        msg = "-El usuario no tiene un punto de operación configurada\n"
    if len(point.agency_id) is 0:
        msg += "-El punto de venta asignado al usuario, no tiene una agencia relacionada\n"
    if len(agency) is 0:
        msg += "-El usuario no tiene una Agencia Asignada\n"
    return msg

def open_current(obj,view):
    return {
        'name': obj._description,
        "context": obj.env.context,
        "view_mode": "form",
        'res_model': obj._name,
        'res_id': obj.id,
        'view_id': obj.env.ref(view).id,
        "type": "ir.actions.act_window",
        "target": "current",
    }

def return_context_ro(self,business,channel,performer,receiver,beneficiary,ctx_model=False,ctx_id=False):
    if self.env.ref(business,False).foreign_code == 'bsln001':
        performer_id = performer
        receiver_id = performer
        beneficiary_id = performer
    elif self.env.ref(business,False).foreign_code == 'bsln005':
        performer_id = performer
        receiver_id = receiver
        beneficiary_id = beneficiary
    elif self.env.ref(business,False).foreign_code == 'bsln006':
        performer_id = performer
        receiver_id = performer
        beneficiary_id = beneficiary
    else:
        performer_id = False
        receiver_id = False
        beneficiary_id = False

    ctx = {
        'payment_model': ctx_model,
        'payment_ide': ctx_id,
        'businessline': self.env.ref(business,False).id,
        'channel':self.env.ref(channel,False).id,

        'default_payer_type_person': performer_id.contrib_type_id,
        'default_payer_ide_document': performer_id.l10n_latam_identification_type_id.id,
        'default_payer_document': performer_id.vat,
        'default_payer_name_paternal': performer_id.lastname,
        'default_payer_name_maternal': performer_id.motherlastname,
        'default_payer_name_client': performer_id.firstname,
        'default_payer_occupation_id': performer_id.occupation_id.id,
        'default_payer_code_ciiu_id': performer_id.code_ciiu_id.id,
        'default_payer_position_id': performer_id.position_id.id,
        'default_payer_legal_address': str(performer_id.street) + ' ' + str(performer_id.street2),
        'default_payer_depaubigeo': performer_id.state_id.id,
        'default_payer_provubigeo': performer_id.city_id.id,
        'default_payer_distubigeo': performer_id.l10n_pe_district.id,
        'default_payer_movil_client': performer_id.mobile or performer_id.phone,

        'default_performer_type_person': receiver_id.contrib_type_id,
        'default_performer_ide_document': receiver_id.l10n_latam_identification_type_id.id,
        'default_performer_document': receiver_id.vat,
        'default_performer_name_paternal': receiver_id.lastname,
        'default_performer_name_maternal': receiver_id.motherlastname,
        'default_performer_name_client': receiver_id.firstname,
        'default_performer_occupation_id': receiver_id.occupation_id.id,
        'default_performer_code_ciiu_id': receiver_id.code_ciiu_id.id,
        'default_performer_position_id': receiver_id.position_id.id,
        'default_performer_legal_address': str(receiver_id.street) + ' ' + str(receiver_id.street2),
        'default_performer_depaubigeo': receiver_id.state_id.id,
        'default_performer_provubigeo': receiver_id.city_id.id,
        'default_performer_distubigeo': receiver_id.l10n_pe_district.id,
        'default_performer_movil_client': receiver_id.mobile or receiver_id.phone,

        'default_beneficiary_type_person': beneficiary_id.contrib_type_id,
        'default_beneficiary_ide_document': beneficiary_id.l10n_latam_identification_type_id.id,
        'default_beneficiary_document': beneficiary_id.vat,
        'default_beneficiary_name_paternal': beneficiary_id.lastname,
        'default_beneficiary_name_maternal': beneficiary_id.motherlastname,
        'default_beneficiary_name_client': beneficiary_id.firstname,
        'default_beneficiary_occupation_id': beneficiary_id.occupation_id.id,
        'default_beneficiary_code_ciiu_id': beneficiary_id.code_ciiu_id.id,
        'default_beneficiary_position_id': beneficiary_id.position_id.id,
        'default_beneficiary_legal_address': str(beneficiary_id.street) + ' ' + str(beneficiary_id.street2),
        'default_beneficiary_depaubigeo': beneficiary_id.state_id.id,
        'default_beneficiary_provubigeo': beneficiary_id.city_id.id,
        'default_beneficiary_distubigeo': beneficiary_id.l10n_pe_district.id,
        'default_beneficiary_movil_client': beneficiary_id.mobile or beneficiary_id.phone,
        }
    return ctx