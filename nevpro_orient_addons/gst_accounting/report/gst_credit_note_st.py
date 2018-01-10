# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# Version 1.0.013 --->  changes related to Report Print for 14% 
#version 1.0.041 to remove hardcoded address,email,phoneno,website from report

import time
from report import report_sxw
from tools.translate import _
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in
from corporate_address import *

class gst_credit_note_st(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(gst_credit_note_st, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'amount_to_text_in': amount_to_text_in,
			'get_cust_addr': self.get_cust_addr,	
			'get_service_classification':self.get_service_classification,
			'get_payment':self.get_payment,
			'get_unit':self.get_unit,
			'get_corporate_address':self.get_corporate_address,
			'get_registered_office_address':self.get_registered_office_address,
			'get_branch_addr':self.get_branch_addr,
			'get_parent_branch':self.get_parent_branch,	
			'get_primary_address': self.get_primary_address,	
			'get_billing_address': self.get_billing_address,	
			'get_tax_total': self.get_tax_total,
			'get_amount_value':self.get_amount_value,
			'total_gst_val':self.total_gst_val,
			'total_gst_amt':self.total_gst_amt,	    
		})
	def get_amount_value(self,self_id,that_is,product):
		cr = self.cr
		uid = self.uid
		dic={
			'amount':0.0,
			'tax_amount_cgst':0.0,
			'tax_amount_sgst':0.0,
			'tax_amount_igst':0.0,
			'tax_amount_utgst':0.0,

		}
		for i in self.pool.get('credit.note.st').browse(cr,uid,[self_id])[0].credit_note_st_one2many:
			if i.account_id.product_id.type==that_is:
				if product:
					if str(i.account_id.name).strip()==str(product).strip():
						dic['amount']=i.debit_amount
		for i in self.pool.get('credit.note.st').browse(cr,uid,[self_id])[0].credit_note_st_one2many:
			if dic['amount']:
				if i.account_id.account_selection=='tax':
					if i.account_id.account_tax_many2one.select_tax_type=='cgst':
						dic['tax_amount_cgst']=dic['amount'] * i.account_id.account_tax_many2one.amount
					elif i.account_id.account_tax_many2one.select_tax_type=='sgst':
						dic['tax_amount_sgst']=dic['amount'] * i.account_id.account_tax_many2one.amount
					elif i.account_id.account_tax_many2one.select_tax_type=='igst':
						dic['tax_amount_igst']=dic['amount'] * i.account_id.account_tax_many2one.amount
					elif i.account_id.account_tax_many2one.select_tax_type=='utgst':
						dic['tax_amount_utgst']=dic['amount'] * i.account_id.account_tax_many2one.amount
		return dic

	def total_gst_val(self,self_id,that_is):
		cr = self.cr
		uid = self.uid
		dic={
			'amount':0.00,
			'tax_amount_cgst':0.00,
			'tax_amount_sgst':0.00,
			'tax_amount_igst':0.00,
			'tax_amount_utgst':0.00,
			'total_tax':0.00,
			'total_amount':0.00
		}
		for i in self.pool.get('credit.note.st').browse(cr,uid,[self_id])[0].credit_note_st_one2many:
			if i.account_id.product_id.type==that_is:
				dic['amount']+=i.debit_amount
			if i.account_id.account_tax_many2one.select_tax_type=='cgst' and i.account_id.account_tax_many2one.select_tax_type == that_is:
				dic['tax_amount_cgst']+=i.debit_amount
			elif i.account_id.account_tax_many2one.select_tax_type=='sgst' and i.account_id.account_tax_many2one.select_tax_type == that_is:
				dic['tax_amount_sgst']+=i.debit_amount	
			elif i.account_id.account_tax_many2one.select_tax_type=='igst' and i.account_id.account_tax_many2one.select_tax_type == that_is:
				dic['tax_amount_igst']+=i.debit_amount
			elif i.account_id.account_tax_many2one.select_tax_type=='utgst' and i.account_id.account_tax_many2one.select_tax_type == that_is:
				dic['tax_amount_utgst']+=i.debit_amount
		for i in self.pool.get('credit.note.st').browse(cr,uid,[self_id])[0].credit_note_st_one2many:
			if i.account_id.account_tax_many2one.select_tax_type in ('cgst','sgst','igst','utgst') and i.account_id.account_selection == that_is:
				dic['total_tax']+=i.debit_amount
		dic['amount']=format(round(dic['amount']),'.2f')
		dic['tax_amount_cgst']=format(round(dic['tax_amount_cgst']),'.2f')
		dic['tax_amount_sgst']=format(round(dic['tax_amount_sgst']),'.2f')
		dic['tax_amount_igst']=format(round(dic['tax_amount_igst']),'.2f')
		dic['tax_amount_utgst']=format(round(dic['tax_amount_utgst']),'.2f')
		dic['total_tax']=format(round(dic['total_tax']),'.2f')
		return dic

	def total_gst_amt(self,self_id,that_is):
		cr = self.cr
		uid = self.uid
		dic={
			'total_amount':0.00
		}
		amount=tax_vals=0.0
		for i in self.pool.get('credit.note.st').browse(cr,uid,[self_id])[0].credit_note_st_one2many:
			if i.account_id.product_id.type=='service':
				amount=i.debit_amount
			if i.account_id.account_tax_many2one.select_tax_type=='cgst':
				tax_vals+=i.debit_amount
			elif i.account_id.account_tax_many2one.select_tax_type=='sgst':
				tax_vals+=i.debit_amount
			elif i.account_id.account_tax_many2one.select_tax_type=='igst':
				tax_vals+=i.debit_amount
			elif i.account_id.account_tax_many2one.select_tax_type=='utgst':
				tax_vals+=i.debit_amount
		if that_is=='total':
			dic['total_amount']=format(round(amount+tax_vals),'.2f')
		return dic

	def get_branch_addr(self,self_id):
		return get_branch_addr(self,self_id)


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
        
        def get_unit(self,self_id,line):
		cr = self.cr
		uid = self.uid
		dic = {
		    
		    'sqrt_unit':'',
		    
		    }
		            
		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id,line]):
		    for ln in self.pool.get('invoice.adhoc').browse(cr,uid,[line]):
		            for unit in sqrt_unit:
		                    if ln.unit == unit[0] and ln.area and ln.rate:
		                           dic['sqrt_unit']=unit[1]
		                           return dic  
		                    else:
		                                         
		                           dic['sqrt_unit'] = ''
		                           return dic   
                    
        
        def get_service_classification(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = {
		        'service_name':'',
		        'stc_code':'',
		        'service_desc':'',
		        'class_service':'',
		        }
		for i in self.pool.get('credit.note').browse(cr,uid,[self_id]):
			srch=self.pool.get('credit.note.line').search(cr,uid,[('credit_id','=',i.id)])
			for i in self.pool.get('credit.note.line').browse(cr,uid,srch):		        
				if i.account_id.account_selection=='against_ref':
					srch_in=self.pool.get('invoice.adhoc.master').search(cr,uid,[('credit_invoice_id','=',i.id),('check_credit_note','=',True)])
					for rec in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch_in):

						if rec.service_classification == 'residential':
							dic['service_name'] = 'Residential Service'
							dic['stc_code'] = 'STC Code:   AABCJ9086FSD001'
							dic['service_desc'] = 'DESCRIPTION OF SERVICE:  CLEANING SERVICE'
							dic['class_service'] = ' CLASSIFICATION OF SERVICE:  65(105) (zzzd)'

						elif rec.service_classification == 'commercial':
							dic['service_name'] = 'Commercial Service'
							dic['stc_code'] = 'STC Code:   AABCJ9086FSD001'
							dic['service_desc'] = 'DESCRIPTION OF SERVICE:  CLEANING SERVICE'
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
							stc_code = ''
						       
							for iterate in rec.invoice_line_adhoc_11:				
									if iterate.location:
											for partner_address in self.pool.get('res.partner.address').browse(cr,uid,[iterate.location.partner_address.id]):

												if partner_address.exempted:
													stc_code = partner_address.certificate_no

						       		                
									
									dic['stc_code'] =  'Exempted under notification no.= '+ stc_code     
       		return dic   		

	def get_cust_addr(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = {
			'cust_addr':'',
			'cust_cont':'',
			'start':'',
			'end':'',
			'id':'',
			'branch_addr':'',
			}
		apartment = ''
		building = ''
		sub_area = ''
		street = ''
		landmark = ''
		state_id = ''
		city_id = ''
		tehsil = ''
		district = ''
		zip1 = ''
		for temp_mn in self.pool.get('credit.note').browse(cr,uid,[self_id]):
			
			search_name = self.pool.get('res.partner').search(cr,uid,[('id','=',temp_mn.customer_name.id)])
			for temp in self.pool.get('res.partner').browse(cr,uid,search_name):
				if temp:			        
						partner_id=temp.id
						apartment = temp.apartment
						building = temp.building
						sub_area = temp.sub_area
						street = temp.street
						landmark = temp.landmark
						state_id = temp.state_id.name
						city_id = temp.city_id.name1
						tehsil = temp.tehsil
						district = temp.district
						zip1 = temp.zip
						address1=[apartment,building,sub_area,street,landmark,city_id,state_id]
						addr1=', '.join(filter(bool,address1))
						dic['cust_addr'] = addr1		
						dic['branch_addr'] = get_branch_addr(self,temp_mn.branch_id.id)['branch_addr']   	
						
						
			return dic        
	
        def get_corporate_address(self):
       		return get_corporate_address(self)
    
 
        def get_registered_office_address(self):
       		return get_registered_office_address(self)


	def get_primary_address(self,partner_id):
		cr = self.cr
		uid = self.uid
		location_obj = self.pool.get('customer.line')
		partner_obj = self.pool.get('res.partner')
		search_id=''
		dic = {
				'primary_address':'',
				'primary_telephone':'',
				'primary_mobile':'',
				'primary_email':'',
				'primary_state':'',
				'primary_state_code':'' 
			 }
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
		primary_state = primary_data.customer_address.state_id.name if primary_data.customer_address.state_id.name else ''
		primary_state_code = primary_data.customer_address.state_id.state_code if primary_data.customer_address.state_id.state_code else ''
		partner_data = partner_obj.browse(cr,uid,partner_id)
		gst_no = partner_data.gst_no
		if not gst_no:
			gst_no = partner_data.uin_no
		dic['primary_address'] = primary_address
		dic['primary_email'] = primary_email
		dic['primary_state'] = primary_state
		dic['primary_state_code'] = primary_state_code
		dic['gst_no'] = gst_no
		return dic


	def get_billing_address(self,note_id):
		cr = self.cr
		uid = self.uid
		credit_note_obj = self.pool.get('credit.note.st')
		credit_note_line_obj = self.pool.get('credit.note.line.st')
		receipt_history_obj = self.pool.get('invoice.receipt.history')
		location_obj = self.pool.get('customer.line')
		dic = {
				'billing_address':'',
				'billing_telephone':'',
				'billing_mobile':'',
				'billing_email':'',
				'billing_state':'',
				'billing_state_code':'' 
			 }
		credit_data = credit_note_obj.browse(cr,uid,note_id)
		credit_note_st_line_id = credit_note_line_obj.search(cr,uid,[('credit_st_id','=',note_id),('type','=','credit')])
		receipt_history_ids = receipt_history_obj.search(cr,uid,[('credit_st_id_history','=',credit_note_st_line_id[0]),('check_invoice','=',True)])
		if len(receipt_history_ids) > 1:
			receipt_history_id = min(receipt_history_ids)
		else:
			receipt_history_id = receipt_history_ids[0]
		receipt_history_data = receipt_history_obj.browse(cr,uid,receipt_history_id)
		invoice_data = receipt_history_data.invoice_receipt_history_id
		if invoice_data.invoice_line_adhoc_12:
			inv_line_data = invoice_data.invoice_line_adhoc_12[0]
			billing_data = inv_line_data.location
			add_id = billing_data.partner_address.id
		elif invoice_data.invoice_line_adhoc_gst:
			inv_line_data = invoice_data.invoice_line_adhoc_gst[0]
			billing_data = inv_line_data.location_invoice
			add_id = billing_data.id
		location_name = billing_data.location_name if billing_data.apartment else ''
		apartment = billing_data.apartment if billing_data.apartment else ''
		building = billing_data.building if billing_data.building else ''
		sub_area = billing_data.sub_area if billing_data.sub_area else ''
		street = billing_data.street if billing_data.street else ''
		landmark = billing_data.landmark if billing_data.landmark else ''
		city_id = billing_data.city_id.name1 if billing_data.city_id.name1 else ''
		state_id = billing_data.state_id.name if billing_data.state_id.name else ''
		zipc = "- " + billing_data.zip if billing_data.zip else ""
		billing_address = [location_name,apartment,building,sub_area,street,landmark,city_id,state_id]
		billing_address = [location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
		billing_address = ', '.join(filter(bool,billing_address))
		dic['billing_telephone'] = billing_data.phone	
		billing_email = billing_data.email if billing_data.email else ""
		billing_state = billing_data.state_id.name if billing_data.state_id.name else ''
		billing_state_code = billing_data.state_id.state_code if billing_data.state_id.state_code else ''
		location_id = location_obj.search(cr,uid,[('customer_address','=',add_id),('partner_id','=',credit_data.customer_name.id)])
		loc_data = location_obj.browse(cr,uid,location_id[0])
		gst_no = loc_data.gst_no
		if not gst_no:
			gst_no = loc_data.partner_id.gst_no
			if not gst_no:
				gst_no = loc_data.partner_id.uin_no
		dic['billing_address'] = billing_address
		dic['billing_email'] = billing_email
		dic['billing_state'] = billing_state
		dic['billing_state_code'] = billing_state_code
		dic['gst_no'] = gst_no
		return dic


	def get_tax_total(self,note_id):
		cr = self.cr
		uid = self.uid
		credit_note_obj = self.pool.get('credit.note.st')
		cgst_amt = 0.00
		sgst_amt = 0.00
		igst_amt = 0.00
		cess_amt = 0.00
		gst_total_value = 0.00
		gst_taxable_value = 0.00

		actual_rate = 0.0
		actual_cgst_rate = 0.0
		actual_sgst_rate = 0.0
		actual_igst_rate = 0.0

		dic = {
				'cgst_tax_total': '0.0',
				'sgst_tax_total': '0.0',
				'igst_tax_total': '0.0',
				'cess_tax_total': '0.0',
				'gst_total_value': '0.0',
				'gst_taxable_value': '0.0',

				'actual_rate': '0.0',
				'actual_cgst_rate':'0.0',
				'actual_sgst_rate':'0.0',
				'actual_igst_rate': '0.0',
			 }

		note_data = credit_note_obj.browse(cr,uid,note_id)
		for credit_note_line in note_data.credit_note_st_one2many:
			
			if credit_note_line.type == 'credit':
				for note_history_line in credit_note_line.credit_st_id_history_one2many:
					if note_history_line.invoice_receipt_history_id.invoice_line_adhoc_12:
						for inv_line in note_history_line.invoice_receipt_history_id.invoice_line_adhoc_12:
							cgst_amt = cgst_amt + inv_line.cgst_amt 
							sgst_amt = sgst_amt + inv_line.sgst_amt 
							igst_amt = igst_amt + inv_line.igst_amt 
							cess_amt = cess_amt + inv_line.cess_amt 
							gst_total_value = gst_total_value + inv_line.total
							gst_taxable_value = gst_taxable_value + inv_line.amount
					elif note_history_line.invoice_receipt_history_id.invoice_line_adhoc_gst:
						for inv_line in note_history_line.invoice_receipt_history_id.invoice_line_adhoc_gst:
							cgst_amt = cgst_amt + inv_line.cgst_amt 
							sgst_amt = sgst_amt + inv_line.sgst_amt 
							igst_amt = igst_amt + inv_line.igst_amt 
							cess_amt = cess_amt + inv_line.cess_amt 
							gst_total_value = gst_total_value + inv_line.total
							gst_taxable_value = gst_taxable_value + inv_line.amount

			if credit_note_line.type == 'debit':
				if credit_note_line.account_id.product_id.prod_type:
					actual_rate = credit_note_line.debit_amount
				if credit_note_line.account_id.account_tax_many2one.select_tax_type=='cgst':
					actual_cgst_rate = actual_rate*credit_note_line.account_id.account_tax_many2one.amount
				if credit_note_line.account_id.account_tax_many2one.select_tax_type=='sgst':
					actual_sgst_rate = actual_rate*credit_note_line.account_id.account_tax_many2one.amount
				if credit_note_line.account_id.account_tax_many2one.select_tax_type=='igst':
					actual_igst_rate = actual_rate*credit_note_line.account_id.account_tax_many2one.amount

		dic['gst_total_value'] = format(round(gst_total_value),'.2f')
		dic['gst_taxable_value'] = format(round(gst_taxable_value),'.2f')
		dic['cgst_tax_total'] = format(round(cgst_amt),'.2f')
		dic['sgst_tax_total'] = format(round(sgst_amt),'.2f')
		dic['igst_tax_total'] = format(round(igst_amt),'.2f')
		dic['cess_tax_total'] = format(round(cess_amt),'.2f')

		dic['actual_rate'] = format(round(actual_rate),'.2f')
		dic['actual_cgst_rate'] = format(round(actual_cgst_rate),'.2f')
		dic['actual_sgst_rate'] = format(round(actual_sgst_rate),'.2f')
		dic['actual_igst_rate'] = format(round(actual_igst_rate),'.2f')
		return dic


	def get_tax_total_old(self,note_id):
		cr = self.cr
		uid = self.uid
		credit_note_obj = self.pool.get('credit.note.st')
		total_amt = 0.00
		taxable_amt = 0.00
		cgst_amt = 0.00
		sgst_amt = 0.00
		igst_amt = 0.00
		cess_amt = 0.00
		actual_rate = 0.0
		actual_cgst_rate = 0.0
		actual_sgst_rate = 0.0
		actual_igst_rate = 0.0
		dic = {
				'actual_rate': '0.0',
				'actual_cgst_rate':'0.0',
				'actual_sgst_rate':'0.0',
				'actual_igst_rate': '0.0',
				'gst_total_value': '0.0',
				'gst_taxable_value': '0.0',
				'cgst_tax_total': '0.0',
				'sgst_tax_total': '0.0',
				'igst_tax_total': '0.0',
				'cess_tax_total': '0.0',
			 }
		note_data = credit_note_obj.browse(cr,uid,note_id)
		for credit_note_line in note_data.credit_note_st_one2many:
			if credit_note_line.type == 'credit':
				for note_history_line in credit_note_line.credit_st_id_history_one2many:
					if note_history_line.invoice_receipt_history_id.invoice_line_adhoc_12:
						for inv_line in note_history_line.invoice_receipt_history_id.invoice_line_adhoc_12:
							cgst_amt = cgst_amt+inv_line.cgst_amt 
							sgst_amt = sgst_amt+inv_line.sgst_amt 
							igst_amt = igst_amt+inv_line.igst_amt 
							cess_amt = cess_amt+inv_line.cess_amt 
							total_amt = total_amt+inv_line.total
							taxable_amt = taxable_amt+inv_line.amount
					elif note_history_line.invoice_receipt_history_id.invoice_line_adhoc_gst:
						for inv_line in note_history_line.invoice_receipt_history_id.invoice_line_adhoc_gst:
							cgst_amt = cgst_amt+inv_line.cgst_amt 
							sgst_amt = sgst_amt+inv_line.sgst_amt 
							igst_amt = igst_amt+inv_line.igst_amt 
							cess_amt = cess_amt+inv_line.cess_amt 
							total_amt = total_amt+inv_line.total
							taxable_amt = taxable_amt+inv_line.amount
			if credit_note_line.type == 'debit':
				if credit_note_line.account_id.product_id.prod_type:
					actual_rate = credit_note_line.debit_amount
				if credit_note_line.account_id.account_tax_many2one.select_tax_type=='cgst':
					actual_cgst_rate = actual_rate*credit_note_line.account_id.account_tax_many2one.amount
				if credit_note_line.account_id.account_tax_many2one.select_tax_type=='sgst':
					actual_sgst_rate = actual_rate*credit_note_line.account_id.account_tax_many2one.amount
				if credit_note_line.account_id.account_tax_many2one.select_tax_type=='igst':
					actual_igst_rate = actual_rate*credit_note_line.account_id.account_tax_many2one.amount
		dic['actual_rate'] = format(round(actual_rate),'.2f')
		dic['actual_cgst_rate'] = format(round(actual_cgst_rate),'.2f')
		dic['actual_sgst_rate'] = format(round(actual_sgst_rate),'.2f')
		dic['actual_igst_rate'] = format(round(actual_igst_rate),'.2f')
		dic['gst_total_value'] = format(round(actual_rate),'.2f')
		dic['gst_taxable_value'] = format(round(actual_rate),'.2f')
		dic['cgst_tax_total'] = format(round(actual_cgst_rate),'.2f')
		dic['sgst_tax_total'] = format(round(actual_sgst_rate),'.2f')
		dic['igst_tax_total'] = format(round(actual_igst_rate),'.2f')
		dic['cess_tax_total'] = format(round(cess_amt),'.2f')
		return dic


report_sxw.report_sxw('report.gst_credit_note_st', 'credit.note.st', '/gst_accounting/report/gst_credit_note_st.rml', parser=gst_credit_note_st, header="False")
