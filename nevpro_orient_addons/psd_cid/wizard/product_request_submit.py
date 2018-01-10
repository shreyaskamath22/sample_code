from osv import osv,fields
from datetime import datetime
from openerp.tools.translate import _

class product_request_submit(osv.osv_memory):
	_name = 'product.request.submit'
	
	def action_confirm(self,cr,uid,ids,context=None):
		res_id = False
		if context is None: context = {}
		active_ids = context.get('active_ids')
		product_req_obj = self.pool.get('product.request')
		product_request_data = product_req_obj.browse(cr, uid, active_ids[0])
		if product_request_data.customer_type == 'existing':
			res_id = product_req_obj.process_existing_customer_request(cr,uid,active_ids,context=context)
			return res_id
		else:
			res_id = product_req_obj.process_new_customer_request(cr,uid,active_ids,context=context)
			return res_id

	def action_cancel(self,cr,uid,ids,context=None):
		return {
	           'type': 'ir.actions.act_window_close'
	           }

product_request_submit()