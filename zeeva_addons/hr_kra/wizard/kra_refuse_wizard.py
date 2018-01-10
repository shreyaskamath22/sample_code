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




class kra_refuse_wizard(osv.TransientModel):
    _name = "kra.refuse.wizard"
    _description = "KRA Refuse Wizard"
    

    def action_confirm(self, cr, uid, ids, context=None):
        print ids, 'idddddddddddddss'
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'request.new.kra', ids[0], 'order_confirm', cr)
        
        ir_model_data = self.pool.get('ir.model.data')
        if not ids: return False
        if not isinstance(ids, list): ids = [ids]
        x = self.browse(cr, uid, ids[0])
        search_valuel = self.pool.get('kra.points').search(cr,uid,[('points_id','=',x.id)])
        for m in self.pool.get('kra.points').browse(cr,uid,search_valuel):
            self.pool.get('kra.points').write(cr,uid,m.id,{'state':'To be Refused'})
        self.pool.get('request.new.kra').write(cr,uid,ids,{'state':'To be Refused'})
        
        view_ref = ir_model_data.get_object_reference(cr, uid, 'hr_kra', 'view_add_kra')
        view_id = view_ref and view_ref[1] or False,
        ctx = dict(context)
        
        
        ctx.update({
            'default_model': 'request.new.kra',
            'default_res_id': ids,
            # 'default_state': 'To be Refused',
            'mark_urgent_request_sent': True
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
        res = super(kra_refuse_wizard, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        task_pool = self.pool.get('request.new.kra')
        task = task_pool.browse(cr, uid, record_id, context=context)
        

        if 'form_number' in fields:
            res['form_number'] = task.id

kra_refuse_wizard()

