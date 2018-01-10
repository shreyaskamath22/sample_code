
#version 1.0.041 to remove hardcoded address,email,phoneno,website from report
from report import report_sxw
import time
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in
from corporate_address import *

sqrt_unit = [('sqr_ft','Sq.ft'),('sqr_mt','Sq.Mt'),('running_mt','Running Mtr')]
list_payment_term = [('full_payment','Full Payment in Advance'),('advance','50% Advance & Balance 50% within 6 Months'),('quarter','Quarterly Payment'),('monthly','Monthly Payment'),('annual','Annual Payment'),('custom','Custom')]

class gst_invoice_adhoc_ipm_report(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(gst_invoice_adhoc_ipm_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'amount_to_text_in': amount_to_text_in,
			'get_branch_addr':self.get_branch_addr,
			'get_cust_addr':self.get_cust_addr,
			'get_service_classification':self.get_service_classification,
			'get_payment':self.get_payment,
			'get_unit':self.get_unit,
			'get_status':self.get_status,
			'get_contract_val':self.get_contract_val,
			'tax_label':self.tax_label,
			'tax_label_amount':self.tax_label_amount,
			'get_corporate_address':self.get_corporate_address,
			'get_registered_office_address':self.get_registered_office_address,
			'get_pms_location_addr':self.get_pms_location_addr,
			'get_ipm_address':self.get_ipm_address,
			'get_parent_branch':self.get_parent_branch,
			'get_report_type': self.get_report_type,
			'get_primary_address': self.get_primary_address,
			'get_first_address': self.get_first_address,
			'get_tax_total': self.get_tax_total,		
			'get_service_title': self.get_service_title,
			'get_service_address': self.get_service_address,
			'get_government_notification': self.get_government_notification,
			'print_narration': self.print_narration,
			'get_format_digits':self.get_format_digits,
		})
	def get_format_digits(self,val):
		val_t=val.split(".")
		if val=="0.00%" or val_t[1] !='0%':
			return val
		val_t[1]="0"+val_t[1]
		val_t=".".join(val_t)
		return val_t
	def get_corporate_address(self):
		return get_corporate_address(self)
	
	def get_pms_location_addr(self,self_id):
		return get_pms_location_addr(self,self_id)
	
	def get_registered_office_address(self):
	   return get_registered_office_address(self)

	def get_branch_addr(self,self_id):
		 return get_branch_addr(self,self_id)

	def get_contract_val(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = {'cotract_val':'',}
		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
			if res.contract_no:
	        		for pay in self.pool.get('sale.contract').browse(cr,uid,[res.contract_no.id]):
		        		dic['cotract_val'] = format(pay.grand_total_amount,'.2f')

		return dic
		
	
	def get_cust_addr(self,self_id):
		return get_cust_addr(self,self_id)
	
	def tax_label(self, srch_ids):
		return tax_label(self, srch_ids)
		
	def tax_label_amount(self,srch_ids):
		return tax_label_amount(self,srch_ids)
	
	def get_payment(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = {
			'pay_term':'',
			}
		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
			for pay in list_payment_term:
				if res.payment_term == pay[0]:
					dic['pay_term'] = pay[1]
		return dic

	def print_narration(self,narr,flag):
		cr = self.cr
		uid = self.uid
		dic = {
			'narration':'',
			}
		if flag==True:
			dic['narration']="Narration: " + str(narr) 
		return dic
		
	def get_unit(self,self_id,line):
		cr = self.cr
		uid = self.uid
		dic = {
			'sqrt_unit':'',
			}
		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id,line]):
			for ln in self.pool.get('invoice.adhoc').browse(cr,uid,[line]):
					for unit in sqrt_unit:
							if ln.unit == unit[0]:
								   dic['sqrt_unit']=unit[1]  
							else:
								   dic['sqrt_unit'] = ''
		return dic   

	def get_status(self,self_id,line_id):
		cr = self.cr
		uid = self.uid
		dic = {
			'status':'',           
			}
		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
			for temp in self.pool.get('invoice.adhoc.master').browse(cr,uid,[line_id]):
				if res.id == temp.id:
					dic.update({'status':'Running Bill'})
		return dic

    	def get_parent_branch(self,self_id):
                cr = self.cr
		uid = self.uid
                dic = {
                        'licence_no':'',
                        'branch_addr':'',
                       }
                lis=str1=''
                for r_add in self.pool.get('res.company').browse(cr,uid,[self_id]):
                      lis =r_add.insecticides_restricted_chemical_license_no if r_add.insecticides_restricted_chemical_license_no else ''
                      lis += ' / ' + r_add.chemical_storage_license_no if r_add.chemical_storage_license_no else ''
                      dic['branch_addr']=self.get_branch_addr(r_add.parent_branch_many2one.id)['branch_addr'] if r_add.parent_branch_many2one else ''
		if lis :
	                str1 ="Insecticides License (Form VIII) : "+lis
                dic['licence_no']=str1 
                return dic
                
	def get_service_classification(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = {
				'service_name':'',
				'stc_code':'',
				'service_desc':'',
				'class_service':'',
				'exempted_flag':'',
				}
				
		for rec in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
	
				if rec.service_classification == 'residential':
						dic['service_name'] = 'Residential Service'
						dic['stc_code'] = 'STC Code:   AABCJ9086FSD001'
						dic['service_desc'] = 'DESCRIPTION OF SERVICE:   CLEANING SERVICE'
						dic['class_service'] = ' CLASSIFICATION OF SERVICE:   65(105) (zzzd)'
	
				elif rec.service_classification == 'commercial':
						dic['service_name'] = 'Commercial Service'
						dic['stc_code'] = 'STC Code:  AABCJ9086FSD001'
						dic['service_desc'] = 'DESCRIPTION OF SERVICE:   CLEANING SERVICE'
						dic['class_service'] = ' CLASSIFICATION OF SERVICE:  65(105) (zzzd)'
	
				elif rec.service_classification == 'port':
						dic['service_name'] = 'Port Service'
						dic['stc_code'] = 'STC Code:  AABCJ9086FSD001'
						dic['service_desc'] = 'DESCRIPTION OF SERVICE:  PORT SERVICE'
						dic['class_service'] = 'CLASSIFICATION OF SERVICE:  65(105) (zn)'
	
				elif rec.service_classification == 'airport':
						dic['service_name'] = 'Airport Service'
						dic['stc_code'] = 'STC Code:  AABCJ9086FSD001'
						dic['service_desc'] = 'DESCRIPTION OF SERVICE:  AIRPORT SERVICE'
						dic['class_service'] = 'CLASSIFICATION OF SERVICE:  65(105) (zzm)'
	
				elif rec.service_classification == 'exempted':
					dic['service_name'] = 'Exempted '
					dic['stc_code'] = 'STC Code:  AABCJ9086FSD001'
					dic['service_desc'] = 'DESCRIPTION OF SERVICE:   CLEANING SERVICE'
					dic['class_service'] = ' CLASSIFICATION OF SERVICE:  65(105) (zzzd)'
					stc_code = ''
					
					for iterate in rec.invoice_line_adhoc_11:
						if iterate.location:
							loc=self.pool.get('new.address').browse(cr,uid,iterate.location.id)
							if loc.partner_address.exempted:
								stc_code = loc.partner_address.certificate_no	
								dic['exempted_flag'] = 'Exempted under notification no.= '+ stc_code
		return dic  

	def get_ipm_address(self,ia_id):
		cr = self.cr
		uid = self.uid
		invoice_adhoc_obj=self.pool.get('invoice.adhoc')
		search_id=''
		dic = {
			'ipm_addr':'',
			'rate':'',
			'area':'',
			'unit':'',
			 }
		
		#for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[iam_id]):
		#	if res.adhoc_invoice:
		#		search_id=invoice_adhoc_obj.search(cr,uid,[('invoice_adhoc_id','=',iam_id)])
		#	
		#	if search_id:
		for res in self.pool.get('invoice.adhoc').browse(cr,uid,[ia_id]):
				if res.invoice_adhoc_id.id:	
					location_name = res.location_invoice.location_name if res.location_invoice.location_name else ''
					apartment = res.location_invoice.apartment if res.location_invoice.apartment else ''
					building =res.location_invoice.building if res.location_invoice.building else ''
					sub_area = res.location_invoice.sub_area if res.location_invoice.sub_area else ''
					street = res.location_invoice.street if res.location_invoice.street else ''
					landmark = res.location_invoice.landmark if res.location_invoice.landmark else ''
					city_id = res.location_invoice.city_id.name1 if res.location_invoice.city_id.name1 else ''
					state_id = res.location_invoice.state_id.name if res.location_invoice.state_id.name else ''
					zipc = "- " + res.location_invoice.zip if res.location_invoice.zip else ""
					
					address=[location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
					addr=', '.join(filter(bool,address))
					dic['ipm_addr'] = addr
					dic['rate']=res.rate if res.rate else ''
					dic['area']=res.area if res.area else ''
					unt=res.unit if res.unit else ''
					if dic['rate'] and dic['area'] and unt:
						for unit in sqrt_unit:
							if unt == unit[0]:
								   dic['unit']=unit[1]
								   break
							else:
								   dic['unit'] = ''
			        else:
			                location_name = res.location.location_name
					apartment = res.location.apartment
					building =res.location.building
					sub_area = res.location.sub_area
					street = res.location.street
					landmark = res.location.landmark
					city_id = res.location.city_id.name1
					state_id = res.location.state_id.name
					zipc = "- " + res.location.zip if res.location.zip else ""
					address=[location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
					addr=', '.join(filter(bool,address))
					dic['ipm_addr'] = addr
					dic['rate']=res.rate if res.rate else ''
					dic['area']=res.area if res.area else ''
					unt=res.unit if res.unit else ''
					if dic['rate'] and dic['area'] and unt:
						for unit in sqrt_unit:
								if unt == unit[0]:
									   dic['unit']=unit[1]
									   break
								else:
									   dic['unit'] = ''
				if res.invoice_adhoc_id12.id:
					o=self.pool.get('invoice.adhoc.master').browse(cr,uid,res.invoice_adhoc_id12.id)
					contract_no = o.contract_no.id
					for contract_line_value in self.pool.get('sale.contract').browse(cr,uid,[contract_no]):
						for line_contract_id in contract_line_value.contract_line_id12:
							dic['area']=line_contract_id.area
				if res.invoice_adhoc_id_gst.id:
					o=self.pool.get('invoice.adhoc.master').browse(cr,uid,res.invoice_adhoc_id_gst.id)
					contract_no = o.contract_no.id
					for contract_line_value in self.pool.get('sale.contract').browse(cr,uid,[contract_no]):
						for line_contract_id in contract_line_value.contract_line_id12:
							dic['area']=line_contract_id.area
		return dic

	def get_report_type(self,invoice_id):
		cr = self.cr
		uid = self.uid
		invoice_obj = self.pool.get('invoice.adhoc.master')
		invoice_data = invoice_obj.browse(cr,uid,invoice_id)
		dic = {
				'report_type':'',
				'report_title': '',
			 }
		invoice_title = 'TAX INVOICE'
		if invoice_data.service_classification:
			if invoice_data.service_classification == 'sez':
				invoice_title = 'TAX INVOICE [SEZ]'
			if invoice_data.service_classification == 'exempted':
				invoice_title = 'BILL OF SUPPLY'
		report_type = invoice_data.report_type
		if report_type == 'original':
			dic['report_type'] = 'ORIGINAL FOR RECIPIENT'
			dic['report_title'] = invoice_title
		else:
			dic['report_type'] = 'DUPLICATE FOR SUPPLIER'
			dic['report_title'] = 'DUPLICATE '+invoice_title
		return dic

	def get_primary_address(self,partner_id,self_id):
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
		gst_no = ''
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
			if location_id:
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
			if location_id:
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


	def get_first_address(self,invoice_id):
		cr = self.cr
		uid = self.uid
		invoice_obj = self.pool.get('invoice.adhoc.master')
		location_obj = self.pool.get('customer.line')
		search_id=gst_no=''
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
		if invoice_data.invoice_line_adhoc_12:
			first_data = invoice_data.invoice_line_adhoc_12[0]
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
			if phone_data:
				if phone_data.type == 'landline':
					dic['first_telephone'] = phone_data.name

				if phone_data.type == 'mobile':
					dic['first_mobile'] = phone_data.name	

			first_email = first_data.location.email if first_data.location.email else ""
			first_city = first_data.location.city_id.name1 if first_data.location.city_id.name1 else ''
			first_state = first_data.location.state_id.name if first_data.location.state_id.name else ''
			first_state_code = first_data.location.state_id.state_code if first_data.location.state_id.state_code else ''
			location_id = location_obj.search(cr,uid,[('customer_address','=',first_data.location.partner_address.id),('partner_id','=',invoice_data.partner_id.id)])
			if location_id:
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
		elif invoice_data.invoice_line_adhoc_gst:
			first_data = invoice_data.invoice_line_adhoc_gst[0]
			location_name = first_data.location_invoice.location_name if first_data.location_invoice.location_name else ''
			apartment = first_data.location_invoice.apartment if first_data.location_invoice.apartment else ''
			building = first_data.location_invoice.building if first_data.location_invoice.building else ''
			sub_area = first_data.location_invoice.sub_area if first_data.location_invoice.sub_area else ''
			street = first_data.location_invoice.street if first_data.location_invoice.street else ''
			landmark = first_data.location_invoice.landmark if first_data.location_invoice.landmark else ''
			city_id = first_data.location_invoice.city_id.name1 if first_data.location_invoice.city_id.name1 else ''
			state_id = first_data.location_invoice.state_id.name if first_data.location_invoice.state_id.name else ''
			zipc = "- " + first_data.location_invoice.zip if first_data.location_invoice.zip else ""
			first_address = [location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
			first_address = ', '.join(filter(bool,first_address))
			phone_data = first_data.location_invoice.phone_m2m_xx
			if phone_data:
				if phone_data.type == 'landline':
					dic['first_telephone'] = phone_data.name
				if phone_data.type == 'mobile':
					dic['first_mobile'] = phone_data.name	
			first_email = first_data.location_invoice.email if first_data.location_invoice.email else ''
			first_city = first_data.location_invoice.city_id.name1 if first_data.location_invoice.city_id.name1 else ''
			first_state = first_data.location_invoice.state_id.name if first_data.location_invoice.state_id.name else ''
			first_state_code = first_data.location_invoice.state_id.state_code if first_data.location_invoice.state_id.state_code else ''
			location_id = location_obj.search(cr,uid,[('customer_address','=',first_data.location_invoice.id),('partner_id','=',invoice_data.partner_id.id)])
			if location_id:
				gst_no = location_obj.browse(cr,uid,location_id[0]).gst_no
			if not gst_no:
				gst_no = invoice_data.partner_id.gst_no
				if not gst_no:
					gst_no = invoice_data.partner_id.uin_no
			dic['first_address'] = first_address
			dic['first_city'] = first_city
			dic['first_state'] = first_state
			dic['first_state_code'] = first_state_code
			dic['first_email'] = first_email
			dic['gst_no'] = gst_no
		return dic


	def get_tax_total(self,invoice_id):
		cr = self.cr
		uid = self.uid
		invoice_obj = self.pool.get('invoice.adhoc.master')
		cgst_amt = 0.00
		sgst_amt = 0.00
		igst_amt = 0.00
		cess_amt = 0.00
		gst_amt = 0.00
		dic = {
				'cgst_tax_total':'',
				'sgst_tax_total':'',
				'igst_tax_total':'',
				'cess_tax_total':'',
				'gst_tax_total':'',
				'round_off':'',
			 }
		inv_data = invoice_obj.browse(cr,uid,invoice_id)
		for inv_line in inv_data.invoice_line_adhoc_12:
			cgst_amt = cgst_amt+inv_line.cgst_amt
			sgst_amt = sgst_amt+inv_line.sgst_amt
			igst_amt = igst_amt+inv_line.igst_amt
			cess_amt = cess_amt+inv_line.cess_amt
			gst_amt = cgst_amt+sgst_amt+igst_amt+cess_amt
		for inv_line in inv_data.invoice_line_adhoc_gst:
			cgst_amt = cgst_amt+inv_line.cgst_amt
			sgst_amt = sgst_amt+inv_line.sgst_amt
			igst_amt = igst_amt+inv_line.igst_amt
			cess_amt = cess_amt+inv_line.cess_amt
			gst_amt = cgst_amt+sgst_amt+igst_amt+cess_amt
		for inv_line in inv_data.invoice_line_scrap_sale:
			cgst_amt = cgst_amt+inv_line.cgst_amt
			sgst_amt = sgst_amt+inv_line.sgst_amt
			igst_amt = igst_amt+inv_line.igst_amt
			cess_amt = cess_amt+inv_line.cess_amt
			gst_amt = cgst_amt+sgst_amt+igst_amt+cess_amt
		dic['gst_tax_total'] = format(gst_amt,'.2f')
		dic['cgst_tax_total'] = format(cgst_amt,'.2f')
		dic['sgst_tax_total'] = format(sgst_amt,'.2f')
		dic['igst_tax_total'] = format(igst_amt,'.2f')
		dic['cess_tax_total'] = format(cess_amt,'.2f')
		dic['round_off'] = format(inv_data.round_off_val,'.2f')
		return dic

	def get_service_title(self,invoice_adhoc_id):
		print"get_service_titleget_service_title-----",invoice_adhoc_id
		cr = self.cr
		uid = self.uid
		invoice_adhoc_obj = self.pool.get('invoice.adhoc')
		product_obj = self.pool.get('product.product')
		nature_obj = self.pool.get('nature.nature')
		invoice_adhoc_data = invoice_adhoc_obj.browse(cr,uid,invoice_adhoc_id)
		dic = {
				'service_title':'',
			  }
		print"invoice_adhoc_data",invoice_adhoc_data
		print"invoice_adhoc_data.pms",invoice_adhoc_data.pms
		print"invoice_adhoc_data.nature_id",invoice_adhoc_data.nature_id
		if invoice_adhoc_data.pms:
			pms_data = product_obj.browse(cr,uid,invoice_adhoc_data.pms.id)
			pms_name = pms_data.product_desc
			service_title = pms_name.upper()
		elif invoice_adhoc_data.nature_id:
			nature_data = nature_obj.browse(cr,uid,invoice_adhoc_data.nature_id.id)
			nature_name = nature_data.name
			service_title = nature_name.upper()
		dic['service_title'] = service_title
		return dic

	def get_service_address(self,services):
		cr = self.cr
		uid = self.uid
		dic = {
				'service_address':'',
			  }
		full_address = services.split('[')[1]
		service_address = '['+full_address
		dic['service_address'] = service_address
		return dic

	def get_government_notification(self,invoice_id):
		cr = self.cr
		uid = self.uid
		govt_notification = ''
		dic = {
				'govt_notification':'',
			  }
		invoice_obj = self.pool.get('invoice.adhoc.master')
		invoice_data = invoice_obj.browse(cr,uid,invoice_id)
		company_data = invoice_data.branch_id.id
		invoice_data.service_classification
		if invoice_data.service_classification == 'sez':
			if invoice_data.branch_id.government_notification:
				govt_notification = invoice_data.branch_id.government_notification
		dic['govt_notification'] = govt_notification
		return dic

report_sxw.report_sxw('report.gst_invoice_print', 'invoice.adhoc.master', '/gst_accounting/report/gst_invoice_adhoc.rml', parser=gst_invoice_adhoc_ipm_report, header="False")
