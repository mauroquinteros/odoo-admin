# -*- coding: utf-8 -*-
{
    "name": "Lista de Precios (Servicios)",
    "summary": """Registros de Servicios basado en la empresa.""",
    "description": """
    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    "category": "Product/Services",
    "version": "13.1.1.4",
    "development_status": "Beta",
    "maintainers": ["Carlos Enrique", "Mauro Quinteros"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>', 'Mauro Quinteros <quinterosmauro0599@gmail.com>'],
    "license": "AGPL-3",
    'qweb' : [],
    'demo': [],
    'test': [],
    'images': [],
    "depends": ['base', 'account', 'product', 'base_company'],
    "data": [
        "security/ir.model.access.csv",

        'data/account_taxes_data.xml',
        'data/product_template_data.xml',
        'data/service_type_list_data.xml',
        'data/service_pricelist_data.xml',
        'data/service_pricelist_detail_data.xml',
        'data/service_pricelist_item_data.xml',
        'data/product.pricelist.csv',
        'data/res_partner_agency_data.xml',

        'views/remittance_exchange_rate_views.xml',
        'views/service_pricelist_views.xml',
        'views/service_pricelist_detail_views.xml',
        'views/service_pricelist_item_views.xml',
        'views/service_type_list_views.xml',

        'views/xpath/xpath_agency_views.xml',
        'views/xpath/xpath_correspondent_views.xml',

        'views/wizard/add_pricelist_agency.xml',
    ],
    "application": False,
    'installable': True,
    "auto_install": False,
    "sequence": 5,
}