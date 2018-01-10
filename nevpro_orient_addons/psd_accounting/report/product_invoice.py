
#version 1.0.041 to remove hardcoded address,email,phoneno,website from report
from report import report_sxw
import time
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in
from corporate_address import *
from datetime import datetime


sqrt_unit = [('sqr_ft','Sq.ft'),('sqr_mt','Sq.Mt'),('running_mt','Running Mtr')]
list_payment_term = [('full_payment','Full Payment in Advance'),('advance','50% Advance & Balance 50% within 6 Months'),('quarter','Quarterly Payment'),('monthly','Monthly Payment'),('annual','Annual Payment'),('custom','Custom')]

class product_invoice(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(product_invoice, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'amount_to_text_in': amount_to_text_in,
			'get_requester_address':self.get_requester_address,
			'get_registered_office_address':self.get_registered_office_address,
			'get_branch_addr':self.get_branch_addr,
			'get_corporate_address':self.get_corporate_address,
			'get_particulars':self.get_particulars,
			'get_rate_amount':self.get_rate_amount,
			'get_rate_amount_in':self.get_rate_amount_in,
			'get_declaration':self.get_declaration,
			'get_primary_address': self.get_primary_address,
			'strip_date':self.strip_date,
			'strip_hsn':self.strip_hsn,
			'get_rate':self.get_rate,
			'get_first_address':self.get_first_address,
			'print_narration':self.print_narration,

		})

	def get_rate(self,rate):
		rate_v=''
		if rate:
			print format(rate,'.2f')
			rate_v=format(rate,'.2f')
		return rate_v

	def strip_hsn(self,hsn):
		hsn_t=''
		if hsn:
			print str(hsn)[0:4],'===============hsn======='
			hsn_t=str(hsn)[0:4]
		return hsn_t

	def get_first_address(self,invoice_id): # Consignee address
		cr = self.cr
		uid = self.uid
		invoice_obj = self.pool.get('invoice.adhoc.master')
		location_obj = self.pool.get('customer.line')
		search_id=''
		dic = {
				'first_address':'',
				'first_telephone':'',
				'first_mobile':'',
				'first_email':'',
				'first_city':'',
				'first_state':'',
				'first_state_code':'' 
			 }
		invoice_data = invoice_obj.browse(cr,uid,invoice_id)
		if invoice_data.product_invoice_lines:
			first_data = invoice_data.product_invoice_lines[0]
			location_name = first_data.location.location_name if first_data.location.location_name else ''
			apartment = first_data.location.apartment if first_data.location.apartment else ''
			building = first_data.location.building if first_data.location.building else ''
			sub_area = first_data.location.sub_area if first_data.location.sub_area else ''
			street = first_data.location.street if first_data.location.street else ''
			landmark = first_data.location.landmark if first_data.location.landmark else ''
			city_id = first_data.location.city_id.name1 if first_data.location.city_id.name1 else ''
			state_id = first_data.location.state_id.name if first_data.location.state_id.name else ''
			zipc = "- " + first_data.location.zip if first_data.location.zip else ""
			first_address = [location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
			first_address = ', '.join(filter(bool,first_address))
			phone_data = first_data.location.partner_address.phone_m2m_xx
			if phone_data.type == 'landline':
				dic['first_telephone'] = phone_data.name
			if phone_data.type == 'mobile':
				dic['first_mobile'] = phone_data.name	
			first_email = first_data.location.email if first_data.location.email else ""
			first_city = first_data.location.city_id.name1 if first_data.location.city_id.name1 else ''
			first_state = first_data.location.state_id.name if first_data.location.state_id.name else ''
			first_state_code = first_data.location.state_id.state_code if first_data.location.state_id.state_code else ''
			location_id = location_obj.search(cr,uid,[('customer_address','=',first_data.location.partner_address.id),('partner_id','=',invoice_data.partner_id.id)])
			gst_no = location_obj.browse(cr,uid,location_id[0]).gst_no
			if not gst_no:
				gst_no = invoice_data.partner_id.gst_no
				if not gst_no:
					gst_no = invoice_data.partner_id.uin_no
			dic['first_address'] = first_address
			dic['first_email'] = first_email
			dic['first_city'] = first_city
			dic['first_state'] = first_state
			dic['first_state_code'] = first_state_code
			dic['gst_no'] = gst_no
		return dic

	def get_primary_address(self,partner_id,self_id): # Primary address
		cr = self.cr
		uid = self.uid
		location_obj = self.pool.get('customer.line')
		partner_obj = self.pool.get('res.partner')
		partner_address_obj = self.pool.get('res.partner.address')
		search_id = ''
		dic = {
				'primary_address':'',
				'primary_telephone':'',
				'primary_mobile':'',
				'primary_email':'',
				'primary_city':'',
				'primary_state':'',
				'primary_state_code':'' 
			 }
		res = self.pool.get('invoice.adhoc.master').browse(cr,uid,self_id)
		if res.location:
			primary_data = partner_address_obj.browse(cr,uid,res.location.id)
			location_name = primary_data.location_name if primary_data.location_name else ''
			apartment = primary_data.apartment if primary_data.apartment else ''
			building = primary_data.building if primary_data.building else ''
			sub_area = primary_data.sub_area if primary_data.sub_area else ''
			street = primary_data.street if primary_data.street else ''
			landmark = primary_data.landmark if primary_data.landmark else ''
			city_id = primary_data.city_id.name1 if primary_data.city_id.name1 else ''
			state_id = primary_data.state_id.name if primary_data.state_id.name else ''
			zipc = "- " + primary_data.zip if primary_data.zip else ""
			primary_address = [location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
			primary_address = ', '.join(filter(bool,primary_address))
			phone_data = primary_data.phone_m2m_xx
			if phone_data.type == 'landline':
				dic['primary_telephone'] = phone_data.name
			if phone_data.type == 'mobile':
				dic['primary_mobile'] = phone_data.name	
			primary_email = primary_data.email if primary_data.email else ''
			primary_city = primary_data.city_id.name1 if primary_data.city_id.name1 else ''
			primary_state = primary_data.state_id.name if primary_data.state_id.name else ''
			primary_state_code = primary_data.state_id.state_code if primary_data.state_id.state_code else ''
			partner_data = partner_obj.browse(cr,uid,partner_id)
			location_id = location_obj.search(cr,uid,[('customer_address','=',primary_data.id),('partner_id','=',partner_id)])
			gst_no = location_obj.browse(cr,uid,location_id[0]).gst_no
			if not gst_no:
				gst_no = res.partner_id.gst_no
				if not gst_no:
					gst_no = res.partner_id.uin_no
			dic['primary_address'] = primary_address
			dic['primary_city'] = primary_city
			dic['primary_state'] = primary_state
			dic['primary_state_code'] = primary_state_code
			dic['primary_email'] = primary_email
			dic['gst_no'] = gst_no
		else:	
			customer_line_id = location_obj.search(cr,uid,[('partner_id','=',partner_id),('check_primary_address_contact','=',True)])
			if not customer_line_id:
				customer_line_ids = location_obj.search(cr,uid,[('partner_id','=',partner_id)])
				if len(customer_line_ids) > 1:
					temp_ids = []
					for customer_line_id in customer_line_ids:
						customer_line_data = location_obj.browse(cr,uid,customer_line_id)
						temp_ids.append(customer_line_data.location_id)
						min_temp_id = min(temp_ids)
						first_location_id = location_obj.search(cr,uid,[('partner_id','=',partner_id),('location_id','=',min_temp_id)])
						location_id = first_location_id[0]
				else:
					location_id = customer_line_ids[0]
					print location_id,'===============loc'
			else:
				location_id = customer_line_id[0]
			primary_location = location_id
			primary_data = location_obj.browse(cr,uid,primary_location)
			location_name = primary_data.customer_address.location_name if primary_data.customer_address.location_name else ''
			apartment = primary_data.customer_address.apartment if primary_data.customer_address.apartment else ''
			building = primary_data.customer_address.building if primary_data.customer_address.building else ''
			sub_area = primary_data.customer_address.sub_area if primary_data.customer_address.sub_area else ''
			street = primary_data.customer_address.street if primary_data.customer_address.street else ''
			landmark = primary_data.customer_address.landmark if primary_data.customer_address.landmark else ''
			city_id = primary_data.customer_address.city_id.name1 if primary_data.customer_address.city_id.name1 else ''
			state_id = primary_data.customer_address.state_id.name if primary_data.customer_address.state_id.name else ''
			zipc = "- " + primary_data.customer_address.zip if primary_data.customer_address.zip else ""
			primary_address = [location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
			primary_address = ', '.join(filter(bool,primary_address))
			phone_data = primary_data.customer_address.phone_m2m_xx
			if phone_data.type == 'landline':
				dic['primary_telephone'] = phone_data.name
			if phone_data.type == 'mobile':
				dic['primary_mobile'] = phone_data.name		
			primary_email = primary_data.customer_address.email if primary_data.customer_address.email else ""
			primary_city = primary_data.customer_address.city_id.name1 if primary_data.customer_address.city_id.name1 else ''
			primary_state = primary_data.customer_address.state_id.name if primary_data.customer_address.state_id.name else ''
			primary_state_code = primary_data.customer_address.state_id.state_code if primary_data.customer_address.state_id.state_code else ''
			partner_data = partner_obj.browse(cr,uid,partner_id)
			if res.invoice_line_adhoc_12:
				addrs_id = res.invoice_line_adhoc_12[0].location.partner_address.id
			else:
				addrs_id = res.invoice_line_adhoc_gst[0].location_invoice.id
			location_id = location_obj.search(cr,uid,[('customer_address','=',addrs_id),('partner_id','=',partner_id)])
			gst_no = location_obj.browse(cr,uid,location_id[0]).gst_no
			if not gst_no:
				gst_no = res.partner_id.gst_no
				if not gst_no:
					gst_no = res.partner_id.uin_no
			dic['primary_address'] = primary_address
			dic['primary_email'] = primary_email
			dic['primary_city'] = primary_city
			dic['primary_state'] = primary_state
			dic['primary_state_code'] = primary_state_code
			dic['gst_no'] = gst_no
		return dic
	def get_rate_amount(self,stock):
		res={}
		cr=self.cr
		uid=self.uid
		total_amount=grand_total = 0.0
		stock_id=self.pool.get('stock.transfer').browse(cr,uid,stock)
		for line_prod in stock_id.stock_transfer_product:
			total_amount+=(line_prod.st_price*line_prod.quantity)
		grand_total += (total_amount + stock_id.freight_amount)
		res['total_amount']="%.2f" % round(grand_total)
		res['grand_total_word']=round(grand_total)
		res['total_amount']=total_amount
		return res
	def strip_date(self,date):
		date_v=''
		print date
		if date:
			date_v=str(date)[0:10]
		print date_v
		return date_v
	def get_rate_amount_in(self,rate,quantity):
		return rate*quantity
	def get_requester_address(self,delivery_location):
		return get_requester_address(self,delivery_location)
	
	def get_branch_addr(self,self_id):
		return get_branch_addr(self,self_id)
		
	def get_registered_office_address(self):
	   return get_registered_office_address(self)
	
	def get_corporate_address(self):
		return get_corporate_address(self)
	
	def get_particulars(self,self_id):
		return get_particulars(self,self_id)

	########## 8 sept 16 changes in declarion for Within and outside Maharashtra state ##########
	def get_declaration(self):
		res={}
		cr=self.cr
		uid=self.uid
		user=self.pool.get('res.users').browse(cr,uid,uid)
		if user.company_id.state_id:
			state_name=user.company_id.state_id.name
			if state_name.lower()== 'maharashtra':
				res['declaration_str']='''"I/We hereby certify that my/our registration certificate under the Maharashtra Value Added Tax Act, 2002, is in force on the date on which the sale of the goods specified in this Tax Invoice is made by me/us and that the transaction of sale covered by this tax invoice has been effected by me/us and it shall be accounted for in the turnover of sales while filing of return and the due tax. If any, payable on the sale has been paid or shall be paid."'''
			else:
				res['declaration_str']="*I / We hereby certify that my/our registration Certificate under the CST/VAT Act, is in force on the Date on which the sale of the goods in this bill/Cash memorandum is made by me/us and the transaction of sale covered by this Bill/Cash memorandum has been affected by me/us in the regular course of my/our Business.*"
			
		return res

	def print_narration(self,narr,flag):
		cr = self.cr
		uid = self.uid
		dic = {
			'narration':'',
			}
		if flag==True:
			dic['narration']="Narration: " + str(narr) 
		return dic

# report_sxw.report_sxw('report.stock.transfer', 'stock.transfer', '/sk/report/stock_transfer1.rml', parser=order, header="external")

report_sxw.report_sxw('report.product_invoice', 'invoice.adhoc.master', 'addons/psd_accounting/report/product_invoice.rml', parser=product_invoice, header=False)

