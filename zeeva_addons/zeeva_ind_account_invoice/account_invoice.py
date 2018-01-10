# -*- coding: utf-8 -*-

from osv import fields,osv
import tools
import pooler
from tools.translate import _
from openerp import SUPERUSER_ID, netsvc
#from datetime import datetime,date
from openerp import netsvc
from openerp.tools.amount_to_text_en import amount_to_text
import math
import openerp.addons.decimal_precision as dp
from datetime import datetime
from time import strftime
from datetime import date
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
from datetime import timedelta,date,datetime
from datetime import datetime,date
from openerp.tools import float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT


class account_invoice(osv.osv):
    _inherit = ['account.invoice','mail.thread']
    _name = 'account.invoice'

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
            etd_date = x.date_invoice
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

    def _get_currency(self, cr, uid, context=None):
        res = False
        journal_id = self._get_journal(cr, uid, context=context)
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            res = journal.currency and journal.currency.id or journal.company_id.currency_id.id
        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

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
            for line in order.invoice_line:
                val1 += line.quantity
            res[order.id] = val1
        return res

    def _total_billed_quantity(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in order.invoice_line:
                val += line.product_billed_qty
            res[order.id] = val
        return res


    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        categ_id_append = []
        amount_total = []
        appended_value = []
        tax_variable = 0.0
        tax_value = 0.0
        total_variable = 0.0
        total_variable1 = 0.0
        tax_name = ''
        append_value = []
        account_tax=[]
        cur_obj = self.pool.get('res.currency')
        sale_order_line_obj = self.pool.get('account.invoice.line')
        tax_summary_report_obj =self.pool.get('invoice.tax.summary.report')
        account_tax_obj = self.pool.get('account.tax')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            main_form_id = order.id
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.currency_id
            partner_id = order.partner_id.id
            type_of_sales = order.partner_id.type_of_sales
            cform_criteria = order.partner_id.cform_criteria
            discount_value = order.discount_value
            apply_discount = order.apply_discount
            discount_value_id = discount_value/100
            for line in order.invoice_line:
                val1 += line.price_subtotal
                price_subtotal_value = line.price_subtotal 
                product_category_id = line.product_category_id.id
                if type_of_sales == 'interstate' and cform_criteria == 'agreed':
                    tax_value = line.product_category_id.sale_with_cform.amount
                    tax_id = line.product_category_id.sale_with_cform.id
                if type_of_sales == 'interstate' and cform_criteria == 'disagreed' or type_of_sales == 'within_state':
                    tax_value = line.product_category_id.sale_without_cform.amount
                    tax_id = line.product_category_id.sale_without_cform.id
                if tax_id not in append_value:
                    append_value.append(tax_id)
                if categ_id_append ==[]:
                    categ_id_append.append(product_category_id)
                if product_category_id in categ_id_append:
                    total_variable += line.price_subtotal
                    if tax_value != tax_variable:
                        tax_variable = tax_value
                else:
                    total_variable1 += line.price_subtotal
                    different_categ_id_tax = total_variable1 * tax_value
                appended_value.append(product_category_id)
            same_categ_id_tax = total_variable * tax_variable
            different_categ_id_tax = total_variable1 * tax_value
            sum_tax_amount =same_categ_id_tax+different_categ_id_tax
            account_tax_obj_search = account_tax_obj.search(cr,uid,[('id','in',append_value)])
            account_tax_obj_browse = account_tax_obj.browse(cr,uid,account_tax_obj_search)
            for account_tax_id in account_tax_obj_browse:
                tax_id = account_tax_id.id
                tax_name = account_tax_id.name
                tax_rate = account_tax_id.tax_rate
                tax_amount = account_tax_id.amount
                if tax_variable == tax_value:
                    variable = {
                                'tax_id': tax_id,
                                'tx_name':str(tax_name),
                                'tax_rate':tax_rate,
                                'total_amount': sum_tax_amount,
                                'invoice_taxes_id':int(main_form_id)
                    }
                elif tax_amount == tax_variable and tax_variable != tax_value:
                    variable = {
                                'tax_id': tax_id,
                                'tx_name':str(tax_name),
                                'tax_rate':tax_rate,
                                'total_amount': same_categ_id_tax,
                                'invoice_taxes_id':int(main_form_id)
                    }
                elif tax_amount == tax_value and tax_variable != tax_value:
                    variable = {
                                'tax_id':tax_id,
                                'tx_name':str(tax_name),
                                'tax_rate':tax_rate,
                                'total_amount': different_categ_id_tax,
                                'invoice_taxes_id':int(main_form_id)
                    }
                tax_summary_report_obj_search = tax_summary_report_obj.search(cr,uid,[('invoice_taxes_id','=',int(main_form_id)),('tax_id','=',tax_id)])
                if not tax_summary_report_obj_search:
                    tax_summary_report_obj.create(cr,uid,variable)
                if tax_summary_report_obj_search and tax_amount == tax_variable and tax_variable != tax_value and same_categ_id_tax != 0.0:
                    cr.execute('update invoice_tax_summary_report set total_amount=%s where tax_id=%s and invoice_taxes_id=%s',(same_categ_id_tax,tax_id,main_form_id))
                elif tax_summary_report_obj_search and tax_amount == tax_value and tax_variable != tax_value and different_categ_id_tax != 0.0:
                    cr.execute('update invoice_tax_summary_report set total_amount=%s where tax_id=%s and invoice_taxes_id=%s',(different_categ_id_tax ,tax_id,main_form_id))
                elif tax_summary_report_obj_search and tax_variable == tax_value and sum_tax_amount != 0.0:
                    cr.execute('update invoice_tax_summary_report set total_amount=%s where tax_id=%s and invoice_taxes_id=%s',(sum_tax_amount ,tax_id,main_form_id))
            tax_summary_report_obj_search_second = tax_summary_report_obj.search(cr,uid,[('tax_id','not in',append_value),('invoice_taxes_id','=',int(main_form_id))])
            if tax_summary_report_obj_search_second:
                cr.execute('delete from invoice_tax_summary_report where id in %s',(tuple(tax_summary_report_obj_search_second),))
            res[order.id]['amount_tax'] = sum_tax_amount
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            total_after_discount = res[order.id]['amount_total'] * discount_value_id
            if total_after_discount != 0.0 and apply_discount:
                res[order.id]['discounted_amount'] = total_after_discount
                res[order.id]['grand_total'] = res[order.id]['amount_total'] - total_after_discount
                roundoff_grand_total = res[order.id]['grand_total'] + 0.5
                s = str(roundoff_grand_total)
                dotStart = s.find('.')
                res[order.id]['roundoff_grand_total'] = int(s[:dotStart])
            else:
                res[order.id]['grand_total'] = res[order.id]['amount_total']
                res[order.id]['discounted_amount'] = 0.0
                roundoff_grand_total = res[order.id]['grand_total'] + 0.5
                s = str(roundoff_grand_total)
                dotStart = s.find('.')
                res[order.id]['roundoff_grand_total'] = int(s[:dotStart])
        return res

    def _get_invoice_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def _get_invoice_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        """Function of the field residua. It computes the residual amount (balance) for each invoice"""
        if context is None:
            context = {}
        ctx = context.copy()
        result = {}
        currency_obj = self.pool.get('res.currency')
        for invoice in self.browse(cr, uid, ids, context=context):
            nb_inv_in_partial_rec = max_invoice_id = 0
            result[invoice.id] = 0.0
            if invoice.move_id:
                for aml in invoice.move_id.line_id:
                    if aml.account_id.type in ('receivable','payable'):
                        if aml.currency_id and aml.currency_id.id == invoice.currency_id.id:
                            result[invoice.id] += aml.amount_residual_currency
                        else:
                            ctx['date'] = aml.date
                            result[invoice.id] += currency_obj.compute(cr, uid, aml.company_id.currency_id.id, invoice.currency_id.id, aml.amount_residual, context=ctx)

                        if aml.reconcile_partial_id.line_partial_ids:
                            #we check if the invoice is partially reconciled and if there are other invoices
                            #involved in this partial reconciliation (and we sum these invoices)
                            for line in aml.reconcile_partial_id.line_partial_ids:
                                if line.invoice and invoice.type == line.invoice.type:
                                    nb_inv_in_partial_rec += 1
                                    #store the max invoice id as for this invoice we will make a balance instead of a simple division
                                    max_invoice_id = max(max_invoice_id, line.invoice.id)
            if nb_inv_in_partial_rec:
                #if there are several invoices in a partial reconciliation, we split the residual by the number
                #of invoice to have a sum of residual amounts that matches the partner balance
                new_value = currency_obj.round(cr, uid, invoice.currency_id, result[invoice.id] / nb_inv_in_partial_rec)
                if invoice.id == max_invoice_id:
                    #if it's the last the invoice of the bunch of invoices partially reconciled together, we make a
                    #balance to avoid rounding errors
                    result[invoice.id] = result[invoice.id] - ((nb_inv_in_partial_rec - 1) * new_value)
                else:
                    result[invoice.id] = new_value

            #prevent the residual amount on the invoice to be less than 0
            result[invoice.id] = max(result[invoice.id], 0.0)            
        return result

    _columns = {
        'invoice_tax_lines': fields.one2many('invoice.tax.summary.report', 'invoice_taxes_id', 'Invoice Tax summary', readonly=True),
        'client_order_ref': fields.char("Buyer's Ref/Order No", size=128),
        'delivery_note': fields.char("Delivery Note", size=128),
        'suppliers_ref': fields.char("Supplier's Reference", size=128),
        'order_date': fields.date('Order Date'),
        'po_date': fields.date('PO Date'),
        'destination': fields.char('Destination', size=128),
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
        'financial_year': fields.function(_get_financial_year, type='selection',method=True,selection=SELECTION_LIST, string="Financial Year"),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Subtotal', track_visibility='always',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'), string='Balance',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','move_id'], 50),
                'account.invoice.tax': (_get_invoice_tax, None, 50),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 50),
                'account.move.line': (_get_invoice_from_line, None, 50),
                'account.move.reconcile': (_get_invoice_from_reconcile, None, 50),
            },
            help="Remaining amount due."),
        #####################for the discount on wholesale order
        'apply_discount': fields.boolean('Apply Discount'),
        'discount_value': fields.float('Discount (in%)'),
        'discounted_amount': fields.function(_amount_all, string='Discounted Amount', multi='sums'),
        'grand_total': fields.function(_amount_all, string='Grand Total', digits_compute=dp.get_precision('Account'), multi='sums'),
        'roundoff_grand_total': fields.function(_amount_all, string='Rounded off Amount', digits_compute=dp.get_precision('Account'), multi='sums'),
        'amount_total_in_words': fields.function(_amount_in_words, string='Total amount in word', type='char', size=128),
        'total_shipped_quantity': fields.function(_total_shipped_quantity, string='Total Shipped Quantity', type='integer',digits_compute= dp.get_precision('Product UoS')),
        'total_billed_quantity': fields.function(_total_billed_quantity, string='Total Billed Quantity', type='integer',digits_compute= dp.get_precision('Product UoS')),
        'cForm': fields.char('cForm',invisible=True),
        'road_permit_attachment': fields.binary('Attach Road Permit'),
        # 'road_permit_attachment': fields.many2one('ir.attachment','Attach Road Permit'),
        'po_attachment': fields.binary('Attach PO'),
    }

    _defaults = {
        'date_invoice': fields.date.context_today,

    }


    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Receipt Details"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                'default_reference': inv.name,
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }

    # def write(self, cr, uid, ids, vals, context=None):
    #     res_id = super(account_invoice, self).write(cr, uid, ids, vals, context)
    #     account_fiscalyear_obj = self.pool.get('account.fiscalyear')
    #     if isinstance(res_id, list):
    #         main_form_id = res_id[0]
    #     else:
    #         main_form_id = res_id
        
    #     code_number = self.browse(cr,uid,ids[0]).number
    #     print 'numberrrr', code_number
    #     todays_date = datetime.now().date()
    #     code_id_search = account_fiscalyear_obj.search(cr,uid,[('date_start','<=',todays_date),('date_stop','>=',todays_date)])
    #     fiscalyear_code = account_fiscalyear_obj.browse(cr,uid,code_id_search[0]).code
    #     code_number = code_number+'/'+fiscalyear_code
    #     print 'numberrrr', code_number,fiscalyear_code, code_id_search
    #     self.write(cr,uid,main_form_id,{'number':code_number})
    #     return res_id

    def invoice_validate(self, cr, uid, ids, context=None):
        inv = self.browse(cr,uid,ids[0])
        if inv.partner_id.road_permit:
            if not inv.road_permit_attachment:
                raise osv.except_osv(_('Warning!!!'),_("Please attach the Road Permit first in the 'Other Info' tab and then validate the Invoice."))
        stock_picking_obj = self.pool.get('stock.picking.out')
        delivery_note = self.browse(cr,uid,ids[0]).delivery_note
        if delivery_note:
            ###################Updating the ready to dispatch state of delivery order on validate button
            # search_delivery_number = stock_picking_obj.search(cr,uid,[('name','=',delivery_note)])
            # browse_delivery_id = stock_picking_obj.browse(cr,uid,search_delivery_number[0])
            # stock_picking_obj.write(cr,uid,search_delivery_number[0],{'state':'ready_to_dispatch'})
            ###############################
            self.write(cr, uid, ids, {'state':'open','number':delivery_note,'journal_id':1}, context=context)
        else:
            account_fiscalyear_obj = self.pool.get('account.fiscalyear')
            code_number = self.browse(cr,uid,ids[0]).number
            todays_date = datetime.now().date()
            code_id_search = account_fiscalyear_obj.search(cr,uid,[('date_start','<=',todays_date),('date_stop','>=',todays_date)])
            fiscalyear_code = account_fiscalyear_obj.browse(cr,uid,code_id_search[0]).code
            code_number = code_number+'/'+fiscalyear_code
            self.write(cr, uid, ids, {'state':'open','number':code_number,'journal_id':1}, context=context)

    def onchange_apply_discount(self,cr,uid,ids,apply_discount):
        v={}
        if apply_discount:
            pass
        elif not apply_discount:
            v['discount_value'] = 0.0
        return {'value':v}


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

    def onchange_partner_id(self, cr, uid, ids, type, part, context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'cForm': False,'partner_shipping_id': False, 'account_id': False, 'payment_term': False, 'fiscal_position': False}}
        cForm = ''
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
        start_date_day = datetime.strptime(date_order,'%Y-%m-%d')
        search_account_payment_line = account_payment_term_line.search(cr,uid,[('payment_id','=',payment_term)])
        browse_account_payment_line = account_payment_term_line.browse(cr,uid,search_account_payment_line[0])
        days = browse_account_payment_line.days
        grace_days = 5
        if type in ('out_invoice', 'out_refund'):
            acc_id = part.property_account_receivable.id
            # partner_payment_term = part.property_payment_term and part.property_payment_term.id or False
        else:
            acc_id = part.property_account_payable.id
            # partner_payment_term = part.property_supplier_payment_term and part.property_supplier_payment_term.id or False
        if part.bank_ids:
            bank_id = part.bank_ids[0].id
        if type_of_sales == 'interstate' and cform_criteria == 'agreed':
            cForm = "Form to Receive : C Form"
            if days != 0:
                new_days = days + grace_days
                added_value_days = start_date_day+timedelta(days=new_days)
                added_values_date =str(added_value_days)
            else:
                added_values_date = ''
        elif type_of_sales == 'within_state' or (type_of_sales == 'interstate' and cform_criteria == 'disagreed'):
            cForm = ""
            if days != 0:
                added_value_days = start_date_day+timedelta(days=days)
                added_values_date =str(added_value_days)
            else:
                added_values_date = ''
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
            'shipping_street': shipping_street,
            'shipping_street2': shipping_street2,
            'shipping_city': shipping_city,
            'shipping_destination': shipping_destination,
            'destination': shipping_destination,
            'shipping_state_id': shipping_state_id,
            'shipping_zip': shipping_zip,
            'shipping_country_id': shipping_country_id,
            'billing_street': billing_street,
            'billing_street2': billing_street2,
            'billing_city': billing_city,
            'billing_state_id': billing_state_id,
            'billing_zip': billing_zip,
            'billing_country_id': billing_country_id,
            'billing_destination': billing_destination,
            'date_due': added_values_date,
            'account_id':acc_id,
            'cForm':cForm,
            # 'order_policy': 'picking',
            # 'section_id':1,
        }
        if pricelist:
            val['pricelist_id'] = pricelist
        return {'value': val}

    def onchange_date_invoice(self,cr,uid,ids,date_invoice,payment_term,partner_id):
        v={}
        res_partner_obj = self.pool.get('res.partner')
        search_partner_id =res_partner_obj.search(cr,uid,[('id','=',partner_id)])
        browse_partner_line_id = res_partner_obj.browse(cr,uid,search_partner_id)
        for browse_partner_id in browse_partner_line_id:
            type_of_sales = browse_partner_id.type_of_sales
            cform_criteria = browse_partner_id.cform_criteria
            account_payment_term_line = self.pool.get('account.payment.term.line')
            if date_invoice and payment_term:
                start_date_day = datetime.strptime(date_invoice,'%Y-%m-%d')
                search_account_payment_line = account_payment_term_line.search(cr,uid,[('payment_id','=',payment_term)])
                browse_account_payment_line = account_payment_term_line.browse(cr,uid,search_account_payment_line[0])
                days = browse_account_payment_line.days
                grace_days = 5
                if type_of_sales == 'interstate' and cform_criteria == 'agreed':
                    if days != 0:
                        new_days = days + grace_days
                        added_value_days = start_date_day+timedelta(days=new_days)
                        added_values_date =str(added_value_days)
                        v['date_due'] = added_values_date
                    else:
                        added_values_date = ''
                        v['date_due'] = added_values_date
                elif type_of_sales == 'within_state' or (type_of_sales == 'interstate' and cform_criteria == 'disagreed'):
                    if days != 0:
                        added_value_days = start_date_day+timedelta(days=days)
                        added_values_date =str(added_value_days)
                        v['date_due'] = added_values_date
                    else:
                        added_values_date = ''
                        v['date_due'] = added_values_date
            elif not date_due or payment_term:
                v['date_due'] = ''
        return {'value':v}


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _name = 'account.invoice.line'


    def _default_account_id(self, cr, uid, context=None):
        # XXX this gets the default account for the user's company,
        # it should get the default account for the invoice's company
        # however, the invoice's company does not reach this point
        if context is None:
            context = {}
        if context.get('type') in ('out_invoice','out_refund'):
            prop = self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ', 'product.category', context=context)
        else:
            prop = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
        return prop and prop.id or False 


    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.product_billed_qty, product=line.product_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    # def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
    #     res = {}
    #     tax_obj = self.pool.get('account.tax')
    #     cur_obj = self.pool.get('res.currency')
    #     for line in self.browse(cr, uid, ids):
    #         price = line.price_unit * (1-(line.discount or 0.0)/100.0)
    #         taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
    #         res[line.id] = taxes['total']
    #         if line.invoice_id:
    #             cur = line.invoice_id.currency_id
    #             res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
    #     return res

    _columns = {

    'sale_price': fields.many2one('product.customer.saleprice','Unit Price'),
    'quantity': fields.float('Shipped Quantity', digits_compute= dp.get_precision('Product UoS'), required=True, ),
    'product_billed_qty': fields.float('Billed Quantity', digits_compute= dp.get_precision('Product UoS'), required=True, ),
    'price_subtotal': fields.function(_amount_line, string='Amount', type="float", digits_compute= dp.get_precision('Account'), store=True),
    'product_category_id': fields.many2one('product.category','Product Category'),
    'tax_applied_id': fields.many2one('account.tax','Tax'),
    'sale_warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
    'product_code': fields.char('Item Code',size=264),
    }


    _defaults={
                'product_billed_qty' : 1,
    }

    


    def onchange_sale_price(self,cr,uid,ids,sale_price):
        result={}
        product_customer_saleprice_obj = self.pool.get('product.customer.saleprice')
        if sale_price:
            sale_price_search = product_customer_saleprice_obj.browse(cr,uid,sale_price).sales_price
            if sale_price_search:
                result.update({'price_unit': sale_price_search})
        return {'value':result}


    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id, 'force_company': company_id})
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined!'),_("You must first select a partner!") )
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain':{'product_uom':[]}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain':{'product_uom':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        product_obj = self.pool.get('product.product')
        partner_obj = self.pool.get('res.partner')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
        if part.lang:
            context.update({'lang': part.lang})
        context_partner = {'lang': part.lang, 'partner_id': partner_id}
        
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)
        print res.description_sale, 'desccccccccccccc'
        result['product_category_id'] = res.categ_id.id
        if type in ('out_invoice','out_refund'):
            a = res.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            a = res.property_account_expense.id
            if not a:
                a = res.categ_id.property_account_expense_categ.id
        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a

        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        # tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
        tax_id = False
        
        if type in ('in_invoice', 'in_refund'):
            result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )
        else:
            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
        # result['name'] = res.partner_ref

        result['uos_id'] = uom_id or res.uom_id.id
        result['name'] = self.pool.get('product.product').name_get(cr, uid, [res.id], context=context_partner)[0][1]
        print result['name'], 'namemmmm'
        if product_obj.description_sale:
            result['name'] += '\n'+product_obj.description_sale
            #result['name'] = '['+product_obj.default_code+']'+product_obj.name
        result['name'] = product_obj.name
        result['product_code'] = product_obj.default_code

        domain = {'uos_id':[('category_id','=',res.uom_id.category_id.id)]}
        warehouse_id = partner_obj.browse(cr, uid, partner_id).warehouse_id.id
        type_of_sales = partner_obj.browse(cr, uid, partner_id).type_of_sales
        cform_criteria = partner_obj.browse(cr, uid, partner_id).cform_criteria
        if type_of_sales == 'interstate' and cform_criteria == 'agreed':
            tax_value =  res.categ_id.sale_with_cform.id
        if type_of_sales == 'interstate' and cform_criteria == 'disagreed' or type_of_sales == 'within_state':
            tax_value =  res.categ_id.sale_without_cform.id
        result['tax_applied_id'] = tax_value
        result['sale_warehouse_id'] = warehouse_id
        result['product_uom'] = res.uom_id.id
        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            if type in ('in_invoice', 'in_refund'):
                res_final['value']['price_unit'] = res.standard_price
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if result['uos_id'] and result['uos_id'] != res.uom_id.id:
            selected_uom = self.pool.get('product.uom').browse(cr, uid, result['uos_id'], context=context)
            new_price = self.pool.get('product.uom')._compute_price(cr, uid, res.uom_id.id, res_final['value']['price_unit'], result['uos_id'])
            res_final['value']['price_unit'] = new_price
        return res_final

    def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id})
        warning = {}
        res = self.product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, currency_id, context=context)
        if not uom:
            res['value']['price_unit'] = 0.0
        if product and uom:
            prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
            prod_uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if prod.uom_id.category_id.id != prod_uom.category_id.id:
                warning = {
                    'title': _('Warning!'),
                    'message': _('The selected unit of measure is not compatible with the unit of measure of the product.')
                }
                res['value'].update({'uos_id': prod.uom_id.id})
            return {'value': res['value'], 'warning': warning}
        return res


class invoice_tax_summary_report(osv.osv):
    _name = "invoice.tax.summary.report"   
    _columns = {
        'tax_id': fields.integer('Tax_ID'),
        'tx_name': fields.char('Tax Name'),
        'total_amount': fields.float('Total Amount', size=128, required=True),
        'tax_rate': fields.float('Tax Rate(in %)'),
        'invoice_taxes_id': fields.many2one('account.invoice', 'Tax lines', ondelete='cascade', select=True),
   
    }

invoice_tax_summary_report()


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _name = 'account.voucher'


    _columns = {

    'bank_name' : fields.char('Bank Name'),

    }

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _name = 'account.move.line'


    _columns = {

    'bank_name' : fields.char('Bank Name'),

    }
