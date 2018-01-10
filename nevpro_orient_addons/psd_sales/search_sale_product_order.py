from osv import osv,fields

class search_sale_product_order(osv.osv):
	_name = "search.sale.product.order"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'name':fields.char('Customer / Company Name',size=30),
		'request_id': fields.char('Request Id',size=100),
		'customer_id':fields.char('Customer Id',size=100),
		'contact_name':fields.char('Contact Name',size=100),
		'contact_number':fields.char('Contact Number',size=11),
		'flat_no':fields.char('Unit/Apartment No',size=100),
		'building_name':fields.char('Building Name',size=100),
		'sub_area':fields.char('Sub Area',size=100),
		'street':fields.char('Street',size=100),
        'landmark':fields.char('Landmark',size=100),
        'city_id':fields.many2one('city.name','City'),		
		'status':fields.selection([('new','New'),
						('pending','Pending'),
						('ordered','Ordered'),
						('partial_delivery_scheduled','Partial Delivery Scheduled'),
						('delivery_scheduled','Delivery Scheduled'),
						('delivered','Delivered'),
						('cancelled','Cancelled'),
						('lost','Lost'),
						],'Status'), 
		'erp_order_no':fields.char('Product Order Number',size=100),
		'web_order_no':fields.char('Web Order Number',size=100),
		'web_order_date_from':fields.date('Online Order Date From'),
		'web_order_date_to':fields.date('Online Order Date To'),		
		'erp_order_date_from':fields.date('Order Date From'),
		'erp_order_date_to':fields.date('Order Date To'),
		'pse_id':fields.many2one('hr.employee','PSE'),
		'search_sales_product_order_lines': fields.one2many('psd.sales.product.order','search_sale_order_id','Product Sale Order'),
		'not_found':fields.boolean('not found'),
		'sku_name_id':fields.many2one('product.product','Product Name'),
		'product_name_id':fields.many2one('product.generic.name','Product'),
		'bird_pro':fields.boolean('Bird Pro'),
	}

	_defaults = {
		'company_id': _get_company
	}

	def clear_product_order(self,cr,uid,ids,context=None):
		for k in self.browse(cr,uid,ids):
			self.write(cr,uid, k.id,
				{
					'name':None,
					'request_id':None,
					'customer_id':None,
					'contact_name':None,
					'contact_number':None,
					'flat_no':None,
					'building_name':None,
					'sub_area':None,
					'landmark':None,
					'street':None,
					'city_id':False,
					'web_order_date_from':False,
					'web_order_date_to':False,
					'pse_id':False,
					'status':None,
					'web_order_no':None,
					'erp_order_no':False,
					'erp_order_date_from':False,
					'erp_order_date_to':False,
					'sku_name_id':False,
					'product_name_id':False,
					'bird_pro':False,
				},context=context)	
			for req in k.search_sales_product_order_lines:
				self.pool.get('psd.sales.product.order').write(cr,uid,req.id,{'search_sale_order_id':None})	
		return True


		

	def search_sales_product_order(self,cr,uid,ids,context=None):
		product_order_obj = self.pool.get('psd.sales.product.order')
		res_partner_add_obj = self.pool.get('res.partner.address')
		res_partner_obj = self.pool.get('res.partner')
		product_order_line_obj = self.pool.get('psd.sales.product.order.lines')
		res = False
		domain = []
		true_items = []
		rec = self.browse(cr, uid, ids[0])
		self.write(cr,uid,ids[0],{'not_found':False,'search_sales_product_order_lines':[(6, 0, 0)]})
		if rec.name:
			true_items.append('name')
		if rec.contact_name:
			true_items.append('contact_person')
		if rec.contact_number:
			true_items.append('contact_number')
		if rec.status:
			true_items.append('state')
		if rec.request_id:
			true_items.append('request_id')
		if rec.erp_order_no:
			true_items.append('erp_order_no')
		if rec.web_order_no:
			true_items.append('web_order_no')
		if rec.bird_pro:
			true_items.append('bird_pro')
		if rec.erp_order_date_from and not rec.erp_order_date_to:
			raise osv.except_osv(("Alert!"),("Please enter 'ERP Order To date'!"))
		if not rec.erp_order_date_from and rec.erp_order_date_to:
			raise osv.except_osv(("Alert!"),("Please enter 'ERP Order From date'!"))	
		if rec.erp_order_date_from and rec.erp_order_date_to:		    
			domain.append(('erp_order_date', '>=', rec.erp_order_date_from))
			domain.append(('erp_order_date', '<=', rec.erp_order_date_to))
		if rec.web_order_date_from and not rec.web_order_date_to:
			raise osv.except_osv(("Alert!"),("Please enter 'Web Order To date'!"))
		if not rec.web_order_date_from and rec.web_order_date_to:
			raise osv.except_osv(("Alert!"),("Please enter 'Web Order From date'!"))	
		if rec.web_order_date_from and rec.web_order_date_to:		    
			domain.append(('web_order_date', '>=', rec.web_order_date_from))
			domain.append(('web_order_date', '<=', rec.web_order_date_to))
		if rec.customer_id:
			true_items.append('partner_id.ou_id')
		if rec.flat_no:
			true_items.append('delivery_location_id.apartment')
		if rec.building_name:
			true_items.append('delivery_location_id.building')
		if rec.sub_area:
			true_items.append('delivery_location_id.sub_area')
		if rec.street:
			true_items.append('delivery_location_id.street')
		if rec.landmark:
			true_items.append('delivery_location_id.landmark')
		if rec.city_id:
			true_items.append('delivery_location_id.city_id.id')
		if rec.pse_id:
			true_items.append('pse_id')
		if rec.sku_name_id:
			true_items.append('sku_name_id')
		if rec.product_name_id:
			true_items.append('product_name_id')
		for true_item in true_items:
			if true_item == 'bird_pro':
				domain.append(('bird_pro', '=', rec.bird_pro))
			if true_item == 'name':
				domain.append(('name', 'ilike', rec.name))
			if true_item == 'state':
				domain.append(('state', 'ilike', rec.status))
			if true_item == 'request_id':
				domain.append(('request_id', 'ilike', rec.request_id))
			if true_item == 'web_order_no':
				domain.append(('web_order_no', 'ilike', rec.web_order_no))
			if true_item == 'erp_order_no':
				domain.append(('erp_order_no', 'ilike', rec.erp_order_no))
			if true_item == 'contact_person':
				domain.append(('contact_person', 'ilike', rec.contact_name))
			if true_item == 'partner_id.ou_id':
				domain.append(('partner_id.ou_id', 'ilike', rec.customer_id))
			if true_item == 'delivery_location_id.apartment':
				domain.append(('delivery_location_id.apartment', 'ilike', rec.flat_no))
			if true_item == 'delivery_location_id.building':
				domain.append(('delivery_location_id.building', 'ilike', rec.building_name))
			if true_item == 'delivery_location_id.sub_area':
				domain.append(('delivery_location_id.sub_area', 'ilike', rec.sub_area))
			if true_item == 'delivery_location_id.landmark':
				domain.append(('delivery_location_id.landmark', 'ilike', rec.landmark))
			if true_item == 'delivery_location_id.street':
				domain.append(('delivery_location_id.street', 'ilike', rec.street))
			if true_item == 'delivery_location_id.city_id.id':
				domain.append(('delivery_location_id.city_id.id', '=', rec.city_id.id))
			if true_item == 'pse_id':
				domain.append(('pse_id', '=', rec.pse_id.id))
			if true_item == 'product_name_id':
				domain.append(('generic', '=', rec.product_name_id.name))
			# if true_item == 'sku_name_id':
			# 	domain.append(('skus', '=', rec.sku_name_id.name))
			if true_item == 'sku_name_id':
				search_prod = product_order_line_obj.search(cr,uid,[('product_name_id','=',rec.sku_name_id.id)])
				lines_list = []
				for x in product_order_line_obj.browse(cr,uid,search_prod):
					if not x.psd_sales_product_order_lines_id.id in lines_list:
						lines_list.append(x.psd_sales_product_order_lines_id.id)
				search_prod = product_order_obj.search(cr,uid,[('id','in',lines_list)])
				domain.append(('id','in',search_prod))

			if true_item == 'contact_number':
				search_number = res_partner_add_obj.search(cr,uid,[('phone_m2m_xx.name','ilike',rec.contact_number)])
				partner_list = []
				for x in res_partner_add_obj.browse(cr,uid,search_number):
					partner_list.append(x.partner_id.id)
				search_order = product_order_obj.search(cr,uid,[('partner_id.id','in',partner_list)])
				domain.append(('id','in',search_order))
		product_order_ids = product_order_obj.search(cr, uid, domain, context=context)
		if not product_order_ids:
			self.write(cr,uid,ids[0],{'not_found':True})
			return res
		else:
			res = self.write(cr, uid, ids[0], 
				{
					'search_sales_product_order_lines': [(6, 0, product_order_ids)]
				})
			return res

search_sale_product_order()
