from datetime import date,datetime, timedelta
from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
import calendar
import re
from base.res import res_company as COMPANY
from base.res import res_partner
import xmlrpclib
import os

class product_location_customer_search(osv.osv_memory):
    _inherit = 'product.location.customer.search' 
    def sync_product_location_customer_search(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            create_uid=write_uid=1
            partner_id=res.partner_id.name
            title=res.title 
            first_name=res.first_name
            middle_name=res.middle_name
            last_name=res.last_name
            designation=res.designation
            premise_type=res.premise_type
            location_name=res.location_name
            apartment=res.apartment
            building=res.building
            sub_area=res.sub_area
            street=res.street
            landmark= res.landmark
            zip=res.zip
            fax=res.fax
            email=res.email
            exempted=res.exempted
            adhoc_job=res.adhoc_job
            city_id=res.city_id.name1
            district = res.district.name
            tehsil = res.tehsil.name
            state_id=res.state_id.name
            certificate_no=res.certificate_no
            exem_attachment=res.exem_attachment
            exempted_classification=res.exempted_classification.name
            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    company_id=False
                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                
                    if context.has_key('phone_number'):
                        phone_number_name = context.get('phone_number')
                        phone_number_string = str(phone_number_name)

                    if context.has_key('customer_line_values'):
                        customer_line_values=context.get('customer_line_values')
                        if customer_line_values.has_key('branch'):
                            company_id=customer_line_values.get('branch')
                        if isinstance(company_id,list):
                            company_id_value = company_id[0]
                        elif isinstance(company_id,tuple):
                            company_id_value = company_id[0]
                        else:
                            company_id_value = company_id   
                    #company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id == False:
                        pass

                    elif company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id_value).name
            
                        con_cat = company_name+'_ProductLocationCustomerSearch_'+str(date)+'_'+str(time_cur)+'.sql'
                        filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                        directory_name = str(os.path.expanduser('~')+'/sql_files/')
                        d = os.path.dirname(directory_name)
                        if not os.path.exists(d):
                            os.makedirs(d)

                        premise_type_import=''
                        location_id=''
                        branch_name=False
                        partner_name=False
                        if context.has_key('customer_line_values'):
                            customer_line_values=context.get('customer_line_values')
                            if customer_line_values.has_key('location_id'):
                                location_id = customer_line_values.get('location_id')

                            if customer_line_values.has_key('premise_type_import'):
                                premise_type_import=customer_line_values.get('premise_type_import')

                            if customer_line_values.has_key('branch'):
                                branch=customer_line_values.get('branch')
                                branch_name=self.pool.get('res.company').browse(cr,uid,branch).name

                            # if customer_line_values.has_key('phone_many2one'):
                            #     phone_many2one=customer_line_values.get('phone_many2one')

                            #     phone_id=self.pool.get('phone.number.child').browse(cr,uid,phone_many2one)
                            #     print'\n\n\n     sjbdfkjsdb',context
                            #     print '\n\n\n ______________________________cccc',phone_id.number
                            #     jn
                            #     phone_number=phone_id.number

                            # if customer_line_values.has_key('customer_address'):
                            #     customer_address=customer_line_values.get('customer_address')
                            #     customer_address_name=self.pool.get('res.partner.address').browse(cr,uid,customer_address).name

                            if customer_line_values.has_key('partner_id'):
                                partner_id=customer_line_values.get('partner_id')    
                                partner_name= self.pool.get('res.partner').browse(cr,uid,partner_id).name
                        insert_main = "\n insert into res_partner_address(form_id,partner_id,exempted_classification,exem_attachment,certificate_no,state_id,tehsil,district,city_id,adhoc_job,exempted,email,fax,zip,landmark,street,sub_area,building,apartment,location_name,premise_type,designation,last_name,middle_name,first_name,title,create_date,write_date,create_uid,write_uid) values ('"+str(location_id)+"',(select * from get_many2oneid('res_partner where name = ''"+str(partner_id)+"'' ')),(select * from get_many2oneid('exempted_classification where name = ''"+str(exempted_classification)+"'' ')),'"+str(exem_attachment)+"','"+str(certificate_no)+"',(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(adhoc_job)+"','"+str(exempted)+"','"+str(email)+"','"+str(fax)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(last_name)+"','"+str(middle_name)+"','"+str(first_name)+"','"+str(title)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"
                        insert_main += "\n insert into customer_line(location_id,premise_type_import,branch,partner_id,state_id,tehsil,district,city_id,zip,landmark,street,sub_area,building,apartment,create_date,write_date,create_uid,write_uid) values ('"+str(location_id)+"','"+str(premise_type_import)+"',(select * from get_many2oneid('res_company where name = ''"+str(branch_name)+"'' ')),(select * from get_many2oneid('res_partner where name = ''"+str(partner_name)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"
                        insert_main +="\n update customer_line set customer_address=(select * from get_many2oneid('res_partner_address where form_id = ''"+str(location_id)+"'' ')) where location_id='"+str(location_id)+"';"

                        # insert_main += "\n insert into customer_line(state_id,tehsil,district,city_id,zip,landmark,street,sub_area,building,apartment,location_name,create_date,write_date,create_uid,write_uid) values ((select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                        # for notes in var.commentmment_line:        
                        #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                        # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                        # with open(filename,'a') as f:
                        #     f.write(insert_main)
                        #     f.close()


                    return True
product_location_customer_search()
class product_request(osv.osv):
    _inherit = 'product.request'
    def sync_cancel_product_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            state=res.state
            product_request_id=res.product_request_id
            cancellation_reason=res.cancellation_reason
            cancel_request=res.cancel_request
            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                

                    if context.has_key('branch'):
                        company_id = context.get('branch')
                        if isinstance(company_id,list):
                            company_id_value = company_id[0]
                        elif isinstance(company_id,tuple):
                            company_id_value = company_id[0]
                        else:
                            company_id_value = company_id

                    # company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id_value).name
            
                        con_cat = company_name+'_CancelProductRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)
                        
                    update="\n update product_request set write_date=(now() at time zone 'UTC'),write_uid=1,state='"+str(state)+"' where product_request_id='"+str(product_request_id)+"';"
                    # insert_main ="\n insert into product_request(product_request_id,active,state,confirm_check,hide_segment,hide_ref,hide_search,tehsil,district,ref_by,state_id,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,customer_type,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,customer_id,inquiry_type,request_date,call_type,name,first_name,last_name,city_id) values ('"+str(product_request_id)+"','"+str(active)+"','"+str(state)+"','"+str(confirm_check)+"','"+str(hide_segment)+"','"+str(hide_ref)+"','"+str(hide_search)+"',(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('customer_source where name = ''"+str(ref_by)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(customer_type)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(customer_id)+"','"+str(inquiry_type)+"','"+str(request_date)+"','"+str(call_type)+"','"+str(name)+"','"+str(first_name)+"','"+str(last_name)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')));"
               

                    # if res.customer_type=='new':
                    #     insert_main +="\n insert into res_partner(active,ou_id,name,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,first_name,last_name) values ('"+str(active)+"','"+str(customer_id)+"','"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(first_name)+"','"+str(last_name)+"');"
                    #     insert_main +="\n insert into res_partner_address(active,designation,state_id,district,tehsil,first_name,middle_name,last_name,state,city_id,name,create_date,write_date,create_uid,write_uid,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,fax,title) values ('"+str(active)+"','"+str(designation)+"',(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),'"+str(first_name)+"','"+str(middle_name)+"','"+str(last_name)+"','"+str(state)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(fax)+"','"+str(title)+"');"
                    # # insert_main +="\n insert into crm_lead(inquiry_type,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(inquiry_type)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    # for products in var.location_request_line:
                    #     insert_main += "\n insert into product_request_locations(create_date,write_date,create_uid,write_uid,product_generic_id,sku_name_id,company_id,remarks,quantity,branch_id,location_request_id,product_uom_id,address) values ((now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"',(select * from get_many2oneid('product_generic_name where name = ''"+str(products.product_generic_id.name)+"'' ')),(select * from get_many2oneid('product_product where name_template = ''"+str(products.sku_name_id.product_id.name)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(products.company_id.name)+"'' ')),'"+str(products.remarks)+"','"+str(products.quantity)+"',(select * from get_many2oneid('res_company where name = ''"+str(products.branch_id.name)+"'' ')),"+"(select * from get_many2oneid('product_request where product_request_id = ''"+str(var.product_request_id)+"'' ')),"+"(select * from get_many2oneid('product_uom where name = ''"+str(products.product_uom_id.name)+"'' ')),'"+str(products.address)+"' );"
                    # # for notes in var.commentmment_line:        
                    # #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(update)
                        f.close()


                    return True
    def sync_update_product_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            state=res.state
            product_request_id=res.product_request_id
            partner_id=res.name
            employee_id=res.employee_id.concate_name
            emp_code = res.employee_id.emp_code

            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                


                    if context.has_key('branch'):
                        company_id = context.get('branch')
                        if isinstance(company_id,list):
                            company_id_value = company_id[0]
                        elif isinstance(company_id,tuple):
                            company_id_value = company_id[0]
                        else:
                            company_id_value = company_id

                    # company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id_value).name
            
                        con_cat = company_name+'_UpdateProductRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)

                    name_split=employee_id.split()

                    update="\n update product_request set write_date=(now() at time zone 'UTC'),write_uid=1,state='"+str(state)+"' where product_request_id='"+str(product_request_id)+"';"
                    # update+="\n update res_partner set main_cse=(select * from get_many2oneid('hr_employee where emp_code = ''"+str(emp_code)+"'' ')),write_date=(now() at time zone 'UTC'),write_uid=1 where id=(select * from get_many2oneid('res_partner where name = ''"+str(partner_id)+"'' '));"

                    # insert_main ="\n insert into product_request(product_request_id,active,state,confirm_check,hide_segment,hide_ref,hide_search,tehsil,district,ref_by,state_id,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,customer_type,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,customer_id,inquiry_type,request_date,call_type,name,first_name,last_name,city_id) values ('"+str(product_request_id)+"','"+str(active)+"','"+str(state)+"','"+str(confirm_check)+"','"+str(hide_segment)+"','"+str(hide_ref)+"','"+str(hide_search)+"',(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('customer_source where name = ''"+str(ref_by)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(customer_type)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(customer_id)+"','"+str(inquiry_type)+"','"+str(request_date)+"','"+str(call_type)+"','"+str(name)+"','"+str(first_name)+"','"+str(last_name)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')));"
               

                    # if res.customer_type=='new':
                    #     insert_main +="\n insert into res_partner(active,ou_id,name,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,first_name,last_name) values ('"+str(active)+"','"+str(customer_id)+"','"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(first_name)+"','"+str(last_name)+"');"
                    #     insert_main +="\n insert into res_partner_address(active,designation,state_id,district,tehsil,first_name,middle_name,last_name,state,city_id,name,create_date,write_date,create_uid,write_uid,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,fax,title) values ('"+str(active)+"','"+str(designation)+"',(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),'"+str(first_name)+"','"+str(middle_name)+"','"+str(last_name)+"','"+str(state)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(fax)+"','"+str(title)+"');"
                    # # insert_main +="\n insert into crm_lead(inquiry_type,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(inquiry_type)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    # for products in var.location_request_line:
                    #     insert_main += "\n insert into product_request_locations(create_date,write_date,create_uid,write_uid,product_generic_id,sku_name_id,company_id,remarks,quantity,branch_id,location_request_id,product_uom_id,address) values ((now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"',(select * from get_many2oneid('product_generic_name where name = ''"+str(products.product_generic_id.name)+"'' ')),(select * from get_many2oneid('product_product where name_template = ''"+str(products.sku_name_id.product_id.name)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(products.company_id.name)+"'' ')),'"+str(products.remarks)+"','"+str(products.quantity)+"',(select * from get_many2oneid('res_company where name = ''"+str(products.branch_id.name)+"'' ')),"+"(select * from get_many2oneid('product_request where product_request_id = ''"+str(var.product_request_id)+"'' ')),"+"(select * from get_many2oneid('product_uom where name = ''"+str(products.product_uom_id.name)+"'' ')),'"+str(products.address)+"' );"
                    # # for notes in var.commentmment_line:        
                    # #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(update)
                        f.close()


                    return True

    def sync_product_request(self, cr, uid, ids, context=None):
        address = ''
        insert_main=''
        for res in self.browse(cr,uid,ids):
            request_date = False
            product_request_id = res.product_request_id
            request_type = res.request_type
            #request_id = res.request_id
            name = res.name
            first_name = res.first_name if res.first_name else ''
            last_name = res.last_name if res.last_name else ''
            city_id = res.city_id.name1
            tehsil_id = res.tehsil.name
            call_type = res.call_type if res.call_type else ''
            request_date=res.request_date if res.request_date else ''
            inquiry_type=res.inquiry_type if res.inquiry_type else ''
            customer_id=res.customer_id
            title=res.title if res.title else ''
            middle_name=res.middle_name if res.middle_name else ''
            fax=res.fax if res.fax else ''
            designation = res.designation if res.designation else ''
            premise_type = res.premise_type
            email = res.email if res.email else ''
            location_name = res.location_name if res.location_name else ''
            apartment = res.apartment if res.apartment else ''
            building = res.building if res.building else ''
            sub_area = res.sub_area if res.sub_area else ''
            customer_type=res.customer_type
            street = res.street if res.street else ''
            landmark = res.landmark if res.landmark else ''
            segment= res.segment
            zip = res.zip if res.zip else ''
            state=res.state
            created_by_global='Administrator'
            contact_name=first_name+' '+middle_name+' '+last_name
            create_uid=write_uid=1
            state_id=res.state_id.name
            ref_by=res.ref_by.name
            district=res.district.name
            tehsil=res.tehsil.name
            hide_search= True
            hide_ref= True
            hide_segment= True
            confirm_check=True
            active=True
            customer=True
            companyname_id=res.company_id.name
            crm_state='open'
            product_request_psd='product_request_psd'
            partner_id=res.name
            crm_inquiry_type='product'
            phone_many2one=res.phone_many2one.number
            phone_many2one_new=res.phone_many2one_new.number
            ref_text=res.ref_text
            created_by='Administrator'
            branch_id=res.branch_id.name
            phone_many2one=res.phone_many2one.number
            phone_many2one_type=res.phone_many2one.contact_select
            phone_many2one_new=res.phone_many2one_new.number
            ref_text=res.ref_text
            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('type','=','ccc')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                
                    if context.has_key('branch'):
                        company_id = context.get('branch')
                        if isinstance(company_id,list):
                            company_id_value = company_id[0]
                        elif isinstance(company_id,tuple):
                            company_id_value = company_id[0]
                        else:
                            company_id_value = company_id

                    # company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id_value).name
            
                        con_cat = company_name+'_ProductRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)

                    if customer_type=='new':
                        crm_quotation_type='lead'
                    else:
                        crm_quotation_type='customer'

                    partner_type = self.pool.get('res.partner').search(cr,uid,[('name','=',partner_id)])
                    customer_since  = self.pool.get('res.partner').browse(cr,uid,partner_type[0]).customer_since

                    if res.customer_type=='new':
                        phone_number_new_psd_obj = self.pool.get('phone.number.new.psd')
                        phone_many2one_new_value = var.phone_many2one_new.id
                        if phone_many2one_new_value==False:
                            phone_many2one_new_value=''
                        elif phone_many2one_new_value:      
                            browse_ids = phone_number_new_psd_obj.browse(cr,uid,phone_many2one_new_value).phone_product_request_id.id
                            search_ids = phone_number_new_psd_obj.search(cr,uid,[('phone_product_request_id','=',browse_ids)])
                            browse_all_phone_ids = phone_number_new_psd_obj.browse(cr,uid,search_ids)

                            if context.has_key('customer_line_values'):
                                customer_line_values=context.get('customer_line_values')
                                if customer_line_values.has_key('partner_id'):
                                    partner_id=customer_line_values.get('partner_id')    
                                    partner_name= self.pool.get('res.partner').browse(cr,uid,partner_id).name
                            for p in browse_all_phone_ids:
                                insert_main +="\n insert into phone_number_new_psd(phone_product_request_id,type,number,create_date,write_date,create_uid,write_uid) values ((select * from get_many2oneid('product_request where product_request_id = ''"+str(p.phone_product_request_id.product_request_id)+"'' ')),'"+str(p.type)+"','"+str(p.number)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"
                                insert_main +="\n insert into phone_number_child(partner_id,contact_select,number,create_date,write_date,create_uid,write_uid) values ((select * from get_many2oneid('res_partner where name = ''"+str(partner_name)+"'' ')),'"+str(p.type)+"','"+str(p.number)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                        # insert_main +="\n insert into phone_m2m(res_location_id,type,name,create_date,write_date,create_uid,write_uid) values ((select * from get_many2oneid('res_partner_address where apartment = ''"+str(apartment)+"'' and building=''"+str(building)+"'' and premise_type=''"+str(premise_type)+"''')),(select * from get_many2oneid('phone_number_child where contact_select = ''"+str(phone_many2one_type)+"'' ')),(select * from get_many2oneid('phone_number_child where number = ''"+str(phone_many2one)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"                      
                        insert_main +="\n insert into res_partner(contact_name,branch_id,phone_many2one,company_id,customer_since,city_id,state_id,district,tehsil,ref_by,customer,active,ou_id,name,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,first_name,last_name) values ('"+str(contact_name)+"',(select * from get_many2oneid('res_company where name = ''"+str(company_name)+"'' ')),(select * from get_many2oneid('phone_number_child where number = ''"+str(phone_many2one_new)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(companyname_id)+"'' ')),'"+str(customer_since)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('customer_source where name = ''"+str(ref_by)+"'' ')),'"+str(customer)+"','"+str(active)+"','"+str(customer_id)+"','"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(first_name)+"','"+str(last_name)+"');"

                        premise_type_import=''
                        location_id=''
                        branch_name=False
                        partner_name=False
                        if context.has_key('customer_line_values'):
                            customer_line_values=context.get('customer_line_values')
                            if customer_line_values.has_key('location_id'):
                                location_id = customer_line_values.get('location_id')
                            if customer_line_values.has_key('premise_type_import'):
                                premise_type_import=customer_line_values.get('premise_type_import')

                            if customer_line_values.has_key('branch'):
                                branch=customer_line_values.get('branch')
                                branch_name=self.pool.get('res.company').browse(cr,uid,branch).name

                            if customer_line_values.has_key('partner_id'):
                                partner_id=customer_line_values.get('partner_id')    
                                partner_name= self.pool.get('res.partner').browse(cr,uid,partner_id).name
                        insert_main +="\n insert into res_partner_address(partner_id,form_id,active,designation,state_id,district,tehsil,first_name,middle_name,last_name,state,city_id,name,create_date,write_date,create_uid,write_uid,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,fax,title) values ((select * from get_many2oneid('res_partner where name = ''"+str(partner_name)+"'' ')),'"+str(location_id)+"','"+str(active)+"','"+str(designation)+"',(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),'"+str(first_name)+"','"+str(middle_name)+"','"+str(last_name)+"','"+str(state)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(fax)+"','"+str(title)+"');"
                        insert_main +="\n insert into phone_m2m(res_location_id,type,name,create_date,write_date,create_uid,write_uid) values ((select * from get_many2oneid('res_partner_address where form_id = ''"+str(location_id)+"'' ')),(select * from get_many2oneid('phone_number_child where contact_select = ''"+str(phone_many2one_type)+"'' ')),(select * from get_many2oneid('phone_number_child where number = ''"+str(phone_many2one)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"
                        insert_main += "\n insert into customer_line(location_id,premise_type_import,branch,partner_id,state_id,tehsil,district,city_id,zip,landmark,street,sub_area,building,apartment,create_date,write_date,create_uid,write_uid) values ('"+str(location_id)+"','"+str(premise_type_import)+"',(select * from get_many2oneid('res_company where name = ''"+str(company_name)+"'' ')),(select * from get_many2oneid('res_partner where name = ''"+str(partner_name)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"
                        insert_main +="\n update customer_line set customer_address=(select * from get_many2oneid('res_partner_address where form_id = ''"+str(location_id)+"'' ')) where location_id='"+str(location_id)+"';"
                    insert_main +="\n insert into product_request(created_by,ref_text,phone_many2one_new,phone_many2one,company_id,product_request_id,active,state,confirm_check,hide_segment,hide_ref,hide_search,tehsil,district,ref_by,state_id,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,customer_type,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,customer_id,inquiry_type,request_date,call_type,name,first_name,last_name,city_id) values ((select * from get_many2oneid('res_users where name = ''"+str(created_by)+"'' ')),'"+str(ref_text)+"',(select * from get_many2oneid('phone_number_new_psd where number = ''"+str(phone_many2one_new)+"'' ')),(select * from get_many2oneid('phone_number_child where number = ''"+str(phone_many2one)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(companyname_id)+"'' ')),'"+str(product_request_id)+"','"+str(active)+"','"+str(state)+"','"+str(confirm_check)+"','"+str(hide_segment)+"','"+str(hide_ref)+"','"+str(hide_search)+"',(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('customer_source where name = ''"+str(ref_by)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(customer_type)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(customer_id)+"','"+str(inquiry_type)+"','"+str(request_date)+"','"+str(call_type)+"','"+str(name)+"','"+str(first_name)+"','"+str(last_name)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')));"
                    insert_main +="\n insert into crm_lead(quotation_type,inquiry_type,product_request_id,partner_id,type_request,inquiry_no,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(crm_quotation_type)+"','"+str(crm_inquiry_type)+"',(select * from get_many2oneid('product_request where product_request_id = ''"+str(product_request_id)+"'' ')),(select * from get_many2oneid('res_partner where name = ''"+str(partner_id)+"'' ')),'"+str(product_request_psd)+"','"+str(product_request_id)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(crm_state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    for products in var.location_request_line:
                        sku_value=products.product_name.id
                        if not sku_value:
                            sku_name=''
                        else:
                            sku_name=products.product_name.name
                        # insert_main += "\n insert into product_request_locations(create_date,write_date,create_uid,write_uid,product_name,sku_name_id,company_id,remarks,quantity,branch_id,location_request_id,product_uom_id,address) values ((now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"',(select * from get_many2oneid('product_product where name_template = ''"+str(products.product_generic_id.name)+"'' ')),(select * from get_many2oneid('product_product where name_template = ''"+str(sku_name)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(products.company_id.name)+"'' ')),'"+str(products.remarks if products.remarks else '')+"','"+str(products.quantity)+"',(select * from get_many2oneid('res_company where name = ''"+str(products.branch_id.name)+"'' ')),"+"(select * from get_many2oneid('product_request where product_request_id = ''"+str(var.product_request_id)+"'' ')),"+"(select * from get_many2oneid('product_uom where name = ''"+str(products.product_uom_id.name)+"'' ')),'"+str(products.address)+"' );"
                    # for notes in var.commentmment_line:        
                    #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks

#                     branch_id ---> id
# location_request_id ---> id
# product_uom_id ----> id
# company_id ---> id
# sku_name_id ---> id
# product_request_ref --> char
# address ---> char
# product_generic_id --> id
# quantity --> integer
# remarks --> char
                    with open(filename,'a') as f:
                        f.write(insert_main)
                        f.close()


                    return True

    #           sock = xmlrpclib.ServerProxy(obj)

    #           if res.partner_id:
    #               #partner = [('name', '=', res.partner_id.name)] 
    #               partner = [('ou_id', '=',res.partner_id.ou_id)]
    #               partner_ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search', partner)

    #               print "PPPPPPPPPPPPPPPPPPppp ",partner_ids

    #           if res.created_by:
    #               srch_created = [('name','=',res.created_by.name)]
    #               created_by_ids = sock.execute(dbname, uid, pwd, 'res.users', 'search', srch_created)

    #           if res.branch_id:
    #               branch_srch = [('name','=',res.branch_id.name)]
    #               branch_ids = sock.execute(dbname, uid, pwd, 'res.company', 'search', branch_srch)

    #           if res.company_id:
    #               company = [('name','=',res.company_id.name)]
    #               company_ids = sock.execute(dbname, uid, pwd, 'res.company', 'search', company)



    #           if res.request_date:
    #               newdate = res.request_date.rpartition('.')[0]

    #           #if res.customer_address:
    #           #   address = [('partner_id','=',partner_ids[0]),('apartment','=',res.customer_address.apartment),('premise_type','=',res.customer_address.premise_type),('building','=',res.customer_address.building)]
    #           #   address_ids = sock.execute(dbname, uid, pwd, 'res.partner.address', 'search', address)  

    #           if res.customer_address:
    #               srch = self.pool.get('customer.line').search(cr,uid,[('partner_id','=',res.partner_id.id)])
    #               for part in self.pool.get('customer.line').browse(cr,uid,srch):
    #                   if part.customer_address.id == res.customer_address.id:

    #                       address = [('location_id','=',part.location_id)]
    #                       address_ids = sock.execute(dbname, uid, pwd, 'customer.line', 'search', address)

    #                       fields = ['customer_address']
    #                       data = sock.execute(dbname, uid, pwd, 'customer.line', 'read', address_ids, fields)
                            
    #                       for ln in data:
    #                           print "LLLLLLLLLLLLLLLLl ",ln['customer_address'][0],res.partner_id.id
    #                           address = ln['customer_address'][0]

    #           phone_srch_id = []
    #           if res.contact_no and address:

    #               phone_srch = [('res_location_id','=',address),('name','=',res.contact_no.name)]

                
    #               phone_srch_id = sock.execute(dbname, uid, pwd, 'phone.m2m', 'search', phone_srch)


    #           info_req = {
    #               'partner_id':partner_ids[0] if partner_ids else False,
    #               'ou_id':res.cust_id_main if res.cust_id_main else '',
    #               'branch_id':branch_ids[0] if branch_ids else False,
    #               'request_date':newdate,
    #               'user_id':created_by_ids[0] if created_by_ids else False,
    #               'contact_name':res.contact_name,
    #               'request_desc':res.request_desc,
    #               'remark':res.remarks,
    #               'address_id':address if address else '',#res.customer_address.id,#address_ids[0] if address_ids else False,
    #               'state':'open',
    #               'origin':company_ids[0] if company_ids else False,
    #               'request_type':request_type,
    #               'name':res.partner_id.name,
    #               'request_id':request_id,
    #               'created_by_global':self.pool.get('res.users').browse(cr,uid,user).name,
    #               'contact_no':phone_srch_id[0] if phone_srch_id else '',
    #                  }
    #           print ":::::::::::::::::::::::::::::::::::::::::::::::: ",info_req
    #           info_req_id = sock.execute(dbname, uid, pwd, 'ccc.customer.request', 'create', info_req)
    #           print ":::::::::::::::::::::::::::::::::::::::::::::::: ",info_req_id,info_req


    #           lead_id = {'partner_id':partner_ids[0] if partner_ids else False,
    #                       'partner_name':res.partner_id.name,
    #                       'type_request':res.request_type,
    #                       'created_by_global':self.pool.get('res.users').browse(cr,uid,user).name,
    #                       'inspection_date':str(datetime.now()),
    #                       'inquiry_no':request_id,
    #                       'state':res.state,
    #                       'comment':res.remarks if res.remarks else '',}
    #           sock.execute(dbname, uid, pwd, 'crm.lead', 'create',lead_id)


    #           if res.comment_line:
    #               for line in res.comment_line:
    #                   notes = {
    #                       'request_id':info_req_id,
    #                       'user_id':line.user_id if line.user_id else '',
    #                       'comment_date':line.comment_date,
    #                       'comment':line.comment
    #                       }
    #                   notes_ids = sock.execute(dbname, uid, pwd, 'customer.request.comment.line', 'create', notes)

    #           update_id = sock.execute(dbname, uid, pwd, 'ccc.customer.request', 'write', info_req_id, {'request_id':res.request_id})

    # return True

    def sync_note_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            create_uid=write_uid=1
            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                

                    company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
            
                        con_cat = company_name+'_NoteRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)

                    for products in var.notes_line:
                        insert_main = "\n insert into product_request_notes_line(product_request_ref,state,comment_date,comment,create_date,write_date,create_uid,write_uid) values ('"+str(products.product_request_ref)+"','"+str(products.state)+"','"+str(products.comment_date)+"','"+str(products.comment)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"
                    # for notes in var.commentmment_line:        
                    #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(insert_main)
                        f.close()


                    return True
product_request()

class product_information_request(osv.osv):
    _inherit = 'product.information.request'

    def sync_cancel_information_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            state=res.state
            information_request_id=res.information_request_id
            cancellation_reason=res.cancellation_reason
            cancel_request=res.cancel_request
            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                
                    if context.has_key('branch'):
                        company_id = context.get('branch')
                        if isinstance(company_id,list):
                            company_id_value = company_id[0]
                        elif isinstance(company_id,tuple):
                            company_id_value = company_id[0]
                        else:
                            company_id_value = company_id

                    # company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id_value).name
            
                        con_cat = company_name+'_CancelInformationRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)
                        
                    update="\n update product_information_request set write_date=(now() at time zone 'UTC'),write_uid=1,state='"+str(state)+"' where information_request_id='"+str(information_request_id)+"';"
                    # insert_main ="\n insert into product_request(product_request_id,active,state,confirm_check,hide_segment,hide_ref,hide_search,tehsil,district,ref_by,state_id,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,customer_type,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,customer_id,inquiry_type,request_date,call_type,name,first_name,last_name,city_id) values ('"+str(product_request_id)+"','"+str(active)+"','"+str(state)+"','"+str(confirm_check)+"','"+str(hide_segment)+"','"+str(hide_ref)+"','"+str(hide_search)+"',(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('customer_source where name = ''"+str(ref_by)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(customer_type)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(customer_id)+"','"+str(inquiry_type)+"','"+str(request_date)+"','"+str(call_type)+"','"+str(name)+"','"+str(first_name)+"','"+str(last_name)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')));"
               

                    # if res.customer_type=='new':
                    #     insert_main +="\n insert into res_partner(active,ou_id,name,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,first_name,last_name) values ('"+str(active)+"','"+str(customer_id)+"','"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(first_name)+"','"+str(last_name)+"');"
                    #     insert_main +="\n insert into res_partner_address(active,designation,state_id,district,tehsil,first_name,middle_name,last_name,state,city_id,name,create_date,write_date,create_uid,write_uid,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,fax,title) values ('"+str(active)+"','"+str(designation)+"',(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),'"+str(first_name)+"','"+str(middle_name)+"','"+str(last_name)+"','"+str(state)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(fax)+"','"+str(title)+"');"
                    # # insert_main +="\n insert into crm_lead(inquiry_type,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(inquiry_type)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    # for products in var.location_request_line:
                    #     insert_main += "\n insert into product_request_locations(create_date,write_date,create_uid,write_uid,product_generic_id,sku_name_id,company_id,remarks,quantity,branch_id,location_request_id,product_uom_id,address) values ((now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"',(select * from get_many2oneid('product_generic_name where name = ''"+str(products.product_generic_id.name)+"'' ')),(select * from get_many2oneid('product_product where name_template = ''"+str(products.sku_name_id.product_id.name)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(products.company_id.name)+"'' ')),'"+str(products.remarks)+"','"+str(products.quantity)+"',(select * from get_many2oneid('res_company where name = ''"+str(products.branch_id.name)+"'' ')),"+"(select * from get_many2oneid('product_request where product_request_id = ''"+str(var.product_request_id)+"'' ')),"+"(select * from get_many2oneid('product_uom where name = ''"+str(products.product_uom_id.name)+"'' ')),'"+str(products.address)+"' );"
                    # # for notes in var.commentmment_line:        
                    # #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(update)
                        f.close()


                    return True
    def sync_update_information_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            state=res.state
            information_request_id=res.information_request_id
            partner_id=res.name
            employee_id=res.employee_id.concate_name
            emp_code = res.employee_id.emp_code

            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                

                    if context.has_key('branch'):
                        company_id = context.get('branch')
                        if isinstance(company_id,list):
                            company_id_value = company_id[0]
                        elif isinstance(company_id,tuple):
                            company_id_value = company_id[0]
                        else:
                            company_id_value = company_id

                    #company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id_value).name
            
                        con_cat = company_name+'_UpdateInformationRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)

                    name_split=employee_id.split()

                    update="\n update product_information_request set write_date=(now() at time zone 'UTC'),write_uid=1,state='"+str(state)+"' where information_request_id='"+str(information_request_id)+"';"
                    # update+="\n update res_partner set main_cse=(select * from get_many2oneid('hr_employee where emp_code = ''"+str(emp_code)+"'' ')),write_date=(now() at time zone 'UTC'),write_uid=1 where id=(select * from get_many2oneid('res_partner where name = ''"+str(partner_id)+"'' '));"

                    # insert_main ="\n insert into product_request(product_request_id,active,state,confirm_check,hide_segment,hide_ref,hide_search,tehsil,district,ref_by,state_id,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,customer_type,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,customer_id,inquiry_type,request_date,call_type,name,first_name,last_name,city_id) values ('"+str(product_request_id)+"','"+str(active)+"','"+str(state)+"','"+str(confirm_check)+"','"+str(hide_segment)+"','"+str(hide_ref)+"','"+str(hide_search)+"',(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('customer_source where name = ''"+str(ref_by)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(customer_type)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(customer_id)+"','"+str(inquiry_type)+"','"+str(request_date)+"','"+str(call_type)+"','"+str(name)+"','"+str(first_name)+"','"+str(last_name)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')));"
               

                    # if res.customer_type=='new':
                    #     insert_main +="\n insert into res_partner(active,ou_id,name,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,first_name,last_name) values ('"+str(active)+"','"+str(customer_id)+"','"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(first_name)+"','"+str(last_name)+"');"
                    #     insert_main +="\n insert into res_partner_address(active,designation,state_id,district,tehsil,first_name,middle_name,last_name,state,city_id,name,create_date,write_date,create_uid,write_uid,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,fax,title) values ('"+str(active)+"','"+str(designation)+"',(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),'"+str(first_name)+"','"+str(middle_name)+"','"+str(last_name)+"','"+str(state)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(fax)+"','"+str(title)+"');"
                    # # insert_main +="\n insert into crm_lead(inquiry_type,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(inquiry_type)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    # for products in var.location_request_line:
                    #     insert_main += "\n insert into product_request_locations(create_date,write_date,create_uid,write_uid,product_generic_id,sku_name_id,company_id,remarks,quantity,branch_id,location_request_id,product_uom_id,address) values ((now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"',(select * from get_many2oneid('product_generic_name where name = ''"+str(products.product_generic_id.name)+"'' ')),(select * from get_many2oneid('product_product where name_template = ''"+str(products.sku_name_id.product_id.name)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(products.company_id.name)+"'' ')),'"+str(products.remarks)+"','"+str(products.quantity)+"',(select * from get_many2oneid('res_company where name = ''"+str(products.branch_id.name)+"'' ')),"+"(select * from get_many2oneid('product_request where product_request_id = ''"+str(var.product_request_id)+"'' ')),"+"(select * from get_many2oneid('product_uom where name = ''"+str(products.product_uom_id.name)+"'' ')),'"+str(products.address)+"' );"
                    # # for notes in var.commentmment_line:        
                    # #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(update)
                        f.close()


                    return True


    def sync_information_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            call_type = res.call_type
            request_date=res.request_date
            customer_type= res.customer_type
            title=res.title
            name= res.name
            contact_name=res.contact_name
            customer_address=res.customer_address
            email = res.email
            fax= res.fax
            remarks=res.remarks
            create_uid=write_uid=1
            state=res.state
            active=True
            crm_state='open'
            product_request_psd='product_request_psd'
            partner_id=res.name
            crm_inquiry_type='product'
            created_by_global='Administrator'
            information_request_type_id=res.information_request_type_id.name
            request_date=res.request_date
            information_request_id=res.information_request_id
            branch_id=res.branch_id.name
            customer_id=res.customer_id
            phone_many2one=res.phone_many2one.number
            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                

                    company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
            
                        con_cat = company_name+'_InformationRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)

                    if customer_type=='new':
                        crm_quotation_type='lead'
                    else:
                        crm_quotation_type='customer'

                    insert_main ="\n insert into product_information_request(phone_many2one,customer_id,branch_id,information_request_type_id,created_by,information_request_id,active,state,create_date,write_date,create_uid,write_uid,remarks,fax,email,customer_address,contact_name,title,name,customer_type,request_date,call_type) values ((select * from get_many2oneid('phone_number_child where number = ''"+str(phone_many2one)+"'' ')),'"+str(customer_id)+"',(select * from get_many2oneid('res_company where name = ''"+str(branch_id)+"'' ')),(select * from get_many2oneid('information_request_types where name = ''"+str(information_request_type_id)+"'' ')),(select * from get_many2oneid('res_users where name = ''"+str(created_by_global)+"'' ')),'"+str(information_request_id)+"','"+str(active)+"','"+str(state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(remarks)+"','"+str(fax)+"','"+str(email)+"','"+str(customer_address)+"','"+str(contact_name)+"','"+str(title)+"','"+str(name)+"','"+str(customer_type)+"','"+str(request_date)+"','"+str(call_type)+"');"
                    insert_main +="\n insert into crm_lead(quotation_type,inquiry_type,information_request_id,partner_id,type_request,inquiry_no,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(crm_quotation_type)+"','"+str(crm_inquiry_type)+"',(select * from get_many2oneid('product_information_request where information_request_id = ''"+str(information_request_id)+"'' ')),(select * from get_many2oneid('res_partner where name = ''"+str(partner_id)+"'' ')),'"+str(product_request_psd)+"','"+str(information_request_id)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(crm_state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    # for products in var.location_request_line:
                        # insert_main += "\n insert into product_request_locations(branch_id,location_request_id,product_uom_id,address) values ((select * from get_many2oneid('res_company where name = ''"+str(products.branch_id.name)+"'' ')),"+"(select * from get_many2oneid('product_request where product_request_id = ''"+str(var.product_request_id)+"'' ')),"+"(select * from get_many2oneid('product_uom where name = ''"+str(products.product_uom_id.name)+"'' ')),'"+str(products.address)+"' );"
                    # for notes in var.commentmment_line:        
                    #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(insert_main)
                        f.close()


                    return True

product_information_request()

class product_complaint_request(osv.osv):
    _inherit='product.complaint.request'   

    def sync_cancel_complaint_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            state=res.state
            complaint_request_id=res.complaint_request_id
            cancellation_reason=res.cancellation_reason
            cancel_request=res.cancel_request
            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                
                    if context.has_key('branch'):
                        company_id = context.get('branch')
                        if isinstance(company_id,list):
                            company_id_value = company_id[0]
                        elif isinstance(company_id,tuple):
                            company_id_value = company_id[0]
                        else:
                            company_id_value = company_id

                    # company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id_value).name
            
                        con_cat = company_name+'_CancelComplaintRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)
                        
                    update="\n update product_complaint_request set write_date=(now() at time zone 'UTC'),write_uid=1,state='"+str(state)+"' where complaint_request_id='"+str(complaint_request_id)+"';"
                    # insert_main ="\n insert into product_request(product_request_id,active,state,confirm_check,hide_segment,hide_ref,hide_search,tehsil,district,ref_by,state_id,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,customer_type,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,customer_id,inquiry_type,request_date,call_type,name,first_name,last_name,city_id) values ('"+str(product_request_id)+"','"+str(active)+"','"+str(state)+"','"+str(confirm_check)+"','"+str(hide_segment)+"','"+str(hide_ref)+"','"+str(hide_search)+"',(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('customer_source where name = ''"+str(ref_by)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(customer_type)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(customer_id)+"','"+str(inquiry_type)+"','"+str(request_date)+"','"+str(call_type)+"','"+str(name)+"','"+str(first_name)+"','"+str(last_name)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')));"
               

                    # if res.customer_type=='new':
                    #     insert_main +="\n insert into res_partner(active,ou_id,name,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,first_name,last_name) values ('"+str(active)+"','"+str(customer_id)+"','"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(first_name)+"','"+str(last_name)+"');"
                    #     insert_main +="\n insert into res_partner_address(active,designation,state_id,district,tehsil,first_name,middle_name,last_name,state,city_id,name,create_date,write_date,create_uid,write_uid,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,fax,title) values ('"+str(active)+"','"+str(designation)+"',(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),'"+str(first_name)+"','"+str(middle_name)+"','"+str(last_name)+"','"+str(state)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(fax)+"','"+str(title)+"');"
                    # # insert_main +="\n insert into crm_lead(inquiry_type,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(inquiry_type)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    # for products in var.location_request_line:
                    #     insert_main += "\n insert into product_request_locations(create_date,write_date,create_uid,write_uid,product_generic_id,sku_name_id,company_id,remarks,quantity,branch_id,location_request_id,product_uom_id,address) values ((now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"',(select * from get_many2oneid('product_generic_name where name = ''"+str(products.product_generic_id.name)+"'' ')),(select * from get_many2oneid('product_product where name_template = ''"+str(products.sku_name_id.product_id.name)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(products.company_id.name)+"'' ')),'"+str(products.remarks)+"','"+str(products.quantity)+"',(select * from get_many2oneid('res_company where name = ''"+str(products.branch_id.name)+"'' ')),"+"(select * from get_many2oneid('product_request where product_request_id = ''"+str(var.product_request_id)+"'' ')),"+"(select * from get_many2oneid('product_uom where name = ''"+str(products.product_uom_id.name)+"'' ')),'"+str(products.address)+"' );"
                    # # for notes in var.commentmment_line:        
                    # #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(update)
                        f.close()


                    return True
    def sync_update_complaint_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            state=res.state
            complaint_request_id=res.complaint_request_id
            partner_id=res.customer
            employee_id=res.employee_id.concate_name
            emp_code = res.employee_id.emp_code

            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                

                    if context.has_key('branch'):
                        company_id = context.get('branch')
                        if isinstance(company_id,list):
                            company_id_value = company_id[0]
                        elif isinstance(company_id,tuple):
                            company_id_value = company_id[0]
                        else:
                            company_id_value = company_id

                    #company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id_value).name
            
                        con_cat = company_name+'_UpdateComplaintRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)

                    name_split=employee_id.split()

                    update="\n update product_complaint_request set write_date=(now() at time zone 'UTC'),write_uid=1,state='"+str(state)+"' where complaint_request_id='"+str(complaint_request_id)+"';"
                    # update+="\n update res_partner set main_cse=(select * from get_many2oneid('hr_employee where emp_code = ''"+str(emp_code)+"'' ')),write_date=(now() at time zone 'UTC'),write_uid=1 where id=(select * from get_many2oneid('res_partner where name = ''"+str(partner_id)+"'' '));"

                    # insert_main ="\n insert into product_request(product_request_id,active,state,confirm_check,hide_segment,hide_ref,hide_search,tehsil,district,ref_by,state_id,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,customer_type,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,customer_id,inquiry_type,request_date,call_type,name,first_name,last_name,city_id) values ('"+str(product_request_id)+"','"+str(active)+"','"+str(state)+"','"+str(confirm_check)+"','"+str(hide_segment)+"','"+str(hide_ref)+"','"+str(hide_search)+"',(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('customer_source where name = ''"+str(ref_by)+"'' ')),(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(customer_type)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(customer_id)+"','"+str(inquiry_type)+"','"+str(request_date)+"','"+str(call_type)+"','"+str(name)+"','"+str(first_name)+"','"+str(last_name)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')));"
               

                    # if res.customer_type=='new':
                    #     insert_main +="\n insert into res_partner(active,ou_id,name,create_date,write_date,create_uid,write_uid,segment,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,designation,fax,middle_name,title,first_name,last_name) values ('"+str(active)+"','"+str(customer_id)+"','"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(segment)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(designation)+"','"+str(fax)+"','"+str(middle_name)+"','"+str(title)+"','"+str(first_name)+"','"+str(last_name)+"');"
                    #     insert_main +="\n insert into res_partner_address(active,designation,state_id,district,tehsil,first_name,middle_name,last_name,state,city_id,name,create_date,write_date,create_uid,write_uid,zip,landmark,street,sub_area,building,apartment,location_name,email,premise_type,fax,title) values ('"+str(active)+"','"+str(designation)+"',(select * from get_many2oneid('state_name where name = ''"+str(state_id)+"'' ')),(select * from get_many2oneid('district_name where name = ''"+str(district)+"'' ')),(select * from get_many2oneid('tehsil_name where name = ''"+str(tehsil)+"'' ')),'"+str(first_name)+"','"+str(middle_name)+"','"+str(last_name)+"','"+str(state)+"',(select * from get_many2oneid('city_name where name1 = ''"+str(city_id)+"'' ')),'"+str(name)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(zip)+"','"+str(landmark)+"','"+str(street)+"','"+str(sub_area)+"','"+str(building)+"','"+str(apartment)+"','"+str(location_name)+"','"+str(email)+"','"+str(premise_type)+"','"+str(fax)+"','"+str(title)+"');"
                    # # insert_main +="\n insert into crm_lead(inquiry_type,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(inquiry_type)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    # for products in var.location_request_line:
                    #     insert_main += "\n insert into product_request_locations(create_date,write_date,create_uid,write_uid,product_generic_id,sku_name_id,company_id,remarks,quantity,branch_id,location_request_id,product_uom_id,address) values ((now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"',(select * from get_many2oneid('product_generic_name where name = ''"+str(products.product_generic_id.name)+"'' ')),(select * from get_many2oneid('product_product where name_template = ''"+str(products.sku_name_id.product_id.name)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(products.company_id.name)+"'' ')),'"+str(products.remarks)+"','"+str(products.quantity)+"',(select * from get_many2oneid('res_company where name = ''"+str(products.branch_id.name)+"'' ')),"+"(select * from get_many2oneid('product_request where product_request_id = ''"+str(var.product_request_id)+"'' ')),"+"(select * from get_many2oneid('product_uom where name = ''"+str(products.product_uom_id.name)+"'' ')),'"+str(products.address)+"' );"
                    # # for notes in var.commentmment_line:        
                    # #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(update)
                        f.close()


                    return True


    def sync_complaint_request(self, cr, uid, ids, context=None):
        address = ''
        for res in self.browse(cr,uid,ids):
            call_type = res.call_type
            requested_date=res.requested_date
            customer_type= res.customer_type
            customer=res.customer
            create_uid=write_uid=1
            state=res.state
            active=True
            crm_state='open'
            product_request_psd='product_request_psd'
            partner_id=res.customer
            crm_inquiry_type='product'
            created_by_global='Administrator'
            complaint_request_id=res.complaint_request_id
            request_date=res.requested_date
            customer_id=res.customer_id

            branch_ids=[]   
            branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
            for rec in self.pool.get('res.company').browse(cr,uid,branch_type):     
            
                vpn_ip_addr = rec.vpn_ip_address
                port = rec.port
                dbname = rec.dbname
                pwd = rec.pwd
                user_name = str(rec.user_name.login)
                user = uid
                username = user_name #the user
                pwd = pwd    #the password of the user
                dbname = dbname

                log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)                 
                obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
                            
                sock_common = xmlrpclib.ServerProxy (log)
                try:
                    raise # (Commented as Discussed with client for offline sync)
                    uid = sock_common.login(dbname, username, pwd)
                except Exception:

                    var = res
                    # request_id = var.request_id
                    location_id = ''
                    # srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',var.customer_address.id)])
                    # if srch:
                    #   location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id

                    company_name = ''

                    time_cur = time.strftime("%H:%M:%S")
                    date = datetime.now().date()
                

                    company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','branch_type')])
                    if company_id:
                        company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
            
                        con_cat = company_name+'_ComplaintRequest_'+str(date)+'_'+str(time_cur)+'.sql'
                    filename = os.path.expanduser('~')+'/sql_files/'+con_cat
                    directory_name = str(os.path.expanduser('~')+'/sql_files/')
                    d = os.path.dirname(directory_name)
                    if not os.path.exists(d):
                        os.makedirs(d)

                    if customer_type=='new':
                        crm_quotation_type='lead'
                    else:
                        crm_quotation_type='customer'


                    insert_main ="\n insert into product_complaint_request(created_by,customer_id,complaint_request_id,active,state,customer,create_date,write_date,create_uid,write_uid,customer_type,requested_date,call_type) values ((select * from get_many2oneid('res_users where name = ''"+str(created_by_global)+"'' ')),'"+str(customer_id)+"','"+str(complaint_request_id)+"','"+str(active)+"','"+str(state)+"','"+str(customer)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(customer_type)+"','"+str(requested_date)+"','"+str(call_type)+"');"
                    insert_main +="\n insert into crm_lead(quotation_type,inquiry_type,complaint_request_id,partner_id,type_request,inquiry_no,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(crm_quotation_type)+"','"+str(crm_inquiry_type)+"',(select * from get_many2oneid('product_complaint_request where complaint_request_id = ''"+str(complaint_request_id)+"'' ')),(select * from get_many2oneid('res_partner where name = ''"+str(partner_id)+"'' ')),'"+str(product_request_psd)+"','"+str(complaint_request_id)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(crm_state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    # insert_main +="\n insert into crm_lead(quotation_type,inquiry_type,product_request_id,partner_id,type_request,inquiry_no,inspection_date,created_by_global,state,create_date,write_date,create_uid,write_uid) values ('"+str(crm_quotation_type)+"','"+str(crm_inquiry_type)+"',(select * from get_many2oneid('product_request where product_request_id = ''"+str(product_request_id)+"'' ')),(select * from get_many2oneid('res_partner where name = ''"+str(partner_id)+"'' ')),'"+str(product_request_psd)+"','"+str(product_request_id)+"','"+str(request_date)+"','"+str(created_by_global)+"','"+str(crm_state)+"',(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"');"

                    for products in var.complaint_line_ids:
                        insert_main += "\n insert into product_complaint_request_line(complaint_id,product_id,pci_office,location_id,create_date,write_date,create_uid,write_uid,contact_person,phone_number,remark) values ((select * from get_many2oneid('product_complaint_request where complaint_request_id = ''"+str(complaint_request_id)+"'' ')),(select * from get_many2oneid('product_template_create where name = ''"+str(products.product_id.product_id.name)+"'' ')),(select * from get_many2oneid('res_company where name = ''"+str(products.pci_office.name)+"'' ')),(select * from get_many2oneid('product_complaint_locations where name = ''"+str(products.location_id.name)+"'' ')),(now() at time zone 'UTC'),(now() at time zone 'UTC'),'"+str(create_uid)+"','"+str(write_uid)+"','"+str(products.contact_person)+"','"+str(products.phone_number)+"','"+str(products.remark)+"');"
                    # for notes in var.commentmment_line:        
                    #       insert_main += "\n insert into customer_request_comment_line(request_id,user_id,comment,comment_date) values ((select * from get_many2oneid('ccc_customer_request where request_id ilike ''"+str(request_id)+"'' ')),'"+str(notes.user_id)+"','"+str(notes.comment)+"','"+str(notes.comment_date)+"' );"
                    # company_id,sku_name_id,product_request_ref,address,product_generic_id,quantity,remarks
                    with open(filename,'a') as f:
                        f.write(insert_main)
                        f.close()


                    return True
product_complaint_request()
