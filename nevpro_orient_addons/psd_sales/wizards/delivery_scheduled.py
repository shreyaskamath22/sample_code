from datetime import date,datetime, timedelta
from osv import osv,fields
from tools.translate import _



class scheduled_product_list(osv.osv):
	_name = "scheduled.product.list"
	_columns = {
		'select_all_orders':fields.boolean('Select all Orders'),
		'scheduled_product_list_ids':fields.one2many('scheduled.product.list.line','scheduled_product_list_id',string='Scheduled Products'),
		'godown':fields.many2one('res.company',string='Godown'),
		}



	def onchange_select_all_orders(self,cr,uid,ids,select_all_orders,scheduled_product_list_ids):
		v={}
		order_ids = []
		if select_all_orders == 1:
			for order_id in scheduled_product_list_ids:
				if order_id[0]==0: 
					order_id[2]['check_order'] = True
					order_ids.append(order_id)
		else :
			for order_id in scheduled_product_list_ids:
				if order_id[0]==0: 
					order_id[2]['check_order'] = False
					order_ids.append(order_id)
		v['scheduled_product_list_ids'] = order_ids
		return {'value': v}

	def default_get(self,cr,uid,fields,context=None):
		customer_line_ids =[]
		if context is None: context = {}
		res = super(scheduled_product_list, self).default_get(cr, uid, fields, context=context)
		picking_ids = context.get('active_ids', [])
		if not picking_ids or (not context.get('active_model') == 'psd.sales.product.order') \
			or len(picking_ids) != 1:
			# Partial Picking Processing may only be done for one picking at a time
			return res
		picking_id, = picking_ids
		if 'scheduled_product_list_ids' in fields:
			picking = self.pool.get('psd.sales.product.order').browse(cr, uid, picking_id, context=context)
			line_rec = self.pool.get('psd.sales.product.order.lines').search(cr,uid,[('psd_sales_product_order_lines_id','=',picking_id),('done_products','=',False)])
			line_brw = self.pool.get('psd.sales.product.order.lines').browse(cr,uid,line_rec)
			moves = [self._partial_move_for(cr, uid, m) for m in line_brw]
			res.update(scheduled_product_list_ids=moves)
		godown_id=self.pool.get('res.users').browse(cr,uid,uid).company_id.parent_establishment.id
		res['godown']=godown_id
		res['select_all_orders']=True
		return res

	def _partial_move_for(self, cr, uid, move):
		partial_move ={}
		product_name_id = move.product_name_id.id
		# sku_name_id = move.sku_name_id.id
		ordered_quantity = move.ordered_quantity
		product_mrp = move.product_mrp
		total_amount = move.total_amount
		batch_no = move.batch_number.id
		mrp_date = move.manufacturing_date
		main_id = move.psd_sales_product_order_lines_id.id
		allocated_quantity = move.allocated_quantity
		extended_warranty =move.extended_warranty
		discount = move.discount
		discounted_value = move.discounted_value
		discounted_price = move.discounted_price
		discounted_amount = move.discounted_amount
		igst_amount =  move.igst_amount
		cgst_amount = move.cgst_amount
		sgst_amount = move.sgst_amount
		igst_rate =  move.igst_rate
		cgst_rate = move.cgst_rate
		sgst_rate = move.sgst_rate
		# tax_id = move.tax_id.id
		total_amount = move.total_amount
		total_amount_paid = total_amount + igst_amount + cgst_amount + sgst_amount

		product_basic_rate = move.product_basic_rate
		godown_id=self.pool.get('res.users').browse(cr,uid,uid).company_id.parent_establishment.id
		# if allocated_quantity == 0.0:
		# 	allocated_quantity = move.ordered_quantity
		# else:
		# 	allocated_quantity = move.ordered_quantity - move.allocated_quantity
		print cgst_amount,sgst_amount,igst_amount
		# bb
		partial_move = {
			'sale_order_id': main_id,
			'sale_order_line_id': move.id,
			'product_name_id': product_name_id,
			# 'sku_name_id': sku_name_id,
			'ordered_quantity': ordered_quantity,
			'allocated_quantity': allocated_quantity,
			'discount':discount,
			'discounted_value':discounted_value,
			'discounted_price':discounted_price,
			'discounted_amount':discounted_amount,
			# 'tax_id':tax_id	,
			'product_basic_rate':product_basic_rate,
			'product_mrp': product_mrp,
			'product_uom_id':move.product_uom_id.id,
			'product_code':move.product_name_id.default_code,
			'mrp_date': mrp_date,
			'extended_warranty':extended_warranty,
			'godown':godown_id,	
			'specification':move.specification,		
			'igst_amount':igst_amount,
			'cgst_amount':cgst_amount,
			'sgst_amount':sgst_amount,
			'igst_rate':igst_rate,
			'sgst_rate':igst_rate,
			'cgst_rate':igst_rate,
			'grand_total':total_amount_paid,
			'check_order':True
		}
		return partial_move

	def round_off_grand_total(self,cr,uid,ids,grand_total,context=None):
		roundoff_grand_total = grand_total + 0.5
		s = str(roundoff_grand_total)
		dotStart = s.find('.')
		grand_total = int(s[:dotStart])
		return grand_total

	def submit(self,cr,uid,ids,context=None):
		amount_list = []
		taxes = {}
		bird_pro = False
		bird_pro_charge = 0.0
		service_tax_value = 0.0
		sb_tax_value = 0.0
		kk_tax_value = 0.0
		total_tax_amount = 0.0
		new_total_amount = 0.0
		total_service_tax = 0.0
		psd_sales_delivery_schedule_obj = self.pool.get('psd.sales.delivery.schedule')
		account_tax = self.pool.get('account.tax')
		scheduled_product_list_line_obj = self.pool.get('scheduled.product.list.line')
		psd_sales_product_order_lines_obj =self.pool.get('psd.sales.product.order.lines')
		psd_sales_product_order_obj = self.pool.get('psd.sales.product.order')
		tax_line_obj = self.pool.get('tax')
		expected_delivery_date= context.get('expected_delivery_date')
		active_ids_value = context.get('sale_order_active_id')

		search_curr_sale_order_id = psd_sales_product_order_obj.search(cr,uid,[('id','=',active_ids_value)])[0]
		browse_curr_sale_order_obj = psd_sales_product_order_obj.browse(cr,uid,search_curr_sale_order_id)
		total_sale_order_line_list= []
		all_allocated_list = []
		if browse_curr_sale_order_obj.bird_pro and browse_curr_sale_order_obj.install_maintain_charges:
			bird_pro = browse_curr_sale_order_obj.bird_pro
			bird_pro_charge = browse_curr_sale_order_obj.install_maintain_charges
		company_id= self.pool.get('res.company')._company_default_get(cr, uid, 'scheduled.product.list.line', context=context)
		todays_date = datetime.now().date()
		self.pool.get('psd.sales.product.order').write(cr,uid,active_ids_value,{'select_all_orders':True})
		cr.commit()
		values_create = {
							'despatcher':company_id,
							'expected_delivery_date':expected_delivery_date,
							'state':'new',
							'sale_order_id':active_ids_value,
							'bird_pro':bird_pro,
							'bird_pro_charge':bird_pro_charge,
							'select':True,
						}
		o= self.browse(cr,uid,ids[0])
		if not o.scheduled_product_list_ids:
			raise osv.except_osv(_('Warning!'),_("No product left for scheduling for this order"))
		for rec in o.scheduled_product_list_ids:
			if not rec.check_order:
				raise osv.except_osv(_('Warning!'),_("Please select all products to schedule this order"))
		values_create['godown'] = o.godown.id
		delivery_id = psd_sales_delivery_schedule_obj.create(cr,uid,values_create,context=context)

		main_id = o.id
		for each in o.scheduled_product_list_ids:
			sale_order_id = each.sale_order_id.id
		check_ids = scheduled_product_list_line_obj.search(cr,uid,[('scheduled_product_list_id','=',main_id)])
		search_ids = scheduled_product_list_line_obj.search(cr,uid,[('scheduled_product_list_id','=',main_id),('check_order','=',True)])
		if len(check_ids) == len(search_ids):
			psd_sales_product_order_obj.write(cr,uid,sale_order_id,{'done_products':True})
			cr.commit()
		else:
			psd_sales_product_order_obj.write(cr,uid,sale_order_id,{'done_products':False})
			cr.commit()
		if not search_ids:
			raise osv.except_osv(_('Warning!'),_("Please tick the check box for the products"))
		if search_ids:
			print search_ids
			browse_ids = scheduled_product_list_line_obj.browse(cr,uid,search_ids)
			for line_id in browse_ids:
				sale_order_id = line_id.sale_order_id.id
				sale_order_line_id = line_id.sale_order_line_id.id
				product_name_id = line_id.product_name_id.id
				# sku_name_id = line_id.sku_name_id.id
				sale_allocated_quantity = line_id.sale_order_line_id.allocated_quantity
				ordered_quantity = line_id.ordered_quantity
				allocated_quantity = line_id.allocated_quantity
				product_mrp = line_id.product_mrp
				batch_no = line_id.batch_no.id
				mrp_date =line_id.mrp_date
				product_basic_rate = line_id.product_basic_rate
				igst_amount = line_id.igst_amount
				sgst_amount = line_id.sgst_amount
				cgst_amount = line_id.cgst_amount
				print sgst_amount,igst_amount,cgst_amount
				# nn
				igst_rate = line_id.igst_rate
				cgst_rate = line_id.cgst_rate
				sgst_rate = line_id.sgst_rate
				total_amount = line_id.total_amount
				# total_amount_paid = line_id.total_amount_paid
				extended_warranty = line_id.extended_warranty

				order_line_obj = self.pool.get('psd.sales.product.order.lines').browse(cr,uid,sale_order_line_id)
				# remaining_qty = order_line_obj.ordered_quantity - order_line_obj.allocated_quantity
				# if remaining_qty < 0:
				# 	raise osv.except_osv(_('Warning!'),_("Allocated Quantity can not be greater than Remaining Quantity!"))				 
				values = {
					'sale_order_id':sale_order_id,
					'sale_order_line_id': sale_order_line_id,
					'product_name_id':product_name_id,
					# 'sku_name_id':sku_name_id,
					'ordered_quantity':ordered_quantity,
					'allocated_quantity':allocated_quantity,
					'product_mrp':product_mrp,
					'batch_no':batch_no,
					'discount':line_id.discount,
					'discounted_price':line_id.discounted_price,
					# 'discounted_amount':discount_value,
					# 'tax_id':line_id.tax_id.id,
					# 'tax_amount':tax_amount,
					'product_basic_rate':product_basic_rate,
					'total_amount':total_amount,
					'mrp_date':mrp_date,
					'scheduled_delivery_list_id':delivery_id,
					'extended_warranty':extended_warranty,
					'godown':line_id.godown.id,
					'specification':line_id.specification,
					'igst_amount':igst_amount,
					'cgst_amount':cgst_amount,
					'sgst_amount':sgst_amount,
					'igst_rate':igst_rate,
					'sgst_rate':sgst_rate,
					'cgst_rate':cgst_rate,
					# 'grand_total':total_amount_paid,
				}
				amount_list.append(total_amount)
				update_calc_data = {'total_amount':total_amount}
				write_id = scheduled_product_list_line_obj.write(cr,uid,line_id.id,update_calc_data)
				psd_id =scheduled_product_list_line_obj.create(cr,uid,values)
				tax_id = line_id.tax_id.id

				print product_name_id,allocated_quantity
				print sale_order_id
				abc = self.pool.get('psd.sales.product.order.lines').search(cr,uid,[('psd_sales_product_order_lines_id','=',sale_order_id),('product_name_id','=',product_name_id)])
				self.pool.get('psd.sales.product.order.lines').write(cr,uid,abc,{'done_products':True})
				cr.commit()

		total = sum(amount_list)
		for sale in browse_curr_sale_order_obj.psd_sales_product_order_lines_ids:
			total_sale_order_line_list.append(1)
			if sale.allocated_quantity == sale.ordered_quantity:
				all_allocated_list.append(1)
		print len(total_sale_order_line_list),len(all_allocated_list)
		if len(total_sale_order_line_list) == len(all_allocated_list):
			psd_sales_product_order_obj.write(cr,uid,active_ids_value,{'state':'delivery_scheduled'})

		return {'type': 'ir.actions.act_window_close'}
scheduled_product_list()


class scheduled_product_list_line(osv.osv):
	_name = "scheduled.product.list.line"

	_columns = {
		'check_order':fields.boolean(''),
		'sale_order_id': fields.many2one('psd.sales.product.order','Sale Order Id'),
		'sale_order_line_id': fields.many2one('psd.sales.product.order.lines','Sale Order Line Id'),
		# 'product_name_id': fields.many2one('product.generic.name','Product Name'),
		'product_name_id':fields.many2one('product.product','Product Name'),
		# 'sku_name_id':fields.many2one('product.product','SKU Name'),
		'ordered_quantity':fields.integer('Ordered Quantity'),
		'allocated_quantity':fields.integer('Allocated Quantity'),
		'product_uom_id':fields.many2one('product.uom','UOM'),
		'product_mrp':fields.float('MRP'),
		'product_code':fields.char('Product Code',size=200),
		'mrp_date':fields.date('Mfg Date'),
		'batch_no':fields.many2one('res.batchnumber','Batch No'),
		'product_basic_rate':fields.float('Basic Rate'),
		'discount':fields.float('Disc %'),
		'discounted_value':fields.float('Discounted Value'),
		'discounted_price':fields.float('Discounted Price'),
		'discounted_amount':fields.float(string='Disc Amt'),
		'tax_id':fields.many2one('account.tax','Tax %'),
		'tax_amount':fields.float('Tax Amt'),
		'total_amount':fields.float('Total Amount'),
		'extended_warranty':fields.selection([
							('6','6 Months'),
							('12','12 Months'),
							('18','18 Months'),
							('24','24 Months'),
							('36','36 Months'),
							('48','48 Months'),
							('60','60 Months')],'Extended Warranty'),
		'scheduled_product_list_id':fields.many2one('scheduled.product.list','Scheduled Products',ondelete='cascade'),
		'scheduled_delivery_list_id': fields.many2one('psd.sales.delivery.schedule','Delivered Products',ondelete='cascade'),
		'godown':fields.many2one('res.company',string='Godown'),
		'specification': fields.char('Specification',size=500),
		'cgst_rate':fields.char('CSGT Rate',size=10),
		'sgst_rate':fields.char('SGST Rate',size=10),
		'igst_rate':fields.char('IGST Rate',size=10),
		'cgst_amount':fields.float('CGST Amount'),
		'sgst_amount':fields.float('SGST Amount'),
		'igst_amount':fields.float('IGST Amount'),
		'grand_total':fields.float('Grand Total'),
		}

scheduled_product_list_line()
