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


class product_category(osv.osv):
    _inherit="product.category"
    _columns={
        'sale_without_cform': fields.many2one('account.tax','Local Tax Rate/Sale without C-Form'),
        'sale_with_cform': fields.many2one('account.tax','Interstate/Sale against C-Form'),
        'parent_id': fields.many2one('product.category','Parent Category', select=True, ondelete='cascade'),
    }

    def onchange_parent_id(self, cr, uid, ids, parent_id, context=None):
        value = {'tax_name': False}
        if parent_id:
            emp = self.pool.get('product.category').browse(cr, uid, parent_id)
            print emp
            parent_tax = emp.tax_name.id
            if parent_tax:
                value['sale_without_cform'] = parent_tax
            else:
                value['sale_without_cform'] = ''
        return {'value': value}

product_category()

class account_tax(osv.osv):
    _inherit="account.tax"
    
    _columns={
        'tax_rate': fields.float('Tax Rate(in %)'),
    }

    
    def create(self, cr, uid, vals, context=None):
        res = super(account_tax,self).create(cr, uid, vals, context=context)
        main_id = res
        if vals.has_key('tax_rate'):
            tax_rate = vals.get('tax_rate')
            percentage_tax_rate = tax_rate / 100.0
            self.write(cr,uid,main_id,{'amount':percentage_tax_rate})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(account_tax, self).write(cr, uid, ids, vals, context=context)
        main_id = ids
        if vals.has_key('tax_rate'):
            tax_rate = vals.get('tax_rate')
            percentage_tax_rate = tax_rate / 100.0
            self.write(cr,uid,main_id,{'amount':percentage_tax_rate})
        return res


account_tax()


class product_product(osv.osv):
    _inherit = 'product.product'

    def _get_product_names(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for x in self.browse(cr, uid, ids, context=context):
            if x.id:
                va = x.name
                print va
                if va:
                    res[x.id] = va
                else:
                    res[x.id] = ''
            else:
                res[x.id] = ''
        return res

    def _get_local_tax(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for x in self.browse(cr, uid, ids, context=context):
            if x.id:
                va = x.categ_id.sale_without_cform.tax_rate
                print va
                if va:
                    res[x.id] = va
                else:
                    res[x.id] = ''
            else:
                res[x.id] = ''
        return res

    def _get_product_codes(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        cur_obj = self.pool.get('product.category')
        for x in self.browse(cr, uid, ids, context=context):
            if x.id:
                va = x.default_code
                print va
                if va:
                    res[x.id] = va
                else:
                    res[x.id] = ''
        return res

    def _get_product_category(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for x in self.browse(cr, uid, ids, context=context):
            product_id = x.id
            if x.id:
                product_category = x.product_tmpl_id.categ_id.id
                res[x.id] = product_category
            else:
                res[x.id] = ''
        return res

    def _get_interstate_tax(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for x in self.browse(cr, uid, ids, context=context):
            if x.id:
                va = x.categ_id.sale_with_cform.tax_rate
                print va
                if va:
                    res[x.id] = va
                else:
                    res[x.id] = ''
            else:
                res[x.id] = ''
        return res

    _columns={
        'product_name':fields.function(_get_product_names, type='char', string="Product Name"),
        'product_code':fields.function(_get_product_codes, type='char', string="Product Code"),
        'product_category':fields.function(_get_product_category, type='many2one', obj="product.category", method=True, string='Product Category'),
        'local_tax_rate':fields.function(_get_local_tax, type='float', string='Local Tax Rate(in %)'),
        'interstate_tax_rate':fields.function(_get_interstate_tax, type='float', string='Interstate Tax Rate(in %)'),
        
    }

product_product()


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()


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
        sale_order_line_obj = self.pool.get('sale.order.line')
        tax_summary_report_obj =self.pool.get('tax.summary.report')
        account_tax_obj = self.pool.get('account.tax')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            main_form_id = order.id
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = val2 = val3 = val4 = val5= val6 = 0.0
            cur = order.pricelist_id.currency_id
            partner_id = order.partner_id.id
            type_of_sales = order.partner_id.type_of_sales
            cform_criteria = order.partner_id.cform_criteria
            discount_value = order.discount_value
            apply_discount = order.apply_discount
            discount_value_id = discount_value/100
            for line in order.order_line:
                val2 += line.price_subtotal
                cr.execute('select distinct(tax_applied_id) from sale_order_line where order_id = %s',(main_form_id,))
                tax_id = map(lambda x: x[0], cr.fetchall())
                tax_applied_id = line.tax_applied_id.id
                tax_id_first = tax_id[0]
                if tax_applied_id == tax_id_first:
                    val1 += line.price_subtotal
                product_tax_amount = self.pool.get('account.tax').browse(cr,uid,tax_id_first).amount
                product_tax_name = self.pool.get('account.tax').browse(cr,uid,tax_id_first).name
                product_tax_rate = self.pool.get('account.tax').browse(cr,uid,tax_id_first).tax_rate
                if len(tax_id) == 2:
                    tax_id_second = tax_id[1]
                    product_tax_amount_second = self.pool.get('account.tax').browse(cr,uid,tax_id_second).amount
                    product_tax_name_second = self.pool.get('account.tax').browse(cr,uid,tax_id_second).name
                    product_tax_rate_second = self.pool.get('account.tax').browse(cr,uid,tax_id_second).tax_rate
                    val4 = val2 - val1 
                    val5 = val4 * product_tax_amount_second
            val3 = val1 * product_tax_amount 
            val6 = val3 + val5
            variable = {
                        'tax_id': tax_id_first,
                        'tx_name':str(product_tax_name),
                        'tax_rate':product_tax_rate,
                        'total_amount': val3,
                        'sale_taxes_id':int(main_form_id)
            }
            tax_summary_report_obj_search = tax_summary_report_obj.search(cr,uid,[('sale_taxes_id','=',int(main_form_id)),('tax_id','=',tax_id_first)])
            if not tax_summary_report_obj_search:
                tax_summary_report_obj.create(cr,uid,variable)
            elif tax_summary_report_obj_search:
                cr.execute('update tax_summary_report set total_amount=%s where tax_id=%s and sale_taxes_id=%s',(val3,tax_id_first,main_form_id))
            if val3 == 0.0:
                cr.execute('delete from tax_summary_report where id in %s',(tax_id_first,))
            if val4 != 0.0:
                tax_summary_report_obj_search_second = tax_summary_report_obj.search(cr,uid,[('sale_taxes_id','=',int(main_form_id)),('tax_id','=',tax_id_second)])
                variable1 = {
                        'tax_id': tax_id_second,
                        'tx_name':str(product_tax_name_second),
                        'tax_rate':product_tax_rate_second,
                        'total_amount': val5,
                        'sale_taxes_id':int(main_form_id)
                }
                if not tax_summary_report_obj_search_second:
                    tax_summary_report_obj.create(cr,uid,variable1)
                elif tax_summary_report_obj_search_second:
                    cr.execute('update tax_summary_report set total_amount=%s where tax_id=%s and sale_taxes_id=%s',(val5,tax_id_second,main_form_id))
                if val5 == 0.0:
                    cr.execute('delete from tax_summary_report where id in %s',(tax_id_second,))
            res[order.id]['amount_tax'] = val6
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val2)
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

    # def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
    #     categ_id_append = []
    #     amount_total = []
    #     appended_value = []
    #     tax_variable = 0.0
    #     tax_value = 0.0
    #     total_variable = 0.0
    #     total_variable1 = 0.0
    #     tax_name = ''
    #     append_value = []
    #     account_tax=[]
    #     cur_obj = self.pool.get('res.currency')
    #     sale_order_line_obj = self.pool.get('sale.order.line')
    #     tax_summary_report_obj =self.pool.get('tax.summary.report')
    #     account_tax_obj = self.pool.get('account.tax')
    #     res = {}
    #     for order in self.browse(cr, uid, ids, context=context):
    #         main_form_id = order.id
    #         res[order.id] = {
    #             'amount_untaxed': 0.0,
    #             'amount_tax': 0.0,
    #             'amount_total': 0.0,
    #         }
    #         val = val1 = 0.0
    #         cur = order.pricelist_id.currency_id
    #         partner_id = order.partner_id.id
    #         type_of_sales = order.partner_id.type_of_sales
    #         cform_criteria = order.partner_id.cform_criteria
    #         discount_value = order.discount_value
    #         apply_discount = order.apply_discount
    #         discount_value_id = discount_value/100
    #         for line in order.order_line:
    #             val1 += line.price_subtotal
    #             price_subtotal_value = line.price_subtotal 
    #             product_category_id = line.product_category_id.id
    #             if type_of_sales == 'interstate' and cform_criteria == 'agreed':
    #                 tax_value = line.product_category_id.sale_with_cform.amount
    #                 tax_id = line.product_category_id.sale_with_cform.id
    #             if type_of_sales == 'interstate' and cform_criteria == 'disagreed' or type_of_sales == 'within_state':
    #                 tax_value = line.product_category_id.sale_without_cform.amount
    #                 tax_id = line.product_category_id.sale_without_cform.id
    #             if tax_id not in append_value:
    #                 append_value.append(tax_id)
    #             if categ_id_append ==[]:
    #                 categ_id_append.append(product_category_id)
    #             if product_category_id in categ_id_append:
    #                 total_variable += line.price_subtotal
    #                 if tax_value != tax_variable:
    #                     tax_variable = tax_value
    #             else:
    #                 total_variable1 += line.price_subtotal
    #                 different_categ_id_tax = total_variable1 * tax_value
    #             appended_value.append(product_category_id)
    #         same_categ_id_tax = total_variable * tax_variable
    #         different_categ_id_tax = total_variable1 * tax_value
    #         sum_tax_amount =same_categ_id_tax+different_categ_id_tax
    #         account_tax_obj_search = account_tax_obj.search(cr,uid,[('id','in',append_value)])
    #         account_tax_obj_browse = account_tax_obj.browse(cr,uid,account_tax_obj_search)
    #         for account_tax_id in account_tax_obj_browse:
    #             tax_id = account_tax_id.id
    #             tax_name = account_tax_id.name
    #             tax_rate = account_tax_id.tax_rate
    #             tax_amount = account_tax_id.amount
    #             if tax_variable == tax_value:
    #                 variable = {
    #                             'tax_id': tax_id,
    #                             'tx_name':str(tax_name),
    #                             'tax_rate':tax_rate,
    #                             'total_amount': sum_tax_amount,
    #                             'sale_taxes_id':int(main_form_id)
    #                 }
    #             elif tax_amount == tax_variable and tax_variable != tax_value:
    #                 variable = {
    #                             'tax_id': tax_id,
    #                             'tx_name':str(tax_name),
    #                             'tax_rate':tax_rate,
    #                             'total_amount': same_categ_id_tax,
    #                             'sale_taxes_id':int(main_form_id)
    #                 }

    #             elif tax_amount == tax_value and tax_variable != tax_value:
    #                 variable = {
    #                             'tax_id':tax_id,
    #                             'tx_name':str(tax_name),
    #                             'tax_rate':tax_rate,
    #                             'total_amount': different_categ_id_tax,
    #                             'sale_taxes_id':int(main_form_id)
    #                 }
    #             tax_summary_report_obj_search = tax_summary_report_obj.search(cr,uid,[('sale_taxes_id','=',int(main_form_id)),('tax_id','=',tax_id)])
    #             if not tax_summary_report_obj_search:
    #                 tax_summary_report_obj.create(cr,uid,variable)
    #             if tax_summary_report_obj_search and tax_amount == tax_variable and tax_variable != tax_value and same_categ_id_tax != 0.0:
    #                 cr.execute('update tax_summary_report set total_amount=%s where tax_id=%s and sale_taxes_id=%s',(same_categ_id_tax,tax_id,main_form_id))
    #             elif tax_summary_report_obj_search and tax_amount == tax_value and tax_variable != tax_value and different_categ_id_tax != 0.0:
    #                 cr.execute('update tax_summary_report set total_amount=%s where tax_id=%s and sale_taxes_id=%s',(different_categ_id_tax ,tax_id,main_form_id))
    #             elif tax_summary_report_obj_search and tax_variable == tax_value and sum_tax_amount != 0.0:
    #                 cr.execute('update tax_summary_report set total_amount=%s where tax_id=%s and sale_taxes_id=%s',(sum_tax_amount ,tax_id,main_form_id))
    #         tax_summary_report_obj_search_second = tax_summary_report_obj.search(cr,uid,[('tax_id','not in',append_value),('sale_taxes_id','=',int(main_form_id))])
    #         if tax_summary_report_obj_search_second:
    #             cr.execute('delete from tax_summary_report where id in %s',(tuple(tax_summary_report_obj_search_second),))
    #         res[order.id]['amount_tax'] = sum_tax_amount
    #         res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
    #         res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
    #         total_after_discount = res[order.id]['amount_total'] * discount_value_id
    #         if total_after_discount != 0.0 and apply_discount:
    #             res[order.id]['grand_total'] = res[order.id]['amount_total'] - total_after_discount
    #             roundoff_grand_total = res[order.id]['grand_total'] + 0.5
    #             s = str(roundoff_grand_total)
    #             dotStart = s.find('.')
    #             res[order.id]['roundoff_grand_total'] = int(s[:dotStart])
    #         else:
    #             res[order.id]['grand_total'] = res[order.id]['amount_total']
    #             roundoff_grand_total = res[order.id]['grand_total'] + 0.5
    #             s = str(roundoff_grand_total)
    #             dotStart = s.find('.')
    #             res[order.id]['roundoff_grand_total'] = int(s[:dotStart])
    #     return res

    _columns = {
        'tax_lines': fields.one2many('tax.summary.report', 'sale_taxes_id', 'Tax summary', readonly=True),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
        ######################for the discount on wholesale order
        'apply_discount': fields.boolean('Apply Discount'),
        'discount_value': fields.float('Discount (in%)'),
        # 'discount_amount': fields.function(_amount_all, string='Rounded off Amount', digits_compute=dp.get_precision('Quantity'), multi='sums'),
        'grand_total': fields.function(_amount_all, string='Grand Total', digits_compute=dp.get_precision('Account'), multi='sums'),
        'roundoff_grand_total': fields.function(_amount_all, string='Rounded off Amount', multi='sums'),
        'discounted_amount': fields.function(_amount_all, string='Discounted Amount', multi='sums'),
    }

    def onchange_apply_discount(self,cr,uid,ids,apply_discount):
        v={}
        if apply_discount:
            pass
        elif not apply_discount:
            v['discount_value'] = 0.0
        return {'value':v}

    def save(self,cr,uid,ids,context=None):
        return True

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns ={
        'product_category_id': fields.many2one('product.category','Product Category'),
        'tax_applied_id': fields.many2one('account.tax','Tax'),
        'product_code': fields.char('Item Code',size=264),
    }


    #------------------------------------------------------------------------------------
    # Inherit Default Product Onchange For the Sale Price to Taken from the New Interface
    #------------------------------------------------------------------------------------
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        ###New Sale Price Interface Object is given###########
        product_customer_obj = self.pool.get('product.customer')
        product_customer_saleprice_obj = self.pool.get('product.customer.saleprice')
        ######################################################
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        result['product_category_id'] = product_obj.categ_id.id
        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            ##############changed the code for taxes##############
            #result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)
            result['tax_id'] = False
            ######################################################

        if not flag:
            ############################################################
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
            #result['name'] = '['+product_obj.default_code+']'+product_obj.name
            result['name'] = product_obj.name
            result['product_code'] = product_obj.default_code
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            ##########code for take the Unit Price in the Sale Order Line####
            # product_customer_search = product_customer_obj.search(cr,uid,[('product_id','=',product)])
            # if product_customer_search:
            #     product_search_id = product_customer_search[0]
            #     customer_salesprice_search = product_customer_saleprice_obj.search(cr,uid,[('customer_saleprice_id','=',product_search_id),('customer_id','=',partner_id)])
            #     if customer_salesprice_search:
            #         for customer_salesprice_search_id in product_customer_saleprice_obj.browse(cr,uid,customer_salesprice_search):
            #             price = customer_salesprice_search_id.sales_price
            #             if price is False:
            #                 warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
            #                         "You have to change either the product, the quantity or the pricelist.")

            #                 warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            #             else:
            #                 result.update({'price_unit': price})
            #     else:
            #         price = 0.0
            #         result.update({'price_unit': price})
            # else:
            #     price = 0.0
            #     result.update({'price_unit': price})

            #########################################################################
        ###############Warehouse Location has been given
        tax_value=''
        warehouse_id = partner_obj.browse(cr, uid, partner_id).warehouse_id.id
        type_of_sales = partner_obj.browse(cr, uid, partner_id).type_of_sales
        cform_criteria = partner_obj.browse(cr, uid, partner_id).cform_criteria
        if type_of_sales == 'interstate' and cform_criteria == 'agreed':
            tax_value =  product_obj.categ_id.sale_with_cform.id
        if type_of_sales == 'interstate' and cform_criteria == 'disagreed' or type_of_sales == 'within_state':
            tax_value =  product_obj.categ_id.sale_without_cform.id
        result['tax_applied_id'] = tax_value
        result['sale_warehouse_id'] = warehouse_id
        result['product_uom'] = product_obj.uom_id.id
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}


    ############################################################
    # Inherited the Product UOM onchange for the price unit function
    #############################################################
    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, context=None):
        context = context or {}
        lang = lang or ('lang' in context and context['lang'])
        # if not uom:
        #     return {'value': {'product_uom' : uom or False}}
        return self.product_id_change(cursor, user, ids, pricelist, product,
                qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id, lang=lang, update_tax=update_tax,
                date_order=date_order, context=context)

sale_order_line()


class tax_summary_report(osv.osv):
    _name = "tax.summary.report"   
    _columns = {
        'tax_id': fields.integer('Tax_ID'),
        'tx_name': fields.char('Tax Name'),
        'total_amount': fields.float('Total Amount', size=128, required=True),
        'tax_rate': fields.float('Tax Rate(in %)'),
        'sale_taxes_id': fields.many2one('sale.order', 'Tax lines', ondelete='cascade', select=True),
   
    }

tax_summary_report()
