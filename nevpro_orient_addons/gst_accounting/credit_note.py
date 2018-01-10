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
from datetime import date,datetime, timedelta
from dateutil.relativedelta import *
from dateutil.relativedelta import relativedelta
import re


class credit_note(osv.osv):
	_inherit = 'credit.note'
	_order = 'credit_note_date desc'
	
	_columns = {
		'gst_credit_note':fields.boolean('GST Credit Note?'),
	}

	def add_credit_note(self, cr, uid, ids, context=None):
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
			
			if res.account_id.account_selection == 'against_ref' and res.status_selection != 'against_itds':
				if res.type == 'debit':
					raise osv.except_osv(('Alert'),('Account Should be credit'))
			
			if res.account_id.account_selection == 'against_ref':
				cr.execute('update invoice_adhoc_master set check_credit_note = False where check_process_credit_note = False and check_credit_note = True and invoice_number is not Null')
			if res.account_id.account_selection == 'against_ref' and res.status_selection=='against_ref_writeoff' and res.type=='credit':
				cr.execute('update debit_note set check_cn_debit = False,receipt_amount=0.0 where check_process_dn = False and debit_note_no is not Null')
			if res.account_id.account_selection == 'security_deposit' and res.status_selection=='against_ref_writeoff' and res.type=='credit':
				cr.execute('update security_deposit set security_check_new_ref = False,partial_payment_amount=0.0 where security_check_process = False and pending_amount!=0.0')
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

	def process(self, cr, uid, ids, context=None): 
	# Credit Note process Button
		sales_receipts = self.pool.get('account.sales.receipts')
		sales_receipts_line = self.pool.get('account.sales.receipts.line')
		cr_total = dr_total = total = amt = 0.0
		move = ''
		post = []
		credit_invoice = ''
		today_date = datetime.now().date()
		flag = py_date = False
		credit_id = ''
		status=[]
		credit_note_date =''
		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			if res.credit_note_date:
				check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
				if check_bool:
					if res.credit_note_date != str(today_date):
						raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
				py_date = str(today_date + relativedelta(days=-5))
				if res.credit_note_date < str(py_date) or res.credit_note_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Date 5 days earlier from current date.'))
				credit_note_date=res.credit_note_date
			else:
				credit_note_date=datetime.now().date()
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
				if acc_selection == 'against_ref':
					for ln in credit_note_line.credit_outstanding_invoice:
						credit_id = ln.credit_invoice_id
						check_credit_note = ln.check_credit_note
						if check_credit_note == True:
							flag = True
						if check_credit_note==False:
							self.pool.get('invoice.adhoc.master').write(cr,uid,ln.id,{'credit_invoice_id':False})
					for ln in credit_note_line.debit_note_one2many:
						credit_id = ln.debit_credit_note_id
						check_debit_note = ln.check_cn_debit
						if check_debit_note == True:
							flag = True
					if flag == False:
						raise osv.except_osv(('Alert'),('No Invoice/Debit Note selected.'))
					if not credit_id and not (acc_selection == 'against_ref' and credit_note.status_selection == 'against_itds'):
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
		self.pms_validation(cr,uid,ids,context=context)
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
			financial_year =str(year1-1)+str(year1)
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
			seq_start = 1
			############## OLD Code to generate credit note number ################ 28-09-2017
			# if pcof_key and credit_note_id:
			# 	cr.execute("select cast(count(id) as integer) from credit_note where credit_note_no is not null and credit_note_date>='2017-07-01'  and  credit_note_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
			# 	temp_count=cr.fetchone()
			# 	if temp_count[0]:
			# 		count= temp_count[0]
			# 	seq=int(count+seq_start)
			# 	value_id = pcof_key + credit_note_id +  str(financial_year) +str(seq).zfill(5)
			# 	#value_id = pcof_key + credit_note_id +  str(year1) +str(seq_new).zfill(6)
			# 	existing_value_id = self.pool.get('credit.note').search(cr,uid,[('credit_note_no','=',value_id)])
			# 	if existing_value_id:
			# 		value_id = pcof_key + credit_note_id +  str(financial_year) +str(seq+1).zfill(5)
			
			############## NEW Code to generate credit note number ################# 28-09-2017
			credit_note_id=4
			financial_year=str(year1)
			if pcof_key and credit_note_id:
				pcof_key_list=pcof_key.split('P')
				like_variable=str(pcof_key_list[1])+str(credit_note_id)+str(financial_year)+'%'
				sql_var="select cast(count(id) as integer) from credit_note where credit_note_no is not null and credit_note_date>='2017-07-01' and credit_note_no ilike '"+like_variable+"' and credit_note_no not ilike '%\P%' and credit_note_no not ilike '%\CN%' and credit_note_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' "
				cr.execute(sql_var)
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key_list[1] + str(credit_note_id) +  str(financial_year) +str(seq).zfill(4)
				#value_id = pcof_key + credit_note_id +  str(year1) +str(seq_new).zfill(6)
				existing_value_id = self.pool.get('credit.note').search(cr,uid,[('credit_note_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key_list[1] + str(credit_note_id) +  str(financial_year) +str(seq+1).zfill(4)
			################## END #################
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
			move = self.pool.get('account.move').create(cr,uid,
				{
					'journal_id':journal_bank,
					'state':'posted',
					'date':date,
					'name':value_id,
					'partner_id':rec.customer_name.id if rec.customer_name.id else '',
					'narration':rec.narration if rec.narration else '',
					'voucher_type':'Credit Note'
				},context=context)
			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.credit_note_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,
							{
								'move_id':line1.id,
								'account_id':ln.account_id.id,
								'debit':ln.debit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_bank,
								'period_id':period_id,
								'date':date,
								'ref':value_id
							},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,
							{
								'move_id':line1.id,
								'account_id':ln.account_id.id,
								'credit':ln.credit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_bank,
								'period_id':period_id,
								'date':date,
								'ref':value_id
							},context=context)
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
			if creditnote_his.status_selection_new == 'against_advance':		
				status_selection1='Against Advance'
			for creditnote_line in creditnote_his.credit_note_one2many:
				amount=creditnote_line.debit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('credit.note.history').create(cr,uid,
				{
					'credit_note_his_many2one':curr_id,
					'credit_note_number':value_id,
					'credit_note_date':creditnote_date,
					'credit_note_type':status_selection1,
					'credit_note_amount':amount
				})
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
											if rec_itds.pending_amount != rec_itds.amount_receipt:
												status='printed'
												pending_status='pending'
												pending_amount=rec_itds.pending_amount - rec_itds.amount_receipt
												paid_amount=rec_itds.amount_receipt
											elif rec_itds.pending_amount == rec_itds.amount_receipt:
												status='paid'
												pending_status='paid'
												pending_amount=0.0
												paid_amount=rec_itds.amount_receipt
											else:
												status='paid'
												pending_status='paid'
												pending_amount=0.0
												paid_amount=rec_itds.amount_receipt
											grand_total += rec_itds.grand_total_amount
											cse_name = rec_itds.cse.name
											itds_cse = rec_itds.cse.id
											invoice_num += rec_itds.invoice_number
											invoice_date_concate += rec_itds.invoice_date
										self.pool.get('invoice.adhoc.master').write(cr,uid,rec_itds.id,
											{
												'pending_amount':pending_amount,
												'pending_status':pending_status,
												'status':status,
												'itds_writeoff_status':ln_itds.writeoff_status,
											})
										self.pool.get('invoice.receipt.history').create(cr,uid,
											{
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
												if rec_itds.paid_amount==rec_itds.amount_receipt:
													status='writeoff'
													pending_amount=rec_itds.paid_amount
												else:
													status='partially_writeoff'
													pending_amount=rec_itds.pending_amount + rec_itds.amount_receipt
													
											else :
													status='writeoff'
													pending_amount=rec_itds.paid_amount
											grand_total += rec_itds.grand_total_amount
											cse_name = rec_itds.cse.name
											itds_cse = rec_itds.cse.id
											invoice_num += rec_itds.invoice_number
											invoice_date_concate += rec_itds.invoice_date
											self.pool.get('invoice.adhoc.master').write(cr,uid,rec_itds.id,
												{
													'pending_amount':pending_amount,
													'pending_status':'pending',
													'status':status,
													'itds_writeoff_status':ln_itds.writeoff_status,
												})
											self.pool.get('invoice.receipt.history').create(cr,uid,
												{
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
							if ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'debit' and itds_flag:
								self.pool.get('itds.adjustment').create(cr,uid,
									{
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
										'added_by_cn':True
									})
							if ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'credit':
								pending_amount =0.0
								for rec_itds in ln_itds.revert_itds_one2many_one:
									if rec_itds.check == True:
										if ln_itds.writeoff_status == 'partially_writeoff':
											if rec_itds.pending_amt != rec_itds.partial_revert:
													pending_amount=rec_itds.pending_amt - rec_itds.partial_revert
													paid_amount=rec_itds.partial_revert
													total_revert = rec_itds.total_revert + rec_itds.partial_revert
											elif rec_itds.pending_amt == rec_itds.partial_revert :
													pending_amount=0.0
													paid_amount=rec_itds.pending_amt
													total_revert = rec_itds.total_revert + rec_itds.pending_amt
											else:
													pending_amount=0.0
													paid_amount=rec_itds.pending_amt
													total_revert = rec_itds.total_revert + rec_itds.pending_amt
											self.pool.get('itds.adjustment').write(cr,uid,rec_itds.id,
												{
													'pending_amt':pending_amount,
													'state':'fully_reversed',
													'partial_revert':0.0,
													'total_revert':total_revert
												})
		self.write(cr,uid,rec.id,{'state':'done','acc_status':''})
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
						if rec1.status_selection_new == 'against_ref_writeoff':
							if rec1.writeoff_status == 'partially_writeoff':
								pending_amount = chk.pending_amount - chk.writeoff_amount
								total_amount = chk.total_writeoff + chk.writeoff_amount
								writeoff_amount = chk.writeoff_amount
								payment_status = 'partially_writeoff'
								pending_status = 'pending'
								status         = 'partially_writeoff'
								check_process  = False
								if chk.writeoff_amount==chk.pending_amount:
									payment_status = 'writeoff' 
									pending_status = 'paid'
									status         = 'writeoff'
									check_process = True
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
							self.pool.get('invoice.receipt.history').create(cr,uid,
								{
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
									'invoice_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date() 
								})
							self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,
								{
									'pending_amount':pending_amount,
									'pending_status':pending_status,
									'status':status,
									'check_process_credit_note':check_process,
									'total_writeoff':total_amount,
									'writeoff_amount':0.0
								})
						if  rec1.status_selection_new =='against_ref_refund':
							if rec1.writeoff_status == 'partially_writeoff':
								if chk.paid_amount == chk.writeoff_amount:
									writeoff_amount = chk.paid_amount
									pending_amount =   chk.pending_amount + chk.paid_amount
									total_amount = chk.total_writeoff + chk.paid_amount
									payment_status = 'writeoff'
									pending_status = 'paid'
									status         = 'writeoff'
									check_process  = True
								else:
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
							self.pool.get('invoice.receipt.history').create(cr,uid,
								{
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
									'invoice_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date() 
								})
							self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,
								{
									'pending_amount':pending_amount,
									'pending_status':pending_status,
									'status':status,
									'check_process_credit_note':check_process,
									'total_writeoff':total_amount,
									'writeoff_amount':0.0
								}) 
						if rec1.status_selection_new == 'against_advance':
								if rec1.writeoff_status == 'partially_writeoff':
									if chk.pending_amount ==chk.writeoff_amount:
										pending_amount = 0.0
										total_amount = chk.total_writeoff + chk.paid_amount
										writeoff_amount = chk.paid_amount
										payment_status = 'writeoff'
										pending_status = 'paid'
										status         = 'paid'
										check_process  = True
									else:	
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
								self.pool.get('invoice.receipt.history').create(cr,uid,
									{
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
										'advance_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date()  
									})
								self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,
									{
										'pending_amount':pending_amount,
										'pending_status':pending_status,
										'status':status,
										'check_process_credit_note':check_process,
										'writeoff_amount':0.0
									})
						if rec1.status_selection_new == 'against_short_payment':
								payment_status ='paid' 
								self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,
									{
										'check_process_credit_note':True,
										'pending_amount':'0.0',
										'pending_status':'paid'
									})
								self.pool.get('invoice.receipt.history').create(cr,uid,
									{
										'credit_id_history':line_state.id,
										'invoice_receipt_history_id':chk.id,
										'invoice_paid_date':rec1.credit_note_date,
										'invoice_date':chk.invoice_date,
										'tax_rate':chk.tax_rate,
										'invoice_paid_amount':chk.pending_amount,
										'invoice_pending_amount':0.0,
										'invoice_number':chk.invoice_number,
										'service_classification':chk.service_classification,
										'cse':chk.cse.id
									})  
						if rec1.status_selection_new == 'against_itds':
							payment_status ='paid'
						pay_con_history =self.pool.get('payment.contract.history')
						srch_history = pay_con_history.search(cr,uid,[('invoice_number','=',chk.invoice_number)])
						if srch_history:
							for invoice_history in pay_con_history.browse(cr,uid,srch_history):
								pay_con_history.write(cr,uid,invoice_history.id,{'payment_status':payment_status})
				for chk in line_state.debit_note_one2many:
					if line_state.debit_note_one2many:
						check_debit_note = chk.check_cn_debit
						if check_debit_note == True:
							if rec1.status_selection_new == 'against_ref_writeoff':
								for debit_line in line_state.debit_note_one2many:
									if debit_line.check_cn_debit==True:
										debit_note_no=debit_line.debit_note_no									
										pending_amount=debit_line.credit_amount_srch-debit_line.receipt_amount
										srch_debit=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',debit_note_no)])
										for i in self.pool.get('debit.note').browse(cr,uid,srch_debit):
											pending_amount=i.pending_amount-i.receipt_amount
											paid_amount=i.receipt_amount+i.paid_amount
											# self.pool.get('debit.note').write(cr,uid,i.id,{'state_new':'open','credit_amount_srch':pending_amount})
											self.pool.get('invoice.receipt.history').create(cr,uid,
												{
													'check_dn':True,
													'invoice_receipt_history_debit_note_id':line_state.id,
													'invoice_number':i.debit_note_no,
													'invoice_pending_amount':pending_amount,
													'receipt_number':line_state.credit_id.credit_note_no,
													'invoice_paid_amount':i.receipt_amount,
													'invoice_paid_date':datetime.now().date(),
													'invoice_date':i.debit_note_date,
													'service_classification':i.service_classification,
													'tax_rate':i.tax_rate,
													'cse_char':i.cse,
												})
											if pending_amount!=0.0:
												cr.execute("update debit_note set pending_amount=%s,paid_amount=%s,state_new='open',check_process_dn='f' where id=%s",(pending_amount,paid_amount,i.id))	
											if pending_amount==0.0:
												cr.execute("update debit_note set pending_amount=%s,paid_amount=%s,state_new='paid',check_process_dn='t' where id=%s",(pending_amount,paid_amount,i.id))
				for rec_advance in line_state.credit_advance_one2many:
					if rec_advance.check_advance_against_ref == True:
						if rec1.status_selection_new == 'against_advance' :
							if rec_advance.advance_pending < rec_advance.partial_amt :
								raise osv.except_osv(('Alert'),('enter proper partial amount'))
							if rec1.writeoff_status == 'partially_writeoff' :
								if rec_advance.advance_pending==rec_advance.partial_amt:
									pending_amt = 0.0 
									refund_amt = rec_advance.advance_pending
								else:
									pending_amt=rec_advance.advance_pending-rec_advance.partial_amt
									refund_amt = rec_advance.partial_amt
							if rec1.writeoff_status == 'fully_writeoff' :
								pending_amt = 0.0 
								refund_amt = rec_advance.advance_pending
							receipt_id=receipt_no=''
							line_srch=sales_receipts_line.search(cr,uid,[('id','=',rec_advance.advance_id.id)])
							if line_srch:
									for i in sales_receipts_line.browse(cr,uid,line_srch):
										main_srch=sales_receipts.search(cr,uid,[('id','=',i.receipt_id.id)])
										for j in sales_receipts.browse(cr,uid,main_srch):
											receipt_no=j.receipt_no
											receipt_id=j.id
											sales_receipts.write(cr,uid,j.id,{'advance_pending':pending_amt})
										if pending_amt==0.0:
											sales_receipts_line.write(cr,uid,i.id,{'state':'finish'})
							self.pool.get('advance.sales.receipts').write(cr,uid,rec_advance.id,
								{
									'advance_pending':pending_amt,
									'check_advance_against_ref':True if pending_amt else False,
									'check_advance_against_ref_process':True if pending_amt else False
								})
							abc=self.pool.get('advance.receipt.history').create(cr,uid,
								{
									'advance_receipt_no':receipt_no if receipt_no else rec_advance.receipt_no,
									'advance_date':rec_advance.receipt_date,
									'cust_name':rec_advance.partner_id.id,
									'advance_refund_amount':refund_amt,
									'advance_pending_amount':pending_amt,
									'advance_receipt_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),'service_classification':rec_advance.service_classification,
									'advance_history_id':line_state.id,
									'history_advance_id':rec_advance.id,
									'receipt_id':receipt_id if receipt_id else False
								}) 
		for rec in self.browse(cr,uid,ids):
						for res in rec.credit_note_one2many:
								if res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'others':
									for line in res.branch_itds_one2many:
										self.pool.get('itds.adjustment').write(cr,uid,line.id,
											{
												'receipt_no':rec.credit_note_no,
												'receipt_date':rec.credit_note_date,
												'customer_name':rec.customer_name.id if rec.customer_name else '',
												'customer_name_char':rec.customer_name.name if rec.customer_name else '',
												'pending_amt':line.itds_amt,
												'state':'pending',
												'ou_id':rec.customer_name.ou_id if rec.customer_name else ''
											})
								if res.account_id.account_selection == 'security_deposit' and res.status_selection =='against_ref_writeoff' and res.type == 'credit':
										if res.cn_security_deposit:
											for line in res.cn_security_deposit:
												if line.security_check_new_ref:
													pending_amount=0.0
													security_check_process=False
													if line.pending_amount==line.partial_payment_amount:
														pending_amount=0.0
														security_check_process=True
													else:
														pending_amount=line.pending_amount-line.partial_payment_amount
													self.pool.get('security.deposit').write(cr,uid,line.id,
														{
															'security_check_process':security_check_process,
															'cn_security_id':res.id,
															'cse':line.cse.id,
															'emp_code':line.cse.emp_code,
															'pending_amount':pending_amount,
															'customer_name':rec.customer_name.id if rec.customer_name else '',
															'customer_id':rec.customer_name.ou_id if rec.customer_name else '',
														})
								if res.account_id.account_selection == 'security_deposit' and res.status_selection =='against_ref_writeoff' and res.type == 'debit':
										sec_id=self.pool.get('security.deposit').create(cr,uid,
											{
												'cn_security_id':res.id,
												'cse':sd_cse,
												'emp_code':sd_emp_code,
												'ref_no':rec.credit_note_no,
												'ref_date':rec.credit_note_date,
												'pending_amount':sd_amount if sd_amount else res.debit_amount,
												'ref_amount':sd_amount if sd_amount else res.debit_amount,
												'customer_name':rec.customer_name.id if rec.customer_name else '',
												'customer_id':rec.customer_name.ou_id if rec.customer_name else '',
											})
										self.pool.get('security.deposit.history').create(cr,uid,
											{ 
												'security_deposit_id':sec_id,
												'ref_no':rec.credit_note_no,
												'customer_name':rec.customer_name.id if rec.customer_name else '',
												'ref_amount':sd_amount if sd_amount else res.debit_amount,
												'pending_amount':sd_amount if sd_amount else res.debit_amount,
												'partial_payment_amount':sd_amount if sd_amount else res.debit_amount,
												'ref_date':rec.credit_note_date,
												'receipt_date':rec.credit_note_date if rec.credit_note_date else '',
												'new_sec':True
											})
		credit_note_data = self.browse(cr,uid,ids[0])
		credit_note_one2many = credit_note_data.credit_note_one2many
		for note_line_id in credit_note_one2many:
			account_selection = note_line_id.account_id.account_selection
			inv_selected = note_line_id.inv_selected
			type_credit_note = note_line_id.type
			if account_selection in ['advance','advance_against_ref','against_ref','sundry_deposit'] and inv_selected != True and type_credit_note=='credit':
				raise osv.except_osv(('Alert'),('Select invoice/advance reference!'))
		self.write(cr,uid,credit_note_data.id,{'gst_credit_note':True})
		self.delete_draft_records(cr,uid,ids,context=context) 
		self.sync_writeoff(cr,uid,ids,context=context) 
		self.sync_credit_note_history(cr,uid,ids,context=context)
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


	def print_report(self,cr,uid,ids,context=None):
		total=total_service=tax_amt =itds_amount_dr =total_tax_amt = 0.0
		receipt_number_itds_no_str = ''
		receipt_number_itds =[]
		debit_note_list = []
		tax_name=tax_amount=''
		flag = False
		report_name = cred_acc_name = ''
		cr.execute('delete from credit_note_report b  where b.report_id=%(val)s',{'val':ids[0]})
		for res in self.browse(cr,uid,ids):
			if uid != 1:
				file_format='pdf'
				doc=str(res.credit_note_no)
				doc_name='credit_note'
				self.pool.get('user.print.detail').update_rec(cr,uid,file_format,doc,doc_name)
			for i in res.credit_note_one2many:
				if i.account_id.account_selection == 'itds_receipt' and i.type =='debit' :
					flag = True
					itds_amount_dr = i.debit_amount
			for i in res.credit_note_one2many:
				if i.account_id.account_selection==False and i.account_id.product_id != False:
					if i.type=='debit':
						total += i.debit_amount
					else:
						total += i.credit_amount
					self.pool.get('credit.note.report').create(cr,uid,
						{
							'report_id':res.id,
							'account_id':i.account_id.id,
							'type':i.type,
							'credit_amount':i.credit_amount,
							'debit_amount':i.debit_amount
						})
				if i.account_id.account_selection=='tax':
					if i.type=='debit':
						tax_amt = i.debit_amount
					else:
						tax_amt = i.credit_amount
					total_tax_amt += tax_amt	
					tax_name +='\n'+i.account_id.name
					tax_amount +='\n'+str(format(tax_amt,'.2f'))
				if flag :
						if i.account_id.account_selection== 'against_ref':
							if i.credit_note_itds_history_one2many:
								for itds in i.credit_note_itds_history_one2many:
									receipt_number_itds.append (itds.invoice_number)
									receipt_number_itds_no_str = ' / '.join(filter(bool,receipt_number_itds))
									total += itds.invoice_paid_amount
									self.pool.get('credit.note.report').create(cr,uid,
										{
											'report_id':res.id,
											'itds_print':'TDS on Contract Receipts / Int.({receipt_number}) '.format(receipt_number=receipt_number_itds_no_str),
											'type':i.type,
											'credit_amount':itds.invoice_paid_amount,
											'debit_amount':itds_amount_dr
										}) 
									receipt_number_itds=[]
				if i.account_id.account_selection== 'advance':	
					for adavnce in i.advance_history_one2many:
						receipt_number_itds.append (adavnce.advance_receipt_no)
					receipt_number_itds_no_str = ' / '.join(filter(bool,receipt_number_itds))
					total += i.debit_amount
					self.pool.get('credit.note.report').create(cr,uid,
						{
							'report_id':res.id,
							'itds_print':'Advance Receipts ({receipt_number}) '.format(receipt_number=receipt_number_itds_no_str),
							'type':i.type,
							'credit_amount':i.credit_amount,
							'debit_amount':i.debit_amount
						})
				if i.account_id.account_selection== 'itds_receipt':
					if i.revert_itds_one2many_one:
						for itds_report in i.revert_itds_one2many_one:
							if itds_report.check == True:
								receipt_number_itds.append (itds_report.receipt_no)
						receipt_number_itds_no_str = ' / '.join(filter(bool,receipt_number_itds))
						total += i.credit_amount
						self.pool.get('credit.note.report').create(cr,uid,
							{
								'report_id':res.id,
								'itds_print':'TDS on Contract Receipts / Int.({receipt_number_itds}) '.format(receipt_number_itds=receipt_number_itds_no_str),
								'type':i.type,
								'credit_amount':i.credit_amount,
								'debit_amount':i.debit_amount
							})
				if i.account_id.account_selection== 'against_ref':
					if i.debit_note_history_one2many:
						for dn in i.debit_note_history_one2many:
							if dn.check_dn == True:
								debit_note_list.append (dn.invoice_number)
						search_debit_note=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','in',debit_note_list)])
						if search_debit_note:
							for x in self.pool.get('debit.note').browse(cr,uid,search_debit_note):
								if x.debit_note_one2many:
									for deb in x.debit_note_one2many:
										if deb.type=='credit':
											cred_acc_name=deb.account_id.name		
						receipt_number_itds_no_str = ' / '.join(filter(bool,receipt_number_itds))
						total += i.credit_amount
						
						self.pool.get('credit.note.report').create(cr,uid,{
							'report_id':res.id,
							'itds_print':cred_acc_name,
							'type':i.type,
							'credit_amount':i.credit_amount,
							'debit_amount':i.debit_amount})
				if i.account_id.account_selection == 'against_ref':
					if i.account_id.gst_applied == True:
						report_name = 'gst_credit_note'
					else:
						report_name = 'credit_note'
			total_service = format(total + total_tax_amt,'.2f')
			s = self.write(cr,uid,res.id,
				{
					'pms_total':str(format(total,'.2f')),
					'tax_name':tax_name,
					'tax_amount':tax_amount,
					'pms_grand_total':total_service
				})
			data = self.pool.get('credit.note').read(cr, uid, [res.id],context)
			datas = {
						'ids': ids,
						'model': 'credit.note',
						'form': data
					}

		credit_note_data = self.browse(cr,uid,ids[0])
		if report_name == 'gst_credit_note_st':
			return {
						'type': 'ir.actions.report.xml',
						'report_name': 'gst_credit_note',
						'datas': datas,
					}
		else:
			return {
						'type': 'ir.actions.report.xml',
						'report_name': 'credit_note',
						'datas': datas,
					}
credit_note()

class credit_note_new(osv.osv):

	_inherit = 'credit.note.new'
	_order = 'credit_note_date desc'
	

credit_note_new()


class credit_note_line(osv.osv):
	_inherit='credit.note.line'
	_columns={

		'debit_note_one2many':fields.one2many('debit.note','debit_credit_note_id','Debit Note'),#
		'debit_note_history_one2many':fields.one2many('invoice.receipt.history','invoice_receipt_history_debit_note_id','Debit Note'),
	}

	def save_outstanding_invoice(self, cr, uid,ids, context=None):
		count = 0.0
		flag = False
		type1 = ""
		invs = []
		inv_flag=False
		check_invoice=False
		for res in self.browse(cr,uid,ids):
			cr_amount = res.credit_amount
			dr_amount = res.debit_amount
			type1 = res.type

			if res.credit_outstanding_invoice == [] and res.debit_note_one2many == []:
				raise osv.except_osv(('Alert'),('No line to proceed.'))
			for line in res.credit_outstanding_invoice:
				if line.check_credit_note == True:
					inv_flag=True
					check_invoice=True
					if res.status_selection == 'against_ref_writeoff' :
						if res.credit_id.writeoff_status == 'partially_writeoff':
							if not line.writeoff_amount:
									raise osv.except_osv(('Alert'),('Enter writeoff Amount'))
							# if (line.writeoff_amount - line.pending_amount) == 0.0:
							# 			raise osv.except_osv(('Alert'),('Please select fully writeoff'))
							if line.writeoff_amount > line.pending_amount:
										raise osv.except_osv(('Alert'),('Writeoff amount should be less than Invoice pending Amount'))
									
							count = count + line.writeoff_amount
							
						# if res.credit_id.writeoff_status == 'fully_writeoff':
								
						# 	if line.writeoff_amount > line.pending_amount:
						# 				raise osv.except_osv(('Alert'),('Writeoff amount should be less than Invoice pending Amount'))
										
						# 	count = count + line.pending_amount
						if check_invoice:
							self.pool.get('invoice.adhoc.master').write(cr,uid,line.id,{'check_invoice':True})
					if res.status_selection == 'against_ref_refund':
						if res.credit_id.writeoff_status == 'partially_writeoff':
							if not line.writeoff_amount:
									raise osv.except_osv(('Alert'),('Enter writeoff Amount'))
							# if (line.writeoff_amount - line.paid_amount) == 0.0:
							# 			raise osv.except_osv(('Alert'),('Please select fully writeoff'))
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
							# if (line.writeoff_amount - line.pending_amount) == 0.0:
							# 	raise osv.except_osv(('Alert'),('Please select fully writeoff'))
							if (line.pending_amount-line.writeoff_amount) < 0.0:
								raise osv.except_osv(('Alert'),('Enter proper Writeoff Amount'))

							count = count + line.writeoff_amount

						if res.credit_id.writeoff_status == 'fully_writeoff':
							if line.writeoff_amount != line.pending_amount:
											raise osv.except_osv(('Alert'),('Writeoff amount should be less than Invoice Paid Amount'))
							count = count + line.pending_amount
					invs.append(line.id)	
			for line in res.debit_note_one2many:
				if line.check_cn_debit == True:
					inv_flag=True
					# check_invoice=True
					if res.status_selection == 'against_ref_writeoff':
						if line.receipt_amount == 0.0:
							raise osv.except_osv(('Alert'),('Payment amount cannot be zero'))
						if line.receipt_amount > line.pending_amount:
							raise osv.except_osv(('Alert'),('Payment amount cannot be greater than Debit Note pending amount'))
						count = count + line.receipt_amount
					invs.append(line.id)
			if inv_flag == False:
				raise osv.except_osv(('Alert'),('Please select either Invoice or Debit Note.'))
			if type1== 'debit':
				self.write(cr,uid,res.id,{'debit_amount':count})
			else:
				self.write(cr,uid,res.id,{'credit_amount':count})
			if len(invs) > 0:
				self.write(cr,uid,ids[0],{'inv_selected':True})
			else:
				self.write(cr,uid,ids[0],{'inv_selected':False})
			
			
		return {'type': 'ir.actions.act_window_close'}

	def show_details(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			credit_id = res.credit_id.id
			search = self.pool.get('credit.note').search(cr,uid,[('id','=',credit_id)])
			for rec in self.pool.get('credit.note').browse(cr,uid,search):
				cust_id = rec.customer_name.id
				if cust_id:
					if res.status_selection == 'against_ref_writeoff':
						srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[
									('status','in',('open','printed','partially_writeoff')),
									('partner_id','=',cust_id),('invoice_number','!=',''),
									('check_process_credit_note','=',False),('pending_amount','!=',0.0)
									])

						for credit in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
							if credit.partner_id.id == cust_id:
								self.pool.get('invoice.adhoc.master').write(cr,uid,credit.id,{'credit_invoice_id':res.id})

						srch_debit_note = self.pool.get('debit.note').search(cr,uid,[
											('customer_name','=',cust_id),
											('state_new','=','open'),
											('debit_note_no','!=',None),
											('pending_amount','!=',0.0),
											('check_process_dn','=',False)
											])
						 
						for debit in self.pool.get('debit.note').browse(cr,uid,srch_debit_note):
							if debit.customer_name.id == cust_id:
								self.pool.get('debit.note').write(cr,uid,debit.id,{'debit_credit_note_id':res.id})

					# if res.status_selection == 'against_short_payment':####short payment
					# 	srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[
					# 							('status','=','paid'),
					# 							('partner_id','=',cust_id),
					# 							('invoice_number','!=',''),
					# 							('check_process_credit_note','=',False),
					# 							('pending_status','=','pending')])
					# 	for credit in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
					# 		if credit.partner_id.id == cust_id:
					# 			self.pool.get('invoice.adhoc.master').write(cr,uid,credit.id,{'credit_invoice_id':res.id})
								
					if res.status_selection == 'against_itds':####itds
						srch1 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
												('status','=','paid'),
												('partner_id','=',cust_id),
												('invoice_number','!=',''),
												('check_process_credit_note','=',False),
												('pending_status','=','pending')])
						for credit in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch1):
							if credit.partner_id.id == cust_id:
								self.pool.get('invoice.adhoc.master').write(cr,uid,credit.id,{'credit_invoice_id':res.id})
								

					if res.status_selection == 'against_cancellation':
						srch1 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
											('status','in',('open','printed')),
											('partner_id','=',cust_id),
											('invoice_number','!=',''),
											('check_process_credit_note','=',False)
											])
						for credit in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch1):
							if credit.partner_id.id == cust_id:
								self.pool.get('invoice.adhoc.master').write(cr,uid,credit.id,{
											'credit_invoice_id':res.id})


					if res.status_selection == 'against_ref_refund':
						srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[
									('status','in',('open','printed','paid','partially_writeoff')),
									('pending_status','in',('pending','paid')),
									('partner_id','=',cust_id),
									('invoice_number','!=',''),
														('check_process_credit_note','=',False)])#added  partially writeoff
						for credit in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
							if credit.partner_id.id == cust_id:
								self.pool.get('invoice.adhoc.master').write(cr,uid,credit.id,{'credit_invoice_id':res.id})

					if res.status_selection == 'against_advance':	# Sagar fro Advance credit note >>>>>>>>>>>>
						srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[
											        	('status','in',
											('open','printed','partially_writeoff')),
											('partner_id','=',cust_id),
											('invoice_number','!=',''),
													('check_process_credit_note','=',False),
													('pending_amount','>',0.0)])
						for credit in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
							if credit.partner_id.id == cust_id:
								self.pool.get('invoice.adhoc.master').write(cr,uid,credit.id,{'credit_invoice_id':res.id})
										##<<<<<<<<<<<<<<<<<<<<<
		return True

	def add(self, cr, uid, ids, context=None):
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
					form_view=models_data.get_object_reference(cr, uid, 'gst_accounting', 'gst_account_credit_against_ref_form')
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
					
			# elif res.account_id.account_selection=='against_ref' and res.status_selection=='against_short_payment': ##short payment
			# 	models_data=self.pool.get('ir.model.data')
			# 	self.show_details(cr,uid,ids,context=context)
			# 	form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_for_short_payment')
			# 	return {
			# 		'name': ("Outstanding Invoice"),'domain': '[]',
			# 		'type': 'ir.actions.act_window',
			# 		'view_id': False,
			# 		'view_type': 'form',
			# 		'view_mode': 'form',
			# 		'res_model': 'credit.note.line',
			# 		'target' : 'new',
			# 		'res_id':int(res_id),
			# 		'views': [(form_view and form_view[1] or False, 'form'),
			# 				   (False, 'calendar'), (False, 'graph')],
			# 		'domain': '[]',
			# 		'nodestroy': True,
					   # }              

			elif  res.status_selection == 'against_itds' and res.type == 'credit' and acc_selection == 'against_ref':
				models_data=self.pool.get('ir.model.data')
				self.show_itds_details_against_ref(cr,uid,ids,context=context)

				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'itds_against_ref_form')#27oct15
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
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_for_itds_payment')
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
				# form_view=models_data.get_object_reference(cr,uid,'account_sales_branch', 'account_other_branch_itds_collection')
				form_view=models_data.get_object_reference(cr,uid,'account_sales_branch', 'itds_against_ref_form')
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
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_form')
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
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_against_ref_form')
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
				form_view=models_data.get_object_reference(cr,uid,'account_sales_branch','against_advance_credit_note_form')
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
				
			elif res.status_selection == 'against_ref_writeoff' and acc_selection =='security_deposit' and res.type == 'credit':
				models_data=self.pool.get('ir.model.data')
				self.show_security_deposit(cr,uid,ids,context=context)
				form_view=models_data.get_object_reference(cr,uid,'account_sales_branch','securit_deposit_credit_note_form')
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


class debit_note(osv.osv):
	_inherit='debit.note'
	_columns={

		'debit_credit_note_id':fields.many2one('credit.note.line','Credit Note Line'),
		'check_cn_debit':fields.boolean(''),
		'tax_rate':fields.char('Tax Rate',size=15),
	}
debit_note()


class invoice_receipt_history(osv.osv):
	_inherit='invoice.receipt.history'
	_columns={
		'invoice_receipt_history_debit_note_id':fields.many2one('credit.note.line','Invoice Receipt history'),
		'cse_char':fields.char('CSE',size=200),
		'check_dn':fields.boolean(''),
	}
invoice_receipt_history()