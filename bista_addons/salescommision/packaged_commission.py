from openerp.osv import osv,fields
import time
from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta
from openerp.osv.orm import setup_modifiers
from lxml import etree
import simplejson
import logging
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
logger = logging.getLogger('arena_log')

class packaged_commission_tracker(osv.osv):
    _name = 'packaged.commission.tracker'
    
    def _get_start_date(self, cr, uid, context=None):
        current_date = time.strftime('%Y-%m-01')
        current_date = datetime.strptime(current_date, '%Y-%m-%d')
        start_date = (current_date - relativedelta(months=1))
        start_date = start_date.date().strftime('%Y-%m-%d')
        return start_date

    def _get_end_date(self, cr, uid, context=None):
        todays_date = datetime.today()
        todays_date = (todays_date - relativedelta(months=1)).date()
        date_month = todays_date.month
        date_year = todays_date.year
        days_month = calendar.monthrange(date_year,date_month)[1]
        end_date = str('%s-%s-%s' % (int(date_year),int(date_month),int(days_month)))
        end_date = datetime.strptime(end_date, '%Y-%m-%d')        
        end_date = end_date.date().strftime('%Y-%m-%d')
        return end_date

    _columns = {
                'name':fields.many2one('hr.employee', 'Employee'),
                'dealer_code':fields.char('Dealer Code',size=64),
                'crash_job_name':fields.many2one('dsr.crash.process.deactivation', 'Job Name'),
                'emp_des':fields.many2one('hr.job', 'Employee Designation'),
                'start_date':fields.date('From Date'),
                'end_date':fields.date('End Date'),
                'comm_store_id':fields.many2one('sap.store', 'Store'),
                'comm_market_id':fields.many2one('market.place', 'Market'),
                'comm_region_id':fields.many2one('market.regions', 'Regions'),
                # 'model_id':fields.selection([('rsa', 'RSA'), ('stl', 'STL'), ('mid', 'MID'), ('rsm', 'RSM'), ('mm', 'MM'), ('dos', 'DOS')], 'Heirarchy Level'),
                'model_id':fields.selection([('rsa', 'RSA'), ('stl', 'STL'), ('mid', 'MID'), ('rsm', 'RSM'), ('mm', 'MM'), ('dos', 'DOS'), ('ca', 'CA'), ('cs', 'CS')], 'Heirarchy Level'),
                'gross_rev':fields.float('Gross Revenue'),
                'smd_rev':fields.float('SMD Revenue'),
                'pmd_rev':fields.float('PMD Revenue'),
                'noncomm_rev':fields.float('Non-Commissionable Revenue'),
                'react_rev':fields.float('React Revenue'),
                'net_rev':fields.float('Net Revenue'),
                'gross_box':fields.float('Gross Boxes'),
                'smd_box':fields.float('SMD Boxes'),
                'pmd_box':fields.float('PMD Boxes'),
                'noncomm_box':fields.float('Non-Commissionable Box'),
                'react_box':fields.float('React Boxes'),
                'net_box':fields.float('Net Boxes'),
                'store_gross_rev':fields.float('Store Gross Revenue'),
                'store_smd_rev':fields.float('Store SMD Revenue'),
                'store_pmd_rev':fields.float('Store PMD Revenue'),
                'store_noncomm_rev':fields.float('Store Non-Commissionable Revenue'),
                'store_react_rev':fields.float('Store React Revenue'),
                'store_net_rev':fields.float('Store Net Revenue'),
                'store_gross_box':fields.float('Store Gross Boxes'),
                'store_smd_box':fields.float('Store SMD Boxes'),
                'store_pmd_box':fields.float('Store PMD Boxes'),
                'store_noncomm_box':fields.float('Store Non-Commissionable Box'),
                'store_react_box':fields.float('Store React Boxes'),
                'store_net_box':fields.float('Store Net Boxes'),
                'base_tot_rev':fields.char('Base Commission Actual Revenue'),
                'base_payout':fields.float('Base Commission Payout'),
                'base_rev_string':fields.char('Base Commission Payout Tier'),
                'voc_achieved':fields.float('VOC Commission Actual Count'),
                'voc_payout':fields.float('VOC Commission Payout'),
                'voc_target':fields.float('VOC Commission Goal'),
                'voc_string':fields.char('VOC Commission Payout Tier'),
                'rsa_tbc_achieved':fields.char('TBC RSA Actual %'),
                'rsa_tbc_goal':fields.char('TBC RSA Goal'),
                'rsa_tbc_string':fields.char('TBC RSA Payout Tier'),
                'rsa_tbc_payout':fields.float('TBC RSA Payout'),
                'rsa_rph_target':fields.char('RPH RSA Actual Count'),
                'rsa_rph_payout_tier':fields.char('RPH RSA Payout Tier'),
                'rsa_rph_payout':fields.float('RPH RSA Payout'),
        #******** new        
                'labor_prod_target':fields.char('Labor Productivity(not in use)'),
                'labor_prod_actual':fields.float('Labor Productivity(not in use)'),
                'rph_import_goal':fields.float('Labor Productivity RPH Goal'),
                'labor_prod_achieved':fields.char('Labor Productivity RPH Actual Count'),
                'labor_prod_payout':fields.float('Labor Productivity Payout'),
                'actual_labor_budget':fields.float('Labor Budget %'),
        #**********            
                'base_box_payout':fields.float('Box Goal Payout'),
                'base_box_actual':fields.float('Box Goal actual count'),
                'base_box_goal':fields.float('Box Goal'),
                'base_box_hit_percent':fields.float('Box Goal Hit Percent'),
                'base_box_pay_tier':fields.char('Box Goal Payout Tier'),
                'kicker_rev_goal_goals':fields.float('Kicker Revenue Goals'),
                'kicker_rev_goal_actual':fields.float('Kicker Actual Revenue Count'),
                'kicker_rev_goal_percent':fields.float('Kicker Revenue Goal %'),
                'kicker_rev_goal_payout':fields.float('Kicker Revenue Payout'),
                'kicker_box_goal_goals':fields.float('Kicker Box Goals'),
                'kicker_box_goal_actual':fields.float('Kicker Actual Box Count'),
                'kicker_box_goal_percent':fields.float('Kicker Box Goal %'),
                'kicker_box_goal_payout':fields.float('Kicker Box Goal Payout'),
                'kicker_store_rev_goal_goals':fields.float('Kicker Store Revenue Goals'),
                'kicker_store_rev_goal_actual':fields.float('Kicker Store Actual Revenue Count'),
                'kicker_store_rev_goal_percent':fields.float('Kicker Store Revnue Goal %'),
                'kicker_store_rev_goal_payout':fields.float('Kicker Store Revenue Payout'),
                # 'kicker_sa_rev_goal_goals':fields.float('Goals'),
                # 'kicker_sa_rev_goal_actual':fields.float('Actual'),
                # 'kicker_sa_rev_goal_percent':fields.float('% to Goal to Date'),
                # 'kicker_sa_rev_goal_payout':fields.float('Payout'),
                'turnover_actual_count':fields.float('Turnover Actual Count'),
                'turnover_payout':fields.float('Turnover Payout'),
                'rev_goal_att_goals':fields.float('Revenue Attainment Goals'),
                'rev_goal_att_actual':fields.float('Revenue Attainment Actual Revenue'),
                'rev_goal_att_percent':fields.float('Revenue Attainment Goal %'),
                'rev_goal_att_payout':fields.float('Revenue Goal Attainment Payout'),
                'tot_box_psa_goals':fields.float('Total Box PSA 2014 Goals'),
                'tot_box_psa_actual':fields.float('Total Box PSA 2014 Actual Box Count'),
                'tot_box_psa_percent':fields.float('Total Box PSA 2014 Goal %'),
                'tot_box_psa_payout':fields.float('Total Box PSA 2014 Payout'),
                'prof_pay_store_profit':fields.float('Profitability Payout Actual Profit %'),
                'profit_goal_percent':fields.float('Profitability Payout(not in use)'),
                'profit_achieved_percent':fields.float('Profitability Payout(not in use)'),
                'prof_pay_payout':fields.float('Profitability Payout'),
                'store_actual_profit':fields.float('Profitability Payout(not in use)'),
                'market_prof_voc_percent':fields.float('Market Profit 2014 profit %'),
                'market_prof_voc_payout':fields.float('Market Profit 2014 Payout'),
                'market_prof_traffic_percent':fields.float('Market Profit 2014(not in use)'),
                'market_prof_traffic_payout':fields.float('Market Profit 2014(not in use)'),
                'market_prof_labour_percent':fields.float('Market Profit 2014(not in use)'),
                'market_prof_labour_payout':fields.float('Market Profit 2014(not in use)'),
                ####### payout tier for Elite and Ops Leaderboard ######
                'ops_leader_store_string':fields.char('OPS Leaderboard Top 50 Store Payout Tier'),
                'ops_leader_market_string':fields.char('OPS Leaderboard Top 5 Market Payout Tier'),
                'ops_leader_region_string':fields.char('OPS Leaderboard Top Region Payout Tier'),
                'rsa_top_rank_comp_string':fields.char('Elite Sales Leaderboard: RSA Top 100 Ranks Payout Tier'),
                'rsa_top_rank_rev_comp_string':fields.char('Elite Revnue Dollars: RSA Top 100 Revnue Payout Tier'),
                'store_top_comp_string':fields.char('Elite Top 50 Rank Store Company Payout Tier'),
                'market_top_comp_string':fields.char('Elite Top 5 Rank Market Company Payout Tier'),
                'region_top_comp_string':fields.char('Elite Top Rank Region Company Payout Tier'),
                ######## Elite Bonus Fields ##########
                'vision_reward_sale_top_comp_leader_rev':fields.integer('Elite Sales Leaderboard: Top 100 RSA Company Rank'),
                'vision_reward_sale_top_comp_leader_payout':fields.float('Elite Sales Leaderboard: Top 100 RSA Company Payout'),
                'vision_reward_sale_top_company_rev':fields.integer('Elite Revnue Dollars: RSA Top 100 Revnue Company Rank'),
                'vision_reward_sale_top_company_payout':fields.float('Elite Revnue Dollars: RSA Top 100 Revnue Company Payout'),
                'vision_reward_sale_top_percent_store':fields.integer('Elite Sales Leaderboard: Top 50 Store in Compnay Rank'),
                'vision_reward_sale_top_percent_store_pay':fields.float('Elite Sales Leaderboard: Top 50 Store in Compnay Payout'),
                'vision_reward_mm_top_leader_market_rev':fields.integer('Elite Top Market - WV Leaderboard Rank'),
                'vision_reward_mm_top_leader_market_payout':fields.float('Elite Top Market - WV Leaderboard Payout'),
                'vision_reward_dos_top_region_rev':fields.integer('Elite Top Region - WV Leaderboard Rank'),
                'vision_reward_dos_top_leader_payout':fields.float('Elite Top Region - WV Leaderboard Payout'),
                ########### OPS Leaderboard Fields
                'vision_reward_ops_top_percent_store':fields.integer('Ops Leaderboard Store Top Rank'),
                'vision_reward_ops_top_store_pay':fields.float('Ops Leaderboard Store Top Payout'),
                'vision_reward_mm_top_ops_market_rev':fields.integer('Ops Leaderboard Market Top Rank'),
                'vision_reward_mm_top_ops_market_payout':fields.float('Ops Leaderboard Market Top Payout'),
                'vision_reward_dos_top_ops_rev':fields.integer('Ops Leaderboard Region Top Rank'),
                'vision_reward_dos_top_ops_payout':fields.float('Ops Leaderboard Region Top Payout'),
                ######## 2014 Vision Reward Fields #####
                'vision_reward_sale_top_market_rev':fields.integer('Elite RSA Top Market Rank(not in use)'),
                'vision_reward_sale_top_market_payout':fields.float('Elite RSA Top Market Payout(not in use)'),
                'vision_reward_stl_top_company_rev':fields.integer('Elite Top Store in Company Revenue Rank(not in use)'),
                'vision_reward_stl_top_company_payout':fields.float('Elite Top Store in Company Revenue Payout(not in use)'),
                'vision_reward_mm_top_market_rev':fields.integer('Elite Top Market Revnue in Company Rank'),
                'vision_reward_mm_top_market_payout':fields.float('Elite Top Market Revnue in Company Payout'),
                'vision_reward_dos_top_region_payout':fields.float('Elite Top Region Revnue in Company Payout(not in use)'),
                'vision_reward_dos_top_leader_rev':fields.integer('Elite Top Region Revnue in Company Rank(not in use)'),
                # ############## Spiff Fields #################################
                'prepaid_goal_actual_count':fields.float('Prepaid Goal Actual Count'),
                'prepaid_goal_goals':fields.float('Prepaid Goal Count'),
                'prepaid_goal_attach_percent':fields.float('Prepaid Goal %'),
                'prepaid_goal_payout':fields.float('Prepaid Payout'),
                'jump_actual_count':fields.char('JUMP Actual Count'),
                'jump_goals':fields.char('JUMP Goal %'),
                'jump_attach_percent':fields.char('JUMP Attachment %'),
                'jump_payout':fields.float('JUMP Payout'),
                '3gb_data_unl_att_count':fields.char('Unlimited Actual Count'),
                '3gb_data_unl_att_goals':fields.char('Unlimited Attachment Goal'),
                '3gb_data_unl_att_percent':fields.char('Unlimited Attachment %'),
                '3gb_data_unl_att_payout':fields.float('Unlimited Attachment Payout'),
                'spiff_3gb_unl_string':fields.char('Unlimited Attachment Payout Tier'),
                '3gb_data_smart_attach_count':fields.char('5GB+ Data Actual Count'),
                '3gb_data_smart_attach_goals':fields.char('5GB+ Data Goal'),
                '3gb_data_smart_attach_percent':fields.char('5GB+ Attachment %'),
                '3gb_data_smart_attach_payout':fields.float('5GB+ Attachment Payout'),
                'spiff_3gb_smart_string':fields.char('5GB+ Payout Tier'),
                'mi_1gb_count':fields.char('MI 1GB Actual Count'),
                'mi_1gb_goals':fields.char('MI 1GB Goals'),
                'mi_1gb_percent':fields.char('MI 1GB Attachment %'),
                'mi_1gb_payout':fields.float('MI 1GB Payout'),
                'mi_1gb_string':fields.char('MI 1GB Payout Tier'),
                'mi_3gb_count':fields.char('MI 3GB Actual Count'),
                'mi_3gb_goals':fields.char('MI 3GB Goals'),
                'mi_3gb_percent':fields.char('MI 3GB Attachment %'),
                'mi_3gb_payout':fields.float('MI 3GB Payout'),
                'mi_5gb_string':fields.char('MI 5GB Payout Tier'),
                'mi_3gb_string':fields.char('MI 3GB Payout Tier'),
                'mi_5gb_count':fields.char('MI 5GB Actual Count'),
                'mi_5gb_goals':fields.char('MI 5GB Goals'),
                'mi_5gb_percent':fields.char('MI 5GB Attachment %'),
                'mi_5gb_payout':fields.float('MI 5GB Payout'),
                'apk_actual_count':fields.char('APK (not in use)'),
                'apk_goals':fields.char('APK Goals'),
                'apk_percent':fields.char('APK Actual'),
                'apk_payout':fields.float('APK Payout'),
                'paid_comm_string':fields.char('Paid Data Commission Payout Tier'),
                'apk_comm_string':fields.char('APK Payout Tier'),
                'jump_comm_string':fields.char('JUMP Payout Tier'),
                'tot_box_conv_actual_count':fields.char('TBC Actual Count'),
                'tot_box_conv_goals':fields.char('TBC Goals'),
                'tot_box_conv_percent':fields.char('TBC Conversion %'),
                'tot_box_conv_payout':fields.float('TBC Payout'),
                'tot_box_payout_tier':fields.char('TBC Payout Tier'),
                'store_prepaid_actual_count':fields.float('Actual Count'),
                'store_prepaid_goals':fields.float('Goals'),
                'store_prepaid_percent':fields.float('Attachment %'),
                'store_prepaid_payout':fields.float('Payout'),
                'mi_conv_count':fields.char('MI Conversion (not in use)'),
                'mi_conv_goals':fields.char('MI Conversion Goals'),
                'mi_conv_percent':fields.char('MI Conversion %'),
                'mi_conv_payout':fields.float('MI Conversion Payout'),
                'mi_conv_string':fields.char('MI Conversion Payout Tier'),
                'gross_payout':fields.float('Total Payout'),
                'app_goal_goals':fields.float('Application Spiff Goals'),
                'app_goal_count':fields.float('Application Spiff Actual Count'),
                'app_goal_percent':fields.float('Application Spiff Percent'),
                'app_goal_payout':fields.float('Application Goal Payout'),
                'box_goal_goals':fields.float('Box Goal Spiff Goals'),
                'box_goal_count':fields.float('Box Goal Spiff Actual Count'),
                'box_goal_percent':fields.float('Box Goal Spiff Percent'),
                'box_goal_payout':fields.float('Box Goal Spiff Payout'),
                'mi_goal_goals':fields.float('MI Spiff Goals 2014'),
                'mi_goal_count':fields.float('MI Spiff Actual Count 2014'),
                'mi_goal_percent':fields.float('MI Spiff Percent 2014'),
                'mi_goal_payout':fields.float('MI Spiff Goal Payout 2014'),
              #******  added Feb - 2015 *************
                'pre_conv_goal':fields.char('Prepaid Coversion Goals'),
                'pre_conv_percent':fields.char('Prepaid Conversion Percent'),
                'pre_conv_count':fields.char('Prepaid Conversion Actual Count'),
                'pre_conv_payout':fields.float('Prepaid Conversion Payout'),
                'pre_conv_string':fields.char('Prepaid Conversion Payout Tier'),
                'spiff_score_count':fields.char('Spiff Score Count'),
                'spiff_score_payout':fields.float('Spiff Score Payout'),
                'spiff_score_string':fields.char('Score Attachment Payout Tier'),
            #********* ends here ********
            #********* added April-2015 ********
                'small_b2b_count':fields.float('Small Business Count'),
                'small_b2b_payout':fields.float('Small Business Payout'),
                'small_b2b_string':fields.char('Small Business Payout Tier'),
            #********* ends here ***************
                'jod_php_attach_count':fields.float('PHP with JOD Actual Count'),
                'jod_php_attach_goals':fields.float('JOD PHP Attachment Goal'),
                'jod_php_attach_percent':fields.float('JOD PHP Attachment Actual %'),
                'jod_php_attach_payout':fields.float('JOD PHP Attachment Payout'),
                'jod_php_attach_string':fields.char('JOD PHP Attach Payout Tier'),
                'jod_php_conv_percent':fields.float('JOD PHP Conversion %'),
                'sqr_metric_count':fields.float('SQR Metric Actual Count'),
                'sqr_metric_pay':fields.float('SQR Metric Payout'),
                'demo_field1_goals':fields.char('Family Plan Postpaid Goals'),
                'demo_field1_count':fields.char('Family Plan Postpaid Actual Count'),
                'demo_field1_percent':fields.char('Family Plan Postpaid Percent'),
                'demo_field1_payout':fields.float('Family Plan Postpaid Payout'),
                'demo_field2_goals':fields.char('Family Plan Upgrade Goals'),
                'demo_field2_count':fields.char('Family Plan Upgrade Actual Count'),
                'demo_field2_percent':fields.char('Family Plan Upgrade Percent'),
                'demo_field2_payout':fields.float('Family Plan Upgrade Payout'),
                'demo_field3_goals':fields.float('Profitability Spiff 2014 Goals'),
                'demo_field3_count':fields.float('Profitability Spiff 2014 Actual Count'),
                'demo_field3_percent':fields.float('Profitability Spiff 2014 Percent'),
                'demo_field3_payout':fields.float('Profitability Spiff 2014 Payout'),
                'demo_field4_goals':fields.char('Paid Data Feature Goals', readonly=True),
                'demo_field4_count':fields.char('Paid Data Feature Actual Count', readonly=True),
                'demo_field4_percent':fields.char('Paid Data Feature Percent', readonly=True),
                'demo_field4_payout':fields.float('Paid Data Feature Payout', readonly=True),
                'demo_field5_goals':fields.char('Demo Field Goals', readonly=True),
                'demo_field5_count':fields.char('Demo Field Actual Count', readonly=True),
                'demo_field5_percent':fields.char('Demo Field Percent', readonly=True),
                'demo_field5_payout':fields.float('Demo Field Payout', readonly=True),
                'demo_field6_goals':fields.char('Demo Field2 Goals', readonly=True),
                'demo_field6_count':fields.char('Demo Field2 Actual Count', readonly=True),
                'demo_field6_percent':fields.char('Demo Field2 Percent', readonly=True),
                'demo_field6_payout':fields.float('Demo Field2 Payout', readonly=True),
                'demo_field7_goals':fields.char('Demo Field3 Goals', readonly=True),
                'demo_field7_count':fields.char('Demo Field3 Actual Count', readonly=True),
                'demo_field7_percent':fields.char('Demo Field3 Percent', readonly=True),
                'demo_field7_payout':fields.float('Demo Field3 Payout', readonly=True),
                'demo_field8_goals':fields.char('Demo Field4 Goals', readonly=True),
                'demo_field8_count':fields.char('Demo Field4 Actual Count', readonly=True),
                'demo_field8_percent':fields.char('Demo Field4 Percent', readonly=True),
                'demo_field8_payout':fields.float('Demo Field4 Payout', readonly=True),
                'pre_package_comm':fields.boolean('Pre Package Comm')
    }
    _defaults = {
               # 'start_date': lambda *a: time.strftime('%Y-%m-01'),
                'start_date':_get_start_date,
                'end_date':_get_end_date,
                'pre_package_comm':False
    }
    _rec_name = 'name'

    def _comm_set_base_field_view(self, cr, uid, comm_active_formula_header, groups_dict, res, doc):
        color = comm_active_formula_header[0].color
        if color == 'red':
            header_class = 'kicker_commission'
        elif color == 'green':
            header_class = 'profitability_payout'
        elif color == 'yellow':
            header_class = 'vision_rewards'
        elif color == 'blue':
            header_class = 'monthly_spiff'
        elif color == 'violet':
            header_class = 'base-box-commission'
        else:
            header_class = 'profitability_payout'

        xml_no_pref_0 = etree.Element("div")
        xml_no_pref_0.set('class', 'wireless_commission_tracker_fields '+header_class+' header')
        xml_no_pref_1 = etree.Element("separator")
        xml_no_pref_1.set('string', '%s' % comm_active_formula_header[0].name)
        xml_no_pref_1.set('class', 'wireless_commission_tracker_separator')
        xml_no_pref_2 = etree.Element("newline")
        
        groups_dict.append(xml_no_pref_0)
        xml_no_pref_0.append(xml_no_pref_1)
        groups_dict.append(xml_no_pref_2)

        count = 1

        child_div_label = {}
        newline_label = {}
        child_div_field = {}
        newline_field = {}

        sub_div_label_child_div = {}
        sub_div_label_child_label = {}
        sub_div_field_child_div = {}
        sub_div_field_child_field = {}
        
        for comm_active_formula_header_each in comm_active_formula_header[1]:
            
            child_div_label[count] = etree.Element("div")
            child_div_label[count].set('class', 'wireless_commission_tracker_fields')
            newline_label[count] = etree.Element("newline")
            child_div_field[count] = etree.Element("div")
            child_div_field[count].set('class', 'wireless_commission_tracker_fields')
            newline_field[count] = etree.Element("newline")
            
            count_sub = 1
            
            column_count = len(comm_active_formula_header_each.fields_mapped) - 1

            for comm_active_formula_header_each_field in comm_active_formula_header_each.fields_mapped:
                
                sub_div_label_child_div[count_sub] = etree.Element('div')
                if count_sub == 1:
                    sub_div_label_child_div[count_sub].set('class', 'colspan%s border-bottom-none'%column_count)
                else:
                    sub_div_label_child_div[count_sub].set('class', 'colspan%s border-bottom-none border-left-none'%column_count)
                
                if comm_active_formula_header_each_field.field_label:
                    sub_div_label_child_label[count_sub] = etree.Element('label')
                    sub_div_label_child_label[count_sub].set('string', '%s' % comm_active_formula_header_each_field.field_label)

                    sub_div_label_child_div[count_sub].append(sub_div_label_child_label[count_sub])
                
                sub_div_field_child_div[count_sub] = etree.Element('div')
                if count_sub == 1:
                    if len(comm_active_formula_header[1]) > count:
                        sub_div_field_child_div[count_sub].set('class', 'colspan%s border-bottom-none'%column_count)
                    else:
                        sub_div_field_child_div[count_sub].set('class', 'colspan%s'%column_count)
                else:
                    if len(comm_active_formula_header[1]) > count:
                        sub_div_field_child_div[count_sub].set('class', 'colspan%s border-bottom-none border-left-none'%column_count)
                    else:
                        sub_div_field_child_div[count_sub].set('class', 'colspan%s border-left-none'%column_count)
                
                if comm_active_formula_header_each_field.field_id:
                    sub_div_field_child_field[count_sub] = etree.Element('field')
                    sub_div_field_child_field[count_sub].set('name', '%s' % comm_active_formula_header_each_field.field_id.name)
#                    sub_div_field_child_field[count_sub].set('nolabel', '1')
#                    sub_div_field_child_field[count_sub].set('readonly', '1')
                    field_string = comm_active_formula_header_each_field.field_id.field_description
                    field_type = comm_active_formula_header_each_field.field_id.ttype
                    res['fields']['%s'%comm_active_formula_header_each_field.field_id.name] = {'sortable': True, 
                                                                                                'string': field_string, 
                                                                                                'searchable': True, 
                                                                                                'views': {}, 
                                                                                                'required': False, 
                                                                                                'manual': False, 
                                                                                                'readonly': True, 
                                                                                                'nolabel': True, 
                                                                                                'depends': (), 
                                                                                                'groups': False, 
                                                                                                'company_dependent': False, 
                                                                                                'type': field_type, 
                                                                                                'store': True}
                    sub_div_field_child_div[count_sub].append(sub_div_field_child_field[count_sub])

                child_div_label[count].append(sub_div_label_child_div[count_sub])
                child_div_field[count].append(sub_div_field_child_div[count_sub])

                count_sub = count_sub + 1

            groups_dict.append(child_div_label[count])
            groups_dict.append(newline_label[count])
            groups_dict.append(child_div_field[count])
            groups_dict.append(newline_field[count])
            count = count + 1
    # ********* Now appending to Notebook spiff tab **************####
        first_node = doc.xpath("//page[@string='Commissions']")
        if first_node and len(first_node) > 0:
            first_node[0].append(groups_dict)
#        result['doc'] = doc
#        result['res'] = res
        return doc

    def _spiff_set_base_field_view(self, cr, uid, comm_active_formula_header, groups_dict, res, doc):
        color = comm_active_formula_header[0].color
        if color == 'red':
            header_class = 'kicker_commission'
        elif color == 'green':
            header_class = 'profitability_payout'
        elif color == 'yellow':
            header_class = 'vision_rewards'
        elif color == 'blue':
            header_class = 'monthly_spiff'
        elif color == 'violet':
            header_class = 'base-box-commission'
        else:
            header_class = 'profitability_payout'

        xml_no_pref_0 = etree.Element("div")
        xml_no_pref_0.set('class', 'wireless_commission_tracker_fields '+header_class+' header')
        xml_no_pref_1 = etree.Element("separator")
        xml_no_pref_1.set('string', '%s' % comm_active_formula_header[0].name)
        xml_no_pref_1.set('class', 'wireless_commission_tracker_separator')
        xml_no_pref_2 = etree.Element("newline")
        
        groups_dict.append(xml_no_pref_0)
        xml_no_pref_0.append(xml_no_pref_1)
        groups_dict.append(xml_no_pref_2)

        count = 1

        child_div_label = {}
        newline_label = {}
        child_div_field = {}
        newline_field = {}

        sub_div_label_child_div = {}
        sub_div_label_child_label = {}
        sub_div_field_child_div = {}
        sub_div_field_child_field = {}
        
        for comm_active_formula_header_each in comm_active_formula_header[1]:
            
            child_div_label[count] = etree.Element("div")
            child_div_label[count].set('class', 'wireless_commission_tracker_fields')
            newline_label[count] = etree.Element("newline")
            child_div_field[count] = etree.Element("div")
            child_div_field[count].set('class', 'wireless_commission_tracker_fields')
            newline_field[count] = etree.Element("newline")
            
            count_sub = 1

            column_count = len(comm_active_formula_header_each.fields_mapped) - 1
            
            for comm_active_formula_header_each_field in comm_active_formula_header_each.fields_mapped:
                
                sub_div_label_child_div[count_sub] = etree.Element('div')
                if count_sub == 1:
                    sub_div_label_child_div[count_sub].set('class', 'colspan%s border-bottom-none'%column_count)
                else:
                    sub_div_label_child_div[count_sub].set('class', 'colspan%s border-bottom-none border-left-none'%column_count)
                
                if comm_active_formula_header_each_field.field_label:
                    sub_div_label_child_label[count_sub] = etree.Element('label')
                    sub_div_label_child_label[count_sub].set('string', '%s' % comm_active_formula_header_each_field.field_label)

                    sub_div_label_child_div[count_sub].append(sub_div_label_child_label[count_sub])
                
                sub_div_field_child_div[count_sub] = etree.Element('div')
                if count_sub == 1:
                    if len(comm_active_formula_header[1]) > count:
                        sub_div_field_child_div[count_sub].set('class', 'colspan%s border-bottom-none'%column_count)
                    else:
                        sub_div_field_child_div[count_sub].set('class', 'colspan%s'%column_count)
                else:
                    if len(comm_active_formula_header[1]) > count:
                        sub_div_field_child_div[count_sub].set('class', 'colspan%s border-bottom-none border-left-none'%column_count)
                    else:
                        sub_div_field_child_div[count_sub].set('class', 'colspan%s border-left-none'%column_count)
                
                if comm_active_formula_header_each_field.field_id:
                    sub_div_field_child_field[count_sub] = etree.Element('field')
                    sub_div_field_child_field[count_sub].set('name', '%s' % comm_active_formula_header_each_field.field_id.name)
#                    sub_div_field_child_field[count_sub].set('nolabel', '1')
#                    sub_div_field_child_field[count_sub].set('readonly', '1')
                    field_string = comm_active_formula_header_each_field.field_id.field_description
                    field_type = comm_active_formula_header_each_field.field_id.ttype
                    res['fields']['%s'%comm_active_formula_header_each_field.field_id.name] = {'sortable': True, 
                                                                                                'string': field_string, 
                                                                                                'searchable': True, 
                                                                                                'views': {}, 
                                                                                                'required': False, 
                                                                                                'manual': False, 
                                                                                                'readonly': True, 
                                                                                                'nolabel': True, 
                                                                                                'depends': (), 
                                                                                                'groups': False, 
                                                                                                'company_dependent': False, 
                                                                                                'type': field_type, 
                                                                                                'store': True}
                    sub_div_field_child_div[count_sub].append(sub_div_field_child_field[count_sub])

                child_div_label[count].append(sub_div_label_child_div[count_sub])
                child_div_field[count].append(sub_div_field_child_div[count_sub])

                count_sub = count_sub + 1

            groups_dict.append(child_div_label[count])
            groups_dict.append(newline_label[count])
            groups_dict.append(child_div_field[count])
            groups_dict.append(newline_field[count])
            count = count + 1
    # ********* Now appending to Notebook spiff tab **************####
        first_node = doc.xpath("//page[@string='Spiffs']")
        if first_node and len(first_node) > 0:
            first_node[0].append(groups_dict)
#        result['doc'] = doc
#        result['res'] = res
        return doc

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False, submenu=False):

    #####  All Formula config masters ###################    
        feature_att_obj = self.pool.get('spiff.feature.attachment')
        mi_obj = self.pool.get('spiff.mobile.internet')
        jump_att_obj = self.pool.get('spiff.jump.attachment')
        base_comm_obj = self.pool.get('comm.basic.commission.formula')
        base_box_comm_obj = self.pool.get('comm.base.box.commission.formula')
        voc_comm_obj = self.pool.get('comm.voc.commission')
        kicker_obj = self.pool.get('comm.kicker.commission.formula')
        rev_goal_att_obj = self.pool.get('comm.revenue.goal.attainment.formula')
        box_psa_goal_att_obj = self.pool.get('comm.top.box.psa.goal.attainment.formula')
        apk_obj = self.pool.get('spiff.apk')
        profit_obj = self.pool.get('comm.profitability.payout')
        rph_comm_obj = self.pool.get('comm.rph.commission')
        tbc_obj = self.pool.get('spiff.store.total.box.conversion')
        mkt_share_prof_obj = self.pool.get('comm.market.share.profitability.payout')
        elite_bonus_obj = self.pool.get('comm.vision.rewards.elite.bonus')
        pre_goal_obj = self.pool.get('spiff.prepaid.goal')
        pre_conv_obj = self.pool.get('spiff.prepaid.conversion')
        score_obj = self.pool.get('spiff.score')
        small_b2b_obj = self.pool.get('spiff.small.business')
        ops_rank_obj = self.pool.get('comm.ops.leader.ranking.master')
        turnover_obj = self.pool.get('comm.turnover.formula')
        jod_php_obj = self.pool.get('spiff.jod.php.att')
    ###### Formula config Masters End here ###########

        ir_field_obj = self.pool.get('ir.model.fields')
        hr_obj = self.pool.get('hr.employee')
        model_obj = self.pool.get('ir.model')
        comm_model_id = model_obj.search(cr, uid, [('model', '=', 'commission.tracker')])
        start_date = time.strftime('%Y-%m-01')
        end_date = time.strftime('%Y-%m-%d')
        designation_id = False
        if context is None:context = {}
        params = context.get('params',{})
        self_id = params.get('id',False)
        if not self_id:
            self_id = context.get('active_id', False)
        if self_id:
            self_data = self.browse(cr, uid, self_id, context=context)
            designation_id = self_data.emp_des.id
            start_date = self_data.start_date
            end_date = self_data.end_date
        else:
            emp_id = hr_obj.search(cr, uid, [('user_id', '=', context.get('uid') or uid)])
            if emp_id:
                designation_id = hr_obj.browse(cr, uid, emp_id[0]).job_id.id
        res = super(packaged_commission_tracker, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        
#########  Creating a list to store all active formulas with their browsed records ############
        active_formula_list = []
        feature_search_ids = feature_att_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if feature_search_ids:
            for feature_search_data in feature_att_obj.browse(cr, uid, feature_search_ids):
                active_formula_list.append(feature_search_data)
        mi_search_ids = mi_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if mi_search_ids:
            for mi_search_data in mi_obj.browse(cr, uid, mi_search_ids):
                active_formula_list.append(mi_search_data)
        jump_att_ids = jump_att_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if jump_att_ids:
            for jump_att_data in jump_att_obj.browse(cr, uid, jump_att_ids):
                active_formula_list.append(jump_att_data)
        base_comm_ids = base_comm_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if base_comm_ids:
            for base_comm_data in base_comm_obj.browse(cr, uid, base_comm_ids):
                active_formula_list.append(base_comm_data)
        base_box_comm_ids = base_box_comm_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if base_box_comm_ids:
            for base_box_comm_data in base_box_comm_obj.browse(cr, uid, base_box_comm_ids):
                active_formula_list.append(base_box_comm_data)
        voc_comm_ids = voc_comm_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if voc_comm_ids:
            for voc_comm_data in voc_comm_obj.browse(cr, uid, voc_comm_ids):
                active_formula_list.append(voc_comm_data)
        kicker_ids = kicker_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if kicker_ids:
            for kicker_data in kicker_obj.browse(cr, uid, kicker_ids):
                active_formula_list.append(kicker_data)
        rev_goal_att_ids = rev_goal_att_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if rev_goal_att_ids:
            for rev_goal_att_data in rev_goal_att_obj.browse(cr, uid, rev_goal_att_ids):
                active_formula_list.append(rev_goal_att_data)
        box_goal_psa_ids = box_psa_goal_att_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if box_goal_psa_ids:
            for box_goal_psa_data in box_psa_goal_att_obj.browse(cr, uid, box_goal_psa_ids):
                active_formula_list.append(box_goal_psa_data)
        apk_ids = apk_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if apk_ids:
            for apk_data in apk_obj.browse(cr, uid, apk_ids):
                active_formula_list.append(apk_data)
        profit_ids = profit_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if profit_ids:
            for profit_data in profit_obj.browse(cr, uid, profit_ids):
                active_formula_list.append(profit_data)
        rph_comm_ids = rph_comm_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if rph_comm_ids:
            for rph_comm_data in rph_comm_obj.browse(cr, uid, rph_comm_ids):
                active_formula_list.append(rph_comm_data)
        tbc_ids = tbc_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if tbc_ids:
            for tbc_data in tbc_obj.browse(cr, uid, tbc_ids):
                active_formula_list.append(tbc_data)
        mkt_share_prof_ids = mkt_share_prof_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if mkt_share_prof_ids:
            for mkt_share_prof_data in mkt_share_prof_obj.browse(cr, uid, mkt_share_prof_ids):
                active_formula_list.append(mkt_share_prof_data)
        elite_bonus_ids = elite_bonus_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if elite_bonus_ids:
            for elite_bonus_data in elite_bonus_obj.browse(cr, uid, elite_bonus_ids):
                active_formula_list.append(elite_bonus_data)
        ops_rank_ids = ops_rank_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if ops_rank_ids:
            for ops_rank_data in ops_rank_obj.browse(cr, uid, ops_rank_ids):
                active_formula_list.append(ops_rank_data)
        pre_goal_ids = pre_goal_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if pre_goal_ids:
            for pre_goal_data in pre_goal_obj.browse(cr, uid, pre_goal_ids):
                active_formula_list.append(pre_goal_data)
        pre_conv_ids = pre_conv_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if pre_conv_ids:
            for pre_conv_data in pre_conv_obj.browse(cr, uid, pre_conv_ids):
                active_formula_list.append(pre_conv_data)
        score_ids = score_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if score_ids:
            for score_data in score_obj.browse(cr, uid, score_ids):
                active_formula_list.append(score_data)
        small_b2b_ids = small_b2b_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if small_b2b_ids:
            for small_b2b_data in small_b2b_obj.browse(cr, uid, small_b2b_ids):
                active_formula_list.append(small_b2b_data)
        turnover_ids = turnover_obj.search(cr, uid, [('comm_designation','=',context.get('designation',designation_id)), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        if turnover_ids:
            for turnover_data in turnover_obj.browse(cr, uid, turnover_ids):
                active_formula_list.append(turnover_data)
        jod_php_ids = jod_php_obj.search(cr, uid, [('spiff_designation','=',context.get('designation',designation_id)), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if jod_php_ids:
            for jod_php_data in jod_php_obj.browse(cr, uid, jod_php_ids):
                active_formula_list.append(jod_php_data)
############# List complete with active formulas ###############

############# Segregating commission and spiff formulas in different lists ###########
        commission_active_formula = []
        spiff_active_formula = []
        for active_formula_list_each in active_formula_list:
            if active_formula_list_each.formula_type == 'comm':
                commission_active_formula.append(active_formula_list_each)
            elif active_formula_list_each.formula_type == 'spiff':
                spiff_active_formula.append(active_formula_list_each)
############## Commission and Spiff formulas list completes here ###############

############## Commission and Spiff formulas with header in [(browse_record(header),[browse_record(formula1),browse_record(formula2)]] format #######
        comm_active_formula_header = []
        spiff_active_formula_header = []
        comm_seq = []
        spiff_seq = []

        for commission_active_formula_each in commission_active_formula:
            inserted = False
            if comm_active_formula_header:
                for comm_active_formula_header_each in comm_active_formula_header:
                    if comm_active_formula_header_each[0] == commission_active_formula_each.header_name:
                        comm_active_formula_header_each[1].append(commission_active_formula_each)
                        inserted = True
                if not inserted:
                    comm_active_formula_header.append((commission_active_formula_each.header_name,[commission_active_formula_each]))
                    comm_seq.append(commission_active_formula_each.header_name.sequence)
            else:
                comm_active_formula_header.append((commission_active_formula_each.header_name,[commission_active_formula_each]))
                comm_seq.append(commission_active_formula_each.header_name.sequence)
        comm_seq.sort()
        comm_seq = list(set(comm_seq))
        for spiff_active_formula_each in spiff_active_formula:
            inserted = False
            if spiff_active_formula_header:
                for spiff_active_formula_header_each in spiff_active_formula_header:
                    if spiff_active_formula_header_each[0] == spiff_active_formula_each.header_name:
                        spiff_active_formula_header_each[1].append(spiff_active_formula_each)
                        inserted = True
                if not inserted:
                    spiff_active_formula_header.append((spiff_active_formula_each.header_name,[spiff_active_formula_each]))
                    spiff_seq.append(spiff_active_formula_each.header_name.sequence)
            else:
                spiff_active_formula_header.append((spiff_active_formula_each.header_name,[spiff_active_formula_each]))
                spiff_seq.append(spiff_active_formula_each.header_name.sequence)
        spiff_seq.sort()
        spiff_seq = list(set(spiff_seq))

########### Commission and Spiff formulas with header lists ends here ############

########### Arranging Commission and Spiff formulas with header lists in sequence defined in headers master ##########
        comm_active_formula_header_seq = []
        spiff_active_formula_header_seq = []
        for comm_seq_each in comm_seq:
            for comm_active_formula_header_each in comm_active_formula_header:
                if comm_active_formula_header_each[0].sequence == comm_seq_each:
                    comm_active_formula_header_seq.append(comm_active_formula_header_each)

        for spiff_seq_each in spiff_seq:
            for spiff_active_formula_header_each in spiff_active_formula_header:
                if spiff_active_formula_header_each[0].sequence == spiff_seq_each:
                    spiff_active_formula_header_seq.append(spiff_active_formula_header_each)
############## Arranging in header sequence ends here ##################
############## Dynamic View starts here ###################
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            groups_dict = {}
            count = 0
            invisible_group = doc.xpath("//group[@id='base_invible_field']")
            if invisible_group and len(invisible_group) > 0:
                doc.remove(invisible_group[0])

############## For Commission tab dynamic design starts here #############            
            for comm_active_formula_header_each in comm_active_formula_header_seq:
                groups_dict[count] = etree.Element("group")
                result = self._comm_set_base_field_view(cr, uid, comm_active_formula_header_each, groups_dict[count], res, doc)
                count = count + 1

############### For Spiff tab dynamic design starts here ###################
            for spiff_active_formula_header_each in spiff_active_formula_header_seq:
                groups_dict[count] = etree.Element("group")
                result = self._spiff_set_base_field_view(cr, uid, spiff_active_formula_header_each, groups_dict[count], res, doc)
                count = count + 1
            res['arch'] = etree.tostring(doc)
        return res

    def onchange_emp(self, cr, uid, ids, emp_id):
        hr_obj = self.pool.get('hr.employee')
        dealer_obj = self.pool.get('dealer.class')
        dealer_code = ''
        if emp_id:
            ######## Getting dealer code from HR one2many ##################
            dealer_ids = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',time.strftime('%Y-%m-%d')),('end_date','>=',time.strftime('%Y-%m-%d'))])
            if dealer_ids:
                dealer_code = dealer_obj.browse(cr, uid, dealer_ids[0]).name
            ################
            hr_data = hr_obj.browse(cr, uid, emp_id)
            designation_id = hr_data.job_id.id
            model_id = hr_data.job_id.model_id
            store_id = hr_data.user_id.sap_id.id
            market_id = hr_data.user_id.market_id.id
            region_id = hr_data.user_id.region_id.id
            if not market_id:
                market_id = hr_data.user_id.sap_id.market_id.id
            if not region_id:
                region_id = hr_data.user_id.sap_id.market_id.region_market_id.id
            return {'value': {'emp_des':designation_id,
                            'model_id':model_id,
                            'comm_store_id':store_id,
                            'comm_market_id':market_id,
                            'comm_region_id':region_id,
                            'dealer_code':dealer_code}}
        return {}

    def default_get(self, cr, uid, fields, context=None):
        res = super(packaged_commission_tracker, self).default_get(cr, uid, fields, context=context)
        hr_obj = self.pool.get('hr.employee')
        emp_id = hr_obj.search(cr, uid, [('user_id','=',context.get('uid') or uid)])
        if emp_id:
            res.update({'name':emp_id[0]})
            vals= self.onchange_emp(cr,uid,1,emp_id[0])
            if vals:
                res.update(vals['value'])
        return res

    def onchange_date(self, cr, uid, ids, start_date, end_date, emp_id):
        dealer_obj = self.pool.get('dealer.class')
        des_track_master = self.pool.get('designation.tracker')
        dealer_code = ''
        designation_id = False
        model_id = False
        if emp_id and start_date and end_date:
            date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
            cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_ids = map(lambda x: x[0], cr.fetchall())
            if not dealer_ids:
                dealer_ids = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            if dealer_ids:    
                for dealer_id in dealer_ids:
                    dealer_code = dealer_obj.browse(cr, uid, dealer_id).name
            cr.execute("select id from designation_tracker where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            des_track_search = map(lambda x: x[0], cr.fetchall())
            if not des_track_search:
                des_track_search = des_track_master.search(cr, uid, [('dealer_id', '=', emp_id), ('start_date', '<=', start_date), ('end_date', '>=', end_date)])
            if des_track_search:    
                for des_track_search_id in des_track_search:
                    des_data = des_track_master.browse(cr, uid, des_track_search_id)
                    designation_id = des_data.designation_id.id
                    model_id = des_data.designation_id.model_id
            return {'value': {'dealer_code':dealer_code,'emp_des':designation_id,'model_id':model_id}}
        return {'value': {'dealer_code':'','emp_des':False,'model_id':False}}

    def commission_open_transactions(self, cr, uid, ids, context=None):
        self_data = self.browse(cr, uid, ids[0])
        prm_crash_obj = self.pool.get('dsr.crash.process.deactivation')
        dealer_obj = self.pool.get('dealer.class')
        emp_id = self_data.name.id
        emp_model_id = self_data.model_id
        start_date = self_data.start_date
        end_date = self_data.end_date
        date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
        #prm_job_id = self_data.crash_job_name.id
        prm_job_id = prm_crash_obj.search(cr, uid, [('dsr_crash_start_date','=',start_date),('dsr_crash_end_date','=',end_date),('state','=','done'),('pre_prm_upload','=',False)])

        cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date desc",(emp_id,start_date,end_date))
        dealer_ids = map(lambda x: x[0], cr.fetchall())
        if not dealer_ids:
            dealer_ids = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
        if dealer_ids:
            store_data = dealer_obj.browse(cr, uid, dealer_ids[0]).store_name
            store_id = store_data.id
            market_id = store_data.market_id.id
            region_id = store_data.market_id.region_market_id.id
        else:
            store_id = False
            market_id = False
            region_id = False

        if emp_model_id == 'dos' and region_id:
            condition = ['|','&',('dsr_region_id','=',region_id),'&',('state','=','done'),'&',('dsr_date','>=',start_date),('dsr_date','<=',end_date),'&',('crash_prm_job_id_rollback','in',prm_job_id),'&',('dsr_region_id','=',region_id),'&',('state','=','done'),'|',('prm_dsr_pmd','=',True),('noncommissionable','=',True)]
        elif emp_model_id == 'mm' and market_id:
            condition = ['|','&',('dsr_market_id','=',market_id),'&',('state','=','done'),'&',('dsr_date','>=',start_date),('dsr_date','<=',end_date),'&',('crash_prm_job_id_rollback','in',prm_job_id),'&',('dsr_market_id','=',market_id),'&',('state','=','done'),'|',('prm_dsr_pmd','=',True),('noncommissionable','=',True)]
        elif ((emp_model_id == 'mid') or (emp_model_id == 'rsm') or (emp_model_id == 'stl')) and store_id:
            condition = ['|','&',('dsr_store_id','=',store_id),'&',('state','=','done'),'&',('dsr_date','>=',start_date),('dsr_date','<=',end_date),'&',('crash_prm_job_id_rollback','in',prm_job_id),'&',('dsr_store_id','=',store_id),'&',('state','=','done'),'|',('prm_dsr_pmd','=',True),('noncommissionable','=',True)]
        else:
            condition = ['|','&',('sales_employee_id','=',emp_id),'&',('state','=','done'),'&',('dsr_date','>=',start_date),('dsr_date','<=',end_date),'&',('crash_prm_job_id_rollback','in',prm_job_id),'&',('sales_employee_id','=',emp_id),'&',('state','=','done'),'|',('prm_dsr_pmd','=',True),('noncommissionable','=',True)]
        ctx = dict(context)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wireless.transactions.report',
            'view_id': False,
            'domain':condition,
            'context': ctx,
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
        cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        res_id = super(packaged_commission_tracker, self).create(cr, uid, vals, context=context)
        self.write(cr, uid, [res_id], {'record_id':res_id})
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        start_date = self.browse(cr, uid, ids[0]).start_date
        end_date = self.browse(cr, uid, ids[0]).end_date
        if 'start_date' in vals:
            start_date = vals['start_date']
        if 'end_date' in vals:
            end_date = vals['end_date']
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
        res_id = super(packaged_commission_tracker, self).write(cr, uid, ids, vals, context=context)
        return res_id

    def view_commission(self, cr, uid, ids, coontext=None):
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

    def _get_dsr_exclude_condition(self,var_name,business_rule,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        dsr_condition = str(' and ')
        if not master_br_dict.has_key('%s'%(business_rule)):
            if master_br_emp_type:
                if len(master_br_emp_type) > 1:
                    dsr_condition += '('+var_name+str('.dsr_emp_type not in %s or '%(tuple(master_br_emp_type),))+var_name+'.dsr_emp_type is null) and '
                else:
                    dsr_condition += '('+var_name+'.dsr_emp_type != %s or '%master_br_emp_type[0]+var_name+'.dsr_emp_type is null) and '
            if master_br_cc:
                if len(master_br_cc) > 1:
                    dsr_condition += '('+var_name+str('.dsr_credit_class not in %s or '%(tuple(master_br_cc),))+var_name+'.dsr_credit_class is null) and '
                else:
                    dsr_condition += '('+var_name+'.dsr_credit_class != %s or '%master_br_cc[0]+var_name+'.dsr_credit_class is null) and '
            if master_br_prod_code:
                if len(master_br_prod_code) > 1:
                    dsr_condition += '('+var_name+str('.dsr_product_code_type not in %s or '%(tuple(master_br_prod_code),))+var_name+'.dsr_product_code_type is null) and '
                else:
                    dsr_condition += '('+var_name+'.dsr_product_code_type != %s or '%master_br_prod_code[0]+var_name+'.dsr_product_code_type is null) and '
            if master_br_soc:
                if len(master_br_prod_code) > 1:
                    dsr_condition += '('+var_name+str('.dsr_product_code not in %s or '%(tuple(master_br_soc),))+var_name+'.dsr_product_code is null) and '
                else:
                    dsr_condition += '('+var_name+'.dsr_product_code != %s or '%master_br_soc[0]+var_name+'.dsr_product_code is null) and '
        dsr_condition = dsr_condition[:-4]
        return dsr_condition

    def _base_comm_payout(self, cr, uid, emp_des, start_date, end_date, tot_rev):
        comm_obj = self.pool.get('comm.basic.commission.formula')
        comm_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        payout = 0.00
        if comm_search_ids:
            comm_rev_percent = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_percent
            comm_rev_fix = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_flat_amount
            if comm_rev_percent:
                payout = (tot_rev * comm_rev_percent) / 100
            elif comm_rev_fix:
                payout = comm_rev_fix
        return payout

    def _base_box_payout(self, cr, uid, emp_des, start_date, end_date, tot_rev):
        comm_obj = self.pool.get('comm.base.box.commission.formula')
        comm_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        payout = 0.00
        if comm_search_ids:
            comm_rev_percent = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_percent
            comm_rev_fix = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_flat_amount
            if comm_rev_percent:
                payout = (tot_rev * comm_rev_percent) / 100
            elif comm_rev_fix:
                payout = comm_rev_fix
        return payout

    def _kicker_rev_goal_payout(self, cr, uid, emp_des, start_date, end_date, tot_rev):
        comm_obj = self.pool.get('comm.kicker.commission.formula')
        comm_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        payout = 0.00
        if comm_search_ids:
            comm_rev_percent = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_rev_goal_percent
            comm_rev_fix = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_rev_goal_amount
            if comm_rev_percent:
                payout = (tot_rev * comm_rev_percent) / 100
            elif comm_rev_fix:
                payout = comm_rev_fix
        return payout

    def _kicker_box_goal_payout(self, cr, uid, emp_des, start_date, end_date, tot_rev):
        comm_obj = self.pool.get('comm.kicker.commission.formula')
        comm_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        payout = 0.00
        if comm_search_ids:
            comm_rev_percent = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_box_goal_percent
            comm_rev_fix = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_box_goal_amount
            if comm_rev_percent:
                payout = (tot_rev * comm_rev_percent) / 100
            elif comm_rev_fix:
                payout = comm_rev_fix
        return payout

    def _kicker_store_rev_goal_payout(self, cr, uid, emp_des, start_date, end_date, tot_rev):
        comm_obj = self.pool.get('comm.kicker.commission.formula')
        comm_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
        payout = 0.00
        if comm_search_ids:
            comm_rev_percent = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_store_rev_goal_percent
            comm_rev_fix = comm_obj.browse(cr, uid, comm_search_ids[0]).comm_store_rev_goal_amount
            if comm_rev_percent:
                payout = (tot_rev * comm_rev_percent) / 100
            elif comm_rev_fix:
                payout = comm_rev_fix
        return payout

    def _calculate_mi_gb(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_3gb_ids, prm_job_id, tot_rev, spiff_no_of_exit, emp_model_id, traffic_stores, traffic_dates,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}
        hr_obj = self.pool.get('hr.employee')
        store_obj = self.pool.get('sap.store')
        dealer_obj = self.pool.get('dealer.class')
        split_goal_obj = self.pool.get('spliting.goals')
        date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
        vals['spiff_mi_gb_count'] = str("") #-- actual count
        vals['spiff_sa_mi_3gb_amount'] = 0.00 #---total payout
        vals['spiff_mi_conv_percent'] = str("") #--- Conversion percent
        vals['spiff_master_mi_conv_percent'] = str("")  #-- master conversion
        vals['mi_1gb_string'] = str("")
        spiff_sa_mi_obj = self.pool.get('spiff.mobile.internet')
        sa_mi_count_payout = 0.00
        spiff_mi_conv_percent = 0.00
        if field_name == 'employee_id':
            field_name = 'store_id'
            field_name_2 = 'employee_id'
            store_data = hr_obj.browse(cr, uid, emp_id).user_id.sap_id
            store_id = store_data.id
            split_search_ids = split_goal_obj.search(cr, uid, [('employee_id','=',emp_id),('start_date','=',start_date),('end_date','=',end_date)])
            if split_search_ids:
                store_data = split_goal_obj.browse(cr, uid, split_search_ids[0]).store_id
                store_id = store_data.id
            cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            for dealer_obj_search_multi_id in dealer_obj_search_multi:
                store_data = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id).store_name
                store_id = store_data.id
            store_emp_search = store_obj.search(cr, uid, [('store_mgr_id','=',emp_id)])
            if store_emp_search:
                store_data = store_obj.browse(cr, uid, store_emp_search[0])
                store_id = store_data.id
        else:
            field_name_2 = field_name
            store_id = emp_id
        spiff_sa_mi_3gb_data = spiff_sa_mi_obj.browse(cr, uid, spiff_sa_mi_3gb_ids[0])
        spiff_business_class = spiff_sa_mi_3gb_data.spiff_business_class
        if len(traffic_stores) == 1:
            mi_new_store_cond = str(" and df.store_id = '%s' "%(traffic_stores[0]))
        elif traffic_stores:
            mi_new_store_cond = str(" and df.store_id in %s "%(tuple(traffic_stores),))
        else:
            mi_new_store_cond = str('')
        if len(traffic_dates) == 1:
            mi_new_date_cond = str(" and df.dsr_act_date = '%s' "%(traffic_dates[0]))
        elif traffic_dates:
            mi_new_date_cond = str(" and df.dsr_act_date in %s "%(tuple(traffic_dates),))
        else:
            mi_new_date_cond = str('')
        var_name = str('df')
        for spiff_business_class_data in spiff_business_class:
            sa_mi_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_per_att = spiff_business_class_data.pay_per_att
            if sa_mi_3gb_business_rule_id:
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,sa_mi_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                sa_mi_business_rule_pos = sa_mi_3gb_business_rule_id.is_postpaid
                sa_mi_business_rule_upg = sa_mi_3gb_business_rule_id.is_upgrade
                sa_mi_business_rule_pre = sa_mi_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if sa_mi_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if sa_mi_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if sa_mi_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in sa_mi_3gb_business_rule_id.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                if from_condition != '':
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''') 
            as df where df.'''+field_name+''' = %s'''+mi_new_store_cond+'''
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            '''+mi_new_date_cond+'''
            and df.prm_dsr_smd = false
            and df.state = 'done'
            '''+condition_string+
    dsr_exclude_condition+''' ''', (store_id, start_date, end_date,start_date,end_date))
                    mi_1gb_data = cr.fetchall()
                    count_sa_mi_1gb_att = mi_1gb_data[0][0]
                    if not count_sa_mi_1gb_att:
                        count_sa_mi_1gb_att = 0.00
                else:
                    count_sa_mi_1gb_att = 0.00
                sa_mi_count_payout = count_sa_mi_1gb_att
                if spiff_no_of_exit > 0.00:
                    spiff_mi_conv_percent = (float(count_sa_mi_1gb_att) * 100) / float(spiff_no_of_exit)
                spiff_mi_conv_percent = round(spiff_mi_conv_percent, 2)
            pay_sa_mi_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_sa_mi_3gb_business_rule_id:
                sa_mi_business_rule_pos = pay_sa_mi_3gb_business_rule_id.is_postpaid
                sa_mi_business_rule_upg = pay_sa_mi_3gb_business_rule_id.is_upgrade
                sa_mi_business_rule_pre = pay_sa_mi_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_sa_mi_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                if sa_mi_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if sa_mi_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if sa_mi_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in pay_sa_mi_3gb_business_rule_id.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                if from_condition != '':
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''') 
            as df where df.'''+field_name_2+''' = %s'''+mi_new_store_cond+'''
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            '''+mi_new_date_cond+'''
            and df.prm_dsr_smd = false
            and df.state = 'done'
            '''+condition_string+
    dsr_exclude_condition+''' ''', (emp_id, start_date, end_date,start_date,end_date))
                    mi_1gb_data = cr.fetchall()
                    count_sa_mi_1gb_att = mi_1gb_data[0][0]
                    if not count_sa_mi_1gb_att:
                        count_sa_mi_1gb_att = 0.00
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''') 
            as df where df.'''+field_name_2+''' = %s'''
            +mi_new_store_cond+'''
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and df.state = 'done'
            '''+condition_string+''' ''', (emp_id, tuple(prm_job_id)))
                    mi_1gb_deact_data = cr.fetchall()
                    count_sa_mi_deact = mi_1gb_deact_data[0][0]
                    if not count_sa_mi_deact:
                        count_sa_mi_deact = 0.00
                else:
                    count_sa_mi_1gb_att = 0.00
                    count_sa_mi_deact = 0.00
                sa_mi_count_payout = count_sa_mi_1gb_att - count_sa_mi_deact
            if sa_mi_3gb_business_rule_id:
                if to_condition_percent != 0:
                    if spiff_mi_conv_percent >= att_condition_percent and spiff_mi_conv_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
                else:
                    if spiff_mi_conv_percent >= att_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
            else:
                if pay_per_att > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                elif pay_on_rev > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                elif flat_pay > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
            att_condition_percent = round(att_condition_percent, 2)
            sa_mi_count_payout = round(sa_mi_count_payout, 2)
            spiff_mi_conv_percent = round(spiff_mi_conv_percent, 2)
            vals['spiff_mi_conv_percent'] += ("%s, "%(spiff_mi_conv_percent,))
            vals['spiff_master_mi_conv_percent'] += str("%s, "%(att_condition_percent,))
            vals['spiff_mi_gb_count'] += str("%s, "%(sa_mi_count_payout,))
        if pay_per_att > 0.00:
            vals['mi_1gb_string'] += ("$ %s per"%(pay_per_att))
        elif flat_pay:
            vals['mi_1gb_string'] += ("$ %s"%(flat_pay))
        elif pay_on_rev:
            vals['mi_1gb_string'] += ("%s"%(pay_on_rev))
            vals['mi_1gb_string'] += (" %")
            if emp_model_id == 'rsa':
                vals['mi_1gb_string'] += (" of RSA Revenue")
            elif emp_model_id == 'stl':
                vals['mi_1gb_string'] += (" of STL Revenue")
            elif emp_model_id == 'mid':
                vals['mi_1gb_string'] += (" of MID Revenue")
            elif emp_model_id == 'rsm':
                vals['mi_1gb_string'] += (" of RSM Revenue")
            elif emp_model_id == 'mm':
                vals['mi_1gb_string'] += (" of MM Revenue")
            elif emp_model_id == 'dos':
                vals['mi_1gb_string'] += (" of DOS Revenue")
        if vals['spiff_mi_gb_count'] != "":
            vals['spiff_mi_gb_count'] = vals['spiff_mi_gb_count'][:-2]
        if vals['spiff_master_mi_conv_percent'] != "":
            vals['spiff_master_mi_conv_percent'] = vals['spiff_master_mi_conv_percent'][:-2]
        if vals['spiff_mi_conv_percent'] != "":
            vals['spiff_mi_conv_percent'] = vals['spiff_mi_conv_percent'][:-2]
        return vals

    def _calculate_pre_conv(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_3gb_ids, prm_job_id, tot_rev, spiff_no_of_exit, emp_model_id, traffic_stores, traffic_dates,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}
        hr_obj = self.pool.get('hr.employee')
        store_obj = self.pool.get('sap.store')
        dealer_obj = self.pool.get('dealer.class')
        split_goal_obj = self.pool.get('spliting.goals')
        date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
        vals['spiff_mi_gb_count'] = str("") #-- actual count
        vals['spiff_sa_mi_3gb_amount'] = 0.00 #---total payout
        vals['spiff_mi_conv_percent'] = str("") #--- Conversion percent
        vals['spiff_master_mi_conv_percent'] = str("")  #-- master conversion
        vals['pre_conv_string'] = str("")
        spiff_sa_mi_obj = self.pool.get('spiff.prepaid.conversion')
        sa_mi_count_payout = 0.00
        spiff_mi_conv_percent = 0.00
        if field_name == 'employee_id':
            field_name = 'store_id'
            field_name_2 = 'employee_id'
            store_data = hr_obj.browse(cr, uid, emp_id).user_id.sap_id
            store_id = store_data.id
            split_search_ids = split_goal_obj.search(cr, uid, [('employee_id','=',emp_id),('start_date','=',start_date),('end_date','=',end_date)])
            if split_search_ids:
                store_data = split_goal_obj.browse(cr, uid, split_search_ids[0]).store_id
                store_id = store_data.id
            cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            for dealer_obj_search_multi_id in dealer_obj_search_multi:
                store_data = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id).store_name
                store_id = store_data.id
            store_emp_search = store_obj.search(cr, uid, [('store_mgr_id','=',emp_id)])
            if store_emp_search:
                store_data = store_obj.browse(cr, uid, store_emp_search[0])
                store_id = store_data.id
        else:
            field_name_2 = field_name
            store_id = emp_id
        spiff_sa_mi_3gb_data = spiff_sa_mi_obj.browse(cr, uid, spiff_sa_mi_3gb_ids[0])
        spiff_business_class = spiff_sa_mi_3gb_data.prepaid_business_class
        if len(traffic_stores) == 1:
            pre_new_store_cond = str(" and df.store_id = '%s' "%(traffic_stores[0]))
        elif traffic_stores:
            pre_new_store_cond = str(" and df.store_id in %s "%(tuple(traffic_stores),))
        else:
            pre_new_store_cond = str('')
        if len(traffic_dates) == 1:
            pre_new_date_cond = str(" and df.dsr_act_date = '%s' "%(traffic_dates[0]))
        elif traffic_dates:
            pre_new_date_cond = str(" and df.dsr_act_date in %s "%(tuple(traffic_dates),))
        else:
            pre_new_date_cond = str('')
        var_name = str('df')
        for spiff_business_class_data in spiff_business_class:
            sa_mi_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_per_att = spiff_business_class_data.pay_per_att
            if sa_mi_3gb_business_rule_id:
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,sa_mi_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                sa_mi_business_rule_pos = sa_mi_3gb_business_rule_id.is_postpaid
                sa_mi_business_rule_upg = sa_mi_3gb_business_rule_id.is_upgrade
                sa_mi_business_rule_pre = sa_mi_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if sa_mi_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if sa_mi_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if sa_mi_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in sa_mi_3gb_business_rule_id.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                if from_condition != '':
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''') 
            as df where df.'''+field_name+''' = %s'''+pre_new_store_cond+'''
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            '''+pre_new_date_cond+'''
            and df.prm_dsr_smd = false
            and df.state = 'done'
            '''+condition_string+
    dsr_exclude_condition+''' ''', (store_id, start_date, end_date,start_date,end_date))
                    mi_1gb_data = cr.fetchall()
                    count_sa_mi_1gb_att = mi_1gb_data[0][0]
                    if not count_sa_mi_1gb_att:
                        count_sa_mi_1gb_att = 0.00
                else:
                    count_sa_mi_1gb_att = 0.00
                sa_mi_count_payout = count_sa_mi_1gb_att
                if spiff_no_of_exit > 0.00:
                    spiff_mi_conv_percent = (float(count_sa_mi_1gb_att) * 100) / float(spiff_no_of_exit)
                spiff_mi_conv_percent = round(spiff_mi_conv_percent, 2)
            pay_sa_mi_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_sa_mi_3gb_business_rule_id:
                sa_mi_business_rule_pos = pay_sa_mi_3gb_business_rule_id.is_postpaid
                sa_mi_business_rule_upg = pay_sa_mi_3gb_business_rule_id.is_upgrade
                sa_mi_business_rule_pre = pay_sa_mi_3gb_business_rule_id.is_prepaid
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_sa_mi_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                from_condition = str('')
                if sa_mi_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if sa_mi_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if sa_mi_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in pay_sa_mi_3gb_business_rule_id.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                if from_condition != '':
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''') 
            as df where df.'''+field_name_2+''' = %s'''+pre_new_store_cond+'''
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            '''+pre_new_date_cond+'''
            and df.prm_dsr_smd = false
            and df.state = 'done'
            '''+condition_string+
    dsr_exclude_condition+''' ''', (emp_id, start_date, end_date,start_date,end_date))
                    mi_1gb_data = cr.fetchall()
                    count_sa_mi_1gb_att = mi_1gb_data[0][0]
                    if not count_sa_mi_1gb_att:
                        count_sa_mi_1gb_att = 0.00
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''') 
            as df where df.'''+field_name_2+''' = %s'''
            +pre_new_store_cond+'''
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and df.state = 'done'
            '''+condition_string+''' ''', (emp_id, tuple(prm_job_id)))
                    mi_1gb_deact_data = cr.fetchall()
                    count_sa_mi_deact = mi_1gb_deact_data[0][0]
                    if not count_sa_mi_deact:
                        count_sa_mi_deact = 0.00
                else:
                    count_sa_mi_1gb_att = 0.00
                    count_sa_mi_deact = 0.00
                sa_mi_count_payout = count_sa_mi_1gb_att - count_sa_mi_deact
            if sa_mi_3gb_business_rule_id:
                if to_condition_percent != 0:
                    if spiff_mi_conv_percent >= att_condition_percent and spiff_mi_conv_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
                else:
                    if spiff_mi_conv_percent >= att_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
            else:
                if pay_per_att > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                elif pay_on_rev > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                elif flat_pay > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
            att_condition_percent = round(att_condition_percent, 2)
            sa_mi_count_payout = round(sa_mi_count_payout, 2)
            spiff_mi_conv_percent = round(spiff_mi_conv_percent, 2)
            vals['spiff_mi_conv_percent'] += ("%s, "%(spiff_mi_conv_percent,))
            vals['spiff_master_mi_conv_percent'] += str("%s, "%(att_condition_percent,))
            vals['spiff_mi_gb_count'] += str("%s, "%(sa_mi_count_payout,))
        if pay_per_att > 0.00:
            if emp_model_id == 'rsa':
                vals['pre_conv_string'] += ("$ %s per sold by RSA"%(pay_per_att))
            elif emp_model_id == 'stl':
                vals['pre_conv_string'] += ("$ %s per sold by STL"%(pay_per_att))
            elif emp_model_id == 'mid':
                vals['pre_conv_string'] += ("$ %s per sold by MID"%(pay_per_att))
            elif emp_model_id == 'rsm':
                vals['pre_conv_string'] += ("$ %s per sold by RSM"%(pay_per_att))
            elif emp_model_id == 'mm':
                vals['pre_conv_string'] += ("$ %s per sold by MM"%(pay_per_att))
            elif emp_model_id == 'dos':
                vals['pre_conv_string'] += ("$ %s per sold by DOS"%(pay_per_att))
        elif flat_pay:
            vals['pre_conv_string'] += ("$ %s"%(flat_pay))
        elif pay_on_rev:
            vals['pre_conv_string'] += ("%s"%(pay_on_rev))
            vals['pre_conv_string'] += (" %")
            if emp_model_id == 'rsa':
                vals['pre_conv_string'] += (" of RSA Revenue")
            elif emp_model_id == 'stl':
                vals['pre_conv_string'] += (" of STL Revenue")
            elif emp_model_id == 'mid':
                vals['pre_conv_string'] += (" of MID Revenue")
            elif emp_model_id == 'rsm':
                vals['pre_conv_string'] += (" of RSM Revenue")
            elif emp_model_id == 'mm':
                vals['pre_conv_string'] += (" of MM Revenue")
            elif emp_model_id == 'dos':
                vals['pre_conv_string'] += (" of DOS Revenue")
        if vals['spiff_mi_gb_count'] != "":
            vals['spiff_mi_gb_count'] = vals['spiff_mi_gb_count'][:-2]
        if vals['spiff_master_mi_conv_percent'] != "":
            vals['spiff_master_mi_conv_percent'] = vals['spiff_master_mi_conv_percent'][:-2]
        if vals['spiff_mi_conv_percent'] != "":
            vals['spiff_mi_conv_percent'] = vals['spiff_mi_conv_percent'][:-2]
        return vals

    def _calculate_score_attachment(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_score_master_ids, prm_job_id, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}
        vals['spiff_score_count'] = str("")
        vals['spiff_score_payout'] = 0.00
        vals['spiff_score_string'] = str("")
        spiff_score_count = 0.00
        spiff_score_payout = 0.00
        spiff_score_master = self.pool.get('spiff.score')
        spiff_score_data = spiff_score_master.browse(cr, uid, spiff_score_master_ids[0])
        spiff_business_class = spiff_score_data.spiff_business_class
        spiff_3gb_smart_percent = 0.00
        count_3gb_smart_att = 0.00
        var_name = str('df')
        for spiff_business_class_data in spiff_business_class:
            plus_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            if plus_3gb_business_rule_id:
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                plus_3gb_business_rule_pos = plus_3gb_business_rule_id.is_postpaid
                plus_3gb_business_rule_upg = plus_3gb_business_rule_id.is_upgrade
                plus_3gb_business_rule_pre = plus_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if plus_3gb_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if plus_3gb_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if plus_3gb_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                from_num_cond = str('')
                if plus_3gb_business_rule_pos or plus_3gb_business_rule_upg:
                    from_num_cond += str('select id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,postpaid_id,upgrade_id,true as created_feature,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_feature_line union all ')
                if plus_3gb_business_rule_pre:
                    from_num_cond += str('select id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,null as postpaid_id,null as upgrade_id,created_feature,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_num_cond = from_num_cond[:-10]
                ##################### Condition string numerator ##################
                spiff_rule_tuple = []
                actual_count_product_type = []
                for sub_rule in plus_3gb_business_rule_id.sub_rules:
                    actual_count_product_type.append(sub_rule.product_code_type.id)
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if not actual_count_product_type:
                    actual_count_product_type = [0]
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                ############### condition string denominator ##########################
                spiff_rule_tuple = []
                for sub_rule in plus_3gb_business_rule_id.sub_rules_2:
                    if sub_rule.tac_code_rel_sub_inc_2:
                        for phone_type in sub_rule.tac_code_rel_sub_inc_2:
                            spiff_rule_tuple.append((sub_rule.product_code_type_2.id,phone_type.id,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type_2.id,False,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
                if spiff_rule_tuple:
                    condition_string_2 = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string_2 += str("(")
                        if spiff_rule_data[0]:
                            condition_string_2 += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string_2 += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string_2 += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string_2 += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string_2 += ") OR "
                    condition_string_2 = condition_string_2[:-4]
                    condition_string_2 += str(")")
                else:
                    condition_string_2 = ''
                ############# denominator ######################
                cr.execute('''select count(df.id) as count
                from ('''+from_condition+''') 
                as df where df.'''+field_name+''' = %s 
                and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                and df.state = 'done'
                and df.prm_dsr_smd = false
                '''+condition_string_2+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))#shashank            
                tot_sto_pos_upg_box = cr.fetchall()
                count_all_elig_pos = tot_sto_pos_upg_box[0][0]
                if not count_all_elig_pos:
                    count_all_elig_pos = 0.00
                ###### numerator to be considered in percent logic only ####################
                cr.execute('''select count(df.id)
                    from ('''+from_num_cond+''')
                    as df where df.'''+field_name+''' = %s 
                    and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                    and df.state = 'done'
                    and df.prm_dsr_smd = false
                    and (df.postpaid_id is not null or df.upgrade_id is not null or df.created_feature=true)
                    '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
                    from ('''+from_num_cond+''')
                    as df where df.'''+field_name+''' = %s 
                    and df.crash_prm_job_id_rollback in %s
                    and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                    and df.state = 'done'
                    and df.dsr_product_code_type in %s'''+
    dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                if count_all_elig_pos > 0.00:    
                    spiff_3gb_smart_percent = (float(count_3gb_percent_logic) * 100) / float(count_all_elig_pos)
                spiff_3gb_smart_percent = round(spiff_3gb_smart_percent, 2)
                count_3gb_smart_att = count_3gb_percent_logic - count_3gb_actual_percent_logic
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            pay_per_att = spiff_business_class_data.pay_per_att
      # ************ smart attachment count as per payment business rule attached ***************** #      
            pay_plus_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_plus_3gb_business_rule_id and (plus_3gb_business_rule_id.id != pay_plus_3gb_business_rule_id.id):
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_rule_tuple = []
                actual_count_product_type = []
                plus_3gb_business_rule_pos = pay_plus_3gb_business_rule_id.is_postpaid
                plus_3gb_business_rule_upg = pay_plus_3gb_business_rule_id.is_upgrade
                plus_3gb_business_rule_pre = pay_plus_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if plus_3gb_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if plus_3gb_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if plus_3gb_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                from_num_cond = str('')
                if plus_3gb_business_rule_pos or plus_3gb_business_rule_upg:
                    from_num_cond += str('select id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,postpaid_id,upgrade_id,true as created_feature,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_feature_line union all ')
                if plus_3gb_business_rule_pre:
                    from_num_cond += str('select id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,null as postpaid_id,null as upgrade_id,created_feature,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_num_cond = from_num_cond[:-10]
                for sub_rule in pay_plus_3gb_business_rule_id.sub_rules:
                    actual_count_product_type.append(sub_rule.product_code_type.id)
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if not actual_count_product_type:
                    actual_count_product_type = [0]
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                cr.execute('''select count(df.id)
                    from ('''+from_num_cond+''')
                    as df where df.'''+field_name+''' = %s 
                    and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                    and df.state = 'done'
                    and df.prm_dsr_smd = false
                    and (df.postpaid_id is not null or df.upgrade_id is not null or df.created_feature=true)
                    '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
                    from ('''+from_num_cond+''')
                    as df where df.'''+field_name+''' = %s 
                    and df.crash_prm_job_id_rollback in %s
                    and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                    and df.state = 'done'
                    and df.dsr_product_code_type in %s''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                count_3gb_smart_att = count_3gb_percent_logic - count_3gb_actual_percent_logic
            if att_condition_percent > 0.00:
                if to_condition_percent != 0:
                    if spiff_3gb_smart_percent >= att_condition_percent and spiff_3gb_smart_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + (count_3gb_smart_att * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + flat_pay
                else:
                    if spiff_3gb_smart_percent >= att_condition_percent:  
                        if pay_per_att > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + (count_3gb_smart_att * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + flat_pay
            else:
                if pay_per_att > 0.00:
                    vals['spiff_score_payout'] = vals['spiff_score_payout'] + (count_3gb_smart_att * pay_per_att)
                elif pay_on_rev > 0.00:
                    vals['spiff_score_payout'] = vals['spiff_score_payout'] + ((tot_rev * pay_on_rev)/100)
                elif flat_pay > 0.00:
                    vals['spiff_score_payout'] = vals['spiff_score_payout'] + flat_pay
            spiff_score_count = round(count_3gb_smart_att,2)
            vals['spiff_score_count'] += str("%s, "%(spiff_score_count,))   
        if pay_per_att > 0.00:
            vals['spiff_score_string'] += ("$ %s per"%(pay_per_att))
        elif flat_pay:
            vals['spiff_score_string'] += ("$ %s"%(flat_pay))
        elif pay_on_rev:
            vals['spiff_score_string'] += ("%s"%(pay_on_rev))
            vals['spiff_score_string'] += (" %")
            if emp_model_id == 'rsa':
                vals['spiff_score_string'] += (" of RSA Revenue")
            elif emp_model_id == 'stl':
                vals['spiff_score_string'] += (" of STL Revenue")
            elif emp_model_id == 'mid':
                vals['spiff_score_string'] += (" of MID Revenue")
            elif emp_model_id == 'rsm':
                vals['spiff_score_string'] += (" of RSM Revenue")
            elif emp_model_id == 'mm':
                vals['spiff_score_string'] += (" of MM Revenue")
            elif emp_model_id == 'dos':
                vals['spiff_score_string'] += (" of DOS Revenue")
        if vals['spiff_score_count'] != "":
            vals['spiff_score_count'] = vals['spiff_score_count'][:-2]
        return vals

    def _calculate_small_b2b(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_score_master_ids, prm_job_id, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}
        vals['spiff_score_count'] = str("")
        vals['spiff_score_payout'] = 0.00
        vals['spiff_score_string'] = str("")
        spiff_score_count = 0.00
        spiff_score_payout = 0.00
        spiff_score_master = self.pool.get('spiff.small.business')
        spiff_score_data = spiff_score_master.browse(cr, uid, spiff_score_master_ids[0])
        spiff_business_class = spiff_score_data.spiff_business_class
        spiff_3gb_smart_percent = 0.00
        count_3gb_smart_att = 0.00
        var_name = str('df')
        for spiff_business_class_data in spiff_business_class:
            plus_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            if plus_3gb_business_rule_id:
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                plus_3gb_business_rule_pos = plus_3gb_business_rule_id.is_postpaid
                plus_3gb_business_rule_upg = plus_3gb_business_rule_id.is_upgrade
                plus_3gb_business_rule_pre = plus_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if plus_3gb_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if plus_3gb_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if plus_3gb_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                ##################### Condition string numerator ##################
                spiff_rule_tuple = []
                actual_count_product_type = []
                for sub_rule in plus_3gb_business_rule_id.sub_rules:
                    actual_count_product_type.append(sub_rule.product_code_type.id)
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if not actual_count_product_type:
                    actual_count_product_type = [0]
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                ############# numerator query ###############                
                cr.execute('''select count(df.id)
                    from ('''+from_condition+''')
                    as df where df.'''+field_name+''' = %s 
                    and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                    and df.state = 'done'
                    and df.prm_dsr_smd = false
                    '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
                    from ('''+from_condition+''')
                    as df where df.'''+field_name+''' = %s 
                    and df.crash_prm_job_id_rollback in %s
                    and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                    and df.state = 'done'
                    and df.dsr_product_code_type in %s'''+
    dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                spiff_3gb_smart_percent = count_3gb_percent_logic
                if field_name == 'market_id':
                    cr.execute("select count(id) from sap_tracker where market_id = %s and start_date <= '%s' and end_date >= '%s' and store_inactive = false"%(emp_id,start_date,end_date))
                    store_count = cr.fetchall()
                    store_count = store_count[0][0]
                    if store_count > 0:
                        spiff_3gb_smart_percent = spiff_3gb_smart_percent / float(store_count)
                if field_name == 'region_id':
                    cr.execute('''select count(sap.id) from sap_tracker sap, market_tracker mkt
                        where sap.market_id = mkt.market_id and sap.store_inactive = false and
                        mkt.region_market_id = %s and mkt.start_date <= '%s' and mkt.end_date >= '%s' '''%(emp_id,start_date,end_date))
                    store_count = cr.fetchall()
                    store_count = store_count[0][0]
                    if store_count > 0:
                        spiff_3gb_smart_percent = spiff_3gb_smart_percent / float(store_count)
                count_3gb_smart_att = count_3gb_percent_logic - count_3gb_actual_percent_logic
                ############### condition string denominator ##########################
                if plus_3gb_business_rule_id.sub_rules_2:
                    spiff_rule_tuple = []
                    for sub_rule in plus_3gb_business_rule_id.sub_rules_2:
                        if sub_rule.tac_code_rel_sub_inc_2:
                            for phone_type in sub_rule.tac_code_rel_sub_inc_2:
                                spiff_rule_tuple.append((sub_rule.product_code_type_2.id,phone_type.id,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
                        else:
                            spiff_rule_tuple.append((sub_rule.product_code_type_2.id,False,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
                    if spiff_rule_tuple:
                        condition_string_2 = str("and (")
                        for spiff_rule_data in spiff_rule_tuple:
                            condition_string_2 += str("(")
                            if spiff_rule_data[0]:
                                condition_string_2 += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                            if spiff_rule_data[1]:
                                condition_string_2 += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                     or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                     or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                            if spiff_rule_data[2]:
                                condition_string_2 += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                            if spiff_rule_data[3]:
                                condition_string_2 += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                            if spiff_rule_data[4]:
                                condition_string += str(''' and df.dsr_monthly_access > 0''')
                            condition_string_2 += ") OR "
                        condition_string_2 = condition_string_2[:-4]
                        condition_string_2 += str(")")
                    else:
                        condition_string_2 = ''
                    ############# denominator ######################
                    cr.execute('''select count(df.id) as count
                    from ('''+from_condition+''') 
                    as df where df.'''+field_name+''' = %s 
                    and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                    and df.state = 'done'
                    and df.prm_dsr_smd = false
                    '''+condition_string_2+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))#shashank            
                    tot_sto_pos_upg_box = cr.fetchall()
                    count_all_elig_pos = tot_sto_pos_upg_box[0][0]
                    if not count_all_elig_pos:
                        count_all_elig_pos = 0.00
                    if count_all_elig_pos > 0.00:
                        spiff_3gb_smart_percent = (float(count_3gb_percent_logic) * 100) / float(count_all_elig_pos)
            spiff_3gb_smart_percent = round(spiff_3gb_smart_percent, 2)
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            pay_per_att = spiff_business_class_data.pay_per_att
      # ************ smart attachment count as per payment business rule attached ***************** #      
            pay_plus_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_plus_3gb_business_rule_id and (plus_3gb_business_rule_id.id != pay_plus_3gb_business_rule_id.id):
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_rule_tuple = []
                actual_count_product_type = []
                plus_3gb_business_rule_pos = pay_plus_3gb_business_rule_id.is_postpaid
                plus_3gb_business_rule_upg = pay_plus_3gb_business_rule_id.is_upgrade
                plus_3gb_business_rule_pre = pay_plus_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if plus_3gb_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if plus_3gb_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if plus_3gb_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                for sub_rule in pay_plus_3gb_business_rule_id.sub_rules:
                    actual_count_product_type.append(sub_rule.product_code_type.id)
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if not actual_count_product_type:
                    actual_count_product_type = [0]
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                cr.execute('''select count(df.id)
                    from ('''+from_condition+''')
                    as df where df.'''+field_name+''' = %s 
                    and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                    and df.state = 'done'
                    and df.prm_dsr_smd = false
                    '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
                    from ('''+from_condition+''')
                    as df where df.'''+field_name+''' = %s 
                    and df.crash_prm_job_id_rollback in %s
                    and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                    and df.state = 'done'
                    and df.dsr_product_code_type in %s''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                count_3gb_smart_att = count_3gb_percent_logic - count_3gb_actual_percent_logic
            if att_condition_percent > 0.00:
                if to_condition_percent != 0:
                    if spiff_3gb_smart_percent >= att_condition_percent and spiff_3gb_smart_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + (count_3gb_smart_att * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + flat_pay
                else:
                    if spiff_3gb_smart_percent >= att_condition_percent:  
                        if pay_per_att > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + (count_3gb_smart_att * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_score_payout'] = vals['spiff_score_payout'] + flat_pay
            else:
                if pay_per_att > 0.00:
                    vals['spiff_score_payout'] = vals['spiff_score_payout'] + (count_3gb_smart_att * pay_per_att)
                elif pay_on_rev > 0.00:
                    vals['spiff_score_payout'] = vals['spiff_score_payout'] + ((tot_rev * pay_on_rev)/100)
                elif flat_pay > 0.00:
                    vals['spiff_score_payout'] = vals['spiff_score_payout'] + flat_pay
            spiff_score_count = round(spiff_3gb_smart_percent,2)
            vals['spiff_score_count'] += str("%s, "%(spiff_score_count,))   
        if pay_per_att > 0.00:
            vals['spiff_score_string'] += ("$ %s per"%(pay_per_att))
        elif flat_pay:
            vals['spiff_score_string'] += ("$ %s"%(flat_pay))
        elif pay_on_rev:
            vals['spiff_score_string'] += ("%s"%(pay_on_rev))
            vals['spiff_score_string'] += (" %")
            if emp_model_id == 'rsa':
                vals['spiff_score_string'] += (" of RSA Revenue")
            elif emp_model_id == 'stl':
                vals['spiff_score_string'] += (" of STL Revenue")
            elif emp_model_id == 'mid':
                vals['spiff_score_string'] += (" of MID Revenue")
            elif emp_model_id == 'rsm':
                vals['spiff_score_string'] += (" of RSM Revenue")
            elif emp_model_id == 'mm':
                vals['spiff_score_string'] += (" of MM Revenue")
            elif emp_model_id == 'dos':
                vals['spiff_score_string'] += (" of DOS Revenue")
        if vals['spiff_score_count'] != "":
            vals['spiff_score_count'] = vals['spiff_score_count'][:-2]
        return vals

    def _calculate_jump_attachment(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids, prm_job_id, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}
        vals['spiff_master_3gb_smart_percent'] = str("")
        vals['spiff_3gb_smart_percent'] = str("")
        vals['spiff_3gb_smart_payout'] = 0.00
        vals['count_3gb_smart_att'] = str("")
        vals['jump_comm_string'] = str("")
        count_all_elig_pos = 0.00
        spiff_3gb_smart_percent = 0.00
        spiff_master_3gb_smart_percent = 0.00
        count_3gb_smart_att = 0.00
        spiff_feature_master = self.pool.get('spiff.jump.attachment')
        spiff_feature_master_data = spiff_feature_master.browse(cr, uid, spiff_feature_master_ids[0])
        spiff_business_class = spiff_feature_master_data.spiff_business_class
        unmet_condition = 0
        var_name = str('df')
        for spiff_business_class_data in spiff_business_class:
            plus_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            plus_3gb_business_rule_pos = plus_3gb_business_rule_id.is_postpaid
            plus_3gb_business_rule_upg = plus_3gb_business_rule_id.is_upgrade
            ##################### Condition string numerator ##################
            dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_rule_tuple = []
            actual_count_product_type = []
            for sub_rule in plus_3gb_business_rule_id.sub_rules:
                actual_count_product_type.append(sub_rule.product_code_type.id)
                if sub_rule.tac_code_rel_sub_inc:
                    for phone_type in sub_rule.tac_code_rel_sub_inc:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                else:
                    spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
            if not actual_count_product_type:
                actual_count_product_type = [0]
            if spiff_rule_tuple:
                condition_string = str("and (")
                for spiff_rule_data in spiff_rule_tuple:
                    condition_string += str("(")
                    if spiff_rule_data[0]:
                        condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                    if spiff_rule_data[1]:
                        condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                             or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                             or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                    if spiff_rule_data[2]:
                        condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                    if spiff_rule_data[3]:
                        condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                    if spiff_rule_data[4]:
                        condition_string += str(''' and df.dsr_monthly_access > 0''')
                    condition_string += ") OR "
                condition_string = condition_string[:-4]
                condition_string += str(")")
            else:
                condition_string = ''
            ############### condition string denominator ##########################
            spiff_rule_tuple = []
            for sub_rule in plus_3gb_business_rule_id.sub_rules_2:
                if sub_rule.tac_code_rel_sub_inc_2:
                    for phone_type in sub_rule.tac_code_rel_sub_inc_2:
                        spiff_rule_tuple.append((sub_rule.product_code_type_2.id,phone_type.id,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
                else:
                    spiff_rule_tuple.append((sub_rule.product_code_type_2.id,False,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
            if spiff_rule_tuple:
                condition_string_2 = str("and (")
                for spiff_rule_data in spiff_rule_tuple:
                    condition_string_2 += str("(")
                    if spiff_rule_data[0]:
                        condition_string_2 += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                    if spiff_rule_data[1]:
                        condition_string_2 += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                             or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                             or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                    if spiff_rule_data[2]:
                        condition_string_2 += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                    if spiff_rule_data[3]:
                        condition_string_2 += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                    if spiff_rule_data[4]:
                        condition_string += str(''' and df.dsr_monthly_access > 0''')
                    condition_string_2 += ") OR "
                condition_string_2 = condition_string_2[:-4]
                condition_string_2 += str(")")
            else:
                condition_string_2 = ''
            #################denomnator##########
            if plus_3gb_business_rule_pos == True and plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id) as count
        from (select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,false as dsr_jump_already,false as dsr_php_already,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_jod,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line 
        union all 
        select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,dsr_jump_already,dsr_php_already,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_jod,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line) 
        as df where df.'''+field_name+''' = %s 
        and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
        and df.state = 'done'
        and df.dsr_jump_already = false
        and (df.dsr_php_already is null or df.dsr_php_already = false)
        and (df.dsr_jod = false or df.dsr_jod is null)
        and df.prm_dsr_smd = false
        '''+condition_string_2+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                tot_sto_pos_upg_box = cr.fetchall()
                count_all_elig_pos = tot_sto_pos_upg_box[0][0]
            elif plus_3gb_business_rule_pos == True:
                cr.execute('''select count(df.id) as count
        from (select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_jod,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line) 
        as df where df.'''+field_name+''' = %s 
        and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
        and df.state = 'done'
        and (df.dsr_jod = false or df.dsr_jod is null)
        and df.prm_dsr_smd = false
        '''+condition_string_2+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                tot_sto_pos_upg_box = cr.fetchall()
                count_all_elig_pos = tot_sto_pos_upg_box[0][0]
            elif plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id) as count
        from (select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,dsr_jump_already,dsr_php_already,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_jod,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line) 
        as df where df.'''+field_name+''' = %s 
        and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
        and df.state = 'done'
        and df.dsr_jump_already = false
        and (df.dsr_php_already is null or df.dsr_php_already = false)
        and (df.dsr_jod = false or df.dsr_jod is null)
        and df.prm_dsr_smd = false
        '''+condition_string_2+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                tot_sto_pos_upg_box = cr.fetchall()
                count_all_elig_pos = tot_sto_pos_upg_box[0][0]
            ###### Attachment percent logic ####################
            if plus_3gb_business_rule_pos == True and plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id)
from wireless_dsr_feature_line df
where df.'''+field_name+''' = %s
and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s)) 
and df.state = 'done'
and df.prm_dsr_smd = false
and ((select not(prm_dsr_smd) from wireless_dsr_postpaid_line where id=df.postpaid_id)
        or (select not(prm_dsr_smd) from wireless_dsr_upgrade_line where id=df.upgrade_id))
'''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
            elif plus_3gb_business_rule_pos == True:
                cr.execute('''select count(df.id)
from wireless_dsr_feature_line df, wireless_dsr_postpaid_line pos
where df.'''+field_name+''' = %s and df.postpaid_id = pos.id
and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s)) 
and df.state = 'done'
and pos.prm_dsr_smd = false and df.prm_dsr_smd = false
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
            elif plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id)
from wireless_dsr_feature_line df, wireless_dsr_upgrade_line pos
where df.'''+field_name+''' = %s and df.postpaid_id = pos.id
and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s)) 
and df.state = 'done'
and pos.prm_dsr_smd = false and df.prm_dsr_smd = false
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
            if count_all_elig_pos > 0.00:    
                spiff_3gb_smart_percent = (float(count_3gb_percent_logic) * 100) / float(count_all_elig_pos)
            spiff_3gb_smart_percent = round(spiff_3gb_smart_percent,2)
            ###### numerator to be considered in percent logic only ####################
            if plus_3gb_business_rule_pos == True and plus_3gb_business_rule_upg == True:    
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.prm_dsr_smd = false
            and (df.postpaid_id is not null or df.upgrade_id is not null)
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s
            and df.state = 'done'
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and (df.postpaid_id is not null or df.upgrade_id is not null)
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            elif plus_3gb_business_rule_pos == True:
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.postpaid_id is not null
            and df.prm_dsr_smd = false
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s
            and df.state = 'done'
            and df.crash_prm_job_id_rollback in %s
            and df.postpaid_id is not null
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            elif plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.upgrade_id is not null
            and df.prm_dsr_smd = false
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s
            and df.state = 'done'
            and df.crash_prm_job_id_rollback in %s
            and df.upgrade_id is not null
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            count_3gb_smart_att = count_3gb_percent_logic - count_3gb_actual_percent_logic
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            pay_per_att = spiff_business_class_data.pay_per_att            
            spiff_master_3gb_smart_percent = spiff_business_class_data.att_condition_percent
      # ************ smart attachment count as per payment business rule attached ***************** #      
            pay_plus_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_plus_3gb_business_rule_id and (plus_3gb_business_rule_id.id != pay_plus_3gb_business_rule_id.id):
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_rule_tuple = []
                actual_count_product_type = []
                for sub_rule in pay_plus_3gb_business_rule_id.sub_rules:
                    actual_count_product_type.append(sub_rule.product_code_type.id)
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if not actual_count_product_type:
                    actual_count_product_type = [0]
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                ###### numerator to be considered in percent logic only ####################
            if plus_3gb_business_rule_pos == True and plus_3gb_business_rule_upg == True:    
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.prm_dsr_smd = false
            and (df.postpaid_id is not null or df.upgrade_id is not null)
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s
            and df.state = 'done'
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and (df.postpaid_id is not null or df.upgrade_id is not null)
            '''+condition_string+''' ''',(emp_id,tuple(prm_job_id)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            elif plus_3gb_business_rule_pos == True:
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.postpaid_id is not null
            and df.prm_dsr_smd = false
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s
            and df.state = 'done'
            and df.crash_prm_job_id_rollback in %s
            and df.postpaid_id is not null
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            '''+condition_string+''' ''',(emp_id,tuple(prm_job_id)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            elif plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.upgrade_id is not null
            and df.prm_dsr_smd = false
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s
            and df.state = 'done'
            and df.crash_prm_job_id_rollback in %s
            and df.upgrade_id is not null
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            '''+condition_string+''' ''',(emp_id,tuple(prm_job_id)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                count_3gb_smart_att = count_3gb_percent_logic - count_3gb_actual_percent_logic
            if to_condition_percent != 0:
                if spiff_3gb_smart_percent >= att_condition_percent and spiff_3gb_smart_percent <= to_condition_percent:
                    if unmet_condition == 0:
                        if pay_per_att > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + (count_3gb_smart_att * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + flat_pay
                else:
                    if (pay_per_att == 0.00) and (pay_on_rev == 0.00) and (flat_pay == 0.00):
                        unmet_condition = unmet_condition + 1
            else:
                if spiff_3gb_smart_percent >= att_condition_percent:
                    if unmet_condition == 0:    
                        if pay_per_att > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + (count_3gb_smart_att * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + flat_pay
                else:
                    if (pay_per_att == 0.00) and (pay_on_rev == 0.00) and (flat_pay == 0.00):
                        unmet_condition = unmet_condition + 1
            if pay_per_att > 0.00:
                vals['jump_comm_string'] += ("$ %s per"%(pay_per_att))
            elif flat_pay:
                vals['jump_comm_string'] += ("$ %s"%(flat_pay))
            elif pay_on_rev:
                vals['jump_comm_string'] += ("%s"%(pay_on_rev))
                vals['jump_comm_string'] += (" %")
                if emp_model_id == 'rsa':
                    vals['jump_comm_string'] += (" of RSA Revenue")
                elif emp_model_id == 'stl':
                    vals['jump_comm_string'] += (" of STL Revenue")
                elif emp_model_id == 'mid':
                    vals['jump_comm_string'] += (" of MID Revenue")
                elif emp_model_id == 'rsm':
                    vals['jump_comm_string'] += (" of RSM Revenue")
                elif emp_model_id == 'mm':
                    vals['jump_comm_string'] += (" of MM Revenue")
                elif emp_model_id == 'dos':
                    vals['jump_comm_string'] += (" of DOS Revenue")
            spiff_3gb_smart_percent = round(spiff_3gb_smart_percent,2)
            spiff_master_3gb_smart_percent = round(spiff_master_3gb_smart_percent,2)
            count_3gb_smart_att = round(count_3gb_smart_att,2)
            vals['spiff_3gb_smart_percent'] += str("%s, "%(spiff_3gb_smart_percent,))
            vals['spiff_master_3gb_smart_percent'] += str("%s, "%(spiff_master_3gb_smart_percent,))
            vals['count_3gb_smart_att'] += str("%s, "%(count_3gb_smart_att,))
        if vals['count_3gb_smart_att'] != "":
            vals['count_3gb_smart_att'] = vals['count_3gb_smart_att'][:-2]
        if vals['spiff_3gb_smart_percent'] != "":
            vals['spiff_3gb_smart_percent'] = vals['spiff_3gb_smart_percent'][:-2]
        if vals['spiff_master_3gb_smart_percent'] != "":
            vals['spiff_master_3gb_smart_percent'] = vals['spiff_master_3gb_smart_percent'][:-2]
        return vals

    def _calculate_jod_php_attachment(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids, prm_job_id, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}    
        vals['jod_php_attach_goals'] = 0.00
        vals['jod_php_attach_percent'] = 0.00
        vals['jod_php_attach_payout'] = 0.00
        vals['jod_php_attach_count'] = 0.00
        vals['jod_php_conv_percent'] = 0.00
        vals['jod_php_attach_string'] = str("")
        jod_php_attach_percent = 0.00
        count_all_elig_pos = 0.00
        jod_php_attach_goals = 0.00
        jod_php_attach_count = 0.00
        jod_php_conv_percent = 0.00
        spiff_feature_master = self.pool.get('spiff.jod.php.att')
        spiff_feature_master_data = spiff_feature_master.browse(cr, uid, spiff_feature_master_ids[0])
        spiff_business_class = spiff_feature_master_data.spiff_business_class
        unmet_condition = 0
        var_name = str('df')
        for spiff_business_class_data in spiff_business_class:
            plus_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            plus_3gb_business_rule_pos = plus_3gb_business_rule_id.is_postpaid
            plus_3gb_business_rule_upg = plus_3gb_business_rule_id.is_upgrade
            plus_3gb_business_rule_fea = plus_3gb_business_rule_id.is_feature
            from_condition = str('')
            child_smd_reject_cond = str('')
            if plus_3gb_business_rule_pos:
                from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_jod,is_jump,noncommissionable,null::integer as postpaid_id,null::integer as upgrade_id from wireless_dsr_postpaid_line union all ')
            if plus_3gb_business_rule_upg:
                from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_jod,is_jump,noncommissionable,null::integer as postpaid_id,null::integer as upgrade_id from wireless_dsr_upgrade_line union all ')
            if plus_3gb_business_rule_fea:
                from_condition += str('select id,feature_product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_jod,false as is_jump,noncommissionable,postpaid_id,upgrade_id from wireless_dsr_feature_line union all ')
                child_smd_reject_cond += str('''and ((select not(prm_dsr_smd) from wireless_dsr_postpaid_line where id=df.postpaid_id)
                                                    or (select not(prm_dsr_smd) from wireless_dsr_upgrade_line where id=df.upgrade_id))''')
            from_condition = from_condition[:-10]
            ##################### Condition string numerator ##################
            dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_rule_tuple = []
            actual_count_product_type = []
            for sub_rule in plus_3gb_business_rule_id.sub_rules:
                actual_count_product_type.append(sub_rule.product_code_type.id)
                if sub_rule.tac_code_rel_sub_inc:
                    for phone_type in sub_rule.tac_code_rel_sub_inc:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid,sub_rule.dsr_jod))
                else:
                    spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid,sub_rule.dsr_jod))
            if not actual_count_product_type:
                actual_count_product_type = [0]
            if spiff_rule_tuple:
                condition_string = str("and (")
                for spiff_rule_data in spiff_rule_tuple:
                    condition_string += str("(")
                    if spiff_rule_data[0]:
                        condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                    if spiff_rule_data[1]:
                        condition_string += str(''' and left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s) '''%(spiff_rule_data[1],))
                    if spiff_rule_data[2]:
                        condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                    if spiff_rule_data[3]:
                        condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                    if spiff_rule_data[4]:
                        condition_string += str(''' and df.dsr_monthly_access > 0''')
                    if spiff_rule_data[5]:
                        condition_string += str(''' and df.dsr_jod = true ''')
                    condition_string += ") OR "
                condition_string = condition_string[:-4]
                condition_string += str(")")
            else:
                condition_string = ''
            ############### condition string denominator ##########################
            spiff_rule_tuple = []
            for sub_rule in plus_3gb_business_rule_id.sub_rules_2:
                if sub_rule.tac_code_rel_sub_inc_2:
                    for phone_type in sub_rule.tac_code_rel_sub_inc_2:
                        spiff_rule_tuple.append((sub_rule.product_code_type_2.id,phone_type.id,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2,sub_rule.dsr_jod_2))
                else:
                    spiff_rule_tuple.append((sub_rule.product_code_type_2.id,False,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2,sub_rule.dsr_jod_2))
            if spiff_rule_tuple:
                condition_string_2 = str("and (")
                for spiff_rule_data in spiff_rule_tuple:
                    condition_string_2 += str("(")
                    if spiff_rule_data[0]:
                        condition_string_2 += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                    if spiff_rule_data[1]:
                        condition_string_2 += str(''' and left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s) '''%(spiff_rule_data[1],))
                    if spiff_rule_data[2]:
                        condition_string_2 += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                    if spiff_rule_data[3]:
                        condition_string_2 += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                    if spiff_rule_data[4]:
                        condition_string_2 += str(''' and df.dsr_monthly_access > 0''')
                    if spiff_rule_data[5]:
                        condition_string_2 += str(''' and df.dsr_jod = true ''')
                    condition_string_2 += ") OR "
                condition_string_2 = condition_string_2[:-4]
                condition_string_2 += str(")")
            else:
                condition_string_2 = ''
            #################denomnator##########
            cr.execute('''select count(df.id) as count
                    from ('''+from_condition+''') as df 
                    where df.'''+field_name+''' = %s 
                    and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                    and df.state = 'done'
                    and df.prm_dsr_smd = false
                    '''+condition_string_2+
                    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
            tot_sto_pos_upg_box = cr.fetchall()
            count_all_elig_pos = tot_sto_pos_upg_box[0][0]
            ###### Attachment percent logic ####################
            cr.execute('''select count(df.id)
                from ('''+from_condition+''') as df
                where df.'''+field_name+''' = %s
                and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s)) 
                and df.state = 'done'
                and df.prm_dsr_smd = false
                '''+child_smd_reject_cond
                +condition_string+
                dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
            count_3gb_store_data = cr.fetchall()
            count_3gb_percent_logic = count_3gb_store_data[0][0]
            cr.execute('''select count(df.id)
                from ('''+from_condition+''') as df
                where df.'''+field_name+''' = %s
                and df.state = 'done'
                and df.crash_prm_job_id_rollback in %s
                and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                '''+condition_string+
                dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id)))
            count_3gb_store_data = cr.fetchall()
            count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            if count_all_elig_pos > 0.00:    
                jod_php_attach_percent = (float(count_3gb_percent_logic) * 100) / float(count_all_elig_pos)
            jod_php_attach_percent = round(jod_php_attach_percent,2)
            jod_php_attach_count = count_3gb_percent_logic - count_3gb_actual_percent_logic
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            pay_per_att = spiff_business_class_data.pay_per_att            
            jod_php_attach_goals = spiff_business_class_data.att_condition_percent
            if jod_php_conv_percent == 0.00:
                jod_php_conv_percent = jod_php_attach_percent
      # ************ smart attachment count as per payment business rule attached ***************** #      
            pay_plus_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_plus_3gb_business_rule_id and (plus_3gb_business_rule_id.id != pay_plus_3gb_business_rule_id.id):
                plus_3gb_business_rule_pos = pay_plus_3gb_business_rule_id.is_postpaid
                plus_3gb_business_rule_upg = pay_plus_3gb_business_rule_id.is_upgrade
                plus_3gb_business_rule_fea = pay_plus_3gb_business_rule_id.is_feature
                from_condition = str('')
                child_smd_reject_cond = str('')
                if plus_3gb_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_jod,is_jump,noncommissionable,null::integer as postpaid_id,null::integer as upgrade_id from wireless_dsr_postpaid_line union all ')
                if plus_3gb_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_jod,is_jump,noncommissionable,null::integer as postpaid_id,null::integer as upgrade_id from wireless_dsr_upgrade_line union all ')
                if plus_3gb_business_rule_fea:
                    from_condition += str('select id,feature_product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_jod,false as is_jump,noncommissionable,postpaid_id,upgrade_id from wireless_dsr_feature_line union all ')
                    child_smd_reject_cond += str('''and ((select not(prm_dsr_smd) from wireless_dsr_postpaid_line where id=df.postpaid_id)
                                                    or (select not(prm_dsr_smd) from wireless_dsr_upgrade_line where id=df.upgrade_id))''')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                actual_count_product_type = []
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                for sub_rule in pay_plus_3gb_business_rule_id.sub_rules:
                    actual_count_product_type.append(sub_rule.product_code_type.id)
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid,sub_rule.dsr_jod))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid,sub_rule.dsr_jod))
                if not actual_count_product_type:
                    actual_count_product_type = [0]
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s) '''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        if spiff_rule_data[5]:
                            condition_string += str(''' and df.dsr_jod = true ''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                ###### numerator to be considered in percent logic only ####################
                cr.execute('''select count(df.id)
                        from ('''+from_condition+''') as df
                        where df.'''+field_name+''' = %s
                        and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s)) 
                        and df.state = 'done'
                        and df.prm_dsr_smd = false
                        '''+child_smd_reject_cond
                        +condition_string+
                        dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
                        from ('''+from_condition+''') as df
                        where df.'''+field_name+''' = %s
                        and df.state = 'done'
                        and df.crash_prm_job_id_rollback in %s
                        and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                        '''+condition_string+''' ''',(emp_id,tuple(prm_job_id)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                jod_php_attach_count = count_3gb_percent_logic - count_3gb_actual_percent_logic
            if to_condition_percent != 0:
                if jod_php_attach_percent >= att_condition_percent and jod_php_attach_percent <= to_condition_percent:
                    if unmet_condition == 0:
                        if pay_per_att > 0.00:
                            vals['jod_php_attach_payout'] = vals['jod_php_attach_payout'] + (jod_php_attach_count * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['jod_php_attach_payout'] = vals['jod_php_attach_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['jod_php_attach_payout'] = vals['jod_php_attach_payout'] + flat_pay
                else:
                    if (pay_per_att == 0.00) and (pay_on_rev == 0.00) and (flat_pay == 0.00):
                        unmet_condition = unmet_condition + 1
            else:
                if jod_php_attach_percent >= att_condition_percent:
                    if unmet_condition == 0:    
                        if pay_per_att > 0.00:
                            vals['jod_php_attach_payout'] = vals['jod_php_attach_payout'] + (jod_php_attach_count * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['jod_php_attach_payout'] = vals['jod_php_attach_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['jod_php_attach_payout'] = vals['jod_php_attach_payout'] + flat_pay
                else:
                    if (pay_per_att == 0.00) and (pay_on_rev == 0.00) and (flat_pay == 0.00):
                        unmet_condition = unmet_condition + 1
            if pay_per_att > 0.00:
                vals['jod_php_attach_string'] += ("$ %s per"%(pay_per_att))
            elif flat_pay:
                vals['jod_php_attach_string'] += ("$ %s"%(flat_pay))
            elif pay_on_rev:
                vals['jod_php_attach_string'] += ("%s"%(pay_on_rev))
                vals['jod_php_attach_string'] += (" %")
                if emp_model_id == 'rsa':
                    vals['jod_php_attach_string'] += (" of RSA Revenue")
                elif emp_model_id == 'stl':
                    vals['jod_php_attach_string'] += (" of STL Revenue")
                elif emp_model_id == 'mid':
                    vals['jod_php_attach_string'] += (" of MID Revenue")
                elif emp_model_id == 'rsm':
                    vals['jod_php_attach_string'] += (" of RSM Revenue")
                elif emp_model_id == 'mm':
                    vals['jod_php_attach_string'] += (" of MM Revenue")
                elif emp_model_id == 'dos':
                    vals['jod_php_attach_string'] += (" of DOS Revenue")
            jod_php_attach_percent = round(jod_php_attach_percent,2)
            jod_php_attach_count = round(jod_php_attach_count,2)
            vals['jod_php_attach_percent'] = jod_php_attach_percent
            vals['jod_php_attach_goals'] = jod_php_attach_goals
            vals['jod_php_attach_count'] = jod_php_attach_count
            vals['jod_php_conv_percent'] = jod_php_conv_percent
        return vals

    def _calculate_feature_attachment(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_feature_master_ids, prm_job_id, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}    
        vals['spiff_master_3gb_smart_percent'] = str("")
        vals['spiff_3gb_smart_percent'] = str("")
        vals['spiff_3gb_smart_payout'] = 0.00
        vals['count_3gb_smart_att'] = str("")
        vals['paid_comm_string'] = str("")
        spiff_3gb_smart_percent = 0.00
        count_all_elig_pos = 0.00
        spiff_master_3gb_smart_percent = 0.00
        count_3gb_smart_att = 0.00
        spiff_feature_master = self.pool.get('spiff.feature.attachment')
        spiff_feature_master_data = spiff_feature_master.browse(cr, uid, spiff_feature_master_ids[0])
        spiff_business_class = spiff_feature_master_data.spiff_business_class
        unmet_condition = 0
        var_name = str('df')
        for spiff_business_class_data in spiff_business_class:
            plus_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            plus_3gb_business_rule_pos = plus_3gb_business_rule_id.is_postpaid
            plus_3gb_business_rule_upg = plus_3gb_business_rule_id.is_upgrade
            ##################### Condition string numerator ##################
            dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            spiff_rule_tuple = []
            actual_count_product_type = []
            for sub_rule in plus_3gb_business_rule_id.sub_rules:
                actual_count_product_type.append(sub_rule.product_code_type.id)
                if sub_rule.tac_code_rel_sub_inc:
                    for phone_type in sub_rule.tac_code_rel_sub_inc:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                else:
                    spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
            if not actual_count_product_type:
                actual_count_product_type = [0]
            if spiff_rule_tuple:
                condition_string = str("and (")
                for spiff_rule_data in spiff_rule_tuple:
                    condition_string += str("(")
                    if spiff_rule_data[0]:
                        condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                    if spiff_rule_data[1]:
                        condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                             or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                             or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                    if spiff_rule_data[2]:
                        condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                    if spiff_rule_data[3]:
                        condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                    if spiff_rule_data[4]:
                        condition_string += str(''' and df.dsr_monthly_access > 0''')
                    condition_string += ") OR "
                condition_string = condition_string[:-4]
                condition_string += str(")")
            else:
                condition_string = ''
            ############### condition string denominator ##########################
            spiff_rule_tuple = []
            for sub_rule in plus_3gb_business_rule_id.sub_rules_2:
                if sub_rule.tac_code_rel_sub_inc_2:
                    for phone_type in sub_rule.tac_code_rel_sub_inc_2:
                        spiff_rule_tuple.append((sub_rule.product_code_type_2.id,phone_type.id,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
                else:
                    spiff_rule_tuple.append((sub_rule.product_code_type_2.id,False,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
            if spiff_rule_tuple:
                condition_string_2 = str("and (")
                for spiff_rule_data in spiff_rule_tuple:
                    condition_string_2 += str("(")
                    if spiff_rule_data[0]:
                        condition_string_2 += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                    if spiff_rule_data[1]:
                        condition_string_2 += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                             or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                             or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                    if spiff_rule_data[2]:
                        condition_string_2 += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                    if spiff_rule_data[3]:
                        condition_string_2 += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                    if spiff_rule_data[4]:
                        condition_string += str(''' and df.dsr_monthly_access > 0''')
                    condition_string_2 += ") OR "
                condition_string_2 = condition_string_2[:-4]
                condition_string_2 += str(")")
            else:
                condition_string_2 = ''
            ############# denominator ######################
            if plus_3gb_business_rule_pos == True and plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id) as count
                from (select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line 
                union all 
                select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line) 
                as df where df.'''+field_name+''' = %s 
                and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                and df.state = 'done'
                and df.prm_dsr_smd = false
                '''+condition_string_2+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))#shashank            
                tot_sto_pos_upg_box = cr.fetchall()
                count_all_elig_pos = tot_sto_pos_upg_box[0][0]
                if not count_all_elig_pos:
                    count_all_elig_pos = 0.00
            elif plus_3gb_business_rule_pos == True:
                cr.execute('''select count(df.id) as count
        from (select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line) 
        as df
        where df.'''+field_name+''' = %s 
        and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
        and df.state = 'done'
        and df.prm_dsr_smd = false
        '''+condition_string_2+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                tot_sto_pos_upg_box = cr.fetchall()
                count_all_elig_pos = tot_sto_pos_upg_box[0][0]
                if not count_all_elig_pos:
                    count_all_elig_pos = 0.00
            elif plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id) as count
        from (select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line) 
        as df
        where df.'''+field_name+''' = %s 
        and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
        and df.state = 'done'
        and df.prm_dsr_smd = false
        '''+condition_string_2+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                tot_sto_pos_upg_box = cr.fetchall()
                count_all_elig_pos = tot_sto_pos_upg_box[0][0]
                if not count_all_elig_pos:
                    count_all_elig_pos = 0.00
            ###### Attachment percent logic ####################
            if plus_3gb_business_rule_pos == True and plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id)
from wireless_dsr_feature_line df
where df.'''+field_name+''' = %s
and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s)) 
and df.state = 'done'
and df.prm_dsr_smd = false
and ((select not(prm_dsr_smd) from wireless_dsr_postpaid_line where id=df.postpaid_id)
        or (select not(prm_dsr_smd) from wireless_dsr_upgrade_line where id=df.upgrade_id))
'''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
            elif plus_3gb_business_rule_pos == True:
                cr.execute('''select count(df.id)
from wireless_dsr_feature_line df, wireless_dsr_postpaid_line pos
where df.'''+field_name+''' = %s and df.postpaid_id = pos.id
and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s)) 
and df.state = 'done'
and pos.prm_dsr_smd = false and df.prm_dsr_smd = false
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
            elif plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id)
from wireless_dsr_feature_line df, wireless_dsr_upgrade_line pos
where df.'''+field_name+''' = %s and df.postpaid_id = pos.id
and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s)) 
and df.state = 'done'
and pos.prm_dsr_smd = false and df.prm_dsr_smd = false
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
            if count_all_elig_pos > 0.00:    
                spiff_3gb_smart_percent = (float(count_3gb_percent_logic) * 100) / float(count_all_elig_pos)
            spiff_3gb_smart_percent = round(spiff_3gb_smart_percent,2)
            ###### numerator to be considered in percent logic only ####################
            if plus_3gb_business_rule_pos == True and plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.prm_dsr_smd = false
            and (df.postpaid_id is not null or df.upgrade_id is not null)
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and df.state = 'done'
            and df.dsr_product_code_type in %s'''+
    dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            elif plus_3gb_business_rule_pos == True:
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.prm_dsr_smd = false
            and df.postpaid_id is not null
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and df.state = 'done'
            and df.dsr_product_code_type in %s'''+
    dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            elif plus_3gb_business_rule_upg == True:
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.state = 'done'
            and df.prm_dsr_smd = false
            and df.upgrade_id is not null
            '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                count_3gb_store_data = cr.fetchall()
                count_3gb_percent_logic = count_3gb_store_data[0][0]
                cr.execute('''select count(df.id)
            from wireless_dsr_feature_line df
            where df.'''+field_name+''' = %s 
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and df.state = 'done'
            and df.dsr_product_code_type in %s'''+
    dsr_exclude_condition+''' ''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                count_3gb_store_data = cr.fetchall()
                count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
            count_3gb_smart_att = count_3gb_percent_logic - count_3gb_actual_percent_logic
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            pay_per_att = spiff_business_class_data.pay_per_att
            spiff_master_3gb_smart_percent = spiff_business_class_data.att_condition_percent
      # ************ smart attachment count as per payment business rule attached ***************** #      
            pay_plus_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_plus_3gb_business_rule_id and (plus_3gb_business_rule_id.id != pay_plus_3gb_business_rule_id.id):
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_rule_tuple = []
                actual_count_product_type = []
                for sub_rule in pay_plus_3gb_business_rule_id.sub_rules:
                    actual_count_product_type.append(sub_rule.product_code_type.id)
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if not actual_count_product_type:
                    actual_count_product_type = [0]
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                if plus_3gb_business_rule_pos == True and plus_3gb_business_rule_upg == True:
                    cr.execute('''select count(df.id)
                from wireless_dsr_feature_line df
                where df.'''+field_name+''' = %s 
                and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                and df.state = 'done'
                and df.prm_dsr_smd = false
                and (df.postpaid_id is not null or df.upgrade_id is not null)
                '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                    count_3gb_store_data = cr.fetchall()
                    count_3gb_percent_logic = count_3gb_store_data[0][0]
                    cr.execute('''select count(df.id)
                from wireless_dsr_feature_line df
                where df.'''+field_name+''' = %s 
                and df.crash_prm_job_id_rollback in %s
                and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                and df.state = 'done'
                and df.dsr_product_code_type in %s''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                    count_3gb_store_data = cr.fetchall()
                    count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                elif plus_3gb_business_rule_pos == True:
                    cr.execute('''select count(df.id)
                from wireless_dsr_feature_line df
                where df.'''+field_name+''' = %s 
                and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                and df.state = 'done'
                and df.prm_dsr_smd = false
                and df.postpaid_id is not null
                '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                    count_3gb_store_data = cr.fetchall()
                    count_3gb_percent_logic = count_3gb_store_data[0][0]
                    cr.execute('''select count(df.id)
                from wireless_dsr_feature_line df
                where df.'''+field_name+''' = %s 
                and df.crash_prm_job_id_rollback in %s
                and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                and df.state = 'done'
                and df.dsr_product_code_type in %s''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                    count_3gb_store_data = cr.fetchall()
                    count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                elif plus_3gb_business_rule_upg == True:
                    cr.execute('''select count(df.id)
                from wireless_dsr_feature_line df
                where df.'''+field_name+''' = %s 
                and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                and df.state = 'done'
                and df.prm_dsr_smd = false
                and df.upgrade_id is not null
                '''+condition_string+
    dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                    count_3gb_store_data = cr.fetchall()
                    count_3gb_percent_logic = count_3gb_store_data[0][0]
                    cr.execute('''select count(df.id)
                from wireless_dsr_feature_line df
                where df.'''+field_name+''' = %s 
                and df.crash_prm_job_id_rollback in %s
                and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                and df.state = 'done'
                and df.dsr_product_code_type in %s''',(emp_id,tuple(prm_job_id),tuple(actual_count_product_type)))
                    count_3gb_store_data = cr.fetchall()
                    count_3gb_actual_percent_logic = count_3gb_store_data[0][0] or 0.00
                count_3gb_smart_att = count_3gb_percent_logic - count_3gb_actual_percent_logic
            if to_condition_percent != 0:
                if spiff_3gb_smart_percent >= att_condition_percent and spiff_3gb_smart_percent <= to_condition_percent:
                    if unmet_condition == 0:
                        if pay_per_att > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + (count_3gb_smart_att * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + flat_pay
                else:
                    if (pay_per_att == 0.00) and (pay_on_rev == 0.00) and (flat_pay == 0.00):
                        unmet_condition = unmet_condition + 1
            else:
                if spiff_3gb_smart_percent >= att_condition_percent:
                    if unmet_condition == 0:    
                        if pay_per_att > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + (count_3gb_smart_att * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_3gb_smart_payout'] = vals['spiff_3gb_smart_payout'] + flat_pay
                else:
                    if (pay_per_att == 0.00) and (pay_on_rev == 0.00) and (flat_pay == 0.00):
                        unmet_condition = unmet_condition + 1
            if pay_per_att > 0.00:
                vals['paid_comm_string'] += ("$ %s per"%(pay_per_att))
            elif flat_pay:
                vals['paid_comm_string'] += ("$ %s"%(flat_pay))
            elif pay_on_rev:
                vals['paid_comm_string'] += ("%s"%(pay_on_rev))
                vals['paid_comm_string'] += (" %")
                if emp_model_id == 'rsa':
                    vals['paid_comm_string'] += (" of RSA Revenue")
                elif emp_model_id == 'stl':
                    vals['paid_comm_string'] += (" of STL Revenue")
                elif emp_model_id == 'mid':
                    vals['paid_comm_string'] += (" of MID Revenue")
                elif emp_model_id == 'rsm':
                    vals['paid_comm_string'] += (" of RSM Revenue")
                elif emp_model_id == 'mm':
                    vals['paid_comm_string'] += (" of MM Revenue")
                elif emp_model_id == 'dos':
                    vals['paid_comm_string'] += (" of DOS Revenue")
            spiff_3gb_smart_percent = round(spiff_3gb_smart_percent,2)
            spiff_master_3gb_smart_percent = round(spiff_master_3gb_smart_percent,2)
            count_3gb_smart_att = round(count_3gb_smart_att,2)
            vals['spiff_3gb_smart_percent'] += str("%s, "%(spiff_3gb_smart_percent,))
            vals['spiff_master_3gb_smart_percent'] += str("%s, "%(spiff_master_3gb_smart_percent,))
            vals['count_3gb_smart_att'] += str("%s, "%(count_3gb_smart_att,))
        if vals['count_3gb_smart_att'] != "":
            vals['count_3gb_smart_att'] = vals['count_3gb_smart_att'][:-2]
        if vals['spiff_3gb_smart_percent'] != "":
            vals['spiff_3gb_smart_percent'] = vals['spiff_3gb_smart_percent'][:-2]
        if vals['spiff_master_3gb_smart_percent'] != "":
            vals['spiff_master_3gb_smart_percent'] = vals['spiff_master_3gb_smart_percent'][:-2]
        return vals

    def _get_basic_parameters_box_rev(self, cr, uid, field_name, level_id, start_date, end_date, condition_box_string, from_box_condition, prm_job_id, box_br, rev_br,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        para_vals = {}
        pre_count = 0.00
        tot_box = 0.00
        actual_box = 0.00
        tot_emp_pos_upg_box = 0.00
        tot_rev = 0.00
        actual_rev = 0.00
        apk_rev = 0.00
        apk_count = 0.00
    #********* added Feb 2015*********#    
        gross_box = 0.00
        gross_rev = 0.00
        smd_box = 0.00
        smd_rev = 0.00
        pmd_box = 0.00
        pmd_rev = 0.00
        react_box = 0.00
        react_rev = 0.00
        noncomm_rev = 0.00
        noncomm_box = 0.00
        var_name = 'test'
        box_dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,box_br[0],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
        rev_dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,rev_br[0],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
   ########### Added for Accessory Chargeback ###############
        acc_deact_rev = 0.00
        if field_name == 'employee_id':
            cr.execute("select sum(amnt) from acc_crash_deacts_master where emp_id = %s and start_date = '%s' "%(level_id,start_date))
            acc_deact_data = cr.fetchall()
            if acc_deact_data:
                acc_deact_rev = acc_deact_data[0][0]
        elif field_name == 'store_id':
            cr.execute("select sum(amnt) from acc_crash_deacts_master where store_id = %s and start_date = '%s' "%(level_id,start_date))
            acc_deact_data = cr.fetchall()
            if acc_deact_data:
                acc_deact_rev = acc_deact_data[0][0]
        elif field_name == 'market_id':
            cr.execute('''select sum(acc.amnt) from acc_crash_deacts_master acc, sap_tracker sap
where sap.market_id = %s and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
and acc.store_id = sap.sap_id and acc.start_date = %s ''',(level_id,start_date,end_date,start_date))
            acc_deact_data = cr.fetchall()
            if acc_deact_data:
                acc_deact_rev = acc_deact_data[0][0]
        elif field_name == 'region_id':
            cr.execute('''select sum(acc.amnt) from acc_crash_deacts_master acc, sap_tracker sap, market_tracker mkt 
where mkt.region_market_id = %s and mkt.end_date >= %s and mkt.start_date <= %s
and sap.market_id = mkt.market_id and sap.end_date >= %s and sap.start_date <= %s and sap.store_inactive = false
and acc.store_id = sap.sap_id and acc.start_date = %s ''',(level_id,start_date,end_date,start_date,end_date,start_date))
            acc_deact_data = cr.fetchall()
            if acc_deact_data:
                acc_deact_rev = acc_deact_data[0][0]
        if not acc_deact_rev:
            acc_deact_rev = 0.00
############ Accessory Chargeback Ends Here ############

        if from_box_condition != '':
            cr.execute('''select dsr_trans_type
        ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
        +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
        from 
    ('''+from_box_condition+''') as test
    where test.''' + field_name + ''' = %s
    and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
    and test.state = 'done'
    --and test.prm_dsr_smd = false
    '''+condition_box_string+
    box_dsr_exclude_condition+'''
    group by test.dsr_trans_type
    order by test.dsr_trans_type asc''', (level_id, start_date, end_date,start_date,end_date))
            emp_data = cr.fetchall()
            for emp_data_id in emp_data:
                gross_box = gross_box + emp_data_id[1]
                if emp_data_id[0] == 'postpaid' or emp_data_id[0] == 'upgrade':
                    tot_emp_pos_upg_box = tot_emp_pos_upg_box + emp_data_id[1]
                if emp_data_id[0] == 'prepaid':
                    pre_count = emp_data_id[1]
            cr.execute('''select dsr_trans_type
        ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
        +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
        from 
    ('''+from_box_condition+''') as test
    where test.''' + field_name + ''' = %s
    and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
    and test.state = 'done'
    and test.prm_dsr_smd = true
    '''+condition_box_string+
    box_dsr_exclude_condition+'''
    group by test.dsr_trans_type
    order by test.dsr_trans_type asc''', (level_id, start_date, end_date,start_date,end_date))
            emp_data = cr.fetchall()
            for emp_data_id in emp_data:
                smd_box = smd_box + emp_data_id[1]
            if not smd_box:
                smd_box = 0.00
            actual_box = gross_box - smd_box
            cr.execute('''select sum(upg.dsr_rev_gen) as prm_deduct
    ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
    +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as prm_box_deduct
from ('''+from_box_condition+'''
union all
select id,feature_product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_feature_line) 
as upg where upg.'''+field_name+''' = %s
and upg.state = 'done'
and upg.crash_prm_job_id_rollback in %s
and upg.prm_dsr_pmd = true''',(level_id,tuple(prm_job_id)))
            emp_data = cr.fetchall()
            deact_pmd_rev = emp_data[0][0]
            deact_pmd_box = emp_data[0][1]
            if not deact_pmd_rev:
                deact_pmd_rev = 0.00
            if not deact_pmd_box:
                deact_pmd_box = 0
            deact_pmd_rev = deact_pmd_rev + acc_deact_rev
            pmd_rev = deact_pmd_rev
            pmd_box = deact_pmd_box
            cr.execute('''select sum(upg.dsr_rev_gen) as prm_deduct
    ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
    +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as prm_box_deduct
from ('''+from_box_condition+'''
union all
select id,feature_product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_feature_line) 
as upg where upg.'''+field_name+''' = %s
and upg.state = 'done'
and upg.crash_prm_job_id_rollback in %s
and upg.noncommissionable = true''',(level_id,tuple(prm_job_id)))
            emp_data = cr.fetchall()
            deact_comm_rev = emp_data[0][0]
            deact_comm_box = emp_data[0][1]
            if not deact_comm_rev:
                deact_comm_rev = 0.00
            if not deact_comm_box:
                deact_comm_box = 0
            noncomm_rev = deact_comm_rev
            noncomm_box = deact_comm_box
            cr.execute('''select sum(upg.dsr_rev_gen) as prm_deduct
    ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
    +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as prm_box_deduct
from ('''+from_box_condition+'''
union all
select id,feature_product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_feature_line) 
as upg where upg.'''+field_name+''' = %s
and upg.state = 'done'
and upg.crash_prm_job_id_rollback in %s
and upg.prm_react_recon = true''',(level_id,tuple(prm_job_id)))
            emp_data = cr.fetchall()
            react_rev = emp_data[0][0]
            react_box = emp_data[0][1]
            if not react_rev:
                react_rev = 0.00
            if not react_box:
                react_box = 0.00
        else:
            actual_box = 0.00
            tot_emp_pos_upg_box = 0.00
            pre_count = 0.00
            deact_rev = 0.00
            deact_box = 0.00
        cr.execute('''select sum(test.dsr_rev_gen) as actual_rev
,dsr_trans_type
,sum(dsr_rev_gen) as acc_mrc
,sum(dsr_quantity) as count
from 
(select id,product_id,dsr_rev_gen,dsr_trans_type,true as created_feature, 0.00 as dsr_acc_mrc,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0 as dsr_quantity,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_postpaid_line 
union all
select id,feature_product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_feature_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,created_feature, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description,dsr_product_code_type
from wireless_dsr_prepaid_line 
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_upgrade_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true,dsr_acc_mrc,false as prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,dsr_quantity,pseudo_date,dsr_emp_type,null as dsr_credit_class,null as dsr_product_code,null as dsr_product_code_type
from wireless_dsr_acc_line) as test
where test.''' + field_name + ''' = %s
and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done' '''+
rev_dsr_exclude_condition+'''
--and test.prm_dsr_smd = false
group by test.dsr_trans_type
order by test.dsr_trans_type asc''', (level_id, start_date, end_date,start_date,end_date))
        emp_data = cr.fetchall()
        for emp_data_id in emp_data:
            if emp_data_id[1] == 'accessory':
                apk_rev = emp_data_id[2]
                apk_count = emp_data_id[3]
            gross_rev = gross_rev + emp_data_id[0]
        cr.execute('''select sum(test.dsr_rev_gen) as actual_rev
,dsr_trans_type
,sum(dsr_rev_gen) as acc_mrc
,sum(dsr_quantity) as count
from 
(select id,product_id,dsr_rev_gen,dsr_trans_type,true as created_feature, 0.00 as dsr_acc_mrc,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0 as dsr_quantity,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_postpaid_line 
union all
select id,feature_product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_feature_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,created_feature, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description,dsr_product_code_type
from wireless_dsr_prepaid_line 
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_upgrade_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true,dsr_acc_mrc,false as prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,dsr_quantity,pseudo_date,dsr_emp_type,null as dsr_credit_class,null as dsr_product_code,null as dsr_product_code_type
from wireless_dsr_acc_line) as test
where test.''' + field_name + ''' = %s
and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done' '''+
rev_dsr_exclude_condition+'''
and test.prm_dsr_smd = true
group by test.dsr_trans_type
order by test.dsr_trans_type asc''', (level_id, start_date, end_date,start_date,end_date))
        emp_data = cr.fetchall()
        for emp_data_id in emp_data:
            if emp_data_id[1] == 'accessory':
                apk_rev = apk_rev - emp_data_id[2]
                apk_count = apk_count - emp_data_id[3]
            smd_rev = smd_rev + emp_data_id[0]
        if not smd_rev:
            smd_rev = 0.00
        actual_rev = gross_rev - smd_rev
        tot_rev = actual_rev - float(deact_pmd_rev) - float(deact_comm_rev)
        tot_box = actual_box - deact_pmd_box - deact_comm_box
        para_vals = {   'pre_count' : pre_count,
                        'tot_box' : tot_box,
                        'actual_box' : actual_box,
                        'tot_emp_pos_upg_box' : tot_emp_pos_upg_box,
                        'tot_rev' : tot_rev,
                        'actual_rev' : actual_rev,
                        'apk_rev' : apk_rev,
                        'apk_count':apk_count,
                        'smd_rev':smd_rev,
                        'smd_box':smd_box,
                        'pmd_rev':pmd_rev,
                        'pmd_box':pmd_box,
                        'react_rev':react_rev,
                        'react_box':react_box,
                        'noncomm_rev':deact_comm_rev,
                        'noncomm_box':deact_comm_box,
                    }
        return para_vals

    def _calculate_store_rev_dsr(self, cr, uid, store_multi_id, start_date, end_date, condition_box_string, from_box_condition, prm_job_id, box_br, rev_br,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        store_vals = {}
        actual_store_rev = 0.00
        actual_store_box = 0.00
        store_acc_rev = 0.00
        tot_store_rev = 0.00
        tot_store_box = 0.00
        store_acc_count = 0.00
        var_name = 'test'
        box_dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,box_br[0],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
        rev_dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,rev_br[0],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
   ########### Added for Accessory Chargeback ###############
        acc_deact_rev = 0.00
        cr.execute("select sum(amnt) from acc_crash_deacts_master where store_id = %s and start_date = '%s' "%(store_multi_id,start_date))
        acc_deact_data = cr.fetchall()
        if acc_deact_data:
            acc_deact_rev = acc_deact_data[0][0]
        if not acc_deact_rev:
            acc_deact_rev = 0.00
############ Accessory Chargeback Ends Here ############

        if from_box_condition != '':    
            cr.execute('''select dsr_trans_type
        ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
        +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
        from 
    ('''+from_box_condition+''') as test
    where test.store_id = %s
    and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
    and test.state = 'done'
    and test.prm_dsr_smd = false
    '''+condition_box_string+
    box_dsr_exclude_condition+'''
    group by test.dsr_trans_type
    order by test.dsr_trans_type asc''',(store_multi_id, start_date, end_date,start_date,end_date))
            store_data = cr.fetchall()
            for store_data_id in store_data:
                actual_store_box = actual_store_box + store_data_id[1]
            cr.execute('''select sum(upg.dsr_rev_gen) as prm_deduct
    ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
    +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as prm_box_deduct
from (select product_id,dsr_rev_gen,crash_prm_job_id_rollback,dsr_trans_type,true as created_feature,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date from wireless_dsr_postpaid_line 
union all 
select product_id,dsr_rev_gen,crash_prm_job_id_rollback,dsr_trans_type, true,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date from wireless_dsr_upgrade_line
union all
select product_id,dsr_rev_gen,crash_prm_job_id_rollback,dsr_trans_type, created_feature,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date from wireless_dsr_prepaid_line
union all
select feature_product_id,dsr_rev_gen,crash_prm_job_id_rollback,dsr_trans_type, true,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date from wireless_dsr_feature_line) 
as upg where upg.store_id = %s
and upg.prm_dsr_smd = false
and upg.state = 'done'
and upg.crash_prm_job_id_rollback in %s''',(store_multi_id,tuple(prm_job_id)))
            emp_data = cr.fetchall()
            deact_rev = emp_data[0][0]
            deact_box = emp_data[0][1]
            if not deact_rev:
                deact_rev = 0.00
            if not deact_box:
                deact_box = 0
        else:
            actual_store_box = 0.00
            deact_rev = 0.00
            deact_box = 0.00
        deact_rev = deact_rev + acc_deact_rev
        cr.execute('''select sum(dsr_rev_gen) as actual_rev
,dsr_trans_type
,sum(dsr_rev_gen) as tot_rev
,sum(dsr_quantity) as count
from 
(select id,product_id,dsr_rev_gen,dsr_trans_type,true as created_feature, 0.00 as dsr_acc_mrc,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0 as dsr_quantity,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_postpaid_line 
union all
select id,feature_product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_feature_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,created_feature, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description,dsr_product_code_type
from wireless_dsr_prepaid_line 
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_upgrade_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true, dsr_acc_mrc,false as prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,dsr_quantity,pseudo_date,dsr_emp_type,null as dsr_credit_class,null as dsr_product_code,null as dsr_product_code_type
from wireless_dsr_acc_line) as test
where test.store_id = %s
and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done'
and test.prm_dsr_smd = false'''
+rev_dsr_exclude_condition+'''
group by test.dsr_trans_type
order by test.dsr_trans_type asc''',(store_multi_id, start_date, end_date,start_date,end_date))
        store_data = cr.fetchall()
        for store_data_id in store_data:
            actual_store_rev = actual_store_rev + store_data_id[0]
            if store_data_id[1] == 'accessory':
                store_acc_rev = store_data_id[2]
                store_acc_count = store_data_id[3]
        tot_store_rev = actual_store_rev - deact_rev
        tot_store_box = actual_store_box - deact_box
        store_vals = {  'actual_store_rev':actual_store_rev,
                        'actual_store_box':actual_store_box,
                        'tot_store_rev':tot_store_rev,
                        'tot_store_box':tot_store_box,
                        'store_acc_rev':store_acc_rev,
                        'store_acc_count':store_acc_count
                    }
        return store_vals

    def _calculate_team_voc_commission(self, cr, uid, comm_voc_record_id, tot_rev, voc_achieved, emp_model_id, context=None):
        voc_vals = {}
        voc_vals = {
                    'voc_payout':0.00,
                    'voc_achieved':0.00,
                    'voc_target':0.00,
                    'voc_string':str("")
                    }
        voc_payout = 0.00
        comm_voc_master = self.pool.get('comm.voc.commission')
        comm_voc_master_data = comm_voc_master.browse(cr, uid, comm_voc_record_id[0])
        voc_multi_bracket = comm_voc_master_data.voc_multi_bracket
        voc_achieved = round(voc_achieved, 2)
        count = 0
        voc_goal = 0
        if voc_multi_bracket:
            for voc_multi_bracket_data in voc_multi_bracket:
                from_voc_value = voc_multi_bracket_data.from_voc_value
                to_voc_value = voc_multi_bracket_data.to_voc_value
                pay_percent = voc_multi_bracket_data.pay_percent
                pay_flat = voc_multi_bracket_data.pay_flat
                if to_voc_value != 0.00:
                    if voc_achieved >= from_voc_value and voc_achieved <= to_voc_value:
                        if pay_flat:
                            voc_payout = pay_flat
                        elif pay_percent:
                            voc_payout = (tot_rev * pay_percent)/100
                else:
                    if voc_achieved >= from_voc_value:
                        if pay_flat:
                            voc_payout = pay_flat
                        elif pay_percent:
                            voc_payout = (tot_rev * pay_percent)/100
                count = count + 1
                if (voc_payout > 0.00) or (count == len(voc_multi_bracket)):
                    voc_goal = from_voc_value
                    break
            if pay_flat:
                voc_vals['voc_string'] += str("$ %s"%(pay_flat))
            elif pay_percent:
                voc_vals['voc_string'] += ("%s"%(pay_percent))
                voc_vals['voc_string'] += (" %")
                if emp_model_id == 'rsa':
                    voc_vals['voc_string'] += (" of RSA Revenue")
                elif emp_model_id == 'stl':
                    voc_vals['voc_string'] += (" of STL Revenue")
                elif emp_model_id == 'mid':
                    voc_vals['voc_string'] += (" of MID Revenue")
                elif emp_model_id == 'rsm':
                    voc_vals['voc_string'] += (" of RSM Revenue")
                elif emp_model_id == 'mm':
                    voc_vals['voc_string'] += (" of MM Revenue")
                elif emp_model_id == 'dos':
                    voc_vals['voc_string'] += (" of DOS Revenue")
        voc_vals = {
                    'voc_payout':voc_payout,
                    'voc_achieved':voc_achieved,
                    'voc_target':voc_goal,
                    'voc_string':voc_vals['voc_string']
                    }
        return voc_vals

    def _calculate_rph_commission(self,cr,uid,comm_rph_emp_record_id,tot_rev,tot_hour,labor_budget,rph_import_goal,field_name,emp_id,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        rph_vals = {}
        rph_vals = {
                    'rsa_rph_payout':0.00,
                    'rsa_rph_target':0.00,
                    'labor_prod_target':str(""),
                    'rsa_rph_payout_tier':str("")
                    }
        rsa_rph_payout = 0.00
        comm_rph_master = self.pool.get('comm.rph.commission')
        comm_rph_emp_record_data = comm_rph_master.browse(cr, uid, comm_rph_emp_record_id[0])
        comm_rph_multi_bracket = comm_rph_emp_record_data.comm_rph_multi_bracket
        count = 0
        rsa_rph_target = 0
        var_name = 'df'
        if comm_rph_multi_bracket:
            for comm_rph_multi_bracket_data in comm_rph_multi_bracket:
                plus_3gb_business_rule_id = comm_rph_multi_bracket_data.att_business_rule
                if plus_3gb_business_rule_id:
                    dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    plus_3gb_business_rule_pos = plus_3gb_business_rule_id.is_postpaid
                    plus_3gb_business_rule_upg = plus_3gb_business_rule_id.is_upgrade
                    plus_3gb_business_rule_pre = plus_3gb_business_rule_id.is_prepaid
                    plus_3gb_business_rule_fea = plus_3gb_business_rule_id.is_feature
                    plus_3gb_business_rule_acc = plus_3gb_business_rule_id.is_acc
                    from_condition = str('')
                    if plus_3gb_business_rule_pos:
                        from_condition += str('select id,product_id,dsr_rev_gen,dsr_trans_type,true as created_feature, 0.00 as dsr_acc_mrc,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0 as dsr_quantity,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type from wireless_dsr_postpaid_line union all ')
                    if plus_3gb_business_rule_upg:
                        from_condition += str('select id,product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type from wireless_dsr_upgrade_line union all ')
                    if plus_3gb_business_rule_pre:
                        from_condition += str('select id,product_id,dsr_rev_gen,dsr_trans_type,created_feature, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description,dsr_product_code_type from wireless_dsr_prepaid_line union all ')
                    if plus_3gb_business_rule_fea:
                        from_condition += str('select id,feature_product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type from wireless_dsr_feature_line union all ')
                    if plus_3gb_business_rule_acc:
                        from_condition += str('select id,product_id,dsr_rev_gen,dsr_trans_type,true,dsr_acc_mrc,false as prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,dsr_quantity,pseudo_date,dsr_emp_type,null as dsr_credit_class,null as dsr_product_code,null as dsr_product_code_type from wireless_dsr_acc_line union all ')
                    from_condition = from_condition[:-10]
                    cr.execute('''select sum(dsr_rev_gen) from 
                        ('''+from_condition+''')
                        as df where df.'''+field_name+''' = %s 
                        and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                        and df.state = 'done'
                        and df.prm_dsr_smd = false'''
                        +dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                    actual_rev_data = cr.fetchall()
                    actual_rev = actual_rev_data[0][0]
                    if not actual_rev:
                        actual_rev = 0.00
                    if tot_hour > 0.00:
                        rsa_rph_target = actual_rev/tot_hour
                    rsa_rph_target = round(rsa_rph_target, 2)
                from_rph_value = comm_rph_multi_bracket_data.from_rph_value
                upto_rph_value = comm_rph_multi_bracket_data.upto_rph_value
                pay_percent_rev = comm_rph_multi_bracket_data.pay_percent_rev
                from_labor_budget = comm_rph_multi_bracket_data.from_labor_budget
                to_labor_budget = comm_rph_multi_bracket_data.to_labor_budget
                pay_flat_amnt = comm_rph_multi_bracket_data.pay_flat_amnt
                hit_rph_target = comm_rph_multi_bracket_data.hit_rph_target
                rph_target_percent = comm_rph_multi_bracket_data.rph_target_percent
                if hit_rph_target:
                    if rph_target_percent:
                        rph_import_goal_new = (rph_import_goal * rph_target_percent)/100
                        if rsa_rph_target >= rph_import_goal_new:
                            if pay_flat_amnt:
                                rsa_rph_payout = pay_flat_amnt
                            elif pay_percent_rev:
                                rsa_rph_payout = (tot_rev * pay_percent_rev)/100
                    else:
                        if rsa_rph_target >= rph_import_goal:
                            if pay_flat_amnt:
                                rsa_rph_payout = pay_flat_amnt
                            elif pay_percent_rev:
                                rsa_rph_payout = (tot_rev * pay_percent_rev)/100
                elif from_labor_budget > 0.00:
                    if to_labor_budget != 0.00:
                        if upto_rph_value != 0.00:
                            if (rsa_rph_target >= from_rph_value) and (rsa_rph_target <= upto_rph_value) and (labor_budget >= from_labor_budget) and (labor_budget <= to_labor_budget):
                                if pay_flat_amnt:
                                    rsa_rph_payout = pay_flat_amnt
                                elif pay_percent_rev:
                                    rsa_rph_payout = (tot_rev * pay_percent_rev)/100
                        else:
                            if (rsa_rph_target >= from_rph_value) and (labor_budget >= from_labor_budget) and (labor_budget <= to_labor_budget):
                                if pay_flat_amnt:
                                    rsa_rph_payout = pay_flat_amnt
                                elif pay_percent_rev:
                                    rsa_rph_payout = (tot_rev * pay_percent_rev)/100
                    else:
                        if upto_rph_value != 0.00:
                            if (rsa_rph_target >= from_rph_value) and (rsa_rph_target <= upto_rph_value) and (labor_budget >= from_labor_budget):
                                if pay_flat_amnt:
                                    rsa_rph_payout = pay_flat_amnt
                                elif pay_percent_rev:
                                    rsa_rph_payout = (tot_rev * pay_percent_rev)/100
                        else:
                            if (rsa_rph_target >= from_rph_value) and (labor_budget >= from_labor_budget):
                                if pay_flat_amnt:
                                    rsa_rph_payout = pay_flat_amnt
                                elif pay_percent_rev:
                                    rsa_rph_payout = (tot_rev * pay_percent_rev)/100
                else:
                    if upto_rph_value != 0.00:
                        if (rsa_rph_target >= from_rph_value) and (rsa_rph_target <= upto_rph_value):
                            if pay_flat_amnt:
                                rsa_rph_payout = pay_flat_amnt
                            elif pay_percent_rev:
                                rsa_rph_payout = (tot_rev * pay_percent_rev)/100
                    else:
                        if rsa_rph_target >= from_rph_value:
                            if pay_flat_amnt:
                                rsa_rph_payout = pay_flat_amnt
                            elif pay_percent_rev:                
                                rsa_rph_payout = (tot_rev * pay_percent_rev)/100
                count = count + 1
                if (rsa_rph_payout > 0.00) or (count == len(comm_rph_multi_bracket)):    
                    rph_vals['labor_prod_target'] += str("%s, "%(from_rph_value))
                    if pay_percent_rev:
                        rph_vals['rsa_rph_payout_tier'] += str("%s"%(pay_percent_rev))
                        rph_vals['rsa_rph_payout_tier'] += str(" %")
                    elif pay_flat_amnt:
                        rph_vals['rsa_rph_payout_tier'] += str("$ %s"%(pay_flat_amnt))
                    # rph_vals['labor_prod_target'] += str("%s, "%(from_labor_budget))
                    break
            if rph_vals['labor_prod_target'] != "":
                rph_vals['labor_prod_target'] = rph_vals['labor_prod_target'][:-2]
        rph_vals = {
                    'rsa_rph_payout':rsa_rph_payout,
                    'rsa_rph_target':rsa_rph_target,
                    'labor_prod_target':rph_vals['labor_prod_target'],
                    'rsa_rph_payout_tier':rph_vals['rsa_rph_payout_tier']
                    }
        return rph_vals

    def _calculate_rev_goal_att(self,cr,uid,field_name,emp_id,comm_rev_att_emp_ids,emp_rev_goal,tot_rev,start_date,end_date,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        rev_att_vals = {}
        rev_att_vals = {
                        'rev_goal_att_goals':0.00,
                        'rev_goal_att_actual':0.00,
                        'rev_goal_att_percent':0.00,
                        'rev_goal_att_payout':0.00
                    }
        rev_goal_att_payout = 0.00
        comm_rev_master = self.pool.get('comm.revenue.goal.attainment.formula')
        comm_rev_emp_record_data = comm_rev_master.browse(cr, uid, comm_rev_att_emp_ids[0])
        comm_rev_multi_bracket = comm_rev_emp_record_data.comm_fixed_amount_on_goal
        count = 0
        rev_goal_att_actual = 0
        rev_goal_att_percent = 0
        rev_att_vals['rev_goal_att_goals'] = emp_rev_goal
        var_name = 'df'
        if comm_rev_multi_bracket:
            for comm_rev_multi_bracket_data in comm_rev_multi_bracket:
                plus_3gb_business_rule_id = comm_rev_multi_bracket_data.att_business_rule
                if plus_3gb_business_rule_id:
                    dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,plus_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                    plus_3gb_business_rule_pos = plus_3gb_business_rule_id.is_postpaid
                    plus_3gb_business_rule_upg = plus_3gb_business_rule_id.is_upgrade
                    plus_3gb_business_rule_pre = plus_3gb_business_rule_id.is_prepaid
                    plus_3gb_business_rule_fea = plus_3gb_business_rule_id.is_feature
                    plus_3gb_business_rule_acc = plus_3gb_business_rule_id.is_acc
                    from_condition = str('')
                    if plus_3gb_business_rule_pos:
                        from_condition += str('select id,product_id,dsr_rev_gen,dsr_trans_type,true as created_feature, 0.00 as dsr_acc_mrc,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0 as dsr_quantity,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type from wireless_dsr_postpaid_line union all ')
                    if plus_3gb_business_rule_upg:
                        from_condition += str('select id,product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type from wireless_dsr_upgrade_line union all ')
                    if plus_3gb_business_rule_pre:
                        from_condition += str('select id,product_id,dsr_rev_gen,dsr_trans_type,created_feature, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description,dsr_product_code_type from wireless_dsr_prepaid_line union all ')
                    if plus_3gb_business_rule_fea:
                        from_condition += str('select id,feature_product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type from wireless_dsr_feature_line union all ')
                    if plus_3gb_business_rule_acc:
                        from_condition += str('select id,product_id,dsr_rev_gen,dsr_trans_type,true,dsr_acc_mrc,false as prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,dsr_quantity,pseudo_date,dsr_emp_type,null as dsr_credit_class,null as dsr_product_code,null as dsr_product_code_type from wireless_dsr_acc_line union all ')
                    from_condition = from_condition[:-10]
                    cr.execute('''select sum(dsr_rev_gen) from 
                        ('''+from_condition+''')
                        as df where df.'''+field_name+''' = %s 
                        and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                        and df.state = 'done'
                        and df.prm_dsr_smd = false'''
                        +dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                    actual_rev_data = cr.fetchall()
                    rev_goal_att_actual = actual_rev_data[0][0]
                    if not rev_goal_att_actual:
                        rev_goal_att_actual = 0.00
                    if rev_att_vals['rev_goal_att_goals'] > 0.00:
                        rev_goal_att_percent = (rev_goal_att_actual * 100)/ rev_att_vals['rev_goal_att_goals']
                    rev_goal_att_percent = round(rev_goal_att_percent, 2)
                comm_min_percent = comm_rev_multi_bracket_data.comm_min_percent
                comm_max_percent = comm_rev_multi_bracket_data.comm_max_percent
                comm_fixed_amount = comm_rev_multi_bracket_data.comm_fixed_amount
                comm_amnt_goal_mul = comm_rev_multi_bracket_data.comm_amnt_goal_mul
                pay_on_rev = comm_rev_multi_bracket_data.pay_on_rev
                if comm_max_percent != 0.00:
                    if (rev_goal_att_percent >= comm_min_percent) and (rev_goal_att_percent <= comm_max_percent):
                        if comm_fixed_amount:
                            rev_goal_att_payout = comm_fixed_amount
                        elif comm_amnt_goal_mul:
                            rev_goal_att_payout = (comm_amnt_goal_mul * rev_goal_att_percent)/100
                        elif pay_on_rev:
                            rev_goal_att_payout = (tot_rev * pay_on_rev)/100
                else:
                    if (rev_goal_att_percent >= comm_min_percent):
                        if comm_fixed_amount:
                            rev_goal_att_payout = comm_fixed_amount
                        elif comm_amnt_goal_mul:
                            rev_goal_att_payout = (comm_amnt_goal_mul * rev_goal_att_percent)/100
                        elif pay_on_rev:
                            rev_goal_att_payout = (tot_rev * pay_on_rev)/100
                count = count + 1
                if (rev_goal_att_payout > 0.00) or (count == len(comm_rev_multi_bracket)):
                    break
        rev_att_vals = {
                        'rev_goal_att_goals':rev_att_vals['rev_goal_att_goals'],
                        'rev_goal_att_actual':rev_goal_att_actual,
                        'rev_goal_att_percent':rev_goal_att_percent,
                        'rev_goal_att_payout':rev_goal_att_payout
                    }
        return rev_att_vals

    def _calculate_turnover(self,cr,uid,tot_rev,turnover_actual_count,comm_turnover_emp_ids):
        rev_att_vals = {}
        rev_att_vals = {
                        'turnover_payout':0.00
                    }
        rev_goal_att_payout = 0.00
        comm_rev_master = self.pool.get('comm.turnover.formula')
        comm_rev_emp_record_data = comm_rev_master.browse(cr, uid, comm_turnover_emp_ids[0])
        comm_rev_multi_bracket = comm_rev_emp_record_data.comm_fixed_amount_on_goal
        count = 0
        if comm_rev_multi_bracket:
            for comm_rev_multi_bracket_data in comm_rev_multi_bracket:
                comm_min_percent = comm_rev_multi_bracket_data.comm_min_percent
                comm_max_percent = comm_rev_multi_bracket_data.comm_max_percent
                comm_fixed_amount = comm_rev_multi_bracket_data.comm_fixed_amount
                pay_on_rev = comm_rev_multi_bracket_data.pay_on_rev
                if comm_max_percent != 0.00:
                    if (turnover_actual_count >= comm_min_percent) and (turnover_actual_count <= comm_max_percent):
                        if comm_fixed_amount:
                            rev_goal_att_payout = comm_fixed_amount
                        elif pay_on_rev:
                            rev_goal_att_payout = (tot_rev * pay_on_rev)/100
                else:
                    if (turnover_actual_count >= comm_min_percent):
                        if comm_fixed_amount:
                            rev_goal_att_payout = comm_fixed_amount
                        elif pay_on_rev:
                            rev_goal_att_payout = (tot_rev * pay_on_rev)/100
                count = count + 1
                if (rev_goal_att_payout > 0.00) or (count == len(comm_rev_multi_bracket)):
                    break
        rev_att_vals = {
                        'turnover_payout':rev_goal_att_payout
                    }
        return rev_att_vals

    def _calculate_profitability_commission(self, cr, uid, store_voc, field_name, store_id, comm_profit_store_search_ids, profit_start_date, profit_end_date, profit_target):
        profit_vals = {}
        profit_vals = {
                        'store_payout':0.00,
                        'store_actual_profit':0.00,
                        'store_income':0.00
        }
        store_payout = 0.00
        p_l_percent_actual_profit = 0.00
        p_l_num_tot_value = 0.00
        store_actual_profit = 0.00
        store_income = 0.00
        field_condition = str('')
        if field_name != 'company_id':
            field_condition += "and %s = %s"%(field_name,store_id)
        comm_obj = self.pool.get('comm.profitability.payout')
        comm_data = comm_obj.browse(cr, uid, comm_profit_store_search_ids[0])
        comm_profit_multi_bracket = comm_data.comm_profit_multi_bracket
        count = 0
        if comm_profit_multi_bracket:
            for comm_profit_multi_bracket_data in comm_profit_multi_bracket:
                att_condition_percent = comm_profit_multi_bracket_data.att_condition_percent
                to_condition_percent = comm_profit_multi_bracket_data.to_condition_percent
                pay_on_rev = comm_profit_multi_bracket_data.pay_on_rev
                flat_pay = comm_profit_multi_bracket_data.pay_flat_amnt
                hit_goal_target = comm_profit_multi_bracket_data.hit_goal_target
                p_l_num_tot_value = 0.00
                p_l_den_tot_value = 0.00
                p_l_percent_actual_profit = 0.00
                account_condition_config_ids = comm_profit_multi_bracket_data.att_business_rule and comm_profit_multi_bracket_data.att_business_rule.account_config_ids or False
                if account_condition_config_ids:
                    for account_config_ids_data in account_condition_config_ids:
                        p_l_account_id = account_config_ids_data.p_l_account_id.id
                        operator = account_config_ids_data.operator.code
                        cr.execute('''select sum(value) from account_store_pl where account_id=%s '''+field_condition+''' 
                            and start_date >= %s and end_date <= %s''',(p_l_account_id,profit_start_date,profit_end_date))
                        p_l_value_data = cr.fetchall()
                        p_l_acc_value = p_l_value_data[0][0]
                        if not p_l_acc_value:
                            p_l_acc_value = 0.00
                        if operator == '+':
                            p_l_num_tot_value = p_l_num_tot_value + p_l_acc_value
                        elif operator == '-':
                            p_l_num_tot_value = p_l_num_tot_value - p_l_acc_value
                account_condition_config_ids_2 = comm_profit_multi_bracket_data.att_business_rule and comm_profit_multi_bracket_data.att_business_rule.account_config_ids_2 or False
                if account_condition_config_ids_2:
                    for account_config_ids_data in account_condition_config_ids_2:
                        p_l_account_id = account_config_ids_data.p_l_account_id.id
                        operator = account_config_ids_data.operator.code
                        cr.execute('''select sum(value) from account_store_pl where account_id=%s '''+field_condition+''' 
                            and start_date >= %s and end_date <= %s''',(p_l_account_id,profit_start_date,profit_end_date))
                        p_l_value_data = cr.fetchall()
                        p_l_acc_value = p_l_value_data[0][0]
                        if not p_l_acc_value:
                            p_l_acc_value = 0.00
                        if operator == '+':
                            p_l_den_tot_value = p_l_den_tot_value + p_l_acc_value
                        elif operator == '-':
                            p_l_den_tot_value = p_l_den_tot_value - p_l_acc_value
                if hit_goal_target and profit_target:#####both the hit goal target and the profit target should be greater than 0
                    p_l_percent_actual_profit = (p_l_num_tot_value * 100 / profit_target)
                elif p_l_den_tot_value > 0.00:
                    p_l_percent_actual_profit = (p_l_num_tot_value * 100 / p_l_den_tot_value)
                p_l_percent_actual_profit = round(p_l_percent_actual_profit, 2)
                account_condition_config_ids = comm_profit_multi_bracket_data.payout_business_rule and comm_profit_multi_bracket_data.payout_business_rule.account_config_ids or False
                if account_condition_config_ids:
                    p_l_num_tot_value = 0.00
                    for account_config_ids_data in account_condition_config_ids:
                        p_l_account_id = account_config_ids_data.p_l_account_id.id
                        operator = account_config_ids_data.operator.code
                        cr.execute('''select sum(value) from account_store_pl where account_id=%s '''+field_condition+''' 
                            and start_date >= %s and end_date <= %s''',(p_l_account_id,profit_start_date,profit_end_date))
                        p_l_value_data = cr.fetchall()
                        p_l_acc_value = p_l_value_data[0][0]
                        if not p_l_acc_value:
                            p_l_acc_value = 0.00
                        if operator == '+':
                            p_l_num_tot_value = p_l_num_tot_value + p_l_acc_value
                        elif operator == '-':
                            p_l_num_tot_value = p_l_num_tot_value - p_l_acc_value
                if to_condition_percent == 0 and att_condition_percent == 0:
                    if pay_on_rev > 0.00 and hit_goal_target:
                        store_payout = store_payout + ((p_l_num_tot_value - profit_target) * pay_on_rev)/100
                    elif pay_on_rev > 0.00:
                        store_payout = store_payout + (p_l_num_tot_value * pay_on_rev)/100
                    if flat_pay > 0.00:
                        store_payout = store_payout + flat_pay
                elif to_condition_percent != 0:
                    if p_l_percent_actual_profit >= att_condition_percent and p_l_percent_actual_profit <= to_condition_percent:
                        if pay_on_rev > 0.00 and hit_goal_target:
                            store_payout = store_payout + ((p_l_num_tot_value - profit_target) * pay_on_rev)/100
                        elif pay_on_rev > 0.00:
                            store_payout = store_payout + (p_l_num_tot_value * pay_on_rev)/100
                        if flat_pay > 0.00:
                            store_payout = store_payout + flat_pay
                else:
                    if p_l_percent_actual_profit >= att_condition_percent:
                        if pay_on_rev > 0.00 and hit_goal_target:
                            store_payout = store_payout + ((p_l_num_tot_value - profit_target) * pay_on_rev)/100
                        elif pay_on_rev > 0.00:
                            store_payout = store_payout + (p_l_num_tot_value * pay_on_rev)/100
                        if flat_pay > 0.00:
                            store_payout = store_payout + flat_pay
                count = count + 1
                if (store_payout > 0.00) or (count == len(comm_profit_multi_bracket)):
                    store_actual_profit = p_l_num_tot_value
                    store_income = p_l_percent_actual_profit
                    break
        is_voc = comm_data.is_voc
        if is_voc:    
            voc_operand = comm_data.voc_operand
            voc_factor = comm_data.voc_factor
            percent_pay_effect = comm_data.percent_pay_effect
            flat_pay_effect = comm_data.flat_pay_effect
            if voc_operand == 'gt':
                if store_voc > voc_factor:
                    if percent_pay_effect > 0.00:
                        store_payout = store_payout + ((store_payout * percent_pay_effect)/100)
                    elif flat_pay_effect > 0.00:
                        store_payout = store_payout + flat_pay_effect
            elif voc_operand == 'lt':
                if store_voc < voc_factor:
                    if percent_pay_effect > 0.00:
                        store_payout = store_payout + ((store_payout * percent_pay_effect)/100)
                    elif flat_pay_effect > 0.00:
                        store_payout = store_payout + flat_pay_effect
            elif voc_operand == 'gte':
                if store_voc >= voc_factor:
                    if percent_pay_effect > 0.00:
                        store_payout = store_payout + ((store_payout * percent_pay_effect)/100)
                    elif flat_pay_effect > 0.00:
                        store_payout = store_payout + flat_pay_effect
            elif voc_operand == 'lte':
                if store_voc <= voc_factor:
                    if percent_pay_effect > 0.00:
                        store_payout = store_payout + ((store_payout * percent_pay_effect)/100)
                    elif flat_pay_effect > 0.00:
                        store_payout = store_payout + flat_pay_effect
            elif voc_operand == 'eq':
                if store_voc == voc_factor:
                    if percent_pay_effect > 0.00:
                        store_payout = store_payout + ((store_payout * percent_pay_effect)/100)
                    elif flat_pay_effect > 0.00:
                        store_payout = store_payout + flat_pay_effect
        profit_vals = {
                        'store_income':store_income,
                        'store_actual_profit':store_actual_profit,
                        'store_payout':store_payout
        }
        return profit_vals

    def _calculate_tbc_commission(self, cr, uid, spiff_sa_tot_box_rule_search, store_actual_box, sto_no_of_exit, field_name, start_date, end_date, emp_id, business_box_rule_ids, tot_rev, emp_model_id, traffic_stores, traffic_dates,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        tbc_vals = {}
        hr_obj = self.pool.get('hr.employee')
        store_obj = self.pool.get('sap.store')
        dealer_obj = self.pool.get('dealer.class')
        split_goal_obj = self.pool.get('spliting.goals')
        date_monthrange = datetime.strptime(start_date, '%Y-%m-%d').date()
        tbc_vals = {
                    'spiff_stl_tot_box_conv_percent':str(""),
                    'spiff_stl_box_count':str(""),
                    'spiff_stl_tot_box_rule_amount':0.00,
                    'spiff_stl_tot_box_rule_percent':str(""),
                    'tot_box_payout_tier':str(""),
                    'rsa_tbc_string':str("")
        }
        if field_name == 'employee_id':
            field_name = 'store_id'
            field_name_2 = 'employee_id'
            store_data = hr_obj.browse(cr, uid, emp_id).user_id.sap_id
            store_id = store_data.id
            split_search_ids = split_goal_obj.search(cr, uid, [('employee_id','=',emp_id),('start_date','=',start_date),('end_date','=',end_date)])
            if split_search_ids:
                store_data = split_goal_obj.browse(cr, uid, split_search_ids[0]).store_id
                store_id = store_data.id
            cr.execute("select id from dealer_class where dealer_id = %s and end_date >= %s and start_date <= %s order by end_date",(emp_id,start_date,end_date))
            dealer_obj_search_multi = map(lambda x: x[0], cr.fetchall())
            if not dealer_obj_search_multi:
                dealer_obj_search_multi = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',start_date),('end_date','>=',end_date)])
            for dealer_obj_search_multi_id in dealer_obj_search_multi:
                store_data = dealer_obj.browse(cr, uid, dealer_obj_search_multi_id).store_name
                store_id = store_data.id
            store_emp_search = store_obj.search(cr, uid, [('store_mgr_id','=',emp_id)])
            if store_emp_search:
                store_data = store_obj.browse(cr, uid, store_emp_search[0])
                store_id = store_data.id
        else:
            field_name_2 = field_name
            store_id = emp_id
        spiff_stl_tot_box_rule_amount = 0.00
        spiff_stl_tot_box_conv_percent = 0.00
        spiff_stl_box_count = 0.00
        att_condition_percent = 0.00
        spiff_tot_box_rule = self.pool.get('spiff.store.total.box.conversion')
        spiff_stl_tot_box_rule_data = spiff_tot_box_rule.browse(cr, uid, spiff_sa_tot_box_rule_search[0])
        spiff_business_class = spiff_stl_tot_box_rule_data.spiff_business_class
        count = 0
        var_name = str('test')
        if len(traffic_stores) == 1:
            tbc_new_store_cond = str(" and test.store_id = '%s' "%(traffic_stores[0]))
        elif traffic_stores:
            tbc_new_store_cond = str(" and test.store_id in %s "%(tuple(traffic_stores),))
        else:
            tbc_new_store_cond = str('')
        if len(traffic_dates) == 1:
            tbc_new_date_cond = str(" and test.dsr_act_date = '%s' "%(traffic_dates[0]))
        elif traffic_dates:
            tbc_new_date_cond = str(" and test.dsr_act_date in %s "%(tuple(traffic_dates),))
        else:
            tbc_new_date_cond = str('')
        for spiff_business_class_data in spiff_business_class:
            att_business_rule = spiff_business_class_data.att_business_rule                
            pay_on_rev = spiff_business_class_data.pay_on_rev
            pay_per_att = spiff_business_class_data.pay_per_att
            flat_pay = spiff_business_class_data.pay_flat_amnt
            if att_business_rule:
                from_condition = str('')
                spiff_stl_tot_box_conv_percent = 0.00
                spiff_stl_box_count = 0.00
                box_is_postpaid = att_business_rule.is_postpaid
                box_is_upgrade = att_business_rule.is_upgrade
                box_is_prepaid = att_business_rule.is_prepaid
                if box_is_postpaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_postpaid_line union all ''')
                if box_is_prepaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description
    from wireless_dsr_prepaid_line union all ''')
                if box_is_upgrade:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_upgrade_line union all ''')
                from_condition = from_condition[:-10]
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,att_business_rule.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_rule_tuple = []
                for sub_rule in att_business_rule.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''test.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(test.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(test.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or test.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and test.dsr_phone_purchase_type = '%s'''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and test.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_tuple[4]:
                            condition_string += str(''' and test.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                cr.execute('''select dsr_trans_type
,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
+sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
from 
('''+from_condition+''') as test
where test.''' + field_name + ''' = %s'''+tbc_new_store_cond+'''
and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
'''+tbc_new_date_cond+'''
and test.state = 'done'
and test.prm_dsr_smd = false
'''+condition_string+
    dsr_exclude_condition+ '''
group by test.dsr_trans_type
order by test.dsr_trans_type asc''',(store_id,start_date,end_date,start_date,end_date))
                box_data = cr.fetchall()
                for emp_data_id in box_data:
                    spiff_stl_box_count = spiff_stl_box_count + emp_data_id[1]
                if sto_no_of_exit > 0.00:
                    spiff_stl_tot_box_conv_percent = (spiff_stl_box_count * 100) / sto_no_of_exit
                spiff_stl_tot_box_conv_percent = round(spiff_stl_tot_box_conv_percent,2)
            payout_business_rule = spiff_business_class_data.payout_business_rule
            if payout_business_rule:
                spiff_stl_box_count = 0.00
                from_condition = str('')
                box_is_postpaid = payout_business_rule.is_postpaid
                box_is_upgrade = payout_business_rule.is_upgrade
                box_is_prepaid = payout_business_rule.is_prepaid
                if box_is_postpaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_postpaid_line union all ''')
                if box_is_prepaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description
    from wireless_dsr_prepaid_line union all ''')
                if box_is_upgrade:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_upgrade_line union all ''')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,payout_business_rule.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                for sub_rule in payout_business_rule.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''test.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(test.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(test.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or test.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and test.dsr_phone_purchase_type = '%s'''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and test.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_data[4]:
                            condition_string += str(''' and test.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                cr.execute('''select dsr_trans_type
,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
+sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
from 
('''+from_condition+''') as test
where test.''' + field_name_2 + ''' = %s'''+tbc_new_store_cond+'''
and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
'''+tbc_new_date_cond+'''
and test.state = 'done'
and test.prm_dsr_smd = false
'''+condition_string+
    dsr_exclude_condition+ '''
group by test.dsr_trans_type
order by test.dsr_trans_type asc''',(emp_id,start_date,end_date,start_date,end_date))
                box_data = cr.fetchall()
                for emp_data_id in box_data:
                    spiff_stl_box_count = spiff_stl_box_count + emp_data_id[1]
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            if att_condition_percent:
                if to_condition_percent != 0:
                    if spiff_stl_tot_box_conv_percent >= att_condition_percent and spiff_stl_tot_box_conv_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + (spiff_stl_box_count * pay_per_att)
                        elif pay_on_rev > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + flat_pay
                else:
                    if spiff_stl_tot_box_conv_percent >= att_condition_percent:
                        if pay_per_att > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + (spiff_stl_box_count * pay_per_att)
                        elif pay_on_rev > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + flat_pay
            else:
                if pay_per_att > 0.00:
                    tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + (spiff_stl_box_count * pay_per_att)
                elif pay_on_rev > 0.00:
                    tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + ((tot_rev * pay_on_rev)/100)
                elif flat_pay > 0.00:
                    tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + flat_pay
            count = count + 1
            if (tbc_vals['spiff_stl_tot_box_rule_amount'] > 0.00) or (count == len(spiff_business_class)):
                spiff_stl_tot_box_conv_percent = round(spiff_stl_tot_box_conv_percent,2)
                att_condition_percent = round(att_condition_percent,2)
                spiff_stl_box_count = round(spiff_stl_box_count,2)
                if pay_per_att:
                    tbc_vals['tot_box_payout_tier'] += str("$ %s per"%(pay_per_att))
                    tbc_vals['rsa_tbc_string'] += ("$ %s per"%(pay_per_att))
                elif pay_on_rev:
                    tbc_vals['tot_box_payout_tier'] += str("%s"%(pay_on_rev))
                    tbc_vals['tot_box_payout_tier'] += str(" %")
                    tbc_vals['rsa_tbc_string'] += ("%s"%(pay_on_rev))
                    tbc_vals['rsa_tbc_string'] += (" %")
                    if emp_model_id == 'rsa':
                        tbc_vals['rsa_tbc_string'] += (" of RSA Revenue")
                    elif emp_model_id == 'stl':
                        tbc_vals['rsa_tbc_string'] += (" of STL Revenue")
                    elif emp_model_id == 'mid':
                        tbc_vals['rsa_tbc_string'] += (" of MID Revenue")
                    elif emp_model_id == 'rsm':
                        tbc_vals['rsa_tbc_string'] += (" of RSM Revenue")
                    elif emp_model_id == 'mm':
                        tbc_vals['rsa_tbc_string'] += (" of MM Revenue")
                    elif emp_model_id == 'dos':
                        tbc_vals['rsa_tbc_string'] += (" of DOS Revenue")
                elif flat_pay:
                    tbc_vals['tot_box_payout_tier'] += str("$ %s"%(flat_pay))
                    tbc_vals['rsa_tbc_string'] += ("$ %s"%(flat_pay))
                tbc_vals['spiff_stl_tot_box_conv_percent'] += str("%s, "%(spiff_stl_tot_box_conv_percent,))
                tbc_vals['spiff_stl_tot_box_rule_percent'] += str("%s, "%(att_condition_percent))
                tbc_vals['spiff_stl_box_count'] += str("%s, "%(spiff_stl_box_count,))
                break
        if tbc_vals['spiff_stl_box_count'] != "":
            tbc_vals['spiff_stl_box_count'] = tbc_vals['spiff_stl_box_count'][:-2]
        if tbc_vals['spiff_stl_tot_box_rule_percent'] != "":
            tbc_vals['spiff_stl_tot_box_rule_percent'] = tbc_vals['spiff_stl_tot_box_rule_percent'][:-2]
        if tbc_vals['spiff_stl_tot_box_conv_percent'] != "":
            tbc_vals['spiff_stl_tot_box_conv_percent'] = tbc_vals['spiff_stl_tot_box_conv_percent'][:-2]
        return tbc_vals

    def _calculate_apk_calc(self, cr, uid, spiff_emp_apk_ids, field_name, emp_id, start_date, end_date, emp_box_goal, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        apk_vals = {
                    'avg_apk':str(""),
                    'spiff_per_box_acc_sold':str(""),
                    'apk_payout':0.00,
                    'apk_actual_count':str(""),
                    'apk_comm_string':str("")
        }
        avg_apk = 0.00
        apk_box_condition_percent = 0.00
        apk_actual_count = 0.00
        count = 0
        apk_obj = self.pool.get('spiff.apk')
        spiff_apk_data = apk_obj.browse(cr, uid, spiff_emp_apk_ids[0])
        var_name = 'test'
        for spiff_business_class_data in spiff_apk_data.spiff_business_class:
            tot_box = 0
            apk_rev = 0
            apk_count = 0
            apk_br_rule = spiff_business_class_data.att_business_rule
            apk_rev_goal = spiff_business_class_data.apk_goal
            apk_count_goal = spiff_business_class_data.apk_count_goal
            spiff_on_rev = spiff_business_class_data.pay_on_rev
            spiff_amount = spiff_business_class_data.pay_flat_amnt
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            if apk_br_rule:
                box_dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,apk_br_rule.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                acc_business_rule_pos = apk_br_rule.is_postpaid
                acc_business_rule_upg = apk_br_rule.is_upgrade
                acc_business_rule_pre = apk_br_rule.is_prepaid
                acc_business_rule_acc = apk_br_rule.is_acc
                if acc_business_rule_acc:
                    cr.execute('''select sum(test.dsr_quantity),sum(test.dsr_rev_gen)
                        from (select id,product_id,dsr_rev_gen,dsr_trans_type,true, dsr_acc_mrc,false as prm_dsr_smd,employee_id
                            ,store_id,market_id,region_id,dsr_act_date,state,dsr_quantity,pseudo_date,dsr_emp_type
                            ,null::integer as dsr_credit_class,null::integer as dsr_product_code,null::integer as dsr_product_code_type
                        from wireless_dsr_acc_line) as test
                        where test.''' + field_name + ''' = %s
                        and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
                        and test.state = 'done' '''+
                        box_dsr_exclude_condition+''' ''',(emp_id,start_date,end_date,start_date,end_date))
                    apk_data = cr.fetchall()
                    apk_rev = apk_data[0][1]
                    apk_count = apk_data[0][0]
                    if not apk_rev:
                        apk_rev = 0
                    if not apk_count:
                        apk_count = 0
                from_box_condition = str('')
                if acc_business_rule_pos:
                    from_box_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_postpaid_line union all ''')
                if acc_business_rule_pre:
                    from_box_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description
    from wireless_dsr_prepaid_line union all ''')
                if acc_business_rule_upg:
                    from_box_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_upgrade_line union all ''')
                from_box_condition = from_box_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in apk_br_rule.sub_rules_2:
                    if sub_rule.tac_code_rel_sub_inc_2:
                        for phone_type in sub_rule.tac_code_rel_sub_inc_2:
                            spiff_rule_tuple.append((sub_rule.product_code_type_2.id,phone_type.id,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type_2.id,False,sub_rule.dsr_phone_purchase_type_2,sub_rule.class_type_2,sub_rule.paid_2))
                if spiff_rule_tuple:
                    condition_string_2 = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string_2 += str("(")
                        if spiff_rule_data[0]:
                            condition_string_2 += str('''test.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string_2 += str(''' and (left(test.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(test.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or test.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string_2 += str(''' and test.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string_2 += str(''' and test.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and test.dsr_monthly_access > 0''')
                        condition_string_2 += ") OR "
                    condition_string_2 = condition_string_2[:-4]
                    condition_string_2 += str(")")
                else:
                    condition_string_2 = ''
                cr.execute('''select dsr_trans_type
        ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
        +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
        from
    ('''+from_box_condition+''') as test
    where ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
    and test.''' + field_name + ''' = %s
    and test.state = 'done'
    and test.prm_dsr_smd = false
    '''+condition_string_2+
    box_dsr_exclude_condition+'''
    group by test.dsr_trans_type
    order by test.dsr_trans_type asc''',(start_date, end_date,start_date,end_date,emp_id))
                emp_data = cr.fetchall()
                for emp_data_id in emp_data:
                    tot_box = tot_box + emp_data_id[1]
            if apk_rev_goal > 0:
                if not apk_rev:
                    apk_rev = 0.00
                if tot_box > 0:
                    avg_apk = apk_rev / tot_box
            elif apk_count_goal > 0:
                if not apk_count:
                    apk_count = 0.00
                if tot_box > 0:
                    avg_apk = float(apk_count) / float(tot_box)
            avg_apk = round(avg_apk, 2)
            print avg_apk
            if att_condition_percent > 0.00:
                if to_condition_percent != 0:
                    if avg_apk >= att_condition_percent and avg_apk <= to_condition_percent:
                        if spiff_amount > 0.00:
                            apk_vals['apk_payout'] = apk_vals['apk_payout'] + spiff_amount
                        elif spiff_on_rev > 0.00:
                            apk_vals['apk_payout'] = apk_vals['apk_payout'] + (tot_rev * spiff_on_rev) / 100
                else:
                    if avg_apk >= att_condition_percent:
                        if spiff_amount > 0.00:
                            apk_vals['apk_payout'] = apk_vals['apk_payout'] + spiff_amount
                        elif spiff_on_rev > 0.00:
                            apk_vals['apk_payout'] = apk_vals['apk_payout'] + (tot_rev * spiff_on_rev) / 100
            else:
                if spiff_amount > 0.00:
                    apk_vals['apk_payout'] = apk_vals['apk_payout'] + spiff_amount
                elif spiff_on_rev > 0.00:
                    apk_vals['apk_payout'] = apk_vals['apk_payout'] + (tot_rev * spiff_on_rev) / 100
            count = count + 1
            if (apk_vals['apk_payout'] > 0) or (count == len(spiff_apk_data.spiff_business_class)):
                apk_vals['spiff_per_box_acc_sold'] += ("%s, "%(att_condition_percent,))
                if spiff_amount > 0.00:
                    apk_vals['apk_comm_string'] += ("$ %s"%(spiff_amount))
                elif spiff_on_rev > 0.00:
                    apk_vals['apk_comm_string'] += ("%s"%(spiff_on_rev))
                    apk_vals['apk_comm_string'] += (" %")
                    if emp_model_id == 'rsa':
                        apk_vals['apk_comm_string'] += (" of RSA Revenue")
                    elif emp_model_id == 'stl':
                        apk_vals['apk_comm_string'] += (" of STL Revenue")
                    elif emp_model_id == 'mid':
                        apk_vals['apk_comm_string'] += (" of MID Revenue")
                    elif emp_model_id == 'rsm':
                        apk_vals['apk_comm_string'] += (" of RSM Revenue")
                    elif emp_model_id == 'mm':
                        apk_vals['apk_comm_string'] += (" of MM Revenue")
                    elif emp_model_id == 'dos':
                        apk_vals['apk_comm_string'] += (" of DOS Revenue")
                apk_vals['avg_apk'] += ("%s, "%(avg_apk,))
                apk_vals['apk_actual_count'] += ("%s, "%(apk_count,))
                print apk_vals
                break
        if apk_vals['spiff_per_box_acc_sold'] != "":
            apk_vals['spiff_per_box_acc_sold'] = apk_vals['spiff_per_box_acc_sold'][:-2]
        if apk_vals['avg_apk'] != "":
            apk_vals['avg_apk'] = apk_vals['avg_apk'][:-2]
        if apk_vals['apk_actual_count'] != "":
            apk_vals['apk_actual_count'] = apk_vals['apk_actual_count'][:-2]
        return apk_vals

    def _calculate_prepaid_count_goal(self, cr, uid, spiff_emp_prepaid_ids, field_name, emp_id, start_date, end_date, prm_job_id, emp_prepaid_goal):
        vals = {
                'store_prepaid_goal':0.00,
                'store_pre_actual_count':0.00,
                'store_pre_actual_percent':0.00,
                'spiff_store_pre_payout':0.00
        }
        store_prepaid_goal = 0.00
        store_pre_actual_count = 0.00
        store_pre_actual_percent = 0.00
        spiff_store_pre_payout = 0.00
        spiff_prepaid_obj = self.pool.get('spiff.prepaid.goal')
        spiff_prepaid_data = spiff_prepaid_obj.browse(cr, uid, spiff_emp_prepaid_ids[0])
        spiff_amount = spiff_prepaid_data.spiff_amount
        spiff_per_att = spiff_prepaid_data.spiff_per_att
        pre_sa_business_rule_id = spiff_prepaid_data.spiff_business_rule
        is_postpaid = pre_sa_business_rule_id.is_postpaid
        is_upgrade = pre_sa_business_rule_id.is_upgrade
        is_prepaid = pre_sa_business_rule_id.is_prepaid
        from_condition = str('')
        if is_postpaid:
            from_condition += str('select id,product_id,true as created_feature,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date from wireless_dsr_postpaid_line union all ')
        if is_upgrade:
            from_condition += str('select id,product_id,created_feature,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date from wireless_dsr_upgrade_line union all ')
        if is_prepaid:
            from_condition += str('select id,product_id,created_feature,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date from wireless_dsr_prepaid_line union all ')
        from_condition = from_condition[:-10]
        spiff_rule_tuple = []
        for sub_rule in pre_sa_business_rule_id.sub_rules:
            if sub_rule.tac_code_rel_sub_inc:
                for phone_type in sub_rule.tac_code_rel_sub_inc:
                    spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
            else:
                spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
        if spiff_rule_tuple:
            condition_string = str("and (")
            for spiff_rule_data in spiff_rule_tuple:
                condition_string += str("(")
                if spiff_rule_data[0]:
                    condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                if spiff_rule_data[1]:
                    condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                         or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                         or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                if spiff_rule_data[2]:
                    condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                if spiff_rule_data[3]:
                    condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                if spiff_rule_data[4]:
                    condition_string += str(''' and df.dsr_monthly_access > 0''')
                condition_string += ") OR "
            condition_string = condition_string[:-4]
            condition_string += str(")")
        else:
            condition_string = ''
        cr.execute('''select count(df.id) from ('''+from_condition+''') as df 
                    where df.'''+field_name+''' = %s 
                    and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
                    and df.state = 'done'
                    and df.prm_dsr_smd = false
                    and created_feature = true
                    '''+condition_string+''' ''', (emp_id, start_date, end_date,start_date,end_date))
        pre_emp_query = cr.fetchall()
        store_pre_actual_count = pre_emp_query[0][0]
        if not store_pre_actual_count:
            store_pre_actual_count = 0.00
        cr.execute('''select count(df.id) from ('''+from_condition+''') as df 
                    where df.state = 'done'
                    and df.'''+field_name+''' = %s
                    and df.crash_prm_job_id_rollback in %s
                    and (df.prm_dsr_pmd = true or df.noncommissionable = true)
                    '''+condition_string+''' ''', (emp_id, tuple(prm_job_id)))
        pre_emp_count_deact = cr.fetchall()
        pre_emp_count_deact = pre_emp_count_deact[0][0]
        if not pre_emp_count_deact:
            pre_emp_count_deact = 0.00
        store_pre_actual_payout_count = store_pre_actual_count - pre_emp_count_deact
        if store_prepaid_goal > 0.00:
            store_pre_actual_percent = (store_pre_actual_count * 100) / store_prepaid_goal
        store_pre_actual_count = store_pre_actual_payout_count
        spiff_percent = spiff_prepaid_data.spiff_percent
        if spiff_percent <= store_pre_actual_percent:
            if spiff_amount > 0.00:
                spiff_store_pre_payout = spiff_amount
            elif spiff_per_att > 0.00:
                 spiff_store_pre_payout = store_pre_actual_payout_count * spiff_per_att
        vals = {
                'spiff_store_pre_payout':spiff_store_pre_payout,
                'store_prepaid_goal':store_prepaid_goal,
                'store_pre_actual_count':store_pre_actual_count,
                'store_pre_actual_percent':store_pre_actual_percent
        }
        return vals



    def _get_basic_parameters_box_company(self, cr, uid, field_name, level_id, start_date, end_date, condition_box_string, from_box_condition, prm_job_id, box_br, rev_br,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        para_vals = {}
        pre_count = 0.00
        tot_box = 0.00
        actual_box = 0.00
        tot_emp_pos_upg_box = 0.00
        tot_rev = 0.00
        actual_rev = 0.00
        apk_rev = 0.00
        apk_count = 0.00
    #********* added Feb 2015*********#
        gross_box = 0.00
        gross_rev = 0.00
        smd_box = 0.00
        smd_rev = 0.00
        pmd_box = 0.00
        pmd_rev = 0.00
        react_box = 0.00
        react_rev = 0.00
        var_name = 'test'
        box_dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,box_br[0],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
        rev_dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,rev_br[0],master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
        if from_box_condition != '':
            cr.execute('''select dsr_trans_type
        ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
        +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
        from
    ('''+from_box_condition+''') as test
    where ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
    and test.state = 'done'
    --and test.prm_dsr_smd = false
    '''+condition_box_string+
    box_dsr_exclude_condition+'''
    group by test.dsr_trans_type
    order by test.dsr_trans_type asc''',(start_date, end_date,start_date,end_date))
            emp_data = cr.fetchall()
            for emp_data_id in emp_data:
                gross_box = gross_box + emp_data_id[1]
                if emp_data_id[0] == 'postpaid' or emp_data_id[0] == 'upgrade':
                    tot_emp_pos_upg_box = tot_emp_pos_upg_box + emp_data_id[1]
                if emp_data_id[0] == 'prepaid':
                    pre_count = emp_data_id[1]
            cr.execute('''select dsr_trans_type
        ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
        +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
        from
    ('''+from_box_condition+''') as test
    where ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
    and test.state = 'done'
    and test.prm_dsr_smd = true
    '''+condition_box_string+
    box_dsr_exclude_condition+'''
    group by test.dsr_trans_type
    order by test.dsr_trans_type asc''', (start_date, end_date,start_date,end_date))
            emp_data = cr.fetchall()
            for emp_data_id in emp_data:
                smd_box = smd_box + emp_data_id[1]
            if not smd_box:
                smd_box = 0.00
            actual_box = gross_box - smd_box
            cr.execute('''select sum(upg.dsr_rev_gen) as prm_deduct
    ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
    +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as prm_box_deduct
from ('''+from_box_condition+'''
union all
select id,feature_product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_feature_line)
as upg where upg.state = %s
and upg.crash_prm_job_id_rollback in %s
and upg.prm_dsr_pmd = true''',('done',tuple(prm_job_id)))
            emp_data = cr.fetchall()
            deact_rev = emp_data[0][0]
            deact_box = emp_data[0][1]
            if not deact_rev:
                deact_rev = 0.00
            if not deact_box:
                deact_box = 0
            pmd_rev = deact_rev
            pmd_box = deact_box
            cr.execute('''select sum(upg.dsr_rev_gen) as prm_deduct
    ,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
    +sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as prm_box_deduct
from ('''+from_box_condition+'''
union all
select id,feature_product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,prm_react_recon,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_feature_line)
as upg where upg.state = %s
and upg.crash_prm_job_id_rollback in %s
and upg.prm_react_recon = true''',('done',tuple(prm_job_id)))
            emp_data = cr.fetchall()
            react_rev = emp_data[0][0]
            react_box = emp_data[0][1]
            if not react_rev:
                react_rev = 0.00
            if not react_box:
                react_box = 0.00
        else:
            actual_box = 0.00
            tot_emp_pos_upg_box = 0.00
            pre_count = 0.00
            deact_rev = 0.00
            deact_box = 0.00
        cr.execute('''select sum(test.dsr_rev_gen) as actual_rev
,dsr_trans_type
,sum(dsr_rev_gen) as acc_mrc
,sum(dsr_quantity) as count
from
(select id,product_id,dsr_rev_gen,dsr_trans_type,true as created_feature, 0.00 as dsr_acc_mrc,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0 as dsr_quantity,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_postpaid_line
union all
select id,feature_product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_feature_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,created_feature, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description,dsr_product_code_type
from wireless_dsr_prepaid_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_upgrade_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true,dsr_acc_mrc,false as prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,dsr_quantity,pseudo_date,dsr_emp_type,null as dsr_credit_class,null as dsr_product_code,null as dsr_product_code_type
from wireless_dsr_acc_line) as test
where ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done'
--and test.prm_dsr_smd = false
'''+rev_dsr_exclude_condition+'''
group by test.dsr_trans_type
order by test.dsr_trans_type asc''', (start_date, end_date,start_date,end_date))
        emp_data = cr.fetchall()
        for emp_data_id in emp_data:
            if emp_data_id[1] == 'accessory':
                apk_rev = emp_data_id[2]
                apk_count = emp_data_id[3]
            gross_rev = gross_rev + emp_data_id[0]
        cr.execute('''select sum(test.dsr_rev_gen) as actual_rev
,dsr_trans_type
,sum(dsr_rev_gen) as acc_mrc
,sum(dsr_quantity) as count
from
(select id,product_id,dsr_rev_gen,dsr_trans_type,true as created_feature, 0.00 as dsr_acc_mrc,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0 as dsr_quantity,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_postpaid_line
union all
select id,feature_product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_feature_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,created_feature, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description,dsr_product_code_type
from wireless_dsr_prepaid_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true, 0.00,prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,0,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code,dsr_product_code_type
from wireless_dsr_upgrade_line
union all
select id,product_id,dsr_rev_gen,dsr_trans_type,true,dsr_acc_mrc,false as prm_dsr_smd,employee_id,store_id,market_id,region_id,dsr_act_date,state,dsr_quantity,pseudo_date,dsr_emp_type,null as dsr_credit_class,null as dsr_product_code,null as dsr_product_code_type
from wireless_dsr_acc_line) as test
where ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done'
and test.prm_dsr_smd = true
group by test.dsr_trans_type
order by test.dsr_trans_type asc''', (start_date, end_date,start_date,end_date))
        emp_data = cr.fetchall()
        for emp_data_id in emp_data:
            if emp_data_id[1] == 'accessory':
                apk_rev = apk_rev - emp_data_id[2]
                apk_count = apk_count - emp_data_id[3]
            smd_rev = smd_rev + emp_data_id[0]
        if not smd_rev:
            smd_rev = 0.00
        actual_rev = gross_rev - smd_rev
        tot_rev = actual_rev - float(deact_rev)
        tot_box = actual_box - deact_box
        para_vals = {   'pre_count' : pre_count,
                        'tot_box' : tot_box,
                        'actual_box' : actual_box,
                        'tot_emp_pos_upg_box' : tot_emp_pos_upg_box,
                        'tot_rev' : tot_rev,
                        'actual_rev' : actual_rev,
                        'apk_rev' : apk_rev,
                        'apk_count':apk_count,
                        'smd_rev':smd_rev,
                        'smd_box':smd_box,
                        'pmd_rev':pmd_rev,
                        'pmd_box':pmd_box,
                        'react_rev':react_rev,
                        'react_box':react_box,
                    }
        return para_vals

    def _calculate_tbc_commission_company(self, cr, uid, spiff_sa_tot_box_rule_search, store_actual_box, sto_no_of_exit, field_name, start_date, end_date, emp_id, business_box_rule_ids, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        tbc_vals = {}
        tbc_vals = {
                    'spiff_stl_tot_box_conv_percent':str(""),
                    'spiff_stl_box_count':str(""),
                    'spiff_stl_tot_box_rule_amount':0.00,
                    'spiff_stl_tot_box_rule_percent':str(""),
                    'tot_box_payout_tier':str(""),
                    'rsa_tbc_string':str("")
        }
        spiff_stl_tot_box_rule_amount = 0.00
        spiff_stl_tot_box_conv_percent = 0.00
        spiff_stl_box_count = 0.00
        att_condition_percent = 0.00
        spiff_tot_box_rule = self.pool.get('spiff.store.total.box.conversion')
        spiff_stl_tot_box_rule_data = spiff_tot_box_rule.browse(cr, uid, spiff_sa_tot_box_rule_search[0])
        spiff_business_class = spiff_stl_tot_box_rule_data.spiff_business_class
        count = 0
        var_name = str('test')
        for spiff_business_class_data in spiff_business_class:
            att_business_rule = spiff_business_class_data.att_business_rule
            pay_on_rev = spiff_business_class_data.pay_on_rev
            pay_per_att = spiff_business_class_data.pay_per_att
            flat_pay = spiff_business_class_data.pay_flat_amnt
            if att_business_rule:
                from_condition = str('')
                spiff_stl_tot_box_conv_percent = 0.00
                spiff_stl_box_count = 0.00
                box_is_postpaid = att_business_rule.is_postpaid
                box_is_upgrade = att_business_rule.is_upgrade
                box_is_prepaid = att_business_rule.is_prepaid
                if box_is_postpaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_postpaid_line union all ''')
                if box_is_prepaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description
    from wireless_dsr_prepaid_line union all ''')
                if box_is_upgrade:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_upgrade_line union all ''')
                from_condition = from_condition[:-10]
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,att_business_rule.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_rule_tuple = []
                for sub_rule in att_business_rule.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''test.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(test.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(test.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or test.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and test.dsr_phone_purchase_type = '%s'''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and test.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_tuple[4]:
                            condition_string += str(''' and test.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                cr.execute('''select dsr_trans_type
,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
+sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
from
('''+from_condition+''') as test
where ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done'
and test.prm_dsr_smd = false
'''+condition_string+
    dsr_exclude_condition+ '''
group by test.dsr_trans_type
order by test.dsr_trans_type asc''',(start_date,end_date,start_date,end_date))
                box_data = cr.fetchall()
                for emp_data_id in box_data:
                    spiff_stl_box_count = spiff_stl_box_count + emp_data_id[1]
                if sto_no_of_exit > 0.00:
                    spiff_stl_tot_box_conv_percent = (spiff_stl_box_count * 100) / sto_no_of_exit
                spiff_stl_tot_box_conv_percent = round(spiff_stl_tot_box_conv_percent,2)
            payout_business_rule = spiff_business_class_data.payout_business_rule
            if payout_business_rule:
                spiff_stl_box_count = 0
                from_condition = str('')
                box_is_postpaid = payout_business_rule.is_postpaid
                box_is_upgrade = payout_business_rule.is_upgrade
                box_is_prepaid = payout_business_rule.is_prepaid
                if box_is_postpaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_postpaid_line union all ''')
                if box_is_prepaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description
    from wireless_dsr_prepaid_line union all ''')
                if box_is_upgrade:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_upgrade_line union all ''')
                from_condition = from_condition[:-10]
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,payout_business_rule.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_rule_tuple = []
                for sub_rule in payout_business_rule.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''test.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(test.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(test.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or test.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and test.dsr_phone_purchase_type = '%s'''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and test.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and test.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                cr.execute('''select dsr_trans_type
,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
+sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
from
('''+from_condition+''') as test
where test.''' + field_name + ''' = %s
and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done'
and test.prm_dsr_smd = false
'''+condition_string+
    dsr_exclude_condition+ '''
group by test.dsr_trans_type
order by test.dsr_trans_type asc''',(emp_id,start_date,end_date,start_date,end_date))
                box_data = cr.fetchall()
                for emp_data_id in box_data:
                    spiff_stl_box_count = spiff_stl_box_count + emp_data_id[1]
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            if att_condition_percent:
                if to_condition_percent != 0:
                    if spiff_stl_tot_box_conv_percent >= att_condition_percent and spiff_stl_tot_box_conv_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + (spiff_stl_box_count * pay_per_att)
                        elif pay_on_rev > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + flat_pay
                else:
                    if spiff_stl_tot_box_conv_percent >= att_condition_percent:
                        if pay_per_att > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + (spiff_stl_box_count * pay_per_att)
                        elif pay_on_rev > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + flat_pay
            else:
                if pay_per_att > 0.00:
                    tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + (spiff_stl_box_count * pay_per_att)
                elif pay_on_rev > 0.00:
                    tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + ((tot_rev * pay_on_rev)/100)
                elif flat_pay > 0.00:
                    tbc_vals['spiff_stl_tot_box_rule_amount'] = tbc_vals['spiff_stl_tot_box_rule_amount'] + flat_pay
            count = count + 1
            if (tbc_vals['spiff_stl_tot_box_rule_amount'] > 0.00) or (count == len(spiff_business_class)):
                spiff_stl_tot_box_conv_percent = round(spiff_stl_tot_box_conv_percent,2)
                att_condition_percent = round(att_condition_percent,2)
                spiff_stl_box_count = round(spiff_stl_box_count,2)
                if pay_per_att:
                    tbc_vals['tot_box_payout_tier'] += str("$ %s per"%(pay_per_att))
                    tbc_vals['rsa_tbc_string'] += ("$ %s per"%(pay_per_att))
                elif pay_on_rev:
                    tbc_vals['tot_box_payout_tier'] += str("%s"%(pay_on_rev))
                    tbc_vals['tot_box_payout_tier'] += str(" %")
                    tbc_vals['rsa_tbc_string'] += ("%s"%(pay_on_rev))
                    tbc_vals['rsa_tbc_string'] += (" %")
                    if emp_model_id == 'rsa':
                        tbc_vals['rsa_tbc_string'] += (" of RSA Revenue")
                    elif emp_model_id == 'stl':
                        tbc_vals['rsa_tbc_string'] += (" of STL Revenue")
                    elif emp_model_id == 'mid':
                        tbc_vals['rsa_tbc_string'] += (" of MID Revenue")
                    elif emp_model_id == 'rsm':
                        tbc_vals['rsa_tbc_string'] += (" of RSM Revenue")
                    elif emp_model_id == 'mm':
                        tbc_vals['rsa_tbc_string'] += (" of MM Revenue")
                    elif emp_model_id == 'dos':
                        tbc_vals['rsa_tbc_string'] += (" of DOS Revenue")
                elif flat_pay:
                    tbc_vals['tot_box_payout_tier'] += str("$ %s"%(flat_pay))
                    tbc_vals['rsa_tbc_string'] += ("$ %s"%(flat_pay))
                tbc_vals['spiff_stl_tot_box_conv_percent'] += str("%s, "%(spiff_stl_tot_box_conv_percent,))
                tbc_vals['spiff_stl_tot_box_rule_percent'] += str("%s, "%(att_condition_percent))
                tbc_vals['spiff_stl_box_count'] += str("%s, "%(spiff_stl_box_count,))
                break
        if tbc_vals['spiff_stl_box_count'] != "":
            tbc_vals['spiff_stl_box_count'] = tbc_vals['spiff_stl_box_count'][:-2]
        if tbc_vals['spiff_stl_tot_box_rule_percent'] != "":
            tbc_vals['spiff_stl_tot_box_rule_percent'] = tbc_vals['spiff_stl_tot_box_rule_percent'][:-2]
        if tbc_vals['spiff_stl_tot_box_conv_percent'] != "":
            tbc_vals['spiff_stl_tot_box_conv_percent'] = tbc_vals['spiff_stl_tot_box_conv_percent'][:-2]
        return tbc_vals

    def _calculate_mi_gb_company(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_3gb_ids, prm_job_id, tot_rev, spiff_no_of_exit, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}
        vals['spiff_mi_gb_count'] = str("") #-- actual count
        vals['spiff_sa_mi_3gb_amount'] = 0.00 #---total payout
        vals['spiff_mi_conv_percent'] = str("") #--- Conversion percent
        vals['spiff_master_mi_conv_percent'] = str("")  #-- master conversion
        vals['mi_1gb_string'] = str("")
        spiff_sa_mi_obj = self.pool.get('spiff.mobile.internet')
        sa_mi_count_payout = 0.00
        spiff_mi_conv_percent = 0.00
        spiff_sa_mi_3gb_data = spiff_sa_mi_obj.browse(cr, uid, spiff_sa_mi_3gb_ids[0])
        spiff_business_class = spiff_sa_mi_3gb_data.spiff_business_class
        var_name = str('df')
        for spiff_business_class_data in spiff_business_class:
            sa_mi_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_per_att = spiff_business_class_data.pay_per_att
            if sa_mi_3gb_business_rule_id:
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,sa_mi_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                sa_mi_business_rule_pos = sa_mi_3gb_business_rule_id.is_postpaid
                sa_mi_business_rule_upg = sa_mi_3gb_business_rule_id.is_upgrade
                sa_mi_business_rule_pre = sa_mi_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if sa_mi_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if sa_mi_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if sa_mi_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in sa_mi_3gb_business_rule_id.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                if from_condition != '':
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''')
            as df where ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.prm_dsr_smd = false
            and df.state = 'done'
            '''+condition_string+
    dsr_exclude_condition+''' ''', (start_date, end_date,start_date,end_date))
                    mi_1gb_data = cr.fetchall()
                    count_sa_mi_1gb_att = mi_1gb_data[0][0]
                    if not count_sa_mi_1gb_att:
                        count_sa_mi_1gb_att = 0.00
                else:
                    count_sa_mi_1gb_att = 0.00
                sa_mi_count_payout = count_sa_mi_1gb_att
                if spiff_no_of_exit > 0.00:
                    spiff_mi_conv_percent = (float(sa_mi_count_payout) * 100) / float(spiff_no_of_exit)
                spiff_mi_conv_percent = round(spiff_mi_conv_percent, 2)
            pay_sa_mi_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_sa_mi_3gb_business_rule_id:
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_sa_mi_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                sa_mi_business_rule_pos = pay_sa_mi_3gb_business_rule_id.is_postpaid
                sa_mi_business_rule_upg = pay_sa_mi_3gb_business_rule_id.is_upgrade
                sa_mi_business_rule_pre = pay_sa_mi_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if sa_mi_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if sa_mi_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if sa_mi_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in pay_sa_mi_3gb_business_rule_id.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                if from_condition != '':
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''')
            as df where df.'''+field_name+''' = %s
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.prm_dsr_smd = false
            and df.state = 'done'
            '''+condition_string+
    dsr_exclude_condition+''' ''', (emp_id, start_date, end_date,start_date,end_date))
                    mi_1gb_data = cr.fetchall()
                    count_sa_mi_1gb_att = mi_1gb_data[0][0]
                    if not count_sa_mi_1gb_att:
                        count_sa_mi_1gb_att = 0.00
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''')
            as df where df.'''+field_name+''' = %s
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and df.state = 'done'
            '''+condition_string+''' ''', (emp_id, tuple(prm_job_id)))
                    mi_1gb_deact_data = cr.fetchall()
                    count_sa_mi_deact = mi_1gb_deact_data[0][0]
                    if not count_sa_mi_deact:
                        count_sa_mi_deact = 0.00
                else:
                    count_sa_mi_1gb_att = 0.00
                    count_sa_mi_deact = 0.00
                sa_mi_count_payout = count_sa_mi_1gb_att - count_sa_mi_deact
            if sa_mi_3gb_business_rule_id:
                if to_condition_percent != 0:
                    if spiff_mi_conv_percent >= att_condition_percent and spiff_mi_conv_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
                else:
                    if spiff_mi_conv_percent >= att_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
            else:
                if pay_per_att > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                elif pay_on_rev > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                elif flat_pay > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
            att_condition_percent = round(att_condition_percent, 2)
            sa_mi_count_payout = round(sa_mi_count_payout, 2)
            spiff_mi_conv_percent = round(spiff_mi_conv_percent, 2)
            vals['spiff_mi_conv_percent'] += ("%s, "%(spiff_mi_conv_percent,))
            vals['spiff_master_mi_conv_percent'] += str("%s, "%(att_condition_percent,))
            vals['spiff_mi_gb_count'] += str("%s, "%(sa_mi_count_payout,))
        if pay_per_att > 0.00:
            vals['mi_1gb_string'] += ("$ %s per"%(pay_per_att))
        elif flat_pay:
            vals['mi_1gb_string'] += ("$ %s"%(flat_pay))
        elif pay_on_rev:
            vals['mi_1gb_string'] += ("%s"%(pay_on_rev))
            vals['mi_1gb_string'] += (" %")
            if emp_model_id == 'rsa':
                vals['mi_1gb_string'] += (" of RSA Revenue")
            elif emp_model_id == 'stl':
                vals['mi_1gb_string'] += (" of STL Revenue")
            elif emp_model_id == 'mid':
                vals['mi_1gb_string'] += (" of MID Revenue")
            elif emp_model_id == 'rsm':
                vals['mi_1gb_string'] += (" of RSM Revenue")
            elif emp_model_id == 'mm':
                vals['mi_1gb_string'] += (" of MM Revenue")
            elif emp_model_id == 'dos':
                vals['mi_1gb_string'] += (" of DOS Revenue")
        if vals['spiff_mi_gb_count'] != "":
            vals['spiff_mi_gb_count'] = vals['spiff_mi_gb_count'][:-2]
        if vals['spiff_master_mi_conv_percent'] != "":
            vals['spiff_master_mi_conv_percent'] = vals['spiff_master_mi_conv_percent'][:-2]
        if vals['spiff_mi_conv_percent'] != "":
            vals['spiff_mi_conv_percent'] = vals['spiff_mi_conv_percent'][:-2]
        return vals

    def _calculate_pre_conv_company(self, cr, uid, field_name, start_date, end_date, emp_id, spiff_sa_mi_3gb_ids, prm_job_id, tot_rev, spiff_no_of_exit, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        vals = {}
        vals['spiff_mi_gb_count'] = str("") #-- actual count
        vals['spiff_sa_mi_3gb_amount'] = 0.00 #---total payout
        vals['spiff_mi_conv_percent'] = str("") #--- Conversion percent
        vals['spiff_master_mi_conv_percent'] = str("")  #-- master conversion
        vals['pre_conv_string'] = str("")
        spiff_sa_mi_obj = self.pool.get('spiff.prepaid.conversion')
        sa_mi_count_payout = 0.00
        spiff_mi_conv_percent = 0.00
        var_name = str('df')
        spiff_sa_mi_3gb_data = spiff_sa_mi_obj.browse(cr, uid, spiff_sa_mi_3gb_ids[0])
        spiff_business_class = spiff_sa_mi_3gb_data.prepaid_business_class
        for spiff_business_class_data in spiff_business_class:
            sa_mi_3gb_business_rule_id = spiff_business_class_data.att_business_rule
            pay_on_rev = spiff_business_class_data.pay_on_rev
            flat_pay = spiff_business_class_data.pay_flat_amnt
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            pay_per_att = spiff_business_class_data.pay_per_att
            if sa_mi_3gb_business_rule_id:
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,sa_mi_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                sa_mi_business_rule_pos = sa_mi_3gb_business_rule_id.is_postpaid
                sa_mi_business_rule_upg = sa_mi_3gb_business_rule_id.is_upgrade
                sa_mi_business_rule_pre = sa_mi_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if sa_mi_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if sa_mi_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if sa_mi_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in sa_mi_3gb_business_rule_id.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''

                if from_condition != '':
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''')
            as df where ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.prm_dsr_smd = false
            and df.state = 'done'
            '''+condition_string+
    dsr_exclude_condition+''' ''', (start_date, end_date,start_date,end_date))
                    mi_1gb_data = cr.fetchall()
                    count_sa_mi_1gb_att_comp = mi_1gb_data[0][0]
                    if not count_sa_mi_1gb_att_comp:
                        count_sa_mi_1gb_att_comp = 0.00
                else:
                    count_sa_mi_1gb_att_comp = 0.00
                sa_mi_count_payout = count_sa_mi_1gb_att_comp
                if spiff_no_of_exit > 0.00:
                    #### below 2 variables i.e 1. for prepaid company level count
                    ### 2nd is company Level exits
                    spiff_mi_conv_percent = (float(sa_mi_count_payout) * 100) / float(spiff_no_of_exit)
                spiff_mi_conv_percent = round(spiff_mi_conv_percent, 2)
            pay_sa_mi_3gb_business_rule_id = spiff_business_class_data.payout_business_rule
            if pay_sa_mi_3gb_business_rule_id:
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,pay_sa_mi_3gb_business_rule_id.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                sa_mi_business_rule_pos = pay_sa_mi_3gb_business_rule_id.is_postpaid
                sa_mi_business_rule_upg = pay_sa_mi_3gb_business_rule_id.is_upgrade
                sa_mi_business_rule_pre = pay_sa_mi_3gb_business_rule_id.is_prepaid
                from_condition = str('')
                if sa_mi_business_rule_pos:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_postpaid_line union all ')
                if sa_mi_business_rule_upg:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code from wireless_dsr_upgrade_line union all ')
                if sa_mi_business_rule_pre:
                    from_condition += str('select id,product_id,dsr_monthly_access,dsr_product_code_type,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_smd,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,noncommissionable,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description from wireless_dsr_prepaid_line union all ')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                for sub_rule in pay_sa_mi_3gb_business_rule_id.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''df.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(df.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(df.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or df.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and df.dsr_phone_purchase_type = '%s' '''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and df.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))
                        if spiff_rule_data[4]:
                            condition_string += str(''' and df.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                if from_condition != '':
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''')
            as df where df.'''+field_name+''' = %s
            and ((df.dsr_act_date between %s and %s) or (df.pseudo_date between %s and %s))
            and df.prm_dsr_smd = false
            and df.state = 'done'
            '''+condition_string+
    dsr_exclude_condition+''' ''', (emp_id, start_date, end_date,start_date,end_date))
                    mi_1gb_data = cr.fetchall()
                    count_sa_mi_1gb_att = mi_1gb_data[0][0]
                    if not count_sa_mi_1gb_att:
                        count_sa_mi_1gb_att = 0.00
                    cr.execute('''select count(df.id) as count
            from ('''+from_condition+''')
            as df where df.'''+field_name+''' = %s
            and df.crash_prm_job_id_rollback in %s
            and (df.prm_dsr_pmd = true or df.noncommissionable = true)
            and df.state = 'done'
            '''+condition_string+''' ''', (emp_id, tuple(prm_job_id)))
                    mi_1gb_deact_data = cr.fetchall()
                    count_sa_mi_deact = mi_1gb_deact_data[0][0]
                    if not count_sa_mi_deact:
                        count_sa_mi_deact = 0.00
                else:
                    count_sa_mi_1gb_att = 0.00
                    count_sa_mi_deact = 0.00
                sa_mi_count_payout = count_sa_mi_1gb_att - count_sa_mi_deact
            if sa_mi_3gb_business_rule_id:
                if to_condition_percent != 0:
                    if spiff_mi_conv_percent >= att_condition_percent and spiff_mi_conv_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
                else:
                    if spiff_mi_conv_percent >= att_condition_percent:
                        if pay_per_att > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                        elif pay_on_rev > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
            else:
                if pay_per_att > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + (sa_mi_count_payout * pay_per_att)
                elif pay_on_rev > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + ((tot_rev * pay_on_rev)/100)
                elif flat_pay > 0.00:
                    vals['spiff_sa_mi_3gb_amount'] = vals['spiff_sa_mi_3gb_amount'] + flat_pay
            att_condition_percent = round(att_condition_percent, 2)
            sa_mi_count_payout = round(sa_mi_count_payout, 2)
            spiff_mi_conv_percent = round(spiff_mi_conv_percent, 2)
            vals['spiff_mi_conv_percent'] += ("%s, "%(spiff_mi_conv_percent,))
            vals['spiff_master_mi_conv_percent'] += str("%s, "%(att_condition_percent,))
            vals['spiff_mi_gb_count'] += str("%s, "%(sa_mi_count_payout,))
        if pay_per_att > 0.00:
            if emp_model_id == 'rsa':
                vals['pre_conv_string'] += ("$ %s per sold by RSA"%(pay_per_att))
            elif emp_model_id == 'stl':
                vals['pre_conv_string'] += ("$ %s per sold by STL"%(pay_per_att))
            elif emp_model_id == 'mid':
                vals['pre_conv_string'] += ("$ %s per sold by MID"%(pay_per_att))
            elif emp_model_id == 'rsm':
                vals['pre_conv_string'] += ("$ %s per sold by RSM"%(pay_per_att))
            elif emp_model_id == 'mm':
                vals['pre_conv_string'] += ("$ %s per sold by MM"%(pay_per_att))
            elif emp_model_id == 'dos':
                vals['pre_conv_string'] += ("$ %s per sold by DOS"%(pay_per_att))
        elif flat_pay:
            vals['pre_conv_string'] += ("$ %s"%(flat_pay))
        elif pay_on_rev:
            vals['pre_conv_string'] += ("%s"%(pay_on_rev))
            vals['pre_conv_string'] += (" %")
            if emp_model_id == 'rsa':
                vals['pre_conv_string'] += (" of RSA Revenue")
            elif emp_model_id == 'stl':
                vals['pre_conv_string'] += (" of STL Revenue")
            elif emp_model_id == 'mid':
                vals['pre_conv_string'] += (" of MID Revenue")
            elif emp_model_id == 'rsm':
                vals['pre_conv_string'] += (" of RSM Revenue")
            elif emp_model_id == 'mm':
                vals['pre_conv_string'] += (" of MM Revenue")
            elif emp_model_id == 'dos':
                vals['pre_conv_string'] += (" of DOS Revenue")
        if vals['spiff_mi_gb_count'] != "":
            vals['spiff_mi_gb_count'] = vals['spiff_mi_gb_count'][:-2]
        if vals['spiff_master_mi_conv_percent'] != "":
            vals['spiff_master_mi_conv_percent'] = vals['spiff_master_mi_conv_percent'][:-2]
        if vals['spiff_mi_conv_percent'] != "":
            vals['spiff_mi_conv_percent'] = vals['spiff_mi_conv_percent'][:-2]
        return vals

    def _calculate_base_box_hit(self, cr, uid, comm_emp_search_ids, emp_box_goal, field_name, start_date, end_date, emp_id, tot_rev, emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc):
        box_vals = {}
        box_vals = {
                    'base_box_payout':0.00,
                    'base_box_actual':0.00,
                    'base_box_goal':0.00,
                    'base_box_hit_percent':0.00,
                    'base_box_pay_tier':str('')
        }
        base_box_payout = 0.00
        base_box_actual = 0.00
        emp_box_goal = round(emp_box_goal,0)
        base_box_goal = emp_box_goal
        base_box_hit_percent = 0.00
        att_condition_percent = 0.00
        spiff_tot_box_rule = self.pool.get('comm.base.box.commission.formula')
        spiff_stl_tot_box_rule_data = spiff_tot_box_rule.browse(cr, uid, comm_emp_search_ids[0])
        spiff_business_class = spiff_stl_tot_box_rule_data.spiff_business_class
        count = 0
        var_name = str('test')
        for spiff_business_class_data in spiff_business_class:
            att_business_rule = spiff_business_class_data.att_business_rule                
            pay_on_rev = spiff_business_class_data.pay_on_rev
            pay_per_att = spiff_business_class_data.pay_per_att
            flat_pay = spiff_business_class_data.pay_flat_amnt
            hit_goal_target = spiff_business_class_data.hit_goal_target
            if att_business_rule:
                from_condition = str('')
                spiff_stl_tot_box_conv_percent = 0.00
                spiff_stl_box_count = 0.00
                box_is_postpaid = att_business_rule.is_postpaid
                box_is_upgrade = att_business_rule.is_upgrade
                box_is_prepaid = att_business_rule.is_prepaid
                if box_is_postpaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_postpaid_line union all ''')
                if box_is_prepaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description
    from wireless_dsr_prepaid_line union all ''')
                if box_is_upgrade:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_upgrade_line union all ''')
                from_condition = from_condition[:-10]
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,att_business_rule.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                spiff_rule_tuple = []
                for sub_rule in att_business_rule.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''test.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(test.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(test.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or test.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and test.dsr_phone_purchase_type = '%s'''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and test.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_tuple[4]:
                            condition_string += str(''' and test.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                cr.execute('''select dsr_trans_type
,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
+sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
from 
('''+from_condition+''') as test
where test.''' + field_name + ''' = %s
and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done'
and test.prm_dsr_smd = false
'''+condition_string+
    dsr_exclude_condition+ '''
group by test.dsr_trans_type
order by test.dsr_trans_type asc''',(emp_id,start_date,end_date,start_date,end_date))
                box_data = cr.fetchall()
                for emp_data_id in box_data:
                    base_box_actual = base_box_actual + emp_data_id[1]
                if not hit_goal_target:
                    if base_box_goal > 0.00:
                        base_box_hit_percent = (base_box_actual * 100) / base_box_goal
                base_box_hit_percent = round(base_box_hit_percent,2)
            payout_business_rule = spiff_business_class_data.payout_business_rule
            if payout_business_rule:
                base_box_actual = 0.00
                from_condition = str('')
                box_is_postpaid = payout_business_rule.is_postpaid
                box_is_upgrade = payout_business_rule.is_upgrade
                box_is_prepaid = payout_business_rule.is_prepaid
                if box_is_postpaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true as created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_postpaid_line union all ''')
                if box_is_prepaid:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,created_feature,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,null as dsr_emp_type,null as dsr_credit_class,dsr_product_description
    from wireless_dsr_prepaid_line union all ''')
                if box_is_upgrade:
                    from_condition += str('''select id,product_id,dsr_monthly_access,dsr_rev_gen,dsr_trans_type,true,dsr_product_code_type,prm_dsr_smd,dsr_imei_no,dsr_phone_purchase_type,crash_prm_job_id_rollback,prm_dsr_pmd,employee_id,store_id,market_id,region_id,dsr_act_date,state,pseudo_date,dsr_emp_type,dsr_credit_class,dsr_product_code
    from wireless_dsr_upgrade_line union all ''')
                from_condition = from_condition[:-10]
                spiff_rule_tuple = []
                dsr_exclude_condition = self._get_dsr_exclude_condition(var_name,payout_business_rule.id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
                for sub_rule in payout_business_rule.sub_rules:
                    if sub_rule.tac_code_rel_sub_inc:
                        for phone_type in sub_rule.tac_code_rel_sub_inc:
                            spiff_rule_tuple.append((sub_rule.product_code_type.id,phone_type.id,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                    else:
                        spiff_rule_tuple.append((sub_rule.product_code_type.id,False,sub_rule.dsr_phone_purchase_type,sub_rule.class_type,sub_rule.paid))
                if spiff_rule_tuple:
                    condition_string = str("and (")
                    for spiff_rule_data in spiff_rule_tuple:
                        condition_string += str("(")
                        if spiff_rule_data[0]:
                            condition_string += str('''test.dsr_product_code_type = %s'''%(spiff_rule_data[0],))
                        if spiff_rule_data[1]:
                            condition_string += str(''' and (left(test.dsr_imei_no,8) in (select tac_code from tac_code_master where phone_type = %s)
                                                 or left(test.dsr_imei_no,8) not in (select tac_code from tac_code_master)
                                                 or test.dsr_imei_no is null)'''%(spiff_rule_data[1],))
                        if spiff_rule_data[2]:
                            condition_string += str(''' and test.dsr_phone_purchase_type = '%s'''%(spiff_rule_data[2],))
                        if spiff_rule_data[3]:
                            condition_string += str(''' and test.dsr_credit_class in (select id from credit_class where category_type = %s)'''%(spiff_rule_data[3],))                
                        if spiff_rule_data[4]:
                            condition_string += str(''' and test.dsr_monthly_access > 0''')
                        condition_string += ") OR "
                    condition_string = condition_string[:-4]
                    condition_string += str(")")
                else:
                    condition_string = ''
                cr.execute('''select dsr_trans_type
,sum(case when dsr_trans_type like 'postpaid' then 1 else 0 end) + sum(case when dsr_trans_type like 'upgrade' then 1 else 0 end)
+sum(case when dsr_trans_type like 'prepaid' and created_feature=false then 1 else 0 end) as total_boxes
from 
('''+from_condition+''') as test
where test.''' + field_name + ''' = %s
and ((test.dsr_act_date between %s and %s) or (test.pseudo_date between %s and %s))
and test.state = 'done'
and test.prm_dsr_smd = false
'''+condition_string+
    dsr_exclude_condition+ '''
group by test.dsr_trans_type
order by test.dsr_trans_type asc''',(emp_id,start_date,end_date,start_date,end_date))
                box_data = cr.fetchall()
                for emp_data_id in box_data:
                    base_box_actual = base_box_actual + emp_data_id[1]
            att_condition_percent = spiff_business_class_data.att_condition_percent
            to_condition_percent = spiff_business_class_data.to_condition_percent
            if att_condition_percent:
                if to_condition_percent != 0:
                    if base_box_hit_percent >= att_condition_percent and base_box_hit_percent <= to_condition_percent:
                        if pay_per_att > 0.00:
                            box_vals['base_box_payout'] = box_vals['base_box_payout'] + (base_box_actual * pay_per_att)
                        elif pay_on_rev > 0.00:
                            box_vals['base_box_payout'] = box_vals['base_box_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            box_vals['base_box_payout'] = box_vals['base_box_payout'] + flat_pay
                else:
                    if base_box_hit_percent >= att_condition_percent:
                        if pay_per_att > 0.00:
                            box_vals['base_box_payout'] = box_vals['base_box_payout'] + (base_box_actual * pay_per_att)
                        elif pay_on_rev > 0.00:
                            box_vals['base_box_payout'] = box_vals['base_box_payout'] + ((tot_rev * pay_on_rev)/100)
                        elif flat_pay > 0.00:
                            box_vals['base_box_payout'] = box_vals['base_box_payout'] + flat_pay
            else:
                if base_box_actual >= base_box_goal:
                    if pay_per_att > 0.00:
                        box_vals['base_box_payout'] = box_vals['base_box_payout'] + (base_box_actual * pay_per_att)
                    elif pay_on_rev > 0.00:
                        box_vals['base_box_payout'] = box_vals['base_box_payout'] + ((tot_rev * pay_on_rev)/100)
                    elif flat_pay > 0.00:
                        box_vals['base_box_payout'] = box_vals['base_box_payout'] + flat_pay
            count = count + 1
            if (box_vals['base_box_payout'] > 0.00) or (count == len(spiff_business_class)):
                base_box_hit_percent = round(base_box_hit_percent,2)
                att_condition_percent = round(att_condition_percent,2)
                base_box_actual = round(base_box_actual,2)
                if pay_per_att:
                    box_vals['base_box_pay_tier'] += str("$ %s per"%(pay_per_att))
                elif pay_on_rev:
                    box_vals['base_box_pay_tier'] += str("%s"%(pay_on_rev))
                    box_vals['base_box_pay_tier'] += str(" %")
                    if emp_model_id == 'rsa':
                        box_vals['base_box_pay_tier'] += (" of RSA Revenue")
                    elif emp_model_id == 'stl':
                        box_vals['base_box_pay_tier'] += (" of STL Revenue")
                    elif emp_model_id == 'mid':
                        box_vals['base_box_pay_tier'] += (" of MID Revenue")
                    elif emp_model_id == 'rsm':
                        box_vals['base_box_pay_tier'] += (" of RSM Revenue")
                    elif emp_model_id == 'mm':
                        box_vals['base_box_pay_tier'] += (" of MM Revenue")
                    elif emp_model_id == 'dos':
                        box_vals['base_box_pay_tier'] += (" of DOS Revenue")
                elif flat_pay:
                    box_vals['base_box_pay_tier'] += str("$ %s"%(flat_pay))
                box_vals['base_box_hit_percent'] = base_box_hit_percent
                box_vals['base_box_actual'] = base_box_actual
                box_vals['base_box_goal'] = emp_box_goal
                break
        return box_vals

    def calculate_total_payout(self, cr, uid, ids, context=None):
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
         ############# JOD PHP Attachment Spiff Calculation ################################ Complete (Taking Postpaid and Upgrade both without Chargebacks)
        spiff_jod_php_obj = self.pool.get('spiff.jod.php.att')
        spiff_jod_php_ids = spiff_jod_php_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        jod_php_attach_count = 0.00
        jod_php_attach_percent = 0.00
        jod_php_attach_payout = 0.00
        jod_php_attach_goals = 0.00
        jod_php_conv_percent = 0.00
        jod_php_attach_string = str("")
        if spiff_jod_php_ids:
            field_name = 'employee_id'
            emp_spiff_jod_data = self._calculate_jod_php_attachment(cr, uid, field_name, start_date, end_date, emp_id, spiff_jod_php_ids, prm_job_id, tot_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            jod_php_attach_goals = emp_spiff_jod_data['jod_php_attach_goals']
            jod_php_attach_percent = emp_spiff_jod_data['jod_php_attach_percent']
            jod_php_attach_payout = emp_spiff_jod_data['jod_php_attach_payout']
            jod_php_attach_count = emp_spiff_jod_data['jod_php_attach_count']
            jod_php_attach_string = emp_spiff_jod_data['jod_php_attach_string']
            jod_php_conv_percent = emp_spiff_jod_data['jod_php_conv_percent']
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
                    jod_php_conv_percent = emp_spiff_jod_data['jod_php_conv_percent']
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
            jod_php_conv_percent = emp_spiff_jod_data['jod_php_conv_percent']
        spiff_jod_php_region_ids = spiff_jod_php_obj.search(cr, uid, [('spiff_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('spiff_start_date', '<=', start_date), ('spiff_end_date', '>=', end_date), ('spiff_inactive', '=', False)])
        if spiff_jod_php_region_ids:            
            field_name = 'region_id'
            emp_spiff_jod_data = self._calculate_jod_php_attachment(cr, uid, field_name, start_date, end_date, region_id, spiff_jod_php_region_ids, prm_job_id, tot_region_rev,emp_model_id,master_br_dict,master_br_emp_type,master_br_cc,master_br_prod_code,master_br_soc)
            jod_php_attach_goals = emp_spiff_jod_data['jod_php_attach_goals']
            jod_php_attach_percent = emp_spiff_jod_data['jod_php_attach_percent']
            jod_php_attach_payout = emp_spiff_jod_data['jod_php_attach_payout']
            jod_php_attach_count = emp_spiff_jod_data['jod_php_attach_count']
            jod_php_attach_string = emp_spiff_jod_data['jod_php_attach_string']
            jod_php_conv_percent = emp_spiff_jod_data['jod_php_conv_percent']
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
                                    'jod_php_conv_percent':jod_php_conv_percent,
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
    
    def calculate_elite_bonus(self, cr, uid, start_date, end_date, pre_prm_upload, context=None):    
        model_obj = self.pool.get('ir.model')
        model_emp_search_id = model_obj.search(cr, uid, [('model', '=', 'hr.employee')])
        model_store_search_id = model_obj.search(cr, uid, [('model', '=', 'sap.store')])
        model_market_search_id = model_obj.search(cr, uid, [('model', '=', 'market.place')])
        model_region_search_id = model_obj.search(cr, uid, [('model', '=', 'market.regions')])
        model_comp_search_id = model_obj.search(cr, uid, [('model', '=', 'res.company')])


        cr.execute('''select count(hr.id) from hr_employee hr, hr_job job, resource_resource res
where hr.resource_id = res.id and res.active=true
and hr.job_id=job.id and job.model_id in ('rsa','stl')''')
        hr_ids = cr.fetchall()
        hr_count = hr_ids[0][0]

        cr.execute("select count(distinct(sap_id)) from sap_tracker where store_inactive=false and end_date >= %s",(start_date,))
        store_count = cr.fetchall()
        store_count = store_count[0][0]

        cr.execute("select count(distinct(market_id)) from market_tracker where end_date >= %s",(start_date,))
        market_count = cr.fetchall()
        market_count = market_count[0][0]

        cr.execute("select count(distinct(region_id)) from region_tracker where end_date >= %s",(start_date,))
        region_ids = cr.fetchall()
        region_count = region_ids[0][0]
    # ########## Vision Reward Formula ############################# Need TO Verify
    
    # ************** for Revnue Dollars RSA in Company ******************** # 
        cr.execute('''select * from get_revenue_perc_by_emp_odoo(%s, %s, 'rsa', %s)''', (start_date, end_date,100))
        rsa_revenue_dollars_data = cr.fetchall()
        rsa_rev_dollars_data = {
                                'emp_id':[],
                                'rank':[]
        }
        for rsa_revenue_dollars_each in rsa_revenue_dollars_data:
            rsa_rev_dollars_data['emp_id'].append(rsa_revenue_dollars_each[0])
            rsa_rev_dollars_data['rank'].append(rsa_revenue_dollars_each[2])

    # ************** for Top Employees in Company RSA ******************* #
        cr.execute('''select * from sp_getRanking_SalesRep(%s,%s,%s,null,null)''', (100, start_date, end_date))
        rsa_top_emp_comp_data = cr.fetchall()
        rsa_top_comp_emp_data = {
                                'emp_id':[],
                                'rank':[]
        }
        for rsa_top_emp_comp_each in rsa_top_emp_comp_data:
            rsa_top_comp_emp_data['emp_id'].append(rsa_top_emp_comp_each[0])
            rsa_top_comp_emp_data['rank'].append(rsa_top_emp_comp_each[1])

    # *************** for top stores in company Store Level *************** #
        cr.execute('''select * from sp_getRanking_RMS(%s,%s,%s,'store','perc')''', (100, start_date, end_date))
        top_store_comp_data = cr.fetchall()
        top_comp_store_data = {
                                'store_id':[],
                                'rank':[]
        }
        for top_store_comp_each in top_store_comp_data:
            top_comp_store_data['store_id'].append(top_store_comp_each[0])
            top_comp_store_data['rank'].append(top_store_comp_each[1])

    # # ***************** for OPS Leaderboard Store Level ***************** #
    #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s,'store',%s)''', (start_date,end_date,store_count,))
    #     top_store_ops_data = cr.fetchall()
    #     top_ops_store_data = {
    #                           'store_id':[],
    #                           'rank':[]
    #     }
    #     for top_store_ops_each in top_store_ops_data:
    #         top_ops_store_data['store_id'].append(top_store_ops_each[0])
    #         top_ops_store_data['rank'].append(top_store_ops_each[1])

    # ***************** for OPS Leaderboard Store Level ***************** #
        # cr.execute('''select store_id,rank from leaderboard_sap where start_date = %s and end_date = %s''', (start_date,end_date))
        # top_store_ops_data = cr.fetchall()
        # top_ops_store_data = {
        #                       'store_id':[],
        #                       'rank':[]
        # }
        # if top_store_ops_data:
        #     for top_store_ops_each in top_store_ops_data:
        #         top_ops_store_data['store_id'].append(top_store_ops_each[0])
        #         top_ops_store_data['rank'].append(top_store_ops_each[1])

    # ************ for top markets in comp Market Level ***************** #
        cr.execute('''select * from sp_getRanking_RMS(100,%s,%s,'market','perc')''', (start_date, end_date))
        top_market_comp_data = cr.fetchall()
        top_comp_market_data = {
                                'market_id':[],
                                'rank':[]
        }
        for top_market_comp_each in top_market_comp_data:
            top_comp_market_data['market_id'].append(top_market_comp_each[0])
            top_comp_market_data['rank'].append(top_market_comp_each[1])

    # # ***************** for OPS Leaderboard Market Level ***************** #
    #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s,'market',%s)''', (start_date,end_date,market_count,))
    #     top_market_ops_data = cr.fetchall()
    #     top_ops_market_data = {
    #                           'market_id':[],
    #                           'rank':[]
    #     }
    #     for top_market_ops_each in top_market_ops_data:
    #         top_ops_market_data['market_id'].append(top_market_ops_each[0])
    #         top_ops_market_data['rank'].append(top_market_ops_each[1])

        # ***************** for OPS Leaderboard Market Level ***************** #
        # cr.execute('''select market_id,rank from leaderboard_markets where start_date = %s and end_date = %s''', (start_date,end_date))
        # top_market_ops_data = cr.fetchall()
        # top_ops_market_data = {
        #                       'market_id':[],
        #                       'rank':[]
        # }
        # if top_market_ops_data:
        #     for top_market_ops_each in top_market_ops_data:
        #         top_ops_market_data['market_id'].append(top_market_ops_each[0])
        #         top_ops_market_data['rank'].append(top_market_ops_each[1])

    # ************* for Top Regions in Company Region Level *********** #
        cr.execute('''select * from sp_getRanking_RMS(100,%s,%s,'region','perc')''', (start_date, end_date))
        top_region_comp_data = cr.fetchall()
        top_comp_region_data = {
                                'region_id':[],
                                'rank':[]
        }
        for top_region_comp_each in top_region_comp_data:
            top_comp_region_data['region_id'].append(top_region_comp_each[0])
            top_comp_region_data['rank'].append(top_region_comp_each[1])

    # # ***************** for OPS Leaderboard Region Level ***************** #
    #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s,'region',%s)''', (start_date,end_date,region_count,))
    #     top_region_ops_data = cr.fetchall()
    #     top_ops_region_data = {
    #                           'region_id':[],
    #                           'rank':[]
    #     }
    #     for top_region_ops_each in top_region_ops_data:
    #         top_ops_region_data['region_id'].append(top_region_ops_each[0])
    #         top_ops_region_data['rank'].append(top_region_ops_each[1])

    # ***************** for OPS Leaderboard Region Level ***************** #
        # cr.execute('''select region_id,rank from leaderboard_regions where start_date = %s and end_date = %s''', (start_date,end_date))
        # top_region_ops_data = cr.fetchall()
        # top_ops_region_data = {
        #                       'region_id':[],
        #                       'rank':[]
        # }
        # if top_region_ops_data:
        #     for top_region_ops_each in top_region_ops_data:
        #         top_ops_region_data['region_id'].append(top_region_ops_each[0])
        #         top_ops_region_data['rank'].append(top_region_ops_each[1])

        comm_obj = self.pool.get('comm.vision.rewards.elite.bonus')
        package_ids = self.search(cr, uid, [('start_date','=',start_date),('end_date','=',end_date),('pre_package_comm','=',pre_prm_upload)])
        for package_data in self.browse(cr, uid, package_ids):
            emp_id = package_data.name.id
            emp_des = package_data.emp_des.id
            tot_rev = package_data.net_rev
            store_id = package_data.comm_store_id.id
            market_id = package_data.comm_market_id.id
            region_id = package_data.comm_region_id.id

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
            comm_emp_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_emp_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])
            if comm_emp_search_ids:
                vision_reward_sale_top_comp_leader_rank = 0
                vision_reward_sale_top_company_rank = 0
                vision_reward_sale_top_comp_leader_rev = 0
                vision_reward_sale_top_company_rev = 0
                # ###################### For Sales Associate Commission #########################
                for comm_emp_search_id in comm_emp_search_ids:
                    comm_obj_emp_browse = comm_obj.browse(cr, uid, comm_emp_search_id)
                    comm_formula_multi_lines = comm_obj_emp_browse.formula_multi_lines
                    for comm_formula_multi_lines_each in comm_formula_multi_lines:
                        if comm_formula_multi_lines_each.cal_type == 'count':
                            from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                            to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                        elif comm_formula_multi_lines_each.cal_type == 'perc':
                            from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * hr_count) / 100
                            to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * hr_count) / 100
                        if comm_formula_multi_lines_each.rank_base == 'all':
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                rsa_top_rank_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                                rsa_top_rank_comp_string += str(" % of RSA Revenue")
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                rsa_top_rank_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                            if emp_id in rsa_top_comp_emp_data['emp_id']:
                                vision_reward_sale_top_comp_leader_rank = rsa_top_comp_emp_data['emp_id'].index(emp_id) + 1                
                            if vision_reward_sale_top_comp_leader_rank > 0 and len(rsa_top_comp_emp_data['rank']) >= vision_reward_sale_top_comp_leader_rank:
                                vision_reward_sale_top_comp_leader_rev = rsa_top_comp_emp_data['rank'][vision_reward_sale_top_comp_leader_rank-1]
                            if (emp_id in rsa_top_comp_emp_data['emp_id']) and (vision_reward_sale_top_comp_leader_rev >= from_comm_top_company_count) and (vision_reward_sale_top_comp_leader_rev <= to_comm_top_company_count):
                                if comm_formula_multi_lines_each.pay_rev > 0.00:
                                    vision_reward_sale_top_comp_leader_payout = (tot_rev * comm_formula_multi_lines_each.pay_rev) / 100
                                elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                    vision_reward_sale_top_comp_leader_payout = comm_formula_multi_lines_each.flat_pay
                        elif comm_formula_multi_lines_each.rank_base == 'rev':                     
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                rsa_top_rank_rev_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                                rsa_top_rank_rev_comp_string += str(" % of RSA Revenue")
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                rsa_top_rank_rev_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                            if emp_id in rsa_rev_dollars_data['emp_id']:
                                vision_reward_sale_top_company_rank = rsa_rev_dollars_data['emp_id'].index(emp_id) + 1                
                            if vision_reward_sale_top_company_rank > 0 and len(rsa_rev_dollars_data['rank']) >= vision_reward_sale_top_company_rank:
                                vision_reward_sale_top_company_rev = rsa_rev_dollars_data['rank'][vision_reward_sale_top_company_rank - 1]
                            if (emp_id in rsa_rev_dollars_data['emp_id']) and (vision_reward_sale_top_company_rev >= from_comm_top_company_count) and (vision_reward_sale_top_company_rev <= to_comm_top_company_count):
                                if comm_formula_multi_lines_each.pay_rev > 0.00:
                                    vision_reward_sale_top_company_payout = (tot_rev * comm_formula_multi_lines_each.pay_rev) / 100
                                elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                    vision_reward_sale_top_company_payout = comm_formula_multi_lines_each.flat_pay
            # ################ For STL/MID/Kiosk Store Manager / Store Manager / Mall and Training Store Manager ###############
            comm_stl_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
            if comm_stl_search_ids:
                vision_reward_sale_top_percent_store = 0
                
                for comm_stl_search_id in comm_stl_search_ids:
                    comm_stl_browse_data = comm_obj.browse(cr, uid, comm_stl_search_ids[0])
                    # #################### Sales Leaderboard: Top 10% of Stores ######################
                    count = 0
                    comm_formula_multi_lines = comm_stl_browse_data.formula_multi_lines
                    for comm_formula_multi_lines_each in comm_formula_multi_lines:
                        if comm_formula_multi_lines_each.cal_type == 'count':
                            from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                            to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                        elif comm_formula_multi_lines_each.cal_type == 'perc':
                            from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * store_count) / 100
                            to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * store_count) / 100
                        if comm_formula_multi_lines_each.rank_base == 'all':
                            if store_id in top_comp_store_data['store_id']:
                                vision_reward_sale_top_percent_store = top_comp_store_data['store_id'].index(store_id) + 1
                            if vision_reward_sale_top_percent_store > 0 and len(top_comp_store_data['rank']) >= vision_reward_sale_top_percent_store:
                                vision_reward_sale_top_percent_store = top_comp_store_data['rank'][vision_reward_sale_top_percent_store-1]
                            if (store_id in top_comp_store_data['store_id']) and (vision_reward_sale_top_percent_store >= from_comm_top_company_count) and (vision_reward_sale_top_percent_store <= to_comm_top_company_count):
                                if comm_formula_multi_lines_each.pay_rev > 0.00:
                                    vision_reward_sale_top_percent_store_pay = (tot_store_rev * comm_formula_multi_lines_each.pay_rev) / 100
                                elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                    vision_reward_sale_top_percent_store_pay = comm_formula_multi_lines_each.flat_pay
                        count = count + 1
                        if (vision_reward_sale_top_percent_store_pay > 0) or (count == len(comm_formula_multi_lines)):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                store_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                                store_top_comp_string += str(" % of Store Revenue")
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                store_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                            break
      #******************# ################### For Market Manager ############################
            comm_mm_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
            if comm_mm_search_ids:
                
                vision_reward_mm_top_leader_market_rev = 0
                for comm_mm_browse_data in comm_obj.browse(cr, uid, comm_mm_search_ids):
                    count = 0
                    # ############## Top 5 Markets WV Leaderboard ########################
                    comm_formula_multi_lines = comm_mm_browse_data.formula_multi_lines
                    for comm_formula_multi_lines_each in comm_formula_multi_lines:
                        if comm_formula_multi_lines_each.cal_type == 'count':
                            from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                            to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                        elif comm_formula_multi_lines_each.cal_type == 'perc':
                            from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * market_count) / 100
                            to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * market_count) / 100
                        if comm_formula_multi_lines_each.rank_base == 'all':
                            if market_id in top_comp_market_data['market_id']:
                                vision_reward_mm_top_leader_market_rev = top_comp_market_data['market_id'].index(market_id) + 1
                            if vision_reward_mm_top_leader_market_rev > 0 and len(top_comp_market_data['rank']) >= vision_reward_mm_top_leader_market_rev:
                                vision_reward_mm_top_leader_market_rev = top_comp_market_data['rank'][vision_reward_mm_top_leader_market_rev-1]
                            if (market_id in top_comp_market_data['market_id']) and (vision_reward_mm_top_leader_market_rev >= from_comm_top_company_count) and (vision_reward_mm_top_leader_market_rev <= to_comm_top_company_count):
                                if comm_formula_multi_lines_each.pay_rev > 0.00:
                                    vision_reward_mm_top_leader_market_payout = (tot_market_rev * comm_formula_multi_lines_each.pay_rev) / 100
                                elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                    vision_reward_mm_top_leader_market_payout = comm_formula_multi_lines_each.flat_pay
                        count = count + 1
                        if (vision_reward_mm_top_leader_market_payout > 0) or (count == len(comm_formula_multi_lines)):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                market_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                                market_top_comp_string += str(" % of Market Revenue")
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                market_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                            break
                # ################ Top Region Leaderboard Ranking ###########################
            comm_dos_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
            if comm_dos_search_ids:
                
                vision_reward_dos_top_region_rev = 0
                comm_dos_browse_data = comm_obj.browse(cr, uid, comm_dos_search_ids[0])
                # ################## Top Region Leaderboard Ranking #############################

                comm_formula_multi_lines = comm_dos_browse_data.formula_multi_lines
                count = 0
                for comm_formula_multi_lines_each in comm_formula_multi_lines:
                    if comm_formula_multi_lines_each.cal_type == 'count':
                        from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                        to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                    elif comm_formula_multi_lines_each.cal_type == 'perc':
                        from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * region_count) / 100
                        to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * region_count) / 100
                    if comm_formula_multi_lines_each.rank_base == 'all':
                        if region_id in top_comp_region_data['region_id']:
                            vision_reward_dos_top_region_rev = top_comp_region_data['region_id'].index(region_id) + 1
                        if vision_reward_dos_top_region_rev > 0 and len(top_comp_region_data['rank']) >= vision_reward_dos_top_region_rev:
                            vision_reward_dos_top_region_rev = top_comp_region_data['rank'][vision_reward_dos_top_region_rev-1]
                        if (region_id in top_comp_region_data['region_id']) and (vision_reward_dos_top_region_rev >= from_comm_top_company_count) and (vision_reward_dos_top_region_rev <= to_comm_top_company_count):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                vision_reward_dos_top_leader_payout = (tot_region_rev * comm_formula_multi_lines_each.pay_rev) / 100
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                vision_reward_dos_top_leader_payout = comm_formula_multi_lines_each.flat_pay
                    count = count + 1
                    if (vision_reward_dos_top_leader_payout > 0) or (count == len(comm_formula_multi_lines)):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            region_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                            region_top_comp_string += str(" % of Region Revenue")
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            region_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                        break
        #############*************** OPS Leaderboard Ranking ******************####################
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
            comm_sto_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
            if comm_sto_ops_search_ids:
                comm_sto_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_sto_ops_search_ids[0])
                vision_reward_ops_top_percent_store = 0

                comm_formula_multi_lines = comm_sto_ops_browse_data.formula_multi_lines
                cr.execute('''select rank from leaderboard_sap where store_id=%s and start_date=%s and end_date=%s''', (store_id,start_date, end_date))
                store_top_hr_ids = cr.fetchall()
                count = 0
                for comm_formula_multi_lines_each in comm_formula_multi_lines:
                    if comm_formula_multi_lines_each.cal_type == 'count':
                        from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                        to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                    elif comm_formula_multi_lines_each.cal_type == 'perc':
                        from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * store_count) / 100
                        to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * store_count) / 100
                    if comm_formula_multi_lines_each.rank_base == 'all':
                        if store_top_hr_ids:
                            vision_reward_ops_top_percent_store = store_top_hr_ids[0][0]
                        if not vision_reward_ops_top_percent_store:
                            vision_reward_ops_top_percent_store = 0
                        if (vision_reward_ops_top_percent_store >= from_comm_top_company_count) and (vision_reward_ops_top_percent_store <= to_comm_top_company_count):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                vision_reward_ops_top_store_pay = (tot_store_rev * comm_formula_multi_lines_each.pay_rev) / 100
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                vision_reward_ops_top_store_pay = comm_formula_multi_lines_each.flat_pay
                    count = count + 1
                    if (vision_reward_ops_top_store_pay > 0) or (count == len(comm_formula_multi_lines)):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            ops_leader_store_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                            ops_leader_store_string += str(" % of RSA Revenue")
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            ops_leader_store_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                        break
                    # # #################### Operations Leaderboard: Top 10% of Stores ######################
                    # vision_reward_ops_top_percent_store_amount = comm_stl_browse_data.comm_stl_amount_store_ops
                    # vision_reward_stl_store_percent_ops = comm_stl_browse_data.comm_stl_top_store_percent_ops
                    # comm_stl_top_rank_store_ops = comm_stl_browse_data.comm_stl_top_rank_store_ops
                    # vision_reward_mall_inline_num_ops = comm_stl_browse_data.comm_stl_mall_inline_loc_ops
                    # vision_reward_mall_inline_leader_payout_ops = comm_stl_browse_data.comm_stl_mall_inline_loc_pay_ops
                    # vision_reward_kiosk_num_ops = comm_stl_browse_data.comm_stl_top_kiosk_ops
                    # vision_reward_mall_kiosk_leader_payout_ops = comm_stl_browse_data.comm_stl_mall_kiosk_loc_pay_ops
                    # store_top_hr_ops = []
                    # top_mall_store_ops = []
                    # top_kiosk_store_ops = []
                    # vision_reward_ops_top_percent_store_rank = 0
                    # ops_leader_store_string += str("$ %s"%(vision_reward_ops_top_percent_store_amount))
                    # if vision_reward_stl_store_percent_ops > 0.00:    
                    #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s,'store',%s)''', (start_date, end_date,store_count, ))
                    #     store_top_hr_ids = cr.fetchall()
                    #     for store_top_hr_id in store_top_hr_ids:
                    #         store_top_hr_ops.append(store_top_hr_id[0])
                    #     if vision_reward_stl_store_percent_ops > 0.00:
                    #         elite_bonus_stl_store_percent_ops = (vision_reward_stl_store_percent_ops * store_count)/100
                    #     elif comm_stl_top_rank_store_ops > 0.00:
                    #         elite_bonus_stl_store_percent_ops = comm_stl_top_rank_store_ops
                    #     if store_id in store_top_hr_ops:
                    #         vision_reward_ops_top_percent_store_rank = store_top_hr_ops.index(store_id) + 1
                    #     # ############### Payout based on OR conditions for STL/MID/SM ##################33
                    #     if (store_id in store_top_hr_ops) and (vision_reward_ops_top_percent_store_rank <= elite_bonus_stl_store_percent_ops):
                    #         vision_reward_ops_top_store_pay = vision_reward_ops_top_percent_store_amount
                    #     vision_reward_ops_top_percent_store = vision_reward_ops_top_percent_store_rank
            comm_mkt_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
            if comm_mkt_ops_search_ids:
                comm_mkt_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_mkt_ops_search_ids[0])
                vision_reward_mm_top_ops_market_rev = 0

                cr.execute('''select rank from leaderboard_markets where market_id=%s and start_date=%s and end_date=%s''', (market_id,start_date, end_date))
                top_mm_markets = cr.fetchall()
                comm_formula_multi_lines = comm_mkt_ops_browse_data.formula_multi_lines
                count = 0
                for comm_formula_multi_lines_each in comm_formula_multi_lines:
                    if comm_formula_multi_lines_each.cal_type == 'count':
                        from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                        to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                    elif comm_formula_multi_lines_each.cal_type == 'perc':
                        from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * market_count) / 100
                        to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * market_count) / 100
                    if comm_formula_multi_lines_each.rank_base == 'all':
                        if top_mm_markets:
                            vision_reward_mm_top_ops_market_rev = top_mm_markets[0][0]
                        if not vision_reward_mm_top_ops_market_rev:
                            vision_reward_mm_top_ops_market_rev = 0
                        if (vision_reward_mm_top_ops_market_rev >= from_comm_top_company_count) and (vision_reward_mm_top_ops_market_rev <= to_comm_top_company_count):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                vision_reward_mm_top_ops_market_payout = (tot_market_rev * comm_formula_multi_lines_each.pay_rev) / 100
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                vision_reward_mm_top_ops_market_payout = comm_formula_multi_lines_each.flat_pay
                    count = count + 1
                    if (vision_reward_mm_top_ops_market_payout > 0) or (count == len(comm_formula_multi_lines)):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            ops_leader_market_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                            ops_leader_market_string += str(" % of RSA Revenue")
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            ops_leader_market_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                        break
                # # ############## Top 5 Markets Operations Leaderboard ########################
                # comm_mm_top_market_opr = comm_mm_browse_data.comm_mm_top_market_opr
                # cr.execute("select count(*) from market_place")
                # market_ids = cr.fetchall()
                # market_count = market_ids[0][0]
                # if len(comm_mm_top_market_opr) > 0:
                #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s, 'market',%s)''', (start_date, end_date, market_count))
                #     top_mm_markets = cr.fetchall()
                #     top_mm_markets_ids_opr = []
                #     for top_mm_market_id in top_mm_markets:
                #         top_mm_markets_ids_opr.append(top_mm_market_id[0])
                #     vision_reward_mm_top_ops_market_rev = top_mm_markets_ids_opr.index(market_id) + 1
                #     for comm_mm_top_market_data in comm_mm_top_market_opr:
                #         if comm_mm_top_market_data.comm_seq == vision_reward_mm_top_ops_market_rev:
                #             vision_reward_mm_top_ops_market_payout = comm_mm_top_market_data.comm_amount
                #     if vision_reward_mm_top_ops_market_payout > 0.00:
                #         ops_leader_market_string += str("$ %s"%(vision_reward_mm_top_ops_market_payout))
                #     else:
                #         ops_leader_market_string += str("$ %s"%(comm_mm_top_market_opr[0].comm_amount))
                # ############## Top 5 Markets Operations Leaderboard ########################
            comm_reg_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
            if comm_reg_ops_search_ids:
                comm_reg_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_reg_ops_search_ids[0])
                vision_reward_dos_top_ops_rev = 0

                comm_formula_multi_lines = comm_reg_ops_browse_data.formula_multi_lines
                cr.execute('''select rank from leaderboard_regions where region_id=%s and start_date=%s and end_date=%s''', (region_id,start_date, end_date))
                top_dos_regions = cr.fetchall()
                count = 0
                for comm_formula_multi_lines_each in comm_formula_multi_lines:
                    if comm_formula_multi_lines_each.cal_type == 'count':
                        from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                        to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                    elif comm_formula_multi_lines_each.cal_type == 'perc':
                        from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * region_count) / 100
                        to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * region_count) / 100
                    if comm_formula_multi_lines_each.rank_base == 'all':
                        if top_dos_regions:
                            vision_reward_dos_top_ops_rev = top_dos_regions[0][0]
                        if not vision_reward_dos_top_ops_rev:
                            vision_reward_dos_top_ops_rev = 0
                        if (vision_reward_dos_top_ops_rev >= from_comm_top_company_count) and (vision_reward_dos_top_ops_rev <= to_comm_top_company_count):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                vision_reward_dos_top_ops_payout = (tot_region_rev * comm_formula_multi_lines_each.pay_rev) / 100
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                vision_reward_dos_top_ops_payout = comm_formula_multi_lines_each.flat_pay
                    count = count + 1
                    if (vision_reward_dos_top_ops_payout > 0) or (count == len(comm_formula_multi_lines)):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            ops_leader_region_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                            ops_leader_region_string += str(" % of RSA Revenue")
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            ops_leader_region_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                        break
                # # ################## Top Region Operations Leaderboard Ranking #############################
                # comm_dos_top_region_opr = comm_dos_browse_data.comm_dos_top_region_rank_opr
                # vision_reward_dos_top_ops_rev = comm_dos_browse_data.comm_dos_amount_rank_opr
                # if comm_dos_top_region_opr > 0:
                #     cr.execute('''select id, name, rank from get_opsleaderboard_stats_odoo(%s, %s, 'region',%s)''', (start_date, end_date, region_count))
                #     top_dos_regions = cr.fetchall()
                #     top_dos_regions_ids_opr = []
                #     ops_leader_region_string += str("$ %s"%(vision_reward_dos_top_ops_rev))
                #     for top_dos_regions_id in top_dos_regions:
                #         top_dos_regions_ids_opr.append(top_dos_regions_id[0])
                #     vision_reward_dos_top_ops_rev = top_dos_regions_ids_opr.index(region_id) + 1
                #     if (region_id in top_dos_regions_ids_opr) and (vision_reward_dos_top_ops_rev <= comm_dos_top_region_opr):
                #         vision_reward_dos_top_ops_payout = comm_dos_browse_data.comm_dos_amount_rank_opr

            gross_payout = package_data.gross_payout

            gross_payout = gross_payout + vision_reward_sale_top_market_payout + vision_reward_sale_top_company_payout 
            gross_payout = gross_payout + vision_reward_dos_top_region_payout + vision_reward_mm_top_market_payout + vision_reward_sale_top_percent_store_pay 
            gross_payout = gross_payout + vision_reward_stl_top_company_payout + vision_reward_dos_top_leader_payout + float(vision_reward_mm_top_leader_market_payout)
            gross_payout = gross_payout + vision_reward_sale_top_comp_leader_payout + vision_reward_ops_top_store_pay + float(vision_reward_mm_top_ops_market_payout) + vision_reward_dos_top_ops_payout

            self.write(cr, uid, [package_data.id], {
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
                                    'gross_payout':gross_payout
                })

    def calculate_elite_bonus_each(self, cr, uid, ids, context=None):    
        model_obj = self.pool.get('ir.model')
        model_emp_search_id = model_obj.search(cr, uid, [('model', '=', 'hr.employee')])
        model_store_search_id = model_obj.search(cr, uid, [('model', '=', 'sap.store')])
        model_market_search_id = model_obj.search(cr, uid, [('model', '=', 'market.place')])
        model_region_search_id = model_obj.search(cr, uid, [('model', '=', 'market.regions')])
        model_comp_search_id = model_obj.search(cr, uid, [('model', '=', 'res.company')])

        comm_obj = self.pool.get('comm.vision.rewards.elite.bonus')
        package_data = self.browse(cr, uid, ids[0])
        emp_id = package_data.name.id
        start_date = package_data.start_date
        end_date = package_data.end_date
        emp_des = package_data.emp_des.id
        tot_rev = package_data.net_rev
        store_id = package_data.comm_store_id.id
        market_id = package_data.comm_market_id.id
        region_id = package_data.comm_region_id.id

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
        if comm_emp_search_ids:
            vision_reward_sale_top_comp_leader_rank = 0
            vision_reward_sale_top_company_rank = 0
            vision_reward_sale_top_comp_leader_rev = 0
            vision_reward_sale_top_company_rev = 0
            cr.execute('''select count(hr.id) from hr_employee hr, hr_job job, resource_resource res
where hr.resource_id = res.id and res.active=true
and hr.job_id=job.id and job.model_id in ('rsa','stl')''')
            hr_ids = cr.fetchall()
            hr_count = hr_ids[0][0]
            # ###################### For Sales Associate Commission #########################
            for comm_emp_search_id in comm_emp_search_ids:
                comm_obj_emp_browse = comm_obj.browse(cr, uid, comm_emp_search_id)
                company_top_hr = []
                company_top_rank = []
                comm_formula_multi_lines = comm_obj_emp_browse.formula_multi_lines
                for comm_formula_multi_lines_each in comm_formula_multi_lines:
                    if comm_formula_multi_lines_each.cal_type == 'count':
                        from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                        to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                    elif comm_formula_multi_lines_each.cal_type == 'perc':
                        from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * hr_count) / 100
                        to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * hr_count) / 100
                    if comm_formula_multi_lines_each.rank_base == 'all':
                        cr.execute('''select * from sp_getRanking_SalesRep(%s,%s,%s,null,null)''', (100, start_date, end_date))
                        company_top_hr_ids = cr.fetchall()
                        for company_top_hr_id in company_top_hr_ids:
                            company_top_hr.append(company_top_hr_id[0])
                            company_top_rank.append(company_top_hr_id[1])
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            rsa_top_rank_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                            rsa_top_rank_comp_string += str(" % of RSA Revenue")
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            rsa_top_rank_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                        if emp_id in company_top_hr:
                            vision_reward_sale_top_comp_leader_rank = company_top_hr.index(emp_id) + 1                
                        if vision_reward_sale_top_comp_leader_rank > 0 and len(company_top_rank) >= vision_reward_sale_top_comp_leader_rank:
                            vision_reward_sale_top_comp_leader_rev = company_top_rank[vision_reward_sale_top_comp_leader_rank-1]
                        if (emp_id in company_top_hr) and (vision_reward_sale_top_comp_leader_rev >= from_comm_top_company_count) and (vision_reward_sale_top_comp_leader_rev <= to_comm_top_company_count):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                vision_reward_sale_top_comp_leader_payout = (tot_rev * comm_formula_multi_lines_each.pay_rev) / 100
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                vision_reward_sale_top_comp_leader_payout = comm_formula_multi_lines_each.flat_pay
                    elif comm_formula_multi_lines_each.rank_base == 'rev':
                        cr.execute('''select * from get_revenue_perc_by_emp_odoo(%s, %s, 'rsa', %s)''', (start_date, end_date,100))
                        company_top_hr_ids = cr.fetchall()
                        for company_top_hr_id in company_top_hr_ids:
                            company_top_hr.append(company_top_hr_id[0])
                            company_top_rank.append(company_top_hr_id[2])                        
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            rsa_top_rank_rev_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                            rsa_top_rank_rev_comp_string += str(" % of RSA Revenue")
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            rsa_top_rank_rev_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                        if emp_id in company_top_hr:
                            vision_reward_sale_top_company_rank = company_top_hr.index(emp_id) + 1                
                        if vision_reward_sale_top_company_rank > 0 and len(company_top_rank) >= vision_reward_sale_top_company_rank:
                            vision_reward_sale_top_company_rev = company_top_rank[vision_reward_sale_top_company_rank - 1]
                        if (emp_id in company_top_hr) and (vision_reward_sale_top_company_rev >= from_comm_top_company_count) and (vision_reward_sale_top_company_rev <= to_comm_top_company_count):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                vision_reward_sale_top_company_payout = (tot_rev * comm_formula_multi_lines_each.pay_rev) / 100
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                vision_reward_sale_top_company_payout = comm_formula_multi_lines_each.flat_pay
        # ################ For STL/MID/Kiosk Store Manager / Store Manager / Mall and Training Store Manager ###############
        comm_stl_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
        if comm_stl_search_ids:
            vision_reward_sale_top_percent_store = 0
            cr.execute("select count(distinct(sap_id)) from sap_tracker where store_inactive=false and end_date >= %s",(start_date,))
            store_count = cr.fetchall()
            store_count = store_count[0][0]
            for comm_stl_search_id in comm_stl_search_ids:
                comm_stl_browse_data = comm_obj.browse(cr, uid, comm_stl_search_ids[0])
                # #################### Sales Leaderboard: Top 10% of Stores ######################
                store_top_hr = []
                store_top_rank = []                
                cr.execute('''select * from sp_getRanking_RMS(%s,%s,%s,'store','perc')''', (100, start_date, end_date))
                store_top_hr_ids = cr.fetchall()
                count = 0
                comm_formula_multi_lines = comm_stl_browse_data.formula_multi_lines
                for comm_formula_multi_lines_each in comm_formula_multi_lines:
                    if comm_formula_multi_lines_each.cal_type == 'count':
                        from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                        to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                    elif comm_formula_multi_lines_each.cal_type == 'perc':
                        from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * store_count) / 100
                        to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * store_count) / 100
                    if comm_formula_multi_lines_each.rank_base == 'all':
                        for store_top_hr_id in store_top_hr_ids:
                            store_top_hr.append(store_top_hr_id[0])
                            store_top_rank.append(store_top_hr_id[1])
                        if store_id in store_top_hr:
                            vision_reward_sale_top_percent_store = store_top_hr.index(store_id) + 1
                        if vision_reward_sale_top_percent_store > 0 and len(store_top_rank) >= vision_reward_sale_top_percent_store:
                            vision_reward_sale_top_percent_store = store_top_rank[vision_reward_sale_top_percent_store-1]
                        if (store_id in store_top_hr) and (vision_reward_sale_top_percent_store >= from_comm_top_company_count) and (vision_reward_sale_top_percent_store <= to_comm_top_company_count):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                vision_reward_sale_top_percent_store_pay = (tot_store_rev * comm_formula_multi_lines_each.pay_rev) / 100
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                vision_reward_sale_top_percent_store_pay = comm_formula_multi_lines_each.flat_pay
                    count = count + 1
                    if (vision_reward_sale_top_percent_store_pay > 0) or (count == len(comm_formula_multi_lines)):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            store_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                            store_top_comp_string += str(" % of Store Revenue")
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            store_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                        break
  #******************# ################### For Market Manager ############################
        comm_mm_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
        if comm_mm_search_ids:
            cr.execute("select count(distinct(market_id)) from market_tracker where end_date >= %s",(start_date,))
            market_count = cr.fetchall()
            market_count = market_count[0][0]
            vision_reward_mm_top_leader_market_rev = 0
            for comm_mm_browse_data in comm_obj.browse(cr, uid, comm_mm_search_ids):
                top_mm_markets_ids = []
                top_mm_markets_ranks = []
                count = 0
                cr.execute('''select * from sp_getRanking_RMS(100,%s,%s,'market','perc')''', (start_date, end_date))
                top_mm_markets = cr.fetchall()
                # ############## Top 5 Markets WV Leaderboard ########################
                comm_formula_multi_lines = comm_mm_browse_data.formula_multi_lines
                for comm_formula_multi_lines_each in comm_formula_multi_lines:
                    if comm_formula_multi_lines_each.cal_type == 'count':
                        from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                        to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                    elif comm_formula_multi_lines_each.cal_type == 'perc':
                        from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * market_count) / 100
                        to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * market_count) / 100
                    if comm_formula_multi_lines_each.rank_base == 'all':                   
                        for top_mm_market_id in top_mm_markets:
                            top_mm_markets_ids.append(top_mm_market_id[0])
                            top_mm_markets_ranks.append(top_mm_market_id[1])
                        if market_id in top_mm_markets_ids:
                            vision_reward_mm_top_leader_market_rev = top_mm_markets_ids.index(market_id) + 1
                        if vision_reward_mm_top_leader_market_rev > 0 and len(top_mm_markets_ranks) >= vision_reward_mm_top_leader_market_rev:
                            vision_reward_mm_top_leader_market_rev = top_mm_markets_ranks[vision_reward_mm_top_leader_market_rev-1]
                        if (market_id in top_mm_markets_ids) and (vision_reward_mm_top_leader_market_rev >= from_comm_top_company_count) and (vision_reward_mm_top_leader_market_rev <= to_comm_top_company_count):
                            if comm_formula_multi_lines_each.pay_rev > 0.00:
                                vision_reward_mm_top_leader_market_payout = (tot_market_rev * comm_formula_multi_lines_each.pay_rev) / 100
                            elif comm_formula_multi_lines_each.flat_pay > 0.00:
                                vision_reward_mm_top_leader_market_payout = comm_formula_multi_lines_each.flat_pay
                    count = count + 1
                    if (vision_reward_mm_top_leader_market_payout > 0) or (count == len(comm_formula_multi_lines)):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            market_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                            market_top_comp_string += str(" % of Market Revenue")
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            market_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                        break
            # ################ Top Region Leaderboard Ranking ###########################
        comm_dos_search_ids = comm_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)])    
        if comm_dos_search_ids:
            cr.execute("select count(distinct(region_id)) from region_tracker where end_date >= %s",(start_date,))
            region_ids = cr.fetchall()
            region_count = region_ids[0][0]
            vision_reward_dos_top_region_rev = 0
            comm_dos_browse_data = comm_obj.browse(cr, uid, comm_dos_search_ids[0])
            # ################## Top Region Leaderboard Ranking #############################
            top_dos_regions_ids = []
            top_dos_regions_ranks = []

            comm_formula_multi_lines = comm_dos_browse_data.formula_multi_lines
            count = 0
            for comm_formula_multi_lines_each in comm_formula_multi_lines:
                if comm_formula_multi_lines_each.cal_type == 'count':
                    from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                    to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                elif comm_formula_multi_lines_each.cal_type == 'perc':
                    from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * region_count) / 100
                    to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * region_count) / 100
                if comm_formula_multi_lines_each.rank_base == 'all':
                    cr.execute('''select * from sp_getRanking_RMS(100,%s,%s,'region','perc')''', (start_date, end_date))
                    top_dos_regions = cr.fetchall()
                    for top_dos_regions_id in top_dos_regions:
                        top_dos_regions_ids.append(top_dos_regions_id[0])
                        top_dos_regions_ranks.append(top_dos_regions_id[1])
                    if region_id in top_dos_regions_ids:
                        vision_reward_dos_top_region_rev = top_dos_regions_ids.index(region_id) + 1
                    if vision_reward_dos_top_region_rev > 0 and len(top_dos_regions_ranks) >= vision_reward_dos_top_region_rev:
                        vision_reward_dos_top_region_rev = top_dos_regions_ranks[vision_reward_dos_top_region_rev-1]
                    if (region_id in top_dos_regions_ids) and (vision_reward_dos_top_region_rev >= from_comm_top_company_count) and (vision_reward_dos_top_region_rev <= to_comm_top_company_count):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            vision_reward_dos_top_leader_payout = (tot_region_rev * comm_formula_multi_lines_each.pay_rev) / 100
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            vision_reward_dos_top_leader_payout = comm_formula_multi_lines_each.flat_pay
                count = count + 1
                if (vision_reward_dos_top_leader_payout > 0) or (count == len(comm_formula_multi_lines)):
                    if comm_formula_multi_lines_each.pay_rev > 0.00:
                        region_top_comp_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                        region_top_comp_string += str(" % of Region Revenue")
                    elif comm_formula_multi_lines_each.flat_pay > 0.00:
                        region_top_comp_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                    break
    #############*************** OPS Leaderboard Ranking ******************####################
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
        comm_sto_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_store_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
        if comm_sto_ops_search_ids:
            comm_sto_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_sto_ops_search_ids[0])
            vision_reward_ops_top_percent_store = 0

            comm_formula_multi_lines = comm_sto_ops_browse_data.formula_multi_lines
            cr.execute('''select rank from leaderboard_sap where store_id=%s and start_date=%s and end_date=%s''', (store_id,start_date, end_date))
            store_top_hr_ids = cr.fetchall()
            count = 0
            for comm_formula_multi_lines_each in comm_formula_multi_lines:
                if comm_formula_multi_lines_each.cal_type == 'count':
                    from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                    to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                elif comm_formula_multi_lines_each.cal_type == 'perc':
                    from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * store_count) / 100
                    to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * store_count) / 100
                if comm_formula_multi_lines_each.rank_base == 'all':
                    if store_top_hr_ids:
                        vision_reward_ops_top_percent_store = store_top_hr_ids[0][0]
                    if not vision_reward_ops_top_percent_store:
                        vision_reward_ops_top_percent_store = 0
                    if (vision_reward_ops_top_percent_store >= from_comm_top_company_count) and (vision_reward_ops_top_percent_store <= to_comm_top_company_count):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            vision_reward_ops_top_store_pay = (tot_store_rev * comm_formula_multi_lines_each.pay_rev) / 100
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            vision_reward_ops_top_store_pay = comm_formula_multi_lines_each.flat_pay
                count = count + 1
                if (vision_reward_ops_top_store_pay > 0) or (count == len(comm_formula_multi_lines)):
                    if comm_formula_multi_lines_each.pay_rev > 0.00:
                        ops_leader_store_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                        ops_leader_store_string += str(" % of RSA Revenue")
                    elif comm_formula_multi_lines_each.flat_pay > 0.00:
                        ops_leader_store_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                    break
                # # #################### Operations Leaderboard: Top 10% of Stores ######################
                # vision_reward_ops_top_percent_store_amount = comm_stl_browse_data.comm_stl_amount_store_ops
                # vision_reward_stl_store_percent_ops = comm_stl_browse_data.comm_stl_top_store_percent_ops
                # comm_stl_top_rank_store_ops = comm_stl_browse_data.comm_stl_top_rank_store_ops
                # vision_reward_mall_inline_num_ops = comm_stl_browse_data.comm_stl_mall_inline_loc_ops
                # vision_reward_mall_inline_leader_payout_ops = comm_stl_browse_data.comm_stl_mall_inline_loc_pay_ops
                # vision_reward_kiosk_num_ops = comm_stl_browse_data.comm_stl_top_kiosk_ops
                # vision_reward_mall_kiosk_leader_payout_ops = comm_stl_browse_data.comm_stl_mall_kiosk_loc_pay_ops
                # store_top_hr_ops = []
                # top_mall_store_ops = []
                # top_kiosk_store_ops = []
                # vision_reward_ops_top_percent_store_rank = 0
                # ops_leader_store_string += str("$ %s"%(vision_reward_ops_top_percent_store_amount))
                # if vision_reward_stl_store_percent_ops > 0.00:    
                #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s,'store',%s)''', (start_date, end_date,store_count, ))
                #     store_top_hr_ids = cr.fetchall()
                #     for store_top_hr_id in store_top_hr_ids:
                #         store_top_hr_ops.append(store_top_hr_id[0])
                #     if vision_reward_stl_store_percent_ops > 0.00:
                #         elite_bonus_stl_store_percent_ops = (vision_reward_stl_store_percent_ops * store_count)/100
                #     elif comm_stl_top_rank_store_ops > 0.00:
                #         elite_bonus_stl_store_percent_ops = comm_stl_top_rank_store_ops
                #     if store_id in store_top_hr_ops:
                #         vision_reward_ops_top_percent_store_rank = store_top_hr_ops.index(store_id) + 1
                #     # ############### Payout based on OR conditions for STL/MID/SM ##################33
                #     if (store_id in store_top_hr_ops) and (vision_reward_ops_top_percent_store_rank <= elite_bonus_stl_store_percent_ops):
                #         vision_reward_ops_top_store_pay = vision_reward_ops_top_percent_store_amount
                #     vision_reward_ops_top_percent_store = vision_reward_ops_top_percent_store_rank
        comm_mkt_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_market_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
        if comm_mkt_ops_search_ids:
            comm_mkt_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_mkt_ops_search_ids[0])
            vision_reward_mm_top_ops_market_rev = 0

            cr.execute('''select rank from leaderboard_markets where market_id=%s and start_date=%s and end_date=%s''', (market_id,start_date, end_date))
            top_mm_markets = cr.fetchall()
            comm_formula_multi_lines = comm_mkt_ops_browse_data.formula_multi_lines
            count = 0
            for comm_formula_multi_lines_each in comm_formula_multi_lines:
                if comm_formula_multi_lines_each.cal_type == 'count':
                    from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                    to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                elif comm_formula_multi_lines_each.cal_type == 'perc':
                    from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * market_count) / 100
                    to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * market_count) / 100
                if comm_formula_multi_lines_each.rank_base == 'all':
                    if top_mm_markets:
                        vision_reward_mm_top_ops_market_rev = top_mm_markets[0][0]
                    if not vision_reward_mm_top_ops_market_rev:
                        vision_reward_mm_top_ops_market_rev = 0
                    if (vision_reward_mm_top_ops_market_rev >= from_comm_top_company_count) and (vision_reward_mm_top_ops_market_rev <= to_comm_top_company_count):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            vision_reward_mm_top_ops_market_payout = (tot_market_rev * comm_formula_multi_lines_each.pay_rev) / 100
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            vision_reward_mm_top_ops_market_payout = comm_formula_multi_lines_each.flat_pay
                count = count + 1
                if (vision_reward_mm_top_ops_market_payout > 0) or (count == len(comm_formula_multi_lines)):
                    if comm_formula_multi_lines_each.pay_rev > 0.00:
                        ops_leader_market_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                        ops_leader_market_string += str(" % of RSA Revenue")
                    elif comm_formula_multi_lines_each.flat_pay > 0.00:
                        ops_leader_market_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                    break
            # # ############## Top 5 Markets Operations Leaderboard ########################
            # comm_mm_top_market_opr = comm_mm_browse_data.comm_mm_top_market_opr
            # cr.execute("select count(*) from market_place")
            # market_ids = cr.fetchall()
            # market_count = market_ids[0][0]
            # if len(comm_mm_top_market_opr) > 0:
            #     cr.execute('''select id from get_opsleaderboard_stats_odoo(%s, %s, 'market',%s)''', (start_date, end_date, market_count))
            #     top_mm_markets = cr.fetchall()
            #     top_mm_markets_ids_opr = []
            #     for top_mm_market_id in top_mm_markets:
            #         top_mm_markets_ids_opr.append(top_mm_market_id[0])
            #     vision_reward_mm_top_ops_market_rev = top_mm_markets_ids_opr.index(market_id) + 1
            #     for comm_mm_top_market_data in comm_mm_top_market_opr:
            #         if comm_mm_top_market_data.comm_seq == vision_reward_mm_top_ops_market_rev:
            #             vision_reward_mm_top_ops_market_payout = comm_mm_top_market_data.comm_amount
            #     if vision_reward_mm_top_ops_market_payout > 0.00:
            #         ops_leader_market_string += str("$ %s"%(vision_reward_mm_top_ops_market_payout))
            #     else:
            #         ops_leader_market_string += str("$ %s"%(comm_mm_top_market_opr[0].comm_amount))
            # ############## Top 5 Markets Operations Leaderboard ########################
        comm_reg_ops_search_ids = ops_leader_obj.search(cr, uid, [('comm_designation', '=', emp_des), ('spiff_model', '=', model_region_search_id[0]), ('comm_start_date', '<=', start_date), ('comm_end_date', '>=', end_date), ('comm_inactive', '=', False)]) 
        if comm_reg_ops_search_ids:
            comm_reg_ops_browse_data = ops_leader_obj.browse(cr, uid, comm_reg_ops_search_ids[0])
            vision_reward_dos_top_ops_rev = 0

            comm_formula_multi_lines = comm_reg_ops_browse_data.formula_multi_lines
            cr.execute('''select rank from leaderboard_regions where region_id=%s and start_date=%s and end_date=%s''', (region_id,start_date, end_date))
            top_dos_regions = cr.fetchall()
            count = 0
            for comm_formula_multi_lines_each in comm_formula_multi_lines:
                if comm_formula_multi_lines_each.cal_type == 'count':
                    from_comm_top_company_count = comm_formula_multi_lines_each.from_cond
                    to_comm_top_company_count = comm_formula_multi_lines_each.to_cond
                elif comm_formula_multi_lines_each.cal_type == 'perc':
                    from_comm_top_company_count = (comm_formula_multi_lines_each.from_cond * region_count) / 100
                    to_comm_top_company_count = (comm_formula_multi_lines_each.to_cond * region_count) / 100
                if comm_formula_multi_lines_each.rank_base == 'all':
                    if top_dos_regions:
                        vision_reward_dos_top_ops_rev = top_dos_regions[0][0]
                    if not vision_reward_dos_top_ops_rev:
                        vision_reward_dos_top_ops_rev = 0
                    if (vision_reward_dos_top_ops_rev >= from_comm_top_company_count) and (vision_reward_dos_top_ops_rev <= to_comm_top_company_count):
                        if comm_formula_multi_lines_each.pay_rev > 0.00:
                            vision_reward_dos_top_ops_payout = (tot_region_rev * comm_formula_multi_lines_each.pay_rev) / 100
                        elif comm_formula_multi_lines_each.flat_pay > 0.00:
                            vision_reward_dos_top_ops_payout = comm_formula_multi_lines_each.flat_pay
                count = count + 1
                if (vision_reward_dos_top_ops_payout > 0) or (count == len(comm_formula_multi_lines)):
                    if comm_formula_multi_lines_each.pay_rev > 0.00:
                        ops_leader_region_string += str("%s"%(comm_formula_multi_lines_each.pay_rev))
                        ops_leader_region_string += str(" % of RSA Revenue")
                    elif comm_formula_multi_lines_each.flat_pay > 0.00:
                        ops_leader_region_string += str("$ %s"%(comm_formula_multi_lines_each.flat_pay))
                    break
            # # ################## Top Region Operations Leaderboard Ranking #############################
            # comm_dos_top_region_opr = comm_dos_browse_data.comm_dos_top_region_rank_opr
            # vision_reward_dos_top_ops_rev = comm_dos_browse_data.comm_dos_amount_rank_opr
            # if comm_dos_top_region_opr > 0:
            #     cr.execute('''select id, name, rank from get_opsleaderboard_stats_odoo(%s, %s, 'region',%s)''', (start_date, end_date, region_count))
            #     top_dos_regions = cr.fetchall()
            #     top_dos_regions_ids_opr = []
            #     ops_leader_region_string += str("$ %s"%(vision_reward_dos_top_ops_rev))
            #     for top_dos_regions_id in top_dos_regions:
            #         top_dos_regions_ids_opr.append(top_dos_regions_id[0])
            #     vision_reward_dos_top_ops_rev = top_dos_regions_ids_opr.index(region_id) + 1
            #     if (region_id in top_dos_regions_ids_opr) and (vision_reward_dos_top_ops_rev <= comm_dos_top_region_opr):
            #         vision_reward_dos_top_ops_payout = comm_dos_browse_data.comm_dos_amount_rank_opr

        gross_payout = package_data.gross_payout

        gross_payout = gross_payout + vision_reward_sale_top_market_payout + vision_reward_sale_top_company_payout 
        gross_payout = gross_payout + vision_reward_dos_top_region_payout + vision_reward_mm_top_market_payout + vision_reward_sale_top_percent_store_pay 
        gross_payout = gross_payout + vision_reward_stl_top_company_payout + vision_reward_dos_top_leader_payout + float(vision_reward_mm_top_leader_market_payout)
        gross_payout = gross_payout + vision_reward_sale_top_comp_leader_payout + vision_reward_ops_top_store_pay + float(vision_reward_mm_top_ops_market_payout) + vision_reward_dos_top_ops_payout

        self.write(cr, uid, [package_data.id], {
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
                                'gross_payout':gross_payout
                })

packaged_commission_tracker()

class misc_payout_deduct(osv.osv):
    _name = 'misc.payout.deduct'
    _columns = {
                'prm_job_id':fields.many2one('dsr.crash.process.deactivation', 'PRM Job Name'),
                'emp_id':fields.many2one('hr.employee', 'Employee'),
                'misc_amount':fields.float('Miscellaneous Amount'),
                'comments':fields.text('Comments')
    }
    _rec_name = 'prm_job_id'

    def create(self, cr, uid, vals, context=None):
        package_obj = self.pool.get('packaged.commission.tracker')
        package_ids = package_obj.search(cr, uid, [('crash_job_name','=',vals['prm_job_id']),('name','=',vals['emp_id'])])
        if package_ids:
            for package_id in package_ids:
                package_pay = package_obj.browse(cr, uid, package_id).gross_payout
                payout = package_pay + vals['misc_amount']
                package_obj.write(cr, uid, [package_id], {'gross_payout':payout})
        res = super(misc_payout_deduct, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        self_data = self.browse(cr, uid, ids[0])
        package_obj = self.pool.get('packaged.commission.tracker')
        prm_job_id_old = self_data.prm_job_id.id
        emp_id_old = self_data.emp_id.id
        misc_amount_old = self_data.misc_amount
        if 'prm_job_id' in vals:
            prm_job_id = vals['prm_job_id']
        else:
            prm_job_id = self_data.prm_job_id.id
        if 'emp_id' in vals:
            emp_id = vals['emp_id']
        else:
            emp_id = self_data.emp_id.id
        if 'misc_amount' in vals:
            misc_amount = vals['misc_amount']
        else:
            misc_amount = self_data.misc_amount
        if prm_job_id_old and emp_id_old and misc_amount_old:
            package_ids_old = package_obj.search(cr, uid, [('crash_job_name','=',prm_job_id_old),('name','=',emp_id_old)])
            if package_ids_old:
                for package_id in package_ids_old:
                    package_pay = package_obj.browse(cr, uid, package_id).gross_payout
                    payout = package_pay - misc_amount_old
                    package_obj.write(cr, uid, [package_id], {'gross_payout':payout})
        package_ids = package_obj.search(cr, uid, [('crash_job_name','=',prm_job_id),('name','=',emp_id)])
        if package_ids:
            for package_id in package_ids:
                package_pay = package_obj.browse(cr, uid, package_id).gross_payout
                payout = package_pay + misc_amount
                package_obj.write(cr, uid, [package_id], {'gross_payout':payout})
        res = super(misc_payout_deduct, self).write(cr, uid, ids, vals, context=context)
        return res

misc_payout_deduct()