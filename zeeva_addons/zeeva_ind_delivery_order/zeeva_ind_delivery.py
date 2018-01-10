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

from osv import fields,osv
import tools
import pooler
import time
from tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import timedelta,date,datetime

from datetime import datetime,date
from openerp import netsvc

from openerp.tools.amount_to_text_en import amount_to_text
from openerp.tools import float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT

import io
import cStringIO as StringIO
#import StringIO
import httplib

from PIL import Image
from PIL import ImageOps
from random import random

import math
import re
import os
import string
import locale

import calendar
import xlsxwriter
import logging
import binascii
import base64
from base64 import b64decode
from xlrd import open_workbook
from openerp import SUPERUSER_ID


_logger = logging.getLogger(__name__)


class stock_picking_out(osv.osv):
	_name = "stock.picking.out"
	_inherit = "stock.picking"
	_table = "stock_picking"
	_description = "Delivery Orders"




	def _amount_in_words(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			a=''
			b=''
			if order.currency_id.name == 'INR':
				a = 'Rupees'
				b = ''
			res[order.id] = amount_to_text(order.roundoff_grand_total, 'en', a).replace('and Zero Cent', b).replace('and Zero Cent', b)
		return res

	def _total_shipped_quantity(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			val = val1 = 0.0
			for line in order.move_lines:
				val1 += line.product_qty
			res[order.id] = val1
		return res

	def _total_billed_quantity(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			val = 0.0
			for line in order.move_lines:
				val += line.product_billed_qty
			res[order.id] = val
		return res

	# SELECTION_LIST = [
	# ('Financial Year(2016-2017)','Financial Year(2016-2017)'),
	# ('Financial Year(2017-2018)','Financial Year(2017-2018)'),
	# ('Financial Year(2018-2019)','Financial Year(2018-2019)'),
	# ('Financial Year(2019-2020)','Financial Year(2019-2020)'),
	# ]

	# def _get_financial_year(self, cr, uid, ids, field_name, arg, context=None):
	# 	res= {}
	# 	for x in self.browse(cr, uid, ids):
	# 		option=''
	# 		etd_date = x.date
	# 		option1='Financial Year(2016-2017)'
	# 		option2='Financial Year(2017-2018)'
	# 		option3='Financial Year(2018-2019)'
	# 		option4='Financial Year(2019-2020)'
	# 		if etd_date>='2016-04-01' and etd_date<='2017-03-31':
	# 			option=option1
	# 		if etd_date>='2017-04-01' and etd_date<='2018-03-31':
	# 			option=option2
	# 		if etd_date>='2018-04-01' and etd_date<='2019-03-31':
	# 			option=option3
	# 		if etd_date>='2019-04-01' and etd_date<='2020-03-31':
	# 			option=option4
	# 		res[x.id] = option
	# 	return res


	def _amount_line_tax(self, cr, uid, line, context=None):
		val = 0.0
		for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
			val += c.get('amount', 0.0)
		return val

	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()

	def _get_shipping_person(self, cr, uid, context=None):
		search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Shipping & Distribution')])
		search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
		for x in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
			userID = x.user_id.id
		return userID

	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		categ_id_append = []
		amount_total = []
		appended_value = []
		tax_variable = 0.0
		tax_value = 0.0
		total_variable = 0.0
		total_variable1 = 0.0
		product_tax_amount = 0.0
		tax_name = ''
		append_value = []
		account_tax=[]
		cur_obj = self.pool.get('res.currency')
		sale_order_line_obj = self.pool.get('sale.order.line')
		tax_summary_report_obj =self.pool.get('delivery.tax.summary.report')
		account_tax_obj = self.pool.get('account.tax')
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			main_form_id = order.id
			res[order.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
			}
			val = val1 = val2 = val3 = val4 = val5= val6 = 0.0
			cur = order.pricelist_id.currency_id
			partner_id = order.partner_id.id
			type_of_sales = order.partner_id.type_of_sales
			cform_criteria = order.partner_id.cform_criteria
			discount_value = order.discount_value
			apply_discount = order.apply_discount
			discount_value_id = discount_value/100
			for line in order.move_lines:
				val2 += line.price_subtotal
				cr.execute('select distinct(tax_applied_id) from stock_move where picking_id = %s',(main_form_id,))
				tax_id = map(lambda x: x[0], cr.fetchall())
				tax_applied_id = line.tax_applied_id.id
				tax_id_first = tax_id[0]
				if tax_applied_id == tax_id_first:
					val1 += line.price_subtotal
				product_tax_amount = self.pool.get('account.tax').browse(cr,uid,tax_id_first).amount
				product_tax_name = self.pool.get('account.tax').browse(cr,uid,tax_id_first).name
				product_tax_rate = self.pool.get('account.tax').browse(cr,uid,tax_id_first).tax_rate
				if len(tax_id) == 2:
					tax_id_second = tax_id[1]
					product_tax_amount_second = self.pool.get('account.tax').browse(cr,uid,tax_id_second).amount
					product_tax_name_second = self.pool.get('account.tax').browse(cr,uid,tax_id_second).name
					product_tax_rate_second = self.pool.get('account.tax').browse(cr,uid,tax_id_second).tax_rate
					val4 = val2 - val1 
					val5 = val4 * product_tax_amount_second
			val3 = val1 * product_tax_amount
			val6 = val3 + val5
			variable = {
						'tax_id': tax_id_first,
						'tx_name':str(product_tax_name),
						'tax_rate':product_tax_rate,
						'total_amount': val3,
						'stock_taxes_id':int(main_form_id)
			}
			tax_summary_report_obj_search = tax_summary_report_obj.search(cr,uid,[('stock_taxes_id','=',int(main_form_id)),('tax_id','=',tax_id_first)])
			if not tax_summary_report_obj_search:
				tax_summary_report_obj.create(cr,uid,variable)
			elif tax_summary_report_obj_search:
				cr.execute('update delivery_tax_summary_report set total_amount=%s where tax_id=%s and stock_taxes_id=%s',(val3,tax_id_first,main_form_id))
			if val3 == 0.0 and isinstance(tax_id_first,list):
				cr.execute('delete from delivery_tax_summary_report where id in %s',(tax_id_first,))
			if val3 == 0.0 and isinstance(tax_id_first,int):
				cr.execute('delete from delivery_tax_summary_report where id = %s',(tax_id_first,))
			if val4 != 0.0:
				tax_summary_report_obj_search_second = tax_summary_report_obj.search(cr,uid,[('stock_taxes_id','=',int(main_form_id)),('tax_id','=',tax_id_second)])
				variable1 = {
						'tax_id': tax_id_second,
						'tx_name':str(product_tax_name_second),
						'tax_rate':product_tax_rate_second,
						'total_amount': val5,
						'stock_taxes_id':int(main_form_id)
				}
				if not tax_summary_report_obj_search_second:
					tax_summary_report_obj.create(cr,uid,variable1)
				elif tax_summary_report_obj_search_second:
					cr.execute('update delivery_tax_summary_report set total_amount=%s where tax_id=%s and stock_taxes_id=%s',(val5,tax_id_second,main_form_id))
				if val5 == 0.0:
					cr.execute('delete from delivery_tax_summary_report where id in %s',(tax_id_second,))
			res[order.id]['amount_tax'] = val6
			res[order.id]['amount_untaxed'] = val2 #cur_obj.round(cr, uid, cur, val2)
			res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
			total_after_discount = res[order.id]['amount_total'] * discount_value_id
			if total_after_discount != 0.0 and apply_discount:
				res[order.id]['discounted_amount'] = total_after_discount
				res[order.id]['grand_total'] = res[order.id]['amount_total'] - total_after_discount
				roundoff_grand_total = res[order.id]['grand_total'] + 0.5
				s = str(roundoff_grand_total)
				dotStart = s.find('.')
				res[order.id]['roundoff_grand_total'] = int(s[:dotStart])
			else:
				res[order.id]['discounted_amount'] = 0.0
				res[order.id]['grand_total'] = res[order.id]['amount_total']
				roundoff_grand_total = res[order.id]['grand_total'] + 0.5
				s = str(roundoff_grand_total)
				dotStart = s.find('.')
				res[order.id]['roundoff_grand_total'] = int(s[:dotStart])
		return res

	# def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
	# 	categ_id_append = []
	# 	amount_total = []
	# 	appended_value = []
	# 	tax_variable = 0.0
	# 	tax_value = 0.0
	# 	total_variable = 0.0
	# 	total_variable1 = 0.0
	# 	tax_name = ''
	# 	append_value = []
	# 	account_tax=[]
	# 	cur_obj = self.pool.get('res.currency')
	# 	sale_order_line_obj = self.pool.get('sale.order.line')
	# 	tax_summary_report_obj =self.pool.get('delivery.tax.summary.report')
	# 	account_tax_obj = self.pool.get('account.tax')
	# 	res = {}
	# 	for order in self.browse(cr, uid, ids, context=context):
	# 		main_form_id = order.id
	# 		res[order.id] = {
	# 			'amount_untaxed': 0.0,
	# 			'amount_tax': 0.0,
	# 			'amount_total': 0.0,
	# 		}
	# 		val = val1 = 0.0
	# 		#cur = order.pricelist_id.currency_id
	# 		partner_id = order.partner_id.id
	# 		type_of_sales = order.partner_id.type_of_sales
	# 		cform_criteria = order.partner_id.cform_criteria
	# 		discount_value = order.discount_value
	# 		apply_discount = order.apply_discount
	# 		discount_value_id = discount_value/100
	# 		for line in order.move_lines:
	# 			val1 += line.price_subtotal
	# 			price_subtotal_value = line.price_subtotal 
	# 			product_category_id = line.product_category_id.id
	# 			if type_of_sales == 'interstate' and cform_criteria == 'agreed':
	# 				tax_value = line.product_category_id.sale_with_cform.amount
	# 				tax_id = line.product_category_id.sale_with_cform.id
	# 			if type_of_sales == 'interstate' and cform_criteria == 'disagreed' or type_of_sales == 'within_state':
	# 				tax_value = line.product_category_id.sale_without_cform.amount
	# 				tax_id = line.product_category_id.sale_without_cform.id
	# 			if tax_id not in append_value:
	# 				append_value.append(tax_id)
	# 			if categ_id_append ==[]:
	# 				categ_id_append.append(product_category_id)
	# 			if product_category_id in categ_id_append:
	# 				total_variable += line.price_subtotal
	# 				if tax_value != tax_variable:
	# 					tax_variable = tax_value
	# 			else:
	# 				total_variable1 += line.price_subtotal
	# 				different_categ_id_tax = total_variable1 * tax_value
	# 			appended_value.append(product_category_id)
	# 		same_categ_id_tax = total_variable * tax_variable
	# 		different_categ_id_tax = total_variable1 * tax_value
	# 		sum_tax_amount =same_categ_id_tax+different_categ_id_tax
	# 		account_tax_obj_search = account_tax_obj.search(cr,uid,[('id','in',append_value)])
	# 		account_tax_obj_browse = account_tax_obj.browse(cr,uid,account_tax_obj_search)
	# 		for account_tax_id in account_tax_obj_browse:
	# 			tax_id = account_tax_id.id
	# 			tax_name = account_tax_id.name
	# 			tax_rate = account_tax_id.tax_rate
	# 			tax_amount = account_tax_id.amount
	# 			if tax_variable == tax_value:
	# 				variable = {
	# 							'tax_id': tax_id,
	# 							'tx_name':str(tax_name),
	# 							'tax_rate':tax_rate,
	# 							'total_amount': sum_tax_amount,
	# 							'stock_taxes_id':int(main_form_id)
	# 				}
	# 			elif tax_amount == tax_variable and tax_variable != tax_value:
	# 				variable = {
	# 							'tax_id': tax_id,
	# 							'tx_name':str(tax_name),
	# 							'tax_rate':tax_rate,
	# 							'total_amount': same_categ_id_tax,
	# 							'stock_taxes_id':int(main_form_id)
	# 				}
	# 			elif tax_amount == tax_value and tax_variable != tax_value:
	# 				variable = {
	# 							'tax_id':tax_id,
	# 							'tx_name':str(tax_name),
	# 							'tax_rate':tax_rate,
	# 							'total_amount': different_categ_id_tax,
	# 							'stock_taxes_id':int(main_form_id)
	# 				}
	# 			tax_summary_report_obj_search = tax_summary_report_obj.search(cr,uid,[('stock_taxes_id','=',int(main_form_id)),('tax_id','=',tax_id)])
	# 			if not tax_summary_report_obj_search:
	# 				tax_summary_report_obj.create(cr,uid,variable)
	# 			if tax_summary_report_obj_search and tax_amount == tax_variable and tax_variable != tax_value and same_categ_id_tax != 0.0:
	# 				cr.execute('update delivery_tax_summary_report set total_amount=%s where tax_id=%s and stock_taxes_id=%s',(same_categ_id_tax,tax_id,main_form_id))
	# 			elif tax_summary_report_obj_search and tax_amount == tax_value and tax_variable != tax_value and different_categ_id_tax != 0.0:
	# 				cr.execute('update delivery_tax_summary_report set total_amount=%s where tax_id=%s and stock_taxes_id=%s',(different_categ_id_tax ,tax_id,main_form_id))
	# 			elif tax_summary_report_obj_search and tax_variable == tax_value and sum_tax_amount != 0.0:
	# 				cr.execute('update delivery_tax_summary_report set total_amount=%s where tax_id=%s and stock_taxes_id=%s',(sum_tax_amount ,tax_id,main_form_id))
	# 		tax_summary_report_obj_search_second = tax_summary_report_obj.search(cr,uid,[('tax_id','not in',append_value),('stock_taxes_id','=',int(main_form_id))])
	# 		if tax_summary_report_obj_search_second:
	# 			cr.execute('delete from delivery_tax_summary_report where id in %s',(tuple(tax_summary_report_obj_search_second),))
	# 		res[order.id]['amount_tax'] = sum_tax_amount
	# 		res[order.id]['amount_untaxed'] = val1 #cur_obj.round(cr, uid, cur, val1)
	# 		res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
	# 		total_after_discount = res[order.id]['amount_total'] * discount_value_id
	# 		if total_after_discount != 0.0 and apply_discount:
	# 			res[order.id]['grand_total'] = res[order.id]['amount_total'] - total_after_discount
	# 			roundoff_grand_total = res[order.id]['grand_total'] + 0.5
	# 			s = str(roundoff_grand_total)
	# 			dotStart = s.find('.')
	# 			res[order.id]['roundoff_grand_total'] = int(s[:dotStart])
	# 		else:
	# 			res[order.id]['grand_total'] = res[order.id]['amount_total']
	# 			roundoff_grand_total = res[order.id]['grand_total'] + 0.5
	# 			s = str(roundoff_grand_total)
	# 			dotStart = s.find('.')
	# 			res[order.id]['roundoff_grand_total'] = int(s[:dotStart])
	# 	return res

	_columns = {
		'shipping_person': fields.many2one('res.users','Shipping Person'),
		'date': fields.date('Dated', help="Creation date, usually the time of the order.", select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
		'po_date': fields.date("Buyer's PO Date"),
		'due_date': fields.date('Payment Due Date',help="Payment Due Date calculation done on the following condition :-\nIf the Customer is Interstate and agreed C-Form then Due Date=Order Date+Payment Term Days+5.\nIf the Customer is Interstate and Disagreed the C-Form or Within the State then Due Date=Order Date+Payment Term Days."),
		'destination': fields.char('Destination', size=128),
		'delivery_order_ref': fields.char("Buyer's PO Number", size=128),
		'dispatch_source': fields.many2one('dispatch.through','Dispatch Through'),
		'user_id': fields.many2one('res.users', 'Salesperson'),
		'payment_term': fields.many2one('account.payment.term','Payment Term'),
		#'financial_year': fields.function(_get_financial_year, type='selection',method=True,selection=SELECTION_LIST, string="Financial Year"),
		'stock_tax_lines': fields.one2many('delivery.tax.summary.report', 'stock_taxes_id', 'Tax summary', readonly=True),
		#############Shipping Address fields
		'shipping_street': fields.char('Shipping Street',size=128),
		'shipping_street2': fields.char('Shipping Street2',size=128),
		'shipping_city': fields.many2one('res.city','Shipping Cities'),
		'shipping_state_id': fields.many2one('res.country.state',' Shipping State'),
		'shipping_zip': fields.char('Shipping Zip',size=24),
		'shipping_country_id': fields.many2one('res.country','Shipping Country'),
		'shipping_destination': fields.char('Shipping Destination', size=128),
		'shipping_contact_person': fields.many2one('res.partner', 'Contact Person'),
		'shipping_contact_mobile_no': fields.char('Mobile Number',size=68),
		'shipping_contact_landline_no': fields.char('Landline Number',size=68),
		'shipping_email_id': fields.char('Email ID',size=68),
		##################Billing Address  fields
		'billing_street': fields.char('Billing Street',size=128),
		'billing_street2': fields.char('Billing Street2',size=128),
		'billing_city': fields.many2one('res.city','Billing Cities'),
		'billing_state_id': fields.many2one('res.country.state','Billing State'),
		'billing_zip': fields.char('Billing Zip',size=24),
		'billing_country_id': fields.many2one('res.country','Billing Country'),
		'billing_destination': fields.char('Billing Destination',size=128),
		'billing_contact_person': fields.many2one('res.partner', 'Contact Person'),
		'billing_contact_mobile_no': fields.char('Mobile Number',size=68),
		'billing_contact_landline_no': fields.char('Landline Number',size=68),
		'billing_email_id': fields.char('Email ID',size=68),
		#############################Total Amount
		'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',multi='sums', help="The amount without tax."),
		'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',multi='sums', help="The tax amount."),
		'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',multi='sums', help="The total amount."),
		'apply_discount': fields.boolean('Apply Discount'),
		'discount_value': fields.float('Discount (in%)'),
		'grand_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Grand Total',multi='sums'),
		'roundoff_grand_total': fields.function(_amount_all, string='Rounded off Amount', digits_compute=dp.get_precision('Account'), multi='sums'),
        'discounted_amount': fields.function(_amount_all, string='Discounted Amount', multi='sums'),		
        'amount_total_in_words': fields.function(_amount_in_words, string='Total amount in word', type='char', size=128),
		'total_shipped_quantity': fields.function(_total_shipped_quantity, string='Total Shipped Quantity', type='integer',digits_compute= dp.get_precision('Product UoS')),
		'total_billed_quantity': fields.function(_total_billed_quantity, string='Total Billed Quantity', type='integer',digits_compute= dp.get_precision('Product UoS')),
		'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', help="Pricelist for current sales order."),
		'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Currency"),
		'current_creation_date': fields.date('Creation Date'),
		'so_date': fields.date('SO Dated'),
		'state': fields.selection([
			('draft', 'Draft'),
			('invoiced','Invoiced'),
			('ready_to_dispatch','Ready to Dispatch'),
			('dispatched','Dispatched'),
			('delivered','Delivered'),
			('cancel', 'Cancelled'),
			('auto', 'Waiting Another Operation'),
			('confirmed', 'Waiting Availability'),
			('assigned', 'Ready to Transfer'),
			('done', 'Transferred'),
			], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
			* Draft: not confirmed yet and will not be scheduled until confirmed\n
			* Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
			* Waiting Availability: still waiting for the availability of products\n
			* Ready to Transfer: products reserved, simply waiting for confirmation.\n
			* Transferred: has been processed, can't be modified or cancelled anymore\n
			* Cancelled: has been cancelled, can't be confirmed anymore"""
		),
		'partial_picking': fields.boolean('Partial Picking'),
		'po_attachment': fields.binary('Attach PO'),
		'backorder_id': fields.many2one('stock.picking.out', 'Back Order of', domain="[('type','=','out')]", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="If this shipment was split, then this field links to the shipment which contains the already processed part.", select=True),
	}
	_defaults={
			'current_creation_date': fields.date.context_today,
			'shipping_person': _get_shipping_person,
	}

	def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context=None):
		context = context or {}
		if not pricelist_id:
			return {}
		value = {
			'currency_id': self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
		}
		if not order_lines:
			return {'value': value}
		warning = {
			'title': _('Pricelist Warning!'),
			'message' : _('If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
		}
		return {'warning': warning, 'value': value}

	def reminder_pending_delivery_order(self,cr,uid,context=None):
		today = datetime.today().date()
		rec_search = self.search(cr, uid, [('id', '>', 0),('state','=','draft')], context=None)
		for x in self.browse(cr,uid,rec_search):
			date_done = x.date_done
			s_id = x.id
			state = x.state
			if date_done:
				convert_date_done = datetime.strptime(date_done, "%Y-%m-%d %H:%M:%S").date()
				if convert_date_done == today:
					search_template_record = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','stock.picking.out'),('name','=','Pending Partial Delivery Order')], context=context)
					if search_template_record:
						self.pool.get('email.template').send_mail(cr, uid, search_template_record[0], s_id, force_send=True, context=context)
		return True

	def create(self, cr, uid, vals, context=None):
		res_id = super(stock_picking_out, self).create(cr, uid, vals, context)
		account_fiscalyear_obj = self.pool.get('account.fiscalyear')
		if isinstance(res_id, list):
			main_form_id = res_id[0]
		else:
			main_form_id = res_id
		if vals.has_key('name'):
			code_number = vals.get('name')
			todays_date = datetime.now().date()
			code_id_search = account_fiscalyear_obj.search(cr,uid,[('date_start','<=',todays_date),('date_stop','>=',todays_date)])
			fiscalyear_code = account_fiscalyear_obj.browse(cr,uid,code_id_search[0]).code
			code_number = code_number+'/'+fiscalyear_code
			self.write(cr,uid,main_form_id,{'name':code_number})
		if vals.has_key('move_lines'):
			if vals['move_lines']:
				combo_line_list_values = vals['move_lines']
				for combo_list_id in combo_line_list_values:
					combo_id = combo_list_id[2]
					if combo_id.has_key('product_qty') and combo_id.has_key('product_billed_qty'):
						shipped_quantity = combo_id.get('product_qty')
						billed_quantity = combo_id.get('product_billed_qty')
						if shipped_quantity < billed_quantity:
							raise osv.except_osv(_('Warning!'),_('Shipped Quantity must be greater than Billed Quantity.'))
		return res_id

	def write(self, cr, uid, ids, vals, context=None):
		res = super(stock_picking_out, self).write(cr, uid, ids, vals, context=context)
		if isinstance(ids, list):
			main_id = ids[0]
		else:
			main_id = ids
		stock_move_obj = self.pool.get('stock.move')
		if vals.has_key('move_lines'):
			search_line_id = stock_move_obj.search(cr,uid,[('picking_id','=',main_id)])
			search_line_browse= stock_move_obj.browse(cr,uid,search_line_id)
			for search_line_browse_id in search_line_browse:
				search_main_id = search_line_browse_id.id
				shipped_quantity = search_line_browse_id.product_qty
				billed_quantity = search_line_browse_id.product_billed_qty
				if shipped_quantity < billed_quantity:
					raise osv.except_osv(_('Warning!'),_('Shipped Quantity must be greater than Billed Quantity.'))
		return res

	def onchange_apply_discount(self,cr,uid,ids,apply_discount):
		v={}
		if apply_discount:
			pass
		elif not apply_discount:
			v['discount_value'] = 0.0
		return {'value':v}

	def onchange_billing_contact_person(self,cr,uid,ids,billing_contact_person):
		v={}
		res_partner_obj=self.pool.get('res.partner')
		if billing_contact_person:
			res_partner_browse = res_partner_obj.browse(cr,uid,billing_contact_person)
			v['billing_contact_mobile_no'] = res_partner_browse.mobile
			v['billing_contact_landline_no'] = res_partner_browse.phone
			v['billing_email_id'] = res_partner_browse.email
		return {'value':v}

	def onchange_shipping_contact_person(self,cr,uid,ids,shipping_contact_person):
		v={}
		res_partner_obj=self.pool.get('res.partner')
		if shipping_contact_person:
			res_partner_browse = res_partner_obj.browse(cr,uid,shipping_contact_person)
			v['shipping_contact_mobile_no'] = res_partner_browse.mobile
			v['shipping_contact_landline_no'] = res_partner_browse.phone
			v['shipping_email_id'] = res_partner_browse.email
		return {'value':v}

	def onchange_partner_in(self, cr, uid, ids, partner_id, context=None):
		val={}
		res_partner_obj = self.pool.get('res.partner')
		if partner_id:
			res_partner_obj_browse = res_partner_obj.browse(cr,uid,partner_id)
			billing_street = res_partner_obj_browse.street
			billing_street2 = res_partner_obj_browse.street2
			billing_destination = res_partner_obj_browse.billing_destination
			billing_city = res_partner_obj_browse.billing_city.id
			billing_state_id = res_partner_obj_browse.state_id.id
			billing_zip = res_partner_obj_browse.zip
			billing_country_id = res_partner_obj_browse.country_id.id
			shipping_street = res_partner_obj_browse.shipping_street
			shipping_street2 = res_partner_obj_browse.shipping_street2
			shipping_city = res_partner_obj_browse.shipping_city2.id
			shipping_state_id = res_partner_obj_browse.shipping_state_id.id
			shipping_zip = res_partner_obj_browse.shipping_zip
			shipping_country_id = res_partner_obj_browse.shipping_country_id.id
			shipping_destination = res_partner_obj_browse.shipping_destination
			payment_term = res_partner_obj_browse.property_payment_term.id
			user_id = res_partner_obj_browse.user_id.id
			val = {
				'billing_street': billing_street,
				'billing_street2': billing_street2,
				'billing_city': billing_city,
				'billing_state_id': billing_state_id,
				'billing_zip': billing_zip,
				'billing_country_id': billing_country_id,
				'billing_destination': billing_destination,
				'shipping_street': shipping_street,
				'shipping_street2': shipping_street2,
				'shipping_city': shipping_city,
				'shipping_state_id': shipping_state_id,
				'shipping_zip': shipping_zip,
				'shipping_country_id': shipping_country_id,
				'shipping_destination': shipping_destination,
				'payment_term': payment_term,
				'destination': shipping_destination,
				'user_id': user_id,
				}
		return {'value':val}

	def action_assign(self, cr, uid, ids, *args):
		""" Changes state of picking to available if all moves are confirmed.
		@return: True
		"""
		wf_service = netsvc.LocalService("workflow")
		for pick in self.browse(cr, uid, ids):
			main_form_id = pick.id
			if pick.state == 'draft':
				wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_confirm', cr)
			move_ids = [x.id for x in pick.move_lines if x.state == 'confirmed']
			if not move_ids:
				raise osv.except_osv(_('Warning!'),_('Not enough stock, unable to reserve the products.'))
			self.pool.get('stock.move').action_assign(cr, uid, move_ids)
			self.write(cr,uid,main_form_id,{'state':'assigned'})
		return True

	def force_assign(self, cr, uid, ids, *args):
		""" Changes state of picking to available if moves are confirmed or waiting.
		@return: True
		"""
		wf_service = netsvc.LocalService("workflow")
		for pick in self.browse(cr, uid, ids):
			main_form_id = pick.id
			move_ids = [x.id for x in pick.move_lines if x.state in ['confirmed','waiting']]
			self.pool.get('stock.move').force_assign(cr, uid, move_ids)
			wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
			self.write(cr,uid,main_form_id,{'state':'assigned'})
		return True


	# def create_account_invoice(self,cr,uid,ids,context=None):
	# 	result = []
	# 	line_order =[]
	# 	tax_line =[]
	# 	account_invoice_obj = self.pool.get('account.invoice')
	# 	account_invoice_line_obj = self.pool.get('account.invoice.line')
	# 	tax_line = self.pool.get('invoice.tax.summary.report')
	# 	product_product_obj = self.pool.get('product.product')
	# 	todays_date = datetime.now()
	# 	for order in self.browse(cr,uid,ids):
	# 			invoice_values = {
	# 							'origin': order.name,
	# 							'date': todays_date,
	# 							'type': 'out_invoice',
	# 							'state': 'draft',
	# 							'partner_id': order.partner_id.id,
	# 							'comment': order.note,
	# 							'company_id': order.company_id.id,
	# 							'po_date': order.po_date,
	# 							'date_due': order.due_date,
	# 							'client_order_ref': order.delivery_order_ref,
	# 							'dispatch_source': order.dispatch_source.id,
	# 							'user_id': order.user_id.id,
	# 							'payment_term': order.payment_term.id,
	# 							'delivery_note':order.name,
	# 							'suppliers_ref': order.origin,
	# 							'order_date': order.so_date,
	# 							#############Shipping Address fields
	# 							'shipping_street': order.shipping_street,
	# 							'shipping_street2': order.shipping_street2,
	# 							'shipping_city': order.shipping_city.id,
	# 							'shipping_state_id':order.shipping_state_id.id,
	# 							'shipping_zip':order.shipping_zip,
	# 							'shipping_country_id': order.shipping_country_id.id,
	# 							'shipping_destination': order.shipping_destination,
	# 							'shipping_contact_person': order.shipping_contact_person.id,
	# 							'shipping_contact_mobile_no': order.shipping_contact_mobile_no,
	# 							'shipping_contact_landline_no': order.shipping_contact_landline_no,
	# 							'shipping_email_id': order.shipping_email_id,
	# 							'destination': order.shipping_destination,
 # #                               ##################Billing Address  fields
	# 							'billing_street': order.billing_street,
	# 							'billing_street2': order.billing_street2,
	# 							'billing_city': order.billing_city.id,
	# 							'billing_state_id': order.billing_state_id.id,
	# 							'billing_zip': order.billing_zip,
	# 							'billing_country_id': order.billing_country_id.id,
	# 							'billing_destination': order.billing_destination,
	# 							'billing_contact_person': order.billing_contact_person.id,
	# 							'billing_contact_mobile_no': order.billing_contact_mobile_no,
	# 							'billing_contact_landline_no': order.billing_contact_landline_no,
	# 							'billing_email_id':order.billing_email_id,
	# 							'apply_discount': order.apply_discount,
	# 							'discount_value': order.discount_value,
	# 							'account_id':order.partner_id.property_account_receivable.id,
	# 	}
	# 	ir_model_data = self.pool.get('ir.model.data')
	# 	form_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
	# 	form_id = form_res and form_res[1] or False
	# 	tree_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
	# 	tree_id = tree_res and tree_res[1] or False
	# 	account_id =account_invoice_obj.create(cr,uid,invoice_values)
	# 	for line1 in order.stock_tax_lines:
	# 		tax_line_values = {
	# 								'tax_id':line1.tax_id,
	# 								'tx_name':line1.tx_name,
	# 								'total_amount':line1.total_amount,
	# 								'tax_rate':line1.tax_rate,
	# 								'stock_taxes_id':account_id
	# 		}
	# 		tax_line_values_create = tax_line.create(cr,uid,tax_line_values)
	# 	for line in order.move_lines:
	# 		product_id = line.product_id.id
	# 		product_product_browse = product_product_obj.browse(cr,uid,product_id).virtual_available
	# 		lines_account_id = product_product_obj.browse(cr,uid,product_id).categ_id.id
	# 		if product_product_browse < 0.00:
	# 			raise osv.except_osv(('Warning!!'),('The stock is not available.'))
	# 		account_line_values={
	# 							'name': line.name,
	# 							'product_id': line.product_id.id,
	# 							'quantity': line.product_qty,
	# 							'product_billed_qty': line.product_billed_qty,
	# 							'sale_warehouse_id':line.delivery_warehouse_id.id,
	# 							'tax_applied_id':line.tax_applied_id.id,
	# 							'product_category_id':line.product_category_id.id,
	# 							'sale_price':line.sale_price.id,
	# 							'partner_id': line.partner_id.id,
	# 							'company_id': order.company_id.id,
	# 							'price_unit': line.price_unit or 0.0,
	# 							'invoice_id':account_id,
	# 							'account_id': lines_account_id,
	# 		}
	# 		invoice_line_values_create = account_invoice_line_obj.create(cr,uid,account_line_values)
	# 		order.refresh()
	# 	return {
	# 				'name': _('Customer Invoices'),
	# 				'view_type': 'form',
	# 				'view_mode': 'form,tree',
	# 				'res_model': 'account.invoice',
	# 				'res_id': account_id,
	# 				'view_id': False,
	# 				'views': [(form_id, 'form'), (tree_id, 'tree')],
	# 				'context': "{'type': 'out_invoice'}",
	# 				'type': 'ir.actions.act_window',
	# 	}

stock_picking_out()

class stock_picking(osv.osv):
	_inherit="stock.picking"

	#
	# TODO: change and create a move if not parents
	#
	def action_done(self, cr, uid, ids, context=None):
		"""Changes picking state to done.
		
		This method is called at the end of the workflow by the activity "done".
		@return: True
		"""
		self.write(cr, uid, ids, {'state': 'draft'})
		return True


	def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
		""" Builds the dict containing the values for the invoice
			@param picking: picking object
			@param partner: object of the partner to invoice
			@param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
			@param journal_id: ID of the accounting journal
			@return: dict that will be used to create the invoice object
		"""
		if isinstance(partner, int):
			partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
		if inv_type in ('out_invoice', 'out_refund'):
			account_id = partner.property_account_receivable.id
			payment_term = partner.property_payment_term.id or False
		else:
			account_id = partner.property_account_payable.id
			payment_term = partner.property_supplier_payment_term.id or False
		comment = self._get_comment_invoice(cr, uid, picking)
		main_form_id = picking.id
		order = self.pool.get('stock.picking.out').browse(cr,uid,main_form_id)
		invoice_vals = {
			# 'name': '',
			'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
			'type': inv_type,
			'account_id': account_id,
			'partner_id': partner.id,
			'comment': comment,
			'payment_term': payment_term,
			'fiscal_position': partner.property_account_position.id,
			'date_invoice': context.get('date_inv', False),
			'company_id': picking.company_id.id,
			'user_id': uid,
			'client_order_ref': order.delivery_order_ref,
			'po_date': order.po_date,
			'delivery_note': order.name,
			'date_due': order.due_date,
			'suppliers_ref': order.origin,
			'order_date': order.so_date,
			'dispatch_source': order.dispatch_source.id,
			'destination': order.shipping_destination,
			###################Shipping Address Details
			'shipping_street': order.shipping_street,
			'shipping_street2': order.shipping_street2,
			'shipping_city': order.shipping_city.id,
			'shipping_state_id':order.shipping_state_id.id,
			'shipping_zip':order.shipping_zip,
			'shipping_country_id': order.shipping_country_id.id,
			'shipping_destination': order.shipping_destination,
			'shipping_contact_person': order.shipping_contact_person.id,
			'shipping_contact_mobile_no': order.shipping_contact_mobile_no,
			'shipping_contact_landline_no': order.shipping_contact_landline_no,
			'shipping_email_id': order.shipping_email_id,
			'destination': order.shipping_destination,
			##################Billing Address  fields
			'billing_street': order.billing_street,
			'billing_street2': order.billing_street2,
			'billing_city': order.billing_city.id,
			'billing_state_id': order.billing_state_id.id,
			'billing_zip': order.billing_zip,
			'billing_country_id': order.billing_country_id.id,
			'billing_destination': order.billing_destination,
			'billing_contact_person': order.billing_contact_person.id,
			'billing_contact_mobile_no': order.billing_contact_mobile_no,
			'billing_contact_landline_no': order.billing_contact_landline_no,
			'billing_email_id':order.billing_email_id,
			'po_attachment': order.po_attachment,
			'apply_discount': order.apply_discount,
            'discount_value': order.discount_value,
            'discounted_amount': order.discounted_amount,
		}
		cur_id = self.get_currency_id(cr, uid, picking)
		if cur_id:
			invoice_vals['currency_id'] = cur_id
		if journal_id:
			invoice_vals['journal_id'] = journal_id
		return invoice_vals

	def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,invoice_vals, context=None):
		""" Builds the dict containing the values for the invoice line
			@param group: True or False
			@param picking: picking object
			@param: move_line: move_line object
			@param: invoice_id: ID of the related invoice
			@param: invoice_vals: dict used to created the invoice
			@return: dict that will be used to create the invoice line
		"""
		if group:
			name = (picking.name or '') + '-' + move_line.name
		else:
			name = move_line.name
		origin = move_line.picking_id.name or ''
		if move_line.picking_id.origin:
			origin += ':' + move_line.picking_id.origin

		if invoice_vals['type'] in ('out_invoice', 'out_refund'):
			account_id = move_line.product_id.property_account_income.id
			if not account_id:
				account_id = move_line.product_id.categ_id.\
						property_account_income_categ.id
		else:
			account_id = move_line.product_id.property_account_expense.id
			if not account_id:
				account_id = move_line.product_id.categ_id.\
						property_account_expense_categ.id
		if invoice_vals['fiscal_position']:
			fp_obj = self.pool.get('account.fiscal.position')
			fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
			account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
		# set UoS if it's a sale and the picking doesn't have one
		uos_id = move_line.product_uos and move_line.product_uos.id or False
		if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
			uos_id = move_line.product_uom.id

		return {
			'name': name,
			'origin': origin,
			'invoice_id': invoice_id,
			'uos_id': uos_id,
			'product_id': move_line.product_id.id,
			'product_code': move_line.product_code,
			'product_category_id': move_line.product_category_id.id,
			'sale_price': move_line.sale_price.id,
			'tax_applied_id':move_line.tax_applied_id.id,
			'price_unit':move_line.price_unit,
			'account_id': account_id,
			# 'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
			'discount': self._get_discount_invoice(cr, uid, move_line),
			'quantity': move_line.product_uos_qty or move_line.product_qty,
			'product_billed_qty': move_line.product_billed_qty,
			'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
			'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
		}


	def action_invoice_create(self, cr, uid, ids, journal_id=False,
			group=False, type='out_invoice', context=None):
		""" Creates invoice based on the invoice state selected for picking.
		@param journal_id: Id of journal
		@param group: Whether to create a group invoice or not
		@param type: Type invoice to be created
		@return: Ids of created invoices for the pickings
		"""
		if context is None:
			context = {}

		invoice_obj = self.pool.get('account.invoice')
		invoice_line_obj = self.pool.get('account.invoice.line')
		partner_obj = self.pool.get('res.partner')
		invoices_group = {}
		res = {}
		inv_type = type
		for picking in self.browse(cr, uid, ids, context=context):
			if picking.invoice_state != '2binvoiced':
				continue
			partner = self._get_partner_to_invoice(cr, uid, picking, context=context)
			if isinstance(partner, int):
				partner = partner_obj.browse(cr, uid, [partner], context=context)[0]
			if not partner:
				raise osv.except_osv(_('Error, no partner!'),
					_('Please put a partner on the picking list if you want to generate invoice.'))

			if not inv_type:
				inv_type = self._get_invoice_type(picking)

			if group and partner.id in invoices_group:
				invoice_id = invoices_group[partner.id]
				invoice = invoice_obj.browse(cr, uid, invoice_id)
				invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
				invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
			else:
				invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
				invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
				invoices_group[partner.id] = invoice_id
			res[picking.id] = invoice_id
			for move_line in picking.move_lines:
				if move_line.state == 'cancel':
					continue
				if move_line.scrapped:
					# do no invoice scrapped products
					continue
				vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
								invoice_id, invoice_vals, context=context)
				if vals:
					print "vvvvvvvvvvvvvvv",vals
					invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
					self._invoice_line_hook(cr, uid, move_line, invoice_line_id)

			invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
					set_total=(inv_type in ('in_invoice', 'in_refund')))
			self.write(cr, uid, [picking.id], {
				'invoice_state': 'invoiced',
				}, context=context)
			self._invoice_hook(cr, uid, picking, invoice_id)
		self.write(cr, uid, res.keys(), {
			'invoice_state': 'invoiced',
			}, context=context)
		self.pool.get('stock.picking.out').write(cr, uid, res.keys(), {
			'state': 'invoiced',
			}, context=context)
		return res

	# FIXME: needs refactoring, this code is partially duplicated in stock_move.do_partial()!
	def do_partial(self, cr, uid, ids, partial_datas, context=None):
		if context is None:
			context = {}
		else:
			context = dict(context)
		res = {}
		append_letters =[]
		empty_string =''
		move_obj = self.pool.get('stock.move')
		uom_obj = self.pool.get('product.uom')
		sequence_obj = self.pool.get('ir.sequence')
		wf_service = netsvc.LocalService("workflow")
		partial_date = partial_datas.get('partial_date')
		partial_picking = partial_datas.get('partial_picking')
		for pick in self.browse(cr, uid, ids, context=context):
			pick1 = self.pool.get('stock.picking.out').browse(cr,uid,ids[0])
			main_form_id = pick1.id
			values = {
				'billing_street': pick1.billing_street,
				'billing_street2': pick1.billing_street2,
				'billing_city': pick1.billing_city.id,
				'billing_state_id': pick1.billing_state_id.id,
				'billing_zip': pick1.billing_zip,
				'billing_country_id': pick1.billing_country_id.id,
				'billing_destination': pick1.billing_destination,
				'shipping_street': pick1.shipping_street,
				'shipping_street2': pick1.shipping_street2,
				'shipping_city': pick1.shipping_city.id,
				'shipping_state_id': pick1.shipping_state_id.id,
				'shipping_zip': pick1.shipping_zip,
				'shipping_country_id': pick1.shipping_country_id.id,
				'shipping_destination': pick1.shipping_destination,
				'payment_term': pick1.payment_term.id,
				'destination': pick1.shipping_destination,
				'user_id': pick1.user_id.id,
				'billing_contact_mobile_no': pick1.billing_contact_mobile_no,
				'billing_contact_landline_no': pick1.billing_contact_landline_no,
				'billing_email_id': pick1.billing_email_id,
				'billing_contact_person': pick1.billing_contact_person.id,
				'shipping_contact_person': pick1.shipping_contact_person.id,
				'shipping_contact_mobile_no': pick1.shipping_contact_mobile_no,
				'shipping_contact_landline_no': pick1.billing_contact_landline_no,
				'shipping_email_id': pick1.shipping_email_id,
				'delivery_order_ref':pick1.delivery_order_ref,
				'apply_discount': pick1.apply_discount,
				'discount_value': pick1.discount_value,
				'discounted_amount': pick1.discounted_amount,
				'po_date':pick1.po_date,
				'date':pick1.date,
				'dispatch_source':pick1.dispatch_source.id,
				'due_date':pick1.due_date,
				'user_id':pick1.user_id.id,
				'so_date':pick1.so_date,
				'date_done':pick1.date_done,
				'partial_picking':partial_picking,
				'current_creation_date': datetime.today().date(),
			}
			new_picking = None
			complete, too_many, too_few, sequence_id_append = [], [], [], []
			move_product_qty, prodlot_ids, product_avail, partial_qty, uos_qty, product_uoms = {}, {}, {}, {}, {}, {}
			for move in pick.move_lines:
				if move.state in ('done', 'cancel'):
					continue
				partial_data = partial_datas.get('move%s'%(move.id), {})
				product_qty = partial_data.get('product_qty',0.0)
				move_product_qty[move.id] = product_qty
				product_billed_qty = partial_data.get('product_billed_qty',0.0)
				product_uom = partial_data.get('product_uom', move.product_uom.id)
				product_price = partial_data.get('product_price',0.0)
				product_currency = partial_data.get('product_currency',False)
				prodlot_id = partial_data.get('prodlot_id')
				prodlot_ids[move.id] = prodlot_id
				product_uoms[move.id] = product_uom
				partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
				# uos_qty[move.id] = move.product_id._compute_uos_qty(product_uom, product_qty, move.product_uos) if product_qty else 0.0
				if move.product_qty == partial_qty[move.id]:
					complete.append(move)
				elif move.product_qty > partial_qty[move.id]:
					too_few.append(move)
				else:
					too_many.append(move)

				if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
					# Record the values that were chosen in the wizard, so they can be
					# used for average price computation and inventory valuation
					move_obj.write(cr, uid, [move.id],
							{'price_unit': product_price,
							 'price_currency_id': product_currency})

			# every line of the picking is empty, do not generate anything
			empty_picking = not any(q for q in move_product_qty.values() if q > 0)

			for move in too_few:
				product_qty = move_product_qty[move.id]
				product_billed_qty_edited = move.product_billed_qty
				if not new_picking and not empty_picking:
					letters = list(string.ascii_uppercase)
					sequence_name = pick.name
					sequence_name_split_variable= sequence_name.split('(') 
					if len(sequence_name_split_variable) == 2:
						sequence_name_split = sequence_name_split_variable[1].split(')')
					else:
						sequence_name_split = sequence_name_split_variable
					for sequence_letters in sequence_name_split:
						if sequence_letters in letters:
							sequence_letters_index = letters.index(sequence_letters)
							sequence_letters_index_add =sequence_letters_index+1
							delete_letters = letters[0:sequence_letters_index_add]
							for delete_letters_id in delete_letters:
								if delete_letters_id in letters:
									pop_delete_letters = letters.remove(delete_letters_id)
							next_letter = letters[0]
							previous_letters = delete_letters[-1]
							sequence_name_split_variable = sequence_name.split('(')
							if len(sequence_name_split_variable) == 2:
								sequence_name_split_second = sequence_name_split_variable[1].split(')')
							remove_last_letter = sequence_name_split_second.remove(sequence_name_split_second[0])
							join_letters= sequence_name_split_variable[0]
							new_picking_name = join_letters+'('+ previous_letters +')'
							same_sequence_name = join_letters+'('+next_letter+')'
						elif sequence_letters not in letters and sequence_letters != empty_string:
							sequence_letters_index_zero = letters[0]
							sequence_letters_index_one = letters[1]
							new_picking_name = pick.name+ '('+ sequence_letters_index_zero +')'
							same_sequence_name = pick.name+'('+sequence_letters_index_one +')'
					self.write(cr, uid, [pick.id], 
							   {'name': same_sequence_name,'date_done' : partial_date
							   })
					pick.refresh()
					new_picking = self.copy(cr, uid, pick.id,
							{
								'name': new_picking_name,
								'move_lines' : [],
								'state':'draft',
							})
				if product_qty != 0:
					partial_data = partial_datas.get('move%s'%(move.id), {})
					wizard_line_billed_qty = partial_data.get('product_billed_qty')
					main_product_billed_qty = product_billed_qty_edited - wizard_line_billed_qty
					defaults = {
							'product_qty' : product_qty,
							'product_billed_qty':wizard_line_billed_qty,
							# 'product_uos_qty': uos_qty[move.id],
							'picking_id' : new_picking,
							'state': 'assigned',
							'move_dest_id': False,
							'price_unit': move.price_unit,
							'product_uom': product_uoms[move.id]
					}
					move_obj.write(cr,uid,move.id,{'product_billed_qty':main_product_billed_qty})
					prodlot_id = prodlot_ids[move.id]
					if prodlot_id:
						defaults.update(prodlot_id=prodlot_id)
					move_obj.copy(cr, uid, move.id, defaults)
				move_obj.write(cr, uid, [move.id],
						{
							'product_qty': move.product_qty - partial_qty[move.id],
							# 'product_uos_qty': move.product_uos_qty - uos_qty[move.id],
							'prodlot_id': False,
							'tracking_id': False,
						})

			if new_picking:
				move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
			for move in complete:
				defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
				if prodlot_ids.get(move.id):
					defaults.update({'prodlot_id': prodlot_ids[move.id]})
				move_obj.write(cr, uid, [move.id], defaults)
			for move in too_many:
				product_qty = move_product_qty[move.id]
				defaults = {
					'product_qty' : product_qty,
					# 'product_uos_qty': uos_qty[move.id],
					'product_uom': product_uoms[move.id]
				}
				prodlot_id = prodlot_ids.get(move.id)
				if prodlot_ids.get(move.id):
					defaults.update(prodlot_id=prodlot_id)
				if new_picking:
					defaults.update(picking_id=new_picking)
				move_obj.write(cr, uid, [move.id], defaults)
			# At first we confirm the new picking (if necessary)
			if new_picking:
				wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
				# Then we finish the good picking
				self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
				self.pool.get('stock.picking.out').write(cr,uid, [new_picking], values)
				self.action_move(cr, uid, [new_picking], context=context)
				wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
				wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
				delivered_pack_id = new_picking
				self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (pick.name), context=context)
			elif empty_picking:
				delivered_pack_id = pick.id
			else:
				self.action_move(cr, uid, [pick.id], context=context)
				wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
				delivered_pack_id = pick.id
			self.pool.get('stock.picking.out').write(cr,uid,main_form_id,{'partial_picking':partial_picking})
			delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
			res[pick.id] = {'delivered_picking': delivered_pack.id or False}
		return res

stock_picking()

class stock_move(osv.osv):
	_inherit= "stock.move"

	def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			price = line.price_unit
			product_billed_qty = line.product_billed_qty
			total = price * product_billed_qty
			# taxes = tax_obj.compute_all(cr, uid, line.tax_applied_id, price, line.product_billed_qty, line.product_id, line.picking_id.partner_id)
			# cur = line.order_id.pricelist_id.currency_id
			res[line.id] = total
		return res

	_columns={
		'product_qty': fields.float('Shipped Quantity', digits_compute=dp.get_precision('Quantity'),
			required=True,states={'done': [('readonly', True)]},
			help="This is the quantity of products from an inventory "
				"point of view. For moves in the state 'done', this is the "
				"quantity of products that were actually moved. For other "
				"moves, this is the quantity of product that is planned to "
				"be moved. Lowering this quantity does not generate a "
				"backorder. Changing this quantity on assigned moves affects "
				"the product reservation, and should be done with care."
		),
		'product_billed_qty': fields.float('Billed Quantity',digits_compute=dp.get_precision('Quantity'),required=True,states={'done': [('readonly', True)]}),
		'delivery_warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
		'product_code': fields.char('Item Code', size=264),
		'sale_price': fields.many2one('product.customer.saleprice','Unit Price'),
		'price_unit': fields.float('Unit Price'),
		'tax_applied_id': fields.many2one('account.tax','Tax'),
		'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
		'product_category_id': fields.many2one('product.category','Product Category'),
	}

	def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,loc_dest_id=False, partner_id=False):
		if not prod_id:
			return {}
		user = self.pool.get('res.users').browse(cr, uid, uid)
		product_obj = self.pool.get('product.product')
		lang = user and user.lang or False
		warehouse_id = False
		tax_value=False
		if partner_id:
			addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
			if addr_rec:
				lang = addr_rec and addr_rec.lang or False
		ctx = {'lang': lang}
		product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
		uos_id  = product.uos_id and product.uos_id.id or False
		product_category_id = product.categ_id.id
		if partner_id:
			warehouse_id = self.pool.get('res.partner').browse(cr,uid,partner_id).warehouse_id.id
			type_of_sales = self.pool.get('res.partner').browse(cr, uid, partner_id).type_of_sales
			cform_criteria = self.pool.get('res.partner').browse(cr, uid, partner_id).cform_criteria
			if type_of_sales == 'interstate' and cform_criteria == 'agreed':
				tax_value =  product.categ_id.sale_with_cform.id
			if type_of_sales == 'interstate' and cform_criteria == 'disagreed' or type_of_sales == 'within_state':
				tax_value =  product.categ_id.sale_without_cform.id
		result = {
			'name': product.partner_ref,
			'product_uom': product.uom_id.id,
			'product_uos': uos_id,
			'product_qty': 1.00,
			'product_billed_qty': 1.00,
			'delivery_warehouse_id': warehouse_id,
			'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
			'prodlot_id' : False,
			'tax_applied_id': tax_value,
			'product_category_id':product_category_id,
		}
		if loc_id:
			result['location_id'] = loc_id
		if loc_dest_id:
			result['location_dest_id'] = loc_dest_id
		return {'value': result}

	def onchange_sale_price(self,cr,uid,ids,sale_price):
		result={}
		product_customer_saleprice_obj = self.pool.get('product.customer.saleprice')
		if sale_price:
			sale_price_search = product_customer_saleprice_obj.browse(cr,uid,sale_price).sales_price
			if sale_price_search:
				result.update({'price_unit': sale_price_search})
		return {'value':result}

	def action_done(self, cr, uid, ids, context=None):
		picking_ids = []
		move_ids = []
		wf_service = netsvc.LocalService("workflow")
		if context is None:
			context = {}

		todo = []
		for move in self.browse(cr, uid, ids, context=context):
			if move.state=="draft":
				todo.append(move.id)
		if todo:
			self.action_confirm(cr, uid, todo, context=context)
			todo = []

		for move in self.browse(cr, uid, ids, context=context):
			if move.state in ['done','cancel']:
				continue
			move_ids.append(move.id)

			if move.picking_id:
				picking_ids.append(move.picking_id.id)
			if move.move_dest_id.id and (move.state != 'done'):
				# Downstream move should only be triggered if this move is the last pending upstream move
				other_upstream_move_ids = self.search(cr, uid, [('id','not in',move_ids),('state','not in',['done','cancel']),
											('move_dest_id','=',move.move_dest_id.id)], context=context)
				if not other_upstream_move_ids:
					self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
					if move.move_dest_id.state in ('waiting', 'confirmed'):
						self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
						if move.move_dest_id.picking_id:
							wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
						if move.move_dest_id.auto_validate:
							self.action_done(cr, uid, [move.move_dest_id.id], context=context)

			# self._update_average_price(cr, uid, move, context=context)
			self._create_product_valuation_moves(cr, uid, move, context=context)
			if move.state not in ('confirmed','done','assigned'):
				todo.append(move.id)

		if todo:
			self.action_confirm(cr, uid, todo, context=context)

		self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
		for id in move_ids:
			 wf_service.trg_trigger(uid, 'stock.move', id, cr)

		for pick_id in picking_ids:
		   #wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
		   self.pool.get('stock.picking').write(cr,uid,pick_id,{'state':'draft'})
		return True


stock_move()

class delivery_tax_summary_report(osv.osv):
	_name = "delivery.tax.summary.report"   
	_columns = {
		'tax_id': fields.integer('Tax_ID'),
		'tx_name': fields.char('Tax Name'),
		'total_amount': fields.float('Total Amount', size=128, required=True),
		'tax_rate': fields.float('Tax Rate(in %)'),
		'stock_taxes_id': fields.many2one('stock.picking.out', 'Tax lines', ondelete='cascade', select=True),
   
	}

delivery_tax_summary_report()


class stock_invoice_onshipping(osv.osv_memory):
	_inherit = "stock.invoice.onshipping"
	_name = "stock.invoice.onshipping"

	_columns = {
        'invoice_date': fields.date('Invoiced date', required=True),
    }

	_defaults = {
        'invoice_date': fields.date.context_today
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
