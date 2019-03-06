from odoo import tools
from odoo import api, fields, models


class MisReport(models.Model):
	_name = "mis.report"
	_description = "MIS Report"
	_auto = False
	#_rec_name = 'confirmation_date'
	#user_name=fields.Char('Sales Person')

	id_user=fields.Many2one('res.users',string="Sales Person",readonly=True)
	bu_head=fields.Many2one('res.users',string="BU Head")
	cust_name=fields.Many2one('res.partner','Customer Name')
	opf_name=fields.Char(string="OPF No.")
	purchase_val_stp=fields.Float('Purchase Amount')
	btm_line_in=fields.Float(string='Bottom Line')
	top_line_in=fields.Float(string='Top Line')
	lineob=fields.Many2one('line_of_business.info','Line of Business (LOB)')
	purchase_nego=fields.Float(string='Purchase Value Negotiated')
	top_line_out=fields.Float(string='Top Line Out')
	act_btm_line_margin_in=fields.Float(string='Actual Bottom Line')
	btm_line_out=fields.Float(string='Bottom Line Out')
	quat=fields.Char('SY Quarter In')
	invoice_quater=fields.Char("Quarter")
	fin_yr=fields.Char(string='FY')
	sale_yr=fields.Char(string='SY')
	in_mnth=fields.Char(string='In Month')
	inv_no=fields.Char(string='Invoice No.')
	inv_date=fields.Date(string='Invoice Date')
	out_mnth=fields.Char(string='Month')
	product_catagory=fields.Char(string='Vendor')
	cust_type=fields.Many2one('cust.type',string='Customer Type')
	location=fields.Char(string='Location')
	pricelist=fields.Char('Currency')
	stata=fields.Char(string='Sales In/Out')
	confirmation_date=fields.Date()
	deal_type=fields.Many2one('deal_type.info',string="Deal Type")
	vertical=fields.Selection([(1,'1.0 (Hardware, Software)'),(2, '2.0 (PSO, MSO)'),(3,'3.0 (IOT, BI)')],string='Vertical')
	pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)
	@api.model_cr
	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW  %s as(
			WITH currency_rate as (%s)
		select
		row_number() OVER () as id,ord.confirmation_date::Date as confirmation_date,
		CASE
		when EXTRACT(month from ord.confirmation_date) IN (11,12,1) THEN 'Q1'
		when EXTRACT(month from ord.confirmation_date) BETWEEN 2 AND 4 THEN 'Q2'
		when EXTRACT(month from ord.confirmation_date) BETWEEN 5 AND 7 THEN 'Q3'
		when EXTRACT(month from ord.confirmation_date) BETWEEN 7 AND 10 THEN 'Q4' END as quat,
		ord.user_id as id_user,
		--res_u.name as user_name,
		--res.name as cust_name,
		ord.partner_id as cust_name,
		ord.opf_name as opf_name,
		sl.line_of_business as lineob,
		trim(split_part(c.complete_name,'/',1)) AS product_catagory,
		sum((sl.purchase_price*sl.product_uom_qty)/COALESCE(cr.rate, 1.0)) as purchase_val_stp,
		case 
		when ac.number is not null then sum(((sl.price_unit-sl.purchase_price)*al.quantity) /COALESCE(cr.rate, 1.0))when ac.number is null and p.name is not null then sum(((sl.price_unit-sl.purchase_price)*pl.product_qty)/COALESCE(cr.rate, 1.0))
		else sum(((sl.price_unit-sl.purchase_price)*sl.product_uom_qty)/COALESCE(cr.rate, 1.0)) end
		as btm_line_in,
		case 
		when ac.number is not null and p.name is not null then sum((sl.price_unit* al.quantity) / COALESCE(cr.rate, 1.0))
		when ac.number is null and p.name is not null then sum((sl.price_unit* pl.product_qty) / COALESCE(cr.rate, 1.0))
		else sum((sl.price_unit * sl.product_uom_qty) / COALESCE(cr.rate, 1.0)) end
		as top_line_in,
		case
		when ac.number is not null and p.name is not null then sum((pl.purchase_price*al.quantity) / COALESCE(cr.rate, 1.0))
                when ac.number is not null and p.name is null then (sum((sl.purchase_price*al.quantity)/ COALESCE(cr.rate,1.0))
		when ac.number is null and p.name is not null then sum((pl.purchase_price*pl.product_qty)/COALESCE(cr.rate, 1.0))
		else sum((sl.purchase_price*sl.product_uom_qty)/COALESCE(cr.rate, 1.0))
		end as purchase_nego,
		case
		when ac.number is not null and p.name is not null then sum((sl.price_unit*al.quantity)/COALESCE(cr.rate, 1.0))-sum((pl.purchase_price*al.quantity) /COALESCE(cr.rate, 1.0))
                when ac.number is not null and p.name is null then sum((sl.price_unit*al.quantity)/COALESCE(cr.rate,1.0)) - sum((sl.purchase_price*al.quantity)/COALESCE(cr.rate,1.0))
		when ac.number is null and p.name is not null then sum((sl.price_unit*pl.product_qty)/COALESCE(cr.rate, 1.0))-sum((pl.purchase_price*pl.product_qty)/COALESCE(cr.rate, 1.0)) 
		else sum((sl.price_unit*sl.product_uom_qty)/COALESCE(cr.rate, 1.0))-sum((sl.purchase_price*sl.product_uom_qty)/COALESCE(cr.rate, 1.0))
		end as act_btm_line_margin_in,
		case
		when sum((al.quantity*al.price_unit)/COALESCE(cr.rate, 1.0)) is null then 0.00
		else sum((al.quantity*al.price_unit)/COALESCE(cr.rate, 1.0)) end as top_line_out,
		case
		when sum((al.quantity*al.price_unit)/COALESCE(cr.rate, 1.0))-sum((sl.purchase_price*al.quantity)/COALESCE(cr.rate, 1.0)) is null then 0.00
		else sum((al.quantity*al.price_unit)/COALESCE(cr.rate, 1.0))-sum((sl.purchase_price*al.quantity)/COALESCE(cr.rate, 1.0)) end as btm_line_out,
		case when to_char(ac.date_invoice,'mm')::int>=11 then 'SY'||to_char(ac.date_invoice,'YY')::int||'-'||to_char(ac.date_invoice,'YY')::int+1
		else 'SY'||to_char(ac.date_invoice,'YY')::int-1||'-'||to_char(ac.date_invoice,'YY')::int end as sale_yr,
		case when to_char(ac.date_invoice,'mm')::int>=4 then 'FY'||to_char(ac.date_invoice,'YY')::int||'-'||to_char(ac.date_invoice,'YY')::int+1
		else 'FY'||to_char(ac.date_invoice,'YY')::int-1||'-'||to_char(ac.date_invoice,'YY')::int end as fin_yr,
		TO_CHAR(ord.confirmation_date :: DATE,'MON ,YY' ) as in_mnth,
		CASE
		when EXTRACT(month from ac.date_invoice) IN (11,12) THEN 'Q1'||E'\\''||to_char(ac.date_invoice,'YY')::int+1
		when EXTRACT(month from ac.date_invoice) = 1 THEN 'Q1'||E'\\''||to_char(ac.date_invoice,'YY')::int
		when EXTRACT(month from ac.date_invoice) BETWEEN 2 AND 4 THEN 'Q2'||E'\\''||to_char(ac.date_invoice,'YY')
		when EXTRACT(month from ac.date_invoice) BETWEEN 5 AND 7 THEN 'Q3'||E'\\''||to_char(ac.date_invoice,'YY')
		when EXTRACT(month from ac.date_invoice) BETWEEN 8 AND 10 THEN 'Q4'||E'\\''||to_char(ac.date_invoice,'YY') END as invoice_quater,
		ac.number as inv_no,
		ac.date_invoice::Date as inv_date,
		to_char(ac.date_invoice::Date,E'MON\\'YY') as out_mnth,
		res.cust_type as cust_type,
		ord.billing_location as location,
		j.name as pricelist,
		ord.pricelist_id as pricelist_id,
		CASE
		when ac.number is null then 'In'
		Else 'Out'
		End as stata,
		apin.users as bu_head,
		sl.deal_type_sol as deal_type,
		ord.vertical as vertical
		from sale_order_line sl
		inner join sale_order ord on sl.order_id = ord.id
		left join sale_order_line_invoice_rel sla on sla.order_line_id = sl.id
		left join account_invoice_line al on al.id = sla.invoice_line_id --and al.product_id = sl.product_id
		left join account_invoice ac on ac.id = al.invoice_id
		left join purchase_order_line pl on pl.saleorder_line_id = sl.id
		left join purchase_order p on p.id = pl.order_id
		inner join res_partner res on ord.partner_id=res.id
		inner join cust_type ct on ct.id = res.cust_type
		inner join res_users u on u.id=ord.user_id
		inner join res_partner res_u on res_u.id=u.partner_id
		inner join product_pricelist j on j.id=ord.pricelist_id
		left join currency_rate cr on (cr.currency_id = j.currency_id and
                        cr.company_id = ord.company_id and
                        cr.date_start <= coalesce(ord.date_order, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(ord.date_order, now())))
		inner join product_product pro on pro.id=sl.product_id
		inner join product_template t on t.id=pro.product_tmpl_id
		inner join product_category c on c.id=t.categ_id
		left join res_partner es on 
		Case 
		when trim(split_part(c.complete_name,'/',1)) = 'Sunfire' 
		then es.name like '%s'
    		else es.name=trim(split_part(c.complete_name,'/',1)) end
		--left join res_partner es on es.name=trim(split_part(c.complete_name,'/',1))
		left join approval_info apin on apin.vendor = es.id and apin.approval_type=4
		where ord.state in ('done','sale') and COALESCE(p.state,'') != 'cancel' 
		and COALESCE(ac.state,'') not in ('cancel') and es.oem=true
		group by bu_head,sl.deal_type_sol,ord.vertical,ord.pricelist_id,
		p.name,ord.user_id,ord.partner_id,ord.opf_name,sl.line_of_business,quat,invoice_quater,fin_yr,sale_yr,in_mnth,ac.number,ac.date_invoice::Date
		,out_mnth,trim(split_part(c.complete_name,'/',1)),res.cust_type,ord.billing_location,j.name,stata,ord.confirmation_date order by ac.number desc NULLS LAST)
		"""%(self._table,self.env['res.currency']._select_companies_rates(),'Sunfire %'))

