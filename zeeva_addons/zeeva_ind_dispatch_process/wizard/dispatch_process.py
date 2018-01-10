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

from openerp import addons
import logging
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import netsvc, SUPERUSER_ID
import time
from datetime import datetime
import datetime
from openerp.tools.float_utils import float_compare
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _

import base64
import logging

from openerp import netsvc
from openerp.osv import osv, fields
from openerp.osv import fields
from openerp import tools
from openerp.tools.translate import _
from urllib import urlencode, quote as quote

from openerp.osv import fields, osv


class dispatch_process_wizard(osv.TransientModel):
    _name = "dispatch.process.wizard"
    _description = "Dispatch Process Wizard"
    

    def action_confirm(self, cr, uid, ids, context=None):
        print ids, 'idddddddddddddss'
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'shipment.dispatch', ids[0], 'order_confirm', cr)

        
        x = self.pool.get('stock.picking.out').browse(cr, uid, ids[0])
        form_id = int(x.id)
        cust_name = int(x.partner_id)
        name_do = str(x.name)
        origin = x.origin
        print form_id, cust_name, 'delivery order name'
        inv_obj = self.pool.get('account.invoice')
        sale_obj = self.pool.get('sale.order')
        search_inv = inv_obj.search(cr,uid,[('origin','=',origin)])
        search_sale = sale_obj.search(cr,uid,[('name','=',origin)])

        sale_id = False
        inv_id = False
        inv_date = False
        for s in sale_obj.browse(cr,uid,search_sale):
            sale_id = int(s.id)
        for i in inv_obj.browse(cr,uid,search_inv):
            inv_id = int(i.id)
            inv_date = str(i.date_invoice)
        search_shipment_dispatch = self.pool.get('shipment.dispatch').search(cr, uid, [('invoice_no', '=', inv_id)], context=context)
        if search_shipment_dispatch:
            print search_shipment_dispatch, 'in the if loop'
        if not ids: return False
        if not isinstance(ids, list): ids = [ids]
        ir_model_data = self.pool.get('ir.model.data')        
        view_ref = ir_model_data.get_object_reference(cr, uid, 'zeeva_ind_dispatch_process', 'dispatch_form')
        view_id = view_ref and view_ref[1] or False,
        if search_shipment_dispatch:
            context.update({
                'default_do_no': form_id,
                'default_so_no': sale_id,
                'default_customer': cust_name,   
                'default_invoice_no': inv_id,
                'default_invoice_date': inv_date,
                'default_flag': True             
                })

            print context, 'context'
            
            return {
               'type': 'ir.actions.act_window',
               'name': 'Dispatch Details',
               'context':context,
               'view_mode': 'form',
               'view_type': 'form',
               'view_id': view_id,
               'res_model': 'shipment.dispatch',
               }

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(dispatch_process_wizard, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        task_pool = self.pool.get('shipment.dispatch')
        task = task_pool.browse(cr, uid, record_id, context=context)
        

        if 'form_number' in fields:
            res['form_number'] = task.id

            
dispatch_process_wizard()


class dispatch_process_wizard1(osv.TransientModel):
    _name = "dispatch.process.wizard1"
    _description = "Dispatch Process Wizard1"
    

    def action_confirm(self, cr, uid, ids, context=None):
        print ids, 'idddddddddddddss'
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'shipment.dispatch', ids[0], 'order_confirm', cr)
        if not ids: return False
        if not isinstance(ids, list): ids = [ids]
        ir_model_data = self.pool.get('ir.model.data')        
        view_ref = ir_model_data.get_object_reference(cr, uid, 'zeeva_ind_dispatch_process', 'dispatch_form')
        view_id = view_ref and view_ref[1] or False,
        # search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Sales & Marketing Support')])
        # print search_dept, 'shipping department iddddd'
        # search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
        # print search_emp_in_shipping, 'employee idddd'
        # user_list = []
        # try:
        #     compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        # except ValueError:
        #     compose_form_id = False 
        # for x in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
        #     userID = x.user_id.id
        #     user_list.append(userID)
        # self.message_subscribe_users(cr, SUPERUSER_ID, ids, user_ids=user_list, context=context)
        # message = _("Dispatch Process is in transit")
        # self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)

        self.pool.get('shipment.dispatch').write(cr,uid,ids,{'flag1':True})
        ctx = dict(context)
        ctx.update({
            'default_model': 'shipment.dispatch',
            'default_res_id': ids,
        })
        
        print ctx
        
        return {
            'type': 'ir.actions.act_window_close',
            'context': ctx,
        }
        
        

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(dispatch_process_wizard1, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        task_pool = self.pool.get('shipment.dispatch')
        task = task_pool.browse(cr, uid, record_id, context=context)
        

        if 'form_number' in fields:
            res['form_number'] = task.id

            
dispatch_process_wizard1()


class dispatch_partial_picking_line(osv.TransientModel):


    _name = "dispatch.partial.picking.line"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True, ondelete='CASCADE'),
        'quantity' : fields.float("Shipped Quantity"),
        'wizard_id' : fields.many2one('dispatch.partial.picking', string="Wizard", ondelete='CASCADE'),
        'line_disp_id' : fields.many2one('dispatch.order.line','disp_line' , ondelete='CASCADE'),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True),
        'prodlot_id' : fields.many2one('stock.production.lot', 'Serial Number', ondelete='CASCADE'),
    }

    _defaults = {

        'quantity':1,
    }

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        uom_id = False
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            uom_id = product.uom_id.id
        return {'value': {'product_uom': uom_id}}
    


class dispatch_partial_picking(osv.osv_memory):
    _name = "dispatch.partial.picking"
    _description = "Partial Picking Processing Wizard"
    _inherit = "mail.thread"

    _columns = {
        'dispatch_move_ids' : fields.one2many('dispatch.partial.picking.line', 'wizard_id', 'Product Moves'),
        'dispatch_id': fields.many2one('shipment.dispatch', 'Dispatch', required=True),
        'partial_picking': fields.boolean('Partial Dispatch'),
        'partial_date': fields.date('Partial Dispatch Date'),
     }

    def onchange_partial_picking(self,cr,uid,ids,partial_picking,partial_date):
        v={}
        if partial_picking == False:
            v['partial_date'] = False
        return {'value':v}

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(dispatch_partial_picking, self).default_get(cr, uid, fields, context=context)
        dispatch_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not dispatch_ids or len(dispatch_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('shipment.dispatch'), 'Bad context propagation'
        dispatch_id, = dispatch_ids
        if 'dispatch_id' in fields:
            res.update(dispatch_id=dispatch_id)
        if 'dispatch_move_ids' in fields:
            dispatch = self.pool.get('shipment.dispatch').browse(cr, uid, dispatch_id, context=context)
            moves = [self._partial_move_for(cr, uid, m) for m in dispatch.dispatch_order_lines]
            res.update(dispatch_move_ids=moves)
        # if 'date' in fields:
        #     res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res


    def _partial_move_for(self, cr, uid, move):
        partial_move = {
            'product_id' : move.product_id.id,
            'quantity' : move.product_qty,
            'product_uom' : move.product_uom.id,
            'line_disp_id' : move.id,
            # 'prodlot_id' : move.prodlot_id.id,
            # 'move_id' : move.id,
            # 'location_id' : move.location_id.id,
            # 'location_dest_id' : move.location_dest_id.id,
        }
        # if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
        #     partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))
        return partial_move


    def do_dispatch_partial(self, cr, uid, ids, context=None):
        from datetime import date
        from datetime import datetime
        if context is None:
            context = {}
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        shipment_dispatch = self.pool.get('shipment.dispatch')
        dispatch_move = self.pool.get('dispatch.order.line')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'partial_date' : partial.partial_date,
            'partial_picking': partial.partial_picking
        }
        
        
        partial_picking_id = partial.dispatch_id.id
        partial_delivery = partial.partial_picking
        partial_date = partial.partial_date
        cr.execute('select count(*) from dispatch_order_line where dispatch_order_id =%s',(partial_picking_id,))
        stock_move_values = map(lambda x: x[0], cr.fetchall())
        stock_move_values_count = stock_move_values[0]
        wizard_move_values_count = len(partial.dispatch_move_ids)

        for wizard_line in partial.dispatch_move_ids:
            print wizard_line.line_disp_id.id, 'wizard lineeee'
            print wizard_line, 'wizard lineeee'
            print wizard_line.quantity, 'quantityyyy'
            line_uom = wizard_line.product_uom
            line_disp_id = wizard_line.line_disp_id.id
            product_move_quantity = wizard_line.line_disp_id.product_qty

        #     #Quantiny must be Positive
            if wizard_line.quantity <= 0.0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

            if wizard_line.quantity > wizard_line.line_disp_id.product_qty:
                raise osv.except_osv(_('Warning!'), _('Shipped Quantities cannot be greater than the original ordered Shipped Quantities.'))

            if partial_date != False:
                pass
            elif product_move_quantity != wizard_line.quantity or stock_move_values_count > wizard_move_values_count:
                raise osv.except_osv(_('Warning!'), _("Since it is a case of Partial Dispatch, please tick the checkbox for 'Partial Dispatch' and enter the Partial Dispatch Date of the backorder."))

        #     #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor <> 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if line_disp_id:
                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.line_disp_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.line_disp_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name =  'shipment.dispatch'
                line_disp_id = dispatch_move.create(cr,uid,{
                                            'product_id': wizard_line.product_id.id,
                                            'product_qty': wizard_line.quantity,
                                            'product_uom': wizard_line.product_uom.id,
                                            },context=context)
                print line_disp_id, 'lineeee disp idddd'
        
            partial_data['move%s' % (line_disp_id)] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
            }
            print partial_data, 'datttttaaa'
        #     if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
        #         partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
        #                                                           product_currency=wizard_line.currency.id)
        # # Do the partial delivery and open the picking that was delivered
        # # We don't need to find which view is required, stock.picking does it.
        print partial.dispatch_id.id,'partial dispatch idddddd'
        done = shipment_dispatch.do_dispatch_partial(
            cr, uid, [partial.dispatch_id.id], partial_data, context=context)
        print done, 'doneeee'
        if done[partial.dispatch_id.id]['delivered_picking'] == partial.dispatch_id.id:
            user_list = []
            search_dept =  self.pool.get('hr.department').search(cr,uid,[('name','=','Sales & Marketing Support')])
            print search_dept, 'shipping department iddddd'
            search_emp_in_shipping = self.pool.get('hr.employee').search(cr,uid,[('department_id','=',search_dept[0])])  
            print search_emp_in_shipping, 'employee idddd'
            search_country_head = self.pool.get('hr.job').search(cr,uid,[('name','=','Country Head For Modern Trade')])
            search_emp_in_country_head = self.pool.get('hr.employee').search(cr,uid,[('job_id','=',search_country_head[0])])  
            for p in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_country_head):
                userID = p.user_id.id
                user_list.append(userID)
            for c in self.pool.get('hr.employee').browse(cr,uid,search_emp_in_shipping):
                userID = c.user_id.id
                user_list.append(userID)

            shipment_dispatch.message_subscribe_users(cr, SUPERUSER_ID, [partial.dispatch_id.id], user_ids=user_list, context=context)
            message = _("<b>Status: Ready to Dispatch --> In Transit</b><br/><br/>The Products in the Invoice %s Sale Order %s Delivery Order %s Dispatch No %s are in Transit and ETA is %s")%(partial.dispatch_id.invoice_no.number,partial.dispatch_id.so_no.name,partial.dispatch_id.do_no.name,partial.dispatch_id.name,str(datetime.strptime(partial.dispatch_id.eta, "%Y-%m-%d").strftime("%d-%m-%Y")))
            # message = _("<b>Status: Ready to Dispatch --> In Transit</b><br/><br/>The Products in the ")
            shipment_dispatch.message_post(cr, uid, [partial.dispatch_id.id], body = message, type='comment', subtype='mt_comment', context = context)
            stock_obj = self.pool.get('stock.picking.out')
            delivery_id = partial.dispatch_id.do_no.id
            stock_obj.write(cr,uid,delivery_id,{'state':'dispatched'})
            shipment_dispatch.write(cr,uid,[partial.dispatch_id.id],{'state':'in transit'})
            return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.act_window',
            'res_model': context.get('active_model', 'shipment.dispatch'),
            'name': _('Partial Dispatch'),
            'res_id': done[partial.dispatch_id.id]['delivered_picking'],
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'context': context,
        }

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
