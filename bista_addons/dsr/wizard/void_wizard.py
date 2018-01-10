from openerp.osv import osv,fields

class wireless_dsr_void_wizard(osv.osv_memory):
	_name = 'wireless.dsr.void.wizard'
	_description = "VOID Wizard"

	def move_yes_no(self, cr, uid, ids, context=None):
		dsr_id = context.get('active_id',[])
		self_obj = self.pool.get('wireless.dsr')
		dsr_data = self_obj.browse(cr, uid, dsr_id)
		pre_obj = self.pool.get('wireless.dsr.prepaid.line')
		fea_obj = self.pool.get('wireless.dsr.feature.line')
		pos_line_data = dsr_data.postpaid_product_line
		upgrade_line_data = dsr_data.upgrade_product_line
		acc_line_data = dsr_data.acc_product_line
		pre_line_data = pre_obj.search(cr, uid, [('product_id','=',dsr_id)])
		fea_line_data = fea_obj.search(cr, uid, [('feature_product_id','=',dsr_id)])
		if pos_line_data:
			for pos_line_id in pos_line_data:
				pos_id = pos_line_id.id
				self.pool.get('wireless.dsr.postpaid.line').write(cr, uid, [pos_id], {'state':'void'})
		if upgrade_line_data:
			for upg_line_id in upgrade_line_data:
				upg_id = upg_line_id.id
				self.pool.get('wireless.dsr.upgrade.line').write(cr, uid, [upg_id], {'state':'void'})
		if acc_line_data:
			for acc_line_id in acc_line_data:
				acc_id = acc_line_id.id
				self.pool.get('wireless.dsr.acc.line').write(cr, uid, [acc_id], {'state':'void'})
		if pre_line_data:
			for pre_line_id in pre_line_data:
				pre_obj.write(cr, uid, [pre_line_id], {'state':'void'})
		if fea_line_data:
			for fea_line_id in fea_line_data:
				fea_obj.write(cr, uid, [fea_line_id], {'state':'void'})
		self_obj.write(cr, uid, dsr_id, {'state':'void'})
		return True

wireless_dsr_void_wizard()