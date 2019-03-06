Ahmednagar
Akola
Amravati
Aurangabad
Beed
Bhandara
Buldhana
Chandrapur
Dhule
Gadchiroli
Gondia
Hingoli
Jalgaon
Jalna
Kolhapur
Latur
Mumbai City
Mumbai Suburban
Nagpur
Nanded
Nandurbar
Nashik
Osmanabad
Palghar
Parbhani
Pune
Raigad
Ratnagiri
Sangli
Satara
Sindhudurg
Solapur
Thane
Wardha
Washim
Yavatmal
('upload_type_info_sam',1137),
('approval_type_line_info_sam',1136),
('Ir_Mail_server_sam',1135),
('master_category_info_sam',1134),
('master_sub_category_info_sam',1133),
('transaction_sunfire_timesheet_sam',1132),
('transaction_sunfire_timesheet_line_sam',1131),
('upload_tab_info_sam',1130),
('approval_tab_info_sam',1129),
('master_approval_types_info_sam',1128),
('master_cust_type_sam',1127),
('master_deal_type_info_sam',1126),
('master_approval_info_sam',1125),
('transaction_dr_info_sam',1124),
('sale_layout_category_sam',1123),
('master_sales_stages_info_sam',1122),
('master_transport_mode_info_sam',1121),
('master_warranty_information_info_sam',1120),
('master_opportunity_stages_info_sam',1119),
('master_lead_source_info_sam',1118),
('master_line_of_business_info_sam',1117),
('master_installtion_terms_info_sam',1116),
('master_delivery_period_info_sam',1115),
('master_delivery_term_info_sam',1114),
('access_mis_report_sam',1113),
('access_mis_report_new_sam',1112),
('access_pipeline_report_sam',1111),
('access_opf_report_sam',1110),
('report_all_channels_sales_sam',969),
('account_account_sale_sam',968),
('report_layout_category_1_sam',967),
('res_partner_group_sale_sam',966),
('product_pricelist_sale_sam',965),
('product_supplierinfo_sale_sam',964),
('product_category_sale_sam',963),
('product_uom_sale_sam',962),
('product_uom_categ_sale_sam',961),
('res_partner_sale_sam',960),
('sale_order_sam',959),
('calendar_event_type_sam',958),
('access_mis_report',957),
('access_report_mis_new',956),
('access_opf_stat',955),
('access_lead_stat',954),
('calendar_event_sam',953),
('crm_lost_reason_sam',952),
('product_attribute_sam_line',951),
('product_attribute_sam_price',950),
('product_attribute_sam_value',949),
('product_attribute_sam',948),
('product_product_sale_sam',947),
('product_template_sale_sam',946),
('stock_location_path_partner_sale_sam',945),
('procurement_rule_sale_sam',944),
('stock_location_sale_sam',943),
('product_packaging_sale_sam',942),
('product_packaging_sam',941),
('stock_picking_sales',940),
('prices_history_sale_sam',939),
('product_pricelist_item_sale_sam',938),
('sale_report',937),
('account_invoice_sam',936),
('stock_move_sam',935),
('crm_lead_tag_sam',934),
('res_partner_category_crm_sam',933),
('res_partner_crm_sam',932),
('crm_opportunity_report',931),
('crm_stage',930),
('crm_lead_sam',929),
('crm_team_sam',928),

"6d/6d8493e204fb148e54715d4bf5b25f25bc4304c5"



Ahmednagar
Akola
Amravati
Aurangabad
Beed
Bhandara
Buldhana
Chandrapur
Dhule
Gadchiroli
Gondia
Hingoli
Jalgaon
Jalna
Kolhapur
Latur
Mumbai City
Mumbai Suburban
Nagpur
Nanded
Nandurbar
Nashik
Osmanabad
Palghar
Parbhani
Pune
Raigad
Ratnagiri
Sangli
Satara
Sindhudurg
Solapur
Thane
Wardha
Washim
Yavatmal



select 
				row_number() OVER () as id,ord.confirmation_date::Date as confirmation_date,
				CASE
				when EXTRACT(month from ord.confirmation_date) BETWEEN 11 AND 1 THEN 'Q1'
				when EXTRACT(month from ord.confirmation_date) BETWEEN 2 AND 4 THEN 'Q2'
				when EXTRACT(month from ord.confirmation_date) BETWEEN 5 AND 7 THEN 'Q3'
				when EXTRACT(month from ord.confirmation_date) BETWEEN 7 AND 10 THEN 'Q4' END as quat, 
				res_u.name as user_id,
				res.id as customer_name,
				ord.opf_name as opf_name,
				sl.line_of_business as lob,
				trim(split_part(c.complete_name,'/',1)) AS product_catagory,
				sum(sl.purchase_price*sl.product_uom_qty) as purchase_val_stp,
				sum(sl.margin_value*sl.product_uom_qty) as btm_line_margin_in,
				sum(sl.price_unit* sl.product_uom_qty ) as top_line_in_ctp,
				case 
				when sum(pl.purchase_price*pl.product_qty) is null then 0.00
				else sum(pl.purchase_price*pl.product_qty) end as purchase_nego,
				case 
				when sum(sl.price_unit*sl.product_uom_qty)-sum(pl.purchase_price*pl.product_qty) is null then 0.00
				else sum(sl.price_unit*sl.product_uom_qty)-sum(pl.purchase_price*pl.product_qty) end as act_btm_line_margin_in,
				case 
				when sum(al.quantity*al.price_unit) is null then 0.00
				else sum(al.quantity*al.price_unit) end as toplineoutinv,
				case
				when sum(al.quantity*al.price_unit)-sum(sl.purchase_price*sl.product_uom_qty) is null then 0.00
				else sum(al.quantity*al.price_unit)-sum(sl.purchase_price*sl.product_uom_qty) end as btm_line_out,
				case when to_char(ord.confirmation_date,'mm')::int>=11 then 'SY'||to_char(ord.confirmation_date,'YY')::int||'-'||to_char(ord.confirmation_date,'YY')::int+1
				else 'SY'||to_char(ord.confirmation_date,'YY')::int-1||'-'||to_char(ord.confirmation_date,'YY')::int end as sale_yr,
				case when to_char(ord.confirmation_date,'mm')::int>=4 then 'FY'||to_char(ord.confirmation_date,'YY')::int||'-'||to_char(ord.confirmation_date,'YY')::int+1
				else 'FY'||to_char(ord.confirmation_date,'YY')::int-1||'-'||to_char(ord.confirmation_date,'YY')::int end as fin_yr,
				TO_CHAR(ord.confirmation_date :: DATE,'MON ,YY' ) as in_mnth,
				CASE
				when EXTRACT(month from ac.date_invoice) BETWEEN 11 AND 1 THEN 'Q1'
				when EXTRACT(month from ac.date_invoice) BETWEEN 2 AND 4 THEN 'Q2'
				when EXTRACT(month from ac.date_invoice) BETWEEN 5 AND 7 THEN 'Q3'
				when EXTRACT(month from ac.date_invoice) BETWEEN 7 AND 10 THEN 'Q4' END as inv_quat,
				ac.number as inv_no,
				ac.date_invoice::Date as inv_date,
				to_char(ac.date_invoice::Date,'MON ,YY') as out_mnth,
				res.cust_type as cust_type,
				ord.billing_location as location,
				j.id AS pricelist_id,
				CASE 
				when ac.number is null then 'In'
				Else 'Out'
				End as stata
				from sale_order_line sl
				inner join sale_order ord on ord.id=sl.order_id
				inner join res_partner res on ord.partner_id=res.id
				inner join cust_type ct on ct.id = res.cust_type
				inner join res_users u on u.id=ord.user_id
				inner join res_partner res_u on res_u.id=u.partner_id
				inner join product_pricelist j on j.id=ord.pricelist_id
				inner join product_product pro on pro.product_tmpl_id=sl.product_id
				inner join product_template t on t.id=pro.product_tmpl_id
				inner join product_category c on c.id=t.categ_id
				left join purchase_order p on p.origin=ord.name
				left join purchase_order_line pl on pl.order_id=p.id and pl.saleorder_line_id=sl.id 
				left join account_invoice ac on ac.origin=ord.name
				left join account_invoice_line al on al.invoice_id=ac.id
				where ord.state in ('done','sale')
				group by 
			res_u.name,customer_name,opf_name,lob,quat,inv_quat,fin_yr,sale_yr,in_mnth,inv_no,inv_date
			,out_mnth,product_catagory,res.cust_type,location,j.id,stata,confirmation_date order by inv_date desc




id
