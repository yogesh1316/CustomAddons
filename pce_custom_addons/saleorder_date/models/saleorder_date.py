# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

class saleorder_date(models.Model):
    _inherit = 'sale.order'

    # create_by | create_date | update_by | update_date
    # Ganesh      19/09/2018                
    # Info : Compute the commitment date on Factory calendor

    @api.depends('date_order', 'order_line.customer_lead')
    def _compute_commitment_date(self):
        
        factory_calendor_obj =  self.env['factory.calendor']
        for order in self:
            dates_list = []
            order_datetime = fields.Datetime.from_string(order.date_order)
            for line in order.order_line.filtered(lambda x: x.state != 'cancel'):
                if line.customer_lead:
                    custlead_day = line.customer_lead
                else:
                    custlead_day = line.order_id.company_id.security_lead
                print('custlead_day',custlead_day)
                dt = order_datetime + timedelta(days=line.customer_lead or 0.0)
                dates_list.append(dt)
            if dates_list:
                commit_date = min(dates_list) if order.picking_policy == 'direct' else max(dates_list)
                commitment_date = fields.Datetime.to_string(commit_date)
                print('order_datetime',order_datetime)
                datelist = factory_calendor_obj.search([('ydate','=',order_datetime)])
                if datelist.seq_no>0:
                    print('seq_no,custlead_day',datelist.seq_no,custlead_day)
                    seq_no = datelist.seq_no+custlead_day
                    commitdate_data = factory_calendor_obj.search([('seq_no','=',seq_no)])
                    print('commitdate_data',commitdate_data)
                    order.commitment_date = commitdate_data.ydate
                else:
                    raise UserError(_('Order date %s is declare as holiday/week day ') %(order_datetime,))

