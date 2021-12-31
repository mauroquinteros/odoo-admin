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

def dynamic_notify(self,comment,mode):
    if mode == 'success':
        return self.env.user.notify_success(message=comment)
    if mode == 'warning':
        return self.env.user.notify_warning(message=comment)
    if mode == 'danger':
        return self.env.user.notify_danger(message=comment)
    if mode == 'info':
        return self.env.user.notify_info(message=comment)

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

def PO_review_existing(self, obj, res = False):
    pay_order = self.env['pay.order']
    model_ref = '%s,%s' % (obj._name, obj.id)
    if pay_order.sudo().search([('operation_ref','=', model_ref)]).id is False:
        res = True
    return res