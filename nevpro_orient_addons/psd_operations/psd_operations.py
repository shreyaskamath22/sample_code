#version 1.0.030 customer name size update
#version 1.0.037
from osv import fields, osv
import time
import datetime as dt
from dateutil.relativedelta import *
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from python_code.dateconversion import *
import python_code.dateconversion as py_date
from urllib import urlopen
import re
import local_time
import xmlrpclib
import os
from datetime import *
from dateutil import tz
import pytz
from time import *
import time
from datetime import timedelta
from lxml import etree
import calendar

role_list =(('manager','Manager'),('branch_manager','Branch Manager'),('sales_manager','Sales Manager'),('assistant_general_manager','Assistant General Manager'),('general_manager','General Manager'),('production_manager','Production Manager'),('regional_manager','Regional Manager'),('base_manager','Base Manager'),('manager_customer_acquisition','Manager Customer Acquisition'),('divisional_manager','Divisional Manager'),('territory_manager','Territory Manager'),('area_manager','Area Manager'),('farm_ manager','Farm Manager'),('lab_assistant','Lab Assistant'),('supervisor','Supervisor'),('customer_sales_executive','Customer Sales Executive'),('product_sales_executive','Product Sales Executive'),('technician','Technician'),('operations_executive','Operations Executive'),('customer_care_executive','Customer Care Executive'),('procurement_coordinator','Procurement Coordinator'),('hr_associate','HR Associate'),('field_ coordinator','Field Coordinator'),('officer','Officer'),('production_officer','Production Officer'),('quality_assurance_executive','Quality Assurance Executive'),('group_leader','Group Leader'),('coordinator','Coordinator'),('data_analyst','Data Analyst'),('peon','Peon'),('entomologist','Entomologist'),('engineer','Engineer'),('maintenance_engineer','Maintenance Engineer'),('mechanic ','Mechanic'),('Electrician','electrician'),('mechanic_cum_electrician','Mechanic cum Electrician'),('director','Director'),('president','President'),('vice_president','Vice-President'),('secretary','Secretary'),('cmd_ceo','CMD & CEO'),('lab_technician','Lab Technician'),('head','Head'),('representative','Representative'),('associate','Associate'),('team_leader','Team Leader'),('horticulturist','Horticulturist'),('support_ engineer','Support Engineer'),('marketing_representative','Marketing Representative'),('in-charge','In-Charge'),('territory_sales_ executive','Territory Sales Executive'),('field_assistant','Field Assistant'),('operations_assistant','Operations Assistant'),('office_ assistant','Office Assistant'),('office_assistant_typist','Office Assistant/Typist'),('clerk','Clerk'),('receptionist','Receptionist'),('accounts_assistant','Accounts Assistant'),('executive_assistant','Executive Assistant'),('typist','Typist'),('data_entry_operator','Data Entry Operator'),('operations_manager','Operations Manager'),('sales_assistant','Sales Assistant'),('sales_officer','Sales Officer'),('products_manager','Products Manager'),('project_manager','Project Manager'),('technical_officer','Technical Officer'))

def _get_role(role_new):
    data = ''
    for x,y in role_list :
        if  x == role_new :
                data = y 
                break
    return data

class res_scheduledjobs(osv.osv):
	_inherit="res.scheduledjobs"

	def _check_transfered(self, cr, uid, ids, field_name, args, context=None):
		res = {}
		for rec in self.browse(cr, uid, ids, context):
			res[rec.id] = False
			if rec.name_contact:
				if rec.name_contact.is_transfered:
					res[rec.id]=True
		return res


	def _show_record(self, cr, uid, ids, field_names, arg=None, context=None):
		result = {}
		if not ids: return result
		for id in ids:
			result.setdefault(id, [])
		for res in self.browse(cr,uid,ids):
			if res.delivery_challan_no and res.job_category == 'delivery':
				scheduled_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('delivery_challan_no','=',res.delivery_challan_no),('job_category','=','delivery')])
				for r in scheduled_id:
					result[res.id].append(r)
			if res.service_order_no and res.job_category == 'service':
				scheduled_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('service_order_no','=',res.service_order_no),('job_category','=','service')])
				for r in scheduled_id:
					result[res.id].append(r)
			return result

	def _show_record_complaint(self, cr, uid, ids, field_names, arg=None, context=None):
		result = {}
		if not ids: return result
		for id in ids:
			result.setdefault(id, [])
		for res in self.browse(cr,uid,ids):
			if res.delivery_challan_no and res.job_category == 'adhoc_product_complaint':
				scheduled_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('delivery_challan_no','=',res.delivery_challan_no),('job_category','=','adhoc_product_complaint')])
				for r in scheduled_id:
					result[res.id].append(r)
			if res.service_order_no and res.job_category == 'adhoc_service_complaint':
				scheduled_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('service_order_no','=',res.service_order_no),('job_category','=','adhoc_service_complaint')])
				for r in scheduled_id:
					result[res.id].append(r)
			return result

	_columns={
		# 'job_category':fields.selection([('service','Service Order'),('delivery','Product Order'),('adhoc_service','Adhoc-Service Order'),('adhoc_product','Adhoc-Product Order'),('adhoc_service_complaint','Adhoc - Service Complaint'),('product_complaint','Adhoc - Product Complaint')],'Job Type'),
		'job':fields.selection([('service','Service Order'),('delivery','Product Order'),('adhoc_service','Adhoc-Service Order'),('adhoc_product','Adhoc-Product Order'),('adhoc_service_complaint','Adhoc - Service Complaint'),('product_complaint','Adhoc - Product Complaint')],'Job Type'),
		'erp_order_no':fields.char('ERP Order No Ref',size=56),
		'service_order_no':fields.char('ERP Order No',size=100),
		'erp_order_date':fields.date('ERP Order Date'),
		'delivery_address':fields.text('Delivery Address',size=200),
		'delivery_order_no':fields.char('Delivery Order No.',size=56),
		'delivery_by':fields.char('Delivery By',size=100),
		'delivery_challan_no':fields.char('Delivery Note No',size=100),
		'delivery_note_date':fields.date('Delivery Note Date'),
		'tech_id':fields.many2one('hr.employee','Technician Names'),
		'squad_id':fields.many2one('res.define.squad','Squad Names'),
		'name_equipment':fields.many2one('product.product','Equipment Name'),
		'ordered_period_from':fields.date('Order Period From*'),
		'ordered_period_to':fields.date('Order Period To*'),
		'contract_period':fields.integer('Contract Period'),
		'web_order_no':fields.char('Web Order No.',size=56),
		'web_order_date':fields.date('Web Order Date'),
		'delivered_by':fields.char('Delivered By',size=56),
		'delivery_date':fields.date('Delivery Date'),
		'against_free_replacement':fields.boolean('Against Free Replacement'),
		'product_transfer_id':fields.one2many('product.transfer','product_data','Product Details'),
		'pse':fields.many2one('hr.employee',string="PSE"),
		'service_type':fields.selection([('Annual Maintainance Contract','Annual Maintainance Contract'),
					('Repairs & Maintainance Charges','Repairs & Maintainance Charges'),
					('Commissioning & Installation Charges','Commissioning & Installation Charges'),
					('Exempted Service','Exempted Service'),
					('Maintainance or Repair Service','Maintainance or Repair Service')
					],'Service Type *'),
		'classification': fields.selection([('Comprehensive','Comprehensive'),
					('Non Comprehensive','Non Comprehensive')],'Classification *'),
		'is_transfered':fields.function(_check_transfered, string="Is Transfered", type="boolean", store=True),
		'ops_record_noncomplaint': fields.function(_show_record,relation='res.scheduledjobs',type='one2many',method=True,string='Operations job history'),
		'ops_record_complaint': fields.function(_show_record_complaint,relation='res.scheduledjobs',string='Operations job history',type='one2many',method=True),
		'site_address1':fields.text('Site Address',size=200),
		'phone1':fields.char('Mobile',size=20),
	}


	# def show_technician(self,cr,uid,ids,context=None):
	# 	res = super(res_scheduledjobs,self).show_technician(cr,uid,ids)
	# 	curr_id = self.browse(cr,uid,ids[0])
	# 	if curr_id.job_start_time > curr_id.job_end_time:
	# 		qqq
	# 		raise osv.except_osv(('Alert!'),('Job End date must be Greater than Job End date !'))
	# 	return True

	def psd_unscheduled_new(self,cr,uid,ids,context=None):
		self.psd_unscheduled(cr,uid,ids,context=context)		


	def psd_unscheduled(self,cr,uid,ids,context=None):
		current_date = datetime.now().date()
		job_id=''
		technician_squad_merge1=''
		technician_squad_merge2=''
		curr_id = self.browse(cr,uid,ids[0])
		for i in self.browse(cr,uid,ids):
			assign = ''
			if i.state=='rescheduled':		

				self.assign_techniciannn(cr,uid,ids,context=context)
				for k in self.browse(cr,uid,ids):

						if k.assigned_technician :
							assign = k.assigned_technician.concate_name
						if k.assigned_squad :
							assign = k.assigned_squad.squad_name
							assigned_squad=k.assigned_squad.id
						if k.remark_one2many :
							for pp in k.remark_one2many :
								reason = pp.comment
						if k.erp_order_no:
							product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',k.erp_order_no)])
							invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',k.delivery_challan_no)])
							if invoice_id :
								self.pool.get('job.history').create(cr,uid,{'contract_no':k.job_id,'job_id':k.scheduled_job_id,'job_schedule_date':k.req_date_time,'job_reschedule_date':str(datetime.now()),'job_start_date':k.job_start_time,'job_end_date':k.job_end_time,'record_date':current_date,
									'technician_squad':assign,'job_status':'Job Scheduled','history_id':k.id,'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
							else:
								self.pool.get('job.history').create(cr,uid,{'contract_no':k.job_id,'job_id':k.scheduled_job_id,'job_schedule_date':k.req_date_time,'job_reschedule_date':str(datetime.now()),'job_start_date':k.job_start_time,'job_end_date':k.job_end_time,'record_date':current_date,
									'technician_squad':assign,'job_status':'Job Scheduled','history_id':k.id,'product_order_id':product_order_id[0]})					
						if k.service_order_no:
							service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',k.service_order_no)])
							invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',k.service_order_no)])
							if invoice_id :
								self.pool.get('job.history').create(cr,uid,{'contract_no':k.job_id,'job_id':k.scheduled_job_id,'job_schedule_date':k.req_date_time,'job_reschedule_date':str(datetime.now()),'job_start_date':k.job_start_time,'job_end_date':k.job_end_time,'record_date':current_date,
									'technician_squad':assign,'job_status':'Job Scheduled','history_id':k.id,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
							else:
								self.pool.get('job.history').create(cr,uid,{'contract_no':k.job_id,'job_id':k.scheduled_job_id,'job_schedule_date':k.req_date_time,'job_reschedule_date':str(datetime.now()),'job_start_date':k.job_start_time,'job_end_date':k.job_end_time,'record_date':current_date,
									'technician_squad':assign,'job_status':'Job Scheduled','history_id':k.id,'service_order_id':service_order_id[0]})					
			
				for clr in self.browse(cr,uid,ids):
					if clr.onhold_reason:
						cr.execute(('update res_scheduledjobs set onhold_reason=%s where id=%s'),('',clr.id))
					'''if clr.expense_line:
						for req in clr.expense_line:
							self.pool.get('operational.expense').unlink(cr,uid,req.id)'''
			if i.state=='unscheduled':
				self.write(cr,uid,ids,{'bulk_bool':False})
				self.assign_techniciannn(cr,uid,ids,context=context)
				for var in self.browse(cr,uid,ids):
					job_id=var.job_id
					if var.assigned_technician :
						assign = var.assigned_technician.concate_name
					if var.assigned_squad :
						assign = var.assigned_squad.squad_name
					if var.erp_order_no:
						product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',var.erp_order_no)])
						invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',var.delivery_challan_no)])
						if invoice_id:
							self.pool.get('job.history').create(cr,uid,{'contract_no':var.job_id,'job_id':var.scheduled_job_id,'job_schedule_date':var.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),'job_start_date':var.job_start_time,'job_end_date':var.job_end_time,'record_date':current_date,
							'job_status':'Job Scheduled','history_id':var.id,'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
						else :
							self.pool.get('job.history').create(cr,uid,{'contract_no':var.job_id,'job_id':var.scheduled_job_id,'job_schedule_date':var.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),'job_start_date':var.job_start_time,'job_end_date':var.job_end_time,'record_date':current_date,
							'job_status':'Job Scheduled','history_id':var.id,'product_order_id':product_order_id[0]})
					if var.service_order_no:
						service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',var.service_order_no)])	
						invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',var.service_order_no)])
						if invoice_id:
							self.pool.get('job.history').create(cr,uid,{'contract_no':var.job_id,'job_id':var.scheduled_job_id,'job_schedule_date':var.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),'job_start_date':var.job_start_time,'job_end_date':var.job_end_time,'record_date':current_date,
							'job_status':'Job Scheduled','history_id':var.id,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
						else:
							self.pool.get('job.history').create(cr,uid,{'contract_no':var.job_id,'job_id':var.scheduled_job_id,'job_schedule_date':var.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),'job_start_date':var.job_start_time,'job_end_date':var.job_end_time,'record_date':current_date,
							'job_status':'Job Scheduled','history_id':var.id,'service_order_id':service_order_id[0]})

				for tech_line in curr_id.technician_detail:
					if tech_line.check_technician == True: 
						self.write(cr,uid,curr_id.id,{'tech_id':tech_line.tech_id.id,'delivery_by':tech_line.tech_id.name or '' +' '+tech_line.tech_id.middle_name or '' +' '+tech_line.tech_id.last_name or ''})
						search_delivery_order_id = self.pool.get('stock.transfer').search(cr,uid,[('stock_transfer_no','=',curr_id.delivery_order_no)])
						self.pool.get('stock.transfer').write(cr,uid,search_delivery_order_id,{'person_name':tech_line.tech_id.name or ''+' '+tech_line.tech_id.middle_name or ''+' '+tech_line.tech_id.last_name or ''})
				for squad_line in curr_id.squad_detail:
					if squad_line.check_squad == True:
						self.write(cr,uid,curr_id.id,{'squad_id':squad_line.squad_id.id,'delivery_by':squad_line.squad_id.squad_name})
						search_delivery_order_id = self.pool.get('stock.transfer').search(cr,uid,[('stock_transfer_no','=',curr_id.delivery_order_no)])
						self.pool.get('stock.transfer').write(cr,uid,search_delivery_order_id,{'person_name':squad_line.squad_id.squad_name})
				for clr in self.browse(cr,uid,ids):
					if clr.extension_reason:
						cr.execute(('update res_scheduledjobs set extension_reason=%s'),('',))
				for cal_date in self.browse(cr,uid,ids):
					self.write(cr,uid,ids,{'job_total_days':str(datetime.now())})
					
			
			if i.state=='complaint':
				self.assign_techniciannn(cr,uid,ids,context=context)
				for var in self.browse(cr,uid,ids):
					job_id=var.job_id
					if var.assigned_technician :
							assign = var.assigned_technician.concate_name
					
					if var.assigned_squad :
							assign = var.assigned_squad.squad_name
					if var.erp_order_no:
						product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',var.erp_order_no)])
						invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',var.delivery_challan_no)])
						if invoice_id:
							self.pool.get('job.history').create(cr,uid,{'contract_no':var.job_id,'job_id':var.scheduled_job_id,'job_schedule_date':var.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),'job_start_date':var.job_start_time,'job_end_date':var.job_end_time,'record_date':current_date,
							'job_status':'Job Scheduled','history_id':var.id,'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
						else:
							self.pool.get('job.history').create(cr,uid,{'contract_no':var.job_id,'job_id':var.scheduled_job_id,'job_schedule_date':var.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),'job_start_date':var.job_start_time,'job_end_date':var.job_end_time,'record_date':current_date,
							'job_status':'Job Scheduled','history_id':var.id,'product_order_id':product_order_id[0]})
					if var.service_order_no:
						service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',var.service_order_no)])	
						invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',var.service_order_no)])
						if invoice_id:										
							self.pool.get('job.history').create(cr,uid,{'contract_no':var.job_id,'job_id':var.scheduled_job_id,'job_schedule_date':var.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),'job_start_date':var.job_start_time,'job_end_date':var.job_end_time,'record_date':current_date,
							 'job_status':'Job Scheduled','history_id':var.id,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
						else:
							self.pool.get('job.history').create(cr,uid,{'contract_no':var.job_id,'job_id':var.scheduled_job_id,'job_schedule_date':var.req_date_time,'technician_squad':assign,'job_reschedule_date':str(datetime.now()),'job_start_date':var.job_start_time,'job_end_date':var.job_end_time,'record_date':current_date,
							 'job_status':'Job Scheduled','history_id':var.id,'service_order_id':service_order_id[0]})

			self.write(cr,uid,ids,{'record_date':current_date,'job_total_days':str(datetime.now()),'attrs_reschedule':False,'attrs_cancel':False,'attrs_extended':False,})


		
		self.write_jobs(cr,uid,ids,context=context) #zubair 22.12.2015 for .sql file on button click
		
		return True


	def psd_check_available(self, cr, uid, ids, context=None): 
		if context == None:
			context = {}
		for res in self.browse(cr,uid,ids):
			return { 
				'type': 'ir.actions.act_window', 
				'name': 'Check Availability', 
				'view_mode': 'calendar', 
				'view_type': 'calendar', 
				'res_model':'res.scheduledjobs',
				'res_id': '', 
				'target': 'new',
				'context': {'default_req_date_time':res.req_date_time},
				'domain':"[('state','in',('scheduled','confirmed'))]"

				   }
	
	def psd_show_technician(self,cr,uid,ids,context=None):
		location_add = temp_id = ''
		DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
		current_date = datetime.now().date()
		start_time1 = ''
		service = ''
		today_2=''
		temp_1=''
		today_22=''
		temp_2=''
		cur_branch=''

		
				#cr.execute("update res_scheduledjobs set job_start_date=cast(job_start_time as date)")
				#cr.execute("update res_scheduledjobs set job_end_date=cast(job_end_time as date)")
		cr.execute("update res_scheduledjobs set job_start_date=cast(job_start_time as date),job_end_date=cast(job_end_time as date) where id =%(val)s",{'val':ids[0]})
		leave_p = []
		leave_a = []
		search_leave = self.pool.get('attendence.master').search(cr,uid,[('id','>',0)])
		for leave_ln in self.pool.get('attendence.master').browse(cr,uid,search_leave):
			if leave_ln.leave_application == False:
				leave_p.append(leave_ln.key)
								
			if leave_ln.leave_application == True:
				leave_a.append(leave_ln.key)     
								  
		leave_p = tuple(leave_p)
		leave_a = tuple(leave_a)
		for o in self.browse(cr,uid,ids):
			if not o.job_start_time or not o.job_end_time:
				raise osv.except_osv(('Alert!'),('Please Select Start and End date.'))
				new_job_start_time1=o.new_job_start_time1
				new_job_end_time1=o.new_job_end_time1

		#Zee
		self.write(cr,uid,ids,{'overtime_bool':False,'not_overtime_bool':False})
		#cr.execute("update res_scheduledjobs set job_start_date=cast(job_start_time as date)")
				#cr.execute("update res_scheduledjobs set job_end_date=cast(job_end_time as date)")
		job_start_date123=o.job_start_date
		job_start_date_new=get_weekday_Name(job_start_date123)
		cur_branch=self.pool.get('res.users').browse(cr,uid,uid).company_id.id
		DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
		if o.job_start_time :
			today_0=datetime.strptime(o.job_start_time, DATETIME_FORMAT)
			today_1=datetime.strptime(o.job_start_time, DATETIME_FORMAT)
			today_2=local_time.convert_time(today_1).time()
			search_users = self.pool.get('res.users').browse(cr,uid,uid).company_id.id
			srh_cmp = self.pool.get('res.company').search(cr,uid,[('id','=',search_users)])
			for company in self.pool.get('res.company').browse(cr,uid,srh_cmp):
				start_time  = company.weekday_start_time
				temp_1 = self.float_time_convert(cr, uid, str(today_0), start_time)
		if o.job_end_time:
			today_00=datetime.strptime(o.job_end_time, DATETIME_FORMAT)	
			today_22=local_time.convert_time(today_00).time()
			search_users = self.pool.get('res.users').browse(cr,uid,uid).company_id.id
			srh_cmp = self.pool.get('res.company').search(cr,uid,[('id','=',search_users)])
			for company in self.pool.get('res.company').browse(cr,uid,srh_cmp):
				end_time  = company.weekday_end_time if company.weekday_end_time else False
				#extended_time  = company.extended_hrs if company.extended_hrs else False
				#total_time = end_time + extended_time
				temp_2 = self.float_time_convert(cr, uid, str(today_00), end_time)
			print type(temp_1),type(temp_2),type(today_2),type(today_22),temp_1,temp_2,today_2,today_22
			check_exist_holiday = self.pool.get('hr.holiday.new').search(cr,uid,[('holiday_selection','!=','optional_holidays'),('from_date','>=',o.job_start_date),('to_date','<=',o.job_end_date),('company_id','=',o.company_id.id)])

			# make str as datatype today_2 & today_22
			#if check_exist_holiday or (job_start_date_new=='Sun') or (today_2 < temp_1) or (today_22 > temp_2) :
			day_no = datetime.strptime(o.job_start_time, DATETIME_FORMAT).weekday()
			day_name = calendar.day_name[day_no]
			day_string = day_name[:3]
			if check_exist_holiday or (day_string=='Sun') or str(today_2) < str(temp_1) or str(today_22) > str(temp_2) :

				self.write(cr,uid,ids,{'overtime_bool':True})
			else:
				self.write(cr,uid,ids,{'not_overtime_bool':True})
			temp_id=o.id
			if not o.job_start_time or not o.job_end_time:	
				raise osv.except_osv(('Alert!'),('Please Select date.'))
			today1=datetime.strptime(o.job_start_time, DATETIME_FORMAT)	
			today2=datetime.strptime(o.job_end_time, DATETIME_FORMAT)
			#if o.job_start_time or o.job_end_time:
				#print "*******************************",today1.date(),current_date,today2.date()
				#print xxxxxxxx
				#if (today1.date() < current_date) or (today2.date() < current_date) :
					#raise osv.except_osv(('Invalid Date !'),('Select proper date.'))
			current_date_new = datetime.now().date()
			DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
		technician_available_search=self.pool.get('technician.available').search(cr,uid,[('technician_id','=',temp_id)])
		squad_available_search=self.pool.get('squad.available').search(cr,uid,[('squad_detail_id','=',temp_id)])
		for temp_technician in o.technician_detail:
			 if temp_technician.check_technician==True:
				  raise osv.except_osv(('Alert!'),('You Cannot Click Again After Assigning The Technician')) 
		for temp_squad in o.squad_detail:
			 if temp_squad.check_squad==True:
			  raise osv.except_osv(('Alert!'),('You Cannot Click Again After Creating a The Squad'))
		self.pool.get('technician.available').unlink(cr,uid,technician_available_search)
		self.pool.get('squad.available').unlink(cr,uid,squad_available_search)
		#cr.execute('''delete from technician_available''')
		#cr.execute('''delete from squad_available''')

		for o in self.browse(cr,uid,ids):
			temp_location_id=o.location_id
			temp_id=o.id
			req_date=o.req_date_time
			start_time1=o.job_start_date
			start_time=o.job_start_time
			end_time=o.job_end_time
			t1=datetime.strptime(o.job_start_time,DATETIME_FORMAT)
			job_start_time_new=local_time.convert_time(t1).date()
			job_start_time_new1=local_time.convert_time(t1)
			end_time=o.job_end_time
			if(not o.job_start_time):
					raise osv.except_osv(('Alert!'),('Please select Job start time.'))
			if o.job_start_time and o.job_end_time:
				if o.job_end_time <= o.job_start_time:
					raise osv.except_osv(('Alert!'),('Please select progressive Job end time.'))
		record_id=[]

		for m in self.browse(cr,uid,ids):
				job_start = m.job_start_time
				job_end = m.job_end_time
				req_date_time = m.req_date_time
				print "job_start  && job_end  && start_time",job_start,job_end,start_time,end_time
				
				Main_Str1 = "select assigned_technician from res_scheduledjobs  where id in( \
																										select id from res_scheduledjobs \
																										where " +"'"+job_start+"'"+" between job_start_time and job_end_time \
																										or"+"'"+job_end+"'"+" between job_start_time and job_end_time \
or "+"job_start_time  between " +"'"+job_start+"'"+" and "+"'"+job_end+"' \
or "+"job_end_time  between " +"'"+job_start+"'"+" and "+"'"+job_end+"' \
																										) and assigned_technician is not null and state not in ('job_done','cancel','complaint','unscheduled','rescheduled') "
				cr.execute(Main_Str1)
				schedule = cr.fetchall()
				print "schedule",schedule
				if schedule != [(None,)]:
					tech_ids=self.pool.get('hr.employee').search(cr,uid,[('id','not in',schedule),('role_selection','=','executor'),('status','!=','resign'),('branch','=',cur_branch)])
				else :
					tech_ids=self.pool.get('hr.employee').search(cr,uid,[('id','>',0),('role_selection','=','executor'),('status','!=','resign'),('branch','=',cur_branch)])
				
				if tech_ids:
					   for remaining_tech in self.pool.get('hr.employee').browse(cr,uid,tech_ids):
						proceed = 0
						service = location_add = search_tech1 = search_tech= ''
						role_new = _get_role(remaining_tech.role)
						role_new1=remaining_tech.executor_type
						if remaining_tech.creation_type == 'extra_emp' and remaining_tech.res_active==True:
							proceed = 1
						if str(current_date) == str(job_start_time_new):
							search_tech = self.pool.get('hr.attendence.new').search(cr,uid,[('date','=',current_date),('employee_name','=',remaining_tech.id),('leaves','in',leave_p)])
							if search_tech != []:
								proceed = 1
						else:
							search_tech1 = self.pool.get('hr.attendence.new').search(cr,uid,[('date','=',job_start_time_new),('employee_name','=',remaining_tech.id),('leaves','in',leave_a)])
							if not search_tech1:
								proceed = 1
						if proceed == 1:
							past_obj = self.pool.get('technician.past.record')
							cr.execute('select technician from technician_past_record where id >0')
							var = [r[0] for r in cr.fetchall()]
							count = 0
							if remaining_tech.id in var :
								count = count +1
								ss = self.pool.get('technician.past.record').search(cr,uid,[('technician','=',remaining_tech.id),('date','=',job_start_time_new)],order="job_start desc",limit=1)
								array = []
								if ss:
									for m1 in self.pool.get('technician.past.record').browse(cr,uid,ss):
										m11 = m1.id
										dt_format = "%Y-%m-%d %H:%M:%S"
										job_start = m1.job_start
										job_end =  m1.job_end
										average1 = re.compile('[\-/\ /\:/]')
										avg1 = average1.split(str(job_start))
										avg2 = average1.split(str(job_end))
										print "avg1",avg1,job_start,job_end
										print "avg1[1]",avg1[1]
										print "avg1[2]",avg1[2]
										print "avg1[3]",avg1[3]
										print "avg2",avg2
										print "avg2[1]",avg2[1]
										print "avg2[2]",avg2[2]
										print "avg2[3]",avg2[3]
										cnt = 0
										job_start_month = datetime.strptime(job_start,dt_format).month
										job_start_day = datetime.strptime(job_start,dt_format).day
										job_end_format = datetime.strptime(job_end,dt_format)
										current_date = datetime.now().date()
										job_start_time=m1.job_start
										job_start_time1=datetime.strptime(job_start_time, DATETIME_FORMAT).date()
										job_s = datetime.strptime(job_start,dt_format)								
										t1_current_tz=setUtc2IstTimeZone(str(t1))
										t1_current_tz=datetime.strptime(t1_current_tz,dt_format)
										if m.service_area:
											service1 = m1.service_area
											array.append(service1)
										else:
											service1 = ''
											array.append(service1)

										if array != []:
											
											for test in array:
												if job_start_day == job_start_time1.day   and job_s<t1_current_tz:
													service = str(test)+'['+avg1[2]+'-'+avg1[1]+' '+avg1[3]+':'+avg1[4]+' to '+avg2[2]+'-'+avg2[1]+' '+avg2[3]+':'+avg2[4]+']'
													location_add = m1.address
												else :
													service=''
													location_add=''
										else:
											if job_start_day == job_start_time1.day  and job_s<t1_current_tz:
												service = '['+avg1[2]+'-'+avg1[1]+' '+avg1[3]+':'+avg1[4]+' to '+avg2[2]+'-'+avg2[1]+' '+avg2[3]+':'+avg2[4]+']'
												location_add = m1.address if m1.address else ''
											else:
												service = ''
												location_add=''
								else:
									service = ''
									location_add=''
							else:
								service = ''
								location_add=''
						
							a = self.pool.get('technician.available').create(cr,uid,{'name':remaining_tech.name,'val':o,'temp_technician_id':temp_id,'designation':role_new,'designation1':role_new1,'location_address':location_add,'technician_id':m.id,'service_info':service,'tech_id':remaining_tech.id})
				Flag = False
				
				Main_Str = "select assigned_squad from res_scheduledjobs  where id in( \
																										select id from res_scheduledjobs \
																										where " +"'"+m.job_start_time+"'"+" between job_start_time and job_end_time \
																										or"+"'"+m.job_end_time+"'"+" between job_start_time and job_end_time \
or "+"job_start_time  between " +"'"+m.job_start_time+"'"+" and "+"'"+m.job_end_time+"' \
or "+"job_end_time  between " +"'"+m.job_start_time+"'"+" and "+"'"+m.job_end_time+"' \
																									) and assigned_squad is not null and state not in ('job_done','cancel','complaint','unscheduled','rescheduled') "

				cr.execute(Main_Str)
				scheduled_squad = cr.fetchall()
				if scheduled_squad != [(None,)]:
					
					#print aaaaa
					squad_ids=self.pool.get('res.define.squad').search(cr,uid,[('id','not in',scheduled_squad)])
				else :
					#print bbbb
					squad_ids=self.pool.get('res.define.squad').search(cr,uid,[('id','>',0)])
				if squad_ids:
						for o in squad_ids:
							count = 0
							count1 = 0
							technician_array3=[]
							remaining_squad=self.pool.get('res.define.squad').browse(cr,uid,o)
							for j in remaining_squad.tech2:
								count = count + 1
								hr_srh = self.pool.get('hr.employee').search(cr,uid,[('id','=',j.technician_id.id),('status','!=','resign'),('branch','=',cur_branch)])
								
								for tech in self.pool.get('hr.employee').browse(cr,uid,hr_srh):
									
									if str(current_date) == str(job_start_time_new):
										if tech.creation_type == 'extra_emp' and tech.res_active==True:
											count1 = count1 + 1
											Flag = True
											name1 = tech.concate_name
											technician_array3.append(name1)
										else:
											search_tech = self.pool.get('hr.attendence.new').search(cr,uid,[('date','=',current_date),('employee_name','=',tech.id),('leaves','in',leave_p)])
											if search_tech:
												for var_att in self.pool.get('hr.attendence.new').browse(cr,uid,search_tech):
													count1 = count1 + 1
													Flag = True
													name1 = tech.concate_name
													technician_array3.append(name1)
									else:
										search_tech = self.pool.get('hr.attendence.new').search(cr,uid,[('date','=',job_start_time_new),('employee_name','=',tech.id),('leaves','in',leave_a)])
										
										if not search_tech:	
											count1 = count1 + 1
											Flag = True
											name1 = tech.concate_name
											technician_array3.append(name1)
							if count == count1 and Flag == True:	
								technicians3 = ''
								if technician_array3 != []:
									for val in technician_array3:
										var = val
										if technicians3 == '':
											technicians3 = var
										else:
											technicians3=technicians3 +','+var
									cr.execute('''insert into squad_available(name,squad_id,squad_detail_id,technicians)values(%(name)s,%(val)s,%(temp_technician_id)s,%(technicians)s)''',{'name':remaining_squad.squad_name,'val':o,'temp_technician_id':temp_id,'technicians':technicians3 if technicians3 else ''})

		Main_Str3 = " select id from res_scheduledjobs \
																						where"+"'"+m.job_start_time+"'"+ "between job_start_time and job_end_time \
																						or"+ "'"+m.job_end_time+"'"+"between job_start_time and job_end_time \
or "+"job_start_time  between " +"'"+m.job_start_time+"'"+" and "+"'"+m.job_end_time+"' \
or "+"job_end_time  between " +"'"+m.job_start_time+"'"+" and "+"'"+m.job_end_time+"' \
																					 and state not in ('job_done','cancel','complaint','unscheduled','rescheduled')"

		cr.execute(Main_Str3)
		tech_squad = cr.fetchall()
		for test in tech_squad:
			tech = self.pool.get('res.scheduledjobs').search(cr,uid,[('id','=',test)])
			technician_job_id=[]
			squad_job_id=[]
			squad_tech = []
			if tech:
				for o11 in self.pool.get('res.scheduledjobs').browse(cr,uid,tech):
					if o11.assigned_technician:
						technician_job_id.append(o11.assigned_technician.id)
						if (((start_time>=o11.job_start_time)and(start_time<=o11.job_end_time))or((end_time>=o11.job_start_time)and(end_time<=o11.job_end_time))or((start_time<=o11.job_start_time)and(end_time>=o11.job_start_time))):
							cr.execute('''delete from technician_available where tech_id=%(val)s''',{'val':o11.assigned_technician.id})
							squad_srh1 = self.pool.get('res.define.squad').search(cr,uid,[('id','>',0)])
							if squad_srh1:
								for variable in self.pool.get('res.define.squad').browse(cr,uid,squad_srh1):
									for var_new in variable.tech2:
										if var_new.technician_id.id == o11.assigned_technician.id:
											cr.execute('''delete from squad_available where squad_id=%(val)s''',{'val':variable.id})
						else:
							technician=self.pool.get('res.technician').browse(cr,uid,o11.assigned_technician.id)
							check_tech=self.pool.get('technician.available').search(cr,uid,[('tech_id','=',o11.assigned_technician.id)])
							if not check_tech:
								print "ff"
					elif o11.assigned_squad:
						squad_search = self.pool.get('res.define.squad').search(cr,uid,[('id','=',o11.assigned_squad.id)])
						for squad in self.pool.get('res.define.squad').browse(cr,uid,squad_search):
							for tech in squad.tech2:
								squad_tech.append(tech.technician_id.id)
						if (((start_time>=o11.job_start_time)and(start_time<=o11.job_end_time))or((end_time>=o11.job_start_time)and(end_time<=o11.job_end_time))or((start_time<=o11.job_start_time)and(end_time>=o11.job_start_time))):
							cr.execute('''delete from squad_available where squad_id=%(val)s''',{'val':o11.assigned_squad.id})
							if squad_tech:
								for value in squad_tech:
									cr.execute('''delete from technician_available where tech_id=%(val)s''',{'val':value})
									#sql = "select SA.id from squad_available SA,res_define_squad RS where RS.squad_name=SA.name and 
								search_sq = self.pool.get('squad.available').search(cr,uid,[('id','>',0)])
								for sq in self.pool.get('squad.available').browse(cr,uid,search_sq):
										
										search_sq1 = self.pool.get('res.define.squad').search(cr,uid,[('id','=',sq.squad_id.id)])
										for val1 in  self.pool.get('res.define.squad').browse(cr,uid,search_sq1):
											for tech in val1.tech2:
												if tech.technician_id.id in squad_tech:
													cr.execute('''delete from squad_available where squad_id=%(val)s''',{'val':val1.id})

		self.write_jobs(cr,uid,ids,context=context) #zubair 22.12.2015 for .sql file on button click
													
											
		return True



	def psd_job_cancel(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'complaint_job_cancel':True,'attrs_cancel':True})
		self.write_jobs(cr,uid,ids,context=context)
		return True

	def psd_job_reschedule(self,cr,uid,ids,context=None):
		current_date = datetime.now().date()
		self.write(cr,uid,ids,{'onhold_bool':True,'record_date':current_date,'attrs_reschedule':True})
		self.write_jobs(cr,uid,ids,context=context)
		return True


	def psd_job_extended1(self,cr,uid,ids,context=None):
		current_date = datetime.now().date()
		self.write(cr,uid,ids,{'extened_bool':True,'record_date':current_date,'attrs_extended':True})
		self.write_jobs(cr,uid,ids,context=context)
		return True


	def psd_job_extended_new(self,cr,uid,ids,context=None):
		assign = ''
		squad = val = ''
		extended_date_time=extended_end_time1=extended_start_time1=''
		current_date = datetime.now().date()
		
		for k in self.browse(cr,uid,ids):
			if not k.job_extended_one2many :
				raise osv.except_osv(('Alert!'),('Please enter the  Job Extension Details'))
			search_id3=self.pool.get('job.extended').search(cr,uid,[('job_extended_line','=',k.id)],order="id desc",limit=1)
			if k.assigned_technician :
				assign = k.assigned_technician.concate_name
			if k.assigned_squad :
				assign = k.assigned_squad.squad_name
			if search_id3:
				for var_time in self.pool.get('job.extended').browse(cr,uid,search_id3) :
					extended_start_time1=var_time.extended_start_time
					start_date11=datetime.strptime(extended_start_time1, "%Y-%m-%d %H:%M:%S").date()
					extended_end_time1=var_time.extended_end_time
					end_date11=datetime.strptime(extended_end_time1, "%Y-%m-%d %H:%M:%S").date()
					extended_date_time=var_time.extended_end_time
					if not var_time.extended_start_time:
						raise osv.except_osv(('Alert!'),('Please Enter The Extended Start Date.'))
					if not var_time.extended_end_time:
						raise osv.except_osv(('Alert!'),('Please Enter The Extended End Date.'))
					if not var_time.extended_reason:
						raise osv.except_osv(('Alert!'),('Please Enter The Reason for Extension.'))
					extended_start_time=var_time.extended_start_time
					extended_end_time=var_time.extended_end_time
					job_ed_time=k.job_end_time
					if extended_start_time < job_ed_time:
						raise osv.except_osv(('Alert!'),('Time should be greater than Schedule Time.'))
					if extended_end_time < job_ed_time:
						raise osv.except_osv(('Alert!'),('Time should be greater than Schedule Time.'))
					job_reason=var_time.extended_reason
					if k.erp_order_no:
						product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',k.erp_order_no)])
						invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',k.delivery_challan_no)])
						if invoice_id:
							self.pool.get('job.history').create(cr,uid,{'contract_no':k.job_id,'job_id':k.scheduled_job_id,'job_schedule_date':k.req_date_time,'job_reschedule_date':str(datetime.now()),
									'reason_for_rescheduling':job_reason,'technician_squad':assign,'job_status':'Job Extended','history_id':k.id,'job_start_date':extended_start_time1,'job_end_date':extended_date_time,'record_date':current_date,'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
						else:
							self.pool.get('job.history').create(cr,uid,{'contract_no':k.job_id,'job_id':k.scheduled_job_id,'job_schedule_date':k.req_date_time,'job_reschedule_date':str(datetime.now()),
									'reason_for_rescheduling':job_reason,'technician_squad':assign,'job_status':'Job Extended','history_id':k.id,'job_start_date':extended_start_time1,'job_end_date':extended_date_time,'record_date':current_date,'product_order_id':product_order_id[0]})
					if k.service_order_no:
						service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',k.service_order_no)])
						invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',k.service_order_no)])
						if invoice_id:
							self.pool.get('job.history').create(cr,uid,{'contract_no':k.job_id,'job_id':k.scheduled_job_id,'job_schedule_date':k.req_date_time,'job_reschedule_date':str(datetime.now()),
									'reason_for_rescheduling':job_reason,'technician_squad':assign,'job_status':'Job Extended','history_id':k.id,'job_start_date':extended_start_time1,'job_end_date':extended_date_time,'record_date':current_date,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
						else:
							self.pool.get('job.history').create(cr,uid,{'contract_no':k.job_id,'job_id':k.scheduled_job_id,'job_schedule_date':k.req_date_time,'job_reschedule_date':str(datetime.now()),
									'reason_for_rescheduling':job_reason,'technician_squad':assign,'job_status':'Job Extended','history_id':k.id,'job_start_date':extended_start_time1,'job_end_date':extended_date_time,'record_date':current_date,'service_order_id':service_order_id[0]})

			if k.job_extended_one2many:
				for ex_rec in k.job_extended_one2many:
					DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
					js= str(k.job_start_time)
					je = str(k.job_end_time)
					a,b,c= get_date_diff(js,je,config_time=True)
					hours = float(a) + float(b)/60 + float(c)/3600
					extend_start_time = str(ex_rec.extended_start_time)
					extend_end_time = str(ex_rec.extended_end_time)
					a1,b1,c1= get_date_diff(extend_start_time,extend_end_time,config_time=True)
					hours1 = float(a1) + float(b1)/60 + float(c1)/3600
					nh = hours+hours1
					job_start_time=datetime.strptime(k.job_start_time,DATETIME_FORMAT)
					time1=local_time.convert_time(job_start_time)
					job_end_time=datetime.strptime(k.job_end_time,DATETIME_FORMAT)
					time2=local_time.convert_time(job_end_time)
					extended_diff_time1=time2-time1
					extend_start_time=datetime.strptime(ex_rec.extended_start_time,DATETIME_FORMAT)
					extend_end_time=datetime.strptime(ex_rec.extended_end_time,DATETIME_FORMAT)
					extended_diff_time2=extend_end_time-extend_start_time
					total_extended_diff_time=extended_diff_time2+extended_diff_time1
					average1 = re.compile('[\:/]')
					avg1 = average1.split(str(total_extended_diff_time))
					print "%%%%%%%%%%%%%%%%%%%%%%%%",avg1
					val = ''
					cnt = 0
		
					for arr in avg1:
							cnt = cnt + 1
							if val == '':
								val = arr 
							else:
								if cnt < 3:
									val = val + ':' + arr
					cr.execute(("update res_scheduledjobs set job_duration_in_time=%s where id =%s"),(nh,k.id))
					ex_st_time=ex_rec.extended_start_time
					ex_ed_time=ex_rec.extended_end_time
					a,b,c= get_date_diff(ex_st_time,ex_ed_time,config_time=True)
					ex_hours = float(a) + float(b)/60 + float(c)/3600			
					if k.assigned_technician or k.assigned_squad:
						if k.manpower_line:

							str_1 = "select distinct (no_of_hours+"+str(ex_hours)+") from manpower_estimate where manpower_estimate_line in ( "+str(k.id)+")"
							print 'FFFFFFFFFF',str_1
							update_str_1 = "update manpower_estimate set no_of_hours = ("+str_1+") where manpower_estimate_line in ("+str(k.id)+");"
							cr.execute(update_str_1)
					#if k.assigned_squad:
					#	if k.manpower_line:
					#		for record in k.manpower_line:
					#			extra_hrs=record.no_of_hours
					#			total_hr=extra_hrs + ex_hours
					#			self.pool.get('manpower.estimate').write(cr,uid,record.id,{'no_of_hours':total_hr})
			
			tech_chemical_rec=self.pool.get('technician.chemical').search(cr,uid,[('job_id','=',k.scheduled_job_id)])
                        self.pool.get('technician.chemical').write(cr,uid,tech_chemical_rec,{'tech_date':start_date11})
					
		#self.write(cr,uid,ids,{'state':'extended',})
		#self.write(cr,uid,ids,{'bulk_bool':True,'job_extended_bool':True})
		#self.write(cr,uid,ids,{'extened_bool':False})
		self.write(cr,uid,ids,{'record_date':current_date,'state':'extended','bulk_bool':True,'job_start_date':start_date11,'job_end_date':start_date11,'job_extended_bool':True,'attrs_cancel':False,'attrs_extended':False,'attrs_reschedule':False,'job_start_time1':extended_start_time1,'extened_bool':False,'job_end_time1':extended_end_time1,'new_job_start_time1':extended_start_time1,'new_job_end_time1':extended_end_time1})
		#cr.execute("update res_scheduledjobs set job_start_date=cast(job_start_time1 as date)")
                #cr.execute("update res_scheduledjobs set job_end_date=cast(job_end_time1 as date)")
		self.write_jobs(cr,uid,ids,context=context) #zubair 22.12.2015 for .sql file on button click		
		return True

	def psd_job_extended_cancel(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'extened_bool':False,'attrs_extended':False})
		for i in self.browse(cr,uid,ids): 
			for k in i.job_extended_one2many:
					self.pool.get('job.extended').unlink(cr,uid,k.id)

	def psd_confirm(self,cr,uid,ids,context=None):
		current_date = datetime.now().date()		
		assign=job_id1=''
		squad_name1=''
		for o in self.browse(cr,uid,ids):
			job_id=o.job_id
			pms1=o.pms_search.id
			location_id2=o.location_id2
			address_on_fly=o.address_on_fly
			if o.assigned_technician :
				assign = o.assigned_technician.concate_name
				job_id1=o.job_id1+1
				technician_squad_merge1=o.technician_squad_merge
			else:
				technician_squad_merge1=''
			if o.assigned_squad :
				assign = o.assigned_squad.squad_name
				job_id1=o.job_id1+1
				squad_name1=o.sq_name_new

			if o.erp_order_no:
				product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',o.erp_order_no)])
				invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',o.delivery_challan_no)])
				if invoice_id:
					self.pool.get('job.history').create(cr,uid,{'contract_no':o.job_id,'job_id':o.scheduled_job_id,'job_schedule_date':o.req_date_time,'job_reschedule_date':str(datetime.now()),'job_start_date':o.job_start_time,'job_end_date':o.job_end_time,'record_date':current_date,
					'technician_squad':assign,'job_status':'Confirmed','history_id':o.id,'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
				else:
					self.pool.get('job.history').create(cr,uid,{'contract_no':o.job_id,'job_id':o.scheduled_job_id,'job_schedule_date':o.req_date_time,'job_reschedule_date':str(datetime.now()),'job_start_date':o.job_start_time,'job_end_date':o.job_end_time,'record_date':current_date,
					'technician_squad':assign,'job_status':'Confirmed','history_id':o.id,'product_order_id':product_order_id[0]})
			if o.service_order_no:
				service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',o.service_order_no)])
				invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',o.service_order_no)])
				if invoice_id:
					self.pool.get('job.history').create(cr,uid,{'contract_no':o.job_id,'job_id':o.scheduled_job_id,'job_schedule_date':o.req_date_time,'job_reschedule_date':str(datetime.now()),'job_start_date':o.job_start_time,'job_end_date':o.job_end_time,'record_date':current_date,
					'technician_squad':assign,'job_status':'Confirmed','history_id':o.id,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
				else:
					self.pool.get('job.history').create(cr,uid,{'contract_no':o.job_id,'job_id':o.scheduled_job_id,'job_schedule_date':o.req_date_time,'job_reschedule_date':str(datetime.now()),'job_start_date':o.job_start_time,'job_end_date':o.job_end_time,'record_date':current_date,
					'technician_squad':assign,'job_status':'Confirmed','history_id':o.id,'service_order_id':service_order_id[0]})

			search_record1 = self.search(cr,uid,[('name_contact','=',o.name_contact.id),('job_id','=',job_id),('job_id1','=',job_id1),('pms_search','=',pms1),('address_on_fly','=',address_on_fly)])
			if search_record1:
				for job1 in self.browse(cr,uid,search_record1):
					self.write(cr,uid,job1.id,{'prev_assign_tech':technician_squad_merge1,'prev_assign_squad':squad_name1})

			self.write(cr,uid,ids,{'record_date':current_date,'state': 'confirmed'})
		
		self.write_jobs(cr,uid,ids,context=context) #zubair 22.12.2015 for .sql file on button click	

		return True

	def psd_job_completion(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state': 'assigned_material'})
		res={}
		result={}
		i=0
		flag1=False
		flag2=False
		for job in self.browse(cr,uid,ids):
			if len(job.chemical) > 0:
				for line1 in job.chemical:
					if line1.quantityhand > 0:
						flag1=True
			else:
				flag1=True
			if len(job.equipment) > 0:
				for line2 in job.equipment:
					if line2.quantityhand_equipment > 0:
						flag2=True
			else:
				flag2=True
				
		if flag1==True and flag2==True:
			for job in self.browse(cr,uid,ids):
				for chemical in job.chemical:
					if chemical.quantityhand==0:
						self.pool.get('res.product').unlink(cr,uid,[chemical.id])
				for equipment in job.equipment:
					if equipment.quantityhand_equipment==0:
						self.pool.get('res.equipment').unlink(cr,uid,[equipment.id])

		for o in self.browse(cr,uid,ids):
			service=o.id
		product_scheduled = self.pool.get('res.scheduledjobs').search(cr,uid,[('id','=',service)])
		product_order=self.pool.get('res.product').search(cr,uid,[('chemical_id','=',service)])
		advance_value=[]
		for line in o.chemical:
		    advance_value.append([line.name.id,line.quantityhand])
		    x=line.name.id
		    y=line.quantityhand
		    product3 = self.pool.get('product.product').browse(cr,uid,ids)
		    for c in product3:
			  pr=c.id 
		    product4 = self.pool.get('product.product').search(cr,uid,[('id','=',line.name.id)])
		    advance_value1=[]
		    for val in self.pool.get('product.product').browse(cr,uid,product4):
				advance_value1.append([val.id,val.quantity_available])
				x1=val.id
				y1=val.quantity_available
		    advance_value_equ=[]
		for line in o.equipment:
		    advance_value_equ.append([line.name_equipment.id,line.quantityhand_equipment])
		    a=line.name_equipment.id
		    b=line.quantityhand_equipment
		    equipment2 = self.pool.get('product.product').search(cr,uid,[('id','=',line.name_equipment.id)])
		    advance_value_equ1=[]
		    for equipmnt in self.pool.get('product.product').browse(cr,uid,equipment2):
			  advance_value_equ1.append([equipmnt.id,equipmnt.quantity_available])
			  a1=equipmnt.id
			  b1=equipmnt.quantity_available
		assign=''
		for o in self.browse(cr,uid,ids):
			if o.assigned_technician :
				assign = o.assigned_technician.concate_name
			if o.assigned_squad :
				assign = o.assigned_squad.squad_name
			if o.erp_order_no:
				product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',o.erp_order_no)])
				invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',o.delivery_challan_no)])
				if invoice_id:
					self.pool.get('job.history').create(cr,uid,{'contract_no':o.job_id,'job_id':o.scheduled_job_id,'job_schedule_date':o.req_date_time,'job_reschedule_date':str(datetime.now()),
					'technician_squad':assign,'job_status':'Assigned Material','history_id':o.id,'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
				else:
					self.pool.get('job.history').create(cr,uid,{'contract_no':o.job_id,'job_id':o.scheduled_job_id,'job_schedule_date':o.req_date_time,'job_reschedule_date':str(datetime.now()),
					'technician_squad':assign,'job_status':'Assigned Material','history_id':o.id,'product_order_id':product_order_id[0]})
			if o.service_order_no:
				service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',o.service_order_no)])
				invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',o.service_order_no)])
				if invoice_id:
					self.pool.get('job.history').create(cr,uid,{'contract_no':o.job_id,'job_id':o.scheduled_job_id,'job_schedule_date':o.req_date_time,'job_reschedule_date':str(datetime.now()),
					'technician_squad':assign,'job_status':'Assigned Material','history_id':o.id,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
				else:	
					self.pool.get('job.history').create(cr,uid,{'contract_no':o.job_id,'job_id':o.scheduled_job_id,'job_schedule_date':o.req_date_time,'job_reschedule_date':str(datetime.now()),
					'technician_squad':assign,'job_status':'Assigned Material','history_id':o.id,'service_order_id':service_order_id[0]})
			return True

	def psd_job_extended_cancel(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'extened_bool':False,'attrs_extended':False})
		for i in self.browse(cr,uid,ids): 
			for k in i.job_extended_one2many:
					self.pool.get('job.extended').unlink(cr,uid,k.id)

	def psd_job_extended(self,cr,uid,ids,context=None):
		current_date = datetime.now().date()
		self.write(cr,uid,ids,{'extened_bool':True,'record_date':current_date,'attrs_extended':True})
		self.write_jobs(cr,uid,ids,context=context)
		return True

res_scheduledjobs()

class product_transfer(osv.osv):
	_inherit="product.transfer"
	_columns={
		'product_data':fields.many2one('res.scheduledjobs','Product Data'),
		'consumption_id':fields.many2one('consumption.report.detail',string="Consumption ID"),
	}

product_transfer()


class res_partner(osv.osv):
	_inherit="res.partner"
	_columns={
		'is_transfered':fields.boolean('Is Transfered'),
	}
res_partner()