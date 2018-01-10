from datetime import date,datetime, timedelta
from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
import calendar
import re
from base.res import res_company as COMPANY
from base.res import res_partner
from collections import Counter
import xmlrpclib

class product_series_main(osv.osv):
	_inherit = "product.series.main"

	def offline_sync_product_series_main(self,cr,uid,ids,context = None):
		if context is None: context = {}
		sync_result = True
		offline_sync = context.get('offline_sync') if context.get('offline_sync') else False
		form_id = offline_sync.get('form_id') if offline_sync and offline_sync.get('form_id') else False
		offline_sync_sync = offline_sync.get('sync_sequence') if offline_sync and offline_sync.get('sync_sequence') else False
		context.update({'offline_sync_sync':offline_sync_sync})
		method_name = offline_sync.get('func_model') if offline_sync and offline_sync.get('func_model') else False
		if form_id:
				sync_result = getattr(self,method_name).__call__(cr, uid, [form_id], context=context)
		return sync_result

	def sync_serial_attachment(self,cr,uid,ids,context=None):
		conn_flag = False
		branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
		for branch_id in self.pool.get('res.company').browse(cr,uid,branch_type):
			vpn_ip_addr = branch_id.vpn_ip_address
			port = branch_id.port
			dbname = branch_id.dbname
			pwd = branch_id.pwd
			user_name = str(branch_id.user_name.login)

			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				uid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_serial_attachment','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
			sock = xmlrpclib.ServerProxy(obj)
			if not conn_flag:
		
				for res in self.browse(cr,uid,ids):
					test_id = res.test.id
					product_series=''
					srch = self.pool.get('receive.indent').search(cr,uid,[('id','=',test_id)])
					for rec in self.pool.get('receive.indent').browse(cr,uid,srch):
						origin = rec.indent_id.order_id
						delivery_type = rec.delivery_type_others
						if delivery_type == 'direct_delivery':
							for ln in rec.receive_indent_line:
								product_id = ln.product_name
								type_product = product_id.type_product
								if type_product == 'track_equipment':
									ci_sync=self.pool.get('res.indent').browse(cr,uid,rec.indent_id.id)
									origin_srch = [('origin', '=',origin),('id','=',ci_sync.ci_sync_id)]
									origin_ids = sock.execute(dbname, uid, pwd, 'stock.picking', 'search', origin_srch)
									if origin_ids:
										product_srch = [('name', '=',ln.product_name.name)]
										product_ids = sock.execute(dbname, uid, pwd, 'product.product', 'search', product_srch)
										product_uom = [('name','=',ln.product_uom.name)]
										product_uom_ids = sock.execute(dbname, uid, pwd, 'product.uom', 'search',product_uom)

										ln_srch = [('product_id', '=',product_ids[0]),('product_code','=',ln.product_code),('state','=','done'),('origin','=',origin)]
										ln_ids = sock.execute(dbname, uid, pwd, 'stock.move', 'search', ln_srch)


										fields =['picking_id']	
										data = sock.execute(dbname, uid, pwd, 'stock.move', 'read', ln_ids,fields)
										product_series=0
										#for lines in data:
										
										srch_product_series=[('test','=',origin_ids[0])]
										srch_product_series_id = sock.execute(dbname, uid, pwd, 'product.series.main', 'search', srch_product_series)
										
										if not srch_product_series_id:
											prod_series_id =  {'test':origin_ids[0]}
											product_series = sock.execute(dbname, uid, pwd, 'product.series.main', 'create', prod_series_id)

											button_visible =  { 'test_state':True }
											button_visible_tree = sock.execute(dbname, uid, pwd, 'stock.picking', 'write', origin_ids[0], button_visible)
										if srch_product_series_id:	
											product_series	=srch_product_series_id[0]		
							
										if ln.generic_id:
											generic_id_srch=[('name','=',ln.generic_id.name)]
											generic_ids=sock.execute(dbname, uid, pwd, 'product.generic.name', 'search', generic_id_srch)

							count = 0
							for line in res.series_multiple:
												product_srch1 = [('name', '=',line.product_name.name_template)]
												product_ids1 = sock.execute(dbname, uid, pwd, 'product.product', 'search', product_srch1)
												count = count + 1	
												new_series = {
													'series_line':product_series,
													'sr_no':count,
													'product_code':line.product_code,
													'product_name':product_ids1[0],
													'generic_id' :generic_ids[0] if generic_ids else False,
													'product_uom':product_uom_ids[0],
													'prod_uom':line.product_uom.name,
													'product_category':line.product_name.categ_id.name if line.product_category else '',
													'batch_val':line.batch.batch_no,
													'quantity':line.quantity,
													'serial_no':line.serial_no,
													'active_id':True if line.active_id else False,
													'serial_check':line.serial_check,
													'reject':True if line.reject else False, #Pallavi 30 DEc
													'short':line.short,
													'excess':line.excess,
														 }
												series_create = sock.execute(dbname, uid, pwd, 'product.series', 'create', new_series)

											#button_visible =  { 'test_state':True }
											#button_visible_tree = sock.execute(dbname, uid, pwd, 'stock.picking', 'write', origin_ids[0], button_visible)
				
			
						
				
		return conn_flag


product_series_main()

