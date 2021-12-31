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

import string, random

def homologant(self,model_name,var,field=False):
    obj = self.env['ir.glossary'].search([('model_id','=',model_name)])
    for homo in obj.homologant_ids:
        if homo.init_key == var and homo.field_key == field:
            if bool(homo.relation_id) is False:
                return homo.final_key
            else:
                return homo.relation_id