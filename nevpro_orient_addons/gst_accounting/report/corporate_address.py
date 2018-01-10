
#1.0.041 for removed hardcoded address,mail,phoneno,website
from osv import osv,fields
import pooler,time
from datetime import datetime,timedelta

def get_corporate_address(self):
    cr=self.cr
    uid=self.uid
    dic_new_corp_addr = {
        'get_corporate_addr_dict':'',
        'get_email_addr_dict':'',
        'get_website_addr_dict':'',
        'get_corporate_phone_dict':'',
         }
    
    corp_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','corp_office')])
    for c_add in self.pool.get('res.company').browse(cr,uid,corp_id):
        floor = c_add.floor 
        apartment = c_add.apartment
        building = c_add.building
        sub_area = c_add.sub_area
        street = c_add.street
        landmark = c_add.landmark
        state_id = c_add.state_id.name
        city_id = c_add.city_id.name1
        tehsil = c_add.tehsil
        district = c_add.district
        zipc = c_add.zip
        address=[apartment,building,floor,sub_area,street,landmark,tehsil,district,city_id,state_id,zipc]
        addr=', '.join(filter(bool,address))
        dic_new_corp_addr['get_corporate_addr_dict'] = addr
        dic_new_corp_addr['get_email_addr_dict'] = c_add.email
        dic_new_corp_addr['get_website_addr_dict'] = c_add.website
        dic_new_corp_addr['get_corporate_phone_dict'] = c_add.phone
        
    return dic_new_corp_addr
    
    
def get_registered_office_address(self):
    cr=self.cr
    uid=self.uid
    dic_new_regd_addr = {
        'get_registered_office_addr_dict':'',
         }
    
    regd_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','regd_office')])
    for r_add in self.pool.get('res.company').browse(cr,uid,regd_id):
        floor = r_add.floor 
        apartment = r_add.apartment
        building = r_add.building
        sub_area = r_add.sub_area
        street = r_add.street
        landmark = r_add.landmark
        state_id = r_add.state_id.name
        city_id = r_add.city_id.name1
        tehsil = r_add.tehsil
        district = r_add.district
        zipc = r_add.zip
        address=[apartment,building,floor,sub_area,street,landmark,tehsil,district,city_id,state_id,zipc]
        addr=', '.join(filter(bool,address))
        dic_new_regd_addr['get_registered_office_addr_dict'] = addr

    return dic_new_regd_addr
    
def get_cust_care(self):
    cr=self.cr
    uid=self.uid
    n_crm_phone_no=[]
    n_crm_srch=self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
    for n_brw_crm in self.pool.get('res.company').browse(cr,uid,n_crm_srch) :
            n_crm_phone_no.append(n_brw_crm.phone)
    n_call_phone='/'.join(n_crm_phone_no)   
    
    return n_call_phone

def get_branch_addr(self,self_id):
	
	cr = self.cr
	uid = self.uid
	dic = {
		'branch_addr':'',
		'cin':'',
		'branch_code':'',
		 }
	for r_add in self.pool.get('res.company').browse(cr,uid,[self_id]):
		floor = r_add.floor 
		apartment = r_add.apartment
		building = r_add.building
		sub_area = r_add.sub_area
		street = r_add.street
		landmark = r_add.landmark
		state_id = r_add.state_id.name 
		city_id = r_add.city_id.name1+" - " if  r_add.city_id.name1 else ' ' 
		city_area = r_add.city_area
		tehsil = r_add.tehsil
		district = r_add.district
		
		zipc = r_add.zip
		if zipc:
			city_id = city_id +zipc
		else:
			city_id = city_id
		
		address=[apartment,floor,building,street,sub_area,landmark,city_area,district,tehsil,city_id,state_id]
		addr=', '.join(filter(bool,address))
		dic['branch_addr'] = addr
		dic['cin'] = 'CIN :' + r_add.cin_no if r_add.cin_no else ''  
		dic['branch_code'] = 'Branch Code : ' + r_add.pcof_key if r_add.pcof_key else '' 
		         
	return dic

def convert_to_double_precision(amount):
	return  str("%.2f" % abs(amount))

def get_pms_location_addr(self,self_id):
	cr = self.cr
	uid = self.uid
	dic = {
		'pms_location_addr':'',
		 }
	for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
		for res1 in res.invoice_line_adhoc_11:
			if res1:
				for res2 in self.pool.get('new.address').browse(cr,uid,[res1.location.id]):
					location_name=res2.location_name
					apartment=res2.apartment
					building=res2.building
					sub_area=res2.sub_area
					street=res2.street
					landmark=res2.landmark
					city=res2.city_id.name1
					state=res2.state_id.name  +" - " if  res2.state_id.name else ' ' 
					zipb=res2.zip
					
					if zipb:
						state = state +zipb
					else:
						state = state
						
				pms_address=[location_name,apartment,building,street,sub_area,landmark,city,state]
				addr=', '.join(filter(bool,pms_address))
				dic['pms_location_addr'] = addr

		for res3 in res.invoice_line_adhoc:
			if res3:
				for res4 in self.pool.get('res.partner.address').browse(cr,uid,[res3.location_invoice.id]):
					location_name=res4.location_name
					apartment=res4.apartment
					building=res4.building
					sub_area=res4.sub_area
					street=res4.street
					landmark=res4.landmark
					city=res4.city_id.name1
					state=res4.state_id.name  +" - " if  res4.state_id.name else ' '
					zipb=res4.zip
					
					if zipb:
						state = state +zipb
					else:
						state = state
				pms_address=[location_name,apartment,building,street,sub_area,landmark,city,state]
				addr=', '.join(filter(bool,pms_address))
				dic['pms_location_addr'] = addr
			
	return dic

def get_contract_val(self,self_id):
	cr = self.cr
	uid = self.uid
	dic = {'cotract_val':'',}
	
	for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
		if res.contract_no:
        		for pay in self.pool.get('sale.contract').browse(cr,uid,[res.contract_no.id]):
	        		dic['cotract_val'] = pay.grand_total_amount

	return dic


def get_cust_addr(self,self_id):
	cr = self.cr
	uid = self.uid
	dic = {
		'cust_addr1':'',
		'cust_addr2':'',
		
		 }
	for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
		if not res.location:
			premise = res.partner_id.premise_type if res.partner_id.premise_type else ''
			location_name = res.partner_id. location_name if res.partner_id.location_name else ''
				
			apartment = res.partner_id.apartment if res.partner_id.apartment else ''
			building = res.partner_id.building if res.partner_id.building else ''
			sub_area = res.partner_id.sub_area if res.partner_id.sub_area else ''
			street = res.partner_id.street if res.partner_id.street else ''
			landmark = res.partner_id.landmark if res.partner_id.landmark else ''
			state_id = res.partner_id.state_id.name if res.partner_id.state_id.name else ''
			city_id = res.partner_id.city_id.name1 if res.partner_id.city_id.name1 else ''
			zip1 = res.partner_id.zip if res.partner_id.zip else ''
			if zip1:
				zip1 = city_id +'-'+zip1
			else:
				zip1 = city_id
				
			tehsil = res.partner_id.tehsil.name if res.partner_id.tehsil.name else ''
			district = res.partner_id.district.name if res.partner_id.district.name else ''
			address1=[location_name,apartment,building,sub_area]
			address2 =[street,landmark,state_id,zip1,tehsil,district]
			addr1=', '.join(filter(bool,address1))
			addr2=', '.join(filter(bool,address2))
			dic['cust_addr1'] = addr1
			dic['cust_addr2'] = addr2
				
		else:
			#premise = res.partner_id.premise_type if res.partner_id.premise_type else ''
			location_name = res.location.location_name if res.location.location_name else ''
			apartment = res.location.apartment if res.location.apartment else ''
			building = res.location.building if res.location.building else ''
			sub_area = res.location.sub_area if res.location.sub_area else ''
			street = res.location.street if res.location.street else ''
			landmark = res.location.landmark if res.location.landmark else ''
			state_id = res.location.state_id.name if res.location.state_id.name else ''
			city_id = res.location.city_id.name1 if res.location.city_id.name1 else ''
			zip1 = res.location.zip if res.location.zip else ''
			if zip1:
				zip1 = city_id +'-'+zip1
			else:
				zip1 = city_id
			tehsil = res.location.tehsil.name if res.location.tehsil.name else ''
			district = res.location.district.name if res.location.district.name else ''
			address1=[location_name,apartment,building,sub_area]
			address2 =[street,landmark,state_id,zip1,tehsil,district]
			addr1=', '.join(filter(bool,address1))
			addr2=', '.join(filter(bool,address2))
			dic['cust_addr1'] = addr1
			dic['cust_addr2'] = addr2                    

	return dic

def get_payment(self,self_id):
	cr = self.cr
	uid = self.uid
	dic = {
		'pay_term':'',           
		}
	for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
		for pay in list_payment_term:
			if res.payment_term == pay[0]:
				dic['pay_term'] = pay[1]
	return dic

def tax_label(self, srch_ids):
        cr = self.cr
	uid = self.uid
	res = ''
	for name in self.pool.get('invoice.adhoc.master').browse(cr,uid,[srch_ids]):
	        for line in name.tax_one2many:
	                res +=line.name +" \n\n\n "
	return res 
		
		
def tax_label_amount(self,srch_ids):
        cr = self.cr
	uid = self.uid
	res = ''
	for name in self.pool.get('invoice.adhoc.master').browse(cr,uid,[srch_ids]):
	        for line in name.tax_one2many:
	                res +=str("%.2f" %line.amount) +" \n\n\n "
	return res



def get_current_time(self):
    now=datetime.now()+timedelta(hours=5,minutes=30)
    return datetime.strftime(now, '%I:%M %p')+' ' +time.strftime('%d') + '-' + now.strftime('%b') + '-' + time.strftime('%Y')
    
def get_closing_balance(dr_amt,cr_amt):
        dic={'cr_bal':'','dr_bal':''}
        if dr_amt > cr_amt:
            dic['cr_bal']= str(dr_amt-cr_amt)+" Cr"
            dic['dr_bal']=''
        elif dr_amt < cr_amt:
            dic['cr_bal']= ''
            dic['dr_bal']=str(cr_amt-dr_amt)+" Dr"
        else:
            dic['cr_bal']= ''
            dic['dr_bal']= '0.00'

        return dic

