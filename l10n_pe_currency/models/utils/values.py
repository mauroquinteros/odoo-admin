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

import operator

principals = ["USD", "PEN", "EUR"]
principal_currencies = ["USD", "EUR"]
domain = [("name", "in", principals)]

type_operation = [("com", "Compra"), ("ven", "Venta")]
type_operator = [("*", "Multiplicar"), ("/", "Division")]

ops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,  # use operator.div for Python 2
    "%": operator.mod,
    "^": operator.xor,
}
