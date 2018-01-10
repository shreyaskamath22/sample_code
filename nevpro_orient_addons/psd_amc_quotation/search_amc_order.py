from osv import osv,fields

class search_amc_order(osv.osv):
	_name = "search.amc.order"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'name':fields.char('Customer / Company Name',size=30),	
		'quotation_no':fields.char('Quotation Number',size=256),
		'order_no':fields.char('Order Number',size=256),
		'order_date':fields.date('Order Date'),
		'from_date':fields.date('From Date'),
		'to_date':fields.date('To Date'),
		'contact_number':fields.char('Contact Number',size=256),
		'product_id':fields.many2one('product.generic.name','Product'),
		'product_type':fields.selection([('product','Product'),
						('amc','AMC')],'Product Type'),
		'status':fields.selection([('new','New'),
						('pending','Pending'),
						('ordered','Ordered'),
						('cancelled','Cancelled'),
						],'Status'),
		'request_id':fields.char('Request ID',size=20),
		'search_amc_order_lines': fields.one2many('amc.sale.order','search_amc_order_id','Service Quotations'),
		'not_found':fields.boolean('not found'),
	}

	_defaults = {
		'company_id': _get_company
	}

	def clear_amc_order(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		self.write(cr,uid, ids[0],
			{
				'name':None,
				'request_id':None,
				'product_id':False,
				'contact_number':None,
				'status':False,
				'from_date':False,
				'to_date':False,
				'quotation_no':None,
				'order_no':None,
				'order_date':None,
				'not_found':False,
			},context=context)		
		return True

	def search_amc_order(self,cr,uid,ids,context=None):
		amc_order_obj = self.pool.get('amc.sale.order')
		res_partner_add_obj = self.pool.get('res.partner.address')
		res_partner_obj = self.pool.get('res.partner')
		res = False
		domain = []
		true_items = []
		rec = self.browse(cr, uid, ids[0])
		self.write(cr,uid,ids[0],{'not_found':False,'search_amc_order_lines':[(6, 0, 0)]})
		res = False
		domain = []
		true_items = []
		rec = self.browse(cr, uid, ids[0])
		if rec.product_id:
			true_items.append('product_id')
		if rec.name:
			true_items.append('customer_name')
		if rec.status:
			true_items.append('state')
		if rec.quotation_no:
			true_items.append('quotation_number')
		if rec.request_id:
			true_items.append('request_id')
		if rec.contact_number:
			true_items.append('contact_number')
		if rec.order_date:
			true_items.append('order_date')
		if rec.order_no:
			true_items.append('order_number')
		if rec.from_date and not rec.to_date:
			raise osv.except_osv(("Alert!"),("Please enter 'To date'!"))
		if not rec.from_date and rec.to_date:
			raise osv.except_osv(("Alert!"),("Please enter 'From date'!"))	
		if rec.from_date and rec.to_date:		    
			domain.append(('quotation_date', '>=', rec.from_date))
			domain.append(('quotation_date', '<=', rec.to_date))
		for true_item in true_items:
			if true_item == 'customer_name':
				domain.append(('customer_name', 'ilike', rec.name))
			if true_item == 'state':
				domain.append(('state', 'ilike', rec.status))
			if true_item == 'quotation_number':
				domain.append(('quotation_number', 'ilike', rec.quotation_no))
			if true_item == 'request_id':
				domain.append(('request_id', 'ilike', rec.request_id))
			if true_item == 'order_date':
				domain.append(('order_date', 'ilike', rec.order_date))
			if true_item == 'order_number':
				domain.append(('order_number', 'ilike', rec.order_no))
			if true_item == 'product_id':
				domain.append(('products', 'ilike', rec.product_id.name))
			if true_item == 'contact_number':
				search_number = res_partner_add_obj.search(cr,uid,[('phone_m2m_xx.name','ilike',rec.contact_number)])
				partner_list = []
				for x in res_partner_add_obj.browse(cr,uid,search_number):
					partner_list.append(x.partner_id.id)
				search_order = amc_order_obj.search(cr,uid,[('partner_id.id','in',partner_list)])
				domain.append(('id','in',search_order))
		amc_order_ids = amc_order_obj.search(cr, uid, domain, context=context)
		if not amc_order_ids:
			self.write(cr,uid,ids[0],{'not_found':True})
			return res
		else:
			res = self.write(cr, uid, ids[0], 
				{
					'search_amc_order_lines': [(6, 0, amc_order_ids)]
				})
			return res

search_amc_order()