# -*- coding: utf-8 -*-
# create_by | create_date | update_by | update_date
#     Ajinkya      29/01/2019     Ajinkya     02/02/2019   
#     Info.: Sale Order Report--><!-- Including Custom Css File
from odoo import models, fields, api
from num2words import num2words
import locale
from collections import OrderedDict 


class sale_report(models.Model):
    _inherit='sale.order'
    
    @api.multi
    def set_amt(self,amt):
        locale.setlocale(locale.LC_ALL, '')
        return locale.format("%.2f", amt, grouping=True)

    @api.multi # calculate amount in words
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

class sale_order_line(models.Model):
    _inherit="sale.order.line"
    
    @api.multi # calculate the sgst and cgst
    def calculate_cgst_sgst(self): 
        sgst={}
        pairs=[]
         
        for tax in self:
            for i in tax.tax_id.children_tax_ids:
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
    
    @api.multi # calculate the igst 
    def caculate_igst(self):
          pairs=[]
          igst_val={}
          for tax in self:
             for i in tax.tax_id:
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

    
    @api.multi # calculate the sgst
    def sgst_calculate(self):
        for tax in self:
            for children_id in tax.tax_id.children_tax_ids:
                if children_id.tax_group_id.name=="SGST":   
#                     print("children_id==Amt.SGST Rate====",children_id.amount,"==",children_id.tax_group_id.name,
#                           "====Price subtotal==",tax.price_subtotal)
                    line_cgst_tax=((children_id.amount)*(tax.price_subtotal))/100
                    print("====line_cgst_tax",line_cgst_tax)
                    return line_cgst_tax