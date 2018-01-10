from openerp import tools
from openerp.osv import fields, osv
from openerp import api
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

_prod_type = [('postpaid','Postpaid'),('prepaid','Prepaid'),('feature','Data Feature'),('upgrade','Upgrade'),('accessory','Accessory')]

where_condition = str(" ")

class wireless_dsr_search_transactions(osv.osv_memory):
    
    def _get_employee_id(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.employee_ids:
            return user.employee_ids[0].id
        return False

    _name = 'wireless.dsr.search.transactions'
    _description = "DSR Transactions Search Wizard"
    _columns = {
                'from_trans_date':fields.date('From Transaction Date', help="Transaction Date from where you want to see the Transactions Details."),
                'end_trans_date':fields.date('To Transaction Date', help="Maximum 60 days records from start date."),
                'dealer_code':fields.char('Dealer Code', help="Specify dealer code to filter transactions Records."),
                'phone_no':fields.char('Phone #', help="Specify 10 digit Phone Number to filter Transactions Records."),
                'sim_no':fields.char('SIM #', help="Specify SIM Number to filter Transaction Records."),
                'imei_no':fields.char('IMEI #', help="Specify IMEI Number to filter Transactions Records."),
                'is_postpaid':fields.boolean('Postpaid', help="Check PostPaid box to filter only PostPaid Transactions."),
                'is_upgrade':fields.boolean('Upgrade', help="Check Upgrade box to filter only Upgrade Transactions."),
                'is_prepaid':fields.boolean('Prepaid', help="Check PrePaid box to filter only PrePaid Transactions."),
                'is_feature':fields.boolean('DataFeature', help="Check DataFeature box to filter only DataFeature Transactions."),
                'is_acc':fields.boolean('Accessory', help="Check Accessory box to filter only Accessory Transactions."),
                'emp_id':fields.many2one('hr.employee', 'Employee'),
                'ban_no':fields.char('BAN #')
            }
    _defaults = {
                'from_trans_date': lambda *a: time.strftime('%Y-%m-01'),
                'end_trans_date': lambda *a: time.strftime('%Y-%m-%d'),
                'emp_id':_get_employee_id
    }

    def create(self, cr, uid, vals, context=None):
        start_date = vals['from_trans_date']
        end_date = vals['end_trans_date']
        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_max_date = (start_datetime + relativedelta(days=62))
            end_max_date = end_max_date.strftime('%Y-%m-%d')
            if end_date > end_max_date:
                raise osv.except_osv(('Alert!'),("You can only view Maximum 60 days records at a time."))
        res_id = super(wireless_dsr_search_transactions, self).create(cr, uid, vals, context=context)
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        self_data = self.browse(cr, uid, ids[0])
        if 'from_trans_date' in vals:    
            start_date = vals['from_trans_date']
        else:
            start_date = self_data.start_date
        if 'end_trans_date' in vals:
            end_date = vals['end_trans_date']
        else:
            end_date = self_data.end_date
        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_max_date = (start_datetime + relativedelta(days=62))
            end_max_date = end_max_date.strftime('%Y-%m-%d')
            if end_date > end_max_date:
                raise osv.except_osv(('Alert!'),("You can only view Maximum 60 days records at a time."))
        res_id = super(wireless_dsr_search_transactions, self).write(cr, uid, ids, vals, context=context)
        return res_id

    def fetch_transactions_dsr(self, cr, uid, ids, context=None):
        s = datetime.today()
        region_obj = self.pool.get('market.regions')
        market_obj = self.pool.get('market.place')
        sap_obj = self.pool.get('sap.store')
        hr_obj = self.pool.get('hr.employee')
        self_data = self.browse(cr, uid, ids[0])
        start_date = self_data.from_trans_date
        end_date = self_data.end_trans_date
        dealer_code = self_data.dealer_code
        is_postpaid = self_data.is_postpaid
        is_prepaid = self_data.is_prepaid
        is_upgrade = self_data.is_upgrade
        is_feature = self_data.is_feature
        ban_no = self_data.ban_no
        is_acc = self_data.is_acc
        sim_no = self_data.sim_no
        imei_no = self_data.imei_no
        phone_no = self_data.phone_no
        emp_id = self_data.emp_id.id
        # global where_condition
        where_condition = [] #("where ")
        where_condition.append(('dsr_date', '>=', start_date))
        where_condition.append(('dsr_date', '<=', end_date))
        if dealer_code:
            where_condition.append(('dealer_code', '=', dealer_code))
        if sim_no:
            where_condition.append(('dsr_sim_no', '=', sim_no))
        if imei_no:
            where_condition.append(('dsr_imei_no', '=', imei_no))
        if phone_no:
            where_condition.append(('dsr_phone_no', '=', phone_no))
        if ban_no:
            where_condition.append(('dsr_cust_ban_no', '=', ban_no))
        if is_postpaid:
            where_condition.append('|')
            where_condition.append(('dsr_trans_type', '=', 'postpaid'))
        if is_prepaid:
            where_condition.append('|')
            where_condition.append(('dsr_trans_type', '=', 'prepaid'))
        if is_upgrade:
            where_condition.append('|')
            where_condition.append(('dsr_trans_type', '=', 'upgrade'))
        if is_feature:
            where_condition.append('|')
            where_condition.append(('dsr_trans_type', '=', 'feature'))
        if is_acc:
            where_condition.append('|')
            where_condition.append(('dsr_trans_type', '=', 'accessory'))
        if is_postpaid or is_prepaid or is_upgrade or is_feature or is_acc:
            condition_or_pos = len(where_condition) - 2
            where_condition.pop(condition_or_pos)
       # region_search = region_obj.search(cr, uid, [('sales_director','=',emp_id)])
       # market_search = market_obj.search(cr, uid, [('market_manager','=',emp_id)])
       # store_search = sap_obj.search(cr, uid, [('store_mgr_id','=',emp_id)])
       # if region_search:
       #     where_condition.append(('dsr_region_id', 'in', region_search))
       # elif market_search:
       #     where_condition.append(('dsr_market_id', 'in', market_search))
       # elif store_search:
       #     where_condition.append(('dsr_store_id', 'in', store_search))
       # else:
       #     where_condition.append(('sales_employee_id', '=', emp_id))
        # where_condition = where_condition[:-4]
        #tools.drop_view_if_exists(cr, 'wireless_transactions_report')
        cr.execute('''
              CREATE OR REPLACE VIEW "public"."wireless_transactions_report" AS
 SELECT --row_number() OVER () AS id,
    transactions.id::bigint,
    transactions.dsr_rev_gen,
    transactions.dsr_entry_no,
    transactions.dsr_comm_per_line,
    transactions.dsr_phone_purchase_type,
    transactions.dsr_eip_no,
    transactions.dsr_soc_code,
    transactions.credit_class,
    transactions.dsr_date,
    transactions.sales_employee_id,
    transactions.dsr_store_id,
    transactions.dsr_market_id,
    transactions.dsr_region_id,
    transactions.dsr_imei_no,
    transactions.dsr_sim_no,
    transactions.dsr_phone_no,
    transactions.dsr_prod_type,
    transactions.dsr_mob_port,
    transactions.dsr_port_comp,
    transactions.dsr_cust_ban_no,
    transactions.state,
    transactions.customer_name,
    transactions.dealer_code,
    transactions.dsr_ship_to,
    transactions.dsr_trade_inn,
    transactions.dsr_temp_no,
    transactions.dsr_trans_type,
    transactions.dsr_phone_spiff,
    transactions.dsr_transaction_id,
    transactions.dsr_monthly_access,
    transactions.dsr_contract_term,
    transactions.dsr_jump_already,
    transactions.dsr_comm_amnt,
    transactions.dsr_comm_added,
    transactions.dsr_disc_percent,
    transactions.dsr_product_sku,
    transactions.crash_prm_job_id_rollback,
    transactions.prm_dsr_smd,
    transactions.prm_dsr_pmd,
    transactions.noncommissionable,
    transactions.comments,
    transactions.pseudo_date
   FROM (( SELECT transactions_1.dsr_rev_gen,
            transactions_1.product_id AS dsr_entry_no,
            transactions_1.dsr_comm_per_line,
            transactions_1.dsr_phone_purchase_type,
            transactions_1.dsr_eip_no,
            transactions_1.dsr_product_code AS dsr_soc_code,
            transactions_1.dsr_credit_class AS credit_class,
            transactions_1.dsr_act_date AS dsr_date,
            transactions_1.employee_id AS sales_employee_id,
            transactions_1.store_id AS dsr_store_id,
            transactions_1.market_id AS dsr_market_id,
            transactions_1.region_id AS dsr_region_id,
            transactions_1.dsr_imei_no,
            transactions_1.dsr_sim_no,
            transactions_1.dsr_phone_no,
            transactions_1.dsr_product_type AS dsr_prod_type,
            NULL::boolean AS dsr_mob_port,
            NULL::integer AS dsr_port_comp,
            transactions_1.dsr_cust_ban_no,
            transactions_1.state,
            transactions_1.customer_name,
            transactions_1.dealer_code,
            transactions_1.dsr_ship_to,
            transactions_1.dsr_trade_inn,
            transactions_1.dsr_temp_no,
            transactions_1.dsr_trans_type,
            transactions_1.dsr_comm_spiff AS dsr_phone_spiff,
            transactions_1.dsr_transaction_id,
            transactions_1.dsr_monthly_access,
            transactions_1.dsr_contract_term,
            transactions_1.dsr_jump_already,
            transactions_1.dsr_comm_amnt,
            transactions_1.dsr_comm_added,
            NULL::integer AS dsr_disc_percent,
            NULL::text AS dsr_product_sku,
            transactions_1.crash_prm_job_id_rollback,
            (transactions_1.id::text||transactions_1.product_id::text)::bigint as id,
            transactions_1.prm_dsr_smd,
            transactions_1.prm_dsr_pmd,
            transactions_1.noncommissionable,
            transactions_1.comments,
            transactions_1.pseudo_date
           FROM wireless_dsr_upgrade_line transactions_1
          )
        UNION ALL
        ( SELECT transactions_1.dsr_rev_gen,
            transactions_1.product_id AS dsr_entry_no,
            transactions_1.dsr_comm_per_line,
            transactions_1.dsr_phone_purchase_type,
            transactions_1.dsr_eip_no,
            transactions_1.dsr_product_code AS dsr_soc_code,
            transactions_1.dsr_credit_class AS credit_class,
            transactions_1.dsr_act_date AS dsr_date,
            transactions_1.employee_id AS sales_employee_id,
            transactions_1.store_id AS dsr_store_id,
            transactions_1.market_id AS dsr_market_id,
            transactions_1.region_id AS dsr_region_id,
            transactions_1.dsr_imei_no,
            transactions_1.dsr_sim_no,
            transactions_1.dsr_phone_no,
            transactions_1.dsr_product_type AS dsr_prod_type,
            transactions_1.dsr_mob_port,
            transactions_1.dsr_port_comp,
            transactions_1.dsr_cust_ban_no,
            transactions_1.state,
            transactions_1.customer_name,
            transactions_1.dealer_code,
            transactions_1.dsr_ship_to,
            transactions_1.dsr_trade_inn,
            transactions_1.dsr_temp_no,
            transactions_1.dsr_trans_type,
            transactions_1.dsr_comm_spiff AS dsr_phone_spiff,
            transactions_1.dsr_transaction_id,
            transactions_1.dsr_monthly_access,
            transactions_1.dsr_contract_term,
            NULL::boolean AS dsr_jump_already,
            transactions_1.dsr_comm_amnt,
            transactions_1.dsr_comm_added,
            NULL::integer AS dsr_disc_percent,
            NULL::text AS dsr_product_sku,
            transactions_1.crash_prm_job_id_rollback,
            (transactions_1.id::text||transactions_1.product_id::text)::bigint as id,
            transactions_1.prm_dsr_smd,
            transactions_1.prm_dsr_pmd,
            transactions_1.noncommissionable,
            transactions_1.comments,
            transactions_1.pseudo_date
           FROM wireless_dsr_postpaid_line transactions_1
          )
        UNION ALL
        ( SELECT transactions_1.dsr_rev_gen,
            transactions_1.product_id AS dsr_entry_no,
            transactions_1.dsr_comm_per_line,
            transactions_1.dsr_phone_purchase_type,
            NULL::character varying AS dsr_eip_no,
            transactions_1.dsr_product_description AS dsr_soc_code,
            NULL::integer AS credit_class,
            transactions_1.dsr_act_date AS dsr_date,
            transactions_1.employee_id AS sales_employee_id,
            transactions_1.store_id AS dsr_store_id,
            transactions_1.market_id AS dsr_market_id,
            transactions_1.region_id AS dsr_region_id,
            transactions_1.dsr_imei_no,
            transactions_1.dsr_sim_no,
            transactions_1.dsr_phone_no,
            transactions_1.dsr_product_type AS dsr_prod_type,
            NULL::boolean AS dsr_mob_port,
            NULL::integer AS dsr_port_comp,
            NULL::character varying AS dsr_cust_ban_no,
            transactions_1.state,
            transactions_1.customer_name,
            transactions_1.dealer_code,
            NULL::boolean AS dsr_ship_to,
            transactions_1.dsr_trade_inn,
            transactions_1.dsr_temp_no,
            transactions_1.dsr_trans_type,
            transactions_1.dsr_comm_spiff AS dsr_phone_spiff,
            transactions_1.dsr_transaction_id,
            transactions_1.dsr_monthly_access,
            transactions_1.dsr_contract_term,
            NULL::boolean AS dsr_jump_already,
            transactions_1.dsr_comm_amnt,
            transactions_1.dsr_comm_added,
            NULL::integer AS dsr_disc_percent,
            NULL::text AS dsr_product_sku,
            transactions_1.crash_prm_job_id_rollback,
            (transactions_1.id::text||transactions_1.product_id::text)::bigint as id,
            transactions_1.prm_dsr_smd,
            transactions_1.prm_dsr_pmd,
            transactions_1.noncommissionable,
            transactions_1.comments,
            transactions_1.pseudo_date
           FROM wireless_dsr_prepaid_line transactions_1
          )
        UNION ALL
        ( SELECT transactions_1.dsr_rev_gen,
            transactions_1.feature_product_id AS dsr_entry_no,
            transactions_1.dsr_comm_per_line,
            transactions_1.dsr_phone_purchase_type,
            transactions_1.dsr_eip_no,
            transactions_1.dsr_product_code AS dsr_soc_code,
            transactions_1.dsr_credit_class AS credit_class,
            transactions_1.dsr_act_date AS dsr_date,
            transactions_1.employee_id AS sales_employee_id,
            transactions_1.store_id AS dsr_store_id,
            transactions_1.market_id AS dsr_market_id,
            transactions_1.region_id AS dsr_region_id,
            transactions_1.dsr_imei_no,
            transactions_1.dsr_sim_no,
            transactions_1.dsr_phone_no,
            transactions_1.dsr_product_type AS dsr_prod_type,
            transactions_1.dsr_mob_port,
            transactions_1.dsr_port_comp,
            transactions_1.dsr_cust_ban_no,
            transactions_1.state,
            transactions_1.customer_name,
            transactions_1.dealer_code,
            transactions_1.dsr_ship_to,
            transactions_1.dsr_trade_inn,
            transactions_1.dsr_temp_no,
            transactions_1.dsr_trans_type,
            transactions_1.dsr_comm_spiff AS dsr_phone_spiff,
            transactions_1.dsr_transaction_id,
            transactions_1.dsr_monthly_access,
            transactions_1.dsr_contract_term,
            NULL::boolean AS dsr_jump_already,
            transactions_1.dsr_comm_amnt,
            transactions_1.dsr_comm_added,
            NULL::integer AS dsr_disc_percent,
            NULL::text AS dsr_product_sku,
            transactions_1.crash_prm_job_id_rollback,
            (transactions_1.id::text||transactions_1.feature_product_id ::text)::bigint as id,
            transactions_1.prm_dsr_smd,
            transactions_1.prm_dsr_pmd,
            transactions_1.noncommissionable,
            transactions_1.comments,
            transactions_1.pseudo_date
           FROM wireless_dsr_feature_line transactions_1
          )
        UNION ALL
        ( SELECT transactions_1.dsr_rev_gen,
            transactions_1.product_id AS dsr_entry_no,
            transactions_1.dsr_comm_per_line,
            transactions_1.dsr_phone_purchase_type,
            NULL::character varying AS dsr_eip_no,
            NULL::integer AS dsr_soc_code,
            NULL::integer AS credit_class,
            transactions_1.dsr_act_date AS dsr_date,
            transactions_1.employee_id AS sales_employee_id,
            transactions_1.store_id AS dsr_store_id,
            transactions_1.market_id AS dsr_market_id,
            transactions_1.region_id AS dsr_region_id,
            NULL::character varying AS dsr_imei_no,
            NULL::character varying AS dsr_sim_no,
            transactions_1.dsr_phone_no,
            NULL::integer AS dsr_prod_type,
            NULL::boolean AS dsr_mob_port,
            NULL::integer AS dsr_port_comp,
            NULL::character varying AS dsr_cust_ban_no,
            transactions_1.state,
            transactions_1.customer_name,
            transactions_1.dealer_code,
            NULL::boolean AS dsr_ship_to,
            transactions_1.dsr_trade_inn,
            transactions_1.dsr_temp_no,
            transactions_1.dsr_trans_type,
            NULL::numeric AS dsr_phone_spiff,
            transactions_1.dsr_transaction_id,
            NULL::double precision AS dsr_monthly_access,
            NULL::integer AS dsr_contract_term,
            NULL::boolean AS dsr_jump_already,
            NULL::numeric AS dsr_comm_amnt,
            NULL::numeric AS dsr_comm_added,
            transactions_1.dsr_disc_percent,
            transactions_1.dsr_product_sku,
            NULL::integer AS crash_prm_job_id_rollback,
            (transactions_1.id::text||transactions_1.product_id::text)::bigint as id,
            NULL::boolean as prm_dsr_smd,
            NULL::boolean as prm_dsr_pmd,
            NULL::boolean as noncommissionable,
            NULL::character as comments,
            transactions_1.pseudo_date
           FROM wireless_dsr_acc_line transactions_1
          )) transactions;''')
        ctx = dict(context)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wireless.transactions.report',
            'view_id': False,
            'domain':where_condition,
            'context': ctx,
        }

wireless_dsr_search_transactions()  

class wireless_transactions_report(osv.osv):
    _name = "wireless.transactions.report"
    _description = "Wireless Trasactions Report"
    #_order='dsr_phone_no'
    _auto = False
    _columns = {
                'dsr_entry_no':fields.many2one('wireless.dsr','Entry #'),
                'dsr_date':fields.date('Transaction Date'),
                'pseudo_date':fields.date('Pseudo Date'),
                'sales_employee_id':fields.many2one('hr.employee','Sales Person'),
                'dsr_region_id':fields.many2one('market.regions', 'Region'),
                'dsr_market_id':fields.many2one('market.place', 'Market'),
                'dsr_store_id':fields.many2one('sap.store','Store'),
                'dsr_prod_type':fields.many2one('product.category', 'Product Type'),
                'dsr_soc_code':fields.many2one('product.product', 'SOC Code'),
                'dsr_phone_no':fields.char('Mobile Phone', size=10),
                'dsr_sim_no':fields.char('SIM #', size=25),
                'dsr_imei_no':fields.char('IMEI #', size=15),
                'dsr_temp_no':fields.char('Temporary #', size=10),
                'dsr_rev_gen':fields.float('Total Rev Gen.'),
                'dsr_comm_per_line':fields.float('Total Commission'),
                'credit_class':fields.many2one('credit.class', 'Credit Class'),
                'dsr_phone_purchase_type':fields.selection([('new_device','EIP'),('sim_only','SIM Only'),('device_outright','Device Outright')],'Phone Purchased'),
                'dsr_eip_no':fields.char('EIP #', size=16),
                'dsr_mob_port':fields.boolean('Mobile Port'),
                'dsr_port_comp':fields.many2one('port.company', 'Port Company'),
                #'dsr_port_comp':fields.char('Port Company', size=90),
                'dsr_cust_ban_no':fields.char('BAN no.', size=16),
                'dsr_ship_to':fields.boolean('Ship To'),
                'dsr_trade_inn':fields.selection([('yes','Yes'),('no','No')],'Trade Inn'),
                'dsr_phone_spiff':fields.float('Phone Spiff'),
                'dsr_comm_amnt':fields.float('Commission'),
                'dsr_comm_added':fields.float('Added Rev'),
                'dsr_trans_type':fields.selection(_prod_type, 'Transaction Type'),
                'dsr_contract_term':fields.integer('Contract Term'), 
                'dsr_monthly_access':fields.float('Monthly Access'),
                'dsr_transaction_id':fields.char('Transaction ID', size=64),
                'dsr_jump_already':fields.boolean('JUMP Already'),
                'dsr_disc_percent':fields.many2one('discount.master', 'Discount'),
                'dsr_product_sku':fields.char('Product Name', size=1024),
                'state':fields.char('State', size=1024),
                'customer_name':fields.char('Customer Name', size=1024),
                'dealer_code':fields.char('Dealer Code', size=1024),
                'prm_dsr_smd':fields.boolean('SMD'),
                'prm_dsr_pmd':fields.boolean('PMD'),
                'noncommissionable':fields.boolean('NonCommissionable'),
                'comments':fields.char('Comment'),
                'crash_prm_job_id_rollback':fields.many2one('dsr.crash.process.deactivation','PRM Crash Rollback'),
                'state':fields.selection([('draft','Draft'),('pending','Pending'),('cancel','Cancel'),('submit','Submit'),('void','VOID'),('done','Done')],'State', readonly=True),
              }

    # def init(self, cr):
    #     cr.execute("select * from wireless_transactions_report")

wireless_transactions_report()

class materialized_view_refresh_log(osv.osv):
    _name = 'materialized.view.refresh.log'
    _columns = {
                'date':fields.date('Date'),
                'user_id':fields.many2one('res.users','User'),
                'status':fields.selection([('pass','Pass'),('fail','Fail')],'Status')
    }
materialized_view_refresh_log()