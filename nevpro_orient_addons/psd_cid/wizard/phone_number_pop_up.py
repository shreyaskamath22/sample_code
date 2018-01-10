from osv import osv,fields
from openerp.tools.translate import _
import curses.ascii

class phone_number_pop_up_psd(osv.osv):
    _name = 'phone.number.pop.up.psd'

    _columns = {
        'phone_number_ids': fields.one2many('phone.number.new.psd', 'phone_pop_id', 'Phone Number'), 
    }

    def save_phone_number(self,cr,uid,ids,context=None): 
        res_id = False
        request_type = False
        active_id = context.get('active_ids')
        request_type = context.get('request_type')
        phone_obj = self.pool.get('phone.number.new.psd')
        pro_loc_obj = self.pool.get('product.location.customer.search')
        phone_list = []
        results = []
        rec = self.browse(cr, uid, ids[0])
        phone_number_ids = rec.phone_number_ids
        for each in phone_number_ids:
            length = len(each.number)
            if each.type=='mobile':
                if length < 10 or length > 10:
                    raise osv.except_osv(('Alert!'),('Please enter 10 digits phone number.'))
            for xx in str(each.number):
                results.append(curses.ascii.isdigit(xx))
            for result in results:
                if result == False:
                    raise osv.except_osv(('Alert!'),('Please enter valid phone number'))
        if request_type == 'product_location':
            if context.has_key('pro_loc_adtn_id'):
                res_id = context.get('pro_loc_adtn_id') 
                pro_loc_data = pro_loc_obj.browse(cr, uid, res_id)
                if pro_loc_data.location_attribute == 'add':
                    pro_loc_obj.write(cr, uid, [res_id], {'phone_new':phone_number_ids[0].id}, context=context)
            for each in phone_number_ids:
                phone_list.append(int(each.id))
                phone_obj.write(cr, uid, each.id, {'phone_product_request_id':active_id[0]} ,context=context)
                if pro_loc_data.partner_id:
                    pro_loc_obj.write(cr,uid,res_id,{'phone':phone_list[0]})
                else:
                    pro_loc_obj.write(cr,uid,res_id,{'phone_new':phone_list[0]})
            return {
                'name': _('New Cutomer Location'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'product.location.customer.search',
                'res_id': res_id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': context,                               
            }  
        elif request_type == 'complaint_location':
            if context.has_key('comp_loc_adtn_id'):
                res_id = context.get('comp_loc_adtn_id')
            for each in phone_number_ids:
                phone_list.append(int(each.id))
                phone_obj.write(cr, uid, each.id, {'complaint_request_id': active_id[0]} ,context=context)
                self.pool.get('complaint.location.addition').write(cr,uid,res_id,{'phone':phone_list[0]})
            return {
                'name': _('New Cutomer Location'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'complaint.location.addition',
                'res_id': res_id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': context,                               
            }  
        elif request_type == 'product':
            for each in phone_number_ids:
                phone_list.append(int(each.id))
                phone_obj.write(cr, uid, each.id, {'phone_product_request_id': active_id[0]} ,context=context)
                self.pool.get('product.request').write(cr,uid,active_id[0],{'phone_many2one_new':phone_list[0]})
            return {'type': 'ir.actions.act_window_close'}
        elif request_type == 'information':
            for each in phone_number_ids:
                phone_list.append(int(each.id))
                phone_obj.write(cr, uid, each.id, {'information_request_id': active_id[0]} ,context=context)
                self.pool.get('product.information.request').write(cr,uid,active_id[0],{'phone_many2one_new':phone_list[0]})
            return {'type': 'ir.actions.act_window_close'}

    def phone_cancel(self, cr, uid, ids, context=None):
        res_id = False
        request_type = context.get('request_type')
        if request_type == 'product_location':
            if context.has_key('pro_loc_adtn_id'):
                res_id = context.get('pro_loc_adtn_id') 
                return {
                    'name': _('New Cutomer Location'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_model': 'product.location.customer.search',
                    'res_id': res_id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'context': context,
                } 
        elif request_type == 'complaint_location':
            if context.has_key('comp_loc_adtn_id'):
                res_id = context.get('comp_loc_adtn_id')
                return {
                    'name': _('New Cutomer Location'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_model': 'complaint.location.addition',
                    'res_id': res_id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'context': context,                               
                } 
        else:
            return {'type': 'ir.actions.act_window_close'}
       

phone_number_pop_up_psd()
