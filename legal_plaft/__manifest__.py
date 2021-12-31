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
    "name": "Cumplimiento Legal - Plaft",
    "summary": """
        Módulo para registrar data oficial de cumplimiento legal""",
    "description": """
    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Legal/Plaft",
    "version": "13.0.0.2",
    "development_status": "Beta",
    "maintainers": ["Carlos Enrique", "Jhosmel Patricio"],
    "contributors": ["Carlos Enrique Paico <EnriqueZav96@gmail.com>"],
    "license": "AGPL-3",
    "qweb": [],
    "demo": [],
    "test": [],
    "images": [],
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "l10n_latam_base",
        "l10n_pe",
        "l10n_pe_sunat",
        "base_config",
    ],
    # always loaded
    "data": [
        "security/security_category.xml",
        "security/security_data.xml",
        "security/ir.model.access.csv",
        "data/correlatives_data.xml",
        "data/plaft.risk.csv",
        "data/plaft.risk.age.csv",
        "data/plaft.position.csv",
        "data/plaft.status.civil.list.csv",
        "data/plaft_document_category_data.xml",
        "data/plaft_regimen_data.xml",
        "data/plaft_control_category_data.xml",
        "data/plaft_documentation_type_data.xml",
        "data/l10n_latam_identification_type.xml",
        "views/res_partner_plaft_views.xml",
        "views/plaft_risk_views.xml",
        "views/plaft_risk_age_views.xml",
        "views/plaft_civil_status_views.xml",
        "views/plaft_control_category_views.xml",
        "views/plaft_control_list_views.xml",
        "views/plaft_document_category_views.xml",
        "views/plaft_country_views.xml",
        "views/plaft_country_state_views.xml",
        "views/plaft_res_city_views.xml",
        "views/plaft_res_city_district_views.xml",
        "views/plaft_currency_views.xml",
        "views/plaft_ro_declaration_views.xml",
        "views/plaft_control_threshold_views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "sequence": 3,
}
