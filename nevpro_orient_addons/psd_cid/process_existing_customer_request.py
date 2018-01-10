from datetime import date,datetime, timedelta
from osv import osv,fields
from tools.translate import _

class product_request(osv.osv):
	_inherit = 'product.request'

	def process_single_address_line(self,cr,uid,ids,context=None):
		partner_obj = self.pool.get('res.partner')
		partner_addrs_obj = self.pool.get('res.partner.address')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		prod_req_line_obj = self.pool.get('product.request.line')
		customer_line_obj = self.pool.get('customer.line')
		crm_lead_obj = self.pool.get('crm.lead')
		phone_child_obj = self.pool.get('phone.number.child')
		phone_m2m_obj = self.pool.get('phone.m2m')
		phone_child_id = False
		phone_m2m_id = False
		pro_ids = []
		office = context.get('office')
		location = context.get('location')
		rec = self.browse(cr,uid,ids[0])
		partner_id = partner_obj.search(cr, uid, [('ou_id','=',rec.customer_id),('company_id','=',office)], context=context)
		if not partner_id:
			customer_inc_no = self.pool.get('ir.sequence').get(cr, uid, 'res.partner') 
		if partner_id:
			cust_prefix = False
			customer_seq = partner_obj.browse(cr, uid, partner_id[0]).ou_id
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
			partner_id = partner_id[0]
			partner_obj.write(cr, uid, partner_id, {'segment': rec.segment}, context=context)
		else:
			partner_addrs_data = partner_addrs_obj.browse(cr, uid, location)
			if partner_addrs_data.phone_m2m_xx:
				phone_child_id = phone_child_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('number','=',partner_addrs_data.phone_m2m_xx.name)], context=context)
				if phone_child_id:
					phone_child_id = phone_child_id[0]
				else:
					phone_child_id = phone_child_obj.create(cr, uid, {
							'partner_id': rec.partner_id.id,
							'contact_select': partner_addrs_data.phone_m2m_xx.type,
							'number': partner_addrs_data.phone_m2m_xx.name
						}, context=context)
			else:
				if rec.phone_many2one:
					phone_child_id = rec.phone_many2one.id
			cust_prefix = '0000'
			customer_seq = cust_prefix+customer_inc_no
			partner_vals={
				'name': rec.name,
				'first_name': partner_addrs_data.first_name,
				'last_name': partner_addrs_data.last_name,
				'middle_name': partner_addrs_data.middle_name,
				'designation': partner_addrs_data.designation,
				'premise_type': partner_addrs_data.premise_type,
				'location_name': partner_addrs_data.location_name,
				'apartment': partner_addrs_data.apartment,
				'building': partner_addrs_data.building,
				'sub_area': partner_addrs_data.sub_area,
				'street': partner_addrs_data.street,
				'landmark': partner_addrs_data.landmark,
				'city_id': partner_addrs_data.city_id.id or False,
				'district': partner_addrs_data.district.id or False,
				'tehsil': partner_addrs_data.tehsil.id or False,
				'state_id': partner_addrs_data.state_id.id or False,
				'zip': partner_addrs_data.zip,
				'fax': partner_addrs_data.fax,
				'email': partner_addrs_data.email,
				'segment': rec.segment,
				'phone_many2one': phone_child_id,
				'ref_by': rec.ref_by and rec.ref_by.id,
				'customer': True,
				'ou_id': customer_seq,
				'customer_id_main': customer_seq,
				'customer_since': datetime.now(),
				'company_id': office,
				'psd': True
			}
			if partner_addrs_data.middle_name and partner_addrs_data.last_name:
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+' '+partner_addrs_data.last_name
			if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
				contact_name = partner_addrs_data.first_name
			if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
			if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
			partner_vals.update({'contact_name':contact_name})
			partner_id = partner_obj.create(cr, uid, partner_vals, context=context)	
			if partner_addrs_data.phone_m2m_xx:
				phone_m2m_id = partner_addrs_data.phone_m2m_xx.id
			else:
				if rec.phone_many2one:
					phone_m2m_id = phone_m2m_obj.create(cr, uid, {
										'res_location_id': partner_addrs_data.id,
										'name': rec.phone_many2one.number,
										'type': rec.phone_many2one_new.contact_select
									}, context=context)
			address_vals = {
				'first_name': partner_addrs_data.first_name,
				'last_name': partner_addrs_data.last_name,
				'middle_name': partner_addrs_data.middle_name,
				'designation': partner_addrs_data.designation,
				'premise_type': partner_addrs_data.premise_type,
				'location_name': partner_addrs_data.location_name,
				'apartment': partner_addrs_data.apartment,
				'building': partner_addrs_data.building,
				'sub_area': partner_addrs_data.sub_area,
				'street': partner_addrs_data.street,
				'landmark': partner_addrs_data.landmark,
				'city_id': partner_addrs_data.city_id.id or False,
				'district': partner_addrs_data.district.id or False,
				'tehsil': partner_addrs_data.tehsil.id or False,
				'state_id': partner_addrs_data.state_id.id or False,
				'zip': partner_addrs_data.zip,
				'fax': partner_addrs_data.fax,
				'email': partner_addrs_data.email,
				'segment': rec.segment,
				'phone_m2m_xx': phone_m2m_id,
				'ref_by': partner_addrs_data.ref_by.id or False,
				'exempted': partner_addrs_data.exempted,
				'exempted_classification': partner_addrs_data.exempted_classification.id,
				'certificate_no': partner_addrs_data.certificate_no,
				'exem_attachment': partner_addrs_data.exem_attachment,
				'adhoc_job': partner_addrs_data.adhoc_job,
				'partner_id': partner_id,
				'company_id': office,
				'primary_contact': True
			}
			if partner_addrs_data.middle_name and partner_addrs_data.last_name:
				name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+''+partner_addrs_data.last_name
			if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
				name = partner_addrs_data.first_name
			if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
				name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
			if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
				name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
			address_vals.update({'name': name})	
			address_id = partner_addrs_obj.create(cr, uid, address_vals, context=context)
			loc_prefix = '0000'
			loc_inc_no = 1
			if loc_inc_no >= 0 and loc_inc_no <= 9:
				st_loc_inc_no = '0'+str(loc_inc_no)
			elif loc_inc_no >= 10 and loc_inc_no <= 99:
				st_loc_inc_no = str(loc_inc_no)
			location_id = loc_prefix+customer_inc_no+st_loc_inc_no
			cust_line_vals = {
				'location_id': location_id,
				'premise_type_import': partner_addrs_data.premise_type, 
				'branch': office,
				'customer_address': address_id,
				'partner_id': partner_id,
				'phone_many2one': phone_m2m_id
			}
			cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)
		req_ids = crm_lead_obj.search(cr, uid, [('partner_id','=',partner_id)], context=context)	
		pr_inc_no = len(req_ids)+1
		if pr_inc_no >= 0 and pr_inc_no <= 9:
			st_pr_inc_no = '00'+str(pr_inc_no)
		elif pr_inc_no >= 10 and pr_inc_no <= 99:
			st_pr_inc_no = '0'+str(pr_inc_no)
		elif pr_inc_no >= 100 and pr_inc_no <= 999:	
			st_pr_inc_no = str(pr_inc_no)	
		pr_code = 'PR'	
		if rec.location_request_line[0].branch_id.id != rec.company_id.id:
			pr_code = 'PRO'	
		pr_seq = rec.company_id.pcof_key + pr_code + customer_inc_no + st_pr_inc_no
		prod_req_loc_obj.write(cr, uid, rec.location_request_line[0].id, {'product_request_ref': pr_seq}, context=context)
		if rec.company_id.establishment_type == 'crm':
			location_branch = 'crm'
		elif rec.location_request_line[0].branch_id.id == rec.company_id.id:
			location_branch = 'same'
		else:
			location_branch = 'different'
		self.write(cr,uid,ids[0],
			{
				'state': 'open',
				'location_branch': location_branch,
				'request_date': datetime.now(),
				'partner_id': partner_id,
				'customer_id': customer_seq,
				'product_request_id': pr_seq,
				'parent_request': ids[0]
		},context=context)
		crm_lead_vals = {
			'inquiry_no': pr_seq,
			'type_request': 'product_request_psd',
			'state': 'open',
			'partner_id': partner_id,
			'created_by_global': rec.created_by.name,
			'inspection_date':	rec.request_date,
			'product_request_id': ids[0],										
		}
		crm_lead_obj.create(cr, uid, crm_lead_vals, context=context)
		pro_ids.append(ids[0])
		return pro_ids

	def same_address_different_offices(self,cr,uid,ids,context=None):
		partner_obj = self.pool.get('res.partner')
		company_obj = self.pool.get('res.company')
		partner_addrs_obj = self.pool.get('res.partner.address')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		prod_req_line_obj = self.pool.get('product.request.line')
		customer_line_obj = self.pool.get('customer.line')
		crm_lead_obj = self.pool.get('crm.lead')
		phone_child_obj = self.pool.get('phone.number.child')
		phone_m2m_obj = self.pool.get('phone.m2m')
		pro_ids = []
		phone_child_id = False
		phone_m2m_id = False
		offices = context.get('offices')
		locations = context.get('locations')
		rec = self.browse(cr, uid, ids[0])
		customer_inc_no_new = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
		for each in offices:
			loc_req_line_ids = []
			prod_req_line_ids = prod_req_loc_obj.search(cr, uid, [('branch_id','=',each),('location_request_id','=',ids[0])], context=context)
			for prod_req_line_id in prod_req_line_ids:
				prod_req_loc_data = prod_req_loc_obj.browse(cr, uid, prod_req_line_id)
				loc_req_line_id = (0, 0, {
					'address': prod_req_loc_data.address,
					'address_id': prod_req_loc_data.address_id,
					'product_generic_id': prod_req_loc_data.product_generic_id.id,
					'sku_name_id': prod_req_loc_data.sku_name_id.id or False,
					'product_uom_id': prod_req_loc_data.product_uom_id.id,
					'branch_id': prod_req_loc_data.branch_id.id,
					'quantity': prod_req_loc_data.quantity,
					'remarks': prod_req_loc_data.remarks,
					'exempted':prod_req_loc_data.exempted,
					'location_request_id': ids[0],
				})
				loc_req_line_ids.append(loc_req_line_id)
			partner_addrs_data = partner_addrs_obj.browse(cr, uid, locations[0])
			if partner_addrs_data.phone_m2m_xx:
				phone_child_id = phone_child_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('number','=',partner_addrs_data.phone_m2m_xx.name)], context=context)
				if phone_child_id:
					phone_child_id = phone_child_id[0]
				else:
					phone_child_id = phone_child_obj.create(cr, uid, {
							'partner_id': rec.partner_id.id,
							'contact_select': partner_addrs_data.phone_m2m_xx.type,
							'number': partner_addrs_data.phone_m2m_xx.name
						}, context=context)
			else:
				if rec.phone_many2one:
					phone_child_id = rec.phone_many2one.id
			pro_req_vals = {
				'name': rec.name,
				'title': partner_addrs_data.title,
				'first_name': partner_addrs_data.first_name,
				'middle_name': partner_addrs_data.middle_name, 
				'last_name': partner_addrs_data.last_name, 
				'designation': partner_addrs_data.designation, 
				'premise_type': partner_addrs_data.premise_type, 
				'building': partner_addrs_data.building, 
				'location_name': partner_addrs_data.location_name, 
				'apartment': partner_addrs_data.apartment,
				'sub_area': partner_addrs_data.sub_area,
				'street': partner_addrs_data.street,
				'landmark': partner_addrs_data.landmark,
				'tehsil': partner_addrs_data.tehsil and partner_addrs_data.tehsil.id,
				'state_id': partner_addrs_data.state_id and partner_addrs_data.state_id.id,
				'city_id': partner_addrs_data.city_id and partner_addrs_data.city_id.id,
				'district': partner_addrs_data.district and partner_addrs_data.district.id ,
				'zip': partner_addrs_data.zip,
				'email': partner_addrs_data.email,
				'fax': partner_addrs_data.fax,
				'phone_many2one': phone_child_id,
				'ref_by': rec.ref_by and rec.ref_by.id,
				'inquiry_type': 'product',
				'call_type': rec.call_type,
				'state': 'open',
				'confirm_check': True,
				'request_date': datetime.now(),
				'created_by': rec.created_by.id,
				'location_request_line': loc_req_line_ids,
				'customer_type': 'existing',
				'segment': rec.segment,
				'hide_search': True,
				'hide_ref': True,
				'hide_segment': True,
				'parent_request': ids[0]
			}
			pro_id = self.create(cr, uid, pro_req_vals, context=context)
			pro_ids.append(pro_id)
			partner_id = partner_obj.search(cr, uid, [('ou_id','=',rec.customer_id),('company_id','=',each)], context=context)
			company = self.pool.get('res.company').browse(cr, uid, each).name
			if partner_id:
				cust_prefix = False
				customer_seq = partner_obj.browse(cr, uid, partner_id[0]).ou_id
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
				partner_id = partner_id[0]
				partner_obj.write(cr, uid, partner_id, {'segment': rec.segment}, context=context)
			else:
				cust_prefix = '0000'
				customer_inc_no = customer_inc_no_new
				customer_seq = cust_prefix+customer_inc_no
				partner_vals={
					'name': rec.name,
					'first_name': partner_addrs_data.first_name,
					'last_name': partner_addrs_data.last_name,
					'middle_name': partner_addrs_data.middle_name,
					'designation': partner_addrs_data.designation,
					'premise_type': partner_addrs_data.premise_type,
					'location_name': partner_addrs_data.location_name,
					'apartment': partner_addrs_data.apartment,
					'building': partner_addrs_data.building,
					'sub_area': partner_addrs_data.sub_area,
					'street': partner_addrs_data.street,
					'landmark': partner_addrs_data.landmark,
					'city_id': partner_addrs_data.city_id.id or False,
					'district': partner_addrs_data.district.id or False,
					'tehsil': partner_addrs_data.tehsil.id or False,
					'state_id': partner_addrs_data.state_id.id or False,
					'zip': partner_addrs_data.zip,
					'fax': partner_addrs_data.fax,
					'email': partner_addrs_data.email,
					'phone_many2one': phone_child_id,
					'segment': rec.segment,
					'ref_by': rec.ref_by and rec.ref_by.id,
					'customer': True,
					'ou_id': customer_seq,
					'customer_id_main': customer_seq,
					'customer_since': datetime.now(),
					'company_id': each,
					'psd': True
				}
				if partner_addrs_data.middle_name and partner_addrs_data.last_name:
					contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+' '+partner_addrs_data.last_name
				if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
					contact_name = partner_addrs_data.first_name
				if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
					contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
				if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
					contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
				partner_vals.update({'contact_name':contact_name})
				partner_id = partner_obj.create(cr, uid, partner_vals, context=context)	
				if partner_addrs_data.phone_m2m_xx:
					phone_m2m_id = partner_addrs_data.phone_m2m_xx.id
				else:
					if rec.phone_many2one:
						phone_m2m_id = phone_m2m_obj.create(cr, uid, {
											'res_location_id': partner_addrs_data.id,
											'name': rec.phone_many2one.number,
											'type': rec.phone_many2one_new.contact_select
										}, context=context)
				address_vals = {
					'first_name': partner_addrs_data.first_name,
					'last_name': partner_addrs_data.last_name,
					'middle_name': partner_addrs_data.middle_name,
					'designation': partner_addrs_data.designation,
					'premise_type': partner_addrs_data.premise_type,
					'location_name': partner_addrs_data.location_name,
					'apartment': partner_addrs_data.apartment,
					'building': partner_addrs_data.building,
					'sub_area': partner_addrs_data.sub_area,
					'street': partner_addrs_data.street,
					'landmark': partner_addrs_data.landmark,
					'city_id': partner_addrs_data.city_id.id or False,
					'district': partner_addrs_data.district.id or False,
					'tehsil': partner_addrs_data.tehsil.id or False,
					'state_id': partner_addrs_data.state_id.id or False,
					'zip': partner_addrs_data.zip,
					'fax': partner_addrs_data.fax,
					'email': partner_addrs_data.email,
					'phone_m2m_xx': phone_m2m_id,
					'ref_by': partner_addrs_data.ref_by.id or False,
					'segment': rec.segment,
					'exempted': partner_addrs_data.exempted,
					'exempted_classification': partner_addrs_data.exempted_classification.id,
					'certificate_no': partner_addrs_data.certificate_no,
					'exem_attachment': partner_addrs_data.exem_attachment,
					'adhoc_job': partner_addrs_data.adhoc_job,
					'partner_id': partner_id,
					'company_id': each,
					'primary_contact': True
				}
				if partner_addrs_data.middle_name and partner_addrs_data.last_name:
					name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+' '+partner_addrs_data.last_name
				if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
					name = partner_addrs_data.first_name
				if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
					name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
				if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
					name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
				address_vals.update({'name': name})	
				address_id = partner_addrs_obj.create(cr, uid, address_vals, context=context)
				loc_prefix = '0000'
				loc_inc_no = 1
				if loc_inc_no >= 0 and loc_inc_no <= 9:
					st_loc_inc_no = '0'+str(loc_inc_no)
				elif loc_inc_no >= 10 and loc_inc_no <= 99:
					st_loc_inc_no = str(loc_inc_no)
				location_id = loc_prefix+customer_inc_no+st_loc_inc_no
				cust_line_vals = {
					'location_id': location_id,
					'premise_type_import': partner_addrs_data.premise_type,
					'branch': each,
					'customer_address': address_id,
					'partner_id': partner_id,
					'phone_many2one': phone_m2m_id
				}
				cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)
			pro_data = self.browse(cr, uid, pro_id)		
			if pro_data.company_id.establishment_type == 'crm':
				location_branch = 'crm'
			elif pro_data.location_request_line[0].branch_id.id == pro_data.company_id.id:
				location_branch = 'same'
			else:
				location_branch = 'different'	
			req_ids = crm_lead_obj.search(cr, uid, [('partner_id','=',partner_id)], context=context)	
			pr_inc_no = len(req_ids)+1
			if pr_inc_no >= 0 and pr_inc_no <= 9:
				st_pr_inc_no = '00'+str(pr_inc_no)
			elif pr_inc_no >= 10 and pr_inc_no <= 99:
				st_pr_inc_no = '0'+str(pr_inc_no)
			elif pr_inc_no >= 100 and pr_inc_no <= 999:	
				st_pr_inc_no = str(pr_inc_no)	
			pr_code = 'PR'	
			if pro_data.location_request_line[0].branch_id.id != pro_data.company_id.id:
				pr_code = 'PRO'		
			pr_seq = rec.company_id.pcof_key + pr_code + customer_inc_no + st_pr_inc_no
			self.write(cr, uid, pro_id, 
				{
					'product_request_id': pr_seq,			
					'customer_id': customer_seq, 
					'partner_id': partner_id,
					'location_branch': location_branch,
				}, context=context)
			pro_loc_ids = prod_req_loc_obj.search(cr, uid, [('location_request_id','=',pro_id)], context=context)
			for pro_loc_id in pro_loc_ids:
				prod_req_loc_obj.write(cr, uid, pro_loc_id, {'product_request_ref':pr_seq}, context=context)
			crm_lead_vals = {
				'inquiry_no': pr_seq,
				'type_request': 'product_request_psd',
				'state': 'open',
				'partner_id': partner_id,
				'created_by_global': rec.created_by.name,
				'inspection_date':	rec.request_date,
				'product_request_id': pro_id,										
			}
			crm = crm_lead_obj.create(cr, uid, crm_lead_vals, context=context)
		self.write(cr, uid, ids[0], {'active': False}, context=context)
		return pro_ids

	def same_address_same_office(self,cr,uid,ids,context=None):
		partner_obj = self.pool.get('res.partner')
		partner_addrs_obj = self.pool.get('res.partner.address')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		prod_req_line_obj = self.pool.get('product.request.line')
		customer_line_obj = self.pool.get('customer.line')
		crm_lead_obj = self.pool.get('crm.lead')
		phone_child_obj = self.pool.get('phone.number.child')
		phone_m2m_obj = self.pool.get('phone.m2m')
		rec = self.browse(cr,uid,ids[0])
		offices = context.get('offices')
		locations = context.get('locations')
		phone_child_id = False
		phone_m2m_id = False
		pro_ids = []
		partner_id = partner_obj.search(cr, uid, [('ou_id','=',rec.customer_id),('company_id','=',offices[0])], context=context)
		if not partner_id:
			customer_inc_no = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
		if partner_id:
			cust_prefix = False
			customer_seq = partner_obj.browse(cr, uid, partner_id[0]).ou_id
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
			partner_id = partner_id[0]
			partner_obj.write(cr, uid, partner_id, {'segment': rec.segment}, context=context)
		else:
			partner_addrs_data = partner_addrs_obj.browse(cr, uid, locations[0])
			if partner_addrs_data.phone_m2m_xx:
				phone_child_id = phone_child_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('number','=',partner_addrs_data.phone_m2m_xx.name)], context=context)
				if phone_child_id:
					phone_child_id = phone_child_id[0]
				else:
					phone_child_id = phone_child_obj.create(cr, uid, {
							'partner_id': rec.partner_id.id,
							'contact_select': partner_addrs_data.phone_m2m_xx.type,
							'number': partner_addrs_data.phone_m2m_xx.name
						}, context=context)
			else:
				if rec.phone_many2one:
					phone_child_id = rec.phone_many2one.id
			cust_prefix = '0000'
			customer_seq = cust_prefix+customer_inc_no
			partner_vals={
				'name': rec.name,
				'first_name': partner_addrs_data.first_name,
				'last_name': partner_addrs_data.last_name,
				'middle_name': partner_addrs_data.middle_name,
				'designation': partner_addrs_data.designation,
				'premise_type': partner_addrs_data.premise_type,
				'location_name': partner_addrs_data.location_name,
				'apartment': partner_addrs_data.apartment,
				'building': partner_addrs_data.building,
				'sub_area': partner_addrs_data.sub_area,
				'street': partner_addrs_data.street,
				'landmark': partner_addrs_data.landmark,
				'city_id': partner_addrs_data.city_id.id or False,
				'district': partner_addrs_data.district.id or False,
				'tehsil': partner_addrs_data.tehsil.id or False,
				'state_id': partner_addrs_data.state_id.id or False,
				'zip': partner_addrs_data.zip,
				'fax': partner_addrs_data.fax,
				'email': partner_addrs_data.email,
				'segment': rec.segment,
				'phone_many2one': phone_child_id,
				'ref_by': rec.ref_by and rec.ref_by.id,
				'customer': True,
				'ou_id': customer_seq,
				'customer_id_main': customer_seq,
				'customer_since': datetime.now(),
				'company_id': offices[0],
				'psd': True
			}
			if partner_addrs_data.middle_name and partner_addrs_data.last_name:
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+' '+partner_addrs_data.last_name
			if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
				contact_name = partner_addrs_data.first_name
			if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
			if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
			partner_vals.update({'contact_name':contact_name})
			partner_id = partner_obj.create(cr, uid, partner_vals, context=context)	
			if partner_addrs_data.phone_m2m_xx:
				phone_m2m_id = partner_addrs_data.phone_m2m_xx.id
			else:
				if rec.phone_many2one:
					phone_m2m_id = phone_m2m_obj.create(cr, uid, {
										'res_location_id': partner_addrs_data.id,
										'name': rec.phone_many2one.number,
										'type': rec.phone_many2one_new.contact_select
									}, context=context)
			address_vals = {
				'first_name': partner_addrs_data.first_name,
				'last_name': partner_addrs_data.last_name,
				'middle_name': partner_addrs_data.middle_name,
				'designation': partner_addrs_data.designation,
				'premise_type': partner_addrs_data.premise_type,
				'location_name': partner_addrs_data.location_name,
				'apartment': partner_addrs_data.apartment,
				'building': partner_addrs_data.building,
				'sub_area': partner_addrs_data.sub_area,
				'street': partner_addrs_data.street,
				'landmark': partner_addrs_data.landmark,
				'city_id': partner_addrs_data.city_id.id or False,
				'district': partner_addrs_data.district.id or False,
				'tehsil': partner_addrs_data.tehsil.id or False,
				'state_id': partner_addrs_data.state_id.id or False,
				'zip': partner_addrs_data.zip,
				'fax': partner_addrs_data.fax,
				'email': partner_addrs_data.email,
				'segment': rec.segment,
				'phone_m2m_xx': phone_m2m_id,
				'ref_by': partner_addrs_data.ref_by.id or False,
				'exempted': partner_addrs_data.exempted,
				'exempted_classification': partner_addrs_data.exempted_classification.id,
				'certificate_no': partner_addrs_data.certificate_no,
				'exem_attachment': partner_addrs_data.exem_attachment,
				'adhoc_job': partner_addrs_data.adhoc_job,
				'partner_id': partner_id,
				'company_id': offices[0],
				'primary_contact': True
			}
			if partner_addrs_data.middle_name and partner_addrs_data.last_name:
				name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+''+partner_addrs_data.last_name
			if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
				name = partner_addrs_data.first_name
			if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
				name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
			if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
				name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
			address_vals.update({'name': name})	
			address_id = partner_addrs_obj.create(cr, uid, address_vals, context=context)
			loc_prefix = '0000'
			loc_inc_no = 1
			if loc_inc_no < 10:
				st_loc_inc_no = '0'+str(loc_inc_no)
			else:	
				st_loc_inc_no = str(loc_inc_no)
			location_id = loc_prefix+customer_inc_no+st_loc_inc_no
			cust_line_vals = {
				'location_id': location_id,
				'premise_type_import': partner_addrs_data.premise_type,
				'branch': offices[0],
				'customer_address': address_id,
				'partner_id': partner_id,
				'phone_many2one': phone_m2m_id
			}
			cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)
		req_ids = crm_lead_obj.search(cr, uid, [('partner_id','=',partner_id)], context=context)	
		pr_inc_no = len(req_ids)+1
		if pr_inc_no >= 0 and pr_inc_no <= 9:
			st_pr_inc_no = '00'+str(pr_inc_no)
		elif pr_inc_no >= 10 and pr_inc_no <= 99:
			st_pr_inc_no = '0'+str(pr_inc_no)
		elif pr_inc_no >= 100 and pr_inc_no <= 999:	
			st_pr_inc_no = str(pr_inc_no)	
		pr_code	= 'PR'
		if rec.location_request_line[0].branch_id.id != rec.company_id.id:
			pr_code = 'PRO'
		pr_seq = rec.company_id.pcof_key + pr_code + customer_inc_no + st_pr_inc_no		
		for each in rec.location_request_line:
			prod_req_loc_obj.write(cr, uid, each.id, {'product_request_ref': pr_seq}, context=context)
		if rec.company_id.establishment_type == 'crm':
			location_branch = 'crm'
		elif rec.location_request_line[0].branch_id.id == rec.company_id.id:
			location_branch = 'same'
		else:
			location_branch = 'different'	
		self.write(cr,uid,ids,
			{
				'state': 'open',
				'location_branch': location_branch,
				'request_date': datetime.now(),
				'partner_id': partner_id,
				'customer_id': customer_seq,
				'product_request_id': pr_seq,
				'parent_request': ids[0]
		})
		pro_ids.append(ids[0])
		crm_lead_vals = {
			'inquiry_no': pr_seq,
			'type_request': 'product_request_psd',
			'state': 'open',
			'partner_id': partner_id,
			'created_by_global': rec.created_by.name,
			'inspection_date':	rec.request_date,
			'product_request_id': ids[0],										
		}
		crm_lead_obj.create(cr, uid, crm_lead_vals, context=context)
		return pro_ids

	def different_addresses_same_office(self,cr,uid,ids,context=None):
		partner_obj = self.pool.get('res.partner')
		partner_addrs_obj = self.pool.get('res.partner.address')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		prod_req_line_obj = self.pool.get('product.request.line')
		customer_line_obj = self.pool.get('customer.line')
		crm_lead_obj = self.pool.get('crm.lead')
		phone_child_obj = self.pool.get('phone.number.child')
		phone_m2m_obj = self.pool.get('phone.m2m')
		offices = []
		locations = []
		offices = context.get('offices')
		locations = context.get('locations')
		phone_child_id = False
		phone_m2m_id = False
		pro_ids = []
		rec = self.browse(cr,uid,ids[0])
		for each in locations:
			partner_addrs_data = partner_addrs_obj.browse(cr, uid, each)
			if partner_addrs_data.phone_m2m_xx:
				phone_child_id = phone_child_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('number','=',partner_addrs_data.phone_m2m_xx.name)], context=context)
				if phone_child_id:
					phone_child_id = phone_child_id[0]
				else:
					phone_child_id = phone_child_obj.create(cr, uid, {
							'partner_id': rec.partner_id.id,
							'contact_select': partner_addrs_data.phone_m2m_xx.type,
							'number': partner_addrs_data.phone_m2m_xx.name
						}, context=context)
			else:
				if rec.phone_many2one:
					phone_child_id = rec.phone_many2one.id
			pro_req_vals = {
				'name': rec.name,
				'title': partner_addrs_data.title,
				'first_name': partner_addrs_data.first_name,
				'middle_name': partner_addrs_data.middle_name, 
				'last_name': partner_addrs_data.last_name, 
				'designation': partner_addrs_data.designation, 
				'premise_type': partner_addrs_data.premise_type, 
				'building': partner_addrs_data.building, 
				'location_name': partner_addrs_data.location_name, 
				'apartment': partner_addrs_data.apartment,
				'sub_area': partner_addrs_data.sub_area,
				'street': partner_addrs_data.street,
				'landmark': partner_addrs_data.landmark,
				'tehsil': partner_addrs_data.tehsil and partner_addrs_data.tehsil.id,
				'state_id': partner_addrs_data.state_id and partner_addrs_data.state_id.id,
				'city_id': partner_addrs_data.city_id and partner_addrs_data.city_id.id,
				'district': partner_addrs_data.district and partner_addrs_data.district.id,
				'zip': partner_addrs_data.zip,
				'email': partner_addrs_data.email,
				'fax': partner_addrs_data.fax,
				'phone_many2one': phone_child_id,
				'ref_by': rec.ref_by and rec.ref_by.id,
				'inquiry_type': 'product',
				'call_type': rec.call_type,
				'state': 'open',
				'confirm_check': True,
				'request_date': datetime.now(),
				'created_by': rec.created_by.id,
				'customer_type': 'existing',
				'segment': rec.segment,
				'hide_search': True,
				'hide_ref': True,
				'hide_segment': True,
				'parent_request': ids[0]
			}
			pro_id = self.create(cr, uid, pro_req_vals, context=context)
			prod_req_loc_ids = prod_req_loc_obj.search(cr, uid, [('address_id','=',each),('location_request_id','=',ids[0])], context=context)
			for prod_req_loc_id in prod_req_loc_ids:
				prod_req_loc_data = prod_req_loc_obj.browse(cr, uid, prod_req_loc_id)
				prod_req_loc_obj.create(cr, uid, {
						'address': prod_req_loc_data.address,
						'address_id': prod_req_loc_data.address_id,
						# 'product_generic_id': prod_req_loc_data.product_name and prod_req_loc_data.product_name.id,
						# 'sku_name_id': prod_req_loc_data.product_name and prod_req_loc_data.product_name.id,
						'product_name': prod_req_loc_data.product_name and prod_req_loc_data.product_name.id,
						'available_quantity':prod_req_loc_data.available_quantity,
						'product_uom_id': prod_req_loc_data.product_uom_id and prod_req_loc_data.product_uom_id.id,
						'branch_id': prod_req_loc_data.branch_id and  prod_req_loc_data.branch_id.id,
						'quantity': prod_req_loc_data.quantity,
						'remarks': prod_req_loc_data.remarks,
						'exempted':prod_req_loc_data.exempted,
						'location_request_id': pro_id,
				}, context=context)
			pro_ids.append(pro_id)
		partner_id = partner_obj.search(cr, uid, [('ou_id','=',rec.customer_id),('company_id','=',offices[0])], context=context)
		if not partner_id:
			customer_inc_no = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
		if partner_id:
			cust_prefix = False
			customer_seq = partner_obj.browse(cr, uid, partner_id[0]).ou_id
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
			partner_id = partner_id[0]
			partner_obj.write(cr, uid, partner_id, {'segment': rec.segment}, context=context)
		else:
			primary_address_ids = partner_addrs_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('primary_contact','=',True)], context=context)
			if primary_address_ids:
				primary_address_id = primary_address_ids[0]
				partner_addrs_data = partner_addrs_obj.browse(cr, uid, primary_address_id)
			else:
				primary_address_id = locations[0]
				partner_addrs_data = partner_addrs_obj.browse(cr, uid, primary_address_id)
			cust_prefix = '0000'
			customer_seq = cust_prefix+customer_inc_no
			if partner_addrs_data.phone_m2m_xx:
				phone_child_id = phone_child_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('number','=',partner_addrs_data.phone_m2m_xx.name)], context=context)
				if phone_child_id:
					phone_child_id = phone_child_id[0]
				else:
					phone_child_id = phone_child_obj.create(cr, uid, {
							'partner_id': rec.partner_id.id,
							'contact_select': partner_addrs_data.phone_m2m_xx.type,
							'number': partner_addrs_data.phone_m2m_xx.name
						}, context=context)
			else:
				if rec.phone_many2one:
					phone_child_id = rec.phone_many2one.id
			partner_vals={
				'name': rec.name,
				'first_name': partner_addrs_data.first_name,
				'last_name': partner_addrs_data.last_name,
				'middle_name': partner_addrs_data.middle_name,
				'designation': partner_addrs_data.designation,
				'premise_type': partner_addrs_data.premise_type,
				'location_name': partner_addrs_data.location_name,
				'apartment': partner_addrs_data.apartment,
				'building': partner_addrs_data.building,
				'sub_area': partner_addrs_data.sub_area,
				'street': partner_addrs_data.street,
				'landmark': partner_addrs_data.landmark,
				'city_id': partner_addrs_data.city_id.id or False,
				'district': partner_addrs_data.district.id or False,
				'tehsil': partner_addrs_data.tehsil.id or False,
				'state_id': partner_addrs_data.state_id.id or False,
				'zip': partner_addrs_data.zip,
				'fax': partner_addrs_data.fax,
				'email': partner_addrs_data.email,
				'segment': rec.segment,
				'phone_many2one': phone_child_id,
				'ref_by': rec.ref_by and rec.ref_by.id,
				'customer': True,
				'ou_id': customer_seq,
				'customer_id_main': customer_seq,
				'customer_since': datetime.now(),
				'company_id': offices[0],
				'psd': True
			}
			if partner_addrs_data.middle_name and partner_addrs_data.last_name:
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+' '+partner_addrs_data.last_name
			if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
				contact_name = partner_addrs_data.first_name
			if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
			if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
				contact_name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
			partner_vals.update({'contact_name':contact_name})
			partner_id = partner_obj.create(cr, uid, partner_vals, context=context)	
			if partner_addrs_data.phone_m2m_xx:
				phone_m2m_id = partner_addrs_data.phone_m2m_xx.id
			else:
				if rec.phone_many2one:
					phone_m2m_id = phone_m2m_obj.create(cr, uid, {
										'res_location_id': partner_addrs_data.id,
										'name': rec.phone_many2one.number,
										'type': rec.phone_many2one_new.contact_select
									}, context=context)
			address_vals = {
				'first_name': partner_addrs_data.first_name,
				'last_name': partner_addrs_data.last_name,
				'middle_name': partner_addrs_data.middle_name,
				'designation': partner_addrs_data.designation,
				'premise_type': partner_addrs_data.premise_type,
				'location_name': partner_addrs_data.location_name,
				'apartment': partner_addrs_data.apartment,
				'building': partner_addrs_data.building,
				'sub_area': partner_addrs_data.sub_area,
				'street': partner_addrs_data.street,
				'landmark': partner_addrs_data.landmark,
				'city_id': partner_addrs_data.city_id.id or False,
				'district': partner_addrs_data.district.id or False,
				'tehsil': partner_addrs_data.tehsil.id or False,
				'state_id': partner_addrs_data.state_id.id or False,
				'zip': partner_addrs_data.zip,
				'fax': partner_addrs_data.fax,
				'email': partner_addrs_data.email,
				'phone_m2m_xx': phone_m2m_id,
				'segment': rec.segment,
				'ref_by': partner_addrs_data.ref_by.id or False,
				'exempted': partner_addrs_data.exempted,
				'exempted_classification': partner_addrs_data.exempted_classification.id,
				'certificate_no': partner_addrs_data.certificate_no,
				'exem_attachment': partner_addrs_data.exem_attachment,
				'adhoc_job': partner_addrs_data.adhoc_job,
				'partner_id': partner_id,
				'company_id': offices[0],
				'primary_contact': True
			}
			if partner_addrs_data.middle_name and partner_addrs_data.last_name:
				name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+' '+partner_addrs_data.last_name
			if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
				name = partner_addrs_data.first_name
			if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
				name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
			if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
				name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
			address_vals.update({'name': name})	
			address_id = partner_addrs_obj.create(cr, uid, address_vals, context=context)
			loc_prefix = '0000'
			loc_inc_no = 1
			if loc_inc_no >= 0 and loc_inc_no <= 9:
				st_loc_inc_no = '0'+str(loc_inc_no)
			elif loc_inc_no >= 10 and loc_inc_no <= 99:
				st_loc_inc_no = str(loc_inc_no)
			location_id = loc_prefix+customer_inc_no+st_loc_inc_no
			cust_line_vals = {
				'location_id': location_id,
				'premise_type_import': partner_addrs_data.premise_type,
				'branch': each,
				'customer_address': address_id,
				'partner_id': partner_id,
				'phone_many2one': phone_m2m_id
			}
			cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)
			for each in locations:
				if each != primary_address_id:
					loc_inc_no = loc_inc_no + 1
					partner_addrs_data = partner_addrs_obj.browse(cr, uid, each)
					if partner_addrs_data.phone_m2m_xx:
						phone_m2m_id = partner_addrs_data.phone_m2m_xx.id
					else:
						if rec.phone_many2one:
							phone_m2m_id = phone_m2m_obj.create(cr, uid, {
												'res_location_id': partner_addrs_data.id,
												'name': rec.phone_many2one.number,
												'type': rec.phone_many2one_new.contact_select
											}, context=context)
					address_vals = {
						'first_name': partner_addrs_data.first_name,
						'last_name': partner_addrs_data.last_name,
						'middle_name': partner_addrs_data.middle_name,
						'designation': partner_addrs_data.designation,
						'premise_type': partner_addrs_data.premise_type,
						'location_name': partner_addrs_data.location_name,
						'apartment': partner_addrs_data.apartment,
						'building': partner_addrs_data.building,
						'sub_area': partner_addrs_data.sub_area,
						'street': partner_addrs_data.street,
						'landmark': partner_addrs_data.landmark,
						'city_id': partner_addrs_data.city_id.id or False,
						'district': partner_addrs_data.district.id or False,
						'tehsil': partner_addrs_data.tehsil.id or False,
						'state_id': partner_addrs_data.state_id.id or False,
						'zip': partner_addrs_data.zip,
						'fax': partner_addrs_data.fax,
						'email': partner_addrs_data.email,
						'phone_m2m_xx': phone_m2m_id,
						'segment': rec.segment,
						'ref_by': partner_addrs_data.ref_by.id or False,
						'exempted': partner_addrs_data.exempted,
						'exempted_classification': partner_addrs_data.exempted_classification.id,
						'certificate_no': partner_addrs_data.certificate_no,
						'exem_attachment': partner_addrs_data.exem_attachment,
						'adhoc_job': partner_addrs_data.adhoc_job,
						'partner_id': partner_id,
						'company_id': offices[0]
					}
					if partner_addrs_data.middle_name and partner_addrs_data.last_name:
						name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name+' '+partner_addrs_data.last_name
					if not partner_addrs_data.middle_name and not partner_addrs_data.last_name:
						name = partner_addrs_data.first_name
					if partner_addrs_data.middle_name and not partner_addrs_data.last_name:	
						name = partner_addrs_data.first_name+' '+partner_addrs_data.middle_name
					if not partner_addrs_data.middle_name and partner_addrs_data.last_name:	
						name = partner_addrs_data.first_name+' '+partner_addrs_data.last_name
					address_vals.update({'name': name})	
					address_id = partner_addrs_obj.create(cr, uid, address_vals, context=context)
					loc_prefix = '0000'
					if loc_inc_no >= 0 and loc_inc_no <= 9:
						st_loc_inc_no = '0'+str(loc_inc_no)
					elif loc_inc_no >= 10 and loc_inc_no <= 99:
						st_loc_inc_no = str(loc_inc_no)
					location_id = loc_prefix+customer_inc_no+st_loc_inc_no
					cust_line_vals = {
						'location_id': location_id,
						'premise_type_import': partner_addrs_data.premise_type,
						'branch': each,
						'customer_address': address_id,
						'partner_id': partner_id,
						'phone_many2one': phone_m2m_id
					}
					cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)
		for pro_id in pro_ids:
			pro_data = self.browse(cr,uid,pro_id)
			if pro_data.company_id.establishment_type == 'crm':
				location_branch = 'crm'
			elif pro_data.location_request_line[0].branch_id.id == pro_data.company_id.id:
				location_branch = 'same'
			else:
				location_branch = 'different'
			req_ids = crm_lead_obj.search(cr, uid, [('partner_id','=',partner_id)], context=context)	
			pr_inc_no = len(req_ids)+1
			if pr_inc_no >= 0 and pr_inc_no <= 9:
				st_pr_inc_no = '00'+str(pr_inc_no)
			elif pr_inc_no >= 10 and pr_inc_no <= 99:
				st_pr_inc_no = '0'+str(pr_inc_no)
			elif pr_inc_no >= 100 and pr_inc_no <= 999:	
				st_pr_inc_no = str(pr_inc_no)			
			pr_code	= 'PR'
			if pro_data.location_request_line[0].branch_id.id != pro_data.company_id.id:
				pr_code = 'PRO'
			pr_seq = rec.company_id.pcof_key + pr_code + customer_inc_no + st_pr_inc_no
			self.write(cr, uid, pro_id, 
				{
					'product_request_id': pr_seq,
					'customer_id': customer_seq, 
					'partner_id': partner_id,
					'location_branch': location_branch
				}, context=context)
			pro_loc_ids = prod_req_loc_obj.search(cr, uid, [('location_request_id','=',pro_id)], context=context)
			for pro_loc_id in pro_loc_ids:
				prod_req_loc_obj.write(cr, uid, pro_loc_id, {'product_request_ref':pr_seq}, context=context)
			crm_data = self.browse(cr, uid, pro_id)
			crm_lead_vals = {
				'inquiry_no': crm_data.product_request_id,
				'type_request': 'product_request_psd',
				'state': 'open',
				'partner_id': crm_data.partner_id.id,
				'created_by_global': crm_data.created_by.name,
				'inspection_date':	crm_data.request_date,
				'product_request_id': pro_id,										
			}
			crm_lead_obj.create(cr, uid, crm_lead_vals, context=context)
		self.write(cr, uid, ids[0], {'active': False}, context=context)
		return pro_ids

	def different_addresses_different_offices(self,cr,uid,ids,context=None):
		partner_obj = self.pool.get('res.partner')
		partner_addrs_obj = self.pool.get('res.partner.address')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		prod_req_line_obj = self.pool.get('product.request.line')
		customer_line_obj = self.pool.get('customer.line')
		crm_lead_obj = self.pool.get('crm.lead')
		phone_child_obj = self.pool.get('phone.number.child')
		phone_m2m_obj = self.pool.get('phone.m2m')
		off_locs = {}
		offices = context.get('offices')
		phone_child_id = False
		phone_m2m_id = False
		pro_ids = []
		rec = self.browse(cr,uid,ids[0])
		customer_inc_no_new = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
		for office in offices:
			locations = []
			prod_req_ids = prod_req_loc_obj.search(cr, uid, [('location_request_id','=',ids[0]),('branch_id','=',office)], context=context)
			for prod_req_id in prod_req_ids:
				prod_req_data = prod_req_loc_obj.browse(cr, uid, prod_req_id)
				locations.append(prod_req_data.address_id)
				locations = list(set(locations))
				off_locs.update({office:locations})
		for off_loc in off_locs:
			primary_address_id = False
			locs = off_locs.get(off_loc)	
			set_locs = set(locs)
			locs = list(set_locs)
			for loc in locs:
				if partner_addrs_obj.browse(cr, uid, loc).primary_contact == True:
					primary_address_id = partner_addrs_obj.browse(cr, uid, loc).id
			if not primary_address_id:
				primary_address_id = locs[0]
			primary_addrs_data = partner_addrs_obj.browse(cr, uid, primary_address_id)

			partner_id = partner_obj.search(cr, uid, [('ou_id','=',rec.customer_id),('company_id','=',off_loc)], context=context)
			if partner_id:
				partner_obj.write(cr, uid, partner_id[0], {'segment': rec.segment}, context=context)
				cust_prefix = False
				customer_seq = partner_obj.browse(cr, uid, partner_id[0]).ou_id
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
					partner_id = partner_id[0]
			else:
				cust_prefix = '0000'
				customer_inc_no = customer_inc_no_new
				customer_seq = cust_prefix+customer_inc_no
				if primary_addrs_data.phone_m2m_xx:
					phone_child_id = phone_child_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('number','=',primary_addrs_data.phone_m2m_xx.name)], context=context)
					if phone_child_id:
						phone_child_id = phone_child_id[0]
					else:
						phone_child_id = phone_child_obj.create(cr, uid, {
								'partner_id': rec.partner_id.id,
								'contact_select': primary_addrs_data.phone_m2m_xx.type,
								'number': primary_addrs_data.phone_m2m_xx.name
							}, context=context)
				else:
					if rec.phone_many2one:
						phone_child_id = rec.phone_many2one.id
				partner_vals={
					'name': rec.name,
					'first_name': primary_addrs_data.first_name,
					'last_name': primary_addrs_data.last_name,
					'middle_name': primary_addrs_data.middle_name,
					'designation': primary_addrs_data.designation,
					'premise_type': primary_addrs_data.premise_type,
					'location_name': primary_addrs_data.location_name,
					'apartment': primary_addrs_data.apartment,
					'building': primary_addrs_data.building,
					'sub_area': primary_addrs_data.sub_area,
					'street': primary_addrs_data.street,
					'landmark': primary_addrs_data.landmark,
					'city_id': primary_addrs_data.city_id.id or False,
					'district': primary_addrs_data.district.id or False,
					'tehsil': primary_addrs_data.tehsil.id or False,
					'state_id': primary_addrs_data.state_id.id or False,
					'zip': primary_addrs_data.zip,
					'fax': primary_addrs_data.fax,
					'email': primary_addrs_data.email,
					'segment': rec.segment,
					'phone_many2one': phone_child_id,
					'ref_by': rec.ref_by and rec.ref_by.id,
					'customer': True,
					'ou_id': customer_seq,
					'customer_id_main': customer_seq,
					'customer_since': datetime.now(),
					'company_id': off_loc,
					'psd': True
				}
				if primary_addrs_data.middle_name and primary_addrs_data.last_name:
					contact_name = primary_addrs_data.first_name+' '+primary_addrs_data.middle_name+' '+primary_addrs_data.last_name
				if not primary_addrs_data.middle_name and not primary_addrs_data.last_name:
					contact_name = primary_addrs_data.first_name
				if primary_addrs_data.middle_name and not primary_addrs_data.last_name:	
					contact_name = primary_addrs_data.first_name+' '+primary_addrs_data.middle_name
				if not primary_addrs_data.middle_name and primary_addrs_data.last_name:	
					contact_name = primary_addrs_data.first_name+' '+primary_addrs_data.last_name
				partner_vals.update({'contact_name':contact_name})
				partner_id = partner_obj.create(cr, uid, partner_vals, context=context)
				address_vals = {
					'first_name': primary_addrs_data.first_name,
					'last_name': primary_addrs_data.last_name,
					'middle_name': primary_addrs_data.middle_name,
					'designation': primary_addrs_data.designation,
					'premise_type': primary_addrs_data.premise_type,
					'location_name': primary_addrs_data.location_name,
					'apartment': primary_addrs_data.apartment,
					'building': primary_addrs_data.building,
					'sub_area': primary_addrs_data.sub_area,
					'street': primary_addrs_data.street,
					'landmark': primary_addrs_data.landmark,
					'city_id': primary_addrs_data.city_id.id or False,
					'district': primary_addrs_data.district.id or False,
					'tehsil': primary_addrs_data.tehsil.id or False,
					'state_id': primary_addrs_data.state_id.id or False,
					'zip': primary_addrs_data.zip,
					'fax': primary_addrs_data.fax,
					'email': primary_addrs_data.email,
					'phone_m2m_xx': phone_m2m_id,
					'segment': rec.segment,
					'ref_by': primary_addrs_data.ref_by.id or False,
					'exempted': primary_addrs_data.exempted,
					'exempted_classification': primary_addrs_data.exempted_classification.id,
					'certificate_no': primary_addrs_data.certificate_no,
					'exem_attachment': primary_addrs_data.exem_attachment,
					'adhoc_job': primary_addrs_data.adhoc_job,
					'partner_id': partner_id,
					'company_id': off_loc,
					'primary_contact': True
				}
				if primary_addrs_data.middle_name and primary_addrs_data.last_name:
					name = primary_addrs_data.first_name+' '+primary_addrs_data.middle_name+' '+primary_addrs_data.last_name
				if not primary_addrs_data.middle_name and not primary_addrs_data.last_name:
					name = primary_addrs_data.first_name
				if primary_addrs_data.middle_name and not primary_addrs_data.last_name:	
					name = primary_addrs_data.first_name+' '+primary_addrs_data.middle_name
				if not primary_addrs_data.middle_name and primary_addrs_data.last_name:	
					name = primary_addrs_data.first_name+' '+primary_addrs_data.last_name
				address_vals.update({'name': name})	
				address_id = partner_addrs_obj.create(cr, uid, address_vals, context=context)
				loc_prefix = '0000'
				loc_inc_no = 1
				if loc_inc_no >= 0 and loc_inc_no <= 9:
					st_loc_inc_no = '0'+str(loc_inc_no)
				elif loc_inc_no >= 10 and loc_inc_no <= 99:
					st_loc_inc_no = str(loc_inc_no)
				location_id = loc_prefix+customer_inc_no+st_loc_inc_no
				cust_line_vals = {
					'location_id': location_id,
					'premise_type_import': primary_addrs_data.premise_type,
					'branch': off_loc,
					'customer_address': address_id,
					'partner_id': partner_id,
					'phone_many2one': phone_m2m_id
				}
				cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)
				for loc in locs:
					if loc != primary_address_id:
						loc_inc_no = loc_inc_no + 1
						partner_addrs_data2 = partner_addrs_obj.browse(cr, uid, loc)
						if partner_addrs_data2.phone_m2m_xx:
							phone_m2m_id = partner_addrs_data2.phone_m2m_xx.id
						else:
							if rec.phone_many2one:
								phone_m2m_id = phone_m2m_obj.create(cr, uid, {
													'res_location_id': partner_addrs_data2.id,
													'name': rec.phone_many2one.number,
													'type': rec.phone_many2one_new.contact_select
												}, context=context)
						address_vals = {
							'first_name': partner_addrs_data2.first_name,
							'last_name': partner_addrs_data2.last_name,
							'middle_name': partner_addrs_data2.middle_name,
							'designation': partner_addrs_data2.designation,
							'premise_type': partner_addrs_data2.premise_type,
							'location_name': partner_addrs_data2.location_name,
							'apartment': partner_addrs_data2.apartment,
							'building': partner_addrs_data2.building,
							'sub_area': partner_addrs_data2.sub_area,
							'street': partner_addrs_data2.street,
							'landmark': partner_addrs_data2.landmark,
							'city_id': partner_addrs_data2.city_id.id or False,
							'district': partner_addrs_data2.district.id or False,
							'tehsil': partner_addrs_data2.tehsil.id or False,
							'state_id': partner_addrs_data2.state_id.id or False,
							'zip': partner_addrs_data2.zip,
							'fax': partner_addrs_data2.fax,
							'email': partner_addrs_data2.email,
							'phone_m2m_xx': phone_m2m_id,
							'segment': rec.segment,
							'ref_by': partner_addrs_data2.ref_by.id or False,
							'exempted': partner_addrs_data2.exempted,
							'exempted_classification': partner_addrs_data2.exempted_classification.id,
							'certificate_no': partner_addrs_data2.certificate_no,
							'exem_attachment': partner_addrs_data2.exem_attachment,
							'adhoc_job': partner_addrs_data2.adhoc_job,
							'partner_id': partner_id,
							'company_id': off_loc,
						}
						if partner_addrs_data2.middle_name and partner_addrs_data2.last_name:
							name = partner_addrs_data2.first_name+' '+partner_addrs_data2.middle_name+' '+partner_addrs_data2.last_name
						if not partner_addrs_data2.middle_name and not partner_addrs_data2.last_name:
							name = partner_addrs_data2.first_name
						if partner_addrs_data2.middle_name and not partner_addrs_data2.last_name:	
							name = partner_addrs_data2.first_name+' '+partner_addrs_data2.middle_name
						if not partner_addrs_data2.middle_name and partner_addrs_data2.last_name:	
							name = partner_addrs_data2.first_name+' '+partner_addrs_data2.last_name
						address_vals.update({'name': name})	
						address_id = partner_addrs_obj.create(cr, uid, address_vals, context=context)
						loc_prefix = '0000'
						if loc_inc_no >= 0 and loc_inc_no <= 9:
							st_loc_inc_no = '0'+str(loc_inc_no)
						elif loc_inc_no >= 10 and loc_inc_no <= 99:
							st_loc_inc_no = str(loc_inc_no)
						location_id = loc_prefix+customer_inc_no+st_loc_inc_no
						cust_line_vals = {
							'location_id': location_id,
							'premise_type_import': partner_addrs_data2.premise_type,
							'branch': off_loc,
							'customer_address': address_id,
							'partner_id': partner_id,
							'phone_many2one': phone_m2m_id
						}
						cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)
			temp_pr_inc_no = 0			
			for loc in locs:
				partner_addrs_data = partner_addrs_obj.browse(cr, uid, loc)	
				if partner_addrs_data.phone_m2m_xx:
					phone_child_id = phone_child_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('number','=',partner_addrs_data.phone_m2m_xx.name)], context=context)
					if phone_child_id:
						phone_child_id = phone_child_id[0]
					else:
						phone_child_id = phone_child_obj.create(cr, uid, {
								'partner_id': rec.partner_id.id,
								'contact_select': partner_addrs_data.phone_m2m_xx.type,
								'number': partner_addrs_data.phone_m2m_xx.name
							}, context=context)
				else:
					if rec.phone_many2one:
						phone_child_id = rec.phone_many2one.id
				pro_req_vals = {
					'name': rec.name,
					'title': partner_addrs_data.title,
					'first_name': partner_addrs_data.first_name,
					'middle_name': partner_addrs_data.middle_name, 
					'last_name': partner_addrs_data.last_name, 
					'designation': partner_addrs_data.designation, 
					'premise_type': partner_addrs_data.premise_type, 
					'building': partner_addrs_data.building, 
					'location_name': partner_addrs_data.location_name, 
					'apartment': partner_addrs_data.apartment,
					'building': partner_addrs_data.building,
					'sub_area': partner_addrs_data.sub_area,
					'street': partner_addrs_data.street,
					'landmark': partner_addrs_data.landmark,
					'tehsil': partner_addrs_data.tehsil and partner_addrs_data.tehsil.id,
					'state_id': partner_addrs_data.state_id and partner_addrs_data.state_id.id,
					'city_id': partner_addrs_data.city_id and partner_addrs_data.city_id.id,
					'district': partner_addrs_data.district and partner_addrs_data.district.id,
					'zip': partner_addrs_data.zip,
					'email': partner_addrs_data.email,
					'fax': partner_addrs_data.fax,
					'phone_many2one': phone_child_id,
					'ref_by': rec.ref_by and rec.ref_by.id,
					'inquiry_type': 'product',
					'call_type': rec.call_type,
					'state': 'open',
					'confirm_check': True,
					'request_date': datetime.now(),
					'created_by': rec.created_by.id,
					'customer_type': 'existing',
					'segment': rec.segment,
					'hide_search': True,
					'hide_ref': True,
					'hide_segment': True,
					'parent_request': ids[0]
				}
				pro_id = self.create(cr, uid, pro_req_vals, context=context)
				prod_req_loc_ids = prod_req_loc_obj.search(cr, uid, [('address_id','=',loc),('location_request_id','=',rec.id),('branch_id','=',off_loc)], context=context)
				for prod_req_loc_id in prod_req_loc_ids:
					prod_req_loc_data = prod_req_loc_obj.browse(cr, uid, prod_req_loc_id)
					prod_req_loc_obj.create(cr, uid, {
							'address': prod_req_loc_data.address,
							'address_id': prod_req_loc_data.address_id,
							'product_generic_id': prod_req_loc_data.product_generic_id and prod_req_loc_data.product_generic_id.id,
							'sku_name_id': prod_req_loc_data.sku_name_id and prod_req_loc_data.sku_name_id.id,
							'product_uom_id': prod_req_loc_data.product_uom_id and prod_req_loc_data.product_uom_id.id,
							'branch_id': off_loc,
							'quantity': prod_req_loc_data.quantity,
							'remarks': prod_req_loc_data.remarks,
							'exempted':prod_req_loc_data.exempted,
							'location_request_id': pro_id,
						}, context=context)
				pro_ids.append(pro_id)
				req_ids = crm_lead_obj.search(cr, uid, [('partner_id','=',partner_id)], context=context)	
				pr_inc_no = temp_pr_inc_no+len(req_ids)+1
				if pr_inc_no >= 0 and pr_inc_no <= 9:
					st_pr_inc_no = '00'+str(pr_inc_no)
				elif pr_inc_no >= 10 and pr_inc_no <= 99:
					st_pr_inc_no = '0'+str(pr_inc_no)
				elif pr_inc_no >= 100 and pr_inc_no <= 999:	
					st_pr_inc_no = str(pr_inc_no)
				pr_code = 'PR'
				if off_loc != rec.company_id.id:
					pr_code = 'PRO'
				pr_seq = rec.company_id.pcof_key + pr_code + customer_inc_no + st_pr_inc_no			
				self.write(cr, uid, pro_id, {'customer_id': customer_seq, 'partner_id': partner_id,'product_request_id':pr_seq}, context=context)	
				temp_pr_inc_no = temp_pr_inc_no + 1
		for	pro_id in pro_ids:
			pro_data = self.browse(cr,uid,pro_id)
			if pro_data.company_id.establishment_type == 'crm':
				location_branch = 'crm'
			elif pro_data.location_request_line[0].branch_id.id == pro_data.company_id.id:
				location_branch = 'same'
			else:
				location_branch = 'different'
			self.write(cr, uid, pro_id, {'location_branch': location_branch}, context=context)	
			pro_loc_ids = prod_req_loc_obj.search(cr, uid, [('location_request_id','=',pro_id)], context=context)
			for pro_loc_id in pro_loc_ids:
				prod_req_loc_obj.write(cr, uid, pro_loc_id, {'product_request_ref':pro_data.product_request_id}, context=context)	
			crm_data = self.browse(cr, uid, pro_id)
			crm_lead_vals = {
				'inquiry_no': crm_data.product_request_id,
				'type_request': 'product_request_psd',
				'state': 'open',
				'partner_id': crm_data.partner_id.id,
				'created_by_global': crm_data.created_by.name,
				'inspection_date':	crm_data.request_date,
				'product_request_id': pro_id,										
			}
			crm_lead_obj.create(cr, uid, crm_lead_vals, context=context)
		self.write(cr, uid, ids[0], {'active': False}, context=context)	
		return pro_ids

	def process_existing_customer_request(self,cr,uid,ids,context=None):
		partner_obj = self.pool.get('res.partner')
		partner_addrs_obj = self.pool.get('res.partner.address')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		prod_req_line_obj = self.pool.get('product.request.line')
		customer_line_obj = self.pool.get('customer.line')
		global_search_obj = self.pool.get('ccc.branch')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		phone_child_obj = self.pool.get('phone.number.child')
		phone_m2m_obj = self.pool.get('phone.m2m')
		models_data=self.pool.get('ir.model.data')
		offices = []
		locations = []
		products = []
		pro_ids = []
		rec = self.browse(cr,uid,ids[0])
		location_request_line = rec.location_request_line
		if len(location_request_line) == 1:
			office = location_request_line[0].branch_id.id
			location = location_request_line[0].address_id
			context.update({'office':office,'location':location})
			pro_ids = self.process_single_address_line(cr, uid, ids, context=context)
			product_request_data = self.browse(cr, uid, pro_ids[0])
			global_search_id=global_search_obj.create(cr,uid,{'enquiry_type': 'product_request'},context=context)
			date_age = global_search_obj.calculate_date_age(cr,uid,ids,product_request_data.request_date,product_request_data.closed_date)
			branch_line_vals =  {       
					'ccc_product_id': global_search_id,
					'request_id': product_request_data.product_request_id,
					'customer_name': product_request_data.name,
					'branch_id': office,
					'origin': product_request_data.company_id.name,
					'request_type_psd': 'product_request',
					'date_age': date_age,
					'state': product_request_data.state,
					'contact_number': product_request_data.phone_many2one and product_request_data.phone_many2one.number,
					'sort_date': product_request_data.request_date,
					'created_by': product_request_data.created_by.id,
					'employee_id': product_request_data.employee_id.id,
					'product_request_id': product_request_data.id
			}
			branch_re_id = branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
			branch_line_id = office
			context.update({'branch':branch_line_id})
			self.sync_product_request(cr,uid,ids,context=context)
			# context.update({'hide_create_quotation':True})
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
			   'context':context
			}
		else:
			for each in location_request_line:
				office = each.branch_id.id
				offices.append(office)
				location = each.address_id
				locations.append(location)
				product = each.product_name.id
				products.append(product)
			if len(set(offices))!=1 and len(set(locations))==1:
				offices=list(set(offices))
				locations=list(set(locations))
				context.update({'offices':offices,'locations':locations})
				pro_ids = self.same_address_different_offices(cr, uid, ids, context=context)
				global_search_id=global_search_obj.create(cr,uid,{'enquiry_type': 'product_request'},context=context)	
				for each in pro_ids:
					product_req_data = self.browse(cr, uid, each)
					date_age = global_search_obj.calculate_date_age(cr,uid,ids,product_req_data.request_date,product_req_data.closed_date)
					branch_line_vals =  {       
							'ccc_product_id': global_search_id,
							'request_id': product_req_data.product_request_id,
							'customer_name': product_req_data.name,
							'branch_id': product_req_data.location_request_line[0].branch_id.id,
							'origin': product_req_data.company_id.name,
							'request_type_psd': 'product_request',
							'date_age': date_age,
							'state': product_req_data.state,
							'contact_number': product_req_data.phone_many2one and product_req_data.phone_many2one.number,
							'sort_date': product_req_data.request_date,
							'created_by': product_req_data.created_by.id,
							'employee_id': product_req_data.employee_id.id,
							'product_request_id': product_req_data.id
					}
					branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
					branch_line_id = product_req_data.location_request_line[0].branch_id.id
					context.update({'branch':branch_line_id})
					self.sync_product_request(cr,uid,[each],context=context)
				# context.update({'hide_create_quotation':True})
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
				   'context':context
				}
			elif len(set(offices))==1 and len(set(locations))==1:
				offices=list(set(offices))
				locations=list(set(locations))
				products=list(set(products))
				context.update({'offices':offices,'locations':locations,'products':products})
				pro_ids = self.same_address_same_office(cr, uid, ids, context=context)
				product_request_data = self.browse(cr, uid, pro_ids[0])
				date_age = global_search_obj.calculate_date_age(cr,uid,ids,product_request_data.request_date,product_request_data.closed_date)
				global_search_id=global_search_obj.create(cr,uid,{'enquiry_type': 'product_request'},context=context)	
				branch_line_vals =  {       
						'ccc_product_id': global_search_id,
						'request_id': product_request_data.product_request_id,
						'customer_name': product_request_data.name,
						'branch_id': offices[0],
						'origin': product_request_data.company_id.name,
						'request_type_psd': 'product_request',
						'date_age': date_age,
						'state': product_request_data.state,
						'contact_number': product_request_data.phone_many2one and product_request_data.phone_many2one.number,
						'sort_date': product_request_data.request_date,
						'created_by': product_request_data.created_by.id,
						'employee_id': product_request_data.employee_id.id,
						'product_request_id': product_request_data.id
				}
				branch_re_id = branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
				branch_line_id = offices
				context.update({'branch':branch_line_id})
				self.sync_product_request(cr,uid,ids,context=context)
				# context.update({'hide_create_quotation':True})
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
				   'context':context
				}
			elif len(set(offices))==1 and len(set(locations))!=1:
				offices=list(set(offices))
				locations=list(set(locations))
				context.update({'offices':offices,'locations':locations})
				pro_ids = self.different_addresses_same_office(cr, uid, ids, context=context)
				global_search_id=global_search_obj.create(cr,uid,{'enquiry_type': 'product_request'},context=context)	
				for each in pro_ids:
					product_req_data = self.browse(cr, uid, each)
					date_age = global_search_obj.calculate_date_age(cr,uid,ids,product_req_data.request_date,product_req_data.closed_date)
					branch_line_vals =  {       
							'ccc_product_id': global_search_id,
							'request_id': product_req_data.product_request_id,
							'customer_name': product_req_data.name,
							'branch_id': product_req_data.location_request_line[0].branch_id.id,
							'origin': product_req_data.company_id.name,
							'request_type_psd': 'product_request',
							'date_age': date_age,
							'state': product_req_data.state,
							'contact_number': product_req_data.phone_many2one and product_req_data.phone_many2one.number,
							'sort_date': product_req_data.request_date,
							'created_by': product_req_data.created_by.id,
							'employee_id': product_req_data.employee_id.id,
							'product_request_id': product_req_data.id
					}
					branch_re_id = branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
					branch_line_id = product_req_data.location_request_line[0].branch_id.id
					context.update({'branch':branch_line_id})
					self.sync_product_request(cr,uid,[each],context=context)
				# context.update({'hide_create_quotation':True})
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
				   'context':context
				}
			elif len(set(offices))!=1 and len(set(locations))!=1:
				offices=list(set(offices))
				context.update({'offices':offices})
				pro_ids = self.different_addresses_different_offices(cr, uid, ids, context=context)
				global_search_id = global_search_obj.create(cr,uid,{'enquiry_type': 'product_request'},context=context)	
				for each in pro_ids:
					product_req_data = self.browse(cr, uid, each)
					date_age = global_search_obj.calculate_date_age(cr,uid,ids,product_req_data.request_date,product_req_data.closed_date)
					branch_line_vals =  {       
							'ccc_product_id': global_search_id,
							'request_id': product_req_data.product_request_id,
							'customer_name': product_req_data.name,
							'branch_id': product_req_data.location_request_line[0].branch_id.id,
							'origin': product_req_data.company_id.name,
							'request_type_psd': 'product_request',
							'date_age': date_age,
							'state': product_req_data.state,
							'contact_number': product_req_data.phone_many2one and product_req_data.phone_many2one.number,
							'sort_date': product_req_data.request_date,
							'created_by': product_req_data.created_by.id,
							'employee_id': product_req_data.employee_id.id,
							'product_request_id': product_req_data.id
					}
					branch_re_id = branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
					branch_line_id = product_req_data.location_request_line[0].branch_id.id
					context.update({'branch':branch_line_id})
					self.sync_product_request(cr,uid,[each],context=context)
				# context.update({'hide_create_quotation':True})
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
				   'context':context
				}
product_request()