from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo.addons.account_treasury.models.utils import values as valtre
from odoo.addons.account_treasury.models.utils import methods as treasury_methods

class RequirementsPCL(models.Model):
    _name = "requirement.pcl"
    _description = "Requerimientos de Políticas de Cumplimiento Legal de Ordenes de Ventas"
    _rec_name = "sale_order_id"
    _inherit = ["mail.thread","mail.activity.mixin"]

    sale_order_id = fields.Many2one(string='Operacion Venta',comodel_name='sale.order',required=True)
    cat_document_id = fields.Many2one(string='Categoría',comodel_name='plaft.document.category')
    document_id = fields.Many2one(string='Documento',comodel_name='l10n_latam.identification.type')
    image = fields.Binary("Adjuntar Imagen", attachment=True, track_visibility='always')
    attachment_ids = fields.Many2many('ir.attachment', string='Adjuntar Archivo')

    state = fields.Selection(string="Estado de los Items", default="unchecked", selection=[("checked", "Revisado"),("unchecked", "No Revisado")])

    def do_mark_line(self):
        pass
        # import pdb; pdb.set_trace()
        # if self._context.get('type_render', False) is False:
        #     if self.pay_order_id.business_line_id.foreign_code == 'bsln001':
        #         view_name = 'op_assistant.cashbox_exhange_money_view_form'
        #     elif self.pay_order_id.business_line_id.foreign_code == 'bsln005':
        #         view_name = 'op_assistant.wizard_pay_remittance_view_form'
        #     elif self.pay_order_id.business_line_id.foreign_code == 'bsln006':
        #         view_name = 'op_assistant.cashbox_send_remittance_view_form'
        #     else:
        #         raise ValidationError('No hay vista configurada.')

        #     order = self._context.get('active_id')
        #     model = self._context.get('active_model')
        #     wizard = self.env[model].browse(order)

        #     self.write({"state": self._context.get("option")})
        #     return {
        #         "name": wizard._description,
        #         "context": self.env.context,
        #         "view_mode": "form",
        #         "res_model": wizard._name,
        #         "res_id": wizard.id,
        #         "view_id": self.env.ref(view_name).id,
        #         "type": "ir.actions.act_window",
        #         "target": "new",
        #     }
        # else:
        #     self.write({"state": self._context.get("option")})

    # @api.onchange('document_id','attachment_ids')
    # def _onchange_field_name(self):
    #     for rec in self:
    #         if len(rec.document_id) == 0 and len(rec.attachment_ids) == 0:
    #           rec.env.user.notify_warning(message='Requisito para ser llenado después: "%s".' % (str(rec.document_id.name or "")))
    #         elif len(rec.document_id) > 0 and len(rec.attachment_ids) > 0:
    #           rec.env.user.notify_info(message='Requisito "%s" ha sido completado, puede marcar (✔) en el registro.' % (str(rec.document_id.name or "")))
