#Version No. : 1.0.039 For Vertual Godown task for branches
from datetime import date,datetime, timedelta
from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
import calendar
import re
import os
from base.res import res_company as COMPANY
from base.res import res_partner
from collections import Counter
import xmlrpclib
import os

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
		if context is None: context = {}
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
			time_cur = time.strftime("%H%M%S")
			date = time.strftime('%Y-%m-%d%H%M%S')
			user_name = str(delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				raise
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_prepare_packlist_branch','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
				##############################################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Prepare_packlist-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION Prepare_packlist() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n prod_ids INT;
						\n remark_srch_id INT;
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT Prepare_packlist();\n"
				sync_str+=func_string+declare+var1
				for line in res.stock_transfer_product:
					origin_ids="\n origin_ids=(SELECT id FROM res_indent WHERE id=%s AND order_id='%s');"%(str(form_branch_id),(res.origin))
					sync_str+=origin_ids
					if line.state!='cancel_order_qty':
						product_ids="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((line.product_name.name).replace("'","''")))
						prod_ids="\n prod_ids=(SELECT id FROM indent_order_line WHERE line_id = origin_ids AND product_id=product_ids);"
						move_ids="\n UPDATE indent_order_line SET state='packlist' WHERE line_id = origin_ids AND product_id=product_ids;"
						sync_str+=product_ids+prod_ids+move_ids
						if line.notes_one2many:
							for material_notes in line.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								source_id=0
								if material_notes.source:
									source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(material_notes.source.name))
								remark_srch_id="\n remark_srch_id=(SELECT id from indent_order_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=prod_ids LIMIT 1);"%(str(comment),str(user_name),str(comment_date))
								ifstr="\n IF remark_srch_id is NULL THEN"
								msg_unread_id="\n UPDATE indent_order_line SET msg_check_unread=True,msg_check_read=False WHERE id=prod_ids;"
								notes_line_id="\n INSERT INTO indent_order_comment_line (indent_id,user_id,source,comment_date,comment) VALUES (prod_ids,'%s',source_id,'%s','%s');"%(str(user_name),str(comment_date),str(comment))
								sync_str+=source_id+remark_srch_id+ifstr+msg_unread_id+notes_line_id+endif
					for notes in res.notes_one2many:
						if notes.source:
							source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
							remark_srch_id="\n remark_srch_id=(SELECT id from indent_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=origin_ids LIMIT 1);"%(str(notes.name),str(notes.user_name),str(notes.date))
							ifstr="\n IF remark_srch_id is NULL THEN"
							notes_line_id="\n INSERT INTO indent_comment_line (indent_id,user_id,source,comment_date,comment,state) VALUES (origin_ids,'%s',source_id,'%s','%s','%s');"%(str(notes.user_name),str(notes.date),str(notes.name),str(notes.state))
							msg_ids="\n UPDATE res_indent SET msg_check=True WHERE id=origin_ids;"
							sync_str+=source_id+remark_srch_id+ifstr +notes_line_id+msg_ids+endif
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
################################################################################################################
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:
				for line in res.stock_transfer_product:
					origin_srch = [('id','=',form_branch_id),('order_id', '=',res.origin)]
					origin_ids = sock.execute(dbname, userid, pwd, 'res.indent', 'search', origin_srch)
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
					for notes in res.notes_one2many:
						if notes.source:
							source_srch = [('name','=',notes.source.name)]
							source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
						remark_srch = [('comment','=',notes.name),('user_id','=',notes.user_name),('source','=',source_id[0]),('comment_date','=',notes.date),('indent_id','=',origin_ids[0])]
						remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.comment.line', 'search', remark_srch)
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
						msg_line={
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
			time_cur = time.strftime("%H%M%S")
			date = time.strftime('%Y-%m-%d%H%M%S')
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				raise
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag_1 = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_prepare_packlist_central','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag_1})

				##############################################################################################
				con_cat = dbname+"-"+ branch_id.vpn_ip_address+"-"+'Prepare_packlist-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION Prepare_packlist() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n ln_ids INT;
						\n remark_srch_id INT;
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT Prepare_packlist();\n"
				sync_str+=func_string+declare+var1
				for rec in self.browse(cr,uid,ids):
					origin_ids="\n origin_ids=(SELECT id FROM stock_picking WHERE id=%s and origin='%s');" %(str(ci_sync_id),str(rec.origin))
					sync_str+=origin_ids
					for ln in rec.stock_transfer_product:
						if ln.state!='cancel_order_qty':
							product_ids="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((ln.product_name.name).replace("'","''")))
							ln_ids="\n ln_ids=(SELECT id FROM stock_move WHERE product_id=product_ids AND picking_id=origin_ids);"
							move_ids="\n UPDATE stock_move SET state='packlist' WHERE id=ln_ids;"
							sync_str+=product_ids+ln_ids+move_ids
							if ln.notes_one2many:
								for material_notes in ln.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									if material_notes.source:
										source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(material_notes.source.name)
									remark_srch_id="\n remark_srch_id=(SELECT id FROM stock_move_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=ln_ids LIMIT 1);" %(str(comment),str(user_name),str(comment_date))
									ifstr="\n IF remark_srch_id IS NULL THEN"
									msg_unread_ids="UPDATE stock_move SET msg_check_unread=True,msg_check_read=False WHERE id=ln_ids;"
									notes_line_id="\n INSERT INTO stock_move_comment_line (indent_id, user_id, source, comment_date, comment) VALUES (ln_ids,'%s',source_id,'%s','%s');"%(str(user_name),str(comment_date),str(comment))
									sync_str+=source_id+remark_srch_id+ifstr+msg_unread_id+notes_line_id+endif
					if rec.notes_one2many:
						for notes in rec.notes_one2many:
							if notes.source:
								source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
								remark_srch_id="\n remark_srch_id=(SELECT id from indent_remark WHERE remark_field='%s' and \"user\"='%s' and source=source_id and date='%s' and remark=origin_ids LIMIT 1);"%(str(notes.name),str(notes.user_name),str(notes.date))
								ifstr="\n IF remark_srch_id is NULL THEN"
								notes_line_id="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (origin_ids,'%s',source_id,'%s','%s');"%(str(notes.user_name),str(notes.date),str(notes.name))
								msg_ids="\n UPDATE stock_picking SET msg_check=True WHERE id=origin_ids;"
								sync_str+=source_id+remark_srch_id+ifstr +notes_line_id+msg_ids+endif
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
#############################################################################################
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
										pick_line={
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
						msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)
		return True

	def sync_ready_to_dispatch(self,cr,uid,ids,context=None):
		if context is None: context = {}
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
			time_cur = time.strftime("%H%M%S")
			date = time.strftime('%Y-%m-%d%H%M%S')
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				raise
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_ready_to_dispatch_branch','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'ready_to_dispatch-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION ready_to_dispatch() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n prod_ids INT;
						\n remark_srch_id INT;
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT ready_to_dispatch();\n"
				sync_str+=func_string+declare+var1
				for line in res.stock_transfer_product:
					origin_ids="\n origin_ids=(SELECT id FROM res_indent WHERE id=%s AND order_id='%s');"%(str(form_branch_id),(res.origin))
					sync_str+=origin_ids
					if line.state!='cancel_order_qty':
						product_ids="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((line.product_name.name).replace("'","''")))
						prod_ids="\n prod_ids=(SELECT id FROM indent_order_line WHERE line_id = origin_ids AND product_id=product_ids);"
						move_ids="\n UPDATE indent_order_line SET state='dispatch',eta='%s' WHERE line_id = origin_ids AND product_id=product_ids;\n UPDATE res_indent SET order_id='%s' WHERE id=origin_ids;" %(str(res.expected_delivery_time),str(res.origin))
						sync_str+=product_ids+prod_ids+move_ids
						if line.notes_one2many:
							for material_notes in line.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								source_id=0
								if material_notes.source:
									source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(material_notes.source.name))
								remark_srch_id="\n remark_srch_id=(SELECT id from indent_order_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=prod_ids LIMIT 1);"%(str(comment),str(user_name),str(comment_date))
								ifstr="\n IF remark_srch_id is NULL THEN"
								msg_unread_id="\n UPDATE indent_order_line SET msg_check_unread=True,msg_check_read=False WHERE id=prod_ids;"
								notes_line_id="\n INSERT INTO indent_order_comment_line (indent_id,user_id,source,comment_date,comment) VALUES (prod_ids,'%s',source_id,'%s','%s');"%(str(user_name),str(comment_date),str(comment))
								sync_str+=source_id+remark_srch_id+ifstr+msg_unread_id+notes_line_id+endif
					for notes in res.notes_one2many:
						if notes.source:
							source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
							remark_srch_id="\n remark_srch_id=(SELECT id from indent_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=origin_ids LIMIT 1);"%(str(notes.name),str(notes.user_name),str(notes.date))
							ifstr="\n IF remark_srch_id is NULL THEN"
							notes_line_id="\n INSERT INTO indent_comment_line (indent_id,user_id,source,comment_date,comment,state) VALUES (origin_ids,'%s',source_id,'%s','%s','%s');"%(str(notes.user_name),str(notes.date),str(notes.name),str(notes.state))
							msg_ids="\n UPDATE res_indent SET msg_check=True WHERE id=origin_ids;"
							sync_str+=source_id+remark_srch_id+ifstr +notes_line_id+msg_ids+endif
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
####################################################################################################
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
								eta_pick_write1 = sock.execute(dbname, userid, pwd, 'res.indent', 'write', origin_ids, eta_picking1)
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
											msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
												}
											msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',prod_ids ,msg_unread)
											msg_flag_branch=True
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
				time_cur = time.strftime("%H%M%S")
				date = time.strftime('%Y-%m-%d%H%M%S')
				username = user_name #the user
				pwd = pwd    #the password of the user
				dbname = dbname
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					raise
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					# offline_obj=self.pool.get('offline.sync')
					# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag_1 = True
					# if not offline_sync_sequence:
					# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_ready_to_dispatch_central','error_log':Err,})
					# else:
					# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag_1})
					##############################################################################################
					con_cat = dbname+"-"+ branch_id.vpn_ip_address+"-"+'ready_to_dispatch-'+str(date)+'_'+str(time_cur)+'.sql'
					sync_str=''
					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
					directory_name =str(os.path.expanduser('~')+'/indent_sync/')
					if not os.path.exists(directory_name):
						os.makedirs(directory_name)
					d = os.path.dirname(directory_name)
					func_string ="\n\n CREATE OR REPLACE FUNCTION ready_to_dispatch() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
					declare=" DECLARE \n "
					var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n ln_ids INT;
							\n remark_srch_id INT;
							\n  BEGIN \n """
					endif="\n\n END IF; \n"
					ret="\n RETURN 1;\n"
					elsestr="\n ELSE \n"
					final="\nEND; \n $$;\n"
					fun_call="\n SELECT ready_to_dispatch();\n"
					sync_str+=func_string+declare+var1
					for rec in self.browse(cr,uid,ids):
						origin_ids="\n origin_ids=(SELECT id FROM stock_picking WHERE id=%s and origin='%s');" %(str(ci_sync_id),str(rec.origin))
						sync_str+=origin_ids
						for ln in rec.stock_transfer_product:
							if ln.state!='cancel_order_qty':
								product_ids="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((ln.product_name.name).replace("'","''")))
								ln_ids="\n ln_ids=(SELECT id FROM stock_move WHERE product_id=product_ids AND picking_id=origin_ids);"
								move_ids="\n UPDATE stock_move SET state='dispatch',eta='%s' WHERE id=ln_ids;" %(str(res.expected_delivery_time))
								sync_str+=product_ids+ln_ids+move_ids
								if ln.notes_one2many:
									for material_notes in ln.notes_one2many:
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										source_id=0
										if material_notes.source:
											source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(material_notes.source.name)
										remark_srch_id="\n remark_srch_id=(SELECT id FROM stock_move_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=ln_ids LIMIT 1);" %(str(comment),str(user_name),str(comment_date))
										ifstr="\n IF remark_srch_id IS NULL THEN"
										msg_unread_ids="UPDATE stock_move SET msg_check_unread=True,msg_check_read=False WHERE id=ln_ids;"
										notes_line_id="\n INSERT INTO stock_move_comment_line (indent_id, user_id, source, comment_date, comment) VALUES (ln_ids,'%s',source_id,'%s','%s');"%(str(user_name),str(comment_date),str(comment))
										sync_str+=source_id+remark_srch_id+ifstr+msg_unread_id+notes_line_id+endif
						if rec.notes_one2many:
							for notes in rec.notes_one2many:
								if notes.source:
									source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
									remark_srch_id="\n remark_srch_id=(SELECT id from indent_remark WHERE remark_field='%s' and \"user\"='%s' and source=source_id and date='%s' and remark=origin_ids LIMIT 1);"%(str(notes.name),str(notes.user_name),str(notes.date))
									ifstr="\n IF remark_srch_id is NULL THEN"
									notes_line_id="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (origin_ids,'%s',source_id,'%s','%s');"%(str(notes.user_name),str(notes.date),str(notes.name))
									msg_ids="\n UPDATE stock_picking SET msg_check=True WHERE id=origin_ids;"
									sync_str+=source_id+remark_srch_id+ifstr +notes_line_id+msg_ids+endif
					with(open(filename,'a')) as f :
						f.write(sync_str)
						f.write(ret)
						f.write(final)
						f.write(fun_call)
						f.close()
	#############################################################################################
				sock = xmlrpclib.ServerProxy(obj)
				if conn_flag_1 == False: 
					origin_srch = [('id','=',ci_sync_id),('origin', '=',res.origin)]
					origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
					if origin_ids:
						for ln in res.stock_transfer_product:
							if ln.state!='cancel_order_qty':
								product_srch = [('name', '=',ln.product_name.name)]
								product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
								ln_srch =  [('product_id', '=',product_ids[0]),('picking_id','=',origin_ids[0])]
								ln_ids = sock.execute(dbname, userid, pwd, 'stock.move', 'search', ln_srch)
								if ln_ids:
									pick_line = {
												'state':'dispatch',
												'eta':res.expected_delivery_time,
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
									remark_srch = [('remark_field','=',notes.name),('user','=',notes.user_name),('source','=',source_id[0]),('remark','=',
	origin_ids[0]),('date','=',notes.date)]
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
		if context is None: context = {}
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
				time_cur = time.strftime("%H%M%S")
				date = time.strftime('%Y-%m-%d%H%M%S')
				username = user_name #the user
				pwd = pwd    #the password of the user
				dbname = dbname
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					raise
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					# offline_obj=self.pool.get('offline.sync')
					# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					# if not offline_sync_sequence:
					# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'update_department_dispatch','error_log':Err,})
					# else:
					# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
####################################################################################################################
					con_cat = dbname+"-"+ branch_id.vpn_ip_address+"-"+'dispatch_department-'+str(date)+'_'+str(time_cur)+'.sql'
					sync_str=''
					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
					directory_name =str(os.path.expanduser('~')+'/indent_sync/')
					if not os.path.exists(directory_name):
						os.makedirs(directory_name)
					d = os.path.dirname(directory_name)
					func_string ="\n\n CREATE OR REPLACE FUNCTION dispatch_department() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
					declare=" DECLARE \n "
					var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n ln_ids INT;
							\n remark_srch_id INT;
							\n  BEGIN \n """
					endif="\n\n END IF; \n"
					ret="\n RETURN 1;\n"
					elsestr="\n ELSE \n"
					final="\nEND; \n $$;\n"
					fun_call="\n SELECT dispatch_department();\n"
					sync_str+=func_string+declare+var1
					origin_ids="\n origin_ids=(SELECT id FROM stock_picking WHERE id=%s and origin='%s');" %(str(ci_sync_id),str(i.origin))
					sync_str+=origin_ids
					for ln in i.stock_transfer_product:
						if ln.state!='cancel_order_qty':
							product_ids="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((ln.product_name.name).replace("'","''")))
							ln_ids="\n ln_ids=(SELECT id FROM stock_move WHERE product_id=product_ids and picking_id=origin_ids);"
							move_ids="\n UPDATE stock_move SET state='intransit' WHERE id=ln_ids;"
							sync_str+=product_ids+ln_ids+move_ids
							if ln.notes_one2many:
								for material_notes in ln.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									if material_notes.source:
										source_id ="\n source_id =(SELECT id FROM res_company WHERE name='%s');"
										remark_srch_id="\n remark_srch_id=(SELECT id FROM stock_move_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and indent_id=ln_ids);"
										ifstr="\n IF remark_srch_id is NULL THEN "
										msg_unread_ids="\n UPDATE stock_move SET msg_check_unread=True,msg_check_read=False WHERE id=ln_ids;"
										notes_line_id="\n INSERT INTO stock_move_comment_line(indent_id,user_id,source,comment_date,comment) VALUES (ln_ids,'%s',source_id,'%s','%s');" %(user_name,str(comment_date),comment)
										sync_str+=source_id+remark_srch_id+ifstr+msg_unread_ids+notes_line_id+endif
					if i.notes_one2many:
						for notes in i.notes_one2many:
							if notes.source:
								source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
								remark_srch_id="\n remark_srch_id=(SELECT id from indent_remark WHERE remark_field='%s' and \"user\"='%s' and source=source_id and date='%s' and remark=origin_ids LIMIT 1);"%(str(notes.name),str(notes.user_name),str(notes.date))
								ifstr="\n IF remark_srch_id is NULL THEN"
								notes_line_id="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (origin_ids,'%s',source_id,'%s','%s');"%(str(notes.user_name),str(notes.date),str(notes.name))
								msg_ids="\n UPDATE stock_picking SET msg_check=True WHERE id=origin_ids;"
								sync_str+=source_id+remark_srch_id+ifstr +notes_line_id+msg_ids+endif
					with(open(filename,'a')) as f :
						f.write(sync_str)
						f.write(ret)
						f.write(final)
						f.write(fun_call)
						f.close()
####################################################################################################################
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
		if context is None: context = {}
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
			time_cur = time.strftime("%H%M%S")
			date = time.strftime('%Y-%m-%d%H%M%S')
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				raise
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'update_branch_state','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
#############################################################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Dispatch_Branch-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION Dispatch_Branch() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n prod_ids INT;
						\n remark_srch_id INT;
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT Dispatch_Branch();\n"
				sync_str+=func_string+declare+var1
				for line in res.stock_transfer_product:
					origin_ids="\n origin_ids=(SELECT id FROM res_indent WHERE id=%s AND order_id='%s');"%(str(form_branch_id),(res.origin))
					sync_str+=origin_ids
					if line.state!='cancel_order_qty':
						product_ids="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((line.product_name.name).replace("'","''")))
						prod_ids="\n prod_ids=(SELECT id FROM indent_order_line WHERE line_id = origin_ids AND product_id=product_ids);"
						move_ids="\n UPDATE indent_order_line SET state='intransit' WHERE line_id = origin_ids AND product_id=product_ids;"
						sync_str+=product_ids+prod_ids+move_ids
						if line.notes_one2many:
							for material_notes in line.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								source_id=0
								if material_notes.source:
									source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(material_notes.source.name))
								remark_srch_id="\n remark_srch_id=(SELECT id from indent_order_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=prod_ids LIMIT 1);"%(str(comment),str(user_name),str(comment_date))
								ifstr="\n IF remark_srch_id is NULL THEN"
								msg_unread_id="\n UPDATE indent_order_line SET msg_check_unread=True,msg_check_read=False WHERE id=prod_ids;"
								notes_line_id="\n INSERT INTO indent_order_comment_line (indent_id,user_id,source,comment_date,comment) VALUES (prod_ids,'%s',source_id,'%s','%s');"%(str(user_name),str(comment_date),str(comment))
								sync_str+=source_id+remark_srch_id+ifstr+msg_unread_id+notes_line_id+endif
					for notes in res.notes_one2many:
						if notes.source:
							source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
							remark_srch_id="\n remark_srch_id=(SELECT id from indent_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=origin_ids LIMIT 1);"%(str(notes.name),str(notes.user_name),str(notes.date))
							ifstr="\n IF remark_srch_id is NULL THEN"
							notes_line_id="\n INSERT INTO indent_comment_line (indent_id,user_id,source,comment_date,comment,state) VALUES (origin_ids,'%s',source_id,'%s','%s','%s');"%(str(notes.user_name),str(notes.date),str(notes.name),str(notes.state))
							msg_ids="\n UPDATE res_indent SET msg_check=True WHERE id=origin_ids;"
							sync_str+=source_id+remark_srch_id+ifstr +notes_line_id+msg_ids+endif
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()

#############################################################################################################
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
		if context is None: context = {}
		msg_flag=False
		ci_sync_id = ''
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
				time_cur = time.strftime("%H%M%S")
				date = time.strftime('%Y-%m-%d%H%M%S')
				username = user_name #the user
				pwd = pwd    #the password of the user
				dbname = dbname
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					raise
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					# offline_obj=self.pool.get('offline.sync')
					# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					# if not offline_sync_sequence:
					# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'update_department_dispatch_delivery','error_log':Err,})
					# else:
					# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
###############################################################################################################
					con_cat = dbname+"-"+ branch_id.vpn_ip_address+"-"+'dispatch_department-'+str(date)+'_'+str(time_cur)+'.sql'
					sync_str=''
					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
					directory_name =str(os.path.expanduser('~')+'/indent_sync/')
					if not os.path.exists(directory_name):
						os.makedirs(directory_name)
					d = os.path.dirname(directory_name)
					func_string ="\n\n CREATE OR REPLACE FUNCTION dispatch_department() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
					declare=" DECLARE \n "
					var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n ln_ids INT;
							\n remark_srch_id INT;
							\n  BEGIN \n """
					endif="\n\n END IF; \n"
					ret="\n RETURN 1;\n"
					elsestr="\n ELSE \n"
					final="\nEND; \n $$;\n"
					fun_call="\n SELECT dispatch_department();\n"
					sync_str+=func_string+declare+var1
					origin_ids="\n origin_ids=(SELECT id FROM stock_picking WHERE id=%s and origin='%s');" %(str(ci_sync_id),str(i.origin))
					sync_str+=origin_ids
					for ln in i.stock_transfer_product:
						if ln.state!='cancel_order_qty':
							product_ids="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((ln.product_name.name).replace("'","''")))
							ln_ids="\n ln_ids=(SELECT id FROM stock_move WHERE product_id=product_ids and picking_id=origin_ids);"
							move_ids="\n UPDATE stock_move SET state='done' WHERE id=ln_ids;"
							sync_str+=product_ids+prod_ids+move_ids
							if ln.notes_one2many:
								for material_notes in ln.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									if material_notes.source:
										source_id ="\n source_id =(SELECT id FROM res_company WHERE name='%s');"
										remark_srch_id="\n remark_srch_id=(SELECT id FROM stock_move_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and indent_id=ln_ids);"
										ifstr="\n IF remark_srch_id is NULL THEN "
										msg_unread_ids="\n UPDATE stock_move SET msg_check_unread=True,msg_check_read=False WHERE id=ln_ids;"
										notes_line_id="\n INSERT INTO stock_move_comment_line(indent_id,user_id,source,comment_date,comment) VALUES (ln_ids,'%s',source_id,'%s','%s');" %(user_name,str(comment_date),comment)
										sync_str+=source_id+remark_srch_id+ifstr+msg_unread_id+notes_line_id+endif
					if rec.notes_one2many:
						for notes in rec.notes_one2many:
							if notes.source:
								source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
								remark_srch_id="\n remark_srch_id=(SELECT id from indent_remark WHERE remark_field='%s' and \"user\"='%s' and source=source_id and date='%s' and remark=origin_ids LIMIT 1);"%(str(notes.name),str(notes.user_name),str(notes.date))
								ifstr="\n IF remark_srch_id is NULL THEN"
								notes_line_id="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (origin_ids,'%s',source_id,'%s','%s');"%(str(notes.user_name),str(notes.date),str(notes.name))
								msg_ids="\n UPDATE stock_picking SET msg_check=True WHERE id=origin_ids;"
								sync_str+=source_id+remark_srch_id+ifstr +notes_line_id+msg_ids+endif
					with(open(filename,'a')) as f :
						f.write(sync_str)
						f.write(ret)
						f.write(final)
						f.write(fun_call)
						f.close()
	###############################################################################################################
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

	def update_branch_state_delivery(self,cr,uid,ids,context=None):#.... This function is used for sales delivery
		if context is None: context = {}
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
			time_cur = time.strftime("%H%M%S")
			date = time.strftime('%Y-%m-%d%H%M%S')
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				raise
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'update_branch_state_delivery','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
#############################################################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Dispatch_Branch_sales-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION Dispatch_Branch_sales() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n prod_ids INT;
						\n remark_srch_id INT; \n receive_origin_ids INT;
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT Dispatch_Branch_sales();\n"
				sync_str+=func_string+declare+var1
				for line in res.stock_transfer_product:
					origin_ids="\n origin_ids=(SELECT id FROM res_indent WHERE id=%s AND order_id='%s');"%(str(form_branch_id),(res.origin))
					sync_str+=origin_ids
					if line.state!='cancel_order_qty':
						product_ids="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((line.product_name.name).replace("'","''")))
						prod_ids="\n prod_ids=(SELECT id FROM indent_order_line WHERE line_id = origin_ids AND product_id=product_ids);"
						move_ids="\n UPDATE indent_order_line SET state='received' WHERE line_id = origin_ids AND product_id=product_ids;"
						sync_str+=product_ids+prod_ids+move_ids
						if line.notes_one2many:
							for material_notes in line.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								source_id=0
								if material_notes.source:
									source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
								remark_srch_id="\n remark_srch_id=(SELECT id from indent_order_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=prod_ids LIMIT 1);"%(str(comment),str(user_name),str(comment_date))
								ifstr="\n IF remark_srch_id is NULL THEN"
								msg_unread_id="\n UPDATE indent_order_line SET msg_check_unread=True,msg_check_read=False WHERE id=prod_ids;"
								notes_line_id="\n INSERT INTO indent_order_comment_line (indent_id,user_id,source,comment_date,comment) VALUES (prod_ids,'%s',source_id,'%s','%s');"%(str(user_name),str(comment_date),str(comment))
								sync_str+=source_id+remark_srch_id+ifstr+msg_unread_id+notes_line_id+endif
					for notes in res.notes_one2many:
						if notes.source:
							source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s');"%(str(notes.source.name))
							remark_srch_id="\n remark_srch_id=(SELECT id from indent_comment_line WHERE comment='%s' and user_id='%s' and source=source_id and comment_date='%s' and indent_id=origin_ids LIMIT 1);"%(str(notes.name),str(notes.user_name),str(notes.date))
							ifstr="\n IF remark_srch_id is NULL THEN"
							notes_line_id="\n INSERT INTO indent_comment_line (indent_id,user_id,source,comment_date,comment,state) VALUES (origin_ids,'%s',source_id,'%s','%s','%s');"%(str(notes.user_name),str(notes.date),str(notes.name),str(notes.state))
							msg_ids="\n UPDATE res_indent SET msg_check=True WHERE id=origin_ids;"
							sync_str+=source_id+remark_srch_id+ifstr +notes_line_id+msg_ids+endif
				
					if res.delivery_type=="export_delivery":
						receive_origin_ids ="\n receive_origin_ids=(SELECT id FROM receive_indent WHERE indent_no='%s' AND state='intransit' AND order_number='%');"%(str(res.origin),str(res.stock_transfer_no))
						recieve_state_ids="\n UPDATE receive_indent SET state='done' WHERE id=receive_origin_ids;", sock.execute(dbname, userid, pwd, 'receive.indent', 'write', receive_origin_ids, recieve_state)
						sync_str+=receive_origin_ids+recieve_state_ids
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
#############################################################################################################
			sock = xmlrpclib.ServerProxy(obj)
			if not conn_flag:
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
		if context is None: context = {}
		remark_srch_id = False
		year = ''
		conn_flag = False
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
			time_cur = time.strftime("%H%M%S")
			date1 = time.strftime('%Y-%m-%d%H%M%S')
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
					
###############################################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Dispatch_Branch_sales-'+str(date1)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION Dispatch_Branch_sales() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" search INT;\n product_ids INT;\n source_id INT;\n prod_ids INT;
						\n remark_srch_id INT; \n receive_origin_ids INT;\n ids INT;
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT Dispatch_Branch_sales();\n"
				sync_str+=func_string+declare+var1
				current_date=date.today()
				monthee = current_date.month
				year = current_date.year
				words_month = dict1[monthee]
				search="\n search=(SELECT id FROM indent_dashboard WHERE month='%s' and year='%s' LIMIT 1);" %(str(words_month),str(year))
				ifstr="\n IF search IS NULL THEN"
				create_dash="\n INSERT INTO indent_dashboard (month,count,year,month_id) VALUES('%s',1,'%s','%s');" %(str(words_month),str(year),str(monthee))
				count4="UPDATE indent_dashboard SET count=count+1 WHERE id=search"
				for_loop=" "
###############################################################################################
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
		if context is None: context = {}
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
			time_cur = time.strftime("%H%M%S")
			date = time.strftime('%Y-%m-%d%H%M%S')
			user_name = str(i.delivery_location.user_name.login)
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				raise
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':i.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_dispatch','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
#############################################################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Dispatch_Branch_Indent-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION Dispatch_Branch_Indent() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n source_ids INT;\n prod_ids INT;\n source_id INT;
\n remark_srch_id INT; \n receive_origin_ids INT; \n location INT; \n concern_branch_ids INT;
\n cust_ids INT; \n stock_id1 INT; \n prod_id INT; \n product_qty_ids INT; \n product_qty_local_ids INT;
\n generic_id INT; \n batch_ids INT; \n stock_tran_prod_id INT; \n 
\n  BEGIN \n cust_ids=NULL;\n concern_branch_ids=NULL; \n location=NULL;\n source_ids=NULL;"""
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT Dispatch_Branch_Indent();\n"
				sync_str+=func_string+declare+var1
				cust_ids=''
				concern_branch_ids=''
				location=''
				source_ids=''
				if i.source :
					source_ids="\n source_ids=(SELECT id FROM res_company WHERE name='%s' LIMIT 1);" %(str(i.source.name))
					sync_str+=source_ids
				if i.delivery_location :
					location="\n location=(SELECT id FROM res_company WHERE name='%s' LIMIT 1);" %(str(i.delivery_location.name))
					sync_str += location
				if i.branch_name :
					concern_branch_ids="\n concern_branch_ids=(SELECT id FROM res_company WHERE name='%s' LIMIT 1);" %(str(i.branch_name.name))
					sync_str += concern_branch_ids
				if i.customer_vat_tin or i.customer_cst_no:
					cust_ids ="\n cust_ids =(SELECT id FROM res_customer WHERE vat='%s' and cst_no='%s' LIMIT 1);" %(str(i.customer_vat_tin),str(i.customer_cst_no))
				if branch_type_temp=='branch_type' :
					stock_id="\n INSERT INTO receive_indent (indent_no,indent_date,transporter, type,delivery_name, source_company, new_delivery_type, delivery_type, customer_name, stock_id, order_number, po_no_sync, po_sync_date, eta_sync, delivery_challan_no, delivery_challan_date, ci_sync_id, form_branch_id, branch_name,state, msg_check, test_state, check_product_serial, reject_check_stn, check_attachment, tag_check,serial_id_check, tag_icon_check, serial_id_icon_check, sync_dispatcher_indent, sync_dispatcher_order, sync_central_indent, sync_central_local_purchase, sync_direct_delivery_dispatcher, sync_direct_delivery_central, branch_stock_transfer_dispatcher, branch_stock_transfer_central, delay_delivery, deliver_percent, labelling, leakage, certificate_quality, company_id, company_name1) VALUES (%s,%s,%s,'internal','direct_delivery',source_ids, '%s', '%s', cust_ids,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s,'intransit', False,'start',False,False, False, False, False, False, True, True,  False, False, False, False, False, False, False, 10, 10, 10, 10, 10, (SELECT company_id FROM res_users WHERE login='admin'), (SELECT name FROM res_company WHERE id=(SELECT company_id FROM res_users WHERE login='admin'))) returning id into stock_id1;" %(("'"+i.origin+"'" if i.origin else 'NULL'),("'"+i.date+"'" if i.date else 'NULL'),("'"+i.transporter.transporter_name+"'" if i.transporter else 'NULL'),(i.delivery_type_char),(i.delivery_type),str(i.stock_id),("'"+i.stock_transfer_no+"'" if i.stock_transfer_no else 'NULL'),("'"+i.stock_transfer_no+"'" if i.stock_transfer_no else 'NULL'),("'"+i.stock_transfer_date+"'" if i.stock_transfer_date else 'NULL'),("'"+i.expected_delivery_time+"'" if i.expected_delivery_time else 'NULL'),("'"+i.delivery_challan_no+"'" if i.delivery_challan_no else 'NULL'),("'"+i.delivery_challan_date+"'" if i.delivery_challan_date else 'NULL'),i.ci_sync_id if i.ci_sync_id else 'NULL',i.form_branch_id if i.form_branch_id else 'NULL','concern_branch_ids' if i.branch_name else 'location')
				else :
					stock_id="\n INSERT INTO receive_indent (indent_no,indent_date,transporter, type,delivery_name, source_company, new_delivery_type, delivery_type, customer_name, stock_id, order_number, po_no_sync, po_sync_date, eta_sync, delivery_challan_no, delivery_challan_date, ci_sync_id, form_branch_id, state, msg_check, test_state, check_product_serial, reject_check_stn, check_attachment, sync_dispatcher_indent, sync_dispatcher_order, sync_central_indent, sync_direct_delivery_dispatcher, sync_direct_delivery_central, branch_stock_transfer_dispatcher, branch_stock_transfer_central, delay_delivery, deliver_percent, labelling, leakage, certificate_quality, company_id, company_name1) VALUES (%s,%s,%s,'internal','direct_delivery',source_ids, '%s', '%s', cust_ids,%s, %s, %s, %s, %s, %s,%s, %s, %s, 'intransit', False,'start','False', False, True, True, False, False, False, False, False, False, 10, 10, 10, 10, 10, (SELECT company_id FROM res_users WHERE login='admin'), (SELECT name FROM res_company WHERE id=(SELECT company_id FROM res_users WHERE login='admin'))) returning id into stock_id1;" %(("'"+i.origin+"'" if i.origin else 'NULL'),("'"+i.date+"'" if i.date else 'NULL'),("'"+i.transporter.transporter_name+"'" if i.transporter else 'NULL'),(i.delivery_type_char),(i.delivery_type),str(i.stock_id),("'"+i.stock_transfer_no+"'" if i.stock_transfer_no else 'NULL'),("'"+i.stock_transfer_no+"'" if i.stock_transfer_no else 'NULL'),("'"+i.stock_transfer_date+"'" if i.stock_transfer_date else 'NULL'),("'"+i.expected_delivery_time+"'" if i.expected_delivery_time else 'NULL'),("'"+i.delivery_challan_no+"'" if i.delivery_challan_no else 'NULL'),("'"+i.delivery_challan_date+"'" if i.delivery_challan_date else 'NULL'),i.ci_sync_id if i.ci_sync_id else 'NULL',i.form_branch_id if i.form_branch_id else 'NULL')
				#stock_id1="\n stock_id1=(SELECT id FROM receive_indent WHERE indent_no='%s' and ci_sync_id='%s' and form_branch_id='%s' );" %(i.origin,i.ci_sync_id,i.form_branch_id)
				sync_str += cust_ids+stock_id
				for k in i.stock_transfer_product :
					variable_status = False
					if k.product_name.type_product=='track_equipment':
					   variable_status = True
					if k.state!='cancel_order_qty':
						prod_id ="\n prod_id =(SELECT id FROM product_product WHERE name_template='%s' LIMIT 1);" %(k.product_name.name).replace("'","''")
						sync_str += prod_id
						if k.product_uom:
							prod_search_d=self.pool.get('product.product').browse(cr,uid,k.product_name.id)
							uom_name=prod_search_d.local_uom_id.name
							product_qty_ids = "\n product_qty_ids=(SELECT id FROM product_uom WHERE name='%s');"%(k.product_uom.name)
							sync_str += product_qty_ids+product_qty_ids
						if k.generic_id:
							generic_id_srch = [('name', '=',k.generic_id.name)] 
							generic_id ="\n generic_id = (SELECT id FROM product_generic_name WHERE name='%s');" %(k.generic_id.name)
							sync_str += generic_id 
						if k.batch.id :
							if branch_type_temp=='branch_type' :
								batch_srch ="\n batch_ids =(SELECT id FROM res_batchnumber WHERE batch_no='%s' AND name=prod_id AND branch_name=%s);"%(k.batch.batch_no,'concern_branch_ids' if i.branch_name else 'location')
							else :
								batch_srch ="\n batch_ids =(SELECT id FROM res_batchnumber WHERE batch_no='%s' AND name=prod_id);"%(k.batch.batch_no)
							ifstr="\n IF batch_ids IS NULL THEN"
							sync_str += batch_srch+ifstr
							if branch_type_temp=='branch_type' :
								batch_id1 ="\n INSERT INTO res_batchnumber (batch_source,name,generic_id,batch_no, manufacturing_date, exp_date, st,distributor, export_price,mrp, uom,product_code,bom, branch_name) VALUES ('direct_delivery', prod_id, generic_id, '%s',%s, %s, %s,0.0,0.0,0.0,product_qty_ids, '%s',0.0,%s);" %(str(k.batch.batch_no),"'"+str(k.batch.manufacturing_date)+"'" if k.batch.manufacturing_date else 'NULL', "'"+str(k.batch.exp_date)+"'" if k.batch.exp_date else 'NULL',str(k.batch.st),str(k.batch.product_code),'concern_branch_ids' if i.branch_name else 'location')
							else :
								batch_id1 ="\n INSERT INTO res_batchnumber (batch_source,name,generic_id,batch_no, manufacturing_date, exp_date, st,distributor, export_price,mrp, uom,product_code,bom) VALUES ('direct_delivery', prod_id, generic_id, '%s',%s, %s, %s,%s,%s,%s,product_qty_ids, '%s',%s);" %(str(k.batch.batch_no),"'"+str(k.batch.manufacturing_date)+"'" if k.batch.manufacturing_date else 'NULL', "'"+str(k.batch.exp_date)+"'" if k.batch.exp_date else 'NULL',str(k.batch.st) if k.batch.st else 0.0 ,str(k.batch.distributor) if k.batch.distributor else 0.0,str(k.batch.export_price) if k.batch.export_price else 0.0,str(k.batch.mrp) if k.batch.mrp else 0.0,str(k.batch.product_code),str(k.batch.bom) if k.batch.bom else 0.0)
							sync_str += batch_id1 + batch_srch +endif
							if branch_type_temp=='branch_type' :
								stock_tran_prod="\n INSERT INTO material_details (indent_id, product_name, generic_id,product_code, batch, product_uom, manufacturing_date, price_unit, local_uom,indented_quantity ,product_qty, series_check_new, branch_name,qty_received) VALUES (stock_id1,prod_id, generic_id, '%s', batch_ids, product_qty_ids, %s,%s,product_qty_ids, %s,%s,%s,%s,%s);" %(str(k.product_code),"'"+str(k.mfg_date)+"'" if k.mfg_date else 'NULL', k.rate if k.rate else 0.0, k.qty_indent,k.quantity,variable_status,'concern_branch_ids' if i.branch_name else 'location',k.quantity)
							else :
								stock_tran_prod="\n INSERT INTO material_details (indent_id, product_name, generic_id,product_code, batch, product_uom, manufacturing_date, price_unit, local_uom,indented_quantity ,product_qty, series_check_new,qty_received) VALUES (stock_id1,prod_id, generic_id, '%s', batch_ids, product_qty_ids, %s,%s,product_qty_ids, %s,%s,%s,%s);" %(str(k.product_code),"'"+str(k.mfg_date)+"'" if k.mfg_date else 'NULL', k.rate if k.rate else 0.0, k.qty_indent,k.quantity,variable_status,k.quantity)
							stock_tran_prod_id="\n stock_tran_prod_id= (SELECT id FROM material_details WHERE indent_id=stock_id1 AND product_name=prod_id AND batch=batch_ids ORDER BY id DESC LIMIT 1);"
							sync_str += stock_tran_prod + stock_tran_prod_id
							if k.serial_line :
								for serials in k.serial_line :
									create_serials_id="\n INSERT INTO transfer_series (line ,series_line,product_code, product_name, product_uom, batch, quantity, serial_name, active_id, serial_check) VALUES (stock_tran_prod_id, stock_tran_prod_id, %s,prod_id, product_qty_ids, batch_ids, %s, %s, %s, %s);" %("'"+str(serials.product_code)+"'" if serials.product_code else 'NULL',str(serials.quantity) if serials.quantity else 'NULL',"'"+serials.serial_no.serial_no+"'" if serials.serial_no.serial_no else 'NULL',serials.active_id if serials.active_id else 'False',serials.serial_check if serials.serial_check else 'False')
									sync_str +=create_serials_id
							if k.notes_one2many:
								for material_notes in k.notes_one2many:
										msg_flag_branch=True
										user_name=material_notes.user_id
										source=material_notes.source.id
										comment=material_notes.comment
										comment_date=material_notes.comment_date
										if material_notes.source:
											source_id="\n source_id=(SELECT id FROM res_company WHERE name='%s' LIMIT 1);" %(material_notes.source.name)
											sync_str += source_id
										notes_line_id="\n INSERT INTO material_details_comment_line(indent_id,user_id, source, comment_date, comment) VALUES (stock_tran_prod_id,%s,source_id,'%s','%s');"%("'"+str(user_name)+"'" if user_name else 'NULL',comment_date,comment)
										msg_unread_ids="\n UPDATE material_details SET msg_check_unread=True,msg_check_read=False WHERE id=stock_tran_prod_id;"
										sync_str += notes_line_id + msg_unread_ids
				if i.notes_one2many :
						msg_flag_branch=True
						for h in i.notes_one2many:
							if h.source:
								source_id ="\n source_id=(SELECT id FROM res_company WHERE name='%s');" %(str(h.source.name))
								sync_str += source_id
							user_sync1="\n INSERT INTO receive_indent_comment_line(receive_indent_id, user_id, state, comment_date, source, comment) VALUES (stock_id1,'%s','%s','%s',source_id,'%s');" %(h.user_name,h.state,h.date,h.name)
							sync_str += user_sync1
				if msg_flag_branch :
					msg_ids="\n UPDATE receive_indent SET msg_check=True WHERE id=stock_id1;"
					sync_str +=msg_ids
					
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
#############################################################################################################
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
					'customer_name':cust_ids if cust_ids else False,
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
										'branch_name':concern_branch_ids[0] if i.branch_name else location[0],
										}
								else:
									batch= {
									'batch_source':'direct_delivery',
									'name':prod_id,
									'generic_id':generic_id[0] if k.generic_id else False,
									'batch_no':k.batch.batch_no if k.batch.batch_no else False,
									'manufacturing_date':k.batch.manufacturing_date if k.batch.manufacturing_date else False,
									'exp_date':k.batch.exp_date if k.batch.exp_date else False,
									'st':k.batch.st if k.batch.st else False,
									'distributor':k.batch.distributor if k.batch.distributor else False,
									'export_price':k.batch.export_price if k.batch.export_price else False,
									'mrp':k.batch.mrp if k.batch.mrp else False,	
									'uom':product_qty_ids[0],
									#'local_uom_id':product_qty_local_ids[0],
									'product_code':k.batch.product_code,
									'bom':k.batch.bom if k.batch.bom else False,
									'branch_name':concern_branch_ids[0] if i.branch_name else location[0],
									}
								batch_id1 = sock.execute(dbname, userid, pwd, 'res.batchnumber', 'create',batch )
						stock_tran_prod = {
							'indent_id':stock_id,
							'product_name':product_ids[0],
							'generic_id':generic_id[0]if generic_id else False,
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
								msg_flag_branch=True
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								source_id=0
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
	def sync_cancel_delivery_order_central_indent(self,cr,uid,ids,context=None):
		if context is None: context = {}
		ci_sync_id = ''
		remark_srch_id = False
		msg_flag=False
		conn_flag=False
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
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_delivery_order_central_indent','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
				######################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Cancel_Delivery_Order_Central_Indent-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION cancel_delivery_order_central_indent() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n ln_ids INT;\n source_id INT;
						\n remark_srch_id INT;  
						
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT cancel_delivery_order_central_indent();\n"
				sync_str+=func_string+declare+var1
				
				for res in self.browse(cr,uid,ids):
					ci_sync_id = res.ci_sync_id
					origin_ids = "\n origin_ids =(select id from stock_picking where id="+str(ci_sync_id)+" and origin='"+str(origin)+"' );"
					ifstr="\n IF origin_ids IS NOT NULL THEN"
					sync_str+= origin_ids + ifstr 
					for ln in res.stock_transfer_product:
						product_ids = "\n product_ids=(select id from product_product where name='"+str((ln.product_name.name).replace("'","''"))+"');"
						ln_ids = "\n ln_ids=(select id from stock_move where product_id=product_ids and picking_id = origin_id);"
						ifstr="\n IF ln_ids IS NOT NULL THEN"
						move_ids = "\n (Update stock_move set state='pending' where id in ln_ids );"
						sync_str+= product_ids + ln_ids + ifstr + move_ids 
						if ln.notes_one2many:
							for material_notes in ln.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								
								if material_notes.source:
									source_id = "\n source_id=(select id from res_company where name='"+str(material_notes.source.name)+"');"
									sync_str+= source_id
								remark_srch_id = "\n remark_srch_id=(select id from stock_move_comment_line where comment='"+str(comment)+"', and user_id='"+str(material_notes.user_id)+"',source=source_id,'"+str(comment_date)+"',ln_ids);"
								
								ifstr ="\n IF remark_srch_id is NULL THEN "
								msg_unread_ids = "\n UPDATE stock_move set msg_check_unread=True ,msg_check_read=False where id in ln_ids"
								notes_line_id = "\n insert into stock_move(indent_id,user_id,source,comment_date,comment) values(ln_ids,"+("'"+str(user_name)+"'" if user_name else 'null')+",source_id,'"+str(comment_date)+"','"+str(comment)+"');"
								sync_str += remark_srch_id + ifstr + msg_unread_ids + notes_line_id + endif
						sync_str += endif			
					if res.notes_one2many:
						for notes in res.notes_one2many:
							if notes.source:
								source_id = "\n source_id=(select id form res_company where name='"+str(notes.source.name)+"');"
								sync_str+=source_id
							remark_srch_id="\n remark_srch_id=(select id from indent_remark where remark=origin_ids and remark_field='"+str(notes.name)+"' and \"user\"='"+str(notes.user_name)+"' and date='"+str(notes.date)+"');"
							ifstr="\n IF remark_srch_id is NULL THEN"
							sync_str += remark_srch_id + ifstr
							notes_line_ids = "\n insert into indent_remark(remark,\"user\",source,date,remark_field) values(origin_ids,'"+str(notes.user_name)+"'" if notes.user_name else 'null'",source_id,'"+str(notes.date)+"','"+str(notes.name)+"');"
							sync_str += notes_line_ids + endif
					msg_ids= "\n (update stock_picking where set msg_check=True where id in origin_ids)"
					sync_str += msg_ids + endif
					
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()		
				#########################################################
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
		if context is None: context = {}
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
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_delivery_order','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
			        #####################################################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Sync_Cancel_Delivery_Order-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION sync_cancel_delivery_order() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n ln_ids INT;\n source_id INT;
						\n remark_srch_id INT; \n msg_unread_ids INT; \n location INT; 
						\n receive_origin_id INT; \n stock_id INT; \n prod_id INT; \n product_qty_ids INT;
						
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT sync_cancel_delivery_order();\n"
				sync_str+=func_string+declare+var1
			        
				origin_ids = "\n origin_ids=(select id form res_indent where id='"+str(form_branch_id)+"' and order_id='"+str(res.origin)+"');"
				ifstr="\n IF origin_ids is NOT NULL THEN"
				sync_str+= origin_ids + ifstr 
				for line in res.stock_transfer_product:
					product_ids = "\n product_ids=(select id from product_product where name='"+str((line.product_name.name).replace("'","''"))+"');"
					prod_ids = "\n prod_ids=(select id from indent_order_line where product_id=product_ids and line_id=origin_ids):"
					ifstr="\n IF prod_ids is NOT NULL THEN"
					sync_str+= product_ids + prod_ids + ifstr
					move_ids="\n UPDATE indent_order_line set state='progress' where id =prod_ids;"
					sync_str+= move_ids
					if line.notes_one2many:
						for material_notes in line.notes_one2many:
							user_name=material_notes.user_id
							source=material_notes.source.id
							comment=material_notes.comment
							comment_date=material_notes.comment_date
							if material_notes.source:
								source_id ="\n source_id =(select id form res_company where name='"+str(material_notes.source.name)+"');"
								sync_str+= source_id
							remark_srch_id="\n remark_srch_id=(select id form indent_order_comment_line where comment='"+str(comment)+"' and user_id='"+str(user_name)+"' and source=source_id and comment_date ='"+str(comment_date)+"' and indent_id=prod_ids );"
							ifstr="IF remark_srch_id is NOT NULL THEN"
							msg_unread_ids="\n UPDATE indent_order_line set msg_check_unread=True and msg_check_read=False where id in(prod_ids);"
							elstr="\n ELSE \n"
							notes_line_id="\n insert into indent_order_comment_line(indent_id,user_id,source,comment_date,comment) values(prod_ids,"+("'"+str(user_name)+"'" if user_name else 'null')+"source_id,'"+str(comment_date)+"','"+str(comment)+"';"   
							sync_str+= remark_srch_id + ifstr + msg_unread_ids + elstr + notes_line_id + endif
					sync_str+=endif			
				if res.notes_one2many:
					for notes in res.notes_one2many:
						if notes.source:
						        source_id ="\n source_id =(select id form res_company where name='"+str(material_notes.source.name)+"');"
						        sync_str+= source_id 
						remark_srch_id="\n remark_srch_id=(select id form indent_comment_line where comment='"+str(comment)+"' and user_id='"+str(user_name)+"' and indent_id=origin_ids and state='"+str(notes.state)+"');"
						
						ifstr="IF remark_srch_id is NOT NULL THEN"
						msg_unread_ids="\n UPDATE indent_comment_line set user_id="+("'"+str(notes.user_name)+"'" if notes.user_name else 'null')+",source=source_id and comment_date='"+str(notes.date)+"' and comment='"+str(notes.name)+"' where id in(remark_srch_id);"
						elstr="\n ELSE \n"
						notes_line_id="\n insert into indent_comment_line(indent_id,user_id,source,comment_date,comment) values(origin_ids,"+("'"+str(user_name)+"'" if user_name else 'null')+"source_id,'"+str(notes.date)+"','"+str(notes.name)+"';"   
						sync_str+=remark_srch_id + ifstr + msg_unread_ids + elstr + notes_line_id + endif
				msg_ids="\n UPDATE res_indent set msg_check=True where id=origin_ids;"
				endif 
						
				receive_origin_ids = "\n receive_origin_id=(select id form receive_indent where indent_no='"+str(res.origin)+"' and order_number='"+str(res.stock_transfer_no)+"');"
				ifstr="\n IF receive_origin_id is NOT NULL THEN"
				
				recieve_state_ids="\n UPDATE receive_indent set state='cancel' where id=receive_origin_ids;"
				sync_str+= msg_ids + endif + receive_origin_ids + ifstr + recieve_state_ids 
				if res.notes_one2many:
					for notes in res.notes_one2many:
						if notes.source:
						        source_id="\n source_id=(select id form res_company where name='"+(notes.source.name)+"');"
						        sync_str+= source_id 
						remark_srch_id="\n remark_srch_id=(select id from receive_indent_comment_line where receive_indent_id=receive_indent_ids and comment='"+str(notes.name)+"' and user_id='"+str(notes.user_name)+"' and state='"+str(notes.state)+"');"
						ifstr="\n IF remark_srch_id is NOT NULL THEN"
						notes_line_id="\n UPDATE receive_indent_comment_line set user_id="+("'"+str(notes.user_name)+"'" if notes.user_name else 'null')+",source=source_id,coment_date='"+str(notes.date)+"',comment='"+str(notes.name)+"' where id in remark_srch_id ;"
						elstr="\n ELSE \n "
						notes_line_id_new ="\n insert into receive_indent_comment_line(receive_indent_id,user_id,source,comment_date,comment) values(receive_indent_id,"+("'"+str(notes.user_name)+"'" if notes.user_name else 'null')+",source,coment_date='"+str(notes.date)+"',comment='"+str(notes.name)+"');"
						sync_str+=remark_srch_id + ifstr + notes_line_id + elstr + notes_line_id_new + endif
						
				if res.stock_transfer_product:
						for ln in res.stock_transfer_product:
							product_ids="\n product_ids=(select id from product_product where name='"+str((ln.product_name.name).replace("'","''"))+"');"
							ln_ids="\n ln_ids=(select id from material_details where product_name=prouct_ids and indent_id=receive_origin_ids );"
							ifstr="\n IF ln_ids is NOT NULL THEN"
							sync_str+= product_ids + ln_ids + ifstr 
							if ln.notes_one2many:
								for material_notes in ln.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									if material_notes.source:
										source_id="\n source_id=(select id from res_company  where name='"+str(material_notes.source.name)+"');"
										sync_str+= source_id
									remark_srch_id="\n remark_srch_id=(select id from material_details_comment_line where comment='"+str(comment)+"' and user_id='"+str(user_name)+"' and source=source_id and comment_date='"+str(comment_date)+"' and indent_id=ln_ids);"
									ifstr="\n IF remark_srch_id is NULl THEN"
									msg_unread_ids="\n UPDATE material_details set msg_check_unread=True,msg_check_read=False where id=ln_ids; "
									notes_line_id="\n insert into materiak_details_comment_line (indent_id,user_id,source,comment_date,comment) values(ln_ids,"+("'"+str(user_name)+"'" if user_name else 'null')+",source_id,'"+str(comment_date)+"','"+str(comment)+"');"
									sync_str+=remark_srch_id + ifstr + msg_unread_ids + notes_line_id + endif
									sync_str+=endif 
				msg_ids="\n UPDATE receive_indent set msg_check=True where id in origin_ids;"
				sync_str+=msg_ids + endif 
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
			        #################################################################################################
			        
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


	def sync_cancel_packlist_central_indent(self,cr,uid,ids,context=None):
		if context is None: context = {}
		ci_sync_id = ''
		form_branch_id = ''
		origin = ''
		remark_srch_id = False
		msg_flag=False
		conn_flag=False
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
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_packlist_central_indent','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})	
				###############################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Sync_Cancel_Packlist_Central_Indent-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION sync_cancel_packlist_central_indent() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n ln_ids INT;\n source_id INT;
						\n remark_srch_id INT; \n msg_unread_ids INT; \n location INT; 
						
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT sync_cancel_packlist_central_indent();\n"
				sync_str+=func_string+declare+var1
				
				origin_ids ="\n origin_ids=(select id from stock_picking where id='"+str(ci_sync_id)+"' and '"+str(origin)+"');"
				ifstr="\n IF origin_ids is NOT NULL THEN"
				sync_str+= origin_ids + ifstr 
				for res in self.browse(cr,uid,ids):
					for ln in res.stock_transfer_product:
						product_ids ="\n product_ids=(select id from prodcut_product where name='"+str(ln.product_name.name)+"');"
						ln_ids = "\n ln_ids=(select id form stock_move product_id=product_ids and picking_id=origin_ids);"
						ifstr="\n IF ln_ids is NOT NULL THEN"
						move_ids="\n UPDATE stock_move set state='view_order' where id in (ln_ids);"
						sync_str+= product_ids + ln_ids + ifstr + move_ids + endif
						if ln.notes_one2many:
							for material_notes in ln.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								if material_notes.source:
									source_id="\n source_id=(select id from res_company where name='"+str(material_notes.source.name)+"');"
									sync_str+= source_id 

								remark_srch_id=" \n remark_srch_id=(select id form stock_move_comment_line where comment='"+str(comment)+"' and user_id='"+str(user_name)+"' and source=source_id and comment_date='"+str(comment_date)+"' and indent_id=ln_ids);"
								ifstr="\n IF remark_srch_id is NULL THEN"
								msg_unread_ids="\n UPDATE stock_move set msg_check_unread=True,msg_check_read=False where id in (ln_ids);"
								elstr="\n ELSE \n "
								notes_line_id ="\n insert into stock_move_comment_line('indent_id,user_id,source,comment_date,comment') values(ln_ids,"+("'"+str(user_name)+"'" if user_name else 'null')+",source_id,'"+str(comment_date)+"','"+str(comment)+"');"
								sync_str+=remark_srch_id +ifstr +msg_unread_ids +elstr+notes_line_id +endif 
						sync_str+= endif
					if res.notes_one2many:
                                                for notes in res.notes_one2many:
                                                        if notes.source:
                                                                source_id="\n source_id=(select id from res_company where name='"+str(notes.source.name)+"');"
                                                                sync_str+= source_id
                                                        remark_srch_id=" \n remark_srch_id=(select id form indent_remark where remark=origin_ids and remark_field='"+str(notes.name)+"' and user='"+str(notes.user_name)+"' and date='"+str(notes.date)+"');"
                                                        ifstr="\n IF remark_srch_id is NULL THEN"

                                                        notes_line_id ="\n UPDATE indent_remark set \"user\"  ="+("'"+(notes.user_name)+"'" if notes.user_name else 'null')+",source=source_id,date='"+str(notes.date)+"',remark_field='"+(notes.name)+"' where id in (remark_srch_id);"
                                                        elstr="\n ELSE \n "	
                                                        notes_line_ids="\n insert into indent_remark(remark,\"user\",source,date,remark_field) values(origin_ids,"+("'"+str(notes.user_name)+"'" if notes.user_name else 'null')+",source_id,'"+str(notes.date)+"','"+str(notes.name)+"' ;"
                                                        sync_str+= remark_srch_id +ifstr + notes_line_id + elstr + notes_line_ids + endif
				msg_ids= "\n UPDATE stock_picking set msg_check=True where id in (origin_ids);"
				sync_str+= msg_ids + endif
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
				################################################################################		
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
		if context is None: context = {}
		remark_srch_id = False
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag = False
		conn_flag = False
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
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_packlist','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
				##########################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Sync_Cancel_Packlist-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('/home/nevpro')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('/home/nevpro')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
					
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION sync_cancel_packlist() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n ln_ids INT;\n source_id INT;
						\n remark_srch_id INT; \n msg_unread_ids INT; \n location INT; 
						
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT sync_cancel_packlist();\n"
				sync_str+=func_string+declare+var1
				origin_ids = "\n origin_ids=(select id from res_indent where id=form_branch_id and order_id='"+str(res.origin)+"');"
				ifstr="\n IF origin_ids is NOT NULL THEN"
				sync_str+= origin_ids+ ifstr
				for line in res.stock_transfer_product:
					product_ids = "\n product_ids=(select id form product_product where name='"+str(line.product_name.name)+"');"
                                        prod_ids = "\n product_ids=(select id from indent_order_line product_id=product_ids and line_id=origin_ids);"
                                        ifstr="IF prod_ids is NOT NULL THEN"
					move_ids="\n UPDATE indent_order_line set state='view_order' where id in (prod_ids);"
					sync_str+= product_ids  + prod_ids + ifstr + move_ids
					if line.notes_one2many:
						for material_notes in line.notes_one2many:
							user_name=material_notes.user_id
							source=material_notes.source.id
							comment=material_notes.comment
							comment_date=material_notes.comment_date
							if material_notes.source:
								source_id="\n source_id=(select id from res_company set name='"+str(material_notes.source.name)+"');"
								sync_str+= source_id 
							remark_srch_id="\m remark_srch_id=(select id form indent_order_comment_line where comment='"+str(comment)+"' and user_id='"+str(user_name)+"' and source=source_id and comment_date='"+str(comment_date)+"' and indent_id=prod_ids);"
							ifstr="\n if remark_srch_id is NULL THEN"
							msg_unread_ids="\n UPDATE indent_order_line set msg_check_unread=True , msg_check_read=False where id=prod_ids ; "
							elstr="\n ELSE \n "
							notes_line_id = "\n insert into indent_order_comment_line(indent_id,user_id,source,comment_date,comment) values(prod_ids,"+("'"+str(user_name)+"'" if user_name else 'null')+",source_id,'"+str(comment_date)+"','"+str(comment)+"')"
							sync_str += remark_srch_id + ifstr + msg_unread_ids + elstr + notes_line_id + endif
							sync_str += endif

				if res.notes_one2many:
					for notes in res.notes_one2many:
						if notes.source:
						      source_id="\n source_id=(select id from res_company where name='"+str(notes.source.name)+"');"
						      sync_str += source_id
						remark_srch_id = "\n remark_srch_id=(select id from indent_comment_line where indent_id =origin_ids and comment='"+str(notes.name)+"' and user_id='"+str(notes.user_name)+"' and comment_date='"+str(notes.date)+"';"
						ifstr="\n if remark_srch_id is NOT NULL THEN"
						notes_line_id="\n UPDATE indent_comment_line set user_id="+("'"+str(notes.user_name)+"'" if notes.user_name else 'null')+",source=source_id and comment_date='"+str(notes.date)+"' and comment='"+str(notes.name)+"' where id in(remark_srch_id);"
						elstr="\n ELSE \n"
						notes_line_id_new = "\n insert into indent_comment_line(indent_id,user_id,soource,comment_date,comment) values(origin_ids,"+("'"+str(notes.user_name)+"'" if notes.user_name else 'null')+",source_id,'"+str(notes.date)+"','"+str(notes.name)+"';"
						sync_str+=remark_srch_id + ifstr+ notes_line_id + elstr + notes_line_id_new + endif

				msg_ids="\n UPDATE res_indent set masg_check=True where id in (origin_ids);"
			        sync_str+= msg_ids + endif
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
				##########################################################################			
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

	def sync_cancel_stock_transfer(self,cr,uid,ids,context=None):
		if context is None: context = {}
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
			userid = ''
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			city_ids=''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_stock_transfer','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
					
				#################3#######################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Cancel_Stock_Transfer-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION cancel_stock_transfer() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" delivery_location_ids INT;\n create_branch_stock_transfer INT;\n source_ids INT;\n prod_ids INT;
						\n create_stock_transfer_product INT; 
						 
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT cancel_stock_transfer();\n"
				sync_str+=func_string+declare+var1
				
				for res in self.browse(cr,uid,ids):
					if res.delivery_location: #delivery_location  Contact person remain
						delivery_location_ids = "\n delivery_location_ids=(select id from res_company where name='"+str(res.delivery_location.name)+"');"
						
					if res.delivery_location.state_id:
						state_ids="\n (select id from state_name where name='"+str(res.delivery_location.name)+"')"
						
					if res.source: 
						source_ids = "\n source_ids=(select id from rs_company where name='"+str(res.source.name)+"');"

					if res.delivery_location.city_id:
						city_ids = "\n (select id from city_name where name1="+str(res.delivery_location.city_id.name1)+")"

					create_branch_stock_transfer ="\n insert into warehouse_stock_transfer(contact_person,delivery_location, stock_transfer_no, stock_transfer_date_new,delivery_type,contact_no,delivery_address,total_amount,origin,date,packlist_no1,packlist_date1,total_weight,mode_transport,transporter,driver_name,lr_no,delivery_date,estimated_value,person_name,vehicle_no,mobile_no,lr_date,expected_delivery_time,excise_invoice_no,packlist_no,stock_transfer_note_no,delivery_challan_no,stn_remark,delivery_challan_remark,excise_invoice_date,packlist_date,stock_transfer_date,delivery_challan_date,source,indent_age,state) values("+str(res.contact_person)+"',delivery_location_ids,'"+str(res.stock_transfer_no)+"','"+str(res.stock_transfer_date_new if res.stock_transfer_date_new else 'null')+"','"+str(res.delivery_type)+"','"+str(res.contact_no)+"','"+str(res.delivery_address)+"','"+str(res.total_amount)+"','"+str( res.origin)+"','"+str( res.date)+"','"+str(res.packlist_no1 if res.packlist_no1 else 'null')+"',"+("'"+str( res.packlist_date1)+"'" if res.packlist_date1 else 'null')+",'"+str( res.total_weight if res.total_weight else 'null')+"','"+str( res.mode_transport if res.mode_transport else 'null')+"','"+str( res.transporter.transporter_name if  res.transporter else 'null')+"','"+str( res.driver_name if res.driver_name else 'null')+"','"+str( res.lr_no if res.lr_no else 'null')+"',"+("'"+str(res.delivery_date)+"'" if res.delivery_date else 'null')+",'"+str( res.estimated_value if res.estimated_value else 'null')+"','"+str( res.person_name if res.person_name else 'null')+"','"+str( res.vehicle_no if res.vehicle_no else 'null')+"','"+str( res.mobile_no if res.mobile_no else 'null')+"','"+str( res.lr_date if res.lr_date else 'null')+"','"+str( res.expected_delivery_time if res.expected_delivery_time else 'null')+"','"+str( res.excise_invoice_no if res.excise_invoice_no  else 'null')+"','"+str( res.packlist_no if res.packlist_no else 'null')+"','"+str( res.stock_transfer_note_no if res.stock_transfer_note_no else 'null')+"','" +str( res.delivery_challan_no if res.delivery_challan_no else 'null')+"','"+str( res.stn_remark if res.stn_remark else 'null')+"','" +str( res.delivery_challan_remark if res.delivery_challan_remark else 'null')+"','"+str( res.excise_invoice_date if res.excise_invoice_date else 'null')+"','"+str( res.packlist_date if res.packlist_date else 'null')+"','"+str( res.stock_transfer_date if res.stock_transfer_date else 'null')+"','"+str( res.delivery_challan_date if res.delivery_challan_date else 'null')+"',source_ids,'"+str(res.intent_age if res.intent_age else 0.00)+"','"+str(res.state)+"') returning id into create_branch_stock_transfer;"
					
					sync_str+= delivery_location_ids + state_ids + source_ids + city_ids
					
					for line in res.stock_transfer_product:
						create_stock_transfer_product = "\n insert into product_transfer1(prod_id,product_category, product_code,product_name, product_uom, available_quantity,rate,quantity,mfg_date,amount,batch) values(create_branch_stock_transfer,'"+str(line.product_category.name if line.product_category else '')+"','"+str(line.product_code if line.product_code else '')+"','"+str(line.product_name.name if line.product_name else '')+"','"+str(line.product_uom.name if line.product_uom else '')+"','" +str(line.available_quantity if line.available_quantity else '')+"','" +str(line.rate if line.rate else 'null')+"','"+str(line.quantity if line.quantity else '')+"','" +str(line.mfg_date if line.mfg_date else 'null')+"','"+str(line.amount if line.amount else '')+"','"+str(line.batch.batch_no if line.batch else '')+"') returning id into create_stock_transfer_product ;"
						sync_str+= create_stock_transfer_product
						
					if res.notes_one2many:
						for pick in res.notes_one2many:
							add ="\n insert into stock_transfer_remarks1 (stock_transfer_id,user_name1,name1,source1,state)  values(create_stock_transfer_product,'"+str(pick.user_name)+"','"+str(pick.date)+"','"+str(pick.name)+"','"+str(pick.source.name)+"','"+str(pick.state)+"');"
							sync_str+= add
							
				with(open(filename,'a')) as f :
						f.write(sync_str)
						f.write(ret)
						f.write(final)
						f.write(fun_call)
						f.close()	
				#########################################################
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
		if context is None: context = {}
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

		branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
		for branch_id in self.pool.get('res.company').browse(cr,uid,branch_type):
			vpn_ip_addr = branch_id.vpn_ip_address
			port = branch_id.port
			dbname = branch_id.dbname
			pwd = branch_id.pwd
			user_name = str(branch_id.user_name.login)
			userid = ''
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
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
		if context is None: context = {}
		remark_srch_id = False
		source_name=''
		ci_sync_id = ''
		form_branch_id = ''
		msg_flag=False
		conn_flag=False
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
					# offline_obj=self.pool.get('offline.sync')
					# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					# if not offline_sync_sequence:
					# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_order_central','error_log':Err,})
					# else:
					# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
					# 	
						#########################
					con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Cancel_Order_Central-'+str(date)+'_'+str(time_cur)+'.sql'
					sync_str=''
					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
					directory_name =str(os.path.expanduser('~')+'/indent_sync/')
					if not os.path.exists(directory_name):
						os.makedirs(directory_name)
					d = os.path.dirname(directory_name)
					func_string ="\n\n CREATE OR REPLACE FUNCTION cancel_order_central() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
					declare=" DECLARE \n "
					var1=""" origin_ids INT;\n ln_ids INT;\n source_ids INT;\n prod_ids INT;
							\n remark_srch_id INT; 
							 
							\n  BEGIN \n """
					endif="\n\n END IF; \n"
					ret="\n RETURN 1;\n"
					elsestr="\n ELSE \n"
					final="\nEND; \n $$;\n"
					fun_call="\n SELECT cancel_order_central();\n"
					sync_str+=func_string+declare+var1
					
					origin_ids = "\n origin_ids =(select id from stock_picking where id="+str(ci_sync_id)+" and origin="+k.origin+");"
					ifstr="\n IF origin_ids is NOT NULL THEN"
					
					ln_ids = "\n ln_ids=(select id from stock_move where picking_id in origin_ids and product_id in (select id from product_product where name='"+str((k.product_name.name).replace("'","''"))+"'));"
					sync_str+= ifstr + ln_ids

					ifstr="\n IF ln_ids is NOT NULL THEN"
					move_ids= "\n UPDATE stock_move set state='pending' where id in ln_ids ;"
					sync_str+= ifstr + move_ids
					if k.notes_one2many:
						for material_notes in k.notes_one2many:
							user_name=material_notes.user_id
							source=material_notes.source.id
							comment=material_notes.comment
							comment_date=material_notes.comment_date

							if material_notes.source:
								source_ids = "\n source_ids=(select id form res_company where name='"+str(material_notes.source.name)+"');"
								sync_str+= source_ids
							
							remark_srch_id= "\n remark_srch_id=(select id from stock_move_comment_line where comment='"+str(comment)+"' and user_id='"+str(user_name)+"' and comment_date='"+str(comment_date)+"' and source=source_ids and indent_id=ln_ids);"
							
							ifstr="\n IF remark_srch_id is NULL THEN"
							msg_unread_ids = "\n UPDATE stock_move set msg_check_unread=True,msg_check_read=False ;"
							
							notes_line_id = "\n insert into stock_move_comment_line(indent_id,user_id,source,comment_date,comment) values (ln_ids,"+user_name if user_name else ''+",source_id,'"+str(comment_date)+"', and '"+str(comment)+"');"
							sync_str+= remark_srch_id+ ifstr + msg_unread_ids + notes_line_id + endif
					sync_str+= endif 
					
					for st_id in self.pool.get('stock.transfer').browse(cr,uid,[k.prod_id.id]):
						if st_id.notes_one2many:
							for notes in st_id.notes_one2many:
								if notes.source:
									source_ids="\n source_ids=(select id from res_company where name='"+str(notes.source.name)+"');"
																		
								remark_srch_id= "\n remark_srch_id=(select id from indent_remark where remark_field='"+str(notes.name)+"' and user='"+str(notes.user_name)+"' and source in source_ids and date='"+str(notes.date)+"' and remark in origin);"
								
								ifstr="\n IF remark_srch_id is NULL THEN"
								
								notes_line_id = "\n insert into stock_move_comment_line(remark,\"user\",source,date,remark_field) values (origin,"+notes.user_name if notes.user_name else ''+",source_id,'"+str(notes.date)+"', and '"+str(notes.name)+"');"
								sync_str+= remark_srch_id +ifstr + notes_line_id + endif
								
					msg_ids = "\n UPDATE stock_picking set msg_check=True where id in origin;"
					sync_str+= msg_ids + endif
					##############################
					with(open(filename,'a')) as f :
						f.write(sync_str)
						f.write(ret)
						f.write(final)
						f.write(fun_call)
						f.close()
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
										msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',ln_ids ,msg_unread)
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
		if context is None: context = {}
		ci_sync_id = ''
		form_branch_id = ''
		delivery_location=0
		msg_flag_branch=False
		conn_flag=False
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
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':delivery_location.id,'srch_condn':False,'form_id':ids[0],'func_model':'sync_cancel_order','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
					
				#########################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'Cancel_Order-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION cancel_order() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n prod_ids INT;\n source_ids INT;\n move_ids INT;
						\n remark_srch_id INT; 
						 
						\n  BEGIN \n """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT cancel_order();\n"
				sync_str+=func_string+declare+var1
				
				origin_ids = "\n origin_ids=(select id from res_indent where order_id = "+str(res.origin)+");"
				ifstr="\n IF origin_ids is NOT NULL THEN"
				prod_ids = "\n prod_ids=(select id from indent_order_line where line_id in origin_ids and product_id in(select id from product_product where name='"+str((res.product_name.name).replace("'","''"))+"'));"
				
				sync_str+= origin_ids + ifstr + prod_ids
				ifstr="\n IF prod_ids is NOT NULL THEN"
				
				move_ids= "\n update indent_order_line where set state='progress' where id in prod_ids;"
				sync_str+= ifstr + move_ids
				
				if res.notes_one2many:
					for material_notes in res.notes_one2many:
						user_name=material_notes.user_id
						source=material_notes.source.id
						comment=material_notes.comment
						comment_date=material_notes.comment_date

						if material_notes.source:
							source_ids="\n source_ids=(select id from res_company where name="+str(material_notes.source.name)+")"
							sync_str+=  source_ids
						remark_srch_id= "\n remark_srch_id=(select id from indent_order_comment_line where comment='"+str(comment)+"' and user_id='"+str(user_name)+"' and comment_date='"+str(comment_date)+"' and source=source_ids and indent_id=prod_ids);"
						
						ifstr="\n IF remark_srch_id is NULL THEN"
						msg_unread_ids = "\n UPDATE indent_order_line set msg_check_unread=True,msg_check_read=False ;"
						
						notes_line_id = "\n insert into indent_order_comment_line(indent_id,user_id,source,comment_date,comment) values (ln_ids,"+user_name if user_name else ''+",source_id,'"+str(comment_date)+"', and '"+str(comment)+"');"
						sync_str+= remark_srch_id +  ifstr+ msg_unread_ids + notes_line_id + endif
						
				sync_str+= endif		
				for st_id in self.pool.get('stock.transfer').browse(cr,uid,[res.prod_id.id]):
					if st_id.notes_one2many:
						for notes in st_id.notes_one2many:
							if notes.source:
								source_ids="\n source_ids=(select id from res_company where name='"+str(notes.source.name)+"');"
								sync_str+=  source_ids
							remark_srch_id= "\n remark_srch_id=(select id from indent_comment_line where remark_field='"+str(notes.name)+"' and user='"+str(notes.user_name)+"' and source in source_ids and date='"+str(notes.date)+"' and remark in origin);"
							
							ifstr="\n IF remark_srch_id is NULL THEN"
	
							notes_line_id = "\n insert into stock_move_comment_line(remark,user_id,source,comment_date,comment) values (origin,"+notes.user_name if notes.user_name else ''+",source_id,'"+str(notes.date)+"', and '"+str(notes.name)+"');"
							sync_str+= remark_srch_id +  ifstr+ notes_line_id + endif

				msg_ids = "\n UPDATE res_indent set msg_check=True where id in origin;"
				sync_str+= msg_ids + endif 
				#######################################
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
					
			sock = xmlrpclib.ServerProxy(obj)
			if conn_flag == False:
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
		if context is None: context = {}
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
										msg_unread_ids= sock.execute(dbname, userid, pwd, 'indent.order.line', 'write',code_id,msg_unread)
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
		if context is None: context = {}
		conn_flag = False
		for i in self.browse(cr,uid,ids):
			branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
			#Sync Code	
			for branch_id_new in self.pool.get('res.company').browse(cr,uid,branch_type):
				dbname = branch_id_new.dbname
				pwd = branch_id_new.pwd
				userid = ''
				user_name = str(branch_id_new.user_name.login)
				time_cur = time.strftime("%H%M%S")
				date = time.strftime('%Y-%m-%d%H%M%S')
				log = ('http://%s:%s/xmlrpc/common')%(branch_id_new.vpn_ip_address,branch_id_new.port)
				obj = ('http://%s:%s/xmlrpc/object')%(branch_id_new.vpn_ip_address,branch_id_new.port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					raise
					userid = sock_common.login(dbname, user_name, pwd)
				except Exception as Err:
					# offline_obj=self.pool.get('offline.sync')
					# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					# if not offline_sync_sequence:
					# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':i,'error_log':Err,})
					# else:
					# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
						
				##########################################
					con_cat = dbname+"-"+ branch_id_new.vpn_ip_address+"-"+'generate_grn-'+str(date)+'_'+str(time_cur)+'.sql'
					sync_str=''
					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
					directory_name =str(os.path.expanduser('~')+'/indent_sync/')
					if not os.path.exists(directory_name):
						os.makedirs(directory_name)
					d = os.path.dirname(directory_name)
					func_string ="\n\n CREATE OR REPLACE FUNCTION generate_grn() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
					declare=" DECLARE \n "
					var1=""" reason_ids INT;\n product_ids INT;\n product_uom_ids INT;\n generic_ids INT ;
							\n company_ids INT; \n remark_srch_id INT;
							\n  BEGIN \n """
					endif="\n\n END IF; \n"
					ret="\n RETURN 1;\n"
					elsestr="\n ELSE \n"
					final="\nEND; \n $$;\n"
					fun_call="\n SELECT generate_grn();\n"
					sync_str+=func_string+declare+var1
					
					if i.product_name.id:
                                            product_ids = "\n product_ids=(select id from product_product where name='"+str((i.product_name.name).replace("'","''"))+"');"
                                            product_uom_ids = "\n product_uom_ids=(select id from product_uom where name='"+str(i.product_name.uom_id.name)+"');"
                                            sync_str+= product_ids + product_uom_ids
                                        if i.generic_id:	
                                            generic_ids = "\n generic_ids=(select id from product_generic_name where name='"+str(i.generic_id.name)+"');"
                                            sync_str+= generic_ids
                                            
                                        if i.reason.id:
                                            reason_ids = "\n reason_ids=(select id from adjustment_reason where name='"+str(i.reason.name)+"');"
                                            ifstr="\n IF reason_ids is NOT NULL THEN"
                                            reason_id = "\n (insert into adjustment_reason (name,action) values('"+str(i.reason.name)+"','"+str(i.reason.action)+"');"
                                            endif
	                                    sync_str+= reason_ids + ifstr + reason_id + endif
	                                    
                                        total_amount_req = 0.0
                                        if i.Batch.id:
                                            total_amount_req = float(i.adj_stock)*float(i.Batch.st)

                                        if i.company_id:
                                            company_ids = "\n company_ids=(select id from res_company where name ='"+str(i.company_id.name)+"' );"			
                                            sync_str += company_ids
                                            
                                        indent_branch="\n insert into critical_adjustment(sam_date,product_name,generic_id,reason,product_code,book_stock,adj_stock,bal_stock,ammount,notes,category,batch_no,batch_serial_no,location,product_uom,source) values("+str(i.sam_no)+",'"+str(i.sam_date)+"',product_ids,generic_id,reason_ids,'"+str(i.product_code)+"','"+str(i.book_stock)+"','"+str(i.adj_stock)+"','"+str(i.bal_stock)+"',"+str(total_amount_req)+",'"+str(i.notes)+"','"+str(i.category)+"','"+str(i.Batch.batch_no)+"'"if i.Batch.id else 'null'+",'"+str(i.serial_no.serial_no)+"'" if i.serial_no.serial_no else 'null'+",'"+str(i.company_id.name)+"'" if i.company_id.name else 'null'+",product_uom_ids,company_ids);"
                                        sync_str += indent_branch
                                        
                                        with open(filename,'a') as f:
			                        f.write(sync_str)
			                        f.close()
                                        #########################################
				sock = xmlrpclib.ServerProxy(obj)
				if conn_flag == False:
				    if i.product_name.id:
					    product_id_srch = [('name', '=',i.product_name.name)]
					    product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_id_srch)

					    product_uom_srch = [('name','=',i.product_name.uom_id.name)]
					    product_uom_ids = sock.execute(dbname, userid, pwd, 'product.uom', 'search', product_uom_srch)

				    if i.generic_id:	
					    generic_id_srch = [('name', '=',i.generic_id.name)]
					    generic_id = sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_id_srch)

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
							    'generic_id':generic_id[0] if i.generic_id else False,
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
		if context is None: context = {}
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
				time_cur = time.strftime("%H%M%S")
				date = time.strftime('%Y-%m-%d%H%M%S')
				username = user_name 
				pwd = pwd    
				dbname = dbname
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					raise
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					# offline_obj=self.pool.get('offline.sync')
					# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_flag = True
					# if not offline_sync_sequence:
					# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':brw,'error_log':Err,})
					# else:
					# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
######################################################################
					con_cat = dbname+"-"+vpn_ip_addr+"-"+'raise_indent-'+str(date)+'_'+str(time_cur)+'.sql'
					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
					directory_name = str(os.path.expanduser('~')+'/indent_sync/')
					if not os.path.exists(directory_name):
						os.makedirs(directory_name)
					d = os.path.dirname(directory_name)
					company_ids="(SELECT id FROM res_company WHERE name='%s' LIMIT 1)" %(str(brw.company_id.name)) if brw.company_id.name else 'NULL'
					branch_ids ="(SELECT id FROM res_company WHERE name='%s' LIMIT 1)" %(str(brw.branch_name.name) if brw.branch_name.name else brw.company_id.name)
					state_ids = "(SELECT id FROM state_name WHERE name='%s' LIMIT 1)" %(str(brw.company_id.state_id.name)) if brw.company_id.state_id.name else 'NULL'
					vat_tin=''
					cst_tin=''
					search_customer = ''
					pan_no=''
					sync_str=''
					if brw.customer_name:
						for cust in self.pool.get('res.customer').browse(cr,uid,[brw.customer_name.id]):
							vat_tin=cust.vat
							cst_tin=cust.cst_no
							pan_no=cust.pan_no if cust.pan_no else 'NULL'
							search_customer = cust.name
					indent_branch ="\n INSERT INTO stock_picking (origin,company_id,contact_person,date,indent_type,contact_no,delivery_address,customer_name,dispatcher_state,customer_vat_tin,customer_cst_no,branch_name,msg_check,hide_process,test_state,state,move_type,type,invoice_state,source_company,form_branch_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'Unassigned',%s,%s,%s,False,True,False,'draft','direct','in','none',%s,%s);"%("'"+str(brw.order_id)+"'" if brw.order_id else 'NULL',company_ids,"'"+str(brw.contact_person_new.name)+"'" if brw.contact_person_new.name else 'NULL',"'"+str(brw.order_date)+"'" if brw.order_date else 'NULL' ,"'"+str(brw.indent_type)+"'" if brw.indent_type else 'NULL',str(brw.contact_no) if brw.contact_no else 'NULL',"'"+str(brw.delivery_address)+"'" if brw.delivery_address else 'NULL' ,"'"+search_customer+"'" if search_customer else 'NULL' ,"'"+vat_tin+"'" if vat_tin else 'NULL',"'"+cst_tin+"'" if cst_tin else 'NULL',branch_ids,str(branch_ids),str(form_new_id) if form_new_id else 'NULL')
					sync_str+=indent_branch
					#with open(filename,'a') as f:
					#	f.write(indent_branch)
					#	f.close()
					
					search_indent_branch_id="(SELECT id from stock_picking where origin='"+str(brw.order_id)+"' AND form_branch_id ='"+str(form_new_id)+"' LIMIT 1)"
					for line in brw.order_line:
						prod_uom=prod_uom_cat=uom_id=product_id=product_verticals=product_categs=prod_category=prod_generic_id='NULL'
						date = time.strftime('%Y-%m-%d %H:%M:%S')
						date_expected = time.strftime('%Y-%m-%d %H:%M:%S')
						prod_uom_cat = "(SELECT id from product_uom_categ where name='"+str(line.product_id.uom_id.category_id.name)+"' LIMIT 1)"
						sql_uom_id = line.product_id.uom_id.id if line.product_id.uom_id else "NULL" 
						prod_uom = "(SELECT id FROM product_uom WHERE name ='%s' LIMIT 1)" %(str(line.product_id.uom_id.name))
						prod_id = "(SELECT id from product_product where name_template='"+str((line.product_id.name).replace("'","''"))+"' LIMIT 1)"
						generic_id = "(SELECT id from product_generic_name where name='"+str(line.generic_id.name)+"' LIMIT 1)"
						prod_vertical = "(SELECT id from product_vertical where name='"+str(line.product_id.product_vertical.name)+"' LIMIT 1)"
						prod_category = "(SELECT id from product_category where name='"+str(line.product_category.name)+"' LIMIT 1)"

						pick_line = "\n INSERT INTO stock_move (state,picking_id,product_id,generic_id,product_uom,product_category,product_code,product_qty,indented_qty,delivery_rate,amount,company_id,date_expected,date) VALUES ('draft',"+search_indent_branch_id+","+prod_id+","+generic_id+","+prod_uom+","+prod_category+",'"+str(line.product_code)+"',"+str(line.product_uom_qty)+","+str(line.product_uom_qty)+","+str(line.price_unit)+","+str(line.total)+","+company_ids+",'"+date_expected+"','"+date+"');"
						sync_str+=pick_line
						#with open(filename,'a') as f:
							#f.write(pick_line)
							#f.close()
						if line.notes_one2many:
							for material_notes in line.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								move_ids = "(SELECT id from stock_move where picking_id in "+search_indent_branch_id+" LIMIT 1)"

								source_id = "(SELECT id FROM res_company WHERE name='%s')"%(str(material_notes.source.name))
								material_notes_line="\n INSERT INTO stock_move_comment_line (indent_id,user_id,source,comment_date,comment) VALUES (%s,'%s',%s,'%s','%s');"%(str(move_ids),str(user_name),str(source_id),str(comment_date),str(comment))
								msg_flag = True
								update_msg="\n UPDATE stock_move set msg_check_unread=True,msg_check_read=False where id ="+str(move_ids)+";"
								sync_str+=material_notes_line+update_msg
								#with open(filename,'a') as f:
									#f.write(material_notes_line)
									#f.write(update_msg)
									#f.close()			
					if brw.comment_line:
						msg_flag = True
						for notes in brw.comment_line:
							source_id="(SELECT id FROM res_company WHERE name='%s')"%(str(notes.source.name))
							notes_line_id="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (%s,'%s',%s,'%s','%s');"%(str(search_indent_branch_id),str(notes.user_id),str(source_id),str(notes.comment_date),str(notes.comment))
							update_msg="\n UPDATE stock_picking set msg_check=True where id ="+str(search_indent_branch_id)+";"
							sync_str+=notes_line_id+update_msg
					with open(filename,'a') as f:
						f.write(sync_str)
						#f.write(update_msg)
						f.close()
######################################################################################################################
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
					pan_no=''
					if brw.customer_name:
						for cust in self.pool.get('res.customer').browse(cr,uid,[brw.customer_name.id]):
							vat_tin=cust.vat
							cst_tin=cust.cst_no
							pan_no=cust.pan_no
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
							'customer_pan_no':pan_no,
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
						for notes in brw.comment_line:
							source_id=False
							msg_flag=True
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
						msg_write = { 
								'msg_check':True,
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
		if context is None: context = {}
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
					time_cur = time.strftime("%H%M%S")
					date = time.strftime('%Y-%m-%d%H%M%S')
					username = user_name #the user
					pwd = pwd    #the password of the user
					dbname = dbname
					userid = ''
					log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
					obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
					sock_common = xmlrpclib.ServerProxy (log)
					try:
						raise
						userid = sock_common.login(dbname, username, pwd)
					except Exception as Err:
						# offline_obj=self.pool.get('offline.sync')
						# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
						conn_central_flag = True
						# if not offline_sync_sequence:
						# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_generate_grn_stock_transfer_central','error_log':Err,})
						# else:
						# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
						# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_central_flag})
####################################################################################################################
						con_cat = dbname+"-"+ branch_id.vpn_ip_address+"-"+'generate_grn-'+str(date)+'_'+str(time_cur)+'.sql'
						sync_str=''
						filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
						directory_name =str(os.path.expanduser('~')+'/indent_sync/')
						if not os.path.exists(directory_name):
							os.makedirs(directory_name)
						d = os.path.dirname(directory_name)
						func_string ="\n\n CREATE OR REPLACE FUNCTION generate_grn() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
						declare=" DECLARE \n "
						var1=""" create_series_ids INT;\n stock_transfer_no_id INT;\n source_ids INT;
\n product_transfer_id INT; \n cmt_id INT;
\n  BEGIN \n """
						endif="\n\n END IF; \n"
						ret="\n RETURN 1;\n"
						elsestr="\n ELSE \n"
						final="\nEND; \n $$;\n"
						fun_call="\n SELECT generate_grn();\n"
						sync_str+=func_string+declare+var1
						stock_transfer_no_id = "\n stock_transfer_no_id=(select id from branch_stock_transfer where stock_transfer_no='"+str(res.stn_no.stock_transfer_no)+"');"
						sync_str +=stock_transfer_no_id
						flag_series=False
						for receive_prod in res.receive_indent_line:
							if receive_prod.generic_id:
								if receive_prod.serial_line:
									if not flag_series:
										flag_series=True
										create_series="\n insert into product_series_main(test) values(stock_transfer_no_id) returning id into create_series_ids ;"
										sync_str +=create_series
									for receive_series in receive_prod.serial_line:
										count += 1
										transporter_create_new="\n insert into product_series(sr_no,product_code,product_name,generic_id,prod_uom,batch_val,product_category,quantity,serial_no,active_id,serial_check,series_line,reject,short,excess) values  (count,'"+str(receive_series.product_code)+"',(select id from product_product where name_template='"+str((receive_prod.product_name.name).replace("'","''"))+"'),	(select id from product_generic_name where name='"+str(receive_prod.generic_id.name)+"'),'"+str(receive_series.product_uom.name)+"','"+str(receive_series.batch.batch_no)+"','"+str(receive_prod.product_name.categ_id.name)+"','"+str(receive_series.quantity)+"','"+str(receive_series.serial_name)+"',"+str(receive_series.active_id)+","+str(receive_series.serial_check)+",create_series_ids,"+str(receive_series.reject_serial_check)+","+str(receive_series.short)+","+str(receive_series.excess)+");"
										
										sync_str +=transporter_create_new
							ifstr="\n IF stock_transfer_no_id IS not NULL THEN"
							
							intransit_state_update_id = "\n UPDATE branch_stock_transfer set serial_check_prod="+str(flag_series)+",grn_no = '"+str(res.grn_no)+"' ,grn_date ='"+str(res.grn_date)+"',state='done' where id in (stock_transfer_no_id);"
							sync_str += ifstr + intransit_state_update_id + endif
							for line in res.receive_indent_line:
									
								product_transfer_id = "\n product_transfer_id=(select id from branch_product_transfer where product_name=(select id from product_product where name_template='"+str((receive_prod.product_name.name).replace("'","''"))+"' LIMIT 1) and prod_id =(select id from product_product where name_template='"+str((line.product_name.name).replace("'","''"))+"' LIMIT 1) limit 1) ;"
								sync_str += product_transfer_id
								if line.notes_one2many:
									for line_id in line.notes_one2many:
										if line_id.source: #Source
											source_ids ="\n source_ids=(select id from res_company where name='"+str(line_id.source.name)+"');"
											sync_str += source_ids

										notes_id="\n (select id from branch_product_transfer_comment_line where user_id='"+str(line_id.user_id)+"' and indent_id=product_transfer_id and comment='"+str(line_id.comment)+"' and comment_date='"+str(line_id.comment_date)+"' and source =source_ids)"
										sync_str += notes_id
									
										msg_unread_ids = " \n UPDATE branch_product_transfer set msg_check_unread=True ,msg_check_read=False where id = product_transfer_id ;"
										sync_str +=msg_unread_ids
										msg_flag=True
										create_material_notes = "\n insert into branch_product_transfer_comment_line (indent_id,user_id,comment,comment_date,source) values (product_transfer_id ,'"+str(line_id.user_id)+"','"+str(line_id.comment)+"','"+str(line_id.comment_date)+"',source_ids);"
										sync_str += create_material_notes
											
							if res.comment_line:
								for remark_line in res.comment_line:
									cmt_id = "\n cmt_id=(select id from branch_stock_transfer_remarks where name='"+str(remark_line.comment)+"' and date='"+str(remark_line.comment_date)+"' and user_name='"+str(remark_line.user_id)+"' and branch_stock_transfer_id in (stock_transfer_no_id));"
									
									ifstr="\n IF cmt_id IS NULL THEN"
									
									add_notes_id = "\n insert into branch_stock_transfer_remarks (branch_stock_transfer_id,user_name,date,name) values (stock_transfer_no_id,'"+(remark_line.user_id if remark_line.user_id else 'administrator')+"',"+("'"+remark_line.comment_date+"'" if remark_line.comment_date else 'null')+" ,'"+(remark_line.comment if remark_line.comment else ' ')+"');"
								sync_str += cmt_id+ ifstr + add_notes_id 
						
								msg_ids = "\n UPDATE branch_stock_transfer set msg_check=True where id in (stock_transfer_no_id);"
					
								sync_str += msg_ids +endif
					
						with(open(filename,'a')) as f :
							f.write(sync_str)
							f.write(ret)
							f.write(final)
							f.write(fun_call)
							f.close()

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
										    'prod_uom':receive_series.product_uom.name,
										    'batch_val':receive_series.batch.batch_no,
										    'product_category':receive_prod.product_name.categ_id.name,
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
				time_cur = time.strftime("%H%M%S")
				date = time.strftime('%Y-%m-%d%H%M%S')
				username = user_name #the user
				pwd = pwd    #the password of the user
				dbname = dbname
				userid = ''
				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
				sock_common = xmlrpclib.ServerProxy (log)
				try:
					raise
					userid = sock_common.login(dbname, username, pwd)
				except Exception as Err:
					# offline_obj=self.pool.get('offline.sync')
					# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_disp_flag = True
					# if not offline_sync_sequence:
					# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':res.source_company.id,'srch_condn':False,'form_id':res,'func_model':'sync_generate_grn_stock_transfer_branch','error_log':Err,})
					# else:
					# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_disp_flag})
					# 
					####################
					con_cat = dbname+"-"+ branch_id.vpn_ip_address+"-"+'generate_grn-'+str(date)+'_'+str(time_cur)+'.sql'
					sync_str=''
					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
					directory_name =str(os.path.expanduser('~')+'/indent_sync/')
					if not os.path.exists(directory_name):
						os.makedirs(directory_name)
					d = os.path.dirname(directory_name)
					func_string ="\n\n CREATE OR REPLACE FUNCTION generate_grn() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
					declare=" DECLARE \n "
					var1=""" origin_ids INT;\n series_ids INT;\n source_ids INT;\n notes_id INT ;\n product_transfer_id INT;
							\n source_id INT; \n remark_srch_id INT;
							\n  BEGIN \n """
					endif="\n\n END IF; \n"
					ret="\n RETURN 1;\n"
					elsestr="\n ELSE \n"
					final="\nEND; \n $$;\n"
					fun_call="\n SELECT generate_grn();\n"
					sync_str+=func_string+declare+var1
				
					origin_ids = "\n origin_ids =(select id from stock_transfer where stock_transfer_no='"+str(res.stn_no.stock_transfer_no)+"');"
					ifstr="\n IF origin_ids IS not NULL THEN"
					
					move_ids = "\n UPDATE stock_transfer set state ='done',grn_no='"+str(res.grn_no)+"',grn_date='"+str(res.grn_date)+"' where id in (origin_ids);"
					
					sync_str += origin_ids + ifstr +  move_ids
					for receive_prod in res.receive_indent_line:
						if receive_prod.serial_line:
							for receive_series in receive_prod.serial_line:
								if receive_series.reject_serial_check:
									series_ids =  "\n series_ids=(select id from transfer_series where serial_name='"+str(receive_series.serial_name)+"');"
									
									transporter_create_new="\n  UPDATE transfer_series set reject="+str(receive_series.reject_serial_check)+",short="+str(receive_series.short)+" where id in (series_ids);"
									sync_str += series_ids + transporter_create_new 

						for line in res.receive_indent_line:
							product_transfer_id = "\n product_transfer_id=(select id from product_transfer where prod_id = origin_ids and product_name in (select id from product_product where name_template='"+str((line.product_name.name).replace("'","''"))+"'));"
							
							sync_str += product_transfer_id
							
							if line.notes_one2many:
								for line_id in line.notes_one2many:
									if line_id.source: #Source
										source_ids = "\n source_ids =(select id from res_company where name='"+str(line_id.source.name)+"');"
										sync_str +=source_ids 
									notes_id = "\n notes_id=(select id from product_transfer_comment_line where user_id="+str(line_id.user_id)+" and indent_id = product_transfer_id and comment='"+str(line_id.comment)+"' and comment_date='"+str(line_id.comment_date)+"' and source = source_ids);"
									
									ifstr="\n IF notes_id IS NULL THEN"
									
									msg_unread_ids = "\n UPDATE product_transfer set msg_check_unread=True ,msg_check_read=False where id = product_transfer_id;"
									
									create_material_notes = "\n insert into product_transfer_comment_line (indent_id,user_id,comment,comment_date,source) values (product_transfer_id , '"+str(line_id.user_id)+"','"+str(line_id.comment)+"','"+str(line_id.comment_date)+"',source_ids);"
									
									sync_str += notes_id +ifstr + msg_unread_ids + create_material_notes +endif
										
							if res.comment_line:
								for notes_line in res.comment_line:
									if notes_line.source:
										source_id = "\n source_id=(select id from res_company where name='"+str(notes_line.source.name)+"');"
									sync_str += source_id
									remark_srch_id = "\n remark_srch_id =(select id from stock_transfer_remarks where name='"+str(notes_line.comment)+"' and user_name ='"+str(notes_line.user_id)+"');"
									
									ifstr="\n IF remark_srch_id IS NULL THEN"
									notes_line_ids = "\n insert into stock_transfer_remarks (stock_transfer_id,user_name,date,name,source) values(origin_ids, '"+(notes_line.user_id if remark_line.user_id else 'administrator')+"', "+("'"+notes_line.comment_date+"'" if notes_line.comment_date else 'null')+" ,'"+(notes_line.comment if notes_line.comment else '')+"' ,source_id);"
									
									msg_ids = "\n UPDATE stock_transfer set msg_check=True where id  = origin_ids;"
									sync_str += remark_srch_id + ifstr + notes_line_ids + msg_ids + endif
					sync_str += endif
					
					with(open(filename,'a')) as f :
						f.write(sync_str)
						f.write(ret)
						f.write(final)
						f.write(fun_call)
						f.close()
######################################################
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
		if context is None: context = {}
		msg_flag=False
		conn_flag=False
		branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
		for branch_id in self.pool.get('res.company').browse(cr,uid,branch_type):
			vpn_ip_addr = branch_id.vpn_ip_address
			port = branch_id.port
			dbname = branch_id.dbname
			pwd = branch_id.pwd
			user_name = str(branch_id.user_name.login)
			time_cur = time.strftime("%H%M%S")
			date = time.strftime('%Y-%m-%d%H%M%S')
			username = user_name #the user
			pwd = pwd    #the password of the user
			dbname = dbname
			userid = ''
			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
			sock_common = xmlrpclib.ServerProxy (log)
			try:
				raise
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				# offline_obj=self.pool.get('offline.sync')
				# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_flag = True
				# if not offline_sync_sequence:
				# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'generate_grn_others','error_log':Err,})
				# else:
				# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
				# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
###############################################################################################################
				con_cat = dbname+"-"+ vpn_ip_addr+"-"+'generate_grn_others-'+str(date)+'_'+str(time_cur)+'.sql'
				sync_str=''
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name =str(os.path.expanduser('~')+'/indent_sync/')
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				func_string ="\n\n CREATE OR REPLACE FUNCTION generate_grn_others() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n "
				var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n prod_ids INT; \n ln_ids INT;
 remark_srch_id INT;
 state1 VARCHAR;
 flag1 INT;
 flag2 INT;
 flag3 INT;
 counter INT;\n  BEGIN \n
 flag1 =0;
 flag2 = 0;
 flag3 =0;
 counter=0; """
				endif="\n\n END IF; \n"
				ret="\n RETURN 1;\n"
				elsestr="\n ELSE \n"
				final="\nEND; \n $$;\n"
				fun_call="\n SELECT generate_grn_others();\n"
				sync_str+=func_string+declare+var1
				for rec in self.browse(cr,uid,ids):
					delivery_type_others= rec.delivery_type_others
					if delivery_type_others == 'direct_delivery':
						origin_ids ="\n origin_ids=(SELECT id FROM stock_picking WHERE origin='%s' AND id=%s LIMIT 1);" %(str(rec.indent_id.order_id),str(rec.indent_id.ci_sync_id))
						ifstr="\n IF origin_ids IS NOT NULL THEN"
						sync_str += origin_ids + ifstr
						for ln in rec.receive_indent_line:
							product_ids ="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((ln.product_name.name).replace("'","''")))
							ln_ids ="\n ln_ids =(SELECT id FROM stock_move WHERE product_id=product_ids AND product_code='%s' AND origin='%s' AND picking_id=origin_ids);" %(str(ln.product_code),str(ln.origin))
							move_ids="\n UPDATE stock_move SET state='done' WHERE product_id=product_ids AND product_code='%s' AND origin='%s' AND picking_id=origin_ids;" %(str(ln.product_code),str(ln.origin))
							sync_str += product_ids + ln_ids + move_ids
							if ln.notes_one2many:
								for material_notes in ln.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									source_id=0
									if material_notes.source:
										source_id ="\n source_id = (SELECT id FROM res_company WHERE name='%s');" %(str(material_notes.source.name))
										sync_str += source_id
									remark_srch_id ="\n remark_srch_id = (SELECT id FROM stock_move_comment_line WHERE comment='%s' AND user_id='%s' AND source=source_id AND comment_date ='%s' AND indent_id=ln_ids);" %(str(comment),str(user_name),str(comment_date))
									ifstr="\n IF remark_srch_id IS NULL THEN"
									notes_line_id="\n INSERT INTO stock_move_comment_line (indent_id,user_id,source,comment_date,comment) VALUE (ln_ids,'%s',source_id,'%s','%s');" %(str(user_name),str(comment_date),str(comment))
									sync_str += remark_srch_id + ifstr + notes_line_id +endif
						if rec.comment_line:
							for notes in rec.comment_line:
								if notes.source:
									source_id ="\n source_id =(SELECT id FROM res_company WHERE name='%s');" %(notes.source.name)
									sync_str +=source_id 
								remark_srch_id ="\n remark_srch_id=(SELECT id FROM indent_remark WHERE remark_field='%s' AND \"user\"='%s' AND source=source_id AND date='%s' AND remark=origin_ids);", sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
								ifstr="\n IF remark_srch_id IS NULL THEN"
								notes_line_ids="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (origin_ids,'%s',source_id,'%s','%s');" %(str(notes.user_id),str(notes.comment_date),str(notes.comment))
								msg_ids="\n UPDATE stock_picking SET msg_check=True WHERE id=origin_ids;"
								sync_str += remark_srch_id + notes_line_ids +msg_ids+endif
						sync_str += '''\n FOR state1 IN (SELECT state FROM stock_move WHERE picking_id=origin_ids) 
LOOP 
	IF state1 != 'done' THEN
		flag1 =1;
	END IF;
	IF state1 != 'cancel' THEN
		flag2 =1;
	END IF;
	IF state1 = 'cancel' OR state1 = 'done' THEN
		flag3 =1;
	END IF;
	IF state1 ='draft' OR state1 ='view_order' OR state1 ='waiting' OR state1 ='confirmed' OR state1 ='pending' OR state1 ='assigned' OR state1 ='packlist' OR state1 ='ready' OR state1 ='progress' OR state1 ='partial_received' THEN
        counter = 1;
    END IF;
  END LOOP;
  IF flag1=0 THEN
	UPDATE stock_picking SET state='done' WHERE id=origin_ids;
  END IF;
  IF flag2=0 THEN
	UPDATE stock_picking SET state='cancel' WHERE id=origin_ids;
  END IF;
  IF flag2=1 AND counter=0 AND flag1=1 AND flag3 =1 THEN
	UPDATE stock_picking SET state='done' WHERE id=origin_ids;
  END IF;'''
						sync_str +=endif
				with(open(filename,'a')) as f :
					f.write(sync_str)
					f.write(ret)
					f.write(final)
					f.write(fun_call)
					f.close()
###############################################################################################################
			sock = xmlrpclib.ServerProxy(obj)
			for rec in self.browse(cr,uid,ids):
				delivery_type_others= rec.delivery_type_others
				if delivery_type_others == 'direct_delivery':
					if conn_flag == False:
						origin_srch = [('origin', '=',rec.indent_id.order_id),('id','=',rec.indent_id.ci_sync_id)]
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

									move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', ln_ids[0], pick_line)
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
					time_cur = time.strftime("%H%M%S")
					date = time.strftime('%Y-%m-%d%H%M%S')
					username = user_name #the user
					pwd = pwd    #the password of the user
					dbname = dbname
					userid = ''
					log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
					obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
					sock_common = xmlrpclib.ServerProxy (log)
					try:
						raise
						userid = sock_common.login(dbname, username, pwd)
					except Exception as Err:
						# offline_obj=self.pool.get('offline.sync')
						# offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
						conn_flag = True
						# if not offline_sync_sequence:
						# 	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':name[0],'srch_condn':False,'form_id':ids[0],'func_model':'sync_generate_grn_others_1','error_log':Err,})
						# else:
						# 	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
						# 	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_flag})
###############################################################################################################
						con_cat = dbname+"-"+ vpn_ip_addr+"-"+'generate_grn_others-'+str(date)+'_'+str(time_cur)+'.sql'
						sync_str=''
						filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
						directory_name =str(os.path.expanduser('~')+'/indent_sync/')
						if not os.path.exists(directory_name):
							os.makedirs(directory_name)
						d = os.path.dirname(directory_name)
						func_string ="\n\n CREATE OR REPLACE FUNCTION generate_grn_others() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
						declare=" DECLARE \n "
						var1=""" origin_ids INT;\n product_ids INT;\n source_id INT;\n prod_ids INT;\n remark_srch_id INT; \n ln_ids INT;
 flag1 INT;
 flag2 INT;
 flag3 INT;
 counter INT;\n \n  BEGIN \n 
 flag1 =0;
 flag2 = 0;
 flag3 =0;
 counter=0;"""
						endif="\n\n END IF; \n"
						ret="\n RETURN 1;\n"
						elsestr="\n ELSE \n"
						final="\nEND; \n $$;\n"
						fun_call="\n SELECT generate_grn_others();\n"
						sync_str+=func_string+declare+var1
						origin_ids ="\n origin_ids=(SELECT id FROM stock_picking WHERE id=%s LIMIT 1);" %(str(track.indent_order_id))
						ifstr="\n IF origin_ids IS NOT NULL THEN"
						sync_str += origin_ids + ifstr
						for ln in rec.receive_indent_line:
							product_ids ="\n product_ids=(SELECT id FROM product_product WHERE name_template='%s');" %(str((track.product_name.name).replace("'","''")))
							ln_ids ="\n ln_ids =(SELECT id FROM stock_move WHERE product_id=product_ids AND product_code='%s' AND origin='%s' AND picking_id=origin_ids);" %(str(track.product_code),str(track.origin))
							move_ids="\n UPDATE stock_move SET state='done' WHERE product_id=product_ids AND product_code='%s' AND origin='%s' AND picking_id=origin_ids;" %(str(track.product_code),str(track.origin))
							sync_str += product_ids + ln_ids + move_ids
							if track.notes_one2many:
								for material_notes in track.notes_one2many:
									user_name=material_notes.user_id
									source=material_notes.source.id
									comment=material_notes.comment
									comment_date=material_notes.comment_date
									source_id=0
									if material_notes.source:
										source_id ="\n source_id = (SELECT id FROM res_company WHERE name='%s');" %(str(material_notes.source.name))
										sync_str += source_id
									remark_srch_id ="\n remark_srch_id = (SELECT id FROM stock_move_comment_line WHERE comment='%s' AND user_id='%s' AND source=source_id AND comment_date ='%s' AND indent_id=ln_ids);" %(str(comment),str(user_name),str(comment_date))
									ifstr="\n IF remark_srch_id IS NULL THEN"
									notes_line_id="\n INSERT INTO stock_move_comment_line (indent_id,user_id,source,comment_date,comment) VALUE (ln_ids,'%s',source_id,'%s','%s');" %(str(user_name),str(comment_date),str(comment))
									sync_str += remark_srch_id + ifstr + notes_line_id +endif
						if rec.comment_line:
							for notes in rec.comment_line:
								if notes.source:
									source_id ="\n source_id =(SELECT id FROM res_company WHERE name='%s');" %(notes.source.name)
									sync_str +=source_id 
								remark_srch_id ="\n remark_srch_id=(SELECT id FROM indent_remark WHERE remark_field='%s' AND \"user\"='%s' AND source=source_id AND date='%s' AND remark=origin_ids);", sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)
								ifstr="\n IF remark_srch_id IS NULL THEN"
								notes_line_ids="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (origin_ids,'%s',source_id,'%s','%s');" %(str(notes.user_id),str(notes.comment_date),str(notes.comment))
								msg_ids="\n UPDATE stock_picking SET msg_check=True WHERE id=origin_ids;"
								sync_str += remark_srch_id + notes_line_ids +msg_ids+endif
						sync_str += '''FOR state1 IN (SELECT state FROM stock_move WHERE picking_id=origin_ids) 
LOOP 
	IF state1 != 'done' THEN
		flag1 =1;
	END IF;
	IF state1 != 'cancel' THEN
		flag2 =1;
	END IF;
	IF state1 = 'cancel' OR state1 = 'done' THEN
		flag3 =1;
	END IF;
	IF state1 ='draft' OR state1 ='view_order' OR state1 ='waiting' OR state1 ='confirmed' OR state1 ='pending' OR state1 ='assigned' OR state1 ='packlist' OR state1 ='ready' OR state1 ='progress' OR state1 ='partial_received' THEN
        counter = 1;
    END IF;
  END LOOP;
  IF flag1=0 THEN
	UPDATE stock_picking SET state='done' WHERE id=origin_ids;
  END IF;
  IF flag2=0 THEN
	UPDATE stock_picking SET state='cancel' WHERE id=origin_ids;
  END IF;
  IF flag2=1 AND counter=0 AND flag1=1 AND flag3 =1 THEN
	UPDATE stock_picking SET state='done' WHERE id=origin_ids;
  END IF;'''
						sync_str +=endif
						with(open(filename,'a')) as f :
							f.write(sync_str)
							f.write(ret)
							f.write(final)
							f.write(fun_call)
							f.close()
###############################################################################################################
					sock = xmlrpclib.ServerProxy(obj)
					if conn_flag==False:
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
