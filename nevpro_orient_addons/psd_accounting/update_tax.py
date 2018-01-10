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
import collections


class update_invoice_taxes(osv.osv):
	_name= 'update.invoice.taxes'


	def service_update_invoice_taxes(self, cr, uid, ids, context=None):
		invoice_obj = self.pool.get('invoice.adhoc.master')
		tax_obj = self.pool.get('account.tax')
		inv_tax_obj = self.pool.get('invoice.tax.rate')
		acc_acc_obj = self.pool.get('account.account')
		invoice_adhoc_line = self.pool.get('invoice.adhoc')
		rec = self.browse(cr, uid, ids[0])
		tax_ids = tax_obj.search(cr,uid,[('active','=',True),('effective_from_date','!=',False),('effective_to_date','!=',False)],context=context)
		for tax_id in tax_ids:
			tax = tax_obj.browse(cr,uid,tax_id)
			effective_from_date = tax.effective_from_date
			effective_to_date = tax.effective_to_date
			invoice_ids = invoice_obj.search(cr,uid,[('invoice_date','>=',effective_from_date),
													 ('invoice_date','<=',effective_to_date),('invoice_type','=','service_invoice')],context=context)
			if invoice_ids:
				account_id = acc_acc_obj.search(cr, uid, [('account_tax_many2one','=',tax_id)],context=context)
				tax_rate = float(tax.amount*100)
				for invoice_id in invoice_ids:
					inv_data = invoice_obj.browse(cr, uid, invoice_id)
					srch_line_id = invoice_adhoc_line.search(cr,uid,[('service_invoice_id','=',invoice_id)])
					total_basic_charge = 0.0
					for line in invoice_adhoc_line.browse(cr,uid,srch_line_id):
						print "--------------------",line.total_amount
						total_basic_charge += line.total_amount
					print "--------------------",total_basic_charge
					invoice_obj.write(cr,uid,inv_data.id,{'basic_charge':total_basic_charge})
					total_amount = inv_data.basic_charge
					amount = (total_amount*tax_rate)/100
					print "--------------------",amount,tax_rate,total_amount
					if not tax_one2many:
						inv_tax_id = inv_tax_obj.create(cr,uid,
							{
								'name':tax.name,
								'invoice_id':invoice_id,
								'tax_rate':str(tax_rate),
								'account_tax_id':tax_id,
								'amount': round(amount),
								'account_id':account_id[0]
							})
		return inv_tax_id


	def update_tax(self, cr, uid, ids, context=None):
		today_date =datetime.today().date()
		account_tax = self.pool.get('account.tax')
		tax_line_obj=self.pool.get('invoice.tax.rate')
		invoice_master_obj = self.pool.get('invoice.adhoc.master')
		invoice_line_obj = self.pool.get('invoice.adhoc')

		product_invoice_ids = invoice_master_obj.search(cr,uid,[('bird_pro','=',False),('invoice_type','=','product_invoice')])
		birdpro_invoice_ids = invoice_master_obj.search(cr,uid,[('bird_pro','=',True),('invoice_type','=','product_invoice')])
		if product_invoice_ids:
			tax_data =[]	
			dct=[]
			tax_rate =0
			tax_amount =0.0
			basic_charge = 0.0
			total_rate = 0.0
			total_qty = 0
			total_discount =0.0
			line_amount =0.0
			total_amount = []
			for srch_id in product_invoice_ids:
				invoice_brw = invoice_master_obj.browse(cr,uid,srch_id)
				if invoice_brw.product_invoice_lines:
					for invoice_line in invoice_brw.product_invoice_lines:
						tax_rate = invoice_line.tax_id.id
						tax_amount = invoice_line.tax_amount
						if tax_rate != False:
							tax_data.append((tax_rate,tax_amount))
						total_rate += invoice_line.rate
						total_qty += invoice_line.ordered_quantity
						total_discount += invoice_line.discount
						line_amount =  invoice_line.rate * invoice_line.ordered_quantity - invoice_line.discounted_amount
						total_amount.append(line_amount)

					basic_charge =sum(total_amount)
					self.pool.get('invoice.adhoc.master').write(cr,uid,invoice_brw.id,{'basic_charge':basic_charge})
					uniq_taxes = [(uk,sum([vv for kk,vv in tax_data if kk==uk])) for uk in set([k for k,v in tax_data])]
					for insert_tax in uniq_taxes:
						tax_name =account_tax.browse(cr,uid,insert_tax[0]).name
						if not invoice_brw.tax_one2many:
							tax_line_obj.create(cr,uid,{'name':tax_name,
																			'account_tax_id':insert_tax[0],
																			'amount':insert_tax[1],
																			'invoice_id':invoice_brw.id})
		if birdpro_invoice_ids:
			tax_data1 =[]	
			dct1=[]
			tax_rate1 =0
			tax_amount1 =0.0
			basic_charge1 = 0.0
			total_rate1 = 0.0
			total_qty1 = 0
			total_discount1 =0.0
			line_amount1 =0.0
			total_amount1 = []
			for birdpro_id in birdpro_invoice_ids:
				cur_rec = invoice_master_obj.browse(cr,uid,birdpro_id)
				invoice_line_srch = invoice_line_obj.search(cr,uid,[('product_invoice_id','=',birdpro_id)])
				invoice_line_brws = invoice_line_obj.browse(cr,uid,invoice_line_srch)
				if invoice_line_srch:
					for invoice_line1 in invoice_line_brws:
						tax_rate1 = invoice_line1.tax_id.id
						tax_amount1 = invoice_line1.tax_amount
						if tax_rate1 != False:
							tax_data1.append((tax_rate1,tax_amount1))
						total_rate1 += invoice_line1.rate
						total_qty1 += invoice_line1.ordered_quantity
						total_discount1 += invoice_line1.discount
						line_amount1 =  invoice_line1.rate * invoice_line1.ordered_quantity - invoice_line1.discounted_amount
						total_amount1.append(line_amount1)

				basic_charge1 = sum(total_amount1)
				self.pool.get('invoice.adhoc.master').write(cr,uid,birdpro_id,{'basic_charge':basic_charge1})
				uniq_taxes1 = [(uk,sum([vv for kk,vv in tax_data1 if kk==uk])) for uk in set([k for k,v in tax_data1])]
				for insert_tax1 in uniq_taxes1:
					tax_name =account_tax.browse(cr,uid,insert_tax1[0]).name
					tax_line_obj.create(cr,uid,{'name':tax_name,
												'account_tax_id':insert_tax1[0],
												'amount':insert_tax1[1],
												'invoice_id':birdpro_id})

				account_service_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','service_tax')])
				if account_service_tax:
					service_tax14 = account_tax.browse(cr,uid,account_service_tax[0]).amount
					service_tax_name = account_tax.browse(cr,uid,account_service_tax[0]).name
					service_tax_value = cur_rec.bird_pro_charge * service_tax14
					service_tax_value = round(service_tax_value)
				account_sb_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','swachh_bharat_service')])
				if account_sb_tax:
					sb_cess_0_05 = account_tax.browse(cr,uid,account_sb_tax[0]).amount
					sb_cess_name = account_tax.browse(cr,uid,account_sb_tax[0]).name
					sb_tax_value = cur_rec.bird_pro_charge * sb_cess_0_05
					sb_tax_value = round(sb_tax_value)
				account_kk_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','krishi_kalyan_service')])
				if account_kk_tax:
					kk_cess_0_50 = account_tax.browse(cr,uid,account_kk_tax[0]).amount
					kk_cess_name = account_tax.browse(cr,uid,account_kk_tax[0]).name
					kk_tax_value = cur_rec.bird_pro_charge * kk_cess_0_50
					kk_tax_value = round(kk_tax_value)		
				# grand_total = cur_rec.bird_pro_charge + service_tax_value + sb_tax_value + kk_tax_value + total_vat_amount + main_form_total_amount
				tax_line_obj.create(cr,uid,{'psd_so_id':int(ids[0]),'account_tax_id':account_service_tax[0],'name':service_tax_name,'amount':service_tax_value,'invoice_id':birdpro_id},context=None)
				tax_line_obj.create(cr,uid,{'psd_so_id':int(ids[0]),'account_tax_id':account_sb_tax[0],'name':sb_cess_name,'amount':sb_tax_value,'invoice_id':birdpro_id})
				tax_line_obj.create(cr,uid,{'psd_so_id':int(ids[0]),'account_tax_id':account_kk_tax[0],'name':kk_cess_name,'amount':kk_tax_value,'invoice_id':birdpro_id})

		return True


update_invoice_taxes()