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
    "name": "Configuración en Ventas",
    "summary": """Cambios de Algoritmos y Data Precargada Ventas""",
    "description": """
    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    "category": "Sale/Config",
    "version": "13.1.1.2",
    "development_status": "Beta",
    "maintainers": ["Carlos Enrique", "Mauro Quinteros"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>', 'Mauro Quinteros <quinterosmauro0599@gmail.com>', ],
    "license": "AGPL-3",
    'qweb': [],
    'demo': [],
    'test': [],
    'images': [],
    "depends": ['account', 'sale', 'sale_management', 'base_company', 'account_treasury', 'l10n_pe_currency', 'mail_layout_extra'],
    "data": [
        'security/security_category.xml',
        'security/security_data.xml',
        'security/ir.model.access.csv',

        'data/mail_data.xml',
        'data/ir.config_parameter.csv',
        'data/account_payment_method.xml',
        'data/payment_acquirer_data.xml',

        'report/paperformat_sale_order.xml',

        'views/customer/sale_customer_limit_views.xml',

        'views/sale/sale_order_views.xml',
        'views/treasury/treasury_moex_online_views.xml',

        'views/plaft/requirement_pcl_views.xml',
    ],
    "application": False,
    'installable': True,
    "auto_install": False,
    "sequence": 9,
}
