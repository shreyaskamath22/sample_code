#Version No. : 1.0.039 For Vertual Godown task for branches
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
class stock_transfer(osv.osv):

	_inherit = 'stock.transfer'

	def offline_sync_stock_transfer(self,cr,uid,ids,context = None):
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

	def sync_prepare_packlist(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag=False
		conn_flag_1=False
		for res in self.browse(cr,uid,ids):
			ci_sync_id = res.ci_sync_id
			form_branch_id = res.form_branch_id
			delivery_location = res.delivery_location
			vpn_ip_addr = delivery_location.vpn_ip_address
			port = delivery_location.port
			dbname = delivery_location.dbname
			pwd = delivery_location.pwd
			user_name = str(delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_prepare_packlist_branch','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})			
			sock = xmlrpclib.ServerProxy(obj)

			if conn_flag == False:
			
				origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
				origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
				if origin_ids:
					for line in res.stock_transfer_product:
						if line.state!='cancel_order_qty':  	

							product_srch = [('name', '=',line.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							prod_srch = [('line_id','=',origin_ids[0]),('product_id', '=',product_ids[0])]
							prod_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', prod_srch)
							if prod_ids:
								pick_line = {
									'state':'packlist'
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', prod_ids, pick_line)
								if line.notes_one2many:
									for material_notes in line.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',prod_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)

										if not remark_srch_id:
											msg_flag_branch=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',prod_ids ,msg_unread)
										notes_line = {
												                'indent_id':prod_ids[0],
												                'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                'comment_date':comment_date,
												                'comment':comment,
												               }
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)

					if res.notes_one2many:
						for notes in res.notes_one2many:
									if notes.source:
										source_srch = [('name','=',notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('comment','=',notes.name),('user_id','=',notes.user_name),('source','=',source_id[0]),('comment_date','=',notes.date),('indent_id','=',origin_ids[0])]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
									if remark_srch_id:
									   for test in remark_srch_id:
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'unlink', test)
									if not remark_srch_id:
										msg_flag_branch=True

									notes_line = {
										                    'indent_id':origin_ids[0],
										                    'user_id':notes.user_name if notes.user_name else '',
										                    'state':notes.state,
												    			'source':source_id[0] if source_id else '',
										                    'comment_date':notes.date,
										                    'comment':notes.name,
										                   }
									notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)
					if msg_flag_branch:
						msg_line = {
									'msg_check':True
								   }
						msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)
						
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
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag_1 = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_prepare_packlist_central','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag_1})


			sock = xmlrpclib.ServerProxy(obj)

			if conn_flag_1 == False:

				for rec in self.browse(cr,uid,ids):
					origin_srch = [('id','=',ci_sync_id),('origin', '=',rec.origin)]
					origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
					if origin_ids:
						for ln in rec.stock_transfer_product:
						 if ln.state!='cancel_order_qty':  	
					
							product_srch = [('name', '=',ln.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
							ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
							if ln_ids:

									pick_line = {
										'state':'packlist'
									   }
									move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)

							if ln.notes_one2many:
								for material_notes in ln.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									source_id=0
									if material_notes.source:
										source_srch = [('name','=',material_notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
									if remark_srch_id:
									   for test in remark_srch_id:
										notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
									if not remark_srch_id:
										msg_flag=True
										msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
											}
										msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids ,msg_unread)
									notes_line = {
										                    'indent_id':ln_ids[0],
										                    'user_id':user_name if user_name else '',
												    			'source':source_id[0] if source_id else '',
										                    'comment_date':comment_date,
										                    'comment':comment,
										                   }
									notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)

						if rec.notes_one2many:
							for notes in rec.notes_one2many:
									if notes.source:
										source_srch = [('name','=',notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('remark','=',origin_ids[0]),('remark_field','=',notes.name),('user','=',notes.user_name),('source','=',source_id[0]),('date','=',notes.date)]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
									if remark_srch_id:
									    for test in remark_srch_id:
											notes_line = {
										                    'user':notes.user_name if notes.user_name else '',
										                    'source':source_id[0] if source_id else '',
										                    'date':notes.date,
										                    'remark_field':notes.name,
										                   }
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', test, notes_line)
									else:
									    msg_flag=True
									    create_notes_line = {
												    'remark':origin_ids[0],
												    'user':notes.user_name if notes.user_name else '',
												    'source':source_id[0] if source_id else '',
												    'date':notes.date,
												    'remark_field':notes.name,
										                   }
									    notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)

					if msg_flag:
						msg_line = {
									'msg_check':True
								   }
						msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)
		return True

	def sync_ready_to_dispatch(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag=False
		conn_flag_1=False
		for res in self.browse(cr,uid,ids):
			ci_sync_id = res.ci_sync_id
			form_branch_id = res.form_branch_id
			delivery_location = res.delivery_location
			vpn_ip_addr = delivery_location.vpn_ip_address
			port = delivery_location.port
			dbname = delivery_location.dbname
			pwd = delivery_location.pwd
			user_name = str(delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_ready_to_dispatch_branch','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
			sock = xmlrpclib.ServerProxy(obj)

			if conn_flag == False:

				origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
				origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
				if origin_ids:
					for line in res.stock_transfer_product:
						if line.state!='cancel_order_qty':  	
							product_srch = [('name', '=',line.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							prod_srch = [('product_id', '=',product_ids[0]),('line_id','=',origin_ids[0])]
							prod_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', prod_srch)

							if prod_ids:
								pick_line = {
									'state':'dispatch',
									'eta':res.expected_delivery_time,
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', prod_ids, pick_line)
								eta_picking1 = {
									'order_id':res.origin,
								   }
								eta_pick_write1 = sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids[0], eta_picking1)

								if line.notes_one2many:
									for material_notes in line.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',prod_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)

										if not remark_srch_id:
											msg_flag_branch=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',prod_ids ,msg_unread)
										notes_line = {
												                'indent_id':prod_ids[0],
												                'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                'comment_date':comment_date,
												                'comment':comment,
												               }
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)
					if res.notes_one2many:
						for notes in res.notes_one2many:
									if notes.source:
										source_srch = [('name','=',notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('comment','=',notes.name),('user_id','=',notes.user_name),('source','=',source_id[0]),('comment_date','=',notes.date),('indent_id','=',origin_ids[0])]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
									if remark_srch_id:
									   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'unlink', test)

									if not remark_srch_id:
										msg_flag_branch=True
									notes_line = {
										      'indent_id':origin_ids[0],
										      'user_id':notes.user_name if notes.user_name else '',
										      'state':notes.state,
												  'source':source_id[0] if source_id else '',
										      'comment_date':notes.date,
										      'comment':notes.name,
										        }
									notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)

					if msg_flag_branch:
						msg_line = {
									'msg_check':True
								   }
						msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)
						
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
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					offline_obj=self.pool.get('offline.sync')
					offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag_1 = True
					if not offline_sync_sequence:
						offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_ready_to_dispatch_central','error_log':Err,})
					else:
						offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
						offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag_1})					
				sock = xmlrpclib.ServerProxy(obj)
				if conn_flag_1 == False:
			
					origin_srch = [('id','=',ci_sync_id),('origin', '=',res.origin)]
					origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
					if origin_ids:
						for ln in res.stock_transfer_product:
					 	 if ln.state!='cancel_order_qty':  				
							product_srch = [('name', '=',ln.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
							ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
							if ln_ids:
								pick_line = {
									'state':'dispatch',
									'eta':res.expected_delivery_time,#Pallavi 17 Dec
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)
								eta_picking = {
									'origin':res.origin,
								   }
								eta_pick_write = sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, eta_picking)
								if ln.notes_one2many:
									for material_notes in ln.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids ,msg_unread)
										notes_line = {
												                'indent_id':ln_ids[0],
												                'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                'comment_date':comment_date,
												                'comment':comment,
												               }
										notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
						if res.notes_one2many:
							for notes in res.notes_one2many:
									if notes.source:
										source_srch = [('name','=',notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('remark_field','=',notes.name),('user','=',notes.user_name),('source','=',source_id[0]),('remark','=',origin_ids[0]),('date','=',notes.date)]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
									if remark_srch_id:
									   for test in remark_srch_id:
										notes_line = {

										                    'user':notes.user_name if notes.user_name else '',
										                    'source':source_id[0] if source_id else '',
										                    'date':notes.date,
										                    'remark_field':notes.name,
										                   }
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', test, notes_line)
									else:
										msg_flag=True
										create_notes_line = {
												    'remark':origin_ids[0],
										        'user':notes.user_name if notes.user_name else '',
										        'source':source_id[0] if source_id else '',
										        'date':notes.date,
										        'remark_field':notes.name,
										                   }
										notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)
						if msg_flag:
							msg_line = {
										'msg_check':True
									   }
							msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)
			return True

	def update_department_dispatch(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		ci_sync_id = ''
		msg_flag=False
		conn_flag=False
		for i in self.browse(cr, uid, ids):
			ci_sync_id = i.ci_sync_id
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
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					offline_obj=self.pool.get('offline.sync')
					offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					if not offline_sync_sequence:
						offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'update_department_dispatch','error_log':Err,})
					else:
						offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
						offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
				sock = xmlrpclib.ServerProxy(obj)

				if conn_flag == False:

					origin_srch = [('id','=',ci_sync_id),('origin', '=',i.origin)]
					origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
					if origin_ids:
						for ln in i.stock_transfer_product:
						 if ln.state!='cancel_order_qty':  							
							product_srch = [('name', '=',ln.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
							ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
							if ln_ids:
								pick_line = {
									'state':'intransit'
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)

								if ln.notes_one2many:
									for material_notes in ln.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids ,msg_unread)
										notes_line = {
												                'indent_id':ln_ids[0],
												                'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                'comment_date':comment_date,
												                'comment':comment,
												               }
										notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
						if i.notes_one2many:
							for notes in i.notes_one2many:
									if notes.source:
										source_srch = [('name','=',notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('remark','=',origin_ids[0]),('remark_field','=',notes.name),('user','=',notes.user_name),('source','=',source_id[0]),('date','=',notes.date)]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
									if remark_srch_id:
									     for test in remark_srch_id:
									     	notes_line = {
												                'user':notes.user_name if notes.user_name else '',
												                'source':source_id[0] if source_id else '',
												                'date':notes.date,
												                'remark_field':notes.name,
												               }
									     	notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', test, notes_line)
									else:
										msg_flag=True
										create_notes_line = {
												    'remark':origin_ids[0],
										        'user':notes.user_name if notes.user_name else '',
										        'source':source_id[0] if source_id else '',
										        'date':notes.date,
										        'remark_field':notes.name,
										                   }
										notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)
						if msg_flag:
							msg_line = {
										'msg_check':True
									   }
							msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)
		return conn_flag


	def update_branch_state(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		form_branch_id = ''
		msg_flag_branch=False
		conn_flag=False
		for res in self.browse(cr,uid,ids):
			form_branch_id = res.form_branch_id
			delivery_location = res.delivery_location
			vpn_ip_addr = delivery_location.vpn_ip_address
			port = delivery_location.port
			dbname = delivery_location.dbname
			pwd = delivery_location.pwd
			user_name = str(delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'update_branch_state','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})			
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:

				origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
				origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
				if origin_ids:
					for line in res.stock_transfer_product:
						if line.state!='cancel_order_qty':  							
							product_srch = [('name', '=',line.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							prod_srch = [('product_id', '=',product_ids[0]),('line_id','=',origin_ids[0])]
							prod_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', prod_srch)

							if prod_ids:
								pick_line = {
									'state':'intransit'
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', prod_ids, pick_line)
								if line.notes_one2many:
									for material_notes in line.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',prod_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag_branch=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',prod_ids ,msg_unread)
										notes_line = {
												                'indent_id':prod_ids[0],
												                'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                'comment_date':comment_date,
												                'comment':comment,
												               }
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)
					if res.notes_one2many:
						for notes in res.notes_one2many:
									if notes.source:
										source_srch = [('name','=',notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('comment','=',notes.name),('user_id','=',notes.user_name),('source','=',source_id[0]),('comment_date','=',notes.date),('indent_id','=',origin_ids[0])]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
									if remark_srch_id:
									   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'unlink', test)
									if not remark_srch_id:
										msg_flag_branch=True
									notes_line = {
										                    'indent_id':origin_ids[0],
										                    'user_id':notes.user_name if notes.user_name else '',
										                    'state':notes.state,
												    			'source':source_id[0] if source_id else '',
										                    'comment_date':notes.date,
										                    'comment':notes.name,
										                   }
									notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)

					if msg_flag_branch:
						msg_line = {
									'msg_check':True
								   }
						msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)
		return conn_flag

	def update_department_dispatch_delivery(self,cr,uid,ids,context=None):# .... This function is used for sales delivery
		if context is None : context = {} 
		msg_flag=False
		ci_sync_id = ''
		conn_flag = False
		for i in self.browse(cr, uid, ids):
			ci_sync_id = i.ci_sync_id
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
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					offline_obj=self.pool.get('offline.sync')
					offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					if not offline_sync_sequence:
						offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'update_department_dispatch_delivery','error_log':Err,})
					else:
						offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
						offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})					
				sock = xmlrpclib.ServerProxy(obj)
				if conn_flag == False:
					origin_srch = [('id','=',ci_sync_id),('origin', '=',i.origin)]
					origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
					if origin_ids:
						for ln in i.stock_transfer_product:
						 if ln.state!='cancel_order_qty':  							
							product_srch = [('name', '=',ln.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
							ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
						
							if ln_ids:
								pick_line = {
									'state':'done'
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)

								if ln.notes_one2many:
									for material_notes in ln.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids ,msg_unread)
										notes_line = {
												                'indent_id':ln_ids[0],
												                'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                'comment_date':comment_date,
												                'comment':comment,
												               }
										notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)

							notes_state_srch = [('product_id', '=',product_ids[0]),('product_code','=',ln.product_code),('dispatcher','=',i.source.name),('origin','=',ln.origin)]
							notes_state_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', notes_state_srch)
			
							if notes_state_ids:

								fields = ['picking_id'] #fields to read
								data = sock.execute(dbname, userid, pwd, 'stock.move', 'read', notes_state_ids, fields)

								for pick in data:
									print "DDDDDDDDDDDDDD",pick['picking_id'][0]

								srch_stock = [('id','=',pick['picking_id'][0])]
								stock_srch_id = sock.execute(dbname,userid,pwd,'stock.picking','search',srch_stock)
								for notes in i.notes_one2many:
									if notes.source:
								                source_srch = [('name','=',notes.source.name)]
								                source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('remark_field','=',notes.name),('user','=',notes.user_name),('source','=',source_id[0]),('date','=',notes.date)]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
									if remark_srch_id:
									     for test in remark_srch_id:
											notes_line = {
												                'user':notes.user_name if notes.user_name else '',
												                'source':source_id[0] if source_id else '',
												                'date':notes.date,
												                'remark_field':notes.name,
												               }
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', test, notes_line)

									if not remark_srch_id:
										msg_flag=True
										create_notes_line = {
												    'remark':stock_srch_id[0],
										                    'user':notes.user_name if notes.user_name else '',
										                    'source':source_id[0] if source_id else '',
										                    'date':notes.date,
										                    'remark_field':notes.name,
										                   }
										notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)
						if msg_flag:
							msg_line = {
										'msg_check':True
									   }
							msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)
								
		return conn_flag

	def update_branch_state_delivery(self,cr,uid,ids,context=None):# .... This function is used for sales delivery
		if context is None : context = {} 
		msg_flag_branch=False
		form_branch_id = ''
		conn_flag = False
		for res in self.browse(cr,uid,ids):
			form_branch_id = res.form_branch_id
			delivery_location = res.delivery_location
			vpn_ip_addr = delivery_location.vpn_ip_address
			port = delivery_location.port
			dbname = delivery_location.dbname
			pwd = delivery_location.pwd
			user_name = str(delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'update_branch_state_delivery','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})			
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:
				for line in res.stock_transfer_product:
					origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
					origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)

					if origin_ids:
					 if line.state!='cancel_order_qty':  							
							product_srch = [('name', '=',line.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							prod_srch = [('product_id', '=',product_ids[0]),('line_id','=',origin_ids[0])]
							prod_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', prod_srch)

							if prod_ids:
								pick_line = {
									'state':'received'
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', prod_ids, pick_line)

								if line.notes_one2many:
									for material_notes in line.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',prod_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag_branch=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',prod_ids ,msg_unread)
										notes_line = {
												                    'indent_id':prod_ids[0],
												                    'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                    'comment_date':comment_date,
												                    'comment':comment,
												                   }
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)
					 if msg_flag_branch:
						msg_line = {
									'msg_check':True
								   }
						msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)

				if res.notes_one2many:
					for notes in res.notes_one2many:
						origin_srch = [('order_id', '=',res.origin)]
						origin_ids1 = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
						if origin_ids1:
									if notes.source:
								                    source_srch = [('name','=',notes.source.name)]
								                    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('comment','=',notes.name),('user_id','=',notes.user_name),('source','=',source_id[0]),('comment_date','=',notes.date),('indent_id','=',origin_ids1[0])]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
									if remark_srch_id:
									   for test in remark_srch_id:
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'unlink', test)
									if not remark_srch_id:
										msg_flag_branch=True
									notes_line = {
										                        'indent_id':origin_ids1[0],
										                        'user_id':notes.user_name if notes.user_name else '',
										                        'state':notes.state,
																'source':source_id[0] if source_id else '',
										                        'comment_date':notes.date,
										                        'comment':notes.name,
										                       }
									notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)
									if msg_flag_branch:
										msg_line = {
												'msg_check':True
													}
										msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)

				if res.delivery_type=="export_delivery":
				 		receive_origin = [('indent_no','=',res.origin),('state','=','intransit'),('order_number','=',res.stock_transfer_no)]
				 		receive_origin_ids = sock.execute(dbname, userid, pwd, 'receive.indent', 'search', receive_origin)

				 		if receive_origin_ids:
				 			material_srch = [('indent_id','=',receive_origin_ids[0])]
				 			material_id = sock.execute(dbname,userid,pwd,'material.details','search',material_srch)
				 			if material_id:
								recieve_state = {
									'state':'done',
								   }
								recieve_state_ids= sock.execute(dbname, userid, pwd, 'receive.indent', 'write', receive_origin_ids, recieve_state)
		return conn_flag

	def sync_dispatch_dashboard(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		remark_srch_id = False
		conn_flag = False
		year = ''
		dict1 = {
				1: 'January', 
				2: 'February', 
				3: 'March',
				4:'April',
				5:'May',
				6:'June',
				7:'July',
				8:'August',
				9:'September',
				10:'October',
				11:'November',
				12:'December'
			};

		#user_ids = []
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
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_dispatch_dashboard','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:
				current_date=date.today()
				monthee = current_date.month
				year = current_date.year
				words_month = dict1[monthee]
				srh1 = [('month','=',words_month),('year','=',year)]
				search = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'search', srh1)
				if search == []:
					crt1 = {
							'month':words_month,
							'count':'1',
							'year':year,
							'month_id':monthee,
							}
					create = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'create', crt1)
				else:
					count3 = ['count']
					count4 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'read', search[0], count3)
					count = count4['count']
					count1 = int(count) + 1
					wrt = {'count':count1}
					write = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', search[0], wrt)
				variable1 = [('id','>',0)]
				variable = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'search', variable1)
				if variable == []:
					print""
				else:
					for var in variable:
						wr_val = {'count1':'','count2':''}
						write_final = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', var, wr_val)
					var1 = [('id','>',0)]
					vart = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'search', var1)
					for test in vart:
						current_date=date.today()
						month = current_date.month
						year = current_date.year
						previous_year = year - 1
						count5 = ['count']
						count6 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'read', test, count5)
						count = count6['count']
						year3 = ['year']
						year2 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'read', test, year3)
						y = year2['year']
						if y:
							if y == str(year):
								write2 = {'check':True,'check1':False}
								write3 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', test, write2)
								write7 = {'count2':count}
								write8 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', test, write7)
							if y == str(previous_year):
								write4 = {'check1':True}
								write5 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', test, write4)
								write6 = {'count1':count}
								write9 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', test, write6)
					
		return conn_flag

	def sync_dispatch(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		msg_flag_branch=False
		generic_id=''
		conn_flag = False
		for i in self.browse(cr, uid, ids):
			ci_sync_id = i.ci_sync_id
			form_branch_id = i.form_branch_id
			transporter_ids = False
			transporter_id1 = ['']
			vpn_ip_addr = i.delivery_location.vpn_ip_address
			port = i.delivery_location.port
			dbname = i.delivery_location.dbname
			pwd = i.delivery_location.pwd
			branch_type_temp=i.delivery_location.branch_type
			user_name = str(i.delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':i.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_dispatch','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:
				if i.source :
					source = [('name','=',i.source.name)]
					source_ids = sock.execute(dbname, userid, pwd,'res.company','search',source)

				if i.delivery_location:		
					delivery_location_srch = [('name','=',i.delivery_location.name)]
					location = sock.execute(dbname, userid, pwd,'res.company','search',delivery_location_srch)	

				concern_branch_ids=0
				cust_ids=0
				if i.branch_name :
					concern_branch = [('name','=',i.branch_name.name)]
					concern_branch_ids = sock.execute(dbname, userid, pwd,'res.company','search',concern_branch)

				if i.customer_vat_tin or i.customer_cst_no:
					cust_search =[('vat','=',i.customer_vat_tin),('cst_no','=',i.customer_cst_no)]
					cust_ids = sock.execute(dbname, userid, pwd,'res.customer','search',cust_search)
		
				stock = {
	   				'indent_no': i.origin,
					'indent_date':i.date,
					'transporter':i.transporter.transporter_name if i.transporter else '' ,
					'type':'internal',
					'delivery_name':'direct_delivery',
					'source_company':source_ids[0] ,
					'new_delivery_type':i.delivery_type_char,
	  				'delivery_type':i.delivery_type,	
	  				'branch_name':concern_branch_ids[0] if i.branch_name else location[0],
					'customer_name':cust_ids[0] if i.customer_vat_tin or i.customer_cst_no else '', 
					'stock_id': i.stock_id,
					'order_number':i.stock_transfer_no,
					'po_no_sync': i.stock_transfer_no,
					'po_sync_date': i.stock_transfer_date_new,
					'eta_sync': i.expected_delivery_time,
					'delivery_challan_no': i.delivery_challan_no,
					'delivery_challan_date': i.delivery_challan_date,
					'ci_sync_id': i.ci_sync_id if i.ci_sync_id else '',
					'form_branch_id': i.form_branch_id if i.form_branch_id else '',
					'branch_name':concern_branch_ids[0] if i.branch_name else location[0],
					'road_permit_no':i.road_permit_no,
					'road_permit_date':i.road_permit_date,
				}
			
				stock_id = sock.execute(dbname, userid, pwd, 'receive.indent', 'create', stock)
				for k in i.stock_transfer_product :
	 			 variable_status = False
				 if k.product_name.type_product=='track_equipment':
		 			 variable_status = True	
				 if k.state!='cancel_order_qty':
					batch_id1=[]
					batch_id1=[]
					prod_data=[]

					prod_name = [('name', '=',k.product_name.name)]
					prod_id = sock.execute(dbname, userid, pwd, 'product.product', 'search', prod_name)
					if isinstance(prod_id, (list, tuple)) and prod_id:
						prod_id = prod_id[0]
					if prod_id:
						prod_fields = ['name','default_code','categ_id','uom_id','fsi_level']
						prod_data = sock.execute(dbname, userid, pwd, 'product.product', 'read', prod_id, prod_fields)

					if k.product_name:
							prod_search_d=self.pool.get('product.product').browse(cr,uid,k.product_name.id)
							uom_name=prod_search_d.local_uom_id.name
							product_srch = [('name', '=',k.product_name.name)] 
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							product_qty = [('name','=',k.product_uom.name)]
							product_qty_ids = sock.execute(dbname, userid, pwd, 'product.uom', 'search',product_qty )
							product_qty_local = [('name','=',uom_name)]
							product_qty_local_ids = sock.execute(dbname, userid, pwd, 'product.uom', 'search',product_qty_local )

					if k.generic_id:
							generic_id_srch = [('name', '=',k.generic_id.name)] 
							generic_id = sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_id_srch)

					batch_ids=[]	
					if k.batch.id :
						if branch_type_temp=='branch_type' :
							batch_srch = [('batch_no','=',k.batch.batch_no),('name','=',prod_id),('branch_name','=',concern_branch_ids[0] if concern_branch_ids else location[0])]
						else :
							batch_srch = [('batch_no','=',k.batch.batch_no),('name','=',prod_id)]
						batch_ids = sock.execute(dbname, userid, pwd, 'res.batchnumber', 'search', batch_srch)
						if not batch_ids:
							if i.delivery_location.branch_type=='branch_type':
									batch= {
									'batch_source':'direct_delivery',
									'name':prod_id,
									'generic_id':generic_id[0] if k.generic_id else False,
									'batch_no':k.batch.batch_no,
									'manufacturing_date':k.batch.manufacturing_date if k.batch.manufacturing_date else False,
									'exp_date':k.batch.exp_date if k.batch.exp_date else False,
									'st':k.batch.st,
									'distributor':0.0,#k.batch.distributor,
									'export_price':0.0,#k.batch.export_price,
									'mrp':0.0,#k.batch.mrp,	
									'uom':product_qty_ids[0],
									#'local_uom_id':product_qty_local_ids[0],
									'product_code':k.batch.product_code,
									'bom': 0.0,#k.batch.bom
									}
							else:		
								batch= {
								'batch_source':'direct_delivery',
								'name':prod_id,
								'generic_id':generic_id[0] if k.generic_id else False,
								'batch_no':k.batch.batch_no,
								'manufacturing_date':k.batch.manufacturing_date if k.batch.manufacturing_date else False,
								'exp_date':k.batch.exp_date if k.batch.exp_date else False,
								'st':k.batch.st,
								'distributor':k.batch.distributor if k.batch.distributor else False,
								'export_price':k.batch.export_price , 
								'mrp':k.batch.mrp,	
								'uom':product_qty_ids[0],
								'local_uom_id':product_qty_local_ids[0],
								'product_code':k.batch.product_code,
								'bom':k.batch.bom,
								'branch_name':concern_branch_ids[0] if i.branch_name else location[0],
								}
							batch_id1 = sock.execute(dbname, userid, pwd, 'res.batchnumber', 'create',batch )

					stock_tran_prod = {
						'indent_id':stock_id,
						'product_name':product_ids[0],
						'generic_id':generic_id[0] if generic_id else False,
						'product_code':k.product_code,
						'batch':batch_ids[0] if batch_ids else batch_id1,
						'product_uom':product_qty_ids[0],
						'manufacturing_date':k.mfg_date,
						'price_unit':k.rate,
						'local_uom':product_qty_ids[0],
						'indented_quantity':k.qty_indent,
						'product_qty':k.quantity,
						'series_check_new':variable_status,  
						'branch_name':concern_branch_ids[0] if i.branch_name else location[0],
						}
					stock_tran_prod_id = sock.execute(dbname, userid, pwd, 'material.details','create', stock_tran_prod)
					if k.serial_line:
						for serials in k.serial_line:
							create_serials={
								'line':stock_tran_prod_id ,
								'series_line':stock_tran_prod_id ,
								'product_code':serials.product_code if serials.product_code else '',
								'product_name':product_ids[0] if product_ids else '',
								'generic_id':generic_id[0] if generic_id else False,
								#'product_category':serials.product_category.id,
								'product_uom':product_qty_ids[0] if product_qty_ids else '',
								'batch':batch_ids[0] if batch_ids else batch_id1,
								'quantity':serials.quantity if serials.quantity else '',
								'serial_name':serials.serial_no.serial_no if serials.serial_no.serial_no else '',
								'active_id':serials.active_id if serials.active_id else '',
								'serial_check':serials.serial_check if serials.serial_check else '',

								}
							create_serials_id = sock.execute(dbname, userid, pwd, 'transfer.series','create', create_serials)

					if k.notes_one2many:
							for material_notes in k.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									source_id=0
									msg_flag_branch=True
									if material_notes.source:
										source_srch = [('name','=',material_notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
									notes_line = {
										                    'indent_id':stock_tran_prod_id,
										                    'user_id':user_name if user_name else '',
												    			'source':source_id[0] if source_id else '',
										                    'comment_date':comment_date,
										                    'comment':comment,
										                   }
									notes_line_id = sock.execute(dbname, userid, pwd, 'material.details.comment.line', 'create', notes_line)
									msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
										}
									msg_unread_ids= sock.execute(dbname, userid, pwd, 'material.details', 'write',stock_tran_prod_id ,msg_unread)

				if i.notes_one2many :	
						msg_flag_branch=True
						for h in i.notes_one2many:
							if h.source:
								source_srch = [('name','=',h.source.name)]
								source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
							user_sync = {
											'receive_indent_id':int(stock_id),
											'user_id':h.user_name if h.user_name else '',
											'state': h.state,
											'comment_date':h.date,
											'source':source_id[0] if source_id else '',
											'comment':h.name,
										}
							user_sync1 = sock.execute(dbname, userid, pwd, 'receive.indent.comment.line','create', user_sync)

				if msg_flag_branch:
					msg_line = {
							'msg_check':True
								}
					msg_ids= sock.execute(dbname, userid, pwd, 'receive.indent', 'write',int(stock_id), msg_line)

		self.update_department_dispatch(cr,uid,ids,context=context)
		self.update_branch_state(cr,uid,ids,context=context)
		return conn_flag

	def sync_cancel_packlist_central_indent(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		ci_sync_id = ''
		form_branch_id = ''
		origin = ''
		remark_srch_id = False
		msg_flag=False
		conn_flag = False
		for res1 in self.browse(cr,uid,ids):
			ci_sync_id = res1.ci_sync_id
			form_branch_id = res1.form_branch_id
			origin = res1.origin
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
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_packlist_central_indent','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})			
			sock = xmlrpclib.ServerProxy(obj)

			if conn_flag == False:

				origin_srch = [('id','=',ci_sync_id),('origin', '=',origin)]
				origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
				if origin_ids:
					for res in self.browse(cr,uid,ids):
							for ln in res.stock_transfer_product:
								product_srch = [('name', '=',ln.product_name.name)]
								product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
								ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
								ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)

								if ln_ids:
									pick_line = {'state':'view_order',}
									move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)
									if ln.notes_one2many:
										for material_notes in ln.notes_one2many:
											user_name=material_notes.user_id
											source=material_notes.source.id
											comment=material_notes.comment
											comment_date=material_notes.comment_date
											source_id=0
											if material_notes.source:
												source_srch = [('name','=',material_notes.source.name)]
												source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

											remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
											remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
											if remark_srch_id:
											   for test in remark_srch_id:
												notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
											if not remark_srch_id:
												msg_flag=True
												msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
													}
												msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids,msg_unread)				
											notes_line = {
														            'indent_id':ln_ids[0],
														            'user_id':user_name if user_name else '',
																		'source':source_id[0] if source_id else '',
														            'comment_date':comment_date,
														            'comment':comment,
														           }
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)

							if res.notes_one2many:
								  for notes in res.notes_one2many:
											if notes.source:
												source_srch = [('name','=',notes.source.name)]
												source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

											remark_srch = [('remark','=',origin_ids[0]),('remark_field','=',notes.name),('user','=',notes.user_name),('date','=',notes.date)]
											remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
											if remark_srch_id:
												for test in remark_srch_id:
													notes_line = {
														    'user':notes.user_name if notes.user_name else '',
														    'source':source_id[0] if source_id else '',
														    'date':notes.date,
														    'remark_field':notes.name,
														   }
												notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', test, notes_line)
											if not remark_srch_id:
												msg_flag=True
												create_notes_line = {
													    		'remark':origin_ids[0],
												            'user':notes.user_name if notes.user_name else '',
												            'source':source_id[0] if source_id else '',
												            'date':notes.date,
												            'remark_field':notes.name,
												           }
												notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)
				if msg_flag:
					msg_line = {
							'msg_check':True
								}
					msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write',origin_ids, msg_line)
		return conn_flag


	def sync_cancel_packlist(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		ci_sync_id = ''
		form_branch_id = ''
		remark_srch_id = False
		msg_flag = False
		conn_flag =False
		for res in self.browse(cr,uid,ids):
			ci_sync_id = res.ci_sync_id
			form_branch_id = res.form_branch_id
			delivery_location = res.delivery_location
			vpn_ip_addr = delivery_location.vpn_ip_address
			port = delivery_location.port
			dbname = delivery_location.dbname
			pwd = delivery_location.pwd
			user_name = str(delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''			
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_packlist','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})	
				
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:
				origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
				origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
				if origin_ids:
					for line in res.stock_transfer_product:
							product_srch = [('name', '=',line.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							prod_srch = [('product_id', '=',product_ids[0]),('line_id','=',origin_ids[0])]
							prod_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', prod_srch)

							if prod_ids:
								pick_line = {
									'state':'view_order',
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', prod_ids, pick_line)
								if line.notes_one2many:
									for material_notes in line.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',prod_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',prod_ids ,msg_unread)
										notes_line = {
												                'indent_id':prod_ids[0],
												                'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                'comment_date':comment_date,
												                'comment':comment,
												               }
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)

					if res.notes_one2many:
						for notes in res.notes_one2many:
										if notes.source:
										   source_srch = [('name','=',notes.source.name)]
										   source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('indent_id','=',origin_ids[0]),('comment','=',notes.name),('user_id','=',notes.user_name),('comment_date','=',notes.date)]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
										if remark_srch_id:
											for test in remark_srch_id:
												notes_line = {
														        'user_id':notes.user_name if notes.user_name else '',
														        'source':source_id[0] if source_id else '',
														        'comment_date':notes.date,
														        'comment':notes.name,
														       }
												notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'write', test, notes_line)
										else:
											msg_flag=True
											notes_line_new = {
												            'indent_id':origin_ids[0],
												            'user_id':notes.user_name if notes.user_name else '',
												            'source':source_id[0] if source_id else '',
												            'comment_date':notes.date,
												            'comment':notes.name,
												           }
											notes_line_id_new = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line_new)
					if msg_flag:
						msg_line = {
									'msg_check':True
									}
						msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)
		self.sync_cancel_packlist_central_indent(cr,uid,ids,context=context)
		return conn_flag

	def sync_cancel_delivery_order_central_indent(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		ci_sync_id = ''
		remark_srch_id = False
		msg_flag=False
		conn_flag=False
		#user_ids = []
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
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_delivery_order_central_indent','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})

			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:

				for res in self.browse(cr,uid,ids):
						ci_sync_id = res.ci_sync_id
						origin_srch = [('id','=',ci_sync_id),('origin', '=',res.origin)]
						origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
						if origin_ids:
							for ln in res.stock_transfer_product:
								product_srch = [('name', '=',ln.product_name.name)]
								product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
								ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
								ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)

								if ln_ids:
									pick_line = {'state':'pending',}
									move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)
									if ln.notes_one2many:
										for material_notes in ln.notes_one2many:
											user_name=material_notes.user_id
											source=material_notes.source.id
											comment=material_notes.comment
											comment_date=material_notes.comment_date
											source_id=0
											if material_notes.source:
												source_srch = [('name','=',material_notes.source.name)]
												source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

											remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
											remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
											if remark_srch_id:
											   for test in remark_srch_id:
												notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
											if not remark_srch_id:
												msg_flag=True

												msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
													}
												msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids ,msg_unread)
											notes_line = {
														            'indent_id':ln_ids[0],
														            'user_id':user_name if user_name else '',
																		'source':source_id[0] if source_id else '',
														            'comment_date':comment_date,
														            'comment':comment,
														           }
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
							if res.notes_one2many:
								for notes in res.notes_one2many:
											if notes.source:
												source_srch = [('name','=',notes.source.name)]
												source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

											remark_srch = [('remark','=',origin_ids[0]),('remark_field','=',notes.name),('user','=',notes.user_name),('date','=',notes.date,)]
											remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
											if remark_srch_id:
												for test in remark_srch_id:
													notes_line = {
														    'user':notes.user_name if notes.user_name else '',
														    'source':source_id[0] if source_id else '',
														    'date':notes.date,
														    'remark_field':notes.name,
														   }
													notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', test, notes_line)
											else:
												msg_flag=True
												create_notes_line = {
													    		'remark':origin_ids[0],
												            'user':notes.user_name if notes.user_name else '',
												            'source':source_id[0] if source_id else '',
												            'date':notes.date,
												            'remark_field':notes.name,
												           }
												notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)
							if msg_flag:
								msg_line = {
											'msg_check':True
											}
								msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)

		return conn_flag

	def sync_cancel_delivery_order(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		remark_srch_id = False
		form_branch_id = ''
		msg_flag_branch = False
		msg_flag_receive = False
		conn_flag = False
		for res in self.browse(cr,uid,ids):
			form_branch_id = res.form_branch_id
			delivery_location = res.delivery_location
			vpn_ip_addr = delivery_location.vpn_ip_address
			port = delivery_location.port
			dbname = delivery_location.dbname
			pwd = delivery_location.pwd
			user_name = str(delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_delivery_order','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})

			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:

				origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
				origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
				if origin_ids:
					for line in res.stock_transfer_product:
							product_srch = [('name', '=',line.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							prod_srch = [('product_id', '=',product_ids[0]),('line_id','=',origin_ids[0])]
							prod_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', prod_srch)
							if prod_ids:
								pick_line = {
									'state':'progress',
								   } 
								move_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', prod_ids, pick_line)

								if line.notes_one2many:
									for material_notes in line.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',prod_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag_branch=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',prod_ids,msg_unread)
										notes_line = {
												                'indent_id':prod_ids[0],
												                'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                'comment_date':comment_date,
												                'comment':comment,
												               }
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)
					if res.notes_one2many:
						for notes in res.notes_one2many:
										if notes.source:
										        source_srch = [('name','=',notes.source.name)]
										        source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('indent_id','=',origin_ids[0]),('comment','=',notes.name),('user_id','=',notes.user_name),('state','=',notes.state)]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
										if remark_srch_id:
											for test in remark_srch_id:
												notes_line = {
												            'user_id':notes.user_name if notes.user_name else '',
												            'source':source_id[0] if source_id else '',
												            'comment_date':notes.date,
												            'comment':notes.name,
												           }
												notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'write', test, notes_line)
										else:
											msg_flag_branch=True
											notes_line_new = {
												            'indent_id':origin_ids[0],
												            'user_id':notes.user_name if notes.user_name else '',
												            'source':source_id[0] if source_id else '',
												            'comment_date':notes.date,
												            'comment':notes.name,
												           }
											notes_line_id_new = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line_new)
					if msg_flag_branch:
						msg_line = {
									'msg_check':True
									}
						msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)

				receive_origin = [('indent_no','=',res.origin),('order_number','=',res.stock_transfer_no)]
				receive_origin_ids = sock.execute(dbname, userid, pwd, 'receive.indent', 'search', receive_origin)
				if receive_origin_ids:
					recieve_state = {
									'state':'cancel',
								   }
					recieve_state_ids= sock.execute(dbname, userid, pwd, 'receive.indent', 'write', receive_origin_ids, recieve_state)
					if res.notes_one2many:
						for notes in res.notes_one2many:
										if notes.source:
										        source_srch = [('name','=',notes.source.name)]
										        source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('receive_indent_id','=',receive_origin_ids[0]),('comment','=',notes.name),('user_id','=',notes.user_name),('state','=',notes.state)]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'receive.indent.comment.line', 'search', remark_srch)
										if remark_srch_id:
											for test in remark_srch_id:
												notes_line = {
												            'user_id':notes.user_name if notes.user_name else '',
												            'source':source_id[0] if source_id else '',
												            'comment_date':notes.date,
												            'comment':notes.name,
												           }
												notes_line_id = sock.execute(dbname, userid, pwd, 'receive.indent.comment.line', 'write', test, notes_line)
										else:
											msg_flag_receive=True

											notes_line_new = {
												            'receive_indent_id':receive_origin_ids[0],
												            'user_id':notes.user_name if notes.user_name else '',
												            'source':source_id[0] if source_id else '',
												            'comment_date':notes.date,
												            'comment':notes.name,
												           }
											notes_line_id_new = sock.execute(dbname, userid, pwd, 'receive.indent.comment.line', 'create', notes_line_new)
					if res.stock_transfer_product:
							for ln in res.stock_transfer_product:
								product_srch = [('name', '=',ln.product_name.name)]
								product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
								ln_srch = [('product_name', '=',product_ids[0]),('indent_id','=',receive_origin_ids[0])]
								ln_ids = sock.execute(dbname, userid, pwd, 'material.details', 'search', ln_srch)
								if ln_ids:
									if ln.notes_one2many:
										for material_notes in ln.notes_one2many:
											user_name=material_notes.user_id
											source=material_notes.source.id
											comment=material_notes.comment
											comment_date=material_notes.comment_date
											source_id=0
											if material_notes.source:
												source_srch = [('name','=',material_notes.source.name)]
												source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

											remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
											remark_srch_id = sock.execute(dbname, userid, pwd, 'material.details.comment.line', 'search', remark_srch)
											if remark_srch_id:
											   for test in remark_srch_id:
												notes_line_id = sock.execute(dbname, userid, pwd, 'material.details.comment.line', 'unlink', test)
											if not remark_srch_id:
												msg_flag_receive=True
												msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
													}
												msg_unread_ids= sock.execute(dbname, userid, pwd, 'material.details', 'write',ln_ids ,msg_unread)
											notes_line = {
														            'indent_id':ln_ids[0],
														            'user_id':user_name if user_name else '',
																		'source':source_id[0] if source_id else '',
														            'comment_date':comment_date,
														            'comment':comment,
														           }
											notes_line_id = sock.execute(dbname, userid, pwd, 'material.details.comment.line', 'create', notes_line)

					if msg_flag_receive:
						msg_line = {
									'msg_check':True
									}
						msg_ids= sock.execute(dbname, userid, pwd, 'receive.indent', 'write', receive_origin_ids, msg_line)

		self.sync_cancel_delivery_order_central_indent(cr,uid,ids,context=context)
		return conn_flag

	def sync_cancel_stock_transfer(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
		for branch_id in self.pool.get('res.company').browse(cr,uid,branch_type):
			state_ids=False
			city_ids=False
			conn_flag=False
			vpn_ip_addr = branch_id.vpn_ip_address
			port = branch_id.port
			dbname = branch_id.dbname
			pwd = branch_id.pwd
			user_name = str(branch_id.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			city_ids=''
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_stock_transfer','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})	
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:
				for res in self.browse(cr,uid,ids):

					if res.delivery_location: #delivery_location  Contact person remain
						delivery_location_srch = [('name', '=',res.delivery_location.name)]
						delivery_location_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', delivery_location_srch)

					if res.source: 
						source_srch = [('name', '=',res.source.name)]
						source_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

					stock_transfer = {
								#'source':source_ids[0] if source_ids else create_source_id,
								'contact_person':res.contact_person,
								'delivery_location':delivery_location_ids[0] if delivery_location_ids else create_delivery_location_id,
								'stock_transfer_no':res.stock_transfer_no,
								'stock_transfer_date_new':res.stock_transfer_date_new if res.stock_transfer_date_new else False,
								'delivery_type':res.delivery_type,
								'contact_no':res.contact_no,
								'delivery_address':res.delivery_address,
								'total_amount':res.total_amount,
								'origin': res.origin,
								'date': res.date,
								'packlist_no1':res.packlist_no1 if res.packlist_no1 else False,
								'packlist_date1': res.packlist_date1 if res.packlist_date1 else False,
								#'branch_name': res.branch_name.name if res.branch_name else '',
								'total_weight': res.total_weight if res.total_weight else False,
								'mode_transport': res.mode_transport if res.mode_transport else False,
								'transporter': res.transporter.transporter_name if  res.transporter else False,
								'driver_name': res.driver_name if res.driver_name else False,
	 							'lr_no': res.lr_no if res.lr_no else False,
								'delivery_date': res.delivery_date if res.delivery_date else False,
								'estimated_value': res.estimated_value if res.estimated_value else False,
								'person_name': res.person_name if res.person_name else False,
								'vehicle_no': res.vehicle_no if res.vehicle_no else False,
								'mobile_no': res.mobile_no if res.mobile_no else False,
								'lr_date': res.lr_date if res.lr_date else False,
								'expected_delivery_time': res.expected_delivery_time if res.expected_delivery_time else False,
								'excise_invoice_no': res.excise_invoice_no if res.excise_invoice_no  else False,
								'packlist_no': res.packlist_no if res.packlist_no else False,
								'stock_transfer_note_no': res.stock_transfer_note_no if res.stock_transfer_note_no else False, 
								'delivery_challan_no': res.delivery_challan_no if res.delivery_challan_no else False,
								'stn_remark': res.stn_remark if res.stn_remark else False, 
								'delivery_challan_remark': res.delivery_challan_remark if res.delivery_challan_remark else False,
								'excise_invoice_date': res.excise_invoice_date if res.excise_invoice_date else False,
								'packlist_date': res.packlist_date if res.packlist_date else False,
								'stock_transfer_date': res.stock_transfer_date if res.stock_transfer_date else False,
								'delivery_challan_date': res.delivery_challan_date if res.delivery_challan_date else False,
								'source':source_ids[0] if source_ids else False,
								'indent_age':res.intent_age if res.intent_age else 0.00,
								'state':res.state,
									}

					create_branch_stock_transfer = sock.execute(dbname, userid, pwd, 'warehouse.stock.transfer', 'create', stock_transfer)
					for line in res.stock_transfer_product:
						stock_transfer_product = {
								
									'prod_id':create_branch_stock_transfer,
									'product_category':line.product_category.name if line.product_category else '',
									'product_code':line.product_code if line.product_code else '',
									'product_name':line.product_name.name if line.product_name else '',
									'product_uom':line.product_uom.name if line.product_uom else '',
									'available_quantity':line.available_quantity if line.available_quantity else '',
									'rate':line.rate if line.rate else False,
									'quantity':line.quantity if line.quantity else '',
									'mfg_date':line.mfg_date if line.mfg_date else False,
									'amount':line.amount if line.amount else '',
									'batch':line.batch.batch_no if line.batch else '',

									}

						create_stock_transfer_product = sock.execute(dbname, userid, pwd, 'product.transfer1', 'create', stock_transfer_product)
					if res.notes_one2many:
						  for pick in res.notes_one2many:
							add_notes1 = {
								'stock_transfer_id':create_branch_stock_transfer,
								'user_name1':pick.user_name,
								'date1':pick.date,
								'name1':pick.name,
								'source1': pick.source.name,
								'state': pick.state,

									}
							add = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks1', 'create', add_notes1)
		return conn_flag

	def sync_cancel_dashboard(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		remark_srch_id = False
		conn_flag = False
		year = ''
		dict1 = {
				1: 'January', 
				2: 'February', 
				3: 'March',
				4:'April',
				5:'May',
				6:'June',
				7:'July',
				8:'August',
				9:'September',
				10:'October',
				11:'November',
				12:'December'
			};

		#user_ids = []
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
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_dashboard','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
			sock = xmlrpclib.ServerProxy(obj)
			if not conn_flag:
				current_date=date.today()
				monthee = current_date.month
				year = current_date.year
				words_month = dict1[monthee]
				srh1 = [('month','=',words_month),('year','=',year)]
				search = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'search', srh1)
				if search == []:
					crt1 = {
							'month':words_month,
							'count':'1',
							'year':year,
							'month_id':monthee,
							}
					create = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'create', crt1)
				else:
					count3 = ['count']
					count4 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'read', search[0], count3)
					count = count4['count']
					count1 = int(count) - 1
					wrt = {'count':count1}
					write = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', search[0], wrt)
				variable1 = [('id','>',0)]
				variable = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'search', variable1)
				if variable == []:
					print""
				else:
					for var in variable:
						wr_val = {'count1':'','count2':''}
						write_final = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', var, wr_val)
					var1 = [('id','>',0)]
					vart = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'search', var1)
					for test in vart:
						current_date=date.today()
						month = current_date.month
						year = current_date.year
						previous_year = year - 1
						count5 = ['count']
						count6 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'read', test, count5)
						count = count6['count']
						year3 = ['year']
						year2 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'read', test, year3)
						y = year2['year']
						if y:
							if y == str(year):
								write2 = {'check':True,'check1':False}
								write3 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', test, write2)
								write7 = {'count2':count}
								write8 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', test, write7)
							if y == str(previous_year):
								write4 = {'check1':True}
								write5 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', test, write4)
								write6 = {'count1':count}
								write9 = sock.execute(dbname, userid, pwd, 'indent.dashboard', 'write', test, write6)
					
		return conn_flag

stock_transfer()

class product_transfer(osv.osv):
	_inherit = 'product.transfer'


	def offline_sync_product_transfer(self,cr,uid,ids,context = None):
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

	def sync_cancel_order_central(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		remark_srch_id = False
		source_name=''
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		conn_flag = False
		branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
		for branch_id in self.pool.get('res.company').browse(cr,uid,branch_type):
   				for k in self.browse(cr,uid,ids):
						var = k.prod_id.id
						search = self.pool.get('stock.transfer').search(cr,uid,[('id','=',k.prod_id.id)])
						for rec in self.pool.get('stock.transfer').browse(cr,uid,search):
							ci_sync_id = rec.ci_sync_id
							form_branch_id = rec.form_branch_id
						vpn_ip_addr = branch_id.vpn_ip_address
						port = branch_id.port
						dbname = branch_id.dbname
						pwd = branch_id.pwd
						user_name = str(branch_id.user_name.login)
						username = user_name #the user
						pwd = pwd    #the password of the user
						dbname = dbname
						userid = ''
						log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
						obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
						sock_common = xmlrpclib.ServerProxy (log)
						try:
							userid = sock_common.login(dbname, username, pwd)
						except Exception as Err:
							offline_obj=self.pool.get('offline.sync')
							offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
							conn_flag = True
							if not offline_sync_sequence:
								offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_order_central','error_log':Err,})
							else:
								offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
								offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})				
						sock = xmlrpclib.ServerProxy(obj)
						if not conn_flag:
							origin_srch = [('id','=',ci_sync_id),('origin', '=', k.origin)]
							origin = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
							if origin:
								product_srch = [('name', '=',k.product_name.name)]
								product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
								ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin[0])]
								ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
								if ln_ids:
									pick_line = {'state':'pending',}
									move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)
									if k.notes_one2many:
										for material_notes in k.notes_one2many:
											user_name=material_notes.user_id
											source=material_notes.source.id
											comment=material_notes.comment
											comment_date=material_notes.comment_date
											source_id=0
											if material_notes.source:
												source_srch = [('name','=',material_notes.source.name)]
												source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

											remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
											remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
											if remark_srch_id:
											   for test in remark_srch_id:
												notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
											if not remark_srch_id:
												msg_flag=True
												msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
													}
												msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids,msg_unread)

											notes_line = {
														                'indent_id':ln_ids[0],
														                'user_id':user_name if user_name else '',
																		'source':source_id[0] if source_id else '',
														                'comment_date':comment_date,
														                'comment':comment,
														               }
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
								for st_id in self.pool.get('stock.transfer').browse(cr,uid,[k.prod_id.id]):
									if st_id.notes_one2many:
										for notes in st_id.notes_one2many:
											if notes.source:
												source_srch = [('name','=',notes.source.name)]
												source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

											remark_srch = [('remark_field','=',notes.name),('user','=',notes.user_name),('source','=',source_id[0]),('date','=',notes.date),('remark','=',origin[0])]
											remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
											if remark_srch_id:
												for test in remark_srch_id:

													notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'unlink', test)
											if not remark_srch_id:
												msg_flag=True

											notes_line = {
															'remark':origin[0] if origin else '',
															'user':notes.user_name if notes.user_name else '',
															'source':source_id[0] if source_id else '',
															'date':notes.date,
															'remark_field':notes.name,
														}
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', notes_line)
								if msg_flag:
									msg_line = {
												'msg_check':True
												}
									msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin, msg_line)
								
		return conn_flag

	def sync_cancel_order(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		ci_sync_id = ''
		form_branch_id = ''
		delivery_location=0
		msg_flag_branch=False
		conn_flag = False
		for k in self.browse(cr,uid,ids):
			var = k.prod_id.id
			search = self.pool.get('stock.transfer').search(cr,uid,[('id','=',k.prod_id.id)])
			for rec in self.pool.get('stock.transfer').browse(cr,uid,search):
				delivery_location = rec.delivery_location
				ci_sync_id = rec.ci_sync_id
				form_branch_id = rec.form_branch_id
		remark_srch_id = False
		for res in self.browse(cr,uid,ids):
			vpn_ip_addr = delivery_location.vpn_ip_address
			port = delivery_location.port
			dbname = delivery_location.dbname
			pwd = delivery_location.pwd
			user_name = str(delivery_location.user_name.login)

			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_order','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})				
			sock = xmlrpclib.ServerProxy(obj)
			if not conn_flag:
				origin_srch = [('id','=',form_branch_id),('order_id','=',res.origin)]
				origin = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
				if origin:
					product_srch = [('name', '=',res.product_name.name)]
					product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
					prod_srch = [('product_id', '=',product_ids[0]),('line_id','=',origin[0])]
					prod_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', prod_srch)
					if prod_ids:
						pick_line = {
								'state':'progress',
							   }
						move_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', prod_ids[0], pick_line)
						if res.notes_one2many:
							for material_notes in res.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								source_id=0
								if material_notes.source:
									source_srch = [('name','=',material_notes.source.name)]
									source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

								remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',prod_ids[0])]
								remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
								if remark_srch_id:
								   for test in remark_srch_id:
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)
								if not remark_srch_id:
									msg_flag_branch=True
									msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
										}
									msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',prod_ids,msg_unread)
								notes_line = {
										     'indent_id':prod_ids[0],
										     'user_id':user_name if user_name else '',
										   	 'source':source_id[0] if source_id else '',
										     'comment_date':comment_date,
										     'comment':comment,
										     }
								notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)
					for st_id in self.pool.get('stock.transfer').browse(cr,uid,[res.prod_id.id]):
						if st_id.notes_one2many:
							for notes in st_id.notes_one2many:
										if notes.source:
										                source_srch = [('name','=',notes.source.name)]
										                source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',notes.name),('user_id','=',notes.user_name),('source','=',source_id[0]),('comment_date','=',notes.date),('indent_id','=',origin[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:

											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag_branch=True

										notes_line = {
												                    'indent_id':origin[0] if origin else '',
												                    'user_id':notes.user_name if notes.user_name else '',
																	'source':source_id[0] if source_id else '',
												                    'comment_date':notes.date,
												                    'comment':notes.name,
												                   }
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)
					if msg_flag_branch:
						msg_line = {
									'msg_check':True
									}
						msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin, msg_line)
						
			self.sync_cancel_order_central(cr,uid,ids,context=context)
			
		return conn_flag
product_transfer()


class mail_compose_message(osv.osv_memory):
	_inherit="mail.compose.message"

	def sync_road_permit(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		stock_transfer=self.pool.get('stock.transfer')
		for mail in self.browse(cr, uid, ids, context=context):
			for rec in stock_transfer.browse(cr,uid,[mail.stock_transfer_id.id]):
				ci_sync_id = rec.ci_sync_id
				form_branch_id = rec.form_branch_id
				delivery_location = rec.delivery_location
				vpn_ip_addr = delivery_location.vpn_ip_address
				port = delivery_location.port
				dbname = delivery_location.dbname
				pwd = delivery_location.pwd
				user_name = str(delivery_location.user_name.login)
				username = user_name #the user
				pwd = pwd    #the password of the user
				dbname = dbname
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception:
					raise osv.except_osv(('Alert!'),('No Connection.'))
				sock = xmlrpclib.ServerProxy(obj)
				origin_srch = [('id','=',form_branch_id),('order_id', '=',rec.origin)]
				origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
				if origin_ids:
					for line in rec.stock_transfer_product:
					  if line.state!='cancel_order_qty':  							
							product_srch = [('name', '=',line.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							prod_code = [('product_id', '=',product_ids[0]),('line_id','=',origin_ids[0])]
							code_id = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', prod_code)

							if code_id:
								pick_line = {
									'state':'dispatch',
									'eta':rec.expected_delivery_time,
								   }
								move_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', code_id, pick_line)

							if line.notes_one2many:
								for material_notes in line.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									source_id=0
									if material_notes.source:
										source_srch = [('name','=',material_notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',code_id[0])]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
									if remark_srch_id:
									   for test in remark_srch_id:
										notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)
									if not remark_srch_id:
										msg_flag_branch=True
										msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
											}
										msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',code_id ,msg_unread)
									notes_line = {
										                        'indent_id':code_id[0],
										                        'user_id':user_name if user_name else '',
																'source':source_id[0] if source_id else '',
										                        'comment_date':comment_date,
										                        'comment':comment,
										                       }
									notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)
					if rec.notes_one2many:
						for notes in rec.notes_one2many:
								if notes.source:
						                        source_srch = [('name','=',notes.source.name)]
						                        source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
								remark_srch = [('comment','=',notes.name),('user_id','=',notes.user_name),('indent_id','=',origin_ids[0]),('comment_date','=',notes.date),('source','=',source_id[0])]
								remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
								if remark_srch_id:
								    for var in remark_srch_id:
						                        notes_line1 = {
						                                    'user_id': notes.user_name if notes.user_name else '',
						                                    'source':source_id[0] if source_id else '',
						                                    'comment_date':notes.date,
						                                    'comment':notes.name,
						                                   }
								        notes_line_id1 = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'write', var, notes_line1)
								else:
									msg_flag_branch=True
									notes_line = {
								                            'indent_id':origin_ids[0],
								                            'user_id':notes.user_name if notes.user_name else '',
								                            'source':source_id[0] if source_id else '',
								                            'comment_date':notes.date,
								                            'comment':notes.name,
								                           }
									notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)

					if msg_flag_branch:
						msg_line = {
									'msg_check':True
									}
						msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)
		
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
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception:
					raise osv.except_osv(('Alert!'),('No Connection.'))
				sock = xmlrpclib.ServerProxy(obj)

				for mail in self.browse(cr, uid, ids, context=context):
					for res in stock_transfer.browse(cr,uid,[mail.stock_transfer_id.id]):
						ci_sync_id = res.ci_sync_id
						origin_srch = [('id','=',ci_sync_id),('origin', '=',res.origin)]
						origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
						if origin_ids:
							for ln in res.stock_transfer_product:
							 if ln.state!='cancel_order_qty':  							
								product_srch = [('name', '=',ln.product_name.name)]
								product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
								ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
								ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)

								if ln_ids:
									pick_line = {
										'state':'dispatch',
										'eta':res.expected_delivery_time,
									   }
									move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)

								if line.notes_one2many:
									for material_notes in line.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_srch = [('name','=',material_notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
										if remark_srch_id:
										   for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
										if not remark_srch_id:
											msg_flag=True
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids,msg_unread)
										notes_line = {
												                    'indent_id':ln_ids[0],
												                    'user_id':user_name if user_name else '',
																	'source':source_id[0] if source_id else '',
												                    'comment_date':comment_date,
												                    'comment':comment,
												                   }
										notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)

							if res.notes_one2many:
								for notes in res.notes_one2many:
									if notes.source:
										source_srch = [('name','=',notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('remark','=',origin_ids[0]),('remark_field','=',notes.name),('user','=',notes.user_name),('source','=',source_id[0]),('date','=',notes.date)]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
									if remark_srch_id:
										for var in remark_srch_id:
											notes_line = {
								                            'user':notes.user_name if notes.user_name else '',
								                            'source':source_id[0] if source_id else '',
								                            'date':notes.date,
								                            'remark_field':notes.name,
								                           }
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', var, notes_line)

									else:
										msg_flag=True
										create_notes_line = {
											    'remark':origin_ids[0],
											    'user':notes.user_name if notes.user_name else '',
											    'source':source_id[0] if source_id else '',
											    'date':notes.date,
											    'remark_field':notes.name,
								                           }
										notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)
							if msg_flag:
								msg_line = {
											'msg_check':True
											}
								msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)
				return True

mail_compose_message()


class stock_adjustment(osv.osv):

	_inherit = 'stock.adjustment'

	def offline_sync_stock_adjustment(self,cr,uid,ids,context = None):
		if context is None: context = {}
		sync_result = True
		offline_sync = context.get('offline_sync') if context.get('offline_sync') else False
		form_id = offline_sync.get('form_id') if offline_sync and offline_sync.get('form_id') else False
		offline_sync_sync = offline_sync.get('sync_sequence') if offline_sync and offline_sync.get('sync_sequence') else False
		context.update({'offline_sync_sync':offline_sync_sync})
		if form_id:
			sync_result = self.sync_stock_adjustment(cr,uid,[form_id],context=context)
		return sync_result


	def sync_stock_adjustment(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		conn_flag = False	
		for i in self.browse(cr,uid,ids):
			branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
			#Sync Code	
			for branch_id_new in self.pool.get('res.company').browse(cr,uid,branch_type):
				dbname = branch_id_new.dbname
				pwd = branch_id_new.pwd
				user_name = str(branch_id_new.user_name.login)
				username = user_name #the user
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(branch_id_new.vpn_ip_address,branch_id_new.port)
				obj = ('http://%s:%s/xmlrpc/object')%(branch_id_new.vpn_ip_address,branch_id_new.port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					offline_obj=self.pool.get('offline.sync')
					offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					if not offline_sync_sequence:
						offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':i,'error_log':Err,})
					else:
						offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
						offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
				sock = xmlrpclib.ServerProxy(obj)
				if 	conn_flag == False:
				    if i.product_name.id:
					    product_id_srch = [('name', '=',i.product_name.name)]
					    product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_id_srch)

					    generic_id_srch = [('name', '=',i.generic_id.name)]
					    generic_id = sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_id_srch)

					    product_uom_srch = [('name','=',i.product_name.uom_id.name)]
					    product_uom_ids = sock.execute(dbname, userid, pwd, 'product.uom', 'search', product_uom_srch)

				    if i.reason.id:
					
					    reason_srch = [('name', '=',i.reason.name)]
					    reason_ids = sock.execute(dbname, userid, pwd, 'adjustment.reason', 'search', reason_srch)
					    if not reason_ids :
						    reason_create = {
							    'name':i.reason.name,
							    'action':i.reason.action,
								    }
						    reason_ids = [sock.execute(dbname, userid, pwd, 'adjustment.reason', 'create', reason_create)]
				    total_amount_req = 0.0
				
				    if i.Batch.id:
					    total_amount_req = float(i.adj_stock)*float(i.Batch.st)

				    if i.company_id:
					    company_srch = [('name', '=',i.company_id.name)]
					    company_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', company_srch)
    #end
				    indent_branch= {'sam_no':i.sam_no,
							    'sam_date':i.sam_date,
							    'product_name':product_ids[0],
							    'generic_id':generic_id[0],
							    'reason':reason_ids[0],
							    'product_code':i.product_code,
							    'book_stock':i.book_stock,
							    'adj_stock':i.adj_stock,
							    'bal_stock':i.bal_stock,
							    'ammount':total_amount_req,
							    'notes':i.notes,
							    'category':i.category,
							    'batch_no':i.Batch.batch_no if i.Batch.id else '' ,
							    'batch_serial_no':i.serial_no.serial_no if i.serial_no.serial_no else '',
							    'location':i.company_id.name if i.company_id.name else '',
							    'product_uom':product_uom_ids[0] if product_uom_ids else '',
							    'source': company_ids[0] if i.company_id else False,
									       }
				    sock.execute(dbname, userid, pwd, 'critical.adjustment', 'create', indent_branch)

		return conn_flag					


stock_adjustment()


class res_indent(osv.osv):

	_inherit = 'res.indent'

	def offline_sync_res_indent(self,cr,uid,ids,context = None):
		if context is None: context = {}
		sync_result = True
		offline_sync = context.get('offline_sync') if context.get('offline_sync') else False
		form_id = offline_sync.get('form_id') if offline_sync and offline_sync.get('form_id') else False
		offline_sync_sync = offline_sync.get('sync_sequence') if offline_sync and offline_sync.get('sync_sequence') else False
		context.update({'offline_sync_sync':offline_sync_sync})
		if form_id:
			sync_result = self.sync_branch_order_confirm(cr,uid,[form_id],context=context)
		return sync_result


	def sync_branch_order_confirm(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		state_ids = False
		city_ids = False
		form_new_id = 0
		msg_flag=False
		conn_flag=False
		for brw in self.browse(cr,uid,ids):
			form_new_id = brw.id
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
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					offline_obj=self.pool.get('offline.sync')
					offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					if not offline_sync_sequence:
						offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':brw,'error_log':Err,})
					else:
						offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
						offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
				sock = xmlrpclib.ServerProxy(obj)
				if conn_flag == False:
					if brw.company_id:
						company_id_srch = [('name', '=',brw.company_id.name)]
						company_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', company_id_srch)

					branch_ids=0
					if brw.branch_name:
						branch_id_srch = [('name', '=',brw.branch_name.name)]
						branch_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', branch_id_srch)

					if brw.company_id.state_id:
						state_id_srch = [('name', '=',brw.company_id.state_id.name)]
						state_ids = sock.execute(dbname, userid, pwd, 'state.name', 'search', state_id_srch)



					vat_tin=''
					cst_tin=''
					if brw.customer_name:
						for cust in self.pool.get('res.customer').browse(cr,uid,[brw.customer_name.id]):
							vat_tin=cust.vat
							cst_tin=cust.cst_no

					indent_branch = {'origin':brw.order_id if brw.order_id else '',
							'company_id':company_ids[0] if company_ids else '',
							'contact_person':brw.contact_person_new.name if brw.contact_person_new.name else '',
							'date':brw.order_date if brw.order_date else False,
							'indent_type':brw.indent_type if brw.indent_type else '',
							'contact_no':brw.contact_no if brw.contact_no else '',
							'delivery_address':brw.delivery_address if brw.delivery_address else '',
							'customer_name':brw.customer_name.name if brw.customer_name.name else '',
							'dispatcher_state':'Unassigned',
							'customer_vat_tin':vat_tin,
							'customer_cst_no':cst_tin,
							'branch_name':branch_ids[0] if brw.branch_name else '',
							'form_branch_id':form_new_id
						
									   }
					indent_branch_id = sock.execute(dbname, userid, pwd, 'stock.picking', 'create', indent_branch)

					for line in brw.order_line:
						if line.product_uom:
							prod_uom = [('name', '=', line.product_uom.name)]
							uom = sock.execute(dbname, userid, pwd, 'product.uom', 'search', prod_uom)

						if line.product_id.uom_id.category_id:
							prod_uom_cat = [('name', '=', line.product_id.uom_id.category_id.name)]
							uom_cat = sock.execute(dbname, userid, pwd, 'product.uom.categ', 'search', prod_uom_cat)

						if line.product_id.uom_id:
							prod_uom_id = [('name', '=', line.product_id.uom_id.name)]
							uom_id = sock.execute(dbname, userid, pwd, 'product.uom', 'search', prod_uom_id)

						if line.product_id:
							prod_id = [('name', '=',line.product_id.name)] 
							product_id = sock.execute(dbname, userid, pwd, 'product.product', 'search', prod_id)

						if line.product_id.product_vertical:
							prod_vertical = [('name', '=',line.product_id.product_vertical.name)] 
							product_verticals = sock.execute(dbname, userid, pwd, 'product.vertical', 'search', prod_vertical)

						if line.product_id.categ_id:
							prod_categ = [('name', '=',line.product_id.categ_id.name)] 
							product_categs = sock.execute(dbname, userid, pwd, 'product.category', 'search', prod_categ)

						if line.product_category:
						    prod_cate = [('name', '=', line.product_category.name)]
						    prod_category = sock.execute(dbname, userid, pwd, 'product.category', 'search', prod_cate)
					
						if line.generic_id:
							prod_generic=[('name','=',line.generic_id.name)]
							prod_generic_id = sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', prod_generic)

						pick_line = {
						        'picking_id':indent_branch_id,
						        'product_id':product_id[0] if product_id else prod_id,
						        'product_uom':uom[0],
						        'product_category':prod_category[0],
						        'product_code':line.product_code,
						        'product_qty':line.product_uom_qty,
							    'indented_qty':line.product_uom_qty,
						        'delivery_rate':line.price_unit,
						        'amount':line.total,
									'generic_id':prod_generic_id[0],
						            }
						move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'create', pick_line)

						if line.notes_one2many:					
							for material_notes in line.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.name
								date=material_notes.comment_date
								comment=material_notes.comment

								branch_ids=0
								if material_notes.source:
									branch_id_srch = [('name', '=',material_notes.source.name)]
									branch_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', branch_id_srch)

								material_notes_line = {
										'indent_id':move_ids,
										'source':branch_ids[0] ,
										'comment_date':date,
										'comment':comment,
										'user_id':user_name,
										
										    }
								material_notes_ids= sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', material_notes_line)
								msg_flag=True	
								msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
									}
								msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',move_ids ,msg_unread)
					if brw.comment_line:	
						msg_flag=True					
						for notes in brw.comment_line:
							source_id=False
							if notes.indent_id:
								cm_srch = [('origin','=',notes.indent_id.order_id)]
								cm_id = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', cm_srch)
							if notes.source:
									source_srch = [('name','=',notes.source.name)]
									source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
						
							cm_ln = { 'remark_field':notes.comment,
									'source':source_id[0] if source_id else '',
								  'remark':cm_id[0],
								  'user':notes.user_id if notes.user_id else '',
								  'date':notes.comment_date,
								}
							notes_ids= sock.execute(dbname, userid, pwd, 'indent.remark', 'create', cm_ln)
					if msg_flag or msg_flag==True:
						msg_write = { 'msg_check':True,
							}
						msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write',indent_branch_id ,msg_write)

		return conn_flag

res_indent()

class receive_indent(osv.osv):
	_inherit = "receive.indent"

	def offline_sync_receive_indent(self,cr,uid,ids,context = None):
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


	def syn_generate_grn(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		warehouse_mismatch_id = ''
		last_delivery_flag=False
		msg_flag=False
		conn_flag = False
		for res in self.browse(cr,uid,ids):
			delivery_type_others= res.delivery_type_others
			if delivery_type_others == 'direct_delivery':
				for line in res.receive_indent_line:
					excess = line.excess
					short = line.short
					reject = line.reject
					document_qty = line.product_qty
					indented_qty = line.indented_quantity
					if document_qty > indented_qty or line.last_delivery:
							last_delivery_flag=True
		if last_delivery_flag:
			for res in self.browse(cr,uid,ids):		
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
								userid = ''
								log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
								obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
								sock_common = xmlrpclib.ServerProxy (log)
								try:
									userid = sock_common.login(dbname, username, pwd)
								except Exception as Err:
									offline_obj=self.pool.get('offline.sync')
									offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
									conn_flag = True
									if not offline_sync_sequence:
										offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'syn_generate_grn','error_log':Err,})
									else:
										offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
										offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
								sock = xmlrpclib.ServerProxy(obj)

								supplier_id=0
								supplier_id1=0
								company_id=0
								if res.company_id:
									company_srch = [('name','=',res.company_id.name)]
									company_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', company_srch)
								warehouse_mismatch = {
										'delivery_challan_no':res.delivery_challan_no,
										'delivery_type_others':res.delivery_type_others,
										'indent_date':res.indent_date,
										'document_date':res.document_date,
										'indent_no':res.indent_id.order_id,
										'transporter_name':res.transporter_name.transporter_name if res.transporter_name.transporter_name else '',
										'requester':company_id[0] if company_id else '',
										'grn_no':res.grn_no,
										'grn_date':res.grn_date,
										'supplier_name':res.supplier_name.name if res.supplier_name else '' ,
										'document_value':res.document_value,
										'delay_delivery':res.delay_delivery,
										'deliver_percent':res.deliver_percent,
										'labelling':res.labelling,		
										'leakage':res.leakage,					
										'certificate_quality':res.certificate_quality,
										'supplier_address':res.supplier_address,
										}
								warehouse_mismatch_id = sock.execute(dbname, userid, pwd, 'warehouse.mismatch.delivery', 'create', warehouse_mismatch)
								for line in res.receive_indent_line:
									if line.product_name:
										product_srch = [('name','=',line.product_name.name)]
										product_id_srch = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)

									if line.generic_id:
										generic_id_srch = [('name','=',line.generic_id.name)]
										generic_id = sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_id_srch)

									if line.product_uom:
										product_uom_srch = [('name','=',line.product_uom.name)]
										product_uom_ids = sock.execute(dbname, userid, pwd, 'product.uom', 'search', product_uom_srch)

									indent_line = {
										'indent_id':warehouse_mismatch_id,
										'product_code':line.product_code,
										'product_name':product_id_srch[0] if product_id_srch else '',
										'generic_id':generic_id[0] if generic_id else '',
										'product_uom':product_uom_ids[0] if product_uom_ids else '',
										'batch':line.batch.batch_no if line.batch else '',
										'product_qty':line.product_qty,
										'excess':excess,
										'short':short,
										'reject':reject,
										'manufacturing_date':line.manufacturing_date if line.manufacturing_date else False,
										'exp_date':line.batch.exp_date if line.batch.exp_date else False,
										'qty_received':line.qty_received,
										'indented_quantity':line.indented_quantity,
										'price_unit':line.price_unit,
										'subtotal':line.subtotal,
										'state':res.state,
											}
									create_indent_line = sock.execute(dbname, userid, pwd, 'warehouse.material.details', 'create', indent_line)
									if line.notes_one2many:
										for line_id in line.notes_one2many:
											source_ids=''
											msg_flag=True
											if line_id.source: #Source
												source_srch = [('name', '=',line_id.source.name)]
												source_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
																}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'warehouse.material.details', 'write',create_indent_line,msg_unread)
											material_notes = {
													'indent_id':create_indent_line,
													'user_id':line_id.user_id,
													'comment':line_id.comment,
													'comment_date':line_id.comment_date,
													'source':source_ids[0] if line_id.source else False,
													}

											create_material_notes = sock.execute(dbname, userid, pwd, 'warehouse.material.details.comment.line', 'create', material_notes)

								if res.comment_line:
									for notes1 in res.comment_line:
										 msg_flag=True
										 if notes1.source:
										                    source_srch = [('name','=',notes1.source.name)]
										                    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
										 cm_ln = { 'receive_indent_id':warehouse_mismatch_id,
										           'comment':notes1.comment,
										           'user_id1':notes1.user_id if notes1.user_id else '',
										           'comment_date':notes1.comment_date,
										           'source':source_id[0] if source_id else '',
										                    
										          }
										 notes_ids2= sock.execute(dbname, userid, pwd, 'receive.indent.comment.line', 'create', cm_ln)

								if msg_flag:
									msg_line = {
													'msg_check':True
												   }
									msg_ids= sock.execute(dbname, userid, pwd, 'warehouse.mismatch.delivery', 'write',warehouse_mismatch_id, msg_line)

		self.generate_grn_others(cr,uid,ids,context=context)
		return conn_flag


	def syn_generate_grn_stock_transfer(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		msg_flag=False
		msg_flag_branch=False
		conn_central_flag=False
		conn_disp_flag=False		
		for res in self.browse(cr,uid,ids):
			delivery_type_others= res.delivery_type_others
			if delivery_type_others in ('banned_st','excess_st','inter_branch_st'):
				count=0
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
					userid = ''
					log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
					obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
					sock_common = xmlrpclib.ServerProxy (log)
					try:
						userid = sock_common.login(dbname, username, pwd)
					except Exception as Err:
						offline_obj=self.pool.get('offline.sync')
						offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
						conn_central_flag = True
						if not offline_sync_sequence:
							offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_generate_grn_stock_transfer_central','error_log':Err,})
						else:
							offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
							offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_central_flag})
					sock = xmlrpclib.ServerProxy(obj)
					if conn_central_flag==False:					
					    stock_transfer_no_id=''
					    stock_transfer_no=res.stn_no.stock_transfer_no
					    if res.stn_no:
						    stock_transfer_no_srch = [('stock_transfer_no','=',stock_transfer_no)]
						    stock_transfer_no_id = sock.execute(dbname, userid, pwd, 'branch.stock.transfer', 'search', stock_transfer_no_srch)

					    flag_series=False
					    create_series=''
					    for receive_prod in res.receive_indent_line:
						    product_srch = [('name', '=',receive_prod.product_name.name)]
						    product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)

					    if receive_prod.generic_id:
						    generic_srch=[('name','=',receive_prod.generic_id.name)]
						    generic_ids=sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_srch)

						    if receive_prod.serial_line:
							    if not flag_series:
								    flag_series=True
								    product_series_main =  {
										    'test':stock_transfer_no_id[0],
									    }
								    create_series = sock.execute(dbname, userid, pwd, 'product.series.main', 'create', product_series_main)	
												
							    for receive_series in receive_prod.serial_line:
								    count = count + 1							
								    series_create = {
										    'sr_no':count,
										    #'line':stock_tran_prod_id ,
										    #'series_line':stock_tran_prod_id ,
										    'product_code':receive_series.product_code,
										    'product_name':product_ids[0],
										    'generic_id':generic_ids[0] if generic_ids else False,
										    #'product_category':ln.product_name.id,
										    'prod_uom':receive_series.product_uom.name,
										    'product_category':receive_prod.product_name.categ_id.name,
										    'batch_val':receive_series.batch.batch_no,
										    'quantity':receive_series.quantity,
										    'serial_no':receive_series.serial_name,
										    'active_id':receive_series.active_id,
										    'serial_check':receive_series.serial_check,
										    'series_line':create_series,
										    'reject':receive_series.reject_serial_check,
										    'short':receive_series.short,
										    'excess':receive_series.excess,
									    }
								    transporter_create_new = sock.execute(dbname, userid, pwd, 'product.series', 'create', series_create)
				
					    if stock_transfer_no_id:
						    intransit_state_update = {
									    'serial_check_prod':flag_series,
									    'grn_no':res.grn_no,
									    'grn_date':res.grn_date,
									    'state':'done',
									    }
						    intransit_state_update_id = sock.execute(dbname, userid, pwd, 'branch.stock.transfer', 'write', stock_transfer_no_id, intransit_state_update)

						    for line in res.receive_indent_line:
							    product_name_srch = [('name','=',line.product_name.name)]
							    product_name_id = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_name_srch)
							    product_transfer_srch = [('product_name','=',product_name_id[0]),('prod_id','=',stock_transfer_no_id[0])]
							    product_transfer_id = sock.execute(dbname, userid, pwd, 'branch.product.transfer', 'search', product_transfer_srch)
							    if line.notes_one2many:
								    for line_id in line.notes_one2many:
									    source_ids=''
									    if line_id.source: #Source
										    source_srch = [('name', '=',line_id.source.name)]
										    source_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
									    notes_srch = [('user_id','=',line_id.user_id),('indent_id','=',product_transfer_id[0]),('comment','=',line_id.comment),('comment_date','=',line_id.comment_date),('source','=',source_ids[0])]
									    notes_id = sock.execute(dbname, userid, pwd, 'branch.product.transfer.comment.line', 'search', notes_srch)
									    if notes_id:
										    print 'l'
									    else:
										    msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
															    }
										    msg_unread_ids= sock.execute(dbname, userid, pwd, 'branch.product.transfer', 'write',product_transfer_id ,msg_unread)
										    msg_flag=True
										    material_notes = {
												    'indent_id':product_transfer_id[0],
												    'user_id':line_id.user_id,
												    'comment':line_id.comment,
												    'comment_date':line_id.comment_date,
												    'source':source_ids[0] if line_id.source else False,
												    }

										    create_material_notes = sock.execute(dbname, userid, pwd, 'branch.product.transfer.comment.line', 'create', material_notes)

						    if res.comment_line:
							    for remark_line in res.comment_line:

								    cmt_srch = [('name','=',remark_line.comment),('date','=',remark_line.comment_date),('user_name','=',remark_line.user_id),('branch_stock_transfer_id','=',stock_transfer_no_id[0])]
								    cmt_id = sock.execute(dbname, userid, pwd, 'branch.stock.transfer.remarks', 'search', cmt_srch)
								    if cmt_id != []:
									    for test in cmt_id:
										    add_notes1 = {           
															    #'branch_stock_transfer_id':stock_transfer_no_id[0],
															    'user_name':remark_line.user_id if remark_line.user_id else '',
															    'date':remark_line.comment_date if remark_line.comment_date else False,
															    'name':remark_line.comment if remark_line.comment else '',
															    }
										    add_notes_id = sock.execute(dbname, userid, pwd, 'branch.stock.transfer.remarks', 'write', test, add_notes1)
								    else:
									    msg_flag=True
									    add_notes = {           
															    'branch_stock_transfer_id':stock_transfer_no_id[0],
															    'user_name':remark_line.user_id if remark_line.user_id else '',
															    'date':remark_line.comment_date if remark_line.comment_date else False,
															    'name':remark_line.comment if remark_line.comment else '',
												    }
									    add_notes_id = sock.execute(dbname, userid, pwd, 'branch.stock.transfer.remarks', 'create', add_notes)

						    if msg_flag:
							    msg_line = {
											    'msg_check':True
										       }
							    msg_ids= sock.execute(dbname, userid, pwd, 'branch.stock.transfer', 'write', stock_transfer_no_id, msg_line)

				vpn_ip_addr = res.source_company.vpn_ip_address
				port = res.source_company.port
				dbname = res.source_company.dbname
				pwd = res.source_company.pwd
				user_name = str(res.source_company.user_name.login)
				username = user_name #the user
				pwd = pwd    #the password of the user
				dbname = dbname
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					offline_obj=self.pool.get('offline.sync')
					offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_disp_flag = True
					if not offline_sync_sequence:
						offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.source_company.id,'srch_condn':False,'form_id':res,'func_model':'sync_generate_grn_stock_transfer_branch','error_log':Err,})
					else:
						offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
						offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_disp_flag})
				sock = xmlrpclib.ServerProxy(obj)
				if conn_disp_flag == False:
					stock_transfer_no=res.stn_no.stock_transfer_no
					origin_srch = [('stock_transfer_no', '=',stock_transfer_no)]
					origin_ids = sock.execute(dbname, userid, pwd, 'stock.transfer', 'search', origin_srch)
					if origin_ids:
							pick_line = {
								'state':'done',
								'grn_no':res.grn_no,
								'grn_date':res.grn_date,
							   }
							move_ids= sock.execute(dbname, userid, pwd, 'stock.transfer', 'write',origin_ids, pick_line)
							for receive_prod in res.receive_indent_line:
								if receive_prod.serial_line:
									for receive_series in receive_prod.serial_line:

										if receive_series.reject_serial_check:
											series_srch = [('serial_name', '=',receive_series.serial_name)]
											series_ids = sock.execute(dbname, userid, pwd, 'transfer.series', 'search', series_srch)									
											series_create = {
														'reject':receive_series.reject_serial_check,
														'short':receive_series.short
												}
											transporter_create_new = sock.execute(dbname, userid, pwd, 'transfer.series', 'write',series_ids, series_create)
							for line in res.receive_indent_line:
								product_name_srch = [('name','=',line.product_name.name)]
								product_name_id = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_name_srch)
								product_transfer_srch = [('product_name','=',product_name_id[0]),('prod_id','=',origin_ids[0])]
								product_transfer_id = sock.execute(dbname, userid, pwd, 'product.transfer', 'search', product_transfer_srch)

								if line.notes_one2many:
									for line_id in line.notes_one2many:
										source_ids=''
										if line_id.source: #Source
											source_srch = [('name', '=',line_id.source.name)]
											source_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
										notes_srch = [('user_id','=',line_id.user_id),('indent_id','=',product_transfer_id[0]),('comment','=',line_id.comment),('comment_date','=',line_id.comment_date),('source','=',source_ids[0])]
										notes_id = sock.execute(dbname, userid, pwd, 'product.transfer.comment.line', 'search', notes_srch)
										if notes_id:
											print 'l'
										else:
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
																}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'product.transfer', 'write',product_transfer_id ,msg_unread)
											msg_flag_branch=True
											material_notes = {
													'indent_id':product_transfer_id[0],
													'user_id':line_id.user_id,
													'comment':line_id.comment,
													'comment_date':line_id.comment_date,
													'source':source_ids[0] if line_id.source else False,
													}

											create_material_notes = sock.execute(dbname, userid, pwd, 'product.transfer.comment.line', 'create', material_notes)

							if res.comment_line:
								for notes_line in res.comment_line:
										if notes_line.source:
										                source_srch = [('name','=',notes_line.source.name)]
										                source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
										remark_srch = [('name','=',notes_line.comment),('user_name','=',notes_line.user_id)]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'search', remark_srch)			
										if remark_srch_id:					
											notes_line = {
												                    'user_name':notes_line.user_id if notes_line.user_id else '',
												                    'source':source_id[0] if source_id else '',
												                    'date':notes_line.comment_date,
												                    'name':notes_line.comment,
												                   }
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'write', remark_srch_id[0], notes_line)
										if not remark_srch_id:
											msg_flag_branch=True
											create_notes_line = {
														'stock_transfer_id':origin_ids[0],
												                    'user_name':notes_line.user_id if notes_line.user_id else '',
												                    'source':source_id[0] if source_id else '',
												                    'date':notes_line.comment_date,
												                    'name':notes_line.comment,
												                   }
											notes_line_ids = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'create', create_notes_line) 

							if msg_flag_branch:
								msg_line = {
												'msg_check':True
											   }
								msg_ids= sock.execute(dbname, userid, pwd, 'stock.transfer', 'write', origin_ids, msg_line)



		return True


	def generate_grn_others(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		msg_flag = False
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
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'generate_grn_others','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})			
			sock = xmlrpclib.ServerProxy(obj)
			for rec in self.browse(cr,uid,ids):
				delivery_type_others= rec.delivery_type_others
				if delivery_type_others == 'direct_delivery':	
					if conn_flag == False:				
						origin_srch = [('origin', '=',rec.indent_id.order_id,),('id','=',rec.indent_id.ci_sync_id)]
						origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
						if origin_ids:
							for ln in rec.receive_indent_line:
								product_srch = [('name', '=',ln.product_name.name)]
								product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
								ln_srch = [('product_id', '=',product_ids[0]),('product_code','=',ln.product_code),('origin','=',ln.origin),('picking_id','=',origin_ids[0])]
								ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
								if ln_ids:
									pick_line = {

											'state':'done'
										   }

									move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_line)
									if ln.notes_one2many:
										for material_notes in ln.notes_one2many:
											user_name=material_notes.user_id
											source=material_notes.source.id
											comment=material_notes.comment
											comment_date=material_notes.comment_date
											source_id=0
											if material_notes.source:
												source_srch = [('name','=',material_notes.source.name)]
												source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

											remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
											remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
											if remark_srch_id:
											   for test in remark_srch_id:
												notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
											if not remark_srch_id:
												msg_flag=True
												msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
																	}
												msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids ,msg_unread)
											notes_line = {
														                'indent_id':ln_ids[0],
														                'user_id':user_name if user_name else '',
																		'source':source_id[0] if source_id else '',
														                'comment_date':comment_date,
														                'comment':comment,
														               }
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
							if rec.comment_line:
								for notes in rec.comment_line:
									if notes.source:
								                    source_srch = [('name','=',notes.source.name)]
								                    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('remark_field','=',notes.comment),('user','=',notes.user_id),('source','=',source_id[0]),('date','=',notes.comment_date),('remark','=',origin_ids[0])]#jjj
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)

									if remark_srch_id:
										for test in remark_srch_id:
											print 'lllllllllllllllll'
											#notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'unlink', test)
									if not remark_srch_id:
										msg_flag=True
									create_notes_line = {
																'remark':origin_ids[0] if origin_ids else '',
										                        'user':notes.user_id if notes.user_id else '',
										                        'source':source_id[0] if notes.source else '',
										                        'date':notes.comment_date,
										                        'remark_field':notes.comment,
										                       }
									notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)

							if msg_flag:
								msg_line = {
												'msg_check':True
											   }
								msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)

		return conn_flag


	def syn_generate_grn_indent(self,cr,uid,ids,context=None):
		if context is None : context = {} 
		for res in self.browse(cr,uid,ids):
			for line in res.receive_indent_line:
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
					userid = ''
					log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
					obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
					sock_common = xmlrpclib.ServerProxy (log)
					try:
						userid = sock_common.login(dbname, username, pwd)
					except Exception:
						raise osv.except_osv(('Alert!'),('No Connection.'))
					sock = xmlrpclib.ServerProxy(obj)

	def sync_generate_grn_others_1(self,cr,uid,ids,context=None):
		if context is None: context = {}
		msg_flag=False
		conn_flag=False
		temp_id = []		
		for rec in self.browse(cr,uid,ids):
			indent_id=rec.indent_id.id
			for track in rec.receive_indent_line:
				name = self.pool.get('res.company').search(cr,uid,[('name','=',track.source_company.name)])
				for branch_id in self.pool.get('res.company').browse(cr,uid,name):
					vpn_ip_addr = branch_id.vpn_ip_address
					port = branch_id.port
					dbname = branch_id.dbname
					pwd = branch_id.pwd
					user_name = str(branch_id.user_name.login)
					username = user_name #the user
					pwd = pwd    #the password of the user
					dbname = dbname
					userid = ''
					log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
					obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
					sock_common = xmlrpclib.ServerProxy (log)
					try:
						userid = sock_common.login(dbname, username, pwd)
					except Exception as Err:
						offline_obj=self.pool.get('offline.sync')
						offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
						conn_flag = True
						if not offline_sync_sequence:
							offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':name[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_generate_grn_others_1','error_log':Err,})
						else:
							offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
							offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
					sock = xmlrpclib.ServerProxy(obj)
					if conn_flag==False:
						print 'cccccccccccccccccccccccccccc',track.ci_sync_id,dbname
						origin_srch = [('id', '=',track.indent_order_id)]
						origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
						if origin_ids:
							product_srch = [('name', '=',track.product_name.name)]
							product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							if not product_ids:
								raise osv.except_osv(('Alert!'),('Product not present at destination'))
							notes_srch = [('product_id', '=',product_ids[0]),('product_code','=',track.product_code),('origin','=',track.origin),('picking_id','=',origin_ids[0])]
							notes_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', notes_srch)
							#ln_srch = [('origin','=',track.origin)]
							ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', notes_srch)
							fact_line={
									'state':'done'
								}	
							fact_ids=sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids[0], fact_line)
							if track.notes_one2many:
								for material_notes in track.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									source_id=0
									if material_notes.source:
										source_srch = [('name','=',material_notes.source.name)]
										source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

									remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',ln_ids[0])]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
									if remark_srch_id:
										for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
									if not remark_srch_id:
										msg_flag=True
										msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
															}
										msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',notes_ids ,msg_unread)

									notes_line = {
														'indent_id':notes_ids[0],
														'user_id':user_name if user_name else '',
														'source':source_id[0] if source_id else '',
														'comment_date':comment_date,
														'comment':comment,
											}
									notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
						if rec.comment_line:
							for notes in rec.comment_line:
								if notes.source:
									source_srch = [('name','=',notes.source.name)]
									source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
									print "TTTTTTTTTTTTTTTTTTTTTTTTTYYYYYYYYYYYYYYYYYYYYYYYYYYY",notes.comment,notes.user_id,source_id[0],origin_ids
									remark_srch = [('remark_field','=',notes.comment),('user','=',notes.user_id),('source','=',source_id[0]),('date','=',notes.comment_date),('remark','=',origin_ids[0])]#jjj
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
									if remark_srch_id:
										for test in remark_srch_id:
											notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'unlink', test)
									if not remark_srch_id:
										msg_flag=True
									create_notes_line = {
														'remark':origin_ids[0] if origin_ids else '',
														'user':notes.user_id if notes.user_id else '',
														'source':source_id[0] if notes.source else '',
														'date':notes.comment_date,
														'remark_field':notes.comment,
										}
									notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)
							if msg_flag:
								msg_line = {
												'msg_check':True
									}
								msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)

		return conn_flag




receive_indent()


