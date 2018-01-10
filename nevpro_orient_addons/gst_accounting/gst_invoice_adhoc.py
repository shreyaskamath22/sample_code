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
from datetime import date,datetime, timedelta


from calendar import monthrange
from osv import osv,fields
from datetime import date,datetime, timedelta
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
from dateutil.relativedelta import relativedelta
import calendar
import xmlrpclib
import re
import time
from base.res import res_partner
from datetime import datetime
import decimal_precision as dp
import os
import sys
from lxml import etree
from openerp.osv.orm import setup_modifiers
from tools.translate import _


class invoice_adhoc(osv.osv):
	_inherit = 'invoice.adhoc'

	_columns = {
		'services':fields.text('Services',size=1000),
		'hsn_code':fields.char('HSN/SAC Code',size=8),
		'qty':fields.integer('Qty.'),
		'discount':fields.float('Discount'),
		'total':fields.float('Total'),
		'cgst_rate':fields.char('CGST Rt',size=10),
		'cgst_amt':fields.float('CGST Amt',size=10),
		'sgst_rate':fields.char('SGST Rt',size=10),
		'sgst_amt':fields.float('SGST Amt',size=10),
		'igst_rate':fields.char('IGST Rt',size=10),
		'igst_amt':fields.float('IGST Amt',size=10),    
		'cess_rate':fields.char('CESS Rt',size=10),
		'cess_amt':fields.float('CESS Amt',size=10),
		'invoice_adhoc_id12':fields.many2one('invoice.adhoc.master','invoice_adhoc_id12'),
		'invoice_adhoc_id_gst':fields.many2one('invoice.adhoc.master','invoice_adhoc_id_gst'),
		'sales_receipt_id':fields.many2one('account.sales.receipts','Receipt'), 
		'unit':fields.selection([('sqr_ft','Sq.ft'),('nos','NOs'),('sqr_mt','Sq.Mt'),('running_mt','Running Mtr')],'Unit'),
		'nature_id':fields.many2one('nature.nature','Nature')
	}

	def onchange_adhoc_pms(self, cr, uid, ids, location_invoice, pms, context=None):
		data = {}
		if location_invoice and pms:
			address_data =  self.pool.get('res.partner.address').browse(cr,uid,location_invoice)
			product_data = self.pool.get('product.product').browse(cr,uid,pms)
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
			product_full_name = product_data.product_desc or ''
			services = product_full_name.upper() + ' '+complete_address
			hsn_code = product_data.hsn_sac_code
			data.update(
				{
					'services': services,
					'hsn_code': hsn_code
				})
		return {'value':data}


	def onchange_adhoc_location_invoice(self, cr, uid, ids, location_invoice, pms, context=None):
		data = {}
		if location_invoice and pms:
			address_data =  self.pool.get('res.partner.address').browse(cr,uid,location_invoice)
			product_data = self.pool.get('product.product').browse(cr,uid,pms)
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
			product_full_name = product_data.product_desc or ''
			services = product_full_name.upper() + ' '+complete_address
			data.update(
				{
					'services': services
				})
		return {'value':data}


	def onchange_adhoc_area(self, cr, uid, ids, qty, rate, area, context=None):
		data = {}
		if rate and area:		
			rateqty = rate*qty
			total = rateqty*float(area)
			data.update(
				{
					'total': round(total),
					'amount': round(total)
				})
		return {'value':data}


invoice_adhoc()


class invoice_adhoc_master(osv.osv):
	_inherit = 'invoice.adhoc.master'
	_order = 'invoice_date desc'

	_columns = {
		'gst_invoice': fields.boolean('GST Invoice?'),
		'adv_receipt_amount':fields.float('Advance Received',size=100),
		'net_amount_payable':fields.float('Net Payable Amount',size=100),
		'invoice_line_adhoc_12':fields.one2many('invoice.adhoc','invoice_adhoc_id12','invoice line adhoc'),
		'invoice_line_adhoc_gst':fields.one2many('invoice.adhoc','invoice_adhoc_id_gst','GST adhoc Invoice lines'),
		'advance_receipts': fields.char('Advance Receipts',size=1000),
		'report_type':fields.selection([
						('original','Original for Recipient'),
						('duplicate','Duplicate for Supplier')],
						'Report Type'),
		'allow_narration': fields.boolean('Print Narration'),
		'gst_adhoc': fields.boolean('GST Adhoc?'),
		'invoice_number_ncs': fields.char('Invoice Number NCS', size=100),
		'service_classification':fields.selection([
						('residential','Residential Service'),
						('commercial','Commercial Service'),
						('port','Port Service'),
						('airport','Airport Service'),
						('exempted','Exempted'),
						('sez','SEZ - ZERO RATED'),
						],'Service Classification *'),
		'service_classification_id':fields.many2one('service.classification','Service Classification'),
		# 'advanced_arrears': fields.boolean('Advanced/Arrears'),
		# 'visit_triggered': fields.boolean('Visit Triggered/Visit Triggered Monthly'),
		# 'inv_type':fields.many2one('invoice.type','Invoice Type'),
		'round_off_val':fields.float('Round off'),
	}

	_defaults = {
		'report_type':'original',
		# 'advanced_arrears':False,
		# 'visit_triggered':False,
	}

	# def onchange_contract_no(self, cr, uid, ids, contract_no, context=None):
	# 	data = {}
	# 	if contract_no:		
	# 		contract_number = self.pool.get('sale.contract').browse(cr,uid,contract_no)
	# 		inv_type=contract_number.inv_type.id
	# 		data.update(
	# 			{
	# 				'inv_type': inv_type
	# 			})
	# 	return {'value':data}

	def generate_invoice(self,cr,uid,ids,context=None):
		sales_rcp_obj = self.pool.get('account.sales.receipts')
		sales_rcp_line_obj = self.pool.get('account.sales.receipts.line')
		inv_adv_rcp_obj = self.pool.get('invoice.advance.receipts')
		inv_adv_rcp_line_obj = self.pool.get('invoice.advance.receipts.line')
		inv_obj = self.pool.get('invoice.adhoc.master')
		inv_adhoc_obj = self.pool.get('invoice.adhoc')
		adv_sales_obj = self.pool.get('advance.sales.receipts')
		premise_obj = self.pool.get('premise.type.master')
		inv_data = self.browse(cr,uid,ids[0])
		partner_id = inv_data.partner_id.id
		pms_list=[]
		if inv_data.gst_adhoc == True:
			self.adhoc_invoice_process(cr,uid,ids,context=None)
		# premise_type = inv_data.partner_id.premise_type
		# premise_id = premise_obj.search(cr,uid,[('key','=',inv_data.partner_id.premise_type)])
		# premise_data = premise_obj.browse(cr,uid,premise_id[0])
		# if premise_data.select_type == 'cbu' and not inv_data.partner_id.gst_no:
		# 	raise osv.except_osv(('Alert'),('Please enter the GST No. for the customer!'))
		# elif premise_data.select_type == 'rbu' and premise_data.key == 'co_operative_housing_society' and not inv_data.partner_id.gst_no:
		# 	raise osv.except_osv(('Alert'),('Please enter the GST No. for the customer!'))
		# inv_data.adhoc_invoice == True:
		# 	inv_adhoc_id = inv_adhoc_obj.search(cr,uid,[('invoice_adhoc_id_gst','=',inv_data.id)])
		# 	inv_adhoc_data = inv_adhoc_obj.browse(cr,uid,inv_adhoc_id[0])
		# 	premise_id = premise_obj.search(cr,uid,[('key','=',inv_adhoc_data.location_invoice.premise_type)])
		# 	premise_data = premise_obj.browse(cr,uid,premise_id[0])
		# 	if premise_data.select_type == 'cbu' and not inv_adhoc_data.location_invoice.partner_address.gst_no:
		# 		raise osv.except_osv(('Alert'),('Please enter the GST No. for the location'))
		# else:
		# 	inv_adhoc_id = inv_adhoc_obj.search(cr,uid,[('invoice_line_adhoc_12','=',inv_data.id)])
		# 	inv_adhoc_data = inv_adhoc_obj.browse(cr,uid,inv_adhoc_id[0])
		# 	premise_id = premise_obj.search(cr,uid,[('key','=',inv_adhoc_data.location.premise_type)])
		# 	premise_data = premise_obj.browse(cr,uid,premise_id[0])
		# 	if premise_data.select_type == 'cbu' and not inv_adhoc_data.location_invoice.partner_address.gst_no:
		# 		raise osv.except_osv(('Alert'),('Please enter the GST No. for the location'))
		if not inv_data.invoice_number_old or inv_data.invoice_number_old==None:
			if not inv_data.partner_id.gst_no:
				raise osv.except_osv(('Alert'),('Please enter the GST No. for the customer!'))
			if not inv_data.contract_no:
				raise osv.except_osv(('Alert'),('Please select Contract Number.'))
		if not inv_data.invoice_period_from and not inv_data.invoice_period_to:
			raise osv.except_osv(('Alert'),('Please enter Invoice Period Dates!'))
		if not inv_data.invoice_period_from:
			raise osv.except_osv(('Alert'),('Please enter Invoice Period from date.'))
		if not inv_data.invoice_period_to:
			raise osv.except_osv(('Alert'),('Please enter Invoice Period to date.'))
		if inv_data.service_classification in ('airport','port'):
			raise osv.except_osv(('Alert!'),('Airport/Port service classification cannot be selected as of now!'))
		# if not inv_data.invoice_number_old or inv_data.invoice_number_old==None:
		# 	if inv_data.advanced_arrears and inv_data.visit_triggered:
		# 		raise osv.except_osv(('Alert'),('Please select either Advanced Arrears or Visit Triggered checkbox!'))
		# 	if inv_data.advanced_arrears!=True and inv_data.visit_triggered!=True:
		# 		raise osv.except_osv(('Alert'),('Please select either Advanced Arrears or Visit Triggered checkbox!'))
		
		# if inv_data.invoice_line_adhoc:
		# 	for x in inv_data.invoice_line_adhoc:
		# 		self.pool.get('invoice.adhoc').write(cr,uid,x.id,{'invoice_adhoc_id_gst':inv_data.id})
		# 	for vals in inv_data.invoice_line_adhoc:
		# 		if inv_data.contract_no:
		# 			contract_line_id = inv_data.contract_no.contract_line_id if inv_data.contract_no.contract_line_id else inv_data.contract_no.contract_line_id12
		# 			for pms in contract_line_id:
		# 				pms_list.append(pms.pms.id)
		# 	for vals in inv_data.invoice_line_adhoc:
		# 		if vals.pms.id==False:
		# 			raise osv.except_osv(('Alert'),('Please Enter PMS!'))
		# 		if vals.pms.id not in pms_list:
		# 			raise osv.except_osv(('Alert'),('Please Enter PMS which is selected in the contract!'))
		# 		if vals.rate==False:
		# 			raise osv.except_osv(('Alert'),('Please Enter Rate!'))
		# 		if vals.area==False:
		# 			raise osv.except_osv(('Alert'),('Please Enter Area!'))
		# 	if not inv_data.total_amount:
		# 		raise osv.except_osv(('Alert'),('Please Enter Amount'))
		self.pool.get('res.partner').write(cr,uid,partner_id,{'gst_created_invoice':True})
		list_id = inv_obj.search(cr,uid,[('contract_no','=',inv_data.contract_no.id),('invoice_number','!=',False)])
		# temp_amount = 0.0
		if list_id:
			# for iter_val in inv_obj.browse(cr,uid,list_id):
			# 	temp_amount += iter_val.grand_total_amount
			if inv_data.contract_no.id!=False:
				if str(inv_data.invoice_period_from)<(inv_data.contract_no.contract_start_date):
					raise osv.except_osv(('Alert'),('Invoice Period from date cannot be less than contract start date'))
				if str(inv_data.invoice_period_to)<(inv_data.contract_no.contract_start_date):
					raise osv.except_osv(('Alert'),('Invoice Period to date cannot be less than contract start date'))
				# self.pool.get('sale.contract').write(cr,uid,inv_data.contract_no.id,{'invoice_value':temp_amount})
		if str(inv_data.invoice_period_to) < str(inv_data.invoice_period_from):
			raise osv.except_osv(('Alert'),('Invoice Period To date cannot be less than Invoice Period To date'))
		if inv_data.gst_adhoc!=True and inv_data.total_amount==0.0:
			raise osv.except_osv(('Alert'),('Total Amount cannot be zero!')) 
		adv_rcp_ids = []
		rcp_ids = sales_rcp_obj.search(cr,uid,[('customer_name','=',inv_data.partner_id.id),('state','=','done'),('advance_pending','!=',0),('receipt_date','>=','2017-07-01'),('gst_receipt','=',True)])
		for rcp_id in rcp_ids:
			sales_rcp_data = sales_rcp_obj.browse(cr,uid,rcp_id)
			for rcp_line in sales_rcp_data.sales_receipts_one2many:
				if rcp_line.account_id.account_selection == 'advance':
					adv_rcp_ids.append(rcp_id)
		if adv_rcp_ids:
			models_data = self.pool.get('ir.model.data')
			form_view = models_data.get_object_reference(cr, uid, 'gst_accounting', 'invoice_advance_receipts_form')
			res_create_id = inv_adv_rcp_obj.create(cr, uid, {'invoice_id':ids[0]}, context=context)
			for adv_rcp_id in adv_rcp_ids:
				receipt_data = sales_rcp_obj.browse(cr,uid,adv_rcp_id)
				recp_line_id = sales_rcp_line_obj.search(cr,uid,[('receipt_id','=',receipt_data.id),('type','=','credit'),('acc_status','=','advance')])
				if recp_line_id!=[]:
					adv_sales_id = adv_sales_obj.search(cr,uid,[('advance_id','=',recp_line_id[0])])
					adv_sales_data = adv_sales_obj.browse(cr,uid,adv_sales_id[0])
					inv_adv_rcp_line_vals = {
						'in_adv_rep_id': res_create_id,
						'receipt_id': receipt_data.id,
						'partner_id': receipt_data.customer_name.id,
						'receipt_date': receipt_data.receipt_date,
						'cse': adv_sales_data.cse.id,
						'advance_pending': receipt_data.advance_pending
					}
					inv_adv_rcp_line_obj.create(cr,uid,inv_adv_rcp_line_vals)
			return {
				'name': _('Advance Receipts'),
				'type': 'ir.actions.act_window',
				'view_id': False,
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'invoice.advance.receipts',
				'target' : 'new',
				'res_id': res_create_id,
				'views': [(form_view and form_view[1] or False,'form'),(False, 'calendar'),(False, 'graph')],
				'domain': '[]',
				'nodestroy': True,
		}
		else:
			self.generate_invoice_main(cr,uid,ids,context=context)

######### view for gst Invoice#######################
	def view_invoice(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			cr.execute("update invoice_receipt_history c set receipt_number =a.receipt_no , amount_receipt = b.credit_amount \
				from account_sales_receipts a ,\
				account_sales_receipts_line b,\
				invoice_adhoc_master d \
				where b.id=c.receipt_id_history \
				and a.id=b.receipt_id \
				and d.id=c.invoice_receipt_history_id \
				--and c.receipt_number is Null \
				and c.invoice_writeoff_date is Null \
				and d.id = %s "%(res.id))
			
			cr.execute("update invoice_receipt_history c set receipt_number =a.credit_note_no , amount_receipt = b.credit_amount \
				from credit_note a ,\
				credit_note_line b,\
				invoice_adhoc_master d \
				where b.id=c.credit_id_history \
				and a.id=b.credit_id \
				and d.id=c.invoice_receipt_history_id \
				--and c.receipt_number is Null \
				and c.invoice_writeoff_date is not Null \
				and d.id = %s "%(res.id))		
			
			cr.execute("update invoice_receipt_history c set receipt_number =a.credit_note_no , amount_receipt = b.credit_amount \
				from credit_note a ,\
				credit_note_line b,\
				invoice_adhoc_master d \
				where b.id=c.credit_note_itds_history_id \
				and a.id=b.credit_id \
				and d.id=c.invoice_receipt_history_id \
				--and c.receipt_number is Null \
				and c.invoice_writeoff_date is not Null \
				and d.id = %s "%(res.id))
				
			cr.execute("update invoice_receipt_history c set receipt_number =a.credit_note_no , amount_receipt = b.credit_amount \
				from credit_note_st a ,\
				credit_note_line_st b,\
				invoice_adhoc_master d \
				where b.id=c.credit_st_id_history \
				and a.id=b.credit_st_id \
				and d.id=c.invoice_receipt_history_id \
				--and c.receipt_number is Null \
				and c.invoice_writeoff_date is not Null \
				and d.id = %s "%(res.id))	
			
			cr.execute("update invoice_receipt_history c set receipt_number =a.jv_number , amount_receipt = b.credit_amount \
				from account_journal_voucher a ,\
				account_journal_voucher_line b,\
				invoice_adhoc_master d \
				where b.id=c.jv_id_history \
				and a.id=b.journal_voucher_id \
				and d.id=c.invoice_receipt_history_id \
				--and c.receipt_number is Null \
				and c.invoice_writeoff_date is not Null \
				and d.id = %s "%(res.id))		
				
			cr.execute("update invoice_receipt_history c set receipt_number =a.jv_number , amount_receipt = b.credit_amount \
				from account_journal_voucher a ,\
				account_journal_voucher_line b,\
				invoice_adhoc_master d \
				where b.id=c.jv_invoice_id_history \
				and a.id=b.journal_voucher_id \
				and d.id=c.invoice_receipt_history_id \
				--and c.receipt_number is Null \
				and c.invoice_writeoff_date is not Null \
				and d.id = %s "%(res.id))
			
			#############################################################################
			
			if res.adhoc_invoice == True:
				name = "Adhoc Invoice"
			else :
				name = "Invoice"
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'gst_accounting', 'invoice_adhoc_id_gst_inherit')
			return{
						'type': 'ir.actions.act_window',
						'name':name,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'invoice.adhoc.master',
						'res_id':ids[0],
						'view_id':form_view[1],
						'target':'current',	
						'context': context,
						}

	def generate_invoice_main_igst(self,cr,uid,ids,seq_id,context=None):
		line_sequence_id = []
		seq_id =seq_id
		payterm_obj = self.pool.get('invoice.line')
		lst=[]
		l1=[]
		l2=[]
		myString = ''
		today_date = datetime.now().date()
		year = today_date.year
		year1 = today_date.strftime('%y')
		pms_lst = ""
		invoice_date = False
		pcof_key = invoice_id = temp_count = start_year = end_year = total_cp=''
		seq = count = 0
		for res in self.browse(cr,uid,ids):
			if res.gst_invoice!=True or res.gst_invoice==False or res.gst_invoice==None:
				line_sequence_id_pay = str(res.line_sequence_id)
				line_sequence_id = payterm_obj.search(cr,uid,[('sequence_id','=',line_sequence_id_pay)])
				cgst_rate = '0.00%'
				cgst_amt = 0.00
				sgst_rate = '0.00%'
				sgst_amt = 0.00
				igst_rate = '0.00%'
				igst_amt = 0.00
				cess_rate = '0.00%'
				cess_amt = 0.00
				amount_new=0.0
				basic_amount = 0.0
				total_tax_amt = 0.0
				grand_total_amount = 0.0
				account_tax_obj = self.pool.get('account.tax')
				today_date = datetime.now().date()
				gst_select_taxes = ['igst']
				gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
				if not gst_taxes:
					raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
				if res.invoice_line_adhoc_11:
					for i in res.invoice_line_adhoc_11:
						address_data = i.location
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
						self.pool.get('invoice.adhoc').write(cr,uid,i.id,
						{
							'services': services,
							'hsn_code': i.pms.hsn_sac_code,
							'discount': 0,
							'location':i.location.id,
							'pms':i.pms.id,
							'rate':i.rate,
							'area':i.area,
							'amount':i.amount,
							'total':i.amount,
							'cse_invoice':res.cse.id,
						})
					basic_amount = 0.0
					total_tax_amt = 0.0
					grand_total_amount = 0.0
					for i in res.invoice_line_adhoc_11:				
						new_address_data = self.pool.get('new.address').browse(cr,uid,i.location.id)
						if res.service_classification != 'exempted':
							if not res.branch_id.state_id or not new_address_data.state_id:
								raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
							else:
								igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
								igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
								if igst_data.effective_from_date and igst_data.effective_to_date:
									if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
										igst_percent = igst_data.amount * 100
										igst_rate = str(igst_percent)+'%'
										igst_amt = round((i.amount*igst_percent)/100,2)
								else:
									raise osv.except_osv(('Alert'),("IGST tax not configured!"))
						self.pool.get('invoice.adhoc').write(cr,uid,i.id,
							{
								# 'type_of_service':i.type_of_service,
								'invoice_adhoc_id11':res.id,
								'invoice_adhoc_id12':res.id,
								# 'area_sq_mt':i.area_sq_mt,
								# 'no_of_trees':i.no_of_trees,
								# 'boolean_pms_tg':i.boolean_pms_tg,
								# 'services': services, 
								'hsn_code': i.pms.hsn_sac_code,
								# 'qty': i.no_of_services,
								'discount': 0,
								'cgst_rate': cgst_rate,
								'cgst_amt': cgst_amt,
								'sgst_rate': sgst_rate,
								'sgst_amt': sgst_amt,
								'igst_rate': igst_rate,
								'igst_amt': igst_amt,
								'cess_rate': cess_rate,
								'cess_amt': cess_amt,			
							})
				self.write(cr,uid,res.id,{'gst_invoice':True})
		for res in self.browse(cr,uid,ids):
			if res.invoice_line_adhoc:
				for x in res.invoice_line_adhoc:
					self.pool.get('invoice.adhoc').write(cr,uid,x.id,{'invoice_adhoc_id_gst':res.id,'invoice_adhoc_id':res.id})
			if res.invoice_line_adhoc_gst:
				for x in res.invoice_line_adhoc_gst:
					self.pool.get('invoice.adhoc').write(cr,uid,x.id,{'invoice_adhoc_id_gst':res.id,'invoice_adhoc_id':res.id})
			for val in res.invoice_line_adhoc_11:
				total_cp = total_cp+","+str(val.credit_period)
			total_cp=total_cp[1:]
			self.write(cr,uid,res.id,{'total_cp':total_cp})
			# self.adhoc_invoice_process(cr,uid,ids,context=context)
			# if res.service_classification != 'exempted':
			self.pool.get('invoice.line').add_invoice_tax(cr,uid,res.id,line_sequence_id)
			# self.pool.get('invoice.tax.rate').add_tax(cr,uid,res.id)
			for val in res.invoice_line_adhoc:
				if val.pms.product_desc=='IPM Service':
					self.write(cr,uid,res.id,{'is_ipm':True})
			if res.is_ipm:
				self.pool.get('invoice.adhoc.new').create(cr,uid,
					{
						'name':'Pest Management Services',
						'amount':res.total_amount if res.total_amount else 0.0 ,
						'invoice_adhoc_id_ipm':res.id
					})
			if res.invoice_date:
				invoice_date=res.invoice_date
			else:
				invoice_date=datetime.now().date()
			if res.invoice_due_date:
				self.write(cr,uid,res.id,{'invoice_number':seq_id,'invoice_date':invoice_date})
			if not res.invoice_due_date:
				self.write(cr,uid,res.id,{'invoice_number':seq_id,'invoice_date':invoice_date,'invoice_due_date': datetime.now().date()})
			self.sync_invoice(cr,uid,ids,seq_id)
			temp_amount = tax_rate = tax_rate_amount = 0.0
			if res.tax_one2many:
				for amt in res.tax_one2many:
					tax_rate_amount +=amt.amount
					tax_rate += float(amt.tax_rate)
			net_amount = res.total_amount + res.total_tax
			# if res.total_amount==0.0:
			# 	raise osv.except_osv(('Alert'),('Total Amount cannot be zero!')) 
			# inv_vals = {'total_tax':tax_rate_amount,'basic_amount':res.total_amount,'tax_rate':str(tax_rate),'grand_total_amount':net_amount}
			self.write(cr,uid,res.id,{'total_tax':res.total_tax,'basic_amount':round(res.total_amount,2),'tax_rate':str(tax_rate),'grand_total_amount':round(net_amount)})
			temp_amount = tax_rate = tax_rate_amount = 0.0
			list_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('contract_no','=',res.contract_no.id),('invoice_number','!=',False)])
			if list_id:
				for iter_val in self.pool.get('invoice.adhoc.master').browse(cr,uid,list_id):
					temp_amount += round(iter_val.grand_total_amount)
				self.pool.get('sale.contract').write(cr,uid,res.contract_no.id,{'invoice_value':round(temp_amount)})
			if res.adv_receipt_amount == 0:
				net_amount_payable = net_amount
				self.write(cr,uid,res.id,{'net_amount_payable': round(net_amount_payable)})
			# self.write(cr,uid,res.id,inv_vals)
			partner_id=res.partner_id.id if res.partner_id else None
			cr.execute(('select icl.id from invoice_adhoc_master ic,payment_contract_history icl where icl.history_adhoc_invoice_id=ic.id and ic.partner_id=%(val)s and icl.invoice_number Is Null and ic.invoice_number is not null'),({'val':partner_id}))
			payment_values = cr.fetchall()
			for invoice_id in payment_values:
				if isinstance(invoice_id,(list,tuple)):
					if not res.adhoc_invoice:
						cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,datetime.now().date(),invoice_id[0]))
					else:
						cse = res.cse.id if res.cse else False
						order_number = res.contract_no.contract_number if res.contract_no else ''
						#self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,{'total_amount':res.total_amount})
						if cse:
							cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s,grand_total=%s,basic_amount=%s,tax_amount=%s,cse=%s,order_number=%s where id=%s',(seq_id,datetime.now().date(),res.grand_total_amount,res.total_amount,(tax_rate),cse,order_number,invoice_id[0]))
						else:
							cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s,grand_total=%s,basic_amount=%s,tax_amount=%s,order_number=%s where id=%s',(seq_id,datetime.now().date(),res.grand_total_amount,res.total_amount,(tax_rate),order_number,invoice_id[0]))
				else:	
					cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,res.invoice_date,invoice_id))
		for rec in self.browse(cr,uid,ids):
			customer_invoice=date1=''
			date1=str(datetime.now().date())
			conv=time.strptime(str(date1),"%Y-%m-%d")
			date1 = time.strftime("%d-%m-%Y",conv)
			if rec.cust_name:
				customer_invoice=rec.cust_name+'   Customer Invoice   Created On    '+date1
				customer_invoice_date=self.pool.get('customer.logs').create(cr,uid,
					{
						'customer_join':customer_invoice,
						'customer_id':rec.partner_id.id
					})
			if rec.invoice_line_adhoc_12:
				for record in rec.invoice_line_adhoc_12:
					pms_data = record.pms.name
					if pms_data != None:
						l1.extend([pms_data])
			if rec.invoice_line_adhoc_gst:
				for record in rec.invoice_line_adhoc_gst:
					pms_data = record.pms.name
					if pms_data != None:
						l1.extend([pms_data])
			for i in l1:
				if i not in l2:
					l2.append(i)
			if l2:
				if l2[0] or l2[0]!=None:
					myString = "/".join(l2)
			self.write(cr,uid,rec.id,{'pms':myString,'concurrent_bool':True})
			self.add_invoice_chart_account(cr,uid,ids,context=context)
			self.round_off_ledger(cr,uid,ids,context=context)
		return True

	def generate_invoice_main(self,cr,uid,ids,context=None):
		if not isinstance(ids,(list,tuple)):
			ids = [ids]
		lst=[]
		l1=[]
		l2=[]
		lot_bond_list = []
		myString = ''
		today_date = datetime.now().date()
		year = today_date.year
		year1 = today_date.strftime('%y')
		pms_lst = ""
		invoice_date = False
		pcof_key = invoice_id = temp_count = start_year = end_year = total_cp=''
		seq = count = 0
		seq_srch = self.pool.get('ir.sequence').search(cr,uid,[('code','=','invoice.adhoc.master')])
		if seq_srch:
			seq_start = self.pool.get('ir.sequence').browse(cr,uid,seq_srch[0]).number_next
		pcof_key = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		invoice_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.invoice_id
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		if month > 3:
			start_year = year
			end_year = year+1
			year1 = int(year1)+1
		else:
			start_year = year-1
			end_year = year
			year1 = int(year1)
		financial_year =str(year1-1)+str(year1) 
		financial_start_date = str(start_year)+'-04-01'
		financial_end_date = str(end_year)+'-03-31'
		seq_start=1	
		if pcof_key and invoice_id:
			# pcof_key=pcof_key.split('P')				
			# cr.execute("select invoice_number from invoice_adhoc_master where id != "+str(ids[0] if isinstance(ids, list) else ids)+" and invoice_number is not null and invoice_date>='2017-07-01' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' order by invoice_number desc limit 1");
			cr.execute("select cast(count(id) as integer) from invoice_adhoc_master where invoice_number is not null and invoice_date>='2017-07-01' and invoice_number ilike '%GT%' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and invoice_number_ncs is null");
			# cr.execute("select cast(count(id) as integer) from invoice_adhoc_master where invoice_number is not null and invoice_date>='2017-07-01' and invoice_number ilike '%GT%' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
			temp_count=cr.fetchone()
			if temp_count[0]:
				count= temp_count[0]
			seq=int(count+seq_start)
			seq_id = pcof_key +invoice_id +str(financial_year) +str(seq).zfill(5)
			existing_invoice_number = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','=',seq_id)])
			if existing_invoice_number:
				seq_id = pcof_key +invoice_id +str(financial_year) +str(seq+1).zfill(5)
				new_existing_invoice_number = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','=',seq_id)])
				if new_existing_invoice_number:
					seq_id = pcof_key +invoice_id +str(financial_year) +str(seq+2).zfill(5)
		# if pcof_key and invoice_id:
		# 	pcof_key=pcof_key.split('P')				
		# 	cr.execute("select invoice_number from invoice_adhoc_master where id != "+str(ids[0] if isinstance(ids, list) else ids)+" and invoice_number is not null and invoice_date>='2017-07-01' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' order by invoice_number desc limit 1");
		# 	temp_count=cr.fetchone()
		# 	if not temp_count or temp_count==None:
		# 		seq=seq_start
		# 		seq_id = pcof_key[1] +invoice_id +str(financial_year) +str(seq).zfill(5)
		# 	else:
		# 		invoice_number = temp_count[0]
		# 		invoice_id_year = invoice_id+str(year1)
		# 		invoice_number_split = invoice_number.split(financial_year)
		# 		invoice_number_second = invoice_number_split[1]
		# 		increment_value = int(invoice_number_second)+1
		# 		new_increment_value = str(increment_value).zfill(5)
		# 		seq_id =  str(invoice_number_split[0])+financial_year+str(new_increment_value)
		# pms_list=[]
		res_company_obj = self.pool.get('res.company')
		invoice_adhoc_obj = self.pool.get('invoice.adhoc')
		new_address_obj = self.pool.get('new.address')
		res_partner_address_obj = self.pool.get('res.partner.address')
		o = self.browse(cr,uid,ids[0])
		branch_id = o.branch_id.id
		service_classification = str(o.service_classification)
		invoice_line_search = invoice_adhoc_obj.search(cr,uid,['|',('invoice_adhoc_id11','=',o.id),('invoice_adhoc_id12','=',o.id)])
		invoice_line_browse = invoice_adhoc_obj.browse(cr,uid,invoice_line_search)
		for invoice_line_id in invoice_line_browse:
			location_id = invoice_line_id.location.id
			new_address_id = new_address_obj.browse(cr,uid,location_id).partner_address.id
			res_partner_address_search = res_partner_address_obj.search(cr,uid,[('id','=',new_address_id)])
			lot_bond = res_partner_address_obj.browse(cr,uid,res_partner_address_search[0]).lot_bond
			lot_bond_list.append(lot_bond)
		if service_classification == 'sez':
			lot_bond_list = list(set(lot_bond_list))
			if len(lot_bond_list) > 1:
				raise osv.except_osv(('Alert!'),('Please Tick or Untick the lot bond for all location !'))
		if branch_id:
			branch_id_name = res_company_obj.browse(cr,uid,branch_id).government_notification
			branch_id_str = branch_id_name
			if lot_bond_list:
				lot_bond_list_value = lot_bond_list[0]
			else:
				lot_bond_list_value = False
			if (branch_id_str and lot_bond_list_value== True and service_classification =='sez') or (branch_id_str and service_classification !='sez') or (not branch_id_str and service_classification !='sez'):
						for res in self.browse(cr,uid,ids):
							if res.gst_invoice!=True or res.gst_invoice==False or res.gst_invoice==None:
								cgst_rate = '0.00%'
								cgst_amt = 0.00
								sgst_rate = '0.00%'
								sgst_amt = 0.00
								igst_rate = '0.00%'
								igst_amt = 0.00
								cess_rate = '0.00%'
								cess_amt = 0.00
								amount_new=0.0
								basic_amount = 0.0
								total_tax_amt = 0.0
								grand_total_amount = 0.0
								account_tax_obj = self.pool.get('account.tax')
								today_date = datetime.now().date()
								gst_select_taxes = ['cgst','sgst','utgst','igst','cess']
								gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
								if not gst_taxes:
									raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
								if res.invoice_line_adhoc_11:
									for i in res.invoice_line_adhoc_11:
										address_data = i.location
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
										self.pool.get('invoice.adhoc').write(cr,uid,i.id,
										{
											'services': services,
											'hsn_code': i.pms.hsn_sac_code,
											'discount': 0,
											'location':i.location.id,
											'pms':i.pms.id,
											'rate':i.rate,
											'area':i.area,
											'amount':i.amount,
											'total':i.amount,
											'cse_invoice':res.cse.id,
										})
									basic_amount = 0.0
									total_tax_amt = 0.0
									grand_total_amount = 0.0
									for i in res.invoice_line_adhoc_11:				
										new_address_data = self.pool.get('new.address').browse(cr,uid,i.location.id)
										if res.service_classification not in ('exempted','sez'):
											if not res.branch_id.state_id or not new_address_data.state_id:
												raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
											# comparing states from customer location and branch
											# case: if both states are same
											if res.branch_id.state_id.id == new_address_data.state_id.id:
												# cgst calculation
												cgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cgst')])
												cgst_data = account_tax_obj.browse(cr,uid,cgst_id[0])
												if cgst_data.effective_from_date and cgst_data.effective_to_date:
													if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
														cgst_percent = cgst_data.amount * 100
														cgst_rate = str(cgst_percent)+'%'
														cgst_amt = round((i.amount*cgst_percent)/100,2)
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
															sgst_amt = round((i.amount*utgst_percent)/100,2)
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
															sgst_amt = round((i.amount*sgst_percent)/100,2)
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
														igst_amt = round((i.amount*igst_percent)/100,2)
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
														cess_amt = round((i.amount*cess_percent)/100,2)
										self.pool.get('invoice.adhoc').write(cr,uid,i.id,
											{
												# 'type_of_service':i.type_of_service,
												'invoice_adhoc_id11':res.id,
												'invoice_adhoc_id12':res.id,
												# 'area_sq_mt':i.area_sq_mt,
												# 'no_of_trees':i.no_of_trees,
												# 'boolean_pms_tg':i.boolean_pms_tg,
												# 'services': services, 
												'hsn_code': i.pms.hsn_sac_code,
												# 'qty': i.no_of_services,
												'discount': 0,
												'cgst_rate': cgst_rate,
												'cgst_amt': cgst_amt,
												'sgst_rate': sgst_rate,
												'sgst_amt': sgst_amt,
												'igst_rate': igst_rate,
												'igst_amt': igst_amt,
												'cess_rate': cess_rate,
												'cess_amt': cess_amt,			
											})
								self.write(cr,uid,res.id,{'gst_invoice':True})
						for res in self.browse(cr,uid,ids):
							if res.invoice_line_adhoc:
								for x in res.invoice_line_adhoc:
									self.pool.get('invoice.adhoc').write(cr,uid,x.id,{'invoice_adhoc_id_gst':res.id,'invoice_adhoc_id':res.id})
							if res.invoice_line_adhoc_gst:
								for x in res.invoice_line_adhoc_gst:
									self.pool.get('invoice.adhoc').write(cr,uid,x.id,{'invoice_adhoc_id_gst':res.id,'invoice_adhoc_id':res.id})
							for val in res.invoice_line_adhoc_11:
								total_cp = total_cp+","+str(val.credit_period)
							total_cp=total_cp[1:]
							self.write(cr,uid,res.id,{'total_cp':total_cp})
							# self.adhoc_invoice_process(cr,uid,ids,context=context)
							# if res.service_classification != 'exempted':
							if res.service_classification != 'sez':
								self.pool.get('invoice.tax.rate').add_tax(cr,uid,res.id)
							for val in res.invoice_line_adhoc:
								if val.pms.product_desc=='IPM Service':
									self.write(cr,uid,res.id,{'is_ipm':True})
							if res.is_ipm:
								self.pool.get('invoice.adhoc.new').create(cr,uid,
									{
										'name':'Pest Management Services',
										'amount':res.total_amount if res.total_amount else 0.0 ,
										'invoice_adhoc_id_ipm':res.id
									})
							if res.invoice_date:
								invoice_date=res.invoice_date
							else:
								invoice_date=datetime.now().date()
							if res.invoice_due_date:
								self.write(cr,uid,res.id,{'invoice_number':seq_id,'invoice_date':invoice_date})
							if not res.invoice_due_date:
								self.write(cr,uid,res.id,{'invoice_number':seq_id,'invoice_date':invoice_date,'invoice_due_date': datetime.now().date()})
							self.sync_invoice(cr,uid,ids,seq_id)
							temp_amount = tax_rate = tax_rate_amount = 0.0
							if res.tax_one2many:
								for amt in res.tax_one2many:
									tax_rate_amount +=amt.amount
									tax_rate += float(amt.tax_rate)
							net_amount = res.total_amount + res.total_tax
							# if res.total_amount==0.0:
							# 	raise osv.except_osv(('Alert'),('Total Amount cannot be zero!')) 
							# inv_vals = {'total_tax':tax_rate_amount,'basic_amount':res.total_amount,'tax_rate':str(tax_rate),'grand_total_amount':net_amount}
							self.write(cr,uid,res.id,{'total_tax':res.total_tax,'basic_amount':round(res.total_amount,2),'tax_rate':str(tax_rate),'grand_total_amount':round(net_amount)})
							temp_amount = tax_rate = tax_rate_amount = 0.0
							list_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('contract_no','=',res.contract_no.id),('invoice_number','!=',False)])
							if list_id:
								for iter_val in self.pool.get('invoice.adhoc.master').browse(cr,uid,list_id):
									temp_amount += round(iter_val.grand_total_amount)
								self.pool.get('sale.contract').write(cr,uid,res.contract_no.id,{'invoice_value':round(temp_amount)})
							if res.adv_receipt_amount == 0:
								net_amount_payable = net_amount
								self.write(cr,uid,res.id,{'net_amount_payable': round(net_amount_payable)})
							# self.write(cr,uid,res.id,inv_vals)
							partner_id=res.partner_id.id if res.partner_id else None
							cr.execute(('select icl.id from invoice_adhoc_master ic,payment_contract_history icl where icl.history_adhoc_invoice_id=ic.id and ic.partner_id=%(val)s and icl.invoice_number Is Null and ic.invoice_number is not null'),({'val':partner_id}))
							payment_values = cr.fetchall()
							for invoice_id in payment_values:
								if isinstance(invoice_id,(list,tuple)):
									if not res.adhoc_invoice:
										cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,datetime.now().date(),invoice_id[0]))
									else:
										cse = res.cse.id if res.cse else False
										order_number = res.contract_no.contract_number if res.contract_no else ''
										#self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,{'total_amount':res.total_amount})
										if cse:
											cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s,grand_total=%s,basic_amount=%s,tax_amount=%s,cse=%s,order_number=%s where id=%s',(seq_id,datetime.now().date(),res.grand_total_amount,res.total_amount,(tax_rate),cse,order_number,invoice_id[0]))
										else:
											cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s,grand_total=%s,basic_amount=%s,tax_amount=%s,order_number=%s where id=%s',(seq_id,datetime.now().date(),res.grand_total_amount,res.total_amount,(tax_rate),order_number,invoice_id[0]))
								else:	
									cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,res.invoice_date,invoice_id))
						for rec in self.browse(cr,uid,ids):
							customer_invoice=date1=''
							date1=str(datetime.now().date())
							conv=time.strptime(str(date1),"%Y-%m-%d")
							date1 = time.strftime("%d-%m-%Y",conv)
							if rec.cust_name:
								customer_invoice=rec.cust_name+'   Customer Invoice   Created On    '+date1
								customer_invoice_date=self.pool.get('customer.logs').create(cr,uid,
									{
										'customer_join':customer_invoice,
										'customer_id':rec.partner_id.id
									})
							if rec.invoice_line_adhoc_12:
								for record in rec.invoice_line_adhoc_12:
									pms_data = record.pms.name
									if pms_data != None:
										l1.extend([pms_data])
							if rec.invoice_line_adhoc_gst:
								for record in rec.invoice_line_adhoc_gst:
									pms_data = record.pms.name
									if pms_data != None:
										l1.extend([pms_data])
							for i in l1:
								if i not in l2:
									l2.append(i)
							if l2:
								if l2[0] or l2[0]!=None:
									myString = "/".join(l2)
							self.write(cr,uid,rec.id,{'pms':myString,'concurrent_bool':True})
							self.add_invoice_chart_account(cr,uid,ids,context=context)
			else:
				self.generate_invoice_main_igst(cr,uid,ids,seq_id,context=None)	
		return True

	def adhoc_invoice_process_igst(self,cr,uid,ids,context=None):
				pms_list = []
				sales_rcp_obj = self.pool.get('account.sales.receipts')
				sales_rcp_line_obj = self.pool.get('account.sales.receipts.line')
				inv_adv_rcp_obj = self.pool.get('invoice.advance.receipts')
				inv_adv_rcp_line_obj = self.pool.get('invoice.advance.receipts.line')
				inv_obj = self.pool.get('invoice.adhoc.master')
				inv_adhoc_obj = self.pool.get('invoice.adhoc')
				adv_sales_obj = self.pool.get('advance.sales.receipts')
				premise_obj = self.pool.get('premise.type.master')
				inv_data = self.browse(cr,uid,ids[0])
				res_company_obj = self.pool.get('res.company')
				branch_id = inv_data.branch_id.id
				service_classification = str(inv_data.service_classification)
				if inv_data.invoice_line_adhoc:
					for x in inv_data.invoice_line_adhoc:
						res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
						if res_users_browse:
							res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key	
						if str(res_company_pcof) not in ('P200','P371') and not inv_data.partner_id.igst_check:
							if x.location_invoice.state_id.id!=inv_data.branch_id.state_id.id:
								raise osv.except_osv(('Alert'),("IGST Adhoc Invoice cannot be created as of now!"))
						self.pool.get('invoice.adhoc').write(cr,uid,x.id,{'invoice_adhoc_id_gst':inv_data.id})
				if not inv_data.contract_no:
					raise osv.except_osv(('Alert'),('Please select Contract Number.'))
				if inv_data.service_classification in ('airport','port'):
					raise osv.except_osv(('Alert!'),('Airport/Port service classification cannot be selected as of now!'))
				for vals in inv_data.invoice_line_adhoc:
					if inv_data.contract_no:
						contract_line_id = inv_data.contract_no.contract_line_id if inv_data.contract_no.contract_line_id else inv_data.contract_no.contract_line_id12
						for pms in contract_line_id:
							pms_list.append(pms.pms.id)
				for vals in inv_data.invoice_line_adhoc:
					if vals.pms.id==False:
						raise osv.except_osv(('Alert'),('Please Enter PMS!'))
					if vals.pms.id not in pms_list:
						raise osv.except_osv(('Alert'),('Please Enter PMS which is selected in the contract!'))
					if vals.amount==0.0:
						raise osv.except_osv(('Alert'),('Please Enter Taxable Value!'))
					# if vals.area==False:
					# 	raise osv.except_osv(('Alert'),('Please Enter Area!'))
				if not inv_data.total_amount:
					raise osv.except_osv(('Alert'),('Please Enter Total Amount'))
				for rec in self.browse(cr,uid,ids):
					cgst_rate = '0.00%'
					cgst_amt = 0.00
					sgst_rate = '0.00%'
					sgst_amt = 0.00
					igst_rate = '0.00%'
					igst_amt = 0.00
					cess_rate = '0.00%'
					cess_amt = 0.00
					amount_new=0.0
					basic_amount = 0.0
					total_tax_amt = 0.0
					grand_total_amount = 0.0
					account_tax_obj = self.pool.get('account.tax')
					today_date = datetime.now().date()
					gst_select_taxes = ['igst']
					gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
					if not gst_taxes:
						raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
					if rec.adhoc_invoice==True:
						if rec.invoice_line_adhoc:
							for i in rec.invoice_line_adhoc_gst:
								address_data = i.location_invoice
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
								self.pool.get('invoice.adhoc').write(cr,uid,i.id,
								{
									'services': services,
									'hsn_code': i.pms.hsn_sac_code,
									'discount': 0,
									'location_invoice':i.location_invoice.id,
									'pms':i.pms.id,
									'rate':i.rate,
									'area':i.area,
									'amount':i.amount,
									'total':i.amount,
									'cse_invoice':rec.cse.id,
								})
							basic_amount = 0.0
							total_tax_amt = 0.0
							grand_total_amount = 0.0
							for i in rec.invoice_line_adhoc_gst:				
								new_address_data = self.pool.get('res.partner.address').browse(cr,uid,i.location_invoice.id)
								if rec.service_classification != 'exempted':
									if not rec.branch_id.state_id or not new_address_data.state_id:
										raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
									else:
										igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
										igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
										igst_data_id = igst_data.id
										igst_name = igst_data.name
										acc_id=self.pool.get('account.account').search(cr,uid,[('account_tax_many2one','=',igst_data_id)])
										if igst_data.effective_from_date and igst_data.effective_to_date:
											if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
												igst_percent = igst_data.amount * 100
												igst_rate = str(igst_percent)+'%'
												igst_amt = round((i.amount*igst_percent)/100,2)
										else:
											raise osv.except_osv(('Alert'),("IGST tax not configured!"))
								self.pool.get('invoice.adhoc').write(cr,uid,i.id,
									{
										# 'type_of_service':i.type_of_service,
										'invoice_adhoc_id_gst':rec.id,
										'invoice_adhoc_id':rec.id,
										# 'area_sq_mt':i.area_sq_mt,
										# 'no_of_trees':i.no_of_trees,
										# 'boolean_pms_tg':i.boolean_pms_tg,
										# 'services': services, 
										'hsn_code': i.pms.hsn_sac_code,
										# 'qty': i.no_of_services,
										'discount': 0,
										'cgst_rate': cgst_rate,
										'cgst_amt': cgst_amt,
										'sgst_rate': sgst_rate,
										'sgst_amt': sgst_amt,
										'igst_rate': igst_rate,
										'igst_amt': igst_amt,
										'cess_rate': cess_rate,
										'cess_amt': cess_amt,
									})
								basic_amount = basic_amount + i.amount
								total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
							for i in rec.invoice_line_adhoc_gst:	
								self.pool.get('invoice.adhoc').write(cr,uid,i.id,
									{
										'invoice_adhoc_id_gst':rec.id,
										'invoice_adhoc_id':rec.id,
									})
				inv_data = self.browse(cr,uid,ids[0])
				grand_total_amount = basic_amount + total_tax_amt
				inv_vals = {
							'gst_adhoc': True,
							'total_tax': total_tax_amt,
							'pending_amount':round(grand_total_amount),
							'basic_amount': round(basic_amount,2),
							'grand_total_amount':round(grand_total_amount)
					       }
				self.write(cr,uid,inv_data.id,inv_vals)
				insert_qry='insert into invoice_tax_rate(name,amount,invoice_id,account_tax_id,tax_rate,account_id)values(%s,%s,%s,%s,%s,%s)' %("'"+str(igst_name)+"'",str(total_tax_amt),str(rec.id),str(igst_id[0]),'18.00',str(acc_id[0]))
				cr.execute(insert_qry)
				if inv_data.gst_invoice == False:
					self.write(cr,uid,inv_data.id,{'gst_invoice':True})
				return True

	def adhoc_invoice_process(self,cr,uid,ids,context=None):
		lot_bond_list = []
		sales_rcp_obj = self.pool.get('account.sales.receipts')
		sales_rcp_line_obj = self.pool.get('account.sales.receipts.line')
		inv_adv_rcp_obj = self.pool.get('invoice.advance.receipts')
		inv_adv_rcp_line_obj = self.pool.get('invoice.advance.receipts.line')
		inv_obj = self.pool.get('invoice.adhoc.master')
		inv_adhoc_obj = self.pool.get('invoice.adhoc')
		adv_sales_obj = self.pool.get('advance.sales.receipts')
		premise_obj = self.pool.get('premise.type.master')
		inv_data = self.browse(cr,uid,ids[0])
		res_company_obj = self.pool.get('res.company')
		invoice_adhoc_obj = self.pool.get('invoice.adhoc')
		new_address_obj = self.pool.get('new.address')
		res_partner_address_obj = self.pool.get('res.partner.address')
		o = self.browse(cr,uid,ids[0])
		branch_id = inv_data.branch_id.id
		service_classification = str(inv_data.service_classification)
		invoice_line_search = invoice_adhoc_obj.search(cr,uid,['|',('invoice_adhoc_id11','=',o.id),('invoice_adhoc_id12','=',o.id)])
		invoice_line_browse = invoice_adhoc_obj.browse(cr,uid,invoice_line_search)
		for invoice_line_id in invoice_line_browse:
			location_id = invoice_line_id.location.id
			new_address_id = new_address_obj.browse(cr,uid,location_id).partner_address.id
			res_partner_address_search = res_partner_address_obj.search(cr,uid,[('id','=',new_address_id)])
			lot_bond = res_partner_address_obj.browse(cr,uid,res_partner_address_search[0]).lot_bond
			lot_bond_list.append(lot_bond)
		if service_classification == 'sez':
			lot_bond_list = list(set(lot_bond_list))
			if len(lot_bond_list) > 1:
				raise osv.except_osv(('Alert!'),('Please Tick or Untick the lot bond for all location!'))
		if branch_id:
			branch_id_name = res_company_obj.browse(cr,uid,branch_id).government_notification
			branch_id_str = branch_id_name
			if lot_bond_list:
				lot_bond_list_value = lot_bond_list[0]
			else:
				lot_bond_list_value = [False]
			if (branch_id_str and lot_bond_list_value[0] == True and service_classification =='sez') or (branch_id_str and service_classification !='sez') or (not branch_id_str and service_classification !='sez'):
					pms_list = []
					if inv_data.invoice_line_adhoc:
						for x in inv_data.invoice_line_adhoc:
							res_users_browse = self.pool.get('res.users').browse(cr,uid,1).company_id.id
							if res_users_browse:
								res_company_pcof = self.pool.get('res.company').browse(cr,uid,res_users_browse).pcof_key	
							if str(res_company_pcof) not in ('P200','P371') and not inv_data.partner_id.igst_check:
								if x.location_invoice.state_id.id!=inv_data.branch_id.state_id.id:
									raise osv.except_osv(('Alert'),("IGST Adhoc Invoice cannot be created as of now!"))
							self.pool.get('invoice.adhoc').write(cr,uid,x.id,{'invoice_adhoc_id_gst':inv_data.id})
					if not inv_data.contract_no:
						raise osv.except_osv(('Alert'),('Please select Contract Number.'))
					if inv_data.service_classification in ('airport','port'):
						raise osv.except_osv(('Alert!'),('Airport/Port service classification cannot be selected as of now!'))
					for vals in inv_data.invoice_line_adhoc:
						if inv_data.contract_no:
							contract_line_id = inv_data.contract_no.contract_line_id if inv_data.contract_no.contract_line_id else inv_data.contract_no.contract_line_id12
							for pms in contract_line_id:
								pms_list.append(pms.pms.id)
					for vals in inv_data.invoice_line_adhoc:
						if vals.pms.id==False:
							raise osv.except_osv(('Alert'),('Please Enter PMS!'))
						if vals.pms.id not in pms_list:
							raise osv.except_osv(('Alert'),('Please Enter PMS which is selected in the contract!'))
						if vals.amount==0.0:
							raise osv.except_osv(('Alert'),('Please Enter Taxable Value!'))
						# if vals.area==False:
						# 	raise osv.except_osv(('Alert'),('Please Enter Area!'))
					if not inv_data.total_amount:
						raise osv.except_osv(('Alert'),('Please Enter Total Amount'))
					for rec in self.browse(cr,uid,ids):
						cgst_rate = '0.00%'
						cgst_amt = 0.00
						sgst_rate = '0.00%'
						sgst_amt = 0.00
						igst_rate = '0.00%'
						igst_amt = 0.00
						cess_rate = '0.00%'
						cess_amt = 0.00
						amount_new=0.0
						basic_amount = 0.0
						total_tax_amt = 0.0
						grand_total_amount = 0.0
						account_tax_obj = self.pool.get('account.tax')
						today_date = datetime.now().date()
						gst_select_taxes = ['cgst','sgst','utgst','igst','cess']
						gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
						if not gst_taxes:
							raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
						if rec.adhoc_invoice==True:
							if rec.invoice_line_adhoc:
								for i in rec.invoice_line_adhoc_gst:
									address_data = i.location_invoice
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
									self.pool.get('invoice.adhoc').write(cr,uid,i.id,
									{
										'services': services,
										'hsn_code': i.pms.hsn_sac_code,
										'discount': 0,
										'location_invoice':i.location_invoice.id,
										'pms':i.pms.id,
										'rate':i.rate,
										'area':i.area,
										'amount':i.amount,
										'total':i.amount,
										'cse_invoice':rec.cse.id,
									})
								basic_amount = 0.0
								total_tax_amt = 0.0
								grand_total_amount = 0.0
								for i in rec.invoice_line_adhoc_gst:				
									new_address_data = self.pool.get('res.partner.address').browse(cr,uid,i.location_invoice.id)
									if rec.service_classification not in ('exempted','sez'):
										if not rec.branch_id.state_id or not new_address_data.state_id:
											raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
										# comparing states from customer location and branch
										# case: if both states are same
										if rec.branch_id.state_id.id == new_address_data.state_id.id:
											# cgst calculation
											cgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cgst')])
											cgst_data = account_tax_obj.browse(cr,uid,cgst_id[0])
											if cgst_data.effective_from_date and cgst_data.effective_to_date:
												if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
													cgst_percent = cgst_data.amount * 100
													cgst_rate = str(cgst_percent)+'%'
													cgst_amt = round((i.amount*cgst_percent)/100,2)
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
														sgst_amt = round((i.amount*utgst_percent)/100,2)
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
														sgst_amt = round((i.amount*sgst_percent)/100,2)
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
													igst_amt = round((i.amount*igst_percent)/100,2)
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
													cess_amt = round((i.amount*cess_percent)/100,2)
									self.pool.get('invoice.adhoc').write(cr,uid,i.id,
										{
											# 'type_of_service':i.type_of_service,
											'invoice_adhoc_id_gst':rec.id,
											'invoice_adhoc_id':rec.id,
											# 'area_sq_mt':i.area_sq_mt,
											# 'no_of_trees':i.no_of_trees,
											# 'boolean_pms_tg':i.boolean_pms_tg,
											# 'services': services, 
											'hsn_code': i.pms.hsn_sac_code,
											# 'qty': i.no_of_services,
											'discount': 0,
											'cgst_rate': cgst_rate,
											'cgst_amt': cgst_amt,
											'sgst_rate': sgst_rate,
											'sgst_amt': sgst_amt,
											'igst_rate': igst_rate,
											'igst_amt': igst_amt,
											'cess_rate': cess_rate,
											'cess_amt': cess_amt,
										})
									basic_amount = basic_amount + i.amount
									total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt+igst_amt+cess_amt
								for i in rec.invoice_line_adhoc_gst:	
									self.pool.get('invoice.adhoc').write(cr,uid,i.id,
										{
											'invoice_adhoc_id_gst':rec.id,
											'invoice_adhoc_id':rec.id,
										})
					inv_data = self.browse(cr,uid,ids[0])
					grand_total_amount = basic_amount + total_tax_amt
					inv_vals = {
								'gst_adhoc': True,
								'total_tax': total_tax_amt,
								'pending_amount':round(grand_total_amount),
								'basic_amount': round(basic_amount,2),
								'grand_total_amount':round(grand_total_amount)
						       }
					self.write(cr,uid,inv_data.id,inv_vals)
					if inv_data.gst_invoice == False:
						self.write(cr,uid,inv_data.id,{'gst_invoice':True})
					# return {	
					# 			'type': 'ir.actions.act_window',
					# 			'name': 'Adhoc Invoice',
					# 			'view_mode': 'form',
					# 			'view_type': 'form',
					# 			'view_id': False,
					# 			'res_id': ids[0],
					# 			'res_model': 'invoice.adhoc.master',
					# 			'target': 'current',
					# 		}

			else:
				self.adhoc_invoice_process_igst(cr,uid,ids,context=None)
			return {	
								'type': 'ir.actions.act_window',
								'name': 'Adhoc Invoice',
								'view_mode': 'form',
								'view_type': 'form',
								'view_id': False,
								'res_id': ids[0],
								'res_model': 'invoice.adhoc.master',
								'target': 'current',
							}			


	def print_invoice(self,cr,uid,ids,context=None):
 		if not isinstance(ids,(list,tuple)):
			ids = [ids]
		cr.execute('delete from history_invoice_report')
		for rec in self.browse(cr,uid,ids):
			print_count=rec.print_count+1
			self.write(cr,uid,ids,{'print_count':print_count})
			if rec.gst_invoice and not rec.report_type:
				raise osv.except_osv(('Alert!'),('Please select the report type!'))
			if rec.grand_total_amount>=100000:
				if not rec.partner_id.pan_no:
					raise osv.except_osv(('Alert!'),('Please update the PAN number as the invoice amount is greater than 1 Lakh'))
			if rec.exempted == True:
				for iterate in rec.invoice_line_adhoc_11:
					if iterate.location:
						for partner_address in self.pool.get('res.partner.address').browse(cr,uid,[iterate.location.partner_address.id]):
							if partner_address.exempted:
								if not partner_address.certificate_no:
									raise osv.except_osv(('Alert!'),('Please fill out the Exempted Certificate no. Against the Exempted Location on Customer Page'))
			if rec.status == 'open':
				self.write(cr,uid,rec.id,{'status':'printed'})
				search_id =self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',rec.invoice_number)])
				self.pool.get('payment.contract.history').write(cr,uid,search_id,{'payment_status':'printed'})

			search_id_company = self.pool.get('res.company').search(cr,uid,[('type','=','ccc')])
			if not search_id_company:
						raise osv.except_osv(('Alert!'),('Please Enter Server Configuration Details'))
			try:
				raise
				for company_id in self.pool.get('res.company').browse(cr,uid,[search_id_company[0]]):
					vpn_ip_addr = company_id.vpn_ip_address
					port =company_id.port
					dbname = company_id.dbname
					pwd = company_id.pwd
					user_name = str(company_id.user_name.login)
					username = user_name
					pwd = pwd   
					dbname = dbname
					log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
					obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
					sock_common = xmlrpclib.ServerProxy (log)
					uid = sock_common.login(dbname, username, pwd)
					sock = xmlrpclib.ServerProxy(obj)
					partner_srch_id = [('ou_id','=',rec.partner_id.ou_id)]
					partner_ids= sock.execute(dbname, uid, pwd, 'res.partner', 'search',partner_srch_id)
					if not partner_ids:
						raise
					if partner_ids:
						search_id = [('invoice_number','=',rec.invoice_number),('partner_id','=',partner_ids[0])]
						contract_id = sock.execute(dbname, uid, pwd, 'invoice.adhoc.master', 'search',search_id)
						if not contract_id:
							raise
						if contract_id:
							sock.execute(dbname, uid, pwd, 'invoice.adhoc.master', 'write',contract_id[0],{'status':'printed'})
			except Exception:
				insert_line=main_name =insert2=insert_line1=''
				for company_id in self.pool.get('res.company').browse(cr,uid,[search_id_company[0]]):
					main_name = company_id.name
				curr_pcof=self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
				time_cur = time.strftime("%H:%M:%S")
				date = datetime.now().date()
				current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key #changes 22jul16
				con_cat = str(main_name)+'_'+current_company+'_accounts'+str(date)+'_'+str(time_cur)+'.sql'
				try:
					filename = os.path.expanduser('~')+"/sql_files/"+con_cat
					d = os.path.dirname(os.path.expanduser('~')+"/sql_files/")
					if not os.path.exists(d):
						os.makedirs(d)
				except IOError as e:
					print "I/O error({0}): {1}".format(e.errno, e.strerror)
				insert ="\nselect * from one2many_update('res_partner where ou_id =''"+str(rec.partner_id.ou_id)+"''','invoice_adhoc_master set status = ''printed'' where invoice_number= ''"+str(rec.invoice_number)+"'' and partner_id =  ');"
				with open(filename,'a') as f:
					f.write(insert)
				f.close() 
			if rec.check_previous_history :
				srch_partner = self.search(cr,uid,[('partner_id','=',rec.partner_id.id),('contract_no','=',rec.contract_no.id),('invoice_number','!=',False)])	
				for in_dt in self.browse(cr,uid,srch_partner):
					grand_total_amount=0.0
					invoice_no=''
					if in_dt.import_flag==True:
						invoice_no=in_dt.invoice_number.replace('/','')
						invoice_no=invoice_no[-8:]
					else:
						invoice_no=in_dt.invoice_number[-8:]
					if invoice_no < rec.invoice_number[-8:]:
						if in_dt.net_amount_payable!=0.0:
							grand_total_amount=in_dt.net_amount_payable
						else:
							grand_total_amount=in_dt.grand_total_amount
						self.pool.get('history.invoice.report').create(cr,uid,
							{
								'history_invoice_report_id':rec.id,
								'invoice_num':in_dt.invoice_number,
								'invoice_date':in_dt.invoice_date,
								'status':str(grand_total_amount) 
							})
			data = self.pool.get('invoice.adhoc.master').read(cr, uid, [rec.id],context)
			datas = {
					'ids': ids,
					'model': 'invoice.adhoc.master',
					'form': data
				}
			if rec.gst_invoice == True:
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'gst_invoice_print',
						'datas': datas,
						}
			else:
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'invoice_print',
						'datas': datas,
						}
		return {'type': 'ir.actions.act_window_close'}



	def receipt(self, cr, uid, ids, vals, context=None):
		adhoc_obj = self.pool.get('invoice.adhoc')
		result = account_security = account_itds = ''
		account_id = False
		for res in self.browse(cr,uid,ids):
				invoice_number = res.invoice_number
				itds_total = ''
				itds_rate = 0.0
				srch =[]
				if res.check_process_invoice == False:
					self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,
						{
							'invoice_id_receipt':'',
							'check_invoice':False,
							'partial_payment_amount':round(res.pending_amount),
						})
				if invoice_number == False:
					raise osv.except_osv(('Alert'),('There is no Invoice Number for this record.'))
				if res.tax_rate == '0.0':
					raise osv.except_osv(('Alert'),('There is no tax_rate for this record.')) 
				if res.tax_rate:
					acc_query="select id from account_account where account_selection = 'against_ref' and name ilike '%"+str(res.tax_rate)+"%' "
					cr.execute(acc_query)
					srch=cr.fetchone()
				else:
					raise osv.except_osv(('Alert'),('There is no tax_rate for this record.')) 
				srch1 = self.pool.get('account.account').search(cr,uid,[('account_selection','=','itds_receipt')])
				srch2 = self.pool.get('account.account').search(cr,uid,[('account_selection','=','security_deposit')])
				if srch:
					srch_id=srch[0] if isinstance(srch,(list,tuple)) else srch
					acc_id =self.pool.get('account.account').browse(cr,uid,srch_id)
					account_id = acc_id.id
				for acc_id in self.pool.get('account.account').browse(cr,uid,srch2):
					account_security = acc_id.id
				for acc_id in self.pool.get('account.account').browse(cr,uid,srch1):
					account_itds = acc_id.id
					itds_rate = acc_id.itds_rate if acc_id.itds_rate else 0.0
				adhoc_ids1 = adhoc_obj.search(cr,uid,[('invoice_adhoc_id12','=',res.id)])
				if adhoc_ids1:
					adhoc_ids = adhoc_ids1
					adhoc_data = adhoc_obj.browse(cr,uid,adhoc_ids[0])
					address_id = adhoc_data.location.partner_address.id
				else:
					adhoc_ids2 = adhoc_obj.search(cr,uid,[('invoice_adhoc_id11','=',res.id)])
					if adhoc_ids2:
						adhoc_ids = adhoc_ids2
						adhoc_data = adhoc_obj.browse(cr,uid,adhoc_ids[0])
						address_id = adhoc_data.location.partner_address.id
					else:
						adhoc_ids3 = adhoc_obj.search(cr,uid,[('invoice_adhoc_id_gst','=',res.id)])
						if adhoc_ids3:
							adhoc_ids = adhoc_ids3
							adhoc_data = adhoc_obj.browse(cr,uid,adhoc_ids[0])
							address_id = adhoc_data.location_invoice.id
						else:
							adhoc_ids4 = adhoc_obj.search(cr,uid,[('invoice_adhoc_id','=',res.id)])
							if adhoc_ids4:
								adhoc_ids = adhoc_ids4
								adhoc_data = adhoc_obj.browse(cr,uid,adhoc_ids[0])
								address_id = adhoc_data.location_invoice.id
				create_id = self.pool.get('account.sales.receipts').create(cr,uid,
					{
						'customer_name':res.partner_id.id,
						'customer_id_invisible':res.partner_id.ou_id,
						'acc_status':'against_ref',
						'chek_receipt':True,
						'invoice_number':res.invoice_number,
						'account_select_boolean':True,
						'billing_location': address_id,
						'payment_status':'partial_payment',
					})
				result = self.pool.get('account.sales.receipts.line').create(cr,uid,
					{
						'customer_name':res.partner_id.id,
						'receipt_id':create_id,
						'acc_status':'against_ref',
						'account_id':account_id,
						'type':'credit',
						'credit_amount':res.pending_amount,
						'check_against_ref_status':False,
						'payment_status':'partial_payment',
					})
				for adhoc_id in adhoc_ids:
					self.pool.get('invoice.adhoc.receipts').create(cr,uid,
						{
							'sales_receipt_id': create_id,
							'invoice_adhoc_id': adhoc_id,
						})
				if itds_rate: 
					itds_rate_per = itds_rate * 0.01
					itds_total = res.pending_amount * itds_rate_per
				else:
					raise osv.except_osv(('Alert'),('Please give Itds Rate'))
				result_itds = self.pool.get('account.sales.receipts.line').create(cr,uid,
					{
						'customer_name':res.partner_id.id,
						'receipt_id':create_id,
						'acc_status':'against_ref',
						'account_id':account_itds,
						'type':'debit',
						'credit_amount':0.0,
						'debit_amount':round(itds_total),
						'check_against_ref_status':False
					})
				result_security = self.pool.get('account.sales.receipts.line').create(cr,uid,
					{
						'customer_name':res.partner_id.id,
						'receipt_id':create_id,
						'acc_status':'against_ref',
						'account_id':account_security,
						'type':'debit',
						'credit_amount':0.0,
						'check_against_ref_status':False
					})
				self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,
					{
						'invoice_id_receipt':result,
						'check_invoice':True
					})
				self.write(cr,uid,res.id,{'check_against_reference':True})
				models_data = self.pool.get('ir.model.data')
				form_view = models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_form')
				print form_view
				return {
					'name':'Sales Receipts',
					'view_mode': 'form',
					'view_id': False,
					'views':[(form_view and form_view[1] or False, 'form')],
					'view_type': 'form',
					'res_model': 'account.sales.receipts',
					'res_id':create_id,
					'type': 'ir.actions.act_window',
					'target': 'current',
					'domain': '[]',
					'context': context,
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

	def round_off_ledger(self,cr,uid,ids,context=None):
		for rec in self.browse(cr,uid,ids):
			search_account=self.pool.get('account.account').search(cr,uid,[('name','=','Round-off')])
			if search_account:
				date = rec.invoice_date
				search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
				for var in self.pool.get('account.period').browse(cr,uid,search_date):
					period_id = var.id
				srch_jour_bank = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Purchase Journal')])
				for jour_bank in self.pool.get('account.journal').browse(cr,uid,srch_jour_bank):
					journal_bank = jour_bank.id
				move=self.pool.get('account.move').create(cr,uid,{
								'journal_id':journal_bank,#Confirm from PCIL(JOURNAL ID)
								'state':'posted',
								'date':date,
								'name':rec.invoice_number,
								'partner_id':rec.partner_id.id,
								'narration':rec.invoice_narration if rec.invoice_narration else '',
								'voucher_type':'Purchase Receipt',},context=context)
				debit_amount=credit_amount=0.0
				for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
					if rec.round_off_val>=0:
						credit_amount=rec.round_off_val
					else:
						debit_amount=-rec.round_off_val
					self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
					'account_id':search_account[0],
					'debit':debit_amount,
					'credit':credit_amount,
					'name':rec.cust_name if rec.cust_name else '',
					'journal_id':journal_bank,
					'period_id':period_id,
					'partner_id':rec.partner_id.id,
					'date':date,
					'state':'valid',
					'ref':rec.invoice_number},context=context)
				cr.execute("update account_move_line set state='posted' where account_id=%s"%(search_account[0]))

		return True

invoice_adhoc_master()


class invoice_tax_rate(osv.osv):
	_inherit = 'invoice.tax.rate'

	def add_tax(self,cr,uid,model_id,use_date=None):
		total_tax=val1=tax_rate=advance_amount=grand_total_amount=amount=round_amount=difference=0.0
		todays_date=use_date if use_date else datetime.now().date().strftime("%Y-%m-%d")
		model_id=model_id if isinstance(model_id,(int,long)) else model_id[0]
		for order in self.pool.get('invoice.adhoc.master').browse(cr,uid,[model_id]):
			if order.adhoc_invoice:
				if order.gst_invoice==True:
					for line in order.invoice_line_adhoc_gst:
						val1 += line.amount
				else:
					for line in order.invoice_line_adhoc:
						val1 += line.amount
			else:
				for line in order.invoice_line_adhoc_11:
					val1 += line.amount
			acc_tax_ids=[]
			acc_id=self.search(cr,uid,[('invoice_id','=',order.id)])
			if acc_id:
				for acc_ids in self.browse(cr,uid,acc_id):
				     acc_tax_ids.append(acc_ids.account_tax_id.id)
			tax_ids= self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',todays_date),('effective_to_date','>',todays_date),('select_tax_type','!=',False)])
			GST_val=self.pool.get('account.account').search(cr,uid,[('name','=','GST')])
			if GST_val:
				Inter_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','igst')])[0]
				union_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','utgst')])[0]
				state_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','sgst')])[0]
				central_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','cgst')])[0]
				for i in order.invoice_line_adhoc_11:
					if order.branch_id.state_id.name==i.location.state_id.name:
						if Inter_state_id in tax_ids:
							tax_ids.remove(Inter_state_id)
						if order.branch_id.state_id.union_territory==False:
							if union_state_id in tax_ids:
								tax_ids.remove(union_state_id)
						else:
							if state_gst in tax_ids:
								tax_ids.remove(state_gst)
					else:
						if union_state_id in tax_ids:
							tax_ids.remove(union_state_id)
						if state_gst in tax_ids:
							tax_ids.remove(state_gst)
						if central_gst in tax_ids:
							tax_ids.remove(central_gst)
				for i in order.invoice_line_adhoc:
					if order.branch_id.state_id.name==i.location_invoice.state_id.name:
						if Inter_state_id in tax_ids:
							tax_ids.remove(Inter_state_id)
						if order.branch_id.state_id.union_territory==False:
							if union_state_id in tax_ids:
								tax_ids.remove(union_state_id)
						else:
							if state_gst in tax_ids:
								tax_ids.remove(state_gst)
					else:
						if union_state_id in tax_ids:
							tax_ids.remove(union_state_id)
						if state_gst in tax_ids:
							tax_ids.remove(state_gst)
						if central_gst in tax_ids:
							tax_ids.remove(central_gst)
			for rec in self.pool.get('account.tax').browse(cr,uid,tax_ids):
				if rec.id not in acc_tax_ids:
					tax =1
					current_tax_amount,tax=self.recr_amount(rec,val1,todays_date,tax)
					acc_id=self.pool.get('account.account').search(cr,uid,[('account_tax_many2one','=',rec.id)])
					if current_tax_amount > 0:
						if order.service_classification=='exempted' or order.exempted: 
							current_tax_amount = 0.0
						cr.execute('insert into invoice_tax_rate(name,amount,invoice_id,account_tax_id,tax_rate,account_id)values(%s,%s,%s,%s,%s,%s)' %("'"+str(rec.name)+"'",str(round(current_tax_amount,2)),str(model_id),str(rec.id),str(tax),str(acc_id[0])))
				if rec.id in acc_tax_ids :
					tax=1
					current_tax_amount,tax=self.recr_amount(rec,val1,todays_date,tax)
					if current_tax_amount > 0:
						if order.service_classification=='exempted' or order.exempted: 
							current_tax_amount = 0.0
						cr.execute("update invoice_tax_rate  set amount="+str(round(current_tax_amount,2))+" where invoice_id="+str(order.id)+" and account_tax_id="+str(rec.id)+"")
			acc_tax_ids = list(set(acc_tax_ids)-set(tax_ids))	
			if acc_tax_ids:		
				acc_query="delete from invoice_tax_rate where invoice_id=%s and account_tax_id in %s "%(str(order.id),'('+str(acc_tax_ids[0])+')' if len(acc_tax_ids) == 1 else tuple(acc_tax_ids))
				cr.execute(acc_query)
			for amt in order.tax_one2many:
				total_tax+=amt.amount
				tax_rate += float(amt.tax_rate)
			advance_amount=order.adv_receipt_amount
			grand_total_amount=val1+total_tax
			amount=grand_total_amount
			round_amount=round(grand_total_amount)
			difference=round((round_amount-amount),2)
			cr.execute("update invoice_adhoc_master set grand_total_amount=%s,net_amount_payable=%s,total_tax=%s,tax_rate=%s,round_off_val=%s where id=%s" %(str(round(val1+total_tax)),str(round(val1+total_tax-advance_amount)),str(total_tax),str(tax_rate),str(difference),str(order.id)))
			if order.invoice_number and order.invoice_date:
				self.pool.get('invoice.adhoc.master').round_off_ledger(cr,uid,[order.id])
		return True

invoice_tax_rate()