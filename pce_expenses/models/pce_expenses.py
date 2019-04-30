# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class HrExpense(models.Model):
    _inherit ="hr.expense"

    product_id = fields.Many2one('product.product', string='Product', readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, required=True)
    iou_no= fields.Char(string="IOU NO")
    exp_type_id=fields.Many2one('expense.type.master',string="Expense Type",domain=[('active','=',True)],required=True)
    cust_id=fields.Many2one('res.partner',string="Customer")
    tour_date=fields.Date(string="Tour Date")
    mode_of_payment=fields.Selection([('by_cheque','By_cheque'),('by_cash','By Cash'),('by_NEFT','By NEFT'),('by_RTGS','By RTGS')],string="Mode Of Payment")

    @api.model
    def create(self,vals):
        date=datetime.datetime.now()
        a=(date.strftime('%y'))
        b=int(a)+1
        p=' '
        c='-'
        p=str(a)+c+str(b)
        vals['iou_no']=self.env['ir.sequence'].next_by_code('hr.expense').replace('x',p)
        res = super(HrExpense, self).create(vals)
        return res


    @api.onchange('sale_order_id')
    def assign_sale_customer(self):
        if self.sale_order_id:
            self.cust_id=self.sale_order_id.partner_id

    @api.multi
    @api.onchange('cust_id')
    def display_cust_related_sale(self):
        if self.cust_id:
            sales=[]
            domain={}
            sale_obj=self.env['sale.order'] #creating sale order object
            sales_ids=sale_obj.search([('partner_id','=',self.cust_id.id)])
            for i in sales_ids:
                sales.append(i.id)
            domain['sale_order_id']=[('id','in',sales)]
            return {'domain':domain}

    @api.multi
    def submit_expenses(self):
        if any(expense.state != 'draft' for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report!"))
        if self.mode_of_payment=='by_cheque' or self.mode_of_payment=='by_NEFT' or self.mode_of_payment=='by_RTGS':
            mode=self.env['account.journal'].search([('name','=','Bank')])
        if self.mode_of_payment=='by_cash':
            mode=self.env['account.journal'].search([('name','=','Cash')])

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'context': {
                'default_expense_line_ids': [line.id for line in self],
                'default_employee_id': self[0].employee_id.id,
                'default_name': self[0].name if len(self.ids) == 1 else '',
                'default_exp_iou_no': self[0].iou_no,
                'default_pay_mode':mode.id,
            }
        }

class HrExpenseSheet(models.Model):
    _inherit ="hr.expense.sheet"

    approve_date=fields.Date(string="Approve Date")
    close_date=fields.Date(string="Closing Date")
    exp_iou_no=fields.Char(string="Exp_Iou_No")
    pay_mode = fields.Many2one('account.journal', string='Pay_mode')


    



class pce_expenses_type(models.Model):
    _name="expense.type.master"
    _rec_name='text'

    seq_no=fields.Integer(string="Seq No")
    text=fields.Char(string='Text')
    active=fields.Boolean(default=True,track_visibility='onchange',help="Active / Deactivate")


    @api.onchange('text')
    def generate_seq_no(self):
        expense_obj=self.env['expense.type.master']
        data=expense_obj.search_count([])
        print(data,".....")
        if data:
            self.seq_no=data+1
        else:
            self.seq_no=1


        