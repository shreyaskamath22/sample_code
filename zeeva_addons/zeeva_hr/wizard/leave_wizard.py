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
from openerp import netsvc
import time
from datetime import datetime
import datetime

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




class leave_request_wizard(osv.TransientModel):
    _name = "leave.request.wizard"
    _inherit = ['mail.thread']
    _description = "Leave Request Wizard"
    

    def action_confirm(self, cr, uid, ids, context=None):
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'hr.holidays', ids[0], 'order_confirm', cr)
        
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_hr', 'edit_holiday_new')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        
        ctx = dict(context)
        
        
        ctx.update({
            'default_model': 'hr.holidays',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_urgent_request_sent': True
        })
        
        print ctx
        print template_id
        print compose_form_id
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(leave_request_wizard, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        task_pool = self.pool.get('hr.holidays')
        task = task_pool.browse(cr, uid, record_id, context=context)
        

        if 'form_number' in fields:
            res['form_number'] = task.id

leave_request_wizard()

class maternity_leave_request_wizard(osv.TransientModel):
    _name = "maternity.leave.request.wizard"
    _inherit = ['mail.thread']
    _description = "Maternity Leave Request Wizard"
    

    def action_confirm(self, cr, uid, ids, context=None):
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'hr.holidays', ids[0], 'order_confirm', cr)
        
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_hr', 'edit_holiday_new')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        
        ctx = dict(context)
        
        
        ctx.update({
            'default_model': 'hr.holidays',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_urgent_request_sent': True
        })
        
        print ctx
        print template_id
        print compose_form_id
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

maternity_leave_request_wizard()

class wedding_leave_request_wizard(osv.TransientModel):
    _name = "wedding.leave.request.wizard"
    _inherit = ['mail.thread']
    _description = "Wedding Leave Request Wizard"
    
    def action_confirm(self, cr, uid, ids, context=None):
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'hr.holidays', ids[0], 'order_confirm', cr)
        
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_hr', 'edit_holiday_new')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        
        ctx = dict(context)
        
        
        ctx.update({
            'default_model': 'hr.holidays',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_urgent_request_sent': True
        })
        
        print ctx
        print template_id
        print compose_form_id
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

wedding_leave_request_wizard()

class casual_leave_request_wizard(osv.TransientModel):
    _name = "casual.leave.request.wizard"
    _inherit = ['mail.thread']
    _description = "Casual Leave Request Wizard"
    

    def action_confirm(self, cr, uid, ids, context=None):
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'hr.holidays', ids[0], 'order_confirm', cr)
        
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_hr', 'edit_holiday_new')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        
        ctx = dict(context)
        
        
        ctx.update({
            'default_model': 'hr.holidays',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_urgent_request_sent': True
        })
        
        print ctx
        print template_id
        print compose_form_id
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        
        

casual_leave_request_wizard()

class compensatory_leave_request_wizard(osv.TransientModel):
    _name = "compensatory.leave.request.wizard"
    _inherit = ['mail.thread']
    _description = "Compensatory-Off Leave Request Wizard"
    

    def action_confirm(self, cr, uid, ids, context=None):
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'hr.holidays', ids[0], 'order_confirm', cr)
        
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_hr', 'edit_holiday_new')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        
        ctx = dict(context)
        
        
        ctx.update({
            'default_model': 'hr.holidays',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_urgent_request_sent': True
        })
        
        print ctx
        print template_id
        print compose_form_id
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

compensatory_leave_request_wizard()

class paternity_leave_request_wizard(osv.TransientModel):
    _name = "paternity.leave.request.wizard"
    _inherit = ['mail.thread']
    _description = "Paternity Leave Request Wizard"
    

    def action_confirm(self, cr, uid, ids, context=None):
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'hr.holidays', ids[0], 'order_confirm', cr)
        
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_hr', 'edit_holiday_new')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        
        ctx = dict(context)
        
        
        ctx.update({
            'default_model': 'hr.holidays',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_urgent_request_sent': True
        })
        
        print ctx
        print template_id
        print compose_form_id
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

paternity_leave_request_wizard()


class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'

    def send_mail(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get('default_model') == 'hr.holidays' and context.get('default_res_id') and context.get('mark_urgent_request_sent'):
            context = dict(context, mail_post_autofollow=True)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'hr.holidays', context['default_res_id'], 'request_sent', cr)
        return super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

