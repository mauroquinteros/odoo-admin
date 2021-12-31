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
    
import string, random

def assemble_names(values):
    values["name"] = (values["name"]).title()
    array = values["name"].split(' ')

    if len(array) >= 3:
        lastname = array[0]
        mlastname = array[1]
        names = array[2] + " " + array[3] if len(array) is 4 else array[2]

        values["firstname"] = names
        values["flstname"] = lastname
        values["mlstname"] = mlastname

    elif len(array) == 2:
        lastname = array[0]
        mlastname = random.choice(string.ascii_lowercase)
        names = array[1] if len(array) is 2 else random.choice(string.ascii_lowercase)

        values["firstname"] = names
        values["flstname"] = lastname
        values["mlstname"] = mlastname

    elif len(array) <= 1:
        lastname = array[0]
        mlastname = random.choice(string.ascii_lowercase)
        names = random.choice(string.ascii_lowercase)

        values["firstname"] = names
        values["flstname"] = lastname
        values["mlstname"] = mlastname

def assemble_mail(values):
    firstname = values["firstname"][:1] if values["firstname"] is not False else ''
    flstname = values["flstname"] if values["flstname"] is not False else ''
    mlstname = values["mlstname"][:1] if values["mlstname"] is not False else ''

    if values["login"] is False or len(values["login"]) < 1:
        assemble_mail = firstname + flstname + mlstname
        values["login"] = assemble_mail.lower()