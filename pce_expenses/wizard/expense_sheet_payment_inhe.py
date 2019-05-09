from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from werkzeug import url_encode

class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):

    _inherit = "hr.expense.sheet.register.payment.wizard"



    @api.model
    def assign_memo(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
        return expense_sheet.exp_iou_no
        # self.communication=expense_sheet.expense_line_ids.iou_no

    @api.model
    def assign_pay_mode(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
        # pay=self.env['account.journal'].search([('id','=',expense_sheet.pay_mode.id)])
        return expense_sheet.pay_mode

    communication = fields.Char(string='Memo',default=assign_memo)
    journal_id = fields.Many2one('account.journal', string='Payment Method',default=assign_pay_mode, required=True)