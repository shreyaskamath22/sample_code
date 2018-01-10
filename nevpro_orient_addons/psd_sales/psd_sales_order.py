from datetime import date,datetime, timedelta
from osv import osv,fields
from tools.translate import _
import time



class job_history(osv.osv):
	_inherit = "job.history"
	_columns = {
		'product_order_id':fields.many2one('psd.sales.product.order','Product Order ID'),

	}

class psd_sales_product_order(osv.osv):
	_inherit = "psd.sales.product.order"
	_order = "id desc, state asc"

	def _get_user(self, cr, uid, context=None):		
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).id

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_datetime(self,cr,uid,context=None):
		return time.strftime("%Y-%m-%d %H:%M:%S")

	def name_get(self, cr, uid, ids, context={}):
		# if not len(ids):
		#     return []
		res=[]
		for emp in self.browse(cr, uid, ids,context=context):
			 res.append((emp.id, emp.erp_order_no))     
		return res


	# def _show_record(self, cr, uid, ids, field_names, arg=None, context=None):
	# 	result = {}
	# 	if not ids: return result
	# 	for id in ids:
	# 		result.setdefault(id, [])
	# 	for res in self.browse(cr,uid,ids):
	# 		if res.erp_order_no:
	# 			scheduled_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('erp_order_no','=',res.erp_order_no)])
	# 			for r in scheduled_id:
	# 				result[res.id].append(r)
	# 		return result

	_columns = {
		'type':fields.char('Type',size=50),
		'company_id':fields.many2one('res.company','Company ID'),
		'partner_id': fields.many2one('res.partner','Partner'),
		'psd_quotation_id':fields.many2one('psd.sales.product.quotation'),
		'name':fields.char('Customer / Company Name',size=100),
		'address':fields.char('Address',size=256),
		'contact_number':fields.char('Contact Number',size=15),
		'created_date':fields.datetime('Created Date'),
		'delivery_date':fields.datetime('Delivery Date'),
		'delivery_location_id':fields.many2one('res.partner.address','Delivery Location'),
		'user_id':fields.many2one('res.users','User ID'),
		'erp_order_no':fields.char('Product Order Number',size=100),
		'erp_order_date':fields.date('Product Order Date'),
		'web_order_no':fields.char('Web Order Number',size=100),
		'web_order_date':fields.date('Web Order Date'),
		'contact_person':fields.char('Contact Person',size=100),
		'billing_location_id':fields.many2one('res.partner.address','Billing Location'),
		'pse_id':fields.many2one('hr.employee','PSE'),
		'request_id':fields.char('Request Id',size=100),
		'expected_delivery_date':fields.date('Expected Delivery Date'),
		'coupon_code':fields.char('Coupon Code',size=100),
		'gift_voucher':fields.char('Gift Voucher',size=100),
		'against_free_replacement':fields.boolean('Against Free Replacement'),
		'against_form':fields.selection([("against_form_c","Against Form 'C'"),("against_form_h","Against Form 'H'")],'Against Form'),
		'state':fields.selection([('new','New'),
						('pending','Pending'),
						('ordered','Ordered'),
						('partial_delivery_scheduled','Partial Delivery Scheduled'),
						('delivery_scheduled','Delivery Scheduled'),
						('delivered','Delivered'),
						('cancelled','Cancelled'),
						],'State'), 
		'order_total_vat':fields.float('Total VAT/CST'),
		'order_total_amount':fields.float('Basic Amount'),
		# 'tax_type':fields.selection([('normal','Normal'),('composite','Composite')],'Tax Type',required=True),
		# 'no_of_service':fields.integer('No of Service'),
		'install_maintain_charges':fields.float('Installation Charges'),
		'service_tax':fields.float('Service Tax 14%'),	
		's_b_cess':fields.float('S B Cess 0.50%'),
		'k_k_cess':fields.float('K K Cess 0.50%'),
		'quotation_no':fields.char('Quotation No',size=40),
		'is_quotation_no':fields.boolean(''),
		'payment_terms':fields.text('Payment Terms', size=500),
		'octroi':fields.selection([('Will be charged extra at actual; if applicable','Will be charged extra at actual; if applicable')],'Octroi'),
		'transportation':fields.text('Transportation',size=500),
		'bank_charges':fields.text('Bank Charges',size=500),
		'warranty':fields.text('Warranty',size=500),
		'despatch_schedule':fields.text('Despatch Schedule',size=500),
		'installation':fields.text('Installation',size=500),
		'notes':fields.text('Notes',size=500),
		'psd_sales_product_order_lines_ids':fields.one2many('psd.sales.product.order.lines','psd_sales_product_order_lines_id','Locations & Products'),
		'shipment_value':fields.float('Shipment Value'),
		'shipment_charges':fields.float('Shipment Charges'),
		'total_amount_paid':fields.float('Total Amount'),
		'search_sale_order_id':fields.many2one('search.sale.product.order','Search Product Order'),
		'delivery_schedule_ids':fields.one2many('psd.sales.delivery.schedule','sale_order_id',string="Delivery Schedule"),	
		'select_all_orders':fields.boolean('Select All'),
		'cancel_order': fields.boolean('Cancel Order'),
		'reason_for_cancellation': fields.text('Reason for Cancellation',size=500),
		'notes_one2many': fields.one2many('psd.sales.order.remarks','sale_order_id','Notes'),
		'tax_one2many':fields.one2many('tax','psd_so_id','Tax'),
		'skus':fields.char('Products',size=1000),
		'generic':fields.char('Generic',size=1000),
		'po_no':fields.char('Purchase Order No',size=100),
		'po_date':fields.date('Purchase Order Date'),
		'attachment':fields.binary('Attachment'),
		#'ops_record_noncomplaint': fields.function(_show_record,relation='res.scheduledjobs',type='one2many',method=True,string='Operations job history'),
		'history_line':fields.one2many('job.history','product_order_id','Job History'),
		'product_invoice_id':fields.one2many('invoice.adhoc.master','sale_order_id','Invoice'),
		'bird_pro':fields.boolean('Bird Pro'),
		'invoiced_amount':fields.float('Invoiced Amount'),
		'document':fields.binary('Attachment'),
		'invoiced_bool':fields.boolean('Invoiced_bool'),
		'done_products':fields.boolean('Done'),
		'bool1':fields.boolean('Bool'),
		'subtotal':fields.float('Subtotal'),
		'product_discount':fields.float('Product Discount %'), 
		'product_discount_amount':fields.float('Product Discount in Amount'),
	}

	_defaults = {
		'company_id': _get_company,
		'created_date': _get_datetime,
		# 'tax_type':'normal',
		'state':'new',
		'user_id':_get_user,
		'type':'Product Order',
	}

	def get_fiscalyear(self,cr,uid,ids,context=None):
		today = datetime.now().date()
		fisc_obj = self.pool.get('account.fiscalyear')
		search_fiscal = fisc_obj.search(cr,uid,[],context=None)
		code=False
		for rec in fisc_obj.browse(cr,uid,search_fiscal):
			if str(today)>=rec.date_start and str(today)<=rec.date_stop:
				code = rec.code
		if code:
			code = code[4:6]
		return code

	def round_off_grand_total(self,cr,uid,ids,grand_total,context=None):
		roundoff_grand_total = grand_total + 0.5
		s = str(roundoff_grand_total)
		dotStart = s.find('.')
		grand_total = int(s[:dotStart])
		return grand_total

	def onchange_select_all_orders(self,cr,uid,ids,select_all_orders,delivery_schedule_ids):
		delivery_schedule_obj = self.pool.get('psd.sales.delivery.schedule')	
		for order_line in delivery_schedule_ids:
			if select_all_orders == True :
				if delivery_schedule_obj.browse(cr,uid,order_line[1]).state == 'new':
					order_line_id = delivery_schedule_obj.write(cr, uid, order_line[1], {'select': True})
			else :
				if delivery_schedule_obj.browse(cr,uid,order_line[1]).state == 'new':
					order_line_id = delivery_schedule_obj.write(cr, uid, order_line[1], {'select': False})
		data = {'delivery_schedule_ids': delivery_schedule_ids}	
		return {'value':data}


	def create_product(self,cr,uid,ids,context=None):
		if context is None: context = {}
		o= self.browse(cr,uid,ids[0])
		main_id = o.id
		if o.expected_delivery_date == False:
			 raise osv.except_osv(_('Warning!'),_("Please Insert Expected Delivery Date!"))

		expected_delivery_date = o.expected_delivery_date
		context.update({'expected_delivery_date':expected_delivery_date,'sale_order_active_id':main_id})
		context = dict(context, active_ids=ids, active_model=self._name)
		print main_id,'===========  main_id'
		print context
		return {
			'name':_("Products List"),
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'scheduled.product.list',
			'res_id': '',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'domain': '[]',
			'context': context,
		}

	# def onchange_tax_type(self,cr,uid,ids,tax_type):
	# 	v={}
	# 	if tax_type == 'composite':
	# 		browse_tax_type = self.browse(cr,uid,tax_type)
	# 		v['no_of_service'] = 1
	# 	else :
	# 		v['no_of_service'] = 0
	# 	return {'value': v}

	def onchange_billing_location_id(self,cr,uid,ids,billing_location_id):
		v={'contact_person':False}
		partner_address_obj = self.pool.get('res.partner.address')
		if billing_location_id:
			partner_rec = partner_address_obj.browse(cr,uid,billing_location_id)
			contact_person = str(partner_rec.first_name)+' '+str(partner_rec.last_name)
			v['contact_person'] = contact_person
		return {'value': v}

	def onchange_bird_pro(self,cr,uid,ids,bird_pro,context=None):
		v={}
		if not bird_pro == False:
			v['install_maintain_charges'] = 0.0
		return {'value':v} 

	def onchange_against_form(self,cr,uid,ids,against_form,context=None):
		v={}
		order_ids = []
		sale_order_line_obj = self.pool.get('psd.sales.product.order.lines')
		cur_rec = self.browse(cr,uid,ids[0])
		product_lines = self.pool.get('psd.sales.product.order.lines')
		product_lines_rec = product_lines.search(cr,uid,[('psd_sales_product_order_lines_id','=',ids[0])])
		grand_total_amount = 0.0
		add_total_amount = 0.0
		total_vat_amount = 0.0
		main_form_total_amount = 0.0
		tax_ids = []
		account_tax = self.pool.get('account.tax')
		tax_line_obj = self.pool.get('tax')
		today_date =datetime.today().date()
		taxes = {}
		for line in product_lines.browse(cr,uid,product_lines_rec):	
			if not line.ordered_quantity or line.ordered_quantity == 0:
				raise osv.except_osv(_('Warning!'),_("Please enter Quantities before calculating Order value!"))
			if not line.product_basic_rate or line.product_basic_rate <= 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper Product Basic rate before calculating quotation value!"))
			if line.product_mrp < 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper Product MRP before calculating quotation value!"))
			if line.exempted:
				raise osv.except_osv(_('Warning!'),_("You are not allowed to select this option as Customer's Location is Exempted!"))
			elif against_form == 'against_form_c':
				account_tax_id1 =self.pool.get('account.tax').search(cr,uid,[('name','ilike','CST 2.0%')])
				tax_id1 = self.pool.get('account.tax').browse(cr,uid,account_tax_id1[0])
				discount_value = line.ordered_quantity * line.product_basic_rate * (line.discount/100)
				vat_amount = (line.ordered_quantity * line.product_basic_rate - discount_value) * (tax_id1.amount)
				vat_amount = round(vat_amount)
				total_amount = discount_value + vat_amount
				line_total_amount = (line.ordered_quantity * line.product_basic_rate) - (line.ordered_quantity * line.product_basic_rate * (line.discount/100)) + vat_amount
				line_total_amount = round(line_total_amount)
				main_total_amount = (line.ordered_quantity * line.product_basic_rate - discount_value)
				main_total_amount = round(main_total_amount)
				total_vat_amount += vat_amount
				main_form_total_amount += main_total_amount
				tax_id = tax_id1.id
				unit_amount = vat_amount
				if not taxes.has_key(tax_id): 
					taxes[tax_id] = [unit_amount]
				else:
					taxes[tax_id].append(unit_amount)  
				order_id = (1, line.id, {'tax_id':account_tax_id1[0],'against_form_check':True,'discounted_amount':discount_value,'tax_amount':vat_amount,'total_amount':line_total_amount})
				order_ids.append(order_id)
			elif against_form == 'against_form_h':
				account_tax_id1 =self.pool.get('account.tax').search(cr,uid,[('name','ilike','VAT 0.0%')])
				tax_id1 = self.pool.get('account.tax').browse(cr,uid,account_tax_id1[0])
				discount_value = line.ordered_quantity * line.product_basic_rate * (line.discount/100)
				vat_amount = (line.ordered_quantity * line.product_basic_rate - discount_value) * (tax_id1.amount)
				vat_amount = round(vat_amount)
				total_amount = discount_value + vat_amount
				line_total_amount = (line.ordered_quantity * line.product_basic_rate) - (line.ordered_quantity * line.product_basic_rate * (line.discount/100)) + vat_amount
				line_total_amount = round(line_total_amount)
				main_total_amount = (line.ordered_quantity * line.product_basic_rate - discount_value)
				main_total_amount = round(main_total_amount)
				total_vat_amount += vat_amount
				main_form_total_amount += main_total_amount
				tax_id = tax_id1.id
				unit_amount = vat_amount
				if not taxes.has_key(tax_id): 
					taxes[tax_id] = [unit_amount]
				else:
					taxes[tax_id].append(unit_amount)  
				order_id = (1, line.id, {'tax_id':account_tax_id1[0],'against_form_check':True,'discounted_amount':discount_value,'tax_amount':vat_amount,'total_amount':line_total_amount})
				order_ids.append(order_id)
			else:
				discount_value = line.ordered_quantity * line.product_basic_rate * (line.discount/100)
				vat_amount = (line.ordered_quantity * line.product_basic_rate - discount_value) * (line.tax_id.amount)
				vat_amount = round(vat_amount)
				total_amount = discount_value + vat_amount
				line_total_amount = (line.ordered_quantity * line.product_basic_rate) - (line.ordered_quantity * line.product_basic_rate * (line.discount/100)) + vat_amount
				line_total_amount = round(line_total_amount)
				main_total_amount = (line.ordered_quantity * line.product_basic_rate - discount_value)
				main_total_amount = round(main_total_amount)
				total_vat_amount += vat_amount
				main_form_total_amount += main_total_amount
				tax_id = line.tax_id.id
				unit_amount = vat_amount
				if not taxes.has_key(tax_id): 
					taxes[tax_id] = [unit_amount]
				else:
					taxes[tax_id].append(unit_amount)  
				order_id = (1, line.id, {'against_form_check':False,'discounted_amount':discount_value,'tax_amount':vat_amount,'total_amount':line_total_amount})
				order_ids.append(order_id)
		taxes = {k:sum(v) for k,v in taxes.items()}  
		for key, value in taxes.iteritems() :
			search_tax = account_tax.search(cr,uid,[('id','=',key)])
			browse_tax = account_tax.browse(cr,uid,search_tax[0])
			value = self.round_off_grand_total(cr,uid,ids,value,context=None)
			for line in cur_rec.tax_one2many:
				taxID = (1, line.id, {'psd_so_id':int(ids[0]),'name':str(browse_tax.name),'account_tax_id':line.account_tax_id.id,'amount':float(value)})
				tax_ids.append(taxID)
		service_tax14 = 0.0
		sb_cess_0_05 = 0.0
		kk_cess_0_50 = 0.0
		account_service_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','service_tax')])
		if account_service_tax:
			service_tax14 = account_tax.browse(cr,uid,account_service_tax[0]).amount
		account_sb_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','swachh_bharat_service')])
		if account_sb_tax:
			sb_cess_0_05 = account_tax.browse(cr,uid,account_sb_tax[0]).amount
		account_kk_tax = account_tax.search(cr,uid,[('effective_from_date','<=',today_date),('effective_to_date','>=',today_date),('select_tax_type','=','krishi_kalyan_service')])
		if account_kk_tax:
			kk_cess_0_50 = account_tax.browse(cr,uid,account_kk_tax[0]).amount
		
		service_tax_value = cur_rec.install_maintain_charges * service_tax14
		sb_tax_value = cur_rec.install_maintain_charges * sb_cess_0_05
		kk_tax_value = cur_rec.install_maintain_charges * kk_cess_0_50
		grand_total = cur_rec.install_maintain_charges + service_tax_value + sb_tax_value + kk_tax_value + total_vat_amount + main_form_total_amount
		grand_total = self.round_off_grand_total(cr,uid,ids,grand_total,context=None)
		v['order_total_amount'] = main_form_total_amount
		v['order_total_vat'] = total_vat_amount
		v['total_amount_paid'] =grand_total                            
		v['install_maintain_charges'] =cur_rec.install_maintain_charges
		v['service_tax'] =service_tax_value
		v['s_b_cess'] =sb_tax_value
		v['k_k_cess'] = kk_tax_value
		v['psd_sales_product_order_lines_ids'] = order_ids
		v['tax_one2many'] = tax_ids
		return {'value': v}

	def cancel(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		total_line=[]
		delivered_list=[]
		cancelled_list =[]
		none_allocated_list =[]
		for schedule_line in rec.delivery_schedule_ids:
			total_line.append(1)
			if schedule_line.state == 'delivered':
				delivered_list.append(1)
			if schedule_line.state == 'cancel':
				cancelled_list.append(1)
		if len(total_line) == len(delivered_list) + len(cancelled_list) and len(delivered_list) > 0:
			self.pool.get('psd.sales.product.order').write(cr,uid,rec.id,{'state':'delivered'})
		# else :
		# 	raise osv.except_osv(_('Warning!'),_("Please cancel remaining orders from Delivery Schedule!"))
		for sale_line in rec.psd_sales_product_order_lines_ids:
			if sale_line.allocated_quantity == 0:
				none_allocated_list.append(1)
		if len(delivered_list)==0:
			self.pool.get('psd.sales.product.order').write(cr,uid,rec.id,{'state':'cancelled'})
		crm_hist_obj = self.pool.get('psd.order.crm.history')
		res_scheduledjobs_obj = self.pool.get('res.scheduledjobs')
		qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(rec.partner_id.id)),('sale_order_id','=',int(rec.id))])
		if qutn_id:			
			crm_hist_obj.write(cr,uid,qutn_id[0],{'status':'cancelled'},context=None)
		job_ids = res_scheduledjobs_obj.search(cr,uid,[('erp_order_no','=',rec.erp_order_no),('state','!=','job_done')])
		if job_ids:
			for job in res_scheduledjobs_obj.browse(cr,uid,job_ids):
				self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'state':'cancel'})
		return True

	def reload_product_quotation(self, cr, uid, ids, context=None):
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_sales', 'view_psd_product_sale_order_branch')
		view_id = view and view[1] or False
		return {
			'name': _('Sales Order-Product'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'psd.sales.product.order',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': ids[0],
		}

	def cancel_order(self,cr,uid,ids,context=None):
		product_request_obj = self.pool.get('product.request')
		request_search_sales_obj = self.pool.get('request.search.sales')
		sales_line_obj = self.pool.get('psd.sales.product.order.lines')
		notes_line_obj = self.pool.get('psd.sales.order.remarks')
		models_data=self.pool.get('ir.model.data')
		tax_line_obj = self.pool.get('tax')
		o = self.browse(cr,uid,ids[0])
		search_product_request = product_request_obj.search(cr,uid,[('product_request_id','=',str(o.request_id))])
		line_ids = []
		notes_ids = []
		tax_ids = []
		if o.psd_sales_product_order_lines_ids:
			for line_id in o.psd_sales_product_order_lines_ids:
				line_ids.append(line_id.id)    
			sales_line_obj.unlink(cr, uid, line_ids, context=context)
		if o.notes_one2many:
			for line_id in o.notes_one2many:
				notes_ids.append(line_id.id)    
			notes_line_obj.unlink(cr, uid, notes_ids, context=context)
		if o.tax_one2many:
			for tax_id in o.tax_one2many:
				tax_ids.append(tax_id.id)    
			tax_line_obj.unlink(cr, uid, tax_ids, context=context)
		if not o.psd_quotation_id: 
			product_request_obj.write(cr,uid,search_product_request[0],{'psd_sales_entry':False})
			self.unlink(cr,uid,ids[0],context=context)
			request_search_sales_id = request_search_sales_obj.create(cr,uid,
				{
					'product_request_ids': [(6, 0, search_product_request)],
					'pushed': False
				},context=context)
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'request_search_sales_form')
			return {
				   'name':'Requests',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'request.search.sales',
				   'res_id':int(request_search_sales_id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   }
		else:
			self.unlink(cr,uid,ids[0],context=context)
			self.pool.get('psd.sales.product.quotation').write(cr,uid,o.psd_quotation_id.id,{'order_created':False},context=None)
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'view_psd_product_quotation_branch')
			return {
				   'name':'Product Quotation',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'psd.sales.product.quotation',
				   'res_id':int(o.psd_quotation_id.id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   }

	def generate_sales_order(self,cr,uid,ids,context=None):
		abc = self.browse(cr,uid,ids)[0]
		print abc
		if abc.quotation_no == None:
			self.calculate_sales_order(cr,uid,ids,context=None)
		product_request_obj = self.pool.get('product.request')
		crm_hist_obj = self.pool.get('sales.product.quotation.history')
		crm_order_hist_obj = self.pool.get('psd.order.crm.history')
		crm_lead_obj = self.pool.get('crm.lead')
		seq = self.pool.get('ir.sequence').get(cr, uid, 'psd.sales.product.order')
		code = self.get_fiscalyear(cr,uid,ids,context=None)
		cur_rec = self.browse(cr,uid,ids[0])
		# if not cur_rec.document:
		# 	raise osv.except_osv(_('Alert!'),("Attach File before generating the Order!"))
		today_date = datetime.now().date()
		year1 = today_date.strftime('%y')
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		if month > 3:
			start_year = year
			end_year = year+1
			year1 = int(year1)+1
		else:
			start_year = year-1
			end_year = year
			year1 = int(year1)
		financial_year =str(year1-1)+str(year1) 
		financial_start_date = str(start_year)+'-04-01'
		financial_end_date = str(end_year)+'-03-31'
		erp_order_no = str(cur_rec.company_id.pcof_key)+str(cur_rec.company_id.sale_order_id)+financial_year+str(seq)
		sale_product_req_data = self.browse(cr, uid, ids[0])
		search_product_request = product_request_obj.search(cr,uid,[('product_request_id','=',str(sale_product_req_data.request_id))])
		for line in sale_product_req_data.psd_sales_product_order_lines_ids:
			self.pool.get('psd.sales.product.order.lines').write(cr,uid,line.id,{'erp_order_no_ref':erp_order_no})
		res = self.write(cr,uid,ids,{	
									'state':'ordered',
									'erp_order_no':erp_order_no,
									'erp_order_date':datetime.today()})
		if sale_product_req_data.psd_quotation_id:
			self.pool.get('psd.sales.product.quotation').write(cr,uid,sale_product_req_data.psd_quotation_id.id,{'state':'ordered'})
			qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(sale_product_req_data.psd_quotation_id.partner_id.id)),('sale_quotation_id','=',int(sale_product_req_data.psd_quotation_id.id))])
			if qutn_id:			
				crm_history_values = {'status':'ordered'}
				crm_hist_obj.write(cr,uid,qutn_id[0],crm_history_values,context=None)
		product_list = []
		generic_name = []
		for line in cur_rec.psd_sales_product_order_lines_ids:
			# if not line.sku_name_id.name in product_list:
			# 	product_list.append(line.sku_name_id.name)
			if not line.product_name_id.name in generic_name:
				generic_name.append(line.product_name_id.name)
		products =', '.join(map(str, product_list))
		generic =', '.join(map(str, generic_name))
		self.write(cr,uid,ids,{'generic':generic,'skus':products})
		ord_id = crm_order_hist_obj.search(cr,uid,[('partner_id','=',int(cur_rec.partner_id.id)),('sale_order_id','=',int(cur_rec.id))])
		if ord_id:
			for m in ord_id:
				crm_order_hist_obj.unlink(cr,uid,m,context=None)
		crm_history_values = { 	'partner_id':cur_rec.partner_id.id,
								'sale_order_id':cur_rec.id,
								'order_id':erp_order_no,
								'order_date':datetime.now(),
								'order_period':str('-'),
								'order_type':cur_rec.type,
								'sku_name':products,
								'request_id':cur_rec.request_id,
								'order_amount':cur_rec.total_amount_paid,
								'status':'ordered',
								'pse':cur_rec.pse_id.concate_name,
							}
		crm_order_hist_obj.create(cr,uid,crm_history_values,context=None)
		product_request_obj.write(cr,uid,search_product_request[0],{'state':'closed','closed_date':datetime.now()})
		crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', str(cur_rec.request_id))], context=context)
		for crm_id in crm_ids:
			crm_lead_obj.write(cr, uid, crm_id, {'state':'closed'}, context=context)
		return res

	def calculate_sales_order(self,cr,uid,ids,context=None):
		cur_rec = self.browse(cr,uid,ids[0])
		# if cur_rec.quotation_no:
		# 	raise osv.except_osv(_('Alert!'),_("Tax is already calculated.\n Kindly generate the order"))
		if not cur_rec.psd_sales_product_order_lines_ids:
			raise osv.except_osv(_('Warning!'),_("No product lines defined!"))
		tax_obj = self.pool.get('tax')
		product_lines = self.pool.get('psd.sales.product.order.lines')
		psd_sales_order_obj = self.pool.get('psd.sales.product.order')
		crm_hist_obj = self.pool.get('psd.order.crm.history')
		partner_address_obj = self.pool.get('res.partner.address')
		product_lines_rec = product_lines.search(cr,uid,[('psd_sales_product_order_lines_id','=',ids[0])])
		grand_total_amount = basic_amount= 0.0
		main_form_total_amount = 0.0
		install_maintain_charges = 0.0
		tax_value = 0.0
		product_basic_rate = sgst_amount = cgst_amount = igst_amount = gst_total =sgst_rate=cgst_rate=igst_rate= 0.0
		tax_ids = []
		account_tax = self.pool.get('account.tax')
		tax_line_obj = self.pool.get('tax')
		today_date =datetime.today().date()
		if cur_rec.tax_one2many:
			for tax_line_id in cur_rec.tax_one2many:
				tax_ids.append(tax_line_id.id)    
			tax_line_obj.unlink(cr, uid, tax_ids, context=context)
		taxes = {}
		check_lines = []

		sgst_tax=account_tax.search(cr,uid,[('name','=','SGST')])[0]
		cgst_tax=account_tax.search(cr,uid,[('name','=','CGST')])[0]
		igst_tax=account_tax.search(cr,uid,[('name','=','IGST')])[0]

		company_id = cur_rec.company_id.state_id.id
		partner_location_addr = cur_rec.delivery_location_id.state_id.id
		if not partner_location_addr:
			raise osv.except_osv(('Warning!'),('Please update the  state of the  customer'))

		additional_amount = additional_basic_amount = 0.0
		
		for line in product_lines.browse(cr,uid,product_lines_rec):
			# tax_id = line.tax_id
			product_basic_rate = line.product_basic_rate
			generics=line.product_name_id.id
			tax_rate =  line.product_name_id.product_tax.id
			tax_amount = line.product_name_id.product_tax.amount
			tax_name = line.product_name_id.product_tax.name
			# skus=line.sku_name_id.id
			# combo=tuple([generics]+[skus])
			combo = generics
			if combo in check_lines:
				raise osv.except_osv(('Invalid Combination!'),('Same Product lines are not allowed!'))
			else:
				check_lines.append(combo)
			print check_lines
			if not line.allocated_quantity or line.allocated_quantity == 0:
				raise osv.except_osv(_('Warning!'),_("Please enter Quantities before calculating Order value!"))
			# if not line.tax_id:
			# 	raise osv.except_osv(_('Warning!'),_("Please select proper TAX before calculating Order value!"))
			if not line.product_basic_rate or line.product_basic_rate <= 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper Product Basic rate before calculating quotation value!"))
			if line.product_mrp < 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper Product MRP before calculating quotation value!"))
			if not line.discount:
				total_basic_amount = product_basic_rate * line.allocated_quantity
				product_lines.write(cr,uid,line.id,{'discounted_amount':total_basic_amount})
				cr.commit()
			else:
				additional_amount = product_basic_rate + line.discount
				additional_basic_amount = additional_amount * line.allocated_quantity
				total_basic_amount = additional_basic_amount
				product_lines.write(cr,uid,line.id,{'discounted_amount':total_basic_amount})
				cr.commit()	
			if company_id == partner_location_addr:
				print "aaaaaaaaaa"
				if line.exempted:
					print "INTRA exempted"
				else:
					if tax_rate:
						# print total_basic_amount
						# mm
						cgst_rate = sgst_rate = tax_amount/2
						cgst_amount = sgst_amount = (tax_amount * total_basic_amount)/2
						cgst_tax_name = account_tax.browse(cr,uid,cgst_tax).name
						sgst_tax_name = account_tax.browse(cr,uid,sgst_tax).name
						gst_total = cgst_amount + sgst_amount

						product_lines.write(cr,uid,line.id,{'sgst_rate':str(sgst_rate*100)+'%','cgst_rate':str(cgst_rate*100)+'%','sgst_amount':sgst_amount,'cgst_amount':cgst_amount,'tax_amount':gst_total,'total_amount':gst_total+total_basic_amount})
						cr.commit()
			else:
				print "bbbbbbbbbbb"
				if line.exempted:
					print "INTER exempted"
				else:
					if tax_rate:
						igst_rate = tax_amount
						igst_amount = tax_amount * total_basic_amount
						igst_tax_name = account_tax.browse(cr,uid,igst_tax).name
						gst_total = igst_amount
						product_lines.write(cr,uid,line.id,{'igst_rate':str(igst_rate*100)+'%','igst_amount':igst_amount,'tax_amount':gst_total,'total_amount':gst_total+total_basic_amount})
		print line.psd_sales_product_order_lines_id
		cr.execute('select sum(sgst_amount) from psd_sales_product_order_lines where psd_sales_product_order_lines_id = %s',(line.psd_sales_product_order_lines_id.id,))
		sgst_amount = cr.fetchone()[0]
		cr.execute('select sum(cgst_amount) from psd_sales_product_order_lines where psd_sales_product_order_lines_id = %s',(line.psd_sales_product_order_lines_id.id,))
		cgst_amount = cr.fetchone()[0]
		cr.execute('select sum(igst_amount) from psd_sales_product_order_lines where psd_sales_product_order_lines_id = %s',(line.psd_sales_product_order_lines_id.id,))
		igst_amount = cr.fetchone()[0]
		cr.execute('select sum(discounted_amount) from psd_sales_product_order_lines where psd_sales_product_order_lines_id = %s',(line.psd_sales_product_order_lines_id.id,))
		basic_amount = cr.fetchone()[0]
		basic_amount = round(basic_amount)
		cr.execute('select sum(total_amount) from psd_sales_product_order_lines where psd_sales_product_order_lines_id = %s',(line.psd_sales_product_order_lines_id.id,))
		total_amount = cr.fetchone()[0]
		total_amount = round(total_amount)
		psd_sales_order_obj.write(cr,uid,cur_rec.id,{'order_total_amount':basic_amount,'total_amount_paid':total_amount,'subtotal':total_amount})
		cr.commit()
		#calculate product prodfit

		cr.execute('select sum(allocated_quantity*product_basic_rate) from psd_sales_product_order_lines where psd_sales_product_order_lines_id = %s',(line.psd_sales_product_order_lines_id.id,))
		basic_rate = cr.fetchone()[0]
		print basic_rate,'=========basic'
		grand_amt = total_amount
		if grand_amt:
			if cur_rec.product_discount:
				for l in product_lines.browse(cr,uid,product_lines_rec):
					if not l.discount:
						raise osv.except_osv(('Alert!'),('You cannot give discount with additional amount as 0'))

				prod_disc = cur_rec.product_discount if cur_rec.product_discount else 0.0
				prod_disc_amt = (grand_amt * prod_disc)/100

				grand_tot = grand_amt - prod_disc_amt
				print grand_tot,'grand tot'
				if grand_tot < basic_rate:
					raise osv.except_osv(('Alert!'),('Discounted amount should not be greater than Basic amount!'))
				self.write(cr,uid,ids,{
						'product_discount_amount':prod_disc_amt,
						'total_amount_paid':grand_tot,
					})

			else:
				self.write(cr,uid,ids,{
						'product_discount_amount':0.00
						
					})

		if  company_id == partner_location_addr:
			tax_line_obj.create(cr,uid,{'psd_so_id':int(ids[0]),'account_tax_id':cgst_tax,'name':cgst_tax_name,'amount':cgst_amount},context=None)	
			cr.commit()
			tax_line_obj.create(cr,uid,{'psd_so_id':int(ids[0]),'account_tax_id':sgst_tax,'name':sgst_tax_name,'amount':sgst_amount},context=None)					
			cr.commit()
		else:
			tax_line_obj.create(cr,uid,{'psd_so_id':int(ids[0]),'account_tax_id':igst_tax,'name':igst_tax_name,'amount':igst_amount},context=None)
			cr.commit()

		if cur_rec.tax_one2many:
			tax_id = tax_obj.search(cr,uid,[('psd_so_id','=',ids[0])])[0]
			browse_rec = tax_obj.browse(cr,uid,tax_id)
			tax_value += browse_rec.amount

		if cur_rec.bird_pro:
			if cur_rec.install_maintain_charges==0.0:
				raise osv.except_osv(('Alert'),('Please enter Installation Charges'))
			if cur_rec.install_maintain_charges!=0.0:
				install_maintain_charges = cur_rec.install_maintain_charges
				grand_total = cur_rec.install_maintain_charges + cur_rec.order_total_amount
		else:
			grand_total = cur_rec.order_total_amount

		grand_total = self.round_off_grand_total(cr,uid,ids,grand_total,context=None)
		# print grand_total
		# n
		self.write(cr,uid,cur_rec.id,{
								# 'total_amount_paid':grand_total,                            
								# 'install_maintain_charges':cur_rec.install_maintain_charges,
								'state':'pending'})
		cr.commit()
		product_list = []
		generic_name = []
		for line in product_lines.browse(cr,uid,product_lines_rec):
			# if not line.sku_name_id.name in product_list:
				# product_list.append(line.sku_name_id.name)
			if not line.product_name_id.name in generic_name:
				generic_name.append(line.product_name_id.name)
		products =', '.join(map(str, product_list))
		generic =', '.join(map(str, generic_name))
		self.write(cr,uid,ids,{'generic':generic,'skus':products}) 
		ord_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(cur_rec.partner_id.id)),('sale_order_id','=',int(cur_rec.id))])
		if ord_id:
			for m in ord_id:
				crm_hist_obj.unlink(cr,uid,m,context=None)
		crm_history_values = { 	'partner_id':cur_rec.partner_id.id,
								'sale_order_id':cur_rec.id,
								'order_id':cur_rec.erp_order_no,
								'order_date':cur_rec.erp_order_date,
								'order_period':str('-'),
								'order_type':cur_rec.type,
								'sku_name':products,
								'request_id':cur_rec.request_id,
								'order_amount':grand_total,
								'status':'pending',
								'pse':cur_rec.pse_id.concate_name,
							}
		crm_hist_obj.create(cr,uid,crm_history_values,context=None)
		return True


	def move_to_stock(self,cr,uid,ids,context=None):
		psd_sales_delivery_schedule_obj = self.pool.get('psd.sales.delivery.schedule')
		scheduled_product_list_line_obj = self.pool.get('scheduled.product.list.line')
		product_transfer_obj =self.pool.get('product.transfer')
		stock_transfer_obj = self.pool.get('stock.transfer')
		tax_line_obj = self.pool.get('tax')
		psd_sale_order_obj = self.pool.get('psd.sales.product.order')
		today_date =datetime.today().date()
		o = self.browse(cr,uid,ids[0])

		sel_rec_ids = psd_sales_delivery_schedule_obj.search(cr,uid,[('sale_order_id','=',o.id),('state','=','new'),('select','=',True)])
		if not sel_rec_ids:
			raise osv.except_osv(_('Alert!'),_("Please select atleast one record!"))

		main_id = o.id
		addrs_items = []
		track_equipment_list = []
		stock_create_id = False
		address = ''
		if o.delivery_location_id.apartment not in [' ',False,None]:
			addrs_items.append(o.delivery_location_id.apartment)
		if o.delivery_location_id.building not in [' ',False,None]:
			addrs_items.append(o.delivery_location_id.building)
		if o.delivery_location_id.sub_area not in [' ',False,None]:
			addrs_items.append(o.delivery_location_id.sub_area)
		if o.delivery_location_id.landmark not in [' ',False,None]:
			addrs_items.append(o.delivery_location_id.landmark)
		if o.delivery_location_id.street not in [' ',False,None]:
			addrs_items.append(o.delivery_location_id.street)
		if o.delivery_location_id.city_id:
			addrs_items.append(o.delivery_location_id.city_id.name1)
		if o.delivery_location_id.district:
			addrs_items.append(o.delivery_location_id.district.name)
		if o.delivery_location_id.tehsil:
			addrs_items.append(o.delivery_location_id.tehsil.name)
		if o.delivery_location_id.state_id:
			addrs_items.append(o.delivery_location_id.state_id.name)
		if o.delivery_location_id.zip not in [' ',False,None]:
			addrs_items.append(o.delivery_location_id.zip)
		if len(addrs_items) > 0:
			last_item = addrs_items[-1]
			for item in addrs_items:
				if item!=last_item:
					address = address+item+','+' '
				if item==last_item:
					address = address+item	
		search_ids = psd_sales_delivery_schedule_obj.search(cr,uid,[('sale_order_id','=',main_id),('state','=','new'),('select','=',True)])
		browse_ids = psd_sales_delivery_schedule_obj.browse(cr,uid,search_ids)
		for list_ids in browse_ids:
			if list_ids.select == True and list_ids.state == 'new' and list_ids.delivery_order_no == False and list_ids.delivery_order_date == False:
				list_id = list_ids.id
				despatcher_id = list_ids.despatcher.id
				if list_ids.godown.name == 'NSD Bhiwandi':
					is_nsd_bhiwandi = True
				else :
					is_nsd_bhiwandi = False

				stock_create_id = stock_transfer_obj.create(cr,uid,{
					'psd_order_management':True,
					'customer_name':o.name,
					'delivery_location':despatcher_id,
					'status':'draft',
					'delivery_address':address,
					'billing_location':address,
					'billing_location_id':o.billing_location_id.id,
					'stock_transfer_date_new':today_date,
					'delivery_type':'sales_delivery',
					'sale_order_no':o.erp_order_no,
					'sale_order_date':o.erp_order_date,
					#######additional field added on the delivery order added by shreyas 
					'expected_delivery_date':o.expected_delivery_date,
					'pse':o.pse_id.id,
					'web_order_number':o.web_order_no,
					'web_order_date':o.web_order_date,
					'against_free_replacement':o.against_free_replacement,
					'against_form': o.against_form,
					'psd_contact_person': o.contact_person,
					#'total_amount':o.total_amount_paid,
					'partner_id':o.partner_id.id,
					'delivery_loc_state':o.delivery_location_id.state_id.name,
					#'source':o.branch_name.id,
					'branch_name':list_ids.godown.id,
					'is_nsd_bhiwandi':is_nsd_bhiwandi,
					'po_no':o.po_no,
					'po_date':o.po_date,
					# 'basic_charge':o.order_total_amount,
					# 'order_total_vat':o.order_total_vat,
					'bird_pro':list_ids.bird_pro,
					'bird_pro_charge':list_ids.bird_pro_charge,
					'total_st':list_ids.total_st,
					'product_cost':list_ids.product_cost,
					'total_vat':list_ids.total_vat,
					'total_amount':list_ids.amount,
					#'delivered_by':o.uid.company_id.id,
					})

				search_line_ids = scheduled_product_list_line_obj.search(cr,uid,[('scheduled_delivery_list_id','=',list_id)])
				browse_line_ids = scheduled_product_list_line_obj.browse(cr,uid,search_line_ids)
				for list_line_ids in browse_line_ids:
					sku_name_id = list_line_ids.product_name_id.id
					quantity = list_line_ids.allocated_quantity
					ordered_quantity = list_line_ids.ordered_quantity
					extended_warranty = list_line_ids.extended_warranty
					allocated_quantity = list_line_ids.allocated_quantity
					discount = list_line_ids.discount

					search_stock=self.pool.get('product.product').browse(cr,uid,sku_name_id).quantity_available
					print search_stock

					if search_stock < list_line_ids.allocated_quantity:
						raise osv.except_osv(('Alert!'),('Ordered quantity is not available for Product %s')%(list_line_ids.product_name_id.name_template))

					product_data = {
						'product_name':sku_name_id,
						'quantity':0,
						#'available_quantity':ordered_quantity,
						'qty_indent':allocated_quantity,
						'prod_id':stock_create_id,
						'psd_order_management':True,
						'generic_id':list_line_ids.product_name_id.generic_name.id,
						'rate':list_line_ids.product_basic_rate,
						'extended_warranty':extended_warranty,
						'discount':0,
						'discounted_price':list_line_ids.discounted_price,
						'discounted_amount':list_line_ids.discounted_amount,
						'tax_id':list_line_ids.tax_id.id,
						'tax_amount':list_line_ids.tax_amount,
						'total_amount':list_line_ids.total_amount,
						'amount':list_line_ids.total_amount,
						'product_uom':list_line_ids.product_name_id.product_tmpl_id.local_uom_id.id,
						'product_code':list_line_ids.product_name_id.default_code,
						# 'product_category':list_line_ids.sku_name_id.product_tmpl_id.categ_id.id,
						'is_qty_allocated':quantity,
						'godown':list_ids.godown.id,
						'specification':list_line_ids.specification,
						'additional_amt':list_line_ids.discount,
						}
					if list_line_ids.product_name_id.type_product == 'track_equipment':
						product_data['is_track_equipment']=True
						track_equipment_list.append(True)
					else:
						product_data['is_track_equipment']=False
						track_equipment_list.append(False)
					product_transfer_obj.create(cr,uid,product_data)
					# print stock_create_id
					# nn
					new_transfer_obj =stock_transfer_obj.browse(cr,uid,stock_create_id)
					psd_sales_delivery_schedule_obj.write(cr,uid,list_ids.id,{
						'delivery_order_no':new_transfer_obj.stock_transfer_no,
						'delivery_order_date':today_date,
						'state':'draft'})
			if list_ids.tax_one2many:
				for tax_line_id in list_ids.tax_one2many:  
					tax_line_values ={
					'stock_transfer_tax_id': int(stock_create_id),
					'name': tax_line_id.name,
					'account_tax_id':tax_line_id.account_tax_id.id,
					'amount':tax_line_id.amount,
					}
					res_tax_order_line_create= tax_line_obj.create(cr,uid,tax_line_values)
		if True in track_equipment_list:
			stock_transfer_obj.write(cr,uid,stock_create_id,{'is_track_equipment':True})
		active_id = context.get('active_id')
		sale_order_obj = psd_sale_order_obj.browse(cr,uid,context.get('active_id'))
		lenght1 = len(sale_order_obj.delivery_schedule_ids)
		ordered_list = []
		total_sale_order_line_list =[]
		all_allocated_list=[]
		amount = 0.0
		for each in sale_order_obj.delivery_schedule_ids:
			amount=amount+each.amount
			if each.state == 'draft':
				ordered_list.append(1)
		for sale in sale_order_obj.psd_sales_product_order_lines_ids:
			total_sale_order_line_list.append(1)
			if sale.allocated_quantity == sale.ordered_quantity:
				all_allocated_list.append(1)
		if len(total_sale_order_line_list) != len(all_allocated_list):
			psd_sale_order_obj.write(cr,uid,sale_order_obj.id,{'state':'partial_delivery_scheduled'})
		if lenght1 == len(ordered_list) and amount == sale_order_obj.total_amount_paid :
			psd_sale_order_obj.write(cr,uid,sale_order_obj.id,{'state':'delivery_scheduled'})
		
		state_list = []
		abc = psd_sales_delivery_schedule_obj.search(cr,uid,[('sale_order_id','=',o.id)])
		for each in psd_sales_delivery_schedule_obj.browse(cr,uid,abc):
			state = each.state
			state_list.append(state)

		if o.done_products == True and 'new' not in state_list:
			self.write(cr,uid,o.id,{'bool1':True})
			cr.commit()
		else:
			self.write(cr,uid,o.id,{'bool1':False})
			cr.commit()

		return True

	#process order on push to invoice button in psd_sales itself
	def psd_process_order(self,cr,uid,ids,context=None): 
		o = self.browse(cr,uid,ids[0])
		order_no = ''
		# if not (o.select_all_orders or o.delivery_schedule_ids[0].select):
		# 	raise osv.except_osv(_('Alert!'),_("Please select atleast one record!"))
		stock_transfer_obj = self.pool.get('stock.transfer')

		if len(o.delivery_schedule_ids) < 1:
			order_no = o.delivery_schedule_ids[0].delivery_order_no
		else:
			for each in o.delivery_schedule_ids:
				if each.select == True:
					if each.state == 'invoiced':
						pass
					else:
						order_no  = each.delivery_order_no
						order_no_sch = stock_transfer_obj.search(cr,uid,[('stock_transfer_no','=',order_no)])
						if order_no_sch:
							s_ids = order_no_sch
							stock_transfer_obj.nsd_prepare_packlist(cr,uid,s_ids,context=None)
							stock_transfer_obj.nsd_ready_to_dispatch(cr,uid,s_ids,context=None)
							stock_transfer_obj.psd_create_invoice(cr,uid,s_ids,context=None)
				else:
					pass
		if order_no:
			order_no_sch = stock_transfer_obj.search(cr,uid,[('stock_transfer_no','=',order_no)])
		else:
			raise osv.except_osv(_('Alert!'),_("Invoice for this line/order is already generated!!"))
		# if order_no_sch:
		# 	s_ids = order_no_sch
		# 	stock_transfer_obj.nsd_prepare_packlist(cr,uid,s_ids,context=None)
		# 	stock_transfer_obj.nsd_ready_to_dispatch(cr,uid,s_ids,context=None)
		# 	stock_transfer_obj.psd_create_invoice(cr,uid,s_ids,context=None)
		if o.bool1 == False:
			self.write(cr,uid,o.id,{'invoiced_bool':False})
			cr.commit()
		else:
			self.write(cr,uid,o.id,{'invoiced_bool':True})
			cr.commit()
			self.write(cr,uid,o.id,{'state':'delivered'})
			cr.commit()
		return True
	

	# #### Added by nitin 18-8-2016
	def psd_post_notes(self,cr,uid,ids,context=None): 
		date=datetime.now()
		for o in self.browse(cr,uid,ids):
			source = o.company_id.id
			user_name=self.pool.get('res.users').browse(cr, uid, uid).name
			if o.notes:
				self.pool.get('psd.sales.order.remarks').create(cr,uid,{'sale_order_id':o.id,
											'user_name':user_name,
											'date':date,
											'source':source,
											'name':'General - '+o.notes,
											'state':o.state})
				self.write(cr,uid,ids,{'notes':None})
	# ########## End ##################
		return True

psd_sales_product_order()


class psd_sales_product_order_lines(osv.osv):
	_name = 'psd.sales.product.order.lines'
	_rec_name = 'ordered_quantity'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'psd_sales_product_order_lines_id': fields.many2one('psd.sales.product.order','PSD Sales Product Order'),
		'exempted':fields.boolean('Exempted'),
		'track_equipment':fields.boolean('Track Equipment'),
		'erp_order_no_ref':fields.char('ERP Order No Ref',size=56),
		# 'product_name_id': fields.many2one('product.generic.name','Product Name'),
		'product_name_id':fields.many2one('product.product','Product Name'),
		# 'sku_name_id':fields.many2one('product.product','SKU Name',domain="[('generic_name','=',product_name_id)]"),
		'extended_warranty':fields.selection([
							('6','6 Months'),
							('12','12 Months'),
							('18','18 Months'),
							('24','24 Months'),
							('36','36 Months'),
							('48','48 Months'),
							('60','60 Months')],'Extended Warranty'),
		'ordered_quantity':fields.integer('Ordered Quantity'),
		'allocated_quantity':fields.integer('Allocated Quantity'),
		'product_uom_id':fields.many2one('product.uom','UOM'),
		'product_mrp':fields.float('MRP'),
		'product_basic_rate':fields.float('Basic Rate'),
		'discount':fields.float('Disc %'),
		'discounted_value':fields.float('Discounted Value'),
		'discounted_price':fields.float('Discounted Price'),
		'discounted_amount':fields.float(string='Disc Amt'),
		# 'tax_id':fields.many2one('account.tax','VAT %',domain="[('description','=','vat'),('active','=',True)]"),
		'tax_amount':fields.float('Tax Amt'),
		'total_amount':fields.float('Total Amount'),
		'against_form_check':fields.boolean('AgainstForm'),
		#########added for the batch number and the manufaturing date shreyas
		'batch_number': fields.many2one('res.batchnumber','Batch No.'),
		'manufacturing_date': fields.date('Manufaturing Date'),
		'notes_one2many': fields.one2many('psd.product.transfer.comment.line','sale_order_line_id','Notes'),
		'msg_check_read':fields.boolean('msg'),
		'msg_check_unread':fields.boolean('msg'),
		'specification': fields.char('Specification',size=500),
		##################### SSD PSD Merge
		'hsn_code':fields.char('HSN Code',size=10),
		'cgst_rate':fields.char('CSGT Rate',size=10),
		'sgst_rate':fields.char('SGST Rate',size=10),
		'igst_rate':fields.char('IGST Rate',size=10),
		'cgst_amount':fields.float('CGST Amount'),
		'sgst_amount':fields.float('SGST Amount'),
		'igst_amount':fields.float('IGST Amount'),
		'done_products':fields.boolean('Done'),

}
	_defaults = {
		'company_id': _get_company
	}

	# def onchange_product_name_id(self,cr,uid,ids,product_name_id,exempted,company_id,context=None):
	# 	data = {'product_uom_id':False,'tax_id':False,}
	# 	product_obj = self.pool.get('product.product')
	# 	generic_obj = self.pool.get('product.generic.name')
	# 	psd_sales_order_obj =self.pool.get('psd.sales.product.order')
	# 	company_state = self.pool.get('res.company').browse(cr,uid,company_id).state_id.id
	# 	cur_rec_id = context.get('active_id')
	# 	delivery_location_state = psd_sales_order_obj.browse(cr,uid,cur_rec_id).delivery_location_id.state_id.id
	# 	tax_id_list =[]
	# 	search_tax_id = False		
	# 	if product_name_id:
	# 		product_ids = product_obj.search(cr, uid, [('name_template','=',product_name_id)], context=context)
	# 		if product_ids[0]:
	# 			product_data = product_obj.browse(cr,uid,product_ids[0])
	# 			product_uom_id = product_data.product_tmpl_id.local_uom_id.id
	# 			if product_uom_id:
	# 				data.update({'product_uom_id': product_uom_id})
	# 	if company_state == delivery_location_state:
	# 		if exempted:
	# 			search_tax_id = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Exempted')])
	# 			tax_id_list.append(search_tax_id[0])
	# 		else:
	# 			check_group_name = generic_obj.browse(cr,uid,product_name_id)
	# 			if check_group_name.product_group_id:
	# 				for each in check_group_name.product_group_id:
	# 					search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',each.tax_name.id),('description','=','vat')])
	# 					if search_tax_id:
	# 						tax_id_list.append(search_tax_id[0])
	# 	else:
	# 		if exempted:
	# 			search_tax_id = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Exempted')])
	# 			tax_id_list.append(search_tax_id[0])
	# 		else:
	# 			check_group_name = generic_obj.browse(cr,uid,product_name_id)
	# 			if check_group_name.product_group_id:
	# 				for each in check_group_name.product_group_id:
	# 					search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',each.tax_name.id),('description','=','cst')])
	# 					if search_tax_id:
	# 						tax_id_list.append(search_tax_id[0])
	# 	if tax_id_list:
	# 		data.update({'tax_id':tax_id_list[0]})
	# 	return {'value':data}

	# def create(self,cr,uid,vals,context=None):
	# 	if vals.get('product_name_id'):
	# 		raise osv.except_osv(('Alert!'),('You cannot add products after your request has been processed. Create a new request for new products!'))
	# 	new_id=super(psd_sales_product_order_lines,self).create(cr,uid,vals,context=context)
	# 	return new_id

	

	def onchange_sku_name_id(self,cr,uid,ids,product_name_id,sku_name_id,context=None):
		res = {'product_basic_rate':False,'product_mrp':False,}
		first_tax_val = False
		tax_name = False
		search_tax_id = False
		partner_obj = self.pool.get('res.partner')
		product_req_data = self.browse(cr, uid, ids[0])
		customer_type = partner_obj.browse(cr,uid,product_req_data.psd_sales_product_order_lines_id.partner_id.id).customer_type
		sku_data = self.pool.get('product.product').browse(cr,uid,sku_name_id)
		product_group_id = sku_data.generic_name.product_group_id  
		if sku_name_id:
			product_obj = self.pool.get('product.product')
			search_product = product_obj.search(cr,uid,[('id','=',sku_name_id)])
			product_name = product_obj.browse(cr,uid,search_product[0])
			if product_name.batch_type == 'non_applicable':
				search_rec = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name.id),('batch_no','=','NA')])
			else:
				search_rec = self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name.id),('batch_no','!=',False)])
			if len(search_rec) > 1:
				dict1= {}
				manufacture_date = []
				for val in self.pool.get('res.batchnumber').browse(cr,uid,search_rec):
					if val.distributor != 0.00 and val.mrp != 0.00:
							distributor =  val.distributor
							mrp = val.mrp 
							manufacture_dt = val.manufacturing_date
							manufacture_date.append([manufacture_dt,val.id])
				manufacture_date.sort()
				rec_search = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',manufacture_date[-1][1]),('manufacturing_date','=',manufacture_date[-1][0]),('name','=',product_name.id)])
				rec1 = self.pool.get('res.batchnumber').browse(cr,uid,rec_search[0])
				res['product_basic_rate'] = rec1.distributor
				res['product_mrp'] = rec1.mrp
				product_dealer=rec1.mrp
				#############changes added for the new fields shreyas
				res['batch_number'] =rec1.id
				res['manufacturing_date'] =rec1.manufacturing_date
			if len(search_rec) == 1:
				x = self.pool.get('res.batchnumber').browse(cr,uid,search_rec[0])
				res['product_basic_rate'] = x.distributor
				res['product_mrp'] = x.mrp
				product_dealer=x.mrp
				#############changes added for the new fields shreyas
				res['batch_number'] =x.id
				res['manufacturing_date'] =x.manufacturing_date
			if customer_type=='dealer':
				res['product_mrp']=product_dealer
			if customer_type=='distributor':
				res['product_mrp']=res['product_basic_rate']
			if customer_type=='customer':
				res['product_mrp']=res['product_mrp']
			return {'value':res}

	# ##################### Added by nitin 18-8-2016	
	def show_notes(self,cr,uid,ids,context=None):
		for i in self.browse(cr,uid,ids):
			form_id = i.id
			if i.msg_check_unread:
				self.write(cr,uid,[form_id],{'msg_check_read':True,'msg_check_unread':False})
			return {
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'psd.sales.product.order.lines',
					'res_id': int(form_id),
					'view_id': False,
					'type': 'ir.actions.act_window',
					'target': 'new',
					}

	def save_notes(self,cr,uid,ids,context=None):
		for i in self.browse(cr,uid,ids):
			form_id = i.id
			source = i.company_id.id
			user_name=self.pool.get('res.users').browse(cr, uid, uid).name
			date=datetime.now()
			if i.notes_one2many:
				self.write(cr,uid,[form_id],{'msg_check_read':True,'msg_check_unread':False})
				for note in i.notes_one2many:
					self.pool.get('psd.sales.order.remarks').create(cr,uid,{'sale_order_id':i.psd_sales_product_order_lines_id.id,
												'user_name':user_name,
												'source':source,
												'name':note.comment,
												'date':date,
												'state':i.psd_sales_product_order_lines_id.state,
												})
		return {'type': 'ir.actions.act_window_close'}
	# ################## End 18-8-2016

psd_sales_product_order_lines()

#object for Delivery scheduled tab
class psd_sales_delivery_schedule(osv.osv):
	_name = "psd.sales.delivery.schedule"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	# def update_quantity(self,cr,uid,ids,context=None):
	# 	curr_obj = self.browse(cr,uid,ids[0])
	# 	psd_sales_product_order_lines_obj =self.pool.get('psd.sales.product.order.lines')
	# 	scheduled_product_list_line_obj = self.pool.get('scheduled.product.list.line')
		

	# 	for line in curr_obj.scheduled_delivery_list:
	# 		allocated_quantity = line.allocated_quantity
	# 		ordered_quantity = line.ordered_quantity
	# 		product_basic_rate =  line.product_basic_rate
	# 		sale_allocated_quantity = line.sale_order_line_id.allocated_quantity
	# 		sale_write_allocated_quantity = sale_allocated_quantity+allocated_quantity
	# 		sale_order_line_id = line.sale_order_line_id.id
	# 		discount_value = allocated_quantity * product_basic_rate * (line.discount/100)
	# 		tax_amount = (allocated_quantity * product_basic_rate - discount_value) * (line.tax_id.amount)
	# 		new_total_amount = (allocated_quantity * product_basic_rate) - (allocated_quantity* product_basic_rate * (line.discount/100)) + tax_amount
	# 		scheduled_product_list_line_obj.write(cr,uid,line.id,{'discounted_amount':discount_value,'tax_amount':tax_amount,'total_amount':new_total_amount})
	# 		psd_sales_product_order_lines_obj.write(cr,uid,sale_order_line_id,{'allocated_quantity':sale_write_allocated_quantity})

	# 		if allocated_quantity < 0:
	# 			raise osv.except_osv(_('Warning!'),_("Allocated Quantity can not be negative!"))
	# 		if allocated_quantity > ordered_quantity:
	# 			raise osv.except_osv(_('Warning!'),_("Allocated Quantity can not be greater than Orderd Quantity!"))
	# 		order_line_obj = self.pool.get('psd.sales.product.order.lines').browse(cr,uid,sale_order_line_id)
	# 		remaining_qty = order_line_obj.ordered_quantity - order_line_obj.allocated_quantity
	# 		if remaining_qty < 0:
	# 			raise osv.except_osv(_('Warning!'),_("Allocated Quantity can not be greater than Remaining Quantity!"))				 
	
	# 	return True

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'select':fields.boolean(''),
		'delivery_order_no':fields.char('Delivery Order No',size=100),
		'delivery_order_date':fields.date('Delivery Order Date'),
		'despatcher':fields.many2one('res.company','Despatcher'),
		'expected_delivery_date':fields.date('Expected Delivery Date'),
		'delivery_challan_no':fields.char('Delivery Challan No',size=15),
		'amount':fields.float('Amount'),
		'product_cost':fields.float('Product Cost'),
		'total_vat':fields.float('Total VAT/CST'),
		'bird_pro':fields.boolean('Bird Pro'),
		'bird_pro_charge':fields.float('Bird Pro Installation Charge'),
		'total_st':fields.float('Bird Pro Service Tax'),
		'state':fields.selection([('new','New'),
						('draft','View Order'),
						('assigned','Packlist/Transport'),
						('confirmed','Ready To Dispatch'),
						('invoiced','Invoiced'),
						('delivered','Delivered'),
						#('progress','In Transit'),
						('cancel','Cancelled'),
						#('done','Done')
						],'State'),
		'sale_order_id':fields.many2one('psd.sales.product.order','Sale Order'),
		'delivery_date': fields.date('Delivery Date'),
		'scheduled_delivery_list':fields.one2many('scheduled.product.list.line','scheduled_delivery_list_id',string='Scheduled Products'),
		'godown':fields.many2one('res.company',string="Godown"),
		'tax_one2many':fields.one2many('tax','delivery_schedule_tax_id','Tax'),
		'cgst_rate':fields.char('CSGT Rate',size=10),
		'sgst_rate':fields.char('SGST Rate',size=10),
		'igst_rate':fields.char('IGST Rate',size=10),
		'cgst_amount':fields.float('CGST Amount'),
		'sgst_amount':fields.float('SGST Amount'),
		'igst_amount':fields.float('IGST Amount'),
	}

	_defaults = {
		'company_id': _get_company,
		'state':'draft'
	}

	def unlink(self,cr,uid,ids,context=None):
		self_obj = self.browse(cr,uid,ids[0])
		sale_order_id = self_obj.sale_order_id.id
		psd_sales_product_order_lines_obj =self.pool.get('psd.sales.product.order.lines')
		if self_obj.state == 'new':
			print sale_order_id,self_obj,'================='
			for each in self_obj.scheduled_delivery_list:
				print each.product_name_id
				product_name_id = each.product_name_id.id
				line_rec = psd_sales_product_order_lines_obj.search(cr,uid,[('psd_sales_product_order_lines_id','=',sale_order_id),('product_name_id','=',product_name_id)])
				print line_rec
				psd_sales_product_order_lines_obj.write(cr,uid,line_rec,{'done_products':False})
				cr.commit()
				form_rec = self.pool.get('psd.sales.product.order').search(cr,uid,[('id','=',sale_order_id)])
				self.pool.get('psd.sales.product.order').write(cr,uid,form_rec,{'done_products':False})
				cr.commit()
		if self_obj.state not in  ['new']:
			raise osv.except_osv(_('Warning!'),_("Delivery Scheduled can not be Deleted!"))
		scheduled_product_list_line_obj = self.pool.get('scheduled.product.list.line')
		# psd_sales_product_order_lines_obj =self.pool.get('psd.sales.product.order.lines')
		for main_id in ids:
			search_delivery_list_id = scheduled_product_list_line_obj.search(cr,uid,[('scheduled_delivery_list_id','=',main_id)])
			browse_ids = scheduled_product_list_line_obj.browse(cr,uid,search_delivery_list_id)
			for browse_id in browse_ids:
				sale_order_line_id = browse_id.sale_order_line_id.id
				allocated_quantity = browse_id.allocated_quantity
				sales_allocated_quantity = psd_sales_product_order_lines_obj.browse(cr,uid,sale_order_line_id).allocated_quantity
				main_allocated_quantity = sales_allocated_quantity - allocated_quantity
				psd_sales_product_order_lines_obj.write(cr,uid,sale_order_line_id,{'allocated_quantity':main_allocated_quantity})
		res = super(psd_sales_delivery_schedule, self).unlink(cr, uid, ids, context=context)
		return res

psd_sales_delivery_schedule()


# ##################### Added by nitin 18-8-2016
class psd_sales_order_remarks(osv.osv):
	_name = "psd.sales.order.remarks"
	_description="Remarks"
	#_order="date desc"

	_columns = {
		'sale_order_id': fields.many2one('psd.sales.product.order','notes'),
		#'user_name':fields.many2one('res.users','User Name'), 
		'user_name':fields.char('User Name',size=64),
		'date': fields.datetime('Date & Time'),
		'name': fields.text('Topic: Notes *',size=500),
		'state': fields.selection([
									('new','New'),
									('pending','Pending'),
									('ordered','Ordered'),
									('partial_delivery_scheduled','Partial Delivery Scheduled'),
									('delivery_scheduled','Delivery Scheduled'),
									('delivered','Delivered'),
									('cancelled','Cancelled'),
								], 'Status', readonly=True, select=True),
		'source':fields.many2one('res.company','Source'),
		}
psd_sales_order_remarks()

class psd_product_transfer_comment_line(osv.osv):
	_name="psd.product.transfer.comment.line"
	_order="comment_date desc"

	def _get_user(self, cr, uid, context=None):		
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).name

	def _get_company(self, cr, uid, context=None):		
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_default_date(self, cr, uid, context=None):
		if context is None:
			context = {}
		return time.strftime('%Y-%m-%d %H:%M:%S')

	_columns={
		'sale_order_line_id': fields.many2one('psd.sales.product.order.lines','notes'),
		'user_id':fields.char('User Name',size=64),
		'comment_date':fields.datetime('Date & Time'),
		'comment':fields.text('Topic: Notes *',size=500,required=True),
		'source':fields.many2one('res.company','Source'),
	}

	_defaults={ 
		  'comment_date':_get_default_date,
		  'user_id':_get_user,
		  'source':_get_company,
			}
psd_product_transfer_comment_line()
# ################## End 18-8-2016

class tax(osv.osv):
	_inherit="tax"
	_columns={
		'psd_so_id':fields.many2one('psd.sales.product.order','Sale Order ID'),
		'delivery_schedule_tax_id':fields.many2one('psd.sales.delivery.schedule','Tax ID'),
	}

tax()
	
class invoice_adhoc_master(osv.osv):
	_inherit="invoice.adhoc.master"
	_columns={
		'sale_order_id':fields.many2one('psd.sales.product.order','Product Order'),
	}

invoice_adhoc_master()	
