from openerp.osv import fields, osv

class employee_script(osv.osv_memory):
	_inherit = 'employee.script'

	def employee_market_reset(self, cr, uid, ids, context=None):
		# market_obj = self.pool.get('market.place')
		# emp_obj = self.pool.get('hr.employee')
		# cr.execute('select id from market_place')
		# market_ids = map(lambda x: x[0], cr.fetchall())
		# for market_id in market_ids:
		# 	market_data = market_obj.browse(cr, uid, market_id)
		# 	if market_data.market_manager:
		# 		emp_id = market_data.market_manager.id
		# 		store_ids = market_data.store_id
		# 		sap_ids = map(lambda x: x.id, store_ids)
		# 		print sap_id
		# 		sdfsf
		return True

	def employee_region_reset(self, cr, uid, ids, context=None):
		return True
employee_script()