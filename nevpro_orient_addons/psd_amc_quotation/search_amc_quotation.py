from osv import osv,fields

class search_amc_quotation(osv.osv):
	_name = "search.amc.quotation"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'name':fields.char('Customer / Company Name',size=30),	
		'quotation_no':fields.char('Quotation Number',size=256),
		'from_date':fields.date('From Date'),
		'to_date':fields.date('To Date'),
		'contact_number':fields.char('Contact Number',size=256),
		'product_id':fields.many2one('product.generic.name','Product'),
		'product_type':fields.selection([('product','Product'),
						('amc','AMC')],'Product Type'),
		'landline':fields.char('Landline',size=256),
		'status':fields.selection([('new','New'),
						('pending','Pending'),
						('ordered','Ordered'),
						('lost','Lost'),
						],'Status'),
		'request_id':fields.char('Request ID',size=20),
		'search_amc_quot_lines': fields.one2many('amc.quotation','search_amc_quot_id','Service Quotations'),
		'not_found':fields.boolean('not found'),
		'address':fields.char('Address',size=500),
		'created_by':fields.many2one('res.users','Created By'),
		'pse':fields.many2one('hr.employee','PSE'),
		'quotation_value_from':fields.float('Quotation Value From'),
		'quotation_value_to':fields.float('Quotation Value To'),
	}

	_defaults = {
		'company_id': _get_company
	}

	def clear_amc_quotation(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		self.write(cr,uid, ids[0],
			{
				'name':None,
				'request_id':None,
				'contact_number':None,
				'status':False,
				'from_date':False,
				'to_date':False,
				'quotation_no':None,
				'product_id':False,
				'not_found':False,
				'address':False,
				'created_by':False,
				'pse':False,
				'quotation_value_from':False,
				'quotation_value_to':False,
			},context=context)		
		return True

	def search_amc_quotation(self,cr,uid,ids,context=None):
		amc_quotation_obj = self.pool.get('amc.quotation')
		res_partner_add_obj = self.pool.get('res.partner.address')
		res_partner_obj = self.pool.get('res.partner')
		amc_quotation_line_obj = self.pool.get('amc.quotation.line')
		res = False
		domain = []
		true_items = []
		rec = self.browse(cr, uid, ids[0])
		self.write(cr,uid,ids[0],{'not_found':False,'search_amc_quot_lines':[(6, 0, 0)]})
		if rec.name:
			true_items.append('name')
		if rec.status:
			true_items.append('state')
		if rec.quotation_no:
			true_items.append('quotation_number')
		if rec.request_id:
			true_items.append('request_id')
		if rec.contact_number:
			true_items.append('contact_number')
		if rec.product_id:
			true_items.append('product_id')
		if rec.address:
			true_items.append('address')
		if rec.created_by:
			true_items.append('created_by')
		if rec.pse:
			true_items.append('pse')
		if rec.quotation_value_from:
			true_items.append('quotation_value_from')
		if rec.quotation_value_to:
			true_items.append('quotation_value_to')
		if rec.from_date and not rec.to_date :
			raise osv.except_osv(("Alert!"),("Please enter 'To date'!"))
		if not rec.from_date and rec.to_date :
			raise osv.except_osv(("Alert!"),("Please enter 'From date'!"))	
		if rec.from_date and rec.to_date:		    
			domain.append(('quotation_date', '>=', rec.from_date))
			domain.append(('quotation_date', '<=', rec.to_date))
		if rec.quotation_value_from and rec.quotation_value_to:
			if rec.quotation_value_from > rec.quotation_value_to:
				raise osv.except_osv(("Alert!"),("'Quotation value From' cannot be greater than 'Quotation Value To'!"))
			domain.append(('grand_total', '>=', rec.quotation_value_from))
			domain.append(('grand_total', '<=', rec.quotation_value_to))
		for true_item in true_items:
			if true_item == 'name':
				domain.append(('name', 'ilike', rec.name))
			if true_item == 'state':
				domain.append(('state', 'ilike', rec.status))
			if true_item == 'quotation_number':
				domain.append(('quotation_number', 'ilike', rec.quotation_no))
			if true_item == 'request_id':
				domain.append(('request_id', 'ilike', rec.request_id))
			if true_item == 'pse':
				domain.append(('pse', '=', rec.pse.id))
			if true_item == 'address':
				search_address = res_partner_add_obj.search(cr,uid,['|',('premise_type','ilike',rec.address),'|',('apartment','ilike',rec.address),'|',('sub_area','ilike',rec.address),'|',('street','ilike',rec.address),'|',('landmark','ilike',rec.address),'|',('apartment','ilike',rec.address),'|',('building','ilike',rec.address),'|',('sub_area','ilike',rec.address),('zip','=',rec.address)])
				# search_address = res_partner_add_obj.search(cr,uid,[('premise_type','ilike',rec.address)])
				domain.append(('site_address','in',search_address))
				domain.append(('billing_address','in',search_address))
			if true_item == 'quotation_value_from':
				domain.append(('grand_total', '>=', rec.quotation_value_from))
			if true_item == 'quotation_value_to':
				domain.append(('grand_total', '<=', rec.quotation_value_to))
			if true_item == 'created_by':
				domain.append(('user_id', '=', rec.created_by.id))
			if true_item == 'contact_number':
				search_number = res_partner_add_obj.search(cr,uid,[('phone_m2m_xx.name','ilike',rec.contact_number)])
				partner_list = []
				for x in res_partner_add_obj.browse(cr,uid,search_number):
					partner_list.append(x.partner_id.id)
				search_quotation = amc_quotation_obj.search(cr,uid,[('partner_id.id','in',partner_list)])
				domain.append(('id','in',search_quotation))
			if true_item == 'product_id':
				search_prod = amc_quotation_line_obj.search(cr,uid,[('product_generic_name','=',rec.product_id.id)])
				lines_list = []
				for x in amc_quotation_line_obj.browse(cr,uid,search_prod):
					if not x.amc_quotation_id in lines_list:
						lines_list.append(x.amc_quotation_id.id)
				search_quotation_prod = amc_quotation_obj.search(cr,uid,[('id','in',lines_list)])
				domain.append(('id','in',search_quotation_prod))
		amc_quotation_ids = amc_quotation_obj.search(cr, uid, domain, context=context)
		if not amc_quotation_ids:
			self.write(cr,uid,ids[0],{'not_found':True})
			return res
		else:
			res = self.write(cr, uid, ids[0], 
				{
					'search_amc_quot_lines': [(6, 0, amc_quotation_ids)]
				})
			return res

search_amc_quotation()