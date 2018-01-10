# Version 1.0.036 --> changes related to  CFOB entries amount of same branch collection 
# Version 1.0.037 --> changes related to  CFOB entries amount of same branch collection for 14%
# Version 1.0.045 --> changes related to other collection on the basis of the tax rate / others and not just in others
# Version 1.0.049 --> changes related to other collection on Cfob entries with other as tax rate segerigated
# Version 1.0.050 --> changes related to imported advance reflecting
# Version 1.0.051 --> changes related to addition of invoice_adhoc_one2many wizard values
# version 1.0.054 --> Changes Related to Non-Taxable transaction process
# version 1.0.059 --> Changes Related to Cheque Bounce
# version 1.0.060 --> Changes Related to cfob entries
# version 1.0.061 --> Changes Related to NON TAXABLE Column for CFOB Scenario

from datetime import date,datetime, timedelta
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

class monthly_report(osv.osv):
	_inherit = 'monthly.report'

	def stmt_collection(self, cr, uid, ids, from_date, to_date, context=None):
	### method to get data for SOC report
		iob_total = iob_total_second = iob_total_three = iob_total_cheque = iob_total_cheque_second = 0.0
		iob_total_cheque_three = itds_total = cash_total = sd_total = others_collect = others = taxable1_total = taxable2_total = 0.0
		receipt_no = result = ''
		
		taxable3_total = taxable3_total_cheque = taxable4_total = taxable4_total_cheque = 0.0  # for 14.0 % HHH
		taxable5_total = taxable5_total_cheque = taxable6_total = taxable6_total_cheque = 0.0  # for 14.0 % HHH
		gross_amt = gross_amt_total = taxable_total_14_50 = taxable_total_14_50_cheque = 0.0 
		taxable7_total = taxable7_total_cheque = 0.0
		against_ref_18=0.0 
		count=0
		for res in self.browse(cr,uid,ids):
			self.write(cr,uid,res.id,{'iob_one_total':0.0,
						'sd_total':0.0,
						'cash_total':0.0,
						'itds_total':0.0,
						'others_total':0.0,
						'others_collect_total':0.0,
						'gross_amount_total':0.0,
						  })

			for ln in res.stmt_collection_line:
				self.pool.get('statement.collection').write(cr,uid,ln.id,{'collection_id':None})

#Sales Receipts :Soc report consist of collection of sales receipts 
			srch = self.pool.get('account.sales.receipts').search(cr,uid,[
										('id','>',0),
										('receipt_date','>=',from_date),
										('receipt_date','<=',to_date),
										('receipt_no','!=',''),
										('state','!=','draft')],order="id")
			count = 0
			sd_credit_amount = sd_iob_one_dr_amt = iob_one_dr_amt = cash_dr_amt = 0.0
			sd_dr_amount = advance_iob_one_dr_amt = advance_cash_dr_amt  = 0.0
			iob_one_debit_amt = iob_one_second_dr_amt = iob_one_three_dr_amt =cash_debit_amt = 0.0
			account_name = account_selection = party_name = narration = ''
			# t1=[]
			for rec in self.pool.get('account.sales.receipts').browse(cr,uid,srch):
				flag=False
				against_ref_cr_amt_10_30=against_ref_cr_amt_12_24=against_ref_cr_amt=against_ref_cr_amt_14_00=0.0
				against_ref_cr_amt_14_50=against_ref_cr_amt_15_0=against_ref_cr_amt_18_0=against_ref_cr_amt_NT=others_cr_amt=itds_dr_amt=0.0
				sd_credit_amount = sd_iob_one_dr_amt = iob_one_dr_amt = cash_dr_amt = 0.0
				sd_dr_amount = advance_iob_one_dr_amt = advance_cash_dr_amt  = 0.0
				iob_one_debit_amt = iob_one_second_dr_amt = iob_one_three_dr_amt =cash_debit_amt = 0.0
				account_name = account_selection = party_name = narration = ''
				t1=[]
				if rec.customer_name.name=='CFOB': # and rec.import_flag == False
					for j in rec.sales_receipts_one2many:
						if j.account_id.account_selection=='against_ref':
							for k in j.sales_other_cfob_one2many:
								t1.extend([k.customer_cfob])#ppppp
						if j.account_id.account_selection=='sundry_deposit':
							for k in j.sundry_deposit_one2many:
								t1.extend([k.customer_name_char])
					party_name=', '.join(set(filter(bool,t1)))  #duplication in SOC
					
				else:
					first_name = rec.customer_name.name
					last_name = '' #rec.customer_name.last_name
					full_name= [first_name,last_name]
					party_name = ' '.join(filter(bool,full_name))
				receipt_date = rec.receipt_date
				receipt_no = rec.receipt_no
				# narration = rec.narration
				if rec.import_flag == False:
					for line in rec.sales_receipts_one2many:
						payment_method = line.payment_method
						acccount_status =  line.acc_status
						account_selection = line.account_id.account_selection
					#### Non-Taxable receipts are excluded here
						if account_selection == 'against_ref' and rec.customer_name != 'CFOB' :
						#### For Invoice receipt History WiZard
							for ln in line.invoice_adhoc_history_one2many:  # for 14.0 % HHH
								invoice_type=False
								if ln.check_invoice == True:
										invoice_number = ln.invoice_number
										search_invoice = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','=',invoice_number)]) 
										if search_invoice:
											invoice_type=self.pool.get('invoice.adhoc.master').browse(cr,uid,search_invoice[0]).invoice_type
										tax_rate = ln.tax_rate
										if tax_rate == '10.30': 
											against_ref_cr_amt_10_30 += ln.invoice_paid_amount
										if tax_rate == '12.24': 
											against_ref_cr_amt_12_24 += ln.invoice_paid_amount
										if tax_rate == '12.36':
											against_ref_cr_amt += ln.invoice_paid_amount
										if tax_rate == '14.0': 
											against_ref_cr_amt_14_00 += ln.invoice_paid_amount
										if tax_rate == '14.5':  # for 14.50 % sagar
											against_ref_cr_amt_14_50 += ln.invoice_paid_amount
										if tax_rate == '15.0':  # for 14.50 % sagar
											against_ref_cr_amt_15_0 += ln.invoice_paid_amount
										if tax_rate == '18.0' and invoice_type!='Scrap Sale Invoice':  # for 14.50 % sagar
											against_ref_cr_amt_18_0 += ln.invoice_paid_amount
										if tax_rate == 'non_taxable':  # for 14.50 % sagar
											against_ref_cr_amt_NT += ln.invoice_paid_amount
										if invoice_type =='Scrap Sale Invoice':  # for 14.50 % sagar
											others_cr_amt += ln.invoice_paid_amount
							tax_rate_list=['10.30','12.24','12.36','14.0','14.5','15.0','Non Taxable','Others','18.0']
							for ln in line.debit_note_one2many:
								if ln.check_debit == True:
									for x in ln.debit_note_one2many:
										acc_name=x.account_id.name
										if tax_rate_list[0] in acc_name: 
											against_ref_cr_amt_10_30 += ln.paid_amount
										if tax_rate_list[1] in acc_name: 
											against_ref_cr_amt_12_24 += ln.paid_amount
										if tax_rate_list[2] in acc_name:
											against_ref_cr_amt += ln.paid_amount
										if tax_rate_list[3] in acc_name:
											against_ref_cr_amt_14_00 += ln.paid_amount
										if tax_rate_list[4] in acc_name:  # for 14.50 % sagar
											against_ref_cr_amt_14_50 += ln.paid_amount
										if tax_rate_list[5] in acc_name:  # for 14.50 % sagar
											against_ref_cr_amt_15_0 += ln.paid_amount
										if tax_rate_list[6] in acc_name:  # for 14.50 % sagar
											against_ref_cr_amt_NT += ln.paid_amount
										if tax_rate_list[7] in acc_name:  # for 14.50 % sagar
											others_cr_amt += ln.paid_amount
										if tax_rate_list[8] in acc_name:  # for 14.50 % sagar
											against_ref_cr_amt_18_0 += ln.paid_amount	
						#### For Invoice receipt History WiZard
                                                
					######## For Non Taxable Entries 
						# if account_selection == 'against_ref' and ('Non' in line.account_id.name) :
						# 		for ln in line.invoice_adhoc_history_one2many:  # for 14.0 % HHH
						# 			if ln.check_invoice == True and 'NT' in ln.invoice_number  and ln.tax_rate == 'non_taxable':
						# 				against_ref_cr_amt_NT += line.credit_amount
								# for ln in line.debit_note_one2many:
								# 	if ln.check_debit == True:
								# 		debit_ids = self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',ln.debit_note_no)])
								# 		browse_obj = self.pool.get('debit.note').browse(cr,uid,debit_ids[0])
								# 		for note in browse_obj.debit_note_one2many:
								# 			if note.account_id.name == 'Sundry Debtors Service (Non Taxable)':
								# 				against_ref_cr_amt_NT += note.debit_amount
						if line.acc_status == 'others' and account_selection == 'against_ref' and ('Non' in line.account_id.name) and line.customer_name.name=='CFOB':
							against_ref_cr_amt_NT = 0.0
							for ln in line.invoice_cfob_one2many:  # for 14.0 % HHH
								if ln.cfob_chk_invoice == True and  ln.tax_rate == 'non_taxable':
									search_amt = self.pool.get('invoice.receipt.history').search(cr,uid,[
									('invoice_receipt_history_id','=',ln.id),
									('receipt_id_history','=',line.id)])
									if search_amt:
										for paid_amt in self.pool.get('invoice.receipt.history').browse(cr,uid,search_amt):
											paid_amount +=paid_amt.invoice_paid_amount
											
								if 'NT' in ln.invoice_number:
									if ln.cfob_chk_invoice == True:
										tax_rate_cf = ln.tax_rate
										if tax_rate_cf == 'non_taxable':
											against_ref_cr_amt_NT += paid_amount
					######## For Non Taxable Entries

						# if line.acc_status == 'against_ref' and account_selection == 'against_ref':
						# 	if '12.36' in line.account_id.name:
						# 		against_ref_cr_amt +=  line.credit_amount
						# 	elif '14.0' in line.account_id.name: 	
						# 		against_ref_cr_amt_14_00 += line.credit_amount
						# 	elif '10.30' in line.account_id.name: 
						# 		against_ref_cr_amt_10_30 += line.credit_amount
						# 	elif '12.24' in line.account_id.name: 
						# 		against_ref_cr_amt_12_24 += line.credit_amount
						# 	elif '14.5' in line.account_id.name:           # for 14.50 % sagar
						# 		against_ref_cr_amt_14_50 += line.credit_amount
						# 	elif '15.0' in line.account_id.name:           # for 14.50 % sagar
						# 		against_ref_cr_amt_15_0 += line.credit_amount

					#### Advance Entries
						if account_selection == 'advance':
							if '12.36' in line.account_id.name:
								against_ref_cr_amt +=  line.credit_amount
							elif '14.0' in line.account_id.name: 	
								against_ref_cr_amt_14_00 += line.credit_amount
							elif '10.30' in line.account_id.name: 
								against_ref_cr_amt_10_30 += line.credit_amount
							elif '12.24' in line.account_id.name: 
								against_ref_cr_amt_12_24 += line.credit_amount
							elif '14.5' in line.account_id.name:           # for 14.50 % sagar
								against_ref_cr_amt_14_50 += line.credit_amount
							elif '15.0' in line.account_id.name:           # for 14.50 % sagar
								against_ref_cr_amt_15_0 += line.credit_amount
							elif '18.0' in line.account_id.name or '18.00' in line.account_id.name:           # for 14.50 % sagar
								against_ref_cr_amt_18_0 += line.credit_amount
					#### Advance Entries


					#### Wizard where we settle our own brances invoice
						paid_amount= 0.0
						if acccount_status == 'others' and account_selection == 'against_ref' and line.customer_name.name=='CFOB':
							against_ref_cr_amt = against_ref_cr_amt_14_00 =against_ref_cr_amt_10_30 = against_ref_cr_amt_12_24 = against_ref_cr_amt_14_50= against_ref_cr_amt_15_0=against_ref_cr_amt_18_0 =0.0
							for cfob_entry in  line.invoice_cfob_one2many:
								if cfob_entry.cfob_chk_invoice == True:
									search_amt = self.pool.get('invoice.receipt.history').search(cr,uid,[
												('invoice_receipt_history_id','=',cfob_entry.id),
												('receipt_id_history','=',line.id)])
									if search_amt:
										for paid_amt in self.pool.get('invoice.receipt.history').browse(cr,uid,search_amt):
											paid_amount =paid_amt.invoice_paid_amount  #sagar remove '+' 27 OCT
	
								if 'NT' not in cfob_entry.invoice_number:
									if cfob_entry.cfob_chk_invoice == True:
										tax_rate_cf = cfob_entry.tax_rate
										if tax_rate_cf == '12.36':
											against_ref_cr_amt += paid_amount
										elif tax_rate_cf == '14.0': # for 14.0 % HHH
											against_ref_cr_amt_14_00 += paid_amount
										elif tax_rate_cf == '10.30':
											against_ref_cr_amt_10_30 += paid_amount
										elif tax_rate_cf == '12.24': 
											against_ref_cr_amt_12_24 += paid_amount
										elif tax_rate_cf == '14.5':    # for 14.50 % sagar
											against_ref_cr_amt_14_50 += paid_amount
										elif tax_rate_cf == '15.0':    # for 14.50 % sagar
											against_ref_cr_amt_15_0 += paid_amount
										elif tax_rate_cf == '18.0' or tax_rate_cf == '18.00':    # for 14.50 % sagar
											against_ref_cr_amt_18_0 += paid_amount
					#### Wizard where we settle our own brances invoice

					#### Wizard where we settle other brances invoice [CFOB]
						#### amount is differentiated based on 12%/14% and other.(first only others).
						if acccount_status == 'others' and account_selection == 'against_ref' and line.customer_name.name=='CFOB':
							count=count+1
							branch_ln_str = ''
							t2=[]
							if line.sales_other_cfob_one2many:
								for line_in in line.sales_other_cfob_one2many:
									if line_in.check_cfob_sales_process:
										tax_rate_other = line_in.tax_rate
										if tax_rate_other == '12.36': #'taxable_12_36':
											against_ref_cr_amt += line_in.ref_amount
										elif tax_rate_other == '14.0': #'taxable_14_00': 
											against_ref_cr_amt_14_00 += line_in.ref_amount
										elif tax_rate_other == '10.30': #'taxable_10_30': 
											against_ref_cr_amt_10_30 += line_in.ref_amount
										elif tax_rate_other == '12.24': #'taxable_12_24': 
											against_ref_cr_amt_12_24 += line_in.ref_amount
										elif tax_rate_other == 'non_taxable' and ('Non' in line.account_id.name): # for Non Taxable
											against_ref_cr_amt_NT += line_in.ref_amount
										elif tax_rate_other == '14.5': #'taxable_14_5': 
											against_ref_cr_amt_14_50 += line_in.ref_amount
										elif tax_rate_other == '15.0': #'taxable_15_0': 
											against_ref_cr_amt_15_0 += line_in.ref_amount
										elif tax_rate_other == '18.0' or tax_rate_other == '18.00': #'taxable_15_0': 
											against_ref_cr_amt_18_0 += line_in.ref_amount
											# against_ref_18+=line_in.ref_amount
											if count>1:
												flag=True
												against_ref_18=against_ref_cr_amt_18_0
										if tax_rate_other == 'others':
											others_cr_amt += line_in.ref_amount
											
									branch_name = str(line_in.branch_name.name) if line_in.branch_name else ''
									narration = rec.narration
									t2.extend([branch_name]) #ppp
									branch_ln_str = ' / '.join(set(filter(bool,t2)))
									narration = branch_ln_str
							else:
								others_cr_amt += line.credit_amount####
								if line.type == 'credit':
									account_name = str(line.account_id.name) 
								narration = narration if narration else '' + '' + account_name
				#### Wizard where we settle other brances invoice [CFOB]
						if account_selection == 'cash':
							cash_dr_amt = line.debit_amount
	
						if account_selection == 'iob_one' and line.account_id.receive_bank_no == 'bank_one':
							iob_one_dr_amt = line.debit_amount
							
						if account_selection == 'iob_one' and line.account_id.receive_bank_no == 'bank_two':
							iob_one_second_dr_amt = line.debit_amount
						
						#8aug16	
						if account_selection == 'iob_one' and line.account_id.receive_bank_no == 'bank_three':
							iob_one_three_dr_amt = line.debit_amount
	
						if account_selection == 'security_deposit':
							if line.type == 'credit':                   #SD Credit in Other collection  by sagar
								others_cr_amt += line.credit_amount
							else:
								sd_dr_amount = line.debit_amount
						if account_selection == 'sundry_deposit': 			
							if line.type == 'credit':
								others_cr_amt += line.credit_amount
								
						if acccount_status == 'others' and rec.customer_name.name != 'CFOB' :
							others_cr_amt  += line.credit_amount
	
						if account_selection == 'itds_receipt':
						        if line.type == 'debit':
        							itds_dr_amt = line.debit_amount
        					        if line.type == 'credit':
        					                others_cr_amt = line.credit_amount

					narration = 'Cancelled' if rec.cancel_boolean else narration	
					result = self.pool.get('statement.collection').create(cr,uid,{
										'collection_id':res.id,
										'iob_acc_one':iob_one_dr_amt if iob_one_dr_amt else 0.0,
										'iob_acc_one_second':iob_one_second_dr_amt if iob_one_second_dr_amt else 0.0,
										
										'iob_acc_one_three':iob_one_three_dr_amt if iob_one_three_dr_amt else 0.0,#8aug16
										
										'cash':cash_dr_amt if cash_dr_amt else 0.0,
										'security_deposit':sd_dr_amount if sd_dr_amount else '',
										'party_name':party_name if party_name else '',
										'date':receipt_date,
										'receipt_no':receipt_no,
										'itds':itds_dr_amt if itds_dr_amt else 0.0,
										'other_collection':others_cr_amt if others_cr_amt else 0.0,
										'taxable3':against_ref_cr_amt,
										'taxable4':against_ref_cr_amt_14_00, 
										'taxable5':against_ref_cr_amt_NT, # for Non Taxable
										'taxable_14_50':against_ref_cr_amt_14_50, 
										'taxable6':against_ref_cr_amt_15_0,
										'taxable7':against_ref_18 if flag else against_ref_cr_amt_18_0, 
										'remarks':narration if narration else '',})

##cheque bounce Entries: The Cheque bounce entries are deducted from the gross total
			
			srch_cheque = self.pool.get('cheque.bounce').search(cr,uid,[
										('id','>',0),
										('payment_date','>=',from_date),
										('payment_date','<=',to_date),
										('payment_no','!=','')],order="id")
										
			for rec_others in self.pool.get('cheque.bounce').browse(cr,uid,srch_cheque):
				or_iob_one_dr_amt = or_iob_one_second_dr_amt = or_iob_one_three_dr_amt =against_ref_cr_amt_15_0 =0.0 
				or_cash_dr_amt = against_ref_cr_amt= credit_amount = credit_amount1 = against_ref_cr_amt_14_50=0.0
				against_ref_cr_amt_14_00= itds_amt = sd_amt=against_ref_cr_amt_10_30=against_ref_cr_amt_12_24=0.0
				against_ref_cr_amt_18_0 =against_ref_cr_amt_NT=0.0
				remarks = rec_others.narration
				cust_name = rec_others.partner_id.name
				receipt_no = rec_others.payment_no
				receipt_date = rec_others.payment_date
				
############################# cheque bounce 
				for line in rec_others.cheque_bounce_lines:
					for line_account in line.debited_invoice_line_new:
						if line_account.cheque_bounce_boolean :
							tax_rate = line_account.tax_rate
							if tax_rate == '10.30': 
								against_ref_cr_amt_10_30 += line_account.invoice_paid_amount####
							elif tax_rate == '12.24': 
								against_ref_cr_amt_12_24 += line_account.invoice_paid_amount####
							elif tax_rate == '12.36':
								against_ref_cr_amt += line_account.invoice_paid_amount####
							elif tax_rate == '14.0': # for 14.0 % HHH
								against_ref_cr_amt_14_00 += line_account.invoice_paid_amount####
							elif tax_rate == '14.5': # for 14.50 % sagar
								against_ref_cr_amt_14_50 += line_account.invoice_paid_amount####
							elif tax_rate == '15.0': # for 14.50 % sagar
								against_ref_cr_amt_15_0 += line_account.invoice_paid_amount####
							elif tax_rate == '18.0' or tax_rate == '18.00': # for 14.50 % sagar
								against_ref_cr_amt_18_0 += line_account.invoice_paid_amount####
							if tax_rate == 'others':
								others_cr_amt += line_account.invoice_paid_amount
							if tax_rate == 'non_taxable':
								against_ref_cr_amt_NT += line_account.invoice_paid_amount
					tax_rate_list=['10.30','12.24','12.36','14.0','14.5','15.0','Non Taxable','18.0']
					for ln in line.debit_note_one2many:
						if ln.dn_cheque_bounce == True:
							acc_name=line.account_id.name
							if tax_rate_list[0] in acc_name: 
								against_ref_cr_amt_10_30 += ln.paid_amount
							if tax_rate_list[1] in acc_name: 
								against_ref_cr_amt_12_24 += ln.paid_amount
							if tax_rate_list[2] in acc_name:
								against_ref_cr_amt += ln.paid_amount
							if tax_rate_list[3] in acc_name:
								against_ref_cr_amt_14_00 += ln.paid_amount
							if tax_rate_list[4] in acc_name:  # for 14.50 % sagar
								against_ref_cr_amt_14_50 += ln.paid_amount
							if tax_rate_list[5] in acc_name:  # for 14.50 % sagar
								against_ref_cr_amt_15_0 += ln.paid_amount
							if tax_rate_list[6] in acc_name:  # for 14.50 % sagar
								against_ref_cr_amt_NT += ln.paid_amount	
							if tax_rate_list[7] in acc_name:  # for 14.50 % sagar
								against_ref_cr_amt_18_0 += ln.paid_amount
################################# cheque bounce  end
					
					if line.account_id.account_selection == 'iob_one' and  line.account_id.receive_bank_no == 'bank_one':
						or_iob_one_dr_amt = line.credit_amount
	
					if line.account_id.account_selection == 'iob_one' and  line.account_id.receive_bank_no == 'bank_two':
						or_iob_one_second_dr_amt = line.credit_amount
					
					#8aug16
					if line.account_id.account_selection == 'iob_one' and  line.account_id.receive_bank_no == 'bank_three':
						or_iob_one_three_dr_amt = line.credit_amount
					
					if line.account_id.account_selection == 'cash':
						or_cash_dr_amt = line.credit_amount

					if line.account_id.account_selection == 'itds_receipt':
					        itds_amt =line.credit_amount
					if line.account_id.account_selection == 'security_deposit' and 'Security' in line.account_id.name:
					        sd_amt	= line.credit_amount

				result = self.pool.get('statement.collection').create(cr,uid,{
									'collection_id':res.id,
									'party_name':cust_name if cust_name else '',
									'date':receipt_date,
									'receipt_no':receipt_no,
									'other_collection':-credit_amount if credit_amount else -credit_amount1,
									'iob_acc_one_cheque':-or_iob_one_dr_amt if -or_iob_one_dr_amt else 0.0,
									'iob_acc_one_second_cheque':-or_iob_one_second_dr_amt if -or_iob_one_second_dr_amt else 0.0,
									
									'iob_acc_one_three_cheque':-or_iob_one_three_dr_amt if -or_iob_one_three_dr_amt else 0.0,#8aug16
									
									'itds': -itds_amt,
									'security_deposit':-sd_amt,
									'cash':-or_cash_dr_amt if -or_cash_dr_amt else 0.0,
									'taxable1_cheque':-against_ref_cr_amt_10_30,
									'taxable2_cheque':-against_ref_cr_amt_12_24,
									'taxable3_cheque':-against_ref_cr_amt,
									'taxable4_cheque':-against_ref_cr_amt_14_00, # for 14.0 % HHH
									'taxable5_cheque':-against_ref_cr_amt_NT, # for NON Taxable 
									'taxable_14_50_cheque':-against_ref_cr_amt_14_50,  # for 14.50 %
									'taxable6_cheque':-against_ref_cr_amt_15_0,
									'taxable7_cheque':-against_ref_cr_amt_18_0,   
									'remarks':remarks if remarks else 'Cheque Bounce',
									})

		for gross in self.browse(cr,uid,ids):
			for line1 in gross.stmt_collection_line:	#8aug16
				gross_amt = line1.iob_acc_one + line1.iob_acc_one_second + line1.iob_acc_one_three + line1.cash + line1.security_deposit + line1.itds + line1.others_cfob + line1.iob_acc_one_cheque+ line1.iob_acc_one_second_cheque + line1.iob_acc_one_three_cheque
				self.pool.get('statement.collection').write(cr,uid,line1.id,{'gross_amount':gross_amt})

		for cal in self.browse(cr,uid,ids):
			self.write(cr,uid,cal.id,{
								'iob_one_total':0.0,
								'cash_total':0.0,
								'sd_total':0.0,
								'itds_total':0.0,
								'others_collect_total':0.0,
								'others_total':0.0,
								'taxable_total3':0.0,
								'taxable_total4':0.0, 
								'taxable_total5':0.0,  # for Non Taxable
								'taxable_total7':0.0,
								'gross_amount_total':0.0,
								'taxable_total_14_50':0.0,}) #14.50% sagar
			for cal_ln in cal.stmt_collection_line:
				iob_acc_one = cal_ln.iob_acc_one
				iob_acc_one_second=cal_ln.iob_acc_one_second
				
				iob_acc_one_three=cal_ln.iob_acc_one_three #8aug16
				
				iob_acc_one_cheque = cal_ln.iob_acc_one_cheque
				iob_acc_one_second_cheque = cal_ln.iob_acc_one_second_cheque
				iob_acc_one_three_cheque = cal_ln.iob_acc_one_three_cheque #8aug16
				cash = cal_ln.cash
				security_deposit = cal_ln.security_deposit
				itds = cal_ln.itds
				other_collection = cal_ln.other_collection
				others_line = cal_ln.others_cfob
				taxable1 = cal_ln.taxable1
				taxable2 = cal_ln.taxable2
				taxable3 = cal_ln.taxable3
				taxable3_cheque = cal_ln.taxable3_cheque
				taxable4 = cal_ln.taxable4  # for 14.0 % HHH
				taxable4_cheque = cal_ln.taxable4_cheque  # for 14.0 % HHH
				taxable_14_50= cal_ln.taxable_14_50                     # for 14.50 % sagar
				taxable_14_50_cheque= cal_ln.taxable_14_50_cheque       # for 14.50 % sagar
				taxable6 = cal_ln.taxable6  # for 14.0 % HHH
				taxable6_cheque = cal_ln.taxable6_cheque  # for 14.0 % HHH
				taxable7 = cal_ln.taxable7  # for 14.0 % HHH
				taxable7_cheque = cal_ln.taxable7_cheque
				taxable5 = cal_ln.taxable5 # for Non Taxable
				taxable5_cheque = cal_ln.taxable5_cheque # for Non Taxable
				gross_amount = cal_ln.gross_amount	

			# Here the Receipt Number which Contains 'CB' i.e Cheque Bounce Entry will be deducted from Gross Amount
				if iob_acc_one:
					iob_total += iob_acc_one
					
				if iob_acc_one_second:
					iob_total_second += iob_acc_one_second
				
				if iob_acc_one_three:
					iob_total_three +=  iob_acc_one_three

				if iob_acc_one_cheque:
					iob_total_cheque += iob_acc_one_cheque
				if iob_acc_one_second_cheque:
					iob_total_cheque_second += iob_acc_one_second_cheque
						
				#8aug16	
				if iob_acc_one_three_cheque:
					iob_total_cheque_three += iob_acc_one_three_cheque
				
				if cash:
					cash_total += cash
					
				if security_deposit:
				        sd_total += security_deposit
				if itds:
				        itds_total += itds
				        
				if other_collection:
					others_collect = others_collect + other_collection
				if others_line:
					others += others_line
				if taxable1:
					taxable1_total += taxable1
					
				if taxable2:
					taxable2_total += taxable2
					
				if taxable3:
					taxable3_total += taxable3
					
				if taxable3_cheque:
					taxable3_total_cheque += taxable3_cheque
					
				if taxable4: 
					taxable4_total += taxable4
					
				if taxable4_cheque: 
					taxable4_total_cheque += taxable4_cheque
					
				if taxable_14_50:                                                    # for 14.50 % sagar >>>
					taxable_total_14_50 +=  taxable_14_50
					
				if taxable_14_50_cheque: 
					taxable_total_14_50_cheque += taxable_14_50_cheque
					   
				if taxable6: 
					taxable6_total += taxable6
					
				if taxable6_cheque: 
					taxable6_total_cheque += taxable6_cheque	
				if taxable7: 
					taxable7_total += taxable7
					
				if taxable7_cheque: 
					taxable7_total_cheque += taxable7_cheque
				if taxable5: # for Non Taxable
				        taxable5_total += taxable5
				if taxable5_cheque: # for Non Taxable
					taxable5_total_cheque -= taxable5_cheque
					
				if gross_amount:
					gross_amt_total += gross_amount

			if iob_total >= iob_total_cheque:
				iob_total +=iob_total_cheque
				iob_total_cheque=0.0
			else:
				iob_total_cheque += iob_total
				iob_total=0.0
				
			if iob_total_second >= iob_total_cheque_second:
				iob_total_second += iob_total_cheque_second
				iob_total_cheque_second=0.0
			else:
				iob_total_cheque_second += iob_total_second
				iob_total_second=0.0
			
			#8aug16	
			if iob_total_three >= iob_total_cheque_three:
				iob_total_three += iob_total_cheque_three
				iob_total_cheque_three=0.0
			else:
				iob_total_cheque_three += iob_total_three
				iob_total_three=0.0

			if taxable3_total > taxable3_total_cheque:
				taxable3_total += taxable3_total_cheque
				taxable3_total_cheque=0.0
			else:
				taxable3_total_cheque += taxable3_total
				taxable3_total=0.0
				
			if taxable4_total > taxable4_total_cheque: # for 14.0 % HHH
				taxable4_total += taxable4_total_cheque
				taxable4_total_cheque=0.0
			else:  # for 14.0 % HHH
				taxable4_total_cheque += taxable4_total
				taxable4_total=0.0
			
			if taxable_total_14_50 > taxable_total_14_50_cheque:                              # for 14.50 % sagar
				taxable_total_14_50 += taxable_total_14_50_cheque
				taxable_total_14_50_cheque=0.0
			else: 
				taxable_total_14_50_cheque += taxable_total_14_50
				taxable_total_14_50=0.0	 
				                                      
			if taxable6_total > taxable6_total_cheque: 
				taxable6_total += taxable6_total_cheque
				taxable6_total_cheque=0.0
			else:  
				taxable6_total_cheque += taxable6_total
				taxable6_total=0.0
			if taxable7_total > taxable7_total_cheque: 
				taxable7_total += taxable7_total_cheque
				taxable7_total_cheque=0.0
			else:  
				taxable7_total_cheque += taxable7_total
				taxable7_total=0.0		
			if taxable5_total > taxable5_total_cheque: # for Non Taxable
				taxable5_total += taxable5_total_cheque
				taxable5_total_cheque=0.0
			else:  # for Non Taxable
				taxable5_total_cheque += taxable5_total
				taxable5_total=0.0
			self.write(cr,uid,cal.id,{
				'iob_one_total':iob_total,
				'iob_one_total_second':iob_total_second,
				
				'iob_one_total_three':iob_total_three,#8aug16
				
				'iob_one_total_cheque':iob_total_cheque,
				'cash_total':cash_total,
				'sd_total':sd_total,
				'itds_total':itds_total,
				'others_collect_total':others_collect,
				'others_total':others,
				'taxable_total1':taxable1_total,
				'taxable_total2':taxable2_total,
				'taxable_total3':taxable3_total,
				'taxable_total3_cheque':taxable3_total_cheque,
				'taxable_total4':taxable4_total,
				'taxable_total4_cheque':taxable4_total_cheque, # for 14.0 % HHH
				'taxable_total5':taxable5_total, # for Non Taxable
				'taxable_total5_cheque':taxable5_total_cheque, # for Non Taxable
				'gross_amount_total':gross_amt_total,
				'taxable_total_14_50':taxable_total_14_50,
				'taxable_total_14_50_cheque':taxable_total_14_50_cheque,
				'taxable_total6':taxable6_total,
				'taxable_total6_cheque':taxable6_total_cheque, # for 14.0 % HHH
				'taxable_total7':taxable7_total,
				'taxable_total7_cheque':taxable7_total_cheque,
				})
		return True	

monthly_report()
