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

#create_by | create_date | update_by | update_date
#Ajinkya     25/03/2019     Ajinkya     27/03/2019   
#Info.: Purchase Report

class purchaseorderreport(models.Model):
    _inherit = "purchase.order"
    
    @api.multi
    def set_amt(self,amt):
        locale.setlocale(locale.LC_ALL, '')
        return locale.format("%.2f", amt, grouping=True)
    @api.multi
    def get_desc(self):
        for order in self:
            if order.order_line:
                li=[]
                for line in order.order_line:
                    #print(line.name)
                    li.append(line.product_id.name)

                return set(li)

                
    @api.multi
    def get_loged_user_name(self):
        for order in self:
            user=self.env['res.users'].search([('id','=',order.env.uid)])
        return user.partner_id.name
    @api.multi
    def set_amt_in_text(self,amount):
#         print('****amount**',amount)
        for curr_id in self:
#             if curr_id.currency_id:
            #print("===================Currency_id",curr_id.currency_id.name,"=======", curr_id.currency_id.currency_subunit_label,"symbol", curr_id.currency_id.symbol,"Main unit",curr_id.currency_id.currency_unit_label,"total amount",curr_id.amount_total) #,"=====",curr_id.currency_subunit_label)
            split_num=str(amount).split('.')
            int_part=int(split_num[0])
            decimal_part=int(split_num[1])
    #         print('*****int',int_part)
    #         print('*****decimal',decimal_part)
    #         print('****amount**',amount)
            fld=0.00
            amt=0
            flagdecima=0.00
            amt,fld=divmod(amount,1)
            flagdecima= fld*100
    #         print("***********************************{:.0f}".format(flagdecima))
            temp="{:.0f}".format(flagdecima)
            a=int(temp)
    #         print("****************a***********",a)
            amountinwordf=num2words(amt,lang='en_IN').replace(',', ' ').title()
#             print("========================================",amountinwordf)
            amountinwords=num2words(a,lang='en_IN').replace(',', ' ').title()
#             print("========================================",amountinwords)
            #print('****amount**',amount)
            # print('******fld********', fld)   
            # print('*****************', round(amt,0))   
            # print('********flagdecima*********',flagdecima) 
            # print('*****************',amountinwordf)   
            # print('*****************',amountinwords) 
            finalamount=curr_id.currency_id.name+"\t"+amountinwordf+' and '+ amountinwords + "\t"+curr_id.currency_id.currency_subunit_label +"\t"+"Only"
            return finalamount
        
class purchase_order_line(models.Model):
    _inherit="purchase.order.line"
    #price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', store=True,digits=dp.get_precision('Price Subtotal'))
    
    @api.multi
    def caculate_igst(self):
          pairs=[]
          igst_val={}
          for tax in self:
             for i in tax.taxes_id:
                #print("@@@@i.amount",i.amount,"====",i.name,"group_id_name",i.tax_group_id.name) 
                if i.tax_group_id.name=='IGST':
                    #print(i.name)
                    sum_tax=((i.amount)*tax.price_subtotal)/100
                    igst_val['sum_tax']=sum_tax
                    igst_val['desc']=i.description
                    pairs.append((i.description,sum_tax))
                #print("======================================",pairs)
          sums = {}
          for pair in pairs:
            sums.setdefault(pair[0], 0)
            sums[pair[0]] += pair[1]
          return sums.items()
        
    @api.multi
    def calculate_cgst_sgst(self): 
        sgst={}
        pairs=[]
         
        for tax in self:
            for i in tax.taxes_id.children_tax_ids:
                #print("=========================",i)
                sum_tx=((i.amount)*tax.price_subtotal)/100
                sgst['sum_tx']=sum_tx
                sgst['description']=i.description
                pairs.append((i.description,sum_tx))
        #print("pairs========",pairs)
        sums = OrderedDict()
        for pair in pairs:
             # print("=========pair============",pair)
              sums.setdefault(pair[0], 0)
              sums[pair[0]] += pair[1]
       # print("========sums",sums)
        return sums.items()
         
    @api.multi
    def sgst_calculate(self):
        for tax in self:
            for children_id in tax.taxes_id.children_tax_ids:
                if children_id.tax_group_id.name=="SGST":   
#                     print("children_id==Amt.SGST Rate====",children_id.amount,"==",children_id.tax_group_id.name,
#                           "====Price subtotal==",tax.price_subtotal)
                    line_cgst_tax=((children_id.amount)*(tax.price_subtotal))/100
                    print("====line_cgst_tax",line_cgst_tax)
                    return line_cgst_tax
          
    # @api.multi
    # def material_desc(self):
    #     for items in 
 
        
                    
        
        
        
    
    