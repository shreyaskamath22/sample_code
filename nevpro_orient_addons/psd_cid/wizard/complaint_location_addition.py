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

from datetime import date,datetime, timedelta
from osv import osv,fields
from base.res import res_partner
from tools.translate import _

class complaint_location_addition(osv.osv):
    _name = 'complaint.location.addition'
    _rec_name = 'complaint_id'
    _columns = {
        'title':fields.selection(res_partner.PARTNER_TITLES,'Title'),
        'first_name':fields.char('First Name *',size=25),
        'middle_name':fields.char('Middle Name',size=25),
        'last_name':fields.char('Last Name *',size=25),
        'designation':fields.char('Designation',size=25),
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
        'location_name':fields.char('Location Name', size=60),#abhi
        'apartment':fields.char('Apartment / Unit Number*',size=60),
        'sub_area':fields.char('Sub Area',size=60),
        'street':fields.char('Street', size=60),
        'tehsil':fields.many2one('tehsil.name','Tehsil'),
        'landmark':fields.char('Landmark',size=60),
        'state_id':fields.many2one('state.name','State *'),
        'city_id':fields.many2one('city.name','City'),
        'district':fields.many2one('district.name','District'),
        'zip':fields.char('Pincode ',size=6),
        'email':fields.char('E-Mail', size=60),
        'fax':fields.char('Fax',size=12),
        'phone':fields.many2one('phone.number.new.psd', 'Phone'),
        'complaint_id':fields.many2one('product.complaint.request', 'Complaint ID')
    }    

    def default_get(self,cr,uid,fields,context=None):
        if context is None: context = {}
        active_ids = context.get('active_ids')
        if active_ids:
            active_id = active_ids[0]
        res = super(complaint_location_addition, self).default_get(cr, uid, fields, context=context)
        res.update({'complaint_id':active_id})
        return res

    def create_number_psd(self,cr,uid,ids,context=None):    
        view = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'psd_cid', 'phone_number_pop_up_psd_form')
        view_id = view and view[1] or False
        context.update({'request_type': 'complaint_location','comp_loc_adtn_id':ids[0]})
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

    def save_new_customer_location(self,cr,uid,ids,context=None):
        active_id = context.get('active_id',False)
        complaint_req_obj = self.pool.get('product.complaint.request')
        complaint_req_line_obj = self.pool.get('product.complaint.request.line')
        complaint_cust_line_obj = self.pool.get('complaint.customer.line')
        partner_obj = self.pool.get('res.partner')
        partner_addr_obj = self.pool.get('res.partner.address')
        complaint_loc_obj = self.pool.get('product.complaint.locations')
        complaint_contact_obj = self.pool.get('complaint.locations.contact')
        customer_search_data = self.browse(cr, uid, ids[0])
        complaint_customer_line_ids = complaint_cust_line_obj.search(cr, uid, [('complaint_customer_search_id','=',ids[0]),('select_cust','=',True)], context=context)

        # complaint_line_ids = complaint_req_line_obj.search(cr, uid, [('complaint_id','=',active_id)], context=context)
        # complaint_req_line_obj.unlink(cr, uid, complaint_line_ids, context=context)
        # complaint_loc_ids = complaint_loc_obj.search(cr, uid, [('complaint_id','=',active_id)], context=context)
        # complaint_loc_obj.unlink(cr, uid, complaint_loc_ids, context=context)

        addr_data = self.browse(cr, uid, ids[0])
        addrs_items = []
        complete_address = ''
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
            complaint_loc_vals = {
                'complaint_id': active_id,
                'name': complete_address,
                'addition_id': addr_data.id,
            }
            loc_id = complaint_loc_obj.create(cr, uid, complaint_loc_vals,context=context)
        if addr_data.first_name and addr_data.last_name and not addr_data.middle_name:
            contact_person = addr_data.first_name+' '+addr_data.last_name
        if addr_data.first_name and addr_data.last_name and addr_data.middle_name:
            contact_person = addr_data.first_name+' '+addr_data.middle_name+' '+addr_data.last_name
        complaint_contact_obj.create(cr, uid, {'complaint_id': active_id,'name': contact_person,'loc_id': loc_id},context=context)
        return {'type': 'ir.actions.act_window_close'}

complaint_location_addition()