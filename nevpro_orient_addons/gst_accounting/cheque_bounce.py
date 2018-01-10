from datetime import date,datetime, timedelta
from dateutil.relativedelta import *
from dateutil.relativedelta import relativedelta
from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
import calendar
import re
from base.res import res_partner
from datetime import datetime
import decimal_precision as dp

class cheque_bounce(osv.osv): 
	_inherit = 'cheque.bounce'
	_order = 'payment_date desc'

	def process(self, cr, uid, ids, context=None): 
	### Cheque Bounce Process
		sales_receipt = self.pool.get('account.sales.receipts')
		invoice_history = self.pool.get('invoice.receipt.history')
		invoice_adhoc_master = self.pool.get('invoice.adhoc.master')
		itds_adjustment = self.pool.get('itds.adjustment')
		security_deposit = self.pool.get('security.deposit')
		cheque_bounce_line = self.pool.get('cheque.bounce.line')
		iob_one = self.pool.get('iob.one.sales.receipts')

		count = count1 = 0
		flag1 =flag3 =flag = py_date = False
		cr_total = dr_total = chk_account_selection = 0.0   ###23de15
		move = grand_total = invoice_date = invoice_number = iob_one_id = neft_id = ''
		post=[]
		status=[]
		advance_id = invoice_id_receipt = advance_ref_id = cheque_no = ''
		neft_amount = cheque_amount = adv_against_line=0.0
		ref_amount = ref_amount_adv = ref_amount_cofb = 0.0
		grand_total_against = grand_total_advance = grand_total = 0.0
		today_date = datetime.now().date()

		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			if res.payment_date:
			        check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
			        if check_bool:
			                if res.payment_date != str(today_date):
        				        raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
        			else:
        			        py_date = str(today_date + relativedelta(days=-5))
				        if res.payment_date < str(py_date) or res.payment_date > str(today_date):
				        	raise osv.except_osv(('Alert'),('Kindly select Receipt Date 5 days earlier from current date.'))
				payment_date=res.payment_date	
			else:
				payment_date=datetime.now().date()
			for line in res.cheque_bounce_lines:
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
				account_id = line.account_id.id
				types = line.type

				if account_id:
					temp = tuple([account_id])
					post.append(temp)
					for i in range(0,len(post)):
						for j in range(i+1,len(post)):
							if post[i][0] == post[j][0]:
								raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
				
				acc_selection = line.account_id.account_selection #23dec15
				
				if acc_selection in ['iob_one','iob_two','cash']:
					chk_account_selection +=1
					
			if chk_account_selection ==0.0:#23dec15
					raise osv.except_osv(('Alert'),('Please select proper account name')) 
										
			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
				
		for record in self.browse(cr,uid,ids):
			itds_flag = itds_flag1 = sd_flag = sd_flag1 = iob_flag = False
			
#--------------------------- Handeling Alerts for ITDS & SD
			for ln in record.cheque_bounce_lines:# HHH 12apr ITDS cheque bounce
				if ln.itds_cheque_bounce_one2many:
					itds_flag1 = True
					for itds_line in ln.itds_cheque_bounce_one2many:
						if itds_line.check:
							itds_flag = True
					
				if ln.sd_cheque_bounce_one2many:
					sd_flag1 = True
					for sd_line in ln.sd_cheque_bounce_one2many:
						if sd_line.security_check_new_ref:
							sd_flag = True

				if sd_flag == False and sd_flag1 == True :
					raise osv.except_osv(('Alert'),('No Security Deposit Entry selected.'))
				if itds_flag == False and itds_flag1 == True:
					raise osv.except_osv(('Alert'),('No ITDS Entry selected.'))
#-------------------------------------------------------------

			for ln in record.cheque_bounce_lines:
				acc_selection = ln.account_id.account_selection
				account_name = ln.account_id.name
				payment_method = ln.payment_method
				if payment_method == 'cheque':
					if acc_selection == 'iob_one':
						cheque_amount = 0.0
						for iob_one_line in ln.iob_one_cheque_bounce_one2many1:
							if iob_one_line.iob_one_check == True:
								iob_flag = True
								iob_one_id = iob_one_line.iob_one_cheque_bounce_id2.id
								cheque_no = iob_one_line.cheque_no
								cheque_amount += iob_one_line.cheque_amount
								
								iob_one.write(cr,uid,iob_one_line.id,{'iob_one_cheque_bounce_process':True})
								
						if iob_flag == False and not ln.IOB_import_cheque :
							raise osv.except_osv(('Alert'),('No Cheque selected.'))
		
						if not iob_one_id and not ln.IOB_import_cheque :
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
							
						elif iob_one_id:
							if ln.debit_amount:
								if  cheque_amount != ln.debit_amount:
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if ln.credit_amount:
								if  cheque_amount  != ln.credit_amount:
									raise osv.except_osv(('Alert'),('Credit amount should be equal'))

				if payment_method == 'neft':
					if acc_selection == 'iob_one':
						cheque_amount = 0.0
						for iob_one_line in ln.neft_cheque_bounce_one2many1:
							if iob_one_line.neft_check_id == True:
								neft_check_id_flag = True
								neft_check_id = iob_one_line.neft_cheque_bounce_id1.id
								neft_no = iob_one_line.pay_ref_no
								neft_amount += iob_one_line.neft_amount
								
								self.pool.get('neft.sales.receipts').write(cr,uid,iob_one_line.id,{'neft_cheque_bounce_process':True})
								
						if neft_check_id_flag == False:
							raise osv.except_osv(('Alert'),('No NEFT/RTGS selected.'))
		
							
						elif neft_check_id:
							if ln.debit_amount:
								if neft_amount != ln.debit_amount:
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if ln.credit_amount:
								if neft_amount  != ln.credit_amount:
									raise osv.except_osv(('Alert'),('Credit amount should be equal'))

				if acc_selection == 'against_ref':
					grand_total_against = invoice_pending_amount = 0.0
					invoice_number = ''
					
#---# add code for cheque bounce which are not present in ERP >>>>>>>>>>start------>> SSS 3Mar

					for invoice_line in ln.debited_invoice_line_new: # invoice receipt history
						if invoice_line.cheque_bounce_boolean == True:
							invoice_id_receipt =  invoice_line.debit_invoice_id_cheque_bounce_new.id
							flag = True
							count= count + 1
							grand_total_against += invoice_line.invoice_paid_amount
							invoice_history.write(cr,uid,invoice_line.id,{
								'cheque_bounce_boolean_process':True,
								'cheque_bounce_date':res.payment_date if res.payment_date else datetime.now().date() })
							
							if invoice_line.invoice_number != invoice_number:
								invoice_number = invoice_line.invoice_number
								invoice_pending_amount = invoice_line.invoice_receipt_history_id.pending_amount
							invoice_pending_amount = invoice_pending_amount + invoice_line.invoice_paid_amount
							invoice_adhoc_master.write(cr,uid,invoice_line.invoice_receipt_history_id.id,{
								'pending_amount':invoice_pending_amount,
								'check_process_invoice':False,
								'status':'printed',
								'pending_status':'pending'})
					
					if ln.debited_invoice_line: ### invoice_adhoc_master
						for rec in ln.debited_invoice_line:
							if rec.cheque_bounce_bool:
								flag = True
								invoice_id_receipt= True
								invoice_history.create(cr,uid,{
									'invoice_paid_amount':rec.partial_payment_amount,
									'service_classification':rec.service_classification,
									'invoice_date':rec.invoice_date,
									'invoice_number':rec.invoice_number,
									'invoice_receipt_history_id':rec.id,
									'tax_rate':rec.tax_rate,
									'cheque_bounce_boolean_process':True,
									'cheque_bounce_boolean':True,
									'debit_invoice_id_cheque_bounce_new':ln.id,
									'cse':rec.cse.id,
									'cheque_bounce_date':res.payment_date if res.payment_date else datetime.now().date() })
								
								invoice_pending_amount = rec.pending_amount + rec.partial_payment_amount
								invoice_adhoc_master.write(cr,uid,rec.id,{
									'pending_amount':invoice_pending_amount,
									'check_process_invoice':False,
									'status':'printed' if rec.status not in ('writeoff','partially_writeoff') else rec.status ,
									'pending_status':'pending',
									'cheque_bounce_bool_process':True})
								
					for cfob_invoice in ln.cfob_line: ### 3Mar
						if cfob_invoice.cfob_boolean_cb:
							flag1 = True
							invoice_id_receipt= True
							self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_invoice.id,{'cfob_boolean_process_cb':True})
						else :
							self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_invoice.id,{'cfob_id':None})
					
					for debit_invoice in ln.debit_note_one2many:
						if debit_invoice.dn_cheque_bounce:
							flag3= True
							invoice_id_receipt = True
							pending_amount=debit_invoice.credit_amount_srch+debit_invoice.pending_amount
							paid_amount=debit_invoice.paid_amount-debit_invoice.credit_amount_srch
							self.pool.get('debit.note').write(cr,uid,debit_invoice.id,{'dn_cheque_bounce_process':True,'state_new':'open','paid_amount':paid_amount,'pending_amount':pending_amount})
						else :
							self.pool.get('debit.note').write(cr,uid,debit_invoice.id,{'cb_debit_id':None})
							
					if flag == False and flag1 == False and flag3 == False:
								print "This is where we should be"
								raise osv.except_osv(('Alert'),('No invoice selected.'))
				
					if not invoice_id_receipt:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
#-------------------------------------------------------------------------------->> sss 3Mar end
				for itds_line in ln.itds_cheque_bounce_one2many: # for ITDS entry
					if itds_line.check:
						itds_adjustment.write(cr,uid,itds_line.id,{'cheque_bounce_boolean_process':True,})
				
				for sd_line in ln.sd_cheque_bounce_one2many: # for SD Entry
					if sd_line.security_check_new_ref:
						security_deposit.write(cr,uid,sd_line.id,{'cheque_bounce_boolean_process':True,
																# 'ref_amount':0.0,
																# 'pending_amount':0.0,
																})

#sagar 14 Dec for advance cheque bounce>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
				advance_flag = False
				if acc_selection == 'advance':
					for advance_line in ln.advance_cheque_bounce_one2many:
						if advance_line.cheque_bounce_boolean == True:
							advance_id_receipt =  advance_line.id
							advance_flag = True

							self.pool.get('advance.sales.receipts').write(cr,uid,advance_line.id,{
								'cheque_bounce_boolean_process':True,
								'advance_pending':0.0,
								'cheque_bounce_date':res.payment_date if res.payment_date else datetime.now().date(), })

							sales_receipt.write(cr,uid,advance_line.advance_id.receipt_id.id,{'advance_pending':0.0})

					if advance_flag == False:
						raise osv.except_osv(('Alert'),('No advance selected.'))
	
					if not advance_id_receipt:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

#<<<<<<<<<<<<
		for rec in self.browse(cr,uid,ids):
		### get payment number
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'cheque_bounce_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'cheque_bounce_tree')
			
			today_date = datetime.now().date()

			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
			
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','cheque.bounce')])
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
			financial_year = str(year1-1)+str(year1)
			financial_start_date = str(start_year)+'-04-01'

			financial_end_date = str(end_year)+'-03-31'
			company_id=self._get_company(cr,uid,context=None)
			if company_id:
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					if comp_id.cheque_bounce_payment_id:
						cheque_bounce_payment_id = comp_id.cheque_bounce_payment_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			seq_start = 1
			if pcof_key and cheque_bounce_payment_id:
				cr.execute("select cast(count(id) as integer) from cheque_bounce where state not in ('draft') and payment_no is not null and  payment_date>='2017-07-01'  and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				# seq_new=self.pool.get('ir.sequence').get(cr,uid,'cheque.bounce')
				value_id = pcof_key + cheque_bounce_payment_id +  str(financial_year) +str(seq).zfill(5)
				#value_id = pcof_key + cheque_bounce_payment_id +  str(year1) +str(seq_new).zfill(6)
				existing_value_id = self.pool.get('cheque.bounce').search(cr,uid,[('payment_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + cheque_bounce_payment_id +  str(financial_year) +str(seq+1).zfill(5)
				########################
			self.write(cr,uid,ids,{'payment_no':value_id,'payment_date': payment_date,'voucher_type':'Payment - CB'})
			date = payment_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id

			srch_jour_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
			for jour_acc in self.pool.get('account.journal').browse(cr,uid,srch_jour_acc):
				journal_id = jour_acc.id

			srch_neft_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','NEFT/RTGS')])
			for neft_acc in self.pool.get('account.journal').browse(cr,uid,srch_neft_acc):
				neft_id = neft_acc.id

			srch_jour_cash = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Cash')])
			for jour_cash in self.pool.get('account.journal').browse(cr,uid,srch_jour_cash):
				journal_cash = jour_cash.id

			move = self.pool.get('account.move').create(cr,uid,{'journal_id':journal_id,
									'state':'posted',
									'date':date,
									'name':value_id,
									'narration':rec.narration if rec.narration else '',
									'voucher_type':'Payment - CB',
									},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.cheque_bounce_lines:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
											'account_id':ln.account_id.id,
											'debit':ln.debit_amount,
											'name':rec.partner_id.name if rec.partner_id.name else '',
											'journal_id':journal_id,
											'period_id':period_id,
											'date':date,
											'ref':value_id},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
											'account_id':ln.account_id.id,
											'credit':ln.credit_amount,
											'name':rec.partner_id.name if rec.partner_id.name else '',
											'journal_id':journal_id,
											'period_id':period_id,
											'date':date,
											'ref':value_id},context=context)

			invoice_number = invoice_no = invoice_date_concate = ''
			grand_total = 0

			srch1 =  self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',invoice_number)])
			if srch1:
				for st in self.pool.get('payment.contract.history').browse(cr,uid,srch1): 
					self.pool.get('payment.contract.history').write(cr,uid,st.id,{'payment_status':'printed'})

			self.sync_invoice_update_state(cr,uid,ids,context=context)
			self.write(cr,uid,rec.id,{'state':'done'})

			for state_line in rec.cheque_bounce_lines:
				cheque_bounce_line.write(cr,uid,state_line.id,{'state':'done'})

		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
		return  {
			'name':'Cheque Bounce',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'cheque.bounce',
			'res_id':rec.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
			}

cheque_bounce()