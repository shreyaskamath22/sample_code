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
from datetime import date,datetime, timedelta
import re
import time
from dateutil.relativedelta import relativedelta


class account_sales_receipts(osv.osv):
	_inherit = 'account.sales.receipts'

	_columns = {
		# 'invoice_advance_id':fields.many2one('invoice.advance.receipts','Invoice'),
		# 'invoice_adjustment_amount': fields.float('Adjustment Amount'),
		'advance_receipt_ids': fields.one2many('advance.line','advance_line_id','Advance Lines'),
		'inv_adhoc_receipt_ids': fields.one2many('invoice.adhoc.receipts','sales_receipt_id','Invoice Lines'),
		'gst_receipt': fields.boolean('GST Receipt?')
	}

	def add_info(self, cr, uid, ids, context=None):
	### Add button on sales receipt form
		line_id =  0
		auto_debit_total=auto_credit_total=auto_credit_cal=auto_debit_cal=itds_total = 0.0
		for res in self.browse(cr,uid,ids):
			account_id = False
			account_id = res.account_id.id
			types = res.type
			acc_status = res.acc_status
			acc_selection = res.account_id.account_selection
			acc_name = res.account_id.name
			# self.write(cr,uid,ids[0],{'payment_status':False})
			if acc_selection == 'advance':
				if acc_status != 'advance':
					raise osv.except_osv(('Alert!'),('Account status should be Advance!'))
				if types == 'debit':
					raise osv.except_osv(('Alert!'),('Account Type of Advance should be Credit'))
				if '18.0' not in acc_name:
					raise osv.except_osv(('Alert!'),("Please select Advance Receipt Taxable 18.0% Ledger!"))
				self.check_tax_rate(cr, uid, account_id)
			if acc_status=='advance':
				if acc_selection in ('cash','iob_one','iob_two'):
					pass
				if acc_selection =='against_ref':
					raise osv.except_osv(('Alert!'),("Kindly select Account Status other than 'Advance'!"))
			if acc_selection =='itds_receipt'  and acc_status != 'against_ref' :
				raise osv.except_osv(('Alert!'),('Account status should be Against Reference')) 

			# if res.account_id.account_selection == 'itds_receipt' and types == 'credit' and res.payment_status in ('short_payment','partial_payment'):
			# 	raise osv.except_osv(('Alert!'),('Short / Partial payment is not allowed \n \n Kindly Select Full payment'))

			account_id1=res.account_id
			account_selection=res.account_id.account_selection
			for i in res.sales_receipts_one2many:
				if account_id1.id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
				# Reciept Entry options for Multiple Tax rate given by Javed 22nd-Nov-2016
				# #<<-----------------------------Code Start #Rahul 02/12/2016 ------------------>>
				# print 'account selection type:',account_selection
				# if account_selection!='against_ref':
				# 	if account_selection==i.account_id.account_selection:
				# 		print 'account_selecttion',account_selection,' '
				# 		raise osv.except_osv(('Alert!'),('Can not select same account.'))
				# #<<-----------------------------Code End--------------------------------------->>

			if not account_id:
				raise osv.except_osv(('Alert'),('Please select Account Name.'))

			if not types:
				raise osv.except_osv(('Alert'),('Please select Type.'))

			if not acc_status:
				raise osv.except_osv(('Alert'),('Please select Status.'))
			
			if res.account_id.account_selection in ('cash','iob_one') and  res.type=='credit':
				raise osv.except_osv(('Alert'),('Please select debit for cash/bank payment.'))
			total_len=0
			for line in res.sales_receipts_one2many:
				account = line.account_id
				line_id = line.id
				if line.account_id.account_selection=="against_ref":
					total_len=total_len+1
			payment_status=[]	
			if res.sales_receipts_one2many:
				for ln in res.sales_receipts_one2many:
					if ln.account_id.account_selection=="against_ref" and ln.acc_status=="against_ref":
						payment_status.append(ln.payment_status)
			if acc_status and res.account_select_boolean == False:
				if acc_selection == 'iob_two':
					raise osv.except_osv(('Alert'),('Please select proper account name.'))
				if acc_status == 'against_ref':	
			                if acc_selection == 'against_ref':
			                        srch1 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
										('status','in',('open','printed','partially_writeoff')),
										('invoice_number','!=',''),
										('check_process_invoice','=',False),
										('partner_id','=',res.customer_name.id)]) #MHM 10dec
					        for advance in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch1):
					                if advance.check_process_invoice == False and total_len<1:
                                                                self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'check_invoice':False,'partial_payment_amount':0.0})
						srch_debit=self.pool.get('debit.note').search(cr,uid,[('customer_name','=',res.customer_name.id),('state_new','=','open'),('pending_amount','!=',0.0)])
						print srch_debit,'srch_debit'
						for x in self.pool.get('debit.note').browse(cr,uid,srch_debit):
								self.pool.get('debit.note').write(cr,uid,x.id,{'check_debit':False,'receipt_amount':0.0})

			        if acc_status == 'new_reference':  
                                        if acc_selection == 'security_deposit':
                                                search_new = self.pool.get('security.deposit').search(cr,uid,[('security_check_process','=',False)])
                                                for new_line in self.pool.get('security.deposit').browse(cr,uid,search_new):
                                                        if new_line.security_check_process == False:
                                                                self.pool.get('security.deposit').write(cr,uid,new_line.id,{'security_check_new_ref':False})                                  

				if acc_selection == 'itds_receipt' and types == 'debit':
			                if res.account_id.itds_rate:
			                        itds_rate = res.account_id.itds_rate
			                        itds_rate_per = itds_rate * 0.01
			                        for line in res.sales_receipts_one2many:
			                                if line.account_id.account_selection == 'against_ref':        
					                        grand_total = line.credit_amount
					                        itds_total = grand_total * itds_rate_per
			                else:
			                        raise osv.except_osv(('Alert'),('Please give Itds Rate'))
			                        		                        
	                     
			        if res.account_id.account_selection in ( 'iob_one' ,'cash'):
					if res.type=='debit':
						for j in res.sales_receipts_one2many:
							if j.type=='credit':
								auto_debit_total += j.credit_amount
							if j.type=='debit':
								auto_credit_total += j.debit_amount
						if auto_debit_total > auto_credit_total:
							auto_debit_total -= auto_credit_total
						else:		
							auto_debit_total=0.0
					else:	
						raise osv.except_osv(('Alert'),('Please select Type as Credit.'))
				if len(payment_status)==1:
					if payment_status[0]!=str(res.payment_status):
						raise osv.except_osv(('Alert'),('Please select proper payment status.'))                            
				self.pool.get('account.sales.receipts.line').create(cr,uid,{
										'receipt_id':res.id,
										'account_id':account_id,
										'acc_status':acc_status,
										'type':types,
										'debit_amount':round(itds_total) if itds_total else auto_debit_total,
										'credit_amount':auto_credit_cal,
										'customer_name':res.customer_name.id if res.customer_name else '',
										'payment_status':res.payment_status,
										})
			
			
			if acc_status and res.account_select_boolean == True:
			## from receipt button (direct receipt from sales)
				credit_value = debit_value = remaining_value = 0.0

				auto_debit_total=auto_credit_total=auto_credit_cal=auto_debit_cal=0.0
				if acc_selection == 'iob_two':
					raise osv.except_osv(('Alert'),('Please select proper account name.'))
				if acc_status == 'against_ref': 	
			                for line in res.sales_receipts_one2many:
			                        if line.account_id.account_selection == 'against_ref':
                                                        credit_value = line.credit_amount
			                                srch1 = self.pool.get('invoice.adhoc.master').search(cr,uid,[
												('status','in',('open','printed','partially_writeoff')),
												('invoice_number','!=',''),
												('check_process_invoice','=',False),
												('partner_id','=',res.customer_name.id),('pending_amount','!=',0.0)])
					                
                                                if line.account_id.account_selection == 'itds_receipt':
			                                debit_value +=  line.debit_amount
			                                
                                                if line.account_id.account_selection == 'security_deposit':
			                                debit_value +=  line.debit_amount
			                                			                        
			                
			                remaining_value = credit_value - debit_value       
			              
			        if  res.account_id.account_selection in ('iob_one','cash'):
					if res.type=='debit':
						for j in res.sales_receipts_one2many:
							if j.type=='credit':
								auto_debit_total += j.credit_amount
							if j.type=='debit':
								auto_credit_total += j.debit_amount
						if auto_debit_total > auto_credit_total:
							auto_debit_total -= auto_credit_total
						else:
							auto_debit_total=0.0
					else:	
						for k in res.sales_receipts_one2many:
							if k.type=='credit':
								auto_debit_cal += k.credit_amount
							if k.type=='debit':
								auto_credit_cal += k.debit_amount
						if auto_debit_cal < auto_credit_cal:
							auto_credit_cal -= auto_debit_cal
						else:
							auto_credit_cal=0.0
				self.pool.get('account.sales.receipts.line').create(cr,uid,{
										'receipt_id':res.id,
										'account_id':account_id,
										'acc_status':acc_status,
										'type':types,
										'debit_amount':remaining_value if remaining_value else auto_debit_total,
										'credit_amount':auto_credit_cal,
										'customer_name':res.customer_name.id if res.customer_name else '',
										'payment_status':res.payment_status,
										
										})

			self.write(cr,uid,res.id,{'account_id':None,'type':''})
		return True

	def settle2(self,cr,uid,ids,context=None):
	### To settle advance receipt against invoice
		for rec in self.browse(cr,uid,ids):
			invoice_no = advance_invoice_no = ''
			total_invoice_amount = ref_amount = total_ref_amount = 0.0
			pending_amt = for_advance_pen=total_advance_amount=0.0

			for line in rec.sales_receipts_one2many:
				invoice_number = line.invoice_number.id
				credit_amount = line.credit_amount

				if line.account_id.account_selection == 'advance':
					total_ref_amount = line.credit_amount
					if line.advance_invoice_one2many == []:
						raise osv.except_osv(('Alert'),('No line present for Invoices.'))
					
					for invoice_line in line.advance_one2many:
						advance_rec_id=invoice_line.id
					for invoice_rec in line.advance_invoice_one2many:
						if invoice_rec.flag == False :
							if invoice_rec.payment_method_adv == 'partial_payment':
								total_advance_amount += invoice_rec.partial_payment_amount
								if invoice_rec.partial_payment_amount > invoice_rec.invoice_amount:
									print invoice_rec.partial_payment_amount,invoice_rec.invoice_amount,'kkkkkkkkk'
									raise osv.except_osv(('Alert'),('Total advance amount is not greater than Invoice amount'))
							# if invoice_rec.payment_method_adv == 'full_payment':
							# 	total_advance_amount += invoice_rec.invoice_amount
					if total_ref_amount < total_advance_amount :
						print total_ref_amount,total_advance_amount,'kkkkkkkkk'
						raise osv.except_osv(('Alert'),('Total Invoice amount is greater than advance amount'))
					for invoice_line in line.advance_invoice_one2many:
					      	if invoice_line.flag == False :
							advance_invoice_no = invoice_line.invoice_number
							total_invoice_amount +=  invoice_line.invoice_amount

							if invoice_line.payment_method_adv == 'partial_payment':
								if invoice_line.partial_payment_amount > total_ref_amount :
									raise osv.except_osv(('Alert'),('Partial Amount of Invoice is greater than Advance amount'))
				                                if invoice_line.partial_payment_amount <= total_ref_amount:
									srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[('id','=',invoice_line.invoice_id.id)])
									for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
										invoice_no = res.invoice_number
										invoice_pending_amount = invoice_line.invoice_amount - invoice_line.partial_payment_amount 
										self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,{
												'status':'printed' if invoice_pending_amount > 0 else 'paid',
												#'invoice_paid_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'pending_status':'pending',
												'pending_amount':invoice_pending_amount,
												'check_advance_ref_invoice':True,
												'invoice_id_receipt_advance':line.id})
												
										self.pool.get('invoice.receipt.history').create(cr,uid,{
										                'receipt_number':rec.receipt_no,
												'invoice_receipt_history_id':res.id,
												'invoice_number':res.invoice_number,
												'amount_receipt':rec.credit_amount,
												'invoice_pending_amount':invoice_pending_amount,
												'invoice_paid_amount':invoice_line.partial_payment_amount,
												'invoice_paid_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'invoice_date':res.invoice_date,
												'service_classification':res.service_classification,
												'advance_writeoff_amount':invoice_line.partial_payment_amount,
												'advance_writeoff_date':datetime.now().date(),
												'tax_rate':res.tax_rate,
												'cse':res.cse.id,'check_invoice':True})
										self.pool.get('advance.receipt.history').create(cr,uid,{
												'history_advance_id':advance_rec_id,
												'advance_receipt_no':rec.receipt_no,
												'cust_name':rec.customer_name.id,
												'advance_refund_amount':invoice_line.partial_payment_amount,
												'advance_pending_amount':for_advance_pen,
												'advance_receipt_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'advance_date':rec.receipt_date,
												'service_classification':res.service_classification,
												'receipt_id':rec.id})  #sagar for advance history 15sept
										srch_history = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',invoice_no)])
										if srch_history:
											for st in self.pool.get('payment.contract.history').browse(cr,uid,srch_history): 
												self.pool.get('payment.contract.history').write(cr,uid,st.id,{'payment_status':'paid'})
											#self.sync_state_paid_advance(cr,uid,ids,context=context)
							# if invoice_line.payment_method_adv == 'full_payment':
							# 	if invoice_line.invoice_amount > total_ref_amount :
							# 		raise osv.except_osv(('Alert'),('Amount of Invoice is greater than Advance amountff'))
											      
				   #                              if invoice_line.invoice_amount <= total_ref_amount:
							# 		srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','=',invoice_line.invoice_id.id)])
							# 		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
							# 			invoice_no = res.invoice_number
							# 			self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,{
							# 					'status':'paid',
							# 					'invoice_paid_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
							# 					'pending_status':'paid',
							# 					'pending_amount':0.0,
							# 					'check_advance_ref_invoice':True,
							# 					'invoice_id_receipt_advance':line.id})
								
							# 			self.pool.get('invoice.receipt.history').create(cr,uid,{
							# 			                'receipt_number':rec.receipt_no,
							# 					'invoice_receipt_history_id':res.id,
							# 					'invoice_number':res.invoice_number,
							# 					'amount_receipt':res.grand_total_amount,
							# 					'invoice_pending_amount':0.0,
							# 					'invoice_paid_amount':invoice_line.invoice_amount,
							# 					'invoice_paid_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
							# 					'invoice_date':res.invoice_date,
							# 					'service_classification':res.service_classification,
							# 					'tax_rate':res.tax_rate,
							# 					'cse':res.cse.id,
							# 					'check_invoice':True})
							# 			self.pool.get('advance.receipt.history').create(cr,uid,{
							# 			                'history_advance_id':advance_rec_id,
							# 					'advance_receipt_no':rec.receipt_no,
							# 					'cust_name':rec.customer_name.id,
							# 					'advance_refund_amount':invoice_line.invoice_amount,
							# 					'advance_pending_amount':0.0,
							# 					'advance_receipt_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
							# 					'advance_date':rec.receipt_date,
							# 					'service_classification':res.service_classification,
							# 					'receipt_id':rec.id})  #sagar for advance history 15sept
							# 			srch_history = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',invoice_no)])
							# 			if srch_history:
							# 				for st in self.pool.get('payment.contract.history').browse(cr,uid,srch_history): 
							# 					self.pool.get('payment.contract.history').write(cr,uid,st.id,{'payment_status':'paid'})

							# 			self.sync_state_paid_advance(cr,uid,ids,context=context)
					for_advance_pen = total_ref_amount - total_advance_amount
					if for_advance_pen >=0.0:
					        if for_advance_pen==0.0:
					                self.write(cr,uid,rec.id,{'settle2':True,'state':'done','new_ad':False})
						        self.pool.get('account.sales.receipts.line').write(cr,uid,line.id,{'state':'finish'})
						self.write(cr,uid,rec.id,{'advance_pending':for_advance_pen})
					else:
						raise osv.except_osv(('Alert'),('Total Invoice amount is greater than advance amount'))
					for advance in line.advance_one2many:
						self.pool.get('advance.sales.receipts').write(cr,uid,advance.id,{
												'check_advance_against_ref':False if for_advance_pen else True,
												'check_advance_against_ref_process':False if for_advance_pen else True,
												'advance_pending':for_advance_pen,})
					for i in line.advance_invoice_one2many:
						self.pool.get('advance.invoice.line').write(cr,uid,i.id,{'check_settle':True,
							                                                'paid_date':datetime.now().date(),
							                                                'flag': True})
		return True

	def settle(self,cr,uid,ids,context=None):
	### To settle advance receipt against invoice
		for rec in self.browse(cr,uid,ids):
			invoice_no = advance_invoice_no = ''
			total_invoice_amount = ref_amount = total_ref_amount = 0.0
			pending_amt = for_advance_pen=total_advance_amount=0.0

			for line in rec.sales_receipts_one2many:
				invoice_number = line.invoice_number.id
				credit_amount = line.credit_amount

				if line.account_id.account_selection == 'advance':
					total_ref_amount = rec.advance_pending
					if line.advance_invoice_one2many == []:
						raise osv.except_osv(('Alert'),('No line present for Invoices.'))
					
					for invoice_line in line.advance_one2many:
						advance_rec_id=invoice_line.id
					for invoice_rec in line.advance_invoice_one2many:
						if invoice_rec.flag == False :
							if invoice_rec.payment_method_adv == 'partial_payment':
								total_advance_amount += invoice_rec.partial_payment_amount
								if invoice_rec.partial_payment_amount > invoice_rec.invoice_amount:
									print invoice_rec.partial_payment_amount,invoice_rec.invoice_amount,'kkkkkkkkk'
									raise osv.except_osv(('Alert'),('Total advance amount is not greater than Invoice amount'))
							if invoice_rec.payment_method_adv == 'full_payment':
								total_advance_amount += invoice_rec.invoice_amount
					if total_ref_amount < total_advance_amount :
						raise osv.except_osv(('Alert'),('Total Invoice amount is greater than advance amount'))
					for invoice_line in line.advance_invoice_one2many:
						if invoice_line.flag == False :
							advance_invoice_no = invoice_line.invoice_number
							total_invoice_amount +=  invoice_line.invoice_amount

							if invoice_line.payment_method_adv == 'partial_payment':
								if invoice_line.partial_payment_amount > total_ref_amount :
									raise osv.except_osv(('Alert'),('Partial Amount of Invoice is greater than Advance amount'))
								if invoice_line.partial_payment_amount <= total_ref_amount:
									srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[('id','=',invoice_line.invoice_id.id)])
									for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
										invoice_no = res.invoice_number
										invoice_pending_amount = invoice_line.invoice_amount - invoice_line.partial_payment_amount 
										self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,{
												'status':'printed' if invoice_pending_amount > 0 else 'paid',
												#'invoice_paid_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'pending_status':'pending',
												'pending_amount':invoice_pending_amount,
												'check_advance_ref_invoice':True,
												'invoice_id_receipt_advance':line.id})
										self.pool.get('invoice.receipt.history').create(cr,uid,{
												'receipt_number':rec.receipt_no,
												'invoice_receipt_history_id':res.id,
												'invoice_number':res.invoice_number,
												'amount_receipt':rec.credit_amount,
												'invoice_pending_amount':invoice_pending_amount,
												'invoice_paid_amount':invoice_line.partial_payment_amount,
												'invoice_paid_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'invoice_date':res.invoice_date,
												'service_classification':res.service_classification,
												'advance_writeoff_amount':invoice_line.partial_payment_amount,
												'advance_writeoff_date':datetime.now().date(),
												'tax_rate':res.tax_rate,
												'cse':res.cse.id,'check_invoice':True})
										self.pool.get('advance.receipt.history').create(cr,uid,{
												'history_advance_id':advance_rec_id,
												'advance_receipt_no':rec.receipt_no,
												'cust_name':rec.customer_name.id,
												'advance_refund_amount':invoice_line.partial_payment_amount,
												'advance_pending_amount':for_advance_pen,
												'advance_receipt_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'advance_date':rec.receipt_date,
												'service_classification':res.service_classification,
												'receipt_id':rec.id})  #sagar for advance history 15sept
										srch_history = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',invoice_no)])
										if srch_history:
											for st in self.pool.get('payment.contract.history').browse(cr,uid,srch_history): 
												self.pool.get('payment.contract.history').write(cr,uid,st.id,{'payment_status':'paid'})
											#self.sync_state_paid_advance(cr,uid,ids,context=context)
							if invoice_line.payment_method_adv == 'full_payment':
								if invoice_line.invoice_amount > total_ref_amount :
									raise osv.except_osv(('Alert'),('Amount of Invoice is greater than Advance amountff'))
								if invoice_line.invoice_amount <= total_ref_amount:
									srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','=',invoice_line.invoice_id.id)])
									for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
										invoice_no = res.invoice_number
										self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,{
												'status':'paid',
												'invoice_paid_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'pending_status':'paid',
												'pending_amount':0.0,
												'check_advance_ref_invoice':True,
												'invoice_id_receipt_advance':line.id})
								
										self.pool.get('invoice.receipt.history').create(cr,uid,{
												'receipt_number':rec.receipt_no,
												'invoice_receipt_history_id':res.id,
												'invoice_number':res.invoice_number,
												'amount_receipt':res.grand_total_amount,
												'invoice_pending_amount':0.0,
												'invoice_paid_amount':invoice_line.invoice_amount,
												'invoice_paid_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'invoice_date':res.invoice_date,
												'service_classification':res.service_classification,
												'tax_rate':res.tax_rate,
												'cse':res.cse.id,
												'check_invoice':True})
										self.pool.get('advance.receipt.history').create(cr,uid,{
												'history_advance_id':advance_rec_id,
												'advance_receipt_no':rec.receipt_no,
												'cust_name':rec.customer_name.id,
												'advance_refund_amount':invoice_line.invoice_amount,
												'advance_pending_amount':0.0,
												'advance_receipt_date':(invoice_line.paid_date if invoice_line.paid_date else datetime.now().date()),
												'advance_date':rec.receipt_date,
												'service_classification':res.service_classification,
												'receipt_id':rec.id})  #sagar for advance history 15sept
										srch_history = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',invoice_no)])
										if srch_history:
											for st in self.pool.get('payment.contract.history').browse(cr,uid,srch_history): 
												self.pool.get('payment.contract.history').write(cr,uid,st.id,{'payment_status':'paid'})

										self.sync_state_paid_advance(cr,uid,ids,context=context)
					for_advance_pen = total_ref_amount - total_advance_amount
					if for_advance_pen >=0.0:
						if for_advance_pen==0.0:
							self.write(cr,uid,rec.id,{'settle2':True,'state':'done','new_ad':False})
							self.pool.get('account.sales.receipts.line').write(cr,uid,line.id,{'state':'finish'})
						self.write(cr,uid,rec.id,{'advance_pending':for_advance_pen})
					else:
						raise osv.except_osv(('Alert'),('Total Invoice amount is greater than advance amount'))
					for advance in line.advance_one2many:
						self.pool.get('advance.sales.receipts').write(cr,uid,advance.id,{
												'check_advance_against_ref':False if for_advance_pen else True,
												'check_advance_against_ref_process':False if for_advance_pen else True,
												'advance_pending':for_advance_pen,})
					for i in line.advance_invoice_one2many:
						self.pool.get('advance.invoice.line').write(cr,uid,i.id,{'check_settle':True,
							                                                'paid_date':datetime.now().date(),
							                                                'flag': True})
		return True


	def process(self, cr, uid, ids, context=None):
		count = count1 = 0
		move = grand_total = invoice_date= invoice_number= iob_one_id = demand_draft_id = neft_id = ''
		flag_service = flag_debit = flag_against = flag = flag1 = flag2 = flag_sundry_deposit = py_date = False
		post=[]
		post2=[]
		status=[]
		security_id = advance_id = cofb_id = invoice_id_receipt = sales_debit_id = ''
		credit_amount_srch_amount= invoice_id_receipt_advance = advance_ref_id = advance_ref_id1 = receipt_date=''
		cheque_no = sundry_id = cfob_other_id = ''
		cheque_amount = adv_against_line= neft_amount = dd_amount = grand_total = 0.0
		ref_amount = ref_amount1 = ref_amount_adv = ref_amount_cofb = ref_amount_cfob_other = 0.0
		grand_total_against = grand_total_against_new = cr_total = dr_total = 0.0
		debit_note_amount = grand_total_advance = ref_amount_security = pay_amount = 0.0
		total_credit=total_debit=0.0
		today_date = datetime.now().date()
		invoice_date_exceed = datetime.now().date()
		models_data=self.pool.get('ir.model.data')
		cfob_sync_flag=False
		for res1 in self.browse(cr,uid,ids):
			if res1.customer_name.name == 'CBOB':
				raise osv.except_osv(('Alert'),('Receipt for CBOB cannnot be Created.'))
			if res1.receipt_date:
				check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
				if check_bool:
					if res1.receipt_date != str(today_date):
						raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
					else:
						py_date = str(today_date + relativedelta(days=-5))
						if res1.receipt_date < str(py_date) or res1.receipt_date > str(today_date):
				 			raise osv.except_osv(('Alert'),('Kindly select Receipt Date 5 days earlier from current date.'))
					receipt_date=res1.receipt_date	
			else:
				receipt_date=datetime.now().date()
			acc_id=self.pool.get('account.account').search(cr,uid,[('account_selection','in',('cash','iob_one'))])
			for line1 in res1.sales_receipts_one2many:
				account_id = line1.account_id.id
				account_name = line1.account_id.name
				acc_status = line1.acc_status
				types = line1.type
				dr_total += line1.debit_amount
				cr_total += line1.credit_amount
				if account_id:
					temp = tuple([account_id])
					post.append(temp)
					for i in range(0,len(post)):
						for j in range(i+1,len(post)):
							if post[i][0] == post[j][0]:
								raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))
				if line1.account_id in acc_id and line1.type != 'debit':
					raise osv.except_osv(('Alert'),('Bank/Cash Account should be debit.'))
		post2 = [r[0] for r in post]
		for post1 in post2:
			if  post1  in acc_id :
				flag_service = True
		if not flag_service:
			raise osv.except_osv(('Alert'),('Entry cannot be processed without cash/bank account.'))
		if round( dr_total,2) !=round( cr_total,2):
			raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))
		if dr_total == 0.0 or cr_total == 0.0:
			raise osv.except_osv(('Alert'),('Amount cannot be zero.')) 
		for res in self.browse(cr,uid,ids):
			for line in res.sales_receipts_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name
				if acc_selection == 'against_ref' and line.acc_status == 'against_ref':
					pending_amt = credit_amount_srch_amount = grand_total_against_new_new = 0.0
					if res.payment_status == False:
						raise osv.except_osv(('Alert'),('Select Payment Status.'))              
					for i in line.debit_note_one2many:
						if i.check_debit == True:
							sales_debit_id = i.sales_debit_id.id
							credit_amount_srch_amount += i.receipt_amount
					grand_total_against_new =0.0
					for invoice_line in line.invoice_adhoc_one2many:
							invoice_id_receipt =  invoice_line.invoice_id_receipt.id
							if invoice_line.check_invoice == True:
								if res.payment_status == 'partial_payment':
									grand_total_against_new += invoice_line.partial_payment_amount if invoice_line.partial_payment_amount else invoice_line.pending_amount
								if res.payment_status == 'short_payment':
									grand_total_against_new += invoice_line.partial_payment_amount if invoice_line.partial_payment_amount else invoice_line.pending_amount
								if res.payment_status == 'full_payment':
									grand_total_against_new += invoice_line.pending_amount
					grand_total_against_new_new = grand_total_against_new + credit_amount_srch_amount
					if round(line.credit_amount,2)!=round(grand_total_against_new_new,2):
						raise osv.except_osv(('Alert'),('Credit amount and Total of Wizard amount is not equal!'))
		for res in self.browse(cr,uid,ids):
			for ln_itds in res.sales_receipts_one2many:
				if ln_itds.type == 'credit':
					if ln_itds.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				elif ln_itds.type == 'debit':
					if ln_itds.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				else:
					raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(line.account_id.name))))
				if (ln_itds.acc_status == 'against_ref') and  ln_itds.customer_name.name !='CFOB':
					if ln_itds.account_id.account_selection == 'itds_receipt':
						if ln_itds.debit_amount != 0.0 and ln_itds.customer_name.tan_no == False:
							raise osv.except_osv(('Alert'),('Kindly fill the Tan Number of customer.'))
			for line in res.sales_receipts_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name
				debit_amt = 0.0
				if acc_selection == 'iob_one':
					receipt_line_obj = self.pool.get('account.sales.receipts.line')
					receipt_line_ids = receipt_line_obj.search(cr, uid, [('receipt_id','=',ids[0]),
													  ('debit_amount','!=',0),
													  ('credit_amount','=',0)], context=context)
					for receipt_line_id in receipt_line_ids:
						receipt_line_data = receipt_line_obj.browse(cr, uid, receipt_line_id)
						debit_amt = debit_amt + receipt_line_data.debit_amount
					for iob_one_line in line.iob_one_one2many: ## cheque
						iob_one_id = iob_one_line.iob_one_id.id
						cheque_no = iob_one_line.cheque_no
						cheque_amount += iob_one_line.cheque_amount
						for n in str(iob_one_line.cheque_no):
							p = re.compile('([0-9]{6}$)')
							if p.match(iob_one_line.cheque_no)== None :
								self.pool.get('iob.one.sales.receipts').create(cr,uid,{'cheque_no':''})
								raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque Number.'))
						if not iob_one_line.cheque_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not iob_one_line.cheque_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not iob_one_line.drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not iob_one_line.bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
						if not iob_one_line.selection_cts:
							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))
					amount =line.debit_amount if line.debit_amount else line.credit_amount
					if amount  and cheque_amount and round(amount,2) != round(cheque_amount,2):
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
					for demand_draft_line in line.demand_draft_one_one2many: #DD 
						demand_draft_id = demand_draft_line.demand_draft_id.id
						dd_no = demand_draft_line.dd_no
						dd_amount += demand_draft_line.dd_amount
						for n in str(demand_draft_line.dd_no):
							p = re.compile('([0-9]{6,9}$)')
							if p.match(demand_draft_line.dd_no)== None :
								self.pool.get('demand.draft.sales.receipts').create(cr,uid,{'dd_no':''})
								raise osv.except_osv(('Alert!'),('Please Enter 6 to 9 digit Demand draft Number.'))
						if not demand_draft_line.dd_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not demand_draft_line.dd_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not demand_draft_line.demand_draft_drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not demand_draft_line.dd_bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
						if not demand_draft_line.selection_cts:
							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))
					amount =line.debit_amount if line.debit_amount else line.credit_amount
					if amount  and dd_amount and round(amount,2) != round(dd_amount,2):
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
					for neft_line in line.neft_one2many:  
						neft_id = neft_line.neft_id.id
						neft_amount +=  neft_line.neft_amount
						if not neft_line.beneficiary_bank_name:
							raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
						if not neft_line.pay_ref_no:
							raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
						if not neft_line.neft_amount:
							raise osv.except_osv(('Alert!'),('Please provide Amount for NEFT/RTGS.'))
					amount = line.debit_amount if line.debit_amount else line.credit_amount
					if amount and neft_amount and round(amount,2) != round(neft_amount,2):
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
					if not iob_one_id:
						if not neft_id:
							if not demand_draft_id:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if iob_one_id or neft_id or demand_draft_id: 
						if cheque_amount:
							bank_amount = cheque_amount
						elif dd_amount:
							bank_amount = dd_amount
						elif neft_amount:
							bank_amount = neft_amount
						if line.debit_amount:
							if round(bank_amount,2) != round(line.debit_amount,2):
								raise osv.except_osv(('Alert'),('Debit amount should be equal'))
						if line.credit_amount:
							if round(bank_amount,2) != round(line.credit_amount,2):
								raise osv.except_osv(('Alert'),('Credit amount should be equal'))
				if acc_selection == 'advance' and line.type == 'credit':
					self.check_tax_rate(cr, uid, account_id)
					for advance_line in line.advance_one2many:
						advance_id = advance_line.advance_id.id
						ref_amount_adv = ref_amount_adv + advance_line.ref_amount
						if not advance_line.ref_date:
							raise osv.except_osv(('Alert'),('Please provide reference date.'))
					amount =line.credit_amount if line.credit_amount else line.debit_amount
					if amount and ref_amount_adv and round(amount,2) != round(ref_amount_adv,2):
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
					if not advance_id:
						raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					elif advance_id:
						if line.debit_amount:
							if round(ref_amount_adv,2) != round(line.debit_amount,2):
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
						if line.credit_amount:
							if round(ref_amount_adv,2) != round(line.credit_amount,2):
								   raise osv.except_osv(('Alert'),('Credit amount should be equal'))
				if line.acc_status != 'advance':
					if line.invoice_adhoc_one2many:
						for inv_date in line.invoice_adhoc_one2many:
							if inv_date.check_invoice == True:
								invoice_date_exceed=inv_date.invoice_date
					if line.sales_other_cfob_one2many:
						for cfob_other in  line.sales_other_cfob_one2many:
							 invoice_date_exceed = cfob_other.ref_date
					if res.receipt_date == False :
						res.receipt_date=str(datetime.now().date())
					if str(res.receipt_date) < str(invoice_date_exceed):
						if line.invoice_adhoc_one2many or line.sales_other_cfob_one2many :
							raise osv.except_osv(('Alert'),('Invoice date is greater than receipt date. Select proper receipt date or for back-date entry select status as advance.'))
					if acc_selection == 'security_deposit':
						sec_id = security_id = ''
						customer_name = line.receipt_id.customer_name.id
						if line.acc_status == 'new_reference':
							payment_status = line.receipt_id.payment_status
							ref_amount_security = 0.0
							for sec_new_line in line.security_new_ref_one2many:
								if sec_new_line.security_check_new_ref == True:
									security_id = sec_new_line.security_new_ref_id.id
									sec_id = sec_new_line.id
									ref_date = sec_new_line.ref_date
									ref_no = sec_new_line.ref_no
									ref_amount = sec_new_line.ref_amount
									pending_amount = sec_new_line.pending_amount
									partial_payment_amount = sec_new_line.partial_payment_amount
									ref_amount_security += (sec_new_line.partial_payment_amount if payment_status == 'partial_payment' else sec_new_line.pending_amount )  
									pending_amount -= (sec_new_line.partial_payment_amount \
													   if payment_status == 'partial_payment' \
													   else sec_new_line.pending_amount) 
									self.pool.get('security.deposit').write(cr,uid,sec_id,
										{ 
											'security_check_process':True if pending_amount == 0.0 else False,
											'pending_amount':pending_amount,
											'customer_name':customer_name,
											'customer_name_char':res.customer_name.name if  res.customer_name.name else '',
											'acc_status_new':line.acc_status,
										})
									self.pool.get('security.deposit.history').create(cr,uid,
										{
											'security_deposit_id':sec_id,
											'ref_no':ref_no,
											'customer_name':customer_name,
											'ref_amount':ref_amount,
											'pending_amount':pending_amount,
											'partial_payment_amount':sec_new_line.partial_payment_amount if payment_status == 'partial_payment' else sec_new_line.pending_amount,
											'ref_date':ref_date,
											'receipt_date':receipt_date if receipt_date else '',
											'receipt_id':line.id,
											'new_sec':True
										})
							if not security_id and res.account_select_boolean==False:  
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
							if not security_id:
								if line.debit_amount > 0.0 or line.credit_amount > 0.0:
									raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
							elif security_id:
								if line.debit_amount:
									if  round(ref_amount_security,2) != round(line.debit_amount,2):
										raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
								if line.credit_amount:
									if  round(ref_amount_security,2) != round(line.credit_amount,2):
										raise osv.except_osv(('Alert'),('Credit amount should be equal.'))
					if acc_selection == 'sundry_deposit' and line.acc_status !='others':
						for sun_dep_line in line.sundry_deposit_one2many:
							if sun_dep_line.sundry_check == True:
								sd_flag=True
								flag_sundry_deposit = True
								sundry_id = sun_dep_line.sundry_id.id
								pay_amount +=  sun_dep_line.partial_amount if sun_dep_line.partial_amount else sun_dep_line.pending_amount
								if sun_dep_line.partial_amount!=0.0:
									amt = sun_dep_line.partial_amount-sun_dep_line.pending_amount
									sd_flag=False
								else:
									amt = sun_dep_line.pending_amount								    
								self.pool.get('sundry.deposit').write(cr,uid,sun_dep_line.id,{'sundry_check_process':sd_flag,"pending_amount":amt})
						if not sundry_id:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						if line.debit_amount:
							if  round(pay_amount,2) != round(line.debit_amount,2):
								raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
						if line.credit_amount:
							if  round(pay_amount,2) != round(line.credit_amount,2):
								raise osv.except_osv(('Alert'),('Credit amount should be equal.'))
					if line.acc_status == 'others' and acc_selection == 'sundry_deposit' and res.customer_name.name=='CFOB':
						for i in line.sundry_deposit_one2many:
							self.pool.get('sundry.deposit').write(cr,uid,i.id,{'pending_amount':i.payment_amount,'customer_name':res.customer_name.id,'acc_status_new':'others'})										
					if acc_selection == 'others':
						for cofb_line in line.cofb_one2many:
							cofb_id = cofb_line.cofb_id.id
							ref_amount_cofb = ref_amount_cofb + cofb_line.ref_amount
						if not cofb_id:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						elif cofb_id:
							if line.debit_amount:
								if round(ref_amount_cofb,2) != round(line.debit_amount,2):
									raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
							if line.credit_amount:
								if round(ref_amount_cofb,2)  != round(line.credit_amount,2):
									raise osv.except_osv(('Alert'),('Credit amount should be equal.'))
					if line.acc_status == 'others' and acc_selection == 'against_ref':
						cfob_id = ''
						total_credit=total_credit+line.credit_amount
						total_debit=total_debit+line.debit_amount
						if line.customer_name.name == 'CFOB':
							for cfob_other_line in line.sales_other_cfob_one2many:
							        cfob_sync_flag = True
								cfob_other_id = cfob_other_line.cfob_other_id.id
								ref_amount_cfob_other = ref_amount_cfob_other + cfob_other_line.ref_amount
								cfob_id = cfob_other_line.id
								self.pool.get('cofb.sales.receipts').write(cr,uid,cfob_other_line.id,{'check_cfob_sales_process':True})
							if line.invoice_cfob_one2many:
								for invoice_cfob_line in line.invoice_cfob_one2many:
									if invoice_cfob_line.cfob_chk_invoice:
										ref_amount_cfob_other = ref_amount_cfob_other + invoice_cfob_line.pending_amount
										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_cfob_line.id,
											{
												'cfob_chk_invoice_process':True,
												'status':'paid',
												'invoice_paid_date':datetime.now().date(),
												'pending_status':'paid'
											})
										self.pool.get('invoice.receipt.history').create(cr,uid,
											{
												'invoice_receipt_history_id':invoice_cfob_line.id,
												'invoice_number':invoice_cfob_line.invoice_number,
												'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
												'receipt_id_history':line.id,
												'invoice_pending_amount':0.0,
												'invoice_paid_amount':invoice_cfob_line.pending_amount,
												'invoice_date':invoice_cfob_line.invoice_date,
												'service_classification':invoice_cfob_line.service_classification,
												'tax_rate':invoice_cfob_line.tax_rate,
												'cse':invoice_cfob_line.cse.id,
												'check_invoice':True
											})
							if not cfob_other_id:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name)) 
							elif cfob_other_id:
								if total_debit:
									if round(ref_amount_cfob_other,2) != round(total_debit,2):
										raise osv.except_osv(('Alert'),('Debit amount should be equal.'))
								if total_credit:
									print total_credit,'credit',ref_amount_cfob_other
									if round(ref_amount_cfob_other,2) != round(total_credit,2):
										raise osv.except_osv(('Alert'),('Credit amount should be equal.'))              
					if acc_selection == 'against_ref' and line.acc_status == 'against_ref':
						pending_amt = credit_amount_srch_amount = 0.0
						if res.payment_status == False:
							raise osv.except_osv(('Alert'),('Select Payment Status.'))              
						for i in line.debit_note_one2many:
							if i.check_debit == True:
								flag = True
								sales_debit_id = i.sales_debit_id.id
								credit_amount_srch_amount += i.receipt_amount
						count = 0
						amount = line.credit_amount if line.credit_amount else line.debit_amount
						for invoice_line in line.invoice_adhoc_one2many:
							invoice_id_receipt =  invoice_line.invoice_id_receipt.id
							if invoice_line.check_invoice == True:
								flag = True
								count +=  1
								grand_total_against += invoice_line.pending_amount
								if res.payment_status == 'partial_payment':
									grand_total_against_new += invoice_line.partial_payment_amount if invoice_line.partial_payment_amount else invoice_line.pending_amount
								if res.payment_status == 'short_payment':
									grand_total_against_new += invoice_line.partial_payment_amount if invoice_line.partial_payment_amount else invoice_line.pending_amount
								if res.payment_status == 'full_payment':
									grand_total_against_new += invoice_line.pending_amount
								if res.payment_status == 'partial_payment' and invoice_line.partial_payment_amount == 0.0:
									raise osv.except_osv(('Alert'),('partial amount cannot be zero.'))
						grand_total_against_new += credit_amount_srch_amount if credit_amount_srch_amount else 0.0  # 4may Debit note 
						credit_amt = 0.0
						receipt_line_obj = self.pool.get('account.sales.receipts.line')
						receipt_line_ids = receipt_line_obj.search(cr, uid, [('receipt_id','=',ids[0]),
														  ('debit_amount','=',0),
														  ('credit_amount','!=',0)], context=context)
						for receipt_line_id in receipt_line_ids:
							receipt_line_data = receipt_line_obj.browse(cr, uid, receipt_line_id)
							credit_amt = credit_amt + receipt_line_data.credit_amount
						amount_new = credit_amt
						grand_total_against_new_new = credit_amt
						if amount_new and grand_total_against_new_new and round(amount_new,2) != round(grand_total_against_new_new,2):
							raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
						credit_amount = line.credit_amount
						for invoice_line in line.invoice_adhoc_one2many:
							if invoice_line.check_invoice == True:
								if invoice_line.pending_amount<=0.0:
									raise osv.except_osv(('Alert'),('Receipt cannot be processed as pending amount for invoice is less than or equal to zero!'))
							invoice_id_receipt =  invoice_line.invoice_id_receipt.id
							if res.payment_status == 'short_payment' and invoice_line.check_invoice == True and invoice_line.pending_amount>0.0:
								if grand_total_against_new < credit_amount :
									raise osv.except_osv(('Alert'),('credit amount should be less than invoice amount.')) #11 may 15
								if grand_total_against > credit_amount:
									if count > 1:
										count -= 1
										pending_amt = grand_total_against - credit_amount
										grand_total_against = grand_total_against - invoice_line.pending_amount 
										credit_amount -= invoice_line.pending_amount 
										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
											'pending_amount':0.0,
											'pending_status':'paid',
											'status':'paid'})
										self.pool.get('invoice.receipt.history').create(cr,uid,
											{
												'invoice_receipt_history_id':invoice_line.id,
												'invoice_number':invoice_line.invoice_number,
												'invoice_pending_amount':0.0,
												'invoice_paid_amount':invoice_line.pending_amount,
												'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
												'receipt_id_history':line.id,
												'invoice_date':invoice_line.invoice_date,
												'service_classification':invoice_line.service_classification,
												'tax_rate':invoice_line.tax_rate,
												'cse':invoice_line.cse.id,
												'check_invoice':True
											})
									else:
										pending_amt = grand_total_against - credit_amount
										#credit_amount = credit_amount - invoice_line.pending_amount 
										
										self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
											'pending_amount':pending_amt,
											'pending_status':'pending',
											'status':'paid'})
										self.pool.get('invoice.receipt.history').create(cr,uid,{
											'invoice_receipt_history_id':invoice_line.id,
											'invoice_number':invoice_line.invoice_number,
											'invoice_pending_amount':pending_amt,
											'invoice_paid_amount':credit_amount,
											'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
											'receipt_id_history':line.id,
											'invoice_date':invoice_line.invoice_date,
											'service_classification':invoice_line.service_classification,
											'tax_rate':invoice_line.tax_rate,
											'cse':invoice_line.cse.id,
											'check_invoice':True})######## For Payment history

								elif grand_total_against == line.credit_amount:
									self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
										'check_process_invoice':True,
										'pending_amount':pending_amt,
										'pending_status':'paid',
										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date()})

									self.pool.get('invoice.receipt.history').create(cr,uid,{
										'invoice_receipt_history_id':invoice_line.id,
										'invoice_number':invoice_line.invoice_number,
										'invoice_pending_amount':pending_amt,
										'invoice_paid_amount':credit_amount,
										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
										'receipt_id_history':line.id,
										'invoice_date':invoice_line.invoice_date,
										'service_classification':invoice_line.service_classification,
										'tax_rate':invoice_line.tax_rate,
										'cse':invoice_line.cse.id,
										'check_invoice':True})######## For Payment history

							elif res.payment_status == 'partial_payment':####Partial payment
								if invoice_line.check_invoice == True and invoice_line.pending_amount>0.0:
									if invoice_line.partial_payment_amount:
										credit_amt = 0.0
										receipt_line_obj = self.pool.get('account.sales.receipts.line')
										receipt_line_ids = receipt_line_obj.search(cr, uid, [('receipt_id','=',ids[0]),
																		  ('debit_amount','=',0),
																		  ('credit_amount','!=',0)], context=context)
										for receipt_line_id in receipt_line_ids:
											receipt_line_data = receipt_line_obj.browse(cr, uid, receipt_line_id)
											credit_amt = credit_amt + receipt_line_data.credit_amount
										credit_amount_new = credit_amt
										grand_total_against_new_new = credit_amt
										if round(grand_total_against_new_new,2) > round(credit_amount_new,2)\
												or round(grand_total_against_new_new,2) < round(credit_amount_new,2):
											raise osv.except_osv(('Alert'),('credit amount and invoice partial amount should be equal.'))	
										pending_amount = invoice_line.pending_amount - invoice_line.partial_payment_amount
										if invoice_line.pending_amount==invoice_line.partial_payment_amount:
											self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
											'check_process_invoice':True,
											'pending_amount':pending_amount,
											'pending_status':'paid',
											'status':'paid',
											'partial_payment_amount':invoice_line.partial_payment_amount})
										else:
											self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
												'pending_amount':pending_amount,
												'pending_status':'pending',
												'status':invoice_line.status,
												'partial_payment_amount':invoice_line.partial_payment_amount})
										self.pool.get('invoice.receipt.history').create(cr,uid,
											{
												'invoice_receipt_history_id':invoice_line.id,
												'invoice_number':invoice_line.invoice_number,
												'invoice_pending_amount':pending_amount,
												'invoice_paid_amount':invoice_line.partial_payment_amount,
												'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
												'receipt_id_history':line.id,
												'invoice_date':invoice_line.invoice_date,
												'service_classification':invoice_line.service_classification,
												'tax_rate':invoice_line.tax_rate,
												'cse':invoice_line.cse.id,
												'check_invoice':True
											})
							elif res.payment_status == 'full_payment':
								if invoice_line.check_invoice == True and invoice_line.pending_amount>0.0:
									credit_amt = 0.0
									receipt_line_obj = self.pool.get('account.sales.receipts.line')
									receipt_line_ids = receipt_line_obj.search(cr, uid, [('receipt_id','=',ids[0]),
																	  ('debit_amount','=',0),
																	  ('credit_amount','!=',0)], context=context)
									for receipt_line_id in receipt_line_ids:
										receipt_line_data = receipt_line_obj.browse(cr, uid, receipt_line_id)
										credit_amt = credit_amt + receipt_line_data.credit_amount
									credit_amount_new = credit_amt
									grand_total_against_new_new = credit_amt
									if round(grand_total_against_new_new,2) > round(credit_amount_new,2)\
											or round(grand_total_against_new_new,2) < round(credit_amount_new,2):
										raise osv.except_osv(('Alert'),('credit amount and invoice amount should be equal.')) 
									pending_amt = grand_total_against - credit_amount
									self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_line.id,{
										'check_process_invoice':True,
										'pending_amount':0.0,
										'pending_status':'paid',
										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
										'status':'paid'}) 
									self.pool.get('invoice.receipt.history').create(cr,uid,{
										'invoice_receipt_history_id':invoice_line.id,
										'invoice_number':invoice_line.invoice_number,
										'invoice_pending_amount':pending_amt,
										'invoice_paid_amount':invoice_line.pending_amount,
										'invoice_paid_date':res.receipt_date if res.receipt_date else datetime.now().date(),
										'receipt_id_history':line.id,
										'invoice_date':invoice_line.invoice_date,
										'service_classification':invoice_line.service_classification,
										'tax_rate':invoice_line.tax_rate,
										'cse':invoice_line.cse.id,
										'check_invoice':True})
						if flag == False:
							raise osv.except_osv(('Alert'),('No invoice selected.'))
						if not invoice_id_receipt and not sales_debit_id:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if acc_selection == 'cash' and line.debit_amount >= 50000 or line.credit_amount >= 50000:
						if line.customer_name.name !='CFOB':
							if line.customer_name.pan_no == False:
								raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))
						else:
							for reco in line.invoice_cfob_one2many:
								if reco.partner_id.pan_no == False:
									raise osv.except_osv(('Alert'),('Kindly fill the Pan Number of customer.'))
		for rec in self.browse(cr,uid,ids):
			cse_name_id=False
			receipt_no = temp_count= seq_srch= seq= invoice_num = invoice_date_concate = cse_name = ''
			count=seq= grand_total = 0
			cse_name_last= cse_name_last_cfob= cfob_invoice= cfob_invoice_date=cfob_cust=''
			cfob_invoice_gross=0.0
			acc_status = rec.acc_status
			form_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_form')
			tree_view=models_data.get_object_reference(cr, uid, 'account_sales_branch', 'account_sales_receipts_tree')
			seq_srch=self.pool.get('ir.sequence').search(cr,uid,[('code','=','account.sales.receipts')])
			if seq_srch:
				seq_start=self.pool.get('ir.sequence').browse(cr,uid,seq_srch[0]).number_next
			ou_code = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
			ab_code = self.pool.get('res.users').browse(cr,uid,uid).company_id.sales_receipt_id
			month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
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
			financial_year =str(year1-1)+str(year1)	
			today_date = datetime.now().date()
			year = today_date.strftime('%y')
			t1=[]
			count=0
			seq_start=1
			if  ou_code and ab_code:
				# cr.execute("select cast(count(id) as integer) from account_sales_receipts where state not in ('draft') and receipt_date >= '2017-06-30' and receipt_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and import_flag = False"); # excluding imported advance through bills payable import 9 oct 15
				cr.execute("select cast(count(id) as integer) from account_sales_receipts where state not in ('draft') and receipt_date >= '2017-07-01' and receipt_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and import_flag = False"); # excluding imported advance through bills payable import 9 oct 15			
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				receipt_no = ou_code+ab_code+str(financial_year)+str(seq).zfill(5)
				existing_receipt_no = self.pool.get('account.sales.receipts').search(cr,uid,[('receipt_no','=',receipt_no)])
				if existing_receipt_no:
					receipt_no = ou_code+ab_code+str(financial_year)+str(seq+1).zfill(5)
					new_existing_receipt_no = self.pool.get('account.sales.receipts').search(cr,uid,[('receipt_no','=',receipt_no)])
					if new_existing_receipt_no:
						receipt_no = ou_code+ab_code+str(financial_year)+str(seq+2).zfill(5)
			if rec.customer_name.name == 'CFOB':
				for j in rec.sales_receipts_one2many:
					if j.account_id.account_selection=='against_ref':
						for k in j.sales_other_cfob_one2many:
							if k.customer_cfob not in t1:
								t1.extend([k.customer_cfob])
					if j.account_id.account_selection=='sundry_deposit':
						for k in j.sundry_deposit_one2many:
							if k.customer_name_char not in t1:
								t1.extend([k.customer_name_char])
				new_cus_name=', '.join(filter(bool,t1))
			else:
				new_cus_name=rec.customer_name.name
			self.write(cr,uid,ids,{
							'receipt_no':receipt_no,
							'receipt_date': receipt_date,
							'voucher_type':'Sales Receipt',
							'new_cus_name':new_cus_name})
			date = receipt_date 
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
			move = self.pool.get('account.move').create(cr,uid,{
									'journal_id':journal_id,
									'state':'posted',
									'date':date ,
									'name':receipt_no,
									'voucher_type':'Sales Receipt',
									'narration':rec.narration if rec.narration else '',
									},context=context)
			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in res.sales_receipts_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
								'account_id':ln.account_id.id,
								'debit':ln.debit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_id,
								'period_id':period_id,
								'date':str(date),
								'ref':receipt_no},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
								'account_id':ln.account_id.id,
								'credit':ln.credit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_id,
								'period_id':period_id,
								'date':date,
								'ref':receipt_no},context=context)
			for ln in res.sales_receipts_one2many:
				if ln.acc_status == 'against_ref':
					invoice_number = ''
					if ln.account_id.account_selection == 'against_ref':
						for debit_line in ln.debit_note_one2many:
							debit_note_no=debit_line.debit_note_no
							if debit_line.check_debit == True:
								if debit_line.pending_amount==debit_line.receipt_amount:
									srch_debit=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',debit_note_no)])
									for i in self.pool.get('debit.note').browse(cr,uid,srch_debit):
										paid_amount=i.pending_amount
										cr.execute("update debit_note set pending_amount=0.0,paid_amount=%s,state_new='paid',check_process_dn='t' where id=%s",(paid_amount,i.id))
								elif debit_line.pending_amount!=debit_line.receipt_amount:
									# pending_amount=debit_line.pending_amount-debit_line.receipt_amount
									srch_debit=self.pool.get('debit.note').search(cr,uid,[('debit_note_no','=',debit_note_no)])
									for i in self.pool.get('debit.note').browse(cr,uid,srch_debit):
										pending_amount=i.pending_amount-i.receipt_amount
										paid_amount=i.receipt_amount+i.paid_amount
										# self.pool.get('debit.note').write(cr,uid,i.id,{'state_new':'open','credit_amount_srch':pending_amount})
										cr.execute("update debit_note set pending_amount=%s,paid_amount=%s,state_new='open' where id=%s",(pending_amount,paid_amount,i.id))
						for invoice_line in ln.invoice_adhoc_one2many:
							invoice_number = invoice_line.invoice_number
							invoice_date = 	invoice_line.invoice_date
							cse_name = emp_code = ''
							if invoice_line.check_invoice == True :
								date1= datetime.strptime(invoice_line.invoice_date, '%Y-%m-%d').date()
								invoice_date= date1.strftime("%d-%m-%Y")
								invoice_date_concate = [invoice_date,invoice_date_concate]
								invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))
								invoice_num = [str(invoice_line.invoice_number),invoice_num]
								invoice_num = ' / '.join(filter(bool,invoice_num))
								emp_code = str(invoice_line.cse.emp_code)
								main_str = "select name from resource_resource where code ilike '" + "%" + str(emp_code) + "%'"
								cr.execute(main_str)
								first_name = cr.fetchone()
								if first_name:
									cse_name = str(first_name[0]) +' '+str(invoice_line.cse.last_name)
								grand_total += invoice_line.grand_total_amount
								cse_name_id = invoice_line.cse.id
								srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[('id','>',0),('invoice_number','=',invoice_number)])
								for adhoc in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
									invoice_paid_date = datetime.now().date()
									self.pool.get('invoice.adhoc.master').write(cr,uid,adhoc.id,{'invoice_paid_date':invoice_paid_date,})
									invoice_history_srch = self.pool.get('payment.contract.history').search(cr,uid,[('invoice_number','=',invoice_number)])
									if invoice_history_srch:
										for invoice_history in self.pool.get('payment.contract.history').browse(cr,uid,invoice_history_srch):
											self.pool.get('payment.contract.history').write(cr,uid,invoice_history.id,{'payment_status':'paid'})
		invoice_gross_amount=0.0
		cfob_invoice_no = cfob_invoice_date = customer_cfob=''
		for res in self.browse(cr,uid,ids):
			customer_id = res.customer_name.id
			customer_name = res.customer_name.name
			cust_ou_id = res.customer_name.ou_id
			tan_no = res.customer_name.tan_no
			for ln_itds in res.sales_receipts_one2many:
				if res.customer_name.name == 'CFOB':
					for cfob_line in ln_itds.sales_other_cfob_one2many:
						customer_cfob = cfob_line.customer_cfob
						cust_cfob_id = cfob_line.cust_cfob_id
						cfob_invoice_no = [str(cfob_line.ref_no),cfob_invoice_no]
						cfob_invoice_no = ' / '.join(filter(bool,cfob_invoice_no))
						cfob_invoice_date = [cfob_line.ref_date,cfob_invoice_date]
						cfob_invoice_date = ' / '.join(filter(bool,cfob_invoice_date))
					for invoice_line_cfob in ln_itds.invoice_cfob_one2many:
						if invoice_line_cfob.cfob_chk_invoice == True:
							customer_id= invoice_line_cfob.partner_id.id
							customer_name= invoice_line_cfob.partner_id.name
							cust_ou_id = invoice_line_cfob.partner_id.ou_id
							tan_no = invoice_line_cfob.partner_id.tan_no
							invoice_num = [str(invoice_line_cfob.invoice_number),invoice_num]
							invoice_num = ' / '.join(filter(bool,invoice_num))
							invoice_date_concate = [invoice_line_cfob.invoice_date,invoice_date_concate]
							invoice_date_concate = ' / '.join(filter(bool,invoice_date_concate))
							cfob_invoice_gross=invoice_line_cfob.grand_total_amount
							cse_name_id = invoice_line_cfob.cse.id
				if ln_itds.type == 'credit':
					invoice_gross_amount+=ln_itds.credit_amount
				if ln_itds.acc_status == 'against_ref':
					if ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'debit':
						self.pool.get('itds.adjustment').create(cr,uid,{
								'receipt_no':receipt_no,
								'receipt_date':res.receipt_date,
								'gross_amt':invoice_gross_amount, 
								'pending_amt':ln_itds.debit_amount,
								'itds_amt':ln_itds.debit_amount,
								'tan_no':res.customer_name.tan_no if res.customer_name.tan_no else False,
								'invoice_no':invoice_num if invoice_num else cfob_invoice_no,
								'invoice_date':invoice_date_concate if invoice_date_concate else cfob_invoice_date ,
								'customer_name_char':customer_cfob if customer_cfob else customer_name ,
								'customer_name': customer_id, 
								'customer_id': cust_ou_id if cust_ou_id else cust_cfob_id ,
								'itds_cse':cse_name_id,
							})
						self.write(cr,uid,rec.id,{'acc_status_new':res.acc_status})
					elif ln_itds.account_id.account_selection == 'itds_receipt' and ln_itds.type == 'credit':
						for lns in ln_itds.revert_itds_one2many:
							if lns.check == True:
								total_pr = lns.total_revert + lns.partial_revert if lns.partial_revert else lns.pending_amt 
								pending_amount=lns.pending_amt - (lns.partial_revert if lns.partial_revert else lns.pending_amt)
								self.pool.get('itds.adjustment').write(cr,uid,lns.id,{
														'pending_amt':pending_amount,
														'state':'partially_reversed' if pending_amount else 'fully_reversed' ,
														'total_revert':total_pr,
														'partial_revert':0.0})
							else:
								self.pool.get('itds.adjustment').write(cr,uid,lns.id,{'revert_id':False})
					if ln_itds.account_id.account_selection == 'security_deposit' and ln_itds.type == 'debit':
						self.pool.get('security.deposit').create(cr,uid,{
							'security_id':ln_itds.id,
							'cse':cse_name_id,
							'ref_no':res.receipt_no,
							'ref_date':res.receipt_date,
							'ref_amount':ln_itds.debit_amount,
							'pending_amount':ln_itds.debit_amount,
							'security_check_against':True,
							'customer_name':customer_id if customer_id else res.customer_id.id,
							'acc_status_new':ln_itds.acc_status,
							'customer_name_char':customer_name if customer_name else customer_cfob,
						})
				self.pool.get('account.sales.receipts.line').write(cr,uid,ln_itds.id,{'state':'done'})
			self.write(cr,uid,rec.id,{'state':'done','acc_status':''})
			for settlement in self.browse(cr,uid,ids):
				for set_line in settlement.sales_receipts_one2many:
					if set_line.account_id.account_selection == 'advance' and set_line.acc_status == 'advance' and set_line.type == 'credit':
						self.write(cr,uid,settlement.id,{
							'check_settlement':True,
							'advance_pending':set_line.credit_amount,
							'new_ad':True,
							})
						for advance in set_line.advance_one2many:
							self.pool.get('advance.sales.receipts').write(cr,uid,advance.id,{
							'receipt_no':settlement.receipt_no,'ref_no':settlement.receipt_no,
							'receipt_date':settlement.receipt_date,})
				self.delete_draft_records_sales(cr,uid,ids,context=context) 
		for rec in self.browse(cr,uid,ids):
			for set_line in settlement.sales_receipts_one2many:
				if set_line.account_id.account_selection == 'against_ref' and set_line.acc_status == 'against_ref' and set_line.type == 'credit':
					if set_line.invoice_adhoc_history_one2many:
						for inv in set_line.invoice_adhoc_history_one2many:
							self.pool.get('invoice.receipt.history').write(cr,uid,inv.id,{
							'receipt_number':rec.receipt_no,
							'invoice_number':inv.invoice_receipt_history_id.invoice_number,
							'invoice_date':inv.invoice_receipt_history_id.invoice_date})
		for rec_log in self.browse(cr,uid,ids):
			customer_invoice_paid = date1=''
			date1=str(datetime.now().date())
			conv=time.strptime(str(date1),"%Y-%m-%d")
			date1 = time.strftime("%d-%m-%Y",conv)
			if rec_log.customer_name:
				customer_invoice_paid= rec_log.customer_name.name+'   Customer Invoice   Paid  On    '+date1
				customer_invoicepaid_date=self.pool.get('customer.logs').create(cr,uid,{
									'customer_join':customer_invoice_paid,
									'customer_id':rec.customer_name.id})
		for receipt_his in self.browse(cr,uid,ids):
			receipt_no=receipt_his.receipt_no
			cust_name=receipt_his.customer_name.name
			amount = 0.0
			if receipt_his.receipt_date:
				receipt_date=receipt_his.receipt_date
			else:
				receipt_date=datetime.now().date()	
			receipt_type=receipt_his.receipt_type
			for receipt_line in receipt_his.sales_receipts_one2many:
				amount += receipt_line.debit_amount
			self.pool.get('receipt.history').create(cr,uid,{
						'receipt_his_many2one':receipt_his.customer_name.id,
						'receipt_number':receipt_no,
						'reciept_date':receipt_date,
						'reciept_type':receipt_type,
						'reciept_amount':amount})
		self.sales_receipt_account_account(cr,uid,ids)
		self.sync_receipt_history(cr,uid,ids)
		if cfob_sync_flag:
			self.sync_CFOB_customer_entry(cr,uid,ids,context=context)
		self.write(cr,uid,ids[0],{'gst_receipt':True})
		return  {
				'name':'Sales Receipt',
				'view_mode': 'form',
				'view_id': False,
				'view_type': 'form',
				'res_model': 'account.sales.receipts',
				'res_id':rec.id,
				'type': 'ir.actions.act_window',
				'target': 'current',
				'domain': '[]',
				'context': context,
				}

	def check_tax_rate(self, cr, uid, account_id = False, context=None):
		amount_new = amt = 0
		account_id = account_id[0] if isinstance(account_id, list) else account_id
		acc_name = self.pool.get('account.account').browse(cr,uid,account_id).name
		date_now = datetime.now().date()
		a = self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',date_now),('effective_to_date','>=',date_now),('description','!=','gst')])
		if a:
			for x in self.pool.get('account.tax').browse(cr,uid,a):
				amount_new += round(x.amount*100,2)
			amt = str(amount_new)
			if map(int, re.findall(r'\d+', acc_name)):
				if amt not in acc_name:
					raise osv.except_osv(('Alert!'),('Select Advance Receipt "%s" account')  % (amt))
		return True


	def generate_report(self,cr,uid,ids,context=None):
		invoice_number = invoice_amt = ''
		if (isinstance(ids,int)):
			ids=[ids]
		for res in self.browse(cr,uid,ids):
			cr.execute('delete from invoice_cheque_line')
			cr.execute('delete from iob_cheque_line')
			cr.execute('delete from neft_cheque_line')
			cr.execute('delete from advance_line')
			cr.execute('delete from demand_draft_cheque_line') 
			data = self.pool.get('account.sales.receipts').read(cr, uid, [res.id],context)
			datas = {
					'ids': ids,
					'model': 'account.sales.receipts',
					'form': data
					}
			if uid != 1:
					file_format='pdf'
					doc=str(res.receipt_no)
					doc_name='sales_receipt'
					self.pool.get('user.print.detail').update_rec(cr,uid,file_format,doc,doc_name)
						
			for line1 in res.sales_receipts_one2many:
				if line1.account_id.account_selection == 'advance':
						for adv in line1.advance_one2many:
							self.pool.get('advance.line').create(cr,uid,{
										'advance_line_id':res.id,
										'advance_amount':round(adv.ref_amount,2),
										'taxable_amount':round(adv.taxable_amount,2),
										'receipt_no':adv.ref_no,
										'cgst_rate':adv.cgst_rate,
										'cgst_amount':round(adv.cgst_amount,2),
										'sgst_rate':adv.sgst_rate,
										'sgst_amount':round(adv.sgst_amount,2),
										'igst_rate':adv.igst_rate,
										'igst_amount':round(adv.igst_amount,2),
										# 'cess_rate':adv.cess_rate,
										# 'cess_amount':adv.cess_amount,
										})
				if line1.acc_status == 'advance' and line1.account_id.account_selection == False:
						if not line1.advance_one2many:
							self.pool.get('advance.line').create(cr,uid,{
										'advance_line_id':res.id,
										'advance_amount':round(line1.credit_amount,2),
										'taxable_amount':round(line1.credit_amount,2),
										})
				if line1.acc_status == 'against_ref' or line1.acc_status == 'others' : 
					if line1.account_id.account_selection == 'against_ref':
						for ln in line1.invoice_adhoc_one2many:
							if ln.check_invoice == True:

								invoice_number = ln.invoice_number
								invoice_amt = ln.pending_invoice_amount
								invoice_date = ln.invoice_date
								invoice_date = str(invoice_date)
								self.pool.get('invoice.cheque.line').create(cr,uid,{
										'invoice_id_report':res.id,
										'invoice_number':invoice_number,
										'grand_total':invoice_amt,
										'invoice_date':invoice_date,
										})
					if line1.account_id.account_selection == 'iob_one':
						for iob in line1.iob_one_one2many:
							if iob.cheque_no:
								iob_cheque_no = iob.cheque_no
								iob_cheque_date = iob.cheque_date
								iob_drawee = iob.drawee_bank_name.name
								self.pool.get('iob.cheque.line').create(cr,uid,{
									'iob_id_report':res.id,
									'cheque_no':iob_cheque_no,
									'cheque_date':iob_cheque_date,
									'drawee_bank':iob_drawee,
									})

						for neft in line1.neft_one2many:
							if neft.pay_ref_no:
								pay_ref_no = neft.pay_ref_no
								neft_date = neft.neft_date
								beneficiary_bank_name = neft.beneficiary_bank_name
								branch_name=neft.branch_name
								self.pool.get('neft.cheque.line').create(cr,uid,{
									'neft_id_report':res.id,
									'pay_ref_no':pay_ref_no,
									'neft_date':neft_date,
									'beneficiary_bank_name':beneficiary_bank_name,
									'branch_name':branch_name})
	
						for dd in line1.demand_draft_one_one2many:
							if dd.dd_no:
								dd_no = dd.dd_no
								dd_date = dd.dd_date
								demand_draft_drawee_bank_name = dd.demand_draft_drawee_bank_name
								dd_bank_branch_name=dd.dd_bank_branch_name
								self.pool.get('demand.draft.cheque.line').create(cr,uid,{
									'demand_draft_id_report':res.id,
									'dd_no':dd_no,
									'dd_date':dd_date,
									'demand_draft_drawee_bank_name':demand_draft_drawee_bank_name,
									'dd_bank_branch_name':dd_bank_branch_name})

			status_bool = False
			status = []
			for ln in res.sales_receipts_one2many:
				acc_status = ln.acc_status
				if acc_status:
					temp = tuple([acc_status])
					status.append(temp)
					for i in range(0,len(status)):
						for j in range(i+1,len(status)):
							if status[i][0] != status[j][0]:
								status_bool = True

			for line in res.sales_receipts_one2many:
				# if line.account_id.account_selection in ('iob_one','cash') :
				# 	if res.gst_receipt == True:
				# 		return {
				# 				'type': 'ir.actions.report.xml',
				# 				'report_name': 'gst.account.sales.receipts.print',
				# 				'datas': datas,
				# 			   }
				# 	else:
				# 		return {
				# 				'type': 'ir.actions.report.xml',
				# 				'report_name': 'account.sales.receipts.print',
				# 				'datas': datas,
				# 			   }
				if line.account_id.account_selection != False:
					if line.account_id.account_selection in ('against_ref'):
						return {
									'type': 'ir.actions.report.xml',
									'report_name': 'account.sales.receipts.print',
									'datas': datas,
								   }
					if line.account_id.account_selection in ('advance') and res.receipt_date<'2017-07-01':
						return {
									'type': 'ir.actions.report.xml',
									'report_name': 'account.sales.receipts.print',
									'datas': datas,
								   }
					if line.account_id.account_selection in ('advance','iob_one','cash') and res.receipt_date>='2017-07-01':
						return {
								'type': 'ir.actions.report.xml',
								'report_name': 'gst.account.sales.receipts.print',
								'datas': datas,
							   }

account_sales_receipts()


class account_sales_receipts_line(osv.osv):
	_inherit = 'account.sales.receipts.line'


	def add(self, cr, uid, ids, context=None): 
	### Sales receipt line  add button 
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			credit_amount = res.credit_amount 
			debit_amount = res.debit_amount
			acc_id = res.account_id
			acc_selection = acc_id.account_selection
			customer_name = res.customer_name.name
			view_name = name_wizard = ''
			acc_selection_list = ['itds_receipt','against_ref','iob_one','security_deposit',
								  'cash','advance','others' ,'sundry_deposit' ]
			
			if not acc_id.name:
				raise osv.except_osv(('Alert'),('Please Select Account.'))
			
			if 'Scrap Sale' in res.account_id.name and res.type=='credit':
				self.show_scrap_invoices_details(cr,uid,ids,context=context)
				view_name ='gst_account_against_ref_form'
				name_wizard = "Outstanding Scrap Sale Invoice"
				obj='gst_accounting'
				if view_name:
					models_data=self.pool.get('ir.model.data')
					form_view=models_data.get_object_reference(cr, uid, obj, view_name)
					return {
					'name': (name_wizard),
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.sales.receipts.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
					(False, 'calendar'), (False, 'graph')],
					'domain': '[]',
					'nodestroy': True,
					}
			if acc_selection in acc_selection_list:
				if  acc_selection == 'itds_receipt':
					if res.type == 'credit':
						self.show_itds_details(cr,uid,ids,context=context)
						obj='account_sales_branch'
						view_name = 'itds_revert_against_ref_form'
						name_wizard = "ITDS Details"
					else:
						raise osv.except_osv(('Alert'),('No Information'))
	
				elif res.acc_status == 'others' and acc_selection == 'against_ref' and customer_name =='CFOB' and res.type == 'credit':
					view_name = 'account_cofb_other_form_id'
					name_wizard= "CFOB Details."
					obj='account_sales_branch'
					
				elif acc_selection == 'iob_one':
					view_name = 'account_iob_one_form'
					name_wizard= "Add"+" "+acc_id.name+" "+"Details"
					obj='account_sales_branch'

				elif acc_selection == 'security_deposit' and res.acc_status !='new_reference' and res.type == 'debit' and res.state=='done' :
					view_name =  'account_security_deposit_form'
					name_wizard = "Security Deposit Details (Against Reference)"
					obj='account_sales_branch'

				elif acc_selection == 'security_deposit' and res.acc_status =='new_reference' and res.type == 'credit':
					self.show_sec_deposit(cr,uid,ids,context=context)
					view_name = 'account_security_deposit_form_new_reference'
					name_wizard = "Security Deposit Details (New Reference)"
					obj='account_sales_branch'

				elif acc_selection == 'cash':
					raise osv.except_osv(('Alert'),('No Information'))
	
				elif acc_selection == 'advance' and res.type == 'credit':
					view_name =  'gst_account_advance_payment_form'
					name_wizard = "Advance Amount Details"
					obj='gst_accounting'

				elif acc_selection == 'others':
					view_name = 'account_cofb_form'
					name_wizard = "Collected on Behalf of Other Branch (CFOB) Details"
					obj='account_sales_branch'

				elif acc_selection == 'against_ref' and customer_name not in ('CFOB','CBOB'):
					self.show_details(cr,uid,ids,context=context)
					view_name ='account_against_ref_form'
					name_wizard = "Outstanding Invoice"
					obj='account_sales_branch'

				elif acc_selection == 'sundry_deposit' and res.type=='credit' and res.acc_status != 'others':
					self.sundry_deposit_details(cr,uid,ids,context=context)
					view_name = 'account_sundry_deposit_id'
					name_wizard = "Add Sundry Deposit Details"
					obj='account_sales_branch'
				
				elif res.acc_status == 'others' and acc_selection == 'sundry_deposit' and customer_name =='CFOB' and res.type=='credit':
					view_name = 'account_sundry_deposit_id_other'
					name_wizard = "Add Sundry Deposit Details"
					obj='account_sales_branch'
				# As per vijay , 28apr
				# elif acc_selection == 'advance' and res.type == 'debit':
				# 	self.show_details(cr,uid,ids,context=context)
				# 	view_name ='account_advance_against_ref_form'
				# 	name_wizard = "Add Advance Amount Details"
			        if view_name:
				        models_data=self.pool.get('ir.model.data')
				        form_view=models_data.get_object_reference(cr, uid, obj, view_name)
				        return {
					        'name': (name_wizard),
					        'type': 'ir.actions.act_window',
					        'view_id': False,
					        'view_type': 'form',
					        'view_mode': 'form',
					        'res_model': 'account.sales.receipts.line',
					        'target' : 'new',
					        'res_id':int(res_id),
					        'views': [(form_view and form_view[1] or False, 'form'),
							           (False, 'calendar'), (False, 'graph')],
					        'domain': '[]',
					        'nodestroy': True,
				        }
			else:
				raise osv.except_osv(('Alert'),('No Information'))

		return True
	def show_details(self, cr, uid, ids, context=None):
		result = ''
		count = 0
		browse_company = self.pool.get('res.users').browse(cr,uid,1).company_id.name
		string_company = str(browse_company)
		for res in self.browse(cr,uid,ids):
			if res.state =='draft': 
				cust_id=res.receipt_id.customer_name.id
				receipt_id = res.receipt_id.id
				search = self.pool.get('account.sales.receipts').search(cr,uid,[('id','=',receipt_id)])
				if 'Jammu' in string_company:
					cr.execute("select cast(substr(rtrim(split_part(name,' ',7),'%'),1,4) as varchar) from account_account where id="+str(res.account_id.id))
				else:
					cr.execute("select cast(substr(rtrim(split_part(name,' ',6),'%'),1,4) as varchar) from account_account where id="+str(res.account_id.id))
				t = cr.fetchone()
				tax = 'non_taxable' if 'Non Taxable' in res.account_id.name else str(t[0])
				srch1=self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_id_receipt','=',res.id)])
				if srch1:
					for advance in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch1):
						self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'invoice_id_receipt':False,})
				for rec in self.pool.get('account.sales.receipts').browse(cr,uid,search):
					cust_id = rec.customer_name.id
					if cust_id:   
						if res.account_id.gst_applied == True:
							cr.execute("select cast(substr(rtrim(split_part(name,' ',5),'%'),1,4) as varchar) from account_account where id="+str(res.account_id.id))
							t = cr.fetchone()
							tax = 'non_taxable' if 'Non Taxable' in res.account_id.name else str(t[0])
							srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[
																('status','in',('open','printed','partially_writeoff')),
																('partner_id','=',cust_id),
																('invoice_number','!=',''),
																('check_process_invoice','=',False),
																('pending_status','in',('open','pending')),
																('tax_rate','like',tax),'|',('invoice_type','!=','Scrap Sale Invoice'),('invoice_type','=',False)
																])#('invoice_type','!=','Scrap Sale Invoice')
						else:
							print "ssssssssssssssssssssssssssss",cust_id,tax
							srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[
																('status','in',('open','printed','partially_writeoff')),
																('partner_id','=',cust_id),
																('invoice_number','!=',''),
																('check_process_invoice','=',False),
																('pending_status','in',('open','pending')),
																('tax_rate','like',tax),'|',('invoice_type','!=','Scrap Sale Invoice'),('invoice_type','=',False)])#,('invoice_type','!=','Scrap Sale Invoice')
							print "sssssssssssssssssss",srch
						for advance in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
							if res.acc_status == 'against_ref':
								if rec.invoice_number:
									if rec.invoice_number == advance.invoice_number:
										count += 1
										self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'invoice_id_receipt':res.id,})
										self.write(cr,uid,res.id,{'credit_amount':advance.grand_total_amount})
								else:
									self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'invoice_id_receipt':res.id})
					if res.acc_status == 'against_ref':
						customer_name=rec.customer_name.id
						srch_debit=self.pool.get('debit.note').search(cr,uid,[('customer_name','=',customer_name),('state_new','=','open')])
						srch_debit2=self.pool.get('debit.note').search(cr,uid,[('sales_debit_id','=',res.id)])
						if srch_debit or srch_debit2 :
							debt_count =0
							flag=True
							for x in self.pool.get('debit.note').browse(cr,uid,srch_debit):
								for debit_id in x.debit_note_one2many:
									if debit_id.account_id.account_selection=='others':
										flag=False
									if flag:
										search_in_lines = self.pool.get('debit.note.line').search(cr,uid,[('debit_id','=',x.id),('account_id','=',res.account_id.id)])
										if search_in_lines:
											self.pool.get('debit.note').write(cr,uid,x.id,{'sales_debit_id':res.id})
											debt_count +=1
							if debt_count >=1:
								s=self.write(cr,uid,res.id,{'visib':True})
						else:
							s=self.write(cr,uid,res.id,{'visib':False})	
					if count == 1:
						cr.execute("update invoice_adhoc_master set check_invoice=%s where invoice_id_receipt=%s",(True,res.id))
		return True

	def show_scrap_invoices_details(self, cr, uid, ids, context=None):
		result = ''
		count = 0
		for res in self.browse(cr,uid,ids):
			if res.state =='draft': 
				cust_id=res.receipt_id.customer_name.id
				receipt_id = res.receipt_id.id
				search = self.pool.get('account.sales.receipts').search(cr,uid,[('id','=',receipt_id)])
				for rec in self.pool.get('account.sales.receipts').browse(cr,uid,search):
					cust_id = rec.customer_name.id
					if cust_id:   
						if res.account_id.gst_applied == True:
							srch = self.pool.get('invoice.adhoc.master').search(cr,uid,[
																('partner_id','=',cust_id),
																('invoice_number','!=',''),
																('check_process_invoice','=',False),
																('pending_status','in',('open','pending')),
																('invoice_type','=','Scrap Sale Invoice')
																])
						for advance in self.pool.get('invoice.adhoc.master').browse(cr,uid,srch):
							if rec.invoice_number:
								if rec.invoice_number == advance.invoice_number:
									count += 1
									self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'invoice_id_receipt':res.id,})
									self.write(cr,uid,res.id,{'credit_amount':advance.grand_total_amount})
							else:
								self.pool.get('invoice.adhoc.master').write(cr,uid,advance.id,{'invoice_id_receipt':res.id})
					if count == 1:
						cr.execute("update invoice_adhoc_master set check_invoice=%s where invoice_id_receipt=%s",(True,res.id))
		return True

	def save_against_ref(self, cr, uid, ids, context=None):
		flag = False
		total = 0.0
		count = 0
		payment_status = '' 
		inv_adhoc_res = self.pool.get('invoice.adhoc.receipts')
		for res in self.browse(cr,uid,ids):
			payment_status  = res.receipt_id.payment_status
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			for line in res.invoice_adhoc_one2many:
				check_invoice = line.check_invoice
				pending_amount = line.pending_amount
				if check_invoice == True:
					if line.invoice_type != 'product_invoice':
						if line.service_classification != 'exempted' and line.tax_rate not in res.account_id.name:
							if 'NT' in line.invoice_number:
								if 'Non' not in res.account_id.name :
									raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
						# else :
						# 	raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
					flag = True
					if line.partial_payment_amount > line.pending_amount:
						raise osv.except_osv(('Alert'),('Receipt amount cannot be exceeded by pending amount!'))
					if line.partial_payment_amount == 0.0:
						raise osv.except_osv(('Alert'),('Please enter Receipt Amount!'))
					total += line.partial_payment_amount
				
				for inv_line in line.invoice_line_adhoc_12:
					existing_ids = inv_adhoc_res.search(cr,uid,[('sales_receipt_id','=',res.receipt_id.id),('invoice_adhoc_id','=',inv_line.id)])
					if not existing_ids:
						inv_adhoc_res.create(cr,uid,
							{
							 'invoice_adhoc_id': inv_line.id,
							 'sales_receipt_id': res.receipt_id.id
							})
			for line2 in res.debit_note_one2many:
				check_debit=line2.check_debit	
				grand_total = line2.credit_amount_srch
				pending_amount=line2.pending_amount
				entered_amount=line2.receipt_amount
				if check_debit == True:
					if entered_amount==0.0:
						raise osv.except_osv(('Alert'),('Receipt Amount Cannot be Zero.'))
					if pending_amount < entered_amount:
						raise osv.except_osv(('Alert'),('Debit Note Receipt Amount cannot be greater than Pending Amount'))
					flag = True
					total += entered_amount
			if res.type=='debit':
				self.write(cr,uid,res.id,{'debit_amount':total})
			else:
				self.write(cr,uid,res.id,{'credit_amount':total})
		if flag == False:
			raise osv.except_osv(('Alert'),('No invoice selected.'))
		return {'type': 'ir.actions.act_window_close'}

	def save_scrap_sale_against_ref(self, cr, uid, ids, context=None):
		flag = False
		total = 0.0
		count = 0
		payment_status = '' 
		inv_adhoc_res = self.pool.get('invoice.adhoc.receipts')
		for res in self.browse(cr,uid,ids):
			payment_status  = res.receipt_id.payment_status
			credit_amount = res.credit_amount
			debit_amount = res.debit_amount
			for line in res.invoice_adhoc_one2many:
				check_invoice = line.check_invoice
				pending_amount = line.pending_amount
				if check_invoice == True:
					# if line.tax_rate!='18.0' :
					# 	raise osv.except_osv(('Alert'),('Please select proper tax_rate'))
					flag = True
					if line.partial_payment_amount > line.pending_amount:
						raise osv.except_osv(('Alert'),('Receipt amount cannot be exceeded by pending amount!'))
					if line.partial_payment_amount == 0.0:
						raise osv.except_osv(('Alert'),('Please enter Receipt Amount!'))
					total += line.partial_payment_amount
							
			if res.type=='debit':
				self.write(cr,uid,res.id,{'debit_amount':total})
			else:
				self.write(cr,uid,res.id,{'credit_amount':total})
		if flag == False:
			raise osv.except_osv(('Alert'),('No invoice selected.'))
		return {'type': 'ir.actions.act_window_close'}

	def save_advance_payment(self, cr, uid, ids, context=None):
	### save advance payment deatils
		total = 0.0
		cgst_amount=0.0
		sgst_amount=0.0
		taxable_amount=0.0
		for rec in self.browse(cr,uid,ids):
			if rec.advance_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process.'))
			for line in rec.advance_one2many:
				if not line.service_classification:
					raise osv.except_osv(('Alert'),('Please select Service Classification'))
				if not line.ref_amount:
					raise osv.except_osv(('Alert'),('Please provide Ref Amount'))
				if not line.ref_date:
					raise osv.except_osv(('Alert'),('Please provide reference date.'))
				ref_amount = line.ref_amount
				gst_rate=18.0
				total_rate=gst_rate+100
				if line.service_classification not in ('sez','exempted'):
					taxable_amount = (ref_amount * 100)/total_rate
					cgst_amount = (taxable_amount * 9.0)/100
					sgst_amount = (taxable_amount * 9.0)/100
					total += ref_amount
				else:
					taxable_amount=line.ref_amount
					cgst_amount=0.0
					sgst_amount=0.0
					total += ref_amount
				self.pool.get('advance.sales.receipts').write(cr,uid,line.id,{'taxable_amount':round(taxable_amount,2),'cgst_amount':round(cgst_amount,2),'sgst_amount':round(sgst_amount,2)})
				if rec.type=='debit':
					self.write(cr,uid,rec.id,{'debit_amount':total})
				else:
					self.write(cr,uid,rec.id,{'credit_amount':total})

			srch = self.pool.get('account.sales.receipts').search(cr,uid,[('id','=',rec.receipt_id.id)])
			for res in self.pool.get('account.sales.receipts').browse(cr,uid,srch):
				if res.customer_name.id:
					for ln in rec.advance_one2many:
						self.pool.get('advance.sales.receipts').write(cr,uid,ln.id,{'partner_id':res.customer_name.id,'advance_pending':ln.ref_amount})

			return {'type': 'ir.actions.act_window_close'}

	def save_security_deposit(self, cr, uid, ids, context=None):
	### save decurity deposite recored
		total = 0.0
		for rec in self.browse(cr,uid,ids):
			payment_status = rec.receipt_id.payment_status
			
			if rec.acc_status != 'new_reference': 
			## for creating secyrity deposite
				if rec.security_deposit_one2many == []:
					raise osv.except_osv(('Alert'),('No line to process.'))
				for line in rec.security_deposit_one2many:
					total += line.ref_amount
					pending_amount = line.pending_amount

					if not line.cse:
						raise osv.except_osv(('Alert'),('Provide CSE'))
					if not line.ref_no:
						raise osv.except_osv(('Alert'),('Provide Reference No.'))
					if not line.ref_date:
						raise osv.except_osv(('Alert'),('Provide Reference Date')) 

			if rec.acc_status == 'new_reference':
			## for settlement of records
				if rec.security_new_ref_one2many == []:
					raise osv.except_osv(('Alert'),('No line to process.'))
				
				for line_new in rec.security_new_ref_one2many:
					if line_new.security_check_new_ref == True:
						if not line_new.cse:
							raise osv.except_osv(('Alert'),('Provide CSE'))
						if not line_new.ref_no:
							raise osv.except_osv(('Alert'),('Provide Reference No.'))
						if not line_new.ref_date:
							raise osv.except_osv(('Alert'),('Provide Reference Date'))
						ref_amount = line_new.ref_amount
						pending_amount = line_new.pending_amount
						
						if payment_status == 'partial_payment':
							if line_new.partial_payment_amount > line_new.pending_amount or line_new.partial_payment_amount == 0.0:
								raise osv.except_osv(('Alert'),('Amount cannot be greater than pending amount!'))
							
							# if line_new.partial_payment_amount - line_new.pending_amount == 0.0 :
							# 	raise osv.except_osv(('Alert'),('Select Full Payment to proceed '))
							total += line_new.partial_payment_amount
					
						if payment_status == 'full_payment':
							total += line_new.pending_amount
							if line_new.partial_payment_amount:
								raise osv.except_osv(('Alert'),('Partial Amount should be Zero'))


			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':total})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':total})

		return {'type': 'ir.actions.act_window_close'}

account_sales_receipts_line()


class account_others_receipts(osv.osv): 
#### Main class to store Other receipts
	_inherit = 'account.others.receipts'
	_order = 'receipt_date desc'

	def process(self, cr, uid, ids, context=None): 
	### Other receipt process button
		dr_total = cr_total = neft_amount = ref_amount = primary_amount = cheque_amount_iob2 =0.0
		post=[]
		iob_one_others_id = neft_others_id = advance_others_id = primary_cost_others_id =receipt_date= ''
		cheque_amount = dd_amount = 0.0 
		demand_draft_others_id = others_iob_two_id = cheque_no = ''
		today_date = datetime.now().date()
		py_date = False
		models_data=self.pool.get('ir.model.data')
		for res in self.browse(cr,uid,ids):
			if res.receipt_date:
					check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
					if check_bool:
						if res.receipt_date != str(today_date):
							raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
					else:
						py_date = str(today_date + relativedelta(days=-5))
						if res.receipt_date < str(py_date) or res.receipt_date > str(today_date):
							raise osv.except_osv(('Alert'),('Kindly select Receipt Date 5 days earlier from current date.'))
					receipt_date=res.receipt_date	
			else:
				receipt_date=datetime.now().date()
			if res.others_receipt_one2many == []:
				raise osv.except_osv(('Alert'),('No line to proceed.'))
			for line in res.others_receipt_one2many:
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
			if round(dr_total,2) != round(cr_total,2):
				raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

			if dr_total == 0.0 or cr_total == 0.0:
				raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
				
		for res in self.browse(cr,uid,ids):
		## validation on process button
			for line in res.others_receipt_one2many:
				acc_selection = line.account_id.account_selection
				account_name = line.account_id.name

				if line.credit_amount:
					if line.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				if line.debit_amount:
					if line.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))

				if acc_selection == 'iob_one':
					for iob_one_line in line.iob_one_others_one2many:
						cheque_no = iob_one_line.cheque_no  
						iob_one_others_id = iob_one_line.iob_one_others_id.id
						cheque_amount += iob_one_line.cheque_amount
						
						if cheque_no:
							for n in str(cheque_no):
								p = re.compile('([0-9]{6}$)')
								if p.match(cheque_no)== None :
									raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque No.'))

						if not iob_one_line.cheque_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not iob_one_line.cheque_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not iob_one_line.drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not iob_one_line.bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
						if not iob_one_line.selection_cts:
							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))
					
					amount =line.debit_amount if line.debit_amount else line.credit_amount
					if amount and cheque_amount and amount != cheque_amount:
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
					
					for demand_draft_line in line.demand_draft_other_one_one2many:
						demand_draft_others_id = demand_draft_line.demand_draft_others_id.id
						dd_no = demand_draft_line.dd_no
						dd_amount += demand_draft_line.dd_amount

						for n in str(demand_draft_line.dd_no):
							p = re.compile('([0-9]{6,9}$)')
							if p.match(demand_draft_line.dd_no)== None :
								self.pool.get('demand.draft.sales.receipts').create(cr,uid,{'dd_no':''})
								raise osv.except_osv(('Alert!'),('Please Enter 6 to 9 digit Demand draft Number.'))

						if not demand_draft_line.dd_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not demand_draft_line.dd_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not demand_draft_line.demand_draft_drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not demand_draft_line.dd_bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
						if not demand_draft_line.selection_cts:
							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))

					amount =line.debit_amount if line.debit_amount else line.credit_amount
					if amount and dd_amount and amount != dd_amount:
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
						
					for neft_line in line.neft_others_one2many:
						neft_others_id = neft_line.neft_others_id.id
						neft_amount += neft_line.neft_amount

						if not neft_line.beneficiary_bank_name:
							raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
						if not neft_line.pay_ref_no:
							raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
						if not neft_line.neft_amount:
							raise osv.except_osv(('Alert!'),('Please provide Amount for NEFT/RTGS.'))
					
					amount =line.debit_amount if line.debit_amount else line.credit_amount
					if amount and neft_amount and amount != neft_amount:
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
						
					if demand_draft_others_id :
						if line.debit_amount:
							if dd_amount != line.debit_amount:
								raise osv.except_osv(('Alert'),('Debit amount should be equal'))
						if line.credit_amount:
							if dd_amount != line.credit_amount:
								raise osv.except_osv(('Alert'),('credit amount should be equal'))

					if not iob_one_others_id:
						if not neft_others_id:
							if not demand_draft_others_id:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if not neft_others_id:
						if iob_one_others_id :
							if line.debit_amount:
								if cheque_amount != line.debit_amount:
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if line.credit_amount:
								if cheque_amount != line.credit_amount:
									raise osv.except_osv(('Alert'),('credit amount should be equal'))

						if not iob_one_others_id:
							if neft_others_id:
								if line.debit_amount:
									if neft_amount != line.debit_amount:
										raise osv.except_osv(('Alert'),(' Debit amount should be equal'))
								if line.credit_amount:
									if neft_amount != line.credit_amount:
										raise osv.except_osv(('Alert'),('credit amount should be equal'))
							
				if acc_selection == 'advance':
					for advance_line in line.advance_others_one2many:
						advance_others_id = advance_line.advance_others_id.id
						ref_amount += advance_line.ref_amount
						
						if not advance_others_id:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						
						if advance_others_id:
							if line.debit_amount:
								if ref_amount != line.debit_amount:
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if line.credit_amount:
								if ref_amount != line.credit_amount:
									raise osv.except_osv(('Alert'),('credit amount should be equal'))

				if acc_selection == 'primary_cost_service':
					for primary_line in line.primary_cost_others_one2many:
						primary_cost_others_id = primary_line.primary_cost_others_id.id
						primary_amount +=  primary_line.amount
						if not primary_cost_others_id:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
						
						if primary_cost_others_id:
							if line.debit_amount:
								if primary_amount != line.debit_amount:
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if line.credit_amount:
								if primary_amount != line.credit_amount:
									raise osv.except_osv(('Alert'),('credit amount should be equal'))
						
									
				if acc_selection == 'iob_two':
					for iob_two_line in line.iob_two_others_one2many:
						cheque_no = iob_two_line.cheque_no  
						others_iob_two_id = iob_two_line.others_iob_two_id.id
						cheque_amount_iob2 += iob_two_line.cheque_amount
						
						if cheque_no:
							for n in str(cheque_no):
								p = re.compile('([0-9]{6}$)')
								if p.match(cheque_no)== None :
									raise osv.except_osv(('Alert!'),('Please Enter 6 digit Cheque No.'))      
						if not others_iob_two_id:
							raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
	
						if not iob_two_line.cheque_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not iob_two_line.cheque_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not iob_two_line.drawee_bank_name_new:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not iob_two_line.bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
						if not iob_two_line.selection_cts:
							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))#abhi--
					
					amount =line.debit_amount if line.debit_amount else line.credit_amount
					if amount and cheque_amount_iob2 and amount != cheque_amount_iob2:
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))	
					
					for demand_draft_line in line.demand_draft_other_one_one2many:
						demand_draft_others_id = demand_draft_line.demand_draft_others_id.id
						dd_no = demand_draft_line.dd_no
						dd_amount += demand_draft_line.dd_amount

						for n in str(demand_draft_line.dd_no):
							p = re.compile('([0-9]{6,9}$)')
							if p.match(demand_draft_line.dd_no)== None :
								self.pool.get('demand.draft.sales.receipts').create(cr,uid,{'dd_no':''})
								raise osv.except_osv(('Alert!'),('Please Enter 6 to 9 digit Demand draft Number.'))

						if not demand_draft_line.dd_date:
							raise osv.except_osv(('Alert'),('Please provide Cheque Date.'))
						if not demand_draft_line.dd_no:
							raise osv.except_osv(('Alert'),('Please provide Cheque Number.'))
						if not demand_draft_line.demand_draft_drawee_bank_name:
							raise osv.except_osv(('Alert'),('Please provide Drawee Bank Name.'))
						if not demand_draft_line.dd_bank_branch_name:
							raise osv.except_osv(('Alert'),('Please provide Branch Bank Name.'))
						if not demand_draft_line.selection_cts:
							raise osv.except_osv(('Alert'),('Please provide CTS/NON CTS.'))

					amount =line.debit_amount if line.debit_amount else line.credit_amount
					if amount and dd_amount and amount != dd_amount:
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
						
					for neft_line in line.neft_others_one2many:
						neft_others_id = neft_line.neft_others_id.id
						neft_amount += neft_line.neft_amount

						if not neft_line.beneficiary_bank_name:
							raise osv.except_osv(('Alert!'),('Please provide Beneficiary Bank Name.'))
						if not neft_line.pay_ref_no:
							raise osv.except_osv(('Alert!'),('Please provide Payment Reference Number.'))
						if not neft_line.neft_amount:
							raise osv.except_osv(('Alert!'),('Please provide Amount for NEFT/RTGS.'))
					
					amount =line.debit_amount if line.debit_amount else line.credit_amount
					if amount and neft_amount and amount != neft_amount:
						raise osv.except_osv(('Alert!'),('wizard amount is not equal'))
						
					if demand_draft_others_id :
						if line.debit_amount:
							if dd_amount != line.debit_amount:
								raise osv.except_osv(('Alert'),('Debit amount should be equal'))
						if line.credit_amount:
							if dd_amount != line.credit_amount:
								raise osv.except_osv(('Alert'),('credit amount should be equal'))

					if not others_iob_two_id:
						if not neft_others_id:
							if not demand_draft_others_id:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
					if not neft_others_id:
						if others_iob_two_id :
							if line.debit_amount:
								if cheque_amount_iob2 != line.debit_amount:
									raise osv.except_osv(('Alert'),('Debit amount should be equal'))
							if line.credit_amount:
								if cheque_amount_iob2 != line.credit_amount:
									raise osv.except_osv(('Alert'),('credit amount should be equal'))

						if not others_iob_two_id:
							if neft_others_id:
								if line.debit_amount:
									if neft_amount != line.debit_amount:
										raise osv.except_osv(('Alert'),(' Debit amount should be equal'))
								if line.credit_amount:
									if neft_amount != line.credit_amount:
										raise osv.except_osv(('Alert'),('credit amount should be equal'))

					if others_iob_two_id:
						if line.debit_amount:
							if cheque_amount_iob2 != line.debit_amount:
								raise osv.except_osv(('Alert'),('Debit amount should be equal'))
						if line.credit_amount:
							if cheque_amount_iob2 != line.credit_amount:
								raise osv.except_osv(('Alert'),('credit amount should be equal'))    

		for t in self.browse(cr,uid,ids): #20may
			for i in t.others_receipt_one2many:
				acc_selection = i.account_id.account_selection
				if acc_selection == 'sundry_deposit':
					for j in i.sundry_deposit_other_one2many:
						if j.sundry_other:
							amt=j.pending_amount -j.partial_amount
							self.pool.get('sundry.deposit').write(cr,uid,j.id,{'sundry_check_process':True if amt else False })
							self.pool.get('sundry.deposit.history').create(cr,uid,{
													'sundry_deposit_history_id':j.id,
													'sundry_id':i.id,
													'customer_name':j.customer_name.id,
													'payment_no':j.payment_no,
													'payment_amount':j.payment_amount,
													'payment_date':j.payment_date,
													'pending_amount':amt,
													'partial_payment_amount':j.partial_amount,
													'settle_date':t.receipt_date,
													'cse':j.cse.id,
													})
		for rec in self.browse(cr,uid,ids):
			receipt_no = seq_start= temp_count=''
			seq= count=0
			ou_code = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
			ab_code = self.pool.get('res.users').browse(cr,uid,uid).company_id.others_receipts_id
			seq_srch=self.pool.get('ir.sequence').search(cr,uid,[('code','=','account.others.receipts')])
			if seq_srch:
				seq_start=self.pool.get('ir.sequence').browse(cr,uid,seq_srch[0]).number_next
			
			month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
			today_date = datetime.now().date()

			year = today_date.year
			year1=today_date.strftime('%y')
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
			today_date = datetime.now().date()
			count=0
			seq_start=1
			if  ou_code and ab_code:
				# cr.execute("select count(id) from account_others_receipts where state not in ('draft') and receipt_date >='2017-06-30' and receipt_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				cr.execute("select count(id) from account_others_receipts where state not in ('draft') and receipt_date >='2017-07-01' and receipt_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=count+seq_start	
				#seq = self.pool.get('ir.sequence').get(cr, uid, 'account.others.receipts')
				receipt_no = ou_code+ab_code+str(financial_year)+str(seq).zfill(5)
				existing_receipt_id = self.pool.get('account.others.receipts').search(cr,uid,[('receipt_no','=',receipt_no)])
				if existing_receipt_id:
					receipt_no = ou_code+ab_code+str(financial_year)+str(seq+1).zfill(5)
			self.write(cr,uid,ids,{'receipt_no':receipt_no,'receipt_date': receipt_date,'voucher_type':'Receipt (Others)'})
			date = receipt_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id
			date = rec.receipt_date
			search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
			for var in self.pool.get('account.period').browse(cr,uid,search_date):
				period_id = var.id
					
			srch_jour_acc = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Bank')])
			for jour_acc in self.pool.get('account.journal').browse(cr,uid,srch_jour_acc):
				journal_id = jour_acc.id
				
			move = self.pool.get('account.move').create(cr,uid,{
					'journal_id':journal_id,####hardcoded not confirm by pcil
					'state':'posted',
					'date':date,
					'name':receipt_no,
					'narration':rec.narration if rec.narration else '',
					},context=context)

			for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
				for ln in rec.others_receipt_one2many:
					if ln.debit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
									'move_id':line1.id,
									'account_id':ln.account_id.id,
									'debit':ln.debit_amount,
									'name':rec.customer_name.name if rec.customer_name.name else '',
									'journal_id':journal_id,
									'period_id':period_id,
									'date':date,
									'ref':receipt_no},context=context)
					if ln.credit_amount:
						self.pool.get('account.move.line').create(cr,uid,{
								'move_id':line1.id,
								'account_id':ln.account_id.id,
								'credit':ln.credit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_id,
								'period_id':period_id,
								'date':date,
								'ref':receipt_no},context=context)

			self.write(cr,uid,rec.id,{'state':'done'})

			for state_line in rec.others_receipt_one2many:
				self.pool.get('account.others.receipts.line').write(cr,uid,state_line.id,{'state':'done'})
				
		self.delete_draft_records_others(cr,uid,ids,context=context) # Delete the records which are in 'Draft' State
		for receipt_his in self.browse(cr,uid,ids):
			receipt_no=receipt_his.receipt_no
			cust_name=receipt_his.customer_name.name
			if receipt_his.receipt_date:
				receipt_date=receipt_his.receipt_date
			else:
				receipt_date=datetime.now().date()
			receipt_type=receipt_his.receipt_type
			curr_id = ''
			amount = 0.0
			for receipt_line in receipt_his.others_receipt_one2many:
				amount +=  receipt_line.debit_amount
			var = self.pool.get('res.partner').search(cr,uid,[('name','=',cust_name)])
			for jj in var:
				curr_id=jj
			self.pool.get('receipt.history').create(cr,uid,{
				'receipt_his_many2one':curr_id,
				'receipt_number':receipt_no,
				'reciept_date':receipt_date,
				'reciept_type':receipt_type,
				'reciept_amount':amount})
		
			srch = self.pool.get('account.others.receipts.line').search(cr,uid,[('other_receipt_id','=',rec.id)])####used for reflection in operation module against employee
			for i in self.pool.get('account.others.receipts.line').browse(cr,uid,srch):
				temp=i.account_id.advance_expence_check
				if  i.account_id.account_selection == 'primary_cost_cse' and temp == True:
					for j in self.pool.get('account.others.receipts.line').browse(cr,uid,srch):
						if j.account_id.account_selection == 'cash':
							for k in i.primary_cost_other_receipt_one2many:
								employee_tempname = k.emp_name.id
								employee_total = k.amount
								if i.debit_amount:
									for emp in self.pool.get('hr.employee').browse(cr,uid,[employee_tempname]):
										employee_total +=  emp.debit
									self.pool.get('hr.employee').write(cr,uid,employee_tempname,{'debit':employee_total})
								if i.credit_amount:
									for emp in self.pool.get('hr.employee').browse(cr,uid,[employee_tempname]):
										employee_total += emp.credit
									self.pool.get('hr.employee').write(cr,uid,employee_tempname,{'credit':employee_total})
		self.sync_others_receipt_history(cr,uid,ids)
	
		return  {
			'name':'Other Receipts Entry',
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'account.others.receipts',
			'res_id':rec.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': '[]',
			'context': context,
		}
account_others_receipts()

class cofb_sales_receipts(osv.osv):
#### save CFOB invoice details(other branch deatils)
	_inherit = 'cofb.sales.receipts'
	_rec_name='customer_cfob'
	
	def _get_tax_rate(self, cr, uid, context=None):	
	### get dynamic details of tax rate 	
		tax_list2=tax_list3=[]        
	 	qry=""" select case when cast(rtrim(split_part(name,' ',6),'%') as varchar )='10.30' then cast(rtrim(split_part(name,' ',6),'%') as varchar) 
     when cast(rtrim(split_part(name,' ',6),'%') as varchar )='10.20' then cast(rtrim(split_part(name,' ',6),'%') as varchar) else 
     case when cast(substr(rtrim(split_part(name,' ',6),'%'),5,1) as varchar )='0' then 
        cast(substr(rtrim(split_part(name,' ',6),'%'),1,4) as varchar ) else cast(rtrim(split_part(name,' ',6),'%') as varchar ) end end as tax from account_account where name ilike '%Sundry Debtors service%' and rtrim(split_part(name,' ',6),'%')<>'' order by tax """
	 	qry1=""" select case when cast(rtrim(split_part(name,' ',5),'%') as varchar )='18.0' then cast(rtrim(split_part(name,' ',5),'%') as varchar) 
    				 else cast(rtrim(split_part(name,' ',5),'%') as varchar ) end as tax from account_account where name ilike '%Sundry Debtors GST%' and rtrim(split_part(name,' ',5),'%')<>'' order by tax """
	 	cr.execute(qry)
	 	tax_list=list(cr.fetchall())
	 	tax_list1=[(str(x[0]),"Taxable "+str(x[0])) for x in tax_list]
	 	cr.execute(qry1)
	 	tax_list2=list(cr.fetchall())
	 	tax_list3.extend([(str(x[0]),"Taxable "+str(x[0])) for x in tax_list2])
	 	tax_list1.extend(tax_list3)
	 	tax_list1.extend([('non_taxable','Non-Taxable'),('others','Others')])
	 	return tuple(tax_list1)
	
	_columns = {
								
		'tax_rate':fields.selection(_get_tax_rate,'Tax'),
		'cfob_service_classification':fields.selection([
								('residential','Residential Service'),
								('commercial','Commercial Service'),
								('port','Port Service'),
								('airport','Airport Service'),
								('exempted','Exempted'),
								('others','Others'),
								('sez','SEZ - ZERO RATED'),
								],'Service Classification'),
		   }

cofb_sales_receipts()

class search_sales_receipt_line(osv.osv):
#### class to show search sales receipts 
	_inherit  = 'search.sales.receipt.line'
	_rec_name = 'receipt_no'
	_order = 'receipt_date desc'

search_sales_receipt_line()


class itds_adjustment(osv.osv):
#### ITDS adjustment class
	_inherit = "itds.adjustment"
	_rec_name = 'receipt_no'
	_order = 'receipt_date desc'

itds_adjustment()

class advance_sales_receipts(osv.osv):
#### class for to save record of advance receipts
	_inherit = 'advance.sales.receipts'
	_columns ={

	'taxable_amount':fields.float('Taxable Amount'),
	'cgst_rate':fields.char('CGST Rate.',size=10),
	'cgst_amount':fields.float('CGST Amount'),
	'sgst_rate':fields.char('SGST/UTGST Rate.',size=10),
	'sgst_amount':fields.float('SGST/UTGST Amount'),
	'igst_rate':fields.char('IGST Rate.',size=10),
	'igst_amount':fields.float('IGST Amount'),
	'service_classification':fields.selection([
							('residential','Residential Service'),
							('commercial','Commercial Service'),
							('port','Port Service'),
							('airport','Airport Service'),
							('exempted','Exempted'),
							('sez','SEZ'),
							],'Service Classification'),
	}

	_defaults = {

	'cgst_rate':'9.00%',
	'sgst_rate':'9.00%',
	'igst_rate':'18.00%',
	}

	def onchange_advance_amount(self, cr, uid, ids, service_classification,ref_amount, context=None):
		data = {}
		if ref_amount:
			print service_classification
			if service_classification=='':
				raise osv.except_osv(('Alert'),('Kindly select Service Classification!'))
			gst_rate=18.0
			total_rate=gst_rate+100
			if service_classification not in ('sez','exempted'):
				taxable_amount = (ref_amount * 100)/total_rate
				cgst_amount = (taxable_amount * 9.0)/100
				sgst_amount = (taxable_amount * 9.0)/100
				# taxable_amount = ref_amount - cgst_amount - sgst_amount
				data.update(
					{
						'taxable_amount': round(taxable_amount,2),
						'cgst_amount': round(cgst_amount,2),
						'sgst_amount': round(sgst_amount,2),
					})
			else:
				data.update(
					{
						'taxable_amount': ref_amount,
						'cgst_amount': 0.00,
						'sgst_amount':0.00,
					})
		return {'value':data}

advance_sales_receipts()


class advance_line(osv.osv):
	_name = 'advance.line'
	_columns = {

	'advance_amount':fields.float('Advance Amount'),
	'taxable_amount':fields.float('Taxable Amount'),
	'advance_line_id':fields.many2one('account.sales.receipts','Sales Receipt'),
	'receipt_no':fields.char('Receipt No.',size=20),
	'cgst_rate':fields.char('CGST Rate.',size=10),
	'cgst_amount':fields.float('CGST Amount'),
	'sgst_rate':fields.char('SGST/UTGST Rate.',size=10),
	'sgst_amount':fields.float('SGST/UTGST Amount'),
	'igst_rate':fields.char('IGST Rate.',size=10),
	'igst_amount':fields.float('IGST Amount'),
	'cess_rate':fields.char('CESS Rate.',size=10),
	'cess_amount':fields.float('Cess Amount'),
	}

advance_line()
