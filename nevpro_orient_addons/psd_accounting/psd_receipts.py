from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
from dateutil.relativedelta import relativedelta
import datetime as dt
import datetime 
import calendar
import re
from datetime import date,datetime, timedelta
from base.res import res_company as COMPANY
from base.res import res_partner
from collections import Counter
import xmlrpclib
import math
import os
from tools.translate import _


class sales_receipts_search(osv.osv):
	_inherit = 'sales.receipts.search'

	_columns={
		'paymode':fields.selection([('standard','Standard'),('cfob','CFOB'),('demand_draft','Demand Draft'),('neft','NEFT')],'Paymode'),
		'cheque_no':fields.integer('Cheque No'),
		'cfob_customer_name': fields.char('CFOB Customer Name', size=100),
		'cfob_customer_id': fields.char('CFOB Customer ID', size=100),
		'customer_name_text': fields.char('Customer Name', size=100),
	}

	# def search(self, cr, uid, ids, context=None):
	# 	srch = self.pool.get('account.account').search(cr,uid,[('account_selection','=','against_ref')])
	# 	for acc_id in self.pool.get('account.account').browse(cr,uid,srch):
	# 		account_id_cash = acc_id.name
	# 	for res in self.browse(cr,uid,ids):
	# 		self.write(cr,uid,ids,{'select_all':False})#18Nov2015
	# 		today_date = datetime.now().date()
	# 		py_date = str(today_date + relativedelta(days=-1))
	# 		cr.execute("delete from search_sales_receipt_line where srch_date < %(date)s",{'date':today_date}) 
	# 		cr.execute("delete from search_sales_receipt_line where search_receipt_id =%(val)s",{'val':res.id})
	# 		Sql_Str = ''
	# 		list_id = []
	# 		receipt_no = res.receipt_no
	# 		customer_name = res.customer_name.id
	# 		date_from = res.date_from
	# 		date_to = res.date_to
	# 		contact_name = res.contact_name
	# 		contact_no = res.contact_no
	# 		cse = res.cse.id
	# 		invoice_no = res.invoice_no
	# 		acc_status_new = res.acc_status_new
	# 		cheque_cash =res.cheque_cash
	# 		customer_id = res.customer_id
	# 		state = res.state
						
	# 		try:
	# 			if receipt_no:
	# 				Sql_Str = Sql_Str + " and ACS.receipt_no ilike '" + "%" + str(receipt_no) + "%'"

	# 			if customer_name:
	# 				Sql_Str = Sql_Str + " and ACS.customer_name = '" + str(customer_name) + "'"

	# 			if date_from:
	# 				Sql_Str =Sql_Str +" and ACS.receipt_date  >= '" + str(date_from) + "'"
					
	# 			if date_to:
	# 				Sql_Str =Sql_Str +" and ACS.receipt_date <= '" + str(date_to) + "'"

	# 			if acc_status_new :
	# 				Sql_Str = Sql_Str + " and ACC.acc_status = '" + str(acc_status_new) + "'"

	# 			if state :
	# 				Sql_Str = Sql_Str + " and ACS.state = '" + str(state) + "'"
				
	# 			if contact_name:
	# 				Sql_Str = Sql_Str + " and ACS.customer_name in (select RP.id from res_partner RP where RP.contact_name ilike '" + "%" + str(contact_name) + "%')"

	# 			if customer_id:
	# 				Sql_Str = Sql_Str + " and ACS.customer_id_invisible ilike '" + "%" + str(customer_id) + "%'"

	# 			if contact_no:
	# 				Sql_Str = Sql_Str + " and ACS.customer_name in (select PN.partner_id from phone_number_child PN where PN.number ilike'"  + "%" + str(contact_no) + "%')" 

	# 			if cse:
	# 				Sql_Str = Sql_Str + " and (ACC.id in (select IRH.receipt_id_history from  invoice_receipt_history IRH where IRH.cse="+ str(cse) +") or ACC.id in (select ADR.advance_id from  advance_sales_receipts ADR where ADR.cse="+ str(cse) +")) "
					
	# 				'''Sql_Str = Sql_Str + " and ACC.acc_status = 'against_ref' and ACC.id in (select IRH.receipt_id_history from invoice_adhoc_master IAM , invoice_receipt_history IRH where partner_id in ( select partner_id from customer_line where cse ='" + str(cse) + "' ) AND IRH.invoice_receipt_history_id =IAM.id and IRH.cse="+ str(cse) +")" '''

	# 			if invoice_no:
	# 				Sql_Str = Sql_Str + " and ACC.acc_status = 'against_ref' and ACC.id in (select IAM.invoice_id_receipt from invoice_adhoc_master IAM where IAM.invoice_number ilike '" + "%" + str(invoice_no) + "%" + "')"

	# 			Sql_Str = Sql_Str + " and ACS.psd_accounting = 'f'"
				 
	# 			Main_Str = "select distinct on(ACS.id) ACS.receipt_date,ACS.receipt_no,ACS.new_cus_name,ACS.customer_name,ACS.credit_amount,"+str(res.id)+" ,'''"+str(today_date)+"''' from account_sales_receipts_line ACC,account_sales_receipts ACS where ACC.receipt_id = ACS.id and ACS.receipt_no is not null"
				
	# 			Main_Str1 = Main_Str + Sql_Str
				
	# 			cash = "select ACC.id from account_sales_receipts_line ACC,account_sales_receipts ACS where ACC.receipt_id = ACS.id and ACS.receipt_no is not null" 
	# 			cash_all = cash + Sql_Str
	# 			cash_id = []
	# 			cr.execute(cash_all)
	# 			cash_id.extend([r[0] for r in cr.fetchall()])
	# 			cash_receipt_id = []
	# 			cheque_receipt_id = []
	# 			dd_receipt_id = []
	# 			neft_receipt_id =[]
	# 			sub_str1 =''
	# 			if cheque_cash:
	# 				if cheque_cash =='cash' :
	# 					for ln in self.pool.get('account.sales.receipts.line').browse(cr,uid,cash_id):
	# 						if ln.account_id.account_selection == 'cash':
	# 							if ln.receipt_id.id not in cash_receipt_id:
	# 								cash_receipt_id.extend([ln.receipt_id.id])
	# 					if cash_receipt_id is not None :
	# 						sub_str1 = " and ACS.id is null"
	# 						cash_receipt_id = tuple(cash_receipt_id)
	# 						cash_receipt_id = ", ".join(str(cash_receipt_id) for cash_receipt_id in cash_receipt_id) #MHM 6oct
	# 						if not cash_receipt_id:
	# 							cash_receipt_id = 'NULL'
	# 						sub_str1 = " and ACS.id in (" + str(cash_receipt_id) +")"

	# 				if cheque_cash =='check' and acc_status_new =='against_ref':
	# 					for ln in self.pool.get('account.sales.receipts.line').browse(cr,uid,cash_id):
	# 						if (ln.account_id.account_selection in ('iob_one','iob_two')) and ln.payment_method == 'cheque':
	# 							if ln.receipt_id.id not in cheque_receipt_id:
	# 								cheque_receipt_id.extend([ln.receipt_id.id])
	# 					if cheque_receipt_id is not None :
	# 						sub_str1 = " and ACS.id is null"

	# 					cheque_receipt_id = tuple(cheque_receipt_id)
	# 					cheque_receipt_id = ", ".join(str(cheque_receipt_id) for cheque_receipt_id in cheque_receipt_id)
	# 					if not cheque_receipt_id:
	# 						cheque_receipt_id = 'NULL'
	# 					sub_str1 = " and ACS.id in (" + str(cheque_receipt_id) +")"

	# 				if cheque_cash =='neft': ## >> for neft search 24 Dec
	# 					for ln in self.pool.get('account.sales.receipts.line').browse(cr,uid,cash_id):
	# 						if ln.account_id.account_selection == 'iob_one' and ln.payment_method == 'neft':
	# 							if ln.receipt_id.id not in neft_receipt_id:
	# 								neft_receipt_id.extend([ln.receipt_id.id]) 

	# 					if neft_receipt_id is not None :
	# 						neft_receipt_id = tuple(neft_receipt_id)
	# 						neft_receipt_id = ", ".join(str(neft_receipt_id) for neft_receipt_id in neft_receipt_id)
	# 						if not neft_receipt_id :
	# 							neft_receipt_id='NULL'
	# 						sub_str1 = " and ACS.id in (" + str(neft_receipt_id) +")"
					
	# 				if cheque_cash =='dd':
	# 					for ln in self.pool.get('account.sales.receipts.line').browse(cr,uid,cash_id):
	# 						if ln.account_id.account_selection == 'iob_one' and ln.payment_method == 'Dd':
	# 							if ln.receipt_id.id not in dd_receipt_id:
	# 								dd_receipt_id.extend([ln.receipt_id.id])

	# 					if dd_receipt_id is not None :
	# 						dd_receipt_id = tuple(dd_receipt_id)
	# 						dd_receipt_id = ", ".join(str(dd_receipt_id) for dd_receipt_id in dd_receipt_id)
	# 						if not dd_receipt_id :
	# 							dd_receipt_id='NULL'
	# 						sub_str1 = " and ACS.id in (" + str(dd_receipt_id) +")"
					
	# 				##################################################################################
	# 			insert_command = "insert into search_sales_receipt_line (receipt_date,receipt_no,new_cus_name,customer_name,credit_amount,search_receipt_id,srch_date) ("+Main_Str1+ sub_str1 +")"
	# 			cr.execute(insert_command)
	# 		except Exception  as exc:
	# 				cr.rollback()
	# 				if exc.__class__.__name__ == 'TransactionRollbackError':
	# 					pass
	# 				elif exc.__class__.__name__ == 'ProgrammingError':#Programming error: syntax error at or near ")"
	# 					#pass
	# 					for line in res.search_sales_receipt_line:
	# 						self.pool.get('search.sales.receipt.line').write(cr,uid,line.id,{'search_receipt_id':False})
	# 				else:
	# 					raise
	# 	return True


	def psd_search(self, cr, uid, ids, context=None):
		srch = self.pool.get('account.account').search(cr,uid,[('account_selection','=','against_ref')])
		for acc_id in self.pool.get('account.account').browse(cr,uid,srch):
			account_id_cash = acc_id.name
		for res in self.browse(cr,uid,ids):
			self.write(cr,uid,ids,{'select_all':False})#18Nov2015
			today_date = datetime.now().date()
			py_date = str(today_date + relativedelta(days=-1))
			cr.execute("delete from search_sales_receipt_line where srch_date < %(date)s",{'date':today_date}) 
			cr.execute("delete from search_sales_receipt_line where search_receipt_id =%(val)s",{'val':res.id})
			Sql_Str = ''
			list_id = []
			receipt_no = res.receipt_no
			# customer_name = res.customer_name.name
			customer_name_text = res.customer_name_text
			date_from = res.date_from
			date_to = res.date_to
			contact_name = res.contact_name
			# contact_no = res.contact_no
			cse = res.cse.id
			invoice_no = res.invoice_no
			acc_status_new = res.acc_status_new
			cheque_cash =res.cheque_cash
			customer_id = res.customer_id
			state = res.state
						
			try:
				if receipt_no:
					Sql_Str = Sql_Str + " and ACS.receipt_no ilike '" + "%" + str(receipt_no) + "%'"

				# if customer_name:
				# 	Sql_Str = Sql_Str + " and ACS.customer_name = '" + str(customer_name) + "'"

				if customer_name_text:
					Sql_Str = Sql_Str + " and ACS.text_customer_name = '" + str(customer_name_text) + "'"	

				if date_from:
					Sql_Str =Sql_Str +" and ACS.receipt_date  >= '" + str(date_from) + "'"
					
				if date_to:
					Sql_Str =Sql_Str +" and ACS.receipt_date <= '" + str(date_to) + "'"

				if acc_status_new :
					Sql_Str = Sql_Str + " and ACC.acc_status = '" + str(acc_status_new) + "'"

				if state :
					Sql_Str = Sql_Str + " and ACS.state = '" + str(state) + "'"
				
				# if contact_name:
				# 	Sql_Str = Sql_Str + " and ACS.customer_name in (select RP.id from res_partner RP where RP.contact_name ilike '" + "%" + str(contact_name) + "%')"

				if customer_id:
					Sql_Str = Sql_Str + " and ACS.customer_id_invisible ilike '" + "%" + str(customer_id) + "%'"

				# if contact_no:
				# 	Sql_Str = Sql_Str + " and ACS.customer_name in (select PN.partner_id from phone_number_child PN where PN.number ilike'"  + "%" + str(contact_no) + "%')" 

				if cse:
					Sql_Str = Sql_Str + " and (ACC.id in (select IRH.receipt_id_history from  invoice_receipt_history IRH where IRH.cse="+ str(cse) +") or ACC.id in (select ADR.advance_id from  advance_sales_receipts ADR where ADR.cse="+ str(cse) +")) "
					
					'''Sql_Str = Sql_Str + " and ACC.acc_status = 'against_ref' and ACC.id in (select IRH.receipt_id_history from invoice_adhoc_master IAM , invoice_receipt_history IRH where partner_id in ( select partner_id from customer_line where cse ='" + str(cse) + "' ) AND IRH.invoice_receipt_history_id =IAM.id and IRH.cse="+ str(cse) +")" '''

				if invoice_no:
					Sql_Str = Sql_Str + " and ACC.acc_status = 'against_ref' and ACC.id in (select IAM.invoice_id_receipt from invoice_adhoc_master IAM where IAM.invoice_number ilike '" + "%" + str(invoice_no) + "%" + "')"

				Sql_Str = Sql_Str + " and ACS.psd_accounting = 't'"
				 
				Main_Str = "select distinct on(ACS.id) ACS.receipt_date,ACS.receipt_no,ACS.new_cus_name,ACS.text_customer_name,ACS.credit_amount,"+str(res.id)+" ,'''"+str(today_date)+"''' from account_sales_receipts_line ACC,account_sales_receipts ACS where ACC.receipt_id = ACS.id and ACS.receipt_no is not null"
				
				Main_Str1 = Main_Str + Sql_Str
				
				cash = "select ACC.id from account_sales_receipts_line ACC,account_sales_receipts ACS where ACC.receipt_id = ACS.id and ACS.receipt_no is not null" 
				cash_all = cash + Sql_Str
				cash_id = []
				cr.execute(cash_all)
				cash_id.extend([r[0] for r in cr.fetchall()])
				cash_receipt_id = []
				cheque_receipt_id = []
				dd_receipt_id = []
				neft_receipt_id =[]
				sub_str1 =''
				if cheque_cash:
					if cheque_cash =='cash' :
						for ln in self.pool.get('account.sales.receipts.line').browse(cr,uid,cash_id):
							if ln.account_id.account_selection == 'cash':
								if ln.receipt_id.id not in cash_receipt_id:
									cash_receipt_id.extend([ln.receipt_id.id])
						if cash_receipt_id is not None :
							sub_str1 = " and ACS.id is null"
							cash_receipt_id = tuple(cash_receipt_id)
							cash_receipt_id = ", ".join(str(cash_receipt_id) for cash_receipt_id in cash_receipt_id) #MHM 6oct
							if not cash_receipt_id:
								cash_receipt_id = 'NULL'
							sub_str1 = " and ACS.id in (" + str(cash_receipt_id) +")"

					if cheque_cash =='check' and acc_status_new =='against_ref':
						for ln in self.pool.get('account.sales.receipts.line').browse(cr,uid,cash_id):
							if (ln.account_id.account_selection in ('iob_one','iob_two')) and ln.payment_method == 'cheque':
								if ln.receipt_id.id not in cheque_receipt_id:
									cheque_receipt_id.extend([ln.receipt_id.id])
						if cheque_receipt_id is not None :
							sub_str1 = " and ACS.id is null"

						cheque_receipt_id = tuple(cheque_receipt_id)
						cheque_receipt_id = ", ".join(str(cheque_receipt_id) for cheque_receipt_id in cheque_receipt_id)
						if not cheque_receipt_id:
							cheque_receipt_id = 'NULL'
						sub_str1 = " and ACS.id in (" + str(cheque_receipt_id) +")"

					if cheque_cash =='neft': ## >> for neft search 24 Dec
						for ln in self.pool.get('account.sales.receipts.line').browse(cr,uid,cash_id):
							if ln.account_id.account_selection == 'iob_one' and ln.payment_method == 'neft':
								if ln.receipt_id.id not in neft_receipt_id:
									neft_receipt_id.extend([ln.receipt_id.id]) 

						if neft_receipt_id is not None :
							neft_receipt_id = tuple(neft_receipt_id)
							neft_receipt_id = ", ".join(str(neft_receipt_id) for neft_receipt_id in neft_receipt_id)
							if not neft_receipt_id :
								neft_receipt_id='NULL'
							sub_str1 = " and ACS.id in (" + str(neft_receipt_id) +")"
					
					if cheque_cash =='dd':
						for ln in self.pool.get('account.sales.receipts.line').browse(cr,uid,cash_id):
							if ln.account_id.account_selection == 'iob_one' and ln.payment_method == 'Dd':
								if ln.receipt_id.id not in dd_receipt_id:
									dd_receipt_id.extend([ln.receipt_id.id])

						if dd_receipt_id is not None :
							dd_receipt_id = tuple(dd_receipt_id)
							dd_receipt_id = ", ".join(str(dd_receipt_id) for dd_receipt_id in dd_receipt_id)
							if not dd_receipt_id :
								dd_receipt_id='NULL'
							sub_str1 = " and ACS.id in (" + str(dd_receipt_id) +")"
					
					##################################################################################
				insert_command = "insert into search_sales_receipt_line (receipt_date,receipt_no,new_cus_name,customer_name_text,credit_amount,search_receipt_id,srch_date) ("+Main_Str1+ sub_str1 +")"
				cr.execute(insert_command)
			except Exception  as exc:
					cr.rollback()
					if exc.__class__.__name__ == 'TransactionRollbackError':
						pass
					elif exc.__class__.__name__ == 'ProgrammingError':#Programming error: syntax error at or near ")"
						#pass
						for line in res.search_sales_receipt_line:
							self.pool.get('search.sales.receipt.line').write(cr,uid,line.id,{'search_receipt_id':False})
					else:
						raise
		return True

	def psd_clear(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			self.write(cr,uid,res.id,{
						'receipt_no':False,
						'customer_name':None,
						'cse':None,
						'invoice_no':False,
						'contact_no':False,
						'contact_name':False,
						'date_from':None,
						'date_to':None,
						'acc_status_new':None,
						'customer_id':False,
						'cheque_cash':False,
						'select_all':False,
						'state':False,
						'customer_name_text': False
						})
			for line in res.search_sales_receipt_line:
				self.pool.get('search.sales.receipt.line').write(cr,uid,line.id,{'search_receipt_id':False})
		return True	

	def open_new(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			#self.pool.get('account.sales.receipts').create(cr,uid,{'account_select_boolean':False})
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_form')
			return {'name': ("Sales Receipts Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.sales.receipts',
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
			context.update({'psd_accounting': True})
			models_data = self.pool.get('ir.model.data')
			print"context",context
			form_view = models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_sales_receipts_form')
			return {'name': ("Sales Receipts Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.sales.receipts',
					'target' : 'current',
					#'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					'context': context
					}

sales_receipts_search()

class search_sales_receipt_line(osv.osv):
	_inherit='search.sales.receipt.line'

	_columns={
		'cfob_customer_name': fields.char('CFOB Customer Name', size=100),
		'cfob_customer_id': fields.char('CFOB Customer ID', size=100),
		'customer_name_text': fields.char('Customer Name',size=200)
	}

	def psd_show_new(self, cr, uid, ids, context=None):
		for res in self.browse(cr, uid, ids):
			res_ids = self.pool.get('account.sales.receipts').search(cr, uid,[('receipt_no', '=', res.receipt_no), ('receipt_date', '=', res.receipt_date)])
			if res_ids:
				res_id=res_ids[0]
			for each_receipt in self.pool.get('account.sales.receipts').browse(cr, uid, [res_id]):
				if each_receipt.customer_name:
					cust_name=each_receipt.customer_name.name
					if cust_name == "CFOB":
						line_rec= self.pool.get('account.sales.receipts.line').search(cr,uid,[('receipt_id','=',res_id)])
						for each_line in self.pool.get('account.sales.receipts.line').browse(cr,uid,line_rec):
							acct_selctn=each_line.account_id.account_selection
							if acct_selctn  == 'against_ref':
								if each_line.partner_id:
									if each_line.partner_id.is_transfered:
										self.pool.get('account.sales.receipts').write(cr,uid,res_id,{'is_transfered':True})
										self.pool.get('account.sales.receipts.line').write(cr,uid,each_line,{'is_transfered':True})
					else:
						if each_receipt.customer_name.is_transfered:
							self.pool.get('account.sales.receipts').write(cr,uid,res_id,{'is_transfered':True})
							print "each each_receipt.id",each_receipt.id
							line_rec = self.pool.get('account.sales.receipts.line').search(cr,uid,[('receipt_id','=',each_receipt.id)])
							self.pool.get('account.sales.receipts.line').write(cr,uid,line_rec,{'is_transfered':True})
			return self.psd_show(cr, uid, ids, context)

	def show(self, cr, uid, ids, context=None):
			res_id= res_ids=''
			for res in self.browse(cr,uid,ids):
				res_ids = self.pool.get('account.sales.receipts').search(cr,uid,[
						('receipt_no','=',res.receipt_no),
						('receipt_date','=',res.receipt_date)])
				if res_ids:
					res_id=res_ids[0]
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_form')
				return {'name': ("Sales Receipt"),
						'domain': '[]',
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'account.sales.receipts',
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
				res_ids = self.pool.get('account.sales.receipts').search(cr,uid,[
						('receipt_no','=',res.receipt_no),
						('receipt_date','=',res.receipt_date)])
				if res_ids:
					res_id=res_ids[0]
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_sales_receipts_form')
				return {'name': ("Sales Receipt"),
						'domain': '[]',
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'account.sales.receipts',
						'target' : 'current',
						'res_id':int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								   (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True,
				}


	def show_details(self, cr, uid, ids, context=None):
		result = ''
		count = 0
		srch = False
		for res in self.browse(cr,uid,ids):
		        if res.state =='draft': 
		                cust_id=res.receipt_id.customer_name.id
			        receipt_id = res.receipt_id.id
			        search = self.pool.get('account.sales.receipts').search(cr,uid,[('id','=',receipt_id)])#aaaa
			        for rec in self.pool.get('account.sales.receipts').browse(cr,uid,search):
				        cust_id = rec.customer_name.id
				        if cust_id:   
					        srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[
						        ('status','in',('open','printed','partially_writeoff')),
						        ('partner_id','=',cust_id),('invoice_number','!=',''),
						        ('check_process_invoice','=',False),
						        ('pending_status','in',('open','pending'))])
					
					if srch:
						for advance in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
							if res.acc_status == 'against_ref':
								if rec.invoice_number:
									if rec.invoice_number == advance.invoice_number:
										count = count + 1
										self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'invoice_id_receipt':res.id,})
										self.write(cr,uid,res.id,{'credit_amount':advance.grand_total_amount})
								else:
									self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'invoice_id_receipt':res.id})

					if res.acc_status == 'against_ref':
						customer_name=rec.customer_name.id
						srch_debit=self.pool.get('debit.note').search(cr,uid,[('customer_name','=',customer_name),('state_new','=','open')])
						srch_debit2=self.pool.get('debit.note').search(cr,uid,[('sales_debit_id','=',res.id)])
						if srch_debit or srch_debit2 :
							debt_count =0
							flag=True
							for x in self.pool.get('debit.note').browse(cr,uid,srch_debit):
								for debit_id in x.debit_note_one2many:
									if debit_id.account_id.account_selection=='others':
										flag=False
										debt_count +=1
								if flag:
									self.pool.get('debit.note').write(cr,uid,x.id,{'sales_debit_id':res.id})
							if debt_count ==0:
								s=self.write(cr,uid,res.id,{'visib':True})
						else:
							s=self.write(cr,uid,res.id,{'visib':False})	
					if count == 1:
						cr.execute("update invoice_adhoc_master set check_invoice=%s where invoice_id_receipt=%s",(True,res.id))

					# As per vijay , 28apr
					# if (res.acc_status == 'advance' or res.account_id.account_selection == 'advance') and res.type == 'debit'):
					# 	srch_advance_ref1 = self.pool.get('advance.sales.receipts').search(cr,uid,[
					# 		('partner_id','=',cust_id),
					# 		('check_advance_against_ref','=',False)])
					# 
					# 	for advance_against1 in self.pool.get('advance.sales.receipts').browse(cr,uid,srch_advance_ref1):
					# 		self.pool.get('advance.sales.receipts').write(cr,uid,advance_against1.id,{'advance_ref_id':res.id})
						
		return True

	def save_against_ref_psd(self, cr, uid, ids, context=None):  #PENDING (CHECK AMOUNT PART)
		flag = False
		total = 0.0
		count = 0
		payment_status = '' 
		for res in self.browse(cr,uid,ids):
			payment_status  = res.receipt_id.payment_status
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			for line in res.invoice_adhoc_one2many:
				check_invoice = line.check_invoice
				pending_amount = line.pending_amount
				
				if check_invoice == True:
					if line.service_classification and line.tax_rate:
						if line.service_classification != 'exempted' and line.tax_rate not in res.account_id.name :
							if 'NT' in line.invoice_number:
								if 'Non' not in res.account_id.name :
									raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
							else :
								raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
					flag = True
					# if payment_status in ('partial_payment','short_payment') :
					# 	total += line.partial_payment_amount
						
					# 	if line.partial_payment_amount > line.pending_amount or line.partial_payment_amount == 0.0:
					# 		raise osv.except_osv(('Alert'),('Enter Proper Partial amount for Partial Payment'))
					# 	if (line.partial_payment_amount - line.pending_amount) == 0.0: ## alert for Select Full payment  
					# 		raise osv.except_osv(('Alert'),('Please Select Full payment '))
				
					# if payment_status == 'full_payment':
					total += pending_amount
			print"total",total
			for line2 in res.debit_note_one2many:
				check_debit=line2.check_debit	
				grand_total = line2.credit_amount_srch
				if check_debit == True:
					flag = True
					total += grand_total

			print"res.type",res.type
			if res.type=='debit':
				self.write(cr,uid,res.id,{'debit_amount':total})
			else:
				self.write(cr,uid,res.id,{'credit_amount':total})
				
		if flag == False:
			raise osv.except_osv(('Alert'),('No invoice selected.'))

		return {'type': 'ir.actions.act_window_close'}

search_sales_receipt_line ()


class account_sales_receipts(osv.osv):
	_inherit='account.sales.receipts'

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(account_sales_receipts, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	_columns = {
		'receipt_type1':fields.selection([('standard','Standard'),('cfob','CFOB')],'Receipt Type'),
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'is_cfob_customer': fields.boolean('CFOB Customer'),
		'cfob_customer_name': fields.char('CFOB Customer Name', size=100),
		'cfob_customer_id': fields.char('CFOB Customer ID', size=100),
		'psd_accounting': fields.boolean('PSD Accounting'),
		'text_customer_name': fields.char('Text Customer Name', size=200),
	}

	_defaults = {
		'receipt_type1': 'standard',
	}

	def onchange_cfob_customer(self,cr,uid,ids,is_cfob_customer,context=None):
		data = {}
		if is_cfob_customer == True:
			data = {'customer_name':False,'customer_id':False,'billing_location':False}
		return {'value':data}			

# 	def process(self, cr, uid, ids, context=None):# Sales receipt process
# 		#self.sync_receipt_history(cr,uid,ids)
# 		count = count1 = 0
# 		move = grand_total = invoice_date= invoice_number= iob_one_id = demand_draft_id = neft_id = ''
# 		flag_service = flag_debit = flag_against = flag = flag1 = flag2 = flag_sundry_deposit = py_date = False
# 		post=[]
# 		post2=[]
# 		status=[]
# 		security_id = advance_id = cofb_id = invoice_id_receipt = sales_debit_id = ''
# 		credit_amount_srch_amount= invoice_id_receipt_advance = advance_ref_id = advance_ref_id1 = receipt_date=''
# 		cheque_no = sundry_id = cfob_other_id = ''
# 		cheque_amount = adv_against_line= neft_amount = dd_amount = grand_total = 0.0
# 		ref_amount = ref_amount1 = ref_amount_adv = ref_amount_cofb = ref_amount_cfob_other = 0.0
# 		grand_total_against = grand_total_against_new = cr_total = dr_total = 0.0
# 		debit_note_amount = grand_total_advance = ref_amount_security = pay_amount = 0.0

# 		today_date = datetime.now().date()
# 		invoice_date_exceed = datetime.now().date()
# 		models_data=self.pool.get('ir.model.data')
# 		cfob_sync_flag=False
# 		for res1 in self.browse(cr,uid,ids):
# 			if res1.customer_name.name == 'CBOB':
# 				raise osv.except_osv(('Alert'),('Receipt for CBOB cannnot be Created.'))
# 			if res1.receipt_date:
# 			        check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
# 			        if check_bool:
# 			                if res1.receipt_date != str(today_date):
#         				        raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
#         			else:
#         			        py_date = str(today_date + relativedelta(days=-5))
# 				        if res1.receipt_date < str(py_date) or res1.receipt_date > str(today_date):
# 				        	raise osv.except_osv(('Alert'),('Kindly select Receipt Date 5 days earlier from current date.'))
# 				receipt_date=res1.receipt_date	
# 			else:
# 				receipt_date=datetime.now().date()
# 			acc_id=self.pool.get('account.account').search(cr,uid,[('account_selection','in',('cash','iob_one'))])
# 			for line1 in res1.sales_receipts_one2many:
# 				account_id = line1.account_id.id
# 				account_name = line1.account_id.name
# 				acc_status = line1.acc_status
# 				types = line1.type
# 				dr_total += line1.debit_amount
# 				cr_total += line1.credit_amount
# 				if account_id:
# 					temp = tuple([account_id])
# 					post.append(temp)
# 					for i in range(0,len(post)):
# 						for j in range(i+1,len(post)):
# 							if post[i][0] == post[j][0]:
# 								raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
# 				if line1.account_id in acc_id and line1.type != 'debit':
# 					raise osv.except_osv(('Alert'),('Bank/Cash Account should be debit.'))
					

# 		post2 = [r[0] for r in post]
# 		for post1 in post2:
# 			if  post1  in acc_id :
# 				flag_service = True
			
# 		if not flag_service:
# 			raise osv.except_osv(('Alert'),('Entry cannot be processed without cash/bank account.'))

# 		if round( dr_total,2) !=round( cr_total,2):
# 			raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

# 		if dr_total == 0.0 or cr_total == 0.0:
# 			raise osv.except_osv(('Alert'),('Amount cannot be zero.')) 

# 		for res in self.browse(cr,uid,ids):
# 			for ln_itds in res.sales_receipts_one2many:
# 			        if ln_itds.credit_amount == 0 and ln_itds.debit_amount == 0:
# 					raise osv.except_osv(('Alert'),('Amount Cannot be zero'))
					
# 				# if (ln_itds.acc_status == 'against_ref') and  ln_itds.customer_name.name !='CFOB':
# 				# 	if ln_itds.account_id.account_selection == 'itds_receipt':
# 				# 		if ln_itds.debit_amount != 0.0 and ln_itds.customer_name.tan_no == False:
# 				# 			raise osv.except_osv(('Alert'),('Kindly fill the Tan Number of customer.'))
			
# 			for line in res.sales_receipts_one2many:
# 				acc_selection = line.account_id.account_selection
# 				account_name = line.account_id.name
# 				if line.credit_amount:
# 					if line.credit_amount == 0.0:
# 						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
# 				if line.debit_amount:
# 					if line.debit_amount == 0.0:
# 						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				
# 				if acc_selection == 'iob_one':
# 					for iob_one_line in line.iob_one_one2many:
# 						iob_one_id = iob_one_line.iob_one_id.id
# 						cheque_no = iob_one_line.cheque_no
# 						cheque_amount += iob_one_line.cheque_amount

# 						for n in str(iob_one_line.cheque_no):
# 							p = re.compile('([0-9]{6}$)')
# 							if p.match(iob_one_line.cheque_no)== None :
# 								self.pool.get('iob.one.sales.receipts').create(cr,uid,{'cheque_no':''})
# 								raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))

# 						if not iob_one_line.cheque_date:
# 							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
# 						if not iob_one_line.cheque_no:
# 							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
# 						if not iob_one_line.drawee_bank_name:
# 							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
# 						if not iob_one_line.bank_branch_name:
# 							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
# 						if not iob_one_line.selection_cts:
# 							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))

# 					for demand_draft_line in line.demand_draft_one_one2many: #DD
# 						demand_draft_id = demand_draft_line.demand_draft_id.id
# 						dd_no = demand_draft_line.dd_no
# 						dd_amount += demand_draft_line.dd_amount
						
# 						for n in str(demand_draft_line.dd_no):
# 							p = re.compile('([0-9]{6,9}$)')
# 							if p.match(demand_draft_line.dd_no)== None :
# 								self.pool.get('demand.draft.sales.receipts').create(cr,uid,{'dd_no':''})
# 								raise osv.except_osv(('Alert!'),('Please Enter 6 to 9 digit Demand draft Number.'))

# 						if not demand_draft_line.dd_date:
# 							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
# 						if not demand_draft_line.dd_no:
# 							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
# 						if not demand_draft_line.demand_draft_drawee_bank_name:
# 							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
# 						if not demand_draft_line.dd_bank_branch_name:
# 							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
# 						if not demand_draft_line.selection_cts:
# 							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))


# 					for neft_line in line.neft_one2many:
# 						neft_id = neft_line.neft_id.id
# 						neft_amount +=  neft_line.neft_amount

# 						if not neft_line.beneficiary_bank_name:
# 							raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
# 						if not neft_line.pay_ref_no:
# 							raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
# 						if not neft_line.neft_amount:
# 							raise osv.except_osv(('Alert!'),('Please provide Amount for NEFT/RTGS.'))

# 					if not iob_one_id:
# 						if not neft_id:
# 							if not demand_draft_id:
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

# 					if iob_one_id or neft_id or demand_draft_id: #16mar 
# 						if cheque_amount:
# 							bank_amount = cheque_amount
# 						elif dd_amount:
# 							bank_amount = dd_amount
# 						elif neft_amount:
# 							bank_amount = neft_amount
# 						if line.debit_amount:
# 							if round(bank_amount,2) != round(line.debit_amount,2):
# 								raise osv.except_osv(('Alert'),('Debit amount should be equal'))
# 						if line.credit_amount:
# 							if round(bank_amount,2) != round(line.credit_amount,2):
# 								raise osv.except_osv(('Alert'),('credit amount should be equal'))


# 				if acc_selection == 'advance' and line.type == 'credit':
# 					self.check_tax_rate(cr, uid, account_id)
# 					for advance_line in line.advance_one2many:
# 						advance_id = advance_line.advance_id.id
# 						ref_amount_adv = ref_amount_adv + advance_line.ref_amount
# 						if not advance_line.ref_no:
# 							raise osv.except_osv(('Alert'),('Please provide reference number.'))

# 						if not advance_line.ref_date:
# 							raise osv.except_osv(('Alert'),('Please provide reference date.'))
				
# 					if not advance_id:
# 						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 					elif advance_id:
# 						if line.debit_amount:
# 							if round(ref_amount_adv,2) != round(line.debit_amount,2):
# 									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
# 						if line.credit_amount:
# 							if round(ref_amount_adv,2) != round(line.credit_amount,2):
# 								   raise osv.except_osv(('Alert'),('credit amount should be equal'))

# 				if line.acc_status != 'advance':
# 					if line.invoice_adhoc_one2many:
# 						for inv_date in line.invoice_adhoc_one2many:
# 							if inv_date.check_invoice == True:
# 								invoice_date_exceed=inv_date.invoice_date
# 					if line.sales_other_cfob_one2many:
# 						for cfob_other in  line.sales_other_cfob_one2many:
# 							 invoice_date_exceed = cfob_other.ref_date
# 					if res.receipt_date == False :
# 						res.receipt_date=str(datetime.now().date())
# 					if str(res.receipt_date) < str(invoice_date_exceed):
# 						if line.invoice_adhoc_one2many or line.sales_other_cfob_one2many :
# 							raise osv.except_osv(('Alert'),('Invoice date is greater than receipt date. Select proper receipt date or for back-date entry select status as advance.'))

# 					if acc_selection == 'security_deposit': #  14mar
# 						sec_id = security_id = ''
# 						customer_name = line.receipt_id.customer_name.id

# 						if line.acc_status == 'new_reference':
# 							payment_status = line.receipt_id.payment_status
# 							# receipt_date = line.receipt_id.receipt_date
# 							# customer_name = line.receipt_id.customer_name
# 							ref_amount_security = 0.0
# 							for sec_new_line in line.security_new_ref_one2many:
# 								if sec_new_line.security_check_new_ref == True:
# 									security_id = sec_new_line.security_new_ref_id.id
# 									sec_id = sec_new_line.id
# 									ref_date = sec_new_line.ref_date
# 									ref_no = sec_new_line.ref_no
# 									ref_amount = sec_new_line.ref_amount
# 									pending_amount = sec_new_line.pending_amount
# 									partial_payment_amount = sec_new_line.partial_payment_amount
# 									# ref_amount_security = ref_amount_security + sec_new_line.ref_amount
# 									ref_amount_security += (sec_new_line.partial_payment_amount if payment_status == 'partial_payment' else sec_new_line.pending_amount )  
# 									pending_amount -= (sec_new_line.partial_payment_amount \
# 													   if payment_status == 'partial_payment' \
# 													   else sec_new_line.pending_amount) 

# 									self.pool.get('security.deposit').write(cr,uid,sec_id,{ #  14mar
# 										'security_check_process':True if pending_amount == 0.0 else False,
# 										'pending_amount':pending_amount,
# 										 'customer_name':customer_name,
# 										 'customer_name_char':res.customer_name.name if  res.customer_name.name else '',
# 										 'acc_status_new':line.acc_status,
# 										})
# 									# for i in sec_new_line.security_deposit_history_one2many:
# 									self.pool.get('security.deposit.history').create(cr,uid,{ #  14mar
# 										'security_deposit_id':sec_id,
# 										'ref_no':ref_no,
# 										'customer_name':customer_name,
# 										'ref_amount':ref_amount,
# 										'pending_amount':pending_amount,
# 										'partial_payment_amount':sec_new_line.partial_payment_amount if payment_status == 'partial_payment' else sec_new_line.pending_amount,
# 										'ref_date':ref_date,
# 										'receipt_date':receipt_date if receipt_date else '',
# 										'receipt_id':line.id,
# 										'new_sec':True
# 										})

# 							if not security_id and res.account_select_boolean==False:####changes for receipt from sales 
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 							if not security_id :####changes for receipt from sales   
# 								if line.debit_amount > 0.0 or line.credit_amount > 0.0:
# 									raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 							elif security_id:
# 								if line.debit_amount:
# 									if  round(ref_amount_security,2) != round(line.debit_amount,2):
# 										raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
# 								if line.credit_amount:
# 									if  round(ref_amount_security,2) != round(line.credit_amount,2):
# 										raise osv.except_osv(('Alert'),('credit amount should be equal.'))


# 					if acc_selection == 'sundry_deposit':
# 						for sun_dep_line in line.sundry_deposit_one2many:
# 							if sun_dep_line.sundry_check == True:
# 								flag_sundry_deposit = True
# 								sundry_id = sun_dep_line.sundry_id.id
# 								pay_amount +=  sun_dep_line.payment_amount
# 								self.pool.get('sundry.deposit').write(cr,uid,sun_dep_line.id,{'sundry_check_process':True})

# 							if not sundry_id:
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 							if line.debit_amount:
# 								if  round(pay_amount,2) != round(line.debit_amount,2):
# 									raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
# 							if line.credit_amount:
# 								if  round(pay_amount,2) != round(line.credit_amount,2):
# 									raise osv.except_osv(('Alert'),('Credit amount should be equal.'))
															
# 					if acc_selection == 'others':
# 						for cofb_line in line.cofb_one2many:
# 							cofb_id = cofb_line.cofb_id.id
# 							ref_amount_cofb = ref_amount_cofb + cofb_line.ref_amount
# 						if not cofb_id:
# 							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 						elif cofb_id:
# 						     if line.debit_amount:
# 						        if round(ref_amount_cofb,2)  != round(line.debit_amount,2):
# 						               raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
# 						     if line.credit_amount:
# 						        if round(ref_amount_cofb,2)  != round(line.credit_amount,2):
# 						               raise osv.except_osv(('Alert'),('credit amount should be equal.'))
						               
# 					if line.acc_status == 'others' and acc_selection == 'against_ref':
# 						cfob_id = ''
# 						if line.customer_name.name == 'CFOB':
# 							for cfob_other_line in line.sales_other_cfob_one2many:
# 							        cfob_sync_flag = True
# 								cfob_other_id = cfob_other_line.cfob_other_id.id
# 								ref_amount_cfob_other = ref_amount_cfob_other + cfob_other_line.ref_amount
# 								cfob_id = cfob_other_line.id
# 								self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_other_line.id,{'check_cfob_sales_process':True})
# 							if line.invoice_cfob_one2many:
# 								for invoice_cfob_line in line.invoice_cfob_one2many:
# 									if invoice_cfob_line.cfob_chk_invoice:
# 										ref_amount_cfob_other = ref_amount_cfob_other + invoice_cfob_line.pending_amount #grand_total 
# 										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_cfob_line.id,{
# 											'cfob_chk_invoice_process':True,
# 											'status':'paid',
# 											'invoice_paid_date':datetime.now().date(),
# 											'pending_status':'paid'})

# ####### history maintained for cfob other (mix entry) 8 sept 15  ######
# 										self.pool.get('invoice.receipt.history').create(cr,uid,{
# 											'invoice_receipt_history_id':invoice_cfob_line.id,
# 											'invoice_number':invoice_cfob_line.invoice_number,
# 											'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 											'receipt_id_history':line.id,
# 											'invoice_pending_amount':0.0,
# 											'invoice_paid_amount':invoice_cfob_line.pending_amount,
# 											'invoice_date':invoice_cfob_line.invoice_date,
# 											'service_classification':invoice_cfob_line.service_classification,
# 											'tax_rate':invoice_cfob_line.tax_rate,
# 											'cse':invoice_cfob_line.cse.id,
# 											'check_invoice':True})

# ####### history maintained for cfob other (mix entry) 8 sept 15  ######
# 							if not cfob_other_id:
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name)) 
# 							elif cfob_other_id:
# 								if line.debit_amount:
# 									if round(ref_amount_cfob_other,2) != round(line.debit_amount,2):
# 											raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
# 								if line.credit_amount:
# 									if round(ref_amount_cfob_other,2) != round(line.credit_amount,2):
# 										raise osv.except_osv(('Alert'),('credit amount should be equal.'))              

# 					if acc_selection == 'against_ref' and line.acc_status == 'against_ref':
# 						pending_amt = credit_amount_srch_amount = 0.0 # Debit note amount added  18feb16
# 						if res.payment_status == False:
# 							raise osv.except_osv(('Alert'),('Select Payment Status.'))              
# 						for i in line.debit_note_one2many:
# 							if i.check_debit == True:
# 								flag = True
# 								sales_debit_id = i.sales_debit_id.id
# 								credit_amount_srch_amount = i.credit_amount_srch # Debit note amount added  18feb16
# 						count = 0
# 						for invoice_line in line.invoice_adhoc_one2many:
# 							invoice_id_receipt =  invoice_line.invoice_id_receipt.id
# 							if invoice_line.check_invoice == True:
# 								flag = True
# 								count +=  1
# 								grand_total_against += invoice_line.pending_amount##s
# 								# if res.payment_status == 'short_payment' or res.payment_status == 'full_payment':
# 								if res.payment_status in  ('short_payment','full_payment'):
# 									grand_total_against_new += invoice_line.pending_amount

# 								if res.payment_status == 'partial_payment':
# 									grand_total_against_new += invoice_line.partial_payment_amount
					
# 								if res.payment_status == 'partial_payment' and invoice_line.partial_payment_amount == 0.0:
# 									raise osv.except_osv(('Alert'),('partial amount cannot be zero.'))
								
# 						grand_total_against_new += credit_amount_srch_amount if credit_amount_srch_amount else 0.0  # 4may Debit note 
# 						credit_amount = line.credit_amount
# 						for invoice_line in line.invoice_adhoc_one2many:
# 							invoice_id_receipt =  invoice_line.invoice_id_receipt.id
# 							if res.payment_status == 'short_payment' and invoice_line.check_invoice == True:
# 								if grand_total_against_new < credit_amount :
# 									raise osv.except_osv(('Alert'),('credit amount should be less than invoice amount.')) #11 may 15

# 								if grand_total_against > credit_amount:####21Apr short payment
# 									if count > 1:
# 										count -= 1
# 										pending_amt = grand_total_against - credit_amount
# 										grand_total_against = grand_total_against - invoice_line.pending_amount 
# 										credit_amount -= invoice_line.pending_amount 

# 										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 											'pending_amount':0.0,
# 											'pending_status':'paid',
# 											'status':'paid'})
# 										self.pool.get('invoice.receipt.history').create(cr,uid,{
# 											'invoice_receipt_history_id':invoice_line.id,
# 											'invoice_number':invoice_line.invoice_number,
# 											'invoice_pending_amount':0.0,
# 											'invoice_paid_amount':invoice_line.pending_amount,
# 											'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 											'receipt_id_history':line.id,
# 											'invoice_date':invoice_line.invoice_date,
# 											'service_classification':invoice_line.service_classification,
# 											'tax_rate':invoice_line.tax_rate,
# 											'cse':invoice_line.cse.id,
# 											'check_invoice':True})######## For Payment history

# 									else:    
# 										pending_amt = grand_total_against - credit_amount
# 										#credit_amount = credit_amount - invoice_line.pending_amount 
										
# 										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 											'pending_amount':pending_amt,
# 											'pending_status':'pending',
# 											'status':'paid'})
# 										self.pool.get('invoice.receipt.history').create(cr,uid,{
# 											'invoice_receipt_history_id':invoice_line.id,
# 											'invoice_number':invoice_line.invoice_number,
# 											'invoice_pending_amount':pending_amt,
# 											'invoice_paid_amount':credit_amount,
# 											'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 											'receipt_id_history':line.id,
# 											'invoice_date':invoice_line.invoice_date,
# 											'service_classification':invoice_line.service_classification,
# 											'tax_rate':invoice_line.tax_rate,
# 											'cse':invoice_line.cse.id,
# 											'check_invoice':True})######## For Payment history

													   
# 								elif grand_total_against == line.credit_amount:
# 									self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 										'check_process_invoice':True,
# 										'pending_amount':pending_amt,
# 										'pending_status':'paid',
# 										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date()})

# 									self.pool.get('invoice.receipt.history').create(cr,uid,{
# 										'invoice_receipt_history_id':invoice_line.id,
# 										'invoice_number':invoice_line.invoice_number,
# 										'invoice_pending_amount':pending_amt,
# 										'invoice_paid_amount':credit_amount,
# 										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 										'receipt_id_history':line.id,
# 										'invoice_date':invoice_line.invoice_date,
# 										'service_classification':invoice_line.service_classification,
# 										'tax_rate':invoice_line.tax_rate,
# 										'cse':invoice_line.cse.id,
# 										'check_invoice':True})######## For Payment history

# 							elif res.payment_status == 'partial_payment':####Partial payment
# 								if invoice_line.check_invoice == True:
# 									if invoice_line.partial_payment_amount:
# 										if round(grand_total_against_new,2) > round(credit_amount,2)\
# 												or round(grand_total_against_new,2) < round(credit_amount,2):
# 											raise osv.except_osv(('Alert'),('credit amount and invoice partial amount should be equal.'))
# 										if (invoice_line.partial_payment_amount - invoice_line.pending_amount) == 0.0: ## alert for Select Full payment  
# 											raise osv.except_osv(('Alert'),('Please Select Full payment '))

# 										pending_amount = invoice_line.pending_amount - invoice_line.partial_payment_amount
# 										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 											'pending_amount':pending_amount,
# 											'pending_status':'pending',
# 											'status':invoice_line.status, #'printed',
# 											'partial_payment_amount':00})
# 										self.pool.get('invoice.receipt.history').create(cr,uid,{
# 											'invoice_receipt_history_id':invoice_line.id,
# 											'invoice_number':invoice_line.invoice_number,
# 											'invoice_pending_amount':pending_amount,
# 											'invoice_paid_amount':invoice_line.partial_payment_amount,
# 											'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 											'receipt_id_history':line.id,
# 											'invoice_date':invoice_line.invoice_date,
# 											'service_classification':invoice_line.service_classification,
# 											'tax_rate':invoice_line.tax_rate,
# 											'cse':invoice_line.cse.id,
# 											'check_invoice':True})######## For Payment history

# 							elif res.payment_status == 'full_payment':
# 								if invoice_line.check_invoice == True:
# 									if round(grand_total_against_new,2) < round(credit_amount,2)\
# 											or round(grand_total_against_new,2) > round(credit_amount,2) :
# 										raise osv.except_osv(('Alert'),('credit amount and invoice amount should be equal.')) #11may15

# 									pending_amt = grand_total_against - credit_amount
# 									self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 									        'check_process_invoice':True,
# 									        'pending_amount':0.0,
# 									        'pending_status':'paid',
# 									        'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 									        'status':'paid'}) 
# 									self.pool.get('invoice.receipt.history').create(cr,uid,{
# 										'invoice_receipt_history_id':invoice_line.id,
# 										'invoice_number':invoice_line.invoice_number,
# 										'invoice_pending_amount':pending_amt,
# 										'invoice_paid_amount':invoice_line.pending_amount,
# 										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 										'receipt_id_history':line.id,
# 										'invoice_date':invoice_line.invoice_date,
# 										'service_classification':invoice_line.service_classification,
# 										'tax_rate':invoice_line.tax_rate,
# 										'cse':invoice_line.cse.id,
# 										'check_invoice':True})######## For Payment history

							#else:
									#raise osv.except_osv(('Alert'),('Credit amount exceed the receipt value')
								
					# 	if flag == False:
					# 		raise osv.except_osv(('Alert'),('No invoice selected.'))

					# 	if not invoice_id_receipt and not sales_debit_id:
					# 		raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))


					# # 50k condition
					# if acc_selection == 'cash' and line.debit_amount >= 50000 or line.credit_amount >= 50000:
					# 	if line.customer_name.name !='CFOB': # 6 0ct 
					# 		if line.customer_name.pan_no == False:
					# 			raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))
					# 	else: # 6 0ct 
					# 		for reco in line.invoice_cfob_one2many:
					# 			if reco.partner_id.pan_no == False:
					# 				raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))

					# if line.acc_status == 'advance' and acc_selection == 'advance' and line.type == 'debit': # As per vijay , 28apr
					# 	for adv_against_line1 in line.advance_against_ref_one2many:
					# 		advance_ref_id1 = adv_against_line1.advance_ref_id.id
					# 		if adv_against_line1.check_advance_against_ref == True:
					# 			flag_debit = True
					# 			ref_amount1 = ref_amount1 + adv_against_line1.ref_amount
					# 			self.pool.get('advance.sales.receipts').write(cr,uid,adv_against_line1.id,{'check_advance_against_ref_process':True})	
					# 
					# 	if flag_debit == False:
					# 			raise osv.except_osv(('Alert'),('Advance record not selected.'))
					# 			    
					# 	if not line.advance_against_ref_one2many:
					# 	        raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					# 	if advance_ref_id1:
					# 		if line.debit_amount:
					# 			if round(ref_amount1,2) != round(line.debit_amount,2):
					# 				raise osv.except_osv(('Alert'),('Debit amount should be equal'))
					# 		if line.credit_amount:
					# 			if round(ref_amount1,2) != round(line.credit_amount,2):
					# 				raise osv.except_osv(('Alert'),('Credit amount should be equal'))


		# for rec in self.browse(cr,uid,ids):
		#         cse_name_id=False
		# 	receipt_no = temp_count= seq_srch= seq= invoice_num = invoice_date_concate = cse_name = ''
		# 	count=seq= grand_total = 0
		# 	cse_name_last= cse_name_last_cfob= cfob_invoice= cfob_invoice_date=cfob_cust=''
		# 	cfob_invoice_gross=0.0

		# 	acc_status = rec.acc_status
		# 	form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_form')
		# 	tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_tree')

		# 	seq_srch=self.pool.get('ir.sequence').search(cr,uid,[('code','=','account.sales.receipts')])
		# 	if seq_srch:
		# 		seq_start=self.pool.get('ir.sequence').browse(cr,uid,seq_srch[0]).number_next
				
		# 	ou_code = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		# 	ab_code = self.pool.get('res.users').browse(cr,uid,uid).company_id.sales_receipt_id
			
		# 	#year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		# 	month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		# 	today_date = datetime.now().date()
		# 	year = today_date.year
		# 	year1=today_date.strftime('%y')
		# 	if month > 3:
		# 		start_year = year
		# 		end_year = year+1
		# 		year1 = int(year1)+1
		# 	else:
		# 		start_year = year-1
		# 		end_year = year
		# 		year1 = int(year1)

		# 	financial_start_date = str(start_year)+'-04-01'
		# 	financial_end_date = str(end_year)+'-03-31'
			
		# 	today_date = datetime.now().date()
		# 	year = today_date.strftime('%y')
		# 	t1=[]
		# 	count=0
		# 	if  ou_code and ab_code:        
		# 		cr.execute("select cast(count(id) as integer) from account_sales_receipts where state not in ('draft') and receipt_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and import_flag = False"); # excluding imported advance through bills payable import 9 oct 15
		# 		temp_count=cr.fetchone()
		# 		if temp_count[0]:
		# 			count= temp_count[0]
		# 		seq=int(count+seq_start)
		# 		receipt_no = ou_code+ab_code+str(year1)+str(seq).zfill(6)

		# 	if rec.customer_name.name == 'CFOB':
		# 		for j in rec.sales_receipts_one2many:
		# 			if j.account_id.account_selection=='against_ref':
		# 				for k in j.sales_other_cfob_one2many:
		# 					if k.customer_cfob not in t1:
		# 						t1.extend([k.customer_cfob])
		# 		new_cus_name=', '.join(filter(bool,t1))
		# 	else:
		# 		new_cus_name=rec.customer_name.name
		
		# 	self.write(cr,uid,ids,{
		# 					'receipt_no':receipt_no,
		# 					'receipt_date': receipt_date,
		# 					'voucher_type':'Sales Receipt',
		# 					'new_cus_name':new_cus_name})
		# 	date = receipt_date 

		# 	search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
		# 	for var in self.pool.get('account.period').browse(cr,uid,search_date):
		# 		period_id = var.id

		# 	srch_jour_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
		# 	for jour_acc in self.pool.get('account.journal').browse(cr,uid,srch_jour_acc):
		# 		journal_id = jour_acc.id

		# 	srch_neft_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','NEFT/RTGS')])
		# 	for neft_acc in self.pool.get('account.journal').browse(cr,uid,srch_neft_acc):
		# 		neft_id = neft_acc.id

		# 	srch_jour_cash = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Cash')])
		# 	for jour_cash in self.pool.get('account.journal').browse(cr,uid,srch_jour_cash):
		# 		journal_cash = jour_cash.id

		# 	move = self.pool.get('account.move').create(cr,uid,{
		# 							'journal_id':journal_id,
		# 							'state':'posted',
		# 							'date':date ,
		# 							'name':receipt_no,
		# 							'voucher_type':'Sales Receipt',###added for day book
		# 							'narration':rec.narration if rec.narration else '',
		# 							},context=context)

		# 	for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
		# 		for ln in res.sales_receipts_one2many:
		# 			if ln.debit_amount:
		# 				self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
		# 						'account_id':ln.account_id.id,
		# 						'debit':ln.debit_amount,
		# 						'name':rec.customer_name.name if rec.customer_name.name else '',
		# 						'journal_id':journal_id,
		# 						'period_id':period_id,
		# 						'date':str(date),
		# 						'ref':receipt_no},context=context)
		# 			if ln.credit_amount:
		# 				self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
		# 						'account_id':ln.account_id.id,
		# 						'credit':ln.credit_amount,
		# 						'name':rec.customer_name.name if rec.customer_name.name else '',
		# 						'journal_id':journal_id,
		# 						'period_id':period_id,
		# 						'date':date,
		# 						'ref':receipt_no},context=context)

		# 	for ln in res.sales_receipts_one2many:
		# 		if ln.acc_status == 'against_ref':
		# 			invoice_number = ''
		# 			if ln.account_id.account_selection == 'against_ref':
		# 				for debit_line in ln.debit_note_one2many:
		# 					debit_note_no=debit_line.debit_note_no
		# 					if debit_line.check_debit == True:
		# 						srch_debit=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',debit_note_no)])
		# 						for i in self.pool.get('debit.note').browse(cr,uid,srch_debit):
		# 							self.pool.get('debit.note').write(cr,uid,i.id,{'state_new':'paid'})

		# 				for invoice_line in ln.invoice_adhoc_one2many:
		# 					invoice_number = invoice_line.invoice_number
		# 					invoice_date = invoice_line.invoice_date
		# 					cse_name = emp_code = ''
		# 					if invoice_line.check_invoice == True :
		# 						date1= datetime.strptime(invoice_line.invoice_date, '%Y-%m-%d').date()
		# 						invoice_date= date1.strftime("%d-%m-%Y")
		# 						invoice_date_concate = [invoice_date,invoice_date_concate]
		# 						invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))
								
		# 						invoice_num = [str(invoice_line.invoice_number),invoice_num]
		# 						invoice_num = ' / '.join(filter(bool,invoice_num))
							
		# 						emp_code = str(invoice_line.cse.emp_code)
		# 						main_str = "select name from resource_resource where code ilike '" + "%" + str(emp_code) + "%'"
		# 						cr.execute(main_str)
		# 						first_name = cr.fetchone()
		# 						if first_name:
		# 							cse_name = str(first_name[0]) +' '+str(invoice_line.cse.last_name)
									 
		# 						grand_total += invoice_line.grand_total_amount
		# 						cse_name_id = invoice_line.cse.id
								
		# 						srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[('id','>',0),('invoice_number','=',invoice_number)])
		# 						for adhoc in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
		# 							invoice_paid_date = datetime.now().date()
		# 							self.pool.get('invoice.adhoc.master').write(cr,uid,adhoc.id,{'invoice_paid_date':invoice_paid_date,})
		# 							invoice_history_srch = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',invoice_number)])
		# 							if invoice_history_srch:
		# 								for invoice_history in self.pool.get('payment.contract.history').browse(cr,uid,invoice_history_srch):
		# 									self.pool.get('payment.contract.history').write(cr,uid,invoice_history.id,{'payment_status':'paid'})

		# 	###################################################################### itds 30 sep 2015#########################
		# invoice_gross_amount=0.0
		# cfob_invoice_no = cfob_invoice_date = '' # 27apr
		
		# for res in self.browse(cr,uid,ids):
		#         customer_id = res.customer_name.id
		#         customer_name = res.customer_name.name
		#         cust_ou_id = res.customer_name.ou_id
		        
		# 	for ln_itds in res.sales_receipts_one2many:
		# 		if res.customer_name.name == 'CFOB':
		# 			for cfob_line in ln_itds.sales_other_cfob_one2many:
		# 				customer_cfob = cfob_line.customer_cfob
		# 				cust_cfob_id = cfob_line.cust_cfob_id
						
		# 				cfob_invoice_no = [str(cfob_line.ref_no),cfob_invoice_no]
		# 				cfob_invoice_no = ' / '.join(filter(bool,cfob_invoice_no))
						
		# 				cfob_invoice_date = [cfob_line.ref_date,cfob_invoice_date]
		# 				cfob_invoice_date = ' / '.join(filter(bool,cfob_invoice_date))
						
		# 			for invoice_line_cfob in ln_itds.invoice_cfob_one2many:
					        
		# 				if invoice_line_cfob.cfob_chk_invoice == True:
		# 					customer_id= invoice_line_cfob.partner_id.id
		# 					customer_name= invoice_line_cfob.partner_id.name
		# 					cust_ou_id = invoice_line_cfob.partner_id.ou_id
							
		# 					invoice_num = [str(invoice_line_cfob.invoice_number),invoice_num]
		# 					invoice_num = ' / '.join(filter(bool,invoice_num))
							
		# 					invoice_date_concate = [invoice_line_cfob.invoice_date,invoice_date_concate]
		# 					invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))
								
		# 					cfob_invoice_gross=invoice_line_cfob.grand_total_amount
		# 					cse_name_id = invoice_line_cfob.cse.id
							
		# 		if ln_itds.acc_status == 'against_ref':
		# 		        if ln_itds.type == 'credit':
		# 			        invoice_gross_amount+=ln_itds.credit_amount
					        
		# 			if ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'debit':
		# 				self.pool.get('itds.adjustment').create(cr,uid,{
		# 						'receipt_no':receipt_no,
		# 						'receipt_date':res.receipt_date, #datetime.now().date(),
		# 						'gross_amt':invoice_gross_amount, 
		# 						'pending_amt':ln_itds.debit_amount,
		# 						'itds_amt':ln_itds.debit_amount,
		# 						'invoice_no':invoice_num if invoice_num else cfob_invoice_no,
		# 						'invoice_date':invoice_date_concate if invoice_date_concate else cfob_invoice_date ,
		# 						'customer_name_char':customer_name if customer_name else customer_cfob ,
		# 						'customer_name': customer_id if customer_id else res.customer_id.id,
		# 						'customer_id': cust_ou_id if cust_ou_id else cust_cfob_id ,
		# 						'itds_cse':cse_name_id,
		# 					})
		# 				self.write(cr,uid,rec.id,{'acc_status_new':res.acc_status})
							
		# 				################################# Itds end ####################################	
		# 			elif ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'credit':
		# 				for lns in ln_itds.revert_itds_one2many:
		# 					if lns.check == True:
		# 						total_pr = lns.total_revert + lns.partial_revert if lns.partial_revert else lns.pending_amt 
		# 						pending_amount=lns.pending_amt - (lns.partial_revert if lns.partial_revert else lns.pending_amt)
		# 						self.pool.get('itds.adjustment').write(cr,uid,lns.id,{
		# 												'pending_amt':pending_amount,
		# 												'state':'partially_reversed' if pending_amount else 'fully_reversed' ,
		# 												'total_revert':total_pr,
		# 												'partial_revert':0.0})

		# 			if ln_itds.account_id.account_selection == 'security_deposit' and ln_itds.type == 'debit':
		# 				self.pool.get('security.deposit').create(cr,uid,{
		# 				                'security_id':ln_itds.id,
		# 					        'cse':cse_name_id,
		# 					        'ref_no':res.receipt_no,
		# 					        'ref_date':res.receipt_date,
		# 					        'ref_amount':ln_itds.debit_amount,
		# 					        'pending_amount':ln_itds.debit_amount,
		# 						'security_check_against':True,
		# 						'customer_name':customer_id if customer_id else res.customer_id.id,
		# 						'acc_status_new':line.acc_status,
		# 						'customer_name_char':customer_name if customer_name else customer_cfob,
		# 						})
		# 		self.pool.get('account.sales.receipts.line').write(cr,uid,ln_itds.id,{'state':'done'})

		# 	self.write(cr,uid,rec.id,{'state':'done','acc_status':''})
			
		# 	# for state_line in rec.sales_receipts_one2many:
		# 	# 	self.pool.get('account.sales.receipts.line').write(cr,uid,state_line.id,{'state':'done'})

		# 	for settlement in self.browse(cr,uid,ids):
		# 		for set_line in settlement.sales_receipts_one2many:
		# 			if set_line.account_id.account_selection == 'advance' and set_line.acc_status == 'advance' and set_line.type == 'credit':
		# 				self.write(cr,uid,settlement.id,{
		# 					'check_settlement':True,
		# 					'advance_pending':set_line.credit_amount,
		# 					'new_ad':True,
		# 					})
		# 				for advance in set_line.advance_one2many:
  #                                                       self.pool.get('advance.sales.receipts').write(cr,uid,advance.id,{
  #                                                                               'receipt_no':settlement.receipt_no,
		# 					                        'receipt_date':settlement.receipt_date,})
							        
		# 		#self.sync_invoice_paid_state(cr,uid,ids,context=context)
		# 		self.delete_draft_records_sales(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
		# 		#####################################abhi itds importtant commneted##############

		# for rec_log in self.browse(cr,uid,ids):
		# 	customer_invoice_paid = date1=''
		# 	date1=str(datetime.now().date())

		# 	conv=time.strptime(str(date1),"%Y-%m-%d")
		# 	date1 = time.strftime("%d-%m-%Y",conv)
		# 	if rec_log.customer_name:
		# 		customer_invoice_paid= rec_log.customer_name.name+'   Customer Invoice   Paid  On    '+date1
		# 		customer_invoicepaid_date=self.pool.get('customer.logs').create(cr,uid,{
		# 							'customer_join':customer_invoice_paid,
		# 							'customer_id':rec.customer_name.id})


		# for receipt_his in self.browse(cr,uid,ids):
		# 	receipt_no=receipt_his.receipt_no
		# 	cust_name=receipt_his.customer_name.name
		# 	amount = 0.0
		# 	if receipt_his.receipt_date:
		# 		receipt_date=receipt_his.receipt_date
		# 	else:
		# 		receipt_date=datetime.now().date()
		# 	receipt_type=receipt_his.receipt_type
		# 	for receipt_line in receipt_his.sales_receipts_one2many:
		# 		amount += receipt_line.debit_amount

		# 	self.pool.get('receipt.history').create(cr,uid,{
		# 				'receipt_his_many2one':receipt_his.customer_name.id,
		# 				'receipt_number':receipt_no,
		# 				'reciept_date':receipt_date,
		# 				'reciept_type':receipt_type,
		# 				'reciept_amount':amount})
						
		# self.sales_receipt_account_account(cr,uid,ids)
		# self.sync_receipt_history(cr,uid,ids)
		# if cfob_sync_flag:             #SYNC CODE IS NOT READY to UNCOMMENT
		#         self.sync_CFOB_customer_entry(cr,uid,ids,context=context)

		# return  {
		# 		'name':'Sales Receipt',
		# 		'view_mode': 'form',
		# 		'view_id': False,
		# 		'view_type': 'form',
		# 		'res_model': 'account.sales.receipts',
		# 		'res_id':rec.id,
		# 		'type': 'ir.actions.act_window',
		# 		'target': 'current',
		# 		'domain': '[]',
		# 		'context': context,
		# 		}

# 	def psd_process(self, cr, uid, ids, context=None):# Sales receipt process
# 		#self.sync_receipt_history(cr,uid,ids)
# 		count = count1 = 0
# 		move = grand_total = invoice_date= invoice_number= iob_one_id = demand_draft_id = neft_id = ''
# 		flag_service = flag_debit = flag_against = flag = flag1 = flag2 = flag_sundry_deposit = py_date = False
# 		post=[]
# 		post2=[]
# 		status=[]
# 		security_id = advance_id = cofb_id = invoice_id_receipt = sales_debit_id = ''
# 		credit_amount_srch_amount= invoice_id_receipt_advance = advance_ref_id = advance_ref_id1 = receipt_date=''
# 		cheque_no = sundry_id = cfob_other_id = ''
# 		cheque_amount = adv_against_line= neft_amount = dd_amount = grand_total = 0.0
# 		ref_amount = ref_amount1 = ref_amount_adv = ref_amount_cofb = ref_amount_cfob_other = 0.0
# 		grand_total_against = grand_total_against_new = cr_total = dr_total = 0.0
# 		debit_note_amount = grand_total_advance = ref_amount_security = pay_amount = 0.0

# 		today_date = datetime.now().date()
# 		invoice_date_exceed = datetime.now().date()
# 		models_data=self.pool.get('ir.model.data')
# 		cfob_sync_flag=False
# 		for res1 in self.browse(cr,uid,ids):
# 			if res1.receipt_type1 == 'cbob':
# 				raise osv.except_osv(('Alert'),('Receipt for CBOB cannnot be Created.'))
# 			if res1.receipt_date:
# 					# check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
# 					# if check_bool:
# 					#         if res1.receipt_date != str(today_date):
# 					#           raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
# 					# else:
# 				if res1.receipt_date > str(today_date):
# 					raise osv.except_osv(('Alert'),("Forward-dated entries are not allowed!"))
# 				py_date = str(today_date + relativedelta(days=-5))
# 				if res1.receipt_date < str(py_date):
# 					raise osv.except_osv(('Alert'),('Only 5 days back-dated receipt date is allowed!'))
# 				receipt_date=res1.receipt_date  
# 			else:
# 				receipt_date=datetime.now().date()
# 			acc_id=self.pool.get('account.account').search(cr,uid,[('account_selection','in',('cash','iob_one'))])
# 			for line1 in res1.sales_receipts_one2many:
# 				account_id = line1.account_id.id
# 				account_name = line1.account_id.name
# 				acc_status = line1.acc_status
# 				types = line1.type
# 				dr_total += line1.debit_amount
# 				cr_total += line1.credit_amount
# 				if account_id:
# 					temp = tuple([account_id])
# 					post.append(temp)
# 					for i in range(0,len(post)):
# 						for j in range(i+1,len(post)):
# 							if post[i][0] == post[j][0]:
# 								raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
# 				if line1.account_id in acc_id and line1.type != 'debit':
# 					raise osv.except_osv(('Alert'),('Bank/Cash Account should be debit.'))
					

# 		post2 = [r[0] for r in post]
# 		for post1 in post2:
# 			if  post1  in acc_id :
# 				flag_service = True
			
# 		if not flag_service:
# 			raise osv.except_osv(('Alert'),('Entry cannot be processed without cash/bank account.'))

# 		if round( dr_total,2) !=round( cr_total,2):
# 			raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

# 		if dr_total == 0.0 or cr_total == 0.0:
# 			raise osv.except_osv(('Alert'),('Amount cannot be zero.')) 

# 		for res in self.browse(cr,uid,ids):
# 			for ln_itds in res.sales_receipts_one2many:
# 				if ln_itds.credit_amount == 0 and ln_itds.debit_amount == 0:
# 					raise osv.except_osv(('Alert'),('Amount Cannot be zero'))
					
# 				# if (ln_itds.acc_status == 'against_ref') and  ln_itds.customer_name.name !='CFOB':
# 				# 	if ln_itds.account_id.account_selection == 'itds_receipt':
# 				# 		if ln_itds.debit_amount != 0.0 and ln_itds.customer_name.tan_no == False:
# 				# 			raise osv.except_osv(('Alert'),('Kindly fill the Tan Number of customer.'))
			
# 			for line in res.sales_receipts_one2many:
# 				acc_selection = line.account_id.account_selection
# 				account_name = line.account_id.name
# 				if line.credit_amount:
# 					if line.credit_amount == 0.0:
# 						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
# 				if line.debit_amount:
# 					if line.debit_amount == 0.0:
# 						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				
# 				if acc_selection == 'iob_one':
# 					for iob_one_line in line.iob_one_one2many:
# 						iob_one_id = iob_one_line.iob_one_id.id
# 						cheque_no = iob_one_line.cheque_no
# 						cheque_amount += iob_one_line.cheque_amount

# 						for n in str(iob_one_line.cheque_no):
# 							p = re.compile('([0-9]{6}$)')
# 							if p.match(iob_one_line.cheque_no)== None :
# 								self.pool.get('iob.one.sales.receipts').create(cr,uid,{'cheque_no':''})
# 								raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))

# 						if not iob_one_line.cheque_date:
# 							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
# 						if not iob_one_line.cheque_no:
# 							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
# 						if not iob_one_line.drawee_bank_name:
# 							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
# 						if not iob_one_line.bank_branch_name:
# 							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
# 						if not iob_one_line.selection_cts:
# 							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))

# 					for demand_draft_line in line.demand_draft_one_one2many: #DD
# 						demand_draft_id = demand_draft_line.demand_draft_id.id
# 						dd_no = demand_draft_line.dd_no
# 						dd_amount += demand_draft_line.dd_amount
						
# 						for n in str(demand_draft_line.dd_no):
# 							p = re.compile('([0-9]{6,9}$)')
# 							if p.match(demand_draft_line.dd_no)== None :
# 								self.pool.get('demand.draft.sales.receipts').create(cr,uid,{'dd_no':''})
# 								raise osv.except_osv(('Alert!'),('Please Enter 6 to 9 digit Demand draft Number.'))

# 						if not demand_draft_line.dd_date:
# 							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
# 						if not demand_draft_line.dd_no:
# 							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
# 						if not demand_draft_line.demand_draft_drawee_bank_name:
# 							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
# 						if not demand_draft_line.dd_bank_branch_name:
# 							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
# 						if not demand_draft_line.selection_cts:
# 							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))


# 					for neft_line in line.neft_one2many:
# 						neft_id = neft_line.neft_id.id
# 						neft_amount +=  neft_line.neft_amount

# 						if not neft_line.beneficiary_bank_name:
# 							raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
# 						if not neft_line.pay_ref_no:
# 							raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
# 						if not neft_line.neft_amount:
# 							raise osv.except_osv(('Alert!'),('Please provide Amount for NEFT/RTGS.'))

# 					if not iob_one_id:
# 						if not neft_id:
# 							if not demand_draft_id:
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

# 					if iob_one_id or neft_id or demand_draft_id: #16mar 
# 						if cheque_amount:
# 							bank_amount = cheque_amount
# 						elif dd_amount:
# 							bank_amount = dd_amount
# 						elif neft_amount:
# 							bank_amount = neft_amount
# 						if line.debit_amount:
# 							if round(bank_amount,2) != round(line.debit_amount,2):
# 								raise osv.except_osv(('Alert'),('Debit amount should be equal'))
# 						if line.credit_amount:
# 							if round(bank_amount,2) != round(line.credit_amount,2):
# 								raise osv.except_osv(('Alert'),('credit amount should be equal'))


# 				if acc_selection == 'advance' and line.type == 'credit':
# 					self.check_tax_rate(cr, uid, account_id)
# 					for advance_line in line.advance_one2many:
# 						advance_id = advance_line.advance_id.id
# 						ref_amount_adv = ref_amount_adv + advance_line.ref_amount
# 						if not advance_line.ref_no:
# 							raise osv.except_osv(('Alert'),('Please provide reference number.'))

# 						if not advance_line.ref_date:
# 							raise osv.except_osv(('Alert'),('Please provide reference date.'))
				
# 					if not advance_id:
# 						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 					elif advance_id:
# 						if line.debit_amount:
# 							if round(ref_amount_adv,2) != round(line.debit_amount,2):
# 									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
# 						if line.credit_amount:
# 							if round(ref_amount_adv,2) != round(line.credit_amount,2):
# 								   raise osv.except_osv(('Alert'),('credit amount should be equal'))

# 				if line.acc_status != 'advance':
# 					if line.invoice_adhoc_one2many:
# 						for inv_date in line.invoice_adhoc_one2many:
# 							if inv_date.check_invoice == True:
# 								invoice_date_exceed=inv_date.invoice_date
# 					if line.sales_other_cfob_one2many:
# 						for cfob_other in  line.sales_other_cfob_one2many:
# 							 invoice_date_exceed = cfob_other.ref_date
# 					if res.receipt_date == False :
# 						res.receipt_date=str(datetime.now().date())
# 					if str(res.receipt_date) < str(invoice_date_exceed):
# 						if line.invoice_adhoc_one2many or line.sales_other_cfob_one2many :
# 							raise osv.except_osv(('Alert'),('Invoice date is greater than receipt date. Select proper receipt date or for back-date entry select status as advance.'))

# 					if acc_selection == 'security_deposit': #  14mar
# 						sec_id = security_id = ''
# 						if line.receipt_id.customer_name:
# 							customer_name = line.receipt_id.customer_name.name
# 						elif line.receipt_id.cfob_customer_name:
# 							customer_name = line.receipt_id.cfob_customer_name

# 						if line.acc_status == 'new_reference':
# 							payment_status = line.receipt_id.payment_status
# 							# receipt_date = line.receipt_id.receipt_date
# 							# customer_name = line.receipt_id.customer_name
# 							ref_amount_security = 0.0
# 							for sec_new_line in line.security_new_ref_one2many:
# 								if sec_new_line.security_check_new_ref == True:
# 									security_id = sec_new_line.security_new_ref_id.id
# 									sec_id = sec_new_line.id
# 									ref_date = sec_new_line.ref_date
# 									ref_no = sec_new_line.ref_no
# 									ref_amount = sec_new_line.ref_amount
# 									pending_amount = sec_new_line.pending_amount
# 									partial_payment_amount = sec_new_line.partial_payment_amount
# 									# ref_amount_security = ref_amount_security + sec_new_line.ref_amount
# 									ref_amount_security += (sec_new_line.partial_payment_amount if payment_status == 'partial_payment' else sec_new_line.pending_amount )  
# 									pending_amount -= (sec_new_line.partial_payment_amount \
# 													   if payment_status == 'partial_payment' \
# 													   else sec_new_line.pending_amount) 

# 									self.pool.get('security.deposit').write(cr,uid,sec_id,{ #  14mar
# 										'security_check_process':True if pending_amount == 0.0 else False,
# 										'pending_amount':pending_amount,
# 										 'customer_name':customer_name,
# 										 'customer_name_char':customer_name or '',
# 										 'acc_status_new':line.acc_status,
# 										})
# 									# for i in sec_new_line.security_deposit_history_one2many:
# 									self.pool.get('security.deposit.history').create(cr,uid,{ #  14mar
# 										'security_deposit_id':sec_id,
# 										'ref_no':ref_no,
# 										'customer_name':customer_name,
# 										'ref_amount':ref_amount,
# 										'pending_amount':pending_amount,
# 										'partial_payment_amount':sec_new_line.partial_payment_amount if payment_status == 'partial_payment' else sec_new_line.pending_amount,
# 										'ref_date':ref_date,
# 										'receipt_date':receipt_date if receipt_date else '',
# 										'receipt_id':line.id,
# 										'new_sec':True
# 										})

# 							if not security_id and res.account_select_boolean==False:####changes for receipt from sales 
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 							if not security_id :####changes for receipt from sales   
# 								if line.debit_amount > 0.0 or line.credit_amount > 0.0:
# 									raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 							elif security_id:
# 								if line.debit_amount:
# 									if  round(ref_amount_security,2) != round(line.debit_amount,2):
# 										raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
# 								if line.credit_amount:
# 									if  round(ref_amount_security,2) != round(line.credit_amount,2):
# 										raise osv.except_osv(('Alert'),('credit amount should be equal.'))


# 					if acc_selection == 'sundry_deposit':
# 						for sun_dep_line in line.sundry_deposit_one2many:
# 							if sun_dep_line.sundry_check == True:
# 								flag_sundry_deposit = True
# 								sundry_id = sun_dep_line.sundry_id.id
# 								pay_amount +=  sun_dep_line.payment_amount
# 								self.pool.get('sundry.deposit').write(cr,uid,sun_dep_line.id,{'sundry_check_process':True})

# 							if not sundry_id:
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 							if line.debit_amount:
# 								if  round(pay_amount,2) != round(line.debit_amount,2):
# 									raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
# 							if line.credit_amount:
# 								if  round(pay_amount,2) != round(line.credit_amount,2):
# 									raise osv.except_osv(('Alert'),('Credit amount should be equal.'))
															
# 					if acc_selection == 'others':
# 						for cofb_line in line.cofb_one2many:
# 							cofb_id = cofb_line.cofb_id.id
# 							ref_amount_cofb = ref_amount_cofb + cofb_line.ref_amount
# 						if not cofb_id:
# 							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 						elif cofb_id:
# 							 if line.debit_amount:
# 								if round(ref_amount_cofb,2)  != round(line.debit_amount,2):
# 									   raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
# 							 if line.credit_amount:
# 								if round(ref_amount_cofb,2)  != round(line.credit_amount,2):
# 									   raise osv.except_osv(('Alert'),('credit amount should be equal.'))
									   
# 					if line.acc_status == 'others' and acc_selection == 'against_ref':
# 						cfob_id = ''
# 						if line.receipt_id.receipt_type1 == 'cfob':
# 							for cfob_other_line in line.sales_other_cfob_one2many:
# 								cfob_sync_flag = True
# 								cfob_other_id = cfob_other_line.cfob_other_id.id
# 								ref_amount_cfob_other = ref_amount_cfob_other + cfob_other_line.ref_amount
# 								cfob_id = cfob_other_line.id
# 								self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_other_line.id,{'check_cfob_sales_process':True})
# 							if line.invoice_cfob_one2many:
# 								for invoice_cfob_line in line.invoice_cfob_one2many:
# 									if invoice_cfob_line.cfob_chk_invoice:
# 										ref_amount_cfob_other = ref_amount_cfob_other + invoice_cfob_line.pending_amount #grand_total 
# 										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_cfob_line.id,{
# 											'cfob_chk_invoice_process':True,
# 											'status':'paid',
# 											'invoice_paid_date':datetime.now().date(),
# 											'pending_status':'paid'})

# ####### history maintained for cfob other (mix entry) 8 sept 15  ######
# 										self.pool.get('invoice.receipt.history').create(cr,uid,{
# 											'invoice_receipt_history_id':invoice_cfob_line.id,
# 											'invoice_number':invoice_cfob_line.invoice_number,
# 											'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 											'receipt_id_history':line.id,
# 											'invoice_pending_amount':0.0,
# 											'invoice_paid_amount':invoice_cfob_line.pending_amount,
# 											'invoice_date':invoice_cfob_line.invoice_date,
# 											'service_classification':invoice_cfob_line.service_classification,
# 											'tax_rate':invoice_cfob_line.tax_rate,
# 											'cse':invoice_cfob_line.cse.id,
# 											'check_invoice':True})

# ####### history maintained for cfob other (mix entry) 8 sept 15  ######
# 							if not cfob_other_id:
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name)) 
# 							elif cfob_other_id:
# 								if line.debit_amount:
# 									if round(ref_amount_cfob_other,2) != round(line.debit_amount,2):
# 											raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
# 								if line.credit_amount:
# 									if round(ref_amount_cfob_other,2) != round(line.credit_amount,2):
# 										raise osv.except_osv(('Alert'),('credit amount should be equal.'))              

# 					if acc_selection == 'against_ref' and line.acc_status == 'against_ref':
# 						pending_amt = credit_amount_srch_amount = 0.0 # Debit note amount added  18feb16
# 						# if res.payment_status == False:
# 						# 	raise osv.except_osv(('Alert'),('Select Payment Status.'))              
# 						for i in line.debit_note_one2many:
# 							if i.check_debit == True:
# 								flag = True
# 								sales_debit_id = i.sales_debit_id.id
# 								credit_amount_srch_amount = i.credit_amount_srch # Debit note amount added  18feb16
# 						count = 0
# 						for invoice_line in line.invoice_adhoc_one2many:
# 							invoice_id_receipt =  invoice_line.invoice_id_receipt.id
# 							if invoice_line.check_invoice == True:
# 								flag = True
# 								count +=  1
# 								grand_total_against += invoice_line.pending_amount##s
# 								# if res.payment_status == 'short_payment' or res.payment_status == 'full_payment':
# 								if res.payment_status in  ('short_payment','full_payment'):
# 									grand_total_against_new += invoice_line.pending_amount

# 								if res.payment_status == 'partial_payment':
# 									grand_total_against_new += invoice_line.partial_payment_amount
					
# 								if res.payment_status == 'partial_payment' and invoice_line.partial_payment_amount == 0.0:
# 									raise osv.except_osv(('Alert'),('partial amount cannot be zero.'))
								
# 						grand_total_against_new += credit_amount_srch_amount if credit_amount_srch_amount else 0.0  # 4may Debit note 
# 						credit_amount = line.credit_amount
# 						for invoice_line in line.invoice_adhoc_one2many:
# 							invoice_id_receipt =  invoice_line.invoice_id_receipt.id
# 							if res.payment_status == 'short_payment' and invoice_line.check_invoice == True:
# 								if grand_total_against_new < credit_amount :
# 									raise osv.except_osv(('Alert'),('credit amount should be less than invoice amount.')) #11 may 15

# 								if grand_total_against > credit_amount:####21Apr short payment
# 									if count > 1:
# 										count -= 1
# 										pending_amt = grand_total_against - credit_amount
# 										grand_total_against = grand_total_against - invoice_line.pending_amount 
# 										credit_amount -= invoice_line.pending_amount 

# 										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 											'pending_amount':0.0,
# 											'pending_status':'paid',
# 											'status':'paid'})
# 										self.pool.get('invoice.receipt.history').create(cr,uid,{
# 											'invoice_receipt_history_id':invoice_line.id,
# 											'invoice_number':invoice_line.invoice_number,
# 											'invoice_pending_amount':0.0,
# 											'invoice_paid_amount':invoice_line.pending_amount,
# 											'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 											'receipt_id_history':line.id,
# 											'invoice_date':invoice_line.invoice_date,
# 											'service_classification':invoice_line.service_classification,
# 											'tax_rate':invoice_line.tax_rate,
# 											'cse':invoice_line.cse.id,
# 											'check_invoice':True})######## For Payment history

# 									else:    
# 										pending_amt = grand_total_against - credit_amount
# 										#credit_amount = credit_amount - invoice_line.pending_amount 
										
# 										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 											'pending_amount':pending_amt,
# 											'pending_status':'pending',
# 											'status':'paid'})
# 										self.pool.get('invoice.receipt.history').create(cr,uid,{
# 											'invoice_receipt_history_id':invoice_line.id,
# 											'invoice_number':invoice_line.invoice_number,
# 											'invoice_pending_amount':pending_amt,
# 											'invoice_paid_amount':credit_amount,
# 											'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 											'receipt_id_history':line.id,
# 											'invoice_date':invoice_line.invoice_date,
# 											'service_classification':invoice_line.service_classification,
# 											'tax_rate':invoice_line.tax_rate,
# 											'cse':invoice_line.cse.id,
# 											'check_invoice':True})######## For Payment history

													   
# 								elif grand_total_against == line.credit_amount:
# 									self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 										'check_process_invoice':True,
# 										'pending_amount':pending_amt,
# 										'pending_status':'paid',
# 										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date()})

# 									self.pool.get('invoice.receipt.history').create(cr,uid,{
# 										'invoice_receipt_history_id':invoice_line.id,
# 										'invoice_number':invoice_line.invoice_number,
# 										'invoice_pending_amount':pending_amt,
# 										'invoice_paid_amount':credit_amount,
# 										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 										'receipt_id_history':line.id,
# 										'invoice_date':invoice_line.invoice_date,
# 										'service_classification':invoice_line.service_classification,
# 										'tax_rate':invoice_line.tax_rate,
# 										'cse':invoice_line.cse.id,
# 										'check_invoice':True})######## For Payment history

# 							# elif res.payment_status == 'partial_payment':####Partial payment
# 							# 	if invoice_line.check_invoice == True:
# 							# 		if invoice_line.partial_payment_amount:
# 							# 			if round(grand_total_against_new,2) > round(credit_amount,2)\
# 							# 					or round(grand_total_against_new,2) < round(credit_amount,2):
# 							# 				raise osv.except_osv(('Alert'),('credit amount and invoice partial amount should be equal.'))
# 							# 			if (invoice_line.partial_payment_amount - invoice_line.pending_amount) == 0.0: ## alert for Select Full payment  
# 							# 				raise osv.except_osv(('Alert'),('Please Select Full payment '))

# 							# 			pending_amount = invoice_line.pending_amount - invoice_line.partial_payment_amount
# 							# 			self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 							# 				'pending_amount':pending_amount,
# 							# 				'pending_status':'pending',
# 							# 				'status':invoice_line.status, #'printed',
# 							# 				'partial_payment_amount':00})
# 							# 			self.pool.get('invoice.receipt.history').create(cr,uid,{
# 							# 				'invoice_receipt_history_id':invoice_line.id,
# 							# 				'invoice_number':invoice_line.invoice_number,
# 							# 				'invoice_pending_amount':pending_amount,
# 							# 				'invoice_paid_amount':invoice_line.partial_payment_amount,
# 							# 				'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 							# 				'receipt_id_history':line.id,
# 							# 				'invoice_date':invoice_line.invoice_date,
# 							# 				'service_classification':invoice_line.service_classification,
# 							# 				'tax_rate':invoice_line.tax_rate,
# 							# 				'cse':invoice_line.cse.id,
# 							# 				'check_invoice':True})######## For Payment history

# 							# elif res.payment_status == 'full_payment':
# 							# 	if invoice_line.check_invoice == True:
# 							# 		if round(grand_total_against_new,2) < round(credit_amount,2)\
# 							# 				or round(grand_total_against_new,2) > round(credit_amount,2) :
# 							# 			raise osv.except_osv(('Alert'),('credit amount and invoice amount should be equal.')) #11may15

# 							# 		pending_amt = grand_total_against - credit_amount
# 							# 		self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 							# 		        'check_process_invoice':True,
# 							# 		        'pending_amount':0.0,
# 							# 		        'pending_status':'paid',
# 							# 		        'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 							# 		        'status':'paid'}) 
# 							# 		self.pool.get('invoice.receipt.history').create(cr,uid,{
# 							# 			'invoice_receipt_history_id':invoice_line.id,
# 							# 			'invoice_number':invoice_line.invoice_number,
# 							# 			'invoice_pending_amount':pending_amt,
# 							# 			'invoice_paid_amount':invoice_line.pending_amount,
# 							# 			'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 							# 			'receipt_id_history':line.id,
# 							# 			'invoice_date':invoice_line.invoice_date,
# 							# 			'service_classification':invoice_line.service_classification,
# 							# 			'tax_rate':invoice_line.tax_rate,
# 							# 			'cse':invoice_line.cse.id,
# 							# 			'check_invoice':True})######## For Payment history

# 							if invoice_line.check_invoice == True:
# 								pending_amount = invoice_line.pending_amount - invoice_line.partial_payment_amount
# 								if pending_amount == 0:
# 									check_process_invoice_psd = True
# 									pending_status_psd = 'paid'
# 									status_psd = 'paid'
# 									invoice_paid_date_psd = res.receipt_date if res.receipt_date else datetime.now().date(),
# 								else:
# 									check_process_invoice_psd = False
# 									pending_status_psd = 'pending'
# 									status_psd = invoice_line.status
# 									invoice_paid_date_psd = False
# 								self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
# 										'check_process_invoice': check_process_invoice_psd,
# 										'pending_amount': pending_amount,
# 										'pending_status': pending_status_psd,
# 										'invoice_paid_date':invoice_paid_date_psd,
# 										'status': status_psd}) 
# 								self.pool.get('invoice.receipt.history').create(cr,uid,{
# 									'invoice_receipt_history_id':invoice_line.id,
# 									'invoice_number':invoice_line.invoice_number,
# 									'invoice_pending_amount':pending_amount,
# 									'invoice_paid_amount': invoice_line.partial_payment_amount,
# 									'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
# 									'receipt_id_history':line.id,
# 									'invoice_date':invoice_line.invoice_date,
# 									'service_classification':invoice_line.service_classification,
# 									'tax_rate':invoice_line.tax_rate,
# 									'cse':invoice_line.cse.id,
# 									'check_invoice':True})######## For Payment history

# 							#else:
# 									#raise osv.except_osv(('Alert'),('Credit amount exceed the receipt value')
								
# 						if flag == False:
# 							if not res.is_cfob_customer:
# 								raise osv.except_osv(('Alert'),('No invoice selected.'))

# 						if not invoice_id_receipt and not sales_debit_id:
# 							if not res.is_cfob_customer:
# 								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))


# 					# 50k condition
# 					# if acc_selection == 'cash' and line.debit_amount >= 50000 or line.credit_amount >= 50000:
# 					# 	if line.customer_name.name !='CFOB': # 6 0ct 
# 					# 		if line.customer_name.pan_no == False:
# 					# 			raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))
# 					# 	else: # 6 0ct 
# 					# 		for reco in line.invoice_cfob_one2many:
# 					# 			if reco.partner_id.pan_no == False:
# 					# 				raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))

# 					# if line.acc_status == 'advance' and acc_selection == 'advance' and line.type == 'debit': # As per vijay , 28apr
# 					#   for adv_against_line1 in line.advance_against_ref_one2many:
# 					#       advance_ref_id1 = adv_against_line1.advance_ref_id.id
# 					#       if adv_against_line1.check_advance_against_ref == True:
# 					#           flag_debit = True
# 					#           ref_amount1 = ref_amount1 + adv_against_line1.ref_amount
# 					#           self.pool.get('advance.sales.receipts').write(cr,uid,adv_against_line1.id,{'check_advance_against_ref_process':True})   
# 					# 
# 					#   if flag_debit == False:
# 					#           raise osv.except_osv(('Alert'),('Advance record not selected.'))
# 					#               
# 					#   if not line.advance_against_ref_one2many:
# 					#           raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
# 					#   if advance_ref_id1:
# 					#       if line.debit_amount:
# 					#           if round(ref_amount1,2) != round(line.debit_amount,2):
# 					#               raise osv.except_osv(('Alert'),('Debit amount should be equal'))
# 					#       if line.credit_amount:
# 					#           if round(ref_amount1,2) != round(line.credit_amount,2):
# 					#               raise osv.except_osv(('Alert'),('Credit amount should be equal'))


# 		for rec in self.browse(cr,uid,ids):
# 			cse_name_id=False
# 			receipt_no = temp_count= seq_srch= seq= invoice_num = invoice_date_concate = cse_name = ''
# 			count=seq= grand_total = 0
# 			cse_name_last= cse_name_last_cfob= cfob_invoice= cfob_invoice_date=cfob_cust=''
# 			cfob_invoice_gross=0.0

# 			acc_status = rec.acc_status
# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_form')
# 			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_tree')

# 			seq_srch=self.pool.get('ir.sequence').search(cr,uid,[('code','=','account.sales.receipts')])
# 			if seq_srch:
# 				seq_start=self.pool.get('ir.sequence').browse(cr,uid,seq_srch[0]).number_next
				
# 			ou_code = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
# 			ab_code = self.pool.get('res.users').browse(cr,uid,uid).company_id.sales_receipt_id
			
# 			#year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
# 			month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
# 			today_date = datetime.now().date()
# 			year = today_date.year
# 			year1=today_date.strftime('%y')
# 			if month > 3:
# 				start_year = year
# 				end_year = year+1
# 				year1 = int(year1)+1
# 			else:
# 				start_year = year-1
# 				end_year = year
# 				year1 = int(year1)

# 			financial_start_date = str(start_year)+'-04-01'
# 			financial_end_date = str(end_year)+'-03-31'
			
# 			today_date = datetime.now().date()
# 			year = today_date.strftime('%y')
# 			t1=[]
# 			count=0
# 			if  ou_code and ab_code:        
# 				cr.execute("select cast(count(id) as integer) from account_sales_receipts where state not in ('draft') and receipt_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and import_flag = False"); # excluding imported advance through bills payable import 9 oct 15
# 				temp_count=cr.fetchone()
# 				if temp_count[0]:
# 					count= temp_count[0]
# 				seq=int(count+seq_start)
# 				receipt_no = ou_code+ab_code+str(year1)+str(seq).zfill(6)

# 			if rec.receipt_type1 == 'cfob':
# 				for j in rec.sales_receipts_one2many:
# 					if j.account_id.account_selection=='against_ref':
# 						for k in j.sales_other_cfob_one2many:
# 							if k.customer_cfob not in t1:
# 								t1.extend([k.customer_cfob])
# 				new_cus_name=', '.join(filter(bool,t1))
# 			else:
# 				if line.receipt_id.customer_name:
# 					new_customer_name = line.receipt_id.customer_name.name
# 				elif line.receipt_id.cfob_customer_name:
# 					new_customer_name = line.receipt_id.cfob_customer_name
# 				new_cus_name=new_customer_name
		
# 			self.write(cr,uid,ids,{
# 							'receipt_no':receipt_no,
# 							'receipt_date': receipt_date,
# 							'voucher_type':'Sales Receipt',
# 							'new_cus_name':new_cus_name})
# 			date = receipt_date 

# 			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
# 			for var in self.pool.get('account.period').browse(cr,uid,search_date):
# 				period_id = var.id

# 			srch_jour_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
# 			for jour_acc in self.pool.get('account.journal').browse(cr,uid,srch_jour_acc):
# 				journal_id = jour_acc.id

# 			srch_neft_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','NEFT/RTGS')])
# 			for neft_acc in self.pool.get('account.journal').browse(cr,uid,srch_neft_acc):
# 				neft_id = neft_acc.id

# 			srch_jour_cash = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Cash')])
# 			for jour_cash in self.pool.get('account.journal').browse(cr,uid,srch_jour_cash):
# 				journal_cash = jour_cash.id

# 			move = self.pool.get('account.move').create(cr,uid,{
# 									'journal_id':journal_id,
# 									'state':'posted',
# 									'date':date ,
# 									'name':receipt_no,
# 									'voucher_type':'Sales Receipt',###added for day book
# 									'narration':rec.narration if rec.narration else '',
# 									},context=context)

# 			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
# 				for ln in res.sales_receipts_one2many:
# 					if ln.receipt_id.customer_name:
# 						customer_name = ln.receipt_id.customer_name.name
# 					elif ln.receipt_id.cfob_customer_name:
# 						customer_name = ln.receipt_id.cfob_customer_name
# 					if ln.debit_amount:
# 							self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
# 									'account_id':ln.account_id.id,
# 									'debit':ln.debit_amount,
# 									'name':customer_name or '',
# 									'journal_id':journal_id,
# 									'period_id':period_id,
# 									'date':str(date),
# 									'ref':receipt_no},context=context)
# 					if ln.credit_amount:
# 						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
# 								'account_id':ln.account_id.id,
# 								'credit':ln.credit_amount,
# 								'name':customer_name or '',
# 								'journal_id':journal_id,
# 								'period_id':period_id,
# 								'date':date,
# 								'ref':receipt_no},context=context)

# 			for ln in res.sales_receipts_one2many:
# 				if ln.acc_status == 'against_ref':
# 					invoice_number = ''
# 					if ln.account_id.account_selection == 'against_ref':
# 						for debit_line in ln.debit_note_one2many:
# 							debit_note_no=debit_line.debit_note_no
# 							if debit_line.check_debit == True:
# 								srch_debit=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',debit_note_no)])
# 								for i in self.pool.get('debit.note').browse(cr,uid,srch_debit):
# 									self.pool.get('debit.note').write(cr,uid,i.id,{'state_new':'paid'})

# 						for invoice_line in ln.invoice_adhoc_one2many:
# 							invoice_number = invoice_line.invoice_number
# 							invoice_date = invoice_line.invoice_date
# 							cse_name = emp_code = ''
# 							if invoice_line.check_invoice == True :
# 								date1= datetime.strptime(invoice_line.invoice_date, '%Y-%m-%d').date()
# 								invoice_date= date1.strftime("%d-%m-%Y")
# 								invoice_date_concate = [invoice_date,invoice_date_concate]
# 								invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))
								
# 								invoice_num = [str(invoice_line.invoice_number),invoice_num]
# 								invoice_num = ' / '.join(filter(bool,invoice_num))
							
# 								emp_code = str(invoice_line.cse.emp_code)
# 								main_str = "select name from resource_resource where code ilike '" + "%" + str(emp_code) + "%'"
# 								cr.execute(main_str)
# 								first_name = cr.fetchone()
# 								if first_name:
# 									cse_name = str(first_name[0]) +' '+str(invoice_line.cse.last_name)
									 
# 								grand_total += invoice_line.grand_total_amount
# 								cse_name_id = invoice_line.cse.id
								
# 								srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[('id','>',0),('invoice_number','=',invoice_number)])
# 								for adhoc in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
# 									invoice_paid_date = datetime.now().date()
# 									self.pool.get('invoice.adhoc.master').write(cr,uid,adhoc.id,{'invoice_paid_date':invoice_paid_date,})
# 									invoice_history_srch = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',invoice_number)])
# 									if invoice_history_srch:
# 										for invoice_history in self.pool.get('payment.contract.history').browse(cr,uid,invoice_history_srch):
# 											self.pool.get('payment.contract.history').write(cr,uid,invoice_history.id,{'payment_status':'paid'})

# 			###################################################################### itds 30 sep 2015#########################
# 		invoice_gross_amount=0.0
# 		cfob_invoice_no = cfob_invoice_date = '' # 27apr
		
# 		for res in self.browse(cr,uid,ids):
# 			if res.customer_name:
# 				cust_name = res.customer_name.name
# 				cust_id = res.customer_name.id
# 				ou_id = res.customer_name.ou_id
# 			elif res.cfob_customer_name:
# 				cust_name = res.cfob_customer_name
# 				cust_id = False
# 				ou_id = res.cfob_customer_id
# 			customer_id = cust_id
# 			customer_name = cust_name
# 			cust_ou_id = ou_id
				
# 			for ln_itds in res.sales_receipts_one2many:
# 				if res.receipt_type1 == 'cfob':
# 					for cfob_line in ln_itds.sales_other_cfob_one2many:
# 						customer_cfob = cfob_line.customer_cfob
# 						cust_cfob_id = cfob_line.cust_cfob_id
						
# 						cfob_invoice_no = [str(cfob_line.ref_no),cfob_invoice_no]
# 						cfob_invoice_no = ' / '.join(filter(bool,cfob_invoice_no))
						
# 						cfob_invoice_date = [cfob_line.ref_date,cfob_invoice_date]
# 						cfob_invoice_date = ' / '.join(filter(bool,cfob_invoice_date))
						
# 					for invoice_line_cfob in ln_itds.invoice_cfob_one2many:
							
# 						if invoice_line_cfob.cfob_chk_invoice == True:
# 							customer_id= invoice_line_cfob.partner_id.id
# 							customer_name= invoice_line_cfob.partner_id.name
# 							cust_ou_id = invoice_line_cfob.partner_id.ou_id
							
# 							invoice_num = [str(invoice_line_cfob.invoice_number),invoice_num]
# 							invoice_num = ' / '.join(filter(bool,invoice_num))
							
# 							invoice_date_concate = [invoice_line_cfob.invoice_date,invoice_date_concate]
# 							invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))
								
# 							cfob_invoice_gross=invoice_line_cfob.grand_total_amount
# 							cse_name_id = invoice_line_cfob.cse.id
							
# 				if ln_itds.acc_status == 'against_ref':

# 					if ln_itds.receipt_id.customer_name:
# 						customer_name = ln_itds.receipt_id.customer_name.name
# 					elif ln_itds.receipt_id.cfob_customer_name:
# 						customer_name = ln_itds.receipt_id.cfob_customer_name
# 					if ln_itds.type == 'credit':
# 						invoice_gross_amount+=ln_itds.credit_amount
							
# 					if ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'debit':
# 						self.pool.get('itds.adjustment').create(cr,uid,{
# 								'receipt_no':receipt_no,
# 								'receipt_date':res.receipt_date, #datetime.now().date(),
# 								'gross_amt':invoice_gross_amount, 
# 								'pending_amt':ln_itds.debit_amount,
# 								'itds_amt':ln_itds.debit_amount,
# 								'invoice_no':invoice_num if invoice_num else cfob_invoice_no,
# 								'invoice_date':invoice_date_concate if invoice_date_concate else cfob_invoice_date ,
# 								'customer_name_char':customer_name if customer_name else customer_cfob ,
# 								'customer_name': customer_id if customer_id else res.customer_id.id,
# 								'customer_id': cust_ou_id if cust_ou_id else cust_cfob_id ,
# 								'itds_cse':cse_name_id,
# 							})
# 						self.write(cr,uid,rec.id,{'acc_status_new':res.acc_status})
							
# 						################################# Itds end #################################### 
# 					elif ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'credit':
# 						for lns in ln_itds.revert_itds_one2many:
# 							if lns.check == True:
# 								total_pr = lns.total_revert + lns.partial_revert if lns.partial_revert else lns.pending_amt 
# 								pending_amount=lns.pending_amt - (lns.partial_revert if lns.partial_revert else lns.pending_amt)
# 								self.pool.get('itds.adjustment').write(cr,uid,lns.id,{
# 														'pending_amt':pending_amount,
# 														'state':'partially_reversed' if pending_amount else 'fully_reversed' ,
# 														'total_revert':total_pr,
# 														'partial_revert':0.0})

# 					if ln_itds.account_id.account_selection == 'security_deposit' and ln_itds.type == 'debit':
# 						self.pool.get('security.deposit').create(cr,uid,{
# 										'security_id':ln_itds.id,
# 									'cse':cse_name_id,
# 									'ref_no':res.receipt_no,
# 									'ref_date':res.receipt_date,
# 									'ref_amount':ln_itds.debit_amount,
# 									'pending_amount':ln_itds.debit_amount,
# 								'security_check_against':True,
# 								'customer_name':customer_id if customer_id else res.customer_id.id,
# 								'acc_status_new':line.acc_status,
# 								'customer_name_char':customer_name if customer_name else customer_cfob,
# 								})
# 				self.pool.get('account.sales.receipts.line').write(cr,uid,ln_itds.id,{'state':'done'})

# 			self.write(cr,uid,rec.id,{'state':'done','acc_status':''})
			
# 			# for state_line in rec.sales_receipts_one2many:
# 			#   self.pool.get('account.sales.receipts.line').write(cr,uid,state_line.id,{'state':'done'})

# 			for settlement in self.browse(cr,uid,ids):
# 				for set_line in settlement.sales_receipts_one2many:
# 					if set_line.account_id.account_selection == 'advance' and set_line.acc_status == 'advance' and set_line.type == 'credit':
# 						self.write(cr,uid,settlement.id,{
# 							'check_settlement':True,
# 							'advance_pending':set_line.credit_amount,
# 							'new_ad':True,
# 							})
# 						for advance in set_line.advance_one2many:
# 														self.pool.get('advance.sales.receipts').write(cr,uid,advance.id,{
# 																				'receipt_no':settlement.receipt_no,
# 													'receipt_date':settlement.receipt_date,})
									
# 				#self.sync_invoice_paid_state(cr,uid,ids,context=context)
# 				self.delete_draft_records_sales(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
# 				#####################################abhi itds importtant commneted##############

# 		for rec_log in self.browse(cr,uid,ids):
# 			if rec_log.customer_name:
# 				customer_name = rec_log.customer_name.name
# 				cust_id = rec_log.customer_name.id
# 			elif rec_log.cfob_customer_name:
# 				customer_name = rec_log.cfob_customer_name
# 				cust_id = False
# 			customer_invoice_paid = date1=''
# 			date1=str(datetime.now().date())

# 			conv=time.strptime(str(date1),"%Y-%m-%d")
# 			date1 = time.strftime("%d-%m-%Y",conv)
# 			if rec_log.customer_name:
# 				customer_invoice_paid= customer_name+'   Customer Invoice   Paid  On    '+date1
# 				customer_invoicepaid_date=self.pool.get('customer.logs').create(cr,uid,{
# 									'customer_join':customer_invoice_paid,
# 									'customer_id':cust_id})

# 		is_cfob_customer = False
# 		cfob_customer_name = False
# 		cust_name = False
# 		for receipt_his in self.browse(cr,uid,ids):
# 			receipt_no=receipt_his.receipt_no
# 			cust_name=receipt_his.customer_name.name
# 			amount = 0.0
# 			is_cfob_customer = receipt_his.is_cfob_customer
# 			cfob_customer_name = receipt_his.cfob_customer_name
# 			if receipt_his.receipt_date:
# 				receipt_date=receipt_his.receipt_date
# 			else:
# 				receipt_date=datetime.now().date()
# 			receipt_type=receipt_his.receipt_type
# 			for receipt_line in receipt_his.sales_receipts_one2many:
# 				amount += receipt_line.debit_amount

# 			self.pool.get('receipt.history').create(cr,uid,{
# 						'receipt_his_many2one':receipt_his.customer_name.id,
# 						'receipt_number':receipt_no,
# 						'reciept_date':receipt_date,
# 						'reciept_type':receipt_type,
# 						'reciept_amount':amount})
						
# 		self.sales_receipt_account_account(cr,uid,ids)
# 		self.sync_receipt_history(cr,uid,ids)
# 		if cfob_sync_flag:             #SYNC CODE IS NOT READY to UNCOMMENT
# 				self.sync_CFOB_customer_entry(cr,uid,ids,context=context)
# 		if is_cfob_customer == True and cfob_customer_name:
# 			text_customer_name = cfob_customer_name
# 		else:
# 			text_customer_name = cust_name
# 		self.write(cr, uid, ids[0], {'text_customer_name':text_customer_name}, context=context)
# 		return  {
# 				'name':'Sales Receipt',
# 				'view_mode': 'form',
# 				'view_id': False,
# 				'view_type': 'form',
# 				'res_model': 'account.sales.receipts',
# 				'res_id':rec.id,
# 				'type': 'ir.actions.act_window',
# 				'target': 'current',
# 				'domain': '[]',
# 				'context': context,
# 				}

	def psd_onchange_account_type(self, cr, uid, ids, account_id,account_select_boolean, context=None):
		v = {}
		if account_id:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in ('cash','iob_one'):
						v['type'] = 'debit'
					elif acc.account_selection == 'iob_two':
						v['type'] = 'credit'
					elif acc.account_selection == 'itds':
						v['type'] = 'debit'
					elif acc.account_selection == 'against_ref':
						v['type'] = 'credit'
					else:
						v['type'] = ''
		return {'value':v}

	def add_info_psd(self, cr, uid, ids, context=None): # Add button on sales receipt form
		line_id =  0
		auto_debit_total=auto_credit_total=auto_credit_cal=auto_debit_cal=itds_total = 0.0
		for res in self.browse(cr,uid,ids):
			account_id = False
			#if res.account_select_boolean == False:
			account_id = res.account_id.id
			types = res.type
			acc_status = res.acc_status
			acc_selection = res.account_id.account_selection
			acc_name = res.account_id.name
			
			if acc_selection == 'advance':
				if acc_status != 'advance':  
					raise osv.except_osv(('Alert!'),('Select proper status against advance!'))
				
				if types == 'debit':
					raise osv.except_osv(('Alert!'),('Account Type of Advance should be Credit'))

				self.check_tax_rate(cr, uid, account_id)

			if acc_selection =='itds_receipt'  and acc_status != 'against_ref' :
				raise osv.except_osv(('Alert!'),('Account status should be Against Reference')) 
			# if acc_selection == 'itds':
			# 	raise osv.except_osv(('Alert!'),('Select proper account')) 

			# if res.account_id.account_selection == 'itds_receipt' and types == 'credit' and res.payment_status in ('short_payment','partial_payment'):
			# 	raise osv.except_osv(('Alert!'),('Short / Partial payment is not allowed \n \n Kindly Select Full payment'))

			account_id1=res.account_id
			account_selection=res.account_id.account_selection
			for i in res.sales_receipts_one2many:
				if account_id1.id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
				# if account_selection==i.account_id.account_selection:
				# 	raise osv.except_osv(('Alert!'),('Can not select same account.'))

			if not account_id:
				raise osv.except_osv(('Alert'),('Please select Account Name.'))

			if not types:
				raise osv.except_osv(('Alert'),('Please select Type.'))

			if not acc_status:
				raise osv.except_osv(('Alert'),('Please select Status.'))
			
			if res.account_id.account_selection=='itds' and res.type=='credit':
				raise osv.except_osv(('Alert'),('For ITDS account, type should always be debit.'))

			if res.account_id.account_selection in ('cash','iob_one') and  res.type=='credit':
				raise osv.except_osv(('Alert'),('Cash / Bank A/c cannot be credited'))		

			for line in res.sales_receipts_one2many:
				account = line.account_id
				line_id = line.id
						
			if acc_status and res.account_select_boolean == False:
				if acc_selection == 'iob_two':
					raise osv.except_osv(('Alert'),('Please select proper account name.'))
				if acc_status == 'against_ref': 	
			                if acc_selection == 'against_ref':

			                        srch1 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
										('status','in',('open','printed')),
										('invoice_number','!=',''),
										('check_process_invoice','=',False),
										('partner_id','=',res.customer_name.id)]) #MHM 10dec
					        for advance in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch1):
					                if advance.check_process_invoice == False:
                                                                self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'check_invoice':False})
						srch_debit=self.pool.get('debit.note').search(cr,uid,[('customer_name','=',res.customer_name.id),('state_new','=','open')])
						for x in self.pool.get('debit.note').browse(cr,uid,srch_debit):
								self.pool.get('debit.note').write(cr,uid,x.id,{'check_debit':False})

                                '''if acc_status == 'advance_against_ref':
                                                              
                                        if acc_selection == 'advance':

			                        srch2 = self.pool.get('advance.sales.receipts').search(cr,uid,[('check_advance_against_ref_process','=',False)])
			                        for against in self.pool.get('advance.sales.receipts').browse(cr,uid,srch2):
			                                if against.check_advance_against_ref_process == False:
			                                        self.pool.get('advance.sales.receipts').write(cr,uid,against.id,{'check_advance_against_ref':False})
                                        if acc_selection == 'against_ref':

			                        srch3 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
										('check_advance_ref_invoice_process','=',False),
										('partner_id','=',res.customer_name.id)]) #MHM 10dec
			                        for against1 in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch3):
			                                if against1.check_advance_ref_invoice_process == False:
			                                        self.pool.get('invoice.adhoc.master').write(cr,uid,against1.id,{
														'check_advance_ref_invoice':False,
														'invoice_id_receipt_advance':line_id}) '''
			                                        
			        if acc_status == 'new_reference':  
                                        if acc_selection == 'security_deposit':
                                                search_new = self.pool.get('security.deposit').search(cr,uid,[('security_check_process','=',False)])
                                                for new_line in self.pool.get('security.deposit').browse(cr,uid,search_new):
                                                        if new_line.security_check_process == False:
                                                                self.pool.get('security.deposit').write(cr,uid,new_line.id,{'security_check_new_ref':False})                                  

				if acc_selection == 'itds_receipt' and types == 'debit':
			                if res.account_id.itds_rate:
			                        itds_rate = res.account_id.itds_rate
			                        itds_rate_per = itds_rate * 0.01
			                        for line in res.sales_receipts_one2many:
			                                if line.account_id.account_selection == 'against_ref':        
					                        grand_total = line.credit_amount
					                        itds_total = grand_total * itds_rate_per
			                else:
			                        raise osv.except_osv(('Alert'),('Please give Itds Rate'))
			                        		                        
	                     
			        if res.account_id.account_selection in ( 'iob_two','iob_one' ,'cash'):
					if res.type=='debit':
						for j in res.sales_receipts_one2many:
							if j.type=='credit':
								auto_debit_total += j.credit_amount
							if j.type=='debit':
								auto_credit_total += j.debit_amount
						if auto_debit_total > auto_credit_total:
							auto_debit_total -= auto_credit_total
						else:		
							auto_debit_total=0.0
					else:	
						for k in res.sales_receipts_one2many:
							if k.type=='credit':
								auto_debit_cal += k.credit_amount
							if k.type=='debit':
								auto_credit_cal += k.debit_amount
						if auto_debit_cal<auto_credit_cal:
							auto_credit_cal -= auto_debit_cal
						else:
							auto_credit_cal=0.0
			                                
				self.pool.get('account.sales.receipts.line').create(cr,uid,{
										'receipt_id':res.id,
										'account_id':account_id,
										'acc_status':acc_status,
										'type':types,
										'debit_amount':round(itds_total) if itds_total else auto_debit_total,
										'credit_amount':auto_credit_cal,
										'customer_name':res.customer_name.id if res.customer_name else '',
										})
			
			
			if acc_status and res.account_select_boolean == True:### from receipt button (direct receipt from sales)
				credit_value = debit_value = remaining_value = 0.0

				auto_debit_total=auto_credit_total=auto_credit_cal=auto_debit_cal=0.0
				if acc_selection == 'iob_two':
					raise osv.except_osv(('Alert'),('Please select proper account name.'))
				if acc_status == 'against_ref': 	
			                for line in res.sales_receipts_one2many:
			                        if line.account_id.account_selection == 'against_ref':
                                                        credit_value = line.credit_amount
			                                srch1 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
												('status','in',('open','printed')),
												('invoice_number','!=',''),
												('check_process_invoice','=',False),
												('partner_id','=',res.customer_name.id)]) #MHM 10dec
					                #for advance in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch1):
					                        #if advance.check_process_invoice == False:
                                                                        #self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'check_invoice':False})
                                                if line.account_id.account_selection == 'itds_receipt':
			                                debit_value +=  line.debit_amount
			                                
                                                if line.account_id.account_selection == 'security_deposit':
			                                debit_value +=  line.debit_amount
			                                			                        
			                
			                remaining_value = credit_value - debit_value       
			              
			        if  res.account_id.account_selection in ('iob_one','cash'):
					if res.type=='debit':
						for j in res.sales_receipts_one2many:
							if j.type=='credit':
								auto_debit_total += j.credit_amount
							if j.type=='debit':
								auto_credit_total += j.debit_amount
						if auto_debit_total > auto_credit_total:
							auto_debit_total -= auto_credit_total
						else:
							auto_debit_total=0.0
					else:	
						for k in res.sales_receipts_one2many:
							if k.type=='credit':
								auto_debit_cal += k.credit_amount
							if k.type=='debit':
								auto_credit_cal += k.debit_amount
						if auto_debit_cal < auto_credit_cal:
							auto_credit_cal -= auto_debit_cal
						else:
							auto_credit_cal=0.0
				self.pool.get('account.sales.receipts.line').create(cr,uid,{
										'receipt_id':res.id,
										'account_id':account_id,
										'acc_status':acc_status,
										'type':types,
										'debit_amount':remaining_value if remaining_value else auto_debit_total,
										'credit_amount':auto_credit_cal,
										'customer_name':res.customer_name.id if res.customer_name else '',
										})

			self.write(cr,uid,res.id,{'account_id':None,'type':''})
		return True

class account_sales_receipts_line(osv.osv):
	_inherit = 'account.sales.receipts.line'

	_columns = {
		'is_transfered': fields.boolean(string = "Is Transfered"),
	}

	def psd_add(self, cr, uid, ids, context=None): # Sales receipt line  add button 
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
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			acc_id = res.account_id
			acc_selection = acc_id.account_selection
			customer_name = res.customer_name.name
			view_name = name_wizard = ''
			acc_selection_list = ['itds_receipt','against_ref','iob_one','security_deposit',
								  'cash','advance','others' ,'sundry_deposit' ]
			if not acc_id.name:
				raise osv.except_osv(('Alert'),('Please Select Account.'))
			if acc_selection in acc_selection_list:
				if  acc_selection == 'itds_receipt':
					if res.type == 'credit':
						self.show_itds_details(cr,uid,ids,context=context)
						view_name = 'psd_itds_revert_against_ref_form'
						name_wizard = "ITDS Details"
					else:
						raise osv.except_osv(('Alert'),('No Information'))
				elif res.acc_status == 'others' and acc_selection == 'against_ref' and res.receipt_id.receipt_type1 == 'cfob':
					view_name = 'psd_account_cofb_other_form_id'
					name_wizard= "CFOB Details."
				elif acc_selection == 'iob_one':
					view_name = 'psd_account_iob_one_form'
					name_wizard= "Add"+" "+acc_id.name+" "+"Details"
				elif acc_selection == 'security_deposit' and res.acc_status !='new_reference' and res.type == 'debit' and res.state=='done' :
					view_name =  'psd_account_security_deposit_form'
					name_wizard = "Security Deposit Details (Against Reference)"
				elif acc_selection == 'security_deposit' and res.acc_status =='new_reference' and res.type == 'credit':
					self.show_sec_deposit(cr,uid,ids,context=context)
					view_name = 'psd_account_security_deposit_form_new_reference'
					name_wizard = "Security Deposit Details (New Reference)"
				elif acc_selection == 'cash':
					raise osv.except_osv(('Alert'),('No Information'))
				elif acc_selection == 'advance' and res.type == 'credit':
					view_name =  'psd_account_advance_payment_form'
					name_wizard = "Advance Amount Details"
				elif acc_selection == 'others':
					view_name = 'psd_account_cofb_form'
					name_wizard = "Collected on Behalf of Other Branch (CFOB) Details"
				elif acc_selection == 'against_ref' and customer_name not in ('CFOB','CBOB'):
					self.show_details(cr,uid,ids,context=context)
					view_name ='psd_account_against_ref_form'
					name_wizard = "Outstanding Invoice"
				elif acc_selection == 'sundry_deposit' :
					self.sundry_deposit_details(cr,uid,ids,context=context)
					view_name = 'psd_account_sundry_deposit_id'
					name_wizard = "Add Sundry Deposit Details"
			        if view_name:
				        models_data=self.pool.get('ir.model.data')
				        form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name)
				        return {
					        'name': (name_wizard),'domain': '[]',
					        'type': 'ir.actions.act_window',
					        'view_id': False,
					        'view_type': 'form',
					        'view_mode': 'form',
					        'res_model': 'account.sales.receipts.line',
					        'target' : 'new',
					        'res_id':int(res_id),
					        'views': [(form_view and form_view[1] or False, 'form'),
							           (False, 'calendar'), (False, 'graph')],
					        'domain': '[]',
					        'nodestroy': True
				        }
			else:
				raise osv.except_osv(('Alert'),('No Information'))
		return True

	def save_against_ref_psd(self, cr, uid, ids, context=None):  #PENDING (CHECK AMOUNT PART)
		flag = False
		total = 0.0
		count = 0
		payment_status = '' 
		sales_receipt_obj = self.pool.get('account.sales.receipts')
		for res in self.browse(cr,uid,ids):
			payment_status  = res.receipt_id.payment_status
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			for line in res.invoice_adhoc_one2many:
				check_invoice = line.check_invoice
				pending_amount = line.pending_amount
				receipt_amount = line.partial_payment_amount
				if check_invoice == True:
					if line.service_classification and line.tax_rate:
						if line.service_classification != 'exempted' and line.tax_rate not in res.account_id.name :
							if 'NT' in line.invoice_number:
								if 'Non' not in res.account_id.name :
									raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
							else:
								raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
					flag = True
					if line.partial_payment_amount > line.pending_amount:
						raise osv.except_osv(('Alert'),('Receipt amount cannot be exceeded by pending amount!'))
					if line.partial_payment_amount == 0.0:
						raise osv.except_osv(('Alert'),('Please enter some amount for receipt amount!'))
			for line2 in res.debit_note_one2many:
				check_debit=line2.check_debit	
				grand_total = line2.credit_amount_srch
				if check_debit == True:
					flag = True
					total += grand_total
			if res.type=='debit':
				self.write(cr,uid,res.id,{'debit_amount':total})
			else:
				self.write(cr,uid,res.id,{'credit_amount':receipt_amount})
		if flag == False:
			raise osv.except_osv(('Alert'),('No invoice selected.'))	
		return {'type': 'ir.actions.act_window_close'}


	def save_iob_one_psd(self, cr, uid, ids, context=None):
		print context.get('active_id'),'lllll'
		id_s = context.get('active_id')
		cheque_obj = self.pool.get('iob.one.sales.receipts')
		neft_obj = self.pool.get('neft.sales.receipts')
		dd_obj = self.pool.get('demand.draft.sales.receipts')
		sales_receipt_obj = self.pool.get('account.sales.receipts')
		narration = ''
		customer_name = ''
		iob_total = neft_total = dd_total = substract = total=0.0
		for rec in self.browse(cr,uid,ids):
			if rec.receipt_id.customer_name:
				customer_name = rec.receipt_id.customer_name.name
			if rec.iob_one_one2many:
				for iob_line in rec.iob_one_one2many:
					total += iob_line.cheque_amount
					if not iob_line.cheque_amount:
						raise osv.except_osv(('Alert'),('Please provide Cheque Amount.'))
					if not iob_line.cheque_date:
						raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
					if not iob_line.cheque_no:
						raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
					if not iob_line.drawee_bank_name:
						raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
					if not iob_line.bank_branch_name:
						raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
					if not iob_line.selection_cts:
						raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))
					if iob_line.cheque_no: 
						for n in str(iob_line.cheque_no):
							p = re.compile('([0-9]{6}$)')
							if p.match(iob_line.cheque_no)== None :
								self.pool.get('iob.one.sales.receipts').create(cr,uid,{'cheque_no':''})
								raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
			elif rec.neft_one2many:
				for neft_line in rec.neft_one2many:
					total += neft_line.neft_amount
					if not neft_line.neft_amount:
						raise osv.except_osv(('Alert!'),('Please provide neft amount.'))
					if not neft_line.beneficiary_bank_name:
						raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
					if not neft_line.pay_ref_no:
						raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
					if not neft_line.neft_amount:
						raise osv.except_osv(('Alert!'),('Please provide Amount.'))
			elif rec.demand_draft_one_one2many:
				for dd_line in rec.demand_draft_one_one2many:
					total += dd_line.dd_amount
					if not dd_line.demand_draft_drawee_bank_name:
						raise osv.except_osv(('Alert!'),('Please provide Demand Draft Drawee Name.'))
					if not dd_line.dd_bank_branch_name:
						raise osv.except_osv(('Alert!'),('Please provide DD Bank Branch Name.'))
					if not dd_line.dd_amount:
						raise osv.except_osv(('Alert!'),('Please provide Amount.'))
					if not dd_line.selection_cts:
						raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))
					if not dd_line.dd_date:
						raise osv.except_osv(('Alert'),('Please provide Demand Draft Date.'))
					if not dd_line.dd_no:
						raise osv.except_osv(('Alert'),('Please provide Demand Draft Number.'))
					if dd_line.dd_no: 
						for n in str(dd_line.dd_no):
							p = re.compile('([0-9]{6,9}$)')
							if p.match(dd_line.dd_no)== None :
								self.pool.get('demand.draft.sales.receipts').create(cr,uid,{'dd_no':''})
								raise osv.except_osv(('Alert!'),('Please Enter 6 to 9 digit Demand draft Number.'))
			else :
				raise osv.except_osv(('Alert'),('No line to process.'))
			if rec.type=='debit':
					self.write(cr,uid,rec.id,{'debit_amount':total})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':total})
		if rec.payment_method == 'cheque' and rec.iob_one_one2many[0]:
			cheque_data = cheque_obj.browse(cr, uid, rec.iob_one_one2many[0].id)
			cheque_no = cheque_data.cheque_no
			cheque_amount = cheque_data.cheque_amount
			drawee_bank_name = cheque_data.drawee_bank_name.name
			narration = 'Cheque Number: '+str(cheque_no)+','+' Cheque Amount: '+str(cheque_amount)+','+' Drawee Bank Name: '+drawee_bank_name
		
		if rec.payment_method == 'neft':
			neft_data = neft_obj.browse(cr, uid, rec.neft_one2many[0].id)
			beneficiary_bank_name = neft_data.beneficiary_bank_name
			branch_name = neft_data.branch_name
			pay_ref_no = neft_data.pay_ref_no
			neft_amount = neft_data.neft_amount
			narration = 'Beneficiary Bank Name: '+beneficiary_bank_name+','+' Branch Name: '+str(branch_name)+','+' Payment Reference Number:'+str(pay_ref_no)+' Neft Amount: '+str(neft_amount)

		if rec.payment_method == 'Dd' and rec.demand_draft_one_one2many[0]:
			dd_data = dd_obj.browse(cr, uid, rec.demand_draft_one_one2many[0].id)
			dd_no = dd_data.dd_no
			dd_amount = dd_data.dd_amount
			drawee_bank_name = dd_data.demand_draft_drawee_bank_name.name
			narration = 'DD Number: '+str(dd_no)+','+' DD Amount: '+str(dd_amount)+','+' Drawee Bank Name: '+drawee_bank_name

		if customer_name:
			narration = narration+','+' Customer Name: ' + customer_name
		res = sales_receipt_obj.write(cr, uid, int(rec.receipt_id.id), {'narration':narration}, context=context)
		# return {'type': 'ir.actions.act_window_close'}
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_sales_receipts_form')
		return {
					'name':'Sales Receipts',
					'view_mode': 'form',
					'view_id': form_view[1],
					'view_type': 'form',
					'res_model': 'account.sales.receipts',
					'res_id': int(rec.receipt_id.id),
					'type': 'ir.actions.act_window',
					'target': 'current',
					'domain': '[]',
					'context': context,
					}	

	def save_against_ref_psd(self, cr, uid, ids, context=None):  #PENDING (CHECK AMOUNT PART)
		flag = False
		total = 0.0
		count = 0
		receipt_amount = 0.0
		payment_status = '' 
		for res in self.browse(cr,uid,ids):
			payment_status  = res.receipt_id.payment_status
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			for line in res.invoice_adhoc_one2many:
				check_invoice = line.check_invoice
				pending_amount = line.pending_amount
				receipt_amount = line.partial_payment_amount
				if check_invoice == True:
					if line.service_classification and line.tax_rate:
						if line.service_classification != 'exempted' and line.tax_rate not in res.account_id.name :
							if 'NT' in line.invoice_number:
								if 'Non' not in res.account_id.name :
									raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
							else :
								raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
					flag = True
					if line.partial_payment_amount > line.pending_amount:
						raise osv.except_osv(('Alert'),('Receipt amount cannot be exceeded by pending amount!'))
					if line.partial_payment_amount == 0.0:
						raise osv.except_osv(('Alert'),('Please enter some amount for receipt amount!'))

			for line2 in res.debit_note_one2many:
				check_debit=line2.check_debit	
				grand_total = line2.credit_amount_srch
				if check_debit == True:
					flag = True
					total += grand_total
			if res.type=='debit':
				self.write(cr,uid,res.id,{'debit_amount':total})
			else:
				self.write(cr,uid,res.id,{'credit_amount':receipt_amount})
				
		if flag == False:
			raise osv.except_osv(('Alert'),('No invoice selected.'))

		return {'type': 'ir.actions.act_window_close'}

	def save_other_cofb_psd(self, cr, uid, ids, context=None):
		total = 0.0
		cust_id=''
		comp_name = self.pool.get('res.users').browse(cr,uid,uid).company_id.name
		for rec in self.browse(cr,uid,ids):
			if rec.sales_other_cfob_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process.'))

			for line in rec.sales_other_cfob_one2many:
			        if not line.branch_name:
					raise osv.except_osv(('Alert'),('Branch name not selected'))
					
				cofb_branch_name = line.branch_name.name 
				branch_ids=self.pool.get('res.company').search(cr,uid,[('name','=',cofb_branch_name)])
					
				if len(branch_ids) !=1:
					raise osv.except_osv(('Alert'),('Branch '+str(cofb_branch_name)+' Not found in res company.'))     
				if cofb_branch_name == comp_name:
					raise osv.except_osv(('Alert'),('CFOB entry of same branch cannot be created.'))
					
				total += line.ref_amount

			for line in rec.invoice_cfob_one2many:
				if line.cfob_chk_invoice:
					# if line.tax_rate not in rec.account_id.name :
					# 		raise osv.except_osv(('Alert'),('Please select proper tax_rate invoice of current branch'))
					if 'Non' in rec.account_id.name: 
						if 'NT' not in line.invoice_number:
							raise osv.except_osv(('Alert'),('Please Select NON TAXABLE invoice'))
					
					total +=  line.pending_amount

			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':total})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':total})

		return {'type': 'ir.actions.act_window_close'}	

account_sales_receipts_line()		


class account_others_receipts(osv.osv):
	_inherit = 'account.others.receipts'

	_columns = {
		'psd_accounting':fields.boolean('PSD Accounting'),
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(account_others_receipts, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	def psd_account_type(self, cr, uid, ids, account_id, context=None):
		v = {}
		if account_id:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in ('cash','iob_one','iob_two'):
						v['type'] = 'debit'
					elif acc.account_selection == 'against_ref':
						v['type'] = 'credit'
					else:
						v['type'] = ''
		return {'value':v}

	def add_others_info_psd(self, cr, uid, ids, context=None):
		auto_credit_cal=auto_debit_cal=auto_credit_total=auto_debit_total=0.0
		for res in self.browse(cr,uid,ids):
			account_id = res.account_id.id
			types = res.type
			acc_selection = res.account_id.account_selection

			if not account_id:
				raise osv.except_osv(('Alert'),('Please select Account Name.'))

			if not types:
				raise osv.except_osv(('Alert'),('Please select Type.'))

			account_id1=res.account_id#a
			for i in res.others_receipt_one2many:
				if account_id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

			if res.account_id.account_selection in ('cash','iob_one') and  res.type=='credit':
				raise osv.except_osv(('Alert'),('Cash / Bank A/c cannot be credited'))			
				
			if acc_selection=='sundry_deposit': # 21 jan 2016
				srch_sun= self.pool.get('sundry.deposit').search(cr,uid,[('sundry_check_process','=',False),('sundry_other','=',True)])	
				for i in self.pool.get('sundry.deposit').browse(cr,uid,srch_sun):
					self.pool.get('sundry.deposit').write(cr,uid,i.id,{'sundry_other':False})

				if  res.account_id.account_selection in ('iob_one' ,'cash','iob_two'):
					if res.type=='debit':
						for j in res.others_receipt_one2many:
							if j.type=='credit':
								auto_debit_total=auto_debit_total+j.credit_amount
							if j.type=='debit':
								auto_credit_total += j.debit_amount
						if auto_debit_total>auto_credit_total:
							auto_debit_total -= auto_credit_total
						else:		
							auto_debit_total=0.0
					else:	
						for k in res.others_receipt_one2many:
							if k.type=='credit':
								auto_debit_cal=auto_debit_cal+k.credit_amount
							if k.type=='debit':
								auto_credit_cal=auto_credit_cal+k.debit_amount
						if auto_debit_cal<auto_credit_cal:
							auto_credit_cal=auto_credit_cal-auto_debit_cal
						else:
							auto_credit_cal=0.0	

			if types:
				self.pool.get('account.others.receipts.line').create(cr,uid,{
						'other_receipt_id':res.id,
						'account_id':account_id,
						'debit_amount':auto_debit_total,
						'credit_amount':auto_credit_cal,
						'type':types,
				})
			self.write(cr,uid,res.id,{'account_id':res.id,'account_id':None,'type':None})
		return True
		
account_others_receipts()


class account_others_receipts_line(osv.osv):
	_inherit = 'account.others.receipts.line'

	def add_others(self, cr, uid, ids, context=None):
			for res in self.browse(cr,uid,ids):
				res_id = res.id
				credit_amount = res.credit_amount
				debit_amount = res.debit_amount
				acc_id = res.account_id
				acc_selection =  acc_id.account_selection
				acc_selection_list = ['iob_one','iob_two','cash','sundry_deposit',
									  'primary_cost_cse','primary_cost_service','advance']

				if not acc_id.name:
					raise osv.except_osv(('Alert'),('Please Select Account.'))
				view_name = name_wizard =''
				if acc_selection in acc_selection_list:

					if acc_selection == 'iob_one':
						view_name = 'account_iob_one_others_form'
						name_wizard = "Add"+" "+ acc_id.name+ " " +"Details"
						
					elif acc_selection == 'iob_two':
						view_name = 'account_others_iob_two_id'
						name_wizard = "Add"+" "+ acc_id.name+ " " +"Details"
		
					elif acc_selection == 'cash':
						raise osv.except_osv(('Alert'),('No Information'))
		
					elif acc_selection == 'advance':
						view_name = 'account_advance_payment_others_form'
						name_wizard = "Advance Amount Details"
						
					elif acc_selection == 'primary_cost_cse':
						self.write(cr,uid,res_id,{'wizard_id':res_id})
						view_name = 'account_primary_cost_other_form'
						name_wizard = "Add Primary Cost Category Details"
						
					elif acc_selection == 'primary_cost_service':
						view_name = 'account_primary_cost_service_form1'
						name_wizard = "Advance Amount Details"
		
					elif acc_selection == 'sundry_deposit':
						self.show_details(cr,uid,ids,context=context)
						view_name = 'account_others_sundry_deposit_form'
						name_wizard = "Add Sundry Deposit Details"

					if view_name:
						models_data=self.pool.get('ir.model.data')
						form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch',view_name )
						return {
							'name': (name_wizard),'domain': '[]',
							'type': 'ir.actions.act_window',
							'view_id': False,
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'account.others.receipts.line',
							'res_id':int(res_id),
							'target' : 'new',
							'views': [(form_view and form_view[1] or False, 'form'),
								(False, 'calendar'), (False, 'graph')],
							'domain': '[]',
							'nodestroy': True,
						}
				
				else:
					raise osv.except_osv(('Alert'),('No Information'))
			return True

	def psd_add_others(self, cr, uid, ids, context=None):
			for res in self.browse(cr,uid,ids):
				res_id = res.id
				credit_amount = res.credit_amount
				debit_amount = res.debit_amount
				acc_id = res.account_id
				acc_selection =  acc_id.account_selection
				acc_selection_list = ['iob_one','iob_two','cash','sundry_deposit',
									  'primary_cost_cse','primary_cost_service','advance']

				if not acc_id.name:
					raise osv.except_osv(('Alert'),('Please Select Account.'))
				view_name = name_wizard =''
				if acc_selection in acc_selection_list:

					if acc_selection == 'iob_one':
						view_name = 'psd_account_iob_one_others_form'
						name_wizard = "Add"+" "+ acc_id.name+ " " +"Details"
						
					elif acc_selection == 'iob_two':
						view_name = 'psd_account_others_iob_two_id'
						name_wizard = "Add"+" "+ acc_id.name+ " " +"Details"
		
					elif acc_selection == 'cash':
						raise osv.except_osv(('Alert'),('No Information'))
		
					elif acc_selection == 'advance':
						view_name = 'psd_account_advance_payment_others_form'
						name_wizard = "Advance Amount Details"
						
					elif acc_selection == 'primary_cost_cse':
						self.write(cr,uid,res_id,{'wizard_id':res_id})
						view_name = 'psd_account_primary_cost_other_form'
						name_wizard = "Add Primary Cost Category Details"
						
					elif acc_selection == 'primary_cost_service':
						view_name = 'psd_account_primary_cost_service_form1'
						name_wizard = "Advance Amount Details"
		
					elif acc_selection == 'sundry_deposit':
						self.show_details(cr,uid,ids,context=context)
						view_name = 'psd_account_others_sundry_deposit_form'
						name_wizard = "Add Sundry Deposit Details"

					
					if view_name:
						models_data=self.pool.get('ir.model.data')
						form_view=models_data.get_object_reference(cr, uid, 'psd_accounting',view_name )
						return {
							'name': (name_wizard),'domain': '[]',
							'type': 'ir.actions.act_window',
							'view_id': False,
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'account.others.receipts.line',
							'res_id':int(res_id),
							'target' : 'new',
							'views': [(form_view and form_view[1] or False, 'form'),
								(False, 'calendar'), (False, 'graph')],
							'domain': '[]',
							'nodestroy': True,
						}
				else:
					raise osv.except_osv(('Alert'),('No Information'))
			return True

account_others_receipts_line()

class cofb_sales_receipts(osv.osv):
	_inherit = 'cofb.sales.receipts'

	# def _get_tax_rate(self, cr, uid, context=None):
	#  	qry=""" select case when cast(rtrim(split_part(name,' ',6),'%') as varchar )='10.30' then cast(rtrim(split_part(name,' ',6),'%') as varchar) 
	# 	when cast(rtrim(split_part(name,' ',6),'%') as varchar )='10.20' then cast(rtrim(split_part(name,' ',6),'%') as varchar) else 
	# 	case when cast(substr(rtrim(split_part(name,' ',6),'%'),5,1) as varchar )='0' then 
	# 	cast(substr(rtrim(split_part(name,' ',6),'%'),1,4) as varchar ) else cast(rtrim(split_part(name,' ',6),'%') as varchar ) end end as tax from account_account where name ilike '%Sundry Debtors service%' and rtrim(split_part(name,' ',6),'%')<>'' order by tax """
	#  	cr.execute(qry)
	#  	tax_list=list(cr.fetchall())
	#  	tax_list1=[(str(x[0]),"Taxable "+str(x[0])) for x in tax_list]
	#  	tax_list1.extend([('non_taxable','Non-Taxable'),('others','Others')])
	#  	tax_list1.extend([('vat','VAT'),('ct','CT')])
	#  	return tuple(tax_list1)

	# _columns = {
	# 		'tax_rate':fields.selection(_get_tax_rate,'Tax'), 	
	# 	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(cofb_sales_receipts, self).default_get(cr, uid, fields, context=context)
		sales_receipts_obj = self.pool.get('account.sales.receipts')
		if context.has_key('sales_receipt_id'):
			sales_receipt_id = context.get('sales_receipt_id')
			receipt_data = sales_receipts_obj.browse(cr, uid, sales_receipt_id)
			if receipt_data.receipt_type1 == 'cfob' and receipt_data.is_cfob_customer == False and receipt_data.customer_name:
				customer_name = receipt_data.customer_name.name
				customer_id = receipt_data.customer_name.ou_id
			elif receipt_data.receipt_type1 == 'cfob' and receipt_data.is_cfob_customer == True:
				customer_name = receipt_data.cfob_customer_name
				customer_id = receipt_data.cfob_customer_id
			else:
				customer_name = False
				customer_id = False
		else:
			customer_name = False
			customer_id = False
		res.update({'customer_cfob': customer_name,'cust_cfob_id':customer_id})
		return res 	

cofb_sales_receipts()


class iob_one_sales_receipts(osv.osv):
	_inherit = 'iob.one.sales.receipts'

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(iob_one_sales_receipts, self).default_get(cr, uid, fields, context=context)
		res.update({'selection_cts': 'cts'})
		return res 

iob_one_sales_receipts()