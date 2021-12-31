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
    'name': "Módulo Catalogos SUNAT",
    'summary': 'Datos de Tablas para creación de factura y complementarias.',
    'description' : """
Datos Catalogos SUNAT.
====================================

Tablas:
--------------------------------------------
    * Tablas requeridas para los Documentos electronicos Peru

    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    'category': 'Accounting & Finance',
    'version': '13.5.1.0.1',
    'license': 'AGPL-3',
    "maintainers": ["Carlos Enrique"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>'],
    'qweb' : [],
    'demo': [],
    'test': [],
    'images': [],
    'depends' : [
        'base',
        'account',
        'account_debit_note',
        'l10n_pe',
        'l10n_latam_base',
        'l10n_latam_invoice_document'],
    'data': [
        'security/security_category.xml',
        'security/security_data.xml',
        'security/ir.model.access.csv',

        'data/l10n_latam_identification_type_data.xml',
        'data/l10n_latam.document.type.csv',
        'data/l10n_pe_sunat_data.xml',
        'data/l10n_pe_sunat.anexo.01.csv',
        'data/l10n_pe_sunat.anexo.02.csv',
        'data/l10n_pe_sunat.anexo.03.csv',
        'data/l10n_pe_sunat.anexo.04.csv',
        'data/l10n_pe_sunat.anexo.05.csv',
        'data/l10n_pe_sunat.anexo.06.csv',
        'data/l10n_pe_sunat.anexo.07.csv',
        'data/l10n_pe_sunat.anexo.08.csv',
        'data/l10n_pe_sunat.anexo.09.csv',
        'data/l10n_pe_sunat.anexo.10.csv',
        'data/l10n_pe_sunat.anexo.11.csv',

        'views/catalog_views.xml',
        'views/anexo_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    "sequence": 2,
    "post_init_hook": "l10n_pe_sunat_catalog_init",
    'uninstall_hook': 'l10n_pe_sunat_catalog_unistall',
}
