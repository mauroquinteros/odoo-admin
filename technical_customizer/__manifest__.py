# -*- coding: utf-8 -*-

{
    "name": "Mantenimiento Técnico",
    "summary": """Módulo para Configurar temas técnicos de origen complejos.""",
    'description' : """""",
    "author": "JetPERU S.A., Carlos Enrique Paico",
    "website": "http://www.jetperu.com.pe",
    'category': 'Technical Settings',
    'version': '13.1.0',
    'license': 'AGPL-3',
    "maintainers": ["Carlos Enrique"],
    'contributors': ['Carlos Enrique Paico <EnriqueZav96@gmail.com>'],
    'qweb' : ['static/src/xml/user_template.xml'],
    'demo': [],
    'test': [],
    'images': [],
    'depends' : ['sale', 'sale_management', 'point_of_sale', 'website', 'base_company', 'data_migration'],
    'data': [
        'security/security_category.xml',
        'security/security_data.xml',
        'security/ir.model.access.csv',

        'data/enrique_gmail_server.xml',
        'data/res_currency_update_data.xml',
        'data/res_company_update_data.xml',
        'data/website_update_data.xml',

        'views/form_send_email_config.xml',
        'views/res_models_xpath_views.xml',
        'views/user_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    "sequence": 14,
}
