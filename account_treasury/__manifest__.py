# -*- coding: utf-8 -*-
{
    "name": "Contabilidad JetPERU",
    "summary": """
    """,
    'description' : """
Modulo Data Contable de la empresa (Complementario).
====================================

Tablas:
--------------------------------------------
    * account.analytic.group
    * account.analytic.account

Information:
--------------------------------------------
    * Analytics Details Update

    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    "category": "account",
    'version': '13.1.0.6',
    "development_status": "Beta",
    "maintainers": ["Carlos Enrique"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>'],
    "license": "AGPL-3",
    'qweb' : [],
    'demo': [],
    'test': [],
    'images': [],
    "depends": ['account','sale_management','base_company','product_services'],
    "data": [
        'security/security_category.xml',
        'security/security_data.xml',
        'security/ir.model.access.csv',

        'data/sequences.xml',
        'data/subtype_msg_data.xml',
        'data/account.analytic.group.csv',
        'data/account.analytic.account.csv',

        'doc/papper_format_treasury_peruvian.xml',

        'report/report_treasury_bank.xml',
        'report/report_treasury_resume_bank.xml',

        'views/res_bank_customize_views.xml',
        'views/pay_order_views.xml',
        'views/deposit_order_views.xml',

        'views/wizard/assistant_treasury_views.xml',
    ],
    "application": True,
    'installable': True,
    "auto_install": False,
    "sequence": 6,
}
