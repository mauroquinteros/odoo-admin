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

# def _load_hr_contract_condition_data(cr, registry):
#     csv_path = join(dirname(realpath(__file__)), 'data', 'hr.contract.condition.csv')
#     csv_file = open(csv_path, 'rb')
#     # Reading the header
#     csv_file.readline() 
#     cr.copy_expert(
#         """COPY hr_contract_condition (name,active) FROM STDIN WITH DELIMITER ','""", csv_file)
#     # Creating xml_ids
#     cr.execute(
#         """INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
#            SELECT concat('hr_contract_condition_', sequence), id, 'data_migration', 'hr.contract.condition', 't'
#            FROM hr_contract_condition""")

# def data_migration_init(cr, registry):
#     _load_hr_contract_condition_data(cr, registry)

# def data_migration_unistall(cr, registry):
#     cr.execute("DELETE FROM hr_contract_condition;")
#     cr.execute("DELETE FROM ir_model_data WHERE model='hr.contract.condition';")