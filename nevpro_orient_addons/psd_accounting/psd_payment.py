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


class account_payment(osv.osv):
	_inherit = 'account.payment'
	_columns = {
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'psd_accounting': fields.boolean('PSD Accounting')
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(account_payment, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	def onchange_payment_date(self, cr, uid, ids, payment_date, context=None):
		v = {}
		if payment_date:
			today_date = datetime.now().date()			
			py_date = str(today_date + relativedelta(days=-5))
			if payment_date < str(py_date) or payment_date > str(today_date):
				raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
		return {'value':v}

	def psd_account_type(self, cr, uid, ids, account_id, context=None):
		v = {}
		if account_id:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in ("iob_one","iob_two"):
						v['type'] = 'credit'
					else:
						v['type'] = ''
		return {'value':v}

	def onchange_type(self, cr, uid, ids, account_id, type, context=None):
		v = {}
		if account_id and type:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in ('iob_one','iob_two') and type == 'debit':
						raise osv.except_osv(('Alert'),('Bank A/c cannot be debited.'))
		return {'value':v}

	def psd_add_info(self, cr, uid, ids, context=None): # Bank Payment
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
			
			if res.account_id.account_selection in ('iob_one','iob_two'):
				if res.type=='debit':
					raise osv.except_osv(('Alert'),('Bank A/c cannot be debited.'))

			account_id1=res.account_id
			#for i in res.payment_one2many:                          #remove duplicate as per vijay requirement. on 1 dec
			#	if account_id1.id==i.account_id.id:
			#		raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
			

			self.write(cr,uid,res.id,{'account_id':None,'type':''})
			total= total_amount=auto_credit_total=0.0
			auto_credit_cal=auto_debit_cal=auto_credit_total=auto_debit_total=0.0
			account_selection = res.account_id.account_selection
			acc_selection_list = ['primary_cost_phone', 'primary_cost_cse','primary_cost_office',
								  'primary_cost_vehicle','primary_cost_service','primary_cost_cse_office']
			
			if account_selection in ('st_input','excise_input'):
				for t in res.payment_one2many:
					if t.account_id.account_selection in acc_selection_list :
						total += t.debit_amount
				
				search_tax_id = [] ###To Remove Hard Code Service Tax 
				service_tax = ed_cess = hs_cess = 0.0
				
			if account_selection in ('iob_one','cash','iob_two'):
				if res.type=='debit':
					for j in res.payment_one2many:
						if j.type=='credit':
							total_amount += j.credit_amount
						if j.type=='debit':
							auto_credit_total += j.debit_amount
					if total_amount>auto_credit_total:
						total_amount -= auto_credit_total
					else:		
						total_amount=0.0
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

			if acc_id:
				self.pool.get('payment.line').create(cr,uid,{'payment_id':res.id,
										'debit_amount':total_amount,
										'credit_amount':auto_credit_cal,
										'account_id':acc_id,
										'type':res.type,
										'customer_name':res.customer_name.id if res.customer_name.id else '',
										})

		return True

	def psd_account_payment_process(self, cr, uid, ids, context=None):#Bank Payment Process Button
		cr_total = dr_total = total = iob_total = service_total = itds_total = cheque_amount = 0.0
		dd_amount = neft_amount = total_sundry_deposit = chk_account_selection = 0.0###23de15
		move = service_cost = iob_two_id = itds_id = primary_cost_id=payment_date = ''
		post = []
		line_acc = []
		iob_one_payment_id = neft_payment_id = demand_draft_payment_id = emp_name= ''
		today_date = datetime.now().date()
		py_date = bank_charges_bool = bank_charge_flag=False
		models_data=self.pool.get('ir.model.data')
		count=0
		for res1 in self.browse(cr,uid,ids):
			if res1.payment_date:
				py_date = str(today_date + relativedelta(days=-5))
				if res1.payment_date < str(py_date) or res1.payment_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
				payment_date=res1.payment_date
			else:
				payment_date=datetime.now().date()
			for line in res1.payment_one2many:
				line_acc.append(line.account_id.account_selection)
				if line.credit_amount:
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				if line.debit_amount:
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

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
			
			if not 'iob_two' in line_acc:
				raise osv.except_osv(('Alert'),('Payment entry cannot be processed if I.O.B A/C IV ledger is not selected.'))		
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
			for bank_line in res.payment_one2many:
				wizard_id = bank_line.wizard_id
				acc_selection = bank_line.account_id.account_selection
				account_name = bank_line.account_id.name
				credit_amount = bank_line.credit_amount
				debit_amount = bank_line.debit_amount
				acc_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
								  'primary_cost_service','primary_cost_vehicle','primary_cost_cse_office','sundry_deposit']
		
				if wizard_id == 0:
					self.wizard_id_write(cr,uid,ids,context=context)
					
				if acc_selection == 'security_deposit': # HHH 9may
					for sec_dep_line in bank_line.security_deposit_one2many:
						self.pool.get('security.deposit').write(cr,uid,sec_dep_line.id,{
							'security_check_against':True,
							'customer_name':bank_line.customer_name.id if bank_line.customer_name.id else '' ,
							'customer_name_char':res.customer_name.name if res.customer_name.name else '' ,
							})
						
				if acc_selection == 'sundry_deposit': # HHH 20may
					for sun_dep_line in bank_line.sundry_deposit_line:
						self.pool.get('sundry.deposit').write(cr,uid,sun_dep_line.id,{
							'sundry_check':True,
							'customer_name':bank_line.customer_name.id if bank_line.customer_name.id else '' ,
							'customer_name_char':res.customer_name.name if res.customer_name.name else '' ,
							})
						
				if acc_selection == 'st_input':
					st_date = ''
					st_total = 0.0
					for cse_line in bank_line.st_input_one2many:
						st_date=cse_line.bill_date
						st_total +=  cse_line.total_amount
						
					if not st_date:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

				if acc_selection == 'excise_input':
					st_date = ''
					st_total = 0.0
					for ex_line in bank_line.excise_input_one2many:
						st_date=ex_line.bill_date
						st_total += ex_line.total_amount
						
					if not st_date:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))


				elif acc_selection == 'iob_one':
					for iob_one_line in bank_line.iob_one_payment_one2many:
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


					for demand_draft_line in bank_line.demand_draft_payment_one2many:
						demand_draft_payment_id = demand_draft_line.demand_draft_payment_id.id
						dd_no = demand_draft_line.dd_no
						dd_amount +=  demand_draft_line.dd_amount
						for n in str(demand_draft_line.dd_no):
							p = re.compile('([0-9]{9}$)')
							if p.match(demand_draft_line.dd_no)== None :
								self.pool.get('demand.draft.sales.receipts').create(cr,uid,{'dd_no':''})
								raise osv.except_osv(('Alert!'),('Please Enter 9 digit Cheque Number.'))

							if not demand_draft_line.dd_amount:
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

					for neft_line in bank_line.neft_payment_one2many:
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

#------------------------------------------------------------------------------------------------------------------------
		for rec in self.browse(cr,uid,ids):
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_payment_form')
			tree_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_payment_tree')
			
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
			if pcof_key and bank_payment_id:
				cr.execute("select cast(count(id) as integer) from account_payment where payment_no is not null   and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + bank_payment_id +  str(year1) +str(seq).zfill(6)
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
			
			for i in rec.payment_one2many:
				search_temp=self.pool.get('st.input').search(cr,uid,[('payment_line_input_id','=',i.id)])
				for j in self.pool.get('st.input').browse(cr,uid,search_temp):
					self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
				search_temp1=self.pool.get('st.input').search(cr,uid,[('payment_line_excise_id','=',i.id)])
				for k in self.pool.get('st.input').browse(cr,uid,search_temp1):
					self.pool.get('st.input').write(cr,uid,k.id,{'account_id':i.account_id.id})
					
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


		return {
			'name':'Bank Payment - A/c IV',
			'view_mode': 'tree,form',
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
	_inherit = 'payment.line'

	# def add(self, cr, uid, ids, context=None): # Bank Payment line (arrow add button)
	# 	total= total_amount= service_tax = ed_cess = hs_cess=0.0
	# 	temp=[]
	# 	bank_charges_bool=True
	# 	account_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
	# 							  'primary_cost_vehicle','primary_cost_service', 'primary_cost_cse_office']
		
	# 	acc_selection_list2 = ['security_deposit','itds','sundry_deposit','st_input','excise_input','iob_two','iob_one']
		
	# 	for i in self.browse(cr,uid,ids):#For st-input  and Excise input
	# 		srch_tmp = self.pool.get('account.payment').search(cr,uid,[('id','=',i.payment_id.id)])
	# 		for j in self.pool.get('account.payment').browse(cr,uid,srch_tmp):
	# 			search_line =  self.pool.get('payment.line').search(cr,uid,[('payment_id','=',j.id)])
	# 			for t in self.pool.get('payment.line').browse(cr,uid,search_line):
	# 				if t.account_id.account_selection in account_selection_list:
	# 					total += t.debit_amount
	
	# 	for res in self.browse(cr,uid,ids):
	# 		res_id = res.id
	# 		credit_amount = res.credit_amount
	# 		debit_amount = res.debit_amount
	# 		acc_id = res.account_id
	# 		acc_selection = acc_id.account_selection

	# 		for i in self.pool.get('account.payment').browse(cr,uid,[res.payment_id.id]):
	# 			if i.payment_one2many:
	# 				for j in i.payment_one2many:
	# 					if j.account_id.bank_charges_bool==True:
	# 						bank_charges_bool=False

	# 		if not acc_id.name:
	# 			raise osv.except_osv(('Alert'),('Please Select Account.'))
			
	# 		if acc_selection in acc_selection_list2:
	# 			if acc_selection in ('st_input','excise_input'):
	# 				search_tax_id = [] ###To Remove Hard Code Service Tax 
	# 				for exc_input in self.pool.get('account.account').search(cr,uid,[('id','=',res.account_id.id)]):
	# 					cr.execute('select tax_id from account_account_tax_default_rel where account_id = %s',(exc_input,))
	# 				if acc_selection == 'st_input':
	# 					view_name =  'st_input_form'
	# 					name_wizard =  "Add ST Input Details"
	
	# 				if acc_selection == 'excise_input':
	# 					view_name =  'excise_input_form'
	# 					name_wizard =  "Add Excise Input Details"
						
	# 			if acc_selection == 'iob_two':
	# 					view_name =   'account_iob_two_form'
	# 					name_wizard = "Add"+" "+ acc_id.name +" "+" Details"
	
	# 			if acc_selection == 'iob_one':
	# 				if acc_id.ho_bank_wizard_check == True:
	# 					view_name =   'account_iob_one_payment_form'
	# 					name_wizard =  "Add"+" "+ acc_id.name +" "+"Details"
	# 				else:
	# 					return True
	
	# 			if acc_selection == 'itds':
	# 				view_name =  'account_itds_form'
	# 				name_wizard = "Add ITDS on Contract Payments Details"
					
	# 			if acc_selection == 'sundry_deposit':
	# 				view_name ='account_sundry_dposit_form'
	# 				name_wizard = "Add Sundry Deposit Details"

	# 			if acc_selection == 'security_deposit' and res.type =='debit': ###security deposit sagar >>>18 Feb 2016
	# 				view_name = 'bank_payment_security_deposit_form'
	# 				name_wizard = "Add Sundry Deposit Details"
					
	# 			models_data=self.pool.get('ir.model.data')
	# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name)
	# 			return {
	# 				'name': (name_wizard),'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'payment.line',
	# 				'target' : 'new',
	# 				'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 				   }
			
	# 		if acc_selection in account_selection_list:
	# 			if acc_id.account_selection == 'primary_cost_cse':
	# 				view_name2 = 'account_primary_cost_form'
	# 				self.write(cr,uid,res_id,{'wizard_id':res_id})
					
	# 			elif acc_selection == 'primary_cost_service':
	# 				view_name2 =  'account_primary_cost_service_form'
	
	# 			elif acc_selection == 'primary_cost_office':
	# 				view_name2 =  'account_bank_primary_cost_office_form'
	
	# 			elif acc_selection == 'primary_cost_phone':
	# 				view_name2 = 'account_bank_primary_cost_phone_form'
	
	# 			elif acc_selection == 'primary_cost_vehicle':
	# 				view_name2 ='account_bank_primary_cost_vehicle_form'
	
	# 			elif acc_selection == 'primary_cost_cse_office':
	# 				view_name2 = 'account_primary_bank_cost_cse_office_form'
	
	# 			models_data=self.pool.get('ir.model.data')
	# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name2)
	# 			return {
	# 				'name': ("Add Primary Cost Category Details"),'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'payment.line',
	# 				'res_id':int(res_id),
	# 				'target' : 'new',
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 			}
	# 		else:
	# 			raise osv.except_osv(('Alert'),('No Information '))

	def psd_add(self, cr, uid, ids, context=None): # Bank Payment line (arrow add button)
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
				acc_selection = acc_id.account_selection

				for i in self.pool.get('account.payment').browse(cr,uid,[res.payment_id.id]):
					if i.payment_one2many:
						for j in i.payment_one2many:
							if j.account_id.bank_charges_bool==True:
								bank_charges_bool=False

				if not acc_id.name:
					raise osv.except_osv(('Alert'),('Please Select Account.'))
				
				if acc_selection in acc_selection_list2:
					if acc_selection in ('st_input','excise_input'):
						search_tax_id = [] ###To Remove Hard Code Service Tax 
						for exc_input in self.pool.get('account.account').search(cr,uid,[('id','=',res.account_id.id)]):
							cr.execute('select tax_id from account_account_tax_default_rel where account_id = %s',(exc_input,))
						if acc_selection == 'st_input':
							view_name =  'psd_st_input_form'
							name_wizard =  "Add ST Input Details"
		
						if acc_selection == 'excise_input':
							view_name =  'psd_excise_input_form'
							name_wizard =  "Add Excise Input Details"
							
					if acc_selection == 'iob_two':
							view_name =   'psd_account_iob_two_form'
							name_wizard = "Add"+" "+ acc_id.name +" "+" Details"
		
					if acc_selection == 'iob_one':
						if acc_id.ho_bank_wizard_check == True:
							view_name =   'psd_account_iob_one_payment_form'
							name_wizard =  "Add"+" "+ acc_id.name +" "+"Details"
						else:
							return True
		
					if acc_selection == 'itds':
						view_name =  'psd_account_itds_form'
						name_wizard = "Add ITDS on Contract Payments Details"
						
					if acc_selection == 'sundry_deposit':
						view_name ='psd_account_sundry_dposit_form'
						name_wizard = "Add Sundry Deposit Details"

					if acc_selection == 'security_deposit' and res.type =='debit': ###security deposit sagar >>>18 Feb 2016
						view_name = 'psd_bank_payment_security_deposit_form'
						name_wizard = "Add Sundry Deposit Details"
						
					models_data=self.pool.get('ir.model.data')
					form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name)
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
						view_name2 = 'psd_account_primary_cost_form'
						self.write(cr,uid,res_id,{'wizard_id':res_id})
						
					elif acc_selection == 'primary_cost_service':
						view_name2 =  'psd_account_primary_cost_service_form'
		
					elif acc_selection == 'primary_cost_office':
						view_name2 =  'psd_account_bank_primary_cost_office_form'
		
					elif acc_selection == 'primary_cost_phone':
						view_name2 = 'psd_account_bank_primary_cost_phone_form'
		
					elif acc_selection == 'primary_cost_vehicle':
						view_name2 ='psd_account_bank_primary_cost_vehicle_form'
		
					elif acc_selection == 'primary_cost_cse_office':
						view_name2 = 'psd_account_primary_bank_cost_cse_office_form'
		
					models_data=self.pool.get('ir.model.data')
					form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name2)
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
payment_line()

class bank_payment_one(osv.osv):
	_inherit = 'bank.payment.one'
	_columns = {
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'psd_accounting': fields.boolean('PSD Accounting')
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(bank_payment_one, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	def onchange_payment_date(self, cr, uid, ids, payment_date, context=None):
		v = {}
		if payment_date:
			today_date = datetime.now().date()			
			py_date = str(today_date + relativedelta(days=-5))
			if payment_date < str(py_date) or payment_date > str(today_date):
				raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
		return {'value':v}

	def onchange_type(self, cr, uid, ids, account_id, type, context=None):
		v = {}
		if account_id and type:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in ('iob_one','iob_two') and type == 'debit':
						raise osv.except_osv(('Alert'),('Bank A/c cannot be debited.'))
		return {'value':v}

	def _get_account_info(self, cr, uid, ids, context=None):
		total = 0.0
		for res in self.browse(cr,uid,ids):
			flag = True
			for line in res.payment_one2many:
				if flag == True:
					flag = False
					cr.execute("update bank_payment_one set particulars = %s where id=%s",(line.account_id.id,res.id))
				if line.type == 'debit':
					account_id = line.account_id.id
					total = total + line.debit_amount
					cr.execute("update bank_payment_one set debit_amount_srch = %s where id=%s",(total,res.id))

		return True

	_constraints = [(_get_account_info, '', ['id'])]
	
	
	def psd_account_type(self, cr, uid, ids, account_id, context=None):
		v = {}
		if account_id:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection == 'cash':
						v['type'] = 'credit'
					elif acc.account_selection == 'iob_one':
						v['type'] = 'credit'
					elif acc.account_selection == 'iob_two':
						v['type'] = 'credit'
					elif acc.account_selection == '':
							v['type'] = ''
					else:
							v['type'] = ''
		return {'value':v}

	def psd_add_cust(self, cr, uid, ids, context=None): # Bank Payment
		for res in self.browse(cr,uid,ids):
			state = res.state
			acc_id = res.account_id.id
			types = res.type
			if state == 'draft':
				if not acc_id:
					raise osv.except_osv(('Alert'),('Plaese select Account Name.'))
				if not types:
					raise osv.except_osv(('Alert'),('Plaese select Type.'))

			if res.account_id.account_selection  == 'iob_one':
				if res.type=='debit':
					raise osv.except_osv(('Alert'),('Bank A/c cannot be debited.'))

			for line in res.payment_one2many:
				if line.account_id.account_selection == 'ho_remmitance' or line.account_id.account_selection == 'others' or line.account_id.account_selection == 'bank_charges' :
			
					if res.account_id.account_selection == 'iob_two':
						raise osv.except_osv(('Alert'),('Please select proper account name.'))

				#else:
					#if res.account_id.account_selection == 'iob_one' and res.account_id.receive_bank_no == 'bank_two':
						#raise osv.except_osv(('Alert'),('Please select proper account name.'))

			if res.account_id.account_selection == 'cash':
				raise osv.except_osv(('Alert'),('Please select proper account name.'))
			#if res.account_id.receive_bank_no =='bank_two':
					#raise osv.except_osv(('Alert'),('Select receive bank two'))
			
			account_id1=res.account_id
			for i in res.payment_one2many:
				if account_id1.id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))


			self.write(cr,uid,res.id,{'account_id':None,'type':''})
			total=0.0
			total_amount=0.0
			auto_credit_cal=auto_debit_cal=auto_credit_total=auto_debit_total=0.0
			auto_credit_total=0.0
			if  res.account_id.account_selection == 'iob_one' or res.account_id.account_selection == 'cash' or res.account_id.account_selection == 'iob_two':
				if res.type=='debit':
					for j in res.payment_one2many:
						if j.type=='credit':
							total_amount=total_amount+j.credit_amount
						if j.type=='debit':
							auto_credit_total=auto_credit_total+j.debit_amount
					if total_amount>auto_credit_total:
						total_amount=total_amount-auto_credit_total	
					else:		
						total_amount=0.0
				else:	
					for k in res.payment_one2many:
						if k.type=='credit':
							auto_debit_cal=auto_debit_cal+k.credit_amount
						if k.type=='debit':
							auto_credit_cal=auto_credit_cal+k.debit_amount
					if auto_debit_cal<auto_credit_cal:
						auto_credit_cal=auto_credit_cal-auto_debit_cal
					else:
						auto_credit_cal=0.0

			if acc_id:
				self.pool.get('bank.payment.one.line').create(cr,uid,{'payment_one_id':res.id,
											'debit_amount':total_amount,
											'credit_amount':auto_credit_cal,
											'account_id':acc_id,
											'type':res.type,
			})

		return True

	def psd_customer_name_change(self, cr, uid, ids, customer_name, context=None):
		v = {}
		if customer_name:
			srch = self.pool.get('res.partner').search(cr,uid,[('id','=',customer_name)])
			if srch:
				for partner in self.pool.get('res.partner').browse(cr,uid,srch):
					ou_id = partner.ou_id
				v['customer_id'] = ou_id
				v['customer_id_invisible'] = ou_id
		if not	customer_name:
			v['customer_id']=None
			v['customer_id_invisible'] = None
			
		return {'value':v}


	def wizard_id_write(self, cr, uid, ids,  context=None):
		for res in self.browse(cr,uid,ids):
			for line in res.payment_one2many:
				cr.execute("update bank_payment_one_line set wizard_id = %s where id=%s",(line.id,res.id))
				#self.pool.get('bank.payment.one.line').write(cr,uid,line.id,{'wizard_id':line.id})
		return True


	def _get_company(self, cr, uid, context=None):
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id


	def delete_draft_records(self, cr, uid, ids, context=None): # Delete the records which are in 'Draft' State
		
		srch_state = self.pool.get('bank.payment.one').search(cr,uid,[('state','=','draft')])
		if srch_state:
			for res in self.pool.get('bank.payment.one').browse(cr,uid,srch_state):
				state = res.state
				form_id = res.id

				srch_line = self.pool.get('bank.payment.one.line').search(cr,uid,[('payment_one_id','=',form_id)])
				if srch_line:
					for line in self.pool.get('bank.payment.one.line').browse(cr,uid,srch_line):
						line_id = line.id

						srch_iob_two = self.pool.get('iob.two.payment').search(cr,uid,[('bank_payment_one_id','=',line_id)])
						if srch_iob_two: # IOB A/c II
							for iob_two in self.pool.get('iob.two.payment').browse(cr,uid,srch_iob_two):
								cr.execute('delete from labour_contractor_itds where id=%(val)s',{'val':iob_two.id})

						srch_iob_one = self.pool.get('iob.one.sales.receipts').search(cr,uid,[('iob_one_payment_id2','=',line_id)])
						if srch_iob_one: # IOB A/c I
							for iob_one in self.pool.get('iob.one.sales.receipts').browse(cr,uid,srch_iob_one):
								cr.execute('delete from iob_one_sales_receipts where id=%(val)s',{'val':iob_one.id})

						srch_neft = self.pool.get('neft.sales.receipts').search(cr,uid,[('neft_bank_payment_one_id','=',line_id)])
						if srch_neft: # NEFT
							for neft_line in self.pool.get('neft.sales.receipts').browse(cr,uid,srch_neft):
								cr.execute('delete from neft_sales_receipts where id=%(val)s',{'val':neft_line.id})

						cr.execute('delete from bank_payment_one_line where id=%(val)s',{'val':line_id})
				cr.execute('delete from bank_payment_one where id=%(val)s',{'val':form_id})
		return True


	def psd_process(self, cr, uid, ids, context=None):#Bank Payment Process Button
		cr_total = 0.0
		dr_total = 0.0
		move = ''
		post = []
		line_acc = []
		service_cost = ''
		bank_payment_one_id = ''
		itds_id = ''
		primary_cost_id=payment_date = ''
		total = 0.0
		iob_total = 0.0
		service_total = 0.0
		itds_total = 0.0
		iob_one_payment_id2 = ''
		neft_bank_payment_one_id = ''
		cheque_amount = 0.0
		neft_amount = 0.0
		total_sundry_deposit = 0.0
		chk_account_selection=0.0###23de15
		emp_name= ''
		today_date = datetime.now().date()
		py_date = False
		ho_remmitance=True
		bank_charges_bool=False
		bank_charges_flag= False
		models_data=self.pool.get('ir.model.data')
		for res1 in self.browse(cr,uid,ids):
			for line in res1.payment_one2many:
				line_acc.append(line.account_id.account_selection)
		if not 'iob_one' in line_acc:
			raise osv.except_osv(('Alert'),('Payment entry cannot be processed if I.O.B A/C III ledger is not selected.'))
		for res1 in self.browse(cr,uid,ids):
			if res1.payment_date:
				py_date = str(today_date + relativedelta(days=-5))
				if res1.payment_date < str(py_date) or res1.payment_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
				payment_date=res1.payment_date
			else:
				payment_date=datetime.now().date()
			for line in res1.payment_one2many:
				if line.credit_amount:
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				if line.debit_amount:
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				cr_amount = line.credit_amount
				dr_amount = line.debit_amount

				dr_total = dr_total + dr_amount
				cr_total = cr_total + cr_amount

				account_id = line.account_id.id
				temp = tuple([account_id])
				post.append(temp)
				for i in range(0,len(post)):	
					for j in range(i+1,len(post)):
						if post[i][0]==post[j][0]:
							raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
			
			###########################################################################################################23dec15
				acc_selection = line.account_id.account_selection
				
				if acc_selection in ['iob_one','iob_two']:
					
					chk_account_selection +=1
					
			if chk_account_selection ==0.0:
					raise osv.except_osv(('Alert'),('Please select proper account name')) 
					
			###########################################################################################################23dec15
			
			self.write(cr,uid,ids,{'debit_amount_srch':dr_total})
			if dr_total != cr_total:
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
# >>>>>>>>>>>>for bank charge				
		count = 0
		acc_selection_list = ['iob_one','iob_two']        
		for res in self.browse(cr,uid,ids):
			if res.payment_one2many:
				for j in res.payment_one2many:
					if j.debit_amount:
						count+=1
					if j.account_id.bank_charges_bool==True:
						bank_charges_bool=True
						bank_charges_flag=True
						
		if count >= 2 and bank_charges_bool==True:
				bank_charges_flag=False
#<<<<<<<<<<<<<<		
		for res in self.browse(cr,uid,ids):

			if res.payment_one2many:
				for j in res.payment_one2many:
					if j.account_id.account_selection=='ho_remmitance':
						ho_remmitance=False
					if bank_charges_flag == False:
						if j.account_id.account_selection in acc_selection_list:
							if not j.payment_method:
								raise osv.except_osv(('Alert'),(' Enter Bank Details for "%s"') % (j.account_id.name))

			for bank_line in res.payment_one2many:
				wizard_id = bank_line.wizard_id
				acc_selection = bank_line.account_id.account_selection
				account_name = bank_line.account_id.name
		
				credit_amount = bank_line.credit_amount
				debit_amount = bank_line.debit_amount
		
				if wizard_id == 0:
					self.wizard_id_write(cr,uid,ids,context=context)

				if acc_selection == 'iob_one' and not bank_charges_flag: # condition add for bank charge to allow
					for iob_one_line in bank_line.iob_one_payment_one2many:
						iob_one_payment_id2 = iob_one_line.iob_one_payment_id2.id
						cheque_no = iob_one_line.cheque_no
						cheque_amount = cheque_amount + iob_one_line.cheque_amount

						if not iob_one_line.cheque_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not iob_one_line.cheque_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not iob_one_line.drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not iob_one_line.bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))

					for neft_line in bank_line.neft_payment_one2many:
						neft_bank_payment_one_id = neft_line.neft_bank_payment_one_id.id
						neft_amount = neft_amount + neft_line.neft_amount
						if not neft_line.beneficiary_bank_name:
							raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
						if not neft_line.pay_ref_no:
							raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
						if not neft_line.neft_amount:
							raise osv.except_osv(('Alert!'),('Please provide Amount for NEFT/RTGS.'))
						
					if not iob_one_payment_id2:
							if not neft_bank_payment_one_id:
								if ho_remmitance:
									raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if not neft_bank_payment_one_id:
							if iob_one_payment_id2 :
									if debit_amount:
											if cheque_amount != debit_amount:
													raise osv.except_osv(('Alert'),('Debit amount should be equal'))
									if credit_amount:
											if cheque_amount != credit_amount:
													raise osv.except_osv(('Alert'),('credit amount should be equal'))

					if not iob_one_payment_id2:
								if neft_bank_payment_one_id:
									if debit_amount:
											if neft_amount != debit_amount:
													raise osv.except_osv(('Alert'),('Debit amount should be equal'))
									if credit_amount:
											if neft_amount != credit_amount:
													raise osv.except_osv(('Alert'),('credit amount should be equal'))
					self.write(cr,uid,ids,{'voucher_type':'Payment (Bank - A/c-I)'})

				elif acc_selection == 'iob_two':
					for iob_two_line in bank_line.iob_two_one2many:
						bank_payment_one_id = iob_two_line.bank_payment_one_id

					if bank_charges_bool:
						raise osv.except_osv(('Alert'),('Account "%s" can not used against Bank Charges.') % (account_name))
					if not bank_payment_one_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if bank_line.iob_two_one2many:
						for iob_two_ln in bank_line.iob_two_one2many:
							if not iob_two_ln.drawee_bank_name_new:
								raise osv.except_osv(('Alert!'),('Please provide Drawee Bank Name.'))

							if not iob_two_ln.bank_branch_name:
								raise osv.except_osv(('Alert!'),('Please provide Bank Branch Name.'))

							cheque_amount = iob_two_ln.cheque_amount
							iob_total = iob_total + cheque_amount

						if credit_amount:
							if iob_total != credit_amount:
								raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))

						if debit_amount:
							if iob_total != debit_amount:
								raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

					if iob_two_ln.cheque_no:                       
						for n in str(iob_two_ln.cheque_no):
								p = re.compile('([0-9]{6}$)')
								if p.match(iob_two_ln.cheque_no)== None :
										raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))

					self.write(cr,uid,ids,{'voucher_type':'Payment  (Bank)'})


		for rec in self.browse(cr,uid,ids):
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_bank_payment_one_form')
			tree_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_bank_payment_one_tree')

						#########################################abhi##################################
			today_date = datetime.now().date()

			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = ''
			end_year = ''
			pcof_key = ''
			credit_note_id = ''			
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','bank.payment.one')])
			if search:
				seq_start=self.pool.get('ir.sequence').browse(cr,uid,search[0]).number_next

			year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
			month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
			###############--

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
					if comp_id.bank_payment_one_id:
						bank_payment_one_id = comp_id.bank_payment_one_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0	
			if pcof_key and bank_payment_one_id:
				cr.execute("select cast(count(id) as integer) from bank_payment_one where payment_no is not null   and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + bank_payment_one_id +  str(year1) +str(seq).zfill(6)

				########################################################################
   
			self.write(cr,uid,ids,{'payment_no':value_id,'payment_date': payment_date})
			date = payment_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id

			for chk_ln in rec.payment_one2many:   
				if chk_ln.account_id.account_selection == 'ho_remmitance':
					self.write(cr,uid,rec.id,{'ho_remittance_check':True})


				if chk_ln.account_id.account_selection == 'primary_cost_service' and chk_ln.account_id.bank_charges_bool:#a
					self.write(cr,uid,rec.id,{'bank_charges_check':True})

				if chk_ln.account_id.account_selection == 'funds_transferred_ho':
					self.write(cr,uid,rec.id,{'funds_transferred_ho_check':True})
			

			move = self.pool.get('account.move').create(cr,uid,{'journal_id':11,#Journal Hardcoded confirm from PCIL
																'state':'posted',
																'date':date,
																'name':value_id,
																'narration':rec.narration if rec.narration else '',
																'voucher_type':rec.voucher_type,},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.payment_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
														'account_id':ln.account_id.id,
														'debit':ln.debit_amount,
														'name':rec.customer_name.name if rec.customer_name.name else '',
														'journal_id':11,
														'period_id':period_id,
														'date':date,
														'ref':value_id},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
														'account_id':ln.account_id.id,
														'credit':ln.credit_amount,
														'name':rec.customer_name.name if rec.customer_name.name else '',
														'journal_id':11,
														'period_id':period_id,
														'date':date,
														'ref':value_id},context=context)

			self.write(cr,uid,rec.id,{'state':'done'})
			for update in rec.payment_one2many:
				self.pool.get('bank.payment.one.line').write(cr,uid,update.id,{'state':'done'})

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
			for bank_payment_one_line in payment_his.payment_one2many:
				amount=bank_payment_one_line.debit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('payment.history').create(cr,uid,{
						'payment_his_many2one':curr_id,
						'payment_number':value_id,'payment_date':payment_date,
						'particulars':particulars,'payment_type':payment_type,'payment_amount':amount})
		##self.sync_bank_payment(cr,uid,ids,context=context)###due to supplier not synced

		return {
			'name':'Bank Payment',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'bank.payment.one',
			'res_id':res.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
		}
# for cancel bank HO Entry by sagar 27 Nov >>>>
		
		def cancel_Bank_one_entry(self,cr,uid,ids, context=None):
			HO_line=self.pool.get('bank.payment.one.line')
			move_id=self.pool.get('account.move')
			
			for rec in self.browse(cr,uid,ids):
					
					for line in rec.payment_one2many:
							HO_line.write(cr,uid,line.id,{'credit_amount':0.0,'debit_amount':0.0})
							acc_name = line.account_id.account_selection
							if acc_name == 'iob_two':
									cr.execute('update iob_two_payment set cheque_amount=0.0 where bank_payment_one_id=%s'%(line.id))
							if acc_name == 'iob_one':
									if line.iob_one_check:
										var_iob = self.pool.get('iob.one.sales.receipts').search(cr,uid,[('iob_one_payment_id2','=',line.id)])
										for iob_line_id in self.pool.get('iob.one.sales.receipts').browse(cr,uid,var_iob):
											
											if iob_line_id.bank_reco_date:
												raise osv.except_osv(('Alert'),('Reco Date Is Present,Cancellation Not Allowed'))	
											else:
												cr.execute('update iob_one_sales_receipts set cheque_amount=0.0 where iob_one_payment_id2=%s'%(line.id))
									if line.neft_check:
											cr.execute('update neft_sales_receipts set neft_amount=0.0 where neft_bank_payment_one_id=%s'%(line.id))
									if line.demand_draft_check:
											cr.execute('update demand_draft_sales_receipts set dd_amount=0.0 where demand_draft_payment_id2=%s'%(line.id))

					srch=move_id.search(cr,uid,[('name','=',rec.payment_no)])
					cr.execute('update account_move_line set credit=0.0,debit=0.0 where move_id=%s'%(tuple(srch)))			
			cr.execute("update bank_payment_one set debit_amount_srch=0.0,state='cancel' where id =%s"%(rec.id))
		return True

bank_payment_one()


class bank_payment_one_line(osv.osv):
	_inherit = 'bank.payment.one.line'

	def psd_add_creditors(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			if res.creditors_list:
				self.write(cr,uid,res.id,{'creditors_check':True})
		return True

	def psd_change_payment_method(self, cr, uid, ids, payment_method, context=None):
		v = {}
		if payment_method:
			v['neft_check'] = False
			v['iob_one_check'] = False
			v['demand_draft_check'] = False#abhidd

		else:
			v['neft_check'] = False
			v['iob_one_check'] = False
			v['demand_draft_check'] = False#abhidd

		srch_cheque = self.pool.get('iob.one.sales.receipts').search(cr,uid,[('iob_one_payment_id2','=',ids[0])])
		if srch_cheque:
			for cheque in self.pool.get('iob.one.sales.receipts').browse(cr,uid,srch_cheque):
				cr.execute('delete from iob_one_sales_receipts where id=%(val)s',{'val':cheque.id})

		srch_neft = self.pool.get('neft.sales.receipts').search(cr,uid,[('neft_bank_payment_one_id','=',ids[0])])
		if srch_neft:
			for neft in self.pool.get('neft.sales.receipts').browse(cr,uid,srch_neft):
				cr.execute('delete from neft_sales_receipts where id=%(val)s',{'val':neft.id})

				
		###########################################abhidd###############################start#########
		srch_dd = self.pool.get('demand.draft.sales.receipts').search(cr,uid,[('demand_draft_id','=',ids[0])])
		if srch_dd:
			for neft in self.pool.get('demand.draft.sales.receiptss').browse(cr,uid,srch_dd):
				cr.execute('delete from demand_draft_sales_receipts where id=%(val)s',{'val':neft.id})
		############################################abhidd############################end#############			
			

		return {'value':v}


	def psd_add_payment_method(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			payment_method = res.payment_method
			if not payment_method:
				raise osv.except_osv(('Alert!'),('Please select Bank Payment Method.'))
			if payment_method == 'cheque':
				self.write(cr,uid,res.id,{'neft_check':False,'iob_one_check':True,'demand_draft_check':False})
			elif payment_method == 'neft':
				self.write(cr,uid,res.id,{'neft_check':True,'iob_one_check':False,'demand_draft_check':False})
				
			elif payment_method == 'Dd':
				self.write(cr,uid,res.id,{'demand_draft_check':True,'iob_one_check':False,'neft_check':False})	#abhidd
			
			elif payment_method == 'Dd':
				self.write(cr,uid,res.id,{'demand_draft_check':True,'iob_one_check':False,'neft_check':False})	#abhidd
			srch_cheque = self.pool.get('iob.one.sales.receipts').search(cr,uid,[('iob_one_payment_id2','=',res.id)])
			if srch_cheque:
				for cheque in self.pool.get('iob.one.sales.receipts').browse(cr,uid,srch_cheque):
					cr.execute('delete from iob_one_sales_receipts where id=%(val)s',{'val':cheque.id})

			srch_neft = self.pool.get('neft.sales.receipts').search(cr,uid,[('neft_bank_payment_one_id','=',res.id)])
			if srch_neft:
				for neft in self.pool.get('neft.sales.receipts').browse(cr,uid,srch_neft):
					cr.execute('delete from neft_sales_receipts where id=%(val)s',{'val':neft.id})

			################################################abhidd####################################start#########		
			srch_demand_draft = self.pool.get('demand.draft.sales.receipts').search(cr,uid,[('demand_draft_id','=',res.id)])
			if srch_demand_draft:
				for ddraft in self.pool.get('demand.draft.sales.receipts').browse(cr,uid,srch_demand_draft):
					cr.execute('delete from demand_draft_sales_receipts where id=%(val)s',{'val':ddraft.id})		
					
			################################################abhidd####################################end#########
		return True

	def psd_remove(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			payment_method = res.payment_method
			if not payment_method:
				raise osv.except_osv(('Alert!'),('Please select Bank Payment Method.'))
		
			if res.iob_one_check == True:
				self.write(cr,uid,res.id,{'iob_one_check':False,'payment_method':''})
			elif res.neft_check == True:
				self.write(cr,uid,res.id,{'neft_check':False,'payment_method':''})

			elif res.demand_draft_check == True:#abhidd
				self.write(cr,uid,res.id,{'demand_draft_check':False,'payment_method':''})	
			srch_cheque = self.pool.get('iob.one.sales.receipts').search(cr,uid,[('iob_one_payment_id2','=',res.id)])
			if srch_cheque:
				for cheque in self.pool.get('iob.one.sales.receipts').browse(cr,uid,srch_cheque):
					cr.execute('delete from iob_one_sales_receipts where id=%(val)s',{'val':cheque.id})

			srch_neft = self.pool.get('neft.sales.receipts').search(cr,uid,[('neft_bank_payment_one_id','=',res.id)])
			if srch_neft:
				for neft in self.pool.get('neft.sales.receipts').browse(cr,uid,srch_neft):
					cr.execute('delete from neft_sales_receipts where id=%(val)s',{'val':neft.id})
					
			################################################abhidd####################################start#########		
			srch_demand_draft = self.pool.get('demand.draft.sales.receipts').search(cr,uid,[('demand_draft_id','=',res.id)])
			if srch_demand_draft:
				for ddraft in self.pool.get('demand.draft.sales.receipts').browse(cr,uid,srch_demand_draft):
					cr.execute('delete from demand_draft_sales_receipts where id=%(val)s',{'val':ddraft.id})		
					
			################################################abhidd####################################end#########		
		return True

	def psd_add(self, cr, uid, ids, context=None):
		total=0.0
		total_amount=0.0
		service_tax=0.0
		ed_cess=0.0
		hs_cess=0.0
		temp=[]
		
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			acc_id = res.account_id

			if not acc_id.name:
				raise osv.except_osv(('Alert'),('Please Select Account.'))
					  
			elif acc_id.account_selection == 'iob_two':
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_iob_two_form')
				return {
					'name': ("Add"+" "+ acc_id.name +" "+" Details"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'bank.payment.one.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					}

			elif acc_id.account_selection == 'iob_one': #and acc_id.receive_bank_no =='bank_one': # I.O.B I wizard open for both receving bank as requirement by vijay patel on 19 jan 2015
				if acc_id.ho_bank_wizard_check == True:
					models_data=self.pool.get('ir.model.data')
					form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_iob_one_payment_form')
					return {
						'name': ("Add"+" "+ acc_id.name +" "+"Details"),'domain': '[]',
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'bank.payment.one.line',
						'target' : 'new',
						'res_id':int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								   (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True,
					}
				else:
					return True

	def save_iob_one(self, cr, uid, ids, context=None):
		iob_total = 0.0
		neft_total = 0.0
		credit_amount = 0.0
		debit_amount=0.0
		dd_total = 0.0#abhidd
		total=0.0
		for rec in self.browse(cr,uid,ids):
			#if rec.iob_one_payment_one2many == []:
				#raise osv.except_osv(('Alert'),('No line to process.'))
			if rec.iob_one_payment_one2many:
				for iob_line in rec.iob_one_payment_one2many:
					cheque_amount = iob_line.cheque_amount
					iob_total = iob_total + cheque_amount

					if not iob_line.cheque_date:
						raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
					if not iob_line.cheque_no:
						raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
					if not iob_line.drawee_bank_name:
						raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
					if not iob_line.bank_branch_name:
						raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))

					search = self.pool.get('bank.payment.one.line').search(cr,uid,[('id','=',iob_line.iob_one_payment_id2.id)])
					for res in self.pool.get('bank.payment.one.line').browse(cr,uid,search):

						credit_amount = res.credit_amount
						debit_amount = res.debit_amount
					amount = iob_line.cheque_amount
					total = total + amount

					if iob_line.cheque_no: 
						for n in str(iob_line.cheque_no):
								p = re.compile('([0-9]{6}$)')
								if p.match(iob_line.cheque_no)== None :
										self.pool.get('iob.one.sales.receipts').create(cr,uid,{
								'cheque_no':''})
										raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
					#else :
					#        raise osv.except_osv(('Alert'),('No line to process.'))
	
					'''if credit_amount:
						if iob_total != credit_amount:
							raise osv.except_osv(('Alert'),('Amount should be equal.'))
					elif debit_amount:
						if iob_total != debit_amount:
							raise osv.except_osv(('Alert'),('Amount should be equal.'))'''#this is for the write the iob value 

				if rec.type=='debit':
					self.write(cr,uid,rec.id,{'debit_amount':total})
				else:
					self.write(cr,uid,rec.id,{'credit_amount':total})#a

			elif rec.neft_payment_one2many:
				for neft_line in rec.neft_payment_one2many:
					neft_amount = neft_line.neft_amount
					neft_total = neft_total + neft_amount

					if not neft_line.beneficiary_bank_name:
						raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
					if not neft_line.pay_ref_no:
						raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
					if not neft_line.neft_amount:
						raise osv.except_osv(('Alert!'),('Please provide Amount.'))

					if neft_line:
						srch = self.pool.get('bank.payment.one.line').search(cr,uid,[('id','=',neft_line.neft_bank_payment_one_id.id)])
						for res in self.pool.get('bank.payment.one.line').browse(cr,uid,srch):
							credit_amount = res.credit_amount
							debit_amount = res.debit_amount

				if rec.type=='debit':
					self.write(cr,uid,rec.id,{'debit_amount':neft_total})
				else:
					self.write(cr,uid,rec.id,{'credit_amount':neft_total})#a

				'''if credit_amount:
					if neft_total != credit_amount:
						raise osv.except_osv(('Alert'),('Amount should be equal.'))
				elif debit_amount:
					if neft_total != debit_amount:
						raise osv.except_osv(('Alert'),('Amount should be equal.'))'''
			#################################################abhidd###############start################
			elif rec.demand_draft_payment_one_one2many:
				for dd_line in rec.demand_draft_payment_one_one2many:
					dd_amount = dd_line.dd_amount
					dd_total = dd_total + dd_amount

					if not dd_line.demand_draft_drawee_bank_name:
						raise osv.except_osv(('Alert!'),('Please provide Demand Draft Drawee Name.'))
					#if not dd_line.demand_draft_check_drawn_name:
						#raise osv.except_osv(('Alert!'),('Please provide Demand Draft Drawn Name.'))
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

					if dd_line:
						srch = self.pool.get('demand.draft.sales.receipts').search(cr,uid,[('id','=',dd_line.demand_draft_id.id)])
						for res in self.pool.get('account.sales.receipts.line').browse(cr,uid,srch):
							credit_amount = res.credit_amount
							debit_amount = res.debit_amount

					if dd_line.dd_no: 
								for n in str(dd_line.dd_no):
										p = re.compile('([0-9]{9}$)')
										if p.match(dd_line.dd_no)== None :
												self.pool.get('demand.draft.sales.receipts').create(cr,uid,{
										'dd_no':''})
												raise osv.except_osv(('Alert!'),('Please Enter 9 digit Demand draft Number.'))
				if rec.type=='debit':
					self.write(cr,uid,rec.id,{'debit_amount':dd_total})
				else:
					self.write(cr,uid,rec.id,{'credit_amount':dd_total})#a
			
			#############################################abhidd######################end##########			
			else :
					raise osv.except_osv(('Alert'),('No line to process.'))
		#self.write(cr,uid,rec.id,{'debit_amount':total})

		return {'type': 'ir.actions.act_window_close'}


	def save_iob_two(self, cr, uid, ids, context=None):
		total = 0.0
		for rec in self.browse(cr,uid,ids):
			if rec.iob_two_one2many == []:
				raise osv.except_osv(('Alert'),('No line to proceed.'))
			for line in rec.iob_two_one2many:
				if not line.drawee_bank_name_new:
					raise osv.except_osv(('Alert!'),('Please provide Drawee Bank Name.'))
				if not line.bank_branch_name:
					raise osv.except_osv(('Alert!'),('Please provide Bank Branch Name.'))

				if line.cheque_no: 
					for n in str(line.cheque_no):
						p = re.compile('([0-9]{6}$)')
						if p.match(line.cheque_no)== None :
							self.pool.get('iob.two.payment').create(cr,uid,{'cheque_no':''})
							raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
				if line:
					search = self.pool.get('bank.payment.one.line').search(cr,uid,[('id','=',line.bank_payment_one_id.id)])
					for res in self.pool.get('bank.payment.one.line').browse(cr,uid,search):

						credit_amount = res.credit_amount
						debit_amount = res.debit_amount

					amount = line.cheque_amount
					total = total + amount
					
			'''if credit_amount:
				if total != credit_amount:
					raise osv.except_osv(('Alert'),('Amount should be equal.'))
			if debit_amount:
				if total != debit_amount:
					raise osv.except_osv(('Alert'),('Amount should be equal.'))'''

			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':total})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':total})#a
		return {'type': 'ir.actions.act_window_close'}

	def cancel(self, cr, uid, ids, context=None):
		return {'type': 'ir.actions.act_window_close'}

bank_payment_one_line()




class cash_payment(osv.osv):
	_inherit = 'cash.payment'
	_columns = {
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'psd_accounting': fields.boolean('PSD Accounting'),
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(cash_payment, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	def onchange_payment_date(self, cr, uid, ids, payment_date, context=None):
		v = {}
		if payment_date:
			today_date = datetime.now().date()			
			py_date = str(today_date + relativedelta(days=-5))
			if payment_date < str(py_date) or payment_date > str(today_date):
				raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
		return {'value':v}

	def account_type(self, cr, uid, ids, account_id, context=None):
		v = {}
		if account_id:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in ('cash','iob_one','iob_two'):
						v['type'] = 'credit'
					else:
						v['type'] = ''
		return {'value':v}

	def onchange_type(self, cr, uid, ids, account_id, type, context=None):
		v = {}
		if account_id and type:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in ('cash','iob_one','iob_two') and type == 'debit':
						raise osv.except_osv(('Alert'),('Cash cannot be debited.'))
		return {'value':v}

	def add_psd_cash_info(self, cr, uid, ids, context=None):#Cash payment ( add button )
		for res in self.browse(cr,uid,ids):

			if not res.customer_name and res.account_id.name=='ITDS on Contract Pymt':
				raise osv.except_osv(('Alert'),('Please select Supplier Name'))

			state = res.state
			acc_id = res.account_id.id
			types = res.type
			account_id1=res.account_id#a
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
			if res.account_id.account_selection in ('st_input','excise_input'):
				for t in res.cash_payment_one2many:
					if t.account_id.account_selection in acc_selection_list:
						total += t.debit_amount

				search_tax_id = [] ###To Remove Hard Code Service Tax 
				service_tax = ed_cess = hs_cess = 0.0

			if res.account_id.account_selection  == 'cash':
				if res.type=='debit':
					raise osv.except_osv(('Alert'),('Cash cannot be debited.'))

			if res.account_id.account_selection in ('iob_one','cash','iob_two'):
				if res.type=='debit':
					for j in res.cash_payment_one2many:
						if j.type=='credit':
							total_amount += j.credit_amount
						if j.type=='debit':
							auto_credit_total += j.debit_amount
					if total_amount>auto_credit_total:
						total_amount -= auto_credit_total
					else:		
						total_amount=0.0
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

			if acc_id:
					self.pool.get('cash.payment.line').create(cr,uid,{
												'cash_payment_id':res.id,
												'debit_amount':total_amount,
												'credit_amount':auto_credit_cal,
												'account_id':acc_id,
												'type':res.type,
												'customer_name':res.customer_name.id if res.customer_name.id else '',
												})

			self.write(cr,uid,res.id,{'account_id':None,'type':''})

		return True


	def psd_cash_payment_process(self, cr, uid, ids, context=None):#Cash Payment Process Button
		cr_total = dr_total = employee_total= itds_total = chk_cash_entry=0.0
		cash_cost_id = employee_tempname= move = ''
		post=[]
		line_acc = []
		today_date = datetime.now().date()
		py_date = False
		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			if res.payment_date:
				py_date = str(today_date + relativedelta(days=-5))
				if res.payment_date < str(py_date) or res.payment_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))

				payment_date=res.payment_date
			else:
				payment_date=datetime.now().date()

			for line in res.cash_payment_one2many:
				line_acc.append(line.account_id.account_selection)
				if line.credit_amount:
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				if line.debit_amount:
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				cr_total += line.credit_amount
				dr_total += line.debit_amount

				account_id = line.account_id.id
				temp = tuple([account_id])
				post.append(temp)
				for i in range(0,len(post)):
					for j in range(i+1,len(post)):
						if post[i][0]==post[j][0]:
							pass #raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
						
				if line.account_id.account_selection == 'cash': # 23 DEC 2015
					chk_cash_entry+=1
			if not 'cash' in line_acc:
				raise osv.except_osv(('Alert'),('Payment entry cannot be processed if Cash ledger is not selected.'))
			if chk_cash_entry ==0.0: # 23 DEC 2015
				raise osv.except_osv(('Alert'),('Please select proper account name.'))
			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
		for rec in self.browse(cr,uid,ids):
			for chk_ln in rec.cash_payment_one2many:   
				if chk_ln.account_id.account_selection == 'primary_cost_service' and chk_ln.account_id.bank_charges_bool:
					self.write(cr,uid,rec.id,{'bank_charges_check':True})
				
			for line in rec.cash_payment_one2many:
				total = 0.0
				emp_name = ""
				credit_amount = line.credit_amount
				debit_amount = line.debit_amount
				account_name = line.account_id.name
				acc_selection = line.account_id.account_selection
				acc_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
								  'primary_cost_service','primary_cost_vehicle','primary_cost_cse_office']
				
				if acc_selection == 'security_deposit': # HHH 9may
					for sec_dep_line in line.security_deposit_one2many:
						self.pool.get('security.deposit').write(cr,uid,sec_dep_line.id,{
							'security_check_against':True,
							'customer_name':line.customer_name.id if line.customer_name.id else '' ,
							'customer_name_char':res.customer_name.name if res.customer_name.name else '' ,
							})
						
				if acc_selection == 'sundry_deposit': # HHH 20may
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
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
					if acc_selection == 'primary_cost_office':
						cash_office_id = ''
						office_total = 0.0
						for office_line in line.cash_office_name:
							cash_office_id = office_line.cash_primary_office_id.id
							total +=  office_line.amount
	
						if not cash_office_id:
							pass # 1 dec as per vijay raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
					if acc_selection == 'primary_cost_phone':
						cash_phone_id = ''
						phone_total = 0.0
						for phone_line in line.cash_primary_phone_line:
							cash_phone_id = phone_line.cash_primary_phone_id.id
							total  += phone_line.amount
	
						if not cash_phone_id:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
					if acc_selection == 'primary_cost_vehicle':
						cash_vehicle_id = ''
						vehicle_total = 0.0
						for vehicle_line in line.cash_primary_vehicle_line:
							cash_vehicle_id = vehicle_line.cash_primary_vehicle_id.id
							total += vehicle_line.amount
	
						if not cash_vehicle_id:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						
					if acc_selection == 'primary_cost_service':
						cash_service_id = ''
						service_total = 0.0
						for service_line in line.primary_cash_cost_service_one2many:
							cash_service_id = service_line.cash_primary_service_id.id
							total += service_line.amount
	
						if not cash_service_id:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					
					if acc_selection == 'primary_cost_cse_office':
						cash_cse_id = ''
						cse_total = 0.0
						for cse_line in line.cash_primary_cse_office_one2many:
							cash_cse_id = cse_line.cash_primary_cse_office_id.id
							emp_name = cse_line.emp_name.id
							total +=  cse_line.amount
						self.write(cr,uid,rec.id,{'employee_name':emp_name})
	
						if not cash_cse_id:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						
					if credit_amount:
						if total != credit_amount:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if total != debit_amount:
							pass # 1 dec as per vijay   raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))
								
	# ITDS cash payment 14 dec >>>>>>>>>>
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
#<<<<<<<<<<<<<<<<<<<<<

				# 50k condition
				if acc_selection == 'cash' and line.debit_amount >= 50000 or line.credit_amount >= 50000 and res.customer_name.id != False:
					raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))
				balance = 0.0
				if acc_selection == 'cash':
					if line.debit_amount >= 10000 or line.credit_amount >= 10000:
						#balance = line.account_id.debit - line.account_id.credit + line.account_id.balance_import
						balance = self.cash_balance(cr,uid,rec.payment_date,context=context)
						if balance < line.credit_amount or balance < line.debit_amount:
							raise osv.except_osv(('Alert'),('Cash account dont have sufficient balance to process.'))
				if acc_selection == 'st_input':
					cash_id = ''
					phone_total = 0.0
					for line1 in line.cash_st_input_one2many:
						cash_id =line1.cash_line_input_id

					if not cash_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

				if acc_selection == 'excise_input':
					cash_id1 = ''
					phone_total = 0.0
					for line1 in line.cash_excise_input_one2many:
						cash_id1 =line1.cash_line_excise_id

					if not cash_id1:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

	
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_cash_payment_form')
			tree_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_cash_payment_tree')
			#value_id = self.pool.get('ir.sequence').get(cr, uid, 'cash.payment')
			
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
			if pcof_key and cash_payment_id:
				cr.execute("select cast(count(id) as integer) from cash_payment where payment_no is not null   and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + cash_payment_id +  str(year1) +str(seq).zfill(6)

			self.write(cr,uid,ids,{'payment_no':value_id,'payment_date': payment_date,'voucher_type':'Payment (Cash)'})
			date = payment_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id

			srch_jour_cash = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Cash')])
			for jour_cash in self.pool.get('account.journal').browse(cr,uid,srch_jour_cash):
				journal_cash = jour_cash.id

			move = self.pool.get('account.move').create(cr,uid,{
									'journal_id':journal_cash,#Confirm from PCIL(JOURNAL ID)
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
			for i in rec.cash_payment_one2many:
				search_temp=self.pool.get('st.input').search(cr,uid,[('cash_line_input_id','=',i.id)])
				for j in self.pool.get('st.input').browse(cr,uid,search_temp):
					self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
				search_temp1=self.pool.get('st.input').search(cr,uid,[('cash_line_excise_id','=',i.id)])
				for k in self.pool.get('st.input').browse(cr,uid,search_temp1):
					self.pool.get('st.input').write(cr,uid,k.id,{'account_id':i.account_id.id})
			for update in rec.cash_payment_one2many:
				self.pool.get('cash.payment.line').write(cr,uid,update.id,{'state':'done'})

			

		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
		for payment_his in self.browse(cr,uid,ids):#edited by rohit 12 may
			#receipt_no=payment_his.value_id#payment_his.receipt_no
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

		models_data=self.pool.get('ir.model.data')
		# form_id = models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_cash_payment_tree')
		#self.sync_cash_payment(cr,uid,ids,context=context)###due to supplier not sync
		return {
			'name':'Cash Payment',
			'view_mode': 'tree,form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'cash.payment',
			'res_id':rec.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
		}

cash_payment()

class cash_payment_line(osv.osv):
	_inherit = 'cash.payment.line'

	# def add(self, cr, uid, ids, context=None):  # Cash payment ( arrow add button)
	# 		total=total_amount=service_tax=ed_cess=hs_cess=0.0
	# 		temp=[]

	# 		for i in self.browse(cr,uid,ids):
	# 			acc_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
	# 								  'primary_cost_service','primary_cost_vehicle','primary_cost_cse_office']
				
	# 			acc_selection_list2 = ['security_deposit' , 'itds' , 'sundry_deposit' , 'st_input' ,'excise_input' ]
				
	# 			srch_tmp = self.pool.get('cash.payment').search(cr,uid,[('id','=',i.cash_payment_id.id)])
	# 			for j in self.pool.get('cash.payment').browse(cr,uid,srch_tmp):
	# 				search_line =  self.pool.get('cash.payment.line').search(cr,uid,[('cash_payment_id','=',j.id)])
	# 				for t in self.pool.get('cash.payment.line').browse(cr,uid,search_line):
	# 					if t.account_id.account_selection in acc_selection_list:
	# 						total += t.debit_amount
						
	# 		for res in self.browse(cr,uid,ids):
	# 			acc_selection = res.account_id.account_selection
	# 			credit_amount = res.credit_amount
	# 			debit_amount = res.debit_amount
	# 			res_id = res.id

	# 			if acc_selection in acc_selection_list:
	# 				if acc_selection == 'primary_cost_cse':
	# 					view_name = 'account_cash_primary_cost_form'
						
	# 				if acc_selection == 'primary_cost_office': 
	# 					view_name = 'account_cash_primary_cost_office_form'
		
	# 				if acc_selection == 'primary_cost_phone':
	# 					view_name = 'account_cash_primary_cost_phone_form'
		
	# 				if acc_selection == 'primary_cost_vehicle':
	# 					view_name = 'account_cash_primary_cost_vehicle_form'
		
	# 				if acc_selection == 'primary_cost_service':
	# 					view_name = 'account_primary_cost_cash_service_form'
		
	# 				if acc_selection == 'primary_cost_cse_office':
	# 					view_name = 'account_primary_cost_cse_office_form'
						
	# 				models_data=self.pool.get('ir.model.data')
	# 				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name)
	# 				return {
	# 					'name': ("Add Primary Cost Category"),'domain': '[]',
	# 					'type': 'ir.actions.act_window',
	# 					'view_id': False,
	# 					'view_type': 'form',
	# 					'view_mode': 'form',
	# 					'res_model': 'cash.payment.line',
	# 					'target' : 'new',
	# 					'res_id':int(res_id),
	# 					'views': [(form_view and form_view[1] or False, 'form'),
	# 							   (False, 'calendar'), (False, 'graph')],
	# 					'domain': '[]',
	# 					'nodestroy': True,
	# 					}


	# 			if acc_selection  in acc_selection_list2:
	# 				if acc_selection == 'security_deposit':
	# 					if  res.type =='debit': # SD sagar 18 Feb 2016
	# 						view_name2 =   'cash_payment_security_deposit_form'
	# 						name_wizard = "Add Security Deposit"
	# 					else:
	# 						raise osv.except_osv(('Alert'),('No Information'))
					
	# 				if acc_selection == 'itds': # add ITDS 14 Dec 
	# 					view_name2 = 'account_cash_itds_form'
	# 					name_wizard = "Add ITDS on Contract Payments Details"
		
	# 				if acc_selection == 'sundry_deposit':
	# 					if res.type =='debit': #EMD sagar 8sept 21
	# 						view_name2 =  'account_cash_sundry_dposit_form'
	# 						name_wizard = "Add Sundry Deposit"
	# 					else:
	# 						raise osv.except_osv(('Alert'),('No Information')) 
						
	# 				if acc_selection == 'st_input':
	# 					view_name2 =  'account_cash_st_input_form'
	# 					name_wizard =  "Add ST Input Details"
						
	# 				if res.account_id.account_selection == 'excise_input':                                                
	# 					view_name2 = 'account_cash_excise_input_form'
	# 					name_wizard = "Add Excise Input Details"
						
	# 				models_data=self.pool.get('ir.model.data')
	# 				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name2)
	# 				return {
	# 					'name': (name_wizard),'domain': '[]',
	# 					'type': 'ir.actions.act_window',
	# 					'view_id': False,
	# 					'view_type': 'form',
	# 					'view_mode': 'form',
	# 					'res_model': 'cash.payment.line',
	# 					'target' : 'new',
	# 					'res_id':int(res_id),
	# 					'views': [(form_view and form_view[1] or False, 'form'),
	# 							   (False, 'calendar'), (False, 'graph')],
	# 					'domain': '[]',
	# 					'nodestroy': True,
	# 				}
	# 			else:
	# 				raise osv.except_osv(('Alert'),('No Information'))
	def psd_add(self, cr, uid, ids, context=None):  # Cash payment ( arrow add button)
			total=total_amount=service_tax=ed_cess=hs_cess=0.0
			temp=[]

			for i in self.browse(cr,uid,ids):
				acc_selection_list = ['primary_cost_phone','primary_cost_cse','primary_cost_office',
									  'primary_cost_service','primary_cost_vehicle','primary_cost_cse_office']
				
				acc_selection_list2 = ['security_deposit' , 'itds' , 'sundry_deposit' , 'st_input' ,'excise_input' ]
				
				srch_tmp = self.pool.get('cash.payment').search(cr,uid,[('id','=',i.cash_payment_id.id)])
				for j in self.pool.get('cash.payment').browse(cr,uid,srch_tmp):
					search_line =  self.pool.get('cash.payment.line').search(cr,uid,[('cash_payment_id','=',j.id)])
					for t in self.pool.get('cash.payment.line').browse(cr,uid,search_line):
						if t.account_id.account_selection in acc_selection_list:
							total += t.debit_amount
						
			for res in self.browse(cr,uid,ids):
				acc_selection = res.account_id.account_selection
				credit_amount = res.credit_amount
				debit_amount = res.debit_amount
				res_id = res.id

				if acc_selection in acc_selection_list:
					if acc_selection == 'primary_cost_cse':
						view_name = 'psd_account_cash_primary_cost_form'
						
					if acc_selection == 'primary_cost_office': 
						view_name = 'psd_account_cash_primary_cost_office_form'
		
					if acc_selection == 'primary_cost_phone':
						view_name = 'psd_account_cash_primary_cost_phone_form'
		
					if acc_selection == 'primary_cost_vehicle':
						view_name = 'psd_account_cash_primary_cost_vehicle_form'
		
					if acc_selection == 'primary_cost_service':
						view_name = 'psd_account_primary_cost_cash_service_form'
		
					if acc_selection == 'primary_cost_cse_office':
						view_name = 'psd_account_primary_cost_cse_office_form'
						
					models_data=self.pool.get('ir.model.data')
					form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name)
					return {
						'name': ("Add Primary Cost Category"),'domain': '[]',
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


				if acc_selection  in acc_selection_list2:
					if acc_selection == 'security_deposit':
						if  res.type =='debit': # SD sagar 18 Feb 2016
							view_name2 =   'psd_cash_payment_security_deposit_form'
							name_wizard = "Add Security Deposit"
						else:
							raise osv.except_osv(('Alert'),('No Information'))
					
					if acc_selection == 'itds': # add ITDS 14 Dec 
						view_name2 = 'psd_account_cash_itds_form'
						name_wizard = "Add ITDS on Contract Payments Details"
		
					if acc_selection == 'sundry_deposit':
						if res.type =='debit': #EMD sagar 8sept 21
							view_name2 =  'psd_account_cash_sundry_dposit_form'
							name_wizard = "Add Sundry Deposit"
						else:
							raise osv.except_osv(('Alert'),('No Information')) 
						
					if acc_selection == 'st_input':
						view_name2 =  'psd_account_cash_st_input_form'
						name_wizard =  "Add ST Input Details"
						
					if res.account_id.account_selection == 'excise_input':                                                
						view_name2 = 'psd_account_cash_excise_input_form'
						name_wizard = "Add Excise Input Details"
						
					models_data=self.pool.get('ir.model.data')
					form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name2)
					return {
						'name': (name_wizard),'domain': '[]',
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
				else:
					raise osv.except_osv(('Alert'),('No Information'))
cash_payment_line()

class cheque_bounce(osv.osv):
	_inherit = 'cheque.bounce'
	_columns = {
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'particulars':fields.selection([('travelling_expenses','Travelling Expenses'),('telephone_and_mobile','Telephone & Mobile'),('conveyance','Conveyance')],'Particulars'),
		'employee':fields.selection([('cse1','CSE 1'),('cse2','CSE 2'),('cse3','CSE3')],'Employee'),
		'psd_accounting': fields.boolean('PSd Accounting'),
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(cheque_bounce, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res	

	def onchange_payment_date(self, cr, uid, ids, payment_date, context=None):
		v = {}
		if payment_date:
			today_date = datetime.now().date()			
			py_date = str(today_date + relativedelta(days=-5))
			if payment_date < str(py_date) or payment_date > str(today_date):
				raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
		return {'value':v}

	def onchange_type(self, cr, uid, ids, account_id, type, context=None):
		v = {}
		if account_id and type:
			srch = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)])
			if srch:
				for acc in self.pool.get('account.account').browse(cr,uid,srch):
					if acc.account_selection in ('iob_one','iob_two') and type == 'debit':
						raise osv.except_osv(('Alert'),('Bank A/c cannot be debited.'))
		return {'value':v}

	def psd_add_cheque_bounce(self, cr, uid, ids, context=None):
		post = []
		temp1=[]
		auto_credit_cal=auto_debit_cal=auto_credit_total=auto_debit_total=0.0
		for res in self.browse(cr,uid,ids):
			state = res.state
			acc_id = res.account_id.id
			types = res.type
			auto_debit_total=auto_credit_total=0.0
			if res.account_id.account_selection in ('iob_one','iob_two'):
				if res.type=='debit':
					raise osv.except_osv(('Alert'),('Bank A/c cannot be debited.'))
			if not acc_id:
				raise osv.except_osv(('Alert'),('Plaese select Account Name.'))
			if not types:
				raise osv.except_osv(('Alert'),('Plaese select Type.'))

			if res.account_id.account_selection == 'cash':
				raise osv.except_osv(('Alert'),('Plaese select proper Account Name.'))

			if res.account_id.account_selection == 'iob_two':
				raise osv.except_osv(('Alert'),('Plaese select proper Account Name.'))

			account_id1=res.account_id
			for i in res.cheque_bounce_lines:
				if account_id1.id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
					
			if  res.account_id.account_selection in ('iob_one','cash','iob_two'):
					if res.type=='debit':
						for j in res.cheque_bounce_lines:
							if j.type=='credit':
								auto_debit_total += j.credit_amount
							if j.type=='debit':
								auto_credit_total += j.debit_amount
						if auto_debit_total>auto_credit_total:
							auto_debit_total -= auto_credit_total
						else:		
							auto_debit_total=0.0
					else:	
						for k in res.cheque_bounce_lines:
							if k.type=='credit':
								auto_debit_cal += k.credit_amount
							if k.type=='debit':
								auto_credit_cal += k.debit_amount
						if auto_debit_cal < auto_credit_cal:
							auto_credit_cal -= auto_debit_cal
						else:
							auto_credit_cal=0.0


			if res.account_id.account_selection == 'against_ref':
				cr.execute('update invoice_adhoc_master set cheque_bounce_bool = False where cheque_bounce_bool_process = False and cheque_bounce_bool = True and invoice_number is not Null')
				
			self.pool.get('cheque.bounce.line').create(cr,uid,{
							'cheque_bounce_line_id':res.id,
							'account_id':acc_id,
							'type':res.type,
							'debit_amount':auto_debit_total,
							'credit_amount':auto_credit_cal,
							'partner_id':res.partner_id.id,
							})

			self.write(cr,uid,res.id,{'account_id':None,'type':''})

		return True	

	def psd_cheque_bounce_process(self, cr, uid, ids, context=None): # Cheque Bounce Process
		sales_receipt = self.pool.get('account.sales.receipts')
		invoice_history = self.pool.get('invoice.receipt.history')
		invoice_adhoc_master = self.pool.get('invoice.adhoc.master')
		itds_adjustment = self.pool.get('itds.adjustment')
		security_deposit = self.pool.get('security.deposit')
		cheque_bounce_line = self.pool.get('cheque.bounce.line')
		iob_one = self.pool.get('iob.one.sales.receipts')

		count = count1 = 0
		flag1 =flag = py_date = False
		cr_total = dr_total = chk_account_selection = 0.0###23de15
		move = grand_total = invoice_date = invoice_number = iob_one_id = neft_id = ''
		post=[]
		status=[]
		line_acc = []
		advance_id = invoice_id_receipt = advance_ref_id = cheque_no = ''
		neft_amount = cheque_amount = adv_against_line=0.0
		ref_amount = ref_amount_adv = ref_amount_cofb = 0.0
		grand_total_against = grand_total_advance = grand_total = 0.0
		today_date = datetime.now().date()

		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			if res.payment_date:
				py_date = str(today_date + relativedelta(days=-5))
				if res.payment_date < str(py_date) or res.payment_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
				payment_date=res.payment_date
			else:	
				payment_date=datetime.now().date()
			for line in res.cheque_bounce_lines:
				line_acc.append(line.account_id.account_selection)
				if line.credit_amount:
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				if line.debit_amount:
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
					
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
				
				if acc_selection in ['iob_one','iob_two']:
					chk_account_selection +=1
			
			if not 'iob_one' in line_acc:
				raise osv.except_osv(('Alert'),('Payment entry cannot be processed if I.O.B A/C III ledger is not selected.'))		
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
					
					if ln.debited_invoice_line: # invoice_adhoc_master
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
								
					for cfob_invoice in ln.cfob_line: # HHH 3Mar
						if cfob_invoice.cfob_boolean_cb:
							flag1 = True
							invoice_id_receipt= True
							self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_invoice.id,{'cfob_boolean_process_cb':True})
						else :
							self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_invoice.id,{'cfob_id':None})

					if flag == False and flag1 == False:
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
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_cheque_bounce_form')
			tree_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_cheque_bounce_tree')
			
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
			if pcof_key and cheque_bounce_payment_id:
				cr.execute("select cast(count(id) as integer) from cheque_bounce where payment_no is not null   and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + cheque_bounce_payment_id +  str(year1) +str(seq).zfill(6)
				
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
			'view_mode': 'tree,form',
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


class cheque_bounce_line(osv.osv):
	_inherit = 'cheque.bounce.line'

	# def add(self, cr, uid, ids, context=None):
	# 	for res in self.browse(cr,uid,ids):
	# 		res_id = res.id
	# 		cheque_bounce_partner=res.cheque_bounce_line_id.partner_id.name
	# 		credit_amount = res.credit_amount
	# 		debit_amount = res.debit_amount
	# 		acc_id = res.account_id
	# 		customer = res.partner_id.name
	# 		partner_id = res.partner_id.id
	# 		types = res.type
	# 		acc_selection = acc_id.account_selection
	# 		acc_selection_list= ['iob_one','itds_receipt','security_deposit','against_ref','advance']

	# 		if not acc_id.name:
	# 			raise osv.except_osv(('Alert'),('Please Select Account.'))
			
	# 		if acc_selection in acc_selection_list:
	# 			if acc_id.account_selection == 'iob_one':
	# 				self.show_iob_details(cr,uid,ids,context=context)
	# 				view_name ='iob_one_cheque_form'
	# 				name_wizard = "Add"+" "+acc_id.name +" "+"Details"
					
	# 			if acc_id.account_selection == 'itds_receipt' and types == 'credit':
	# 				self.show_itds_details(cr,uid,ids,context=context)
	# 				view_name = 'itds_cheque_form'
	# 				name_wizard = "Paid ITDS Details"

	# 			if acc_id.account_selection == 'security_deposit' and types == 'credit': 
	# 				self.show_sd_details(cr,uid,ids,context=context)
	# 				view_name = 'sd_cheque_form'
	# 				name_wizard = "Paid Security Details"
					
	# 			if acc_id.account_selection == 'against_ref' and cheque_bounce_partner != 'CFOB': 
	# 				self.show_details(cr,uid,ids,context=context)
	# 				view_name = 'cheque_bounce_invoice_form'
	# 				name_wizard = "Paid Invoices Details"
					
	# 			if acc_id.account_selection == 'against_ref' and cheque_bounce_partner == 'CFOB':
	# 				self.show_details_cfob(cr,uid,ids,context=context)
	# 				view_name =  'cheque_bounce_invoice_cfob_form'
	# 				name_wizard =  "Paid CFOB Invoices Details"
					
	# 			if acc_id.account_selection == 'advance':                       # sagar 11 Dec for advance cheque_bounce
	# 				self.show_advance_details(cr,uid,ids,context=context)
	# 				view_name =  'cheque_bounce_advance_form'
	# 				name_wizard =  "Paid Advance Details"
					
	# 			models_data=self.pool.get('ir.model.data')
	# 			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name)
	# 			return {
	# 				'name': (name_wizard),'domain': '[]',
	# 				'type': 'ir.actions.act_window',
	# 				'view_id': False,
	# 				'view_type': 'form',
	# 				'view_mode': 'form',
	# 				'res_model': 'cheque.bounce.line',
	# 				'target' : 'new',
	# 				'res_id':int(res_id),
	# 				'views': [(form_view and form_view[1] or False, 'form'),
	# 						   (False, 'calendar'), (False, 'graph')],
	# 				'domain': '[]',
	# 				'nodestroy': True,
	# 			}
	def psd_add(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			cheque_bounce_partner=res.cheque_bounce_line_id.partner_id.name
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			acc_id = res.account_id
			customer = res.partner_id.name
			partner_id = res.partner_id.id
			types = res.type
			acc_selection = acc_id.account_selection
			acc_selection_list= ['iob_one','itds_receipt','security_deposit','against_ref','advance']

			if not acc_id.name:
				raise osv.except_osv(('Alert'),('Please Select Account.'))
			
			if acc_selection in acc_selection_list:
				if acc_id.account_selection == 'iob_one':
					self.show_iob_details(cr,uid,ids,context=context)
					view_name ='psd_iob_one_cheque_form'
					name_wizard = "Add"+" "+acc_id.name +" "+"Details"
					
				if acc_id.account_selection == 'itds_receipt' and types == 'credit':
					self.show_itds_details(cr,uid,ids,context=context)
					view_name = 'psd_itds_cheque_form'
					name_wizard = "Paid ITDS Details"

				if acc_id.account_selection == 'security_deposit' and types == 'credit': 
					self.show_sd_details(cr,uid,ids,context=context)
					view_name = 'psd_sd_cheque_form'
					name_wizard = "Paid Security Details"
					
				if acc_id.account_selection == 'against_ref' and cheque_bounce_partner != 'CFOB': 
					self.show_details(cr,uid,ids,context=context)
					view_name = 'psd_cheque_bounce_invoice_form'
					name_wizard = "Paid Invoices Details"
					
				if acc_id.account_selection == 'against_ref' and cheque_bounce_partner == 'CFOB':
					self.show_details_cfob(cr,uid,ids,context=context)
					view_name =  'psd_cheque_bounce_invoice_cfob_form'
					name_wizard =  "Paid CFOB Invoices Details"
					
				if acc_id.account_selection == 'advance':                       # sagar 11 Dec for advance cheque_bounce
					self.show_advance_details(cr,uid,ids,context=context)
					view_name =  'psd_cheque_bounce_advance_form'
					name_wizard =  "Paid Advance Details"
					
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name)
				return {
					'name': (name_wizard),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'cheque.bounce.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
				}
cheque_bounce_line()


class cust_supp_credit_refund(osv.osv):
	_inherit = 'cust.supp.credit.refund'

	_columns = {
		'is_transfered': fields.boolean(string = "Is Transfered"),
		'particulars':fields.selection([('travelling_expenses','Travelling Expenses'),('telephone_and_mobile','Telephone & Mobile'),('conveyance','Conveyance')],'Particulars'),
		'employee':fields.selection([('cse1','CSE 1'),('cse2','CSE 2'),('cse3','CSE3')],'Employee'),
		'psd_accounting': fields.boolean('PSD Accounting')
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(cust_supp_credit_refund, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res

	def onchange_payment_date(self, cr, uid, ids, payment_date, context=None):
		v = {}
		if payment_date:
			today_date = datetime.now().date()			
			py_date = str(today_date + relativedelta(days=-5))
			if payment_date < str(py_date) or payment_date > str(today_date):
				raise osv.except_osv(('Alert'),('Kindly select Payment Date 5 days earlier from current date.'))
		return {'value':v}

	def psd_add_credit_refund_info(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			state = res.state
			account_id = res.account_id.id
			types = res.type
			status = res.status
			auto_credit_cal=auto_debit_cal=auto_credit_total=auto_debit_total=0.0
			if not account_id:
				raise osv.except_osv(('Alert'),('Please select Account Name.'))
			if not types:
				raise osv.except_osv(('Alert'),('Please select Type.'))
			# if not status:
			# raise osv.except_osv(('Alert'),('Please select status.'))
			if res.account_id.account_selection:
				if res.account_id.account_selection in ('cash'):
					raise osv.except_osv(('Alert'),('Please select proper account name.'))
				if res.account_id.account_selection in ('iob_one','iob_two') and res.type=='debit':
					raise osv.except_osv(('Alert'),('Bank A/c cannot be debited.'))
				if  res.account_id.account_selection == 'iob_two':
						if res.type=='debit':
							for j in res.credit_refund_cs_one2many:
								if j.type=='credit':
									auto_debit_total += j.credit_amount
								if j.type=='debit':
									auto_credit_total += j.debit_amount
							if auto_debit_total>auto_credit_total:
								auto_debit_total -= auto_credit_total
							else:
								auto_debit_total=0.0
						else:
							for k in res.credit_refund_cs_one2many:
								if k.type=='credit':
									auto_debit_cal += k.credit_amount
								if k.type=='debit':
									auto_credit_cal += k.debit_amount
							if auto_debit_cal < auto_credit_cal:
								auto_credit_cal -= auto_debit_cal
							else:
								auto_credit_cal=0.0
							
			self.pool.get('cust.supp.credit.refund.line').create(cr,uid,{
										'credit_refund_id':res.id,
										'account_id':account_id,
										'type':types,
										'credit_amount':auto_credit_cal,
										'debit_amount':auto_debit_total,
										'status':res.status,
										'customer_name':res.customer_name.id,
										'payment_status':res.payment_status,
										 })
			self.write(cr,uid,res.id,{'account_id':None,'type':''})
			
		return True
cust_supp_credit_refund()


class cust_supp_credit_refund_line(osv.osv):
	_inherit = 'cust.supp.credit.refund.line'

	# def add(self, cr, uid, ids, context=None):
	# 	for res in self.browse(cr,uid,ids):
	# 		acc_selection = res.account_id.account_selection
	# 		status = res.status
	# 		types = res.type
	# 		res_id = res.id
	# 		view_name = name_wizard = ''
	# 		acc_selection_list = [ 'against_ref' ,'iob_two' , 'advance','iob_one']

	# 		if acc_selection in acc_selection_list:
	# 			if status == 'new_ref' and types == 'debit' and acc_selection != 'iob_two' :
	# 				view_name = 'credit_refund_form' 
	# 				name_wizard = "Credit Note Details/Credit Note ST Details"
					
	# 			if status == 'against_adv' and acc_selection != 'iob_two' and types == 'debit':
	# 				self.show_details(cr,uid,ids,context=context)
	# 				view_name =   'against_advance_form_cust_payment'
	# 				name_wizard = "Advance Payment Details"
					
	# 			if acc_selection == 'iob_two':
	# 				view_name ='account_credit_refund_iob_two_form'
	# 				name_wizard = "Add"+" "+ res.account_id.name +" "+"Details"
					
	# 			if acc_selection == 'iob_one':
	# 				view_name ='account_credit_refund_iob_one_form'
	# 				name_wizard = "Add"+" "+ res.account_id.name +" "+"Details"
	
	# 			if view_name:
	# 				models_data=self.pool.get('ir.model.data')
	# 				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name)
	# 				return {
	# 					'name': (name_wizard),'domain': '[]',
	# 					'type': 'ir.actions.act_window',
	# 					'view_id': False,
	# 					'view_type': 'form',
	# 					'view_mode': 'form',
	# 					'res_model': 'cust.supp.credit.refund.line',
	# 					'target' : 'new',
	# 					'res_id':int(res_id),
	# 					'views': [(form_view and form_view[1] or False, 'form'),
	# 							   (False, 'calendar'), (False, 'graph')],
	# 					'domain': '[]',
	# 					'nodestroy': True,
	# 				}
	# 	return True

	def psd_add(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			if res.account_id.account_selection:
				acc_selection = res.account_id.account_selection
				status = res.status
				types = res.type
				res_id = res.id
				view_name = name_wizard = ''
				acc_selection_list = [ 'against_ref' ,'iob_two' , 'advance','iob_one']

				if acc_selection in acc_selection_list:
					if types == 'debit' and acc_selection == 'against_ref' :
						view_name = 'psd_credit_refund_form' 
						name_wizard = "Credit Note Details/Credit Note ST Details"
						
					if acc_selection == 'advance' and types == 'debit':   #######Sagar 26aug15 >>
						self.show_details(cr,uid,ids,context=context)
						view_name =   'psd_against_advance_form_cust_payment'
						name_wizard = "Advance Payment Details"
						
					if acc_selection == 'iob_two':
						view_name ='psd_account_credit_refund_iob_two_form'
						name_wizard = "Add"+" "+ res.account_id.name +" "+"Details"
						
					if acc_selection == 'iob_one':
						view_name ='psd_account_credit_refund_iob_one_form'
						name_wizard = "Add"+" "+ res.account_id.name +" "+"Details"

					if view_name:
						models_data=self.pool.get('ir.model.data')
						form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name)
						return {
							'name': (name_wizard),'domain': '[]',
							'type': 'ir.actions.act_window',
							'view_id': False,
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'cust.supp.credit.refund.line',
							'target' : 'new',
							'res_id':int(res_id),
							'views': [(form_view and form_view[1] or False, 'form'),
									   (False, 'calendar'), (False, 'graph')],
							'domain': '[]',
							'nodestroy': True,
						}
		return True

cust_supp_credit_refund_line()