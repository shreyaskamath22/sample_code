from datetime import date,datetime, timedelta
from osv import osv,fields
from tools.translate import _
from base.res import res_partner
import time

class product_request(osv.osv):
	_name = 'product.request'
	_rec_name = 'product_request_id'
	_order = 'request_date desc'

	def _get_user(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).id

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_datetime(self,cr,uid,context=None):
		return time.strftime("%Y-%m-%d %H:%M:%S")

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'active':fields.boolean('Active', select=True),
		'name':fields.char('Customer / Company Name * ',size=100, select=True),
		'customer_type': fields.selection([('existing','Existing Customer'),('new','New Customer')],'Customer Type * ', select=True),
		'customer_id': fields.char('Customer ID',size=256),
		'call_type':fields.selection([('inbound','Inbound'),('outbound','Outbound')],'Call Type * '),
		'state':fields.selection([('new','New'),
						('open','Opened'),
						('assigned','Resource Assigned'),
						('closed','Closed'),
						('cancel','Cancelled')
						],'Status', select=True), 
		'created_date': fields.datetime('Created Date'),
		'created_by':fields.many2one('res.users','Created By'),
		'request_date':fields.datetime('Request Date'),
		'inquiry_type':fields.selection([('product','Product'),('service','Service')],'Lead Type * '),
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
		'location_name':fields.char('Location Name', size=100),#abhi
		'apartment':fields.char('Apartment / Unit Number *',size=600),
		'sub_area':fields.char('Sub Area',size=60),
		'street':fields.char('Street', size=60),
		'tehsil':fields.many2one('tehsil.name','Tehsil'),
		'landmark':fields.char('Landmark',size=60),
		'state_id':fields.many2one('state.name','State *'),
		'city_id':fields.many2one('city.name','City'),
		'district':fields.many2one('district.name','District'),
		'zip':fields.char('Pincode ',size=6),
		'email':fields.char('E-Mail', size=60),
		'fax': fields.char('Fax',size=12),
		'mobile': fields.related('partner_id','mobile',relation='phone.number.child',type="many2one",string="Landline/Mobile",domain="[('partner_id','=',partner_id)]"),
		'ref_by': fields.many2one('customer.source','Reference by *'),
		'ref_text':fields.char('Reference*',size=124),
		'check_ref':fields.boolean('Check Ref'),
		'customer_address':fields.text('Address'),
		'remarks':fields.text('Remarks'),
		'branch_id':fields.many2one('res.company','PSD Office',domain="[('establishment_type','=','psd')]"),
		'phone_many2one':fields.many2one('phone.number.child','Phone Number'),
		'phone_many2one_new':fields.many2one('phone.number.new.psd','Phone Number'),
		'notes_line': fields.one2many('product.request.notes.line','request_id','Comments'),
		'location_request_line': fields.one2many('product.request.locations','location_request_id','Locations & Products'),
		'comment_remark':fields.text('Comments',size=400),
		'show_table': fields.boolean('Show Table'),
		'confirm_check':fields.boolean('Confirm Check'),
		'show_loc': fields.boolean('Show Location'),
		'cust_address_id': fields.many2one('res.partner.address', 'Address'),
		'cust_address_id_1': fields.many2one('res.partner.address', 'Address'),
		'cust_address_id_new': fields.many2one('product.request.line', 'Address'),
		'cust_address_id_2': fields.many2one('product.request.line', 'Address'),
		'product_request_line_ids': fields.one2many('product.request.line','product_request_id','Addresses'),
		'partner_id': fields.many2one('res.partner','Partner'),
		'request_search_sales_id': fields.many2one('request.search.sales', 'Address'),
		'employee_id': fields.many2one('hr.employee', 'Assign Resource'),
		'cancel_request': fields.boolean('Cancel Request'),
		'cancellation_reason': fields.char('Cancellation Reason*',size=50),
		'select_request': fields.boolean('Select Request'),
		'product_quotation_id': fields.many2one('psd.sales.product.quotation', 'Product Quotation'),
		'product_order_id': fields.many2one('psd.sales.product.order', 'Product Quotation'),
		'amc_quotation_id1': fields.many2one('amc.quotation', 'AMC Quotation'),
		'product_request_id': fields.char('Request ID',size=100),
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
		'psd_sales_entry':fields.boolean('PSD Sales Entry'),
		'primary_contact': fields.boolean('primary_contact'),
		'hide_search': fields.boolean('Hide Search'),
		'hide_ref': fields.boolean('Hide Ref'),
		'hide_segment': fields.boolean('Hide Segment'),
		'segment': fields.selection([
			('retail','Retail Segment'),
			('distributor','Distributor Segment'),
			('institutional','Institutional/Govt Segment'),
		   ],'Segment'),
		'parent_request': fields.many2one('product.request','Parent Request'),
		'request_cancellation_type': fields.selection([('existing_loction','Existing customer existing location'),
													   ('new_location', 'Existing customer new location'),
													   ('other_branch', 'Send to other branch'),
													  ],'Request Cancellation Type'),
		'new_partner_id': fields.many2one('res.partner','Customer'),
		'new_name':fields.char('Customer / Company Name*',size=100),
		'other_branch_id':fields.many2one('res.company','Other PCI branch*'),
		'closed_date':fields.datetime('Closed Date'),
		'location_branch': fields.selection([('same', 'Same'),
											 ('different', 'Different'),
											 ('crm', 'CRM')
											 ],'Location Branch'),
		'products':fields.char('SKU Name',size=1000),
	}

	_defaults = {
		'company_id': _get_company,
		'active': True,
		'show_table': False,
		'inquiry_type': 'product',
		'call_type':'inbound',
		'state':'new',
		'request_date':_get_datetime,
		'created_by':lambda self, cr, uid, context: self._get_user(cr, uid, context),
		'customer_type': 'new',
		'request_type': 'product'
	}

	def _get_default_date(self, cr, uid, context=None):
		if context is None:
			context = {}
		if 'date' in context:
			return context['date'] + time.strftime(' %H:%M:%S')
		return time.strftime('%Y-%m-%d %H:%M:%S')


	def create_number_psd(self,cr,uid,ids,context=None):	
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_cid', 'phone_number_pop_up_psd_form')
		view_id = view and view[1] or False
		context.update({'request_type':'product'})
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

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		crm_lead_obj = self.pool.get('crm.lead')
		for product_req_id in ids:
			crm_lead_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=',product_req_id)], context=context)
			crm_lead_obj.unlink(cr, uid, crm_lead_ids, context=context)
		res = super(product_request, self).unlink(cr, uid, ids, context=context)
		return res

	# def create(self, cr, uid, vals, context=None):
	# 	pr_seq = self.pool.get('ir.sequence').get(cr, uid, 'product.request')
	# 	vals.update({'product_request_id': pr_seq})
	# 	return super(product_request, self).create(cr, uid, vals, context=context)				

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
		return {'value':v}

	def onchange_ref_by(self,cr,uid,ids,ref_by,context=None):		
		v = {}
		cust_source_obj = self.pool.get('customer.source')
		if ref_by:
			name = cust_source_obj.browse(cr, uid, ref_by).name
			if name == 'Others (Specify)':
				v['check_ref'] = True
			else :
				v['check_ref'] = False
		return {'value':v}

	def confirm_primary_contact(self,cr,uid,ids,context=None):
		primary_data = self.browse(cr, uid, ids[0])
		if not primary_data.name :
			raise osv.except_osv(("Alert!"),("Please enter 'Customer / Company Name'!"))
		if not primary_data.first_name :
			raise osv.except_osv(("Alert!"),("Please enter 'First Name'!"))
		if not primary_data.last_name :
			raise osv.except_osv(("Alert!"),("Please enter 'Last Name'!"))
		if not primary_data.premise_type :
			raise osv.except_osv(("Alert!"),("Please enter 'Premise Type'!"))
		if not primary_data.apartment :
			raise osv.except_osv(("Alert!"),("Please enter 'Apartment'!"))			
		if not primary_data.building :
			raise osv.except_osv(("Alert!"),("Please enter 'Building Name'!"))
		if not primary_data.ref_by :
			raise osv.except_osv(("Alert!"),("Please Enter 'Reference by'!"))	
		if not primary_data.customer_type:
			raise osv.except_osv(("Alert!"),("Please select 'Customer Type'!"))
		if not primary_data.state_id:
			raise osv.except_osv(("Alert!"),("Please select 'State'!"))		
		# if not primary_data.segment:
		# 	raise osv.except_osv(("Alert!"),("Please select 'Segment'!"))				
		if primary_data.zip :
			if len(primary_data.zip) < 6 or len(primary_data.zip) > 6:
				raise osv.except_osv(("Alert!"),("Pincode must be 6 digits long!"))
		if primary_data.customer_type == 'new':	
			addrs_items = []
			address = ''	
			if primary_data.apartment not in [' ',False,None]:
				addrs_items.append(primary_data.apartment)
			if primary_data.building not in [' ',False,None]:
				addrs_items.append(primary_data.building)
			if primary_data.sub_area not in [' ',False,None]:
				addrs_items.append(primary_data.sub_area)
			if primary_data.landmark not in [' ',False,None]:
				addrs_items.append(primary_data.landmark)
			if primary_data.street not in [' ',False,None]:
				addrs_items.append(primary_data.street)
			if primary_data.city_id:
				addrs_items.append(primary_data.city_id.name1)
			if primary_data.district:
				addrs_items.append(primary_data.district.name)
			if primary_data.tehsil:
				addrs_items.append(primary_data.tehsil.name)
			if primary_data.state_id:
				addrs_items.append(primary_data.state_id.name)
			if primary_data.zip not in [' ',False,None]:
				addrs_items.append(primary_data.zip)
			if len(addrs_items) > 0:
				last_item = addrs_items[-1]
				for item in addrs_items:
					if item!=last_item:
						address = address+item+','+' '
					if item==last_item:
						address = address+item
			product_request_line_vals = {
				'primary_contact': True,
				'title': primary_data.title,
				'first_name': primary_data.first_name,
				'middle_name': primary_data.middle_name, 
				'last_name': primary_data.last_name, 
				'designation': primary_data.designation, 
				'premise_type': primary_data.premise_type, 
				'building': primary_data.building, 
				'location_name': primary_data.location_name, 
				'apartment': primary_data.apartment,
				'sub_area': primary_data.sub_area,
				'street': primary_data.street,
				'tehsil': primary_data.tehsil.id,
				'landmark': primary_data.landmark,
				'state_id': primary_data.state_id.id,
				'city_id': primary_data.city_id.id,
				'district': primary_data.district.id,
				'zip': primary_data.zip,
				'email': primary_data.email,
				'fax': primary_data.fax,
				'address': address,
				'phone_new': primary_data.phone_many2one_new.id,
				'segment': primary_data.segment,
				'product_request_id': ids[0]
			}
			self.pool.get('product.request.line').create(cr, uid, product_request_line_vals)
		self.write(cr,uid,ids,
			{
				'confirm_check':True,
				'primary_contact':True,
				'hide_search':True,
				'hide_segment':True,
				'hide_ref':True
			},context=context)
		return True

	def edit_location(self, cr, uid, ids, context=None):
		if context is None: context = {}
		rec = self.browse(cr, uid, ids[0])
		if rec.customer_type=='existing' and not rec.ref_by:
			raise osv.except_osv(_('Warning!'),_("Please select 'Reference by'!"))
		# if rec.customer_type=='existing' and not rec.segment:
		# 	raise osv.except_osv(_('Warning!'),_("Please select 'Segment'!"))
		context.update({'location_attribute': 'edit'})
		return {
			'name': _('Customer Location'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': False,
			'res_model': 'product.location.customer.search',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'context': context,                               
		}	

	def add_new_location(self,cr,uid,ids,context=None):		
		if context is None: context = {}
		rec = self.browse(cr, uid, ids[0])
		if rec.customer_type=='existing' and not rec.ref_by:
			raise osv.except_osv(_('Warning!'),_("Please select 'Reference by'!"))
		# if rec.customer_type=='existing' and not rec.segment:
		# 	raise osv.except_osv(_('Warning!'),_("Please select 'Segment'!"))
		context.update({'location_attribute': 'add'})
		return {
			'name': _('Customer Location'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': False,
			'res_model': 'product.location.customer.search',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'context': context,                               
		}	
		return True

	def submit_product_request(self,cr,uid,ids,context=None):
		models_data=self.pool.get('ir.model.data')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		product_obj = self.pool.get('product.product')
		repeated_ids = []
		rec = self.browse(cr,uid,ids[0])
		if rec.customer_type == 'new' and rec.confirm_check == False:
			raise osv.except_osv(_('Warning!'),_("Please confirm the primary contact!"))
		location_request_line = rec.location_request_line
		
		for record in location_request_line:
			product_name = record.product_name
			if product_name:
				product_ids = product_obj.search(cr, uid, [('id','=',product_name.id)], context=context)
				if product_ids:
					product_data = product_obj.browse(cr,uid,product_ids[0])
					qty_available = product_data.quantity_actual if product_data.quantity_actual else 0.00
					prod_req_loc_obj.write(cr,uid,record.id,{'available_quantity':qty_available})


		if not location_request_line:
			raise osv.except_osv(_('Warning!'),_("Please select locations & products!"))
		for loc_req_line in location_request_line:
			if loc_req_line.quantity < 1:
				raise osv.except_osv(_('Warning!'),_("Quantity should be atleast 1!"))
			office = loc_req_line.branch_id.id
			product = loc_req_line.product_name.id
			# sku = loc_req_line.sku_name_id.id
			if rec.customer_type == 'existing':
				loc = 'address_id'
				location = loc_req_line.address_id
			else:
				loc = 'address_id_2'
				location = loc_req_line.address_id_2
			if len(location_request_line) > 1:
				repeated_ids = prod_req_loc_obj.search(cr, uid, [
								('location_request_id','=',rec.id),
								(loc,'=',location),
								('branch_id','=',office),
								('product_name','=',product),
								('id','!=',loc_req_line.id)], context=context)
			if repeated_ids:
				raise osv.except_osv(_('Invalid Combination!'),_("Same locations, same offices & same products are not allowed!"))
		form_id = models_data.get_object_reference(cr, uid, 'psd_cid', 'product_request_submit_form')
		return {
			   'name':'Confirm Product Request',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'product.request.submit',
			   'type': 'ir.actions.act_window',
			   'target': 'new'
		}		

	def assign_resource(self,cr,uid,ids,context=None):	
		rec = self.browse(cr, uid, ids[0])
		main_id = rec.id
		crm_lead_obj = self.pool.get('crm.lead')	
		customer_line_obj = self.pool.get('customer.line')
		partner_addr_obj = self.pool.get('res.partner.address')
		partner_obj = self.pool.get('res.partner')
		search_location_company = self.pool.get('product.request.locations').search(cr,uid,[('location_request_id','=',main_id)])
		browse_location_company = self.pool.get('product.request.locations').browse(cr,uid,search_location_company[0]).branch_id.id
		res = self.write(cr,uid,ids,{'state':'assigned'},context=context)
		customer_line_id = False
		crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'progress'}, context=context)
		if rec.employee_id:
			addr_id = partner_addr_obj.search(cr, uid, [
					('partner_id','=',rec.partner_id.id),
					('first_name','=',rec.first_name),
					('last_name','=',rec.last_name),
					('apartment','=',rec.apartment),
					('building','=',rec.building),
					('premise_type','=',rec.premise_type),
					('state_id','=',rec.state_id.id),
			], context=context)
			if addr_id:
				customer_line_id = customer_line_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('customer_address','=',addr_id[0])], context=context)
			if customer_line_id:
				temp_location_id = customer_line_obj.browse(cr, uid, customer_line_id[0]).location_id
				location_id = temp_location_id[4:]
				pcof_key = rec.company_id.pcof_key
				new_location_id = pcof_key+location_id
				temp_ou_id = rec.partner_id.ou_id
				ou_id = temp_ou_id[4:]
				new_ou_id = pcof_key+ou_id
				cust_line_vals = {'location_id':new_location_id}
				customer_line_obj.write(cr, uid, customer_line_id[0], cust_line_vals, context=context)
				partner_obj.write(cr, uid, rec.partner_id.id, {'ou_id': new_ou_id}, context=context)
				if rec.employee_id.role_selection == 'cse':		
					cust_line_vals.update({'cse':rec.employee_id.id})
				customer_line_obj.write(cr, uid, customer_line_id[0], cust_line_vals, context=context)
		temp_customer_id = rec.customer_id
		customer_id = temp_customer_id[4:]
		new_customer_id = rec.company_id.pcof_key+customer_id
		self.write(cr, uid, rec.id, {'customer_id':new_customer_id}, context=context)
		context.update({'branch':browse_location_company})
		self.sync_update_product_request(cr,uid,ids,context=context)
		return res

	def cancel_product_request(self,cr,uid,ids,context=None):
		crm_lead_obj = self.pool.get('crm.lead')	
		rec = self.browse(cr, uid, ids[0])
		main_id =rec.id
		search_location_company = self.pool.get('product.request.locations').search(cr,uid,[('location_request_id','=',main_id)])
		browse_location_company = self.pool.get('product.request.locations').browse(cr,uid,search_location_company[0]).branch_id.id
		if not rec.cancellation_reason:
			raise osv.except_osv(_('Warning!'),_("Please enter reason for cancellation!"))
		res = self.write(cr,uid,ids,{'state':'cancel'})
		crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'cancel'}, context=context)
		context.update({'branch':browse_location_company})
		self.sync_cancel_product_request(cr,uid,ids,context=context)
		return res

	def product_request_cancel(self,cr,uid,ids,context=None):	
		primary_data = self.browse(cr, uid, ids[0])
		phone_psd_obj = self.pool.get('phone.number.new.psd')
		models_data = self.pool.get('ir.model.data')
		search_numbers = phone_psd_obj.search(cr,uid,[('phone_product_request_id','=',ids[0])])
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

	# def cancel_product_request(self,cr,uid,ids,context=None):	
	# 	primary_data = self.browse(cr, uid, ids[0])
	# 	if not primary_data.name :
	# 		raise osv.except_osv(("Alert!"),("Please enter 'Customer / Company Name'!"))
	# 	if not primary_data.first_name :
	# 		raise osv.except_osv(("Alert!"),("Please enter 'First Name'!"))
	# 	if not primary_data.last_name :
	# 		raise osv.except_osv(("Alert!"),("Please enter 'Last Name'!"))
	# 	if not primary_data.premise_type :
	# 		raise osv.except_osv(("Alert!"),("Please enter 'Premise Type'!"))
	# 	if not primary_data.apartment :
	# 		raise osv.except_osv(("Alert!"),("Please enter 'Apartment'!"))			
	# 	if not primary_data.building :
	# 		raise osv.except_osv(("Alert!"),("Please enter 'Building Name'!"))
	# 	if not primary_data.ref_by :
	# 		raise osv.except_osv(("Alert!"),("Please Enter 'Reference by'!"))	
	# 	if not primary_data.customer_type:
	# 		raise osv.except_osv(("Alert!"),("Please select 'Customer Type'!"))					
	# 	if primary_data.zip :
	# 		if len(primary_data.zip) < 6 or len(primary_data.zip) > 6:
	# 			raise osv.except_osv(("Alert!"),("Pincode must be 6 digits long!"))
	# 	self.write(cr,uid,ids,{'state':'cancel'})
	# 	return True

	def close_product_request(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])	
		models_data = self.pool.get('ir.model.data')
		global_search_obj = self.pool.get('ccc.branch')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		form_id = models_data.get_object_reference(cr, uid, 'psd_cid', 'view_ccc_branch_form_psd_inherit_new')	
		global_search_vals = {
			'enquiry_type': 'product_request'
		}	
		global_search_id=global_search_obj.create(cr,uid,global_search_vals,context=context)
		product_data = self.browse(cr, uid, ids[0])
		date_age = global_search_obj.calculate_date_age(cr,uid,ids,product_data.request_date,product_data.closed_date)
		if product_data.state != 'new':
			branch_id = product_data.location_request_line[0].branch_id.id
		else:
			branch_id = False
		if product_data.customer_type == 'existing':
			phone = product_data.phone_many2one.number
		else:
			phone = product_data.phone_many2one_new.number
		if product_data.state == 'assigned':
			product_request_state = 'progress'
		else:
			product_request_state = product_data.state
		branch_line_vals =  {       
				'ccc_product_id': global_search_id,
				'request_id': product_data.product_request_id,
				'customer_name': product_data.name,
				'branch_id': branch_id,
				'origin': product_data.company_id.name,
				'request_type_psd': 'product_request',
				'date_age': date_age,
				'state': product_request_state,
				'contact_number': phone,
				'sort_date': product_data.request_date,
				'created_by': rec.created_by.id,
				'employee_id': rec.employee_id.id,
				'product_request_id': product_data.id
		}
		branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
		context.update({'hide_create_quotation':True})
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
				self.pool.get('product.request.notes.line').create(cr,uid,{
																'request_id':o.id,
																'comment':o.comment_remark,
																'comment_date':date,
																'user_id':user.id,
																'state':state,
																'product_request_ref':o.product_request_id,
																})
				self.write(cr,uid,ids,{'comment_remark':None})
				self.sync_note_request(cr,uid,ids,context=context)
			else :
				raise osv.except_osv(('Alert!'),('Please Enter Remark.'))
		return True

	def search_record(self, cr, uid, ids, context=None):
		cur_rec = self.browse(cr, uid, ids[0])
		if not cur_rec.name:
			raise osv.except_osv(('Alert!'),('Please mention Customer name into Customer Search!'))
		context = dict(context, active_ids=ids, active_model=self._name)
		res_create_id = self.pool.get("psd.customer.search.wizard").create(cr, uid, {}, context=context)
		return {
		'view_type': 'form',
		'view_mode': 'form',
		'name': _('Search Customer'),
		'res_model': 'psd.customer.search.wizard',
		'res_id': res_create_id,
		'type': 'ir.actions.act_window',
		'target': 'new',
		'context': context,
		'nodestroy': True,
		}

	def add_product_locations(self, cr, uid, ids, context=None):
		partner_obj = self.pool.get('res.partner')
		product_req_loc_obj = self.pool.get('product.request.locations')
		cur_rec = self.browse(cr, uid, ids[0])
		if not cur_rec.cust_address_id_1 and not cur_rec.cust_address_id_2:
			raise osv.except_osv(('Alert!'),('No location selected!.'))
		if cur_rec.cust_address_id_1:
			if not cur_rec.cust_address_id_1.state_id.id:
				raise osv.except_osv(('Alert!'),('Please update the State of the customer.'))
		if cur_rec.cust_address_id_2:
			if not cur_rec.cust_address_id_2.state_id.id:
				raise osv.except_osv(('Alert!'),('Please update the State of the customer.'))
		if cur_rec.customer_type == 'existing':
			partner = cur_rec.cust_address_id_1
			company_id = partner.company_id.id
			if not company_id:
				company_id = partner.partner_id.company_id.id
		if cur_rec.customer_type == 'new':
			partner = cur_rec.cust_address_id_2
			company_id = cur_rec.company_id.id
		if cur_rec.customer_type=='existing' and not cur_rec.ref_by:
			raise osv.except_osv(_('Warning!'),_("Please select 'Reference by'!"))
		# if cur_rec.customer_type=='existing' and not cur_rec.segment:
		# 	raise osv.except_osv(_('Warning!'),_("Please select 'Segment'!"))
		addrs_items = []
		address = ''
		if partner.apartment not in [' ',False,None]:
			addrs_items.append(partner.apartment)
		if partner.building not in [' ',False,None]:
			addrs_items.append(partner.building)
		if partner.sub_area not in [' ',False,None]:
			addrs_items.append(partner.sub_area)
		if partner.landmark not in [' ',False,None]:
			addrs_items.append(partner.landmark)
		if partner.street not in [' ',False,None]:
			addrs_items.append(partner.street)
		if partner.city_id:
			addrs_items.append(partner.city_id.name1)
		if partner.district:
			addrs_items.append(partner.district.name)
		if partner.tehsil:
			addrs_items.append(partner.tehsil.name)
		if partner.state_id:
			addrs_items.append(partner.state_id.name)
		if partner.zip not in [' ',False,None]:
			addrs_items.append(partner.zip)
		if len(addrs_items) > 0:
			last_item = addrs_items[-1]
			for item in addrs_items:
				if item!=last_item:
					address = address+item+','+' '
				if item==last_item:
					address = address+item
		# company_id = partner.company_id.id
		# establishment_type = partner.company_id.establishment_type
		# if not company_id:
		# 	company_id = partner.partner_id.company_id.id
		# 	establishment_type = partner.partner_id.company_id.establishment_type
		# if establishment_type not in ['psd','branch','base']:
		# 	branch_id = False
		# else:
		# 	branch_id = company_id
		pro_loc_vals = {
			'address': address,
			'location_request_id': ids[0],
			'exempted': partner.exempted,
			'branch_id': company_id,
		}	
		if cur_rec.customer_type == 'existing':
			pro_loc_vals.update({'address_id': partner.id})
		if cur_rec.customer_type == 'new':
			pro_loc_vals.update({'address_id_2': partner.id})	
		res_id = product_req_loc_obj.create(cr, uid, pro_loc_vals, context=context)
		self.write(cr, uid, ids[0], {'confirm_check':True,'hide_search':True,'hide_ref':True}, context=context)
		return res_id	

	def cancel_and_create_new_request(self, cr, uid, ids, context=None):
		rec = self.browse(cr, uid, ids[0])
		models_data=self.pool.get('ir.model.data')
		form_view = models_data.get_object_reference(cr,uid,'psd_cid','view_product_request_form_crm')
		if rec.request_cancellation_type == 'existing_loction':
			if not rec.new_partner_id:
				raise osv.except_osv(_('Warning!'),_("Please enter the customer!"))
			pro_id = self.existing_customer_existing_location(cr, uid, ids, context=context)
			return {
				'type':'ir.actions.act_window',
				'name': 'Product Request',
				'view_type':'form',
				'view_mode':'form',
				'res_model':'product.request',
				'view_id':form_view[1],
				'res_id': pro_id,
				'target':'current',
				'context': context
			}
		elif rec.request_cancellation_type == 'new_location':
			if not rec.new_partner_id:
				raise osv.except_osv(_('Warning!'),_("Please enter the customer!"))
			pro_id = self.existing_customer_new_location(cr, uid, ids, context=context)
			return {
				'type':'ir.actions.act_window',
				'name': 'Product Request',
				'view_type':'form',
				'view_mode':'form',
				'res_model':'product.request',
				'view_id':form_view[1],
				'res_id': pro_id,
				'target':'current',
				'context': context
			}

	def existing_customer_existing_location(self, cr, uid, ids, context=None):
		rec = self.browse(cr, uid, ids[0])
		crm_lead_obj = self.pool.get('crm.lead')
		partner_obj = self.pool.get('res.partner')
		cust_source_obj = self.pool.get('customer.source') 
		product_request_line_obj = self.pool.get('product.request.line')
		partner_addr_obj = self.pool.get('res.partner.address')
		customer_line_obj = self.pool.get('customer.line')
		cust_pro_ids =  self.search(cr, uid, [('partner_id','=',rec.partner_id.id),('state','!=','cancel')], context=context)	
		current_req = cust_pro_ids.index(ids[0])
		cust_pro_ids.pop(current_req)
		if cust_pro_ids:
			location_request_id = rec.location_request_line[0]
			addr_id = partner_addr_obj.search(cr, uid, [
					('partner_id','=',rec.partner_id.id),
					('first_name','=',rec.first_name),
					('last_name','=',rec.last_name),
					('apartment','=',rec.apartment),
					('building','=',rec.building),
					('premise_type','=',rec.premise_type),
					('state_id','=',rec.state_id.id),
			], context=context)
			if addr_id:
				customer_line_id = customer_line_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('customer_address','=',addr_id[0])], context=context)
				partner_addr_obj.unlink(cr, uid, addr_id[0], context=context)
				if customer_line_id:
					customer_line_obj.unlink(cr, uid, customer_line_id[0], context=context)
				primary_addr_ids = partner_addr_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('primary_contact','=',True)], context=context)
				if not primary_addr_ids:
					partner_addr_ids = partner_addr_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id)], context=context)
					if partner_addr_ids:
						partner_addr_obj.write(cr, uid, partner_addr_ids[0], {'primary_contact': True}, context=context)
		if not cust_pro_ids:
			partner_obj.write(cr, uid, rec.partner_id.id, {'active':False},context=context)
		self.write(cr, uid, ids[0], {
			'state':'cancel',
			'cancel_request': True,
			'request_cancellation_type': rec.request_cancellation_type,
			'cancellation_reason': 'Cancelled due to selection of existing customer'
		}, context=context)
		crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'cancel'}, context=context)
		ref_id = cust_source_obj.search(cr, uid, [('name','=','Existing/Old Customer')], context=context)	
		pro_req_vals = {
			'name': rec.new_partner_id.name,
			'title': rec.new_partner_id.title,
			'first_name': rec.new_partner_id.first_name,
			'middle_name': rec.new_partner_id.middle_name, 
			'last_name': rec.new_partner_id.last_name, 
			'designation': rec.new_partner_id.designation, 
			'premise_type': rec.new_partner_id.premise_type, 
			'building': rec.new_partner_id.building, 
			'location_name': rec.new_partner_id.location_name, 
			'apartment': rec.new_partner_id.apartment,
			'sub_area': rec.new_partner_id.sub_area,
			'street': rec.new_partner_id.street,
			'landmark': rec.new_partner_id.landmark,
			'tehsil': rec.new_partner_id.tehsil and rec.new_partner_id.tehsil.id,
			'state_id': rec.new_partner_id.state_id and rec.new_partner_id.state_id.id,
			'city_id': rec.new_partner_id.city_id and rec.new_partner_id.city_id.id,
			'district': rec.new_partner_id.district and rec.new_partner_id.district.id ,
			'zip': rec.new_partner_id.zip,
			'email': rec.new_partner_id.email,
			'fax': rec.new_partner_id.fax,
			'phone_many2one': rec.new_partner_id.phone_many2one and rec.new_partner_id.phone_many2one.id,
			'ref_by': ref_id[0],
			'inquiry_type': 'product',
			'call_type': rec.call_type,
			'state': 'new',
			'confirm_check': True,
			'request_date': datetime.now(),
			'created_by': uid,
			'customer_type': 'existing',
			'segment': rec.segment,
			# 'hide_search': True,
			# 'hide_ref': True,
			'hide_segment': True,
			'partner_id': rec.new_partner_id.id,
			'customer_id': rec.new_partner_id.ou_id,	
		}
		pro_id = self.create(cr, uid, pro_req_vals, context=context)
		return pro_id

	def existing_customer_new_location(self, cr, uid, ids, context=None):
		rec = self.browse(cr, uid, ids[0])
		models_data=self.pool.get('ir.model.data')
		crm_lead_obj = self.pool.get('crm.lead')
		partner_obj = self.pool.get('res.partner')
		cust_source_obj = self.pool.get('customer.source') 
		product_request_line_obj = self.pool.get('product.request.line')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		partner_addr_obj = self.pool.get('res.partner.address')
		customer_line_obj = self.pool.get('customer.line')
		phone_m2m_obj = self.pool.get('phone.m2m')
		phone_m2m_id = False
		cust_pro_ids =  self.search(cr, uid, [('partner_id','=',rec.partner_id.id),('state','!=','cancel')], context=context)	
		current_req = cust_pro_ids.index(ids[0])
		cust_pro_ids.pop(current_req)
		if cust_pro_ids:
			location_request_id = rec.location_request_line[0]
			addr_id = partner_addr_obj.search(cr, uid, [
					('partner_id','=',rec.partner_id.id),
					('first_name','=',rec.first_name),
					('last_name','=',rec.last_name),
					('apartment','=',rec.apartment),
					('building','=',rec.building),
					('premise_type','=',rec.premise_type),
					('state_id','=',rec.state_id.id),
			], context=context)
			if addr_id:
				customer_line_id = customer_line_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('customer_address','=',addr_id[0])], context=context)
				partner_addr_obj.unlink(cr, uid, addr_id[0], context=context)
				if customer_line_id:
					customer_line_obj.unlink(cr, uid, customer_line_id[0], context=context)
				primary_addr_ids = partner_addr_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id),('primary_contact','=',True)], context=context)
				if not primary_addr_ids:
					partner_addr_ids = partner_addr_obj.search(cr, uid, [('partner_id','=',rec.partner_id.id)], context=context)
					if partner_addr_ids:
						partner_addr_obj.write(cr, uid, partner_addr_ids[0], {'primary_contact': True}, context=context)
		if not cust_pro_ids:
			partner_obj.write(cr, uid, rec.partner_id.id, {'active':False},context=context)
		self.write(cr, uid, ids[0], {
			'state':'cancel',
			'cancel_request': True,
			'request_cancellation_type': rec.request_cancellation_type,
			'cancellation_reason': 'Cancelled due to selection of existing customer'
		}, context=context)
		crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'cancel'}, context=context)
		address_vals = {
			'first_name': rec.first_name,
			'last_name': rec.last_name,
			'middle_name': rec.middle_name,
			'designation': rec.designation,
			'premise_type': rec.premise_type,
			'location_name': rec.location_name,
			'apartment': rec.apartment,
			'building': rec.building,
			'sub_area': rec.sub_area,
			'street': rec.street,
			'landmark': rec.landmark,
			'city_id': rec.city_id.id or False,
			'district': rec.district.id or False,
			'tehsil': rec.tehsil.id or False,
			'state_id': rec.state_id.id or False,
			'zip': rec.zip,
			'fax': rec.fax,
			'email': rec.email,
			'ref_by': rec.ref_by.id or False,
			'partner_id': rec.new_partner_id.id,
		}	
		if rec.middle_name and rec.last_name:
			name = rec.first_name+' '+rec.middle_name+' '+rec.last_name
		if not rec.middle_name and not rec.last_name:
			name = rec.first_name
		if rec.middle_name and not rec.last_name:	
			name = rec.first_name+' '+rec.middle_name
		if not rec.middle_name and rec.last_name:	
			name = rec.first_name+' '+rec.last_name
		address_vals.update({'name': name})	
		address_id = partner_addr_obj.create(cr, uid, address_vals, context=context)
		if rec.phone_many2one_new:
			phone_m2m_id = phone_m2m_obj.create(cr, uid, {
				'res_location_id': address_id,
				'name': rec.phone_many2one_new.number,
				'type': rec.phone_many2one_new.type
			}, context=context)	
		partner_addr_obj.write(cr, uid, address_id, {'phone_m2m_xx':phone_m2m_id}, context=context)
		branch = rec.location_request_line[0].branch_id.id
		cust_line_vals = {
			'location_id': 'P155'+str(address_id),
			'premise_type_import': rec.premise_type,
			'branch': branch,
			'customer_address': address_id,
			'partner_id': rec.new_partner_id.id,
			'phone_many2one': phone_m2m_id
		}
		cust_line_id = customer_line_obj.create(cr, uid, cust_line_vals, context=context)	
		ref_id = cust_source_obj.search(cr, uid, [('name','=','Existing/Old Customer')], context=context)
		pro_req_vals = {
			'name': rec.new_partner_id.name,
			'title': rec.new_partner_id.title,
			'first_name': rec.new_partner_id.first_name,
			'middle_name': rec.new_partner_id.middle_name, 
			'last_name': rec.new_partner_id.last_name, 
			'designation': rec.new_partner_id.designation, 
			'premise_type': rec.new_partner_id.premise_type, 
			'building': rec.new_partner_id.building, 
			'location_name': rec.new_partner_id.location_name, 
			'apartment': rec.new_partner_id.apartment,
			'sub_area': rec.new_partner_id.sub_area,
			'street': rec.new_partner_id.street,
			'landmark': rec.new_partner_id.landmark,
			'tehsil': rec.new_partner_id.tehsil and rec.new_partner_id.tehsil.id,
			'state_id': rec.new_partner_id.state_id and rec.new_partner_id.state_id.id,
			'city_id': rec.new_partner_id.city_id and rec.new_partner_id.city_id.id,
			'district': rec.new_partner_id.district and rec.new_partner_id.district.id ,
			'zip': rec.new_partner_id.zip,
			'email': rec.new_partner_id.email,
			'fax': rec.new_partner_id.fax,
			'phone_many2one': rec.new_partner_id.phone_many2one and rec.new_partner_id.phone_many2one.id,
			'inquiry_type': 'product',
			'call_type': rec.call_type,
			'state': 'new',
			'confirm_check': True,
			'request_date': datetime.now(),
			'created_by': uid,
			'customer_type': 'existing',
			'segment': rec.segment,
			'ref_by': ref_id[0],
			# 'hide_search': True,
			# 'hide_ref': True,
			'hide_segment': True,
			'partner_id': rec.new_partner_id.id,
			'customer_id': rec.new_partner_id.ou_id
		}
		pro_id = self.create(cr, uid, pro_req_vals, context=context)
		for location_line_data in rec.location_request_line:
			prod_req_loc_obj.create(cr, uid, 
				{
					'address': location_line_data.address,
					'address_id_2': location_line_data.address_id_2,
					'product_generic_id': location_line_data.product_generic_id.id,
					'sku_name_id': location_line_data.sku_name_id.id or False,
					'product_uom_id': location_line_data.product_uom_id.id,
					'branch_id': location_line_data.branch_id.id,
					'quantity': location_line_data.quantity,
					'remarks': location_line_data.remarks,
					'exempted':location_line_data.exempted,
					'location_request_id': pro_id,
				}, context=context)
		return pro_id	

	def send_to_other_branch(self, cr, uid, ids, context=None):
		models_data=self.pool.get('ir.model.data')
		global_search_obj = self.pool.get('ccc.branch')
		branch_req_line_obj = self.pool.get('ccc.branch.request.line')
		partner_obj = self.pool.get('res.partner')
		form_id = models_data.get_object_reference(cr, uid, 'psd_cid', 'view_ccc_branch_form_psd_inherit_new')	
		crm_lead_obj = self.pool.get('crm.lead')
		prod_req_loc_obj = self.pool.get('product.request.locations')
		rec = self.browse(cr, uid, ids[0])
		pro_ids = []
		if not rec.other_branch_id:
			raise osv.except_osv(_('Warning!'),_("Please select the branch!"))
		self.write(cr, uid, ids[0], {
			'state':'cancel',
			'cancel_request': True,
			'request_cancellation_type': rec.request_cancellation_type,
			'cancellation_reason': 'Cancelled as the request is sent to other branch'
		}, context=context)
		pro_ids.append(ids[0])
		crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', ids[0])], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'cancel'}, context=context)	
		inc_no = '001'
		cust_prefix = False
		customer_seq = partner_obj.browse(cr, uid,  rec.partner_id.id).ou_id
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
		pr_code = 'PR'	
		if rec.other_branch_id.id != rec.company_id.id:
			pr_code = 'PRO'		
		pr_seq = rec.company_id.pcof_key + pr_code + customer_inc_no + inc_no		
		pro_req_vals = {
			'name': rec.partner_id.name,
			'title': rec.partner_id.title,
			'first_name': rec.partner_id.first_name,
			'middle_name': rec.partner_id.middle_name, 
			'last_name': rec.partner_id.last_name, 
			'designation': rec.partner_id.designation, 
			'premise_type': rec.partner_id.premise_type, 
			'building': rec.partner_id.building, 
			'location_name': rec.partner_id.location_name, 
			'apartment': rec.partner_id.apartment,
			'sub_area': rec.partner_id.sub_area,
			'street': rec.partner_id.street,
			'landmark': rec.partner_id.landmark,
			'tehsil': rec.partner_id.tehsil and rec.partner_id.tehsil.id,
			'state_id': rec.partner_id.state_id and rec.partner_id.state_id.id,
			'city_id': rec.partner_id.city_id and rec.partner_id.city_id.id,
			'district': rec.partner_id.district and rec.partner_id.district.id ,
			'zip': rec.partner_id.zip,
			'email': rec.partner_id.email,
			'fax': rec.partner_id.fax,
			'phone_many2one': rec.partner_id.phone_many2one and rec.partner_id.phone_many2one.id,
			'ref_by': rec.partner_id.ref_by and rec.partner_id.ref_by.id,
			'inquiry_type': 'product',
			'call_type': rec.call_type,
			'state': 'open',
			'confirm_check': True,
			'request_date': datetime.now(),
			'created_by': uid,
			'customer_type': 'existing',
			'segment': rec.segment,
			'hide_search': True,
			'hide_ref': True,
			'hide_segment': True,
			'partner_id': rec.partner_id.id,
			'customer_id': rec.partner_id.ou_id,
			'product_request_id': pr_seq,	
		}
		pro_id = self.create(cr, uid, pro_req_vals, context=context)
		for location_line_data in rec.location_request_line:
			prod_req_loc_obj.create(cr, uid, 
				{
					'address': location_line_data.address,
					'address_id_2': location_line_data.address_id_2,
					'product_generic_id': location_line_data.product_generic_id.id,
					'sku_name_id': location_line_data.sku_name_id.id or False,
					'product_uom_id': location_line_data.product_uom_id.id,
					'branch_id': rec.other_branch_id.id,
					'quantity': location_line_data.quantity,
					'remarks': location_line_data.remarks,
					'exempted':location_line_data.exempted,
					'location_request_id': pro_id,
					'product_request_ref': pr_seq
			}, context=context)
		pro_ids.append(pro_id)
		partner_obj.write(cr, uid, rec.partner_id.id, {'active':False},context=context)
		global_search_id=global_search_obj.create(cr,uid,{'enquiry_type': 'product_request'},context=context)
		for each in pro_ids:
			product_req_data = self.browse(cr, uid, each)
			date_age = global_search_obj.calculate_date_age(cr,uid,each,product_req_data.request_date,product_req_data.closed_date)
			branch_line_vals =  {       
					'ccc_product_id': global_search_id,
					'request_id': product_req_data.product_request_id,
					'customer_name': product_req_data.name,
					'branch_id': product_req_data.location_request_line[0].branch_id.id,
					'origin': product_req_data.company_id.name,
					'request_type_psd': 'product_request',
					'date_age': date_age,
					'state': product_req_data.state,
					'contact_number': product_req_data.phone_many2one_new and product_req_data.phone_many2one_new.number,
					'sort_date': product_req_data.request_date,
					'created_by': product_req_data.created_by.id,
					'employee_id': product_req_data.employee_id.id,
					'product_request_id': product_req_data.id
			}
			branch_re_id = branch_req_line_obj.create(cr, uid, branch_line_vals, context=context)
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

	def generate_sales_product_quotation(self, cr, uid, ids, context=None):
		if not isinstance(ids, (list)):
			ids = [ids]
		if context is None:
			context = {}
		product_basic_rate = False
		product_mrp = False
		batch_number = False
		manufacturing_date = False
		address = False
		product_quotation_obj = self.pool.get('psd.sales.product.quotation')
		partner_address_obj = self.pool.get('res.partner.address')
		psd_sales_lines_obj = self.pool.get('psd.sales.lines')
		search_product_quotation_obj = self.pool.get('search.product.quotation')
		models_data=self.pool.get('ir.model.data')
		psd_sales_ids = []
		product_req_data = self.browse(cr, uid, ids[0])
		partner_address_id = partner_address_obj.search(cr, uid, [('partner_id','=',product_req_data.partner_id.id)], context=context)
		quotation_vals = {
			'name': product_req_data.name,
			'partner_id':product_req_data.partner_id.id,
			# 'delivery_location_id': partner_address_id[0],
			# 'contact_person': product_req_data.partner_id.contact_name,
			# 'billing_location_id': partner_address_id[0],
			'pse_id': product_req_data.employee_id.id,
			'request_id':product_req_data.product_request_id,
			# 'psd_sales_id':  psd_sales_ids,
		}
		res = product_quotation_obj.create(cr, uid, quotation_vals, context=context)
		for loc_req_line in product_req_data.location_request_line:
			product_generic_id = loc_req_line.product_name.id
			product_uom_id = loc_req_line.product_uom_id.id
			product_quantity = loc_req_line.quantity
			# sku_name_id = loc_req_line.sku_name_id.id
			exempted = loc_req_line.exempted
			igst_check = product_req_data.partner_id.igst_check
			company_id = product_req_data.company_id.state_id.id
			partner_state = product_req_data.partner_id.state_id.id
			print igst_check,company_id,partner_state
			
			if company_id != partner_state:
				if igst_check == False:
					raise osv.except_osv(('Warning!'),('IGST Quotation cannot be created without approval'))

			if product_req_data.customer_type == "existing":
				if loc_req_line.address_id:
					address = loc_req_line.address_id
			else:
				addr_id = partner_address_obj.search(cr, uid, [
										('partner_id','=',product_req_data.partner_id.id),
										('first_name','=',product_req_data.first_name),
										('last_name','=',product_req_data.last_name),
										('apartment','=',product_req_data.apartment),
										('building','=',product_req_data.building),
										('premise_type','=',product_req_data.premise_type),
										('state_id','=',product_req_data.state_id.id),
										], context=context)
				if addr_id:
					address = addr_id[0]
			vat_id_list =[]
			vat_id = False
			track_equipment = False
			search_tax_id = False
			search_state = partner_address_obj.browse(cr,uid,address).state_id.id
			if product_req_data.company_id.state_id.id == search_state:
				if exempted:
					search_tax_id = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Exempted')])
					vat_id_list.append(search_tax_id[0])
				else:
					if loc_req_line.product_name:
						# for each in loc_req_line.product_generic_id.product_group_id:
						# search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',each.tax_name.id),('description','=','vat')])
						search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',loc_req_line.product_name.product_tax.id),('description','=','gst')])						
						if search_tax_id:
							vat_id_list.append(search_tax_id[0])
			else:
				if exempted:
					search_tax_id = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Exempted')])
					vat_id_list.append(search_tax_id[0])
				else:
					if loc_req_line.product_name:
						# for each in loc_req_line.product_generic_id.product_group_id:
						search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',loc_req_line.product_name.product_tax.id),('description','=','gst')])
						if search_tax_id:
							vat_id_list.append(search_tax_id[0])
			if product_generic_id:
				sku_data = self.pool.get('product.product').browse(cr,uid,product_generic_id)
				if sku_data.type_product == "track_equipment":
					track_equipment = True
				product_obj = self.pool.get('product.product')
				search_product = product_obj.search(cr,uid,[('id','=',product_generic_id)])
				product_name = product_obj.browse(cr,uid,search_product[0])
				print product_name.id
				hsn_code = product_name.hsn_sac_code
				if product_name.batch_type == 'non_applicable':
					search_rec = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name.id),('batch_no','=','NA')])
				else:
					search_rec = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name.id),('batch_no','!=',False)])
				if search_rec == []:
					raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(loc_req_line.product_name.name_template))
				if len(search_rec) > 1:
					dict1= {}
					manufacture_date = []
					for val in self.pool.get('res.batchnumber').browse(cr,uid,search_rec):
						# if val.distributor != 0.00 and val.mrp != 0.00:
						if val.st != 0.0:
							distributor =  val.distributor
							mrp = val.mrp 
							manufacture_dt = val.manufacturing_date
							manufacture_date.append([manufacture_dt,val.id])
					manufacture_date.sort()
					rec_search = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',manufacture_date[-1][1]),('manufacturing_date','=',manufacture_date[-1][0]),('name','=',product_name.id)])
					rec1 = self.pool.get('res.batchnumber').browse(cr,uid,rec_search[0])
					product_basic_rate = rec1.st
					product_mrp = rec1.mrp
					#############changes added for the new fields shreyas
					batch_number = rec1.id
					manufacturing_date = rec1.manufacturing_date
				if len(search_rec) == 1:
					x = self.pool.get('res.batchnumber').browse(cr,uid,search_rec[0])
					product_basic_rate = x.st
					product_mrp = x.mrp
					#############changes added for the new fields shreyas
					batch_number = x.id
					manufacturing_date = x.manufacturing_date
				print product_basic_rate
			if len(vat_id_list) > 0 :
				vat_id = vat_id_list[0]
			else:
				vat_id = False
			psd_sales_lines_vals = {
				'product_name_id': product_generic_id,
				# 'sku_name_id':loc_req_line.sku_name_id.id or False,
				'hsn_code':hsn_code,
				'track_equipment':track_equipment,
				'exempted':loc_req_line.exempted,
				'product_uom_id': product_uom_id,
				'quantity':product_quantity,
				'product_basic_rate':product_basic_rate,
				'product_mrp':product_mrp,
				'vat_id':vat_id,
				'batch_number':batch_number,
				'manufacturing_date':manufacturing_date,
				'psd_sales_lines_id': int(res)
			}
			psd_sales_lines_obj.create(cr, uid, psd_sales_lines_vals, context=context)
		partner_rec = partner_address_obj.browse(cr,uid,address)
		contact_person = str(partner_rec.first_name)+' '+str(partner_rec.last_name)
		product_quotation_obj.write(cr,uid,int(res),{'contact_person':contact_person,'delivery_location_id':address,'billing_location_id':address})
		self.write(cr, uid, ids, {'product_quotation_id': int(res),'psd_sales_entry':True}, context=context)
		# self.write(cr, uid, ids, {'product_quotation_id': res,'state':'quotation'}, context=context)
		if context.get('request_from_sale') == 'request_from_sale':
			return res
		else:
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'view_psd_product_quotation_branch')	
			return {
			   'name':'Product Quotation',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'psd.sales.product.quotation',
			   'res_id': int(res),
			   'type': 'ir.actions.act_window',
			   'target': 'current',
			   'context':context
			}

	def generate_service_quotation(self, cr, uid, ids, context=None):
		if not isinstance(ids, (list)):
			ids = [ids]
		if context is None:
			context = {}
		amc_quotation_obj = self.pool.get('amc.quotation')
		partner_address_obj = self.pool.get('res.partner.address')
		amc_quotation_lines_obj = self.pool.get('amc.quotation.line')
		search_amc_quotation_obj = self.pool.get('search.amc.quotation')
		address = False
		models_data=self.pool.get('ir.model.data')
		product_req_data = self.browse(cr, uid, ids[0])
		partner_address_id = partner_address_obj.search(cr, uid, [('partner_id','=',product_req_data.partner_id.id)], context=context)
		quotation_vals = {
			'name': product_req_data.name,
			'partner_id':product_req_data.partner_id.id,
			# 'product_request_id':product_req_data.id,
			# 'site_address': partner_address_id[0],
			# 'contact_person': product_req_data.partner_id.contact_name,
			# 'billing_address': partner_address_id[0],
			'pse': product_req_data.employee_id.id,
			'request_id':product_req_data.product_request_id,		
		}
		print quotation_vals
		res = amc_quotation_obj.create(cr, uid, quotation_vals, context=context)
		print res
		for loc_req_line in product_req_data.location_request_line:
			amc_flag = loc_req_line.product_name.amc_product
			product_generic_id = loc_req_line.product_name.id
			if product_req_data.customer_type == "existing":
				if loc_req_line.address_id:
					address = loc_req_line.address_id
			else:
				addr_id = partner_address_obj.search(cr, uid, [
										('partner_id','=',product_req_data.partner_id.id),
										('first_name','=',product_req_data.first_name),
										('last_name','=',product_req_data.last_name),
										('apartment','=',product_req_data.apartment),
										('building','=',product_req_data.building),
										('premise_type','=',product_req_data.premise_type),
										('state_id','=',product_req_data.state_id.id),
										], context=context)
				if addr_id:
					address = addr_id[0]
			if not amc_flag:
				raise osv.except_osv(_('Warning!'),_("You can not create Service Quotation for product '%s' as it is not an AMC product'!")%(loc_req_line.product_name.name))
			product_generic_id = loc_req_line.product_name.id
			product_uom_id = loc_req_line.product_uom_id.id
			product_quantity = loc_req_line.quantity
			# rate_per_unit = 
			# sku_name_id = loc_req_line.sku_name_id.id
			print product_generic_id,int(res),product_quantity,'==========================='
			if product_generic_id:
				# if sku_data.type_product == "track_equipment":
				# 	track_equipment = True
				product_obj = self.pool.get('product.product')
				search_product = product_obj.search(cr,uid,[('id','=',product_generic_id)])
				product_name = product_obj.browse(cr,uid,search_product[0])
				hsn_code = product_name.hsn_sac_code
				if product_name.batch_type == 'non_applicable':
					search_rec = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name.id),('batch_no','=','NA')])
				else:
					search_rec = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name.id),('batch_no','!=',False)])
				if search_rec == []:
					raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(loc_req_line.product_name.name_template))				
				if len(search_rec) > 1:
					dict1= {}
					manufacture_date = []
					for val in self.pool.get('res.batchnumber').browse(cr,uid,search_rec):
						# if val.distributor != 0.00 and val.mrp != 0.00:
						if val.st != 0.0:
							distributor =  val.distributor
							mrp = val.mrp 
							manufacture_dt = val.manufacturing_date
							manufacture_date.append([manufacture_dt,val.id])
					manufacture_date.sort()
					rec_search = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',manufacture_date[-1][1]),('manufacturing_date','=',manufacture_date[-1][0]),('name','=',product_name.id)])
					rec1 = self.pool.get('res.batchnumber').browse(cr,uid,rec_search[0])
					product_basic_rate = rec1.st
					product_mrp = rec1.mrp
					#############changes added for the new fields shreyas
					batch_number = rec1.id
					manufacturing_date = rec1.manufacturing_date
				if len(search_rec) == 1:
					x = self.pool.get('res.batchnumber').browse(cr,uid,search_rec[0])
					product_basic_rate = x.st
					product_mrp = x.mrp
					#############changes added for the new fields shreyas
					batch_number = x.id
					manufacturing_date = x.manufacturing_date
			print product_basic_rate,'product basic rate'
			amc_quotation_lines_vals = {
				'product_generic_name': product_generic_id,
				# 'product_id':loc_req_line.sku_name_id.id or False,
				'amc_quotation_id': int(res),
				'no_of_units':product_quantity,
				'rate_per_unit':product_basic_rate,
			}
			print amc_quotation_lines_vals,'linesssssssssssssss'
			amc_quotation_lines_obj.create(cr, uid, amc_quotation_lines_vals, context=context)
		partner_rec = partner_address_obj.browse(cr,uid,address)
		contact_person = str(partner_rec.first_name)+' '+str(partner_rec.last_name)
		amc_quotation_obj.write(cr,uid,int(res),{'contact_person':contact_person,'site_address':address,'billing_address':address})
		self.write(cr, uid, ids, {'amc_quotation_id1': int(res),'psd_sales_entry':True}, context=context)
		if context.get('request_from_sale') == 'request_from_sale':
			return res
		else:
			form_id = models_data.get_object_reference(cr, uid, 'psd_amc_quotation', 'view_amc_quotation_form')	
			return {
			   'name':'Service Quotation',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'amc.quotation',
			   'res_id': int(res),
			   'type': 'ir.actions.act_window',
			   'target': 'current',
			   'context':context
			}

	def generate_direct_sales_product_order(self, cr, uid, ids, context=None):
		if not isinstance(ids, (list)):
			ids = [ids]
		if context is None:
			context = {}
		product_basic_rate = False
		product_mrp = False
		batch_number = False
		manufacturing_date = False
		address = False
		product_order_obj = self.pool.get('psd.sales.product.order')
		partner_address_obj = self.pool.get('res.partner.address')
		psd_sales_order_lines_obj = self.pool.get('psd.sales.product.order.lines')
		search_product_order_obj = self.pool.get('search.product.order')
		prod_req_line_obj = self.pool.get('product.request.line')
		models_data=self.pool.get('ir.model.data')
		batch_price = self.pool.get('res.batchnumber')
		psd_sales_ids = []
		product_list = []
		generic_name = []
		product_req_data = self.browse(cr, uid, ids[0])
		partner_address_id = partner_address_obj.search(cr, uid, [('partner_id','=',product_req_data.partner_id.id)], context=context)
		quotation_vals = {
			'name': product_req_data.name,
			'partner_id':product_req_data.partner_id.id,
			# 'delivery_location_id': partner_address_id[0],
			# 'contact_person': product_req_data.partner_id.contact_name,
			# 'billing_location_id': partner_address_id[0],
			'pse_id': product_req_data.employee_id.id,
			'request_id':product_req_data.product_request_id,
			'user_id':product_req_data.created_by.id,
			# 'psd_sales_id':  psd_sales_ids,
			# 'quotation_no': seq,			
		}
		res = product_order_obj.create(cr, uid, quotation_vals, context=context)
		for loc_req_line in product_req_data.location_request_line:
			# product_generic_id = loc_req_line.product_generic_id.id
			product_generic_id =  loc_req_line.product_name.id
			product_uom_id = loc_req_line.product_uom_id.id
			product_quantity = loc_req_line.quantity
			# sku_name_id = loc_req_line.sku_name_id.id
			exempted = loc_req_line.exempted
			igst_check = product_req_data.partner_id.igst_check
			company_id = product_req_data.company_id.state_id.id
			partner_state = product_req_data.partner_id.state_id.id
			print igst_check,company_id,partner_state
			
			if company_id != partner_state:
				if igst_check == False:
					raise osv.except_osv(('Warning!'),('IGST Product Order cannot be created without approval'))
			# if not loc_req_line.sku_name_id.name in product_list:
			# 	product_list.append(loc_req_line.sku_name_id.name)
			if not loc_req_line.product_name.name in generic_name:
				generic_name.append(loc_req_line.product_name.name)
			if product_req_data.customer_type == "existing":
				if loc_req_line.address_id:
					address = loc_req_line.address_id
			else:
				addr_id = partner_address_obj.search(cr, uid, [
										('partner_id','=',product_req_data.partner_id.id),
										('first_name','=',product_req_data.first_name),
										('last_name','=',product_req_data.last_name),
										('apartment','=',product_req_data.apartment),
										('building','=',product_req_data.building),
										('premise_type','=',product_req_data.premise_type),
										('state_id','=',product_req_data.state_id.id),
										], context=context)
				if addr_id:
					address = addr_id[0]
			sku_data = self.pool.get('product.product').browse(cr,uid,product_generic_id)
			vat_id_list =[]
			vat_id = False
			track_equipment = False
			search_tax_id = False
			todays_date = datetime.now().date()
			search_state = partner_address_obj.browse(cr,uid,address).state_id.id
			if product_req_data.company_id.state_id.id == search_state:
				if exempted:
					search_tax_id = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Exempted')])
					vat_id_list.append(search_tax_id[0])
				else:
					print loc_req_line.product_name
					if loc_req_line.product_name:
						# for each in loc_req_line.product_name:
						# 	print each
							search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',loc_req_line.product_name.product_tax.id),('description','=','gst')])
							if search_tax_id:
								vat_id_list.append(search_tax_id[0])
			else:
				if exempted:
					search_tax_id = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Exempted')])
					vat_id_list.append(search_tax_id[0])
				else:
					# if loc_req_line.product_generic_id.product_group_id:
					# 	for each in loc_req_line.product_generic_id.product_group_id:
					print loc_req_line.product_name
					if loc_req_line.product_name:
							search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',loc_req_line.product_name.product_tax.id),('description','=','gst')])
							browse_tax_id = self.pool.get('account.tax').browse(cr,uid,search_tax_id)[0]
							print browse_tax_id

							# print search_tax_id
							# bb
							# if search_tax_id:
							# 	vat_id_list.append(search_tax_id[0])

			if product_generic_id:
				if sku_data.type_product == "track_equipment":
					track_equipment = True
				product_obj = self.pool.get('product.product')
				search_product = product_obj.search(cr,uid,[('id','=',product_generic_id)])
				product_name = product_obj.browse(cr,uid,search_product[0])
				hsn_code = product_name.hsn_sac_code
				if product_name.batch_type == 'non_applicable':
					search_rec = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name.id),('batch_no','=','NA')])
				else:
					search_rec = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name.id),('batch_no','!=',False)])
				if search_rec == []:
					raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(loc_req_line.product_name.name_template))				
				if len(search_rec) > 1:
					dict1= {}
					manufacture_date = []
					for val in self.pool.get('res.batchnumber').browse(cr,uid,search_rec):
						# if val.distributor != 0.00 and val.mrp != 0.00:
						if val.st != 0.0:
							distributor =  val.distributor
							mrp = val.mrp 
							manufacture_dt = val.manufacturing_date
							manufacture_date.append([manufacture_dt,val.id])
					manufacture_date.sort()
					rec_search = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',manufacture_date[-1][1]),('manufacturing_date','=',manufacture_date[-1][0]),('name','=',product_name.id)])
					rec1 = self.pool.get('res.batchnumber').browse(cr,uid,rec_search[0])
					product_basic_rate = rec1.st
					product_mrp = rec1.mrp
					#############changes added for the new fields shreyas
					batch_number = rec1.id
					manufacturing_date = rec1.manufacturing_date
				if len(search_rec) == 1:
					x = self.pool.get('res.batchnumber').browse(cr,uid,search_rec[0])
					product_basic_rate = x.st
					product_mrp = x.mrp
					#############changes added for the new fields shreyas
					batch_number = x.id
					manufacturing_date = x.manufacturing_date
			if len(vat_id_list) > 0 :
				vat_id = vat_id_list[0]
			else:
				vat_id = False
			# vat1 = self.pool.get('account.tax').search(cr,uid,[('id','=',vat_id)])
			# vat = self.pool.get('account.tax').browse(cr,uid,vat1)[0]
			# amount = vat.amount
			# print vat,amount
			psd_sales_lines_vals = {
				'product_name_id': product_generic_id,
				# 'sku_name_id':loc_req_line.sku_name_id.id or False,
				'product_uom_id': product_uom_id,
				'track_equipment':track_equipment,
				'exempted':loc_req_line.exempted,
				# 'ordered_quantity':product_quantity,
				'allocated_quantity':product_quantity,
				'product_basic_rate':product_basic_rate,
				'product_mrp':product_mrp,
				'hsn_code':hsn_code,
				# 'igst_rate':vat_id,
				'batch_number':batch_number,
				'manufacturing_date':manufacturing_date,
				'psd_sales_product_order_lines_id': int(res)
			}
			psd_sales_order_lines_obj.create(cr, uid, psd_sales_lines_vals, context=context)
		partner_rec = partner_address_obj.browse(cr,uid,address)
		contact_person = str(partner_rec.first_name)+' '+str(partner_rec.last_name)
		products =', '.join(map(str, product_list))
		generic =', '.join(map(str, generic_name))
		product_order_obj.write(cr,uid,int(res),{'skus':products,'generic':generic,'contact_person':contact_person,'delivery_location_id':address,'billing_location_id':address})
		self.write(cr, uid, ids, {'product_order_id': int(res),'psd_sales_entry':True}, context=context)
		if context.get('request_from_sale') == 'request_from_sale':
			return res
		else:
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'view_psd_product_sale_order_branch')	
			return {
			   'name':'Sale Product Order',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'psd.sales.product.order',
			   'res_id': int(res),
			   'type': 'ir.actions.act_window',
			   'target': 'current',
			   'context':context
			}



	def select_product_request(self,cr,uid,ids,context=None):	
		res = self.write(cr, uid, ids[0], 
			{
				'select_request': True
			})
		return res	

	def deselect_product_request(self,cr,uid,ids,context=None):	
		res = self.write(cr, uid, ids[0], 
			{
				'select_request': False
			})
		return res

	def reload_product_request(self, cr, uid, ids, context=None):
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_cid', 'view_product_request_form_crm')
		view_id = view and view[1] or False
		return {
			'name': _('Product Request'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'product.request',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': ids[0],
		}			

product_request()

class product_request_line(osv.osv):
	_name = 'product.request.line'
	_rec_name = 'address'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'product_request_id':fields.many2one('product.request','Request Id',ondelete='cascade'),
		'product_request_ref': fields.char('Product Request',size=100),
		'address': fields.char('Address', size=100),
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
		'location_name':fields.char('Location Name', size=100),#abhi
		'apartment':fields.char('Apartment / Unit Number',size=600),
		'sub_area':fields.char('Sub Area',size=60),
		'street':fields.char('Street', size=60),
		'tehsil':fields.many2one('tehsil.name','Tehsil'),
		'landmark':fields.char('Landmark',size=60),
		'state_id':fields.many2one('state.name','State'),
		'city_id':fields.many2one('city.name','City'),
		'district':fields.many2one('district.name','District'),
		'zip':fields.char('Pincode ',size=6),
		'email':fields.char('E-Mail', size=60),
		'phone':fields.many2one('phone.number.child','Phone'),
		'phone_new':fields.many2one('phone.number.new.psd','Phone'),
		'fax':fields.char('Fax',size=12),
		'exempted': fields.boolean('Exempted'),
		'exempted_classification': fields.many2one('exempted.classification','Exempted Classification'),
		'certificate_no':fields.char('Certificate Number',size=50),
		'exem_attachment':fields.binary('Attachment',size=124),
		'adhoc_job': fields.boolean('Adhoc-Job'),
		'segment': fields.selection([
			('retail','Retail Segment'),
			('distributor','Distributor Segment'),
			('institutional','Institutional/Govt Segment'),
		   ],'Segment'),
		'primary_contact': fields.boolean('Primary Contact')
	}

	_defaults = {
		'company_id': _get_company
	}

product_request_line()

class product_request_locations(osv.osv):
	_name = 'product.request.locations'
	_rec_name = 'address'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'location_request_id':fields.many2one('product.request','Product Request',ondelete='cascade'),
		'address_id': fields.integer('Address ID'),
		'address_id_2': fields.integer('Address ID 2'),
		'address': fields.char('Addresss',size=200),
		# 'product_generic_id': fields.many2one('product.generic.name','Product Generic Name'),
		# 'sku_name_id':fields.many2one('product.product','SKU Name',domain="[('generic_name','=',product_generic_id)]"),
		'check_sold_by_psd':fields.boolean('PSD'),
		'check_sold_by_ssd': fields.boolean('SSD'),
		'product_uom_id':fields.many2one('product.uom','UOM'),
		'branch_id':fields.many2one('res.company','PCI Office'),
		'quantity':fields.integer('Quantity',size=400),
		'remarks':fields.char('Remarks',size=200),
		'exempted':fields.boolean('Exempted'),
		'product_request_ref': fields.char('Product Request',size=100),
		'product_name':fields.many2one('product.product','Product Name'),
		'available_quantity':fields.float('Available Quantity')
	}   

	_defaults = {
		'company_id': _get_company,
	}

	def onchange_branch_id(self,cr,uid,ids,branch_id):
		v={}
		branch_obj = self.pool.get('res.company')
		if branch_id:
			branch_search = branch_obj.browse(cr,uid,branch_id).establishment_type
			if branch_search == 'branch':
				v['check_sold_by_psd'] = False
				v['check_sold_by_ssd'] = False
			else:
				v['check_sold_by_psd'] = False
				v['check_sold_by_ssd'] = True 
			print v['check_sold_by_ssd'],v['check_sold_by_psd']
		return {'value':v}		

	def onchange_product_generic_id(self,cr,uid,ids,product_name,context=None):
		data = {'product_uom_id':False,'available_quantity':False}
		product_obj = self.pool.get('product.product')
		if product_name:
			product_ids = product_obj.search(cr, uid, [('id','=',product_name)], context=context)
			if product_ids:
				product_data = product_obj.browse(cr,uid,product_ids[0])
				product_uom_id = product_data.product_tmpl_id.local_uom_id.id
				qty_available = product_data.quantity_actual
				data = {'product_uom_id': product_uom_id if product_uom_id else None,
						'available_quantity': qty_available if qty_available else 0.00
					   }
				return {'value':data}

	def onchange_check_sold_by_psd(self,cr,uid,ids,check_sold_by_psd,context=None):
		domain = {}
		if check_sold_by_psd:
			product_generic_ids = self.pool.get('product.generic.name').search(cr,uid,[('sold_by_psd','=','True')],context=context)
			domain = {'product_generic_id': [('id', 'in', product_generic_ids)]}
		else:
			product_generic_ids = self.pool.get('product.generic.name').search(cr,uid,[],context=context)
			domain = {'product_generic_id': [('id', 'in', product_generic_ids)]}
		return {'domain': domain}



product_request_locations()


class product_request_notes_line(osv.osv):
	_name = 'product.request.notes.line'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'request_id':fields.many2one('product.request','Request Id',ondelete='cascade'),
		'user_id':fields.many2one('res.users','User Name'),
		'state':fields.selection([
									('new','New'),
									('open','Opened'),
									('assigned','Resource Assigned'),
									('closed','Closed'),
									('cancel','Cancelled')
									],'State'),
		'comment_date':fields.datetime('Comment Date & Time'),
		'comment':fields.text('Comment',size=400),
		'product_request_ref': fields.char('Product Request',size=100),
	}

	_defaults = {
		'company_id': _get_company
	}

product_request_notes_line()

class product_product(osv.osv):
	_inherit = "product.product"

	_columns = {
		'amc_product':fields.boolean('Is AMC product?'),
		'is_imported':fields.boolean('Is Imported'),
		'psd_sale':fields.boolean('PSD Sale'),
	}

product_product()