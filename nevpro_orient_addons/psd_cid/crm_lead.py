from osv import osv,fields
from datetime import datetime

class crm_lead(osv.osv):
	_inherit = 'crm.lead'

	_columns = {
	    'inquiry_no': fields.char('Enquiry No',size=100,select=True,readonly=True),
		'type_request':fields.selection([('type_request','Request Type'),
										 ('complaint_request','Complaint Request'),
										 ('renewal_request','Renewal Request'),
										 ('information_request','Miscellaneous Request'),
										 ('new_cust','New Customer Request'),
										 ('lead_request','Existing Customer Request'),
										 ('product_request_psd','Product Request'),
										 ('complaint_request_psd','Complaint Request'),
										 ('information_request_psd','Information Request'),
										 ],
										'Request Type',select=1),
		'product_request_id': fields.many2one('product.request'),
		'complaint_request_id': fields.many2one('product.complaint.request'),
		'information_request_id': fields.many2one('product.information.request'),
	}

	def show_details(self,cr,uid,ids,context=None):
		models_data=self.pool.get('ir.model.data')
		rec = self.browse(cr, uid, ids[0])
		context.update({'hide_create_quotation':True})
		if rec.type_request == 'product_request_psd':
			form_view = models_data.get_object_reference(cr,uid,'psd_cid','view_product_request_form_crm')
			return {
			'type':'ir.actions.act_window',
			'name': 'Product Request',
			'view_type':'form',
			'view_mode':'form',
			'res_model':'product.request',
			'view_id':form_view[1],
			'res_id': rec.product_request_id.id,
			'target':'current',
			'context': context
			}
		elif rec.type_request == 'complaint_request_psd':
			form_view = models_data.get_object_reference(cr,uid,'psd_cid','complaint_request_form_psd')
			return {
			'type':'ir.actions.act_window',
			'name': 'Complaint Request',
			'view_type':'form',
			'view_mode':'form',
			'res_model':'product.complaint.request',
			'view_id':form_view[1],
			'res_id': rec.complaint_request_id.id,
			'target':'current',
			'context': context
			}
		elif rec.type_request == 'information_request_psd':
			form_view = models_data.get_object_reference(cr,uid,'psd_cid','view_info_request_form_crm')
			return {
			'type':'ir.actions.act_window',
			'name': 'Information Request',
			'view_type':'form',
			'view_mode':'form',
			'res_model':'product.information.request',
			'view_id':form_view[1],
			'res_id': rec.information_request_id.id,
			'target':'current',
			'context': context
			}
		else:
			return super(crm_lead, self).show_details(cr, uid, ids, context=context)
			# for each in self.browse(cr,uid,ids):
			# 		form_view=models_data.get_object_reference(cr, uid, 'sale', 'view_order_form')
			# 		tree_view=models_data.get_object_reference(cr, uid, 'sale', 'view_order_tree')
			# 		return {
			# 			'type': 'ir.actions.act_window',
			# 			'name': 'Order Management(SC-05)', 
			# 			'view_type': 'form',
			# 			'view_mode': 'form',
			# 			'res_model': self._name,
			# 			'res_id':ids[0],
			# 			'views': [(form_view and form_view[1] or False, 'form'),
			# 					 (tree_view and tree_view[1] or False, 'tree'),
			# 					(False, 'calendar'), (False, 'graph')],
			# 			'target': 'current',
			# 		}

crm_lead()
