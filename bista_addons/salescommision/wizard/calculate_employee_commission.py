from openerp.osv import osv,fields
import time

class wizard_employee_commission(osv.osv_memory):
	_name = 'wizard.employee.commission'
	_description = "Calculate Employee Commission"
	_columns = {
				'emp_id':fields.many2one('hr.employee', 'Employee'),
				'start_date':fields.date('Start Date'),
				'end_date':fields.date('End Date'),
	}
	_defaults = {
				'start_date': lambda *a: time.strftime('%Y-%m-01'),
				'end_date':  lambda *a: time.strftime('%Y-%m-%d')
	}

	def calculate_commission(self, cr, uid, ids, context=None):
		dealer_class = self.pool.get('dealer.class')
		comm_obj = self.pool.get('commission.tracker')
		emp_read = self.read(cr, uid, ids, ['emp_id', 'start_date', 'end_date'])
		if emp_read:
			emp_id = emp_read[0]['emp_id'][0]
			start_date = emp_read[0]['start_date']
			end_date = emp_read[0]['end_date']
			dealer_code_search = dealer_class.search(cr, uid, [('dealer_id','=',emp_id)])
			count = 0
			for dealer_code_search_id in dealer_code_search:
				dealer_code_data = dealer_class.browse(cr, uid, dealer_code_search_id)
				emp_code = dealer_code_data.id
				store_classification_id = dealer_code_data.store_name.store_classification.id
				store_id = dealer_code_data.store_name.id
				market_id = dealer_code_data.store_name.market_id.id
				region_id = dealer_code_data.store_name.market_id.region_market_id.id
				emp_des = dealer_code_data.designation_id.id
				if not dealer_code_data.end_date:
					if dealer_code_data.start_date <= start_date:
						dealer_start_date = emp_read[0]['start_date']
						dealer_end_date = emp_read[0]['end_date']
						comm_obj.calculate_total_payout(cr, uid, emp_code, emp_id, store_classification_id, store_id, start_date, end_date, market_id, region_id, emp_des, dealer_start_date, dealer_end_date)
					else:
						dealer_start_date = dealer_code_data.start_date
						dealer_end_date = emp_read[0]['end_date']
						comm_obj.calculate_total_payout(cr, uid, emp_code, emp_id, store_classification_id, store_id, start_date, end_date, market_id, region_id, emp_des, dealer_start_date, dealer_end_date)
				else:
					if dealer_code_data.end_date >= start_date:
						if count == 0:
							dealer_start_date = emp_read[0]['start_date']
							count = count + 1
						else:
							dealer_start_date = dealer_code_data.start_date
						dealer_end_date = dealer_code_data.end_date
						comm_obj.calculate_total_payout(cr, uid, emp_code, emp_id, store_classification_id, store_id, start_date, end_date, market_id, region_id, emp_des, dealer_start_date, dealer_end_date)
		return True

wizard_employee_commission()
