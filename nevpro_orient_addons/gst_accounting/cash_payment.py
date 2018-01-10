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

class cash_payment(osv.osv):
	_inherit = 'cash.payment'
	_order = 'payment_date desc'

	def add_cash_info(self, cr, uid, ids, context=None):
        ###Cash payment (add button) add record in child table(cash payment line)
		freight_input_rate = 0.0
		check_freight=igst_check=False
		customer_state=False
		for res in self.browse(cr,uid,ids):

			if not res.customer_name and res.account_id.name=='ITDS on Contract Pymt':
				raise osv.except_osv(('Alert'),('Please select Supplier Name'))

			state = res.state
			acc_id = res.account_id.id
			types = res.type
			# account_id1=res.account_id
			#for i in res.cash_payment_one2many:     #remove duplicate as per vijay requirement. on 1 dec
			#	if account_id1.id==i.account_id.id:
			#		raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

			if state == 'draft':
				if not acc_id:
					raise osv.except_osv(('Alert'),('Please select Account Name.'))
				if not types:
					raise osv.except_osv(('Alert'),('Please select Type.'))
			
				if acc_id:
					if res.account_id.account_selection in ('iob_one','iob_two') :
						raise osv.except_osv(('Alert'),('Please select proper account name.'))

			total= total_amount= service_tax = ed_cess = hs_cess = total_amount=0.0
			auto_credit_cal=auto_debit_cal=auto_credit_total=auto_debit_total=0.0
			acc_selection_list =['primary_cost_phone','primary_cost_cse','primary_cost_office',
								 'primary_cost_vehicle','primary_cost_service','primary_cost_cse_office']
			if 'Freight Inward-GST' in res.account_id.name:
				freight_input_rate='5'
				if not res.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
				if res.customer_name:
					if not res.customer_name.state_id:
						raise osv.except_osv(('Alert'),('Kindly update the State of Supplier!'))
			if 'Freight Outward-GST' in res.account_id.name:
				freight_input_rate='5'
				if not res.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
				if res.customer_name:
					if not res.customer_name.state_id:
						raise osv.except_osv(('Alert'),('Kindly update the State of Supplier!'))					 
			if res.cash_payment_one2many and res.customer_name.gst_no==False or res.customer_name.gst_no=='Unregistered':
				for ln in res.cash_payment_one2many:
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
			if res.account_id.account_selection in ('st_input','excise_input'):
			        if res.cash_payment_one2many:
				     for t in res.cash_payment_one2many:
					if t.account_id.account_selection in acc_selection_list:
						total += t.debit_amount

				search_tax_id = [] ###To Remove Hard Code Service Tax 
				service_tax = ed_cess = hs_cess = 0.0

			if  res.account_id.account_selection =='cash':
				if res.type=='debit':
					raise osv.except_osv(('Alert'),('Please select type as Credit.'))
				else:	
					for k in res.cash_payment_one2many:
						if k.type=='credit':
							auto_debit_cal += k.credit_amount
						if k.type=='debit':
							auto_credit_cal += k.debit_amount
					if auto_debit_cal<auto_credit_cal:
						auto_credit_cal -= auto_debit_cal
					else:
						auto_credit_cal=0.0
			if res.customer_name.id:
				if res.customer_name.gst_type_supplier.name=='Composition':
					# tax_rate=0.0
					freight_input_rate=0.0
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
			if acc_id:
					self.pool.get('cash.payment.line').create(cr,uid,{
												'cash_payment_id':res.id,
												'debit_amount':total_amount,
												'credit_amount':auto_credit_cal,
												'account_id':acc_id,
												'type':res.type,
												'customer_name':res.customer_name.id if res.customer_name.id else '',
												'freight_input_rate':freight_input_rate,
												'igst_check':igst_check,
												})

			self.write(cr,uid,res.id,{'account_id':None,'type':''})

		return True

	def process(self, cr, uid, ids, context=None):
		cr_total = dr_total = employee_total= itds_total = chk_cash_entry=freight_debit=sc_debit=0.0
		total_cgst_amount=total_sgst_amount=total_igst_amount=total_cgst=total_sgst=total_igst=0.0
		cash_cost_id = employee_tempname= move = ''
		post=[]
		today_date = datetime.now().date()
		py_date=freightin_check=freightot_check=sc_flag=igst_check=False
		total_frin_amount=total_frot_amount=cash_exp_amount=total_sc_amount=0.0
		models_data=self.pool.get('ir.model.data')
		advance_append_list =[]
		account_account_obj = self.pool.get('account.account')
		primary_cost_category_obj = self.pool.get('primary.cost.category')
		o = self.browse(cr,uid,ids[0])
		for line in o.cash_payment_one2many:
			main_id = line.account_id.id
			line_id = line.id
			advance_account_check = account_account_obj.browse(cr,uid,main_id)
			advance_expence_check_val = advance_account_check.advance_expence_check
			advance_staff_check_val = advance_account_check.advance_staff_check
			if advance_staff_check_val == True and advance_expence_check_val == False:
				search_id = primary_cost_category_obj.search(cr,uid,[('cash_primary_cost_id','=',line_id)])
				if len(search_id) == 0:
						raise osv.except_osv(('Alert'),('Primary Cost Category are not added in Advance to staff account.'))
		for res in self.browse(cr,uid,ids):
			if res.customer_name:
				if not res.customer_name.gst_type_supplier:
					raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
				if res.customer_name.gst_type_supplier and (res.customer_name.gst_no==False or res.customer_name.gst_no=='' or res.customer_name.gst_no==None):
					raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
				if res.customer_name.gst_no==False or res.customer_name.gst_no=='' or res.customer_name.gst_no==None:
					raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
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
			for line in res.cash_payment_one2many:
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
				temp = tuple([account_id])
				post.append(temp)
				for i in range(0,len(post)):
					for j in range(i+1,len(post)):
						if post[i][0]==post[j][0]:
							pass
				if line.account_id.account_selection == 'cash':
					chk_cash_entry+=1
			if 	chk_cash_entry ==0.0:
				raise osv.except_osv(('Alert'),('Please select proper account name.'))
			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))
			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
		for rec in self.browse(cr,uid,ids):
			input_list=[]
			freight_list_new=[]
			for chk_ln in rec.cash_payment_one2many:   
				if chk_ln.account_id.account_selection == 'primary_cost_service' and chk_ln.account_id.bank_charges_bool:
					self.write(cr,uid,rec.id,{'bank_charges_check':True})
			for chk_ln in rec.cash_payment_one2many:
				if 'Sundry Creditors' in chk_ln.account_id.name and chk_ln.type=='debit':
					if chk_ln.sundry_expense_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (chk_ln.account_id.name))
					else:
						for sc in chk_ln.sundry_expense_one2many:
							if sc.check_exp:
								total_sc_amount=total_sc_amount+sc.bill_value
								self.pool.get('account.purchase.receipts').write(cr,uid,sc.purchase_id.id,{'state':'finish'})
						sc_flag=True
						sc_debit=chk_ln.debit_amount
				if 'Freight Inward-GST' in chk_ln.account_id.name and chk_ln.type=='debit' and chk_ln.debit_amount>750:
					if chk_ln.freight_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (chk_ln.account_id.name))
					else:
						freight_list_new=[]
						for frin in chk_ln.freight_one2many:
							total_frin_amount=total_frin_amount+frin.bill_value
							total_cgst=total_cgst+frin.cgst_tax_amount
							total_sgst=total_sgst+frin.sgst_tax_amount
							total_igst=total_igst+frin.igst_tax_amount
							if frin.freight_input_rate:
								freight_list_new.append(frin.id)
						freightin_check=True
						freight_debit=chk_ln.debit_amount
					igst_check=chk_ln.igst_check
				if 'Freight Outward-GST' in chk_ln.account_id.name and chk_ln.type=='debit' and chk_ln.debit_amount>750:
					if chk_ln.freight_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (chk_ln.account_id.name))
					else:
						freight_list_new=[]
						for frot in chk_ln.freight_one2many:
							total_frot_amount=total_frot_amount+frot.bill_value
							total_cgst=total_cgst+frot.cgst_tax_amount
							total_sgst=total_sgst+frot.sgst_tax_amount
							total_igst=total_igst+frot.igst_tax_amount
							if frot.freight_input_rate:
								freight_list_new.append(frot.id)
						freightot_check=True
						freight_debit=chk_ln.debit_amount
					igst_check=chk_ln.igst_check
			if sc_flag:
				if round(total_sc_amount,2)!=round(sc_debit,2):
					raise osv.except_osv(('Alert'),('Total of wizard amount is not equal to Debit amount'))
				if not rec.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			if freightin_check:
				if round(total_frin_amount,2)!=round(freight_debit,2):
					raise osv.except_osv(('Alert'),('Total of wizard amount is not equal to Debit amount'))
				if not rec.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			if freightot_check:
				if round(total_frot_amount,2)!=round(freight_debit,2):
					raise osv.except_osv(('Alert'),('Total of wizard amount is not equal to Debit amount'))
				if not rec.customer_name:
					raise osv.except_osv(('Alert'),('Please select Supplier Name!'))
			for line in rec.cash_payment_one2many:
				total = 0.0
				emp_name = ""
				credit_amount = line.credit_amount
				debit_amount = line.debit_amount
				account_name = line.account_id.name
				acc_selection = line.account_id.account_selection
				gst_applied = line.account_id.gst_applied
				code = line.account_id.code
				acc_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
								  'primary_cost_service','primary_cost_vehicle','primary_cost_cse_office']
				if acc_selection=='expenses' and line.type=='debit':
					igst_check=line.igst_check
					if line.cash_expense_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (line.account_id.name))
					else:
						for cash_exp in line.cash_expense_one2many:
							cash_exp_amount=cash_exp_amount+cash_exp.total_amount
					if cash_exp_amount!=0.0:
						if round(debit_amount,2)!=round(cash_exp_amount,2):
							raise osv.except_osv(('Alert'),("Debit Amount should match with its wizard value!!"))
				if acc_selection == 'security_deposit':
					for sec_dep_line in line.security_deposit_one2many:
						self.pool.get('security.deposit').write(cr,uid,sec_dep_line.id,{
							'security_check_against':True,
							'customer_name':line.customer_name.id if line.customer_name.id else '' ,
							'customer_name_char':res.customer_name.name if res.customer_name.name else '' ,
							})
				if acc_selection == 'sundry_deposit':
					for sun_dep_line in line.cash_sundry_deposite_one2many:
						self.pool.get('sundry.deposit').write(cr,uid,sun_dep_line.id,{
							'sundry_check':True,
							'customer_name':line.customer_name.id if line.customer_name.id else '' ,
							'customer_name_char':res.customer_name.name if res.customer_name.name else '' ,
							})
				if acc_selection in acc_selection_list:
					if acc_selection == 'primary_cost_cse':
						for line1 in line.cash_primary_cost_one2many:
							cash_cost_id = line1.cash_primary_cost_id.id
							emp_name=line1.emp_name.id
							total +=  line1.amount
						self.write(cr,uid,rec.id,{'employee_name':emp_name})
						if not cash_cost_id:
							pass
					if acc_selection == 'primary_cost_office':
						cash_office_id = ''
						office_total = 0.0
						for office_line in line.cash_office_name:
							cash_office_id = office_line.cash_primary_office_id.id
							total +=  office_line.amount
						if not cash_office_id:
							pass
					if acc_selection == 'primary_cost_phone':
						cash_phone_id = ''
						phone_total = 0.0
						for phone_line in line.cash_primary_phone_line:
							cash_phone_id = phone_line.cash_primary_phone_id.id
							total  += phone_line.amount
						if not cash_phone_id:
							pass
					if acc_selection == 'primary_cost_vehicle':
						cash_vehicle_id = ''
						vehicle_total = 0.0
						for vehicle_line in line.cash_primary_vehicle_line:
							cash_vehicle_id = vehicle_line.cash_primary_vehicle_id.id
							total += vehicle_line.amount
						if not cash_vehicle_id:
							pass 
					if acc_selection == 'primary_cost_service':
						cash_service_id = ''
						service_total = 0.0
						for service_line in line.primary_cash_cost_service_one2many:
							cash_service_id = service_line.cash_primary_service_id.id
							total += service_line.amount
						if not cash_service_id:
							pass 
					if acc_selection == 'primary_cost_cse_office':
						cash_cse_id = ''
						cse_total = 0.0
						for cse_line in line.cash_primary_cse_office_one2many:
							cash_cse_id = cse_line.cash_primary_cse_office_id.id
							emp_name = cse_line.emp_name.id
							total +=  cse_line.amount
						self.write(cr,uid,rec.id,{'employee_name':emp_name})
						if not cash_cse_id:
							pass
					if credit_amount:
						if total != credit_amount:
							pass
					if debit_amount:
						if total != debit_amount:
							pass 
				if acc_selection == 'itds':
					if line.itds_cash_one2many != []:
						itds_id = ''
						for itds_line in line.itds_cash_one2many:
							itds_id = itds_line.id
						
						if not itds_id:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					else :
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))			
					if line.itds_cash_one2many:
						for itds_ln in line.itds_cash_one2many:
							total += itds_ln.itds_amount
					if credit_amount:
						if total != credit_amount:
							raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))
				if acc_selection == 'cash' and line.debit_amount >= 50000 or line.credit_amount >= 50000 and res.customer_name.id != False:
					raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))
				balance = 0.0
				if acc_selection == 'cash':
					if line.debit_amount >= 10000 or line.credit_amount >= 10000:
						balance = self.cash_balance(cr,uid,rec.payment_date,context=context)
						if balance < line.credit_amount or balance < line.debit_amount:
							raise osv.except_osv(('Alert'),('Cash account dont have sufficient balance to process.'))
				#customized for gst-------------------------------------------------------------------------------------
				if acc_selection == 'st_input' and gst_applied == False:
					cash_id = ''
					phone_total = 0.0
					for line1 in line.cash_st_input_one2many:
						cash_id =line1.cash_line_input_id

					if not cash_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

				if acc_selection == 'st_input' and gst_applied == True:
					cash_id = ''
					total_debit_amount = 0.0
					phone_total = 0.0
					if code == 'igst':
						if line.cash_st_input_igst_ids ==[]:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						else:
							for line1 in line.cash_st_input_igst_ids:
								cash_id = line1.cash_payment_line_igst_id
								total_debit_amount = total_debit_amount+line1.igst_tax_amount
						total_igst_amount=total_debit_amount
						if round(total_debit_amount,2) != round(debit_amount,2):
							raise osv.except_osv(('Alert'),('Wizard amount and debit amount should be same!'))
					if code == 'cgst':
						if line.cash_st_input_cgst_ids ==[]:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						else:
							for line1 in line.cash_st_input_cgst_ids:
								cash_id = line1.cash_payment_line_cgst_id
								total_debit_amount = total_debit_amount+line1.cgst_tax_amount
						total_cgst_amount=total_debit_amount
						if round(total_debit_amount,2) != round(debit_amount,2):
							raise osv.except_osv(('Alert'),('Wizard amount and debit amount should be same'))
					input_list.append(code)
				#customized for gst------------------------------------------------------------------------------------------
				if acc_selection == 'excise_input':
					cash_id1 = ''
					phone_total = 0.0
					for line1 in line.cash_excise_input_one2many:
						cash_id1 =line1.cash_line_excise_id
					if not cash_id1:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
			# form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_cash_payment_form')
			# tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_cash_payment_tree')
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
			for line in rec.cash_payment_one2many:
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
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','cash.payment')])
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
					if comp_id.cash_payment_id:
						cash_payment_id = comp_id.cash_payment_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
			count = 0
			seq_start = 1
			if pcof_key and cash_payment_id:
				cr.execute("select cast(count(id) as integer) from cash_payment where state not in ('draft') and payment_no is not null and payment_date>='2017-07-01'  and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + cash_payment_id +  str(financial_year) +str(seq).zfill(5)
				existing_value_id = self.pool.get('cash.payment').search(cr,uid,[('payment_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + cash_payment_id +  str(financial_year) +str(seq+1).zfill(5)
			self.write(cr,uid,ids,{'payment_no':value_id,'payment_date': payment_date,'voucher_type':'Payment (Cash)'})
			date = payment_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id
			srch_jour_cash = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Cash')])
			for jour_cash in self.pool.get('account.journal').browse(cr,uid,srch_jour_cash):
				journal_cash = jour_cash.id
			move = self.pool.get('account.move').create(cr,uid,{
									'journal_id':journal_cash,
									'state':'posted',
									'date':date,
									'name':value_id,
									'narration':rec.narration if rec.narration else '',
									'voucher_type':'Payment (Cash)',
									},context=context)
			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.cash_payment_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
											'move_id':line1.id,
											'account_id':ln.account_id.id,
											'debit':ln.debit_amount,
											'name':rec.customer_name.name if rec.customer_name.name else '',
											'journal_id':journal_cash,
											'period_id':period_id,
											'date':date,
											'ref':value_id},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
											'move_id':line1.id,
											'account_id':ln.account_id.id,
											'credit':ln.credit_amount,
											'name':rec.customer_name.name if rec.customer_name.name else '',
											'journal_id':journal_cash,
											'period_id':period_id,
											'date':date,
											'ref':value_id},context=context)
			self.write(cr,uid,rec.id,{'state':'done'})
			if freight_list_new!=[]:
				# if rec.customer_name.gst_no==False or rec.customer_name.gst_no=='Unregistered':
					# if igst_check:
					# 	raise osv.except_osv(('Alert'),("Kindly update the GST Number of Supplier!"))
					# if not igst_check:
					# 	if 'cgst' not in input_list:
					# 		 raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
					# 	if 'sgst' not in input_list:
					# 		 raise osv.except_osv(('Alert'),("Add 'SGST - Input' ledger to process the entry !!")) 
				# for ln in rec.cash_payment_one2many:
					# if rec.customer_name.gst_no==False or rec.customer_name.gst_no=='Unregistered':
					# 	if igst_check:
					# 		raise osv.except_osv(('Alert'),("Kindly update the GST Number of Supplier!"))
					# 	if not igst_check:
					# 		if 'cgst' not in input_list:
					# 			 raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
					# 		if 'sgst' not in input_list:
					# 			 raise osv.except_osv(('Alert'),("Add 'SGST - Input' ledger to process the entry !!")) 
					# if ln.account_id.name in ('CGST - Input','SGST - Input','IGST - Input') and ln.account_id.account_selection=='st_input':
					# 	raise osv.except_osv(('Alert'),("You cannot select '%s' Ledger!")%(ln.account_id.name))
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
						# for chk_ln in rec.cash_payment_one2many:
						# 	if chk_ln.freight_one2many!=[]:						
						# 		for frin in chk_ln.freight_one2many:				
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
			for i in rec.cash_payment_one2many:
				#customized for gst------------------------------------------------------------------------
				if i.account_id.gst_applied == False:
					search_temp=self.pool.get('st.input').search(cr,uid,[('cash_line_input_id','=',i.id)])
					for j in self.pool.get('st.input').browse(cr,uid,search_temp):
						self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
				else:
					if i.account_id.code == 'igst':
						search_temp=self.pool.get('st.input').search(cr,uid,[('cash_payment_line_igst_id','=',i.id)])
						for j in self.pool.get('st.input').browse(cr,uid,search_temp):
							self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
					else:
						search_temp=self.pool.get('st.input').search(cr,uid,[('cash_payment_line_cgst_id','=',i.id)])
						for j in self.pool.get('st.input').browse(cr,uid,search_temp):
							self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
				#customized for gst--------------------------------------------------------------------------
				search_temp1=self.pool.get('st.input').search(cr,uid,[('cash_line_excise_id','=',i.id)])
				for k in self.pool.get('st.input').browse(cr,uid,search_temp1):
					self.pool.get('st.input').write(cr,uid,k.id,{'account_id':i.account_id.id})

			for update in rec.cash_payment_one2many:
				self.pool.get('cash.payment.line').write(cr,uid,update.id,{'state':'done'})
		self.delete_draft_records(cr,uid,ids,context=context) 
		for payment_his in self.browse(cr,uid,ids):
			curr_id = ''
			cust_name=payment_his.customer_name.name
			if  payment_his.payment_date:
				payment_date=payment_his.payment_date
			else:	
				payment_date=datetime.now().date()
			payment_type='CASH'
			particulars=payment_his.particulars.name
			for payment_line in payment_his.cash_payment_one2many:
				amount=payment_line.credit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('payment.history').create(cr,uid,{
											'payment_his_many2one':curr_id,
											'payment_number':value_id,
											'payment_date':payment_date,
											'particulars':particulars,
											'payment_type':payment_type,
											'payment_amount':amount})

			srch = self.pool.get('cash.payment.line').search(cr,uid,[('cash_payment_id','=',rec.id)])
			for i in self.pool.get('cash.payment.line').browse(cr,uid,srch):
				temp=i.account_id.advance_expence_check
				if  i.account_id.account_selection == 'primary_cost_cse' and temp == True:
					for j in self.pool.get('cash.payment.line').browse(cr,uid,srch):
						if j.account_id.account_selection == 'cash':
							for k in i.cash_primary_cost_one2many:
								employee_tempname = k.emp_name.id
								employee_total = k.amount
								if i.debit_amount:
									for emp in self.pool.get('hr.employee').browse(cr,uid,[employee_tempname]):
										emp_debit= emp.debit
										employee_total += emp_debit 
									self.pool.get('hr.employee').write(cr,uid,employee_tempname,{'debit':employee_total})
								if i.credit_amount:
									for emp in self.pool.get('hr.employee').browse(cr,uid,[employee_tempname]):
										emp_credit= emp.credit
										employee_total +=  emp_credit 
									self.pool.get('hr.employee').write(cr,uid,employee_tempname,{'credit':employee_total})
			for chk_ln in payment_his.cash_payment_one2many:
				if 'Sundry Creditors' in chk_ln.account_id.name and chk_ln.type=='debit':
						if chk_ln.sundry_expense_one2many:
							for sc in chk_ln.sundry_expense_one2many:
								if not sc.check_exp:
									self.pool.get('sundry.expenses').unlink(cr,uid,sc.id)
		return {
			'name':'Cash Payment',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'cash.payment',
			'res_id':rec.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
		}


class cash_payment_line(osv.osv):
	_inherit = 'cash.payment.line'
	_rec_name = 'type'

	_columns = {
		'cash_st_input_igst_ids':fields.one2many('st.input','cash_payment_line_igst_id','ST Input'),
		'cash_st_input_cgst_ids':fields.one2many('st.input','cash_payment_line_cgst_id','ST Input'),
		'freight_one2many':fields.one2many('st.input','freight_id','Freight Entry'),
		'cash_expense_one2many':fields.one2many('expense.payment','cash_payment_expense_id'),
		'sundry_expense_one2many':fields.one2many('sundry.expenses','cash_sundry_expense_id'),
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
								'cash_sundry_expense_id':res.id,
								})
		return True

	def add(self, cr, uid, ids, context=None):  
		total = total_amount = service_tax = ed_cess = hs_cess = 0.0
		temp = []
		for i in self.browse(cr,uid,ids):
			acc_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
								  'primary_cost_service','primary_cost_vehicle','primary_cost_cse_office']
			acc_selection_list2 = ['security_deposit','itds','sundry_deposit','st_input','excise_input']
			srch_tmp = self.pool.get('cash.payment').search(cr,uid,[('id','=',i.cash_payment_id.id)])
			for j in self.pool.get('cash.payment').browse(cr,uid,srch_tmp):	
				search_line =  self.pool.get('cash.payment.line').search(cr,uid,[('cash_payment_id','=',j.id)])
				for t in self.pool.get('cash.payment.line').browse(cr,uid,search_line):
					if t.account_id.account_selection in acc_selection_list:
						total += t.debit_amount
		for res in self.browse(cr,uid,ids):
			acc_selection = res.account_id.account_selection
			code = res.account_id.code
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			res_id = res.id
			if 'Sundry Creditors' in res.account_id.name and res.type=='debit':
				self.show_expense_details(cr,uid,ids,context=context)
				objt = 'gst_accounting'
				view_name2 = 'expense_payment_form'
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
							'res_model': 'cash.payment.line',
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
					view_name2 = 'freight_entry_form'
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
						'res_model': 'cash.payment.line',
						'target' : 'new',
						'res_id': int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								  (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True
					}
			if acc_selection == 'expenses':
				objt = 'gst_accounting'
				view_name2 = 'expense_cash_form'
				name_wizard = "Add Expenses Details"
				models_data = self.pool.get('ir.model.data')
				form_view = models_data.get_object_reference(cr, uid, objt, view_name2)
				return {
						'name': (name_wizard),
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'cash.payment.line',
						'target' : 'new',
						'res_id': int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								  (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True
					}
			if acc_selection in acc_selection_list:
				if acc_selection == 'primary_cost_cse':
					view_name = 'account_cash_primary_cost_form'
					objt = 'account_sales_branch'
				if acc_selection == 'primary_cost_office': 
					view_name = 'account_cash_primary_cost_office_form'
					objt = 'account_sales_branch'
				if acc_selection == 'primary_cost_phone':
					view_name = 'account_cash_primary_cost_phone_form'
					objt = 'account_sales_branch'
				if acc_selection == 'primary_cost_vehicle':
					view_name = 'account_cash_primary_cost_vehicle_form'
					objt = 'account_sales_branch'
				if acc_selection == 'primary_cost_service':
					view_name = 'account_primary_cost_cash_service_form'
					objt = 'account_sales_branch'
				if acc_selection == 'primary_cost_cse_office':
					view_name = 'account_primary_cost_cse_office_form'
					objt = 'account_sales_branch'
				models_data = self.pool.get('ir.model.data')
				form_view = models_data.get_object_reference(cr, uid, objt, view_name)
				return {
					'name': ("Add Primary Cost Category"),
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'cash.payment.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					}
			if acc_selection in acc_selection_list2:
				if acc_selection == 'security_deposit':
					if  res.type =='debit': 
						view_name2 = 'cash_payment_security_deposit_form'
						objt = 'account_sales_branch'
						name_wizard = "Add Security Deposit"
					else:
						raise osv.except_osv(('Alert'),('No Information'))
				if acc_selection == 'itds': 
					view_name2 = 'account_cash_itds_form'
					objt = 'account_sales_branch'
					name_wizard = "Add ITDS on Contract Payments Details"
				if acc_selection == 'sundry_deposit':
					if res.type =='debit':
						view_name2 = 'account_cash_sundry_dposit_form'
						objt = 'account_sales_branch'
						name_wizard = "Add Sundry Deposit"
					else:
						raise osv.except_osv(('Alert'),('No Information')) 
				if acc_selection == 'st_input':
					if code == False:
						view_name2 = 'account_cash_st_input_form'
						objt = 'account_sales_branch'
						name_wizard = "Add ST Input Details"
					elif code in ('igst','cgst'):
						if code == 'igst':
							view_name2 = 'account_cash_st_input_form_igst_inherit'
							objt = 'gst_accounting'
							name_wizard = "Add ST Input Details"
						if code == 'cgst':
							view_name2 = 'account_cash_st_input_form_cgst_inherit'
							objt = 'gst_accounting'
							name_wizard = "Add ST Input Details"
					else:
						raise osv.except_osv(('Alert'),('No Information!'))
				if res.account_id.account_selection == 'excise_input':                                                
					view_name2 = 'account_cash_excise_input_form'
					objt = 'account_sales_branch'
					name_wizard = "Add Excise Input Details"
				models_data = self.pool.get('ir.model.data')
				form_view = models_data.get_object_reference(cr, uid, objt, view_name2)
				return {
						'name': (name_wizard),
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'cash.payment.line',
						'target' : 'new',
						'res_id': int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								  (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True
					}
			else:
				raise osv.except_osv(('Alert'),('No Information'))


	def save_input_cash_gst(self, cr, uid, ids, context=None):
		total_amount = 0.0
		bill_no=[]
		bill_date=[]
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		for rec in self.browse(cr,uid,ids):
			if rec.cash_st_input_cgst_ids == [] and rec.cash_st_input_igst_ids == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.cash_st_input_cgst_ids:
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
			for line in rec.cash_st_input_igst_ids:
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
				raise osv.except_osv(('Alert'),('You cannot add different bill nos and its Input details!'))
		if bill_date!=[]:
			bill_date=list(set(bill_date))
			if len(bill_date)>1:
				raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
		return {'type': 'ir.actions.act_window_close'}

	def save_freight_entry(self, cr, uid, ids, context=None):
		amount = 0.0
		total_amount = 0.0
		freight_tax_amount = 0.0
		igst_check=False
		bill_no=[]
		bill_date=[]
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		for rec in self.browse(cr,uid,ids):
			if rec.freight_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.freight_one2many:
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
			if rec.cash_expense_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.cash_expense_one2many:
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
					self.pool.get('expense.payment').write(cr,uid,line.id,{
						'total_amount':round(amount,2),
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

cash_payment_line()


class st_input(osv.osv):
	_inherit = 'st.input'
	_rec_name='bill_no'

	_columns = {
		'cash_payment_line_igst_id':fields.many2one('cash.payment.line','Cash Payment line'),
		'cash_payment_line_cgst_id':fields.many2one('cash.payment.line','Cash Payment line'),
		'bill_value':fields.float('Bill Value'),
		'freight_id':fields.many2one('cash.payment.line','Freight Entry'),
		# 'gst_input_rate': fields.selection([('0','0.00%'),('5','5.00%'),('12','12.00%'),('18','18.00%'),('28','28.00%')],'Rate'),
		'gst_input_rate':fields.many2one('gst.rate.master','Rate'),
		'freight_input_rate':fields.float('Rate', size=20),
		'igst_tax_amount': fields.float('Tax Amount',size=1000),
		'freight_tax_amount': fields.float('Tax Amount',size=1000),
		'cgst_tax_amount': fields.float('Tax Amount',size=1000),
		'sgst_tax_amount': fields.float('Tax Amount',size=1000),
		'igst_tax_amount': fields.float('Tax Amount',size=1000),
		'from_state':fields.many2one('state.name','From(Place Of Dispatch)'),
		'to_state':fields.many2one('state.name','To(Place of Destination)'),
		'input_type': fields.selection([('input_service','Input Service'),
										('input_credit','Input Credit'),
										('capital_goods','Capital Goods')],'Input Type'),
		'igst_check':fields.boolean('IGST Check'),
	}

	_defaults = {
		# 'freight_input_rate':5.0,
	}

	def onchange_freight_input_rate(self, cr, uid, ids, from_state,to_state, igst_check, bill_value, freight_input_rate, context=None):
		data = {}
		divided_tax_amount=0.0
		total_amount=0.0
		igst_amount=0.0
		if bill_value and freight_input_rate>=0.0:
			# if igst_check==False:
			freight_tax_amount = (bill_value * float(freight_input_rate))/100
			divided_tax_amount = freight_tax_amount/2
			total_amount = bill_value+freight_tax_amount
			if from_state!=to_state:
				divided_tax_amount=0.0
				igst_amount=freight_tax_amount
			round_amount=round(total_amount)
			difference=round((round_amount-total_amount),2)
			data.update(
				{
					'cgst_tax_amount': divided_tax_amount,
					'sgst_tax_amount': divided_tax_amount,
					'igst_tax_amount': igst_amount,
					'total_amount': total_amount,
					'round_off': difference,
				})
		else:
			data.update(
				{
					'cgst_tax_amount': 0.00,
					'sgst_tax_amount': 0.00,
					'igst_tax_amount': 0.00,
					'total_amount': 0.00,
					'round_off': 0.00,
				})
		return {'value':data}

	def onchange_igst_input_rate(self, cr, uid, ids, bill_value, gst_input_rate, context=None):
		data = {}
		if bill_value and gst_input_rate:
			rate=self.pool.get('gst.rate.master').browse(cr,uid,gst_input_rate).rate
			print rate
			igst_tax_amount = (bill_value * rate)/100
			total_amount = bill_value+igst_tax_amount
			round_amount=round(total_amount)
			difference=round((round_amount-total_amount),2)
			data.update(
				{
					'igst_tax_amount': igst_tax_amount,
					'total_amount': total_amount,
					'round_off': difference,
				})
		else:
			data.update(
				{
					'igst_tax_amount': 0.00,
					'total_amount': 0.00,
					'round_off': 0.00,
				})
		return {'value':data}


	def onchange_cgst_input_rate(self, cr, uid, ids, bill_value, gst_input_rate, context=None):
		data = {}
		if bill_value and gst_input_rate:
			rate=self.pool.get('gst.rate.master').browse(cr,uid,gst_input_rate).rate
			tax_amount = (bill_value * rate)/100
			divided_tax_amount = tax_amount/2
			total_amount = bill_value+tax_amount
			round_amount=round(total_amount)
			difference=round((round_amount-total_amount),2)
			data.update(
				{
					'cgst_tax_amount': divided_tax_amount,
					'sgst_tax_amount': divided_tax_amount,
					'total_amount': total_amount,
					'round_off': difference,
				})
		else:
			data.update(
				{
					'cgst_tax_amount': 0.00,
					'sgst_tax_amount': 0.00,
					'total_amount': 0.00,
					'round_off': 0.00,
				})
		return {'value':data}

st_input()


class expense_payment(osv.osv):
	_name = 'expense.payment'
	_rec_name='bill_no'

	_columns = {
		'customer_name':fields.many2one('res.partner','Supplier'),
		'cash_payment_expense_id':fields.many2one('cash.payment.line','Cash Payment line'),
		'bank_payment_expense_id':fields.many2one('payment.line','Bank Payment line'),
		'other_payment_expense_id':fields.many2one('other.payment.line','Other Payment line'),
		'bill_no':fields.char('Bill No',size=16),
		'bill_value':fields.float('Bill Value'),
		'bill_date':fields.date('Bill Date'),
		'gst_item_master':fields.many2one('gst.item.master','Item'),	
		'rate':fields.float('Rate'),	
		'tax_amount': fields.float('Tax Amount',size=1000),
		'total_amount': fields.float('Total Amount',size=1000),
		'hsn_sac_code': fields.char('HSN/SAC Code',size=1000),
	}

expense_payment()

class sundry_expenses(osv.osv):
	_name = 'sundry.expenses'

	_columns = {
		'cash_sundry_expense_id':fields.many2one('cash.payment.line','Cash Payment Line'),
		'check_exp':fields.boolean(''),
		'customer_name':fields.many2one('res.partner','Supplier'),
		'name':fields.char('Voucher No',size=1000),
		'purchase_id':fields.many2one('account.purchase.receipts','purchase id'),
		'bill_value':fields.float('Bill Value'),
		'bill_date':fields.date('Bill Date'),
		'bill_no':fields.char('Bill No',size=16),
	}

sundry_expenses()
