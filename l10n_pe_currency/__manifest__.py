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
    'name' : 'Tipo de cambio Peru',
    'version' : '2.1.0',
    "author": "JetPERU S.A., Carlos Enrique Paico",
    'category' : 'Generic Modules/Base',
    'summary': 'Permite ingresar tipo de cambio en formato peruano, Money Exchange y Web Services',
    'license': 'AGPL-3',
    "maintainers": ["Carlos Enrique"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>'],
    'description' : """
        Registro de tpo de cambio
        -----------------------

        Registra el tipo de cambio al estilo peruano:

        ANTES:
        S/. 1 = S/. 1
        $ 1 = S/. 0.30769

        AHORA
        S/. 1 = S/. 1
        $ 1 = S/. 3.25
    """,
    'website': 'http://www.jetperu.com.pe',
    'depends' : ['account', 'l10n_pe', 'sale_management', 'base_company', 'account_treasury'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',

        'views/res_currency_view.xml',
        'views/wizard/api_query_exchange_rate.xml',
        'views/wizard/copy_tc_oer.xml',
        'views/res_currency_moex_auto_approvement_views.xml',
        'views/res_currency_moex_calculation.xml',
        'views/res_currency_rate_oer_views.xml',
        'views/res_currency_bottons.xml',

        'data/ir_cron_process.xml',
        'data/ir.config_parameter.csv',
        'data/res_currency_data.xml',
        'data/res_currency_moex_calculation_data.xml',
        'data/res_currency_rate_oer_data.xml',
        'data/res_currency_moex_approvement.xml',
    ],
    'qweb' : [
        'static/src/xml/top_button.xml',
    ],
    'demo': [
        #'demo/account_demo.xml',
    ],
    'test': [
        #'test/account_test_users.yml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
    "sequence": 7,
}