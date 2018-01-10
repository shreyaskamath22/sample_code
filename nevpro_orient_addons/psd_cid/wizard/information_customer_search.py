from osv import osv,fields
from datetime import datetime
from openerp.tools.translate import _


class information_customer_search(osv.osv_memory):
	_name = 'information.customer.search'

	_columns = {
		'customer': fields.char('Customer/Company Name*',size=32),
		'contact': fields.char('Contact Number',size=32),
		'flat': fields.char('Flat No', size=32),
		'building': fields.char('Building Name',size=32),
		'sub_area': fields.char('Sub Area', size=32),
		'street': fields.char('Street',size=32),
		'landmark': fields.char('Landmark',size=32),
		'pincode': fields.char('Pin Code', size=32),
		'order_num': fields.char('Order No',size=32),
		'invoice_num': fields.char('Invoice Number', size=32),
		'information_customer_line_ids': fields.one2many('information.customer.line', 'information_customer_search_id', 'Customers'), 
	}

	def default_get(self, cr, uid, fields, context=None):
		customer_line_ids =[]
		if context is None: context = {}
		res = super(information_customer_search, self).default_get(cr, uid, fields, context=context)
		active_ids = context.get('active_ids')
		if active_ids:
			active_id = active_ids[0]
			information_req_obj = self.pool.get('product.information.request')
			partner_obj = self.pool.get('res.partner')
			complaint_cust_line_obj = self.pool.get('information.customer.line')
			information_req_data = information_req_obj.browse(cr, uid, active_id)
			customer = information_req_data.name
			if information_req_data.company_id.establishment_type == 'psd':
				customer_ids = partner_obj.search(cr, uid, [
						('name', 'ilike', customer),
						('customer','=',True),
						('company_id','=',information_req_data.company_id.id)], context=context) 
			else:
				customer_ids = partner_obj.search(cr, uid, [
						('name', 'ilike', customer),
						('customer','=',True),], context=context)  
			res_create_id = self.create(cr,uid,{'customer':customer})
			for customer_id in customer_ids:
				addrs_items = []
				address = ''
				partner = partner_obj.browse(cr,uid,customer_id)
				if partner.apartment not in [' ',False,None]:
					addrs_items.append(partner.apartment)
				if partner.building not in [' ',False,None]:
					addrs_items.append(partner.building)
				if partner.sub_area not in [' ',False,None]:
					addrs_items.append(partner.sub_area)
				if partner.landmark not in [' ',False,None]:
					addrs_items.append(partner.landmark)
				if partner.street not in [' ',False,None]:
					addrs_items.append(partner.street)
				if partner.city_id:
					addrs_items.append(partner.city_id.name1)
				if partner.district:
					addrs_items.append(partner.district.name)
				if partner.tehsil:
					addrs_items.append(partner.tehsil.name)
				if partner.state_id:
					addrs_items.append(partner.state_id.name)
				if partner.zip not in [' ',False,None]:
					addrs_items.append(partner.zip)
				if len(addrs_items) > 0:
					last_item = addrs_items[-1]
					for item in addrs_items:
						if item!=last_item:
							address = address+item+','+' '
						if item==last_item:
							address = address+item
				customer_line_id = ({
					'customer_name': partner.name,
					'complete_address': address,
					'contact_person': partner.contact_name,
					'contact_number': partner.phone_many2one.number,
					'partner_id': partner.id,
					'branch_id': partner.company_id.id
				 })
				customer_line_ids.append(customer_line_id)
		picking_ids = context.get('active_ids', [])
		if not picking_ids or (not context.get('active_model') == 'product.information.request') \
			or len(picking_ids) != 1:
			# Partial Picking Processing may only be done for one picking at a time
			return res
		picking_id, = picking_ids
		if 'customer' in fields:
			picking=self.pool.get('product.information.request').browse(cr,uid,picking_id,context=context)
			res.update(customer=picking.name)
		if 'information_customer_line_ids' in fields:
			picking = self.pool.get('information.customer.search').browse(cr, uid, picking_id, context=context)
			moves = [self._partial_move_for(cr, uid, m) for m in customer_line_ids]
			res.update(information_customer_line_ids=moves)
		return res

	def _partial_move_for(self, cr, uid, move):
		customer_name = move.get('customer_name')
		complete_address = move.get('complete_address')
		contact_person = move.get('contact_person')
		contact_number = move.get('contact_number')
		partner_id = move.get('partner_id')
		branch_id = move.get('branch_id')
		partial_move = {
			'customer_name': customer_name,
			'complete_address' : complete_address,
			'contact_person' : contact_person,
			'contact_number' : contact_number,
			'partner_id': partner_id,
			'branch_id': branch_id
		}
		return partial_move

	def search_information_customer(self,cr,uid,ids,context=None):
		partner_obj = self.pool.get('res.partner')
		info_cust_line_obj = self.pool.get('information.customer.line')
		information_req_obj = self.pool.get('product.information.request')
		active_ids = context.get('active_ids')
		if active_ids:
			active_id = active_ids[0]
		information_req_data = information_req_obj.browse(cr, uid, active_id) 
		res = False
		display_ids = []
		true_items = []
		domain = []
		information_customer_line_ids = []
		rec = self.browse(cr, uid, ids[0])
		if rec.information_customer_line_ids:
			for information_customer_line_id in rec.information_customer_line_ids:
				information_customer_line_ids.append(information_customer_line_id.id)    
			info_cust_line_obj.unlink(cr, uid, information_customer_line_ids, context=context)
		if rec.customer:
			true_items.append('name')
		if rec.contact:
			true_items.append('contact')    
		if rec.flat:
			true_items.append('flat')
		if rec.building:
			true_items.append('building') 
		if rec.sub_area:
			true_items.append('sub_area')
		if rec.street:
			true_items.append('street')
		if rec.landmark:
			true_items.append('landmark')
		if rec.pincode:
			true_items.append('pincode')                                     
		for true_item in true_items:
			if true_item == 'name':
				domain.append(('name', 'ilike', rec.customer))
			if true_item == 'contact':
				domain.append(('phone_many2one.number', 'ilike', rec.contact))  
			if true_item == 'flat':
				domain.append(('apartment', 'ilike', rec.flat))
			if true_item == 'building':
				domain.append(('building', 'ilike', rec.building))  
			if true_item == 'sub_area':
				domain.append(('sub_area', 'ilike', rec.sub_area))
			if true_item == 'street':
				domain.append(('street', 'ilike', rec.street))  
			if true_item == 'landmark':
				domain.append(('landmark', 'ilike', rec.landmark))
			if true_item == 'pincode':
				domain.append(('zip', 'ilike', rec.pincode)) 
		domain.append(('customer', '=', True))          
		if information_req_data.company_id.establishment_type == 'psd':
			domain.append(('company_id','=',information_req_data.company_id.id))  
		display_ids = partner_obj.search(cr, uid, domain, context=context)
		for display_id in display_ids:
			addrs_items = []
			cust_address = ''
			partner = partner_obj.browse(cr,uid,display_id)
			if partner.apartment:
				addrs_items.append(partner.apartment)
			if partner.building:
				addrs_items.append(partner.building)
			if partner.sub_area:
				addrs_items.append(partner.sub_area)
			if partner.landmark:
				addrs_items.append(partner.landmark)
			if partner.street:
				addrs_items.append(partner.street)
			if partner.city_id:
				addrs_items.append(partner.city_id.name1)
			if partner.district:
				addrs_items.append(partner.district.name)
			if partner.tehsil:
				addrs_items.append(partner.tehsil.name)
			if partner.state_id:
				addrs_items.append(partner.state_id.name)
			if partner.zip:
				addrs_items.append(partner.zip)
			if addrs_items:
				last_item = addrs_items[-1]
				for item in addrs_items:
					if item!=last_item:
						cust_address = cust_address+item+','+' '
					if item==last_item:
						cust_address = cust_address+item                
			res = info_cust_line_obj.create(cr,uid,
				{
					'customer_name': partner.name,
					'complete_address': cust_address,
					'contact_person': partner.contact_name,
					'contact_number': partner.phone_many2one.number,
					'information_customer_search_id':ids[0],
					'partner_id': partner.id,
					'branch_id': partner.company_id.id
				})
		return res

	def select_information_customer(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		information_req_obj = self.pool.get('product.information.request')
		information_req_line_obj = self.pool.get('information.request.line')
		information_cust_line_obj = self.pool.get('information.customer.line')
		partner_obj = self.pool.get('res.partner')
		customer = ''
		customer_id = ''
		lines = []
		customer_search_data = self.browse(cr, uid, ids[0])
		information_customer_line_ids = customer_search_data.information_customer_line_ids
		for line in information_customer_line_ids:
			if line.select_cust == True:
				lines.append(line.id)
				ou_id = partner_obj.browse(cr, uid, line.partner_id).ou_id
				partner = partner_obj.browse(cr, uid, line.partner_id)
				customer = line.customer_name
				customer_id = ou_id
		if len(lines) == 0:
			raise osv.except_osv(_('Warning!'),_("Please select one customer!"))                
		if len(lines) > 1:
			raise osv.except_osv(_('Warning!'), _("Multiple selection not allowed!"))
		active_id = context.get('active_id',False) 
		information_req_data = information_req_obj.browse(cr, uid, active_id)
		info_cust_line_data = information_cust_line_obj.browse(cr, uid, lines[0])
		if info_cust_line_data.branch_id.establishment_type == 'crm':
			location_branch = 'crm'
		elif info_cust_line_data.branch_id.id == information_req_data.company_id.id:
			location_branch = 'same'
		else:
			location_branch = 'different'
		information_req_obj.write(cr, uid, active_id, 
			{
				'name': customer,
				'location_branch': location_branch,
				'title': partner.title,
				'customer_address':info_cust_line_data.complete_address,
				'contact_name':info_cust_line_data.contact_person,
				'branch_id':info_cust_line_data.branch_id.id,
				'email':partner.email,
				'fax':partner.fax,
				'partner_id':partner.id,
				'customer_id': customer_id,
				'phone_many2one':partner.phone_many2one.id,
				'customer_type': 'existing',
				'selected':True,
			},context=context)
		return {'type': 'ir.actions.act_window_close'}
		
	def clear_information_customer(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'customer':None,'contact':None,'address':None,'invoice_num':None})

	
information_customer_search()

class information_customer_line(osv.osv_memory):
	_name='information.customer.line'  

	_columns = {
		'information_customer_search_id': fields.many2one('information.customer.search', 'information Customer Search'),
		'customer_name': fields.char('Customer Name',size=32),
		'complete_address': fields.char('Address',size=100),
		'contact_person': fields.char('Contact Person',size=32),
		'contact_number': fields.char('Contact Number',size=32),
		'select_cust': fields.boolean('Select Customer'),
		'partner_id': fields.integer('Partner ID'),
		'branch_id':fields.many2one('res.company','PCI Office'),
	}
	 
	def select_cust_details(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids[0],{'select_cust':True},context)
		return True

	def deselect_cust_details(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids[0],{'select_cust':False})
		return True

information_customer_line()   
