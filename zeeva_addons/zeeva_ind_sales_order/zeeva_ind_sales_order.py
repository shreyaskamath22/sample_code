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

from openerp.tools import amount_to_text_en
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.tools import float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID


class res_company(osv.osv):
    _name = 'res.company'
    _inherit = 'res.company'
    
    _columns = {
        'logo_header': fields.binary("Image Header", help="This field holds the image used for report\'s header"),
    }
    
res_company()

class sale_order(osv.osv):
    _inherit="sale.order"

    def _amount_in_words(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            a=''
            b=''
            if order.currency_id.name == 'INR':
                a = 'Rupees'
                b = ''
            res[order.id] = amount_to_text(order.roundoff_grand_total, 'en', a).replace('and Zero Cent', b).replace('and Zero Cent', b)
        return res

    def _total_shipped_quantity(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            val = val1 = 0.0
            for line in order.order_line:
                val1 += line.product_uom_qty
            res[order.id] = val1
        return res

    def _total_billed_quantity(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in order.order_line:
                val += line.product_billed_qty
            res[order.id] = val
        return res

    SELECTION_LIST = [
    ('Financial Year(2016-2017)','Financial Year(2016-2017)'),
    ('Financial Year(2017-2018)','Financial Year(2017-2018)'),
    ('Financial Year(2018-2019)','Financial Year(2018-2019)'),
    ('Financial Year(2019-2020)','Financial Year(2019-2020)'),
    ]

    def _get_financial_year(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for x in self.browse(cr, uid, ids):
            option=''
            etd_date = x.date_order
            option1='Financial Year(2016-2017)'
            option2='Financial Year(2017-2018)'
            option3='Financial Year(2018-2019)'
            option4='Financial Year(2019-2020)'
            if etd_date>='2016-04-01' and etd_date<='2017-03-31':
                option=option1
            if etd_date>='2017-04-01' and etd_date<='2018-03-31':
                option=option2
            if etd_date>='2018-04-01' and etd_date<='2019-03-31':
                option=option3
            if etd_date>='2019-04-01' and etd_date<='2020-03-31':
                option=option4
            res[x.id] = option
        return res

    _columns={
    	'po_date': fields.date("Buyer's PO Date"),
    	'due_date': fields.date('Payment Due Date',help="Payment Due Date calculation done on the following condition :-\nIf the Customer is Interstate and agreed C-Form then Due Date=Order Date+Payment Term Days+5.\nIf the Customer is Interstate and Disagreed the C-Form or Within the State then Due Date=Order Date+Payment Term Days."),
    	#'destination': fields.many2one('res.city','Destination'),
    	'destination': fields.char('Destination', size=128),
    	'client_order_ref': fields.char("Buyer's PO Number", size=128),
    	'dispatch_source': fields.many2one('dispatch.through','Dispatch Through'),
    	##############Shipping Address fields
    	'shipping_street': fields.char('Shipping Street',size=128),
    	'shipping_street2': fields.char('Shipping Street2',size=128),
    	'shipping_city': fields.many2one('res.city','Shipping Cities'),
    	'shipping_state_id': fields.many2one('res.country.state',' Shipping State'),
    	'shipping_zip': fields.char('Shipping Zip',size=24),
    	'shipping_country_id': fields.many2one('res.country','Shipping Country'),
    	'shipping_destination': fields.char('Shipping Destination', size=128),
        'shipping_contact_person': fields.many2one('res.partner', 'Contact Person'),
        'shipping_contact_mobile_no': fields.char('Mobile Number',size=68),
        'shipping_contact_landline_no': fields.char('Landline Number',size=68),
        'shipping_email_id': fields.char('Email ID',size=68),
    	##################Billing Address  fields
    	'billing_street': fields.char('Billing Street',size=128),
    	'billing_street2': fields.char('Billing Street2',size=128),
    	'billing_city': fields.many2one('res.city','Billing Cities'),
    	'billing_state_id': fields.many2one('res.country.state','Billing State'),
    	'billing_zip': fields.char('Billing Zip',size=24),
    	'billing_country_id': fields.many2one('res.country','Billing Country'),
    	'billing_destination': fields.char('Billing Destination',size=128),
        'billing_contact_person': fields.many2one('res.partner', 'Contact Person'),
        'billing_contact_mobile_no': fields.char('Mobile Number',size=68),
        'billing_contact_landline_no': fields.char('Landline Number',size=68),
        'billing_email_id': fields.char('Email ID',size=68),
    	#####################Display total amount_totalt in words
    	'amount_total_in_words': fields.function(_amount_in_words, string='Total amount in word', type='char', size=128),
    	'total_shipped_quantity': fields.function(_total_shipped_quantity, string='Total Shipped Quantity', type='integer',digits_compute= dp.get_precision('Product UoS')),
    	'total_billed_quantity': fields.function(_total_billed_quantity, string='Total Billed Quantity', type='integer',digits_compute= dp.get_precision('Product UoS')),
        #####################Display the Financial Year
        'financial_year': fields.function(_get_financial_year, type='selection',method=True,selection=SELECTION_LIST, string="Financial Year"),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),    
                ('picking', 'On Delivery Order'),
                ('prepaid', 'Before Delivery'),
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""On demand: A draft invoice can be created from the sales order when needed. \nOn delivery order: A draft invoice can be created from the delivery order when the products have been delivered. \nBefore delivery: A draft invoice is created from the sales order and must be paid before the products can be delivered."""),
        'created_delivery_order': fields.boolean('Created Delivery Order'),
        'po_attachment': fields.binary('Attach PO', required=True)
    }

    def onchange_billing_contact_person(self,cr,uid,ids,billing_contact_person):
        v={}
        res_partner_obj=self.pool.get('res.partner')
        if billing_contact_person:
            res_partner_browse = res_partner_obj.browse(cr,uid,billing_contact_person)
            v['billing_contact_mobile_no'] = res_partner_browse.mobile
            v['billing_contact_landline_no'] = res_partner_browse.phone
            v['billing_email_id'] = res_partner_browse.email
        return {'value':v}

    def onchange_shipping_contact_person(self,cr,uid,ids,shipping_contact_person):
        v={}
        res_partner_obj=self.pool.get('res.partner')
        if shipping_contact_person:
            res_partner_browse = res_partner_obj.browse(cr,uid,shipping_contact_person)
            v['shipping_contact_mobile_no'] = res_partner_browse.mobile
            v['shipping_contact_landline_no'] = res_partner_browse.phone
            v['shipping_email_id'] = res_partner_browse.email
        return {'value':v}

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}

        added_values_date = ''
        todays_date =datetime.now().date()
        date_order = str(todays_date)
        account_payment_term_line = self.pool.get('account.payment.term.line')
        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        #####################Shipping address###############
        shipping_street = part.shipping_street
        shipping_street2 = part.shipping_street2
        shipping_city = part.shipping_city2.id
        shipping_state_id = part.shipping_state_id.id
        shipping_zip = part.shipping_zip
        shipping_country_id = part.shipping_country_id.id
        shipping_destination = part.shipping_destination
        #####################Billing address#################
        billing_street = part.street
        billing_street2 = part.street2
        billing_city = part.billing_city.id
        billing_state_id = part.state_id.id
        billing_zip = part.zip
        billing_country_id = part.country_id.id
        billing_destination = part.billing_destination
        type_of_sales = part.type_of_sales
        cform_criteria = part.cform_criteria
        payment_term = part.property_payment_term.id
        primary_contact = part.primary_contact
        billing_contact_person = False
        shipping_contact_person = False
        if part.child_ids:
            for line in part.child_ids:
                primary_contact = line.primary_contact
                if primary_contact:
                    billing_contact_person = line.id
                    shipping_contact_person = line.id
        
        start_date_day = datetime.strptime(date_order,'%Y-%m-%d')
        search_account_payment_line = account_payment_term_line.search(cr,uid,[('payment_id','=',payment_term)])
    	browse_account_payment_line = account_payment_term_line.browse(cr,uid,search_account_payment_line[0])
    	days = browse_account_payment_line.days
    	grace_days = 5
        if type_of_sales == 'interstate' and cform_criteria == 'agreed':
        	if days != 0:
        		new_days = days + grace_days
        		added_value_days = start_date_day+timedelta(days=new_days)
    			added_values_date =str(added_value_days)
    		else:
    			added_values_date = ''
    	elif type_of_sales == 'within_state' or (type_of_sales == 'interstate' and cform_criteria == 'disagreed'):
    		if days != 0:
        		added_value_days = start_date_day+timedelta(days=days)
    			added_values_date =str(added_value_days)
    		else:
    			added_values_date = False
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
            'shipping_contact_person': shipping_contact_person,
            'shipping_street': shipping_street,
            'shipping_street2': shipping_street2,
            'shipping_city': shipping_city,
            'shipping_destination': shipping_destination,
            'destination': shipping_destination,
            'shipping_state_id': shipping_state_id,
            'shipping_zip': shipping_zip,
            'shipping_country_id': shipping_country_id,
            'billing_contact_person': billing_contact_person,
            'billing_street': billing_street,
            'billing_street2': billing_street2,
            'billing_city': billing_city,
            'billing_state_id': billing_state_id,
            'billing_zip': billing_zip,
            'billing_country_id': billing_country_id,
            'billing_destination': billing_destination,
            'due_date': added_values_date,
            'order_policy': 'picking',
            'section_id':1,
        }
        if pricelist:
            val['pricelist_id'] = pricelist
        return {'value': val}

    def action_wait(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            noprod = self.test_no_product(cr, uid, o, context)
            if (o.order_policy == 'manual') or noprod:
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
                sale_order_number = o.name
                subscribe_ids = []
                zeeva_ind_management = ['nitin','arun']
                subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',zeeva_ind_management)])
                self.message_subscribe_users(cr, SUPERUSER_ID, [o.id], user_ids=subscribe_ids, context=context)
                # message1 = _("<b>Status: Draft --> Sales Order</b>")
                # self.message_post(cr, uid, ids, body = message1, type='comment', subtype='mt_comment', context = context)
                message = _("<b>Status: Draft --> Sales Order</b>,<br/><br/><b>Dear Sir,<br/><br/> The Sale Order %s has been confirmed.</b>") % (sale_order_number)
                self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
        return True

    def onchange_date_order(self,cr,uid,ids,date_order,payment_term,partner_id):
    	v={}
    	res_partner_obj = self.pool.get('res.partner')
    	search_partner_id =res_partner_obj.search(cr,uid,[('id','=',partner_id)])
    	browse_partner_line_id = res_partner_obj.browse(cr,uid,search_partner_id)
    	for browse_partner_id in browse_partner_line_id:
	    	type_of_sales = browse_partner_id.type_of_sales
	    	cform_criteria = browse_partner_id.cform_criteria
	    	account_payment_term_line = self.pool.get('account.payment.term.line')
	    	if date_order and payment_term:
	    		start_date_day = datetime.strptime(date_order,'%Y-%m-%d')
	    		search_account_payment_line = account_payment_term_line.search(cr,uid,[('payment_id','=',payment_term)])
	    		browse_account_payment_line = account_payment_term_line.browse(cr,uid,search_account_payment_line[0])
	    		days = browse_account_payment_line.days
	    		grace_days = 5
	    		if type_of_sales == 'interstate' and cform_criteria == 'agreed':
	        		if days != 0:
	        			new_days = days + grace_days
	        			added_value_days = start_date_day+timedelta(days=new_days)
	    				added_values_date =str(added_value_days)
	    				v['due_date'] = added_values_date
	    			else:
	    				added_values_date = ''
	    				v['due_date'] = added_values_date
	    		elif type_of_sales == 'within_state' or (type_of_sales == 'interstate' and cform_criteria == 'disagreed'):
	    			if days != 0:
	        			added_value_days = start_date_day+timedelta(days=days)
	    				added_values_date =str(added_value_days)
	    				v['due_date'] = added_values_date
	    			else:
	    				added_values_date = ''
	    				v['due_date'] = added_values_date
	    	elif not date_order or payment_term:
	    		v['due_date'] = ''
    	return {'value':v}

    def create_delivery_order(self,cr,uid,ids,context=None):
        result = []
        line_order =[]
        tax_line =[]
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        stock_obj = self.pool.get('stock.picking.out')
        stock_move = self.pool.get('stock.move')
        tax_line = self.pool.get('delivery.tax.summary.report')
        product_product_obj = self.pool.get('product.product')
        todays_date = datetime.now()
        for order in self.browse(cr,uid,ids):
                partner_id = order.partner_id.id
                main_form_id = order.id
                stock_values = {
                                'name': str(pick_name),
                                'origin': order.name,
                                'date': todays_date,
                                'type': 'out',
                                'state': 'draft',
                                'partner_id': order.partner_id.id,
                                'note': order.note,
                                'company_id': order.company_id.id,
                                'po_date': order.po_date,
                                'due_date': order.due_date,
                                'delivery_order_ref': order.client_order_ref,
                                'dispatch_source': order.dispatch_source.id,
                                'user_id': order.user_id.id,
                                'payment_term': order.payment_term.id,
                                #############Shipping Address fields
                                'shipping_street': order.shipping_street,
                                'shipping_street2': order.shipping_street2,
                                'shipping_city': order.shipping_city.id,
                                'shipping_state_id':order.shipping_state_id.id,
                                'shipping_zip':order.shipping_zip,
                                'shipping_country_id': order.shipping_country_id.id,
                                'shipping_destination': order.shipping_destination,
                                'shipping_contact_person': order.shipping_contact_person.id,
                                'shipping_contact_mobile_no': order.shipping_contact_mobile_no,
                                'shipping_contact_landline_no': order.shipping_contact_landline_no,
                                'shipping_email_id': order.shipping_email_id,
                                'destination': order.shipping_destination,
                                ##################Billing Address  fields
                                'billing_street': order.billing_street,
                                'billing_street2': order.billing_street2,
                                'billing_city': order.billing_city.id,
                                'billing_state_id': order.billing_state_id.id,
                                'billing_zip': order.billing_zip,
                                'billing_country_id': order.billing_country_id.id,
                                'billing_destination': order.billing_destination,
                                'billing_contact_person': order.billing_contact_person.id,
                                'billing_contact_mobile_no': order.billing_contact_mobile_no,
                                'billing_contact_landline_no': order.billing_contact_landline_no,
                                'billing_email_id':order.billing_email_id,
                                'apply_discount': order.apply_discount,
                                'discount_value': order.discount_value,
                                'discounted_amount': order.discounted_amount,
                                'pricelist_id': order.pricelist_id.id,
                                'stock_journal_id':1,
                                'so_date':order.date_order,
                                'po_attachment':order.po_attachment,
                                'invoice_state': '2binvoiced',
                                'date_done': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'stock', 'view_picking_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'stock', 'view_picking_out_tree')
        tree_id = tree_res and tree_res[1] or False
        stock_id =stock_obj.create(cr,uid,stock_values)
        for line1 in order.tax_lines:
            tax_line_values = {
                                    'tax_id':line1.tax_id,
                                    'tx_name':line1.tx_name,
                                    'total_amount':line1.total_amount,
                                    'tax_rate':line1.tax_rate,
                                    'stock_taxes_id':stock_id
            }
            tax_line_values_create = tax_line.create(cr,uid,tax_line_values)
        for line in order.order_line:
            location_id = line.sale_warehouse_id.lot_stock_id.id
            output_id = line.sale_warehouse_id.lot_output_id.id
            product_id = line.product_id.id
            product_product_browse = product_product_obj.browse(cr,uid,product_id).virtual_available
            # if product_product_browse < 0.00:
            #     raise osv.except_osv(('Warning!!'),('The stock is not available.'))
            stock_line_values={
                                'name': line.name,
                                'product_id': line.product_id.id,
                                'product_qty': line.product_uom_qty,
                                'product_billed_qty': line.product_billed_qty,
                                'product_uom': line.product_uom.id,
                                'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
                                'product_uos': (line.product_uos and line.product_uos.id)\
                                        or line.product_uom.id,
                                'partner_id': line.order_partner_id.id,
                                'location_id': location_id,
                                'location_dest_id': output_id,
                                'tracking_id': False,
                                'state': 'confirmed',
                                'company_id': order.company_id.id,
                                'price_unit': line.price_unit or 0.0,
                                'delivery_warehouse_id':line.sale_warehouse_id.id,
                                'sale_price':line.sale_price.id,
                                'tax_applied_id':line.tax_applied_id.id,
                                'product_category_id':line.product_category_id.id,
                                'picking_id':stock_id,
                                'product_code':line.product_code,
            }
            stock_line_values_create = stock_move.create(cr,uid,stock_line_values)
            self.write(cr,uid,main_form_id,{'created_delivery_order':True})
            order.refresh()
        return {
                    'name': _('Delivery Order'),
                    'view_type': 'form',
                    'view_mode': 'form,tree',
                    'res_model': 'stock.picking.out',
                    'res_id': stock_id,
                    'view_id': False,
                    'views': [(form_id, 'form'), (tree_id, 'tree')],
                    'context': "{'type': 'out'}",
                    'type': 'ir.actions.act_window',
        }


       
sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns ={
        'sale_warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
    }

    def create(self, cr, uid, vals, context=None):
        line_values=[]
        main_append = []
        product_sale_price_obj =self.pool.get('product.customer.saleprice')
        res_id = super(sale_order_line, self).create(cr, uid, vals, context=context)
        if vals.has_key('sale_price'):
            product_id =vals.get('product_id')
            sale_price_id = vals.get('sale_price')
            order_id = vals.get('order_id')
            sale_order_browse = self.pool.get('sale.order').browse(cr,uid,order_id).partner_id.id
            product_sale_price_obj.write(cr,uid,sale_price_id,{'product_id':product_id,'customer_id':sale_order_browse})
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        main_id = ids[0]
        product_sale_price_obj =self.pool.get('product.customer.saleprice')
        if vals.has_key('product_id'):
            product_id =vals.get('product_id')
            sale_price_id = self.browse(cr,uid,main_id).sale_price.id
            customer_id = self.browse(cr,uid,main_id).order_partner_id.id
            product_sale_price_obj.write(cr,uid,sale_price_id,{'product_id':product_id,'customer_id':customer_id})
        return res

sale_order_line()

class dispatch_through(osv.osv):
    _name = "dispatch.through" 
    _description = "Dispatch"
    _columns = {
        'name': fields.char('Dispatch Source'),
   
    }

dispatch_through()



   