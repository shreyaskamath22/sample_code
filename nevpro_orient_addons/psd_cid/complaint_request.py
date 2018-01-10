from osv import osv,fields
from openerp.tools.translate import _
from datetime import date,datetime, timedelta
import time

class product_complaint_request(osv.osv):
	_name='product.complaint.request'	
	_rec_name='complaint_request_id'
	_order = 'create_date desc'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_user(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).id	

	def _get_datetime(self,cr,uid,context=None):
		return time.strftime("%Y-%m-%d %H:%M:%S")

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),	
		'active':fields.boolean('Active', select=True),
		'state': fields.selection([('new', 'New'),
								   ('opened', 'Opened'),
								   ('resource_assigned', 'Resource Assigned'),
								   ('cancel', 'Cancelled'),
								   ('closed', 'Closed'),
								   ], 'Status', select=True),
		'call_type': fields.selection([('inbound', 'Inbound'),
								   ('outbound', 'Outbound'),
								   ], 'Call Type'),
		'requested_date': fields.datetime("Request Date"),
		'created_by': fields.many2one('res.users','Created by'),
		'customer': fields.char('Customer/Company Name*',size=32),
		'customer_id': fields.char('Customer ID',size=32),
		'customer_type': fields.selection([('existing', 'Existing'),
										   ('new','New'),
										   ], 'Customer Type'),
		'complaint_line_ids': fields.one2many('product.complaint.request.line', 'complaint_id', 'Locations & Products'),
		'remark': fields.text('Remarks', size=100),
		'psd_company_id': fields.many2one('res.company', 'PSD Office'),
		'complaint_request_id': fields.char('Request ID',size=30),
		'global_search_id': fields.many2one('ccc.branch', 'Global Search'),		
		'partner_id': fields.many2one('res.partner','Customer'),	
		'request_type': fields.selection([
									      ('lead_request','Existing Customer Request'),
										  ('complaint_request','Complaint Request'),
										  ('renewal_request','Renewal Request'),
							              ('information_request','Miscellaneous Request'),
										  ('product', 'Product Request'),
										  ('complaint', 'Complaint Request'),
										  ('information', 'Information Request'),
										 ],'Request Type'),
		'employee_id': fields.many2one('hr.employee', 'Assign Resource'),
		'cancel_request': fields.boolean('Cancel Request'),
		'cancellation_reason': fields.char('Cancellation Reason*',size=50),
		'resolution':fields.text('Resolution*',size=500),
		'closed_date':fields.datetime('Closed Date'),
		'comment_remark':fields.text('Comments',size=500),
		'notes_line': fields.one2many('product.complaint.request.notes.line','request_id','Comments'),
		'location_branch': fields.selection([('same', 'Same'),
											 ('different', 'Different'),
											 ('crm', 'CRM')
											 ],'Location Branch'),
		'parent_request': fields.many2one('product.complaint.request','Parent Request'),
	}

	_defaults = {
		'company_id': _get_company,
		'active': True,
		'call_type' : 'inbound',
		'created_by': lambda self, cr, uid, context: self._get_user(cr, uid, context),
		'requested_date':_get_datetime,
		'state': 'new',
		'customer_type': 'new',
		'request_type': 'complaint'
	}

	def _get_default_date(self, cr, uid, context=None):
		if context is None:
			context = {}
		if 'date' in context:
			return context['date'] + time.strftime(' %H:%M:%S')
		return time.strftime('%Y-%m-%d %H:%M:%S')

	def assign_resource(self,cr,uid,ids,context=None):	
		crm_lead_obj = self.pool.get('crm.lead')
		customer_line_obj = self.pool.get('customer.line')
		res = self.write(cr,uid,ids,{'state':'resource_assigned'})
		partner_obj = self.pool.get('res.partner')
		customer_line_id = False
		crm_ids = crm_lead_obj.search(cr, uid, [('complaint_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'progress'}, context=context)
		rec = self.browse(cr, uid, ids[0])	
		main_id = rec.id
		search_location_company = self.pool.get('product.complaint.request.line').search(cr,uid,[('complaint_id','=',main_id)])
		browse_location_company = self.pool.get('product.complaint.request.line').browse(cr,uid,search_location_company[0]).pci_office.id
		if rec.customer_type == 'existing':
			if rec.employee_id:
				addr_id = rec.complaint_line_ids[0].location_id.address_id.id
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
		self.sync_update_complaint_request(cr,uid,ids,context=context)
		return res

	def cancel_complaint_request(self,cr,uid,ids,context=None):	
		crm_lead_obj = self.pool.get('crm.lead')
		rec = self.browse(cr, uid, ids[0])
		main_id =rec.id
		search_location_company = self.pool.get('product.complaint.request.line').search(cr,uid,[('complaint_id','=',main_id)])
		browse_location_company = self.pool.get('product.complaint.request.line').browse(cr,uid,search_location_company[0]).pci_office.id
		if not rec.cancellation_reason:
			raise osv.except_osv(_('Warning!'),_("Please enter reason for cancellation!"))
		res = self.write(cr,uid,ids,{'state':'cancel'})
		crm_ids = crm_lead_obj.search(cr, uid, [('complaint_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'cancel'}, context=context)
		context.update({'branch':browse_location_company})
		self.sync_cancel_complaint_request(cr,uid,ids,context=context)
		return res

	def product_complaint_request_cancel(self,cr,uid,ids,context=None):	
		primary_data = self.browse(cr, uid, ids[0])
		phone_psd_obj = self.pool.get('phone.number.new.psd')
		models_data = self.pool.get('ir.model.data')
		search_numbers = phone_psd_obj.search(cr,uid,[('complaint_request_id','=',ids[0])])
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

	def customer_search_pop_up(self, cr, uid, ids, context=None):
		if context is None: context = {}
		context = dict(context, active_ids=ids, active_model=self._name)
		res_create_id = self.pool.get("complaint.customer.search").create(cr, uid, {}, context=context)
		return {
			'name': _('Customer Search'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': False,
			'res_model': 'complaint.customer.search',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'res_id': res_create_id,
			'context': context,
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
				self.pool.get('product.complaint.request.notes.line').create(cr,uid,{
																		'request_id':o.id,
																		'comment':o.comment_remark,
																		'comment_date':date,
																		'user_id':user.id,
																		'state':state,
																		'complaint_request_ref': o.complaint_request_id
																		})
				self.write(cr,uid,ids,{'comment_remark':None})
			else :
				raise osv.except_osv(('Alert!'),('Please Enter Remark.'))
		return True

	def close_complaint_request(self,cr,uid,ids,context=None):	
		models_data = self.pool.get('ir.model.data')
		global_search_obj = self.pool.get('ccc.branch')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		contact_number = False
		branch_id = False
		form_id = models_data.get_object_reference(cr, uid, 'psd_cid', 'view_ccc_branch_form_psd_inherit_new')
		global_search_id = global_search_obj.create(cr,uid,{'enquiry_type': 'complaint_request'},context=context)
		complaint_req_data = self.browse(cr, uid, ids[0])
		if complaint_req_data.state != 'new':
			if complaint_req_data.complaint_line_ids:
				for comp_line in complaint_req_data.complaint_line_ids:
					contact_number = comp_line.loc_phone_id and comp_line.loc_phone_id.number
					branch_id = comp_line.pci_office.id
		date_age = global_search_obj.calculate_date_age(cr,uid,ids,complaint_req_data.requested_date,complaint_req_data.closed_date)
		if complaint_req_data.state == 'resource_assigned':
			comp_req_state = 'progress'
		elif complaint_req_data.state == 'opened':
			comp_req_state = 'open'
		else:
			comp_req_state = complaint_req_data.state
		branch_line_vals =  {       
				'ccc_complaint_id': global_search_id,
				'request_id': complaint_req_data.complaint_request_id,
				'customer_name': complaint_req_data.customer,
				'branch_id': branch_id,
				'origin': complaint_req_data.company_id.name,
				'request_type_psd': 'complaint_request',
				'date_age': date_age,
				'state': comp_req_state,
				'contact_number': contact_number,
				'sort_date': complaint_req_data.requested_date,
				'created_by': complaint_req_data.created_by.id,
				'employee_id': complaint_req_data.employee_id.id,
				'complaint_request_id': ids[0]
		}
		branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
		return {
		   'name':'Global Search',
		   'view_mode': 'form',
		   'view_id': form_id[1],
		   'view_type': 'form',
		   'res_model': 'ccc.branch',
		   'res_id': global_search_id,
		   'type': 'ir.actions.act_window',
		   'target': 'current',
		   'context':context
		}

	def process_complaint_request(self, cr, uid, ids, context=None):
		res = False
		pro_ids = []
		pro_ids.append(ids[0])
		complaint_line_obj = self.pool.get('product.complaint.request.line')
		seq_obj = self.pool.get('ir.sequence')
		models_data = self.pool.get('ir.model.data')
		global_search_obj = self.pool.get('ccc.branch')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		crm_lead_obj = self.pool.get('crm.lead')
		rec = self.browse(cr,uid,ids[0])

		cust_prefix = False
		if rec.state == 'resource_assigned':
			if not rec.resolution:
				raise osv.except_osv(_('Warning!'),_("Please enter resolution!"))
			crm_ids = crm_lead_obj.search(cr, uid, [('complaint_request_id','=', ids[0])], context=context)
			for crm_id in crm_ids:
				crm_lead_obj.write(cr, uid, crm_id, {'state':'closed'}, context=context)	
			res = self.write(cr, uid, ids[0], {'state':'closed','closed_date':datetime.now()}, context=context)
			return res
		complaint_line_ids = rec.complaint_line_ids
		if not complaint_line_ids:
			raise osv.except_osv(_('Warning!'),_("Please select locations & products!"))

		cust_id = self.pool.get('res.partner').search(cr,uid,[('ou_id','=',rec.customer_id)])
		cust_brw = self.pool.get('res.partner').browse(cr,uid,cust_id)[0]
		company_id = cust_brw.company_id.id

		abc = complaint_line_obj.search(cr,uid,[('complaint_id','=',rec.id)])
		for each in abc:
			complaint_line_obj.write(cr,uid,each,{'pci_office':company_id})
			cr.commit()

		for each in complaint_line_ids:
			if not each.location_id or not each.product_id or not each.pci_office:
				raise osv.except_osv(_('Warning!'),_("Some locations are empty!"))
		last_item = complaint_line_ids[-1]
		for each in complaint_line_ids:
			req_ids = crm_lead_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id)], context=context)	
			if rec.customer_type == 'existing':
				cr_inc_no = len(req_ids)+1
				if cr_inc_no >= 0 and cr_inc_no <= 9:
					st_cr_inc_no = '00'+str(cr_inc_no)
				elif cr_inc_no >= 10 and cr_inc_no <= 99:
					st_cr_inc_no = '0'+str(cr_inc_no)
				elif cr_inc_no >= 100 and cr_inc_no <= 999:	
					st_cr_inc_no = str(cr_inc_no)	
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
				cr_seq = rec.company_id.pcof_key + 'PC' + customer_inc_no + st_cr_inc_no
			else:
				# cr_inc_no = 1
				cr_inc_no = self.pool.get('ir.sequence').get(cr, uid, 'product.complaint.request')
				st_cr_inc_no = '000000000'+str(cr_inc_no)
				cr_seq = rec.company_id.pcof_key + 'PCN' + st_cr_inc_no
			if each != last_item:
				comp_req_vals = {
							'customer_type': rec.customer_type,
							'requested_date':datetime.now(),
							'customer': rec.customer, 
							'customer_id': rec.customer_id,
							'state': 'opened',
							'complaint_request_id': cr_seq,
							'parent_request': rec.id
						}
				if rec.customer_type == 'existing':
					comp_req_vals.update({'partner_id': rec.partner_id.id})
				comp_id = self.create(cr, uid, comp_req_vals, context=context)
				complaint_line_vals = {
					'location_id': each.location_id.id,
					'product_id': each.product_id.id,
					'loc_contact_id': each.loc_contact_id.id,
					'loc_phone_id': each.loc_phone_id.id,
					'pci_office': each.pci_office.id,
					'remark': each.remark,
					'complaint_id': comp_id
				}
				complaint_line_obj.create(cr, uid, complaint_line_vals, context=context)
				complaint_line_obj.unlink(cr, uid, each.id, context=context)
				pro_ids.append(comp_id)
				if rec.partner_id:
					crm_lead_vals = {
						'inquiry_no': cr_seq,
						'type_request': 'complaint_request_psd',
						'state': 'open',
						'partner_id': rec.partner_id.id,
						'created_by_global': rec.created_by.name,
						'inspection_date':	rec.requested_date,
						'complaint_request_id': comp_id,										
					}
					crm_lead_obj.create(cr, uid, crm_lead_vals, context=context) 
			else:
				res = self.write(cr,uid,ids,
					{
						'state': 'opened',
						'requested_date': datetime.now(),
						'complaint_request_id': cr_seq,
						'parent_request': rec.id
					},context=context)	
				if rec.partner_id:
					crm_lead_vals = {
						'inquiry_no': cr_seq,
						'type_request': 'complaint_request_psd',
						'state': 'open',
						'partner_id': rec.partner_id.id,
						'created_by_global': rec.created_by.name,
						'inspection_date':	rec.requested_date,
						'complaint_request_id': ids[0],										
					}
					crm_lead_obj.create(cr, uid, crm_lead_vals, context=context) 
		global_search_vals = {
			'enquiry_type': 'complaint_request'
		}	
		global_search_id=global_search_obj.create(cr,uid,global_search_vals,context=context)
		for each in pro_ids:
			comp_data = self.browse(cr, uid, each)
			if comp_data.company_id.establishment_type == 'crm':
				location_branch = 'crm'
			elif comp_data.complaint_line_ids[0].pci_office.id == comp_data.company_id.id:
				location_branch = 'same'
			else:
				location_branch = 'different'
			self.write(cr, uid, comp_data.id, {'location_branch': location_branch}, context=context)
			date_age = global_search_obj.calculate_date_age(cr,uid,ids,comp_data.requested_date,comp_data.closed_date)
			if comp_data.state == 'resource_assigned':
				comp_req_state = 'progress'
			elif comp_data.state == 'opened':
				comp_req_state = 'open'
			else:
				comp_req_state = comp_req.state
			for comp_line in comp_data.complaint_line_ids:
				branch_id = comp_line.pci_office.id
				contact_number = comp_line.loc_phone_id.number
			branch_line_vals =  {       
					'ccc_complaint_id': global_search_id,
					'request_id': comp_data.complaint_request_id,
					'customer_name': comp_data.customer,
					'branch_id': branch_id,
					'origin': comp_data.company_id.name,
					'request_type_psd': 'complaint_request',
					'date_age': date_age,
					'state': comp_req_state,
					'contact_number': contact_number,
					'sort_date': comp_data.requested_date,
					'created_by': rec.created_by.id,
					'employee_id': rec.employee_id.id,
					'complaint_request_id': comp_data.id
			}
			branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
			branch_id_sync = branch_id
			context.update({'branch_id_sync':branch_id_sync})
			self.sync_complaint_request(cr,uid,ids,context=context)
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

	def add_new_complaint_locations(self,cr,uid,ids,context=None):		
		if context is None: context = {}
		return {
			'name': _('New Cutomer Location'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': False,
			'res_model': 'complaint.location.addition',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'context': context,                               
		}		
				
product_complaint_request()		

class product_complaint_request_line(osv.osv):
	_name='product.complaint.request.line'     
	_rec_name = 'location_id'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def onchange_batch(self,cr,uid,ids,batch_no,context=None):
		data={}
		mfg_date = self.pool.get('res.batchnumber').browse(cr,uid,batch_no).manufacturing_date
		data.update({'mfg_date': mfg_date})
		return {'value':data}

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'complaint_id': fields.many2one('product.complaint.request', 'Complaint',ondelete='cascade'),
		'remark': fields.text('Remarks', size=100),
		'product_id': fields.many2one('product.product', 'Product Name'),
		'location_id': fields.many2one('product.complaint.locations', 'Address'),
		'contact_person': fields.char('Contact Person',size=100),
		'phone_number': fields.char('Phone Number',size=100),
		'loc_contact_id': fields.many2one('complaint.locations.contact', 'Contact Person'),
		'loc_phone_id':fields.many2one('phone.number.new.psd','Phone Number'),
		'pci_office': fields.many2one('res.company','PCI Office'),
		'customer_type': fields.selection([('existing','Existing Customer'),('new','New Customer')],'Customer Type'),
		'complaint_request_ref': fields.char('Complaint Request',size=50),
		'batch_no':fields.many2one('res.batchnumber','Batch'),
		'mfg_date':fields.date('Mfg Date'),
	}

	_defaults = {
		'company_id': _get_company
	}
	
	def onchange_location_id(self,cr,uid,ids,location_id,context=None):
		data = {}
		complaint_location_obj = self.pool.get('product.complaint.locations')
		locations_contact_obj = self.pool.get('complaint.locations.contact')
		location_addition_obj = self.pool.get('complaint.location.addition')
		partner_address_obj = self.pool.get('res.partner.address')
		if location_id :
			contact_person = ''
			phone_number = ''
			location_data = complaint_location_obj.browse(cr, uid, location_id)
			if location_data.complaint_id.customer_type == 'existing':
				pci_office = location_data.complaint_id.partner_id.company_id.id
				addr_data = partner_address_obj.browse(cr, uid, location_data.address_id.id)
				if addr_data.first_name and addr_data.last_name and not addr_data.middle_name:
					contact_person =  addr_data.first_name+' '+ addr_data.last_name
				if addr_data.first_name and addr_data.last_name and addr_data.middle_name:
					contact_person =  addr_data.first_name+' '+addr_data.middle_name+' '+addr_data.last_name 
				if addr_data.phone_m2m_xx:
					phone_number = addr_data.phone_m2m_xx.name
				data.update(
					{
						'customer_type': 'existing',
						'contact_person': contact_person,
						'phone_number': phone_number,
						'pci_office': pci_office, 
					})
				return {'value': data}
			else:
				pci_office = location_data.complaint_id.company_id.id
				contact_person_id = locations_contact_obj.search(cr, uid, [
					('complaint_id','=',location_data.complaint_id.id),
					('loc_id','=',location_data.id)], 
					context=context)
				phone = complaint_location_obj.browse(cr, uid, location_id).addition_id.phone
				if phone:
					phone_number = phone.number
				else:
					phone_number = False
				contact_person = locations_contact_obj.browse(cr, uid, contact_person_id[0]).name
				data.update(
					{
						'customer_type': 'new',
						'contact_person': contact_person,
						'phone_number': phone_number,
						'pci_office': pci_office, 
					})
				return {'value': data}
		else:
			return {'value': data}

	def create(self, cr, uid, vals, context=None):
		complaint_id = vals.get('complaint_id')
		complaint_request_id = self.pool.get('product.complaint.request').browse(cr, uid, complaint_id).complaint_request_id
		vals.update({'complaint_request_ref': complaint_request_id})
		return super(product_complaint_request_line, self).create(cr, uid, vals, context=context)

	def select_cust_details(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids[0],{'select_cust':True},context)
		return True

	def deselect_cust_details(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids[0],{'select_cust':False})
		return True        

product_complaint_request_line()

class product_complaint_locations(osv.osv):
	_name='product.complaint.locations' 

	_columns = {
	'company_id':fields.many2one('res.company','Company ID'),
	'complaint_id': fields.many2one('product.complaint.request', 'Complaint ID'),
	'name': fields.char('Address', size=200),
	'address_id': fields.many2one('res.partner.address','Address ID'),
	'addition_id': fields.many2one('complaint.location.addition','Addition ID')

	}

	# def name_get(self, cr, uid, ids, context=None):
	# 	print"in get"
	# 	# context = context or {}
	# 	if context.get('from_complaint_contact'):
	# 		print"context contact",context
	# 		if not ids:
	# 			return []
	# 		if isinstance(ids, (int, long)):
	# 			ids = [ids]
	# 		loc_data = self.browse(cr, uid, ids)
	# 		print"loc_data",loc_data
	# 		contact_person = loc_data[0].contact_person
	# 		res = []				
	# 		res.append((ids, contact_person))
	# 		print"res",res
	# 	return res
	# 	# if context.get('from_complaint_phone'):
	# 	# 	print"context phone",context
	# 	# 	if not ids:
	# 	# 		return []
	# 	# 	if isinstance(ids, (int, long)):
	# 	# 		ids = [ids]
	# 	# 	reads = self.read(cr, uid, ids, ['name', 'contact_number'], context=context)
	# 	# 	res = []
	# 	# 	for record in reads:
	# 	# 		name = record['name']
	# 	# 		if record['contact_number']:
	# 	# 			name = record['contact_number']
	# 	# 		res.append((record['id'], name))
	# 	# 	return res
	# 	if not context.get('from_complaint_contact'):
	# 		return super(product_complaint_locations, self).name_get(cr, uid, ids, context)

	# def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
	# 	print"in search"
	# 	if not args:
	# 		args = []
	# 	if context.get('from_complaint_contact') or context.get('from_complaint_phone'): 
	# 		ids = []
	# 		if name:
	# 			ids = self.search(cr, uid, [('name', '=like', "%"+name)] + args, limit=limit)
	# 			if not ids:
	# 				ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit)
	# 		else:
	# 			ids = self.search(cr, uid, args, context=context, limit=limit)		
	# 		return self.name_get(cr, uid, ids, context=context) 
	# 	return super(product_complaint_locations, self).name_search(cr, uid, name=name, args=args, operator=operator, context=context, limit=limit)

product_complaint_locations()	

class complaint_locations_contact(osv.osv):
	_name='complaint.locations.contact'

	_columns = {
	'company_id':fields.many2one('res.company','Company ID'),
	'complaint_id': fields.many2one('product.complaint.request', 'Complaint ID'),
	'name': fields.char('Contact Person', size=50),
	'loc_id': fields.many2one('product.complaint.locations', 'Complaint ID'),
	}

complaint_locations_contact()


class product_complaint_request_notes_line(osv.osv):
	_name = 'product.complaint.request.notes.line'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'complaint_request_ref': fields.char('Complaint Request',size=20),
		'request_id':fields.many2one('product.complaint.request','Request Id',ondelete='cascade'),
		'user_id':fields.many2one('res.users','User Name'),
		'state':fields.selection([
									('new','New'),
									('opened','Opened'),
									('resource_assigned','Resource Assigned'),
									('closed','Closed'),
									('cancel','Cancelled')
									],'State'),
		'comment_date':fields.datetime('Comment Date & Time'),
		'comment':fields.text('Comment',size=400),
	}

	_defaults = {
		'company_id': _get_company
	}

product_complaint_request_notes_line()