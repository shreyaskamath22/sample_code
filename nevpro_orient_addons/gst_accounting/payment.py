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


class account_payment(osv.osv):
#### class to store bank payment details
	_inherit = 'account.payment'
	_order = 'payment_date desc'

	def add_info(self, cr, uid, ids, context=None): 
	### Bank Payment add button to add record in child table(payment_line)
		freight_input_rate=0.0
		check_freight=igst_check=False
		for res in self.browse(cr,uid,ids):
			if not res.customer_name and res.account_id.name=='ITDS on Contract Pymt':
				raise osv.except_osv(('Alert'),('Please select Supplier Name'))
			state = res.state
			acc_id = res.account_id.id
			types = res.type
			if state == 'draft':
				if not acc_id:
					raise osv.except_osv(('Alert'),('Plaese select Account Name.'))
				if not types:
					raise osv.except_osv(('Alert'),('Plaese select Type.'))

			if res.account_id.account_selection == 'cash':
				raise osv.except_osv(('Alert'),('Please select proper account name.'))
			
			# account_id1=res.account_id
			#for i in res.payment_one2many:                          #remove duplicate as per vijay requirement. on 1 dec
			#	if account_id1.id==i.account_id.id:
			#		raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
			

			self.write(cr,uid,res.id,{'account_id':None,'type':''})
			total= total_amount=auto_credit_total=0.0
			auto_credit_cal=auto_debit_cal=auto_credit_total=auto_debit_total=0.0
			account_selection = res.account_id.account_selection
			acc_selection_list = ['primary_cost_phone', 'primary_cost_cse','primary_cost_office',
								  'primary_cost_vehicle','primary_cost_service','primary_cost_cse_office']
			if res.payment_one2many and res.customer_name.gst_no==False or res.customer_name.gst_no=='Unregistered':
				for ln in res.payment_one2many:
					if 'Freight Inward-GST' in ln.account_id.name:
						check_freight=True
					if 'Freight Outward-GST' in ln.account_id.name:
						check_freight=True
			# if check_freight:
				# if res.type=='debit' and res.account_id.name in ('IGST - Input') and res.account_id.account_selection=='st_input':
				# 	raise osv.except_osv(('Alert'),("Kindly Update the GST No of Supplier!"))
				# if res.type=='debit' and res.account_id.name in ('CGST - Input','SGST - Input','IGST - Input') and res.account_id.account_selection=='st_input':
				# 	raise osv.except_osv(('Alert'),("You cannot add '%s' Ledger!")%(res.account_id.name))
			if res.account_id.account_selection=='st_input' and res.account_id.code in ('sgst','cgst','igst','utgst'):
				if not res.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			if account_selection in ('st_input','excise_input'):
				for t in res.payment_one2many:
					if t.account_id.account_selection in acc_selection_list :
						total += t.debit_amount
				
				search_tax_id = [] ###To Remove Hard Code Service Tax 
				service_tax = ed_cess = hs_cess = 0.0
			if 'Freight Inward-GST' in res.account_id.name:
				freight_input_rate='5'
				if not res.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			if 'Freight Outward-GST' in res.account_id.name:
				freight_input_rate='5'
				if not res.customer_name:	
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			if account_selection in ('iob_one','iob_two'):
				if res.type=='debit':
					raise osv.except_osv(('Alert'),('Please select Type as Credit.'))
				else:	
					for k in res.payment_one2many:
						if k.type=='credit':
							auto_debit_cal += k.credit_amount
						if k.type=='debit':
							auto_credit_cal += k.debit_amount
					if auto_debit_cal<auto_credit_cal:
						auto_credit_cal -= auto_debit_cal
					else:
						auto_credit_cal=0.0
			if res.customer_name:
				if not res.customer_name.state_id:
					raise osv.except_osv(('Alert'),('Kindly update the State of Supplier!'))
				if res.customer_name.state_id:
					customer_state = res.customer_name.state_id.id
					branch_state=res.company_id.state_id.id
					if customer_state!=branch_state:
							igst_check=True
			if igst_check==False:
				if res.account_id.name in ('IGST - Input') and res.account_id.account_selection=='st_input':
					raise osv.except_osv(('Alert'),("You cannot add 'IGST - Input' Ledger"))
			# if igst_check:
			# 	if res.account_id.name in ('CGST - Input','SGST - Input','UTGST - Input') and res.account_id.account_selection=='st_input':
			# 		raise osv.except_osv(('Alert'),("You cannot add '%s' Ledger!")%(res.account_id.name))
			if res.customer_name.id:
				if res.customer_name.gst_type_supplier.name=='Composition':
					# tax_rate=0.0
					freight_input_rate=0.0
			if acc_id:
				self.pool.get('payment.line').create(cr,uid,{'payment_id':res.id,
										'debit_amount':total_amount,
										'credit_amount':auto_credit_cal,
										'account_id':acc_id,
										'type':res.type,
										'customer_name':res.customer_name.id if res.customer_name.id else '',
										'freight_input_rate':freight_input_rate,
										'igst_check':igst_check,
										})

		return True

	def process(self, cr, uid, ids, context=None):
	### Bank Payment Process Button
		cr_total = dr_total = total = iob_total = service_total = itds_total = cheque_amount = freight_debit = 0.0
		dd_amount = neft_amount = total_sundry_deposit = chk_account_selection = total_cgst_amount=total_sgst_amount=total_igst_amount=total_cgst=total_sgst=total_igst=0.0
		move = service_cost = iob_two_id = itds_id = primary_cost_id=payment_date = ''
		post = []
		iob_one_payment_id = neft_payment_id = demand_draft_payment_id = emp_name= ''
		today_date = datetime.now().date()
		py_date = bank_charges_bool = bank_charge_flag=freightin_check=freightot_check=sc_flag=igst_check=False
		models_data=self.pool.get('ir.model.data')
		#############################Validation done for the Advance to staff
		advance_append_list =[]
		account_account_obj = self.pool.get('account.account')
		primary_cost_category_obj = self.pool.get('primary.cost.category')
		o = self.browse(cr,uid,ids[0])
		for line in o.payment_one2many:
			main_id = line.account_id.id
			line_id = line.id
			advance_account_check = account_account_obj.browse(cr,uid,main_id)
			advance_expence_check_val = advance_account_check.advance_expence_check
			advance_staff_check_val = advance_account_check.advance_staff_check
			if advance_staff_check_val == True and advance_expence_check_val == False:
				search_id = primary_cost_category_obj.search(cr,uid,[('primary_cost_id','=',line_id)])
				if len(search_id) == 0:
						raise osv.except_osv(('Alert'),('Primary Cost Category are not added in Advance to staff account.'))
		#####################################################################
		count=0
		total_frin_amount=total_frot_amount=bank_exp_amount=total_sc_amount=sc_debit=0.0
		for res1 in self.browse(cr,uid,ids):
			if res1.customer_name:
				if not res1.customer_name.gst_type_supplier:
					raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
				if res1.customer_name.gst_type_supplier and (res1.customer_name.gst_no==False or res1.customer_name.gst_no=='' or res1.customer_name.gst_no==None):
					raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
				if res1.customer_name.gst_no==False or res1.customer_name.gst_no=='' or res1.customer_name.gst_no==None:
					raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
			freight_list_new=[]
			if res1.payment_date:
			        check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
			        if check_bool:
			                if res1.payment_date != str(today_date):
        				        raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
        			else:
        			        py_date = str(today_date + relativedelta(days=-5))
				        if res1.payment_date < str(py_date) or res1.payment_date > str(today_date):
				        	raise osv.except_osv(('Alert'),('Kindly select Receipt Date 5 days earlier from current date.'))
				payment_date=res1.payment_date	
			else:
				payment_date=datetime.now().date()
				
			for line in res1.payment_one2many:
				if line.type == 'credit':
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				elif line.type == 'debit':
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				else:
					raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(line.account_id.name))))

				cr_total +=  line.credit_amount
				dr_total +=  line.debit_amount

				account_id = line.account_id.id
				temp = tuple([account_id])
				post.append(temp)
				#for i in range(0,len(post)):	
				#	for j in range(i+1,len(post)):
				#		if post[i][0]==post[j][0]:
				#			raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
				
				acc_selection = line.account_id.account_selection ##23dec15
				
				if acc_selection in ['iob_one','iob_two']:
					chk_account_selection +=1
				if 'Sundry Creditors' in line.account_id.name and line.type=='debit':
					if line.sundry_expense_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (line.account_id.name))
					else:
						for sc in line.sundry_expense_one2many:
							if sc.check_exp:
								total_sc_amount=total_sc_amount+sc.bill_value
								self.pool.get('account.purchase.receipts').write(cr,uid,sc.purchase_id.id,{'state':'finish'})
						sc_flag=True
						sc_debit=line.debit_amount
				if 'Freight Inward-GST' in line.account_id.name and line.type=='debit' and line.debit_amount>750:
					if line.bank_payment_freight_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (line.account_id.name))	
					else:
						freight_list_new=[]
						for frin in line.bank_payment_freight_one2many:
							total_frin_amount=total_frin_amount+frin.bill_value
							total_cgst=total_cgst+frin.cgst_tax_amount
							total_sgst=total_sgst+frin.sgst_tax_amount
							total_igst=total_igst+frin.igst_tax_amount
							if frin.freight_input_rate:
								freight_list_new.append(frin.id)
						freightin_check=True
						freight_debit=line.debit_amount
					igst_check=line.igst_check
				if 'Freight Outward-GST' in line.account_id.name and line.type=='debit' and line.debit_amount>750:
					if line.bank_payment_freight_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (line.account_id.name))
					else:
						freight_list_new=[]
						for frot in line.bank_payment_freight_one2many:
							total_frot_amount=total_frot_amount+frot.bill_value
							total_cgst=total_cgst+frot.cgst_tax_amount
							total_sgst=total_sgst+frot.sgst_tax_amount
							total_igst=total_igst+frot.igst_tax_amount
							if frot.freight_input_rate:
								freight_list_new.append(frot.id)
						freightot_check=True
						freight_debit=line.debit_amount
					igst_check=line.igst_check
			if sc_flag:
				if round(total_sc_amount,2)!=round(sc_debit,2):
					raise osv.except_osv(('Alert'),('Total of wizard amount is not equal to Debit amount'))
				if not res1.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			if freightin_check:
				if round(total_frin_amount,2)!=round(freight_debit,2):
					raise osv.except_osv(('Alert'),('Total of wizard amount is not equal to Debit amount'))
				if not res1.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			if freightot_check:
				if round(total_frot_amount,2)!=round(freight_debit,2):
					raise osv.except_osv(('Alert'),('Total of wizard amount is not equal to Debit amount'))
				if not res1.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			if chk_account_selection ==0.0: #23dec15
					raise osv.except_osv(('Alert'),('Please select proper account name')) 
					
			self.write(cr,uid,ids,{'debit_amount_srch':dr_total})
			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
				
##>>>>>>>>>>>>>for bank_charges in bank_payment in
		for res in self.browse(cr,uid,ids):
			if res.payment_one2many:
				for j in res.payment_one2many:
					if j.debit_amount :
							count += 1
					if j.account_id.bank_charges_bool==True:
						bank_charges_bool=True
						bank_charge_flag=True
							
		if count >=2 and bank_charges_bool==True:
		        bank_charge_flag=False      
##<<<<<<<<<<<<<<<<<<<<<<<<<		        
		        
		for res in self.browse(cr,uid,ids):
			input_list=[]
			for bank_line in res.payment_one2many:
				wizard_id = bank_line.wizard_id
				acc_selection = bank_line.account_id.account_selection
				account_name = bank_line.account_id.name
				credit_amount = bank_line.credit_amount
				debit_amount = bank_line.debit_amount
				gst_applied = bank_line.account_id.gst_applied
				code = bank_line.account_id.code
				acc_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
								  'primary_cost_service','primary_cost_vehicle','primary_cost_cse_office','sundry_deposit']
		
				if wizard_id == 0:
					self.wizard_id_write(cr,uid,ids,context=context)
				
				if acc_selection=='expenses' and bank_line.type=='debit':
					igst_check=bank_line.igst_check
					if bank_line.bank_expense_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (line.account_id.name))
					else:
						for bank_exp in bank_line.bank_expense_one2many:
							bank_exp_amount=bank_exp_amount+bank_exp.total_amount
					if bank_exp_amount!=0.0:
						if round(debit_amount,2)!=round(bank_exp_amount,2):
							raise osv.except_osv(('Alert'),("Debit Amount should match with its wizard value!!"))

				if acc_selection == 'security_deposit': ## security deposite
					for sec_dep_line in bank_line.security_deposit_one2many:
						self.pool.get('security.deposit').write(cr,uid,sec_dep_line.id,{
							'security_check_against':True,
							'customer_name':bank_line.customer_name.id if bank_line.customer_name.id else '' ,
							'customer_name_char':res.customer_name.name if res.customer_name.name else '' ,
							})
						
				if acc_selection == 'sundry_deposit': ## sundry deposite
					for sun_dep_line in bank_line.sundry_deposit_line:
						self.pool.get('sundry.deposit').write(cr,uid,sun_dep_line.id,{
							'sundry_check':True,
							'customer_name':bank_line.customer_name.id if bank_line.customer_name.id else '' ,
							'customer_name_char':res.customer_name.name if res.customer_name.name else '' ,
							})
						
				if acc_selection == 'st_input' and gst_applied !=True:
					st_date = ''
					st_total = 0.0
					if bank_line.st_input_one2many:
						for cse_line in bank_line.st_input_one2many:
							st_date=cse_line.bill_date
							st_total +=  cse_line.total_amount

					# if bank_line.bank_st_input_cgst_ids:
					# 	for cse_line in bank_line.bank_st_input_cgst_ids:
					# 		st_date=cse_line.bill_date
					# 		st_total +=  cse_line.total_amount

					# if bank_line.bank_st_input_igst_ids:
					# 	for cse_line in bank_line.bank_st_input_igst_ids:
					# 		st_date=cse_line.bill_date
					# 		st_total +=  cse_line.total_amount
						
					if not st_date:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

				if acc_selection == 'st_input' and gst_applied == True:
					bank_id = ''
					total_debit_amount = 0.0
					if code == 'igst':
						if bank_line.bank_st_input_igst_ids==[]:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						else:
							for line1 in bank_line.bank_st_input_igst_ids:
								bank_id = line1.bank_payment_line_igst_id
								total_debit_amount = total_debit_amount+line1.igst_tax_amount
						total_igst_amount=total_debit_amount
						if round(total_debit_amount,2) != round(debit_amount,2):
							raise osv.except_osv(('Alert'),('Wizard amount and debit amount should be same!'))
					if code == 'cgst':
						if bank_line.bank_st_input_cgst_ids == []:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						else:
							for line1 in bank_line.bank_st_input_cgst_ids:
								bank_id = line1.bank_payment_line_cgst_id
								total_debit_amount = total_debit_amount+line1.cgst_tax_amount
						total_cgst_amount=total_debit_amount
						if round(total_debit_amount,2) != round(debit_amount,2):
							raise osv.except_osv(('Alert'),('Wizard amount and debit amount should be same'))
					input_list.append(code)		
				if acc_selection == 'excise_input':
					st_date = ''
					st_total = 0.0
					for ex_line in bank_line.excise_input_one2many:
						st_date=ex_line.bill_date
						st_total += ex_line.total_amount
						
					if not st_date:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))


				elif acc_selection == 'iob_one':
				## validation in bank accounts
					for iob_one_line in bank_line.iob_one_payment_one2many:##cheque
						iob_one_payment_id = iob_one_line.iob_one_payment_id.id
						cheque_no = iob_one_line.cheque_no
						cheque_amount += iob_one_line.cheque_amount
						if not iob_one_line.cheque_amount:
							raise osv.except_osv(('Alert'),('Please provide Cheque Amount.'))
						if not iob_one_line.cheque_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not iob_one_line.cheque_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not iob_one_line.drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not iob_one_line.bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))


					for demand_draft_line in bank_line.demand_draft_payment_one2many:## DD
						demand_draft_payment_id = demand_draft_line.demand_draft_payment_id.id
						dd_no = demand_draft_line.dd_no
						dd_amount +=  demand_draft_line.dd_amount
						for n in str(demand_draft_line.dd_no):
							p = re.compile('([0-9]{9}$)')
							if p.match(demand_draft_line.dd_no)== None :
								self.pool.get('demand.draft.sales.receipts').create(cr,uid,{'dd_no':''})
								raise osv.except_osv(('Alert!'),('Please Enter 9 digit Cheque Number.'))

                                                        if not  demand_draft_line.dd_amount:
								raise osv.except_osv(('Alert'),('Please provide DD Amount.'))
							if not demand_draft_line.dd_date:
								raise osv.except_osv(('Alert'),('Please provide DD Date.'))
							if not demand_draft_line.dd_no:
								raise osv.except_osv(('Alert'),('Please provide DD Number.'))
							if not demand_draft_line.demand_draft_drawee_bank_name:
								raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
							if not demand_draft_line.dd_bank_branch_name:
								raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
							if not demand_draft_line.selection_cts:
								raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))

					for neft_line in bank_line.neft_payment_one2many:##NEFT
						neft_payment_id = neft_line.neft_payment_id.id
						neft_amount += neft_line.neft_amount
                                        
                                                if not neft_line.neft_amount:
							raise osv.except_osv(('Alert!'),('Please provide NEFT AMOUNT'))
						if not neft_line.beneficiary_bank_name:
							raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
						if not neft_line.pay_ref_no:
							raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
						if not neft_line.neft_amount:
							raise osv.except_osv(('Alert!'),('Please provide Amount for NEFT/RTGS.'))

					if not iob_one_payment_id:
						if not neft_payment_id:
							if not demand_draft_payment_id:
								if bank_line.account_id.ho_bank_wizard_check == True:
									raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if not neft_payment_id:
						if iob_one_payment_id :
							if debit_amount:
								if cheque_amount != debit_amount:
									pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if credit_amount:
								if cheque_amount != credit_amount:
									pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('credit amount should be equal'))

					if not iob_one_payment_id:
						if neft_payment_id:
							if debit_amount:
								if neft_amount != debit_amount:
									pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if credit_amount:
								if neft_amount != credit_amount:
									pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('credit amount should be equal'))

					self.write(cr,uid,ids,{'voucher_type':'Payment (Bank - A/c-I)'})

				elif acc_selection == 'itds':
					for itds_line in bank_line.itds_one2many:
						itds_id = itds_line.itds_id.id
					if not itds_id:
						pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

					if bank_line.itds_one2many:
						for itds_ln in bank_line.itds_one2many:
							itds_total += itds_ln.itds_amount 
					
						if credit_amount:
							if itds_total != credit_amount:
								pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
						
						if debit_amount:
							if itds_total != debit_amount:
								pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

				elif acc_selection == 'iob_two':
					for iob_two_line in bank_line.iob_two_one2many:
						iob_two_id = iob_two_line.iob_two_id

					#if not iob_two_id:
					     #   if bank_charges_bool: #### for Bank Charges wizard
					#        pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if not bank_charge_flag :
						if bank_line.iob_two_one2many:
							for iob_two_ln in bank_line.iob_two_one2many:
								if not iob_two_ln.drawee_bank_name_new:
									raise osv.except_osv(('Alert!'),('Please provide Drawee Bank Name.'))

								if not iob_two_ln.bank_branch_name:
									raise osv.except_osv(('Alert!'),('Please provide Bank Branch Name.'))
								iob_total +=  iob_two_ln.cheque_amount
								
								if iob_two_ln.cheque_no:                       
									for n in str(iob_two_ln.cheque_no):
										p = re.compile('([0-9]{6}$)')
										if p.match(iob_two_ln.cheque_no)== None :
											raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
							if credit_amount:
								if iob_total != credit_amount:
									raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
							if debit_amount:
								if iob_total != debit_amount:
									raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))
						else :
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))#alert if o2mempty inside

					self.write(cr,uid,ids,{'voucher_type':'Payment  (Bank)'})
					
				if acc_selection in acc_selection_list:
					if acc_selection == 'primary_cost_service':
						for service_line in bank_line.primary_cost_service_one2many:
							service_cost = service_line.primary_cost_service_id.id
						if not service_cost:
							pass #raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						if bank_line.primary_cost_service_one2many:
							for service_ln in bank_line.primary_cost_service_one2many:
								total += service_ln.amount
	
					elif acc_selection == 'primary_cost_cse':
						total = 0.0
						emp_name= ""
						for i in bank_line.primary_cost_one2many:
							emp_name=i.emp_name.id
						self.write(cr,uid,res.id,{'employee_name':emp_name})
						if bank_line.primary_cost_one2many == []:
							pass # 1 dec as per vijay raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
						if bank_line.primary_cost_one2many:
							for ln in bank_line.primary_cost_one2many:
								total += ln.amount
	
					elif acc_selection == 'primary_cost_office':
						bank_office_id = ''
						office_total = 0.0
						for office_line in bank_line.bank_office_name:
							bank_office_id = office_line.bank_primary_office_id
							office_name = office_line.office_name
							total +=  office_line.amount
							
						if not bank_office_id:
							pass # 1 dec as per vijay raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
						#if not office_name:
						#	pass # 1 dec as per vijay raise osv.except_osv(('Alert'),('Please enter office name.'))
	
					elif acc_selection == 'primary_cost_phone':
						bank_phone_id = ''
						phone_total = 0.0
						for phone_line in bank_line.bank_primary_phone_line:
							bank_phone_id = phone_line.bank_primary_phone_id.id
							total += phone_line.amount
							phone_mobile_no = phone_line.phone_mobile_no
	
						if not bank_phone_id:
							pass # 1 dec as per vijay raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
						#if not phone_mobile_no:
							#pass # 1 dec as per vijay raise osv.except_osv(('Alert'),('Please enter phone/mobile number.'))
	
						
					elif acc_selection == 'primary_cost_vehicle':
						bank_vehicle_id = ''
						vehicle_total = 0.0
						for vehicle_line in bank_line.bank_primary_vehicle_line:
							bank_vehicle_id = vehicle_line.bank_primary_vehicle_id.id
							total += vehicle_line.amount
							vehicle_no = vehicle_line.vehicle_no
	
						if not bank_vehicle_id:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
						if not vehicle_no:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Please enter vehicle number.'))
	
	
					elif acc_selection == 'primary_cost_cse_office':
						bank_cse_id = ''
						cse_total = 0.0
						for cse_line in bank_line.bank_primary_cse_office_one2many:
							bank_cse_id = cse_line.bank_primary_cse_office_id.id
							total += cse_line.amount
							emp_name=cse_line.emp_name.id
							
						self.write(cr,uid,res.id,{'employee_name':emp_name})
						if not bank_cse_id:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
						
					elif acc_selection == 'sundry_deposit':
						if bank_line.sundry_deposit_line == []:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('No line to process.'))
	
						for sundry_line in bank_line.sundry_deposit_line:
							total += sundry_line.payment_amount
	
							if not sundry_line.cse:
									pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Provide CSE Name.'))
							if not sundry_line.payment_no:
									pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Provide Payment Number.'))
							if not sundry_line.payment_date:
									pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Provide Payment Date.'))
								
					if credit_amount:
						if total != credit_amount:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if total != debit_amount:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))
			if input_list!=[]:
				if 'cgst' in input_list:
					if 'sgst' in input_list:
						pass
					elif 'utgst' in input_list:
						pass
					else:
						raise osv.except_osv(('Alert'),("Add either 'SGST - Input' ledger or 'UTGST - Input' ledger to process the entry!!"))
				elif 'sgst' in input_list:
					 if 'cgst' not in input_list:
					 	raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
				elif 'utgst' in input_list:
					 if 'cgst' not in input_list:
					 	raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
			# if res.customer_name.gst_no!='Unregistered':
			# 	if 'igst' not in input_list and igst_check:
			# 		raise osv.except_osv(('Alert'),("Add 'IGST - Input' ledger to process the entry !!"))
#------------------------------------------------------------------------------------------------------------------------
		for rec in self.browse(cr,uid,ids):
			for line in rec.payment_one2many:
				credit_amount = line.credit_amount
				debit_amount = line.debit_amount
				account_name = line.account_id.name
				acc_selection = line.account_id.account_selection
				gst_applied = line.account_id.gst_applied
				code = line.account_id.code
				if acc_selection == 'st_input' and gst_applied == True:
					if total_cgst_amount!=0.0:
						if code=='sgst':
							if round(debit_amount,2)!=round(total_cgst_amount,2):
								raise osv.except_osv(('Alert'),("SGST-Input ledger value should match with CGST-Input ledger value!!"))
						if code=='utgst':
							if round(debit_amount,2)!=round(total_cgst_amount,2):
								raise osv.except_osv(('Alert'),("UTGST-Input ledger value should match with CGST-Input ledger value!!"))
		for rec in self.browse(cr,uid,ids):
		## generate payment number
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_payment_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_payment_tree')
			
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
			
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','account.payment')])
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
					if comp_id.bank_payment_id:
						bank_payment_id = comp_id.bank_payment_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			seq_start=1	
			if pcof_key and bank_payment_id:
				cr.execute("select cast(count(id) as integer) from account_payment where state not in ('draft') and payment_no is not null  and payment_date>='2017-07-01' and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				# seq_new=self.pool.get('ir.sequence').get(cr,uid,'account.payment')
				value_id = pcof_key + bank_payment_id +  str(financial_year) +str(seq).zfill(5)
				#value_id = pcof_key + bank_payment_id +  str(year1) +str(seq_new).zfill(6)
				existing_value_id = self.pool.get('account.payment').search(cr,uid,[('payment_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + bank_payment_id +  str(financial_year) +str(seq+1).zfill(5)
#-------------------------------------------------------------------------------------

			self.write(cr,uid,ids,{'payment_no':value_id,'payment_date': payment_date})
			date = payment_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id

			for chk_ln in rec.payment_one2many:   
				if chk_ln.account_id.account_selection == 'ho_remmitance':
					self.write(cr,uid,rec.id,{'ho_remittance_check':True})

				if chk_ln.account_id.account_selection == 'primary_cost_service' and chk_ln.account_id.bank_charges_bool:
					self.write(cr,uid,rec.id,{'bank_charges_check':True})

				if chk_ln.account_id.account_selection == 'funds_transferred_ho':
					self.write(cr,uid,rec.id,{'funds_transferred_ho_check':True})
			
                        ## craete Journal entry
			move = self.pool.get('account.move').create(cr,uid,{
									'journal_id':11,#Journal Hardcoded confirm from PCIL
									'state':'posted',
									'date':date,
									'name':value_id,
									'narration':rec.narration if rec.narration else '',
									'voucher_type':rec.voucher_type,
									},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.payment_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
									'move_id':line1.id,
									'account_id':ln.account_id.id,
									'debit':ln.debit_amount,
									'name':rec.customer_name.name if rec.customer_name.name else '',
									'journal_id':11,
									'period_id':period_id,
									'date':date,
									'ref':value_id},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
									'move_id':line1.id,
									'account_id':ln.account_id.id,
									'credit':ln.credit_amount,
									'name':rec.customer_name.name if rec.customer_name.name else '',
									'journal_id':11,
									'period_id':period_id,
									'date':date,
									'ref':value_id},context=context)


			self.write(cr,uid,rec.id,{'state':'done'})
			if freight_list_new!=[]:
				# if rec.customer_name.gst_no==False or rec.customer_name.gst_no=='Unregistered':
				# 	if igst_check:
				# 		raise osv.except_osv(('Alert'),("Kindly update the GST Number of Supplier!"))
				# 	if not igst_check:
				# 		if 'cgst' not in input_list:
				# 			 raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
				# 		if 'sgst' not in input_list:
				# 			 raise osv.except_osv(('Alert'),("Add 'SGST - Input' ledger to process the entry !!")) 
				# for ln in rec.payment_one2many:
				# 	if ln.account_id.name in ('CGST - Input','SGST - Input','IGST - Input') and ln.account_id.account_selection=='st_input':
				# 		raise osv.except_osv(('Alert'),("You cannot select '%s' Ledger!")%(ln.account_id.name))
				# if rec.customer_name.gst_no!='Unregistered':
				# 	if rec.customer_name.gst_no!=False:
				# 		if 'igst' not in input_list and igst_check:
				# 			raise osv.except_osv(('Alert'),("Add 'IGST - Input' ledger to process the entry !!"))
				narration="Tax Liability generated against the voucher no: "+str(value_id)
				if input_list==[]:
					create_id = self.pool.get('account.stat.adjustment').create(cr,uid,{
									'state':'done',
									'date':date,
									'debit_amount':total_cgst+total_sgst+total_igst,
									'credit_amount':total_cgst+total_sgst+total_igst,
									'total_credit':total_cgst+total_sgst+total_igst,
									'total_debit':total_cgst+total_sgst+total_igst,
									'customer_name':rec.customer_name.id,
									'narration':narration,
									'voucher_type':'stat_adjustment',},context=context)
					if create_id:
						if company_id:
							for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
								if comp_id.stat_adjustment_seq_id:
									stat_adjustment_seq_id = comp_id.stat_adjustment_seq_id
								if comp_id.pcof_key:
									pcof_key = comp_id.pcof_key
							
						count = 0
						seq_start=1	
						if pcof_key and stat_adjustment_seq_id:
							cr.execute("select cast(count(id) as integer) from account_stat_adjustment where state not in ('draft') and stat_adjustment_number is not null  and date>='2017-07-01' and  date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
							temp_count=cr.fetchone()
							if temp_count[0]:
								count= temp_count[0]
							seq=int(count+seq_start)
							value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq).zfill(5)
							existing_value_id = self.pool.get('account.stat.adjustment').search(cr,uid,[('stat_adjustment_number','=',value_id)])
							if existing_value_id:
								value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq+1).zfill(5)
						self.pool.get('account.stat.adjustment').write(cr,uid,int(create_id),{'stat_adjustment_number':value_id,'date': date,'state':'done'})		
						search_tax_on_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','Tax on RCM')])
						if search_tax_on_rcm:
							debit_account_id=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
								'account_stat_adjustment_id':int(create_id),
								'debit_amount':total_cgst+total_sgst+total_igst,
								'account_id':search_tax_on_rcm[0],
								'type':'debit',
								'state':'done',
								'freight_flag':True,
								})
							if freight_list_new:
								for freight in freight_list_new:
									self.pool.get('st.input').write(cr,uid,int(freight),{'stat_freight_id':debit_account_id})
						# for chk_ln in rec.payment_one2many:
						# 	if chk_ln.bank_payment_freight_one2many!=[]:						
						# 		for frin in chk_ln.bank_payment_freight_one2many:				
						# 			self.pool.get('account.legal.profession.charges').create(cr,uid,
						# 				{'stat_legal_profession_id':int(debit_account_id),
						# 				 'bill_no':frin.bill_no,
						# 				 'bill_date':frin.bill_date,
						# 				 'bill_value':frin.bill_value,
						# 				 'rate':frin.freight_input_rate,
						# 				 'cgst_amount':frin.cgst_tax_amount,
						# 				 'sgst_amount':frin.sgst_tax_amount,
						# 				 'igst_amount':frin.igst_tax_amount,
						# 				 'total_amount':frin.total_amount})
						if igst_check==True:
							search_igst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','IGST - RCM')])
							if search_igst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_igst,
									'account_id':search_igst_rcm[0],
									'type':'credit',
									'state':'done',
									})
						else:
							search_cgst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','CGST - RCM')])
							if search_cgst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_cgst,
									'account_id':search_cgst_rcm[0],
									'type':'credit',
									'state':'done',
									})
							search_sgst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','SGST - RCM')])
							if search_sgst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_sgst,
									'account_id':search_sgst_rcm[0],
									'type':'credit',
									'state':'done',
									})
			# if 'igst' not in input_list and igst_check:
			# 	raise osv.except_osv(('Alert'),("Add 'IGST - Input' ledger to process the entry !!"))
			for i in rec.payment_one2many:
				#customized for gst------------------------------------------------------------------------
				if i.account_id.gst_applied == False:
					search_temp=self.pool.get('st.input').search(cr,uid,[('payment_line_input_id','=',i.id)])
					for j in self.pool.get('st.input').browse(cr,uid,search_temp):
						self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
					search_temp1=self.pool.get('st.input').search(cr,uid,[('payment_line_excise_id','=',i.id)])
					for k in self.pool.get('st.input').browse(cr,uid,search_temp1):
						self.pool.get('st.input').write(cr,uid,k.id,{'account_id':i.account_id.id})
				else:
					if i.account_id.code == 'igst':
						search_temp=self.pool.get('st.input').search(cr,uid,[('bank_payment_line_igst_id','=',i.id)])
						for j in self.pool.get('st.input').browse(cr,uid,search_temp):
							self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
					else:
						search_temp=self.pool.get('st.input').search(cr,uid,[('bank_payment_line_cgst_id','=',i.id)])
						for j in self.pool.get('st.input').browse(cr,uid,search_temp):
							self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
				#customized for gst--------------------------------------------------------------------------
				
					
			for update in rec.payment_one2many:
				self.pool.get('payment.line').write(cr,uid,update.id,{'state':'done'})


		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State

		for payment_his in self.browse(cr,uid,ids):#edited by rohit 12 may
			#receipt_no=payment_his.value_id#payment_his.receipt_no
			curr_id = ''
			cust_name=payment_his.customer_name.name
			if payment_his.payment_date:
				payment_date=payment_his.payment_date
			else:
				payment_date=datetime.now().date()
			payment_type='BANK'
			particulars=payment_his.particulars.name
			for payment_line in payment_his.payment_one2many:
				amount=payment_line.debit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('payment.history').create(cr,uid,{
							'payment_his_many2one':curr_id,
							'payment_number':value_id,'payment_date':payment_date,
							'particulars':particulars,
							'payment_type':payment_type,
							'payment_amount':amount})
			for chk_ln in payment_his.payment_one2many:
				if 'Sundry Creditors' in chk_ln.account_id.name and chk_ln.type=='debit':
						if chk_ln.sundry_expense_one2many:
							for sc in chk_ln.sundry_expense_one2many:
								if not sc.check_exp:
									self.pool.get('sundry.expenses').unlink(cr,uid,sc.id)

		return {
			'name':'Bank Payment',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'account.payment',
			'res_id':res.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
		}

account_payment()


class payment_line(osv.osv):
#### child class for Bank payment
	_inherit = 'payment.line'
	_rec_name = 'type'
	_columns = {
		'bank_st_input_igst_ids':fields.one2many('st.input','bank_payment_line_igst_id','ST Input'),
		'bank_st_input_cgst_ids':fields.one2many('st.input','bank_payment_line_cgst_id','ST Input'),
		'bank_payment_freight_one2many':fields.one2many('st.input','bank_payment_freight_id','Freight Entry'),
		'bank_expense_one2many':fields.one2many('expense.payment','bank_payment_expense_id','Expenses'),
		'sundry_expense_one2many':fields.one2many('sundry.expenses','bank_sundry_expense_id'),
		'freight_input_rate':fields.float('Rate'),
		'igst_check':fields.boolean('IGST input'),
	}

	def show_expense_details(self, cr, uid, ids, context=None):
		sc_flag=False
		for res in self.browse(cr,uid,ids):
			if res.state=='done':
				if res.sundry_expense_one2many!=[]:
					for recs in res.sundry_expense_one2many:
						if not recs.check_exp:
							self.pool.get('sundry.expenses').unlink(cr,uid,recs.id)
			if res.state=='draft':
				exp_list=[]
				new_exp_list=[]
				if res.sundry_expense_one2many!=[]:
					for recs in res.sundry_expense_one2many:
						exp_list.append(recs.purchase_id.id)
						self.pool.get('sundry.expenses').unlink(cr,uid,recs.id)
				search_expenses=self.pool.get('account.purchase.receipts').search(cr,uid,[('customer_name','=',res.customer_name.id),('state','=','done')])
				for rec in self.pool.get('account.purchase.receipts').browse(cr,uid,search_expenses):
					if rec.purchase_receipt_one2many:
						for rec_line in rec.purchase_receipt_one2many:
							if rec_line.account_id.name=='Sundry Creditors' and rec_line.type=='credit':
								exp_list.append(rec.id)
				new_exp_list=list(set(exp_list))
				if new_exp_list:
					for rec in self.pool.get('account.purchase.receipts').browse(cr,uid,new_exp_list):
						bill_value=0.0
						bill_no=[]
						billNo=''
						if rec.purchase_receipt_one2many:
							for rec_line in rec.purchase_receipt_one2many:
								if rec_line.type=='debit' and rec_line.account_id.account_selection!='st_input':
									if rec_line.legal_profession_one2many!=[]:
										for legal in rec_line.legal_profession_one2many:
											if legal.bill_no!=False:
												bill_no.append(legal.bill_no)
									if rec_line.purchase_expense_one2many!=[]:
										for exp in rec_line.purchase_expense_one2many:
											if exp.bill_no!=False:
												bill_no.append(exp.bill_no)
									if rec_line.goods_purchase_expense_one2many!=[]:
										for exp1 in rec_line.goods_purchase_expense_one2many:
											if exp1.bill_no!=False:
												bill_no.append(exp1.bill_no)
									if rec_line.purchase_freight_one2many!=[]:
										for fr in rec_line.purchase_freight_one2many:
											if fr.bill_no!=False:
												bill_no.append(fr.bill_no)
								if bill_no!=[]:
									bill_no=list(set(bill_no))
									billNo=','.join(bill_no)
								if rec_line.account_id.name=='Sundry Creditors' and rec_line.type=='credit':
									bill_value=rec_line.credit_amount
									sc_flag=True
						if sc_flag:
							self.pool.get('account.purchase.receipts').write(cr,uid,rec.id,{'expense_flag':True})
							sundry_id=self.pool.get('sundry.expenses').create(cr,uid,{
								'customer_name':rec.customer_name.id,
								'purchase_id':rec.id,
								'name':rec.receipt_no,
								'bill_no':billNo,
								'bill_value':bill_value,
								'bill_date':rec.receipt_date,
								'bank_sundry_expense_id':res.id,
								})
		return True

	def add(self, cr, uid, ids, context=None): 
	### Bank Payment line (arrow add button) to open wizard
		total= total_amount= service_tax = ed_cess = hs_cess=0.0
		temp=[]
		bank_charges_bool=True
		account_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
								  'primary_cost_vehicle','primary_cost_service', 'primary_cost_cse_office']
		
		acc_selection_list2 = ['security_deposit','itds','sundry_deposit','st_input','excise_input','iob_two','iob_one']
		
		for i in self.browse(cr,uid,ids):#For st-input  and Excise input
			srch_tmp = self.pool.get('account.payment').search(cr,uid,[('id','=',i.payment_id.id)])
			for j in self.pool.get('account.payment').browse(cr,uid,srch_tmp):
				search_line =  self.pool.get('payment.line').search(cr,uid,[('payment_id','=',j.id)])
				for t in self.pool.get('payment.line').browse(cr,uid,search_line):
					if t.account_id.account_selection in account_selection_list:
						total += t.debit_amount
	
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			acc_id = res.account_id
			code = res.account_id.code
			acc_selection = acc_id.account_selection

			for i in self.pool.get('account.payment').browse(cr,uid,[res.payment_id.id]):
				if i.payment_one2many:
					for j in i.payment_one2many:
						if j.account_id.bank_charges_bool==True:
							bank_charges_bool=False

			if not acc_id.name:
				raise osv.except_osv(('Alert'),('Please Select Account.'))

			if 'Sundry Creditors' in res.account_id.name and res.type=='debit':
				self.show_expense_details(cr,uid,ids,context=context)
				objt = 'gst_accounting'
				view_name2 = 'bank_expense_payment_form'
				name_wizard = "Expense Details"
				models_data = self.pool.get('ir.model.data')
				if view_name2:
					form_view = models_data.get_object_reference(cr, uid, objt, view_name2)
					return {
							'name': (name_wizard),
							'type': 'ir.actions.act_window',
							'view_id': False,
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'payment.line',
							'target' : 'new',
							'res_id': int(res_id),
							'views': [(form_view and form_view[1] or False, 'form'),
									  (False, 'calendar'), (False, 'graph')],
							'domain': '[]',
							'nodestroy': True
						}
				else:
					raise osv.except_osv(('Alert'),('No Information'))

			if ('Freight Inward-GST' in res.account_id.name) or ('Freight Outward-GST' in res.account_id.name) :
				# print debit_amount,'kkkkkk'
				if debit_amount>750.0:
					objt = 'gst_accounting'
					view_name2 = 'bank_payment_freight_entry_form'
					name_wizard = "Add Freight Details"
				else:
					raise osv.except_osv(('Alert'),('No Information'))
				models_data = self.pool.get('ir.model.data')
				form_view = models_data.get_object_reference(cr, uid, objt, view_name2)
				return {
						'name': (name_wizard),
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'payment.line',
						'target' : 'new',
						'res_id': int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								  (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True
					}
			if acc_selection == 'expenses':
				objt = 'gst_accounting'
				view_name2 = 'expense_bank_form'
				name_wizard = "Add Expenses Details"
				models_data = self.pool.get('ir.model.data')
				form_view = models_data.get_object_reference(cr, uid, objt, view_name2)
				return {
						'name': (name_wizard),
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'payment.line',
						'target' : 'new',
						'res_id': int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								  (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True
					}
			if acc_selection in acc_selection_list2:
				if acc_selection in ('st_input','excise_input'):
					search_tax_id = [] ###To Remove Hard Code Service Tax 
					for exc_input in self.pool.get('account.account').search(cr,uid,[('id','=',res.account_id.id)]):
						cr.execute('select tax_id from account_account_tax_default_rel where account_id = %s',(exc_input,))
					# if acc_selection == 'st_input':
					# 	view_name =  'st_input_form'
					# 	name_wizard =  "Add ST Input Details"
					if acc_selection == 'st_input':
						if code == False:
							view_name =  'st_input_form'
							name_wizard =  "Add ST Input Details"
							objt = 'account_sales_branch'
						elif code in ('igst','cgst'):
							if code == 'igst':
								view_name = 'account_bank_st_input_form_igst_inherit'
								objt = 'gst_accounting'
								name_wizard = "Add ST Input Details"
							if code == 'cgst':
								view_name = 'account_bank_st_input_form_cgst_inherit'
								objt = 'gst_accounting'
								name_wizard = "Add ST Input Details"
						else:
							raise osv.except_osv(('Alert'),('No Information!'))
					if acc_selection == 'excise_input':
						objt = 'account_sales_branch'
						view_name =  'excise_input_form'
						name_wizard =  "Add Excise Input Details"
						
				if acc_selection == 'iob_two':## iob II
						view_name =   'account_iob_two_form'
						objt = 'account_sales_branch'
						name_wizard = "Add"+" "+ acc_id.name +" "+" Details"
	
				if acc_selection == 'iob_one':## iob one
					if acc_id.ho_bank_wizard_check == True:
						objt = 'account_sales_branch'
						view_name =   'account_iob_one_payment_form'
						name_wizard =  "Add"+" "+ acc_id.name +" "+"Details"
					else:
						return True
	
				if acc_selection == 'itds':## itds
					view_name =  'account_itds_form'
					objt = 'account_sales_branch'
					name_wizard = "Add ITDS on Contract Payments Details"
					
				if acc_selection == 'sundry_deposit':
					view_name ='account_sundry_dposit_form'
					objt = 'account_sales_branch'
					name_wizard = "Add Sundry Deposit Details"

				if acc_selection == 'security_deposit' and res.type =='debit': ###security deposit sagar >>>18 Feb 2016
					view_name = 'bank_payment_security_deposit_form'
					objt = 'account_sales_branch'
					name_wizard = "Add Sundry Deposit Details"
					
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, objt, view_name)
				return {
					'name': (name_wizard),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'payment.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					   }
			
			if acc_selection in account_selection_list:
				if acc_id.account_selection == 'primary_cost_cse':
					view_name2 = 'account_primary_cost_form'
					self.write(cr,uid,res_id,{'wizard_id':res_id})
					
				elif acc_selection == 'primary_cost_service':
					view_name2 =  'account_primary_cost_service_form'
	
				elif acc_selection == 'primary_cost_office':
					view_name2 =  'account_bank_primary_cost_office_form'
	
				elif acc_selection == 'primary_cost_phone':
					view_name2 = 'account_bank_primary_cost_phone_form'
	
				elif acc_selection == 'primary_cost_vehicle':
					view_name2 ='account_bank_primary_cost_vehicle_form'
	
				elif acc_selection == 'primary_cost_cse_office':
					view_name2 = 'account_primary_bank_cost_cse_office_form'
	
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name2)
				return {
					'name': ("Add Primary Cost Category Details"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'payment.line',
					'res_id':int(res_id),
					'target' : 'new',
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
				}
			else:
				raise osv.except_osv(('Alert'),('No Information '))

	def save_input_bank_gst(self, cr, uid, ids, context=None):
		total_amount = 0.0
		bill_no=[]
		bill_date=[]
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		for rec in self.browse(cr,uid,ids):
			if rec.bank_st_input_cgst_ids == [] and rec.bank_st_input_igst_ids == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.bank_st_input_cgst_ids:
				if line:
					bn = line.bill_no
					bn = bn.lower()
					bn = bn.strip()
					bn = bn.replace(" ","")
					if len(bn) >16:
						raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
					if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if not reg.match(bn):
						raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
					total_amount = total_amount + line.cgst_tax_amount
					bill_no.append(line.bill_no)
					bill_date.append(line.bill_date)
			for line in rec.bank_st_input_igst_ids:
				if line:
					bn = line.bill_no
					bn = bn.lower()
					bn = bn.strip()
					bn = bn.replace(" ","")
					if len(bn) >16:
						raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
					if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if not reg.match(bn):
						raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
					total_amount = total_amount + line.igst_tax_amount
					bill_no.append(line.bill_no)
					bill_date.append(line.bill_date)
			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':round(total_amount,2)})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':round(total_amount,2)})
		if bill_no!=[]:
			bill_no=list(set(bill_no))
			if len(bill_no)>1:
				raise osv.except_osv(('Alert'),('You cannot add different bill nos and its Freight details!'))
		if bill_date!=[]:
			bill_date=list(set(bill_date))
			if len(bill_date)>1:
				raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
		return {'type': 'ir.actions.act_window_close'}

	def save_bank_freight_entry(self, cr, uid, ids, context=None):
		amount = 0.0
		total_amount = 0.0
		freight_tax_amount = 0.0
		igst_check=False
		bill_no=[]
		bill_date=[]
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		for rec in self.browse(cr,uid,ids):
			if rec.bank_payment_freight_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.bank_payment_freight_one2many:
				if line.bill_value:
					bn = line.bill_no
					bn = bn.lower()
					bn = bn.strip()
					bn = bn.replace(" ","")
					if len(bn) >16:
						raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
					if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if not reg.match(bn):
						raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
					freight_tax_amount = (line.bill_value * float(rec.freight_input_rate))/100
					amount = (line.bill_value*float(rec.freight_input_rate))/100 + line.bill_value
					total_amount =total_amount+line.bill_value
					if line.from_state.id!=line.to_state.id:
						self.pool.get('st.input').write(cr,uid,line.id,{'total_amount':amount,'freight_tax_amount':freight_tax_amount,'sgst_tax_amount':0.0,'cgst_tax_amount':0.0,'igst_tax_amount':round(freight_tax_amount,2),'freight_input_rate':rec.freight_input_rate})
						igst_check=True
					else:
						self.pool.get('st.input').write(cr,uid,line.id,{'total_amount':amount,'freight_tax_amount':freight_tax_amount,'sgst_tax_amount':round(freight_tax_amount/2,2),'cgst_tax_amount':round(freight_tax_amount/2,2),'igst_tax_amount':0.0,'freight_input_rate':rec.freight_input_rate})						
					bill_no.append(line.bill_no)
					bill_date.append(line.bill_date)
			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':round(total_amount,2),'igst_check':igst_check})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':round(total_amount,2),'igst_check':igst_check})
		if bill_no!=[]:
			bill_no=list(set(bill_no))
			if len(bill_no)>1:
				raise osv.except_osv(('Alert'),('You cannot add different bill nos and its Freight details!'))
		if bill_date!=[]:
			bill_date=list(set(bill_date))
			if len(bill_date)>1:
				raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
		return {'type': 'ir.actions.act_window_close'}

	def save_expense_entry(self, cr, uid, ids, context=None):
		amount = 0.0
		total_amount = 0.0
		tax_amount = 0.0
		rate = 0.0
		bill_no=[]
		bill_date=[]
		cgst_amount=sgst_amount=igst_amount=0.0
		igst_check=False
		today_date = effective_date_from = ''
		today_date = str(datetime.now().date())
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		for rec in self.browse(cr,uid,ids):
			igst_check=rec.igst_check
			if rec.bank_expense_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.bank_expense_one2many:
				if line.bill_value:
					bn = line.bill_no
					bn = bn.lower()
					bn = bn.strip()
					bn = bn.replace(" ","")
					if len(bn) >16:
						raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
					if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if not reg.match(bn):
						raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
					if rec.customer_name.id:
						if rec.customer_name.gst_type_supplier.name=='Composition':
							tax_amount=0.0
							amount = line.bill_value
							total_amount =total_amount+amount
							cgst_amount=sgst_amount=igst_amount=0.0
							rate=0.0
						else:
							if line.gst_item_master.effective_date_from:
								if today_date >= line.gst_item_master.effective_date_from:
									tax_amount = (line.bill_value * float(line.gst_item_master.new_tax_rate))/100
									amount = (line.bill_value*float(line.gst_item_master.new_tax_rate))/100 + line.bill_value
									total_amount =total_amount+amount
									rate=line.gst_item_master.new_tax_rate
								else:
									tax_amount = (line.bill_value * float(line.gst_item_master.item_rate))/100
									amount = (line.bill_value*float(line.gst_item_master.item_rate))/100 + line.bill_value
									total_amount =total_amount+amount
									rate=line.gst_item_master.item_rate
							else:
								tax_amount = (line.bill_value * float(line.gst_item_master.item_rate))/100
								amount = (line.bill_value*float(line.gst_item_master.item_rate))/100 + line.bill_value
								total_amount =total_amount+amount
								rate=line.gst_item_master.item_rate
							if igst_check:
								igst_amount=round(tax_amount,2)
							else:
								cgst_amount=round(tax_amount/2,2)
								sgst_amount=cgst_amount
					self.pool.get('expense.payment').write(cr,uid,line.id,
						{'total_amount':round(amount,2),
						'tax_amount':round(tax_amount,2),'rate':rate,
						'cgst_amount':cgst_amount,
						'sgst_amount':sgst_amount,
						'igst_amount':igst_amount})
					bill_no.append(line.bill_no)
					bill_date.append(line.bill_date)
			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':round(total_amount,2)})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':round(total_amount,2)})
		if bill_no!=[]:
			bill_no=list(set(bill_no))
			if len(bill_no)>1:
				raise osv.except_osv(('Alert'),('You cannot add different bill nos and its Expenses details!'))
		if bill_date!=[]:
			bill_date=list(set(bill_date))
			if len(bill_date)>1:
				raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
		return {'type': 'ir.actions.act_window_close'}

	def save_sundry_expense_entry(self, cr, uid, ids, context=None):
		amount = 0.0
		total_amount = 0.0
		tax_amount = 0.0
		flag=False
		for rec in self.browse(cr,uid,ids):
			if rec.sundry_expense_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.sundry_expense_one2many:
				if line.check_exp:
					flag=True
					total_amount=total_amount+line.bill_value
			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':round(total_amount,2)})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':round(total_amount,2)})
		if flag==False:
			raise osv.except_osv(('Alert'),('Select any record to process!'))
		return {'type': 'ir.actions.act_window_close'}

payment_line()

class cust_supp_credit_refund(osv.osv):
	_inherit = 'cust.supp.credit.refund'
	_order = 'payment_date desc'

	def process(self, cr, uid, ids, context=None):
	### Customer/Supplier Payment Refund Process Button 
		sales_receipts = self.pool.get('account.sales.receipts')
		sales_receipts_line = self.pool.get('account.sales.receipts.line')
		advance_receipts = self.pool.get('advance.sales.receipts')
		advance_history = self.pool.get('advance.receipt.history')
		cr_total = dr_total = total = iob_total = 0.0
		post=[]
		post_new = []
		cr_refund_id = move = cr_paid_refund_id = iob_two_id = ''
		today_date = datetime.now().date()
		py_date = False
		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			if res.payment_date:
			        check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
			        if check_bool:
			                if res.payment_date != str(today_date):
        				        raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
				py_date = str(today_date + relativedelta(days=-5))
				if res.payment_date < str(py_date) or res.payment_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
				payment_date=res.payment_date
			else:	
				payment_date = datetime.now().date()
				
			for line in res.credit_refund_cs_one2many:
				if line.type == 'credit' and  line.account_id.account_selection not in ('iob_one','iob_two','cash'):
					raise osv.except_osv(('Alert'),('Please select cash or bank ledger to process.'))
				if line.type == 'credit':
					if line.credit_amount <= 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				elif line.type == 'debit':
					if line.debit_amount <= 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				else:
					raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(line.account_id.name))))

				cr_total += line.credit_amount
				dr_total += line.debit_amount

				account_id = line.account_id.id
				temp = tuple([account_id])
				post.append(temp)
				for i in range(0,len(post)):
					for j in range(i+1,len(post)):
						if post[i][0]==post[j][0]:
							raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))

		for refund in self.browse(cr,uid,ids):
			for refund_line in refund.credit_refund_cs_one2many:
				account_name = refund_line.account_id.name
				credit_amount = refund_line.credit_amount
				debit_amount = refund_line.debit_amount
				acc_selection = refund_line.account_id.account_selection
				customer_name = refund.customer_name.name                #sagar adavance refund  27Aug15>>>
				pending_amount = amt=0.0
				receipt_no=''

				if acc_selection in ('against_ref' ,'advance') and refund_line.status == 'against_adv':
					for ln2 in refund_line.advance_record_one2many:
						total += ln2.partial_amt
						
					if credit_amount:
							if total != credit_amount:
								raise osv.except_osv(('Alert'),('Credit Amount should be equal to wizard amount.'))
					if debit_amount:
						if total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal to wizard amount.'))

					for advance_refund in refund_line.advance_record_one2many:
						if refund_line.payment_status == 'partial_payment':
						        if advance_refund.advance_pending < advance_refund.partial_amt :
						                raise osv.except_osv(('Alert'),('enter proper partial amount'))
					                pending_amount = advance_refund.advance_pending - advance_refund.partial_amt

						if advance_refund.check_advance_against_ref == True:
							new_cus_name =advance_refund.partner_id.name
							amt = 0.0 if refund_line.payment_status == 'full_payment' else pending_amount
							advance_receipts.write(cr,uid,advance_refund.id,{
										'check_advance_against_ref_process':True if refund_line.payment_status == 'full_payment' else False,
										'check_advance_against_ref':False,
										'advance_pending':amt,
										})
							############################
							receipt_id=receipt_no=''
							line_srch=sales_receipts_line.search(cr,uid,[('id','=',advance_refund.advance_id.id)])
							if line_srch:
							        for i in sales_receipts_line.browse(cr,uid,line_srch):
							                main_srch=sales_receipts.search(cr,uid,[('id','=',i.receipt_id.id)])
							                for j in sales_receipts.browse(cr,uid,main_srch):
							                        receipt_no=j.receipt_no
							                        sales_receipts.write(cr,uid,j.id,{'advance_pending':amt})
							                
							###########################
							advance_history.create(cr,uid,{
										'advance_receipt_no':receipt_no if receipt_no else advance_refund.ref_no,
										'cust_name':advance_refund.partner_id.id,
										'advance_refund_amount':advance_refund.advance_pending if refund_line.payment_status == 'full_payment' else advance_refund.partial_amt,
										'advance_pending_amount':amt,
										'advance_receipt_date':datetime.now().date(),
										'advance_date':advance_refund.ref_date,
										'history_advance_id':advance_refund.id,
										'service_classification':advance_refund.service_classification,
										'csr_receipt_id':refund_line.id,
										'receipt_id':receipt_id if receipt_id else False,})  

				if acc_selection == 'against_ref' and refund_line.status != 'against_adv' :
					for new_line in refund_line.credit_refund_one2many:
						cr_refund_id = new_line.cr_refund_id
					for new_line1 in refund_line.credit_paid_refund_one2many:
						cr_paid_refund_id = new_line1.cr_paid_refund_id
					if not cr_refund_id and not cr_paid_refund_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

					if refund_line.credit_refund_one2many:
						for ln in refund_line.credit_refund_one2many:
							total += ln.amount
							account_id = ln.credit_note_no.id
							temp = tuple([account_id])
							post_new.append(temp)
							for i in range(0,len(post_new)):
								for j in range(i+1,len(post_new)):
									if post_new[i][0]==post_new[j][0]:
										raise osv.except_osv(('Alert!'),('Duplicate entries are not allowed.'))
						
						if credit_amount:
							if total != credit_amount:
								raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
						if debit_amount:
							if total != debit_amount:
								raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

					if refund_line.credit_paid_refund_one2many:				
						for ln1 in refund_line.credit_paid_refund_one2many:
							total += ln1.amount
							account_id = ln1.credit_note_no_st.id
							temp = tuple([account_id])
							post_new.append(temp)
							for i in range(0,len(post_new)):
								for j in range(i+1,len(post_new)):
									if post_new[i][0]==post_new[j][0]:
										raise osv.except_osv(('Alert!'),('Duplicate entries are not allowed.'))

						if credit_amount:
							if total != credit_amount:
								raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))

						if debit_amount:
							if total != debit_amount:
								raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

				if acc_selection == 'advance' and refund_line.status == 'against_adv':
					for ln2 in refund_line.advance_record_one2many:
						total += ln2.partial_amt
						account_id = ln2.cust_advance_id.account_id.id
						temp = tuple([account_id])
						post_new.append(temp)
						for i in range(0,len(post_new)):
							for j in range(i+1,len(post_new)):
								if post_new[i][0]==post_new[j][0]:
									raise osv.except_osv(('Alert!'),('Duplicate entries are not allowed.'))


				if acc_selection == 'iob_two':
					for iob_two_line in refund_line.credit_refund_iob_two:
						iob_two_id = iob_two_line.cr_refund_iob_two_id
					if not iob_two_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

					if refund_line.credit_refund_iob_two:
						for iob_two_ln in refund_line.credit_refund_iob_two:
							if not iob_two_ln.cheque_no:
								raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
							if not iob_two_ln.drawee_bank_name_new:
								raise osv.except_osv(('Alert!'),('Please provide Drawee Bank Name.'))
							if not iob_two_ln.bank_branch_name:
								raise osv.except_osv(('Alert!'),('Please provide Bank Branch Name.'))

							cheque_amount = iob_two_ln.cheque_amount
							iob_total = iob_total + cheque_amount
							if iob_two_ln.cheque_no:                       
								for n in str(iob_two_ln.cheque_no):
									p = re.compile('([0-9]{6}$)')
									if p.match(iob_two_ln.cheque_no)== None :
										raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
						if credit_amount:
							if iob_total != credit_amount:
								raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))

						if debit_amount:
							if iob_total != debit_amount:
								raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))
				if acc_selection == 'iob_one':
					if refund_line.credit_refund_iob_one==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					iob_total=0.0
					for iob_one_ln in refund_line.credit_refund_iob_one:
						if not iob_one_ln.cheque_no:
							raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
						if not iob_one_ln.drawee_bank_name:
							raise osv.except_osv(('Alert!'),('Please provide Drawee Bank Name.'))
						if not iob_one_ln.bank_branch_name:
							raise osv.except_osv(('Alert!'),('Please provide Bank Branch Name.'))

						iob_total += iob_one_ln.cheque_amount
						if iob_one_ln.cheque_no:                       
							for n in str(iob_one_ln.cheque_no):
								p = re.compile('([0-9]{6}$)')
								if p.match(iob_one_ln.cheque_no)== None :
									raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
					if credit_amount:
						if iob_total != credit_amount:
							raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if iob_total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))


		for rec in self.browse(cr,uid,ids):
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_refund_payment_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_credit_refund_payment_tree')
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','cust.supp.credit.refund')])
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
					if comp_id.cust_sup_refund_payment_id:
						cust_sup_refund_payment_id = comp_id.cust_sup_refund_payment_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			seq_start = 1	
			if pcof_key and cust_sup_refund_payment_id:
				cr.execute("select cast(count(id) as integer) from cust_supp_credit_refund where state not in ('draft') and payment_no is not null and payment_date>='2017-07-01' and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
		        	temp_count=cr.fetchone()
		        	if temp_count[0]:
		        		count= temp_count[0]
		        	seq=int(count+seq_start)
		        	# seq_new=self.pool.get('ir.sequence').get(cr,uid,'cust.supp.credit.refund')
				#value_id = pcof_key + cust_sup_refund_payment_id +  str(year1) +str(seq_new).zfill(6)
				value_id = pcof_key + cust_sup_refund_payment_id +  str(financial_year) +str(seq).zfill(5)
				existing_value_id = self.pool.get('cust.supp.credit.refund').search(cr,uid,[('payment_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + cust_sup_refund_payment_id +  str(financial_year) +str(seq+1).zfill(5)

			self.write(cr,uid,ids,{'payment_no':value_id,'payment_date': payment_date,'voucher_type':'Cust_refund'})
			date = payment_date
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
						'narration':rec.narration if rec.narration else '',
						'voucher_type':'Cust_refund',},context=context)

                	for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.credit_refund_cs_one2many:
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
			self.write(cr,uid,rec.id,{'state':'done','status':''})
			for update in rec.credit_refund_cs_one2many:
				self.pool.get('cust.supp.credit.refund.line').write(cr,uid,update.id,{'state':'done'})
				for credit_line in update.credit_refund_one2many:
					credit_note_no = credit_line.credit_note_no.credit_note_no
					
					srch_credit = self.pool.get('credit.note').search(cr,uid,[('credit_note_no','=',credit_note_no),('state','=','done')])
					for brw_credit in self.pool.get('credit.note').browse(cr,uid,srch_credit):
						for i in brw_credit.credit_note_one2many:
							for a in i.credit_note_history_one2many:
						
								self.pool.get('invoice.adhoc.master').write(cr,uid,
								                a.invoice_receipt_history_id.id,{
											                'pending_amount':0.0,
											                'pending_status':'paid',
											                'status':'paid'})
											
								self.pool.get('invoice.receipt.history').create (cr,uid,{
											'invoice_paid_amount':a.invoice_writeoff_amount,
											'refund_date':rec.payment_date,
											'cse':a.cse.id,
											'service_classification':a.service_classification,
											'tax_rate':a.tax_rate,
											'invoice_number':a.invoice_number,
											'invoice_date':a.invoice_date,
											'invoice_receipt_history_id':a.invoice_receipt_history_id.id,
											'receipt_number':rec.payment_no,
											})
											
							for b in i.credit_note_itds_history_one2many:
								self.pool.get('invoice.adhoc.master').write(cr,uid,b.invoice_receipt_history_id.id,{
											                'pending_amount':0.0,
											                'pending_status':'paid',
											                'status':'paid'})
											
					                        self.pool.get('invoice.receipt.history').create (cr,uid,{
											'invoice_paid_amount':b.itds_revert_amount,
											'refund_date':rec.payment_date,
											'cse':b.cse.id,
											'service_classification':b.service_classification,
											'tax_rate':b.tax_rate,
											'invoice_number':b.invoice_number,
											'invoice_date':b.invoice_date,
											'invoice_receipt_history_id':b.invoice_receipt_history_id.id,
											'receipt_number':rec.payment_no,
											})
											
						self.pool.get('credit.note').write(cr,uid,brw_credit.id,{'state':'finish'})
						
				for credit_line1 in update.credit_paid_refund_one2many:
					credit_note_no_st = credit_line1.credit_note_no_st.credit_note_no
					
					srch_credit1 = self.pool.get('credit.note.st').search(cr,uid,[('credit_note_no','=',credit_note_no_st),('state','=','done')])
					for brw_credit1 in self.pool.get('credit.note.st').browse(cr,uid,srch_credit1):
						############ HHH 29jan16 - updating IAM 
						for cn_rec in brw_credit1.credit_note_st_one2many:
						        for cn_line in cn_rec.credit_st_id_history_one2many:
							        if cn_line.check_invoice == True:
							                self.pool.get('invoice.adhoc.master').write(cr,uid,cn_line.invoice_receipt_history_id.id,{
											'pending_amount':0.0,
											'pending_status':'paid',
											'status':'paid'})

									self.pool.get('invoice.receipt.history').create (cr,uid,{
											'invoice_paid_amount':cn_line.invoice_writeoff_amount,
											'refund_date':rec.payment_date,
											'cse':cn_line.cse.id,
											'service_classification':cn_line.service_classification,
											'tax_rate':cn_line.tax_rate,
											'invoice_number':cn_line.invoice_number,
											'invoice_date':cn_line.invoice_date,
											'invoice_receipt_history_id':cn_line.invoice_receipt_history_id.id,
											'receipt_number':rec.payment_no,
											})
						#############
						self.pool.get('credit.note.st').write(cr,uid,brw_credit1.id,{'state':'finish'})
						
		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
		return  {
			'name':'Customer Supplier Credit Refund',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'cust.supp.credit.refund',
			'res_id':rec.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
		}

		return True

cust_supp_credit_refund()



class st_input(osv.osv):
	_inherit = 'st.input'
	_rec_name='bill_no'

	_columns = {
		'bank_payment_line_igst_id':fields.many2one('payment.line','Bank Payment line'),
		'bank_payment_line_cgst_id':fields.many2one('payment.line','Bank Payment line'),
		'bank_payment_freight_id':fields.many2one('payment.line','Freight Entry'),
	}

st_input()

class sundry_expenses(osv.osv):
	_inherit = 'sundry.expenses'

	_columns = {
		'bank_sundry_expense_id':fields.many2one('payment.line','Bank Payment Line'),
	}

sundry_expenses()

