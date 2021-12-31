# -*- coding: utf-8 -*-
{
    "name": "Núcleo JetCompany",
    "summary": """Concepto Nuevo de Pilar Base para Módulos complementarios en el núcleo de negocio""",
    "description": """
    Modulo Base Núcleo Empresarial.
    ====================================

    Tablas:
    --------------------------------------------
        * Profile_Operator
        * Profile_AccountBank
        * Customer Partner
        * Correspondent Partner
        * Agency Partner

    Information:
    --------------------------------------------
        * Company Details Update
        * Sample Server Mail Gmail
    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    "category": "BusinessCore",
    "version": "13.5.2.6",
    "development_status": "Beta",
    "maintainers": ["Carlos Enrique", "Mauro Quinteros"],
    "contributors": [
        "Carlos Enrique Paico <EnriqueZav96@gmail.com>",
        "Mauro Quinteros <quinterosmauro0599@gmail.com>",
    ],
    "license": "AGPL-3",
    "qweb": [],
    "demo": [],
    "test": [],
    "images": [],
    "depends": [
        "web_responsive",
        "web_notify",
        "l10n_pe_sunat",
        "base_config",
        "legal_plaft",
        "point_of_sale",
        "account_check_printing",
        "sale",
        "sale_management",
    ],
    "data": [
        "security/security_category.xml",
        "security/security_data.xml",
        "security/ir.model.access.csv",
        "data/correlatives_data.xml",
        "data/profile.config.csv",
        "data/business_data.xml",
        "data/plaft_data.xml",
        "data/res_partner_enterprise_data.xml",
        "data/res_partner_correspondent_data.xml",
        "data/res_partner_agency_data.xml",
        # "data/pos_config_data.xml",
        # "data/pos_config_correlative_data.xml",
        "views/configuration.xml",
        "views/business_views.xml",
        "views/res_partner_management_views.xml",
        "views/res_partner_correspondent_views.xml",
        "views/res_partner_agency_views.xml",
        "views/xpath/xpath_pos_config_views.xml",
        "views/pos_config_correlative_views.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
    "sequence": 4,
}
