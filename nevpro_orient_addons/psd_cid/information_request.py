from datetime import date,datetime, timedelta
from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
from base.res import res_company as COMPANY
from base.res import res_partner
import os
from tools.translate import _
##### INFORMATION REQUEST ##################################

class product_information_request(osv.osv):
	_name = "product.information.request"
	_rec_name = 'information_request_id'

	def _get_user(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).id

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_datetime(self,cr,uid,context=None):
		return time.strftime("%Y-%m-%d %H:%M:%S")

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'active':fields.boolean('Active', select=True),
		'information_request_id':fields.char('Information Request ID',size=100),
		'customer_id': fields.char('Customer ID',size=256),
		'partner_id':fields.many2one('res.partner','Partner ID'),
		'name':fields.char('Customer / Company Name',size=100),
		'call_type':fields.selection([('inbound','Inbound'),('outbound','Outbound')],'Call Type'),
		'state':fields.selection([('new','New'),
						('open','Opened'),
						('progress','Resource Assigned'),
						('closed','Closed'),
						('cancel','Cancelled')
						],'State'), 
		'created_date': fields.datetime('Created Date'),
		'created_by':fields.many2one('res.users','Created By'),
		'request_date':fields.datetime('Request Date'),
		'customer_type': fields.selection([('existing','Existing Customer'),('new','New Customer')],'Customer Type'),
		'title':fields.selection(res_partner.PARTNER_TITLES,'Title'),
		'contact_name':fields.char('Contact Name',size=100),
		'customer_address':fields.text('Address*'),
		'remarks':fields.text('Remarks*'),
		'branch_id':fields.many2one('res.company','PCI Office*'),
		'email':fields.char('E-Mail', size=60),
		'fax':fields.char('Fax',size=12),
		'phone_many2one':fields.many2one('phone.number.child','Phone Number'),
		'phone_many2one_new':fields.many2one('phone.number.new.psd','Phone Number'),
		'notes_line': fields.one2many('product.information.request.notes.line','request_id','Comments'),
		'comment_remark':fields.text('Comments',size=500),
		'selected':fields.boolean('Selected'),
		# 'crm_lead_id':fields.many2one('crm.lead','Crm Lead ID'),
		'information_request_id': fields.char('Request ID',size=30),
		'global_search_id': fields.many2one('ccc.branch', 'Global Search'),
		'request_type': fields.selection([
										  ('lead_request','Existing Customer Request'),
										  ('complaint_request','Complaint Request'),
										  ('renewal_request','Renewal Request'),
							              ('information_request','Miscellaneous Request'),
										  ('product', 'Product Request'),
										  ('complaint', 'Complaint Request'),
										  ('information', 'Information Request'),
										 ],'Request Type'),
		# 'request_desc':fields.selection([('amc_request','Service Request'),
		# 								 ('any_product_query','Any Product Query')
		# 								],'Request Type*'),
		'information_request_type_id': fields.many2one('information.request.types','Request Type*'),
		'employee_id': fields.many2one('hr.employee', 'Assign Resource'),
		'cancel_request': fields.boolean('Cancel Request'),
		'cancellation_reason': fields.char('Cancellation Reason*',size=50),
		'resolution':fields.text('Resolution*',size=500),
		'closed_date':fields.datetime('Closed Date'),
		'location_branch': fields.selection([('same','Same'),
											 ('different','Different'),
											 ('crm','CRM')
											 ],'Location Branch'),
		# 'request_desc':fields.selection([
		# 								('not_happy_with_rates','Not happy with the rates given'),
		# 								('cert_for_pest_control_service','Certification for pest control service'),
		# 								('contract_renewal_bt_not_receive_paper','Contract renewed but did not receive contract papers'),
		# 								('has_gss_contract_enquired_for_tspo','Has GSS contract and enquired for TSPO but doesnot remember the rate quoted for TSPO'),
		# 								('need_to_discuss_reg_renewal','Need to discuss regarding renewal'),
		# 								('want_discus_reg_inspection','Want to discuss regarding inspection'),
		# 								('whether_all_service_done_or_pending','Whether all service is done or is pending'),
		# 								('collection_payment','Collection of payment'),
		# 								('corection/clarification_required_invoice','Corrections / clarifications required in invoice'),
		# 								('change_address/transfer_contract','Change of address/transfer of contract'),
		# 								('update_contact_info','Update contact information'),
		# 								('need_info_on_exist_cust','Need information on existing contract'),
		# 								('contract_exp_bt_service_pendin','Contract expired but service pending'),
		# 								('order_cancellation','Order Cancellation'),
		# 								('name_on_the_cheque','Name on the cheque'),
		# 								('Amount_on_the_cheque','Amount on the cheque'),
		# 								('request_refund','Request for refund'),
		# 								('validity_contract','Validity of contract'),
		# 								('wants_to_upgrade_annual_contract','Wants to upgrade to Annual contract'),
		# 								('inspection_done_bt_quote_not_receive','Inspection done but quotation not received'),
		# 								('contract_exp_bt_complaint','Contract expired but complaint'),
		# 								('want_cnfirm_appointment','Wants to confirm appointment'),
		# 								('wants_schedule_service','wants to schedule service'),
		# 								('pre/post_service','Pre or postpond service'),
		# 								('cancle_schedule_service','Cancel the scheduled service'),
		# 								('did_treatment_hurry','Did treatment in hurry'),
		# 								('no_reminder_prev_day_confirmation','No reminder previous day for confirmation of appointment'),
		# 								('called_collect_dead_rat','Called to collect dead rat'),
		# 								('is_chem_harmfull','Is the chemicals harmful?'),
		# 								('pickup_dead_rat','To pick-up dead rat'),
		# 								('partial_treatment','Did partial treatment'),
		# 								('not_received_catch-a-roach','Did not receive catch-a-roach'),
		# 								('partial_treat_pending','Partial treatment pending'),
		# 								('want_branch/staff/divs_no','Want branch/Staff/Division No.'),
		# 								('want_know_about_prod','want to know about any product'),
		# 								('pci_dearlership','Wants PCI Dearlership')],'Request Type'),

	}

	_defaults = {
		'company_id':_get_company,
		'active': True,
		'customer_type': 'new',
		'call_type':'inbound',
		'state':'new',
		'request_date':_get_datetime,
		'created_by':lambda self, cr, uid, context: self._get_user(cr, uid, context),   
		'branch_id':_get_company,
		'request_type': 'information'  
	}

	def create_number(self,cr,uid,ids,context=None):	
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'base', 'view_res_contact_number_form')
		view_id = view and view[1] or False
		context.update({'request_type':'information'})
		return {
			'name': _('Phone Number'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'phone.number',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'res_id': False,
			'context': context
		}

	def create_number_psd(self,cr,uid,ids,context=None):	
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_cid', 'phone_number_pop_up_psd_form')
		view_id = view and view[1] or False
		context.update({'request_type':'information'})
		return {
			'name': _('Phone Number'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'phone.number.pop.up.psd',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'res_id': False,
			'context': context
		}				

	def _get_default_date(self, cr, uid, context=None):
		if context is None:
			context = {}
		if 'date' in context:
			return context['date'] + time.strftime(' %H:%M:%S')
		return time.strftime('%Y-%m-%d %H:%M:%S')

	def process_information_request(self,cr,uid,ids,context=None):
		partner_obj = self.pool.get('res.partner')
		models_data=self.pool.get('ir.model.data')
		global_search_obj = self.pool.get('ccc.branch')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		crm_lead_obj = self.pool.get('crm.lead')
		rec = self.browse(cr,uid,ids[0])
		if rec.state == 'progress':
			if not rec.resolution:
				raise osv.except_osv(_('Warning!'),_("Please enter resolution!"))
			crm_ids = crm_lead_obj.search(cr, uid, [('information_request_id','=', ids[0])], context=context)
			for crm_id in crm_ids:
				crm_lead_obj.write(cr, uid, crm_id, {'state':'closed'}, context=context)		
			res = self.write(cr, uid, ids[0], {'state':'closed','closed_date':datetime.now()}, context=context)
			return res
		if not rec.name:
			raise osv.except_osv(_('Warning!'),_('Please enter Customer/Company Name!'))
		if not rec.information_request_type_id:
			raise osv.except_osv(_('Warning!'),_('Please enter Request Type!'))
		if not rec.customer_address:
			raise osv.except_osv(_('Warning!'),_('Please enter address!'))
		if not rec.remarks:
			raise osv.except_osv(_('Warning!'),_('Please enter remarks!'))
		if not rec.branch_id:
			raise osv.except_osv(_('Warning!'),_('Please enter PCI Office!'))
		req_ids = crm_lead_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id)], context=context)	
		if rec.customer_type == 'existing':
			cust_prefix = False
			ir_inc_no = len(req_ids)+1
			if ir_inc_no >= 0 and ir_inc_no <= 9:
				st_ir_inc_no = '00'+str(ir_inc_no)
			elif ir_inc_no >= 10 and ir_inc_no <= 99:
				st_ir_inc_no = '0'+str(ir_inc_no)
			elif ir_inc_noc_no >= 100 and ir_inc_no <= 999:	
				st_ir_inc_no = str(ir_inc_no)	
			customer_seq = rec.partner_id.ou_id
			if len(customer_seq) == 12:
				temp_customer_inc_no = customer_seq[4:]
			elif len(customer_seq) == 16:
				temp_customer_inc_no = customer_seq[10:]
			elif len(customer_seq) == 17:
				temp_customer_inc_no = customer_seq[11:]
			elif len(customer_seq) == 4:
				temp_customer_inc_no = customer_seq
			if len(temp_customer_inc_no) == 6:
				cust_prefix = '00'
			if len(temp_customer_inc_no) == 4:
				cust_prefix = '0000'	
			if cust_prefix:
				customer_inc_no = cust_prefix + temp_customer_inc_no
			else:
				customer_inc_no = temp_customer_inc_no
			ir_seq = rec.company_id.pcof_key + 'IR' + customer_inc_no + st_ir_inc_no
		else:
			ir_inc_no = self.pool.get('ir.sequence').get(cr, uid, 'product.information.request')
			st_ir_inc_no = '000000000'+str(ir_inc_no)
			ir_seq = rec.company_id.pcof_key + 'IRN' + st_ir_inc_no
		if rec.company_id.establishment_type == 'crm':
			location_branch = 'crm'
		elif rec.branch_id.id == rec.company_id.id:
			location_branch = 'same'
		else:
			location_branch = 'different'	
		self.write(cr,uid,ids,
			{
				'state':'open',
				'location_branch': location_branch,
				'request_date':datetime.now(),
				'information_request_id': ir_seq
			},context=context)
		if rec.partner_id:	
			crm_lead_vals = {
				'inquiry_no': ir_seq,
				'type_request': 'information_request_psd',
				'state': 'open',
				'partner_id': rec.partner_id.id,
				'created_by_global': rec.created_by.name,
				'inspection_date':	rec.request_date,
				'information_request_id': ids[0],										
			}
			crm_lead_obj.create(cr, uid, crm_lead_vals, context=context) 
		global_search_vals = {
			'enquiry_type': 'information_request'
		}	
		global_search_id=global_search_obj.create(cr,uid,global_search_vals,context=context)
		info_data = self.browse(cr, uid, ids[0])
		date_age = global_search_obj.calculate_date_age(cr,uid,ids,info_data.request_date,info_data.closed_date)
		if info_data.customer_type == 'existing':
			phone = info_data.phone_many2one.number
		else:
			phone = info_data.phone_many2one_new.number
		branch_line_vals =  {       
				'ccc_information_id': global_search_id,
				'request_id': info_data.information_request_id,
				'customer_name': info_data.name,
				'branch_id': info_data.branch_id.id,
				'origin': info_data.company_id.name,
				'request_type_psd': 'information_request',
				'date_age': date_age,
				'state': info_data.state,
				'contact_number': phone,
				'sort_date': info_data.request_date,
				'created_by': rec.created_by.id,
				'employee_id': rec.employee_id.id,
				'information_request_id': info_data.id
		}
		branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
		branch_id_sync = info_data.branch_id.id
		context.update({'branch_id_sync':branch_id_sync})
		self.sync_information_request(cr,uid,ids,context=context)
		form_id = models_data.get_object_reference(cr, uid, 'psd_cid', 'view_ccc_branch_form_psd_inherit_new')	
		return {
		   'name':'Global Search',
		   'view_mode': 'form',
		   'view_id': form_id[1],
		   'view_type': 'form',
		   'res_model': 'ccc.branch',
		   'res_id': global_search_id,
		   'type': 'ir.actions.act_window',
		   'target': 'current',
		   'context': context
		}

	def assign_resource(self,cr,uid,ids,context=None):	
		crm_lead_obj = self.pool.get('crm.lead')	
		partner_address_obj = self.pool.get('res.partner.address')	
		customer_line_obj = self.pool.get('customer.line')
		res = self.write(cr,uid,ids,{'state':'progress'},context=context)
		partner_obj = self.pool.get('res.partner')
		crm_ids = crm_lead_obj.search(cr, uid, [('information_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'progress'}, context=context)	
		rec = self.browse(cr, uid, ids[0])
		browse_location_company = rec.branch_id.id
		if rec.customer_type == 'existing':
			if rec.employee_id:	
				addr_id = partner_address_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('primary_contact','=',True)], context=context)
				if addr_id:
					customer_line_id = customer_line_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('customer_address','=',addr_id)], context=context)
				if customer_line_id:
					temp_location_id = customer_line_obj.browse(cr, uid, customer_line_id[0]).location_id
					location_id = temp_location_id[4:]
					pcof_key = rec.company_id.pcof_key
					new_location_id = pcof_key+location_id
					temp_ou_id = rec.partner_id.ou_id
					ou_id = temp_ou_id[4:]
					new_ou_id = pcof_key+ou_id
					cust_line_vals = {'location_id':new_location_id}
					partner_obj.write(cr, uid, rec.partner_id.id, {'ou_id': new_ou_id}, context=context)
					if rec.employee_id.role_selection == 'cse':		
						cust_line_vals.update({'cse':rec.employee_id.id})
					customer_line_obj.write(cr, uid, customer_line_id[0], cust_line_vals, context=context)
		context.update({'branch':browse_location_company})
		self.sync_update_information_request(cr,uid,ids,context=context)
		return res	

	def cancel_information_request(self,cr,uid,ids,context=None):	
		crm_lead_obj = self.pool.get('crm.lead')
		rec = self.browse(cr, uid, ids[0])
		browse_location_company = rec.branch_id.id
		if not rec.cancellation_reason:
			raise osv.except_osv(_('Warning!'),_("Please enter reason for cancellation!"))
		res = self.write(cr,uid,ids,{'state':'cancel'})
		crm_ids = crm_lead_obj.search(cr, uid, [('information_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'cancel'}, context=context)
		context.update({'branch':browse_location_company})	
		self.sync_cancel_information_request(cr,uid,ids,context=context)
		return res

	def product_information_request_cancel(self,cr,uid,ids,context=None):	
		primary_data = self.browse(cr, uid, ids[0])
		phone_psd_obj = self.pool.get('phone.number.new.psd')
		models_data = self.pool.get('ir.model.data')
		search_numbers = phone_psd_obj.search(cr,uid,[('information_request_id','=',ids[0])])
		if search_numbers:
			for number in search_numbers:
				phone_psd_obj.unlink(cr,uid,number,context=context)
		# for line in primary_data.location_request_line:
		# 	product_req_loc_obj.unlink(cr,uid,line.id,context=context)
		self.unlink(cr,uid,ids[0],context=context)
		form_id = models_data.get_object_reference(cr, uid, 'psd_cid', 'view_ccc_branch_form_psd_inherit_new')	
		return {
		   'name':'Global Search',
		   'view_mode': 'form',
		   'view_id': form_id[1],
		   'view_type': 'form',
		   'res_model': 'ccc.branch',
		   'res_id': '',
		   'type': 'ir.actions.act_window',
		   'target': 'current',
		   'context':context
		}	

	def close_information_request(self,cr,uid,ids,context=None):	
		global_search_obj = self.pool.get('ccc.branch')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		models_data=self.pool.get('ir.model.data')
		rec = self.browse(cr,uid,ids[0])
		global_search_vals = {
			'enquiry_type': 'information_request'
		}	
		global_search_id=global_search_obj.create(cr,uid,global_search_vals,context=context)
		info_data = self.browse(cr, uid, ids[0])
		date_age = global_search_obj.calculate_date_age(cr,uid,ids,info_data.request_date,info_data.closed_date)
		if info_data.customer_type == 'existing':
			phone = info_data.phone_many2one.number
		else:
			phone = info_data.phone_many2one_new.number
		branch_line_vals =  {       
				'ccc_information_id': global_search_id,
				'request_id': info_data.information_request_id,
				'customer_name': info_data.name,
				'branch_id': info_data.branch_id.id,
				'origin': info_data.company_id.name,
				'request_type_psd': 'information_request',
				'date_age': date_age,
				'state': info_data.state,
				'contact_number': phone,
				'sort_date': info_data.request_date,
				'created_by': rec.created_by.id,
				'employee_id': rec.employee_id.id,
				'information_request_id': info_data.id
		}
		branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
		form_id = models_data.get_object_reference(cr, uid, 'psd_cid', 'view_ccc_branch_form_psd_inherit_new')	
		return {
		   'name':'Global Search',
		   'view_mode': 'form',
		   'view_id': form_id[1],
		   'view_type': 'form',
		   'res_model': 'ccc.branch',
		   'res_id': global_search_id,
		   'type': 'ir.actions.act_window',
		   'target': 'current',
		   'context': context
		}

	def new_post_comment(self,cr,uid,ids,context=None):
		date=self._get_default_date(cr,uid)
		user_name = ''
		location = False
		for o in self.browse(cr,uid,ids):
			search = self.pool.get('res.users').search(cr,uid,[('id','=',uid)])
			for user in self.pool.get('res.users').browse(cr,uid,search):
				user_name = user.name
			
			state = o.state
			comment_remark = o.comment_remark
			if comment_remark:				
				self.pool.get('product.information.request.notes.line').create(cr,uid,{
																'request_id':o.id,
																'comment':o.comment_remark,
																'comment_date':date,
																'user_id':user.id,
																'state':state,
																'information_request_ref': o.information_request_id
																})
				
				self.write(cr,uid,ids,{'comment_remark':None})
			else :
				raise osv.except_osv(('Alert!'),('Please Enter Remark.'))
		return True

	def customer_search_pop_up(self, cr, uid, ids, context=None):
		if context is None: context = {}
		context = dict(context, active_ids=ids, active_model=self._name)
		res_create_id = self.pool.get('information.customer.search').create(cr, uid, {}, context=context)
		return {
			'name': _('Customer Search'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': False,
			'res_model': 'information.customer.search',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'res_id': res_create_id,
			'context': context,
		}

	def reload_information_request(self, cr, uid, ids, context=None):
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_cid', 'view_info_request_form_crm')
		view_id = view and view[1] or False
		return {
			'name': _('Information Request'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'product.information.request',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': ids[0],
		}	

product_information_request()

class product_information_request_notes_line(osv.osv):
	_name = 'product.information.request.notes.line'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'information_request_ref': fields.char('Information Request',size=20),
		'request_id':fields.many2one('product.information.request','Request Id',ondelete='cascade'),
		'user_id':fields.many2one('res.users','User Name'),
		'state':fields.selection([
									('new','New'),
									('open','Opened'),
									('progress','Resource Assigned'),
									('closed','Closed'),
									('cancel','Cancelled')
									],'State'),
		'comment_date':fields.datetime('Comment Date & Time'),
		'comment':fields.text('Comment',size=400),
	}

	_defaults = {
		'company_id': _get_company
	}

product_information_request_notes_line()