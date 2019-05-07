from odoo import api, fields, models, tools,SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from num2words import num2words
from itertools import groupby
import itertools
from collections import OrderedDict 
from babel.numbers import format_decimal
#from babel.numbers import format_currency

from odoo.addons import decimal_precision as dp
import locale
import datetime

#create_by  | create_date | update_by | update_date
#Pradip      27/12/2018   12:00PM  Pradip       
#Info.: TAX Report

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    transmode = fields.Selection([('1','Road'),('2','Rail'),('3','Air'),('4','Ship')])
    transdistance = fields.Char(string='Distance (km)')
    transportername = fields.Many2one('transport_mode.master',string='Transporter Name')
    transporterid = fields.Char(string='Transporter ID')
    transdocno = fields.Char(string='Document No.')   
    vehicleno = fields.Char(string='Vehicle No.')
    vehicletype = fields.Selection([('R','Regular'),('O','ODC')])
    transdocdate = fields.Date(string='Transaction doc. date',help="Transaction date should be greater then invoice date", copy=False)
    number = fields.Char(store=True, readonly=True, copy=False)
    no_of_package=fields.Integer(compute='assign_no_of_package',store=True)   
    sequence_id=fields.Char()
    invoice_type=fields.Selection([('Original For Receipient','Original For Receipient'),('Duplicate For Transporter','Duplicate For Transporter'),('Triplicate For Assessee','Triplicate For Assessee'),('Extra Copy','Extra Copy'),('All','All')])
   
    # po_date=fields.Date(compute='assign_po_date')
    # po_no=fields.Char(compute='assign_po_no')
        
    @api.multi
    def invoice_validate(self):
        date=datetime.datetime.now()
        a=(date.strftime('%y'))
        b=int(a)+1
        p=' '
        c='-'
        p=str(a)+c+str(b)
        self.number=self.env['ir.sequence'].next_by_code('invoice').replace('x',p)
        
        for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
            invoice.message_subscribe([invoice.partner_id.id])
        self._check_duplicate_supplier_reference()
        stock_pick_obj=self.env['stock.picking'].search([])
        for i in stock_pick_obj:
            s=str(i.origin)
            if self.origin in i.origin:
                if i.picking_type_id.name=='Delivery Orders':
                    self.env.cr.execute("update stock_picking set invoice_status='Y',invoice_no=%s,invoice_date=%s where id= %s",(self.number,self.date_invoice,i.id,))


     
        return self.write({'state': 'open'})


    @api.depends('origin')
    def assign_no_of_package(self):
        sale_order_line_obj=self.env['sale.order.line'].search([])
        sale_obj=self.env['sale.order'].search([('name','=',self.origin)])
        if sale_obj:
            for i in sale_order_line_obj:
                if sale_obj.id==i.order_id.id:
                    self.no_of_package=i.qty_delivered
        
    
    
     
    
    # @api.depends('origin',)
    # def assign_po_no(self):
    #     sale_obj=self.env['sale.order'].search([('name','=',self.origin)])
    #     if sale_obj:
    #         self.po_no=sale_obj.client_order_ref
    #     # purchase_obj=self.env['purchase.order'].search([('name','=',self.po_no)])
    #     # if purchase_obj:
    #     #     self.po_date=purchase_obj.date_order

    # @api.depends('po_no')
    # def assign_po_date(self):
    #     purchase_obj=self.env['purchase.order'].search([('name','=',self.po_no)])
    #     print(purchase_obj,";;;;;;;purchase_obj")
    #     if purchase_obj:
    #         print(purchase_obj.date_order,";;;;;;;po date_order")
    #         self.po_date=purchase_obj.date_order

    @api.multi
    def _address(self):
        for addres in self:
            print("==================INV ADD===============partner_id",addres.partner_id.id)
            print("==================Ship ADD===============partner_id",addres.partner_shipping_id.id)
#         res_partner_obj=self.env["res.partner"]
#         in_addr_id=res_partner_obj.search([('id','=',self.origin)])
#         print(" res_partner_obj=========", res_partner_obj)
        
    
    
    
    def get_num_igst(self,x):
        return str(x[4:8])
    def get_num(self,x):
        return str(x[10:14])
        # return float(''.join(ele for ele in x if ele.isdigit())) 
    def sum_cgst_calculate(self):
            for tax in self:
                sum=0
                for i in tax.invoice_line_ids:
                    for j in i.invoice_line_tax_ids.children_tax_ids:
                        #line_cgst_tax=((j.amount)*(i.price_subtotal))/100
                        #print("====================line_cgst_tax=================",line_cgst_tax)
                        if j.tax_group_id.name=="CGST":
                            pass
                            line_cgst_tax=round((((j.amount)*(i.price_subtotal))/100),2)
                            sum+=(line_cgst_tax)
                            #print("=======line_cgst_tax",round(line_cgst_tax,2))
                #print("CGST SUM:=====================================",sum)
                            
                return sum
    def sum_sgst_calculate(self):
            for tax in self:
                sum=0.00
                for i in tax.invoice_line_ids:
                    for j in i.invoice_line_tax_ids.children_tax_ids:
                        line_sgst_tax=round((((j.amount)*(i.price_subtotal))/100),2)
                        if j.tax_group_id.name=="SGST":
                            sum+=(line_sgst_tax)
                            
                return sum
    def sum_igst_calculate(self):
            for tax in self:
                sum=0
                for i in tax.invoice_line_ids:
                    line_igst_tax=round((((i.invoice_line_tax_ids.amount)*(i.price_subtotal))/100),2)
                    if i.invoice_line_tax_ids.tax_group_id.name=="IGST":
                        #print(i.price_subtotal,i.invoice_line_tax_ids.amount)
                        sum+=line_igst_tax
                return sum
            
    @api.multi
    def set_amt(self,amt):
        locale.setlocale(locale.LC_ALL, '')
        return locale.format("%.2f", amt, grouping=True)
             
           
    @api.multi
    def set_amt_in_text(self,amount):
        for curr_id in self:
            split_num=str(amount).split('.')
            int_part=int(split_num[0])
            decimal_part=int(split_num[1])
            fld=0.00
            amt=0
            flagdecima=0.00
            amt,fld=divmod(amount,1)
            flagdecima= fld*100
            temp="{:.0f}".format(flagdecima)
            a=int(temp)
            amountinwordf=num2words(amt,lang='en_IN').replace(',', ' ').title()
            amountinwords=num2words(a,lang='en_IN').replace(',', ' ').title()
            finalamount=curr_id.currency_id.name+"\t"+amountinwordf+' and '+ amountinwords + "\t"+curr_id.currency_id.currency_subunit_label +"\t"+"Only"
            return finalamount

    # @api.multi
    # def type_invoive(self):
    #     action = self.env.ref('Sample_Tax_Report.act_invoice_wizard_inhe').read()[0]
    #     print(action,"action")
    #     return action

         
class account_invoice_line(models.Model):
    _inherit="account.invoice.line"
    
    def price_subtotal_amount(self):
        product_hsn=[]
        for i in self:
            product_hsn.append(i.product_id.l10n_in_hsn_code)
            if i.product_id.l10n_in_hsn_code:
            #print("=====================",i.price_subtotal)
                print("===============product_hsn=====",product_hsn)
            
         
    @api.multi
    def cgst_calculate(self):
        default=0.00
        for tax in self:
            for children_id in tax.invoice_line_tax_ids.children_tax_ids:
                if children_id.tax_group_id.name=="CGST":   
                    line_cgst_tax=((children_id.amount)*(tax.price_subtotal))/100
                    c_tax=round(line_cgst_tax,2)
                    return "%.2f" % c_tax
    
    def sgst_calculate(self):
        default=0.00
        for tax in self:
            for children_id in tax.invoice_line_tax_ids.children_tax_ids:
                if children_id.tax_group_id.name=="SGST":   
                    line_sgst_tax=((children_id.amount)*(tax.price_subtotal))/100
                    s_tax=round(line_sgst_tax,2)
                    return "%.2f" % s_tax
                
    def igst_calculate(self):
        default=0.00
        for tax in self:
            for i in tax.invoice_line_tax_ids:
                if i.tax_group_id.name=="IGST":
                    line_igst_tax=((i.amount)*(tax.price_subtotal))/100
                    i_tax=round(line_igst_tax,2)
                    return "%.2f" % i_tax 
                
 
        
                    
        
        
        
    
    