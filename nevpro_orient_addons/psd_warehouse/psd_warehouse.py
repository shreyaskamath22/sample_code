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
import datetime as dt
import datetime 
import calendar
import re
from datetime import date,datetime, timedelta
from base.res import res_company as COMPANY
from base.res import res_partner
from collections import Counter
import xmlrpclib
import math
import os


class stock_transfer(osv.osv):
	_inherit = "stock.transfer"

	# def _compute_total_value(self, cr, uid, ids, field_name, arg, context=None):
	# 	result={}
	# 	subtotal =0
	# 	total=0     
	# 	stock_transfer_obj = self.pool.get('stock.transfer')
	# 	stock_transfer_line_obj = self.pool.get('product.transfer')
	# 	for records_stock in stock_transfer_obj.browse(cr, uid, ids):
	# 		for records_stock_lines in records_stock.stock_transfer_product:
	# 			total += records_stock_lines.amount
	# 		result[records_stock.id] = total
	# 	return result

	def _compute_total_value(self, cr, uid, ids, field_name, arg, context=None):
		result={}
		subtotal =0
		total=0     
		stock_transfer_obj = self.pool.get('stock.transfer')
		stock_transfer_line_obj = self.pool.get('product.transfer')
		for records_stock in stock_transfer_obj.browse(cr, uid, ids):
			for records_stock_lines in records_stock.stock_transfer_product:
				print records_stock_lines
				# subtotal = records_stock_lines.rate * records_stock_lines.quantity
				subtotal = records_stock_lines.tot_amount
				total += subtotal
				total = round(total)
			result[records_stock.id] = total
		return result

	def onchange_supplier(self, cr,uid, ids, supplier):
		val = {}
		if supplier:
			src = self.pool.get('res.partner').search(cr,uid,[('id','=',supplier)])
			for files in self.pool.get('res.partner').browse(cr,uid,src):
				apt = files.apartment
				building = files.building
				street = files.street
				area = files.sub_area
				landmark=files.landmark
				city = files.city_id.name1
				zip = files.zip
				phone=files.phone
				mobile=files.mobile
				email=files.email
				address=[apt,building,street,area,landmark,city,zip,phone,mobile,email]
				addr=', '.join(filter(bool,address))
				print "-----------------",addr
				val['supplier_address'] = addr
			return {'value':val}

	def onchange_branch_name(self,cr,uid,ids,branch_name):
		v={}
		prod_list = []
		active_obj = self.browse(cr,uid,ids[0])
		company_id = self.pool.get('res.company').browse(cr,uid,branch_name)
		if company_id.name == 'NSD Bhiwandi':
			v.update(is_nsd_bhiwandi= True)
		else:
			v.update(is_nsd_bhiwandi= False)
		for prod_line in active_obj.stock_transfer_product:
			prod_list.append((1,prod_line.id,{'godown':branch_name}))
		v.update(stock_transfer_product = prod_list)
		return {'value':v}

	_columns={
		'origin': fields.char('Indent Number', size=20),
		'psd_order_management': fields.boolean('Order Management'),
		'batch_edit':fields.boolean(''),
		'packlist_no1':fields.char('Packlist No.', size=100),
		'customer_name':fields.char('Customer Name',size=100),
		'freight_amount':fields.float('Freight Amount'),
		'create_bool':fields.boolean('No sync'),
		'stock_id': fields.char('Stock ID',size=10),
		'with_rate' : fields.boolean('With Rate'),
		'customer_cst_no':fields.char('Customer CST NO',size=34),
		'packlist_date1':fields.char('Packlist Date', size=100),
		'invoice_remark':fields.text('Invoice Remarks',size=2048),
		'stock_transfer_product1': fields.one2many('product.transfer','prod_id','Product Details'),
		'customer_vat_tin':fields.char('Customer Vat/Tin ',size=34),
		'invoice_no': fields.char('Invoice No',size=200),
		'company_address':fields.char('Addr',size=124),
		'state': fields.selection([
						('draft','View Order'),
						('assigned','Packlist/Transport'),
						('confirmed','Ready To Dispatch'),
						('invoiced','Invoiced'),
						('delivered','Delivered'),
						('progress','In Transit'),
						('cancel','Cancelled'),
						('done','Done')
						], 'Status', readonly=True),
		#############Inherited from the stock_transfer file
		'add_debit':fields.float('ADD DEBIT NOTE'),
		'less_credit':fields.float('LESS CREDIT NOTE'),
		'rounding':fields.float('Rounding'),
		'dis_total':fields.float("Distribute Total"),
		'export_total':fields.float("Export Total"),
		'total_tax':fields.float("Tax Total"),
		'grt_tax':fields.char("Greater tax",size=32),
		'total_unadjastable':fields.float("Total UnAdj. Amount"),
		'rounding_selection':fields.selection([('add', '+'), ('substract', '-')], 'Select'),
		'delivery_type': fields.selection([('sales_delivery', 'Sales Delivery'),('export_delivery', 'Export Delivery'),('internal_delivery', 'Internal Delivery'),('external_delivery', 'External Delivery'),('direct_sales','Direct Sales'),('free_sample_delivery','Free Sample Delivery'),('calibration','Calibration'),('banned_st','Branch Stock Transfer'),('excess_st','Excess Stock Transfer'),('inter_branch_st','Inter branch Stock Transfer')],'Delivery Type',required=True),
		'sale_order_no':fields.char('Order Number',size=60),
		'sale_order_date':fields.datetime('Order Date'),
		'transfer_series_ids':fields.one2many('transfer.series','serial_line_id',string="Serial No."),
		####Additional field added according to screenshot
		'invisible_create_indent': fields.boolean('Invisible Create Indent'),
		'psd_contact_person': fields.char('Contact Person',size=100),
		'web_order_number': fields.char('Web Order Number',size=100),
		'web_order_date': fields.date('Web Order Date'),
		'pse': fields.many2one('hr.employee','PSE'),
		'billing_location': fields.text('Billing Location',size=200),
		'against_free_replacement': fields.boolean('Against Free Replacement'),
		'delivered_by': fields.many2one('res.company', 'Delivered By'),
		'expected_delivery_date': fields.datetime('Expected Delivery Date'),
		'against_form':fields.selection([("against_form_c","Against Form 'C'"),("against_form_h","Against Form 'H'")],'Against Form'),
		'partner_id': fields.many2one('res.partner','Partner ID'),
		'billing_location_id':fields.many2one('res.partner.address','Partner ID'),
		############################################
		'is_received':fields.boolean('Received'),
		'reference_id':fields.char('Form Reference ID',size=40),
		'total_amount':fields.function(_compute_total_value, type='float', obj='stock.transfer', method=True, store=True, string='Total Amount'),
		# 'total_amount':fields.float('Total Amount'),
		'is_track_equipment':fields.boolean('IS Track Equipment'),
		'is_road_permit':fields.boolean('IS Road Permit'),
		'is_nsd_bhiwandi':fields.boolean('IS NSD Bhiwandi'),
		'delivered_ref_id':fields.char('Delivered Ref ID',size=56),
		'delivered_ref_date':fields.date('Delivered Ref Date'),
		'psd_indent_number': fields.char('Indent Number',size=100),
		'psd_indent_date': fields.date('Indent Date'),
		'po_no':fields.char('Purchase Order No',size=100),
		'po_date':fields.date('Purchase Order Date'),
		'basic_charge':fields.float('Basic Charge'),
		'order_total_vat':fields.float('Total VAT'),
		'product_cost':fields.float('Product Cost'),
		'total_vat':fields.float('Total VAT/CST'),
		'bird_pro':fields.boolean('Bird Pro'),
		'bird_pro_charge':fields.float('Bird Pro Installation Charges'),
		'total_st':fields.float('Bird Pro Service Tax'),
		'tax_one2many':fields.one2many('tax','stock_transfer_tax_id','Tax'),
		'delivery_loc_state':fields.char('Delivery Location State',size=100),
		'delivery_mechanism':fields.selection([('supplier_delivery', 'Direct from Supplier'),('pci_delivery', 'PCI Delivery'),('courier', 'PCI through Courier')],'Delivery Mechanism'),
		'supplier':fields.many2one('res.partner','Supplier'),
		'supplier_challan_no':fields.char('Supplier Challan No.',size=100),
		'supplier_address':fields.text('Supplier Address',size=150),
		'docket_no':fields.char('Docket No.',size=100),
		#'update_delivery_id':fields.many2one('update.delivery',string="Update Delivery ID"),
		############################################
	}
	_defaults = {
			'rounding_selection':'add',
		}

	##### CEATE INVOICE ###########################################
	def psd_create_invoice(self,cr,uid,ids,context=None):
		tax_line_obj = self.pool.get('invoice.tax.rate')
		account_tax_obj = self.pool.get('account.tax')
		invoice_obj = self.pool.get('invoice.adhoc.master')
		invoice_line_obj = self.pool.get('invoice.adhoc')
		psd_sales_product_order_obj = self.pool.get('psd.sales.product.order')
		delivery_obj = self.browse(cr,uid,ids[0])
		bird_pro_flag = False
		product_invoice_flag = False
		if delivery_obj.bird_pro:
			bird_pro_flag = True
			product_invoice_flag = False
		else:
			bird_pro_flag = False
			product_invoice_flag = True
		total_vat = 0.0
		total_basic_rate=0.0
		fr_tax_amount = 0.0
		total_amount = 0.0
		tax_list = []
		tax_line_values = {}
		for calc in delivery_obj.stock_transfer_product:
			total_vat = total_vat + calc.tax_amount
			total_basic_rate = total_basic_rate + calc.rate
			#######################calculation for the due date in the serial tab from the Sync GRN Indent tab
			product_name = calc.product_name.id
			product_obj = self.pool.get('product.product').browse(cr,uid,product_name)
			product_warranty = product_obj.warranty_life
			for transfer_series_id in delivery_obj.transfer_series_ids:
				main_id  = transfer_series_id.id
				delivery_challan_date = transfer_series_id.from_date
				total_warranty = int(product_warranty) + int(calc.extended_warranty)
				no_of_months = relativedelta(months=total_warranty)
				string_datetime_conversion = datetime.strptime(delivery_challan_date, "%Y-%m-%d %H:%M:%S")
				string_datetime_conversion_date = string_datetime_conversion.date()
				to_date = string_datetime_conversion_date + no_of_months + relativedelta(days=-1)
				self.pool.get('transfer.series').write(cr,uid,main_id,{'due_date':to_date,'duration':total_warranty})
			####################################################
		prod_order_no = delivery_obj.sale_order_no
		if prod_order_no:
			prod_order_rec_id = psd_sales_product_order_obj.search(cr,uid,[('erp_order_no','=', prod_order_no)])
			if prod_order_rec_id:
				for res in psd_sales_product_order_obj.browse(cr,uid,prod_order_rec_id):
					subtotal = res.subtotal
					product_discount = res.product_discount
					product_discount_amount = res.product_discount_amount
					prod_order_grand_total = res.total_amount_paid



		order_data={'cust_name':delivery_obj.customer_name,
					'status':'open',
					'erp_order_no':delivery_obj.sale_order_no,
					'web_order_no':delivery_obj.web_order_number,
					'pse':delivery_obj.pse.id,
					'against_form':delivery_obj.against_form,
					'expected_delivery_date':delivery_obj.expected_delivery_date,
					'erp_order_date':delivery_obj.sale_order_date,
					'web_order_date':delivery_obj.web_order_date,
					'delivered_by':delivery_obj.branch_name.name,
					'billing_location':delivery_obj.billing_location,
					'pse':delivery_obj.pse.id,
					'delivery_order_no':delivery_obj.stock_transfer_no,
					'customer_id':delivery_obj.partner_id.id,
					'delivery_address':delivery_obj.delivery_address,
					'billing_location_id':delivery_obj.billing_location_id.id,
					'against_form':delivery_obj.against_form,
					'invoice_period_to':date.today(),
					'invoice_period_from':date.today(),
					'partner_id':delivery_obj.partner_id.id,
					'delivery_note_date':delivery_obj.delivery_challan_date,
					'delivery_note_no':delivery_obj.delivery_challan_no,
					'invoice_due_date':date.today(),
					'is_product_invoice':product_invoice_flag,
					'total_weight':delivery_obj.total_weight,
					'estimated_value':delivery_obj.estimated_value,
					'mode_transport':delivery_obj.mode_transport,
					'person_name':delivery_obj.person_name,
					'transporter':delivery_obj.transporter.id,
					'vehicle_no':delivery_obj.vehicle_no,
					'driver_name':delivery_obj.driver_name,
					'mobile_no':delivery_obj.mobile_no,
					'lr_no':delivery_obj.lr_no,
					'lr_date':delivery_obj.lr_date,
					'delivery_date':delivery_obj.delivery_date,
					'freight_amount':delivery_obj.freight_amount,
					'freight_amount_invoice':delivery_obj.freight_amount,
					'po_ref':delivery_obj.po_no,
					'po_ref_date':delivery_obj.po_date,
					'basic_charge':delivery_obj.product_cost,
					# 'order_total_vat':delivery_obj.total_vat,
					'bird_pro':bird_pro_flag,
					'bird_pro_charge':delivery_obj.bird_pro_charge,
					'total_st':delivery_obj.total_st,
					'invoice_type':'product_invoice',
					'subtotal':subtotal if subtotal else 0.0,
					'product_discount':product_discount if product_discount else 0.0,
					'product_discount_amount':product_discount_amount if product_discount_amount else 0.0,
					# 'product_order_grand_total':delivery_obj.total_amount,
					}
		new_invoice_id = invoice_obj.create(cr,uid,order_data,context=context)
		for serial_line_id in delivery_obj.transfer_series_ids:
			self.pool.get('transfer.series').write(cr,uid,serial_line_id.id,{'invoice_id':int(new_invoice_id)})
		for line_id in delivery_obj.stock_transfer_product:
			if line_id.state != 'cancel_order_qty':
				print line_id.sgst_amount,line_id.gst_amount,line_id.amount
				# vv
				line_values ={
				'invoice_type':'product_invoice',
				'product_invoice_id':int(new_invoice_id),
				'product_id': line_id.product_name.id,
				'ordered_quantity':line_id.quantity,
				'product_uom': line_id.product_uom.id,
				'exp_date':line_id.exp_date,
				'batch': line_id.batch.id,
				'rate': line_id.rate,
				'sgst_amt':line_id.sgst_amount,
				'cgst_amt':line_id.cgst_amount,
				'igst_amt':line_id.igst_amount,
				'sgst_rate':line_id.sgst_rate,
				'cgst_rate':line_id.cgst_rate,
				'igst_rate':line_id.igst_rate,
				# 'total_tax':line_id.gst_amount,
				'total':line_id.amount,
				'serial_number': line_id.serial_number,
				'is_track_equipment': line_id.is_track_equipment,
				'specification':line_id.specification,
				'discount':line_id.additional_amt,
				}
				res_sale_order_line_create= self.pool.get('invoice.adhoc').create(cr,uid,line_values)
				cr.commit()
				
				cr.execute('select sum(sgst_amount) from product_transfer where prod_id = %s',(line_id.prod_id.id,))
				sgst_amount = cr.fetchone()[0]
				cr.execute('select sum(cgst_amount) from product_transfer where prod_id = %s',(line_id.prod_id.id,))
				cgst_amount = cr.fetchone()[0]
				cr.execute('select sum(igst_amount) from product_transfer where prod_id = %s',(line_id.prod_id.id,))
				igst_amount = cr.fetchone()[0]
				cr.execute('select sum(amount) from product_transfer where prod_id = %s',(line_id.prod_id.id,))
				amount = cr.fetchone()[0]
				total_amount = round(amount)
				print sgst_amount,cgst_amount,igst_amount,'========='
				gst_total = 0.0
				gst_total = sgst_amount + cgst_amount + igst_amount
				print gst_total
				# bb
				
				invoice_obj.write(cr,uid,new_invoice_id,{'total_tax':gst_total,'basic_charge':total_amount})
				cr.commit()

		for note in delivery_obj.notes_one2many:
			note_lines = {
			'user_name':note.user_name,
			'comment_date':note.date,
			'comment':note.name,
			'invoice_line_id':new_invoice_id,
			}
			res_invoice_notes_create = self.pool.get('comment.line').create(cr,uid,note_lines)
		if delivery_obj.tax_one2many:
			for tax_line_id in delivery_obj.tax_one2many:
				search_tax = account_tax_obj.search(cr,uid,[('id','=',tax_line_id.account_tax_id.id),('description','=','vat'),('active','=',True)])
				if search_tax:
					tax_list.append(search_tax[0])  
		if delivery_obj.freight_amount != 0.0 and str(delivery_obj.delivery_loc_state) == str(delivery_obj.source.state_id.name):
			search_tax = False
			tax_amount = []
			searched_tax = []
			max_tax_amount = 0.0
			if tax_list:
				for tax in tax_list:
					search_tax = account_tax_obj.search(cr,uid,[('id','=',tax),('description','=','vat')])
					searched_tax.append(search_tax[0])
			if searched_tax:
				for browse_record in account_tax_obj.browse(cr,uid,searched_tax):
					amount = browse_record.amount
					tax_amount.append(amount)
				if tax_amount:
					if len(tax_amount) == 1:
						max_tax_amount = tax_amount[0]
					else:
						max_tax_amount = max(tax_amount)
					fr_tax_amount = max_tax_amount * delivery_obj.freight_amount				
					fr_tax_amount = round(fr_tax_amount)
					total_amount = delivery_obj.freight_amount + fr_tax_amount + delivery_obj.total_amount
					total_amount = round(total_amount)
					total_vat = fr_tax_amount + delivery_obj.total_vat
					max_tax_name = account_tax_obj.search(cr,uid,[('description','=','vat'),('amount','=',max_tax_amount)])
					tax_name = account_tax_obj.browse(cr,uid,max_tax_name[0]).name
					tax_id = account_tax_obj.browse(cr,uid,max_tax_name[0]).id
					for tax_line_id in delivery_obj.tax_one2many:
						if tax_line_id.name == tax_name or tax_line_id.id == tax_id:
							tax_line_amt = tax_line_id.amount + fr_tax_amount
							tax_line_values ={
							'invoice_id': int(new_invoice_id),
							'account_tax_id':tax_line_id.account_tax_id.id,
							'name': tax_line_id.name,
							'amount':tax_line_amt,
							'tax_rate':tax_line_id.account_tax_id.amount * 100
							}
						else:
							tax_line_values ={
							'invoice_id': int(new_invoice_id),
							'account_tax_id':tax_line_id.account_tax_id.id,
							'name': tax_line_id.name,
							'amount':tax_line_id.amount,
							'tax_rate':tax_line_id.account_tax_id.amount * 100
							}
						res_tax_order_line_create= tax_line_obj.create(cr,uid,tax_line_values)
		else:
			total_amount = delivery_obj.freight_amount + delivery_obj.total_amount
			total_vat = delivery_obj.total_vat
			for tax_line_id in delivery_obj.tax_one2many:
				tax_line_values ={
				'invoice_id': int(new_invoice_id),
				'account_tax_id':tax_line_id.account_tax_id.id,
				'name': tax_line_id.name,
				'amount':tax_line_id.amount,
				'tax_rate':tax_line_id.account_tax_id.amount * 100
				}
				res_tax_order_line_create= tax_line_obj.create(cr,uid,tax_line_values)
		invoice_obj.write(cr,uid,int(new_invoice_id),{'product_order_grand_total':prod_order_grand_total,'order_total_vat':total_vat})
		delivery_schedule_id = self.pool.get('psd.sales.delivery.schedule').search(cr,uid,[('delivery_order_no','=',delivery_obj.stock_transfer_no)])
		self.pool.get('psd.sales.delivery.schedule').write(cr,uid,delivery_schedule_id,{'state':'invoiced'})
		brw_ids = self.pool.get('psd.sales.delivery.schedule').browse(cr,uid,delivery_schedule_id)[0] #sale_order_id
		sale_order_id = brw_ids.sale_order_id.id
		bool1 = brw_ids.sale_order_id.bool1

		if bool1 == False:
			self.pool.get('psd.sales.product.order').write(cr,uid,sale_order_id,{'invoiced_bool':False})
			cr.commit()
		else:
			self.pool.get('psd.sales.product.order').write(cr,uid,sale_order_id,{'invoiced_bool':True})
			cr.commit()
			self.pool.get('psd.sales.product.order').write(cr,uid,sale_order_id,{'state':'delivered'})
			cr.commit()

		self.write(cr,uid,delivery_obj.id,{'state':'invoiced'})
		# schedule_jobs_obj =  self.pool.get('res.scheduledjobs')
		# job_history_obj = self.pool.get('job.history')
		# print delivery_obj.delivery_challan_no,'DCCCCCCCCCCCCCCCC'
		# search_job_id = schedule_jobs_obj.search(cr,uid,[('delivery_challan_no','=',delivery_obj.delivery_challan_no)])
		# print search_job_id,'ssssss job id'
		# browse_job_id = schedule_jobs_obj.browse(cr,uid,search_job_id[0]).job_id
		# print browse_job_id,'bbbbbbbbbbbbbbbbbbbbbbbbbbbbb=='
		# search_history_ids = job_history_obj.search(cr,uid,[('job_id','=',browse_job_id)])
		# print search_history_ids,'idsssssssssssssssssssssss'
		# # b
		# for history_id in search_history_ids: 
		# 	self.pool.get('job.history').write(cr,uid,history_id,{'invoice_id':new_invoice_id})
		return True


	def print_report(self, cr, uid,ids,context=None):
		delivery_id = self.browse(cr,uid,ids[0])
		for calc in delivery_id.stock_transfer_product:
			product_name = calc.product_name.id
			product_obj = self.pool.get('product.product').browse(cr,uid,product_name)
			product_warranty = product_obj.warranty_life
			for transfer_series_id in delivery_id.transfer_series_ids:
				main_id  = transfer_series_id.id
				delivery_challan_date = transfer_series_id.from_date
				total_warranty = int(product_warranty) + int(calc.extended_warranty)
				no_of_months = relativedelta(months=total_warranty)
				string_datetime_conversion = datetime.strptime(delivery_challan_date, "%Y-%m-%d %H:%M:%S")
				string_datetime_conversion_date = string_datetime_conversion.date()
				to_date = string_datetime_conversion_date + no_of_months + relativedelta(days=-1)
				self.pool.get('transfer.series').write(cr,uid,main_id,{'due_date':to_date,'duration':total_warranty})
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'sk', 'stock_indent_report_print')
		return {
			'view_type': 'form',
			'view_mode': 'form',
			'name':'Report',
			'res_model': 'indent.report',
			'res_id': False,
			'views': [(form_view and form_view[1] or False, 'form'),
						(False, 'calendar'), (False, 'graph')],
			'type': 'ir.actions.act_window',
			'target':'new',
			}
		
	##### CEATE INVOICE ###########################################
	def onchange_stock_transfer_line(self,cr,uid,ids,transfer_line):
		val={}
		total_price=0
		for line in transfer_line:
			if line[2] and 'amount' in line[2]:
				total_price=total_price+line[2].get('amount')
		val['total_amount']=total_price
		val['batch_edit']=True # update_stock_dispatch button visible
		return {'value':val}
	#### Cancel Delivery Order 

	def nsd_cancel_stock_transfer(self,cr,uid,ids,context=None):
		###########added by shreyas for the indent
		res_indent_obj = self.pool.get('res.indent')
		o = self.browse(cr,uid,ids[0])
		delivery_order_id = o.id
		invisible_create_indent = o.invisible_create_indent
		if invisible_create_indent == True:
			res_indent_search = res_indent_obj.search(cr,uid,[('delivery_id','=',delivery_order_id)])
			res_indent_main_id = res_indent_obj.browse(cr,uid,res_indent_search[0]).id
			res_indent_state = res_indent_obj.browse(cr,uid,res_indent_search[0]).state
			if res_indent_state != 'draft':
				raise osv.except_osv(('Alert!'),('You Cannot Cancel the Order because the indent is created and proceeded'))
			if res_indent_state == 'new':
				write = res_indent_obj.write(cr,uid,res_indent_main_id,{'state','=','cancel'})
		#########################
		nosync_flag=False
		self.material_notes_update(cr,uid,ids,context=context)  
		self.state_update_cancel_order(cr,uid,ids)
		delivery_obj = self.browse(cr,uid,ids[0])
		sale_order_no = delivery_obj.sale_order_no
		psd_sale_order_obj = self.pool.get('psd.sales.product.order')
		for res in self.browse(cr,uid,ids):
			if res.create_bool:
				nosync_flag=res.create_bool
			if res.state =='draft':
				for line in res.stock_transfer_product:  
					if line.state != 'cancel_order_qty' and line.state != False:               
						self.pool.get('product.transfer').cancel_order(cr,uid,[line.id],context=None)
			else: 

# added for stock register report cancel delivery den delete entry from batchproduct_info table
			#for res in self.browse(cr,uid,ids):

							#self.pool.get('res.batchnumber').write(cr,uid,batch.id,{'qty':total})
							###################################Code for the reverse of the Stock in the batch
							
				if res.create_bool:
					nosync_flag=res.create_bool
				for line in res.stock_transfer_product:
					name = line.product_name.id
					q = line.quantity
					rt = line.rate
					if (line.batch) or (line.batch == 'NA'):
						for batch in self.pool.get('res.batchnumber').browse(cr,uid,[line.batch.id]):
							qty = batch.local_qty
							total = q + qty
							name = batch.name.id
							product_search = self.pool.get('product.product').search(cr,uid,[('id','=',name)])
							for kk in self.pool.get('product.product').browse(cr,uid,product_search):
								quantity_main = kk.quantity_available
								local_uom_relation = kk.local_uom_relation
								batch_quantity = total / local_uom_relation
								#self.pool.get('res.batchnumber').write(cr,uid,batch.id,{'qty':batch_quantity,'local_qty':total})
								quantity_main = 0.0
								name = batch.name.id
								batch_prodid=self.pool.get('batchproduct.info').search(cr,uid,[('ids','=',batch.id),('product_id','=',name),('qty','=',line.quantity),('sent','=',True),('datetime','=',line.datetime)])
								for btch_id in batch_prodid:
									self.pool.get('batchproduct.info').unlink(cr,uid,[btch_id]) 

			for k in self.browse(cr,uid,ids):
				form = k.id
				for o in k.stock_transfer_product:
					q = o.quantity
					if o.serial_line:
						for searials in o.serial_line:
							self.pool.get('product.series').write(cr,uid,searials.serial_no.id,{'quantity':1})              
							self.pool.get('transfer.series').unlink(cr,uid,[searials.id])               
				
					if (o.batch) or (o.batch == 'NA'):
						for i in self.pool.get('res.batchnumber').browse(cr,uid,[o.batch.id]):
							# qty = i.qty
							# #if qty >= 0:
							# total = q + qty
							# self.pool.get('res.batchnumber').write(cr,uid,[i.id],{'qty':total})
							#self.pool.get('product.product')._update_product_quantity(cr,uid,[i.name.id])
							qty = o.batch.local_qty
							total = q + qty
							name = i.name.id
							product_search = self.pool.get('product.product').search(cr,uid,[('id','=',name)])
							for kk in self.pool.get('product.product').browse(cr,uid,product_search):
								quantity_main = kk.quantity_available
								local_uom_relation = kk.local_uom_relation
								batch_quantity = total / local_uom_relation
								self.pool.get('res.batchnumber').write(cr,uid,i.id,{'qty':batch_quantity,'local_qty':total})
					self.pool.get('product.transfer').write(cr,uid,o.id,{'state':'cancel_order_qty'})					
			# if not nosync_flag:                 
			#     self.sync_cancel_delivery_order(cr,uid,ids,context=context) 
			self.prepare_notes_update(cr,uid,ids,context=context) 
			for res in self.browse(cr,uid,ids):
				if res.create_bool:
					nosync_flag=res.create_bool
				form_id = res.id		
				if res.state =='draft':
					self.write(cr, uid,res.id,{'state':'cancel'})
				if res.state =='assigned':
					self.write(cr, uid,res.id,{'state':'cancel'})
				if res.state=='confirmed':
					self.write(cr, uid,res.id,{'packlist_no':'','packlist_date':0,'stock_transfer_note_no':'','stock_transfer_date':0,'delivery_challan_no':'','delivery_challan_date':0,'state':'cancel'})
				if res.state=='progress':
					self.write(cr, uid,res.id,{'state':'cancel'})
				if res.state=='invoiced':
					self.write(cr, uid,res.id,{'state':'cancel'})
				origin = res.origin     
			# if not nosync_flag:
			#     self.sync_cancel_stock_transfer(cr,uid,ids,context=context)
			#     self.sync_cancel_dashboard(cr,uid,ids,context=context) 
			year = ''
			dict1 = {
					1: 'January', 
					2: 'February', 
					3: 'March',
					4:'April',
					5:'May',
					6:'June',
					7:'July',
					8:'August',
					9:'September',
					10:'October',
					11:'November',
					12:'December'
				};
		
			variable = self.pool.get('indent.new.dashboard').search(cr,uid,[('id','>',0)])
			current_date=date.today()
			monthee = current_date.month
			year = current_date.year
			words_month = dict1[monthee]
			search = self.pool.get('indent.new.dashboard').search(cr,uid,[('month','=',words_month),('year','=',year)])
			if search == []:
				create = self.pool.get('indent.new.dashboard').create(cr,uid,{'month':words_month,'count':'1','year':year,'month_id':monthee})
			else:
				for var in self.pool.get('indent.new.dashboard').browse(cr,uid,search):
					count = var.count
					count1 = int(count) - 1
					create = self.pool.get('indent.new.dashboard').write(cr,uid,var.id,{'count':count1,})
		
			variable = self.pool.get('indent.new.dashboard').search(cr,uid,[('id','>',0)])
			if variable == []:
				print"" 
			else:
				for file1 in self.pool.get('indent.new.dashboard').browse(cr,uid,variable):
					self.pool.get('indent.new.dashboard').write(cr,uid,file1.id,{'count1':None,'count2':None})

				vart=self.pool.get('indent.new.dashboard').search(cr,uid,[('id','>',0)])
				print vart
				for test in self.pool.get('indent.new.dashboard').browse(cr,uid,vart):
					current_date=date.today()
					month = current_date.month
					year = current_date.year
					previous_year = year - 1
					y = test.year
					count = test.count
					if y:
						if y == str(year):
							self.pool.get('indent.new.dashboard').write(cr,uid,test.id,{'check':True,'check1':False})
							self.pool.get('indent.new.dashboard').write(cr,uid,test.id,{'count2':count})
				
						if y == str(previous_year):
							self.pool.get('indent.new.dashboard').write(cr,uid,test.id,{'check1':True})
							self.pool.get('indent.new.dashboard').write(cr,uid,test.id,{'count1':count})
			psd_sales_product_order_id = psd_sale_order_obj.search(cr,uid,[('erp_order_no','=',sale_order_no)])
			browse_ids = self.pool.get('psd.sales.product.order').browse(cr,uid,psd_sales_product_order_id[0])
			delivery_scheduled_obj = self.pool.get('psd.sales.delivery.schedule')
			delivery_schedule_id = delivery_scheduled_obj.search(cr,uid,[('delivery_order_no','=',res.stock_transfer_no)])
			self.pool.get('psd.sales.delivery.schedule').write(cr,uid,delivery_schedule_id,{'state':'cancel'})
			lenght1 = len(browse_ids.delivery_schedule_ids)
			cancelled_list = []
			for each in browse_ids.delivery_schedule_ids:
				if each.state == 'cancel':
					cancelled_list.append(1)
			if lenght1 == len(cancelled_list):
				psd_sale_order_obj.write(cr,uid,psd_sales_product_order_id,{'state':'ordered'})
			else:
				psd_sale_order_obj.write(cr,uid,psd_sales_product_order_id,{'state':'partial_delivery_scheduled'})
		sale_order_line_obj = self.pool.get('psd.sales.product.order.lines')
		product_transfer_obj =  self.pool.get('product.transfer')
		stock_transfer_obj = self.pool.get('stock.transfer')
		browse_schedule_data = delivery_scheduled_obj.browse(cr,uid,delivery_schedule_id[0])
		for line_id in browse_schedule_data.scheduled_delivery_list:
			for sale_line in browse_ids.psd_sales_product_order_lines_ids:
				sale_product_name = sale_line.sku_name_id.id
				if sale_product_name == line_id.sku_name_id.id:
					sale_allocated_quantity = sale_line.allocated_quantity
					allocated_quantity = line_id.allocated_quantity
					if sale_allocated_quantity > 0: 
						sale_write_allocated_quantity = sale_allocated_quantity-allocated_quantity
						sale_order_line_obj.write(cr,uid,sale_line.id,{'allocated_quantity':sale_write_allocated_quantity})
		if res.delivery_challan_no:
			search_job_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('delivery_challan_no','=',res.delivery_challan_no)])
			self.pool.get('res.scheduledjobs').write(cr,uid,search_job_id[0],{'state':'cancel'})		
		
		models_data = self.pool.get('ir.model.data')
		tree_view = models_data.get_object_reference(cr, uid, 'psd_warehouse', 'stock_transfer_order_management_tree')
		form_view = models_data.get_object_reference(cr, uid, 'psd_warehouse', 'stock_transfer_order_management_form')
		return {
				'name': ('Delivery Order'),
				'view_type': 'list',
				'view_mode': 'list',
				'res_model': 'stock.transfer',
				'res_id':delivery_order_id,
				'view_id': False,
				'views': [(form_view and form_view[1] or False, 'form')],
				'type': 'ir.actions.act_window',
		}


	def state_update_cancel_order(self,cr,uid,ids):
		for k in self.browse(cr,uid,ids):
			state = k.state
			product = k.delivery_location.id
			for i in k.stock_transfer_product:
				search = self.pool.get('stock.picking').search(cr,uid,[('origin','=',k.origin),('id','=',k.stock_id)])#jan31
				for o in self.pool.get('stock.picking').browse(cr,uid,search):
					self.pool.get('stock.picking').write(cr,uid,o.id,{'check_process':False,'hide_check':True,'date_exp_check':False,'exp_final_delivery_dt':None,'hide_cancel':True})                  
					for search_id in o.move_lines:
						if search_id.product_id == i.product_name:
							if i.cancel_box==True:
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'pending'})
							else:                                               
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'pending','eta':0,'check_process':False,})
		return True


	
	def nsd_source_change(self, cr,uid, ids, source):
		val = {}
		if source:
			src = self.pool.get('res.company').search(cr,uid,[('id','=',source)])
			for files in self.pool.get('res.company').browse(cr,uid,src):
				apt = files.apartment
				building = files.building
				street = files.street
				area = files.sub_area
				landmark=files.landmark
				city = files.city_id.name1
				zip = files.zip
				phone=files.phone
				mobile=files.mobile
				email=files.email
				address=[apt,building,street,area,landmark,city,zip,phone,mobile,email]
				addr=', '.join(filter(bool,address))
				val['company_address'] = addr
			return {'value':val}
	### Cancel Delivery Order ################## END ################

	def ready_to_dispatch(self,cr,uid,ids,context=None):
		res = super(stock_transfer,self).ready_to_dispatch(cr,uid,ids,context=context)
		browse_id = self.browse(cr,uid,ids[0])
		if browse_id.delivery_location.state_id.id != browse_id.branch_name.state_id.id:
			is_road_permit = True
		else :
			is_road_permit = False
		self.pool.get('stock.transfer').write(cr,uid,browse_id.id,{'is_road_permit':is_road_permit})
		return res


	
	def round_off_grand_total(self,cr,uid,ids,grand_total,context=None):
		roundoff_grand_total = grand_total + 0.5
		s = str(roundoff_grand_total)
		dotStart = s.find('.')
		grand_total = int(s[:dotStart])
		return grand_total


	def serial_invisible(self,cr,uid,ids):
		for k in self.browse(cr,uid,ids):
			for o in k.stock_transfer_product:
				if o.product_name.type_product == 'track_equipment':
					self.pool.get('product.transfer').write(cr,uid,o.id,{'serial_check_visible':True})
		return True
	
	def nsd_prepare_packlist(self,cr,uid,ids,context=None):
		nosync_flag=False
		self.material_notes_update(cr,uid,ids,context=context)  
		id_val= []
		distribute_id = []
		iteritems = {}
		result = ''
		check_cancel_box=True
		amount=0.0
		total_weight=0.0
		total_vat=0.0
		additional_amt = subtotal = 0.0
		for check_b in self.browse(cr,uid,ids):
			if check_b.create_bool:
				nosync_flag=check_b.create_bool
			for res_b in check_b.stock_transfer_product:
				if not res_b.cancel_box:
					check_cancel_box=False
			if check_cancel_box:
				raise osv.except_osv(('Alert!'),('You Can Not Proceed With Cancelled Order'))
		for rec in self.browse(cr,uid,ids):
			
			delivery_type = rec.delivery_type
			for ls in rec.list_delivery_type_stock:
				if delivery_type == ls[0]:
					self.write(cr,uid,rec.id,{'delivery_type_char':ls[1]})
			delivery_location=rec.delivery_location.id
			source_location=rec.source.id
			source_state=0

			for chk in self.pool.get('res.company').browse(cr,uid,[source_location]):
				if chk.division.name == 'Product Sales':
					self.write(cr,uid,rec.id,{'sale_check':True})
				if chk.division.name != 'Product Sales':
					self.write(cr,uid,rec.id,{'not_product_sale':True})
			for chk in self.pool.get('res.company').browse(cr,uid,[delivery_location]): 
				if chk.division.name == 'Product Sales':
					self.write(cr,uid,rec.id,{'not_for_sale':False})
				else:
					self.write(cr,uid,rec.id,{'not_for_sale':True})

			for record in self.pool.get('res.company').browse(cr,uid,[delivery_location]):
				for record_state in self.pool.get('res.company').browse(cr,uid,[source_location]):
					source_state=record_state.state_id.id
				if record.state_id.id:
					if record.state_id.id != source_state:
						for temp in self.pool.get('state.name').browse(cr,uid,[record.state_id.id]):
							self.write(cr,uid,rec.id,{'permit_box':temp.state_box})
					if record.state_id.id == source_state:
						self.write(cr,uid,rec.id,{'permit_box':False})
				else:
					self.write(cr,uid,rec.id,{'permit_box':False})
			today_date=datetime.now().date()   
			stock_date=time.strftime('%Y-%m-%d %H:%M:%S')
			packlist_seq1=self._get_packlist(cr,uid,ids,context=None)
			self.pool.get('stock.transfer').write(cr,uid,rec.id,{'packlist_no1':packlist_seq1,'packlist_date1':stock_date})
			if rec.stock_transfer_product:
				form_id = rec.id
				#amount=rec.total_amount
				for line in rec.stock_transfer_product:
				  if not line.cancel_box: 
					for product_line in self.pool.get('product.product').browse(cr,uid,[line.product_name.id]):
						if line.qty_indent > product_line.quantity_available:
							if line.cancel_box != True:
								raise osv.except_osv(('Alert !'),('Required quantity is not present in selected Product %s.')%(line.product_name.name))

					if line.product_name.batch_type=='non_applicable':
						cr.execute("SELECT id,qty,manufacturing_date,name,batch_no,st,distributor,pm_dc_price,export_price,mrp,bom,local_qty  from res_batchnumber WHERE  name =%s and qty >0 " %(line.product_name.id))
					if line.product_name.batch_type=='applicable':
						cr.execute("SELECT id,qty,manufacturing_date,name,batch_no,st,distributor,pm_dc_price,export_price,mrp,bom,local_qty  from res_batchnumber WHERE manufacturing_date  >=(SELECT min(manufacturing_date) FROM res_batchnumber where name =%s ) and name =%s and qty > 0 order by manufacturing_date ",(line.product_name.id,line.product_name.id))
				
					id_val.extend(cr.fetchall())
				count1 = 0
				for line1 in rec.stock_transfer_product:
					new_values =line1.qty_indent
					discount = line1.discount
					print discount
					# nn
					if id_val:

							  #y - id, values_id - qty,r - manufacturing_date,l - name, k - batch_no,m - st,dist-distributor price
							  for y,values_id,r,l,k,m,dist,pm_dc_price,export_price,mrp,bom,local_qty in id_val:
								if not dist:
									dist = 0.0
								if len(id_val)-1 >= count1:
									batch_id=self.pool.get('res.batchnumber').search(cr,uid,[('id','=',y)])
									if values_id >= new_values and l == line1.product_name.id :
										#result=new_values*id_val[count1][5]
										result=new_values*dist if rec.delivery_type=='sales_delivery' else  new_values*m
										discount_amount = new_values * line1.rate * (line1.discount/100)
										# tax_amount = (new_values * line1.rate - discount_amount) * (line1.tax_id.amount)
										# tax_amount = self.round_off_grand_total(cr,uid,ids,tax_amount,context=None)
										# amount = line1.rate*new_values+tax_amount-discount_amount
										amount = line1.qty_indent * line1.rate
										amount = self.round_off_grand_total(cr,uid,ids,amount,context=None)
										total_weight=line1.product_name.weight_net*new_values
										print new_values,dist,export_price,pm_dc_price,m,line1.godown.id,'=========='
										if int(values_id)!=0:
											prod_id=self.pool.get("product.transfer").create(cr,uid,{'prod_id': rec.id,
																	'mfg_date':r,
																	'quantity' : new_values ,
																	#'available_quantity':values_id,
																	'available_quantity':local_qty,
																	'batch':batch_id[0],
																	'product_code':line1.product_code,
																	'product_name':line1.product_name.id,
																	'generic_id':line1.generic_id.id,
																	'amount':amount,
																	# 'rate':dist if rec.delivery_type=='sales_delivery' else m,
																	'qty_indent':line1.qty_indent,
																	'product_uom':line1.product_uom.id,
																	'product_category':line1.product_name.categ_id.id,
																	'msg_check_read':line1.msg_check_read,
																	'msg_check_unread':line1.msg_check_unread,
																	'batch_old':batch_id[0],
																	'quantity_old' : new_values ,
																	############################################
																	# 'cost_price':float(bom) if bom else 0.0,
																	'mrp':mrp if mrp else 0.0,
																	'dist_price':dist if dist else 0.0,
																	'export_price':export_price if export_price else 0.0,
																	'pmdc_price':pm_dc_price if pm_dc_price else 0.0,
																	'st_price':m if m else 0.0,
																	'state':'assigned',
																	############################################
																	# 'tax_id':line1.tax_id.id,
																	'dicount':line1.discount,
																	# 'discounted_amount':discount_amount,
																	# 'tax_amount':tax_amount,
																	'rate':line1.rate,
																	# 'amount':line1.amount,
																	# 'total_amount':line1.total_amount,
																	'godown':line1.godown.id,
																	'is_qty_allocated':line1.is_qty_allocated,
																	'is_track_equipment':line1.is_track_equipment,
																	'extended_warranty':line1.extended_warranty,
																	'additional_amt':line1.additional_amt,
																	# 'specification':line1.specification,
																	})
											distribute_id.extend([prod_id]) 
										if line1.notes_one2many:
											for notes_material in line1.notes_one2many:
												self.pool.get('product.transfer.comment.line').create(cr,uid,{
																						'user_id':notes_material.user_id,
																						'comment_date':notes_material.comment_date,
																						'comment':notes_material.comment,
																						'source':notes_material.source.id,
																						'indent_id':prod_id,})
										self.pool.get('product.transfer').unlink(cr,uid,line1.id)
										
										amount=amount+result
										
										track_prod_search=self.pool.get('product.series').search(cr,uid,[('product_name','=',line1.product_name.id),('batch','=',batch_id[0]),('quantity','=',1),('reject','=',False)])
										count=0
										if track_prod_search!=[]:
											for prod_series in track_prod_search:
												count=count+1
												if count <= new_values:
													self.pool.get('transfer.series').create(cr,uid,{'serial_no':prod_series,'series_line1':prod_id})
										count1 += 1
										break
									elif l == line1.product_name.id:
										new_values = new_values - int(values_id)
										total_weight=line1.product_name.weight_net*values_id
										result=id_val[count1][1]*dist if rec.delivery_type=='sales_delivery' else  id_val[count1][1]*m

										discount_amount1 = int(values_id) * line1.rate * (line1.discount/100)
										discount_amount1 = self.round_off_grand_total(cr,uid,ids,discount_amount1,context=None)
										tax_amount1 = (int(values_id) * line1.rate - discount_amount1) * (line1.tax_id.amount)
										tax_amount1 = self.round_off_grand_total(cr,uid,ids,tax_amount1,context=None)
										amount = line1.rate*int(values_id)+tax_amount1-discount_amount1
										if int(values_id) != 0:
											prod_id=self.pool.get("product.transfer").create(cr,uid,{'prod_id': rec.id,
																	'mfg_date':r,
																	'quantity' : new_values ,
																	#'available_quantity':values_id,
																	'available_quantity':local_qty,
																	'batch':batch_id[0],
																	'product_code':line1.product_code,
																	'product_name':line1.product_name.id,
																	'generic_id':line1.generic_id.id,
																	'amount':amount,
																	# 'rate':dist if rec.delivery_type=='sales_delivery' else m,
																	'qty_indent':line1.qty_indent,
																	'product_uom':line1.product_uom.id,
																	'product_category':line1.product_name.categ_id.id,
																	'msg_check_read':line1.msg_check_read,
																	'msg_check_unread':line1.msg_check_unread,
																	'batch_old':batch_id[0],
																	'quantity_old' : new_values ,
																	############################################
																	# 'cost_price':float(bom) if bom else 0.0,
																	'mrp':mrp if mrp else 0.0,
																	'dist_price':dist if dist else 0.0,
																	'export_price':export_price if export_price else 0.0,
																	'pmdc_price':pm_dc_price if pm_dc_price else 0.0,
																	'st_price':m if m else 0.0,
																	'state':'assigned',
																	############################################
																	# 'tax_id':line1.tax_id.id,
																	'dicount':line1.discount,
																	# 'discounted_amount':discount_amount,
																	# 'tax_amount':tax_amount,
																	'rate':line1.rate,
																	# 'amount':line1.amount,
																	# 'total_amount':line1.total_amount,
																	'godown':line1.godown.id,
																	'is_qty_allocated':line1.is_qty_allocated,
																	'is_track_equipment':line1.is_track_equipment,
																	'extended_warranty':line1.extended_warranty,
																	'additional_amt':line1.additional_amt,
																	})
											distribute_id.extend([prod_id]) 
											amount=amount+result
										if line1.notes_one2many:
											for notes_material in line1.notes_one2many:
												self.pool.get('product.transfer.comment.line').create(cr,uid,{
																						'user_id':notes_material.user_id,
																						'comment_date':notes_material.comment_date,
																						'comment':notes_material.comment,
																						'source':notes_material.source.id,
																						'indent_id':prod_id,})

										track_prod_search=self.pool.get('product.series').search(cr,uid,[('product_name','=',line1.product_name.id),('batch','=',batch_id[0]),('quantity','=',1),('reject','=',False)])
										count=0
										if track_prod_search!=[]:
											for prod_series in track_prod_search:
												count=count+1
												if count <= new_values:
													self.pool.get('transfer.series').create(cr,uid,{'serial_no':prod_series,'series_line1':prod_id})

										self.pool.get('product.transfer').unlink(cr,uid,line1.id)
										count1 += 1
					total_weight+=(line1.product_name.weight_net*line1.quantity)
				self.write(cr,uid,ids,{'state':'assigned','estimated_value':amount,'total_weight':total_weight,'total_amount':rec.total_amount})
				self.serial_invisible(cr,uid,ids)
				self.total_list(cr,uid,ids)
				#self.road_check(cr,uid,ids)
				self.state_update(cr,uid,ids) 
				self.prepare_cancel_box(cr,uid,ids)
				self.get_packaging_details(cr,uid,ids)
			else:
				raise osv.except_osv(('Alert!'),('Please Enter Product Details.'))
			delivery_schedule_id = self.pool.get('psd.sales.delivery.schedule').search(cr,uid,[('delivery_order_no','=',rec.stock_transfer_no)])
			self.pool.get('psd.sales.delivery.schedule').write(cr,uid,delivery_schedule_id,{'state':'assigned'})
			for product_line in rec.stock_transfer_product:
				if product_line.product_name.type_product == 'track_equipment':
					self.write(cr,uid,ids[0],{'is_track_equipment':True},context=context)
		if distribute_id:
			distribute_id.append(ids)
			self.distributor_mrp(cr, uid, distribute_id, context=context)
		#commented for the sync function used in nsd bhiwandi
		# if not nosync_flag:
		#     self.sync_prepare_packlist(cr,uid,ids,context=context)
		#####################################################
		self.prepare_notes_update(cr,uid,ids,context=context) 
		return True

	### Cancel Packlist 
	def nsd_cancel_packlist(self,cr,uid,ids,context=None):
		self.material_notes_update(cr,uid,ids,context=context)  
		count = 0
		##self.sync_cancel_packlist(cr,uid,ids,context=context)                      
		# for res in self.browse(cr,uid,ids):
		#     if not res.create_bool:
				#self.sync_cancel_packlist(cr,uid,ids,context=context)
		for res in self.browse(cr,uid,ids):
			self.write(cr,uid,res.id,{'sale_check':False})

			self.write(cr,uid,res.id,{'permit_box':False})
			for line in res.stock_transfer_product:
				cc_date = datetime.now()
				c_date=datetime.strftime(cc_date,"%Y-%m-%d %H:%M:%S")
				current_date = datetime.now().date()
				monthee = current_date.month
				year = current_date.year
				day = current_date.day
				name = line.product_name.id
				self.pool.get('product.series').write(cr,uid,line.serial_no.id,{'quantity':1}) 
				q = line.quantity
				rt = line.rate
				if (line.batch) or (line.batch == 'NA'):
					for batch in self.pool.get('res.batchnumber').browse(cr,uid,[line.batch.id]):
						#qty = batch.qty
						qty = batch.local_qty
						quantity_main = 0.0
						name = batch.name.id
						product_search = self.pool.get('product.product').search(cr,uid,[('id','=',name)])
						for kk in self.pool.get('product.product').browse(cr,uid,product_search):
							quantity_main = kk.quantity_available
							local_uom_relation = kk.local_uom_relation
						if qty >= 0: 
						
							total = q + qty
							#self.pool.get('res.batchnumber').write(cr,uid,batch.id,{'qty':total})
							###################################Code for the reverse of the Stock in the batch
							batch_quantity = total / local_uom_relation
							self.pool.get('res.batchnumber').write(cr,uid,batch.id,{'qty':batch_quantity,'local_qty':total})
							#################################################################################

							batch_prodid=self.pool.get('batchproduct.info').search(cr,uid,[('ids','=',batch.id),('product_id','=',name),('qty','=',line.quantity),('sent','=',True),('datetime','=',line.datetime)])
							for btch_id in batch_prodid:
								self.pool.get('batchproduct.info').unlink(cr,uid,[btch_id])                         

							self.pool.get('product.product')._update_product_quantity(cr,uid,[batch.name.id])
				
			self.write(cr,uid,res.id,{
										'total_weight':'',
										'estimated_value':0.0,
										'person_name':'',
										'transporter':'',
										'vehicle_no':'',
										'driver_name':'',
										'lr_no':'',
										'lr_date':0,
										#'total_amount':0,
										'state':'draft'
									})
			var = ''
			for val in res.stock_transfer_product:
				if val.serial_line:
					for var_serial in val.serial_line:
						self.pool.get('transfer.series').unlink(cr,uid,var_serial.id)
				if val.product_name:
					count = count + 1
					if var == val.product_name.id:
						self.pool.get('product.transfer').unlink(cr,uid,val.id)
						count = 0
					else:
						self.pool.get('product.transfer').write(cr, uid,[val.id],{'batch':'',
										'quantity':0,
										'amount':val.amount,
										'available_quantity':0.0,
										#'rate':0.0, 
										'mfg_date':None})
						var = val.product_name.id
		self.cancel_prepare_box(cr,uid,ids)
		self.state_update_cancel_packlist(cr,uid,ids)
		self.prepare_notes_update(cr,uid,ids,context=context) 
		delivery_schedule_id = self.pool.get('psd.sales.delivery.schedule').search(cr,uid,[('delivery_order_no','=',res.stock_transfer_no)])
		self.pool.get('psd.sales.delivery.schedule').write(cr,uid,delivery_schedule_id,{'state':'draft'})
		return True

	def cancel_prepare_box(self,cr,uid,ids):
		for k in self.browse(cr,uid,ids):
			for o in k.stock_transfer_product:
				if o.prepare_cancel == True :
					self.pool.get('product.transfer').write(cr,uid,o.id,{'prepare_cancel':False})
		return True

	def state_update_cancel_packlist(self,cr,uid,ids):
		for k in self.browse(cr,uid,ids):
			state = k.state
			product = k.delivery_location.id
			for i in k.stock_transfer_product:
				search = self.pool.get('stock.picking').search(cr,uid,[('origin','=',k.origin),('id','=',k.stock_id)])
				for o in self.pool.get('stock.picking').browse(cr,uid,search):
					for search_id in o.move_lines:
						if search_id.product_id == i.product_name :
							if i.cancel_box==True:
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'pending'})
							else:                                               
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'view_order','eta':None})
		return True
	### Cancel Packlist ################ END ######################################### 

	def total_list(self,cr,uid,ids):
			for k in self.browse(cr,uid,ids):
				ids1 = k.id
				cc_date = datetime.now()
				c_date=datetime.strftime(cc_date,"%Y-%m-%d %H:%M:%S")
				current_date = datetime.now().date()
				monthee = current_date.month
				year = current_date.year
				day = current_date.day
				for line in k.stock_transfer_product:
					 res = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',line.product_name.id)],order='manufacturing_date desc')
					 if line.batch.id != False:
					  for batch in self.pool.get('res.batchnumber').browse(cr,uid,[line.batch.id]):
							# total =  batch.qty - line.quantity
							total =  batch.local_qty - line.quantity
							quantity_main = 0.0
							name = batch.name.id
							product_search = self.pool.get('product.product').search(cr,uid,[('id','=',name)])
							for kk in self.pool.get('product.product').browse(cr,uid,product_search):
								quantity_main = kk.quantity_available
								local_uom_relation = kk.local_uom_relation
							batch_quantity = total/local_uom_relation
							self.pool.get('res.batchnumber').write(cr,uid,[batch.id],{'local_qty':total,'qty':batch_quantity})
							ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':batch.id,'product_id':name,'date':current_date,'sent':True,'qty':line.quantity,'day':day,'month':monthee,'year':year,'product_qty':quantity_main,'datetime':c_date,'transaction_number':k.packlist_no1,'transaction_date':k.packlist_date1})
							self.pool.get('product.product')._update_product_quantity(cr,uid,[batch.name.id])
							self.pool.get('product.series').write(cr,uid,line.serial_no.id,{'quantity':0})
							self.pool.get('product.transfer').write(cr,uid,line.id,{'datetime':c_date})
					 elif line.batch.id == False:
						for batch in self.pool.get('res.batchnumber').browse(cr,uid,res):
							# total =  batch.qty - line.quantity
							total =  batch.local_qty - line.quantity
							quantity_main = 0.0
							name = batch.name.id
							product_search = self.pool.get('product.product').search(cr,uid,[('id','=',name)])
							for kk in self.pool.get('product.product').browse(cr,uid,product_search):
								quantity_main = kk.quantity_available
								local_uom_relation = kk.local_uom_relation
							batch_quantity = total/local_uom_relation
							self.pool.get('res.batchnumber').write(cr,uid,[batch.id],{'local_qty':total,'qty':batch_quantity})
							ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':batch.id,'product_id':name,'date':current_date,'sent':True,'qty':line.quantity,'day':day,'month':monthee,'year':year,'product_qty':quantity_main,'datetime':c_date,'transaction_number':k.packlist_no1,'transaction_date':k.packlist_date1})
							self.pool.get('product.product')._update_product_quantity(cr,uid,[batch.name.id])
							self.pool.get('product.series').write(cr,uid,line.serial_no.id,{'quantity':0})
							self.pool.get('product.transfer').write(cr,uid,line.id,{'datetime':c_date})
			return True

	def state_update(self,cr,uid,ids):
		for k in self.browse(cr,uid,ids):
			state = k.state
			product = k.delivery_location.id
			for i in k.stock_transfer_product:
				search = self.pool.get('stock.picking').search(cr,uid,[('origin','=',k.origin),('id','=',k.stock_id)])
				for o in self.pool.get('stock.picking').browse(cr,uid,search):
					for search_id in o.move_lines:
						if search_id.product_id == i.product_name :
							if i.cancel_box==True:
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'pending'})
							else:
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'packlist'})
		return True

	def prepare_cancel_box(self,cr,uid,ids):
		for k in self.browse(cr,uid,ids):
			for o in k.stock_transfer_product:
				if o.state != 'cancel_order_qty':
					self.pool.get('product.transfer').write(cr,uid,o.id,{'prepare_cancel':True})
		return True

	def prepare_notes_update(self,cr,uid,ids,context=None):
		msg_flag=False
		for i in self.browse(cr,uid,ids):       
			stock_id = i.stock_id
			search = self.pool.get('stock.picking').search(cr,uid,[('id','=',stock_id)])
			for j in self.pool.get('stock.picking').browse(cr,uid,search):
				form_id = j.id
				if i.notes_one2many:
					for test in i.notes_one2many:
						search1 = self.pool.get('indent.remark').search(cr,uid,[('remark','=',form_id),('source','=',test.source.id),('user','=',test.user_name),('date','=',test.date),('remark_field','=',test.name)])
						if search1 == []:
							msg_flag=True
							create = self.pool.get('indent.remark').create(cr,uid,{'remark':form_id,'source':test.source.id,'user':test.user_name,'date':test.date,'remark_field':test.name})
				if msg_flag:
					self.pool.get('stock.picking').write(cr,uid,form_id,{'msg_check':True,})
		for i in self.browse(cr,uid,ids):       
			stock_id = int(i.stock_id)
			search = self.pool.get('stock.picking').search(cr,uid,[('id','=',stock_id)])
			for order in i.stock_transfer_product:
				product_name=order.product_name.id
				for order_id in order.notes_one2many:
					user=order_id.user_id
					comment=order_id.comment
					comment_date=order_id.comment_date
					source=order_id.source.id
					search_move = self.pool.get('stock.move').search(cr,uid,[('product_id','=',product_name),('picking_id','=',stock_id)])
					for line in self.pool.get('stock.move').browse(cr,uid,search_move):
						form_id = line.id
						search_notes=self.pool.get('stock.move.comment.line').search(cr,uid,[('indent_id','=',form_id),('user_id','=',user),('comment','=',comment),('comment_date','=',comment_date),('source','=',source)])   
						if search_notes:
							print 'kk'
						else:
							msg_flag=True
							self.pool.get('stock.move').write(cr,uid,[form_id],{'msg_check_unread':True,'msg_check_read':False})
							self.pool.get('stock.move.comment.line').create(cr,uid,{'user_id':user,'comment':comment,
																	'comment_date':comment_date,'source':source,'indent_id':form_id})           
			if msg_flag:
				self.pool.get('stock.picking').write(cr,uid,stock_id,{'msg_check':True,})
		return True

	def get_packaging_details(self,cr,uid,ids):
		total_carton=0.0        
		search_ids = self.pool.get('product.transfer').search(cr,uid,[('prod_id','=',ids),('pakaging_details_manual','=',False)])
		for eachprod in self.pool.get('product.transfer').browse(cr,uid,search_ids):    
			c_type=eachprod.product_name.carton_type.id
			prod_qty=eachprod.quantity
			per_shipper=eachprod.product_name.carton_per_shipper
			'''if eachprod.product_name.carton_type.carton_code=='other':
				other_count +=1
				if other_count==1:
					self.pool.get('product.transfer').write(cr,uid,eachprod.id,{'carton_no':1,'carton_type':c_type,'contained':'contained'})
				else:
					self.pool.get('product.transfer').write(cr,uid,eachprod.id,{'contained':'packed'})

			else:'''
			if prod_qty >0 and prod_qty<per_shipper:
				total_carton=1
		
			else:
				total_carton = (math.ceil(eachprod.quantity/float(eachprod.product_name.carton_per_shipper))) if eachprod.product_name.carton_per_shipper else 0

			self.pool.get('product.transfer').write(cr,uid,eachprod.id,{'carton_no':total_carton,'carton_type':c_type})


	def nsd_ready_to_dispatch(self,cr,uid,ids,context=None):
		nosync_flag=False
		distribute_id = []
		unadjastable=0
		total_unadjastable=0
		flag=True
		batch=''
		additional_amt = subtotal = 0.0
		self.material_notes_update(cr,uid,ids,context=context)
		#self.update_stock_dispatch(cr,uid,ids,context=context)  
		for res in self.browse(cr,uid,ids):

			if res.create_bool:
				nosync_flag=res.create_bool
			stock_transfer_id = res.id
			current_date=datetime.now()
			del_date=datetime.strptime(res.delivery_date,"%Y-%m-%d")
			# if del_date.date() < current_date.date():
			# 		raise osv.except_osv(('Alert!'),('Please Enter Valid date.'))
			if (not res.mode_transport) or (not res.delivery_date) :
				raise osv.except_osv(('Alert!'),('Please enter appropriate transport details.'))
			today_date=datetime.now().date()
			for line1 in res.stock_transfer_product:
				print line1.rate,line1.quantity,'================lineeeee'
				self.pool.get('product.transfer').write(cr,uid,line1.id,{'qunatity':line1.qty_indent})
				cr.commit()				
				amount = line1.rate * line1.qty_indent
				self.pool.get('product.transfer').write(cr,uid,line1.id,{'amount':amount})
				cr.commit()
				if line1.rate <=0 or amount<=0 :
					raise osv.except_osv(('Alert!'),('Rate and Amount for %s cannot Zero .' %(line1.product_name.name)))
			if not res.stock_transfer_note_no :
				if res.delivery_type not in ('sales_delivery','free_sample_delivery','calibration'):
					stock_seq= self._get_stn(cr,uid,ids,context=None)
				else :
					stock_seq=None
			else :
					stock_seq=res.stock_transfer_note_no
			if not res.delivery_challan_no :
				delivery_challan_seq= self._get_delivery_challan(cr,uid,ids,context=None)
			else :
				delivery_challan_seq=res.delivery_challan_no
			#invoice_seq = self._get_invoice(cr,uid,ids,context=None)        

			for line1 in res.stock_transfer_product:
			 if line1.batch != batch:
				batch=line1.batch
			 else:
				raise osv.except_osv(('Alert!'),('Select Unique Batch for Product: "%s" ')%(line1.product_name.name_template))     

			for line1 in res.stock_transfer_product:
				if line1.additional_amt!=0.0:
					additional_amt = line1.additional_amt
					subtotal = line1.rate + additional_amt
					subtotal = subtotal * line1.quantity
					self.pool.get('product.transfer').write(cr,uid,line1.id,{'amount':subtotal})
					cr.commit()
				else:
					subtotal = line1.rate * line1.quantity
					self.pool.get('product.transfer').write(cr,uid,line1.id,{'amount':subtotal})
					cr.commit()
				print subtotal,'=====================subtotal'
				product_obj = self.pool.get('product.product').browse(cr,uid,line1.product_name.id)
				product_warranty = product_obj.warranty_life
				current_date = datetime.now().date()
				total_warranty = int(product_warranty) + int(line1.extended_warranty)
				no_of_months = relativedelta(months=total_warranty)
				to_date = current_date + no_of_months + relativedelta(days=-1)
				if line1.state!='cancel_order_qty':
					distribute_id.extend([line1.id]) 
					# if line1.product_name.type_product=='track_equipment':
					# 		if not line1.serial_line:
					# 			raise osv.except_osv(('Alert !'),('Please Attach Serial Number For Product: "%s" ') % (line1.product_name.name_template,))
				for serial in line1.serial_line:
					if serial:
						self.pool.get('transfer.series').write(cr,uid,serial.id,
							{'serial_line_id':stock_transfer_id,
							#'serial_no':serial.serial_no.id,
							'serial_name':serial.serial_name,
							'sr_no':serial.sr_no,
							'product_code':serial.serial_no.product_name.default_code,
							'product_name':serial.serial_no.product_name.id,
							'product_category':serial.serial_no.product_category.id,
							'product_uom':serial.serial_no.product_name.uom_id.id,
							'batch':serial.serial_no.batch.id,
							'quantity':1,
							'active_id':False,
							'serial_check':True,
							'from_date':current_date,
							'due_date':to_date,
							'duration':total_warranty})
						serial_no=serial.serial_no.id
						self.pool.get('product.series').write(cr,uid,serial_no,{'quantity':0 })  
				#for line1 in res.stock_transfer_product:
				if line1.state!='cancel_order_qty':
					if line1.product_name.type_product=='track_equipment':
						count=0
						for line in line1.serial_line:
							count=count+1
						# if line1.quantity != count:
						# 	raise osv.except_osv(('Alert!'),('Serial Line Should be Equal to Quantity for Product: "%s"  And  For Batch:"%s" ')%(line1.product_name.name_template,line1.batch.batch_no))    
				stock_date=time.strftime('%Y-%m-%d %H:%M:%S')
				self.pool.get('stock.transfer').write(cr,uid,res.id,{'stock_transfer_note_no':stock_seq,
										'stock_transfer_date':stock_date,
										'delivery_challan_no':delivery_challan_seq,
										#'invoice_no':invoice_seq,
										'invoice_date':stock_date,
										'delivery_challan_date':stock_date}) 
				######### Create Job on Ready To Dipatch #############################e
				seq_id = self.pool.get('ir.sequence').get(cr, uid,'operation.job.id')
				ou_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
				# year1=today_date.strftime('%y')
				company_id=self._get_company(cr,uid,context=None)
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					job_code=comp_id.job_id
				# month=today_date.strftime('%m')
				# if int(month)>3:
				# 		year2=int(year1)+1
				# else :  
				# 		year2=int(year1)
				# job_id =str(ou_id)+job_code+str(year2)+str(seq_id)
				today_date = datetime.now().date()
				year1 = today_date.strftime('%y')
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
				job_id =str(ou_id)+job_code+financial_year+str(seq_id)
				# print job_id,res.against_free_replacement
				# bb
				job_data = {
							'name_contact':res.partner_id.id,
							'job_category':'delivery',	
							'job':'delivery',
							'delivery_order_no':res.stock_transfer_no,
							'delivery_address':res.delivery_address,
							'delivery_challan_no':delivery_challan_seq,
							'delivery_note_date':stock_date,
							'job_id':job_id,
							'scheduled_job_id':job_id,
							'pse':res.pse.id if res.pse.id else None,
							'web_order_no':res.web_order_number,
							'web_order_date':res.web_order_date,
							'erp_order_no':res.sale_order_no,
							'erp_order_date':res.sale_order_date,
							'against_free_replacement':res.against_free_replacement,
							# 'phone_on_fly':res.contact_no,
							'phone1':res.contact_no,
							'state':'unscheduled',
							'company_id':company_id,
							'req_date_time':res.expected_delivery_date,# expected delivery date
							'contact_name':res.partner_id.name,#customer name both
							'is_transfered':False,
							# 'holiday_active':1,
							}
		self.generate_gst_taxes(cr,uid,ids,context=context) 	
		# print job_data,'\n========================'
		# invoice_id = self.pool.get('res.scheduledjobs').create(cr,uid,job_data)
		# print invoice_id,'========================='
		# nnn
		for line2 in res.stock_transfer_product:
			if line2.state != 'cancel_order_qty':
				self.pool.get('product.transfer').write(cr,uid,line2.id,
					{'exp_date':line2.batch.exp_date})
				# self.pool.get('product.transfer').write(cr,uid,line2.id,
				# 	{'exp_date':line2.batch.exp_date,'product_data':invoice_id})
		################################## END ###############################
		delivery_schedule_id = self.pool.get('psd.sales.delivery.schedule').search(cr,uid,[('delivery_order_no','=',res.stock_transfer_no)])
		self.pool.get('psd.sales.delivery.schedule').write(cr,uid,delivery_schedule_id,{'state':'confirmed','delivery_challan_no':delivery_challan_seq})
		if distribute_id:
			distribute_id.append(ids)
			self.distributor_mrp(cr, uid, distribute_id, context=context)
		self.state_update_ready(cr,uid,ids)
		self.write(cr,uid,ids,{'state':'confirmed','packlist_no':res.packlist_no1,'packlist_date':res.packlist_date1,})
		#####Comment for the sync functionality in the NSD Bhiwandi branch
		# if not nosync_flag:
		#     self.sync_ready_to_dispatch(cr,uid,ids,context)
		#############################################
		self.prepare_notes_update(cr,uid,ids,context=context) #feb11
		return True

	def generate_gst_taxes(self,cr,uid,ids,context=None): #stock.purchase
		cur_rec = self.browse(cr,uid,ids)[0]
		sgst_rate=cgst_rate=igst_rate=igst_amount=sgst_amount=cgst_amount=gst_total=0.0
		supplier_state=''
		tax_rate=additional_amount=0.0
		tax_check = False
		st_rate = ''
		grn_o_brw=self.browse(cr,uid,ids[0]) 
		company_state=self.pool.get('res.users').browse(cr,uid,1).company_id.state_id.id
		if grn_o_brw:
			delivery_location = grn_o_brw.partner_id.state_id.id
			print delivery_location,company_state
			if not delivery_location:
				raise osv.except_osv(('Alert!'),('Please Verify delivery location state'))				
			for i in grn_o_brw.stock_transfer_product:
				tax_check=i.product_name.product_tax.id
				tax_rate=i.product_name.product_tax.amount
				hsn_code=i.product_name.hsn_sac_code
				if not hsn_code:
							raise osv.except_osv(('Alert!'),('Please verify HSN/SAC Code for product '+str(i.product_name.name)))					
				if not tax_check:
							raise osv.except_osv(('Alert!'),('Please check product tax for product '+str(i.product_name.name)))	

				subtotal = i.rate * i.qty_indent
				if tax_rate or tax_rate == 0.0:
					if company_state==delivery_location:
						sgst_rate=cgst_rate=tax_rate/2
						sgst_amount=cgst_amount=(tax_rate*subtotal)/2
					else:
						igst_rate=tax_rate
						igst_amount=tax_rate*subtotal
				print sgst_amount,cgst_amount,igst_amount
				gst_total=igst_amount+sgst_amount+cgst_amount
				mat_ids=self.pool.get('product.transfer').search(cr,uid,[('id','=',i.id)])
				if mat_ids:
					self.pool.get('product.transfer').write(cr,uid,mat_ids[0],{'sgst_rate':str(sgst_rate*100)+'%','cgst_rate':str(cgst_rate*100)+'%','igst_rate':str(igst_rate*100)+'%','sgst_amount':sgst_amount,'cgst_amount':cgst_amount,'igst_amount':igst_amount,'amount':subtotal,'gst_amount':gst_total,'tot_amount':gst_total+subtotal})
					cr.commit()
		return True
	#######################################################################################################
	def nsd_update_stock_dispatch(self, cr, uid, ids, context=None):
		for res in self.browse(cr,uid,ids if isinstance(ids,(list,tuple)) else [ids]):
			if res.state=='assigned' :
				quantity_main=0.0
	
	##############################################################################################################          
				qry="select sum(quantity) as allocated,max(qty_indent) as intended,(select name_template from product_product where id=product_name) from product_transfer where prod_id=%s AND (state not in ('cancel_order_qty','cancel') or state is null) group by product_name"%(str(res.id))
				cr.execute(qry)
				prod_transfer=cr.fetchall()
				if prod_transfer:
					for eachprod in prod_transfer:
						if eachprod[0]!= eachprod[1]:
							raise osv.except_osv(('Alert!'),('Total Allocated quantity should match with Indent quantity for Product:  %s')%(eachprod[2]))
	##############################################################################################################
				total_amount = 0.0
				for line_prod in res.stock_transfer_product:
					if line_prod.batch.id ==line_prod.batch_old.id and line_prod.quantity == line_prod.quantity_old :
						pass
					else :
						cc_date = datetime.now()
						c_date=datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
						current_date = datetime.now().date()
						monthee = current_date.month
						year = current_date.year
						day = current_date.day
						quantity_main = self.pool.get('product.product').browse(cr,uid,line_prod.batch.name.id).quantity_available
						if (line_prod.batch.id !=line_prod.batch_old.id and line_prod.batch_old.id) or (line_prod.quantity != line_prod.quantity_old and line_prod.quantity_old) :
							if line_prod.batch.id !=line_prod.batch_old.id and line_prod.batch_old.id :
								batch_qty=self.pool.get('res.batchnumber').browse(cr,uid,line_prod.batch_old.id).qty
								total_total =  batch_qty + line_prod.quantity_old
								self.pool.get('res.batchnumber').write(cr,uid,line_prod.batch_old.id,{'qty':total_total})
								if line_prod.quantity >0:
									quantity_main = self.pool.get('product.product').browse(cr,uid,line_prod.batch.name.id).quantity_available
									batch_qty=self.pool.get('res.batchnumber').browse(cr,uid,line_prod.batch.id).qty
									total_total =  batch_qty - line_prod.quantity
									self.pool.get('res.batchnumber').write(cr,uid,line_prod.batch.id,{'qty':total_total})
								else :
									quantity_main = self.pool.get('product.product').browse(cr,uid,line_prod.batch.name.id).quantity_available
									total_total =  batch_qty + line_prod.quantity_old
									self.pool.get('res.batchnumber').write(cr,uid,line_prod.batch.id,{'qty':total_total})
							else :
								quantity_main = self.pool.get('product.product').browse(cr,uid,line_prod.batch.name.id).quantity_available
								batch_qty=self.pool.get('res.batchnumber').browse(cr,uid,line_prod.batch.id).qty
								diff_qty=line_prod.quantity_old-line_prod.quantity
								if diff_qty==line_prod.quantity_old :
									total_total =  batch_qty + line_prod.quantity_old
									self.pool.get('res.batchnumber').write(cr,uid,line_prod.batch.id,{'qty':total_total})
								else :
									total_total =  batch_qty + diff_qty
									self.pool.get('res.batchnumber').write(cr,uid,line_prod.batch.id,{'qty':total_total})
						if not line_prod.batch_old.id and not line_prod.quantity_old :
							quantity_main = self.pool.get('product.product').browse(cr,uid,line_prod.batch.name.id).quantity_available
							batch_qty=self.pool.get('res.batchnumber').browse(cr,uid,line_prod.batch.id).qty
							total_total =  batch_qty - line_prod.quantity
							self.pool.get('res.batchnumber').write(cr,uid,line_prod.batch.id,{'qty':total_total})
						self.pool.get('product.product')._update_product_quantity(cr,uid,[line_prod.batch.name.id])
						amount =line_prod.rate*line_prod.quantity+line_prod.tax_amount-line_prod.discounted_amount
						self.pool.get('product.transfer').write(cr,uid,line_prod.id,{'batch_old':line_prod.batch.id,'quantity_old':line_prod.quantity,'amount':amount})
						total_amount = total_amount + line_prod.amount

				for line_prod in res.stock_transfer_product:
					if line_prod.quantity <=0 :
						self.pool.get('product.transfer').unlink(cr,uid,line_prod.id)
		self.pool.get('stock.transfer').write(cr,uid,line_prod.prod_id.id,{'total_amount':total_amount})
		self.get_packaging_details(cr,uid,ids)
		self.write(cr,uid,ids,{'batch_edit':False}) # nsd_update_stock_dispatch button invisible
		return True
################################################################################################################################

	def distributor_mrp(self, cr, uid, distribute_id, context=None):
		prod_transfer_obj = self.pool.get('product.transfer')
		stock_transfer_obj = self.pool.get('stock.transfer')
		batch_obj = self.pool.get('res.batchnumber')
		o2m_list = distribute_id[0:len(distribute_id)-1]
		main_list = distribute_id[len(distribute_id)-1]
		total_amount = 0.0
		total_export_amount = 0.0
		total_tax_amount=0.0
		total_unadjastable1=0
		grt_tax=0
		for dis_id in o2m_list:
			prod_transfer = prod_transfer_obj.browse(cr, uid, [dis_id])[0]
			dis_price = prod_transfer.batch.distributor if prod_transfer.batch else 1 
			export_price = prod_transfer.batch.export_price if prod_transfer.batch else 1 
			allocated = prod_transfer.qty_indent
			sub_total = dis_price * allocated
			export_sub_total=export_price * allocated
			vat_tax=0
			vat_amount_total=0.0
			total_unadjastable=0
			total_unadjastable1=sub_total+total_unadjastable1
			unadjastable=0
			for var_id in self.pool.get('product.product').browse(cr,uid,[prod_transfer.product_name.id]):
				if var_id.tax_one2many:
				  for tax_id in var_id.tax_one2many:
					vat_tax=tax_id.tax_value
					if vat_tax > grt_tax:
						grt_tax=vat_tax
					vat_tax_val=sub_total * (vat_tax/100)
					vat_amount_total=vat_amount_total+vat_tax_val
			total_tax_amount=total_tax_amount+vat_amount_total  
			###########Commented by shreyas because dis_sub_total,export_sub_total field is not found in SSD product.transfer
			prod_transfer_obj.write(cr, uid, dis_id, {'export_rate':export_price,'export_sub_total':export_sub_total,'dis_rate':dis_price, 'dis_sub_total':sub_total,'total_taxable':vat_amount_total})
			# prod_transfer_obj.write(cr, uid, dis_id, {'export_rate':export_price,'dis_rate':dis_price,'total_taxable':vat_amount_total})
		for sk_id in main_list:
			stock_transfer = stock_transfer_obj.browse(cr, uid, [sk_id])[0]
			for st_line in stock_transfer.stock_transfer_product:
				###########Commented by shreyas because dis_sub_total,export_sub_total field is not found in SSD product.transfer
				total_amount=total_amount+st_line.dis_sub_total
				total_export_amount=total_export_amount+st_line.export_sub_total
				# total_amount = total_amount
				# total_export_amount=total_export_amount

			if stock_transfer.rounding_selection:
				if stock_transfer.rounding_selection in ('add'):
					unadjastable=stock_transfer.rounding
				if stock_transfer.rounding_selection in ('substract'):
						unadjastable=-stock_transfer.rounding
			total_unadjastable1=unadjastable+stock_transfer.add_debit-stock_transfer.less_credit
		total_unadjastable = total_amount +total_tax_amount+total_unadjastable1
		stock_transfer_obj.write(cr, uid, main_list, {'dis_total':total_amount,'total_tax':total_tax_amount,'total_unadjastable':total_unadjastable,'export_total':total_export_amount,
'grt_tax':grt_tax})
		return True


	def state_update_ready(self,cr,uid,ids):
		for k in self.browse(cr,uid,ids):
			state = k.state
			product = k.delivery_location.id
			for i in k.stock_transfer_product:
				if i.state != 'cancel_order_qty':
					self.pool.get('product.transfer').write(cr,uid,i.id,{'state':'confirmed',})
				search = self.pool.get('stock.picking').search(cr,uid,[('origin','=',k.origin),('id','=',k.stock_id)])
				for o in self.pool.get('stock.picking').browse(cr,uid,search):
					for search_id in o.move_lines:
						if search_id.product_id == i.product_name :
							if i.cancel_box==True:
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'pending'})
							else:                                               
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'ready','eta':k.expected_delivery_time})
		return True


	def nsd_dispatch(self,cr,uid,ids,context=None):
		nosync_flag=False
		year = ''
		dict1 = {
				1: 'January', 
				2: 'February', 
				3: 'March',
				4:'April',
				5:'May',
				6:'June',
				7:'July',
				8:'August',
				9:'September',
				10:'October',
				11:'November',
				12:'December'
			};
		self.material_notes_update(cr,uid,ids,context=context)          
		for s in self.browse(cr,uid,ids):
			if s.create_bool:
				nosync_flag=s.create_bool
			if not s.road_permit_no and s.permit_box:
				raise osv.except_osv(('Alert!'),('please Enter Road Permit Number'))
		variable = self.pool.get('indent.new.dashboard').search(cr,uid,[('id','>',0)])
		current_date=date.today()
		monthee = current_date.month
		year = current_date.year
		words_month = dict1[monthee]
		search = self.pool.get('indent.new.dashboard').search(cr,uid,[('month','=',words_month),('year','=',year)])
		if search == []:
			create = self.pool.get('indent.new.dashboard').create(cr,uid,{'month':words_month,'count':'1','year':year,'month_id':monthee})
		else:
			for var in self.pool.get('indent.new.dashboard').browse(cr,uid,search):
				count = var.count
				count1 = int(count) + 1
				create = self.pool.get('indent.new.dashboard').write(cr,uid,var.id,{'count':count1,})
		
		variable = self.pool.get('indent.new.dashboard').search(cr,uid,[('id','>',0)])
		if variable == []:
			print"" 
		else:
			for file1 in self.pool.get('indent.new.dashboard').browse(cr,uid,variable):
				self.pool.get('indent.new.dashboard').write(cr,uid,file1.id,{'count1':None,'count2':None})

			vart=self.pool.get('indent.new.dashboard').search(cr,uid,[('id','>',0)])
			for test in self.pool.get('indent.new.dashboard').browse(cr,uid,vart):
				current_date=date.today()
				month = current_date.month
				year = current_date.year
				previous_year = year - 1
				y = test.year
				count = test.count
				if y:
					if y == str(year):
						self.pool.get('indent.new.dashboard').write(cr,uid,test.id,{'check':True,'check1':False})
						self.pool.get('indent.new.dashboard').write(cr,uid,test.id,{'count2':count})
				
					if y == str(previous_year):
						self.pool.get('indent.new.dashboard').write(cr,uid,test.id,{'check1':True})
						self.pool.get('indent.new.dashboard').write(cr,uid,test.id,{'count1':count})

		
		for s in self.browse(cr,uid,ids):
			if not s.road_permit_no and s.permit_box:
				raise osv.except_osv(('Alert!'),('please Enter Road Permit Number'))
		self.write(cr,uid,ids,{'state':'progress'})
		
		# if not nosync_flag:
		#     self.sync_dispatch(cr,uid,ids,context=context)
		#     self.sync_dispatch_dashboard(cr,uid,ids,context=context)
		self.prepare_notes_update(cr,uid,ids,context=context) #feb11            
		self.state_update_dispatch(cr,uid,ids)

		delivery_schedule_id = self.pool.get('psd.sales.delivery.schedule').search(cr,uid,[('delivery_order_no','=',s.stock_transfer_no)])
		self.pool.get('psd.sales.delivery.schedule').write(cr,uid,delivery_schedule_id,{'state':'progress'})
			  
		return True

	def state_update_dispatch(self,cr,uid,ids):
		for k in self.browse(cr,uid,ids):
			state = k.state
			product = k.delivery_location.id
			for i in k.stock_transfer_product:
				self.pool.get('product.transfer').write(cr,uid,i.id,{'state':'progress',})
				search = self.pool.get('stock.picking').search(cr,uid,[('origin','=',k.origin),('id','=',k.stock_id)])
				for o in self.pool.get('stock.picking').browse(cr,uid,search):
					for search_id in o.move_lines:
						if search_id.product_id.id == i.product_name.id : 
							if i.cancel_box==True:
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'pending'})
							else:                                               
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'progress',})
		return True

	def nsd_delivery_done(self,cr,uid,ids,context=None):#.... This function is used for sales delivery
		nosync_flag=False
		for rec_line in self.browse(cr,uid,ids):
			if rec_line.create_bool:
				nosync_flag=rec_line.create_bool
		self.material_notes_update(cr,uid,ids,context=context)  
		self.write(cr,uid,ids,{'state':'done'})
		# if not nosync_flag:
		#     self.update_department_dispatch_delivery(cr,uid,ids)
		#     self.update_branch_state_delivery(cr,uid,ids)
		self.state_update_delivery(cr,uid,ids)
		return True

	def state_update_delivery(self,cr,uid,ids):#.. This function is used for sales delivery
		for k in self.browse(cr,uid,ids):
			state = k.state
			product = k.delivery_location.id
			check_status=False
			for i in k.stock_transfer_product:
				search = self.pool.get('stock.picking').search(cr,uid,[('origin','=',k.origin),('id','=',k.stock_id)])
				for o in self.pool.get('stock.picking').browse(cr,uid,search):
					for search_id in o.move_lines:
						if search_id.product_id == i.product_name:
							if i.cancel_box==True:
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'pending'})
							else:                                               
								self.pool.get('stock.move').write(cr,uid,search_id.id,{'state':'done',})
						
		return True

	def psd_create_indent(self,cr,uid,ids,context=None):
		res_indent_obj= self.pool.get('res.indent')
		indent_order_line_obj = self.pool.get('indent.order.line')
		psd_sales_product_order_obj =self.pool.get('psd.sales.product.order')
		psd_sales_delivery_schedule_obj = self.pool.get('psd.sales.delivery.schedule')
		scheduled_product_list_line_obj = self.pool.get('scheduled.product.list.line')
		product_transfer_obj = self.pool.get('product.transfer')
		customer_line_obj =self.pool.get('customer.line')
		o= self.browse(cr,uid,ids[0])
		main_delivery_id = o.id
		partner_id = o.partner_id.id
		customer_id =o.partner_id.ou_id
		stock_transfer_no = o.stock_transfer_no
		delivery_address = o.delivery_address
		billing_location = o.billing_location
		psd_sales_delivery_schedule_search = psd_sales_delivery_schedule_obj.search(cr,uid,[('delivery_order_no','=',stock_transfer_no)])
		scheduled_product_list_line_obj_search = scheduled_product_list_line_obj.search(cr,uid,[('scheduled_delivery_list_id','=',psd_sales_delivery_schedule_search[0])])
		scheduled_product_list_line_obj_browse = scheduled_product_list_line_obj.browse(cr,uid,scheduled_product_list_line_obj_search[0])
		sale_order_id = scheduled_product_list_line_obj_browse.sale_order_id.id
		delivery_location_id = psd_sales_product_order_obj.browse(cr,uid,sale_order_id).delivery_location_id.id
		billing_location_id = psd_sales_product_order_obj.browse(cr,uid,sale_order_id).billing_location_id.id
		delivery_customer_location_id = customer_line_obj.search(cr,uid,[('customer_address','=',delivery_location_id),('partner_id','=',partner_id)])
		billing_customer_location_id = customer_line_obj.search(cr,uid,[('customer_address','=',billing_location_id),('partner_id','=',partner_id)])
		delivery_pcof_id = customer_line_obj.browse(cr,uid,delivery_customer_location_id[0]).location_id
		billing_pcof_id = customer_line_obj.browse(cr,uid,billing_customer_location_id[0]).location_id
		values_delivery_order = {
								'delivery_id':main_delivery_id,
								'customer_name':partner_id,
								'customer_id': customer_id,
								'delivery_address_id': delivery_location_id,
								'billing_address_id': billing_location_id,
								'billing_location_id_char':billing_pcof_id,
								'delivery_location_id_char': delivery_pcof_id,
								'delivery_address': delivery_address,
								'billing_address_char': billing_location,
								'indent_type': 'external_delivery',
									}
		res_indent_create = res_indent_obj.create(cr,uid,values_delivery_order)
		product_transfer_search = product_transfer_obj.search(cr,uid,[('prod_id','=',main_delivery_id)])
		product_transfer_browse = product_transfer_obj.browse(cr,uid,product_transfer_search)
		for search_id in product_transfer_browse:
			search_state = search_id.state
			if search_state != 'cancel_order_qty':
				qty_indent = search_id.qty_indent
				price_unit = search_id.rate
				total = qty_indent * price_unit
				values_product_transfer={
									'product_id':search_id.product_name.id,
									'product_code': search_id.product_code,
									'product_category':search_id.product_category.id,
									'generic_id':search_id.generic_id.id,
									'product_uom_qty':search_id.qty_indent,
									'price_unit':search_id.rate,
									'product_uom':search_id.product_uom.id,
									#'total':search_id.amount,
									'total': total,
									'line_id': res_indent_create,
				}
				indent_order_line_obj.create(cr,uid,values_product_transfer)
		self.write(cr,uid,main_delivery_id,{'invisible_create_indent':True})
		models_data=self.pool.get('ir.model.data')
		form_view = models_data.get_object_reference(cr,uid,'sk','view_indent_form')
		return {
			'type':'ir.actions.act_window',
			'name': 'Indent',
			'view_type':'form',
			'view_mode':'form',
			'res_model':'res.indent',
			'view_id':form_view[1],
			'res_id': res_indent_create,
			'target':'current',
			'context': context
			}



stock_transfer()

class product_transfer(osv.osv):
	_inherit = "product.transfer"
	_columns={
		'product_uom': fields.many2one('product.uom','UOM'),
		'prepare_cancel':fields.boolean('prepare'), 
		'qty_indent': fields.integer('Indent Quantity'),
		'contained': fields.selection([
									('contained','cont'),
									('packed','packed in above')], 'Contained'),
		'local_rate':fields.float('Local Rate',digits=(4,4)),
		'batch': fields.many2one('res.batchnumber','Batch No'),
		'mrp': fields.float('MRP'),
		'batch_old': fields.many2one('res.batchnumber','Batch No'),
		'carton_no': fields.integer('No of Cartan'),
		'pmdc_price': fields.float('PM DC Price'),
		'cost_price': fields.float('Cost Price'),
		'order_by_group':fields.integer('Combined Carton'),
		'pakaging_details_manual':fields.boolean('Update Details'),
		'export_price': fields.float('Export Price'),
		'quantity_old': fields.integer('Quantity'),
		'carton_type':fields.many2one('carton.type.master','Carton Type',ondelete="cascade"),
		'dist_price': fields.float('Distributor Price'),
		'st_price': fields.float('ST Price'),
		'origin': fields.char('Indent Number', size=20),
		'cancel_box':fields.boolean('cancel'),
		'rate': fields.float('ST Rate'),
		'state': fields.selection([
									('draft','View Order'),
									('assigned','Packlist/Transport'),
									('confirmed','Ready To Dispatch'),
									('progress','In Transit'),
									('cancel','Cancelled'),
									('done','Done'),
									('cancel_order_qty','Cancelled')
								], 'State'),
		'dis_rate':fields.float('Distributed Rate'),
		'dis_sub_total':fields.float("Distribute SubTotal"),
		'total_taxable':fields.float("Amount with Tax"),
		'export_rate':fields.float('Export Rate'),
		'export_sub_total':fields.float('Export SubTotal'),
		'order_line': fields.one2many('indent.order.line','line_id','Order Lines'),
		'extended_warranty':fields.selection([
							('6','6 Months'),
							('12','12 Months'),
							('18','18 Months'),
							('24','24 Months'),
							('36','36 Months'),
							('48','48 Months'),
							('60','60 Months')],'Extended Warranty'),
		'discount':fields.float('Disc %'),
		'discounted_value':fields.float('Discounted Value'),
		'discounted_price':fields.float('Discounted Price'),
		'discounted_amount':fields.float(string='Disc Amt'),
		'tax_id':fields.many2one('account.tax','Tax %'),
		'tax_amount':fields.float('Tax Amt'),
		'total_amount':fields.float('Total Amount'),
		'is_track_equipment':fields.boolean('IS Track Equipment'),
		'is_qty_allocated':fields.integer('IS Qty Allocated'),
		'exp_date':fields.date('Expiry Date'),
		'godown':fields.many2one('res.company',string="Godown"),
		'act_id':fields.integer('Act Id'),
		'serial_number':fields.text('Serial Number',size=300),
		'specification':fields.char('Specification',size=500),
		'additional_amt':fields.float('Additional Amount'),
		# 'excise_invoice_no': fields.char('Excise Invoice No',size=200),
		# 'excise_invoice_date':fields.datetime('Excise Invoice Date'),
		# 'invoice_date':fields.datetime('Invoice Date'),
	}

	_defaults = {
		'dis_rate':0.0,
		'dis_sub_total':0.0,
		'total_taxable':0.0,
		'export_rate':0.0,
		'export_sub_total':0.0,
	}

	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(product_transfer, self).default_get(cr, uid, fields, context=context)
		#curr_id = self.pool.get('stock.transfer').browse(cr,uid,context.get('active_id'))
		# if curr_id.stock_transfer_product:
		# 	for prod_line in curr_id.stock_transfer_product:
		# 		product_list.append(prod_line.product_name.id)
		# if context.has_key('branch_name'):
		# 	res['godown'] = context.get('branch_name','')
		res['act_id']=context.get('active_id')
		return res


	def onchange_prod_name1(self,cr,uid,ids,product_name,act_id): 
		val={}
		manues_date=''
		available_quantity=''
		st_rate=''
		bat_no=''
		present_product=self.pool.get('stock.transfer').browse(cr,uid,act_id)
		for prod_line in present_product.stock_transfer_product:
			# if res.type_product == 'track_equipment' :
			# 	val['category_check'] = True	
			# else:
			# 	val['category_check'] = False
			# res=self.pool.get('product.product').browse(cr,uid,product_name)
			# red=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name)])
			# if res.type_product == 'track_equipment':
			# 	st_rate=0.0
			# 	search_product=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name)],order='manufacturing_date desc')
			# 	for ss in self.pool.get('res.batchnumber').browse(cr,uid,search_product):
			# 		manues_date=ss.manufacturing_date
			# else:
			# 	search_product=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name)],order='manufacturing_date desc')
			# 	for ss in self.pool.get('res.batchnumber').browse(cr,uid,search_product):
			# 		manues_date=ss.manufacturing_date
			# 		st_rate=ss.st
			# 		rate=ss.local_price
			# 		if ss.batch_no=='NA':
			# 			val['batch']=ss.id
			# 			val['batch_invisible']=ss.id
			# 			val['batch_char']='NA'
			# 		else:
			# 			val['batch']=None
			# 			val['batch_char']=''
			# 			val['quantity']=1
			# 		break
			if prod_line.product_name.id == product_name:
				val['godown']=prod_line.godown.id
				val['generic_id']=prod_line.generic_id.id
				val['product_category']=prod_line.product_category.id
				val['product_code']=str(prod_line.product_code)	
				val['product_uom']=prod_line.product_uom.id
				val['available_quantity']=prod_line.available_quantity
				val['qty_indent']=prod_line.qty_indent
				val['mfg_date']=prod_line.mfg_date
				val['available_quantity_invisible']=prod_line.available_quantity
				val['product_code_invisible']=str(prod_line.product_code)	
				val['product_uom_invisible']=prod_line.product_uom.id
				val['product_category_invisible']=prod_line.product_category.id
				val['batch']=prod_line.batch.id
				val['rate']=prod_line.rate
				val['rate_invisible']=prod_line.rate
				val['extended_warranty']=prod_line.extended_warranty
				val['state']=prod_line.state
				val['discount']=prod_line.discount
				val['tax_id']=prod_line.tax_id.id
				# val['carton_no']=prod_line.carton_no
				# val['carton_type']=prod_line.carton_type
				# val['state']=prod_line.state
				# # val['mfg_date']=manues_date
				#val['rate']=st_rate
				# val['amount']=0
		return {'value':val}




	def psd_onchange_quantity(self,cr,uid,ids,product_id,batch,quantity,available_quantity,rate,discount,tax_id):
		val={}
		lines=''
		for i in self.browse(cr,uid,ids):
			lines=i.id
		serial_add = []
		tag_add = []
		if quantity and rate:
			amt_tax = self.pool.get('account.tax').browse(cr,uid,tax_id).amount
			discount_value = quantity * rate * (discount/100)
			tax_amount = (quantity * rate - discount_value) * (amt_tax)
			new_total_amount = (quantity * rate)  + tax_amount - discount_value
			val['amount']=new_total_amount or 0.0
			val['tax_amount']=tax_amount or 0.0
			val['discounted_amount']=discount_value or 0.0

		if product_id and (quantity > available_quantity):
			raise osv.except_osv(('Alert!'),('Quantity to be Transferred should not be greater than available quantity.'))

		if product_id and batch and quantity :
			rec=self.pool.get('product.series').search(cr,uid,[('product_name','=',product_id),('batch','=',batch),('quantity','>',0),('reject','=',False)])
			count = 0
			for res in self.pool.get('product.series').browse(cr,uid,rec):
				count=count+1
				sr_no=count
				product_code=res.product_code
				product_name=res.product_name.id
				#product_category=res.product_category.id
				product_uom=res.product_uom.id
				batch=res.batch.id
				quantity1=res.quantity
				serial_no=res.id
				serial_check=res.serial_check
				active_id=res.active_id
				if count <= quantity:
					serial_add.append({
						'serie_line':lines,
						'sr_no':sr_no,
						'product_code':product_code,
						#'product_category':product_category,
						'product_uom':product_uom,
						'product_name':product_name,
						'batch':batch,
						'quantity':quantity1,
						'serial_no':serial_no,
						'serial_check':serial_check,
						'active_id':active_id,
						})
		if product_id and quantity :#for tag ID added by Sreejith 11 June
			rec1=self.pool.get('product.tag').search(cr,uid,[('product_id','=',product_id),('product_quantity','>',0)])
			count = 0
			for res1 in self.pool.get('product.tag').browse(cr,uid,rec1):
				count=count+1
				product_code=res1.product_code
				product_name=res1.product_id.id
				#product_category=res.product_category.id
				product_uom=res1.product_uom.id
				quantity1=res1.product_quantity
				tag_id=res1.id
				if count <= quantity:
					tag_add.append({
								'product_code':product_code,
								'product_uom':product_uom,
								'product_id':product_name,
								'product_quantity':quantity1,
								'tag_id':tag_id,
								})
		val['tag_line'] = tag_add
		val['serial_line'] = serial_add

		return {'value':val}


	def cancel_order(self,cr,uid,ids,context=None):
		var = '' 
		search = False
		process_flag=False
		self.material_notes_update(cr,uid,ids,context=context)  
		#self.sync_cancel_order(cr,uid,ids,context=context)
		for res in self.browse(cr,uid,ids):
			srch_ids=res.prod_id.id
			if srch_ids:
				chk_boolean=self.pool.get('stock.transfer').browse(cr,uid,srch_ids).create_bool
				# if not chk_boolean:
				#     self.sync_cancel_order(cr,uid,ids,context=context)
		self.indent_mgnt_notes_updatn(cr,uid,ids,context=context)
		for k in self.browse(cr,uid,ids):
			self.write(cr,uid,k.id,{'state':'cancel_order_qty','cancel_box':True})
			var = k.prod_id.id
			if k.state=='cancel_order_qty':
				search = self.pool.get('stock.transfer').search(cr,uid,[('id','=',k.prod_id.id)])
				for rec in self.pool.get('stock.transfer').browse(cr,uid,search):
				  search_id = self.pool.get('stock.picking').search(cr,uid,[('origin','=',rec.origin),('id','=',rec.stock_id)])
				  for o in self.pool.get('stock.picking').browse(cr,uid,search_id):
					for temp in rec.stock_transfer_product:
						if temp.cancel_box == True:
							res = self.pool.get('stock.move').search(cr,uid,[('product_id','=',k.product_name.id),('picking_id','=',search_id[0])])
							for part in self.pool.get('stock.move').browse(cr,uid,res):
									temp_id = self.pool.get("stock.move").write(cr,uid,part.id,{'state':'pending','check_process':False,'check_job':False})
		search_id = self.pool.get('product.transfer').search(cr,uid,[('prod_id','=',var)])
		search1 = self.pool.get('product.transfer').search(cr,uid,[('prod_id','=',var),('state','=','cancel_order_qty')])
		a=len(search1)
		b=len(search_id)
		###################################################### for Hide process Button  Start 11Jan########################3
		for k in self.browse(cr,uid,ids):
			var = k.prod_id.id
			if k.state=='cancel_order_qty':
				search = self.pool.get('stock.transfer').search(cr,uid,[('id','=',k.prod_id.id)])
				for rec in self.pool.get('stock.transfer').browse(cr,uid,search):
					search_id = self.pool.get('stock.picking').search(cr,uid,[('origin','=',rec.origin),('id','=',rec.stock_id)])
					for process_check_flag in self.pool.get('stock.picking').browse(cr,uid,search_id):
						if process_check_flag.move_lines:
							for move_lines_check in process_check_flag.move_lines:
								if not move_lines_check.check_process:
									process_flag=True
									break   
					# if not process_flag:
					#     self.pool.get('stock.picking').write(cr,uid,search_id[0],{'hide_process':True})
					# if process_flag:
					#     self.pool.get('stock.picking').write(cr,uid,search_id[0],{'date_exp_check':False,'exp_final_delivery_dt':None,'hide_check':True,'hide_cancel':True})
		###################################################### for Hide process Button  End 11Jan########################3
		sale_order_line_obj =  self.pool.get('psd.sales.product.order.lines')
		psd_sale_order_obj = self.pool.get('psd.sales.product.order')
		sale_order_id = psd_sale_order_obj.search(cr,uid,[('erp_order_no','=',k.prod_id.sale_order_no)])
		browse_rec = psd_sale_order_obj.browse(cr,uid,sale_order_id[0])

		search_line_rec_ids =sale_order_line_obj.search(cr,uid,[('psd_sales_product_order_lines_id','=',sale_order_id[0]),('product_name_id','=',k.product_name.id)]) 
		browse_line_rec = sale_order_line_obj.browse(cr,uid,search_line_rec_ids[0])
		sale_product_name = browse_line_rec.product_name_id.id
		if sale_product_name == k.product_name.id:
			sale_allocated_quantity = browse_line_rec.allocated_quantity
			allocated_quantity = k.qty_indent
			sale_write_allocated_quantity = sale_allocated_quantity-allocated_quantity
			sale_order_line_obj.write(cr,uid,browse_line_rec.id,{'allocated_quantity':sale_write_allocated_quantity})
		self._update_sale_order_status(cr,uid,ids)
		cur_rec = self.browse(cr,uid,ids[0])
		# if cur_rec.state=='cancel_order_qty':
		tax_amount_deduct = 0.0
		total_vat_deduct = 0.0
		total_amount = 0.0
		stock_transfer_obj = self.pool.get('stock.transfer')
		tax_line_obj = self.pool.get('tax')
		cur_rec_basic = round(cur_rec.rate * cur_rec.qty_indent - cur_rec.discounted_amount)
		cur_rec_tax_amount = cur_rec.tax_amount
		cur_rec_tax_name = cur_rec.tax_id.name
		cur_rec_tax_id = cur_rec.tax_id.id
		search = stock_transfer_obj.search(cr,uid,[('id','=',cur_rec.prod_id.id)])
		search_rec = stock_transfer_obj.browse(cr,uid,search[0])
		cur_rec_product_cost = round(search_rec.product_cost - cur_rec_basic)
		if search_rec.tax_one2many:
			for line in search_rec.tax_one2many:
				if line.name == str(cur_rec_tax_name) or line.id == cur_rec_tax_id:
					tax_amount_deduct = line.amount - cur_rec_tax_amount
					total_vat_deduct = search_rec.total_vat - cur_rec_tax_amount
					tax_line_obj.write(cr,uid,line.id,{'amount':tax_amount_deduct})
			total_amount = cur_rec_product_cost + total_vat_deduct
		stock_transfer_obj.write(cr,uid,search_rec.id,
								{'product_cost':cur_rec_product_cost,
								'total_vat':total_vat_deduct,
								'total_amount':total_amount})
		if a == b:
			self.pool.get('stock.transfer').write(cr,uid,[var],{'state':'cancel'})
			delivery_schedule_id = self.pool.get('psd.sales.delivery.schedule').search(cr,uid,[('delivery_order_no','=',k.prod_id.stock_transfer_no)])
			self.pool.get('psd.sales.delivery.schedule').write(cr,uid,delivery_schedule_id,{'state':'cancel'})
		view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'psd_warehouse', 'stock_transfer_order_management_form')
		view_id = view and view[1] or False
		return {
						'type': 'ir.actions.act_window',
						'view_mode': 'form',
						'view_type': 'form',
						'view_id':view_id,
						'res_id':int(search[0]),
						'res_model':'stock.transfer',
						'target':'current',
				}


	def _update_sale_order_status(self,cr,uid,ids,context=None):
		k = self.browse(cr,uid,ids[0])
		sale_order_line_obj =  self.pool.get('psd.sales.product.order.lines')
		psd_sale_order_obj = self.pool.get('psd.sales.product.order')
		sale_order_id = psd_sale_order_obj.search(cr,uid,[('erp_order_no','=',k.prod_id.sale_order_no)])
		browse_rec = psd_sale_order_obj.browse(cr,uid,sale_order_id[0])
		sale_order_list = []
		empty_allocated_qty=[]
		for sale_line in browse_rec.psd_sales_product_order_lines_ids:
			sale_order_list.append(1)
			if sale_line.allocated_quantity == 0:
				empty_allocated_qty.append(1)
		if len(sale_order_list) == len(empty_allocated_qty):
			psd_sale_order_obj.write(cr,uid,sale_order_id[0],{'state':'ordered'})
		#self.unlink(cr,uid,k.id)
		#self.pool.get('stock.transfer').write(cr,uid,k.prod_id.id,{'stock_transfer_product':(2,k.id)})
		return True

	def indent_mgnt_notes_updatn(self,cr,uid,ids,context=None):
		stock_id = ''
		for k in self.browse(cr,uid,ids):
			var = k.prod_id.id
			search = self.pool.get('stock.transfer').search(cr,uid,[('id','=',k.prod_id.id)])
			for st_id in self.pool.get('stock.transfer').browse(cr,uid,search):
				stock_id = st_id.stock_id
				pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',stock_id)])
				if st_id.notes_one2many:
						for notes in st_id.notes_one2many:
								notes_srh = self.pool.get('indent.remark').search(cr,uid,[('remark_field','=',notes.name),('user','=',notes.user_name),('source','=',notes.source.id),('date','=',notes.date),('remark','=',pick_srch[0])])
								if notes_srh:
									for test in notes_srh:
										self.pool.get('indent.remark').unlink(cr,uid,test)
								notes_line = {
											'remark':pick_srch[0],
											'user':notes.user_name if notes.user_name else '',
											'source':notes.source.id if notes.source else '',
											'date':notes.date,
											'remark_field':notes.name,
											 }
								self.pool.get('indent.remark').create(cr,uid,{'remark':pick_srch[0],
																			  'user':notes.user_name if notes.user_name else '',
																			  'source':notes.source.id if notes.source else '',
																			  'date':notes.date,
																			  'remark_field':notes.name,})
		return True

	def material_notes_update(self,cr,uid,ids,context=None):    
		for res in self.browse(cr,uid,ids):
			for rec in res.order_line:
				product_name=rec.product_id.name
				if rec.notes_one2many:
					for notes in rec.notes_one2many:
						self.pool.get('indent.comment.line').create(cr,uid,{'indent_id':res.id,'comment':product_name+' - '+notes.comment,'comment_date':notes.comment_date,'user_id':notes.user_id,'source':notes.source.id})
						

	def onchange_batch1(self,cr,uid,ids,batch,batch_char,batch_invisible,quantity_old,batch_old): 
		val={}
		if batch:
		   temp_batch=self.pool.get('stock.transfer').browse(cr,uid,batch)
		   result=self.pool.get('res.batchnumber').browse(cr,uid,batch)
		   
		   if batch_old :
			   result_old=self.pool.get('res.batchnumber').browse(cr,uid,batch_old)
			   if result.batch_no==result_old.batch_no :
					quantity_batch=result.qty+(quantity_old if quantity_old else 0)
			   else :
					quantity_batch=result.qty
		   else :
				quantity_batch=result.qty
		   val['batch_ok']=True
		   val['batch_char']=result.batch_no
		   val['available_quantity']=quantity_batch
		   val['available_quantity_invisible']=quantity_batch
		######################all Prices from res_batchnumber###########################
		   val['cost_price']=float(result.bom) if result.bom else 0.0
		   val['mrp']=result.mrp if result.mrp else 0.0
		   val['dist_price']=result.distributor if result.distributor else 0.0
		   val['export_price']=result.export_price if result.export_price else 0.0
		   val['pmdc_price']=result.pm_dc_price if result.pm_dc_price else 0.0
		  # val['st_price']= 0.0
		 #	  val['rate']= 0.0
		   val['mfg_date']=result.manufacturing_date if result.manufacturing_date else False
		################################################################################
		if not batch:
		   val['batch_ok']=False
		if not batch and batch_char=='NA':
			val['batch']=batch_invisible
		return {'value':val}

product_transfer()

class res_batchnumber(osv.osv):
	_inherit="res.batchnumber"
	_columns ={
		'pm_dc_price':fields.float('PM DC Price',size=8),
		'name': fields.many2one('product.product','Product Name',size=124,domain="[('type','in',('product','consu')),('product_state','!=','unusable'),('is_imported','=',True)]"),

	}
res_batchnumber()

class indent_new_dashboard(osv.osv):
	_name = "indent.new.dashboard"
	_order = "month_id"
	_columns = {
		'month':fields.char("Month",size=15),
		'year': fields.char('year',size=15),
		'count': fields.integer('Deliveries'),
		'check': fields.boolean('current year'), 
		'check1': fields.boolean('Previous year'),
		'count1':fields.integer("Previous Year"),
		'count2': fields.integer('Current year'),
		'month_id': fields.char('Month value',size=10),
		}

indent_new_dashboard()


# # ############### Added by nitin  18-8-2016
class transfer_series(osv.osv): 
	_inherit = "transfer.series"
	_rec_name="serial_no"
	_columns = {
		'serial_line_id':fields.many2one('stock.transfer','Serial ID'),
		'from_date':fields.datetime('From Date'),
		'due_date':fields.datetime('Due Date'),
		'duration':fields.integer('Warrantee Duration in Month'),
		}
# # ############### END #######################

class res_indent(osv.osv):
	_inherit="res.indent"
	_columns={
		'delivery_id': fields.many2one('stock.transfer','Delivery Order No'),
	}


	# def order_confirm(self, cr, uid, ids, context=None):
	# 	product_append = []
	# 	indent_append = []
	# 	product_transfer_obj = self.pool.get('product.transfer')
	# 	indent_order_line_obj = self.pool.get('indent.order.line')
	# 	stock_transfer_obj = self.pool.get('stock.transfer')
	# 	o= self.browse(cr,uid,ids[0])
	# 	main_id = o.id
	# 	delivery_id = o.delivery_id.id
	# 	search_product = product_transfer_obj.search(cr,uid,[('prod_id','=',delivery_id)])
	# 	browse_product = product_transfer_obj.browse(cr,uid,search_product)
	# 	for browse_id in browse_product:
	# 		product_name = browse_id.product_name.id
	# 		qty_indent = browse_id.qty_indent
	# 		delivery_product = [product_name,qty_indent]
	# 		product_append.append(delivery_product)
	# 	search_indent_product = indent_order_line_obj.search(cr,uid,[('line_id','=',main_id)])
	# 	browse_indent_product = indent_order_line_obj.browse(cr,uid,search_indent_product)
	# 	for browse_indent_id in browse_indent_product:
	# 		product_id = browse_indent_id.product_id.id
	# 		product_uom_qty = browse_indent_id.product_uom_qty
	# 		indent_product =[product_id,product_uom_qty]
	# 		indent_append.append(indent_product)
	# 	for list_values in product_append:
	# 		if list_values not in indent_append:
	# 			raise osv.except_osv(('Alert!'),('The Product lines does not matches with the Delivery order product lines')) 
	# 	#################### MOQ validation 13.07.16 ################
	# 	min_order_qty_check=''
	# 	for k in self.browse(cr,uid,ids):
	# 		for line in k.order_line:
	# 			if line.product_uom_qty < line.min_order_qty:
	# 				min_order_qty_check += line.product_id.name +" , "
	# 	if min_order_qty_check:
	# 		raise osv.except_osv(('Alert!'),('MOQ requirement does not meet for the Product(s):\n{}'.format(min_order_qty_check.rstrip(' , ')))) 
	# 	####################
			
	# 	obj_indent_order_line=self.pool.get('indent.order.line')
	# 	vals={}
	# 	vals.update({'state':'progress',})
	# 	indent_date= time.strftime("%Y-%m-%d %H:%M:%S")
	# 	self.material_notes_update(cr,uid,ids,context=context)
	# 	self.write(cr,uid,ids,{'order_date':indent_date})
	# 	monthee = ''
	# 	words_month = ''
	# 	year = ''
		
	# 	dict1 = {
	# 			1: 'January', 
	# 			2: 'February', 
	# 			3: 'March',
	# 			4:'April',
	# 			5:'May',
	# 			6:'June',
	# 			7:'July',
	# 			8:'August',
	# 			9:'September',
	# 			10:'October',
	# 			11:'November',
	# 			12:'December'
	# 		};
	# 	indent_no = ''
	# 	# current_date=date.today()
	# 	# year=current_date.strftime('%y')
	# 	today_date = datetime.now().date()
	# 	year=today_date.strftime('%y')
	# 	month =today_date.strftime('%m')
	# 	if int(month) > 3:
	# 		 year = int(year)+1
	# 	else:
	# 		 year=year
	# 	year=str(year)
	# 	branch_code=''
	# 	indent_req_id = ''
	# 	search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','res.indent')])
	# 	for i in self.pool.get('ir.sequence').browse(cr,uid,search):
	# 		if i.year != year or i.year==False:
	# 			self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year,'implementation':'no_gap','number_next':1})	
	# 	sequence_no=self.pool.get('ir.sequence').get(cr, uid, 'res.indent')
	# 	company_id=self._get_company(cr,uid,context=None)
	# 	for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
	# 		if comp_id.internal_branch_no:
	# 			branch_code=comp_id.internal_branch_no
	# 		if comp_id.indent_req_id:
	# 			indent_req_id=comp_id.indent_req_id
	# 	indent_no=branch_code + indent_req_id + str(year) + sequence_no
	# 	####################14jul16 create indent sequence###########3
	# 	search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','branch.create.indent')])
	# 	for i in self.pool.get('ir.sequence').browse(cr,uid,search):
	# 		if int(i.year) != int(year) or i.year==False:
	# 			self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year,'implementation':'no_gap','number_next':1})	
	# 	seq_no=self.pool.get('ir.sequence').get(cr, uid, 'branch.create.indent')
	# 	indent_seq=branch_code + str(year)+ seq_no
		
	# 	############################################################	
	# 	for o in self.browse(cr,uid,ids):
	# 		if not o.order_line:
	# 			raise osv.except_osv(('Alert!'),('You cannot proceed with indent order which has no order line.'))
	# 		for line in o.order_line:
	# 			obj_indent_order_line.write(cr,uid,[line.id],vals,context=context)
	# 			# super(indent_order_line,obj_indent_order_line).write(cr,uid,[line.id],vals,context=context)
	# 	for k in self.browse(cr,uid,ids):
	# 		for line in k.order_line:
	# 			self.pool.get('indent.order.line').write(cr,uid,[line.id],{'form_branch_id_seq':indent_seq,}) ###15jul16 create indent sequence###########3
	# 			if line.notes_one2many:
	# 				self.pool.get('indent.order.line').write(cr,uid,[line.id],{'msg_check_read':True,'msg_check_unread':False,})
	# 	date=datetime.now()
	# 	current_date=date.today()
	# 	monthee = current_date.month
	# 	year = current_date.year
	# 	words_month = dict1[monthee]
	# 	search = self.pool.get('indent.dashboard').search(cr,uid,[('month','=',words_month),('year','=',year)])
	# 	if search == []:
	# 		create = self.pool.get('indent.dashboard').create(cr,uid,{'month':words_month,'count':'1','year':year,'month_id':monthee})
	# 	else:
	# 		for var in self.pool.get('indent.dashboard').browse(cr,uid,search):
	# 			count = var.count
	# 			count1 = int(count) + 1
	# 			create = self.pool.get('indent.dashboard').write(cr,uid,var.id,{'count':count1,})
	# 	####################14jul16 create indent sequence###########3
	# 	self.write(cr, uid, ids, {'state': 'progress','monthee':words_month,'order_id':indent_no,'form_branch_id_seq':indent_seq})
	# 	if delivery_id:
	# 		stock_transfer_obj.write(cr,uid,delivery_id,{'psd_indent_number':indent_no,'psd_indent_date':date})
	# 	cr.execute('update res_indent set treecount1=(select count(*) from indent_order_line where line_id=%s) where id=%s',(tuple(ids),tuple(ids)))
	# 	context = dict(context, active_ids=ids, active_model=self._name)
	# 	partial_id=self.pool.get('stock.picking').create(cr, uid, {}, context=context)

	# 	#sync to indent dept starts from here:

	# 	self.sync_branch_order_confirm(cr,uid,ids,context=context)	
	# 	variable = self.pool.get('indent.dashboard').search(cr,uid,[('id','>',0)])
	# 	if variable == []:
	# 		print"" 
	# 	else:
	# 		for file1 in self.pool.get('indent.dashboard').browse(cr,uid,variable):
	# 			self.pool.get('indent.dashboard').write(cr,uid,file1.id,{'count1':None,'count2':None})

	# 		vart=self.pool.get('indent.dashboard').search(cr,uid,[('id','>',0)])
	# 		for test in self.pool.get('indent.dashboard').browse(cr,uid,vart):
	# 			date=datetime.now()
	# 			current_date=date.today()
	# 			month = current_date.month
	# 			year = current_date.year
	# 			previous_year = year - 1
	# 			y = test.year
	# 			count = test.count
	# 			if y:
	# 				if y == str(year):
	# 					self.pool.get('indent.dashboard').write(cr,uid,test.id,{'check':True,'check1':False})
	# 					self.pool.get('indent.dashboard').write(cr,uid,test.id,{'count2':count})
				
	# 				if y == str(previous_year):
	# 					self.pool.get('indent.dashboard').write(cr,uid,test.id,{'check1':True})
	# 					self.pool.get('indent.dashboard').write(cr,uid,test.id,{'count1':count})
	# 	tree_view=self.pool.get('ir.model.data').get_object_reference(cr,uid,'sk','view_indent_tree')
	# 	form_view=self.pool.get('ir.model.data').get_object_reference(cr,uid,'sk','view_indent_form')
	# 	return {
	# 		'name':'Indent',
	# 		'type':'ir.actions.act_window',
	# 		'view_type':'tree',
	# 		'view_mode':'tree',
	# 		'res_model':'res.indent',
	# 		'views':[
	# 			(tree_view and tree_view[1] or False, 'list'),
	# 			(form_view and form_view[1] or False, 'form'),
	# 		],
	# 		'target':'current'
	# 		}


	def onchange_delivery_id(self,cr,uid,ids,delivery_id):
		v={}
		append_id = []
		res_indent_obj= self.pool.get('res.indent')
		indent_order_line_obj = self.pool.get('indent.order.line')
		psd_sales_product_order_obj =self.pool.get('psd.sales.product.order')
		psd_sales_delivery_schedule_obj = self.pool.get('psd.sales.delivery.schedule')
		scheduled_product_list_line_obj = self.pool.get('scheduled.product.list.line')
		product_transfer_obj = self.pool.get('product.transfer')
		customer_line_obj =self.pool.get('customer.line')
		stock_transfer_obj = self.pool.get('stock.transfer')
		if delivery_id:
			browse_stock_transfer = stock_transfer_obj.browse(cr,uid,delivery_id)
			main_delivery_id = browse_stock_transfer.id
			partner_id = browse_stock_transfer.partner_id.id
			customer_id =browse_stock_transfer.partner_id.ou_id
			stock_transfer_no = browse_stock_transfer.stock_transfer_no
			delivery_address = browse_stock_transfer.delivery_address
			billing_location = browse_stock_transfer.billing_location
			psd_sales_delivery_schedule_search = psd_sales_delivery_schedule_obj.search(cr,uid,[('delivery_order_no','=',stock_transfer_no)])
			scheduled_product_list_line_obj_search = scheduled_product_list_line_obj.search(cr,uid,[('scheduled_delivery_list_id','=',psd_sales_delivery_schedule_search[0])])
			scheduled_product_list_line_obj_browse = scheduled_product_list_line_obj.browse(cr,uid,scheduled_product_list_line_obj_search[0])
			sale_order_id = scheduled_product_list_line_obj_browse.sale_order_id.id
			delivery_location_id = psd_sales_product_order_obj.browse(cr,uid,sale_order_id).delivery_location_id.id
			billing_location_id = psd_sales_product_order_obj.browse(cr,uid,sale_order_id).billing_location_id.id
			delivery_customer_location_id = customer_line_obj.search(cr,uid,[('customer_address','=',delivery_location_id),('partner_id','=',partner_id)])
			billing_customer_location_id = customer_line_obj.search(cr,uid,[('customer_address','=',billing_location_id),('partner_id','=',partner_id)])
			delivery_pcof_id = customer_line_obj.browse(cr,uid,delivery_customer_location_id[0]).location_id
			billing_pcof_id = customer_line_obj.browse(cr,uid,billing_customer_location_id[0]).location_id
			v['delivery_id'] = main_delivery_id
			v['customer_name'] = partner_id
			v['customer_id'] = customer_id
			v['delivery_address_id'] = delivery_location_id
			v['billing_address_id'] = billing_location_id
			v['billing_location_id_char'] = billing_pcof_id
			v['delivery_location_id_char'] = delivery_pcof_id
			v['delivery_address'] = delivery_address
			v['billing_address_char'] = billing_location
			product_transfer_search = product_transfer_obj.search(cr,uid,[('prod_id','=',main_delivery_id)])
			product_transfer_browse = product_transfer_obj.browse(cr,uid,product_transfer_search)
			for search_id in product_transfer_browse:
				search_state = search_id.state
				if search_state != 'cancel_order_qty':
					values_product_transfer={
										'product_id':search_id.product_name.id,
										'product_code': search_id.product_code,
										'product_category':search_id.product_category.id,
										'generic_id':search_id.generic_id.id,
										'product_uom_qty':search_id.qty_indent,
										'price_unit':search_id.rate,
										'product_uom':search_id.product_uom.id,
										'total':search_id.amount,
					}
					append_id.append(values_product_transfer)
			v['order_line'] = append_id
		return {'value':v}




		### ext_delivery_add_sync
	def indent_onchange_type(self,cr,uid,ids,indent_type,customer_name,branch_name):
		v = {}
		addr = ''
		var=[]
		var1=[]
		if customer_name:
			var1 = self.pool.get('res.partner.address').search(cr,uid,[('partner_id','=',customer_name),('primary_contact','=',True)])
			if var1:
				for r in self.pool.get('res.partner.address').read(cr,uid,var1,['location_name','premise_type','building','apartment',\
				'sub_area','street','tehsil','state_id','city_id','district','zip','landmark']):
					elems=[r['location_name'],r['apartment'],r['building'],r['sub_area'],r['street'],r['landmark'] ,r['city_id'] and r['city_id'][1],r['tehsil'] and r['tehsil'][1],r['district'] and r['district'][1],r['state_id'] and r['state_id'][1],r['zip']]
				addr = ', '.join(filter(bool, elems))

		var = self.pool.get('res.company').search(cr,uid,[('id','=',branch_name)])
		for res in self.pool.get('res.company').browse(cr,uid,var):
				apartment=res.apartment
				building=res.building
				street=res.street
				sub_area=res.sub_area
				landmark=res.landmark
				district=res.district
				tehsil=res.tehsil
				zip=res.zip
				state=res.state_id.name
				city=res.city_id.name1
				email=res.email
				address=[ apartment,building,street,landmark,sub_area,district,tehsil,city,state,zip,email ]
				company_address=', '.join(filter(bool,address))

		if indent_type=='sales_delivery':
			address=COMPANY._get_company_address(self,cr,uid,context=None)
			v['delivery_address']=address
			v['delivery_address_invisible']=address
			if customer_name:
				v['delivery_address']=addr
				v['delivery_address_invisible']=addr
		elif indent_type=='export_delivery':
			v['delivery_address']=''
			v['delivery_address_invisible']=''
			v['customer_id']=''
			v['delivery_address_id']=''
			v['billing_address_id']=''
			v['billing_location_id_char']=''
			v['delivery_location_id_char']=''
			v['billing_address_char']=''
		if customer_name:
			v['delivery_address']=addr
			v['delivery_address_invisible']=addr
		elif indent_type=='direct_sales':
			v['delivery_address']=''
			v['delivery_address_invisible']=''
			v['customer_id']=''
			v['delivery_address_id']=''
			v['billing_address_id']=''
			v['billing_location_id_char']=''
			v['delivery_location_id_char']=''
			v['billing_address_char']=''
		if branch_name:
			v['delivery_address']=company_address
			v['delivery_address_invisible']=company_address

		elif indent_type=='internal_delivery':	
			address=COMPANY._get_company_address(self,cr,uid,context=None)
			v['delivery_address']=address
			v['delivery_address_invisible']=address
		# elif indent_type=='external_delivery':
		# 	v['delivery_address']=''
		# 	v['delivery_address_invisible']=''
		# 	v['customer_id']=''
		# 	v['delivery_address_id']=''
		# 	v['billing_address_id']=''
		# 	v['billing_location_id_char']=''
		# 	v['delivery_location_id_char']=''
		# 	v['billing_address_char']=''
		# 	if customer_name:
		# 		cust_id=self.pool.get('res.partner').browse(cr,uid,customer_name).ou_id
		# 		v['customer_id']=cust_id
		return {'value':v}


	def create(self,cr,uid,vals,context=None):
		new_id = super(res_indent,self).create(cr,uid,vals,context=context)
		stock_transfer_obj = self.pool.get('stock.transfer')
		if vals.get('delivery_id'):
			delivery_id= vals.get('delivery_id')
			cr.execute('update stock_transfer set invisible_create_indent=True where id=%s',(delivery_id,))
		return new_id

	def write(self, cr, uid, ids, vals, context=None):
		stock_transfer_obj = self.pool.get('stock.transfer')
		read_id = self.read(cr,uid,ids,['delivery_id'])
		print "read_id",read_id,ids
		if isinstance(ids,int):
			main_id = ids
		else:
			main_id =ids[0]
		o = self.browse(cr,uid,main_id)
		delivery_id = o.delivery_id.id
		if delivery_id:
			if isinstance(read_id,list):
				previous_delivery_id = read_id[0].get('delivery_id')[0]
				print "previous_delivery_id",previous_delivery_id
				cr.execute('update stock_transfer set invisible_create_indent=False where id=%s',(previous_delivery_id,))
		new_id = super(res_indent,self).write(cr,uid,ids,vals,context=context)
		if isinstance(ids,int):
			main_id = ids
		else:
			main_id =ids[0]
		o = self.browse(cr,uid,main_id)
		delivery_id = o.delivery_id.id
		if delivery_id:
			cr.execute('update stock_transfer set invisible_create_indent=True where id=%s',(delivery_id,))
		return new_id
res_indent()

class branch_stock_transfer(osv.osv):
	_inherit ='branch.stock.transfer'
branch_stock_transfer()

class tax(osv.osv):
	_inherit="tax"
	_order="name desc"
	_columns={
		'stock_transfer_tax_id':fields.many2one('stock.transfer','Stock Transfer ID'),
	}
tax()
