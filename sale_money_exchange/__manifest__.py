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
    "name": "Ventas Cambio Divisas",
    "summary": """De Cotizaciones a Cambio de Divisas""",
    "description": """
    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    # "website": "http://www.jetperu.com.pe",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Sales/MoEx",
    "version": "1.2",
    "development_status": "Beta",
    "application": True,
    "installable": True,
    # "auto_install": True,
    "maintainers": ["Carlos Enrique"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>'],
    "license": "AGPL-3",
    # any module necessary for this one to work correctly

    "depends": ['sale', 'sale_management', 'sale_config'],
    # always loaded
    "data": [
        'security/security_category.xml',
        'security/security_data.xml',
        'security/ir.model.access.csv',

        'data/mail_data.xml',
        'data/ir.config_parameter.csv',

        'docs/ro_declaration_report.xml',
        'docs/pay_order_ticket.xml',
        'docs/quote_newsletter.xml',

        'report/report_customer_so.xml',
        'report/report_day_so.xml',
        'report/report_moex_so.xml',
        'report/report_pending_so.xml',

        'views/sale/sale_order_moex_views.xml',
        'views/wizard/money_exchange_sale_order_wizard.xml',
    ],
    "sequence": 10,
}