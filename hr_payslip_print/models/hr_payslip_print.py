from odoo import api, fields, models
from num2words import num2words

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def set_amt_in_text(self,amount):
        for curr_id in self:
            fld=0.00
            amt=0
            flagdecima=0.00
            amt,fld=divmod(amount,1)
            flagdecima= fld*100
            temp="{:.0f}".format(flagdecima)
            a=int(temp)
            amountinwordf=num2words(amt,lang='en_IN').replace(',', ' ').title()
            amountinwords=num2words(a,lang='en_IN').replace(',', ' ').title()
            finalamount=curr_id.company_id.currency_id.name+"\t"+amountinwordf+' and '+ amountinwords + "\t"+curr_id.company_id.currency_id.currency_subunit_label +"\t"+"Only"
            return finalamount

