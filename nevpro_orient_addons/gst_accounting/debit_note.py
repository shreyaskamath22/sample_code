# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from osv import osv,fields
# from datetime import date,datetime, timedelta
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

class debit_note(osv.osv):
	_inherit = 'debit.note'
	_order = 'debit_note_date desc'

	_columns = {
		'gst_debit_note':fields.boolean('GST Debit Note?'),
	}
	
	def add_debit_note(self, cr, uid, ids, context=None):
		tax_rate=''
		for res in self.browse(cr,uid,ids):
			account_id = res.account_id.id
			account_selection =self.pool.get('account.account').browse(cr,uid,account_id).account_selection
			if res.type=='debit' and account_selection=='against_ref':
				account_name=res.account_id.name
				tax_list=['10.20','10.30','12.24','12.36','14.0','14.5','15.0','Non Taxable', 'Others','18.0']
				if tax_list[0] in account_name:
					tax_rate='10.20'
				elif tax_list[1] in account_name :
					tax_rate='10.30'
				elif tax_list[2] in account_name :
					tax_rate='12.24'
				elif tax_list[3] in account_name :
					tax_rate='12.36'
				elif tax_list[4] in account_name :
					tax_rate='14.0'
				elif tax_list[5] in account_name :
					tax_rate='14.5'
				elif tax_list[6] in account_name :
					tax_rate='15.0'
				elif tax_list[7] in account_name :
					tax_rate='non_taxable'
				elif tax_list[8] in account_name :
					tax_rate='Others'
				elif tax_list[9] in account_name :
					tax_rate='18.0'
			for i in res.debit_note_one2many:
				if res.account_id.id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

			if not res.account_id.id:
				raise osv.except_osv(('Alert'),('Please select Account Name.'))
				
			if res.account_id.account_selection in ('iob_one','iob_two','cash'):
				raise osv.except_osv(('Alert'),('Account is not available for this entry.'))
				
			if not res.type:
				raise osv.except_osv(('Alert'),('Please select Type.'))
				
			if res.account_id.account_selection == 'against_ref':
			        if res.type == 'debit':
			                cr.execute("update invoice_adhoc_master set check_debit_note = False where status='paid' and check_process_credit_note = False and check_debit_note = True and invoice_number is not Null")
                                else:
                                        raise osv.except_osv(('Alert'),('Please select Type as Debit.'))
                                
			if res.debit_note_one2many != []:
			   for line in res.debit_note_one2many:
				flag = False 
				if line.account_id.account_selection == 'against_ref':
					for ln in line.debit_outstanding_invoice:
						if ln.check_debit_note == True:
							flag = True
							if ln.invoice_number:
								for adhoc_ln in ln.invoice_line_adhoc_11:
									pms = adhoc_ln.pms.id
									if res.account_id.product_id:
										if pms == res.account_id.product_id.id:
											amount = adhoc_ln.amount
										else:
											raise osv.except_osv(('Alert'),('Please select proper Account Name.'))
                                                                for adhoc_ln in ln.invoice_line_adhoc:
									pms1 = adhoc_ln.pms.id
									if res.account_id.product_id:
										if pms1 == res.account_id.product_id.id:
											amount = adhoc_ln.amount
										else:
											raise osv.except_osv(('Alert'),('Please select proper Account Name.'))
			debit = credit = 0.0
			for j in res.debit_note_one2many:
				v={}
				if j.type=='credit':
					credit += j.credit_amount
				if j.type=='debit':
					debit += j.debit_amount
					
		        if debit >= credit:
			        amount = debit - credit
			else:
			        amount = credit - debit
			self.pool.get('debit.note.line').create(cr,uid,{
			                                                'credit_amount': amount if res.type =='credit' else 0.0,
			                                                'debit_amount':amount if res.type =='debit' else 0.0,
									'debit_id':res.id,
									'account_id':res.account_id.id,
									'status':res.status,
									'type':res.type,
									'customer_name':res.customer_name.id,
									'tax_rate':tax_rate,
									 })

			self.write(cr,uid,res.id,{'account_id':None,'type':''})
		
		return True

	def gen_report(self,cr,uid,ids,context=None):
		if (isinstance(ids,int)):
			ids = [ids]
		for res in self.browse(cr,uid,ids):
			data = self.pool.get('debit.note').read(cr, uid, [res.id], context)
			datas = {
						'ids': ids,
						'model': 'debit.note',
						'form': data
					}
			if res.gst_debit_note == False:
				return {
							'type': 'ir.actions.report.xml',
							'report_name': 'debit_note_report1',
							'datas': datas,
					   }
			else:
				return {
							'type': 'ir.actions.report.xml',
							'report_name': 'gst_debit_note_report',
							'datas': datas,
					   }

	def process(self, cr, uid, ids, context=None):
		cr_total = dr_total = grand_total = 0.0
		move = debit_invoice_id=''
		post=[]
		today_date = datetime.now().date()
		flag = py_date = False
		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			if res.debit_note_date:
				check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
				if check_bool:
					if res.debit_note_date != str(today_date):
						raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
				py_date = str(today_date + relativedelta(days=-5))
				if res.debit_note_date < str(py_date) or res.debit_note_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Date 5 days earlier from current date.'))
				debit_note_date=res.debit_note_date	
			else:
				debit_note_date=datetime.now().date()
			for line in res.debit_note_one2many:
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
			if dr_total != cr_total:
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))
		for res in self.browse(cr,uid,ids):
			for line in res.debit_note_one2many:
				account_name = line.account_id.name
				if line.account_id.account_selection == 'against_ref':
					if line.debit_outstanding_invoice:
						for invoice_line in line.debit_outstanding_invoice:
							debit_invoice_id =  invoice_line.debit_invoice_id.id
							if invoice_line.check_debit_note == True:
								flag = True
								grand_total += invoice_line.grand_total
					flag=False
					if line.debit_paid_receipt_one2many:
						for invoice_line in line.debit_paid_receipt_one2many:
							if invoice_line.check_invoice == True:
								flag=True
						for invoice_line in line.debit_paid_receipt_one2many:
							if invoice_line.check_invoice == True:
								self.pool.get('invoice.receipt.history').write(cr,uid,invoice_line.id,{'debit_note_process':'True','refund_date':debit_note_date })
								amount=(invoice_line.invoice_receipt_history_id.pending_amount)+invoice_line.invoice_paid_amount
								self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.invoice_receipt_history_id.id,
									{
										'pending_amount':amount,
										'status':'printed',
										'pending_status':'pending',
										'check_process_invoice':False
									})
		self.pms_validation(cr,uid,ids,context=context)
		for rec in self.browse(cr,uid,ids):
			amount = total = 0.0
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_debit_note_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_debit_note_tree')
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
			search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','debit.note')])
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
					if comp_id.credit_note_id:
						debit_note_id = comp_id.debit_note_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
			count = 0
			seq_start = 1
			if pcof_key and debit_note_id:
				cr.execute("select cast(count(id) as integer) from debit_note where debit_note_no is not null and debit_note_date>='2017-07-01' and  debit_note_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
			temp_count=cr.fetchone()
			if temp_count[0]:
				count= temp_count[0]
			seq=int(count+seq_start)
			value_id = pcof_key + debit_note_id +  str(financial_year) +str(seq).zfill(5)
			existing_value_id = self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',value_id)])
			if existing_value_id:
				value_id = pcof_key + debit_note_id +  str(financial_year) +str(seq+1).zfill(5)
			self.write(cr,uid,ids,{'debit_note_no':value_id,'debit_note_date': debit_note_date,'cust_name':rec.customer_name.name,'voucher_type':'Debit Note'})
			for res in self.browse(cr,uid,ids):
				for line in res.debit_note_one2many:
					account_name = line.account_id.name
					cse=''
					service_classification=''
					full_name = ''
					service_classification=''
					if line.account_id.account_selection == 'against_ref':
						if line.type=='debit':
							if not line.debit_paid_receipt_one2many:
								raise osv.except_osv(('Alert!'),('Please enter the details  against "%s" entry to proceed.')%(line.account_id.name))
						if line.debit_paid_receipt_one2many:
							for invoice_line in line.debit_paid_receipt_one2many:
								if invoice_line.cse:
									cse=invoice_line.cse.name
									cse_id=invoice_line.cse.id
									for x in  self.pool.get('hr.employee').browse(cr,uid,[cse_id]):
										middle_name = x.middle_name if x.middle_name else ''
										last_name = x.last_name if x.last_name else ''
										full_name = invoice_line.cse.name + " " + middle_name + " " + last_name
								service_classification=invoice_line.service_classification
								self.pool.get('invoice.receipt.history').write(cr,uid,invoice_line.id,{'receipt_number':value_id,'tax_rate':line.tax_rate})
								self.write(cr,uid,res.id,{'cse':full_name,'service_classification':service_classification,'tax_rate':line.tax_rate})
			date = debit_note_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id
			srch_jour_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
			for jour_acc in self.pool.get('account.journal').browse(cr,uid,srch_jour_acc):
				journal_id = jour_acc.id
			move = self.pool.get('account.move').create(cr,uid,
				{
					'journal_id':journal_id,
					'state':'posted',
					'date':date,
					'name':value_id,
					'narration':rec.narration if rec.narration else '',
					'voucher_type':'Debit Note',
				},context=context)
			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in rec.debit_note_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,
							{
								'move_id':line1.id,
								'account_id':ln.account_id.id,
								'debit':ln.debit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_id,
								'period_id':period_id,
								'date':date,
								'ref':value_id
							},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,
							{
								'move_id':line1.id,
								'account_id':ln.account_id.id,
								'credit':ln.credit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_id,
								'period_id':period_id,
								'date':date,
								'ref':value_id
							},context=context)
			self.write(cr,uid,rec.id,{'state':'done','status':'','state_new':'open'})
			for line_state in rec.debit_note_one2many:
				self.pool.get('debit.note.line').write(cr,uid,line_state.id,{'state':'done'})
				for chk in line_state.debit_outstanding_invoice:
					check_debit_note = chk.check_debit_note
					if check_debit_note == True:
						self.pool.get('invoice.adhoc.master').write(cr,uid,chk.id,{'check_process_debit_note':True})
		cr_total = dr_total = 0.0
		for res in self.browse(cr,uid,ids):
			if res.debit_note_one2many:
				for line in res.debit_note_one2many:
					cr_total += line.credit_amount
					dr_total +=  line.debit_amount
		cr.execute("update debit_note set debit_amount_srch = %s,credit_amount_srch = %s where id=%s",(dr_total,cr_total,res.id))
		cr.execute("update debit_note set pending_amount=credit_amount_srch where state_new='open'")
		self.delete_draft_records(cr,uid,ids,context=context) 
		for debitnote_his in self.browse(cr,uid,ids):
			cust_name=debitnote_his.customer_name.name
			debitnote_date=debitnote_his.debit_note_date
			for debitnote_line in debitnote_his.debit_note_one2many:
				amount=debitnote_line.debit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('debit.note.history').create(cr,uid,
				{
					'debit_note_his_many2one':curr_id,
					'debit_note_number':value_id,
					'debit_note_date':debit_note_date,
					'debit_note_amount':amount
				})
		self.sync_debit_note_history(cr,uid,ids,context=context)
		self.write(cr,uid,ids[0],{'gst_debit_note': True})
		return  {
			'name':'Debit Note',
			'view_mode'	: 'form',
			'view_id'	: False,
			'view_type'	: 'form',
			'res_model'	: 'debit.note',
			'res_id'	:rec.id,
			'type'		: 'ir.actions.act_window',
			'target'	: 'current',
			'domain'	: '[]',
			'context'	: context,
		}

debit_note()