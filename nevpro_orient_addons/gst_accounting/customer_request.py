
from osv import osv,fields
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import xmlrpclib
import os
import re

# class ccc_new_address(osv.osv):
# 	_inherit = 'ccc.new.address'

# 	_columns = {
# 		'principle_place_of_business_tag':fields.many2one('principle.place.of.business','Principle place of business tag'),
# 		'special_status':fields.many2one('special.status','Special Status'),
# 		'gst_no':fields.char('GST No.',size=124),
# 	}

# ccc_new_address()


class ccc_branch_new(osv.osv):
	_inherit = 'ccc.branch.new'

	_columns = {
		'gst_no':fields.char('GST No.',size=124),
	}

	def onchange_premise_type(self,cr,uid,ids,premise_type,context=None):
		data = {}
		if premise_type:
			premise_obj = self.pool.get('premise.type.master')
			premise_id = premise_obj.search(cr,uid,[('key','=',premise_type)])
			premise_data = premise_obj.browse(cr,uid,premise_id[0])
			if premise_data.select_type == 'rbu' and premise_data.key != 'co_operative_housing_society':
				data.update(
					{
						'gst_no': 'Unregistered'
					})
			elif premise_data.select_type == 'rbu' and premise_data.key == 'co_operative_housing_society':
				data.update(
					{
						'gst_no': ''
					})
			else:
				data.update(
					{
						'gst_no': ''
					})
		else:
			data.update(
				{
					'gst_no': ''
				})
		return {'value': data}


	def confirm_contact(self,cr,uid,ids,context=None):
		check = False
		for rec in self.browse(cr,uid,ids):	
			if str(rec.name).find("'")!=-1 or str(rec.first_name).find("'")!=-1 or str(rec.middle_name).find("'")!=-1 or str(rec.last_name).find("'")!=-1 or str(rec.designation).find("'")!=-1 or str(rec.location_name).find("'")!=-1 or str(rec.apartment).find("'")!=-1 or str(rec.building).find("'")!=-1 or str(rec.sub_area).find("'")!=-1 or str(rec.street).find("'")!=-1 or str(rec.landmark).find("'")!=-1 or str(rec.zip).find("'")!=-1 or str(rec.ref_text).find("'")!=-1 :
				raise osv.except_osv(('Alert!'),('Please remove the single quote from the field'))
			search_id = rec.id
			if rec.name:
				search = self.pool.get('ccc.new.address').search(cr,uid,[('new_customer_id1','=',rec.id)])
				if not search:
					check = True
					address_id = self.pool.get('ccc.new.address').create(cr,uid,
						{
							'new_customer_id1':rec.id,
							'contact_name':rec.contact_name,
							'name':rec.name,
							'premise_type':rec.premise_type,
							'title':rec.title,
							'building':rec.building,
							'apartment':rec.apartment,
							'location_name':rec.location_name,
							'sub_area':rec.sub_area,
							'street':rec.street,
							'landmark':rec.landmark,
							'state_id':rec.state_id.id,	
							'city_id':rec.city_id.id,
							'district':rec.district.id,
							'tehsil':rec.tehsil.id,
							'zip':rec.zip,											
							'email':rec.email,
							'phone':rec.phone,
							'fax':rec.fax,
							'mobile':rec.mobile,
							'first_name':rec.first_name,
							'middle_name':rec.middle_name,
							'last_name':rec.last_name,
							'designation':rec.designation,
							'primary_contact':True
						},context=None)
					if rec.phone_many2one:
						search_phone_id = self.pool.get('phone.number.child.new').search(cr,uid,[('partner_id_new_cust','=',rec.id)])
						for iterate in self.pool.get('phone.number.child.new').browse(cr,uid,search_phone_id):
							phone_m2m_id = self.pool.get('phone.m2m').create(cr,uid,{'name':iterate.number,'type':iterate.contact_select,'ccc_new_address_id':address_id})
							self.pool.get('ccc.new.address').write(cr,uid,address_id,{'phone_m2m_xx':phone_m2m_id})
			if not rec.premise_type :
				raise osv.except_osv(('Alert!'),('Please Enter Premise Type'))
			if not rec.building :
				raise osv.except_osv(('Alert!'),('Please Enter Building Name'))
			if not rec.apartment :
				raise osv.except_osv(('Alert!'),('Please Enter Apartment'))
			if not rec.ref_by :
				raise osv.except_osv(('Alert!'),('Please Enter Reference By'))
			if not rec.first_name :
				raise osv.except_osv(('Alert!'),('Please Enter First Name'))
			if not rec.last_name :
				raise osv.except_osv(('Alert!'),('Please Enter Last Name'))
			if not rec.city_id :
				raise osv.except_osv(('Alert!'),('Please Enter City'))
			if not rec.state_id :
				raise osv.except_osv(('Alert!'),('Please Enter State'))
			# if not rec.gst_no:
			# 	raise osv.except_osv(('Alert!'),('Please Enter GST No.'))
			if rec.gst_no and rec.gst_no!= 'Unregistered':
				test_gst_no=re.match(r'^([0-9]){2}([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}([a-zA-Z0-9]){3}$',rec.gst_no)
				if not test_gst_no:
					raise osv.except_osv(('Alert'),('Please verify the GST No.'))
				if rec.state_id.state_code != rec.gst_no[0:2]:
					raise osv.except_osv(('Alert'),('Please verify the State Code'))
		self.write(cr,uid,ids,{'check_branch':True})
		return True		

	def process_new_customer_sync(self,cr,uid,o,k,main_dict,branch_dict,count_location,seq_id):
		credit_period = 0
		premise_type = ''
		count_record = 0
		premise_obj = self.pool.get('premise.type.master')
		registration_obj = self.pool.get('gst.type.customer')
		if o.form_id_new_cust:
			main_dict = self.check_existing(cr,uid,o,k,main_dict)
			count_total_rec = self.pool.get('ccc.branch.new').search(cr,uid,[('form_id_new_cust','=',o.form_id_new_cust)])
			count_record = len(count_total_rec)
		contact = [k.new_customer_address_id.first_name ,k.new_customer_address_id.middle_name ,k.new_customer_address_id.last_name]
		total_name = ' '.join(filter(bool,contact))
		
		if k.branch_id.id not in main_dict['branch_list'] and k.branch_id and k.branch_id.name != 'Branch Unknown':
											
			premise_id = premise_obj.search(cr,uid,[('key','=',o.premise_type)])
			premise_data = premise_obj.browse(cr,uid,premise_id[0])		

			cust_create_vals = {
								'name':o.name,'customer_category_id':o.customer_category_id.id,
								'title':o.title,'contact_name':total_name,
								'first_name':o.first_name,'middle_name':o.middle_name,
								'last_name':o.last_name,'designation':o.designation,										
								'email':o.email,'premise_type':k.new_customer_address_id.premise_type,
								'location_name':k.new_customer_address_id.location_name,
								'apartment':k.new_customer_address_id.apartment,'phone':o.phone,
								'building':k.new_customer_address_id.building,'sub_area':k.new_customer_address_id.sub_area,
								'fax':k.new_customer_address_id.fax,'street':k.new_customer_address_id.street,
								'user_id':uid,
								'landmark':k.new_customer_address_id.landmark,'mobile':o.mobile,
								'city_id':k.new_customer_address_id.city_id.id if o.city_id else '',
								'state_id':k.new_customer_address_id.state_id.id if o.state_id else '','tag_new':o.tag_new,
								'district':k.new_customer_address_id.district.id,'ref_by':o.ref_by.id,
								'tehsil':k.new_customer_address_id.tehsil.id,
								'ref_by_name':o.ref_text,
								'customer_since':str(datetime.now().date()),
								'zip':k.new_customer_address_id.zip,'customer_id_main':seq_id,'ou_id':seq_id,
								# 'gst_type_customer':
								# 'gst_no':
								}
			if premise_data.select_type == 'rbu' and premise_data.key != 'co_operative_housing_society':
				registration_id = registration_obj.search(cr,uid,[('name','=','Unregistered')])
				gst_no = 'Unregistered'
				cust_create_vals.update({
						'gst_type_customer': registration_id[0],
						'gst_no': gst_no
					})
			# elif premise_data.select_type == 'rbu' and premise_data.key == 'co_operative_housing_society':
			# 	registration_id = registration_obj.search(cr,uid,[('name','=','Registered')])
			# 	gst_no =  o.gst_no
			# 	cust_create_vals.update({
			# 			'gst_type_customer': registration_id[0],
			# 			'gst_no': gst_no
			# 		})
			# else:
			# 	registration_id = registration_obj.search(cr,uid,[('name','=','Registered')])
			# 	gst_no = o.gst_no
			# 	cust_create_vals.update({
			# 			'gst_type_customer': registration_id[0],
			# 			'gst_no': gst_no
			# 		})
			customer_create_id= self.pool.get('res.partner').create(cr,uid,cust_create_vals)														
			
			customer_create=''
			date1=''
			date1=str(datetime.now().date())
			conv=time.strptime(str(date1),"%Y-%m-%d")
			date1 = time.strftime("%d-%m-%Y",conv)
			customer_create=o.name+'   Customer Created On   '+date1
			customer_create_date=self.pool.get('customer.logs').create(cr,uid,{'customer_join':customer_create,'customer_id':customer_create_id})
			main_dict.update({'customer_create_id':customer_create_id})
			
	

			val_ids = tuple([k.branch_id.id]+[customer_create_id])
			main_dict['main_partner'].append(val_ids)
			###############################################
			if o.phone_id:
				for iterate in self.pool.get('phone.number.new').browse(cr,uid,[o.phone_id.id]):

					phone_new_id = self.pool.get('phone.number').create(cr,uid,{'partner_id':customer_create_id})
					for iterate_line in iterate.phone_number_one2many:
						child_id =self.pool.get('phone.number.child').create(cr,uid,{'partner_id':customer_create_id,'contact_number':phone_new_id,
'contact_select':iterate_line.contact_select,'number':iterate_line.number})
						self.pool.get('res.partner').write(cr,uid,customer_create_id,{'phone_id':phone_new_id,'phone_many2one':child_id})

		request_id = ''
		req_id_new = ''
		for iter_values_id in main_dict['main_partner']:
		    for a,b in [iter_values_id]:
				if isinstance(a,(list,tuple)):
					if a == k.branch_id.id:
						main_dict.update({'customer_create_id':b})
				else:
					if a == k.branch_id.id:
						main_dict.update({'customer_create_id':b})

		customer_create_id = main_dict['customer_create_id']
		if not o.request_id:
			req_id_new = self.pool.get('ir.sequence').get(cr, uid, 'ccc.new.location')	
		else:
			request_id = o.request_id
		if customer_create_id:
			cust_id = self.pool.get('res.partner').browse(cr,uid,main_dict['customer_create_id']).customer_id_main
			ou_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
			prefix = self.pool.get('res.users').browse(cr,uid,uid).company_id.new_cust_prefix_id

		
			values = cust_id
		
			if '0000' in values[:4]:
				cust_id = cust_id[4:]
				self.pool.get('res.partner').write(cr,uid,main_dict['customer_create_id'],{'customer_id_main':cust_id})
			count_sequence = 0
			if not o.request_id:
				#request_id = ou_id+prefix+self.pool.get('res.partner').browse(cr,uid,main_dict['customer_create_id']).ou_id[4:]+req_id_new

				if not o.form_id_new_cust:
					count_sequence = main_dict['count_sequence']+1
				else:
					count_sequence = count_record+1

				if count_sequence <= 9:
					request_id= ou_id+prefix+cust_id+'00'+str(count_sequence)
				elif count_sequence <= 99:
					request_id= ou_id+prefix+cust_id+'0'+str(count_sequence)
					
				else:
					request_id= ou_id+prefix+cust_id+str(count_sequence)


			main_dict.update({'count_sequence':count_sequence})

			main_dict.update({'request_id':request_id})
			self.pool.get('ccc.new.location').write(cr,uid,k.id,{'request_id':request_id})


		
		

		for iter_values_location in main_dict['count_address']:
		    for s,t in [iter_values_location]:
				if isinstance(s,(list,tuple)):
					if s == k.branch_id.id:
						count_location=t
				else:
					if s == k.branch_id.id:
						count_location=t



		if k.branch_id and k.branch_id.name != 'Branch Unknown':
			self.pool.get('crm.lead').create(cr,uid,{'partner_id':main_dict['customer_create_id'],
			'partner_name':o.name,
			'type_request':o.request_type,
			'user_id':uid,
			'inspection_date':str(datetime.now()),'inquiry_no':request_id,'state':'open','comment':o.comment_remark})
		if k.new_customer_address_id.id not in main_dict['customer_location_id_main'] and k.branch_id and k.branch_id.name != 'Branch Unknown':
				
				if count_location <= 9:
					count_location += 1
					location_number = self.pool.get('res.partner').browse(cr,uid,main_dict['customer_create_id']).ou_id+'0'+str(count_location)
					main_dict.update({'location_number':location_number})
					val_ids = tuple([k.branch_id.id]+[count_location])
					main_dict['count_address'].append(val_ids)
				else:
					count_location += 1
					location_number = self.pool.get('res.partner').browse(cr,uid,main_dict['customer_create_id']).customer_id_main+'0'+str(count_location)
					main_dict.update({'location_number':location_number})
					val_ids = tuple([k.branch_id.id]+[count_location])
					main_dict['count_address'].append(val_ids)
				primary_contact = False
				if count_location == 1:
					primary_contact = True
				search_type = self.pool.get('premise.type.master').search(cr,uid,[('key','=',k.new_customer_address_id.premise_type)])	
				cust_type = self.pool.get('premise.type.master').browse(cr,uid,search_type)[0].select_type					
				search_credit = self.pool.get('credit.period').search(cr,uid,[('name','=',cust_type)])
				credit_period_val = self.pool.get('credit.period').browse(cr,uid,search_credit)[0].credit_period
				partner_address_id = self.pool.get('res.partner.address').create(cr,uid,{
'location_id':location_number,'title':o.title,'contact_name':total_name,'first_name':k.new_customer_address_id.first_name,'middle_name':k.new_customer_address_id.middle_name,'last_name':k.new_customer_address_id.last_name,
'designation':k.new_customer_address_id.designation,'fax':k.new_customer_address_id.fax,'email':k.new_customer_address_id.email,
'title':k.new_customer_address_id.title,'premise_type':k.new_customer_address_id.premise_type,'location_name':k.new_customer_address_id.location_name,'apartment':k.new_customer_address_id.apartment,
'building':k.new_customer_address_id.building,'sub_area':k.new_customer_address_id.sub_area,
'street':k.new_customer_address_id.street,'landmark':k.new_customer_address_id.landmark,'name':total_name,
'tehsil':k.new_customer_address_id.tehsil.id if k.new_customer_address_id.tehsil.id else '',
'zip':k.new_customer_address_id.zip,'district':k.new_customer_address_id.district.id if k.new_customer_address_id.district else '',
'state_id':str(k.new_customer_address_id.state_id.id) if k.new_customer_address_id.state_id else '','primary':k.new_customer_address_id.primary_contact if k.new_customer_address_id.primary_contact else False,
'city_id':str(k.new_customer_address_id.city_id.id) if k.new_customer_address_id.city_id else '','partner_id':main_dict['customer_create_id'],'primary_contact':primary_contact,'credit_period_days':credit_period_val})
				search_phone_id = self.pool.get('phone.m2m').search(cr,uid,[('ccc_new_address_id','=',k.new_customer_address_id.id)])
				print "@@@@@@@@@@@@@@@@@@@@@ main dict###########################################",main_dict['customer_create_id']
				print "@@@@@@@@@@@@@@@@@@@@@ main dict###########################################",main_dict
				#print lll
				#ccp task pratik started
				# premise_type=k.new_customer_address_id.premise_type
				# total_id = self.pool.get('premise.type.master').search(cr,uid,[('key','=',premise_type)])
				# for get_val in self.pool.get('premise.type.master').browse(cr,uid,total_id):
				# 	if get_val.select_type == 'cbu':
				# 		credit_period=30
				# 	if get_val.select_type == 'rbu':
				# 		credit_period=1
				# if customer_create_id:
				# 	for customer in self.pool.get('res.partner').browse(cr,uid,[customer_create_id]):
				# 		credit_period=customer.credit_period
				# code ends here (credit period added in customer.line)
				

				if search_phone_id:

						self.pool.get('phone.m2m').write(cr,uid,search_phone_id,{'res_location_id':partner_address_id})
						self.pool.get('res.partner.address').write(cr,uid,partner_address_id,{'phone_m2m_xx':search_phone_id[0]})
				self.pool.get('customer.line').create(cr,uid,{
							'location_id':main_dict['location_number'],
							'customer_address':partner_address_id,
							'service_area':k.service_area.id,'branch':k.branch_id.id,
							'resource_assign':k.assign_resource.name,'phone_many2one':search_phone_id[0] if search_phone_id else '',
							'partner_id':main_dict['customer_create_id'],
							'credit_period':credit_period,
							})
						
				


				
				main_dict['customer_location_id'].append(k.new_customer_address_id.id)
				main_dict['branch_list'].append(k.branch_id.id)
				val = tuple([k.new_customer_address_id.id]+[partner_address_id])
				#if k.new_customer_address_id.phone_m2m_xx:
				
				main_dict['main_address_id'].append(val)
				loc_id = ''
				for iter_values in main_dict['main_address_id']:
					for x,y in [iter_values]:
						if isinstance(x,(list,tuple)):
							if x == k.new_customer_address_id.id:
								loc_id = y
						else:
							if x == k.new_customer_address_id.id:
								loc_id = y
				branch_dict.update({'customer_create_id':main_dict['customer_create_id'],'req_id':main_dict['request_id'],'location_id':main_dict['location_number']})

		if k.branch_id.id != self.pool.get('res.users').browse(cr,uid,uid).company_id.id and k.branch_id and k.branch_id.name != 'Branch Unknown':
			if o.form_id_new_cust:
				branch_dict=self.check_existing_for_branch(cr,uid,o,k,branch_dict)
			self.pool.get('res.partner').write(cr,uid,main_dict['customer_create_id'],{'active':False})
			self.process_new_customer_other_branch_sync(cr,uid,o,k,branch_dict)
							
		if k.branch_id and k.branch_id.name != 'Branch Unknown':
			
			main_dict = self.process_main_sync(cr,uid,o,k,main_dict,k.new_customer_address_id.id)										
		return main_dict,count_location	


	def process_new_customer_request(self,cr,uid,ids,context=None):
		new_loc = self.pool.get('ccc.new.location')
		val = ''
		main_list= []
		customer_location_id = []
		customer_flag = False
		post_pms = []
		post=[]
		main_dict = {
			'customer_location_id_list':[],
			'customer_flag':False,
			'branch_partner_id':'',
			'customer_create_id':'',
			'rec':[],
			'branch_list':[],
			'branch_list_main':[],
			'count_address':[],
			'state':'',
			'customer_location_id':[],
			'customer_location_id_main':[],
			'check_address_id':[],
			'check_partner':[],
			'request_id':'',
			'main_address_id':[],
			'main_partner':[],
			'count_id':0,
			'partner_address_id':[],
			'count_location':0,
			'location_number':'',
			'pms_list_id':[],
			'count_sequence':0,
		} 
		branch_dict = {
			'customer_create_id':'',
			'address_id':[],
			'customer_location_id_list':[],
			'customer_flag':False,
			'branch_partner_id':'',
			'location_id':'',
			'branch_address_id':[],
			'branch_id_list':[],
			'req_id':'',
			'partner_list':[],
		}
		post_branch = []
		phone_number_append = []
		list_id = []
		state_ids = []
		for o in self.browse(cr,uid,ids):
			# if not o.gst_no:
			# 	raise osv.except_osv(('Alert!'),('Please Enter GST No.'))
			if o.gst_no and o.gst_no != 'Unregistered':
				test_gst_no=re.match(r'^([0-9]){2}([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}([a-zA-Z0-9]){3}$',o.gst_no)
				if not test_gst_no:
					raise osv.except_osv(('Alert'),('Please verify the GST No.'))
				if o.state_id.state_code != o.gst_no[0:2]:
					raise osv.except_osv(('Alert'),('Please verify the State Code'))
			customer_company_name = o.name
			search_phone_number = self.pool.get('phone.number.child.new').search(cr,uid,[('partner_id_new_cust','=',o.id)])
			browse_phone_number = self.pool.get('phone.number.child.new').browse(cr,uid,search_phone_number)
			for browse_phone_number_id in browse_phone_number:
				phone_number = browse_phone_number_id.number
				phone_number_append.append(str(phone_number))
			strip_customer_company_name = str(customer_company_name).strip(' ')
			filter_id = [('name','=',strip_customer_company_name)]
			search_res_partner = self.pool.get('res.partner').search(cr,uid,filter_id)
			search_phone_number_exist = self.pool.get('phone.number.child').search(cr,uid,[('partner_id','in',search_res_partner)])
			browse_phone_number_exist = self.pool.get('phone.number.child').browse(cr,uid,search_phone_number_exist)
			for search_phone_number_id in browse_phone_number_exist:
				phone_number_str = search_phone_number_id.number
				if phone_number_str in phone_number_append:
					raise osv.except_osv(('Alert!'),('Cannot create customer of same name!'))
			aa = o.request_type
			q = self.pool.get('ccc.branch').create(cr,uid,{'inquiry_type':'all_request'},context=context)
			main_branch_id = q
			search_id=o.id
			seq_id = ''
			ccc_customer_request_id = self.pool.get('ccc.branch.new').search(cr,uid,[('form_id_new_cust','=',o.form_id_new_cust),('state','!=','new')])
			created_by = self.pool.get('res.users').browse(cr,uid,uid).name      
			product_dic = {}
			for location_line in o.new_customer_location:
				# premise_type = location_line.new_customer_address_id.premise_type
				# premise_id = self.pool.get('premise.type.master').search(cr,uid,[('key','=',premise_type)])
				# premise_data = self.pool.get('premise.type.master').browse(cr,uid,premise_id[0])
				# if premise_data.select_type == 'cbu' and not location_line.new_customer_address_id.gst_no:
				# 	raise osv.except_osv(('Alert!'),('Please enter the GST No. for the location!')) 
				# elif premise_data.select_type == 'rbu' and premise_data.key == 'co_operative_housing_society' and not location_line.new_customer_address_id.gst_no:
				# 	raise osv.except_osv(('Alert!'),('Please enter the GST No. for the location!')) 
				# gst_no = location_line.new_customer_address_id.gst_no
				state_id = location_line.new_customer_address_id.state_id.id
				state_ids.append(state_id)
			state_ids = set(state_ids)
			state_ids = list(state_ids)
			if len(state_ids) > 1:
				raise osv.except_osv(('Alert!'),('Delivery addresses will be belong to single state only!')) 
			for pms_iterate in o.new_customer_location:
				temp11 = pms_iterate.new_customer_address_id.id
				temp22 = pms_iterate.product_id.id
				k = pms_iterate.product_id.name
				temp33 = tuple([temp11]+[temp22])
				post_pms.append(temp33)
				if temp11 not in product_dic :
					product_dic[temp11]=[k]
				else :
					product_dic[temp11].append(k)
				for i in product_dic:
					if len(product_dic[i] ) > 1 and 'TMG' in product_dic[i]:
						raise osv.except_osv(('Alert!'),('You cannot select any other service with TMG'))
				for irange in range(0,len(post_pms)):   
						for jrange in range(irange+1,len(post_pms)):
							if post_pms[irange][0]==post_pms[jrange][0] and post_pms[irange][1]==post_pms[jrange][1]:
								raise osv.except_osv(('Alert!'),('Duplicate PMS for same address is not allowed.')) 
			for service in o.new_customer_location:
				if service.no_of_services==0 and service.no_of_inspections==0:
					raise osv.except_osv(('Alert!'),('Must Enter Inspections or Services.'))        
			if o.form_id_new_cust and ccc_customer_request_id:
				seq_id = self.pool.get('ccc.branch.new').browse(cr,uid,ccc_customer_request_id[0]).partner_id.ou_id
			elif not o.request_id:
				seq_id = self.pool.get('ir.sequence').get(cr, uid, 'res.partner.code.new')
			else:
				if o.partner_id:
					seq_id =  '0000'+self.pool.get('res.partner').browse(cr,uid,o.partner_id.id).customer_id_main
			if not o.form_id_new_cust:
				for line_in in o.new_customer_location:
					temp_in1=line_in.new_customer_address_id.id
					temp_in2=line_in.branch_id.id
					temp_in3=tuple([temp_in1]+[temp_in2])
					post_branch.append(temp_in3)
					for p in range(0,len(post_branch)): 
						for l in range(p+1,len(post_branch)):
							if post_branch[p][0]==post_branch[l][0]:
								if post_branch[p][1]!=post_branch[l][1]:
									raise osv.except_osv(('Alert!'),('Same Location with Differnt Branch cannot be Selected.'))
			else:
				ccc_customer_branch_check = self.pool.get('ccc.branch.new').search(cr,uid,[('form_id_new_cust','=',o.form_id_new_cust)])
				for record_id in self.pool.get('ccc.branch.new').browse(cr,uid,ccc_customer_branch_check):
					for line_in in record_id.new_customer_location:
						temp_in1=line_in.new_customer_address_id.id
						company_obj = self.pool.get('res.company')
						temp_in2=line_in.branch_id.id
						temp_in3=tuple([temp_in1]+[temp_in2])
						post_branch.append(temp_in3)
						for p in range(0,len(post_branch)): 
							for l in range(p+1,len(post_branch)):
								print post_branch[p][0],post_branch[l][0],post_branch[p][1],post_branch[l][1]
								if post_branch[p][0]==post_branch[l][0]:
									if post_branch[p][1] and post_branch[l][1]:
										if (company_obj.browse(cr,uid,post_branch[p][1]).name != 'Branch Unknown' and post_branch[p][1]) and (company_obj.browse(cr,uid,post_branch[l][1]).name != 'Branch Unknown' and post_branch[l][1]) :
										
											if post_branch[p][1]!=post_branch[l][1]:
												raise osv.except_osv(('Alert!'),('Same Location with Differnt Branch cannot be Selected.'))
			if o.request_type == 'new_cust':
				if o.check_cancel == True:
					self.write(cr,uid,o.id,{'check_cancel':False})
				if not o.new_customer_location:
					raise osv.except_osv(('Alert'),('You cannot confirm a new customer order which has no line.'))
				new_customer_line_obj = self.pool.get('ccc.new.location')
				new_customer_line = new_customer_line_obj.search(cr,uid,[('new_customer_id1','=',o.id)],order='new_customer_address_id')
				for line in new_customer_line_obj.browse(cr,uid,new_customer_line): 
					contact=[line.new_customer_address_id.first_name ,line.new_customer_address_id.middle_name ,line.new_customer_address_id.last_name]
					total_name=' '.join(filter(bool,contact))
					count_location = 0
					if line.branch_id.name=='Branch Unknown' or not line.branch_id:
						state='new'
					else:
						state='open'
					premise = line.new_customer_address_id.premise_type
					location_name = line.new_customer_address_id.location_name#abhi
					apartment = line.new_customer_address_id.apartment
					building = line.new_customer_address_id.building
					sub_area = line.new_customer_address_id.sub_area
					street = line.new_customer_address_id.street
					landmark = line.new_customer_address_id.landmark
					state_id = line.new_customer_address_id.state_id.name
					city_id = line.new_customer_address_id.city_id.name1
					tehsil = str(line.new_customer_address_id.tehsil.id)
					district = str(line.new_customer_address_id.district.id)
					address=[location_name,apartment,building,sub_area,street,landmark,state_id,city_id,tehsil,district]#abhi
					addr=', '.join(filter(bool,address))
					if line.branch_id.name =='Branch Unknown' or not line.branch_id: # by pratik
						main_dict,count_location = self.process_new_customer_sync(cr,uid,o,line,main_dict,branch_dict,count_location,seq_id)
					else:
						main_dict,count_location = self.process_new_customer_sync(cr,uid,o,line,main_dict,branch_dict,count_location,seq_id)
					b = self.pool.get('ccc.branch.new').create(cr,uid,
						{
							'request_type':'new_cust',
							'partner_id':o.partner_id.id,
							'form_id_new_cust':o.form_id_new_cust if o.form_id_new_cust else o.id,
							'tag_new':o.tag_new,'user_name':created_by,
							'state':state,'request_id':main_dict['request_id'],
							'contact_name':total_name,'inquiry_type':o.inquiry_type,
							'premise_type':line.new_customer_address_id.premise_type,
							'location_name':line.new_customer_address_id.location_name,#abhi 
							'apartment':line.new_customer_address_id.apartment,'tag':o.tag.id,
							'building':line.new_customer_address_id.building,'email':o.email,
							'name':o.name,'sub_area':line.new_customer_address_id.sub_area,'fax':line.new_customer_address_id.fax,'street':line.new_customer_address_id.street,
							'service_area':line.service_area.id,
							'branch_id':line.branch_id.id,'landmark':line.new_customer_address_id.landmark,
							'ref_by':o.ref_by.id,'city_id':line.new_customer_address_id.city_id.id,'district':line.new_customer_address_id.district.id,
							'tehsil':line.new_customer_address_id.tehsil.id,'state_id':line.new_customer_address_id.state_id.id,'zip':line.new_customer_address_id.zip,
							'request_id_related':line.request_id,
							'check_ref':o.check_ref,'title':o.title,
							'ref_text':o.ref_text,
							'first_name':o.first_name,
							'middle_name':o.middle_name,
							'last_name':o.last_name,
							'designation':o.designation,
							'check_branch':True,'call_type':o.call_type,
							'request_date':o.request_date,
							'gst_no': o.gst_no,'lead_desc':o.lead_desc,'lead_data_id':o.lead_data_id,'status_track_date':datetime.now().date(),'check_lead_tracker':o.check_lead_tracker,'lead_tracker':o.lead_tracker,'submitter_empcode':o.submitter_empcode,'check_pci_tec':o.check_pci_tec
						},context=context)
					mobile_id = self.pool.get('phone.m2m').search(cr,uid,[('ccc_new_address_id','=',line.new_customer_address_id.id)])
					if mobile_id:
						for iterate in self.pool.get('phone.m2m').browse(cr,uid,mobile_id):
							phone_new_id = self.pool.get('phone.number.new').create(cr,uid,{'partner_id_new_cust':b})
							child_ids = self.pool.get('phone.number.child.new').create(cr,uid,
								{
									'partner_id_new_cust':b,'contact_number':phone_new_id,
									'contact_select':iterate.type,'number':iterate.name
								})
							self.pool.get('ccc.branch.new').write(cr,uid,b,{'phone_id':phone_new_id,'phone_many2one':child_ids})
					address = line.new_customer_address_id.id
					list_id.append(b)
					discount_amount=''
					amount=''
					if line.service_rate and line.discount_flat_gss:
						discount_amount=float((line.service_rate*line.discount_flat_gss)/100)
						amount=(line.service_rate - discount_amount)
					ccc_location_id = self.pool.get('ccc.new.location').create(cr,uid,
						{
							'new_customer_id1':b,
							'request_id':main_dict['request_id'],
							'origin':line.origin.id,
							'new_customer_address_id':line.new_customer_address_id.id,
							'branch_id':line.branch_id.id,
							'product_id':line.product_id.id,
							'service_frequency':line.service_frequency.id,
							'no_of_services':line.no_of_services,
							'service_area':line.service_area.id,
							'no_of_inspections':line.no_of_inspections,
							'requested_date':line.requested_date,
							'service_rate':line.service_rate,
							'discount_flat_gss':line.discount_flat_gss,
							'discount_amount_gss':amount,
							'state':state,
							'remark':line.remark,
							'scheme_name':line.scheme_name.id,
							'campaign_discount':line.campaign_discount,
							'area_type':line.area_type.id if line.area_type else '',
							'check':True,
							'rates_with_tax':line.rates_with_tax,           
							'campaign_discount':line.campaign_discount if line.campaign_discount else 0.0,
							'campaign_disc_amnt':line.campaign_disc_amnt if line.campaign_disc_amnt else 0.0 ,
							'type_of_service':line.type_of_service,
							'area_sq_mt':line.area_sq_mt,
							'no_of_trees':line.no_of_trees,
							'boolean_pms_tg':line.boolean_pms_tg,
						},context=context)
					for part in o.comment_line_new:
						if line.new_customer_address_id.id == part.location.id:
							self.pool.get('ccc.new.comment.line').create(cr,uid,
								{	'request_id1':b,
									'user_id':part.user_id,
									'comment':part.comment,'location':part.location.id,
									'comment_date':part.comment_date,
									'state':part.state
								},context=context)
					if not o.partner_id :
						self.pool.get('ccc.branch.new').write(cr,uid,b,{'partner_id':main_dict['customer_create_id'],'request_id':main_dict['request_id']})
					loc_id= ''
					for iter_values in main_dict['main_address_id']:
						for x,y in [iter_values]:
							if isinstance(x,(list,tuple)):
								if x == line.new_customer_address_id.id:
									loc_id = y
							else:
								if x == line.new_customer_address_id.id:
									loc_id = y
					self.pool.get('ccc.new.location').write(cr,uid,ccc_location_id,{'location_id':loc_id,'request_id':main_dict['request_id']})
					self.pool.get('ccc.new.address').write(cr,uid,line.new_customer_address_id.id,{'new_customer_id1':b})
					cr.execute("DELETE FROM ccc_new_location WHERE id=%s", ([line.id]))
				cr.execute("DELETE FROM ccc_branch_new WHERE id=%s", ([o.id]))
				type_request = 'new_cust'
				list_request = ['complaint_request','renewal_request','information_request','lead_request','new_cust','generic_request']
			else:
				location_name = o.location.location_name
				apartment1 = o.location.apartment
				building1 = o.location.building
				street1 = o.location.street
				address1=[location_name,apartment1,building1,street1]
				addr1=', '.join(filter(bool,address1))
		self.pool.get('ccc.branch').search_ccc_branch(cr,uid,[q]) 
		# status_track_date = datetime.now().date()
		# print "iiiiiiiiiiiiiiiiiiiiiii",ids,status_track_date,type(status_track_date),type(ids[0])
		# self.write(cr,uid,ids[0],{'status_track_date':status_track_date})  
		return {
					'type': 'ir.actions.act_window',
					'name': 'Global Search',
					'view_mode': 'form',
					'view_type': 'form',
					'view_id': False,
					'res_id':int(q),
					'res_model':'ccc.branch',
					'target':'current',
				}


	def process_sales(self,cr,uid,ids,context=None):
		for o in self.browse(cr,uid,ids):
			product_name=''
			ref_name=''
			assign = ''
			mobile_number = ''
			landline_number = ''
			new_address_id =''
			if o.ref_text:
				ref_name=o.ref_text
			customer_lead=''
			date1=''
			date1=str(datetime.now().date())
			conv=time.strptime(str(date1),"%Y-%m-%d")
			date1 = time.strftime("%d-%m-%Y",conv)
			customer_lead=self.pool.get('res.partner').browse(cr,uid,o.partner_id.id).name+'   Inspection / Costing Created On   '+date1
			customer_lead_date=self.pool.get('customer.logs').create(cr,uid,{'customer_join':customer_lead,'customer_id':o.partner_id.id})

			#print "###########customer log processed , with partner id",o.partner_id
			if o.lead_tracker:
				self.write(cr,uid,ids,{'check_lead_tracker':True})
			if o.id:
				self.pool.get('ccc.branch.new').write(cr,uid,o.id,{'create_entry_sales_msg':True})
			if o.request_type == 'lead_request':
				req = self.pool.get('ccc.branch.new').search(cr,uid,[('request_id','=',o.request_id)])
				for k in self.pool.get('ccc.branch.new').browse(cr,uid,req):
					today_date = datetime.now().date()
					for i in o.lead_request_line:
						form = k.id
						val = i.request_id
						exempted = i.address_id.exempted
						adhoc = i.address_id.adhoc_invoice
						cer = i.address_id.certificate_no
						premise = i.address_id.premise_type
						location_name = i.address_id.location_name
						apartment = i.address_id.apartment
						building = i.address_id.building
						assign=i.assign_resource.id
						sub_area = i.address_id.sub_area
						street = i.address_id.street
						landmark = i.address_id.landmark
						state_id = i.address_id.state_id.name if i.address_id.state_id else False
						city_id = i.address_id.city_id.name1 if i.address_id.city_id else False
						tehsil = str(i.address_id.tehsil.id) if  i.address_id.tehsil.id else False
						district = str(i.address_id.district.id) if i.address_id.district.id else False
						address=[location_name,apartment,building,sub_area,street,landmark,state_id,city_id,tehsil,district]
						addr=', '.join(filter(bool,address))
						search_lead_address= self.pool.get('new.address').search(cr,uid,[('id','>',0)])
						flag = False
						customer_line=self.pool.get('customer.line').search(cr,uid,[('customer_address','=',i.address_id.id)])
						if not i.address_id.cse:
							osv.except_osv(('Alert!'),('Please Select CSE from Customer Record')) 
						if search_lead_address:
							for record_address in self.pool.get('new.address').browse(cr,uid,search_lead_address):
								if record_address.partner_address.id == i.address_id.id:
									new_address_id = record_address.id
									flag = True
									break
						if not flag:
							new_address_id = self.pool.get('new.address').create(cr,uid,
								{
									'partner_address':i.address_id.id,
									'title':i.address_id.title,'premise_type':i.address_id.premise_type,
									'location_name':i.address_id.location_name,
									'apartment':i.address_id.apartment,'building':i.address_id.building,'sub_area':i.address_id.sub_area,
									'street':i.address_id.street,'landmark':i.address_id.landmark,
									'district':i.address_id.district.id,'zip':i.address_id.zip,
									'state_id':str(i.address_id.state_id.id if i.address_id.state_id else ''),
									'city_id':str(i.address_id.city_id.id if i.address_id.city_id else '')
								})
						quotation_master = self.pool.get('inspection.costing.master').create(cr,uid,
								{
									'customer_name':o.partner_id.name,'contact_name':o.contact_name,
									'first_name':o.first_name,'middle_name':o.middle_name,
									'last_name':o.last_name,'designation':o.designation,
									'pms':i.product_id.id,'cse':i.address_id.cse.id if i.address_id.cse else assign, #19 Nov 15 CSE History
									'premise_type':i.address_id.premise_type,'apartment':i.address_id.apartment,
									'location_name':i.address_id.location_name,
									'building':k.building,'sub_area':k.sub_area,
									'fax':i.address_id.fax,'street':i.address_id.street,
									'landmark':i.address_id.landmark,
									'city_id':i.address_id.city_id.id if i.address_id.city_id else '',
									'state_id':i.address_id.state_id.id if i.address_id.state_id else '',
									'district':i.address_id.district.id,'address_id':new_address_id
								})
						product_name=''
						record_id_list=''
						for i in o.lead_request_line:
							product_name = self.pool.get('product.product').browse(cr,uid,i.product_id.id).prod_type
						record_id_list1=''
						service_type = ''
						frequency_name = ''
						contract_cost = 0.0
						rate_check = False
						if i.product_id:
							service_type = self.pool.get('product.product').browse(cr,uid,i.product_id.id).prod_type
							product_name = self.pool.get('product.product').browse(cr,uid,i.product_id.id).name_template #Abdulrahim 22 may 
						if i.area_type and service_type in ('gss','fum'):
							area_split_list = (i.area_type.area.split('. '))
							area = area_split_list[0]
							room = area_split_list[1]
						seq_id=''
						contract_vals = {
								'gst_contract': True,
								'lead_no':val,
								'adhoc_invoice':True if i.address_id.adhoc_invoice else False,
								'cse':i.address_id.cse.id if i.address_id.cse else assign,
								'cust_name':o.partner_id.name,
								'exempted':True if i.address_id.exempted else False,
								'inquiry_type':'Service',
								'branch_id':self.pool.get('res.users').browse(cr,uid,uid).company_id.id,
								'partner_id':o.partner_id.id,
								'pms':i.product_id.id,
								'pms_line':i.product_id.name,
								'payment_term':'full_payment'
							}
						if service_type  =='gss' and i.service_rate:
							record_id_list1 = self.pool.get('sale.contract').create(cr,uid,contract_vals) 
						elif service_type =='fum':
							contract_vals.update({'fum_contract':True})                         
							record_id_list1 = self.pool.get('sale.contract').create(cr,uid,contract_vals) 
							self.pool.get('ccc.branch.new').write(cr,uid,o.id,{'check_msg_gss':True})
						else:
							today_date = datetime.now().date()
							year = today_date.year
							year1=today_date.strftime('%y')
							search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','inspection.costing')])
							seq_id=''
							if search:
								for sequence_in in self.pool.get('ir.sequence').browse(cr,uid,search):
									if sequence_in.year != year1:
										self.pool.get('ir.sequence').write(cr,uid,sequence_in.id,{'year':year1,'number_next':1})
									value_id = self.pool.get('ir.sequence').get(cr, uid, 'inspection.costing')
									pcof_key = ''
									inspection_id = ''
									company_id=self._get_company(cr,uid,context=None)
									if company_id:
										for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
											inspection_id= comp_id.inspection_id
											pcof_key = comp_id.pcof_key
									seq_id = str(pcof_key) +str(inspection_id)+ str(year1) +str(value_id)
							cust_line_obj = self.pool.get('customer.line')
							record_id_list = self.pool.get('inspection.costing').create(cr,uid,
								{
									'lead_origin':o.branch_id.name,
									'service_area_id':i.service_area.id,
									'customer_name':o.partner_id.name,
									'first_name':o.first_name,'middle_name':o.middle_name,
									'last_name':o.last_name,'designation':o.designation,
									'partner_id':o.partner_id.id,
									'lead_no':val,'company_id':self.pool.get('res.users').browse(cr,uid,uid).company_id.id,
									'contact_name':o.partner_id.name,
									'cse':i.address_id.cse.id if i.address_id.cse else assign,
									'title':o.partner_id.title if o.partner_id else '',
									'inspection_id':quotation_master,
									'premise_type':i.address_id.premise_type,'lead_date':str(datetime.now().date()),
									'building':i.address_id.building,'lead_type':o.inquiry_type,
									'street':i.address_id.street,'lead_for':'Existing Customer','lead_origin':o.branch_id.name,
									'apartment':i.address_id.apartment,
									'location_name':i.address_id.location_name,
									'service_area':i.service_area.name,
									'city_id':i.address_id.city_id.id if i.address_id.city_id else '',
									'zip':i.address_id.zip,'state_id':i.address_id.state_id.id if i.address_id.state_id else '' ,
									'district':i.address_id.district.id,'landmark':i.address_id.landmark,
									'tehsil':i.address_id.tehsil.id,
									'sub_area':i.address_id.sub_area,
									'ref_by':o.partner_id.ref_by.id if o.partner_id.ref_by else '',
									'ref_text':ref_name,
									'email':i.address_id.email,
									'fax':i.address_id.fax,'certificate_no':cer,
									'exempted':True if i.address_id.exempted else False,'adhoc_invoice':True if i.address_id.adhoc_invoice else False,
								}) 
						line_id=''
						line_id=record_id_list1
						mobile_number = ''
						landline_number=''
						area = ''
						actual_phone = ''
						actual_lstrip = ''
						actual_rstrip = ''
						room = ''
						iterate_id=''
						for iterate_id in self.pool.get('inspection.costing').browse(cr,uid,[record_id_list]):
							iterate_id=iterate_id.id
							if o.partner_id:
								lead_partner_id = self.pool.get('phone.m2m').search(cr,uid,[('res_location_id','=',i.address_id.id)])
								count = 0
								for iter_id in self.pool.get('phone.m2m').browse(cr,uid,lead_partner_id):
										if len(lead_partner_id) > 1:
											if iter_id.type ==  'mobile':
												if count != len(lead_partner_id)-1 :
													mobile_number += iter_id.name+','
												else:
													mobile_number += iter_id.name
											if iter_id.type ==  'landline':
												if count != len(lead_partner_id)-1 :
													if count == 0:
														landline_number += iter_id.name
													else:
														landline_number += iter_id.name+','
												else:
													landline_number += iter_id.name
										else:
											if iter_id.type ==  'mobile':
												mobile_number = iter_id.name
											if iter_id.type ==  'landline':
												landline_number = iter_id.name  
										count += 1
										actual_phone = landline_number+','+ mobile_number
										actual_rstrip = actual_phone.rstrip(',')
										actual_lstrip = actual_rstrip.lstrip(',')
							self.pool.get('inspection.costing').write(cr,uid,record_id_list,{'phone':actual_lstrip})
						service_type = ''
						frequency_name = ''
						contract_cost = 0.0
						rate_check = False
						if i.product_id:
							service_type = self.pool.get('product.product').browse(cr,uid,i.product_id.id).prod_type
							product_name = self.pool.get('product.product').browse(cr,uid,i.product_id.id).name_template #Abdulrahim 22 may 
						if i.service_frequency:
							frequency_name = i.service_frequency.name
						if  service_type =='gss' and i.address_id.premise_type == 'flat_apartment' and i.service_rate or (service_type == 'carpro' and i.address_id.premise_type == 'car_pro' and i.service_rate):
							rate_check = True
							contract_cost = i.service_rate
						else:
							rate_check = False 
						if  service_type in ('gss','fum') and i.service_rate:
							self.pool.get('ccc.branch.new').write(cr,uid,o.id,{'check_msg_gss':True})
						discount_amount=''
						amount=''
						if i.service_rate and i.campaign_discount:
							discount_amount=float((i.service_rate*i.campaign_discount)/100)
							amount=(i.service_rate - discount_amount)
						elif i.service_rate and i.campaign_disc_amnt:
							amount=(i.service_rate - i.campaign_disc_amnt)
						else:
							amount=i.service_rate
						if i.area_sq_mt:
							area=i.area_sq_mt
						elif i.no_of_trees:
							area=i.no_of_trees 
						else: 
							area=''
						new_address_data = self.pool.get('new.address').browse(cr,uid,new_address_id)
						addrs_items = []
						long_address = ''
						if new_address_data.apartment not in [' ',False,None]:
							addrs_items.append(new_address_data.apartment)
						if new_address_data.location_name not in [' ',False,None]:
							addrs_items.append(new_address_data.location_name)
						if new_address_data.building not in [' ',False,None]:
							addrs_items.append(new_address_data.building)
						if new_address_data.sub_area not in [' ',False,None]:
							addrs_items.append(new_address_data.sub_area)
						if new_address_data.street not in [' ',False,None]:
							addrs_items.append(new_address_data.street)
						if new_address_data.landmark not in [' ',False,None]:
							addrs_items.append(new_address_data.landmark)
						if new_address_data.city_id:
							addrs_items.append(new_address_data.city_id.name1)
						if new_address_data.district:
							addrs_items.append(new_address_data.district.name)
						if new_address_data.tehsil:
							addrs_items.append(new_address_data.tehsil.name)
						if new_address_data.state_id:
							addrs_items.append(new_address_data.state_id.name)
						if new_address_data.zip not in [' ',False,None]:
							addrs_items.append(new_address_data.zip)
						if len(addrs_items) > 0:
							last_item = addrs_items[-1]
							for item in addrs_items:
								if item!=last_item:
									long_address = long_address+item+','+' '
								if item==last_item:
									long_address = long_address+item
						if long_address:
							complete_address = '['+long_address+']'
						else:
							complete_address = ' '
						product_full_name = i.product_id.product_desc or ''
						services = product_full_name.upper() + ' '+complete_address
						if o.partner_id.nature == True:
							nature = True
						else:
							nature = False
						self.pool.get('inspection.costing.line').create(cr,uid,
							{
								'address_new':new_address_id,
								'area':area,
								'rooms':room,
								'rate':i.service_rate if not area else '',
								'estimated_contract_rate':contract_cost,
								'rate_check':rate_check,
								'inspection_no':seq_id,
								'tspr_inspection_no':seq_id,
								'pps_inspection_no':seq_id,
								'tspo_inspection_no':seq_id,
								'inspection_line_id':iterate_id,
								'requested_date':i.requested_date,
								'premise_type':i.address_id.premise_type,
								'service_frequency':i.service_frequency.id,
								'inspector_name':i.address_id.cse.id,
								'phone':landline_number,
								'mobile':mobile_number,
								'building':i.address_id.building,'lead_type':o.inquiry_type,
								'street':i.address_id.street,'lead_for':'Lead','lead_origin':o.branch_id.name,
								'apartment':i.address_id.apartment,
								'location_name':i.address_id.location_name,
								'service_area_form':i.service_area.name,
								'city_id':i.address_id.city_id.id if i.address_id.city_id else '',
								'zip':i.address_id.zip,'state_id':i.address_id.state_id.id if i.address_id.state_id else '' ,
								'area_type':i.area_type.id,
								'cost_rate':'rate_chart' if i.area_type else '',
								'service_frequency_area_type':i.service_frequency.id,
								'landmark':i.address_id.landmark,
								'district':i.address_id.district.id,
								'landmark':i.address_id.landmark,
								'tehsil':i.address_id.tehsil.id,
								'sub_area':i.address_id.sub_area,
								'email':i.address_id.email,
								'ref_by':o.ref_by.id,
								'fax':i.address_id.fax,
								'service_area':i.service_area.id,
								'solution_off':i.product_id.id,
								'solution_frequency':i.service_frequency.id,
								'pms':i.product_id.id,
								'description':product_name,
								'estimated_contract_cost':amount,
								'name':o.partner_id.name,
								'no_of_services':i.no_of_services,
								'no_of_inspections':i.no_of_inspections,
								'location_check':True,
								'name':o.partner_id.name,
								'rate_check':rate_check,
								'bps_name':o.partner_id.name,
								'name':o.partner_id.name,
								'tspr_inspector_name':i.address_id.cse.id,
								'bps_inspector_name':i.address_id.cse.id,
								'pps_inspector_name':i.address_id.cse.id,
								'gss_inspector_name':i.address_id.cse.id,
								'bps_email':o.email,
								'bps_phone':landline_number.rstrip(','),
								'bps_mobile':mobile_number.rstrip(','),
								'mobile':mobile_number,
								'phone':landline_number,
								'gss_customer_name':o.name,
								'gss_solution_off':i.product_id.id,
								'gss_solution_frequency':i.service_frequency.id,
								'gss_phone':landline_number.rstrip(','),
								'gss_mobile':mobile_number.rstrip(','),
								'gss_email':o.email,
								'gss_inspector_name':i.assign_resource.id,
								'tspo_customer_name':o.name,
								'tspo_solution_off':i.product_id.id,
								'tspo_solution_frequency':i.service_frequency.id,
								'tspo_phone':landline_number.rstrip(','),
								'tspo_mobile':mobile_number.rstrip(','),
								'tspo_email':o.email,
								'tspo_person_to_meet':o.name,
								'tspo_inspector_name':i.address_id.cse.id,  
								'tspr_customer_name':o.name,
								'tspr_solution_off':i.product_id.id,
								'tspr_phone':landline_number.rstrip(','),
								'tspr_mobile':mobile_number.rstrip(','),
								'tspr_email':o.email,
								'tspr_inspector_name':i.address_id.cse.id,
								'pps_customer_name':o.name,
								'pps_phone':landline_number.rstrip(','),
								'pps_mobile':mobile_number.rstrip(','),
								'pps_email':o.email,
								'pps_inspector_name':i.address_id.cse.id,
								'discount_flat_gss':i.campaign_discount,
								'discount_amount':i.discount_amount_gss,
								'remark':i.remark,
								'scheme_name':i.scheme_name.id, 
								'campaign_discount':i.campaign_discount if i.campaign_discount else 0.0,
								'campaign_disc_amnt':i.campaign_disc_amnt if i.campaign_disc_amnt else 0.0,
								'campaign_discount_readonly':i.campaign_discount if i.campaign_discount else 0.0,
								'campaign_disc_amnt_readonly':i.campaign_disc_amnt if i.campaign_disc_amnt else 0.0,
								'contract_id1':line_id,
								'contract_id12':line_id,
								'campaign_disc_flag':True if i.campaign_disc_amnt else '',
								'rates_with_tax':i.rates_with_tax,
								'tspo_refer_by':o.ref_by.id,
								'tspo_refer_by_name':o.ref_text if o.ref_text else '',
								'refer_by':o.ref_by.id,
								'other_refer_by_name':o.ref_text if o.ref_text else '',
								'tspr_refer_by':o.ref_by.id,
								'tspr_refer_by_name':o.ref_text if o.ref_text else '',
								'pps_refer_by':o.ref_by.id,
								'pps_refer_by_name':o.ref_text if o.ref_text else '',
								'cse_inspection':i.address_id.cse.id if i.address_id.cse else i.assign_resource.id, #19 Nov 15 
								'cse_contract':i.address_id.cse.id if i.address_id.cse else i.assign_resource.id, #19 Nov 15 
								'type_of_service':i.type_of_service,
								'area_sq_mt':i.area_sq_mt,
								'no_of_trees':i.no_of_trees,
								'boolean_pms_tg':i.boolean_pms_tg,
								'processed':True,
								'services': services,
								'hsn_code': i.product_id.hsn_sac_code,
								'discount': 0,
								'taxable_value':amount,
								'nature': nature
							})
					for iterate in k.comment_line:
						date=datetime.now()
						self.pool.get('comment.line').create(cr,uid,{'comment_line_id':record_id_list,'user_name':iterate.user_id,'comment_date':datetime.now().date(),'comment':iterate.comment})
					return True
			if o.request_type == 'new_cust':
				for i in o.new_customer_location:
					product_name=i.product_id.prod_type
				search_id=''    
				contact_landline_number=''
				contact_landline_number_new=''
				search_id=self.pool.get('phone.number.child.new').search(cr,uid,[('partner_id_new_cust','=',o.id)])
				for rec in self.pool.get('phone.number.child.new').browse(cr,uid,search_id):
					contact_landline_number=rec.number
					if rec.contact_select=='landline':
						contact_landline_number_new=rec.number
				flag = False
				new_address_id = ''
				today_date = datetime.now().date()
				customer_line = 0
				record_id_list = ''
				for k in o.new_customer_location:
						form = k.id
						partner_address_id1 =   self.pool.get('res.partner.address').browse(cr,uid,int(k.location_id))
						if k.assign_resource.role_selection != 'cse':
							if not partner_address_id1.cse:
								raise osv.except_osv(('Alert!'),('Please Select CSE from Customer Record'))
						val = k.request_id
						assign = k.assign_resource.id
						premise = k.new_customer_address_id.premise_type
						apartment = k.new_customer_address_id.apartment
						location_name = k.new_customer_address_id.location_name
						building = k.new_customer_address_id.building
						sub_area = k.new_customer_address_id.sub_area
						street = k.new_customer_address_id.street
						landmark = k.new_customer_address_id.landmark
						state_id = k.new_customer_address_id.state_id.name if k.new_customer_address_id.state_id else False 
						city_id = k.new_customer_address_id.city_id.name1 if k.new_customer_address_id.city_id else False
						tehsil = str(k.new_customer_address_id.tehsil.id)
						district =str(k.new_customer_address_id.district.id)
						address=[location_name,apartment,building,sub_area,street,landmark,state_id,city_id,tehsil,district]
						addr=', '.join(filter(bool,address))
						search_new_address= self.pool.get('new.address').search(cr,uid,[('id','>',0)])
						flag_1 = False
						if search_new_address:
							for record_address in self.pool.get('new.address').browse(cr,uid,search_new_address):
								if record_address.partner_address.id == int(k.location_id):
									new_address_id = record_address.id
									flag_1 = True
									break
						if not flag_1:
							cr.execute('select cc.customer_address from customer_line cc where partner_id =%(val)s',{'val':o.partner_id.id})    
							var = cr.fetchone()[0]
							new_address_id = self.pool.get('new.address').create(cr,uid,
								{
									'partner_address':k.location_id,
									'name':k.new_customer_address_id.name,
									'title':k.new_customer_address_id.title,
									'premise_type':k.new_customer_address_id.premise_type,
									'location_name':k.new_customer_address_id.location_name,
									'apartment':k.new_customer_address_id.apartment,
									'building':k.new_customer_address_id.building,
									'sub_area':k.new_customer_address_id.sub_area,
									'street':k.new_customer_address_id.street,
									'landmark':k.new_customer_address_id.landmark,
									'tehsil':k.new_customer_address_id.tehsil.id,
									'district':k.new_customer_address_id.district.id,
									'zip':k.new_customer_address_id.zip,
									'state_id':str(k.new_customer_address_id.state_id.id) if k.new_customer_address_id.state_id else '',
									'city_id':str(k.new_customer_address_id.city_id.id) if k.new_customer_address_id.city_id else ''
								})
							flag_1 = True
						record_id_list1=''
						seq_id=''
						service_type = ''
						frequency_name = ''
						contract_cost = 0.0
						rate_check = False
						if i.product_id:
							service_type = self.pool.get('product.product').browse(cr,uid,i.product_id.id).prod_type
							product_name = self.pool.get('product.product').browse(cr,uid,i.product_id.id).name_template #Abdulrahim 22 may 
						partner_address_obj = self.pool.get('res.partner.address')
						partner_address_id =    self.pool.get('res.partner.address').browse(cr,uid,int(k.location_id))
						fum_contract=False
						if service_type=='gss' and k.service_rate:
							record_id_list1 = self.pool.get('sale.contract').create(cr,uid,
								{
									'gst_contract': True,
									'lead_no':val,
									'adhoc_invoice':True if partner_address_id.adhoc_invoice else False,
									'exempted':True if partner_address_id.exempted else False,
									'cse':partner_address_id.cse.id if partner_address_id.cse else assign,
									'fum_contract':fum_contract,
									'cust_name':o.partner_id.name,
									'inquiry_type':'Service',
									'payment_term':'full_payment',
									'branch_id':self.pool.get('res.users').browse(cr,uid,uid).company_id.id,
									'partner_id':o.partner_id.id,
									'pms':i.product_id.id,
									'pms_line':i.product_id.name,
								}) 
							self.pool.get('ccc.branch.new').write(cr,uid,o.id,{'check_msg_gss':True})   
						elif service_type=='fum':
							fum_contract=True
							record_id_list1 = self.pool.get('sale.contract').create(cr,uid,
								{
									'gst_contract': True,
									'lead_no':val,
									'adhoc_invoice':True if partner_address_id.adhoc_invoice else False,
									'exempted':True if partner_address_id.exempted else False,
									'cse':partner_address_id.cse.id if partner_address_id.cse else assign,
									'fum_contract':fum_contract,
									'cust_name':o.partner_id.name,
									'inquiry_type':'Service',
									'payment_term':'full_payment',
									'branch_id':self.pool.get('res.users').browse(cr,uid,uid).company_id.id,
									'partner_id':o.partner_id.id,
									'pms':i.product_id.id,
									'pms_line':i.product_id.name,
								}) 
							self.pool.get('ccc.branch.new').write(cr,uid,o.id,{'check_msg_gss':True})
						else:
							today_date = datetime.now().date()
							year = today_date.year
							year1=today_date.strftime('%y')
							search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','inspection.costing')])
							if search:
								for i in self.pool.get('ir.sequence').browse(cr,uid,search):
									if i.year != year1:
										self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year1,'number_next':1})
									value_id = self.pool.get('ir.sequence').get(cr, uid, 'inspection.costing')
									pcof_key = ''
									inspection_id = ''
									company_id=self._get_company(cr,uid,context=None)
									if company_id:
										for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
											inspection_id= comp_id.inspection_id
											pcof_key = comp_id.pcof_key
									seq_id = str(pcof_key) +str(inspection_id)+ str(year1) +str(value_id)
							record_id_list = self.pool.get('inspection.costing').create(cr,uid,
								{
									'lead_no':val,
									'company_id':self.pool.get('res.users').browse(cr,uid,uid).company_id.id,
									'lead_date':today_date,
									'lead_origin':o.origin.name,
									'service_area_id':k.service_area.id,
									'cse':partner_address_id.cse.id if partner_address_id.cse else assign,
									'lead_type':o.inquiry_type,
									'lead_for':'New Customer','first_name':o.first_name,'middle_name':o.middle_name,'last_name':o.last_name,                                                                    'designation':o.designation,
									'customer_name':o.name,
									'contact_name':o.contact_name,
									'title':o.title,
									'email':o.email,
									'premise_type':o.premise_type,
									'building':o.building,
									'apartment':o.apartment,
									'location_name':o.location_name,
									'sub_area':o.sub_area,
									'street':o.street,
									'state':'open',
									'service_area':k.service_area.name,
									'fax':o.fax,
									'landmark':o.landmark,
									'total_cost':k.service_rate,
									'tehsil':o.tehsil.id,
									'ref_by':o.ref_by.id,
									'ref_text':ref_name,
									'state_id':o.state_id.id if o.state_id else '',
									'city_id':o.city_id.id if o.city_id else '',
									'district':o.district.id,
									'zip':o.zip,'partner_id':o.partner_id.id,
									'contact_landline_no':contact_landline_number_new,'adhoc_invoice':True if partner_address_id.adhoc_invoice else False,
									'exempted':True if partner_address_id.exempted else False,          
									'type_of_service':k.type_of_service,
									'area_sq_mt':k.area_sq_mt,
									'no_of_trees':k.no_of_trees,
									'boolean_pms_tg':k.boolean_pms_tg,
								}) 
						line_id=''  
						line_id=record_id_list1
						line_id=record_id_list1
						for comment in o.comment_line_new:
							self.pool.get('comment.line').create(cr,uid,{'user_name':comment.user_id,'comment_date':comment.comment_date,'comment':comment.comment,'comment_line_id':record_id_list})
						iterate_id=''
						landline_number=''
						mobile_number=''
						actual_phone = ''
						actual_number = ''
						actual_rstrip = ''
						actual_lstrip =''
						area = ''
						room =''
						for iterate_id in self.pool.get('inspection.costing').browse(cr,uid,[record_id_list]):
									iterate_id=iterate_id.id
									if o.partner_id:
										lead_partner_id = self.pool.get('phone.m2m').search(cr,uid,[('ccc_new_address_id','=',k.new_customer_address_id.id)])
										count = 0
										for iter_id in self.pool.get('phone.m2m').browse(cr,uid,lead_partner_id):
											if len(lead_partner_id) > 1:
												if iter_id.type ==  'mobile':
													if count != len(lead_partner_id)-1 :
														mobile_number += iter_id.name+','
													else:
														mobile_number += iter_id.name
												else :
													if count != len(lead_partner_id)-1 :
														landline_number += iter_id.name+','
													else:
														landline_number += iter_id.name
											else:
												if iter_id.type ==  'mobile':
													mobile_number = iter_id.name
												else:
													landline_number = iter_id.name  
											count += 1
											actual_phone = landline_number+','+ mobile_number
											actual_rstrip = actual_phone.rstrip(',')
											actual_lstrip = actual_rstrip.lstrip(',')
									self.pool.get('inspection.costing').write(cr,uid,record_id_list,{'phone':actual_lstrip})
						service_type = ''
						frequency_name = ''
						contract_cost = 0.0
						rate_check = False
						if k.product_id:
							service_type = self.pool.get('product.product').browse(cr,uid,k.product_id.id).prod_type
							product_name = self.pool.get('product.product').browse(cr,uid,k.product_id.id).name_template #Abdulrahim 22 may 
						if k.service_frequency:
							frequency_name = k.service_frequency.name
						if  service_type in ('gss','fum') or (service_type == 'carpro' and o.premise_type == 'car_pro' and k.service_rate):
							rate_check = True
							contract_cost = k.service_rate
						else:
								rate_check = False
						if k.area_type and (service_type in ('gss','fum')):
							area_split_list = (k.area_type.area.split('. '))
							area = area_split_list[0]
							room = area_split_list[1]
						discount_amount=''
						amount=''   
						if k.service_rate and k.campaign_discount:
							discount_amount=float((k.service_rate*k.campaign_discount)/100)
							amount=(k.service_rate - discount_amount)
						elif k.service_rate and k.campaign_disc_amnt:                   
							amount=(k.service_rate - k.campaign_disc_amnt)
						else:
							amount=k.service_rate
						if k.area_sq_mt:
							area=k.area_sq_mt
						elif k.no_of_trees:
							area=k.no_of_trees 
						else: 
							area=''
						new_address_data = self.pool.get('new.address').browse(cr,uid,new_address_id)
						addrs_items = []
						long_address = ''   
						if new_address_data.apartment not in [' ',False,None]:
							addrs_items.append(new_address_data.apartment)
						if new_address_data.location_name not in [' ',False,None]:
							addrs_items.append(new_address_data.location_name)
						if new_address_data.building not in [' ',False,None]:
							addrs_items.append(new_address_data.building)
						if new_address_data.sub_area not in [' ',False,None]:
							addrs_items.append(new_address_data.sub_area)
						if new_address_data.street not in [' ',False,None]:
							addrs_items.append(new_address_data.street)
						if new_address_data.landmark not in [' ',False,None]:
							addrs_items.append(new_address_data.landmark)
						if new_address_data.city_id:
							addrs_items.append(new_address_data.city_id.name1)
						if new_address_data.district:
							addrs_items.append(new_address_data.district.name)
						if new_address_data.tehsil:
							addrs_items.append(new_address_data.tehsil.name)
						if new_address_data.state_id:
							addrs_items.append(new_address_data.state_id.name)
						if new_address_data.zip not in [' ',False,None]:
							addrs_items.append(new_address_data.zip)
						if len(addrs_items) > 0:
							last_item = addrs_items[-1]
							for item in addrs_items:
								if item!=last_item:
									long_address = long_address+item+','+' '
								if item==last_item:
									long_address = long_address+item
						if long_address:
							complete_address = '['+long_address+']'
						else:
							complete_address = ' '
						product_full_name = k.product_id.product_desc or ''
						services = product_full_name.upper() + ' '+complete_address
						inspection_id=self.pool.get('inspection.costing.line').create(cr,uid,
							{
								'address_new':new_address_id,
								'area':area ,
								'rooms':room,
								'rate':k.service_rate if not area else '',
								'inspection_line_id':iterate_id,
								'inspection_no':seq_id,
								'tspr_inspection_no':seq_id,
								'pps_inspection_no':seq_id,
								'tspo_inspection_no':seq_id,
								'premise_type':o.premise_type,
								'building':o.building,
								'street':o.street,
								'apartment':o.apartment,
								'location_name':o.location_name,
								'service_area_form':k.service_area.name,
								'city_id':o.city_id.id if o.city_id else '',                                                        'landmark':o.landmark,
								'area_type':k.area_type.id if k.area_type else '',
								'service_frequency_area_type':k.service_frequency.id if k.service_frequency else '',
								'zip':o.zip,'state_id':o.state_id.id if o.state_id else '',
								'district':o.district.id,
								'tehsil':o.tehsil.id,
								'sub_area':o.sub_area,
								'requested_date':k.requested_date,
								'name':o.name,
								'email':o.email,
								'service_frequency':k.service_frequency.id,
								'estimated_contract_rate':contract_cost,
								'inspector_name':partner_address_id.cse.id,
								'phone':landline_number,
								'mobile':mobile_number,
								'solution_off':k.product_id.id,
								'solution_frequency':k.service_frequency.id,
								'mobile':mobile_number,
								'cost_rate':'rate_chart' if k.area_type else '',
								'no_of_inspections':k.no_of_inspections,
								'no_of_services':k.no_of_services,
								'service_area':k.service_area.id,
								'pms':k.product_id.id,
								'description':product_name,        
								'estimated_contract_cost':amount,
								'location_check':True,
								'rate_check':rate_check,
								'bps_name':o.contact_name,
								'bps_email':o.email,
								'bps_phone':landline_number,
								'bps_mobile':mobile_number,
								'gss_customer_name':o.name,
								'gss_solution_off':k.product_id.id,
								'gss_solution_frequency':k.service_frequency.id,
								'gss_phone':landline_number,
								'gss_mobile':mobile_number,
								'gss_email':o.email,
								'gss_inspector_name':partner_address_id.cse.id,
								'tspo_customer_name':o.name,
								'tspo_solution_off':k.product_id.id,
								'tspo_solution_frequency':k.service_frequency.id,
								'tspo_phone':landline_number,
								'tspo_mobile':mobile_number,
								'tspo_email':o.email,
								'tspo_inspector_name':partner_address_id.cse.id,
								'tspr_customer_name':o.name,
								'tspr_solution_off':k.product_id.id,
								'tspr_phone':landline_number,
								'tspr_mobile':mobile_number,
								'tspr_email':o.email,
								'tspr_inspector_name':partner_address_id.cse.id,
								'pps_customer_name':o.name,
								'pps_phone':landline_number,
								'pps_mobile':mobile_number,
								'pps_email':o.email,
								'pps_inspector_name':partner_address_id.cse.id,
								'contact_landline_no':contact_landline_number_new,
								'bps_phone':contact_landline_number_new,
								'gss_phone':contact_landline_number_new,
								'tspo_phone':contact_landline_number_new,
								'tspr_phone':contact_landline_number_new,
								'pps_phone':contact_landline_number_new,
								'phone':contact_landline_number_new,
								'discount_flat_gss':k.discount_flat_gss,
								'discount_amount':k.discount_amount_gss,
								'tspo_person_to_meet':o.name,
								'pps_person_to_meet':o.name,
								'tspr_person_to_meet':o.name,
								'person_to_meet':o.name,
								'remark':k.remark,  
								'scheme_name':k.scheme_name.id,
								'campaign_discount':k.campaign_discount if k.campaign_discount else 0.0,
								'campaign_disc_amnt':k.campaign_disc_amnt if k.campaign_disc_amnt else 0.0,
								'campaign_discount_readonly':k.campaign_discount if k.campaign_discount else 0.0,
								'campaign_disc_amnt_readonly':k.campaign_disc_amnt if k.campaign_disc_amnt else 0.0,
								'campaign_disc_flag':True if k.campaign_disc_amnt else '',
								'contract_id1':line_id,
								'contract_id12':line_id,
								'discount_flat_gss':k.campaign_discount,
								'discount_amount':amount,
								'rates_with_tax':k.rates_with_tax,
								'tspo_refer_by':o.ref_by.id,
								'tspo_refer_by_name':o.ref_text if o.ref_text else '',
								'refer_by':o.ref_by.id,
								'other_refer_by_name':o.ref_text if o.ref_text else '',
								'tspr_refer_by':o.ref_by.id,
								'tspr_refer_by_name':o.ref_text if o.ref_text else '',
								'pps_refer_by':o.ref_by.id,
								'pps_refer_by_name':o.ref_text if o.ref_text else '',
								'cse_inspection':partner_address_id.cse.id if partner_address_id.cse else assign, #19 Nov 15 
								'cse_contract':partner_address_id.cse.id if partner_address_id.cse else assign, #19 Nov 15 
								'type_of_service':k.type_of_service,
								'area_sq_mt':k.area_sq_mt,
								'no_of_trees':k.no_of_trees,
								'boolean_pms_tg':k.boolean_pms_tg,
								'processed':True,
								'services': services,
								'hsn_code': k.product_id.hsn_sac_code,
								'discount': 0,
								'taxable_value':amount,
							})
				status_track_date = datetime.now().date()
				self.write(cr,uid,o.id,{'status_track_date':status_track_date})  
				return True
			if o.request_type == 'renewal_request':
				for renewal in o.lead_renewal_line:
					search_contract = self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',renewal.name)])        
					for iterate in  self.pool.get('sale.contract').browse(cr,uid,search_contract):  
						self.pool.get('sale.contract').write(cr,uid,iterate.id,{'renewal_amt':iterate.renewal_amt})
						return {
								'type': 'ir.actions.act_window',
								'name': 'Contract',
								'view_mode': 'form',
								'view_type': 'form',
								'view_id': False,
								'res_id':iterate.id,
								'res_model':'sale.contract',
								'target':'current',
							}
ccc_branch_new()


class ccc_sync_lead_request(osv.osv):
	_inherit = 'res.partner.branch.new'

	def process_customer(self,cr,uid,ids,context=None):
		created_by =  self.pool.get('res.users').browse(cr,uid,uid).name
		conn_flag = False
		curr_id = []
		curr_id = ids
		crm_obj = self.pool.get('crm.lead')
		customer_obj = self.pool.get('customer.line')
		customer_request_obj =self.pool.get('ccc.branch.new')
		request_date=datetime.now().date()
		count = 0
		date=datetime.now()
		request_type='lead_request'
		note=''
		branch=''
		addresses=[]
		list_id=[]
		telephonic = []
		temp_comment_line = []
		lead_list = []
		lead_crm = []
		vpn_ip_addr = ''
		port=''
		dbname = ''
		pwd = ''
		login_id= ''
		list_id = []
		main_partner = []
		phone_list_id = []
		branch_address_id = []
		count_address = []
		partner_list = []
		customer_location_id = []
		branch_id_list = []
		customer_location_id_list = []
		post = []	
		branch_partner_id = ''
		customer_flag = False
		count_location = 0
		list_id = []
		location_id = ''
		branch_list = []
		ccc_new_address_id = ''
		customer_create_id = False
		user_name = ''
		area = False
		customer_address = False
		branch_dict = {
			'customer_create_id':'',
			'address_id':[],
			'customer_location_id_list':[],
			'customer_flag':False,
			'branch_partner_id':'',
			'location_id':'',
			'branch_address_id':[],
			'branch_id_list':[],
			'req_id':'',
			'partner_list':[],
		}
		branch_dict_main = {
			'customer_create_id':'',
			'address_id':[],
			'customer_location_id_list':[],
			'customer_flag':False,
			'branch_partner_id':'',
			'location_id':'',
			'branch_address_id':[],
			'branch_id_list':[],
			'req_id':'',
			'partner_list':[],
		}
		post_branch = []
		post_branch_loc = []
		ids2 = False
		address_id = False
		state_ids = []
		for rec in self.browse(cr,uid,ids):
			if not rec.city_id:
				raise osv.except_osv(('Alert!'),('Please select City.'))
			if not rec.state_id:
				raise osv.except_osv(('Alert!'),('Please select State.'))
			for line_in in rec.branch_new_customer_location_service_line:
				if not line_in.service_frequency :
					raise osv.except_osv(('Alert!'),('Please Select Service Frequency.'))
				if not line_in.pms_id:
					raise osv.except_osv(('Alert!'),('Please select PMS.'))
				temp_in1=line_in.customer_address.id
				temp_in2=line_in.branch.id
				temp_in3=tuple([temp_in1]+[temp_in2])
				post_branch_loc.append(temp_in3)
				for p1 in range(0,len(post_branch_loc)):	
					for q1 in range(p1+1,len(post_branch_loc)):
						if post_branch_loc[p1][0]==post_branch_loc[q1][0]:
							if post_branch_loc[p1][1]!=post_branch_loc[q1][1]:
								raise osv.except_osv(('Alert!'),('Same Location with Differnt Branch cannot be Selected.'))
			for service in rec.branch_new_customer_location_service_line:
				if service.no_service==0 and service.no_inspection==0:
					raise osv.except_osv(('Alert!'),('Must Enter Inspections or Services.'))
			post_branch= []
			for location_line in rec.branch_new_customer_location_service_line:
				state_id = location_line.customer_address.state_id.id
				state_ids.append(state_id)
			state_ids = set(state_ids)
			state_ids = list(state_ids)
			if len(state_ids) > 1:
				raise osv.except_osv(('Alert!'),('Delivery addresses will be belong to single state only!')) 
			for pms_in in rec.branch_new_customer_location_service_line:
					temp_in1=pms_in.customer_address.id
					temp_in2=pms_in.pms_id.id
					temp_in3=tuple([temp_in1]+[temp_in2])
					post_branch.append(temp_in3)
					for p in range(0,len(post_branch)):	
						for q in range(p+1,len(post_branch)):
							if post_branch[p][0]==post_branch[q][0]:
								if post_branch[p][1]==post_branch[q][1]:
									raise osv.except_osv(('Alert!'),('Duplicate PMS for same address is not allowed.'))
			for x in rec.partner_id.branch_customer_request_line :
				lead_list.extend([x.id])
			for jk in rec.partner_id.opportunity_ids :
				lead_crm.extend([jk.id])
			partner_id = rec.partner_id.id
			if not rec.branch_new_customer_location_service_line:
				raise osv.except_osv(('Alert!'),('Please create Locations & Services to process Lead Request.'))
			for line in rec.branch_new_customer_location_service_line:
				if line.customer_address:
					partner = self.pool.get('res.partner').search(cr,uid,[('id','=',partner_id)])
					for part in self.pool.get('res.partner').browse(cr,uid,partner):
						for ln in part.new_customer_location_service_line:
							if ln.customer_address.id == line.customer_address.id:
								addresses.append(line.customer_address.id)
								for address in addresses:
									self.pool.get('res.partner.address').write(cr,uid,[address],{'partner_id':rec.partner_id.id})
		count = 0
		for var in self.browse(cr,uid,ids):
			company = self.pool.get('res.users').browse(cr,uid,uid).company_id.name
			location =''
			form = var.id
			partner_id = var.partner_id.id
			customer_category_id = var.customer_category_id.id
			aaa = self.pool.get('res.partner').search(cr,uid,[('id','=',partner_id)])
			phone_m2m = {'type':'', 'name':'', 'res_active':True}
			for jj in self.pool.get('res.partner').browse(cr,uid,aaa):
				lead_req_id = ''
				ids = jj.id
				contact_nos=[var.mobile,var.phone]
				contact_no=', '.join(filter(bool,contact_nos))
				for s in var.branch_new_customer_location_service_line:
					seq_ids = ''
					if s.branch.id == var.partner_id.company_id.id or s.branch.name == 'Branch Unknown' or not s.branch:
						req_ids = self.pool.get('ir.sequence').get(cr, uid, 'ccc.branch.new.code')
						cust_id = self.pool.get('res.partner').browse(cr,uid,jj.id).customer_id_main
						ou_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
						prefix = self.pool.get('res.users').browse(cr,uid,uid).company_id.lead_prefix_id
						record_search=self.pool.get('ccc.branch.new').search(cr,uid,[('partner_id','=',var.partner_id.id),('request_id','!=',False)])
						record_val= str(len(record_search)+1)
						total_len_count = len(ou_id)+len(prefix)+len(cust_id)+1
						required_count=18-total_len_count
						seq_ids = ou_id+prefix+cust_id+str(record_val).zfill(required_count)
						phone_number_ids = ''
						search_phone_id = self.pool.get('phone.m2m').search(cr,uid,[('res_location_id','=',s.customer_address.id)])	
						b = self.pool.get('ccc.branch.new').create(cr,uid,{'partner_id':jj.id,
											'name':jj.name,
											'branch_id':s.branch.id,
											'request_date':var.request_date if str(var.request_date) else str(datetime.now()),
											'pan_no':jj.pan_no,
											'request_type':'lead_request',
											'user_name':created_by,
											'user_id':uid,
											'origin':self.pool.get('res.users').browse(cr,uid,uid).company_id.id,
											'call_type':var.call_type,
											'activity_type':var.activity_type,
											'title':jj.title,
											'contact_name':jj.contact_name,
											'first_name':jj.first_name,
											'middle_name':jj.middle_name,
											'last_name':jj.last_name,
											'designation':jj.designation,
											'premise_type':jj.premise_type,
											'location_name':s.customer_address.location_name,#abhi
											'apartment':s.customer_address.apartment,
											'building':s.customer_address.building,
											'sub_area':s.customer_address.sub_area,
											'street':s.customer_address.street,'phone_m2o':search_phone_id[0] if search_phone_id else '',
											'landmark':s.customer_address.landmark,
											'tehsil':s.customer_address.tehsil.id if s.customer_address.tehsil else '',
											'zip':s.customer_address.zip,
											'district':s.customer_address.district.id if s.customer_address.district else '',
											'email':jj.email,
											'fax':jj.fax,
											'city_id':s.customer_address.city_id.id if s.customer_address.city_id else '',
											'state_id':s.customer_address.state_id.id if s.customer_address.state_id else '',
											'ref_by':jj.ref_by.id,
											'ref_by_name':jj.ref_by_name,
											'lead_desc':var.lead_desc,
											'lead_tracker':var.lead_tracker,
											'check_pci_tec':var.check_pci_tec,
											'lead_data_id':var.lead_data_id,
											'check_lead_tracker':var.check_lead_tracker,
											'submitter_empcode':var.submitter_empcode,
											'status_track_date':datetime.now().date(),
											'request_id':seq_ids,'state':'open' if s.branch.name != 'Branch Unknown' and s.branch else 'new',										},context=context)

						if var.request_date and var.lead_tracker:
							cr.execute("update ccc_branch_new set request_date = '%s' where id =%s "%(var.request_date,b))
						self.pool.get('customer.branch.lead.line').create(cr,uid,{
											'branch_id':s.branch.id,
											'service_frequency':s.service_frequency.id,
											'request_id':seq_ids,
											'address_id':s.customer_address.id,
											'product_id':s.pms_id.id,
											'lead_id':b,
											'service_area':s.service_area.id,
											'no_of_services':s.no_service,
											'no_of_inspections':s.no_inspection,
											'requested_date':s.requested_date,
											'service_rate':s.service_rate,
											'area_type':s.area_type.id,
											'discount_flat_gss':s.discount_flat_gss,	
											'discount_amount_gss':s.discount_amount_gss,
											'remark':s.remark,
											'rates_with_tax':s.rates_with_tax,
											'scheme_name':s.scheme_name.id,
											'campaign_discount':s.campaign_discount if s.campaign_discount else 0.0,
											'campaign_disc_amnt':s.campaign_disc_amnt if s.campaign_disc_amnt else 0.0,
											'state':'open' if s.branch.name != 'Branch Unknown' and s.branch else 'new',
											'type_of_service':s.type_of_service,
											'area_sq_mt':s.area_sq_mt,
											'no_of_trees':s.no_of_trees,
											'boolean_pms_tg':s.boolean_pms_tg
											},context=context)
						self.pool.get('crm.lead').create(cr,uid,{'partner_id':var.partner_id.id,
										'type_request':'lead_request',
										'user_id':uid,
										'created_by_global':created_by,
										'inspection_date':str(datetime.now()),
										'inquiry_no':seq_ids,'state':'open',
										'comment':''},context=context)
						if var.comment_line :
							for temp in var.comment_line :
								if temp.location.id == s.customer_address.id :
									a = self.pool.get('generic.request.comment.line').create(cr,uid,
										{
											'user_id':temp.user_id.name,
											'comment':temp.comment,
											'comment_date':temp.comment_date,
											'location':temp.location.id,
											'request_id':b
										})
					if b:
						lead_ids=self.pool.get('ccc.branch.new').search(cr,uid,[('lead_data_id','=',var.lead_data_id)])
						if len(lead_ids) > 0:
							for i in lead_ids:
								lead_tracker=self.pool.get('ccc.branch.new').browse(cr,uid,i).lead_tracker
								request_type=self.pool.get('ccc.branch.new').browse(cr,uid,i).request_type
								check_exist=self.pool.get('ccc.branch.new').browse(cr,uid,i).check_exist
								if request_type =='new_cust' and lead_tracker and check_exist:
									self.pool.get('ccc.branch.new').unlink(cr,uid,i)
					if s.branch.id == var.partner_id.company_id.id:
						branch=s.branch.id
						res = self.pool.get('res.company').search(cr,uid,[('id','=',branch)])
						b_name = self.pool.get('res.company').browse(cr,uid,res[0]).name
						if b_name == 'Branch Unknown':
							state = 'new'
						else:
							state = 'open'
						lead_req_id=seq_ids
						ou_id = ''
						branch_invisible = False
						remark=''	
						address=s.customer_address.id			
						credit_period_val=0
						search_type = self.pool.get('premise.type.master').search(cr,uid,[('key','=',s.customer_address.premise_type)])
						if search_type :
							cust_type = self.pool.get('premise.type.master').browse(cr,uid,search_type)[0].select_type					
							search_credit = self.pool.get('credit.period').search(cr,uid,[('name','=',cust_type)])
							credit_period_val = self.pool.get('credit.period').browse(cr,uid,search_credit)[0].credit_period        ####Credit_period new
						service_area=s.service_area.id
						pms=s.pms_id.id
						area_type = s.area_type.id if s.area_type else '',
						service_freq=s.service_frequency.id
						service=s.no_service
						inspection=s.no_inspection
						rates=s.service_rate
						requested_date=s.requested_date
						feedback=s.customer_feedback
						remark=s.remark
						discount_flat_gss=''
						discount_amount_gss=''
						if s.discount_flat_gss:
							discount_flat_gss=s.discount_flat_gss
						if s.discount_amount_gss:
							discount_amount_gss=s.discount_amount_gss
						name_search_ids = []
						self.pool.get('customer.branch.line.new').write(cr,uid,s.id,{'partner_id':var.partner_id.id})
						requested_date = request_date
						address_dup_id = customer_obj.search(cr, uid, [('customer_address','=',address),('partner_id','=',var.partner_id.id)])
						if not address_dup_id:
							if  branch:
								ou_id=self.pool.get('res.company').browse(cr,uid,branch).pcof_key
							partner = self.pool.get('customer.line').search(cr,uid,[('partner_id','=',var.partner_id.id)])
							length = len(partner)
							if length <= 9:
								length += 1
								location = str(var.partner_id.customer_id_main)+'0'+str(length)
							else:
								location = str(var.partner_id.customer_id_main)+str(length)
							d = self.pool.get('customer.line').create(cr,uid,{'partner_id':var.partner_id.id,
										'branch':branch,
										'customer_address':address,
										'service_area':service_area,
										'pms_id':pms,
										'service_frequency':service_freq,
										'no_service':service,
										'no_inspection':inspection,
										'service_rate':rates,
										'requested_date':request_date,
										'area_type':area_type,
										'customer_feedback':feedback,'location_id':'0000'+location,
										'credit_period':credit_period_val,
										},context=context)
							self.pool.get('res.partner.address').write(cr,uid,[address],{'location_id':'0000'+location})
						if address_dup_id:
							self.pool.get('customer.line').write(cr, uid, address_dup_id, {'resource_assign':s.assign_resource.name})
						res_id = var.partner_id.id
						count = count + 1
						city_list_id = []
						state_ids = []
						if s.branch.name != 'Branch Unknown' and s.branch:
							new_loc = ''
							search_id=self.pool.get('res.company').search(cr,uid,[('type','=','ccc')])
							if search_id:
								for res in self.pool.get('res.company').browse(cr,uid,[search_id[0]]):
									if not res.vpn_ip_address or not res.port or not res.dbname or not res.pwd:
										raise osv.except_osv(('Alert!'),('Please Enter Server Configuration Details'))
									vpn_ip_addr = res.vpn_ip_address
									port =res.port
									dbname = res.dbname
									pwd = res.pwd
									user_name = str(res.user_name.login)
							username = user_name 
							pwd = pwd    
							dbname = dbname
							log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
							obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
							sock_common = xmlrpclib.ServerProxy (log)
							try:
								raise
								uid = sock_common.login(dbname, username, pwd)
							except Exception as Err:
								conn_flag = True
							if conn_flag :
								company_name = ''
								insert_crm_lead=''
								time_cur = time.strftime("%H:%M:%S")
								date = datetime.now().date()
								company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
								if company_id[0]:
									company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
								current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.name
								current_company=current_company.replace(' ','_')
								con_cat = company_name+'_'+current_company+'_ExistingCustomer_'+str(date)+'_'+str(time_cur)+'.sql'
								filename = os.path.expanduser('~')+'/sql_files/'+con_cat
								directory_name = str(os.path.expanduser('~')+'/sql_files/')
								d = os.path.dirname(directory_name)
								if not os.path.exists(d):
									os.makedirs(d)
								d = os.path.dirname(directory_name)
								main_sql_str=''
								func_string ="\n\n CREATE OR REPLACE FUNCTION Existing_Customer_Request() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
								declare=" DECLARE \n \t"
								var1=""" service_frequency INT;\n service_area INT;\n pms_ids INT;
										branch_ids INT;\n name_search_ids INT;\n branch_search_ids INT;\n partner_ids INT;\n partner_ids1 INT;
										area INT;\n city_list_id INT;\n state_ids INT;\n address_ids INT;\n get_id INT;\n phone_number_ids INT;
										partner_address_ids INT;\n company_ids INT; \n lead_request_ids INT; \n srch_shceme_id INT; \n  \n  BEGIN \n """
								endif="\n\n END IF; \n"
								ret="\n RETURN 1;\n"
								elsestr="\n ELSE \n"
								final="\nEND; \n $$;\n"
								fun_call="\n SELECT Existing_Customer_Request();\n"
								if s.service_frequency:
									main_sql_str += "\n service_frequency=(SELECT id FROM service_frequency WHERE name ='%s' LIMIT 1);" %(str(s.service_frequency.name))
								if s.service_area:
									main_sql_str += "\n service_area=(SELECT id from service_area WHERE name='%s' LIMIT 1);" %(str(s.service_area.name))
								if s.pms_id:
									main_sql_str += "\n pms_ids=(SELECT id FROM product_product WHERE name_template='%s' LIMIT 1);" %(str(s.pms_id.name))
								if s.branch:
									main_sql_str +="\n branch_ids=(SELECT id FROM res_company WHERE name='%s' LIMIT 1);" %(str(s.branch.name))
								if var.user_id:
									main_sql_str += "\n name_search_ids=(SELECT id FROM res_users WHERE name='%s' LIMIT 1);" %(str(var.user_id.name))
								if var.partner_id:
									main_sql_str += "\n branch_search_ids=(SELECT id FROM res_company WHERE name='%s' LIMIT 1);" %(str(self.pool.get('res.users').browse(cr,uid,uid).company_id.name))
									main_sql_str +="\n IF branch_search_ids IS NOT NULL THEN"
									main_sql_str +="\n partner_ids =(SELECT id FROM res_partner WHERE ou_id='%s' and branch_id=branch_search_ids  LIMIT 1);" %(str(var.partner_id.ou_id))
									main_sql_str +=endif
									main_sql_str +="\n IF branch_ids IS NOT NULL THEN"
									main_sql_str +="\n partner_ids1 =(SELECT id FROM res_partner WHERE customer_id_main='%s' and branch_id=branch_ids LIMIT 1);" %(str(var.partner_id.customer_id_main))
									main_sql_str +=endif
								if s.area_type :
									main_sql_str +="\n area =(SELECT id FROM rates_area_master_ccc WHERE area='%s' LIMIT 1);" %(str(s.area_type.area))
								if s.customer_address.city_id:
									main_sql_str +="\n city_list_id =(SELECT id FROM city_name WHERE name1='%s' LIMIT 1);" %(str(s.customer_address.city_id.name1))
								if s.customer_address.state_id:
									main_sql_str +="\n state_ids = (SELECT id FROM state_name WHERE name='%s' LIMIT 1);" %(str(s.customer_address.state_id.name))
								if s.branch:
									ou_id=self.pool.get('res.company').browse(cr,uid,s.branch.id).pcof_key
								if address:
									company_id_srch = [('name', '=',self.pool.get('res.users').browse(cr,uid,uid).company_id.name)] 
									srch = self.pool.get('customer.line').search(cr,uid,[('partner_id','=',var.partner_id.id)])
									for part in self.pool.get('customer.line').browse(cr,uid,srch):
										if part.customer_address.id == address:
											main_sql_str +="\n IF partner_ids IS NOT NULL THEN "#f search_partner_id:
											main_sql_str +="\n FOR address_ids in (SELECT customer_address FROM customer_line WHERE location_id = '%s' and partner_id = partner_ids) \n LOOP \n " %(str(part.location_id))
											main_sql_str +="\n --get_id =(SELECT id FROM phone_m2m WHERE res_location_id = address_ids); "
									main_sql_str +="\n END LOOP;\n"+endif+"\n IF address_ids IS NULL THEN "
									for xx_id in s.customer_address.telephonic:
										temp = phone_m2m.copy()
										temp.update({'type':xx_id.type, 'name':xx_id.name})
										telephonic.extend([(0,0,temp)])
									main_sql_str +="\n INSERT INTO res_partner_address (state_id,city_id,zip,email,fax,landmark,first_name,last_name,middle_name,designation,title,district,partner_id,premise_type,location_name,apartment,building,sub_area,tehsil,street) VALUES (state_ids,city_list_id,%s,%s,%s,%s,%s, %s,%s,%s,%s,(select id from district_name where name=%s),partner_ids,%s,%s,%s,%s,%s,(select id from tehsil_name where name=%s),%s);" %("'"+str(s.customer_address.zip)+"'" if s.customer_address.zip else 'Null',"'"+str(s.customer_address.email)+"'" if s.customer_address.email else 'Null',"'"+str(s.customer_address.fax)+"'" if s.customer_address.fax else 'NULL',"'"+str(s.customer_address.landmark)+"'" if s.customer_address.landmark else 'NULL',"'"+str(s.customer_address.first_name) +"'" if s.customer_address.first_name else 'NULL',"'"+str(s.customer_address.last_name) +"'" if s.customer_address.last_name else 'NULL',"'"+ str(s.customer_address.middle_name) +"'" if s.customer_address.middle_name else 'NULL',"'"+str(s.customer_address.designation)+"'" if s.customer_address.designation else 'NULL',"'"+ str(s.customer_address.title)+"'" if s.customer_address.title else 'NULL',"'"+str(s.customer_address.district.name)+"'" if s.customer_address.district.name else 'NULL',"'"+str(s.customer_address.premise_type) +"'" if s.customer_address.premise_type else 'NULL',"'"+str(s.customer_address.location_name) +"'" if s.customer_address.location_name else 'NULL',"'"+str(s.customer_address.apartment)+"'" if s.customer_address.apartment else 'NULL',"'"+str(s.customer_address.building)+"'" if s.customer_address.building else 'NULL',"'"+str(s.customer_address.sub_area)+"'" if s.customer_address.sub_area else 'NULL',"'"+str(s.customer_address.tehsil.name)+"'" if s.customer_address.tehsil.name else 'NULL',"'"+str(s.customer_address.street)+"'" if s.customer_address.street else 'NULL')
									search_phone_id = self.pool.get('phone.m2m').search(cr,uid,[('res_location_id','=',s.customer_address.id)])
									main_sql_str+="\n partner_address_ids = (SELECT id from res_partner_address where partner_id=partner_ids AND apartment=%s AND premise_type=%s AND building =%s LIMIT 1);" %("'"+str(s.customer_address.apartment)+"'" if s.customer_address.apartment else 'NULL',"'"+str(s.customer_address.premise_type)+"'" if s.customer_address.premise_type else 'NULL',"'"+str(s.customer_address.building)+"'" if s.customer_address.building else 'NULL')
									for iter_phone in self.pool.get('phone.m2m').browse(cr,uid,search_phone_id):
										main_sql_str +="\n INSERT INTO phone_m2m (res_location_id,name,type) VALUES ( partner_address_ids ,'%s' ,'%s') ;" %(str(iter_phone.name),str(iter_phone.type))
										main_sql_str+="\n phone_number_ids=(SELECT MAX(id) FROM phone_m2m);"
									cust_srch_id = self.pool.get('customer.line').search(cr,uid,[('partner_id','=',var.partner_id.id),('customer_address','=',s.customer_address.id)])
									if cust_srch_id:
										self.pool.get('customer.line').write(cr,uid,cust_srch_id,{'phone_many2one':search_phone_id[0] if search_phone_id else ''})
									main_sql_str+="\n INSERT INTO customer_line(phone_many2one,partner_id,branch,location_id) VALUES (phone_number_ids,partner_ids,branch_ids,'%s');" %(str('0000'+location))
									main_sql_str+=endif
								if var.comment_line:
									temp_comment_line = []
									for xx_id in var.comment_line:
										if s.customer_address:
											args_address = [('partner_id','=',partner_ids),('apartment','=',s.customer_address.apartment),('premise_type','=',s.customer_address.premise_type),('building','=',s.customer_address.building)]
											main_sql_str+="\n partner_address_ids = (SELECT id from res_partner_address where partner_id=partner_ids AND apartment=%s AND premise_type=%s AND building =%s LIMIT 1);" %("'"+str(s.customer_address.apartment)+"'","'"+str(s.customer_address.premise_type)+"'" if s.customer_address.premise_type else 'NULL',"'"+str(s.customer_address.building)+"'" if s.customer_address.building else 'NULL')
										line_id = xx_id.id
										comment = {
											'lead_coment_id':partner_ids[0] if partner_ids else False,
											'user_id':xx_id.user_id.name if xx_id.user_id else False,
											'comment':xx_id.comment,
											'comment_date':xx_id.comment_date,
											'location':ids2[0] if ids2 else address_id,
											}
										if s.customer_address.id == xx_id.location.id:
											temp_comment_line.extend([(0,0,comment)])
								company_ids="company_ids=(select id from res_company where name=%s);" %(str(self.pool.get('res.users').browse(cr,uid,uid).company_id.name))
								main_sql_str+="\n INSERT INTO ccc_customer_request(user_id,partner_id,name,branch_id,request_type,state,request_id,origin,comment_remark,title,contact_name,first_name,middle_name,last_name,designation,premise_type,location_name,apartment,building,sub_area,landmark,street,tehsil,state_id,city_id,district,zip,phone_m2o,fax,email,ref_by,created_by_global,ref_text,call_type) values(name_search_ids,partner_ids,%s,branch_ids,'lead_request','open',%s,branch_ids,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,(select id from tehsil_name where name=%s),state_ids,city_list_id,(select id from district_name where name=%s),%s,phone_number_ids,%s,%s,%s,%s,%s,%s);" %("'"+str(var.partner_id.name)+"'" if var.partner_id.name else 'Null',"'"+str(lead_req_id)+"'" if lead_req_id else 'Null',"'"+str(temp_comment_line)+"'" if temp_comment_line else 'Null',"'"+str(var.partner_id.title)+"'" if var.partner_id.title else 'Null',"'"+str(var.partner_id.contact_name)+"'" if var.partner_id.contact_name else 'Null',"'"+str(var.partner_id.first_name)+"'" if var.partner_id.first_name else 'Null',"'"+str(var.partner_id.middle_name)+"'" if var.partner_id.middle_name else 'Null',"'"+str(var.partner_id.last_name)+"'" if var.partner_id.last_name else 'Null',"'"+str(var.partner_id.designation)+"'" if var.partner_id.designation else 'Null',"'"+str(var.partner_id.premise_type)+"'" if var.partner_id.premise_type else 'Null',"'"+str(s.customer_address.location_name)+"'" if s.customer_address.location_name else 'Null',"'"+str(s.customer_address.apartment)+"'" if s.customer_address.apartment else 'Null',"'"+str(s.customer_address.building)+"'" if s.customer_address.building else 'Null',"'"+str(s.customer_address.sub_area)+"'" if s.customer_address.sub_area else 'Null',"'"+str(s.customer_address.landmark)+"'" if s.customer_address.landmark else 'Null',"'"+str(s.customer_address.street)+"'" if s.customer_address.street else 'Null',"'"+str(s.customer_address.tehsil.name)+"'" if s.customer_address.tehsil.name else 'Null',"'"+str(s.customer_address.district.name)+"'" if s.customer_address.district.name else 'Null',"'"+str(s.customer_address.zip)+"'" if s.customer_address.zip else 'Null',"'"+str(var.partner_id.fax)+"'" if var.partner_id.fax else 'Null',"'"+str(var.partner_id.email)+"'" if var.partner_id.email else 'Null','Null',"'"+str(created_by)+"'" if created_by else 'Null',"'"+str(var.partner_id.ref_by_name)+"'" if var.partner_id.ref_by_name else 'Null',"'"+str(var.call_type)+"'" if var.call_type else 'Null')
								main_sql_str+="\n lead_request_ids=(select id from ccc_customer_request where request_id=%s);" %("'"+str(lead_req_id)+"'" if lead_req_id else 'Null')
								srch_shceme_id = []
								if s.scheme_name:
									srch_shceme_name = [('campaign_seq','=',s.scheme_name.campaign_seq)]
									main_sql_str+="\n srch_shceme_id=(select id from marketing_discount_campaign where campaign_seq=%s);" %(str(s.scheme_name.campaign_seq) if s.scheme_name.campaign_seq else 'Null')
								main_sql_str+="\n INSERT INTO customer_lead_line(lead_id,address_id,request_id,product_id,service_frequency,no_of_services,service_area,no_of_inspections,requested_date,service_rate,customer_feedback,area_type,branch_id,discount_flat_gss,discount_amount_gss,scheme_name,campaign_discount,campaign_disc_amnt,rates_with_tax,remark) values(lead_request_ids,(select id from res_partner_address where location_id=%s and branch_id=branch_ids),%s,pms_ids,service_frequency,%s,service_area,%s,%s,%s,%s,area,branch_ids,%s,%s,srch_shceme_id,%s,%s,%s,%s);" %("'"+str(part.location_id)+"'" if part.location_id else 'NULL',"'"+str(lead_req_id)+"'" if lead_req_id else 'Null', "'"+str(s.no_service)+"'" if s.no_service else 'Null',"'"+str(s.no_inspection)+"'" if s.no_inspection else 'Null',"'"+str(s.requested_date)+"'" if s.requested_date else 'Null',"'"+str(s.service_rate)+"'" if s.service_rate else 'Null',"'"+str(s.customer_feedback)+"'" if s.customer_feedback else 'Null',"'"+str(discount_flat_gss)+"'" if discount_flat_gss else 'Null',"'"+str(discount_amount_gss)+"'" if discount_amount_gss else 'Null',"'"+str(line.campaign_discount)+"'" if line.campaign_discount else 0.0,"'"+str(line.campaign_disc_amnt)+"'" if line.campaign_disc_amnt else 0.0,"'"+str(line.rates_with_tax)+"'" if line.rates_with_tax else 'Null',"'"+str(remark)+"'" if remark else 'Null') 
								main_sql_str+="\n INSERT INTO crm_lead(partner_id,created_by_global,inquiry_type,quotation_type,type_request,user_id,inspection_date,inquiry_no,state) values(partner_ids,%s,'service','lead','lead_request',%s,%s,%s,'open');" %("'"+str(created_by)+"'" if created_by else 'Null',"'"+str(uid)+"'" if uid else 'Null',"'"+str(datetime.now().date())+"'","'"+str(lead_req_id)+"'" if lead_req_id else 'Null')
								with open (filename,'a') as f :
									f.write(func_string)
									f.write(declare)
									f.write(var1)
									f.write(main_sql_str)
									f.write(ret)
									f.write(final)
									f.write(fun_call)
									f.close()
					elif s.branch:
						search_type = self.pool.get('premise.type.master').search(cr,uid,[('key','=',s.customer_address.premise_type)])
						if search_type :
							cust_type = self.pool.get('premise.type.master').browse(cr,uid,search_type)[0].select_type					
							search_credit = self.pool.get('credit.period').search(cr,uid,[('name','=',cust_type)])
							credit_period_val = self.pool.get('credit.period').browse(cr,uid,search_credit)[0].credit_period        ####Credit_period new
						line = s
						for jj in self.pool.get('res.partner').browse(cr,uid,[var.partner_id.id]):
							if line.branch.name != 'Branch Unknown':
												print "CUSTOMER _ID",jj.customer_id_main,jj.ou_id
												partner_address_id = line.customer_address.id
												if line.branch.id not in branch_dict_main['branch_id_list'] and line.branch and line.branch.name != 'Branch Unknown':
													customer_create_id= self.pool.get('res.partner').create(cr,uid,
														{
															'name':jj.name,
															'active':False,
															'tag_new':jj.tag_new,
															'ou_id':'0000'+jj.customer_id_main,
															'active':False,
															'customer_id_main':jj.customer_id_main,
															'title':line.customer_address.title,
															'contact_name':jj.contact_name,
															'email':jj.email,
															'premise_type':line.customer_address.premise_type,
															'apartment':line.customer_address.apartment,'location_name':line.customer_address.location_name,'first_name':line.customer_address.first_name,
															'last_name':line.customer_address.last_name,'middle_name':line.customer_address.middle_name,
															'designation':line.customer_address.designation,
															'building':line.customer_address.building,'sub_area':line.customer_address.sub_area,
															'fax':line.customer_address.fax,'street':line.customer_address.street,
															'user_id':uid,'last_name':line.customer_address.last_name,'first_name':line.customer_address.first_name,
															'middle_name':line.customer_address.middle_name,'designation':line.customer_address.designation,
															'landmark':line.customer_address.landmark,
															'city_id':line.customer_address.city_id.id if line.customer_address.city_id else '',
															'state_id':line.customer_address.state_id.id if line.customer_address.state_id else '',
															'district':line.customer_address.district.id,'ref_by':jj.ref_by.id,
															'tehsil':line.customer_address.tehsil.id,'branch_id':line.branch.id,
															'customer_since':str(datetime.now().date()),
															'zip':line.customer_address.zip
														})
													customer_name=''
													for temp_cust in self.pool.get('res.partner').browse(cr,uid,[branch_dict['customer_create_id']]):
														customer_name = jj.name
														date1=''
														date1=str(datetime.now().date())
														conv=time.strptime(str(date1),"%Y-%m-%d")
														date1 = time.strftime("%d-%m-%Y",conv)
													branch_dict.update({'customer_create_id':customer_create_id})
													val_ids = tuple([line.branch.id]+[customer_create_id])
													main_partner.append(val_ids)
													branch_dict_main['branch_id_list'].append(line.branch.id)
												for iter_values_id in main_partner:
													for a,b in [iter_values_id]:
														if isinstance(a,(list,tuple)):
															if a == line.branch.id:
																customer_create_id = b
														else:
															if a == line.branch.id:
																customer_create_id = b
												for iter_values_location in count_address:
													for s,t in [iter_values_location]:
														if isinstance(s,(list,tuple)):
															if s == line.branch.id:
																count_location = t
														else:
															if s == line.branch.id:
																count_location = t
												if line.customer_address.id not in customer_location_id:
														if customer_create_id :
															for partner_iterate in self.pool.get('res.partner').browse(cr,uid,[customer_create_id]):
																if count_location <= 9 :
																	count_location += 1
																	location_id = '0000'+jj.customer_id_main+'0'+str(count_location)
																	val_ids = tuple([line.branch.id]+[count_location])
																	count_address.append(val_ids)
																else:
																	count_location += 1
																	location_id = '0000'+jj.customer_id_main+str(count_location)
																self.pool.get('res.partner.address').write(cr,uid,line.customer_address.id,{'partner_id':customer_create_id})
																if line.customer_address.phone_m2m_xx:
																	search_phone_id = self.pool.get('phone.m2m').search(cr,uid,[('res_location_id','=',line.customer_address.id)])
																	if search_phone_id:
																		self.pool.get('phone.m2m').write(cr,uid,search_phone_id,{'res_location_id':partner_address_id})
																		self.pool.get('res.partner.address').write(cr,uid,partner_address_id,{'phone_m2m_xx':search_phone_id[0]})
																self.pool.get('customer.line').create(cr,uid,
																	{
																		'location_id':location_id,
																		'customer_address':partner_address_id,
																		'branch':line.branch.id,
																		'partner_id':customer_create_id,'primary_contact':True,
																		'credit_period':credit_period_val,
																	})
																customer_location_id.append(line.customer_address.id)
																branch_list.append(line.branch.id)
												req_id = ''
												if customer_create_id :
													req_id_new = self.pool.get('ir.sequence').get(cr, uid, 'ccc.branch.new.code')
													cust_id =self.pool.get('res.partner').browse(cr,uid,customer_create_id).customer_id_main
													values_left = cust_id
													if '0000' in values_left:
														cust_id = cust_id[4:]
														self.pool.get('res.partner').write(cr,uid,customer_create_id,{'customer_id_main':cust_id})
													ou_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
													prefix = self.pool.get('res.users').browse(cr,uid,uid).company_id.lead_prefix_id
													record_search=self.pool.get('ccc.branch.new').search(cr,uid,[('partner_id','=',customer_create_id),('request_id','!=',False)])
													record_val= str(len(record_search)+1)
													total_len_count = len(ou_id)+len(prefix)+len(cust_id)+1
													required_count=18-total_len_count
													req_id = ou_id+prefix+cust_id+str(record_val).zfill(required_count)
												crm_id = self.pool.get('crm.lead').create(cr,uid,
													{
														'partner_id':customer_create_id,
														'partner_name':jj.name,
														'type_request':'lead_request',
														'user_id':uid,
														'inspection_date':datetime.now().date(),
														'inquiry_no':req_id,'state':'open'
													},context=context)
												phone_id_m2m = self.pool.get('phone.m2m').search(cr,uid,[('res_location_id','=',line.customer_address.id)])

												b = self.pool.get('ccc.branch.new').create(cr,uid,
													{
														'request_type':'lead_request',
														'partner_id':customer_create_id,'phone_m2o':phone_id_m2m[0] if phone_id_m2m else '',
														'state':'open','request_id':req_id,'user_name':created_by,
														'contact_name':jj.contact_name,'inquiry_type':'service',
														'last_name':line.customer_address.last_name,'first_name':line.customer_address.first_name,
														'middle_name':line.customer_address.middle_name,'designation':line.customer_address.designation,
														'premise_type':line.customer_address.premise_type,'title':line.customer_address.title,'location_name':line.customer_address.location_name,
														'apartment':line.customer_address.apartment,'ref_by':jj.ref_by.id,
														'building':line.customer_address.building,'email':line.customer_address.email,
														'name':jj.name,'sub_area':line.customer_address.sub_area,'fax':line.customer_address.fax,'street':line.customer_address.street,
														'service_area':line.service_area.id,
														'lead_desc':var.lead_desc,
														'lead_tracker':var.lead_tracker,
														'check_pci_tec':var.check_pci_tec,
														'submitter_empcode':var.submitter_empcode,
														'lead_data_id':var.lead_data_id,
														'status_track_date':datetime.now().date(),
														'check_lead_tracker':var.check_lead_tracker,
														'request_date':var.request_date,
														'branch_id':line.branch.id,'landmark':line.customer_address.landmark,
														'ref_by':jj.ref_by.id,'city_id':line.customer_address.city_id.id,'district':line.customer_address.district.id,
														'tehsil':line.customer_address.tehsil.id,'state_id':line.customer_address.state_id.id,'zip':line.customer_address.zip,
														'tag_new':jj.tag_new,'origin':self.pool.get('res.users').browse(cr,uid,uid).company_id.id,'track_date':str(datetime.today().date()),
														'confirm_check':'open','dashboard_check':True,'crm_lead_id':crm_id
													},context=context)
												customer_line =self.pool.get('customer.branch.lead.line').create(cr,uid,
													{
														'service_frequency':line.service_frequency.id,
														'request_id':req_id,
														'address_id':line.customer_address.id,
														'product_id':line.pms_id.id,
														'lead_id':b,
														'area_type':line.area_type.id,
														'service_area':line.service_area.id,
														'no_of_services':line.no_service,
														'no_currof_inspections':line.no_inspection,
														'requested_date':line.requested_date,
														'service_rate':line.service_rate,
														'state':'open',
														'branch_id':line.branch.id,
														'scheme_name':line.scheme_name.id,
														'campaign_discount':line.campaign_discount,
														'campaign_disc_amnt':line.campaign_disc_amnt,
														'rates_with_tax':line.rates_with_tax,
													},context=context)
												if b:
													lead_ids=self.pool.get('ccc.branch.new').search(cr,uid,[('lead_data_id','=',var.lead_data_id)])
													if len(lead_ids) > 0:
														for i in lead_ids:
															request_type=self.pool.get('ccc.branch.new').browse(cr,uid,i).request_type
															lead_tracker=self.pool.get('ccc.branch.new').browse(cr,uid,i).lead_tracker
															check_exist=self.pool.get('ccc.branch.new').browse(cr,uid,i).check_exist
															if request_type =='new_cust' and lead_tracker and check_exist:
																self.pool.get('ccc.branch.new').unlink(cr,uid,i)
												phone_number_id = self.pool.get('phone.number').create(cr,uid,{'partner_id':customer_create_id})
												phone_list = self.pool.get('phone.m2m').search(cr,uid,[('res_location_id','=',line.customer_address.id)])
												if phone_list:
													for phone_list_id in self.pool.get('phone.m2m').browse(cr,uid,phone_list):
														phone_number_child_id = self.pool.get('phone.number.child').create(cr,uid,
															{
																'partner_id':customer_create_id,'number':phone_list_id.name,
																'contact_select':phone_list_id.type,
																'contact_number':phone_number_id
															})
													self.pool.get('res.partner').write(cr,uid,customer_create_id,{'phone_id':phone_number_id,'phone_many2one':phone_number_child_id})
												for values in var.comment_line:
													if values.location.id == s.customer_address.id:
														self.pool.get('generic.request.comment.line').create(cr,uid,{'comment':values.comment,'user_id':self.pool.get('res.users').browse(cr,uid,uid).name,'comment_date':values.comment_date,'request_id':b})
												if line.branch and line.branch.name != 'Branch Unknown':
													main_id = self.pool.get('ccc.branch.new').browse(cr,uid,b)
													line_id = self.pool.get('customer.branch.lead.line').browse(cr,uid,customer_line)
													branch_dict.update({'customer_create_id':customer_create_id,'location_id':location_id})
													branch_dict_main.update({'customer_create_id':customer_create_id,'location_id':location_id,'req_id':req_id})
													branch_dict.update({'req_id':req_id})
													branch_dict =self.pool.get('ccc.branch.new').process_new_customer_other_branch_existing_sync(cr,uid,main_id,line_id,branch_dict,lead_req_id,count_location)
													branch_dict_main	=self.pool.get('ccc.branch.new').process_new_customer_other_branch_existing_sync_main(cr,uid,main_id,line_id,branch_dict_main,lead_req_id,count_location)
		self.write(cr,uid,form,{'state1':'done'},context={'create_id':True})	
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'base', 'view_partner_form')
		tree_view=models_data.get_object_reference(cr, uid, 'base', 'view_partner_tree')
		return {
					'type': 'ir.actions.act_window',
					'name': 'Customer', 
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'res.partner',
					'res_id':int(partner_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							  (tree_view and tree_view[1] or False, 'tree'),
							  (False, 'calendar'), (False, 'graph')],
					'target': 'current',
				}