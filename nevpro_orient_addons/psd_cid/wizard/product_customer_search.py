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
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
import calendar
import re
from dateutil.relativedelta import relativedelta
from base.res import res_company as COMPANY
from base.res import res_partner
import xmlrpclib
from openerpsync.sockconnect import connection as sockConnect
import os
from tools.translate import _

class psd_customer_search_wizard(osv.osv_memory):
    _name = "psd.customer.search.wizard"
    _description = "Psd Customer Search"

    _columns = {
        'name':fields.char('Customer/Company Name',size=100),
        'new_name': fields.char('Customer/Company Name',size=100),
        'contact_no':fields.char('Contact No',size=12),
        'address':fields.char('Address',size=100),
        'order_no':fields.char('Order No',size=100),
        'invoice_no':fields.char('Invoice No',size=32),
        'flat_no':fields.char('Flat No',size=100),
        'building_name':fields.char('Building Name',size=100),
        'sub_area':fields.char('Sub Area',size=100),
        'street':fields.char('Street',size=100),
        'landmark':fields.char('Landmark',size=100),
        'pincode':fields.char('Pin code',size=100),
        'psd_customer_search_line': fields.one2many('psd.customer.request.line', 'product_req_customer_search_id', 'Customers'),
        'cancellation_search': fields.boolean('Cancellation Search')
    }    

    def default_get(self,cr,uid,fields,context=None):
        customer_line_ids =[]
        if context is None: context = {}
        res = super(psd_customer_search_wizard, self).default_get(cr, uid, fields, context=context)
        active_ids = context.get('active_ids')
        if active_ids:
            active_id = active_ids[0]
            product_req_obj = self.pool.get('product.request')
            partner_obj = self.pool.get('res.partner')
            psd_customer_request_line = self.pool.get('psd.customer.request.line')
            product_req_data = product_req_obj.browse(cr, uid, active_id)
            if product_req_data.request_cancellation_type=='existing_loction' or product_req_data.request_cancellation_type=='new_location' or product_req_data.new_name:
                customer = product_req_data.new_name     
                res_create_id = self.create(cr,uid,{'new_name':customer,'cancellation_search':True})
            else:
                customer = product_req_data.name
                res_create_id = self.create(cr,uid,{'name':customer,'cancellation_search':False})
            if product_req_data.company_id.establishment_type == 'psd':
                customer_ids = partner_obj.search(cr, uid, [
                        ('name', 'ilike', customer),
                        ('customer','=',True),
                        ('company_id','=',product_req_data.company_id.id)], context=context) 
            else:
                customer_ids = partner_obj.search(cr, uid, [
                        ('name', 'ilike', customer),
                        ('customer','=',True),], context=context)  
            for customer_id in customer_ids:
                addrs_items = []
                address = ''
                partner = partner_obj.browse(cr,uid,customer_id)
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
                customer_line_id = ({
                    'customer_name': partner.name,
                    'complete_address': address,
                    'contact_person': partner.contact_name,
                    'partner_id': partner.id,
                    'contact_no': partner.phone_many2one.number,
                    'branch_id': partner.company_id.id
                 })
                customer_line_ids.append(customer_line_id)
        picking_ids = context.get('active_ids', [])
        if not picking_ids or (not context.get('active_model') == 'product.request') \
            or len(picking_ids) != 1:
            return res
        picking_id, = picking_ids
        if 'name' in fields:
            picking=self.pool.get('product.request').browse(cr,uid,picking_id,context=context)
            res.update(name=picking.name)
            res.update(cancellation_search=False)
        if 'new_name' in fields:
            picking=self.pool.get('product.request').browse(cr,uid,picking_id,context=context)
            res.update(new_name=picking.new_name)
            if picking.request_cancellation_type == 'existing_loction' or picking.request_cancellation_type == 'new_location' or picking.new_name:
                res.update(cancellation_search=True)
        if 'psd_customer_search_line' in fields:
            picking = self.pool.get('psd.customer.request.line').browse(cr, uid, picking_id, context=context)
            moves = [self._partial_move_for(cr, uid, m) for m in customer_line_ids]
            res.update(psd_customer_search_line=moves)
        return res

    def _partial_move_for(self, cr, uid, move):
        customer_name = move.get('customer_name')
        complete_address = move.get('complete_address')
        contact_person = move.get('contact_person')
        partner_id = move.get('partner_id')
        contact_no = move.get('contact_no')
        branch_id = move.get('branch_id')
        partial_move = {
            'name': customer_name,
            'cust_address' : complete_address,
            'contact_name' : contact_person,
            'partner_id': partner_id,
            'contact_no' : contact_no,
            'branch_id': branch_id
        }
        return partial_move
         
    
    def product_request_search_customer(self,cr,uid,ids,context=None):
        partner_obj = self.pool.get('res.partner')
        product_cust_line_obj = self.pool.get('psd.customer.request.line')
        product_req_obj = self.pool.get('product.request')
        active_ids = context.get('active_ids')
        if active_ids:
            active_id = active_ids[0]
        product_req_data = product_req_obj.browse(cr, uid, active_id)    
        res = False
        display_ids = []
        true_items = []
        domain = []
        psd_customer_search_line_ids = []
        rec = self.browse(cr, uid, ids[0])
        if rec.psd_customer_search_line:
            for psd_customer_search_line_id in rec.psd_customer_search_line:
                psd_customer_search_line_ids.append(psd_customer_search_line_id.id)    
            product_cust_line_obj.unlink(cr, uid, psd_customer_search_line_ids, context=context)
        if rec.cancellation_search == True and rec.new_name:
            true_items.append('new_name')
        elif rec.name:
            true_items.append('name')
        if rec.contact_no:
            true_items.append('contact')    
        if rec.flat_no:
            true_items.append('flat')
        if rec.building_name:
            true_items.append('building')    
        if rec.sub_area:
            true_items.append('sub_aread') 
        if rec.street:
            true_items.append('street')
        if rec.landmark:
            true_items.append('landmark')
        if rec.pincode:
            true_items.append('pincode')                                     
        for true_item in true_items:
            if true_item == 'name':
                domain.append(('name', 'ilike', rec.name))
            if true_item == 'new_name':
                domain.append(('name', 'ilike', rec.new_name))
            if true_item == 'contact':
                domain.append(('phone_many2one.number', 'ilike', rec.contact_no))  
            if true_item == 'flat':
                domain.append(('apartment', 'ilike', rec.flat_no))
            if true_item == 'building':
                domain.append(('building', 'ilike', rec.building_name))  
            if true_item == 'sub_area':
                domain.append(('sub_area', 'ilike', rec.sub_area))
            if true_item == 'street':
                domain.append(('street', 'ilike', rec.street))  
            if true_item == 'landmark':
                domain.append(('landmark', 'ilike', rec.landmark))
            if true_item == 'pincode':
                domain.append(('zip', 'ilike', rec.pincode)) 
        domain.append(('customer', '=', True))  
        if product_req_data.company_id.establishment_type == 'psd':
            domain.append(('company_id','=',product_req_data.company_id.id))        
        display_ids = partner_obj.search(cr, uid, domain, context=context)
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
            res = product_cust_line_obj.create(cr, uid,
                {
                    'name': partner.name,
                    'cust_address': cust_address,
                    'contact_name': partner.contact_name,
                    'contact_no': partner.phone_many2one.number,
                    'product_req_customer_search_id':ids[0],
                    'partner_id': partner.id,
                    'branch_id': partner.company_id.id
                })
        return res   

    def select_searched_customer(self,cr,uid,ids,context=None):
        active_id = context.get('active_ids',False)
        product_req_obj = self.pool.get('product.request')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('psd.customer.request.line')
        cust_source_obj = self.pool.get('customer.source') 
        crm_lead_obj = self.pool.get('crm.lead')
        request_counter_obj = self.pool.get('request.counter')
        rec = self.browse(cr, uid, ids[0])
        product_req_data = product_req_obj.browse(cr,uid,active_id)
        res = line_obj.search(cr,uid,[('product_req_customer_search_id','=',ids[0]),('select_cust','=',True)])
        if len(res) == 0:
            raise osv.except_osv(_('Warning!'),_("Please select one customer!"))
        if len(res) > 1:
            raise osv.except_osv(_('Warning!'),_("Multiple selection not allowed!"))
        customer_id = line_obj.browse(cr,uid,res[0],context=context).partner_id
        customer_search = partner_obj.search(cr,uid,[('id','=',customer_id)],context=context)
        customer = partner_obj.browse(cr,uid,customer_search[0],context=context)
        # pr_ids = crm_lead_obj.search(cr, uid, [('partner_id','=',customer.id),('type_request','=','product_request_psd')], context=context)  
        # counter_ids = request_counter_obj.search(cr, uid, [], context=context)
        # product_request_counter = request_counter_obj.browse(cr, uid, max(counter_ids)).product_request_counter
        # if len(pr_ids) >= product_request_counter:
        #     raise osv.except_osv(_('Exceeding limit warning!'),_("The product request counter for this customer has reached the maximum limit!"))
        if customer:
            if rec.cancellation_search == True:
                product_req_obj.write(cr,uid,active_id,{'new_name':customer.name,'new_partner_id':customer.id})
            else:
                ref_id = cust_source_obj.search(cr, uid, [('name','=','Existing/Old Customer')], context=context)
                product_req_obj.write(cr,uid,active_id,
                    {
                        'name':customer.name,
                        'partner_id': customer.id,
                        'customer_id':customer.ou_id,
                        'customer_type':'existing',
                        'title':customer.title,
                        'first_name':customer.first_name,
                        'last_name':customer.last_name,
                        'middle_name':customer.middle_name,
                        'designation':customer.designation,
                        'premise_type':customer.premise_type,
                        'building':customer.building,
                        'location_name':customer.location_name,
                        'apartment':customer.apartment,
                        'sub_area':customer.sub_area,
                        'street':customer.street,
                        'tehsil':customer.tehsil and customer.tehsil.id,
                        'landmark':customer.landmark,
                        'state_id':customer.state_id and customer.state_id.id,
                        'city_id':customer.city_id and customer.city_id.id,
                        'district':customer.district and customer.district.id,
                        'fax':customer.fax,
                        'phone_many2one':customer.phone_many2one.id,
                        'zip':customer.zip,
                        'email':customer.email,
                        'ref_by':ref_id[0],
                        'segment': customer.segment,
                        'confirm_check': True,
                        'hide_segment': True
                    })
        return {'type': 'ir.actions.act_window_close'}

    def clear_customer(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'name':None,'new_name':None,'contact_no':None,'invoice_no':None,'address':None})

psd_customer_search_wizard()



class psd_customer_request_line(osv.osv_memory):
    _name='psd.customer.request.line'  

    _columns = {
        'product_req_customer_search_id': fields.many2one('psd.customer.search.wizard', 'Customer Search'),
        'select_cust': fields.boolean('Select'),
        'name':fields.char('Customer Name',size=256),
        'partner_id': fields.char('Customer ID',size=256),
        'contact_name':fields.char('Contact Person',size=100),
        'cust_address': fields.char('Address',size=256),
        'contact_no':fields.char('Contact Number',size=100),
        'branch_id':fields.many2one('res.company','PCI Office'),
    }

    
    def select_customer(self,cr,uid,ids,context=None):        
        self.write(cr,uid,ids[0],{'select_cust':True})
        return True

    def selected_cust_details(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids[0],{'select_cust':False})
        return True 

psd_customer_request_line()   
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
