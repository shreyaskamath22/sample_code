# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv,fields
from datetime import date,datetime, timedelta
import xmlrpclib
import time
import os
import curses.ascii
import re


class res_partner_address(osv.osv):
	_inherit = 'res.partner.address'

	_columns = {
		'gst_no':fields.char('GST No.',size=124),
		'gst_type_customer':fields.many2one('gst.type.customer','Registration Type'),
	}

	def save_record(self,cr,uid,ids,context=None):
		lead_obj = self.pool.get('res.partner.branch.new')
		premise_type=''
		credit_period=0
		conn_flag=False
		for rec in self.browse(cr,uid,ids,context=None):  
		    branch_type = self.pool.get('res.company').search(cr,uid,[('type','=','ccc')])
		    if not rec.apartment:
		        raise osv.except_osv(('Alert!'),('Please Enter Flat/Apartment Number.'))
		    if not rec.building:
		        raise osv.except_osv(('Alert!'),('Please Enter Building/Society Name.'))
		    if not rec.city_id:
		        raise osv.except_osv(('Alert!'),('Please Enter City.'))
		    if not rec.state_id:
		        raise osv.except_osv(('Alert!'),('Please Enter State.'))
		    if rec.gst_no and rec.gst_no != 'Unregistered':
		        test_gst_no=re.match(r'^([0-9]){2}([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}([a-zA-Z0-9]){3}$',rec.gst_no)
		        if not test_gst_no:
		            raise osv.except_osv(('Alert'),('Please verify the GST No.'))
		        if rec.state_id.state_code != rec.gst_no[0:2]:
		            raise osv.except_osv(('Alert'),('Please verify the State Code'))
		    search_phone_id = self.pool.get('phone.m2m').search(cr,uid,[('res_location_id','=',rec.id)]) 
		    #ccp task pratik started
		    premise_type=rec.premise_type
		    total_id = self.pool.get('premise.type.master').search(cr,uid,[('key','=',premise_type)])
		    for get_val in self.pool.get('premise.type.master').browse(cr,uid,total_id):
		         get_ids= self.pool.get('credit.period').search(cr,uid,[('name','=',get_val.select_type)])
		         for period in self.pool.get('credit.period').browse(cr,uid,get_ids):
		                        credit_period=period.credit_period    
		        # if get_val.select_type == 'cbu':
		        #     credit_period=30
		        # if get_val.select_type == 'rbu':
		        #     credit_period=1
		    if str(rec.first_name).find("'")!=-1 or str(rec.middle_name).find("'")!=-1 or str(rec.last_name).find("'")!=-1 or str(rec.designation).find("'")!=-1 or str(rec.location_name).find("'")!=-1 or str(rec.apartment).find("'")!=-1 or str(rec.building).find("'")!=-1 or str(rec.sub_area).find("'")!=-1 or str(rec.street).find("'")!=-1 or str(rec.landmark).find("'")!=-1 or str(rec.zip).find("'")!=-1 :
				raise osv.except_osv(('Alert!'),('Please remove the single quote from the field'))

		    search_id=rec.id
		    #search=self.pool.get('ccc.new.address').search(cr,uid,[('new_customer_id1','=',rec.id)])
		    #if not search:
		    check=True
		    address_id = self.pool.get('ccc.new.address').create(cr,uid,{'new_customer_id1':context.get('ccc_branch_new_ids')[0] if context.get('ccc_branch_new_ids') else '','premise_type':rec.premise_type,'title':rec.title,'building':rec.building,'apartment':rec.apartment,'location_name':rec.location_name,'sub_area':rec.sub_area,'street':rec.street,'landmark':rec.landmark,'state_id':rec.state_id.id,'city_id':rec.city_id.id,'district':rec.district.id,'tehsil':rec.tehsil.id,'zip':rec.zip,'email':rec.email,'fax':rec.fax,'mobile':rec.mobile,'first_name':rec.first_name,'middle_name':rec.middle_name,'last_name':rec.last_name,'designation':rec.designation,},context=None)
		    '''if rec.phone_many2one:
			search_phone_id = self.pool.get('phone.number.child.new').search(cr,uid,[('partner_id_new_cust','=',rec.id)])
		    	for iterate in self.pool.get('phone.number.child.new').browse(cr,uid,search_phone_id):
				phone_m2m_id = self.pool.get('phone.m2m').create(cr,uid,{'name':iterate.number,'type':iterate.contact_select,'ccc_new_address_id':address_id})
				self.pool.get('ccc.new.address').write(cr,uid,address_id,{'phone_m2m_xx':phone_m2m_id})'''
		    self.pool.get('res.partner.address').write(cr,uid,ids,{'ccc_branch_new_id':context.get('ccc_branch_new_ids')[0] if context.get('ccc_branch_new_ids') else '','partner_id':rec.partner_id.id,'credit_period_days':credit_period}) 
		    cr.commit()
		  
		    if context.get('check_model') == 'res_partner':
		        
		        partner_id = rec.partner_id.id
		        partner_obj = self.pool.get('res.partner')
		        city_list_id = []
		        state_ids = []
		        company_ids= []
		        partner_ids = []


		        search_id = self.pool.get('res.company').search(cr,uid,[('type','=','ccc')])
				
			self.pool.get('new.address').create(cr,uid,{'zip':rec.zip,
											    'title':rec.title,
											    'last_name':rec.last_name,
											    'first_name':rec.first_name,
											    'middle_name':rec.middle_name,
											    'designation':rec.designation,
											    'last_name':rec.last_name,
											    'first_name':rec.first_name,
											    'middle_name':rec.middle_name,
											    'designation':rec.designation,
											    'partner_id':rec.partner_id.id,
											    'premise_type':rec.premise_type,
		                                        'location_name':rec.location_name,#abhi
											    'apartment':rec.apartment,
											    'building':rec.building,
											    'sub_area':rec.sub_area,
		                                        'partner_address':rec.id,
											    'tehsil':rec.tehsil.id,
											    'district':rec.district.id,
											    'city_id':rec.city_id.id if rec.city_id else '',
											    'state_id':rec.state_id.id if rec.state_id else '',
											    'street':rec.street,
											    'email':rec.email,
											    'fax':rec.fax,})		

			if search_id:
				for res in self.pool.get('res.company').browse(cr,uid,[search_id[0]]):
		                            vpn_ip_addr = res.vpn_ip_address
					    port =res.port
					    dbname = res.dbname
					    pwd = res.pwd
					    user_name = str(res.user_name.login)
					    city_list_id = []
					    state_ids =[]
					    username = user_name 
					    pwd = pwd   
					    dbname = dbname
			
					    log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
					    obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
					    sock_common = xmlrpclib.ServerProxy (log)
		                            print "USER",user_name,pwd,dbname
					    try:
						
									raise	
									uid = sock_common.login(dbname, username, pwd)
					    except Exception as Err:
									#raise osv.except_osv(('Alert!'),('Connection to the Server Failed'))
		                                                        conn_flag = True
		                                                        #offline_obj=self.pool.get('sale.offline.sync')
									#offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
									#if not offline_sync_sequence:
									#		offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'save_record1','error_log':Err,})
									#else:
									#		offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
									#		offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})						
					    sock = xmlrpclib.ServerProxy(obj)
		                            if conn_flag:
						company_name = ''
						insert_crm_lead=''
						main_sql_str=''
						time_cur = time.strftime("%H:%M:%S")
						date = datetime.now().date()
						company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
						if company_id[0]:
							company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
							current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.name
						current_company=('_').join(current_company.split(' '))
						con_cat = company_name+'_'+current_company+'_ExistingCustomer_Add_New_location_'+str(date)+'_'+str(time_cur)+'.sql'
						filename = os.path.expanduser('~')+'/sql_files/'+con_cat
						directory_name = str(os.path.expanduser('~')+'/sql_files/')
						d = os.path.dirname(directory_name)
						if not os.path.exists(d):
							os.makedirs(d)
						d = os.path.dirname(directory_name)
						func_string ="\n\n CREATE OR REPLACE FUNCTION Add_New_location() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
						ret="\n RETURN 1;\n"
						declare=" DECLARE \n \t"
						var="city_list_ids int;\nstate_ids int;\nbranch_srch_id int;\npartner_ids int;\nBEGIN \ncity_list_ids:=Null;\nstate_ids:=Null;\n"
						final="\nEND; \n $$;\n"
						fun_call="\n SELECT Add_New_location();\n"
						'''with open (filename,'a') as f :
							f.write(func_string)
							f.write(declare)
							f.write(var)
							f.close()'''
		                                if rec.city_id:
									    city_srch = [('name1', '=',rec.city_id.name1)]
									    #city_list_id = sock.execute(dbname, uid, pwd, 'city.name', 'search', city_srch)
		                                                            main_sql_str += "\n city_list_ids=(select id from city_name where name1='%s'); " %(str(rec.city_id.name1))
		                                if rec.state_id:
									    state_srch = [('name', '=',rec.state_id.name)] 
									    #state_ids = sock.execute(dbname, uid, pwd, 'state.name', 'search', state_srch)	
		                                                            main_sql_str += "\n state_ids=(select id from state_name where name='%s');" %(str(rec.state_id.name))
						

		                                  	    
						partner_obj = self.pool.get('res.partner')
						company_id_srch = [('name', '=',partner_obj.browse(cr,uid,partner_id).company_id.name)]
		                                #branch_srch_id = sock.execute(dbname, uid, pwd, 'res.company', 'search', company_id_srch)
						main_sql_str += "\n branch_srch_id=(select id from res_company where name='%s');" %(str(partner_obj.browse(cr,uid,partner_id).company_id.name))
					
		                                if partner_id:
									        #partner_id_srch = [('customer_id_main', '=',str(partner_obj.browse(cr,uid,partner_id).customer_id_main)),('branch_id','=',branch_srch_id[0])]
									        #partner_ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search', partner_id_srch)
										main_sql_str += "\n partner_ids=(select id from res_partner where customer_id_main='%s' and branch_id=branch_srch_id);" %(str(partner_obj.browse(cr,uid,partner_id).customer_id_main))
		                                
		                                address_line = {
											        'zip':rec.zip,
											        'title':rec.title,
											        'last_name':rec.last_name,
											        'first_name':rec.first_name,
											        'middle_name':rec.middle_name,
											        'designation':rec.designation,
											        'last_name':rec.last_name,
											        'first_name':rec.first_name,
											        'middle_name':rec.middle_name,
											        'designation':rec.designation,
											        'partner_id':partner_ids[0] if partner_ids else False,
											        'premise_type':rec.premise_type,
		                                            'location_name':rec.location_name,#abhi
											        'apartment':rec.apartment,
											        'building':rec.building,
											        'sub_area':rec.sub_area,
											        'tehsil':rec.tehsil.id,
											        'district':rec.district.id,
											        'city_id':city_list_id[0] if city_list_id else '',
											        'state_id':state_ids[0] if state_ids else '',
											        'street':rec.street,
											        'email':rec.email,
											        'fax':rec.fax,
		                                            'credit_period_days':credit_period,
											        }
		                                #address = (sock.execute(dbname, uid, pwd, 'res.partner.address', 'create', address_line))
						#main_sql_str += "\n insert into res_partner_address(zip,title,last_name,first_name,middle_name,designation,partner_id,premise_type,location_name,apartment,building,sub_area,tehsil,district,city_id,state_id,street,email,fax,credit_period_days) values('"+str(rec.zip)+"','"+str(rec.title)+"','"+str(rec.last_name)+"','"+str(rec.first_name)+"','"+str(rec.middle_name)+"','"+str(rec.designation)+"',partner_ids,'"+str(rec.premise_type)+"','"+str(rec.location_name)+"','"+str(rec.apartment)+"','"+str(rec.building)+"','"+str(rec.sub_area)+"',(select id from tehsil_name where name='"+str(rec.tehsil.name)+"'),(select id from district_name where name='"+str(rec.district.name)+"'),city_list_ids,state_ids,'"+str(rec.street)+"','"+str(rec.email)+"','"+str(rec.fax)+"',"+str(credit_period)+");"


		                                
						phone_number_ids= []				
		                                
		                                #for iter_phone in self.pool.get('phone.m2m').browse(cr,uid,search_phone_id):
						#				                phone_number_partner = {
						#					                'res_location_id':address if address else '',
						#					                'name':iter_phone.name,
						#					                'type':iter_phone.type,
						#					
						#					                }
						#		
						#				
						#				                phone_number_ids = sock.execute(dbname, uid, pwd, 'phone.m2m', 'create',phone_number_partner)
		                                len_address = self.pool.get('customer.line').search(cr,uid,[('partner_id','=',partner_id)])

		                                location_id= ''
		                                if len(len_address) <= 9:
								        location_id = '0000'+partner_obj.browse(cr,uid,partner_id).customer_id_main+'0'+str(len(len_address)+1)
		                                else:
								        location_id = '0000'+partner_obj.browse(cr,uid,partner_id).customer_id_main+str(len(len_address)+1)
							


						cust_line_vals = {'location_id':location_id,'partner_id':partner_id,'principle_place_of_business_tag':rec.principle_place_of_business_tag.id,'special_status':rec.special_status.id,'gst_no':str(rec.gst_no),'customer_address':rec.id,'branch':partner_obj.browse(cr,uid,partner_id).company_id.id,'credit_period':credit_period,'phone_many2one':search_phone_id[0] if search_phone_id else ''}
		                                cust_line_id=self.pool.get('customer.line').create(cr,uid,cust_line_vals)
		                                self.pool.get('customer.line').write(cr,uid,cust_line_id,{'gst_no':rec.gst_no})
		                                #if conn_flag:
					    		
		                                #address_line = {
						#				                'location_id':location_id,
						#				                'phone_many2one':phone_number_ids if phone_number_ids else '',
						#				                'partner_id':partner_ids[0] if partner_ids else False,
						#				                'customer_address':address if address else '',
						#				                'branch':branch_srch_id[0] if branch_srch_id else '',
						#				                'credit_period':credit_period,
						#				
						#				                }
		                                #sock.execute(dbname, uid, pwd, 'customer.line', 'create', address_line)
						main_sql_str += "\n insert into res_partner_address(branch_id,location_id,zip,title,last_name,first_name,middle_name,designation,partner_id,premise_type,location_name,apartment,building,sub_area,tehsil,district,city_id,state_id,street,email,fax,credit_period_days) values((select id from res_company where name='"+str(partner_obj.browse(cr,uid,partner_id).company_id.name)+"'),'"+str(location_id if location_id else 'Null')+"','"+str(rec.zip if rec.zip else 'Null')+"','"+str(rec.title if rec.title else 'Null')+"','"+str(rec.last_name if rec.last_name else 'Null')+"','"+str(rec.first_name if rec.first_name else 'Null')+"','"+str(rec.middle_name if rec.middle_name else 'Null')+"','"+str(rec.designation if rec.designation else 'Null')+"',partner_ids,'"+str(rec.premise_type if rec.premise_type else 'Null')+"','"+str(rec.location_name if rec.location_name else 'Null')+"','"+str(rec.apartment if rec.apartment else 'Null')+"','"+str(rec.building if rec.building else 'Null')+"','"+str(rec.sub_area if rec.sub_area else 'Null')+"',(select id from tehsil_name where name='"+str(rec.tehsil.name)+"'),(select id from district_name where name='"+str(rec.district.name)+"'),city_list_ids,state_ids,'"+str(rec.street if rec.street else 'Null')+"','"+str(rec.email if rec.email else 'Null')+"','"+str(rec.fax if rec.fax else 'Null')+"',"+str(credit_period if credit_period else 0)+");"



						main_sql_str += "\n insert into customer_line(location_id,partner_id,customer_address,branch) values('%s',partner_ids,(select id from res_partner_address where location_id='%s' and branch_id=(select id from res_company where name='%s')),branch_srch_id);" %(str(location_id if location_id else 'Null'),str(location_id if location_id else 'Null'),str(partner_obj.browse(cr,uid,partner_id).company_id.name))
						with open (filename,'a') as f :
		                                        f.write(func_string)
		                                        f.write(declare)
		                                        f.write(var)
							f.write(main_sql_str)
							f.write(ret)
							f.write(final)
							f.write(fun_call)
							f.close()
	  

                return {'view_mode' : 'tree,form','type': 'ir.actions.act_window_close'}


	def save_edit_record(self,cr,uid,ids,context=None):
			
			form_id = False
			sock = ''
			dbname= ''
			pwd= ''
			partner_id = False
			address = False
			branch = False
			conn_flag=False
			result = []
			for k in self.browse(cr,uid,ids):
			    if k.zip :


									length = len(k.zip)
									if length < 6 or length > 6:
										raise osv.except_osv(('Alert!'),('Please Enter 6 Digit Pincode No.'))
									for xx in str(k.zip):
										result.append(curses.ascii.isdigit(xx))
									for res_id in result:
										if res_id==False or length < 6 or length > 6:
											raise osv.except_osv(('Alert!'),('Please Enter 6 Digit Pincode No.'))


			for res in self.browse(cr,uid,ids,context=None):
			    if not res.city_id:
				raise osv.except_osv(('Alert!'),('Please Enter City.'))
			    if not res.state_id:
				raise osv.except_osv(('Alert!'),('Please Enter State.'))
			    if res.gst_no and res.gst_no != 'Unregistered':
			        test_gst_no=re.match(r'^([0-9]){2}([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}([a-zA-Z0-9]){3}$',res.gst_no)
			        if not test_gst_no:
			            raise osv.except_osv(('Alert'),('Please verify the GST No.'))
			        if res.state_id.state_code != res.gst_no[0:2]:
			            raise osv.except_osv(('Alert'),('Please verify the State Code'))				
			    partner_id = res.partner_id.id
			    model = ''
			    city_srch_ids =[]
			    state_srch_ids = []
			    district_srch_ids = []
			    tehsil_srch_ids = []
			    form_id = []
			    #sock,dbname,uid,pwd = ''
			    model_branch = ''
			    loc_id = ''
			    if context is None : context ={}
			    active_model = context.get('active_model')

			    if active_model == 'res.partner' or active_model == 'res.partner.branch.new':
				model = 'res.partner.new'
				model_branch = 'res.partner.branch.new'
			    else:
				model = 'ccc.customer.request'
				model_branch = 'ccc.branch.new'
			    branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])

			    contact=[res.first_name ,res.middle_name ,res.last_name]
		       	    total_name=' '.join(filter(bool,contact))
			    if context:

								for x,y in context.iteritems():
									if x == 'form_id':

											form_id = y
			    					cust_line_srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',res.id)])
                                    				if cust_line_srch :
                                                			location_id_val = self.pool.get('customer.line').browse(cr,uid,cust_line_srch[0]).location_id

			                                                if location_id_val:
			                                                    loc_id = location_id_val[-2:]
								if loc_id == '01' or active_model != 'res.partner':
										if active_model=='res.partner.branch.new':
											self.pool.get(model_branch).write(cr,uid,form_id,{'title':res.title,'first_name':res.first_name,'email':res.email,'fax':res.fax,'middle_name':res.middle_name,'last_name':res.last_name,'designation':res.designation,'location_name':res.location_name,'apartment':res.apartment,'building':res.building,'sub_area':res.sub_area,'street':res.street,'city_id':res.city_id.id,'district':res.district.id,
		'tehsil':res.tehsil.id,'state_id':res.state_id.id,'zip':res.zip,'landmark':res.landmark,'premise_type':res.premise_type})
											cr.commit()
				                                if loc_id == '01':
				                                                                self.pool.get('res.partner').write(cr,uid,res.partner_id.id,{'title':res.title,'first_name':res.first_name,'middle_name':res.middle_name,'email':res.email,'fax':res.fax,'last_name':res.last_name,'designation':res.designation,'location_name':res.location_name,'apartment':res.apartment,'building':res.building,'sub_area':res.sub_area,'street':res.street,
		'city_id':res.city_id.id,'district':res.district.id,'tehsil':res.tehsil.id,'state_id':res.state_id.id,'zip':res.zip,'landmark':res.landmark,'premise_type':res.premise_type,'contact_name':total_name})
												cr.commit()
				                                customer_line = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',ids[0])])

								new_address_search = self.pool.get('new.address').search(cr,uid,[('partner_address','=',res.id)])
								if new_address_search:
									self.pool.get('new.address').write(cr,uid,new_address_search,{'apartment':res.apartment,'building':res.building,'sub_area':res.sub_area,'street':res.street,'city_id':res.city_id.id,'district':res.district.id,
		'tehsil':res.tehsil.id,'state_id':res.state_id.id,'zip':res.zip,'landmark':res.landmark,'premise_type':res.premise_type})
									inspection_ids=self.pool.get('inspection.costing.line').search(cr,uid,[('address_new','=',new_address_search)])
									if inspection_ids:
										for x in inspection_ids:
											self.pool.get('inspection.costing.line').write(cr,uid,x,{'apartment':res.apartment,'building':res.building,'sub_area':res.sub_area,'street':res.street,'city_id':res.city_id.id,'district':res.district.id,
					'tehsil':res.tehsil.id,'state_id':res.state_id.id,'zip':res.zip,'landmark':res.landmark,'premise_type':res.premise_type,'location_name':res.location_name})

								cse = ''
								service_area = ''
								principle_place_of_business_tag=''
								special_status=''
								gst_no=''
								if res.cse:
									cse = res.cse.id
								if res.service_area:
									service_area = res.service_area.id
								if res.principle_place_of_business_tag:
									principle_place_of_business_tag=res.principle_place_of_business_tag.id
								if res.special_status:
									special_status=res.special_status.id
								if res.gst_no:
									gst_no=res.gst_no

								self.pool.get('customer.line').write(cr,uid,customer_line,{'cse':cse,'service_area':service_area,'principle_place_of_business_tag':principle_place_of_business_tag,'special_status':special_status,'gst_no':gst_no})
								cr.commit()
				                                if customer_line:
												self.pool.get('customer.line').write(cr,uid,customer_line[0],{'credit_period':res.credit_period_days})

				                                                                branch_obj = self.pool.get('res.company')
				                                                                branch_id = self.pool.get('customer.line').browse(cr,uid,customer_line[0]).branch.id
												ccc_id = branch_obj.search(cr,uid,[('type','=','ccc')])
				                                                                location_id = self.pool.get('customer.line').browse(cr,uid,customer_line[0]).location_id
				                                                                #sock,dbname,uid,pwd = self.sync_param_req(cr,uid,ccc_id[0])
												branch_type = self.pool.get('res.company').search(cr,uid,[('type','=','ccc')])
												for rec in self.pool.get('res.company').browse(cr,uid,branch_type):
													vpn_ip_addr = rec.vpn_ip_address
													port = rec.port
													dbname = rec.dbname
													pwd = rec.pwd
													user_name = str(rec.user_name.login)
													username = user_name #the user
													pwd = pwd    #the password of the user
													dbname = dbname


													log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
													obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)

													sock_common = xmlrpclib.ServerProxy (log)
													try:
														raise # (Commented as Discussed with client for offline sync)
														uid = sock_common.login(dbname, username, pwd)
													except Exception as Err:
														#raise osv.except_osv(('Alert!'),('Connection to the Server Failed'))
														# offline_obj=self.pool.get('sale.offline.sync')
														# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
														conn_flag = True
														# if not offline_sync_sequence:
														# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'save_edit_record1','error_log':Err,})
														# else:
														# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
														# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
												sock = xmlrpclib.ServerProxy(obj)
												if  True:
													company_name = ''
													insert_crm_lead=''
													time_cur = time.strftime("%H:%M:%S")
													date = datetime.now().date()
													company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
													if company_id[0]:
														company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
													current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.name
													current_company=current_company.replace(' ','_')

													con_cat = company_name+'_'+current_company+'_Edit_Address_'+str(date)+'_'+str(time_cur)+'.sql'
													#filename = "/home/ubuntumaladtesting/sql_files/"+con_cat
													#d = os.path.dirname("/home/ubuntumaladtesting/sql_files/")
													filename = os.path.expanduser('~')+'/sql_files/'+con_cat
													directory_name = str(os.path.expanduser('~')+'/sql_files/')
													d = os.path.dirname(directory_name)
													if not os.path.exists(d):
														os.makedirs(d)
													d = os.path.dirname(directory_name)
													main_sql_str=''
													func_string ="\n\n CREATE OR REPLACE FUNCTION Edit_Address() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
													declare=" DECLARE \n \t"
													var1=""" company_ids INT;\n partner_main INT;\n city_srch_ids INT;\n state_srch_ids INT;\n district_srch_ids INT;\n tehsil_srch_ids INT;\n service_srch_ids INT;\n main_cust_line_id INT;\n	cust_read_data INT;\n  \n  BEGIN \n """
													endif="\n\n END IF; \n"
													ret="\n RETURN 1;\n"
													elsestr="\n ELSE \n"
													final="\nEND; \n $$;\n"
													fun_call="\n SELECT Edit_Address();\n"

													if branch_id:
															#main_sql_str += "\n company_ids=(SELECT id FROM res_company WHERE name ='%s' LIMIT 1);" %(str(branch_obj.browse(cr,uid,branch_id).name))

														#company_id_srch = [('name', '=',branch_obj.browse(cr,uid,branch_id).name)]
														#company_ids = sock.execute(dbname, uid, pwd, 'res.company', 'search', company_id_srch)

														#if company_ids:
															#main_sql_str +="\n IF company_ids IS NOT NULL THEN"
															main_sql_str += "\n partner_main=(SELECT id FROM res_partner WHERE ou_id ='%s' and branch_id=(SELECT id FROM res_company WHERE name ='%s' LIMIT 1) LIMIT 1);" %(str(res.partner_id.ou_id),str(branch_obj.browse(cr,uid,branch_id).name))
															#partner_srch = [('ou_id','=',res.partner_id.ou_id),('branch_id','=',company_ids[0])]

															#partner_main = sock.execute(dbname, uid, pwd, 'res.partner', 'search', partner_srch)
															service_srch_ids = []
															main_sql_str +="\n IF partner_main IS NOT NULL THEN"
															#if partner_main:
															if res.city_id:
																	# city_srch = [('name1', '=',res.city_id.name1)]
																	# city_srch_ids = sock.execute(dbname, uid, pwd, 'city.name', 'search', city_srch)

																	main_sql_str += "\n city_srch_ids=(SELECT id FROM city_name WHERE name1 ='%s' LIMIT 1);" %(str(res.city_id.name1))


															if res.state_id:
																	# state_srch = [('name', '=',res.state_id.name)]
																	# state_srch_ids = sock.execute(dbname, uid, pwd, 'state.name','search', state_srch)
																	main_sql_str += "\n state_srch_ids=(SELECT id FROM state_name WHERE name ='%s' LIMIT 1);" %(str(res.state_id.name))
															if res.district:
																	# district_srch = [('name', '=',res.district.name)]
																	# district_srch_ids = sock.execute(dbname, uid, pwd, 'district.name','search', district_srch)
																	main_sql_str += "\n district_srch_ids=(SELECT id FROM district_name WHERE name ='%s' LIMIT 1);" %(str(res.district.name))
															if res.tehsil:
																	# tehsil_srch = [('name', '=',res.tehsil.name)]
																	# tehsil_srch_ids = sock.execute(dbname, uid, pwd, 'tehsil.name','search', tehsil_srch)
																	main_sql_str += "\n tehsil_srch_ids=(SELECT id FROM tehsil_name WHERE name ='%s' LIMIT 1);" %(str(res.tehsil.name))
															if res.service_area:
																	# service_area_srch = [('name', '=',res.service_area.name)]
																	# service_srch_ids = sock.execute(dbname, uid, pwd, 'service.area','search', service_area_srch)
																	main_sql_str += "\n service_srch_ids=(SELECT id FROM service_area WHERE name ='%s' LIMIT 1);" %(str(res.service_area.name))
															if loc_id== '01':
																	main_sql_str += "\n update res_partner set title='%s',first_name='%s',email='%s',fax='%s',middle_name='%s',last_name='%s',designation='%s',location_name='%s',apartment='%s',building='%s',contact_name='%s',sub_area='%s',street='%s',city_id=city_srch_ids,district=district_srch_ids,tehsil=tehsil_srch_ids,state_id=state_srch_ids,zip='%s',landmark='%s',premise_type='%s' where id =partner_main;" %(str(res.title) if res.title else '',str(res.first_name) if res.first_name else '',str(res.email) if res.email else '',str(res.fax) if res.fax else '',str(res.middle_name) if res.middle_name else '' ,str(res.last_name) if res.last_name else '',str(res.designation) if res.designation else '',str(res.location_name) if res.location_name else '',str(res.apartment) if res.apartment else '',str(res.building) if res.building else '',str(total_name) if total_name else '',str(res.sub_area) if res.sub_area else '' ,str(res.street) if res.street else '',str(res.zip) if res.zip else '',str(res.landmark) if res.landmark else '',str(res.premise_type) if res.premise_type else '')
																	#sock.execute(dbname,uid,pwd,'res.partner','write',partner_main,{'title':res.title,'first_name':res.first_name,'email':res.email,'fax':res.fax,'middle_name':res.middle_name,'last_name':res.last_name,'designation':res.designation,'location_name':res.location_name,'apartment':res.apartment,'building':res.building,'contact_name':total_name,'sub_area':res.sub_area,'street':res.street,'city_id':city_srch_ids[0] if city_srch_ids else '','district':district_srch_ids[0] if district_srch_ids else '','tehsil':tehsil_srch_ids[0] if tehsil_srch_ids else '','state_id':state_srch_ids[0] if state_srch_ids else '','zip':res.zip,'landmark':res.landmark,'premise_type':res.premise_type})
																	#main_cust_line_srch = [('location_id','=',location_id),('partner_id','=',partner_main[0])]
																	#main_cust_line_id = sock.execute(dbname, uid, pwd, 'customer.line', 'search', main_cust_line_srch)
																	#main_sql_str += "\n main_cust_line_id=(select id from customer_line where location_id='%s' and partner_id=partner_main);" %(str(location_id))

															if res.cse and res.service_area:
																		#sock.execute(dbname, uid, pwd, 'customer.line', 'write', main_cust_line_id,{'service_area':service_srch_ids[0] if service_srch_ids else '','resource_assign':res.cse.concate_name})
																		#avi
																		main_sql_str += "\n update customer_line set service_area= service_srch_ids,resource_assign='%s' where location_id='%s' and partner_id=partner_main;" %(str(res.cse.concate_name),str(location_id))
															#phone_no_search = self.pool.get('phone.m2m').search(cr,uid,[('res_location_id','=',res.id)])
															#main_sql_str += "\n phone_no_search=(select id from phone_m2m where res_location_id='%s')"
															list_phone_val = []


															#if main_cust_line_id:
															# address_read_id = ['customer_address']
															#cust_read_data = sock.execute(dbname, uid, pwd, 'customer.line', 'read',main_cust_line_id,address_read_id)
															main_sql_str += "\n cust_read_data =(select customer_address from customer_line where  partner_id=(select id from res_partner WHERE ou_id ='%s' and branch_id=(SELECT id FROM res_company WHERE name ='%s' LIMIT 1) LIMIT 1) and location_id='%s');" %(str(res.partner_id.ou_id),str(branch_obj.browse(cr,uid,branch_id).name),str(location_id))

															#main_sql_str += "\n for data in (select customer_address from customer_line where id in ( main_cust_line_id )) \n LOOP \n"
															#for data in cust_read_data:
															#phone_srch = [('res_location_id','=',data['customer_address'][0])]
															#main_sql_str += "\n phone_srch_id =(select id from phone_m2m where res_location_id=(select id from customer_line where id in ( main_cust_line_id ))"
															#phone_srch_id = sock.execute(dbname,uid,pwd,'phone.m2m','search',phone_srch)
															#phone_srch_child = [('partner_id','=',partner_main[0])]

															#phone_srch_id_child = sock.execute(dbname,uid,pwd,'phone.number.child','search',phone_srch_child)
															#main_sql_str += "\n phone_srch_id_child=(select id from phone_number_child where partner_id=partner_main)"
															#total_num_list = phone_no_search[len(phone_srch_id):len(phone_no_search)]



															#srch_contact_id = sock.execute(dbname,uid,pwd,'phone.number','search',[('partner_id','=',partner_main[0])])
															# if not srch_contact_id:
															# 	mobile_create= sock.execute(dbname,uid,pwd,'phone.number','create',{'partner_id':partner_main[0]})
															#
															# 	srch_contact_id.append(mobile_create)

															#for phone_id in self.pool.get('phone.m2m').browse(cr,uid,total_num_list):
															#if True:
															if loc_id == '01':
																#phone_create_id = sock.execute(dbname,uid,pwd,'phone.number.child','create',{'number':phone_id.name,'contact_select':phone_id.type,'partner_id':partner_main[0],'contact_number':srch_contact_id[0] if srch_contact_id else ''})
																#sock.execute(dbname,uid,pwd,'res.partner','write',partner_main,{'phone_many2one':phone_create_id})
																#contact_branch = self.pool.get('phone.number').create(cr,uid,{'partner_id':partner_id})
																#child_branch_id =self.pool.get('phone.number.child').create(cr,uid,{'number':phone_id.name,'contact_select':phone_id.type,'partner_id':partner_id,'contact_number':contact_branch})
																#self.pool.get('res.partner').write(cr,uid,partner_id,{'phone_many2one':child_branch_id})
																cr.commit()
																#phone_create_id = sock.execute(dbname,uid,pwd,'phone.m2m','create',{'name':phone_id.name,'type':phone_id.type,'res_location_id':data['customer_address'][0]})
																#sock.execute(dbname,uid,pwd,'res.partner.address','write',data['customer_address'][0],{'phone_m2m_xx':phone_create_id})
																#sock.execute(dbname,uid,pwd,'customer.line','write',main_cust_line_id,{'phone_many2one':phone_create_id})
																#self.pool.get('customer.line').write(cr,uid,customer_line[0],{'phone_many2one':phone_id.id})
																cr.commit()
																#branch_child_srch_id = self.pool.get('phone.number.child').search(cr,uid,[('partner_id','=',partner_id)])
																#zip_id = zip(phone_srch_id,phone_no_search,phone_srch_id_child,branch_child_srch_id)
																#if zip_id:
																	# for iterate_phone in zip_id:
																	# 	phone_m2m_val =self.pool.get('phone.m2m').browse(cr,uid,iterate_phone[1])
																	#
																	# 	if loc_id == '01':
																	# 		#sock.execute(dbname,uid,pwd,'phone.number.child','write',iterate_phone[2],{'number':phone_m2m_val.name,'contact_select':phone_m2m_val.type,'partner_id':partner_main[0],'contact_number':srch_contact_id[0] if srch_contact_id else ''})
																	# 		self.pool.get('phone.number.child').write(cr,uid,iterate_phone[3],{'number':phone_m2m_val.name,'contact_select':phone_m2m_val.type,'partner_id':partner_id})
																	# 	#sock.execute(dbname,uid,pwd,'phone.m2m','write',iterate_phone[0],{'name':phone_m2m_val.name,'type':phone_m2m_val.type,'res_location_id':data['customer_address'][0]})
																	# 	cr.commit()
															main_sql_str += "\n update res_partner_address set title='%s',first_name='%s',middle_name='%s',last_name='%s',designation='%s',location_name='%s',apartment='%s',building='%s',sub_area='%s',street='%s',email='%s',fax='%s',city_id=city_srch_ids,district=district_srch_ids,tehsil=tehsil_srch_ids,state_id=state_srch_ids,zip='%s',landmark='%s',premise_type='%s' where id =cust_read_data;" %(str(res.title),str(res.first_name),str(res.middle_name),str(res.last_name),str(res.designation),str(res.location_name),str(res.apartment),str(res.building),str(res.sub_area),str(res.street),str(res.email),str(res.fax),str(res.zip),str(res.landmark),str(res.premise_type))
															#main_sql_str += "\n LOOP \n"
															with open (filename,'a') as f :
																f.write(func_string)
																f.write(declare)
																f.write(var1)
																f.write(main_sql_str)
																f.write(endif)
																f.write(ret)
																f.write(final)
																f.write(fun_call)
																f.close()

																			#sock.execute(dbname,uid,pwd,'res.partner.address','write',data['customer_address'][0],{'title':res.title,'first_name':res.first_name,'middle_name':res.middle_name,'last_name':res.last_name,'designation':res.designation,'location_name':res.location_name,'apartment':res.apartment,'building':res.building,'sub_area':res.sub_area,'street':res.street,'email':res.email,'fax':res.fax,'city_id':city_srch_ids[0] if city_srch_ids else '','district':district_srch_ids[0] if district_srch_ids else '','tehsil':tehsil_srch_ids[0] if tehsil_srch_ids else '','state_id':state_srch_ids[0] if state_srch_ids else '','zip':res.zip,'landmark':res.landmark,'premise_type':res.premise_type})


				                                if active_model=='res.partner.branch.new':
													self.pool.get('res.partner.branch.new').write(cr,uid,form_id,{'edit_location':''})
				                                if active_model=='ccc.branch.new':
													self.pool.get('ccc.branch.new').write(cr,uid,form_id,{'edit_location':''})
				                                if active_model=='res.partner':
													self.pool.get('res.partner').write(cr,uid,res.partner_id.id,{'edit_location':'','edit_location_existing':''})
				                                #cr.commit()
			#if partner_id and not form_id:
				#			self.lead_address_customer_line(cr,uid,partner_id,address,context=context)
			#self.pool.get('res.partner.address').write(cr,uid,ids,{'partner_id':res.partner_id.id})
			#self.pool.get('res.partner.new').write(cr,uid,form_id[0],{'edit_location':None})
			return {'view_mode' : 'tree,form','type': 'ir.actions.act_window_close',}


	def create_contract(self,cr,uid,ids,context=None):
		create_id = ''
		list_invoice_id = []
		values = ''
		cse = ''
		for temp in self.browse(cr,uid,ids):
			if temp.adhoc_invoice or temp.exempted:
				cr.execute(('select partner.id from res_partner partner,customer_line cc where partner.id = (select c.partner_id from customer_line c where c.customer_address=%(val)s) limit 1'),{'val':temp.id})
				for invoice in cr.fetchall():
					cr.execute(('select ic.id from invoice_adhoc_master ic where ic.partner_id=%(val)s'),{'val':invoice[0]})
					values = cr.fetchall()
					credit_period_val=0
					for res in self.pool.get('res.partner').browse(cr,uid,[invoice[0]]):
						for k in res.new_customer_location_service_line:
							cse = k.cse.id
							if k.cse.id == False:
								cse = temp.cse.id
								self.pool.get('customer.line').write(cr,uid,k.id,{'cse':cse})
							search_type = self.pool.get('premise.type.master').search(cr,uid,[('key','=',k.customer_address.premise_type)])
							if search_type:
								cust_type = self.pool.get('premise.type.master').browse(cr,uid,search_type)[0].select_type
								search_credit = self.pool.get('credit.period').search(cr,uid,[('name','=',cust_type)])
								credit_period_val = self.pool.get('credit.period').browse(cr,uid,search_credit)[0].credit_period
						create_id = self.pool.get('invoice.adhoc.master').create(cr,uid,
							{
								'cust_name':res.name,
								'status':'open',
								'service_classification':'exempted' if temp.exempted else '',
								'exempted':temp.exempted,
								'adhoc_invoice':True,
								'cse':cse,
								#'cse_new':cse,
								'partner_id':invoice[0],
								'gst_adhoc': True,
								'gst_invoice': True
							})
						self.pool.get('invoice.adhoc').create(cr,uid,
							{
								'invoice_adhoc_id':create_id,
								'invoice_adhoc_id_gst':create_id,
								'location_invoice':temp.id,
								'cse_invoice':cse
							})
				for invoice in values:
					if isinstance(invoice,(list,tuple)):
						for invoice_id in self.pool.get('invoice.adhoc.master').browse(cr,uid,[invoice[0]]):
							self.pool.get('payment.contract.history').create(cr,uid,{'history_adhoc_invoice_id':create_id,'invoice_number':invoice_id.invoice_number,'payment_status':invoice_id.status,'basic_amount':invoice_id.total_amount,'tax_amount':invoice_id.total_tax,'grand_total':invoice_id.grand_total_amount,'order_number':invoice_id.contract_no.contract_number})
							list_invoice_id.append(invoice_id.id)
					else:
						for invoice_id in self.pool.get('invoice.adhoc.master').browse(cr,uid,[invoice[0]]):
							self.pool.get('payment.contract.history').create(cr,uid,{'history_adhoc_invoice_id':create_id,'invoice_number':invoice_id.invoice_number,'payment_status':invoice_id.status,'basic_amount':invoice_id.total_amount,'tax_amount':invoice_id.total_tax,'grand_total':invoice_id.grand_total_amount,'order_number':invoice_id.contract_no.contract_number})
				history_id = self.pool.get('payment.contract.history').create(cr,uid,{'history_adhoc_invoice_id':create_id,'payment_status':'open'})
				for iter_values in list_invoice_id:
					self.pool.get('payment.contract.history').create(cr,uid,{'history_adhoc_invoice_id':iter_values,'payment_status':'open'})
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'gst_accounting', 'invoice_adhoc_id_gst_inherit')
		return{
				'type': 'ir.actions.act_window',
				'name':'Adhoc Invoice',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'invoice.adhoc.master',
				'res_id':create_id,
				 #'res_id':val,
				'view_id':form_view[1],
				'target':'current',
				'context': context,
			}

	def onchange_gst_type(self, cr, uid, ids, gst_type_customer, context=None):
	    if context is None: 
                context = {}
            value = {}
	    if gst_type_customer:
	        gst_type_customer = self.pool.get('gst.type.customer').browse(cr,uid,gst_type_customer).name
	    if gst_type_customer: 
	        if gst_type_customer == 'Unregistered':
	            value['gst_no'] = 'Unregistered'     
            return {'value': value}

res_partner_address()


class customer_line(osv.osv):
	_inherit = 'customer.line'

	_columns = {
		'gst_no':fields.char('GST No.',size=124),
		'special_status_check': fields.boolean('Special Status')
	}

	def onchange_special_status(self,cr,uid,ids,special_status,context=None):
		data = {}
		complaint_location_obj = self.pool.get('product.complaint.locations')
		if special_status != False:
			data.update(
				{
					'special_status_check': True
				})
		else:
			data.update(
				{
					'special_status_check': False
				})
		return {'value': data}

customer_line()

class res_company(osv.osv):
	_inherit = 'res.company'

	_columns = {
		'government_notification':fields.text('Government Notification',size=1000),
	}

res_company()


class res_partner(osv.osv):
	_inherit = 'res.partner'

	def write(self, cr, uid, ids,vals, context=None):
		res = super(res_partner, self).write(cr, uid, ids,vals, context=context)
		if isinstance(ids,(int,long)):
			ids = [ids]
		contract_obj = self.pool.get('sale.contract')
		contract_line_obj = self.pool.get('inspection.costing.line')
		if 'nature' in vals:
			contract_ids = contract_obj.search(cr,uid,[('partner_id','=',ids[0])])
			for contract_id in contract_ids:
				contract_data = contract_obj.browse(cr,uid,contract_id)
				if contract_data.gst_contract == True:
					contract_lines = contract_data.contract_line_id12
				else:
					contract_lines = contract_data.contract_line_id
				for contract_line in contract_lines:
					contract_line_obj.write(cr,uid,contract_line.id,{'nature':vals.get('nature')})
		return res

res_partner()
