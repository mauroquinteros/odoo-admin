# -*- coding: utf-8 -*-
{
    'name': "Configuración en Base",

    'summary': """Adaptar módulos base para compañía""",

    'description': """
        Long description of module's purpose
    """,

    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    "category": "Base",
    'version': '13.1.3.1',
    "development_status": "Beta",
    "maintainers": ["Carlos Enrique", "Mauro Quinteros"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>', 'Mauro Quinteros <quinterosmauro0599@gmail.com>'],
    "license": "AGPL-3",
    'qweb': [],
    'demo': [],
    'test': [],
    'images': [],

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'account', 'l10n_pe_sunat', 'l10n_latam_base', 'l10n_pe'],

    # always loaded
    'data': [
        'data/res.partner.bank.profile.csv',
        'data/res_partner_title_data.xml',
        'data/res.partner.category.csv',
        'data/res_bank_data.xml',
        'data/res_country_reference_data.xml',
        'data/res_partner_bank_data.xml',
        'data/res_partner_enterprise_data.xml',

        'doc/papper_format_latin.xml',

        'views/xpath/xpath_res_company_views.xml',

        'views/configuration.xml',
        "views/wizard/partner_convert_client.xml",
        "views/res_partner_beneficiary_views.xml"
    ],
    "application": False,
    'installable': True,
    "auto_install": False,
    "sequence": 1,
}
