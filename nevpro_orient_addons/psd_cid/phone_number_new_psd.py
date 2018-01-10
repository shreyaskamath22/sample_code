from osv import osv,fields
from tools.translate import _

class phone_number_new_psd(osv.osv):
	_name = 'phone.number.new.psd'
	_rec_name = 'number'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'phone_pop_id':fields.many2one('phone.number.pop.up.psd','Phone pop-up'),
		'phone_product_request_id':fields.many2one('product.request','Product Request'),
		'complaint_request_id':fields.many2one('product.complaint.request','Complaint Request'),
		'information_request_id':fields.many2one('product.information.request','Information Request'),
		'number':fields.char('Number',size=10),
		'type':fields.selection([
								('mobile','Mobile'),
								('landline','Landline'),
								],'Type'),
	}

	_defaults = {
		'company_id': _get_company
	}	
phone_number_new_psd()
	
class phone_number(osv.osv):
	_inherit = 'phone.number'

	def save_record(self,cr,uid,ids,context=None):
		res_id = False
		active_id = context.get('active_ids')
		request_type = context.get('request_type')
		phone_obj = self.pool.get('phone.number.child')
		phone_m2m_obj = self.pool.get('phone.m2m')
		pro_loc_obj = self.pool.get('product.location.customer.search')
		info_req_obj = self.pool.get('product.information.request')
		rec = self.browse(cr, uid, ids[0])
		phone_number_ids = rec.phone_number_one2many
		if request_type == 'partner':
			if context.has_key('pro_loc_adtn_id'):
				res_id = context.get('pro_loc_adtn_id') 
				pro_loc_data = pro_loc_obj.browse(cr, uid, res_id)
				if pro_loc_data.location_attribute == 'add':
					pro_loc_obj.write(cr, uid, [res_id], {'phone':phone_number_ids[0].id}, context=context)
			if context.has_key('partner_id'):
				partner_id = context.get('partner_id')
				partner_address_id = self.pool.get('res.partner.address').search(cr,uid,[('primary_contact','=',True),('partner_id','=',partner_id)])
			for each in phone_number_ids:
				phone_obj.write(cr, uid, each.id, {
					'partner_id': partner_id,
					'contact_select': each.contact_select,
					'number': each.number
				},context=context)
				phone_m2m_obj.create(cr, uid, {
					'name': each.number,
					'res_location_id': partner_address_id[0],
					'type': each.contact_select
				}, context=context)
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
		elif request_type == 'information':
			partner_id = info_req_obj.browse(cr, uid, active_id[0]).partner_id.id
			for each in rec.phone_number_one2many:
				phone_obj.write(cr, uid, each.id, {
					'partner_id': partner_id,
					'contact_select': each.contact_select,
					'number': each.number
				},context=context)
				info_req_obj.write(cr, uid,  active_id[0], {'phone_many2one':rec.phone_number_one2many[0].id}, context=context)
			return {'type': 'ir.actions.act_window_close'}
		else:
			return super(phone_number, self).save_record(cr, uid, ids, context=context)


	def cancel_record(self,cr,uid,ids,context=None):
		res_id = False
		request_type = context.get('request_type')
		if request_type == 'partner':
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
		else:
			return super(phone_number, self).cancel_record(cr, uid, ids, context=context)	

phone_number()
