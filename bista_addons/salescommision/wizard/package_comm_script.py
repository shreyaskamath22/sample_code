from openerp.osv import osv,fields
from datetime import datetime
import calendar
import logging
logger = logging.getLogger('arena_log')

class package_comm_script(osv.osv_memory):
    _name = 'package.comm.script'
    _columns = {
                'start_date':fields.date('Start Date'),
                'end_date':fields.date('End Date')
    }

    def create(self, cr, uid, vals, context=None):
        start_date = vals['start_date']
        end_date = vals['end_date']
        if not start_date:
            raise osv.except_osv(('Warning'),("Start date can not be blank."))
        if not end_date:
            raise osv.except_osv(('Warning'),("End date can not be blank."))
        end_date_mon = datetime.strptime(end_date,'%Y-%m-%d').strftime('%m')
        end_date_day = datetime.strptime(end_date,'%Y-%m-%d').strftime('%d')
        end_date_year = datetime.strptime(end_date,'%Y-%m-%d').strftime('%Y')
        start_date_day = datetime.strptime(start_date,'%Y-%m-%d').strftime('%d')
        start_date_mon = datetime.strptime(start_date,'%Y-%m-%d').strftime('%m')
        start_date_year = datetime.strptime(start_date,'%Y-%m-%d').strftime('%Y')
        days_month = calendar.monthrange(int(end_date_year),int(end_date_mon))[1]
        if start_date and end_date:
            if int(start_date_day) != 1:
                raise osv.except_osv(('Warning'),("Start date should be first of month."))
            if int(days_month) != int(end_date_day):
                raise osv.except_osv(('Warning'),("End date should be month last date."))
            if start_date_mon != end_date_mon:
                raise osv.except_osv(('Warning'),("Start date and End date should be in same month."))
            if start_date_year != end_date_year:
                raise osv.except_osv(('Warning'),("Start date and End date should be in same year."))
        res_id = super(package_comm_script, self).create(cr, uid, vals, context=context)
        return res_id

    def run_script_pre(self, cr, uid, ids, context=None):
        vals = {}
        list_package_ids = []
        hr_obj = self.pool.get('hr.employee')
        prm_crash_obj = self.pool.get('dsr.crash.process.deactivation')
        package_comm = self.pool.get('packaged.commission.tracker')
        dealer_obj = self.pool.get('dealer.class')
        des_track_master = self.pool.get('designation.tracker')
        split_obj = self.pool.get('spliting.goals')
        self_obj = self.browse(cr, uid, ids[0])
        start_date = self_obj.start_date
        end_date = self_obj.end_date
        ########## get employees RSA/STL/MID/RSM/MM/DOS #####################
        cr.execute('''select distinct(hr.id) 
    from hr_employee hr, designation_tracker dt, hr_job job
where hr.id = dt.dealer_id and dt.designation_id = job.id
and dt.end_date >= %s and hr.hire_date <= %s and job.model_id in ('rsa','stl')''',(start_date,end_date))
        hr_ids = map(lambda x: x[0], cr.fetchall())

        cr.execute("select distinct(store_mgr_id) from sap_tracker where end_date >= %s and start_date <= %s and store_mgr_id is not null",(start_date,end_date))
        store_hr_ids = map(lambda x: x[0], cr.fetchall())
        for store_hr_id in store_hr_ids:
            hr_ids.append(store_hr_id)

        cr.execute("select distinct(market_manager) from market_tracker where end_date >= %s and start_date <= %s and market_manager is not null",(start_date,end_date))
        mm_hr_ids = map(lambda x: x[0], cr.fetchall())
        for mm_hr_id in mm_hr_ids:
            hr_ids.append(mm_hr_id)

        cr.execute("select distinct(sales_director) from region_tracker where end_date >= %s and start_date <= %s and sales_director is not null",(start_date,end_date))
        dos_hr_ids = map(lambda x: x[0], cr.fetchall())
        for dos_hr_id in dos_hr_ids:
            hr_ids.append(dos_hr_id)

        cr.execute('''select emp.id
from hr_employee emp,hr_job job,designation_tracker dc
where dc.dealer_id = emp.id and dc.designation_id=job.id and emp.hire_date <= %s
and dc.end_date >= %s and job.model_id = 'mid' ''',(start_date,end_date))

        mid_hr_ids = map(lambda x: x[0], cr.fetchall())
        for mid_hr_id in mid_hr_ids:
            hr_ids.append(mid_hr_id)
        hr_ids = list(set(hr_ids))

        s = datetime.today()
        prm_search = prm_crash_obj.search(cr, uid, [('dsr_crash_start_date','=',start_date),('dsr_crash_end_date','=',end_date),('state','=','done'),('pre_prm_upload','=',True)])
        if prm_search:
            for hr_id in hr_ids:
                hr_data = hr_obj.browse(cr, uid, hr_id)
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(hr_id,start_date,end_date))
                dealer_ids = map(lambda x: x[0], cr.fetchall())
                if not dealer_ids:
                    dealer_ids = dealer_obj.search(cr, uid, [('dealer_id','=',hr_id),('start_date','<=',start_date),('end_date','>=',end_date)])
                if dealer_ids:
                    for dealer_id in dealer_ids:
                        dealer_code = dealer_obj.browse(cr, uid, dealer_id).name
                else:
                    dealer_code = ''
                cr.execute("select id from designation_tracker where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(hr_id,start_date,end_date))
                des_track_search = map(lambda x: x[0], cr.fetchall())
                if not des_track_search:
                    des_track_search = des_track_master.search(cr, uid, [('dealer_id', '=', hr_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
                # split_des_search = split_obj.search(cr, uid, [('employee_id','=',hr_id),('start_date','=',start_date),('end_date','=',end_date)])
                # if split_des_search:
                #     designation_id = split_obj.browse(cr, uid, split_des_search[0]).designation_id.id
                #     model_id = split_obj.browse(cr, uid, split_des_search[0]).designation_id.model_id
                if des_track_search:
                    for des_track_search_id in des_track_search:
                        designation_id = des_track_master.browse(cr, uid, des_track_search_id).designation_id.id
                        model_id = des_track_master.browse(cr, uid, des_track_search_id).designation_id.model_id
                else:
                    designation_id = hr_data.job_id.id
                    model_id = hr_data.job_id.model_id
                if hr_data.user_id:
                    if hr_data.user_id.sap_id:
                        store_id = hr_data.user_id.sap_id.id
                        market_id = hr_data.user_id.market_id.id
                        region_id = hr_data.user_id.region_id.id
                        if not market_id:
                            market_id = hr_data.user_id.sap_id.market_id.id
                        if not region_id:
                            region_id = hr_data.user_id.sap_id.market_id.region_market_id.id
                        vals = {
                                'name':hr_id,
                                'crash_job_name':prm_search[0],
                                'emp_des':designation_id,
                                'start_date':start_date,
                                'end_date':end_date,
                                'model_id':model_id,
                                'comm_store_id':store_id,
                                'comm_market_id':market_id,
                                'comm_region_id':region_id,
                                'pre_package_comm':True,
                                'dealer_code':dealer_code
                        }
                        package_id = package_comm.create(cr, uid, vals)
                        list_package_ids.append(package_id)
#                        package_comm.calculate_pre_total_payout(cr, uid, [package_id])
#                        cr.commit()
        else:
            raise osv.except_osv(('Warning'),("PRM data crashing record could not be found for the given period."))
        count = 0
        ### code to calculate the payout for all the package ids
        for each_pack_id in list_package_ids:
            logger.error("count: %s"%(count))
            package_comm.calculate_pre_total_payout(cr, uid, [each_pack_id])
        #### code ends here
            count = count + 1

        package_ids = package_comm.search(cr, uid, [('start_date','=',start_date),('end_date','=',end_date),('pre_package_comm','=',True)])
        if package_ids:
            package_comm.calculate_elite_bonus(cr, uid, start_date, end_date, True)
        logger.error("Completed pre Commissions for Pre packaging: %s"%(count))
        logger.error("Completed pre Commissions for Pre packaging: %s"%(count))
        return True

    def run_script(self, cr, uid, ids, context=None):
        vals = {}
        list_package_ids = []
        hr_obj = self.pool.get('hr.employee')
        prm_crash_obj = self.pool.get('dsr.crash.process.deactivation')
        package_comm = self.pool.get('packaged.commission.tracker')
        dealer_obj = self.pool.get('dealer.class')
        des_track_master = self.pool.get('designation.tracker')
        split_obj = self.pool.get('spliting.goals')
        self_obj = self.browse(cr, uid, ids[0])
        start_date = self_obj.start_date
        end_date = self_obj.end_date
        ########## get employees RSA/STL/MID/RSM/MM/DOS #####################
        cr.execute('''select distinct(hr.id) 
    from hr_employee hr, designation_tracker dt, hr_job job
where hr.id = dt.dealer_id and dt.designation_id = job.id
and dt.end_date >= %s and hr.hire_date <= %s and job.model_id in ('rsa','stl')''',(start_date,end_date))
        hr_ids = map(lambda x: x[0], cr.fetchall())

        cr.execute("select distinct(store_mgr_id) from sap_tracker where end_date >= %s and start_date <= %s and store_mgr_id is not null",(start_date,end_date))
        store_hr_ids = map(lambda x: x[0], cr.fetchall())
        for store_hr_id in store_hr_ids:
            hr_ids.append(store_hr_id)

        cr.execute("select distinct(market_manager) from market_tracker where end_date >= %s and start_date <= %s and market_manager is not null",(start_date,end_date))
        mm_hr_ids = map(lambda x: x[0], cr.fetchall())
        for mm_hr_id in mm_hr_ids:
            hr_ids.append(mm_hr_id)

        cr.execute("select distinct(sales_director) from region_tracker where end_date >= %s and start_date <= %s and sales_director is not null",(start_date,end_date))
        dos_hr_ids = map(lambda x: x[0], cr.fetchall())
        for dos_hr_id in dos_hr_ids:
            hr_ids.append(dos_hr_id)

        cr.execute('''select emp.id
from hr_employee emp,hr_job job,designation_tracker dc
where dc.dealer_id = emp.id and dc.designation_id=job.id and emp.hire_date <= %s
and dc.end_date >= %s and job.model_id = 'mid' ''',(start_date,end_date))

        mid_hr_ids = map(lambda x: x[0], cr.fetchall())
        for mid_hr_id in mid_hr_ids:
            hr_ids.append(mid_hr_id)
        hr_ids = list(set(hr_ids))

        s = datetime.today()
        prm_search = prm_crash_obj.search(cr, uid, [('dsr_crash_start_date','=',start_date),('dsr_crash_end_date','=',end_date),('state','=','done'),('pre_prm_upload','=',False)])
        if prm_search:
            for hr_id in hr_ids:
                print hr_id
                hr_data = hr_obj.browse(cr, uid, hr_id)
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
       ########## dealer code fetch from dealer tracker master ################s
                cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(hr_id,start_date,end_date))
                dealer_ids = map(lambda x: x[0], cr.fetchall())
                if not dealer_ids:
                    dealer_ids = dealer_obj.search(cr, uid, [('dealer_id','=',hr_id),('start_date','<=',start_date),('end_date','>=',end_date)])
                if dealer_ids:
                    for dealer_id in dealer_ids:
                        dealer_code = dealer_obj.browse(cr, uid, dealer_id).name
                else:
                    dealer_code = ''
        ########## designation and model_id fetch from designation tracker, else from spliting goals object else False ########
                cr.execute("select id from designation_tracker where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(hr_id,start_date,end_date))
                des_track_search = map(lambda x: x[0], cr.fetchall())
                if not des_track_search:
                    des_track_search = des_track_master.search(cr, uid, [('dealer_id', '=', hr_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
                # split_des_search = split_obj.search(cr, uid, [('employee_id','=',hr_id),('start_date','=',start_date),('end_date','=',end_date)])
                # if split_des_search:
                #     designation_id = split_obj.browse(cr, uid, split_des_search[0]).designation_id.id
                #     model_id = split_obj.browse(cr, uid, split_des_search[0]).designation_id.model_id
                if des_track_search:
                    for des_track_search_id in des_track_search:
                        designation_id = des_track_master.browse(cr, uid, des_track_search_id).designation_id.id
                        model_id = des_track_master.browse(cr, uid, des_track_search_id).designation_id.model_id
                else:
                    designation_id = hr_data.job_id.id
                    model_id = hr_data.job_id.model_id
         ########### store, market, region just for access rights hidden fields ##########
                if hr_data.user_id:
                    if hr_data.user_id.sap_id:
                        store_id = hr_data.user_id.sap_id.id
                        market_id = hr_data.user_id.market_id.id
                        region_id = hr_data.user_id.region_id.id
                        if not market_id:
                            market_id = hr_data.user_id.sap_id.market_id.id
                        if not region_id:
                            region_id = hr_data.user_id.sap_id.market_id.region_market_id.id
        ######### Creating package comm record and calculating payout ########
                        vals = {
                                'name':hr_id,
                                'crash_job_name':prm_search[0],
                                'emp_des':designation_id,
                                'start_date':start_date,
                                'end_date':end_date,
                                'model_id':model_id,
                                'comm_store_id':store_id,
                                'comm_market_id':market_id,
                                'comm_region_id':region_id,
                                'pre_package_comm':False,
                                'dealer_code':dealer_code
                        }
                        package_id = package_comm.create(cr, uid, vals)
                        list_package_ids.append(package_id)
                        #package_comm.calculate_total_payout(cr, uid, [package_id])
                        #cr.commit()
        else:
            raise osv.except_osv(('Warning'),("PRM data crashing record could not be found for the given period."))

        count = 0
        ### code to calculate the payout for all the package ids
        for each_pack_id in list_package_ids:
            logger.error("pack count: %s"%(count))
            package_comm.calculate_total_payout(cr, uid, [each_pack_id])
        #### code ends here
            count = count + 1

        package_ids = package_comm.search(cr, uid, [('start_date','=',start_date),('end_date','=',end_date),('pre_package_comm','=',False)])
        if package_ids:
            package_comm.calculate_elite_bonus(cr, uid, start_date, end_date, False)
        logger.error("Completed Packaged Commission: %s"%(count))
        logger.error("Completed Packaged Commissions: %s"%(count))

        return True

package_comm_script()


class repackaged_commission(osv.osv_memory):
    _name = 'repackaged.commission'
    _columns = {
                'emp_id':fields.many2one('hr.employee','Employee'),
                'start_date':fields.date('Start Date'),
                'end_date':fields.date('End Date')
    }

    def create(self, cr, uid, vals, context=None):
        start_date = vals['start_date']
        end_date = vals['end_date']
        if not start_date:
            raise osv.except_osv(('Warning'),("Start date can not be blank."))
        if not end_date:
            raise osv.except_osv(('Warning'),("End date can not be blank."))
        end_date_mon = datetime.strptime(end_date,'%Y-%m-%d').strftime('%m')
        end_date_day = datetime.strptime(end_date,'%Y-%m-%d').strftime('%d')
        end_date_year = datetime.strptime(end_date,'%Y-%m-%d').strftime('%Y')
        start_date_day = datetime.strptime(start_date,'%Y-%m-%d').strftime('%d')
        start_date_mon = datetime.strptime(start_date,'%Y-%m-%d').strftime('%m')
        start_date_year = datetime.strptime(start_date,'%Y-%m-%d').strftime('%Y')
        days_month = calendar.monthrange(int(end_date_year),int(end_date_mon))[1]
        if start_date and end_date:
            if int(start_date_day) != 1:
                raise osv.except_osv(('Warning'),("Start date should be first of month."))
            if int(days_month) != int(end_date_day):
                raise osv.except_osv(('Warning'),("End date should be month last date."))
            if start_date_mon != end_date_mon:
                raise osv.except_osv(('Warning'),("Start date and End date should be in same month."))
            if start_date_year != end_date_year:
                raise osv.except_osv(('Warning'),("Start date and End date should be in same year."))
        res_id = super(repackaged_commission, self).create(cr, uid, vals, context=context)
        return res_id

    def rerun_packaged_commission(self, cr, uid, ids, context=None):
        pack_obj = self.pool.get('packaged.commission.tracker')
        self_obj = self.browse(cr, uid, ids[0])
        emp_id = self_obj.emp_id.id
        start_date = self_obj.start_date
        end_date = self_obj.end_date
        package_ids = pack_obj.search(cr, uid, [('name','=',emp_id),('start_date','=',start_date),('end_date','=',end_date),('pre_package_comm','=',False)])
        if package_ids:
            pack_obj.calculate_total_payout(cr, uid, package_ids)
            pack_obj.calculate_elite_bonus_each(cr, uid, package_ids)
        else:
            raise osv.except_osv(('Warning!!'),('No Records could be found for this employee in given time period.'))
        return True

repackaged_commission()