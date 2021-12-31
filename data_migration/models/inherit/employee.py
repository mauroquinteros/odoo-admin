
from odoo import models, fields, api, exceptions, _

class hr_employee_inherit(models.Model):
    _inherit = ['hr.employee']
    
    namecomplete = fields.Char(string="Nombre",store=False,readonly=True,compute="_get_complete_name")
    hr_firstname = fields.Char(string='Primer Nombre')
    hr_lastname = fields.Char(string='Apellido Paterno')
    hr_motherlastname = fields.Char(string='Apellido Materno')
    
    @api.depends("hr_firstname", "hr_lastname", "hr_motherlastname")
    def _get_complete_name(self):
        completename = ""
        if self.hr_lastname:
            completename += str(self.hr_lastname) + " "
        if self.hr_motherlastname:
            completename += str(self.hr_motherlastname) + " "
        if self.hr_firstname:
            completename += str(self.hr_firstname)

        self.namecomplete = str.strip(completename)
        
    @api.onchange("namecomplete")
    def _onchange_namecomplete(self):
        if str.strip(self.namecomplete) != None or "" or " ":
            self.name = self.namecomplete