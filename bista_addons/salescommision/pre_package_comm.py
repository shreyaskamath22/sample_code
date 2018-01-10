from openerp.osv import osv,fields
import time
from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta
from openerp.osv.orm import setup_modifiers
from lxml import etree
import simplejson
import logging
logger = logging.getLogger('arena_log')

class packaged_commission_tracker(osv.osv):
    _inherit = 'packaged.commission.tracker'

    def calculate_pre_total_payout(self, cr, uid, ids, context=None):
        s = datetime.today()
        dsr_obj = self.pool.get('wireless.dsr')
        pos_obj = self.pool.get('wireless.dsr.postpaid.line')
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        feature_obj = self.pool.get('wireless.dsr.feature.line')
        upg_obj = self.pool.get('wireless.dsr.upgrade.line')
        acc_obj = self.pool.get('wireless.dsr.acc.line')
        market_obj = self.pool.get('market.place')
        region_obj = self.pool.get('market.regions')
        model_obj = self.pool.get('ir.model')
        des_track_master = self.pool.get('designation.tracker')
        dealer_obj = self.pool.get('dealer.class')
        package_obj = self.pool.get('packaged.commission.tracker')
        prm_obj = self.pool.get('dsr.crash.process.deactivation')
        business_rule_master = self.pool.get('business.rule.master')
        split_goal_obj = self.pool.get('spliting.goals')
        store_obj = self.pool.get('sap.store')
        sap_track_obj = self.pool.get('sap.tracker')
        market_track_obj = self.pool.get('market.tracker')
        region_track_obj = self.pool.get('region.tracker')
        split_goal_obj = self.pool.get('spliting.goals')
        goal_obj = self.pool.get('import.goals')
# ######## Self Obj Parameters ############
        self_obj = self.browse(cr, uid, ids[0])
        emp_id = self_obj.name.id        
        start_date = self_obj.start_date
        end_date = self_obj.end_date
        store_data = self_obj.name.user_id.sap_id
        store_id = store_data.id
        market_id = store_data.market_id.id
        region_id = store_data.market_id.region_market_id.id
        store_classification_id = store_data.store_classification.id
        traffic_red = store_data.store_classification.traffic_reduction
        cal_level = store_data.store_classification.cal_level
        hire_date = self_obj.name.hire_date
        hire_date_min = datetime.strptime(start_date, '%Y-%m-%d')
        hire_date_min = (hire_date_min - relativedelta(days=30))
######### profit start date and end date (1 month before commission date) ##########
        profit_start_date_1 = datetime.strptime(start_date, '%Y-%m-%d')
        current_date = profit_start_date_1.date()
        current_date_month = current_date.month
        current_date_year = current_date.year
        current_days_month = calendar.monthrange(current_date_year,current_date_month)[1]
        profit_start_date = (profit_start_date_1 - relativedelta(months=1))
        profit_start_date = profit_start_date.date().strftime('%Y-%m-%d')
        profit_end_date_1 = datetime.strptime(end_date, '%Y-%m-%d')
        todays_date = (profit_end_date_1 - relativedelta(months=1)).date()
        date_month = todays_date.month
        date_year = todays_date.year
        days_month = calendar.monthrange(date_year,date_month)[1]
        store_max_date_traffic = (profit_end_date_1 + relativedelta(days=30)).date()
        profit_end_date = str('%s-%s-%s' % (int(date_year),int(date_month),int(days_month)))
        profit_end_date = datetime.strptime(profit_end_date, '%Y-%m-%d')
        profit_end_date = profit_end_date.date().strftime('%Y-%m-%d')
# ****************** Parameters used to get month to date (goals, no. of exits) for employees for that period of time like if emp is running from 1 to 15, goals and no. of exit will be calculated for 1-15 date only ******** #
        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        delta_date = goal_end_date - goal_start_date
        delta_date = delta_date.days + 1
        date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
        days_in_month = calendar.monthrange(date_monthrange.year, date_monthrange.month)[1]
########## Employee designation between period of commission is running ###############        
        cr.execute("select id from designation_tracker where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date desc",(emp_id,start_date,end_date))
        des_track_search = map(lambda x: x[0], cr.fetchall())
        if not des_track_search:
            des_track_search = des_track_master.search(cr, uid, [('dealer_id', '=', emp_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
        if des_track_search:
            emp_des = des_track_master.browse(cr, uid, des_track_search[0]).designation_id.id
            emp_model_id = des_track_master.browse(cr, uid, des_track_search[0]).designation_id.model_id
        else:
            emp_des = self_obj.emp_des.id
            emp_model_id = self_obj.emp_des.model_id
############ RSA/STL/MID store,market,region from dealer code tracker table ##############
        cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
        dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
        if not dealer_obj_search_multi:
            dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
        for dealer_obj_search_multi_id in dealer_obj_search_multi:
            store_data = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id).store_name
            store_id = store_data.id
            cr.execute('''select sap.market_id from sap_tracker sap, designation_tracker dt 
                    where sap.desig_id = dt.id and sap.sap_id = %s and sap.end_date >= %s and sap.start_date <= %s 
                    and dt.covering_str_check = false and sap.store_inactive = false order by sap.end_date desc''',(store_id,start_date,end_date))
            rsa_mkt_search = cr.fetchall()
            if rsa_mkt_search:
                market_id = rsa_mkt_search[0][0]
            else:
                market_id = store_data.market_id.id
            cr.execute('''select mkt.region_market_id from market_tracker mkt, designation_tracker dt 
                    where mkt.desig_id = dt.id and mkt.market_id = %s and mkt.end_date >= %s and mkt.start_date <= %s 
                    and dt.covering_str_check = false order by mkt.end_date desc''',(market_id,start_date,end_date))
            rsa_reg_search = cr.fetchall()
            if rsa_reg_search:
                region_id = rsa_reg_search[0][0]
            else:
                region_id = store_data.market_id.region_market_id.id
            traffic_red = store_data.store_classification.traffic_reduction
            store_classification_id = store_data.store_classification.id
            cal_level = store_data.store_classification.cal_level
########### RSM/RTSM store,market,region from SAP Tracker table ####################        
        cr.execute('''select sap.id from sap_tracker sap, designation_tracker dt 
            where sap.desig_id = dt.id and sap.store_mgr_id = %s and sap.end_date >= %s and sap.start_date <= %s 
            and dt.covering_str_check = false and sap.store_inactive = false order by sap.end_date desc''',(emp_id,start_date,end_date))
        store_emp_search = map(lambda x: x[0], cr.fetchall())
        if not store_emp_search:
            store_emp_search = sap_track_obj.search(cr, uid, [('store_mgr_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
        if store_emp_search:
            store_data = sap_track_obj.browse(cr, uid, store_emp_search[0])
            store_id = store_data.sap_id.id
            market_id = store_data.market_id.id
            cr.execute('''select mkt.region_market_id from market_tracker mkt, designation_tracker dt
             where mkt.desig_id = dt.id and mkt.market_id = %s and mkt.end_date >= %s and mkt.start_date <= %s 
             and dt.covering_str_check = false order by mkt.end_date desc''',(market_id,start_date,end_date))
            rsm_reg_search = cr.fetchall()
            if rsm_reg_search:
                region_id = rsm_reg_search[0][0]
            else:
                region_id = store_data.market_id.region_market_id.id
            traffic_red = store_data.sap_id.store_classification.traffic_reduction
            store_classification_id = store_data.sap_id.store_classification.id
            cal_level = store_data.sap_id.store_classification.cal_level
############## Market manager market, region consideration from Market Tracker table ##############
        cr.execute('''select mkt.id from market_tracker mkt, designation_tracker dt
         where mkt.desig_id = dt.id and mkt.market_manager = %s and mkt.end_date >= %s and mkt.start_date <= %s 
         and dt.covering_market_check = false order by mkt.end_date desc''',(emp_id,start_date,end_date))
        market_emp_search = map(lambda x: x[0], cr.fetchall())
        if not market_emp_search:
            market_emp_search = market_track_obj.search(cr, uid, [('market_manager','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
        if market_emp_search:
            market_data = market_track_obj.browse(cr, uid, market_emp_search[0])
            market_id = market_data.market_id.id
            region_id = market_data.region_market_id.id
############ DOS region consideration from Region Tracker Table #################
        cr.execute('''select reg.id from region_tracker reg, designation_tracker dt 
            where reg.desig_id = dt.id and reg.sales_director = %s and reg.end_date >= %s and reg.start_date <= %s 
            and dt.covering_region_check = false order by reg.end_date desc''',(emp_id,start_date,end_date))
        region_emp_search = map(lambda x: x[0], cr.fetchall())
        if not region_emp_search:
            region_emp_search = region_track_obj.search(cr, uid, [('sales_director','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
        if region_emp_search:
            region_data = region_track_obj.browse(cr, uid, region_emp_search[0])
            region_id = region_data.region_id.id
        if (not market_id) or (not region_id) or (not store_id):
            return True

        ############### Exclusion of DSR transactions as defined in Master Business Rule in format {'1':[emp,cc,code_type,soc]} #####################
        master_br_dict = {}
        master_br_emp_type = []
        master_br_cc = []
        master_br_prod_code = []
        master_br_soc = []
        master_br_obj = self.pool.get('dsr.exclude.business.rule')
        master_br_ids = master_br_obj.search(cr, uid, [])
        for master_br_data in master_br_obj.browse(cr, uid, master_br_ids):
            master_br_dict['%s'%(master_br_data.commission_br.id)] = []
            master_br_dict['%s'%(master_br_data.commission_br.id)].append(master_br_data.dsr_emp_type.id)
            master_br_dict['%s'%(master_br_data.commission_br.id)].append(master_br_data.credit_class.id)
            master_br_dict['%s'%(master_br_data.commission_br.id)].append(master_br_data.dsr_prod_code.id)
            master_br_dict['%s'%(master_br_data.commission_br.id)].append(master_br_data.dsr_soc_code.id)
            if (master_br_data.dsr_emp_type.id) and (master_br_data.dsr_emp_type.id not in master_br_emp_type):
                master_br_emp_type.append(master_br_data.dsr_emp_type.id)
            if (master_br_data.credit_class.id) and (master_br_data.credit_class.id not in master_br_cc):
                master_br_cc.append(master_br_data.credit_class.id)
            if (master_br_data.dsr_prod_code.id) and (master_br_data.dsr_prod_code.id not in master_br_prod_code):
                master_br_prod_code.append(master_br_data.dsr_prod_code.id)
            if (master_br_data.dsr_soc_code.id) and (master_br_data.dsr_soc_code.id not in master_br_soc):
                master_br_soc.append(master_br_data.dsr_soc_code.id)

        ##### code written to get the company id if its the Kiosk type of store as a list
        ##### empty list
        company_ids_search = []
        if cal_level.model == 'res.company':
            company_ids_search = self.pool.get('res.company').search(cr, uid, [])

        ##### code written here

        ###################### SMD, PMD Condition #####################################
        package_ids = package_obj.search(cr, uid, [('name','=',emp_id),('start_date','=',start_date),('end_date','>=',end_date)])
        if package_ids:
            prm_ids = prm_obj.search(cr, uid, [('dsr_crash_start_date','=',start_date),('dsr_crash_end_date','>=',end_date),('state','=','done')])
            if prm_ids:
                prm_job_id = prm_ids
            else:
                prm_job_id = [0]
        else:
            prm_job_id = [0]
        # ################## Model Search ########################################
        model_emp_search_id = model_obj.search(cr, uid, [('model', '=', 'hr.employee')])
        model_store_search_id = model_obj.search(cr, uid, [('model', '=', 'sap.store')])
        model_market_search_id = model_obj.search(cr, uid, [('model', '=', 'market.place')])
        model_region_search_id = model_obj.search(cr, uid, [('model', '=', 'market.regions')])
        model_comp_search_id = model_obj.search(cr, uid, [('model', '=', 'res.company')])
        comm_model_id = model_obj.search(cr, uid, [('model', '=', 'commission.tracker')])
        # ############### Goal Calculation #################################        
        from_box_condition = str('')
        business_box_rule_ids = self.pool.get('business.rule.master').search(cr, uid, [('is_box','=',True), ('active', '=', True), ('comm_report_selection', '=', 'commission')])
        if business_box_rule_ids:
            # cr.execute('select prod_type_id from included_feature_business_rel where rule_id=%s' % business_rule_ids[0])
            # incl_prod_type_ids = map(lambda x: x[0], cr.fetchall())
            business_rule_data = business_rule_master.browse(cr, uid, business_box_rule_ids[0])
            box_is_postpaid = business_rule_data.is_postpaid
            box_is_upgrade = business_rule_data.is_upgrade
            box_is_prepaid = business_rule_data.is_prepaid
            if box_is_postpaid:
                from_box_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
from wireless_dsr_postpaid_line union all ''')
            if box_is_prepaid:
                from_box_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description
from wireless_dsr_prepaid_line union all ''')
            if box_is_upgrade:
                from_box_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
from wireless_dsr_upgrade_line union all ''')
            from_box_condition = from_box_condition[:-10]
            spiff_rule_tuple = []
            for sub_rule in business_rule_data.sub_rules:
                if sub_rule.tac_code_rel_sub_inc:
                    for phone_type in sub_rule.tac_code_rel_sub_inc:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                else:
                    spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
            if spiff_rule_tuple:
                condition_box_string = str("and (")
                for spiff_rule_data in spiff_rule_tuple:
                    condition_box_string += str("(")
                    if spiff_rule_data[0]:
                        condition_box_string += str('''test.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                    if spiff_rule_data[1]:
                        condition_box_string += str(''' and (left(test.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                             or left(test.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                             or test.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                    if spiff_rule_data[2]:
                        condition_box_string += str(''' and test.dsr_phone_purchase_type = '%s'''%(spiff_rule_data[2],))
                    if spiff_rule_data[3]:
                        condition_box_string += str(''' and test.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                    if spiff_rule_data[4]:
                        condition_string += str(''' and test.dsr_monthly_access > 0''')
                    condition_box_string += ") OR "
                condition_box_string = condition_box_string[:-4]
                condition_box_string += str(")")
            else:
                condition_box_string = ''
        else:
            business_box_rule_ids = [0]
        business_rev_rule_ids = business_rule_master.search(cr, uid, [('is_revenue','=',True), ('active', '=', True), ('comm_report_selection', '=', 'commission')])
        if not business_rev_rule_ids:
            business_rev_rule_ids = [0]

        a = datetime.today()
        region_traffic_stores = []
        market_traffic_stores = []
        region_traffic_date = []
        market_traffic_date = []
        store_traffic_date = []
        tot_rev = 0.00
        actual_rev = 0.00
        tot_box = 0.00
        actual_box = 0.00
        actual_store_rev = 0.00
        store_tot_box = 0.00
        store_actual_box = 0.00
        tot_store_rev = 0.00
        pre_count = 0.00
        tot_emp_pos_upg_box = 0.00
        apk_rev = 0.00
        all_region_tot_box = 0.00
        all_region_actual_box = 0.00
        region_pre_box_gross = 0.00
        tot_reg_pos_upg_box = 0.00
        actual_region_rev = 0.00
        tot_region_rev = 0.00
        region_acc_rev = 0.00
        all_market_tot_box = 0.00
        all_market_actual_box = 0.00
        market_pre_box_gross = 0.00
        tot_mkt_pos_upg_box = 0.00
        actual_market_rev = 0.00
        tot_market_rev = 0.00
        market_acc_rev = 0.00
        pre_box_gross = 0.00
        tot_sto_pos_upg_box = 0.00
        store_acc_rev = 0.00
        region_voc = 0.00
        market_voc = 0.00
        store_voc = 0.00
        sto_no_of_exit = 0.00
        mkt_no_of_exit = 0.00
        reg_no_of_exit = 0.00
        apk_count = 0.00
        sto_apk_count = 0.00
        mkt_apk_count = 0.00
        reg_apk_count = 0.00
        region_smd_rev = 0.00
        region_smd_box = 0.00
        region_pmd_rev = 0.00
        region_pmd_box = 0.00
        region_react_rev = 0.00
        region_noncomm_rev = 0.00
        region_react_box = 0.00
        region_noncomm_box = 0.00
        market_smd_rev = 0.00
        market_smd_box = 0.00
        market_pmd_rev = 0.00
        market_pmd_box = 0.00
        market_react_rev = 0.00
        market_noncomm_rev = 0.00
        market_react_box = 0.00
        market_noncomm_box = 0.00
        store_smd_rev = 0.00
        store_smd_box = 0.00
        store_pmd_rev = 0.00
        store_pmd_box = 0.00
        store_react_rev = 0.00
        store_noncomm_rev = 0.00
        store_react_box = 0.00
        store_noncomm_box = 0.00
        emp_smd_rev = 0.00
        emp_smd_box = 0.00
        emp_pmd_rev = 0.00
        emp_pmd_box = 0.00
        emp_react_rev = 0.00
        emp_noncomm_rev = 0.00
        emp_react_box = 0.00
        emp_noncomm_box = 0.00
        emp_rev_goal = 0.00
        emp_box_goal = 0.00
        store_rev_goal = 0.00
        store_box_goal = 0.00
        tot_region_revenue_goal = 0.00
        tot_region_box_goal = 0.00
        tot_market_revenue_goal = 0.00
        tot_market_box_goal = 0.00

        ##### 03052015 changes also included company_ids search for this
        ##### company_ids_search

        ##### code to get the boxes count for the entire company on the specified date
        com_exit_traffic = 0.0
        if company_ids_search:
            field_name='company_id'
            company_vals = self._get_basic_parameters_box_company(cr, uid, field_name, company_ids_search[0], start_date, end_date, condition_box_string, from_box_condition, prm_job_id, business_box_rule_ids, business_rev_rule_ids,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            all_company_tot_box = company_vals['tot_box']
            all_company_actual_box = company_vals['actual_box']

            #### company wide traffic code
#            cr.execute('''
#                            select sum(no_of_exit) as com_exit
#                            from import_shopper_track as test
#                            where test.date_customer_enter between %s and %s
#            ''', (start_date, end_date))
#            company_exit_data = cr.dictfetchall()
#            com_exit_traffic = company_exit_data[0]['com_exit']
#            logger.error("exit traffic for Company is %s",com_exit_traffic)
            cr.execute('''select sum(no_of_exit), stype.traffic_reduction
from import_shopper_track as test inner join sap_store sap on (test.store_id = sap.id)
                                left outer join stores_classification stype on (sap.store_classification = stype.id)
                                where test.date_customer_enter between %s and %s 
group by sap.id, stype.traffic_reduction''', (start_date, end_date))


            no_of_exit_company_data = cr.fetchall()
            for no_of_exit_company_id in no_of_exit_company_data:
                no_of_exit_company_id = list(no_of_exit_company_id)
                if no_of_exit_company_id[1] is None:
                    no_of_exit_company_id[1] = 0.00
                com_exit_traffic = com_exit_traffic + float(no_of_exit_company_id[0] - float(no_of_exit_company_id[0] * no_of_exit_company_id[1] / 100))
            logger.error("exit traffic for Company is %s",com_exit_traffic)
            #### code ends here

        if market_emp_search or region_emp_search:
            field_name = 'region_id'
            region_vals = self._get_basic_parameters_box_rev(cr, uid, field_name, region_id, start_date, end_date, condition_box_string, from_box_condition, prm_job_id, business_box_rule_ids, business_rev_rule_ids,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            all_region_tot_box = region_vals['tot_box']
            all_region_actual_box = region_vals['actual_box']
            region_pre_box_gross = region_vals['pre_count']
            tot_reg_pos_upg_box = region_vals['tot_emp_pos_upg_box']
            actual_region_rev = region_vals['actual_rev']
            tot_region_rev = region_vals['tot_rev']
            region_acc_rev = region_vals['apk_rev']
            reg_apk_count = region_vals['apk_count']
            region_smd_rev = region_vals['smd_rev']
            region_smd_box = region_vals['smd_box']
            region_pmd_rev = region_vals['pmd_rev']
            region_pmd_box = region_vals['pmd_box']
            region_react_rev = region_vals['react_rev']
            region_react_box = region_vals['react_box']
            region_noncomm_rev = region_vals['noncomm_rev']
            region_noncomm_box = region_vals['noncomm_box']
    #***************** Region VOC ************#
            cr.execute('''select ((avg(sat)+avg(knowledge)+avg(prof)+avg(cus)+avg(timel))/5)+avg(comb) as voc_count
from (select avg(overall_satisfaction) as sat,avg(knowledge) as knowledge,avg(professionalism_courtesy) as prof
,avg(valued_customer) as cus,avg(timeliness) as timel,avg(combined_plus_1) as comb
from import_voc_file voc, sap_tracker sap, market_tracker mkt 
where mkt.region_market_id = %s and mkt.end_date >= %s and mkt.start_date <= %s
and sap.market_id = mkt.market_id and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
and voc.store_id = sap.sap_id and voc.start_date >= %s and voc.end_date <= %s
group by voc.store_id) as voc''', (region_id, start_date, end_date, start_date, end_date, start_date, end_date))
            voc_data = cr.fetchall()
            region_voc = voc_data[0][0]
            if not region_voc:
                region_voc = 0.00
    # ******** no of exit *********** #        
            cr.execute('''select * from (
                select sum(no_of_exit) as exit_tot, stype.traffic_reduction, sap.id, test.date_customer_enter
                from import_shopper_track as test inner join sap_store sap on (test.store_id = sap.id)
                left outer join stores_classification stype on (sap.store_classification = stype.id)
                where test.date_customer_enter between %s and %s
                and test.sap_id in (select sap_data.sap_id from( 
                        select min(start_date) as date,sap_id from sap_tracker where 
                        sap_id in (
                            select distinct(sap.sap_id) from sap_tracker sap, market_tracker mkt
                            where mkt.region_market_id = %s and sap.market_id = mkt.market_id
                            and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
                            and mkt.end_date >= %s and mkt.start_date <= %s
                            ) 
                        group by sap_id
                        ) as sap_data
                    where %s::date > sap_data.date::date + 29
                )
                group by sap.id, stype.traffic_reduction, test.date_customer_enter
                ) as all_para 
                where all_para.exit_tot > 0''', (start_date, end_date, region_id, start_date, end_date, start_date, end_date, end_date))
            no_of_exit_region_data = cr.fetchall()
            for no_of_exit_region_id in no_of_exit_region_data:
                no_of_exit_region_id = list(no_of_exit_region_id)
                if no_of_exit_region_id[1] is None:
                    no_of_exit_region_id[1] = 0.00
                reg_no_of_exit = reg_no_of_exit + float(no_of_exit_region_id[0] - float(no_of_exit_region_id[0] * no_of_exit_region_id[1] / 100))
                region_traffic_stores.append(no_of_exit_region_id[2])
                if no_of_exit_region_id[3] not in region_traffic_date:
                    region_traffic_date.append(no_of_exit_region_id[3])
            cr.execute('''select sum(revenue),sum(tot_box) from (select imp.revenue,imp.tot_box from import_goals imp, sap_tracker sap, market_tracker mkt
                where mkt.region_market_id = %s and mkt.end_date >= %s and mkt.start_date <= %s
                and sap.market_id = mkt.market_id and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
                and imp.store_id = sap.sap_id and imp.start_date = %s group by imp.store_id,imp.revenue,imp.tot_box) as sum'''
            ,(region_id,start_date,end_date,start_date,end_date,start_date))
            region_revenue_goal = cr.fetchall()
            tot_region_revenue_goal = region_revenue_goal[0][0]
            tot_region_box_goal = region_revenue_goal[0][1]
            if not tot_region_revenue_goal:
                tot_region_revenue_goal = 0.00
            if not tot_region_box_goal:
                tot_region_box_goal = 0.00
            # ############## Market Revenue ###################################
            field_name = 'market_id'
            market_vals = self._get_basic_parameters_box_rev(cr, uid, field_name, market_id, start_date, end_date, condition_box_string, from_box_condition, prm_job_id, business_box_rule_ids, business_rev_rule_ids,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            all_market_tot_box = market_vals['tot_box']
            all_market_actual_box = market_vals['actual_box']
            market_pre_box_gross = market_vals['pre_count']
            tot_mkt_pos_upg_box = market_vals['tot_emp_pos_upg_box']
            actual_market_rev = market_vals['actual_rev']
            tot_market_rev = market_vals['tot_rev']
            market_acc_rev = market_vals['apk_rev']
            mkt_apk_count = market_vals['apk_count']            
            market_smd_rev = market_vals['smd_rev']
            market_smd_box = market_vals['smd_box']
            market_pmd_rev = market_vals['pmd_rev']
            market_pmd_box = market_vals['pmd_box']
            market_react_rev = market_vals['react_rev']
            market_react_box = market_vals['react_box']
            market_noncomm_rev = market_vals['noncomm_rev']
            market_noncomm_box = market_vals['noncomm_box']
        #************ Market VOC **************************#
            cr.execute('''select ((avg(sat)+avg(knowledge)+avg(prof)+avg(cus)+avg(timel))/5)+avg(comb) as voc_count
from (select avg(overall_satisfaction) as sat,avg(knowledge) as knowledge,avg(professionalism_courtesy) as prof
,avg(valued_customer) as cus,avg(timeliness) as timel,avg(combined_plus_1) as comb
from import_voc_file voc, sap_tracker sap, market_tracker mkt 
where sap.market_id = %s and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
and voc.store_id = sap.sap_id and voc.start_date >= %s and voc.end_date <= %s
group by voc.store_id) as voc''', (market_id, start_date, end_date, start_date, end_date))
            voc_data = cr.fetchall()
            market_voc = voc_data[0][0]
            if not market_voc:
                market_voc = 0.00
        # ******** no of exit *********** #        
            cr.execute('''select * from (
                select sum(no_of_exit) as exit_tot, stype.traffic_reduction, sap.id, test.date_customer_enter
                from import_shopper_track as test inner join sap_store sap on (test.store_id = sap.id)
                left outer join stores_classification stype on (sap.store_classification = stype.id)
                where test.date_customer_enter between %s and %s
                and test.sap_id in (
                                    select sap_data.sap_id from( 
                                        select min(start_date) as date,sap_id from sap_tracker where 
                                        sap_id in (
                                                    select distinct(sap.sap_id) from sap_tracker sap
                                                    where sap.market_id = %s and sap.end_date >= %s 
                                                    and sap.start_date <= %s and sap.store_inactive = false
                                                    ) 
                                        group by sap_id
                                    ) as sap_data
                                    where %s::date > sap_data.date::date + 29
                                )
                group by sap.id, stype.traffic_reduction, test.date_customer_enter
                ) as all_para 
                where all_para.exit_tot > 0''', (start_date, end_date, market_id, start_date, end_date, end_date))
            no_of_exit_market_data = cr.fetchall()
            for no_of_exit_market_id in no_of_exit_market_data:
                no_of_exit_market_id = list(no_of_exit_market_id)
                if no_of_exit_market_id[1] is None:
                    no_of_exit_market_id[1] = 0.00
                mkt_no_of_exit = mkt_no_of_exit + float(no_of_exit_market_id[0] - float(no_of_exit_market_id[0] * no_of_exit_market_id[1] / 100))
                market_traffic_stores.append(no_of_exit_market_id[2])
                if no_of_exit_market_id[3] not in market_traffic_date:
                    market_traffic_date.append(no_of_exit_market_id[3])
            cr.execute('''select sum(revenue),sum(tot_box) from (select imp.revenue, imp.tot_box from import_goals imp, sap_tracker sap
where sap.market_id = %s and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
and imp.store_id = sap.sap_id and imp.start_date = %s group by imp.store_id,imp.revenue,imp.tot_box) as sum ''',(market_id,start_date,end_date,start_date))
            market_revenue_goal = cr.fetchall()
            tot_market_revenue_goal = market_revenue_goal[0][0]
            tot_market_box_goal = market_revenue_goal[0][1]
            if not tot_market_revenue_goal:
                tot_market_revenue_goal = 0.00
            if not tot_market_box_goal:
                tot_market_box_goal = 0.00
        else:    
            # ############ Store Revenue ###############################
            # ####### Product_id means dsr_parent_id #####################
            field_name = 'store_id'
            store_vals = self._get_basic_parameters_box_rev(cr, uid, field_name, store_id, start_date, end_date, condition_box_string, from_box_condition, prm_job_id, business_box_rule_ids, business_rev_rule_ids,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            store_tot_box = store_vals['tot_box']
            store_actual_box = store_vals['actual_box']
            pre_box_gross = store_vals['pre_count']
            tot_sto_pos_upg_box = store_vals['tot_emp_pos_upg_box']
            actual_store_rev = store_vals['actual_rev']
            tot_store_rev = store_vals['tot_rev']
            store_acc_rev = store_vals['apk_rev']
            sto_apk_count = store_vals['apk_count']
            store_smd_rev = store_vals['smd_rev']
            store_smd_box = store_vals['smd_box']
            store_pmd_rev = store_vals['pmd_rev']
            store_pmd_box = store_vals['pmd_box']
            store_react_rev = store_vals['react_rev']
            store_react_box = store_vals['react_box']
            store_noncomm_rev = store_vals['noncomm_rev']
            store_noncomm_box = store_vals['noncomm_box']
  #************ Store VOC **************************#
            cr.execute('''select ((avg(overall_satisfaction)+avg(knowledge)+avg(professionalism_courtesy)+avg(valued_customer)+avg(timeliness))/5)+avg(combined_plus_1) as voc
from import_voc_file where start_date >= %s and end_date <= %s and store_id = %s''', (start_date, end_date, store_id))
            voc_data = cr.fetchall()
            store_voc = voc_data[0][0]
            if not store_voc:
                store_voc = 0.00            
    # ******** no of exit *********** #        
            cr.execute("select min(start_date) from sap_tracker where sap_id = %s",(store_id,))
            sap_min_date = cr.fetchall()
            sap_min_date = sap_min_date[0][0]
            if sap_min_date <= store_max_date_traffic.strftime('%Y-%m-%d'):
                cr.execute('''select * from (select sum(no_of_exit) as exit_tot,shop.date_customer_enter from import_shopper_track shop
                                                where shop.date_customer_enter between %s and %s and shop.store_id = %s
                                                group by shop.date_customer_enter) as all_para
                                where all_para.exit_tot > 0'''
                    , (start_date, end_date, store_id))
                exit_data = cr.fetchall()
                for exit_data_each in exit_data:
                    sto_no_of_exit = sto_no_of_exit + exit_data_each[0]
                    store_traffic_date.append(exit_data_each[1])
                if not sto_no_of_exit:
                    sto_no_of_exit = 0.00
                sto_no_of_exit = sto_no_of_exit - (sto_no_of_exit * traffic_red / 100)
    ##********* Store Revenue Goal ************#
            store_goal_ids = goal_obj.search(cr, uid, [('store_id', '=', store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
            if store_goal_ids:
                store_goal_data = goal_obj.browse(cr, uid, store_goal_ids)
                store_rev_goal = store_goal_data.revenue
                store_box_goal = store_goal_data.tot_box
            # ############# Total Reveue Employee Level and Total Box ################
            field_name = 'employee_id'
            emp_vals = self._get_basic_parameters_box_rev(cr, uid, field_name, emp_id, start_date, end_date, condition_box_string, from_box_condition, prm_job_id, business_box_rule_ids, business_rev_rule_ids,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            tot_box = emp_vals['tot_box']
            actual_box = emp_vals['actual_box']
            pre_count = emp_vals['pre_count']
            tot_emp_pos_upg_box = emp_vals['tot_emp_pos_upg_box']
            actual_rev = emp_vals['actual_rev']
            tot_rev = emp_vals['tot_rev']
            apk_rev = emp_vals['apk_rev']
            apk_count = emp_vals['apk_count']
            emp_smd_rev = emp_vals['smd_rev']
            emp_smd_box = emp_vals['smd_box']
            emp_pmd_rev = emp_vals['pmd_rev']
            emp_pmd_box = emp_vals['pmd_box']
            emp_react_rev = emp_vals['react_rev']
            emp_react_box = emp_vals['react_box']
            emp_noncomm_rev = emp_vals['noncomm_rev']
            emp_noncomm_box = emp_vals['noncomm_box']
            ######### Employee Revenue Goals ########
            split_goal_ids = split_goal_obj.search(cr, uid, [('employee_id', '=', emp_id), ('active', '=', True), ('start_date', '=', start_date)])
            if split_goal_ids:
                split_goal_data = split_goal_obj.browse(cr, uid, split_goal_ids[0])
                emp_rev_goal = split_goal_data.revenue
                emp_box_goal = split_goal_data.tot_box
        b = datetime.today()
        c = b - a
        print "Pre-data Calculation", c.total_seconds()
 ### ******************** Added for Feb-2015 changes ************************ ##############
        gross_rev = 0.00
        gross_box = 0.00
        smd_rev = 0.00
        smd_box = 0.00
        pmd_rev = 0.00
        pmd_box = 0.00
        react_rev = 0.00
        react_box = 0.00
        net_rev = 0.00
        net_box = 0.00
        noncomm_rev = 0.00
        noncomm_box = 0.00
        store_gross_rev = 0.00
        store_gross_box = 0.00
        store_smd_rev_2 = 0.00
        store_smd_box_2 = 0.00
        store_pmd_rev_2 = 0.00
        store_pmd_box_2 = 0.00
        store_react_rev_2 = 0.00
        store_react_box_2 = 0.00
        store_net_rev = 0.00
        store_noncomm_rev_2 = 0.00
        store_net_box = 0.00
        store_noncomm_box_2 = 0.00
        if emp_model_id == 'rsa' or emp_model_id == 'stl':
            gross_rev = actual_rev
            gross_box = actual_box
            smd_rev = emp_smd_rev
            smd_box = emp_smd_box
            pmd_rev = emp_pmd_rev
            pmd_box = emp_pmd_box
            react_rev = emp_react_rev
            react_box = emp_react_box
            net_rev = tot_rev
            net_box = tot_box
            noncomm_rev = emp_noncomm_rev
            noncomm_box = emp_noncomm_box
        elif emp_model_id == 'mm':
            gross_rev = actual_market_rev
            gross_box = all_market_actual_box
            smd_rev = market_smd_rev
            smd_box = market_smd_box
            pmd_rev = market_pmd_rev
            pmd_box = market_pmd_box
            react_rev = market_react_rev
            react_box = market_react_box
            net_rev = tot_market_rev
            net_box = all_market_tot_box
            noncomm_rev = market_noncomm_rev
            noncomm_box = market_noncomm_box
        elif emp_model_id == 'dos':
            gross_rev = actual_region_rev
            gross_box = all_region_actual_box
            smd_rev = region_smd_rev
            smd_box = region_smd_box
            pmd_rev = region_pmd_rev
            pmd_box = region_pmd_box
            react_rev = region_react_rev
            react_box = region_react_box
            net_rev = tot_region_rev
            net_box = all_region_tot_box
            noncomm_rev = region_noncomm_rev
            noncomm_box = region_noncomm_box
        if emp_model_id == 'stl' or emp_model_id == 'mid' or emp_model_id == 'rsm':
            store_gross_rev = actual_store_rev
            store_gross_box = store_actual_box
            store_smd_rev_2 = store_smd_rev
            store_smd_box_2 = store_smd_box
            store_pmd_rev_2 = store_pmd_rev
            store_pmd_box_2 = store_pmd_box
            store_react_rev_2 = store_react_rev
            store_react_box_2 = store_react_box
            store_net_rev = tot_store_rev
            store_net_box = store_tot_box
            store_noncomm_rev_2 = store_noncomm_rev
            store_noncomm_box_2 = store_noncomm_box
        ######################### Team Commission ###################################
        voc_achieved = 0.00
        voc_payout = 0.00
        voc_target = 0.00
        voc_string = str("")
        comm_voc_master = self.pool.get('comm.voc.commission')
        comm_voc_store_record_id = comm_voc_master.search(cr, uid, [('comm_designation', '=', emp_des),('spiff_model','=',model_store_search_id[0]),('comm_start_date', '<=', start_date),('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_voc_store_record_id:
            voc_achieved = store_voc
            voc_vals = self._calculate_team_voc_commission(cr, uid, comm_voc_store_record_id, tot_rev, voc_achieved, emp_model_id, context=context)
            voc_payout = voc_vals['voc_payout']
            voc_achieved = voc_vals['voc_achieved']
            voc_target = voc_vals['voc_target']
            voc_string = voc_vals['voc_string']
        comm_voc_market_record_id = comm_voc_master.search(cr, uid, [('comm_designation', '=', emp_des),('spiff_model','=',model_market_search_id[0]),('comm_start_date', '<=', start_date),('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_voc_market_record_id:
            voc_achieved = market_voc
            voc_vals = self._calculate_team_voc_commission(cr, uid, comm_voc_market_record_id, tot_rev, voc_achieved, emp_model_id, context=context)
            voc_payout = voc_vals['voc_payout']
            voc_achieved = voc_vals['voc_achieved']
            voc_target = voc_vals['voc_target']
            voc_string = voc_vals['voc_string']
        comm_voc_region_record_id = comm_voc_master.search(cr, uid, [('comm_designation', '=', emp_des),('spiff_model','=',model_region_search_id[0]),('comm_start_date', '<=', start_date),('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_voc_region_record_id:
            voc_achieved = region_voc
            voc_vals = self._calculate_team_voc_commission(cr, uid, comm_voc_region_record_id, tot_rev, voc_achieved, emp_model_id, context=context)
            voc_payout = voc_vals['voc_payout']
            voc_achieved = voc_vals['voc_achieved']
            voc_target = voc_vals['voc_target']
            voc_string = voc_vals['voc_string']
        ####################### Revenue Per Hour Commission ###########################
        labor_prod_achieved = str("")
        labor_prod_payout = 0.00
        labor_prod_actual = 0.00
        labor_prod_target = str("")
        rsa_rph_payout_tier = str("")
        actual_labor_budget = 0.00
        rph_import_goal = 0.00
        rsa_rph_target = 0.00
        comm_rph_master = self.pool.get('comm.rph.commission')
        comm_rph_emp_record_id = comm_rph_master.search(cr, uid, [('comm_designation', '=', emp_des),('spiff_model','=',model_emp_search_id[0]),('comm_start_date', '<=', start_date),('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_rph_emp_record_id:
            cr.execute("select (sum(reg_hours)+sum(over_hours)) as count from import_employee_hours where employee_id = %s and date between %s and %s",(emp_id,start_date,end_date))
            emp_hour_data = cr.fetchall()
            emp_hour = emp_hour_data[0][0]
            if not emp_hour:
                emp_hour = 0.00
            cr.execute('''select (%s * 100 / (sum(monthly_budgeted_hours) * %s/%s)) as labor_hours_budget 
                from labour_staffing where store_id = %s and start_date = %s''',(emp_hour,delta_date,current_days_month,store_id,start_date))
            labor_budget_data = cr.fetchall()
            labor_budget = labor_budget_data[0][0]            
            if not labor_budget:
                labor_budget = 0.00
            cr.execute("select sum(rph_goal) from spliting_goals where employee_id=%s and start_date='%s' "%(emp_id,start_date))
            emp_rph_target = cr.fetchall()
            emp_rph_target = emp_rph_target[0][0]
            if not emp_rph_target:
                emp_rph_target = 0.00
            field_name = 'employee_id'
            rph_vals = self._calculate_rph_commission(cr,uid,comm_rph_emp_record_id,tot_rev,emp_hour,labor_budget,emp_rph_target,field_name,emp_id,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            labor_prod_payout = rph_vals['rsa_rph_payout']
            labor_prod_target = rph_vals['labor_prod_target']
            rsa_rph_payout_tier = rph_vals['rsa_rph_payout_tier']
            rsa_rph_target = rph_vals['rsa_rph_target']
            rph_import_goal = emp_rph_target
            actual_labor_budget = labor_budget
            rsa_rph_target = round(rsa_rph_target, 2)
            labor_prod_achieved += str("$ %s, "%(rsa_rph_target))
            labor_prod_achieved = labor_prod_achieved[:-2]
            labor_prod_actual = actual_rev
        comm_rph_store_record_id = comm_rph_master.search(cr, uid, [('comm_designation', '=', emp_des),('spiff_model','=',model_store_search_id[0]),('comm_start_date', '<=', start_date),('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_rph_store_record_id:
            cr.execute("select (sum(reg)+sum(ot)) as count from import_store_hours where store_id = %s and date between %s and %s",(store_id,start_date,end_date))
            emp_hour_data = cr.fetchall()
            emp_hour = emp_hour_data[0][0]
            if not emp_hour:
                emp_hour = 0.00
            cr.execute('''select (%s * 100 / (sum(monthly_budgeted_hours) * %s/%s)) as labor_hours_budget from labour_staffing 
                where store_id = %s and start_date = %s''',(emp_hour,delta_date,current_days_month,store_id, start_date))
            labor_budget_data = cr.fetchall()
            labor_budget = labor_budget_data[0][0]
            if not labor_budget:
                labor_budget = 0.00
            cr.execute("select sum(rph_goal) from import_goals where store_id=%s and start_date='%s' "%(store_id,start_date))
            store_rph_target = cr.fetchall()
            store_rph_target = store_rph_target[0][0]
            if not store_rph_target:
                store_rph_target = 0.00
            field_name = 'store_id'
            rph_vals = self._calculate_rph_commission(cr,uid,comm_rph_store_record_id,tot_store_rev,emp_hour,labor_budget,store_rph_target,field_name,store_id,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            labor_prod_payout = rph_vals['rsa_rph_payout']
            labor_prod_target = rph_vals['labor_prod_target']
            rsa_rph_payout_tier = rph_vals['rsa_rph_payout_tier']
            rsa_rph_target = rph_vals['rsa_rph_target']
            rph_import_goal = store_rph_target
            actual_labor_budget = labor_budget
            rsa_rph_target = round(rsa_rph_target, 2)
            labor_prod_achieved += str("$ %s, "%(rsa_rph_target))
            labor_prod_achieved = labor_prod_achieved[:-2]
            labor_prod_actual = actual_store_rev
        comm_rph_market_record_id = comm_rph_master.search(cr, uid, [('comm_designation', '=', emp_des),('spiff_model','=',model_market_search_id[0]),('comm_start_date', '<=', start_date),('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_rph_market_record_id:
            cr.execute('''select (sum(hr.reg)+sum(hr.ot)) as count from import_store_hours hr
where hr.date between %s and %s 
and hr.store_id in (select distinct(sap.sap_id) from sap_tracker sap
            where sap.market_id = %s and sap.end_date >= %s 
            and sap.start_date <= %s and sap.store_inactive = false)''',(start_date,end_date,market_id,start_date,end_date))
            emp_hour_data = cr.fetchall()
            emp_hour = emp_hour_data[0][0]
            if not emp_hour:
                emp_hour = 0.00
            cr.execute('''select (%s * 100 / (sum(monthly_budgeted_hours) * %s/%s)) as labor_hours_budget from labour_staffing
where start_date = %s
and store_id in (select distinct(sap.sap_id) from sap_tracker sap
            where sap.market_id = %s and sap.end_date >= %s 
            and sap.start_date <= %s and sap.store_inactive = false)''',(emp_hour,delta_date,current_days_month,start_date,market_id,start_date,end_date))
            labor_budget_data = cr.fetchall()
            labor_budget = labor_budget_data[0][0]
            if not labor_budget:
                labor_budget = 0.00
            cr.execute('''select sum(rph_goals) from market_profitability_rph where market_id = %s and start_date=%s ''',(market_id,start_date))
            market_rph_target = cr.fetchall()
            market_rph_target = market_rph_target[0][0]
            if not market_rph_target:
                market_rph_target = 0.00
            field_name = 'market_id'
            rph_vals = self._calculate_rph_commission(cr,uid,comm_rph_market_record_id,tot_market_rev,emp_hour,labor_budget,market_rph_target,field_name,market_id,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            labor_prod_payout = rph_vals['rsa_rph_payout']
            labor_prod_target = rph_vals['labor_prod_target']
            rsa_rph_payout_tier = rph_vals['rsa_rph_payout_tier']
            rsa_rph_target = rph_vals['rsa_rph_target']
            rph_import_goal = market_rph_target
            actual_labor_budget = labor_budget
            rsa_rph_target = round(rsa_rph_target, 2)
            labor_prod_achieved += str("$ %s, "%(rsa_rph_target))
            labor_prod_achieved = labor_prod_achieved[:-2]
            labor_prod_actual = actual_market_rev
        comm_rph_region_record_id = comm_rph_master.search(cr, uid, [('comm_designation', '=', emp_des),('spiff_model','=',model_region_search_id[0]),('comm_start_date', '<=', start_date),('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_rph_region_record_id:
            cr.execute('''select (sum(hr.reg)+sum(hr.ot)) as count from import_store_hours hr
where hr.date between %s and %s
and hr.store_id in (select distinct(sap.sap_id) from sap_tracker sap, market_tracker mkt
            where mkt.region_market_id = %s and sap.market_id = mkt.market_id
            and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
            and mkt.end_date >= %s and mkt.start_date <= %s) ''',(start_date,end_date,region_id,start_date,end_date,start_date,end_date))
            emp_hour_data = cr.fetchall()
            emp_hour = emp_hour_data[0][0]
            if not emp_hour:
                emp_hour = 0.00
            cr.execute('''select (%s * 100 / (sum(monthly_budgeted_hours) * %s/%s)) as labor_hours_budget from labour_staffing hr
where hr.start_date = %s
and hr.store_id in (select distinct(sap.sap_id) from sap_tracker sap, market_tracker mkt
            where mkt.region_market_id = %s and sap.market_id = mkt.market_id
            and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
            and mkt.end_date >= %s and mkt.start_date <= %s) ''',(emp_hour,delta_date,current_days_month,start_date,region_id,start_date,end_date,start_date,end_date))
            labor_budget_data = cr.fetchall()
            labor_budget = labor_budget_data[0][0]
            if not labor_budget:
                labor_budget = 0.00
            cr.execute('''select avg(prof.rph_goals) from market_profitability_rph prof
where prof.start_date = %s and prof.market_id in (select distinct(market_id) from market_tracker
where region_market_id = %s and end_date >= %s and start_date <= %s)''',(start_date,region_id,start_date,end_date))
            region_rph_target = cr.fetchall()
            region_rph_target = region_rph_target[0][0]
            if not region_rph_target:
                region_rph_target = 0.00
            field_name = 'region_id'
            rph_vals = self._calculate_rph_commission(cr,uid,comm_rph_region_record_id,tot_region_rev,emp_hour,labor_budget,region_rph_target,field_name,region_id,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            labor_prod_payout = rph_vals['rsa_rph_payout']
            labor_prod_target = rph_vals['labor_prod_target']
            rsa_rph_payout_tier = rph_vals['rsa_rph_payout_tier']
            rsa_rph_target = rph_vals['rsa_rph_target']
            rph_import_goal = region_rph_target
            actual_labor_budget = labor_budget
            rsa_rph_target = round(rsa_rph_target, 2)
            labor_prod_achieved += str("$ %s, "%(rsa_rph_target))
            labor_prod_achieved = labor_prod_achieved[:-2]
            labor_prod_actual = actual_region_rev
    # **************** Feb-2015 changes ends here ****************** ##########    
        # ############### Base Commission ###########################################
        base_payout = 0.00
        base_tot_rev = str("")
        base_rev_string = str("")
        comm_obj = self.pool.get('comm.basic.commission.formula')
        comm_emp_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model','=',model_emp_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_emp_search_ids:
            comm_emp_data = comm_obj.browse(cr, uid, comm_emp_search_ids[0])
            comm_rev_percent = comm_emp_data.comm_percent
            comm_rev_fix = comm_emp_data.comm_flat_amount
            print_tot_rev = round(tot_rev, 2)
            base_tot_rev += str("%s, "%(print_tot_rev))
            if comm_rev_percent > 0.00:
                base_rev_string += str("Revenue Payout @ %s"%(comm_rev_percent))
                base_rev_string += str(" %")
                base_payout = base_payout + (tot_rev * comm_rev_percent) / 100
            elif comm_rev_fix > 0.00:
                base_rev_string += str("Revenue Payout %s $"%(comm_rev_fix))
                base_payout = base_payout + comm_rev_fix
        comm_store_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model','=',model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_store_search_ids:
            comm_emp_data = comm_obj.browse(cr, uid, comm_store_search_ids[0])
            comm_rev_percent = comm_emp_data.comm_percent
            comm_rev_fix = comm_emp_data.comm_flat_amount
            print_tot_rev = round(tot_store_rev, 2)
            base_tot_rev += str("%s, "%(print_tot_rev))
            if comm_rev_percent > 0.00:
                base_rev_string += str("Revenue Payout @ %s"%(comm_rev_percent))
                base_rev_string += str(" %")
                base_payout = base_payout + (tot_store_rev * comm_rev_percent) / 100
            elif comm_rev_fix > 0.00:
                base_rev_string += str("Revenue Payout %s $"%(comm_rev_fix))
                base_payout = base_payout + comm_rev_fix
        comm_market_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model','=',model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_market_search_ids:
            comm_emp_data = comm_obj.browse(cr, uid, comm_market_search_ids[0])
            comm_rev_percent = comm_emp_data.comm_percent
            comm_rev_fix = comm_emp_data.comm_flat_amount
            print_tot_rev = round(tot_market_rev, 2)
            base_tot_rev += str("%s, "%(print_tot_rev))
            if comm_rev_percent > 0.00:
                base_rev_string += str("Revenue Payout @ %s"%(comm_rev_percent))
                base_rev_string += str(" %")
                base_payout = base_payout + (tot_market_rev * comm_rev_percent) / 100
            elif comm_rev_fix > 0.00:
                base_rev_string += str("Revenue Payout %s $"%(comm_rev_fix))
                base_payout = base_payout + comm_rev_fix
        comm_region_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model','=',model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_region_search_ids:
            comm_emp_data = comm_obj.browse(cr, uid, comm_region_search_ids[0])
            comm_rev_percent = comm_emp_data.comm_percent
            comm_rev_fix = comm_emp_data.comm_flat_amount
            print_tot_rev = round(tot_region_rev, 2)
            base_tot_rev += str("%s, "%(print_tot_rev))
            if comm_rev_percent > 0.00:
                base_rev_string += str("Revenue Payout @ %s"%(comm_rev_percent))
                base_rev_string += str(" %")
                base_payout = base_payout + (tot_region_rev * comm_rev_percent) / 100
            elif comm_rev_fix > 0.00:
                base_rev_string += str("Revenue Payout %s $"%(comm_rev_fix))
                base_payout = base_payout + comm_rev_fix
        base_tot_rev = base_tot_rev[:-2]
        # ############### KICKER Formula ########################
        kicker_obj = self.pool.get('comm.kicker.commission.formula')
        split_goal_obj = self.pool.get('spliting.goals')
        goal_obj = self.pool.get('import.goals')
        goal_ids = goal_obj.search(cr, uid, [('store_id', '=', store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
        split_goal_ids = split_goal_obj.search(cr, uid, [('employee_id', '=', emp_id), ('active', '=', True), ('store_id', '=', store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
        tot_store_revenue = 0.00
        tot_box_goal = 0.00
        per_worker_rev = 0.00
        per_worker_box_goal = 0.00
        kicker_rev_goal_percent = 0.00
        kicker_box_goal_percent = 0.00
        kicker_store_rev_goal_percent = 0.00
        kicker_rev_goal_payout = 0.00
        kicker_box_goal_payout = 0.00
        kicker_store_rev_goal_payout = 0.00
        if goal_ids:
            goal_data = goal_obj.browse(cr, uid, goal_ids[0])
            # tot_box_goal = (goal_data.tot_box * delta_date)/days_in_month#krishna code
            tot_box_goal = goal_data.tot_box  # shashank code 1/12
            # tot_store_revenue = (goal_data.revenue * delta_date)/days_in_month#krishna code
            tot_store_revenue = goal_data.revenue  # shashank code 1/12
        if split_goal_ids:
            split_goal_data = split_goal_obj.browse(cr, uid, split_goal_ids[0])        
            # per_worker_box_goal = (split_goal_data.tot_box * delta_date)/days_in_month#krishna code
            per_worker_box_goal = split_goal_data.tot_box  # shashank code 1/12
            # per_worker_rev = (split_goal_data.revenue * delta_date)/days_in_month#krishna code
            per_worker_rev = split_goal_data.revenue  # shashank code 1/12
        if per_worker_rev > 0.00:    
            kicker_rev_goal_percent = (actual_rev * 100) / per_worker_rev
        if per_worker_box_goal > 0.00:
            kicker_box_goal_percent = (actual_box * 100) / per_worker_box_goal
        if tot_store_revenue > 0.00:
            kicker_store_rev_goal_percent = (actual_store_rev * 100) / tot_store_revenue
        if kicker_rev_goal_percent >= 100.00:
            kicker_rev_goal_payout = self._kicker_rev_goal_payout(cr, uid, emp_des, start_date, end_date, tot_rev)
        if kicker_box_goal_percent >= 100.00:
            kicker_box_goal_payout = self._kicker_box_goal_payout(cr, uid, emp_des, start_date, end_date, tot_rev)
        if kicker_store_rev_goal_percent >= 100.00:
            kicker_store_rev_goal_payout = self._kicker_store_rev_goal_payout(cr, uid, emp_des, start_date, end_date, tot_rev)          
        # ################ Base Box Commission Calculation #####################
        comm_obj = self.pool.get('comm.base.box.commission.formula')
        comm_emp_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des),('spiff_model','=',model_emp_search_id[0]),('comm_start_date', '<=', start_date),('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        base_box_payout = 0.00
        base_box_actual = 0.00
        base_box_goal = 0.00
        base_box_hit_percent = 0.00
        base_box_pay_tier = str('')
        if comm_emp_search_ids:
            field_name = 'employee_id'
            base_box_emp_data = self._calculate_base_box_hit(cr, uid, comm_emp_search_ids, emp_box_goal, field_name, start_date, end_date, emp_id, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            base_box_payout = base_box_emp_data['base_box_payout']
            base_box_actual = base_box_emp_data['base_box_actual']
            base_box_goal = base_box_emp_data['base_box_goal']
            base_box_hit_percent = base_box_emp_data['base_box_hit_percent']
            base_box_pay_tier = base_box_emp_data['base_box_pay_tier']
        comm_store_search_ids = comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('spiff_model','=',model_store_search_id[0]),('comm_start_date','<=',start_date),('comm_end_date','>=',end_date),('comm_inactive','=',False)])
        if comm_store_search_ids:
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    base_box_emp_data = self._calculate_base_box_hit(cr, uid, comm_store_search_ids, store_box_goal, field_name, start_date, end_date, store_multi_id, tot_store_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    base_box_payout_pre = base_box_emp_data['base_box_payout']
                    base_box_actual = base_box_emp_data['base_box_actual']
                    base_box_goal = base_box_emp_data['base_box_goal']
                    base_box_hit_percent = base_box_emp_data['base_box_hit_percent']
                    base_box_pay_tier = base_box_emp_data['base_box_pay_tier']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        base_box_payout = base_box_payout_pre
                    else:
                        base_box_payout = base_box_payout + (base_box_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                count_multi = count_multi + 1
        comm_market_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_market_search_ids:
            field_name = 'market_id'
            base_box_emp_data = self._calculate_base_box_hit(cr, uid, comm_market_search_ids, tot_market_box_goal, field_name, start_date, end_date, market_id, tot_market_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            base_box_payout = base_box_emp_data['base_box_payout']
            base_box_actual = base_box_emp_data['base_box_actual']
            base_box_goal = base_box_emp_data['base_box_goal']
            base_box_hit_percent = base_box_emp_data['base_box_hit_percent']
            base_box_pay_tier = base_box_emp_data['base_box_pay_tier']
        comm_region_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_region_search_ids:
            field_name = 'region_id'
            base_box_emp_data = self._calculate_base_box_hit(cr, uid, comm_region_search_ids, tot_region_box_goal, field_name, start_date, end_date, region_id, tot_region_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            base_box_payout = base_box_emp_data['base_box_payout']
            base_box_actual = base_box_emp_data['base_box_actual']
            base_box_goal = base_box_emp_data['base_box_goal']
            base_box_hit_percent = base_box_emp_data['base_box_hit_percent']
            base_box_pay_tier = base_box_emp_data['base_box_pay_tier']
        a = datetime.today()
        c = a - b
        print "Base,Kicker,Base Box", c.total_seconds()
        # ########## Vision Reward Formula ############################# Need TO Verify
        comm_obj = self.pool.get('comm.vision.rewards.elite.bonus')
        comm_emp_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        vision_reward_sale_top_company_payout = 0.00
        vision_reward_sale_top_market_payout = 0.00
        vision_reward_sale_top_company_rev = 0.00
        vision_reward_sale_top_market_rev = 0.00
        vision_reward_sale_top_percent_store = 0.00
        vision_reward_sale_top_percent_store_pay = 0.00
        vision_reward_stl_top_company_rev = 0.00
        vision_reward_stl_top_company_payout = 0.00
        vision_reward_mm_top_market_rev = 0.00
        vision_reward_mm_top_market_payout = 0.00
        vision_reward_mm_top_leader_market_rev = 0.00
        vision_reward_mm_top_leader_market_payout = 0.00
        vision_reward_dos_top_region_rev = 0.00
        vision_reward_dos_top_region_payout = 0.00
        vision_reward_dos_top_leader_rev = 0.00
        vision_reward_dos_top_leader_payout = 0.00
  # ************* new fields added 2015-Feb *********************#      
        vision_reward_sale_top_comp_leader_payout = 0.00
        vision_reward_sale_top_comp_leader_rev = 0.00
        rsa_top_rank_comp_string = str("")
        rsa_top_rank_rev_comp_string = str("")
        store_top_comp_string = str("")
        market_top_comp_string = str("")
        region_top_comp_string = str("")
        from_comm_top_company_count = 0
        to_comm_top_company_count = 0
#         if comm_emp_search_ids:
#             vision_reward_sale_top_comp_leader_rank = 0
#             vision_reward_sale_top_company_rank = 0
#             vision_reward_sale_top_comp_leader_rev = 0
#             vision_reward_sale_top_company_rev = 0
#             cr.execute('''select count(hr.id) from hr_employee hr, hr_job job, resource_resource res
# where hr.resource_id = res.id and res.active=true
# and hr.job_id=job.id and job.model_id in ('rsa','stl')''')
#             hr_ids = cr.fetchall()
#             hr_count = hr_ids[0][0]
#             # ###################### For Sales Associate Commission #########################
#             for comm_emp_search_id in comm_emp_search_ids:
#                 comm_obj_emp_browse = comm_obj.browse(cr, uid, comm_emp_search_id)
#                 company_top_hr = []
#                 company_top_rank = []
#                 comm_formula_multi_lines = comm_obj_emp_browse.formula_multi_lines
#                 for comm_formula_multi_lines_each in comm_formula_multi_lines:
#                     if comm_formula_multi_lines_each.cal_type == 'count':
#                         from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
#                         to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
#                     elif comm_formula_multi_lines_each.cal_type == 'perc':
#                         from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * hr_count) / 100
#                         to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * hr_count) / 100
#                     if comm_formula_multi_lines_each.rank_base == 'all':
#                         cr.execute('''select * from sp_getRanking_SalesRep(%s,%s,%s,null,null)''', (100, start_date, end_date))
#                         company_top_hr_ids = cr.fetchall()
#                         for company_top_hr_id in company_top_hr_ids:
#                             company_top_hr.append(company_top_hr_id[0])
#                             company_top_rank.append(company_top_hr_id[1])
#                         if comm_formula_multi_lines_each.pay_rev > 0.00:
#                             rsa_top_rank_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
#                             rsa_top_rank_comp_string += str(" % of RSA Revenue")
#                         elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                             rsa_top_rank_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
#                         if emp_id in company_top_hr:
#                             vision_reward_sale_top_comp_leader_rank = company_top_hr.index(emp_id) + 1                
#                         if vision_reward_sale_top_comp_leader_rank > 0 and len(company_top_rank) >= vision_reward_sale_top_comp_leader_rank:
#                             vision_reward_sale_top_comp_leader_rev = company_top_rank[vision_reward_sale_top_comp_leader_rank-1]
#                         if (emp_id in company_top_hr) and (vision_reward_sale_top_comp_leader_rev >= from_comm_top_company_count) and (vision_reward_sale_top_comp_leader_rev <= to_comm_top_company_count):
#                             if comm_formula_multi_lines_each.pay_rev > 0.00:
#                                 vision_reward_sale_top_comp_leader_payout = (tot_rev * comm_formula_multi_lines_each.pay_rev) / 100
#                             elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                                 vision_reward_sale_top_comp_leader_payout = comm_formula_multi_lines_each.flat_pay
#                     elif comm_formula_multi_lines_each.rank_base == 'rev':
#                         cr.execute('''select * from get_revenue_perc_by_emp_odoo(%s, %s, 'rsa', %s)''', (start_date, end_date,100))
#                         company_top_hr_ids = cr.fetchall()
#                         for company_top_hr_id in company_top_hr_ids:
#                             company_top_hr.append(company_top_hr_id[0])
#                             company_top_rank.append(company_top_hr_id[2])                        
#                         if comm_formula_multi_lines_each.pay_rev > 0.00:
#                             rsa_top_rank_rev_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
#                             rsa_top_rank_rev_comp_string += str(" % of RSA Revenue")
#                         elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                             rsa_top_rank_rev_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
#                         if emp_id in company_top_hr:
#                             vision_reward_sale_top_company_rank = company_top_hr.index(emp_id) + 1                
#                         if vision_reward_sale_top_company_rank > 0 and len(company_top_rank) >= vision_reward_sale_top_company_rank:
#                             vision_reward_sale_top_company_rev = company_top_rank[vision_reward_sale_top_company_rank - 1]
#                         if (emp_id in company_top_hr) and (vision_reward_sale_top_company_rev >= from_comm_top_company_count) and (vision_reward_sale_top_company_rev <= to_comm_top_company_count):
#                             if comm_formula_multi_lines_each.pay_rev > 0.00:
#                                 vision_reward_sale_top_company_payout = (tot_rev * comm_formula_multi_lines_each.pay_rev) / 100
#                             elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                                 vision_reward_sale_top_company_payout = comm_formula_multi_lines_each.flat_pay
#         # ################ For STL/MID/Kiosk Store Manager / Store Manager / Mall and Training Store Manager ###############
#         comm_stl_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
#         if comm_stl_search_ids:
#             vision_reward_sale_top_percent_store = 0
#             cr.execute("select count(distinct(sap_id)) from sap_tracker where store_inactive=false and end_date >= %s",(start_date,))
#             store_count = cr.fetchall()
#             store_count = store_count[0][0]
#             for comm_stl_search_id in comm_stl_search_ids:
#                 comm_stl_browse_data = comm_obj.browse(cr, uid, comm_stl_search_ids[0])
#                 # #################### Sales Leaderboard: Top 10% of Stores ######################
#                 store_top_hr = []
#                 store_top_rank = []                
#                 cr.execute('''select * from sp_getRanking_RMS(%s,%s,%s,'store','perc')''', (100, start_date, end_date))
#                 store_top_hr_ids = cr.fetchall()
#                 count = 0
#                 comm_formula_multi_lines = comm_stl_browse_data.formula_multi_lines
#                 for comm_formula_multi_lines_each in comm_formula_multi_lines:
#                     if comm_formula_multi_lines_each.cal_type == 'count':
#                         from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
#                         to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
#                     elif comm_formula_multi_lines_each.cal_type == 'perc':
#                         from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * store_count) / 100
#                         to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * store_count) / 100
#                     if comm_formula_multi_lines_each.rank_base == 'all':
#                         for store_top_hr_id in store_top_hr_ids:
#                             store_top_hr.append(store_top_hr_id[0])
#                             store_top_rank.append(store_top_hr_id[1])
#                         if store_id in store_top_hr:
#                             vision_reward_sale_top_percent_store = store_top_hr.index(store_id) + 1
#                         if vision_reward_sale_top_percent_store > 0 and len(store_top_rank) >= vision_reward_sale_top_percent_store:
#                             vision_reward_sale_top_percent_store = store_top_rank[vision_reward_sale_top_percent_store-1]
#                         if (store_id in store_top_hr) and (vision_reward_sale_top_percent_store >= from_comm_top_company_count) and (vision_reward_sale_top_percent_store <= to_comm_top_company_count):
#                             if comm_formula_multi_lines_each.pay_rev > 0.00:
#                                 vision_reward_sale_top_percent_store_pay = (tot_store_rev * comm_formula_multi_lines_each.pay_rev) / 100
#                             elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                                 vision_reward_sale_top_percent_store_pay = comm_formula_multi_lines_each.flat_pay
#                     count = count + 1
#                     if (vision_reward_sale_top_percent_store_pay > 0) or (count == len(comm_formula_multi_lines)):
#                         if comm_formula_multi_lines_each.pay_rev > 0.00:
#                             store_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
#                             store_top_comp_string += str(" % of Store Revenue")
#                         elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                             store_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
#                         break
#   #******************# ################### For Market Manager ############################
#         comm_mm_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
#         if comm_mm_search_ids:
#             cr.execute("select count(distinct(market_id)) from market_tracker where end_date >= %s",(start_date,))
#             market_count = cr.fetchall()
#             market_count = market_count[0][0]
#             vision_reward_mm_top_leader_market_rev = 0
#             for comm_mm_browse_data in comm_obj.browse(cr, uid, comm_mm_search_ids):
#                 top_mm_markets_ids = []
#                 top_mm_markets_ranks = []
#                 count = 0
#                 cr.execute('''select * from sp_getRanking_RMS(100,%s,%s,'market','perc')''', (start_date, end_date))
#                 top_mm_markets = cr.fetchall()
#                 # ############## Top 5 Markets WV Leaderboard ########################
#                 comm_formula_multi_lines = comm_mm_browse_data.formula_multi_lines
#                 for comm_formula_multi_lines_each in comm_formula_multi_lines:
#                     if comm_formula_multi_lines_each.cal_type == 'count':
#                         from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
#                         to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
#                     elif comm_formula_multi_lines_each.cal_type == 'perc':
#                         from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * market_count) / 100
#                         to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * market_count) / 100
#                     if comm_formula_multi_lines_each.rank_base == 'all':                   
#                         for top_mm_market_id in top_mm_markets:
#                             top_mm_markets_ids.append(top_mm_market_id[0])
#                             top_mm_markets_ranks.append(top_mm_market_id[1])
#                         if market_id in top_mm_markets_ids:
#                             vision_reward_mm_top_leader_market_rev = top_mm_markets_ids.index(market_id) + 1
#                         if vision_reward_mm_top_leader_market_rev > 0 and len(top_mm_markets_ranks) >= vision_reward_mm_top_leader_market_rev:
#                             vision_reward_mm_top_leader_market_rev = top_mm_markets_ranks[vision_reward_mm_top_leader_market_rev-1]
#                         if (market_id in top_mm_markets_ids) and (vision_reward_mm_top_leader_market_rev >= from_comm_top_company_count) and (vision_reward_mm_top_leader_market_rev <= to_comm_top_company_count):
#                             if comm_formula_multi_lines_each.pay_rev > 0.00:
#                                 vision_reward_mm_top_leader_market_payout = (tot_market_rev * comm_formula_multi_lines_each.pay_rev) / 100
#                             elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                                 vision_reward_mm_top_leader_market_payout = comm_formula_multi_lines_each.flat_pay
#                     count = count + 1
#                     if (vision_reward_mm_top_leader_market_payout > 0) or (count == len(comm_formula_multi_lines)):
#                         if comm_formula_multi_lines_each.pay_rev > 0.00:
#                             market_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
#                             market_top_comp_string += str(" % of Market Revenue")
#                         elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                             market_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
#                         break
#             # ################ Top Region Leaderboard Ranking ###########################
#         comm_dos_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
#         if comm_dos_search_ids:
#             cr.execute("select count(distinct(region_id)) from region_tracker where end_date >= %s",(start_date,))
#             region_ids = cr.fetchall()
#             region_count = region_ids[0][0]
#             vision_reward_dos_top_region_rev = 0
#             comm_dos_browse_data = comm_obj.browse(cr, uid, comm_dos_search_ids[0])
#             # ################## Top Region Leaderboard Ranking #############################
#             top_dos_regions_ids = []
#             top_dos_regions_ranks = []

#             comm_formula_multi_lines = comm_dos_browse_data.formula_multi_lines
#             count = 0
#             for comm_formula_multi_lines_each in comm_formula_multi_lines:
#                 if comm_formula_multi_lines_each.cal_type == 'count':
#                     from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
#                     to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
#                 elif comm_formula_multi_lines_each.cal_type == 'perc':
#                     from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * region_count) / 100
#                     to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * region_count) / 100
#                 if comm_formula_multi_lines_each.rank_base == 'all':
#                     cr.execute('''select * from sp_getRanking_RMS(100,%s,%s,'region','perc')''', (start_date, end_date))
#                     top_dos_regions = cr.fetchall()
#                     for top_dos_regions_id in top_dos_regions:
#                         top_dos_regions_ids.append(top_dos_regions_id[0])
#                         top_dos_regions_ranks.append(top_dos_regions_id[1])
#                     if region_id in top_dos_regions_ids:
#                         vision_reward_dos_top_region_rev = top_dos_regions_ids.index(region_id) + 1
#                     if vision_reward_dos_top_region_rev > 0 and len(top_dos_regions_ranks) >= vision_reward_dos_top_region_rev:
#                         vision_reward_dos_top_region_rev = top_dos_regions_ranks[vision_reward_dos_top_region_rev-1]
#                     if (region_id in top_dos_regions_ids) and (vision_reward_dos_top_region_rev >= from_comm_top_company_count) and (vision_reward_dos_top_region_rev <= to_comm_top_company_count):
#                         if comm_formula_multi_lines_each.pay_rev > 0.00:
#                             vision_reward_dos_top_leader_payout = (tot_region_rev * comm_formula_multi_lines_each.pay_rev) / 100
#                         elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                             vision_reward_dos_top_leader_payout = comm_formula_multi_lines_each.flat_pay
#                 count = count + 1
#                 if (vision_reward_dos_top_leader_payout > 0) or (count == len(comm_formula_multi_lines)):
#                     if comm_formula_multi_lines_each.pay_rev > 0.00:
#                         region_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
#                         region_top_comp_string += str(" % of Region Revenue")
#                     elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                         region_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
#                     break
#     #############*************** OPS Leaderboard Ranking ******************####################
        ops_leader_obj = self.pool.get('comm.ops.leader.ranking.master')
        vision_reward_ops_top_percent_store = 0.00
        vision_reward_ops_top_store_pay = 0.00
        vision_reward_mm_top_ops_market_rev = 0.00
        vision_reward_mm_top_ops_market_payout = 0.00
        vision_reward_dos_top_ops_rev = 0.00
        vision_reward_dos_top_ops_payout = 0.00
        ops_leader_store_string = str("")
        ops_leader_market_string = str("")
        ops_leader_region_string = str("")
#         comm_sto_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
#         if comm_sto_ops_search_ids:
#             comm_sto_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_sto_ops_search_ids[0])
#             vision_reward_ops_top_percent_store = 0

#             comm_formula_multi_lines = comm_sto_ops_browse_data.formula_multi_lines
#             cr.execute('''select rank from leaderboard_sap where store_id=%s and start_date=%s and end_date=%s''', (store_id,start_date, end_date))
#             store_top_hr_ids = cr.fetchall()
#             count = 0
#             for comm_formula_multi_lines_each in comm_formula_multi_lines:
#                 if comm_formula_multi_lines_each.cal_type == 'count':
#                     from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
#                     to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
#                 elif comm_formula_multi_lines_each.cal_type == 'perc':
#                     from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * store_count) / 100
#                     to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * store_count) / 100
#                 if comm_formula_multi_lines_each.rank_base == 'all':
#                     if store_top_hr_ids:
#                         vision_reward_ops_top_percent_store = store_top_hr_ids[0][0]
#                     if not vision_reward_ops_top_percent_store:
#                         vision_reward_ops_top_percent_store = 0
#                     if (vision_reward_ops_top_percent_store >= from_comm_top_company_count) and (vision_reward_ops_top_percent_store <= to_comm_top_company_count):
#                         if comm_formula_multi_lines_each.pay_rev > 0.00:
#                             vision_reward_ops_top_store_pay = (tot_store_rev * comm_formula_multi_lines_each.pay_rev) / 100
#                         elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                             vision_reward_ops_top_store_pay = comm_formula_multi_lines_each.flat_pay
#                 count = count + 1
#                 if (vision_reward_ops_top_store_pay > 0) or (count == len(comm_formula_multi_lines)):
#                     if comm_formula_multi_lines_each.pay_rev > 0.00:
#                         ops_leader_store_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
#                         ops_leader_store_string += str(" % of RSA Revenue")
#                     elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                         ops_leader_store_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
#                     break
#                 # # #################### Operations Leaderboard: Top 10% of Stores ######################
#                 # vision_reward_ops_top_percent_store_amount = comm_stl_browse_data.comm_stl_amount_store_ops
#                 # vision_reward_stl_store_percent_ops = comm_stl_browse_data.comm_stl_top_store_percent_ops
#                 # comm_stl_top_rank_store_ops = comm_stl_browse_data.comm_stl_top_rank_store_ops
#                 # vision_reward_mall_inline_num_ops = comm_stl_browse_data.comm_stl_mall_inline_loc_ops
#                 # vision_reward_mall_inline_leader_payout_ops = comm_stl_browse_data.comm_stl_mall_inline_loc_pay_ops
#                 # vision_reward_kiosk_num_ops = comm_stl_browse_data.comm_stl_top_kiosk_ops
#                 # vision_reward_mall_kiosk_leader_payout_ops = comm_stl_browse_data.comm_stl_mall_kiosk_loc_pay_ops
#                 # store_top_hr_ops = []
#                 # top_mall_store_ops = []
#                 # top_kiosk_store_ops = []
#                 # vision_reward_ops_top_percent_store_rank = 0
#                 # ops_leader_store_string += str("$ %s"%(vision_reward_ops_top_percent_store_amount))
#                 # if vision_reward_stl_store_percent_ops > 0.00:    
#                 #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s,'store',%s)''', (start_date, end_date,store_count, ))
#                 #     store_top_hr_ids = cr.fetchall()
#                 #     for store_top_hr_id in store_top_hr_ids:
#                 #         store_top_hr_ops.append(store_top_hr_id[0])
#                 #     if vision_reward_stl_store_percent_ops > 0.00:
#                 #         elite_bonus_stl_store_percent_ops = (vision_reward_stl_store_percent_ops * store_count)/100
#                 #     elif comm_stl_top_rank_store_ops > 0.00:
#                 #         elite_bonus_stl_store_percent_ops = comm_stl_top_rank_store_ops
#                 #     if store_id in store_top_hr_ops:
#                 #         vision_reward_ops_top_percent_store_rank = store_top_hr_ops.index(store_id) + 1
#                 #     # ############### Payout based on OR conditions for STL/MID/SM ##################33
#                 #     if (store_id in store_top_hr_ops) and (vision_reward_ops_top_percent_store_rank <= elite_bonus_stl_store_percent_ops):
#                 #         vision_reward_ops_top_store_pay = vision_reward_ops_top_percent_store_amount
#                 #     vision_reward_ops_top_percent_store = vision_reward_ops_top_percent_store_rank
#         comm_mkt_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
#         if comm_mkt_ops_search_ids:
#             comm_mkt_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_mkt_ops_search_ids[0])
#             vision_reward_mm_top_ops_market_rev = 0

#             cr.execute('''select rank from leaderboard_markets where market_id=%s and start_date=%s and end_date=%s''', (market_id,start_date, end_date))
#             top_mm_markets = cr.fetchall()
#             comm_formula_multi_lines = comm_mkt_ops_browse_data.formula_multi_lines
#             count = 0
#             for comm_formula_multi_lines_each in comm_formula_multi_lines:
#                 if comm_formula_multi_lines_each.cal_type == 'count':
#                     from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
#                     to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
#                 elif comm_formula_multi_lines_each.cal_type == 'perc':
#                     from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * market_count) / 100
#                     to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * market_count) / 100
#                 if comm_formula_multi_lines_each.rank_base == 'all':
#                     if top_mm_markets:
#                         vision_reward_mm_top_ops_market_rev = top_mm_markets[0][0]
#                     if not vision_reward_mm_top_ops_market_rev:
#                         vision_reward_mm_top_ops_market_rev = 0
#                     if (vision_reward_mm_top_ops_market_rev >= from_comm_top_company_count) and (vision_reward_mm_top_ops_market_rev <= to_comm_top_company_count):
#                         if comm_formula_multi_lines_each.pay_rev > 0.00:
#                             vision_reward_mm_top_ops_market_payout = (tot_market_rev * comm_formula_multi_lines_each.pay_rev) / 100
#                         elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                             vision_reward_mm_top_ops_market_payout = comm_formula_multi_lines_each.flat_pay
#                 count = count + 1
#                 if (vision_reward_mm_top_ops_market_payout > 0) or (count == len(comm_formula_multi_lines)):
#                     if comm_formula_multi_lines_each.pay_rev > 0.00:
#                         ops_leader_market_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
#                         ops_leader_market_string += str(" % of RSA Revenue")
#                     elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                         ops_leader_market_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
#                     break
#             # # ############## Top 5 Markets Operations Leaderboard ########################
#             # comm_mm_top_market_opr = comm_mm_browse_data.comm_mm_top_market_opr
#             # cr.execute("select count(*) from market_place")
#             # market_ids = cr.fetchall()
#             # market_count = market_ids[0][0]
#             # if len(comm_mm_top_market_opr) > 0:
#             #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s, 'market',%s)''', (start_date, end_date, market_count))
#             #     top_mm_markets = cr.fetchall()
#             #     top_mm_markets_ids_opr = []
#             #     for top_mm_market_id in top_mm_markets:
#             #         top_mm_markets_ids_opr.append(top_mm_market_id[0])
#             #     vision_reward_mm_top_ops_market_rev = top_mm_markets_ids_opr.index(market_id) + 1
#             #     for comm_mm_top_market_data in comm_mm_top_market_opr:
#             #         if comm_mm_top_market_data.comm_seq == vision_reward_mm_top_ops_market_rev:
#             #             vision_reward_mm_top_ops_market_payout = comm_mm_top_market_data.comm_amount
#             #     if vision_reward_mm_top_ops_market_payout > 0.00:
#             #         ops_leader_market_string += str("$ %s"%(vision_reward_mm_top_ops_market_payout))
#             #     else:
#             #         ops_leader_market_string += str("$ %s"%(comm_mm_top_market_opr[0].comm_amount))
#             # ############## Top 5 Markets Operations Leaderboard ########################
#         comm_reg_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
#         if comm_reg_ops_search_ids:
#             comm_reg_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_reg_ops_search_ids[0])
#             vision_reward_dos_top_ops_rev = 0

#             comm_formula_multi_lines = comm_reg_ops_browse_data.formula_multi_lines
#             cr.execute('''select rank from leaderboard_regions where region_id=%s and start_date=%s and end_date=%s''', (region_id,start_date, end_date))
#             top_dos_regions = cr.fetchall()
#             count = 0
#             for comm_formula_multi_lines_each in comm_formula_multi_lines:
#                 if comm_formula_multi_lines_each.cal_type == 'count':
#                     from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
#                     to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
#                 elif comm_formula_multi_lines_each.cal_type == 'perc':
#                     from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * region_count) / 100
#                     to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * region_count) / 100
#                 if comm_formula_multi_lines_each.rank_base == 'all':
#                     if top_dos_regions:
#                         vision_reward_dos_top_ops_rev = top_dos_regions[0][0]
#                     if not vision_reward_dos_top_ops_rev:
#                         vision_reward_dos_top_ops_rev = 0
#                     if (vision_reward_dos_top_ops_rev >= from_comm_top_company_count) and (vision_reward_dos_top_ops_rev <= to_comm_top_company_count):
#                         if comm_formula_multi_lines_each.pay_rev > 0.00:
#                             vision_reward_dos_top_ops_payout = (tot_region_rev * comm_formula_multi_lines_each.pay_rev) / 100
#                         elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                             vision_reward_dos_top_ops_payout = comm_formula_multi_lines_each.flat_pay
#                 count = count + 1
#                 if (vision_reward_dos_top_ops_payout > 0) or (count == len(comm_formula_multi_lines)):
#                     if comm_formula_multi_lines_each.pay_rev > 0.00:
#                         ops_leader_region_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
#                         ops_leader_region_string += str(" % of RSA Revenue")
#                     elif comm_formula_multi_lines_each.flat_pay > 0.00:
#                         ops_leader_region_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
#                     break
#             # # ################## Top Region Operations Leaderboard Ranking #############################
#             # comm_dos_top_region_opr = comm_dos_browse_data.comm_dos_top_region_rank_opr
#             # vision_reward_dos_top_ops_rev = comm_dos_browse_data.comm_dos_amount_rank_opr
#             # if comm_dos_top_region_opr > 0:
#             #     cr.execute('''select id, name, rank from get_opsleaderboard_stats_odoo(%s, %s, 'region',%s)''', (start_date, end_date, region_count))
#             #     top_dos_regions = cr.fetchall()
#             #     top_dos_regions_ids_opr = []
#             #     ops_leader_region_string += str("$ %s"%(vision_reward_dos_top_ops_rev))
#             #     for top_dos_regions_id in top_dos_regions:
#             #         top_dos_regions_ids_opr.append(top_dos_regions_id[0])
#             #     vision_reward_dos_top_ops_rev = top_dos_regions_ids_opr.index(region_id) + 1
#             #     if (region_id in top_dos_regions_ids_opr) and (vision_reward_dos_top_ops_rev <= comm_dos_top_region_opr):
#             #         vision_reward_dos_top_ops_payout = comm_dos_browse_data.comm_dos_amount_rank_opr
        b = datetime.today()
        c = b - a
        print "Vision Reward", c.total_seconds()
        # ################# Profitability Payout ###################################
        comm_obj = self.pool.get('comm.profitability.payout')
        store_income = 0.00
        store_payout = 0.00
        store_actual_profit = 0.00
        profit_store_id = False
        profit_market_id = False
        profit_region_id = False
    ########## ******* 1 month before data fetch for rsm/mid/mm/dos to run for profitability *********** ###        
        profit_date_monthrange = datetime.strptime(profit_start_date, '%Y-%m-%d').date()
        cr.execute("select id from designation_tracker where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date desc",(emp_id,profit_start_date,profit_end_date))
        profit_des_track_search = map(lambda x: x[0], cr.fetchall())
        if not profit_des_track_search:
            profit_des_track_search = des_track_master.search(cr, uid, [('dealer_id', '=', emp_id), ('start_date', '<=', profit_start_date), ('end_date', '>=', profit_end_date)])
        if profit_des_track_search:
            profit_emp_des = des_track_master.browse(cr, uid, profit_des_track_search[0]).designation_id.id
            profit_emp_model_id = des_track_master.browse(cr, uid, profit_des_track_search[0]).designation_id.model_id
        else:
            profit_emp_des = self_obj.emp_des.id
            profit_emp_model_id = self_obj.emp_des.model_id
        if profit_emp_model_id == 'rsm':
            cr.execute('''select sap.id from sap_tracker sap, designation_tracker dt 
                where sap.desig_id = dt.id and sap.store_mgr_id = %s and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
                and dt.covering_str_check = false order by sap.end_date desc''',(emp_id,profit_start_date,profit_end_date))
            profit_store_emp_search = map(lambda x: x[0], cr.fetchall())
            if not profit_store_emp_search:
                profit_store_emp_search = sap_track_obj.search(cr, uid, [('store_mgr_id','=',emp_id),('start_date','<=',profit_start_date),('end_date','>=',profit_end_date)])
            if profit_store_emp_search:
                profit_store_data = sap_track_obj.browse(cr, uid, profit_store_emp_search[0]).sap_id
                profit_store_id = profit_store_data.id
                profit_market_id = profit_store_data.market_id.id
                cr.execute('''select mkt.region_market_id from market_tracker mkt, designation_tracker dt 
                    where mkt.desig_id = dt.id and mkt.market_id = %s and mkt.end_date >= %s and mkt.start_date <= %s 
                    and dt.covering_region_check = false order by mkt.end_date desc''',(profit_market_id,profit_start_date,profit_end_date))
                rsm_reg_search = cr.fetchall()
                if rsm_reg_search:
                    profit_region_id = rsm_reg_search[0][0]
                else:
                    profit_region_id = profit_store_data.market_id.region_market_id.id
        elif profit_emp_model_id == 'mid':
            cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date desc",(emp_id,profit_start_date,profit_end_date))
            profit_dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not profit_dealer_obj_search_multi:
                profit_dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',profit_start_date),('end_date','>=',profit_end_date)])
            if profit_dealer_obj_search_multi:
                profit_store_data = dealer_obj.browse(cr, uid, profit_dealer_obj_search_multi[0]).store_name
                profit_store_id = profit_store_data.id
                cr.execute('''select sap.market_id from sap_tracker sap, designation_tracker dt 
                    where sap.desig_id = dt.id and sap.sap_id = %s and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false 
                    and dt.covering_market_check = false order by sap.end_date desc''',(profit_store_id,profit_start_date,profit_end_date))
                profit_rsm_sap_search = cr.fetchall()
                if profit_rsm_sap_search:
                    profit_market_id = profit_rsm_sap_search[0][0]
                else:
                    profit_market_id = profit_store_data.market_id.id
                cr.execute('''select mkt.region_market_id from market_tracker mkt, designation_tracker dt 
                    where mkt.desig_id = dt.id and mkt.market_id = %s and mkt.end_date >= %s and mkt.start_date <= %s 
                    and dt.covering_region_check = false order by mkt.end_date desc''',(profit_market_id,profit_start_date,profit_end_date))
                profit_rsm_mkt_search = cr.fetchall()
                if profit_rsm_mkt_search:
                    profit_region_id = profit_rsm_mkt_search[0][0]
                else:
                    profit_region_id = profit_store_data.market_id.region_market_id.id                
        elif profit_emp_model_id == 'mm':
            cr.execute('''select mkt.id from market_tracker mkt, designation_tracker dt 
                where mkt.desig_id = dt.id and mkt.market_manager = %s and mkt.end_date >= %s and mkt.start_date <= %s 
                and dt.covering_market_check = false order by mkt.end_date desc''',(emp_id,profit_start_date,profit_end_date))
            profit_market_emp_search = map(lambda x: x[0], cr.fetchall())
            if not profit_market_emp_search:
                profit_market_emp_search = market_track_obj.search(cr, uid, [('market_manager','=',emp_id),('start_date','<=',profit_start_date),('end_date','>=',profit_end_date)])
            if profit_market_emp_search:
                profit_market_data = market_track_obj.browse(cr, uid, profit_market_emp_search[0])
                profit_market_id = profit_market_data.market_id.id
                profit_region_id = profit_market_data.region_market_id.id
        elif profit_emp_model_id == 'dos':
            cr.execute('''select reg.id from region_tracker reg, designation_tracker dt 
                where reg.desig_id = dt.id and reg.sales_director = %s and reg.end_date >= %s and reg.start_date <= %s
                and dt.covering_region_check = false order by reg.end_date desc''',(emp_id,profit_start_date,profit_end_date))
            profit_region_emp_search = map(lambda x: x[0], cr.fetchall())
            if not profit_region_emp_search:
                profit_region_emp_search = region_track_obj.search(cr, uid, [('sales_director','=',emp_id),('start_date','<=',profit_start_date),('end_date','>=',profit_end_date)])
            if profit_region_emp_search:
                profit_region_data = region_track_obj.browse(cr, uid, profit_region_emp_search[0])
                profit_region_id = profit_region_data.region_id.id
        if profit_store_id:
              #************ Store VOC **************************#
            cr.execute('''select ((avg(overall_satisfaction)+avg(knowledge)+avg(professionalism_courtesy)+avg(valued_customer)+avg(timeliness))/5)+avg(combined_plus_1) as voc
from import_voc_file where start_date >= %s and end_date <= %s and store_id = %s''', (profit_start_date, profit_end_date, profit_store_id))
            voc_data = cr.fetchall()
            profit_store_voc = voc_data[0][0]
            if not profit_store_voc:
                profit_store_voc = 0.00
        else:
            profit_store_voc = store_voc
        profit_market_voc = market_voc
        profit_region_voc = region_voc
    #### ******* market and region target profit *********** ##
        market_profit_target = 0.00
        region_profit_target = 0.00
        if profit_market_id:
            cr.execute('''select sum(profit_target) from market_profitability_rph where market_id = %s and start_date=%s ''',(profit_market_id,profit_start_date))
            market_profit_target = cr.fetchall()
            if market_profit_target:
                market_profit_target = market_profit_target[0][0]
            else:
                market_profit_target = 0.00
        if profit_region_id:
            cr.execute('''select sum(profit_target) from (select prof.profit_target from market_profitability_rph prof, market_tracker mkt
                where prof.market_id = mkt.market_id and mkt.end_date >= %s and mkt.start_date <= %s
                and mkt.region_market_id = %s and prof.start_date=%s group by prof.market_id,prof.profit_target) as revenue'''
            ,(profit_start_date,profit_end_date,profit_region_id,profit_start_date))
            region_profit_target = cr.fetchall()
            if region_profit_target:
                region_profit_target = region_profit_target[0][0]
            else:
                region_profit_target = 0.00
        store_profit_target = 0.00

        comm_profit_store_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', profit_emp_des),('spiff_model', '=', model_store_search_id[0]),('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_profit_store_search_ids and profit_store_id:
            field_name = 'store_id'
            profit_vals = self._calculate_profitability_commission(cr, uid, profit_store_voc, field_name, profit_store_id, comm_profit_store_search_ids, profit_start_date, profit_end_date, store_profit_target)
            store_income = profit_vals['store_income']
            store_payout = profit_vals['store_payout']
            store_actual_profit = profit_vals['store_actual_profit']
        comm_profit_market_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', profit_emp_des),('spiff_model', '=', model_market_search_id[0]),('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_profit_market_search_ids and profit_market_id:
            field_name = 'market_id'
            profit_vals = self._calculate_profitability_commission(cr, uid, profit_market_voc, field_name, profit_market_id, comm_profit_market_search_ids, profit_start_date, profit_end_date, market_profit_target)
            store_income = profit_vals['store_income']
            store_payout = profit_vals['store_payout']
            store_actual_profit = profit_vals['store_actual_profit']
        comm_profit_region_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', profit_emp_des),('spiff_model', '=', model_region_search_id[0]),('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_profit_region_search_ids and profit_region_id:
            field_name = 'region_id'
            profit_vals = self._calculate_profitability_commission(cr, uid, profit_region_voc, field_name, profit_region_id, comm_profit_region_search_ids, profit_start_date, profit_end_date, region_profit_target)
            store_income = profit_vals['store_income']
            store_payout = profit_vals['store_payout']
            store_actual_profit = profit_vals['store_actual_profit']
        comm_profit_comp_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', profit_emp_des),('spiff_model', '=', model_comp_search_id[0]),('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_profit_comp_search_ids and profit_region_id:
            field_name = 'company_id'
            profit_vals = self._calculate_profitability_commission(cr, uid, profit_region_voc, field_name, profit_region_id, comm_profit_comp_search_ids, profit_start_date, profit_end_date, region_profit_target)
            store_income = profit_vals['store_income']
            store_payout = profit_vals['store_payout']
            store_actual_profit = profit_vals['store_actual_profit']
        # ################## Market Share Profitability ############################### Need to Review
        wv_dash_obj = self.pool.get('import.wv.branded.dashboard')
        shopper_obj = self.pool.get('import.shopper.track')
        labor_obj = self.pool.get('labour.staffing')
        comm_obj = self.pool.get('comm.market.share.profitability.payout')
        p_and_l_obj = self.pool.get('import.profit.loss')
        tot_market_voc = 0.00
        market_conv_percent = 0.00
        hour_range = 0.00
        market_share_profit = 0.00
        market_store_income = 0.00
        region_conv_percent = 0.00
        comm_store_search = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des),('comm_store_class','=',store_classification_id),('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_store_search:
            shopper_ids = shopper_obj.search(cr, uid, [('sap_id', '=', store_id), ('date_customer_enter', '>=', start_date), ('date_customer_enter', '<=', end_date)])
            labour_ids = labor_obj.search(cr, uid, [('store_id', '=', store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
            tot_market_voc = store_voc
            no_of_exit_market = sto_no_of_exit
            if no_of_exit_market > 0.00:    
                market_conv_percent = (store_actual_box * 100) / no_of_exit_market
            if labour_ids:
                labour_data = labor_obj.browse(cr, uid, labour_ids[0])
                hour_range = int(labour_data.mtd_of_hours)
            import_market_data = market_obj.browse(cr, uid, market_id)
            import_store_ids = import_market_data.store_id
            market_income = 0.00
            for import_store_id in import_store_ids:
                p_and_l_search = p_and_l_obj.search(cr, uid, [('store_id', '=', import_store_id.id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
                if p_and_l_search:
                    market_income = market_income + p_and_l_obj.browse(cr, uid, p_and_l_search[0]).netincome
            comm_store_data = comm_obj.browse(cr, uid, comm_store_search[0])
            comm_voc_percent = comm_store_data.comm_voc
            comm_conv_percent = comm_store_data.comm_percent_conversion
            comm_start_labor = comm_store_data.comm_start_percent_labour
            comm_end_labor = comm_store_data.comm_end_percent_labour
            p_and_l_search = p_and_l_obj.search(cr, uid, [('store_id', '=', store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
            if p_and_l_search:
                market_store_income = p_and_l_obj.browse(cr, uid, p_and_l_search[0]).netincome
            if market_store_income > 0.00 and market_income > 0.00:
                if comm_end_labor > 0.00:
                    if tot_market_voc >= comm_voc_percent and market_conv_percent >= comm_conv_percent and hour_range >= comm_start_labor and hour_range <= comm_end_labor:
                        market_share_percent = comm_store_data.comm_percent_market_profit
                        market_share_profit = (market_income * market_share_percent) / 100
                    else:
                        market_share_profit = 0.00
                else:
                    if tot_market_voc >= comm_voc_percent and market_conv_percent >= comm_conv_percent:
                        market_share_percent = comm_store_data.comm_percent_market_profit
                        market_share_profit = (market_income * market_share_percent) / 100
                    else:
                        market_share_profit = 0.00
              # ###################### Market Calculation #################################
        comm_market_search = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_market_search:
            import_market_data = market_obj.browse(cr, uid, market_id)
            import_store_ids = import_market_data.store_id
            market_sap_goal_ids = []
            shopper_obj_ids = []
            labor_obj_ids = []
            for import_store_id in import_store_ids:
                sap_id = import_store_id.sap_number
                import_store_id = import_store_id.id
                goal_ids = goal_obj.search(cr, uid, [('store_id', '=', import_store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
                labour_ids = labor_obj.search(cr, uid, [('store_id', '=', import_store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
                if goal_ids:
                    market_sap_goal_ids.append(goal_ids[0])
                if labour_ids:
                    labor_obj_ids.append(labour_ids[0])
            tot_market_voc = market_voc
            mm_share_income = 0.00
            region_store_inc = 0.00
            no_of_exit_market = mkt_no_of_exit
            if no_of_exit_market > 0.00:
                market_conv_percent = (all_market_actual_box * 100) / no_of_exit_market
            if labor_obj_ids:
                for labour_obj_id in labor_obj_ids:
                    labour_data = labor_obj.browse(cr, uid, labour_obj_id)
                    hour_range = hour_range + int(labour_data.mtd_of_hours)
                hour_range = hour_range / len(labor_obj_ids)
            cr.execute('''select sum(netincome) from import_profit_loss pl, sap_store sap where pl.store_id = sap.id and sap.market_id = %s''',(market_id,))
            region_store_income = cr.fetchall()
            if region_store_income:
                mm_share_income = region_store_income[0][0]
            else:
                mm_share_income = 0.00
            comm_market_data = comm_obj.browse(cr, uid, comm_market_search[0])
            comm_voc_percent = comm_market_data.comm_voc
            comm_conv_percent = comm_market_data.comm_percent_conversion
            comm_start_labor = comm_market_data.comm_start_percent_labour
            comm_end_labor = comm_market_data.comm_end_percent_labour
            if mm_share_income > 0.00:    
                if comm_end_labor > 0.00:
                    if tot_market_voc >= comm_voc_percent and market_conv_percent >= comm_conv_percent and hour_range >= comm_start_labor and hour_range <= comm_end_labor:
                        market_share_percent = comm_market_data.comm_percent_market_profit
                        market_share_profit = (mm_share_income * market_share_percent) / 100
                    else:
                        market_share_percent = comm_market_data.comm_miss_metrics_percent
                        market_share_profit = (mm_share_income * market_share_percent) / 100
                else:
                    if tot_market_voc >= comm_voc_percent and market_conv_percent >= comm_conv_percent:
                        market_share_percent = comm_market_data.comm_percent_market_profit
                        market_share_profit = (mm_share_income * market_share_percent) / 100
                    else:
                        market_share_percent = comm_market_data.comm_miss_metrics_percent
                        market_share_profit = (mm_share_income * market_share_percent) / 100
        # ###################### Region Calculation ##############################
        comm_region_search = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_region_search:
            import_region_data = region_obj.browse(cr, uid, region_id)
            import_market_ids = import_region_data.market_place_ids
            region_sap_goal_ids = []
            shopper_obj_ids = []
            labor_obj_ids = []
            for import_market_id in import_market_ids:
                import_store_ids = import_market_id.store_id
                for import_store_id in import_store_ids:
                    sap_id = import_store_id.sap_number
                    import_store_id = import_store_id.id
                    goal_ids = goal_obj.search(cr, uid, [('store_id', '=', import_store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
                    labour_ids = labor_obj.search(cr, uid, [('store_id', '=', import_store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
                    if goal_ids:
                        region_sap_goal_ids.append(goal_ids[0])
                    if labour_ids:
                        labor_obj_ids.append(labour_ids[0])
            tot_market_voc = region_voc
            dos_share_income = 0.00
            company_store_inc = 0.00
            no_of_exit_region = reg_no_of_exit
            if no_of_exit_region > 0.00:
                region_conv_percent = (all_region_actual_box * 100) / no_of_exit_region
            market_conv_percent = region_conv_percent
            if labor_obj_ids:
                for labour_obj_id in labor_obj_ids:
                    labour_data = labor_obj.browse(cr, uid, labour_obj_id)
                    hour_range = hour_range + labour_data.mtd_of_hours
                hour_range = hour_range / len(labor_obj_ids)
            cr.execute('''select sum(netincome) as market_income
,reg.id
from import_profit_loss as test inner join sap_store sap on (test.store_id = sap.id)
                                inner join market_place mkt on (sap.market_id = mkt.id)
                                inner join market_regions reg on (mkt.region_market_id = reg.id)
                                where test.start_date between %s and %s
group by reg.id''', (start_date, end_date))
            company_store_income = cr.fetchall()
            if company_store_income:
                for company_store_income_id in company_store_income:
                    company_store_inc = company_store_inc + company_store_income_id[0]
                dos_share_income = company_store_inc / len(company_store_income)
            comm_market_data = comm_obj.browse(cr, uid, comm_region_search[0])
            comm_voc_percent = comm_market_data.comm_voc
            comm_conv_percent = comm_market_data.comm_percent_conversion
            comm_start_labor = comm_market_data.comm_start_percent_labour
            comm_end_labor = comm_market_data.comm_end_percent_labour
            if dos_share_income > 0.00:    
                if comm_end_labor > 0.00:    
                    if tot_market_voc >= comm_voc_percent and market_conv_percent >= comm_conv_percent and hour_range >= comm_start_labor and hour_range <= comm_end_labor:
                        market_share_percent = comm_market_data.comm_percent_market_profit
                        market_share_profit = (dos_share_income * market_share_percent) / 100
                    else:
                        market_share_percent = comm_market_data.comm_miss_metrics_percent
                        market_share_profit = (dos_share_income * market_share_percent) / 100
                else:
                    if tot_market_voc >= comm_voc_percent and market_conv_percent >= comm_conv_percent:
                        market_share_percent = comm_market_data.comm_percent_market_profit
                        market_share_profit = (dos_share_income * market_share_percent) / 100
                    else:
                        market_share_percent = comm_market_data.comm_miss_metrics_percent
                        market_share_profit = (dos_share_income * market_share_percent) / 100
        a = datetime.today()
        c = a - b
        print "Profit, Market Profit", c.total_seconds()

        # ################ Turnover Formula #####################   
        turnover_comm_obj = self.pool.get('comm.turnover.formula')
        turnover_actual_count = 0.00
        turnover_payout = 0.00

        comm_turnover_emp_ids = turnover_comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_turnover_emp_ids:
            # ********** default passing 0 as turnover at employee level as there is no calculation at emp level #
            turnover_actual_count = 0
            turnover_vals = self._calculate_turnover(cr,uid,tot_rev,turnover_actual_count,comm_turnover_emp_ids)
            turnover_payout = turnover_vals['turnover_payout']

        comm_turnover_store_ids = turnover_comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_turnover_store_ids:
             # ********** default passing 0 as turnover at store level as there is no calculation at store level #
            turnover_actual_count = 0
            turnover_vals = self._calculate_turnover(cr,uid,tot_rev,turnover_actual_count,comm_turnover_store_ids)
            turnover_payout = turnover_vals['turnover_payout']
        
        comm_turnover_market_ids = turnover_comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_turnover_market_ids:
             # ********** default passing 0 as turnover at market level as there is no calculation at market level #
            turnover_actual_count = 0
            turnover_vals = self._calculate_turnover(cr,uid,tot_rev,turnover_actual_count,comm_turnover_market_ids)
            turnover_payout = turnover_vals['turnover_payout']

        comm_turnover_region_ids = turnover_comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_turnover_region_ids:
            cr.execute("select turnover_perc from region_turnover_data where region_id = %s and start_date = %s",(region_id,start_date))
            turnover_data = cr.fetchall()
            if turnover_data:
                turnover_actual_count = turnover_data[0][0]
            if not turnover_actual_count:
                turnover_actual_count = 0
            turnover_vals = self._calculate_turnover(cr,uid,tot_rev,turnover_actual_count,comm_turnover_region_ids)
            turnover_payout = turnover_vals['turnover_payout']

        # ################ Revenue Goal Attainment #####################   Need TO Verify
        rev_goal_att_comm_obj = self.pool.get('comm.revenue.goal.attainment.formula')
        rev_goal_att_goals = 0.00
        rev_goal_att_actual = 0.00
        rev_goal_att_percent = 0.00
        rev_goal_att_payout = 0.00

        comm_rev_att_emp_ids = rev_goal_att_comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_rev_att_emp_ids:
            field_name = 'employee_id'
            if hire_date_min.strftime('%Y-%m-%d') > hire_date:
                rev_att_vals = self._calculate_rev_goal_att(cr,uid,field_name,emp_id,comm_rev_att_emp_ids,emp_rev_goal,tot_rev,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            else:
                rev_goal_start_date = (datetime.strptime(hire_date,'%Y-%m-%d') + relativedelta(months=1))
                rev_goal_start_date = rev_goal_start_date.strftime('%Y-%m-%d')
                rev_goal_end_date = end_date
                rev_att_vals = self._calculate_rev_goal_att(cr,uid,field_name,emp_id,comm_rev_att_emp_ids,emp_rev_goal,tot_rev,rev_goal_start_date,rev_goal_end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            rev_goal_att_goals = rev_att_vals['rev_goal_att_goals']
            rev_goal_att_actual = rev_att_vals['rev_goal_att_actual']
            rev_goal_att_percent = rev_att_vals['rev_goal_att_percent']
            rev_goal_att_payout = rev_att_vals['rev_goal_att_payout']

        comm_rev_att_store_ids = rev_goal_att_comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_rev_att_store_ids:
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                store_goal_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    goal_ids_multi = goal_obj.search(cr, uid, [('store_id','=',store_multi_id),('start_date','<=',start_date),('end_date','>=',end_date)])
                    if goal_ids_multi:
                        goal_data_multi = goal_obj.browse(cr, uid, goal_ids_multi[0])
                        store_goal_multi = goal_data_multi.revenue
                    rev_att_vals = self._calculate_rev_goal_att(cr,uid,field_name,store_multi_id,comm_rev_att_store_ids,store_goal_multi,tot_store_rev,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    rev_goal_att_goals = rev_att_vals['rev_goal_att_goals']
                    rev_goal_att_actual = rev_att_vals['rev_goal_att_actual']
                    rev_goal_att_percent = rev_att_vals['rev_goal_att_percent']
                    rev_goal_att_payout_pre = rev_att_vals['rev_goal_att_payout']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        rev_goal_att_payout = rev_goal_att_payout_pre
                    else:
                        rev_goal_att_payout = rev_goal_att_payout + (rev_goal_att_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                    count_multi = count_multi + 1
        
        comm_rev_att_market_ids = rev_goal_att_comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_rev_att_market_ids:
            market_rev_att_percent = 0.00
            field_name = 'market_id'
            rev_att_vals = self._calculate_rev_goal_att(cr,uid,field_name,market_id,comm_rev_att_market_ids,tot_market_revenue_goal,tot_market_rev,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            rev_goal_att_goals = rev_att_vals['rev_goal_att_goals']
            rev_goal_att_actual = rev_att_vals['rev_goal_att_actual']
            rev_goal_att_percent = rev_att_vals['rev_goal_att_percent']
            rev_goal_att_payout = rev_att_vals['rev_goal_att_payout']

        comm_rev_att_region_ids = rev_goal_att_comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_rev_att_region_ids:
            region_rev_att_percent = 0.00
            field_name = 'region_id'
            rev_att_vals = self._calculate_rev_goal_att(cr,uid,field_name,region_id,comm_rev_att_region_ids,tot_region_revenue_goal,tot_region_rev,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            rev_goal_att_goals = rev_att_vals['rev_goal_att_goals']
            rev_goal_att_actual = rev_att_vals['rev_goal_att_actual']
            rev_goal_att_percent = rev_att_vals['rev_goal_att_percent']
            rev_goal_att_payout = rev_att_vals['rev_goal_att_payout']

        # ##################### Total Box PSA Goal attainment (Per Store Average) #######################
        tot_box_att_obj = self.pool.get('comm.top.box.psa.goal.attainment.formula')
        comm_market_tot_box_search_ids = tot_box_att_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        tot_box_psa_payout = 0.00
        box_goal_att_market = 0.00
        tot_box_psa_actual = 0.00
        tot_box_psa_goals = 0.00
        if comm_market_tot_box_search_ids:
            comm_obj_data = tot_box_att_obj.browse(cr, uid, comm_market_tot_box_search_ids[0])
            comm_box_fixed_amount_above_100 = comm_obj_data.comm_fixed_amount_above_100
            comm_box_fixed_amount_100 = comm_obj_data.comm_fixed_amount_above_100
            comm_box_fixed_amount_on_goal = comm_obj_data.comm_fixed_amount_on_goal
            cr.execute('''select count(test.id) as count_box
from (select id,product_id,dsr_trans_type,false as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,employee_id,store_id,market_id,region_id,dsr_act_date,state
    from wireless_dsr_postpaid_line
    union all
    select id,product_id,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,employee_id,store_id,market_id,region_id,dsr_act_date,state
    from wireless_dsr_prepaid_line 
    union all
    select id,product_id,dsr_trans_type,false,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,employee_id,store_id,market_id,region_id,dsr_act_date,state
    from wireless_dsr_upgrade_line) as test
where test.market_id = %s
and test.dsr_act_date between %s and %s
and test.state = 'done'
and test.prm_dsr_smd = false
and test.created_feature = false
'''+condition_box_string+'''
group by test.store_id''', (market_id, start_date, end_date))
            actual_psa_boxes = cr.fetchall()
            for actual_psa_boxes_id in actual_psa_boxes:
                tot_box_psa_actual = tot_box_psa_actual + actual_psa_boxes_id[0]
            if len(actual_psa_boxes) > 0.00:
                tot_box_psa_actual = tot_box_psa_actual / len(actual_psa_boxes)
            cr.execute('''select avg(sg.tot_box)
from import_goals sg,sap_store sp
where sg.store_id = sp.id and sp.market_id = %s
and start_date >= %s and end_date <= %s''',(market_id,start_date,end_date))
            tot_box_psa_goal_ids = cr.fetchall()
            tot_box_psa_goals = tot_box_psa_goal_ids[0][0]
            if tot_box_psa_goals > 0.00:
                box_goal_att_market = (tot_box_psa_actual * 100) / tot_box_psa_goals
            if box_goal_att_market > 100:
                tot_box_psa_payout = (comm_box_fixed_amount_above_100 * box_goal_att_market) / 100
            elif box_goal_att_market == 100:
                tot_box_psa_payout = comm_box_fixed_amount_100
            elif comm_box_fixed_amount_on_goal:
                for comm_fixed_amount_on_goal_id in comm_box_fixed_amount_on_goal:
                    comm_min_percent = comm_fixed_amount_on_goal_id.comm_min_percent
                    comm_max_percent = comm_fixed_amount_on_goal_id.comm_max_percent
                    comm_fixed_amount = comm_fixed_amount_on_goal_id.comm_fixed_amount
                    if box_goal_att_market <= comm_max_percent and box_goal_att_market >= comm_min_percent:
                        tot_box_psa_payout = comm_fixed_amount
        comm_region_tot_box_search_ids = tot_box_att_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if comm_region_tot_box_search_ids:
            comm_obj_data = tot_box_att_obj.browse(cr, uid, comm_region_tot_box_search_ids[0])
            comm_box_fixed_amount_above_100 = comm_obj_data.comm_fixed_amount_above_100
            comm_box_fixed_amount_100 = comm_obj_data.comm_fixed_amount_above_100
            comm_box_fixed_amount_on_goal = comm_obj_data.comm_fixed_amount_on_goal
            cr.execute('''select count(test.id) as count_box
from (select id,product_id,dsr_trans_type,false as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,employee_id,store_id,market_id,region_id,dsr_act_date,state
    from wireless_dsr_postpaid_line
    union all
    select id,product_id,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,employee_id,store_id,market_id,region_id,dsr_act_date,state
    from wireless_dsr_prepaid_line 
    union all
    select id,product_id,dsr_trans_type,false,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,employee_id,store_id,market_id,region_id,dsr_act_date,state
    from wireless_dsr_upgrade_line) as test
where test.region_id = %s
and test.dsr_act_date between %s and %s
and test.state = 'done'
and test.created_feature = false
and test.prm_dsr_smd = false
'''+condition_box_string+'''
group by test.store_id''', (region_id, start_date, end_date))
            actual_psa_boxes = cr.fetchall()
            for actual_psa_boxes_id in actual_psa_boxes:
                tot_box_psa_actual = tot_box_psa_actual + actual_psa_boxes_id[0]
            if len(actual_psa_boxes) > 0.00:
                tot_box_psa_actual = tot_box_psa_actual / len(actual_psa_boxes)
            cr.execute('''select avg(sg.tot_box)
from import_goals sg,sap_store sp,market_place mkt
where sg.store_id = sp.id and sp.market_id = mkt.id and mkt.region_market_id = %s
and start_date <= %s and end_date >= %s''',(region_id,start_date,end_date))
            tot_box_psa_goal_ids = cr.fetchall()
            tot_box_psa_goals = tot_box_psa_goal_ids[0][0]
            if tot_box_psa_goals > 0.00:
                box_goal_att_market = (tot_box_psa_actual * 100) / tot_box_psa_goals
            if box_goal_att_market > 100:
                tot_box_psa_payout = (comm_box_fixed_amount_above_100 * box_goal_att_market) / 100
            elif box_goal_att_market == 100:
                tot_box_psa_payout = comm_box_fixed_amount_100
            elif comm_box_fixed_amount_on_goal:
                for comm_fixed_amount_on_goal_id in comm_box_fixed_amount_on_goal:
                    comm_min_percent = comm_fixed_amount_on_goal_id.comm_min_percent
                    comm_max_percent = comm_fixed_amount_on_goal_id.comm_max_percent
                    comm_fixed_amount = comm_fixed_amount_on_goal_id.comm_fixed_amount
                    if box_goal_att_market <= comm_max_percent and box_goal_att_market >= comm_min_percent:
                        tot_box_psa_payout = comm_fixed_amount    
        b = datetime.today()
        c = b - a
        print "Rev Goal, PSA", c.total_seconds()
        # ################# Spiff Calculation #########################################
        # ####################### SA Special ####################################        
        # #################### Mobile Internet 1GB Spiff ###############################
        spiff_sa_mi_obj = self.pool.get('spiff.mobile.internet')
        tac_obj = self.pool.get('tac.code.master')
        ir_field_obj = self.pool.get('ir.model.fields')
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'mi_1gb_payout'), ('model_id', '=', comm_model_id[0])])
        spiff_master_sa_mi_1gb_percent = 0.00
        spiff_sa_mi_1gb_percent = 0.00
        spiff_sa_mi_1gb_payout = 0.00
        count_sa_mi_1gb_att = 0
        count_all_elig_pos_pre = 0
        mi_1gb_string = str("")
        if ir_field_ids:
            spiff_sa_mi_1gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_1gb_ids:
                field_name = 'employee_id'
                mi_1gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_1gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_1gb_att = mi_1gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_1gb_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_1gb_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_1gb_percent = mi_1gb_vals['spiff_mi_conv_percent']
                mi_1gb_string = mi_1gb_vals['mi_1gb_string']
                print "mi_1gb_vals", mi_1gb_vals
            spiff_store_mi_1gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_store_mi_1gb_ids:
                field_name = 'store_id'
                mi_1gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_1gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_1gb_att = mi_1gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_1gb_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_1gb_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_1gb_percent = mi_1gb_vals['spiff_mi_conv_percent']
                mi_1gb_string = mi_1gb_vals['mi_1gb_string']
            spiff_market_mi_1gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_market_mi_1gb_ids:
                field_name = 'market_id'
                mi_1gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_1gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_1gb_att = mi_1gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_1gb_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_1gb_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_1gb_percent = mi_1gb_vals['spiff_mi_conv_percent']
                mi_1gb_string = mi_1gb_vals['mi_1gb_string']
            spiff_region_mi_1gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_region_mi_1gb_ids:
                field_name = 'region_id'
                mi_1gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_1gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_1gb_att = mi_1gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_1gb_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_1gb_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_1gb_percent = mi_1gb_vals['spiff_mi_conv_percent']
                mi_1gb_string = mi_1gb_vals['mi_1gb_string']
        # #################### Mobile Internet 3GB Spiff ###############################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'mi_3gb_payout'), ('model_id', '=', comm_model_id[0])])
        spiff_master_sa_mi_3gb_percent = 0.00
        spiff_sa_mi_3gb_percent = 0.00
        spiff_sa_mi_3gb_payout = 0.00
        count_sa_mi_3gb_att = 0
        count_all_elig_pos_pre = 0
        mi_3gb_string = str("")
        if ir_field_ids:
            spiff_sa_mi_3gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_3gb_ids:
                field_name = 'employee_id'
                mi_3gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_3gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_3gb_att = mi_3gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_3gb_payout = mi_3gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_3gb_percent = mi_3gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_3gb_percent = mi_3gb_vals['spiff_mi_conv_percent']
                mi_3gb_string = mi_3gb_vals['mi_1gb_string']
            spiff_store_mi_3gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_store_mi_3gb_ids:
                field_name = 'store_id'
                mi_3gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_3gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_3gb_att = mi_3gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_3gb_payout = mi_3gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_3gb_percent = mi_3gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_3gb_percent = mi_3gb_vals['spiff_mi_conv_percent']
                mi_3gb_string = mi_3gb_vals['mi_1gb_string']
            spiff_market_mi_3gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_market_mi_3gb_ids:
                field_name = 'market_id'
                mi_3gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_3gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_3gb_att = mi_3gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_3gb_payout = mi_3gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_3gb_percent = mi_3gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_3gb_percent = mi_3gb_vals['spiff_mi_conv_percent']
                mi_3gb_string = mi_3gb_vals['mi_1gb_string']
            spiff_region_mi_3gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_region_mi_3gb_ids:
                field_name = 'region_id'
                mi_3gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_3gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_3gb_att = mi_3gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_3gb_payout = mi_3gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_3gb_percent = mi_3gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_3gb_percent = mi_3gb_vals['spiff_mi_conv_percent']
                mi_3gb_string = mi_3gb_vals['mi_1gb_string']
        # #################### Mobile Internet 5GB Spiff ###############################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'mi_5gb_payout'), ('model_id', '=', comm_model_id[0])])
        spiff_master_sa_mi_5gb_percent = 0.00
        spiff_sa_mi_5gb_percent = 0.00
        spiff_sa_mi_5gb_payout = 0.00
        count_sa_mi_5gb_att = 0
        count_all_elig_pos_pre = 0
        mi_5gb_string = str("")
        if ir_field_ids:
            spiff_sa_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_5gb_ids:
                field_name = 'employee_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_5gb_att = mi_5gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_5gb_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_5gb_percent = mi_5gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_5gb_percent = mi_5gb_vals['spiff_mi_conv_percent']
                mi_5gb_string = mi_5gb_vals['mi_1gb_string']
            spiff_store_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_store_mi_5gb_ids:
                field_name = 'store_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_5gb_att = mi_5gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_5gb_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_5gb_percent = mi_5gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_5gb_percent = mi_5gb_vals['spiff_mi_conv_percent']
                mi_5gb_string = mi_5gb_vals['mi_1gb_string']
            spiff_market_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_market_mi_5gb_ids:
                field_name = 'market_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_5gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_5gb_att = mi_5gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_5gb_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_5gb_percent = mi_5gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_5gb_percent = mi_5gb_vals['spiff_mi_conv_percent']
                mi_5gb_string = mi_5gb_vals['mi_1gb_string']
            spiff_region_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_region_mi_5gb_ids:
                field_name = 'region_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_5gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                count_sa_mi_5gb_att = mi_5gb_vals['spiff_mi_gb_count']
                spiff_sa_mi_5gb_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_sa_mi_5gb_percent = mi_5gb_vals['spiff_master_mi_conv_percent']
                spiff_sa_mi_5gb_percent = mi_5gb_vals['spiff_mi_conv_percent']
                mi_5gb_string = mi_5gb_vals['mi_1gb_string']
        # #################### Mobile Internet with base field 1 ###############################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field4_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field4_goals = 0.00
        demo_field4_percent = 0.00
        demo_field4_payout = 0.00
        demo_field4_count = 0.00
        if ir_field_ids:
            spiff_sa_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_5gb_ids:
                field_name = 'employee_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field4_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field4_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field4_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field4_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_store_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_store_mi_5gb_ids:
                field_name = 'store_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field4_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field4_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field4_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field4_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_market_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_market_mi_5gb_ids:
                field_name = 'market_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_5gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field4_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field4_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field4_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field4_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_region_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_region_mi_5gb_ids:
                field_name = 'region_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_5gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field4_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field4_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field4_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field4_percent = mi_5gb_vals['spiff_mi_conv_percent']
        # #################### Mobile Internet with base field 2 ###############################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field5_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field5_goals = 0.00
        demo_field5_percent = 0.00
        demo_field5_payout = 0.00
        demo_field5_count = 0.00
        if ir_field_ids:
            spiff_sa_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_5gb_ids:
                field_name = 'employee_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field5_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field5_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field5_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field5_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_store_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_store_mi_5gb_ids:
                field_name = 'store_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field5_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field5_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field5_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field5_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_market_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_market_mi_5gb_ids:
                field_name = 'market_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_5gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field5_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field5_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field5_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field5_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_region_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_region_mi_5gb_ids:
                field_name = 'region_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_5gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field5_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field5_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field5_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field5_percent = mi_5gb_vals['spiff_mi_conv_percent']
        # #################### Mobile Internet with base field 3 ###############################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field6_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field6_goals = 0.00
        demo_field6_percent = 0.00
        demo_field6_payout = 0.00
        demo_field6_count = 0.00
        if ir_field_ids:
            spiff_sa_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_5gb_ids:
                field_name = 'employee_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field6_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field6_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field6goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field6_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_store_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_store_mi_5gb_ids:
                field_name = 'store_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field6_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field6_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field6_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field6_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_market_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_market_mi_5gb_ids:
                field_name = 'market_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_5gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field6_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field6_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field6_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field6_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_region_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_region_mi_5gb_ids:
                field_name = 'region_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_5gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field6_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field6_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field6_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field6_percent = mi_5gb_vals['spiff_mi_conv_percent']
        # #################### Mobile Internet with base field 4 ###############################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field7_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field7_goals = 0.00
        demo_field7_percent = 0.00
        demo_field7_payout = 0.00
        demo_field7_count = 0.00
        if ir_field_ids:
            spiff_sa_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_5gb_ids:
                field_name = 'employee_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field7_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field7_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field7_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field7_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_store_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_store_mi_5gb_ids:
                field_name = 'store_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field7_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field7_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field7_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field7_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_market_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_market_mi_5gb_ids:
                field_name = 'market_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_5gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field7_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field7_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field7_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field7_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_region_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_region_mi_5gb_ids:
                field_name = 'region_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_5gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field7_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field7_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field7_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field7_percent = mi_5gb_vals['spiff_mi_conv_percent']
        # #################### Mobile Internet with base field 5 ###############################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field8_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field8_goals = 0.00
        demo_field8_percent = 0.00
        demo_field8_payout = 0.00
        demo_field8_count = 0.00
        if ir_field_ids:
            spiff_sa_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_5gb_ids:
                field_name = 'employee_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field8_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field8_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field8_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field8_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_store_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_store_mi_5gb_ids:
                field_name = 'store_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_5gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field8_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field8_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field8_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field8_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_market_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_market_mi_5gb_ids:
                field_name = 'market_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_5gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field8_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field8_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field8_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field8_percent = mi_5gb_vals['spiff_mi_conv_percent']
            spiff_region_mi_5gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_region_mi_5gb_ids:
                field_name = 'region_id'
                mi_5gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_5gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field8_count = mi_5gb_vals['spiff_mi_gb_count']
                demo_field8_payout = mi_5gb_vals['spiff_sa_mi_3gb_amount']
                demo_field8_goals = mi_5gb_vals['spiff_master_mi_conv_percent']
                demo_field8_percent = mi_5gb_vals['spiff_mi_conv_percent']
        a = datetime.today()
        c = a - b
        print "MI 1gb,3gb,5gb+", c.total_seconds()
        # ############### 3GB+ Unlimited Attachment Spiff #########################
        spiff_feature_master = self.pool.get('spiff.feature.attachment')
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', '3gb_data_unl_att_payout'), ('model_id', '=', comm_model_id[0])])
        spiff_master_3gb_unl_percent = 0.00
        spiff_3gb_unl_percent = 0.00
        spiff_3gb_unl_payout = 0.00
        spiff_3gb_unl_string = str("")
        count_unl_att = 0
        count_all_pos = 0
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_master_3gb_unl_percent = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            spiff_3gb_unl_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            spiff_3gb_unl_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            count_unl_att = emp_spiff_feature_data['count_3gb_smart_att']
            spiff_3gb_unl_string = emp_spiff_feature_data['paid_comm_string']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    spiff_master_3gb_unl_percent = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                    spiff_3gb_unl_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                    spiff_3gb_unl_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                    count_unl_att = emp_spiff_feature_data['count_3gb_smart_att']
                    spiff_3gb_unl_string = emp_spiff_feature_data['paid_comm_string']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        spiff_3gb_unl_payout = spiff_3gb_unl_payout_pre
                    else:
                        spiff_3gb_unl_payout = spiff_3gb_unl_payout + (spiff_3gb_unl_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                    count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_master_3gb_unl_percent = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            spiff_3gb_unl_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            spiff_3gb_unl_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            count_unl_att = emp_spiff_feature_data['count_3gb_smart_att']
            spiff_3gb_unl_string = emp_spiff_feature_data['paid_comm_string']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_master_3gb_unl_percent = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            spiff_3gb_unl_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            spiff_3gb_unl_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            count_unl_att = emp_spiff_feature_data['count_3gb_smart_att']
            spiff_3gb_unl_string = emp_spiff_feature_data['paid_comm_string']
        b = datetime.today()
        c = b - a
        print "Unlimited", c.total_seconds()
        # #################### Total Box Conversion ######################################## Complete
        spiff_tot_box_rule = self.pool.get('spiff.store.total.box.conversion')        
        spiff_stl_tot_box_conv_percent = 0.00
        spiff_stl_tot_box_rule_percent = 0.00
        spiff_stl_tot_box_rule_amount = 0.00
        spiff_stl_box_count = 0.00
        tot_box_payout_tier = str("")
        rsa_tbc_string = str("")
        spiff_sa_tot_box_rule_search = spiff_tot_box_rule.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])       
        spiff_stl_tot_box_rule_search = spiff_tot_box_rule.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        spiff_mm_tot_box_rule_search = spiff_tot_box_rule.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        spiff_dos_tot_box_rule_search = spiff_tot_box_rule.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_sa_tot_box_rule_search:
            # spiff_sa_tot_box_rule_search_class = spiff_tot_box_rule.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_store_class', '=', store_classification_id), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            ##### below code written to calculate tbc conversion and Payout at company level for TBC
            ##### for designation RSA
            logger.error("exit traffic for Company is %s",spiff_sa_tot_box_rule_search)
            field_name = 'employee_id'
            if company_ids_search and spiff_sa_tot_box_rule_search:
                tbc_vals = self._calculate_tbc_commission_company(cr, uid, spiff_sa_tot_box_rule_search, all_company_actual_box, com_exit_traffic, field_name, start_date, end_date, emp_id, business_box_rule_ids, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_stl_tot_box_conv_percent = tbc_vals['spiff_stl_tot_box_conv_percent']
                spiff_stl_tot_box_rule_percent = tbc_vals['spiff_stl_tot_box_rule_percent']
                spiff_stl_tot_box_rule_amount = tbc_vals['spiff_stl_tot_box_rule_amount']
                spiff_stl_box_count = tbc_vals['spiff_stl_box_count']
                tot_box_payout_tier = tbc_vals['tot_box_payout_tier']
                rsa_tbc_string = tbc_vals['rsa_tbc_string']
                logger.error("rsa tbc string for Company is %s",tbc_vals)

            # ##### code ends here and the below condition is converted in to elif instead of "if"
            # elif spiff_sa_tot_box_rule_search_class:
            #     tbc_vals = self._calculate_tbc_commission(cr, uid, spiff_sa_tot_box_rule_search_class, store_actual_box, sto_no_of_exit, field_name, start_date, end_date, emp_id, business_box_rule_ids, tot_rev, emp_model_id)
            #     spiff_stl_tot_box_conv_percent = tbc_vals['spiff_stl_tot_box_conv_percent']
            #     spiff_stl_tot_box_rule_percent = tbc_vals['spiff_stl_tot_box_rule_percent']
            #     spiff_stl_tot_box_rule_amount = tbc_vals['spiff_stl_tot_box_rule_amount']
            #     spiff_stl_box_count = tbc_vals['spiff_stl_box_count']
            #     tot_box_payout_tier = tbc_vals['tot_box_payout_tier']
            #     rsa_tbc_string = tbc_vals['rsa_tbc_string']
            else:
                tbc_vals = self._calculate_tbc_commission(cr, uid, spiff_sa_tot_box_rule_search, store_actual_box, sto_no_of_exit, field_name, start_date, end_date, emp_id, business_box_rule_ids, tot_rev, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_stl_tot_box_conv_percent = tbc_vals['spiff_stl_tot_box_conv_percent']
                spiff_stl_tot_box_rule_percent = tbc_vals['spiff_stl_tot_box_rule_percent']
                spiff_stl_tot_box_rule_amount = tbc_vals['spiff_stl_tot_box_rule_amount']
                spiff_stl_box_count = tbc_vals['spiff_stl_box_count']
                tot_box_payout_tier = tbc_vals['tot_box_payout_tier']
                rsa_tbc_string = tbc_vals['rsa_tbc_string']
        elif spiff_stl_tot_box_rule_search:
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    spiff_stl_no_of_exit_multi = 0.00
                    date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                    days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                    dealer_obj_data = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    multi_store_id = dealer_obj_data.store_name.id
                    traffic_red_multi = dealer_obj_data.store_name.store_classification.traffic_reduction
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    tbc_box_actual = self._calculate_store_rev_dsr(cr, uid, multi_store_id, start_date, end_date, condition_box_string, from_box_condition, prm_job_id, business_box_rule_ids, business_rev_rule_ids,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)['actual_store_box']
                    # spiff_stl_tot_box_rule_search_class = spiff_tot_box_rule.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_store_class', '=', store_classification_id), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
                    
                    ##### below code written to calculate tbc conversion and Payout at company level for TBC
                    ##### for designation STL
                    if company_ids_search and spiff_stl_tot_box_rule_search:
                        field_name = 'store_id'
                        tbc_vals = self._calculate_tbc_commission_company(cr, uid, spiff_stl_tot_box_rule_search, all_company_actual_box, com_exit_traffic, field_name, start_date, end_date, multi_store_id, business_box_rule_ids, tot_store_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                        spiff_stl_tot_box_conv_percent = tbc_vals['spiff_stl_tot_box_conv_percent']
                        spiff_stl_tot_box_rule_percent = tbc_vals['spiff_stl_tot_box_rule_percent']
                        spiff_stl_tot_box_rule_amount_pre = tbc_vals['spiff_stl_tot_box_rule_amount']
                        spiff_stl_box_count = tbc_vals['spiff_stl_box_count']
                        tot_box_payout_tier = tbc_vals['tot_box_payout_tier']
                        rsa_tbc_string = tbc_vals['rsa_tbc_string']
                        logger.error(" kiosk tbc string is %s",tbc_vals)

                    ##### code ends here and the below condition is converted in to elif instead of "if"

                    # elif spiff_stl_tot_box_rule_search_class:
                    #     field_name = 'store_id'
                    #     tbc_vals = self._calculate_tbc_commission(cr, uid, spiff_stl_tot_box_rule_search_class, tbc_box_actual, sto_no_of_exit, field_name, start_date, end_date, multi_store_id, business_box_rule_ids, tot_store_rev, emp_model_id)
                    #     spiff_stl_tot_box_conv_percent = tbc_vals['spiff_stl_tot_box_conv_percent']
                    #     spiff_stl_tot_box_rule_percent = tbc_vals['spiff_stl_tot_box_rule_percent']
                    #     spiff_stl_tot_box_rule_amount_pre = tbc_vals['spiff_stl_tot_box_rule_amount']
                    #     spiff_stl_box_count = tbc_vals['spiff_stl_box_count']  
                    #     tot_box_payout_tier = tbc_vals['tot_box_payout_tier']
                    #     rsa_tbc_string = tbc_vals['rsa_tbc_string']
                    else:
                        field_name = 'store_id'
                        tbc_vals = self._calculate_tbc_commission(cr, uid, spiff_stl_tot_box_rule_search, tbc_box_actual, sto_no_of_exit, field_name, start_date, end_date, multi_store_id, business_box_rule_ids, tot_store_rev, emp_model_id, [], store_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                        spiff_stl_tot_box_conv_percent = tbc_vals['spiff_stl_tot_box_conv_percent']
                        spiff_stl_tot_box_rule_percent = tbc_vals['spiff_stl_tot_box_rule_percent']
                        spiff_stl_tot_box_rule_amount_pre = tbc_vals['spiff_stl_tot_box_rule_amount']
                        spiff_stl_box_count = tbc_vals['spiff_stl_box_count']
                        tot_box_payout_tier = tbc_vals['tot_box_payout_tier']
                        rsa_tbc_string = tbc_vals['rsa_tbc_string']
                    if dealer_obj_data.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        spiff_stl_tot_box_rule_amount = spiff_stl_tot_box_rule_amount_pre
                    else:
                        spiff_stl_tot_box_rule_amount = spiff_stl_tot_box_rule_amount + (spiff_stl_tot_box_rule_amount_pre * float(delta_date.days + 1) / float(days_in_month))
                    count_multi = count_multi + 1
        elif spiff_mm_tot_box_rule_search:
            field_name = 'market_id'
            tbc_vals = self._calculate_tbc_commission(cr, uid, spiff_mm_tot_box_rule_search, all_market_actual_box, mkt_no_of_exit, field_name, start_date, end_date, market_id, business_box_rule_ids, tot_rev, emp_model_id, market_traffic_stores, market_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_stl_tot_box_conv_percent = tbc_vals['spiff_stl_tot_box_conv_percent']
            spiff_stl_tot_box_rule_percent = tbc_vals['spiff_stl_tot_box_rule_percent']
            spiff_stl_tot_box_rule_amount = tbc_vals['spiff_stl_tot_box_rule_amount']
            spiff_stl_box_count = tbc_vals['spiff_stl_box_count']
            tot_box_payout_tier = tbc_vals['tot_box_payout_tier']
            rsa_tbc_string = tbc_vals['rsa_tbc_string']
        elif spiff_dos_tot_box_rule_search:
            field_name = 'region_id'
            tbc_vals = self._calculate_tbc_commission(cr, uid, spiff_dos_tot_box_rule_search, all_region_actual_box, reg_no_of_exit, field_name, start_date, end_date, region_id, business_box_rule_ids, tot_rev, emp_model_id, region_traffic_stores, region_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_stl_tot_box_conv_percent = tbc_vals['spiff_stl_tot_box_conv_percent']
            spiff_stl_tot_box_rule_percent = tbc_vals['spiff_stl_tot_box_rule_percent']
            spiff_stl_tot_box_rule_amount = tbc_vals['spiff_stl_tot_box_rule_amount']
            spiff_stl_box_count = tbc_vals['spiff_stl_box_count']
            tot_box_payout_tier = tbc_vals['tot_box_payout_tier']
            rsa_tbc_string = tbc_vals['rsa_tbc_string']
        a = datetime.today()
        c = a - b
        print "TBC", c.total_seconds()
        # ################# Prepaid Goal Calculation ############################# Complete
        spiff_prepaid_obj = self.pool.get('spiff.prepaid.goal')
        spiff_emp_prepaid_ids = spiff_prepaid_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        store_prepaid_goal = 0.00
        store_pre_actual_count = 0.00
        store_pre_actual_percent = 0.00
        spiff_store_pre_payout = 0.00
        if spiff_emp_prepaid_ids:
            field_name = 'employee_id'
            cr.execute('select prepaid from spliting_goals where employee_id = %s and start_date <= %s and end_date >= %s',(emp_id,start_date,end_date))
            emp_prepaid_goal = map(lambda x: x[0], cr.fetchall())
            if not emp_prepaid_goal:
                emp_prepaid_goal = 0.00
            vals = self._calculate_prepaid_count_goal(cr, uid, spiff_emp_prepaid_ids, field_name, emp_id, start_date, end_date, prm_job_id, emp_prepaid_goal)
            store_prepaid_goal = vals['store_prepaid_goal']
            store_pre_actual_count = vals['store_pre_actual_count']
            store_pre_actual_percent = vals['store_pre_actual_percent']
            spiff_store_pre_payout = vals['spiff_store_pre_payout']
        spiff_store_prepaid_ids = spiff_prepaid_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_store_prepaid_ids:
            spiff_store_prepaid_data = spiff_prepaid_obj.browse(cr, uid, spiff_store_prepaid_ids[0])
            pre_sa_business_rule_id = spiff_store_prepaid_data.spiff_business_rule
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    field_name = 'store_id'
                    cr.execute('select prepaid from import_goals where store_id = %s and start_date <= %s and end_date >= %s',(store_id,start_date,end_date))
                    store_pre_goal = map(lambda x: x[0], cr.fetchall())
                    if not store_pre_goal:
                        store_pre_goal = 0.00
                    vals = self._calculate_prepaid_count_goal(cr, uid, spiff_store_prepaid_ids, field_name, store_id, start_date, end_date, prm_job_id, store_pre_goal)
                    store_prepaid_goal = vals['store_prepaid_goal']
                    store_pre_actual_count = vals['store_pre_actual_count']
                    store_pre_actual_percent = vals['store_pre_actual_percent']
                    spiff_store_pre_payout_pre = vals['spiff_store_pre_payout']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        spiff_store_pre_payout = spiff_store_pre_payout_pre
                    else:
                        spiff_store_pre_payout = spiff_store_pre_payout + (spiff_store_pre_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                count_multi = count_multi + 1
        spiff_market_prepaid_ids = spiff_prepaid_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_market_prepaid_ids:            
            field_name = 'market_id'
            cr.execute('''select prepaid from import_goals im, sap_store sap
                where sap.market_id = %s and im.store_id = sap.id and start_date <= %s and end_date >= %s''',(market_id,start_date,end_date))
            market_pre_goal = map(lambda x: x[0], cr.fetchall())
            if not market_pre_goal:
                market_pre_goal = 0.00
            vals = self._calculate_prepaid_count_goal(cr, uid, spiff_market_prepaid_ids, field_name, market_id, start_date, end_date, prm_job_id, market_pre_goal)
            store_prepaid_goal = vals['store_prepaid_goal']
            store_pre_actual_count = vals['store_pre_actual_count']
            store_pre_actual_percent = vals['store_pre_actual_percent']
            spiff_store_pre_payout_pre = vals['spiff_store_pre_payout']
        spiff_region_prepaid_ids = spiff_prepaid_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_region_prepaid_ids:
            field_name = 'region_id'
            cr.execute('''select prepaid from import_goals im, sap_store sap, market_place mkt
                where mkt.region_market_id = %s and sap.market_id = mkt.id and im.store_id = sap.id 
                and start_date <= %s and end_date >= %s''',(region_id,start_date,end_date))
            region_pre_goal = map(lambda x: x[0], cr.fetchall())
            if not region_pre_goal:
                region_pre_goal = 0.00
            vals = self._calculate_prepaid_count_goal(cr, uid, spiff_region_prepaid_ids, field_name, region_id, start_date, end_date, prm_job_id, region_pre_goal)
            store_prepaid_goal = vals['store_prepaid_goal']
            store_pre_actual_count = vals['store_pre_actual_count']
            store_pre_actual_percent = vals['store_pre_actual_percent']
            spiff_store_pre_payout_pre = vals['spiff_store_pre_payout']
        b = datetime.today()
        c = b - a
        print "Prepaid", c.total_seconds()
        # ############# APK Spiff Calculation ################################ Complete
        apk_obj = self.pool.get('spiff.apk')
        spiff_emp_apk_ids = apk_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        avg_apk = 0.00
        spiff_per_box_acc_sold = 0.00
        apk_payout = 0.00
        apk_actual_count = 0.00
        apk_comm_string = str("")
        if spiff_emp_apk_ids:
            field_name = 'employee_id'
            cr.execute("select sum(tot_box) from spliting_goals where employee_id=%s and start_date=%s",(emp_id,start_date))
            emp_box_goal_query = cr.fetchall()
            emp_box_goal = emp_box_goal_query[0][0]
            if not emp_box_goal:
                emp_box_goal = 0.00
            apk_vals = self._calculate_apk_calc(cr, uid, spiff_emp_apk_ids, field_name, emp_id, start_date, end_date, emp_box_goal, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            avg_apk = apk_vals['avg_apk']
            spiff_per_box_acc_sold = apk_vals['spiff_per_box_acc_sold']
            apk_payout = apk_vals['apk_payout']
            apk_actual_count = apk_vals['apk_actual_count']
            apk_comm_string = apk_vals['apk_comm_string']
        spiff_store_apk_ids = apk_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_store_apk_ids:
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    sto_box_goal = cr.execute("select sum(tot_box) from import_goals where store_id=%s and start_date >= '%s' and end_date <= '%s'"%(store_multi_id,start_date,end_date))
                    sto_box_goal = cr.fetchall()
                    sto_box_goal = sto_box_goal[0][0]
                    if not sto_box_goal:
                        sto_box_goal = 0
                    field_name = 'store_id'
                    apk_vals = self._calculate_apk_calc(cr, uid, spiff_store_apk_ids, field_name, store_multi_id, start_date, end_date, sto_box_goal, tot_store_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    avg_apk = apk_vals['avg_apk']
                    spiff_per_box_acc_sold = apk_vals['spiff_per_box_acc_sold']
                    apk_payout_pre = apk_vals['apk_payout']
                    apk_actual_count = apk_vals['apk_actual_count']
                    apk_comm_string = apk_vals['apk_comm_string']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        apk_payout = apk_payout_pre
                    else:
                        apk_payout = apk_payout + (apk_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                    count_multi = count_multi + 1
        spiff_market_apk_ids = apk_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_market_apk_ids:
            field_name = 'market_id'
            cr.execute('''select sum(im.tot_box) from import_goals im, sap_store sap
             where im.start_date >= %s and im.end_date <= %s
             and sap.market_id = %s and im.store_id = sap.id''',(start_date,end_date,market_id))
            market_box_goal_query = cr.fetchall()
            mkt_box_goal = market_box_goal_query[0][0]
            if not mkt_box_goal:
                mkt_box_goal = 0.00
            apk_vals = self._calculate_apk_calc(cr, uid, spiff_market_apk_ids, field_name, market_id, start_date, end_date, mkt_box_goal, tot_market_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            avg_apk = apk_vals['avg_apk']
            spiff_per_box_acc_sold = apk_vals['spiff_per_box_acc_sold']
            apk_payout = apk_vals['apk_payout']
            apk_actual_count = apk_vals['apk_actual_count']
            apk_comm_string = apk_vals['apk_comm_string']
        spiff_region_apk_ids = apk_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_region_apk_ids:
            field_name = 'region_id'
            cr.execute('''select sum(im.tot_box) from import_goals im, sap_store sap, market_place mkt
             where im.start_date >= %s and im.end_date <= %s and mkt.region_market_id = %s 
             and sap.market_id = mkt.id and im.store_id = sap.id''',(start_date,end_date,region_id))
            region_box_goal_query = cr.fetchall()
            reg_box_goal = region_box_goal_query[0][0]
            if not reg_box_goal:
                reg_box_goal = 0.00
            apk_vals = self._calculate_apk_calc(cr, uid, spiff_region_apk_ids, field_name, region_id, start_date, end_date, reg_box_goal, tot_region_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            avg_apk = apk_vals['avg_apk']
            spiff_per_box_acc_sold = apk_vals['spiff_per_box_acc_sold']
            apk_payout = apk_vals['apk_payout']
            apk_actual_count = apk_vals['apk_actual_count']
            apk_comm_string = apk_vals['apk_comm_string']
        # ############# JUMP Attachment Spiff Calculation ################################ Complete (Taking Postpaid and Upgrade both without Chargebacks)
        spiff_jump_obj = self.pool.get('spiff.jump.attachment')
        spiff_jump_emp_ids = spiff_jump_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        jump_goals = 0.00
        jump_attach_percent = 0.00
        jump_payout = 0.00
        jump_actual_count = 0.00
        jump_comm_string = str("")
        if spiff_jump_emp_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_jump_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_jump_emp_ids, prm_job_id, tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            jump_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            jump_attach_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            jump_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            jump_actual_count = emp_spiff_feature_data['count_3gb_smart_att']
            jump_comm_string = emp_spiff_feature_data['jump_comm_string']
        spiff_jump_store_ids = spiff_jump_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_jump_store_ids:
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    emp_spiff_feature_data = self._calculate_jump_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_jump_store_ids, prm_job_id, tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    jump_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                    jump_attach_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                    jump_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                    jump_actual_count = emp_spiff_feature_data['count_3gb_smart_att']
                    jump_comm_string = emp_spiff_feature_data['jump_comm_string']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        jump_payout = jump_payout_pre
                    else:
                        jump_payout = jump_payout + (jump_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                    count_multi = count_multi + 1
        spiff_jump_market_ids = spiff_jump_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_jump_market_ids:            
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_jump_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_jump_market_ids, prm_job_id, tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            jump_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            jump_attach_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            jump_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            jump_actual_count = emp_spiff_feature_data['count_3gb_smart_att']
            jump_comm_string = emp_spiff_feature_data['jump_comm_string']
        spiff_jump_region_ids = spiff_jump_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_jump_region_ids:            
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_jump_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_jump_region_ids, prm_job_id, tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            jump_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            jump_attach_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            jump_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            jump_actual_count = emp_spiff_feature_data['count_3gb_smart_att']
            jump_comm_string = emp_spiff_feature_data['jump_comm_string']    
        a = datetime.today()
        c = a - b
        print "APK, JUMP", c.total_seconds()
        # ############# JOD PHP Attachment Spiff Calculation ################################ Complete (Taking Postpaid and Upgrade both without Chargebacks)
        spiff_jod_php_obj = self.pool.get('spiff.jod.php.att')
        spiff_jod_php_ids = spiff_jod_php_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        jod_php_attach_count = 0.00
        jod_php_attach_percent = 0.00
        jod_php_attach_payout = 0.00
        jod_php_attach_goals = 0.00
        jod_php_attach_string = str("")
        if spiff_jod_php_ids:
            field_name = 'employee_id'
            emp_spiff_jod_data = self._calculate_jod_php_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_jod_php_ids, prm_job_id, tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            jod_php_attach_goals = emp_spiff_jod_data['jod_php_attach_goals']
            jod_php_attach_percent = emp_spiff_jod_data['jod_php_attach_percent']
            jod_php_attach_payout = emp_spiff_jod_data['jod_php_attach_payout']
            jod_php_attach_count = emp_spiff_jod_data['jod_php_attach_count']
            jod_php_attach_string = emp_spiff_jod_data['jod_php_attach_string']
        spiff_jod_php_store_ids = spiff_jod_php_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_jod_php_store_ids:
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    emp_spiff_jod_data = self._calculate_jod_php_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_jod_php_store_ids, prm_job_id, tot_store_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    jod_php_attach_goals = emp_spiff_jod_data['jod_php_attach_goals']
                    jod_php_attach_percent = emp_spiff_jod_data['jod_php_attach_percent']
                    jod_php_attach_payout_pre = emp_spiff_jod_data['jod_php_attach_payout']
                    jod_php_attach_count = emp_spiff_jod_data['jod_php_attach_count']
                    jod_php_attach_string = emp_spiff_jod_data['jod_php_attach_string']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        jod_php_attach_payout = jod_php_attach_payout_pre
                    else:
                        jod_php_attach_payout = jod_php_attach_payout + (jod_php_attach_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                    count_multi = count_multi + 1
        spiff_jod_php_market_ids = spiff_jod_php_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_jod_php_market_ids:            
            field_name = 'market_id'
            emp_spiff_jod_data = self._calculate_jod_php_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_jod_php_market_ids, prm_job_id, tot_market_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            jod_php_attach_goals = emp_spiff_jod_data['jod_php_attach_goals']
            jod_php_attach_percent = emp_spiff_jod_data['jod_php_attach_percent']
            jod_php_attach_payout = emp_spiff_jod_data['jod_php_attach_payout']
            jod_php_attach_count = emp_spiff_jod_data['jod_php_attach_count']
            jod_php_attach_string = emp_spiff_jod_data['jod_php_attach_string']
        spiff_jod_php_region_ids = spiff_jod_php_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_jod_php_region_ids:            
            field_name = 'region_id'
            emp_spiff_jod_data = self._calculate_jod_php_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_jod_php_region_ids, prm_job_id, tot_region_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            jod_php_attach_goals = emp_spiff_jod_data['jod_php_attach_goals']
            jod_php_attach_percent = emp_spiff_jod_data['jod_php_attach_percent']
            jod_php_attach_payout = emp_spiff_jod_data['jod_php_attach_payout']
            jod_php_attach_count = emp_spiff_jod_data['jod_php_attach_count']
            jod_php_attach_string = emp_spiff_jod_data['jod_php_attach_string']
        ######################### Score Attachment #####################################
        spiff_score_count = 0.00
        spiff_score_payout = 0.00
        spiff_score_string = str("")
        spiff_score_master = self.pool.get('spiff.score')
        spiff_emp_score_ids = spiff_score_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_emp_score_ids:
            field_name = 'employee_id'
            emp_spiff_score_data = self._calculate_score_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_emp_score_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_score_count = emp_spiff_score_data['spiff_score_count']
            spiff_score_payout = emp_spiff_score_data['spiff_score_payout']
            spiff_score_string = emp_spiff_score_data['spiff_score_string']
        spiff_score_store_ids = spiff_score_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_score_store_ids:
            field_name = 'store_id'
            emp_spiff_score_data = self._calculate_score_attachment(cr, uid, field_name, start_date, end_date, store_id, spiff_score_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_score_count = emp_spiff_score_data['spiff_score_count']
            spiff_score_payout = emp_spiff_score_data['spiff_score_payout']
            spiff_score_string = emp_spiff_score_data['spiff_score_string']
        spiff_score_market_ids = spiff_score_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_score_market_ids:
            field_name = 'market_id'
            emp_spiff_score_data = self._calculate_score_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_score_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_score_count = emp_spiff_score_data['spiff_score_count']
            spiff_score_payout = emp_spiff_score_data['spiff_score_payout']
            spiff_score_string = emp_spiff_score_data['spiff_score_string']
        spiff_score_region_ids = spiff_score_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_score_region_ids:
            field_name = 'region_id'
            emp_spiff_score_data = self._calculate_score_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_score_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_score_count = emp_spiff_score_data['spiff_score_count']
            spiff_score_payout = emp_spiff_score_data['spiff_score_payout']
            spiff_score_string = emp_spiff_score_data['spiff_score_string']
        ######################### Small Business Attachment #####################################
        small_b2b_count = 0.00
        small_b2b_payout = 0.00
        small_b2b_string = str("")
        spiff_b2b_master = self.pool.get('spiff.small.business')
        spiff_emp_b2b_ids = spiff_b2b_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_emp_b2b_ids:
            field_name = 'employee_id'
            emp_spiff_b2b_data = self._calculate_small_b2b(cr, uid, field_name, start_date, end_date, emp_id, spiff_emp_b2b_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            small_b2b_count = emp_spiff_b2b_data['spiff_score_count']
            small_b2b_payout = emp_spiff_b2b_data['spiff_score_payout']
            small_b2b_string = emp_spiff_b2b_data['spiff_score_string']
        spiff_b2b_store_ids = spiff_b2b_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_b2b_store_ids:
            field_name = 'store_id'
            emp_spiff_b2b_data = self._calculate_small_b2b(cr, uid, field_name, start_date, end_date, store_id, spiff_b2b_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            small_b2b_count = emp_spiff_b2b_data['spiff_score_count']
            small_b2b_payout = emp_spiff_b2b_data['spiff_score_payout']
            small_b2b_string = emp_spiff_b2b_data['spiff_score_string']
        spiff_b2b_market_ids = spiff_b2b_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_b2b_market_ids:
            field_name = 'market_id'
            emp_spiff_b2b_data = self._calculate_small_b2b(cr, uid, field_name, start_date, end_date, market_id, spiff_b2b_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            small_b2b_count = emp_spiff_b2b_data['spiff_score_count']
            small_b2b_payout = emp_spiff_b2b_data['spiff_score_payout']
            small_b2b_string = emp_spiff_b2b_data['spiff_score_string']
        spiff_b2b_region_ids = spiff_b2b_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_b2b_region_ids:
            field_name = 'region_id'
            emp_spiff_b2b_data = self._calculate_small_b2b(cr, uid, field_name, start_date, end_date, region_id, spiff_b2b_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            small_b2b_count = emp_spiff_b2b_data['spiff_score_count']
            small_b2b_payout = emp_spiff_b2b_data['spiff_score_payout']
            small_b2b_string = emp_spiff_b2b_data['spiff_score_string']
        # ###################### 3GB+ Data Attachment Smartphone ##########################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', '3gb_data_smart_attach_payout'), ('model_id', '=', comm_model_id[0])])
        spiff_master_3gb_smart_percent = 0.00
        spiff_3gb_smart_percent = 0.00
        spiff_3gb_smart_payout = 0.00
        count_3gb_smart_att = 0.00
        spiff_3gb_smart_string = str("")
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_master_3gb_smart_percent = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            spiff_3gb_smart_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            spiff_3gb_smart_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            count_3gb_smart_att = emp_spiff_feature_data['count_3gb_smart_att']
            spiff_3gb_smart_string = emp_spiff_feature_data['paid_comm_string']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    spiff_master_3gb_smart_percent = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                    spiff_3gb_smart_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                    spiff_3gb_smart_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                    count_3gb_smart_att = emp_spiff_feature_data['count_3gb_smart_att']
                    spiff_3gb_smart_string = emp_spiff_feature_data['paid_comm_string']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        spiff_3gb_smart_payout = spiff_3gb_smart_payout_pre
                    else:
                        spiff_3gb_smart_payout = spiff_3gb_smart_payout + (spiff_3gb_smart_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                    count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_master_3gb_smart_percent = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            spiff_3gb_smart_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            spiff_3gb_smart_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            count_3gb_smart_att = emp_spiff_feature_data['count_3gb_smart_att']
            spiff_3gb_smart_string = emp_spiff_feature_data['paid_comm_string']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_master_3gb_smart_percent = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            spiff_3gb_smart_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            spiff_3gb_smart_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            count_3gb_smart_att = emp_spiff_feature_data['count_3gb_smart_att']
            spiff_3gb_smart_string = emp_spiff_feature_data['paid_comm_string']
        b = datetime.today()
        c = b - a
        print "3GB+ attachment", c.total_seconds()
        # ##################################### Base field 1 ################################################
        ir_field_base1_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field1_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field1_goals = 0.00
        demo_field1_percent = 0.00
        demo_field1_payout = 0.00
        demo_field1_count = 0.00
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_base1_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field1_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field1_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field1_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field1_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_base1_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            dealer_obj_search_single = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_single:
                emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field1_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                demo_field1_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                demo_field1_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
                demo_field1_count = emp_spiff_feature_data['count_3gb_smart_att']
            else:
                cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
                dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
                if dealer_obj_search_multi:
                    date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                    days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                    count_multi = 0
                    for dealer_obj_search_multi_id in dealer_obj_search_multi:
                        dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                        store_multi_id = dealer_obj_data_multi.store_name.id
                        if count_multi == 0:
                            goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                        else:
                            goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                        if dealer_obj_data_multi.end_date >= end_date:
                            goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        else:
                            goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                        delta_date = goal_end_date - goal_start_date
                        emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                        demo_field1_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                        demo_field1_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                        demo_field1_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                        demo_field1_count = emp_spiff_feature_data['count_3gb_smart_att']
                        if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                            demo_field1_payout = demo_field1_payout_pre
                        else:
                            demo_field1_payout = demo_field1_payout + (demo_field1_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                        count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_base1_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field1_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field1_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field1_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field1_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_base1_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field1_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field1_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field1_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field1_count = emp_spiff_feature_data['count_3gb_smart_att']
        a = datetime.today()
        c = a - b
        print "Family Postpaid", c.total_seconds()
        # ######################## Base Field 2 #######################################################################
        ir_field_base2_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field2_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field2_goals = 0.00
        demo_field2_percent = 0.00
        demo_field2_payout = 0.00
        demo_field2_count = 0.00
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_base2_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field2_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field2_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field2_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field2_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_base2_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            dealer_obj_search_single = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_single:
                emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field2_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                demo_field2_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                demo_field2_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
                demo_field2_count = emp_spiff_feature_data['count_3gb_smart_att']
            else:
                cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
                dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
                if dealer_obj_search_multi:
                    date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                    days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                    count_multi = 0
                    for dealer_obj_search_multi_id in dealer_obj_search_multi:
                        dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                        store_multi_id = dealer_obj_data_multi.store_name.id
                        if count_multi == 0:
                            goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                        else:
                            goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                        if dealer_obj_data_multi.end_date >= end_date:
                            goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        else:
                            goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                        delta_date = goal_end_date - goal_start_date
                        emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                        demo_field2_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                        demo_field2_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                        demo_field2_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                        demo_field2_count = emp_spiff_feature_data['count_3gb_smart_att']
                        if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                            demo_field2_payout = demo_field2_payout_pre
                        else:
                            demo_field2_payout = demo_field2_payout + (demo_field2_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                        count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_base2_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field2_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field2_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field2_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field2_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_base2_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field2_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field2_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field2_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field2_count = emp_spiff_feature_data['count_3gb_smart_att']
        b = datetime.today()
        c = b - a
        print "Family Upgrade", c.total_seconds()
        # ######################## Base Field 4 #######################################################################
        ir_field_base4_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field4_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field4_goals = 0.00
        demo_field4_percent = 0.00
        demo_field4_payout = 0.00
        demo_field4_count = 0.00
        paid_comm_string = str("")
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_base4_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field4_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field4_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field4_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field4_count = emp_spiff_feature_data['count_3gb_smart_att']
            paid_comm_string = emp_spiff_feature_data['paid_comm_string']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_base4_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_multi:
                date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                count_multi = 0
                for dealer_obj_search_multi_id in dealer_obj_search_multi:
                    dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                    store_multi_id = dealer_obj_data_multi.store_name.id
                    if count_multi == 0:
                        goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                    if dealer_obj_data_multi.end_date >= end_date:
                        goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                    delta_date = goal_end_date - goal_start_date
                    emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    demo_field4_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                    demo_field4_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                    demo_field4_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                    demo_field4_count = emp_spiff_feature_data['count_3gb_smart_att']
                    paid_comm_string = emp_spiff_feature_data['paid_comm_string']
                    if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                        demo_field4_payout = demo_field4_payout_pre
                    else:
                        demo_field4_payout = demo_field4_payout + (demo_field4_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                    count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_base4_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field4_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field4_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field4_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field4_count = emp_spiff_feature_data['count_3gb_smart_att']
            paid_comm_string = emp_spiff_feature_data['paid_comm_string']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_base4_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field4_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field4_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field4_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field4_count = emp_spiff_feature_data['count_3gb_smart_att']
            paid_comm_string = emp_spiff_feature_data['paid_comm_string']
        # ##################################### Base field 5 ################################################
        ir_field_base5_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field5_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field5_goals = 0.00
        demo_field5_percent = 0.00
        demo_field5_payout = 0.00
        demo_field5_count = 0.00
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_base5_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field5_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field5_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field5_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field5_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_base5_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            dealer_obj_search_single = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_single:
                emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field5_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                demo_field5_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                demo_field5_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
                demo_field5_count = emp_spiff_feature_data['count_3gb_smart_att']
            else:
                cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
                dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
                if dealer_obj_search_multi:
                    date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                    days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                    count_multi = 0
                    for dealer_obj_search_multi_id in dealer_obj_search_multi:
                        dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                        store_multi_id = dealer_obj_data_multi.store_name.id
                        if count_multi == 0:
                            goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                        else:
                            goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                        if dealer_obj_data_multi.end_date >= end_date:
                            goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        else:
                            goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                        delta_date = goal_end_date - goal_start_date
                        emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                        demo_field5_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                        demo_field5_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                        demo_field5_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                        demo_field5_count = emp_spiff_feature_data['count_3gb_smart_att']
                        if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                            demo_field5_payout = demo_field5_payout_pre
                        else:
                            demo_field5_payout = demo_field5_payout + (demo_field5_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                        count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_base5_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field5_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field5_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field5_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field5_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_base5_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field5_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field5_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field5_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field5_count = emp_spiff_feature_data['count_3gb_smart_att']
        # ##################################### Base field 6 ################################################
        ir_field_base6_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field6_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field6_goals = 0.00
        demo_field6_percent = 0.00
        demo_field6_payout = 0.00
        demo_field6_count = 0.00
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_base6_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field6_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field6_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field6_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field6_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_base6_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            dealer_obj_search_single = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_single:
                emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field6_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                demo_field6_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                demo_field6_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
                demo_field6_count = emp_spiff_feature_data['count_3gb_smart_att']
            else:
                cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
                dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
                if dealer_obj_search_multi:
                    date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                    days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                    count_multi = 0
                    for dealer_obj_search_multi_id in dealer_obj_search_multi:
                        dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                        store_multi_id = dealer_obj_data_multi.store_name.id
                        if count_multi == 0:
                            goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                        else:
                            goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                        if dealer_obj_data_multi.end_date >= end_date:
                            goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        else:
                            goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                        delta_date = goal_end_date - goal_start_date
                        emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                        demo_field6_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                        demo_field6_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                        demo_field6_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                        demo_field6_count = emp_spiff_feature_data['count_3gb_smart_att']
                        if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                            demo_field6_payout = demo_field6_payout_pre
                        else:
                            demo_field6_payout = demo_field6_payout + (demo_field6_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                        count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_base6_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field6_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field6_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field6_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field6_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_base6_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field6_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field6_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field6_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field6_count = emp_spiff_feature_data['count_3gb_smart_att']
        # ##################################### Base field 7 ################################################
        ir_field_base7_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field7_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field7_goals = 0.00
        demo_field7_percent = 0.00
        demo_field7_payout = 0.00
        demo_field7_count = 0.00
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_base7_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field7_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field7_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field7_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field7_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_base7_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            dealer_obj_search_single = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_single:
                emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field7_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                demo_field7_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                demo_field7_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
                demo_field7_count = emp_spiff_feature_data['count_3gb_smart_att']
            else:
                cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
                dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
                if dealer_obj_search_multi:
                    date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                    days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                    count_multi = 0
                    for dealer_obj_search_multi_id in dealer_obj_search_multi:
                        dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                        store_multi_id = dealer_obj_data_multi.store_name.id
                        if count_multi == 0:
                            goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                        else:
                            goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                        if dealer_obj_data_multi.end_date >= end_date:
                            goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        else:
                            goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                        delta_date = goal_end_date - goal_start_date
                        emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                        demo_field7_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                        demo_field7_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                        demo_field7_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                        demo_field7_count = emp_spiff_feature_data['count_3gb_smart_att']
                        if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                            demo_field7_payout = demo_field7_payout_pre
                        else:
                            demo_field7_payout = demo_field7_payout + (demo_field7_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                        count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_base7_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field7_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field7_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field7_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field7_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_base7_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field7_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field7_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field7_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field7_count = emp_spiff_feature_data['count_3gb_smart_att']
        # ##################################### Base field 8 ################################################
        ir_field_base8_ids = ir_field_obj.search(cr, uid, [('name', '=', 'demo_field8_payout'), ('model_id', '=', comm_model_id[0])])
        demo_field8_goals = 0.00
        demo_field8_percent = 0.00
        demo_field8_payout = 0.00
        demo_field8_count = 0.00
        spiff_feature_master_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_field_name', '=', ir_field_base8_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_master_ids:
            field_name = 'employee_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field8_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field8_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field8_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field8_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_store_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_field_name', '=', ir_field_base8_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_store_ids:
            field_name = 'store_id'
            dealer_obj_search_single = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_obj_search_single:
                emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                demo_field8_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                demo_field8_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                demo_field8_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
                demo_field8_count = emp_spiff_feature_data['count_3gb_smart_att']
            else:
                cr.execute("select * from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
                dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
                if dealer_obj_search_multi:
                    date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
                    days_in_month = calendar.monthrange(date_monthrange.year,date_monthrange.month)[1]
                    count_multi = 0
                    for dealer_obj_search_multi_id in dealer_obj_search_multi:
                        dealer_obj_data_multi = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id)
                        store_multi_id = dealer_obj_data_multi.store_name.id
                        if count_multi == 0:
                            goal_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                        else:
                            goal_start_date = datetime.strptime(dealer_obj_data_multi.start_date, '%Y-%m-%d').date()
                        if dealer_obj_data_multi.end_date >= end_date:
                            goal_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        else:
                            goal_end_date = datetime.strptime(dealer_obj_data_multi.end_date, '%Y-%m-%d').date()
                        delta_date = goal_end_date - goal_start_date
                        emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, store_multi_id, spiff_feature_store_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                        demo_field8_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
                        demo_field8_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
                        demo_field8_payout_pre = emp_spiff_feature_data['spiff_3gb_smart_payout']
                        demo_field8_count = emp_spiff_feature_data['count_3gb_smart_att']
                        if dealer_obj_data_multi.end_date >= end_date and len(dealer_obj_search_multi) == 1:
                            demo_field8_payout = demo_field8_payout_pre
                        else:
                            demo_field8_payout = demo_field8_payout + (demo_field8_payout_pre * float(delta_date.days + 1) / float(days_in_month))
                        count_multi = count_multi + 1
        spiff_feature_market_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_field_name', '=', ir_field_base8_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_market_ids:
            field_name = 'market_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, market_id, spiff_feature_market_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field8_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field8_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field8_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field8_count = emp_spiff_feature_data['count_3gb_smart_att']
        spiff_feature_region_ids = spiff_feature_master.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_field_name', '=', ir_field_base8_ids[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_feature_region_ids:
            field_name = 'region_id'
            emp_spiff_feature_data = self._calculate_feature_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_feature_region_ids,prm_job_id,tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            demo_field8_goals = emp_spiff_feature_data['spiff_master_3gb_smart_percent']
            demo_field8_percent = emp_spiff_feature_data['spiff_3gb_smart_percent']
            demo_field8_payout = emp_spiff_feature_data['spiff_3gb_smart_payout']
            demo_field8_count = emp_spiff_feature_data['count_3gb_smart_att']
        # #################### Mobile Internet Conversion ##########################
        ir_field_ids = ir_field_obj.search(cr, uid, [('name', '=', 'mi_conv_payout'), ('model_id', '=', comm_model_id[0])])
        spiff_mi_conv_percent = 0.00
        spiff_master_mi_conv_percent = 0.00
        spiff_mi_conv_payout = 0.00
        spiff_mi_conv_count = 0.00
        mi_conv_string = str("")
        if ir_field_ids:
            spiff_sa_mi_1gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            spiff_store_mi_1gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            spiff_market_mi_1gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            spiff_region_mi_1gb_ids = spiff_sa_mi_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_field_name', '=', ir_field_ids[0]), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
            if spiff_sa_mi_1gb_ids:
                if company_ids_search:
                    field_name = 'employee_id'
                    mi_1gb_vals = self._calculate_mi_gb_company(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_1gb_ids, prm_job_id, tot_rev, com_exit_traffic, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    spiff_mi_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                    spiff_mi_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                    spiff_master_mi_conv_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                    spiff_mi_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                    mi_conv_string = mi_1gb_vals['mi_1gb_string']
                else:
                    field_name = 'employee_id'
                    # sa_mi_count_payout = 0.00
                    mi_1gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_1gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    spiff_mi_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                    spiff_mi_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                    spiff_master_mi_conv_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                    spiff_mi_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                    mi_conv_string = mi_1gb_vals['mi_1gb_string']
            elif spiff_store_mi_1gb_ids:
                ###### code to get the company wide MI Conversion incase the store of the
                ###### employee is a Kiosk type of Store and putting the other condition in else part in
                ###### below. 03062015
                logger.error("exit traffic for Company is %s",prm_job_id)
                if company_ids_search:
                    field_name = 'store_id'
                    mi_1gb_vals = self._calculate_mi_gb_company(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_1gb_ids, prm_job_id, tot_store_rev, com_exit_traffic, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    spiff_mi_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                    spiff_mi_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                    spiff_master_mi_conv_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                    spiff_mi_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                    mi_conv_string = mi_1gb_vals['mi_1gb_string']
                else:
                    field_name = 'store_id'
                    mi_1gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_1gb_ids, prm_job_id, tot_store_rev, sto_no_of_exit, emp_model_id, [], store_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    spiff_mi_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                    spiff_mi_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                    spiff_master_mi_conv_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                    spiff_mi_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                    mi_conv_string = mi_1gb_vals['mi_1gb_string']
                #### code ends here 03062015.
            elif spiff_market_mi_1gb_ids:
                field_name = 'market_id'
                mi_1gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_1gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, market_traffic_stores, market_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_mi_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                spiff_mi_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_mi_conv_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                spiff_mi_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                mi_conv_string = mi_1gb_vals['mi_1gb_string']
            elif spiff_region_mi_1gb_ids:
                field_name = 'region_id'
                mi_1gb_vals = self._calculate_mi_gb(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_1gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, region_traffic_stores, region_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_mi_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                spiff_mi_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                spiff_master_mi_conv_percent = mi_1gb_vals['spiff_master_mi_conv_percent']
                spiff_mi_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                mi_conv_string = mi_1gb_vals['mi_1gb_string']
        a = datetime.today()
        c = a - b
        print "base field for 3gb att, MI Conv", c.total_seconds()
        #     *********************** Prepaid Conversion Formula ********************  ###########
        pre_conv_goal = 0.00
        pre_conv_percent = 0.00
        pre_conv_count = 0.00
        pre_conv_payout = 0.00
        pre_conv_string = str("")
        spiff_pre_conv_obj = self.pool.get('spiff.prepaid.conversion')
        spiff_sa_mi_1gb_ids = spiff_pre_conv_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        spiff_store_mi_1gb_ids = spiff_pre_conv_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        spiff_market_mi_1gb_ids = spiff_pre_conv_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        spiff_region_mi_1gb_ids = spiff_pre_conv_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_sa_mi_1gb_ids:
            field_name = 'employee_id'
            # sa_mi_count_payout = 0.00
            ###### code to get the company wide Prepaid Conversion incase the store of the
            ###### employee is a Kiosk type of Store and putting the other condition in else part in
            ###### below. 03062015
            logger.error("GB Ids is %s",spiff_sa_mi_1gb_ids)
            if company_ids_search:
                mi_1gb_vals = self._calculate_pre_conv_company(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_1gb_ids, prm_job_id, tot_rev, com_exit_traffic, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                pre_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                pre_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                pre_conv_goal = mi_1gb_vals['spiff_master_mi_conv_percent']
                pre_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                pre_conv_string = mi_1gb_vals['pre_conv_string']
            else:
                mi_1gb_vals = self._calculate_pre_conv(cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_1gb_ids, prm_job_id, tot_rev, sto_no_of_exit, emp_model_id, [], [],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                pre_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                pre_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                pre_conv_goal = mi_1gb_vals['spiff_master_mi_conv_percent']
                pre_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                pre_conv_string = mi_1gb_vals['pre_conv_string']
        elif spiff_store_mi_1gb_ids:
            field_name = 'store_id'
            ###### code to get the Company wide Prepaid Conversion incase the store of the
            ###### employee is a Kiosk type of Store and putting the other condition in else part in
            ###### below. 03062015
            logger.error("spiff_sa_mi_1gb_ids gb uds is %s",spiff_store_mi_1gb_ids)
            if company_ids_search:
                mi_1gb_vals = self._calculate_pre_conv_company(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_1gb_ids, prm_job_id, tot_store_rev, com_exit_traffic, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                pre_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                pre_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                pre_conv_goal = mi_1gb_vals['spiff_master_mi_conv_percent']
                pre_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                pre_conv_string = mi_1gb_vals['pre_conv_string']
                logger.error("Prepaid Conversion is %s",mi_1gb_vals)
            else:
                mi_1gb_vals = self._calculate_pre_conv(cr, uid, field_name, start_date, end_date, store_id, spiff_store_mi_1gb_ids, prm_job_id, tot_store_rev, sto_no_of_exit, emp_model_id, [], store_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                pre_conv_count = mi_1gb_vals['spiff_mi_gb_count']
                pre_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
                pre_conv_goal = mi_1gb_vals['spiff_master_mi_conv_percent']
                pre_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
                pre_conv_string = mi_1gb_vals['pre_conv_string']
        elif spiff_market_mi_1gb_ids:
            field_name = 'market_id'
            mi_1gb_vals = self._calculate_pre_conv(cr, uid, field_name, start_date, end_date, market_id, spiff_market_mi_1gb_ids, prm_job_id, tot_rev, mkt_no_of_exit, emp_model_id, market_traffic_stores, market_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            pre_conv_count = mi_1gb_vals['spiff_mi_gb_count']
            pre_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
            pre_conv_goal = mi_1gb_vals['spiff_master_mi_conv_percent']
            pre_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
            pre_conv_string = mi_1gb_vals['pre_conv_string']
        elif spiff_region_mi_1gb_ids:
            field_name = 'region_id'
            mi_1gb_vals = self._calculate_pre_conv(cr, uid, field_name, start_date, end_date, region_id, spiff_region_mi_1gb_ids, prm_job_id, tot_rev, reg_no_of_exit, emp_model_id, region_traffic_stores, region_traffic_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            pre_conv_count = mi_1gb_vals['spiff_mi_gb_count']
            pre_conv_payout = mi_1gb_vals['spiff_sa_mi_3gb_amount']
            pre_conv_goal = mi_1gb_vals['spiff_master_mi_conv_percent']
            pre_conv_percent = mi_1gb_vals['spiff_mi_conv_percent']
            pre_conv_string = mi_1gb_vals['pre_conv_string']
        # ################ For KIOSK Store ############################################
        # ########################### Application Goal ###################################
        spiff_app_goal = self.pool.get('spiff.application.goal')
        app_goal_payout = 0.00
        app_goal_percent = 0.00
        pos_count = 0.00
        app_goal_master = 0.00
        spiff_store_app_goal = spiff_app_goal.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_store_class', '=', store_classification_id), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_store_app_goal:
            spiff_store_app_goal_data = spiff_app_goal.browse(cr, uid, spiff_store_app_goal[0])
            spiff_cc_type = spiff_store_app_goal_data.spiff_cc_type.id
            spiff_app_goal_master = spiff_store_app_goal_data.spiff_app_goal_master
            cr.execute('''select sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) 
    + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end) as total_boxes
    from 
    (select id,product_id,dsr_trans_type,dsr_credit_class,prm_dsr_smd
    from wireless_dsr_postpaid_line
    union all
    select id,product_id,dsr_trans_type,dsr_credit_class,prm_dsr_smd
    from wireless_dsr_upgrade_line) as test inner join wireless_dsr dsr on (test.product_id = dsr.id)
                                        inner join sap_store sap on (dsr.dsr_store_id = sap.id and sap.id=%s)
                                        inner join credit_class cr on (test.dsr_credit_class = cr.id)
                                        where dsr.dsr_date between %s and %s 
                                        and dsr.state = 'done' 
                                        and test.prm_dsr_smd = false
                                        and cr.category_type = %s''', (store_id, start_date, end_date, spiff_cc_type))
            prime_count_data = cr.fetchall()
            pos_count = prime_count_data[0][0]
            if not pos_count:
                pos_count = 0.00
            goal_ids = goal_obj.search(cr, uid, [('store_id', '=', store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
            if goal_ids:
                goal_data = goal_obj.browse(cr, uid, goal_ids[0])
                # app_goal_master = (goal_data.app_goal * delta_date)/days_in_month#krishna code
                app_goal_master = goal_data.app_goal  # shashank code 1/12
            if app_goal_master > 0.00:
                app_goal_percent = (pos_count * 100) / app_goal_master
            if app_goal_percent >= 200.00:
                app_goal_payout = spiff_store_app_goal_data.spiff_amount_above_200
            if spiff_app_goal_master:
                for spiff_app_goal_master_id in spiff_app_goal_master:
                    app_goal_master_min_percent = spiff_app_goal_master_id.spiff_from_percent
                    app_goal_master_max_percent = spiff_app_goal_master_id.spiff_to_percent
                    if app_goal_percent >= app_goal_master_min_percent and app_goal_percent <= app_goal_master_max_percent:
                        app_goal_payout = spiff_app_goal_master_id.spiff_amount
        b = datetime.today()
        c = b - a
        print "Application Goal", c.total_seconds()
        # ################## Spiff Box Goal #############################################
        spiff_box_goal = self.pool.get('spiff.box.goal')
        box_goal_payout = 0.00
        box_goal_percent = 0.00
        box_count = 0.00
        box_goal_master = 0.00
        spiff_box_goal_ids = spiff_box_goal.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_store_class', '=', store_classification_id), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_box_goal_ids:
            spiff_box_goal_data = spiff_box_goal.browse(cr, uid, spiff_box_goal_ids[0])
            box_goal_master_percent = spiff_box_goal_data.spiff_percent_to_box
            box_count = store_actual_box
            goal_ids = goal_obj.search(cr, uid, [('store_id', '=', store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
            if goal_ids:
                goal_data = goal_obj.browse(cr, uid, goal_ids[0])
                # box_goal_master = (goal_data.tot_box * delta_date)/days_in_month#krishna code
                box_goal_master = goal_data.tot_box  # shashank code 1/12
            if box_goal_master > 0.00:    
                box_goal_percent = (box_count * 100) / box_goal_master
            if box_goal_percent >= box_goal_master_percent:
                box_goal_payout = spiff_box_goal_data.spiff_amount
        # ######################## Spiff MI Box Goal ########################################
        spiff_mi_box_goal = self.pool.get('spiff.boxes.with.tablet')
        mi_goal_payout = 0.00
        mi_goal_percent = 0.00
        mi_count = 0.00
        mi_goal_master = 0.00
        spiff_mi_goal_ids = spiff_mi_box_goal.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('spiff_store_class', '=', store_classification_id), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_mi_goal_ids:
            spiff_mi_goal_data = spiff_mi_box_goal.browse(cr, uid, spiff_mi_goal_ids[0])
            cr.execute('select phone_id from spiff_box_phone_rel where jump_id=%s' % spiff_mi_goal_ids[0])
            spiff_phone_type = map(lambda x: x[0], cr.fetchall())
            mi_goal_master = store_tot_box
            cr.execute('''select count(upg.id) as count
from (select id,product_id,dsr_product_code_type,dsr_imei_no from wireless_dsr_postpaid_line 
union all 
select id,product_id,dsr_product_code_type,dsr_imei_no from wireless_dsr_upgrade_line
union all
select id,product_id,dsr_product_code_type,dsr_imei_no from wireless_dsr_prepaid_line) 
as upg, wireless_dsr dsr
where upg.product_id = dsr.id
and dsr.dsr_store_id = %s 
and dsr.dsr_date between %s and %s
and dsr.state = 'done'
and left(upg.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type in %s)''', (store_id, start_date, end_date, tuple(spiff_phone_type)))
            mi_box_count_data = cr.fetchall()
            mi_count = mi_box_count_data[0][0]
            if mi_goal_master > 0.00:
                mi_goal_percent = (float(mi_count) * 100) / float(mi_goal_master)
            store_goal_ids = goal_obj.search(cr, uid, [('store_id', '=', store_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
            store_goal = 0.00
            if store_goal_ids:
                # store_goal = (goal_obj.browse(cr, uid, store_goal_ids[0]).tot_box * delta_date)/days_in_month#krishna code
                store_goal = goal_obj.browse(cr, uid, store_goal_ids[0]).tot_box  # shashank code 1/12
            if mi_goal_master >= store_goal:
                mi_goal_master_percent = spiff_mi_goal_data.spiff_percent_to_box
                if mi_goal_percent >= mi_goal_master_percent:
                    mi_goal_payout = spiff_mi_goal_data.spiff_amount
        a = datetime.today()
        c = a - b
        print "MI and Box Goal", c.total_seconds()
        # ###################### Market Profitability Spiff ########################################
        spiff_profitability = self.pool.get('spiff.profitability')
        demo_field3_count = 0.00
        demo_field3_goals = 0.00
        demo_field3_percent = 0.00
        demo_field3_payout = 0.00
        spiff_mkt_search_ids = spiff_profitability.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_mkt_search_ids:
            spiff_mkt_search_data = spiff_profitability.browse(cr, uid, spiff_mkt_search_ids[0])
            demo_field3_goals = spiff_mkt_search_data.spiff_profit_percent
            cr.execute('''select sum(netincome) from import_profit_loss where start_date >= %s and end_date <= %s''', (start_date, end_date))
            company_inc_query = cr.fetchall()
            company_inc = company_inc_query[0][0]
            cr.execute('''select sum(netincome) from import_profit_loss pl
                inner join sap_store sap on (pl.store_id = sap.id)
                inner join market_place mkt on (sap.market_id = mkt.id)
                where pl.start_date >= %s and pl.end_date <= %s
                and mkt.id = %s''', (start_date, end_date, market_id))
            market_inc_query = cr.fetchall()
            demo_field3_count = market_inc_query[0][0]
            if not demo_field3_count:
                demo_field3_count = 0.00
            if company_inc > 0.00 and demo_field3_count > 0.00:
                demo_field3_percent = (float(demo_field3_count) * 100) / float(company_inc)
            if demo_field3_percent >= demo_field3_goals:
                demo_field3_payout = spiff_mkt_search_data.spiff_payout
        spiff_reg_search_ids = spiff_profitability.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_reg_search_ids:
            spiff_reg_search_data = spiff_profitability.browse(cr, uid, spiff_reg_search_ids[0])
            demo_field3_goals = spiff_reg_search_data.spiff_profit_percent
            cr.execute('''select sum(netincome) from import_profit_loss where start_date >= %s and end_date <= %s''', (start_date, end_date))
            company_inc_query = cr.fetchall()
            company_inc = company_inc_query[0][0]
            cr.execute('''select sum(netincome) from import_profit_loss pl
                inner join sap_store sap on (pl.store_id = sap.id)
                inner join market_place mkt on (sap.market_id = mkt.id)
                inner join market_regions reg on (mkt.region_market_id = reg.id)
                where pl.start_date >= %s and pl.end_date <= %s
                and reg.id = %s''', (start_date, end_date, region_id))
            market_inc_query = cr.fetchall()
            demo_field3_count = market_inc_query[0][0]
            if not demo_field3_count:
                demo_field3_count = 0.00
            if company_inc > 0.00 and demo_field3_count > 0.00:
                demo_field3_percent = (float(demo_field3_count) * 100) / float(company_inc)
            if demo_field3_percent >= demo_field3_goals:
                demo_field3_payout = spiff_reg_search_data.spiff_payout
        # ####################### Gross Payout Calculation #######################################
        gross_payout = base_payout + kicker_rev_goal_payout + kicker_box_goal_payout + kicker_store_rev_goal_payout + pre_conv_payout
        gross_payout = gross_payout + store_payout + market_share_profit + base_box_payout + rev_goal_att_payout + tot_box_psa_payout
        gross_payout = gross_payout + spiff_store_pre_payout + jump_payout + apk_payout + spiff_3gb_unl_payout + spiff_stl_tot_box_rule_amount + spiff_sa_mi_1gb_payout + spiff_sa_mi_3gb_payout + spiff_sa_mi_5gb_payout + spiff_3gb_smart_payout + spiff_mi_conv_payout + app_goal_payout + box_goal_payout + mi_goal_payout
        gross_payout = gross_payout + demo_field1_payout + demo_field2_payout + demo_field3_payout + demo_field4_payout + demo_field5_payout + demo_field6_payout + demo_field7_payout + demo_field8_payout 
        gross_payout = gross_payout + voc_payout + labor_prod_payout + spiff_score_payout + small_b2b_payout + turnover_payout + jod_php_attach_payout
        
        gross_payout = gross_payout + vision_reward_sale_top_market_payout + vision_reward_sale_top_company_payout 
        gross_payout = gross_payout + vision_reward_dos_top_region_payout + vision_reward_mm_top_market_payout + vision_reward_sale_top_percent_store_pay 
        gross_payout = gross_payout + vision_reward_stl_top_company_payout + vision_reward_dos_top_leader_payout + float(vision_reward_mm_top_leader_market_payout)
        gross_payout = gross_payout + vision_reward_sale_top_comp_leader_payout + vision_reward_ops_top_store_pay + float(vision_reward_mm_top_ops_market_payout) + vision_reward_dos_top_ops_payout
        # ####################### Writing Values in Object #######################################
        b = datetime.today()
        c = b - a
        print "Profit Spiff, Gross Payout", c.total_seconds()
        rsa_tbc_achieved = spiff_stl_tot_box_conv_percent
        rsa_tbc_payout = spiff_stl_tot_box_rule_amount
        rsa_tbc_goal = spiff_stl_tot_box_rule_percent
        rsa_rph_target = labor_prod_achieved
        rsa_rph_payout = labor_prod_payout
        self.write(cr, uid, ids, { 'base_tot_rev':base_tot_rev,
                                    'base_payout': base_payout,
                                    'base_rev_string':base_rev_string,
                                   # ********  
                                    'voc_achieved':voc_achieved,
                                    'voc_payout':voc_payout,
                                    'voc_target':voc_target,
                                    'voc_string':voc_string,
                                    'rsa_rph_target':rsa_rph_target,
                                    'rsa_rph_payout':rsa_rph_payout,
                                    'rsa_tbc_goal':rsa_tbc_goal,
                                    'rsa_tbc_achieved':rsa_tbc_achieved,
                                    'rsa_tbc_payout':rsa_tbc_payout,
                                    'rsa_tbc_string':rsa_tbc_string,
                                    'rsa_rph_payout_tier':rsa_rph_payout_tier,
                                    'gross_rev':gross_rev,
                                    'smd_rev':smd_rev,
                                    'pmd_rev':pmd_rev,
                                    'react_rev':react_rev,
                                    'net_rev':net_rev,
                                    'gross_box':gross_box,
                                    'smd_box':smd_box,
                                    'pmd_box':pmd_box,
                                    'react_box':react_box,
                                    'net_box':net_box,
                                    'noncomm_rev':noncomm_rev,
                                    'noncomm_box':noncomm_box,
                                    'store_gross_rev':store_gross_rev,
                                    'store_smd_rev':store_smd_rev_2,
                                    'store_pmd_rev':store_pmd_rev_2,
                                    'store_react_rev':store_react_rev_2,
                                    'store_net_rev':store_net_rev,
                                    'store_gross_box':store_gross_box,
                                    'store_smd_box':store_smd_box_2,
                                    'store_pmd_box':store_pmd_box_2,
                                    'store_react_box':store_react_box_2,
                                    'store_net_box':store_net_box,
                                    'store_noncomm_rev':store_noncomm_rev_2,
                                    'store_noncomm_box':store_noncomm_box_2,
                                    # 'sqr_metric_count':sqr_metric_count,
                                    # 'sqr_metric_pay':sqr_metric_pay,
                                  #  *********
                                    'vision_reward_sale_top_comp_leader_rev':vision_reward_sale_top_comp_leader_rev,
                                    'vision_reward_sale_top_comp_leader_payout':vision_reward_sale_top_comp_leader_payout,
                                    'vision_reward_ops_top_percent_store':vision_reward_ops_top_percent_store,
                                    'vision_reward_ops_top_store_pay':vision_reward_ops_top_store_pay,
                                    'vision_reward_mm_top_ops_market_rev':vision_reward_mm_top_ops_market_rev,
                                    'vision_reward_mm_top_ops_market_payout':vision_reward_mm_top_ops_market_payout,
                                    'vision_reward_dos_top_ops_rev':vision_reward_dos_top_ops_rev,
                                    'vision_reward_dos_top_ops_payout':vision_reward_dos_top_ops_payout,
                                # *****************
                                    'vision_reward_sale_top_market_rev':vision_reward_sale_top_market_rev,
                                    'vision_reward_sale_top_market_payout':vision_reward_sale_top_market_payout,
                                    'vision_reward_sale_top_company_payout':vision_reward_sale_top_company_payout,
                                    'vision_reward_sale_top_company_rev':vision_reward_sale_top_company_rev,
                                    'vision_reward_sale_top_percent_store':vision_reward_sale_top_percent_store,
                                    'vision_reward_sale_top_percent_store_pay':vision_reward_sale_top_percent_store_pay,
                                    'vision_reward_stl_top_company_rev':vision_reward_stl_top_company_rev,
                                    'vision_reward_stl_top_company_payout':vision_reward_stl_top_company_payout,
                                    'vision_reward_mm_top_market_rev':vision_reward_mm_top_market_rev,
                                    'vision_reward_mm_top_market_payout':vision_reward_mm_top_market_payout,
                                    'vision_reward_mm_top_leader_market_rev':vision_reward_mm_top_leader_market_rev,
                                    'vision_reward_mm_top_leader_market_payout':vision_reward_mm_top_leader_market_payout,
                                    'vision_reward_dos_top_region_rev':vision_reward_dos_top_region_rev,
                                    'vision_reward_dos_top_region_payout':vision_reward_dos_top_region_payout,
                                    'vision_reward_dos_top_leader_rev':vision_reward_dos_top_leader_rev,
                                    'vision_reward_dos_top_leader_payout':vision_reward_dos_top_leader_payout,
                                    'ops_leader_store_string':ops_leader_store_string,
                                    'ops_leader_market_string':ops_leader_market_string,
                                    'ops_leader_region_string':ops_leader_region_string,
                                    'rsa_top_rank_comp_string':rsa_top_rank_comp_string,
                                    'rsa_top_rank_rev_comp_string':rsa_top_rank_rev_comp_string,
                                    'store_top_comp_string':store_top_comp_string,
                                    'market_top_comp_string':market_top_comp_string,
                                    'region_top_comp_string':region_top_comp_string,
                                    'rph_import_goal':rph_import_goal,
                                    'labor_prod_target':labor_prod_target,
                                    'labor_prod_actual':labor_prod_actual,
                                    'labor_prod_achieved':labor_prod_achieved,
                                    'labor_prod_payout':labor_prod_payout,
                                    'actual_labor_budget':actual_labor_budget,
                                    'kicker_rev_goal_goals':per_worker_rev,
                                    'kicker_box_goal_goals':per_worker_box_goal,
                                    'kicker_store_rev_goal_goals':tot_store_revenue,
                                    'kicker_rev_goal_actual':actual_rev,
                                    'kicker_box_goal_actual':actual_box,
                                    'kicker_store_rev_goal_actual':actual_store_rev,
                                    'kicker_rev_goal_percent':kicker_rev_goal_percent,
                                    'kicker_box_goal_percent':kicker_box_goal_percent,
                                    'kicker_store_rev_goal_percent':kicker_store_rev_goal_percent,
                                    'kicker_rev_goal_payout':kicker_rev_goal_payout,
                                    'kicker_box_goal_payout':kicker_box_goal_payout,
                                    'kicker_store_rev_goal_payout':kicker_store_rev_goal_payout,
                                    'base_box_payout':base_box_payout,
                                    'base_box_actual':base_box_actual,
                                    'base_box_goal':base_box_goal,
                                    'base_box_hit_percent':base_box_hit_percent,
                                    'base_box_pay_tier':base_box_pay_tier,
                                    'turnover_actual_count':turnover_actual_count,
                                    'turnover_payout':turnover_payout,
                                    'rev_goal_att_goals':rev_goal_att_goals,
                                    'rev_goal_att_actual':rev_goal_att_actual,
                                    'rev_goal_att_percent':rev_goal_att_percent,
                                    'rev_goal_att_payout':rev_goal_att_payout,
                                    'tot_box_psa_goals':tot_box_psa_goals,
                                    'tot_box_psa_actual':tot_box_psa_actual,
                                    'tot_box_psa_percent':box_goal_att_market,
                                    'tot_box_psa_payout':tot_box_psa_payout,
                                    'prof_pay_store_profit':store_income,
                                    'prof_pay_payout':store_payout,
                                    'store_actual_profit':store_actual_profit,
                                    'market_prof_voc_percent':tot_market_voc,
                                    'market_prof_traffic_percent':market_conv_percent,
                                    'market_prof_labour_percent':hour_range,
                                    'market_prof_voc_payout':market_share_profit,
                                    'prepaid_goal_goals':store_prepaid_goal,
                                    'prepaid_goal_actual_count':store_pre_actual_count,
                                    'prepaid_goal_attach_percent':store_pre_actual_percent,
                                    'prepaid_goal_payout':spiff_store_pre_payout,
                                    'jump_actual_count':jump_actual_count,
                                    'jump_goals':jump_goals,
                                    'jump_attach_percent':jump_attach_percent,
                                    'jump_payout':jump_payout,
                                    'jump_comm_string':jump_comm_string,
                                    'jod_php_attach_goals':jod_php_attach_goals,
                                    'jod_php_attach_percent':jod_php_attach_percent,
                                    'jod_php_attach_payout':jod_php_attach_payout,
                                    'jod_php_attach_count':jod_php_attach_count,
                                    'jod_php_attach_string':jod_php_attach_string,
                                    'apk_actual_count':apk_actual_count,
                                    'apk_goals':spiff_per_box_acc_sold,
                                    'apk_percent':avg_apk,
                                    'apk_payout':apk_payout,
                                    'apk_comm_string':apk_comm_string,
                                    '3gb_data_unl_att_count':count_unl_att,
                                    '3gb_data_unl_att_goals':spiff_master_3gb_unl_percent,
                                    '3gb_data_unl_att_percent':spiff_3gb_unl_percent,
                                    '3gb_data_unl_att_payout':spiff_3gb_unl_payout,
                                    'spiff_3gb_unl_string':spiff_3gb_unl_string,
                                    'tot_box_conv_actual_count':spiff_stl_box_count,
                                    'tot_box_conv_goals':spiff_stl_tot_box_rule_percent,
                                    'tot_box_conv_percent':spiff_stl_tot_box_conv_percent,
                                    'tot_box_conv_payout':spiff_stl_tot_box_rule_amount,
                                    'tot_box_payout_tier':tot_box_payout_tier,
                                    'mi_1gb_count':count_sa_mi_1gb_att,
                                    'mi_1gb_goals':0.00,
                                    'mi_1gb_percent':0.00,
                                    'mi_1gb_payout':spiff_sa_mi_1gb_payout,
                                    'mi_1gb_string':mi_1gb_string,
                                    'mi_3gb_count':count_sa_mi_3gb_att,
                                    'mi_3gb_goals':0.00,
                                    'mi_3gb_percent':0.00,
                                    'mi_3gb_payout':spiff_sa_mi_3gb_payout,
                                    'mi_3gb_string':mi_3gb_string,
                                    'mi_5gb_count':count_sa_mi_5gb_att,
                                    'mi_5gb_goals':0.00,
                                    'mi_5gb_percent':0.00,
                                    'mi_5gb_payout':spiff_sa_mi_5gb_payout,
                                    'mi_5gb_string':mi_5gb_string,
                                    '3gb_data_smart_attach_count':count_3gb_smart_att,
                                    '3gb_data_smart_attach_goals':spiff_master_3gb_smart_percent,
                                    '3gb_data_smart_attach_percent':spiff_3gb_smart_percent,
                                    '3gb_data_smart_attach_payout':spiff_3gb_smart_payout,
                                    'spiff_3gb_smart_string':spiff_3gb_smart_string,
                                    'mi_conv_count':0.00,
                                    'mi_conv_goals':spiff_master_mi_conv_percent,
                                    'mi_conv_percent':spiff_mi_conv_percent,
                                    'mi_conv_payout':spiff_mi_conv_payout,
                                    'mi_conv_string':mi_conv_string,
                                    'app_goal_count':pos_count,
                                    'app_goal_goals':app_goal_master,
                                    'app_goal_percent':app_goal_percent,
                                    'app_goal_payout':app_goal_payout,
                                    'box_goal_count':box_count,
                                    'box_goal_goals':box_goal_master,
                                    'box_goal_percent':box_goal_percent,
                                    'box_goal_payout':box_goal_payout,
                                    'mi_goal_count':mi_count,
                                    'mi_goal_goals':mi_goal_master,
                                    'mi_goal_percent':mi_goal_percent,
                                    'mi_goal_payout':mi_goal_payout,
                                    'demo_field1_count':demo_field1_count,
                                    'demo_field1_goals':demo_field1_goals,
                                    'demo_field1_percent':demo_field1_percent,
                                    'demo_field1_payout':demo_field1_payout,
                                    'demo_field2_count':demo_field2_count,
                                    'demo_field2_goals':demo_field2_goals,
                                    'demo_field2_percent':demo_field2_percent,
                                    'demo_field2_payout':demo_field2_payout,
                                    'demo_field3_count':demo_field3_count,
                                    'demo_field3_goals':demo_field3_goals,
                                    'demo_field3_percent':demo_field3_percent,
                                    'demo_field3_payout':demo_field3_payout,
                                    'demo_field4_count':demo_field4_count,
                                    'demo_field4_goals':demo_field4_goals,
                                    'demo_field4_percent':demo_field4_percent,
                                    'demo_field4_payout':demo_field4_payout,
                                    'paid_comm_string':paid_comm_string,
                                    'demo_field5_count':demo_field5_count,
                                    'demo_field5_goals':demo_field5_goals,
                                    'demo_field5_percent':demo_field5_percent,
                                    'demo_field5_payout':demo_field5_payout,
                                    'demo_field6_count':demo_field6_count,
                                    'demo_field6_goals':demo_field6_goals,
                                    'demo_field6_percent':demo_field6_percent,
                                    'demo_field6_payout':demo_field6_payout,
                                    'demo_field7_count':demo_field7_count,
                                    'demo_field7_goals':demo_field7_goals,
                                    'demo_field7_percent':demo_field7_percent,
                                    'demo_field7_payout':demo_field7_payout,
                                    'demo_field8_count':demo_field8_count,
                                    'demo_field8_goals':demo_field8_goals,
                                    'demo_field8_percent':demo_field8_percent,
                                    'demo_field8_payout':demo_field8_payout,
                                    'gross_payout':gross_payout,
                                    'pre_conv_goal':pre_conv_goal,
                                    'pre_conv_percent':pre_conv_percent,
                                    'pre_conv_count':pre_conv_count,
                                    'pre_conv_payout':pre_conv_payout,
                                    'pre_conv_string':pre_conv_string,
                                    'spiff_score_count':spiff_score_count,
                                    'spiff_score_payout':spiff_score_payout,
                                    'spiff_score_string':spiff_score_string,
                                    'comm_store_id':store_id,
                                    'comm_market_id':market_id,
                                    'comm_region_id':region_id,
                                    'pre_package_comm':True,
                                    #****** April-2015 ***********
                                    'small_b2b_count':small_b2b_count,
                                    'small_b2b_payout':small_b2b_payout,
                                    'small_b2b_string':small_b2b_string
                                    })
        e = datetime.today()
        d = e - s
        print "total", d.total_seconds()
        cr.execute("select id from ir_ui_view where model='packaged.commission.tracker' and type='form' and name='packaged.commission.tracker.form'")
        view_id = map(lambda x: x[0], cr.fetchall())
        if view_id:
            view_id = view_id[0]
        else:
            view_id = False
        return {
            # 'name': _('Commission Tracker'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'packaged.commission.tracker',
            # 'views': [(compose_form.id, 'form')],
            'view_id': view_id,
            'target': 'current',
            'res_id': ids[0],
            'context': {},
        }
packaged_commission_tracker()