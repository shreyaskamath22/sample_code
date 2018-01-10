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

from osv import osv,fields
import time
import decimal_precision as dp
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from urllib import urlopen
import math
import calendar
import datetime as dt
import xmlrpclib
from python_code.dateconversion import *
import python_code.dateconversion as py_date
import re
from lxml import etree
import time
import os
from openerp.osv.orm import setup_modifiers


class inspection_costing_line(osv.osv):
	_inherit = 'inspection.costing.line'
	_columns = {
		'services':fields.text('Services',size=1000),
		'hsn_code':fields.char('HSN Code',size=8),
		'discount':fields.float('Discount'),
		'taxable_value':fields.float('Taxable Value'),
		'cgst_rate':fields.char('CGST Rt',size=10),
		'cgst_amt':fields.float('CGST Amt',size=10),
		'sgst_rate':fields.char('SGST Rt',size=10),
		'sgst_amt':fields.float('SGST Amt',size=10),
		'igst_rate':fields.char('IGST Rt',size=10),
		'igst_amt':fields.float('IGST Amt',size=10),	
		'cess_rate':fields.char('CESS Rt',size=10),
		'cess_amt':fields.float('CESS Amt',size=10),
		'contract_id12':fields.many2one('sale.contract','contract_id'),
		'nature_id':fields.many2one('nature.nature','Nature'),
		'nature':fields.boolean('Nature?')
	}

	def onchange_nature_id(self, cr, uid, ids, nature_id, context=None):
		if context is None: 
			context = {}
		vals = {}
		nature_obj = self.pool.get('nature.nature')
		ins_cosline_data = self.browse(cr,uid,ids[0])
		if ins_cosline_data.hsn_code:
			hsn_code = ins_cosline_data.hsn_code
		else:
			hsn_code = None
		if nature_id:
			nature_data = nature_obj.browse(cr,uid,nature_id)
			hsn_code = nature_data.hsn_code
			vals['hsn_code'] = hsn_code
		else:
			vals['hsn_code'] = hsn_code
		return {'value': vals}

inspection_costing_line()

class inspection_costing(osv.osv):
	_inherit='inspection.costing'


	def create_quotation(self,cr,uid,ids,context=None):
		if context is None: context = {}
		quotation_id =[]
		for rec in self.browse(cr,uid,ids):
			if rec.inspection_line:
				for pr in rec.inspection_line:
					res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
					if res_users_browse:
						res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key	
					# if str(res_company_pcof) != 'P200' or str(res_company_pcof) != 'P371':	
					if str(res_company_pcof) not in ('P200','P371') and not rec.partner_id.igst_check:
						if pr.address_new.state_id.id!=rec.company_id.state_id.id:
							raise osv.except_osv(('Alert!'),('IGST Quotation cannot be created as of now!'))
					if pr.pms:
						product_srch = self.pool.get('product.product').search(cr,uid,[('id','=',pr.pms.id)])
						if product_srch:
							for product in self.pool.get('product.product').browse(cr,uid,product_srch):
								prod_type = product.prod_type
								if prod_type == 'fum':
									raise osv.except_osv(('Alert!'),('You can not create Inspection Costing for FUM!'))
			if rec.state != 'costing_updated':
				raise osv.except_osv(('Alert !'),('You Can Not Proceed before updating the cost'))
			if rec.state == 'costing_updated':
				if not rec.inspection_line:	
					raise osv.except_osv(('Warning !'),('You Can Not Process without Service'))
				customer_quotation=''
				date1=''
				date1=str(datetime.now().date())
				conv=time.strptime(str(date1),"%Y-%m-%d")
				date1 = time.strftime("%d-%m-%Y",conv)
				customer_quotation=rec.customer_name+'   Quotation  Created On    '+date1
				customer_lead_date=self.pool.get('customer.logs').create(cr,uid,{'customer_join':customer_quotation,'customer_id':rec.partner_id.id})
			
				
				if rec.inspection_line:
						name="Inspection"
						search_id = self.pool.get('inspection.costing.line').search(cr,uid,[('inspection_line_id','=',rec.id)])
						if len(search_id) == 1:
							return_dict= self.direct_entry(cr,uid,rec.id,context=None)
							return return_dict
							
						line_id = self.pool.get("inspection.wizard").create(cr, uid, {'inspection_id':rec.id,'lead_no':rec.lead_no,'sequence_id':rec.sequence_id})
					
						for k in rec.inspection_line:
							quotation_id = self.pool.get('sale.quotation').search(cr,uid,[('sequence_id','=',rec.sequence_id),('state','!=','quoted')])
							if k.box_inspection == False:
									self.pool.get("inspection.wizard.line").create(cr, uid, {'inspection_wizard_line_id':line_id,'address_new':k.address_new.id,'pms':k.pms.id},context=None)
						if quotation_id:
							for res in rec.inspection_line:
								search_id = self.pool.get('product.product').search(cr,uid,[('id','=',res.pms.id)])
								if search_id:
									for r in  self.pool.get('product.product').browse(cr,uid,search_id):
										for temp in rec.inspection_line:

											if r.name_template=="TSPR" :
												cr.execute("update sale_quotation set check_specification=%s,quotation_no =%s  where id=%s",(True,rec.sequence_id))
							for res_in in self.pool.get('sale.quotation').browse(cr,uid,quotation_id):
								for temp_id in res_in.quotation_line_id:
									if temp_id.address_new.id == k.address_new.id and k.box_inspection == False:
										self.pool.get("inspection.wizard.line").create(cr, uid, {'inspection_wizard_line_id':line_id,'address_new':k.address_new.id,'pms':res.pms.id},context=None)
									# else:
									# 	if k.box_inspection == False:
									# 		self.pool.get("inspection.wizard.line").create(cr, uid, {'inspection_wizard_line_id':line_id,'address_new':k.address_new.id,'pms':k.pms.id},context=None)
						# else:
											# if k.box_inspection == False:
											# 		print "sdasdasdsadadsad"
											# 		self.pool.get("inspection.wizard.line").create(cr, uid, {'inspection_wizard_line_id':line_id,'address_new':k.address_new.id,'pms':k.pms.id},context=None)

				return {
				       'name':'Choose a Location for Quotation',
				       'view_mode': 'form',
				       'view_id': False,
				       'view_type': 'form',
				       'res_model': 'inspection.wizard',
				       'res_id':line_id,
				       'type': 'ir.actions.act_window',
				       'target': 'new',
				       'domain': '[]',
				       'context': context,
				     }


inspection_costing()

class sale_quotation(osv.osv):
	_inherit = 'sale.quotation'


	#######process tax claculation
	def recr_amount(self,obj,value,date):
		if not obj.parent_id:
			return obj.amount*value
		else:
			if obj.parent_id.effective_from_date <= date and obj.parent_id.effective_to_date > date:
				return obj.amount*self.recr_amount(obj.parent_id,value,date)	
		return 0

	def add_process_normal_tax(self,cr,uid,model_id,model):
		val1=0
		qry=if_present=False
		tax_ids=[]
		todays_date=datetime.now().date().strftime("%Y-%m-%d")
		contract_end_date=contract_date=''
		model_id=model_id if isinstance(model_id,(int,long)) else model_id[0]
		for order in self.pool.get('sale.contract').browse(cr,uid,[model_id]):
			if order.exempted != True:
				for line in order.contract_line_id12:
						val1 += line.amount
				total_amount = round(val1)
				total_amount = round(order.basic_amount)
				
				sale_ids=self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',order.contract_number)])

				for k in self.pool.get('sale.contract').browse(cr,uid,sale_ids):
					
					if k.contract_end_date:
						contract_end_date=(datetime.strptime(k.contract_end_date,'%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')
					compare_date=contract_end_date if contract_end_date > todays_date else todays_date
					tax_ids= self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',compare_date),('effective_to_date','>',compare_date),('description','=','gst'),('select_tax_type','in',('sgst','cgst'))])
					GST_val=self.pool.get('account.account').search(cr,uid,[('name','=','GST')])
				for i in self.pool.get('account.tax').browse(cr,uid,tax_ids):
					
					current_tax_amount=self.recr_amount(i,total_amount,compare_date)
					cr.execute("select account_tax_id from tax where sale_contract_id=%s and account_tax_id=%s" %(str(model_id),str(i.id)))
					if_present=cr.fetchall()
					if current_tax_amount>0:
						if not if_present:
							insert_qry='insert into tax(name,amount,sale_contract_id,account_tax_id)values(%s,%s,%s,%s)' %("'"+str(i.name)+"'",str(current_tax_amount),str(model_id),str(i.id))
							cr.execute(insert_qry)

				cr.execute('delete from tax where sale_contract_id=%s and account_tax_id != %s',(model_id,tax_ids[0]))
				cr.commit()
						
		return True


	def add_contract_tax(self,cr,uid,model_id,model):
		val1=0
		qry=if_present=False
		tax_ids=[]
		todays_date=datetime.now().date().strftime("%Y-%m-%d")
		contract_end_date=contract_date=''
		model_id=model_id if isinstance(model_id,(int,long)) else model_id[0]
		for order in self.pool.get('sale.contract').browse(cr,uid,[model_id]):
			if order.exempted != True:
				for line in order.contract_line_id12:
						val1 += line.amount
				total_amount = round(val1)
				total_amount = round(order.basic_amount)
				
				sale_ids=self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',order.contract_number)])

				for k in self.pool.get('sale.contract').browse(cr,uid,sale_ids):
					
					if k.contract_end_date:
						contract_end_date=(datetime.strptime(k.contract_end_date,'%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')
					compare_date=contract_end_date if contract_end_date > todays_date else todays_date
					tax_ids= self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',compare_date),('effective_to_date','>',compare_date),('description','=','gst'),('select_tax_type','=','igst')])
					GST_val=self.pool.get('account.account').search(cr,uid,[('name','=','GST')])
				for i in self.pool.get('account.tax').browse(cr,uid,tax_ids):
					
					current_tax_amount=self.recr_amount(i,total_amount,compare_date)
					cr.execute("select account_tax_id from tax where sale_contract_id=%s and account_tax_id=%s" %(str(model_id),str(i.id)))
					if_present=cr.fetchall()
					if current_tax_amount>0:
						if not if_present:
							insert_qry='insert into tax(name,amount,sale_contract_id,account_tax_id)values(%s,%s,%s,%s)' %("'"+str(i.name)+"'",str(current_tax_amount),str(model_id),str(i.id))
							cr.execute(insert_qry)

				# cr.execute('delete from tax where sale_contract_id=%s and account_tax_id != %s',(model_id,tax_ids[0]))
				# cr.commit()
						
		return True



	def normal_create_contract(self,cr,uid,ids,context=None):
		cgst_rate = '0.0%'
		cgst_amt = 0.0
		sgst_rate = '0.0%'
		sgst_amt = 0.0
		igst_rate = '0.0%'
		igst_amt = 0.0
		cess_rate = '0.0%'
		cess_amt = 0.0
		total_tax_amt=0.0
		account_tax_obj = self.pool.get('account.tax')
		today_date = datetime.now().date()
		gst_select_taxes = ['cgst','sgst']
		gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
		if not gst_taxes:
			raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
		for res in self.browse(cr,uid,ids):
			if res.quotation_line_id:
				for pr in res.quotation_line_id:
					res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
					if res_users_browse:
						res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key	
					if str(res_company_pcof) not in ('P200','P371') and not res.partner_id.igst_check:
						if pr.address_new.state_id.id!=res.company_id.state_id.id:
							raise osv.except_osv(('Alert!'),('IGST Contract cannot be created as of now!'))
			if res.state != 'contracted':
				value_id = self.pool.get('sale.contract').create(cr,uid,
					{
						'gst_contract': True,
						'lead_no':res.lead_no,
						'service_classification':'exempted' if res.exempted else '',
						'cse':res.cse.id,
						'quotation_number':res.quotation_number,
						'cust_name':res.partner_id.name,
						'inquiry_type':'Service',
						'exempted':res.exempted,
						'adhoc_invoice':res.adhoc_invoice,
						'branch_id':res.company_id.id,
						'partner_id':res.partner_id.id,
						'payment_term':res.pay_term,
						'add_custom_payterm':res.add_custom_payterm if res.add_custom_payterm else '',
						'bool_custom_payterm':res.bool_custom_payterm,
						'service_classification':'sez'
					})
				context.update({'value_id':value_id})
				for temp in res.quotation_line_id:
					address_data = temp.address_new
					addrs_items = []
					long_address = ''
					if address_data.apartment not in [' ',False,None]:
						addrs_items.append(address_data.apartment)
					if address_data.location_name not in [' ',False,None]:
						addrs_items.append(address_data.location_name)
					if address_data.building not in [' ',False,None]:
						addrs_items.append(address_data.building)
					if address_data.sub_area not in [' ',False,None]:
						addrs_items.append(address_data.sub_area)
					if address_data.street not in [' ',False,None]:
						addrs_items.append(address_data.street)
					if address_data.landmark not in [' ',False,None]:
						addrs_items.append(address_data.landmark)
					if address_data.city_id:
						addrs_items.append(address_data.city_id.name1)
					if address_data.district:
						addrs_items.append(address_data.district.name)
					if address_data.tehsil:
						addrs_items.append(address_data.tehsil.name)
					if address_data.state_id:
						addrs_items.append(address_data.state_id.name)
					if address_data.zip not in [' ',False,None]:
						addrs_items.append(address_data.zip)
					if len(addrs_items) > 0:
						last_item = addrs_items[-1]
						for item in addrs_items:
							if item!=last_item:
								long_address = long_address+item+','+' '
							if item==last_item:
								long_address = long_address+item
					if long_address:
						complete_address = '['+long_address+']'
					else:
						complete_address = ' '
					product_full_name = temp.pms.product_desc or ''
					services = product_full_name.upper() + ' '+complete_address
					cust_line_obj =  self.pool.get('customer.line')
					cust_line_srch = cust_line_obj.search(cr,uid,[('customer_address','=',temp.address_new.partner_address.id)])
					cse =''
					if cust_line_srch:
						cse = cust_line_obj.browse(cr,uid,cust_line_srch[0]).cse.id	
					if temp.pms.prod_type=='ipm':
						self.write(cr,uid,ids,{'is_ipm':True})
						self.pool.get('sale.contract').write(cr,uid,value_id,{'is_ipm':res.is_ipm})
						cr.commit()
					self.pool.get('sale.contract').write(cr,uid,value_id,{'pms':temp.pms.id,'cse':cse if cse else res.cse.id})
					cr.commit()
					cse_contract=temp.address_new.partner_address.cse.id if temp.address_new.partner_address.cse else temp.cse_quotation.id
					if res.partner_id.nature == True:
						nature = True
					else:
						nature = False
					self.pool.get('inspection.costing.line').write(cr,uid,temp.id, 
						{
							'contract_id1':value_id,
							'contract_id12':value_id,
							'revised_quotation':False,
							'revised_contract':False,
							'cse_contract':cse_contract,
							'taxable_value': temp.amount,
							'services':services,
							'nature':nature
						})
					new_address_data = temp.address_new
					cont_data = self.browse(cr,uid,ids[0])
					# if cont_data.service_classification != 'exempted':
					if not res.company_id.state_id or not new_address_data.state_id:
						raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
					# if 'cgst' in select_tax_type:
					# 	# cgst calculation
					# 	cgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cgst')])
					# 	cgst_data = account_tax_obj.browse(cr,uid,cgst_id[0])
					# 	if cgst_data.effective_from_date and cgst_data.effective_to_date:
					# 		if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
					# 			cgst_percent = cgst_data.amount * 100
					# 			cgst_rate = str(cgst_percent)+'%'
					# 			cgst_amt = round((temp.estimated_contract_cost*cgst_percent)/100,2)
					# 	else:
					# 		raise osv.except_osv(('Alert'),("CGST tax not configured!"))
					# if 'sgst' in select_tax_type:
					# 		sgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','sgst')])
					# 		st_data = account_tax_obj.browse(cr,uid,sgst_id[0])
					# 		if st_data.effective_from_date and st_data.effective_to_date:
					# 			if str(today_date) >= st_data.effective_from_date and str(today_date) <= st_data.effective_to_date:
					# 				sgst_percent = st_data.amount * 100
					# 				sgst_rate = str(sgst_percent)+'%'
					# 				sgst_amt = round((temp.estimated_contract_cost*sgst_percent)/100,2)
					# 		else:
					# 			raise osv.except_osv(('Alert'),("SGST tax not configured!"))
					self.pool.get('inspection.costing.line').write(cr,uid,temp.id,
						{
							'cgst_rate': cgst_rate,
							'cgst_amt': cgst_amt,
							'sgst_rate': sgst_rate,
							'sgst_amt': sgst_amt,
							'igst_rate': igst_rate,
							'igst_amt': igst_amt,
							'cess_rate': cess_rate,
							'cess_amt': cess_amt,
						})
					# total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
				# self.pool.get('tax').add_tax(cr,uid,value_id,'sale.contract')
				self.add_process_normal_tax(cr,uid,value_id,'sale.contract')
				if value_id:
					for sc in self.pool.get('sale.contract').browse(cr,uid,[value_id]):
						if sc.tax_one2many:
							for amt in sc.tax_one2many:
								total_tax_amt+=amt.amount
					self.pool.get('sale.contract').write(cr,uid,value_id,{'total_tax_amt':total_tax_amt})
				for iterate in res.comment_line_o2m:
					date=datetime.now()
					self.pool.get('comment.line').create(cr,uid,
						{
							'contract_line_id':value_id,
							'user_name':self.pool.get('res.users').browse(cr,uid,uid).name,
							'comment_date':iterate.comment_date,
							'comment':iterate.comment
						})
				self.write(cr,uid,ids,{'comment_remark':None})
			else:
				raise osv.except_osv(('Warning!'),('You cannot create Contracted Entry'))
			self.write(cr,uid,res.id,{'contract_created':True})
		return True


	def create_igst_contract(self,cr,uid,ids,context=None):
		cgst_rate = '0.0%'
		cgst_amt = 0.0
		sgst_rate = '0.0%'
		sgst_amt = 0.0
		igst_rate = '0.0%'
		igst_amt = 0.0
		cess_rate = '0.0%'
		cess_amt = 0.0
		total_tax_amt=0.0
		account_tax_obj = self.pool.get('account.tax')
		today_date = datetime.now().date()
		gst_select_taxes = ['igst']
		gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
		if not gst_taxes:
			raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
		for res in self.browse(cr,uid,ids):
				if res.quotation_line_id:
					for pr in res.quotation_line_id:
						res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
						if res_users_browse:
							res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key	
						if str(res_company_pcof) not in ('P200','P371') and not res.partner_id.igst_check:
							if pr.address_new.state_id.id!=res.company_id.state_id.id:
								raise osv.except_osv(('Alert!'),('IGST Contract cannot be created as of now!'))
				if res.state != 'contracted':
					value_id = self.pool.get('sale.contract').create(cr,uid,
						{
							'gst_contract': True,
							'lead_no':res.lead_no,
							'service_classification':'exempted' if res.exempted else '',
							'cse':res.cse.id,
							'quotation_number':res.quotation_number,
							'cust_name':res.partner_id.name,
							'inquiry_type':'Service',
							'exempted':res.exempted,
							'adhoc_invoice':res.adhoc_invoice,
							'branch_id':res.company_id.id,
							'partner_id':res.partner_id.id,
							'payment_term':res.pay_term,
							'add_custom_payterm':res.add_custom_payterm if res.add_custom_payterm else '',
							'bool_custom_payterm':res.bool_custom_payterm,
							'service_classification':'sez'
						})
					context.update({'value_id':value_id})
					for temp in res.quotation_line_id:
						address_data = temp.address_new
						addrs_items = []
						long_address = ''	
						if address_data.apartment not in [' ',False,None]:
							addrs_items.append(address_data.apartment)
						if address_data.location_name not in [' ',False,None]:
							addrs_items.append(address_data.location_name)
						if address_data.building not in [' ',False,None]:
							addrs_items.append(address_data.building)
						if address_data.sub_area not in [' ',False,None]:
							addrs_items.append(address_data.sub_area)
						if address_data.street not in [' ',False,None]:
							addrs_items.append(address_data.street)
						if address_data.landmark not in [' ',False,None]:
							addrs_items.append(address_data.landmark)
						if address_data.city_id:
							addrs_items.append(address_data.city_id.name1)
						if address_data.district:
							addrs_items.append(address_data.district.name)
						if address_data.tehsil:
							addrs_items.append(address_data.tehsil.name)
						if address_data.state_id:
							addrs_items.append(address_data.state_id.name)
						if address_data.zip not in [' ',False,None]:
							addrs_items.append(address_data.zip)
						if len(addrs_items) > 0:
							last_item = addrs_items[-1]
							for item in addrs_items:
								if item!=last_item:
									long_address = long_address+item+','+' '
								if item==last_item:
									long_address = long_address+item
						if long_address:
							complete_address = '['+long_address+']'
						else:
							complete_address = ' '
						product_full_name = temp.pms.product_desc or ''
						services = product_full_name.upper() + ' '+complete_address
						cust_line_obj =  self.pool.get('customer.line')
						cust_line_srch = cust_line_obj.search(cr,uid,[('customer_address','=',temp.address_new.partner_address.id)])
						cse =''
						if cust_line_srch:
							cse = cust_line_obj.browse(cr,uid,cust_line_srch[0]).cse.id			
						if temp.pms.prod_type=='ipm':
							self.write(cr,uid,ids,{'is_ipm':True})
							self.pool.get('sale.contract').write(cr,uid,value_id,{'is_ipm':res.is_ipm})
							cr.commit()
						self.pool.get('sale.contract').write(cr,uid,value_id,{'pms':temp.pms.id,'cse':cse if cse else res.cse.id})
						cr.commit()
						cse_contract=temp.address_new.partner_address.cse.id if temp.address_new.partner_address.cse else temp.cse_quotation.id
						if res.partner_id.nature == True:
							nature = True
						else:
							nature = False
						self.pool.get('inspection.costing.line').write(cr,uid,temp.id, 
							{
								'contract_id1':value_id,
								'contract_id12':value_id,
								'revised_quotation':False,
								'revised_contract':False,
								'cse_contract':cse_contract,
								'taxable_value': temp.amount,
								'services':services,
								'nature':nature
							})
						new_address_data = temp.address_new
						cont_data = self.browse(cr,uid,ids[0])
						# if cont_data.service_classification != 'exempted':
						if not res.company_id.state_id or not new_address_data.state_id:
							raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
						else:
							igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
							igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
							if igst_data.effective_from_date and igst_data.effective_to_date:
								if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
									igst_percent = igst_data.amount * 100
									igst_rate = str(igst_percent)+'%'
									igst_amt = round((temp.estimated_contract_cost*igst_percent)/100,2)
							else:
								raise osv.except_osv(('Alert'),("IGST tax not configured!"))
						self.pool.get('inspection.costing.line').write(cr,uid,temp.id,
							{
								'cgst_rate': cgst_rate,
								'cgst_amt': cgst_amt,
								'sgst_rate': sgst_rate,
								'sgst_amt': sgst_amt,
								'igst_rate': igst_rate,
								'igst_amt': igst_amt,
								'cess_rate': cess_rate,
								'cess_amt': cess_amt,
							})
						# total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
					# self.pool.get('tax').add_tax(cr,uid,value_id,'sale.contract')
					self.add_contract_tax(cr,uid,value_id,'sale.contract')
					if value_id:
						for sc in self.pool.get('sale.contract').browse(cr,uid,[value_id]):
							if sc.tax_one2many:
								for amt in sc.tax_one2many:
									total_tax_amt+=amt.amount
						self.pool.get('sale.contract').write(cr,uid,value_id,{'total_tax_amt':total_tax_amt})
					for iterate in res.comment_line_o2m:
						date=datetime.now()
						self.pool.get('comment.line').create(cr,uid,
							{
								'contract_line_id':value_id,
								'user_name':self.pool.get('res.users').browse(cr,uid,uid).name,
								'comment_date':iterate.comment_date,
								'comment':iterate.comment
							})
					self.write(cr,uid,ids,{'comment_remark':None})
				else:
					raise osv.except_osv(('Warning!'),('You cannot create Contracted Entry'))
				self.write(cr,uid,res.id,{'contract_created':True})
		return True

	def create_contract(self,cr,uid,ids,context=None):
		cgst_rate = '0.0%'
		cgst_amt = 0.0
		sgst_rate = '0.0%'
		sgst_amt = 0.0
		igst_rate = '0.0%'
		igst_amt = 0.0
		cess_rate = '0.0%'
		cess_amt = 0.0
		total_tax_amt=0.0
		service_classification_list = []
		partner_address_list =[]
		special_status_list = []
		lot_bond_list = []
		res_company_obj =self.pool.get('res.company')
		account_tax_obj = self.pool.get('account.tax')
		inspection_costing_line_obj = self.pool.get('inspection.costing.line')
		new_address_obj = self.pool.get('new.address')
		res_partner_address_obj = self.pool.get('res.partner.address')
		today_date = datetime.now().date()
		########## Create Contract
		search = self.browse(cr,uid,ids[0])
		main_id = search.id
		search_inspection_line_id = self.pool.get('inspection.costing.line').search(cr,uid,[('quotation_id1','=',main_id)])
		browse_inspection_line_id = self.pool.get('inspection.costing.line').browse(cr,uid,search_inspection_line_id)
		for browse_location_id in browse_inspection_line_id:
			location_id = browse_location_id.address_new.id
			partner_address = new_address_obj.browse(cr,uid,location_id).partner_address.id
			lot_bond = res_partner_address_obj.browse(cr,uid,partner_address).lot_bond
			lot_bond_list.append(lot_bond)
			partner_address_list.append(partner_address)
			if len(partner_address_list) == 1:
				query_str = "select distinct(special_status) from res_partner_address where id="+str(partner_address_list[0])
				cr.execute(query_str)
			elif len(partner_address_list) > 1:
				query_str_tuple = "select distinct(special_status) from res_partner_address where id in "+str(tuple(partner_address_list))
				cr.execute(query_str_tuple)
			values = cr.fetchall()
			values_id = [x[0] for x in values]
			if len(values_id) > 1:
				for values_browse_id in values_id:
					if values_browse_id != None:
						browse_special_status = self.pool.get('special.status').browse(cr,uid,values_browse_id).name
						special_status_list.append(str(browse_special_status))
					if values_browse_id == None:
						special_status_list.append(None)
				if 'SEZ' in special_status_list and None in special_status_list:
					raise osv.except_osv(('Warning !'),('All Locations must have special status as SEZ in customer location'))
			if len(values_id) == 1:
				for values_browse_id in values_id:
					if values_browse_id != None:
						browse_special_status = self.pool.get('special.status').browse(cr,uid,values_browse_id).name
						special_status_list.append(str(browse_special_status))
				if 'SEZ' in special_status_list:
					lot_bond_list = list(set(lot_bond_list))
					if len(lot_bond_list) > 1:
						raise osv.except_osv(('Warning !'),('Please Tick or Untick the lot bond for all the SEZ customer location'))
		for o in self.pool.get('sale.quotation').browse(cr,uid,ids):
			company_id = o.company_id.id
			for location in o.quotation_line_id:
				location_id = location.address_new.id
				partner_address = new_address_obj.browse(cr,uid,location_id).partner_address.id
				print "ppppppppppppp",partner_address
				service_classification = res_partner_address_obj.browse(cr,uid,partner_address).special_status.name
				if company_id:
					branch_id_name = res_company_obj.browse(cr,uid,company_id).government_notification
					branch_id_str = branch_id_name
		####################################################################
		gst_select_taxes = ['cgst','sgst','utgst','igst','cess']
		gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
		if not gst_taxes:
			raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
		for res in self.browse(cr,uid,ids):
			search_quotation_line = inspection_costing_line_obj.search(cr,uid,[('quotation_id1','=',res.id)])
			browse_quotation_line = inspection_costing_line_obj.browse(cr,uid,search_quotation_line)
			for search_quotation_id in browse_quotation_line:
				address_new_id =search_quotation_id.address_new.id
				search_new_address = new_address_obj.search(cr,uid,[('id','=',address_new_id)])
				browse_new_address = new_address_obj.browse(cr,uid,search_new_address[0]).partner_address.id
				lot_bond = res_partner_address_obj.browse(cr,uid,browse_new_address).lot_bond
			# if not res.sez_quotation:
			if service_classification != 'SEZ' or service_classification == None:
					if res.quotation_line_id:
						for pr in res.quotation_line_id:
							res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
							if res_users_browse:
								res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key	
							if str(res_company_pcof) not in ('P200','P371') and not res.partner_id.igst_check:
								if pr.address_new.state_id.id!=res.company_id.state_id.id:
									raise osv.except_osv(('Alert!'),('IGST Contract cannot be created as of now!'))
					if res.state != 'contracted':
						value_id = self.pool.get('sale.contract').create(cr,uid,
							{
								'gst_contract': True,
								'lead_no':res.lead_no,
								'service_classification':'exempted' if res.exempted else '',
								'cse':res.cse.id,
								'quotation_number':res.quotation_number,
								'cust_name':res.partner_id.name,
								'inquiry_type':'Service',
								'exempted':res.exempted,
								'adhoc_invoice':res.adhoc_invoice,
								'branch_id':res.company_id.id,
								'partner_id':res.partner_id.id,
								'payment_term':res.pay_term,
								'add_custom_payterm':res.add_custom_payterm if res.add_custom_payterm else '',
								'bool_custom_payterm':res.bool_custom_payterm
							})
						for temp in res.quotation_line_id:
							address_data = temp.address_new
							addrs_items = []
							long_address = ''	
							if address_data.apartment not in [' ',False,None]:
								addrs_items.append(address_data.apartment)
							if address_data.location_name not in [' ',False,None]:
								addrs_items.append(address_data.location_name)
							if address_data.building not in [' ',False,None]:
								addrs_items.append(address_data.building)
							if address_data.sub_area not in [' ',False,None]:
								addrs_items.append(address_data.sub_area)
							if address_data.street not in [' ',False,None]:
								addrs_items.append(address_data.street)
							if address_data.landmark not in [' ',False,None]:
								addrs_items.append(address_data.landmark)
							if address_data.city_id:
								addrs_items.append(address_data.city_id.name1)
							if address_data.district:
								addrs_items.append(address_data.district.name)
							if address_data.tehsil:
								addrs_items.append(address_data.tehsil.name)
							if address_data.state_id:
								addrs_items.append(address_data.state_id.name)
							if address_data.zip not in [' ',False,None]:
								addrs_items.append(address_data.zip)
							if len(addrs_items) > 0:
								last_item = addrs_items[-1]
								for item in addrs_items:
									if item!=last_item:
										long_address = long_address+item+','+' '
									if item==last_item:
										long_address = long_address+item
							if long_address:
								complete_address = '['+long_address+']'
							else:
								complete_address = ' '
							product_full_name = temp.pms.product_desc or ''
							services = product_full_name.upper() + ' '+complete_address
							cust_line_obj =  self.pool.get('customer.line')
							cust_line_srch = cust_line_obj.search(cr,uid,[('customer_address','=',temp.address_new.partner_address.id)])
							cse =''
							if cust_line_srch:
								cse = cust_line_obj.browse(cr,uid,cust_line_srch[0]).cse.id			
							if temp.pms.prod_type=='ipm':
								self.write(cr,uid,ids,{'is_ipm':True})
								self.pool.get('sale.contract').write(cr,uid,value_id,{'is_ipm':res.is_ipm})
								cr.commit()
							self.pool.get('sale.contract').write(cr,uid,value_id,{'pms':temp.pms.id,'cse':cse if cse else res.cse.id})
							cr.commit()
							cse_contract=temp.address_new.partner_address.cse.id if temp.address_new.partner_address.cse else temp.cse_quotation.id
							if res.partner_id.nature == True:
								nature = True
							else:
								nature = False
							self.pool.get('inspection.costing.line').write(cr,uid,temp.id, 
								{
									'contract_id1':value_id,
									'contract_id12':value_id,
									'revised_quotation':False,
									'revised_contract':False,
									'cse_contract':cse_contract,
									'taxable_value': temp.amount,
									'services':services,
									'nature': nature
								})
							new_address_data = temp.address_new
							cont_data = self.browse(cr,uid,ids[0])
							# if cont_data.service_classification != 'exempted':
							if not res.company_id.state_id or not new_address_data.state_id:
								raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
							if res.company_id.state_id.id == new_address_data.state_id.id:
								# cgst calculation
								cgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cgst')])
								cgst_data = account_tax_obj.browse(cr,uid,cgst_id[0])
								if cgst_data.effective_from_date and cgst_data.effective_to_date:
									if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
										cgst_percent = cgst_data.amount * 100
										cgst_rate = str(cgst_percent)+'%'
										cgst_amt = round((temp.estimated_contract_cost*cgst_percent)/100,2)
								else:
									raise osv.except_osv(('Alert'),("CGST tax not configured!"))
								# sgst/utgst calculation
								# case: if state is a union_territory
								if new_address_data.state_id.union_territory:
									utgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','utgst')])
									ut_data = account_tax_obj.browse(cr,uid,utgst_id[0])
									if ut_data.effective_from_date and ut_data.effective_to_date:
										if str(today_date) >= ut_data.effective_from_date and str(today_date) <= ut_data.effective_to_date:
											utgst_percent = ut_data.amount * 100
											sgst_rate = str(utgst_percent)+'%'
											sgst_amt = round((temp.estimated_contract_cost*utgst_percent)/100,2)
									else:
										raise osv.except_osv(('Alert'),("UTGST tax not configured!"))
								# case: if state is not a union_territory
								else:
									sgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','sgst')])
									st_data = account_tax_obj.browse(cr,uid,sgst_id[0])
									if st_data.effective_from_date and st_data.effective_to_date:
										if str(today_date) >= st_data.effective_from_date and str(today_date) <= st_data.effective_to_date:
											sgst_percent = st_data.amount * 100
											sgst_rate = str(sgst_percent)+'%'
											sgst_amt = round((temp.estimated_contract_cost*sgst_percent)/100,2)
									else:
										raise osv.except_osv(('Alert'),("SGST tax not configured!"))
							# case: if both states are different
							else:
								igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
								igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
								if igst_data.effective_from_date and igst_data.effective_to_date:
									if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
										igst_percent = igst_data.amount * 100
										igst_rate = str(igst_percent)+'%'
										igst_amt = round((temp.estimated_contract_cost*igst_percent)/100,2)
								else:
									raise osv.except_osv(('Alert'),("IGST tax not configured!"))
							# cess calculation
							cess_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cess')])
							if cess_id:
								cess_data = account_tax_obj.browse(cr,uid,cess_id[0])
								if cess_data.effective_from_date and cess_data.effective_to_date:
									if str(today_date) >= cess_data.effective_from_date and str(today_date) <= cess_data.effective_to_date:								
										cess_percent = cess_data.amount * 100
										cess_rate = str(cess_percent)+'%'
										cess_amt = round((temp.estimated_contract_cost*cess_percent)/100,2)
							self.pool.get('inspection.costing.line').write(cr,uid,temp.id,
								{
									'cgst_rate': cgst_rate,
									'cgst_amt': cgst_amt,
									'sgst_rate': sgst_rate,
									'sgst_amt': sgst_amt,
									'igst_rate': igst_rate,
									'igst_amt': igst_amt,
									'cess_rate': cess_rate,
									'cess_amt': cess_amt,
								})
							# total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
						self.pool.get('tax').add_tax(cr,uid,value_id,'sale.contract')
						if value_id:
							for sc in self.pool.get('sale.contract').browse(cr,uid,[value_id]):
								if sc.tax_one2many:
									for amt in sc.tax_one2many:
										total_tax_amt+=amt.amount
							self.pool.get('sale.contract').write(cr,uid,value_id,{'total_tax_amt':total_tax_amt})
						for iterate in res.comment_line_o2m:
							date=datetime.now()
							self.pool.get('comment.line').create(cr,uid,
								{
									'contract_line_id':value_id,
									'user_name':self.pool.get('res.users').browse(cr,uid,uid).name,
									'comment_date':iterate.comment_date,
									'comment':iterate.comment
								})
						self.write(cr,uid,ids,{'comment_remark':None})
					else:
						raise osv.except_osv(('Warning!'),('You cannot create Contracted Entry'))
					self.write(cr,uid,res.id,{'contract_created':True})
					return{
								'type': 'ir.actions.act_window',
								'name':'Contract',
								'view_type': 'form',
								'view_mode': 'form',
								'res_model': 'sale.contract',
								'res_id':value_id,
								#'res_id':val,
								'view_id':False,
								'target':'current',	
								'context': context,
						}
			# elif res.sez_quotation == 'sez_without_notification' or lot_bond==False:
			elif not branch_id_str and service_classification == 'SEZ' or lot_bond_list[0] == False:
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr,uid,'gst_accounting','invoice_push_notification_form_view')
				context.update({'sale_form_id_form':res.id,'sale_igst_check':True})
				return {
					'type': 'ir.actions.act_window',
					'name': 'Notification',
					'view_mode': 'form',
					'view_type': 'form',
					'view_id': form_view[1],
					# 'res_id': '',
					'res_model': 'invoice.push.notification',
					'target': 'new',
					'context':context
			}
			# elif res.sez_quotation == 'sez_with_notification' and lot_bond == True:
			elif branch_id_str and service_classification =='SEZ' and lot_bond_list[0]==True:
				self.normal_create_contract(cr,uid,[res.id],context)
				if context.has_key('value_id'):
					value_id = context.get('value_id')
				return{
								'type': 'ir.actions.act_window',
								'name':'Contract',
								'view_type': 'form',
								'view_mode': 'form',
								'res_model': 'sale.contract',
								'res_id':value_id,
								#'res_id':val,
								'view_id':False,
								'target':'current',	
								'context': context,
						}

sale_quotation()


class sale_contract(osv.osv):
	_inherit = 'sale.contract'
	_columns = {
		'gst_contract': fields.boolean('GST Contract?'),
		'contract_line_id12':fields.one2many('inspection.costing.line','contract_id12','contract_line_id'),
		# 'campaign':fields.selection([('bps_campaign','Bird Pro Campaign'),('festive_campaign','Festive Offer Campaign'),('no_campaign','No Campaign')],'Campaign'),
		'campaign':fields.many2one('campaign','Campaign'),
		'service_classification':fields.selection([
									('residential','Residential Service'),
									('commercial','Commercial Service'),
									('port','Port Service'),
									('airport','Airport Service'),
									('exempted','Exempted'),
									('sez','SEZ - ZERO RATED'),
									],'Service Classification *'),
		'service_classification_id':fields.many2one('service.classification','Service Classification'),
		'pms_detail':fields.boolean('PMS detail print'),
		'pms_ipm':fields.many2one('product.product','IPM ID'),
		'contract_job':fields.selection([('contract','Contract'),('job','Job')],'Contract/Job'),
		# 'contract_number_ncs': fields.char('Contract Number NCS', size=100),
		# 'inv_type':fields.many2one('invoice.type','Invoice Type'),
		'round_off_val':fields.float('Round off'),
	}

	# _defaults = {
	# 	'contract_job':'contract',
	# }

	def onchange_contract_period(self,cr,uid,ids,contract_period,contract_end_date,contract_start_date):
		v = {}
		contract_period=int(contract_period)
		if contract_period < 12 and contract_period >=0:
			v['contract_job']='job'
		else:
			v['contract_job']='contract'
		if contract_period and not contract_start_date:
			raise osv.except_osv(('Alert !'),('Please select Contract Start Date'))
		else:
			if contract_period and contract_start_date:
				renewal_period = contract_period - 2
				end_dt= self.add_months(contract_start_date,contract_period)
				renewal=self.add_months(contract_start_date,renewal_period)
				exp_date = (datetime.strptime(str(end_dt)[0:10],'%Y-%m-%d')) + relativedelta( days =- 1)
				v['contract_end_date']=str(exp_date.date())
				end_dt = str(end_dt)
			

				if end_dt :
					date1=datetime.strptime(contract_start_date, '%Y-%m-%d').date()
					contract_s_date=date1.strftime("%d/%m/%Y")
					date2=exp_date.date()
					contract_e_date=date2.strftime("%d/%m/%Y")
					date_concate = contract_s_date + ' - ' + contract_e_date #abdulrahim26April
				        v['contract_start_end'] = date_concate
			if contract_period == 0 and contract_start_date:
				v['contract_end_date']=contract_start_date
				date1=datetime.strptime(contract_start_date, '%Y-%m-%d').date()
				contract_s_date=date1.strftime("%d/%m/%Y")
				v['contract_start_end']=contract_s_date  + ' - ' + contract_s_date
			cr.execute(('update sale_contract set job_create =True where id=%s'),(ids))
			return {'value': v}
			
	def onchange_ipm(self,cr,uid,ids,pms_detail,context=None):
		data={}
		if pms_detail:
			data.update({'pms_detail':pms_detail})
			ipm_id=self.pool.get('product.product').search(cr,uid,[('prod_type','=','ipm')])
			if ipm_id:
				data.update({'pms_ipm':ipm_id[0]})
		return {'value':data}


	def recr_amount(self,obj,value,date):
		if not obj.parent_id:
			return obj.amount*value
		else:
			if obj.parent_id.effective_from_date <= date and obj.parent_id.effective_to_date > date:
				return obj.amount*self.recr_amount(obj.parent_id,value,date)	
		return 0	

	def add_contract_tax(self,cr,uid,model_id,model):
		val1=0
		qry=if_present=False
		tax_ids=[]
		todays_date=datetime.now().date().strftime("%Y-%m-%d")
		contract_end_date=contract_date=''
		model_id=model_id if isinstance(model_id,(int,long)) else model_id[0]
		# cr.execute('delete from tax where sale_contract_id=%s',(model_id,))
		for order in self.pool.get('sale.contract').browse(cr,uid,[model_id]):
			if order.exempted != True:
				for line in order.contract_line_id12:
						val1 += line.amount
				total_amount = round(val1)
				total_amount = round(order.basic_amount)
				
				sale_ids=self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',order.contract_number)])

				for k in self.pool.get('sale.contract').browse(cr,uid,sale_ids):
					
					if k.contract_end_date:
						contract_end_date=(datetime.strptime(k.contract_end_date,'%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')
						
					# if not k.renew_check:
						
						
					# search_ids = self.pool.get('tax').search(cr,uid,[('sale_contract_id','=',k.id)])
					# for each_tax in self.pool.get('tax').browse(cr,uid,search_ids):
					# 	tax_ids.append(each_tax.account_tax_id.id)
					compare_date=contract_end_date if contract_end_date > todays_date else todays_date
					tax_ids= self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',compare_date),('effective_to_date','>',compare_date),('description','=','gst'),('select_tax_type','=','igst')])
					GST_val=self.pool.get('account.account').search(cr,uid,[('name','=','GST')])
					# if GST_val:
					# 	Inter_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','igst')])[0]
					# 	union_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','utgst')])[0]
					# 	state_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','sgst')])[0]
					# 	central_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','cgst')])[0]
					# 	for i in k.contract_line_id:
					# 		if k.branch_id.state_id.name==i.state_id.name:
					# 			if Inter_state_id in tax_ids:
					# 				tax_ids.remove(Inter_state_id)
					# 			if k.branch_id.state_id.union_territory==False:
					# 				if union_state_id in tax_ids:
					# 					tax_ids.remove(union_state_id)
					# 			else:
					# 				if state_gst in tax_ids:
					# 					tax_ids.remove(state_gst)
					# 		else:
					# 			if (union_state_id in tax_ids or state_gst in tax_ids or central_gst in tax_ids): 
					# 				tax_ids.remove(union_state_id)
					# 				tax_ids.remove(state_gst)
					# 				tax_ids.remove(central_gst)
					#######################remove this########################
					#service_tax_id=k.service_tax_many2one.id
					#swachh_bharat_tax_id=k.swachh_bharat_tax_many2one.id
					#edu_tax_id=k.edu_tax_many2one.id
					#hs_edu_tax_id=k.hs_edu_many2one.id
					#tax_ids1=[service_tax_id ,swachh_bharat_tax_id,edu_tax_id,hs_edu_tax_id]
					#tax_ids=filter(None,tax_ids1)
					##########################################################
				# compare_date=contract_end_date if contract_end_date > todays_date else todays_date
				# if renew_check:
				# 	tax_ids= self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',compare_date),('effective_to_date','>',compare_date)])
				# cr.execute("select account_tax_id from renewal_tax where renew_contract_id=%s" %(str(model_id)))
				# current_ids=cr.fetchall()
				# del_ids=[a for a in current_ids if a not ifin tax_ids]
				# if del_ids:
				# 	for j in del_ids:
				# 		cr.execute("delete from renewal_tax where account_tax_id=%s and renew_contract_id=%s" %(str(j[0]),str(model_id)))
				for i in self.pool.get('account.tax').browse(cr,uid,tax_ids):
					
					current_tax_amount=self.recr_amount(i,total_amount,compare_date)
					cr.execute("select account_tax_id from tax where sale_contract_id=%s and account_tax_id=%s" %(str(model_id),str(i.id)))
					if_present=cr.fetchall()
					if current_tax_amount>0:
						if not if_present:
							insert_qry='insert into tax(name,amount,sale_contract_id,account_tax_id)values(%s,%s,%s,%s)' %("'"+str(i.name)+"'",str(current_tax_amount),str(model_id),str(i.id))
							cr.execute(insert_qry)

				cr.execute('delete from tax where sale_contract_id=%s and account_tax_id != %s',(model_id,tax_ids[0]))
				cr.commit()
							# cr.execute('insert into renewal_tax(name,amount,renew_contract_id,account_tax_id)values(%s,%s,%s,%s)' %("'"+str(i.name)+"'",str(current_tax_amount),str(model_id),str(i.id)))
						# else:
						# 	cr.execute("update tax set amount=%s where sale_contract_id=%s and account_tax_id=%s" %(str(current_tax_amount),str(model_id),str(i.id)))
						
		return True

	def government_notification_igst(self,cr,uid,ids,context=None):
		pcof_key=self.pool.get('res.users').browse(cr,uid,1).company_id.pcof_key
		for res in self.browse(cr,uid,ids):
			new_address_data=state_val=''
			inspection_line_search_t=self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id12','=',ids[0])]) if self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id12','=',ids[0])]) else self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',ids[0])])
			if inspection_line_search_t:
				for i in inspection_line_search_t:
					new_address_data=self.pool.get('inspection.costing.line').browse(cr,uid,i).address_new
					if new_address_data:
						state_val=new_address_data.state_id.name if new_address_data.state_id else self.pool.get('inspection.costing.line').browse(cr,uid,i).state_id.name
					if res.service_classification not in ('exempted','sez'):
						try:
							if not res.branch_id.state_id.name or not state_val:
								raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
						except:
								raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
			if res.contract_start_date > res.contract_end_date:
				raise osv.except_osv(('Alert!'),('Contract start date must be less or equal to Contract end date'))
			if res.service_classification in ('airport','port'):
				raise osv.except_osv(('Alert!'),('Airport/Port service classification cannot be selected as of now!'))
		cgst_rate = '0.0%'
		cgst_amt = 0.0
		sgst_rate = '0.0%'
		sgst_amt = 0.0
		igst_rate = '0.0%'
		igst_amt = 0.0
		cess_rate = '0.0%'
		cess_amt = 0.0
		total_tax_amt=0.0
		gst_grand_total=0.0
		contract_job=''
		account_tax_obj = self.pool.get('account.tax')
		today_date = datetime.now().date()
		gst_select_taxes = ['igst']
		gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
		if not gst_taxes:
			raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
		insp_ids = self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',ids)])
		for isp_id in insp_ids:
			self.pool.get('inspection.costing.line').write(cr,uid,isp_id,{'tab_visible':True})
		if self.browse(cr,uid,ids[0]).is_ipm:
			insp_ipm_ids = self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',ids)])
			if insp_ipm_ids :
				new_address_id=self.pool.get('inspection.costing.line').browse(cr,uid,insp_ipm_ids)[0].address_new.id
			insp_ids = self.pool.get('inspection.costing.line').search(cr,uid,[('ipm_id','=',insp_ipm_ids)])
			for isp_id in insp_ids:
				self.pool.get('inspection.costing.line').write(cr,uid,isp_id,{'tab_visible':True,'address_new': new_address_id}) # get address new against child services of IPM 
		self.write(cr,uid,ids[0],{'invoice_date_invisible':True})
		today_date = datetime.now().date()
		year = today_date.year
		year1=today_date.strftime('%y')
		for res in self.browse(cr,uid,ids):
			if res.contract_line_id:
				for x in res.contract_line_id:
					if x.estimated_contract_cost==0.0 or res.grand_total==0.0:
						raise osv.except_osv(('Alert!'),('Contract Amount cannot be zero!'))
		search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','sale.contract')])
		if search:
			for i in self.pool.get('ir.sequence').browse(cr,uid,search):
				if i.year != year1:
						self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year1,'number_next':1})	
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		start_year =''
		end_year = ''
		contract_id = ''
		if month > 3:
			start_year = year
			end_year = year+1
			year1 = int(year1)+1
		else:
			start_year = year-1
			end_year = year
			year1 = int(year1)
		if str(today_date) >= '2017-03-01' and str(today_date) <= '2017-03-31':
			financial_start_date ='2017-03-01'
			financial_end_date = '2017-03-31'
		else:
			financial_start_date = str(start_year)+'-04-01'
			financial_end_date = str(end_year)+'-03-31'
			financial_year =str(year1-1)+str(year1)
			if not res.gst_contract:
				for get_values in res.contract_line_id:
					contract_id='2CO'
					if get_values.pms:
						if get_values.pms.prod_type == 'BPS' or get_values.pms.prod_type == 'bps':
							contract_id = '2BO'
					if contract_id=='2BO':
						seq_temp=str(pcof_key)+'2BO1718%'
						# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2BO18%' order by contract_number desc limit 1")
						# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+"and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2BO1718%' order by contract_number desc limit 1")
						cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number_ncs is null and contract_number ilike '"+str(seq_temp)+"' order by contract_number desc limit 1")
					else:
						seq_temp=str(pcof_key)+'2CO1718%'
						# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2CO18%' order by contract_number desc limit 1")
						# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2CO1718%' order by contract_number desc limit 1")
						cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number_ncs is null and contract_number ilike '"+str(seq_temp)+"' order by contract_number desc limit 1")
					# if contract_id=='2BO':
					# 	# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2BO18%' order by contract_number desc limit 1")
					# 	cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2BO1718%' order by contract_number desc limit 1")
					# else:
					# 	# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2CO18%' order by contract_number desc limit 1")
					# 	cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2CO1718%' order by contract_number desc limit 1")
					increment_value = ''
					get_count = cr.fetchone()
			if res.gst_contract:
				for get_values in res.contract_line_id12:
					contract_id='2CO'
					if get_values.pms:
						if get_values.pms.prod_type == 'BPS' or get_values.pms.prod_type == 'bps':
							contract_id = '2BO'
					if contract_id=='2BO':
						seq_temp=str(pcof_key)+'2BO1718%'
						# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2BO18%' order by contract_number desc limit 1")
						# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+"and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2BO1718%' order by contract_number desc limit 1")
						cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number_ncs is null and contract_number ilike '"+str(seq_temp)+"' order by contract_number desc limit 1")
					else:
						seq_temp=str(pcof_key)+'2CO1718%'
						# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2CO18%' order by contract_number desc limit 1")
						# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2CO1718%' order by contract_number desc limit 1")
						cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number_ncs is null and contract_number ilike '"+str(seq_temp)+"' order by contract_number desc limit 1")
					# if contract_id=='2BO':
					# 	# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2BO18%' order by contract_number desc limit 1")
					# 	cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2BO1718%' order by contract_number desc limit 1")
					# else:
					# 	# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2CO18%' order by contract_number desc limit 1")
					# 	cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2CO1718%' order by contract_number desc limit 1")
					increment_value = ''
					get_count = cr.fetchone()

		con_no = ''
		pcof_key = ''
		company_id=self._get_company(cr,uid,context=None)
		if company_id:
			for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
				if comp_id.contract_id:
					contract_id= comp_id.contract_id
				if comp_id.pcof_key:
					pcof_key = comp_id.pcof_key
			for get_values in res.contract_line_id:
				if get_values.pms:
					if get_values.pms.prod_type == 'BPS' or get_values.pms.prod_type == 'bps':
						contract_id = '2BO'
			if not get_count or get_count==None:
				seq=1
				#con_no = pcof_key + contract_id + str(year1) + str(seq).zfill(6)
				con_no = pcof_key + contract_id + str(financial_year) + str(seq).zfill(5)
			else:
				contract_number = get_count[0]
				if '2CO1718' in contract_number:
					# contract_id_year = '2CO'+str(year1)
					contract_id_year = '2CO'+str(financial_year)
				elif '2BO1718' in contract_number:
					# contract_id_year = '2BO'+str(year1)
					contract_id_year = '2BO'+str(financial_year)
					contract_id='2BO'
				contract_number_split = contract_number.split(contract_id_year)
				contract_number_second = contract_number_split[1]
				increment_value = int(contract_number_second)+1
				# new_increment_value = str(increment_value).zfill(6)
				new_increment_value = str(increment_value).zfill(5)
				con_no = pcof_key + contract_id + str(financial_year) + str(new_increment_value)
		pms_line = ''
		for res in self.browse(cr,uid,ids):
			date=datetime.now().date()
			start_date = datetime.strptime(res.contract_start_date, "%Y-%m-%d").date()
			end_date = datetime.strptime(res.contract_end_date, "%Y-%m-%d").date()
			contract_period = res.contract_period
			today_date = datetime.strptime(str(date), "%Y-%m-%d").date()
			if start_date < today_date:
				total_cal =  (today_date - start_date).days
				if total_cal >= 15:
					raise osv.except_osv(('Alert!'),('Please Select Proper Start Date'))
			if start_date < end_date and int(contract_period)==0:
				total_cal =  relativedelta(end_date,start_date).months
				if total_cal >=1:
					raise osv.except_osv(('Alert!'),('Cannot create contract greater than one month with contract period zero'))
			if res.parent_ref:
				self.write(cr,uid,ids,{'state':'renew','contract_key':con_no}) # 12july16 for renewed contract contract key = contract number 
				renew_sale_id = self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',res.parent_ref)])
				self.pool.get('sale.contract').write(cr,uid,renew_sale_id,{'renew_check':False,'renew_print_check':False})
			if not res.no_of_payment:
				raise osv.except_osv(('Alert!'),('Please Enter Number of Payment'))
			if not res.contract_invoice_line:
				raise osv.except_osv(('Alert!'),('Please Generate Payterm Line'))
			contract_date = str(datetime.now().date())	
			seq_id = con_no 
			if res.quotation_number!=False:
				search = self.pool.get('sale.quotation').search(cr,uid,[('quotation_number','=',res.quotation_number)])
				if search:
						self.pool.get('sale.quotation').write(cr,uid,search[0],{'contract_value':res.grand_total})
			cr.execute("update sale_contract set contract_number =%s,contract_date=%s where id=%s",(con_no,contract_date,res.id))
			for temp in res.contract_line_id:
				self.pool.get('contract.duplicate').create(cr,uid,
					{
						'location_id':temp.address_new.id,
						'res_partner_address_id':temp.address_new.partner_address,
						'start_date':res.contract_start_date,
						'end_date':res.contract_end_date,
						'contract_number':seq_id,
						'pest_issue_id':temp.pest.id,
						'pest_issue':temp.pest.name,
						'pms_people_id':temp.pms.id,
						'pms_people':temp.pms.name,
						'contract_id':res.id
					})
			for line in res.contract_line_id:
				if line.pms:
					pms = line.pms.name
					new_pms_line = [pms,pms_line]
					pms_line = ' , '.join(filter(bool,new_pms_line))
			cr.execute("update sale_contract set pms_lines =%s,renewal_amt = %s,contract_date = %s  where id=%s",(pms_line,res.total_amount,str(datetime.now().date()),res.id))
			self.sale_contract(cr, uid, ids,con_no,pms_line, context=context)
		for rec in self.browse(cr,uid,ids):
			customer_contract=''
			date1=''
			date1=str(datetime.now().date())
			conv=time.strptime(str(date1),"%Y-%m-%d")
			date1 = time.strftime("%d-%m-%Y",conv)
			customer_contract=rec.cust_name+'    Contract  Created On    '+date1
			customer_contract_date=self.pool.get('customer.logs').create(cr,uid,{'customer_join':customer_contract,'customer_id':rec.partner_id.id})
			if rec.service_classification not in ('exempted'):
				self.add_contract_tax(cr,uid,ids,'sale.contract')
			if res.gst_contract == True:
				contract_line_id = res.contract_line_id12
			else:
				contract_line_id = res.contract_line_id
		for i in contract_line_id:
			is_chs=False
			if i.address_new.premise_type=='co_operative_housing_society':
				is_chs=True
			if not res.is_ipm:
				if not is_chs:
					self.pool.get('inspection.costing.line').write(cr,uid,i.id,{'tab_visible':True})
					new_id = self.pool.get('inspection.costing.line').create_job_scheduled(cr,uid,[i.id],context=context)
				else:
					for j in i.ipm_one2many:
						if not is_chs:
								self.pool.get('inspection.costing.line').write(cr,uid,j.id,{'tab_visible':True})
						new_id = self.pool.get('inspection.costing.line').create_job_scheduled(cr,uid,[j.id],context=context)
			
			if i.contract_id1.gst_contract == False:
				address_data = i.address_new
				addrs_items = []
				long_address = ''	
				if address_data.apartment not in [' ',False,None]:
					addrs_items.append(address_data.apartment)
				if address_data.location_name not in [' ',False,None]:
					addrs_items.append(address_data.location_name)
				if address_data.building not in [' ',False,None]:
					addrs_items.append(address_data.building)
				if address_data.sub_area not in [' ',False,None]:
					addrs_items.append(address_data.sub_area)
				if address_data.street not in [' ',False,None]:
					addrs_items.append(address_data.street)
				if address_data.landmark not in [' ',False,None]:
					addrs_items.append(address_data.landmark)
				if address_data.city_id:
					addrs_items.append(address_data.city_id.name1)
				if address_data.district:
					addrs_items.append(address_data.district.name)
				if address_data.tehsil:
					addrs_items.append(address_data.tehsil.name)
				if address_data.state_id:
					addrs_items.append(address_data.state_id.name)
				if address_data.zip not in [' ',False,None]:
					addrs_items.append(address_data.zip)
				if len(addrs_items) > 0:
					last_item = addrs_items[-1]
					for item in addrs_items:
						if item!=last_item:
							long_address = long_address+item+','+' '
						if item==last_item:
							long_address = long_address+item
				if long_address:
					complete_address = '['+long_address+']'
				else:
					complete_address = ' '
				product_full_name = i.pms.product_desc or ''
				services = product_full_name.upper() + ' '+complete_address
				self.pool.get('inspection.costing.line').write(cr,uid,i.id,
					{
						'services': services,
						'hsn_code': i.pms.hsn_sac_code,
						'discount': 0,
						'taxable_value': i.amount,	
						'contract_id12': i.contract_id1.id,
						'pms':i.pms.id,
						'processed': True
					})
			new_address_data = i.address_new
			cont_data = self.browse(cr,uid,ids[0])
			if cont_data.service_classification not in ('exempted'):
				state_val=new_address_data.state_id.name if new_address_data.state_id else i.state_id.name
				if not res.branch_id.state_id or not state_val:
					raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
				
				# case: if both states are different
				else:
					igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
					igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
					if igst_data.effective_from_date and igst_data.effective_to_date:
						if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
							igst_percent = igst_data.amount * 100
							igst_rate = str(igst_percent)+'%'
							igst_amt = round((i.estimated_contract_cost*igst_percent)/100,2)
					else:
						raise osv.except_osv(('Alert'),("IGST tax not configured!"))
				self.pool.get('inspection.costing.line').write(cr,uid,i.id,
					{
						'cgst_rate': cgst_rate,
						'cgst_amt': cgst_amt,
						'sgst_rate': sgst_rate,
						'sgst_amt': sgst_amt,
						'igst_rate': igst_rate,
						'igst_amt': igst_amt,
						'cess_rate': cess_rate,
						'cess_amt': cess_amt,
					})
				total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
			elif cont_data.service_classification == 'exempted':
				self.pool.get('inspection.costing.line').write(cr,uid,i.id,
					{
						'cgst_rate': cgst_rate,
						'cgst_amt': cgst_amt,
						'sgst_rate': sgst_rate,
						'sgst_amt': sgst_amt,
						'igst_rate': igst_rate,
						'igst_amt': igst_amt,
						'cess_rate': cess_rate,
						'cess_amt': cess_amt,
					})
				total_tax_amt = 0.00
		contract_data = self.browse(cr,uid,ids[0])
		contract_period=contract_data.contract_period
		if contract_data.gst_contract == False:
			self.write(cr,uid,contract_data.id,{'gst_contract':True})
		if contract_data.service_classification not in ('exempted'):
			gst_grand_total=contract_data.gst_grand_total
		elif contract_data.service_classification=='exempted':
			gst_grand_total=contract_data.gst_total_amount
			for i in contract_data.tax_one2many:
				self.pool.get('tax').write(cr,uid,i.id,{'amount':0.0})
		if int(contract_period) < 12 and int(contract_period) >=0:
			contract_job='job'
		else:
			contract_job='contract'
		self.write(cr,uid,contract_data.id,{'gst_total_amount':contract_data.gst_total_amount,'total_tax_amt':igst_amt,'gst_grand_total':round(gst_grand_total),'contract_job':contract_job})
		return True
		


	def generate_contract(self, cr, uid, ids, context=None):
		service_classification_list = []
		partner_address_list = []
		special_status_list = []
		lot_bond_list = []
		nature_name = ''
		pcof_key=self.pool.get('res.users').browse(cr,uid,1).company_id.pcof_key
		res_company_obj = self.pool.get('res.company')
		new_address_obj = self.pool.get('new.address')
		res_partner_address_obj =self.pool.get('res.partner.address')
		o = self.browse(cr,uid,ids[0])
		service_classification = str(o.service_classification)
		pcof_key=self.pool.get('res.users').browse(cr,uid,1).company_id.pcof_key
		search_inspection_line_id = self.pool.get('inspection.costing.line').search(cr,uid,['|',('contract_id1','=',o.id),('contract_id12','=',o.id)])
		browse_inspection_line_id = self.pool.get('inspection.costing.line').browse(cr,uid,search_inspection_line_id)
		for browse_location_id in browse_inspection_line_id:
			location_id = browse_location_id.address_new.id
			partner_address = new_address_obj.browse(cr,uid,location_id).partner_address.id
			lot_bond = res_partner_address_obj.browse(cr,uid,partner_address).lot_bond
			lot_bond_list.append(lot_bond)
			partner_address_list.append(partner_address)
			if len(partner_address_list) == 1:
				query_str = "select distinct(special_status) from res_partner_address where id="+str(partner_address_list[0])
				cr.execute(query_str)
				lot_bond = res_partner_address_obj.browse(cr,uid,partner_address_list[0]).lot_bond
			elif len(partner_address_list) > 1:
				query_str_tuple = "select distinct(special_status) from res_partner_address where id in "+str(tuple(partner_address_list))
				cr.execute(query_str_tuple)
			values = cr.fetchall()
			values_id = [x[0] for x in values]
			if len(values_id) > 1 or len(values_id) == 1:
				for values_browse_id in values_id:
					if values_browse_id != None:
						browse_special_status = self.pool.get('special.status').browse(cr,uid,values_browse_id).name
						special_status_list.append(str(browse_special_status))
					if values_browse_id == None:
						special_status_list.append(None)
				if service_classification =='sez':
					if 'SEZ' in special_status_list and None in special_status_list:
						raise osv.except_osv(('Warning !'),('All Locations must have special status as SEZ in customer location'))
					if None in special_status_list:
						raise osv.except_osv(('Warning !'),('All Locations must have special status as SEZ in customer location'))
				if service_classification == 'sez':
					if 'SEZ' in special_status_list:
						lot_bond_list = list(set(lot_bond_list))
						if len(lot_bond_list) > 1:
							raise osv.except_osv(('Alert!'),('Please Tick or Untick the lot bond for all location !'))
		lead_no=o.lead_no
		if lead_no:
			lead_no=lead_no.split(',')
			for i in lead_no:
				if i:
					cr.execute("update ccc_branch_new set state ='closed' where request_id ='%s'"%(i))
		branch_id = o.branch_id.id
		service_classification = str(o.service_classification)
		if branch_id:
			branch_id_name = res_company_obj.browse(cr,uid,branch_id).government_notification
			branch_id_str = branch_id_name
			if (branch_id_str and lot_bond == True and service_classification == 'sez') or (branch_id_str and service_classification !='sez') or (not branch_id_str and service_classification !='sez'):
					for res in self.browse(cr,uid,ids):
						new_address_data=state_val=''
						inspection_line_search_t=self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id12','=',ids[0])]) if self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id12','=',ids[0])]) else self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',ids[0])])
						if inspection_line_search_t:
							for i in inspection_line_search_t:
								new_address_data=self.pool.get('inspection.costing.line').browse(cr,uid,i).address_new
								if new_address_data:
									state_val=new_address_data.state_id.name if new_address_data.state_id else self.pool.get('inspection.costing.line').browse(cr,uid,i).state_id.name
								if res.service_classification not in ('exempted','sez'):
									try:
										if not res.branch_id.state_id.name or not state_val:
											raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
									except:
											raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
						if res.contract_start_date > res.contract_end_date:
							raise osv.except_osv(('Alert!'),('Contract start date must be less or equal to Contract end date'))
						if res.service_classification in ('airport','port'):
							raise osv.except_osv(('Alert!'),('Airport/Port service classification cannot be selected as of now!'))
					cgst_rate = '0.0%'
					cgst_amt = 0.0
					sgst_rate = '0.0%'
					sgst_amt = 0.0
					igst_rate = '0.0%'
					igst_amt = 0.0
					cess_rate = '0.0%'
					cess_amt = 0.0
					total_tax_amt=0.0
					gst_grand_total=0.0
					contract_job=''
					account_tax_obj = self.pool.get('account.tax')
					today_date = datetime.now().date()
					gst_select_taxes = ['cgst','sgst','utgst','igst','cess']
					gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
					if not gst_taxes:
						raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
					insp_ids = self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',ids)])
					for isp_id in insp_ids:
						self.pool.get('inspection.costing.line').write(cr,uid,isp_id,{'tab_visible':True})
					if self.browse(cr,uid,ids[0]).is_ipm:
						insp_ipm_ids = self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',ids)])
						if insp_ipm_ids :
							new_address_id=self.pool.get('inspection.costing.line').browse(cr,uid,insp_ipm_ids)[0].address_new.id
						insp_ids = self.pool.get('inspection.costing.line').search(cr,uid,[('ipm_id','=',insp_ipm_ids)])
						for isp_id in insp_ids:
							self.pool.get('inspection.costing.line').write(cr,uid,isp_id,{'tab_visible':True,'address_new': new_address_id}) # get address new against child services of IPM 
					self.write(cr,uid,ids[0],{'invoice_date_invisible':True})
					today_date = datetime.now().date()
					year = today_date.year
					year1=today_date.strftime('%y')
					for res in self.browse(cr,uid,ids):
						if res.contract_line_id:
							for x in res.contract_line_id:
								if x.estimated_contract_cost==0.0 or res.grand_total==0.0:
									raise osv.except_osv(('Alert!'),('Contract Amount cannot be zero!'))
					search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','sale.contract')])
					if search:
						for i in self.pool.get('ir.sequence').browse(cr,uid,search):
							if i.year != year1:
									self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year1,'number_next':1})	
					year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
					month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
					start_year =''
					end_year = ''
					contract_id = ''
					if month > 3:
						start_year = year
						end_year = year+1
						year1 = int(year1)+1
					else:
						start_year = year-1
						end_year = year
						year1 = int(year1)
					if str(today_date) >= '2017-03-01' and str(today_date) <= '2017-03-31':
						financial_start_date ='2017-03-01'
						financial_end_date = '2017-03-31'
					else:
						financial_start_date = str(start_year)+'-04-01'
						financial_end_date = str(end_year)+'-03-31'
						financial_year =str(year1-1)+str(year1)
						if not res.gst_contract:
							for get_values in res.contract_line_id:
								contract_id='2CO'
								if get_values.pms:
									if get_values.pms.prod_type == 'BPS' or get_values.pms.prod_type == 'bps':
										contract_id = '2BO'
								if contract_id=='2BO':
									seq_temp=str(pcof_key)+'2BO1718%'
									# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2BO18%' order by contract_number desc limit 1")
									# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+"and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2BO1718%' order by contract_number desc limit 1")
									cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number_ncs is null and contract_number ilike '"+str(seq_temp)+"' order by contract_number desc limit 1")
								else:
									seq_temp=str(pcof_key)+'2CO1718%'
									# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2CO18%' order by contract_number desc limit 1")
									# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2CO1718%' order by contract_number desc limit 1")
									cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number_ncs is null and contract_number ilike '"+str(seq_temp)+"' order by contract_number desc limit 1")
								# if contract_id=='2BO':
								# 	# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2BO18%' order by contract_number desc limit 1")
								# 	cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2BO1718%' order by contract_number desc limit 1")
								# else:
								# 	# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2CO18%' order by contract_number desc limit 1")
								# 	cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2CO1718%' order by contract_number desc limit 1")
								increment_value = ''
								get_count = cr.fetchone()
						if res.gst_contract:
							pcof_key=self.pool.get('res.users').browse(cr,uid,1).company_id.pcof_key
							for get_values in res.contract_line_id12:
								contract_id='2CO'
								if get_values.pms:
									if get_values.pms.prod_type == 'BPS' or get_values.pms.prod_type == 'bps':
										contract_id = '2BO'
								if contract_id=='2BO':
									seq_temp=str(pcof_key)+'2BO1718%'
									# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2BO18%' order by contract_number desc limit 1")
									# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+"and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2BO1718%' order by contract_number desc limit 1")
									cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number_ncs is null and contract_number ilike '"+str(seq_temp)+"' order by contract_number desc limit 1")
								else:
									seq_temp=str(pcof_key)+'2CO1718%'
									# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and contract_number ilike '%2CO18%' order by contract_number desc limit 1")
									# cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number ilike '%2CO1718%' order by contract_number desc limit 1")
									cr.execute("select contract_number from sale_contract  where id!="+str(ids[0])+" and contract_number is not null and contract_number not ilike '%/%' and import_bool <> True and contract_date>='2017-07-01' and contract_number_ncs is null and contract_number ilike '"+str(seq_temp)+"' order by contract_number desc limit 1")
								increment_value = ''
								get_count = cr.fetchone()

					con_no = ''
					pcof_key = ''
					company_id=self._get_company(cr,uid,context=None)
					if company_id:
						for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
							if comp_id.contract_id:
								contract_id= comp_id.contract_id
							if comp_id.pcof_key:
								pcof_key = comp_id.pcof_key
						for get_values in res.contract_line_id:
							if get_values.pms:
								if get_values.pms.prod_type == 'BPS' or get_values.pms.prod_type == 'bps':
									contract_id = '2BO'
						if not get_count or get_count==None:
							seq=1
							#con_no = pcof_key + contract_id + str(year1) + str(seq).zfill(6)
							con_no = pcof_key + contract_id + str(financial_year) + str(seq).zfill(5)
						else:
							contract_number = get_count[0]
							if '2CO1718' in contract_number:
								# contract_id_year = '2CO'+str(year1)
								contract_id_year = '2CO'+str(financial_year)
							elif '2BO1718' in contract_number:
								# contract_id_year = '2BO'+str(year1)
								contract_id_year = '2BO'+str(financial_year)
								contract_id='2BO'
							contract_number_split = contract_number.split(contract_id_year)
							contract_number_second = contract_number_split[1]
							increment_value = int(contract_number_second)+1
							# new_increment_value = str(increment_value).zfill(6)
							new_increment_value = str(increment_value).zfill(5)
							con_no = pcof_key + contract_id + str(financial_year) + str(new_increment_value)
					pms_line = ''
					for res in self.browse(cr,uid,ids):
						date=datetime.now().date()
						start_date = datetime.strptime(res.contract_start_date, "%Y-%m-%d").date()
						end_date = datetime.strptime(res.contract_end_date, "%Y-%m-%d").date()
						contract_period = res.contract_period
						today_date = datetime.strptime(str(date), "%Y-%m-%d").date()
						if start_date < today_date:
							total_cal =  (today_date - start_date).days
							if total_cal >= 15:
								raise osv.except_osv(('Alert!'),('Please Select Proper Start Date'))
						if start_date < end_date and int(contract_period)==0:
							total_cal =  relativedelta(end_date,start_date).months
							if total_cal >=1:
								raise osv.except_osv(('Alert!'),('Cannot create contract greater than one month with contract period zero'))
						if res.parent_ref:
							self.write(cr,uid,ids,{'state':'renew','contract_key':con_no}) # 12july16 for renewed contract contract key = contract number 
							renew_sale_id = self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',res.parent_ref)])
							self.pool.get('sale.contract').write(cr,uid,renew_sale_id,{'renew_check':False,'renew_print_check':False})
						if not res.no_of_payment:
							raise osv.except_osv(('Alert!'),('Please Enter Number of Payment'))
						if not res.contract_invoice_line:
							raise osv.except_osv(('Alert!'),('Please Generate Payterm Line'))
						contract_date = str(datetime.now().date())	
						seq_id = con_no 
						if res.quotation_number!=False:
							search = self.pool.get('sale.quotation').search(cr,uid,[('quotation_number','=',res.quotation_number)])
							if search:
									self.pool.get('sale.quotation').write(cr,uid,search[0],{'contract_value':res.grand_total})
						cr.execute("update sale_contract set contract_number =%s,contract_date=%s where id=%s",(con_no,contract_date,res.id))
						for temp in res.contract_line_id:
							self.pool.get('contract.duplicate').create(cr,uid,
								{
									'location_id':temp.address_new.id,
									'res_partner_address_id':temp.address_new.partner_address,
									'start_date':res.contract_start_date,
									'end_date':res.contract_end_date,
									'contract_number':seq_id,
									'pest_issue_id':temp.pest.id,
									'pest_issue':temp.pest.name,
									'pms_people_id':temp.pms.id,
									'pms_people':temp.pms.name,
									'contract_id':res.id
								})
						for line in res.contract_line_id:
							if line.pms:
								pms = line.pms.name
								new_pms_line = [pms,pms_line]
								pms_line = ' , '.join(filter(bool,new_pms_line))
						cr.execute("update sale_contract set pms_lines =%s,renewal_amt = %s,contract_date = %s  where id=%s",(pms_line,res.total_amount,str(datetime.now().date()),res.id))
						self.sale_contract(cr, uid, ids,con_no,pms_line, context=context)
					for rec in self.browse(cr,uid,ids):
						customer_contract=''
						date1=''
						date1=str(datetime.now().date())
						conv=time.strptime(str(date1),"%Y-%m-%d")
						date1 = time.strftime("%d-%m-%Y",conv)
						customer_contract=rec.cust_name+'    Contract  Created On    '+date1
						customer_contract_date=self.pool.get('customer.logs').create(cr,uid,{'customer_join':customer_contract,'customer_id':rec.partner_id.id})
						if rec.service_classification not in ('exempted','sez'):
							self.pool.get('tax').add_tax(cr,uid,ids,'sale.contract')
						if res.gst_contract == True:
							contract_line_id = res.contract_line_id12
						else:
							contract_line_id = res.contract_line_id
					for i in contract_line_id:
						is_chs=False
						if i.address_new.premise_type=='co_operative_housing_society':
							is_chs=True
						if not res.is_ipm:
							if not is_chs:
								self.pool.get('inspection.costing.line').write(cr,uid,i.id,{'tab_visible':True})
								new_id = self.pool.get('inspection.costing.line').create_job_scheduled(cr,uid,[i.id],context=context)
							else:
								for j in i.ipm_one2many:
									if not is_chs:
											self.pool.get('inspection.costing.line').write(cr,uid,j.id,{'tab_visible':True})
									new_id = self.pool.get('inspection.costing.line').create_job_scheduled(cr,uid,[j.id],context=context)
						if i.contract_id12.gst_contract == True:
							costing_vals = {	
								'contract_id1': i.contract_id12.id,
								'contract_id12': i.contract_id12.id,
							}
							for contract_line in rec.contract_line_id12:
								if contract_line.pms.name_template == 'IPM' or contract_line.pms.name_template == 'IPM Service':
									if contract_line.ipm_one2many:
										for each in contract_line.ipm_one2many:
											if each.nature_id:
												nature_name = each.nature_id.name
												costing_vals.update(
													{
														'nature_id':each.nature_id.id
													})
								if contract_line.nature_id:
									nature_name = contract_line.nature_id.name
								# else:
								if nature_name:
									addrs_items = []
									full_address = ''
									if contract_line.location not in [' ',False,None]:
										addrs_items.append(contract_line.location)
									if contract_line.apartment not in [' ',False,None]:
										addrs_items.append(contract_line.apartment)
									if contract_line.building not in [' ',False,None]:
										addrs_items.append(contract_line.building)
									if contract_line.sub_area not in [' ',False,None]:
										addrs_items.append(contract_line.sub_area)
									if contract_line.landmark not in [' ',False,None]:
										addrs_items.append(contract_line.landmark)
									if contract_line.street not in [' ',False,None]:
										addrs_items.append(contract_line.street)
									if contract_line.city_id:
										addrs_items.append(contract_line.city_id.name1)
									if contract_line.district:
										addrs_items.append(contract_line.district.name)
									if contract_line.tehsil:
										addrs_items.append(contract_line.tehsil.name)
									if contract_line.state_id:
										addrs_items.append(contract_line.state_id.name)
									if contract_line.zip not in [' ',False,None]:
										addrs_items.append(contract_line.zip)
									if len(addrs_items) > 0:
										last_item = addrs_items[-1]
									for item in addrs_items:
										if item != last_item:
											full_address = full_address+item+','+' '
										if item == last_item:
											full_address = full_address+item
									services_new = nature_name.upper()+' '+'['+full_address+']'
									costing_vals.update(
										{
											'services':services_new,
											'pms':None,
											'description':None
										})
							self.pool.get('inspection.costing.line').write(cr,uid,i.id,costing_vals)
						if i.contract_id1.gst_contract == False:
							address_data = i.address_new
							addrs_items = []
							long_address = ''	
							if address_data.apartment not in [' ',False,None]:
								addrs_items.append(address_data.apartment)
							if address_data.location_name not in [' ',False,None]:
								addrs_items.append(address_data.location_name)
							if address_data.building not in [' ',False,None]:
								addrs_items.append(address_data.building)
							if address_data.sub_area not in [' ',False,None]:
								addrs_items.append(address_data.sub_area)
							if address_data.street not in [' ',False,None]:
								addrs_items.append(address_data.street)
							if address_data.landmark not in [' ',False,None]:
								addrs_items.append(address_data.landmark)
							if address_data.city_id:
								addrs_items.append(address_data.city_id.name1)
							if address_data.district:
								addrs_items.append(address_data.district.name)
							if address_data.tehsil:
								addrs_items.append(address_data.tehsil.name)
							if address_data.state_id:
								addrs_items.append(address_data.state_id.name)
							if address_data.zip not in [' ',False,None]:
								addrs_items.append(address_data.zip)
							if len(addrs_items) > 0:
								last_item = addrs_items[-1]
								for item in addrs_items:
									if item!=last_item:
										long_address = long_address+item+','+' '
									if item==last_item:
										long_address = long_address+item
							if long_address:
								complete_address = '['+long_address+']'
							else:
								complete_address = ' '
							product_full_name = i.pms.product_desc or ''
							services = product_full_name.upper() + ' '+complete_address
							self.pool.get('inspection.costing.line').write(cr,uid,i.id,
								{
									'services': services,
									'hsn_code': i.pms.hsn_sac_code,
									'discount': 0,
									'taxable_value': i.amount,	
									'contract_id12': i.contract_id1.id,
									'contract_id1': i.contract_id1.id,
									'pms':i.pms.id,
									'processed': True
								})
						new_address_data = i.address_new
						cont_data = self.browse(cr,uid,ids[0])
						if cont_data.service_classification not in ('exempted','sez'):
							state_val=new_address_data.state_id.name if new_address_data.state_id else i.state_id.name
							if not res.branch_id.state_id or not state_val:
								raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
							if res.branch_id.state_id.id == new_address_data.state_id.id:
								# cgst calculation
								cgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cgst')])
								cgst_data = account_tax_obj.browse(cr,uid,cgst_id[0])
								if cgst_data.effective_from_date and cgst_data.effective_to_date:
									if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
										cgst_percent = cgst_data.amount * 100
										cgst_rate = str(cgst_percent)+'%'
										cgst_amt = round((i.estimated_contract_cost*cgst_percent)/100,2)
								else:
									raise osv.except_osv(('Alert'),("CGST tax not configured!"))
								# sgst/utgst calculation
								# case: if state is a union_territory
								if new_address_data.state_id.union_territory:
									utgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','utgst')])
									ut_data = account_tax_obj.browse(cr,uid,utgst_id[0])
									if ut_data.effective_from_date and ut_data.effective_to_date:
										if str(today_date) >= ut_data.effective_from_date and str(today_date) <= ut_data.effective_to_date:
											utgst_percent = ut_data.amount * 100
											sgst_rate = str(utgst_percent)+'%'
											sgst_amt = round((i.estimated_contract_cost*utgst_percent)/100,2)
									else:
										raise osv.except_osv(('Alert'),("UTGST tax not configured!"))
								# case: if state is not a union_territory
								else:
									sgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','sgst')])
									st_data = account_tax_obj.browse(cr,uid,sgst_id[0])
									if st_data.effective_from_date and st_data.effective_to_date:
										if str(today_date) >= st_data.effective_from_date and str(today_date) <= st_data.effective_to_date:
											sgst_percent = st_data.amount * 100
											sgst_rate = str(sgst_percent)+'%'
											sgst_amt = round((i.estimated_contract_cost*sgst_percent)/100,2)
									else:
										raise osv.except_osv(('Alert'),("SGST tax not configured!"))
							# case: if both states are different
							else:
								igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
								igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
								if igst_data.effective_from_date and igst_data.effective_to_date:
									if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
										igst_percent = igst_data.amount * 100
										igst_rate = str(igst_percent)+'%'
										igst_amt = round((i.estimated_contract_cost*igst_percent)/100,2)
								else:
									raise osv.except_osv(('Alert'),("IGST tax not configured!"))
							# cess calculation
							cess_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cess')])
							if cess_id:
								cess_data = account_tax_obj.browse(cr,uid,cess_id[0])
								if cess_data.effective_from_date and cess_data.effective_to_date:
									if str(today_date) >= cess_data.effective_from_date and str(today_date) <= cess_data.effective_to_date:								
										cess_percent = cess_data.amount * 100
										cess_rate = str(cess_percent)+'%'
										cess_amt = round((i.estimated_contract_cost*cess_percent)/100,2)
							self.pool.get('inspection.costing.line').write(cr,uid,i.id,
								{
									'cgst_rate': cgst_rate,
									'cgst_amt': cgst_amt,
									'sgst_rate': sgst_rate,
									'sgst_amt': sgst_amt,
									'igst_rate': igst_rate,
									'igst_amt': igst_amt,
									'cess_rate': cess_rate,
									'cess_amt': cess_amt,
								})
							total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
						elif cont_data.service_classification == 'exempted' or cont_data.service_classification == 'sez':
							self.pool.get('inspection.costing.line').write(cr,uid,i.id,
								{
									'cgst_rate': cgst_rate,
									'cgst_amt': cgst_amt,
									'sgst_rate': sgst_rate,
									'sgst_amt': sgst_amt,
									'igst_rate': igst_rate,
									'igst_amt': igst_amt,
									'cess_rate': cess_rate,
									'cess_amt': cess_amt,
								})
							total_tax_amt = 0.00
					contract_data = self.browse(cr,uid,ids[0])
					contract_period=contract_data.contract_period
					if contract_data.gst_contract == False:
						self.write(cr,uid,contract_data.id,{'gst_contract':True})
					if contract_data.service_classification not in ('exempted','sez'):
						gst_grand_total=contract_data.gst_grand_total
					elif contract_data.service_classification=='exempted' or contract_data.service_classification=='sez':
						gst_grand_total=contract_data.gst_total_amount
						for i in contract_data.tax_one2many:
							self.pool.get('tax').write(cr,uid,i.id,{'amount':0.0})
						self.write(cr,uid,contract_data.id,{'round_off_val':0.0})
					if int(contract_period) < 12 and int(contract_period) >=0:
						contract_job='job'
					else:
						contract_job='contract'
					self.write(cr,uid,contract_data.id,{'gst_total_amount':contract_data.gst_total_amount,'total_tax_amt':total_tax_amt,'gst_grand_total':round(gst_grand_total),'contract_job':contract_job})
					return {
								'type': 'ir.actions.act_window',
								'name': 'Contract',
								'view_mode': 'form',
								'view_type': 'form',
								'view_id': False,
								'res_id': ids[0],
								'res_model': 'sale.contract',
								'target': 'current',
							}

			elif not branch_id_str and service_classification=='sez' or lot_bond == False:
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr,uid,'gst_accounting','invoice_push_notification_form_view')
				context.update({'sale_contract_id_form':ids[0]})
				return {
					'type': 'ir.actions.act_window',
					'name': 'Notification',
					'view_mode': 'form',
					'view_type': 'form',
					'view_id': form_view[1],
					# 'res_id': '',
					'res_model': 'invoice.push.notification',
					'target': 'new',
					'context':context
			}				

	def onchange_service_classification_id(self, cr, uid, ids, service_classification_id, context=None):
		data = {}
		if service_classification_id:
			classification_obj = self.pool.get('service.classification')
			classification_name = classification_obj.browse(cr,uid,service_classification_id).name
			classification_name = classification_name.title()
			print"classification_name",classification_name
			if 'Residential' in classification_name:
				service_classification = 'residential'
			elif 'Commercial' in classification_name:
				service_classification = 'commercial'
			elif 'Airport' in classification_name:
				service_classification = 'airport'
			elif 'Port' in classification_name:
				service_classification = 'port'
			elif 'Exempted' in classification_name:
				service_classification = 'exempted'
			elif 'Sez' in classification_name:
				service_classification = None
			else:
				service_classification = None
			data.update(
				{
					'service_classification': service_classification,
				})
		else:
			data.update(
				{
					'service_classification': None,
				})
		return {'value':data}		
			
sale_contract()


class invoice_line(osv.osv):

	_inherit = 'invoice.line'
	_columns = {
		}


	def recr_amount(self,obj,value,date):
		if not obj.parent_id:
			return obj.amount*value
		else:
			if obj.parent_id.effective_from_date <= date and obj.parent_id.effective_to_date > date:
				return obj.amount*self.recr_amount(obj.parent_id,value,date)	
		return 0	

	def add_invoice_tax(self,cr,uid,model_id,temp_id):
		val1=0
		qry=if_present=False
		tax_ids=[]
		tax = '18.00'
		todays_date=datetime.now().date().strftime("%Y-%m-%d")
		contract_end_date=contract_date=''
		model_id=model_id if isinstance(model_id,(int,long)) else model_id[0]
		# cr.execute('delete from tax where sale_contract_id=%s',(model_id,))
		for order in self.pool.get('invoice.line').browse(cr,uid,temp_id):
				# print "sssssssssssssssssssssssss",order.amount
				total_amount = round(order.amount)
				sale_contract_browse = self.pool.get('sale.contract').browse(cr,uid,order.invoice_line_id.id)
				sale_ids=self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',sale_contract_browse.contract_number)])

				for k in self.pool.get('sale.contract').browse(cr,uid,sale_ids):
					
					if k.contract_end_date:
						contract_end_date=(datetime.strptime(k.contract_end_date,'%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')
					
					compare_date=contract_end_date if contract_end_date > todays_date else todays_date
					tax_ids= self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',compare_date),('effective_to_date','>',compare_date),('description','=','gst'),('select_tax_type','=','igst')])
					GST_val=self.pool.get('account.account').search(cr,uid,[('name','=','GST')])
					
				for i in self.pool.get('account.tax').browse(cr,uid,tax_ids):
					acc_id=self.pool.get('account.account').search(cr,uid,[('account_tax_many2one','=',i.id)])
					current_tax_amount=self.recr_amount(i,total_amount,compare_date)
					cr.execute("select account_tax_id from invoice_tax_rate where invoice_id=%s and account_tax_id=%s" %(str(model_id),str(i.id)))
					if_present=cr.fetchall()
					if current_tax_amount>0:
						if not if_present:
							insert_qry='insert into invoice_tax_rate(name,amount,invoice_id,account_tax_id,tax_rate,account_id)values(%s,%s,%s,%s,%s,%s)' %("'"+str(i.name)+"'",str(round(current_tax_amount)),str(model_id),str(i.id),str(tax),str(acc_id[0]))
							cr.execute(insert_qry)
						
		return True

	def button_push_igst(self,cr,uid,ids,context=None):
		for temp_id in self.browse(cr,uid,ids):
			total = 0.0
			basic_amount = 0.00
			amount =0.0
			tax_amount = 0.0
			list_invoice_id = []
			list_contract_id = []
			grand_total = 0.0
			temp_amount = 0.0
			amount_new=0.0
			create_id = ''
			adhoc = False
			exempted = False
			res_id=''
			invoice_created=False
			fum_invoice=False
			region_of_use=False
			fumigant=False
			cgst_rate = '0.00%'
			cgst_amt = 0.00
			sgst_rate = '0.00%'
			sgst_amt = 0.00
			igst_rate = '0.00%'
			igst_amt = 0.00
			cess_rate = '0.00%'
			cess_amt = 0.00
			total_tax_amt=0.00
			account_tax_obj = self.pool.get('account.tax')
			today_date = datetime.now().date()
			gst_select_taxes = ['igst']
			gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
			if not gst_taxes:
				raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
			for res in self.pool.get('sale.contract').browse(cr,uid,[temp_id.invoice_line_id.id]):
				contract_line_id = res.contract_line_id12 if res.gst_contract else res.contract_line_id
				service_classification = str(res.service_classification)
				if res.check_invoice:
					raise osv.except_osv(('Alert!'),('Check the other server for invoice'))
				if res.id:
					res_id=res.id
					self.pool.get('sale.contract').write(cr,uid,res.id,{'create_entry_sales_msg':True,'payterm_button':True})#payterm 
					if contract_line_id:
						for j in contract_line_id:
							if not j.invoice_created:
								self.pool.get('inspection.costing.line').write(cr,uid,j.id,{'invoice_created':True})
								invoice_created=True
					if invoice_created:
						# if service_classification not in ('exempted'):
						# 	self.pool.get('tax').add_tax(cr,uid,res.id,'sale.contract')
						company_name = ''
						test=False
						time_cur = time.strftime("%H:%M:%S")#a
						date = datetime.now().date()#a
						company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
						if company_id:
							company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
						#req_idd = res.request_id
						current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key #changes 22jul16
						con_cat = str(company_name)+'_'+str(current_company)+'_contract_amount'+str(date)+str(time_cur)+'.sql'#A date
						filename = os.path.expanduser('~')+'/sql_files/'+con_cat
						directory_name = str(os.path.expanduser('~')+'/sql_files/')
						d = os.path.dirname(directory_name)
						if not os.path.exists(d):
							os.makedirs(d)
						if contract_line_id:#a
							for j in contract_line_id:#a
								update_contract_amount = "\nupdate inspection_costing_line set estimated_contract_cost = '"+str(j.estimated_contract_cost)+"' where contract_id1 = (select id from sale_contract where contract_number = '"+str(res.contract_number)+"' ) and pms =(select id from product_product where name_template ilike  '"+str(j.pms.name)+"' );"
						with open(filename,'a') as f:
							f.write(update_contract_amount)
							f.close()
				amount = round(temp_id.amount)
				if res.service_classification == 'exempted':
					exempted=True
				if res.fum_contract == True:
					fum_invoice=True,
					fumigant=res.fumigant
					region_of_use=res.region_of_use
				create_id = self.pool.get('invoice.adhoc.master').create(cr,uid,
											{
												'gst_invoice': True,
												'cust_name':res.cust_name,
												'service_classification':res.service_classification,
												'service_classification_id':res.service_classification_id.id,
												'invoice_date_before':temp_id.invoice_date,
												'billing_term':res.billing_term,
												'cce':res.cce_assigned.id,
												'partner_id':res.partner_id.id,
												'contract_no':res.id,
												'cse':res.cse.id,
												'line_sequence_id':temp_id.sequence_id,
												'payment_term':res.payment_term,
												'bool_custom_payterm':res.bool_custom_payterm,
												'add_custom_payterm':res.add_custom_payterm,
												'status':'open',
												'is_ipm':res.is_ipm,
												'total_tax':res.total_tax_amt,
												# 'basic_amount':res.total_amount,
												'exempted':exempted,
												#'adhoc_invoice':res.adhoc_invoice,
												'adhoc_invoice':adhoc,
												'basic_amount':round(temp_id.amount,2), 
												# 'pending_amount':temp_id.amount,
												'fum_invoice':fum_invoice,
												'fumigant':fumigant,
												'region_of_use':region_of_use,
												# 'inv_type':res.inv_type.id,
											})
				self.pool.get('res.partner').write(cr,uid,res.partner_id.id,{'created_invoice':True})
				if create_id:
					company_name = ''
					time_cur = time.strftime("%H:%M:%S")#a
					date = datetime.now().date()#a
					con_cat ='Check_Invoice_Created'+str(date)+str(time_cur)+'.sql'#A date
					filename = os.path.expanduser('~')+'/sql_files/check_invoice_sync_old/'+con_cat
					directory_name = str(os.path.expanduser('~')+'/sql_files/check_invoice_sync_old/')
					d = os.path.dirname(directory_name)
					if not os.path.exists(d):
						os.makedirs(d)
					update_check_invoice = "\nupdate sale_contract set check_invoice = True where contract_number =  '"+str(res.contract_number)+"';"
					with open(filename,'a') as f:
						f.write(update_check_invoice)
						f.close()
				if contract_line_id:
					for val in contract_line_id:
						cust_line_obj =  self.pool.get('customer.line')
						cust_line_srch = cust_line_obj.search(cr,uid,[('customer_address','=',val.address_new.partner_address.id)])
						cse = ''
						if cust_line_srch:
							cse = cust_line_obj.browse(cr,uid,cust_line_srch[0]).cse.id
						total_id=self.pool.get('customer.line').search(cr,uid,[('customer_address','=',val.address_new.partner_address.id)])
						for get_val in self.pool.get('customer.line').browse(cr,uid,total_id):
							credit_period=get_val.credit_period
						if val.pms.prod_type== 'ipm':
							for val11 in val.ipm_one2many:
								self.pool.get('invoice.adhoc.master').write(cr,uid,create_id,{'ipm_not_ipm':True,'cse':cse if cse else res.cse.id})
								cr.commit()
								amount_ipm = 0.0
								if not val11.complimentary:
									amount_ipm = val11.amount/res.no_of_payment
									self.pool.get('invoice.adhoc').create(cr,uid,{'pms':val11.pms.id,'rate':val11.rate,'amount':amount_ipm,'area':val11.area,'unit':val11.unit,'location':val.address_new.id,'ipm_id':create_id,'credit_period':credit_period, 'cse_invoice':val.address_new.partner_address.cse.id if val.address_new.partner_address.cse else val.cse_contract.id,})
								self.pool.get('invoice.adhoc.ipm').create(cr,uid,{'pms':val11.pms.id,'rate':val11.rate,'amount':val11.amount,'area':val11.area,'unit':val11.unit,'invoice_adhoc_ipm_id':create_id})
						else:
							self.pool.get('invoice.adhoc.master').write(cr,uid,create_id,{'cse':cse if cse else res.cse.id})
				for iterate_comment in res.comment_line_o2m:
					date=datetime.now()
					self.pool.get('comment.line').create(cr,uid,{'invoice_line_id':create_id,'user_name':self.pool.get('res.users').browse(cr,uid,uid).name,'comment_date':iterate_comment.comment_date,'comment':iterate_comment.comment})
				for temp in contract_line_id:
					# if temp.contract_id12.gst_contract == False:
					address_data = temp.address_new
					addrs_items = []
					long_address = ''
					services=''	
					if address_data.apartment not in [' ',False,None]:
						addrs_items.append(address_data.apartment)
					if address_data.location_name not in [' ',False,None]:
						addrs_items.append(address_data.location_name)
					if address_data.building not in [' ',False,None]:
						addrs_items.append(address_data.building)
					if address_data.sub_area not in [' ',False,None]:
						addrs_items.append(address_data.sub_area)
					if address_data.street not in [' ',False,None]:
						addrs_items.append(address_data.street)
					if address_data.landmark not in [' ',False,None]:
						addrs_items.append(address_data.landmark)
					if address_data.city_id:
						addrs_items.append(address_data.city_id.name1)
					if address_data.district:
						addrs_items.append(address_data.district.name)
					if address_data.tehsil:
						addrs_items.append(address_data.tehsil.name)
					if address_data.state_id:
						addrs_items.append(address_data.state_id.name)
					if address_data.zip not in [' ',False,None]:
						addrs_items.append(address_data.zip)
					if len(addrs_items) > 0:
						last_item = addrs_items[-1]
						for item in addrs_items:
							if item!=last_item:
								long_address = long_address+item+','+' '
							if item==last_item:
								long_address = long_address+item
					if long_address:
						complete_address = '['+long_address+']'
					else:
						complete_address = ' '
					if temp.nature_id:
						product_full_name = temp.nature_id.name or ''
						hsn = temp.nature_id.hsn_code
						pms = None
					elif temp.pms:
						product_full_name = temp.pms.product_desc or ''
						hsn = temp.pms.hsn_sac_code
					else:
						product_full_name = ''
						hsn = ''
					services = product_full_name.upper() + ' '+complete_address
					if temp_id.amount > 0:
						amount_new=temp.estimated_contract_cost/float(res.total_amount)*temp_id.amount
						basic_amount = basic_amount + amount_new
					search_type = self.pool.get('premise.type.master').search(cr,uid,[('key','=',temp.address_new.premise_type)])
					credit_period_val=0
					if search_type:
						cust_type = self.pool.get('premise.type.master').browse(cr,uid,search_type)[0].select_type
						search_credit = self.pool.get('credit.period').search(cr,uid,[('name','=',cust_type)])
						credit_period_val = self.pool.get('credit.period').browse(cr,uid,search_credit)[0].credit_period
					new_address_data = self.pool.get('new.address').browse(cr,uid,temp.address_new.id)
					if res.service_classification not in ('exempted'):
						if not res.branch_id.state_id or not new_address_data.state_id:
							raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
						# comparing states from customer location and branch
						# case: if both states are same
						res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
						if res_users_browse:
							res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key
						if res.branch_id.state_id.id != new_address_data.state_id.id:
										raise osv.except_osv(('Alert'),("IGST Invoice cannot be created as of now!"))
						
						else:
							igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
							igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
							if igst_data.effective_from_date and igst_data.effective_to_date:
								if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
									igst_percent = igst_data.amount * 100
									igst_rate = str(igst_percent)+'%'
									igst_amt = round((amount_new*igst_percent)/100,2)
							else:
								raise osv.except_osv(('Alert'),("IGST tax not configured!"))
					total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
					adhoc_vals = {
							'location':temp.address_new.id,
							'pms':temp.pms.id,
							'rate':temp.rate,
							'invoice_adhoc_id11':create_id,
							'invoice_adhoc_id12':create_id,
							'credit_period':credit_period_val,
							'unit':temp.unit,
							'area':temp.area,
							'amount':amount_new,
							'cse_invoice':temp.address_new.partner_address.cse.id if temp.address_new.partner_address.cse else temp.cse_contract.id,
							'type_of_service':temp.type_of_service,
							'area_sq_mt':temp.area_sq_mt,
							'no_of_trees':temp.no_of_trees,
							'boolean_pms_tg':temp.boolean_pms_tg,
							'services': services, 
							'hsn_code': temp.pms.hsn_sac_code,
							'qty': temp.no_of_services,
							'discount': 0,
							'total': amount_new,
							'cgst_rate': cgst_rate,
							'cgst_amt': cgst_amt,
							'sgst_rate': sgst_rate,
							'sgst_amt': sgst_amt,
							'igst_rate': igst_rate,
							'igst_amt': igst_amt,
							'cess_rate': cess_rate,
							'cess_amt': cess_amt,						
						}
					adhoc_id = self.pool.get('invoice.adhoc').create(cr,uid,adhoc_vals)
			self.pool.get('invoice.adhoc.master').write(cr,uid,int(create_id),
				{
					'total_tax': total_tax_amt,
					'basic_amount': round(basic_amount,2),
					'grand_total_amount': round(basic_amount+total_tax_amt),
					'pending_amount': round(basic_amount+total_tax_amt)})
			if not exempted :
				self.add_invoice_tax(cr,uid,create_id,[temp_id.id])
			self.pool.get('invoice.line').write(cr,uid,temp_id.id,{'pay_check':True,'invoice_done':True,'reason':''})
			return True


	def button_push(self,cr,uid,ids,context=None):#Zeeshan 7 Jan
		#scr.execute("update sale_contract set invoice_number=%s",seq_id)
		credit_period=0
		service_classification_list = []
		partner_address_list = []
		special_status_list = []
		lot_bond_list = []
		nature_id = False
		sale_contract_obj = self.pool.get('sale.contract')
		res_company_obj = self.pool.get('res.company')
		new_address_obj = self.pool.get('new.address')
		res_partner_address_obj =self.pool.get('res.partner.address')
		o = self.browse(cr,uid,ids[0])
		invoice_line_id = o.invoice_line_id.id
		sale_contract_browse = sale_contract_obj.browse(cr,uid,invoice_line_id)
		branch_id = sale_contract_browse.branch_id.id
		service_classification = str(sale_contract_browse.service_classification)
		search_inspection_line_id = self.pool.get('inspection.costing.line').search(cr,uid,['|',('contract_id1','=',invoice_line_id),('contract_id12','=',invoice_line_id)])
		browse_inspection_line_id = self.pool.get('inspection.costing.line').browse(cr,uid,search_inspection_line_id)
		for browse_location_id in browse_inspection_line_id:
			location_id = browse_location_id.address_new.id
			partner_address = new_address_obj.browse(cr,uid,location_id).partner_address.id
			lot_bond = res_partner_address_obj.browse(cr,uid,partner_address).lot_bond
			lot_bond_list.append(lot_bond)
			partner_address_list.append(partner_address)
			if len(partner_address_list) == 1:
				query_str = "select distinct(special_status) from res_partner_address where id="+str(partner_address_list[0])
				cr.execute(query_str)
				lot_bond = res_partner_address_obj.browse(cr,uid,partner_address_list[0]).lot_bond
			elif len(partner_address_list) > 1:
				query_str_tuple = "select distinct(special_status) from res_partner_address where id in "+str(tuple(partner_address_list))
				cr.execute(query_str_tuple)
			values = cr.fetchall()
			values_id = [x[0] for x in values]
			if len(values_id) > 1 or len(values_id) == 1:
				for values_browse_id in values_id:
					if values_browse_id != None:
						browse_special_status = self.pool.get('special.status').browse(cr,uid,values_browse_id).name
						special_status_list.append(str(browse_special_status))
					if values_browse_id == None:
						special_status_list.append(None)
				if service_classification == 'sez':
					if 'SEZ' in special_status_list and None in special_status_list:
						raise osv.except_osv(('Warning !'),('All Locations must have special status as SEZ in customer location'))
					if None in special_status_list:
						raise osv.except_osv(('Warning !'),('All Locations must have special status as SEZ in customer location'))
				if service_classification == 'sez':
					if 'SEZ' in special_status_list:
						lot_bond_list = list(set(lot_bond_list))
						if len(lot_bond_list) > 1:
							raise osv.except_osv(('Alert!'),('Please Tick or Untick the lot bond for all location !'))
		if branch_id:
			branch_id_name = res_company_obj.browse(cr,uid,branch_id).government_notification
			branch_id_str = branch_id_name
			if (branch_id_str and lot_bond==True and service_classification == 'sez') or (branch_id_str and service_classification != 'sez') or (not branch_id_str and service_classification != 'sez'):
					for temp_id in self.browse(cr,uid,ids):
						total = 0.0
						basic_amount = 0.00
						amount =0.0
						tax_amount = 0.0
						list_invoice_id = []
						list_contract_id = []
						grand_total = 0.0
						temp_amount = 0.0
						amount_new=0.0
						create_id = ''
						adhoc = False
						exempted = False
						res_id=''
						invoice_created=False
						fum_invoice=False
						region_of_use=False
						fumigant=False
						cgst_rate = '0.00%'
						cgst_amt = 0.00
						sgst_rate = '0.00%'
						sgst_amt = 0.00
						igst_rate = '0.00%'
						igst_amt = 0.00
						cess_rate = '0.00%'
						cess_amt = 0.00
						total_tax_amt=0.00
						account_tax_obj = self.pool.get('account.tax')
						today_date = datetime.now().date()
						gst_select_taxes = ['cgst','sgst','utgst','igst','cess']
						gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
						if not gst_taxes:
							raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
						for res in self.pool.get('sale.contract').browse(cr,uid,[temp_id.invoice_line_id.id]):
							contract_line_id = res.contract_line_id12 if res.gst_contract else res.contract_line_id
							service_classification = str(res.service_classification)
							if res.check_invoice:
								raise osv.except_osv(('Alert!'),('Check the other server for invoice'))
							if res.id:
								res_id=res.id
								self.pool.get('sale.contract').write(cr,uid,res.id,{'create_entry_sales_msg':True,'payterm_button':True})#payterm 
								if contract_line_id:
									for j in contract_line_id:
										if not j.invoice_created:
											self.pool.get('inspection.costing.line').write(cr,uid,j.id,{'invoice_created':True})
											invoice_created=True
								if invoice_created:
									if service_classification not in ('exempted','sez'):
										self.pool.get('tax').add_tax(cr,uid,res.id,'sale.contract')
									company_name = ''
									test=False
									time_cur = time.strftime("%H:%M:%S")#a
									date = datetime.now().date()#a
									company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
									if company_id:
										company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
									#req_idd = res.request_id
									current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key #changes 22jul16
									con_cat = str(company_name)+'_'+str(current_company)+'_contract_amount'+str(date)+str(time_cur)+'.sql'#A date
									filename = os.path.expanduser('~')+'/sql_files/'+con_cat
									directory_name = str(os.path.expanduser('~')+'/sql_files/')
									d = os.path.dirname(directory_name)
									if not os.path.exists(d):
										os.makedirs(d)
									if contract_line_id:#a
										for j in contract_line_id:#a
											update_contract_amount = "\nupdate inspection_costing_line set estimated_contract_cost = '"+str(j.estimated_contract_cost)+"' where contract_id1 = (select id from sale_contract where contract_number = '"+str(res.contract_number)+"' ) and pms =(select id from product_product where name_template ilike  '"+str(j.pms.name)+"' );"
									with open(filename,'a') as f:
										f.write(update_contract_amount)
										f.close()
							amount = round(temp_id.amount)
							if res.exempted or res.service_classification == 'exempted' or res.service_classification == 'sez':
								exempted=True
							if res.fum_contract == True:
								fum_invoice=True,
								fumigant=res.fumigant
								region_of_use=res.region_of_use
							create_id = self.pool.get('invoice.adhoc.master').create(cr,uid,
														{
															'gst_invoice': True,
															'cust_name':res.cust_name,
															'service_classification':res.service_classification,
															'service_classification_id':res.service_classification_id.id,
															'invoice_date_before':temp_id.invoice_date,
															'billing_term':res.billing_term,
															'cce':res.cce_assigned.id,
															'partner_id':res.partner_id.id,
															'contract_no':res.id,
															'cse':res.cse.id,
															'line_sequence_id':temp_id.sequence_id,
															'payment_term':res.payment_term,
															'bool_custom_payterm':res.bool_custom_payterm,
															'add_custom_payterm':res.add_custom_payterm,
															'status':'open',
															'is_ipm':res.is_ipm,
															'total_tax':res.total_tax_amt,
															# 'basic_amount':res.total_amount,
															'exempted':exempted,
															#'adhoc_invoice':res.adhoc_invoice,
															'adhoc_invoice':adhoc,
															'basic_amount':round(temp_id.amount,2), 
															# 'pending_amount':temp_id.amount,
															'fum_invoice':fum_invoice,
															'fumigant':fumigant,
															'region_of_use':region_of_use,
															# 'inv_type':res.inv_type.id,
														})
							self.pool.get('res.partner').write(cr,uid,res.partner_id.id,{'created_invoice':True})
							if create_id:
								company_name = ''
								time_cur = time.strftime("%H:%M:%S")#a
								date = datetime.now().date()#a
								con_cat ='Check_Invoice_Created'+str(date)+str(time_cur)+'.sql'#A date
								filename = os.path.expanduser('~')+'/sql_files/check_invoice_sync_old/'+con_cat
								directory_name = str(os.path.expanduser('~')+'/sql_files/check_invoice_sync_old/')
								d = os.path.dirname(directory_name)
								if not os.path.exists(d):
									os.makedirs(d)
								update_check_invoice = "\nupdate sale_contract set check_invoice = True where contract_number =  '"+str(res.contract_number)+"';"
								with open(filename,'a') as f:
									f.write(update_check_invoice)
									f.close()
							if contract_line_id:
								for val in contract_line_id:
									cust_line_obj =  self.pool.get('customer.line')
									cust_line_srch = cust_line_obj.search(cr,uid,[('customer_address','=',val.address_new.partner_address.id)])
									cse = ''
									if cust_line_srch:
										cse = cust_line_obj.browse(cr,uid,cust_line_srch[0]).cse.id
									total_id=self.pool.get('customer.line').search(cr,uid,[('customer_address','=',val.address_new.partner_address.id)])
									for get_val in self.pool.get('customer.line').browse(cr,uid,total_id):
										credit_period=get_val.credit_period
									if val.pms.prod_type== 'ipm':
										for val11 in val.ipm_one2many:
											self.pool.get('invoice.adhoc.master').write(cr,uid,create_id,{'ipm_not_ipm':True,'cse':cse if cse else res.cse.id})
											cr.commit()
											amount_ipm = 0.0
											if not val11.complimentary:
												amount_ipm = val11.amount/res.no_of_payment
												self.pool.get('invoice.adhoc').create(cr,uid,{'pms':val11.pms.id,'rate':val11.rate,'amount':amount_ipm,'area':val11.area,'unit':val11.unit,'location':val.address_new.id,'ipm_id':create_id,'credit_period':credit_period, 'cse_invoice':val.address_new.partner_address.cse.id if val.address_new.partner_address.cse else val.cse_contract.id,})
											self.pool.get('invoice.adhoc.ipm').create(cr,uid,{'pms':val11.pms.id,'rate':val11.rate,'amount':val11.amount,'area':val11.area,'unit':val11.unit,'invoice_adhoc_ipm_id':create_id})
									else:
										self.pool.get('invoice.adhoc.master').write(cr,uid,create_id,{'cse':cse if cse else res.cse.id})
							for iterate_comment in res.comment_line_o2m:
								date=datetime.now()
								self.pool.get('comment.line').create(cr,uid,{'invoice_line_id':create_id,'user_name':self.pool.get('res.users').browse(cr,uid,uid).name,'comment_date':iterate_comment.comment_date,'comment':iterate_comment.comment})
							for temp in contract_line_id:
								# if temp.contract_id12.gst_contract == False:

								address_data = temp.address_new
								addrs_items = []
								long_address = ''
								services=''	
								if address_data.apartment not in [' ',False,None]:
									addrs_items.append(address_data.apartment)
								if address_data.location_name not in [' ',False,None]:
									addrs_items.append(address_data.location_name)
								if address_data.building not in [' ',False,None]:
									addrs_items.append(address_data.building)
								if address_data.sub_area not in [' ',False,None]:
									addrs_items.append(address_data.sub_area)
								if address_data.street not in [' ',False,None]:
									addrs_items.append(address_data.street)
								if address_data.landmark not in [' ',False,None]:
									addrs_items.append(address_data.landmark)
								if address_data.city_id:
									addrs_items.append(address_data.city_id.name1)
								if address_data.district:
									addrs_items.append(address_data.district.name)
								if address_data.tehsil:
									addrs_items.append(address_data.tehsil.name)
								if address_data.state_id:
									addrs_items.append(address_data.state_id.name)
								if address_data.zip not in [' ',False,None]:
									addrs_items.append(address_data.zip)
								if len(addrs_items) > 0:
									last_item = addrs_items[-1]
									for item in addrs_items:
										if item!=last_item:
											long_address = long_address+item+','+' '
										if item==last_item:
											long_address = long_address+item
								if long_address:
									complete_address = '['+long_address+']'
								else:
									complete_address = ' '
								if temp.nature_id:
									product_full_name = temp.nature_id.name or ''
									hsn = temp.nature_id.hsn_code
									pms = None
									nature_id = temp.nature_id.id
								elif temp.pms:
									product_full_name = temp.pms.product_desc or ''
									hsn = temp.pms.hsn_sac_code
									pms = temp.pms.id
								else:
									product_full_name = ''
									hsn = ''
									pms = None
								services = product_full_name.upper() + ' '+complete_address
								if temp_id.amount > 0:
									amount_new=temp.estimated_contract_cost/float(res.total_amount)*temp_id.amount
									basic_amount = basic_amount + amount_new
								search_type = self.pool.get('premise.type.master').search(cr,uid,[('key','=',temp.address_new.premise_type)])
								credit_period_val=0
								if search_type:
									cust_type = self.pool.get('premise.type.master').browse(cr,uid,search_type)[0].select_type
									search_credit = self.pool.get('credit.period').search(cr,uid,[('name','=',cust_type)])
									credit_period_val = self.pool.get('credit.period').browse(cr,uid,search_credit)[0].credit_period
								new_address_data = self.pool.get('new.address').browse(cr,uid,temp.address_new.id)
								if res.service_classification not in ('exempted','sez'):
									if not res.branch_id.state_id or not new_address_data.state_id:
										raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
									# comparing states from customer location and branch
									# case: if both states are same
									res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
									if res_users_browse:
										res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key
										if str(res_company_pcof) not in ('P200','P371') and not res.partner_id.igst_check:
												if res.branch_id.state_id.id != new_address_data.state_id.id:
													raise osv.except_osv(('Alert'),("IGST Invoice cannot be created as of now!"))
									if res.branch_id.state_id.id == new_address_data.state_id.id:
										# cgst calculation
										cgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cgst')])
										cgst_data = account_tax_obj.browse(cr,uid,cgst_id[0])
										if cgst_data.effective_from_date and cgst_data.effective_to_date:
											if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
												cgst_percent = cgst_data.amount * 100
												cgst_rate = str(cgst_percent)+'%'
												cgst_amt = round((amount_new*cgst_percent)/100,2)
										else:
											raise osv.except_osv(('Alert'),("CGST tax not configured!"))
										# sgst/utgst calculation
										# case: if state is a union_territory
										if new_address_data.state_id.union_territory:
											utgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','utgst')])
											ut_data = account_tax_obj.browse(cr,uid,utgst_id[0])
											if ut_data.effective_from_date and ut_data.effective_to_date:
												if str(today_date) >= ut_data.effective_from_date and str(today_date) <= ut_data.effective_to_date:
													utgst_percent = ut_data.amount * 100
													sgst_rate = str(utgst_percent)+'%'
													sgst_amt = round((amount_new*utgst_percent)/100,2)
											else:
												raise osv.except_osv(('Alert'),("UTGST tax not configured!"))
										# case: if state is not a union_territory
										else:
											sgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','sgst')])
											st_data = account_tax_obj.browse(cr,uid,sgst_id[0])
											if st_data.effective_from_date and st_data.effective_to_date:
												if str(today_date) >= st_data.effective_from_date and str(today_date) <= st_data.effective_to_date:
													sgst_percent = st_data.amount * 100
													sgst_rate = str(sgst_percent)+'%'
													sgst_amt = round((amount_new*sgst_percent)/100,2)
											else:
												raise osv.except_osv(('Alert'),("SGST tax not configured!"))
									# case: if both states are different
									else:
										igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
										igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
										if igst_data.effective_from_date and igst_data.effective_to_date:
											if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
												igst_percent = igst_data.amount * 100
												igst_rate = str(igst_percent)+'%'
												igst_amt = round((amount_new*igst_percent)/100,2)
										else:
											raise osv.except_osv(('Alert'),("IGST tax not configured!"))
									# cess calculation
									cess_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cess')])
									if cess_id:
										cess_data = account_tax_obj.browse(cr,uid,cess_id[0])
										if cess_data.effective_from_date and cess_data.effective_to_date:
											if str(today_date) >= cess_data.effective_from_date and str(today_date) <= cess_data.effective_to_date:								
												cess_percent = cess_data.amount * 100
												cess_rate = str(cess_percent)+'%'
												cess_amt = round((amount_new*cess_percent)/100,2)
								total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
								res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
								if res_users_browse:
									res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key	
								if str(res_company_pcof) not in ('P200','P371') and not res.partner_id.igst_check:	
									if igst_amt > 0:
										raise osv.except_osv(('Alert'),("IGST Invoice cannot be created as of now!"))
								adhoc_vals = {
										'services': services,
										'pms': pms, 
										'hsn_code': hsn,
										'nature_id': nature_id,
										'location': temp.address_new.id,
										'rate': temp.rate,
										'invoice_adhoc_id11': create_id,
										'invoice_adhoc_id12': create_id,
										'credit_period': credit_period_val,
										'unit': temp.unit,
										'area': temp.area,
										'amount': amount_new,
										'cse_invoice': temp.address_new.partner_address.cse.id if temp.address_new.partner_address.cse else temp.cse_contract.id,
										'type_of_service': temp.type_of_service,
										'area_sq_mt': temp.area_sq_mt,
										'no_of_trees': temp.no_of_trees,
										'boolean_pms_tg': temp.boolean_pms_tg,
										'hsn_code': temp.pms.hsn_sac_code,
										'qty': temp.no_of_services,
										'discount': 0,
										'total': amount_new,
										'cgst_rate': cgst_rate,
										'cgst_amt': cgst_amt,
										'sgst_rate': sgst_rate,
										'sgst_amt': sgst_amt,
										'igst_rate': igst_rate,
										'igst_amt': igst_amt,
										'cess_rate': cess_rate,
										'cess_amt': cess_amt				
									}
								adhoc_id = self.pool.get('invoice.adhoc').create(cr,uid,adhoc_vals)
						self.pool.get('invoice.adhoc.master').write(cr,uid,int(create_id),
							{
								'total_tax': total_tax_amt,
								'basic_amount': round(basic_amount,2),
								'grand_total_amount': round(basic_amount+total_tax_amt),
								'pending_amount': round(basic_amount+total_tax_amt)})
						# if not exempted :
						self.pool.get('invoice.tax.rate').add_tax(cr,uid,create_id)
						self.pool.get('invoice.line').write(cr,uid,temp_id.id,{'pay_check':True,'invoice_done':True,'reason':''})
						return{
										'type': 'ir.actions.act_window',
										'name':'Contract',
										'view_type': 'form',
										'view_mode': 'form',
										'res_model': 'sale.contract',
										'res_id': res_id,
										'view_id': False,
										'target': 'current',	
										'context': context,
									}

			elif not branch_id_str and service_classification == 'sez' or lot_bond == False:
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr,uid,'gst_accounting','invoice_push_notification_form_view')
				context.update({'invoice_form_id_form':ids[0],'model':'invoice.line'})
				return {
					'type': 'ir.actions.act_window',
					'name': 'Notification',
					'view_mode': 'form',
					'view_type': 'form',
					'view_id': form_view[1],
					# 'res_id': '',
					'res_model': 'invoice.push.notification',
					'target': 'new',
					'context':context
			}					

invoice_line()
class campaign(osv.osv):
	_name='campaign'
	_columns = {
		'name':fields.char('Name',size=300),
	}
campaign()

# class invoice_type(osv.osv):
# 	_name='invoice.type'
# 	_columns = {
# 		'name':fields.char('Name',size=300),
# 	}
# invoice_type()

class invoice_push_notification(osv.osv):
	_name='invoice.push.notification'
	_columns = {
		'push_text':fields.text('Name',size=300),
	}

	def _get_push_text(self, cr, uid, ids, context=None):
		text = "Government Bond is not available for SEZ location and hence IGST 18.00% will be charged. Do you want to generate invoice?"
		return text

	_defaults ={
		'push_text' : _get_push_text,
	}

	def push_confirm(self,cr,uid,ids,context=None):
		print "ssssssssssssssssssss",context
		if context.has_key('sale_contract_id_form') or context.has_key('invoice_form_id_form'):
			if context.has_key('sale_contract_id_form'):
				sale_contract_id_key = context.get('sale_contract_id_form')
				model_key = 'sale.contract'
				self.pool.get('sale.contract').government_notification_igst(cr,uid,[sale_contract_id_key])
			if context.has_key('invoice_form_id_form'):
				invoice_line_id_key = context.get('invoice_form_id_form')
				model_key = context.get('model')
				self.pool.get('invoice.line').button_push_igst(cr,uid,[invoice_line_id_key])
				sale_contract_id_key = self.pool.get('invoice.line').browse(cr,uid,invoice_line_id_key).invoice_line_id.id
			return {
						'type': 'ir.actions.act_window',
						'name': 'Contract',
						'view_mode': 'form',
						'view_type': 'form',
						'view_id': False,
						'res_id': sale_contract_id_key,
						'res_model': 'sale.contract',
						'target': 'current',
					}
		elif context.has_key('quotation_form_id_form') and context.has_key('sale_igst_check') != True:
			quotation_line_id_key = context.get('quotation_form_id_form')
			igst_check = context.get('igst_check')
			igst_continue_check = context.get('igst_continue_check')
			if igst_check == True:
				self.pool.get('inspection.costing').igst_direct_push(cr,uid,[quotation_line_id_key],context)
			if igst_continue_check == True:
				self.pool.get('inspection.wizard').igst_continue_line(cr,uid,[quotation_line_id_key],context)
			if context.has_key('line_id1'):
				line_id1 = context.get('line_id1')
			# sale_contract_id_key = self.pool.get('invoice.line').browse(cr,uid,quotation_line_id_key).invoice_line_id.id
			return{
													'type': 'ir.actions.act_window',
													'name':'Quotation',
													'view_type': 'form',
													'view_mode': 'form',
													'res_model': 'sale.quotation',
											 	'res_id':line_id1,
													'view_id':False,
													'target':'current',
												
											}
		elif context.has_key('sale_form_id_form'):
			sale_form_id_form = context.get('sale_form_id_form')
			self.pool.get('sale.quotation').create_igst_contract(cr,uid,[sale_form_id_form],context)
			if context.has_key('value_id'):
				value_id = context.get('value_id')
			return{
								'type': 'ir.actions.act_window',
								'name':'Contract',
								'view_type': 'form',
								'view_mode': 'form',
								'res_model': 'sale.contract',
								'res_id':value_id,
								#'res_id':val,
								'view_id':False,
								'target':'current',	
								'context': context,
						}             

	def cancel(self,cr,uid,ids,context=None):
		return {'type': 'ir.actions.act_window_close'}
	

invoice_push_notification()
