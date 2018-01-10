# Version 1.0.012 --->  Added Branch name for the refence number for the other cfob 
#version 1.0.041 to remove hardcoded address,email,phoneno,website from report
# version 1.0.056 --> Changes Related to DD receipt print 09 oct 15
import time
from report import report_sxw
from tools.translate import _
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in
from corporate_address import *

class gst_cheque(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):

		super(gst_cheque, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'amount_to_text_in': amount_to_text_in,
			'sales_receipt_cheque':self.sales_receipt_cheque,
			'sales_receipt_cheque_duplicate':self.sales_receipt_cheque_duplicate,
			'get_cust_add':self.get_cust_add,
			'get_phone_landline':self.get_phone_landline,
			'get_branch_addr':self.get_branch_addr,
			'get_corporate_address':self.get_corporate_address,
			'get_registered_office_address':self.get_registered_office_address,
			'cheque_str':self.cheque_str,
			'get_corporate_address':self.get_corporate_address,
			'get_parent_branch':self.get_parent_branch,
			'get_primary_address': self.get_primary_address,
			'get_billing_address': self.get_billing_address,
			'get_line_data': self.get_line_data,
			'get_total_value': self.get_total_value,
			'get_invoice_details': self.get_invoice_details
		})

	def cheque_str(self,self_id):
		return str(self_id).zfill(6)
	def get_corporate_address(self):
	   return get_corporate_address(self)

	def get_registered_office_address(self):
	   return get_registered_office_address(self)

	def get_branch_addr(self,self_id):
		return get_branch_addr(self,self_id)

	def get_phone_landline(self,self_id,no=0):
		cr = self.cr
		uid = self.uid
		dic = {}
		for rec in self.pool.get('account.sales.receipts').browse(cr,uid,[self_id]):
			for ln in rec.sales_receipts_one2many:
				customer_name= ln.partner_id.id if ln.partner_id else rec.customer_name.id
				if no == 3:
					dic['email']= ln.partner_id.email if ln.partner_id else rec.customer_name.email if rec.customer_name else ''
				srch_id = self.pool.get('phone.number.child').search(cr,uid,[('partner_id','=',customer_name)])
				if srch_id:
					number_ln_str = number_mob_str =''
					landline_arr = []
					mobile_arr = []
					for brw in self.pool.get('phone.number.child').browse(cr,uid,srch_id):
						if no == 1:
							if brw.contact_select == 'landline':
								if brw.number not in landline_arr:
									new_number_ln = [brw.number,number_ln_str]
									number_ln_str = ' / '.join(filter(bool,new_number_ln))
									dic['telephone'] = number_ln_str
									landline_arr.extend([brw.number])
						elif no == 2 :
							if brw.contact_select == 'mobile':
								if brw.number not in mobile_arr:
									new_number_mob = [brw.number,number_mob_str]
									number_mob_str = ' / '.join(filter(bool,new_number_mob)) 
									dic['mobile'] = number_mob_str
									mobile_arr.extend([brw.number])
						else :
								dic['telephone']=''
								dic['mobile'] = ''
			return dic

	def sales_receipt_cheque(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = { 'customer_name':'',
				'cust_cfob_id':'',
				'reciept_no_digit':'',
				'pan_no':'',
				'drawn_name':'',
				'cheque_no':'',
				'cheque_date':'',
				'drawee_bank_name':'',
				'check_drawn_name':'',
				'branch_name':'',
				'sub_total':'',
				'total':'',
				'ledger_name':'',
				'ledger_amount':'',
				'ledger_name_dr':'',
				'ledger_amount_dr':'',
			}
	   
		cheque_no = cheque_date =bank_branch_name =drawee_bank_name = ''
		dd_no = dd_date =dd_branch_name = dd_check_drawn_name = dd_drawee_bank_name =''
		pay_ref_no =neft_date =neft_branch_name = beneficiary_bank_name =''
		for res in self.pool.get('account.sales.receipts').browse(cr,uid,[self_id]):
			dic['reciept_no_digit'] = res.receipt_no[-6:] if res.receipt_no else ''
			dic['pan_no'] = res.company_id.pan_no

			for ln in res.sales_receipts_one2many:
			#---------------- # For BANK Details--------------------
				if ln.iob_one_one2many:
					for  i in ln.iob_one_one2many:
						if i.cheque_no:
							cheque_no +=str(i.cheque_no)+"\n"
						if i.cheque_date:
							cheque_date +=str(i.cheque_date)+"\n"
						if i.bank_branch_name:
							bank_branch_name +=str(i.bank_branch_name)+"\n" 
						if i.drawee_bank_name:
							drawee_bank_name += str(i.drawee_bank_name.name)+"\n"
						if i.check_drawn_name:
							#dic['drawn_name']= str(i.check_drawn_name.rstrip("\ / \n"))
							dic['drawn_name']= i.check_drawn_name

				if ln.demand_draft_one_one2many:
					for  i in ln.demand_draft_one_one2many:
						if i.dd_no:
							dd_no += str(i.dd_no)+"\n"
						if i.dd_date:
							dd_date +=str(i.dd_date)+"\n"
						if i.dd_bank_branch_name:
							dd_branch_name += str(i.dd_bank_branch_name)+"\n"
						if i.demand_draft_drawee_bank_name:
							dd_drawee_bank_name +=str(i.demand_draft_drawee_bank_name.name)+""
						if i.demand_draft_check_drawn_name:
							dd_check_drawn_name += str(i.demand_draft_check_drawn_name)
							dic['check_drawn_name'] = '\n ' + dd_check_drawn_name.rstrip("\ / \n ") 
							dic['drawn_name'] = dd_check_drawn_name.rstrip("\ / \n ") 
							
				if ln.neft_one2many:
					for  i in ln.neft_one2many:
						if i.pay_ref_no:
							pay_ref_no +=i.pay_ref_no+"\n"
						if i.neft_date:
							neft_date +=i.neft_date+"\n"
						if i.branch_name:
							neft_branch_name +=i.branch_name+"\n"
						if i.beneficiary_bank_name:
							beneficiary_bank_name +=i.beneficiary_bank_name+"\n"
							
			dic['cheque_no'] = 'Cheque no : \n' +cheque_no if cheque_no else 'Demand draft no : \n '+dd_no if dd_no else 'NEFT no : \n '+pay_ref_no if  pay_ref_no else ''
			dic['cheque_date'] = 'Dated : \n ' + (cheque_date if cheque_date else dd_date if dd_date else neft_date if neft_date else '')
			dic['branch_name']= '\n ' +(bank_branch_name if bank_branch_name else dd_branch_name if dd_branch_name else neft_branch_name if neft_branch_name else '')
			dic['drawee_bank_name'] = 'Drawn On : \n'+(drawee_bank_name if drawee_bank_name else dd_drawee_bank_name if dd_drawee_bank_name else beneficiary_bank_name if beneficiary_bank_name else '')
	#-------------------  # For BANK Details---------------------------

			dic['customer_name'] = res.customer_name.name
			dic['cust_cfob_id']=res.customer_name.ou_id
			ledger_name=ledger_amt=ledger_name_dr=ledger_amt_dr=''
			total_amt =sub_amt=0.0
			
			for ln in res.sales_receipts_one2many:
				if ln.acc_status == 'against_ref' and ln.type=='credit' and res.customer_name.name != 'CFOB' :
					if ln.invoice_adhoc_history_one2many:
						for i in ln.invoice_adhoc_history_one2many:
							if i.check_invoice == True:
								ledger_name += str(i.invoice_number)+' ( '+ str( i.invoice_date) + '),'
								ledger_amt +=str(i.invoice_paid_amount)+","
					if ln.debit_note_one2many:
						ref_str=[]
						db_amount=0.0
						for i in ln.debit_note_one2many:
							if i.check_debit: 
								ref_str.append(str(i.debit_note_no))
								db_amount += i.credit_amount_srch
						db_ref_no_str = ' / '.join(filter(bool,ref_str))
						
						ledger_name += 'Debit Note No. : ' +str(db_ref_no_str)+','
						ledger_amt += str(db_amount)+","
					total_amt += ln.credit_amount
					 
				elif ln.acc_status == 'others' and ln.type=='credit' and res.customer_name.name == 'CFOB':
					ref_str=[]
					for cfob_name in ln.sales_other_cfob_one2many:
						dic['customer_name'] = cfob_name.customer_cfob if cfob_name.customer_cfob else ln.partner_id.name if ln.partner_id.name else ''
						dic['cust_cfob_id'] = cfob_name.cust_cfob_id if cfob_name.cust_cfob_id else ln.partner_id.ou_id if ln.partner_id.name else ''
						
						ledger_name += str(cfob_name.branch_name.name if cfob_name.branch_name.name else '' )+' : ' +str(cfob_name.ref_no if cfob_name.ref_no else '' )+','
						ledger_amt += str(cfob_name.ref_amount)+"," 
						
					for  i in ln.invoice_cfob_one2many:  
						paid_amount =0.0
						if i.cfob_chk_invoice == True:
							search_amt = self.pool.get('invoice.receipt.history').search(cr,uid,[('invoice_receipt_history_id','=',i.id),
																									('receipt_id_history','=',ln.id)])
							if search_amt:
								for paid_amt in self.pool.get('invoice.receipt.history').browse(cr,uid,search_amt):
										paid_amount =paid_amt.invoice_paid_amount
									
						ledger_name += str(i.invoice_number)+' ( '+ str( i.invoice_date) + '),'
						ledger_amt +=str(paid_amount)+","
					total_amt += ln.credit_amount
					
				elif ln.acc_status == 'advance' and ln.account_id.account_selection=='advance':
					ref_str=[]
					for ad_ln in ln.advance_one2many:
						ref_str.append(ad_ln.ref_no)
					ad_ref_no_str = ' / '.join(filter(bool,ref_str))

					ledger_name += "Advance : " +"[ "+str(ad_ref_no_str)+" ],"
					ledger_amt += str(ln.credit_amount)+","
					total_amt += ln.credit_amount
						
				elif ln.account_id.account_selection == 'security_deposit' :
					if ln.acc_status == 'new_reference' and ln.type=='credit':
						ref_str=[]
						for line in ln.security_deposit_history_line_one2many:
								ref_str.append(line.ref_no)
						ref_no_str = ' / '.join(filter(bool,ref_str))

						ledger_name += "Security Deposit : " +"[ "+str(ref_no_str)+" ],"
						ledger_amt += str(ln.credit_amount)+","
						total_amt += ln.credit_amount
						
					if ln.acc_status != 'new_reference' and ln.type=='debit':
						ref_str=[]
						for line in ln.security_deposit_one2many:
								ref_str.append(line.ref_no)
						ref_no_str = ' / '.join(filter(bool,ref_str))

						ledger_name_dr += "Less (Security Deposit):" +"["+str(ref_no_str)+"],"
						ledger_amt_dr += "(-"+str(ln.debit_amount)+"),"
						sub_amt += ln.debit_amount
						
				elif ln.account_id.account_selection == 'sundry_deposit' and ln.type=='credit':
					if ln.acc_status == 'others':
						ref_str=[]
						for ch_ln in ln.sundry_deposit_one2many:
							ref_new = [str(ch_ln.payment_no),ref_no_str]
						ref_no_str = ' / '.join(filter(bool,ref_new))
						
						ledger_name += "Reference No :" +"["+str(ref_no_str)+"],"
						ledger_amt += str(ln.credit_amount)+","
						total_amt += ln.credit_amount
					else :
						ref_str=[]
						for ch_ln in ln.sundry_deposit_one2many:
							if ch_ln.sundry_check_process:
								ref_str.append(ch_ln.payment_no)
						ref_no_str = ' / '.join(filter(bool,ref_str))
						
						ledger_name += "Reference No :" +"["+str(ref_no_str)+"],"
						ledger_amt += str(ln.credit_amount)+","
						total_amt += ln.credit_amount
						
				elif ln.acc_status == 'against_ref' and ln.account_id.account_selection == 'itds_receipt':
					if ln.type == 'debit':
						ledger_name_dr += 'Less :'+str(ln.account_id.name)+"\n"
						ledger_amt_dr += "(-"+str(ln.debit_amount)+"),"
						sub_amt += ln.debit_amount
						
					if ln.type == 'credit':
						ledger_name += str(ln.account_id.name)+","
						ledger_amt += str(ln.credit_amount)+","
						total_amt += ln.credit_amount
						
				elif ln.acc_status == 'others' and ln.account_id.name == 'Sundry Receipts':
						total_amt += ln.credit_amount
				else:
						if ln.type =='credit':
								ledger_name += str(ln.account_id.name)+","
								ledger_amt += str(ln.credit_amount)+","
								total_amt += ln.credit_amount
				if ledger_amt_dr:
					roundoff=ledger_amt_dr.split('.')
					roundoff2=roundoff[1].split(')')
					if roundoff2[0]=='0':
						ledger_amt_dr=roundoff[0]+".00"
						ledger_amt_dr=ledger_amt_dr+")\n"                            
				dic['ledger_name'] = ledger_name
				dic['ledger_amount'] = ledger_amt
				dic['ledger_name_dr'] = ledger_name_dr
				dic['ledger_amount_dr'] = ledger_amt_dr
				dic['sub_total'] = total_amt
				dic['total'] = total_amt-sub_amt
				if not dic['drawn_name']:
					dic['drawn_name']=dic['customer_name']
		return dic

	def sales_receipt_cheque_duplicate(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = { 'customer_name':'',
				'cust_cfob_id':'',
				'reciept_no_digit':'',
				'pan_no':'',
				'drawn_name':'',
				'cheque_no':'',
				'cheque_date':'',
				'drawee_bank_name':'',
				'check_drawn_name':'',
				'branch_name':'',
				'sub_total':'',
				'total':'',
				'ledger_name':'',
				'ledger_amount':'',
				'ledger_name_dr':'',
				'ledger_amount_dr':'',
			}
	   
		cheque_no = cheque_date =bank_branch_name =drawee_bank_name = ''
		dd_no = dd_date =dd_branch_name = dd_check_drawn_name = dd_drawee_bank_name =''
		pay_ref_no =neft_date =neft_branch_name = beneficiary_bank_name =''
		for res in self.pool.get('account.sales.receipts').browse(cr,uid,[self_id]):
			dic['reciept_no_digit'] = res.receipt_no[-6:] if res.receipt_no else ''
			dic['pan_no'] = res.company_id.pan_no

			for ln in res.sales_receipts_one2many:
			#---------------- # For BANK Details--------------------
				if ln.iob_one_one2many:
					for  i in ln.iob_one_one2many:
						if i.cheque_no:
							cheque_no +=str(i.cheque_no)+"\n"
						if i.cheque_date:
							cheque_date +=str(i.cheque_date)+"\n"
						if i.bank_branch_name:
							bank_branch_name +=str(i.bank_branch_name)+"\n" 
						if i.drawee_bank_name:
							drawee_bank_name += str(i.drawee_bank_name.name)+"\n"
						if i.check_drawn_name:
							#dic['drawn_name']= str(i.check_drawn_name.rstrip("\ / \n"))
							dic['drawn_name']= i.check_drawn_name

				if ln.demand_draft_one_one2many:
					for  i in ln.demand_draft_one_one2many:
						if i.dd_no:
							dd_no += str(i.dd_no)+"\n"
						if i.dd_date:
							dd_date +=str(i.dd_date)+"\n"
						if i.dd_bank_branch_name:
							dd_branch_name += str(i.dd_bank_branch_name)+"\n"
						if i.demand_draft_drawee_bank_name:
							dd_drawee_bank_name +=str(i.demand_draft_drawee_bank_name.name)+""
						if i.demand_draft_check_drawn_name:
							dd_check_drawn_name += str(i.demand_draft_check_drawn_name)
							dic['check_drawn_name'] = '\n ' + dd_check_drawn_name.rstrip("\ / \n ") 
							dic['drawn_name'] = dd_check_drawn_name.rstrip("\ / \n ") 
							
				if ln.neft_one2many:
					for  i in ln.neft_one2many:
						if i.pay_ref_no:
							pay_ref_no +=i.pay_ref_no+"\n"
						if i.neft_date:
							neft_date +=i.neft_date+"\n"
						if i.branch_name:
							neft_branch_name +=i.branch_name+"\n"
						if i.beneficiary_bank_name:
							beneficiary_bank_name +=i.beneficiary_bank_name+"\n"
							
			dic['cheque_no'] = 'Cheque no : \n' +cheque_no if cheque_no else 'Demand draft no : \n '+dd_no if dd_no else 'NEFT no : \n '+pay_ref_no if  pay_ref_no else ''
			dic['cheque_date'] = 'Dated : \n ' + (cheque_date if cheque_date else dd_date if dd_date else neft_date if neft_date else '')
			dic['branch_name']= '\n ' +(bank_branch_name if bank_branch_name else dd_branch_name if dd_branch_name else neft_branch_name if neft_branch_name else '')
			dic['drawee_bank_name'] = 'Drawn On : \n'+(drawee_bank_name if drawee_bank_name else dd_drawee_bank_name if dd_drawee_bank_name else beneficiary_bank_name if beneficiary_bank_name else '')
	#-------------------  # For BANK Details---------------------------

			dic['customer_name'] = res.customer_name.name
			dic['cust_cfob_id']=res.customer_name.ou_id
			ledger_name=ledger_amt=ledger_name_dr=ledger_amt_dr=''
			total_amt =sub_amt=0.0
			
			for ln in res.sales_receipts_one2many:
				if ln.acc_status == 'against_ref' and ln.type=='credit' and res.customer_name.name != 'CFOB' :
					if ln.invoice_adhoc_history_one2many:
						for i in ln.invoice_adhoc_history_one2many:
							if i.check_invoice == True:
								ledger_name += str(i.invoice_number)+' ( '+ str( i.invoice_date) + '), '
								ledger_amt +=str(i.invoice_paid_amount)+","
						print ledger_name,ledger_amt
					# if ln.invoice_adhoc_one2many_duplicate:
					#     for i in ln.invoice_adhoc_one2many_duplicate:
					#         if i.check_invoice == True:
					#             ledger_name += str(i.invoice_number)+' ( '+ str( i.invoice_date) + '),'
					#             if i.partial_payment_amount:
					#                 ledger_amt +=str(i.partial_payment_amount)+","
					if ln.debit_note_one2many:
						ref_str=[]
						db_amount=0.0
						for i in ln.debit_note_one2many:
							if i.check_debit==True: 
								ref_str.append(str(i.debit_note_no))
								db_amount += i.credit_amount_srch
								db_ref_no_str = ' / '.join(filter(bool,ref_str))
								ledger_name += 'Debit Note No. : ' +str(db_ref_no_str)+','
								ledger_amt += str(db_amount)+", "
					print ledger_name,ledger_amt
					total_amt += ln.credit_amount
					 
				elif ln.acc_status == 'others' and ln.type=='credit' and res.customer_name.name == 'CFOB':
					ref_str=[]
					for cfob_name in ln.sales_other_cfob_one2many:
						dic['customer_name'] = cfob_name.customer_cfob if cfob_name.customer_cfob else ln.partner_id.name if ln.partner_id.name else ''
						dic['cust_cfob_id'] = cfob_name.cust_cfob_id if cfob_name.cust_cfob_id else ln.partner_id.ou_id if ln.partner_id.name else ''
						
						ledger_name += str(cfob_name.branch_name.name if cfob_name.branch_name.name else '' )+' : ' +str(cfob_name.ref_no if cfob_name.ref_no else '' )+', '
						ledger_amt += str(cfob_name.ref_amount)+"," 
						
					for  i in ln.invoice_cfob_one2many_duplicate:  
						paid_amount =0.0
						if i.cfob_chk_invoice == True:
							search_amt = self.pool.get('invoice.receipt.history').search(cr,uid,[('invoice_receipt_history_id','=',i.id),
																									('receipt_id_history','=',ln.id)])
							if search_amt:
								for paid_amt in self.pool.get('invoice.receipt.history').browse(cr,uid,search_amt):
										paid_amount =paid_amt.invoice_paid_amount
									
							ledger_name += str(i.invoice_number)+' ( '+ str( i.invoice_date) + '), '
							ledger_amt +=str(paid_amount)+","
					total_amt += ln.credit_amount
					
				elif ln.acc_status == 'advance' and ln.account_id.account_selection=='advance':
					ref_str=[]
					for ad_ln in ln.advance_one2many:
						ref_str.append(ad_ln.ref_no)
					ad_ref_no_str = ' / '.join(filter(bool,ref_str))

					ledger_name += "Advance : " +"[ "+str(ad_ref_no_str)+" ], "
					ledger_amt += str(ln.credit_amount)+","
					total_amt += ln.credit_amount
						
				elif ln.account_id.account_selection == 'security_deposit' :
					if ln.acc_status == 'new_reference' and ln.type=='credit':
						ref_str=[]
						for line in ln.security_deposit_history_line_one2many:
								ref_str.append(line.ref_no)
						ref_no_str = ' / '.join(filter(bool,ref_str))

						ledger_name += "Security Deposit : " +"[ "+str(ref_no_str)+" ], "
						ledger_amt += str(ln.credit_amount)+","
						total_amt += ln.credit_amount
						
					if ln.acc_status != 'new_reference' and ln.type=='debit':
						ref_str=[]
						for line in ln.security_deposit_one2many:
								ref_str.append(line.ref_no)
						ref_no_str = ' / '.join(filter(bool,ref_str))

						ledger_name_dr += "Less (Security Deposit):" +"["+str(ref_no_str)+"], "
						ledger_amt_dr += "(-"+str(ln.debit_amount)+"),"
						sub_amt += ln.debit_amount
						
				elif ln.account_id.account_selection == 'sundry_deposit' and ln.type=='credit':
					if ln.acc_status == 'others':
						ref_str=[]
						for ch_ln in ln.sundry_deposit_one2many:
							ref_new = [str(ch_ln.payment_no),ref_no_str]
						ref_no_str = ' / '.join(filter(bool,ref_new))
						
						ledger_name += "Reference No :" +"["+str(ref_no_str)+"], "
						ledger_amt += str(ln.credit_amount)+","
						total_amt += ln.credit_amount
					else :
						ref_str=[]
						for ch_ln in ln.sundry_deposit_one2many:
							if ch_ln.sundry_check_process:
								ref_str.append(ch_ln.payment_no)
						ref_no_str = ' / '.join(filter(bool,ref_str))
						
						ledger_name += "Reference No :" +"["+str(ref_no_str)+"], "
						ledger_amt += str(ln.credit_amount)+","
						total_amt += ln.credit_amount
						
				elif ln.acc_status == 'against_ref' and ln.account_id.account_selection == 'itds_receipt':
					if ln.type == 'debit':
						ledger_name_dr += 'Less :'+str(ln.account_id.name)+", "
						ledger_amt_dr += "(-"+str(ln.debit_amount)+"),"
						sub_amt += ln.debit_amount
						
					if ln.type == 'credit':
						ledger_name += str(ln.account_id.name)+", "
						ledger_amt += str(ln.credit_amount)+","
						total_amt += ln.credit_amount
						
				elif ln.acc_status == 'others' and ln.account_id.name == 'Sundry Receipts':
						total_amt += ln.credit_amount
				else:
						if ln.type =='credit':
								ledger_name += str(ln.account_id.name)+", "
								ledger_amt += str(ln.credit_amount)+","
								total_amt += ln.credit_amount
							
				dic['ledger_name'] = ledger_name
				dic['ledger_amount'] = ledger_amt
				dic['ledger_name_dr'] = ledger_name_dr
				dic['ledger_amount_dr'] = ledger_amt_dr
				dic['sub_total'] = total_amt
				dic['total'] = total_amt-sub_amt
				if not dic['drawn_name']:
					dic['drawn_name']=dic['customer_name']
		print dic,'dicccc'
		l_name = ledger_name.split(', ')
		print l_name
		l_amt = ledger_amt.split(',')
		print l_amt
		sale_line_obj = self.pool.get('sale.receipts.print.line')
		search_in_lines = sale_line_obj.search(cr,uid,[('account_sales_receipts_id','=',self_id)])
		for dele in sale_line_obj.browse(cr,uid,search_in_lines):
			sale_line_obj.unlink(cr,uid,dele.id)
		for m,l in zip(l_name,l_amt):
			if m and l:
				sale_line_obj.create(cr,uid,{'ledger_name':m,'ledger_amount':l,'account_sales_receipts_id':self_id})
		return dic                              

	def get_cust_add(self,self_id):

		cr = self.cr
		uid = self.uid
		dice = {'address':'',}
		count =count1 = 0
		for res in self.pool.get('account.sales.receipts').browse(cr,uid,[self_id]):
			if res.billing_location:
				address=self.pool.get('res.partner.address').name_get(cr, uid, [res.billing_location.id])
				addr= address[0][1]
				if addr:
				   dice['address'] = addr
			else:
				count1 +=1   
				for ln in res.sales_receipts_one2many:
					if ln.account_id.account_selection :
							location_name =ln.partner_id.location_name if ln.partner_id.location_name else res.customer_name.location_name   if res.customer_name.location_name else ''   
							apartment = ln.partner_id.apartment if ln.partner_id.apartment else res.customer_name.apartment if res.customer_name.apartment else ''
							building = ln.partner_id.building if ln.partner_id.building else res.customer_name.building if res.customer_name.building  else  ''
							sub_area = ln.partner_id.sub_area if ln.partner_id.sub_area else res.customer_name.sub_area if res.customer_name.sub_area else ''
							street = ln.partner_id.street if ln.partner_id.street else res.customer_name.street if res.customer_name.street else ''
							landmark = ln.partner_id.landmark if ln.partner_id.landmark else res.customer_name.landmark if res.customer_name.landmark else ''
							state_id = ln.partner_id.state_id.name if ln.partner_id.state_id else res.customer_name.state_id.name if res.customer_name.state_id else ''
							city_id = ln.partner_id.city_id.name1 if ln.partner_id.city_id else res.customer_name.city_id.name1 if res.customer_name.city_id.name1 else ''
							tehsil = ln.partner_id.tehsil.name if ln.partner_id.tehsil else res.customer_name.tehsil.name if res.customer_name.tehsil.name else ''
							district = ln.partner_id.district.name if ln.partner_id.district else res.customer_name.district.name if res.customer_name.district.name else ''

							zip1= ln.partner_id.zip if ln.partner_id.zip else res.customer_name.zip if res.customer_name.zip else ''
							if zip1:

									zip1=city_id+'-'+ zip1
							else:
									zip1=city_id
							count +=1
							address=[location_name,apartment,building,sub_area,street,landmark,tehsil,district,zip1,state_id]
							addr=', '.join(filter(bool,address))
							if addr:
									dice['address'] = addr
		return dice

	def get_parent_branch(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = {
				'licence_no':'',
				'branch_addr':'',
				}
		lis=str1=''
		for r_add in self.pool.get('res.company').browse(cr,uid,[self_id]):
			lis =r_add.insecticides_restricted_chemical_license_no if r_add.insecticides_restricted_chemical_license_no else ''
			lis += ' / ' + r_add.chemical_storage_license_no if r_add.chemical_storage_license_no else ''
			dic['branch_addr']=self.get_branch_addr(r_add.parent_branch_many2one.id)['branch_addr'] if r_add.parent_branch_many2one else ''
		if lis :
			str1 ="Insecticides License (Form VIII) : "+lis
			dic['licence_no']=str1 
		return dic


	def get_primary_address(self,partner_id):
		cr = self.cr
		uid = self.uid
		location_obj = self.pool.get('customer.line')
		partner_obj = self.pool.get('res.partner')
		search_id=''
		dic = {
				'primary_address':'',
				'primary_telephone':'',
				'primary_mobile':'',
				'primary_email':'',
				'primary_state':'',
				'primary_state_code':'' 
			 }
		customer_line_id = location_obj.search(cr,uid,[('partner_id','=',partner_id),('check_primary_address_contact','=',True)])
		if not customer_line_id:
			customer_line_ids = location_obj.search(cr,uid,[('partner_id','=',partner_id)])
			if len(customer_line_ids) > 1:
				temp_ids = []
				for customer_line_id in customer_line_ids:
					customer_line_data = location_obj.browse(cr,uid,customer_line_id)
					temp_ids.append(customer_line_data.location_id)
					min_temp_id = min(temp_ids)
					first_location_id = location_obj.search(cr,uid,[('partner_id','=',partner_id),('location_id','=',min_temp_id)])
					location_id = first_location_id[0]
			else:
				location_id = customer_line_ids[0]
		else:
			location_id = customer_line_id[0]
		primary_location = location_id
		primary_data = location_obj.browse(cr,uid,primary_location)
		location_name = primary_data.customer_address.location_name if primary_data.customer_address.location_name else ''
		apartment = primary_data.customer_address.apartment if primary_data.customer_address.apartment else ''
		building = primary_data.customer_address.building if primary_data.customer_address.building else ''
		sub_area = primary_data.customer_address.sub_area if primary_data.customer_address.sub_area else ''
		street = primary_data.customer_address.street if primary_data.customer_address.street else ''
		landmark = primary_data.customer_address.landmark if primary_data.customer_address.landmark else ''
		city_id = primary_data.customer_address.city_id.name1 if primary_data.customer_address.city_id.name1 else ''
		state_id = primary_data.customer_address.state_id.name if primary_data.customer_address.state_id.name else ''
		zipc = "- " + primary_data.customer_address.zip if primary_data.customer_address.zip else ""
		primary_address = [location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
		primary_address = ', '.join(filter(bool,primary_address))
		phone_data = primary_data.customer_address.phone_m2m_xx
		if phone_data.type == 'landline':
			dic['primary_telephone'] = phone_data.name
		if phone_data.type == 'mobile':
			dic['primary_mobile'] = phone_data.name		
		primary_email = primary_data.customer_address.email if primary_data.customer_address.email else ""
		primary_state = primary_data.customer_address.state_id.name if primary_data.customer_address.state_id.name else ''
		primary_state_code = primary_data.customer_address.state_id.state_code if primary_data.customer_address.state_id.state_code else ''
		partner_data = partner_obj.browse(cr,uid,partner_id)
		gst_no = partner_data.gst_no
		if not gst_no:
			gst_no = partner_data.uin_no
		dic['primary_address'] = primary_address
		dic['primary_email'] = primary_email
		dic['primary_state'] = primary_state
		dic['primary_state_code'] = primary_state_code
		dic['gst_no'] = gst_no
		return dic


	def get_billing_address(self,address_id):
		cr = self.cr
		uid = self.uid
		address_obj = self.pool.get('res.partner.address')
		location_obj = self.pool.get('customer.line')
		search_id=''
		dic = {
				'billing_address':'',
				'billing_telephone':'',
				'billing_mobile':'',
				'billing_email':'',
				'billing_state':'',
				'billing_state_code':'' 
			 }
		billing_data = address_obj.browse(cr,uid,address_id)
		location_name = billing_data.location_name if billing_data.location_name else ''
		apartment = billing_data.apartment if billing_data.apartment else ''
		building = billing_data.building if billing_data.building else ''
		sub_area = billing_data.sub_area if billing_data.sub_area else ''
		street = billing_data.street if billing_data.street else ''
		landmark = billing_data.landmark if billing_data.landmark else ''
		city_id = billing_data.city_id.name1 if billing_data.city_id.name1 else ''
		state_id = billing_data.state_id.name if billing_data.state_id.name else ''
		zipc = "- " + billing_data.zip if billing_data.zip else ""
		billing_address = [location_name,apartment,building,sub_area,street,landmark,city_id,state_id,zipc]
		billing_address = ', '.join(filter(bool,billing_address))
		dic['billing_telephone'] = billing_data.phone
		billing_email = billing_data.email if billing_data.email else ""
		billing_state = billing_data.state_id.name if billing_data.state_id.name else ''
		billing_state_code = billing_data.state_id.state_code if billing_data.state_id.state_code else ''
		location_id = location_obj.search(cr,uid,[('customer_address','=',address_id),('partner_id','=',billing_data.partner_id.id)])
		gst_no = location_obj.browse(cr,uid,location_id[0]).gst_no
		if not gst_no:
			gst_no = billing_data.partner_id.gst_no
			if not gst_no:
				gst_no = billing_data.partner_id.uin_no
		dic['billing_address'] = billing_address
		dic['billing_email'] = billing_email
		dic['billing_state'] = billing_state
		dic['billing_state_code'] = billing_state_code
		dic['gst_no'] = gst_no
		return dic

	def get_line_data(self,adhoc_receipt_id):
		cr = self.cr
		uid = self.uid 
		dic = {
				'service_desc':'',
				'taxable_value':'',
				'cgst_rate': '',
				'cgst_amt': '',
				'sgst_rate': '',
				'sgst_amt': '',
				'igst_rate': '',
				'igst_amt': '',
				'cess_rate': '',
				'cess_amt': '',
				'total_cgst_amt': '',
				'total_sgst_amt': '',
			 }
		adhoc_res_obj = self.pool.get('invoice.adhoc.receipts')
		invoice_line_obj = self.pool.get('invoice.adhoc')
		adhoc_receipt_data = adhoc_res_obj.browse(cr,uid,adhoc_receipt_id)
		line_data = invoice_line_obj.browse(cr,uid,adhoc_receipt_data.invoice_adhoc_id)
		services = line_data.services
		product = services.split('[')[0]
		invoice_number = line_data.invoice_adhoc_id12.invoice_number
		inv_code = invoice_number[10:]
		dic['service_desc'] = product+'('+'Ref-'+inv_code+')'
		taxable_value = line_data.amount
		dic['taxable_value'] = taxable_value
		cgst_rate = line_data.cgst_rate
		dic['cgst_rate'] = cgst_rate
		sgst_rate = line_data.sgst_rate
		dic['sgst_rate'] = sgst_rate
		igst_rate = line_data.igst_rate
		dic['igst_rate'] = igst_rate
		cess_rate = line_data.cess_rate
		dic['cess_rate'] = cess_rate
		cgst_amt = line_data.cgst_amt
		dic['cgst_amt'] = cgst_amt
		sgst_amt = line_data.sgst_amt
		dic['sgst_amt'] = sgst_amt
		igst_amt = line_data.igst_amt
		dic['igst_amt'] = igst_amt 
		cess_amt = line_data.cess_amt
		dic['cess_amt'] = cess_amt 
		return dic

	

	def get_total_value(self,res_id):
		cr = self.cr
		uid = self.uid 
		dic = {
				'total_advance_value': 0.00,
				'total_taxable_value': 0.00,
				'cgst_rate': '0.00%',
				'total_cgst_amt': 0.00,
				'sgst_rate': '0.00%',
				'total_sgst_amt': 0.00,
				'igst_rate':'0.00%',
				'total_igst_amt': 0.00,
			 }
		total_advance_value = 0.00
		total_taxable_value = 0.00
		total_cgst_amt = 0.00
		total_sgst_amt = 0.00
		total_igst_amt = 0.00
		total_cess_amt = 0.00
		sales_res_obj = self.pool.get('account.sales.receipts')
		for res_data in sales_res_obj.browse(cr,uid,[res_id]):
			for m in res_data.advance_receipt_ids:
				total_advance_value = total_advance_value + float(m.advance_amount)
				total_taxable_value = total_taxable_value + float(m.taxable_amount)
				total_cgst_amt = total_cgst_amt + float(m.cgst_amount)
				total_sgst_amt = total_sgst_amt + float(m.sgst_amount)
		dic['total_advance_value'] = format(total_advance_value,'.2f')
		dic['total_taxable_value'] = format(total_taxable_value,'.2f')
		dic['total_cgst_amt'] = format(total_cgst_amt,'.2f')
		dic['total_sgst_amt'] = format(total_sgst_amt,'.2f')
		return dic

	def get_invoice_details(self,res_id):
		cr = self.cr
		uid = self.uid 
		dic = {
				'invoice_details': ''
			  }
		invoice_details = ''
		sales_res_obj = self.pool.get('account.sales.receipts')
		res_data = sales_res_obj.browse(cr,uid,res_id)
		for res_line in res_data.sales_receipts_one2many:
			if res_line.type == 'credit':
				for adhoc_history_id in res_line.invoice_adhoc_history_one2many:
					invoice_data = adhoc_history_id.invoice_receipt_history_id
					invoice_number = invoice_data.invoice_number
					invoice_date = invoice_data.invoice_date
					invoice_amount = invoice_data.net_amount_payable
					long_name = invoice_number+'('+invoice_date+')'+'Rs.'+str(invoice_amount)+', '
					invoice_details = invoice_details+long_name
		dic['invoice_details'] = invoice_details
		return dic


report_sxw.report_sxw('report.gst.account.sales.receipts.print', 'account.sales.receipts', 'gst_accounting/report/gst_sales_receipts_print.rml', parser=gst_cheque, header="False")
