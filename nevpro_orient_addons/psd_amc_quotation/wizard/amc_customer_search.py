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



class psd_amc_customer_search_wizard(osv.osv_memory):
    _name = "psd.amc.customer.search.wizard"
    _description = "AMC Quotation Customer Search"
    


    _columns = {

        'name':fields.char('Customer/Company Name',size=100),
        'contact_no':fields.char('Contact No',size=12),
        'order_no':fields.char('Order No',size=100),
        'invoice_no':fields.char('Invoice No',size=32),
        #############Search View according to the next changes
        'flat_no':fields.char('Flat No',size=100),
        'building_name':fields.char('Building Name',size=100),
        'sub_area':fields.char('Sub Area',size=100),
        'street':fields.char('Street',size=100),
        'landmark':fields.char('Landmark',size=100),
        'pincode':fields.char('Pincode',size=100),
        'psd_amc_customer_search_line': fields.one2many('psd.amc.customer.request.line', 'product_req_customer_search_id', 'Customers'),
    }    

    def default_get(self,cr,uid,fields,context=None):
        customer_line_ids =[]
        if context is None: context = {}
        res = super(psd_amc_customer_search_wizard, self).default_get(cr, uid, fields, context=context)
        active_ids = context.get('active_ids')
        if active_ids:
            active_id = active_ids[0]
            product_req_obj = self.pool.get('amc.quotation')
            partner_obj = self.pool.get('res.partner')
            psd_customer_request_line = self.pool.get('psd.amc.customer.request.line')
            customer = product_req_obj.browse(cr, uid, active_id).customer_name
            customer_ids = partner_obj.search(cr, uid, [('name', 'ilike', customer)], context=context)
            res_create_id = self.create(cr,uid,{'name':customer})
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
                 })
                customer_line_ids.append(customer_line_id)
        picking_ids = context.get('active_ids', [])
        if not picking_ids or (not context.get('active_model') == 'amc.quotation') \
            or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        picking_id, = picking_ids
        if 'name' in fields:
            picking=self.pool.get('amc.quotation').browse(cr,uid,picking_id,context=context)
            res.update(name=picking.customer_name)
        if 'psd_amc_customer_search_line' in fields:
            picking = self.pool.get('psd.amc.customer.request.line').browse(cr, uid, picking_id, context=context)
            moves = [self._partial_move_for(cr, uid, m) for m in customer_line_ids]
            res.update(psd_amc_customer_search_line=moves)
        return res

    def _partial_move_for(self, cr, uid, move):
        customer_name = move.get('customer_name')
        complete_address = move.get('complete_address')
        contact_person = move.get('contact_person')
        partner_id = move.get('partner_id')
        contact_no = move.get('contact_no')
        partial_move = {
            'name': customer_name,
            'cust_address' : complete_address,
            'contact_name' : contact_person,
            'partner_id': partner_id,
            'contact_no' : contact_no,
        }
        return partial_move
         
    
    def product_request_search_customer(self,cr,uid,ids,context=None):
        partner_obj = self.pool.get('res.partner')
        display_ids = []
        customer_search_data = self.browse(cr, uid, ids[0])
        loc_line_ids = []
        locations_line_ids = self.browse(cr,uid,ids[0]).psd_amc_customer_search_line
        if locations_line_ids:
            for locations_line_id in locations_line_ids:
                loc_line_ids.append(locations_line_id.id)
        self.pool.get('psd.amc.customer.request.line').unlink(cr, uid, loc_line_ids, context=context)
        partner_obj = self.pool.get('res.partner')
        psd_customer_request_line = self.pool.get('psd.amc.customer.request.line')
        customer = self.browse(cr, uid, ids[0]).name
        customer_ids = partner_obj.search(cr, uid, [('name', 'ilike', customer)], context=context)
        for customer_id in customer_ids:
            addrs_items = []
            address = ''
            partner = partner_obj.browse(cr,uid,customer_id)
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
                        address = address+item+','+' '
                    if item==last_item:
                        address = address+item
                   
            self.pool.get('psd.amc.customer.request.line').create(cr,uid,{'name': partner.name,
            'cust_address': address,
            'contact_name': partner.contact_name,
            'partner_id': partner.id,
            'contact_no': partner.phone_many2one.number,'product_req_customer_search_id':ids[0]})
        return True

    def select_searched_customer(self,cr,uid,ids,context=None):
        active_id = context.get('active_id',False)
        product_req_obj = self.pool.get('amc.quotation')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('psd.amc.customer.request.line')
        res=line_obj.search(cr,uid,[('product_req_customer_search_id','=',ids[0]),('select_cust','=',True)])
        if len(res) == 0:
            raise osv.except_osv(_('Warning!'),_("Please select one customer!"))
        if len(res) > 1:
            raise osv.except_osv(_('Warning!'),_("Multiple selection not allowed!"))
        customer_id = line_obj.browse(cr,uid,res[0],context=context).partner_id
        customer_search = partner_obj.search(cr,uid,[('id','=',customer_id)],context=context)
        customer = partner_obj.browse(cr,uid,customer_search[0],context=context)

        if customer:
            product_req_obj.write(cr,uid,active_id,
                {
                    'customer_name':customer.name,
                    'partner_id': customer.id,
                    'customer_id':customer.ou_id,
                    'customer_type':'existing',
                    'title':customer.title,
                    'contact_person':customer.first_name+' '+customer.last_name,
                    'last_name':customer.last_name,
                    'middle_name':customer.middle_name,
                    'designation':customer.designation,
                    'premise_type':customer.premise_type,
                    'building':customer.building,
                    'location_name':customer.location_name,
                    'apartment':customer.apartment,
                    'sub_area':customer.sub_area,
                    'street':customer.street,
                    'tehsil':customer.tehsil.id,
                    'landmark':customer.landmark,
                    'state_id':customer.state_id.id,
                    'city_id':customer.city_id.id,
                    'district':customer.district.id,
                    'fax':customer.fax,
                    'ref_by':customer.ref_by.id,
                    'phone_many2one':customer.phone_many2one.id,
                    'zip':customer.zip,
                    'email':customer.email,
                })
        return {'type': 'ir.actions.act_window_close'}

    def clear_customer(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'name':None,'contact_no':None,'invoice_no':None,'address':None})

psd_amc_customer_search_wizard()



class psd_amc_customer_request_line(osv.osv_memory):
    _name='psd.amc.customer.request.line'  

    _columns = {
        'product_req_customer_search_id': fields.many2one('psd.amc.customer.search.wizard', 'Customer Search'),
        'select_cust': fields.boolean('Select'),
        'name':fields.char('Customer/Company Name',size=256),
        'partner_id': fields.char('Customer ID',size=256),
        'contact_name':fields.char('Contact Name',size=100),
        'cust_address': fields.char('Address',size=256),
        'contact_no':fields.char('Contact Number',size=100),
    }

    
    def select_customer(self,cr,uid,ids,context=None):        
        self.write(cr,uid,ids[0],{'select_cust':True})
        return True

    def selected_cust_details(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids[0],{'select_cust':False})
        return True 

psd_amc_customer_request_line()   
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
