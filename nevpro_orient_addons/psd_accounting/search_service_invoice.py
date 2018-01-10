from osv import osv,fields

class search_service_invoice(osv.osv):
	_name = "search.service.invoice"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'name':fields.char('Customer Name',size=200),	
		'invoice_number':fields.char('Invoice Number',size=256),
		'from_date':fields.date('From Date'),
		'to_date':fields.date('To Date'),
		'delivery_note_date':fields.date('Delivery Note Date'),
		'state':fields.selection([('open','Open'),
						('printed','Printed'),
						('paid','Paid'),
						('writeoff','Writeff'),
						('partially_writeoff','Partially Writeoff'),
						('cancelled','Cancelled'),
						],'Status'),
		'mobile':fields.char('Contact Number',size=256),
		'customer_id':fields.char('Customer ID',size=256),
		'pse':fields.many2one('hr.employee','PSE Name'),
		# 'landline':fields.char('Landline',size=256),
		'search_amc_invoice_lines':fields.one2many('invoice.adhoc.master','search_sevice_invoice_id','Search Invoice'),
		# 'search_product_quot_lines': fields.one2many('psd.sales.product.quotation','search_product_quot_id','Product Quotations'),
		'not_found':fields.boolean('not found'),
		'erp_order_no':fields.many2one('amc.sale.order'),
		'erp_order_date':fields.date(string='Service Order Date'),
		'product_id':fields.many2one('product.product','SKU Name'),
		'service_type':fields.selection([('Annual Maintainance Contract','Annual Maintainance Contract'),
					('Repairs & Maintainance Charges','Repairs & Maintainance Charges'),
					('Commissioning & Installation Charges','Commissioning & Installation Charges'),
					('Exempted Service','Exempted Service'),
					('Maintainance or Repair Service','Maintainance or Repair Service')
					],'Service Type *'),
		'classification': fields.selection([('Comprehensive','Comprehensive'),
					('Non Comprehensive','Non Comprehensive')],'Classification *'),
	}

	_defaults = {
		'company_id': _get_company
	}

	def clear_service_invoice_search(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		self.write(cr,uid, ids[0],
			{
				'name':None,
				'request_id':None,
				'product_type':False,
				'mobile':None,
				'status':False,
				'from_date':False,
				'to_date':False,
				'not_found':False,
				'quotation_no':None,
			},context=context)		
		return True

	def search_service_invoice_psd(self,cr,uid,ids,context=None):
		invoice_obj = self.pool.get('invoice.adhoc.master')
		invoice_adhoc = self.pool.get('invoice.adhoc')
		res = False
		domain = []
		true_items = []
		rec = self.browse(cr, uid, ids[0])
		self.write(cr,uid,ids[0],{'not_found':False,'search_amc_invoice_lines': [(6, 0, False)]})
		domain.append(('invoice_type', '=', 'service_invoice'))
		if rec.name:
			true_items.append('name')
		if rec.state:
			true_items.append('status')
		if rec.invoice_number:
			true_items.append('invoice_number')
		if rec.customer_id:
			true_items.append('partner_id.ou_id')
		if rec.pse:
			true_items.append('pse')
		if rec.from_date:
			true_items.append('from_date')		    
		if rec.to_date:
			true_items.append('to_date')
		if rec.product_id:
			true_items.append('product_id')
		if rec.erp_order_no:
			true_items.append('erp_order_no')
		if rec.erp_order_date:
			true_items.append('erp_order_date')
		if rec.service_type:
			true_items.append('service_type')
		if rec.classification:
			true_items.append('classification')

		for true_item in true_items:
			if true_item == 'name':
				domain.append(('cust_name', 'ilike', rec.name))
			if true_item == 'status':
				domain.append(('status', 'ilike', rec.state))
			if true_item == 'invoice_number':
				domain.append(('invoice_number', 'ilike', rec.invoice_number))
			if true_item == 'partner_id.ou_id':
				domain.append(('partner_id.ou_id', 'ilike', rec.customer_id))
			if true_item == 'pse':
				domain.append(('pse', '=', rec.pse.id))
			if true_item == 'from_date':
				domain.append(('invoice_date', '>=', rec.from_date))
			if true_item == 'to_date':
				domain.append(('invoice_date', '<=', rec.to_date))
			if true_item == 'product_id':
				search_prod = invoice_adhoc.search(cr,uid,[('product_id','=',rec.product_id.id)])
				lines_list = []
				for x in invoice_adhoc.browse(cr,uid,search_prod):
					if not x.service_invoice_id.id in lines_list:
						lines_list.append(x.service_invoice_id.id)
				search_quotation_prod = invoice_obj.search(cr,uid,[('id','in',lines_list)])
				domain.append(('id','in',search_quotation_prod))
			if true_item == 'erp_order_no':
				domain.append(('erp_order_no', 'ilike', rec.erp_order_no.order_number))
			if true_item == 'erp_order_date':
				domain.append(('erp_order_date', '=', rec.erp_order_date))
			if true_item == 'service_type':
				domain.append(('service_type', '=', rec.service_type))
			if true_item == 'classification':
				domain.append(('classification', '=', rec.classification))
		invoice_line_ids = invoice_obj.search(cr, uid, domain, context=context)
		if not invoice_line_ids:
			self.write(cr,uid,ids[0],{'not_found':True})
			return res
		else:
			res = self.write(cr, uid, ids[0], 
				{
					'search_amc_invoice_lines': [(6, 0, invoice_line_ids)]
				})
			return res

search_service_invoice()
