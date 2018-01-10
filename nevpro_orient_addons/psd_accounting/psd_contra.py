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

from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
from dateutil.relativedelta import relativedelta
import calendar
import re
from base.res import res_company as COMPANY
from base.res import res_partner
from collections import Counter
import xmlrpclib
import math
import os
from tools.translate import _
from datetime import date,datetime, timedelta
from osv import osv,fields
import time 
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import calendar
import re
from base.res import res_partner
import decimal_precision as dp
import xlsxwriter
import xlsxwriter as xls
from dateutil.relativedelta import relativedelta
import pdb


class contra_entry(osv.osv):
	_inherit = 'contra.entry'

	_columns = {
		'psd_accounting': fields.boolean('PSD Accounting')
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(contra_entry, self).default_get(cr, uid, fields, context=context)
		if context.has_key('psd_accounting'):
			psd_accounting = context.get('psd_accounting')
		else:
			psd_accounting = False
		res.update({'psd_accounting': psd_accounting})
		return res
	
	def psd_add_contra(self, cr, uid, ids, context=None):
			for res in self.browse(cr,uid,ids):
				account_id = res.account_id.id
				types = res.type
				contra_type = res.contra_type
				auto_debit_total=auto_credit_total=auto_credit_cal=auto_debit_cal=0.0	
				account_id1=res.account_id
				if res.type == "debit" and res.contra_type=="cash_deposit" and res.account_id.account_selection == "cash":
					raise osv.except_osv(('Alert'),('Cash cannot be debited.'))
				elif res.type == "credit" and res.contra_type=="cash_withdrawal" and res.account_id.account_selection == "cash":
					raise osv.except_osv(('Alert'),('Cash cannot be credited.'))
				for i in res.contra_one2many:
					if account_id1.id==i.account_id.id:
						raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
				if not account_id:
					raise osv.except_osv(('Alert'),('Please select Account Name.'))
				if not types:
					raise osv.except_osv(('Alert'),('Please select Type.'))
				if res.account_id.account_selection  == 'iob_one':
					if res.type=='debit':
						raise osv.except_osv(('Alert'),('Bank Account cannot be debited.'))			
				if  res.account_id.account_selection in ( 'iob_two' ,'iob_one','cash'):
						if res.type=='debit':
							for j in res.contra_one2many:
								if j.type=='credit':
									auto_debit_total += j.credit_amount
								if j.type=='debit':
									auto_credit_total += j.debit_amount
							if auto_debit_total > auto_credit_total:
								auto_debit_total -= auto_credit_total
							else:		
								auto_debit_total=0.0
						else:	
							for k in res.contra_one2many:
								if k.type=='credit':
									auto_debit_cal += k.credit_amount
								if k.type=='debit':
									auto_credit_cal += k.debit_amount
							if auto_debit_cal < auto_credit_cal:
								auto_credit_cal -= auto_debit_cal
							else:
								auto_credit_cal=0.0

				self.pool.get('contra.entry.line').create(cr,uid,{
									'contra_entry_id':res.id,
									'account_id':account_id,
									'type':types,
									'contra_type':contra_type,
									'debit_amount':auto_debit_total,
									'credit_amount':auto_credit_cal,
								    })
										    
				self.write(cr,uid,res.id,{'account_id':None,'type':''})
			return True
     
	def psd_change_account_type_new(self, cr, uid, ids, contra_type,account_id, context=None):
		v = {}
		acc_type = ''
		if account_id == 'cash' and contra_type=='cash_deposit':
			search = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)]) 
			for k in  self.pool.get('account.account').browse(cr,uid,search):
				if k.account_selection == 'cash':        
					acc_type = 'credit'
			v['type']= acc_type
		elif account_id=='cash' and contra_type=='cash_withdrawal':
			search = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)]) 
			for k in  self.pool.get('account.account').browse(cr,uid,search):
				if k.account_selection == 'cash':        
					acc_type = 'debit'
			v['type']= acc_type	

		if account_id:
			if contra_type=='cash_deposit':
				search = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)]) 
				for k in  self.pool.get('account.account').browse(cr,uid,search):
					if k.account_selection == 'cash':        
						acc_type = 'credit'
					if k.account_selection == 'iob_one':        
						acc_type = 'debit'
				v['type']= acc_type

			if contra_type=='cash_withdrawal':
					search = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)]) 
					for k in  self.pool.get('account.account').browse(cr,uid,search):
						if k.account_selection == 'cash':        
								acc_type = 'debit'
						if k.account_selection == 'iob_two':        
								acc_type = 'credit'
					v['type']= acc_type
					
			if contra_type=='transfer_one_to_two':
					search = self.pool.get('account.account').search(cr,uid,[('id','=',account_id)]) 
					for k in  self.pool.get('account.account').browse(cr,uid,search):
						if k.account_selection == 'iob_two':        
							acc_type = 'debit'
						if k.account_selection == 'iob_one':        
							acc_type = 'credit'
					v['type']= acc_type
					   
		else:
			v['type']= ''
				
		return {'value':v}        

	
	def psd_process(self, cr, uid, ids, context=None):
		cr_total = dr_total = cheque_amount_one = cheque_amount_two = 0.0
		move = contra_iob_two_id = cheque_no = contra_iob_one_id = ''
		post=[]
		status=[]
		today_date = datetime.now().date()
		py_date = False
		models_data=self.pool.get('ir.model.data')
		for res1 in self.browse(cr,uid,ids):
			if res1.contra_date:
				py_date = str(today_date + relativedelta(days=-5))
				if res1.contra_date < str(py_date) or res1.contra_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Date 5 days earlier from current date.'))
				contra_date=res1.contra_date
			else:
				contra_date=datetime.now().date()
			if not res1.contra_type:
				raise osv.except_osv(('Alert'),('Select contra type.'))
			# if res1.account_id == "cash" and res1.type == "debit":
			# 	raise osv.except_osv(('Alert'),('Cash cannot be debited.'))
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
			form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_contra_form')
			tree_view=models_data.get_object_reference(cr, uid, 'psd_accounting', 'psd_account_contra_tree')
			
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
			if pcof_key and contra_id:
				cr.execute("select cast(count(id) as integer) from contra_entry where contra_no is not null   and  contra_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + contra_id +  str(year1) +str(seq).zfill(6)

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
			self.write(cr,uid,res.id,{'state':'done','contra_type':'','bank_reco_date':res.contra_date})

			for res in self.browse(cr,uid,ids):
				if res.state == 'done' :
					for ln in res.contra_one2many:
						self.pool.get('contra.entry.line').write(cr,uid,ln.id,{'state1':'done'})  

		self.delete_draft_records(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State

		return {
			'name':'Contra Entry',
			'view_mode': 'tree,form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'contra.entry',
			'res_id':res.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
			}
contra_entry()

class contra_entry_line(osv.osv):
	_inherit= 'contra.entry.line'

	def add(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			acc_selection = res.account_id.account_selection
			# search = self.pool.get('contra.entry.line').search(cr,uid,[('id','=',res_id)])
			obj = self.pool.get('contra.entry.line').browse(cr,uid,[res_id])
			acc_selection_list = ['iob_one','iob_two']

			if acc_selection in acc_selection_list:
				if acc_selection == 'iob_one':
					for rec in obj:
						if rec.contra_type in ('cash_deposit','cash_withdrawal') :
							raise osv.except_osv(('Alert'),('No Information to process.'))
				
						if rec.contra_type == 'transfer_one_to_two' :
							view_name = 'contra_iob_one_form'

				elif acc_selection == 'iob_two':
					for rec in obj:
						if rec.contra_type in ('transfer_one_to_two','cash_deposit'):
								raise osv.except_osv(('Alert'),('No Information to process.'))
						else:
							view_name = 'contra_iob_two_form'
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', view_name)
				return {
					'name': ("Add"+" "+ res.account_id.name +" "+"Details"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'contra.entry.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
				}
		return True

	def psd_add(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			acc_selection = res.account_id.account_selection
			# search = self.pool.get('contra.entry.line').search(cr,uid,[('id','=',res_id)])
			obj = self.pool.get('contra.entry.line').browse(cr,uid,[res_id])
			acc_selection_list = ['iob_one','iob_two']

			if acc_selection in acc_selection_list:
				if acc_selection == 'iob_one':
					for rec in obj:
						if rec.contra_type in ('cash_deposit','cash_withdrawal') :
							raise osv.except_osv(('Alert'),('No Information to process.'))
				
						if rec.contra_type == 'transfer_one_to_two' :
							view_name = 'psd_contra_iob_one_form'

				elif acc_selection == 'iob_two':
					for rec in obj:
						if rec.contra_type in ('transfer_one_to_two','cash_deposit'):
								raise osv.except_osv(('Alert'),('No Information to process.'))
						else:
							view_name = 'psd_contra_iob_two_form'
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'psd_accounting', view_name)
				return {
					'name': ("Add"+" "+ res.account_id.name +" "+"Details"),'domain': '[]',
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'contra.entry.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							   (False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
				}

		return True
contra_entry_line()
