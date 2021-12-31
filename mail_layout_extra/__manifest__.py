# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2020.
#    Authors      :  JET PERU, Carlos Enrique Paico <EnriqueZav96@gmail.com>
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

{
    "name": "Plantillas de Correo Customizadas",
    "summary": """Módulo para agregar plantillas nuevas.""",
    "description": """
    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    # "website": "http://www.jetperu.com.pe",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Mail",
    "version": "1.4",
    "development_status": "Beta",
    "application": True,
    "installable": True,
    # "auto_install": True,
    "maintainers": ["Carlos Enrique"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>'],
    "license": "AGPL-3",
    # any module necessary for this one to work correctly

    "depends": [
    ],
    # always loaded
    "data": [
        'data/mail_layout_data.xml',
    ],
    "sequence": 8,
}