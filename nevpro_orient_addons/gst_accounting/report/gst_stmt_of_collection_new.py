# Version 1.0.050 - changes related to imported advance reflecting -->
# version 1.0.054 --> Changes Related to Non-Taxable transaction process

import pdb
import time
from report import report_sxw
from tools.translate import _
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in
from corporate_address import *

class total_amount_sum :
	sum_amount=sum_amount1=sum_amount2=sum_amount3=sum_amount4=sum_amount5=sum_amount6=sum_amount7=sum_amount8=sum_amount9=sum_amount10=sum_amount11=sum_amount12=sum_amount13=sum_amount14=sum_amount15=0 ## for 14.0 % HHH

class gst_statement_of_collection_new(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(gst_statement_of_collection_new, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'amount_to_text_in': amount_to_text_in,
			'get_account_name': self.get_account_name,
			'get_branch_addr' : self.get_branch_addr,
			'set_page_total' : self.set_page_total,
			'get_page_total' : self.get_page_total,
			'set_to_zero' : self.set_to_zero,
			'get_current_time':self.get_current_time,
		})

##########################################################################################################################################

	def get_branch_addr(self,self_id):
		return get_branch_addr(self,self_id)

	def set_page_total(self,new_amount,new_amount1,new_amount2,new_amount3,new_amount4,new_amount5,new_amount6,new_amount7,new_amount8,new_amount9,new_amount10,new_amount11,new_amount12,new_amount13,new_amount14,new_amount15,remark,party_name) :  ## for 14.0 % HHH
		cr=self.cr
		uid=self.uid
		print"RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR",remark,party_name
		total_amount_sum.sum_amount =total_amount_sum.sum_amount + new_amount
		total_amount_sum.sum_amount1 =total_amount_sum.sum_amount1 + new_amount1
		total_amount_sum.sum_amount2 =total_amount_sum.sum_amount2 + new_amount2
		total_amount_sum.sum_amount3 =total_amount_sum.sum_amount3 + new_amount3
		total_amount_sum.sum_amount4 =total_amount_sum.sum_amount4 + new_amount4
		total_amount_sum.sum_amount5 =total_amount_sum.sum_amount5 + new_amount5
		total_amount_sum.sum_amount6 =total_amount_sum.sum_amount6 + new_amount6
		total_amount_sum.sum_amount7 =total_amount_sum.sum_amount7 + new_amount7
		total_amount_sum.sum_amount8 =total_amount_sum.sum_amount8 + new_amount8
		total_amount_sum.sum_amount9 =total_amount_sum.sum_amount9 + new_amount9
		total_amount_sum.sum_amount10 =total_amount_sum.sum_amount10 + new_amount10
		total_amount_sum.sum_amount11 =total_amount_sum.sum_amount11 + new_amount11 ## for 14.0 % HHH
		total_amount_sum.sum_amount12 =total_amount_sum.sum_amount12 + new_amount12 ## for non taxable
		total_amount_sum.sum_amount13 =total_amount_sum.sum_amount13 + new_amount13  # for 14.50% sagar
		total_amount_sum.sum_amount14 =total_amount_sum.sum_amount14 + new_amount14
		total_amount_sum.sum_amount15 =total_amount_sum.sum_amount15 + new_amount15
		return
		
	def get_page_total(self,self_id) :
		cr=self.cr
		uid=self.uid
		dic = {
			'new_amount':'',
			'new_amount1':'',
			'new_amount2':'',
			'new_amount3':'',
			'new_amount4':'',
			'new_amount5':'',
			'new_amount6':'',
			'new_amount7':'',
			# 'new_amount8':'',
			'new_amount9':'',
			'new_amount10':'',
			'new_amount11':'', ## for 14.0 % HHH
			'new_amount12':'',			
			'new_amount13':'', #  for 14.50% sagar
			'new_amount14':'',
			'new_amount15':'',
			}
		dic['new_amount'] = format(total_amount_sum.sum_amount,'.2f')
		dic['new_amount1'] = format(total_amount_sum.sum_amount1,'.2f')
		dic['new_amount2'] = format(total_amount_sum.sum_amount2,'.2f')
		dic['new_amount3'] = format(total_amount_sum.sum_amount3,'.2f')
		dic['new_amount4'] = format(total_amount_sum.sum_amount4,'.2f')
		dic['new_amount5'] = format(total_amount_sum.sum_amount5,'.2f')
		dic['new_amount6'] = format(total_amount_sum.sum_amount6,'.2f')
		dic['new_amount7'] = format(total_amount_sum.sum_amount7,'.2f')
		# dic['new_amount8'] = format(total_amount_sum.sum_amount8,'.2f')
		dic['new_amount9'] = format(total_amount_sum.sum_amount9,'.2f')
		dic['new_amount10'] = format(total_amount_sum.sum_amount10,'.2f')
		dic['new_amount11'] = format(total_amount_sum.sum_amount11,'.2f') ## for 14.0 % HHH
		dic['new_amount12'] = format(total_amount_sum.sum_amount12,'.2f') ## for Non Taxable
		dic['new_amount13'] = format(total_amount_sum.sum_amount13,'.2f')  #  for 14.50% sagar
		dic['new_amount14'] = format(total_amount_sum.sum_amount14,'.2f')
		dic['new_amount15'] = format(total_amount_sum.sum_amount15,'.2f')
		return  dic
	
	def set_to_zero(self) :
		
		total_amount_sum.sum_amount =0
		total_amount_sum.sum_amount1 =0
		total_amount_sum.sum_amount2 =0
		total_amount_sum.sum_amount3 =0
		total_amount_sum.sum_amount4 =0
		total_amount_sum.sum_amount5 =0
		total_amount_sum.sum_amount6 =0
		total_amount_sum.sum_amount7 =0
		total_amount_sum.sum_amount8 =0
		total_amount_sum.sum_amount9 =0
		total_amount_sum.sum_amount10 =0
		total_amount_sum.sum_amount11 =0  ## for 14.0 % HHH
		total_amount_sum.sum_amount12 =0  ## for Non Taxable
		total_amount_sum.sum_amount13 =0  # for 14.50% sagar
		total_amount_sum.sum_amount14 =0
		total_amount_sum.sum_amount15 =0

	def get_account_name(self,self_id,to_date):
		cr = self.cr
		uid = self.uid
		dic = {
			'iob_one_1':'',
			'iob_one_2':'',
			'iob_one_3':'',
			'iob_two':'',
			 }
		for res in self.pool.get('monthly.report').browse(cr,uid,[self_id]):
				
				search_name = self.pool.get('account.account').search(cr,uid,[('account_selection','in',('iob_one','iob_two')),('create_date','<=',to_date)])
				#search_name.reverse()
				print"LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLll",search_name
				for nm in self.pool.get('account.account').browse(cr,uid,search_name):
						print"UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU",nm.receive_bank_no
						if nm.receive_bank_no == 'bank_one':
								dic['iob_one_1'] = nm.name
								print"UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU",nm.name
						if nm.receive_bank_no == 'bank_two':
								dic['iob_one_2'] = nm.name
								print"UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU",nm.name
						if nm.receive_bank_no == 'bank_three':
								dic['iob_one_3'] = nm.name
								print"UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU",nm.name
						if not nm.receive_bank_no:
								dic['iob_two'] = nm.name
						
				return dic
			
	def get_current_time(self):
		return get_current_time(self)

report_sxw.report_sxw('report.gst_stmt_of_collection_new', 'monthly.report', '/gst_accounting/report/gst_stmt_of_collection_new.rml', parser=gst_statement_of_collection_new, header="False")

