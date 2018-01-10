from osv import osv,fields
from datetime import datetime

class res_partner(osv.osv):
	_inherit = 'res.partner'

	_columns = {
		'psd': fields.boolean('PSD'),
		# 'request_type': fields.selection(
		# 					[('product_request','Product Request'),
		# 					('complaint_request','Product Complaint Request'),
		# 					('information_request','Product Information Request')],'New Request',select=1),
		'request_type': fields.selection(
							[('lead_request','Existing Customer Request'),
							('complaint_request','Complaint Request'),
							('renewal_request','Renewal Request'),
							('information_request','Miscellaneous Request'),
							('product_request','Product Request'),
							('product_complaint_request','Product Complaint Request'),
							('product_information_request','Product Information Request')],'New Request',select=1),
		'crm_history_ids': fields.one2many('crm.history','partner_id','Requests'),
		'segment': fields.selection([
						('retail','Retail Segment'),
						('distributor','Distributor Segment'),
						('institutional','Institutional/Govt Segment'),
						],'Segment'),
	}

	def name_get(self, cr, uid, ids, context=None):
		if context.get('from_request_search'):
			if not ids:
				return []
			if isinstance(ids, (int, long)):
				ids = [ids]
			reads = self.read(cr, uid, ids, ['name', 'ou_id'], context=context)
			res = []
			for record in reads:
				name = record['name']
				if record['ou_id']:
					name = record['ou_id']
				res.append((record['id'], name))
			return res
		if not context.get('from_request_search'):
			return super(res_partner, self).name_get(cr, uid, ids, context)

	def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
		if context.get('from_request_search'):
			if not args:
				args = []
			ids = []
			if name:
				ids = self.search(cr, uid, [('ou_id', '=like', "%"+name)] + args, limit=limit)
				if not ids:
					ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit)
			else:
				ids = self.search(cr, uid, args, context=context, limit=limit)      
			return self.name_get(cr, uid, ids, context=context) 
		if not context.get('from_request_search'):
			return super(res_partner, self).name_search(cr, uid, name=name, args=args, operator=operator, context=context, limit=limit)    

	def create_request(self,cr,uid,ids,context=None): 
		product_req_obj = self.pool.get('product.request')
		comp_req_obj = self.pool.get('product.complaint.request')
		comp_loc_obj = self.pool.get('product.complaint.locations')
		partner_address_obj = self.pool.get('res.partner.address')
		info_req_obj = self.pool.get('product.information.request')
		cust_source_obj = self.pool.get('customer.source') 
		rec = self.browse(cr, uid, ids[0])  
		request_type = rec.request_type
		ref_id = cust_source_obj.search(cr, uid, [('name','=','Existing/Old Customer')], context=context)
		if request_type == 'product_request':
			pro_req_vals = {
				'name': rec.name,
				'title': rec.title,
				'first_name': rec.first_name,
				'middle_name': rec.middle_name, 
				'last_name': rec.last_name, 
				'designation': rec.designation, 
				'premise_type': rec.premise_type, 
				'building': rec.building, 
				'location_name': rec.location_name, 
				'apartment': rec.apartment,
				'sub_area': rec.sub_area,
				'street': rec.street,
				'tehsil': rec.tehsil and rec.tehsil.id,
				'landmark': rec.landmark,
				'state_id': rec.state_id and rec.state_id.id,
				'city_id': rec.city_id and rec.city_id.id,
				'district': rec.district and  rec.district.id,
				'zip': rec.zip,
				'email': rec.email,
				'fax': rec.fax,
				'customer_id': rec.ou_id,
				'inquiry_type': 'product',
				'call_type':'inbound',
				'splitted': False,
				'state':'new',
				'confirm_check': True,
				'request_date': datetime.now(),
				'created_by': uid,
				'customer_type': 'existing',
				'partner_id': rec.id,
				'phone_many2one': rec.phone_many2one and rec.phone_many2one.id,
				'ref_by': ref_id[0],
				# 'segment': rec.segment,
				# 'hide_search': True,
				# 'hide_ref': True,
				# 'hide_segment': True,
			}
			product_req_id = product_req_obj.create(cr,uid,pro_req_vals,context=context)
			models_data = self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'psd_cid', 'view_product_request_form_crm')
			context.update({'product_req_id': product_req_id,'hide_create_quotation': True})
			return {
					'type': 'ir.actions.act_window',
					'name': 'Product Request', 
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'product.request',
					'res_id': product_req_id,
					'views': [(form_view and form_view[1] or False, 'form'),],
					'target': 'current',
					'context': context
				}
		elif request_type == 'product_complaint_request': 
			comp_req_vals = {
				'call_type': 'inbound',
				'requested_date': datetime.now(),
				'created_by': uid,
				'customer_type':'existing',
				'customer': rec.name,
				'customer_id': rec.ou_id,
				'state':'new',
				'partner_id': rec.id
			} 
			complaint_req_id = comp_req_obj.create(cr,uid,comp_req_vals,context=context)
			customer_lines = []
			addrs_items = []
			complete_address = ''
			cust_lines = rec.new_customer_location_service_line
			for cust_line in cust_lines:
				customer_lines.append(cust_line.customer_address.id)
			address_ids = partner_address_obj.search(cr, uid, [('partner_id','=',rec.id)],context=context)
			for address_id in address_ids:
				if address_id in customer_lines:
					addr_data = partner_address_obj.browse(cr, uid, address_id)
					if addr_data.apartment not in [' ',False,None]:
						addrs_items.append(addr_data.apartment)
					if addr_data.building not in [' ',False,None]:
						addrs_items.append(addr_data.building)
					if addr_data.sub_area not in [' ',False,None]:
						addrs_items.append(addr_data.sub_area)
					if addr_data.landmark not in [' ',False,None]:
						addrs_items.append(addr_data.landmark)
					if addr_data.street not in [' ',False,None]:
						addrs_items.append(addr_data.street)
					if addr_data.city_id:
						addrs_items.append(addr_data.city_id.name1)
					if addr_data.district:
						addrs_items.append(addr_data.district.name)
					if addr_data.tehsil:
						addrs_items.append(addr_data.tehsil.name)
					if addr_data.state_id:
						addrs_items.append(addr_data.state_id.name)
					if addr_data.zip not in [' ',False,None]:
						addrs_items.append(addr_data.zip)
					if len(addrs_items) > 0:
						last_item = addrs_items[-1]
						for item in addrs_items:
							if item!=last_item:
								complete_address = complete_address+item+','+' '
							if item==last_item:
								complete_address = complete_address+item
						comp_loc_vals = {
							'name': complete_address,
							'address_id': addr_data.id,
							'complaint_id': complaint_req_id
						}
						comp_loc_obj.create(cr,uid,comp_loc_vals,context=context)
			models_data = self.pool.get('ir.model.data')
			form_view = models_data.get_object_reference(cr, uid, 'psd_cid', 'complaint_request_form_psd')
			return {
					'type': 'ir.actions.act_window',
					'name': 'Product Complaint Request', 
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'product.complaint.request',
					'res_id': complaint_req_id,
					'views': [(form_view and form_view[1] or False, 'form'),],
					'target': 'current',
					'context': context
				}
		elif request_type == 'product_information_request': 
			addrs_items = []
			cust_address = ''
			if rec.apartment:
				addrs_items.append(rec.apartment)
			if rec.building:
				addrs_items.append(rec.building)
			if rec.sub_area:
				addrs_items.append(rec.sub_area)
			if rec.landmark:
				addrs_items.append(rec.landmark)
			if rec.street:
				addrs_items.append(rec.street)
			if rec.city_id:
				addrs_items.append(rec.city_id.name1)
			if rec.district:
				addrs_items.append(rec.district.name)
			if rec.tehsil:
				addrs_items.append(rec.tehsil.name)
			if rec.state_id:
				addrs_items.append(rec.state_id.name)
			if rec.zip:
				addrs_items.append(rec.zip)
			if addrs_items:    
				for item in addrs_items:
					cust_address = cust_address+item+','+' '   
			info_req_vals = {
				'call_type': 'inbound',
				'customer_type': 'existing',
				'requested_date': datetime.now(),
				'created_by': uid,
				'name': rec.name,
				'contact_name': rec.first_name+' '+rec.last_name,
				'state':'new',
				'email': rec.email,
				'fax': rec.fax,
				'customer_address': cust_address,
				'partner_id': rec.id
			} 
			information_req_id = info_req_obj.create(cr,uid,info_req_vals,context=context)
			models_data = self.pool.get('ir.model.data')
			form_view = models_data.get_object_reference(cr, uid, 'psd_cid', 'view_info_request_form_crm')
			return {
					'type': 'ir.actions.act_window',
					'name': 'Product Information Request', 
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'product.information.request',
					'res_id': information_req_id,
					'views': [(form_view and form_view[1] or False, 'form'),],
					'target': 'current',
					'context': context
				}
		else:
			return super(res_partner, self).create_request(cr, uid, ids, context=context)

	def write(self, cr, uid, ids, vals, context=None):
		if ids:
			if isinstance(ids, (int, long)):
				ids = [ids]
			partner_addr_obj = self.pool.get('res.partner.address')
			phone_obj = self.pool.get('phone.number.child')
			phone_m2m_obj = self.pool.get('phone.m2m')
			partner_addr_obj = self.pool.get('res.partner.address')
			main_address_id = False
			address_id = False
			cit, dist, stat, teh, pho = False, False, False, False, False
			partner_data = self.browse(cr, uid, ids[0])
			address_ids = partner_addr_obj.search(cr, uid, [('partner_id','=', ids[0])], context=context)
			for address_id in address_ids:
				address_data = partner_addr_obj.browse(cr, uid, address_id)
				if partner_data.district and address_data.district:
					if partner_data.district.id == address_data.district.id:
						dist = True         
				if not partner_data.district and not address_data.district:
					dist = True
				if partner_data.city_id and address_data.city_id:
					if partner_data.city_id.id == address_data.city_id.id:
						cit = True          
				if not partner_data.city_id and not address_data.city_id:
					cit = True    
				if partner_data.state_id and address_data.state_id:
					if partner_data.state_id.id == address_data.state_id.id:
						stat = True         
				if not partner_data.state_id and not address_data.state_id:
					stat = True    
				if partner_data.tehsil and address_data.tehsil:
					if partner_data.tehsil.id == address_data.tehsil.id:
						teh = True          
				if not partner_data.tehsil and not address_data.tehsil:
					teh = True      
				if partner_data.phone_many2one and address_data.phone_m2m_xx:
					if partner_data.phone_many2one.number == address_data.phone_m2m_xx.name:
						pho = True          
				if not partner_data.phone_many2one and not address_data.phone_m2m_xx:
					pho = True                      
				if partner_data.title==address_data.title and \
						partner_data.first_name==address_data.first_name and  \
						partner_data.middle_name==address_data.middle_name and \
						partner_data.last_name==address_data.last_name and \
						partner_data.designation==address_data.designation and \
						partner_data.premise_type==address_data.premise_type and \
						partner_data.location_name==address_data.location_name and \
						partner_data.building==address_data.building and \
						partner_data.sub_area==address_data.sub_area and \
						partner_data.street==address_data.street and \
						partner_data.landmark==address_data.landmark and \
						partner_data.zip==address_data.zip and \
						partner_data.fax==address_data.fax and \
						partner_data.email==address_data.email and \
						cit == True and dist == True and teh == True and stat == True and pho == True:
					main_address_id = address_id
			if 'phone_many2one' in vals:
				v_phone_many2one = vals.get('phone_many2one')       
				if v_phone_many2one != False:
					pho_data = phone_obj.browse(cr, uid, v_phone_many2one)
					number = pho_data.number
					contact_select = pho_data.contact_select
					phone_m2m_id = phone_m2m_obj.create(cr, uid, {'name': number,'type': contact_select,'res_location_id': address_id}, context=context)
					vals.update({'phone_m2m_xx': phone_m2m_id})
				else:
					vals.update({'phone_m2m_xx': False})
			partner_addr_obj.write(cr, uid, main_address_id, vals, context=context)     
		return super(res_partner, self).write(cr, uid, ids, vals, context)

res_partner()

class res_partner_address(osv.osv):
	_inherit = 'res.partner.address'

	_columns = {
		'segment': fields.selection([
					('retail','Retail Segment'),
					('distributor','Distributor Segment'),
					('institutional','Institutional/Govt Segment'),
					],'Segment'),
	}

res_partner_address()

class crm_history(osv.osv):
	_name = 'crm.history'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id': fields.many2one('res.company','Company ID'),
		'request_id': fields.char('Request ID', size=32),
		'request_type_psd': fields.selection([('product_request','Product Request'),
									  ('complaint_request','Complaint Request'),
									  ('information_request','Information Request')
									 ],'Request Type'),
		'date_age':fields.char("Date:Age(In Days)",size=32),
		'state':fields.selection([
							  ('new','New'),
							  ('open','Opened'),
							  ('progress','Resource Assigned'),
							  ('closed','Closed'),
							  ('cancel','Cancelled')
							 ],'Status'),
		'pse': fields.many2one('hr.employee', 'PSE'),
		'product_request_id': fields.many2one('product.request'),
		'complaint_request_id': fields.many2one('product.complaint.request'),
		'information_request_id': fields.many2one('product.information.request'),
		'partner_id': fields.many2one('res.partner'),
		'created_by':fields.many2one('res.users','Created By'), 
		'created_date':fields.datetime('Created Date'),
	}

	_defaults = {
			'company_id': _get_company
	}

crm_history()

class sale_customer_master(osv.osv):
	_inherit = 'sale.customer.master'

	def search_customer(self,cr,uid,ids,context=None):
		for temp in self.browse(cr,uid,ids):
			try:
				list_id = []
				company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id
				Sql_Str = ''
				job_id= ''
				if temp.job_id:
								job_id = temp.job_id.lstrip()
								job_id  = temp.job_id.rstrip()
				if temp.job_id:
					Sql_Str = Sql_Str + " and IC.id in (select rs.name_contact from res_scheduledjobs rs where rs.scheduled_job_id ilike '" +"%"+str(job_id)+ "%')"
				if temp.customer_no:
					Sql_Str = Sql_Str + " and IC.ou_id ilike '" +"%"+ str(temp.customer_no) + "%'"
				if temp.customer_name :
					Sql_Str = Sql_Str + " and IC.name ilike '" +"%"+ str(temp.customer_name) + "%'"
				if temp.contact_name :
					Sql_Str = Sql_Str + " and IC.contact_name ilike '" +"%"+ str(temp.contact_name) + "%'"
				if temp.service_area_cust.id != False:
					Sql_Str = Sql_Str + " and ICL.service_area ='" +str(temp.service_area_cust.id) + "'"
				if temp.city_id.id :
					Sql_Str = Sql_Str + " and IC.city_id ='" +str(temp.city_id.id) + "'"
				if temp.mobile:
							Sql_Str = Sql_Str+" and ICL.customer_address in (select i.res_location_id from phone_m2m i where i.name ilike '"+"%" + str(temp.mobile) + "%' and i.type in ('"'mobile'"','"'landline'"'))"
				if temp.phone:
							Sql_Str = Sql_Str+" and ICL.customer_address in (select i.res_location_id from phone_m2m i where i.name ilike '"+"%" + str(temp.phone) + "%' and i.type in ('"'mobile'"','"'landline'"'))"
				if temp.zip:
					Sql_Str = Sql_Str + " and IC.zip ilike '"+"%"+str(temp.zip) +"%'"
				if temp.contact_no:
					Sql_Str = Sql_Str + " and IC.mobile ilike '"+"%"+str(temp.contact_no) +"%'"
				if temp.cse.id:
					Sql_Str = Sql_Str + " and IC.main_cse ='" +str(temp.cse.id) + "'"
				if temp.branch_id.id:
					Sql_Str = Sql_Str + " and ICL.branch ='" +str(temp.branch_id.id) + "'"
				if temp.from_date:
					Sql_Str =Sql_Str +" and IC.customer_since >= '" +  str(temp.from_date) + "'"
				if temp.to_date:
					Sql_Str =Sql_Str +" and IC.customer_since <= '" + str(temp.to_date) + "'"
				if temp.location.id:
					Sql_Str = Sql_Str + " and ICL.customer_address ='" +str(temp.location.id) + "'"
				if temp.contract_no:
					Sql_Str = Sql_Str + " and IC.id in (select RP.partner_id from sale_contract RP where RP.contract_number ilike '" +"%"+ str(temp.contract_no) + "%')"
				if temp.building:
					Sql_Str = Sql_Str + " and ICL.customer_address in (select id from res_partner_address where building ilike '"+"%"+str(temp.building) +"%')"
				if company_id.establishment_type=='psd': 
					Sql_Str = Sql_Str + " and IC.company_id ='" +str(company_id.id) + "'"
				Main_Str123 = "select distinct(IC.id) from res_partner IC join customer_line ICL on ICL.partner_id=IC.id and IC.customer=True and IC.ou_id is not Null "
				main_str1234=Main_Str123 + Sql_Str
				update_command = "update res_partner set  cust_line_id="+str(temp.id)+"  where id in ("+main_str1234+")"
				cr.execute(update_command)
				cr.commit()
				update_command = "update res_partner set  cust_line_id=Null  where id not in ("+main_str1234+")"
				cr.execute(update_command)
				cr.commit()
			except Exception  as exc:
				if exc.__class__.__name__ == 'TransactionRollbackError':
					pass
				else:
					raise

sale_customer_master()
