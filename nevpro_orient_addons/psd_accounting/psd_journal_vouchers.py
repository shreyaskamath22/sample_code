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

class journal_voucher_search(osv.osv):
	_inherit = 'journal.voucher.search'

	def open_new(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			#self.pool.get('account.sales.receipts').create(cr,uid,{'account_select_boolean':False})
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_journal_voucher_form')
			return {    'name': ("Journal Voucher Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.journal.voucher',
					'target' : 'current',
					#'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
				}

	def psd_open_new(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			#self.pool.get('account.sales.receipts').create(cr,uid,{'account_select_boolean':False})
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_journal_voucher_form')
			context.update({'psd_accounting':True})
			return {    'name': ("Journal Voucher Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.journal.voucher',
					'target' : 'current',
					#'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
								(False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					'context': context
				}

	# def psd_search(self, cr, uid, ids, context=None):
	# 	for res in self.browse(cr,uid,ids):
	# 		today_date = datetime.now().date()
	# 		py_date = str(today_date + relativedelta(days=-1))
	# 		cr.execute("delete from search_journal_voucher_line where srch_date < %(date)s",{'date':today_date}) 
	# 		cr.execute("delete from search_journal_voucher_line where search_receipt_id =%(val)s",{'val':res.id})
			
	# 		list_id = []
	# 		main_str =Sql_Str = ''
			
	# 		try:
	# 			if res.jv_number:
	# 					Sql_Str = Sql_Str + " and jv.jv_number ilike '" + "%" + str(res.jv_number) + "%'"

	# 			if res.customer_name.id:
	# 				Sql_Str = Sql_Str + " and jv.customer_name = '" + str(res.customer_name.id) + "'"

	# 			if res.employee_name.id:
	# 				Sql_Str = Sql_Str + " and jv.employee_name = '" + str(res.employee_name.id) + "'"

	# 			if res.customer_id:
	# 				Sql_Str = Sql_Str + " and jv.customer_id_invisible ilike '" + "%" + str(res.customer_id) + "%'"

	# 			if res.from_date:
	# 				Sql_Str =Sql_Str +" and jv.date  >= '" + str(res.from_date) + "'"

	# 			if res.to_date:
	# 				Sql_Str =Sql_Str +" and jv.date <= '" + str(res.to_date) + "'"

	# 			if res.state:           #adding state filter
	# 				Sql_Str =Sql_Str +" and jv.state = '" + str(res.state) + "'"
					
	# 			if res.cfob_sync_flag:
	# 				Sql_Str =Sql_Str +" and cfob_sync_flag = " + str(res.cfob_sync_flag) + ""

	# 			Sql_Str =Sql_Str +" and jv.psd_accounting = 'f'"  
	# 			Sql_Str =Sql_Str +" and jv.state = 'done'"                       

	# 			### To concatenate CBOB customer Name and display cse 18.11.15
	# 			Main_Str ="select distinct on (jv.id) jv.jv_number,jv.id,(select concat_ws(' - ',(select name from res_partner where id=jv.customer_name), CASE WHEN (select name from res_partner where id=jv.customer_name)='CFOB'THEN (select array_to_string(array(select distinct(customer_cfob) from cofb_sales_receipts where cfob_jv_id in (select id from account_journal_voucher_line  where journal_voucher_id=jv.id) and check_cfob='t'),' / ')) ELSE (select name from res_partner where id=(select distinct(partner_id) from account_journal_voucher_line where journal_voucher_id =jv.id and partner_id is not null))END)),(select array_to_string(array(select (select concat_ws(' ',rr.name,hr.middle_name,last_name)) from hr_employee hr,resource_resource rr where hr.resource_id=rr.id and hr.id in(select distinct(cse) from invoice_receipt_history where jv_id_history in(select id from account_journal_voucher_line where journal_voucher_id=jv.id))),' / ')),jv.credit_amount,jv.debit_amount,jv.date,"+str(res.id)+" ,'''"+str(today_date)+"''' from  account_journal_voucher jv where jv.id >0 "
				
	# 			Main_Str1 = Main_Str + Sql_Str
					
	# 			insert_command = "insert into search_journal_voucher_line (jv_number,jv_id,customer_name,employee_name,credit_amount,debit_amount,date,search_receipt_id,srch_date) ("+Main_Str1+")"
	# 			cr.execute(insert_command)
				
	# 		except Exception  as exc:
	# 				cr.rollback()
	# 				if exc.__class__.__name__ == 'TransactionRollbackError':
	# 					pass
	# 				else:
	# 					raise
	# 	return True			

	def psd_search(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			today_date = datetime.now().date()
			py_date = str(today_date + relativedelta(days=-1))
			cr.execute("delete from search_journal_voucher_line where srch_date < %(date)s",{'date':today_date}) 
			cr.execute("delete from search_journal_voucher_line where search_receipt_id =%(val)s",{'val':res.id})
			
			list_id = []
			main_str =Sql_Str = ''
			
			try:
				if res.jv_number:
						Sql_Str = Sql_Str + " and jv.jv_number ilike '" + "%" + str(res.jv_number) + "%'"

				if res.customer_name.id:
					Sql_Str = Sql_Str + " and jv.customer_name = '" + str(res.customer_name.id) + "'"

				if res.employee_name.id:
					Sql_Str = Sql_Str + " and jv.employee_name = '" + str(res.employee_name.id) + "'"

				if res.customer_id:
					Sql_Str = Sql_Str + " and jv.customer_id_invisible ilike '" + "%" + str(res.customer_id) + "%'"

				if res.from_date:
					Sql_Str =Sql_Str +" and jv.date  >= '" + str(res.from_date) + "'"

				if res.to_date:
					Sql_Str =Sql_Str +" and jv.date <= '" + str(res.to_date) + "'"

				if res.state:           #adding state filter
					Sql_Str =Sql_Str +" and jv.state = '" + str(res.state) + "'"
					
				if res.cfob_sync_flag:
					Sql_Str =Sql_Str +" and cfob_sync_flag = " + str(res.cfob_sync_flag) + ""

				Sql_Str = Sql_Str +" and jv.psd_accounting = 't'"   
				Sql_Str = Sql_Str +" and jv.state = 'done'"                      
 
				### To concatenate CBOB customer Name and display cse 18.11.15
				Main_Str ="select distinct on (jv.id) jv.jv_number,jv.id,(select concat_ws(' - ',(select name from res_partner where id=jv.customer_name), CASE WHEN (select name from res_partner where id=jv.customer_name)='CFOB'THEN (select array_to_string(array(select distinct(customer_cfob) from cofb_sales_receipts where cfob_jv_id in (select id from account_journal_voucher_line  where journal_voucher_id=jv.id) and check_cfob='t'),' / ')) ELSE (select name from res_partner where id=(select distinct(partner_id) from account_journal_voucher_line where journal_voucher_id =jv.id and partner_id is not null))END)),(select array_to_string(array(select (select concat_ws(' ',rr.name,hr.middle_name,last_name)) from hr_employee hr,resource_resource rr where hr.resource_id=rr.id and hr.id in(select distinct(cse) from invoice_receipt_history where jv_id_history in(select id from account_journal_voucher_line where journal_voucher_id=jv.id))),' / ')),jv.credit_amount,jv.debit_amount,jv.date,"+str(res.id)+" ,'''"+str(today_date)+"''' from  account_journal_voucher jv where jv.id >0 "
				
				Main_Str1 = Main_Str + Sql_Str
					
				insert_command = "insert into search_journal_voucher_line (jv_number,jv_id,customer_name,employee_name,credit_amount,debit_amount,date,search_receipt_id,srch_date) ("+Main_Str1+")"
				cr.execute(insert_command)
				
			except Exception  as exc:
					cr.rollback()
					if exc.__class__.__name__ == 'TransactionRollbackError':
						pass
					else:
						raise
		return True

journal_voucher_search()


class search_journal_voucher_line(osv.osv):
	_inherit = 'search.journal.voucher.line'
				
	def show(self, cr, uid, ids, context=None):
		res_id= res_ids=''
		for res in self.browse(cr,uid,ids):
			#res_ids = self.pool.get('account.journal.voucher').search(cr,uid,[('jv_number','=',res.jv_number)])
			res_ids = self.pool.get('account.journal.voucher').search(cr,uid,[('id','=',res.jv_id)])
			if res_ids:
				res_id=res_ids[0]
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_journal_voucher_form')
			return {
					'name': ("Journal Voucher Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.journal.voucher',
					'target' : 'current',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
				}

	def psd_show(self, cr, uid, ids, context=None):
		res_id= res_ids=''
		for res in self.browse(cr,uid,ids):
			#res_ids = self.pool.get('account.journal.voucher').search(cr,uid,[('jv_number','=',res.jv_number)])
			res_ids = self.pool.get('account.journal.voucher').search(cr,uid,[('id','=',res.jv_id)])
			if res_ids:
				res_id=res_ids[0]
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_journal_voucher_form')
			return {
					'name': ("Journal Voucher Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.journal.voucher',
					'target' : 'current',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True
			}

search_journal_voucher_line ()

class account_journal_voucher(osv.osv):
	_inherit='account.journal.voucher'

	_columns = {
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'jv_type':fields.selection([('standard','Standard'),('cfob','CFOB'),('cbob','CBOB')],'JV Type'),
		'status':fields.selection([('done','Done'),('cancelled','Cancelled')],'Status'),
		'psd_accounting':fields.boolean('PSD Accounting'),
		'customer_name_text': fields.char('Customer Name',size=100)
	}

	_defaults = {
    'jv_type': 'standard', 
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(account_journal_voucher, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	def account_type(self, cr, uid, ids, account_id, context=None):
		v = {}
		if account_id:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in  ( 'cash','iob_one','against_ref'):
						v['type'] = 'debit'
					elif acc.account_selection in ('others','iob_two'):
						v['type'] = 'credit'
					else:
						v['type'] = ''
		return {'value':v}	
	
	def psd_add_info(self, cr, uid, ids, context=None):
		journal_line_obj = self.pool.get('account.journal.voucher.line')
		for res in self.browse(cr,uid,ids):
			account_id = res.account_id.id
			account_name = res.account_id.name
			acc_selection = res.account_id.account_selection
			customer_name=res.customer_name.id
			customer_name_char = res.customer_name.name
			types = res.type
			auto_credit_cal = auto_debit_cal = auto_credit_total = auto_debit_total = itds_total = temp=0.0
			acc_list=['against_ref','advance','sundry_deposit','security_deposit','others']
			account_id1=res.account_id
			if res.account_id.account_selection in acc_list :
				for i in res.journal_voucher_one2many:
					if account_id1.id==i.account_id.id:
						raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

			if not account_id:
				raise osv.except_osv(('Alert'),('Please select Account Name.'))

			# if res.jv_type == 'cfob' or res.jv_type == 'cbob':
			# 	if not customer_name_char:
			# 		raise osv.except_osv(('Alert'),('Enter a valid customer name.'))

			if customer_name_char == 'CFOB' and types == 'credit' and res.account_id.account_selection == 'against_ref':
				raise osv.except_osv(('Alert'),('Please Select Type Debit.'))
				
			if customer_name_char == 'CBOB' and types == 'debit' and res.account_id.account_selection == 'against_ref':
				raise osv.except_osv(('Alert'),('Please Select Type Credit.'))
			
			if not types:
				raise osv.except_osv(('Alert'),('Please select Type.'))
			
			if acc_selection=='sundry_deposit':
				srch_sun= self.pool.get('sundry.deposit').search(cr,uid,[
					('sundry_check_process','=',False),
					('sundry_jv','=',True)])
				for i in self.pool.get('sundry.deposit').browse(cr,uid,srch_sun):
					self.pool.get('sundry.deposit').write(cr,uid,i.id,{'sundry_jv':False})
			
			if account_id:
				if acc_selection == 'against_ref':
					if res.customer_name.name == 'CFOB':##### for check box functionality 
						cr.execute("update cofb_sales_receipts set check_cfob = False where check_cfob_jv_process = False and check_cfob = True ")
					elif res.customer_name.name == 'CBOB':
						cr.execute('update invoice_adhoc_master set cbob_chk_invoice = False where cbob_chk_invoice_process = False and cbob_chk_invoice = True and invoice_number is not Null')
					else:
						cr.execute('update invoice_adhoc_master set check_journal_invoice = False where check_process_journal_invoice = False and check_journal_invoice = True and invoice_number is not Null')
								
				if acc_selection == 'itds_receipt':
					if res.account_id.itds_rate:
						itds_rate = res.account_id.itds_rate
						itds_rate_per = itds_rate * 0.01
						for line in res.journal_voucher_one2many:
							if line.account_id.account_selection == 'against_ref':        
								grand_total = line.credit_amount
								itds_total = grand_total * itds_rate_per
					else:
						raise osv.except_osv(('Alert'),('Please give Itds Rate'))
				
				if acc_selection == 'others':
					# if res.customer_name.name == 'CFOB':
							branch_name = []
							i = 0
							flag_branch = False
							acc_name = ''
							for i in  res.journal_voucher_one2many:
									if i.account_id.account_selection =='against_ref':
											search_main = self.pool.get('account.journal.voucher.line').search(cr,uid,[('journal_voucher_id','=',res.id)])
											for val in self.pool.get('account.journal.voucher.line').browse(cr,uid,search_main):
												search_branch = self.pool.get('cofb.sales.receipts').search(cr,uid,[('cfob_jv_id','=',val.id)])
												for branch in self.pool.get('cofb.sales.receipts').browse(cr,uid,search_branch):
													if branch.check_cfob == True:
														branch_name.append(branch.branch_name.name)
														acc_name = account_name
											if acc_name not in branch_name:
												raise osv.except_osv(('Alert'),('Select proper Branch'))
							if res.journal_voucher_one2many:
								deb = res.journal_voucher_one2many[0].debit_amount
								if deb != 0:
									auto_credit_cal = deb
										
			# if  res.account_id.account_selection == 'iob_two' or res.account_id.account_selection == 'iob_one' or res.account_id.account_selection == 'cash':
			if  res.account_id.account_selection in ('iob_two','iob_one','cash'):
					raise osv.except_osv(('Alert'),('Please select proper account name.'))
								
			if itds_total :
				temp = itds_total 
			elif auto_debit_total :
				temp = auto_debit_total
			else:
				temp =  0.0
				
			self.pool.get('account.journal.voucher.line').create(cr,uid,{
					'journal_voucher_id':res.id,
					'account_id':account_id,
					'customer_name':customer_name,
					'debit_amount':temp,
					'credit_amount':auto_credit_cal,
					'type':types,
				})
											
			self.write(cr,uid,res.id,{'account_id':None,'type':None})
		return True

	def psd_process(self,cr,uid,ids, context=None ):# Journal Voucher Process 28JAN
		post=[]
		grand_total = grand_total_against = pending_amt = cbob_total = dr_total = cr_total = 0.0
		ref_amount_security = pending_amt = pay_amount = 0.0
		cfob_id = date = sundry_jv_id = security_jv_id = cbob_id = invoice_id_journal = invoice_no = ''
		invoice_num = invoice_date_concate = ''
		count = 0
		today_date = datetime.now().date()
		flag = py_date = sec_flag = sun_flag = cbob_flag = False
		
		invoice_adhoc_master = self.pool.get('invoice.adhoc.master')
		invoice_receipt_history = self.pool.get('invoice.receipt.history')
		payment_contract_history = self.pool.get('payment.contract.history')
		sales_receipts = self.pool.get('account.sales.receipts')
		sales_receipts_line = self.pool.get('account.sales.receipts.line')
		advance_receipts = self.pool.get('advance.sales.receipts')
		
		models_data=self.pool.get('ir.model.data')
		acc_list=['against_ref','advance','sundry_deposit','security_deposit','others']
		for res in self.browse(cr,uid,ids):
			if res.date:
				py_date = str(today_date + relativedelta(days=-5))
				if res.date < str(py_date) or res.date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Date 5 days earlier from current date.'))
				date=res.date
			else:
				date=datetime.now().date()
			if res.journal_voucher_one2many == []:
				raise osv.except_osv(('Alert'),('No line to proceed.'))
			
			for line in res.journal_voucher_one2many:
				if line.type == 'credit':
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				elif line.type == 'debit':
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				else:
					raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(line.account_id.name))))

				cr_total += line.credit_amount
				dr_total += line.debit_amount
                        
                                if line.account_id.account_selection in acc_list:
                                        if line.account_id.id in post :
                                                raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
                                        else:
                                                account_id = line.account_id.id
				                temp = tuple([account_id])
				                post.append(temp)
				
			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
		
		for res in self.browse(cr,uid,ids):
			for line in res.journal_voucher_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name
				customer_name = res.customer_name.name
				
				if acc_selection == 'against_ref':
					if line.journal_voucher_id.jv_type == 'cfob': ##### CFOB Entry 
						cfob_amount = 0.0
						branch_name = []
						i = 0
						j = 1
						for cfob_line in line.cfob_jv_one2many:
							cfob_id = cfob_line.cfob_jv_id
							if cfob_line.check_cfob == True :
								branch_name.append(cfob_line.branch_name.name)
								cfob_amount += cfob_line.ref_amount
								self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_line.id,{'check_cfob_jv_process':True})

						if not cfob_id:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed')%(account_name))
						elif cfob_id:
							if line.debit_amount:
								if round(cfob_amount,2) != round(line.debit_amount,2):
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if line.credit_amount:
								if round(cfob_amount,2) != round(line.credit_amount,2):
									raise osv.except_osv(('Alert'),('Credit amount should be equal'))
	
					elif line.journal_voucher_id.jv_type == 'cbob':  # CBOB 
						credit_amount = line.credit_amount

						if line.invoice_cbob_one2many == []:
							raise osv.except_osv(('Alert'),('Please provide invoice information.'))
						# if line.payment_method == False:
						# 	raise osv.except_osv(('Alert'),('Select Payment Method Before Selecting Invoice'))
						for cbob_line in line.invoice_cbob_one2many:
							if cbob_line.cbob_chk_invoice == True:
								cbob_flag = True
								invoice_no = cbob_line.invoice_number
								total_amount = cbob_line.grand_total_amount
								cbob_total += total_amount
								invoice_no = cbob_line.invoice_number
								partial_payment = cbob_line.partial_payment_amount
 
							pending_amount = cbob_line.pending_amount - cbob_line.partial_payment_amount
							if not cbob_line.partial_payment_amount:
									raise osv.except_osv(('Alert'),('partial amount cannot be zero.'))

							if cbob_line.cbob_chk_invoice == True:
								invoice_receipt_history.create(cr,uid,{
									'invoice_receipt_history_id':cbob_line.id,
									'invoice_number':cbob_line.invoice_number,
									'invoice_pending_amount':pending_amount,
									'invoice_paid_amount':cbob_line.partial_payment_amount,
									'invoice_paid_date':res.date if res.date else datetime.now().date(),
									'jv_id_history':line.id,
									'invoice_date':cbob_line.invoice_date,
									'service_classification':cbob_line.service_classification,
									'tax_rate':cbob_line.tax_rate,
									'cse':cbob_line.cse.id,
									'check_invoice':True})


							if pending_amount == 0:
								pending_status = 'paid'
								status = 'paid'
								partial_pending_amount = 0 
							else:
								pending_status = 'pending',
								status = cbob_line.status,
								partial_payment_amount = 0

							invoice_adhoc_master.write(cr,uid,cbob_line.id,{
								'pending_amount': pending_amount,
								'pending_status':pending_status,
								'status':status,
								'partial_payment_amount':partial_pending_amount})
								
								
						if cbob_flag == False:
							raise osv.except_osv(('Alert'),('Please select the invoice.'))

						invoice_history_srch = payment_contract_history.search(cr,uid,[('invoice_number','=',invoice_no)])
						if invoice_history_srch:
							for invoice_history in payment_contract_history.browse(cr,uid,invoice_history_srch):
								payment_contract_history.write(cr,uid,invoice_history.id,{'payment_status':'paid'})
							
					else: 
						invoice_no = ''
						if line.type == 'credit':
							for invoice_line in line.invoice_one2many:
								invoice_id_journal = invoice_line.invoice_id_journal
								invoice_num = [str(invoice_line.invoice_number),invoice_num]
								invoice_num = ' / '.join(filter(bool,invoice_num))
								invoice_date_concate = [invoice_line.invoice_date,invoice_date_concate]
								invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))

								pending_amount = invoice_line.pending_amount - invoice_line.partial_payment_amount 

								if invoice_line.check_journal_invoice == True:
									flag = True
									count += 1
								if pending_amount == 0:
									search1 = payment_contract_history.search(cr,uid,[('invoice_number','=',invoice_no)])
									for st in payment_contract_history.browse(cr,uid,search1): 
										payment_contract_history.write(cr,uid,st.id,{'payment_status':'paid'})
									self.sync_invoice_update_state_journal(cr,uid,ids,context=context)
									grand_total += invoice_line.grand_total_amount
									check_process_journal_invoice = True
									status = 'paid'
									pending_amount = 0
									pending_status = 'paid'
								else:
									check_process_journal_invoice = False
									status = invoice_line.status,
									pending_amount = pending_amount,
									pending_status = 'pending',

								invoice_adhoc_master.write(cr,uid,invoice_line.id,{
									'check_process_journal_invoice': check_process_journal_invoice,
									'status': status,
									'pending_amount': pending_amount,
									'pending_status': pending_status,
									'invoice_paid_date': datetime.now().date()
								})
								invoice_receipt_history.create(cr,uid,{
									'invoice_receipt_history_id':invoice_line.id,
									'invoice_number':invoice_line.invoice_number,
									'invoice_pending_amount':pending_amount,
									'invoice_paid_amount':invoice_line.partial_payment_amount,
									'invoice_paid_date':res.date if res.date else datetime.now().date(),
									'jv_invoice_id_history':line.id,
									'invoice_date':invoice_line.invoice_date,
									'service_classification':invoice_line.service_classification,
									'tax_rate':invoice_line.tax_rate,
									'cse':invoice_line.cse.id,
									'check_invoice':True})######## For Payment history

						if line.type == 'debit':
							for invoice_line in line.invoice_one2many:
								invoice_id_journal = invoice_line.invoice_id_journal
								invoice_num = [str(invoice_line.invoice_number),invoice_num]
								invoice_num = ' / '.join(filter(bool,invoice_num))
								invoice_date_concate = [invoice_line.invoice_date,invoice_date_concate]
								invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))

								pending_amount = invoice_line.pending_amount - invoice_line.partial_payment_amount 

								if invoice_line.check_journal_invoice == True:
									flag = True
									count += 1
								if pending_amount == 0:
									search1 = payment_contract_history.search(cr,uid,[('invoice_number','=',invoice_no)])
									for st in payment_contract_history.browse(cr,uid,search1): 
										payment_contract_history.write(cr,uid,st.id,{'payment_status':'paid'})
									self.sync_invoice_update_state_journal(cr,uid,ids,context=context)
									grand_total += invoice_line.grand_total_amount
									check_process_journal_invoice = True
									status = 'paid'
									pending_amount = 0
									pending_status = 'paid'
								else:
									check_process_journal_invoice = False
								 	status = invoice_line.status,
									pending_amount = pending_amount,
									pending_status = 'pending',

								invoice_adhoc_master.write(cr,uid,invoice_line.id,{
									'check_process_journal_invoice': check_process_journal_invoice,
									'status': status,
									'pending_amount': pending_amount,
									'pending_status': pending_status,
									'invoice_paid_date': datetime.now().date()
								})
								invoice_receipt_history.create(cr,uid,{
									'invoice_receipt_history_id':invoice_line.id,
									'invoice_number':invoice_line.invoice_number,
									'invoice_pending_amount':pending_amount,
									'invoice_paid_amount':invoice_line.partial_payment_amount,
									'invoice_paid_date':res.date if res.date else datetime.now().date(),
									'jv_invoice_id_history':line.id,
									'invoice_date':invoice_line.invoice_date,
									'service_classification':invoice_line.service_classification,
									'tax_rate':invoice_line.tax_rate,
									'cse':invoice_line.cse.id,
									'check_invoice':True})######## For Payment history

						if flag == False:
							raise osv.except_osv(('Alert'),('No invoice selected.'))

						if not invoice_id_journal:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.')%(account_name))
						elif invoice_id_journal:
							if line.credit_amount:
								if grand_total != line.credit_amount:
									#raise osv.except_osv(('Alert'),('Credit amount should be equal'))
									pass

#>>>>>>>>>>>> sagar 11sept CBOB Advance	 # advance in CBOB is stored directly in account_sales_receipt

				if acc_selection == 'advance' and line.journal_voucher_id.jv_type == 'cbob':
					ref_amount_adv =0.0
					advance_id = ''
					for adv_cbob_line in line.cbob_advance_one2many:
						advance_id = adv_cbob_line.cbob_advance_id.id
						ref_amount_adv += adv_cbob_line.ref_amount
						if not adv_cbob_line.ref_no:
							raise osv.except_osv(('Alert'),('Please provide reference number.'))

						if not adv_cbob_line.ref_date:
							raise osv.except_osv(('Alert'),('Please provide reference date.'))
					
					if not advance_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					elif advance_id:
						if line.debit_amount:
							if ref_amount_adv != line.debit_amount:
								raise osv.except_osv(('Alert'),('Debit amount should be equal'))
						if line.credit_amount:
							if ref_amount_adv != line.credit_amount:
								raise osv.except_osv(('Alert'),('credit amount should be equal'))
	                                for ln in line.cbob_advance_one2many:
	                                         self.pool.get('advance.sales.receipts').write(cr,uid,ln.id,{
                                                                                'receipt_no':res.jv_number,
							                        'receipt_date':res.date,})
#<<<<<<<<<<<< #sagar    
				if acc_selection == 'advance' and line.journal_voucher_id.jv_type != 'cbob':
					for advance_refund in line.journal_advance_one2many:
						if advance_refund.check_advance_against_ref == True:
						        if advance_refund.advance_pending < advance_refund.partial_amt :
						                raise osv.except_osv(('Alert'),('enter proper partial amount'))
						        amt=advance_refund.advance_pending-advance_refund.partial_amt if advance_refund.partial_amt else 0
						        
							advance_receipts.write(cr,uid,advance_refund.id,{
								'check_advance_against_ref_process':True if amt==0.0 else False ,
								'check_advance_against_ref':True if amt==0.0 else False,
								'advance_pending':amt if amt  else '0.0'})
							receipt_id=''
							############################
							line_srch=sales_receipts_line.search(cr,uid,[('id','=',advance_refund.advance_id.id)])
							if line_srch:
							        for i in sales_receipts_line.browse(cr,uid,line_srch):
							                main_srch=sales_receipts.search(cr,uid,[('id','=',i.receipt_id.id)])
							                for j in sales_receipts.browse(cr,uid,main_srch):
							                        receipt_id=j.id
							                        sales_receipts.write(cr,uid,j.id,{'advance_pending':amt})
							###########################
							self.pool.get('advance.receipt.history').create(cr,uid,{
								                        'jv_receipt_id':line.id,
								                        'advance_receipt_no':advance_refund.receipt_no,
								                        'advance_date':advance_refund.receipt_date,
								                        'cust_name':advance_refund.partner_id.id,
								                        'advance_refund_amount':advance_refund.partial_amt if advance_refund.partial_amt else advance_refund.advance_pending,
								                        'advance_pending_amount': amt if amt else 0.0,
								                        'advance_receipt_date':res.date if res.date else datetime.now().date(),
                                                                        'service_classifiaction':advance_refund.service_classification,
								                        'history_advance_id':advance_refund.id,
								                        'receipt_id':receipt_id if receipt_id else False,
								                })  
				for rec_line in res.journal_voucher_one2many:						
				        if rec_line.account_id.account_selection == 'security_deposit' and rec_line.type=='debit':
				                line_id1=rec_line.id
				                amt=rec_line.debit_amount
				                sec_flag = True
					#####EMD summ report
				if acc_selection == 'sundry_deposit':
				        payment_no=cse=customer_id=customer_name=''
					for sun_line in line.sundry_deposit_jv_one2many:
						if sun_line.sundry_jv:
							sundry_jv_id = sun_line.sundry_jv_id.id
							pay_amount += sun_line.payment_amount
							payment_no += ' / '+sun_line.payment_no
							cse = sun_line.cse
							customer_id=sun_line.customer_name.id
							customer_name = sun_line.customer_name.name
							self.pool.get('sundry.deposit').write(cr,uid,sun_line.id,{'sundry_check_process':True})
					if sundry_jv_id:
						if line.debit_amount:
							if  pay_amount != line.debit_amount:
								raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
						if line.credit_amount:
							if  pay_amount != line.credit_amount:
								raise osv.except_osv(('Alert'),('credit amount should be equal.'))

					if line.type == 'credit':
						sun_flag = True   #####EMD summ report
						
                                        if sec_flag:
                                                self.pool.get('security.deposit').create(cr,uid,{
						                                'security_jv_id':line_id1,
							                        'cse':cse if cse else False,
							                        'ref_no':payment_no,
							                        'ref_date':res.date,
							                        'ref_amount':amt,
							                        'pending_amount':amt,
								                'security_check_against':True,
								                'customer_name':customer_id if customer_id else res.customer_name.id,
								                #'acc_status_new':line.acc_status,
								                'customer_name_char':customer_name,
								                })


				if sec_flag == True and sun_flag == True:
					for line_id in res.journal_voucher_one2many:
						self.pool.get('account.journal.voucher.line').write(cr,uid,line_id.id,{'chk_emd_report':True})

		for rec in self.browse(cr,uid,ids):
			jv_no = ''
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_journal_voucher_form')
			
			#seq_id = self.pool.get('ir.sequence').get(cr, uid, 'account.journal.voucher')
			
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = ''
			end_year = ''
			pcof_key = ''
			credit_note_id = ''	
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','account.journal.voucher')])
			if search:
				seq_start=self.pool.get('ir.sequence').browse(cr,uid,search[0]).number_next

			year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
			month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
			
			if month > 3:
				start_year = year
				end_year = year+1
				year1 = int(year1)+1
			else:
				start_year = year-1
				end_year = year
				year1 = str(year1)

			financial_start_date = str(start_year)+'-04-01'

			financial_end_date = str(end_year)+'-03-31'
			company_id=self._get_company(cr,uid,context=None)
			if company_id:
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					if comp_id.journal_voucher_id:
						journal_voucher_id = comp_id.journal_voucher_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
			
			if res.date:
				py_date = str(today_date + relativedelta(days=-5))
				if res.date < str(py_date) or res.date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Date 5 days earlier from current date.'))
				date=res.date
			else:
				date=datetime.now().date()
			year = today_date.strftime('%y')

			count=0	
			if pcof_key and journal_voucher_id:
				cr.execute("select cast(count(id) as integer) from account_journal_voucher where jv_number is not null   and  date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				jv_no = pcof_key + journal_voucher_id +  str(year1) +str(seq).zfill(6)

			cus_new=''
			if rec.jv_type == 'cfob':
				for j  in rec.journal_voucher_one2many:
					if j.account_id.account_selection=='against_ref':
						for k in j.cfob_jv_one2many:
							if k.check_cfob == True:
								cus_new= ', '.join(filter(bool,['CFOB - ' + k.customer_cfob]))

			elif rec.jv_type == 'cbob':
				for j  in rec.journal_voucher_one2many:
					if j.account_id.account_selection=='against_ref':
						for k in j.invoice_cbob_one2many:
							if k.cbob_chk_invoice == True:
								cus_new='CBOB - ' + j.partner_id.name  
								#cus_new=', '.join(filter(bool,[j.partner_id.name]))

			else:
				cus_new= rec.customer_name.name if rec.customer_name else ''

			self.write(cr,uid,ids,{
				'jv_number':jv_no,
				'date': date,
				'voucher_type':'Journal(JV)',
				'cus_new':cus_new})

			search_date = self.pool.get('account.period').search(cr,uid,[
				                                                        ('date_start','<=',date),
				                                                        ('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id
				#date = rec.date
			search_date = self.pool.get('account.period').search(cr,uid,[
				                                                        ('date_start','<=',date),
				                                                        ('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id

			srch_jour_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
			for jour_acc in self.pool.get('account.journal').browse(cr,uid,srch_jour_acc):
				journal_id = jour_acc.id
			move = self.pool.get('account.move').create(cr,uid,{
						'journal_id':journal_id,####hardcoded not confirm by pcil
						'state':'posted',
						'date':date,
						'name':jv_no,
						'narration':rec.narration if rec.narration else '',
						'journal_boolean':True,
						'voucher_type':'Journal(JV)',
					},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.journal_voucher_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
							'move_id':line1.id,
							'account_id':ln.account_id.id,
							'debit':ln.debit_amount,
							'name':rec.customer_name.name if rec.customer_name.name else '',
							'journal_id':journal_id,
							'period_id':period_id,
							'date':date,
							'ref':jv_no},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
							'account_id':ln.account_id.id,
							'credit':ln.credit_amount,
							'name':rec.customer_name.name if rec.customer_name.name else '',
							'journal_id':journal_id,
							'period_id':period_id,
							'date':date,
							'ref':jv_no},context=context)

		date=''  
		curr_id = False                                              
		for journal_his in self.browse(cr,uid,ids):#rohit 12 may
			#receipt_no=payment_his.value_id#payment_his.receipt_no
			
			cust_name=journal_his.customer_name.name
			if journal_his.date:
				date=journal_his.date
			else:
				date=datetime.now().date()
			for payment_line in journal_his.journal_voucher_one2many:
				amount=payment_line.debit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('journal.vouchar.history').create(cr,uid,{
					'journal_vouchar_his_many2one':curr_id,
					'journal_vouchar_number':jv_no,
					'journal_vouchar_date':date,
					'journal_vouchar_amount':amount})


		'''for record_line in self.browse(cr,uid,ids): # Sagar 11 sept
			customer_id=''
			for cbob_line1 in record_line.journal_voucher_one2many:
				if cbob_line1.journal_voucher_id.customer_name:
					customer_id=cbob_line1.journal_voucher_id.customer_name

			for cbob_line in record_line.journal_voucher_one2many:
				acc_selection = cbob_line.account_id.account_selection
				if acc_selection == 'advance':
					for rec_line in cbob_line.cbob_advance_one2many:
						aa=sales_receipts.create(cr,uid,{
							'receipt_no':rec_line.ref_no,
							'receipt_date':rec_line.ref_date,
							'credit_amount':rec_line.ref_amount,
							'advance_pending':rec_line.ref_amount,
							'customer_name':customer_id.id,
							'new_cus_name':customer_id.name,
							#'state':'done',
							'import_flag':True,
							})
						self.pool.get('advance.sales.receipts').write(cr,uid,rec_line.id,{'advance_id':aa})'''

###################### for itds create 30 oct 2015 Priya ##############
		for res in self.browse(cr,uid,ids):
			invoice_no = inv_date = cfob_cse = cse_name_last_cbob=cust_name_cbob=''
			gross_amt = 0.0
			flag=False

			for line in res.journal_voucher_one2many:
				acc_selection = line.account_id.account_selection
				cust_name_cbob= line.partner_id.name 
				
				if acc_selection == 'itds_receipt':
					itds_debit=line.debit_amount
					flag= True
			for line in res.journal_voucher_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name
				if res.date:
					date=res.date
				else:
					date=datetime.now().date()

				if acc_selection == 'against_ref':
					if line.invoice_cbob_one2many:
						for invoice_line in line.invoice_cbob_one2many:
							if invoice_line.cbob_chk_invoice == True :
								invoice_no=invoice_line.invoice_number
								inv_date=invoice_line.invoice_date	
								gross_amt=invoice_line.grand_total_amount
								idts_pending=invoice_line.pending_amount

								main_str = "select name from resource_resource where id = '" + "" + str(invoice_line.cse.resource_id.id) + "'"
								cr.execute(main_str)
								first_name = cr.fetchone()
								if first_name:
									cse_name_last_cbob = str(first_name[0]) +' '+str(invoice_line.cse.last_name)
					if flag == True:
						self.pool.get('itds.adjustment').create(cr,uid,{'receipt_no':res.jv_number,
										'receipt_date':date,
										'gross_amt':gross_amt,
										'pending_amt':idts_pending,
										'itds_amt':itds_debit,
										'invoice_no':invoice_no,
										'invoice_date':inv_date,
										'customer_name':res.customer_name.id,
										'customer_name_char':cust_name_cbob,
										'cse':cse_name_last_cbob,
										})
						flag= False
			
			self.write(cr,uid,rec.id,{'state':'done'})
			
	######################################################## itds Create#######################################
			for res in self.browse(cr,uid,ids):
				if res.state == 'done':
					for ln in res.journal_voucher_one2many:
						self.pool.get('account.journal.voucher.line').write(cr,uid,ln.id,{'state1':'done'}) 

			self.delete_draft_records_jv(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
			self.sync_cbob_invoices(cr,uid,ids,context=context)
			self.sync_account_journal(cr,uid,ids)

		for rec in self.browse(cr,uid,ids):
			emp_name=''
			for line in rec.journal_voucher_one2many:
				if line.account_id.account_selection == 'primary_cost_cse':
					for line1 in line.journal_primary_cost_one2many:
						emp_name=line1.emp_name.id
					self.write(cr,uid,rec.id,{'employee_name':emp_name})
			for line1 in rec.journal_voucher_one2many:
				if line1.account_id.account_selection == 'primary_cost_cse_office':
					for line2 in line.journal_primary_cost_one2many:
						emp_name=line2.emp_name.id
					self.write(cr,uid,rec.id,{'employee_name':emp_name})

		return  {
			'name':'Journal Voucher',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'account.journal.voucher',
			'res_id':rec.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
		}

account_journal_voucher()    


class account_journal_voucher_line(osv.osv):
	_inherit = 'account.journal.voucher.line'

	_columns = {
		'is_transfered': fields.boolean('Is Transfered')
	}

	# domain added
	def show_details_cfob_psd(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			search = self.pool.get('account.journal.voucher').search(cr,uid,[('id','=',res.journal_voucher_id.id)])
			for rec in self.pool.get('account.journal.voucher').browse(cr,uid,search):
				srch_cfob = self.pool.get('cofb.sales.receipts').search(cr,uid,[
						('id','>',0),
						('check_cfob_sales_process','=',True),
						('check_cfob_jv_process','=',False),
					    ('customer_cfob','=',res.journal_voucher_id.customer_name.name)
						])
				for val in self.pool.get('cofb.sales.receipts').browse(cr,uid,srch_cfob):
					self.pool.get('cofb.sales.receipts').write(cr, uid,val.id,{'cfob_jv_id':res.id})
		return True


	def psd_add_others(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			account_id = res.account_id
			type_acc = res.type
			acc_selection = res.account_id.account_selection
			customer_name = res.customer_name.name
			acc_selection_list = ['against_ref','security_deposit','sundry_deposit',
								  'primary_cost_cse','primary_cost_office','primary_cost_phone',
								  'primary_cost_vehicle','primary_cost_service','primary_cost_cse_office','advance']
			view_name = name_wizard = ''

			if acc_selection in acc_selection_list :
				if acc_selection == 'against_ref' and res.journal_voucher_id.jv_type not in ('cbob','cfob') and res.type=='credit' :
					context.update({'type':'debit'})
					self.show_details(cr,uid,ids,context=context)
					view_name = 'psd_invoice_details_form'
					name_wizard = 'Invoice Details'
					
				if acc_selection == 'against_ref' and res.journal_voucher_id.jv_type == 'cbob' and res.type=='debit':
					# sundry debtors 15% 14%
					view_name = 'psd_cbob_invoice_details_form'
					name_wizard = 'Outstanding Invoice Details'
					
				if acc_selection == 'security_deposit' and res.state1 != 'draft' and res.type=='debit':
					view_name =  'psd_account_security_deposit_jv_id'
					name_wizard = 'Security Deposit'
						 
				if acc_selection == 'sundry_deposit' and res.type=='credit':
					# sundry deposits
					self.show_details_sundry(cr,uid,ids,context=context)
					view_name = 'psd_account_sundry_deposit_jv_id'
					name_wizard = 'Sundry Deposit'
					 
				if acc_selection == 'against_ref' and res.journal_voucher_id.jv_type == 'cfob' and res.type=='debit':
					# sundry debtors 15% 14%
					self.show_details_cfob_psd(cr,uid,ids,context=context)
					view_name = 'psd_account_cfob_jv_id'
					name_wizard = 'CFOB Details'
	
				if acc_selection == 'primary_cost_cse':
					view_name = 'psd_account_journal_primary_cost_form'
					name_wizard = ("Add Primary Cost Category")
	
				if acc_selection == 'primary_cost_office':
					view_name = 'psd_account_journal_primary_cost_office_form'
					name_wizard = ("Add Primary Cost Category")
				
				if acc_selection == 'primary_cost_phone':
					view_name = 'psd_account_journal_primary_cost_phone_form'
					name_wizard = ("Add Primary Cost Category")
				
				if acc_selection == 'primary_cost_vehicle':
					view_name = 'psd_account_journal_primary_cost_vehicle_form'
					name_wizard = ("Add Primary Cost Category")
	
				if acc_selection == 'primary_cost_service':##
					view_name = 'psd_account_primary_cost_journal_service_form'
					name_wizard = ("Add Primary Cost Category")
	
				if acc_selection == 'primary_cost_cse_office':#
					view_name = 'psd_account_journal_primary_cost_cse_office_form'
					name_wizard = ("Add Primary Cost Category")
	
				if acc_selection == 'advance' and type_acc == 'credit': #sagar advance CBOB 11 sept
					# advance receipts
					view_name = 'psd_account_journal_advance_cbob_form'
					name_wizard = ("Add Advance Details")
	
				if acc_selection == 'advance' and type_acc == 'debit':   # HHH 31oct15
					# advance receipts
					self.show_details_jv(cr,uid,ids,context=context)
					view_name = 'psd_against_advance_form_1'
					name_wizard = ("Advance Payment Details")
					
				if view_name:
					models_data=self.pool.get('ir.model.data')
					form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name)
					self.write(cr, uid, ids[0], {'partner_id':res.journal_voucher_id.customer_name.id}, context=context)
					return {
						'name': name_wizard,'domain': '[]',
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'account.journal.voucher.line',
						'target' : 'new',
						'res_id':int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								   (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True,
					}
		return True	


	def cbob_invoice_save_psd(self, cr, uid, ids, context=None):
		flag = False
		total = 0.0
		for res in self.browse(cr,uid,ids):
			# if res.payment_method == False:
			# 	raise osv.except_osv(('Alert'),('Select Payment Method'))
			for line in res.invoice_cbob_one2many:
				if  line.cbob_chk_invoice == True:
					# if line.tax_rate not in res.account_id.name:
					# 		print"line.tax_rate",line.tax_rate
					# 		print"res.account_id.name",res.account_id.name
					# 		raise osv.except_osv(('Alert'),('select proper tax_rate invoices')) 
					flag = True
					# if res.payment_method == 'partial_payment':
					if line.partial_payment_amount == 0.0:
						raise osv.except_osv(('Alert'),('Payment amount cannot be zero'))
					if line.partial_payment_amount > line.pending_amount:
						raise osv.except_osv(('Alert'),('Payment amount cannot be greater than invoice pending amount'))
					total += line.partial_payment_amount
								
					# if res.payment_method == 'full_payment': 
					# 	total += line.pending_amount
						
			if res.type== 'debit':
				self.write(cr,uid,res.id,{'debit_amount':total})
			else:
				self.write(cr,uid,res.id,{'credit_amount':total})

		if flag == False:
			raise osv.except_osv(('Alert'),('Please select the invoice.'))

		return {'type': 'ir.actions.act_window_close'}	


	def save_cfob_psd(self, cr,uid,ids,context=None):
		type1 = ""
		total = 0.0
		journal_voucher_obj = self.pool.get('account.journal.voucher')
		cofb_receipts_obj = self.pool.get('cofb.sales.receipts')
		for rec in self.browse(cr,uid,ids):
			type1 = rec.type
			if rec.cfob_jv_one2many == []:
					raise osv.except_osv(('Alert'),('No line to process.'))

			for line in rec.cfob_jv_one2many:
				if line.check_cfob == True:
					total += line.ref_amount

			if type1== 'debit':
				self.write(cr,uid,rec.id,{'debit_amount':total})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':total})

			cofb_receipt_id = cofb_receipts_obj.search(cr, uid, [('check_cfob','=',True),('cfob_jv_id','=',rec.id)], context=context)
			if cofb_receipt_id:
				customer_cfob = cofb_receipts_obj.browse(cr, uid, cofb_receipt_id[0]).customer_cfob
				journal_voucher_obj.write(cr, uid, rec.journal_voucher_id.id, {'customer_name_text':customer_cfob}, context=context)

		return {'type': 'ir.actions.act_window_close'}	

account_journal_voucher_line()