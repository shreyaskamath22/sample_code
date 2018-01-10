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

	def sync_prepare_packlist_branch(self,cr,uid,ids,context=None):
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag=False
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
				conn_flag = True
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

		return conn_flag


	def sync_prepare_packlist_central(self,cr,uid,ids,context=None):
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag_1=False
		for res in self.browse(cr,uid,ids):
			ci_sync_id = res.ci_sync_id
			form_branch_id = res.form_branch_id
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
				conn_flag_1 = True
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
		return conn_flag_1

	def sync_ready_to_dispatch_branch(self,cr,uid,ids,context=None):
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
				conn_flag = True
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

		return conn_flag

	def sync_ready_to_dispatch_central(self,cr,uid,ids,context=None):
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag_1=False
		for res in self.browse(cr,uid,ids):
			ci_sync_id = res.ci_sync_id
			form_branch_id = res.form_branch_id
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
				conn_flag_1 = True
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
				
			return conn_flag_1


stock_transfer()

class receive_indent(osv.osv):
	
	_inherit = 'receive.indent'

	def indent_sync_central(self, cr, uid, ids, context=None):
		if context is None : context = {}
		val_prod_series_srh1 = ''
		ci_sync_id = ''
		conn_central_flag=False
		conn_dispatcher_flag=False		
		for i in self.browse(cr, uid, ids):
			msg_flag=False
			msg_flag_branch=False
			msg_flag_stock=False
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
					conn_central_flag = True
				sock = xmlrpclib.ServerProxy(obj)
				if conn_central_flag==False:
				    ln_ids = ''
				    count = 0
				    origin_srch = [('id','=',i.ci_sync_id),('origin', '=', i.indent_no)]
				    origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
				    if origin_ids:
					    for ln in i.receive_indent_line:
						    create_series11 = 0
						    if ln.product_name.type_product == 'track_equipment':
							    button_attrs =  {
												    'test_state':True
											    }
											
							    final_val = sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids[0], button_attrs)
							    prod_series_srh = [('test', '=',origin_ids[0])]
							    val_prod_series_srh = sock.execute(dbname, useid, pwd, 'product.series.main', 'search', prod_series_srh)
							    if val_prod_series_srh:
									    create_series11 = val_prod_series_srh[0]
							    if val_prod_series_srh == []:
									    product_series_main =  {
										    'test':origin_ids[0],
															    }
									    val_prod_series_srh1 = sock.execute(dbname, userid, pwd, 'product.series.main', 'create', product_series_main)
									    create_series11 = val_prod_series_srh1
							    if ln.serial_line:
								    product_srch = [('name', '=',ln.product_name.name)]
								    product_ids = sock.execute(dbname, useid, pwd, 'product.product', 'search', product_srch)	
							    if ln.generic_id:
								    generic_srch=[('name','=',ln.generic_id.name)]
								    generic_ids=sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_srch)						
								    for serials in ln.serial_line:
									    count = count + 1
									    series_create = {
													    'sr_no':count,
													    'product_code':ln.product_code,
													    'product_name':product_ids[0],
													    'generic_id' :generic_ids[0] if generic_ids else False,
													    'prod_uom':ln.product_name.local_uom_id.name,
													    'batch_val':ln.batch.batch_no,
													    'quantity':serials.quantity,
													    'serial_no':serials.serial_name,
													    'product_category':serials.product_name.categ_id.name,
													    'active_id':serials.active_id,
													    'serial_check':serials.serial_check,
													    'series_line':create_series11,
													    'reject':serials.reject_serial_check,
													    'short':serials.short,
													    'excess':serials.excess,
													    }
									    transporter_create_new = sock.execute(dbname, userid, pwd, 'product.series', 'create', series_create)
				    product_uom_qty = 0
				    for p in i.receive_indent_line:
							    product_srch = [('name', '=',p.product_name.name)]
							    product_ids11 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)	
							    stock_move_srh = [('product_id', '=',product_ids11[0]),('picking_id','=',origin_ids[0])]
							    stock_val = sock.execute(dbname, userid, pwd, 'stock.move', 'search', stock_move_srh)
							    if stock_val:
								    pick_line = {
											    'state':'done'
											    }
								    move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', stock_val[0], pick_line)
								    if p.notes_one2many:
									    for material_notes in p.notes_one2many:
										    user_name=material_notes.user_id
										    source=material_notes.source.id
										    comment=material_notes.comment
										    comment_date=material_notes.comment_date
										    source_id=0
										    if material_notes.source:
											    source_srch = [('name','=',material_notes.source.name)]
											    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										    remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',stock_val[0])]
										    remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
										    if remark_srch_id:
										       for test in remark_srch_id:
											    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
										    if not remark_srch_id:
											    msg_flag=True
											    msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												    }
											    msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',stock_val,msg_unread)									

										    notes_line = {
												                        'indent_id':stock_val[0],
												                        'user_id':user_name if user_name else '',
																	    'source':source_id[0] if source_id else '',
												                        'comment_date':comment_date,
												                        'comment':comment,
												                       }
										    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)

				    if i.comment_line:						
					    for notes_line in i.comment_line:
						    if notes_line.source:
							    source_srch = [('name','=',notes_line.source.name)]
							    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
							    remark_srch = [('remark_field','=',notes_line.comment),('user','=',notes_line.user_id),('remark','=',origin_ids[0]),('date','=',notes_line.comment_date),('source','=',source_id[0])]
							    remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)	
							    if remark_srch_id:
								    for k in remark_srch_id:					
									    notes_line = {
												    'user':notes_line.user_id if notes_line.user_id else '',
												    'source':source_id[0] if source_id else '',
												    'date':notes_line.comment_date,
												    'remark_field':notes_line.comment,
												     }
									    notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', k , notes_line)

							    else:
									    msg_flag=True
									    create_notes_line = {
														    'remark':origin_ids[0],
														    'user':notes_line.user_id if notes_line.user_id else '',
														    'source':source_id[0] if source_id else '',
														    'date':notes_line.comment_date,
														    'remark_field':notes_line.comment,
														    }
									    notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)

				    if msg_flag:
						    msg_line = {
											    'msg_check':True
										       }
						    msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)

		return conn_central_flag

	def indent_sync_branch(self, cr, uid, ids, context=None):
		if context is None : context = {}
		val_prod_series_srh1 = ''
		ci_sync_id = ''
		conn_central_flag=False
		conn_dispatcher_flag=False
		for i in self.browse(cr, uid, ids):
			msg_flag=False
			msg_flag_branch=False
			msg_flag_stock=False
			ci_sync_id = i.ci_sync_id
			branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])	
			stock_val=''			
			vpn_ip_addr = i.source_company.vpn_ip_address
			port = i.source_company.port
			dbname = i.source_company.dbname
			pwd = i.source_company.pwd
			user_name = str(i.source_company.user_name.login)
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
				conn_dispatcher_flag = True
			sock = xmlrpclib.ServerProxy(obj)
			if conn_dispatcher_flag==False:
			    origin_srch_qq = [('id', '=',i.stock_id),('origin', '=',i.indent_no)]
			    origin_ids_qq = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch_qq)
			    product_uom_qty = 0
			    for p in i.receive_indent_line:
				    product_srch = [('name', '=',p.product_name.name)]
				    product_ids11 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)	
				    stock_move_srh = [('product_id', '=',product_ids11[0]),('picking_id','=',origin_ids_qq[0])] 
				    stock_val = sock.execute(dbname, userid, pwd, 'stock.move', 'search', stock_move_srh)
				    if stock_val:
				          pick_value = {
							    'state':'done'
							    }
				          move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', stock_val[0], pick_value)	
				          if p.notes_one2many:
							    for material_notes in p.notes_one2many:
										    user_name=material_notes.user_id
										    source=material_notes.source.id
										    comment=material_notes.comment
										    comment_date=material_notes.comment_date
										    source_id=0
										    if material_notes.source:
											    source_srch = [('name','=',material_notes.source.name)]
											    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

										    remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',stock_val[0])]
										    remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
										    if remark_srch_id:
										       for test in remark_srch_id:
											    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)

										    if not remark_srch_id:
											    msg_flag_branch=True
											    msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												    }
											    msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',stock_val,msg_unread)

										    notes_line = {
												                        'indent_id':stock_val[0],
												                        'user_id':user_name if user_name else '',
																	    'source':source_id[0] if source_id else '',
												                        'comment_date':comment_date,
												                        'comment':comment,
												                       }
										    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
			    if i.comment_line:
				    for notes_line in i.comment_line:
					    if notes_line.source:
						    source_srch = [('name','=',notes_line.source.name)]
						    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
					    remark_srch = [('remark','=',origin_ids_qq),('remark_field','=',notes_line.comment),('user','=',notes_line.user_id),('date','=',notes_line.comment_date),('source','=',source_id[0])]
					    remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)	
					    if remark_srch_id:
						    for k in remark_srch_id:					
							    notes_line = {
										    'user':notes_line.user_id if notes_line.user_id else '',
										    'source':source_id[0] if source_id else '',
										    'date':notes_line.comment_date,
										    'remark_field':notes_line.comment,
										      }
							    notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', k , notes_line)

					    else:
						    msg_flag_branch
						    create_notes_line = {
											    'remark':origin_ids_qq[0],
											    'user':notes_line.user_id if notes_line.user_id else '',
											    'source':source_id[0] if source_id else '',
											    'date':notes_line.comment_date,
											    'remark_field':notes_line.comment,
											    }
						    notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)

			    if msg_flag_branch:
				    msg_line = {
											    'msg_check':True
										       }
				    msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids_qq, msg_line)	
    #sync for stock transfer of the Dispatcher
			    o_srch = [('stock_transfer_no', '=',i.order_number),('origin','=',i.indent_no)]
			    origin_stock_transfer = sock.execute(dbname, userid, pwd, 'stock.transfer', 'search', o_srch)
			    if origin_stock_transfer:
				    pick_line = {
								    'state':'done'
						      	 			}
				    move_ids= sock.execute(dbname, userid, pwd, 'stock.transfer', 'write',origin_stock_transfer[0], pick_line)
			    if i.comment_line:
				    for notes_line in i.comment_line:
					    if notes_line.source:
						    source_srch = [('name','=',notes_line.source.name)]
					    remark_srch = [('name','=',notes_line.comment),('user_name','=',notes_line.user_id),('stock_transfer_id','=',origin_stock_transfer[0]),('date','=',notes_line.comment_date)]
					    remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'search', remark_srch)			
								
					    if remark_srch_id:
						    for variable in remark_srch_id:	
							    notes_line = {
										    'user_name':notes_line.user_id if notes_line.user_id else '',
										    'source':source_id[0] if source_id else '',
										    'date':notes_line.comment_date,
										    'name':notes_line.comment,
										    }
							    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'write', variable, notes_line)
					    else:
							    msg_flag_stock=True
							    create_notes_line = {
												    'stock_transfer_id':origin_stock_transfer[0],
												    'user_name':notes_line.user_id if notes_line.user_id else '',
												    'source':source_id[0] if source_id else '',
												    'date':notes_line.comment_date,
												    'name':notes_line.comment,
										                           }
							    notes_line_ids = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'create', create_notes_line)

			    if origin_stock_transfer:
				    for ln in i.receive_indent_line:
					    for serials in ln.serial_line:
						    if serials.reject_serial_check or serials.short:
							    reject_serial_check = serials.reject_serial_check
							    search_val = [('serial_no', '=',serials.serial_name)]
							    search_val_prod = sock.execute(dbname, userid, pwd, 'product.series', 'search', search_val)	
							    if search_val_prod:
								    search_2 = [('serial_no', '=',search_val_prod[0])]
								    search_val22 = sock.execute(dbname, userid, pwd, 'transfer.series', 'search', search_2)
								    if search_val22:
									    reject_serial_check_val = {'reject_serial_check':serials.reject_serial_check,'short':serials.short}
									    create_series = sock.execute(dbname, userid, pwd, 'transfer.series', 'write',search_val22[0], reject_serial_check_val)
					    product_srch = [('name', '=',ln.product_name.name)]
					    product_ids11 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
					    rec_search = [('product_name', '=',product_ids11[0]),('prod_id','=',origin_stock_transfer[0])]
					    rec_search_val = sock.execute(dbname, userid, pwd, 'product.transfer', 'search', rec_search)
					    if rec_search_val:
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

									    remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',rec_search_val[0])]
									    remark_srch_id = sock.execute(dbname, userid, pwd, 'product.transfer.comment.line', 'search', remark_srch)
									    if remark_srch_id:
									       for test in remark_srch_id:
										    notes_line_id = sock.execute(dbname, userid, pwd, 'product.transfer.comment.line', 'unlink', test)

									    if not remark_srch_id:
											    msg_flag_stock=True
											    msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												    }
											    msg_unread_ids= sock.execute(dbname, userid, pwd, 'product.transfer', 'write',rec_search_val,msg_unread)

									    notes_line = {
										                            'indent_id':rec_search_val[0],
										                            'user_id':user_name if user_name else '',
																    'source':source_id[0] if source_id else '',
										                            'comment_date':comment_date,
										                            'comment':comment,
										                           }
									    notes_line_id = sock.execute(dbname, userid, pwd, 'product.transfer.comment.line', 'create', notes_line)

			    if msg_flag_stock:
				    msg_line = {
											    'msg_check':True
										       }
				    msg_ids= sock.execute(dbname, userid, pwd, 'stock.transfer', 'write',origin_stock_transfer, msg_line)

		return conn_dispatcher_flag


	def sync_generate_grn_stock_transfer_central(self,cr,uid,ids,context=None):
		msg_flag=False
		msg_flag_branch=False
		conn_central_flag=False
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

		return conn_central_flag

	def sync_generate_grn_stock_transfer_branch(self,cr,uid,ids,context=None):
		msg_flag=False
		msg_flag_branch=False
		conn_disp_flag=False
		for res in self.browse(cr,uid,ids):
			delivery_type_others= res.delivery_type_others
			if delivery_type_others in ('banned_st','excess_st','inter_branch_st'):
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
											source_ids = sock.execute(dbname, useid, pwd, 'res.company', 'search', source_srch)
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

		return conn_disp_flag

receive_indent()


class stock_partial_picking(osv.osv):

	_inherit = 'stock.partial.picking' 

	def sync_central_dept_central(self,cr,uid,ids,context=None):
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag_1 = False
		search = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
		for branch_id in self.pool.get('res.company').browse(cr,uid,search):
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
			    conn_flag_1 = True
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag_1 == False:
					date_new=False
					for res in self.browse(cr,uid,ids):
					    picking_id = res.picking_id.id
					    for line in res.move_ids:
							job_check = line.job_assign_check
							if job_check == True:
							   pick = self.pool.get('stock.move').write(cr,uid,line.move_id.id,{'check_job':job_check,
								                                                                  'dispatcher':res.warehouse.name})
					    if pick:
						    srch_pick_ids=0
						    pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',picking_id)])
						    for pick_brw in self.pool.get('stock.picking').browse(cr,uid,pick_srch):
						        ci_sync_id = pick_brw.ci_sync_id
						        date_new = pick_brw.exp_final_delivery_dt
					    for ln in res.move_ids:
						        origin_srch = [('id','=',ci_sync_id),('origin', '=',res.origin)]
						        origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
						        if origin_ids:
													pick_id = ''
							  				  		if ln.job_assign_check == True :
							  				  			product_srch = [('name', '=',ln.product_id.name)]
							  				  			product_ids2 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
							  				  			ln_srch = [('picking_id','=',origin_ids[0]),('product_id', '=',product_ids2[0])]
							  				  			ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
							  				  			date_value = {'exp_final_delivery_dt':date_new}
							  				  			pick_id11 = sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids[0], date_value) 
							  				  			if ln_ids:
															for test in ln_ids:
							  				  					pick_ln = {
												            'state':'view_order'
												              }
																pick_id = sock.execute(dbname, userid, pwd, 'stock.move', 'write', test, pick_ln)
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

							  				  		if msg_flag or msg_flag==True:
							  				  			msg_write = { 'msg_check':True,
										                }
							  				  			msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write',origin_ids[0],msg_write)

					    for notes in res.picking_note_line:
					    	origin_srch = [('id','=',ci_sync_id),('origin', '=',res.origin)]
					    	origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
					    	if notes.source:
					    		source_srch = [('name','=',notes.source.name)]
					    		source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
					    	remark_srch = [('remark','=',origin_ids[0]),('remark_field','=',notes.remark_field),('user','=',notes.user),('source','=',source_id),('date','=',notes.date)]
					    	remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
					    	if remark_srch_id:
					    		for p in remark_srch_id:
					    			central_in_write = {'remark_field':notes.remark_field,
						                      		'state':notes.state,
						                      		'user':notes.user if notes.user else '',
						                      		'date':notes.date,
						                      		'source':source_id[0] if source_id else '',
							  				  					}
					    			notes_ids= sock.execute(dbname, userid, pwd, 'indent.remark', 'write', p,central_in_write)
					    	else:
					    		msg_flag=True
					    		central_in_create = { 'remark_field':notes.remark_field,
								                  'state':notes.state,
								                  'remark':origin_ids[0],
								                  'user':notes.user if notes.user else '',
								                  'date':notes.date,
								                  'source':source_id[0] if source_id else '',
								  				  			}
					    		notes_ids= sock.execute(dbname, userid, pwd, 'indent.remark', 'create', central_in_create)

					    		if msg_flag or msg_flag==True:
					    			msg_write = { 'msg_check':True,
					    						}
					    			msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write',origin_ids[0],msg_write)

		return conn_flag_1

	def sync_central_dept_branch(self,cr,uid,ids,context=None):
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag = False
		for i in self.browse(cr,uid,ids):
			search_branch = self.pool.get('res.company').search(cr,uid,[('id','=',i.company_id1.id)])
			for branch_id1 in self.pool.get('res.company').browse(cr,uid,search_branch):
				vpn_ip_addr = branch_id1.vpn_ip_address
				port = branch_id1.port
				dbname = branch_id1.dbname
				pwd = branch_id1.pwd
				user_name = str(branch_id1.user_name.login)
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
					conn_flag = True
				sock = xmlrpclib.ServerProxy(obj)
				if conn_flag == False:
					date_new=False
					for res in self.browse(cr,uid,ids):
						picking_id = res.picking_id.id
						for line in res.move_ids:
							job_check = line.job_assign_check
							if job_check == True:
								pick = self.pool.get('stock.move').write(cr,uid,line.move_id.id,{'check_job':job_check,
									                                                          'dispatcher':res.warehouse.name})
						if pick:
							pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',picking_id)])
							for pick_brw in self.pool.get('stock.picking').browse(cr,uid,pick_srch):
								form_branch_id = pick_brw.form_branch_id
								date_new = pick_brw.exp_final_delivery_dt
						for ln in res.move_ids:
							origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
							origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
							if origin_ids:
									  				  search = []                
									  				  pick_id = ''
									  				  if ln.job_assign_check == True :
															product_srch = [('name', '=',ln.product_id.name)]
															product_ids2 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
															ln_srch = [('line_id','=',origin_ids[0]),('product_id', '=',product_ids2[0])]
															ln_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', ln_srch)
															date_value = {'exp_final_delivery_dt':date_new}
															pick_id11 = sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids[0], date_value)
															if ln_ids:
																for test in ln_ids:
																	pick_ln = {
																				'state':'view_order'
																			   }
																	pick_id = sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', test, pick_ln)
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
																		remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
																		if remark_srch_id:
																		   for test in remark_srch_id:
																			notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)
																		if not remark_srch_id:
																			msg_flag_branch=True
																		msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
																				}
																		msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',ln_ids ,msg_unread)
																		notes_line = {
																									'indent_id':ln_ids[0],
																									'user_id':user_name if user_name else '',
																									'source':source_id[0] if source_id else '',
																									'comment_date':comment_date,
																									'comment':comment,
																								   }
																		notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)

							if msg_flag_branch or msg_flag_branch==True:
									msg_line = {
									        'msg_check':True 
									       }
									msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)

						for notes in i.picking_note_line: 
							origin_srch = [('id','=',form_branch_id),('order_id', '=',i.origin)]
							origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
							if notes.source:
								source_srch = [('name','=',notes.source.name)]
								source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

							remark_srch = [('comment','=',notes.remark_field),('user_id','=',notes.user),('source','=',source_id),('comment_date','=',notes.date),('indent_id','=',origin_ids)]
							remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)

							if remark_srch_id:
								result = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'unlink', remark_srch_id[0])
							if not remark_srch_id:
								msg_flag_branch=True
							notes_line = {
											'indent_id':origin_ids[0],
											'user_id':notes.user if notes.user else '',
											'source':source_id[0] if source_id else '',
											'comment_date':notes.date,
											'comment':notes.remark_field,
										}
							notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)

							if msg_flag_branch or msg_flag_branch==True:
								msg_line = {
									        'msg_check':True 
									       }
								msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)
		                        
		return conn_flag

	def sync_request_central_dept_central(self,cr,uid,ids,context=None):
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag = False
		search_central = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
		for branch_id in self.pool.get('res.company').browse(cr,uid,search_central):
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
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				conn_flag = True
			sock = xmlrpclib.ServerProxy(obj)
			if not conn_flag:
				for res in self.browse(cr,uid,ids):
					picking_id = res.picking_id.id
					for line in res.move_ids:
						job_check = line.job_assign_check
						if job_check == True:
							 pick = self.pool.get('stock.move').write(cr,uid,line.move_id.id,{
							'check_job':job_check,
							'state':'done',
							'dispatcher':res.warehouse.name})
					if pick:
							pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',picking_id)])
							for pick_brw in self.pool.get('stock.picking').browse(cr,uid,pick_srch):
								ci_sync_id = pick_brw.ci_sync_id

					for ln in res.move_ids:
						origin_srch = [('id','=',ci_sync_id),('origin', '=',res.origin)]
						origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
						if origin_ids:
							pick_id = ''
							if ln.job_assign_check == True :
									product_srch = [('name', '=',ln.product_id.name)]
									product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
									ln_srch = [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
									ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
									srch_pick_ids=0
									if ln_ids:
											fields = ['picking_id'] #fields to read
											data = sock.execute(dbname, userid, pwd, 'stock.move', 'read', ln_ids, fields)
											for pick in data:
												srch_pick_id = [('id', '=',pick['picking_id'][0])]
												srch_pick_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', srch_pick_id)

											stock_pick = {
											'dispatcher_state':'Unassigned',
											'hide_process':False,
											}
											stok_pick_id = sock.execute(dbname, userid, pwd, 'stock.picking', 'write', srch_pick_ids, stock_pick)
											pick_ln = {
										'dispatcher':'',
										'state':'draft'
											 }
											pick_id = sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids, pick_ln)
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
														msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids ,msg_unread)
													notes_line = {
																				 'indent_id':ln_ids[0],
																				 'user_id':user_name if user_name else '',
																				 'source':source_id[0] if source_id else '',
																				 'comment_date':comment_date,
																				 'comment':comment,
																				}
													notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)

							if msg_flag or msg_flag==True:
								msg_write = { 'msg_check':True,
											}
								msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write',origin_ids[0],msg_write)

		return conn_flag

	def sync_request_central_dept_branch(self,cr,uid,ids,context=None):
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		msg_flag_branch=False
		conn_flag_1 = False
		for i in self.browse(cr,uid,ids):
			search_branch = self.pool.get('res.company').search(cr,uid,[('id','=',i.company_id1.id)])
			for branch_id1 in self.pool.get('res.company').browse(cr,uid,search_branch):
				vpn_ip_addr = branch_id1.vpn_ip_address
				port = branch_id1.port
				dbname = branch_id1.dbname
				pwd = branch_id1.pwd
				user_name = str(branch_id1.user_name.login)
				username = user_name #the user
				pwd = pwd    #the password of the user
				dbname = dbname	
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					conn_flag_1 = True
				sock = xmlrpclib.ServerProxy(obj)
				if not conn_flag_1:
					for res in self.browse(cr,uid,ids):
						picking_id = res.picking_id.id
						for line in res.move_ids:
							job_check = line.job_assign_check
							if job_check == True:
								pick = self.pool.get('stock.move').write(cr,uid,line.move_id.id,{'check_job':job_check,
																							# 'state':'pending',
																							 'dispatcher':res.warehouse.name})
							if pick:
								pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',picking_id)])
								for pick_brw in self.pool.get('stock.picking').browse(cr,uid,pick_srch):
									form_branch_id = pick_brw.form_branch_id
									date_new = pick_brw.exp_final_delivery_dt
						for ln in res.move_ids:
							origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
							origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
							if origin_ids:
								search = []                
								pick_id = ''
								if ln.job_assign_check == True :
									product_srch = [('name', '=',ln.product_id.name)]
									product_ids2 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
									ln_srch = [('line_id','=',origin_ids[0]),('product_id', '=',product_ids2[0])]

									ln_ids = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', ln_srch)
									date_value = {'exp_final_delivery_dt':False}
									pick_id11 = sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, date_value)
									if ln_ids:
										pick_ln = {
													'state':'progress',
													'source_company':'',
											}
										pick_id = sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', ln_ids[0], pick_ln)
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
												remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'search', remark_srch)
												if remark_srch_id:
													for test in remark_srch_id:
														notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'unlink', test)
												if not remark_srch_id:
													msg_flag_branch=True
													msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
															}
													msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',ln_ids ,msg_unread)

												notes_line = {
												'indent_id':ln_ids[0],
												'user_id':user_name if user_name else '',
												'source':source_id[0] if source_id else '',
												'comment_date':comment_date,
												'comment':comment,
												}
												notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)

								if msg_flag_branch or msg_flag_branch==True:
									  msg_line = {
									'msg_check':True 
										 }
									  msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)

			for notes in i.picking_note_line: 
				origin_srch = [('id','=',form_branch_id),('order_id', '=',i.origin)]
				origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
				if notes.source:
					source_srch = [('name','=',notes.source.name)]
					source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
	
				remark_srch = [('comment','=',notes.remark_field),('user_id','=',notes.user),('source','=',source_id),('comment_date','=',notes.date),('indent_id','=',origin_ids[0])]
				remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
	
				if remark_srch_id:
					for value in remark_srch_id:
						result = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'unlink', value)
	
				if not remark_srch_id:
					msg_flag_branch=True
	
				notes_line = {
								'indent_id':origin_ids[0],
								'user_id':notes.user if notes.user else '',
								'source':source_id[0] if source_id else '',
								'comment_date':notes.date,
								'comment':notes.remark_field,
							}
				notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)
	
				if msg_flag_branch or msg_flag_branch==True:
					msg_line = {
									'msg_check':True 
						}
					msg_ids= sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, msg_line)

		return conn_flag_1


	def do_partial_res_indent(self, cr, uid, ids, context=None):
		flag2 = False
		stock = ''
		operating_unit = ''
		res_indent_create = ''
		ci_sync_id = 0
		form_branch_id = 0
		origin = ''
		company_id_transfer = ''
		conn_flag = False
		partial = self.browse(cr, uid, ids[0], context=context)
		job_assign = ''
		source_company_create = ''
		source_id_sync = ''
		diff = amt_diff = amt_qty = delivery_rate = 0.0
		source_id_sync = partial.warehouse.name 
		picking_type = partial.picking_id.type
		picking_id = partial.picking_id.id
		stock = []
		stock = [stock_id.stock_ids for stock_id in self.browse(cr,uid,ids) if stock_id.stock_ids]
		res_indent_create = []
		res_indent_create = [create_id.res_indent_create for create_id in self.browse(cr,uid,ids) if create_id.res_indent_create]
		if isinstance(res_indent_create,(list,tuple)):
			res_indent_create = res_indent_create[0] if res_indent_create else []
		for line1 in partial.move_ids:
			qty = line1.quantity
			qty_invisible = line1.quantity_invisible
			diff = float(qty_invisible) - float(qty)
			delivery_rate = line1.delivery_rate
			amt_diff = diff * float(delivery_rate)
			amt_qty = float(qty) * float(delivery_rate)
			msg_check_read=False
			msg_check_read=False

			if qty < qty_invisible:
				split_flag=True
		if split_flag:
			for line in partial.move_ids:
				qty = line.quantity
				qty_invisible = line.quantity_invisible
				diff = float(qty_invisible) - float(qty)
				delivery_rate = line.delivery_rate
				amt_diff = diff * float(delivery_rate)
				amt_qty = float(qty) * float(delivery_rate)
				msg_check_read=False
				msg_check_read=False        
				move_srch = self.pool.get('stock.move').search(cr,uid,[('id','=',int(line.move_id))])
				for move_brw in self.pool.get('stock.move').browse(cr,uid,move_srch):
					msg_check_read=move_brw.msg_check_read
					msg_check_unread=move_brw.msg_check_unread	
				pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',picking_id)])
				for pick_brw in self.pool.get('stock.picking').browse(cr,uid,pick_srch):
					form_branch_id = pick_brw.form_branch_id
					ci_sync_id = pick_brw.ci_sync_id
					origin = pick_brw.origin
					company_id_transfer = pick_brw.company_id.id
					if not flag2:
# sync splitting qtywise::::::::creation of rec in CI
####record creation in Branch for qty splitting
						connect_obj = self.sock_connection_branch(cr, uid, ids, company_id_transfer,context=context)
						sock,userid,conn_flag,Err = socket_connect= self.connect(cr, uid, connect_obj, context=context)
						ip,dbname,usr,pwd,port,company_id_transfer = connect_obj
						if not conn_flag: 
							if pick_brw.company_id:
								company_id_srch1 = [('name', '=',pick_brw.company_id.name)]
								company_ids1 = sock.execute(dbname, userid, pwd, 'res.company', 'search', company_id_srch1)
							if pick_brw.contact_person:
								contact_srch = [('name', '=',pick_brw.contact_person)]
								contact_ids = sock.execute(dbname, userid, pwd, 'res.users', 'search', contact_srch)
							if company_ids1:
								val_fields = ['name']
								val_data = sock.execute(dbname, userid, pwd, 'res.company', 'read', company_ids1, val_fields)
								for var1 in val_data:
									operating_unit = var1['name']
							indent_branch = {
									'order_id':pick_brw.origin,
									'order_date':pick_brw.date if pick_brw.date else False,
									'res_indent_date':pick_brw.date if pick_brw.date else False,
									'operating_unit':operating_unit,
									'indent_type':pick_brw.indent_type if pick_brw.indent_type else '',
									'contact_person_new':contact_ids[0] if contact_ids else False,
									'contact_no':pick_brw.contact_no if pick_brw.contact_no else '',
									'delivery_address':pick_brw.delivery_address if pick_brw.delivery_address else '', 
									'state':'progress',
									'company_id':company_ids1[0] if company_ids1 else '',
									'msg_check':pick_brw.msg_check,
									'job_assign':True,	
										}
							res_indent_create = sock.execute(dbname, userid, pwd, 'res.indent', 'create', indent_branch)
							self.write(cr,uid,ids,{'res_indent_create':res_indent_create})
							current_obj = self.pool.get('stock.picking')
							current_obj.write(cr,uid,stock,{'form_branch_id':res_indent_create})
							#notes updatn overall in the newly created rec in Requester when qtywise splitted: 
							for notes in pick_brw.indent_remark_one2m:
								if res_indent_create:
									if notes.source:
										source_srch1 = [('name','=',notes.source.name)]
										source_id1 = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch1)
									remark_srch = [('comment','=',notes.remark_field),('user_id','=',notes.user),('source','=',source_id1),('comment_date','=',notes.date),('indent_id','=',res_indent_create)]
									remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)

									if remark_srch_id:
										result = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'unlink', remark_srch_id[0])
									notes_line = {
							'indent_id':res_indent_create,
							'user_id':notes.user if notes.user else '',
							'source':source_id1[0] if source_id1 else '',
							'comment_date':notes.date,
							'comment':notes.remark_field,
							    	}
									notes_line_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'create', notes_line)
							#creatn of rec in indent.order.line in Branch after splitting
							if res_indent_create:
							    for ln in pick_brw.move_lines:
							        if ln.indented_qty > ln.product_qty: 
										if ln.product_id:
											prod_id_branch = [('name', '=',ln.product_id.name)] 
											product_id_branch = sock.execute(dbname, userid, pwd, 'product.product', 'search', prod_id_branch)
										if ln.generic_id:
											generic_id_srch_branch = [('name', '=',ln.generic_id.name)] 
											generic_id_branch = sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_id_srch_branch)	
										if ln.product_category:
											prod_cate_branch = [('name', '=', ln.product_category.name)]
											prod_category_branch = sock.execute(dbname, userid, pwd, 'product.category', 'search', prod_cate_branch)
										if ln.product_uom:
											prod_uom_branch = [('name', '=', ln.product_uom.name)]
											uom_branch = sock.execute(dbname, userid, pwd, 'product.uom', 'search',prod_uom_branch)
										if source_id_sync:
											source_id_sync_branch = [('name', '=', source_id_sync)]
											source_company_create = sock.execute(dbname, userid, pwd, 'res.company', 'search',source_id_sync_branch)
										p=ln.indented_qty-ln.product_qty
	
										branch_rec = {
											'product_id':product_id_branch[0] if product_id_branch else False,
											'generic_id':generic_id_branch[0] if generic_id_branch else False,
											'product_code':ln.product_code,
											'product_category':prod_category_branch[0] if prod_category_branch else False,
											'price_unit':ln.delivery_rate,
											'product_uom_qty':ln.indented_qty-ln.product_qty ,
											'product_uom':uom_branch[0] if uom_branch else False,
											'total':float(ln.delivery_rate) *(int(ln.indented_qty)- int(ln.product_qty)),
											'state':'progress',
											'source_company':source_company_create[0] if source_company_create else '',
											'line_id':res_indent_create,
											'msg_check_read':msg_check_read,
											'msg_check_unread':msg_check_unread,
										}
										indent_order_line_sync= sock.execute(dbname, userid, pwd, 'indent.order.line', 'create', branch_rec)
										flag2 = True
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
												notes_line = {
														'indent_id':indent_order_line_sync,
														'user_id':user_name if user_name else '',
														'source':source_id[0] if source_id else '',
														'comment_date':comment_date,
														'comment':comment,
												}
												notes_line_id = sock.execute(dbname, userid, pwd, 'indent.order.comment.line', 'create', notes_line)		
							#updation of indent.order.line old rec in Branch
										branch_indent_srh = [('id', '=',form_branch_id),('order_id','=',origin)]
										branch_indent_id = sock.execute(dbname, userid, pwd, 'res.indent', 'search', branch_indent_srh)
										branch_indent_srh_move = [('line_id', '=',branch_indent_id[0])]
										branch_indent_srh_move_id = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', branch_indent_srh_move)
										if branch_indent_srh_move_id:
											for value in branch_indent_srh_move_id:
												order_line_srh = [('id','=',value),('product_id','=',product_id_branch[0])]
												order_line_id = sock.execute(dbname, userid, pwd, 'indent.order.line', 'search', order_line_srh)
												if order_line_id:
													rec_order_line_srh1 = {'product_uom_qty':ln.product_qty ,'total':float(ln.delivery_rate) *(int(ln.product_qty))}
													rec_order_line_write = sock.execute(dbname, userid, pwd, 'indent.order.line', 'write', value, rec_order_line_srh1)

		return conn_flag

	def do_partial_central_stock_picking(self, cr, uid, ids, context=None):
		flag2 = False
		stock = ''
		operating_unit = ''
		ci_sync_id = 0
		form_branch_id = 0
		origin = ''
		company_id_transfer = ''
		conn_flag = False
		partial = self.browse(cr, uid, ids[0], context=context)
		job_assign = ''
		source_company_create = ''
		source_id_sync = ''
		source_id_sync = partial.warehouse.name 
		picking_type = partial.picking_id.type
		picking_id = partial.picking_id.id
		stock = []
		stock = [stock_id.stock_ids for stock_id in self.browse(cr,uid,ids) if stock_id.stock_ids]
		res_indent_create = []
		res_indent_create = [create_id.res_indent_create for create_id in self.browse(cr,uid,ids) if create_id.res_indent_create]
		if isinstance(res_indent_create,(list,tuple)):
			res_indent_create = res_indent_create[0] if res_indent_create else []
		stock_picking_create = []
		stock_picking_create = [create_id.stock_picking_create for create_id in self.browse(cr,uid,ids) if create_id.stock_picking_create]
		if isinstance(stock_picking_create,(list,tuple)):
			stock_picking_create = stock_picking_create[0] if stock_picking_create else []
		#####record creation in CI for qty splitting
		for line1 in partial.move_ids:
			qty = line1.quantity
			qty_invisible = line1.quantity_invisible
			diff = float(qty_invisible) - float(qty)
			delivery_rate = line1.delivery_rate
			amt_diff = diff * float(delivery_rate)
			amt_qty = float(qty) * float(delivery_rate)
			msg_check_read=False
			msg_check_read=False
			if qty < qty_invisible:
				split_flag=True
		if split_flag:
			if not flag2:
				pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',picking_id)])
				for pick_brw in self.pool.get('stock.picking').browse(cr,uid,pick_srch):
						form_branch_id = pick_brw.form_branch_id
						ci_sync_id = pick_brw.ci_sync_id
						origin = pick_brw.origin
						company_id_transfer = pick_brw.company_id.id
						connect_obj = self.sock_connection(cr, uid, ids, context=context)
						sock,userid,conn_flag,Err = socket_connect= self.connect(cr, uid, connect_obj, context=context)
						ip,dbname,usr,pwd,port,central_id = connect_obj
						if not conn_flag:
							if pick_brw.company_id:
								company_id_srch = [('name', '=',pick_brw.company_id.name)]
								company_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', company_id_srch)
							branch_ids=0
							if pick_brw.branch_name:
								branch_id_srch = [('name', '=',pick_brw.branch_name.name)]
								branch_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', branch_id_srch)

							indent_branch = {
								'origin':pick_brw.origin,
								'company_id':company_ids[0] if company_ids else '',
								'date':pick_brw.date if pick_brw.date else False,
								'indent_category':pick_brw.indent_category if pick_brw.indent_category else '',
								'indent_type':pick_brw.indent_type if pick_brw.indent_type else '',
								'contact_person':pick_brw.contact_person if pick_brw.contact_person else '',
								'customer_name':pick_brw.customer_name if pick_brw.customer_name else '',
								'contact_no':pick_brw.contact_no if pick_brw.contact_no else '',
								'delivery_address':pick_brw.delivery_address if pick_brw.delivery_address else '',    
								'state':'assigned',   
								'customer_vat_tin':pick_brw.customer_vat_tin,
								'customer_cst_no':pick_brw.customer_cst_no,
								'branch_name':branch_ids[0] if branch_ids else '',
								'dispatcher_relation':job_assign if job_assign else '',
								'dispatcher_state':job_assign if job_assign else '',
								'form_branch_id': res_indent_create if res_indent_create else '',
								'msg_check':pick_brw.msg_check,
							}
							stock_picking_create = sock.execute(dbname, userid, pwd, 'stock.picking', 'create', indent_branch)
							self.write(cr,uid,ids,{'stock_picking_create':stock_picking_create})
							current_obj = self.pool.get('stock.picking')
							current_obj.write(cr,uid,stock,{'ci_sync_id':stock_picking_create})
							flag2 = True
							#notes updatn in CI for newly created record when qtywise splitted:
							if stock_picking_create:
								pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',picking_id)])
								for pick_brw in self.pool.get('stock.picking').browse(cr,uid,pick_srch):
									for notes in pick_brw.indent_remark_one2m:
										if notes.source:
											source_srch = [('name','=',notes.source.name)]
											source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
										remark_srch = [('remark','=',stock_picking_create),('remark_field','=',notes.remark_field),('user','=',notes.user),('source','=',source_id),('date','=',notes.date)]
										remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
										if remark_srch_id:
											for p in remark_srch_id:
												central_in_write = {'remark_field':notes.remark_field,
																	'state':notes.state,
																	'user':notes.user if notes.user else '',
																	'date':notes.date,
																	'source':source_id[0] if source_id else '',
																	}
												notes_ids= sock.execute(dbname, userid, pwd, 'indent.remark', 'write', p, central_in_write)
										else:
											central_in_create = { 'remark_field':notes.remark_field,
																  'state':notes.state,
																  'remark':stock_picking_create,
																  'user':notes.user if notes.user else '',
																  'date':notes.date,
																  'source':source_id[0] if source_id else '',
																}
											notes_ids= sock.execute(dbname, userid, pwd, 'indent.remark', 'create', central_in_create)
							for line in partial.move_ids:
								qty = line.quantity
								qty_invisible = line.quantity_invisible
								diff = float(qty_invisible) - float(qty)
								delivery_rate = line.delivery_rate
								amt_diff = diff * float(delivery_rate)
								amt_qty = float(qty) * float(delivery_rate)
								msg_check_read=False
								msg_check_read=False        
								move_srch = self.pool.get('stock.move').search(cr,uid,[('id','=',int(line.move_id))])
								for move_brw in self.pool.get('stock.move').browse(cr,uid,move_srch):
									msg_check_read=move_brw.msg_check_read
									msg_check_unread=move_brw.msg_check_unread
								if diff > 0:
									if line.product_id:
										prod_id = [('name', '=',line.product_id.name)] 
										product_id = sock.execute(dbname, userid, pwd, 'product.product', 'search', prod_id)

									if line.generic_id:
										generic_id_srch = [('name', '=',line.generic_id.name)] 
										generic_id = sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_id_srch)

									if line.product_category:
										prod_cate = [('name', '=', line.product_category.name)]
										prod_category = sock.execute(dbname, userid, pwd, 'product.category', 'search', prod_cate)
									if line.product_uom:
										prod_uom = [('name', '=', line.product_uom.name)]
										uom = sock.execute(dbname, userid, pwd, 'product.uom', 'search', prod_uom)
									pick_line1 = {
										'product_id':product_id[0] if product_id else prod_id,
										'generic_id':generic_id[0] if generic_id else False,
										'product_uom':uom[0],
										'product_category':prod_category[0],
										'product_code':line.product_code,
										'product_qty':diff,
										'delivery_rate':line.delivery_rate,
										'amount':amt_diff,
										'dispatcher':partial.warehouse.name,
										'state':'pending',
										'picking_id':stock_picking_create,
										'msg_check_read': msg_check_read,
										'msg_check_unread':msg_check_unread,
													}
									move_ids_sync= sock.execute(dbname, userid, pwd, 'stock.move', 'create', pick_line1)
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
										notes_line = {
													'indent_id':move_ids_sync,
													'user_id':user_name if user_name else '',
													'source':source_id[0] if source_id else '',
													'comment_date':comment_date,
													'comment':comment,
													}
										notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
							#updation of stock.move old rec in CI
							rec_srh = [('id', '=',ci_sync_id),('origin','=',origin)]
							rec_srh_id = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', rec_srh)
							rec_srh_move = [('picking_id', '=',rec_srh_id[0])]
							rec_srh_move_id = sock.execute(dbname, userid, pwd, 'stock.move', 'search', rec_srh_move)
							if line.product_id:
								prod_id_1 = [('name', '=',line.product_id.name)] 
								product_id_1 = sock.execute(dbname, userid, pwd, 'product.product', 'search', prod_id_1)
							if rec_srh_move_id:
								for var in rec_srh_move_id:
									srh_move = [('id','=',var),('product_id','=',product_id_1[0])]
									srh_move_id = sock.execute(dbname, userid, pwd, 'stock.move', 'search', srh_move)
									if srh_move_id:
										rec_stock_move_srh = {'product_qty':qty,'amount':amt_qty}
										rec_stock_move_write = sock.execute(dbname, userid, pwd, 'stock.move', 'write', var, rec_stock_move_srh)
		return conn_flag

	def do_partial_res_indent_ci_sync_update(self, cr, uid, ids, context=None):
		flag2 = False
		operating_unit = ''
		res_indent_create = ''
		ci_sync_id = 0
		form_branch_id = 0
		origin = ''
		company_id_transfer = ''
		conn_flag = False
		partial = self.browse(cr, uid, ids[0], context=context)
		job_assign = ''
		source_company_create = ''
		source_id_sync = ''
		source_id_sync = partial.warehouse.name 
		picking_type = partial.picking_id.type
		picking_id = partial.picking_id.id
		stock_picking_create = []
		stock_picking_create = [create_id.stock_picking_create for create_id in self.browse(cr,uid,ids) if create_id.stock_picking_create]
		if isinstance(stock_picking_create,(list,tuple)):
			stock_picking_create = stock_picking_create[0] if stock_picking_create else []
		stock = []
		stock = [stock_id.stock_ids for stock_id in self.browse(cr,uid,ids) if stock_id.stock_ids]
		if isinstance(stock,(list,tuple)):
			stock = stock[0] if stock else []
		pick_srch = self.pool.get('stock.picking').search(cr,uid,[('id','=',picking_id)])
		for pick_brw in self.pool.get('stock.picking').browse(cr,uid,pick_srch):
			company_id_transfer = pick_brw.company_id.id
		connect_obj = self.sock_connection_branch(cr, uid, ids, company_id_transfer,context=context)
		sock,userid,conn_flag,Err = socket_connect= self.connect(cr, uid, connect_obj, context=context)
		ip,dbname,usr,pwd,port,company_id_transfer = connect_obj
		if not conn_flag:
			indent_srch_fact = {
				'indent_id': stock,
				'ci_sync_id':stock_picking_create,
			}
			indent_ids_fact= sock.execute(dbname, userid, pwd, 'res.indent', 'write', res_indent_create ,indent_srch_fact)

		return conn_flag

stock_partial_picking()


