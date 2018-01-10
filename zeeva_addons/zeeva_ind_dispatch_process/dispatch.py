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
from dateutil import tz
from time import strftime
from datetime import date
from dateutil.relativedelta import relativedelta
from time import time
import string
import locale
import base64
import re


class shipment_dispatch(osv.osv):
    _name = 'shipment.dispatch'
    _description = 'Dispatch'
    _inherit = ['mail.thread']
    
    def _compute_total_transit_days(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for x in self.browse(cr, uid, ids, context=context):
            delivered_date = x.delivered_date
            dispatch_date = x.dispatch_date
            if delivered_date and dispatch_date:
                delivered_date_date = datetime.strptime(str(delivered_date), "%Y-%m-%d").date()
                dispatch_date_date = datetime.strptime(str(dispatch_date), "%Y-%m-%d").date()
                transit_day = relativedelta(delivered_date_date,dispatch_date_date)
                if delivered_date < dispatch_date:
                    # osv.except_osv(_('Warning!'),_("Dispatch Date cannot be greater than Delivered Date"))
                    res[x.id] = ''
                else:
                    if transit_day.days == 0.0 or transit_day.days == 1.0:
                        print transit_day.days,'transit days'
                        res[x.id] = 1
                    else:
                        res[x.id] = transit_day.days - 1
                print res
                return res
            else:
                res[x.id] = 0
                return res

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            
            'waybill_no': self.pool.get('ir.sequence').get(cr, uid, 'dispatch.through'),      
        })
        return super(shipment_dispatch, self).copy(cr, uid, id, default, context=context)

    def _mark_true(self, cr, uid, ids, name, arg, context=None):
        res = {}
        flag = False
        today = datetime.today().date()
        for x in self.browse(cr,uid,ids,context=context):
            eta = x.eta
            s_id = x.id
            state = x.state
            print eta, state
            if state in ('ready to dispatch','in transit') and str(eta) < str(today):
                flag = True
                
            else:
                flag = False
            res[x.id] = flag
        return res

     
    def _get_shipping_person(self, cr, uid, context=None):
        search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Shipping & Distribution')])
        print search_dept, 'shipping department iddddd'
        search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
        print search_emp_in_shipping, 'employee idddd'
        for x in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
            userID = x.user_id.id
        return userID


    _columns = {
        'shipping_person': fields.many2one('res.users','Shipping Person'),
        'name': fields.char('Dispatch No'),
        'invoice_no': fields.many2one('account.invoice', 'Invoice No',domain="[('type','=','out_invoice')]"),
        'customer': fields.many2one('res.partner','Customer',domain="[('customer','=',True)]"),
        'invoice_date': fields.date('Invoice Date'),
        'invoice_amt':fields.float('InVoice Amount'),
        'do_no': fields.many2one('stock.picking.out','DO No.', domain="[('type','=','out')]"),
        'so_no': fields.many2one('sale.order','SO No.'),
        'shipping_street': fields.char('Shipping Street',size=128),
        'shipping_street2': fields.char('Shipping Street2',size=128),
        'shipping_city': fields.char(' Shipping City',size=128),
        'shipping_city2': fields.many2one('res.city','Shipping Cities'),
        'shipping_destination': fields.char('Shipping Destination',size=128),
        'shipping_state_id': fields.many2one('res.country.state',' Shipping State'),
        'shipping_zip': fields.char('Shipping Zip',size=24),
        'shipping_country_id': fields.many2one('res.country','Shipping Country'),
        'shipping_contact_person': fields.many2one('res.partner', 'Contact Person'),
        'shipping_contact_mobile_no': fields.char('Mobile Number',size=68),
        'shipping_contact_landline_no': fields.char('Landline Number',size=68),
        'shipping_email_id': fields.char('Email ID',size=68),
        'consignor': fields.many2one('res.company','Consignor'),
        'dispatch_date': fields.date('Dispatch Date'),
        'courier_name': fields.many2one('dispatch.through','Courier Name'),
        'waybill_no': fields.char('Waybill No.'),
        'box': fields.integer('No of Boxes'),
        'weight': fields.float('Weight'),
        # 'etd': fields.date('ETD'),
        'eta': fields.date('Estimated Time of Delivery'),
        'delivered_date': fields.date('Delivered Date'),
        'attachment_of_pod': fields.binary('POD'),
        'total_transit_days': fields.function(_compute_total_transit_days,string='Total Transit Days',type='integer',store=True),
        'grn_no': fields.char('GRN No.'),
        'road_permit': fields.binary('Road Permit'),
        'grn': fields.binary('GRN'),
        'dispatch_order_lines': fields.one2many('dispatch.order.line', 'dispatch_order_id', 'Dispatch Lines'),
        'remarks_dispatch_lines': fields.one2many('remarks.dispatch','remarks_id','Remarks'),
        'state': fields.selection([('ready to dispatch','Ready to Dispatch'),('in transit', 'In Transit'),('delivered', 'Delivered'),('cancelled', 'Cancelled')], 'Status'),    
        'flag': fields.boolean('Flag'),
        'flag1': fields.boolean('Flag'),
        'date_today': fields.date('Today'),
        'in_transit': fields.function(_mark_true, type='boolean', string='In transit'),
        'xyz': fields.selection([('A','A'),('B', 'B'),('C', 'C'),('D', 'D')], 'xyz'),
        'date_creation': fields.date('Date'),
        'dispatch_backorder_id': fields.many2one('shipment.dispatch', 'Back Order of', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="If this shipment was split, then this field links to the shipment which contains the already processed part.", select=True),
        'internal_waybill_no': fields.char('Waybill No'),
        'partial_picking': fields.boolean('Partial Picking'),
        'po_attachment': fields.binary('Attach PO'),
        'current_url':fields.char('URL'),
    }
        
    _defaults = {
        'box':1,
        'name': lambda self, cr, uid, context: '/',
        'waybill_no': lambda self, cr, uid, context: '/',
        'state': 'ready to dispatch',
        'consignor': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'shipment.dispatch', context=c),
        'date_today': fields.date.context_today,
        'in_transit': False,
        'shipping_person': _get_shipping_person,
        'xyz':'B',
        'date_creation': fields.date.context_today,
    }

    _order = 'xyz asc'


    def do_dispatch_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        print ids, partial_datas, 'values from the wizardddd'
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('dispatch.order.line')
        dispatch_obj = self.pool.get('shipment.dispatch')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        partial_date = partial_datas.get('partial_date')
        partial_picking = partial_datas.get('partial_picking')
        x = self.browse(cr, uid, ids[0], context)
        delivered_dt =  x.delivered_date
        dispatch_dt = x.dispatch_date
        print dispatch_dt, 'dispathc dattte'
        eta = x.eta
        from datetime import date
        from datetime import datetime
        eta_new = datetime.strptime(eta, "%Y-%m-%d").strftime("%d-%m-%Y")
        inv_no = x.invoice_no.id
        inv_name = x.invoice_no.number
        courier = x.courier_name.name
        so_no = x.so_no.name
        do_no = x.do_no.name

        for pick in self.browse(cr, uid, ids, context=context):
            pick1 = dispatch_obj.browse(cr,uid,ids[0])
            main_form_id = pick1.id
            values = {
                
                'dispatch_date':partial_date,
                'partial_picking':partial_picking,
                'eta':partial_date
            }
            print values, 'valuessss'
            print pick, 'pickkkkkkk'
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            print pick.dispatch_order_lines, 'pick order lines'
            for move in pick.dispatch_order_lines:
                print move.id,'mmmmmmmmmmmmmmmm'
                print partial_datas, 'partial data dictionary'
                partial_data = partial_datas.get('move%s'%(move.id), {})
                print partial_data, 'partial_data'
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
                # product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)
                print too_few, too_many, complete, 'lists of partial picking'
                
            empty_picking = not any(q for q in move_product_qty.values() if q > 0)
            print empty_picking, 'Emptyyyy Pickinggg'
            for move in too_few:
                product_qty = move_product_qty[move.id]
                print product_qty, 'product_qty'
                print new_picking, empty_picking, 'Pickingggg'
                if not new_picking and not empty_picking:

                    letters = list(string.ascii_uppercase)
                    sequence_name = pick.name
                    sequence_name_split = sequence_name.split('-')
                    for sequence_letters in sequence_name_split:
                        if sequence_letters in letters:
                            sequence_letters_index = letters.index(sequence_letters)
                            sequence_letters_index_add =sequence_letters_index+1
                            delete_letters = letters[0:sequence_letters_index_add]
                            for delete_letters_id in delete_letters:
                                if delete_letters_id in letters:
                                    pop_delete_letters = letters.remove(delete_letters_id)
                            next_letter = letters[0]
                            previous_letters = delete_letters[-1]
                            sequence_name_split_second = sequence_name.split('-')
                            remove_last_letter = sequence_name_split_second.remove(sequence_name_split_second[-1])
                            join_letters= '-'.join(sequence_name_split_second)
                            new_picking_name = join_letters+ '-'+ previous_letters
                            same_sequence_name = join_letters+'-'+next_letter
                        else:
                            sequence_letters_index_zero = letters[0]
                            sequence_letters_index_one = letters[1]
                            new_picking_name = pick.name+ '-'+ sequence_letters_index_zero
                            same_sequence_name = pick.name+'-'+sequence_letters_index_one
                        print same_sequence_name, new_picking_name, 'Seeequenceeeeeeee'
                    self.write(cr, uid, [pick.id], 
                               {'name': same_sequence_name
                               })
                    pick.refresh()
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': new_picking_name,
                                'dispatch_order_lines' : [],
                                'state':'in transit',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'dispatch_order_id' : new_picking,
                            'state': 'in transit',
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty': move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
                        })

            if new_picking:
                print new_picking, 'new_pickingggg idddd'
                self.write(cr,uid,[pick.id],{'dispatch_backorder_id': new_picking,'dispatch_date':dispatch_dt})
                move_obj.write(cr, uid, [c.id for c in complete], {'dispatch_order_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                if new_picking:
                    defaults.update(dispatch_order_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            if new_picking:
                self.write(cr, uid, [pick.id], {'dispatch_order_id': new_picking})
                dispatch_obj.write(cr,uid,ids,values)
                stock_obj = self.pool.get('stock.picking.out')
                delivery_id = x.do_no.id
                stock_obj.write(cr,uid,delivery_id,{'state':'dispatched'})
                delivered_pack_id = new_picking
                back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
                search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Sales & Marketing Support')])
                search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
                search_country_head = self.pool.get('hr.job').search(cr,uid,[('name','=','Country Head For Modern Trade')])
                search_emp_in_country_head = self.pool.get('hr.employee').search(cr,uid,[('job_id','=',search_country_head[0])])  
                user_list = []
                for p in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_country_head):
                    userID = p.user_id.id
                    user_list.append(userID)
                for c in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
                    userID = c.user_id.id
                    user_list.append(userID)
                
                dispatch_obj.message_subscribe_users(cr, SUPERUSER_ID, [new_picking], user_ids=user_list, context=context)
                message = _("<b>Status: Ready to Dispatch --> In Transit</b><br/><br/>The Products in the Invoice %s Sale Order %s Delivery Order %s Dispatch No %s are in Transit and ETA is %s")%(inv_name,so_no,do_no,x.name,eta_new)
                dispatch_obj.message_post(cr, uid, [new_picking], body = message, type='comment', subtype='mt_comment', context = context)
                # self.message_post(cr, uid, ids, body=_("Partial Dispatch <em>%s</em> has been <b>created</b>.") % (back_order_name), context=context)
            else:
                delivered_pack_id = pick.id
            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}
        return res


    def reminder_pending_dispatch_order(self,cr,uid,context=None):
        today = datetime.today().date()
        rec_search = self.search(cr, uid, [('id', '>', 0),('eta','=',today),('state','in',('ready to dispatch','in transit'))], context=None)
        print rec_search
        for x in self.browse(cr,uid,rec_search):
            count = 0
            eta = x.eta
            s_id = x.id
            state = x.state
            customer = x.customer.name
            print eta, state            
            search_template_record = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','shipment.dispatch'),('lang','=','Dispatch Status')], context=context)
            if search_template_record:
                self.pool.get('email.template').send_mail(cr, uid, search_template_record[0], s_id, force_send=True, context=context)
                print "Send Reminder"
                count = count+1
                return True

    def reminder_etd_crossed(self,cr,uid,context=None):
        today = datetime.today().date()
        rec_search = self.search(cr, uid, [('id', '>', 0),('eta','<=',today),('state','in',('ready to dispatch','in transit'))], context=None)
        print rec_search
        ir_model_data = self.pool.get('ir.model.data')
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        print base_url ,'baseee urlll'
        query = {'db': cr.dbname}
        templ_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_ind_dispatch_process', 'dispatch_form')[1]
        print templ_id, 'menu iddd'
        for x in self.browse(cr,uid,rec_search):
            count = 0
            eta = x.eta
            s_id = x.id
            state = x.state
            customer = x.customer.name
            print eta, state
            url=base_url+"?db=%s#id=%s&view_type=form&model=shipment.dispatch"%(cr.dbname,s_id)
            print url, 'main url'            
            self.write(cr,uid,s_id,{'current_url':url})
            search_template_record = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','shipment.dispatch'),('lang','=','ETD crossed')], context=context)
            if search_template_record:
                self.pool.get('email.template').send_mail(cr, uid, search_template_record[0], s_id, force_send=True, context=context)
                print "Send Reminder"
                count = count+1
                return True


    def reminder_pending_grn(self,cr,uid,context=None):
        today = datetime.today().date()
        rec_search = self.search(cr, uid, [('id','>',0),('customer.grn', '=',True),('state','=','delivered'),('grn','=',None)], context=None)
        print rec_search
        email_obj = self.pool.get('email.template')  
        #get the object corresponding to template_id
        for x in self.browse(cr,uid,rec_search):
            count = 0
            s_id = x.id            
            search_template_record = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','shipment.dispatch'),('lang','=','Pending GRN')], context=context)
            if search_template_record:
                self.pool.get('email.template').send_mail(cr, uid, search_template_record[0], s_id, force_send=True, context=context)
                print "Send Reminder"
                count = count+1
        return True

    def check_pending_dispatch_order(self,cr,uid,context=None):
        today = datetime.today().date()
        rec_search = self.search(cr, uid, [('id', '>', 0),('eta','<',today),('state','in',('ready to dispatch','in transit'))], context=None)
        print rec_search
        for x in self.browse(cr,uid,rec_search):
            count = 0
            eta = x.eta
            s_id = x.id
            state = x.state
            customer = x.customer.name
            self.write(cr,uid,s_id,{'xyz':'A'})
            print s_id, eta, state            
            count = count+1
        return True

    def print_confirmation_letter(self, cr, uid, ids, context=None):
        
        #assert len(ids) == 1, 'This option should only be used for a single id at a time'
        #wf_service = netsvc.LocalService("workflow")
        #wf_service.trg_validate(uid, 'hr.employee.confirmation', ids[0], 'quotation_sent', cr)
            
        datas = {
                 'model': 'shipment.dispatch',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
                 # 'date_of_confirmation': dateOfConf,
        }
        print datas
        return {'type': 'ir.actions.report.xml', 'report_name': 'shipment.dispatch', 'datas': datas, 'nodestroy': True}

    def onchange_shipping_contact_person(self,cr,uid,ids,shipping_contact_person):
        v={}
        res_partner_obj=self.pool.get('res.partner')
        if shipping_contact_person:
            res_partner_browse = res_partner_obj.browse(cr,uid,shipping_contact_person)
            v['shipping_contact_mobile_no'] = res_partner_browse.mobile
            v['shipping_contact_landline_no'] = res_partner_browse.phone
            v['shipping_email_id'] = res_partner_browse.email
        return {'value':v}

   
    def onchange_courier(self, cr, uid, ids, courier_name, context=None):
        value={'waybill_no': False}
        print 'in the onchange function'
        c =  self.browse(cr,uid,ids[0])
        cn = self.pool.get('dispatch.through').browse(cr, uid, courier_name)

        print c.internal_waybill_no, 'internal_waybill_no'
        
        waybill_no = False
        if courier_name:

            if cn.name == "Hand Delivery By Office Boy":  
                print  'in the if loop'
                if c.internal_waybill_no:        
                    waybill_no = c.internal_waybill_no
                else:
                    waybill_no = '/'
            else:
                print 'in the else loop'
                waybill_no = False
            value = {
            'waybill_no' : waybill_no
            }

            print value, 'valuess'
            return {'value':value}


        

    def onchange_dispatch(self, cr, uid, ids, dispatch_date, delivered_date, context=None):
        
        if dispatch_date and delivered_date:
            if dispatch_date > delivered_date:
                raise osv.except_osv(_('Warning!'),_("Dispatch Date cannot be greater than Delivered Date"))   
        else:
            return False
        return False

    def create(self, cr, uid, vals, context=None):
        res_id = super(shipment_dispatch, self).create(cr, uid, vals, context)
        #print vals, 'vallssss'
        courier = vals['courier_name']  
        c_name = ''
        code_number = ''
        search_courier = self.pool.get('dispatch.through').search(cr,uid,[('id','=',courier)], context=context)
        for g in self.pool.get('dispatch.through').browse(cr,uid,search_courier):
            c_name = g.name
        account_fiscalyear_obj = self.pool.get('account.fiscalyear')
        if isinstance(res_id, list):
            main_form_id = res_id[0]
        else:
            main_form_id = res_id
        if c_name == 'Hand Delivery By Office Boy':
            vals['waybill_no'] = self.pool.get('ir.sequence').get(cr, uid, 'dispatch.through') or '/'
            print vals['waybill_no'], 'waybill_no'
            vals['internal_waybill_no'] = vals['waybill_no']
            print vals['internal_waybill_no'], 'internall waybill_no'
            self.write(cr,uid,main_form_id,{'waybill_no': vals['waybill_no'],'internal_waybill_no': vals['waybill_no']})
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'shipment.dispatch') or '/'
            code_number = vals.get('name')
            todays_date = datetime.now().date()
            code_id_search = account_fiscalyear_obj.search(cr,uid,[('date_start','<=',todays_date),('date_stop','>=',todays_date)])
            fiscalyear_code = account_fiscalyear_obj.browse(cr,uid,code_id_search[0]).code
            code_number = code_number+'/'+fiscalyear_code
            self.write(cr,uid,main_form_id,{'name':code_number})
        search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Sales & Marketing Support')])
        search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
        search_country_head = self.pool.get('hr.job').search(cr,uid,[('name','=','Country Head For Modern Trade')])
        search_emp_in_country_head = self.pool.get('hr.employee').search(cr,uid,[('job_id','=',search_country_head[0])])  
        user_list = []
        for x in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_country_head):
            userID = x.user_id.id
            user_list.append(userID)
        for x in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
            userID = x.user_id.id
            user_list.append(userID)
        print user_list, 'user lissstt'
        self.message_subscribe_users(cr, SUPERUSER_ID, [main_form_id], user_ids=user_list, context=context)
        self.message_post(cr, uid, [main_form_id], body=_("<b>Dispatch <em>%s</em> has been created</b>.") % (vals['name']), type='comment', subtype='mt_comment',context=context)
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        #print vals, 'valsssssssss'
        res = super(shipment_dispatch,self).write(cr, uid, ids, vals, context=context)
        if isinstance(ids, list):
            main_form_id = ids[0]
        else:
            main_form_id = ids
        c = self.browse(cr, uid, main_form_id)
        waybill_no = c.waybill_no
        internal_waybill_no = c.internal_waybill_no
        wb_no = False
        print c.dispatch_date, 'dispatch date'
        print c.delivered_date, 'delivered_date'
        print c.eta, 'estimated time of delivery'
        if c.dispatch_date and c.delivered_date:
            if c.dispatch_date > c.delivered_date:
                raise osv.except_osv(_('Warning!'),_("Dispatch Date cannot be greater than Delivered Date"))
        if c.eta < c.dispatch_date:
            raise osv.except_osv(_('Warning!'),_("The 'Estimated Time of Delivery' Date has to be greater than or equal to Dispatch Date"))      
        if vals.has_key('courier_name'):
            courier = vals['courier_name']  
            c_name = ''
            search_courier = self.pool.get('dispatch.through').search(cr,uid,[('id','=',courier)], context=context)
            for g in self.pool.get('dispatch.through').browse(cr,uid,search_courier):
                c_name = g.name
            if c_name == "Hand Delivery By Office Boy":
                if internal_waybill_no:
                    wb_no = internal_waybill_no
                else:
                    wb_no = self.pool.get('ir.sequence').get(cr, uid, 'dispatch.through') or '/'
                res = super(shipment_dispatch,self).write(cr, uid, main_form_id, {'waybill_no':wb_no}, context=context)
        return res

    def action_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Open the partial picking wizard"""
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dispatch.partial.picking',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }

    def ready_to_dispatch(self, cr, uid, ids, context=None):
        x = self.browse(cr, uid, ids[0], context)
        delivered_dt =  x.delivered_date
        dispatch_dt = x.dispatch_date
        eta = x.eta
        from datetime import date
        from datetime import datetime
        eta_new = datetime.strptime(eta, "%Y-%m-%d").strftime("%d-%m-%Y")
        inv_no = x.invoice_no.id
        inv_name = x.invoice_no.number
        courier = x.courier_name.name
        so_no = x.so_no.name
        do_no = x.do_no.name
        waybill_no = x.waybill_no
        flag = x.flag
        flag1 = x.flag1
        box = x.box
        if box == 0:
            raise osv.except_osv(_('Warning'),_('Number of Boxes cannot be Zero.'))

        if courier != "Hand Delivery By Office Boy":
            if waybill_no == "/":
                raise osv.except_osv(_('Warning!'),_("Please enter the Waybill No.")) 
        search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Sales & Marketing Support')])
        print search_dept, 'shipping department iddddd'
        search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
        print search_emp_in_shipping, 'employee idddd'
        user_list = []
        for p in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
            userID = p.user_id.id
            user_list.append(userID)
        if dispatch_dt and delivered_dt:
            if dispatch_dt > delivered_dt:
                raise osv.except_osv(_('Warning!'),_("Dispatch Date cannot be greater than Delivered Date"))   
        if eta < dispatch_dt:
            raise osv.except_osv(_('Warning!'),_("ETA cannot be less than Dispatch Date"))   
        self.message_subscribe_users(cr, SUPERUSER_ID, ids, user_ids=user_list, context=context)
        return self.action_process(cr, uid, ids, context=context)


    def in_transit(self, cr, uid, ids, context=None):
        stock_obj = self.pool.get('stock.picking.out')
        x = self.browse(cr, uid, ids[0], context)
        from datetime import date
        from datetime import datetime
        inv_name = x.invoice_no.number
        eta = x.eta
        delivered_date = x.delivered_date
        delivered_date = datetime.strptime(delivered_date, "%Y-%m-%d").strftime("%d-%m-%Y")

        so_no = x.so_no.name
        do_no = x.do_no.name
        do_id = x.do_no.id
        new_delivered_date = datetime.strptime(str(x.delivered_date), "%Y-%m-%d").date()
        new_eta = datetime.strptime(str(x.eta), "%Y-%m-%d").date()
        tenure = relativedelta(new_delivered_date,new_eta)
        print tenure.days, 'tenuree days'
        search_value = self.pool.get('remarks.dispatch').search(cr,uid,[('remarks_id','=',x.id)])
        
        if tenure.days > 0:
            if not x.remarks_dispatch_lines:
                raise osv.except_osv(_('Warning!'),_("Since the shipment has been delivered late, please add the reason for delay of shipment in the 'Remarks' section."))
            if x.remarks_dispatch_lines:
                for m in self.pool.get('remarks.dispatch').browse(cr,uid,search_value):
                    if not m.remarks_date or not m.remarks_reason:
                        raise osv.except_osv(_('Warning!'),_("Since the shipment has been delivered late, please add the reason for delay of shipment in the 'Remarks' section."))

        search_template_record = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','shipment.dispatch'),('lang','=','Delivered To Customer')], context=context)
        if search_template_record:
            print "ggggggggggggggggggggggggggggggggggggggggggggggg", search_template_record
            print 'I am intoooo self rating reminder definition'
            self.pool.get('email.template').send_mail(cr, uid, search_template_record[0], x.id, force_send=True, context=context)
        message = _("<b>Status: In Transit --> Delivered</b><br/><br/>The Products in the Invoice %s Sale Order %s Delivery Order %s Dispatch No %s has been Delivered on %s")%(inv_name,so_no,do_no,x.name,delivered_date)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        self.write(cr, uid, ids, {'state': 'delivered'}, context=context)
        search_dispatch_total = self.search(cr,uid,[('do_no','=',do_id)])
        search_dispatch_delivered = self.search(cr,uid,[('do_no','=',do_id),('state','=','delivered')])
        if len(search_dispatch_total) == len(search_dispatch_delivered):
            stock_obj.write(cr,uid,do_id,{'state':'delivered'})
        return True
        

    def cancelled(self, cr, uid, ids, context=None):
        x = self.browse(cr, uid, ids[0], context)
        inv_name = x.invoice_no.number
        so_no = x.so_no.name
        do_no = x.do_no.name
        message = _("Hi All,<p>The Dispatch Order %s has been cancelled")%(x.name)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)

shipment_dispatch()


class dispatch_order_line(osv.osv):
    _name = 'dispatch.order.line'  

    _columns = {
        'name': fields.char('Description'),
        'dispatch_order_id':fields.many2one('shipment.dispatch','Dispatch Lines'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True),('type','<>','service')], required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True),
        'product_qty': fields.float('Shipped Quantity', digits_compute=dp.get_precision('Quantity')),
        'warehouse': fields.many2one('stock.warehouse','Stock Warehouse'),
        'state': fields.selection([('ready to dispatch','Ready to Dispatch'),('in transit', 'In Transit'),('delivered', 'Delivered'),('cancelled', 'Cancelled')], 'Status'),    
        }

    _defaults = {

    'product_qty': 1,

    }
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        uom_id = False
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            uom_id = product.uom_id.id
        return {'value': {'product_uom': uom_id}}

dispatch_order_line()

class remarks_dispatch(osv.osv):
    _name = 'remarks.dispatch'
    _columns = {

        'remarks_id':fields.many2one('shipment.dispatch','Remarks'),
        'remarks_date': fields.date('Remarks Date'),
        'remarks_reason': fields.char('Reason'),
    }




class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns={
            'dispatch_button_invisible': fields.boolean('Dispatch Button Invisible'),
    }

    def _get_partner_to_invoice(self, cr, uid, picking, context=None):
        """ Gets the partner that will be invoiced
            Note that this function is inherited in the sale and purchase modules
            @param picking: object of the picking for which we are selecting the partner to invoice
            @return: object of the partner to invoice
        """
        return picking.partner_id and picking.partner_id.id

    def _dispatch_line_hook(self, cr, uid, move_line, dispatch_line_id):
        '''Call after the creation of the invoice line'''
        return

    def _dispatch_hook(self, cr, uid, picking, dispatch_id):
        '''Call after the creation of the invoice'''
        return
       

    def _prepare_dispatch_lines(self, cr, uid, picking, move_line, dispatch_order_id,
        dispatch_vals, context=None):

        return {
            'dispatch_order_id': dispatch_order_id,
            'product_id': move_line.product_id.id,
            'product_qty': move_line.product_qty,
            'product_uom':move_line.product_uom.id,
            'warehouse':move_line.delivery_warehouse_id.id
        }

    def _prepare_dispatch(self, cr, uid, picking, partner, context=None):
        print picking, 'pickinggggggg'
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        x = self.pool.get('stock.picking.out').browse(cr, uid, picking)
        form_id = picking.id
        
        print form_id, 'form_id'
        # cust_name = int(x.partner_id)
        name_do = str(picking.name)
        print name_do, 'name_do'
        origin = picking.origin
        print origin , 'originnnnnn'
        shipping_street = picking.shipping_street
        shipping_street2 = picking.shipping_street2
        shipping_destination = picking.shipping_destination
        shipping_city_id = picking.shipping_city.id
        print shipping_street, shipping_city_id, 'shipping_city  jhkjhk'
        # print form_id, cust_name, 'delivery order name'
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        sale_obj = self.pool.get('sale.order')
        stock_move_obj = self.pool.get('stock.move')
        search_inv = inv_obj.search(cr,uid,[('delivery_note','=',name_do)])
        print search_inv, 'searchhhhhhh'
        search_sale = sale_obj.search(cr,uid,[('name','=',origin)])
        saleid = False
        # inv_id = False
        # inv_date = False
        for s in sale_obj.browse(cr,uid,search_sale):
            saleid = int(s.id)
        i = inv_obj.browse(cr,uid,search_inv[0])
        inv_id = i.id
        inv_date = str(i.date_invoice)
        print inv_id, inv_date, 'ddddddddd'

        dispatch_vals = {
            'do_no': picking.id,
            'so_no': saleid,
            'customer': partner.id,   
            'invoice_no': search_inv[0],
            'invoice_date': inv_date, 
            'shipping_street': shipping_street,
            'shipping_street2': shipping_street2,
            'shipping_destination': shipping_destination, 
            'shipping_city2': shipping_city_id,
            'shipping_state_id': picking.shipping_state_id.id,
            'shipping_zip': picking.shipping_zip,
            'shipping_country_id': picking.shipping_country_id.id,
            'courier_name': picking.dispatch_source.id,
            'shipping_contact_person': picking.shipping_contact_person.id,
            'shipping_contact_mobile_no': picking.shipping_contact_mobile_no,
            'shipping_contact_landline_no': picking.shipping_contact_landline_no,
            'shipping_email_id': picking.shipping_email_id,
            'po_attachment': picking.po_attachment,
        }

        return dispatch_vals

    

    def delivery_order_to_dispatch1(self, cr, uid, ids, context=None):
            
        if context is None:
            context = {}
        invoice_obj = self.pool.get('shipment.dispatch')
        invoice_line_obj = self.pool.get('dispatch.order.line')
        partner_obj = self.pool.get('res.partner')
        # invoices_group = {}
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            main_form_id = picking.id
            partner = self._get_partner_to_invoice(cr, uid, picking, context=context)
            if isinstance(partner, int):
                partner = partner_obj.browse(cr, uid, [partner], context=context)[0]
            if not partner:
                raise osv.except_osv(_('Error, no partner!'),
                    _('Please put a partner on the picking list if you want to generate dispatch order.'))

            invoice_vals = self._prepare_dispatch(cr, uid, picking, partner, context=context)
            invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
            res[picking.id] = invoice_id
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                if move_line.scrapped:
                    continue
                vals = self._prepare_dispatch_lines(cr, uid, picking, move_line,
                                invoice_id, invoice_vals, context=context)
                if vals:
                    invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
                    self._dispatch_line_hook(cr, uid, move_line, invoice_line_id)
                self._dispatch_hook(cr, uid, picking, invoice_id)
            self.write(cr,uid,main_form_id,{'dispatch_button_invisible': True})
            return self.open_dispatch( cr, uid, ids, invoice_id, context=context)


    
    def open_dispatch(self, cr, uid, ids, shipment_ids, context=None):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'zeeva_ind_dispatch_process', 'dispatch_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'zeeva_ind_dispatch_process', 'dispatch_tree_view')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Dispatch'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'shipment.dispatch',
            'res_id': shipment_ids,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            # 'context': "{'type': 'out_invoice'}",
            'type': 'ir.actions.act_window',
        }

stock_picking_out()

class account_invoice(osv.osv):
    _inherit = ['account.invoice','mail.thread']
    _name = 'account.invoice'

    def _get_shipping_person(self, cr, uid, context=None):
        search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Shipping & Distribution')])
        print search_dept, 'shipping department iddddd'
        search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
        print search_emp_in_shipping, 'employee idddd'
        for x in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
            userID = x.user_id.id
        return userID

    def _get_user_name(self, cr, uid, *args):
        user_obj = self.pool.get('res.users')
        user_value = user_obj.browse(cr, uid, uid)
        print user_value.id,'iddd'
        return user_value.name or False


    _columns = {
        'do_id':fields.char('Do ID'),
        'shipping_person': fields.many2one('res.users','Shipping Person'),
        'current_user':fields.many2one('res.users','Current User',size=32),
        'current_url':fields.char('URL'),
        'current_date_time':fields.char('Date Time'),
    }

    _defaults = {
        'shipping_person': _get_shipping_person,
        'current_user': lambda obj, cr, uid, ctx=None: uid,
    }


    def invoice_to_dispatch(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the dispatch template message loaded by default
        '''
        print uid, 'UID'
        self.write(cr,uid,ids,{'current_user': uid})
        search_usr =  self.pool.get('res.users').search(cr,uid,[('id','=',uid)])
        print search_usr, 'search user'
        p = self.browse(cr,uid,ids[0])
        delivery_note = p.delivery_note
        po_attachment = p.po_attachment
        road_permit = p.road_permit_attachment
        l = []
        if delivery_note:
            l = self.pool.get('stock.picking.out').search(cr,uid,[('name','=',delivery_note)])
            print l[0]
        for x in self.pool.get('res.users').browse(cr,uid,search_usr):
            nm = x.name
            print nm, 'name'
        search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Shipping & Distribution')])
        print search_dept, 'shipping department iddddd'
        search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
        print search_emp_in_shipping, 'employee idddd'
        for x in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
            userID = x.user_id.id
            user_email = x.user_id.email
            print userID, user_email, 'user ID of shipping employee'
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        print base_url ,'baseee urlll'
        query = {'db': cr.dbname}
        templ_id = ir_model_data.get_object_reference(cr, uid, 'stock', 'action_picking_tree')[1]
        print templ_id, 'menu iddd'
        url=base_url+"?db=%s#id=%s&view_type=form&model=stock.picking.out&action=%s"%(cr.dbname,l[0],templ_id)
        print url, 'main url'
        self.write(cr,uid,ids,{'current_url': url,'do_id':l[0]})


        ###########################
        import datetime
        current_dt_time = datetime.datetime.now()
        split_time = str(current_dt_time).split(' ')
        # print datetime.strptime(str(current_dt_time).split(' ')[0] ,"%Y-%m-%d").strftime("%d/%m/%Y"), 'letsss try'

        print split_time, 'split listt'
        print 'current_dt_time', current_dt_time

        #################################
        from datetime import date
        from datetime import datetime
        from datetime import timedelta
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Asia/Kolkata')

        utc = datetime.strptime(str(current_dt_time), '%Y-%m-%d %H:%M:%S.%f')
        utc = utc.replace(tzinfo=from_zone)

        # Convert time zone
        central = utc.astimezone(to_zone)
        central = str(central)
        central_split = central.split('+')
        central_split1 = central_split[0].split(' ') 
        central_date = central_split1[0]
        central_time = central_split1[1]
        print central_time[:2], central_time[3:5], 'central timeeee'
        central_date = datetime.strptime(central_date ,"%Y-%m-%d").strftime("%d/%m/%Y")
        date_time_field = str(central_date) + " " + str(central_time)
        today = datetime.today().date()
        date_after_today = today + timedelta(days=1)
        date_after_today = datetime.strptime(str(date_after_today) ,"%Y-%m-%d").strftime("%d/%m/%Y")
        tom_day = ''
        if int(central_time[:2]) > int(14) and int(central_time[3:5]) > int(00):
            print 'time is greater'
            tom_day = "tomorrow i.e. " + str(date_after_today)
        else:
            tom_day = "today i.e. " + str(central_date)
        print date_time_field, 'current_dt_time'
        
        
        self.write(cr,uid,ids,{'current_url': url,'do_id':l[0],'current_date_time':tom_day})
        email_obj = self.pool.get('email.template')  
        #get the object corresponding to template_id
        
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_ind_dispatch_process', 'dispatch_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        print compose_form_id, 'compose_form_id'
        ctx = dict(context)
        email = email_obj.browse(cr, uid, template_id)
        attachment_obj = self.pool.get('ir.attachment')
        attch = attachment_obj.search(cr,uid,[('res_id','=',ids[0]),('res_model','=','account.invoice')])
        print attch, 'attchhh'
        for record in self.browse(cr, uid, ids, context=context):
            ir_actions_report = self.pool.get('ir.actions.report.xml')
            matching_reports = ir_actions_report.search(cr, uid, [('name','=','Delivery Slip')])
            matching_reports1 = ir_actions_report.search(cr, uid, [('name','=','Invoices')])
            print matching_reports, 'matching reporttttttttsss'
            if matching_reports:
                report = ir_actions_report.browse(cr, uid, matching_reports[0])
                print report, 'Report'
                report_service = 'report.' + report.report_name
                print report_service, 'rrrrrr'
                service = netsvc.LocalService(report_service)
                print service, 'sssssssss'
                print report.id
                (result, format) = service.create(cr, uid, l, {'model': 'mail.compose.message'}, context=context)
                eval_context = {'time': time, 'object': record}
                
                    # no auto-saving of report as attachment, need to do it manually
                result = base64.b64encode(result)
                file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', 'Delivery Order')
                file_name += ".pdf"
                print file_name
                attachment_id = attachment_obj.create(cr, uid,
                    {
                        'name': file_name,
                        'datas': result,
                        'datas_fname': file_name,
                        'res_model': 'stock.picking.out',
                        'res_id': l[0],
                        'type': 'binary'
                    }, context=context)
                print attachment_id, 'attachment_id'
                email_obj.write(cr, uid, template_id, {'attachment_ids': [(6,0,[attachment_id])]})
            if matching_reports1:
                report = ir_actions_report.browse(cr, uid, matching_reports1[0])
                print report, 'Report'
                report_service = 'report.' + report.report_name
                print report_service, 'rrrrrr'
                service = netsvc.LocalService(report_service)
                print service, 'sssssssss'
                print report.id
                (result, format) = service.create(cr, uid, ids, {'model': self._name}, context=context)
                eval_context = {'time': time, 'object': record}
                
                    # no auto-saving of report as attachment, need to do it manually
                result = base64.b64encode(result)
                file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', 'Tax Invoice')
                file_name += ".pdf"
                print file_name
                attachment_id1 = attachment_obj.create(cr, uid,
                    {
                        'name': file_name,
                        'datas': result,
                        'datas_fname': file_name,
                        'res_model': 'account.invoice',
                        'res_id': ids[0],
                        'type': 'binary'
                    }, context=context)
                print attachment_id1, 'attachment_id'
                result = base64.b64decode(po_attachment)
                eval_context = {'time': time, 'object': record}
            
                # no auto-saving of report as attachment, need to do it manually
                result = base64.b64encode(result)
                file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', 'Purchase Order')
                file_name += ".pdf"
                print file_name
                attachment_id3 = attachment_obj.create(cr, uid,
                    {
                    'name': file_name,
                    'datas': result,
                    'datas_fname': file_name,
                    'res_model': 'account.invoice',
                    'res_id': ids[0],
                    'type': 'binary'
                    }, context=context)
                print attachment_id3, 'attachment_id'
                if p.partner_id.road_permit:
                    result = base64.b64decode(road_permit)
                    eval_context = {'time': time, 'object': record}
                    # no auto-saving of report as attachment, need to do it manually
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', 'Road Permit')
                    file_name += ".pdf"
                    print file_name
                    attachment_id2 = attachment_obj.create(cr, uid,
                        {
                        'name': file_name,
                        'datas': result,
                        'datas_fname': file_name,
                        'res_model': 'account.invoice',
                        'res_id': ids[0],
                        'type': 'binary'
                        }, context=context)
                        
                    email_obj.write(cr, uid, template_id, {'attachment_ids': [(6,0,[attachment_id,attachment_id1,attachment_id2,attachment_id3])]})
                else:
                    email_obj.write(cr, uid, template_id, {'attachment_ids': [(6,0,[attachment_id,attachment_id1,attachment_id3])]})
            
        ctx.update({
            'default_model': 'account.invoice',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_partner_ids': int(userID),
            'default_current_user': str(nm),
            'default_current_url': str(url),
            'default_delivery_order_no': l[0],
            # 'default_road_permit_attachment': road_permit_attach
        })
        print ctx, 'context'
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'attachment_ids': [(6,0,[attachment_id])],
            'target': 'new',
            'context': ctx,
        }

class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'

    def send_mail(self, cr, uid, ids, context=None):
        context = context or {}
        stock_picking_obj = self.pool.get('stock.picking.out')
        do_id = context.get('default_delivery_order_no')
        print "dddddddddddddddddddddddddddddddddddd",do_id
        stock_picking_obj.write(cr,uid,do_id,{'state':'ready_to_dispatch'})
        if context.get('default_model') == 'account.invoice' and context.get('default_res_id') and context.get('mark_invoice_as_sent'):
            context = dict(context, mail_post_autofollow=True)
            self.pool.get('account.invoice').write(cr, uid, [context['default_res_id']], {'sent': True}, context=context)
        return super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)

class reason_refusal(osv.osv):
    _name = "reason.refusal"
    _description = "Reason for Refusal"
    

    _columns = {

        'name':fields.char('Description'),
        'refusal_reason':fields.text('Reason for Refusal'),
        
        }

reason_refusal()


