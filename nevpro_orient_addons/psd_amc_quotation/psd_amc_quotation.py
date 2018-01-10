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
from tools.translate import _
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
import time



class job_history(osv.osv):
	_inherit = "job.history"
	_columns = {
		'service_order_id':fields.many2one('amc.sale.order','Service Order ID'),
	}

#############AMC Quotation and AMC Quoation Line
class amc_quotation(osv.osv):
	_inherit = "amc.quotation"
	_order = "id desc"

	def _get_user(self, cr, uid, context=None):		
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).id

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_datetime(self,cr,uid,context=None):
		return time.strftime("%Y-%m-%d %H:%M:%S")

	_columns = {
		'type':fields.char('Type',size=50),
		'company_id':fields.many2one('res.company','Company ID'),
		'partner_id':fields.many2one('res.partner','Partner ID'),
		'created_date':fields.datetime('Created Date'),
		# 'product_request_id':fields.many2one('product.request','Product Request ID'),	
		'name': fields.char('Customer/Company Name', size=256),
		'quotation_number': fields.char('Quotation Number',size=256),
		'quotation_date': fields.date('Quotation Date'),
		'parent_quotation_no':fields.char('Parent Quotation Number',size=100),
		'parent_quotation_date':fields.datetime("Parent Quotation Date"),
		'site_address': fields.many2one('res.partner.address','Site Address'),
		'contact_person': fields.char('Contact Person',size=256),
		'billing_address': fields.many2one('res.partner.address','Billing Address'),
		'service_type':fields.selection([('Annual Maintainance Contract','Annual Maintainance Contract'),
					('Repairs & Maintainance Charges','Repairs & Maintainance Charges'),
					('Commissioning & Installation Charges','Commissioning & Installation Charges'),
					('Exempted Service','Exempted Service'),
					('Maintainance or Repair Service','Maintainance or Repair Service')
					],'Service Type *'),
		'request_id':fields.char('Request ID',size=50),
		'pse': fields.many2one('hr.employee','PSE'),
		'state':fields.selection([('new','New'),
					('pending','Pending'),
					('quoted','Quoted'),
					('revised','Revised'),
					('lost','Lost'),
					('ordered','Ordered'),
					],'State'),
		'basic_charge': fields.float('Basic Charge'),
		'service_tax_14': fields.float('Service Tax'),
		'sb_cess_0_50': fields.float('S B Cess'),
		'kk_cess_0_50': fields.float('K K Cess'),
		'grand_total': fields.float('Grand Total'),
		'quotation_lost': fields.boolean('Quotation Lost'),
		'reason_for_lost': fields.text('Reason for Lost'),
		'amc_quotation_line_id': fields.one2many('amc.quotation.line','amc_quotation_id','Quotation Line'),
		'payment_term': fields.text('Payment Term'),
		'other_services': fields.text('Other Services'),
		'placement_of_spare_parts': fields.text('Placement of Spare Parts'),
		'response_time': fields.text('Response Time'),
		'notes': fields.text('Notes'),
		'classification': fields.selection([('Comprehensive','Comprehensive'),
					('Non Comprehensive','Non Comprehensive')],'Classification *'),
		'search_amc_quot_id':fields.many2one('search.amc.quotation','Search Service Quotation'),
		'tax_one2many':fields.one2many('tax','amc_quotn_id','Tax'),
		'quotation_history_id':fields.one2many('amc.quotation.history','quotation_history_lines_id','Quotation History'),
		'order_created':fields.boolean('Order Created'),
		'allow_logo':fields.boolean('Allow Logo'),
		'quotation_revised':fields.boolean('Quotn Revised'),
		'user_id':fields.many2one('res.users','User ID'),
		'notes_one2many': fields.one2many('amc.quotation.remarks','quotation_order_id','Notes'),
		'visits':fields.text('Visits',size=500),
		'products':fields.text('Products',size=5000),
		'skus':fields.text('SKU Name',size=5000),
		'territry_manager':fields.char('territry manager',size=200),
		'email':fields.char('Email',size=50),
		'mobile':fields.char('Mobile No.',size=20),
		'designation':fields.char('Designation',size=200),
	}

	_defaults={
		'state':'new',
		'quotation_lost':False,
		'company_id': _get_company,
		'created_date': _get_datetime,
		'user_id':_get_user,
		'type':'Service Quotation',
	}

	def onchange_billing_address(self,cr,uid,ids,billing_address):
		v={'contact_person':False}
		partner_address_obj = self.pool.get('res.partner.address')
		if billing_address:
			partner_rec = partner_address_obj.browse(cr,uid,billing_address)
			contact_person = str(partner_rec.first_name)+' '+str(partner_rec.last_name)
			v['contact_person'] = contact_person
		return {'value': v}

	def get_fiscalyear(self,cr,uid,ids,context=None):
		today = datetime.now().date()
		fisc_obj = self.pool.get('account.fiscalyear')
		search_fiscal = fisc_obj.search(cr,uid,[],context=None)
		code=False
		for rec in fisc_obj.browse(cr,uid,search_fiscal):
			if str(today)>=rec.date_start and str(today)<=rec.date_stop:
				code = rec.code
		if code:
			code = code[4:6]
		return code

	def round_off_grand_total(self,cr,uid,ids,grand_total,context=None):
		roundoff_grand_total = grand_total + 0.5
		s = str(roundoff_grand_total)
		dotStart = s.find('.')
		grand_total = int(s[:dotStart])
		return grand_total

	def psd_post_notes(self,cr,uid,ids,context=None): 
		date=datetime.now()
		for o in self.browse(cr,uid,ids):
			source = o.company_id.id
			user_name=self.pool.get('res.users').browse(cr, uid, uid).name
			if o.notes:
				self.pool.get('amc.quotation.remarks').create(cr,uid,{'quotation_order_id':o.id,
											'user_name':user_name,
											'date':date,
											'source':source,
											'name':'General - '+o.notes,
											'state':o.state})
			self.write(cr,uid,ids,{'notes':None})
		return True

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		amc_quotation_obj = self.pool.get('amc.quotation')
		res = super(amc_quotation, self).default_get(cr, uid, fields, context=context)
		picking_ids = context.get('active_ids', [])
		if not picking_ids or (not context.get('active_model') == 'amc.quotation') \
			or len(picking_ids) != 1:
			# Partial Picking Processing may only be done for one picking at a time
			return res
		picking_id, = picking_ids
		picking=amc_quotation_obj.browse(cr,uid,picking_id,context=context)
		state='new'
		if 'state' in fields:
			res.update(state=state)
		if 'name' in fields:			
			res.update(name=picking.name)
		if 'billing_address' in fields:
			res.update(billing_address=picking.billing_address.id) 
		if 'partner_id' in fields:
			res.update(partner_id=picking.partner_id.id)
		if 'site_address' in fields:
			res.update(site_address=picking.site_address.id)
		if 'request_id' in fields:
			res.update(request_id=picking.request_id)
		if 'service_type' in fields:
			res.update(service_type=picking.service_type)
		if 'customer_id' in fields:
			res.update(customer_id=picking.customer_id)
		if 'call_type' in fields:
			res.update(call_type=picking.call_type)
		if 'contact_person' in fields:
			res.update(contact_person=picking.contact_person)
		if 'amc_quotation_line_id' in fields:
			moves = [self._partial_move_for(cr, uid, m) for m in picking.amc_quotation_line_id]
			res.update(amc_quotation_line_id=moves)
		if 'tax_one2many' in fields:
			moves = [self._tax_for(cr, uid, m) for m in picking.tax_one2many]
			res.update(tax_one2many=moves)
		if 'quotation_number' in fields:
			res.update(parent_quotation_no=picking.quotation_number)
		if 'quotation_date' in fields:
			res.update(parent_quotation_date=picking.quotation_date)
		if 'pse' in fields:
			res.update(pse=picking.pse.id)
		if 'payment_term' in fields:
			res.update(payment_term=picking.payment_term)
		if 'other_services' in fields:
			res.update(other_services=picking.other_services)
		if 'placement_of_spare_parts' in fields:
			res.update(placement_of_spare_parts=picking.placement_of_spare_parts)
		if 'response_time' in fields:
			res.update(response_time=picking.response_time)
		if 'classification' in fields:
			res.update(classification=picking.classification)
		if 'service_tax_14' in fields:
			res.update(service_tax_14=picking.service_tax_14)
		if 'sb_cess_0_50' in fields:
			res.update(sb_cess_0_50=picking.sb_cess_0_50)
		if 'kk_cess_0_50' in fields:
			res.update(kk_cess_0_50=picking.kk_cess_0_50)
		if 'grand_total' in fields:
			res.update(grand_total=picking.grand_total)
		if 'quotation_lost' in fields:
			res.update(quotation_lost=picking.quotation_lost)
		if 'reason_for_lost' in fields:
			res.update(reason_for_lost=picking.reason_for_lost)
		if 'basic_charge' in fields:
			res.update(basic_charge=picking.basic_charge)
		res.update(quotation_history_id= [(0,0, {
								'quotation_date':picking.quotation_date,
								'quotation_number': picking.quotation_number,
								'quotation_amount': picking.grand_total,
								'previous_quotation_number':picking.parent_quotation_no,
				 })])
		return res

	def _partial_move_for(self, cr, uid, move):
		partial_move = {
			'product_generic_name': move.product_generic_name.id,
			'product_id' : move.product_id.id,
			'no_of_units': move.no_of_units,
			'rate_per_unit' : move.rate_per_unit,
			'no_of_visits':move.no_of_visits,
			'particulars_equipment' : move.particulars_equipment,
			'total_amount':move.total_amount
		}
		return partial_move

	def _tax_for(self, cr, uid, tax):
		tax_move = {
			'name': tax.name,
			'account_tax_id':tax.account_tax_id.id,
			'amount':tax.amount
		}
		return tax_move

	def search_record(self, cr, uid, ids, context=None):
		context = dict(context, active_ids=ids, active_model=self._name)
		res_create_id = self.pool.get("psd.amc.customer.search.wizard").create(cr, uid, {}, context=context)
		return {
		'view_type': 'form',
		'view_mode': 'form',
		'name': _('Search Customer'),
		'res_model': 'psd.amc.customer.search.wizard',
		'res_id': res_create_id,
		'type': 'ir.actions.act_window',
		'target': 'new',
		'context': context,
		'nodestroy': True,
		}

	def reload_amc_quotation(self, cr, uid, ids, context=None):
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_amc_quotation', 'view_amc_quotation_form')
		view_id = view and view[1] or False
		return {
			'name': _('Service Quotation'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'amc.quotation',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': ids[0],
		}

	def calculate(self, cr, uid, ids, context=None):
		add_total_amount = 0.0
		total_amount_value = 0.0
		service_tax_value = 0.0
		sb_tax_value = 0.0
		kk_tax_value = 0.0
		grand_total = 0.0
		no_of_visits = 0.0
		main_form_total_amount =tax_value=total_basic_amount= total_basic=0.0
		product_basic_rate = sgst_amount = cgst_amount = igst_amount = gst_total =sgst_rate=cgst_rate=igst_rate= 0.0
		tax_ids = []
		today_date =datetime.today().date()
		account_tax = self.pool.get('account.tax')
		amc_quotation_line_obj = self.pool.get('amc.quotation.line')
		amc_quotation_obj = self.pool.get('amc.quotation')
		crm_hist_obj = self.pool.get('sales.product.quotation.history')
		tax_line_obj = self.pool.get('tax')
		o = self.browse(cr,uid,ids[0])

		sgst_tax=account_tax.search(cr,uid,[('name','=','SGST')])[0]
		cgst_tax=account_tax.search(cr,uid,[('name','=','CGST')])[0]
		igst_tax=account_tax.search(cr,uid,[('name','=','IGST')])[0]

		company_id = o.company_id.state_id.id
		partner_location_addr = o.billing_address.state_id.id
		if not partner_location_addr:
			raise osv.except_osv(('Warning!'),('Please update the state of the customer'))
		print o.amc_quotation_line_id[0].no_of_visits
		for each in o.amc_quotation_line_id:
			if not each.no_of_visits:
		# if not o.amc_sale_order_line_id[0].no_of_visits:
				raise osv.except_osv(('Alert!'),('Specify the no. of visits!'))
		if not o.amc_quotation_line_id:
			raise osv.except_osv(_('Warning!'),_("No product lines defined!"))
		if not o.service_type:
			raise osv.except_osv(_('Warning!'),_("Please select 'Service Type'!"))
		if not o.classification:
			raise osv.except_osv(_('Warning!'),_("Please select 'Classification'!"))
		main_id = o.id
		search_values = amc_quotation_line_obj.search(cr,uid,[('amc_quotation_id','=',main_id)])
		browse_values = amc_quotation_line_obj.browse(cr,uid,search_values)
		if o.tax_one2many:
			for tax_line_id in o.tax_one2many:
				tax_ids.append(tax_line_id.id)    
			tax_line_obj.unlink(cr, uid, tax_ids, context=context)
		check_lines = []
		for browse_id in browse_values:
			generics=browse_id.product_generic_name.id
			print generics
			tax_rate =  browse_id.product_generic_name.product_tax.id
			tax_amount = browse_id.product_generic_name.product_tax.amount
			tax_name = browse_id.product_generic_name
			# print generics.product_tax.name
			# skus=browse_id.product_id.id
			# combo=tuple([generics]+[skus])
			combo = generics
			if combo in check_lines:
				raise osv.except_osv(('Invalid Combination!'),('Same Product lines are not allowed!'))
			else:
				check_lines.append(combo)
			print check_lines
			# check_lines.append(combo)
			# for irange in range(0,len(check_lines)):	
			# 		for jrange in range(irange+1,len(check_lines)):
			# 			if check_lines[irange][0]==check_lines[jrange][0] and check_lines[irange][1]==check_lines[jrange][1]:
			# 				raise osv.except_osv(('Invalid Combination!'),('Same Product lines are not allowed!'))
			if not browse_id.rate_per_unit or browse_id.rate_per_unit <= 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper rate per unit before calculating quotation value!"))
			if not browse_id.no_of_units or browse_id.no_of_units <= 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper no of units before calculating quotation value!"))
			no_of_visits = browse_id.no_of_visits
			no_of_visits = float(no_of_visits)
			total_basic = browse_id.rate_per_unit * browse_id.no_of_units
			total_basic_amount = total_basic * no_of_visits
			amc_quotation_line_obj.write(cr,uid,browse_id.id,{'total_basic':total_basic_amount})
			cr.commit()
			if company_id == partner_location_addr:
				print "aaaaaaaaaa"
				if o.service_type == 'exempted_service':
					# print "INTRA exempted"
					igst_amount = cgst_amount = sgst_amount = 0.0
				else:
					if tax_rate:
						# print product_basic_rate
						cgst_rate = sgst_rate = tax_amount/2
						cgst_amount = sgst_amount = (tax_amount * total_basic_amount)/2
						cgst_tax_name = account_tax.browse(cr,uid,cgst_tax).name
						sgst_tax_name = account_tax.browse(cr,uid,sgst_tax).name
						gst_total = cgst_amount + sgst_amount
						amc_quotation_line_obj.write(cr,uid,browse_id.id,{'sgst_rate':str(sgst_rate*100)+'%','cgst_rate':str(cgst_rate*100)+'%','sgst_amount':sgst_amount,'cgst_amount':cgst_amount,'tax_amount':gst_total,'total_amount':gst_total+total_basic_amount})
						cr.commit()

			else:
				print "bbbbbbbbbbb"
				if o.service_type == 'exempted_service':
					# print "INTRA exempted"
					igst_amount = cgst_amount = sgst_amount = 0.0
				else:
					if tax_rate:
						igst_rate = tax_amount
						igst_amount = tax_amount * total_basic_amount
						igst_tax_name = account_tax.browse(cr,uid,igst_tax).name
						gst_total = igst_amount
						amc_quotation_line_obj.write(cr,uid,browse_id.id,{'igst_rate':str(igst_rate*100)+'%','igst_amount':igst_amount,'tax_amount':gst_total,'total_amount':gst_total+total_basic_amount})
						cr.commit()
		cr.execute('select sum(sgst_amount) from amc_quotation_line where amc_quotation_id = %s',(browse_id.amc_quotation_id.id,))
		sgst_amount = cr.fetchone()[0]
		cr.execute('select sum(cgst_amount) from amc_quotation_line where amc_quotation_id = %s',(browse_id.amc_quotation_id.id,))
		cgst_amount = cr.fetchone()[0]
		cr.execute('select sum(igst_amount) from amc_quotation_line where amc_quotation_id = %s',(browse_id.amc_quotation_id.id,))
		igst_amount = cr.fetchone()[0]
		cr.execute('select sum(total_basic) from amc_quotation_line where amc_quotation_id = %s',(browse_id.amc_quotation_id.id,))
		total_basic = cr.fetchone()[0]
		total_basic = round(total_basic)
		cr.execute('select sum(total_amount) from amc_quotation_line where amc_quotation_id = %s',(browse_id.amc_quotation_id.id,))
		total_amount = cr.fetchone()[0]
		total_amount = round(total_amount)
		amc_quotation_obj.write(cr,uid,o.id,{'basic_charge':total_basic,'grand_total':total_amount})
		cr.commit()
		print sgst_amount,'sssssssssssssssssssssss'
		# tax_amount = cgst_amount + sgst_amount + igst_amount

		if company_id == partner_location_addr:
			tax_line_obj.create(cr,uid,{'amc_quotn_id':int(ids[0]),'account_tax_id':cgst_tax,'name':cgst_tax_name,'amount':cgst_amount},context=None)	
			cr.commit()
			tax_line_obj.create(cr,uid,{'amc_quotn_id':int(ids[0]),'account_tax_id':sgst_tax,'name':sgst_tax_name,'amount':sgst_amount},context=None)					
			cr.commit()
		else:
			tax_line_obj.create(cr,uid,{'amc_quotn_id':int(ids[0]),'account_tax_id':igst_tax,'name':igst_tax_name,'amount':igst_amount},context=None)
			cr.commit()

		if o.parent_quotation_no and o.parent_quotation_date:
			search_amc_qut = self.search(cr,uid,[('quotation_number','=',str(o.parent_quotation_no))])
			self.write(cr,uid,search_amc_qut[0],{'state':'revised'},context=None)
			qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(o.partner_id.id)),('amc_quotation_id','=',int(search_amc_qut[0]))])
			if qutn_id:
				crm_hist_obj.write(cr,uid,qutn_id[0],{'status':'revised'},context=None)
		self.write(cr,uid,main_id,{'state':'pending'})
		product_list = []
		for line in o.amc_quotation_line_id:
			if not line.product_generic_name.name in product_list:
				product_list.append(line.product_generic_name.name)
		products =', '.join(map(str, product_list))
		self.write(cr,uid,ids,{'skus':products},context=None)
		qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(o.partner_id.id)),('amc_quotation_id','=',int(o.id))])
		if qutn_id:
			for m in qutn_id:
				crm_hist_obj.unlink(cr,uid,m,context=None)
		crm_history_values = { 	'partner_id':o.partner_id.id,
								'amc_quotation_id':o.id,
								'quotation_id':o.quotation_number,
								'quotation_date':o.quotation_date,
								'quotation_type':o.type,
								'sku_name':products,
								'request_id':o.request_id,
								'quotation_amount':grand_total,
								'status':'pending',
								'pse':o.pse.concate_name,
							}
		crm_hist_obj.create(cr,uid,crm_history_values,context=None)
		return True

	def print_quotation(self, cr, uid, ids, context=None):
		emp_obj =  self.pool.get('hr.employee')
		user_obj = self.pool.get('res.users')
		search_branch_mgr = emp_obj.search(cr,uid,[('role','=','branch_manager')])
		employee = emp_obj.browse(cr,uid,search_branch_mgr[1])
		emp_name = employee.concate_name
		emp_designation = employee.emp_role.value
		search_user = user_obj.search(cr,uid,[('name','ilike',emp_name),('emp_code','=',employee.emp_code)])
		user = user_obj.browse(cr,uid,search_user[0])
		self.write(cr,uid,ids,{'territry_manager':emp_name,'email':user.user_email,'mobile':user.mobile,'designation':emp_designation})
		datas = {
				 'model': 'amc.quotation',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'amc.quotation', 'datas': datas, 'nodestroy': True}


	def cancel_quotation(self,cr,uid,ids,context=None):
		product_request_obj = self.pool.get('product.request')
		request_search_amc_obj = self.pool.get('search.amc.quotation')
		quotation_line_obj = self.pool.get('amc.quotation.line')
		history_line_obj = self.pool.get('amc.quotation.history')
		request_search_sales_obj = self.pool.get('request.search.sales')
		tax_line_obj = self.pool.get('tax')
		o = self.browse(cr,uid,ids[0])
		search_product_request = product_request_obj.search(cr,uid,[('product_request_id','=',str(o.request_id))])
		line_ids = []
		history_ids = []
		tax_ids = []
		if o.amc_quotation_line_id:
			for line_id in o.amc_quotation_line_id:
				line_ids.append(line_id.id)    
			quotation_line_obj.unlink(cr, uid, line_ids, context=context)
		if o.quotation_history_id:
			for line_id in o.quotation_history_id:
				history_ids.append(line_id.id)    
			history_line_obj.unlink(cr, uid, history_ids, context=context)
		if o.tax_one2many:
			for tax_id in o.tax_one2many:
				tax_ids.append(tax_id.id)    
			tax_line_obj.unlink(cr, uid, tax_ids, context=context)
		if o.parent_quotation_no:
			search_amc_qut = self.search(cr,uid,[('quotation_number','=',str(o.parent_quotation_no)),('id','>','0')])
			self.write(cr,uid,search_amc_qut[0],{'quotation_revised':False},context=None)
			self.unlink(cr,uid,ids[0],context=context)
			request_search_amc_id = request_search_amc_obj.create(cr,uid,
				{
					'search_amc_quot_lines': [(6, 0, search_amc_qut)],
				},context=context)
			models_data=self.pool.get('ir.model.data')
			form_id = models_data.get_object_reference(cr, uid, 'psd_amc_quotation', 'search_amc_quotation_form')
			return {
				   'name':'Search Service Quotation',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'search.amc.quotation',
				   'res_id':int(request_search_amc_id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   }
		else:
			product_request_obj.write(cr,uid,search_product_request[0],{'psd_sales_entry':False})
			self.unlink(cr,uid,ids[0],context=context)
			request_search_sales_id = request_search_sales_obj.create(cr,uid,
				{
					'product_request_ids': [(6, 0, search_product_request)],
					'pushed': False
				},context=context)
			models_data=self.pool.get('ir.model.data')
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'request_search_sales_form')
			return {
				   'name':'Requests',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'request.search.sales',
				   'res_id':int(request_search_sales_id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   } 

	def generate_quotation(self,cr,uid,ids,context=None):
		crm_hist_obj = self.pool.get('sales.product.quotation.history')
		seq = self.pool.get('ir.sequence').get(cr, uid, 'amc.quotation')
		self.calculate(cr,uid,ids,context=context)
		o = self.browse(cr,uid,ids[0])
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
		# code = self.get_fiscalyear(cr,uid,ids,context=None)
		quotation_number = str(o.company_id.pcof_key)+str(o.company_id.service_quotation_id)+financial_year+str(seq)
		self.write(cr,uid,ids,{'state':'quoted','quotation_date':datetime.today(),'quotation_number':quotation_number})
		product_list = []
		generic_name = []
		for line in o.amc_quotation_line_id:
			self.pool.get('amc.quotation.line').write(cr,uid,line.id,{'quotation_no_ref':quotation_number},context=None)
			if not line.product_generic_name.name in product_list:
				product_list.append(line.product_generic_name.name)
			# if not line.product_generic_name.name in generic_name:
			# 	generic_name.append(line.product_generic_name.name)
		products =', '.join(map(str, product_list))
		generic = ''
		if len(generic_name) > 1:
			last_item = generic_name[-1]
			second_last = generic_name[-2]
			for x in generic_name:
				if x == last_item:
					generic = generic+'& ' + x
				elif x == second_last:
					generic =  generic + x +' '
				else:
					generic =  generic + x +', '
		elif len(generic_name) == 1:
			generic = generic_name[0]
		self.write(cr,uid,ids,{'products':generic,'skus':products})
		qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(o.partner_id.id)),('amc_quotation_id','=',int(o.id))])
		if qutn_id:
			crm_history_values = { 	
									'quotation_id':quotation_number,
									'quotation_date':datetime.today(),
									'sku_name':products,
									'quotation_amount':o.grand_total,
									'status':'quoted',
									'pse':o.pse.concate_name,
								}
			crm_hist_obj.write(cr,uid,qutn_id[0],crm_history_values,context=None)
		else:
			crm_history_values = { 	'partner_id':o.partner_id.id,
									'amc_quotation_id':o.id,
									'quotation_id':quotation_number,
									'quotation_date':datetime.today(),
									'quotation_type':o.type,
									'sku_name':products,
									'request_id':o.request_id,
									'quotation_amount':o.grand_total,
									'status':'quoted',
									'pse':o.pse.concate_name,
								}
			crm_hist_obj.create(cr,uid,crm_history_values,context=None)
		return True

	def revise_quotation(self,cr,uid,ids,context=None):
		if context is None: context = {}
		context = dict(context, active_ids=ids, active_model=self._name)
		res_create_id = self.pool.get("amc.quotation").create(cr, uid, {}, context=context)
		self.write(cr,uid,ids,{'quotation_revised':True})
		return {
			'name':_("Revise Service Quotation"),
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'amc.quotation',
			'res_id': res_create_id,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'domain': '[]',
			'context': context,
		}

	# def print_quotation(self,cr,uid,ids,context=None):
	# 	return True

	def lost(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'lost'})
		crm_hist_obj = self.pool.get('sales.product.quotation.history')
		product_req_obj = self.pool.get('product.request')
		crm_lead_obj = self.pool.get('crm.lead')
		rec = self.browse(cr,uid,ids[0])
		qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(rec.partner_id.id)),('amc_quotation_id','=',int(rec.id))])
		req_id = product_req_obj.search(cr,uid,[('partner_id','=',int(rec.partner_id.id)),('product_request_id','=',rec.request_id)])
		if qutn_id:			
			crm_history_values = { 
									'quotation_amount':rec.grand_total,
									'status':'lost',
								}
			crm_hist_obj.write(cr,uid,qutn_id[0],crm_history_values,context=None)
		if req_id:
			product_req_obj.write(cr,uid,req_id[0],{'state':'closed'})
			crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', str(rec.request_id))], context=context)
			for crm_id in crm_ids:
				crm_lead_obj.write(cr, uid, crm_id, {'state':'closed'}, context=context)
		return True

	def generate_contract(self,cr,uid,ids,context=None):
		amc_sale_order_obj = self.pool.get('amc.sale.order')
		amc_sale_order_line_obj = self.pool.get('amc.sale.order.line')
		amc_quotation_line_obj = self.pool.get('amc.quotation.line')
		tax_line_obj = self.pool.get('tax')
		o = self.browse(cr,uid,ids[0])
		main_id = o.id
		main_form_values={
		'customer_name':o.name,
		'partner_id':o.partner_id.id,
		# 'product_request_id':o.product_request_id.id,
		'request_id':o.request_id,
		'quotation_number':o.quotation_number,
		'quotation_date':o.quotation_date,
		'amc_quotn_id':o.id,
		'site_address': o.site_address.id,
		'contact_person': o.contact_person,
		'billing_address': o.billing_address.id,
		'pse': o.pse.id,
		'state': 'pending',
		'basic_charge':o.basic_charge,
		'service_tax_14': o.service_tax_14,
		'sb_cess_0_50': o.sb_cess_0_50,
		'kk_cess_0_50': o.kk_cess_0_50,
		'grand_total': o.grand_total,
		'payment_term':o.payment_term,
		'other_services':o.other_services,
		'placement_of_spare_parts':o.placement_of_spare_parts,
		'response_time':o.response_time,
		'visits':o.visits,
		'notes': o.notes,
		'service_type':o.service_type,
		'classification':o.classification,
		}
		res_sale_order_create = amc_sale_order_obj.create(cr,uid,main_form_values)
		quotation_line_obj_search = amc_quotation_line_obj.search(cr,uid,[('amc_quotation_id','=',main_id)])
		quotation_line_obj_browse = amc_quotation_line_obj.browse(cr,uid,quotation_line_obj_search)
		generic_name = []
		for line_id in quotation_line_obj_browse:
			if not line_id.product_generic_name.name in generic_name:
				generic_name.append(line_id.product_generic_name.name)
			line_values ={
			'amc_sale_order_id': res_sale_order_create,
			'no_of_units': line_id.no_of_units,
			'rate_per_unit':line_id.rate_per_unit,
			'particulars_equipment': line_id.particulars_equipment,
			'no_of_visits': line_id.no_of_visits,
			'product_code': line_id.product_code,
			'product_generic_name': line_id.product_generic_name.id,
			# 'product_id': line_id.product_id.id,
			'total_amount': line_id.total_amount,
			'cgst_rate':line_id.cgst_rate,
			'sgst_rate':line_id.sgst_rate,
			'igst_rate':line_id.igst_rate,
			'cgst_amount':line_id.cgst_amount,
			'sgst_amount':line_id.sgst_amount,
			'igst_amount':line_id.igst_amount,
			'tax_amount':line_id.tax_amount,
			}
			res_sale_order_line_create= amc_sale_order_line_obj.create(cr,uid,line_values)
		generic =', '.join(map(str, generic_name))
		amc_sale_order_obj.write(cr,uid,int(res_sale_order_create),{'products':generic})
		if o.tax_one2many:
			for tax_line_id in o.tax_one2many:  
				tax_line_values ={
				'amc_so_id': int(res_sale_order_create),
				'name': tax_line_id.name,
				'account_tax_id':tax_line_id.account_tax_id.id,
				'amount':tax_line_id.amount,
				}
				res_tax_order_line_create= tax_line_obj.create(cr,uid,tax_line_values)
		self.write(cr,uid,main_id,{'order_created':True})
		return {
				'view_type': 'form',
				'view_mode': 'form',
				'name': _('Service Order'),
				'res_model': 'amc.sale.order',
				'res_id': res_sale_order_create,
				'type': 'ir.actions.act_window',
				'target': 'current',
				'context': context,
				'nodestroy': True,
		}

amc_quotation()


class amc_quotation_line(osv.osv):
	_name = 'amc.quotation.line'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),	
		'amc_quotation_id':fields.many2one('amc.quotation','AMC Quotation ID',ondelete='cascade'),
		'no_of_visits':fields.selection([('1','Single Service'),('2','2 Visits'),('3','3 Visits'),('4','4 Visits'),('6','6 Visits'),('12','12 Visits')],'No of Visits'),
		'quotation_no_ref':fields.char('Quotation Ref',size=50),
		'product_code': fields.char('Product Code', size=256),
		'particulars_equipment': fields.char('Particulars of the Equipment', size=256),
		'rate_per_unit':fields.float('Rate P.U.'),
		'no_of_units':fields.integer('No of Units'),
		#'product_name': fields.many2one('product.group','Product Name'),
		# 'product_generic_name': fields.many2one('product.generic.name','Product Name'),
		'product_generic_name':fields.many2one('product.product','Product Name'),
		# 'product_id':fields.many2one('product.product','SKU Name'),
		'total_basic':fields.float('Total Basic Amont'),
		'cgst_rate':fields.char('CSGT Rate',size=10),
		'sgst_rate':fields.char('SGST Rate',size=10),
		'igst_rate':fields.char('IGST Rate',size=10),
		'cgst_amount':fields.float('CGST Amount'),
		'sgst_amount':fields.float('SGST Amount'),
		'igst_amount':fields.float('IGST Amount'),
		'tax_amount':fields.float('Tax Amount'),
		'total_amount':fields.float('Total Amount'),
	}

	_defaults = {
		'company_id': _get_company
	}

	def onchange_product_id(self,cr,uid,ids,product_id):
		v={}
		if product_id:
			product_browse_id = self.pool.get('product.product').browse(cr,uid,product_id)
			v['product_code'] = product_browse_id.default_code
		return {'value': v}

amc_quotation_line()


class amc_quotation_history(osv.osv):
	_name = 'amc.quotation.history'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'quotation_history_lines_id': fields.many2one('amc.quotation','Quoation History ID'),
		'quotation_date': fields.date('Quotation Date'),
		'quotation_number': fields.char('Quotation Number',size=50),
		'quotation_amount': fields.float('Quotation Amount'),
		'previous_quotation_number': fields.char('Previous Quotation Number',size=50),
	}

	_defaults = {
		'company_id': _get_company
	}
	
amc_quotation_history()

###########AMC Sale Order 
class amc_sale_order(osv.osv):
	_name="amc.sale.order"
	_order = "id desc"
	_rec_name = 'customer_name'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_corp_company(self, cr, uid, context=None):
		res = False
		company_obj = self.pool.get('res.company')
		search_corp = company_obj.search(cr,uid,[('branch_type','=','corp_office')])
		if search_corp:
			res = search_corp[0]
		return res

	def _get_regd_company(self, cr, uid, context=None):
		res = False
		company_obj = self.pool.get('res.company')
		search_regd = company_obj.search(cr,uid,[('branch_type','=','regd_office')])
		if search_regd:
			res = search_regd[0]
		return res

	def _get_datetime(self,cr,uid,context=None):
		return time.strftime("%Y-%m-%d %H:%M:%S")

	def _get_user(self, cr, uid, context=None):		
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).id

	def name_get(self, cr, uid, ids, context={}):
		# if not len(ids):
		#     return []
		res=[]
		for emp in self.browse(cr, uid, ids,context=context):
			 res.append((emp.id, emp.order_number))     
		return res
		
	def onchange_no_of_months(self,cr,uid,ids,no_of_months,order_period_from,order_period_to):
		v={}
		if not no_of_months and order_period_from:
			v['order_period_to'] = order_period_from
		if no_of_months and order_period_from:
			date_period_to = datetime.strptime(order_period_from, '%Y-%m-%d')+ relativedelta(months=no_of_months,days=-1)	
			v['order_period_to'] = str(date_period_to.date())
		return {'value': v}

	def onchange_order_period_from(self,cr,uid,ids,order_period_from,order_period_to,no_of_months):
		v = {}
		date=datetime.now().date()
		no_of_months=int(no_of_months)
		start_date = datetime.strptime(order_period_from, "%Y-%m-%d").date()
		today_date = datetime.strptime(str(date), "%Y-%m-%d").date()
		total_amount = 0.0
		if no_of_months == 0:
			v['order_period_to'] = order_period_from
		if start_date < today_date:
			total_cal =  (today_date - start_date).days
			'''if total_cal > 15 and total_amount < 50000:
				raise osv.except_osv(('Alert!'),('Please Select Proper Start Date'))'''
		
		if order_period_from:
			if start_date < date:
			 	#raise osv.except_osv(('Alert!'),('Please Select Proper Date'))
				print "SSSS"
			else:
				if order_period_from and no_of_months>0:
						renewal_period = no_of_months - 2
						end_dt= self.add_months(order_period_from,no_of_months)
						renewal=self.add_months(order_period_from,renewal_period)
                                                exp_date = (datetime.strptime(str(end_dt)[0:10],'%Y-%m-%d')) + relativedelta( days =- 1) #contract
                                                v['order_period_from']=str(exp_date.date())
                                                date1=datetime.strptime(contract_start_date, '%Y-%m-%d').date()
                                                contract_s_date=date1.strftime("%d/%m/%Y")
                                                date2=exp_date.date()
                                                contract_e_date=date2.strftime("%d/%m/%Y")

                                                date_concate = contract_s_date + ' - ' + contract_e_date #abdulrahim26April
                                                v['order_period_to'] = date_concate
		return {'value': v}


	def onchange_order_period_to(self,cr,uid,ids,order_period_from,order_period_to,no_of_months):
		v = {}
		if order_period_from and order_period_to:
			start_date = datetime.strptime(order_period_from, "%Y-%m-%d")
			end_date =  datetime.strptime(order_period_to, "%Y-%m-%d")
			month_start=start_date.strftime("%m")
			year_start = start_date.strftime("%Y")
			month_end=end_date.strftime("%m")
			year_end = end_date.strftime("%Y")
			relative_data= (int(year_end) - int(year_start)) * 12 + (int(month_end) -int(month_start))
			total_days = (end_date - start_date).days
			v['no_of_days'] = total_days
		return {'value': v} 


	def _show_record(self, cr, uid, ids, field_names, arg=None, context=None):
		result = {}
		if not ids: return result
		for id in ids:
			result.setdefault(id, [])
		for res in self.browse(cr,uid,ids):
			if res.order_number:
				scheduled_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('service_order_no','=',res.order_number)])
				for r in scheduled_id:
					result[res.id].append(r)
			return result

	_columns = {
		'type':fields.char('Type',size=50),
		'company_id':fields.many2one('res.company','Company ID'),
		'corp_office_id':fields.many2one('res.company','Corporate Office'),
		'regd_office_id':fields.many2one('res.company','Registered Office'),
		'partner_id':fields.many2one('res.partner','Partner ID'),
		'amc_quotn_id':fields.many2one('amc.quotation'),
		'created_date':fields.datetime('Created Date'),
		# 'product_request_id':fields.many2one('product.request','Product Request ID'),
		'customer_name': fields.char('Customer/Company Name', size=256),
		'quotation_number': fields.char('Quotation Number',size=256),
		'quotation_date': fields.date('Quotation Date'),
		'order_number': fields.char('Serivce Order Number',size=256),
		'order_date': fields.date('Service Order Date'),
		'parent_order_no': fields.char('Parent Order Number',size=256),
		'parent_order_date': fields.date('Parent Order Date'),
		'wo_no': fields.char('W. O. Number',size=256),
		'wo_date': fields.date('W. O. Date'),
		'no_of_months':fields.integer('No. of Months'),
		'no_of_days':fields.integer('No. of Days'),
		'order_period_from': fields.date('Order Period From'),
		'order_period_to': fields.date('Order Period To'),
		'site_address': fields.many2one('res.partner.address','Site Address'),
		'contact_person': fields.char('Contact Person',size=256),
		'billing_address': fields.many2one('res.partner.address','Billing Address'),
		'pse': fields.many2one('hr.employee','PSE'),
		'service_type':fields.selection([('Annual Maintainance Contract','Annual Maintainance Contract'),
					('Repairs & Maintainance Charges','Repairs & Maintainance Charges'),
					('Commissioning & Installation Charges','Commissioning & Installation Charges'),
					('Exempted Service','Exempted Service'),
					('Maintainance or Repair Service','Maintainance or Repair Service')
					],'Service Type *'),
		'request_id':fields.char('Request ID',size=50),
		'state':fields.selection([('new','New'),
					('pending','Pending'),
					('ordered','Ordered'),
					('renewed','Renewed'),
					('cancelled','Cancelled')
					],'State'),
		'basic_charge': fields.float('Basic Charge'),
		'service_tax_14': fields.float('Service Tax'),
		'sb_cess_0_50': fields.float('S B Cess'),
		'kk_cess_0_50': fields.float('K K Cess'),
		'grand_total': fields.float('Grand Total'),
		'cancel_order': fields.boolean('Cancel Order'),
		'reason_for_cancellation': fields.text('Reason for Cancellation',size=500),
		'amc_sale_order_line_id': fields.one2many('amc.sale.order.line','amc_sale_order_id','Quotation Line'),
		'payment_term': fields.text('Payment Term'),
		'other_services': fields.text('Other Services'),
		'placement_of_spare_parts': fields.text('Placement of Spare Parts'),
		'response_time': fields.text('Response Time'),
		'notes': fields.text('Notes'),
		'classification': fields.selection([('Comprehensive','Comprehensive'),
					('Non Comprehensive','Non Comprehensive')],'Classification *'),
		'search_amc_order_id':fields.many2one('search.amc.order','Search Service Order'),
		'tax_one2many':fields.one2many('tax','amc_so_id','Tax'),
		'no_of_payment':fields.integer('No Of Payment'),
		'billing_term':fields.char('Special Instruction',size=124),
		'invoice_date':fields.date('Invoice Date'),
		'amount':fields.float('Amount',size=26),
		'amc_invoice_line':fields.one2many('amc.invoice.line','amc_inv_line','contract_invoice_line'),
		'user_id':fields.many2one('res.users','User ID'),
		'notes_one2many': fields.one2many('amc.order.remarks','amc_order_id','Notes'),
		'visits':fields.text('Visits',size=500),
		'products':fields.text('Products'),
		'skus':fields.text('SKU Name',size=5000),
		'allow_logo':fields.boolean('Allow Logo'),
		'territry_manager':fields.char('territry manager',size=200),
		'email':fields.char('Email',size=50),
		'mobile':fields.char('Mobile No.',size=20),
		'designation':fields.char('Designation',size=200),	
        'ops_record_noncomplaint': fields.function(_show_record,relation='res.scheduledjobs',type='one2many',method=True,string='Operations job history'),
		#'ops_record_complaint': fields.function(_show_record_complaint,relation='res.scheduledjobs',string='Operations job history',type='one2many',method=True),
		'invoiced':fields.boolean('Invoiced'),
		'service_invoice_id':fields.one2many('invoice.adhoc.master','service_order_id','Invoice'),
		'order_renewed':fields.boolean('Order Renewed'),
		'invoiced_amount':fields.float('Invoiced Amount'),
		'history_line':fields.one2many('job.history','service_order_id','Job History'),
	}

	_defaults={
		'state':'new',
		'company_id': _get_company,
		'corp_office_id': _get_corp_company,
		'regd_office_id': _get_regd_company,
		'created_date': _get_datetime,
		'user_id':_get_user,
		'type':'Service Order',
	}

	def onchange_billing_address(self,cr,uid,ids,billing_address):
		v={'contact_person':False}
		partner_address_obj = self.pool.get('res.partner.address')
		if billing_address:
			partner_rec = partner_address_obj.browse(cr,uid,billing_address)
			contact_person = str(partner_rec.first_name)+' '+str(partner_rec.last_name)
			v['contact_person'] = contact_person
		return {'value': v}

	def get_fiscalyear(self,cr,uid,ids,context=None):
		today = datetime.now().date()
		fisc_obj = self.pool.get('account.fiscalyear')
		search_fiscal = fisc_obj.search(cr,uid,[],context=None)
		code=False
		for rec in fisc_obj.browse(cr,uid,search_fiscal):
			if str(today)>=rec.date_start and str(today)<=rec.date_stop:
				code = rec.code
		if code:
			code = code[4:6]
		return code

	def round_off_grand_total(self,cr,uid,ids,grand_total,context=None):
		roundoff_grand_total = grand_total + 0.5
		s = str(roundoff_grand_total)
		dotStart = s.find('.')
		grand_total = int(s[:dotStart])
		return grand_total

	def search_record(self, cr, uid, ids, context=None):
		context = dict(context, active_ids=ids, active_model=self._name)
		res_create_id = self.pool.get("psd.amc.sale.customer.search.wizard").create(cr, uid, {}, context=context)
		return {
		'view_type': 'form',
		'view_mode': 'form',
		'name': _('Search Customer'),
		'res_model': 'psd.amc.sale.customer.search.wizard',
		'res_id': res_create_id,
		'type': 'ir.actions.act_window',
		'target': 'new',
		'context': context,
		'nodestroy': True,
		}

	def renew_service_order(self,cr,uid,ids,context=None):
		res = self.browse(cr,uid,ids[0])
		if context is None: context = {}
		context = dict(context, active_ids=ids, active_model=self._name)
		today=datetime.now().date()
		contract_end_date = (datetime.strptime(res.order_period_to[0:10],'%Y-%m-%d')).date()
		exp_date = (datetime.strptime(res.order_period_to[0:10],'%Y-%m-%d')) + relativedelta( months =- 2)
		if today <= exp_date.date() and res.no_of_months!=0:
			raise osv.except_osv(('Alert!'),('Service order cannot be renewed before 2 months of order period.'))
		if today > exp_date.date() and res.no_of_months!=0:
			raise osv.except_osv(('Alert!'),('Service order cannot be renewed now!'))
		res_create_id = self.pool.get("amc.sale.order").create(cr, uid, {}, context=context)
		self.write(cr,uid,ids,{'order_renewed':True})
		return {
			'name':_("Renewed Service Order"),
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'amc.sale.order',
			'res_id': res_create_id,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'domain': '[]',
			'context': context,
		}

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		amc_order_obj = self.pool.get('amc.sale.order')
		res = super(amc_sale_order, self).default_get(cr, uid, fields, context=context)
		picking_ids = context.get('active_ids', [])
		if not picking_ids or (not context.get('active_model') == 'amc.sale.order') \
			or len(picking_ids) != 1:
			return res
		picking_id, = picking_ids
		picking=amc_order_obj.browse(cr,uid,picking_id,context=context)
		state='new'
		if 'state' in fields:
			res.update(state=state)
		if 'customer_name' in fields:			
			res.update(customer_name=picking.customer_name)
		if 'billing_address' in fields:
			res.update(billing_address=picking.billing_address.id) 
		if 'partner_id' in fields:
			res.update(partner_id=picking.partner_id.id)
		if 'site_address' in fields:
			res.update(site_address=picking.site_address.id)
		if 'request_id' in fields:
			res.update(request_id=picking.request_id)
		if 'service_type' in fields:
			res.update(service_type=picking.service_type)
		if 'customer_id' in fields:
			res.update(customer_id=picking.customer_id)
		if 'call_type' in fields:
			res.update(call_type=picking.call_type)
		if 'contact_person' in fields:
			res.update(contact_person=picking.contact_person)
		if 'amc_sale_order_line_id' in fields:
			moves = [self._partial_move_for(cr, uid, m) for m in picking.amc_sale_order_line_id]
			res.update(amc_sale_order_line_id=moves)
		if 'tax_one2many' in fields:
			moves = [self._tax_for(cr, uid, m) for m in picking.tax_one2many]
			res.update(tax_one2many=moves)
		if 'order_number' in fields:
			res.update(parent_order_no=picking.order_number)
		if 'order_date' in fields:
			res.update(parent_order_date=picking.order_date)
		if 'wo_no' in fields:
			res.update(wo_no=picking.wo_no)
		if 'wo_date' in fields:
			res.update(wo_date=picking.wo_date)
		if 'quotation_number' in fields:
			res.update(quotation_number=picking.quotation_number)
		if 'quotation_date' in fields:
			res.update(quotation_date=picking.quotation_date)
		if 'order_period_to' in fields:
			order_period_from = picking.order_period_to
			order_period_from = datetime.strptime(order_period_from, "%Y-%m-%d") + timedelta(days=1)
			res.update(order_period_from=order_period_from)
		if 'no_of_months' in fields:
			res.update(no_of_months=picking.no_of_months)
		if 'no_of_months' and 'order_period_to' in fields:
			order_period_from = picking.order_period_to
			order_period_from = datetime.strptime(order_period_from, "%Y-%m-%d") + timedelta(days=1)
			if picking.no_of_months == 0:
				res.update(order_period_to=order_period_from)
			else:
				order_period_to = order_period_from + relativedelta(months=picking.no_of_months,days=-1)
				res.update(order_period_to=order_period_to)  		
		if 'pse' in fields:
			res.update(pse=picking.pse.id)
		if 'payment_term' in fields:
			res.update(payment_term=picking.payment_term)
		if 'other_services' in fields:
			res.update(other_services=picking.other_services)
		if 'placement_of_spare_parts' in fields:
			res.update(placement_of_spare_parts=picking.placement_of_spare_parts)
		if 'response_time' in fields:
			res.update(response_time=picking.response_time)
		if 'classification' in fields:
			res.update(classification=picking.classification)
		if 'service_tax_14' in fields:
			res.update(service_tax_14=picking.service_tax_14)
		if 'sb_cess_0_50' in fields:
			res.update(sb_cess_0_50=picking.sb_cess_0_50)
		if 'kk_cess_0_50' in fields:
			res.update(kk_cess_0_50=picking.kk_cess_0_50)
		if 'grand_total' in fields:
			res.update(grand_total=picking.grand_total)
		if 'quotation_lost' in fields:
			res.update(quotation_lost=picking.quotation_lost)
		if 'reason_for_lost' in fields:
			res.update(reason_for_lost=picking.reason_for_lost)
		if 'basic_charge' in fields:
			res.update(basic_charge=picking.basic_charge)
		return res

	def _partial_move_for(self, cr, uid, move):
		partial_move = {
			'product_generic_name': move.product_generic_name.id,
			'product_id' : move.product_id.id,
			'no_of_units': move.no_of_units,
			'rate_per_unit' : move.rate_per_unit,
			'no_of_visits':move.no_of_visits,
			'particulars_equipment' : move.particulars_equipment,
			'total_amount':move.total_amount
		}
		return partial_move

	def _tax_for(self, cr, uid, tax):
		tax_move = {
			'name': tax.name,
			'amount':tax.amount,
			'account_tax_id':tax.account_tax_id.id
		}
		return tax_move

	def reload_amc_order(self, cr, uid, ids, context=None):
		self.write(cr,uid,ids,{'invoiced':False})
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_amc_quotation', 'view_amc_sale_order_form')
		view_id = view and view[1] or False
		return {
			'name': _('Service Order'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'amc.sale.order',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': ids[0],
		}

	def cancel(self,cr,uid,ids,context=None):
		crm_order_hist_obj = self.pool.get('psd.order.crm.history')
		amc_inv_line_obj = self.pool.get('amc.invoice.line')
		res_scheduledjobs_obj = self.pool.get('res.scheduledjobs')
		self.write(cr,uid,ids,{'state':'cancelled'})
		rec=self.browse(cr,uid,ids[0])
		if rec.amc_invoice_line:
			for line in rec.amc_invoice_line:
				amc_inv_line_obj.write(cr,uid,line.id,{'state':'cancelled'})
		qutn_id = crm_order_hist_obj.search(cr,uid,[('partner_id','=',int(rec.partner_id.id)),('service_order_id','=',int(rec.id))])
		if qutn_id:			
			crm_order_hist_obj.write(cr,uid,qutn_id[0],{'status':'cancelled'},context=None)
		job_ids = res_scheduledjobs_obj.search(cr,uid,[('service_order_no','=',rec.order_number),('state','!=','job_done')])
		if job_ids:
			for job in res_scheduledjobs_obj.browse(cr,uid,job_ids):
				self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'state':'cancel'})
		return True

	def psd_post_notes(self,cr,uid,ids,context=None): 
		date=datetime.now()
		for o in self.browse(cr,uid,ids):
			source = o.company_id.id
			user_name=self.pool.get('res.users').browse(cr, uid, uid).name
			if o.notes:
				self.pool.get('amc.order.remarks').create(cr,uid,{'amc_order_id':o.id,
											'user_name':user_name,
											'date':date,
											'source':source,
											'name':'General - '+o.notes,
											'state':o.state})
				self.write(cr,uid,ids,{'notes':None})
	# ########## End ##################
		return True

	def cancel_order(self,cr,uid,ids,context=None):
		product_request_obj = self.pool.get('product.request')
		request_search_sales_obj = self.pool.get('request.search.sales')
		sales_line_obj = self.pool.get('amc.sale.order.line')
		tax_line_obj = self.pool.get('tax')
		models_data=self.pool.get('ir.model.data')
		o = self.browse(cr,uid,ids[0])
		search_product_request = product_request_obj.search(cr,uid,[('product_request_id','=',str(o.request_id))])
		line_ids = []
		tax_ids = []
		if o.amc_sale_order_line_id:
			for line_id in o.amc_sale_order_line_id:
				line_ids.append(line_id.id)    
			sales_line_obj.unlink(cr, uid, line_ids, context=context)
		if o.tax_one2many:
			for tax_id in o.tax_one2many:
				tax_ids.append(tax_id.id)    
			tax_line_obj.unlink(cr, uid, tax_ids, context=context)
		if o.parent_order_no:
			search_amc_order = self.search(cr,uid,[('order_number','=',str(o.parent_order_no)),('id','>','0')])
			self.write(cr,uid,search_amc_order[0],{'order_renewed':False},context=None)
			self.unlink(cr,uid,ids[0],context=context)
			models_data=self.pool.get('ir.model.data')
			form_id = models_data.get_object_reference(cr, uid, 'psd_amc_quotation', 'view_amc_sale_order_form')
			return {
				   'name':'Service Order',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'amc.sale.order',
				   'res_id':search_amc_order[0],
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   }
		else:
			self.unlink(cr,uid,ids[0],context=context)
			self.pool.get('amc.quotation').write(cr,uid,o.amc_quotn_id.id,{'order_created':False},context=None)
			form_id = models_data.get_object_reference(cr, uid, 'psd_amc_quotation', 'view_amc_quotation_form')
			return {
				   'name':'Service Quotation',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'amc.quotation',
				   'res_id':int(o.amc_quotn_id.id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   }

	def calculate(self, cr, uid, ids, context=None):
		add_total_amount = 0.0
		total_amount_value = 0.0
		service_tax_value = 0.0
		sb_tax_value = 0.0
		kk_tax_value = 0.0
		total_basic = total_basic_amount = 0.0
		grand_total = 0.0
		no_of_visits = 0.0
		tax_ids = []
		today_date =datetime.today().date()
		account_tax = self.pool.get('account.tax')
		amc_sale_order_obj = self.pool.get('amc.sale.order')
		amc_sale_order_line_obj = self.pool.get('amc.sale.order.line')
		tax_line_obj = self.pool.get('tax')
		crm_order_hist_obj = self.pool.get('psd.order.crm.history')

		sgst_tax=account_tax.search(cr,uid,[('name','=','SGST')])[0]
		cgst_tax=account_tax.search(cr,uid,[('name','=','CGST')])[0]
		igst_tax=account_tax.search(cr,uid,[('name','=','IGST')])[0]

		o = self.browse(cr,uid,ids[0])
		company_id = o.company_id.state_id.id
		partner_location_addr = o.billing_address.state_id.id
		if not partner_location_addr:
			raise osv.except_osv(('Warning!'),('Please update the state of the custommer'))
		# if o.quotation_number:
		# 	raise osv.except_osv(_('Alert!'),_("Tax is generated already. \n Kindly generate the order"))
		if not o.amc_sale_order_line_id:
			raise osv.except_osv(_('Warning!'),_("No product lines defined!"))
		for each in o.amc_sale_order_line_id:
			if not each.no_of_visits:
				raise osv.except_osv(('Alert!'),('Specify the no. of visits!'))
		if not o.service_type:
			raise osv.except_osv(_('Warning!'),_("Please select 'Service Type'!"))
		if not o.classification:
			raise osv.except_osv(_('Warning!'),_("Please select 'Classification'!"))

		# if o.order_period_from > o.order_period_to:
		# 	raise osv.except_osv(_('Warning!'),_("Order Period From cannot be greater than Order Period To'!"))
		if not o.classification:
			raise osv.except_osv(_('Warning!'),_("Please select 'Classification'!"))
		if o.tax_one2many:
			for tax_line_id in o.tax_one2many:
				tax_ids.append(tax_line_id.id)    
			tax_line_obj.unlink(cr, uid, tax_ids, context=context)
		main_id = o.id
		search_values = amc_sale_order_line_obj.search(cr,uid,[('amc_sale_order_id','=',main_id)])
		browse_values = amc_sale_order_line_obj.browse(cr,uid,search_values)
		check_lines = []
		for browse_id in browse_values:
			generics=browse_id.product_generic_name.id
			tax_rate =  browse_id.product_generic_name.product_tax.id
			tax_amount = browse_id.product_generic_name.product_tax.amount
			tax_name = browse_id.product_generic_name
			# skus=browse_id.product_id.id
			# combo=tuple([generics]+[skus])
			combo = generics
			if combo in check_lines:
				raise osv.except_osv(('Invalid Combination!'),('Same Product lines are not allowed!'))
			else:
				check_lines.append(combo)
			print check_lines
			# check_lines.append(combo)
			# for irange in range(0,len(check_lines)):	
			# 		for jrange in range(irange+1,len(check_lines)):
			# 			if check_lines[irange][0]==check_lines[jrange][0] and check_lines[irange][1]==check_lines[jrange][1]:
			# 				raise osv.except_osv(('Invalid Combination!'),('Same Product lines are not allowed!'))
			if not browse_id.rate_per_unit or browse_id.rate_per_unit <= 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper rate per unit before calculating quotation value!"))
			if not browse_id.no_of_units or browse_id.no_of_units <= 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper no of units before calculating quotation value!"))
			# total_basic = browse_id.rate_per_unit * browse_id.no_of_units
			# total_basic_amount = total_basic * browse_id.no_of_visits
			no_of_visits = browse_id.no_of_visits
			no_of_visits = float(no_of_visits)
			total_basic = browse_id.rate_per_unit * browse_id.no_of_units
			total_basic_amount = total_basic * no_of_visits
			amc_sale_order_line_obj.write(cr,uid,browse_id.id,{'total_basic':total_basic_amount})
			cr.commit()
			if company_id == partner_location_addr:
				print "aaaaaaaaaa"
				if o.service_type == 'exempted_service':
					# print "INTRA exempted"
					igst_amount = cgst_amount = sgst_amount = 0.0
				else:
					if tax_rate:
						# print product_basic_rate
						cgst_rate = sgst_rate = tax_amount/2
						cgst_amount = sgst_amount = (tax_amount * total_basic_amount)/2
						cgst_tax_name = account_tax.browse(cr,uid,cgst_tax).name
						sgst_tax_name = account_tax.browse(cr,uid,sgst_tax).name
						gst_total = cgst_amount + sgst_amount
						amc_sale_order_line_obj.write(cr,uid,browse_id.id,{'sgst_rate':str(sgst_rate*100)+'%','cgst_rate':str(cgst_rate*100)+'%','sgst_amount':sgst_amount,'cgst_amount':cgst_amount,'tax_amount':gst_total,'total_amount':gst_total+total_basic_amount})
						cr.commit()

			else:
				print "bbbbbbbbbbb"
				if o.service_type == 'exempted_service':
					# print "INTRA exempted"
					igst_amount = cgst_amount = sgst_amount = 0.0
				else:
					if tax_rate:
						igst_rate = tax_amount
						igst_amount = tax_amount * total_basic_amount
						igst_tax_name = account_tax.browse(cr,uid,igst_tax).name
						gst_total = igst_amount
						amc_sale_order_line_obj.write(cr,uid,browse_id.id,{'igst_rate':str(igst_rate*100)+'%','igst_amount':igst_amount,'tax_amount':gst_total,'total_amount':gst_total+total_basic_amount})
						cr.commit()
		cr.execute('select sum(sgst_amount) from amc_sale_order_line where amc_sale_order_id = %s',(browse_id.amc_sale_order_id.id,))
		sgst_amount = cr.fetchone()[0]
		cr.execute('select sum(cgst_amount) from amc_sale_order_line where amc_sale_order_id = %s',(browse_id.amc_sale_order_id.id,))
		cgst_amount = cr.fetchone()[0]
		cr.execute('select sum(igst_amount) from amc_sale_order_line where amc_sale_order_id = %s',(browse_id.amc_sale_order_id.id,))
		igst_amount = cr.fetchone()[0]
		cr.execute('select sum(total_basic) from amc_sale_order_line where amc_sale_order_id = %s',(browse_id.amc_sale_order_id.id,))
		total_basic = cr.fetchone()[0]
		total_basic = round(total_basic)
		cr.execute('select sum(total_amount) from amc_sale_order_line where amc_sale_order_id = %s',(browse_id.amc_sale_order_id.id,))
		total_amount = cr.fetchone()[0]
		total_amount = round(total_amount)
		amc_sale_order_obj.write(cr,uid,o.id,{'basic_charge':total_basic,'grand_total':total_amount})
		cr.commit()
		print sgst_amount,'sssssssssssssssssssssss'
		# tax_amount = cgst_amount + sgst_amount + igst_amount

		if company_id == partner_location_addr:
			tax_line_obj.create(cr,uid,{'amc_so_id':int(ids[0]),'account_tax_id':cgst_tax,'name':cgst_tax_name,'amount':cgst_amount},context=None)	
			cr.commit()
			tax_line_obj.create(cr,uid,{'amc_so_id':int(ids[0]),'account_tax_id':sgst_tax,'name':sgst_tax_name,'amount':sgst_amount},context=None)					
			cr.commit()
		else:
			tax_line_obj.create(cr,uid,{'amc_so_id':int(ids[0]),'account_tax_id':igst_tax,'name':igst_tax_name,'amount':igst_amount},context=None)
			cr.commit()
		# 	total_amount_value = browse_id.rate_per_unit * browse_id.no_of_units
		# 	add_total_amount+=total_amount_value
		# 	amc_sale_order_line_obj.write(cr,uid,browse_id.id,{'total_amount':total_amount_value})
		# if o.service_type == 'exempted_service':
		# 	service_tax_value = 0.0
		# 	sb_tax_value = 0.0
		# 	kk_tax_value = 0.0
		# 	grand_total = service_tax_value+sb_tax_value+kk_tax_value+add_total_amount
		# else:
		# 	# account_service_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','service_tax')])
		# 	# if account_service_tax:
		# 	# 	service_tax14 = account_tax.browse(cr,uid,account_service_tax[0]).amount
		# 	# 	service_tax_name = account_tax.browse(cr,uid,account_service_tax[0]).name
		# 	# 	service_tax_value = add_total_amount * service_tax14
		# 	# 	service_tax_value = self.round_off_grand_total(cr,uid,ids,service_tax_value,context=None)
		# 	# account_sb_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','swachh_bharat_service')])
		# 	# if account_sb_tax:
		# 	# 	sb_cess_0_05 = account_tax.browse(cr,uid,account_sb_tax[0]).amount
		# 	# 	sb_cess_name = account_tax.browse(cr,uid,account_sb_tax[0]).name
		# 	# 	sb_tax_value = add_total_amount * sb_cess_0_05
		# 	# 	sb_tax_value = self.round_off_grand_total(cr,uid,ids,sb_tax_value,context=None)
		# 	# account_kk_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','krishi_kalyan_service')])
		# 	# if account_kk_tax:
		# 	# 	kk_cess_0_50 = account_tax.browse(cr,uid,account_kk_tax[0]).amount
		# 	# 	kk_cess_name = account_tax.browse(cr,uid,account_kk_tax[0]).name
		# 	# 	kk_tax_value = add_total_amount * kk_cess_0_50
		# 	# 	kk_tax_value = self.round_off_grand_total(cr,uid,ids,kk_tax_value,context=None)	
		# 	# grand_total = service_tax_value+sb_tax_value+kk_tax_value+add_total_amount
			prod = self.pool.get('product.product').browse(cr,uid,generics)
			product_tax = prod.product_tax.id
			account_gst_tax = account_tax.search(cr,uid,[('id','=',product_tax)])[0]
			print account_gst_tax
			if account_gst_tax:
				amount = account_tax.browse(cr,uid,account_gst_tax).amount
				name = account_tax.browse(cr,uid,account_gst_tax).name
				gst_tax_value = add_total_amount * amount
				gst_tax_value = self.round_off_grand_total(cr,uid,ids,gst_tax_value,context=None)
				print amount,name,add_total_amount,gst_tax_value
			grand_total = gst_tax_value+add_total_amount
		grand_total = self.round_off_grand_total(cr,uid,ids,grand_total,context=None)
		# tax_line_obj.create(cr,uid,{'amc_so_id':int(ids[0]),'account_tax_id':account_gst_tax,'name':name,'amount':gst_tax_value},context=None)
		self.write(cr,uid,main_id,{'state':'pending'})
		if o.parent_order_no:
			search_parent_order = self.search(cr,uid,[('order_number','=',str(o.parent_order_no))])
			if search_parent_order:
				searched_order = self.browse(cr,uid,search_parent_order[0])
				if searched_order.order_renewed:
					self.write(cr,uid,int(searched_order.id),{'state':'renewed'})
		product_list = []
		generic_name = []
		for line in o.amc_sale_order_line_id:
			# if not line.product_id.name in product_list:
			# 	product_list.append(line.product_id.name)
			if not line.product_generic_name.name in generic_name:
				generic_name.append(line.product_generic_name.name)
		products =', '.join(map(str, product_list))
		generic = ''
		if len(generic_name) > 1:
			last_item = generic_name[-1]
			second_last = generic_name[-2]
			for x in generic_name:
				if x == last_item:
					generic = generic+'& ' + x
				elif x == second_last:
					generic =  generic + x +' '
				else:
					generic =  generic + x +', '
		elif len(generic_name) == 1:
			generic = generic_name[0]
		self.write(cr,uid,ids,{'products':generic,'skus':products})
		ord_id = crm_order_hist_obj.search(cr,uid,[('partner_id','=',int(o.partner_id.id)),('service_order_id','=',int(o.id))])
		if ord_id:
			for m in ord_id:
				crm_order_hist_obj.unlink(cr,uid,m,context=None)
		order_period = False
		if o.order_period_from and o.order_period_to:
			order_period=str(datetime.strptime(o.order_period_from, "%Y-%m-%d").strftime("%d/%m/%Y"))+'-'+str(datetime.strptime(o.order_period_to, "%Y-%m-%d").strftime("%d/%m/%Y"))
		else:
			order_period ='-'
		crm_history_values = { 	'partner_id':o.partner_id.id,
								'service_order_id':o.id,
								'order_id':o.order_number,
								'order_date':o.order_date,
								'order_period':order_period,
								'sku_name':products,
								'request_id':o.request_id,
								'order_amount':grand_total,
								'order_type':o.type,
								'status':'pending',
								'pse':o.pse.concate_name,
							}
		crm_order_hist_obj.create(cr,uid,crm_history_values,context=None)
		return True

	def generate_order(self,cr,uid,ids,context=None):
		rec = self.browse(cr, uid, ids[0])
		if not rec.quotation_number:
			self.calculate(cr,uid,ids,context=context)
		inv_line_obj = self.pool.get('amc.invoice.line')
		crm_lead_obj = self.pool.get('crm.lead')
		if not rec.amc_invoice_line:
			raise osv.except_osv(_('Warning!'),_("Without selecting payterms, order cannot be generated! Kindly select payterms!"))
		if rec.amc_invoice_line:
			total = 0.0
			for s in rec.amc_invoice_line:
				inv_amount = s.amount
				total += inv_amount
			if total < rec.basic_charge:
				amt = rec.basic_charge-total
				raise osv.except_osv(_('Warning!'),_("Total of payterms is less by %s Rs. It should be equal to Basic Amount!")%(amt))
			if total > rec.basic_charge:
				amt = total-rec.basic_charge
				raise osv.except_osv(_('Warning!'),_("Total of payterms is greater by %s Rs. It should be equal to Basic Amount!")%(amt))
		seq = self.pool.get('ir.sequence').get(cr, uid,'amc.sale.order')
		# code = self.get_fiscalyear(cr,uid,ids,context=None)
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
		order_number = str(rec.company_id.pcof_key)+str(rec.company_id.service_order_id)+financial_year+str(seq)
		self.write(cr,uid,ids,{'state':'ordered','order_date':datetime.today(),'order_number':order_number})
		product_request_obj = self.pool.get('product.request')
		crm_hist_obj = self.pool.get('sales.product.quotation.history')
		crm_order_hist_obj = self.pool.get('psd.order.crm.history')
		search_product_request = product_request_obj.search(cr,uid,[('product_request_id','=',str(rec.request_id))])
		self.pool.get('amc.quotation').write(cr,uid,rec.amc_quotn_id.id,{'state':'ordered'},context=context)
		product_request_obj.write(cr,uid,search_product_request[0],{'state':'closed','closed_date':datetime.now()})
		crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', str(rec.request_id))], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'closed'}, context=context)
		# if sale_product_req_data.psd_quotation_id:
		# 	self.pool.get('psd.sales.product.quotation').write(cr,uid,sale_product_req_data.psd_quotation_id.id,{'state':'ordered'})
		if rec.amc_quotn_id:
			qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(rec.amc_quotn_id.partner_id.id)),('amc_quotation_id','=',int(rec.amc_quotn_id.id))])
			if qutn_id:			
				crm_history_values = {'status':'ordered'}
				crm_hist_obj.write(cr,uid,qutn_id[0],crm_history_values,context=None)
		product_list = []
		generic_name = []
		for line in rec.amc_sale_order_line_id:
			self.pool.get('amc.sale.order.line').write(cr,uid,line.id,{'order_no_ref':order_number})
			# if not line.product_id.name in product_list:
			# 	product_list.append(line.product_id.name)
			if not line.product_generic_name.name in generic_name:
				generic_name.append(line.product_generic_name.name)
		products =', '.join(map(str, product_list))
		generic = ''
		if len(generic_name) > 1:
			last_item = generic_name[-1]
			second_last = generic_name[-2]
			for x in generic_name:
				if x == last_item:
					generic = generic+'& ' + x
				elif x == second_last:
					generic =  generic + x +' '
				else:
					generic =  generic + x +', '
		elif len(generic_name) == 1:
			generic = generic_name[0]
		self.write(cr,uid,ids,{'products':generic,'skus':products})
		ord_id = crm_order_hist_obj.search(cr,uid,[('partner_id','=',int(rec.partner_id.id)),('service_order_id','=',int(rec.id))])
		if ord_id:
			for m in ord_id:
				crm_order_hist_obj.unlink(cr,uid,m,context=None)
		order_period = False
		if rec.order_period_from and rec.order_period_to:
			order_period=str(datetime.strptime(rec.order_period_from, "%Y-%m-%d").strftime("%d/%m/%Y"))+'-'+str(datetime.strptime(rec.order_period_to, "%Y-%m-%d").strftime("%d/%m/%Y"))
		else:
			order_period ='-'
		crm_history_values = { 	'partner_id':rec.partner_id.id,
								'service_order_id':rec.id,
								'order_id':order_number,
								'order_date':datetime.today(),
								'order_period':order_period,
								'sku_name':products,
								'request_id':rec.request_id,
								'order_amount':rec.grand_total,
								'order_type':rec.type,
								'status':'ordered',
								'pse':rec.pse.concate_name,
							}
		crm_order_hist_obj.create(cr,uid,crm_history_values,context=None)
		######### Create Job on Generate AMC Order #############################
		record = self.browse(cr,uid,ids[0])
		for product_line in record.amc_sale_order_line_id:
			no_of_jobs = product_line.no_of_units * int(product_line.no_of_visits)
			service_laps = record.no_of_days/no_of_jobs
			three_mon_rel = relativedelta(days=service_laps)
			service_date = datetime.strptime(record.order_period_from , '%Y-%m-%d')
			addrs_items = []
			address = ''
			if record.site_address.apartment not in [' ',False,None]:
				addrs_items.append(record.site_address.apartment)
			if record.site_address.building not in [' ',False,None]:
				addrs_items.append(record.site_address.building)
			if record.site_address.sub_area not in [' ',False,None]:
				addrs_items.append(record.site_address.sub_area)
			if record.site_address.landmark not in [' ',False,None]:
				addrs_items.append(record.site_address.landmark)
			if record.site_address.street not in [' ',False,None]:
				addrs_items.append(record.site_address.street)
			if record.site_address.city_id:
				addrs_items.append(record.site_address.city_id.name1)
			if record.site_address.district:
				addrs_items.append(record.site_address.district.name)
			if record.site_address.tehsil:
				addrs_items.append(record.site_address.tehsil.name)
			if record.site_address.state_id:
				addrs_items.append(record.site_address.state_id.name)
			if record.site_address.zip not in [' ',False,None]:
				addrs_items.append(record.site_address.zip)

			if len(addrs_items) > 0:
				last_item = addrs_items[-1]
				for item in addrs_items:
					if item!=last_item:
						address = address+item+','+' '
					if item==last_item:
						address = address+item

			for job in range(0,no_of_jobs):
				seq_id = self.pool.get('ir.sequence').get(cr, uid,'operation.job.id')
				ou_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
				year1=date.today().strftime('%y')
				company_id=self._get_company(cr,uid,context=None)
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					job_code=comp_id.job_id
				month=date.today().strftime('%m')
				if int(month)>3:
						year2=int(year1)+1
				else :  
						year2=int(year1)
				job_id =str(ou_id)+job_code+str(year2)+str(seq_id)
				service_date =  service_date + three_mon_rel
				# service_date = service_date.date()
				# bbb
				job_data = {
						'name_contact':record.partner_id.id,
						'job_category':'service',
						'job':'service',
						# 'classification':record.classification,
						# 'service_type':record.service_type,
						'job_id':job_id,
						'scheduled_job_id':job_id,
						# 'pse':record.pse.id,
						'service_order_no':order_number,
						'erp_order_date':datetime.today(),
						'name_equipment':product_line.product_generic_name.id,
						'ordered_period_from':datetime.strptime(record.order_period_from , '%Y-%m-%d'),
						'ordered_period_to':datetime.strptime(record.order_period_to , '%Y-%m-%d'),
						'contract_period':record.no_of_months,
						'state':'unscheduled',
						'company_id':company_id,
						'req_date_time':service_date, #expected delivery date
						'contact_name':record.contact_person, #customer name both
						# 'site_address1':address,
						# 'phone1':record.partner_id.phone_many2one.number,
						#'holiday_active':1,
					}
				print job_data,'amc quotation class'
				job_ids = self.pool.get('res.scheduledjobs').create(cr,uid,job_data,context=context)
				cr.commit()
				holiday_ids = self.pool.get('hr.holiday.new').search(cr,uid,[])				
				holiday_list = []
				for holiday in self.pool.get('hr.holiday.new').browse(cr,uid,holiday_ids):
					holiday_list.append(holiday.from_date)
				if service_date.strftime("%A") == 'Sunday' or service_date in holiday_list:
					service_date = service_date + relativedelta(days=+1)
		######### END ############################################################
			for s in rec.amc_invoice_line:
				inv_line_obj.write(cr,uid,s.id,{'state':'ordered'})
		return True


	def button_create(self,cr,uid,ids,context=None):
		total = 0
		flag =  False
		loop_value = 0
		for res in self.browse(cr,uid,ids,context=None):	
			if not res.no_of_payment:
				raise osv.except_osv(('Alert!'),('Please Select Number of Payment'))
			unlink_id = self.pool.get('amc.invoice.line').search(cr,uid,[('amc_inv_line','=',res.id),('id','>',0)])
			if unlink_id:
				self.pool.get('amc.invoice.line').unlink(cr,uid,unlink_id)
			loop_value = res.no_of_payment
			while loop_value > 0:
				contract_amount = res.basic_charge/(res.no_of_payment)
				loop_value -= 1
				date_new = datetime.today().date()
				self.pool.get('amc.invoice.line').create(cr,uid,{'invoice_date':date_new,'amount':round(contract_amount),'amc_inv_line':res.id,'state':res.state})
			if res.amc_invoice_line:
				for k in res.amc_invoice_line:
					if res.state =='ordered':
						self.pool.get('amc.invoice.line').write(cr,uid,k.id,{'pay_check':False,'bool_cancel_new':False})
		self.write(cr,uid,ids,{'no_of_payment':0})

	def button_add(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids,context=None):
			total_amount = 0.0
			actual_amount = 0.0
			flag = False
			amount=int(res.amount)
			if not res.invoice_date and not res.amount :
				raise osv.except_osv(('Alert!'),('Please Select All Details'))
			if not res.amount:
				raise osv.except_osv(('Alert!'),('Please Enter Amount'))
			# if res.invoice_date > res.contract_end_date or res.invoice_date < res.contract_start_date:
			# 	raise osv.except_osv(('Alert!'),('Invoice Date Must be Within Contract Start Date and End Date'))
			for temp in res.amc_invoice_line:
				total_amount += temp.amount
			actual_amount = round(total_amount,2)
			

			if int(total_amount+amount) > int((res.basic_charge)):
				raise osv.except_osv(('Alert!'),('Total Amount Greater than Basic Amount'))
			# if res.state == 'pending':
			# 	flag = True
			
			self.pool.get('amc.invoice.line').create(cr,uid,{'amc_inv_line':res.id,'invoice_date':res.invoice_date,'amount':amount,'state':res.state})
			self.pool.get('amc.sale.order').write(cr,uid,res.id,{'invoice_date':False,'amount':0.0})

	def print_order(self, cr, uid, ids, context=None):
		corp_office_id = False
		regd_office_id = False
		company_obj = self.pool.get('res.company')
		emp_obj =  self.pool.get('hr.employee')
		user_obj = self.pool.get('res.users')
		search_branch_mgr = emp_obj.search(cr,uid,[('role','=','branch_manager')])
		employee = emp_obj.browse(cr,uid,search_branch_mgr[1])
		emp_name = employee.concate_name
		emp_designation = employee.emp_role.value
		search_user = user_obj.search(cr,uid,[('name','ilike',emp_name),('emp_code','=',employee.emp_code)])
		user = user_obj.browse(cr,uid,search_user[0])
		search_corp = company_obj.search(cr,uid,[('branch_type','=','corp_office')])
		search_regd = company_obj.search(cr,uid,[('branch_type','=','regd_office')])
		if search_corp:
			corp_office_id = search_corp[0]
		if search_regd:
			regd_office_id = search_regd[0]
		self.write(cr,uid,ids,{'territry_manager':emp_name,'email':user.user_email,'mobile':user.mobile,'designation':emp_designation,'corp_office_id':corp_office_id,'regd_office_id':regd_office_id})
		datas = {
				 'model': 'amc.sale.order',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'amc.service.order', 'datas': datas, 'nodestroy': True}


amc_sale_order()


class amc_sale_order_line(osv.osv):
	_name = 'amc.sale.order.line'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'amc_sale_order_id':fields.many2one('amc.sale.order','AMC Sale Order ID',ondelete='cascade'),
		#'no_of_visits':fields.selection([('single_service','Single Service'),('2_visits','2 Visits'),('3_visits','3 Visits'),('4_visits','4 Visits'),('6_visits','6 Visits'),('12_visits','12 Visits')],'No of Visits'),
		'no_of_visits':fields.selection([('1','Single Service'),('2','2 Visits'),('3','3 Visits'),('4','4 Visits'),('6','6 Visits'),('12','12 Visits')],'No of Visits'),
		'product_code': fields.char('Product Code', size=256),
		'particulars_equipment': fields.char('Particulars of the Equipment', size=256),
		'rate_per_unit':fields.float('Rate P.U.'),
		'no_of_units':fields.integer('No of Units'),
		#'product_name': fields.many2one('product.group','Product Name'),
		# 'product_generic_name': fields.many2one('product.generic.name','Product Name'),
		'product_generic_name':fields.many2one('product.product','SKU Name'),
		'cgst_rate':fields.char('CSGT Rate',size=10),
		'sgst_rate':fields.char('SGST Rate',size=10),
		'igst_rate':fields.char('IGST Rate',size=10),
		'cgst_amount':fields.float('CGST Amount'),
		'sgst_amount':fields.float('SGST Amount'),
		'igst_amount':fields.float('IGST Amount'),
		'total_basic':fields.float('Total Basic'),
		'tax_amount':fields.float('Tax Amount'),
		'total_amount':fields.float('Total Amount'),
		'order_no_ref':fields.char('ERP order no ref',size=30),
	}

	_defaults = {
		'company_id': _get_company
	}

	def onchange_product_id(self,cr,uid,ids,product_id):
		v={}
		if product_id:
			product_browse_id = self.pool.get('product.product').browse(cr,uid,product_id)
			v['product_code'] = product_browse_id.default_code
		return {'value': v}


amc_sale_order_line()

class amc_quotation_remarks(osv.osv):
	_name = "amc.quotation.remarks"
	_description="Remarks"
	#_order="date desc"

	_columns = {
		'quotation_order_id': fields.many2one('amc.quotation','notes'),
		#'user_name':fields.many2one('res.users','User Name'), 
		'user_name':fields.char('User Name',size=64),
		'date': fields.datetime('Date & Time'),
		'name': fields.text('Topic: Notes *',size=500),
		'state': fields.selection([	('new','New'),
									('pending','Pending'),
									('quoted','Quoted'),
									('ordered','Ordered'),
									('lost','Lost'),
									('revised','Revised'),
									],'State', readonly=True, select=True),
		'source':fields.many2one('res.company','Source'),
		}
amc_quotation_remarks()

class amc_order_remarks(osv.osv):
	_name = "amc.order.remarks"
	_description="Remarks"
	#_order="date desc"

	_columns = {
		'amc_order_id': fields.many2one('amc.sale.order','notes'),
		#'user_name':fields.many2one('res.users','User Name'), 
		'user_name':fields.char('User Name',size=64),
		'date': fields.datetime('Date & Time'),
		'name': fields.text('Topic: Notes *',size=500),
		'state':fields.selection([('new','New'),
					('pending','Pending'),
					('ordered','Ordered'),
					('cancelled','Cancelled')
					],'State', readonly=True, select=True),
		'source':fields.many2one('res.company','Source'),
		}
amc_order_remarks()


class amc_invoice_line(osv.osv):
	_name = 'amc.invoice.line'
	_order = 'invoice_date'
	_rec_name = 'id'
	_columns = {
		'sequence_id':fields.char('Sequence Number',size=124),
		'pay_check':fields.boolean('',invisible=True),
		'amc_inv_line':fields.many2one('amc.sale.order','AMC Inv Line ID',invisible=True),
		'reason':fields.char('Payterm Cancel Reason',size=124),
		'invoice_date':fields.date('Invoice Date'),
		'amount':fields.float('Amount'),
		'bool_cancel':fields.boolean('',invisible=True),
		'bool_cancel_new':fields.boolean('',invisible=True),
		'invoice_done':fields.boolean('invoice_done',invisible=True),
		'lost':fields.boolean('lost',invisible=False),
		'contract_key':fields.char('Contract Key', size=364),
		'state':fields.selection([('new','New'),
					('pending','Pending'),
					('ordered','Ordered'),
					('cancelled','Cancelled')
					],'State'),
		}

	def unlink(self,cr,uid,ids,context=None):
		self_obj = self.browse(cr,uid,ids[0])
		if self_obj.pay_check == True:
			raise osv.except_osv(_('Warning!'),_("You cannot delete this Invoice line, as this line is already pushed to Accounting module!"))
		res = super(amc_invoice_line, self).unlink(cr, uid, ids, context=context)
		return res

	def round_off_grand_total(self,cr,uid,ids,grand_total,context=None):
		roundoff_grand_total = grand_total + 0.5
		s = str(roundoff_grand_total)
		dotStart = s.find('.')
		grand_total = int(s[:dotStart])
		return grand_total

	def view_contract_invioce(self,cr,uid,ids,context=None):
		temp_id = self.browse(cr,uid,ids[0])
		amc_sale_order_obj = self.pool.get('amc.sale.order')
		o = amc_sale_order_obj.browse(cr,uid,temp_id.amc_inv_line.id)
		main_id = o.id
		if o.amc_invoice_line:
			total = 0.0
			for s in o.amc_invoice_line:
				inv_amount = s.amount
				total += inv_amount
			if total < o.basic_charge:
				amt = o.basic_charge-total
				raise osv.except_osv(_('Warning!'),_("Total of payterms is less by %s Rs. It should be equal to Basic Amount!")%(amt))
			if total > o.basic_charge:
				amt = total-o.basic_charge
				raise osv.except_osv(_('Warning!'),_("Total of payterms is greater by %s Rs. It should be equal to Basic Amount!")%(amt))
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'psd_amc_quotation', 'branch_amc_invoice_line_id')
		#branch_invoice_line_id
		return{
					'type': 'ir.actions.act_window',
					'name':'Payterm Detail',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'amc.invoice.line',
					'res_id':ids[0],
	                 #'res_id':val,
					'views': [(form_view and form_view[1] or False, 'form')],
					'view_id':False,
					'target':'new',	
					'context': context,
					}

	def cancel_check(self,cr,uid,ids,context=None):
		for k in self.browse(cr,uid,ids):
			self.write(cr,uid,k.id,{'bool_cancel':True})	
		return True

	def button_cancel(self,cr,uid,ids,context=None):
		for k in self.browse(cr,uid,ids):
			if not k.reason:
				raise osv.except_osv(('Alert !'),('Reason for Cancel')) 
			self.write(cr,uid,k.id,{'bool_cancel_new':True})	
		return {'view_mode' : 'tree,form','type': 'ir.actions.act_window_close'}

	def button_push(self,cr,uid,ids,context=None):
		service_tax_value = 0.0
		sb_tax_value = 0.0
		kk_tax_value = 0.0
		grand_total = 0.0
		basic_charges_new = 0.0
		today_date =datetime.today().date()
		temp_id = self.browse(cr,uid,ids[0])
		basic_amount = temp_id.amount
		amc_sale_order_obj = self.pool.get('amc.sale.order')
		amc_sale_order_line_obj = self.pool.get('amc.sale.order.line')
		inv_obj = self.pool.get('invoice.adhoc.master')
		inv_line_obj = self.pool.get('invoice.adhoc')
		tax_line_obj = self.pool.get('invoice.tax.rate')
		account_tax = self.pool.get('account.tax')
		o = amc_sale_order_obj.browse(cr,uid,temp_id.amc_inv_line.id)
		main_id = o.id
		amc_lines = o.amc_sale_order_line_id
		print amc_lines	
		gst_tax_value = tax_rate_gst= 0.0
		prod_id = amc_lines[0].product_generic_name.product_tax.id
		lines = amc_lines[0]
		print lines

		account_gst_tax = account_tax.search(cr,uid,[('id','=',prod_id),('select_tax_type','=','gst')])
		if account_gst_tax:
			account_gst_amount = account_tax.browse(cr,uid,account_gst_tax[0]).amount
			account_gst_name = account_tax.browse(cr,uid,account_gst_tax[0]).name
			gst_tax_value = basic_amount * account_gst_amount
			tax_rate_gst = 100 * account_gst_amount
			gst_tax_value = self.round_off_grand_total(cr,uid,ids,gst_tax_value,context=None)		
		grand_total = gst_tax_value+basic_amount
		main_form_values={
			'service_order_id':main_id,
			'amc_inv_id':temp_id.id,
			'cust_name':o.customer_name,
			'partner_id':o.partner_id.id,
			'order_period_from':o.order_period_from,
			'erp_order_no':o.order_number,
			'erp_order_date':o.order_date,
			'order_period_to':o.order_period_to,
			'site_address': o.site_address.id,
			'so_reference_no': o.wo_no,
			'so_reference_date': o.wo_date,
			'billing_address': o.billing_address.id,
			'pse': o.pse.id,
			'status': 'open',
			'basic_charge':temp_id.amount,
			# 'service_tax_14': gst_tax_value,  # for time being. else create a new field for GST
			# 'sb_cess_0_50': sb_tax_value,
			# 'kk_cess_0_50': kk_tax_value,
			# 'service_order_grand_total': grand_total,
			'service_type':o.service_type,
			'classification':o.classification,
			'order_total_vat':(service_tax_value+sb_tax_value+kk_tax_value),
			'invoice_type':'service_invoice'
		}

		res_inv_create = inv_obj.create(cr,uid,main_form_values)
		cr.commit()
		# for each in o.tax_one2many:
		# 	print each.name,each.amount,each.account_tax_id.id,o.id
		# 	tax_lines = {
		# 		'name':each.name,
		# 		'amount':each.amount,
		# 		'account_tax_id':each.account_tax_id.id,
		# 		'invoice_id':res_inv_create,
		# 	}
		# 	tax_lines_create = tax_line_obj.create(cr,uid,tax_lines)
		# 	cr.commit()
		for line_id in amc_lines:
			if o.no_of_payment:
				contract_amount = o.basic_charge/(o.no_of_payment)
				contract_amount = round(contract_amount)
				if basic_amount == contract_amount:
					basic_charges_new = line_id.total_amount/o.no_of_payment
				else:
					percentage = (basic_amount*100)/o.basic_charge
					basic_charges_new = (line_id.total_amount * percentage)/100
			else:
				percentage = (basic_amount*100)/o.basic_charge
				basic_charges_new = (line_id.total_amount * percentage)/100
			print res_inv_create,line_id.particulars_equipment,line_id.rate_per_unit,line_id.no_of_visits,line_id.product_code,line_id.product_generic_name.id,basic_charges_new,'\n'
			line_values ={
			'invoice_type':'service_invoice',
			'service_invoice_id': res_inv_create,
			'rate_per_unit':line_id.rate_per_unit,
			'particulars_equipment': line_id.particulars_equipment,
			'no_of_visits': line_id.no_of_visits,
			'no_of_units':line_id.no_of_units,
			'product_code': line_id.product_code,
			'product_generic_name': line_id.product_generic_name.id,
			# 'product_id': line_id.product_id.id,
			'total':line_id.total_basic,
			'cgst_rate':line_id.cgst_rate,
			'sgst_rate':line_id.sgst_rate,
			'igst_rate':line_id.igst_rate,
			'sgst_amt':line_id.sgst_amount,
			'cgst_amt':line_id.cgst_amount,
			'igst_amt':line_id.igst_amount,
			'total_amount': basic_charges_new,
			}
			res_inv_line_create= inv_line_obj.create(cr,uid,line_values)
			cr.commit()
		# tax_line_obj.create(cr,uid,{'invoice_id':int(res_inv_create),'account_tax_id':account_gst_tax,'name':account_gst_tax,'tax_rate':tax_rate_gst,'amount':gst_tax_value},context=None)
		# tax_line_obj.create(cr,uid,{'invoice_id':int(res_inv_create),'account_tax_id':account_sb_tax[0],'name':sb_cess_name,'tax_rate':tax_rate_sb,'amount':sb_tax_value})
		# tax_line_obj.create(cr,uid,{'invoice_id':int(res_inv_create),'account_tax_id':account_kk_tax[0],'name':kk_cess_name,'tax_rate':tax_rate_kk,'amount':kk_tax_value})			        
		self.write(cr,uid,temp_id.id,{'pay_check':True,'invoice_done':True,'reason':''})
		amc_sale_order_obj.write(cr,uid,main_id,{'invoiced':True})
		schedule_jobs_obj =  self.pool.get('res.scheduledjobs')
		job_history_obj = self.pool.get('job.history')
		print o.order_number
		# bbb
		search_job_id = schedule_jobs_obj.search(cr,uid,[('service_order_no','=',o.order_number)])
		browse_job_id = schedule_jobs_obj.browse(cr,uid,search_job_id[0]).job_id
		search_history_ids = job_history_obj.search(cr,uid,[('job_id','=',browse_job_id)])
		for history_id in search_history_ids: 
			self.pool.get('job.history').write(cr,uid,history_id,{'invoice_id':res_inv_create})
		return {
				'view_type': 'form',
				'view_mode': 'form',
				'name': _('Service Order'),
				'res_model': 'amc.sale.order',
				'res_id': main_id,
				'type': 'ir.actions.act_window',
				'target': 'current',
				'context': context,
				'nodestroy': True,
		}

amc_invoice_line()

class tax(osv.osv):
	_inherit="tax"
	_order="name desc"
	_columns={
		'amc_quotn_id':fields.many2one('amc.quotation','Inspection Costing ID'),
		'amc_so_id':fields.many2one('amc.sale.order','Sale Quotation ID'),
	}

tax()

class res_partner(osv.osv):
	_inherit = 'res.partner'

	_columns = {
		'sale_quotation_crm_history_ids':fields.one2many('sales.product.quotation.history','partner_id','Quotation Histoty'),
		'psd_order_crm_history_ids':fields.one2many('psd.order.crm.history','partner_id','Order Histoty'),
		'sale_history_quotation_id':fields.one2many('psd.sales.product.quotation','partner_id','Quotation Histoty'),
		'amc_history_quotation_id':fields.one2many('amc.quotation','partner_id','Quotation Histoty'),
		'sale_psd_history_order_id':fields.one2many('psd.sales.product.order','partner_id','Order Histoty'),
		'service_psd_history_order_id':fields.one2many('amc.sale.order','partner_id','Order History',),
	}

	
res_partner()


class sales_product_quotation_history(osv.osv):
	_name = 'sales.product.quotation.history'

	_columns = {
		'partner_id':fields.many2one('res.partner','Partner ID'),
		'sale_quotation_id':fields.many2one('psd.sales.product.quotation','Quotation Histoty'),
		'amc_quotation_id':fields.many2one('amc.quotation','Quotation Histoty'),
		'quotation_id':fields.char('Quotation ID',size=100),
		'quotation_date':fields.date('Quotation Date'),
		'quotation_type':fields.char('Quotation Type',size=100),
		'sku_name':fields.char('SKU Name',size=1000),
		'request_id':fields.char('Request ID',size=100),
		'quotation_amount':fields.float('Grand Total'),
		'status':fields.selection([('new','New'),
						('pending','Pending'),
						('quoted','Quoted'),
						('ordered','Ordered'),
						('lost','Lost'),
						('revised','Revised'),
						],'Status'),
		'pse':fields.char('PSE',size=200),

	}

	def show_details_quotation(self, cr, uid, ids, context=None):
		cur_rec = self.browse(cr,uid,ids[0])
		cur_rec_id = False
		if cur_rec.sale_quotation_id:
			cur_rec_id = cur_rec.sale_quotation_id.id
			view = self.pool.get('ir.model.data').get_object_reference(
				cr, uid, 'psd_sales', 'view_psd_product_quotation_branch')
			model = 'psd.sales.product.quotation'
			name = 'Product Quotation'
		else:
			cur_rec_id = cur_rec.amc_quotation_id.id
			view = self.pool.get('ir.model.data').get_object_reference(
				cr, uid, 'psd_amc_quotation', 'view_amc_quotation_form')
			model = 'amc.quotation'
			name = 'Service Quotation'
		view_id = view and view[1] or False
		return {
			'name': _(name),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': model,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': cur_rec_id,
		}

	
sales_product_quotation_history()

class psd_order_crm_history(osv.osv):
	_name = 'psd.order.crm.history'

	_columns = {
		'partner_id':fields.many2one('res.partner','Partner ID'),
		'sale_order_id':fields.many2one('psd.sales.product.order','Order Histoty'),
		# 'amc_order_id':fields.many2one('amc.sale.order','Order History'),
		'service_order_id':fields.many2one('amc.sale.order','Order History'),
		'order_id':fields.char('Order ID',size=100),
		'order_date':fields.date('Order Date'),
		'order_type':fields.char('Order Type',size=100),
		'sku_name':fields.char('SKU Name',size=1000),
		'request_id':fields.char('Request ID',size=100),
		'order_amount':fields.float('Grand Total'),
		'order_period':fields.char('Order Period',size=50),
		'status':fields.selection([('new','New'),
						('pending','Pending'),
						('ordered','Ordered'),
						('partial_delivery_scheduled','Partial Delivery Scheduled'),
						('delivery_scheduled','Delivery Scheduled'),
						('delivered','Delivered'),
						('cancelled','Cancelled'),
						],'Status'),
		'pse':fields.char('PSE',size=200),

	}

	def show_details_order(self, cr, uid, ids, context=None):
		cur_rec = self.browse(cr,uid,ids[0])
		cur_rec_id = False
		if cur_rec.sale_order_id:
			cur_rec_id = cur_rec.sale_order_id.id
			view = self.pool.get('ir.model.data').get_object_reference(
				cr, uid, 'psd_sales', 'view_psd_product_quotation_branch')
			model = 'psd.sales.product.order'
			name = 'Product Order'
		else:
			cur_rec_id = cur_rec.service_order_id.id
			view = self.pool.get('ir.model.data').get_object_reference(
				cr, uid, 'psd_amc_quotation', 'view_amc_sale_order_form')
			model = 'amc.sale.order'
			name = 'Service Order'
		view_id = view and view[1] or False
		return {
			'name': _(name),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': model,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': cur_rec_id,
		}

	
psd_order_crm_history()


class invoice_adhoc_master(osv.osv):
	_inherit="invoice.adhoc.master"
	_columns={
		'service_order_id':fields.many2one('amc.sale.order','Service Order'),
	}

invoice_adhoc_master()	