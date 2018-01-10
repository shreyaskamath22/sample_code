# -*- coding: utf-8 -*-

from osv import fields,osv
import tools
import pooler
from tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools.amount_to_text_en import amount_to_text

class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'
    
    def _amount_total_in_words(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            temp_text = amount_to_text(invoice.amount_total, currency=invoice.currency_id.name)
            #cut = temp_text.find('euro')
            #temp_text = temp_text[0:cut]
            #temp_text += 'Cartons Only'
            #print temp_text, invoice.currency_id.name
            res[invoice.id] = temp_text
        return res
        
    _columns = {
        'amount_total_in_words': fields.function(_amount_total_in_words, string='Total amount in words', type='char', size=128),
        'picking_id': fields.many2one('stock.picking', 'Related Stock Picking'),
    }
    
    def message_subscribe(self, cr, uid, ids, partner_ids, subtype_ids=None, context=None):
        """ Add partners to the records followers. """
        test = set(partner_ids)
        mail_followers_obj = self.pool.get('mail.followers')
        subtype_obj = self.pool.get('mail.message.subtype')
        partner_obj = self.pool.get('res.partner')

        user_pid = self.pool.get('res.users').browse(cr, uid, uid, context=context).partner_id.id
        if set(partner_ids) == set([user_pid]):
            try:
                self.check_access_rights(cr, uid, 'read')
            except (osv.except_osv, orm.except_orm):
                return
        else:
            self.check_access_rights(cr, uid, 'write')

        for record in self.browse(cr, SUPERUSER_ID, ids, context=context):
            existing_pids = set([f.id for f in record.message_follower_ids
                                            if f.id in partner_ids])
            new_pids = set(partner_ids) - existing_pids
            
            ### MOD START: if id is a customer, DO NOT ADD HIM
            for partner in partner_ids:
                if partner_obj.browse(cr, SUPERUSER_ID, partner, context=context).customer == True:
                    new_pids -= set([partner])
            ### MOD STOP

            # subtype_ids specified: update already subscribed partners
            if subtype_ids and existing_pids:
                fol_ids = mail_followers_obj.search(cr, SUPERUSER_ID, [
                                                        ('res_model', '=', self._name),
                                                        ('res_id', '=', record.id),
                                                        ('partner_id', 'in', list(existing_pids)),
                                                    ], context=context)
                mail_followers_obj.write(cr, SUPERUSER_ID, fol_ids, {'subtype_ids': [(6, 0, subtype_ids)]}, context=context)
            # subtype_ids not specified: do not update already subscribed partner, fetch default subtypes for new partners
            elif subtype_ids is None:
                subtype_ids = subtype_obj.search(cr, uid, [
                                                        ('default', '=', True),
                                                        '|',
                                                        ('res_model', '=', self._name),
                                                        ('res_model', '=', False)
                                                    ], context=context)
            # subscribe new followers
            for new_pid in new_pids:
                mail_followers_obj.create(cr, SUPERUSER_ID, {
                                                'res_model': self._name,
                                                'res_id': record.id,
                                                'partner_id': new_pid,
                                                'subtype_ids': [(6, 0, subtype_ids)],
                                            }, context=context)

        return True
    
    def line_get_convert(self, cr, uid, x, part, date, context=None):
        return {
            'date_maturity': x.get('date_maturity', False),
            'partner_id': part,
            'name': x['name'][:64],
            'date': date,
            'debit': x['price']>0 and x['price'],
            'credit': x['price']<0 and -x['price'],
            'account_id': x['account_id'],
            'analytic_lines': x.get('analytic_lines', []),
            'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
            'currency_id': x.get('currency_id', False),
            'tax_code_id': x.get('tax_code_id', False),
            'tax_amount': x.get('tax_amount', False),
            'ref': x.get('ref', False),
            'quantity': x.get('quantity',1.00),
            'product_id': x.get('product_id', False),
            'product_uom_id': x.get('uos_id', False),
            'analytic_account_id': x.get('account_analytic_id', False),
        }
        
        
account_invoice()

class account_invoice_line(osv.osv):
    
    _inherit = 'account.invoice.line'
    
    _columns = {
        'move_id': fields.many2one('stock.move', 'Related Stock Move'),
        'name': fields.text('Description', required=False),
    }
    
    def move_line_get_item(self, cr, uid, line, context=None):
        
        var_name = ''
        if line.product_id:
            var_name = '[' + line.product_id.default_code + '] '+ line.product_id.name
            
            if line.product_id.variants:
                var_name += ' - ' + line.product_id.variants
                
        return {
            'type':'src',
            'name': var_name,
            'price_unit':line.price_unit,
            'quantity':line.quantity,
            'price':line.price_subtotal,
            'account_id':line.account_id.id,
            'product_id':line.product_id.id,
            'uos_id':line.uos_id.id,
            'account_analytic_id':line.account_analytic_id.id,
            'taxes':line.invoice_line_tax_id,
        }

account_invoice_line
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
