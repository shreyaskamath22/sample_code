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
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
from dateutil.relativedelta import relativedelta
import calendar
import re
from base.res import res_company as COMPANY
from base.res import res_partner
from collections import Counter
import xmlrpclib
import math
import os
from tools.translate import _
from datetime import date,datetime, timedelta
from osv import osv,fields
import time 
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import calendar
import re
from base.res import res_partner
import decimal_precision as dp
import xlsxwriter
import xlsxwriter as xls
from dateutil.relativedelta import relativedelta
import pdb


class account_account(osv.osv):
	_inherit = 'account.account'
	_columns = {
		# 'account_selection':fields.selection([
		# 			('advance','Advance'),
		# 			('advance_against_ref','Advance Against Reference'),
		# 			('against_ref','Against Reference'),
		# 			('bank_charges','Bank Charges'),
		# 			('cash','Cash'),
		# 			('funds_transferred_ho','Funds Transferred to HO'),
		# 			('ho_remmitance','HO Remmitance'),
		# 			('iob_one','Receive in Bank'),
		# 			('iob_two','Pay from Bank'),
		# 			('employee','Employee'),
		# 			('others','Others(CFOB)'),
		# 			('primary_cost_cse','Primary Cost Category(CSE)'), # Emp Name + Amount
		# 			('primary_cost_office','Primary Cost Category(Office)'), # Office Name + Amount
		# 			('primary_cost_phone','Primary Cost Category(Phone/Mobile No.)'), #Phone/MobileNo+EmpName+Amount
		# 			('primary_cost_vehicle','Primary Cost Category(Vehicle)'), #Vehicle No. + Empe Name + Amount
		# 			('primary_cost_service','Primary Cost Category(Service)'), # Service + Amount
		# 			('primary_cost_cse_office','Primary Cost Category(CSE Office)'), # office Name + Employee Name + Amount
		# 			('security_deposit','Security Deposits'),
		# 			('sundry_deposit','Sundry Deposits'),
		# 			('itds','ITDS'),('itds_receipt','ITDS on Contract Receipts'),
		# 			('st_input','ST Input'),('excise_input','Excies Input'),
		# 			('tax','Tax'),
		# 			],'Selection'),
		'invoice_type': fields.selection([
					('product','Product'),
					('service','Service'),
					('composite','Composite'),
					],'Invoice Type'),
	}

account_account()

class res_partner(osv.osv):
	_inherit = 'res.partner'
	_columns = {
	'is_transfered': fields.boolean('Is Transfered'),
	'insecticide_lic_no': fields.char(string='INSECTICIDE LICESNSE NO',size=100)
	}
	def new_location_supplier1(self,cr,uid,ids,context=None):
		
		models_data=self.pool.get('ir.model.data')
		form_id = models_data.get_object_reference(cr, uid, 'account_sales_branch', 'view_partner_address_wizard_supplier_form')
		for k in self.browse(cr,uid,ids):

			return {
						   'name':'Add New Location',
						   'view_mode': 'form',
						   'view_id': form_id[1],
						   'view_type': 'form',
						   'res_model': 'res.partner.address',
						   #'res_id':line_id,
						   'type': 'ir.actions.act_window',
						   'target': 'new',
						   'domain': '[]',
						   'context': {'title':k.title,'name':k.contact_name,'default_partner_id':k.id,'location_check':True,'first_name':k.first_name,'middle_name':k.middle_name,
						   'last_name':k.last_name,'default_designation':k.designation}}

	def psd_new_location_supplier1(self,cr,uid,ids,context=None):
	
		models_data=self.pool.get('ir.model.data')
		form_id = models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_view_partner_address_wizard_supplier_form')
		for k in self.browse(cr,uid,ids):

			return {
						   'name':'Add New Location',
						   'view_mode': 'form',
						   'view_id': form_id[1],
						   'view_type': 'form',
						   'res_model': 'res.partner.address',
						   #'res_id':line_id,
						   'type': 'ir.actions.act_window',
						   'target': 'new',
						   'domain': '[]',
						   'context': {'title':k.title,'name':k.contact_name,'default_partner_id':k.id,'location_check':True,'first_name':k.first_name,'middle_name':k.middle_name,
						   'last_name':k.last_name,'default_designation':k.designation}}

	def edit_location_supplier1(self,cr,uid,ids,context=None):
		models_data=self.pool.get('ir.model.data')
		form_id = models_data.get_object_reference(cr, uid, 'account_sales_branch', 'view_partner_address_wizard_line_supplier_form')
		for k in self.browse(cr,uid,ids):
			if not k.location_address.id:
				raise osv.except_osv(('Alert'),('Please select location to edit.'))
			if k.location_address.id:
				#print "xxxxxxxx",k.designation,form_id,ids,k.id,k.location_address.id
				cr.execute('update res_partner_address set designation=%(vals)s where  id =%(ids)s',{'vals':k.designation,'ids':k.location_address.id})
				
				return {
							   'name':'Add New Location',
							   'view_mode': 'form',
							   'view_id': form_id[1],
							   'view_type': 'form',
							   'res_model': 'res.partner.address',
							   'res_id':k.location_address.id,
							   'type': 'ir.actions.act_window',
							   'target': 'new',
							   'domain': '[]',
							   'context': {'title':k.title,'name':k.contact_name,'designation':k.designation,'default_partner_id':k.id,'location_check':True,
							   'first_name':k.first_name,'middle_name':k.middle_name,
							   'last_name':k.last_name,}}

	def psd_edit_location_supplier1(self,cr,uid,ids,context=None):
			models_data=self.pool.get('ir.model.data')
			form_id = models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_view_partner_address_wizard_line_supplier_form')
			for k in self.browse(cr,uid,ids):
				if not k.location_address.id:
					raise osv.except_osv(('Alert'),('Please select location to edit.'))
				if k.location_address.id:
					#print "xxxxxxxx",k.designation,form_id,ids,k.id,k.location_address.id
					cr.execute('update res_partner_address set designation=%(vals)s where  id =%(ids)s',{'vals':k.designation,'ids':k.location_address.id})
					
					return {
								   'name':'Add New Location',
								   'view_mode': 'form',
								   'view_id': form_id[1],
								   'view_type': 'form',
								   'res_model': 'res.partner.address',
								   'res_id':k.location_address.id,
								   'type': 'ir.actions.act_window',
								   'target': 'new',
								   'domain': '[]',
								   'context': {'title':k.title,'name':k.contact_name,'designation':k.designation,'default_partner_id':k.id,'location_check':True,
								   'first_name':k.first_name,'middle_name':k.middle_name,
								   'last_name':k.last_name,}}
res_partner()

class monthly_report(osv.osv):
	_inherit = 'monthly.report'
	_columns = {
		'monthly_selection':fields.selection([('summary_accounts','Summary of Accounts (SOA)'),
											  ('stmt_collection','Statement of Collection'),
											  ('stmt_recoveries','Statement of Recoveries (SOR)'),
											  ('stmt_tds_recoveries','Statement of TDS Recoveries'),
											  ('stmt_funds_transfer_a/c_II','Statement of Funds Transferred from A/c I to A/c II'),
											  ('stmt_cash_withdrawal','Statement of Cash Withdrawal / Cheque Payments'),
											  ('cash_bank_payment_extract','Cash Bank Payment Extract (SOP)'),
											  ('stmt_funds_remitted','Statement of Funds Remitted to HO / Branches'),
											  ('stmt_bank_charges','Statement of Bank Charges'),
											  ('stmt_debtors_reconciliation','Statement of Debtors Reconciliation with List'),
											  #('bank_reconciliation_iob_one','Bank Reconciliation of I.O.B Account I'),
											  #('bank_reconciliation_iob_two','Bank Reconciliation of I.O.B Account II'),
											  ('bank_slip_book','Bank Slip Book'),
											  #('stmt_credit_register','Statement of ST Input Credit Register'),
											  ('st_input_report','ST Input (Purchase / Expenses) Credit Entry & Report'),
											  ('cse_collection_summary','CSE Collection Summary'),
											  ],'Monthly Report'),
		'total_air_port_10_30':fields.float(' air port 10_30'),
		'service_total_port_10_30':fields.float('port 10_30 '),
		'service_total_10_20':fields.float('cleaning 10_20'),
		'total_port_10_30':fields.float('port 10_30 '),
		'service_total_air_port_10_30':fields.float(' air port 10_30'),
		'total_10_20':fields.float('cleaning 10_20')
	}

	def psd_print_monthly_report(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
		        cr.execute("SELECT pg_get_functiondef(oid) FROM pg_proc WHERE  proname = 'account_name_function'") 
                        is_function=cr.fetchone()
                        if not is_function :
                                cr.execute("""CREATE OR Replace FUNCTION account_name_function()
                                RETURNS double precision AS $sum$
                                declare
                                sum double precision ;
                                begin
                                update account_account aa set name=(case when aa.name ilike '%15.0%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 15.00%'
		when aa.name ilike '%14.5%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 14.50%'
		when aa.name ilike '%14.0%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 14.00%'
		when aa.name ilike '%12.36%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 12.36%'
		when aa.name ilike '%12.24%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 12.24%'
		when aa.name ilike '%10.30%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 10.30%'
		when aa.name ilike '%10.20%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 10.20%'
	        else
		aa.name end) where aa.account_selection='against_ref';
		
		                update cofb_sales_receipts csr set tax_rate=(case when csr.tax_rate='taxable_15_0' then '15.0'
						when csr.tax_rate='taxable_14_5' then '14.5'
						when csr.tax_rate='taxable_14_00' then '14.0'
						when csr.tax_rate='taxable_12_36' then '12.36'
						when csr.tax_rate='taxable_12_24' then '12.24'
						when csr.tax_rate='taxable_10_30' then '10.30'
						when csr.tax_rate='taxable_10_20' then '10.20' else
						csr.tax_rate end);
                                return sum;
                                end;
                                $sum$
                                LANGUAGE plpgSQL;""")
                                cr.execute("SELECT account_name_function()") 
                                
			from_date = res.from_date
			to_date = res.to_date
			monthly_selection = res.monthly_selection

			if not monthly_selection:
				raise osv.except_osv(('Alert'),('Please select type.'))
			if from_date == False:
				raise osv.except_osv(('Alert'),('Please select From Date.'))
			if to_date == False:
				raise osv.except_osv(('Alert'),('Please select To Date.'))

			if monthly_selection == 'stmt_collection':
				self.stmt_collection(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'summary_accounts':
				now=datetime.now().day

				now_date=datetime.strftime(datetime.now(),'%Y-%m')+'-01'
				if now in (1,2,3,4,5):
					date_current = datetime.strptime(now_date, "%Y-%m-%d")
					prev_date=date_current-relativedelta(months=1)
					account_srch=self.pool.get('account.account').search(cr,uid,[('account_selection','in',('iob_two','cash','iob_one'))])
					if account_srch:
						self.pool.get('account.account').write(cr,uid,account_srch[0],{'from_date_again':prev_date})
						self.pool.get('account.account').opening_bal_scheduler_again(cr,uid, [account_srch[0]])
				self.summary_of_accounts(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'stmt_bank_charges':
				self.statement_of_bank_charges(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'bank_slip_book':
				self.bank_slip_book_iob_one(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'stmt_cash_withdrawal':
				self.cash_withdrawal_cheque_payment(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'stmt_tds_recoveries':
				self.stmt_tds_recoveries(cr,uid,ids,from_date,to_date,context=context)
				
			if monthly_selection == 'stmt_recoveries':	
				self.stmt_recoveries(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'stmt_funds_transfer_a/c_II':
				self.stmt_funds_transfer_to_two(cr,uid,ids,from_date,to_date,context=context)
				
			if monthly_selection == 'stmt_funds_remitted':
				self.stmt_funds_remitted(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'stmt_debtors_reconciliation':
				self.stmt_debtors_reconciliation(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'cash_bank_payment_extract':
				self.cash_bank_payment_extract(cr,uid,ids,from_date,to_date,context=context)
			
			if monthly_selection == 'summary_service_tax':
				self.stmt_summary_service_tax(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'bank_reconciliation_iob_one':
					self.bank_reconciliation_iob_one(cr,uid,ids,from_date,to_date,context=context)
					
			if monthly_selection == 'bank_reconciliation_iob_two':
					self.bank_reconciliation_iob_two(cr,uid,ids,from_date,to_date,context=context)

			if monthly_selection == 'cse_collection_summary':
					self.cse_collection_summary(cr,uid,ids,from_date,to_date,context=context)

		for report in self.browse(cr,uid,ids):
			monthly_selection = report.monthly_selection
			from_date = report.from_date
			date = datetime.strptime(from_date, "%Y-%m-%d")
			date_year = date.year
			
			bank_three_id=self.pool.get('account.account').search(cr,uid,[('receive_bank_no', '=' ,'bank_three')])
			bank_three_id= bank_three_id if bank_three_id else False
			data = self.pool.get('monthly.report').read(cr, uid, [report.id],context)
			datas = {
					'ids': ids,
					'model': 'monthly.report',
					'form': data
					}
                        if uid != 1:
                                file_format='pdf'
                                doc=str(monthly_selection) if monthly_selection else ''
                                doc_name='monthly_report'
                                self.pool.get('user.print.detail').update_rec(cr,uid,file_format,doc,doc_name)
                                
			if monthly_selection == 'stmt_collection' and bank_three_id  :
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'psd.statement.collection.old.records.new1',
						'datas': datas,
						}
			if monthly_selection == 'stmt_collection' and  bank_three_id == False:
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'psd.statement.collection.old.records',
						'datas': datas,
						}

			if monthly_selection == 'summary_accounts':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'psd.summary.accounts',
						'datas': datas,
					}

			if monthly_selection == 'stmt_bank_charges':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.bank.charges',
						'datas': datas,
					}

			if monthly_selection == 'bank_slip_book':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'slip.book.one',
						'datas': datas,
					}

			if monthly_selection == 'stmt_cash_withdrawal':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'cash.withdraw.cheque.payment',
						'datas': datas,
					}

			if monthly_selection == 'stmt_tds_recoveries':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.tds.recoveries',
						'datas': datas,
					}


			if monthly_selection == 'stmt_recoveries':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.recoveries',
						'datas': datas,
					}

			if monthly_selection == 'stmt_funds_transfer_a/c_II':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.funds.transferred.two',
						'datas': datas,
					}
			
			if monthly_selection == 'stmt_funds_remitted':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.remitted',
						'datas': datas,
					}


			if monthly_selection == 'stmt_debtors_reconciliation':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.debtors.reconciliation',
						'datas': datas,
					}
			if monthly_selection == 'cash_bank_payment_extract':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.of.payment',
						'datas': datas,
					}

			if monthly_selection == 'bank_reconciliation_iob_one':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'bank.reconciliation.iob.one',
					'datas': datas,
				}
				
			if monthly_selection == 'bank_reconciliation_iob_two':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'bank.reconciliation.iob.two',
					'datas': datas,
				}
			if monthly_selection == 'summary_service_tax':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'stmt.summary.service.tax',
					'datas': datas,
				}

			if monthly_selection == 'cse_collection_summary':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'cse_collection_summary',
					'datas': datas,
					}

					
			'''if monthly_selection == 'credit_note_register':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'credit.note.register',
						'datas': datas,
					}'''
					
		return True


monthly_report()


class outstanding_list(osv.osv):
	_inherit='outstanding.list'
	_columns={
		'today_date':fields.date('Today Date'),
		'select':fields.char('Select',size=40),
	}
outstanding_list()


class invoice_search_master(osv.osv):
	_inherit = "invoice.search.master"

	# def _check_transfered(self, cr, uid, ids, field_name, args, context=None):
	
	#   res = {}
	#   for rec in self.browse(cr, uid, ids, context):
	#       print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2contract",rec
	#       print "!!!!!!!!!!!!!!!!!!!!!!!!!!!", rec.partner_id
	#       res[rec.id]=False
	#       if rec.partner_id:
	#           if rec.partner_id.is_transfered:
	#               res[rec.id]=True
	#   return res

	def search_product_sales_invoice(self,cr,uid,ids,context=None):
		product_invoice_obj = self.pool.get('invoice.adhoc.master')
		invoice_adhoc = self.pool.get('invoice.adhoc')
		res = False
		domain = []
		true_items = []
		rec = self.browse(cr, uid,ids[0])
		self.write(cr,uid,ids[0],{'not_found':False,'search_invoice_line':[(6, 0, 0)]})
		if rec.invoice_number:
			true_items.append('invoice_number')
		if rec.customer_id:
			true_items.append('partner_id.ou_id')
		if rec.cust_name:
			true_items.append('cust_name')
		if rec.state:
			true_items.append('state')
		if rec.web_order_no:
			true_items.append('web_order_no')
		if rec.delivery_order_no:
			true_items.append('delivery_order_no')
		if rec.delivery_note_date:
			true_items.append('delivery_note_date')
		if rec.product_id:
			true_items.append('product_id')
		if rec.date_from:
			true_items.append('date_from')
		if rec.date_to:
			true_items.append('date_to')
		if rec.order_no:
			true_items.append('order_no')
		for true_item in true_items:
			if true_item == 'invoice_number':
				domain.append(('invoice_number', 'ilike', rec.invoice_number))
			if true_item == 'cust_name':
				domain.append(('customer_id', 'ilike', rec.cust_name.id))
			if true_item == 'partner_id.ou_id':
				domain.append(('partner_id.ou_id', 'ilike', rec.customer_id))
			if true_item == 'state':
				domain.append(('status', 'ilike', rec.state))
			if true_item == 'web_order_no':
				domain.append(('web_order_no', 'ilike', rec.web_order_no))
			if true_item == 'order_no':
				domain.append(('erp_order_no', 'ilike', rec.order_no))
			if true_item == 'delivery_order_no':
				domain.append(('delivery_note_no', 'ilike', rec.delivery_order_no))
			if true_item == 'date_from':
				domain.append(('invoice_date','>=',rec.date_from))
			if true_item == 'date_to':
				domain.append(('invoice_date','<=',rec.date_to))
			if true_item == 'delivery_note_date':
				domain.append(('delivery_note_date', '=', rec.delivery_note_date))
			if true_item == 'product_id':
				search_prod = invoice_adhoc.search(cr,uid,[('product_id','=',rec.product_id.id)])
				lines_list = []
				for x in invoice_adhoc.browse(cr,uid,search_prod):
					if not x.product_invoice_id.id in lines_list:
						lines_list.append(x.product_invoice_id.id)
				search_quotation_prod = product_invoice_obj.search(cr,uid,[('id','in',lines_list)])
				domain.append(('id','in',search_quotation_prod))
		domain.append(('is_product_invoice','=',True))
		product_invoice_ids = product_invoice_obj.search(cr, uid,domain, context=context)
		if not product_invoice_ids:
			self.write(cr,uid,ids[0],{'not_found':True})
			return res
		else:
			res = self.write(cr, uid, ids[0], 
				{
					'search_invoice_line': [(6, 0, product_invoice_ids)]
				})
			return res


	_columns={
		'invoice_date':fields.datetime('Invoice Date'),
		'order_no':fields.char('Product Order No',size=40),
		'delivery_order_no':fields.char('Delivery Note No',size=40),
		'delivery_note_date':fields.date('Delivery Note Date'),
		'erp_order_no':fields.char('Order No',size=40),
		'erp_order_date':fields.datetime('Order Date'),
		'web_order_no':fields.char('Web Order No',size=40),
		'web_order_date':fields.datetime('Web Order Date'),
		'expected_delivery_date':fields.date('Expected Delivery Date'),
		'pse':fields.many2one('hr.employee','PSE'),
		'user':fields.char('User',size=40),
		'is_product_invoice':fields.boolean('Is Product Invoice'),
		'not_found':fields.boolean('Not Found'),
		'product_id':fields.many2one('product.product','Product Name'),
		# 'is_transfered': fields.function(_check_transfered, string="Is Transfered", type="boolean", store=True),

		}


	def search_product_composite_invoice(self,cr,uid,ids,context=None):
		product_invoice_obj = self.pool.get('invoice.adhoc.master')
		invoice_adhoc = self.pool.get('invoice.adhoc')
		res = False
		domain = []
		true_items = []
		rec = self.browse(cr, uid,ids[0])
		self.write(cr,uid,ids[0],{'not_found':False,'search_invoice_line':[(6, 0, 0)]})
		if rec.invoice_number:
			true_items.append('invoice_number')
		if rec.customer_id:
			true_items.append('customer_id')
		if rec.cust_name:
			true_items.append('cust_name')
		if rec.state:
			true_items.append('state')
		if rec.web_order_no:
			true_items.append('web_order_no')
		if rec.delivery_order_no:
			true_items.append('delivery_order_no')
		if rec.delivery_note_date:
			true_items.append('delivery_note_date')
		if rec.product_id:
			true_items.append('product_id')
		for true_item in true_items:
			if true_item == 'invoice_number':
				domain.append(('invoice_number', 'ilike', rec.invoice_number))
			if true_item == 'cust_name':
				domain.append(('customer_id', 'ilike', rec.cust_name.id))
			if true_item == 'customer_id':
				domain.append(('customer_id', 'ilike', rec.customer_id))
			if true_item == 'state':
				domain.append(('status', 'ilike', rec.state))
			if true_item == 'web_order_no':
				domain.append(('web_order_no', 'ilike', rec.web_order_no))
			if true_item == 'delivery_order_no':
				domain.append(('delivery_order_no', 'ilike', rec.delivery_order_no))
			if true_item == 'delivery_note_date':
				domain.append(('delivery_note_date', 'ilike', rec.delivery_note_date))
			if true_item == 'product_id':
				search_prod = invoice_adhoc.search(cr,uid,[('product_id','=',rec.product_id.id)])
				lines_list = []
				for x in invoice_adhoc.browse(cr,uid,search_prod):
					if not x.product_invoice_id.id in lines_list:
						lines_list.append(x.product_invoice_id.id)
				search_quotation_prod = product_invoice_obj.search(cr,uid,[('id','in',lines_list)])
				domain.append(('id','in',search_quotation_prod))
		domain.append(('bird_pro','=',True))
		product_invoice_ids = product_invoice_obj.search(cr, uid, domain, context=context)
		if not product_invoice_ids:
			self.write(cr,uid,ids[0],{'not_found':True})
			return res
		else:
			res = self.write(cr, uid, ids[0], 
				{
					'search_invoice_line': [(6, 0, product_invoice_ids)]
				})
			return res

invoice_search_master()


class product_transfer(osv.osv):
	_inherit = "product.transfer"
	_columns={
		'product_invoice_id':fields.many2one('invoice.adhoc.master','Product Invoice'),
		}
product_transfer()

class transfer_series(osv.osv):
	_inherit = "transfer.series"
	_columns={
		'invoice_id':fields.many2one('invoice.adhoc.master','Invoice'),
		}
transfer_series()


class job_history(osv.osv):
	_inherit = "job.history"
	_columns = {
		'invoice_id':fields.many2one('invoice.adhoc.master','Invoice ID'),

	}

class invoice_adhoc_master(osv.osv):
	_inherit= 'invoice.adhoc.master'
	_order = 'id desc'

	def _check_transfered(self, cr, uid, ids, field_name, args, context=None):
		res = {}
		for rec in self.browse(cr, uid, ids, context):
			partner_id = self.pool.get('invoice.adhoc.master').browse(cr,uid,rec.id).customer_id
			res[rec.id]=False
			partner_id_int = int(partner_id)
			if partner_id:
				transferred_val = self.pool.get('res.partner').browse(cr,uid,partner_id_int).is_transfered
				if transferred_val:
					res[rec.id]=True
		return res

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_corp_company(self, cr, uid, context=None):
		res = False
		company_obj = self.pool.get('res.company')
		search_corp = company_obj.search(cr,uid,[('branch_type','=','corp_office')])
		if search_corp:
			res = search_corp[0]
		return res

	def _get_regd_company(self, cr, uid, context=None):
		res = False
		company_obj = self.pool.get('res.company')
		search_regd = company_obj.search(cr,uid,[('branch_type','=','regd_office')])
		if search_regd:
			res = search_regd[0]
		return res

	_columns = {
		'invoice_type':fields.selection([('service_invoice','Service Invoice'),('product_invoice','Product Invoice'),('Scrap Sale Invoice','Scrap Sale Invoice')],'Invoice Type'),
		'pse':fields.many2one('hr.employee','PSE'),
		'service_order_id':fields.many2one('amc.sale.order','AMC Order'),
		'amc_inv_id':fields.many2one('amc.invoice.line','AMC invoice line Id'),
		'quotation_no':fields.char('Quotation No',size=20),
		'so_reference_no':fields.char('S.O. Reference No',size=20),
		'so_reference_date':fields.date('S.O. Reference Date'),
		'service_type':fields.selection([('Annual Maintainance Contract','Annual Maintainance Contract'),
					('Repairs & Maintainance Charges','Repairs & Maintainance Charges'),
					('Commissioning & Installation Charges','Commissioning & Installation Charges'),
					('Exempted Service','Exempted Service'),
					('Maintainance or Repair Service','Maintainance or Repair Service')
					],'Service Type *'),
		'classification': fields.selection([('Comprehensive','Comprehensive'),
					('Non Comprehensive','Non Comprehensive')],'Classification *'),
		'order_period_from': fields.date('Order Period From'),
		'order_period_to': fields.date('Order Period To'),
		'site_address': fields.many2one('res.partner.address','Site Address'),
		'billing_address': fields.many2one('res.partner.address','Billing Address'),
		'contact_no':fields.char('Contact No',size=30),
		'delivered_by':fields.char('Delivered By',size=40),
		'delivery_note_no':fields.char('Delivery Note No',size=40),
		'delivery_order_no':fields.char('Delivery Order No',size=40),
		'delivery_note_date':fields.date('Delivery Note Date'),
		'erp_order_no':fields.char('Product Order No',size=40),
		'erp_order_date':fields.date('Product Order Date'),
		'web_order_no':fields.char('Web Order No',size=40),
		'web_order_date':fields.date('Web Order Date'),
		'expected_delivery_date':fields.date('Expected Delivery Date'),
		'delivery_address':fields.text('Delivery Address',size=300),
		'billing_location':fields.text('Billing  Location',size=300),
		'billing_location_id':fields.many2one('res.partner.address','Billing Location'),
		'against_form':fields.selection([("against_form_c","Against Form 'C'"),("against_form_h","Against Form 'H'")],'Against Form'),
		'po_ref':fields.char('P.O Reference',size=40),
		'po_ref_date':fields.date('P.O Reference Date'),
		'user':fields.char('User',size=40),
		'product_transfer_ids':fields.one2many('product.transfer','product_invoice_id',string='Product List'),
		'service_invoice_lines':fields.one2many('invoice.adhoc','service_invoice_id','Invoice Lines'),
		'product_invoice_lines':fields.one2many('invoice.adhoc','product_invoice_id','Invoice Lines'),
		'total_weight':fields.float('Total weight in kg.(Estimated)'),
		'estimated_value':fields.float('Estimated value(Rs.)'),
		'mode_transport': fields.selection([('transport','Transport'),('hand_delivery','Hand Delivery'),('courier','Courier')],'Mode of Transport'),
		'person_name':fields.char('Person Name',size=100),
		'transporter':fields.many2one('warehouse.transporters','Transporter'),
		#'transporter':fields.char('Transporter',size=100),
		'vehicle_no':fields.char('Vehicle No.',size=100),
		'driver_name':fields.char('Driver Name',size=100),
		'mobile_no':fields.char('Mobile No.',size=10),
		'lr_no':fields.char('L.R. No.',size=100),
		'lr_date':fields.date('L.R.Date'),
		'delivery_date':fields.date('Date of Delivery(Expected)'),
		'freight_amount':fields.float('Freight Amount'),
		'freight_amount_invoice':fields.float('Freight Amount'),
		'fr_tax_amount':fields.float('Freight Tax Amount'),
		'transfer_series_ids':fields.one2many('transfer.series','invoice_id',string='Transfer Series'),
		'is_product_invoice':fields.boolean('Is Product Invoice'),
		'product_cost':fields.float('Product Cost'),
		# 'total_vat':fields.float('Total VAT/CST'),
		'bird_pro':fields.boolean('Bird Pro'),
		'bird_pro_charge':fields.float('Bird Pro Installation Charges'),
		'total_st':fields.float('Bird Pro Service Tax'),
		'basic_charge': fields.float('Basic Amount'),
		'order_total_vat':fields.float('Total VAT/CST'),
		'service_tax_14': fields.float('Service Tax'),
		'sb_cess_0_50': fields.float('S B Cess'),
		'kk_cess_0_50': fields.float('K K Cess'),
		'service_order_grand_total': fields.float('Grand Total'),
		'product_order_grand_total': fields.float('Grand Total'),
		'search_sevice_invoice_id':fields.many2one('search.service.invoice','Search Service Invoice'),
		'is_transfered': fields.function(_check_transfered, string="Is Transfered", type="boolean", store=True),
		'invoice_no_generated':fields.boolean('Invoice No Generated'),
		'credit_inv_batch_id':fields.one2many('credit.invoice.batch.quantity','invoice_adhoc_id','Credit Invoice Batches'),
		'credit_note_id': fields.many2one('credit.note','Credit Note'),
		'history_line':fields.one2many('job.history','invoice_id','Job History'),
		'company_id':fields.many2one('res.company','Company ID'),
		'corp_office_id':fields.many2one('res.company','Corporate Office'),
		'regd_office_id':fields.many2one('res.company','Registered Office'),
		'pse_code':fields.char('PSE Code',size=100),
		'subtotal':fields.float('Subtotal'),
		'product_discount':fields.float('Product Discount %'), 
		'product_discount_amount':fields.float('Product Discount in Amount'),
		}

	_defaults={
		'company_id': _get_company,
		'corp_office_id': _get_corp_company,
		'regd_office_id': _get_regd_company,
	}

	# def psd_receipt(self, cr, uid, ids, vals, context=None):
	# 	result = account_security = account_itds = ''
	# 	chart_account_obj = self.pool.get('account.account')
	# 	for res in self.browse(cr,uid,ids):
	# 			if res.pending_amount < res.grand_total_amount:
	# 				partial_payment_amount = res.pending_amount
	# 			else:
	# 				partial_payment_amount = res.grand_total_amount
	# 			invoice_number = res.invoice_number
	# 			itds_total = ''
	# 			itds_rate = 0.0
	# 			if res.check_process_invoice == False:
	# 				self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,{'invoice_id_receipt':'','check_invoice':False})    
	# 			if invoice_number == False:
	# 				raise osv.except_osv(('Alert'),('There is no Invoice Number for this record.'))
	# 			product_account = chart_account_obj.search(cr, uid, [('invoice_type','=','product')], context=context)	
	# 			ct_account = chart_account_obj.search(cr, uid, [('invoice_type','=','composite')], context=context)	
	# 			if res.invoice_type == 'service_invoice':
	# 				service_account = res.tax_one2many[0].account_tax_id.chart_account_id.id
	# 				account_id = service_account
	# 			elif res.invoice_type == 'product_invoice' and res.bird_pro == False:
	# 				account_id = product_account[0]
	# 			elif res.invoice_type == 'product_invoice' and res.bird_pro == True:
	# 				account_id = ct_account[0]
	# 			srch1 = self.pool.get('account.account').search(cr,uid,[('account_selection','=','itds_receipt')])
	# 			srch2 = self.pool.get('account.account').search(cr,uid,[('account_selection','=','security_deposit')])
	# 			for acc_id in self.pool.get('account.account').browse(cr,uid,srch2):
	# 				account_security = acc_id.id
	# 			for acc_id in self.pool.get('account.account').browse(cr,uid,srch1):
	# 				account_itds = acc_id.id
	# 				itds_rate = acc_id.itds_rate if acc_id.itds_rate else 0.0
	# 			create_id = self.pool.get('account.sales.receipts').create(cr,uid,{
	# 									'psd_accounting': True,
	# 									'customer_name':res.partner_id.id,
	# 									'customer_id_invisible':res.partner_id.ou_id,
	# 									'acc_status':'against_ref',
	# 									'chek_receipt':True,
	# 									'invoice_number':res.invoice_number,
	# 									'account_select_boolean':True,})
	# 			result = self.pool.get('account.sales.receipts.line').create(cr,uid,{
	# 									'customer_name':res.partner_id.id,
	# 									'receipt_id':create_id,
	# 									'acc_status':'against_ref',
	# 									'account_id':account_id,
	# 									'type':'credit',
	# 									'credit_amount':res.pending_amount,##s
	# 									'check_against_ref_status':False})				
	# 			if itds_rate: 
	# 				itds_rate_per = itds_rate * 0.01
	# 				itds_total = res.pending_amount * itds_rate_per
	# 			else:
	# 				raise osv.except_osv(('Alert'),('Please give Itds Rate'))
	# 			result_itds = self.pool.get('account.sales.receipts.line').create(cr,uid,{
	# 				'customer_name':res.partner_id.id,
	# 				'receipt_id':create_id,
	# 				'acc_status':'against_ref',
	# 				'account_id':account_itds,
	# 				'type':'debit',
	# 				'credit_amount':0.0,
	# 				'debit_amount':round(itds_total),
	# 				'check_against_ref_status':False})
					
	# 			result_itds = self.pool.get('account.sales.receipts.line').create(cr,uid,{
	# 				'customer_name':res.partner_id.id,
	# 				'receipt_id':create_id,
	# 				'acc_status':'against_ref',
	# 				'account_id':account_security,
	# 				'type':'debit',
	# 				'credit_amount':0.0,
	# 				'check_against_ref_status':False})

	# 			self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,{
	# 						'invoice_id_receipt':result,
	# 						'check_invoice':True,
	# 						'partial_payment_amount':partial_payment_amount})
			
	# 			self.write(cr,uid,res.id,{'check_against_reference':True})
	# 			#self.pool.get('account.sales.receipts').write(cr,uid,res.id,{'invoice_id_receipt':create_id})
	# 			view = self.pool.get('ir.model.data').get_object_reference(
	# 				cr, uid, 'psd_accounting', 'psd_account_sales_receipts_form')
	# 			view_id = view and view[1] or False
	# 			return {
	# 				'name':'Sales Receipts',
	# 				'view_mode': 'form',
	# 				'view_id': view_id,
	# 				'view_type': 'form',
	# 				'res_model': 'account.sales.receipts',
	# 				'res_id':create_id,
	# 				'type': 'ir.actions.act_window',
	# 				'target': 'current',
	# 				'domain': '[]',
	# 				'context': context,
	# 				}		

	def psd_receipt(self, cr, uid, ids, vals, context=None):
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
							'partial_payment_amount':res.pending_amount,
						})
				if invoice_number == False:
					raise osv.except_osv(('Alert'),('There is no Invoice Number for this record.'))

				srch = self.pool.get('account.account').search(cr,uid,[('name','=','Sundry Debtors - Product')])
				if srch:
					srch_id=srch[0] if isinstance(srch,(list,tuple)) else srch
					acc_id =self.pool.get('account.account').browse(cr,uid,srch_id)
					account_id = acc_id.id
				else:
					raise osv.except_osv(('Alert'),('Chart of accounts not configured for "Sundry Debtors - Product" account')) 
				srch1 = self.pool.get('account.account').search(cr,uid,[('account_selection','=','itds_receipt')])
				srch2 = self.pool.get('account.account').search(cr,uid,[('account_selection','=','security_deposit')])
				for acc_id in self.pool.get('account.account').browse(cr,uid,srch2):
					account_security = acc_id.id
				for acc_id in self.pool.get('account.account').browse(cr,uid,srch1):
					account_itds = acc_id.id
					itds_rate = acc_id.itds_rate if acc_id.itds_rate else 0.0
				adhoc_ids1 = adhoc_obj.search(cr,uid,[('product_invoice_id','=',res.id)])
				if adhoc_ids1:
					adhoc_ids = adhoc_ids1
					adhoc_data = adhoc_obj.browse(cr,uid,adhoc_ids[0])
					address_id = adhoc_data.product_invoice_id.billing_location_id.id

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
				return {
					'name':'Sales Receipts',
					'view_mode': 'form',
					'view_id': False,
					'view_type': 'form',
					'res_model': 'account.sales.receipts',
					'res_id':create_id,
					'views':[(form_view and form_view[1] or False, 'form')],
					'type': 'ir.actions.act_window',
					'target': 'current',
					'domain': '[]',
					'context': context,
					}

	def reload_invoice_lines(self, cr, uid, ids, context=None):	
		rec = self.browse(cr, uid, ids[0])
		credit_note_line_id = rec.credit_invoice_id.id	
		# adhoc_master_ids = self.search(cr, uid, [('check_credit_note','=',True),('credit_invoice_id','=',credit_note_line_id)], context=context)	
		# if len(adhoc_master_ids) > 1:
		# 	raise osv.except_osv(_('Warning!'),_("Process one invoice at a time!")) 
		models_obj = self.pool.get('ir.model.data')
		form_id = models_obj.get_object_reference(cr, uid, 'psd_accounting', 'psd_credit_note_invoice_pop_up_form')
		context.update({'credit_note_line_id':credit_note_line_id})
		return {
			   'name':'Invoice Lines',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'credit.note.invoice.pop.up',
			   'type': 'ir.actions.act_window',
			   'target': 'new',
			   'context': context
		}	


	def open_service_invoice(self,cr,uid,ids,context=None):
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_service_invoice_form')
		res = self.browse(cr,uid,ids[0])
		return {
					'type': 'ir.actions.act_window',
					'name':'Service Invoice',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'invoice.adhoc.master',
					'res_id':ids[0],
					'view_id':form_view[1],
					'target':'current',
					'context': context,
				}
	
	def view_invoice(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			if res.adhoc_invoice == True:
				name = "Adhoc Invoice"
			else :
				name = "Invoice"
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'invoice_adhoc_id')
			print"==========================",form_view
			
			return{
						'type': 'ir.actions.act_window',
						'name':name,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'invoice.adhoc.master',
						'res_id':ids[0],
						'view_id':form_view[1],
						'priority':20,
						'target':'current',
						'context': context
			}



	def psd_view_invoice(self,cr,uid,ids,context=None):

		for res in self.browse(cr,uid,ids):
			if res.bird_pro == True:
				name = "Composite Invoice"
			else :
				name = "Product Invoice"
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_invoice_adhoc_id')
			print"==========================",form_view
			
			return{
						'type': 'ir.actions.act_window',
						'name':name,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'invoice.adhoc.master',
						'res_id':ids[0],
						'view_id':form_view[1],
						'priority':20,
						'target':'current',
						'context': context}
	
	def psd_print_invoice(self, cr, uid, ids, context=None):
		corp_office_id = False
		regd_office_id = False
		company_obj = self.pool.get('res.company')
		cur_rec = self.browse(cr,uid,ids[0])
		print_count=cur_rec.print_count+1
		search_corp = company_obj.search(cr,uid,[('branch_type','=','corp_office')])
		search_regd = company_obj.search(cr,uid,[('branch_type','=','regd_office')])
		if search_corp:
			corp_office_id = search_corp[0]
		if search_regd:
			regd_office_id = search_regd[0]
		self.write(cr,uid,cur_rec.id,{'print_count':print_count,'corp_office_id':corp_office_id,'regd_office_id':regd_office_id})

		# if cur_rec.status == 'open':
		# 	self.write(cr,uid,cur_rec.id,{'status':'printed'})
		# # stock_no=self.browse(cr,uid,ids[0]).erp_order_no
		# # print stock_no
		# # stock_ids=self.pool.get('stock.transfer').search(cr,uid,[('sale_order_no','=',stock_no)])
		# # stock_ids=stock_ids[0]
		# # data = self.pool.get('stock.transfer').read(cr, uid, [stock_ids], context=context)
		# # datas = {
		# # 		'ids': [stock_ids],
		# # 		'model': 'stock.transfer',
		# # 		'form': data
		# # 		}
		# # return {
		# # 	'type': 'ir.actions.report.xml',
		# # 	'report_name': 'stock_transfer_invoice',
		# # 	'datas': datas,
		# # 	}
		# self.write(cr,uid,cur_rec.id,{'print_count':print_count,'corp_office_id':corp_office_id,'regd_office_id':regd_office_id})
		datas = {
				 'model': 'invoice.adhoc.master',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		if cur_rec.status == 'open':
			self.write(cr,uid,cur_rec.id,{'status':'printed'})
		return {'type': 'ir.actions.report.xml', 'report_name': 'product_invoice', 'datas': datas, 'nodestroy': True}

	def print_service_invoice(self, cr, uid, ids, context=None):
		corp_office_id = False
		regd_office_id = False
		company_obj = self.pool.get('res.company')
		cur_rec = self.browse(cr,uid,ids[0])
		print_count=cur_rec.print_count+1
		search_corp = company_obj.search(cr,uid,[('branch_type','=','corp_office')])
		search_regd = company_obj.search(cr,uid,[('branch_type','=','regd_office')])
		if search_corp:
			corp_office_id = search_corp[0]
		if search_regd:
			regd_office_id = search_regd[0]
		self.write(cr,uid,cur_rec.id,{'print_count':print_count})
		datas = {
				 'model': 'invoice.adhoc.master',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		if cur_rec.status == 'open':
			self.write(cr,uid,cur_rec.id,{'status':'printed'})
		return {'type': 'ir.actions.report.xml', 'report_name': 'service.invoice', 'datas': datas, 'nodestroy': True}

	def psd_view_invoice_new(self,cr,uid,ids,context=None):
		for rec in self.browse(cr, uid, ids):
			c_code = rec.cce_code if rec.cce_code else None
			self.write(cr,uid,rec.id,{'cce_code':c_code})
			print "XXXXXXXXXXXXXXXXXXXx----------------------------------------------------"
			return self.psd_view_invoice(cr, uid, ids, context)


	def cancel_product_invoice(self,cr,uid,ids,context=None):### used for cancel invoice
		rec = self.browse(cr,uid,ids[0])
		delivery_order_obj = self.pool.get('stock.transfer')
		if rec.cancel_boolean:
			if not rec.canceled_date:
				raise osv.except_osv(('Alert'),('Please Enter Cancel Date'))
			if rec.canceled_date:
				mon=datetime.today().month
				yer=datetime.today().year
				cancel_mon=datetime.strptime(rec.invoice_date,"%Y-%m-%d").month
				cancel_yer=datetime.strptime(rec.invoice_date,"%Y-%m-%d").year
				if mon != cancel_mon or cancel_yer != yer :
					raise osv.except_osv(('Alert'),("You can't cancel this Invoice "))	
			if len(rec.cancel_reason) <8:               
				raise osv.except_osv(('Alert'),('Please Enter Reason at least 8 characters for Cancellation'))
			delivery_order_id = delivery_order_obj.search(cr,uid,[('delivery_challan_no','=',str(rec.delivery_note_no))])
			print delivery_order_id,'oddd'
			delivery_order_obj.nsd_cancel_stock_transfer(cr,uid,delivery_order_id,context=None)
			self.write(cr,uid,ids,{'status':'cancelled'})
		return True

	def service_inv_cancel_button(self, cr, uid, ids, context=None):
		rec = self.browse(cr,uid,ids[0])
		amc_sale_order_obj = self.pool.get('amc.sale.order')
		inv_line_obj = self.pool.get('invoice.adhoc')
		tax_line_obj = self.pool.get('invoice.tax.rate')
		amc_inv_line = self.pool.get('amc.invoice.line')
		service_order_id = rec.service_order_id.id
		amc_inv_id = rec.amc_inv_id.id
		if rec.service_invoice_lines:
			for line in rec.service_invoice_lines:
				inv_line_obj.unlink(cr,uid,line.id,context=None)
		if rec.tax_one2many:
			for line in rec.tax_one2many:
				tax_line_obj.unlink(cr,uid,line.id,context=None)
		self.unlink(cr,uid,ids,context=None)
		amc_inv_line.write(cr,uid,amc_inv_id,{'pay_check':False,'invoice_done':False})
		amc_sale_order_obj.write(cr,uid,service_order_id,{'invoiced':False})
		return {
				'view_type': 'form',
				'view_mode': 'form',
				'name': _('Service Order'),
				'res_model': 'amc.sale.order',
				'res_id': service_order_id,
				'type': 'ir.actions.act_window',
				'target': 'current',
				'context': context,
				'nodestroy': True,
		}

	def product_invoice_cancel(self, cr, uid, ids, context=None):
		rec = self.browse(cr,uid,ids[0])
		delivery_order_obj = self.pool.get('stock.transfer')
		inv_line_obj = self.pool.get('invoice.adhoc')
		tax_line_obj = self.pool.get('invoice.tax.rate')
		if rec.product_invoice_lines:
			for line in rec.product_invoice_lines:
				inv_line_obj.unlink(cr,uid,line.id,context=None)
		if rec.tax_one2many:
			for line in rec.tax_one2many:
				tax_line_obj.unlink(cr,uid,line.id,context=None)
		delivery_order_id = delivery_order_obj.search(cr,uid,[('delivery_challan_no','=',str(rec.delivery_note_no))])
		delivery_order_obj.write(cr,uid,delivery_order_id[0],{'state':'confirmed'})
		view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'psd_warehouse', 'stock_transfer_order_management_form')
		view_id = view and view[1] or False
		self.unlink(cr,uid,ids,context=None)
		return {
				'view_type': 'form',
				'view_mode': 'form',
				'view_id':view_id,
				'name': _('Delivery Order'),
				'res_model': 'stock.transfer',
				'res_id': delivery_order_id[0],
				'type': 'ir.actions.act_window',
				'target': 'current',
				'context': context,
				'nodestroy': True,
		}

	def onchange_freight(self,cr,uid,ids,freight_amount,context=None):
		v={}
		if freight_amount:
			v['freight_amount_invoice'] = freight_amount
		return{'value':v}

	def get_fiscalyear(self,cr,uid,ids,context=None):
		today = datetime.now().date()
		fisc_obj = self.pool.get('account.fiscalyear')
		search_fiscal = fisc_obj.search(cr,uid,[],context=None)
		code=False
		for rec in fisc_obj.browse(cr,uid,search_fiscal):
			if str(today)>=rec.date_start and str(today)<=rec.date_stop:
				code = rec.code
		if code:
			code = code[4:6]
		return code

	def show_details_invoice(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			if res.is_product_invoice == True:
				view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'psd_accounting', 'psd_invoice_adhoc_id')
				view_id = view and view[1] or False
				return{
				'type': 'ir.actions.act_window',
				'name':'Product Invoice',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'invoice.adhoc.master',
				'res_id':ids[0],#'res_id':val,
				'view_id':view_id,
				'target':'current',	
				'context': context,
				}
			elif res.invoice_type == 'service_invoice':
				view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'psd_accounting', 'psd_service_invoice_form')
				view_id = view and view[1] or False
				return{
				'type': 'ir.actions.act_window',
				'name':'Service Invoice',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'invoice.adhoc.master',
				'res_id':ids[0],#'res_id':val,
				'view_id':view_id,
				'target':'current',	
				'context': context,
				}
			else:
				return{
				'type': 'ir.actions.act_window',
				'name':'Invoice',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'invoice.adhoc.master',
				'res_id':ids[0],#'res_id':val,
				'view_id':False,
				'target':'current',	
				'context': context,
				}


	def generate_service_invoice(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		order_obj = self.pool.get('amc.sale.order')
		seq = self.pool.get('ir.sequence').get(cr, uid, 'service.invoice.number')
		user_obj = self.pool.get('res.users')
		code = self.get_fiscalyear(cr,uid,ids,context=None)
		account_tax_obj = self.pool.get('account.tax')
		total_tax_amount = 0
		# seq = count = 0

		grand_total_amount = rec.service_order_grand_total
		pcof_key = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		invoice_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.service_invoice_id
		user_data = user_obj.browse(cr, uid, uid)
		today_date = datetime.now().date()
		year = today_date.year
		year1 = today_date.strftime('%y')
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
		seq_start =1
		# if pcof_key and invoice_id:
		# 	# pcof_key=pcof_key.split('P')				
		# 	# cr.execute("select invoice_number from invoice_adhoc_master where id != "+str(ids[0] if isinstance(ids, list) else ids)+" and invoice_number is not null and invoice_date>='2017-07-01' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' order by invoice_number desc limit 1");
		# 	cr.execute("select cast(count(id) as integer) from invoice_adhoc_master where invoice_number is not null and invoice_date>='2017-07-01' and invoice_number ilike '%SS%' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and invoice_number_ncs is null");
		# 	temp_count=cr.fetchone()
		# 	if temp_count[0]:
		# 		count= temp_count[0]
		# 	seq=int(count+seq_start)
		# 	seq_id = pcof_key +invoice_id +str(financial_year) +str(seq).zfill(5)
		# 	existing_invoice_number = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','=',seq_id)])
		# 	if existing_invoice_number:
		# 		seq_id = pcof_key +invoice_id +str(financial_year) +str(seq+1).zfill(5)
		# invoice_no = seq_id
		invoice_no = str(rec.branch_id.pcof_key)+str(rec.branch_id.service_invoice_id)+financial_year+str(seq)


		res = self.write(cr,uid,ids,{'invoice_number':invoice_no,'invoice_date':datetime.today(),'invoice_no_generated':True})
		invoiced_amt = order_obj.browse(cr,uid,int(rec.service_order_id.id)).invoiced_amount
		invoiced_amount = invoiced_amt + grand_total_amount
		order_obj.write(cr, uid, int(rec.service_order_id.id), 
				{
					'invoiced_amount':invoiced_amount,
					'service_invoice_id': [(4, rec.id)]
				})
		visits = quantity=0.0
		sgst_rate = igst_rate = cgst_rate = cess_rate =''
		sgst_amt = cgst_amt = igst_amt = cess_amt =0.0
		res = self.browse(cr,uid,ids[0])
		for i in res.service_invoice_lines:
			print i			
			# new_address_data = self.pool.get('new.address').browse(cr,uid,i.location.id)
			customer_addr = res.billing_address.state_id.id
			if not customer_addr:
				raise osv.except_osv(('Alert'),('State not defined in customer location!'))
			company_id = res.company_id.state_id.id
			if not company_id:
				raise osv.except_osv(('Alert'),('State not defined in company location!'))
			print customer_addr,company_id
			# if res.service_classification != 'exempted':
			# if company_id != customer_addr:
				# if not res.branch_id.state_id or not new_address_data.state_id:
				# 	raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
				# comparing states from customer location and branch
				# case: if both states are same
			product_tax = i.product_generic_name.product_tax.amount
			rate = i.rate_per_unit
			quantity = i.no_of_units
			visits = i.no_of_visits
			print rate,quantity,visits
			# bb
			amount = rate * quantity * float(visits)
			self.pool.get('invoice.adhoc').write(cr,uid,i.id,{'total':amount})
			cr.commit()
			if company_id == customer_addr:
				# cgst calculation
				# cgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cgst')])
				cgst_tax=account_tax_obj.search(cr,uid,[('name','=','CGST')])
				cgst_data = account_tax_obj.browse(cr,uid,cgst_tax[0])
				if cgst_data.effective_from_date and cgst_data.effective_to_date:
					if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
						cgst_percent = product_tax * 100
						cgst_percent = cgst_percent/2
						cgst_rate = str(cgst_percent)+'%'
						cgst_amt = round((amount*cgst_percent)/100,2)

				else:
					raise osv.except_osv(('Alert'),("CGST tax not configured!"))
				# sgst/utgst calculation
				# case: if state is a union_territory
				if res.billing_address.state_id.union_territory:
					# utgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','utgst')])
					utgst_tax = account_tax_obj.search(cr,uid,[('name','=','UTGST')])
					ut_data = account_tax_obj.browse(cr,uid,utgst_tax[0])
					if ut_data.effective_from_date and ut_data.effective_to_date:
						if str(today_date) >= ut_data.effective_from_date and str(today_date) <= ut_data.effective_to_date:
							# utgst_percent = ut_data.amount * 100
							utgst_percent = product_tax * 100
							utgst_percent = utgst_percent/2
							sgst_rate = str(utgst_percent)+'%'
							sgst_amt = round((amount*utgst_percent)/100,2)
					else:
						raise osv.except_osv(('Alert'),("UTGST tax not configured!"))
				# case: if state is not a union_territory
				else:
					# sgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','sgst')])
					sgst_tax=account_tax_obj.search(cr,uid,[('name','=','SGST')])
					st_data = account_tax_obj.browse(cr,uid,sgst_tax[0])
					if st_data.effective_from_date and st_data.effective_to_date:
						if str(today_date) >= st_data.effective_from_date and str(today_date) <= st_data.effective_to_date:
							# sgst_percent = st_data.amount * 100
							sgst_percent = product_tax * 100
							sgst_percent = sgst_percent/2
							sgst_rate = str(sgst_percent)+'%'
							sgst_amt = round((amount*sgst_percent)/100,2)
					else:
						raise osv.except_osv(('Alert'),("SGST tax not configured!"))
			# case: if both states are different
			else:
				# igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
				igst_tax=account_tax_obj.search(cr,uid,[('name','=','IGST')])
				igst_data = account_tax_obj.browse(cr,uid,igst_tax[0])
				if igst_data.effective_from_date and igst_data.effective_to_date:
					if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
						# igst_percent = igst_data.amount * 100
						igst_percent = product_tax * 100
						igst_rate = str(igst_percent)+'%'
						igst_amt = round((amount*igst_percent)/100,2)
				else:
					raise osv.except_osv(('Alert'),("IGST tax not configured!"))
			# cess calculation
			cess_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cess')])
			if cess_id:
				cess_data = account_tax_obj.browse(cr,uid,cess_id[0])
				if cess_data.effective_from_date and cess_data.effective_to_date:
					if str(today_date) >= cess_data.effective_from_date and str(today_date) <= cess_data.effective_to_date:								
						# cess_percent = cess_data.amount * 100
						cess_percent = product_tax * 100
						cess_rate = str(cess_percent)+'%'
						cess_amt = round((amount*cess_percent)/100,2)

			self.pool.get('invoice.adhoc').write(cr,uid,i.id,
				{
					'hsn_code': i.product_id.hsn_sac_code,
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
			cr.commit()

		cr.execute('select sum(total) from invoice_adhoc where service_invoice_id = %s',(res.id,))
		basic_charge = cr.fetchone()[0]
		cr.execute('select sum(sgst_amt) from invoice_adhoc where service_invoice_id = %s',(res.id,))
		sgst_amt = cr.fetchone()[0]
		cr.execute('select sum(cgst_amt) from invoice_adhoc where service_invoice_id = %s',(res.id,))
		cgst_amt = cr.fetchone()[0]
		cr.execute('select sum(igst_amt) from invoice_adhoc where service_invoice_id = %s',(res.id,))
		igst_amt = cr.fetchone()[0]

		if company_id == customer_addr:
			self.pool.get('invoice.tax.rate').create(cr,uid,{'amount':cgst_amt,'name':cgst_data.name,'account_tax_id':cgst_data.id,'invoice_id':res.id})
			cr.commit()
			if res.billing_address.state_id.union_territory:
				self.pool.get('invoice.tax.rate').create(cr,uid,{'amount':utgst_amt,'name':utgst_data.name,'account_tax_id':utgst_data.id,'invoice_id':res.id})
				cr.commit()
			else:
				self.pool.get('invoice.tax.rate').create(cr,uid,{'amount':sgst_amt,'name':st_data.name,'account_tax_id':st_data.id,'invoice_id':res.id})
				cr.commit()
		else:
			self.pool.get('invoice.tax.rate').create(cr,uid,{'amount':igst_amt,'name':igst_data.name,'account_tax_id':igst_data.id,'invoice_id':res.id})
			cr.commit()


		basic_charge = round(basic_charge)
		total_tax_amount = sgst_amt + cgst_amt + igst_amt
		total_tax_amount = round(total_tax_amount)
		grand_total_amount = round(basic_charge + total_tax_amount)
		res = self.write(cr,uid,ids,{
			# 'invoice_number':invoice_no,
			# 'invoice_date':datetime.today(),
			'cse':res.pse.id,
			'pse':res.pse.id,
			# 'sale_order_id':search_order[0],
			'invoice_no_generated':True,
			'basic_charge': basic_charge,
			'total_tax':total_tax_amount,
			'service_order_grand_total': grand_total_amount,
			'status':'paid',
		})
		cr.commit()
		return True

	def generate_product_invoice(self,cr,uid,ids,context=None):
		res = self.browse(cr,uid,ids[0])
		invoiced_amount = 0.0
		fr_tax_amount = 0.0
		invoice_no = ""
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
		tax_rate = 0.0
		today_date = datetime.now().date()
		order_obj = self.pool.get('psd.sales.product.order')
		account_tax_obj = self.pool.get('account.tax')
		tax_line_obj = self.pool.get('invoice.tax.rate')
		user_obj = self.pool.get('res.users')
		code = self.get_fiscalyear(cr,uid,ids,context=None)
		total_vat = res.order_total_vat
		grand_total_amount = res.product_order_grand_total
		basic_amount = res.basic_charge
		search_order = order_obj.search(cr,uid,[('erp_order_no','=',res.erp_order_no)])
		user_data = user_obj.browse(cr, uid, uid)
		pcof_key = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		invoice_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.psd_product_invoice_id
		year1 = today_date.strftime('%y')
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		seq = count = 0
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
		if res.bird_pro:
			seq = self.pool.get('ir.sequence').get(cr, uid, 'composite.invoice.number')
			# invoice_no = str(res.branch_id.pcof_key)+str(res.branch_id.psd_birdpro_invoice)+code+str(seq)
			invoice_no = str(res.branch_id.pcof_key)+str(res.branch_id.psd_birdpro_invoice)+financial_year+str(seq)
			tax_rate = user_data.company_id.psd_birdpro_invoice
			if tax_rate == "BP":
				tax_rate = "CT"
		else:
			# seq = self.pool.get('ir.sequence').get(cr, uid, 'product.invoice.number')
			# invoice_no = str(res.branch_id.pcof_key)+str(res.branch_id.psd_product_invoice_id)+code+str(seq)
			seq_start =1
			if pcof_key and invoice_id:
				# pcof_key=pcof_key.split('P')				
				# cr.execute("select invoice_number from invoice_adhoc_master where id != "+str(ids[0] if isinstance(ids, list) else ids)+" and invoice_number is not null and invoice_date>='2017-07-01' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' order by invoice_number desc limit 1");
				cr.execute("select cast(count(id) as integer) from invoice_adhoc_master where invoice_number is not null and invoice_date>='2017-07-01' and invoice_number ilike '%PI%' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and invoice_number_ncs is null");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				seq_id = pcof_key +invoice_id +str(financial_year) +str(seq).zfill(5)
				existing_invoice_number = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','=',seq_id)])
				if existing_invoice_number:
					seq_id = pcof_key +invoice_id +str(financial_year) +str(seq+1).zfill(5)
			invoice_no = seq_id
			# invoice_no = str(res.branch_id.pcof_key)+str(res.branch_id.psd_product_invoice_id)+financial_year+str(seq)	
			tax_rate = user_data.company_id.psd_product_invoice_id
		
		if not res.partner_id.gst_no:
			raise osv.except_osv(('Alert'),('Please enter the GST No. for the customer!'))

		for i in res.product_invoice_lines:
			print i			
			# new_address_data = self.pool.get('new.address').browse(cr,uid,i.location.id)

			location = res.billing_location_id.id
			search_new_address=self.pool.get('new.address').search(cr,uid,[('partner_address','=',location)])
			if search_new_address:
				self.pool.get('invoice.adhoc').write(cr,uid,i.id,{'location':search_new_address[0]})
				cr.commit()

			customer_addr = res.billing_location_id.state_id.id
			if not customer_addr:
				raise osv.except_osv(('Alert'),('State not defined in customer location!'))
			company_id = res.company_id.state_id.id
			if not company_id:
				raise osv.except_osv(('Alert'),('State not defined in company location!'))
			print customer_addr,company_id
			# if res.service_classification != 'exempted':
			# if company_id != customer_addr:
				# if not res.branch_id.state_id or not new_address_data.state_id:
				# 	raise osv.except_osv(('Alert'),("State not defined for either current branch or customer location!"))
				# comparing states from customer location and branch
				# case: if both states are same
			product_tax = i.product_id.product_tax.amount
			rate = i.rate
			quantity = i.ordered_quantity
			print rate,quantity
			# bb
			additional_amount = 0.0
			additional_amount = i.discount
			if additional_amount == 0.0 or additional_amount==None:
				amount = rate * quantity
				self.pool.get('invoice.adhoc').write(cr,uid,i.id,{'total':amount,'discount':additional_amount})
				cr.commit()
			else:
				rate = rate + additional_amount
				amount = rate * quantity
				self.pool.get('invoice.adhoc').write(cr,uid,i.id,{'total':amount,'discount':additional_amount})
				cr.commit()
			if company_id == customer_addr:
				# cgst calculation
				cgst_id = account_tax_obj.search(cr,uid,[('name','=','CGST')])
				cgst_data = account_tax_obj.browse(cr,uid,cgst_id[0])
				if cgst_data.effective_from_date and cgst_data.effective_to_date:
					if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
						cgst_percent = product_tax * 100
						cgst_percent = cgst_percent/2
						cgst_rate = str(cgst_percent)+'%'
						cgst_amt = round((i.total*cgst_percent)/100,2)

				else:
					raise osv.except_osv(('Alert'),("CGST tax not configured!"))
				# sgst/utgst calculation
				# case: if state is a union_territory
				if res.billing_location_id.state_id.union_territory:
					utgst_id = account_tax_obj.search(cr,uid,[('name','=','UTGST')])
					ut_data = account_tax_obj.browse(cr,uid,utgst_id[0])
					if ut_data.effective_from_date and ut_data.effective_to_date:
						if str(today_date) >= ut_data.effective_from_date and str(today_date) <= ut_data.effective_to_date:
							# utgst_percent = ut_data.amount * 100
							utgst_percent = product_tax * 100
							utgst_percent = utgst_percent/2
							sgst_rate = str(utgst_percent)+'%'
							sgst_amt = round((i.total*utgst_percent)/100,2)
					else:
						raise osv.except_osv(('Alert'),("UTGST tax not configured!"))
				# case: if state is not a union_territory
				else:
					sgst_id = account_tax_obj.search(cr,uid,[('name','=','SGST')])
					st_data = account_tax_obj.browse(cr,uid,sgst_id[0])
					if st_data.effective_from_date and st_data.effective_to_date:
						if str(today_date) >= st_data.effective_from_date and str(today_date) <= st_data.effective_to_date:
							# sgst_percent = st_data.amount * 100
							sgst_percent = product_tax * 100
							sgst_percent = sgst_percent/2
							sgst_rate = str(sgst_percent)+'%'
							sgst_amt = round((i.total*sgst_percent)/100,2)
					else:
						raise osv.except_osv(('Alert'),("SGST tax not configured!"))
			# case: if both states are different
			else:
				igst_id = account_tax_obj.search(cr,uid,[('name','=','IGST')])
				igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
				if igst_data.effective_from_date and igst_data.effective_to_date:
					if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
						# igst_percent = igst_data.amount * 100
						igst_percent = product_tax * 100
						igst_rate = str(igst_percent)+'%'
						igst_amt = round((i.total*igst_percent)/100,2)
				else:
					raise osv.except_osv(('Alert'),("IGST tax not configured!"))
			# cess calculation
			cess_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cess')])
			if cess_id:
				cess_data = account_tax_obj.browse(cr,uid,cess_id[0])
				if cess_data.effective_from_date and cess_data.effective_to_date:
					if str(today_date) >= cess_data.effective_from_date and str(today_date) <= cess_data.effective_to_date:								
						# cess_percent = cess_data.amount * 100
						cess_percent = product_tax * 100
						cess_rate = str(cess_percent)+'%'
						cess_amt = round((i.total*cess_percent)/100,2)

			temp_amount = tax_rate = tax_rate_amount = 0.0
			if res.tax_one2many:
				for amt in res.tax_one2many:
					tax_rate_amount +=amt.amount
					tax_rate += float(amt.tax_rate)
					print tax_rate
			tax_rate = tax_rate
			print tax_rate
			net_amount = res.total_amount + res.total_tax
			self.pool.get('invoice.adhoc').write(cr,uid,i.id,
				{
					'hsn_code': i.product_id.hsn_sac_code,
					# 'discount': 0,
					'cgst_rate': cgst_rate,
					'cgst_amt': cgst_amt,
					'sgst_rate': sgst_rate,
					'sgst_amt': sgst_amt,
					'igst_rate': igst_rate,
					'igst_amt': igst_amt,
					'cess_rate': cess_rate,
					'cess_amt': cess_amt,			
				})
			cr.commit()

		cr.execute('select sum(total) from invoice_adhoc where product_invoice_id = %s',(res.id,))
		basic_charge = cr.fetchone()[0]
		cr.execute('select sum(sgst_amt) from invoice_adhoc where product_invoice_id = %s',(res.id,))
		sgst_amt = cr.fetchone()[0]
		cr.execute('select sum(cgst_amt) from invoice_adhoc where product_invoice_id = %s',(res.id,))
		cgst_amt = cr.fetchone()[0]
		cr.execute('select sum(igst_amt) from invoice_adhoc where product_invoice_id = %s',(res.id,))
		igst_amt = cr.fetchone()[0]
		if company_id == customer_addr:
			self.pool.get('invoice.tax.rate').create(cr,uid,{'amount':cgst_amt,'name':cgst_data.name,'account_tax_id':cgst_data.id,'invoice_id':res.id,'tax_rate':(product_tax * 100)/2})
			cr.commit()
			if res.billing_location_id.state_id.union_territory:
				self.pool.get('invoice.tax.rate').create(cr,uid,{'amount':sgst_amt,'name':utgst_data.name,'account_tax_id':utgst_data.id,'invoice_id':res.id,'tax_rate':(product_tax * 100)/2})
				cr.commit()
			else:
				self.pool.get('invoice.tax.rate').create(cr,uid,{'amount':sgst_amt,'name':st_data.name,'account_tax_id':st_data.id,'invoice_id':res.id,'tax_rate':(product_tax * 100)/2})
				cr.commit()
		else:
			self.pool.get('invoice.tax.rate').create(cr,uid,{'amount':igst_amt,'name':igst_data.name,'account_tax_id':igst_data.id,'invoice_id':res.id,'tax_rate':product_tax * 100})
			cr.commit()
		basic_charge = round(basic_charge)
		total_tax_amount = sgst_amt + cgst_amt + igst_amt
		total_tax_amount = round(total_tax_amount)
		grand_total_amount = round(basic_charge + total_tax_amount)
		res = self.write(cr,uid,ids,{
			'invoice_number':invoice_no,
			'invoice_date':datetime.today(),
			'cse':res.pse.id,
			'pse':res.pse.id,
			'sale_order_id':search_order[0],
			'invoice_no_generated':True,
			'basic_charge': basic_charge,
			'total_tax':total_tax_amount,
			#'product_order_grand_total': grand_total_amount,
			'pending_amount':res.product_order_grand_total,
			'grand_total_amount':res.product_order_grand_total,
			'status':'open',
			# 'tax_rate':tax_rate,
		})
		cr.commit()
		# invoiced_amt = order_obj.browse(cr,uid,search_order[0]).invoiced_amount
		# invoiced_amount = invoiced_amt + grand_total_amount
		# order_obj.write(cr, uid, search_order[0], 
		# 		{	'invoiced_amount':invoiced_amount,
		# 			'product_invoice_id': [(4, rec.id)]
		# 		})
		return True

invoice_adhoc_master()

class invoice_adhoc(osv.osv):
	_inherit = 'invoice.adhoc'
	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'invoice_type':fields.selection([('product_invoice','Product Invoice'),('service_invoice','Service Invoice')],'Invoice Type'),
		'service_invoice_id':fields.many2one('invoice.adhoc.master','Service Invoice ID',ondelete='cascade'),
		'product_invoice_id':fields.many2one('invoice.adhoc.master','Product Invoice ID',ondelete='cascade'),
		#'no_of_visits':fields.selection([('single_service','Single Service'),('2_visits','2 Visits'),('3_visits','3 Visits'),('4_visits','4 Visits'),('6_visits','6 Visits'),('12_visits','12 Visits')],'No of Visits'),
		'no_of_visits':fields.selection([('1','Single Service'),('2','2 Visits'),('3','3 Visits'),('4','4 Visits'),('6','6 Visits'),('12','12 Visits')],'No of Visits'),
		'product_code': fields.char('Product Code', size=256),
		'particulars_equipment': fields.char('Particulars of the Equipment', size=256),
		'rate_per_unit':fields.float('Rate P.U.'),
		'no_of_units':fields.integer('No of Units'),
		#'product_name': fields.many2one('product.group','Product Name'),
		# 'product_generic_name': fields.many2one('product.generic.name','Product Name'),
		'product_generic_name':fields.many2one('product.product','Product Name'),
		'product_id':fields.many2one('product.product','SKU Name'),
		'total_amount':fields.float('Total Amount'),
		'invoice_no_ref':fields.char('Invoice no ref',size=30),
		'product_uom': fields.many2one('product.uom','UOM'),
		'ordered_quantity': fields.integer('Ordered Quantity'),
		'batch': fields.many2one('res.batchnumber','Batch No'),
		'exp_date':fields.date('Expiry Date'),
		'rate': fields.float('Rate'),
		'discount':fields.float('Disc %'),
		'discounted_value':fields.float('Discounted Value'),
		'discounted_price':fields.float('Discounted Price'),
		'discounted_amount':fields.float(string='Discount Amount'),
		'tax_id':fields.many2one('account.tax','Tax Rate'),
		'tax_amount':fields.float('Tax Amount'),
		'is_track_equipment':fields.boolean('IS Track Equipment'),
		'serial_number':fields.text('Serial Number',size=300),
		'specification':fields.char('Specification',size=500),
	}
invoice_adhoc()



class temp_supplier_search(osv.osv):
	_inherit = "temp.supplier.search"

	# def add(self, cr, uid, ids, context=None):
				
	# 	for res in self.browse(cr,uid,ids):
	# 			search_supp = self.pool.get('res.partner').search(cr,uid,[('ou_id','=',res.supp_id)])
	# 			for rec in self.pool.get('res.partner').browse(cr,uid,search_supp):
	# 				rec_id = rec.id
					
	# 				models_data=self.pool.get('ir.model.data')
				
	# 				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'view_partner_supplier_form_new')
	# 				return {
	# 						'name': (""),'domain': '[]',
	# 						'type': 'ir.actions.act_window',
	# 						'view_id': False,
	# 						'view_type': 'form',
	# 						'view_mode': 'form',
	# 						'res_model': 'res.partner',
	# 						'target' : 'current',
	# 						'res_id':int(rec_id),
	# 						'views': [(form_view and form_view[1] or False, 'form'),
	# 								   (False, 'calendar'), (False, 'graph')],
	# 						'domain': '[]',
	# 						'nodestroy': True,
	# 						   }
	
	def psd_add(self, cr, uid, ids, context=None):
				
		for res in self.browse(cr,uid,ids):
				search_supp = self.pool.get('res.partner').search(cr,uid,[('ou_id','=',res.supp_id)])
				for rec in self.pool.get('res.partner').browse(cr,uid,search_supp):
					rec_id = rec.id
					
					models_data=self.pool.get('ir.model.data')
				
					form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_view_partner_supplier_form_new')
					return {
							'name': (""),'domain': '[]',
							'type': 'ir.actions.act_window',
							'view_id': False,
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'res.partner',
							'target' : 'current',
							'res_id':int(rec_id),
							'views': [(form_view and form_view[1] or False, 'form'),
									   (False, 'calendar'), (False, 'graph')],
							'domain': '[]',
							'nodestroy': True,
							   }
temp_supplier_search()

class account_support_master(osv.osv):
	_inherit="account.supplier.master"

	# def create_supplier(self, cr, uid, ids, context=None):
	# 	PSD
	# 	for res in self.browse(cr,uid,ids):
	# 		res_id = res.id
	# 		models_data=self.pool.get('ir.model.data')
	# 		form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'view_partner_supplier_form_new')
	# 		return {
	# 				'name': ("Supplier"),
	# 				'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'res.partner',
	# 				'target' : 'current',
	# 				#'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 			   }

	# def psd_create_supplier(self, cr, uid, ids, context=None):
	# 	for res in self.browse(cr,uid,ids):
	# 		res_id = res.id
	# 		models_data=self.pool.get('ir.model.data')
	# 		form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_view_partner_supplier_form_new')
	# 		return {
	# 				'name': ("Supplier"),
	# 				'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'res.partner',
	# 				'target' : 'current',
	# 				#'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 			   }
account_support_master()

class service_invoice_number(osv.osv):
	_name = 'service.invoice.number'

	_columns = {

	}
service_invoice_number()

class composite_invoice_number(osv.osv):
	_name = 'composite.invoice.number'

	_columns = {

	}

composite_invoice_number()

class product_invoice_number(osv.osv):
	_name = 'product.invoice.number'

	_columns = {

	}

product_invoice_number()


class account_tax(osv.osv):
	_inherit = 'account.tax'
	_columns = {
		'chart_account_id': fields.many2one('account.account','Chart of Account'), 
		'description': fields.selection([('vat','VAT'),('cst','CST'),('service_tax','Service Tax'),('tds','TDS'),('road_tax','Road Tax'),('lbt','LBT'),('excise','Excise'),('fbt','FBT'),('octroi','Octroi'),('others_tax','Others'),('gst','GST')], 'Tax Type', required=True),
	}
account_tax()
