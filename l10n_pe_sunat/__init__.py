# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2020
#    Author      :  Carlos Enrique
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################
import logging
from os.path import join, dirname, realpath
from odoo import tools

from . import controllers
from . import models

def _load_catalog_03_data(cr, registry):
    csv_path = join(dirname(realpath(__file__)), 'data', 'l10n_pe_sunat.catalog.03.csv')
    csv_file = open(csv_path, 'rb')
    # Reading the header
    csv_file.readline() 
    cr.copy_expert(
        """COPY l10n_pe_sunat_catalog_03 (code, name, active) FROM STDIN WITH DELIMITER '|'""", csv_file)
    # Creating xml_ids
    cr.execute(
        """INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
           SELECT concat('l10n_pe_sunat_cat03_', code), id, 'l10n_pe_sunat', 'l10n_pe_sunat.catalog.03', 't'
           FROM l10n_pe_sunat_catalog_03""")

def _load_catalog_25_data(cr, registry):
    csv_path = join(dirname(realpath(__file__)), 'data', 'l10n_pe_sunat.catalog.25.csv')
    csv_file = open(csv_path, 'rb')
    # Reading the header
    csv_file.readline() 
    cr.copy_expert(
        """COPY l10n_pe_sunat_catalog_25 (code, name, active) FROM STDIN WITH DELIMITER '|'""", csv_file)
    # Creating xml_ids
    cr.execute(
        """INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
           SELECT concat('l10n_pe_sunat_cat25_', code), id, 'l10n_pe_sunat', 'l10n_pe_sunat.catalog.25', 't'
           FROM l10n_pe_sunat_catalog_25""")

def l10n_pe_sunat_catalog_init(cr, registry):
    _load_catalog_03_data(cr, registry)
    _load_catalog_25_data(cr, registry)

def l10n_pe_sunat_catalog_unistall(cr, registry):
    cr.execute("DELETE FROM l10n_pe_sunat_catalog_03;")
    cr.execute("DELETE FROM ir_model_data WHERE model='l10n_pe_sunat.catalog.03';")
    cr.execute("DELETE FROM l10n_pe_sunat_catalog_25;")
    cr.execute("DELETE FROM ir_model_data WHERE model='l10n_pe_sunat.catalog.25';")