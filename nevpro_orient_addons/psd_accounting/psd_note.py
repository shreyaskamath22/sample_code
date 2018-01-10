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


class credit_note_search(osv.osv):
	_inherit = 'credit.note.search'

	# def search(self, cr, uid, ids, context=None):
	# 	for res in self.browse(cr,uid,ids):
	# 		try:
	# 			today_date = datetime.now().date()
	# 			py_date = str(today_date + relativedelta(days=-1))
	# 			cr.execute("delete from credit_note_new where srch_date < %(date)s",{'date':today_date}) 
	# 			cr.execute("delete from credit_note_new where credit_note_search_new_id =%(val)s",{'val':res.id})
	# 			Sql_Str = ''
	# 			list_id = []
	# 			credit_note_no = res.credit_note_no
	# 			customer_name = res.customer_name.id
	# 			date_from = res.from_date
	# 			date_to = res.to_date
	# 			status_selection_new = res.status_selection_new
	# 			state=res.state #adding state filter
	# 			customer_id = res.customer_id

	# 			if credit_note_no:
	# 				Sql_Str = Sql_Str + " and ACS.credit_note_no ilike '" + "%" + str(credit_note_no) + "%'"

	# 			if customer_name:
	# 				Sql_Str = Sql_Str + " and ACS.customer_name = '" + str(customer_name) + "'"

	# 			if date_from:
	# 				Sql_Str =Sql_Str +" and ACS.credit_note_date  >= '" + str(date_from) + "'"

	# 			if status_selection_new:
	# 				Sql_Str = Sql_Str + " and ACC.status_selection = '" + str(status_selection_new) + "'"

	# 			if date_to:
	# 				Sql_Str =Sql_Str +" and ACS.credit_note_date <= '" + str(date_to) + "'"

	# 			if customer_id:
	# 				Sql_Str = Sql_Str + " and ACS.customer_id_invisible ilike '" + "%" + str(customer_id) + "%'"
	# 			if state: 
	# 				Sql_Str =Sql_Str +" and ACS.state = '" + str(state) + "'"

	# 			Sql_Str = Sql_Str +" and ACS.psd_accounting = 'f'"
			
	# 			Main_Str_new = "select distinct on (ACS.id) ACS.credit_note_no,ACS.credit_note_date,ACC.status_selection,ACS.debit_amount_srch,ACS.credit_amount_srch ,"+str(res.id)+" ,'''"+str(today_date)+"''' ,ACS.customer_name  from credit_note_line ACC,credit_note ACS where ACC.credit_id = ACS.id and ACS.credit_note_no is not null" # ACS.status_selection_new,

	# 			Main_Str_new1 = Main_Str_new + Sql_Str

	# 			insert_new=("insert into credit_note_new (credit_note_no,credit_note_date,status_selection_new,debit_amount_srch,credit_amount_srch,credit_note_search_new_id,srch_date,customer_name)("+str(Main_Str_new1)+")")

	# 			cr.execute(insert_new)
	# 		except Exception  as exc:
 #   				cr.rollback()
	# 			if exc.__class__.__name__ == 'TransactionRollbackError':
	# 				pass
	# 			else:
	# 				raise
	# 	return True

	def psd_search(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			try:
				today_date = datetime.now().date()
				py_date = str(today_date + relativedelta(days=-1))
				cr.execute("delete from  credit_note_new where srch_date < %(date)s",{'date':today_date}) 
				cr.execute("delete from credit_note_new where credit_note_search_new_id =%(val)s",{'val':res.id})
				Sql_Str = ''
				list_id = []
				credit_note_no = res.credit_note_no
				customer_name = res.customer_name.id
				date_from = res.from_date
				date_to = res.to_date
				status_selection_new = res.status_selection_new
				state=res.state #adding state filter
				customer_id = res.customer_id

				if credit_note_no:
					Sql_Str = Sql_Str + " and ACS.credit_note_no ilike '" + "%" + str(credit_note_no) + "%'"

				if customer_name:
					Sql_Str = Sql_Str + " and ACS.customer_name = '" + str(customer_name) + "'"

				if date_from:
					Sql_Str =Sql_Str +" and ACS.credit_note_date  >= '" + str(date_from) + "'"

				if status_selection_new:
					Sql_Str = Sql_Str + " and ACC.status_selection = '" + str(status_selection_new) + "'"

				if date_to:
					Sql_Str =Sql_Str +" and ACS.credit_note_date <= '" + str(date_to) + "'"

				if customer_id:
					Sql_Str = Sql_Str + " and ACS.customer_id_invisible ilike '" + "%" + str(customer_id) + "%'"
				if state: 
					Sql_Str =Sql_Str +" and ACS.state = '" + str(state) + "'"

				Sql_Str = Sql_Str +" and ACS.psd_accounting = 't'"
			
				Main_Str_new = "select distinct on (ACS.id) ACS.credit_note_no,ACS.credit_note_date,ACC.status_selection,ACS.debit_amount_srch,ACS.credit_amount_srch ,"+str(res.id)+" ,'''"+str(today_date)+"''' ,ACS.customer_name  from credit_note_line ACC,credit_note ACS where ACC.credit_id = ACS.id and ACS.credit_note_no is not null" # ACS.status_selection_new,

				Main_Str_new1 = Main_Str_new + Sql_Str

				insert_new=("insert into credit_note_new (credit_note_no,credit_note_date,status_selection_new,debit_amount_srch,credit_amount_srch,credit_note_search_new_id,srch_date,customer_name)("+str(Main_Str_new1)+")")

				cr.execute(insert_new)
			except Exception  as exc:
   				cr.rollback()
				if exc.__class__.__name__ == 'TransactionRollbackError':
					pass
				else:
					raise
		return True

	def open_new(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_note_form')
			return {    'name': ("Credit Note Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note',
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
			models_data=self.pool.get('ir.model.data')
			context.update({'psd_accounting':True})
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_note_form')
			return {    'name': ("Credit Note Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note',
					'target' : 'current',
					#'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),(False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					'context': context
					}
credit_note_search()

class credit_note_new(osv.osv):
	_inherit='credit.note.new'

# def show(self, cr, uid, ids, context=None):
#   sssssssssadsfasdfdsd
#   res_id=''
#   res_ids=''
#   for res in self.browse(cr,uid,ids):
#       res_ids = self.pool.get('credit.note').search(cr,uid,[('credit_note_no','=',res.credit_note_no)])
#       if res_ids:
#           res_id=res_ids[0]
#       models_data=self.pool.get('ir.model.data')
#       form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_note_form')
#       return {    'name': ("Credit Note Entry"),
#               'domain': '[]',
#               'type': 'ir.actions.act_window',
#               'view_id': False,
#               'view_type': 'form',
#               'view_mode': 'form',
#               'res_model': 'credit.note',
#               'target' : 'current',
#               'res_id':int(res_id),
#               'views': [(form_view and form_view[1] or False, 'form'),
#                          (False, 'calendar'), (False, 'graph')],
#               'domain': '[]',
#               'nodestroy': True,
#               }

	def show(self, cr, uid, ids, context=None):
		res_id=''
		res_ids=''
		for res in self.browse(cr,uid,ids):
			res_ids = self.pool.get('credit.note').search(cr,uid,[('credit_note_no','=',res.credit_note_no)])
			if res_ids:
				res_id=res_ids[0]
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_note_form')
			return {'name': ("Credit Note Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note',
					'target' : 'current',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					}


	def psd_show(self, cr, uid, ids, context=None):
		res_id=''
		res_ids=''
		for res in self.browse(cr,uid,ids):
			res_ids = self.pool.get('credit.note').search(cr,uid,[('credit_note_no','=',res.credit_note_no)])
			if res_ids:
				res_id=res_ids[0]
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_note_form')
			return {'name': ("Credit Note Entry"),
					'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note',
					'target' : 'current',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					}

	def psd_show_credit_note_new(self,cr,uid,ids,context=None):
		for rec in self.browse(cr, uid, ids):
			res_ids = self.pool.get('credit.note').search(cr,uid,[('credit_note_no','=',rec.credit_note_no)])
			for res in self.pool.get('credit.note').browse(cr, uid, res_ids):
				type_field = res.type if res.type else None
				self.pool.get('credit.note').write(cr,uid,res.id,{'type':type_field})
			return self.psd_show(cr, uid, ids, context)

credit_note_new()

class credit_note(osv.osv):
	_inherit = 'credit.note'

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(credit_note, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	def _check_transfered(self, cr, uid, ids, field_name, args, context=None):
		res = {}
		for rec in self.browse(cr, uid, ids, context):
			res[rec.id]=False
			if rec.customer_name:
				if rec.customer_name.is_transfered:
					res[rec.id]=True
		return res

	_columns = {
		'psd_accounting': fields.boolean('PSD Accounting'),
		'credit_note_type': fields.selection([('Standard','Standard'),('damaged','Damaged Goods'),('return','Return')],'Type'),
		'is_transfered': fields.function(_check_transfered, string="Is Transfered", type="boolean", store=True),
		'invoice_adhoc_ids': fields.one2many('invoice.adhoc.master','credit_note_id','Invoice Lines'),
	}

	def add_credit_note_psd(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			
			if  res.account_id.account_selection in ('cash','iob_one','iob_two'): #HHH 3mar
				raise osv.except_osv(('Alert'),("You can't add Cash or Bank account"))
			
			for i in res.credit_note_one2many:
				if res.account_id.id == i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
			if not res.account_id.id:
				raise osv.except_osv(('Alert'),('Please select Account Name.'))
			if not res.type:
				raise osv.except_osv(('Alert'),('Please select Type.'))
			if not res.status_selection:
				raise osv.except_osv(('Alert'),('Please select status.'))
			if res.status_selection == 'against_short_payment':
				raise osv.except_osv(('Alert'),('"Against short Payment" not applicable for PSD!'))
			if res.account_id.account_selection == 'against_ref':
				cr.execute('update invoice_adhoc_master set check_credit_note = False where check_process_credit_note = False and check_credit_note = True and invoice_number is not Null')

			if res.credit_note_one2many != []:
				flag = False
				test= True
				for line in res.credit_note_one2many:
					if line.account_id.account_selection == 'against_ref':
						for ln in line.credit_outstanding_invoice:
							check_credit_note = ln.check_credit_note
							if check_credit_note == True:
								invoice_number = ln.invoice_number
								flag = True
								if res.account_id.product_id:
									test=False
									if invoice_number:
										for adhoc_ln in ln.invoice_line_adhoc_11:
											pms = adhoc_ln.pms.id
											if res.account_id.product_id:
												if pms == res.account_id.product_id.id:
													amount = adhoc_ln.amount
													test=True
													
                                                                                for adhoc_ln in ln.invoice_line_adhoc:
											pms = adhoc_ln.pms.id
											if res.account_id.product_id:
												if pms == res.account_id.product_id.id:
													amount = adhoc_ln.amount
													test=True
					if test== False:
						raise osv.except_osv(('Alert'),('Please select proper Account Name.'))

			total=amount_dr=amount_cr=0.0

			for i in res.credit_note_one2many:
				if i.account_id.account_selection==False and i.account_id.product_id != False:
					if i.type=='debit':
						total +=i.debit_amount
					else:
						total +=i.credit_amount
			if res.account_id.account_selection== 'tax':			
			        amt = res.account_id.account_tax_many2one.amount
				if res.type=='debit':
					amount_dr = round((float(total)*amt))
				else:
					amount_cr = round((float(total)*amt))

                        elif res.status_selection== 'against_itds' :
                                for i in res.credit_note_one2many:
                                        if i.type == 'credit':
                                                amount_dr += i.credit_amount
                                                               
                        self.pool.get('credit.note.line').create(cr,uid,{
									'credit_id':res.id,
									'account_id':res.account_id.id,
								        'debit_amount':amount_dr,
								        'credit_amount':amount_cr,
									'type':res.type,
									'status_selection':res.status_selection,
									'writeoff_status':res.writeoff_status,
									 })

			self.write(cr,uid,res.id,{'account_id':None,'type':''})

		return True


	def process_psd(self, cr, uid, ids, context=None): # Credit Note process Button
	        sales_receipts = self.pool.get('account.sales.receipts')
		sales_receipts_line = self.pool.get('account.sales.receipts.line')
		cr_total = dr_total = total = 0.0
		move = ''
		post = []
		credit_invoice = ''
		today_date = datetime.now().date()
		flag = py_date = False
		credit_id = ''
		status=[]
		credit_note_date =''
		writeoff_amount=0
		check_process = False
		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			if res.credit_note_date:
				py_date = str(today_date + relativedelta(days=-5))
				if res.credit_note_date > str(today_date):
					raise osv.except_osv(('Alert'),("Forward-dated entries are not allowed!"))
				if res.credit_note_date < str(py_date):
					raise osv.except_osv(('Alert'),('Only 5 days back-dated receipt date is allowed!'))
				credit_note_date=res.credit_note_date
			else:
				credit_note_date=datetime.now().date()
				
			# if not res.writeoff_status:
			#         raise osv.except_osv(('Alert'),('Kindly select the writeoff status before proceeding.'))
			for line in res.credit_note_one2many:

                                if line.credit_amount == 0.0 and line.debit_amount == 0.0:
				        raise osv.except_osv(('Alert'),('Debit and Credit Amount should be greater than zero.'))

				dr_total += line.credit_amount
				cr_total += line.debit_amount

				account_id = line.account_id.id
				temp = tuple([account_id])
				post.append(temp)
				for i in range(0,len(post)):
					for j in range(i+1,len(post)):
						if post[i][0]==post[j][0]:
							raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

				acc_status = line.status_selection
				if acc_status:
					temp = tuple([acc_status])
					status.append(temp)
					for i in range(0,len(status)):
						for j in range(i+1,len(status)):
							if status[i][0] != status[j][0]:
								raise osv.except_osv(('Alert!'),('Status should be same.'))

			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))

		for credit_note in self.browse(cr,uid,ids):
			for credit_note_line in credit_note.credit_note_one2many:
				credit_amount = credit_note_line.credit_amount
				debit_amount = credit_note_line.debit_amount
				acc_selection = credit_note_line.account_id.account_selection
				
				if acc_selection == 'against_ref' and credit_note.status_selection == 'against_itds':
					if flag == False :
						flag = True
				
				################################ 11##############
				if acc_selection == 'against_ref':
					for ln in credit_note_line.credit_outstanding_invoice:
						credit_id = ln.credit_invoice_id
						check_credit_note = ln.check_credit_note
						if check_credit_note == True:
							flag = True
	
				if acc_selection == 'against_ref' and credit_note.writeoff_status != 'fully_writeoff':# added fully
					for ln in credit_note_line.credit_outstanding_invoice:
						credit_id = ln.credit_invoice_id
						check_credit_note = ln.check_credit_note
						if check_credit_note == True:
							flag = True
				
					if flag == False:
						raise osv.except_osv(('Alert'),('No invoice selected.'))
						
					if not credit_id and not (acc_selection == 'against_ref' and credit_note.status_selection == 'against_itds'):
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

		self.pms_validation(cr,uid,ids,context=context) # Validation for Accounts of PMS

########################################################ir#####
		for rec in self.browse(cr,uid,ids):
			amount = total = 0.0

			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_note_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_note_tree')

			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = ''
			
			pcof_key = ''
			credit_note_id = ''
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','credit.note')])
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
				year1 = int(year1)

			financial_start_date = str(start_year)+'-04-01'
			financial_end_date = str(end_year)+'-03-31'
			company_id=self._get_company(cr,uid,context=None)
			
			if company_id:
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					if comp_id.credit_note_id:
						credit_note_id = comp_id.credit_note_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			if pcof_key and credit_note_id:
				cr.execute("select cast(count(id) as integer) from credit_note where credit_note_no is not null   and  credit_note_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + credit_note_id +  str(year1) +str(seq).zfill(6)
			self.write(cr,uid,ids,{
						        'credit_note_no':value_id,
						        'credit_note_date': credit_note_date,
						        'voucher_type':'Credit Note'
							})
							
			date = credit_note_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id

			srch_jour_bank = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
			for jour_bank in self.pool.get('account.journal').browse(cr,uid,srch_jour_bank):
				journal_bank = jour_bank.id

			move = self.pool.get('account.move').create(cr,uid,{
							'journal_id':journal_bank,#Confirm from PCIL(JOURNAL ID)
							'state':'posted',
							'date':date,
							'name':value_id,
							'partner_id':rec.customer_name.id if rec.customer_name.id else '',
							'narration':rec.narration if rec.narration else '',
							'voucher_type':'Credit Note',},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.credit_note_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
							'account_id':ln.account_id.id,
							'debit':ln.debit_amount,
							'name':rec.customer_name.name if rec.customer_name.name else '',
							'journal_id':journal_bank,
							'period_id':period_id,
							'date':date,
							'ref':value_id},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
							'account_id':ln.account_id.id,
							'credit':ln.credit_amount,
							'name':rec.customer_name.name if rec.customer_name.name else '',
							'journal_id':journal_bank,
							'period_id':period_id,
							'date':date,
							'ref':value_id},context=context)

			self.write(cr,uid,rec.id,{'status_selection_new':rec.status_selection})
			self.write(cr,uid,rec.id,{'state':'done','status_selection':''})

		for creditnote_his in self.browse(cr,uid,ids):
			status_selection1=''
			cust_name=creditnote_his.customer_name.name
			if creditnote_his.credit_note_date:
				creditnote_date=creditnote_his.credit_note_date
			else:
				credit_note_date=datetime.now().date()
			creditnote_type=creditnote_his.type
			if creditnote_his.status_selection_new == 'against_ref_writeoff':
				status_selection1='Against Invoice Write-Off'
			if creditnote_his.status_selection_new == 'against_ref_refund':
				status_selection1='Against Reference Refund'
			if creditnote_his.status_selection_new == 'against_short_payment':
				status_selection1='Against Short Payment'
			if creditnote_his.status_selection_new == 'against_itds':
				status_selection1='Against Itds'
			if creditnote_his.status_selection_new == 'against_advance':		#sagar 3 sept from advance
				status_selection1='Against Advance'
			for creditnote_line in creditnote_his.credit_note_one2many:
				amount=creditnote_line.debit_amount

			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('credit.note.history').create(cr,uid,{
					                                        'credit_note_his_many2one':curr_id,
					                                        'credit_note_number':value_id,
					                                        'credit_note_date':creditnote_date,
					                                        'credit_note_type':status_selection1,
					                                        'credit_note_amount':amount})
					                                        
		#################################################  Itds #########################

		for res in self.browse(cr,uid,ids):
                        grand_total =0.0
                        cse_name = itds_cse = invoice_num = invoice_date_concate =''

		        for ln_itds in res.credit_note_one2many:
                		if ln_itds.status_selection == 'against_itds' :
                		        itds_flag=True
                			for line in res.credit_note_one2many:
                				if line.account_id.account_selection == 'others' :
                					itds_flag=False
                		        if ln_itds.account_id.account_selection == 'against_ref' and ln_itds.type == 'credit':
					        for rec_itds in ln_itds.outstanding_invoice_itds:
						        status=pending_status=''
	                                                pending_amount=paid_amount=0.0
						        if rec_itds.credit_itds_invoice_check == True:
                                		                if ln_itds.writeoff_status == 'partially_writeoff':
                                		                        status='printed'
                                		                        pending_status='pending'
                                		                        pending_amount=rec_itds.pending_amount - rec_itds.amount_receipt
                                		                        paid_amount=rec_itds.amount_receipt
                                		                else :
                                 		                        status='paid'
                                		                        pending_status='paid'
                                		                        pending_amount=0.0
                                		                        paid_amount=rec_itds.amount_receipt
                                		                        
                                                                grand_total += rec_itds.grand_total_amount
                                                                cse_name = rec_itds.cse.name
                                                                itds_cse = rec_itds.cse.id
                                                                invoice_num += rec_itds.invoice_number
                                                                invoice_date_concate += rec_itds.invoice_date
                                                                
							        self.pool.get('invoice.adhoc.master').write(cr,uid,rec_itds.id,{
									        'pending_amount':pending_amount,
									        'pending_status':pending_status,
									        'status':status,
									        'itds_writeoff_status':ln_itds.writeoff_status,
									        })
							        self.pool.get('invoice.receipt.history').create(cr,uid,{
									        'invoice_receipt_history_id':rec_itds.id,
									        'invoice_number':rec_itds.invoice_number,
									        'invoice_pending_amount':pending_amount,
									        'invoice_paid_amount':paid_amount,
									        'invoice_paid_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
									        'credit_note_itds_history_id':ln_itds.id,
									        'invoice_date':rec_itds.invoice_date,
                                                                        'service_classification':rec_itds.service_classification,
									        'tax_rate':rec_itds.tax_rate,
									        'cse':rec_itds.cse.id,
									        'check_invoice':True,
									        'itds_outstanding_paid_boolean_process_cn':True,
							        })
							        
				                for rec_itds in ln_itds.paid_invoice_itds_one2many:
						        status=''
	                                                pending_amount=paid_amount=0.0
						        if rec_itds.paid_itds_invoice_check == True:
						                paid_amount=rec_itds.amount_receipt
						                
                                		                if ln_itds.writeoff_status == 'partially_writeoff':
                                		                        status='partially_writeoff'
                                		                        pending_amount=rec_itds.pending_amount + rec_itds.amount_receipt
                                		                        
                                		                else :
                                 		                        status='writeoff'
                                		                        pending_amount=rec.paid_amount
                                		                        
                                                                grand_total += rec_itds.grand_total_amount
                                                                cse_name = rec_itds.cse.name
                                                                itds_cse = rec_itds.cse.id
                                                                invoice_num += rec_itds.invoice_number
                                                                invoice_date_concate += rec_itds.invoice_date
                                                                
							        self.pool.get('invoice.adhoc.master').write(cr,uid,rec_itds.id,{
									        'pending_amount':pending_amount,
									        'pending_status':'pending',
									        'status':status,
									        'itds_writeoff_status':ln_itds.writeoff_status,
									        })
							        self.pool.get('invoice.receipt.history').create(cr,uid,{
									        'invoice_receipt_history_id':rec_itds.id,
									        'invoice_number':rec_itds.invoice_number,
									        'invoice_pending_amount':pending_amount,
									        'itds_revert_amount':paid_amount,
									        'invoice_paid_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
									        'credit_note_itds_history_id':ln_itds.id,
									        'invoice_date':rec_itds.invoice_date,
                                                                        'service_classification':rec_itds.service_classification,
									        'tax_rate':rec_itds.tax_rate,
									        'cse':rec_itds.cse.id,
									        'check_invoice':True,
									        'itds_outstanding_paid_boolean_process_cn':True,
							        })
								        
                		        if ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'debit' and itds_flag:
 					        self.pool.get('itds.adjustment').create(cr,uid,{
					                        'receipt_no':res.credit_note_no,
					                        'receipt_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
					                        'gross_amt':grand_total,
					                        'pending_amt':ln_itds.debit_amount,
					                        'itds_amt':ln_itds.debit_amount,
					                        'invoice_no':invoice_num,
					                        'invoice_date':invoice_date_concate,
					                        'customer_name':res.customer_name.id,
                                                                'customer_name_char':res.customer_name.name,	
					                        'customer_id':res.customer_name.ou_id ,
					                        'cse':cse_name,
					                        'itds_cse':itds_cse,
					                        'added_by_cn':True,})

                		        if ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'credit':
                		                pending_amount =0.0
                		                for rec_itds in ln_itds.revert_itds_one2many_one:
						        if rec_itds.check == True:
						               if ln_itds.writeoff_status == 'partially_writeoff':
                                		                        pending_amount=rec_itds.pending_amt - rec_itds.partial_revert
                                		                        paid_amount=rec_itds.partial_revert
                                		                        total_revert = rec_itds.total_revert + rec_itds.partial_revert
                                        		       else :
                                		                        pending_amount=0.0
                                		                        paid_amount=rec_itds.pending_amt
                                		                        total_revert = rec_itds.total_revert + rec_itds.pending_amt

                                        		       self.pool.get('itds.adjustment').write(cr,uid,rec_itds.id,{
													'pending_amt':pending_amount,
													'state':'fully_reversed',
													'partial_revert':0.0,
													'total_revert':total_revert})
													
							       '''invoice_num = tuple (re.split(' / |, ',rec_itds.invoice_no))	
                                        		       srch_inv = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','in',invoice_num)])
                                        		       for inv in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch_inv):
									paid_amount += inv.pending_amount
									self.pool.get('invoice.adhoc.master').write(cr,uid,inv.id,{
													'pending_amount':pending_amount,
													'pending_status':'pending',
													'status':'printed',
													'check_process_credit_note':True,
													'itds_reverted_to_invoice_pending_amt':True,
													'check_process_invoice':False})
													
									self.pool.get('invoice.receipt.history').create(cr,uid,{
													'invoice_number':inv.invoice_number,
													'invoice_pending_amount':pending_amount,
													'itds_revert_amount':paid_amount,
													'invoice_paid_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
													'invoice_receipt_history_id':inv.id,
													                                                                                'service_classification':inv.service_classification,
										                        'tax_rate':inv.tax_rate,
										                        'cse':inv.cse.id,
})				'''
                                                
		self.write(cr,uid,rec.id,{'state':'done','acc_status':''})
		################################################ itds#########################
                sd_cse=sd_emp_code=''
                sd_amount=0.0
                
		for rec1 in self.browse(cr,uid,ids):
			for line_state in rec1.credit_note_one2many:
				pending_amt= pending_amount =grand_total_against=total_amount=0.0
				pending_status = status = payment_status =''
				self.pool.get('credit.note.line').write(cr,uid,line_state.id,{'state':'done'})
				for chk in line_state.credit_outstanding_invoice:
					check_credit_note = chk.check_credit_note
					if check_credit_note == True:
	                ##### Against Reference Writeoff
						if rec1.status_selection_new == 'against_ref_writeoff':
							if rec1.writeoff_status == 'partially_writeoff':
								pending_amount = chk.pending_amount - chk.writeoff_amount
								total_amount = chk.total_writeoff + chk.writeoff_amount
								writeoff_amount = chk.writeoff_amount
								payment_status = 'partially_writeoff'
								pending_status = 'pending'
								status         = 'partially_writeoff'
                                                                check_process  = False
                                                                
							if rec1.writeoff_status == 'fully_writeoff':
							        pending_amount = 0.0
							        writeoff_amount = chk.pending_amount
							        payment_status = 'writeoff' 
							        pending_status = 'paid'
								status         = 'writeoff'
							        total_amount  = chk.total_writeoff + chk.pending_amount
							        check_process  = True
							
							sd_amount += writeoff_amount
							sd_cse = chk.cse.id 
							sd_emp_code =  chk.cse.emp_code   
							   
							self.pool.get('invoice.receipt.history').create(cr,uid,{
								'invoice_receipt_history_id':chk.id,
								'invoice_number':chk.invoice_number,
								'invoice_pending_amount':pending_amount,
								'credit_id_history':line_state.id,
								'invoice_date':chk.invoice_date,
								'service_classification':chk.service_classification,
								'tax_rate':chk.tax_rate,
								'cse':chk.cse.id,
								'check_invoice':True,
								'invoice_writeoff_amount':writeoff_amount,
								'invoice_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date() })
							self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{
									'pending_amount':pending_amount,
									'pending_status':pending_status,
									'status':status,
									'check_process_credit_note':check_process,
									'total_writeoff':total_amount,
									'writeoff_amount':0.0
									})
							
                                ##### Against Reference Refund
						if  rec1.status_selection_new =='against_ref_refund':
							if rec1.writeoff_status == 'partially_writeoff':
								pending_amount =   chk.pending_amount + chk.writeoff_amount
								total_amount = chk.total_writeoff + chk.writeoff_amount
								writeoff_amount = chk.writeoff_amount
							        payment_status = 'partially_writeoff'
							        pending_status = 'pending'
								status         = 'partially_writeoff'
								check_process  = False
								
							if rec1.writeoff_status == 'fully_writeoff':
							        writeoff_amount = chk.paid_amount
								pending_amount =   chk.pending_amount + chk.paid_amount
								total_amount = chk.total_writeoff + chk.paid_amount
								payment_status = 'writeoff'
								pending_status = 'paid'
								status         = 'writeoff'
								check_process  = True
									
							self.pool.get('invoice.receipt.history').create(cr,uid,{
								'invoice_receipt_history_id':chk.id,
								'invoice_number':chk.invoice_number,
								'invoice_pending_amount':pending_amount,
								'credit_id_history':line_state.id,
								'invoice_date':chk.invoice_date,
								'service_classification':chk.service_classification,
								'tax_rate':chk.tax_rate,
								'cse':chk.cse.id,
								'check_invoice':True,
								'invoice_writeoff_amount':writeoff_amount,
								'invoice_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date() })
							self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{
								'pending_amount':pending_amount,
								'pending_status':pending_status,
								'status':status,
								'check_process_credit_note':check_process,
								'total_writeoff':total_amount,
								'writeoff_amount':0.0}) 

	####### Advance Credit note 3 sept 15 #########>>>>>>>>>>>>>>>>>>>
						if rec1.status_selection_new == 'against_advance'  :
						        if rec1.writeoff_status == 'partially_writeoff':
								pending_amount = chk.pending_amount - chk.writeoff_amount
								paid_amt=chk.grand_total_amount-pending_amount
								writeoff_amount = chk.writeoff_amount
							        payment_status = 'partially_writeoff'
							        pending_status = 'pending'
								status         = 'printed'
								check_process  = False
								
							if rec1.writeoff_status == 'fully_writeoff':
								pending_amount = 0.0
								total_amount = chk.total_writeoff + chk.paid_amount
								writeoff_amount = chk.paid_amount
								payment_status = 'writeoff'
								pending_status = 'paid'
								status         = 'paid'
								check_process  = True
								
							self.pool.get('invoice.receipt.history').create(cr,uid,{
										'invoice_receipt_history_id':chk.id,
										'invoice_number':chk.invoice_number,
										'invoice_pending_amount':pending_amount,
										'credit_id_history':line_state.id,
										'invoice_date':chk.invoice_date,
										'service_classification':chk.service_classification,
										'tax_rate':chk.tax_rate,
										'invoice_paid_amount':chk.writeoff_amount,
										'cse':chk.cse.id,
										'check_invoice':True,
										'advance_writeoff_amount':chk.writeoff_amount,
										'advance_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date()  })
								
							self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{
									'pending_amount':pending_amount,
									'pending_status':pending_status,
									'status':status,
									'check_process_credit_note':check_process,
									'writeoff_amount':0.0,})
								
		##### Against Short Payment
					        if  rec1.status_selection_new == 'against_short_payment':
					                payment_status ='paid' 
						        self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{
					                                        'check_process_credit_note':True,
					                                        'pending_amount':'0.0',
					                                        'pending_status':'paid'})
																				                
                                                        self.pool.get('invoice.receipt.history').create(cr,uid,{
                                                                                'credit_id_history':line_state.id,
                                                                                'invoice_receipt_history_id':chk.id,
                                                                                'invoice_paid_date':rec1.credit_note_date,
                                                                                'invoice_date':chk.invoice_date,
                                                                                'tax_rate':chk.tax_rate,
                                                                                'invoice_paid_amount':chk.pending_amount,
                                                                                'invoice_pending_amount':0.0,
                                                                                'invoice_number':chk.invoice_number,
                                                                                'service_classification':chk.service_classification,
                                                                                'cse':chk.cse.id,})  
                                        
                                                if  rec1.status_selection_new == 'against_itds':
                                                        payment_status ='paid'
                                                        
                                                pay_con_history =self.pool.get('payment.contract.history')
                                                srch_history = pay_con_history.search(cr,uid,[('invoice_number','=',chk.invoice_number)])
						if srch_history:
							for invoice_history in pay_con_history.browse(cr,uid,srch_history):
								pay_con_history.write(cr,uid,invoice_history.id,{'payment_status':payment_status})
							
			############### sagar advance Credit note 3sept #############>>>>>>>>>>>>>>>>>>>>>>
				for rec_advance in line_state.credit_advance_one2many:
					if rec_advance.check_advance_against_ref == True:
						if rec1.status_selection_new == 'against_advance' :
						        if rec_advance.advance_pending < rec_advance.partial_amt :
						                raise osv.except_osv(('Alert'),('enter proper partial amount'))
						                
							if rec1.writeoff_status == 'partially_writeoff' :
								pending_amt=rec_advance.advance_pending-rec_advance.partial_amt
								refund_amt = rec_advance.partial_amt
								
							if rec1.writeoff_status == 'fully_writeoff' :
							        pending_amt = 0.0 
								refund_amt = rec_advance.advance_pending
								
							receipt_id=receipt_no=''
							############################
							line_srch=sales_receipts_line.search(cr,uid,[('id','=',rec_advance.advance_id.id)])
							if line_srch:
							        for i in sales_receipts_line.browse(cr,uid,line_srch):
							                main_srch=sales_receipts.search(cr,uid,[('id','=',i.receipt_id.id)])
							                for j in sales_receipts.browse(cr,uid,main_srch):
							                        receipt_no=j.receipt_no
							                        receipt_id=j.id
							                        sales_receipts.write(cr,uid,j.id,{'advance_pending':pending_amt})
							###########################
								
							self.pool.get('advance.sales.receipts').write(cr,uid,rec_advance.id,{
									        'advance_pending':pending_amt,
									        'check_advance_against_ref':True if pending_amt else False,
									        'check_advance_against_ref_process':True if pending_amt else False,})
							abc=self.pool.get('advance.receipt.history').create(cr,uid,{
								                        'advance_receipt_no':receipt_no if receipt_no else rec_advance.receipt_no,
								                        'advance_date':rec_advance.receipt_date,
								                        'cust_name':rec_advance.partner_id.id,
								                        'advance_refund_amount':refund_amt,
								                        'advance_pending_amount':pending_amt,
								                        'advance_receipt_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),'service_classification':rec_advance.service_classification,
								                        'advance_history_id':line_state.id,
								                        'history_advance_id':rec_advance.id,
								                        'receipt_id':receipt_id if receipt_id else False}) 
			#<<<<<<<<<<<<<<<<<<<<<<<<< sagar##################################
		for rec in self.browse(cr,uid,ids):
                        for res in rec.credit_note_one2many:
                                if res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'others':
                                        for line in res.branch_itds_one2many:
                                                self.pool.get('itds.adjustment').write(cr,uid,line.id,{'receipt_no':rec.credit_note_no,
                                                                                                       'receipt_date':rec.credit_note_date,
                                                                                                       'customer_name':rec.customer_name.id if rec.customer_name else '',
                                                                                                'customer_name_char':rec.customer_name.name if rec.customer_name else '',
                                                                                                       'pending_amt':line.itds_amt,
                                                                                                       'state':'pending',
                                                                                                       'ou_id':rec.customer_name.ou_id if rec.customer_name else '',})
                                if res.account_id.account_selection == 'security_deposit' and res.status_selection =='against_ref_writeoff' and res.type == 'debit':
                                        self.pool.get('security.deposit').create(cr,uid,{
                                                                                'cn_security_id':res.id,
                                                                                'cse':sd_cse,
                                                                                'emp_code':sd_emp_code,
                                                                                'ref_no':rec.credit_note_no,
		                                                                'ref_date':rec.credit_note_date,
		                                                                'pending_amount':sd_amount,
		                                                                'ref_amount':sd_amount,
		                                                                'customer_name':rec.customer_name.id if rec.customer_name else '',
		                                                                'customer_id':rec.customer_name.ou_id if rec.customer_name else '',
                                                                                })
			if rec.credit_note_type == 'return':
				for invoice_id in rec.invoice_adhoc_ids:
					for each in rec.invoice_adhoc_ids:
						credit_inv_batch_id = each.credit_inv_batch_id
						for batch_quantity_id in credit_inv_batch_id:
							batch_id = batch_quantity_id.batch_id.id
							quantity = batch_quantity_id.quantity
							avl_qty = batch_quantity_id.batch_id.local_qty
							qty = batch_quantity_id.batch_id.qty
							new_avl_qty = avl_qty + quantity
							conversion_ratio = batch_quantity_id.batch_id.name.local_uom_relation
							new_qty = new_avl_qty/conversion_ratio
							self.pool.get('res.batchnumber').write(cr, uid, batch_id, {'local_qty':new_avl_qty,'qty':new_qty}, context=context)
		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
		self.sync_writeoff(cr,uid,ids,context=context) # Syncronization for Writeoff state with CCC Main
		self.sync_credit_note_history(cr,uid,ids,context=context)#synchronization for credit note history in ccc main
		return  {
			'name':'Credit Note',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'credit.note',
			'res_id':rec1.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
			}


	def psd_onchange_account_type(self, cr, uid, ids, account_id, context=None):
		v = {}
		if account_id:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection == '':
						v['type'] = ''
					elif acc.account_selection == 'itds_receipt':
						v['status_selection_new'] = 'against_itds' 
					elif acc.account_selection == 'against_ref':
						v['type'] = 'credit'
					else:
						v['type'] = ''
						
		return {'value':v}		

credit_note()

class credit_note_st(osv.osv):
	_inherit='credit.note.st'

	_columns = {
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'reference':fields.selection([('new_reference','New Reference'),('against_reference','Against Reference'),('against_advance','Against Advance')],'Reference'),
		'psd_accounting': fields.boolean('PSD Accounting')
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(credit_note_st, self).default_get(cr, uid, fields, context=context)
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
					if acc.account_selection in ('cash','iob_one'):
						v['type'] = 'debit'
					elif acc.account_selection == 'iob_two':
						v['type'] = 'credit'
					elif acc.account_selection == 'against_ref':
						v['type'] = 'credit'
					else:
						v['type'] = ''
		return {'value':v}


credit_note_st()


class credit_note_line_st(osv.osv):

	_inherit = 'credit.note.line.st'

	def add(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			acc_selection = res.account_id.account_selection
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			acc_selection_list = ['against_ref','advance']
			view_name = name_wizard ='' 
			if acc_selection in acc_selection_list:
				if acc_selection == 'against_ref':
					temp=''
					if res.status == 'against_cancellation' :
						self.show_details(cr,uid,ids,context=context)
						view_name = 'account_credit_against_ref_form_st'
						name_wizard ="Outstanding Invoices"
						
				if acc_selection == 'advance' and res.type == 'debit':# HHH 3nov adjusting CFOB entries reflecting under advance
					self.show_details_cr(cr,uid,ids,context=context)
					view_name = 'against_advance_form_cr'
					name_wizard = "Advance Payment Details"

				models_data=self.pool.get('ir.model.data')
				if view_name :
						form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch',view_name )
						return {
							'name': (name_wizard),'domain': '[]',
							'type': 'ir.actions.act_window',
							'view_id': False,
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'credit.note.line.st',
							'target' : 'new',
							'res_id':int(res_id),
							'views': [(form_view and form_view[1] or False, 'form'),
									   (False, 'calendar'), (False, 'graph')],
							'domain': '[]',
							'nodestroy': True,
						}
		return True


	def psd_add(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			acc_selection = res.account_id.account_selection
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			acc_selection_list = ['against_ref','advance']
			view_name = name_wizard ='' 
			if acc_selection in acc_selection_list:
				if acc_selection == 'against_ref':
					temp=''
					if res.status == 'against_cancellation' :
						self.show_details(cr,uid,ids,context=context)
						view_name = 'psd_account_credit_against_ref_form_st'
						name_wizard ="Outstanding Invoices"
						
				if acc_selection == 'advance' and res.type == 'debit':# HHH 3nov adjusting CFOB entries reflecting under advance
					self.show_details_cr(cr,uid,ids,context=context)
					view_name = 'psd_against_advance_form_cr'
					name_wizard = "Advance Payment Details"

				models_data=self.pool.get('ir.model.data')
				if view_name :
						form_view=models_data.get_object_reference(cr, uid, 'psd_accounting',view_name )
						return {
							'name': (name_wizard),'domain': '[]',
							'type': 'ir.actions.act_window',
							'view_id': False,
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'credit.note.line.st',
							'target' : 'new',
							'res_id':int(res_id),
							'views': [(form_view and form_view[1] or False, 'form'),
									   (False, 'calendar'), (False, 'graph')],
							'domain': '[]',
							'nodestroy': True,
						}		
		return True

credit_note_line_st()


class credit_note_line(osv.osv):
	_inherit = 'credit.note.line'

	_columns = {
		'total_writeoff': fields.float('Total Writeoff'),	
	}

	def save_outstanding_invoice_psd(self, cr, uid,ids, context=None):
		count = 0.0
		flag = False
		type1 = ""
		for res in self.browse(cr,uid,ids):
			cr_amount = res.credit_amount
			dr_amount = res.debit_amount
			type1 = res.type
			true_invoice_ids = []
			if res.credit_outstanding_invoice == []:
				raise osv.except_osv(('Alert'),('No line to proceed.'))
			for line in res.credit_outstanding_invoice:
				if line.check_credit_note == True:
					if res.status_selection == 'against_ref_writeoff':
						if res.credit_id.writeoff_status == 'partially_writeoff':
							if not line.writeoff_amount:
									raise osv.except_osv(('Alert'),('Enter writeoff Amount'))
							if (line.writeoff_amount - line.pending_amount) == 0.0:
										raise osv.except_osv(('Alert'),('Please select fully writeoff'))
							if line.writeoff_amount > line.pending_amount:
										raise osv.except_osv(('Alert'),('Writeoff amount should be less than Invoice pending Amount'))
									
							count = count + line.writeoff_amount
							
						if res.credit_id.writeoff_status == 'fully_writeoff':
								
							if line.writeoff_amount > line.pending_amount:
										raise osv.except_osv(('Alert'),('Writeoff amount should be less than Invoice pending Amount'))
										
							count = count + line.pending_amount

					if res.status_selection == 'against_ref_refund':
						if res.credit_id.writeoff_status == 'partially_writeoff':
							if not line.writeoff_amount:
									raise osv.except_osv(('Alert'),('Enter writeoff Amount'))
							if (line.writeoff_amount - line.paid_amount) == 0.0:
										raise osv.except_osv(('Alert'),('Please select fully writeoff'))
							if line.writeoff_amount > line.paid_amount:
										raise osv.except_osv(('Alert'),('Writeoff amount should be less than Invoice Paid Amount'))
							count = count + line.writeoff_amount
							
						if res.credit_id.writeoff_status == 'fully_writeoff':
								if line.writeoff_amount > line.paid_amount:
										raise osv.except_osv(('Alert'),('Writeoff amount should be less than Invoice Paid Amount'))
								count = count + line.paid_amount
							
					elif res.status_selection =='against_short_payment':###short payment
						count = count + line.pending_amount
					elif res.status_selection =='against_itds':###itds
						count = count + line.pending_amount
					elif res.status_selection == 'against_cancellation':
						count = count + line.grand_total_amount
					if res.status_selection == 'against_advance' :
						if res.credit_id.writeoff_status == 'partially_writeoff':
							if not line.writeoff_amount:
								raise osv.except_osv(('Alert'),('Enter writeoff Amount'))
							if (line.writeoff_amount - line.pending_amount) == 0.0:
								raise osv.except_osv(('Alert'),('Please select fully writeoff'))
							if (line.pending_amount-line.writeoff_amount) < 0.0:
								raise osv.except_osv(('Alert'),('Enter proper Writeoff Amount'))

							count = count + line.writeoff_amount

						if res.credit_id.writeoff_status == 'fully_writeoff':
							if line.writeoff_amount != line.pending_amount:
											raise osv.except_osv(('Alert'),('Writeoff amount should be less than Invoice Paid Amount'))
							count = count + line.pending_amount
					true_invoice_ids.append(line.id)	
			if type1== 'debit':
				self.write(cr,uid,res.id,{'debit_amount':count})
			else:
				self.write(cr,uid,res.id,{'credit_amount':count})

			self.pool.get('invoice.adhoc.master').write(cr,uid,line.id,{'check_invoice':True})
			self.pool.get('credit.note').write(cr, uid, res.credit_id.id, {'invoice_adhoc_ids':[(6, 0, true_invoice_ids)]}, context=context)
		return {'type': 'ir.actions.act_window_close'}


	# def add(self, cr, uid, ids, context=None):
	# 	for res in self.browse(cr,uid,ids):
	# 		acc_selection = res.account_id.account_selection
	# 		res_id = res.id
	# 		credit_amount = res.credit_amount
	# 		debit_amount = res.debit_amount
	# 		temp=''
			
	# 		if (res.status_selection == 'against_ref_writeoff' or  res.status_selection == 'against_ref_refund') and acc_selection =='against_ref':
	# 			models_data=self.pool.get('ir.model.data')
	# 			if  res.account_id.account_selection == 'against_ref':
	# 				if res.status_selection == 'against_ref_writeoff':
	# 					temp="Outstanding Invoice"
	# 				else:
	# 					temp="Paid Invoices"
	# 				self.show_details(cr,uid,ids,context=context)
	# 				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_form')
	# 				return {
	# 					'name': temp,'domain': '[]',
	# 					'type': 'ir.actions.act_window',
	# 					'view_id': False,
	# 					'view_type': 'form',
	# 					'view_mode': 'form',
	# 					'res_model': 'credit.note.line',
	# 					'target' : 'new',
	# 					'res_id':int(res_id),
	# 					'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 					'domain': '[]',
	# 					'nodestroy': True,
	# 				}
	# 			else:
	# 				pass
					
	# 		elif res.account_id.account_selection=='against_ref' and res.status_selection=='against_short_payment': ##short payment
	# 			models_data=self.pool.get('ir.model.data')
	# 			self.show_details(cr,uid,ids,context=context)
	# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_for_short_payment')
	# 			return {
	# 				'name': ("Outstanding Invoice"),'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'credit.note.line',
	# 				'target' : 'new',
	# 				'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 				   }              

	# 		elif  res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'against_ref':
	# 			models_data=self.pool.get('ir.model.data')
	# 			self.show_itds_details_against_ref(cr,uid,ids,context=context)

	# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'itds_against_ref_form')#27oct15
	# 			return {
	# 				'name': ("Outstanding Invoice"),'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'credit.note.line',
	# 				'target' : 'new',
	# 				'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 				   }

	# 		elif  res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'itds_receipt':
	# 			models_data=self.pool.get('ir.model.data')
	# 			self.show_itds_details(cr,uid,ids,context=context)
	# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_for_itds_payment')
	# 			return {
	# 				'name': ("Outstanding Invoice"),'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'credit.note.line',
	# 				'target' : 'new',
	# 				'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 				   }
					   
	# 		elif  res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'others':
	# 			models_data=self.pool.get('ir.model.data')
	# 			form_view=models_data.get_object_reference(cr,uid,'account_sales_branch', 'account_other_branch_itds_collection')
	# 			return {
	# 				'name': ("Outstanding Invoice"),'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'credit.note.line',
	# 				'target' : 'new',
	# 				'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 				   }
					   
	# 		elif res.status_selection == 'against_cancellation' :
	# 			models_data=self.pool.get('ir.model.data')
	# 			self.show_details(cr,uid,ids,context=context)
	# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_form')
	# 			return {
	# 				'name': ("Paid Invoices"),'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'credit.note.line',
	# 				'target' : 'new',
	# 				'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 				(False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 			}

	# 	######## Advance Credit Refund
	# 		elif res.status_selection == 'against_advance' and acc_selection == 'against_ref' and res.type == 'credit':
	# 			models_data=self.pool.get('ir.model.data')
	# 			self.show_details(cr,uid,ids,context=context)
	# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_form')
	# 			return {
	# 				'name': temp,'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'credit.note.line',
	# 				'target' : 'new',
	# 				'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 								   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 						}

	# 		elif res.status_selection == 'against_advance' and acc_selection == 'advance' and res.type == 'debit':
	# 			models_data=self.pool.get('ir.model.data')
	# 			self.show_advance_details(cr,uid,ids,context=context)
	# 			form_view=models_data.get_object_reference(cr,uid,'account_sales_branch','against_advance_credit_note_form')
	# 			return{
	# 				'name':('Advance Payment Details'),'domain':'[]',
	# 				'type':'ir.actions.act_window',
	# 				'view_id':False,
	# 				'view_type':'form',
	# 				'view_model':'form',
	# 				'res_model':'credit.note.line',
	# 				'target':'new',
	# 				'res_id':int(res_id),
	# 				'views':[(form_view and form_view[1] or False, 'form'),
	# 				(False,'calender'),(False,'graph')],
	# 				'domain':'[]',
	# 				'nodestroy':True,
	# 			}
				
	# 		elif res.status_selection == 'against_ref_writeoff' and acc_selection =='security_deposit' and res.type == 'debit' and res.state=='done':
	# 			models_data=self.pool.get('ir.model.data')
	# 			form_view=models_data.get_object_reference(cr,uid,'account_sales_branch','securit_deposit_credit_note_form')
	# 			return{
	# 				'name':('Security Deposit Details'),'domain':'[]',
	# 				'type':'ir.actions.act_window',
	# 				'view_id':False,
	# 				'view_type':'form',
	# 				'view_model':'form',
	# 				'res_model':'credit.note.line',
	# 				'target':'new',
	# 				'res_id':int(res_id),
	# 				'views':[(form_view and form_view[1] or False, 'form'),
	# 				(False,'calender'),(False,'graph')],
	# 				'domain':'[]',
	# 				'nodestroy':True,
	# 			}
	# 	return True

	def psd_add(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			acc_selection = res.account_id.account_selection
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			temp=''
			
			if (res.status_selection == 'against_ref_writeoff' or  res.status_selection == 'against_ref_refund') and acc_selection =='against_ref':
				models_data=self.pool.get('ir.model.data')
				if  res.account_id.account_selection == 'against_ref':
					if res.status_selection == 'against_ref_writeoff':
						temp="Outstanding Invoice"
					else:
						temp="Paid Invoices"
					self.show_details(cr,uid,ids,context=context)
					form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_against_ref_form')
					return {
						'name': temp,'domain': '[]',
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'credit.note.line',
						'target' : 'new',
						'res_id':int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True,
					}
				else:
					pass
					
			elif res.account_id.account_selection=='against_ref' and res.status_selection=='against_short_payment': ##short payment
				models_data=self.pool.get('ir.model.data')
				self.show_details(cr,uid,ids,context=context)
				form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_against_ref_for_short_payment')
				return {
					'name': ("Outstanding Invoice"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					   }              

			elif  res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'against_ref':
				models_data=self.pool.get('ir.model.data')
				self.show_itds_details_against_ref(cr,uid,ids,context=context)

				form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_itds_against_ref_form')#27oct15
				return {
					'name': ("Outstanding Invoice"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					   }

			elif  res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'itds_receipt':
				models_data=self.pool.get('ir.model.data')
				self.show_itds_details(cr,uid,ids,context=context)
				form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_against_ref_for_itds_payment')
				return {
					'name': ("Outstanding Invoice"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					   }
					   
			elif  res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'others':
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr,uid,'psd_accounting', 'psd_account_other_branch_itds_collection')
				return {
					'name': ("Outstanding Invoice"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					   }
					   
			elif res.status_selection == 'against_cancellation' :
				models_data=self.pool.get('ir.model.data')
				self.show_details(cr,uid,ids,context=context)
				form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_against_ref_form')
				return {
					'name': ("Paid Invoices"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
					(False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
				}

		######## Advance Credit Refund
			elif res.status_selection == 'against_advance' and acc_selection == 'against_ref' and res.type == 'credit':
				models_data=self.pool.get('ir.model.data')
				self.show_details(cr,uid,ids,context=context)
				form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_against_ref_form')
				return {
					'name': temp,'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'credit.note.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
									   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
							}

			elif res.status_selection == 'against_advance' and acc_selection == 'advance' and res.type == 'debit':
				models_data=self.pool.get('ir.model.data')
				self.show_advance_details(cr,uid,ids,context=context)
				form_view=models_data.get_object_reference(cr,uid,'psd_accounting','psd_against_advance_credit_note_form')
				return{
					'name':('Advance Payment Details'),'domain':'[]',
					'type':'ir.actions.act_window',
					'view_id':False,
					'view_type':'form',
					'view_model':'form',
					'res_model':'credit.note.line',
					'target':'new',
					'res_id':int(res_id),
					'views':[(form_view and form_view[1] or False, 'form'),
					(False,'calender'),(False,'graph')],
					'domain':'[]',
					'nodestroy':True,
				}
				
			elif res.status_selection == 'against_ref_writeoff' and acc_selection =='security_deposit' and res.type == 'debit' and res.state=='done':
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr,uid,'psd_accounting','psd_securit_deposit_credit_note_form')
				return{
					'name':('Security Deposit Details'),'domain':'[]',
					'type':'ir.actions.act_window',
					'view_id':False,
					'view_type':'form',
					'view_model':'form',
					'res_model':'credit.note.line',
					'target':'new',
					'res_id':int(res_id),
					'views':[(form_view and form_view[1] or False, 'form'),
					(False,'calender'),(False,'graph')],
					'domain':'[]',
					'nodestroy':True,
				}
		return True

credit_note_line()

class credit_note_register_line(osv.osv):
	_inherit='credit.note.register.line'
	_columns={
		'credit_note_register_id':fields.many2one('credit.note.search',''),
		'credit_date':fields.date('Date'),
		'credit_note_particulars':fields.char('Particulars',size=280),
		'credit_voucher_no':fields.char('Voucher No.',size=124),
		'credit_voucher_ref':fields.char('Bill No.',size=280),
		'credit_gross_total':fields.float('Gross Total'),
		'credit_service_tax':fields.float('Service Tax'),
		'credit_tspo':fields.float('TSPO'),
		'credit_tspr':fields.float('TSPR'),
		'credit_gss':fields.float('GSS'),
		'credit_pss':fields.float('PSS'),
		'credit_pps':fields.float('PPS'),
		'credit_gpm':fields.float('GPM'),
		'credit_ifm':fields.float('IFM'),
		'credit_imm':fields.float('IMM'),
		'credit_all_item':fields.float('All Item'),
	}

credit_note_register_line()



class debit_note(osv.osv):
	_inherit='debit.note'
	
	_columns={
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'psd_accounting': fields.boolean('PSD Accounting')
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(debit_note, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	def onchange_debit_note_date(self, cr, uid, ids, debit_note_date, context=None):
		v = {}
		if debit_note_date:
			today_date = datetime.now().date()			
			py_date = str(today_date + relativedelta(days=-5))
			if debit_note_date < str(py_date) or debit_note_date > str(today_date):
				raise osv.except_osv(('Alert'),('Kindly select Debit note Date 5 days earlier from current date.'))
		return {'value':v}

	def psd_debit_note_process(self, cr, uid, ids, context=None):
		cr_total = dr_total = grand_total = 0.0
		move = debit_invoice_id=''
		post=[]
		today_date = datetime.now().date()
		flag = py_date = False
		line_acc = []
		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			line_acc = []
			if res.debit_note_date:
				py_date = str(today_date + relativedelta(days=-5))
				if res.debit_note_date < str(py_date) or res.debit_note_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Date 5 days earlier from current date.'))
				debit_note_date=res.debit_note_date	
			else:
				debit_note_date=datetime.now().date()
			for line in res.debit_note_one2many:
				line_acc.append(line.account_id.account_selection)
				if line.credit_amount:
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				if line.debit_amount:
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				cr_total += line.credit_amount
				dr_total +=  line.debit_amount

				account_id = line.account_id.id
				temp = tuple([account_id])
				post.append(temp)
				for i in range(0,len(post)):
					for j in range(i+1,len(post)):
						if post[i][0]==post[j][0]:
							raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

			if dr_total != cr_total:
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
			# if 'cash' or 'iob_one' or 'iob_two' in line_acc:
			# 	raise osv.except_osv(('Alert'),('Cash or Bank ledger cannot be used in Debit note'))
		for res in self.browse(cr,uid,ids):
			for line in res.debit_note_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name
		        if acc_selection == 'against_ref':
					if line.debit_outstanding_invoice:
						for invoice_line in line.debit_outstanding_invoice:
							debit_invoice_id =  invoice_line.debit_invoice_id.id
							if invoice_line.check_debit_note == True:
								flag = True
								grand_total += invoice_line.grand_total
					if line.debit_paid_receipt_one2many:
						for invoice_line in line.debit_paid_receipt_one2many:
							if invoice_line.check_invoice == True:
								self.pool.get('invoice.receipt.history').write(cr,uid,invoice_line.id,{'debit_note_process':'True'})
								amount=(invoice_line.invoice_receipt_history_id.pending_amount)+invoice_line.invoice_paid_amount
								self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.invoice_receipt_history_id.id,{
									'pending_amount':amount,
									'status':'printed',
									'pending_status':'pending',
									'check_process_invoice':False})
		self.pms_validation(cr,uid,ids,context=context)

		for rec in self.browse(cr,uid,ids):
			amount = total = 0.0
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_debit_note_form')
			tree_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_debit_note_tree')

			today_date = datetime.now().date()

			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''

			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','debit.note')])
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
				year1 = int(year1)

			financial_start_date = str(start_year)+'-04-01'
			financial_end_date = str(end_year)+'-03-31'
			company_id=self._get_company(cr,uid,context=None)
			if company_id:
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					if comp_id.credit_note_id:
						debit_note_id = comp_id.debit_note_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			if pcof_key and debit_note_id:
				cr.execute("select cast(count(id) as integer) from debit_note where debit_note_no is not null   and  debit_note_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
		        	temp_count=cr.fetchone()
		        	if temp_count[0]:
		        		count= temp_count[0]
		        	seq=int(count+seq_start)
				value_id = pcof_key + debit_note_id +  str(year1) +str(seq).zfill(6)
			
			self.write(cr,uid,ids,{'debit_note_no':value_id,'debit_note_date': debit_note_date,'cust_name':rec.customer_name.name,'voucher_type':'Debit Note'})
			date = debit_note_date
            		search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
            		for var in self.pool.get('account.period').browse(cr,uid,search_date):
                		period_id = var.id
                	srch_jour_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
			for jour_acc in self.pool.get('account.journal').browse(cr,uid,srch_jour_acc):
				journal_id = jour_acc.id
				
			move = self.pool.get('account.move').create(cr,uid,{'journal_id':journal_id,####hardcoded not confirm by pcil
                                                                    'state':'posted',
                                                                    'date':date,
                                                                    'name':value_id,
								    'narration':rec.narration if rec.narration else '',
								    'voucher_type':'Debit Note',
                                                                    },context=context)

                	for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in rec.debit_note_one2many:
					if ln.debit_amount:
                				self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
                                                                'account_id':ln.account_id.id,
                                                                'debit':ln.debit_amount,
                                                                'name':rec.customer_name.name if rec.customer_name.name else '',
                                                                'journal_id':journal_id,
                                                                'period_id':period_id,
                                                                'date':date,
                                                                'ref':value_id},context=context)
					if ln.credit_amount:
                				self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
                                                                'account_id':ln.account_id.id,
                                                                'credit':ln.credit_amount,
                                                                'name':rec.customer_name.name if rec.customer_name.name else '',
                                                                'journal_id':journal_id,
                                                                'period_id':period_id,
                                                                'date':date,
                                                                'ref':value_id},context=context)

                		
			self.write(cr,uid,rec.id,{'state':'done','status':'','state_new':'open'})#a
			for line_state in rec.debit_note_one2many:
				self.pool.get('debit.note.line').write(cr,uid,line_state.id,{'state':'done'})
				for chk in line_state.debit_outstanding_invoice:
					check_debit_note = chk.check_debit_note
					if check_debit_note == True:
						self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{'check_process_debit_note':True})


		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State

		for debitnote_his in self.browse(cr,uid,ids):#edited by rohit 12 may
			#receipt_no=payment_his.value_id#payment_his.receipt_no
			cust_name=debitnote_his.customer_name.name
			debitnote_date=debitnote_his.debit_note_date

			for debitnote_line in debitnote_his.debit_note_one2many:
				amount=debitnote_line.debit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('debit.note.history').create(cr,uid,{
									'debit_note_his_many2one':curr_id,
									'debit_note_number':value_id,
									'debit_note_date':debit_note_date,
									'debit_note_amount':amount})
		
		self.sync_debit_note_history(cr,uid,ids,context=context)
		return  {
			'name':'Debit Note',
			'view_mode'	: 'tree,form',
			'view_id'	: False,
			'view_type'	: 'form',
			'res_model'	: 'debit.note',
			'res_id'	: rec.id,
			'type'		: 'ir.actions.act_window',
			'target'	: 'current',
			'domain'	: '[]',
			'context'	: context,
		}

debit_note()


