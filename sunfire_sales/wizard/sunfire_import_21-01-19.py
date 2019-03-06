import base64
import xlrd
from odoo import api, fields, models, SUPERUSER_ID, _
import codecs
import io
import base64
import datetime as dt
import io
import itertools
import logging
import psycopg2
import operator
import os
import re
from odoo.tools.translate import _
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.misc import ustr
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import datetime


class magna_import(models.TransientModel):
    _name='magna.import'
    
    my_xlsx_file=fields.Binary("Import File")
   
    def _import_compute_margin(self,record):
       
        if record[7] == "Percentage":
            list_price = (record[6] + (record[6]* (record[8]/100)))
            #record.append(list_price)
        else:
            list_price=record[6]+record[8]
            #record.append(list_price)
        #print(record)
        return list_price


     
   
    @api.multi
    def import_csv(self):
        active_ids=self.env.context['active_ids']
        sale_order_obj = self.env['sale.order']
        product_product_obj = self.env['product.template']
        product_pr_obj = self.env['product.product']
        product_category_obj = self.env['product.category']
        layout_category_obj=self.env['sale.layout_category']
        line_of_business_obj=self.env['line_of_business.info']
        deal_type_obj=self.env['deal_type.info']
       
        if active_ids:
            sale_order_rec = sale_order_obj.search([('id','=',active_ids[0])])
            sale_order_rec.order_line = [(5,0,0)]
            
        if self.my_xlsx_file:    
            ax=codecs.decode(self.my_xlsx_file)
            ax1=base64.b64decode(ax)
            book = xlrd.open_workbook(file_contents=ax1 )
            first_sheet=book.sheet_by_index(0)
            ro=first_sheet.nrows
            co=first_sheet.ncols
            data=[]
            for i in range(1,ro):
                maja=[]
                for j in range(0,co):
                    cell=first_sheet.cell(i,j)
                    maja.append(cell.value)
                data.append(maja)

        
            for record in data:
                if record[2]!="": 
                    # prodcut_type =  record[0]#12-07-2018 Type removed from excel import
                    product_heading =  record[0]
                    # dr_data =  xlrd.xldate_as_tuple(record[4],book.datemode)
                    # print(dr_data)
                    # dr_date = record[4] #datetime.datetime(dr_data[0],dr_data[1],dr_data[2])
                    # print(dr_date)
                    #part_num=part_number= product_name
                    part_num =  record[1]
                    product_amount =  magna_import._import_compute_margin(self,record)
                    hsn_no =  record[3]
                    name=record[2]
                    product_category =  record[4]
                    # model_group_code = record[10]
                    quantity =  record[5]
                    stp =  record[6] 
                    margin_type =record[7]
                    margin_value =record[8]
                    line_of_business=record[9]
                    up_sell=record[10]
                    deal_type=record[11]
                    
                    if hsn_no:
                        hsn_no=str(hsn_no).split('.')[0]
                    #Default values for Deal Type
                    deal_type_vals={
                        'deal_type':deal_type
                    }
                    #Search for Deal Type
                    deal_type_ids=deal_type_obj.search([('deal_type','=',deal_type)])
                    if deal_type_ids:
                        deal_type_id=deal_type_ids.id
                    else:
                        deal_type_id=deal_type_ids.create(deal_type_vals)

                    #Default values for LOB(Line of Business)
                    lob_vals={
                        'line_of_business':line_of_business
                    }
                    #search for LOB
                    line_of_business_ids=line_of_business_obj.search([('line_of_business','=',line_of_business)])
                    if line_of_business_ids:
                        line_of_business_id=line_of_business_ids.id
                    else:
                        line_of_business_id=line_of_business_obj.create(lob_vals)
                    
                    #Default values for product_heading(Product Heading)
                    layout_vals={
                        'name':product_heading,
                        'sequence':10,
                    }
                    #Search for Layout Caategory i.e product_heading(Product Heading)
                    layout_category_ids=layout_category_obj.search([('name','=',product_heading)])
                    if layout_category_ids:
                        layout_category_id=layout_category_ids.id
                    else:
                        layout_category_id=layout_category_obj.create(layout_vals)

                    # Search for category
                    product_category_ids =  product_category_obj.search([('complete_name','=',product_category)])
                    if product_category_ids:
                        product_category_id = product_category_ids.id
                    
                    
                    
                    # First create product and then mapping to sale order line
                    # product_vals = {
                    #                 'default_code' : part_num,
                    #                 'type' : prodcut_type,
                    #                 'categ_id' : product_category_id,
                    #                 'list_price' : product_amount,
                    #                 'l10n_in_hsn_code' : hsn_no,
                    #                 #'barcode' : part_number,
                    #                 # 'model_group_code' : model_group_code,
                    #                 'name':name,
                    #                 'standard_price' : stp,
                    #                 'uom_id' : 1
                    #                 }
                    
                    product_vals = {
                                'name' : part_num,
                                'categ_id' : product_category_id,
                                'list_price' : product_amount,
                                'l10n_in_hsn_code' : hsn_no,
                                'description_sale':name,
                                'standard_price' : stp,
                                'uom_id' : 1
                                }
                    product_id = product_product_obj.create(product_vals)       

                    sale_order_line_vals = {
                                            'order_id':sale_order_rec.id,
                                            'product_id' : product_id.id,
                                            'categ_id' : product_id.categ_id,
                                            'l10n_in_hsn_code' : product_id.l10n_in_hsn_code,
                                            'name' : product_id.name,
                                            'product_uom_qty' : quantity,
                                            'product_uom' : 1,
                                            'price_unit' : product_id.list_price,
                                            'purchase_price' : product_id.standard_price,
                                            'margin_value' :margin_value,
                                            'margin_type' : margin_type,
                                            'layout_category_id':layout_category_id,
                                            'line_of_business':line_of_business_id,
                                            'up_sell':up_sell,
                                            }
                    if sale_order_rec:
                        sale_order_rec.order_line= [(0,0,sale_order_line_vals)]  


              

    
       
       
       
       
       
