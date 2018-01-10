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

class bank_payment_one(osv.osv):
	_inherit = 'bank.payment.one'
	_order = 'payment_date desc'

	def process(self, cr, uid, ids, context=None):
	### Bank Payment Process Button 
		cr_total = dr_total = total = iob_total = service_total = chk_account_selection=0.0
		itds_total = cheque_amount = neft_amount = total_sundry_deposit = 0.0
		primary_cost_id=payment_date = neft_bank_payment_one_id = ''
		move = emp_name= service_cost = bank_payment_one_id = itds_id = iob_one_payment_id2 = ''
		post = []
		py_date = bank_charges_flag= bank_charges_bool=False
		ho_remmitance=True

		today_date = datetime.now().date()

		models_data=self.pool.get('ir.model.data')
		for res1 in self.browse(cr,uid,ids):
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
			## validation for credit and debit
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
							raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
			
				acc_selection = line.account_id.account_selection
				if acc_selection in ['iob_one','iob_two']:
					chk_account_selection +=1
					
			if chk_account_selection ==0.0:
					raise osv.except_osv(('Alert'),('Please select proper account name')) 
			
			self.write(cr,uid,ids,{'debit_amount_srch':dr_total})
			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
# >>>>>>>>>>>>for bank charge
		count = 0
		acc_selection_list = ['iob_one','iob_two']
		for res in self.browse(cr,uid,ids):
			for j in res.payment_one2many:
				if j.debit_amount:
					count+=1
				if j.account_id.bank_charges_bool==True:
					bank_charges_bool=True
					bank_charges_flag=True
		if count >= 1 and bank_charges_bool==True:
		        bank_charges_flag=False
#<<<<<<<<<<<<<<		
		for res in self.browse(cr,uid,ids):
			if res.payment_one2many:
				for j in res.payment_one2many:
					if j.account_id.account_selection=='ho_remmitance':
						ho_remmitance=False
					if  bank_charges_flag == False:
						# 21-04-2017
						if  j.account_id.account_selection == 'iob_two':
							j.payment_method = 'cheque'
						# ######################
						if  j.account_id.account_selection in acc_selection_list:
							if not j.payment_method:
								raise osv.except_osv(('Alert'),(' Enter Bank Details for "%s"') % (j.account_id.name))

			for bank_line in res.payment_one2many:
			## validation
				wizard_id = bank_line.wizard_id
				acc_selection = bank_line.account_id.account_selection
				account_name = bank_line.account_id.name
		
				credit_amount = bank_line.credit_amount
				debit_amount = bank_line.debit_amount
				if wizard_id == 0:
					self.wizard_id_write(cr,uid,ids,context=context)

				if acc_selection == 'iob_one': # condition add for bank charge to allow
					payment_method=bank_line.payment_method
					if payment_method=="" or payment_method==False:
						raise osv.except_osv(('Alert'),('Enter Payment Details Details against "%s" entry to proceed.') % (account_name))
					elif payment_method=="cheque":
						if not bank_line.iob_one_payment_one2many:
							raise osv.except_osv(('Alert'),('Enter Cheque Details against "%s" entry to proceed.') % (account_name))
					elif payment_method=="neft":
						if not bank_line.neft_payment_one2many:
							raise osv.except_osv(('Alert'),('Enter NEFT/RTGS Details against "%s" entry to proceed.') % (account_name))
					elif payment_method=="Dd":
						if not bank_line.demand_draft_payment_one2many:
							raise osv.except_osv(('Alert'),('Enter Demand Draft Details against "%s" entry to proceed.') % (account_name))
					for iob_one_line in bank_line.iob_one_payment_one2many: ## cheque
						iob_one_payment_id2 = iob_one_line.iob_one_payment_id2.id
						cheque_no = iob_one_line.cheque_no
						cheque_amount += iob_one_line.cheque_amount

						if not iob_one_line.cheque_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not iob_one_line.cheque_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not iob_one_line.drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not iob_one_line.bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))

					for neft_line in bank_line.neft_payment_one2many:  ##NEFT
						neft_bank_payment_one_id = neft_line.neft_bank_payment_one_id.id
						neft_amount  += neft_line.neft_amount
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
								if round(cheque_amount,2) != round(debit_amount,2):
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if credit_amount:
								if round(cheque_amount,2) != round(credit_amount,2):
									raise osv.except_osv(('Alert'),('credit amount should be equal'))

					if not iob_one_payment_id2:
						if neft_bank_payment_one_id:
							if debit_amount:
								if round(neft_amount,2) != round(debit_amount,2):
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if credit_amount:
								if round(neft_amount,2) != round(credit_amount,2):
									raise osv.except_osv(('Alert'),('credit amount should be equal'))
					self.write(cr,uid,ids,{'voucher_type':'Payment (Bank - A/c-I)'})

				elif acc_selection == 'iob_two':## bank II
					for iob_two_line in bank_line.iob_two_one2many:
						bank_payment_one_id = iob_two_line.bank_payment_one_id

					if bank_charges_bool:
						raise osv.except_osv(('Alert'),('Account "%s" can not used against Bank Charges.') % (account_name))
					if not bank_payment_one_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if bank_line.iob_two_one2many:
						for iob_two_ln in bank_line.iob_two_one2many:
							iob_total += iob_two_ln.cheque_amount
							if not iob_two_ln.drawee_bank_name_new:
								raise osv.except_osv(('Alert!'),('Please provide Drawee Bank Name.'))

							if not iob_two_ln.bank_branch_name:
								raise osv.except_osv(('Alert!'),('Please provide Bank Branch Name.'))

						if credit_amount:
							if round(iob_total,2) != round(credit_amount,2):
								raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
						if debit_amount:
							if round(iob_total,2) != round(debit_amount,2):
								raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

					if iob_two_ln.cheque_no:                       
						for n in str(iob_two_ln.cheque_no):
								p = re.compile('([0-9]{6}$)')
								if p.match(iob_two_ln.cheque_no)== None :
										raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))

					self.write(cr,uid,ids,{'voucher_type':'Payment  (Bank)'})
					
				elif acc_selection == 'sundry_deposit':
					for sundry_line in bank_line.HO_sundry_deposite_one2many:
						self.pool.get('sundry.deposit').write(cr,uid,sundry_line.id,{'pending_amount':sundry_line.payment_amount})
						

		for rec in self.browse(cr,uid,ids):
		## create payment number
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_bank_payment_one_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_bank_payment_one_tree')

			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = credit_note_id = end_year = pcof_key = ''

			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','bank.payment.one')])
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
					if comp_id.bank_payment_one_id:
						bank_payment_one_id = comp_id.bank_payment_one_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			seq_start = 1
			if pcof_key and bank_payment_one_id:
				# cr.execute("select cast(count(id) as integer) from bank_payment_one where payment_no is not null and payment_date>='2017-06-30'  and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				cr.execute("select cast(count(id) as integer) from bank_payment_one where payment_no is not null and payment_date>='2017-07-01'  and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				# seq_new=self.pool.get('ir.sequence').get(cr,uid,'bank.payment.one')
				value_id = pcof_key + bank_payment_one_id +  str(financial_year) +str(seq).zfill(5)
				existing_value_id = self.pool.get('bank.payment.one').search(cr,uid,[('payment_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + bank_payment_one_id +  str(financial_year) +str(seq+1).zfill(5)
				#value_id = pcof_key + bank_payment_one_id +  str(year1) +str(seq_new).zfill(6)

			self.write(cr,uid,ids,{'payment_no':value_id,'payment_date': payment_date})
			date = payment_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id

			for chk_ln in rec.payment_one2many:   
				if chk_ln.account_id.account_selection == 'ho_remmitance':
					self.write(cr,uid,rec.id,{'ho_remittance_check':True, 'voucher_type':'Payment (Bank - A/c-I)'})
					
				if chk_ln.account_id.account_selection == 'primary_cost_service' and chk_ln.account_id.bank_charges_bool:#a
					self.write(cr,uid,rec.id,{'bank_charges_check':True})

				if chk_ln.account_id.account_selection == 'funds_transferred_ho':
					self.write(cr,uid,rec.id,{'funds_transferred_ho_check':True})

			move = self.pool.get('account.move').create(cr,uid,{
								'journal_id':11,#Journal Hardcoded confirm from PCIL
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

		self.delete_draft_records(cr,uid,ids,context=context) ## Delete the records which are in 'Draft' State

		for payment_his in self.browse(cr,uid,ids):
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

bank_payment_one()