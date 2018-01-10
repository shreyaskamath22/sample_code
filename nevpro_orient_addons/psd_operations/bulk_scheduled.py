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
import local_time
import calendar
import datetime as dt
import xmlrpclib
from python_code.dateconversion import *
import python_code.dateconversion as py_date
import re
import time
import os
from openerpsync.sockconnect import connection as sockConnect


class bulk_schedule_jobs(osv.osv):
	_inherit= "bulk.schedule.jobs"
	_columns= {
		'job_category':fields.selection([('service','Service Order'),('delivery','Product Order'),('adhoc_service','Adhoc-Service Order'),('adhoc_product','Adhoc-Product Order'),('adhoc_service_complaint','Adhoc - Service Complaint'),('product_complaint','Adhoc - Product Complaint')],'Job Type'),
		}
bulk_schedule_jobs()


class bulk_reschedule(osv.osv):
    _inherit="bulk.reschedule"

    def psd_onchange_select_all1(self, cr, uid, ids, select_all1,reschedule_ids):
		value_list = val = []
		if select_all1:
			for i in reschedule_ids:
				for res in self.pool.get('bulk.reschedule').browse(cr,uid,[i[1]]):
					val.extend([(1,i[1],{'select_any':True})])
			print val
		if not select_all1:
			for i in reschedule_ids:
				for res in self.pool.get('bulk.reschedule').browse(cr,uid,[i[1]]):
					val.extend([(1,i[1],{'select_any':False})])
			print val
		return {'value':{'reschedule_ids':val}}

    '''def _tech_assign(self,cr,uid,ids,context=None):
		for a in self.pool.get('bulk.reschedule.one2many').search(cr,uid,[('select_any','=',True)]):
			for b in self.browse(cr,uid,a):
				print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5',b.tech_name,b.reassign_tech'''
    _columns = {
	'name':fields.char('Name', size=300),
	'reschedule_ids':fields.one2many('bulk.reschedule.one2many','result_id','Jobs',size=32),
        'tech_name':fields.many2one('hr.employee','Technician',size=32),
        'squad_name':fields.many2one('res.define.squad','Squad Name',size=32),
        'from_date': fields.date('Job Date From',size=32),
        'to_date':fields.date('Job Date To',size=32),
	'reassign_tech':fields.many2one('bulk.technician','Reassign To',size=32),
	'select_all1':fields.boolean('Select all'),
	#'assigntech':fields.function(_tech_assign,type='boolean',string='Assign'),
    }

    '''def assigntech(self,cr,uid,ids,context = None):
		tech111 = ''
		
		for i in self.browse(cr,uid,ids):
			if i.reschedule_ids:
				for j in i.reschedule_ids:
					if not j.select_any :
						self.pool.get('bulk.reschedule.one2many').unlink(cr,uid,j.id)
						#raise osv.except_osv(('Alert!'),('Please select The Records !'))
					if j.select_any:
						customer_name = j.name
						contract_no = j.job_id
						scheduled_job_id = j.scheduled_job_id
						state = j.state
						job_start_time=j.job_start_time
						job_end_time=j.job_end_time
						assigned_technician = j.assigned_technician.id
						new_technician = i.reassign_tech.id
						assigned_squad = j.assigned_squad
						if i.reassign_tech.emp_code:
							new_tech_empcode = i.reassign_tech.emp_code
							search_tech = self.pool.get('hr.employee').search(cr,uid,[('emp_code','=',new_tech_empcode)])
							time_check = self.pool.get('res.scheduledjobs').search(cr,uid,[('assigned_technician','=',search_tech)])
							for i in self.pool.get('res.scheduledjobs').browse(cr,uid,time_check):
								if(i.job_start_time >= job_start_time and i.job_start_time <= job_end_time) or (i.job_end_time >= job_start_time and i.job_end_time <= job_end_time) or (i.job_start_time <= job_start_time and i.job_end_time >= job_start_time):
									raise osv.except_osv(('Alert!'),('Already Assigned !'))
							#print "DDDDDDDDD",time_check
							#print ret
							if time_check:
								for search_tech1 in self.pool.get('hr.employee').browse(cr,uid,search_tech):
									global tech111
									tech111=search_tech1.id
									tech_first_name=tech_middle_name=tech_middle_name = ''
									if search_tech1.name:
										tech_first_name=search_tech1.name
									else :
										tech_first_name=''
									if search_tech1.middle_name:
										tech_middle_name=search_tech1.middle_name
									else:
										tech_middle_name=''
									if search_tech1.last_name:
										tech_last_name=search_tech1.last_name
									else:
										tech_last_name=''
									tech_name123=tech_first_name+ ' ' +tech_middle_name+ ' ' +tech_last_name
								print 'kkkkkkkkkkkkkkkkkkkkkkkkkk',assigned_technician,job_start_time,job_end_time
								DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
								ds=datetime.strptime(job_start_time,DATETIME_FORMAT)
								de=datetime.strptime(job_end_time,DATETIME_FORMAT)
								ds=local_time.convert_time(ds)
								de=local_time.convert_time(de)
								ds=ds.strftime(DATETIME_FORMAT)
								de=de.strftime(DATETIME_FORMAT)
								#print local_time.convert_time()
								print 'ppppppppppppppppppppppppppppp',ds,de,type(ds)
								#print uuuuuuuuuuuuuuuuuuu
								print 'uuuuuuuuuuuuuuuuuuu',tech111
								search_id1=self.pool.get('technician.past.record').search(cr,uid,[('technician','=',assigned_technician),('job_start','=',ds),('job_end','=',de)])
								print "000000000000000000000000000000000000000",search_id1,ds,de,assigned_technician
								#print lllllllllllllllllllllll
								if search_id1:
									for val1 in self.pool.get('technician.past.record').browse(cr,uid,search_id1):
										print 'iiiiiiiiiiiiiiiiiiiiii',val1
										past_record_undate=self.pool.get('technician.past.record').write(cr,uid,val1.id,{'technician':tech111})					
										print 'uuuuuuuuuuuuuuuuuuuuuuuuuu',val1.id,tech111
								jobs_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('name','=',customer_name),('job_id','=',contract_no),('scheduled_job_id','=',scheduled_job_id),('state','=',state),('assigned_technician','=',assigned_technician)])
								print 'iiiiiiiiiiiiiiiiiiiooooooo',assigned_technician
								a=self.pool.get('res.scheduledjobs').write(cr, uid, jobs_id, {'assigned_technician':search_tech[0],'technician_squad_merge':tech_name123,'assign_resource_id':'','assign_resource_id1':'','assigned_squad':0,'sq_name_new1':'','sq_name_new2':tech_name123,'sq_name_new':''},context={'default_search_record':True})#,'state':'scheduled'
								b=self.pool.get('bulk.reschedule.one2many').write(cr,uid,j.id,{'assigned_technician':tech111})
								#self.pool.get('res.scheduledjobs').write(cr,uid,jobs_id,{'technician_job_merge':i.reassign_tech.name,'sq_name_new2':i.reassign_tech.name})
								#print '****   ',customer_name,'****   ',contract_no,'****   ',scheduled_job_id,jobs_id,i.reassign_tech.name,a,b,past_record_undate
							
								
						else :
							squad_name = i.reassign_tech.name
							squad_id=self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',squad_name)])
							if squad_id:
								print squad_id
								flag1=0
								for k in self.pool.get('res.define.squad').browse(cr,uid,squad_id):
									for l in k.tech2:
										print 
										hr_emp_id = self.pool.get('hr.employee').search(cr,uid,[('id','=',l.technician_id.id)])
										
										if hr_emp_id:
											
											for hr_emp in self.pool.get('hr.employee').browse(cr,uid,hr_emp_id):
												tech_id = hr_emp.id
												print 'ooooooooooooooooooooooooooooooooooooooooooo%%%%%%%%%%%%',l.name,hr_emp.id
												time_check1 = self.pool.get('res.scheduledjobs').search(cr,uid,[('assigned_technician','=',tech_id)])
												for i in self.pool.get('res.scheduledjobs').browse(cr,uid,time_check1):
													if(i.job_start_time >= job_start_time and i.job_start_time <= job_end_time) or (i.job_end_time >= job_start_time and i.job_end_time <= job_end_time) or (i.job_start_time <= job_start_time and i.job_end_time >= job_start_time):
														raise osv.except_osv(('Alert!'),('Technician in squad already assigned !'))
									
													else:													
														jobs_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('name','=',customer_name),('job_id','=',contract_no),('scheduled_job_id','=',scheduled_job_id),('state','=',state),('assigned_technician','=',assigned_technician)])	
														
														
														if jobs_id:
															self.pool.get('res.scheduledjobs').write(cr, uid,jobs_id, {'technician_squad_merge':squad_name,'assign_resource_id':'','assign_resource_id1':'','assigned_squad':0,'sq_name_new1':squad_name,'sq_name_new2':squad_name,'sq_name_new':''},context={'default_search_record':True})							
												DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
												ds=datetime.strptime(job_start_time,DATETIME_FORMAT)
												de=datetime.strptime(job_end_time,DATETIME_FORMAT)
												ds=local_time.convert_time(ds)
												de=local_time.convert_time(de)
												ds=ds.strftime(DATETIME_FORMAT)
												de=de.strftime(DATETIME_FORMAT)	
																
												x=self.pool.get('technician.past.record').search(cr,uid,[('technician','=',assigned_technician),('job_start','=',ds,),('job_end','=',de)])
												print 'ttttttttttttttttttttttttttttttt',x
												if x:
													for y in self.pool.get('technician.past.record').browse(cr,uid,x):
														print 'yyyyyyyyyyyy',hr_emp,flag1
														if flag1==0:
															self.pool.get('technician.past.record').write(cr,uid,y.id,{'technician':hr_emp.id})
															job_start=y.job_start
															job_end=y.job_end
															service_area=y.service_area
															address=y.address
															date=y.date

												if flag1>0:
													self.pool.get('technician.past.record').create(cr,uid,{'job_start':job_start,'job_end':job_end,'service_area':service_area,'address':address,'technician':hr_emp.id,'date':date})
													
												flag1=flag1+1
												print 'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk',assigned_technician,flag1
												assigned_technician=hr_emp.id
												print 'gggggggggggggggggggggggggggggggggggggggggg',assigned_technician
												
													
											
								#print 'iiiiiiiiiiiiiiiiiiiiii',search_id2,hr_emp_id
								#print yyyyyyyyyyyyyyyyy
								
														
								print squad_name
								#print llllllllllllllllllllll
							
							#if vall.assigned_squad:
							#	assigned_squad1=vall.assigned_squad.squad_name
							#search_squad = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',assigned_squad1)])
							
					else:
						print "Pass"
											
		for line in o.technician_line:
			line_id=line.id					
			res_jobs=self.pool.get('res.scheduledjobs').search(cr,uid,[('id', '=',line_id)])
			for res in self.pool.get('res.scheduledjobs').browse(cr,uid,res_jobs):
				self.pool.get('res.scheduledjobs').write(cr, uid, res.id, {'assigned_technician':0,'assigned_squad':0},context={'default_search_record':True})
		
		return True'''

    def psd_assigntech(self,cr,uid,ids,context = None):
		for ro in self.browse(cr,uid,ids):
				for line1 in ro.reschedule_ids:
					current_date=datetime.now().date()
					if line1.select_any:
						DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
						start_date_date = datetime.strptime(line1.job_start_time,DATETIME_FORMAT).date()
						if ro.reassign_tech:
								if not ro.reassign_tech.squad:
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
									search_emp = self.pool.get('hr.employee').search(cr,uid,[('emp_code','=',ro.reassign_tech.emp_code),('role_selection','=','executor')])
									if search_emp:
										for emp in self.pool.get('hr.employee').browse(cr,uid,search_emp):
											emp_code = emp.emp_code
											emp_id = emp.id
											if emp.creation_type != 'extra_emp':
												if start_date_date == current_date:
													search = self.pool.get('hr.attendence.new').search(cr,uid,[('date','=',start_date_date),('employee_name','=',emp_id),('leaves','in',leave_p)])
													print "OOOOOOOOOOOOOOOOOOOOOOOOOOO",search,emp.creation_type
													if search == [] :
														raise osv.except_osv(('Alert!'),('Technician '+ro.reassign_tech.name+ ' is Not Available '))
												else:
													search = self.pool.get('hr.attendence.new').search(cr,uid,[('date','=',start_date_date),('employee_name','=',emp_id),('leaves','in',leave_a)])
													if search != [] :
															raise osv.except_osv(('Alert!'),('Technician '+ro.reassign_tech.name+ ' is Not Available'))


								else:
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

									squad_srh = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',ro.reassign_tech.name)])
									if squad_srh:
										squad_name = ''
			
										for squad in self.pool.get('res.define.squad').browse(cr,uid,squad_srh):
												squad_array = []
												squad_name = squad.squad_name
												for val in squad.tech2:
													technician_id = val.technician_id.id
													squad_array.append(technician_id)
												for sqd in squad_array:
													srh_hr = self.pool.get('hr.employee').search(cr,uid,[('id','=',sqd)])
													for emp1 in self.pool.get('hr.employee').browse(cr,uid,srh_hr):
														if emp1.creation_type != 'extra_emp': 
															if start_date_date == current_date: 
																attendence = self.pool.get('hr.attendence.new').search(cr,uid,[('date','=',start_date_date),('employee_name','=',emp1.id),('leaves','in',leave_p)])
																if attendence == []:
																		raise osv.except_osv(('Alert!'),('Technicians of Squad '+ro.reassign_tech.name+ ' is Not Available '))

															else:
																attendence = self.pool.get('hr.attendence.new').search(cr,uid,[('date','=',start_date_date),('employee_name','=',emp1.id),('leaves','in',leave_a)])
																if attendence != [] :
																		raise osv.except_osv(('Alert!'),('Technicians of Squad '+ro.reassign_tech.name+ ' is Not Available '))
											



					start_time=end_time=pre_full_name=tt1=tt2=''
					start_date=line1.job_start_time
					end_date=line1.job_end_time
					if line1.select_any:
						if not ro.reassign_tech.squad:
							tech_emp_code=ro.reassign_tech.emp_code
							hr_emp_id=self.pool.get('hr.employee').search(cr,uid,[('emp_code','=',tech_emp_code)])
							for i in self.pool.get('hr.employee').browse(cr,uid,hr_emp_id):
								f_name = i.name if i.name else ''
								s_name = i.middle_name if i.middle_name else ''
								l_name = i.last_name if i.last_name else ''
								temp_name = [f_name,s_name,l_name]
								pre_full_name = ' '.join(filter(bool,temp_name))
								search_job_id=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed','extended'))])
						
								#if (((start_time>=o11.job_start_time)and(start_time<=o11.job_end_time))or((end_time>=o11.job_start_time)and(end_time<=o11.job_end_time))or((start_time<=o11.job_start_time)and(end_time>=o11.job_start_time)))
								for av in self.pool.get('res.scheduledjobs').browse(cr,uid,search_job_id):
									if av.assigned_technician:
										if av.assigned_technician.id == i.id:
											if (av.job_start_time >= start_date and av.job_start_time <= end_date) or (av.job_end_time >= start_date and av.job_end_time <= end_date) or (av.job_start_time <= start_date and av.job_end_time >= start_date):
													tech_job_id=av.scheduled_job_id
													DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
													t1=datetime.strptime(av.job_start_time,DATETIME_FORMAT)
													start_time=local_time.convert_time(t1).time()
													start_tm=str(start_time)
													ti1=start_tm.split(':')
													tt1=ti1[0]+':'+ti1[1]
													t2=datetime.strptime(av.job_end_time,DATETIME_FORMAT)
													end_time=local_time.convert_time(t2).time()
													end_tm=str(end_time)
													ei1=end_tm.split(':')
													tt2=ei1[0]+':'+ei1[1]
													print "technician id",search_job_id,start_time,end_time
						
													if search_job_id:
														raise osv.except_osv(('Alert!'),('Technician '+ro.reassign_tech.name+ ' is Already assigned between ' +tt1+' and '+tt2+' for job '+tech_job_id+'.'))
									else:
										squad_tech2=[]
										squad_search22 = self.pool.get('res.define.squad').search(cr,uid,[('id','=',av.assigned_squad.id)])
										for squad11 in self.pool.get('res.define.squad').browse(cr,uid,squad_search22):
											for tech1 in squad11.tech2:
												squad_tech2.append(tech1.technician_id.id)
										if i.id in squad_tech2:
												if (av.job_start_time >= start_date and av.job_start_time <= end_date) or (av.job_end_time >= start_date and av.job_end_time <= end_date) or (av.job_start_time <= start_date and av.job_end_time >= start_date):
																tech_job_id=av.scheduled_job_id
																DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
																t1=datetime.strptime(av.job_start_time,DATETIME_FORMAT)
																start_time=local_time.convert_time(t1).time()
																start_tm=str(start_time)
																ti1=start_tm.split(':')
																tt1=ti1[0]+':'+ti1[1]
																t2=datetime.strptime(av.job_end_time,DATETIME_FORMAT)
																end_time=local_time.convert_time(t2).time()
																end_tm=str(end_time)
																ei1=end_tm.split(':')
																tt2=ei1[0]+':'+ei1[1]
																raise osv.except_osv(('Alert!'),('The Technician '+ro.reassign_tech.name+ ' is Already assigned in Squad between'+tt1+' and '+tt2+' for job '+tech_job_id+'.'))	
								
						else :
						
								s_name=ro.reassign_tech.name
								search_job_id1=self.pool.get('res.scheduledjobs').search(cr,uid,[('state','in',('scheduled','confirmed','extended'))])
								if search_job_id1:
									for av in self.pool.get('res.scheduledjobs').browse(cr,uid,search_job_id1):
										if av.assigned_squad:
											if av.sq_name_new==s_name:
												if (av.job_start_time >= start_date and av.job_start_time <= end_date) or (av.job_end_time >= start_date and av.job_end_time <= end_date) or (av.job_start_time <= start_date and av.job_end_time >= start_date):
													tech_job_id=av.scheduled_job_id
													DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
													t1=datetime.strptime(av.job_start_time,DATETIME_FORMAT)
													start_time=local_time.convert_time(t1).time()
													start_tm=str(start_time)
													ti1=start_tm.split(':')
													tt1=ti1[0]+':'+ti1[1]
													t2=datetime.strptime(av.job_end_time,DATETIME_FORMAT)
													end_time=local_time.convert_time(t2).time()
													end_tm=str(end_time)
													ei1=end_tm.split(':')
													tt2=ei1[0]+':'+ei1[1]
													raise osv.except_osv(('Alert!'),('The Squad '+ro.reassign_tech.name+ ' is Already assigned between'+tt1+' and '+tt2+' for job '+tech_job_id+'.'))
											else:
												squad_tech1=[]
												squad_search11 = self.pool.get('res.define.squad').search(cr,uid,[('id','=',av.assigned_squad.id)])
												for squad1 in self.pool.get('res.define.squad').browse(cr,uid,squad_search11):
													for tech1 in squad1.tech2:
														squad_tech1.append(tech1.technician_id.id)		
												if squad_tech1:
													search_sq = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',s_name)])
													for sq in self.pool.get('res.define.squad').browse(cr,uid,search_sq):
														for tech in sq.tech2:
															if tech.technician_id.id in squad_tech1:
																if (av.job_start_time >= start_date and av.job_start_time <= end_date) or (av.job_end_time >= start_date and av.job_end_time <= end_date) or (av.job_start_time <= start_date and av.job_end_time >= start_date):
																	tech_job_id=av.scheduled_job_id
																	DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
																	t1=datetime.strptime(av.job_start_time,DATETIME_FORMAT)
																	start_time=local_time.convert_time(t1).time()
																	start_tm=str(start_time)
																	ti1=start_tm.split(':')
																	tt1=ti1[0]+':'+ti1[1]
																	t2=datetime.strptime(av.job_end_time,DATETIME_FORMAT)
																	end_time=local_time.convert_time(t2).time()
																	end_tm=str(end_time)
																	ei1=end_tm.split(':')
																	tt2=ei1[0]+':'+ei1[1]
																	raise osv.except_osv(('Alert!'),('The Technicians of  '+ro.reassign_tech.name+ ' is Already assigned between'+tt1+' and '+tt2+' for job '+tech_job_id+'.')) 

										else:
											technician_tech1=[]
											technician_tech1.append(av.assigned_technician.id)
											search_sq_search = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',s_name)])
											for sq11 in self.pool.get('res.define.squad').browse(cr,uid,search_sq_search):
														for tech in sq11.tech2:
															if tech.technician_id.id in technician_tech1:
																	if (av.job_start_time >= start_date and av.job_start_time <= end_date) or (av.job_end_time >= start_date and av.job_end_time <= end_date) or (av.job_start_time <= start_date and av.job_end_time >= start_date):
																		tech_job_id=av.scheduled_job_id
																		DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
																		t1=datetime.strptime(av.job_start_time,DATETIME_FORMAT)
																		start_time=local_time.convert_time(t1).time()
																		start_tm=str(start_time)
																		ti1=start_tm.split(':')
																		tt1=ti1[0]+':'+ti1[1]
																		t2=datetime.strptime(av.job_end_time,DATETIME_FORMAT)
																		end_time=local_time.convert_time(t2).time()
																		end_tm=str(end_time)
																		ei1=end_tm.split(':')
																		tt2=ei1[0]+':'+ei1[1]
																		raise osv.except_osv(('Alert!'),('The Technician of  '+ro.reassign_tech.name+ ' is Already assigned between'+tt1+' and '+tt2+' for job '+tech_job_id+'.'))


		for v in self.browse(cr,uid,ids):
			current_date= datetime.now().date()
			squad_full_detail=squad_full_detail11=''
			if v.reschedule_ids:
				for j in v.reschedule_ids:
					if not j.select_any:
						self.pool.get('bulk.reschedule.one2many').unlink(cr,uid,j.id)
					if j.select_any:
						if not v.reassign_tech:
							raise osv.except_osv(('Alert!'),('Please Select Technician/Squad to Reassign'))
						assigned_technician1=tech111=''
						assigned_squad1=''
						search_id=''
						if not v.reassign_tech.squad:
							search_tech = self.pool.get('hr.employee').search(cr,uid,[('emp_code','=',v.reassign_tech.emp_code)])
							for search_tech1 in self.pool.get('hr.employee').browse(cr,uid,search_tech):
								tech111=search_tech1.id

							#search_id=self.pool.get('bulk.reschedule.one2many').search(cr,uid,[('id','=',one2many_id)])
							#if search_id:
							#for val in self.pool.get('bulk.reschedule.one2many').browse(cr,uid,search_id):
							if j.assigned_technician:
										assigned_technician1=j.assigned_technician.id
										print "(((((((((((((((((",assigned_technician1
										print "assigned_tech_name",j.assigned_technician.name
										job_start_time=j.job_start_time
										job_end_time=j.job_end_time
										DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
										import pytz
										time_zone='Asia/Kolkata'
										tz = pytz.timezone(time_zone)

										assigned_technician=j.assigned_technician.id
										t1=datetime.strptime(j.job_start_time,DATETIME_FORMAT)
										tzoffset = tz.utcoffset(t1)
										job_start_timee= t1 + tzoffset #local_time.convert_time(t1)
										job_start_timee1=job_start_timee.date()
										print "))))))))))))))))))))))))",job_start_timee1
										t2=datetime.strptime(j.job_end_time,DATETIME_FORMAT)
										tzoffset = tz.utcoffset(t1)
										job_end_timee=t2 + tzoffset#local_time.convert_time(t2)
										search_id1=self.pool.get('technician.past.record').search(cr,uid,[('technician','=',assigned_technician1),('job_start','=',str(job_start_timee)),('job_end','=',str(job_end_timee))],)
										if search_id1:
											for val1 in self.pool.get('technician.past.record').browse(cr,uid,search_id1):
												print ")))))))))))))))))",tech111
												past_record_undate=self.pool.get('technician.past.record').write(cr,uid,val1.id,{'technician':tech111})
							if j.assigned_squad:
										DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
										import pytz
										time_zone='Asia/Kolkata'
										tz = pytz.timezone(time_zone)

										assigned_technician=j.assigned_technician.id
										t1=datetime.strptime(j.job_start_time,DATETIME_FORMAT)
										tzoffset = tz.utcoffset(t1)
										job_start_timee= t1 + tzoffset #local_time.convert_time(t1)
										job_start_timee1=job_start_timee.date()
										print "))))))))))))))))))))))))",job_start_timee1
										t2=datetime.strptime(j.job_end_time,DATETIME_FORMAT)
										tzoffset = tz.utcoffset(t1)
										job_end_timee=t2 + tzoffset#local_time.convert_time(t2)
										service_area=j.service_area
										assigned_squad1=j.assigned_squad.squad_name
										search_squad = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',assigned_squad1)])
										if search_squad:
											for i in self.pool.get('res.define.squad').browse(cr,uid,search_squad):
												for pp in i.tech2 :
													technician123 = pp.technician_id.id
													search_id3=self.pool.get('technician.past.record').search(cr,uid,[('technician','=',technician123)],order="id desc",limit=1)
													if search_id3:
														for val1 in self.pool.get('technician.past.record').browse(cr,uid,search_id3):
																self.pool.get('technician.past.record').unlink(cr,uid,val1.id)

										search_rec = self.pool.get('res.scheduledjobs').search(cr,uid,[('assigned_squad','=',j.assigned_squad.id),('scheduled_job_id','=',j.scheduled_job_id)])
										if search_rec:
											for y in self.pool.get('res.scheduledjobs').browse(cr,uid,search_rec):
												search_squad1234 = self.pool.get('hr.employee').search(cr,uid,[('emp_code','=',v.reassign_tech.emp_code)])
												if search_squad1234:
														for k in self.pool.get('hr.employee').browse(cr,uid,search_squad1234):
																	name = k.id
																	self.pool.get('technician.past.record').create(cr,uid,{'technician':name,'job_start':str(job_start_timee),'job_end':str(job_end_timee),'service_area':service_area if service_area else '','address':y.address_on_fly if y.address_on_fly else '','date':job_start_timee1})	
						
						else:
							'''search_id123=self.pool.get('bulk.reschedule.one2many').search(cr,uid,[('id','=',one2many_id)])
							if search_id123:
								for vall in self.pool.get('bulk.reschedule.one2many').browse(cr,uid,search_id123):
									if vall.assigned_squad:
										assigned_squad1=vall.assigned_squad.squad_name
										search_squad = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',assigned_squad1)])
										if search_squad:
											for i in self.pool.get('res.define.squad').browse(cr,uid,search_squad):
												for pp in i.tech2 :
													technician123 = pp.technician_id.id
													search_id3=self.pool.get('technician.past.record').search(cr,uid,[('technician','=',technician123)],order="id desc",limit=1)
													if search_id3:
															for val1 in self.pool.get('technician.past.record').browse(cr,uid,search_id3):
																search_squad1234 = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',o.technician_select.name)])
																if search_squad1234:
																	for k in self.pool.get('res.define.squad').browse(cr,uid,search_squad1234):
																		for kk in k.tech2 :
																			name = kk.technician_id.id
																			past_record_undate1=self.pool.get('technician.past.record').write(cr,uid,val1.id,{'technician':name})'''

							#search_id123=self.pool.get('bulk.reschedule.one2many').search(cr,uid,[('id','=',one2many_id)])
							#if search_id123:
								#for vall in self.pool.get('bulk.reschedule.one2many').browse(cr,uid,search_id123):
							if j.assigned_squad:
										DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
										import pytz
										time_zone='Asia/Kolkata'
										tz = pytz.timezone(time_zone)

										assigned_technician=j.assigned_technician.id
										t1=datetime.strptime(j.job_start_time,DATETIME_FORMAT)
										tzoffset = tz.utcoffset(t1)
										job_start_timee= t1 + tzoffset #local_time.convert_time(t1)
										job_start_timee1=job_start_timee.date()
										print "))))))))))))))))))))))))",job_start_timee1
										t2=datetime.strptime(j.job_end_time,DATETIME_FORMAT)
										tzoffset = tz.utcoffset(t1)
										job_end_timee=t2 + tzoffset#local_time.convert_time(t2)
										service_area=j.service_area
										assigned_squad1=j.assigned_squad.squad_name
										print ")))))))))))))))))))))))))))))))))))))",j.assigned_squad.id,j.scheduled_job_id
										search_rec = self.pool.get('res.scheduledjobs').search(cr,uid,[('assigned_squad','=',j.assigned_squad.id),('scheduled_job_id','=',j.scheduled_job_id)])
										if search_rec:
											for y in self.pool.get('res.scheduledjobs').browse(cr,uid,search_rec):
												search_squad = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',assigned_squad1)])
												if search_squad:
													for i in self.pool.get('res.define.squad').browse(cr,uid,search_squad):
														for pp in i.tech2 :
															technician123 = pp.technician_id.id
															search_id3=self.pool.get('technician.past.record').search(cr,uid,[('technician','=',technician123),('job_start','=',str(job_start_timee)),('job_end','=',str(job_end_timee))])
											
															if search_id3:
																	for val1 in self.pool.get('technician.past.record').browse(cr,uid,search_id3):
																		self.pool.get('technician.past.record').unlink(cr,uid,val1.id)
												search_squad1234 = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',v.reassign_tech.name)])
												if search_squad1234:
														for k in self.pool.get('res.define.squad').browse(cr,uid,search_squad1234):
															for kk in k.tech2 :
																	name = kk.technician_id.id
																	self.pool.get('technician.past.record').create(cr,uid,{'technician':name,'job_start':str(job_start_timee),'job_end':str(job_end_timee),'service_area':service_area if service_area else '','address':y.address_on_fly if y.address_on_fly else '','date':job_start_timee1})
							if j.assigned_technician:
										DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
										import pytz
										time_zone='Asia/Kolkata'
										tz = pytz.timezone(time_zone)

										assigned_technician=j.assigned_technician.id
										t1=datetime.strptime(j.job_start_time,DATETIME_FORMAT)
										tzoffset = tz.utcoffset(t1)
										job_start_timee= t1 + tzoffset #local_time.convert_time(t1)
										job_start_timee1=job_start_timee.date()
										print "))))))))))))))))))))))))",job_start_timee1
										t2=datetime.strptime(j.job_end_time,DATETIME_FORMAT)
										tzoffset = tz.utcoffset(t1)
										job_end_timee=t2 + tzoffset#local_time.convert_time(t2)
										assigned_technician1=j.assigned_technician.id
										service_area=j.service_area
										search_squad = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',v.reassign_tech.name)])
										if search_squad:
											for i in self.pool.get('res.define.squad').browse(cr,uid,search_squad):
												for pp in i.tech2 :
													technician123 = pp.technician_id.id
													search_id3=self.pool.get('technician.past.record').search(cr,uid,[('technician','=',assigned_technician1),('job_start','=',str(job_start_timee)),('job_end','=',str(job_end_timee))],)
													if search_id3:
															for val1 in self.pool.get('technician.past.record').browse(cr,uid,search_id3):
																self.pool.get('technician.past.record').unlink(cr,uid,val1.id)
										search_rec = self.pool.get('res.scheduledjobs').search(cr,uid,[('assigned_technician','=',j.assigned_technician.id),('scheduled_job_id','=',j.scheduled_job_id)])
										if search_rec:
											for y in self.pool.get('res.scheduledjobs').browse(cr,uid,search_rec):
												search_squad1 = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',v.reassign_tech.name)])
												if search_squad1:
													for i in self.pool.get('res.define.squad').browse(cr,uid,search_squad1):
														for pp in i.tech2 :
															name = pp.technician_id.id
															self.pool.get('technician.past.record').create(cr,uid,{'technician':name,'job_start':str(job_start_timee),'job_end':str(job_end_timee),'service_area':service_area if service_area else '','address':y.address_on_fly if y.address_on_fly else '','date':job_start_timee1})
						'''for line in self.pool.get('res.scheduledjobs').search(cr,uid,[('id','=',hr_emp)]):
							line_id=line.id					
							res_jobs=self.pool.get('res.scheduledjobs').search(cr,uid,[('id', '=',line_id)])
							for res in self.pool.get('res.scheduledjobs').browse(cr,uid,res_jobs):
								self.pool.get('res.scheduledjobs').write(cr, uid, res.id, {'assigned_technician':0,'assigned_squad':0},context={'default_search_record':True})'''
########################################################23apr15##########################################################################

						srch_one2many=self.pool.get('bulk.reschedule.one2many').search(cr,uid,[('scheduled_job_id','=',j.scheduled_job_id)])
						if srch_one2many :
							for j_one2many in self.pool.get('bulk.reschedule.one2many').browse(cr,uid,srch_one2many):
								if v.reassign_tech.squad == False:
									emp_code=v.reassign_tech.emp_code
									search_tech = self.pool.get('hr.employee').search(cr,uid,[('emp_code','=',emp_code)])

									self.pool.get('bulk.reschedule.one2many').write(cr,uid,j_one2many.id,{'assigned_technician':search_tech[0],'assigned_squad':''})		
								if v.reassign_tech.squad == True:
									technician_array =[]
									
									search_sq_name1=self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',v.reassign_tech.name)])
									
									self.pool.get('bulk.reschedule.one2many').write(cr,uid,j_one2many.id,{'assigned_squad':search_sq_name1[0],'assigned_technician':''})
#####################################################################################################################################	


						search_job_id = self.pool.get('res.scheduledjobs').search(cr,uid,[('scheduled_job_id','=',j.scheduled_job_id)])
						if search_job_id:
							for i in self.pool.get('res.scheduledjobs').browse(cr,uid,search_job_id):
								if v.reassign_tech.squad == False:
									emp_code=v.reassign_tech.emp_code
									search_tech = self.pool.get('hr.employee').search(cr,uid,[('emp_code','=',emp_code)])
									self.pool.get('res.scheduledjobs').write(cr, uid, i.id, {'assigned_technician':search_tech[0],'tech_id':search_tech[0],'technician_squad_merge':v.reassign_tech.name,'assign_resource_id':'','assign_resource_id1':'','assigned_squad':0,'sq_name_new1':'','sq_name_new2':j.name,'sq_name_new':''})#,'state':'scheduled'
									if j.erp_order_no:
										product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',j.erp_order_no)])
										invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',j.delivery_challan_no)])
										if invoice_id:
											self.pool.get('job.history').create(cr,uid,{'contract_no':j.job_id,'job_id':j.scheduled_job_id,'job_reschedule_date':datetime.now(),'technician_squad':v.reassign_tech.name,'job_status':'Technician Reassigned','history_id':i.id,'job_start_date':j.job_start_time,'job_end_date':j.job_end_time,'record_date':current_date,	'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
										else:
											self.pool.get('job.history').create(cr,uid,{'contract_no':j.job_id,'job_id':j.scheduled_job_id,'job_reschedule_date':datetime.now(),'technician_squad':v.reassign_tech.name,'job_status':'Technician Reassigned','history_id':i.id,'job_start_date':j.job_start_time,'job_end_date':j.job_end_time,'record_date':current_date,	'product_order_id':product_order_id[0]})
									if j.service_order_no:
										service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',j.service_order_no)])
										invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',j.service_order_no)])
										if invoice_id:
											self.pool.get('job.history').create(cr,uid,{'contract_no':j.job_id,'job_id':j.scheduled_job_id,'job_reschedule_date':datetime.now(),'technician_squad':v.reassign_tech.name,'job_status':'Technician Reassigned','history_id':i.id,'job_start_date':j.job_start_time,'job_end_date':j.job_end_time,'record_date':current_date,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
										else:
											self.pool.get('job.history').create(cr,uid,{'contract_no':j.job_id,'job_id':j.scheduled_job_id,'job_reschedule_date':datetime.now(),'technician_squad':v.reassign_tech.name,'job_status':'Technician Reassigned','history_id':i.id,'job_start_date':j.job_start_time,'job_end_date':j.job_end_time,'record_date':current_date,'service_order_id':service_order_id[0]})

									if i.delivery_order_no :
										tech_name=self.pool.get('hr.employee').browse(cr,uid,search_tech[0])
										search_delivery_order_id = self.pool.get('stock.transfer').search(cr,uid,[('stock_transfer_no','=',i.delivery_order_no)])
										self.pool.get('stock.transfer').write(cr,uid,search_delivery_order_id,{'person_name':tech_name.name or '' +' '+ tech_name.middle_name or ''+' '+ tech_name.last_name or ''})
								if v.reassign_tech.squad == True:
									technician_array =[]
									#search_squad = self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',j.name)])
									search_sq_name1=self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',v.reassign_tech.name)])
									if search_sq_name1:
										for search_sq_name_1 in self.pool.get('res.define.squad').browse(cr,uid,search_sq_name1):
												for search_sq_name_technician in search_sq_name_1.tech2:
														technician11 = search_sq_name_technician.name
														technician_array.append(technician11)												
												technicians3 = ''
												if technician_array != []:
														for val1 in technician_array:
																	var1 = val1
																	if technicians3 == '':
																			technicians3 = var1
																	else:
																			technicians3=technicians3 +','+var1	
									squad_full_detail=v.reassign_tech.name + '(' + technicians3 + ')'
									squad_full_detail11 = technicians3
									self.pool.get('res.scheduledjobs').write(cr, uid, i.id, {'assigned_squad':search_sq_name1[0],'squad_id':search_sq_name1[0],'sq_name_new1':squad_full_detail,'sq_name_new2':squad_full_detail11,'sq_name_new':v.reassign_tech.name,'assign_resource_id':'','assign_resource_id1':'','technician_squad_merge':v.reassign_tech.name,'assigned_technician':0,})#,'state':'scheduled'
									if j.erp_order_no:
										product_order_id = self.pool.get('psd.sales.product.order').search(cr,uid,[('erp_order_no','=',j.erp_order_no)])
										invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('delivery_note_no','=',j.delivery_challan_no)])
										if invoice_id:
											self.pool.get('job.history').create(cr,uid,{'contract_no':j.job_id,'job_id':j.scheduled_job_id,'job_reschedule_date':datetime.now(),'technician_squad':v.reassign_tech.name,'job_status':'Technician Reassigned','history_id':i.id,'job_start_date':j.job_start_time,'job_end_date':j.job_end_time,'record_date':current_date,	'product_order_id':product_order_id[0],'invoice_id':invoice_id[0] or None})
										else:
											self.pool.get('job.history').create(cr,uid,{'contract_no':j.job_id,'job_id':j.scheduled_job_id,'job_reschedule_date':datetime.now(),'technician_squad':v.reassign_tech.name,'job_status':'Technician Reassigned','history_id':i.id,'job_start_date':j.job_start_time,'job_end_date':j.job_end_time,'record_date':current_date,	'product_order_id':product_order_id[0]})
									if j.service_order_no:
										service_order_id = self.pool.get('amc.sale.order').search(cr,uid,[('order_number','=',j.service_order_no)])
										invoice_id = self.pool.get('invoice.adhoc.master').search(cr,uid,[('erp_order_no','=',j.service_order_no)])
										if invoice_id:
											self.pool.get('job.history').create(cr,uid,{'contract_no':j.job_id,'job_id':j.scheduled_job_id,'job_reschedule_date':datetime.now(),'technician_squad':v.reassign_tech.name,'job_status':'Technician Reassigned','history_id':i.id,'job_start_date':j.job_start_time,'job_end_date':j.job_end_time,'record_date':current_date,'service_order_id':service_order_id[0],'invoice_id':invoice_id[0] or None})
										else:
											self.pool.get('job.history').create(cr,uid,{'contract_no':j.job_id,'job_id':j.scheduled_job_id,'job_reschedule_date':datetime.now(),'technician_squad':v.reassign_tech.name,'job_status':'Technician Reassigned','history_id':i.id,'job_start_date':j.job_start_time,'job_end_date':j.job_end_time,'record_date':current_date,'service_order_id':service_order_id[0]})

									if i.delivery_order_no :
										squad_name=self.pool.get('res.define.squad').browse(cr,uid,search_sq_name1[0]).squad_name
										search_delivery_order_id = self.pool.get('stock.transfer').search(cr,uid,[('stock_transfer_no','=',i.delivery_order_no)])
										self.pool.get('stock.transfer').write(cr,uid,search_delivery_order_id,{'person_name':squad_name})
								#tech_name=i.assigned_technician.id
								#job_start=i.job_start_time
								#job_end=i.job_end_time
								#code for updating the technician value in assign resource grid
								#before_technician_reassign=j.extend_tech_name
								#assign_res_id=i.assign_resource_id
								'''if assign_res_id:
									split_tech_id=assign_res_id.split(',')
									for sp_id in split_tech_id:
										search_assign_id=self.pool.get('assign.resource').search(cr,uid,[('id','=',sp_id)])
										if search_assign_id:
											for j in self.pool.get('assign.resource').browse(cr,uid,search_assign_id):
												if j.assign_resource_technician_one2many:
													for tst in j.assign_resource_technician_one2many:
														tech_ids=tst.tech_name.name #== job.assigned_technician.id:
														if tech_ids == before_technician_reassign and not v.if_squad_bool:
															hr_name_id=self.pool.get('hr.employee').search(cr,uid,[('emp_code','=',emp_code)])
															a=self.pool.get('assign.resource.technician.grid').write(cr,uid,tst.id,{'extend_tech_name':hr_name_id[0]})'''
								
			
								if not v.reassign_tech.squad and not i.job_extended_bool:
									job_end = i.job_end_time
									start_date = i.job_start_time
									a,b,c= get_date_diff(start_date,job_end,config_time=True)	
									tech_time = float(a) + float(b)/60 + float(c)/3600
									technician_name=v.reassign_tech.name
									emp_code=v.reassign_tech.emp_code
									desig_id=self.pool.get('resource.resource').search(cr,uid,[('code','=',emp_code)])
									desig_id1=self.pool.get('hr.employee').search(cr,uid,[('resource_id','=',desig_id)])
									for role1 in self.pool.get('hr.employee').browse(cr,uid,desig_id1):
										role=role1.role
										self.pool.get('manpower.estimate').create(cr,uid,{'manpower_estimate_line':i.id,
												'designation':role,'no_of_manpower':1,'no_of_hours':tech_time,'empl':role1.id})

								if v.reassign_tech.squad and not i.job_extended_bool:
									job_end = i.job_end_time
									start_date = i.job_start_time
									a,b,c= get_date_diff(start_date,job_end,config_time=True)	
									tech_time = float(a) + float(b)/60 + float(c)/3600
									sq_name=v.reassign_tech.name
									sq_id=self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',sq_name)])
									for sq_detail in self.pool.get('res.define.squad').browse(cr,uid,sq_id):
										for emp in sq_detail.tech2:
											tech_name=emp.name
											emp_code=emp.emp_code
											desig_id=self.pool.get('resource.resource').search(cr,uid,[('code','=',emp_code)])
											desig_id1=self.pool.get('hr.employee').search(cr,uid,[('resource_id','=',desig_id)])	
											for role1 in self.pool.get('hr.employee').browse(cr,uid,desig_id1):
												role=role1.role 
												self.pool.get('manpower.estimate').create(cr,uid,{'manpower_estimate_line':i.id,
														'designation':role,'no_of_manpower':1,'no_of_hours':tech_time,'empl':role1.id})
								if i.job_extended_bool and not v.reassign_tech.squad:
									if i.job_extended_one2many:
										for time in i.job_extended_one2many:
											ex_time_st=time.extended_start_time
											ex_time_ed=time.extended_end_time
											emp_code=v.reassign_tech.emp_code
											a,b,c= get_date_diff(ex_time_st,ex_time_ed,config_time=True)
											hours1 = float(a) + float(b)/60 + float(c)/3600
											re_tech_name=v.reassign_tech.name
											desig_id=self.pool.get('resource.resource').search(cr,uid,[('code','=',emp_code)])
											desig_id1=self.pool.get('hr.employee').search(cr,uid,[('resource_id','=',desig_id)])	
											for role1 in self.pool.get('hr.employee').browse(cr,uid,desig_id1):
												role=role1.role 
												self.pool.get('manpower.estimate').create(cr,uid,{'manpower_estimate_line':i.id,
														'designation':role,'no_of_manpower':1,'no_of_hours':hours1,'empl':role1.id})
								if i.job_extended_bool and v.reassign_tech.squad:
									if i.job_extended_one2many:
										for time in i.job_extended_one2many:
											ex_time_st=time.extended_start_time
											ex_time_ed=time.extended_end_time
											a,b,c= get_date_diff(ex_time_st,ex_time_ed,config_time=True)
											hours1 = float(a) + float(b)/60 + float(c)/3600
											re_squad_name=v.reassign_tech.name
											sq_id=self.pool.get('res.define.squad').search(cr,uid,[('squad_name','=',re_squad_name)])
											for sq_detail in self.pool.get('res.define.squad').browse(cr,uid,sq_id):
												for emp in sq_detail.tech2:
														self.pool.get('manpower.estimate').create(cr,uid,{'manpower_estimate_line':i.id,
																'designation':emp.technician_id.role,'no_of_manpower':1,'no_of_hours':hours1,'empl':emp.technician_id.id})


						#form_id=o.id
						#tech_wizard=o.technician_select.id
						#one2many_id=o.one2many_id
							
			
		
		return True


    def psd_clear_jobs(self, cr, uid, ids, context=None):
	for i in self.browse(cr,uid,ids): 
		self.pool.get('bulk.reschedule').write(cr, uid,i.id, {'select_all1':False})
		for k in i.reschedule_ids:
			self.pool.get('bulk.reschedule.one2many').unlink(cr,uid,k.id)
	self.write(cr,uid,ids,{'tech_name':False,'squad_name':False,'from_date':False,'to_date':False,'reassign_tech':False})
	return True

    def psd_search_jobs(self, cr, uid, ids, context=None):
	search_val=''
	current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.id
	for o in self.browse(cr,uid,ids):
		self.pool.get('bulk.reschedule').write(cr, uid,o.id, {'select_all1':False})
		cr.execute("update bulk_technician set active1=False")
		if not o.from_date and not o.to_date:
				raise osv.except_osv(('Alert!'),('Please select From Date and To Date'))
		if not o.from_date:
				raise osv.except_osv(('Alert!'),('Please select From Date'))
		if not o.to_date:
				raise osv.except_osv(('Alert!'),('Please select To Date'))
		cr.execute("delete from bulk_technician")
		#cr.execute("delete from bulk_reschedule_one2many")
		for k11 in o.reschedule_ids:
			self.pool.get('bulk.technician').unlink(cr,uid,k11.id)
			self.pool.get('bulk.reschedule.one2many').unlink(cr,uid,k11.id)
		current_date = datetime.now().date()
		
		squad_srh = self.pool.get('res.define.squad').search(cr,uid,[('id','>',0),('record_id','!=','False')])
		for emp1 in self.pool.get('res.define.squad').browse(cr,uid,squad_srh):
			resign_flag=False
			tech_id1= self.pool.get('res.technician2').search(cr,uid,[('id2','=',emp1.id)])
			for oo in self.pool.get('res.technician2').browse(cr,uid,tech_id1):
				if oo.technician_id.status=='resign':
					resign_flag=True
					
			if resign_flag==False:
				self.pool.get('bulk.technician').create(cr,uid,{'name':emp1.squad_name,'squad':True,'active1':True})
		search_emp = self.pool.get('hr.employee').search(cr,uid,[('id','>',0),('role_selection','=','executor'),('status','!=','resign'),('branch','=',current_company)])
		for emp in self.pool.get('hr.employee').browse(cr,uid,search_emp):
			emp_code = emp.emp_code
			pre_tech=emp.id
			if pre_tech:
				for na in self.pool.get('hr.employee').browse(cr,uid,[pre_tech]):
					f_name = na.name if na.name else ''
					s_name = na.middle_name if na.middle_name else ''
					l_name = na.last_name if na.last_name else ''
					temp_name = [f_name,s_name,l_name]
					pre_full_name = ' '.join(filter(bool,temp_name))
					self.pool.get('bulk.technician').create(cr,uid,{'emp_code':emp.emp_code,'name':pre_full_name,'active1':True})
		search_job=o.id
		job_tech=o.tech_name.id
		job_squad = o.squad_name.id
		from_search=o.from_date
		to_search=o.to_date
		search_val = ''
		tech_search=self.pool.get('hr.employee')
		job_search=tech_search.search(cr, uid, [('id', '=',job_tech),('branch','=',current_company)])
		assigned_tech=self.pool.get('res.scheduledjobs')
		scheduled_job_search=self.pool.get('res.scheduledjobs').search(cr,uid,[('result_id', '=',search_job)])
		if scheduled_job_search:
		   for l in self.pool.get('res.scheduledjobs').browse(cr,uid,scheduled_job_search): 
			self.pool.get('res.scheduledjobs').write(cr,uid,l.id,{'result_id':0})
		if o.tech_name and o.squad_name:
			raise osv.except_osv(('Alert'),('Please select either Technician or Squad'))
                if not o.tech_name and not o.squad_name:
			raise osv.except_osv(('Alert'),('Please select either Technician or Squad'))
		if o.tech_name:
			search_val=assigned_tech.search(cr, uid, [('assigned_technician', '=',job_tech),('state','in',('scheduled','confirmed','extended'))])
		if o.squad_name:
			search_val = assigned_tech.search(cr, uid, [('assigned_squad', '=',job_squad),('state','in',('scheduled','confirmed','extended'))])
		if search_val:
			for t in self.pool.get('res.scheduledjobs').browse(cr,uid,search_val):
				search_job_date=t.job_start_time
				search_end_date=t.job_end_time
				##################### Check whether customer is transfered or not ######################
				show_rec = True
				if t.name_contact:
					if t.name_contact.is_transfered:
						show_rec=False
				else:
					if t.job_id:
						contract_search=self.pool.get('sale.contract').search(cr,uid,[('contract_number', '=',t.job_id)])
						if contract_search:
							for each in self.pool.get('sale.contract').browse(cr,uid,contract_search):
								get_partner_status=each.partner_id.is_transfered
								if get_partner_status:
									show_rec=False
				if show_rec:
				##################### Check whether customer is transfered or not ######################
					if ((from_search <= t.job_start_date and from_search <= t.job_end_date) and (to_search >= t.job_start_date and to_search >= t.job_end_date)):
						self.pool.get('bulk.reschedule.one2many').create(cr,uid,{'result_id':search_job,'name':t.name,'scheduled_job_id':t.scheduled_job_id,'job_id':t.job_id,'job_start_time':t.new_job_start_time1,'job_start_date':t.job_start_date,'job_end_date':t.job_start_date,
	'job_end_time':t.new_job_end_time1,'service_area':t.service_area_on_fly.name,'state':t.state,'req_date_time':t.req_date_time,'assigned_technician':t.assigned_technician.id,'assigned_squad':t.assigned_squad.id})
		
		else:
	                raise osv.except_osv(('Alert'),('No Record Found'))	
	return True


bulk_reschedule()