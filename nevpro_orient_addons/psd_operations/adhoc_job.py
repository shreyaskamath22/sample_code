#version 1.0.030 customer name size update
#version 1.0.041 Task Reated to IPM/CPM PMS service
from osv import osv, fields
from datetime import datetime
from osv import osv,fields
import time
import decimal_precision as dp
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math
import calendar
import datetime as dt
import xmlrpclib
from python_code.dateconversion import *
import python_code.dateconversion as py_date
import re
import time
import os
from openerpsync.sockconnect import connection as sockConnect

class adhoc_job(osv.osv):
	_inherit= "adhoc.job"

	def onchange_phone_no1(self,cr,uid,ids,cust_name):
		val = []
		phone_no=''
		if cust_name:
			cust_name1=cust_name
			cnt=0
			result=self.pool.get('res.partner').search(cr,uid,[('id','=',cust_name)])
			if result:
				for k in self.pool.get('res.partner').browse(cr,uid,result):
					phone_no=k.phone_many2one.number
					result1=self.pool.get('sale.contract').search(cr,uid,[('partner_id','=',cust_name1)])
					if result1:
						for i in self.pool.get('sale.contract').browse(cr,uid,result1):
							cnt=cnt+1
							
					return {'value':{'mobile_no':phone_no,'cnt':cnt}}
			else:
				return val


	# def onchange_details(self,cr,uid,ids,cust_name,location,adhoc_jobtype,cnt):
	# 	val = []
	# 	name_array = []
	# 	service_area1=service_new=phone_m2m_xx=''
	# 	if cnt==1:
	# 	    if adhoc_jobtype == 'with_contract':
	# 		if location and cust_name:
	# 			result1=self.pool.get('sale.contract').search(cr,uid,[('partner_id','=',cust_name)])
	# 			if result1 and adhoc_jobtype == 'with_contract':
	# 				mob_search = self.pool.get('res.partner.address').search(cr,uid,[('id','=',location)])
	# 				if mob_search:
	# 					for mobile in self.pool.get('res.partner.address').browse(cr,uid,mob_search):
	# 						phone_m2m_xx = mobile.phone_m2m_xx.name
						
	# 				for k in self.pool.get('sale.contract').browse(cr,uid,result1):
	# 					contract_start_date=k.contract_start_date
	# 					contract_end_date=k.contract_end_date
	# 					cse=k.cse.id
	# 					contract_no=k.id
	# 					contract_period=k.contract_period
	# 					sale_contract=k.id
	# 					for kk in k.contract_line_id:
	# 							no_of_service = kk.no_of_services
	# 							no_of_inspection= kk.no_of_inspections
	# 							pms1=kk.pms.id
	# 							service_area1=kk.service_area.id
	# 							if kk.location_name:
	# 								name_array.append(kk.location_name)
	# 							if kk.apartment:
	# 								name_array.append(kk.apartment)
	# 							if kk.building:
	# 								name_array.append(kk.building)
	# 							if kk.sub_area:
	# 								name_array.append(kk.sub_area)
	# 							if kk.street:
	# 								name_array.append(kk.street)
	# 							if kk.landmark:
	# 								name_array.append(kk.landmark)
	# 							if kk.city_id :
	# 								city = kk.city_id.name1
	# 								name_array.append(city)
	# 							if kk.tehsil:
	# 								teh=kk.tehsil.name
	# 								name_array.append(teh)
	# 							if kk.district:
	# 								distr=kk.district.name
	# 								name_array.append(distr)
	# 							if kk.state_id :
	# 								state =kk.state_id.name
	# 								name_array.append(state)
	# 							if kk.zip:
	# 								name_array.append(kk.zip)
	# 							address = ''
	# 							if name_array != []:
	# 								for val in name_array:
	# 									var = val
	# 									if address == '':
	# 										address = var
	# 									else:
	# 										address=address +','+var
	# 							return {'value':{'contract_no':contract_no,'contract_strtdt':contract_start_date,'contract_enddt'
	# 							:contract_end_date,'Contract_Period':contract_period,'cse':cse,
	# 							'contact_location':address,'sale_contract':int(sale_contract),'no_of_services':no_of_service,'no_of_inspection':no_of_inspection,'mobile_no':phone_m2m_xx,}}
			
	# 		else:
	# 			return val
	# 	else:
	# 		if location and cust_name:
	# 			result1=self.pool.get('sale.contract').search(cr,uid,[('partner_id','=',cust_name)])
	# 			if result1 and adhoc_jobtype == 'with_contract':
	# 				for i in self.pool.get('sale.contract').browse(cr,uid,result1):
	# 					onchange=i.cust_name
	# 					return {'value':{'cust_name_invisible1':str(onchange)}}
	# 		else:
	# 			return val

	# 	if adhoc_jobtype == 'without_contract':
	# 		#cr.execute('''delete from ops_product_temp''')
	# 		#cr.execute('''delete from service_area_temp''')
	# 		service_area1=service_new=''
	# 		if location and cust_name:
	# 			result11=self.pool.get('ccc.branch.new').search(cr,uid,[('partner_id','=',cust_name)])
	# 			if result11 and adhoc_jobtype == 'without_contract':
	# 				address_search = self.pool.get('res.partner.address').search(cr,uid,[('id','=',location)])
	# 				if address_search:
	# 					for add in self.pool.get('res.partner.address').browse(cr,uid,address_search):
	# 								phone_m2m_xx = add.phone_m2m_xx.name
	# 								service_area=add.service_area.id
	# 								cse = add.cse.id
	# 								if add.location_name:
	# 										name_array.append(add.location_name)
	# 								if add.apartment:
	# 										name_array.append(add.apartment)
	# 								if add.building:
	# 										name_array.append(add.building)
	# 								if add.sub_area:
	# 										name_array.append(add.sub_area)
	# 								if add.street:
	# 										name_array.append(add.street)
	# 								if add.landmark:
	# 										name_array.append(add.landmark)
	# 								if add.city_id :
	# 										city = add.city_id.name1
	# 										name_array.append(city)
	# 								if add.tehsil:
	# 										teh=add.tehsil.name
	# 										name_array.append(teh)
	# 								if add.district:
	# 									#if kk.district == add.district:
	# 										distr=add.district.name
	# 										name_array.append(distr)
	# 								if add.state_id :
	# 										state =add.state_id.name
	# 										name_array.append(state)
	# 								if add.zip:
	# 									#if kk.zip == add.zip:
	# 										name_array.append(add.zip)
	# 								address8 = ''
	# 								if name_array != []:
	# 									for val in name_array:
	# 										var = val
	# 										if address8 == '':
	# 											address8 = var
	# 										else:
	# 											address8=address8 +','+var
	# 					'''for k in self.pool.get('ccc.branch.new').browse(cr,uid,result11):
	# 						for k1 in k.new_customer_location:
								
	# 								service_area=k1.service_area.id
	# 								assign_resource=k1.assign_resource.id
	# 								search_val1 = self.pool.get('service.area.temp').search(cr,uid,[('name','=',k1.service_area.name)])
	# 								if not search_val1:
	# 									self.pool.get('service.area.temp').create(cr,uid,{'name':k1.service_area.name})
	# 								search = self.pool.get('service.area.temp').search(cr,uid,[('id','>',0)])
	# 								for i1 in self.pool.get('service.area.temp').browse(cr,uid,search):
	# 										service_new = i1.id'''
					
	# 				return {'value':{'cse':cse,'contact_location':address8,'service_area':service_area,'mobile_no':phone_m2m_xx,}}#'service_area':service_area,


	# def onchange_details1(self,cr,uid,ids,cust_name,location,adhoc_jobtype,cnt):
	# 	val = []
	# 	name_array = []
	# 	service_area1=service_new=phone_m2m_xx=''
	# 	if cnt==1:
	# 	    if adhoc_jobtype == 'with_contract':
	# 		if location and cust_name:
	# 			result1=self.pool.get('sale.contract').search(cr,uid,[('partner_id','=',cust_name)])
	# 			if result1 and adhoc_jobtype == 'with_contract':
	# 				mob_search = self.pool.get('res.partner.address').search(cr,uid,[('id','=',location)])
	# 				if mob_search:
	# 					for mobile in self.pool.get('res.partner.address').browse(cr,uid,mob_search):
	# 						phone_m2m_xx = mobile.phone_m2m_xx.name
						
	# 				for k in self.pool.get('sale.contract').browse(cr,uid,result1):
	# 					contract_start_date=k.contract_start_date
	# 					contract_end_date=k.contract_end_date
	# 					cse=k.cse.id
	# 					contract_no=k.id
	# 					contract_period=k.contract_period
	# 					sale_contract=k.id
	# 					for kk in k.contract_line_id:
	# 							no_of_service = kk.no_of_services
	# 							no_of_inspection= kk.no_of_inspections
	# 							pms1=kk.pms.id
	# 							service_area1=kk.service_area.id
	# 							if kk.location_name:
	# 								name_array.append(kk.location_name)
	# 							if kk.apartment:
	# 								name_array.append(kk.apartment)
	# 							if kk.building:
	# 								name_array.append(kk.building)
	# 							if kk.sub_area:
	# 								name_array.append(kk.sub_area)
	# 							if kk.street:
	# 								name_array.append(kk.street)
	# 							if kk.landmark:
	# 								name_array.append(kk.landmark)
	# 							if kk.city_id :
	# 								city = kk.city_id.name1
	# 								name_array.append(city)
	# 							if kk.tehsil:
	# 								teh=kk.tehsil.name
	# 								name_array.append(teh)
	# 							if kk.district:
	# 								distr=kk.district.name
	# 								name_array.append(distr)
	# 							if kk.state_id :
	# 								state =kk.state_id.name
	# 								name_array.append(state)
	# 							if kk.zip:
	# 								name_array.append(kk.zip)
	# 							address = ''
	# 							if name_array != []:
	# 								for val in name_array:
	# 									var = val
	# 									if address == '':
	# 										address = var
	# 									else:
	# 										address=address +','+var
								
	# 							return {'value':{'contract_no':contract_no,'contract_strtdt':contract_start_date,'contract_enddt'
	# 							:contract_end_date,'Contract_Period':contract_period,'cse':cse,
	# 							'contact_location':address,'sale_contract':int(sale_contract),'no_of_services':no_of_service,'no_of_inspection':no_of_inspection,'mobile_no':phone_m2m_xx,}}
			
	# 		else:
	# 			return val
	# 	else:
	# 		if location and cust_name:
	# 			result1=self.pool.get('sale.contract').search(cr,uid,[('partner_id','=',cust_name)])
	# 			if result1 and adhoc_jobtype == 'with_contract':
	# 				for i in self.pool.get('sale.contract').browse(cr,uid,result1):
	# 					onchange=i.cust_name
	# 					return {'value':{'cust_name_invisible1':str(onchange)}}
	# 		else:
	# 			return val

	# 	if adhoc_jobtype == 'without_contract':
	# 		#cr.execute('''delete from ops_product_temp''')
	# 		#cr.execute('''delete from service_area_temp''')
	# 		service_area1=service_new=''
	# 		if location and cust_name:
	# 			result11=self.pool.get('ccc.branch.new').search(cr,uid,[('partner_id','=',cust_name)])
	# 			if result11 and adhoc_jobtype == 'without_contract':
	# 				address_search = self.pool.get('res.partner.address').search(cr,uid,[('id','=',location)])
	# 				if address_search:
	# 					for add in self.pool.get('res.partner.address').browse(cr,uid,address_search):
	# 								phone_m2m_xx = add.phone_m2m_xx.name
	# 								service_area=add.service_area.id
	# 								cse = add.cse.id
	# 								if add.location_name:
	# 										name_array.append(add.location_name)
	# 								if add.apartment:
	# 										name_array.append(add.apartment)
	# 								if add.building:
	# 										name_array.append(add.building)
	# 								if add.sub_area:
	# 										name_array.append(add.sub_area)
	# 								if add.street:
	# 										name_array.append(add.street)
	# 								if add.landmark:
	# 										name_array.append(add.landmark)
	# 								if add.city_id :
	# 										city = add.city_id.name1
	# 										name_array.append(city)
	# 								if add.tehsil:
	# 										teh=add.tehsil.name
	# 										name_array.append(teh)
	# 								if add.district:
	# 									#if kk.district == add.district:
	# 										distr=add.district.name
	# 										name_array.append(distr)
	# 								if add.state_id :
	# 										state =add.state_id.name
	# 										name_array.append(state)
	# 								if add.zip:
	# 									#if kk.zip == add.zip:
	# 										name_array.append(add.zip)
	# 								address8 = ''
	# 								if name_array != []:
	# 									for val in name_array:
	# 										var = val
	# 										if address8 == '':
	# 											address8 = var
	# 										else:
	# 											address8=address8 +','+var
	# 					'''for k in self.pool.get('ccc.branch.new').browse(cr,uid,result11):
	# 						for k1 in k.new_customer_location:
								
	# 								service_area=k1.service_area.id
	# 								assign_resource=k1.assign_resource.id
	# 								search_val1 = self.pool.get('service.area.temp').search(cr,uid,[('name','=',k1.service_area.name)])
	# 								if not search_val1:
	# 									self.pool.get('service.area.temp').create(cr,uid,{'name':k1.service_area.name})
	# 								search = self.pool.get('service.area.temp').search(cr,uid,[('id','>',0)])
	# 								for i1 in self.pool.get('service.area.temp').browse(cr,uid,search):
	# 										service_new = i1.id'''
					
	# 				return {'value':{'cse':cse,'contact_location':address8,'service_area':service_area,'mobile_no':phone_m2m_xx,}}#'service_area':service_area,

	def onchange_service_order_no(self,cr,uid,ids,service_order_no):
		val={}
		name_array = []
		so_obj = self.pool.get('amc.sale.order').browse(cr,uid,service_order_no)
		kk = self.pool.get('res.partner.address').browse(cr,uid,so_obj.billing_address.id)
		if kk.location_name:
			name_array.append(str(kk.location_name))
		if kk.apartment:
			name_array.append(str(kk.apartment))
		if kk.building:
			name_array.append(str(kk.building))
		if kk.sub_area:
			name_array.append(str(kk.sub_area))
		if kk.street:
			name_array.append(str(kk.street))
		if kk.landmark:
			name_array.append(str(kk.landmark))
		if kk.city_id :
			city = kk.city_id.name1
			name_array.append(str(city))
		if kk.tehsil:
			teh=kk.tehsil.name
			name_array.append(str(teh))
		if kk.district:
			distr=kk.district.name
			name_array.append(str(distr))
		if kk.state_id :
			state =kk.state_id.name
			name_array.append(str(state))
		if kk.zip:
			name_array.append(str(kk.zip))
		address = ''
		if name_array != []:
			for val in name_array:
				var = val
				if address == '':
					address = var
				else:
					address += ',' + var
		address_string = address
		val = { 'contact_location': address_string or '',
				'Contract_Period':str(so_obj.no_of_months) or None,
				'cse':so_obj.pse.id or None,
				'contract_strtdt':so_obj.order_period_from or False,
				'contract_enddt':so_obj.order_period_to or False,
			}
		return {'value':val}

	def psd_save(self, cr, uid, ids, context=None):
		address =''
		name_array = []
		name_array1 = []
		cust_id=''
		pms=''
		location1=''
		sale_contract_id=''
		adhoc_record={}
		current_date = datetime.now().date()
		for res1 in self.browse(cr,uid,ids):
			contract_end_date=res1.contract_enddt
			expired_contract_no=res1.expired_contr_no.id
			adhoc_job_type1=res1.adhoc_jobtype		
			customer_name=res1.cust_name.id
			new_job_id=res1.job_id.scheduled_job_id
			cust_id=res1.cust_name.ou_id
 
			#search_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('contract_end_date','=',contract_end_date),('name_contact','=',customer_name),('state','=','unscheduled'),('scheduled_job_id','=',new_job_id)])
			search_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('name_contact','=',customer_name),('state','=','unscheduled'),('scheduled_job_id','=',new_job_id)])
			print 'lllll',search_id,'oooooo'
			
			if search_id and adhoc_job_type1 == 'without_contract':
				for job_adj in self.pool.get('res.scheduledjobs').browse(cr,uid,search_id):
					self.pool.get('res.scheduledjobs').write(cr, uid, search_id,{'state':'adjusted'},context={'default_search_record':True}) 
			
			for res in self.browse(cr,uid,ids):
				# if not res.pms:
				# 	raise osv.except_osv(('Alert!'),('Please select PMS'))
				if res.adhoc_jobtype=='without_contract':	
					search_standard_job = self.pool.get('adhoc.job').search(cr,uid,[('adhoc_jobtype','=','without_contract'),('cust_name','=',res.cust_name.id),('job_category','=','adhoc_standard'),('location','=',res.location.id),('pms','=',res.pms.id)])
					if search_standard_job == []:
						if (res.job_category == 'adhoc_complaint') or  (res.job_category == 'adhoc_inspection'):
							raise osv.except_osv(('Alert!'),(res.job_category+' cannot be created before creating Adhoc Standard Job for '+res.pms.name+' PMS'))
				if res.location.location_name:
					name_array.append(res.location.location_name)
					name_array1.append(res.location.location_name)
				if res.location.apartment:
					name_array.append(res.location.apartment)
					name_array1.append(res.location.apartment)
				if res.location.building:
					name_array.append(res.location.building)
					name_array1.append(res.location.building)
				if res.location.sub_area:
					name_array.append(res.location.sub_area)
					name_array1.append(res.location.sub_area)
				if res.location.street:
					name_array.append(res.location.street)
					name_array1.append(res.location.street)
				if res.location.landmark:
					name_array.append(res.location.landmark)
					name_array1.append(res.location.landmark)
				if res.location.city_id :
					city = res.location.city_id.name1
					name_array.append(city)
				if res.location.tehsil:
					teh=res.location.tehsil.name
					name_array.append(teh)
					name_array1.append(teh)
				if res.location.district:
					distr=res.location.district.name
					name_array.append(distr)
					name_array1.append(distr)
				if res.location.state_id :
					state =res.location.state_id.name
					name_array.append(state)
				if res.location.zip:
					name_array.append(res.location.zip)
					name_array1.append(res.location.zip)
				address = ''
				if name_array != []:
					for val in name_array:
						var = val
						if address == '':
							address = var
						else:
							address=address +','+var

				address1 = ''
				for val1 in name_array1:
					var1 = val1
					if address1 == '':
						address1 = var1
					else:
						address1=address1 +','+var1
				location1=address
				location2=address1
				Flaggg1 = False
				if res.contract_strtdt and res.contract_enddt:
					if res.contract_strtdt==res.contract_enddt:
						Flaggg1 = True
				
				adhoc_search1 = self.pool.get('res.scheduledjobs').search(cr,uid,[('name_contact','=',res.cust_name.id),('location_id','=',location1),('job_category','in',('adhoc_standard','adhoc_inspection','adhoc_complaint','adhoc_complementary')),('pms','=',res.pms.name)])
				is_ipm=res.is_pim
				useservice_completeslip=res.useservice_completeslip

				seq_id = self.pool.get('ir.sequence').get(cr, uid,'operation.job.id')
				ou_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
				today_date = datetime.now().date()
				year = today_date.year
				year1=today_date.strftime('%y')
				company_name11 = ''
				company_id11 = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
				if company_id11:
					company_name11 = self.pool.get('res.company').browse(cr,uid,company_id11[0]).id

				company_id=self._get_company(cr,uid,context=None)

				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					job_code=comp_id.adhoc_id
				month=today_date.strftime('%m')
				if int(month)>3:
					year2=int(year1)+1
				else :
					year2=int(year1)
				cr.execute("select id,year from ir_sequence where code='operation.job.id'")
				year_db=cr.fetchone()
				if int(year_db[1])!=year2 :
					#cr.execute("select id from ir_sequence where code='operation.job.id'")
					cr.execute("ALTER SEQUENCE ir_sequence_%s RESTART WITH 2" %(str(year_db[0])))
					cr.execute("update ir_sequence set year='"+str(year2)+"' where code='operation.job.id'")
					seq_id='000001'

				job_id =str(ou_id)+job_code+str(year2)+str(seq_id)
				pms1 = [pms.pms.id for pms in self.browse(cr,uid,[res.id])]	
				self.pool.get('adhoc.job').write(cr, uid, res.id,{'adhoc_jobid':job_id})
				sale_contract_id=res.sale_contract.id
				cust_name1=res.cust_name.id
				contract_no1=res.contract_no.contract_number
				pms_search=res.pms.id
				cnt=0
				search_record1=self.pool.get('res.scheduledjobs').search(cr,uid,[('name_contact','=',cust_name1),('job_id','=',contract_no1),('pms_search','=',pms_search)])
				print 'aaaaaaaa',search_record1,'bbbbbb',adhoc_search1,'uuuuu'
				#print error
				if search_record1:
					for i in self.pool.get('res.scheduledjobs').browse(cr,uid,search_record1):
						cnt=cnt+1
				cnt1=cnt+1
				#avi
				if res.adhoc_jobtype=='without_contract':
					c=res.expired_contr_no.contract_number
					cntr_strt=res1.expired_contr_no.contract_start_date
					cntr_end=res1.expired_contr_no.contract_end_date
					#t1=time.strptime(cntr_strt, "%Y-%m-%d")
					#t2=time.strptime(cntr_end, "%Y-%m-%d")
					t1= datetime.fromtimestamp(time.mktime(time.strptime(cntr_strt, "%Y-%m-%d"))) if cntr_strt else ''
					t2= datetime.fromtimestamp(time.mktime(time.strptime(cntr_end, "%Y-%m-%d"))) if cntr_end else ''
					contr_period=relativedelta(t2, t1).months if t1 and t2 else ''
					
				else:
					c=res.contract_no.contract_number
					cntr_strt=res.contract_strtdt
					cntr_end=res.contract_enddt
					contr_period=res.Contract_Period
				print 'rrrrrrrrrrrr',contr_period,'rrrrrrrrr'
				new_job_data = {
										'name_contact':res.cust_name.id if res.cust_name else False,
										'name':res.cust_name.name if res.cust_name.name else '',
										'company_id': self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
										'contact_name':res.cust_name.contact_name if res.cust_name.contact_name else '',
										#'no_of_services':1 if res.job_category=='adhoc_standard' mbelse 0,
										#'no_of_inspection':1 if res.job_category=='adhoc_inspection' else 0,
										'job_type':'service',
										'location_id':address if address else '',
										'pms':res.pms.name_template if res.pms.name_template else '',
										'job_category':res.job_category if res.job_category else '',
										'job':res.job_category if res.job_category else '',
										'req_date_time':str(res.req_tentdt) if res.req_tentdt else False,
										'scheduled_job_id':job_id if job_id else '',
										'is_ipm':True if is_ipm == True else False,
										#'service_area':res.service_area.name if res.service_area.name else '',
										#'contract_start_date':res.contract_strtdt if res.contract_strtdt else False,'contract_end_date':res.contract_enddt if res.contract_enddt else False,
										'contract_start_date':cntr_strt if cntr_strt else False,'contract_end_date':cntr_end if cntr_end else False,
										'cse_new':res.cse.id if res.cse else False,
										'pse':res.cse.id or False,
										#'job_id':res.adhoc_jobid or False,
										#'contract_period':res.Contract_Period if res.Contract_Period else '',
										'contract_period':contr_period if contr_period else '',
										'phone1':res.mobile_no if res.mobile_no else '',
										#'job_id':res.contract_no.contract_number if res.contract_no.contract_number else '',
										#'job_id':c if c else '',
										'sale_contract':sale_contract_id if sale_contract_id else False,
										'state':'complaint' if res.job_category=='adhoc_complaint' else 'unscheduled',
										'adhoc_job_type':res.adhoc_jobtype if res.adhoc_jobtype else '',
										'jobid_bool':True if adhoc_search1 == [] or res1.job_category == 'adhoc_complaint' else False, 
										'emp_code':res.cse.emp_code if res.cse.emp_code else '',
										'adhoc_job_type_bool':True,
										'customer_id':cust_id,
										'use_service_card_readonly_bool':Flaggg1,
										'lastjob_bool':True if res.adhoc_jobtype == 'with_contract' else False,
										'record_date':current_date,
										#'service_area_search':res.service_area.id,
										'pms_search':res.pms.id,
										'job_id1':cnt1,
										'location_invisible':location2,
										'location_id2':res.location.id if res.location else '',
										'contract_frequency':res.contract_frequency.id if res.contract_frequency.id else '',
										'sq_foot_area':str(res.Sq_foot_area) if res.Sq_foot_area else '',
										'no_of_services':str(res.no_of_services) if res.no_of_services else '',
										'no_of_inspection':str(res.no_of_inspection) if res.no_of_inspection else '',
										}

				###################################Product order###################################################
				if res.job_category in  ['adhoc_product','product_complaint']:
					product_order_id = self.pool.get('stock.transfer').search(cr,uid,[('stock_transfer_no','=',res.delivery_order_no.stock_transfer_no)])
					product_order_obj= self.pool.get('stock.transfer').browse(cr,uid,product_order_id[0])
					delivery_order_no = product_order_obj.stock_transfer_no,
					delivery_address = product_order_obj.delivery_address,
					delivery_challan_no = product_order_obj.delivery_challan_no,
					web_order_no = product_order_obj.web_order_number,
					web_order_date = product_order_obj.web_order_date,
					against_free_replacement = product_order_obj.against_free_replacement,
					erp_order_no = product_order_obj.sale_order_no, 
					pse = product_order_obj.pse.id,
					new_job_data.update({'web_order_date':web_order_date[0],
										'delivery_order_no':delivery_order_no[0],
										'delivery_address':delivery_address[0],
										'delivery_challan_no':delivery_challan_no[0],
										'web_order_no':web_order_no[0],
										'against_free_replacement':against_free_replacement[0],
										'erp_order_no':erp_order_no[0],
										'pse':pse[0],
										'is_transfered':False,
										'job_id':job_id if job_id else '',})

				#####################################Service Order##################################################
				if res.job_category in ['adhoc_service','adhoc_service_complaint']:
					service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',res.service_order_no.order_number)])
					service_order_obj = self.pool.get('amc.sale.order').browse(cr,uid,service_order_id[0])
					service_order_no = service_order_obj.order_number,
					erp_order_date = service_order_obj.order_date,
					name_equipment = res.equipment_name.id,
					ordered_period_from = service_order_obj.order_period_from,
					ordered_period_to = service_order_obj.order_period_to,
					classification = service_order_obj.classification,
					service_type = service_order_obj.service_type,
					site_address1 = res.contact_location,
					contract_period = res.Contract_Period,
					new_job_data.update({'service_order_no':service_order_no[0],
										'erp_order_date':erp_order_date[0],
										'name_equipment':name_equipment[0],
										'ordered_period_from':ordered_period_from[0],
										'ordered_period_to':ordered_period_to[0],
										'contract_period':contract_period[0],
										'classification':classification[0],
										'service_type':service_type[0],
										'site_address1':site_address1[0],
										'job_id':job_id if job_id else '',})

				a = self.pool.get('res.scheduledjobs').create(cr,uid,new_job_data)
				if res.job_category in  ['adhoc_product','product_complaint']:
					for prod_line in product_order_obj.stock_transfer_product:
						self.pool.get('product.transfer').write(cr,uid,prod_line.id,{'exp_date':prod_line.batch.exp_date,'product_data':a})

				connect_obj = self.sock_connection1(cr, uid, ids, context=context)
				sock,userid,conn_flag,Err = socket_connect = self.self_connect(cr, uid, connect_obj, context=context)
				ip,dbname,usr,pwd,port = connect_obj
				user_id = partner_ids = ''
				contract_no = res.contract_no.contract_number
				contract_ids_1=False
				company = self.pool.get('res.users').browse(cr, uid, uid).company_id.name
				address1=''
				'''if not conn_flag:
				    if contract_no:
						contract_srh = [('contract_number','=',contract_no)]
						print 'contract Noooooooooooooooooo',contract_no,contract_srh
						#contract_ids_1 = conn_obj.execute('sale.contract', actions='search',vals_condition = contract_srh)
						contract_ids_1 = sock.execute(dbname,userid,pwd,'sale.contract','search',contract_srh)
				    if res.cust_name:
								partner_name = ['|',('ou_id','=',res.cust_name.ou_id),('name','=',res.cust_name.name)]
								#partner_ids = conn_obj.execute('res.partner', actions='search',vals_condition = partner_name)
								partner_ids = sock.execute(dbname, userid, pwd,'res.partner','search',partner_name)
								if not partner_ids:
									conn_flag=True
								if res.location:
											srch = self.pool.get('customer.line').search(cr,uid,[('partner_id','=',res.cust_name.id)])
											for part in self.pool.get('customer.line').browse(cr,uid,srch):
												if part.customer_address.id == res.location.id:

													address_in = [('location_id','=',part.location_id)]
													address_ids = sock.execute(dbname, userid, pwd, 'customer.line', 'search', address_in)

													fields = ['customer_address']
													data = sock.execute(dbname,userid, pwd, 'customer.line', 'read', address_ids, fields)
													for ln in data:
														address1 = ln['customer_address'][0]
								adhoc_record={
														'name_contact':partner_ids[0] if partner_ids else False,
														'name':res.cust_name.name if res.cust_name.name else False,
														'company_id': company if company else False,
														'state':'complaint' if res.job_category=='adhoc_complaint' else 'unscheduled',
														'contact_name':res.cust_name.contact_name if res.cust_name.contact_name else '',
														#'no_of_services':1 if res.job_category=='adhoc_standard' else 0,
														#'no_of_inspection':1 if res.job_category=='adhoc_inspection' else 0,
														'job_type':'service',
														'location_id':address if address else False,
														'pms':res.pms.name_template if res.pms.name_template else False,
														'job_category':res.job_category if res.job_category else False,
														'mobile':res.mobile_no if res.mobile_no else False,
														'req_date_time':res.req_tentdt if res.req_tentdt else False,
														'scheduled_job_id':str(job_id) if job_id else False,
														'is_ipm':True if is_ipm == True else False,
														'service_completion_slip':True if useservice_completeslip == True else False,
														#'service_area':res.service_area.name if res.service_area.name else False,
														'contract_start_date':res.contract_strtdt if res.contract_strtdt else False,
														'contract_end_date':res.contract_enddt if res.contract_enddt else False,
														'cse_new':res.cse.concate_name if res.cse.concate_name else False,
														'emp_code':res.cse.emp_code if res.cse.emp_code else False,
														#'contract_period':res.Contract_Period if res.Contract_Period else '',
														'mobile':res.mobile_no if res.mobile_no else False,
														'job_id':res.contract_no.contract_number if res.contract_no.contract_number else '',
														#'jobid_bool':True,
														'jobid_bool':True if adhoc_search1 == [] or res1.job_category == 'adhoc_complaint' else False,
														'adhoc_job_type':res.adhoc_jobtype if res.adhoc_jobtype else '',
														'adhoc_job_type_bool':True,
														'use_service_card_readonly_bool':Flaggg1,
														#'jobid_bool':True if adhoc_search1 == [] else False,
														'customer_id':str(cust_id),
														'record_date':str(current_date),
														'sale_contract':contract_ids_1[0] if contract_ids_1 else 0,
														'location_id2':address1 if address1 else False,
														'contract_frequency':res.contract_frequency.name if res.contract_frequency.name else '',
														'sq_foot_area':str(res.Sq_foot_area) if res.Sq_foot_area else '',
														'no_of_services':str(res.no_of_services) if res.no_of_services else '',
														'no_of_inspection':str(res.no_of_inspection) if res.no_of_inspection else '',
														}
								print "**********************************************",adhoc_record,cust_id,type(cust_id)
								final_adhoc = sock.execute(dbname, userid, pwd, 'res.scheduledjobs', 'create',adhoc_record)
								#print "*********************************************************************",adhoc_record
								#final_create = conn_obj.execute('res.scheduledjobs', actions='create',vals=adhoc_record)'''

				#if conn_flag:
				from openerpsync.sync import field_keys as syncField_Keys
				ops_offline_sync_data=syncField_Keys(adhoc_record)
				self.pool.get('ops.offline.sync').create(cr,uid,{'form_id':a,'sync_sequence':self.pool.get('ir.sequence').get(cr, uid, 'ops.offline.sync'),'srch_condn':"[('"'scheduled_job_id'"','"'='"','"+job_id+"')]",'src_model':'res.scheduledjobs','sync_data':ops_offline_sync_data,'dest_model':'res.scheduledjobs','sync_company_id':company_name11,'error_log':Err,'created_date':str(datetime.now())})	#'sync_company_id':,


				# for rec in self.pool.get('product.product').browse(cr,uid,[pms1[0]]):
				# 	if rec.chemicals:
				# 		for rec1 in rec.chemicals:
				# 			generic_name=rec1.generic_name.id
				# 			product_search = self.pool.get('product.product').search(cr,uid,[('generic_name','=',generic_name),('type_product','=','chemical')])				
				# 			if product_search:
				# 				for var2 in self.pool.get('product.product').browse(cr,uid,product_search):
				# 					product_id=var2.product_id.id
				# 					local_uom=var2.local_uom_id.name
				# 					operation_id1 = self.pool.get('res.product').create(cr,uid,{'name':var2.id,
				# 										'uom':local_uom,
				# 										'quantityhand':'0',
				# 										'chemical_id':int(a)})
				# for rec in self.pool.get('product.product').browse(cr,uid,[pms1[0]]):
				# 	if rec.stocks:
				# 		for rec1 in rec.stocks:
				# 			generic_name=rec1.generic_name.id
				# 			product_search = self.pool.get('product.product').search(cr,uid,[('generic_name','=',generic_name),('type_product','!=','chemical')])				
				# 			if product_search:
				# 				for var2 in self.pool.get('product.product').browse(cr,uid,product_search):
				# 					product_id=var2.product_id.id
				# 					local_uom=var2.local_uom_id.name
				# 					operation_id2 = self.pool.get('res.equipment').create(cr,uid,{'name_equipment':var2.id,
				# 									'uom_equipment':local_uom,
				# 									'quantityhand_equipment':'0',
				# 									'chemical_id_equipment':int(a)})
			for var in self.browse(cr,uid,ids):
				cr.execute(('update adhoc_job set state=%s where id = %s'),('mid',var.id))
		return True


	_columns= {
		'equipment_name':fields.many2one('product.product',string='Equipment Name'),
		'service_order_no':fields.many2one('amc.sale.order',string='Service Order'),
		'erp_order_no':fields.many2one('psd.sales.product.order',string='Product Order'),
		'delivery_order_no':fields.many2one('stock.transfer',string='Delivery Order'),
		# 'job_category':fields.selection([('adhoc_service','Adhoc-Service Order'),('adhoc_product','Adhoc-Product Order'),('adhoc_service_complaint','Adhoc - Service Complaint'),('product_complaint','Adhoc - Product Complaint')],'Job Category *'),
	}


class assign_res_search(osv.osv):
	_inherit="assign.res.search"

	_columns= {
		}


	def psd_create_assign_resource(self,cr,uid,ids,context=None):
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'psd_operations', 'psd_assign_resource_id')
		return {
			'type': 'ir.actions.act_window',
			'name': 'Confirm Product Job Orders', 
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'assign.resource',
			#'res_id':,
			'views': [(form_view and form_view[1] or False, 'form')],
			'target': 'current',
			'context':None
			}

	def psd_assign_search(self,cr,uid,ids,context=None):
		for rec in self.browse(cr,uid,ids):
			cust_ids=self.pool.get('assign.res.search.result').search(cr,uid,[('parent_rel','=',rec.id)])
			self.pool.get('assign.res.search.result').unlink(cr,uid,cust_ids,context=context)
		
		sql_str=sql_str_tech=sql_str_squad=''
		for res in self.browse(cr,uid,ids):
			if res.state:
				sql_str+=" and state='"+str(res.state)+"'"
			if res.created_date:
				sql_str+=" and created_date='"+str(res.created_date)+"'"
			if res.assign_id:
				sql_str+=" and assign_material_id='"+str(res.assign_id)+"'"
			if res.from_date:
				sql_str+=" and from_date>='"+str(res.from_date)+"'"
			if res.to_date:
				sql_str+=" and to_date<='"+str(res.to_date)+"'"

			if res.tech_id and res.squad_id:
				main_str="select distinct(ar.id),"+str(res.id)+",ar.assign_material_id,ar.created_date,ar.state from assign_resource ar,assign_resource_technician_grid artg,assign_resource_squad_grid arsg where ar.assign_material_id is not null and ((ar.id=artg.assign_resource_technician_line and  artg.tech_name="+str(res.tech_id.id)+") or (ar.id=arsg.assign_resource_squad_line and arsg.squad_name="+str(res.squad_id.id)+"))"
				main_str1=main_str+sql_str
				insert_command = "insert into assign_res_search_result(assign_id,parent_rel,name,created_date,state)("+str(main_str1)+")"
				cr.execute(insert_command)
				return

			if res.tech_id:
				main_str_tech="select distinct(ar.id),"+str(res.id)+",ar.assign_material_id,ar.created_date,ar.state from assign_resource ar,assign_resource_technician_grid artg where ar.id=artg.assign_resource_technician_line and ar.assign_material_id is not null and  artg.tech_name="+str(res.tech_id.id)
				main_str_tech1=main_str_tech+sql_str
				insert_command = "insert into assign_res_search_result(assign_id,parent_rel,name,created_date,state)("+str(main_str_tech1)+")"
				cr.execute(insert_command)
				return

			if res.squad_id:
				main_str_squad="select distinct(ar.id),"+str(res.id)+",ar.assign_material_id,ar.created_date,ar.state from assign_resource ar,assign_resource_squad_grid arsg where ar.id=arsg.assign_resource_squad_line and ar.assign_material_id is not null and arsg.squad_name="+str(res.squad_id.id)
				main_str_squad1=main_str_squad+sql_str
				insert_command = "insert into assign_res_search_result(assign_id,parent_rel,name,created_date,state)("+str(main_str_squad1)+")"
				cr.execute(insert_command)
				return

			if not res.tech_id and not res.squad_id:
				main_str="select distinct(ar.id),"+str(res.id)+",ar.assign_material_id,ar.created_date,ar.state,ar.tech_name from assign_resource ar,assign_resource_technician_grid artg,assign_resource_squad_grid arsg where ar.assign_material_id is not null and (ar.id=artg.assign_resource_technician_line or ar.id=arsg.assign_resource_squad_line) "
				var1=cr.execute(main_str)
				var = map(lambda x:x[0],cr.fetchall())
				main_str1=main_str+sql_str
				insert_command = "insert into assign_res_search_result(assign_id,parent_rel,name,created_date,state,tech_squad_name)("+str(main_str1)+")"
				cr.execute(insert_command)
				return
		


	def psd_assign_clear(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'tech_id':None,'squad_id':None,'from_date':None,'to_date':None,'name':None,'cust_id':None,'assign_id':None,'created_date':None,'state':None})
		for rec in self.browse(cr,uid,ids):
			cust_ids=self.pool.get('assign.res.search.result').search(cr,uid,[('parent_rel','=',rec.id)])
			self.pool.get('assign.res.search.result').unlink(cr,uid,cust_ids,context=context)
		return True





class assign_res_search_result(osv.osv):
	_inherit="assign.res.search.result"
	_columns={
		'tech_squad_name':fields.char(string="Technician/Squad Name",size=100),
		}
	
	def psd_open_assign_resource(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr,uid,'psd_operations','psd_assign_resource_id')
                    	return{
					'type': 'ir.actions.act_window',
					'name':'Confirm Product Job Orders',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'assign.resource',
                    'res_id':res.assign_id.id,
					'view_id':form_view[1],
					'target':'current',	
					}
assign_res_search_result()

class assign_resource(osv.osv):
	_inherit= "assign.resource"
	_columns= {
		'assign_resource_technician_one2many':fields.one2many('assign.resource.technician.grid','assign_resource_technician_line','Assign Resource Technician Grid'),
		}

	def psd_assign_resource_search(self,cr,uid,ids,context=None):
		for draft_id in self.pool.get('assign.resource.wizard.grid').search(cr,uid,[('state','=','draft')]):
			done_id = self.pool.get('assign.resource.wizard.grid').write(cr,uid,draft_id,{'state':'done'})
		for i in self.browse(cr,uid,ids): 
			if i.state == 'initial':
				for k in i.assign_resource_technician_one2many:
					self.pool.get('assign.resource.technician.grid').unlink(cr,uid,k.id)
				for val in i.assign_resource_squad_one2many:
					self.pool.get('assign.resource.squad.grid').unlink(cr,uid,val.id)
				#from_date = i.from_date
				#to_date = i.to_date

		for res in self.browse(cr,uid,ids):
			query_result2=[]
			if not res.from_date and not res.to_date:
				raise osv.except_osv(('Alert!'),('Please select From Date and To Date'))
			if not res.from_date:
				raise osv.except_osv(('Alert!'),('Please select From Date'))
			if not res.to_date:
				raise osv.except_osv(('Alert!'),('Please select To Date'))
			if i.state == 'initial':
					if res.from_date:
						from_date = datetime.strptime(res.from_date, "%Y-%m-%d")
						from_date = from_date.strftime('%Y-%m-%d %H:%M:%S')
					if res.to_date:
						to_date = datetime.strptime(res.to_date, "%Y-%m-%d")
						to_date = to_date.strftime('%Y-%m-%d %H:%M:%S')
					list_id = []
					true_items = []
					domain = []
					if res.from_date:
						true_items.append('from_date')
					if res.to_date:
						true_items.append('to_date')
					if res.technician_name:
						true_items.append('technician_name')
					if res.name_contact:
						true_items.append('name_contact')
					if res.squad_name:
						true_items.append('squad_name')
					for true_item in true_items:
						if true_item == 'technician_name':
							domain.append(('tech_id', '=', res.technician_name.id))
						if true_item == 'squad_name':
							domain.append(('squad_id', '=',res.squad_name.id))
					if res.from_date and res.to_date:		    
						domain.append(('job_start_date', '>=', str(from_date)))
						domain.append(('job_end_date', '<=', str(to_date)))	
					domain.append(('state', '=','scheduled'))
					search_record = self.pool.get('res.scheduledjobs').search(cr, uid, domain, context=context)
					technician_list = []
					squad_list = []
					for tech in self.pool.get('res.scheduledjobs').browse(cr,uid,search_record):
						if tech.tech_id.id:
							technician_list.append(tech.tech_id.id)
					for squad in self.pool.get('res.scheduledjobs').browse(cr,uid,search_record):
						if squad.squad_id.id:
							squad_list.append(squad.squad_id.id)
					domain.append(('tech_id','=',technician_list))
					tech_search = self.pool.get('res.scheduledjobs').search(cr,uid,domain)
					domain.append(('squad_id','=',squad_list))
					new_domain = []
					for domain_id in domain :
						domain_val = domain_id[0]
						if domain_val != 'tech_id':
							new_domain.append(domain_id)
					squad_search = self.pool.get('res.scheduledjobs').search(cr,uid,new_domain)
					t_material_name = ''
					t_cust_name = ''
					t_materials = ''
					t_customers = ''
					s_material_name = ''
					s_cust_name = ''
					s_materials = ''
					s_customers = ''
					############## Technician Search ##################
					for combinations in  self.pool.get('res.scheduledjobs').browse(cr,uid,tech_search):
						if combinations.tech_id:
							if combinations.product_transfer_id:
									for pro_line in combinations.product_transfer_id:
										if t_material_name == '': 
											t_material_name = t_material_name + '' + pro_line.product_name.name +'('+pro_line.product_name.uom_id.name+')'
										else:
											t_material_name = t_material_name + ',' + pro_line.product_name.name +'('+pro_line.product_name.uom_id.name+')'
							if combinations.name_contact:
								t_cust_name = combinations.name_contact.name
						srh_technician = self.pool.get('assign.resource.technician.grid').search(cr,uid,[('assign_resource_technician_line','=',res.id),('tech_name','=',combinations.tech_id.id)])
						if not srh_technician:
							self.pool.get('assign.resource.technician.grid').create(cr,uid,{'tech_name':combinations.tech_id.id,'assign_resource_technician_line':res.id,'name_contact':t_cust_name,'material_details':t_material_name})				
						else:
							search_ids= self.pool.get('assign.resource.technician.grid').search(cr,uid,[('assign_resource_technician_line','=',res.id),('tech_name','=',combinations.tech_id.id)])
							for each in self.pool.get('assign.resource.technician.grid').browse(cr,uid,search_ids):
								t_materials = each.material_details+','+t_material_name
								t_customers = each.name_contact+','+t_cust_name
							self.pool.get('assign.resource.technician.grid').write(cr,uid,each.id,{'name_contact':t_customers,'material_details':t_materials,'assign_resource_technician_line':res.id})				
 					

					############## Squad Search ##################
 					for combine in  self.pool.get('res.scheduledjobs').browse(cr,uid,squad_search):
						if combine.squad_id:
							if combine.product_transfer_id:
								for pro_line in combine.product_transfer_id:
									if s_material_name == '': 
										s_material_name = s_material_name + ''+ pro_line.product_name.name +'('+pro_line.product_name.uom_id.name+')'
									else: 
										s_material_name = s_material_name + ','+ pro_line.product_name.name +'('+pro_line.product_name.uom_id.name+')'


							if combine.name_contact:
								s_cust_name = combine.name_contact.name
						srh_squad = self.pool.get('assign.resource.squad.grid').search(cr,uid,[('assign_resource_squad_line','=',res.id),('squad_name','=',combine.squad_id.id)])
						if not srh_squad:
							self.pool.get('assign.resource.squad.grid').create(cr,uid,{'squad_name':combine.squad_id.id,'assign_resource_squad_line':res.id,'name_contact':s_cust_name,'material_details':s_material_name})
						else:
							search_ids= self.pool.get('assign.resource.squad.grid').search(cr,uid,[('assign_resource_squad_line','=',res.id),('squad_name','=',combine.squad_id.id)])
							for each in self.pool.get('assign.resource.squad.grid').browse(cr,uid,search_ids):
								s_materials = each.material_details+','+s_material_name
								s_customers = each.name_contact+','+s_cust_name
							self.pool.get('assign.resource.squad.grid').write(cr,uid,each.id,{'name_contact':s_customers,'material_details':s_materials})				

		return True


	def psd_assign_resource_clear(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'from_date':False,'to_date':False,'technician_name':False,'squad_name':False,'include_confirmed_jobs':False,'name_contact':False})
		for i in self.browse(cr,uid,ids):
			if i.assign_resource_technician_one2many:
				srh = self.pool.get('assign.resource.technician.grid').search(cr,uid,[('assign_resource_technician_line','=',i.id)])
				if srh:
					for var in self.pool.get('assign.resource.technician.grid').browse(cr,uid,srh):
						self.pool.get('assign.resource.technician.grid').unlink(cr,uid,var.id)
			if i.assign_resource_squad_one2many:
				srh_squad = self.pool.get('assign.resource.squad.grid').search(cr,uid,[('assign_resource_squad_line','=',i.id)])
				if srh_squad:
					for var1 in self.pool.get('assign.resource.squad.grid').browse(cr,uid,srh_squad):
						self.pool.get('assign.resource.squad.grid').unlink(cr,uid,var1.id)

	

	def psd_assign_report(self,cr,uid,ids,context=None):#a
		cr.execute('delete from technician_squad')
		x=0
		pre_full_name=''
		d = datetime.now()
		date= d.strftime("%d-%m-%Y")
	
		for res in self.browse(cr,uid,ids):
			if res.state == 'initial':
				raise osv.except_osv(('Alert!'),('Please Assign Resource'))
			if res.assign_resource_technician_one2many:
				for i in res.assign_resource_technician_one2many:
					wizard_id=self.pool.get('assign.resource.wizard').search(cr,uid,[('assign_resource_id','=',i.id)])
					emp_id = i.tech_name.id
					if emp_id:
						for na in self.pool.get('hr.employee').browse(cr,uid,[emp_id]):
							f_name = na.name if na.name else ''
							s_name = na.middle_name if na.middle_name else ''
							l_name = na.last_name if na.last_name else ''
							temp_name = [f_name,s_name,l_name]
							pre_full_name = ' '.join(filter(bool,temp_name))
					for j in self.pool.get('assign.resource.wizard').browse(cr,uid,wizard_id):
						grid_id=self.pool.get('assign.resource.wizard.grid').search(cr,uid,[('assign_resource_wizard_line','=',j.id)])
						if grid_id:							
							for k in self.pool.get('assign.resource.wizard.grid').browse(cr,uid,grid_id):
								x=x+1
								self.pool.get('technician.squad').create(cr,uid,{'sr_no':x,'technician':pre_full_name,'technician_chemical':k.chemical_name.name,'qty_issue':k.qty_issue,
			'qty_in_hand':k.qty_in_stock,'batch_no':k.batch.batch_no,'tag_id':k.tag_id.tag_name,'uom':k.uom.name,
			'technician_id1':res.id})

			if res.assign_resource_squad_one2many:
				for p in res.assign_resource_squad_one2many:
					squad_id=self.pool.get('assign.resource.wizard').search(cr,uid,[('assign_resource_id','=',p.id)])
					if squad_id:
						for q in self.pool.get('assign.resource.wizard').browse(cr,uid,squad_id):
							squad_grid=self.pool.get('assign.resource.wizard.grid').search(cr,uid,[('assign_resource_wizard_line','=',q.id)])
							if squad_grid:
								for r in self.pool.get('assign.resource.wizard.grid').browse(cr,uid,squad_grid):
									x=x+1
									self.pool.get('technician.squad').create(cr,uid,{'sr_no':x,'technician':p.squad_name.squad_name,'technician_chemical':r.chemical_name.name,'qty_issue':r.qty_issue,'qty_in_hand':r.qty_in_stock,
			'batch_no':r.batch.batch_no,'tag_id':r.tag_id.tag_name,'uom':r.uom.name,'technician_id1':res.id})
									
		self.write(cr,uid,ids,{'user_name':self.pool.get('res.users').browse(cr, uid, uid).name})						
		
		self.write(cr,uid,ids,{'date':date})		
		data = self.pool.get('assign.resource').read(cr, uid, [res.id],context)
		datas = {
				'ids': ids,
				'model': 'assign.resource',
				'form': data
			}

		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'assign.resources',
			'datas': datas,
			}

	def psd_update_report(self,cr,uid,ids,context=None):
		scheduled_obj = self.pool.get('res.scheduledjobs')
		tech_obj = self.pool.get('technician.chemical')
		c_dt = datetime.now()
		current_date = datetime.now().date()
		current_date_time = datetime.now().date()
		monthee = current_date.month
		year = current_date.year
		day = current_date.day
		for i in self.browse(cr,uid,ids):
			if not i.assign_resource_technician_one2many and not i.assign_resource_squad_one2many:
				raise osv.except_osv(('Alert!'),('No records found for updation'))
			batch_no=''
			godown=''
			godown_stock=0
			if i.assign_resource_technician_one2many:
				for j in i.assign_resource_technician_one2many:
					result1=self.pool.get('assign.resource.wizard').search(cr,uid,[('assign_resource_id','=',j.id)])
					for k in self.pool.get('assign.resource.wizard').browse(cr,uid,result1):
						self.pool.get('assign.resource.wizard').write(cr,uid,k.id,{'state':'stock_updated'})
						for l in k.assign_resource_wizard_one2many:
							batch_no=l.batch.id
							batch_srh = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',batch_no)])
							for batch in self.pool.get('res.batchnumber').browse(cr,uid,batch_srh):
								godown=batch.branch_name.id
								update_qty = l.qty_issue
								local_qty=0
								prod_local_qty=0
								product_search = self.pool.get('product.product').search(cr,uid,[('id','=',batch.name.id)])
								for kk in self.pool.get('product.product').browse(cr,uid,product_search):
										quantity_main = kk.quantity_available
										prod_local_qty = kk.local_qty
										n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',batch.name.id),('branch_name','=',godown)])
										if kk.uom_id.id != kk.local_uom_id.id:
											issue = l.qty_issue
											qty_val = float(l.qty_issue)/float(kk.local_uom_relation)
											actual_qty=float(batch.qty)-float(qty_val)
											avail_qty = float(batch.local_qty) - float(l.qty_issue)
											# print 'SSSSSSSSSSSSSSSSS',actual_qty
											local_qty=float(l.qty_issue)#*kk.local_uom_relation)
											godown_stock=0.0
											for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
												godown_stock+=n_batch_ids.local_qty
											godown_stock=(godown_stock) if godown_stock else 0
											#prod_local_qty1 = int(kk.quantity_available * kk.local_uom_relation)
											self.pool.get('res.batchnumber').write(cr,uid,batch.id,{'qty':actual_qty,'local_qty':int(float(batch.local_qty) - float(l.qty_issue))})
											new_qty = self.pool.get('product.product')._update_product_quantity(cr,uid,[batch.name.id])
											previous_qty = float(new_qty) - float(update_qty)
										elif kk.uom_id.id == kk.local_uom_id.id:
											avail_qty = float(batch.qty) - float(l.qty_issue)
											local_qty=float(l.qty_issue)
											godown_stock=0.0
											for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
												godown_stock+=n_batch_ids.local_qty
											godown_stock=(godown_stock) if godown_stock else 0
											#prod_local_qty1 = int(kk.quantity_available) 
											self.pool.get('res.batchnumber').write(cr,uid,batch.id,{'qty':float(batch.qty) - float(l.qty_issue)})
											new_qty = self.pool.get('product.product')._update_product_quantity(cr,uid,[batch.name.id])
											previous_qty = float(new_qty) - float(update_qty)
							
							
		#batchproduct_info rec
								ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':batch.id,'product_id':batch.name.id,'date':current_date,'sent':True,'qty':int(local_qty),'day':day,'month':monthee,'year':year,'product_qty':int(godown_stock),'datetime':c_dt,'branch_name':godown})
							self.pool.get('assign.resource.wizard.grid').write(cr,uid,[l.id],{'state':'done'})								
					
	
			
			if i.assign_resource_squad_one2many:
				for j in i.assign_resource_squad_one2many:
					godown=''
					godown_stock=0
					result1=self.pool.get('assign.resource.wizard').search(cr,uid,[('assign_resource_id','=',j.id)])
					for k in self.pool.get('assign.resource.wizard').browse(cr,uid,result1):
						self.pool.get('assign.resource.wizard').write(cr,uid,k.id,{'state':'stock_updated'})
						for l in k.assign_resource_wizard_one2many:
							if l.tag_id: 
								tag_id_srh = self.pool.get('product.tag').search(cr,uid,[('id','=',l.tag_id.id)])
								for var in self.pool.get('product.tag').browse(cr,uid,tag_id_srh):
									self.pool.get('product.tag').write(cr,uid,var.id,{'product_quantity':0})

							batch_no=l.batch.id
							batch_srh = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',batch_no)])
							for batch in self.pool.get('res.batchnumber').browse(cr,uid,batch_srh):
								godown=batch.branch_name.id
								update_qty = l.qty_issue
								local_qty=0
								prod_local_qty=0
								n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',batch.name.id),('branch_name','=',godown)])
								product_search = self.pool.get('product.product').search(cr,uid,[('id','=',batch.name.id)])
								for kk in self.pool.get('product.product').browse(cr,uid,product_search):
										quantity_main = kk.quantity_available
										prod_local_qty = kk.local_qty
										if kk.uom_id.id != kk.local_uom_id.id:
											issue = l.qty_issue
											qty_val = float(l.qty_issue)/float(kk.local_uom_relation)
											actual_qty=float(batch.qty)-float(qty_val)
											avail_qty = float(batch.local_qty) - float(l.qty_issue)
											# print 'SSSSSSSSSSSSSSSSS',actual_qty
											local_qty=float(l.qty_issue)#*kk.local_uom_relation)
											godown_stock=0.0
											for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
												godown_stock+=n_batch_ids.local_qty
											godown_stock=(godown_stock) if godown_stock else 0
											#prod_local_qty1 = int(kk.quantity_available * kk.local_uom_relation)
											self.pool.get('res.batchnumber').write(cr,uid,batch.id,{'qty':actual_qty,'local_qty':int(float(batch.local_qty) - float(l.qty_issue))})
											new_qty = self.pool.get('product.product')._update_product_quantity(cr,uid,[batch.name.id])
											previous_qty = float(new_qty) - float(update_qty)
										elif kk.uom_id.id == kk.local_uom_id.id:
											avail_qty = float(batch.qty) - float(l.qty_issue)
											local_qty=float(l.qty_issue)
											godown_stock=0.0
											for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
												godown_stock+=n_batch_ids.local_qty
											godown_stock=(godown_stock) if godown_stock else 0
											#prod_local_qty1 = int(kk.quantity_available) 
											self.pool.get('res.batchnumber').write(cr,uid,batch.id,{'qty':float(batch.qty) - float(l.qty_issue)})
											new_qty = self.pool.get('product.product')._update_product_quantity(cr,uid,[batch.name.id])
											previous_qty = float(new_qty) - float(update_qty)
							
							
		#batchproduct_info rec

								ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':batch.id,'product_id':batch.name.id,'date':current_date,'sent':True,'qty':int(local_qty),'day':day,'month':monthee,'year':year,'product_qty':int(godown_stock),'datetime':c_dt,'branch_name':batch.branch_name.id})
							self.pool.get('assign.resource.wizard.grid').write(cr,uid,[l.id],{'state':'done'})	

		for res in self.browse(cr,uid,ids):
			to_date=res.to_date
			from_date=res.from_date
			customer_name=res.name_contact.id
			if res.assign_resource_technician_one2many:
				for rec in res.assign_resource_technician_one2many:
						# if not rec.chemical_name_qty:
						# 	raise osv.except_osv(('Alert!'),('Please Select Chemical/Equipment to assign'))
						technician=rec.tech_name.id if rec.tech_name else False
						technician1=rec.tech_name.concate_name
						from_date=res.from_date
						to_date=res.to_date
						if res.include_confirmed_jobs==True and res.include_extended_jobs==True:
							if res.name_contact:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed','extended')),('assigned_technician','=',technician),('job_start_date','>=',from_date),('job_start_date','<=',to_date),('name_contact','=',customer_name)])
								
							else:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed','extended')),('assigned_technician','=',technician),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])

						if res.include_confirmed_jobs==True and res.include_extended_jobs==False:
							#job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('job_start_date','>=',from_date),('job_end_date','<=',to_date),('state','in',('scheduled','confirmed')),('assigned_technician','=',technician)])
							if res.name_contact:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed',)),('assigned_technician','=',technician),('job_start_date','>=',from_date),('job_start_date','<=',to_date),('name_contact','=',customer_name)])
								
							else:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed',)),('assigned_technician','=',technician),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])

						if res.include_extended_jobs==True and res.include_confirmed_jobs==False:
							#job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('job_start_date','>=',from_date),('job_end_date','<=',to_date),('state','in',('scheduled','confirmed')),('assigned_technician','=',technician)])
							if res.name_contact:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','extended')),('assigned_technician','=',technician),('job_start_date','>=',from_date),('job_start_date','<=',to_date),('name_contact','=',customer_name)])
								
							else:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','extended')),('assigned_technician','=',technician),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])
								 
						if res.include_confirmed_jobs==False and  res.include_extended_jobs==False:
							#job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('job_start_date','>=',from_date),('job_end_date','<=',to_date),('state','=','scheduled'),('assigned_technician','=',technician)])
							if res.name_contact:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','=','scheduled'),('assigned_technician','=',technician),('job_start_date','>=',from_date),('job_start_date','<=',to_date),('name_contact','=',customer_name)])
								

							else:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','=','scheduled'),('assigned_technician','=',technician),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])
						scheduled_obj = self.pool.get('res.scheduledjobs')
						tech_obj = self.pool.get('technician.chemical')
						for job in scheduled_obj.browse(cr, uid, job_confirm_id):
							state_new=job.state
							job_start_date_date=job.job_start_date
							job_start_end_date=job.job_end_date
							value = job.assign_resource_id
							if value:
								final_val = str(value) + ',' + str(res.id)
							else:
								final_val = res.id
							if state_new=='extended':
								self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'assign_material_bool':True,'assign_resource_id':final_val,'record_date':current_date})
							else:
								self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'state':'confirmed','assign_material_bool':True,'assign_resource_id':final_val,'record_date':current_date})
							if state_new=='scheduled':
								#self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'state':'confirmed'})
								if job.erp_order_no:
									product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',job.erp_order_no)])
									invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',job.delivery_challan_no)])
									if invoice_id:
										self.pool.get('job.history').create(cr,uid,{'contract_no':job.job_id,'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'job_reschedule_date':str(datetime.now()),
												'technician_squad':technician1,'job_status':'Job confirmed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job.job_end_time,'record_date':current_date,	'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
									else:
										self.pool.get('job.history').create(cr,uid,{'contract_no':job.job_id,'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'job_reschedule_date':str(datetime.now()),
												'technician_squad':technician1,'job_status':'Job confirmed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job.job_end_time,'record_date':current_date,	'product_order_id':product_order_id[0]})
								if job.service_order_no:
									service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',job.service_order_no)])
									invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',job.service_order_no)])
									if invoice_id:
										self.pool.get('job.history').create(cr,uid,{'contract_no':job.job_id,'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'job_reschedule_date':str(datetime.now()),
												'technician_squad':technician1,'job_status':'Job confirmed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job.job_end_time,'record_date':current_date,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
									else:
										self.pool.get('job.history').create(cr,uid,{'contract_no':job.job_id,'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'job_reschedule_date':str(datetime.now()),
												'technician_squad':technician1,'job_status':'Job confirmed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job.job_end_time,'record_date':current_date,'service_order_id':service_order_id[0]})
							job_id=job.job_id
							job_id1=job.job_id1+1
							prev_assign_tech=job.assigned_technician.name
							pms1=job.pms_search.id
							location_id2=job.location_id2
							address_on_fly=job.address_on_fly
							technician_squad_merge1=job.technician_squad_merge
							search_record1 = self.pool.get('res.scheduledjobs').search(cr,uid,[('name_contact','=',job.name_contact.id),('job_id','=',job_id),('job_id1','=',job_id1),('pms_search','=',pms1),('address_on_fly','=',address_on_fly)])
							if search_record1:
								for job1 in self.pool.get('res.scheduledjobs').browse(cr,uid,search_record1):
									self.pool.get('res.scheduledjobs').write(cr,uid,job1.id,{'prev_assign_tech':technician_squad_merge1})
							# print "\n HELLO WORLD",job.chemical_rec_one2many,technician,res.id
							job_line_m2o = job.id
							final_vals = ''
							update_id = False
							job_line_id = job.scheduled_job_id
							track_line_id = []
							track_id = []
							track_chem_id = []
							line_vals = {
								'tech_date':job_start_date_date,
								'tech_name':False,
								'job_id':job_line_id,
								'chemical_id':final_vals,
								'chemical_record_line':job_line_m2o
							}
							if isinstance(job.chemical_rec_one2many, list) and job.chemical_rec_one2many:
								for line in job.chemical_rec_one2many:
									# print "\n STEP ",line.tech_name
									line_id = line.id
									final_vals = line.chemical_id
									emp_id = line.tech_name.id if line.tech_name else False
									if track_line_id.count(emp_id):
										pass
									else:
										track_line_id.extend([emp_id])
										track_id.extend([line_id])
										track_chem_id.extend([final_vals])
							if technician not in track_line_id:
								track_line_id.extend([technician])
								final_vals = res.id
								line_vals.update({
									'tech_name':technician,
									'chemical_id':final_vals,
								})
								# print "\n Final Vals ",final_vals
								tech_obj.create(cr, uid, line_vals)
									#query = 'UPDATE technician_chemical set chemical_id='+final_vals+' where id ='+line_id+";"
									#cr.execute(query)
							else:
								index = track_line_id.index(technician)
								update_id = track_id[index]
								final_vals = track_chem_id[index]
								final_vals = final_vals +','+str(res.id)
								line_vals.update({
									'tech_name':technician,
									'chemical_id':final_vals,
								})
								tech_obj.write(cr, uid, update_id, line_vals)
							self.pool.get('res.scheduledjobs').write_jobs(cr,uid,job.id)
							#cr.commit()
			if res.assign_resource_squad_one2many:
				
				for rec in res.assign_resource_squad_one2many:
						# if not rec.chemical_name_qty:
						# 	raise osv.except_osv(('Alert!'),('Please Select Chemical/Equipment to assign'))
						squad=rec.squad_name.squad_name
						track_squad_id=rec.squad_name.id if rec.squad_name else False
						#technician1=rec.tech_name.concate_name
						from_date=res.from_date
						to_date=res.to_date
						if res.include_confirmed_jobs==True and res.include_extended_jobs==True:
							#job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('job_start_date','>=',from_date),('job_end_date','<=',to_date),('state','in',('scheduled','confirmed')),('assigned_squad','=',squad)])#a
							if res.name_contact:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed','extended')),('assigned_squad','=',squad),('job_start_date','>=',from_date),('job_start_date','<=',to_date),('name_contact','=',customer_name)])#a
							else:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed','extended')),('assigned_squad','=',squad),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])#a
						if res.include_confirmed_jobs==True and res.include_extended_jobs==False:
							#job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('job_start_date','>=',from_date),('job_end_date','<=',to_date),('state','in',('scheduled','confirmed')),('assigned_squad','=',squad)])#a
							if res.name_contact:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed',)),('assigned_squad','=',squad),('job_start_date','>=',from_date),('job_start_date','<=',to_date),('name_contact','=',customer_name)])#a
							else:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed',)),('assigned_squad','=',squad),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])#a
						if res.include_extended_jobs==True and res.include_confirmed_jobs==False:
							#job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('job_start_date','>=',from_date),('job_end_date','<=',to_date),('state','in',('scheduled','confirmed')),('assigned_squad','=',squad)])#a
							if res.name_contact:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','extended')),('assigned_squad','=',squad),('job_start_date','>=',from_date),('job_start_date','<=',to_date),('name_contact','=',customer_name)])#a
							else:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','extended')),('assigned_squad','=',squad),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])#a


						if res.include_confirmed_jobs==False and res.include_extended_jobs==False:
							#job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('job_start_date','>=',from_date),('job_end_date','<=',to_date),('state','=','scheduled'),('assigned_squad','=',squad)])
							if res.name_contact:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','=','scheduled'),('assigned_squad','=',squad),('job_start_date','>=',from_date),('job_start_date','<=',to_date),('name_contact','=',customer_name)])
							else:
								job_confirm_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','=','scheduled'),('assigned_squad','=',squad),('job_start_date','>=',from_date),('job_start_date','<=',to_date)])

						for job in self.pool.get('res.scheduledjobs').browse(cr,uid,job_confirm_id):
							
							job_start_date_date=job.job_start_date
							state_new=job.state
							value = job.assign_resource_id1
							if value:
								final_val = str(value) + ',' + str(res.id)
							else:
								final_val = res.id
							if state_new=='extended':
								self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'assign_material_bool':True,'assign_resource_id1':final_val,'record_date':current_date,})
								
							else:
								self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'state':'confirmed','assign_material_bool':True,'assign_resource_id1':final_val,'record_date':current_date,})

							if state_new=='scheduled':
								if job.erp_order_no:
									product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',job.erp_order_no)])
									invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',job.delivery_challan_no)])
									if invoice_id:
										self.pool.get('job.history').create(cr,uid,{'contract_no':job.job_id,'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'job_reschedule_date':str(datetime.now()),
										'technician_squad':squad,'job_status':'Job confirmed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job.job_end_time,'record_date':current_date,'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
									else:
										self.pool.get('job.history').create(cr,uid,{'contract_no':job.job_id,'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'job_reschedule_date':str(datetime.now()),
										'technician_squad':squad,'job_status':'Job confirmed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job.job_end_time,'record_date':current_date,'product_order_id':product_order_id[0]})
								if job.service_order_no:
									service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',job.service_order_no)])
									invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',job.service_order_no)])
									if invoice_id:
										self.pool.get('job.history').create(cr,uid,{'contract_no':job.job_id,'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'job_reschedule_date':str(datetime.now()),
										'technician_squad':squad,'job_status':'Job confirmed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job.job_end_time,'record_date':current_date,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
									else:
										self.pool.get('job.history').create(cr,uid,{'contract_no':job.job_id,'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'job_reschedule_date':str(datetime.now()),
										'technician_squad':squad,'job_status':'Job confirmed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job.job_end_time,'record_date':current_date,'service_order_id':service_order_id[0]})


							job_id=job.job_id
							job_id1=job.job_id1+1
							prev_assign_squad=job.sq_name_new
							pms1=job.pms_search.id
							location_id2=job.location_id2
							search_record1 = self.pool.get('res.scheduledjobs').search(cr,uid,[('name_contact','=',job.name_contact.id),('job_id','=',job_id),('job_id1','=',job_id1),('pms_search','=',pms1),('location_id2','=',location_id2)])
							if search_record1:
								for job1 in self.pool.get('res.scheduledjobs').browse(cr,uid,search_record1):
									self.pool.get('res.scheduledjobs').write(cr,uid,job1.id,{'prev_assign_squad':prev_assign_squad})
#---------------------------------new squad---------------------------------------------------------------------------------
							# print "\n HELLO WORLD",job.chemical_rec_one2many,track_squad_id,res.id
							job_line_m2o = job.id
							final_vals = ''
							update_id = False
							job_line_id = job.scheduled_job_id
							track_line_id = []
							track_id = []
							track_chem_id = []
							line_vals = {
								'tech_date':job_start_date_date,
								'squad_name':False,
								'job_id':job_line_id,
								'chemical_id':final_vals,
								'chemical_record_line':job_line_m2o,
								'squad_bool':True,
							}
							if isinstance(job.chemical_rec_one2many, list) and job.chemical_rec_one2many:
								for line in job.chemical_rec_one2many:
									# print "\n STEP ",line.tech_name
									line_id = line.id
									final_vals = line.chemical_id
									emp_id = line.squad_name.id if line.squad_name else False
									if track_line_id.count(emp_id):
										pass
									else:
										track_line_id.extend([emp_id])
										track_id.extend([line_id])
										track_chem_id.extend([final_vals])
							if track_squad_id not in track_line_id:
								track_line_id.extend([track_squad_id])
								final_vals = res.id
								line_vals.update({
									'squad_name':track_squad_id,
									'chemical_id':final_vals,
								})
								# print "\n Final Vals ",final_vals
								tech_obj.create(cr, uid, line_vals)
									#query = 'UPDATE technician_chemical set chemical_id='+final_vals+' where id ='+line_id+";"
									#cr.execute(query)
							else:
								index = track_line_id.index(track_squad_id)
								update_id = track_id[index]
								final_vals = track_chem_id[index]
								final_vals = final_vals +','+str(res.id)
								line_vals.update({
									'squad_name':track_squad_id,
									'chemical_id':final_vals,
								})
								tech_obj.write(cr, uid, update_id, line_vals)
							self.pool.get('res.scheduledjobs').write_jobs(cr,uid,job.id)
							# print "\n FINAL VALS ",final_vals
#-----------------------------------end squad-----------------------------------------------------------------------------

		date=datetime.now()
		#date1=datetime.strptime(str(date),"%d-%m-%Y %H:%M:%S")
		seq_id1 = self.pool.get('ir.sequence').get(cr, uid,'assign.resource')
		ou_id1 = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		today_date = datetime.now().date()
		year = today_date.year
		year12=today_date.strftime('%y')
		company_id=self.pool.get('res.users').browse(cr, uid, uid).company_id.id
		for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
			job_code=comp_id.assign_resource_id
			job_id =str(ou_id1)+job_code+year12+str(seq_id1)
		# print "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",job_id,seq_id1
		#print aaaa
		self.write(cr,uid,ids,{'state':'stock_updated','assign_material_id':job_id,'created_date':date,'assign_material_date':date})
	    

					
		# just remove the code for functionality
		#self.write(cr,uid,ids,{'state':'stock_updated'})
		return True

assign_resource()





class assign_resource_technician_grid(osv.osv):
	_inherit= "assign.resource.technician.grid"
	_columns= {
		'material_details':fields.char('Material Details/Qty',size=500),
		'name_contact':fields.char(string="Customer Name",size=500),
		'assign_resource_technician_line':fields.many2one('assign.resource',ondelete='cascade',),
		}
assign_resource_technician_grid()

class assign_resource_squad_grid(osv.osv):
	_inherit= "assign.resource.squad.grid"
	_columns= {
		'material_details':fields.char('Material Details/Qty',size=500),
		'name_contact':fields.char(string="Customer Name",size=500),
		}
assign_resource_squad_grid()



# class stock_transfer(osv.osv):
# 	_inherit= "stock.transfer"
# 	_columns= {
# 		'update_delivery_id':fields.many2one('update.delivery',string="Update Delivery ID"),
# 		}		
# stock_transfer()

class consumption_report_search(osv.osv):
	_inherit="consumption.report.search"
	_columns={
				
		}

	_defaults={
		
		}
	
	def psd_create_consumption_report(self,cr,uid,ids,context=None):
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'psd_operations', 'psd_consumption_report_form')
		return {
			'type': 'ir.actions.act_window',
			'name': 'Delivered Product Job Orders', 
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'consumption.report',
			#'res_id':,
			'views': [(form_view and form_view[1] or False, 'form')],
			'target': 'current',
			'context':None
			}

	#avi 04092015
	def psd_consumption_search(self,cr,uid,ids,context=None):
		sql_str=sql_str_tech=sql_str_squad=''
		for res in self.browse(cr,uid,ids):
			cust_ids=self.pool.get('consumption.report.search.result').search(cr,uid,[('parent_rel','=',res.id)])
			self.pool.get('consumption.report.search.result').unlink(cr,uid,cust_ids,context=context)
		
		sql_str=sql_str_tech=sql_str_squad=''
		for res in self.browse(cr,uid,ids):
			if res.state:
				sql_str+=" and state='"+str(res.state)+"'"
			if res.created_date:
				sql_str+=" and created_date='"+str(res.created_date)+"'"
			if res.consumption_id:
				sql_str+=" and consumption_material_id='"+str(res.consumption_id)+"'"
			if res.from_date:
				sql_str+=" and from_date>='"+str(res.from_date)+"'"
			if res.to_date:
				sql_str+=" and to_date<='"+str(res.to_date)+"'"
			if res.name:
				sql_str+=" and com.cust_name="+str(res.name.id)
			if res.tech_id and res.squad_id:
				main_str="select distinct(cr.id),"+str(res.id)+",cr.consumption_material_id,cr.created_date,cr.state from consumption_report cr,consumption_one2many com where cr.consumption_material_id is not null and cr.id=com.consumption_many2one and (com.technician_name ="+str(res.tech_id.id)+" or  and com.squad_name="+str(res.squad_id.id)+")"
				main_str1=main_str+sql_str
				insert_command = "insert into consumption_report_search_result(consumption_id,parent_rel,name,created_date,state)("+str(main_str1)+")"
				cr.execute(insert_command)
				return

			if res.tech_id:
				main_str_tech="select distinct(cr.id),"+str(res.id)+",cr.consumption_material_id,cr.created_date,cr.state from consumption_report cr,consumption_one2many com where cr.consumption_material_id is not null and cr.id=com.consumption_many2one and  com.technician_name="+str(res.tech_id.id)
				main_str_tech1=main_str_tech+sql_str
				insert_command = "insert into consumption_report_search_result(consumption_id,parent_rel,name,created_date,state)("+str(main_str_tech1)+")"
				cr.execute(insert_command)
				return

			if res.squad_id:
				main_str_squad="select distinct(cr.id),"+str(res.id)+",cr.consumption_material_id,cr.created_date,cr.state from consumption_report cr,consumption_one2many com where cr.consumption_material_id is not null and cr.id=com.consumption_many2one and com.squad_name="+str(res.squad_id.id)
				main_str_squad1=main_str_squad+sql_str
				insert_command = "insert into consumption_report_search_result(consumption_id,parent_rel,name,created_date,state)("+str(main_str_squad1)+")"
				cr.execute(insert_command)
				return

			if not res.tech_id and not res.squad_id:
				main_str="select distinct(cr.id),"+str(res.id)+",cr.consumption_material_id,cr.created_date,cr.state from consumption_report cr,consumption_one2many com where cr.consumption_material_id is not null and cr.id=com.consumption_many2one"
				main_str1=main_str+sql_str
				insert_command = "insert into consumption_report_search_result(consumption_id,parent_rel,name,created_date,state)("+str(main_str1)+")"
				cr.execute(insert_command)
				return

	def psd_consumption_clear(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'pms':None,'tech_id':None,'squad_id':None,'from_date':None,'to_date':None,'name':None,'cust_id':None,'assign_id':None,'created_date':None,'state':None})
		for rec in self.browse(cr,uid,ids):
			cust_ids=self.pool.get('consumption.report.search.result').search(cr,uid,[('parent_rel','=',rec.id)])
			self.pool.get('consumption.report.search.result').unlink(cr,uid,cust_ids,context=context)
		return True

class consumption_report_search_result(osv.osv):
	_inherit="consumption.report.search.result"


	def psd_open_consumption_report(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr,uid,'psd_operations','psd_consumption_report_form')
        	return{
				'type': 'ir.actions.act_window',
				'name':'Delivered Product Job Search Orders',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'consumption.report',
		        'res_id':res.consumption_id.id,
				'view_id':form_view[1],
				'target':'current',	
				}
	_columns={
		'tech_squad_name':fields.char('Technician/Squad Name',size=100),
		}

class consumption_report(osv.osv):
	_inherit = "consumption.report"

	_columns = {
		'delivery_note_no':fields.char('Delivery Note No.',size=56),
		'state': fields.selection([('initial','Confirmed'),('final','Completed')],'State'),
	}

	def psd_search_record(self,cr,uid,ids,context=None):
		curr_id=''
		for res in self.browse(cr,uid,ids):
			if res.state == 'initial':
				for req in res.consumption_one2many:
					self.pool.get('consumption.one2many').write(cr,uid,req.id,{'consumption_many2one':None})
		for res in self.browse(cr,uid,ids):
			if not res.from_date and not res.to_date:
				raise osv.except_osv(('Alert!'),('Please select From Date and To Date'))
			if not res.from_date:
				raise osv.except_osv(('Alert!'),('Please select From Date'))
			if not res.to_date:
				raise osv.except_osv(('Alert!'),('Please select To Date'))
			if res.from_date:
				from_date = datetime.strptime(res.from_date, "%Y-%m-%d")
				from_date = from_date.strftime('%Y-%m-%d %H:%M:%S')[:10]
			if res.to_date:
				to_date = datetime.strptime(res.to_date, "%Y-%m-%d")
				to_date = to_date.strftime('%Y-%m-%d %H:%M:%S')[:10]
			if res.state == 'initial':
					from_date=res.from_date
					to_date=res.to_date
					list_id = []
					Sql_Str = ''
					if res.from_date:
						Sql_Str = Sql_Str + " and job_start_date >= '"+ str(from_date) + "'"
					if res.to_date:
						Sql_Str = Sql_Str +" and job_end_date <= '"  + str(to_date) + "'"
					if res.job_id:
						Sql_Str = Sql_Str + " and  id ='" +str(res.job_id.id) + "'"
					if res.technician_name:
						Sql_Str = Sql_Str +" and assigned_technician = '"  + str(res.technician_name.id) + "'"
					if res.squad_name:
						Sql_Str = Sql_Str + " and  assigned_squad ='" +str(res.squad_name.id) + "'"
					if res.cust_name:
						Sql_Str = Sql_Str + " and  name_contact ='" +str(res.cust_name.id) + "'"

					Main_Str = "select id from res_scheduledjobs where id > 0 and state in ('confirmed','extended')"
					Main_Str1 = Main_Str + Sql_Str
					cr.execute(Main_Str1)
					query_result2=cr.fetchall()
					#for x in query_result2:

					search_record=self.pool.get('res.scheduledjobs').search(cr,uid,[('id','=',query_result2)])
					for i in self.pool.get('res.scheduledjobs').browse(cr,uid,search_record):
						name_array = []
						scheduled_job_id=i.id
						cust_name=i.name_contact.id
						pms=i.pms
						technician_name=i.assigned_technician.id
						squad_name=i.assigned_squad.id
						if i.service_area_on_fly:
							service_area=i.service_area_on_fly.name
							name_array.append(service_area)
						#if i.address_on_fly:
						contract_loc=i.address_on_fly
						name_array.append(contract_loc)
						address = ''
						cust_address = ''
						# print "contract_locsasasasasas",contract_loc
						if name_array != []:
							for val in name_array:
								var = val
								if address == '':
									address = var
								else:
									address=address +','+var
						if i.job == 'delivery':
							cust_address = i.delivery_address
						if i.job == 'service':
							cust_address = i.site_address1
						self.pool.get('consumption.one2many').create(cr,uid,{'consumption_many2one':res.id,
																			'cust_name':cust_name,
																			'job_id':scheduled_job_id,
																			'technician_name':technician_name,
																			'squad_name':squad_name,
																			'job_category':i.job_category,
																			'delivery_note_no':i.delivery_challan_no,
																			'delivery_address':cust_address,
																			'delivery_note_date':i.delivery_note_date,
																			})

		return True

	def psd_clear(self,cr,uid,ids,context=None):
		for o in self.browse(cr,uid,ids):
			self.pool.get('consumption.report').write(cr,uid,o.id,{'from_date':False,'to_date':False,'pms':False,'job_id':False,'technician_name':False,'squad_name':False,'cust_name':False})
			for req in o.consumption_one2many:
				self.pool.get('consumption.one2many').unlink(cr,uid,req.id)
		return True

	def psd_record_consumption(self,cr,uid,ids,context=None):	
		res_tmp_id = []
		idd=job_end_date_new_change=''
		manpower_obj = self.pool.get('hr.manpower.cost')
		current_date = datetime.now().date()
		for res in self.browse(cr,uid,ids):
			if not res.consumption_one2many:
				raise osv.except_osv(('Alert!'),('No records found for updation'))
			# if res.consumption_one2many:
			# 	for rec in res.consumption_one2many:
			# 			if rec.check==False:
			# 				raise osv.except_osv(('Alert!'),('Please Enter Consumption Details'))

		for i in self.browse(cr,uid,ids):
			#connect_obj = self.sock_connection(cr, uid, ids, context=context)
			#sock,userid,conn_flag,Err = socket_connect= self.connect(cr, uid, connect_obj, context=context)
			#ip,dbname,usr,pwd,port = connect_obj
			assign=pms1=job_id1=job_date=inspec_line_id=complain_request_id=pre_full_name=full_name=chem_total1=sq_tech_name=treatment_name=treatment_name_total=treatment_name_total1=''
			job_completion_date=False
			user_obj = self.pool.get('res.users')
			company_id =user_obj.get_uid_company_id(cr, uid, context=context)
			company_id=company_id[0].name

			for var in i.consumption_one2many:
				if var.check != True :
					self.pool.get('consumption.one2many').unlink(cr,uid,var.id)
				company_name=''
				company_id = self.pool.get('res.company').search(cr,uid,[('branch_type','=','ccc')])
				job_id1=var.job_id.scheduled_job_id
				job_id3=var.job_id.id
				if company_id:
					company_name = self.pool.get('res.company').browse(cr,uid,company_id[0]).name
					current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
				#for job in i.consumption_one2many:
					#job_id=job.job_id.scheduled_job_id
				current_date = datetime.now().date()
				current_date1 = datetime.now()
				current_date1=datetime.strftime(current_date1,"%y_%m_%d_%H_%M_%S")
				con_cat = str(company_name)+'_'+current_company+'_Jobs_consumption_'+str(job_id1)+'_'+current_date1+'.sql'
				
				filename = os.path.expanduser('~')+'/sql_files/'+con_cat
				directory_name = str(os.path.expanduser('~')+'/sql_files/')
				d = os.path.dirname(directory_name)

				if not os.path.exists(d):
					os.makedirs(d)
				job_closed_date1=datetime.now().date()
				search = self.pool.get('res.scheduledjobs').search(cr,uid,[('id','=',job_id3)])
				search_product = ''
				for jjob in self.pool.get('res.scheduledjobs').browse(cr,uid,search):
					contract_no = jjob.job_id
#----------------ccc ops integration start---------------------------------------------------------------------------------------
					name=jjob.name_contact.name
					job_completion_date=datetime.now()
					# print "gggggggggggg",job_completion_date
					complain_request_id=jjob.complaint_request_id
					assigned_tech=chem_total=''
					if jjob.job_category == 'complaint':
						job_completion_date1=pre_tech=pre_squad=full_na1=''
						wizard11 = self.pool.get('consumption.report.detail').search(cr,uid,[('consumption_report_id','=',var.id)])
						if wizard11:
							for var1 in self.pool.get('consumption.report.detail').browse(cr,uid,wizard11):
								opening = self.pool.get('res.scheduledjobs').search(cr,uid,[('name_contact','=',var1.cust_name.id),('pms','=',var.pms),('state','=','job_done')],order="req_date_time desc",limit=1)

								if opening:
									ct=1
									ct1=1
									for vv in self.pool.get('res.scheduledjobs').browse(cr,uid,opening):
										if vv.consumed_estimate_actual_line:
											for chem_det in vv.consumed_estimate_actual_line:
												if chem_det.chemical_name.type_product == 'chemical' and chem_det.quantity != 0:
													ct+=1
													ch_name=chem_det.chemical_name.name
													uom=chem_det.uom.name
													quantity=chem_det.quantity 
													chem_total= chem_total + str(ch_name)+" "+str(quantity)+" "+str(uom)+ ','
													chem_total1=chem_total[:-1]
										# print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",chem_total1
										if vv.treatment_line1:
											for treatment_det in vv.treatment_line1:
													ct1+=1
													treatment_name=treatment_det.treatment_name
													treatment_name_total= treatment_name_total + str(treatment_name)+','
													treatment_name_total1=treatment_name_total[:-1]
										# print "----------------------------------------------------------------",treatment_name_total1
										job_completion_date1=vv.job_completion_date
										pre_tech=vv.assigned_technician.id
										if pre_tech:
											for na in self.pool.get('hr.employee').browse(cr,uid,[pre_tech]):
												f_name = na.name if na.name else ''
												#s_name = na.middle_name if na.middle_name else ''
												l_name = na.last_name if na.last_name else ''
												temp_name = [f_name,l_name]
												pre_full_name = ' '.join(filter(bool,temp_name))
												# print "pre full name",pre_full_name
										pre_squad=vv.sq_name_new
										full_na=''
										squad_search_id=self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',pre_squad)])
										# print "sqqqqqqqqqqqqsssssssssqqqqqqq",squad_search_id
										for tech in self.pool.get('res.define.squad').browse(cr,uid,squad_search_id):
											if tech.tech2:
												for i in tech.tech2:
													f_name_id=self.pool.get('hr.employee').search(cr,uid,[('name','=',i.name)])
													for j in self.pool.get('hr.employee').browse(cr,uid,f_name_id):
														f_name = j.name if j.name else ''
														#s_name = j.middle_name if j.middle_name else ''
														l_name = j.last_name if j.last_name else ''
														temp_name = [f_name,l_name]
														full_na = full_na+' '.join(filter(bool,temp_name))+','
														#full_na=full_na+full_na+','
													full_na1=full_na[:-1]
													#sq_tech_name=sq_tech_name+str(i.name)+','
													#sq_tech_name1=sq_tech_name[:-1]
												# print "sqqqqqqqqqqqqsssssssssqqqqqqquuuuuuuuuuu",full_na1


							

							
						assigned_tech=jjob.assigned_technician.id
						if assigned_tech:
							for na in self.pool.get('hr.employee').browse(cr,uid,[assigned_tech]):
								f_name = na.name if na.name else ''
								s_name = na.middle_name if na.middle_name else ''
								l_name = na.last_name if na.last_name else ''
								temp_name = [f_name,s_name,l_name]
								full_name = ' '.join(filter(bool,temp_name))
								# print "nananananananann",full_name
						complaint_id=self.pool.get('ccc.branch.new').search(cr,uid,[('partner_id','=',name),('request_id','=',complain_request_id)])
						if complaint_id:#'cap_closure1':full_name if full_name else jjob.assigned_squad.squad_name,
							self.pool.get('ccc.branch.new').write(cr,uid,complaint_id,{'service_date':var1.job_end_date,'state':'closed','resolution':'Service Rendered','pest_name_report':chem_total1,'previous_treatment_area':treatment_name_total1,'last_comp_date':job_completion_date1 if job_completion_date1 else False,'last_tech_name':pre_full_name if pre_full_name else full_na1})
						crm_lead_srh = self.pool.get('crm.lead').search(cr,uid,[('inquiry_no','=',complain_request_id)])
						if crm_lead_srh:
							self.pool.get('crm.lead').write(cr,uid,crm_lead_srh[0],{'state':'closed'})
						'''if not conn_flag:
							complaint_id_srh = [('request_id','=',complain_request_id)]
							complaint_ids = sock.execute(dbname, userid, pwd,'ccc.customer.request','search',complaint_id_srh)
							if complaint_ids:#'cap_closure1':assigned_tech if assigned_tech else jjob.assigned_squad.squad_name,
								complaint_val = {'state':'closed','resolution':'Service Rendered','service_date':str(job_completion_date)}
								complaint_write = sock.execute(dbname, userid, pwd,'ccc.customer.request','write',complaint_ids[0] ,complaint_val)
								crm_lead_srh = [('inquiry_no','=',complain_request_id)]
								crm_id = sock.execute(dbname, userid, pwd,'crm.lead','search',crm_lead_srh)
								if crm_id:
									crm_val = {'state':'closed'}
									crm_write = sock.execute(dbname, userid, pwd,'crm.lead','write',crm_id[0] ,crm_val)'''
						#if conn_flag:
						update_query_1 = "\nupdate ccc_customer_request set write_date=(now() at time zone 'UTC'),write_uid=1,state='closed',resolution='Service Rendered','service_date'=''"+str(job_completion_date)+"'' where  request_id =''"+str(complain_request_id)+"'';"
						with open(filename,'a') as f:
							f.write(update_query_1)
							f.close()
						update_query_2 = "\nupdate crm_lead set write_date=(now() at time zone 'UTC'),write_uid=1,state = 'closed' where inquiry_no =''"+str(complain_request_id)+"'';"
						with open(filename,'a') as f:
							f.write(update_query_2)
							f.close()

#----------------ccc ops integration end-----------------------------------------------------------------------------------------
					pms = jjob.pms_search.id
					pms1=jjob.pms
					search_product = self.pool.get('product.product').search(cr,uid,[('id','=',pms)])
					job_date=jjob.job_start_date
					cust_name=var.cust_name.id
					service_location_area=var.service_location_area
					wizard = self.pool.get('consumption.report.detail').search(cr,uid,[('consumption_report_id','=',var.id)])
					if wizard:
						for var1 in self.pool.get('consumption.report.detail').browse(cr,uid,wizard):
								job_id = var1.job_id
								attached_completion_slip1=var1.attached_completion_slip
								final_job_duration = var1.job_duration

								job_end_date_new_change=var1.job_end_date
								job_end_date_new_change1=datetime.strptime(job_end_date_new_change, "%Y-%m-%d %H:%M:%S").date()

								if contract_no:
									search_job1 = self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',contract_no)])
									# print ")))))))))))))))))))))))))))))))))))))))",search_job1
								
									if search_job1:
											for search_job in self.pool.get('sale.contract').browse(cr,uid,search_job1):
													search_inspection = self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',search_job.id)])
													if search_inspection:
														for search_job_new in self.pool.get('inspection.costing.line').browse(cr,uid,search_inspection):
															if search_job_new.pms.prod_type != 'ipm':
																if search_job_new.pms.id == search_product[0]:
																	inspect_id=search_job_new.id
																	man_cost=overtime_cost=man_total_cost=0.0
																	if search_job_new.address_new.partner_address.id == jjob.location_id2:
																		if var1.chemical_consumed_one2many:
																			for chem_det in var1.chemical_consumed_one2many:
																				ch_name=chem_det.chemical_name.id
																				uom=chem_det.uom.name
																				quantity=chem_det.quantity
																				srch_chem=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',chem_det.chemical_name.id),('batch_no','=',chem_det.batch_id.batch_no)])
																			 	for price_id in self.pool.get('res.batchnumber').browse(cr,uid,srch_chem):
																					actual_value=float((price_id.local_price)*quantity)
																					# print 'LOCAL PRICE',actual_value
																				self.pool.get('material.consumed').create(cr,uid,{
																													'job_id':job_id1 if job_id1 else '',							
																													'job_date':job_date if job_date else False,								
																													'name':ch_name if ch_name else False,						
																													'uom':uom if uom else False,						
																													'chemical_consumed':quantity if quantity else 0,
																													'material_consumed_id':search_job_new.id, 

																													'price':actual_value if price_id.local_price else '',
		})
																		if var1.operational_expense_new_line:
																			for job_ex in var1.operational_expense_new_line:
																				expense_type=job_ex.expense_type
																				expense_quantity=job_ex.expense_quantity
																				expense_amt=job_ex.expense_amt
																				expense_remarks=job_ex.expense_remarks
																				self.pool.get('expense.incurred').create(cr,uid,{
																													'expense_incurred_id':search_job_new.id,
																													'expense_type':expense_type if expense_type else '',
																													'expense_quantity':expense_quantity if expense_quantity else '',		
																													'expense_amt':expense_amt if expense_amt else '',									
																													'job_id':job_id1 if job_id1 else '',													
																													'job_date':job_date if job_date else False})
																		if var1.manpower_one2many:
																			man_cost=overtime_cost=man_total_cost=0.0
																			for job_manpower in var1.manpower_one2many:
																				empl=job_manpower.empl.id
																				e_code=job_manpower.empl.emp_code
																				no_of_manpower=job_manpower.no_of_manpower
																				manpower_cost=manpower_obj.manpower_cost(cr,uid,emp_code=str(e_code), context=context)
																				# print "manpower_cost1212",manpower_cost
																				designation=manpower_obj.manpower_designation(cr,uid,emp_code=str(e_code), context=context)#job_manpower.designation
																				overtime_cost =manpower_obj.manpower_cost(cr,uid,emp_code=str(e_code),ttype='overtime', context=context)#job_manpower.designation
																				designation1=job_manpower.designation1
																				no_of_hours=job_manpower.no_of_hours
																				no_of_over_time_hours=job_manpower.no_of_over_time_hours
																				# print "emppppppppppppp_codeeeeeeeee",manpower_cost,designation
																				#print aaa
																				name=job_manpower.name
																				man_cost=man_cost+manpower_cost*no_of_hours
																				overtime_cost=overtime_cost + (2*manpower_cost)*no_of_over_time_hours

																				# print "dcdcdcdcdcdcdcdcdcdcdc",overtime_cost
																				man_total_cost=man_cost+overtime_cost
																				a=self.pool.get('manpower.utilization').create(cr,uid,{'job_id':job_id1 if job_id1 else '',
																												'job_date':job_date if job_date else False,
																												'designation':designation if designation else '',
																												'emp_code':job_manpower.empl.emp_code if job_manpower.empl else False,
																												'designation1':designation1 if designation1 else '',
																												'empl':empl if empl else False,
																												'manpower_cost':manpower_cost if manpower_cost else 0,
																												'overtime_cost':job_manpower.overtime_cost if job_manpower.overtime_cost else 0,
																												'no_of_hours':no_of_hours if no_of_hours else 0.0,'no_of_manpower':no_of_manpower if no_of_manpower else 0,'manpower_utilization_id':search_job_new.id, 'no_of_overtime_hours':no_of_over_time_hours})
																				# print "dddddddddddddddddddddddrererer",a

															else:
																for iterate_val in search_job_new.ipm_one2many:
																	# print "****************************",iterate_val.pms.id,search_product[0],iterate_val.ipm_id.address_new.partner_address.id,jjob.location_id2
																	if iterate_val.pms.id == search_product[0]:
																		inspect_id=iterate_val.id
																		man_cost=overtime_cost=man_total_cost=0.0
																		if iterate_val.ipm_id.address_new.partner_address.id == jjob.location_id2:
																			if var1.chemical_consumed_one2many:
																				for chem_det in var1.chemical_consumed_one2many:
																					ch_name=chem_det.chemical_name.id
																					uom=chem_det.uom.name
																					quantity=chem_det.quantity
																					srch_chem=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',chem_det.chemical_name.id),('batch_no','=',chem_det.batch_id.batch_no)])
																				 	for price_id in self.pool.get('res.batchnumber').browse(cr,uid,srch_chem):
																						actual_value=float((price_id.local_price)*quantity)
																						# print 'LOCAL PRICE',actual_value
																					self.pool.get('material.consumed').create(cr,uid,{
																														'job_id':job_id1 if job_id1 else '',							
																														'job_date':job_date if job_date else False,								
																														'name':ch_name if ch_name else False,						
																														'uom':uom if uom else False,						
																														'chemical_consumed':quantity if quantity else 0,
																														'material_consumed_id':iterate_val.id, 

																														'price':actual_value if price_id.local_price else '',
			})
																			if var1.operational_expense_new_line:
																				for job_ex in var1.operational_expense_new_line:
																					expense_type=job_ex.expense_type
																					expense_quantity=job_ex.expense_quantity
																					expense_amt=job_ex.expense_amt
																					expense_remarks=job_ex.expense_remarks
																					self.pool.get('expense.incurred').create(cr,uid,{
																														'expense_incurred_id':iterate_val.id,
																														'expense_type':expense_type if expense_type else '',
																														'expense_quantity':expense_quantity if expense_quantity else '',		
																														'expense_amt':expense_amt if expense_amt else '',									
																														'job_id':job_id1 if job_id1 else '',													
																														'job_date':job_date if job_date else False})
																			if var1.manpower_one2many:
																				man_cost=overtime_cost=man_total_cost=0.0
																				for job_manpower in var1.manpower_one2many:

																					empl=job_manpower.empl.id
																					e_code=job_manpower.empl.emp_code
																					no_of_manpower=job_manpower.no_of_manpower
																					manpower_cost=manpower_obj.manpower_cost(cr,uid,emp_code=str(e_code), context=context)
																					designation=manpower_obj.manpower_designation(cr,uid,emp_code=str(e_code), context=context)#job_manpower.designation
																					designation1=job_manpower.designation1
																					no_of_hours=job_manpower.no_of_hours
																					no_of_over_time_hours=job_manpower.no_of_over_time_hours
																					# print "emppppppppppppp_codeeeeeeeee",manpower_cost,designation
																					#print aaa
																					name=job_manpower.name
																					man_cost=man_cost+manpower_cost*no_of_hours
																					overtime_cost=overtime_cost + (2*manpower_cost)*no_of_over_time_hours
																					man_total_cost=man_cost+overtime_cost
																					a=self.pool.get('manpower.utilization').create(cr,uid,{'job_id':job_id1 if job_id1 else '',
																													'job_date':job_date if job_date else False,
																													'designation':designation if designation else '',
																													'emp_code':job_manpower.empl.emp_code if job_manpower.empl else False,
																													'designation1':designation1 if designation1 else '',
																													'empl':empl if empl else False,
																													'manpower_cost':manpower_cost if manpower_cost else 0,
																													'no_of_hours':no_of_hours if no_of_hours else 0.0,'no_of_manpower':no_of_manpower if no_of_manpower else 0,'manpower_utilization_id':iterate_val.id, 'no_of_overtime_hours':no_of_over_time_hours})
																					# print "dddddddddddddddddddddddrererer",a

			#-------------------------------------------start sync of chemical consumed,expense,manpower in sales---------------
															if search_job_new.pms.prod_type != 'ipm':
																'''if not conn_flag:
																	product_srh = [('name','=',pms1)]
																	product_id = sock.execute(dbname, userid, pwd,'product.product','search',product_srh)
																	if product_id:
																		contract_srh = [('contract_number','=',contract_no)]
																		contract_id = sock.execute(dbname, userid, pwd,'sale.contract','search',contract_srh)
																		if not contract_id:
																			conn_flag=True
																		if contract_id:
																			inspectn_srh = [('contract_id1','=',contract_id),('pms','=',product_id)]
																			inspectn_id = sock.execute(dbname, userid, pwd,'inspection.costing.line','search',inspectn_srh)
																			if inspectn_id:
																				if var1.manpower_one2many:
																					for job_manpower in var1.manpower_one2many:
																						designation=job_manpower.designation
																						designation1=job_manpower.designation1
																						empl=job_manpower.empl.name
																						no_of_manpower=job_manpower.no_of_manpower
																						no_of_hours=job_manpower.no_of_hours
																						no_of_over_time_hours=job_manpower.no_of_over_time_hours

																						manpower_val = {'empl':empl if empl else '',
																										'manpower_utilization_id':inspectn_id[0] if inspectn_id else False,
																										'designation':designation if designation else '',
																										'designation1':designation1 if designation1 else '',
																										'job_id':job_id1 if job_id1 else '',
																										'job_date':job_date if job_date else False,
																										'no_of_manpower':no_of_manpower if no_of_manpower else '',	
																										'no_of_hours':no_of_hours if no_of_hours else '',
																										'no_of_overtime_hours':no_of_over_time_hours if no_of_over_time_hours else ''}
																						manpower_create = sock.execute(dbname, userid, pwd,'manpower.utilization','create',manpower_val)
																				if var1.operational_expense_new_line:
																					for expense_table in var1.operational_expense_new_line:
																						expensetype=expense_table.expense_type
																						expensequantity=expense_table.expense_quantity
																						expenseamount=expense_table.expense_amt
																						expense_val = {'expense_type':expensetype if expensetype else '',
																								   'expense_quantity':expensequantity if expensequantity else '',
																								   'expense_amt':expenseamount if expenseamount else 0.0, 
																								   'expense_incurred_id':inspectn_id[0] if inspectn_id else False,
																								   'job_id':job_id1 if job_id1 else '',
																								   'job_date':job_date if job_date else False}
																						expense_create = sock.execute(dbname, userid, pwd,'expense.incurred','create',expense_val)

																				if var1.chemical_consumed_one2many:
																					for chem_det in var1.chemical_consumed_one2many:
																						ch_name=chem_det.chemical_name.name
																						uom=chem_det.uom.name
																						quantity=chem_det.quantity
																						material_val = {
																						'job_id':job_id1 if job_id1 else '',							
																						'job_date':job_date if job_date else False,								
																						'name':ch_name if ch_name else '',						
																						'uom':uom if uom else False,						
																						'chemical_consumed':quantity if quantity else 0,
																						'material_consumed_id':inspectn_id[0] if inspectn_id else False }
																						expense_create = sock.execute(dbname, userid, pwd,'material.consumed','create',material_val)'''
																#if conn_flag:
																
																if var1.manpower_one2many:
																	for job_manpower in var1.manpower_one2many:
																		designation=job_manpower.designation
																		designation1=job_manpower.designation1
																		empl=job_manpower.empl.name
																		no_of_manpower=job_manpower.no_of_manpower
																		no_of_hours=job_manpower.no_of_hours
																		no_of_over_time_hours=job_manpower.no_of_over_time_hours

																		insert_query1 = "\ninsert into manpower_utilization (create_date,create_uid,empl, manpower_utilization_id,designation, job_id, job_date, no_of_manpower, no_of_hours ,no_of_overtime_hours) values ((now() at time zone 'UTC'),1,'"+str(empl)+"',(select * from get_many2oneid('inspection_costing_line where contract_id1 in (select id from sale_contract where contract_number =''"+str(contract_no)+"'')and pms =(select id from product_product where name_template =''"+str(pms1)+"'')')),'"+str(designation)+"','"+str(job_id1)+"','"+str(job_date)+"',"+str(no_of_manpower)+","+str(no_of_hours)+","+str(no_of_over_time_hours)+");"
																		# print "a00000000000000000000000000000",insert_query1
																		with open(filename,'a') as f:
																			f.write(insert_query1)
																			f.close()


																if var1.operational_expense_new_line:
																	for expense_table in var1.operational_expense_new_line:
																		expensetype=expense_table.expense_type
																		expensequantity=expense_table.expense_quantity
																		expenseamount=expense_table.expense_amt

																		insert_query2="\ninsert into expense_incurred (create_date,create_uid,expense_type,expense_quantity,expense_amt,expense_incurred_id,job_id,job_date) values ((now() at time zone 'UTC'),1,'"+str(expensetype)+"','"+str(expensequantity)+"','"+str(expenseamount)+"',(select * from get_many2oneid('inspection_costing_line where contract_id1 in (select id from sale_contract where contract_number =''"+str(contract_no)+"'')and pms =(select id from product_product where name_template =''"+str(pms1)+"'')')),'"+str(job_id1)+"','"+str(job_date)+"');"
																		# print "))))))))))))))))))))))))))))))))))",insert_query2
																		with open(filename,'a') as f:
																			f.write(insert_query2)
																			f.close()


																if var1.chemical_consumed_one2many:
																	for chem_det in var1.chemical_consumed_one2many:
																		ch_name=chem_det.chemical_name.name
																		# print "_______________________",ch_name
																		uom=chem_det.uom.name
																		quantity=chem_det.quantity

																		insert_query3 = "\ninsert into material_consumed (create_date,create_uid,job_id,job_date,name,uom,chemical_consumed,material_consumed_id) values ((now() at time zone 'UTC'),1,'"+str(job_id1)+"','"+str(job_date)+"','"+str(ch_name)+"','"+str(uom)+"','"+str(quantity)+"',(select * from get_many2oneid('inspection_costing_line where contract_id1 in (select id from sale_contract where contract_number =''"+str(contract_no)+"'')and pms =(select id from product_product where name_template =''"+str(pms1)+"'')')));"
																		# print ")))))))))))))))))))",insert_query3
																		with open(filename,'a') as f:
																			f.write(insert_query3)
																			f.close()

															else:
																'''if not conn_flag:
																	product_srh = [('name','=',pms1)]
																	product_id = sock.execute(dbname, userid, pwd,'product.product','search',product_srh)
																	if product_id:
																		contract_srh = [('contract_number','=',contract_no)]
																		contract_id = sock.execute(dbname, userid, pwd,'sale.contract','search',contract_srh)
																		if not contract_id:
																			conn_flag = True
																		if contract_id:
																					inspectn_srh = [('contract_id1','=',contract_id)]#,('pms','=',product_id)
																					inspectn_id = sock.execute(dbname, userid, pwd,'inspection.costing.line','search',inspectn_srh)
																					if inspectn_id:
																						inspectn_srh1 = [('ipm_id','=',inspectn_id[0]),('pms','=',product_id[0])]#,('pms','=',product_id)
																						inspectn_id1 = sock.execute(dbname, userid, pwd,'inspection.costing.line','search',inspectn_srh1)
																						if inspectn_id1:
																							if var1.manpower_one2many:
																								for job_manpower in var1.manpower_one2many:
																									designation=job_manpower.designation
																									designation1=job_manpower.designation1
																									empl=job_manpower.empl.name
																									no_of_manpower=job_manpower.no_of_manpower
																									no_of_hours=job_manpower.no_of_hours
																									no_of_over_time_hours=job_manpower.no_of_over_time_hours

																									manpower_val = {'empl':empl if empl else '',
																													'manpower_utilization_id':inspectn_id1[0] if inspectn_id1 else False,
																													'designation':designation if designation else '',
																													'designation1':designation1 if designation1 else '',
																													'job_id':job_id1 if job_id1 else '',
																													'job_date':job_date if job_date else False,
																													'no_of_manpower':no_of_manpower if no_of_manpower else '',	
																													'no_of_hours':no_of_hours if no_of_hours else '',
																													'no_of_overtime_hours':no_of_over_time_hours if no_of_over_time_hours else ''}
																									manpower_create = sock.execute(dbname, userid, pwd,'manpower.utilization','create',manpower_val)
																							if var1.operational_expense_new_line:
																								for expense_table in var1.operational_expense_new_line:
																									expensetype=expense_table.expense_type
																									expensequantity=expense_table.expense_quantity
																									expenseamount=expense_table.expense_amt
																									expense_val = {'expense_type':expensetype if expensetype else '',
																											   'expense_quantity':expensequantity if expensequantity else '',
																											   'expense_amt':expenseamount if expenseamount else 0.0, 
																											   'expense_incurred_id':inspectn_id1[0] if inspectn_id1 else False,
																											   'job_id':job_id1 if job_id1 else '',
																											   'job_date':job_date if job_date else False}
																									expense_create = sock.execute(dbname, userid, pwd,'expense.incurred','create',expense_val)

																							if var1.chemical_consumed_one2many:
																								for chem_det in var1.chemical_consumed_one2many:
																									ch_name=chem_det.chemical_name.name
																									uom=chem_det.uom.name
																									quantity=chem_det.quantity
																									material_val = {
																									'job_id':job_id1 if job_id1 else '',							
																									'job_date':job_date if job_date else False,								
																									'name':ch_name if ch_name else '',						
																									'uom':uom if uom else False,						
																									'chemical_consumed':quantity if quantity else 0,
																									'material_consumed_id':inspectn_id1[0] if inspectn_id1 else False }
																									expense_create = sock.execute(dbname, userid, pwd,'material.consumed','create',material_val)'''
																#if conn_flag:
																
																# print "ipm offline code"
																if var1.manpower_one2many:
																	for job_manpower in var1.manpower_one2many:
																		designation=job_manpower.designation
																		designation1=job_manpower.designation1
																		empl=job_manpower.empl.name
																		no_of_manpower=job_manpower.no_of_manpower
																		no_of_hours=job_manpower.no_of_hours
																		no_of_over_time_hours=job_manpower.no_of_over_time_hours

																		insert_query1 = "\ninsert into manpower_utilization (create_date,create_uid,empl, manpower_utilization_id,designation, job_id, job_date, no_of_manpower, no_of_hours ,no_of_overtime_hours) values ((now() at time zone 'UTC'),1,'"+str(empl)+"',(select id from inspection_costing_line where ipm_id = (select id from inspection_costing_line  where contract_id1 = (select * from get_many2oneid('sale_contract where contract_number = ''"+str(contract_no)+"'' '))) and pms = (select * from get_many2oneid('product_product where name_template=''"+str(pms1)+"''  '))),'"+str(designation)+"','"+str(job_id1)+"','"+str(job_date)+"',"+str(no_of_manpower)+","+str(no_of_hours)+","+str(no_of_over_time_hours)+");"
																		with open(filename,'a') as f:
																			f.write(insert_query1)
																			f.close()


																if var1.operational_expense_new_line:
																	for expense_table in var1.operational_expense_new_line:
																		expensetype=expense_table.expense_type
																		expensequantity=expense_table.expense_quantity
																		expenseamount=expense_table.expense_amt

																		insert_query2="\ninsert into expense_incurred (create_date,create_uid,expense_type,expense_quantity,expense_amt,expense_incurred_id,job_id,job_date) values ((now() at time zone 'UTC'),1,'"+str(expensetype)+"','"+str(expensequantity)+"','"+str(expenseamount)+"',(select id from inspection_costing_line where ipm_id = (select id from inspection_costing_line  where contract_id1 = (select * from get_many2oneid('sale_contract where contract_number = ''"+str(contract_no)+"'' '))) and pms = (select * from get_many2oneid('product_product where name_template=''"+str(pms1)+"''  '))),'"+str(job_id1)+"','"+str(job_date)+"');"
																		with open(filename,'a') as f:
																			f.write(insert_query2)
																			f.close()


																if var1.chemical_consumed_one2many:
																	for chem_det in var1.chemical_consumed_one2many:
																		ch_name=chem_det.chemical_name.name
																		uom=chem_det.uom.name
																		quantity=chem_det.quantity

																		insert_query3 = "\ninsert into material_consumed (create_date,create_uid,job_id,job_date,name,uom,chemical_consumed,material_consumed_id) values ((now() at time zone 'UTC'),1,'"+str(job_id1)+"','"+str(job_date)+"','"+str(ch_name)+"','"+str(uom)+"','"+str(quantity)+"',(select id from inspection_costing_line where ipm_id = (select id from inspection_costing_line  where contract_id1 = (select * from get_many2oneid('sale_contract where contract_number = ''"+str(contract_no)+"'' '))) and pms = (select * from get_many2oneid('product_product where name_template=''"+str(pms1)+"''  '))));"
																		with open(filename,'a') as f:
																			f.write(insert_query3)
																			f.close()
																																	
#-------------------------------------------end sync of chemical consumed,expense,manpower in sales---------------
								self.pool.get('consumption.report.detail').write(cr,uid,var1.id,{'state':'final'})
								job_srh1 = self.pool.get('res.scheduledjobs').search(cr,uid,[('scheduled_job_id','=',job_id),('state','not in',('unscheduled','cancel'))])

								for job in self.pool.get('res.scheduledjobs').browse(cr,uid,job_srh1):
													dt=job.job_total_days
													job_completion_date1=str(datetime.now().date())
													start_date=datetime.strptime(dt,"%Y-%m-%d")
													end_date=datetime.strptime(job_completion_date1, "%Y-%m-%d")
													if end_date >= start_date:
														dta= (end_date - start_date).days
													if dta == 0:
														dta=dta+1
														cr.execute(("update res_scheduledjobs set job_age=%s where id =%s"),(dta,job.id))
														cr.commit()
													else:
														dta=dta+1
														cr.execute(("update res_scheduledjobs set job_age=%s where id =%s"),(dta,job.id))
														cr.commit()
													res_tmp_id.extend([job.id])
													#self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'state':'job_done','job_completion_date':str(datetime.now())})		
													if job.assigned_technician :
														assign = job.assigned_technician.concate_name
													if job.assigned_squad :
														assign = job.assigned_squad.squad_name
													
													if job.erp_order_no:
														product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',job.erp_order_no)])
														invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',job.delivery_challan_no)])
														if invoice_id:
															self.pool.get('job.history').create(cr,uid,{'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),
										'job_status':'Job Completed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job_end_date_new_change,'record_date':current_date,'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
														else:
															self.pool.get('job.history').create(cr,uid,{'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),
										'job_status':'Job Completed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job_end_date_new_change,'record_date':current_date,'product_order_id':product_order_id[0]})

													if job.service_order_no:
														service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',job.service_order_no)])
														invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',job.service_order_no)])
														if invoice_id:
															self.pool.get('job.history').create(cr,uid,{'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),
										'job_status':'Job Completed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job_end_date_new_change,'record_date':current_date,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
														else:
															self.pool.get('job.history').create(cr,uid,{'job_id':job.scheduled_job_id,'job_schedule_date':job.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),
										'job_status':'Job Completed','history_id':job.id,'job_start_date':job.job_start_time,'job_end_date':job_end_date_new_change,'record_date':current_date,'service_order_id':service_order_id[0]})

													########### Update Status after job done ##########
													stock_transfer_obj = self.pool.get('stock.transfer')
													sale_order_obj = self.pool.get('psd.sales.product.order')
													delivery_scheduled_obj = self.pool.get('psd.sales.delivery.schedule')
													product_transfer_obj = self.pool.get('product.transfer')
													if job.delivery_challan_no:
														delivery_search_id = stock_transfer_obj.search(cr,uid,[('delivery_challan_no','=',job.delivery_challan_no)])
														stock_transfer_obj.write(cr,uid,delivery_search_id,{'state':'delivered'})
														delivery_schedule_id =delivery_scheduled_obj.search(cr,uid,[('delivery_challan_no','=',job.delivery_challan_no)])
														delivery_scheduled_obj.write(cr,uid,delivery_schedule_id,{'state':'delivered'}),
														sale_order_id = sale_order_obj.search(cr,uid,[('erp_order_no','=',job.erp_order_no)])
														sale_order_obj=sale_order_obj.browse(cr,uid,sale_order_id[0])
														search_product_ids = product_transfer_obj.search(cr,uid,[('prod_id','=',delivery_search_id)])
														for prod_line in product_transfer_obj.browse(cr,uid,search_product_ids):
															product_transfer_obj.write(cr,uid,prod_line.id,{'state':'done'})
														sale_line_length = []
														equal_qty=[]
														for sale_line in sale_order_obj.psd_sales_product_order_lines_ids:
															sale_line_length.append(1)
															if sale_line.allocated_quantity == sale_line.ordered_quantity:
																equal_qty.append(1)
														if len(sale_line_length) == len(equal_qty):
															self.pool.get('psd.sales.product.order').write(cr,uid,sale_order_id[0],{'state':'delivered'})
													################################################
													self.pool.get('res.scheduledjobs').write(cr,uid,job.id,{'customer_job_id':job_id1,'cust_name':cust_name,'job_duration_in_time':final_job_duration,'service_location_area':service_location_area,'job_closed_date':job_closed_date1,'new_job_end_time1':job_end_date_new_change,'job_end_date':job_end_date_new_change1,'attached_completion_slip':attached_completion_slip1,'state':'job_done','job_completion_date':str(datetime.now())})
													if var1.res_comment_line:
														for k in var1.res_comment_line:
															comment_date=k.comment_date
															comment=k.comment
															sequence=k.sequence
															user_name=self.pool.get('res.users').browse(cr, uid, uid).id
															# print "*********************",user_name
															search = self.pool.get('comment.line').search(cr,uid,[('operation_notes','=',job.id),('sequence','=',sequence),])
															if not search:
																self.pool.get('comment.line').write(cr,uid,k.id,{'comment_date':comment_date,'comment':comment,'operation_notes':job.id,'user_id':user_name})	
															#self.pool.get('operations.comment.line').write(cr,uid,k.id,{'comment_date':comment_date,'comment':comment,'indent_id':job.id,'user_id':user_name})
													#---------------Manpower Requirement updation from sale to job closure-------------------------start-----------------------------
													contract_num=job.job_id
													pms = job.pms_search.id
													search_product = self.pool.get('product.product').search(cr,uid,[('id','=',pms)])
													if search_product:
														search_job = self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',contract_num)])
														if search_job:
																search_inspection = self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',search_job[0]),])
																if search_inspection:
																	for man_req in self.pool.get('inspection.costing.line').browse(cr,uid,search_inspection):
																		if man_req.pms.prod_type != 'ipm':
																			if man_req.pms.id == search_product[0]:
																				if man_req.address_new.partner_address.id == job.location_id2:
																					if man_req.manpower_line:
																						for mp_det in man_req.manpower_line:
																							#designation=mp_det.designation
																							desig_value = self.pool.get('hr.manpower.cost').search(cr,uid,[('key','=',mp_det.designation)])
																							for desig_srch in self.pool.get('hr.manpower.cost').browse(cr,uid,desig_value):
																								designation = desig_srch.value
																							no_of_manpower=mp_det.no_of_manpower
																							no_of_hours=mp_det.no_of_hours
																							no_of_over_time_hours=mp_det.no_of_over_time_hours
																							self.pool.get('new.man.power.line').create(cr,uid,{
																									'designation':designation if designation else '',
																									'manpower_job_many2one_id':job.id,
																									'no_of_manpower':no_of_manpower if no_of_manpower else '',
																									'no_of_hours':no_of_hours if no_of_hours else '',
																									'no_of_over_time_hours':no_of_over_time_hours if no_of_over_time_hours else ''})
																																		
																		else:
																			for iterate_val in man_req.ipm_one2many:
																				if iterate_val.pms.id == search_product[0]:
																					if iterate_val.ipm_id.address_new.partner_address.id == job.location_id2:
																						if iterate_val.manpower_line:
																							for mp_det in iterate_val.manpower_line:
																								#designation=mp_det.designation
																								desig_value = self.pool.get('hr.manpower.cost').search(cr,uid,[('key','=',mp_det.designation)])
																								for desig_srch in self.pool.get('hr.manpower.cost').browse(cr,uid,desig_value):
																									designation = desig_srch.value
																									no_of_manpower=mp_det.no_of_manpower
																									no_of_hours=mp_det.no_of_hours
																									no_of_over_time_hours=mp_det.no_of_over_time_hours
																									self.pool.get('new.man.power.line').create(cr,uid,{
																											'designation':designation if designation else '',
																											'manpower_job_many2one_id':job.id,
																											'no_of_manpower':no_of_manpower if no_of_manpower else '',
																											'no_of_hours':no_of_hours if no_of_hours else '',
																											'no_of_over_time_hours':no_of_over_time_hours if no_of_over_time_hours else ''})
																			
#------------------------------Manpower Requirement updation from sale to job closure-------------------------end--------------
													if var1.estimated_chem_one2many:
														for chem1 in var1.estimated_chem_one2many:
															self.pool.get('estimated.chemical.equipment').create(cr,uid,{'chemical_name':chem1.chemical_name.id,'quantity':chem1.quantity,'estimated_equip_line':job.id,'uom':chem1.uom.id})
													if var1.chemical_consumed_one2many:
														for i in var1.chemical_consumed_one2many:
															self.pool.get('chemical.consumed').create(cr,uid,{'chemical_name':i.chemical_name.id,'quantity':i.quantity,'estimate_actual':job.id,'uom':i.uom.id,'batch_id':i.batch_id.id})
													'''if job.manpower_line:
														for total_hr in job.manpower_line:
															dta=total_hr.no_of_hours
															cr.execute(("update res_scheduledjobs set job_age=%s where id =%s"),(dta,job.id))'''
													if var1.treatment_one2many:
														for treat in var1.treatment_one2many:
															treatment_name=treat.treatment_name
															observations=treat.observations
															area_sq_foot=treat.area_sq_foot
															self.pool.get('treatment.area').create(cr,uid,{'treatment_area_line_est':job.id,'treatment_name':treatment_name,'observations':observations,'area_sq_foot':area_sq_foot})
													if var1.operational_expense_new_line:
														for exp_inc in var1.operational_expense_new_line:
															expense_type=exp_inc.expense_type
															expense_quantity=exp_inc.expense_quantity
															expense_amt=exp_inc.expense_amt
															expense_remarks=exp_inc.expense_remarks

															self.pool.get('operational.expense').create(cr,uid,{'expense_type_line_est':job.id,'expense_type':expense_type,'expense_quantity':expense_quantity,'expense_amt':expense_amt,
												'expense_remarks':expense_remarks})

													if var1.manpower_one2many:
																for mp in var1.manpower_one2many:
																			empl=mp.empl.id
																			designation=mp.designation
																			designation1=mp.designation1
																			no_of_hours=mp.no_of_hours
																			no_of_manpower=mp.no_of_manpower
																			no_of_over_time_hours=mp.no_of_over_time_hours
																			no_hr_waste=mp.no_hr_waste
																			self.pool.get('manpower.estimate').create(cr,uid,{'manpower_job_estimate_line':job.id,'designation':designation,'designation1':designation1,'no_of_manpower':no_of_manpower,'empl':empl,'no_of_hours':no_of_hours,'no_hr_waste':no_hr_waste,'no_of_over_time_hours':no_of_over_time_hours,
'no_of_over_time_hours':no_of_over_time_hours})


													'''wiz_job = self.pool.get('res.scheduled.completion.wizard').create(cr,uid,{'job_closed_date':datetime.now().date(),'scheduledjobs_id':job.id,'form_id':job.id,'attached_completion_slip':var1.attached_completion_slip})
													job_wizard_srh = self.pool.get('res.scheduled.completion.wizard').search(cr,uid,[('scheduledjobs_id','=',job.id),('form_id','=',job.id)])
												
													if job_wizard_srh:
														for wiz in self.pool.get('res.scheduled.completion.wizard').browse(cr,uid,job_wizard_srh):
															if var1.chemical_consumed_one2many:
																for chem in var1.chemical_consumed_one2many:
																			if chem.chemical_name.type_product == 'chemical':
																				self.pool.get('res.product').create(cr,uid,{'name':chem.chemical_name.id,'quantityavailable':chem.quantity,'batch_no':chem.batch_id.id,'chemical_id_wiz':wiz.id,'uom':chem.uom.name})
																			if chem.chemical_name.type_product != 'chemical':
																				self.pool.get('res.equipment').create(cr,uid,{'name_equipment':chem.chemical_name.id,'quantityavailable_equipment':chem.quantity,'uom_equipment':chem.uom.name,
															'chemical_id_equipment_wiz':wiz.id,'serial_no':chem.tag_id.id if chem.tag_id else False,'batch_no':chem.batch_id.id if chem.batch_id else False})
															if var1.treatment_one2many:
																for treat in var1.treatment_one2many:
																			treatment_name=treat.treatment_name
																			observations=treat.observations
																			area_sq_foot=treat.area_sq_foot
																			self.pool.get('treatment.area').create(cr,uid,{'treatment_area_line_wiz':wiz.id,'treatment_name':treatment_name,'observations':observations,'area_sq_foot':area_sq_foot})
															if var1.operational_expense_new_line:
																for exp_inc in var1.operational_expense_new_line:
																			expense_type=exp_inc.expense_type
																			expense_quantity=exp_inc.expense_quantity
																			expense_amt=exp_inc.expense_amt
																			expense_remarks=exp_inc.expense_remarks

																			self.pool.get('operational.expense').create(cr,uid,{'expense_type_line_wiz':wiz.id,'expense_type':expense_type,'expense_quantity':expense_quantity,'expense_amt':expense_amt,
											'expense_remarks':expense_remarks})
															if var1.manpower_one2many:
																for mp in var1.manpower_one2many:
																			empl=mp.empl.id
																			designation=mp.designation
																			designation1=mp.designation1
																			no_of_hours=mp.no_of_hours
																			no_of_manpower=mp.no_of_manpower
																			no_of_over_time_hours=mp.no_of_over_time_hours
																			no_hr_waste=mp.no_hr_waste
																			self.pool.get('manpower.estimate').create(cr,uid,{'manpower_job_estimate_line':job.id,'designation':designation,'designation1':designation1,'no_of_manpower':no_of_manpower,'empl':empl,'no_of_hours':no_of_hours,'no_hr_waste':no_hr_waste,'no_of_over_time_hours':no_of_over_time_hours,
'no_of_over_time_hours':no_of_over_time_hours})'''

						
													'''no_of_hours_wasted=job.hours
													job_id=job.scheduled_job_id
													job_date=job.req_date_time
													assigned_technician=job.assigned_technician.id
													contract_no=job.job_id
													sale_contract_id=job.sale_contract.id
													pms=job.pms
													inspection_id=''
													search_id1 = self.pool.get('product.product').search(cr,uid,[('name','=',pms)])
													for varp in self.pool.get('product.product').browse(cr,uid,search_id1):
														pms1 = varp.id
														contract_number_search=self.pool.get('sale.contract').search(cr,uid,[('contract_number','=',contract_no)])
														for sale_contr in self.pool.get('sale.contract').browse(cr,uid,contract_number_search):
															salecontract_id=sale_contr.id
															inspection_id=self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',salecontract_id),('pms','=',pms1)])
															if inspection_id:
																for inspect_id in self.pool.get('inspection.costing.line').browse(cr,uid,inspection_id):
																	inspec_line_id=inspect_id.id
																	#self.pool.get('manpower.utilization').create(cr,uid,{'empl':job.assigned_technician.id,'no_hrs_wasted':no_of_hours_wasted,'manpower_utilization_id':inspec_line_id,
							#'job_id':job_id,'job_date':job_date})
													if job.expense_line:
														for expens in job.expense_line:
															expense_type=expens.expense_type
															expense_quantity=expens.expense_quantity
															expense_amt=expens.expense_amt
															expense_remarks=expens.expense_remarks
															self.pool.get('expense.incurred').create(cr,uid,{'expense_incurred_id':inspec_line_id,'job_id':job_id,'job_date':job_date,'expense_type':expense_type,'expense_quantity':expense_quantity,'expense_amt':expense_amt,
									'expense_remarks':expense_remarks})
					#----------------------------------------------------end-------------------------------------------------------------------------------
					#----- sync of no of hours wasted and expense at the time of reschedule(start)---------------------------------------------------------

															no_of_hours_wasted=job.hours
															job_id=job.scheduled_job_id
															job_date=job.req_date_time
															assigned_technician=job.assigned_technician.name
															#contract_no=job.job_id
															sale_contract_id=job.sale_contract.id
															contract_no = job.sale_contract.contract_number
															pms=job.pms
															if not conn_flag:
																product_srh = [('name','=',pms)]
																product_id = sock.execute(dbname, uid, pwd,'product.product','search',product_srh)
																if product_id:
																	contract_srh = [('contract_number','=',contract_no)]
																	contract_id = sock.execute(dbname, uid, pwd,'sale.contract','search',contract_srh)
																	if contract_id:
																		inspectn_srh = [('contract_id1','=',contract_id),('pms','=',product_id)]
																		inspectn_id = sock.execute(dbname, uid, pwd,'inspection.costing.line','search',inspectn_srh)
																		if inspectn_id:
																			if job.manpower_line:
																				for manpower_line in job.manpower_line:
																					empl=manpower_line.empl.name
																					designation=manpower_line.designation

																					no_of_manpower = manpower_line.no_of_manpower
																					no_of_over_time_hours = manpower_line.no_of_over_time_hours
																					no_of_hours=manpower_line.no_of_hours	
																					manpower_val = {'empl':empl,
																										'no_hrs_wasted':no_of_hours_wasted,
																										'manpower_utilization_id':inspectn_id[0] if inspectn_id else False,
																										'designation':designation,
																										'job_id':job_id,
																										'job_date':job_date,
																										'no_of_manpower':no_of_manpower,	
																										'no_of_hours':no_of_hours,
																										'no_of_overtime_hours':no_of_over_time_hours}
																					manpower_create = sock.execute(dbname, uid, pwd,'manpower.utilization','create',manpower_val)
																			if job.expense_line:
																				for expense_table in job.expense_line:
																					expensetype=expense_table.expense_type
																					expensequantity=expense_table.expense_quantity
																					expenseamount=expense_table.expense_amt
																					expense_val = {'expense_type':expensetype,
																								   'expense_quantity':expensequantity,
																								   'expense_amt':expenseamount, 
																								   'expense_incurred_id':inspectn_id[0] if inspectn_id else False,
																								   'job_id':job_id,
																								   'job_date':job_date}
																					expense_create = sock.execute(dbname, uid, pwd,'expense.incurred','create',expense_val)
															elif conn_flag:
																if job.manpower_line:
																	for manpower_line in job.manpower_line:
																		empl=manpower_line.empl.name
																		designation=manpower_line.designation

																		no_of_manpower = manpower_line.no_of_manpower
																		no_of_over_time_hours = manpower_line.no_of_over_time_hours
																		no_of_hours=manpower_line.no_of_hours	

																		insert_query1 = "insert into manpower_utilization (empl, manpower_utilization_id,designation, job_id, job_date, no_of_manpower, no_of_hours ,no_of_overtime_hours) values ('"+str(empl)+"',(select id from inspection_costing_line where contract_id1=(select * from get_many2oneid('sale_contract where contract_number ilike ''"+str(contract_no)+"'' ')) and pms=(select * from get_many2oneid('product_product where name_template=''"+str(pms1)+"''  '))) ,'"+str(designation)+"','"+str(job_id)+"','"+str(job_date)+"',"+str(no_of_manpower)+","+str(no_of_hours)+","+str(no_of_over_time_hours)+");"
																		with open(filename,'a') as f:
																			f.write(insert_query1)
																			f.close.()
																if job.expense_line:
																	for expense_table in job.expense_line:
																		expensetype=expense_table.expense_type
																		expensequantity=expense_table.expense_quantity
																		expenseamount=expense_table.expense_amt

																		insert_query2="insert into expense_incurred (expense_type,expense_quantity,expense_amt,expense_incurred_id,job_id,job_date) values ('"+str(expensetype)+"','"+str(expensequantity)+"','"+str(expenseamount)+"',(select * from get_many2oneid('inspection_costing_line where contract_id1 in (select id from sale_contract where contract_number =''"+str(contract_no)+"'')and pms =(select id from product_product where name_template =''"+str(pms)+"'')')),'"+str(job_id1)+"','"+str(job_date)+"');"
																		with open(filename,'a') as f:
																			f.write(insert_query2)
																			f.close()'''

			
		date=datetime.now()
		seq_id1 = self.pool.get('ir.sequence').get(cr, uid,'consumption.report')
		ou_id1 = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		today_date = datetime.now().date()
		year = today_date.year
		year12=today_date.strftime('%y')
		company_id=self.pool.get('res.users').browse(cr, uid, uid).company_id.id
		for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
			job_code=comp_id.consumption_resource_id
			job_id =str(ou_id1)+job_code+year12+str(seq_id1)
		self.write(cr,uid,ids,{'state':'final','consumption_material_id':job_id,'created_date':date})
		self.pool.get('res.scheduledjobs').write(cr,uid,res_tmp_id,{'sync_bool':True},)
		self.pool.get('res.scheduledjobs').write_jobs(cr,uid,res_tmp_id)
		return True

consumption_report()

class consumption_one2many(osv.osv):
	_inherit = "consumption.one2many"

	_columns = {
		'delivery_note_no':fields.char('Delivery Note No.',size=56),
		'delivery_note_date':fields.date('Delivery Note Date'),
		'delivery_address':fields.char('Delivery address',size=200),
		'job_category':fields.selection([('standard','Standard'),('service','Service Order'),('delivery','Product Order'),('adhoc_service','Adhoc-Service Order'),('adhoc_product','Adhoc-Product Order'),('adhoc_service_complaint','Adhoc - Service Complaint'),('product_complaint','Adhoc - Product Complaint')],'Job Type'),
	}


	def psd_note_estimate(self,cr,uid,ids,context=None):
		if context is None: context = {}
		manpower_obj=self.pool.get('hr.manpower.cost')
		list1=[]
		list2=[]
		for res in self.browse(cr,uid,ids):
			search_many2one_id=res.consumption_many2one.id
			create_id=cust_name = service_location_area = job_start_date = job_end_date = from_date=to_date=''
#---------------------------------------------------------------------------------------------------
			search_data=self.pool.get('consumption.report').search(cr,uid,[('id','=',search_many2one_id)])
			if search_data:
				for kk in self.pool.get('consumption.report').browse(cr,uid,search_data):
					from_date=kk.from_date
					to_date=kk.to_date
					# print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",from_date,to_date
			job_id=res.job_id.scheduled_job_id
			cust_name = res.cust_name.id
			service_location_area = res.service_location_area 
			models_data=self.pool.get('ir.model.data')
			if res.job_category == 'delivery':
				form_view1=models_data.get_object_reference(cr, uid, 'psd_operations', 'psd_product_consumption_report_detail_form')
			if res.job_category == 'service':
				form_view2=models_data.get_object_reference(cr, uid, 'psd_operations', 'psd_service_consumption_report_detail_form')
			consumptn_srh = self.pool.get('consumption.report.detail').search(cr,uid,[('consumption_report_id','=',res.id),('job_id','=',job_id)])
			srch_job1 = self.pool.get('res.scheduledjobs').search(cr,uid,[('scheduled_job_id','=',job_id),('state','not in',('unscheduled','cancel'))])
			job_end_date=job_start_date=''
			if srch_job1:
				for job1 in self.pool.get('res.scheduledjobs').browse(cr,uid,srch_job1):
					job_start_date=job1.job_start_time
					job_end_date=job1.new_job_end_time1
					site_address=job1.site_address1
					pse=job1.pse.id
					job_category=job1.job_category
					service_type=job1.service_type
					classification=job1.classification
					equipment=job1.name_equipment.name
					product_transfer_ids=job1.product_transfer_id
					order_period_from=job1.ordered_period_from
					order_period_to=job1.ordered_period_from
					service_order_no = job1.service_order_no
			if consumptn_srh == []:
				create_id=self.pool.get('consumption.report.detail').create(cr,uid,{'consumption_report_id':res.id,
																					'job_id':job_id,'cust_name':cust_name,
																					'service_location_area':service_location_area,
																					'job_start_date':job_start_date,
																					'job_end_date':job_end_date,
																					#'contract_no':,
																					'site_address':site_address,
																					'pse':pse,
																					'job_category':job_category,
																					'service_type':service_type,
																					'classification':classification,
																					'order_period_from':order_period_from,
																					'order_period_to':order_period_to,
																					'equipment_name':equipment,
																					'service_order_no':service_order_no,
																					})

				for prod_line in job1.product_transfer_id:
					self.pool.get('consumption.report.detail').write(cr,uid,create_id,{'product_transfer_ids':[(4,prod_line.id)]})
				
				srch_job = self.pool.get('res.scheduledjobs').search(cr,uid,[('scheduled_job_id','=',job_id),('state','not in',('unscheduled','cancel'))])
				for job in self.pool.get('res.scheduledjobs').browse(cr,uid,srch_job):
					if job.manpower_line:
						for jd in job.manpower_line:
							job_duratn=jd.no_of_hours
							self.pool.get('consumption.report.detail').write(cr,uid,create_id,{'job_duration':job_duratn})
					#by pratik
					for exp_line in job.expense_line:
						self.pool.get('operational.expense.new').create(cr,uid,{'expense_type':exp_line.expense_type, 'expense_quantity':exp_line.expense_quantity,'expense_amt':exp_line.expense_amt,'expense_remarks':exp_line.expense_remarks,'expense_consumption_line':create_id})
# end of code
																	
							
						
					if job.sale_contract:
						sale_contract=job.sale_contract.id
						pms = job.pms
						prod_srh = self.pool.get('product.product').search(cr,uid,[('name','=',pms)])
						for product in self.pool.get('product.product').browse(cr,uid,prod_srh):
							product_id = product.id					
							search_id=self.pool.get('sale.contract').search(cr,uid,[('id','=',sale_contract)])
							search_id1=self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',search_id)])#('pms','=',product_id)
							
							for inspectn in self.pool.get('inspection.costing.line').browse(cr,uid,search_id1):
								if inspectn.pms.prod_type != 'ipm':
									if inspectn.pms.id == product_id and inspectn.address_new.partner_address.id == job.location_id2: 
										if inspectn.chemical_line:
											for chem in inspectn.chemical_line:
												curr_id=chem.id
												chem_name=chem.product_id.id
												uom=chem.product_uom.id
												quantity=chem.quantity
												self.pool.get('estimated.chemical.equipment').create(cr,uid,{'estimated_chem_line':create_id, 'chemical_name':chem_name,'uom':uom,'quantity':quantity})
								else:
									#search_id_ipm=self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',search_id_ipm)])
									#search_id_ipm_insp=self.pool.get('inspection.costing.line').search(cr,uid,[('ipm_id','=',search_id),('pms','=',product_id)])
									#print "search_id_ipm_insp",search_id_ipm_insp
									#print ret
									for iterate in inspectn.ipm_one2many:
									#if search_id_ipm_insp:
										#for inspectn in self.pool.get('inspection.costing.line').browse(cr,uid,search_id_ipm_insp):
											#if inspectn.ipm_one2many:
										if iterate.pms.id == product_id and iterate.ipm_id.address_new.partner_address.id == job.location_id2:
											if iterate.chemical_line:
												for chem in iterate.chemical_line:
															curr_id=chem.id
															chem_name=chem.product_id.id
															uom=chem.product_uom.id
															quantity=chem.quantity
															self.pool.get('estimated.chemical.equipment').create(cr,uid,{'estimated_chem_line':create_id, 'chemical_name':chem_name,'uom':uom,'quantity':quantity})	
					if job.assigned_technician:
						tech_name_id=job.assigned_technician.id
						job_id=job.scheduled_job_id
						search_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('assigned_technician','=',tech_name_id),('state','in',('confirmed','extended','job_done')),('scheduled_job_id','=',job_id),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])
						if search_id:
							for i in self.pool.get('res.scheduledjobs').browse(cr,uid,search_id):
								
								if i.manpower_line:
									for manpower in i.manpower_line:
										empl1=manpower.empl.id
										emp_code=manpower.empl.emp_code
										manpower_cost=manpower_obj.manpower_cost(cr,uid,emp_code=str(emp_code))
										overtime_cost=manpower_obj.manpower_cost(cr,uid,emp_code=str(emp_code), ttype='overtime')
										# print "^^^^^^^^^^^^^^^^^^^^^^^^^^",overtime_cost,manpower_cost
										no_of_hours=manpower.no_of_hours
										# print "fffffffffffffffff",no_of_hours
										role_srh=self.pool.get('hr.employee').search(cr,uid,[('id','=',empl1)])
										for tech_rec in self.pool.get('hr.employee').browse(cr,uid,role_srh):
											des=tech_rec.role
											des1=tech_rec.executor_type
											#tech_name=i.assigned_technician.id
									
											self.pool.get('manpower.estimate').write(cr,uid,manpower.id,{'manpower_consumption_line':create_id,
													'designation':des,'no_of_hours':no_of_hours,'designation1':des1,'no_of_manpower':1,
												'empl':empl1,'emp_code':emp_code,'manpower_cost':manpower_cost, 'overtime_cost':overtime_cost})
								#self.pool.get('manpower.estimate').create(cr,uid,{'manpower_consumption_line':create_id,
												#'designation':des,'no_of_manpower':1,'empl':tech_name,'no_hr_waste':hr_waste})
								if i.assign_material_bool==True and i.assign_resource_id:
									assign_resource_id = i.assign_resource_id
									assign_resource_id1 = re.compile('[\,/]')
									assign_resource_id2 = assign_resource_id1.split(str(assign_resource_id))
									# print "asign_resource_id2111111111111111111111111111111111111111111",assign_resource_id2,assign_resource_id,assign_resource_id1
									for var1 in assign_resource_id2:
										if list1.count(var1):
											pass
										else:
											list1.extend([var1]) 
											search_assign_id=self.pool.get('assign.resource').search(cr,uid,[('id','=',var1)])
											if search_assign_id:
												for j in self.pool.get('assign.resource').browse(cr,uid,search_assign_id):
													if j.assign_resource_technician_one2many:
														for tst in j.assign_resource_technician_one2many:
															if tst.tech_name.id == job.assigned_technician.id:
																ids_srh = tst.id
																#####
																search_ass_wiz_id=self.pool.get('assign.resource.wizard').search(cr,uid,[('assign_resource_id','=',ids_srh),('technician_bool','=',True)])
																if search_ass_wiz_id:
																	for ass_rec in self.pool.get('assign.resource.wizard').browse(cr,uid,search_ass_wiz_id):
																		branch_name=''
																		for tt in ass_rec.assign_resource_wizard_one2many:
																			chemical_name=tt.chemical_name.id
																			batch=tt.batch.id
																			uom=tt.uom.id
																			tag_id=tt.tag_id.id
																			if tt.branch_name :
																				branch_name=tt.branch_name.id
																			if tag_id:
																				self.pool.get('chemical.consumed').create(cr,uid,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})
																			else:
																				search_material=self.pool.get('chemical.consumed').search(cr,uid,[('chemical_name','=',chemical_name),('batch_id','=',batch),('chemical_consumed_line','=',create_id),('branch_name','=',branch_name)])
																
																				if search_material !=[]:
																					for qty_val in self.pool.get('chemical.consumed').browse(cr,uid,search_material):

																						self.pool.get('chemical.consumed').write(cr,uid,qty_val.id,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})
																				else:
																					self.pool.get('chemical.consumed').create(cr,uid,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})
															if tst.extend_tech_name.id:
																if tst.extend_tech_name.id == job.assigned_technician.id:
																	# print "extend name && assigned_tech",tst.extend_tech_name.id,job.assigned_technician.id
																	ids_srh = tst.id
																	#####
																	search_ass_wiz_id=self.pool.get('assign.resource.wizard').search(cr,uid,[('assign_resource_id','=',ids_srh),('technician_bool','=',True)])
																	if search_ass_wiz_id:
																		for ass_rec in self.pool.get('assign.resource.wizard').browse(cr,uid,search_ass_wiz_id):
																			for tt in ass_rec.assign_resource_wizard_one2many:
																				chemical_name=tt.chemical_name.id
																				batch=tt.batch.id
																				uom=tt.uom.id
																				tag_id=tt.tag_id.id
																				if tt.branch_name :
																					branch_name=tt.branch_name.id
																				if tag_id:
																					self.pool.get('chemical.consumed').create(cr,uid,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})
																				else:
																					search_material=self.pool.get('chemical.consumed').search(cr,uid,[('chemical_name','=',chemical_name),('batch_id','=',batch),('chemical_consumed_line','=',create_id),('branch_name','=',branch_name),])
																
																					if search_material !=[]:
																						for qty_val in self.pool.get('chemical.consumed').browse(cr,uid,search_material):

																							self.pool.get('chemical.consumed').write(cr,uid,qty_val.id,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})
																					else:
																						self.pool.get('chemical.consumed').create(cr,uid,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})

															
					if job.assigned_squad:
						squad_name_id=job.assigned_squad.id
						job_id=job.scheduled_job_id
						search_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('assigned_squad','=',squad_name_id),('state','in',('confirmed','extended','job_done')),('scheduled_job_id','=',job_id),('job_start_date','>=',from_date),('job_start_date','<=',to_date),])
						if search_id:
							for i in self.pool.get('res.scheduledjobs').browse(cr,uid,search_id):

								if i.sq_name_new:
									
									for manpower in i.manpower_line:
															emp_code=manpower.empl.emp_code
															manpower_cost=manpower_obj.manpower_cost(cr,uid,emp_code=str(emp_code))
															self.pool.get('manpower.estimate').write(cr,uid,manpower.id,{'manpower_consumption_line':create_id,
																	'designation':manpower.empl.role,'designation1':manpower.empl.executor_type,'no_of_manpower':1,
'empl':manpower.empl.id,'no_hr_waste':i.hours,'emp_code':emp_code,'manpower_cost':manpower_cost})
												#self.pool.get('manpower.estimate').create(cr,uid,{'manpower_consumption_line':create_id,'designation':squad_des,'no_of_manpower':1,'empl':squad_tech,'no_hr_waste':no_of_hours_wasted})
								if i.assign_material_bool==True and i.assign_resource_id1:
									assign_resource_id = i.assign_resource_id1
									assign_resource_id1 = re.compile('[\,/]')
									assign_resource_id2 = assign_resource_id1.split(str(assign_resource_id))
									for var1 in assign_resource_id2:
										if list2.count(var1):
											pass
										else:
											list2.extend([var1]) 
											search_assign_id=self.pool.get('assign.resource').search(cr,uid,[('id','=',var1)])
											if search_assign_id:
												for j in self.pool.get('assign.resource').browse(cr,uid,search_assign_id):
													if j.assign_resource_squad_one2many:
																for tst in j.assign_resource_squad_one2many:
																	if tst.squad_name.id == job.assigned_squad.id:
																		ids_srh = tst.id
																		#####
																		search_ass_wiz_id=self.pool.get('assign.resource.wizard').search(cr,uid,[('assign_resource_id','=',ids_srh),('squad_bool','=',True)])
																		if search_ass_wiz_id:
																			for ass_rec in self.pool.get('assign.resource.wizard').browse(cr,uid,search_ass_wiz_id):
																				for tt in ass_rec.assign_resource_wizard_one2many:
																					chemical_name=tt.chemical_name.id
																					batch=tt.batch.id
																					uom=tt.uom.id
																					tag_id=tt.tag_id.id
																					if tt.branch_name :
																						branch_name=tt.branch_name.id
																					if tag_id:
																						self.pool.get('chemical.consumed').create(cr,uid,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})
																					else:
																						search_material=self.pool.get('chemical.consumed').search(cr,uid,[('chemical_name','=',chemical_name),('batch_id','=',batch),('chemical_consumed_line','=',create_id),('branch_name','=',branch_name),])
																
																						if search_material !=[]:
																							for qty_val in self.pool.get('chemical.consumed').browse(cr,uid,search_material):

																								self.pool.get('chemical.consumed').write(cr,uid,qty_val.id,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})
																						else:
																							self.pool.get('chemical.consumed').create(cr,uid,{'chemical_consumed_line':create_id,'chemical_name':chemical_name,'batch_id':batch,'uom':uom,'tag_id':tag_id,'branch_name':branch_name,})


			else:
				create_id = consumptn_srh[0]
			if res.job_category == 'delivery':
				return {
							'name': ("Product Order Details"),
							'type': 'ir.actions.act_window',
							'res_id': int(create_id),
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'consumption.report.detail',
							'target' : 'new',
							'view_id': form_view1[1],
							#'domain': '[]',
							#'nodestroy': True,
					}
			if res.job_category == 'service':
				return {
							'name': ("Service Order Details"),
							'type': 'ir.actions.act_window',
							'res_id': int(create_id),
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'consumption.report.detail',
							'target' : 'new',
							'view_id': form_view2[1],
							#'domain': '[]',
							#'nodestroy': True,
					}
consumption_one2many()




class consumption_report_detail(osv.osv):
	_inherit="consumption.report.detail"
	_columns={
		'product_transfer_ids': fields.one2many('product.transfer','consumption_id',string="Product Details"),
		'remark':fields.text(string="Delivery Remark",size=300),
		'cust_name':fields.many2one('res.partner','Customer Name'),
		'contract_no':fields.char('Contract No',size=100),
		'service_order_no':fields.char('Service Order No',size=50),
		'site_address':fields.char('Site Address',size=100),
		'pse':fields.many2one('hr.employee','PSE'),
		'job_category':fields.selection([('service','Service Order'),('delivery','Product Order'),('adhoc_service','Adhoc-Service Order'),('adhoc_product','Adhoc-Product Order'),('adhoc_service_complaint','Adhoc - Service Complaint'),('product_complaint','Adhoc - Product Complaint')],'Job Type'),
		'service_type':fields.selection([('Annual Maintainance Contract','Annual Maintainance Contract'),
					('Repairs & Maintainance Charges','Repairs & Maintainance Charges'),
					('Commissioning & Installation Charges','Commissioning & Installation Charges'),
					('Exempted Service','Exempted Service'),
					('Maintainance or Repair Service','Maintainance or Repair Service')
					],'Service Type *'),
		'classification': fields.selection([('Comprehensive','Comprehensive'),
					('Non Comprehensive','Non Comprehensive')],'Classification *'),
		'order_period_from':fields.date('Order Period From'),
		'order_period_to':fields.date('Order Period To'),
		'equipment_name':fields.char('Equipment Name',size=100),
		'remark':fields.text(string="Delivery Remark",size=300),
		'res_comment_line': fields.one2many('comment.line','res_notes'),
	}
consumption_report_detail()


class comment_line(osv.osv):
	_inherit="comment.line"

	def default_get(self,cr,uid,fields,context=None):
		customer_line_ids =[]
		if context is None: context = {}
		res = super(comment_line, self).default_get(cr, uid, fields, context=context)
		res['user_id'] = uid
		res['comment_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		return res
comment_line()