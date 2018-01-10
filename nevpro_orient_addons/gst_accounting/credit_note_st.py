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

class credit_note_st(osv.osv):
	_inherit = 'credit.note.st'
	_order = 'credit_note_date desc'

	_columns = {
		'gst_credit_note_st':fields.boolean('GST Credit Note ST?'),
		'reason':fields.many2one('reason.for.issue.of.doc','Reason'),
	}

	def add_credit_note(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			if  res.account_id.account_selection in ('cash','iob_one','iob_two'): #HHH 3mar
				raise osv.except_osv(('Alert'),("You can't add Cash or Bank account"))
			
			account_id = res.account_id.id
			types = res.type
			status = res.status
			customer_name=res.customer_name.id
			if (res.account_id.product_id.id  != False or res.account_id.account_selection == 'tax') and res.type == 'credit' :
				raise osv.except_osv(('Alert!'),('Services and tax cannot be Cannot be of type credit'))
			
			
			for i in res.credit_note_st_one2many:
				if account_id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
			if not account_id:
				raise osv.except_osv(('Alert'),('Please select Account Name.'))
			if not types:
				raise osv.except_osv(('Alert'),('Please select Type.'))
			if not status:
				raise osv.except_osv(('Alert'),('Please select status.'))
				
			if res.account_id.account_selection == 'against_ref':
				cr.execute('update invoice_adhoc_master set check_credit_note_st = False,check_credit_note_st_paid=False where check_process_credit_note_st =False and check_credit_note_st = True or check_credit_note_st_paid=True')
				cr.execute('update debit_note set check_cn_debit = False,receipt_amount=0.0 where check_process_dn = False and debit_note_no is not Null')
			if res.credit_note_st_one2many != []:
				flag = False	
				test= True
				for line in res.credit_note_st_one2many:
					if line.account_id.account_selection == 'against_ref' or line.account_id.account_selection == 'advance':
						for ln in line.credit_st_outstanding_invoice:
							check_credit_note_st = ln.check_credit_note_st
							if check_credit_note_st == True:
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
												
						for ln in line.credit_st_paid_invoice:
							check_credit_note_st_paid = ln.check_credit_note_st_paid#added in sales_receripts
							if check_credit_note_st_paid == True:
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

			total=service_debit_tax=service_credit_tax=0.0
			
			for i in res.credit_note_st_one2many:
				if i.account_id.account_selection==False and i.account_id.product_id != False:
					if i.type=='debit':
						total +=i.debit_amount
					else:
						total +=i.credit_amount
						
			if res.account_id.account_selection== 'tax':
				if res.type=='debit':
					service_debit_tax = round((float(total)*(res.account_id.account_tax_many2one.amount)))
				else:
					service_credit_tax = round((float(total)*(res.account_id.account_tax_many2one.amount)))
					
			self.pool.get('credit.note.line.st').create(cr,uid,{
								'credit_st_id':res.id,
								'account_id':account_id,
								'credit_amount':service_credit_tax,
								'debit_amount':service_debit_tax,
								'type':types,
								'status_selection':status,
								'customer_name':customer_name,
								'writeoff_status':res.writeoff_status,
								 })	

			self.write(cr,uid,res.id,{'account_id':None,'type':''})

		return True

	def process(self, cr, uid, ids, context=None):
		invoice_adhoc_master = self.pool.get('invoice.adhoc.master')
		sales_receipts = self.pool.get('account.sales.receipts')
		sales_receipts_line = self.pool.get('account.sales.receipts.line')
		cr_total = dr_total = cr_amount=dr_amount=total = 0.0
		move = credit_invoice = credit_st_id=credit_st_id1 =debit_note_st_id = credit_note_date =''
		post = []
		today_date = datetime.now().date()
		flag = py_date = False
		status=[]
		pms_list=[]
		pms_list1=[]
		tax_list=[]
		tax_list1=[]
		credit_flag = debit_flag = debit_nt_flag = False
		for credit_note in self.browse(cr,uid,ids):
			if not credit_note.reason:
				raise osv.except_osv(('Alert'),('Kindly select Reason!'))
			for credit_note_line in credit_note.credit_note_st_one2many:
				if credit_note_line.account_id.account_selection=='advance' and credit_note_line.type=='debit':
					credit_flag=True
			for credit_note_line in credit_note.credit_note_st_one2many:
				if credit_note_line.account_id.account_selection=='against_ref' and credit_note_line.type=='credit':
					debit_flag=True
			for credit_note_line in credit_note.credit_note_st_one2many:
				credit_amount = credit_note_line.credit_amount
				debit_amount = credit_note_line.debit_amount
				acc_selection = credit_note_line.account_id.account_selection
				if acc_selection=='st_input' and credit_note_line.account_id.code in ('sgst','cgst','igst','utgst'):
					acc_name=credit_note_line.account_id.name
					acc_name=acc_name.split('-')
					if acc_name[0]:
						raise osv.except_osv(('Alert'),("Kindly select '%s' ledger!")%(acc_name[0]))
				if debit_flag == True and credit_flag == False:
					if not credit_note.customer_name:
						raise osv.except_osv(('Alert'),('Please select customer Name!'))
				if debit_flag == False and credit_flag == False:
					if not credit_note.customer_name:
						raise osv.except_osv(('Alert'),('Please select customer Name!'))
				if acc_selection == 'against_ref':
					if credit_note_line.credit_st_outstanding_invoice:
						for ln in credit_note_line.credit_st_outstanding_invoice:
							check_credit_note_st = ln.check_credit_note_st
							if check_credit_note_st == True:
								if ln.invoice_date<'2017-07-01':
									raise osv.except_osv(('Alert!'),('Credit Note (ST) entry not allowed for invoices generated on/prior to 30-06-2017. Pass normal credit note entry for write-off.'))
								search_invoices=invoice_adhoc_master.search(cr,uid,[('invoice_number','=',ln.invoice_number)])
								if search_invoices:
									for inv in invoice_adhoc_master.browse(cr,uid,search_invoices):
										if inv.invoice_line_adhoc_11:
											for inv_line in inv.invoice_line_adhoc_11:
												pms_list.append(inv_line.pms.id)
										if inv.invoice_line_adhoc:
											for inv_line in inv.invoice_line_adhoc:
												pms_list.append(inv_line.pms.id)
										if inv.tax_one2many:
											for tax in inv.tax_one2many:
												tax_list.append(tax.account_id.id)
					if credit_note_line.credit_st_paid_invoice:
						for ln in credit_note_line.credit_st_paid_invoice:
							check_credit_note_st_paid = ln.check_credit_note_st_paid
							if check_credit_note_st_paid == True:
								if ln.invoice_date<'2017-07-01':
									raise osv.except_osv(('Alert!'),('Credit Note (ST) entry not allowed for invoices generated on/prior to 30-06-2017. Pass normal credit note entry for write-off.'))
								search_invoices=invoice_adhoc_master.search(cr,uid,[('invoice_number','=',ln.invoice_number)])
								if search_invoices:
									for inv in invoice_adhoc_master.browse(cr,uid,search_invoices):
										if inv.invoice_line_adhoc_11:
											for inv_line in inv.invoice_line_adhoc_11:
												pms_list.append(inv_line.pms.id)
										if inv.invoice_line_adhoc:
											for inv_line in inv.invoice_line_adhoc:
												pms_list.append(inv_line.pms.id)
										if inv.tax_one2many:
											for tax in inv.tax_one2many:
												tax_list.append(tax.account_id.id)
					if credit_note_line.debit_note_cnst_one2many:
						for ln in credit_note_line.debit_note_cnst_one2many:
							credit_id = ln.debit_credit_note_st_id
							check_debit_note = ln.check_cn_debit
							if check_debit_note == True:
								debit_nt_flag = True
			if credit_note.customer_name:
				if pms_list:
					for credit_note in self.browse(cr,uid,ids):
						for credit_note_line in credit_note.credit_note_st_one2many:
							if credit_note_line.type=='debit' and credit_note_line.account_id.product_id.id!=False:
								pms_list1.append(credit_note_line.account_id.product_id.id)
				if pms_list and pms_list1:
					any_in = [i for i in pms_list if i in pms_list1]
					if any_in==[]:
						raise osv.except_osv(('Alert'),('Please select any service type which is present in the selected invoice.'))
				if tax_list:
					for credit_note_line in credit_note.credit_note_st_one2many:
						if credit_note_line.type=='debit' and credit_note_line.account_id.account_selection=='tax':
							tax_list1.append(credit_note_line.account_id.id)
				if tax_list1==[] and debit_nt_flag==False:
					raise osv.except_osv(('Alert'),('Credit Note(ST) entry cannot be processed without service tax bifurcation which is present in the selected Invoice.'))
				
				if tax_list and tax_list1:
					if set(tax_list)!=set(tax_list1):
						raise osv.except_osv(('Alert'),('Credit Note(ST) entry cannot be processed without service tax bifurcation which is present in the selected Invoice.'))
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
				
			for line in res.credit_note_st_one2many:
				if line.type == 'credit':
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				elif line.type == 'debit':
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				else:
					raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(line.account_id.name))))
					
				cr_amount += line.credit_amount
				dr_amount += line.debit_amount

				account_id = line.account_id.id
				temp = tuple([account_id])
				post.append(temp)
				for i in range(0,len(post)):	
					for j in range(i+1,len(post)):
						if post[i][0]==post[j][0]:
							raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

			if str(cr_amount) != str(dr_amount):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if cr_amount == 0.0 or dr_amount == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
		
		for credit_note in self.browse(cr,uid,ids):
		        advance_flag=True
			for credit_note_line in credit_note.credit_note_st_one2many:
				
				credit_amount = credit_note_line.credit_amount
				debit_amount = credit_note_line.debit_amount
				acc_selection = credit_note_line.account_id.account_selection
				
				for i in credit_note.credit_note_st_one2many:
				        if i.account_id.account_selection == 'advance':
        				        advance_flag=False
				        
				if acc_selection == 'against_ref':
					for ln in credit_note_line.credit_st_outstanding_invoice:
						check_credit_note_st = ln.check_credit_note_st
						if check_credit_note_st == True:
							if ln.invoice_date<'2017-07-01':
								raise osv.except_osv(('Alert!'),('Credit Note (ST) entry not allowed for invoices generated on/prior to 30-06-2017. Pass normal credit note entry for write-off.'))
							credit_st_id = ln.credit_invoice_id1
							full_1=ln.total_writeoff + ln.writeoff_amount
							# if ln.pending_status=='open':
							# 	if full_1 == ln.pending_amount and credit_note.writeoff_status == 'partially_writeoff':
							# 		raise osv.except_osv(('Alert'),('please select fully writeoff.'))

							if credit_note.status == 'against_cancellation':#Against Cancellation
								flag = True
								invoice_number = ln.invoice_number
								if credit_note.writeoff_status == 'partially_writeoff':
									total += ln.writeoff_amount

								# if credit_note.writeoff_status == 'fully_writeoff':
								# 	total += ln.pending_amount

					for ln in credit_note_line.credit_st_paid_invoice:
						check_credit_note_st1 = ln.check_credit_note_st_paid
						if check_credit_note_st1 == True:
							if ln.invoice_date<'2017-07-01':
								raise osv.except_osv(('Alert!'),('Credit Note (ST) entry not allowed for invoices generated on/prior to 30-06-2017. Pass normal credit note entry for write-off.'))
							credit_st_id1 = ln.credit_note_paid
							if ln.pending_status=='paid':
								full_2=ln.total_writeoff_paid + ln.writeoff_amount_paid
								# if full_2 == ln.paid_amount and credit_note.writeoff_status == 'partially_writeoff':
								# 	raise osv.except_osv(('Alert'),('please select fully writeoff.'))

							if credit_note.status == 'against_cancellation':#Against Cancellation
								flag = True
								invoice_number = ln.invoice_number
								if credit_note.writeoff_status == 'partially_writeoff':
										total += ln.writeoff_amount_paid
									
								# if credit_note.writeoff_status == 'fully_writeoff':
								# 		total += ln.paid_amount
					for ln in credit_note_line.debit_note_cnst_one2many:
						check_cn_debit = ln.check_cn_debit
						if check_cn_debit == True:
							debit_note_st_id = ln.debit_credit_note_st_id
							#Against Cancellation
							flag = True

					if flag == False:
						raise osv.except_osv(('Alert'),('No invoice/debit note selected.'))

					if not credit_st_id and not credit_st_id1 and not debit_note_st_id:
						raise osv.except_osv(('Alert'),('Select Invoice/Debit Note against "%s" entry to proceed.') % (credit_note_line.account_id.name))
					
				if acc_selection == 'advance': #adjusting CFOB entries reflecting under advance HHH 9mar
					for advance_refund in credit_note_line.cnst_advance_one2many:
						if advance_refund.check_advance_against_ref == True:
						        if advance_refund.advance_pending < advance_refund.partial_amt :
						                raise osv.except_osv(('Alert'),('enter proper partial amount'))
						        pending_amt=advance_refund.advance_pending - advance_refund.partial_amt if advance_refund.partial_amt  else '0.0'
						        
						        ############################
						        receipt_id=receipt_no=''
							line_srch=sales_receipts_line.search(cr,uid,[('id','=',advance_refund.advance_id.id)])
							if line_srch:
							        for i in sales_receipts_line.browse(cr,uid,line_srch):
							                main_srch=sales_receipts.search(cr,uid,[('id','=',i.receipt_id.id)])
							                for j in sales_receipts.browse(cr,uid,main_srch):
							                        receipt_no=j.receipt_no
							                        receipt_id=j.id
							                        sales_receipts.write(cr,uid,j.id,{'advance_pending':pending_amt})
							                if pending_amt==0.0:
							                        sales_receipts_line.write(cr,uid,i.id,{'state':'finish'})
							###########################
							
							self.pool.get('advance.sales.receipts').write(cr,uid,advance_refund.id,{
								                        'check_advance_against_ref':False,
								                        'check_advance_against_ref_process':True if (advance_refund.advance_pending-advance_refund.partial_amt)==0 else False ,
								                        'advance_pending':pending_amt})
								                        
							self.pool.get('advance.receipt.history').create(cr,uid,{
								                        'cr_receipt_id':credit_note_line.id,
								                        'advance_receipt_no':receipt_no if receipt_no else advance_refund.ref_no,
								                        'cust_name':advance_refund.partner_id.id,
								                        'advance_refund_amount':advance_refund.partial_amt if advance_refund.partial_amt  else advance_refund.advance_pending,
								                        'advance_pending_amount':pending_amt,
								                        'advance_receipt_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
								                        'advance_date':advance_refund.ref_date,
								                        'history_advance_id':advance_refund.id,
								                        'receipt_id':receipt_id if receipt_id else False,
								                        'service_classification':advance_refund.service_classification,
								                        })				

		self.pms_validation(cr,uid,ids,context=context) # Validation for Accounts of PMS
		
		for rec1 in self.browse(cr,uid,ids):
			print rec1.status,'status'
			for line_state in rec1.credit_note_st_one2many:
				pending_amt=grand_total_against=0.0
				t2=self.pool.get('credit.note.line.st').write(cr,uid,line_state.id,{'state':'done'})
				
				for chk in line_state.credit_st_outstanding_invoice:
					full_2=chk.total_writeoff
					if full_2 == chk.grand_total_amount:
						#raise osv.except_osv(('Alert'),('please select full writeoff.3'))
						pass

					check_credit_note_st = chk.check_credit_note_st
					if check_credit_note_st == True:
						status=""
						if rec1.status == 'against_cancellation':
							if rec1.writeoff_status == 'partially_writeoff':
								pending_amount = chk.pending_amount - chk.writeoff_amount
								total_amount = chk.total_writeoff + chk.writeoff_amount#hi
								if chk.pending_amount==chk.writeoff_amount:
									status='writeoff'
									self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{
										'check_process_credit_note_st':True,
										'status':'writeoff',
										'pending_amount':pending_amount,
										'pending_status':'paid',#chk.pending_status,
										'total_writeoff':total_amount,
										'writeoff_amount':0.0})
								else:
									status='partially_writeoff'	
									self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{
										'check_process_credit_note_st':False,
										'status':'partially_writeoff',
										#'pending_amount':pending_amount,
										'pending_status':'pending',#chk.pending_status,
										'total_writeoff':total_amount,
										'writeoff_amount':0.0})
								cr.execute("update invoice_adhoc_master set pending_amount=%s where id=%s",(pending_amount,chk.id))
								
								self.pool.get('invoice.receipt.history').create(cr,uid,{
									'invoice_receipt_history_id':chk.id,
									'invoice_number':chk.invoice_number,
									'invoice_pending_amount':pending_amount,
									'invoice_writeoff_amount':chk.writeoff_amount,
									'invoice_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
									'credit_st_id_history':line_state.id,
									'invoice_date':chk.invoice_date,
									'service_classification':chk.service_classification,
									'tax_rate':chk.tax_rate,
									'cse':chk.cse.id,
									'check_invoice':True})
								srch_history = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',chk.invoice_number)])
								if srch_history:
									for invoice_history in self.pool.get('payment.contract.history').browse(cr,uid,srch_history):
										self.pool.get('payment.contract.history').write(cr,uid,invoice_history.id,{'payment_status':status})

								        
							# if rec1.writeoff_status == 'fully_writeoff':
							# 	tot_wrt_off = chk.total_writeoff + chk.writeoff_amount
							# 	self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{
							# 			'check_process_credit_note_st':True,
							# 			'status':'writeoff',
							# 			'pending_status':'paid',
							# 			'pending_amount':0.0,
							# 			'total_writeoff':tot_wrt_off,
							# 			'writeoff_amount':0.0})
										        
							# 	self.pool.get('invoice.receipt.history').create(cr,uid,{
							# 			'invoice_receipt_history_id':chk.id,
							# 			'invoice_number':chk.invoice_number,
							# 			'invoice_pending_amount':0.0,
							# 			'invoice_writeoff_amount':chk.writeoff_amount,
							# 			'invoice_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
							# 			'credit_st_id_history':line_state.id,
							# 			'invoice_date':chk.invoice_date,
							# 			'service_classification':chk.service_classification,
							# 			'tax_rate':chk.tax_rate,
							# 			'cse':chk.cse.id,
							# 			'check_invoice':True})

							# 	srch_history = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',chk.invoice_number)])
							# 	if srch_history:
							# 		for invoice_history in self.pool.get('payment.contract.history').browse(cr,uid,srch_history):
							# 			self.pool.get('payment.contract.history').write(cr,uid,invoice_history.id,{'payment_status':'writeoff'})
				for chk1 in line_state.credit_st_paid_invoice:###FOR PAID INVOICE
					check_credit_note_st = chk1.check_credit_note_st_paid#hi
					full_1=chk1.total_writeoff
					if check_credit_note_st == True:
						if full_1 == chk1.grand_total_amount:
							# raise osv.except_osv(('Alert'),('please select full writeoff.'))
							pass
						if rec1.status == 'against_cancellation':
							if rec1.writeoff_status == 'partially_writeoff':
								pending_amount =   chk1.pending_amount + chk1.writeoff_amount_paid
								total_amount = chk1.total_writeoff_paid + chk1.writeoff_amount_paid #total_writeoff_paid
								self.pool.get('invoice.adhoc.master').write(cr,uid,chk1.id,{
									'check_process_credit_note_st':False,
									'status':'partially_writeoff',
									'pending_status':'pending',
									'total_writeoff':chk1.total_writeoff,
									'writeoff_amount_paid':0.0,
									'total_writeoff_paid':total_amount,
									'pending_amount':pending_amount})#total_writeoff_paid
								self.pool.get('invoice.receipt.history').create(cr,uid,{
										'invoice_receipt_history_id':chk1.id,
										'invoice_number':chk1.invoice_number,
										'invoice_writeoff_amount':chk1.writeoff_amount_paid,
										'invoice_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
										'credit_st_id_history':line_state.id,
										'invoice_date':chk1.invoice_date,
										'service_classification':chk1.service_classification,
										'tax_rate':chk1.tax_rate,
										'cse':chk1.cse.id,
										'check_invoice':True})

								srch_history = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',chk1.invoice_number)])
								if srch_history:
									for invoice_history in self.pool.get('payment.contract.history').browse(cr,uid,srch_history):
										self.pool.get('payment.contract.history').write(cr,uid,invoice_history.id,{'payment_status':'partially_writeoff'})
				for chk in line_state.debit_note_cnst_one2many:
					if line_state.debit_note_cnst_one2many:
						check_debit_note = chk.check_cn_debit
						if check_debit_note == True:
							if rec1.status == 'against_cancellation':
								for debit_line in line_state.debit_note_cnst_one2many:
									if debit_line.check_cn_debit==True:
										debit_note_no=debit_line.debit_note_no									
										pending_amount=debit_line.credit_amount_srch-debit_line.receipt_amount
										srch_debit=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',debit_note_no)])
										for i in self.pool.get('debit.note').browse(cr,uid,srch_debit):
											pending_amount=i.pending_amount-i.receipt_amount
											paid_amount=i.receipt_amount+i.paid_amount
											self.pool.get('invoice.receipt.history').create(cr,uid,
												{
													'check_dn':True,
													'invoice_receipt_history_debit_id':line_state.id,
													'invoice_number':i.debit_note_no,
													'invoice_pending_amount':pending_amount,
													'receipt_number':line_state.credit_st_id.credit_note_no,
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
							# if rec1.writeoff_status == 'fully_writeoff':
								
							# 	pending_amount_full =   chk1.pending_amount + chk1.writeoff_amount_paid
							# 	self.pool.get('invoice.adhoc.master').write(cr,uid,chk1.id,{
							# 							'check_process_credit_note_st':True,
							# 							'status':'writeoff',
							# 							'pending_status':'paid',
							# 							#'pending_amount':pending_amount_full,
							# 							#'total_writeoff':total_amount,
							# 							#'writeoff_amount_paid':total_amount_full
							# 							})
							# 	cr.execute("update invoice_adhoc_master set pending_amount=%s where id=%s",(pending_amount_full,chk1.id))	
									
							# 	self.pool.get('invoice.receipt.history').create(cr,uid,{
							# 					'invoice_receipt_history_id':chk1.id,
							# 					'invoice_number':chk1.invoice_number,
							# 					'invoice_pending_amount':0.0,
							# 					'invoice_writeoff_amount':chk1.writeoff_amount_paid,
							# 					'invoice_writeoff_date':res.credit_note_date if res.credit_note_date else datetime.now().date(),
							# 					'credit_st_id_history':line_state.id,
							# 					'invoice_date':chk1.invoice_date,
							# 					'service_classification':chk1.service_classification,
							# 					'tax_rate':chk1.tax_rate,
							# 					'cse':chk1.cse.id,
							# 					'check_invoice':True})
	
							# 	srch_history = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',chk1.invoice_number)])
							# 	if srch_history:
							# 		for invoice_history in self.pool.get('payment.contract.history').browse(cr,uid,srch_history):
							# 			self.pool.get('payment.contract.history').write(cr,uid,invoice_history.id,{'payment_status':'writeoff'})
										
		for rec in self.browse(cr,uid,ids):
			amount = total = 0.0
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_note_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_note_tree')

			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = credit_note_id = end_year = pcof_key = ''
			
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','credit.note.st')])
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
			financial_year =str(year1-1)+str(year1)
			financial_end_date = str(end_year)+'-03-31'
			company_id=self._get_company(cr,uid,context=None)
			if company_id:
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					if comp_id.credit_note_id:
						credit_note_st_id = comp_id.credit_note_st_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			seq_start = 1
			####################### OLD Code for Credit note ST number generation ##################
			# if pcof_key and credit_note_st_id:
			# 	cr.execute("select cast(count(id) as integer) from credit_note_st where credit_note_no is not null and credit_note_date>='2017-07-01' and  credit_note_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
			# 	temp_count=cr.fetchone()
			# 	if temp_count[0]:
			# 		count= temp_count[0]
			# 	seq=int(count+seq_start)
			# 	# seq_new=self.pool.get('ir.sequence').get(cr,uid,'credit.note.st')
			# 	value_id = pcof_key + credit_note_st_id +  str(financial_year) +str(seq).zfill(5)
			# 	#value_id = pcof_key + credit_note_st_id +  str(year1) +str(seq_new).zfill(6)
			# 	existing_value_id = self.pool.get('credit.note.st').search(cr,uid,[('credit_note_no','=',value_id)])
			# 	if existing_value_id:
			# 		value_id = pcof_key + credit_note_st_id +  str(financial_year) +str(seq+1).zfill(5)

			######################## NEW Code to generate Credit Note ST Number ##########
			credit_note_st_id=5
			financial_year=str(year1)
			if pcof_key and credit_note_st_id:
				pcof_key_list=pcof_key.split('P')
				like_variable=str(pcof_key_list[1])+str(credit_note_st_id)+str(financial_year)+'%'
				sql_var="select cast(count(id) as integer) from credit_note_st where credit_note_no is not null and credit_note_date>='2017-07-01' and credit_note_no ilike '"+like_variable+"' and credit_note_no not ilike '%\P%' and credit_note_no not ilike '%\CN(ST)%' and credit_note_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' "
				cr.execute(sql_var)
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key_list[1] + str(credit_note_st_id) +  str(financial_year) +str(seq).zfill(4)
				#value_id = pcof_key + credit_note_id +  str(year1) +str(seq_new).zfill(6)
				existing_value_id = self.pool.get('credit.note.st').search(cr,uid,[('credit_note_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key_list[1] + str(credit_note_st_id) +  str(financial_year) +str(seq+1).zfill(4)
			################## END #################
			t=self.write(cr,uid,ids,{'credit_note_no':value_id,'credit_note_date': credit_note_date,'voucher_type':'Credit Note'})
			
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
							'date':date,'name':value_id,
							'partner_id':rec.customer_name.id if rec.customer_name.id else None,
							'narration':rec.narration if rec.narration else '',
							'voucher_type':'Credit Note ST',
							},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.credit_note_st_one2many:
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

			t1=self.write(cr,uid,rec.id,{'status':rec.status})
			self.write(cr,uid,rec.id,{'state':'done',})
			

		for creditnote_his in self.browse(cr,uid,ids):#edited by rohit 12 may
			status_selection1=''
			# if creditnote_his.inv_selected == False:
			# 	raise osv.except_osv(('Alert'),('Select advance reference!'))
			cust_name=creditnote_his.customer_name.name
			if creditnote_his.credit_note_date:
				creditnote_date=creditnote_his.credit_note_date
			else:
				credit_note_date=datetime.now().date()
			creditnote_type=creditnote_his.type

			if creditnote_his.status == 'against_cancellation':
				status_selection1='Against Cancellation'

			for creditnote_line in creditnote_his.credit_note_st_one2many:
				amount=creditnote_line.debit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			curr_id =''
			for jj in var:
				curr_id=jj
			if curr_id:
				self.pool.get('credit.note.history').create(cr,uid,{
							'credit_note_his_many2one':curr_id,
							'credit_note_number':value_id,
							'credit_note_date':creditnote_date,
							'credit_note_type':status_selection1,
							'credit_note_amount':amount})

		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
		credit_note_data = self.browse(cr,uid,ids[0])
		credit_note_st_one2many = credit_note_data.credit_note_st_one2many
		for note_line_id in credit_note_st_one2many:
			account_selection = note_line_id.account_id.account_selection
			inv_selected = note_line_id.inv_selected
			if account_selection in ['advance','advance_against_ref','against_ref','security_deposit','sundry_deposit'] and inv_selected != True:
				raise osv.except_osv(('Alert'),('Select invoice/advance reference!'))	
		self.write(cr,uid,credit_note_data.id,{'gst_credit_note_st':True})		
 		return  {
			'name':'Credit Note ST',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'credit.note.st',
			'res_id':rec1.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
			}

	def print_report(self,cr,uid,ids,context=None):
		total=total_service=tax_amt=total_tax_amt=0.00
		tax_name =tax_amount=''
		cr.execute('delete from credit_note_report_st b  where b.report_id=%(val)s',{'val':ids[0]})
		note_st_data = self.browse(cr,uid,ids[0])
		report_name = ''
		for res in self.browse(cr,uid,ids):
			if uid != 1:
				file_format='pdf'
				doc=str(res.credit_note_no)
				doc_name='credit_note(ST)'
				self.pool.get('user.print.detail').update_rec(cr,uid,file_format,doc,doc_name)
			for i in res.credit_note_st_one2many:
				if (i.account_id.account_selection==False and i.account_id.product_id != False) or i.account_id.account_selection=='advance':
					if i.type == 'debit':
						total += i.debit_amount
					else:
						total += i.credit_amount
					self.pool.get('credit.note.report.st').create(cr,uid,{
											'report_id':res.id,
											'account_id':i.account_id.id,
											'type':i.type,
											'credit_amount':i.credit_amount,
											'debit_amount':i.debit_amount})
				if i.account_id.account_selection=='tax':
					if i.type == 'debit':
						tax_amt = i.debit_amount
					else:
						tax_amt = i.credit_amount
					total_tax_amt += tax_amt	
					tax_name +='\n '+i.account_id.name
					tax_amount +='\n '+str(format(tax_amt,'.2f'))
				if i.account_id.account_selection == 'against_ref':
					if i.account_id.gst_applied == True:
						report_name = 'gst_credit_note_st'
					else:
						report_name = 'credit_note_st'
			total_service = format(total + total_tax_amt,'.2f')
			s = self.write(cr,uid,res.id,
				{
					'pms_total':str(format(total,'.2f')),
					'tax_name':tax_name,
					'tax_amount':tax_amount,
					'pms_grand_total':total_service
				})
			data = self.pool.get('credit.note.st').read(cr, uid, [res.id],context)
			datas = {
				'ids': ids,
				'model': 'credit.note.st',
				'form': data
				}
		if report_name == 'gst_credit_note_st':
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'gst_credit_note_st',
				'datas': datas,
			}
		else:
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'credit_note_st',
				'datas': datas,
			}

credit_note_st()

class credit_note_line_st(osv.osv):
	_inherit = 'credit.note.line.st'

	_columns = {

		'debit_note_cnst_one2many':fields.one2many('debit.note','debit_credit_note_st_id','Debit Note'),#
		'debit_note_cnst_history_one2many':fields.one2many('invoice.receipt.history','invoice_receipt_history_debit_id','Debit Note'),
	}
	def save_advance(self, cr, uid, ids, context=None): ### HHH 3nov adjusting CFOB entries reflecting under advance
		total = amount = 0.0
		invs = []
		cur = self.browse(cr,uid,ids[0])
		for rec in self.browse(cr,uid,ids):
			if rec.cnst_advance_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process.'))
			for line in rec.cnst_advance_one2many:
				if line.check_advance_against_ref == True: 
					if rec.writeoff_status =='partially_writeoff':
					        amount = line.partial_amt
					        if line.partial_amt > line.advance_pending or line.partial_amt <= 0.0 :
					                raise osv.except_osv(('Alert'),('Please Enter proper partial amount'))
					                
					# if rec.writeoff_status =='fully_writeoff':
					#         amount = line.advance_pending
					
					total += amount 
					invs.append(line.id)					
			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':total})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':total})
		if len(invs) > 0:
			self.write(cr,uid,ids[0],{'inv_selected':True})
		else:
			self.write(cr,uid,ids[0],{'inv_selected':False})
		return {'type': 'ir.actions.act_window_close'}

	def show_details(self, cr, uid, ids, context=None):
		final_lst=[]
		for res in self.browse(cr,uid,ids):
			credit_st_id = res.credit_st_id.id
			search = self.pool.get('credit.note.st').search(cr,uid,[('id','=',credit_st_id)])
			account_name = ''
			for rec in self.pool.get('credit.note.st').browse(cr,uid,search):
				cust_id = rec.customer_name.id
				if rec.credit_note_st_one2many:
					for st_line in rec.credit_note_st_one2many:
						account_name = st_line.account_id.name
				tax_rate = ''
				tax_rate_list = ['10.20','10.30','12.24','12.36','14.00','14.50','15.0','18.00']
				if tax_rate_list[0] in account_name:
					tax_rate = 10.20
				if tax_rate_list[1] in account_name:
					tax_rate = 10.30
				if tax_rate_list[2] in account_name:
					tax_rate = 12.24
				if tax_rate_list[3] in account_name:
					tax_rate = 12.36
				if tax_rate_list[4] in account_name:
					tax_rate = 14.0
				if tax_rate_list[5] in account_name:
					tax_rate = 14.50
				if tax_rate_list[6] in account_name:
					tax_rate = 15.0
				if tax_rate_list[7] in account_name:
					tax_rate = 18.0
				if cust_id:
					if res.status == 'against_cancellation':
						srch1 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
												('status','in',('open','printed')),
												('pending_status','=','open'),
												('partner_id','=',cust_id),
												('tax_rate','=',tax_rate),
												('invoice_number','!=',''),
												('check_process_credit_note_st','=',False),
												('pending_amount','!=',0.0)])
						if srch1:
							final_lst.append(srch1)
							cr.execute('update invoice_adhoc_master set credit_invoice_id1=%s where id in %s',(res.id,tuple(srch1)))
						srch2 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
												('status','in',('open','printed','partially_writeoff')),
												('pending_status','=','pending'),
												('partner_id','=',cust_id),
												('tax_rate','=',tax_rate),
												('invoice_number','!=',''),
												('check_process_credit_note_st','=',False)])
						if srch2:
							final_lst.append(srch2)
							cr.execute('update invoice_adhoc_master set credit_invoice_id1=%s,credit_note_paid=%s where id in %s',(res.id,res.id,tuple(srch2)))
							cr.execute('update invoice_adhoc_master set credit_invoice_id1=Null where pending_amount=0.0')
						srch3 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
												('status','in',('paid','partially_writeoff')),
												('pending_status','=','paid'),
												('partner_id','=',cust_id),
												('tax_rate','=',tax_rate),
												('invoice_number','!=',''),
												('check_process_credit_note_st','=',False)])
						if srch3:
							final_lst.append(srch3)
							cr.execute('update invoice_adhoc_master set credit_note_paid=%s where id in %s',(res.id,tuple(srch3)))
							cr.execute('update invoice_adhoc_master set credit_note_paid=Null where grand_total_amount=total_writeoff_paid')
						if final_lst:
							flat_list = [item for sublist in final_lst for item in sublist]
							for rec in self.pool.get('invoice.adhoc.master').browse(cr,uid,flat_list):
								myString = ''
								l1=[]
								l2=[]
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
								self.pool.get('invoice.adhoc.master').write(cr,uid,rec.id,{'pms':myString,'concurrent_bool':True})
						srch_debit_note = self.pool.get('debit.note').search(cr,uid,[
											('customer_name','=',cust_id),
											('state_new','=','open'),
											('debit_note_no','!=',None),
											('pending_amount','!=',0.0),
											('check_process_dn','=',False)
											])
						 
						for debit in self.pool.get('debit.note').browse(cr,uid,srch_debit_note):
							if debit.customer_name.id == cust_id:
								self.pool.get('debit.note').write(cr,uid,debit.id,{'debit_credit_note_st_id':res.id})
				else:
					now_date=datetime.now().strftime('%Y-%m-%d')
					cr.execute("update invoice_adhoc_master a set credit_invoice_id1=%s where  (a.pending_amount + outstanding_invoice_function(a.id,'%s') ) > 0.0 and invoice_date <= '%s' and status != 'cancelled'"%(res.id,now_date,now_date))
		return True

	def save_outstanding_invoice(self, cr, uid,ids, context=None):
		count = 0.0
		flag = flag_paid = debit_nt_flag = False
		type1 = ""
		invs = []
		for rec in self.browse(cr,uid,ids):
			for invoice_line in rec.credit_st_outstanding_invoice:
				if invoice_line.check_credit_note_st:
					check_invoice = invoice_line.check_credit_note_st
					total_1= invoice_line.total_writeoff + invoice_line.writeoff_amount + invoice_line.total_writeoff_paid
					grand_total_1 = invoice_line.grand_total_amount
					if check_invoice == True:
						if invoice_line.invoice_date<'2017-07-01':
							raise osv.except_osv(('Alert!'),('Credit Note (ST) entry not allowed for invoices generated on/prior to 30-06-2017. Pass normal credit note entry for write-off.'))
						flag = True
					
					# if total_1 >= grand_total_1 and rec.writeoff_status=='partially_writeoff':
					# 			raise osv.except_osv(('Alert'),('Please select Fully writeoff'))
					invs.append(invoice_line.id)
			for invoice_line in rec.credit_st_paid_invoice:
				if invoice_line.check_credit_note_st_paid:
					check_invoice = invoice_line.check_credit_note_st_paid
					total_2= invoice_line.total_writeoff_paid + invoice_line.writeoff_amount_paid + invoice_line.total_writeoff
					grand_total_2 = invoice_line.grand_total_amount
					if check_invoice == True:
						if invoice_line.invoice_date<'2017-07-01':
							raise osv.except_osv(('Alert!'),('Credit Note (ST) entry not allowed for invoices generated on/prior to 30-06-2017. Pass normal credit note entry for write-off.'))
						flag_paid = True
						# if total_2 >= grand_total_2 and rec.writeoff_status=='partially_writeoff':
						# 		raise osv.except_osv(('Alert'),('Please select Fully writeoff'))
					invs.append(invoice_line.id)
			for invoice_line in rec.debit_note_cnst_one2many:
				if invoice_line.check_cn_debit:
					check_invoice = invoice_line.check_cn_debit
					if check_invoice == True:
						debit_nt_flag = True
						# if total_2 >= grand_total_2 and rec.writeoff_status=='partially_writeoff':
						# 		raise osv.except_osv(('Alert'),('Please select Fully writeoff'))
					invs.append(invoice_line.id)
		if (flag == False and flag_paid==False and debit_nt_flag==False):
			raise osv.except_osv(('Alert'),('Please select record in outstanding invoice OR Paid invoice OR Debit Note.'))
			
		if (flag == True and flag_paid==True and debit_nt_flag==True):
			raise osv.except_osv(('Alert'),('Please select one record in outstanding invoice OR Paid invoice OR Debit Note.'))	


		for res in self.browse(cr,uid,ids):
			cr_amount = res.credit_amount
			dr_amount = res.debit_amount
			type1 = res.type
			paid_flag= pending_flag = False
			if res.credit_st_paid_invoice == [] and res.credit_st_outstanding_invoice == [] and res.debit_note_cnst_one2many==[]:
				raise osv.except_osv(('Alert'),('No line to proceed.'))
				
			if res.credit_st_id.writeoff_status == 'partially_writeoff':
			        for line in res.credit_st_outstanding_invoice:
				        if line.check_credit_note_st == True:
				                pending_flag = True
				                if not line.writeoff_amount:
					                raise osv.except_osv(('Alert'),('Enter Writeoff Amount'))
					                
				                if line.writeoff_amount and res.status == 'against_cancellation':
				                        if line.writeoff_amount > line.pending_amount:
				                                raise osv.except_osv(('Alert'),('Writeoff amount should not be greater than Invoice Pending Amount'))
			                                count += line.writeoff_amount
			                                
			        for line in res.credit_st_paid_invoice:
				        if line.check_credit_note_st_paid == True:
				                paid_flag = True
				                if not line.writeoff_amount_paid:
					                raise osv.except_osv(('Alert'),('Enter Writeoff Amount'))
				                if line.writeoff_amount_paid and res.status == 'against_cancellation':
				                        print (line.writeoff_amount_paid + line.total_writeoff_paid),line.paid_amount,'lllllllll'
				                        if (line.writeoff_amount_paid + line.total_writeoff_paid) > line.paid_amount:
				                                raise osv.except_osv(('Alert'),('Writeoff amount should not be greater than Invoice Paid Amount'))
				                
				                count += line.writeoff_amount_paid
				                
		                	self.pool.get('invoice.adhoc.master').write(cr,uid,line.id,{'check_invoice':True})
			        for line in res.debit_note_cnst_one2many:
						if line.check_cn_debit == True:
							# inv_flag=True
							# if res.status_selection == 'against_ref_writeoff':
							if line.receipt_amount == 0.0:
								raise osv.except_osv(('Alert'),('Payment amount cannot be zero'))
							if line.receipt_amount > line.pending_amount:
								raise osv.except_osv(('Alert'),('Payment amount cannot be greater than Debit Note pending amount'))
							count = count + line.receipt_amount
							# invs.append(line.id)
							# self.pool.get('invoice.adhoc.master').write(cr,uid,line.id,{'check_invoice':True})
			# if res.credit_st_id.writeoff_status == 'fully_writeoff':
			#         for line in res.credit_st_outstanding_invoice:
					
			# 	        if line.check_credit_note_st == True:
			# 	                pending_flag = True
			# 	                if res.status == 'against_cancellation':
			# 	                        if (line.writeoff_amount) > line.pending_amount:
			# 	                                raise osv.except_osv(('Alert'),('Writeoff amount should not be greater than Invoice Pending Amount'))
			#                                 if (line.writeoff_amount) < line.pending_amount:
			# 	                                raise osv.except_osv(('Alert'),('Writeoff amount should not be less than Invoice Pending Amount'))
			#                                 count += line.writeoff_amount
				
			#         for line in res.credit_st_paid_invoice:
			# 	        if line.check_credit_note_st_paid == True:
			# 	                paid_flag = True
			# 	                if res.status == 'against_cancellation':
				                       
			# 	                        if (line.writeoff_amount_paid+line.total_writeoff_paid) > line.paid_amount:
			# 	                                raise osv.except_osv(('Alert'),('Writeoff amount should not be greater than Invoice Paid Amount'))
			#                                 if (line.writeoff_amount_paid+line.total_writeoff_paid) < line.paid_amount:
			# 	                                raise osv.except_osv(('Alert'),('Writeoff amount should not be less than Invoice Paid Amount'))
				                
			# 	                count += line.writeoff_amount_paid	       
		
		 #                self.pool.get('invoice.adhoc.master').write(cr,uid,line.id,{'check_invoice':True})
		
			if type1== 'debit':
				self.write(cr,uid,rec.id,{'debit_amount':count})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':count})
			if len(invs) > 0:
				self.write(cr,uid,ids[0],{'inv_selected':True})
			else:
				self.write(cr,uid,ids[0],{'inv_selected':False})	

		return {'type': 'ir.actions.act_window_close'}

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
						view_name = 'gst_account_credit_against_ref_form_st'
						name_wizard ="Outstanding Invoices"
						objit='gst_accounting'
				if acc_selection == 'advance' and res.type == 'debit':# HHH 3nov adjusting CFOB entries reflecting under advance
					self.show_details_cr(cr,uid,ids,context=context)
					view_name = 'against_advance_form_cr'
					name_wizard = "Advance Payment Details"
					objit='account_sales_branch'
				models_data=self.pool.get('ir.model.data')
				if view_name :
					form_view=models_data.get_object_reference(cr, uid, objit, view_name )
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

class debit_note(osv.osv):
	_inherit='debit.note'
	_columns={

		'debit_credit_note_st_id':fields.many2one('credit.note.line.st','Credit Note St Line'),
	}
debit_note()

class invoice_receipt_history(osv.osv):
	_inherit='invoice.receipt.history'
	_columns={
		'invoice_receipt_history_debit_id':fields.many2one('credit.note.line.st','Invoice Receipt history'),
	}
invoice_receipt_history()

class reason_for_issue_of_doc(osv.osv):
	_name='reason.for.issue.of.doc'
	_columns={
		'name':fields.char('Name',size=1000),
	}
reason_for_issue_of_doc()