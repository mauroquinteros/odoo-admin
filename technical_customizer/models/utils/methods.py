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

def dynamic_notify(self,comment,mode):
    if mode == 'success':
        return self.env.user.notify_success(message=comment)
    if mode == 'warning':
        return self.env.user.notify_warning(message=comment)
    if mode == 'danger':
        return self.env.user.notify_danger(message=comment)
    if mode == 'info':
        return self.env.user.notify_info(message=comment)