# -*- coding: utf-8 -*-

import openerp
#from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

import time


class sale_offer(osv.osv):
    _description = 'Sales Offer Sheet'
    _name = "sale.offer"
    _inherit = ['mail.thread']
    
    _order = "name desc"
    
    _columns = {
        'name': fields.char('Name', size=128),
        'lead_id': fields.many2one('crm.lead','Lead'),
        'customer_id': fields.many2one('res.partner','Customer'),
        'customer_contact_id': fields.many2one('res.partner','Contact'),
        'creation_date': fields.date('Date of Creation'),
        'currency_id': fields.many2one('res.currency', 'Currency', required="True"),
        'line_ids': fields.one2many('sale.offer.line', 'offer_id', 'Offer Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('sent', 'Sent to customer'),
            ('cancel', 'Cancelled'),
            ], 'Status', readonly=True, track_visibility='onchange', select=True,
            help="Gives the status of the sales offer sheet."),
                
        'remarks': fields.text('Remarks'),
        
        'user_id': fields.many2one('res.users', 'Account Manager', states={'draft': [('readonly', False)]}, readonly="True"),
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
        'port_of_loading_id': fields.many2one('stock.port', 'Port of Loading'),
        'port_of_discharge_id': fields.many2one('stock.port', 'Port of Discharge'),
        'shipment_mode': fields.selection([('sea','Sea'),('air','Air')], 'Mode of Shipment'),
    }
    
    _defaults = {
        'name': '/',
        'creation_date': lambda self, cr, uid, ctx: fields.date.context_today(self,cr,uid,context=ctx),
        'currency_id': lambda self, cr, uid, ctx: self.pool.get('res.currency').search(cr, uid, [('name','=','USD')], context=ctx),
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def onchange_customer_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'customer_id': False, 'customer_contact_id': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        #pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        #payment_term = part.property_payment_term and part.property_payment_term.id or False
        #fiscal_position = part.property_account_position and part.property_account_position.id or False
        #dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'customer_contact_id': addr['contact'],
            #'partner_shipping_id': addr['delivery'],
            #'payment_term': payment_term,
            #'fiscal_position': fiscal_position,
            #'user_id': dedicated_salesman,
        }
        #if pricelist:
            #val['pricelist_id'] = pricelist
        return {'value': val}
    
    def create(self, cr, user, vals, context=None):
        
        # Get the next name
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'sale.offer')

        return super(sale_offer,self).create(cr, user, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
            
        #name = self.pool.get('ir.sequence').get(cr, uid, 'sale.offer') or '/'
        date = fields.date.context_today(self,cr,uid,context=context)
        
        print "here",default
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'sale.offer'),
            'creation_date': date,
            'state': 'draft',
            'user_id': uid,
        })
        print "here2",default
        return super(sale_offer, self).copy(cr, uid, id, default, context=context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        if not context:
            context = {}
            
        return self.write(cr, uid, ids, {'state': 'cancel'})
        
    def action_reset(self, cr, uid, ids, context=None):
        if not context:
            context = {}
            
        return self.write(cr, uid, ids, {'state': 'draft'})
        
    def print_offersheet(self, cr, uid, ids, context=None):
        '''
        This function prints all the Offer Sheet
        '''
        
        datas = {
                 'model': 'sale.offer',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'sale.offer.lead', 'datas': datas, 'context': context, 'nodestroy': True}
        
    def print_specification(self, cr, uid, ids, context=None):
        '''
        This function prints all the Specification Sheets of the Offer Sheet
        '''
        
        offer_obj = self.browse(cr, uid, ids[0],context=context)
        product_ids = []
        product_ids += [p.product_id.id for p in offer_obj.line_ids]
        product_ids = list(set(product_ids))
        
        # Select 3 images to show on the spec sheet
        #for im in self.pool.get('product.zeemage').browse(cr, uid, product_ids, context):
            #print im.view_type_earphone, im.view_type_headphone
            
        if offer_obj.lead_id:
            customer_name = offer_obj.lead_id.partner_name
        else:
            customer_name = offer_obj.customer_id.name
        
        context.update({
            'so_name': offer_obj.name,
            'customer_name': customer_name,
        })
        datas = {
                 'model': 'product.template',
                 'ids': product_ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        #print datas
        return {'type': 'ir.actions.report.xml', 'report_name': 'product.specification.sheet.lead', 'datas': datas, 'context': context, 'nodestroy': True}

sale_offer()

    
class sale_offer_line(osv.osv):
    _description = 'Sales Offer Sheet Line'
    _name = "sale.offer.line"
    
    _order = "name"
    
    _columns = {
        'name': fields.char('Name', size=128),
        'sequence': fields.integer('Sequence'),
        'offer_id': fields.many2one('sale.offer', 'Related Offer Sheet', required="True", ondelete='cascade'),
        
        'product_id': fields.many2one('product.template','Raw Product', required="True"),
        'desc': fields.char('Description', size=128),
        'moq': fields.integer('MOQ'),
        'price': fields.float('Unit Price'),
    }
    
    _defaults = {
        'sequence': 10,
    }
    
sale_offer_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
