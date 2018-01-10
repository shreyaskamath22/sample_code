# version 1.0.054 --> Changes Related to Non-Taxable transaction process
# version 1.0.071 --> Changes Related to Addition of 14.5 % column in SOC report 18nov
from osv import osv,fields
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
import calendar
import re
from base.res import res_partner
import decimal_precision as dp
import datetime
from datetime import datetime
from datetime import timedelta
from time import strftime
from datetime import date
import xlsxwriter
import xlsxwriter as xls
from dateutil.relativedelta import relativedelta
import pdb
from tools.translate import _
from StringIO import StringIO
from xlsxwriter.utility import xl_rowcol_to_cell
import base64, urllib
from xlsxwriter.utility import xl_rowcol_to_cell
# import corporate_address
from sales_branch.report.corporate_address import *
from datetime import date,datetime, timedelta
from osv import osv,fields
import time
from base.res import res_partner
from datetime import datetime
import decimal_precision as dp
import time
from dateutil.relativedelta import relativedelta


class monthly_report(osv.osv):

	_inherit = 'monthly.report'

	_columns = {

		'taxable_total7':fields.float('Taxable 14.00 Total'), #  HHH
		'taxable_total7_cheque':fields.float('Taxable 14.00 Total'), #  HHH

		}



	def print_monthly_report(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids):
				cr.execute("SELECT pg_get_functiondef(oid) FROM pg_proc WHERE  proname = 'account_name_function'") 
				is_function=cr.fetchone()
				if not is_function :
								cr.execute("""CREATE OR Replace FUNCTION account_name_function()
								RETURNS double precision AS $sum$
								declare
								sum double precision ;
								begin
								update account_account aa set name=(case when aa.name ilike '%15.0%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 15.00%'
		when aa.name ilike '%14.5%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 14.50%'
		when aa.name ilike '%14.0%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 14.00%'
		when aa.name ilike '%12.36%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 12.36%'
		when aa.name ilike '%12.24%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 12.24%'
		when aa.name ilike '%10.30%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 10.30%'
		when aa.name ilike '%10.20%' and aa.account_selection='against_ref' then 'Sundry Debtors Service - (Taxable) 10.20%'
			else
		aa.name end) where aa.account_selection='against_ref';
		
						update cofb_sales_receipts csr set tax_rate=(case when csr.tax_rate='taxable_15_0' then '15.0'
						when csr.tax_rate='taxable_14_5' then '14.5'
						when csr.tax_rate='taxable_14_00' then '14.0'
						when csr.tax_rate='taxable_12_36' then '12.36'
						when csr.tax_rate='taxable_12_24' then '12.24'
						when csr.tax_rate='taxable_10_30' then '10.30'
						when csr.tax_rate='taxable_10_20' then '10.20' else
						csr.tax_rate end);
								return sum;
								end;
								$sum$
								LANGUAGE plpgSQL;""")
								cr.execute("SELECT account_name_function()") 
								
				from_date = res.from_date
				to_date = res.to_date
				monthly_selection = res.monthly_selection

				if not monthly_selection:
					raise osv.except_osv(('Alert'),('Please select type.'))
				if from_date == False:
					raise osv.except_osv(('Alert'),('Please select From Date.'))
				search_eff = self.pool.get('sync.invoice.adhoc.master').search(cr,uid,[('effective_date','!=',None)])
				a = self.pool.get('sync.invoice.adhoc.master').browse(cr,uid,search_eff)
				for each in a:
					search_eff_date = each.effective_date
					if from_date < search_eff_date:
						raise osv.except_osv(('Alert'),('Please select From Date greater than effective date.'))
				if to_date == False:
					raise osv.except_osv(('Alert'),('Please select To Date.'))

				if monthly_selection == 'stmt_collection':
					self.stmt_collection(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'summary_accounts':
					now=datetime.now().day

					now_date=datetime.strftime(datetime.now(),'%Y-%m')+'-01'
					if now in (1,2,3,4,5):
						date_current = datetime.strptime(now_date, "%Y-%m-%d")
						prev_date=date_current-relativedelta(months=1)
						account_srch=self.pool.get('account.account').search(cr,uid,[('account_selection','in',('iob_two','cash','iob_one'))])
						if account_srch:
							self.pool.get('account.account').write(cr,uid,account_srch[0],{'from_date_again':prev_date})
							self.pool.get('account.account').opening_bal_scheduler_again(cr,uid, [account_srch[0]])
					self.summary_of_accounts(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'stmt_bank_charges':
					self.statement_of_bank_charges(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'bank_slip_book':
					self.bank_slip_book_iob_one(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'stmt_cash_withdrawal':
					self.cash_withdrawal_cheque_payment(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'stmt_tds_recoveries':
					self.stmt_tds_recoveries(cr,uid,ids,from_date,to_date,context=context)
					
				if monthly_selection == 'stmt_recoveries':	
					self.stmt_recoveries(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'stmt_funds_transfer_a/c_II':
					self.stmt_funds_transfer_to_two(cr,uid,ids,from_date,to_date,context=context)
					
				if monthly_selection == 'stmt_funds_remitted':
					self.stmt_funds_remitted(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'stmt_debtors_reconciliation':
					self.stmt_debtors_reconciliation(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'cash_bank_payment_extract':
					self.cash_bank_payment_extract(cr,uid,ids,from_date,to_date,context=context)
				
				if monthly_selection == 'summary_service_tax':
					self.stmt_summary_service_tax(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'bank_reconciliation_iob_one':
						self.bank_reconciliation_iob_one(cr,uid,ids,from_date,to_date,context=context)
						
				if monthly_selection == 'bank_reconciliation_iob_two':
						self.bank_reconciliation_iob_two(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'cse_collection_summary':
						self.cse_collection_summary(cr,uid,ids,from_date,to_date,context=context)

				if monthly_selection == 'advance_adjustment':
						self.advance_adjustment_summary(cr,uid,ids,from_date,to_date,context=context) 

				if monthly_selection == 'fund_received_from_co_to_branch':
					self.fund_received_from_co_to_branch(cr, uid, ids, from_date, to_date, context=context) 

		for report in self.browse(cr,uid,ids):
			monthly_selection = report.monthly_selection
			from_date = report.from_date
			date = datetime.strptime(from_date, "%Y-%m-%d")
			date_year = date.year
			
			bank_three_id=self.pool.get('account.account').search(cr,uid,[('receive_bank_no', '=' ,'bank_three')])
			bank_three_id= bank_three_id if bank_three_id else False
			data = self.pool.get('monthly.report').read(cr, uid, [report.id],context)
			datas = {
					'ids': ids,
					'model': 'monthly.report',
					'form': data
					}
			if uid != 1:
								file_format='pdf'
								doc=str(monthly_selection) if monthly_selection else ''
								doc_name='monthly_report'
								self.pool.get('user.print.detail').update_rec(cr,uid,file_format,doc,doc_name)
								
			if from_date<'2017-07-01':
				if monthly_selection == 'stmt_collection' and bank_three_id  :
					return {
							'type': 'ir.actions.report.xml',
							'report_name': 'statement.collection.old.records.new1',
							'datas': datas,
							}
				if monthly_selection == 'stmt_collection' and  bank_three_id == False:
					return {
							'type': 'ir.actions.report.xml',
							'report_name': 'stmt_of_collection_old_records',
							'datas': datas,
							}
			if from_date>='2017-07-01':
				if monthly_selection == 'stmt_collection' and bank_three_id  :
					return {
							'type': 'ir.actions.report.xml',
							'report_name': 'gst_stmt_of_collection_new',
							'datas': datas,
							}
				if monthly_selection == 'stmt_collection' and  bank_three_id == False:
					return {
							'type': 'ir.actions.report.xml',
							'report_name': 'gst_stmt_of_collection',
							'datas': datas,
							}
			if monthly_selection == 'summary_accounts':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'summary.accounts',
						'datas': datas,
					}

			if monthly_selection == 'stmt_bank_charges':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.bank.charges',
						'datas': datas,
					}

			if monthly_selection == 'bank_slip_book':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'slip.book.one',
						'datas': datas,
					}

			if monthly_selection == 'stmt_cash_withdrawal':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'cash.withdraw.cheque.payment',
						'datas': datas,
					}

			if monthly_selection == 'stmt_tds_recoveries':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.tds.recoveries',
						'datas': datas,
					}


			if monthly_selection == 'stmt_recoveries':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.recoveries',
						'datas': datas,
					}

			if monthly_selection == 'stmt_funds_transfer_a/c_II':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.funds.transferred.two',
						'datas': datas,
					}
			
			if monthly_selection == 'stmt_funds_remitted':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.remitted',
						'datas': datas,
					}


			if monthly_selection == 'stmt_debtors_reconciliation':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'gst_statement_debtors_reconciliation',
						'datas': datas,
					}
			if monthly_selection == 'cash_bank_payment_extract':
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'statement.of.payment',
						'datas': datas,
					}

			if monthly_selection == 'bank_reconciliation_iob_one':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'bank.reconciliation.iob.one',
					'datas': datas,
				}
				
			if monthly_selection == 'bank_reconciliation_iob_two':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'bank.reconciliation.iob.two',
					'datas': datas,
				}
			if monthly_selection == 'summary_service_tax':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'stmt.summary.service.tax',
					'datas': datas,
				}

			if monthly_selection == 'cse_collection_summary':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'cse_collection_summary',
					'datas': datas,
					}

			if monthly_selection == 'advance_adjustment':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'advance.adjustment.summary',
					'datas': datas,
					}

			if monthly_selection == 'fund_received_from_co_to_branch':
				return {
					'type': 'ir.actions.report.xml',
					'report_name': 'fund.received.from.co.to.branch',
					'datas': datas,
					}

					
			'''if monthly_selection == 'credit_note_register':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'credit.note.register',
						'datas': datas,
					}'''
					
		return True

monthly_report()

class statement_collection(osv.osv):
	_inherit = 'statement.collection'

	_columns = {  #  HHH
		'taxable7':fields.float('Taxable @ 18.00'), #  HHH
		'taxable7_cheque':fields.float('Taxable @ 18.00'),
	}



statement_collection()


