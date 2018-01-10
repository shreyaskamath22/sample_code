from osv import osv,fields
from tools.translate import _

class request_search_sales(osv.osv):
	_inherit = "request.search.sales"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id': fields.many2one('res.company','Company ID'),
		'name': fields.char('Customer / Company Name',size=30),
		'product_request_id': fields.many2one('product.request','Request Id'),
		'partner_id': fields.many2one('res.partner','Customer Id'),
		'contact_name_first': fields.char('Contact First Name',size=30),
		'contact_name_last': fields.char('Contact Last Name',size=30),
		'phone': fields.char('Phone',size=16),
		'apartment': fields.char('Unit/Apartment No',size=50),
		'building': fields.char('Building Name',size=50),
		'sub_area': fields.char('Sub Area',size=50),
		'street': fields.char('Street', size=60),
		'city_id': fields.many2one('city.name','City'),
		'from_date': fields.datetime('From Date'),
		'to_date': fields.datetime('To Date'),
		'psd_company_id': fields.many2one('res.company','PSD Office'),
		'pse': fields.many2one('hr.employee','PSE'),
		'state': fields.selection([('new','New'),
						('open','Opened'),
						('progress','Resource Assigned'),
						('closed','Closed'),
						('cancel','Cancelled')
						],'State'), 
		'product_request_ids': fields.one2many('product.request','request_search_sales_id','Product Requests'),
		'pushed': fields.boolean('Pushed?'),
		'select_all': fields.boolean('Select All'),
		'not_found':fields.boolean('not found'),
	}

	_defaults = {
		'company_id': _get_company
	}

	def clear_request_search_sales(self,cr,uid,ids,context=None):
		for k in self.browse(cr,uid,ids):
			self.write(cr,uid, k.id,
				{
					'name':None,
					'product_request_id':False,
					'customer_id':False,
					'contact_name_first':None,
					'contact_name_last':None,
					'location_name':None,
					'location_name':None,
					'phone':None,
					'apartment':None,
					'building':None,
					'sub_area':None,
					'street':None,
					'city_id':False,
					'from_date':False,
					'to_date':False,
					'pse':False,
					'not_found':False,
					'partner_id':None,
				},context=context)	
			for req in k.product_request_ids:
				self.pool.get('product.request').write(cr,uid,req.id,{'request_search_sales_id':None})	
		return True




	def search_product_requests(self,cr,uid,ids,context=None):
		product_request_obj = self.pool.get('product.request')
		res=False
		rec = self.browse(cr, uid, ids[0])
		self.write(cr,uid,ids[0],{'not_found':False,'product_request_ids':[(6, 0, 0)]})
		true_items = []
		domain = []
		product_list = []
		products = False
		all_pro_req_ids = product_request_obj.search(cr, uid, [], context=context)
		product_request_obj.write(cr, uid, all_pro_req_ids, {'select_request': False}, context=context)
		if rec.name:
			true_items.append('name')
		if rec.product_request_id:
			true_items.append('product_request_id')    
		if rec.partner_id:
			true_items.append('partner_id')
		if rec.contact_name_first:
			true_items.append('contact_name_first') 
		if rec.contact_name_last:
			true_items.append('contact_name_last')     
		if rec.phone:
			true_items.append('phone')
		if rec.apartment:
			true_items.append('apartment')
		if rec.building:
			true_items.append('building')
		if rec.sub_area:
			true_items.append('sub_area')
		if rec.street:
			true_items.append('street')
		if rec.city_id:
			true_items.append('city_id')
		if rec.pse:
			true_items.append('pse')
		if rec.from_date and not rec.to_date :
			raise osv.except_osv(("Alert!"),("Please enter 'Date to'!"))
		if not rec.from_date and rec.to_date :
			raise osv.except_osv(("Alert!"),("Please enter 'Date from'!"))			
		for true_item in true_items:
			if true_item == 'name':
				domain.append(('name', 'ilike', rec.name))
			if true_item == 'product_request_id':
				domain.append(('product_request_id', '=', rec.product_request_id.product_request_id))  
			if true_item == 'partner_id':
				domain.append(('customer_id', '=', rec.partner_id.ou_id))
			if true_item == 'contact_name_first':
				domain.append(('first_name', 'ilike', rec.contact_name_first))
			if true_item == 'contact_name_last':			    
				domain.append(('last_name', 'ilike', rec.contact_name_last))    
			if true_item == 'phone':
				domain.append('|')
				domain.append(('phone_many2one.number', 'ilike', rec.phone))
				domain.append(('phone_many2one_new.number', 'ilike', rec.phone))
			if true_item == 'apartment':
				domain.append(('apartment', 'ilike', rec.apartment))  
			if true_item == 'building':
				domain.append(('building', 'ilike', rec.building))
			if true_item == 'sub_area':
				domain.append(('sub_area', 'ilike', rec.sub_area))
			# if true_item == 'landline':
			#     domain.append(('name', 'ilike', rec.landline)) 
			if true_item == 'street':
				domain.append(('street', 'ilike', rec.street))
			if true_item == 'city_id':
				domain.append(('city_id', '=', rec.city_id.id))  
			if true_item == 'pse':
				domain.append(('employee_id', '=', rec.pse.id))  
		if rec.from_date and rec.to_date:		    
			domain.append(('request_date', '>=', rec.from_date+"%"))
			domain.append(('request_date', '<=', rec.to_date+"%"))		    
		domain.append(('state','=','assigned'))
		domain.append(('psd_sales_entry','=',False))
		display_ids = product_request_obj.search(cr, uid, domain, context=context)   
		if display_ids:
			for disp_ids in product_request_obj.browse(cr,uid,display_ids):
				product_list = []
				for line in disp_ids.location_request_line:
					if line.product_name.id:
						if not line.product_name.name in product_list:
							product_list.append(line.product_name.name)
				if product_list:
					products =', '.join(map(str, product_list))
					product_request_obj.write(cr, uid, int(disp_ids.id), {'products': products}, context=context)         
				else:
					product_request_obj.write(cr, uid, int(disp_ids.id), {'products':''}, context=context)         
		if not display_ids:
			self.write(cr,uid,ids[0],{'not_found':True})
			return res
		else:
			res = self.write(cr, uid, ids[0], 
				{
					'product_request_ids': [(6, 0, display_ids)],
					'pushed': False
				},context=context)
			return res		

	def generate_sales_product_quotation(self,cr,uid,ids,context=None):		
		product_req_obj = self.pool.get('product.request')
		search_product_quotation_obj = self.pool.get('search.product.quotation')
		models_data=self.pool.get('ir.model.data')
		product_req_ids = product_req_obj.search(cr, uid, [('select_request','=',True),('psd_sales_entry','=',False)], context=context)
		if not product_req_ids:
			raise osv.except_osv(("Alert!"),("No request selected!")) 
		new_id_list = []
		context.update({'request_from_sale':'request_from_sale'})
		for product_req_id in product_req_ids:
			new_id = product_req_obj.generate_sales_product_quotation(cr, uid, product_req_id, context=context)
			product_req_obj.write(cr, uid, product_req_id, {'select_request': False}, context=context)
			new_id_list.append(int(new_id))
		self.write(cr, uid, ids[0], 
			{
				'product_request_ids': [(6, 0, [])],
				'pushed': True
			},context=context)	
		if len(new_id_list) == 1:
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'view_psd_product_quotation_branch')	
			return {
			   'name':'Product Quotation',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'psd.sales.product.quotation',
			   'res_id': new_id_list[0],
			   'type': 'ir.actions.act_window',
			   'target': 'current',
			   'context':context
			}
		if len(new_id_list) > 1:
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'search_product_quotation_form')
			search_product_quotation_vals = {
				'search_product_quot_lines': [(6, 0, new_id_list)]
			}
			search_product_quotation_id = search_product_quotation_obj.create(cr,uid,search_product_quotation_vals,context=context)
			
			return {
				   'name':'Sales Order-Quotation',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'search.product.quotation',
				   'res_id':int(search_product_quotation_id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   }

	def onchange_select_all_requests(self,cr,uid,ids,select_all,product_request_ids,context=None):
		product_request_obj = self.pool.get('product.request')
		for product_request_id in product_request_ids:
			pro_req_id = product_request_obj.write(cr, uid, product_request_id[1], {'select_request': select_all}, context=context)
		data = {'product_request_ids': product_request_ids}	
		return {'value':data}

	def generate_sales_product_order(self,cr,uid,ids,context=None):		
		product_req_obj = self.pool.get('product.request')
		models_data=self.pool.get('ir.model.data')
		product_req_ids = product_req_obj.search(cr, uid, [('select_request','=',True),('psd_sales_entry','=',False)], context=context)
		if not product_req_ids:
			raise osv.except_osv(("Alert!"),("No request selected!"))
		new_id_list = []
		context.update({'request_from_sale':'request_from_sale'})
		for product_req_id in product_req_ids:
			new_id = product_req_obj.generate_direct_sales_product_order(cr, uid, product_req_id, context=context)
			product_req_obj.write(cr, uid, product_req_id, {'select_request': False}, context=context)
			new_id_list.append(int(new_id))
		self.write(cr, uid, ids[0], 
			{
				'product_request_ids': [(6, 0, [])],
				'pushed': True
			},context=context)
		if len(new_id_list) == 1:
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'view_psd_product_sale_order_branch')	
			return {
			   'name':'Sale Product Order',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'psd.sales.product.order',
			   'res_id': new_id_list[0],
			   'type': 'ir.actions.act_window',
			   'target': 'current',
			   'context':context
			}
		if len(new_id_list) > 1:
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'search_sale_product_order_form')
			search_sale_order_val = {
					'search_sales_product_order_lines': [(6, 0, new_id_list)]
				}
			search_sale_order_obj = self.pool.get('search.sale.product.order')
			search_sale_order_id = search_sale_order_obj.create(cr,uid,search_sale_order_val,context=None)
			
			return {
				   'name':'Sales Order-Product',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'search.sale.product.order',
				   'res_id':int(search_sale_order_id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   }


	def generate_service_quotation(self,cr,uid,ids,context=None):		
		product_req_obj = self.pool.get('product.request')
		search_amc_quotation_obj = self.pool.get('search.amc.quotation')
		models_data=self.pool.get('ir.model.data')
		product_req_ids = product_req_obj.search(cr, uid, [('select_request','=',True),('psd_sales_entry','=',False)], context=context)
		if not product_req_ids:
			raise osv.except_osv(("Alert!"),("No request selected!")) 
		new_id_list = []
		context.update({'request_from_sale':'request_from_sale'})
		for product_req_id in product_req_ids:
			new_id = product_req_obj.generate_service_quotation(cr, uid, product_req_id, context=context)
			product_req_obj.write(cr, uid, product_req_id, {'select_request': False}, context=context)
			new_id_list.append(int(new_id))
		self.write(cr, uid, ids[0], 
			{
				'product_request_ids': [(6, 0, [])],
				'pushed': True
			},context=context)	
		print len(new_id_list),'pppp'
		if len(new_id_list) == 1:
			form_id = models_data.get_object_reference(cr, uid, 'psd_amc_quotation', 'view_amc_quotation_form')	
			return {
			   'name':'Service Quotation',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'amc.quotation',
			   'res_id': new_id_list[0],
			   'type': 'ir.actions.act_window',
			   'target': 'current',
			   'context':context
			}
		if len(new_id_list) > 1:
			form_id = models_data.get_object_reference(cr, uid, 'psd_amc_quotation', 'search_amc_quotation_form')
			search_amc_quotation_vals = {
				'search_amc_quot_lines': [(6, 0, new_id_list)]
			}
			search_amc_quotation_id = search_amc_quotation_obj.create(cr,uid,search_amc_quotation_vals,context=context)
			
			return {
				   'name':'Search Service Quotation',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'search.amc.quotation',
				   'res_id':int(search_amc_quotation_id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   }

request_search_sales()