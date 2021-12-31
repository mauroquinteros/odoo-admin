# -*- coding: utf-8 -*-

{
    "name": "Migración de Data",
    "summary": """Módulo para albergar data y esquemas de tablas para procesos de migración de data.""",
    'description' : """
Datos Migratorios.
====================================

Tablas:
--------------------------------------------
    * Tablas Agencias
    * Tablas Empleados

    """,
    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    'category': 'Technical Settings',
    'version': '13.4.2.17.9',
    'license': 'AGPL-3',
    "maintainers": ["Carlos Enrique"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>'],
    'qweb' : [],
    'demo': [],
    'test': [],
    'images': [],
    'depends' : ['hr','hr_contract'],
    'data': [
        'security/ir.model.access.csv',

        'data/sequences.xml',
        'data/hr.department.csv',
        'data/hr.job.csv',
        'data/hr.contract.condition.labor.csv',
        'data/ir.glossary.csv',
        'data/ir.glossary.homologant.csv',
        'data/ir_cron_data.xml',

        'views/lote_user_raw_view.xml',
        'views/agent_agency_external_raw_view.xml',
        'views/ir_glossary_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    "sequence": 13,
}
