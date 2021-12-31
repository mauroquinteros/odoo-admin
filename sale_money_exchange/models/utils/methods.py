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

import base64

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

def target_sequence_pos(self, values):
    for pos in self.env.user.pos_ids:
        if pos.agency_id.agency_code == self.env.ref('base_company.agency_virtual_009').agency_code:
            sequence = self.env["ir.sequence"].next_by_code("correlative.quote")
            for correlative in pos.correlative_ids:
                if correlative.ir_sequence_id.id == self.env.ref('base_company.correlative_quote').id:
                    correlative.sudo().write({'i_number': correlative.ir_sequence_id.number_next_actual - 1})

def locate_product(self, product_id):
    return self.env['product.product'].search([('product_tmpl_id','=',product_id.id)])

def attach_ro_send(self,name,report_id,record_id):
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