# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2020
#    Author      :  JetPERU
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

modelist = [
    ("hr.employee", "Empleados"),
    ("res.currency", "Monedas"),
    ("res.country", "País"),
    ("res.country.state", "Estado"),
    ("res.city", "Ciudad"),
    ("l10n_pe.res.city.district", "Distrito"),
    ("l10n_latam.identification.type", "Identificación"),
    ("res.partner", "Partner")
]

models = ['hr.employee','res.partner']

channel_type = [('sale', 'Venta'), ('pay', 'Pago')]

account_bank_type = [("normal", "Normal"),("interbanc", "Interbancaria")]

state_remittance = [('pending', 'Pendiente a Pagar'), ('reserved', 'Remesa Reservada'), ('cusreg', 'Cliente Registrado')]