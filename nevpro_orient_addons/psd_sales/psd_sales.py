from datetime import date,datetime, timedelta
from osv import osv,fields
from tools.translate import _
import time

class psd_sales_product_quotation(osv.osv):
	_inherit = "psd.sales.product.quotation"
	_order = "id desc, state asc"

	def _get_user(self, cr, uid, context=None):		
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).id

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def _get_datetime(self,cr,uid,context=None):
		return time.strftime("%Y-%m-%d %H:%M:%S")

	_columns = {
		'type':fields.char('Type',size=50),
		'account_fiscalyear':fields.many2one('account.fiscalyear','Fiscal Year'),
		'company_id':fields.many2one('res.company','Company ID'),
		'user_id':fields.many2one('res.users','User ID'),
		'partner_id': fields.many2one('res.partner','Partner'),	
		'created_date':fields.datetime('Created Date'),
		'name':fields.char('Customer / Company Name',size=100),
		'quotation_no':fields.char('Quotation Number',size=100),
		'quotation_date':fields.date("Quotation Date"),
		'delivery_location_id':fields.many2one('res.partner.address','Delivery Location'),
		'parent_quotation_no':fields.char('Parent Quotation Number',size=100),
		'parent_quotation_date':fields.date("Parent Quotation Date"),
		'billing_location_id':fields.many2one('res.partner.address','Billing Location'),
		'request_id':fields.char('Request Id',size=100),
		'customer_type': fields.selection([('existing','Existing Customer'),('new','New Customer')],'Customer Type * '),
		'customer_id': fields.char('Customer ID',size=256),
		'call_type':fields.selection([('inbound','Inbound'),('outbound','Outbound')],'Call Type * '),
		'state':fields.selection([('new','New'),
						('pending','Pending'),
						('quoted','Quoted'),
						('revised','Revised'),						
						('lost','Lost'),
						('ordered','Ordered'),
						],'State'), 
		'contact_person':fields.char('Contact Person',size=100),
		'quotation_validity':fields.selection([('30','30 Days'),
						('45','45 Days'),
						('60','60 Days'),
						],'Quotation Validity'), 
		# 'tax_type':fields.selection([('normal','Normal'),('composite','Composite')],'Tax Type',required=True),
		# 'no_of_service':fields.integer('No of Service'),
		'install_maintain_charges':fields.float('Installation/Maintainance Charges'),
		'service_tax':fields.float('Service Tax 14%'),  
		's_b_cess':fields.float('S B Cess 0.50%'),
		'k_k_cess':fields.float('K K Cess 0.50%'),
		'pse_id':fields.many2one('hr.employee','PSE'),
		'hospital':fields.boolean('Hospital'),
		'industry':fields.boolean('Industry'),
		'psd_sales_ids':fields.one2many('psd.sales.lines','psd_sales_lines_id','Locations & Products'),
		'quotation_total_amount':fields.float('Basic Amount'),
		'quotation_total_vat':fields.float('Total Vat'),
		'quotation_grand_total':fields.float('Grand Total'),    
		'search_product_quot_id':fields.many2one('search.product.quotation','Search Product Quotation'),
		'payment_terms':fields.text('Payment Terms', size=500),
		'octroi':fields.selection([('Will be charged extra at actual; if applicable','Will be charged extra at actual; if applicable')],'Octroi'),
		'despatch_schedule':fields.text('Despatch Schedule',size=500),
		'installation':fields.text('Installation',size=500),
		'transportation':fields.text('Transportation',size=500),
		'bank_charges':fields.text('Bank Charges',size=500),
		'warranty':fields.text('Warranty',size=500),
		'notes':fields.text('Notes',size=500),
		'quotation_history_id':fields.one2many('psd.quotation.history','quotation_history_lines_id','Quotation History'),
		'order_created':fields.boolean('Order Created'),
		'tax_one2many':fields.one2many('tax','psd_quotn_id','Tax'),
		'quotation_lost': fields.boolean('Quotation Lost'),
		'reason_for_lost': fields.text('Reason for Lost'),
		'quotation_revised':fields.boolean('Quotn Revised'),
		'notes_one2many': fields.one2many('psd.sales.quotation.remarks','quotation_order_id','Notes'),
		'products':fields.char('Products',size=5000),
		'skus':fields.char('Sku Name',size=5000),
		'allow_logo':fields.boolean('Allow Logo'),
		'territry_manager':fields.char('territry manager',size=200),
		'email':fields.char('Email',size=50),
		'mobile':fields.char('Mobile No.',size=20),
		'designation':fields.char('Designation',size=200),
		'subtotal':fields.float('Subtotal'),
		'product_discount':fields.float('Product Discount %'), 
		'product_discount_amount':fields.float('Product Discount in Amount'),
	}

	_defaults = {
		'company_id': _get_company,
		'created_date': _get_datetime,
		'user_id':_get_user,
		# 'tax_type':'normal',
		'type':'Product Quotation',
		'state':'new',
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

	def psd_post_notes(self,cr,uid,ids,context=None): 
		date=datetime.now()
		for o in self.browse(cr,uid,ids):
			source = o.company_id.id
			user_name=self.pool.get('res.users').browse(cr, uid, uid).name
			if o.notes:
				self.pool.get('psd.sales.quotation.remarks').create(cr,uid,{'quotation_order_id':o.id,
											'user_name':user_name,
											'date':date,
											'source':source,
											'name':'General - '+o.notes,
											'state':o.state})
			self.write(cr,uid,ids,{'notes':None})
		return True

	def onchange_billing_location_id(self,cr,uid,ids,billing_location_id):
		v={'contact_person':False}
		partner_address_obj = self.pool.get('res.partner.address')
		if billing_location_id:
			partner_rec = partner_address_obj.browse(cr,uid,billing_location_id)
			contact_person = str(partner_rec.first_name)+' '+str(partner_rec.last_name)
			v['contact_person'] = contact_person
		return {'value': v}

	def calculate_sales_quotation(self,cr,uid,ids,context=None):
		cur_rec = self.browse(cr,uid,ids[0])
		if not cur_rec.psd_sales_ids:
			raise osv.except_osv(_('Warning!'),_("No product lines defined!"))
		product_lines = self.pool.get('psd.sales.lines')
		crm_hist_obj = self.pool.get('sales.product.quotation.history')
		psd_sales_product_quotation = self.pool.get('psd.sales.product.quotation')
		product_lines_rec = product_lines.search(cr,uid,[('psd_sales_lines_id','=',ids[0])])
		total_vat_amount = 0.0
		main_form_total_amount =tax_value=total_basic_amount= 0.0
		product_basic_rate = sgst_amount = cgst_amount = igst_amount = gst_total =sgst_rate=cgst_rate=igst_rate= 0.0
		tax_ids = []
		account_tax = self.pool.get('account.tax')
		tax_line_obj = self.pool.get('tax')
		partner_obj = self.pool.get('res.partner')
		today_date =datetime.today().date()

		sgst_tax=account_tax.search(cr,uid,[('name','=','SGST')])[0]
		cgst_tax=account_tax.search(cr,uid,[('name','=','CGST')])[0]
		igst_tax=account_tax.search(cr,uid,[('name','=','IGST')])[0]


		company_id = cur_rec.company_id.state_id.id
		partner_location_addr = cur_rec.delivery_location_id.state_id.id
		if not partner_location_addr:
			raise osv.except_osv(('Warning!'),('Please update the state of the custommer'))

		if cur_rec.tax_one2many:
			for tax_line_id in cur_rec.tax_one2many:
				tax_ids.append(tax_line_id.id)    
			tax_line_obj.unlink(cr, uid, tax_ids, context=context)
		taxes = {}
		check_lines = []
		additional_amount = additional_basic_amount=0.0

		for line in product_lines.browse(cr,uid,product_lines_rec):
			print line,'========================================='
			generics=line.product_name_id.id
			product_basic_rate = line.product_basic_rate
			# skus=line.sku_name_id.id
			# combo=tuple([generics]+[skus])
			combo = generics
			# check_lines.append(combo)
			tax_rate =  line.product_name_id.product_tax.id
			tax_amount = line.product_name_id.product_tax.amount
			tax_name = line.product_name_id.product_tax.name
			if combo in check_lines:
				raise osv.except_osv(('Invalid Combination!'),('Same Product lines are not allowed!'))
			else:
				check_lines.append(combo)
			print check_lines
			# for irange in range(0,len(check_lines)):	
			# 		for jrange in range(irange+1,len(check_lines)):
			# 			if check_lines[irange][0]==check_lines[jrange][0] and check_lines[irange][1]==check_lines[jrange][1]:
			# 				raise osv.except_osv(('Invalid Combination!'),('Same Product lines are not allowed!'))
			if not line.quantity or line.quantity == 0:
				raise osv.except_osv(_('Warning!'),_("Please enter Quantities before calculating quotation value!"))
			if not line.vat_id:
				raise osv.except_osv(_('Warning!'),_("Please select proper VAT before calculating quotation value!"))
			if not line.product_basic_rate or line.product_basic_rate <= 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper Product Basic rate before calculating quotation value!"))
			if line.product_mrp < 0.0:
				raise osv.except_osv(_('Warning!'),_("Please enter proper Product MRP before calculating quotation value!"))
			if not line.discount:
				total_basic_amount = product_basic_rate * line.quantity
				product_lines.write(cr,uid,line.id,{'discounted_amount':total_basic_amount})
				cr.commit()
			else:
				additional_amount = product_basic_rate + line.discount
				additional_basic_amount = additional_amount * line.quantity
				total_basic_amount = additional_basic_amount
				product_lines.write(cr,uid,line.id,{'discounted_amount':total_basic_amount})
				cr.commit()				
			if company_id == partner_location_addr:
				print "aaaaaaaaaa"
				if line.exempted:
					print "INTRA exempted"
				else:
					if tax_rate:
						# print product_basic_rate
						cgst_rate = sgst_rate = tax_amount/2
						cgst_amount = sgst_amount = (tax_amount * total_basic_amount)/2
						cgst_tax_name = account_tax.browse(cr,uid,cgst_tax).name
						sgst_tax_name = account_tax.browse(cr,uid,sgst_tax).name
						gst_total = cgst_amount + sgst_amount
						product_lines.write(cr,uid,line.id,{'sgst_rate':str(sgst_rate*100)+'%','cgst_rate':str(cgst_rate*100)+'%','sgst_amount':sgst_amount,'cgst_amount':cgst_amount,'vat_amount':gst_total,'total_amount':gst_total+total_basic_amount})
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
						product_lines.write(cr,uid,line.id,{'igst_rate':str(igst_rate*100)+'%','igst_amount':igst_amount,'vat_amount':gst_total,'total_amount':gst_total+total_basic_amount})
						cr.commit()

		print line.psd_sales_lines_id
		cr.execute('select sum(sgst_amount) from psd_sales_lines where psd_sales_lines_id = %s',(line.psd_sales_lines_id.id,))
		sgst_amount = cr.fetchone()[0]
		cr.execute('select sum(cgst_amount) from psd_sales_lines where psd_sales_lines_id = %s',(line.psd_sales_lines_id.id,))
		cgst_amount = cr.fetchone()[0]
		cr.execute('select sum(igst_amount) from psd_sales_lines where psd_sales_lines_id = %s',(line.psd_sales_lines_id.id,))
		igst_amount = cr.fetchone()[0]
		cr.execute('select sum(discounted_amount) from psd_sales_lines where psd_sales_lines_id = %s',(line.psd_sales_lines_id.id,))
		total_amount = cr.fetchone()[0]
		total_amount = round(total_amount)
		cr.execute('select sum(total_amount) from psd_sales_lines where psd_sales_lines_id = %s',(line.psd_sales_lines_id.id,))
		grand_amount = cr.fetchone()[0]
		grand_amount = round(grand_amount)
		psd_sales_product_quotation.write(cr,uid,cur_rec.id,{'quotation_total_amount':total_amount})
		print sgst_amount,'sssssssssssssssssssssss'
		if company_id == partner_location_addr:
			tax_line_obj.create(cr,uid,{'psd_quotn_id':int(ids[0]),'account_tax_id':cgst_tax,'name':cgst_tax_name,'amount':cgst_amount},context=None)	
			cr.commit()
			tax_line_obj.create(cr,uid,{'psd_quotn_id':int(ids[0]),'account_tax_id':sgst_tax,'name':sgst_tax_name,'amount':sgst_amount},context=None)					
			cr.commit()
		else:
			tax_line_obj.create(cr,uid,{'psd_quotn_id':int(ids[0]),'account_tax_id':igst_tax,'name':igst_tax_name,'amount':igst_amount},context=None)
			cr.commit()

		if cur_rec.tax_one2many:
			tax_id = tax_line_obj.search(cr,uid,[('psd_quotn_id','=',ids[0])])[0]
			browse_rec = tax_line_obj.browse(cr,uid,tax_id)
			tax_value += browse_rec.amount

		if total_vat_amount == 0.0:
			total_vat_amount = 0.0
		grand_total = cur_rec.install_maintain_charges + gst_total + total_basic_amount
		grand_total = self.round_off_grand_total(cr,uid,ids,grand_total,context=None)
		if cur_rec.parent_quotation_no and cur_rec.parent_quotation_date:
			search_amc_qut = self.search(cr,uid,[('quotation_no','=',str(cur_rec.parent_quotation_no))])
			self.write(cr,uid,search_amc_qut[0],{'state':'revised'},context=None)
			qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(cur_rec.partner_id.id)),('sale_quotation_id','=',int(search_amc_qut[0]))])
			if qutn_id:
				crm_hist_obj.write(cr,uid,qutn_id[0],{'status':'revised'},context=None)
		product_list = []
		for line in product_lines.browse(cr,uid,product_lines_rec):
			if not line.product_name_id.name in product_list:
				product_list.append(line.product_name_id.name)
		products =', '.join(map(str, product_list))
		self.write(cr,uid,ids,{
								'quotation_grand_total':grand_amount,							
								'state':'pending',
								'skus':products,
								'subtotal':grand_amount})

		cr.execute('select sum(quantity*product_basic_rate) from psd_sales_lines where psd_sales_lines_id = %s',(line.psd_sales_lines_id.id,))
		basic_rate = cr.fetchone()[0]
		print basic_rate,'=========basic'
		#calculate product profit
		grand_amt = grand_amount
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
						'quotation_grand_total':grand_tot,
					})
			else:
				self.write(cr,uid,ids,{
						'product_discount_amount':0.00
						
					})

		qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(cur_rec.partner_id.id)),('sale_quotation_id','=',int(cur_rec.id))])
		if qutn_id:
			for m in qutn_id:
				crm_hist_obj.unlink(cr,uid,m,context=None)
		crm_history_values = { 	'partner_id':cur_rec.partner_id.id,
								'sale_quotation_id':cur_rec.id,
								'quotation_id':cur_rec.quotation_no,
								'quotation_date':cur_rec.quotation_date,
								'quotation_type':cur_rec.type,
								'sku_name':products,
								'request_id':cur_rec.request_id,
								'quotation_amount':grand_total,
								'status':'pending',
								'pse':cur_rec.pse_id.concate_name,
							}
		crm_hist_obj.create(cr,uid,crm_history_values,context=None)	
		return True

	def generate_quotation(self,cr,uid,ids,context=None):
		self.calculate_sales_quotation(cr,uid,ids,context=context)
		rec = self.browse(cr,uid,ids[0])
		seq = self.pool.get('ir.sequence').get(cr, uid, 'psd.sales.product.quotation')
		code = self.get_fiscalyear(cr,uid,ids,context=None)
		# quotation_no = str(rec.company_id.pcof_key)+str(rec.company_id.sale_quotation_id)+code+str(seq)
		cur_rec = self.browse(cr,uid,ids[0])
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
		quotation_no = str(rec.company_id.pcof_key)+str(rec.company_id.sale_quotation_id)+financial_year+str(seq)
		crm_hist_obj = self.pool.get('sales.product.quotation.history')
		res = self.write(cr,uid,ids,{'state':'quoted','quotation_no':quotation_no,'quotation_date':datetime.today()})
		product_list = []
		generic_name = []
		for line in rec.psd_sales_ids:
			self.pool.get('psd.sales.lines').write(cr,uid,line.id,{'quotation_no_ref':quotation_no},context=None)
			if not line.product_name_id.name in product_list:
				product_list.append(line.product_name_id.name)
			if not line.product_name_id.name in generic_name:
				generic_name.append(line.product_name_id.name)
		products =', '.join(map(str, product_list))
		generic = ''
		if len(generic_name) > 1:
			last_item = generic_name[-1]
			second_last = generic_name[-2]
			for x in generic_name:
				if x == last_item:
					generic = generic+'& ' + x
				elif x == second_last:
					generic =  generic + x +' '
				else:
					generic =  generic + x +', '
		elif len(generic_name) == 1:
			generic = generic_name[0]
		self.write(cr,uid,ids,{'products':generic,'skus':products})
		qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(rec.partner_id.id)),('sale_quotation_id','=',int(rec.id))])
		if qutn_id:			
			crm_history_values = { 	
									'quotation_id':quotation_no,
									'quotation_date':datetime.now(),
									'sku_name':products,
									'quotation_amount':rec.quotation_grand_total,
									'status':'quoted',
									'pse':rec.pse_id.concate_name,
								}
			crm_hist_obj.write(cr,uid,qutn_id[0],crm_history_values,context=None)
		else:
			crm_history_values = { 	'partner_id':rec.partner_id.id,
								'sale_quotation_id':rec.id,
								'quotation_id':quotation_no,
								'quotation_date':datetime.now(),
								'quotation_type':rec.type,
								'sku_name':products,
								'request_id':rec.request_id,
								'quotation_amount':rec.quotation_grand_total,
								'status':'quoted',
								'pse':rec.pse_id.concate_name,
							}
			crm_hist_obj.create(cr,uid,crm_history_values,context=None)
		return rec

	def lost(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'lost'})
		crm_hist_obj = self.pool.get('sales.product.quotation.history')
		crm_lead_obj = self.pool.get('crm.lead')
		product_req_obj = self.pool.get('product.request')
		rec = self.browse(cr,uid,ids[0])
		qutn_id = crm_hist_obj.search(cr,uid,[('partner_id','=',int(rec.partner_id.id)),('sale_quotation_id','=',int(rec.id))])
		req_id = product_req_obj.search(cr,uid,[('partner_id','=',int(rec.partner_id.id)),('product_request_id','=',rec.request_id)])
		if qutn_id:			
			crm_history_values = { 
									'quotation_amount':rec.quotation_grand_total,
									'status':'lost',

								}
			crm_hist_obj.write(cr,uid,qutn_id[0],crm_history_values,context=None)
		if req_id:
			product_req_obj.write(cr,uid,req_id[0],{'state':'closed'})
			crm_ids = crm_lead_obj.search(cr, uid, [('product_request_id','=', str(rec.request_id))], context=context)
			for crm_id in crm_ids:
				crm_lead_obj.write(cr, uid, crm_id, {'state':'closed'}, context=context)
		return True

	def print_quotation(self, cr, uid, ids, context=None):
		emp_obj =  self.pool.get('hr.employee')
		user_obj = self.pool.get('res.users')
		search_branch_mgr = emp_obj.search(cr,uid,[('role','=','branch_manager')])
		employee = emp_obj.browse(cr,uid,search_branch_mgr[1])
		emp_name = employee.concate_name
		emp_designation = employee.emp_role.value
		# search_user = user_obj.search(cr,uid,[('name','ilike',emp_name),('emp_code','=',employee.emp_code)])
		search_user = user_obj.search(cr,uid,[('name','ilike',employee.name),('emp_code','=',employee.emp_code)])
		user = user_obj.browse(cr,uid,search_user[0])
		self.write(cr,uid,ids,{'territry_manager':emp_name,'email':user.user_email,'mobile':user.mobile,'designation':emp_designation})
		datas = {
				 'model': 'psd.sales.product.quotation',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'Sales Quotation', 'datas': datas, 'nodestroy': True}


	def cancel_quotation(self,cr,uid,ids,context=None):
		product_request_obj = self.pool.get('product.request')
		search_product_quotation_obj =  self.pool.get('search.product.quotation')
		request_search_sales_obj = self.pool.get('request.search.sales')
		sales_line_obj = self.pool.get('psd.sales.lines')
		history_line_obj = self.pool.get('psd.quotation.history')
		tax_line_obj = self.pool.get('tax')
		o = self.browse(cr,uid,ids[0])
		search_product_request = product_request_obj.search(cr,uid,[('product_request_id','=',str(o.request_id))])
		line_ids = []
		history_ids = []
		tax_ids = []
		if o.psd_sales_ids:
			for line_id in o.psd_sales_ids:
				line_ids.append(line_id.id)    
			sales_line_obj.unlink(cr, uid, line_ids, context=context)
		if o.quotation_history_id:
			for line_id in o.quotation_history_id:
				history_ids.append(line_id.id)    
			history_line_obj.unlink(cr, uid, history_ids, context=context)
		if o.tax_one2many:
			for tax_id in o.tax_one2many:
				tax_ids.append(tax_id.id)    
			tax_line_obj.unlink(cr, uid, tax_ids, context=context)
		if o.parent_quotation_no:
			search_pr_qut = self.search(cr,uid,[('quotation_no','=',str(o.parent_quotation_no))])
			self.write(cr,uid,search_pr_qut[0],{'quotation_revised':False},context=None)
			self.unlink(cr,uid,ids[0],context=context)
			request_search_quotn_id = search_product_quotation_obj.create(cr,uid,
				{
					'search_product_quot_lines': [(6, 0, search_pr_qut)],
				},context=context)
			models_data=self.pool.get('ir.model.data')
			form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'search_product_quotation_form')
			return {
				   'name':'Search Product Quotation',
				   'view_mode': 'form',
				   'view_id': form_id[1],
				   'view_type': 'form',
				   'res_model': 'search.product.quotation',
				   'res_id':int(request_search_quotn_id),
				   'type': 'ir.actions.act_window',
				   'target': 'current',
				   'context':context
				   } 
		else:
			self.unlink(cr,uid,ids[0],context=context)
			product_request_obj.write(cr,uid,search_product_request[0],{'psd_sales_entry':False})
			request_search_sales_id = request_search_sales_obj.create(cr,uid,
				{
					'product_request_ids': [(6, 0, search_product_request)],
					'pushed': False
				},context=context)
			models_data=self.pool.get('ir.model.data')
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

	def generate_sales_product_order(self, cr, uid, ids, context=None):
		if not isinstance(ids, (list)):
			ids = [ids]
		if context is None:
			context = {}
		sales_product_quotation_obj = self.pool.get('psd.sales.product.order')
		partner_address_obj = self.pool.get('res.partner.address')
		psd_sales_lines_obj = self.pool.get('psd.sales.product.order.lines')
		search_sale_order_obj = self.pool.get('search.sale.product.order')
		tax_line_obj = self.pool.get('tax')
		psd_sales_ids = []
		product_list = []
		generic_name = []
		sale_product_req_data = self.browse(cr, uid, ids[0])
		# seq = self.pool.get('ir.sequence').get(cr, uid, 'psd.sales.product.order')
		# partner_address_id = partner_address_obj.search(cr, uid, [('partner_id','=',product_req_data.partner_id.id)], context=context)
		quotation_vals = {
			'name': sale_product_req_data.name,
			'contact_person': sale_product_req_data.contact_person,
			'state':'pending',
			'partner_id':sale_product_req_data.partner_id.id,
			'billing_location_id': sale_product_req_data.billing_location_id.id,
			'delivery_location_id': sale_product_req_data.delivery_location_id.id,
			'pse_id': sale_product_req_data.pse_id.id,
			'user_id':context.get('uid'),
			'quotation_no':sale_product_req_data.quotation_no,
			'is_quotation_no':True,
			'request_id':sale_product_req_data.request_id,
			'psd_quotation_id':sale_product_req_data.id,
			'install_maintain_charges':sale_product_req_data.install_maintain_charges,
			'order_total_vat':sale_product_req_data.quotation_total_vat,
			'order_total_amount':sale_product_req_data.quotation_total_amount,
			'total_amount_paid':sale_product_req_data.quotation_grand_total,
			'service_tax':sale_product_req_data.service_tax,
			's_b_cess':sale_product_req_data.s_b_cess,
			'k_k_cess':sale_product_req_data.k_k_cess,
			'payment_terms':sale_product_req_data.payment_terms,
			'transportation':sale_product_req_data.transportation,
			'bank_charges':sale_product_req_data.bank_charges,
			'despatch_schedule':sale_product_req_data.despatch_schedule,
			'warranty':sale_product_req_data.warranty,
			'installation':sale_product_req_data.installation,
			'octroi':sale_product_req_data.octroi,
			'product_discount':sale_product_req_data.product_discount,
			'product_discount_amount':sale_product_req_data.product_discount_amount,
			'subtotal':sale_product_req_data.subtotal
			}
		res = sales_product_quotation_obj.create(cr, uid, quotation_vals, context=context)
		for psd_sales_product_order_line in sale_product_req_data.psd_sales_ids:
			product_group_id = psd_sales_product_order_line.product_name_id.id
			# sku_name_id = psd_sales_product_order_line.sku_name_id.id
			product_uom_id = psd_sales_product_order_line.product_uom_id.id
			product_quantity = psd_sales_product_order_line.quantity
			extended_warranty = psd_sales_product_order_line.extended_warranty
			# if not psd_sales_product_order_line.sku_name_id.name in product_list:
			# 	product_list.append(psd_sales_product_order_line.sku_name_id.name)
			if not psd_sales_product_order_line.product_name_id.name in generic_name:
				generic_name.append(psd_sales_product_order_line.product_name_id.name)
			psd_sales_order_lines_vals = {
				'product_name_id': product_group_id,
				# 'sku_name_id': sku_name_id,
				'product_uom_id': product_uom_id,
				'ordered_quantity':product_quantity,
				'allocated_quantity':product_quantity,
				'psd_sales_product_order_lines_id': int(res),
				'track_equipment':psd_sales_product_order_line.track_equipment,
				'extended_warranty':extended_warranty,
				'product_mrp':psd_sales_product_order_line.product_mrp,
				'product_basic_rate':psd_sales_product_order_line.product_basic_rate,
				'tax_id':psd_sales_product_order_line.vat_id.id,
				'tax_amount':psd_sales_product_order_line.vat_amount,
				'discount':psd_sales_product_order_line.discount,
				'discounted_amount':psd_sales_product_order_line.discounted_amount,
				'total_amount':psd_sales_product_order_line.total_amount,
				###############added for the batch fields by shreyas
				'batch_number':psd_sales_product_order_line.batch_number.id,
				'manufacturing_date':psd_sales_product_order_line.manufacturing_date,
				'exempted':psd_sales_product_order_line.exempted,
				'specification':psd_sales_product_order_line.specification,
			}
			psd_sales_lines_obj.create(cr, uid, psd_sales_order_lines_vals, context=context)
		if sale_product_req_data.tax_one2many:
			for tax_line_id in sale_product_req_data.tax_one2many:  
				tax_line_values ={
				'psd_so_id': int(res),
				'name': tax_line_id.name,
				'account_tax_id':tax_line_id.account_tax_id.id,
				'amount':tax_line_id.amount,
				}
				res_tax_order_line_create= tax_line_obj.create(cr,uid,tax_line_values)
		self.write(cr,uid,ids[0],{'order_created':True})
		products =', '.join(map(str, product_list))
		generic =', '.join(map(str, generic_name))
		sales_product_quotation_obj.write(cr, uid, int(res), {'skus':products,'generic':generic}, context=context)
		models_data=self.pool.get('ir.model.data')
		form_id = models_data.get_object_reference(cr, uid, 'psd_sales', 'view_psd_product_sale_order_branch')
		return {
			   'name':'Sales Order-Product',
			   'view_mode': 'form',
			   'view_id': form_id[1],
			   'view_type': 'form',
			   'res_model': 'psd.sales.product.order',
			   'res_id':int(res),
			   'type': 'ir.actions.act_window',
			   'target': 'current',
			   'context':context
			   } 


	def reload_product_quotation(self, cr, uid, ids, context=None):
		view = self.pool.get('ir.model.data').get_object_reference(
			cr, uid, 'psd_sales', 'view_psd_product_quotation_branch')
		view_id = view and view[1] or False
		return {
			'name': _('Product Quotation'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id or False,
			'res_model': 'psd.sales.product.quotation',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': ids[0],
		}       

	def revise_quotation(self,cr,uid,ids,context=None):
		if context is None: context = {}
		context = dict(context, active_ids=ids, active_model=self._name)
		res_create_id = self.pool.get("psd.sales.product.quotation").create(cr, uid, {}, context=context)
		self.write(cr,uid,ids,{'quotation_revised':True})
		return {
			'name':_("Revise Product Quotation"),
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'psd.sales.product.quotation',
			'res_id': int(res_create_id),
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'domain': '[]',
			'context': context,
		}

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		psd_sales_product_quotation_obj =self.pool.get('psd.sales.product.quotation')
		res = super(psd_sales_product_quotation, self).default_get(cr, uid, fields, context=context)
		picking_ids = context.get('active_ids', [])
		if not picking_ids or (not context.get('active_model') == 'psd.sales.product.quotation') \
			or len(picking_ids) != 1:
			return res
		picking_id, = picking_ids
		picking=psd_sales_product_quotation_obj.browse(cr,uid,picking_id,context=context)
		state='new'
		if 'state' in fields:
			res.update(state=state)
		if 'name' in fields:			
			res.update(name=picking.name)
		if 'partner_id' in fields:
			res.update(partner_id=picking.partner_id.id) 
		if 'billing_location_id' in fields:
			res.update(billing_location_id=picking.billing_location_id.id) 
		if 'delivery_location_id' in fields:
			res.update(delivery_location_id=picking.delivery_location_id.id)
		if 'request_id' in fields:
			res.update(request_id=picking.request_id)
		if 'customer_type' in fields:
			res.update(customer_type=picking.customer_type)
		if 'customer_id' in fields:
			res.update(customer_id=picking.customer_id)
		if 'call_type' in fields:
			res.update(call_type=picking.call_type)
		if 'contact_person' in fields:
			res.update(contact_person=picking.contact_person)
		if 'psd_sales_ids' in fields:
			moves = [self._partial_move_for(cr, uid, m) for m in picking.psd_sales_ids]
			res.update(psd_sales_ids=moves)
		if 'quotation_no' in fields:
			res.update(parent_quotation_no=picking.quotation_no)
		if 'quotation_validity' in fields:
			res.update(quotation_validity=picking.quotation_validity)
		if 'pse_id' in fields:
			res.update(pse_id=picking.pse_id.id)
		if 'quotation_date' in fields:
			moves = [self._partial_move_for(cr, uid, m) for m in picking.psd_sales_ids]
			res.update(parent_quotation_date=picking.quotation_date)
		if 'install_maintain_charges' in fields:
			res.update(install_maintain_charges=picking.install_maintain_charges)
		if 'service_tax' in fields:
			res.update(service_tax=picking.service_tax)
		if 's_b_cess' in fields:
			res.update(s_b_cess=picking.s_b_cess)
		if 'k_k_cess' in fields:
			res.update(k_k_cess=picking.k_k_cess)
		if 'quotation_total_amount' in fields:
			res.update(quotation_total_amount=picking.quotation_total_amount)
		if 'tax_one2many' in fields:
			moves = [self._tax_for(cr, uid, m) for m in picking.tax_one2many]
			res.update(tax_one2many=moves)
		if 'quotation_total_vat' in fields:
			res.update(quotation_total_vat=picking.quotation_total_vat)
		if 'quotation_grand_total' in fields:
			res.update(quotation_grand_total=picking.quotation_grand_total)
		res.update(quotation_history_id= [(0,0, {
								'quotation_date':picking.quotation_date,
								'quotation_number': picking.quotation_no,
								'quotation_amount': picking.quotation_grand_total,
								'previous_quotation_number':picking.parent_quotation_no,
				 })])
		return res

	def _partial_move_for(self, cr, uid, move):
		partial_move = {
			'product_name_id': move.product_name_id.id,
			#'sku_name_id' : move.sku_name_id.id,
			'exempted': move.exempted,
			'extended_warranty' : move.extended_warranty,
			'quantity':move.quantity,
			'product_uom_id' : move.product_uom_id.id,
			'product_mrp' : move.product_mrp,
			'product_basic_rate':move.product_basic_rate,
			'discount' : move.discount,
			'discounted_value' : move.discounted_value,
			'discounted_price' : move.discounted_price,
			'discounted_amount' : move.discounted_amount,
			'vat_id': move.vat_id.id,
			'vat_amount': move.vat_amount,
			'total_amount':move.total_amount
		}
		return partial_move

	def _tax_for(self, cr, uid, tax):
		tax_move = {
			'name': tax.name,
			'amount':tax.amount,
			'account_tax_id':tax.account_tax_id.id,
		}
		return tax_move

psd_sales_product_quotation()


class psd_sales_lines(osv.osv):
	_name = 'psd.sales.lines'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'psd_sales_lines_id': fields.many2one('psd.sales.product.quotation','PSD Sales Product Quotation'),
		'quotation_no_ref':fields.char('Quotation Ref',size=56),
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
		'quantity':fields.integer('Quantity'),
		'product_uom_id':fields.many2one('product.uom','UOM'),
		'product_mrp':fields.float('MRP'),
		'product_basic_rate':fields.float('Basic Rate'),
		'discount':fields.float('Disc %'),
		'discounted_value':fields.float('Discounted Value'),
		'discounted_price':fields.float('Discounted Price'),
		'discounted_amount':fields.float(string='Disc Amt'),
		'vat_id':fields.many2one('account.tax','VAT %',domain="['|',('description','=','vat'),('description','=','cst'),('active','=',True)]"),
		'vat_amount':fields.float('VAT Amt'),
		'total_amount':fields.float('Total Amount'),
		#########added for the batch number and the manufaturing date
		'batch_number': fields.many2one('res.batchnumber','Batch No.'),
		'manufacturing_date': fields.date('Manufaturing Date'),
		'exempted':fields.boolean('Exempted'),
		'track_equipment':fields.boolean('Track Equipment'),
		'specification': fields.char('Specification',size=500),
		'hsn_code':fields.char('HSN Code',size=10),
		'cgst_rate':fields.char('CSGT Rate',size=10),
		'sgst_rate':fields.char('SGST Rate',size=10),
		'igst_rate':fields.char('IGST Rate',size=10),
		'cgst_amount':fields.float('CGST Amount'),
		'sgst_amount':fields.float('SGST Amount'),
		'igst_amount':fields.float('IGST Amount'),

	}

	_defaults = {
		'company_id': _get_company
	}

	# def create(self,cr,uid,vals,context=None):

	# 	print "vals",vals
	# 	if vals.get('product_name_id'):
	# 		raise osv.except_osv(('Alert!'),('You cannot add products after your request has been processed. Create a new request for new products!'))
	# 	new_id=super(psd_sales_lines,self).create(cr,uid,vals,context=context)
	# 	return new_id

	def onchange_product_name_id(self,cr,uid,ids,product_name_id,exempted,company_id,context=None):
		data = {'product_uom_id':False,'vat_id':False}
		product_obj = self.pool.get('product.product')
		psd_sales_product_quotation_obj =self.pool.get('psd.sales.product.quotation')
		generic_obj = self.pool.get('product.generic.name')
		company_state = self.pool.get('res.company').browse(cr,uid,company_id).state_id.id
		vat_id_list =[]
		search_tax_id = False
		cur_rec_id = context.get('active_id')
		delivery_location_state = psd_sales_product_quotation_obj.browse(cr,uid,cur_rec_id).delivery_location_id.state_id.id
		if product_name_id:
			product_ids = product_obj.search(cr, uid, [('generic_name','=',product_name_id)], context=context)
			if product_ids[0]:
				product_data = product_obj.browse(cr,uid,product_ids[0])
				product_uom_id = product_data.product_tmpl_id.local_uom_id.id
				if product_uom_id:
					data.update({'product_uom_id': product_uom_id})
		if company_state == delivery_location_state:
			if exempted:
				search_tax_id = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Exempted')])
				vat_id_list.append(search_tax_id[0])
			else:
				check_group_name = generic_obj.browse(cr,uid,product_name_id)
				if check_group_name.product_group_id:
					for each in check_group_name.product_group_id:
						search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',each.tax_name.id),('description','=','vat')])
						if search_tax_id:
							vat_id_list.append(search_tax_id[0])
		else:
			if exempted:
				search_tax_id = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Exempted')])
				vat_id_list.append(search_tax_id[0])
			else:
				check_group_name = generic_obj.browse(cr,uid,product_name_id)
				if check_group_name.product_group_id:
					for each in check_group_name.product_group_id:
						search_tax_id = self.pool.get('account.tax').search(cr,uid,[('id','=',each.tax_name.id),('description','=','cst')])
						if search_tax_id:
							vat_id_list.append(search_tax_id[0])
		if vat_id_list:
			data.update({'vat_id':vat_id_list[0]})
		return {'value':data}

	def onchange_sku_name_id(self,cr,uid,ids,product_name_id,sku_name_id,context=None):
		res = {'product_basic_rate':False,'product_mrp':False,'batch_number':False,'manufacturing_date':False,'track_equipment':False}
		first_tax_val = False
		tax_name = False
		search_tax_id = False
		partner_obj = self.pool.get('res.partner')
		product_req_data = self.browse(cr, uid, ids[0])
# 		partner_address_id = partner_address_obj.search(cr, uid, [('partner_id','=',product_req_data.partner_id.id)], context=context)
		customer_type = partner_obj.browse(cr,uid,product_req_data.psd_sales_lines_id.partner_id.id).customer_type
		sku_data = self.pool.get('product.product').browse(cr,uid,sku_name_id)
		product_group_id = sku_data.generic_name.product_group_id
		type_product = sku_data.type_product
		if type_product == "track_equipment":
			res['track_equipment'] = True
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
				product_dealer=rec1.dealer
				#############changes added for the new fields shreyas
				res['batch_number'] =rec1.id
				res['manufacturing_date'] =rec1.manufacturing_date
			if len(search_rec) == 1:
				x = self.pool.get('res.batchnumber').browse(cr,uid,search_rec[0])
				res['product_basic_rate'] = x.distributor
				res['product_mrp'] = x.mrp
				product_dealer=x.dealer
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

psd_sales_lines()

class psd_sales_quotation_remarks(osv.osv):
	_name = "psd.sales.quotation.remarks"
	_description="Remarks"
	#_order="date desc"

	_columns = {
		'quotation_order_id': fields.many2one('psd.sales.product.quotation','notes'),
		#'user_name':fields.many2one('res.users','User Name'), 
		'user_name':fields.char('User Name',size=64),
		'date': fields.datetime('Date & Time'),
		'name': fields.text('Topic: Notes *',size=500),
		'state': fields.selection([	('new','New'),
									('pending','Pending'),
									('quoted','Quoted'),
									('ordered','Ordered'),
									('lost','Lost'),
									('revised','Revised'),
									],'State', readonly=True, select=True),
		'source':fields.many2one('res.company','Source'),
		}
psd_sales_quotation_remarks()

################Added view for the Quotation History Shreyas
class psd_quotation_history(osv.osv):
	_name = 'psd.quotation.history'

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'quotation_history_lines_id': fields.many2one('psd.sales.product.quotation','Quoation History ID'),
		'quotation_date': fields.date('Quotation Date'),
		'quotation_number': fields.char('Quotation Number',size=50),
		'quotation_amount': fields.float('Quotation Amount'),
		'previous_quotation_number': fields.char('Previous Quotation Number',size=50),
	}

	_defaults = {
		'company_id': _get_company
	}
	
psd_quotation_history()

class tax(osv.osv):
	_inherit="tax"
	_order="name desc"
	_columns={
		'psd_quotn_id':fields.many2one('psd.sales.product.quotation','PSD Quotation ID'),
	}

tax()
