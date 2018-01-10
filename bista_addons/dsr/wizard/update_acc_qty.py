from openerp.osv import osv,fields
import logging
logger = logging.getLogger('arena_log')

class wireless_update_acc_qty(osv.osv_memory):
	_name = 'wireless.update.acc.qty'

	def upgrade_acc(self, cr, uid, ids, context=None):
		acc_obj = self.pool.get('wireless.dsr.acc.line')
		acc_ids = acc_obj.search(cr, uid, [('dsr_act_date','>=','2015-02-01'),('dsr_act_date','<=','2015-02-10'),('dsr_disc_percent','!=',False)])
		for acc_data in acc_obj.browse(cr, uid, acc_ids):
			disc_percent = acc_data.dsr_disc_percent.disc_percent
			list_price = acc_data.dsr_list_price
			rev = acc_data.dsr_acc_mrc
			if list_price > 0:
				qty = (rev * 100) / (list_price * (100 - disc_percent))
				if qty < 1:
					qty = 1
				acc_obj.write(cr, uid, [acc_data.id], {'dsr_quantity':qty})
		return True

	def update_dsr_delete_soc(self, cr, uid, ids, context=None):
		dsr_obj = self.pool.get('wireless.dsr')
		feature_obj = self.pool.get('wireless.dsr.feature.line')
		upg_obj = self.pool.get('wireless.dsr.upgrade.line')
		pos_obj = self.pool.get('wireless.dsr.postpaid.line')
		cr.execute('''select id from product_product where default_code in ('SC2HDAT1B','SC2HDAT1','B2HDAT1B','B2HDAT1','pradduttv','SCNCUTT')''')
		prod_ids = map(lambda x: x[0], cr.fetchall())
		if prod_ids:
			feature_ids = feature_obj.search(cr, uid, [('dsr_product_code','in',prod_ids),('dsr_act_date','>=','2015-02-01'),('state','in',('done','pending'))])
			for feature_data in feature_obj.browse(cr, uid, feature_ids):
				logger.info("****************:%s"%(feature_data.id))
				upgrade_id = feature_data.upgrade_id
				postpaid_id = feature_data.postpaid_id
				#state = feature_data.state
				product_id = feature_data.feature_product_id.id
				if upgrade_id:
					upg_obj.write(cr, uid, [upgrade_id.id], {'data':False,'data_soc':False})
				if postpaid_id:
					pos_obj.write(cr, uid, [postpaid_id.id], {'data':False,'data_soc':False})
				feature_obj.unlink(cr, uid, [feature_data.id])
				dsr_obj.write(cr, uid, [product_id], {'history_dsr_id':" "})
			
			del_dsr_ids = []
			del_feature_ids = []
			postpaid_ids = pos_obj.search(cr, uid, [('dsr_product_code','in',prod_ids),('dsr_act_date','>=','2015-02-01')])
			if postpaid_ids:
				del_feature_ids = feature_obj.search(cr, uid, [('postpaid_id','in',tuple(postpaid_ids)),('dsr_act_date','>=','2015-02-01')])
			logger.info("****************del_feature_ids:%s,$$$$$$$$$$$$$$$$:del_postpaid_ids:%s"%(len(del_feature_ids),len(postpaid_ids)))
			for post_data in pos_obj.browse(cr, uid, postpaid_ids):
				del_dsr_ids.append(post_data.product_id.id)
			if del_dsr_ids:
				feature_obj.unlink(cr, uid, del_feature_ids)
				pos_obj.unlink(cr, uid, postpaid_ids)
				dsr_obj.write(cr, uid, del_dsr_ids, {'history_dsr_id':" "})

		cr.execute('''select id from product_product where default_code in ('SNCADDUTT','SNC4HMBB','SNC2HMBB','SCNMIMDG5','SCNCFUTT','PSCNC5GB','PSCNC3GB','PSCNC1GB','SNC500MBB')''')
		prod_upg_ids = map(lambda x: x[0], cr.fetchall())
		del_dsr_ids = []
		del_feature_ids = []
		upgrade_ids = upg_obj.search(cr, uid, [('dsr_product_code','in',prod_upg_ids),('dsr_act_date','>=','2015-02-01')])
		if upgrade_ids:
			del_feature_ids = feature_obj.search(cr, uid, [('upgrade_id','in',tuple(upgrade_ids)),('dsr_act_date','>=','2015-02-01')])
		logger.info("****************del_feature_ids:%s,$$$$$$$$$$$$$$$$:del_upgrade_ids:%s"%(len(del_feature_ids),len(upgrade_ids)))
		for upg_data in upg_obj.browse(cr, uid, upgrade_ids):
			del_dsr_ids.append(upg_data.product_id.id)
		if del_dsr_ids:
			feature_obj.unlink(cr, uid, del_feature_ids)
			upg_obj.unlink(cr, uid, upgrade_ids)
			dsr_obj.write(cr, uid, del_dsr_ids, {'history_dsr_id':" "})
		return True

wireless_update_acc_qty()