# Version 1.0.020 --->  Added Changes of Debtors Reconciliation for Collection at Head Office,Collection at Other Branch
# Version 1.0.022 --->  Added Changes of Statement Sundry Debtors
# Version 1.0.027 --->  Added Changes of Debtor reconsilation as per requirement
# Version 1.0.031 --->  Added Changes of Debtor reconsilation as per requirement
# Version 1.0.039 --->  Added Condition of partial_payment in outstanding given by Vijay on 10 SEP 15 
# Version 1.0.045 --->  Advance and Other Branch Collection included in collection of period on 21 sept
# Version 1.0.050 --->  issue of taxable_10_30 in opening and closing outstanding
# Version 1.0.051 --->  issue of taxable_10_30 in opening outstanding(Full writeoff) and CFOB 
# Version 1.0.052 -->  Added journal voucher for cfob
# Version 1.0.054    --Added Non taxable
# Version 1.0.054    -- Changes Related to Collection of period 13 oct 15
# Version 1.0.059    -- Changes Related to cancelled invoice and check bounce entry added in opening outstanding
# version 1.0.061 --> Changes Related to NON TAXABLE Column for CFOB Scenario

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
import openerp

class monthly_report(osv.osv):
	_inherit = 'monthly.report'
	_columns = {

#Taxable 1
		'opening_outstanding1':fields.float('Opening Outstanding1'),
		'month_bill1':fields.float('Billing during the month1'),
		'period_collection1':fields.float('Collection for the Period1'),
		'head_office_collection1':fields.float('Collection at Head Office1'),
		'collection_other_branches1':fields.float('Collection at Other Branches1'),
		'credit_note1':fields.float('Credit Notes1'),
		'advance_receipt1':fields.float('Advance Receipt Billed during the Period1'),
		'other_branch_collection1':fields.float('Other Branch Collection1'),
		'debit_notes1':fields.float('Debit Notes1'),
		'cheques_dishonoured1':fields.float('Cheques Dishonoured1'),
		'excess_collection1':fields.float('Excess Collection / Advance Receipt1'),
		'sales_refund1':fields.float('Sales Refund to Parties (against Credit Notes)1'),
		'outstanding1':fields.float('Outstanding as on1'),
		'total_outstanding1':fields.float('Total Outstanding1'),
#Taxable 2
		'opening_outstanding2':fields.float('Opening Outstanding2'),
		'month_bill2':fields.float('Billing during the month2'),
		'period_collection2':fields.float('Collection for the Period2'),
		'head_office_collection2':fields.float('Collection at Head Office2'),
		'collection_other_branches2':fields.float('Collection at Other Branches2'),
		'credit_note2':fields.float('Credit Notes2'),
		'advance_receipt2':fields.float('Advance Receipt Billed during the Period2'),
		'other_branch_collection2':fields.float('Other Branch Collection2'),
		'debit_notes2':fields.float('Debit Notes2'),
		'cheques_dishonoured2':fields.float('Cheques Dishonoured2'),
		'excess_collection2':fields.float('Excess Collection / Advance Receipt2'),
		'sales_refund2':fields.float('Sales Refund to Parties (against Credit Notes)2'),
		'outstanding2':fields.float('Outstanding as on2'),
		'total_outstanding2':fields.float('Total Outstanding2'),
#Taxable 3
		'opening_outstanding3':fields.float('Opening Outstanding3'),
		'month_bill3':fields.float('Billing during the month3'),
		'period_collection3':fields.float('Collection for the Period3'),
		'head_office_collection3':fields.float('Collection at Head Office3'),
		'collection_other_branches3':fields.float('Collection at Other Branches3'),
		'credit_note3':fields.float('Credit Notes3'),
		'advance_receipt3':fields.float('Advance Receipt Billed during the Period3'),
		'other_branch_collection3':fields.float('Other Branch Collection3'),
		'debit_notes3':fields.float('Debit Notes3'),
		'cheques_dishonoured3':fields.float('Cheques Dishonoured3'),
		'excess_collection3':fields.float('Excess Collection / Advance Receipt3'),
		'sales_refund3':fields.float('Sales Refund to Parties (against Credit Notes)3'),
		'outstanding3':fields.float('Outstanding as on3'),
		'total_outstanding3':fields.float('Total Outstanding3'),
#Taxable 4
		'opening_outstanding4':fields.float('Opening Outstanding4'),
		'month_bill4':fields.float('Billing during the month4'),
		'period_collection4':fields.float('Collection for the Period4'),
		'head_office_collection4':fields.float('Collection at Head Office4'),
		'collection_other_branches4':fields.float('Collection at Other Branches4'),
		'credit_note4':fields.float('Credit Notes4'),
		'advance_receipt4':fields.float('Advance Receipt Billed during the Period4'),
		'other_branch_collection4':fields.float('Other Branch Collection4'),
		'debit_notes4':fields.float('Debit Notes4'),
		'cheques_dishonoured4':fields.float('Cheques Dishonoured4'),
		'excess_collection4':fields.float('Excess Collection / Advance Receipt4'),
		'sales_refund4':fields.float('Sales Refund to Parties (against Credit Notes)4'),
		'outstanding4':fields.float('Outstanding as on4'),
		'total_outstanding4':fields.float('Total Outstanding4'),		
#Taxable 5
		'opening_outstanding5':fields.float('Opening Outstanding5'),
		'month_bill5':fields.float('Billing during the month5'),
		'period_collection5':fields.float('Collection for the Period5'),
		'head_office_collection5':fields.float('Collection at Head Office5'),
		'collection_other_branches5':fields.float('Collection at Other Branches5'),
		'credit_note5':fields.float('Credit Notes5'),
		'advance_receipt5':fields.float('Advance Receipt Billed during the Period5'),
		'other_branch_collection5':fields.float('Other Branch Collection5'),
		'debit_notes5':fields.float('Debit Notes5'),
		'cheques_dishonoured5':fields.float('Cheques Dishonoured5'),
		'excess_collection5':fields.float('Excess Collection / Advance Receipt5'),
		'sales_refund5':fields.float('Sales Refund to Parties (against Credit Notes)5'),
		'outstanding5':fields.float('Outstanding as on5'),
		'total_outstanding5':fields.float('Total Outstanding5'),

#Taxable 6
		'opening_outstanding6':fields.float('Opening Outstanding6'),
		'month_bill6':fields.float('Billing during the month6'),
		'period_collection6':fields.float('Collection for the Period6'),
		'head_office_collection6':fields.float('Collection at Head Office6'),
		'collection_other_branches6':fields.float('Collection at Other Branches6'),
		'credit_note6':fields.float('Credit Notes6'),
		'advance_receipt6':fields.float('Advance Receipt Billed during the Period6'),
		'other_branch_collection6':fields.float('Other Branch Collection6'),
		'debit_notes6':fields.float('Debit Notes6'),
		'cheques_dishonoured6':fields.float('Cheques Dishonoured6'),
		'excess_collection6':fields.float('Excess Collection / Advance Receipt6'),
		'sales_refund6':fields.float('Sales Refund to Parties (against Credit Notes)6'),
		'outstanding6':fields.float('Outstanding as on6'),
		'total_outstanding6':fields.float('Total Outstanding6'),
#Taxable 7		
		'opening_outstanding7':fields.float('Opening Outstanding7'),
		'month_bill7':fields.float('Billing during the month7'),
		'period_collection7':fields.float('Collection for the Period7'),
		'head_office_collection7':fields.float('Collection at Head Office7'),
		'collection_other_branches7':fields.float('Collection at Other Branches7'),
		'credit_note7':fields.float('Credit Notes7'),
		'advance_receipt7':fields.float('Advance Receipt Billed during the Period7'),
		'other_branch_collection7':fields.float('Other Branch Collection7'),
		'debit_notes7':fields.float('Debit Notes7'),
		'cheques_dishonoured7':fields.float('Cheques Dishonoured7'),
		'excess_collection7':fields.float('Excess Collection / Advance Receipt7'),
		'sales_refund7':fields.float('Sales Refund to Parties (against Credit Notes)7'),
		'outstanding7':fields.float('Outstanding as on7'),
		'total_outstanding7':fields.float('Total Outstanding7'),
		#'total_outstanding8':fields.float('Total Outstanding8'),

#Taxable 8		
		'opening_outstanding8':fields.float('Opening Outstanding8'),
		'month_bill8':fields.float('Billing during the month8'),
		'period_collection8':fields.float('Collection for the Period8'),
		'head_office_collection8':fields.float('Collection at Head Office8'),
		'collection_other_branches8':fields.float('Collection at Other Branches8'),
		'credit_note8':fields.float('Credit Notes8'),
		'advance_receipt8':fields.float('Advance Receipt Billed during the Period8'),
		'other_branch_collection8':fields.float('Other Branch Collection8'),
		'debit_notes8':fields.float('Debit Notes8'),
		'cheques_dishonoured8':fields.float('Cheques Dishonoured8'),
		'excess_collection8':fields.float('Excess Collection / Advance Receipt8'),
		'sales_refund8':fields.float('Sales Refund to Parties (against Credit Notes)8'),
		'outstanding8':fields.float('Outstanding as on8'),
		#'outstanding8':fields.float('Outstanding as on8'),
		#'total_outstanding8':fields.float('Total Outstanding8'),
		'total_outstanding8':fields.float('Total Outstanding8'),

#Taxable 10
		'opening_outstanding10':fields.float('Opening Outstanding10'),
		'month_bill10':fields.float('Billing during the month10'),
		'period_collection10':fields.float('Collection for the Period10'),
		'head_office_collection10':fields.float('Collection at Head Office10'),
		'collection_other_branches10':fields.float('Collection at Other Branches10'),
		'credit_note10':fields.float('Credit Notes10'),
		'advance_receipt10':fields.float('Advance Receipt Billed during the Period10'),
		'other_branch_collection10':fields.float('Other Branch Collection10'),
		'debit_notes10':fields.float('Debit Notes10'),
		'cheques_dishonoured10':fields.float('Cheques Dishonoured10'),
		'excess_collection10':fields.float('Excess Collection / Advance Receipt10'),
		'sales_refund10':fields.float('Sales Refund to Parties (against Credit Notes)10'),
		'outstanding10':fields.float('Outstanding as on10'),
		'total_outstanding10':fields.float('Total Outstanding10'),

		'month_bill_new_company':fields.float('Billing during the month for new company'),
		'outstanding11':fields.float('Outstanding as on11 new company'),	
		'opening_outstanding11':fields.float('Opening Outstanding11'),
		'collection_other_branches11':fields.float('Collection at Other Branches11'),

		   }

	def stmt_debtors_reconciliation(self, cr, uid, ids, from_date, to_date, context=None):
		import datetime

		from_date_rdm = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
		to_date_rdm = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
		#print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Date Status:',to_date_rdm.month
		for i in range(3,int(from_date_rdm.month)+1):
			from_date1=str(str(from_date_rdm.year)+'-'+str(i).zfill(2)+'-'+str(from_date_rdm.day).zfill(2))
			print 'from date',from_date1
			#from_date2=str(str(from_date_rdm.year)+'-'+str(i+1).zfill(2)+'-'+str(from_date_rdm.day).zfill(2)).date()
			next_month = datetime.date(from_date_rdm.year, i, 1).replace(day=28) + datetime.timedelta(days=4)  # this will never fail
			to_date1 = next_month - datetime.timedelta(days=next_month.day)
			#print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ we are passing this From Date:',from_date1,' To Date:',to_date1
			for line in self.browse(cr, uid, ids, context=context):
				# if outstanding1_rdm!=0 and i!=3:
				# 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding1':outstanding1_rdm})
				# if outstanding2_rdm!=0 and i!=3:
				# 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding2':outstanding2_rdm})
				# if outstanding3_rdm!=0 and i!=3:
				# 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding3':outstanding3_rdm})
				# if outstanding4_rdm!=0 and i!=3:
				# 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding4':outstanding4_rdm})
				# if outstanding5_rdm!=0 and i!=3:
				# 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding5':outstanding5_rdm})
				# if outstanding6_rdm!=0 and i!=3:
				# 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding6':outstanding6_rdm})
				# if outstanding7_rdm!=0 and i!=3:
				# 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding7':outstanding7_rdm})
				# if outstanding10_rdm!=0 and i!=3:
				# 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding10':outstanding10_rdm})
				if i!=3:
					#print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
					outstanding1_rdm=line.outstanding1 if line.outstanding1 else 0
					outstanding2_rdm=line.outstanding2 if line.outstanding2 else 0
					outstanding3_rdm=line.outstanding3 if line.outstanding3 else 0
					outstanding4_rdm=line.outstanding4 if line.outstanding4 else 0
					outstanding5_rdm=line.outstanding5 if line.outstanding5 else 0
					outstanding6_rdm=line.outstanding6 if line.outstanding6 else 0
					outstanding7_rdm=line.outstanding7 if line.outstanding7 else 0
					outstanding8_rdm=line.outstanding8 if line.outstanding8 else 0
					outstanding10_rdm=line.outstanding10 if line.outstanding10 else 0
					outstanding11_rdm=line.outstanding11 if line.outstanding11 else 0
					print '@@@@@@@@@@@@@@@@@@@@@@@@@@ outstanding8_rdm:::::',outstanding8_rdm,from_date1,to_date1
					print 'Parameter Values: opening_outstasnding1',outstanding1_rdm,'opening_outstasnding2',outstanding2_rdm,'opening_outstasnding3',outstanding3_rdm,'opening_outstasnding4',outstanding4_rdm,'opening_outstasnding5:',outstanding5_rdm,' opening_outstasnding6:',outstanding6_rdm,' opening_outstasnding7:',outstanding7_rdm,' opening_outstasnding10:',outstanding10_rdm,'opening_outstasnding11',outstanding11_rdm
					self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context={'opening_outstanding1':outstanding1_rdm,'opening_outstanding2':outstanding2_rdm,'opening_outstanding3':outstanding3_rdm,'opening_outstanding4':outstanding4_rdm,'opening_outstanding5':outstanding5_rdm,'opening_outstanding6':outstanding6_rdm,'opening_outstanding7':outstanding7_rdm,'opening_outstanding8':outstanding8_rdm,'opening_outstanding10':outstanding10_rdm,'opening_outstanding11':outstanding11_rdm})
				else:
					#print '_______________________________________________________________________________________________'
					#print 'Nothing Passing.'
				 	self.stmt_debtors_reconciliation_process(cr, uid, ids, from_date1, to_date1,context=context)
			#print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! we are out form the custome loop !!!!!!!!!'			
	
	def stmt_debtors_reconciliation_process(self, cr, uid, ids, from_date, to_date, context=None):
	        tax_list=['10.20','10.30','12.24','12.36','14.0','14.5','15.0','18.0','non_taxable']
	        for res in self.browse(cr,uid,ids):
	        	date1=datetime.strptime(from_date,'%Y-%m-%d') # 01-04-2017
	        	prev_date=date1-relativedelta(days=1)
	        	prev_month=date1-relativedelta(months=1)
	        	march_cutoff='2017-03-01'
### Opening Outstanding as on  ##    
                # Opening Outstanding => Consider those Invoices which are in outstanding till from date
                        if from_date == '2017-03-01':
                            total_amount_1 = self.opening_for_march(cr,uid,ids,date1,tax_list[0]) 
                            total_amount_2 = self.opening_for_march(cr,uid,ids,date1,tax_list[1])
                            total_amount_3 = self.opening_for_march(cr,uid,ids,date1,tax_list[2])
                            total_amount_4 = self.opening_for_march(cr,uid,ids,date1,tax_list[3])
                            total_amount_5 = self.opening_for_march(cr,uid,ids,date1,tax_list[4])
                            total_amount_6 = self.opening_for_march(cr,uid,ids,date1,tax_list[5])
                            print "tttttttttttttttttttttttttttttt",total_amount_6
                            total_amount_7 = self.opening_for_march(cr,uid,ids,date1,tax_list[6])
                            total_amount_8 = self.opening_for_march(cr,uid,ids,date1,tax_list[7])
                            total_amount_10 = self.opening_for_march(cr,uid,ids,date1,tax_list[8])
                        else:
                            total_amount_1 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[0]) 
                            total_amount_2 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[1])
                            total_amount_3 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[2])
                            total_amount_4 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[3])
                            total_amount_5 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[4])
                            total_amount_6 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[5])
                            print "sssssssssssssssssssssssss1111",total_amount_6
                            total_amount_7 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[6])
                            total_amount_8 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[7])
                            total_amount_10 = self.opening_outstanding(cr,uid,ids,prev_date,date1,tax_list[8])
###pcil opening 

### Add : Billing during the month ##
		        pcil_opening = self.billing_month_new_company (cr,uid,ids,march_cutoff,prev_date,tax_list[6])
                 # Billing during Month => grand_total amount of Invoices which are created in date 
		        bill_month1 = self.billing_month (cr,uid,ids,from_date,to_date,tax_list[0])
		        bill_month2 = self.billing_month (cr,uid,ids,from_date,to_date,tax_list[1])
		        bill_month3 = self.billing_month (cr,uid,ids,from_date,to_date,tax_list[2])
		        bill_month4 = self.billing_month (cr,uid,ids,from_date,to_date,tax_list[3])
		        bill_month5 = self.billing_month (cr,uid,ids,from_date,to_date,tax_list[4])
		        bill_month6 = self.billing_month (cr,uid,ids,from_date,to_date,tax_list[5])
		        bill_month7 = self.billing_month (cr,uid,ids,from_date,to_date,tax_list[6])
		        bill_month8 = self.billing_month (cr,uid,ids,from_date,to_date,tax_list[7])
		        bill_month_non = self.billing_month_nt (cr,uid,ids,from_date,to_date,tax_list[8])
		        bill_month_new_company = self.billing_month_new_company (cr,uid,ids,from_date,to_date,tax_list[6])
		        my_flg_rdm=False
		        #print 'Paramiter Cathced Values:'
		        #print 'a:',context.get('opening_outstanding1')
		        #print 'b:',context.get('opening_outstanding2')
		        #print 'c:',context.get('opening_outstanding3')
		        #print 'd:',context.get('opening_outstanding4')
		        #print 'e:',context.get('opening_outstanding5')
		        #print 'f:',context.get('opening_outstanding6')
		        #print 'g:',context.get('opening_outstanding7')
		        print "dasdkjasgfdhfgduwqjsdyd",context.get('opening_outstanding6')
		        if context.get('opening_outstanding1') and int(context.get('opening_outstanding1'))!=0:
		        	total_amount_1=context.get('opening_outstanding1')
		        	print ' we are in the 1:',total_amount_1
	        	if context.get('opening_outstanding2') and int(context.get('opening_outstanding2'))!=0:
	        		total_amount_2=context.get('opening_outstanding2')
	        		print ' we are in the 2:',total_amount_2
		        if context.get('opening_outstanding3') and int(context.get('opening_outstanding3'))!=0:
		        	total_amount_3=context.get('opening_outstanding3')
		        	print ' we are in the 3:',total_amount_3
	        	if context.get('opening_outstanding4') and int(context.get('opening_outstanding4'))!=0:
	        		total_amount_4=context.get('opening_outstanding4')
	        		print ' we are in the 4:',total_amount_4
		        if context.get('opening_outstanding5') and int(context.get('opening_outstanding5'))!=0:
		        	total_amount_5=context.get('opening_outstanding5')
		        	print ' we are in the 5:',total_amount_5
	        	if context.get('opening_outstanding6') and int(context.get('opening_outstanding6'))!=0:
	        		total_amount_6=context.get('opening_outstanding6')
	        		print ' we are in the 6:',total_amount_6
		        if context.get('opening_outstanding7') and int(context.get('opening_outstanding7'))!=0:
		        	total_amount_7=context.get('opening_outstanding7')
		        	print ' we are in the 7:',total_amount_7
		        if context.get('opening_outstanding8') and int(context.get('opening_outstanding8'))!=0:
		        	total_amount_8=context.get('opening_outstanding8')
		        	print ' we are in the 8:',total_amount_8
	        	if context.get('opening_outstanding10') and int(context.get('opening_outstanding10'))!=0:
	        		total_amount_10=context.get('opening_outstanding10')
	        		print ' we are in the 10:',total_amount_10
		        if context.get('opening_outstanding11') and int(context.get('opening_outstanding11'))!=0:
		         	pcil_opening=context.get('opening_outstanding11')
		         	print ' we are in the 11:',pcil_opening
	        	else:
	        		pcil_opening=context.get('opening_outstanding11')
	        	print 'Old Values opening_outstanding1:',total_amount_1,' opening_outstanding2:',total_amount_2,'opening_outstanding3:',total_amount_3,' opening_outstanding4:',total_amount_4,'opening_outstanding5:',total_amount_5,' opening_outstanding6:',total_amount_6,' opening_outstanding7:',total_amount_7,' opening_outstanding8:',total_amount_8,' pcil_opening:',pcil_opening
		        self.write(cr,uid,res.id,{'month_bill1':bill_month1,   'opening_outstanding1':total_amount_1,
			                          'month_bill2':bill_month2,   'opening_outstanding2':total_amount_2,
			                          'month_bill3':bill_month3,   'opening_outstanding3':total_amount_3,
			                          'month_bill4':bill_month4,   'opening_outstanding4':total_amount_4,
			                          'month_bill5':bill_month5,   'opening_outstanding5':total_amount_5,
			                          'month_bill6':bill_month6,   'opening_outstanding6':total_amount_6,
			                          'month_bill7':bill_month7,   'opening_outstanding7':total_amount_7,
			                          'month_bill8':bill_month8,	'opening_outstanding8':total_amount_8,
			                          'month_bill10':bill_month_non, 'opening_outstanding10':total_amount_10,
			                          'month_bill_new_company':bill_month_new_company,'opening_outstanding11':pcil_opening})   

#Less : Collections for the Period
                # Collection for period => Sales Receipts -> Total amount of all transactions
                # For the entries with 'others' as tax rate are excluded 23rd Sept

                CFOB_amount_1 = CFOB_invoice_amt_1 = total_invoice_amt_1 = total_advance_1 = total_db_amount_1 =0.0
	        CFOB_amount_2 = CFOB_invoice_amt_2 = total_invoice_amt_2 = total_advance_2 = total_db_amount_2 =0.0
	        CFOB_amount_3 = CFOB_invoice_amt_3 = total_invoice_amt_3 = total_advance_3 = total_db_amount_3 =0.0
                CFOB_amount_4 = CFOB_invoice_amt_4 = total_invoice_amt_4 = total_advance_4 = total_db_amount_4 =0.0
	        CFOB_amount_5 = CFOB_invoice_amt_5 = total_invoice_amt_5 = total_advance_5 = total_db_amount_5 =0.0
	        CFOB_amount_6 = CFOB_invoice_amt_6 = total_invoice_amt_6 = total_advance_6 = total_db_amount_6 =0.0
	        CFOB_amount_7 = CFOB_invoice_amt_7 = total_invoice_amt_7 = total_advance_7 = total_db_amount_7 =0.0
	        CFOB_amount_8 = CFOB_invoice_amt_8 = total_invoice_amt_8 = total_advance_8 = total_db_amount_8 =0.0
	        CFOB_amount_non = CFOB_invoice_amt_non = total_invoice_amt_non = total_advance_non = total_db_amount_non =0.0

		search_receipts1 = self.pool.get('account.sales.receipts').search(cr,uid,[
										('receipt_date','>=',from_date),
										('receipt_date','<=',to_date),
										('receipt_no','!=',''),
										('state','!=','draft')])
		if search_receipts1:						                
			for receipts in self.pool.get('account.sales.receipts').browse(cr,uid,search_receipts1):
			        for line in receipts.sales_receipts_one2many: 
			                if line.acc_status == 'others' and line.account_id.account_selection == 'against_ref':
			                # OTHRE branch invoices >>>>>>>>>
			                        for invoice in line.sales_other_cfob_one2many:
                                			if invoice.tax_rate != 'others':
                                			        if invoice.tax_rate == tax_list[0] : #'taxable_10_20': 
								        CFOB_amount_1 += invoice.ref_amount
							        elif invoice.tax_rate == tax_list[1]: 
								        CFOB_amount_2 += invoice.ref_amount
							        elif invoice.tax_rate == tax_list[2]: 
								        CFOB_amount_3 += invoice.ref_amount
							        elif invoice.tax_rate == tax_list[3]:
								        CFOB_amount_4 += invoice.ref_amount
							        elif invoice.tax_rate == tax_list[4]:       
								        CFOB_amount_5 += invoice.ref_amount
							        elif invoice.tax_rate == tax_list[5]: 
								        CFOB_amount_6 += invoice.ref_amount
								elif invoice.tax_rate == tax_list[6]: 
								        CFOB_amount_7 += invoice.ref_amount
								elif invoice.tax_rate == tax_list[7]: 
								        CFOB_amount_8 += invoice.ref_amount
								elif invoice.tax_rate == tax_list[8]: 
								        CFOB_amount_non   += invoice.ref_amount
                                         #<<<<<<<<<<<<<<
                                         #Self branch invoice >>>>>>>>>>
						for invoice in line.invoice_cfob_one2many:
							paid_amount=0.0
							if invoice.cfob_chk_invoice == True:
							        search_amt = self.pool.get('invoice.receipt.history').search(cr,uid,[
							          ('invoice_receipt_history_id','=',invoice.id),
							          ('receipt_id_history','=',line.id)])
							        if search_amt:
							        	for paid_amt in self.pool.get('invoice.receipt.history').browse(cr,uid,search_amt):
							        		paid_amount +=paid_amt.invoice_paid_amount

						        if invoice.cfob_chk_invoice == True:
								if 'NT' in invoice.invoice_number:
									CFOB_invoice_amt_non   += paid_amount
								elif invoice.tax_rate == tax_list[0]:
									CFOB_invoice_amt_1 += paid_amount
								elif invoice.tax_rate == tax_list[1]:
									CFOB_invoice_amt_2 += paid_amount
								elif invoice.tax_rate == tax_list[2]: 
									CFOB_invoice_amt_3 += paid_amount
								elif invoice.tax_rate == tax_list[3]:
									CFOB_invoice_amt_4 += paid_amount
								elif invoice.tax_rate == tax_list[4]:                # for 14.0 % HHH
									CFOB_invoice_amt_5 += paid_amount
								elif invoice.tax_rate == tax_list[5]: 
									CFOB_invoice_amt_6 += paid_amount
								elif invoice.tax_rate == tax_list[6]: 
									CFOB_invoice_amt_7 += paid_amount		
								elif invoice.tax_rate == tax_list[7]: 
									CFOB_invoice_amt_8 += paid_amount		
					#<<<<<<<<<<<<<<
			# normal sales_receipt entry >>>>>>>>>>						
					if line.account_id.account_selection == 'against_ref' and line.acc_status == 'against_ref':
						for invoice in line.invoice_adhoc_history_one2many:
							tax_rate = invoice.tax_rate
							if 'NT' in invoice.invoice_number:
								total_invoice_amt_non   += invoice.invoice_paid_amount
							elif tax_rate == tax_list[0]:
								total_invoice_amt_1 += invoice.invoice_paid_amount
							elif tax_rate == tax_list[1]:
								total_invoice_amt_2 += invoice.invoice_paid_amount
							elif tax_rate == tax_list[2]:
								total_invoice_amt_3 += invoice.invoice_paid_amount
							elif tax_rate == tax_list[3]:
								total_invoice_amt_4 += invoice.invoice_paid_amount
							elif tax_rate == tax_list[4]:
								total_invoice_amt_5 += invoice.invoice_paid_amount
							elif tax_rate == tax_list[5]:
								total_invoice_amt_6 += invoice.invoice_paid_amount
							elif tax_rate == tax_list[6]:
								total_invoice_amt_7 += invoice.invoice_paid_amount
							elif tax_rate == tax_list[7]:
								total_invoice_amt_8 += invoice.invoice_paid_amount
								print total_invoice_amt_8,'invoice paid_amount'
								print line.receipt_id.receipt_no,'receipts>>>>>>>>>>>>>>>>>>>>>>>'
						for rec_line in line.debit_note_one2many:
							if rec_line.check_debit==True:
								account_name = line.account_id.name
								if tax_list[0] in account_name :
									total_db_amount_1 += rec_line.paid_amount
								elif tax_list[1] in account_name :
									total_db_amount_2 += rec_line.paid_amount
								elif tax_list[2] in account_name :
									total_db_amount_3 += rec_line.paid_amount
								elif tax_list[3] in account_name :
									total_db_amount_4 += rec_line.paid_amount
								elif tax_list[4] in account_name :
									total_db_amount_5 += rec_line.paid_amount
								elif tax_list[5] in account_name :
									total_db_amount_6 += rec_line.paid_amount
								elif tax_list[6] in account_name :
									total_db_amount_7 += rec_line.paid_amount
								elif tax_list[7] in account_name :
									total_db_amount_8 += rec_line.paid_amount
								elif 'Non Taxable' in account_name :
									total_db_amount_non += rec_line.paid_amount
                        # <<<<<<<<<<<<<<<
        #### Advance Entries  >>>>>>>>>>
					if line.account_id.account_selection == 'advance' and line.acc_status == 'advance':
					        account_name = line.account_id.name
					        for rec_line in line.advance_one2many:
						        if tax_list[0] in account_name: 
							        total_advance_1 += rec_line.ref_amount
						        elif tax_list[1] in account_name: 
							        total_advance_2 += rec_line.ref_amount
						        elif tax_list[2] in account_name: 
							        total_advance_3 += rec_line.ref_amount
						        elif tax_list[3] in account_name:
							        total_advance_4 += rec_line.ref_amount
						        elif tax_list[4] in account_name: 
							        total_advance_5 += rec_line.ref_amount
						        elif tax_list[5] in account_name: 
							        total_advance_6 += rec_line.ref_amount
							elif tax_list[6] in account_name: 
							        total_advance_7 += rec_line.ref_amount
							elif tax_list[7] in account_name: 
							        total_advance_8 += rec_line.ref_amount
							elif 'Non' in account_name: 
							        total_advance_non   += rec_line.ref_amount
	###<<<<<<<<<<
	### Addition of fields for collection of periods	
                total_collection_1 = CFOB_amount_1 + CFOB_invoice_amt_1 + total_invoice_amt_1 + total_advance_1 + total_db_amount_1 
	        total_collection_2 = CFOB_amount_2 + CFOB_invoice_amt_2 + total_invoice_amt_2 + total_advance_2 + total_db_amount_2
	        total_collection_3 = CFOB_amount_3 + CFOB_invoice_amt_3 + total_invoice_amt_3 + total_advance_3 + total_db_amount_3
                total_collection_4 = CFOB_amount_4 + CFOB_invoice_amt_4 + total_invoice_amt_4 + total_advance_4 + total_db_amount_4
	        total_collection_5 = CFOB_amount_5 + CFOB_invoice_amt_5 + total_invoice_amt_5 + total_advance_5	+ total_db_amount_5
	        total_collection_6 = CFOB_amount_6 + CFOB_invoice_amt_6 + total_invoice_amt_6 + total_advance_6 + total_db_amount_6
	        total_collection_7 = CFOB_amount_7 + CFOB_invoice_amt_7 + total_invoice_amt_7 + total_advance_7 + total_db_amount_7
	        total_collection_8 = CFOB_amount_8 + CFOB_invoice_amt_8 + total_invoice_amt_8 + total_advance_8 + total_db_amount_8
	        total_collection_10 = CFOB_amount_non + CFOB_invoice_amt_non + total_invoice_amt_non + total_advance_non + total_db_amount_non
	### Addition of fields for collection of periods

###Less : Advance Receipt Billed during the Period
        # Advance Receipt Billed => Sales Receipts -> status = Advance and paid date between from and to date
                advance_receipt_amt_1 = advance_receipt_amt_2 = advance_receipt_amt_3 = advance_receipt_amt_4 =0.0
                advance_receipt_amt_6 = advance_receipt_amt_7 = advance_receipt_amt_8 = advance_receipt_amt_5 = advance_receipt_amt_10 =0.0
		search_receipts = self.pool.get('account.sales.receipts').search(cr,uid,[('receipt_date','<=',to_date),
											('receipt_no','!=',''),
											('state','!=','draft')])
		if search_receipts:
			for receipts_advance_line in self.pool.get('account.sales.receipts').browse(cr,uid,search_receipts):
				for n_line in receipts_advance_line.sales_receipts_one2many:
					if n_line.account_id.account_selection == 'advance':
					    for n_line_advance in n_line.advance_invoice_one2many:
							if n_line_advance.paid_date >= str(from_date) and n_line_advance.paid_date<=str(to_date):
							        if n_line.payment_status =='partial_payment' :
							                amount = n_line_advance.partial_payment_amount      
							        else : 
							                amount = n_line_advance.invoice_amount
							        if tax_list[0]  in n_line_advance.tax_rate :        
                                                                       advance_receipt_amt_1 += amount
                                              			elif tax_list[1] in n_line_advance.tax_rate :        
                                                                       advance_receipt_amt_2 += amount
                                              			elif tax_list[2] in  n_line_advance.tax_rate:
                                                                        advance_receipt_amt_3 += amount        
                                                		elif tax_list[3] in n_line_advance.tax_rate :
                                                                        advance_receipt_amt_4 += amount
                                                                elif tax_list[4] in  n_line_advance.tax_rate:
									advance_receipt_amt_5 += amount	
								elif tax_list[5] in n_line_advance.tax_rate :
                                                                       advance_receipt_amt_6 += amount
                                                                elif tax_list[6] in n_line_advance.tax_rate :
                                                                       advance_receipt_amt_7 += amount
                                                                elif tax_list[7] in n_line_advance.tax_rate :
                                                                       advance_receipt_amt_8 += amount
                                                                elif 'non_taxable' in n_line_advance.tax_rate :
                                                                       advance_receipt_amt_10 += amount
                                                                       
##Less : Collection at Head Office #######start
                total_jv_head_amount1 =total_jv_head_amount2 =total_jv_head_amount3 =total_jv_head_amount4 =total_jv_head_amount5 =0.0 
                total_jv_head_amount6 =total_jv_head_amount7=total_jv_head_amount8=  total_jv_head_amount10 = 0.0
		branch_jv3 = self.pool.get('account.journal.voucher').search(cr,uid,[('id','>',0),('jv_number','!=',''),
											('date','>=',from_date),('date','<=',to_date),
											('state','!=','draft')])
		if branch_jv3:
			for i in self.pool.get('account.journal.voucher').browse(cr,uid,branch_jv3):
				for j in i.journal_voucher_one2many:
					if j.account_id.account_selection == 'ho_remmitance':
						for n_jv_id in j.journal_voucher_id.journal_voucher_one2many :
							for amt in n_jv_id.journal_voucher_history_one2many:
								if 'NT' in amt.invoice_number :
									total_jv_head_amount10 +=amt.invoice_paid_amount
                                                                elif amt.tax_rate== tax_list[0]: 
                                                                        total_jv_head_amount1 += amt.invoice_paid_amount 
                                                                elif amt.tax_rate== tax_list[1]:
                                                                        total_jv_head_amount2 += amt.invoice_paid_amount 
                                                                elif amt.tax_rate== tax_list[2]:
                                                                        total_jv_head_amount3 += amt.invoice_paid_amount 
                                                                elif amt.tax_rate== tax_list[3] :
                                                                        total_jv_head_amount4 += amt.invoice_paid_amount 
                                                                elif amt.tax_rate== tax_list[4] :
                                                                        total_jv_head_amount5 += amt.invoice_paid_amount 
                                                                elif amt.tax_rate== tax_list[5]:
                                                                        total_jv_head_amount6 += amt.invoice_paid_amount 
						                elif amt.tax_rate== tax_list[6] :
						                	print amt.tax_rate,tax_list[6]
                                                                        total_jv_head_amount7 += amt.invoice_paid_amount
						                elif amt.tax_rate== tax_list[7] :
                                                                        total_jv_head_amount8 += amt.invoice_paid_amount
			for i in self.pool.get('account.journal.voucher').browse(cr,uid,branch_jv3):
				for j in i.journal_voucher_one2many:
					if j.account_id.account_selection == 'ho_remmitance':       
						for n_jv_id in j.journal_voucher_id.journal_voucher_one2many :
							if n_jv_id.cbob_advance_one2many:
								for amt in n_jv_id.cbob_advance_one2many:
									acc_name=n_jv_id.account_id.name
									if 'Non Taxable' in acc_name:
										total_jv_head_amount10 +=amt.ref_amount
									elif tax_list[0] in acc_name: 
										total_jv_head_amount1 += amt.ref_amount
									elif tax_list[1] in acc_name:
										total_jv_head_amount2 += amt.ref_amount 
									elif tax_list[2] in acc_name:
										total_jv_head_amount3 += amt.ref_amount 
									elif tax_list[3] in acc_name:
										total_jv_head_amount4 += amt.ref_amount 
									elif tax_list[4] in acc_name:
										total_jv_head_amount5 += amt.ref_amount 
									elif tax_list[5] in acc_name:
										total_jv_head_amount6 += amt.ref_amount 
									elif tax_list[6] in acc_name:
										total_jv_head_amount7 += amt.ref_amount
									elif tax_list[7] in acc_name:
										total_jv_head_amount8 += amt.ref_amount
##Add : Other Branch Collection
        # Other branch collection => Sales Receipts -> status = Others and customer name =CFOB
		total_dr_amt_1=total_dr_amt_2 =total_dr_amt_3 =total_dr_amt_4 = total_dr_amt_6 = total_dr_amt_7=total_dr_amt_8=total_dr_amt_5= total_dr_amt_10 =0.0
		branch_jv = self.pool.get('account.sales.receipts').search(cr,uid,[('id','>',0),('receipt_date','>=',from_date),
		                                                ('receipt_date','<=',to_date),('receipt_no','!=',''),
		                                                ('state','!=','draft'),('customer_name','=','CFOB')])
	        if branch_jv:
			for i in self.pool.get('account.sales.receipts').browse(cr,uid,branch_jv):
			        for j in i.sales_receipts_one2many:
					if j.acc_status == 'others' and j.account_id.account_selection == 'against_ref':
						for line_in in j.sales_other_cfob_one2many:
							if line_in.tax_rate != 'others':
								if line_in.tax_rate == tax_list[1]: #'taxable_10_30': 
									total_dr_amt_2 += line_in.ref_amount
								if line_in.tax_rate == tax_list[2]: #'taxable_12_24': 
									total_dr_amt_3 += line_in.ref_amount
								if line_in.tax_rate == tax_list[3]: #'taxable_12_36':
									total_dr_amt_4 += line_in.ref_amount
								if line_in.tax_rate == tax_list[4]: #'taxable_14_00':                   
									total_dr_amt_5 += line_in.ref_amount
								if line_in.tax_rate == tax_list[5]: #'taxable_14_5':                    
									total_dr_amt_6+= line_in.ref_amount
								if line_in.tax_rate == tax_list[6]: #'taxable_15_0':                    
									total_dr_amt_7+= line_in.ref_amount
								if line_in.tax_rate == tax_list[7]: #'taxable_18_0':                    
									total_dr_amt_7+= line_in.ref_amount
								if line_in.tax_rate == tax_list[8]: #'non_taxable': 
									total_dr_amt_10 += line_in.ref_amount
									
###Less : Collection at Other Branches
        # Collection at other branches => JV enetries of CBOB
		total_jv_amount1 = total_jv_amount2 =total_jv_amount3 =total_jv_amount4 =total_jv_amount5 =total_jv_amount6=total_jv_amount7=total_jv_amount8= total_jv_amount10=total_jv_amount11=sum_credit_amt_sync=main_amount=.0

		branch_jv2 = self.pool.get('account.journal.voucher').search(cr,uid,[('id','>',0),('jv_number','!=',''),
										('date','>=',from_date),('date','<=',to_date),
										('state','=','done'),('customer_name','=','CBOB'),])
		if branch_jv2:
			for journal in self.pool.get('account.journal.voucher').browse(cr,uid,branch_jv2):
			        cbob_flag=cbob_other_flag=False
			        for line in journal.journal_voucher_one2many:
			                if line.account_id.account_selection == 'others':
        			                cbob_other_flag=True
			        if cbob_other_flag == True :
			                for line in journal.journal_voucher_one2many:
			                        if line.account_id.account_selection == 'against_ref':
			                                if 'Non Taxable' in j.account_id.name:
					                        cbob_flag=True
					                for invoice in line.journal_voucher_history_one2many:
					                        if cbob_flag==True:                                     #sagar 5oct15
								        total_jv_amount10 += invoice.invoice_paid_amount
						                elif invoice.tax_rate == tax_list[0]:
							                total_jv_amount1 += invoice.invoice_paid_amount
						                elif invoice.tax_rate == tax_list[1]:
							                total_jv_amount2 += invoice.invoice_paid_amount
						                elif invoice.tax_rate == tax_list[2]:
							                total_jv_amount3 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[3]:
							                total_jv_amount4 += invoice.invoice_paid_amount
						                elif invoice.tax_rate == tax_list[4]:
							                total_jv_amount5 += invoice.invoice_paid_amount
						                elif invoice.tax_rate == tax_list[5]:
							                total_jv_amount6 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[6]:
							                #total_jv_amount7 += invoice.invoice_paid_amount
							                total_jv_amount7 += 0 #invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[6]:
							                #total_jv_amount7 += invoice.invoice_paid_amount
							                total_jv_amount8 += invoice.invoice_paid_amount
							                #total_jv_amount8 += 0 #invoice.invoice_paid_amount
							for invoice in line.invoice_cbob_one2many_reverse1:
								if invoice.cbob_chk_invoice_reverse==True:
									
							                if cbob_flag==True:                                     #sagar 5oct15
										total_jv_amount10 -= invoice.jv_amount
								        elif invoice.tax_rate == tax_list[0]:
									        total_jv_amount1 -= invoice.jv_amount
								        elif invoice.tax_rate == tax_list[1]:
									        total_jv_amount2 -= invoice.jv_amount
								        elif invoice.tax_rate == tax_list[2]:
									        total_jv_amount3 -= invoice.jv_amount
		                                                        elif invoice.tax_rate == tax_list[3]:
									        total_jv_amount4 -= invoice.jv_amount
								        elif invoice.tax_rate == tax_list[4]:
									        total_jv_amount5 -= invoice.jv_amount
								        elif invoice.tax_rate == tax_list[5]:
									        total_jv_amount6 -= invoice.jv_amount
		                                                        elif invoice.tax_rate == tax_list[6]:
									        total_jv_amount7 -= invoice.jv_amount
		                                                        elif invoice.tax_rate == tax_list[6]:
									        total_jv_amount8 -= invoice.jv_amount
							                
		search_jv_advance = self.pool.get('account.journal.voucher').search(cr,uid,[('date','>=',from_date), ('date','<=',to_date),
										             ('jv_number','!=',''),('state','!=','draft'),('customer_name','!=','CBOB')]) ##change by ujwala
										
		for receipts in self.pool.get('account.journal.voucher').browse(cr,uid,search_jv_advance):	                
		        for rec_line in receipts.journal_voucher_one2many:
		                if rec_line.account_id.account_selection == 'advance' and rec_line.type=='credit':
        		                if tax_list[0] in rec_line.account_id.name :
				                total_jv_amount1 += rec_line.credit_amount
			                elif tax_list[1] in rec_line.account_id.name :
				                total_jv_amount2 += rec_line.credit_amount
			                elif tax_list[2] in rec_line.account_id.name :
				                total_jv_amount3 += rec_line.credit_amount
			                elif tax_list[3] in rec_line.account_id.name :
				                total_jv_amount4 += rec_line.credit_amount
			                elif tax_list[4] in rec_line.account_id.name :
				                total_jv_amount5 += rec_line.credit_amount
			                elif tax_list[5] in rec_line.account_id.name :
				                total_jv_amount6 += rec_line.credit_amount
				        elif tax_list[6] in rec_line.account_id.name :
				                total_jv_amount7 += rec_line.credit_amount
				        elif tax_list[7] in rec_line.account_id.name :
				                total_jv_amount8 += rec_line.credit_amount
				        elif 'Non taxable' in rec_line.account_id.name :
				                total_jv_amount10 += rec_line.credit_amount
				
				branch_jv3 = self.pool.get('account.journal.voucher').search(cr,uid,[('id','>',0),('jv_number','!=',''),
                                                                                ('date','>=',from_date),('date','<=',to_date),
                                                                                ('state','!=','draft'),
									        ('customer_name','not in',('CFOB'))])
                if branch_jv2:
                        for journal in self.pool.get('account.journal.voucher').browse(cr,uid,branch_jv3):
                        	for rec_line in journal.journal_voucher_one2many:
				        if rec_line.account_id.account_selection == 'advance' and rec_line.type=='credit':
				                if tax_list[0] in rec_line.account_id.name :
						        total_jv_amount1 += rec_line.credit_amount
					        elif tax_list[1] in rec_line.account_id.name :
						        total_jv_amount2 += rec_line.credit_amount
					        elif tax_list[2] in rec_line.account_id.name :
						        total_jv_amount3 += rec_line.credit_amount
					        elif tax_list[3] in rec_line.account_id.name :
						        total_jv_amount4 += rec_line.credit_amount
					        elif tax_list[4] in rec_line.account_id.name :
						        total_jv_amount5 += rec_line.credit_amount
					        elif tax_list[5] in rec_line.account_id.name :
						        total_jv_amount6 += rec_line.credit_amount
						elif tax_list[6] in rec_line.account_id.name :
						        total_jv_amount7 += rec_line.credit_amount
						elif tax_list[7] in rec_line.account_id.name :
						        total_jv_amount8 += rec_line.credit_amount
						elif 'Non taxable' in rec_line.account_id.name :
						        total_jv_amount10 += rec_line.credit_amount
                                cbob_flag_1=cbob_other_flag_1=cbob_other_flag_2=False
                                for line in journal.journal_voucher_one2many:
					if line.account_id.account_selection == 'others':
	                                        cbob_other_flag_1=True
					if line.account_id.account_selection == 'ho_remmitance':
						cbob_other_flag_2=True
                                if cbob_other_flag_1 == True and cbob_other_flag_2==True:
                                        for line in journal.journal_voucher_one2many:
                                                if line.account_id.account_selection == 'against_ref':
                                                        if 'Non Taxable' in j.account_id.name:
                                                                cbob_flag_1=True
                                                        for invoice in line.journal_voucher_invoice_history_one2many:
                                                                if cbob_flag_1==True:
                                                                        total_jv_amount10 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[0]:
                                                                        total_jv_amount1 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[1]:
                                                                        total_jv_amount2 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[2]:
                                                                        total_jv_amount3 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[3]: 
                                                                        total_jv_amount4 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[4]:
                                                                        total_jv_amount5 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[5]: 
                                                                        total_jv_amount6 += invoice.invoice_paid_amount
                                                                elif invoice.tax_rate == tax_list[6]:
							                total_jv_amount7 += 0 #invoice.invoice_paid_amount			
                                                                elif invoice.tax_rate == tax_list[6]:
							                total_jv_amount8 += invoice.invoice_paid_amount			
							                #total_jv_amount8 += 0 #invoice.invoice_paid_amount			
							                #total_jv_amount7 += invoice.invoice_paid_amount
		#cr.execute("select sum(credit_amount) from account_journal_voucher_line where journal_voucher_id in (select id from account_journal_voucher where date between '2017-03-01' and '2017-03-31' and narration ilike 'Being Collection made by PCI vide Receipt No.%')")
		total_jv_amount6 = 0
		CBOB_value = self.pool.get('res.partner').search(cr,uid,[('name','=','CBOB')])
		str_qry="select sum(credit_amount) from account_journal_voucher_line where account_id in (select id from account_account where name ilike 'Sundry Debtors Service - (Taxable) 15.0%') and journal_voucher_id in (select id from account_journal_voucher where customer_name = "+str(CBOB_value[0])+" and date between '"+str(from_date)+"' and '"+str(to_date)+"') and type='credit'"# and narration ilike '%vide Receipt No.%')"
		cr.execute(str_qry)
		sum_credit_amt_sync = cr.fetchone()
		str_qry2="select sum(asr.ref_amount) from account_journal_voucher_line ajvl left join advance_sales_receipts asr on asr.cbob_advance_id=ajvl.id where asr.ref_date between '"+str(from_date)+"' and '"+str(to_date)+"' and type='credit'"
		print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ okey :',str_qry2
		cr.execute(str_qry2)
		sum_credit_amt_sync2 = cr.fetchone()
		print 'we have value: sum_credit_amt_sync1:',sum_credit_amt_sync2
		#sum_credit_amt_sync=sum_credit_amt_sync+total_jv_amount7
		print '######################################################## sum_credit_amt:',sum_credit_amt_sync[0],' total_jv_amount7:',total_jv_amount7
		str_qry1="select sum(credit_amount) from account_journal_voucher_line where account_id in (select id from account_account where name ilike 'Sundry Debtors Service - (Taxable) 14.50%') and  journal_voucher_id in (select id from account_journal_voucher where date between '"+str(from_date)+"' and '"+str(to_date)+"' and narration ilike '%vide Receipt No.%') and type='credit'"
		cr.execute(str_qry1)
		sum_credit_amt_sync1 = cr.fetchone()
		print '*********************************** sum_credit_amt_sync1:',sum_credit_amt_sync1[0],' total_jv_amount6:',total_jv_amount6
		# if sum_credit_amt_sync1[0]:
		# 	total_jv_amount6 += sum_credit_amt_sync1[0]
		# 	total_jv_amount7 += sum_credit_amt_sync[0]-sum_credit_amt_sync1[0]
		# else:
		# 	if sum_credit_amt_sync[0]:
		# 		total_jv_amount7 += sum_credit_amt_sync[0]
		print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Current Value of total_jv_amount7:',total_jv_amount7
		branch_jv_pci = self.pool.get('account.journal.voucher').search(cr,uid,[('id','>',0),('jv_number','!=',''),
										('date','>=',from_date),('date','<=',to_date),
										('state','!=','draft'),('customer_name','=','CBOB'),('narration','ilike','Being Sub-Contracting Invoices raised on Pest Control (India) Pvt Ltd. during the')])
		if branch_jv_pci:
			for journal in self.pool.get('account.journal.voucher').browse(cr,uid,branch_jv_pci):
				for line in journal.journal_voucher_one2many:
					if line.account_id.account_selection == 'against_ref':
						if line.journal_voucher_history_one2many:
							for invoice in line.journal_voucher_history_one2many:
								if invoice.check_invoice==True:                                     #sagar 5oct15
									total_jv_amount11 += invoice.invoice_paid_amount
		if sum_credit_amt_sync1[0]:
			total_jv_amount6 += sum_credit_amt_sync1[0]
			total_jv_amount7 += sum_credit_amt_sync[0] -total_jv_head_amount7
		else:
			if sum_credit_amt_sync[0]:
				main_amount += sum_credit_amt_sync[0]
				total_jv_amount7 = main_amount - total_jv_amount11-total_jv_head_amount7
				if sum_credit_amt_sync2[0]:
					total_jv_amount7 =  total_jv_amount7 + sum_credit_amt_sync2[0] -total_jv_head_amount7
##Less : Credit Notes ---/  (added st as new reqiremt from vijay)
		#credit Note >>>>>>>>>
		total_credit_note_1 = credit_note_1 = credit_note_1_st = credit_note_1_it = 0.0
		total_credit_note_2 = credit_note_2 = credit_note_2_st = credit_note_2_it = 0.0
		total_credit_note_3 = credit_note_3 = credit_note_3_st = credit_note_3_it = 0.0
		total_credit_note_4 = credit_note_4 = credit_note_4_it = credit_note_4_st = 0.0
		total_credit_note_5 = credit_note_5 = credit_note_5_st = credit_note_5_it = 0.0
		total_credit_note_6 = credit_note_6 = credit_note_6_st = credit_note_6_it = 0.0
		total_credit_note_7 = credit_note_7 = credit_note_7_st = credit_note_7_it = 0.0
		total_credit_note_8 = credit_note_8 = credit_note_8_st = credit_note_8_it = 0.0
		total_credit_note_10 = credit_note_10 = credit_note_10_st = credit_note_10_it = 0.0
		 #<<<<<<<<<<<

		credit_writeoff = self.pool.get('credit.note').search(cr,uid,[('id','>',0),
		                                                              ('credit_note_date','>=',from_date),
		                                                              ('credit_note_date','<=',to_date),
		                                                              ('credit_note_no','!=',''),('state','!=','draft')])
		                                                              
		if credit_writeoff:
			for credit in self.pool.get('credit.note').browse(cr,uid,credit_writeoff):
				status=['against_ref_writeoff','against_short_payment','against_ref_refund','against_advance']
				flag=False		
				for n_line in credit.credit_note_one2many:
					if n_line.account_id.account_selection =='against_ref' and n_line.status_selection in status:
					        flag=True
						for n_hist in n_line.credit_note_history_one2many:
        						amount=n_hist.invoice_writeoff_amount if n_hist.invoice_writeoff_amount else n_hist.advance_writeoff_amount if n_hist.advance_writeoff_amount else n_hist.advance_writeoff_amount if n_hist.advance_writeoff_amount else n_hist.invoice_paid_amount if n_hist.invoice_paid_amount else 0.0

							if n_hist.tax_rate== tax_list[0]:                          
								credit_note_1 += amount 
 							if n_hist.tax_rate== tax_list[1]:                           
								credit_note_2 += amount
							if n_hist.tax_rate== tax_list[2]:                          
								credit_note_3 += amount
							if n_hist.tax_rate== tax_list[3]:                          
								credit_note_4 += amount
							if n_hist.tax_rate== tax_list[4]:                           
								credit_note_5  += amount
							if n_hist.tax_rate== tax_list[5]:                            
								credit_note_6  += amount
							if n_hist.tax_rate== tax_list[6]:                           
								credit_note_7  += amount	
							if n_hist.tax_rate== tax_list[7]:                           
								credit_note_8  += amount	
							if n_hist.tax_rate=='non_taxable':                           
								credit_note_10  += amount	
								
			########## ITDS >>>>>>>>>>>>>>>>>>>>>> add code for ITDS & Advance in  Priyanka				
					if n_line.status_selection =='against_itds' and n_line.type=='credit':
					        flag=True
						if  n_line.account_id.account_selection != 'itds_receipt':
							for itds_line in n_line.credit_note_itds_history_one2many:	
								if itds_line.tax_rate == tax_list[0]:
									credit_note_1_it += itds_line.invoice_paid_amount
								if itds_line.tax_rate == tax_list[1]:
									credit_note_2_it +=  itds_line.invoice_paid_amount
								if itds_line.tax_rate == tax_list[2]:
									credit_note_3_it += itds_line.invoice_paid_amount
								if itds_line.tax_rate == tax_list[3]:
									credit_note_4_it +=  itds_line.invoice_paid_amount
								if itds_line.tax_rate == tax_list[4]:
									credit_note_5_it +=  itds_line.invoice_paid_amount
								if itds_line.tax_rate == tax_list[5]:
			                                                credit_note_6_it +=  itds_line.invoice_paid_amount
			                                        if itds_line.tax_rate == tax_list[6]:
			                                                credit_note_7_it +=  itds_line.invoice_paid_amount
			                                        if itds_line.tax_rate == tax_list[7]:
			                                                credit_note_8_it +=  itds_line.invoice_paid_amount
			                                        if itds_line.tax_rate == 'non_taxable':
			                                                credit_note_10_it +=  itds_line.invoice_paid_amount
			                                                
		###### added for reflecting advance credit note as per Client requirement on (24 Aug 2016)	>>>>>>>
				if flag == False:
				        for n_line1 in credit.credit_note_one2many:
				        	if tax_list[0] in n_line1.account_id.name:                          
							credit_note_1 += n_line1.credit_amount
						if tax_list[1] in n_line1.account_id.name:                           
							credit_note_2 += n_line1.credit_amount
						if tax_list[2] in n_line1.account_id.name:                          
							credit_note_3 += n_line1.credit_amount
						if tax_list[3] in n_line1.account_id.name:                          
							credit_note_4 += n_line1.credit_amount
						if tax_list[4] in n_line.account_id.name:                           
							credit_note_5  += n_line1.credit_amount
						if tax_list[5] in n_line1.account_id.name:                            
							credit_note_6  += n_line1.credit_amount
						if tax_list[6] in n_line1.account_id.name:                           
							credit_note_7  += n_line1.credit_amount
						if tax_list[7] in n_line1.account_id.name:                           
							credit_note_8  += n_line1.credit_amount
								
## credit note st (added st as new reqiremt from vijay)
		credit_writeoff_st = self.pool.get('credit.note.st').search(cr,uid,[('id','>',0),('credit_note_date','>=',from_date),('credit_note_date','<=',to_date),('credit_note_no','!=',''),('state','!=','draft')])
		
		if credit_writeoff_st:	
			for credit in self.pool.get('credit.note.st').browse(cr,uid,credit_writeoff_st):
				for n_line in credit.credit_note_st_one2many:	
					if n_line.account_id.account_selection =='against_ref':
					        for invoice in n_line.credit_st_id_history_one2many:
						        if invoice.tax_rate == tax_list[0]:                   
							        credit_note_1_st += invoice.invoice_writeoff_amount
						        if invoice.tax_rate == tax_list[1]:                   
							        credit_note_2_st += invoice.invoice_writeoff_amount
						        if invoice.tax_rate == tax_list[2]:                   
							        credit_note_3_st += invoice.invoice_writeoff_amount
						        if invoice.tax_rate == tax_list[3]:                   
							        credit_note_4_st += invoice.invoice_writeoff_amount
						        if invoice.tax_rate == tax_list[4]:                      
							        credit_note_5_st += invoice.invoice_writeoff_amount
						        if invoice.tax_rate == tax_list[5]:                    
							        credit_note_6_st += invoice.invoice_writeoff_amount
							if invoice.tax_rate == tax_list[6]:                    
							        credit_note_7_st += invoice.invoice_writeoff_amount
							if invoice.tax_rate == tax_list[7]:                    
							        credit_note_8_st += invoice.invoice_writeoff_amount
					                if invoice.tax_rate == 'non_taxable':                    
							        credit_note_10_st += invoice.invoice_writeoff_amount
							        
##credit note st (added st as new reqiremt from vijay)
		total_credit_note_1 = credit_note_1 + credit_note_1_st + credit_note_1_it
		total_credit_note_2 = credit_note_2 + credit_note_2_st + credit_note_2_it
		total_credit_note_3 = credit_note_3 + credit_note_3_st + credit_note_3_it 
		total_credit_note_4 = credit_note_4 + credit_note_4_it + credit_note_4_st
		total_credit_note_5 = credit_note_5 + credit_note_5_st + credit_note_5_it 
		total_credit_note_6 = credit_note_6 + credit_note_6_st + credit_note_6_it
		total_credit_note_7 = credit_note_7 + credit_note_7_st + credit_note_7_it
		total_credit_note_8 = credit_note_8 + credit_note_8_st + credit_note_8_it
		total_credit_note_10 = credit_note_10 + credit_note_10_st + credit_note_10_it
		
##Add : Sales Refund to Parties (against Credit Notes)			
		total_credit_refund1 =total_credit_refund2 =total_credit_refund3 =total_credit_refund4 =total_credit_refund5 =total_credit_refund6 =total_credit_refund7=total_credit_refund8= total_credit_refund10=0.0
		
		payment_refund = self.pool.get('cust.supp.credit.refund').search(cr,uid,[('id','>',0),('payment_date','>=',from_date),('payment_date','<=',to_date),('payment_no','!=',''),('state','!=','draft')])
		
		for refund in self.pool.get('cust.supp.credit.refund').browse(cr,uid,payment_refund):
		        flag=False
			for n_line in refund.credit_refund_cs_one2many:
			        if n_line.status !='against_adv' and n_line.account_id.account_selection == 'against_ref':
			                flag= True
				        account_name = n_line.account_id.name
				        if tax_list[0] in account_name :
					        total_credit_refund1 += n_line.debit_amount
                                        elif tax_list[1] in account_name :
					        total_credit_refund2 += n_line.debit_amount
                                        elif tax_list[2] in account_name :
					        total_credit_refund3 += n_line.debit_amount
				        elif tax_list[3] in account_name :
					        total_credit_refund4 += n_line.debit_amount
				        elif tax_list[4] in account_name :
					        total_credit_refund5+= n_line.debit_amount
				        elif tax_list[5] in account_name :
					        total_credit_refund6+= n_line.debit_amount
				        elif tax_list[6] in account_name :
					        total_credit_refund7+= n_line.debit_amount
				        elif tax_list[7] in account_name :
					        total_credit_refund8+= n_line.debit_amount
					elif 'Non taxable' in account_name :
					        total_credit_refund10+= n_line.debit_amount
			if flag ==False:
		                for n_line in refund.credit_refund_cs_one2many:
		                        if n_line.status !='against_adv' and n_line.account_id.account_selection == 'advance':
				                account_name = n_line.account_id.name
				                if tax_list[0] in account_name :
					                total_credit_refund1 += n_line.debit_amount
                                                elif tax_list[1] in account_name :
					                total_credit_refund2 += n_line.debit_amount
                                                elif tax_list[2] in account_name :
					                total_credit_refund3 += n_line.debit_amount
				                elif tax_list[3] in account_name :
					                total_credit_refund4 += n_line.debit_amount
				                elif tax_list[4] in account_name :
					                total_credit_refund5+= n_line.debit_amount
				                elif tax_list[5] in account_name :
					                total_credit_refund6+= n_line.debit_amount
				                elif tax_list[6] in account_name :
					                total_credit_refund7+= n_line.debit_amount
				                elif tax_list[7] in account_name :
					                total_credit_refund8+= n_line.debit_amount
					        elif 'Non taxable' in account_name :
					                total_credit_refund10+= n_line.debit_amount						
# ### end

##Add : Debit Notes ######## Start
		total_debit_amount_1=total_debit_amount_2 = total_debit_amount_3 = total_debit_amount_4 =total_debit_amount_5 = total_debit_amount_6 = total_debit_amount_7= total_debit_amount_8 = total_debit_amount_10 =0.0 
		srch_debit = self.pool.get('debit.note').search(cr,uid,[('id','>',0),('debit_note_no','!=',''),
															('debit_note_date','>=',from_date),
															('debit_note_date','<=',to_date),
															('state','!=','draft'),
															('state_new','in',('open','paid'))])
		for debit in self.pool.get('debit.note').browse(cr,uid,srch_debit):
			for n_line in debit.debit_note_one2many:
				account_name = n_line.account_id.name
				if n_line.debit_amount!=0.0:
					if tax_list[0] in str(account_name) :
						total_debit_amount_1 += n_line.debit_amount
					if tax_list[1] in str(account_name) :
						total_debit_amount_2 += n_line.debit_amount
					if tax_list[2] in str(account_name) :
						total_debit_amount_3 += n_line.debit_amount
					if tax_list[3] in str(account_name) :
						total_debit_amount_4 += n_line.debit_amount
					if tax_list[4] in str(account_name) :
						total_debit_amount_5 += n_line.debit_amount
					if tax_list[5] in str(account_name) :
						total_debit_amount_6 += n_line.debit_amount
					if tax_list[6] in str(account_name) :
						total_debit_amount_7 += n_line.debit_amount
					if tax_list[7] in str(account_name) :
						total_debit_amount_8 += n_line.debit_amount
					if 'Non Taxable' in str(account_name) :
						total_debit_amount_10 += n_line.debit_amount
############# Add : Debit Notes ######## End

#cheques  dishonoured >>>>>>>>>> start
                cheque_dish_amt_2 = cheque_dish_amt_3 = cheque_dish_amt_4 = cheque_dish_amt_6 = cheque_dish_amt_7 = 0.0
                cheque_dish_amt_8 = 0.0
                cheque_dish_amt_5 = cheque_dish_amt_1 = cheque_dish_amt_10 =0.0
		srch_cheque = self.pool.get('cheque.bounce').search(cr,uid,[('payment_no','!=',''),
								('payment_date','>=',from_date),
								('payment_date','<=',to_date),
								('state','!=','draft')])
		for cheque in self.pool.get('cheque.bounce').browse(cr,uid,srch_cheque):
			for line in cheque.cheque_bounce_lines:
			        if line.account_id.account_selection == 'against_ref':
        			        for rec in line.debited_invoice_line_new:
        			                if rec.cheque_bounce_boolean_process:
                			                if rec.tax_rate == tax_list[0]:
		                			        cheque_dish_amt_1 += rec.invoice_paid_amount
        			                        if rec.tax_rate == tax_list[1]:
		                			        cheque_dish_amt_2 += rec.invoice_paid_amount
		                			if rec.tax_rate == tax_list[2]:
		        				        cheque_dish_amt_3 += rec.invoice_paid_amount
		        				if rec.tax_rate == tax_list[3]:
			        			        cheque_dish_amt_4 += rec.invoice_paid_amount
        					        if rec.tax_rate == tax_list[4]:
        						        cheque_dish_amt_5 += rec.invoice_paid_amount
			        		        if rec.tax_rate == tax_list[5]:
			        			        cheque_dish_amt_6 += rec.invoice_paid_amount
			        			if rec.tax_rate == tax_list[6]:
			        			        cheque_dish_amt_7 += rec.invoice_paid_amount
			        			if rec.tax_rate == tax_list[7]:
			        			        cheque_dish_amt_8 += rec.invoice_paid_amount
			        			if rec.tax_rate == 'non_taxable' :
			        			        cheque_dish_amt_10 += rec.invoice_paid_amount
					tax_rate_list=['10.20','10.30','12.24','12.36','14.0','14.5','15.0','18.0','Non Taxable']
					if line.debit_note_one2many:
						for ln in line.debit_note_one2many:
							if ln.dn_cheque_bounce == True:
								acc_name=line.account_id.name
								if tax_rate_list[0] in acc_name: 
									cheque_dish_amt_1 += ln.paid_amount
								if tax_rate_list[1] in acc_name: 
									cheque_dish_amt_2 += ln.paid_amount
								if tax_rate_list[2] in acc_name:
									cheque_dish_amt_3 += ln.paid_amount
								if tax_rate_list[3] in acc_name:
									cheque_dish_amt_4 += ln.paid_amount
								if tax_rate_list[4] in acc_name:  # for 14.50 % sagar
									cheque_dish_amt_5 += ln.paid_amount
								if tax_rate_list[5] in acc_name:  # for 14.50 % sagar
									cheque_dish_amt_6 += ln.paid_amount
								if tax_rate_list[6] in acc_name:  # for 14.50 % sagar
									cheque_dish_amt_7 += ln.paid_amount
								if tax_rate_list[7] in acc_name:  # for 18.00 % rahul
									cheque_dish_amt_8 += ln.paid_amount
								if tax_rate_list[8] in acc_name:  # for 14.50 % sagar
									cheque_dish_amt_10 += ln.paid_amount

			        if line.account_id.account_selection == 'advance':
				       	for rec in line.advance_cheque_bounce_one2many:
					       	account_id_name = line.account_id.name
					       	
					       	account_split = account_id_name.split(' ')
					       	account_name = [str(x) for x in account_split]
					       	
					       	if rec.cheque_bounce_boolean == True:
						       	if str(tax_list[0]) in str(account_name[4]):
							       	if rec.cheque_bounce_boolean == True:
							   	        cheque_dish_amt_1 += rec.ref_amount
						                # cheque_dish_amt_11 += rec.ref_amount
						     	if str(tax_list[1]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_2 += rec.ref_amount
						                # cheque_dish_amt_22 += rec.ref_amount
						        if str(tax_list[2]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_3 += rec.ref_amount
						                # cheque_dish_amt_33 += rec.ref_amount
						        if str(tax_list[3]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_4 += rec.ref_amount
						                # cheque_dish_amt_44 += rec.ref_amount
						        if str(tax_list[4]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_5 += rec.ref_amount
						                # cheque_dish_amt_55 += rec.ref_amount
						        if str(tax_list[5]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_6 += rec.ref_amount
						                # cheque_dish_amt_66 += rec.ref_amount
						        if str(tax_list[6]) in  str(account_name[4]):
						            if rec.cheque_bounce_boolean == True: 
						                cheque_dish_amt_7 += rec.ref_amount
						                # cheque_dish_amt_77 += rec.ref_amount
						        if str(tax_list[7]) in  str(account_name[4]):
						            if rec.cheque_bounce_boolean == True: 
						                cheque_dish_amt_8 += rec.ref_amount
						                # cheque_dish_amt_77 += rec.ref_amount
						        if str('non_taxable') in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_10 += rec.ref_amount
						                # cheque_dish_amt_100 += rec.ref_amount

#<<<<<<<<<<<<<<<<< End

##Add : Excess Collection / Advance Receipt    #### start
        # Excess Collection Advance => Sales Receipts -> status = Advance
		total_advance_amount_1 =total_advance_amount_2 =total_advance_amount_3 =total_advance_amount_4 = total_advance_amount_5 =total_advance_amount_6 =total_advance_amount_7=total_advance_amount_8 = total_advance_amount_10 = 0.0

		search_receipts_advance_sr = self.pool.get('account.sales.receipts').search(cr,uid,[('receipt_date','>=',from_date),
										                ('receipt_date','<=',to_date),
										                ('receipt_no','!=',''),
										                ('state','!=','draft')])
		part_list=[]
		acc_list=[]								
		for receipts in self.pool.get('account.sales.receipts').browse(cr,uid,search_receipts_advance_sr):
		        for rec_line in receipts.sales_receipts_one2many:
		                for advance_receipt in rec_line.advance_one2many:
        		                if tax_list[0] in rec_line.account_id.name :
					        total_advance_amount_1 += advance_receipt.ref_amount
				        elif tax_list[1] in rec_line.account_id.name :
					        total_advance_amount_2 += advance_receipt.ref_amount
				        elif tax_list[2] in rec_line.account_id.name :
					        total_advance_amount_3 += advance_receipt.ref_amount
				        elif tax_list[3] in rec_line.account_id.name :
					        total_advance_amount_4 += advance_receipt.ref_amount
				        elif tax_list[4] in rec_line.account_id.name :
					        total_advance_amount_5 += advance_receipt.ref_amount
				        elif tax_list[5] in rec_line.account_id.name :
					        total_advance_amount_6 += advance_receipt.ref_amount
					elif tax_list[6] in rec_line.account_id.name :
					        total_advance_amount_7 += advance_receipt.ref_amount
					elif tax_list[7] in rec_line.account_id.name :
					        total_advance_amount_8 += advance_receipt.ref_amount
					elif 'Non Taxable' in rec_line.account_id.name :
					        total_advance_amount_10 += advance_receipt.ref_amount

		search_jv_advance = self.pool.get('account.journal.voucher').search(cr,uid,[('date','>=',from_date),
										                ('date','<=',to_date),
										                ('jv_number','!=',''),
										                ('state','!=','draft')])
										
		for receipts in self.pool.get('account.journal.voucher').browse(cr,uid,search_jv_advance):
		        for rec_line in receipts.journal_voucher_one2many:
		                if rec_line.account_id.account_selection == 'advance':
        		                if tax_list[0] in rec_line.account_id.name :
					        total_advance_amount_1 += rec_line.credit_amount
				        elif tax_list[1] in rec_line.account_id.name :
					        total_advance_amount_2 += rec_line.credit_amount
				        elif tax_list[2] in rec_line.account_id.name :
					        total_advance_amount_3 += rec_line.credit_amount
				        elif tax_list[3] in rec_line.account_id.name :
					        total_advance_amount_4 += rec_line.credit_amount
				        elif tax_list[4] in rec_line.account_id.name :
					        total_advance_amount_5 += rec_line.credit_amount
				        elif tax_list[5] in rec_line.account_id.name :
					        total_advance_amount_6 += rec_line.credit_amount
					elif tax_list[6] in rec_line.account_id.name :
					        total_advance_amount_7 += rec_line.credit_amount
					elif tax_list[7] in rec_line.account_id.name :
					        total_advance_amount_8 += rec_line.credit_amount
					elif 'Non Taxable' in rec_line.account_id.name :
					        total_advance_amount_10 += rec_line.credit_amount
						
	#### less cheque bounce advance value from the advance receipts if invoice is not settled##########
		cheque_dish_amt_22 = cheque_dish_amt_33 = cheque_dish_amt_44 = cheque_dish_amt_66 = cheque_dish_amt_77 = 0.0
		cheque_dish_amt_55 = cheque_dish_amt_11 = cheque_dish_amt_100 = cheque_dish_amt_88 = 0.0
		search_receipts_advance_sr = self.pool.get('account.sales.receipts').search(cr,uid,[('receipt_date','>=',from_date),
										                ('receipt_date','<=',to_date),
										                ('receipt_no','!=',''),
										                ('state','!=','draft')])		

		if search_receipts_advance_sr:
			for receipts in self.pool.get('account.sales.receipts').browse(cr,uid,search_receipts_advance_sr):
				for rec_line in receipts.sales_receipts_one2many:
					if rec_line.account_id.account_selection=='advance':
						if not rec_line.advance_invoice_one2many:
							srch_cheque = self.pool.get('cheque.bounce').search(cr,uid,[('payment_no','!=',''),
								('payment_date','>=',from_date),
								('payment_date','<=',to_date),
								('state','!=','draft'),('partner_id','=',receipts.customer_name.id)])

							for cheque in self.pool.get('cheque.bounce').browse(cr,uid,srch_cheque):
								for line in cheque.cheque_bounce_lines:
									if line.advance_cheque_bounce_one2many:
										for n_line_advance in line.advance_cheque_bounce_one2many:
											if line.account_id.account_selection=='advance':
												if n_line_advance.receipt_no==receipts.receipt_no:
													acc_list.append(cheque.id)
		if acc_list:
			for cheque in self.pool.get('cheque.bounce').browse(cr,uid,acc_list):
				for line in cheque.cheque_bounce_lines:
					if line.advance_cheque_bounce_one2many and line.account_id.account_selection=='advance':
						for rec in line.advance_cheque_bounce_one2many:
							account_id_name = line.account_id.name
							account_split = account_id_name.split(' ')
							account_name = [str(x) for x in account_split]
					       	if rec.cheque_bounce_boolean == True:
						       	if str(tax_list[0]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_11 += rec.ref_amount
						        if str(tax_list[1]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_22 += rec.ref_amount
						        if str(tax_list[2]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_33 += rec.ref_amount
						        if str(tax_list[3]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_44 += rec.ref_amount
						        if str(tax_list[4]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_55 += rec.ref_amount
						        if str(tax_list[5]) in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_66 += rec.ref_amount
						        if str(tax_list[6]) in  str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_77 += rec.ref_amount
						        if str(tax_list[7]) in  str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_88 += rec.ref_amount
						        if str('non_taxable') in str(account_name[4]):
						            if rec.cheque_bounce_boolean == True:
						                cheque_dish_amt_100 += rec.ref_amount
		if total_advance_amount_1 and cheque_dish_amt_11:
			total_advance_amount_1 = total_advance_amount_1 - cheque_dish_amt_11 
		if total_advance_amount_2 and cheque_dish_amt_22:
			total_advance_amount_2 = total_advance_amount_2 - cheque_dish_amt_22
		if total_advance_amount_3 and cheque_dish_amt_33:
			total_advance_amount_3 = total_advance_amount_3 - cheque_dish_amt_33
		if total_advance_amount_4 and cheque_dish_amt_44:
			total_advance_amount_4 = total_advance_amount_4 - cheque_dish_amt_44
		if total_advance_amount_5 and cheque_dish_amt_55:
			total_advance_amount_5 = total_advance_amount_5 - cheque_dish_amt_55
		if total_advance_amount_6 and cheque_dish_amt_66:
			total_advance_amount_6 = total_advance_amount_6 - cheque_dish_amt_66
		if total_advance_amount_7 and cheque_dish_amt_77:
			total_advance_amount_7 = total_advance_amount_7 - cheque_dish_amt_77
		if total_advance_amount_10 and cheque_dish_amt_100:
			total_advance_amount_10 = total_advance_amount_10 - cheque_dish_amt_100
	################################################# end #############
		self.write(cr,uid,res.id,{
						'period_collection1':total_collection_1,
						'period_collection2':total_collection_2,                
						'period_collection3':total_collection_3,
						'period_collection4':total_collection_4,
						'period_collection5':total_collection_5,
						'period_collection6':total_collection_6,                
						'period_collection7':total_collection_7,
						'period_collection8':total_collection_8,                
						'period_collection10':total_collection_10,
						
						'head_office_collection1':total_jv_head_amount1,
						'head_office_collection2':total_jv_head_amount2,        
						'head_office_collection3':total_jv_head_amount3,
						'head_office_collection4':total_jv_head_amount4,
						'head_office_collection5':total_jv_head_amount5,
						'head_office_collection6':total_jv_head_amount6,        
						'head_office_collection7':total_jv_head_amount7,
						'head_office_collection8':total_jv_head_amount8,        
						'head_office_collection10':total_jv_head_amount10,
						
						'collection_other_branches1':total_jv_amount1,
						'collection_other_branches2':total_jv_amount2,          
						'collection_other_branches3':total_jv_amount3,
						'collection_other_branches4':total_jv_amount4,
						'collection_other_branches5':total_jv_amount5,
						'collection_other_branches6':total_jv_amount6,          
						'collection_other_branches7':total_jv_amount7,
						'collection_other_branches8':total_jv_amount8,          
						'collection_other_branches10':total_jv_amount10,
						'collection_other_branches11':total_jv_amount11,

						'credit_note1':total_credit_note_1,
						'credit_note2':total_credit_note_2,                     
						'credit_note3':total_credit_note_3,
						'credit_note4':total_credit_note_4,
						'credit_note5':total_credit_note_5,
						'credit_note6':total_credit_note_6,                     
						'credit_note7':total_credit_note_7,
						'credit_note8':total_credit_note_8,                      
						'credit_note10':total_credit_note_10,
						
						'advance_receipt1':advance_receipt_amt_1,
						'advance_receipt2':advance_receipt_amt_2,               
						'advance_receipt3':advance_receipt_amt_3,
						'advance_receipt4':advance_receipt_amt_4,
						'advance_receipt5':advance_receipt_amt_5,
						'advance_receipt6':advance_receipt_amt_6,               
						'advance_receipt7':advance_receipt_amt_7,
						'advance_receipt8':advance_receipt_amt_8,                 
						'advance_receipt10':advance_receipt_amt_10,  
						
						'other_branch_collection1':total_dr_amt_1,  
						'other_branch_collection2':total_dr_amt_2,              
						'other_branch_collection3':total_dr_amt_3,              
						'other_branch_collection4':total_dr_amt_4,
						'other_branch_collection5':total_dr_amt_5,
						'other_branch_collection6':total_dr_amt_6,
						'other_branch_collection7':total_dr_amt_7,
						'other_branch_collection8':total_dr_amt_8,             
						'other_branch_collection10':total_dr_amt_10,
						
						'debit_notes1':total_debit_amount_1,
						'debit_notes2':total_debit_amount_2,                    
						'debit_notes3':total_debit_amount_3,
						'debit_notes4':total_debit_amount_4, 
						'debit_notes5':total_debit_amount_5,                   
						'debit_notes6':total_debit_amount_6,                    
						'debit_notes7':total_debit_amount_7,
						'debit_notes8':total_debit_amount_8,                    
						'debit_notes10':total_debit_amount_10,
						
						'cheques_dishonoured1':cheque_dish_amt_1,
						'cheques_dishonoured2':cheque_dish_amt_2,               
						'cheques_dishonoured3':cheque_dish_amt_3,
						'cheques_dishonoured4':cheque_dish_amt_4,
						'cheques_dishonoured5':cheque_dish_amt_5,
						'cheques_dishonoured6':cheque_dish_amt_6, 
						'cheques_dishonoured7':cheque_dish_amt_7,
						'cheques_dishonoured8':cheque_dish_amt_8,
						'cheques_dishonoured10':cheque_dish_amt_10,
						
						'excess_collection1':total_advance_amount_1,
						'excess_collection2':total_advance_amount_2,            
						'excess_collection3':total_advance_amount_3,
						'excess_collection4':total_advance_amount_4, 
						'excess_collection5':total_advance_amount_5,           
						'excess_collection6':total_advance_amount_6,            
						'excess_collection7':total_advance_amount_7,
						'excess_collection8':total_advance_amount_8,             
						'excess_collection10':total_advance_amount_10,
						
						'sales_refund1':total_credit_refund1,
						'sales_refund2':total_credit_refund2,                   
						'sales_refund3':total_credit_refund3,
						'sales_refund4':total_credit_refund4,
						'sales_refund5':total_credit_refund5,
						'sales_refund6':total_credit_refund6,                   
						'sales_refund7':total_credit_refund7,
						'sales_refund8':total_credit_refund8,
						'sales_refund10':total_credit_refund10,
						})
						
		for rec_amt in self.browse(cr,uid,ids):
			total_outstanding1 = rec_amt.opening_outstanding1 + rec_amt.month_bill1 - rec_amt.period_collection1 - rec_amt.head_office_collection1 - rec_amt.collection_other_branches1 - rec_amt.credit_note1 - rec_amt.advance_receipt1 + rec_amt.other_branch_collection1 + rec_amt.debit_notes1 + rec_amt.cheques_dishonoured1 + rec_amt.excess_collection1 + rec_amt.sales_refund1

			total_outstanding2 = rec_amt.opening_outstanding2 + rec_amt.month_bill2 - rec_amt.period_collection2 - rec_amt.head_office_collection2 - rec_amt.collection_other_branches2 - rec_amt.credit_note2 - rec_amt.advance_receipt2 + rec_amt.other_branch_collection2 + rec_amt.debit_notes2 + rec_amt.cheques_dishonoured2 + rec_amt.excess_collection2 + rec_amt.sales_refund2

			total_outstanding3 = rec_amt.opening_outstanding3 + rec_amt.month_bill3 - rec_amt.period_collection3 - rec_amt.head_office_collection3 - rec_amt.collection_other_branches3 - rec_amt.credit_note3 - rec_amt.advance_receipt3 + rec_amt.other_branch_collection3 + rec_amt.debit_notes3 + rec_amt.cheques_dishonoured3 + rec_amt.excess_collection3 + rec_amt.sales_refund3

			total_outstanding4 = rec_amt.opening_outstanding4 + rec_amt.month_bill4 - rec_amt.period_collection4 - rec_amt.head_office_collection4 - rec_amt.collection_other_branches4 - rec_amt.credit_note4 - rec_amt.advance_receipt4 + rec_amt.other_branch_collection4 + rec_amt.debit_notes4 + rec_amt.cheques_dishonoured4 + rec_amt.excess_collection4 + rec_amt.sales_refund4

			total_outstanding5 = rec_amt.opening_outstanding5 + rec_amt.month_bill5 - rec_amt.period_collection5 - rec_amt.head_office_collection5 - rec_amt.collection_other_branches5 - rec_amt.credit_note5 - rec_amt.advance_receipt5 + rec_amt.other_branch_collection5 + rec_amt.debit_notes5 + rec_amt.cheques_dishonoured5 + rec_amt.excess_collection5 + rec_amt.sales_refund5

			total_outstanding6 = rec_amt.opening_outstanding6 + rec_amt.month_bill6 - rec_amt.period_collection6 - rec_amt.head_office_collection6 - rec_amt.collection_other_branches6 - rec_amt.credit_note6 - rec_amt.advance_receipt6 + rec_amt.other_branch_collection6 + rec_amt.debit_notes6 + rec_amt.cheques_dishonoured6 + rec_amt.excess_collection6 + rec_amt.sales_refund6

			total_outstanding7 = rec_amt.opening_outstanding7 + rec_amt.month_bill7 - rec_amt.period_collection7 - rec_amt.head_office_collection7 - rec_amt.collection_other_branches7 - rec_amt.credit_note7 - rec_amt.advance_receipt7 + rec_amt.other_branch_collection7 + rec_amt.debit_notes7 + rec_amt.cheques_dishonoured7 + rec_amt.excess_collection7 + rec_amt.sales_refund7
			total_outstanding8 = rec_amt.opening_outstanding8 + rec_amt.month_bill8 - rec_amt.period_collection8 - rec_amt.head_office_collection8 - rec_amt.collection_other_branches8 - rec_amt.credit_note8 - rec_amt.advance_receipt8 + rec_amt.other_branch_collection8 + rec_amt.debit_notes8 + rec_amt.cheques_dishonoured8* + rec_amt.excess_collection8 + rec_amt.sales_refund8
			
			total_outstanding10 = rec_amt.opening_outstanding10 + rec_amt.month_bill10 - rec_amt.period_collection10 - rec_amt.head_office_collection10 - rec_amt.collection_other_branches10 - rec_amt.credit_note10 - rec_amt.advance_receipt10 + rec_amt.other_branch_collection10 + rec_amt.debit_notes10 + rec_amt.cheques_dishonoured10 + rec_amt.excess_collection10 + rec_amt.sales_refund10
			
			total_outstanding11 = rec_amt.month_bill_new_company + rec_amt.opening_outstanding11 - rec_amt.collection_other_branches11

			final_total = total_outstanding1 + total_outstanding2 + total_outstanding3 + total_outstanding4 + total_outstanding6 + total_outstanding5 + total_outstanding7 + total_outstanding8 + total_outstanding10 + total_outstanding11
			print 'Final Value to be Write total_outstanding6:',total_outstanding6
			self.write(cr,uid,rec_amt.id,{'outstanding1':round(total_outstanding1,2),'outstanding2':round(total_outstanding2,2),
                                        'outstanding3':round(total_outstanding3,2),'outstanding4':round(total_outstanding4,2),
                                        'outstanding5':round(total_outstanding5,2),'outstanding6':round(total_outstanding6,2),
                                'outstanding7':round(total_outstanding7,2),'outstanding8':round(total_outstanding8,2),'outstanding10':round(total_outstanding10,2),'outstanding11':round(total_outstanding11,2),
                                'total_outstanding1':round(final_total,2)})
		return True


	def opening_for_march(self,cr,uid,ids,date1,tax_rate,context=None):
		opening_balance_obj = self.pool.get('opening.balance')
		account_march_id=0
		grand_total_month = [0]
		if tax_rate == '10.20':
			cr.execute("select id from account_account where name ilike '%10.20%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
		if tax_rate == '10.30':
			cr.execute("select id from account_account where name ilike '%10.30%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
		if tax_rate == '12.24':
			cr.execute("select id from account_account where name ilike '%12.24%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
		if tax_rate == '12.36':
			cr.execute("select id from account_account where name ilike '%12.36%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
		if tax_rate == '14.0':
			cr.execute("select id from account_account where name ilike '%14.0%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
		if tax_rate == '14.5':
			cr.execute("select id from account_account where name ilike '%14.5%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
		if tax_rate == '15.0':
			cr.execute("select id from account_account where name ilike '%15.0%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
		if tax_rate == '18.0':
			cr.execute("select id from account_account where name ilike '%18.0%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = int(opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance)
				print 'sdfsdfddb:',opening_balance
				grand_total_month = [opening_balance]
		if tax_rate == 'non_taxable':
			cr.execute("select id from account_account where name ilike '%Non Taxable%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
		if account_march_id==0:
			return 0.0	
		return grand_total_month[0] if grand_total_month[0] else 0.0 
		
	def opening_outstanding(self,cr,uid,ids,from_date,date1,tax_rate,context=None):
		opening_balance = opening_total = [0.0]
		opening_balance_obj = self.pool.get('opening.balance')
		account_march_id=0
		if tax_rate == '10.20':
			cr.execute("select id from account_account where name ilike '%10.20%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		if tax_rate == '10.30':
			cr.execute("select id from account_account where name ilike '%10.30%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		if tax_rate == '12.24':
			cr.execute("select id from account_account where name ilike '%12.24%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		if tax_rate == '12.36':
			cr.execute("select id from account_account where name ilike '%12.36%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		if tax_rate == '14.0':
			cr.execute("select id from account_account where name ilike '%14.0%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		if tax_rate == '14.5':
			print 'we are calculating 14.5 value 6:' 
			cr.execute("select id from account_account where name ilike '%14.5%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		if tax_rate == '15.0':
			cr.execute("select id from account_account where name ilike '%15.0%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		if tax_rate == '18.0':
			cr.execute("select id from account_account where name ilike '%18.0%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		if tax_rate == 'non_taxable':
			cr.execute("select id from account_account where name ilike '%Non Taxable%' and parent_id =(select id from account_account where name='Sundry Debtors')")
			account_id = cr.fetchone()
			if account_id or account_id !=None:
				account_march_id = account_id[0]
			search_opening_balance = opening_balance_obj.search(cr,uid,[('account_id','=',account_march_id),('start_date','=','2017-03-01')])
			if search_opening_balance:
				opening_balance = opening_balance_obj.browse(cr,uid,search_opening_balance[0]).opening_balance
				grand_total_month = [opening_balance]
				opening_total = grand_total_month
		# print "dfgsdfudkfhifgijhffjd",from_date,tax_rate
		str_query="select sum(a.pending_amount+outstanding_invoice_function(a.id,'%s')) from invoice_adhoc_master a where a.invoice_number is not null and invoice_date >= '2017-03-01' and invoice_date <= '%s' and tax_rate ='%s' and status != 'cancelled' " %(str(from_date),str(from_date),tax_rate)
		cr.execute(str_query)
		grand_total_month2=cr.fetchone()
		if grand_total_month2[0] == None:
			grand_total_month2 = [0]
		if grand_total_month2[0] == 0:
			grand_total_month1 =  grand_total_month2[0]
		else:
			grand_total_month1 = grand_total_month2[0]+opening_total[0]
		# grand_total_month1 =  grand_total_month2[0]+opening_total[0] #"""grand_total_month2[0]+"""
		grand_total_month1 = [grand_total_month1]
		if account_march_id==0:
			return 0.0
		return grand_total_month1[0] if grand_total_month1[0] else 0.0
	
	def billing_month (self,cr,uid,ids,from_date,to_date,tax_rate,context=None):
		branch_pcof_key	= self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		main_str="select sum(grand_total_amount) from invoice_adhoc_master where id in (select id from invoice_adhoc_master where id > 0 and tax_rate='"+str(tax_rate)+"'  and invoice_number != '' and invoice_number not like '%%NT%%' and invoice_date >= '"+str(from_date)+"' and invoice_date <= '"+str(to_date)+"' and status not in  ('cancelled')) and invoice_number ilike '%"+str(branch_pcof_key)+"%' and cust_name not ilike 'Pest Control (India) Pvt Ltd'"
		# main_str="select sum(grand_total_amount) from invoice_adhoc_master where id in (select id from invoice_adhoc_master where id > 0 and tax_rate='"+str(tax_rate)+"'  and invoice_number != '' and invoice_date >= '"+str(from_date)+"' and invoice_date <= '"+str(to_date)+"' and status not in  ('cancelled')) and invoice_number ilike '%"+str(branch_pcof_key)+"%'"
		cr.execute(main_str)
		grand_total_month = cr.fetchone() 
		return grand_total_month[0] if grand_total_month else 0.0

	def billing_month_new_company (self,cr,uid,ids,from_date,to_date,tax_rate,context=None):
		branch_pcof_key	= self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		main_str="select sum(grand_total_amount) from invoice_adhoc_master where id in (select id from invoice_adhoc_master where id > 0 and tax_rate='"+str(tax_rate)+"'  and invoice_number != '' and invoice_number not like '%%NT%%' and invoice_date >= '"+str(from_date)+"' and invoice_date <= '"+str(to_date)+"' and status not in  ('cancelled')) and invoice_number ilike '%"+str(branch_pcof_key)+"%' and cust_name ilike 'Pest Control (India) Pvt Ltd'"
		# main_str="select sum(grand_total_amount) from invoice_adhoc_master where id in (select id from invoice_adhoc_master where id > 0 and tax_rate='"+str(tax_rate)+"'  and invoice_number != '' and invoice_date >= '"+str(from_date)+"' and invoice_date <= '"+str(to_date)+"' and status not in  ('cancelled')) and invoice_number ilike '%"+str(branch_pcof_key)+"%'"
		cr.execute(main_str)
		grand_total_month = cr.fetchone()
		print "ssssssssssssssssssssssss",grand_total_month
		return grand_total_month[0] if grand_total_month else 0.0

	def billing_month_nt (self,cr,uid,ids,from_date,to_date,tax_rate,context=None):
		branch_pcof_key	= self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		main_str="select sum(grand_total_amount) from invoice_adhoc_master where id in (select id from invoice_adhoc_master where id > 0 and tax_rate='"+str(tax_rate)+"'  and invoice_number != '' and invoice_number ilike '%%NT%%' and invoice_date >= '"+str(from_date)+"' and invoice_date <= '"+str(to_date)+"' and status not in  ('cancelled')) and invoice_number ilike '%"+str(branch_pcof_key)+"%' and cust_name not ilike 'Pest Control (India) Pvt Ltd'"
		# main_str="select sum(grand_total_amount) from invoice_adhoc_master where id in (select id from invoice_adhoc_master where id > 0 and tax_rate='"+str(tax_rate)+"'  and invoice_number != '' and invoice_date >= '"+str(from_date)+"' and invoice_date <= '"+str(to_date)+"' and status not in  ('cancelled')) and invoice_number ilike '%"+str(branch_pcof_key)+"%'"
		cr.execute(main_str)
		grand_total_month = cr.fetchone() 
		return grand_total_month[0] if grand_total_month else 0.0
		
monthly_report()

class debtors_report_query(osv.osv):
        _name='debtors.report.query'
	_columns = {
	        'opening_string':fields.char('String',size=256),
	        'opening_invoice_number':fields.char('Invoice_number',size=256),
	        'opening_amount':fields.float('opening amount'),
	        
	        'paid_string':fields.char('String',size=256),
	        'paid_invoice_number':fields.char('Invoice_number',size=256),
	        'paid_amount':fields.float('Paid amount'),
	        
	        'net_amount':fields.float('opening - Paid Amount'),
	        
	        'closing_invoice_number':fields.char('Invoice_number',size=256),
                'closing_amount':fields.float('closing amount'),
                
                'final_diff':fields.float('Difference in amount(net_amount-closing_amount)'),
               }
	_defaults = {
	        'opening_amount':0.0,
	        'paid_amount':0.0,
	        'net_amount':0.0,
	        'closing_amount':0.0,
	        'final_diff':0.0,
	        }
               
	def generate_data_xls(self,cr,uid,from_date,to_date,tax_rate,context=None):
	        date1=datetime.strptime(from_date,'%Y-%m-%d')
                prev_date=date1-relativedelta(days=1)
	        cr.execute("truncate TABLE debtors_report_query")
	        
	        opening_query="insert into debtors_report_query(opening_string,opening_invoice_number,opening_amount) (select  'opening',invoice_number,sum(pending_amount+outstanding_invoice_function(id,'"+str(prev_date)+"')) as amount from invoice_adhoc_master where invoice_date <='"+str(prev_date)+"' and tax_rate='"+str(tax_rate)+"' group by invoice_number having sum(pending_amount+outstanding_invoice_function(id,'"+str(prev_date)+"'))>0) union all (select 'bill invoice',invoice_number,grand_total_amount as amount from invoice_adhoc_master where invoice_date between '"+str(from_date)+"' and '"+str(to_date)+"' and tax_rate='"+str(tax_rate)+"' and status <>'cancelled')"
	        cr.execute(opening_query)
                paid_query="UPDATE debtors_report_query A set paid_string=concat_ws('/',A.paid_string,B.nm),paid_invoice_number=B.invoice_number,paid_amount=(coalesce(A.paid_amount,0)+coalesce(B.amount,0)) FROM debtors_report_query as A1 INNER JOIN(select B1.nm,B1.invoice_number,B1.amount from ((select 'sales_receipt' as nm,irh.invoice_number as invoice_number,sum(irh.invoice_paid_amount) as amount from account_sales_receipts asr join account_sales_receipts_line asrl on asr.id=asrl.receipt_id join invoice_receipt_history irh on irh.receipt_id_history=asrl.id where asr.receipt_date between '"+str(from_date)+"' and '"+str(to_date)+"' and irh.tax_rate='"+str(tax_rate)+"' group by irh.invoice_number) union all (select 'JV_CBOB' as nm,irh.invoice_number as invoice_number,sum(irh.invoice_paid_amount) as amount from account_journal_voucher  ajv join account_journal_voucher_line ajvl on ajv.id=ajvl.journal_voucher_id join invoice_receipt_history irh on ajvl.id=irh.jv_id_history where ajv.date between '"+str(from_date)+"' and '"+str(to_date)+"' and ajvl.customer_name in (select id from res_partner where name ='CBOB' )  and irh.tax_rate='"+str(tax_rate)+"'  group by irh.invoice_number) union all (select 'advance_settlement' as nm,invoice_number as invoice_number,sum(amount) as amount from (select ail.invoice_number,sum(ail.partial_payment_amount)as amount from advance_invoice_line ail join account_sales_receipts_line asrl on asrl.id=ail.advance_invoice_line_id join account_sales_receipts asr on asr.id=asrl.receipt_id  where asr.receipt_date <='"+str(to_date)+"' and ail.paid_date between '"+str(from_date)+"' and '"+str(to_date)+"' and asrl.payment_status='partial_payment' and ail.tax_rate='"+str(tax_rate)+"'  group by ail.invoice_number union all select ail.invoice_number,sum(ail.invoice_amount)as amount from advance_invoice_line  ail join account_sales_receipts_line  asrl on asrl.id=ail.advance_invoice_line_id join account_sales_receipts asr on asr.id=asrl.receipt_id  where asr.receipt_date <='"+str(to_date)+"' and ail.paid_date between '"+str(from_date)+"' and '"+str(to_date)+"' and asrl.payment_status <> 'partial_payment' and ail.tax_rate='"+str(tax_rate)+"' group by ail.invoice_number)total group by total.invoice_number order by total.invoice_number) union all (select  'CN ST' as nm,irh.invoice_number as invoice_number ,irh.invoice_writeoff_amount as amount from invoice_receipt_history irh join credit_note_line_st cnl on irh.credit_st_id_history=cnl.id join credit_note_st cn on cn.id=cnl.credit_st_id where cn.credit_note_date between '"+str(from_date)+"' and '"+str(to_date)+"' and irh.tax_rate='"+str(tax_rate)+"') union all (select  'Cheque Bounce' as nm,irh.invoice_number as invoice_number ,-irh.invoice_paid_amount as amount from invoice_receipt_history irh join cheque_bounce_line cbl on irh.debit_invoice_id_cheque_bounce_new=cbl.id join cheque_bounce cb on cb.id=cbl.cheque_bounce_line_id where cb.payment_date between '"+str(from_date)+"' and '"+str(to_date)+"' and irh.tax_rate='"+str(tax_rate)+"'))B1)B ON  A1.opening_invoice_number=B.invoice_number WHERE A.id=A1.id"
                cr.execute(paid_query)
                
                net_query="UPDATE debtors_report_query A set net_amount=(coalesce(A.opening_amount,0)-coalesce(A.paid_amount,0)) "
                cr.execute(net_query)
                
	        closing_query="update debtors_report_query A set closing_invoice_number=B.invoice_number,closing_amount=B.amount FROM debtors_report_query A1 INNER JOIN (select invoice_number,sum(pending_amount+outstanding_invoice_function(id,'"+str(to_date)+"'))as amount from invoice_adhoc_master where invoice_date <='"+str(to_date)+"' and tax_rate='"+str(tax_rate)+"' and status <> 'cancelled' group by invoice_number having sum(pending_amount+outstanding_invoice_function(id,'"+str(to_date)+"'))>0)B ON  A1.opening_invoice_number=B.invoice_number WHERE A.id=A1.id"
	        cr.execute(closing_query)
                
                final_query="UPDATE debtors_report_query A set final_diff=(coalesce(A.net_amount,0)-coalesce(A.closing_amount,0))"
                cr.execute(final_query)
                
                return True

