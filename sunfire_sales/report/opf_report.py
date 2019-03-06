from odoo import tools
from odoo import api, fields, models


class OPFReport(models.Model):
    _name = "opf.report"
    _description = "After OPF Statistics"
    _auto = False
    _rec_name = 'confirmation_date'
    #_order = 'confirmation_date desc'
    
    
    usr_id=fields.Many2one('res.users',string="Sales Person")
    customer_name=fields.Many2one('res.partner',string="Customer")
    opf_name=fields.Char(string="OPF No.")
    opf_status=fields.Char(string="OPF Status")
    opf_qty=fields.Integer(string="OPF Quantity")
    po_no=fields.Char(string="PO No.")
    po_status=fields.Char("PO Status")
    purchase_qty=fields.Integer(string="PO Qty")
    received_qty=fields.Integer(string="Received Qty")
    qty_delivered=fields.Integer(string="Delivered Qty")
    inv_name=fields.Char(string="Invoice No.")
    inv_state=fields.Char(string="Invoice Status")
    confirmation_date=fields.Date(string="OPF Date")
    prod_id=fields.Many2one('product.product',string="-")
    part_no=fields.Text(related='prod_id.description_sale',compute='limit_desc',string="Product Description")
    po_date=fields.Date(string="PO Date")
    @api.model_cr
    def init(self):
        #self._table = quotation_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW  %s as(
            select 
            row_number() OVER () as id,
            u.id as usr_id,
            res.id as customer_name ,
            ord.confirmation_date::Date as confirmation_date,
            opf_name as opf_name,
            case when ord.state='done' and ord.approve_flag='t' Then 'Approved OPF'
            when ord.state='sale' and ord.approve_flag='t' Then 'Validated'
            when ord.state='sale' and ord.approve_flag='f' Then 'Open' 
            END as opf_status,
            product_uom_qty  as opf_qty,
            p.name as po_no,
            case when p.state='draft'Then 'Draft' 
                when p.state='purchase' Then 'Loaded'
                when p.state='cancel' Then 'Cancelled' End as po_status,
            product_qty as purchase_qty, 
            Qty_received as received_qty,
            sl.qty_delivered as qty_delivered,
            ac.number as inv_name,
            case when ac.state='draft' Then 'Draft'
                when ac.state='open' Then 'Invoiced'
                when ac.state='paid' Then 'Payment Received'
		when ac.state is null Then 'To Invoice' End as inv_state,
            sl.product_id as prod_id,
            p.date_order as po_date
            from sale_order_line sl
                inner join sale_order ord on sl.order_id=ord.id
                left join sale_order_line_invoice_rel sla on sla.order_line_id = sl.id
                left join account_invoice_line al on al.id = sla.invoice_line_id --and al.product_id = sl.product_id
                left join account_invoice ac on ac.id = al.invoice_id
                left join purchase_order_line pl on pl.saleorder_line_id = sl.id
                left join purchase_order p on p.id = pl.order_id
                inner join res_partner res on ord.partner_id=res.id
                inner join cust_type ct on ct.id = res.cust_type
                inner join res_users u on u.id=ord.user_id
                inner join res_partner res_u on res_u.id=u.partner_id
            where ord.state in ('sale','done'))
            """%(self._table))



        # select 
        #     row_number() OVER () as id,
        #     u.id as usr_id,
        #     res.id as customer_name ,
        #     ord.confirmation_date::Date as confirmation_date,
        #     opf_name as opf_name,
        #     case when ord.state='done' and ord.approve_flag='t' Then 'Approved OPF'
        #     when ord.state='sale' and ord.approve_flag='t' Then 'Validated'
        #     when ord.state='sale' and ord.approve_flag='f' Then 'Open' 
        #     END as opf_status,
        #     product_uom_qty  as opf_qty,
        #     p.name as po_no,
        #     case when p.state='draft'Then 'Draft' 
        #         when p.state='purchase' Then 'Loaded'
        #         when p.state='cancel' Then 'Cancelled' End as po_status,
        #     product_qty as purchase_qty, 
        #     Qty_received as received_qty,
        #     sl.qty_delivered as qty_delivered,
        #     ac.number as inv_name,
        #     case when ac.state='draft' Then 'Draft'
        #         when ac.state='open' Then 'Invoiced'
        #         when ac.state='paid' Then 'Payment Received' End as inv_state,
        #     sl.product_id as prod_id
        #     from sale_order ord 
        #     inner join res_partner res on ord.partner_id=res.id
        #     inner join res_users u on u.id=ord.user_id 
        #     inner join res_partner res_u on res_u.id=u.partner_id
        #     inner join sale_order_line sl on sl.order_id=ord.id
        #     left join purchase_order_line pl on pl.saleorder_line_id=sl.id 
        #     left join purchase_order p on p.id=pl.order_id
        #     left join account_invoice ac on ac.origin=ord.name
        #     where ord.state in ('sale','done')
