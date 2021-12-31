# -*- coding: utf-8 -*-
{
    "name": "Envío de Remesas",
    "summary": """
        - Cotizaciones
        - Validación con tesorería
        - Validación con cumplimiento legal
        - Envío de remesa a través de API""",
    "description": """
        - Cotizaciones
        - Validación con tesorería
        - Validación con cumplimiento legal
        - Envío de remesa a través de API
    """,
    "author": "JetPERU",
    "website": "http://www.jetperu.com.pe",
    "maintainers": ["Mauro Quinteros"],
    "contributors": [
        "Mauro Quinteros <quinterosmauro0599@gmail.com>",
    ],
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Sales/RemSend",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "sale",
        "sale_management",
        "sale_config",
        "product_services",
    ],
    # always loaded
    "data": [
        'data/ir.config_parameter.csv',
        'data/mail_data.xml',

        'docs/report_quote.xml',

        "views/config_static_views.xml",
        "views/wizard/assistant_remittance_price_view.xml",
        "views/sale/sale_remittance_views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
