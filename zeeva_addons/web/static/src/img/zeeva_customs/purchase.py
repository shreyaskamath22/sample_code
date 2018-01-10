# -*- coding: utf-8 -*-

from osv import fields,osv
import tools
import pooler
from tools.translate import _

from datetime import datetime,date
from openerp import netsvc

from openerp.tools.amount_to_text_en import amount_to_text

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def _amount_in_words(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for so in self.browse(cr, uid, ids, context=context):
            temp_text = amount_to_text(so.amount_total, currency=so.currency_id.name)
            #cut = temp_text.find('euro')
            #temp_text = temp_text[0:cut]
            #temp_text += 'Cartons Only'
            res[so.id] = temp_text
        return res
    
    _columns = {
        'sup_code': fields.related('partner_id', 'ref', string="Supplier Code", type='char', size=64),
        
        'ready_date': fields.date('Merchandise Ready Date', help=""),
        'fct_inspection_date': fields.date('Functional Inspection Date', help=""),
        'pac_inspection_date': fields.date('Packing Inspection Date', help=""),
        'port_of_loading': fields.many2one('stock.port', 'Port of Loading'),
        'port_of_discharge': fields.many2one('stock.port', 'Port of Discharge'),
        'shipment_mode': fields.selection([('sea','Sea'),('air','Air')], 'Mode of Shipment'),
        'incoterm': fields.many2one('stock.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
        
        'amount_total_in_words': fields.function(_amount_in_words, string='Total amount in word', type='char', size=128),
    }
    
    _defaults = {
    }
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        partner = self.pool.get('res.partner')
        if not partner_id:
            return {'value': {
                'fiscal_position': False,
                'payment_term_id': False,
                'dest_address_id': False,
                }}
        supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
        supplier = partner.browse(cr, uid, partner_id)
        return {'value': {
            'pricelist_id': supplier.property_product_pricelist_purchase.id,
            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
            'payment_term_id': supplier.property_supplier_payment_term.id or False,
            }}
    
    def print_specification(self, cr, uid, ids, context=None):
        '''
        This function prints the all the Specification Sheets
        '''
        #assert len(ids) == 1, 'This option should only be used for a single id at a time'
        #wf_service = netsvc.LocalService("workflow")
        #wf_service.trg_validate(uid, 'sale.order', ids[0], 'quotation_sent', cr)
        purchase_obj = self.browse(cr, uid, ids[0],context=context)
        product_ids = []
        product_ids += [p.product_id.id for p in purchase_obj.order_line]
        context.update({
            'so_name': '',
            'po_name': purchase_obj.name,
        })
        datas = {
                 'model': 'product.product',
                 'ids': product_ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'product.specification.sheet', 'datas': datas, 'context': context, 'nodestroy': True}
    
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    _columns = {
        'name': fields.text('Description', required=False),
        'sup_code': fields.related('order_id','partner_id', 'ref', string="Supplier Code", type='char', size=64),
        'currency_id': fields.related('order_id','currency_id', string='Currency', relation="res.currency", type='many2one', readonly=True),
    }
    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        
        context = context or {}
        
        res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty=qty, uom_id=uom_id, 
            partner_id=partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, context=context)
              
        #update of result obtained in super function
        res['value']['name'] = ''
        
        return res

purchase_order_line()

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    
    _columns = {
    }
    
    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
        """Create the purchase order from the procurement, using
           the provided field values, after adding the given purchase
           order line in the purchase order.

           :params procurement: the procurement object generating the purchase order
           :params dict po_vals: field values for the new purchase order (the
                                 ``order_line`` field will be overwritten with one
                                 single line, as passed in ``line_vals``).
           :params dict line_vals: field values of the single purchase order line that
                                   the purchase order will contain.
           :return: id of the newly created purchase order
           :rtype: int
        """
        line_vals.update({'name': ''})
        po_vals.update({'order_line': [(0,0,line_vals)]})
        return self.pool.get('purchase.order').create(cr, uid, po_vals, context=context)
    
procurement_order()
