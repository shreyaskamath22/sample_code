from openerp.osv import osv,fields

class wireless_dsr_manually_update(osv.osv):
	_name = 'wireless.dsr.manually.update'
	_description = "DSR Manually Update Records"

	def _get_start_date(self, cr, uid, context=None):
		start_date = None
		if context is not None:
			start_date = context.get('start_date')
		return start_date

	def _get_end_date(self, cr, uid, context=None):
		end_date = None
		if context is not None:
			end_date = context.get('end_date')
		return end_date

	def _get_emp_id(self, cr, uid, context=None):
		emp_id = None
		if context is not None:
			emp_id = context.get('emp_id')
		return emp_id

	def _get_dealer_code_upg(self, cr, uid, context=None):
		dealer_code_upg = None
		if context is not None:
			dealer_code_upg = context.get('dealer_code_upg')
		return dealer_code_upg

	def _get_sap_id_upg(self, cr, uid, context=None):
		sap_id_upg = None
		if context is not None:
			sap_id_upg = context.get('sap_id_upg')
		return sap_id_upg

	_columns = {
				'start_date':fields.date('From Date'),
				'end_date':fields.date('Upto Date'),
				'emp_id':fields.many2one('hr.employee', 'Sales Representative'),
				# 'emp_id_upg':fields.many2one('hr.employee', 'Sales Representative'),
				'dealer_code_upg':fields.char('Dealer Code'),
				'job_id_upg':fields.many2one('hr.job','Designation'),
				'sap_id_upg':fields.many2one('sap.store', 'Home/Base Store'),
	}
	_defaults = {
				'start_date':_get_start_date,
				'end_date':_get_end_date,
				'emp_id':_get_emp_id,
				'dealer_code_upg':_get_dealer_code_upg,
				'sap_id_upg':_get_sap_id_upg
	}

	def dsr_update(self, cr, uid, ids, context=None):
		vals = {}
		vals_child = {}
		update_str = str("")
		update_str_child = str("")
		dsr_obj = self.pool.get('wireless.dsr')
		pos_obj = self.pool.get('wireless.dsr.postpaid.line')
		pre_obj = self.pool.get('wireless.dsr.prepaid.line')
		upg_obj = self.pool.get('wireless.dsr.upgrade.line')
		feature_obj = self.pool.get('wireless.dsr.feature.line')
		acc_obj = self.pool.get('wireless.dsr.acc.line')
		self_obj = self.browse(cr, uid, ids[0])
		start_date = self_obj.start_date
		end_date = self_obj.end_date
		emp_id = self_obj.emp_id.ids
		dsr_ids = dsr_obj.search(cr, uid, [('dsr_date','>=',start_date),('dsr_date','<=',end_date),('dsr_sales_employee_id','=',emp_id)])
		if dsr_ids:
			dealer_code_upg = self_obj.dealer_code_upg
			if dealer_code_upg:
				update_str += str("dsr_dealer_code = %s,"%(dealer_code_upg))
				update_str_child += str("dealer_code = %s,"%(dealer_code_upg))
			job_id_upg = self_obj.job_id_upg
			if job_id_upg:
				update_str += str("dsr_designation_id = %s,"%(job_id_upg.id))
			sap_id_upg = self_obj.sap_id_upg
			if sap_id_upg:
				update_str += str("dsr_store_id = %s,"%(sap_id_upg.id))
				update_str += str("dsr_market_id = %s,"%(sap_id_upg.market_id.id))
				update_str += str("dsr_region_id = %s,"%(sap_id_upg.market_id.region_market_id.id))
				update_str_child += str("store_id = %s,"%(sap_id_upg.id))
				update_str_child += str("market_id = %s,"%(sap_id_upg.market_id.id))
				update_str_child += str("region_id = %s,"%(sap_id_upg.market_id.region_market_id.id))
			update_str = update_str[:-1]
			update_str_child = update_str_child[:-1]
			if dealer_code_upg or job_id_upg or sap_id_upg:

				####### code written as if...else condition since for a single records tuple function doesnt get incorporated in
				####### the query 03052015
				if len(dsr_ids) > 1:
				
					cr.execute("UPDATE wireless_dsr SET "+update_str+" where id in %s"%(tuple(dsr_ids),))
					cr.execute("UPDATE wireless_dsr_postpaid_line SET "+update_str_child+" where product_id in %s"%(tuple(dsr_ids),))
					cr.execute("UPDATE wireless_dsr_upgrade_line SET "+update_str_child+" where product_id in %s"%(tuple(dsr_ids),))
					cr.execute("UPDATE wireless_dsr_feature_line SET "+update_str_child+" where feature_product_id in %s"%(tuple(dsr_ids),))
					cr.execute("UPDATE wireless_dsr_prepaid_line SET "+update_str_child+" where product_id in %s"%(tuple(dsr_ids),))
					cr.execute("UPDATE wireless_dsr_acc_line SET "+update_str_child+" where product_id in %s"%(tuple(dsr_ids),))
				else:
                                        cr.execute("UPDATE wireless_dsr SET "+update_str+" where id = %s"%(dsr_ids[0]))
                                        cr.execute("UPDATE wireless_dsr_postpaid_line SET "+update_str_child+" where product_id = %s"%(dsr_ids[0]))
                                        cr.execute("UPDATE wireless_dsr_upgrade_line SET "+update_str_child+" where product_id = %s"%(dsr_ids[0]))
                                        cr.execute("UPDATE wireless_dsr_feature_line SET "+update_str_child+" where feature_product_id = %s"%(dsr_ids[0]))
                                        cr.execute("UPDATE wireless_dsr_prepaid_line SET "+update_str_child+" where product_id = %s"%(dsr_ids[0]))
                                        cr.execute("UPDATE wireless_dsr_acc_line SET "+update_str_child+" where product_id = %s"%(dsr_ids[0]))
				######## code ends here


		return True

	def create(self, cr, uid, vals, context=None):		
		res_id = super(wireless_dsr_manually_update, self).create(cr, uid, vals, context=context)
		vals_log = {
					'user_id':uid,
					'employee_id':vals['emp_id'],
					'dealer_code_upg':vals['dealer_code_upg'],
					'job_id_upg':vals['job_id_upg'],
					'sap_id_upg':vals['sap_id_upg'],
					'start_date':vals['start_date'],
					'end_date':vals['end_date'],
					'update_wiz_id':res_id,
					'type':'create'
					}
		self.pool.get('dsr.manually.update.log').create(cr, uid, vals_log, context=context)
		return res_id

	def write(self, cr, uid, ids, vals, context=None):
		res_id = super(wireless_dsr_manually_update, self).write(cr, uid, ids, vals, context=context)
		cr.commit()
		self_data = self.browse(cr, uid, ids[0])
		vals_log = {
					'user_id':uid,
					'employee_id':self_data.emp_id.id,
					'dealer_code_upg':self_data.dealer_code_upg,
					'job_id_upg':self_data.job_id_upg.id,
					'sap_id_upg':self_data.sap_id_upg.id,
					'start_date':self_data.start_date,
					'end_date':self_data.end_date,
					'update_wiz_id':ids[0],
					'type':'write'
		}
		self.pool.get('dsr.manually.update.log').create(cr, uid, vals_log, context=context)
		return res_id

wireless_dsr_manually_update()

class dsr_manually_update_log(osv.osv):
	_name = 'dsr.manually.update.log'
	_description = "DSR Manually Update Log"
	_columns = {
				'user_id':fields.many2one('res.users','User'),
				'update_wiz_id':fields.many2one('wireless.dsr.manually.update','Update Wizard Id'),
				'employee_id':fields.many2one('hr.employee', 'Employee Id'),
				'dealer_code_upg':fields.char('Dealer Code'),
				'job_id_upg':fields.many2one('hr.job', 'Upgraded Job'),
				'sap_id_upg':fields.many2one('sap.store', 'Sap #'),
				'start_date':fields.date('Start Date'),
				'end_date':fields.date('End Date'),
				'type':fields.selection([('create','Created'),('write','Write')],'Log Type'),
	}
dsr_manually_update_log()
