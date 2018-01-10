from datetime import date,datetime, timedelta
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
from calendar import monthrange

class account_journal_voucher(osv.osv):
	_inherit = 'account.journal.voucher'
	_order = 'date desc'
	_columns = {
		'jv_month':fields.char('JV Month',size=10),
	}
	_defaults = {
		'jv_month':'',
	}

	def process(self,cr,uid,ids, context=None ):# Journal Voucher Process 28JAN
		cr.execute("update invoice_adhoc_master iam set cse=(select cse_contract from inspection_costing_line where contract_id1=iam.contract_no limit 1) where cust_name ilike 'Pest Control%' and invoice_date between '2017-03-01' and '2017-05-31' and iam.contract_no is not null")
		cr.commit()
		post=[]
		grand_total = grand_total_against = pending_amt = cbob_total = dr_total = cr_total = 0.0
		ref_amount_security = pending_amt = pay_amount = 0.0
		cfob_id = date = sundry_jv_id = security_jv_id = cbob_id = invoice_id_journal = invoice_no = ''
		invoice_num = invoice_date_concate = ''
		count = 0
		today_date = datetime.now().date()
		flag = py_date = sec_flag = sec_flag_credit = sec_flag_others = sun_flag = cbob_flag = debit_flag = False
		#############################Validation done for the Advance to staff
		advance_append_list =[]
		account_account_obj = self.pool.get('account.account')
		primary_cost_category_obj = self.pool.get('primary.cost.category')
		o = self.browse(cr,uid,ids[0])
		for line in o.journal_voucher_one2many:
			main_id = line.account_id.id
			line_id = line.id
			advance_account_check = account_account_obj.browse(cr,uid,main_id)
			advance_expence_check_val = advance_account_check.advance_expence_check
			advance_staff_check_val = advance_account_check.advance_staff_check
			if advance_staff_check_val == True and advance_expence_check_val == False:
				search_id = primary_cost_category_obj.search(cr,uid,[('journal_primary_cost_id','=',line_id)])
				if len(search_id) == 0:
						raise osv.except_osv(('Alert'),('Primary Cost Category are not added in Advance to staff account.'))
		#####################################################################		
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
				check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
				if check_bool:
			        	if res.date != str(today_date):
				    	   	raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
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
				count=0
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name
				customer_name = res.customer_name.name
				if line.invoice_cbob_one2many and not customer_name:
					raise osv.except_osv(('Alert'),('Please Enter Customer Name!'))
				if line.cbob_one2many and not customer_name:
					raise osv.except_osv(('Alert'),('Please Enter Customer Name!'))
				if line.journal_voucher_history_one2many and not customer_name:
					raise osv.except_osv(('Alert'),('Please Enter Customer Name!'))
				if line.cfob_jv_one2many and not customer_name:
					raise osv.except_osv(('Alert'),('Please Enter Customer Name!'))
				if line.cbob_advance_one2many and not customer_name:
					raise osv.except_osv(('Alert'),('Please Enter Customer Name!'))
				
				if acc_selection == 'against_ref':
					if line.customer_name.name == 'CFOB': ##### CFOB Entry 
						cfob_amount = 0.0
						branch_name = []
						i = 0
						j = 1
						if line.cfob_jv_one2many: 
							for cfob_line in line.cfob_jv_one2many:
								cfob_id = cfob_line.cfob_jv_id
								if cfob_line.check_cfob == True :
									branch_name.append(cfob_line.branch_name.name)
									cfob_amount += cfob_line.ref_amount
									self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_line.id,{'check_cfob_jv_process':True})
								else :
								        self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_line.id,{'cfob_jv_id':None})
						if line.cfob_jv_one2many_reverse: 
							for cfob_line in line.cfob_jv_one2many_reverse:
								cfob_id = cfob_line.cfob_jv_reversal_id
								if cfob_line.check_cfob_reversal == True :
									branch_name.append(cfob_line.branch_name.name)
									cfob_amount += cfob_line.ref_amount
									self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_line.id,{'check_cfob_jv_process':False})
								else :
								        self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_line.id,{'cfob_jv_reversal_id':None})

						if not cfob_id:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed')%(account_name))
						elif cfob_id:
							if line.debit_amount:
								if round(cfob_amount,2) != round(line.debit_amount,2):
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if line.credit_amount:
								if round(cfob_amount,2) != round(line.credit_amount,2):
									raise osv.except_osv(('Alert'),('Credit amount should be equal'))
	
					elif line.customer_name.name == "CBOB" and acc_selection=="against_ref" and line.type=="credit": # CBOB 
						credit_amount = line.credit_amount
						if line.invoice_cbob_one2many == [] and line.debit_cbob_one2many==[]:
							raise osv.except_osv(('Alert'),('Please provide invoice/debit note information.'))
						if line.payment_method == False:
							raise osv.except_osv(('Alert'),('Select Payment Method Before Selecting Invoice'))
						if line.invoice_cbob_one2many:
							for cbob_line in line.invoice_cbob_one2many:
								if cbob_line.cbob_chk_invoice == True:
									cbob_flag = True
									invoice_no = cbob_line.invoice_number
									total_amount = cbob_line.grand_total_amount
									cbob_total += total_amount
									invoice_no = cbob_line.invoice_number
									partial_payment = cbob_line.partial_payment_amount

								if line.payment_method == 'partial_payment':####Partial payment
									if cbob_line.cbob_chk_invoice == True:
										if cbob_line.partial_payment_amount:
											pending_amount = cbob_line.pending_amount - cbob_line.partial_payment_amount
											invoice_adhoc_master.write(cr,uid,cbob_line.id,{
														'pending_amount':pending_amount,
														'pending_status':'pending',
														'status':cbob_line.status,
														'partial_payment_amount':00})
											if not cbob_line.partial_payment_amount:
												raise osv.except_osv(('Alert'),('partial amount cannot be zero.'))

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
												'check_invoice':True})######## For Payment history


								elif line.payment_method == 'full_payment':
									if cbob_line.cbob_chk_invoice == True:
										invoice_receipt_history.create(cr,uid,{
											'invoice_receipt_history_id':cbob_line.id,
											'invoice_number':cbob_line.invoice_number,
											'invoice_pending_amount':0.0,
											'invoice_paid_amount':cbob_line.pending_amount,
											'invoice_paid_date':res.date if res.date else datetime.now().date(),
											'jv_id_history':line.id,
											'invoice_date':cbob_line.invoice_date,
											'service_classification':cbob_line.service_classification,
											'tax_rate':cbob_line.tax_rate,
											'cse':cbob_line.cse.id,
											'check_invoice':True})

										invoice_adhoc_master.write(cr,uid,cbob_line.id,{
											'pending_amount':0.0,
											'pending_status':'paid',
											'status':'paid',
											'partial_payment_amount':00})
											
							# if cbob_flag == False:
							# 	raise osv.except_osv(('Alert'),('Please select the invoice.'))

							invoice_history_srch = payment_contract_history.search(cr,uid,[('invoice_number','=',invoice_no)])
							if invoice_history_srch:
								for invoice_history in payment_contract_history.browse(cr,uid,invoice_history_srch):
									payment_contract_history.write(cr,uid,invoice_history.id,{'payment_status':'paid'})
						if line.debit_cbob_one2many:
							for debit_line in line.debit_cbob_one2many:
								debit_note_no=debit_line.debit_note_no
								if debit_line.check_journal_debit == True:
									cbob_flag = True
									if line.payment_method == 'full_payment':
									# if debit_line.credit_amount_srch==debit_line.receipt_amount:
										srch_debit=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',debit_note_no)])
										for i in self.pool.get('debit.note').browse(cr,uid,srch_debit):
											cr.execute("update debit_note set pending_amount=0.0,paid_amount=%s,state_new='paid' where id=%s",(debit_line.receipt_amount,i.id))
									elif line.payment_method == 'partial_payment':
										pending_amount=debit_line.credit_amount_srch-debit_line.receipt_amount
										srch_debit=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',debit_note_no)])
										for i in self.pool.get('debit.note').browse(cr,uid,srch_debit):
											pending_amount=i.credit_amount_srch-i.receipt_amount
											# self.pool.get('debit.note').write(cr,uid,i.id,{'state_new':'open','credit_amount_srch':pending_amount})
											cr.execute("update debit_note set pending_amount=%s,paid_amount=%s,state_new='open' where id=%s",(pending_amount,debit_line.receipt_amount,i.id))
						if cbob_flag == False:
							raise osv.except_osv(('Alert'),('Please select either Invoice or Debit Note.'))
					
					elif line.customer_name.name == 'CBOB' and acc_selection=="against_ref" and line.type=="debit": # CBOB 
						credit_amount = line.credit_amount
						if line.invoice_cbob_one2many_reverse == []:
							raise osv.except_osv(('Alert'),('Please provide invoice information.'))
						if line.invoice_cbob_one2many_reverse:
							for cbob_line in line.invoice_cbob_one2many_reverse:
								if cbob_line.cbob_chk_invoice_reverse == True:
									cbob_flag = True
									total_amount = cbob_line.jv_amount
									cbob_total += total_amount
									invoice_no = cbob_line.invoice_number
									if cbob_line.jv_amount:
										pending_amount = cbob_line.pending_amount + cbob_line.jv_amount
										invoice_adhoc_master.write(cr,uid,cbob_line.id,{
													'pending_amount':pending_amount,
													'pending_status':'pending',
													'status':'partially_writeoff',
													'partial_payment_amount':00,
													'inv_reversed':True,
													'cbob_invoice_id_reverse1':line.id})
										
							if cbob_flag == False:
								raise osv.except_osv(('Alert'),('Please select the invoice.'))

					else:
						invoice_no = ''
						if line.type == 'credit':
						        for invoice_line in line.invoice_one2many:
							        invoice_id_journal = invoice_line.invoice_id_journal
							        invoice_num = [str(invoice_line.invoice_number),invoice_num]
							        invoice_num = ' / '.join(filter(bool,invoice_num))
							        invoice_date_concate = [invoice_line.invoice_date,invoice_date_concate]
							        invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))
																
							        if line.payment_method == 'full_payment':
								        if invoice_line.check_journal_invoice == True:
									        flag = True
									        count += 1
									        grand_total += invoice_line.grand_total_amount
						
									        invoice_adhoc_master.write(cr,uid,invoice_line.id,{
											        'check_process_journal_invoice':True,
											        'status':'paid',
											        'invoice_paid_date':datetime.now().date() ,
											        'pending_amount':0.0,
											        'pending_status':'paid',})
									        invoice_receipt_history.create(cr,uid,{
										        'invoice_receipt_history_id':invoice_line.id,
										        'invoice_number':invoice_line.invoice_number,
										        'invoice_pending_amount':0.0,
										        'invoice_paid_amount':invoice_line.pending_amount,
										        'invoice_paid_date':res.date if res.date else datetime.now().date(),
										        'jv_invoice_id_history':line.id,
										        'invoice_date':invoice_line.invoice_date,
										        'service_classification':invoice_line.service_classification,
										        'tax_rate':invoice_line.tax_rate,
										        'cse':invoice_line.cse.id,'check_invoice':True})######## For Payment history
								        search1 = payment_contract_history.search(cr,uid,[('invoice_number','=',invoice_no)])
								        for st in payment_contract_history.browse(cr,uid,search1): 
									        payment_contract_history.write(cr,uid,st.id,{'payment_status':'paid'})
											
								        self.sync_invoice_update_state_journal(cr,uid,ids,context=context)


							        if line.payment_method == 'partial_payment':
								        if invoice_line.check_journal_invoice == True:
									        flag = True
									        count += 1
									        pending_amount = invoice_line.pending_amount - invoice_line.partial_payment_amount 
									        invoice_adhoc_master.write(cr,uid,invoice_line.id,{
										        'check_process_journal_invoice':False,
										        'status':invoice_line.status,
										        'invoice_paid_date':datetime.now().date() ,
										        'pending_amount':pending_amount,
										        'pending_status':'pending',})
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
																
							        if line.payment_method == 'full_payment':
								        if invoice_line.check_journal_invoice == True:
									        flag = True
									        count += 1
									        grand_total += invoice_line.grand_total_amount
						
									        invoice_adhoc_master.write(cr,uid,invoice_line.id,{
											        'check_process_journal_invoice':True,
											        'status':'paid',
											        'invoice_paid_date':datetime.now().date() ,
											        'pending_amount':0.0,
											        'pending_status':'paid',})
											        
									        invoice_receipt_history.create(cr,uid,{
										        'invoice_receipt_history_id':invoice_line.id,
										        'invoice_number':invoice_line.invoice_number,
										        'invoice_pending_amount':0.0,
										        'refund_date':res.date if res.date else datetime.now().date(),
										        'jv_invoice_id_history':line.id,
										        'invoice_date':invoice_line.invoice_date,
                                                		        'service_classification':invoice_line.service_classification,
										        'tax_rate':invoice_line.tax_rate,
										        'cse':invoice_line.cse.id,'check_invoice':True})######## For Payment history
								        search1 = payment_contract_history.search(cr,uid,[('invoice_number','=',invoice_no)])
								        for st in payment_contract_history.browse(cr,uid,search1): 
									        payment_contract_history.write(cr,uid,st.id,{'payment_status':'paid'})
											
								        self.sync_invoice_update_state_journal(cr,uid,ids,context=context)


							        if line.payment_method == 'partial_payment':
								        if invoice_line.check_journal_invoice == True:
									        flag = True
									        count += 1
									        pending_amount = invoice_line.pending_amount - invoice_line.partial_payment_amount 
									        invoice_adhoc_master.write(cr,uid,invoice_line.id,{
										        'check_process_journal_invoice':False,
										        'status':invoice_line.status,
										        'invoice_paid_date':datetime.now().date() ,
										        'pending_amount':pending_amount,
										        'pending_status':'pending',})
									        invoice_receipt_history.create(cr,uid,{
										        'invoice_receipt_history_id':invoice_line.id,
										        'invoice_number':invoice_line.invoice_number,
										        'invoice_pending_amount':pending_amount,
		                			                'invoice_paid_amount':invoice_line.partial_payment_amount,
										        'refund_date':res.date if res.date else datetime.now().date(),
										        'jv_invoice_id_history':line.id,
										        'invoice_date':invoice_line.invoice_date,
						        	        'service_classification':invoice_line.service_classification,
										        'tax_rate':invoice_line.tax_rate,
										        'cse':invoice_line.cse.id,
										        'check_invoice':True})######## For Payment history
						if flag == False:
							raise osv.except_osv(('Alert'),('No invoice selected.'))
						total_t=grand_total_t=0.0
						for invoice in line.invoice_one2many:
							if invoice.check_journal_invoice == True:
								if line.payment_method == 'full_payment':
									grand_total_t = invoice.pending_amount
								if line.payment_method == 'partial_payment':
									grand_total_t = invoice.partial_payment_amount
								total_t += grand_total_t
						if round(total_t,2) != round(line.credit_amount,2):
							raise osv.except_osv(('Alert'),('Amount in wizard does not match amount in credit amount'))
						if not invoice_id_journal:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.')%(account_name))
						elif invoice_id_journal:
							if line.credit_amount:
								if grand_total != line.credit_amount:
									#raise osv.except_osv(('Alert'),('Credit amount should be equal'))
									pass

#>>>>>>>>>>>> sagar 11sept CBOB Advance	 # advance in CBOB is stored directly in account_sales_receipt

				# if acc_selection == 'advance' and customer_name == 'CBOB':
				# 	ref_amount_adv =0.0
				# 	advance_id = ''
				# 	for adv_cbob_line in line.cbob_advance_one2many:
				# 		advance_id = adv_cbob_line.cbob_advance_id.id
				# 		ref_amount_adv += adv_cbob_line.ref_amount
				# 		if not adv_cbob_line.ref_no:
				# 			raise osv.except_osv(('Alert'),('Please provide reference number.'))

				# 		if not adv_cbob_line.ref_date:
				# 			raise osv.except_osv(('Alert'),('Please provide reference date.'))
					
				# 	if not advance_id:
				# 		raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
				# 	elif advance_id:
				# 		if line.debit_amount:
				# 			if ref_amount_adv != line.debit_amount:
				# 				raise osv.except_osv(('Alert'),('Debit amount should be equal'))
				# 		if line.credit_amount:
				# 			if ref_amount_adv != line.credit_amount:
				# 				raise osv.except_osv(('Alert'),('credit amount should be equal'))
	   #                              for ln in line.cbob_advance_one2many:
	   #                         		 print ln.id,res.date,res.jv_number,'iddd'
	   #                                       self.pool.get('advance.sales.receipts').write(cr,uid,ln.id,{'receipt_no':res.jv_number,'receipt_date':res.date,'cbob_advance_id':advance_id})
#<<<<<<<<<<<< #sagar
				if acc_selection == 'advance' and customer_name != 'CBOB' : 
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
							                if amt==0.0:
							                        sales_receipts_line.write(cr,uid,i.id,{'state':'finish'})
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
				year1 = int(year1)
			financial_year =str(year1-1)+str(year1)
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
				# py_date = str(today_date + relativedelta(days=-5))
				# if res.date < str(py_date) or res.date > str(today_date):
				# 	raise osv.except_osv(('Alert'),('Kindly select Date 5 days earlier from current date.'))
				date=res.date
			else:
				date=datetime.now().date()
			year = today_date.strftime('%y')

			count=0
			seq_start=1	
			if pcof_key and journal_voucher_id:
				cr.execute("select cast(count(id) as integer) from account_journal_voucher where jv_number is not null and date>='2017-07-01' and  date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				#seq_new = self.pool.get('ir.sequence').get(cr, uid, 'account.journal.voucher')
				jv_no = pcof_key + journal_voucher_id +  str(financial_year) +str(seq).zfill(5)
				#jv_no = pcof_key + journal_voucher_id +  str(year1) +str(seq_new).zfill(6)
				existing_jv_id = self.pool.get('account.journal.voucher').search(cr,uid,[('jv_number','=',jv_no)])
				if existing_jv_id:
					jv_no = pcof_key + journal_voucher_id +  str(financial_year) +str(seq+1).zfill(5)

			if rec.date >='2017-03-01' and rec.date<='2017-03-31':
				year1='17'
				jv_date=rec.date
				if jv_date:
					cr.execute("select cast(count(id) as integer) from account_journal_voucher where jv_number is not null and  date between '2017-03-01' and '2017-03-31' ");
					temp_count=cr.fetchone()
					if temp_count[0]:
						count= temp_count[0]
					seq=int(count+1)
					#seq_new = self.pool.get('ir.sequence').get(cr, uid, 'account.journal.voucher')
					jv_no = pcof_key + journal_voucher_id +  str(year1) +str(seq).zfill(6)
			cus_new=''
			if rec.customer_name.name == 'CFOB':
				for j  in rec.journal_voucher_one2many:
					if j.account_id.account_selection=='against_ref':
						for k in j.cfob_jv_one2many:
							if k.check_cfob == True:
								cus_new= ', '.join(filter(bool,['CFOB - ' + k.customer_cfob]))
						if j.cfob_jv_one2many_reverse:
							for k in j.cfob_jv_one2many_reverse:
								if k.check_cfob_reversal == True:
									cus_new= ', '.join(filter(bool,['CFOB - ' + k.customer_cfob]))
			elif rec.customer_name.name == 'CBOB':
				for j  in rec.journal_voucher_one2many:
					if j.account_id.account_selection=='against_ref' and j.type=="credit":
						for k in j.invoice_cbob_one2many:
							if k.cbob_chk_invoice == True:
								if not j.partner_id.id:
									raise osv.except_osv(('Alert'),('Please Select Customer Name!'))
								else:
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

		for res in self.browse(cr,uid,ids):
			partner_id = ''
			customer_name = res.customer_name.name
			for line in res.journal_voucher_one2many:
				if line.account_id.account_selection == 'against_ref' and customer_name == 'CBOB':
					if line.partner_id.id:
						partner_id = line.partner_id.id

		for res in self.browse(cr,uid,ids):
			for line in res.journal_voucher_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name
				customer_name = res.customer_name.name
				if acc_selection == 'advance' and customer_name == 'CBOB':
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
								self.pool.get('advance.sales.receipts').write(cr,uid,ln.id,{'receipt_no':res.jv_number,'receipt_date':res.date,'cbob_advance_id':advance_id,'advance_pending':ln.ref_amount,'partner_id':partner_id})
								
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
				cust_name_cbob= line.partner_id.name 
				if line.account_id.account_selection == 'security_deposit' and line.type=='credit':
					if line.security_deposit_cbob_jv_one2many == []:
						raise osv.except_osv(('Alert'),('Please enter the details for Security Deposit wizard!'))	
				        line_id1=line.id
				        sec_flag_credit = True
				if line.account_id.account_selection == 'others' and line.type=='debit':
				        line_id1=line.id
				        sec_flag_others = True		
			for line in res.journal_voucher_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name
				if res.date:
					date=res.date
				else:
					date=datetime.now().date()
				if sec_flag_credit and sec_flag_others:
					if line.security_deposit_cbob_jv_one2many:
						for invoice_line in line.security_deposit_cbob_jv_one2many:
							if invoice_line.check_sc_cbob_jv == True :
								self.pool.get('security.deposit').write(cr,uid,invoice_line.id,{'pending_amount':0.0})
				if acc_selection in ('against_ref','security_deposit'):
					if line.security_deposit_cbob_jv_one2many:
						for invoice_line in line.security_deposit_cbob_jv_one2many:
							if invoice_line.check_sc_cbob_jv == True :
								if invoice_line.cse:
									main_str = "select name from resource_resource where id = '" + "" + str(invoice_line.cse.resource_id.id) + "'"
									cr.execute(main_str)
									first_name = cr.fetchone()
									if first_name:
										cse_name_last_cbob = str(first_name[0]) +' '+str(invoice_line.cse.last_name)
								else:
									if invoice_line.cse_char:
										cse_char = str(invoice_line.cse_char)
										cse_char = cse_char.split(' ')
										if len(cse_char)==3:
											cse_name_last_cbob = str(cse_char[0]) +' '+str(cse_char[2])
					if line.invoice_cbob_one2many:
						for invoice_line in line.invoice_cbob_one2many:
							if invoice_line.cbob_chk_invoice == True :
								invoice_no=invoice_line.invoice_number
								inv_date=invoice_line.invoice_date	
								gross_amt=invoice_line.grand_total_amount
								idts_pending=invoice_line.pending_amount
								if invoice_line.cse:
									main_str = "select name from resource_resource where id = '" + "" + str(invoice_line.cse.resource_id.id) + "'"
									cr.execute(main_str)
									first_name = cr.fetchone()
									if first_name:
										cse_name_last_cbob = str(first_name[0]) +' '+str(invoice_line.cse.last_name)
								else:
									if invoice_line.cse_char:
										cse_char = str(invoice_line.cse_char)
										cse_char = cse_char.split(' ')
										if len(cse_char)==3:
											cse_name_last_cbob = str(cse_char[0]) +' '+str(cse_char[2])
					if line.invoice_cbob_one2many_reverse:
						for invoice_line in line.invoice_cbob_one2many_reverse:
							if invoice_line.cbob_chk_invoice_reverse == True :
								invoice_no=invoice_line.invoice_number
								inv_date=invoice_line.invoice_date	
								gross_amt=invoice_line.grand_total_amount
								idts_pending=invoice_line.pending_amount
								if invoice_line.cse:
									main_str = "select name from resource_resource where id = '" + "" + str(invoice_line.cse.resource_id.id) + "'"
									cr.execute(main_str)
									first_name = cr.fetchone()
									if first_name:
										cse_name_last_cbob = str(first_name[0]) +' '+str(invoice_line.cse.last_name)
								else:
									if invoice_line.cse_char:
										cse_char = str(invoice_line.cse_char)
										cse_char = cse_char.split(' ')
										if len(cse_char)==3:
											cse_name_last_cbob = str(cse_char[0]) +' '+str(cse_char[2])
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

class search_journal_voucher_line(osv.osv):
	_inherit = 'search.journal.voucher.line'
	_rec_name = 'jv_number'
	_order = 'date desc'


search_journal_voucher_line ()