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

class other_payment(osv.osv):
	_inherit = 'other.payment'
	_order = 'payment_date desc'

	def process(self, cr, uid, ids, context=None):#other Payment Process Button
		post=[]
		employee_tempname= other_cost_id = move = ''
		employee_total= cr_total = dr_total = other_exp_amount = 0.0
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
				payment_date=datetime.now().date()

			for line in res.other_payment_one2many:
				if line.type == 'credit':
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				elif line.type == 'debit':
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				else:
					raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(line.account_id.name))))

				cr_total += line.credit_amount
				dr_total +=  line.debit_amount

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
		
		for rec in self.browse(cr,uid,ids):
			acc_selection_list = ['iob_one','iob_two']
			for line in rec.other_payment_one2many:
				total = 0.0
				emp_name = ""
				credit_amount = line.credit_amount
				debit_amount = line.debit_amount
				account_name = line.account_id.name
				if line.account_id.account_selection == 'expenses' and line.type=='debit':
					if line.other_expense_one2many==[]:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (line.account_id.name))
					else:
						for other_exp in line.other_expense_one2many:
							other_exp_amount=other_exp_amount+other_exp.total_amount
					if other_exp_amount!=0.0:
						print other_exp_amount,debit_amount,'lllllll'
						if round(debit_amount,2)!=round(other_exp_amount,2):
							raise osv.except_osv(('Alert!'),("Debit Amount should match with its wizard value!!"))
				if  line.account_id.account_selection in acc_selection_list:
					if line.account_id.account_selection== 'iob_one':
						payment_method=line.payment_method
						if payment_method==False or payment_method=="":
							raise osv.except_osv(('Alert'),('Enter Payment Details Details against "%s" entry to proceed.') % (account_name))
						elif payment_method=="cheque":
							if not line.other_iob_one_payment_one2many:
								raise osv.except_osv(('Alert'),('Enter Cheque Details against "%s" entry to proceed.') % (account_name))
						elif payment_method=="neft":
							if not line.other_neft_payment_one2many:
								raise osv.except_osv(('Alert'),('Enter NEFT/RTGS Details against "%s" entry to proceed.') % (account_name))
						elif payment_method=="Dd":
							if not line.demand_draft_other_one2many:
								raise osv.except_osv(('Alert'),('Enter Demand Draft Details against "%s" entry to proceed.') % (account_name))
					if line.account_id.account_selection== 'iob_two':
						if not line.other_iob_two_one2many:
							raise osv.except_osv(('Alert'),('Enter Cheque Details against "%s" entry to proceed.') % (account_name))
				if line.account_id.account_selection == 'primary_cost_cse':
					for line1 in line.other_primary_cost_one2many:
						other_cost_id = line1.other_primary_cost_id.id
						emp_name=line1.emp_name.id
						total += line1.amount

					self.write(cr,uid,rec.id,{'employee_name':emp_name})
					if not other_cost_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if credit_amount:
						if total != credit_amount:
							raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

				if line.account_id.account_selection == 'primary_cost_office':
					other_office_id = ''
					office_total = 0.0
					for office_line in line.other_office_name:
						other_office_id = office_line.other_primary_office_id.id
						office_total += office_line.amount

					if not other_office_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if credit_amount:
						if office_total != credit_amount:
							raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if office_total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

				if line.account_id.account_selection == 'primary_cost_phone':
					other_phone_id = ''
					phone_total = 0.0
					for phone_line in line.other_primary_phone_line:
						other_phone_id = phone_line.other_primary_phone_id.id
						phone_total += phone_line.amount

					if not other_phone_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if credit_amount:
						if phone_total != credit_amount:
							raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if phone_total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

				if line.account_id.account_selection == 'primary_cost_vehicle':
					other_vehicle_id = ''
					vehicle_total = 0.0
					for vehicle_line in line.other_primary_vehicle_line:
						other_vehicle_id = vehicle_line.other_primary_vehicle_id.id
						vehicle_total += vehicle_line.amount

					if not other_vehicle_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if credit_amount:
						if vehicle_total != credit_amount:
							raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if vehicle_total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

				if line.account_id.account_selection == 'primary_cost_service':
					other_service_id = ''
					service_total = 0.0
					for service_line in line.primary_other_cost_service_one2many:
						other_service_id = service_line.other_primary_service_id.id
						service_total += service_line.amount

					if not other_service_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if credit_amount:
						if service_total != credit_amount:
							raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if service_total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

				if line.account_id.account_selection == 'primary_cost_cse_office':
					other_cse_id = ''
					cse_total = 0.0
					for cse_line in line.other_primary_cse_office_one2many:
						other_cse_id = cse_line.other_primary_cse_office_id.id
						cse_total += cse_line.amount
						emp_name = cse_line.emp_name.id
					self.write(cr,uid,rec.id,{'employee_name':emp_name})

					if not other_cse_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if credit_amount:
						if service_total != credit_amount:
							raise osv.except_osv(('Alert'),('Credit Amount should be equal.'))
					if debit_amount:
						if cse_total != debit_amount:
							raise osv.except_osv(('Alert'),('Debit Amount should be equal.'))

				# 50k condition
				"""
				if line.account_id.account_selection == 'other' and line.debit_amount >= 50000 or line.credit_amount >= 50000:
					raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))"""
				balance = 0.0
				print line.account_id.account_selection, line.debit_amount, line.credit_amount
				if line.account_id.account_selection == 'cash':
					if line.debit_amount >= 10000 or line.credit_amount >= 10000:
						
						balance = line.account_id.debit - line.account_id.credit + line.account_id.balance_import
						if balance < line.credit_amount or balance < line.debit_amount:
							raise osv.except_osv(('Alert'),('Cash account dont have sufficient balance to process.'))

				print line.account_id.account_selection, line.debit_amount, line.credit_amount, balance
				if line.account_id.account_selection == 'st_input':
					other_id = ''
					phone_total = 0.0
					for line1 in line.other_st_input_one2many:
						other_id =line1.other_line_input_id

					if not other_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

				if line.account_id.account_selection == 'excise_input':
					other_id1 = ''
					phone_total = 0.0
					for line1 in line.other_excise_input_one2many:
						other_id1 =line1.other_line_excise_id

					if not other_id1:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))

	
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_other_payment_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_other_payment_tree')

			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = credit_note_id = end_year = pcof_key = ''
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','other.payment')])
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
					if comp_id.other_payment_id:
						other_payment_id = comp_id.other_payment_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			seq_start = 1	
			if pcof_key and other_payment_id:
				cr.execute("select cast(count(id) as integer) from other_payment where payment_no is not null and payment_date>='2017-07-01' and  payment_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				# seq_new=search=self.pool.get('ir.sequence').get(cr,uid,'other.payment')
				value_id = pcof_key + other_payment_id +  str(financial_year) +str(seq).zfill(5)
				#value_id = pcof_key + other_payment_id +  str(year1) +str(seq_new).zfill(6)
				existing_value_id = self.pool.get('other.payment').search(cr,uid,[('payment_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + other_payment_id +  str(financial_year) +str(seq+1).zfill(5)
				
			for chk_ln in rec.other_payment_one2many:   
				if chk_ln.account_id.account_selection == 'ho_remmitance':
					self.write(cr,uid,rec.id,{'ho_remittance_check':True})

				if chk_ln.account_id.account_selection == 'primary_cost_service' and chk_ln.account_id.bank_charges_bool:
					self.write(cr,uid,rec.id,{'bank_charges_check':True})

				if chk_ln.account_id.account_selection == 'funds_transferred_ho':
					self.write(cr,uid,rec.id,{'funds_transferred_ho_check':True})
			

			self.write(cr,uid,ids,{'payment_no':value_id,'payment_date': payment_date,'voucher_type':'Payment (other)'})
			date = payment_date######
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id

			srch_jour_other = self.pool.get('account.journal').search(cr,uid,[('name','ilike','cash')])
			for jour_other in self.pool.get('account.journal').browse(cr,uid,srch_jour_other):
				journal_other = jour_other.id

			move = self.pool.get('account.move').create(cr,uid,{
									'journal_id':journal_other,#Confirm from PCIL(JOURNAL ID)
									'state':'posted',
									'date':date,
									'name':value_id,
									'narration':rec.narration if rec.narration else '',
									'voucher_type':'Payment (other)',
									},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.other_payment_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
							'move_id':line1.id,
							'account_id':ln.account_id.id,
							'debit':ln.debit_amount,
							'name':rec.customer_name.name if rec.customer_name.name else '',
							'journal_id':journal_other,
							'period_id':period_id,
							'date':date,
							'ref':value_id},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
							'move_id':line1.id,
							'account_id':ln.account_id.id,
							'credit':ln.credit_amount,
							'name':rec.customer_name.name if rec.customer_name.name else '',
							'journal_id':journal_other,
							'period_id':period_id,
							'date':date,
							'ref':value_id},context=context)

			self.write(cr,uid,rec.id,{'state':'done'})
			for update in rec.other_payment_one2many:
				self.pool.get('other.payment.line').write(cr,uid,update.id,{'state':'done'})

			for i in rec.other_payment_one2many:
				search_temp=self.pool.get('st.input').search(cr,uid,[('other_line_input_id','=',i.id)])
				for j in self.pool.get('st.input').browse(cr,uid,search_temp):
					self.pool.get('st.input').write(cr,uid,j.id,{'account_id':i.account_id.id})
				search_temp1=self.pool.get('st.input').search(cr,uid,[('other_line_excise_id','=',i.id)])
				for k in self.pool.get('st.input').browse(cr,uid,search_temp1):
					self.pool.get('st.input').write(cr,uid,k.id,{'account_id':i.account_id.id})

		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
		for payment_his in self.browse(cr,uid,ids):
			curr_id = ''
			cust_name=payment_his.customer_name.name
			if  payment_his.payment_date:
				payment_date=payment_his.payment_date
			else:	
				payment_date=datetime.now().date()
			payment_type='CASH'
			particulars=payment_his.particulars.name
			for payment_line in payment_his.other_payment_one2many:
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

			srch = self.pool.get('other.payment.line').search(cr,uid,[('other_payment_id','=',rec.id)])
			for i in self.pool.get('other.payment.line').browse(cr,uid,srch):
				temp=i.account_id.advance_expence_check
				if  i.account_id.account_selection == 'primary_cost_cse' and temp == True:
					for j in self.pool.get('other.payment.line').browse(cr,uid,srch):
						if j.account_id.account_selection == 'cash':
							for k in i.other_primary_cost_one2many:
								employee_tempname = k.emp_name.id
								employee_total = k.amount
								if i.debit_amount:
									for emp in self.pool.get('hr.employee').browse(cr,uid,[employee_tempname]):
										employee_total += emp.debit
									self.pool.get('hr.employee').write(cr,uid,employee_tempname,{'debit':employee_total})
								if i.credit_amount:
									for emp in self.pool.get('hr.employee').browse(cr,uid,[employee_tempname]):
										employee_total +=  emp.credit
									self.pool.get('hr.employee').write(cr,uid,employee_tempname,{'credit':employee_total})

		return {
				'name':'Other Payment',
				'view_mode': 'form',
				'view_id': False,
				'view_type': 'form',
				'res_model': 'other.payment',
				'res_id':rec.id,
				'type': 'ir.actions.act_window',
				'target': 'current',
				'domain': '[]',
				'context': context,
				}
other_payment()

class other_payment_line(osv.osv):

	_inherit = 'other.payment.line'
	_rec_name = 'type'
	_columns = {
		'other_expense_one2many':fields.one2many('expense.payment','other_payment_expense_id','Expenses'),
	}

	def add(self, cr, uid, ids, context=None): # other Payment (arrow add button)
		total=total_amount=0.0
		temp=[]
		acc_selection_list=['primary_cost_phone','primary_cost_cse','primary_cost_office',
					   'primary_cost_vehicle','primary_cost_service','primary_cost_cse_office']
		acc_selection_list2 = ['st_input','excise_input','iob_two','iob_one','itds']
		for res in self.browse(cr,uid,ids):
			acc_selection = res.account_id.account_selection
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			res_id = res.id
			if acc_selection == 'expenses':
				objt = 'gst_accounting'
				view_name2 = 'expense_other_form'
				name_wizard = "Add Expenses Details"
				models_data = self.pool.get('ir.model.data')
				form_view = models_data.get_object_reference(cr, uid, objt, view_name2)
				return {
						'name': (name_wizard),
						'type': 'ir.actions.act_window',
						'view_id': False,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'other.payment.line',
						'target' : 'new',
						'res_id': int(res_id),
						'views': [(form_view and form_view[1] or False, 'form'),
								  (False, 'calendar'), (False, 'graph')],
						'domain': '[]',
						'nodestroy': True
					}
			if acc_selection in acc_selection_list2:

				if acc_selection == 'st_input':
					view_name = 'account_other_st_input_form'
					name_wizard = "Add ST Input Details"
					
				if acc_selection == 'excise_input':
					view_name = 'account_other_excise_input_form'
					name_wizard = "Add Excise Input Details"
					
				if acc_selection == 'iob_two':
					view_name = 'account_iob_two_other_form'
					name_wizard = "Add"+" "+ res.account_id.name +" "+" Details"
					
				if acc_selection == 'iob_one':
					view_name =  'account_iob_one_other_payment_form'
					name_wizard = "Add"+" "+ res.account_id.name +" "+" Details"
					
				if acc_selection == 'itds':
					view_name =  'account_itds_other_form'
					name_wizard = "Add ITDS on Contract Payments Details"
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name)
				return {
					'name': (name_wizard),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'other.payment.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					   }
	
			if acc_selection in acc_selection_list:
				if acc_selection == 'primary_cost_cse':
					view_name2 = 'account_other_primary_cost_form'
					
				if acc_selection == 'primary_cost_office':
					view_name2 = 'account_other_primary_cost_office_form'
					
	
				if acc_selection == 'primary_cost_phone':
					view_name2 = 'account_other_primary_cost_phone_form'
					
				if acc_selection == 'primary_cost_vehicle':
					view_name2 = 'account_other_primary_cost_vehicle_form'
	
				if acc_selection == 'primary_cost_service':
					view_name2 = 'account_primary_cost_other_service_form'
					
				if acc_selection == 'primary_cost_cse_office':
					view_name2 = 'account_primary_cost_cse_office_other_form'
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name2)
				return {
					'name': ("Add Primary Cost Category"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'other.payment.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					   }

	def save_expense_entry(self, cr, uid, ids, context=None):
		amount = 0.0
		total_amount = 0.0
		tax_amount = 0.0
		for rec in self.browse(cr,uid,ids):
			if rec.other_expense_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.other_expense_one2many:
				if line.bill_value:
					tax_amount = (line.bill_value * float(line.gst_item_master.item_rate))/100
					amount = (line.bill_value*float(line.gst_item_master.item_rate))/100 + line.bill_value
					total_amount =total_amount+amount
					self.pool.get('expense.payment').write(cr,uid,line.id,{'total_amount':amount,'tax_amount':tax_amount})
			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':total_amount})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':total_amount})
		return {'type': 'ir.actions.act_window_close'}

other_payment_line()