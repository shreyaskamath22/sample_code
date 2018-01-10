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

class cotra_entry(osv.osv):
	_inherit='contra.entry'
	_order = 'contra_date desc'

	def process(self, cr, uid, ids, context=None):
		cr_total = dr_total = cheque_amount_one = cheque_amount_two = 0.0
		move = contra_iob_two_id = cheque_no = contra_iob_one_id = ''
		post=[]
		status=[]
		today_date = datetime.now().date()
		py_date = False
		models_data=self.pool.get('ir.model.data')
		for res1 in self.browse(cr,uid,ids):
			if res1.contra_date:
				check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
			        if check_bool:
			                if res1.contra_date != str(today_date):
        				        raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
				py_date = str(today_date + relativedelta(days=-5))
				if res1.contra_date < str(py_date) or res1.contra_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Date 5 days earlier from current date.'))
				contra_date=res1.contra_date
			else:
				contra_date=datetime.now().date()
			if res1.contra_one2many == []:
				raise osv.except_osv(('Alert'),('No Details to proceed.'))
			for line1 in res1.contra_one2many:
				cr_total += line1.credit_amount
				dr_total +=  line1.debit_amount

				account_id = line1.account_id.id
				temp = tuple([account_id])
				post.append(temp)
				for i in range(0,len(post)):	
					for j in range(i+1,len(post)):
						if post[i][0]==post[j][0]:
							raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

				acc_status = line1.contra_type
				if acc_status:
					temp = tuple([acc_status])
					status.append(temp)
					for i in range(0,len(status)):
						for j in range(i+1,len(status)):
							if status[i][0] != status[j][0]:
									raise osv.except_osv(('Alert!'),('Status should be same.'))

			if dr_total != cr_total:
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
			
		for res in self.browse(cr,uid,ids):
			for line in res.contra_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name

				if line.credit_amount:
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				if line.debit_amount:
					if line.debit_amount == 0.0:
					   raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				if acc_selection == 'iob_one' and res.contra_type=='transfer_one_to_two':
					for iob_one_line in line.contra_iob_one_one2many:
						cheque_no = iob_one_line.cheque_no
						contra_iob_one_id = iob_one_line.contra_iob_one_id.id
						cheque_amount_one += iob_one_line.cheque_amount

						if not iob_one_line.cheque_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not iob_one_line.cheque_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not iob_one_line.drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not iob_one_line.bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))

						if cheque_no:                 
							for n in str(cheque_no):
								p = re.compile('([0-9]{6}$)')
								if p.match(cheque_no)== None :
									raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
							
					if not contra_iob_one_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed')%(account_name))
					elif contra_iob_one_id:
						if line.debit_amount:
							if cheque_amount_one != line.debit_amount:
								raise osv.except_osv(('Alert'),('Debit amount should be equal'))
						if line.credit_amount:
							if cheque_amount_one != line.credit_amount:
								raise osv.except_osv(('Alert'),('Credit amount should be equal'))
									
				if acc_selection == 'iob_two' and res.contra_type=='cash_withdrawal':
					for iob_two_line in line.contra_iob_two_one2many:
						if not iob_two_line.drawee_bank_name_new:
							raise osv.except_osv(('Alert!'),('Please provide Drawee Bank Name.'))
						if not iob_two_line.bank_branch_name:
							raise osv.except_osv(('Alert!'),('Please provide Bank Branch Name.'))

						cheque_no = iob_two_line.cheque_no
						contra_iob_two_id = iob_two_line.contra_iob_two_id.id
						cheque_amount_two += iob_two_line.cheque_amount

						if cheque_no:            
							for n in str(cheque_no):
								p = re.compile('([0-9]{6}$)')
								if p.match(cheque_no)==None:
									raise osv.except_osv(('Alert'),('Please Enter 6 digit Cheque Number.'))
								
					if not contra_iob_two_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.')%(account_name))
					elif contra_iob_two_id:
							if line.debit_amount:
								if cheque_amount_two != line.debit_amount:
										raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if line.credit_amount:
								if cheque_amount_two != line.credit_amount:
										raise osv.except_osv(('Alert'),('Credit amount should be equal'))
									
## update bank_reco_date in cash withdrawal as contra date on 24 Feb by Vijay
				if acc_selection == 'iob_two' and res.contra_type=='cash_withdrawal':
					for iob_two_line in line.contra_iob_two_one2many:
						self.pool.get('iob.two.payment').write(cr,uid,iob_two_line.id,{'bank_reco_date':contra_date})
						
		for res in self.browse(cr,uid,ids):
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_contra_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_contra_tree')
			
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			
			pcof_key = credit_note_id = end_year = start_year = ''
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','contra.entry')])
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
					if comp_id.contra_id:
						contra_id = comp_id.contra_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
			
			year = today_date.strftime('%y')

			count = 0
			seq_start = 1
			if pcof_key and contra_id:
				cr.execute("select cast(count(id) as integer) from contra_entry where contra_no is not null and contra_date>='2017-07-01' and  contra_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				#seq_new=self.pool.get('ir.sequence').get(cr,uid,'contra.entry')
				value_id = pcof_key + contra_id +  str(financial_year) +str(seq).zfill(5)
				#value_id = pcof_key + contra_id +  str(year1) +str(seq_new).zfill(6)
				existing_value_id = self.pool.get('contra.entry').search(cr,uid,[('contra_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + contra_id +  str(financial_year) +str(seq+1).zfill(5)

			self.write(cr,uid,ids,{'contra_no':value_id,'contra_date': contra_date,'voucher_type':'Contra'})
			date = contra_date
			
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id
				
			srch_jour_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
			for jour_acc in self.pool.get('account.journal').browse(cr,uid,srch_jour_acc):
				journal_id = jour_acc.id
				
			move = self.pool.get('account.move').create(cr,uid,{
							'journal_id':journal_id,#hardcoded not confirm by pcil
							'state':'posted',
							'date':date,
							'name':value_id,
							'narration':res.narration if res.narration else '',
							'voucher_type':'Contra',
							},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.contra_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
							'account_id':ln.account_id.id,
							'debit':ln.debit_amount,
							'name':' ',
							#'name':res.customer_name.name if res.customer_name.name else '',
							'journal_id':journal_id,
							'period_id':period_id,
							'date':date,
							'ref':value_id},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
							'account_id':ln.account_id.id,
							'credit':ln.credit_amount,
							'name':' ',
							#'name':res.customer_name.name if res.customer_name.name else '',
							'journal_id':journal_id,
							'period_id':period_id,
							'date':date,
							'ref':value_id},context=context)

			self.write(cr,uid,res.id,{'search_contra_type':res.contra_type})
			self.write(cr,uid,res.id,{'state':'done','contra_type':''})

			for res in self.browse(cr,uid,ids):
				if res.state == 'done' :
					for ln in res.contra_one2many:
						self.pool.get('contra.entry.line').write(cr,uid,ln.id,{'state1':'done'})  

		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State

		return {
			'name':'Contra Entry',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'contra.entry',
			'res_id':res.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
			}

cotra_entry()