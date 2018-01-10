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
import time
from tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import timedelta,date,datetime

from datetime import datetime,date
from openerp import netsvc

from openerp.tools.amount_to_text_en import amount_to_text
from openerp.tools import float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT

import xmlrpclib
from openerp import SUPERUSER_ID


#############################################################
# Customized Table for the channels defined for the customer 
##############################################################

class customer_channels(osv.osv):
    _name = 'customer.channels'
    _description = 'Customer Channels'
    _columns = {
        'name': fields.char('Channel',size=890),
        'modern_trade': fields.boolean('Modern Trade'),
        'general_trade': fields.boolean('General Trade'),
        'type_of_channels': fields.selection([('general_trade', 'General Trade'),('modern_trade','Modern Trade')], 'Type of Channels'),
    }

    def onchange_general_trade(self,cr,uid,ids,general_trade):
    	v={}
    	if general_trade:
    		v['type_of_channels'] = 'general_trade'
    		v['modern_trade'] = False
    	return {'value':v}

    def onchange_modern_trade(self,cr,uid,ids,modern_trade):
    	v={}
    	if modern_trade:
    		v['type_of_channels'] = 'modern_trade'
    		v['general_trade'] = False
    	return {'value':v}

customer_channels()

#####################################################################
# Customized Table to define various Zones in openerp for Customers
#####################################################################

class customer_zones(osv.osv):
    _name = 'customer.zones'
    _description = 'Zones'
    _columns = {
        'name': fields.char('Zone',size=890),
        'country_id': fields.many2one('res.country','Country'),
    }

customer_zones()

#############################################
# Inherited the state table to add the zones
#############################################

class CountryState(osv.osv):
    _inherit = 'res.country.state'
    _columns = {
        'customer_zone': fields.many2one('customer.zones', 'Zones', required=True),
    }

CountryState()

#####################################
# Customized table to add the cities
#####################################

# class customer_cities(osv.osv):
#     _name = 'customer.cities'
#     _description = 'City'
#     _columns = {
#         'name': fields.char('City Name',size=890),
#         'state_id': fields.many2one('res.country.state','State'),
#         'zone_id': fields.many2one('customer.zones', 'Zones'),
#         'country_id': fields.many2one('res.country', 'Country'), 
#     }

# customer_cities()

class res_city(osv.osv):
	_inherit = 'res.city'
	_columns = {
			'zone_id': fields.many2one('customer.zones', 'Zones'),
	}

res_city()

#####################################
# Customized table to add the regions
#####################################

class customer_regions(osv.osv):
    _name = 'customer.regions'
    _description = 'Regions'
    _columns = {
        'name': fields.char('Region Name',size=890),
        'city_id': fields.many2one('res.city','City'),
        'state_id': fields.many2one('res.country.state','State'),
        'zone_id': fields.many2one('customer.zones', 'Zones'),
        'country_id': fields.many2one('res.country', 'Country'), 
    }

customer_regions()

###########################
# Customized Customer Table
###########################

class res_partner(osv.osv):
    _inherit="res.partner"
    _columns={
    		'owner_partner_name': fields.char('Name of the Owner/Partner',size=200),
    		'customer_state': fields.selection([('draft', 'Draft'),('waiting_management_approval','Waiting Management Approval'),('customer_created','Customer Created')], 'State'),
    		'type_of_sales': fields.selection([('within_state', 'Within the state/Local'),('interstate','Interstate')], 'Type of Sales'),
    		'cform_criteria': fields.selection([('agreed', 'Agreed'),('disagreed','Disagreed')], 'C-form criteria'),
    		'pan_no': fields.char('Pan No.',size=10),
    		'vat_no': fields.char('VAT No',size=64),
    		'cst_no': fields.char('CST No',size=64),
    		'country_id': fields.many2one('res.country', 'Billing Country'),
    		'billing_city': fields.many2one('res.city','Cities'),
            'billing_destination': fields.char('Billing Destination', size=128),
    		'same_as_above': fields.boolean('Same as Above'),
    		'shipping_street': fields.char('Shipping Street',size=128),
    		'shipping_street2': fields.char('Shipping Street2',size=128),
    		'shipping_city': fields.char(' Shipping City',size=128),
    		'shipping_city2': fields.many2one('res.city','Shipping Cities'),
    		'shipping_state_id': fields.many2one('res.country.state',' Shipping State'),
    		'shipping_zip': fields.char('Shipping Zip',size=24),
    		'shipping_country_id': fields.many2one('res.country','Shipping Country'),
            'shipping_destination': fields.char('Shipping Destination', size=128),
    		'business_commencement_date': fields.date('Business Commencement Date of Dealer'),
            'business_commencement_date_zeeva': fields.date('Business Commencement Date with Zeeva'),
    		'primary_contact': fields.boolean('Primary Contact'),
    		'salesperson':fields.many2many('res.users','users_salespersons_rel','sale_id','res_id','Source of CRF'),
    		'headquarters': fields.many2one('res.partner','Headquarters(HQ)'),
    		'child_ids': fields.one2many('res.partner', 'parent_id', 'Contacts'),
    		'general_trade_channels':fields.many2many('customer.channels','customer_general_trade_rel','partner_id','channel_id','General/Modern Trade'),
    		'general_trade': fields.boolean('General Trade'),
    		'modern_trade': fields.boolean('Modern Trade'),
            'type_of_customer': fields.char('Type of Customer'),
    		'verified_by': fields.many2one('hr.employee','Verified By'),
    		'verified_date': fields.date('Verified Date'),
    		'approved_by': fields.many2one('hr.employee', 'Approved By'),
    		'approved_date': fields.date('Approved Date'),
    		'product_brand':fields.many2many('product.brand','customer_product_brand_rel','partner_id','brand_id','Brands Allowed'),
    		#####################Geographical Location fields
    		'country_id1': fields.many2one('res.country','Geographical Country'),
    		'zone_id': fields.many2one('customer.zones','Geographical Zone'),
    		'state_id1': fields.many2one('res.country.state','Geographical State'),
    		'city_id1': fields.many2one('res.city','Geographical City'),
    		'regions': fields.many2many('customer.regions','customer_regions_rel','partner_id','region_id','Geographical Regions'),
    		'zone_editable': fields.boolean('Zone Editable'),
    		'state_editable': fields.boolean('State Editable'),
    		'city_region_editable': fields.boolean('City Region Editable'),
    		'source_of_crf': fields.many2one('res.users','Source of CRF'),
    		'customer_channels_readonly': fields.boolean('Channels'),
			'road_permit': fields.boolean('Will Provide Road Permit'),
			'grn': fields.boolean('Will Provide GRN'),
            ########################for warehouse location
            'warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
    }

    _defaults={
    	'active': False,
    	'customer_state': 'draft',
    	'is_company': True,
    	'type_of_sales':'within_state',
    	'same_as_above':False,
    	'primary_contact':False,
    	'ref':'/',
    	'notification_email_send':'none',
    	'customer_channels_readonly': False,
    }

    def onchange_country_id1(self,cr,uid,ids,country_id1):
    	v={}
    	if country_id1:
    		v['zone_editable'] = True
    	elif not country_id1:
    		v['zone_editable'] = False
    	return {'value':v}

    def onchange_zone_id(self,cr,uid,ids,zone_id):
    	v={}
    	if zone_id:
    		v['state_editable'] = True
    	elif not zone_id:
    		v['state_editable'] = False
    	return {'value':v}

    def onchange_state_id1(self,cr,uid,ids,state_id1):
    	v={}
    	if state_id1:
    		v['city_region_editable'] = True
    	elif state_id1:
    		v['city_region_editable'] = False
    	return {'value':v}

    def onchange_general_trade(self,cr,uid,ids,general_trade):
    	v={}
    	if general_trade:
    		v['modern_trade'] = False
    		v['customer_channels_readonly'] = True
                v['type_of_customer'] = 'General Trade'
        return {'value':v}

    def onchange_modern_trade(self,cr,uid,ids,modern_trade):
    	v={}
    	if modern_trade:
    		v['general_trade'] = False
    		v['customer_channels_readonly'] = True
                v['type_of_customer'] = 'Modern Trade'
        return {'value':v}


    def create(self, cr, uid, vals, context=None):        
        if context is None:
            context = {}
        if vals.get('general_trade') == False and vals.get('modern_trade') == False:
        	raise osv.except_osv(_("Warning"),("Please select the appropriate channel in the 'General Details' tab."))
        if vals.get('general_trade') == True:
            vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'general.trade') or '/'
        if vals.get('modern_trade') == True:
            vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'modern.trade') or '/'  
        res_id = super(res_partner, self).create(cr, uid, vals, context=context)
        if vals.has_key('name'):
        	name_id = vals.get('name')
        	search_partner_id =self.search(cr,uid,[('name','=',name_id)])
        	if search_partner_id:
        		raise osv.except_osv(_("Warning"),("Every Customer Name must be Unique. The Customer '%s' already exists"%(name_id)))
        return res_id

    def onchange_same_as_above(self,cr,uid,ids,same_as_above,street,street2,city,state_id,zip,country_id,billing_city,billing_destination):
    	v={}
    	if same_as_above:
            v['shipping_street'] = street
            v['shipping_street2'] = street2
            v['shipping_city'] = city
            v['shipping_state_id'] = state_id
            v['shipping_zip'] = zip
            v['shipping_country_id'] = country_id
            v['shipping_city2'] = billing_city
            v['shipping_destination'] = billing_destination
        else:
            v['shipping_street'] = False
            v['shipping_street2'] = False
            v['shipping_city'] = False
            v['shipping_state_id'] = False
            v['shipping_zip'] = False
            v['shipping_country_id'] = False
            v['shipping_city2'] = False
            v['shipping_destination'] = False
    	return {'value':v}


    def onchange_headquarters(self,cr,uid,ids,headquarters):
        result={}
        if not headquarters:
	  		v={'child_ids' : ''}
	  		result = {'value': v}
	  		return result
        if headquarters:
        	val = self.get_primary_contacts(cr, uid, ids, headquarters)
	        if val:
	            for x,y in val.iteritems():
	                if y:
	                    for o in y:
	                        v={'child_ids' : y}
	                        result = {'value': v}
	                        return result
	                else:
	                    v={'child_ids' : ''}
	                    result = {'value': v}
	                    return result

    def get_primary_contacts(self, cr, uid, ids, headquarters):
            result = {}
            line_data = []
            sale_order_obj = self.pool.get('res.partner')
            headquarters_variable = headquarters
            o = self.browse(cr,uid,headquarters)
            for line in o.child_ids:
            	primary_contact = line.primary_contact
            	if primary_contact:
            		line_data.append({
            			'name': line.name,
            			'function': line.function,
            			'email': line.email,
            			'phone': line.phone,
            			'mobile': line.mobile,
            			})
            result[id] = line_data
            return result

    

    def submit_to_management(self,cr,uid,ids,context=None):
    	login_users_append=[]
    	hr_employee_obj = self.pool.get('hr.employee')
    	res_users_obj =self.pool.get('res.users')
        o = self.browse(cr,uid,ids[0])
        main_form_id = o.id
        customer_name = o.name
        user_id = o.user_id.login
        string_uid = [str(user_id)]
        todays_date = datetime.now().date()
        hr_employee_search_id = hr_employee_obj.search(cr,uid,[('user_id','=',uid)])
        employee_id = hr_employee_search_id[0]
        subscribe_ids = []
        cr.execute('select res_id from users_salespersons_rel where sale_id = %s',(main_form_id,))
        res_values = map(lambda x: x[0], cr.fetchall())
        res_users_browse = res_users_obj.browse(cr,uid,res_values)
        for users_id in res_users_browse:
        	login_users = users_id.login
        	login_users_append.append(str(login_users))
        zeeva_ind_management = ['nitin','akshay']
        zeeva_ind_management.extend(login_users_append)
        zeeva_ind_management.extend(string_uid)
        subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',zeeva_ind_management)])
        self.message_subscribe_users(cr, SUPERUSER_ID, [o.id], user_ids=subscribe_ids, context=context)
        message1 = _("<b>Status: Draft --> Waiting Management Approval</b><br/><br/>Dear Sir,<br/><br/>I kindly request you to approve the customer:<b> %s.</b>") % (customer_name,)
        self.message_post(cr, uid, ids, body = message1, type='comment', subtype='mt_comment', context = context)
        self.write(cr,uid,main_form_id,{'customer_state': 'waiting_management_approval','active':False,'verified_by':employee_id,'verified_date':todays_date,'customer_channels_readonly':False})
        return True

    def onchange_shipping_state_id(self, cr, uid, ids, shipping_state_id, context=None):
        if shipping_state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, shipping_state_id, context).country_id.id
            return {'value':{'shipping_country_id':country_id}}
        return {}

    def approved(self,cr,uid,ids,context=None):
    	login_users_append=[]
    	hr_employee_obj = self.pool.get('hr.employee')
    	res_users_obj =self.pool.get('res.users')
        o = self.browse(cr,uid,ids[0])
        main_form_id = o.id
        customer_name = o.name
        user_id = o.user_id.login
        string_uid = [str(user_id)]
        hr_employee_search_id = hr_employee_obj.search(cr,uid,[('user_id','=',uid)])
        employee_id = hr_employee_search_id[0]
        subscribe_ids = []
        cr.execute('select res_id from users_salespersons_rel where sale_id = %s',(main_form_id,))
        res_values = map(lambda x: x[0], cr.fetchall())
        res_users_browse = res_users_obj.browse(cr,uid,res_values)
        for users_id in res_users_browse:
        	login_users = users_id.login
        	login_users_append.append(str(login_users))
        zeeva_ind_management = ['nitin','akshay']
        zeeva_ind_management.extend(login_users_append)
        zeeva_ind_management.extend(string_uid)
        todays_date = datetime.now().date()
        subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',zeeva_ind_management)])
        self.message_subscribe_users(cr, SUPERUSER_ID, [o.id], user_ids=subscribe_ids, context=context)
        message1 = _("<b>Status: Waiting Management Approval --> Customer Created</b><br/><br/>Hi,<br/><br/>This customer: <b>%s</b> has been approved and created.") % (customer_name,)
        self.message_post(cr, uid, ids, body = message1, type='comment', subtype='mt_comment', context = context)
        #message = _("<b>Hi,<br/><br/>This Customer %s has been Approved and Created.</b>") % (customer_name,)
        #self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        self.write(cr,uid,main_form_id,{'customer_state': 'customer_created','active':True,'date':todays_date,'approved_date':todays_date,'approved_by':employee_id,'customer_channels_readonly':False})
        return True

    def reset_to_draft(self,cr,uid,ids,context=None):
        o = self.browse(cr,uid,ids[0])
        main_form_id = o.id
        state = o.customer_state
        subscribe_ids = []
        zeeva_ind_management = ['nitin','akshay']
        subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',zeeva_ind_management)])
        self.message_subscribe_users(cr, SUPERUSER_ID, [o.id], user_ids=subscribe_ids, context=context)
        if state == 'customer_created':
            message = _("<b>Status: Customer Created --> Draft</b>")
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        else:
            message = _("<b>Status: Waiting Management Approval --> Draft</b>")
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        self.write(cr,uid,main_form_id,{'customer_state': 'draft','active':False,'customer_channels_readonly':True})
        return True



res_partner()

class res_partner_bank(osv.osv):
	_inherit="res.partner.bank"
	_columns={
			'account_holder_name': fields.char('Account Holder Name', size=264),
			'micr_code': fields.char('MICR Code',size=128),
	}

	_defaults={
    	'state': 'bank',
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

