from osv import osv,fields
from base.res import res_partner
from tools.translate import _

class product_location_customer_search(osv.osv_memory):
	_name = 'product.location.customer.search'        

	_columns = {
	'title':fields.selection(res_partner.PARTNER_TITLES,'Title'),
	'first_name':fields.char('First Name *',size=256),
	'middle_name':fields.char('Middle Name',size=256),
	'last_name':fields.char('Last Name *',size=256),
	'designation':fields.char('Designation',size=256),
	'premise_type':fields.selection([
				('flat_apartment','Flat , Apartment'),
				('bungalow','Bungalow'),
				('office','Office'),
				('individual_house','Individual House'),
				('car_pro','Car Type'),
				('farm_house','Farm House'),
				('co_operative_housing_society','Co-operative Housing Society'),
				('bank','Bank'),
				('individual_private_residence','Individual private Residence'),
				('hostel','Hostel'),
				('dormitory','Dormitory'),
				('restaurant_unbranded','Restaurant - Unbranded'),
				('transit_camp','Transit camp'),
				('remand_home_correlation_facility','Remand Home, Correlation Facility'),
				('guest_house','Guest House'),
				('lodge','Lodge'),
				('personal_vehicle','Personal Vehicle'),
				('transport','Transport'),
				('house_boat','House boat'),
				('club','Club '),
				('club_within_housing_complex','Club - within housing complex'),
				('garage_gala','Garage, Gala'),
				('marriage_hall','Marriage Hall'),
				('marriage_room','Marriage room'),
				('party_hall','Party Hall'),
				('charitable_trust_ngo','Charitable Trust / NGO'),
				('open_ground_public_place','Open Ground / Public place'),
				('salon_parlor','Salon / Parlor'),
				('charitable_trust','Charitable Trust'),
				('open_ground_ublic_place','Open Ground / ublic place'),
				('salon_Parlo_unbranded' , 'Salon Parlor Unbranded'),
				('ngo','NGO'),
				('ymca_ywca','YMCA, YWCA'),
				('graveyard_cemetery','Graveyard / Cemetery'),
				('library','Library'),
				('race_course_stud_farms','Race Course, Stud Farms'),
				('textile_show_room_shop','Textile Show room / shop'),
				('old_age_home','Old Age home'),
				('dollar_shops','Dollar shops'),
				('Cyber-cafe','cyber_cafe'),
				('cyber_cafe','Cyber-cafe'),
				('florist_gift_shop','Florist, Gift shop'),
				('driving_school','Driving School'),
				('play_school','School, Play school, KIDZE'),
				('school_play_school_kidze','School, Play school, KIDZE'),
				('vending_machine','Vending Machine'),
				('cfa','CFA'),
				('distributor','Distributor'),
				('food_dc','Food DC'),
				('food_dC','Food DC'),
				('logistic','Logistic'),
				('packers_movers','Packers & Movers'),
				('cold_storage','Cold Storage'),
				('bus_fleet','Bus Fleet'),
				('aircraft','Aircraft'),
				('ship_cruise_liner','Ship, Cruise Liner'),
				('car_vehicle_service_center','Car / Vehicle Service Center'),
				('aircraft','Aircraft'),
				('tour_operator','Tour Operator'),
				('travel_tour_agency','Travel & Tour agency'),
				('bus_fleet','Bus Fleet'),
				('retail_store','Retail Store'),
				('hyper_market','Hyper Market'),
				('super_market','Super Market'),
				('mall','Mall'),
				('health_clinic' , 'Health Clinic'),
				('hospital','Hospital'),
				('super_specialty','Super Specialty'),
				('multi_specialt','Multi Specialt'),
				('medical_clinics','Medical Clinics'),
				('multi_specialty','Multi Specialty'),
				('medical_clinic','Medical Clinic'),
				('dental_clinic','Dental Clinic'),
				('nursing_home','Nursing Home'),
				('polyclinic','Polyclinic'),
				('pharmaceuticals','Pharmaceuticals'),
				('pharmacy_shops_chain','Pharmacy shops - chain'),
				('pharmacy_warehouse','Pharmacy Warehouse'),
				('laboratory_diagnostics_center','Laboratory / Diagnostics Center'),
				('r_and_d','R and D'),
				('r_d','R & D'),
				('blood_bank','Blood Bank'),
				('clinical_research_labs','Clinical Research Labs'),
				('gymnasium','Gymnasium'),
				('saloon_parlor_branded','Saloon & Parlor - Branded'),
				('building_contractor','Building Contractor'),
				('interior_decorator','Interior Decorator'),
				('architect_civil_engineering_firm','Architect, Civil Engineering Firm'),
				('builder','Builder'),
				('building_material_fabricator','Building Material Fabricator'),
				('landscaping_gardening_lawn','Landscaping & Gardening / Lawn'),
				('landscaping_gardening','Landscaping & Gardening'),
				('7_star','7 Star'),
				('5_star','5 Star'),
				('4_star','4 Star'),
				('3_star','3 Star'),
				('7_star_hotel','7 Star Hotel'),
				('5_star_hotel','5 Star Hotel'),
				('4_star_hotel','4 Star Hotel'),
				('3_star_hotel','3 Star Hotel'),
				('service_apartment','Service Apartment'),
				('club_health_sports','Club, Health & Sports'),
				('wellness_center' , 'Wellness Center'),
				('spa','Spa'),
				('resort','Resort'),
				('motel','Motel'),
				('food_processor','Food Processor'),
				('food_retailer','Food Retailer'),
				('food_handler','Food Handler'),
				('tobacco_ind','Tobacco Ind'),
				('tobacco_industry','Tobacco Industry'),
				('baking_bakery','Baking & Bakery'),
				('confectionery_chocolate','Confectionery & Chocolate'),
				('brewery_distillery','Brewery, & Distillery'),
				('beverages_bottling','Beverages & Bottling'),
				('spice_processor','Spice Processor'),
				('packaged_foods_ready_to_eat','Packaged Foods - Ready to eat'),
				('flour_mills','Flour Mills'),
				('jams_and_sauces','Jams and Sauces'),
				('canning_industry','Canning Industry'),
				('meat_fish','Meat & Fish '),
				('poultry_poultry_farm','Poultry & Poultry Farm'),
				('pet_cattle_feed','Pet & Cattle Feed'),
				('pet_shop','Pet Shop'),
				('dairy_ind','Dairy Ind'),
				('dairy_industry','Dairy Industry'),
				('cafe','Cafe'),
				('food_grade_packaging','Food Grade Packaging'),
				('dal_mill','Dal Mill'),
				('sugar_factory','Sugar Factory'),
				('government_tender','Government Tender'),
				('private_tender','Private Tender'),
				('residential_tender','Residential Tender'),
				('commercial_tender','Commercial Tender'),
				('heritage_conservation','Heritage Conservation'),
				('heritage_special_treatment','Heritage Special Treatment'),
				('heritage_special_treatment_eo_co2','Heritage Special Treatment - EO, CO2'),
				('art_gallery','Art Gallery'),
				('space_fumigation','Space Fumigation'),
				('container_fumigation','Container Fumigation'),
				('bubble_fumigation','Bubble Fumigation'),
				('commodity_fumigation','Commodity Fumigation'),
				('port','Port'),
				('airport','Airport'),
				('commodity_fumigation','Commodity Fumigation '),
				('chain_restaurants','Chain Restaurants'),
				('fast_foods','Fast Foods'),
				('caterers','Caterers'),
				('cafeteria','Cafeteria'),
				('commercial_kitchens','Commercial Kitchens'),
				('flight_kitchens','Flight Kitchens'),
				('community_kitchens','Community Kitchens'),
				('coaches','Coaches'),
				('railway_yards','Railway Yards'),
				('railway_platforms','Railway Platforms'),
				('studios_film_city','Studios, Film City'),
				('theme_parks_zoo','Theme Parks & Zoo'),
				('theaters_cinema_drama','Theaters-Cinema-Drama'),
				('amusement_parks','Amusement Parks'),
				('multiplexes','Multiplexes'),
				('aquariums','Aquariums'),
				('bank','Bank'),
				('branch_offices_and_atms','Branch Offices and ATMs'),
				('insurance_company_offices','Insurance Company Offices'),
				('bpos','BPOs'),('kpos','KPOs'),
				('computer_assemblers','Computer Assemblers'),
				('ibm_wipro','IBM, WIPRO'),
				('electronics','Electronics'),
				('airports_aircrafts','Airports & Aircrafts'),
				('industrial_estate_unit','Industrial Estate Unit'),
				('refineries','Refineries'),
				('power_generation_stations','Power Generation Stations'),
				('electric_transformer_switch_yards','Electric Transformer Switch Yards'),
				('hydro_electric','Hydro electric'),
				('wind_power_suzlon','Wind Power-Suzlon'),
				('thermal_power','Thermal Power'),
				('psus','PSUs'),
				('consulates_embassies','Consulates / Embassies'),
				('residences_of_consules','Residences of Consules'),
				('cpwd_mes_p_t','CPWD / MES / P & T'),
				('rbi_offices_and_treasury','RBI - Offices and Treasury'),
				('mines_gold_and_coal','Mines - Gold and Coal'),
				('defense_establishments','Defense Establishments'),
				('barc_dae_drdo_isro','BARC / DAE / DRDO / ISRO'),
				('municipal_corporation_business','Municipal Corporation Business'),
				('government_tender','Government Tender'),
				('private_tender','Private Tender'),
				('residential_tender','Residential Tender'),
				('commercial_tender','Commercial Tender'),
				('radio','Radio'),
				('television','Television'),
				('newspaers','Newspaers'),
				('printing_press','Printing Press'),
				('advertising_industry','Advertising industry'),
				('graphics_and_printers','Graphics and Printers'),
				('car_and_vehicle_manufacturers','Car and Vehicle manufacturers'),
				('automobile_ancillory_manufacturers','Automobile ancillory manufacturers'),
				('corugated_boxes','Corugated Boxes'),
				('pallet_manufacturers','Pallet Manufacturers'),
				('ply_and_laminate_manufactures','Ply and laminate manufactures'),
				('furniture_manufactures','Furniture Manufactures'),
				('wpm','WPM'),
				('temples_and_mosques_church_etc','Temples and Mosques, Church, etc'),
				('college_and_schools','College and Schools'),
				('international_schools','International Schools'),
				('mobile_phone_towers','Mobile Phone Towers'),
				('telephone_exchanges','Telephone Exchanges'),
				('fumigation_clients','Fumigation clients'),
				('sez_special_economic_zone','SEZ(Special Economic Zone)'),
				('engineering_industries','Engineering Industries'),
				('non_engineeriing_industries','Non-Engineeriing Industries'),
				('others','Others'),
			],'Premise Type * '),
	'building':fields.char('Building / Society Name * ',size=60),
	'location_name':fields.char('Location Name', size=100),
	'apartment':fields.char('Apartment / Unit Number*',size=600),
	'sub_area':fields.char('Sub Area',size=60),
	'street':fields.char('Street', size=60),
	'tehsil':fields.many2one('tehsil.name','Tehsil'),
	'landmark':fields.char('Landmark',size=60),
	'state_id':fields.many2one('state.name','State*'),
	'city_id':fields.many2one('city.name','City'),
	'district':fields.many2one('district.name','District'),
	'zip':fields.char('Pincode ',size=6),
	'email':fields.char('E-Mail', size=60),
	'phone':fields.many2one('phone.number.child','Phone'),
	'phone_new':fields.many2one('phone.number.new.psd','Phone'),
	'fax':fields.char('Fax',size=12),
	'location_attribute': fields.char('Location Attribute',size=10),
	'cust_address_id': fields.integer('Cust Address Id'),
	'original_address': fields.boolean('Original Address'),
	'exempted': fields.boolean('Exempted'),
	'exempted_classification': fields.many2one('exempted.classification','Exempted Classification'),
	'certificate_no':fields.char('Certificate Number',size=50),
	'exem_attachment':fields.binary('Attachment',size=124),
	'adhoc_job': fields.boolean('Adhoc-Job'),
	'segment': fields.selection([
				('retail','Retail Segment'),
				('distributor','Distributor Segment'),
				('institutional','Institutional/Govt Segment'),
			   ],'Segment *'),
	'product_request_id':fields.many2one('product.request','Product Request ID'),
	'partner_id':fields.many2one('res.partner','Partner ID'),
	}

	_defaults = {
		'adhoc_job': True,
	}

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		active_ids = context.get('active_ids')
		active_model = context.get('active_model')
		partner_addrs_obj = self.pool.get('res.partner.address')
		product_req_line_obj = self.pool.get('product.request.line')
		phone_child_obj = self.pool.get('phone.number.child')
		update_data = False
		true_items = []
		cit, dist, stat, teh, fa, ema = False, False, False, False, False, False
		res = super(product_location_customer_search, self).default_get(cr, uid, fields, context=context)
		location_attribute = context.get('location_attribute')
		if active_model and active_model == 'res.partner':
			if context.has_key('product_req_id'):
				product_req_id = context.get('product_req_id')
		elif active_model and active_model == 'ccc.branch.request.line':
			if context.has_key('product_req_id'):
				product_req_id = context.get('product_req_id')
		else:
			product_req_id = active_ids[0]
		product_request_data = self.pool.get('product.request').browse(cr, uid, product_req_id)
		if location_attribute == 'add':
			res.update({
				'location_attribute': 'add',
				'partner_id': product_request_data.partner_id.id,
				'product_request_id': product_request_data.id
				})
			return res
		if product_request_data.cust_address_id: 
			update_data = product_request_data.cust_address_id
		else:
			update_data = product_request_data.cust_address_id_new
		res.update({
			'title': update_data.title,
			'first_name': update_data.first_name,
			'middle_name': update_data.middle_name, 
			'last_name': update_data.last_name, 
			'designation': update_data.designation, 
			'premise_type': update_data.premise_type, 
			'building': update_data.building, 
			'location_name': update_data.location_name, 
			'apartment': update_data.apartment,
			'sub_area': update_data.sub_area,
			'street': update_data.street,
			'landmark': update_data.landmark,
			'zip': update_data.zip,
			'email': update_data.email,
			'fax': update_data.fax,
			'segment': product_request_data.segment,
			'exempted': update_data.exempted,
			'exempted_classification':update_data.exempted_classification.id,
			'certificate_no':update_data.certificate_no,
			'exem_attachment':update_data.exem_attachment,
			'adhoc_job':update_data.adhoc_job,
			'product_request_id': product_req_id,
			'location_attribute': location_attribute
		})
		if update_data.tehsil:
			res.update({
					'tehsil': update_data.tehsil.id
				})
		if update_data.district:
			res.update({
					'district': update_data.district.id
				})
		if update_data.city_id:
			res.update({
					'city_id': update_data.city_id.id
				})
		if update_data.state_id:
			res.update({
					'state_id': update_data.state_id.id
				})
		if product_request_data.partner_id:
			if update_data.phone_m2m_xx:
				phone_child_id = phone_child_obj.search(cr, uid, [('partner_id','=',product_request_data.partner_id.id),('number','=',update_data.phone_m2m_xx.name)], context=context)
				if phone_child_id:
					phone_child_id = phone_child_id[0]
			else:
				phone_child_id = False
			res.update({
					'partner_id': product_request_data.partner_id.id,
					'phone': phone_child_id
				})
		else:
			res.update({
					'phone_new': update_data.phone_new.id
				})

		if product_request_data.cust_address_id:
			address_ids = partner_addrs_obj.search(cr, uid, [('partner_id','=',product_request_data.partner_id.id)], context=context)
			if address_ids:
				primary_id = partner_addrs_obj.search(cr, uid, [('partner_id','=',product_request_data.partner_id.id),('primary_contact','=',True)], context=context)
				if not primary_id:
					if update_data.fax == ' ':
						update_data.fax = False
					if update_data.email == ' ':
						update_data.email = False

					if product_request_data.fax == ' ':
						product_request_data.fax = False
					if product_request_data.email == ' ':
						product_request_data.email = False

					if product_request_data.fax and update_data.fax:
						if product_request_data.fax == update_data.fax:
							fa = True			
					if not product_request_data.fax and not update_data.fax:
						fa = True	

					if product_request_data.email and update_data.email:
						if product_request_data.email == update_data.email:
							ema = True			
					if not product_request_data.email and not update_data.email:
						ema = True

					if product_request_data.district and update_data.district:
						if product_request_data.district.id == update_data.district.id:
							dist = True			
					if not product_request_data.district and not update_data.district:
						dist = True
					if product_request_data.city_id and update_data.city_id:
						if product_request_data.city_id.id == update_data.city_id.id:
							cit = True			
					if not product_request_data.city_id and not update_data.city_id:
						cit = True    
					if product_request_data.state_id and update_data.state_id:
						if product_request_data.state_id.id == update_data.state_id.id:
							stat = True			
					if not product_request_data.state_id and not update_data.state_id:
						stat = True    
					if product_request_data.tehsil and update_data.tehsil:
						if product_request_data.tehsil.id == update_data.tehsil.id:
							teh = True			
					if not product_request_data.tehsil and not update_data.tehsil:
						teh = True       		 		
					if product_request_data.title==update_data.title and \
							product_request_data.first_name==update_data.first_name and  \
							product_request_data.middle_name==update_data.middle_name and \
							product_request_data.last_name==update_data.last_name and \
							product_request_data.designation==update_data.designation and \
							product_request_data.premise_type==update_data.premise_type and \
							product_request_data.location_name==update_data.location_name and \
							product_request_data.building==update_data.building and \
							product_request_data.sub_area==update_data.sub_area and \
							product_request_data.street==update_data.street and \
							product_request_data.landmark==update_data.landmark and \
							product_request_data.zip==update_data.zip and \
							cit == True and dist == True and teh == True and stat == True and fa==True and ema==True:
						res.update({'original_address': True})
				else:
					primary_contact = partner_addrs_obj.browse(cr, uid, update_data.id).primary_contact
					if primary_contact == True:
						res.update({'original_address': True})
		elif product_request_data.cust_address_id_new:
			primary_contact = product_req_line_obj.browse(cr, uid, update_data.id).primary_contact
			if primary_contact == True:
				res.update({'original_address': True})
		return res

	def onchange_city_id(self,cr,uid,ids,city_id,context=None):
		v = {}
		if city_id :
			state = self.pool.get('city.name').browse(cr,uid,city_id).state_id.id
			district=self.pool.get('city.name').browse(cr,uid,city_id).district_id.id
			tehsil=self.pool.get('city.name').browse(cr,uid,city_id).tehsil_id.id	
			city_name = self.pool.get('city.name').browse(cr,uid,city_id).name1
			v['state_id'] = state
			v['district'] = district
			v['tehsil'] = tehsil
			v['state_id'] = state
		return {'value':v}		

	def product_location_phone_create(self,cr,uid,ids,context=None):	
		rec = self.browse(cr, uid, ids[0])
		if rec.partner_id:		
			view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'view_res_contact_number_form')
			view_id = view and view[1] or False
			context.update({'request_type':'partner','pro_loc_adtn_id':ids[0],'partner_id':rec.partner_id.id})
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
		else:
			view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'psd_cid', 'phone_number_pop_up_psd_form')
			view_id = view and view[1] or False
			context.update({'request_type':'product_location','pro_loc_adtn_id':ids[0]})
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

	def modify_existing_address(self,cr,uid,ids,context=None):	
		active_ids = context.get('active_ids')
		active_model = context.get('active_model')
		partner_addrs_obj = self.pool.get('res.partner.address')
		product_request_obj = self.pool.get('product.request')
		proudct_location_obj = self.pool.get('product.request.locations')
		customer_line_obj = self.pool.get('customer.line')
		partner_obj = self.pool.get('res.partner')
		phone_m2m_obj = self.pool.get('phone.m2m')
		pro_req_vals = {}
		partner_vals = {}
		cust_loc_data = self.browse(cr, uid, ids[0])
		if not cust_loc_data.first_name :
			raise osv.except_osv(("Alert!"),("Please enter 'First Name'!"))
		if not cust_loc_data.last_name :
			raise osv.except_osv(("Alert!"),("Please enter 'Last Name'!"))
		if not cust_loc_data.premise_type :
			raise osv.except_osv(("Alert!"),("Please enter 'Premise Type'!"))
		if not cust_loc_data.building :
			raise osv.except_osv(("Alert!"),("Please enter 'Building Name'!"))	
		if not cust_loc_data.apartment :
			raise osv.except_osv(("Alert!"),("Please enter 'Apartment'!"))
		if not cust_loc_data.state_id :
			raise osv.except_osv(("Alert!"),("Please enter 'State'!"))	
		# if not cust_loc_data.segment :
		# 	raise osv.except_osv(("Alert!"),("Please enter 'Segment'!"))	 					
		if cust_loc_data.zip :
			if len(cust_loc_data.zip) < 6 or len(cust_loc_data.zip) > 6:
				raise osv.except_osv(("Alert!"),("Pincode must be 6 digits long!"))
		if active_model and active_model == 'res.partner':
			if context.has_key('product_req_id'):
				product_req_id = context.get('product_req_id')
		elif active_model and active_model == 'ccc.branch.request.line':
			if context.has_key('product_req_id'):
				product_req_id = context.get('product_req_id')		
		else:
			product_req_id = active_ids[0]
		product_request_data = self.pool.get('product.request').browse(cr, uid, product_req_id)	
		partner_id = product_request_data.partner_id.id
		partner_address_id = [product_request_data.cust_address_id.id]
		addrs_items = []
		address = ''
		if cust_loc_data.apartment not in [' ',False,None]:
			addrs_items.append(cust_loc_data.apartment)
		if cust_loc_data.building not in [' ',False,None]:
			addrs_items.append(cust_loc_data.building)
		if cust_loc_data.sub_area not in [' ',False,None]:
			addrs_items.append(cust_loc_data.sub_area)
		if cust_loc_data.landmark not in [' ',False,None]:
			addrs_items.append(cust_loc_data.landmark)
		if cust_loc_data.street not in [' ',False,None]:
			addrs_items.append(cust_loc_data.street)
		if cust_loc_data.city_id:
			addrs_items.append(cust_loc_data.city_id.name1)
		if cust_loc_data.district:
			addrs_items.append(cust_loc_data.district.name)
		if cust_loc_data.tehsil:
			addrs_items.append(cust_loc_data.tehsil.name)
		if cust_loc_data.state_id:
			addrs_items.append(cust_loc_data.state_id.name)
		if cust_loc_data.zip not in [' ',False,None]:
			addrs_items.append(cust_loc_data.zip)
		if len(addrs_items) > 0:
			last_item = addrs_items[-1]
			for item in addrs_items:
				if item!=last_item:
					address = address+item+','+' '
				if item==last_item:
					address = address+item	
		if partner_id:
			if cust_loc_data.phone:
				phone_m2m_id = phone_m2m_obj.search(cr, uid, [('res_location_id','=',partner_address_id[0]),('name','=',cust_loc_data.phone.number)], context=context)
				if phone_m2m_id:
					phone_m2m_id = phone_m2m_id[0]
				else:
					phone_m2m_id = phone_m2m_obj.create(cr, uid, {
						'res_location_id': partner_address_id[0],
						'name': cust_loc_data.phone.number,
						'type': cust_loc_data.phone.contact_select
					}, context)
			else:
				phone_m2m_id = False
			partner_addrs_vals = {
				'title': cust_loc_data.title,
				'first_name': cust_loc_data.first_name,
				'middle_name': cust_loc_data.middle_name, 
				'last_name': cust_loc_data.last_name, 
				'designation': cust_loc_data.designation, 
				'premise_type': cust_loc_data.premise_type, 
				'location_name': cust_loc_data.location_name, 
				'apartment': cust_loc_data.apartment,
				'building': cust_loc_data.building, 
				'sub_area': cust_loc_data.sub_area,
				'street': cust_loc_data.street,
				'landmark': cust_loc_data.landmark,
				'city_id': cust_loc_data.city_id.id,
				'district': cust_loc_data.district.id,
				'tehsil': cust_loc_data.tehsil.id,
				'state_id': cust_loc_data.state_id.id,
				'zip': cust_loc_data.zip,
				'email': cust_loc_data.email,
				'fax': cust_loc_data.fax,
				'phone_m2m_xx': phone_m2m_id,
				'exempted': cust_loc_data.exempted,
				'exempted_classification': cust_loc_data.exempted_classification.id,
				'certificate_no': cust_loc_data.certificate_no,
				'exem_attachment': cust_loc_data.exem_attachment,
				'adhoc_job': cust_loc_data.adhoc_job,
				'segment': cust_loc_data.segment,
				'partner_id': partner_id
			}
			partner_addrs_obj.write(cr, uid, partner_address_id, partner_addrs_vals, context=context)
			cust_line_id = customer_line_obj.search(cr, uid, [('customer_address','=',partner_address_id[0]),('partner_id','=',partner_id)], context=context)
			customer_line_obj.write(cr, uid, cust_line_id[0], {'phone_many2one':phone_m2m_id}, context=context)
			partner_data = partner_obj.browse(cr, uid, partner_id)
			if cust_loc_data.original_address == True:
				customer_vals = {
					'title': cust_loc_data.title,
					'first_name': cust_loc_data.first_name,
					'middle_name': cust_loc_data.middle_name, 
					'last_name': cust_loc_data.last_name, 
					'designation': cust_loc_data.designation, 
					'premise_type': cust_loc_data.premise_type, 
					'location_name': cust_loc_data.location_name, 
					'apartment': cust_loc_data.apartment,
					'building': cust_loc_data.building, 
					'sub_area': cust_loc_data.sub_area,
					'street': cust_loc_data.street,
					'landmark': cust_loc_data.landmark,
					'city_id': cust_loc_data.city_id.id,
					'district': cust_loc_data.district.id,
					'tehsil': cust_loc_data.tehsil.id,
					'state_id': cust_loc_data.state_id.id,
					'zip': cust_loc_data.zip,
					'email': cust_loc_data.email,
					'fax': cust_loc_data.fax,
					'phone_many2one': cust_loc_data.phone.id,
					'exempted': cust_loc_data.exempted,
					'exempted_classification': cust_loc_data.exempted_classification.id,
					'certificate_no': cust_loc_data.certificate_no,
					'exem_attachment': cust_loc_data.exem_attachment,
					'adhoc_job': cust_loc_data.adhoc_job,
					'segment': cust_loc_data.segment
					# 'cust_address_id_new': False,
					# 'cust_address_id': False,
				}				
				product_request_obj.write(cr, uid, product_req_id, customer_vals, context=context)		
				partner_obj.write(cr, uid, partner_id, customer_vals, context=context)	
			address_id = product_request_data.cust_address_id.id
			if product_request_data.location_request_line:
				for location_line in product_request_data.location_request_line:
					if location_line.address_id == address_id:
						proudct_location_obj.write(cr, uid, location_line.id, {'address': address}, context=context)	
		else:
			product_request_line_vals = {
				'title': cust_loc_data.title,
				'first_name': cust_loc_data.first_name,
				'middle_name': cust_loc_data.middle_name, 
				'last_name': cust_loc_data.last_name, 
				'designation': cust_loc_data.designation, 
				'premise_type': cust_loc_data.premise_type, 
				'building': cust_loc_data.building, 
				'location_name': cust_loc_data.location_name, 
				'apartment': cust_loc_data.apartment,
				'sub_area': cust_loc_data.sub_area,
				'street': cust_loc_data.street,
				'tehsil': cust_loc_data.tehsil.id,
				'landmark': cust_loc_data.landmark,
				'state_id': cust_loc_data.state_id.id,
				'city_id': cust_loc_data.city_id.id,
				'district': cust_loc_data.district.id,
				'zip': cust_loc_data.zip,
				'email': cust_loc_data.email,
				'fax': cust_loc_data.fax,
				'phone_new': cust_loc_data.phone_new.id, 
				'exempted': cust_loc_data.exempted,
				'exempted_classification': cust_loc_data.exempted_classification.id,
				'certificate_no': cust_loc_data.certificate_no,
				'exem_attachment': cust_loc_data.exem_attachment,
				'adhoc_job': cust_loc_data.adhoc_job,
				'segment': cust_loc_data.segment,
				'address': address,
			}
			self.pool.get('product.request.line').write(cr, uid, [product_request_data.cust_address_id_new.id], product_request_line_vals, context=context)
			if cust_loc_data.original_address == True:
				product_request_vals = {
					'title': cust_loc_data.title,
					'first_name': cust_loc_data.first_name,
					'middle_name': cust_loc_data.middle_name, 
					'last_name': cust_loc_data.last_name, 
					'designation': cust_loc_data.designation, 
					'premise_type': cust_loc_data.premise_type, 
					'location_name': cust_loc_data.location_name, 
					'apartment': cust_loc_data.apartment,
					'building': cust_loc_data.building, 
					'sub_area': cust_loc_data.sub_area,
					'street': cust_loc_data.street,
					'landmark': cust_loc_data.landmark,
					'city_id': cust_loc_data.city_id.id,
					'district': cust_loc_data.district.id,
					'tehsil': cust_loc_data.tehsil.id,
					'state_id': cust_loc_data.state_id.id,
					'zip': cust_loc_data.zip,
					'email': cust_loc_data.email,
					'fax': cust_loc_data.fax,
					'phone_many2one_new': cust_loc_data.phone_new.id,
					'segment': cust_loc_data.segment,
					# 'cust_address_id_new': False,
					# 'cust_address_id': False,
				}
				product_request_obj.write(cr, uid, product_req_id, product_request_vals, context=context)
			address_id_2 = product_request_data.cust_address_id_new.id
			if product_request_data.location_request_line:
				for location_line in product_request_data.location_request_line:
					print"location_line",location_line
					if location_line.address_id_2 == address_id_2:
						proudct_location_obj.write(cr, uid, location_line.id, {'address': address}, context=context)	
		return {'type': 'ir.actions.act_window_close'}

	def create_new_address(self,cr,uid,ids,context=None):
		customer_line_obj = self.pool.get('customer.line')
		partner_address_obj = self.pool.get('res.partner.address')
		phone_m2m_obj = self.pool.get('phone.m2m')
		active_ids = context.get('active_ids')
		active_model = context.get('active_model')
		cust_loc_data = self.browse(cr, uid, ids[0])
		phone_m2m_id = False
		if not cust_loc_data.first_name :
			raise osv.except_osv(("Alert!"),("Please enter 'First Name'!"))
		if not cust_loc_data.last_name :
			raise osv.except_osv(("Alert!"),("Please enter 'Last Name'!"))
		if not cust_loc_data.premise_type :
			raise osv.except_osv(("Alert!"),("Please enter 'Premise Type'!"))
		if not cust_loc_data.building :
			raise osv.except_osv(("Alert!"),("Please enter 'Building Name'!"))		
		if not cust_loc_data.apartment :
			raise osv.except_osv(("Alert!"),("Please enter 'Apartment'!"))
		# if not cust_loc_data.segment :
		# 	raise osv.except_osv(("Alert!"),("Please enter 'Segment'!"))	 	
		if not cust_loc_data.state_id :
			raise osv.except_osv(("Alert!"),("Please enter 'State'!"))
		if cust_loc_data.zip :
			if len(cust_loc_data.zip) < 6 or len(cust_loc_data.zip) > 6:
				raise osv.except_osv(("Alert!"),("Pincode must be 6 digits long!"))
		product_req_id = context.get('product_req_id',False)
		if active_model and active_model == 'res.partner':
			if context.has_key('product_req_id'):
				product_req_id = context.get('product_req_id')
		elif active_model and active_model == 'ccc.branch.request.line':
			if context.has_key('product_req_id'):
				product_req_id = context.get('product_req_id')		
		else:
			product_req_id = active_ids[0]
		product_request_data = self.pool.get('product.request').browse(cr, uid, product_req_id)	
		partner_id = product_request_data.partner_id.id
		if partner_id:
			partner_addrs_vals = {
				'title': cust_loc_data.title,
				'first_name': cust_loc_data.first_name,
				'middle_name': cust_loc_data.middle_name, 
				'last_name': cust_loc_data.last_name, 
				'designation': cust_loc_data.designation, 
				'premise_type': cust_loc_data.premise_type, 
				'building': cust_loc_data.building, 
				'location_name': cust_loc_data.location_name, 
				'apartment': cust_loc_data.apartment,
				'sub_area': cust_loc_data.sub_area,
				'street': cust_loc_data.street,
				'tehsil': cust_loc_data.tehsil.id,
				'landmark': cust_loc_data.landmark,
				'state_id': cust_loc_data.state_id.id,
				'city_id': cust_loc_data.city_id.id,
				'district': cust_loc_data.district.id,
				'zip': cust_loc_data.zip,
				'email': cust_loc_data.email,
				'segment': cust_loc_data.segment,
				'fax': cust_loc_data.fax,
				'exempted': cust_loc_data.exempted,
				'exempted_classification': cust_loc_data.exempted_classification.id,
				'certificate_no': cust_loc_data.certificate_no,
				'exem_attachment': cust_loc_data.exem_attachment,
				'adhoc_job': cust_loc_data.adhoc_job,
				'branch_id': product_request_data.partner_id.company_id.id,
				'partner_id': partner_id
			}
			address_id = partner_address_obj.create(cr, uid, partner_addrs_vals, context=context)	
			if cust_loc_data.phone:
				phone_m2m_id = phone_m2m_obj.create(cr, uid, {
					'res_location_id': address_id,
					'name': cust_loc_data.phone.number,
					'type': cust_loc_data.phone.contact_select
				}, context=context)	
			partner_address_obj.write(cr, uid, address_id, {'phone_m2m_xx': phone_m2m_id}, context=context)	
			loctn_ids = customer_line_obj.search(cr, uid, [('partner_id','=',partner_id)], context=context)
			prefix = '0000'
			loc_inc_no = len(loctn_ids)+1
			if loc_inc_no >= 0 and loc_inc_no <= 9:
				st_loc_inc_no = '0'+str(loc_inc_no)
			elif loc_inc_no >= 10 and loc_inc_no <= 99:
				st_loc_inc_no = str(loc_inc_no)
			customer_seq = product_request_data.partner_id.ou_id
			cust_prefix = False
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
			location_id = prefix+customer_inc_no+st_loc_inc_no
			cust_line_vals = {
				'location_id': location_id,
				'premise_type_import': cust_loc_data.premise_type,
				'branch': product_request_data.partner_id.company_id.id,
				'customer_address': address_id,
				'partner_id': partner_id,
				'phone_many2one': phone_m2m_id
			}
			cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)
			context.update({'customer_line_values':cust_line_vals,'phone_number':cust_loc_data.phone.number})
			self.sync_product_location_customer_search(cr,uid,ids,context=context)
		else:
			addrs_items = []
			address = ''	
			if cust_loc_data.apartment not in [' ',False,None]:
				addrs_items.append(cust_loc_data.apartment)
			if cust_loc_data.building not in [' ',False,None]:
				addrs_items.append(cust_loc_data.building)
			if cust_loc_data.sub_area not in [' ',False,None]:
				addrs_items.append(cust_loc_data.sub_area)
			if cust_loc_data.landmark not in [' ',False,None]:
				addrs_items.append(cust_loc_data.landmark)
			if cust_loc_data.street not in [' ',False,None]:
				addrs_items.append(cust_loc_data.street)
			if cust_loc_data.city_id:
				addrs_items.append(cust_loc_data.city_id.name1)
			if cust_loc_data.district:
				addrs_items.append(cust_loc_data.district.name)
			if cust_loc_data.tehsil:
				addrs_items.append(cust_loc_data.tehsil.name)
			if cust_loc_data.state_id:
				addrs_items.append(cust_loc_data.state_id.name)
			if cust_loc_data.zip not in [' ',False,None]:
				addrs_items.append(cust_loc_data.zip)
			if len(addrs_items) > 0:
				last_item = addrs_items[-1]
				for item in addrs_items:
					if item!=last_item:
						address = address+item+','+' '
					if item==last_item:
						address = address+item
			product_request_line_vals = {
				'title': cust_loc_data.title,
				'first_name': cust_loc_data.first_name,
				'middle_name': cust_loc_data.middle_name, 
				'last_name': cust_loc_data.last_name, 
				'designation': cust_loc_data.designation, 
				'premise_type': cust_loc_data.premise_type, 
				'building': cust_loc_data.building, 
				'location_name': cust_loc_data.location_name, 
				'apartment': cust_loc_data.apartment,
				'sub_area': cust_loc_data.sub_area,
				'street': cust_loc_data.street,
				'tehsil': cust_loc_data.tehsil.id,
				'landmark': cust_loc_data.landmark,
				'state_id': cust_loc_data.state_id.id,
				'city_id': cust_loc_data.city_id.id,
				'district': cust_loc_data.district.id,
				'zip': cust_loc_data.zip,
				'email': cust_loc_data.email,
				'fax': cust_loc_data.fax,
				'phone_new': cust_loc_data.phone_new.id,
				'address': address,
				'exempted': cust_loc_data.exempted,
				'exempted_classification': cust_loc_data.exempted_classification.id,
				'certificate_no': cust_loc_data.certificate_no,
				'exem_attachment': cust_loc_data.exem_attachment,
				'adhoc_job': cust_loc_data.adhoc_job,
				'segment': cust_loc_data.segment,
				'product_request_id': active_ids[0],
				'product_request_ref': product_request_data.product_request_id
			}
			self.pool.get('product.request.line').create(cr, uid, product_request_line_vals)
			self.sync_product_location_customer_search(cr,uid,ids,context=context)	
		return {'type': 'ir.actions.act_window_close'}

product_location_customer_search() 