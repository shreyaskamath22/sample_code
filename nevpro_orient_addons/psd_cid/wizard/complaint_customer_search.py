from osv import osv,fields
from datetime import datetime
from openerp.tools.translate import _


class complaint_customer_search(osv.osv_memory):
    _name = 'complaint.customer.search'

    _columns = {
        'customer': fields.char('Customer/Company Name',size=32),
        'contact': fields.char('Contact No',size=32),
        'flat': fields.char('Flat No', size=32),
        'building': fields.char('Building Name',size=32),
        'sub_area': fields.char('Sub Area', size=32),
        'street': fields.char('Street',size=32),
        'landmark': fields.char('Landmark',size=32),
        'pincode': fields.char('Pin Code', size=32),
        'order_num': fields.char('Order No',size=32),
        'invoice_num': fields.char('Invoice No', size=32),
        'complaint_customer_line_ids': fields.one2many('complaint.customer.line', 'complaint_customer_search_id', 'Customers'), 
    }

    def default_get(self, cr, uid, fields, context=None):
        customer_line_ids =[]
        if context is None: context = {}
        res = super(complaint_customer_search, self).default_get(cr, uid, fields, context=context)
        active_ids = context.get('active_ids')
        if active_ids:
            active_id = active_ids[0]
            complaint_req_obj = self.pool.get('product.complaint.request')
            partner_obj = self.pool.get('res.partner')
            complaint_cust_line_obj = self.pool.get('complaint.customer.line')
            complaint_req_data = complaint_req_obj.browse(cr, uid, active_id)
            customer = complaint_req_data.customer
            if complaint_req_data.company_id.establishment_type == 'psd':
                customer_ids = partner_obj.search(cr, uid, [
                        ('name', 'ilike', customer),
                        ('customer','=',True),
                        ('company_id','=',complaint_req_data.company_id.id)], context=context) 
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
        if not picking_ids or (not context.get('active_model') == 'product.complaint.request') \
            or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        picking_id, = picking_ids
        if 'customer' in fields:
            picking=self.pool.get('product.complaint.request').browse(cr,uid,picking_id,context=context)
            res.update(customer=picking.customer)
        if 'complaint_customer_line_ids' in fields:
            picking = self.pool.get('complaint.customer.search').browse(cr, uid, picking_id, context=context)
            moves = [self._partial_move_for(cr, uid, m) for m in customer_line_ids]
            res.update(complaint_customer_line_ids=moves)
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

    def search_complaint_customer(self,cr,uid,ids,context=None):
        partner_obj = self.pool.get('res.partner')
        comp_cust_line_obj = self.pool.get('complaint.customer.line')
        complaint_req_obj = self.pool.get('product.complaint.request')
        active_ids = context.get('active_ids') 
        if active_ids:
            active_id = active_ids[0]
        complaint_req_data = complaint_req_obj.browse(cr, uid, active_id)  
        res = False
        display_ids = []
        true_items = []
        domain = []
        complaint_customer_line_ids = []
        rec = self.browse(cr, uid, ids[0])
        if rec.complaint_customer_line_ids:
            for complaint_customer_line_id in rec.complaint_customer_line_ids:
                complaint_customer_line_ids.append(complaint_customer_line_id.id)    
            comp_cust_line_obj.unlink(cr, uid, complaint_customer_line_ids, context=context)
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
        if complaint_req_data.company_id.establishment_type == 'psd':
            domain.append(('company_id','=',complaint_req_data.company_id.id))       
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
            res = comp_cust_line_obj.create(cr,uid,
                {
                    'customer_name': partner.name,
                    'complete_address': cust_address,
                    'contact_person': partner.contact_name,
                    'contact_number': partner.phone_many2one.number,
                    'complaint_customer_search_id':ids[0],
                    'partner_id': partner.id,
                    'branch_id': partner.company_id.id
                })
        return res

    def select_complaint_customer(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id',False)     
        complaint_req_obj = self.pool.get('product.complaint.request')
        complaint_req_line_obj = self.pool.get('product.complaint.request.line')
        complaint_cust_line_obj = self.pool.get('complaint.customer.line')
        partner_obj = self.pool.get('res.partner')
        partner_addr_obj = self.pool.get('res.partner.address')
        complaint_loc_obj = self.pool.get('product.complaint.locations')
        complaint_loc_contact_obj = self.pool.get('complaint.locations.contact')
        phone_obj = self.pool.get('phone.number.new.psd')
        phone_num_child_obj = self.pool.get('phone.number.child')
        complaint_phone_id = False
        loc_ids = []
        contact_ids = []
        phone_ids = []
        contact_persons = []
        phone_numbers = []
        customer_search_data = self.browse(cr, uid, ids[0])
        complaint_customer_line_ids = complaint_cust_line_obj.search(cr, uid, [('complaint_customer_search_id','=',ids[0]),('select_cust','=',True)], context=context)
        if len(complaint_customer_line_ids) == 0:
            raise osv.except_osv(_('Warning!'),_("Please select one customer!"))                
        if len(complaint_customer_line_ids) > 1:
            raise osv.except_osv(_('Warning!'), _("Multiple selection not allowed!"))
        complaint_cust_line_data = complaint_cust_line_obj.browse(cr, uid, complaint_customer_line_ids[0])    
        partner_data = partner_obj.browse(cr, uid, complaint_cust_line_data.partner_id)
        customer = complaint_cust_line_data.customer_name
        customer_id = partner_data.ou_id
        partner_id = partner_data.id
        complaint_req_obj.write(cr, uid, active_id, 
            {
                'customer': customer,
                'customer_id': customer_id,
                'partner_id': partner_id,
                'customer_type': 'existing',
            },context=context)
        complaint_line_ids = complaint_req_line_obj.search(cr, uid, [('complaint_id','=',active_id)], context=context)
        complaint_req_line_obj.unlink(cr, uid, complaint_line_ids, context=context)
        complaint_loc_ids = complaint_loc_obj.search(cr, uid, [('complaint_id','=',active_id)], context=context)
        complaint_loc_obj.unlink(cr, uid, complaint_loc_ids, context=context)
        complaint_contact_ids = complaint_loc_contact_obj.search(cr, uid, [('complaint_id','=',active_id)], context=context)
        complaint_loc_contact_obj.unlink(cr, uid, complaint_contact_ids, context=context)
        complaint_phone_ids = phone_obj.search(cr, uid, [('complaint_request_id','=',active_id)], context=context)
        phone_obj.unlink(cr, uid, complaint_phone_ids, context=context)
        address_ids = partner_addr_obj.search(cr, uid, [('partner_id','=',partner_id)], context=context)
        for address_id in address_ids:
            addrs_items = []
            complete_address = ''
            contact_person = ''
            addr_data = partner_addr_obj.browse(cr, uid, address_id)
            if addr_data.first_name and addr_data.last_name and not addr_data.middle_name:
                contact_person =  addr_data.first_name+' '+ addr_data.last_name
            if addr_data.first_name and addr_data.last_name and addr_data.middle_name:
                contact_person =  addr_data.first_name+' '+addr_data.middle_name+' '+addr_data.last_name    
            if addr_data.apartment not in [' ',False,None]:
                addrs_items.append(addr_data.apartment)
            if addr_data.building not in [' ',False,None]:
                addrs_items.append(addr_data.building)
            if addr_data.sub_area not in [' ',False,None]:
                addrs_items.append(addr_data.sub_area)
            if addr_data.landmark not in [' ',False,None]:
                addrs_items.append(addr_data.landmark)
            if addr_data.street not in [' ',False,None]:
                addrs_items.append(addr_data.street)
            if addr_data.city_id:
                addrs_items.append(addr_data.city_id.name1)
            if addr_data.district:
                addrs_items.append(addr_data.district.name)
            if addr_data.tehsil:
                addrs_items.append(addr_data.tehsil.name)
            if addr_data.state_id:
                addrs_items.append(addr_data.state_id.name)
            if addr_data.zip not in [' ',False,None]:
                addrs_items.append(addr_data.zip)
            if len(addrs_items) > 0:
                last_item = addrs_items[-1]
                for item in addrs_items:
                    if item!=last_item:
                        complete_address = complete_address+item+','+' '
                    if item==last_item:
                        complete_address = complete_address+item
            complaint_loc_vals = {
                'complaint_id': active_id,
                'name': complete_address,
                'address_id': addr_data.id,
            }
            loc_id = complaint_loc_obj.create(cr, uid, complaint_loc_vals,context=context)
            loc_ids.append(loc_id)
            contact_persons.append(contact_person)
            if addr_data.phone_m2m_xx:
                phone_number = addr_data.phone_m2m_xx.name
                phone_numbers.append(phone_number)
            contact_id = complaint_loc_contact_obj.create(cr, uid, {'complaint_id':active_id,'name':contact_person,'loc_id':loc_id}, context=context)
            contact_ids.append(contact_id)
            phone_num_child_ids = phone_num_child_obj.search(cr, uid, [('partner_id','=',partner_id)], context=context)
            for each in phone_num_child_ids:
                phone_num_data = phone_num_child_obj.browse(cr, uid, each)
                phone_id = phone_obj.create(cr, uid, {
                    'complaint_request_id': active_id,
                    'number': phone_num_data.number,
                    'type': phone_num_data.contact_select
                    }, context=context)
                phone_ids.append(phone_id)
        complaint_req_line_obj.create(cr, uid, {
            'complaint_id': active_id,
            'customer_type': 'existing',
            'contact_person': contact_persons[0] if contact_persons else None,
            'phone_number': phone_numbers[0] if phone_numbers else None,
            'location_id': loc_ids[0] if loc_ids else None,
            # 'loc_contact_id': contact_ids[0],
            # 'loc_phone_id': phone_ids and phone_ids[0] or False,
            'pci_office':complaint_cust_line_data.branch_id.id,
            }, context=context)
        return {'type': 'ir.actions.act_window_close'}
        
    def clear_complaint_customer(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'customer':None,'contact':None,'address':None,'invoice_num':None})

complaint_customer_search()

class complaint_customer_line(osv.osv_memory):
    _name='complaint.customer.line'  

    _columns = {
        'complaint_customer_search_id': fields.many2one('complaint.customer.search', 'Complaint Customer Search'),
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

complaint_customer_line()   