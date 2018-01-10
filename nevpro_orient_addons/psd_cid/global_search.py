from osv import osv,fields
from tools.translate import _
from datetime import datetime, date
import time
from datetime import timedelta
from time import strftime
from dateutil.relativedelta import relativedelta

class ccc_branch(osv.osv):
	_inherit = "ccc.branch"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'inquiry_type': fields.selection([('customer', 'Customer'),
										  ('all_request','All Requests'),
										  ('new_cust','New Customer Request'),
										  ('lead_request','Existing Customer Request'),
										  ('complaint_request','Complaint Request'),
										  ('renewal_request','Renewal Request'),
										  ('information_request','Miscellaneous Request'),
										  ('generic_request','Generic Request'),
										  ('product_request','Product Requests'),
										  ('product_complaint_request','Product Complaint Request'),
										  ('product_information_request','Product Information Requests'),
										 ],'Search For *',select=1,required=True),
		'enquiry_type': fields.selection([
							('customers','Customers'),
							('product_request','Product Requests'),
							('complaint_request','Product Complaint Request'),
							('information_request','Product Information Requests'),
							('all_requests','All Requests'),
							],'Search For'),
		'apartment': fields.char('Unit/Apartment No',size=25),
		'street': fields.char('Street',size=25),
		'customer_ids': fields.one2many('ccc.branch.request.line','ccc_customer_id','Customers'),
		'product_req_ids': fields.one2many('ccc.branch.request.line','ccc_product_id','Product Requests'),
		'complaint_req_ids': fields.one2many('ccc.branch.request.line','ccc_complaint_id','Complaint Requests'),
		'information_req_ids': fields.one2many('ccc.branch.request.line','ccc_information_id','Information Requests'),
	}	

	_defaults = {
		'enquiry_type': 'all_requests',
		'company_id': _get_company,
	}


	def calculate_date_age(self, cr, uid, ids, request_date, closed_date,context=None):      
		request_date_dt= datetime.strptime(request_date[0:10], "%Y-%m-%d").date()
		request_date_month = request_date_dt.strftime("%B")
		today = datetime.today().date()
		date_age = False
		if closed_date:
			closed_date_dt= datetime.strptime(closed_date[0:10], "%Y-%m-%d").date()
			closed_date_month = closed_date_dt.strftime("%B")
			date_age = relativedelta(closed_date_dt, request_date_dt)
		else:
			date_age = relativedelta(today, request_date_dt)
		formatted_date = ''
		if date_age.years == 0 and date_age.months and date_age.days:
			formatted_date = "{0.months} mon {0.days} days ".format(date_age)
		if date_age.years and date_age.months == 0 and date_age.days:
			formatted_date = "{0.years} years {0.days} days ".format(date_age)
		if date_age.years and date_age.months and date_age.days == 0:
			formatted_date = "{0.years} years {0.months} mon ".format(date_age)
		if date_age.years == 0 and date_age.months ==0 and date_age.days:
			formatted_date = "{0.days} days ".format(date_age)
		if date_age.years and date_age.months == 0 and date_age.days == 0:
			formatted_date = "{0.years} years ".format(date_age)
		if date_age.years == 0 and date_age.months and date_age.days == 0:
			formatted_date = "{0.months} mon ".format(date_age)
		if date_age.years == 0 and date_age.months == 0 and date_age.days == 0:
			formatted_date = "{0.days} days ".format(date_age)
		formatted_date = str(request_date[8:10]) + '/' + str(request_date_month[:3]) + ':' + str(formatted_date)
		return formatted_date

	def onchange_inquiry_type(self,cr,uid,ids,inquiry_type,context=None):
		v = {}
		req_line = []
		assign_line = []
		if inquiry_type:
			v['customer_id'] = None
			v['req_id'] = None
			v['service_area_cust'] = None
			v['contact_name_cust'] = None
			v['partner_name_cust'] = None
			v['city_id'] = None
			v['mobile_cust'] = None
			v['phone_cust'] = None
			v['pincode'] = None
			v['user_id_cust'] = None
			v['branch_id'] = None
			v['due_date_from_cust'] = None
			v['due_date_to_cust'] = None
			v['check_state'] = False
			v['customer_category_id'] = None
			v['state'] = None
			v['contract_number'] =None
			v['check'] = False
			v['cse'] = None
			
			v['request_line'] = []
			v['assign_line'] = []
			v['update_line'] =[]

			v['customer_ids'] = []
			v['product_req_ids'] =[]	
			v['complaint_req_ids'] =[]
			v['information_req_ids'] =[]
			return {'value':v}

	def onchange_enquiry_type(self,cr,uid,ids,enquiry_type,context=None):
		vals = {}
		if enquiry_type:
			vals['customer_id'] = None
			vals['req_id'] = None
			vals['contact_name_cust'] = None
			vals['partner_name_cust'] = None
			vals['city_id'] = None
			vals['phone_cust'] = None
			vals['pincode'] = None
			vals['branch_id'] = None
			vals['due_date_from_cust'] = None
			vals['due_date_to_cust'] = None
			vals['state'] = None
			vals['check'] = False
			vals['cse'] = None
			vals['customer_ids'] = []
			vals['product_req_ids'] =[]	
			vals['complaint_req_ids'] =[]
			vals['information_req_ids'] =[]
			vals['request_line'] = []
			return {'value':vals}

	def clear_crm_request_psd(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		self.write(cr,uid, ids[0],
			{
				'contact_name_cust':None,
				'partner_name_cust':None,
				'customer_id':None,
				'cse':None,
				'req_id':None,
				'location_name':None,
				'location_name':None,
				'building':None,
				'subarea':None,
				'landmark':None,
				'service_area_cust':None,
				'city_id':None,
				'mobile_cust':None,
				'phone_cust':None,
				'pincode':None,'branch_id':None,
				'due_date_from_cust':None,'due_date_to_cust':None,
				'check_state':False,'contract_number':None,
				'customer_category_id':None,
				'user_id_cust':None,
				'state':None,'check':False,
				'customer_id':None,
				'req_id':None,
				'location_name':None,
				'location_name':None,
				'building':None,
				'sub_area':None,
				'landmark':None,
				'apartment':None,
				'street': None
			},context=context)		
		return True

	def get_customers(self,cr,uid,ids,context=None):
		res = False
		true_items = []
		domain = []
		display_ids = []
		from_date = False
		to_date = False
		partner_obj = self.pool.get('res.partner')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		req_line_ids = branch_req_line_obj.search(cr, uid, [('ccc_customer_id','=',ids)], context=context)
		branch_req_line_obj.unlink(cr, uid, req_line_ids, context=context)
		rec = self.browse(cr, uid, ids)
		if rec.partner_name_cust:
			true_items.append('partner_name_cust')
		if rec.customer_id:
			true_items.append('customer_id')    
		if rec.contact_name_cust:
			true_items.append('contact_name_cust')
		if rec.phone_cust:
			true_items.append('phone_cust')     
		if rec.apartment:
			true_items.append('apartment')
		if rec.building:
			true_items.append('building')
		if rec.subarea:
			true_items.append('subarea')
		if rec.landmark:
			true_items.append('landmark') 
		if rec.street:
			true_items.append('street')
		if rec.city_id:
			true_items.append('city_id')    
		if rec.pincode:
			true_items.append('pincode')
		if rec.branch_id:
			true_items.append('branch_id')  
		if rec.cse:
			true_items.append('cse') 
		for true_item in true_items:    
			if true_item == 'partner_name_cust':
				domain.append(('name', 'ilike', rec.partner_name_cust))
			if true_item == 'customer_id':
				domain.append(('ou_id', 'ilike', rec.customer_id))  
			if true_item == 'contact_name_cust':
				domain.append(('contact_name', 'ilike', rec.contact_name_cust))   
			if true_item == 'phone_cust':
				domain.append(('phone_many2one.number', 'ilike', rec.phone_cust)) 
			if true_item == 'apartment':
				domain.append(('apartment', 'ilike', rec.apartment))  
			if true_item == 'building':
				domain.append(('building', 'ilike', rec.building))      
			if true_item == 'subarea':
				domain.append(('sub_area', 'ilike', rec.subarea))
			if true_item == 'landmark':
				domain.append(('landmark', 'ilike', rec.landmark))	
			if true_item == 'street':
				domain.append(('street', 'ilike', rec.street))    
			if true_item == 'city_id':
				domain.append(('city_id', '=', rec.city_id.id))
			if true_item == 'pincode':
				domain.append(('zip', 'ilike', rec.pincode))  
			if true_item == 'branch_id':
				domain.append(('company_id', '=', rec.branch_id.id))  
			if true_item == 'cse':
				domain.append(('main_cse', '=', rec.cse.id))
		if rec.due_date_from_cust:
			from_date = datetime.strptime(rec.due_date_from_cust, "%Y-%m-%d")	
		if rec.due_date_to_cust:
			to_date = datetime.strptime(rec.due_date_to_cust, "%Y-%m-%d")	
		if from_date and not to_date:	
			domain.append(('customer_since', '>=', from_date))
		elif not from_date and to_date:
			domain.append(('customer_since', '<=', to_date))	
		elif from_date and to_date:				
			domain.append(('customer_since', '>=', from_date))
			domain.append(('customer_since', '<=', to_date))	
		domain.append(('customer', '=', True))
		domain.append(('company_id', '=', rec.company_id.id))
		display_ids = partner_obj.search(cr, uid, domain, context=context)
		if display_ids:
			res = []
			self.write(cr, uid, [ids], {'check':False}, context=context)
			for display_id in display_ids:
				addrs_items = []
				cust_address = ''
				partner = partner_obj.browse(cr,uid,display_id)
				if partner.apartment:
					addrs_items.append(partner.apartment)
				if partner.building:
					addrs_items.append(partner.building)
				if partner.sub_area:
					addrs_items.append(partner.sub_area)
				if partner.landmark:
					addrs_items.append(partner.landmark)
				if partner.street:
					addrs_items.append(partner.street)
				if partner.city_id:
					addrs_items.append(partner.city_id.name1)
				if partner.district:
					addrs_items.append(partner.district.name)
				if partner.tehsil:
					addrs_items.append(partner.tehsil.name)
				if partner.state_id:
					addrs_items.append(partner.state_id.name)
				if partner.zip:
					addrs_items.append(partner.zip)
				if addrs_items:
					last_item = addrs_items[-1]
					for item in addrs_items:
						if item!=last_item:
							cust_address = cust_address+item+','+' '
						if item==last_item:
							cust_address = cust_address+item
				res_vals =  {       
						'ccc_customer_id': ids,
						'customer_id': partner.ou_id,
						'customer_name': partner.name,
						'complete_address': cust_address,
						'contact_name': partner.contact_name,
						'branch_id': partner.company_id.id,
						'contact_number': partner.phone_many2one.number,
						'customer_since': partner.show_customer_since or False,
						'partner_id': partner.id
					}
				branch_re_id = branch_req_line_obj.create(cr, uid, res_vals, context=context)
				res.append(branch_re_id)
			return res
		else:
			self.write(cr, uid, [ids], {'check':True}, context=context)
		return res		

	def get_product_requests(self,cr,uid,ids,context=None):
		res = False
		true_items = []
		domain = []
		display_ids = []
		final_display_ids = []
		branch_pro_ids = []
		from_date = False
		to_date = False
		product_req_obj = self.pool.get('product.request')
		product_req_loc_obj = self.pool.get('product.request.locations')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		req_line_ids = branch_req_line_obj.search(cr, uid, [('ccc_product_id','=',ids)], context=context)
		branch_req_line_obj.unlink(cr, uid, req_line_ids, context=context)
		rec = self.browse(cr, uid, ids)
		if rec.partner_name_cust:
			true_items.append('partner_name_cust')
		if rec.customer_id:
			true_items.append('customer_id')    
		if rec.req_id:
			true_items.append('req_id')  
		if rec.contact_name_cust:
			true_items.append('contact_name_cust')
		if rec.mobile_cust:
			true_items.append('mobile_cust')   
		if rec.phone_cust:
			true_items.append('phone_cust')  
		if rec.apartment:
			true_items.append('apartment')
		if rec.building:
			true_items.append('building')
		if rec.subarea:
			true_items.append('subarea')
		if rec.landmark:
			true_items.append('landmark') 
		if rec.street:
			true_items.append('street')
		if rec.city_id:
			true_items.append('city_id')    
		if rec.pincode:
			true_items.append('pincode')
		if rec.branch_id:
			true_items.append('branch_id')  
		if rec.cse:
			true_items.append('cse') 
		if rec.state:
			true_items.append('state')	 
		if true_items:    
			for true_item in true_items:    
				if true_item == 'partner_name_cust':
					domain.append(('name', 'ilike', rec.partner_name_cust))
				if true_item == 'req_id':
					domain.append(('product_request_id', 'ilike', rec.req_id))  
				if true_item == 'customer_id':
					domain.append(('customer_id', 'ilike', rec.customer_id))  
				if true_item == 'contact_name_cust':
					domain.append(('|'))
					domain.append(('first_name', 'ilike', rec.contact_name_cust))
					domain.append(('|'))
					domain.append(('middle_name', 'ilike', rec.contact_name_cust))
					domain.append(('last_name', 'ilike', rec.contact_name_cust))
				if true_item == 'mobile_cust':
					domain.append(('|'))
					domain.append(('phone_many2one.number', 'ilike', rec.mobile_cust))
					domain.append(('phone_many2one_new.number', 'ilike', rec.mobile_cust))
				if true_item == 'phone_cust':
					domain.append(('|'))
					domain.append(('phone_many2one.number', 'ilike', rec.phone_cust))
					domain.append(('phone_many2one_new.number', 'ilike', rec.phone_cust))
				if true_item == 'apartment':
					domain.append(('apartment', 'ilike', rec.apartment))  
				if true_item == 'building':
					domain.append(('building', 'ilike', rec.building))      
				if true_item == 'subarea':
					domain.append(('sub_area', 'ilike', rec.subarea))
				if true_item == 'landmark':
					domain.append(('landmark', 'ilike', rec.landmark))	
				if true_item == 'street':
					domain.append(('street', 'ilike', rec.street))    
				if true_item == 'city_id':
					domain.append(('city_id', '=', rec.city_id.id))
				if true_item == 'pincode':
					domain.append(('zip', 'ilike', rec.pincode))  
				if true_item == 'cse':
					domain.append(('employee_id', '=', rec.cse.id))    
				if true_item == 'state':
					if rec.state == 'new':
						state = 'new'
					elif rec.state == 'open':
						state = 'open'
					elif rec.state == 'progress':
						state = 'assigned'
					elif rec.state == 'closed':
						state = 'closed'
					elif rec.state == 'cancel':
						state = 'cancel'
					domain.append(('state', '=', state))
		if rec.due_date_from_cust:
			from_date = datetime.strptime(rec.due_date_from_cust, "%Y-%m-%d")
			#from_date = from_date.strftime('%Y-%m-%d 24:00:00')	
			from_date = from_date.strftime('%Y-%m-%d')
		if rec.due_date_to_cust:
			to_date = datetime.strptime(rec.due_date_to_cust, "%Y-%m-%d")
			# temp_to_date = datetime.strptime(rec.due_date_to_cust, "%Y-%m-%d")
			# to_date = temp_to_date+relativedelta(hours=23)
			#to_date = to_date.strftime('%Y-%m-%d 24:00:00')	
			to_date = to_date.strftime('%Y-%m-%d')
		if from_date and not to_date:
			domain.append(('request_date', '>=', from_date))	
		elif not from_date and to_date:
			domain.append(('request_date', '<=', to_date))	
		elif from_date and to_date:				
			domain.append(('request_date', '>=', from_date))
			domain.append(('request_date', '<=', to_date))	
		display_ids = product_req_obj.search(cr, uid, domain, context=context)
		if rec.branch_id:
			rec_loc_ids = product_req_loc_obj.search(cr, uid, [('branch_id.id','=',rec.branch_id.id)], context=context)
			for rec_loc_id in rec_loc_ids:
				branch_pro_id = product_req_loc_obj.browse(cr, uid, rec_loc_id).location_request_id.id
				branch_pro_ids.append(branch_pro_id)
			if branch_pro_ids:
				intersected_ids = set(display_ids).intersection(branch_pro_ids)
				final_display_ids = list(intersected_ids)
			else:
				final_display_ids = []
		else:
			final_display_ids = display_ids
		if final_display_ids:
			res = []
			self.write(cr, uid, [ids], {'check':False}, context=context)
			for display_id in final_display_ids:
				product_req_data = product_req_obj.browse(cr,uid,display_id)
				if product_req_data.customer_type == 'existing':
					phone = product_req_data.phone_many2one.number
				else:
					phone = product_req_data.phone_many2one_new.number
				if product_req_data.state != 'new':
					branch_id = product_req_data.location_request_line[0].branch_id.id
				else:
					branch_id = False
				date_age = self.calculate_date_age(cr,uid,ids,product_req_data.request_date,product_req_data.closed_date)
				if product_req_data.state == 'assigned':
					product_request_state = 'progress'
				else:
					product_request_state = product_req_data.state
				res_vals =  {       
						'ccc_product_id': ids,
						'request_id': product_req_data.product_request_id,
						'customer_name': product_req_data.name,
						'branch_id': branch_id,
						'origin': product_req_data.company_id.name,
						'request_type_psd': 'product_request',
						'date_age': date_age,
						'state': product_request_state,
						'contact_number': phone,
						'sort_date': product_req_data.request_date,
						'created_by': product_req_data.created_by.id,
						'employee_id': product_req_data.employee_id.id,
						'product_request_id': product_req_data.id
					}
				branch_re_id = branch_req_line_obj.create(cr, uid, res_vals, context=context)
				res.append(branch_re_id)
			return res
		else:
			res = self.write(cr, uid, [ids], {'check':True}, context=context)
		return res

	def get_complaint_requests(self,cr,uid,ids,context=None):
		res = False
		from_date = False
		to_date = False
		true_items = []
		domain = []
		partner_domain = []
		partner_comp_ids = []
		final_display_ids = []
		comp_req_obj = self.pool.get('product.complaint.request')
		comp_req_line_obj = self.pool.get('product.complaint.request.line')  
		comp_req_loc_obj = self.pool.get('product.complaint.locations')  
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')	 
		partner_obj = self.pool.get('res.partner')
		req_line_ids = branch_req_line_obj.search(cr, uid, [('ccc_complaint_id','=',ids)], context=context)
		branch_req_line_obj.unlink(cr, uid, req_line_ids, context=context)
		rec = self.browse(cr, uid, ids)
		if rec.partner_name_cust:
			true_items.append('partner_name_cust')
		if rec.customer_id:
			true_items.append('customer_id')
		if rec.req_id:
			true_items.append('req_id')    
		if rec.contact_name_cust:
			true_items.append('contact_name_cust')
		if rec.phone_cust:
			true_items.append('phone_cust')   
		if rec.mobile_cust:
			true_items.append('mobile_cust')    
		if rec.apartment:
			true_items.append('apartment')
		if rec.building:
			true_items.append('building')
		if rec.subarea:
			true_items.append('subarea')
		if rec.landmark:
			true_items.append('landmark') 
		if rec.street:
			true_items.append('street')
		if rec.city_id:
			true_items.append('city_id')    
		if rec.pincode:
			true_items.append('pincode')
		if rec.branch_id:
			true_items.append('branch_id')	
		if rec.cse:
			true_items.append('cse') 
		if rec.state:
			true_items.append('state')	
		if true_items:    
			for true_item in true_items:    
				if true_item == 'partner_name_cust':
					domain.append(('customer', 'ilike', rec.partner_name_cust))
				if true_item == 'customer_id':
					domain.append(('customer_id', 'ilike', rec.customer_id))
				if true_item == 'req_id':
					domain.append(('complaint_request_id', 'ilike', rec.req_id))   
				if true_item == 'cse':
					domain.append(('employee_id', '=', rec.cse.id))    	
				if true_item == 'state':
					if rec.state == 'new':
						state = 'new'
					elif rec.state == 'open':
						state = 'opened'
					elif rec.state == 'progress':
						state = 'resource_assigned'
					elif rec.state == 'closed':
						state = 'closed'
					elif rec.state == 'cancel':
						state = 'cancel'
					domain.append(('state', '=', state))	
				if true_item == 'apartment':
					comp_loc_ids = comp_req_loc_obj.search(cr,uid,[('name','ilike',rec.apartment)])
					lines_list = []
					for x in comp_req_loc_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_apartment = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_apartment))  
					partner_domain.append(('apartment', 'ilike', rec.apartment))  
				if true_item == 'building':
					comp_loc_ids = comp_req_loc_obj.search(cr,uid,[('name','ilike',rec.building)])
					lines_list = []
					for x in comp_req_loc_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_building = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_building))    
					partner_domain.append(('building', 'ilike', rec.building))    
				if true_item == 'subarea':
					comp_loc_ids = comp_req_loc_obj.search(cr,uid,[('name','ilike',rec.subarea)])
					lines_list = []
					for x in comp_req_loc_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_subarea = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_subarea))
					partner_domain.append(('sub_area', 'ilike', rec.subarea))  
				if true_item == 'landmark':
					comp_loc_ids = comp_req_loc_obj.search(cr,uid,[('name','ilike',rec.landmark)])
					lines_list = []
					for x in comp_req_loc_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_landmark = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_landmark))	
					partner_domain.append(('landmark', 'ilike', rec.landmark))  
				if true_item == 'street':
					comp_loc_ids = comp_req_loc_obj.search(cr,uid,[('name','ilike',rec.street)])
					lines_list = []
					for x in comp_req_loc_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_street = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_street))	
					partner_domain.append(('street', 'ilike', rec.street))      
				if true_item == 'pincode':
					comp_loc_ids = comp_req_loc_obj.search(cr,uid,[('name','ilike',rec.pincode)])
					lines_list = []
					for x in comp_req_loc_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_pincode = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_pincode))	
					partner_domain.append(('zip', 'ilike', rec.pincode))  	
				if true_item == 'city_id':
					comp_loc_ids = comp_req_loc_obj.search(cr,uid,[('name','ilike',rec.city_id.name1)])
					lines_list = []
					for x in comp_req_loc_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_city = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_city))
				if true_item == 'contact_name_cust':
					comp_loc_ids = comp_req_line_obj.search(cr,uid,[('contact_person', 'ilike', rec.contact_name_cust)])
					lines_list = []
					for x in comp_req_line_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_contact = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_contact))	
				if true_item == 'phone_cust':
					#comp_loc_ids = comp_req_line_obj.search(cr,uid,[('loc_phone_id.number', 'ilike', rec.phone_cust)])
					comp_loc_ids = comp_req_line_obj.search(cr,uid,[('phone_number', 'ilike', rec.phone_cust)])
					lines_list = []
					for x in comp_req_line_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_phone = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_phone))
				if true_item == 'mobile_cust':
					#comp_loc_ids = comp_req_line_obj.search(cr,uid,[('loc_phone_id.number', 'ilike', rec.mobile_cust)])
					comp_loc_ids = comp_req_line_obj.search(cr,uid,[('phone_number', 'ilike', rec.mobile_cust)])
					lines_list = []
					for x in comp_req_line_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_phone = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_phone))
				if true_item == 'branch_id':
					comp_loc_ids = comp_req_line_obj.search(cr,uid,[('pci_office.name', 'ilike', rec.branch_id.name)])
					lines_list = []
					for x in comp_req_line_obj.browse(cr,uid,comp_loc_ids):
						if not x.complaint_id.id in lines_list:
							lines_list.append(x.complaint_id.id)
					search_comp_branch = comp_req_obj.search(cr,uid,[('id','in',lines_list)])
					domain.append(('id','in',search_comp_branch))
		if rec.due_date_from_cust:
			from_date = datetime.strptime(rec.due_date_from_cust, "%Y-%m-%d")
			#from_date = from_date.strftime('%Y-%m-%d 24:00:00')	
			from_date = from_date.strftime('%Y-%m-%d')	
		if rec.due_date_to_cust:
			to_date = datetime.strptime(rec.due_date_to_cust, "%Y-%m-%d")
			#to_date = to_date.strftime('%Y-%m-%d 24:00:00')	
			to_date = to_date.strftime('%Y-%m-%d')	
		if from_date and not to_date:
			domain.append(('requested_date', '>=', from_date))	
		elif not from_date and to_date:
			domain.append(('requested_date', '<=', to_date))	
		elif from_date and to_date:				
			domain.append(('requested_date', '>=', from_date))
			domain.append(('requested_date', '<=', to_date))

		if partner_domain:
			partner_ids = partner_obj.search(cr, uid, partner_domain, context=context)
			for each in partner_ids:
				partner_comp_ids = comp_req_obj.search(cr, uid, [('partner_id','=',each)], context=context)

		display_ids = comp_req_obj.search(cr, uid, domain, context=context)

		if partner_comp_ids and display_ids:
			final_display_ids = list(set(partner_comp_ids) & set(display_ids))	

		if display_ids and not partner_comp_ids:
			final_display_ids = display_ids
		if final_display_ids:
			res = []
			# res = self.write(cr, uid, ids, {'complaint_req_ids': [(6, 0, display_ids)]},context=context)
			self.write(cr, uid, [ids], {'check':False}, context=context)
			for display_id in final_display_ids:
				branch_id = False
				contact_number = False
				comp_req = comp_req_obj.browse(cr,uid,display_id)
				date_age = self.calculate_date_age(cr,uid,ids,comp_req.requested_date,comp_req.closed_date)
				if comp_req.state != 'new':
					if comp_req.complaint_line_ids:
						branch_id = comp_req.complaint_line_ids[0].pci_office.id
				if comp_req.complaint_line_ids:
					contact_number = comp_req.complaint_line_ids[0].loc_phone_id.number
				if comp_req.state == 'resource_assigned':
					comp_req_state = 'progress'
				elif comp_req.state == 'opened':
					comp_req_state = 'open'
				else:
					comp_req_state = comp_req.state
				res_vals =  {       
						'ccc_complaint_id': ids,
						'request_id': comp_req.complaint_request_id,
						'customer_name': comp_req.customer,
						'branch_id': branch_id,
						'origin': comp_req.company_id.name,
						'request_type_psd': 'complaint_request',
						'date_age': date_age,
						'state': comp_req_state,
						'contact_number': contact_number,
						'sort_date': comp_req.requested_date,
						'created_by': comp_req.created_by.id,
						'employee_id': comp_req.employee_id.id,
						'complaint_request_id': comp_req.id
					}
				branch_re_id = branch_req_line_obj.create(cr, uid, res_vals, context=context)
				res.append(branch_re_id)
			return res
		else:
			res = self.write(cr, uid, [ids], {'check':True}, context=context)
		return res	

	def get_information_requests(self,cr,uid,ids,context=None):
		res = False
		true_items = []
		domain = []
		partner_domain = []
		partner_info_ids = []
		display_ids = []
		final_display_ids = []
		from_date = False
		to_date = False
		complaint_domain = []
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')	
		info_req_obj = self.pool.get('product.information.request')
		partner_obj = self.pool.get('res.partner')
		req_line_ids = branch_req_line_obj.search(cr, uid, [('ccc_information_id','=',ids)], context=context)
		branch_req_line_obj.unlink(cr, uid, req_line_ids, context=context)
		rec = self.browse(cr, uid, ids)
		if rec.partner_name_cust:
			true_items.append('partner_name_cust')
		if rec.customer_id:
			true_items.append('customer_id')
		if rec.req_id:
			true_items.append('req_id')    
		if rec.contact_name_cust:
			true_items.append('contact_name_cust')
		if rec.mobile_cust:
			true_items.append('mobile_cust')
		if rec.phone_cust:
			true_items.append('phone_cust')     
		if rec.apartment:
			true_items.append('apartment')
		if rec.building:
			true_items.append('building')
		if rec.subarea:
			true_items.append('subarea')
		if rec.landmark:
			true_items.append('landmark') 
		if rec.street:
			true_items.append('street')
		if rec.city_id:
			true_items.append('city_id')    
		if rec.pincode:
			true_items.append('pincode')
		if rec.branch_id:
			true_items.append('branch_id')	
		if rec.cse:
			true_items.append('cse') 
		if rec.state:
			true_items.append('state')				 
		if true_items:    
			for true_item in true_items:    
				if true_item == 'partner_name_cust':
					domain.append(('name', 'ilike', rec.partner_name_cust))
				if true_item == 'req_id':
					domain.append(('information_request_id', 'ilike', rec.req_id)) 
				if true_item == 'customer_id':
					domain.append(('customer_id', 'ilike', rec.customer_id)) 					 
				if true_item == 'contact_name_cust':
					domain.append(('contact_name', 'ilike', rec.contact_name_cust))  
				if true_item == 'phone_cust':
					domain.append(('|'))
					domain.append(('phone_many2one.number', 'ilike', rec.phone_cust))
					domain.append(('phone_many2one_new.number', 'ilike', rec.phone_cust)) 
				if true_item == 'mobile_cust':
					domain.append(('|'))
					domain.append(('phone_many2one.number', 'ilike', rec.mobile_cust))
					domain.append(('phone_many2one_new.number', 'ilike', rec.mobile_cust)) 
				if true_item == 'apartment':
					partner_domain.append(('apartment', 'ilike', rec.apartment)) 
					domain.append(('customer_address', 'ilike', rec.apartment))					
				if true_item == 'building':
					partner_domain.append(('building', 'ilike', rec.building)) 
					domain.append(('customer_address', 'ilike', rec.building))      
				if true_item == 'subarea':
					partner_domain.append(('sub_area', 'ilike', rec.subarea))
					domain.append(('customer_address', 'ilike', rec.subarea)) 
				if true_item == 'landmark':
					partner_domain.append(('landmark', 'ilike', rec.landmark))
					domain.append(('customer_address', 'ilike', rec.landmark)) 	
				if true_item == 'street':
					partner_domain.append(('street', 'ilike', rec.street)) 
					domain.append(('customer_address', 'ilike', rec.street))    
				if true_item == 'city_id':
					partner_domain.append(('city_id', '=', rec.city_id.id))
					domain.append(('customer_address', 'ilike', rec.city_id.name1)) 
				if true_item == 'pincode':
					partner_domain.append(('zip', 'ilike', rec.pincode)) 
					domain.append(('customer_address', 'ilike', rec.pincode)) 

				if true_item == 'branch_id':
					domain.append(('branch_id', '=', rec.branch_id.id))  
				if true_item == 'cse':
					domain.append(('employee_id', '=', rec.cse.id)) 
				if true_item == 'state':
					domain.append(('state', '=', rec.state))   	
		if rec.due_date_from_cust:
			from_date = datetime.strptime(rec.due_date_from_cust, "%Y-%m-%d")
			#from_date = from_date.strftime('%Y-%m-%d 24:00:00')	
			from_date = from_date.strftime('%Y-%m-%d')
		if rec.due_date_to_cust:
			to_date = datetime.strptime(rec.due_date_to_cust, "%Y-%m-%d")
			#to_date = to_date.strftime('%Y-%m-%d 24:00:00')	
			to_date = to_date.strftime('%Y-%m-%d')	
		if from_date and not to_date:
			domain.append(('request_date', '>=', from_date))	
		elif not from_date and to_date:
			domain.append(('request_date', '<=', to_date))	
		elif from_date and to_date:				
			domain.append(('request_date', '>=', from_date))
			domain.append(('request_date', '<=', to_date))

		if partner_domain:
			partner_ids = partner_obj.search(cr, uid, partner_domain, context=context)
			for each in partner_ids:
				partner_info_ids = info_req_obj.search(cr, uid, [('partner_id','=',each)], context=context)

		display_ids = info_req_obj.search(cr, uid, domain, context=context)

		if partner_info_ids and display_ids:
			final_display_ids = list(set(partner_info_ids) & set(display_ids))	

		if display_ids and not partner_info_ids:
			final_display_ids = display_ids

		if final_display_ids:	
			res = []
			self.write(cr, uid, ids, {'check':False}, context=context)
			for display_id in final_display_ids:
				info_req_data = info_req_obj.browse(cr,uid,display_id)
				if info_req_data.customer_type == 'existing':
					phone = info_req_data.phone_many2one.number
				else:
					phone = info_req_data.phone_many2one_new.number
				date_age = self.calculate_date_age(cr,uid,ids,info_req_data.request_date,info_req_data.closed_date)
				res_vals =  {       
						'ccc_information_id': ids,
						'request_id': info_req_data.information_request_id,
						'customer_name': info_req_data.name,
						'branch_id': info_req_data.branch_id.id,
						'origin': info_req_data.company_id.name,
						'request_type_psd': 'information_request',
						'date_age': date_age,
						'state': info_req_data.state,
						'contact_number': phone,
						'sort_date': info_req_data.request_date,
						'created_by': info_req_data.created_by.id,
						'employee_id': info_req_data.employee_id.id,
						'information_request_id': info_req_data.id
					}
				branch_re_id = branch_req_line_obj.create(cr, uid, res_vals, context=context)
				res.append(branch_re_id)
			return res
		else:
			res = self.write(cr, uid, [ids], {'check':True}, context=context)
		return res

	def get_all_requests(self,cr,uid,ids,context=None):
		res = []
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')	
		request_lines = []
		all_request_ids = []
		req_line_ids = branch_req_line_obj.search(cr, uid, [('ccc_branch_id','=',ids)], context=context)
		branch_req_line_obj.unlink(cr, uid, req_line_ids, context=context)
		info_ids = self.get_information_requests(cr, uid, ids)
		if type(info_ids) == bool:
			info_ids = []
		complaint_ids = self.get_complaint_requests(cr, uid, ids)
		if type(complaint_ids) == bool:
			complaint_ids = []
		product_ids = self.get_product_requests(cr, uid, ids)
		if type(product_ids) == bool:
			product_ids = []
		if info_ids and complaint_ids and product_ids:
			all_request_ids = info_ids + complaint_ids + product_ids
		if info_ids and not complaint_ids and not product_ids:
			all_request_ids = info_ids
		if info_ids and complaint_ids and not product_ids:
			all_request_ids = info_ids + complaint_ids	
		if info_ids and not complaint_ids and product_ids:
			all_request_ids = info_ids + product_ids
		if not info_ids and complaint_ids and not product_ids:
			all_request_ids = complaint_ids		
		if not info_ids and complaint_ids and product_ids:
			all_request_ids = complaint_ids + product_ids
		if not info_ids and not complaint_ids and product_ids:
			all_request_ids = product_ids
		for each in all_request_ids:
			self.write(cr, uid, ids, {'check':False}, context=context)
			branch_req_data = branch_req_line_obj.browse(cr, uid, each)
			res_vals =  {       
				'ccc_branch_id': ids,
				'request_id': branch_req_data.request_id or False,
				'customer_name': branch_req_data.customer_name,
				'branch_id': branch_req_data.branch_id.id,
				'origin': branch_req_data.origin,
				'request_type_psd': branch_req_data.request_type_psd,
				'date_age': branch_req_data.date_age,
				'state': branch_req_data.state,
				'contact_number': branch_req_data.contact_number,
				'sort_date': branch_req_data.sort_date,
				'created_by': branch_req_data.created_by.id,
				'employee_id': branch_req_data.employee_id.id,
				'information_request_id': branch_req_data.information_request_id and branch_req_data.information_request_id.id,
				'complaint_request_id': branch_req_data.complaint_request_id and branch_req_data.complaint_request_id.id,
				'product_request_id': branch_req_data.product_request_id and branch_req_data.product_request_id.id,
			}
			branch_re_id = branch_req_line_obj.create(cr, uid, res_vals, context=context)
			res.append(branch_re_id)
		return res

	def search_ccc_branch(self,cr,uid,ids,context=None):
		
		branch_new_obj = self.pool.get('ccc.branch.new')
		branch_line_obj = self.pool.get('ccc.branch.request.line')
		for o in self.browse(cr,uid,ids):
			search_id=o.id
			aaa = o
			if o.customer_category_id:
				tag_new_id = o.customer_category_id
			
			
			for line in o.customer_branch:
					self.pool.get('res.partner').write(cr,uid,line.id,{'customer_branch_id':None})


			select_com = 'select id from ccc_branch_request_line where ccc_assign_id ='+str(o.id)+'or ccc_update_id='+str(o.id)+'or ccc_branch_id='+str(o.id)

			del_com = "delete from ccc_branch_request_line where id in ("+select_com+")"
			cr.execute(del_com)
			customer_id=o.customer_id
			if customer_id:
								customer_id =  customer_id.lstrip()
								customer_id = customer_id.rstrip()
							
			request_id=o.req_id
			if request_id:
								request_id = request_id.lstrip()
								request_id = request_id.rstrip()
			partner_name_cust = o.partner_name_cust
			if partner_name_cust:
								partner_name_cust = partner_name_cust.lstrip()
								partner_name_cust = partner_name_cust.rstrip()
							#location_customer=o.location_cust_name
							#location_contact=o.location_contact_name
			contact_name_cust = o.contact_name_cust
			if contact_name_cust:
								contact_name_cust = contact_name_cust.lstrip()
								contact_name_cust = contact_name_cust.rstrip()
			if o.customer_category_id:
				tag=o.customer_category_id.id
			service_area_cust = o.service_area_cust.id
			city_id = o.city_id.id		
			mobile_cust = o.mobile_cust
			if mobile_cust:
								mobile_cust = mobile_cust.lstrip()
								mobile_cust = mobile_cust.rstrip()
			phone_cust = o.phone_cust
			pincode = o.pincode
			if pincode:
								pincode = pincode.rstrip()
								pincode = pincode.lstrip()
			branch_id = o.branch_id.id
			due_date_from_cust = o.due_date_from_cust
			due_date_to_cust = o.due_date_to_cust
			user_id_cust = o.user_id_cust.id
			contract_number = ''
			state = o.state
			if o.contract_number:
								contract_number = o.contract_number.lstrip()
								contract_number = o.contract_number.rstrip()

			rec= o.inquiry_type		
			job_id = ''
			if o.job_id:
								job_id = o.job_id.lstrip()
								job_id  = o.job_id.rstrip()	

			if o.inquiry_type == 'new_cust' :
							try:
								Sql_Str=''
								employee_id = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id.id)])
								employee_id1= self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id_cust.id)])

								#abdulrahim 07 May 2014 Customer Id, Request Id Search

								if aaa.req_id:
									Sql_Str = Sql_Str + " and AM.request_id ilike '" +"%"+ str(request_id) + "%'"
							
								if aaa.customer_id:
									print ":::::::::::::in customer id"
									Sql_Str = Sql_Str + " and AM.partner_id in (select RP.id from res_partner RP where RP.ou_id ilike '" +"%"+ str(customer_id) + "%')"

								if aaa.partner_name_cust:
									Sql_Str = Sql_Str + " and AM.name ilike '" +"%"+ str(partner_name_cust) + "%'"
								if aaa.contact_name_cust:
									Sql_Str = Sql_Str +" and AM.contact_name ilike '" +  "%" + str(contact_name_cust) + "%'"
								#if aaa.customer_category_id.id != False:
									#Sql_Str = Sql_Str + " and AM.tag = '" + str(aaa.customer_category_id.id) + "'"
									#print "customer_category_id",aaa.customer_category_id.id
									#print "Sql str we got is",Sql_Str
								if aaa.state:
									Sql_Str = Sql_Str + " and AM.state ilike '" + str(aaa.state) + "'"
								if aaa.service_area_cust.id :
									Sql_Str = Sql_Str +" and PM.service_area = '"  + str(aaa.service_area_cust.id) + "'"
								if aaa.city_id.id : 
									Sql_Str = Sql_Str +" and AM.city_id = '"  + str(aaa.city_id.id) + "'"


							
								
								if aaa.mobile_cust:

									Sql_Str = Sql_Str+" and PM.new_customer_address_id in (select i.ccc_new_address_id from phone_m2m i where i.name ilike '"+  "%" + str(mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"')) or CN.number like '"+str(mobile_cust)+"'"

								if aaa.phone_cust:
									Sql_Str = Sql_Str+" and PM.new_customer_address_id in (select i.ccc_new_address_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.type in ('"'mobile'"','"'landline'"')) or CN.number like '"+str(mobile_cust)+"'"

								if aaa.pincode:
									Sql_Str = Sql_Str +" and AM.zip = '" + str(aaa.pincode) + "'"
								if aaa.branch_id.id:
									Sql_Str =Sql_Str +" and PM.branch_id = '" + str(aaa.branch_id.id) + "'"
								if aaa.due_date_from_cust :
									Sql_Str =Sql_Str +" and cast(AM.request_date as date) >= '" +  str(aaa.due_date_from_cust) + "'"
								if aaa.due_date_to_cust :
									Sql_Str =Sql_Str +" and cast(AM.request_date as date) <= '" + str(aaa.due_date_to_cust) + "'"
								if aaa.landmark:
									Sql_Str =Sql_Str +" and AM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"

								if aaa.subarea:
									Sql_Str =Sql_Str +" and AM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"

								if aaa.building:
									Sql_Str =Sql_Str +" and AM.building ilike  '" +  "%" + str(aaa.building) + "%'"
								if aaa.location_name:
									Sql_Str =Sql_Str +" and AM.location_name ilike  '" +  "%" + str(aaa.location_name) + "%'"

								if aaa.cse:

							
									Sql_Str =Sql_Str +" and PM.assign_resource = " + str(aaa.cse.id)
							
								if aaa.customer_category_id:
									Sql_Str =Sql_Str +" and AM.tag_new ilike  '" +  "%" + str(aaa.customer_category_id.name) + "%'"	
								if aaa.lead_tracker:
										Sql_Str = Sql_Str +" and AM.lead_tracker =True" 
								#abdulrahim 08 May 2014 
								Main_Str = "select distinct on(AM.id)AM.id,AM.check_exist,AM.message_id_new,AM.name,PM.branch_id,(select name from res_company where id= AM.origin),AM.request_type,AM.user_name,AM.state,AM.request_date,AM.user_id,AM.request_id,case when AM.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when AM.state in ('progress','closed') then "+str(o.id)+" else Null end,case when AM.ccc_update_check=True and AM.message_id_new=False and Am.state != 'new' then "+str(o.id)+" else Null end,ph.name,case when AM.state not in ('cancel','closed') then to_char(AM.request_date,'dd')||'/'||to_char(AM.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(AM.request_date as date)) ) else  to_char(AM.request_date,'dd')||'/'||to_char(AM.request_date, 'Mon')||':' || date_part('day',age(AM.close_date,cast(AM.request_date as date))) end,PM.service_area,PM.assign_resource from contact_name CN right join ccc_branch_new AM on CN.request_id=AM.id left join ccc_new_location PM on AM.id = PM.new_customer_id1  left join phone_m2m ph on PM.new_customer_address_id=ph.ccc_new_address_id where AM.request_type='new_cust'  "
						
								Main_Str1 = Main_Str + Sql_Str


						

								insert_command = "insert into ccc_branch_request_line (request_search,check_exist,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1+")"

								cr.execute(insert_command)

								cr.commit()
			
								search_com = "select cs.id from ccc_branch_request_line cs  join ccc_branch cc on case when cs.state in ('open','cancel','new') then   cs.ccc_branch_id="+str(o.id)+" when cs.state in ('progress','closed') then   cs.ccc_assign_id="+str(o.id)+" else    cs.ccc_update_id="+str(o.id)+" end order by cs.id desc limit 1"

								cr.execute(search_com)
						
								if not cr.fetchall():
									self.write(cr,uid,ids,{'check':True})
								else:
									self.write(cr,uid,ids,{'check':False})
								# if o.lead_tracker:
								for i in o.request_line:
									if not i.contact_number:
										ccc_request=self.pool.get('ccc.branch.new').search(cr,uid,[('id','=',i.request_search)])
										if ccc_request:
											ccc_brw=self.pool.get('ccc.branch.new').browse(cr,uid,ccc_request[0])
											if ccc_brw.phone_many2one:
												cr.execute("update ccc_branch_request_line set contact_number='"+str(ccc_brw.phone_many2one.number)+"' where id ="+str(i.id)+"")
								cr.commit()	 
							except Exception  as exc:
								if exc.__class__.__name__ == 'TransactionRollbackError':
									pass
								else:
									raise						
			if rec == 'renewal_request' :
					try:
						Sql_Str = ''
						employee_id = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id.id)])
						employee_id1= self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id_cust.id)])
						#abdulrahim 08 may Customer id , Request id
						if aaa.req_id:
								Sql_Str = Sql_Str + " and CC.request_id ilike '" +"%"+ str(request_id) + "%'"

						if aaa.customer_id:
								Sql_Str = Sql_Str + " and CC.partner_id in (select RP.id from res_partner RP where RP.ou_id ilike '" +"%"+ str(customer_id) + "%')"

						if aaa.partner_name_cust:
							Sql_Str = Sql_Str + " and AM.name ilike '" +   "%" + str(partner_name_cust) + "%'"
						if aaa.contact_name_cust:
							Sql_Str = Sql_Str +" and AM.contact_name ilike '" +   "%" + str(contact_name_cust) + "%'"
						if aaa.state :
							Sql_Str = Sql_Str + " and CC.state ilike '" + str(aaa.state) + "'"
						if aaa.service_area_cust.id :
							Sql_Str = Sql_Str +" and CC.area_service = '"  + str(aaa.service_area_cust.id) + "'"
						if aaa.city_id:
							Sql_Str = Sql_Str +" and CM.city_id = '" + str(aaa.city_id.id) + "'"

						if aaa.mobile_cust:

							Sql_Str = Sql_Str+" and CM.customer_address in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"

						if aaa.phone_cust:
							Sql_Str = Sql_Str+" and CM.customer_address in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"


						if aaa.pincode:
							Sql_Str = Sql_Str +" and CM.zip ilike '" +   "%" + str(aaa.pincode) + "%'"
						if aaa.branch_id:
							Sql_Str =Sql_Str +" and AM.branch_id = '" + str(aaa.branch_id.id) + "'"
						if aaa.due_date_from_cust :
							Sql_Str =Sql_Str +" and cast(CC.request_date as date) >= '" + str(aaa.due_date_from_cust) + "'"
						if aaa.due_date_to_cust :
							Sql_Str =Sql_Str +" and cast(CC.request_date as date) <= '" + str(aaa.due_date_to_cust) + "'"
						if aaa.cse:

						
								Sql_Str =Sql_Str +" and CM.cse = " + str(aaa.cse.id)

						if aaa.landmark:
								Sql_Str =Sql_Str +" and AM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"

						if aaa.subarea:
								Sql_Str =Sql_Str +" and AM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"

						if aaa.location_name:
								Sql_Str =Sql_Str +" and AM.location_name ilike  '" +  "%" + str(aaa.location_name) + "%'"
						if aaa.building:
								Sql_Str =Sql_Str +" and AM.building ilike  '" +  "%" + str(aaa.building) + "%'"
						if aaa.customer_category_id:
								Sql_Str =Sql_Str +" and AM.tag_new ilike  '" +  "%" + str(aaa.customer_category_id.name) + "%'"


						Main_Str = "select distinct on(CC.id)CC.id,CC.message_id_new,AM.name,CC.branch_id,(Select name from res_company where id=CC.origin),CC.request_type,CC.user_name,CC.state,CC.request_date,CC.user_id,CC.request_id,case when CC.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when CC.state in ('progress','closed') then "+str(o.id)+" else Null end,case when CC.ccc_update_check=True and CC.message_id_new=False and CC.state != 'new' then "+str(o.id)+" else Null end,ph.name,case when CC.state not in ('cancel','closed') then to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(CC.request_date as date)) ) else  to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(CC.close_date,cast(CC.request_date as date))) end,CC.area_service,CC.assign_resource from ccc_branch_new CC left join res_partner AM on AM.id=CC.partner_id left join customer_line CM on AM.id=CM.partner_id  left join phone_m2m ph on ph.res_location_id=CM.customer_address where CC.request_type='renewal_request' "


						Main_Str1 = Main_Str + Sql_Str
	 	
						insert_command = "insert into ccc_branch_request_line (request_search,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1+")"

						cr.execute(insert_command)
					

						search_com = "select cs.id from ccc_branch_request_line cs  join ccc_branch cc on case when cs.state in ('open','cancel','new') then   cs.ccc_branch_id="+str(o.id)+" when cs.state in ('progress','closed') then   cs.ccc_assign_id="+str(o.id)+" else    cs.ccc_update_id="+str(o.id)+" end order by cs.id desc limit 1"

						cr.execute(search_com)
					
						if not cr.fetchall():
							self.write(cr,uid,ids,{'check':True})
						else:
							self.write(cr,uid,ids,{'check':False})
						# if o.lead_tracker:
						for i in o.request_line:
							if not i.contact_number:
								ccc_request=self.pool.get('ccc.branch.new').search(cr,uid,[('id','=',i.request_search)])
								if ccc_request:
									ccc_brw=self.pool.get('ccc.branch.new').browse(cr,uid,ccc_request[0])
									if ccc_brw.phone_many2one:
										cr.execute("update ccc_branch_request_line set contact_number='"+str(ccc_brw.phone_many2one.number)+"' where id ="+str(i.id)+"")
										# self.pool.get('global.search.line').write(cr,uid,i.id,{'phone_mobile':ccc_brw.phone_many2one.number})
						cr.commit()	 	 
					except Exception  as exc:
						if exc.__class__.__name__ == 'TransactionRollbackError':
							pass
						else:
							raise		
					

			if rec == 'information_request' :
					try:
						Sql_Str = ''
						Sql_Str2=''
						employee_id = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id.id)])
						employee_id1= self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id_cust.id)])
						#abdulrahim 08 may Customer id , Request id
						if aaa.req_id:
							Sql_Str = Sql_Str + " and CC.request_id ilike '" +"%"+ str(request_id) + "%'"
							Sql_Str2 = Sql_Str2 + " and CC.request_id ilike '" +"%"+ str(request_id) + "%'"
						if aaa.customer_id:
							Sql_Str = Sql_Str + " and CC.partner_id in (select RP.id from res_partner RP where RP.ou_id ilike '" +"%"+ str(customer_id) + "%')"
							#Sql_Str2 = Sql_Str2 + " and AM.partner_id in (select RP.id from res_partner RP where RP.ou_id ilike '" +"%"+ str(customer_id) + "%')"

						if aaa.partner_name_cust:
							Sql_Str = Sql_Str + " and CC.name ilike '" +   "%" + str(partner_name_cust) + "%'"
							Sql_Str2 = Sql_Str2 + " and CC.name ilike '" +  "%" +str(partner_name_cust) + "%'"	
						if aaa.contact_name_cust:
							Sql_Str = Sql_Str +" and CC.contact_name ilike '" +   "%" + str(contact_name_cust) + "%'"
							Sql_Str2 = Sql_Str2 +" and CC.contact_name ilike '" +   "%" + str(contact_name_cust) + "%'"
						if aaa.state :
							Sql_Str = Sql_Str + " and CC.state ilike '" + str(aaa.state) + "'"
							Sql_Str2 = Sql_Str2 + " and CC.state ilike '" + str(aaa.state) + "'"
						if aaa.city_id.id :
							Sql_Str = Sql_Str +" and CC.city_id = '" + str(aaa.city_id.id) + "'"
							#Sql_Str2 = Sql_Str2 +" and AM.customer_address = '" + str(aaa.city_id.id) + "'	
						if aaa.mobile_cust:
							Sql_Str = Sql_Str+" and CM.customer_address in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"
							Sql_Str2 = Sql_Str2+" and CC.id in (select i.partner_id_new_cust from phone_number_child_new i where i.number ilike '"+  "%" + str(aaa.mobile_cust) + "%' and i.contact_select in ('"'mobile'"','"'landline'"'))"
						if aaa.phone_cust:
							Sql_Str = Sql_Str+" and CC.customer_address in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.type ilike '"'landline'"')"
							Sql_Str2 = Sql_Str2+" and CC.id in (select i.partner_id_new_cust from phone_number_child_new i where i.number ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.contact_select in ('"'mobile'"','"'landline'"'))"

						if aaa.pincode :
							Sql_Str = Sql_Str +" and CC.zip ilike '" +   "%" + str(aaa.pincode) + "%'"
							Sql_Str2 = Sql_Str2 +" and CC.generic_address  ilike '" +   "%" + str(aaa.pincode) + "%'"
						if aaa.branch_id:
							Sql_Str =Sql_Str +" and CC.branch_id = '" + str(aaa.branch_id.id) + "'"
							Sql_Str2 =Sql_Str2 +" and CC.branch_id = '" + str(aaa.branch_id.id) + "'"
						if aaa.due_date_from_cust :
							Sql_Str =Sql_Str +" and cast(CC.request_date as date) >= '" + str(aaa.due_date_from_cust) + "'"
							Sql_Str2 =Sql_Str2 +" and cast(CC.request_date as date) >= '" + str(aaa.due_date_from_cust) + "'"
						if aaa.due_date_to_cust:
							Sql_Str =Sql_Str +" and cast(CC.request_date as date) <= '" + str(aaa.due_date_to_cust) + "'"
							Sql_Str2 =Sql_Str2 +" and cast(CC.request_date as date) <= '" + customer_branch_idstr(aaa.due_date_to_cust) + "'"
						if aaa.cse:

						
								Sql_Str =Sql_Str +" and CC.assign_resource = " + str(aaa.cse.id)
								Sql_Str2 =Sql_Str2 +" and CC.assign_resource = " + str(aaa.cse.id)

						if aaa.landmark:
							Sql_Str =Sql_Str +" and CM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"
							Sql_Str2 =Sql_Str2 +" and CC.generic_address ilike '"  +  "%" + str(aaa.landmark) + "%'"
						if aaa.subarea:
							Sql_Str =Sql_Str +" and CM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"
							Sql_Str2 =Sql_Str2 +" and CC.generic_address ilike '" +  "%" + str(aaa.subarea) + "%'"
						if aaa.building:
							Sql_Str =Sql_Str +" and CM.building ilike  '" +  "%" + str(aaa.building) + "%'"
							Sql_Str2 =Sql_Str2 +" and CC.generic_address ilike  '" +  "%" + str(aaa.building) + "%'"

						if aaa.location_name:
							Sql_Str =Sql_Str +" and AM.location_name ilike  '" +  "%" + str(aaa.location_name) + "%'"
						if aaa.customer_category_id:
							Sql_Str =Sql_Str +" and AM.tag_new ilike  '" +  "%" + str(aaa.customer_category_id.name) + "%'"
							Sql_Str2 =Sql_Str2 +" and CC.generic_address ilike  '" +  "%" + str(aaa.customer_category_id.name) + "%'"



						Main_Str = "select distinct on(CC.id)CC.id,CC.message_id_new,AM.name,CC.branch_id,(select name from res_company where id=CC.origin),CC.request_type,CC.user_name,CC.state,CC.request_date,CC.user_id,CC.request_id,case when CC.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when CC.state in ('progress','closed') then "+str(o.id)+" else Null end,case when CC.ccc_update_check=True and CC.message_id_new=False and CC.state != 'new' then "+str(o.id)+" else Null end,ph.name,case when CC.state not in ('cancel','closed') then to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(CC.request_date as date)) ) else  to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(CC.close_date,cast(CC.request_date as date))) end,CC.area_service,CC.assign_resource from ccc_branch_new CC left join res_partner AM on AM.id=CC.partner_id left join customer_line CM on AM.id=CM.partner_id  left join phone_m2m ph on ph.res_location_id=CM.customer_address where CC.request_type='information_request' "


						Main_Str1 = Main_Str + Sql_Str
	 	
						insert_command = "insert into ccc_branch_request_line (request_search,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1+")"

						cr.execute(insert_command)					

						Main_Str_generic1 = "select distinct on(CC.id)CC.id,CC.message_id_new,CC.name,CC.branch_id,(select name from res_company where id=CC.origin),CC.request_type,CC.user_name,CC.state,CC.request_date,CC.user_id,CC.request_id,case when CC.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when CC.state in ('progress','closed') then "+str(o.id)+" else Null end,case when CC.ccc_update_check=True and CC.message_id_new=False and CC.state != 'new' then "+str(o.id)+" else Null end,ph.number,case when CC.state not in ('cancel','closed') then to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(CC.request_date as date)) ) else  to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(CC.close_date,cast(CC.request_date as date))) end,CC.area_service,CC.assign_resource from ccc_branch_new CC left join phone_number_child_new ph on ph.partner_id_new_cust=CC.id where  CC.request_type='generic_request'  "
					
						Main_Str1generic = Main_Str_generic1 + Sql_Str2
					
						insert_command_generic = "insert into ccc_branch_request_line (request_search,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1generic+")"
						cr.execute(insert_command_generic)	
						cr.commit()					


						search_com = "select cs.id from ccc_branch_request_line cs  join ccc_branch cc on case when cs.state in ('open','cancel','new') then   cs.ccc_branch_id="+str(o.id)+" when cs.state in ('progress','closed') then   cs.ccc_assign_id="+str(o.id)+" else    cs.ccc_update_id="+str(o.id)+" end order by cs.id desc limit 1"

						cr.execute(search_com)
					
						if not cr.fetchall():
							self.write(cr,uid,ids,{'check':True})
						else:
							self.write(cr,uid,ids,{'check':False})
						cr.commit()	 
					except Exception  as exc:
						if exc.__class__.__name__ == 'TransactionRollbackError':
							pass
						else:
							raise


			if rec == 'lead_request' :
					try:
						employee_id = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id.id)])
						employee_id1= self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id_cust.id)])
						Sql_Str =''
						#abdulrahim 08 may Customer id , Request id
						if aaa.req_id:
								Sql_Str = Sql_Str + " and CC.request_id ilike '" +"%"+ str(request_id) + "%'"
						if aaa.customer_id:
								print ":::::::::::::in customer id"
								Sql_Str = Sql_Str + " and CC.partner_id in (select RP.id from res_partner RP where RP.ou_id ilike '" +"%"+ str(customer_id) + "%')"

						if aaa.partner_name_cust:
							Sql_Str = Sql_Str + " and AM.name ilike '" + "%" + str(aaa.partner_name_cust) + "%'"
						if aaa.contact_name_cust:
							Sql_Str = Sql_Str +" and AM.contact_name ilike '" +  "%" + str(aaa.contact_name_cust) + "%'"
						#if aaa.customer_category_id.id != False:
						#	Sql_Str = Sql_Str + " and AM.customer_category_id = '" + str(aaa.customer_category_id.id) + "'"
						if aaa.state:
							Sql_Str = Sql_Str + " and CC.state ilike '" + str(aaa.state) + "'"
						if aaa.service_area_cust.id :
							Sql_Str = Sql_Str +" and CM.service_area = '" +   str(aaa.service_area_cust.id) + "'"
						if aaa.city_id :
							Sql_Str = Sql_Str +" and AM.city_id = '" + str(aaa.city_id.id) + "'"
						if aaa.mobile_cust:

							Sql_Str = Sql_Str+" and CL.address_id in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"

						if aaa.phone_cust:
							Sql_Str = Sql_Str+" and CL.address_id in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"
						
						if aaa.pincode :
							Sql_Str = Sql_Str +" and AM.zip ilike '" +  "%" + str(aaa.pincode) + "%'"
						if aaa.branch_id:
							Sql_Str =Sql_Str +" and CC.branch_id = '" + str(aaa.branch_id.id) + "'"
						if aaa.due_date_from_cust :
							Sql_Str =Sql_Str +" and cast(CC.request_date as date)  >= '" + str(aaa.due_date_from_cust) + "'"
						if aaa.due_date_to_cust :
							Sql_Str =Sql_Str +" and cast(CC.request_date as date) <= '" + str(aaa.due_date_to_cust) + "'"
						if aaa.cse:

						
								Sql_Str =Sql_Str +" and CL.assign_resource = " + str(aaa.cse.id)
						
						if aaa.landmark:
								Sql_Str =Sql_Str +" and AM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"

						if aaa.subarea:
								Sql_Str =Sql_Str +" and AM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"

						if aaa.building:
								Sql_Str =Sql_Str +" and AM.building ilike  '" +  "%" + str(aaa.building) + "%'"
						if aaa.location_name:
								Sql_Str =Sql_Str +" and AM.location_name ilike  '" +  "%" + str(aaa.location_name) + "%'"
						if aaa.customer_category_id:
							Sql_Str =Sql_Str +" and AM.tag_new ilike  '" +  "%" + str(aaa.customer_category_id.name) + "%'"

					
						Main_Str = "select distinct on(CC.id)CC.id,CC.message_id_new,CC.name,CL.branch_id,(Select name from res_company where id=CC.origin),CC.request_type,CC.user_name,CC.state,CC.request_date,CC.user_id,CC.request_id,case when CC.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when CC.state in ('progress','closed') then "+str(o.id)+" else Null end,case when CC.ccc_update_check=True and CC.message_id_new=False and CC.state != 'new' then "+str(o.id)+" else Null end,ph.name,case when CC.state not in ('cancel','closed') then to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(CC.request_date as date)) ) else  to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(CC.close_date,cast(CC.request_date as date))) end,CL.service_area,CL.assign_resource from ccc_branch_new CC left join res_partner AM on AM.id=CC.partner_id left join customer_line CM on AM.id=CM.partner_id left join customer_branch_lead_line CL on CL.lead_id= CC.id left join phone_m2m ph on ph.res_location_id=CM.customer_address where CC.request_type='lead_request' "

						Main_Str1 = Main_Str + Sql_Str

						insert_command = "insert into ccc_branch_request_line (request_search,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1+")"

						cr.execute(insert_command)

						cr.commit()

						search_com = "select cs.id from ccc_branch_request_line cs  join ccc_branch cc on case when cs.state in ('open','cancel','new') then   cs.ccc_branch_id="+str(o.id)+" when cs.state in ('progress','closed') then   cs.ccc_assign_id="+str(o.id)+" else    cs.ccc_update_id="+str(o.id)+" end order by cs.id desc limit 1"

						cr.execute(search_com)
					
						if not cr.fetchall():
							self.write(cr,uid,ids,{'check':True})
						else:
							self.write(cr,uid,ids,{'check':False})
						# if o.lead_tracker:
						for i in o.request_line:
							if not i.contact_number:
								ccc_request=self.pool.get('ccc.branch.new').search(cr,uid,[('id','=',i.request_search)])
								if ccc_request:
									ccc_brw=self.pool.get('ccc.branch.new').browse(cr,uid,ccc_request[0])
									if ccc_brw.phone_many2one:
										cr.execute("update ccc_branch_request_line set contact_number='"+str(ccc_brw.phone_many2one.number)+"' where id ="+str(i.id)+"")
										# self.pool.get('global.search.line').write(cr,uid,i.id,{'phone_mobile':ccc_brw.phone_many2one.number})
						cr.commit()	 
					except Exception  as exc:
						if exc.__class__.__name__ == 'TransactionRollbackError':
							pass
						else:
							raise					
			if rec == 'complaint_request':
					try:
						Sql_Str =''
						employee_id = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id.id)])
						employee_id1= self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id_cust.id)])
						#abdulrahim 08 may Customer id , Request id
						if aaa.req_id:
								Sql_Str = Sql_Str + " and CC.request_id ilike '" +"%"+ str(request_id) + "%'"
						if aaa.customer_id:
								print ":::::::::::::in customer id"
								Sql_Str = Sql_Str + " and CC.partner_id in (select RP.id from res_partner RP where RP.ou_id ilike '" +"%"+ str(customer_id) + "%')"

						if aaa.partner_name_cust:
							Sql_Str = Sql_Str + " and AM.name ilike '" + "%" + str(partner_name_cust) + "%'"
						if aaa.contact_name_cust :
							Sql_Str = Sql_Str +" and AM.contact_name ilike '" +  "%" + str(contact_name_cust) + "%'"
					
						if aaa.state :
							Sql_Str = Sql_Str + " and CC.state ilike '" + str(aaa.state) + "'"
						if aaa.service_area_cust:
							Sql_Str = Sql_Str +" and CC.area_service = '" +   str(aaa.service_area_cust.id) + "'"
						if aaa.city_id:
							Sql_Str = Sql_Str +" and AM.city_id = '" + str(aaa.city_id.id) + "'"


						if aaa.mobile_cust:
						

							Sql_Str = Sql_Str+" and CC.location in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"

						
						if aaa.phone_cust:
							Sql_Str = Sql_Str+" and CC.location in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"


					
						if aaa.pincode :
							Sql_Str = Sql_Str +" and AM.zip ilike '" +  "%" + str(aaa.pincode) + "%'"
						if aaa.branch_id:
							Sql_Str =Sql_Str +" and CC.branch_id = '" + str(aaa.branch_id.id) + "'"
						if aaa.due_date_from_cust :
							Sql_Str =Sql_Str +" and cast(CC.request_date as date)  >= '" + str(aaa.due_date_from_cust) + "'"
						if aaa.due_date_to_cust :
							Sql_Str =Sql_Str +" and cast(CC.request_date as date) <= '" + str(aaa.due_date_to_cust) + "'"
						if aaa.cse:

						
								Sql_Str =Sql_Str +" and CC.assign_resource = " + str(aaa.cse.id)


						if aaa.landmark:
								Sql_Str =Sql_Str +" and AM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"

						if aaa.subarea:
								Sql_Str =Sql_Str +" and AM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"

						if aaa.location_name:
								Sql_Str =Sql_Str +" and AM.location_name ilike  '" +  "%" + str(aaa.location_name) + "%'"
						if aaa.building:
								Sql_Str =Sql_Str +" and AM.building ilike  '" +  "%" + str(aaa.building) + "%'"
						if aaa.customer_category_id:
								Sql_Str =Sql_Str +" and AM.tag_new ilike  '" +  "%" + str(aaa.customer_category_id.name) + "%'"			
						Main_Str = "select distinct on(CC.id)CC.id,CC.message_id_new,CC.name,CC.branch_id,(select name from res_company where id=CC.origin),CC.request_type,CC.user_name,CC.state,CC.request_date,CC.user_id,CC.request_id,case when CC.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when CC.state in ('progress','closed') then "+str(o.id)+" else Null end,case when CC.ccc_update_check=True and CC.message_id_new=False and CC.state != 'new' then "+str(o.id)+" else Null end,ph.name,case when CC.state not in ('cancel','closed') then to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(CC.request_date as date)) ) else  to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(CC.close_date,cast(CC.request_date as date))) end,CC.area_service,CC.assign_resource from ccc_branch_new CC left join  res_partner AM on AM.id=CC.partner_id left join customer_line CM on AM.id=CM.partner_id left join phone_m2m ph on ph.res_location_id=CM.customer_address where CC.request_type='complaint_request'  "

						Main_Str1 = Main_Str + Sql_Str
	 	
						insert_command = "insert into ccc_branch_request_line (request_search,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1+")"

						cr.execute(insert_command)

						cr.commit()


						search_com = "select cs.id from ccc_branch_request_line cs  join ccc_branch cc on case when cs.state in ('open','cancel','new') then   cs.ccc_branch_id="+str(o.id)+" when cs.state in ('progress','closed') then   cs.ccc_assign_id="+str(o.id)+" else    cs.ccc_update_id="+str(o.id)+" end order by cs.id desc limit 1"

						cr.execute(search_com)
					
						if not cr.fetchall():
							self.write(cr,uid,ids,{'check':True})
						else:
							self.write(cr,uid,ids,{'check':False})
						cr.commit()
					except Exception  as exc:
						if exc.__class__.__name__ == 'TransactionRollbackError':
							pass
						else:
							raise					 
			if rec == 'all_request':
					try:
						Sql_Str='' # For New Customer
						Sql_Str4='' # For generic request
						Sql_Str2=''# For Existing Customer
						Sql_Str3 = '' #for Lead
						name=''
						count=0
						output = set()
						query_generic=[]
						employee_id = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id.id)])
						employee_id1= self.pool.get('hr.employee').search(cr,uid,[('user_id','=',aaa.user_id_cust.id)])

					
						if aaa.customer_id:
						
						
							print "::::::::::::::::::::; in customer id"
					
							Sql_Str3 = Sql_Str3 + " and AM.ou_id ilike '" +  "%" +str(customer_id) + "%'"
							Sql_Str2 = Sql_Str2 + " and AM.ou_id ilike '" +  "%" +str(customer_id) + "%'"
							Sql_Str =Sql_Str +" and AM.partner_id in (select RP.id from res_partner RP where RP.ou_id ilike '" +  "%" +str(aaa.customer_id) + "%')"
						

						if aaa.req_id :
							Sql_Str = Sql_Str + " and AM.request_id ilike '" +  "%" +str(request_id) + "%'"
							Sql_Str2 = Sql_Str2 + " and CC.request_id ilike '" +   "%" + str(request_id) + "%'"
							Sql_Str4 =Sql_Str4 +" and CC.request_id ilike '" + "%" +str(request_id) + "%'"
							Sql_Str3 =Sql_Str3 +" and CC.request_id ilike '" + "%" +str(request_id) + "%'"
						if aaa.partner_name_cust :
							Sql_Str = Sql_Str + " and AM.name ilike '" +  "%" +str(partner_name_cust) + "%'"
							Sql_Str2 = Sql_Str2 + " and AM.name ilike '" +   "%" + str(partner_name_cust) + "%'"
							Sql_Str4 =Sql_Str4 +" and CC.name ilike '" + "%" +str(partner_name_cust) + "%'"
							Sql_Str3 =Sql_Str3 +" and CC.name ilike '" + "%" +str(partner_name_cust) + "%'"

						if aaa.contact_name_cust :
							Sql_Str = Sql_Str +" and AM.contact_name ilike '" +   "%" + str(contact_name_cust) + "%'"
							Sql_Str2 = Sql_Str2 +" and AM.contact_name ilike '" +   "%" + str(contact_name_cust) + "%'"
							Sql_Str4 = Sql_Str4 +" and CC.contact_name ilike '" +   "%" + str(contact_name_cust) + "%'"
							Sql_Str3 = Sql_Str3 +" and AM.contact_name ilike '" +   "%" + str(contact_name_cust) + "%'"

						if aaa.state :
							Sql_Str = Sql_Str + " and AM.state ilike '" + str(aaa.state) + "'"
							Sql_Str2 = Sql_Str2 + " and CC.state ilike '" + str(aaa.state) + "'"
							Sql_Str4 = Sql_Str4 + " and CC.state ilike '" + str(aaa.state) + "'"
							Sql_Str3 = Sql_Str3 + " and CC.state ilike '" + str(aaa.state) + "'"
						
						if aaa.service_area_cust:
							Sql_Str = Sql_Str +" and PM.service_area = '" +    str(aaa.service_area_cust.id) + "'"
							Sql_Str2 = Sql_Str2 +" and CM.service_area = '" + str(aaa.service_area_cust.id) + "'"
							
							Sql_Str3 = Sql_Str3 +" and CL.service_area = '" + str(aaa.service_area_cust.id) + "'" 
							count=count+1
						

						if aaa.city_id:
							Sql_Str = Sql_Str +" and AM.city_id  = '" + str(aaa.city_id.id) + "'"
							Sql_Str2 = Sql_Str2 +" and AM.city_id = '" + str(aaa.city_id.id) + "'"
							Sql_Str3 = Sql_Str3 +" and AM.city_id = '" + str(aaa.city_id.id) + "'"
							#Sql_Str4 =Sql_Str4 
							count=count+1
						
						if aaa.mobile_cust:

							Sql_Str = Sql_Str+" and PM.new_customer_address_id in (select i.ccc_new_address_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"')) or CN.number='"+str(aaa.mobile_cust)+"'"
							Sql_Str4 = Sql_Str4 +" and CC.id in (select i.partner_id_new_cust from phone_number_child_new i where i.number ilike '"+  "%" + str(aaa.mobile_cust) + "%' and i.contact_select in ('"'mobile'"','"'landline'"'))"


							Sql_Str2 = Sql_Str2+" and CC.location in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"

							Sql_Str3 = Sql_Str3+" and CL.address_id in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"


						
						if aaa.phone_cust:

							Sql_Str = Sql_Str+" and PM.new_customer_address_id in (select i.ccc_new_address_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.type in ('"'mobile'"','"'landline'"')) or CN.number='"+str(aaa.phone_cust)+"'"

							Sql_Str4 = Sql_Str4 +" and CC.id in (select i.partner_id_new_cust from phone_number_child_new i where i.number ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.contact_select in ('"'mobile'"','"'landline'"'))"
							Sql_Str2 = Sql_Str2+" and CC.location in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"
							Sql_Str3 = Sql_Str3+" and CL.address_id in (select i.res_location_id from phone_m2m i where i.name ilike '"+  "%" + str(aaa.phone_cust) + "%' and i.type in ('"'mobile'"','"'landline'"'))"
						
						if aaa.pincode:
							Sql_Str = Sql_Str +" and AM.zip ilike'" +   "%" + str(aaa.pincode) + "%'"
							Sql_Str2 = Sql_Str2 +" and AM.zip ilike '" +   "%" + str(aaa.pincode) + "%'"
						#	
							Sql_Str3 = Sql_Str3 +" and CC.zip ilike '" +   "%" + str(aaa.pincode) + "%'"
							count=count+1
						


					
					
						if aaa.branch_id:
							Sql_Str =Sql_Str +" and PM.branch_id = '" + str(aaa.branch_id.id) + "'"


							Sql_Str4 =Sql_Str4 +" and CC.branch_id = '" + str(aaa.branch_id.id) + "'"
							Sql_Str2 =Sql_Str2 +" and CC.branch_id = '" + str(aaa.branch_id.id) + "'"
							Sql_Str3 =Sql_Str3 +" and CC.branch_id = '" + str(aaa.branch_id.id) + "'"
						if aaa.due_date_from_cust :
							Sql_Str =Sql_Str +" and cast(AM.request_date as date) >= '" + str(aaa.due_date_from_cust) + "'"
							Sql_Str4 =Sql_Str4 +" and cast(CC.request_date as date) >= '" + str(aaa.due_date_from_cust) + "'"
							Sql_Str2 =Sql_Str2 +" and cast(CC.request_date as date) >= '" + str(aaa.due_date_from_cust) + "'"
							Sql_Str3 =Sql_Str3 +" and cast(CC.request_date as date) >= '" + str(aaa.due_date_from_cust) + "'"
						if aaa.due_date_to_cust :
							Sql_Str =Sql_Str +" and cast(AM.request_date as date) <= '" + str(aaa.due_date_to_cust) + "'"
							Sql_Str4 =Sql_Str4 +" and cast(CC.request_date as date)<= '" + str(aaa.due_date_to_cust) + "'"
							Sql_Str2 =Sql_Str2 +" and cast(CC.request_date as date) <= '" + str(aaa.due_date_to_cust) + "'"
							Sql_Str3 =Sql_Str3 +" and cast(CC.request_date as date) <= '" + str(aaa.due_date_to_cust) + "'"
					
						if aaa.landmark:
								Sql_Str =Sql_Str +" and AM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"
								Sql_Str2 =Sql_Str2 +" and AM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"
								Sql_Str3 =Sql_Str3 +" and AM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"

						if aaa.subarea:
								Sql_Str =Sql_Str +" and AM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"
								Sql_Str2 =Sql_Str2 +" and AM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"
								Sql_Str3 =Sql_Str3 +" and AM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"

							
						if aaa.building:
								Sql_Str =Sql_Str +" and AM.building ilike  '" +  "%" + str(aaa.building) + "%'"
								Sql_Str2 =Sql_Str2 +" and AM.building ilike  '" +  "%" + str(aaa.building) + "%'"
								Sql_Str3 =Sql_Str3 +" and AM.building ilike  '" +  "%" + str(aaa.building) + "%'"
						if aaa.customer_category_id:
								Sql_Str = Sql_Str + " and AM.tag_new ilike '" +  "%" +str(aaa.customer_category_id.name) + "%'" 
								Sql_Str2 = Sql_Str2 + " and AM.tag_new ilike '" + "%" + str(aaa.customer_category_id.name) + "%'"
								Sql_Str3 =Sql_Str3 +" and AM.tag_new ilike '" + "%" +str(aaa.customer_category_id.name) + "%'"


						if  aaa.cse:
							Sql_Str =Sql_Str +" and PM.assign_resource = " + str(aaa.cse.id)
							Sql_Str2 =Sql_Str2 +" and CC.assign_resource = " + str(aaa.cse.id)
							Sql_Str3 =Sql_Str3 +" and CL.assign_resource = " + str(aaa.cse.id)
							Sql_Str4 =Sql_Str4 +" and CC.assign_resource = " + str(aaa.cse.id)
						if aaa.lead_tracker:
								Sql_Str = Sql_Str +" and AM.lead_tracker =True" 
								Sql_Str4 = Sql_Str4 +" and CC.lead_tracker =True"
								Sql_Str2 = Sql_Str2 +" and CC.lead_tracker =True" 
								Sql_Str3 = Sql_Str3 +" and CC.lead_tracker =True" 

						Main_Str = "select distinct on(AM.id)AM.id,AM.check_exist,AM.message_id_new,AM.name,PM.branch_id,(select name from res_company where id= AM.origin),AM.request_type,AM.user_name,AM.state,AM.request_date,AM.user_id,AM.request_id,case when AM.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when AM.state in ('progress','closed') then "+str(o.id)+" else Null end,case when AM.ccc_update_check=True and AM.message_id_new=False and AM.state != 'new' then "+str(o.id)+" else Null end,ph.name,case when AM.state not in ('cancel','closed') then to_char(AM.request_date,'dd')||'/'||to_char(AM.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(AM.request_date as date)) ) else  to_char(AM.request_date,'dd')||'/'||to_char(AM.request_date, 'Mon')||':' || date_part('day',age(AM.close_date,cast(AM.request_date as date))) end,PM.service_area,PM.assign_resource from contact_name CN right join ccc_branch_new AM on AM.id=CN.request_id left join ccc_new_location PM on AM.id = PM.new_customer_id1  left join phone_m2m ph on PM.new_customer_address_id=ph.ccc_new_address_id where AM.request_type='new_cust'  "
					
						Main_Str1 = Main_Str + Sql_Str


					

						insert_command = "insert into ccc_branch_request_line (request_search,check_exist,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1+")"


						cr.execute(insert_command)

						cr.commit()
					
						Main_Str = "select distinct on(CC.id)CC.id,CC.check_exist,CC.message_id_new,AM.name,CC.branch_id,(select name from res_company where id=CC.origin),CC.request_type,CC.user_name,CC.state,CC.request_date,CC.user_id,CC.request_id,case when CC.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when CC.state in ('progress','closed') then "+str(o.id)+" else Null end,case when CC.ccc_update_check=True and CC.message_id_new=False and CC.state != 'new' then "+str(o.id)+" else Null end,ph.name,case when CC.state not in ('cancel','closed') then to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(CC.request_date as date)) ) else  to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(CC.close_date,cast(CC.request_date as date))) end,CC.area_service,CC.assign_resource from ccc_branch_new CC left join res_partner AM on AM.id=CC.partner_id left join customer_line CM on AM.id=CM.partner_id  left join phone_m2m ph on ph.res_location_id=CM.customer_address where CC.request_type in ('information_request','renewal_request','complaint_request') "


						Main_Str2 = Main_Str + Sql_Str2
	 	
						insert_command =  "insert into ccc_branch_request_line (request_search,check_exist,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str2+")"

						cr.execute(insert_command)					

						Main_Str_generic1 = "select distinct on(CC.id)CC.id,CC.check_exist,CC.message_id_new,CC.name,CC.branch_id,(select name from res_company where id=CC.origin),CC.request_type,CC.user_name,CC.state,CC.request_date,CC.user_id,CC.request_id,case when CC.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when CC.state in ('progress','closed') then "+str(o.id)+" else Null end,case when CC.ccc_update_check=True and CC.message_id_new=False and CC.state != 'new' then "+str(o.id)+" else Null end,ph.number,case when CC.state not in ('cancel','closed') then to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(CC.request_date as date)) ) else  to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(CC.close_date,cast(CC.request_date as date))) end,CC.area_service,CC.assign_resource from ccc_branch_new CC left join phone_number_child_new ph on ph.partner_id_new_cust=CC.id where  CC.request_type='generic_request'  "
					
						Main_Str1generic = Main_Str_generic1 + Sql_Str4
					
						insert_command_generic = "insert into ccc_branch_request_line (request_search,check_exist,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1generic+")"
						cr.execute(insert_command_generic)	
						cr.commit()					

						Main_Str = "select distinct on(CC.id)CC.id,CC.check_exist,CC.message_id_new,CC.name,CL.branch_id,(Select name from res_company where id=CC.origin),CC.request_type,CC.user_name,CC.state,CC.request_date,CC.user_id,CC.request_id,case when CC.state in ('open','cancel','new') then "+str(o.id)+" else Null end,case when CC.state in ('progress','closed') then "+str(o.id)+" else Null end,case when CC.ccc_update_check=True and CC.message_id_new=False and CC.state != 'new' then "+str(o.id)+" else Null end,ph.name,case when CC.state not in ('cancel','closed') then to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(cast(now() as date),cast(CC.request_date as date)) ) else  to_char(CC.request_date,'dd')||'/'||to_char(CC.request_date, 'Mon')||':' || date_part('day',age(CC.close_date,cast(CC.request_date as date))) end,CL.service_area,CL.assign_resource from ccc_branch_new CC left join res_partner AM on AM.id=CC.partner_id left join customer_line CM on AM.id=CM.partner_id left join customer_branch_lead_line CL on CL.lead_id= CC.id left join phone_m2m ph on ph.res_location_id=CM.customer_address where CC.request_type='lead_request' "

						Main_Str1 = Main_Str + Sql_Str3
						
						insert_command = "insert into ccc_branch_request_line (request_search,check_exist,message_id_new,customer_name,branch_id,origin,request_type,user_name,state,sort_date,user_id,request_id,ccc_branch_id,ccc_assign_id,ccc_update_id,contact_number,date_age,service_area,assign_resource) ("+Main_Str1+")"

						cr.execute(insert_command)

						cr.commit()

						search_com = "select cs.id from ccc_branch_request_line cs  join ccc_branch cc on case when cs.state in ('open','cancel','new') then   cs.ccc_branch_id="+str(o.id)+" when cs.state in ('progress','closed') then   cs.ccc_assign_id="+str(o.id)+" else    cs.ccc_update_id="+str(o.id)+" end order by cs.id desc limit 1"

						cr.execute(search_com)
					
						if not cr.fetchall():
							self.write(cr,uid,ids,{'check':True})
						else:
							self.write(cr,uid,ids,{'check':False})
						# if o.lead_tracker:
						for i in o.request_line:
							if not i.contact_number:
								ccc_request=self.pool.get('ccc.branch.new').search(cr,uid,[('id','=',i.request_search)])
								if ccc_request:
									ccc_brw=self.pool.get('ccc.branch.new').browse(cr,uid,ccc_request[0])
									if ccc_brw.phone_many2one:
										cr.execute("update ccc_branch_request_line set contact_number='"+str(ccc_brw.phone_many2one.number)+"' where id ="+str(i.id)+"")
						cr.commit()
					except Exception  as exc:
						if exc.__class__.__name__ == 'TransactionRollbackError':
							pass
						else:
							raise	 
					
			if rec == 'product_request' :
				self.get_product_requests(cr, uid, ids[0])
			if rec == 'product_information_request' :
				self.get_information_requests(cr, uid, ids[0])
			if rec == 'product_complaint_request' :
				self.get_complaint_requests(cr, uid, ids[0])
			if rec == 'customer' :
				try:

					Sql_Str = ''
					if aaa.job_id:
							Sql_Str = Sql_Str + " and AM.id in (select rs.name_contact from res_scheduledjobs rs where rs.scheduled_job_id ilike '" +"%"+ str(job_id) + "%')"	
					if aaa.contract_number:
						Sql_Str = Sql_Str + " and AM.id in (select RP.partner_id from sale_contract RP where RP.contract_number ilike '" +"%"+ str(aaa.contract_number) + "%')"	
					if aaa.customer_id:
						Sql_Str = Sql_Str + " and AM.ou_id ilike '" +"%"+ str(aaa.customer_id) + "%'"
					if aaa.req_id:
							#Sql_Str = Sql_Str + " and AM.id=CC.partner_id and CC.request_id ilike '" +"%"+ str(aaa.req_id) + "%'"


							Sql_Str = Sql_Str + " and AM.id in (select rs.partner_id from ccc_branch_new rs where rs.request_id ilike '" +"%"+ str(aaa.req_id) + "%')"	
					if aaa.partner_name_cust:
						Sql_Str = Sql_Str + " and AM.name ilike '" +"%"+ str(aaa.partner_name_cust) + "%'"
					if aaa.contact_name_cust:
						Sql_Str = Sql_Str +" and AM.contact_name ilike '" +  "%" + str(aaa.contact_name_cust) + "%'"
					if aaa.city_id.id:
						Sql_Str = Sql_Str +" and AM.city_id = '"  + str(aaa.city_id.id) + "'"	
					if aaa.mobile_cust:
						Sql_Str = Sql_Str+" and CM.customer_address in (select i.res_location_id from phone_m2m i where i.name ilike '"+"%" + str(aaa.mobile_cust) + "%' and i.type in ('"'mobile'"','"'landline'"')) or CN.number='"+str(aaa.mobile_cust)+"'"

					if aaa.phone_cust:
						
						Sql_Str = Sql_Str+" and CM.customer_address in (select i.res_location_id from phone_m2m i where i.name ilike '"+"%" + str(aaa.phone_cust) + "%' and i.type in ('"'mobile'"','"'landline'"')) or CN.number='"+str(aaa.phone_cust)+"'"
						
					if aaa.pincode:
						Sql_Str = Sql_Str +" and AM.zip ilike '" +  "%" + str(aaa.pincode) + "%'"
					if aaa.branch_id:
						Sql_Str =Sql_Str +" and CM.branch = '" + str(aaa.branch_id.id) + "'"
					if aaa.due_date_from_cust:
						Sql_Str =Sql_Str +" and AM.customer_since >= '" +  str(aaa.due_date_from_cust) + "'"
					if aaa.due_date_to_cust:
						Sql_Str =Sql_Str +" and AM.customer_since <= '" + str(aaa.due_date_to_cust) + "'"


					if aaa.landmark:
							Sql_Str =Sql_Str +" and AM.landmark ilike '"  +  "%" + str(aaa.landmark) + "%'"

					if aaa.subarea:
							Sql_Str =Sql_Str +" and AM.sub_area ilike '" +  "%" + str(aaa.subarea) + "%'"

					if aaa.location_name:
							Sql_Str =Sql_Str +" and AM.location_name ilike  '" +  "%" + str(aaa.location_name) + "%'"
					if aaa.building:
							Sql_Str =Sql_Str +" and AM.building ilike  '" +  "%" + str(aaa.building) + "%'"
					if aaa.customer_category_id:
							Sql_Str =Sql_Str +" and AM.tag_new ilike  '" +  "%" + str(aaa.customer_category_id.name) + "%'"	
					#Main_Str123 = "select distinct (AM.id) from res_partner AM , customer_line CM where  AM.id=CM.partner_id and AM.ou_id is not Null  and AM.active=True "
					Main_Str123 = "select distinct (AM.id) from contact_name CN right join res_partner AM on CN.contact_id=AM.id left join customer_line CM on AM.id=CM.partner_id where AM.ou_id is not Null  and AM.active=True "

					main_str1234=Main_Str123 + Sql_Str
						
					update_command = "update res_partner set customer_branch_id ="+str(search_id)+"  where id in ("+main_str1234+")"				

					cr.execute(update_command)
					cr.commit()


					search_com = "select cs.id from res_partner cs join ccc_branch cc on cs.customer_branch_id="+str(o.id)+" order by cs.id desc limit 1"

				
					cr.execute(search_com)
					

					if not cr.fetchall():
						self.write(cr,uid,ids,{'check':True})
					else:
						self.write(cr,uid,ids,{'check':False})
					cr.commit()	

				except Exception  as exc:
						if exc.__class__.__name__ == 'TransactionRollbackError':
							pass
						else:
							raise
		return True

	def search_ccc_branch_psd(self,cr,uid,ids,context=None):
		rec = self.browse(cr, uid, ids[0])
		if rec.enquiry_type == 'customers':
			self.get_customers(cr, uid, ids[0])
		if rec.enquiry_type == 'product_request':
			self.get_product_requests(cr, uid, ids[0])	
		if rec.enquiry_type == 'complaint_request':
			self.get_complaint_requests(cr, uid, ids[0])		
		if rec.enquiry_type == 'information_request':
			self.get_information_requests(cr, uid, ids[0])	
		if rec.enquiry_type == 'all_requests':
			self.get_all_requests(cr, uid, ids[0])						
		return True

	# def search_ccc_branch(self,cr,uid,ids,context=None):

ccc_branch()


class ccc_branch_request_line(osv.osv):
	_inherit = "ccc.branch.request.line"

	_columns = {
		'customer_id':fields.char('Customer ID',size=50),
		'contact_name':fields.char('Contact Name',size=50),
		'complete_address':fields.char('Address',size=100),
		'customer_since': fields.char('Created Date',size=25),
		'ccc_customer_id':fields.many2one('ccc.branch'),
		'ccc_product_id':fields.many2one('ccc.branch'),
		'ccc_complaint_id':fields.many2one('ccc.branch'),
		'ccc_information_id':fields.many2one('ccc.branch'),
		'partner_id': fields.many2one('res.partner'),
		'product_request_id': fields.many2one('product.request'),
		'complaint_request_id': fields.many2one('product.complaint.request'),
		'information_request_id': fields.many2one('product.information.request'),
		'request_type_psd': fields.selection([('product_request','Product Request'),
											  ('complaint_request','Product Complaint Request'),
											  ('information_request','Product Information Request')
											 ],'Request Type'),
		'created_by':fields.many2one('res.users','Created By'),  
		'employee_id': fields.many2one('hr.employee', 'PSE')
	}

	def reload_customer(self,cr,uid,ids,context=None):
		rec = self.browse(cr, uid, ids[0])
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'base', 'view_partner_form')
		view_id = view and view[1] or False
		return {
			'name': _('Customer'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'res.partner',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': rec.partner_id.id,
		}

	def reload_product_request(self,cr,uid,ids,context=None):
		rec = self.browse(cr, uid, ids[0])
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_cid', 'view_product_request_form_crm')
		view_id = view and view[1] or False
		context.update({'hide_create_quotation':True})
		return {
			'name': _('Product Request'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'product.request',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': rec.product_request_id.id,
			'context':context
		}

	def reload_complaint_request(self,cr,uid,ids,context=None):
		rec = self.browse(cr, uid, ids[0])
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_cid', 'complaint_request_form_psd')
		view_id = view and view[1] or False
		return {
			'name': _('Product Complaint Request'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'product.complaint.request',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': rec.complaint_request_id.id,
			'context':context
		}		

	def reload_information_request(self,cr,uid,ids,context=None):
		rec = self.browse(cr, uid, ids[0])
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_cid', 'view_info_request_form_crm')
		view_id = view and view[1] or False
		return {
			'name': _('Product Information Request'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'product.information.request',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': rec.information_request_id.id,
			'context':context
		}	

	def reload_record(self,cr,uid,ids,context=None):
		rec = self.browse(cr, uid, ids[0])

		if rec.request_type_psd == 'product_request' and rec.request_type_psd != 'complaint_request' and rec.request_type_psd != 'information_request':
			rec = self.browse(cr, uid, ids[0])
			view = self.pool.get('ir.model.data').get_object_reference(
				cr, uid, 'psd_cid', 'view_product_request_form_crm')
			view_id = view and view[1] or False
			context.update({'hide_create_quotation':True})
			return {
				'name': _('Product Request'),
				'view_type': 'form',
				'view_mode': 'form',
				'view_id': view_id or False,
				'res_model': 'product.request',
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'current',
				'res_id': rec.product_request_id.id,
				'context':context
			}

		if rec.request_type_psd == 'complaint_request' and rec.request_type_psd != 'product_request' and rec.request_type_psd != 'information_request':
			rec = self.browse(cr, uid, ids[0])
			view = self.pool.get('ir.model.data').get_object_reference(
				cr, uid, 'psd_cid', 'complaint_request_form_psd')
			view_id = view and view[1] or False
			return {
				'name': _('Product Complaint Request'),
				'view_type': 'form',
				'view_mode': 'form',
				'view_id': view_id or False,
				'res_model': 'product.complaint.request',
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'current',
				'res_id': rec.complaint_request_id.id,
				'context':context
			}
		if rec.request_type_psd == 'information_request' and rec.request_type_psd != 'product_request' and rec.request_type_psd != 'complaint_request':
			rec = self.browse(cr, uid, ids[0])
			view = self.pool.get('ir.model.data').get_object_reference(
				cr, uid, 'psd_cid', 'view_info_request_form_crm')
			view_id = view and view[1] or False
			return {
				'name': _('Product Information Request'),
				'view_type': 'form',
				'view_mode': 'form',
				'view_id': view_id or False,
				'res_model': 'product.information.request',
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'current',
				'res_id': rec.information_request_id.id,
				'context':context
			}


ccc_branch_request_line()