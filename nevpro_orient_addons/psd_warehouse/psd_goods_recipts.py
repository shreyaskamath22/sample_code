#version 10.10.0.39 manual creation in warehouse

from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
import datetime 
import calendar
import re
# from dateutil.relativedelta import relativedelta
from datetime import date,datetime, timedelta
from base.res import res_company as COMPANY
from base.res import res_partner
from collections import Counter
import xmlrpclib
import math
import os



class receive_indent(osv.osv):
	_inherit = "receive.indent"


	# def _compute_document_value(self, cr, uid, ids, field_name, arg, context=None):
	# 	result={}
	# 	total=0
	# 	for rec in self.browse(cr,uid,ids):
	# 		for line in rec.receive_indent_line:
	# 			total = total+(line.qty_received*line.price_unit)+line.cst_vat +line.excise_value
	# 		result[rec.id]=total
	# 	return result

	_columns={
		'user_id':fields.char('User Name',size=64),
		'po_no':fields.char('PO No.',size=64),
		'invoice_no':fields.char('Invoice No.',size=64),
		'invoice_date':fields.date('Invoice Date',size=64),
		'generate_grn_invisible':fields.boolean('Generate GRN Invisible'),
		'delivery_type_others': fields.selection([('banned_st','Branch Stock Transfer'),
			('excess_st','Excess Stock Transfer'),
			('inter_branch_st','Inter branch Stock Transfer'),
			('direct_delivery','Direct Delivery'),
			('local_purchase','Local Purchase'),
			('internal_delivery','Internal Delivery')],'Delivery Type *'),
		# 'document_value':fields.function(_compute_document_value, type='float', obj='receive.indent', method=True, store=False, string='Estimated Value(Rs)'),
		'delivery_receive_date':fields.date('Delivery Recive Date'),
	}

	_defaults={
		'generate_grn_invisible':False,
		#'delivery_receive_date':datetime.now().date() ,
	}

	def update_serial_check(self,cr,uid,ids,context=None):
		product_product_obj = self.pool.get('product.product')
		o=self.browse(cr,uid,ids[0])
		form_id=o.id
		self.write(cr,uid,form_id,{'generate_grn_invisible':True,'check_product_serial':'True'})
		lineids=self.pool.get('material.details').search(cr, uid, [('indent_id', '=', form_id)])
		if lineids:
			browse_ids = self.pool.get('material.details').browse(cr,uid,lineids)
			for r in browse_ids:
				line_id = r.id
				product_name = r.product_name.id
				type_product = product_product_obj.browse(cr,uid,product_name).type_product
				if type_product == 'track_equipment':
					self.pool.get('material.details').write(cr,uid,line_id,{'serial_check1':True,'series_check_new':True})
		return True

	def onchange_receive_indent_line1(self,cr,uid,ids,receive_indent_line):
		val={}
		total_price=0
		for line in receive_indent_line:
			if line[2] and (('price_unit' in line[2]) and ('qty_received' in line[2])) :
				total_price=total_price+(line[2].get('price_unit')*line[2].get('qty_received'))

		val['document_value']=total_price
		return{'value':val}		

	def onchange_indent_id1(self,cr,uid,ids,indent_id):
		v={}
		values=[]
		notes=[]
		if indent_id:
			line_ids = ids and self.pool.get('material.details').search(cr, uid, [('indent_id', '=', ids[0])]) or False
			if line_ids:
				self.pool.get('material.details').unlink(cr, uid, line_ids)
			res=self.pool.get('res.indent').browse(cr,uid,indent_id)
			for value in res.comment_line:
					notes.append({
						'user_id':value.user_id,
						'source':value.source.id,
						'comment_date':value.comment_date,
						'comment':value.comment,
						})	
			for var in res.order_line:
				msg_flag=False
				product_name=var.product_id.id
				res1=self.pool.get('product.product').browse(cr,uid,product_name)
				batch_NA = ''
				if res1.batch_type=='non_applicable':
					red=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name)])
					for r in self.pool.get('res.batchnumber').browse(cr,uid,red):
						batch_NA=r.id
				else:
					red=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name)])
					if red:
						for r in self.pool.get('res.batchnumber').browse(cr,uid,red):
							batch_NA=False
							#manufacturing_date = r.manufacturing_date
				if var.notes_one2many:
					msg_flag=True

				if var.source_company:						
				  if var.state in ('progress','partial_received'):
					values.append({ 'product_code':var.product_code,
									'product_name':var.product_id.id,
									'generic_id':var.generic_id.id,
									'product_qty':(var.product_uom_qty-var.received_quantity),
									'indented_quantity':var.product_uom_qty,
									'product_uom':var.product_id.uom_id.id,
									'price_unit':var.price_unit,
									'batch':batch_NA,
									'source_company':var.source_company.id,
									'subtotal':(var.product_uom_qty*var.price_unit),
									'indent_line_sequence':var.indent_line_sequence,
									'delivery_type':'direct_delivery',
									'local_uom':var.product_id.local_uom_id.id,
									'qty_received':(var.product_uom_qty-var.received_quantity),
									'origin':res.order_id,
									'indent_order_id':var.indent_order_id,
									'ci_sync_id':var.ci_sync_id,
									'msg_check_unread':msg_flag, 'msg_check_read':False,})
			return {'value':{'comment_line':notes,'receive_indent_line':values,'indent_date':res.order_date}}
		return{'value':{'receive_indent_line':None,'indent_date':None,'comment_line':None}}

# 	def nsd_generate_grn(self, cr, uid,ids,vals, context=None):
# 		if context is None : context is {} 
# 		exp_date = ''
# 		ccount = ''
# 		account = ''
# 		bcount = ''
# 		qqqty = 0
# 		transporter_name = ''
# 		c = 0
# 		qty_received = 0.0
# 		count = 0
# 		prod_qty = ''
# 		generic_id = ''
# 		self.material_notes_update(cr,uid,ids,context=context)	
# 		for var_stn in self.browse(cr,uid,ids):
# 				if not var_stn.receive_indent_line:
# 					raise osv.except_osv(('Alert!'),('Please Add product line before Receive Grn.'))
# 				if var_stn.delivery_type_others in ('banned_st','excess_st','inter_branch_st'):
# 					stn_no=var_stn.stn_no.id
# 					for stn_var in self.pool.get('branch.stock.transfer').browse(cr,uid,[stn_no]):
# 						state=stn_var.state
# 						if state=='cancel':
# 							raise osv.except_osv(('Alert!'),('You can not proceed with cancelled order'))
# 					for files in var_stn.receive_indent_line:
# 						manufacturing_date = files.manufacturing_date
# 						product_code = files.product_code
# 						product_category = files.product_name.categ_id.id

# 						qty_received = files.qty_received
# 						product_name = files.product_name.id
# 						reject_qty=files.reject
# 						flag=False
# 						reject_count=0
# 						if files.product_name.type_product == 'track_equipment':
# 							if not files.serial_line:
# 								search_serial=self.pool.get('transfer.series').search(cr,uid,[('stn_no','=',files.stn_no),('product_name','=',files.product_name.id)])
# 								for rec in search_serial:
# #feb15
# 									self.pool.get('transfer.series').write(cr,uid,rec,{'series_line':files.id,'product_category':product_category})								
# 		for brw_batch in self.browse(cr,uid,ids):
# 			for batch_line in brw_batch.receive_indent_line:
# 				product_name = batch_line.product_name.id
# 				batch = batch_line.batch.id

# 				if batch_line.product_qty==0:
# 					raise osv.except_osv(('Alert!'),('Documented Quantity Should be greater than 0.'))
# 				if batch_line.short or batch_line.reject:
# 						if batch_line.product_qty < batch_line.short or batch_line.product_qty < batch_line.reject or batch_line.product_qty < batch_line.reject + batch_line.short:
# 							raise osv.except_osv(('Alert!'),('Quantity Cannot be greater than the Documented Qty'))	

# 				srch = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',batch)])
# 				for batch_brw in self.pool.get('res.batchnumber').browse(cr,uid,srch):
# 					if product_name != batch_brw.name.id:
# 						raise osv.except_osv(('Alert!'),('Please select proper Product Name to assign the batch.'))
		
# 		for var in self.browse(cr,uid,ids):
# 				cc_date = datetime.now()
# 				c_date=datetime.strftime(cc_date,"%Y-%m-%d %H:%M:%S")
# 				current_date = datetime.now().date()
# 				monthee = current_date.month
# 				year = current_date.year
# 				day = current_date.day
# 				#partner_seq=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
# 				year1=current_date.strftime('%y')
# 				month =current_date.strftime('%m')
# 				if int(month) > 3:
# 					 year1 = int(year1)+1
# 				else:
# 					 year1=year1
# 				year1=str(year1)
# 				branch_code=''
# 				grn_id = ''
# 				search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','res.warehouse2')])
# 				for i in self.pool.get('ir.sequence').browse(cr,uid,search):
# 					if i.year != year1:
# 						self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year1,'implementation':'no_gap','number_next':1})
# 				sequence_no=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
# 				company_id=self._get_company(cr,uid,context=None)
# 				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
# 					if comp_id.internal_branch_no:
# 						branch_code=comp_id.internal_branch_no
# 					if comp_id.indent_req_id:
# 						grn_id=comp_id.grn_id
# 				partner_seq = branch_code + grn_id + year1 + sequence_no
# 				check='False'
# 				for lines in var.receive_indent_line:
# 					if lines.product_name.type_product=='track_equipment':
# 						check='True'
# 				grn_date= fields.date.context_today(self, cr, uid, context=context),
# 				self.pool.get('receive.indent').write(cr,uid,var.id,{'grn_no':partner_seq,
# 																	 'state':'done',
# 																	 'grn_date':time.strftime('%Y-%m-%d %H:%M:%S'),
# 																	 'check_product_serial':check})
# 				grn_no = var.grn_no
# 				if var.delivery_type_others not in ('banned_st','excess_st','inter_branch_st'):
# 				 for files in var.receive_indent_line:
# 					manufacturing_date = files.manufacturing_date
# 					product_code = files.product_code
# 					qty_received = files.qty_received
# 					product_name = files.product_name.id
# 					if not files.batch:
# 						raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(files.product_name.name_template))						
# 					if files.product_name.batch_type=='applicable' and not files.manufacturing_date:
# 						raise osv.except_osv(('Alert!'),('Please Enter Manufacturing Date of the Product.'))
# 					elif files.product_name.batch_type=='applicable' and files.manufacturing_date:
# 						aaa = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
# 						for v in self.pool.get('product.product').browse(cr,uid,aaa):
# 							qqqty = v.quantity_available
# 							shelf_life = v.shelf_life
# 							exp_date = self.add_months(manufacturing_date,shelf_life)
# 							prod_qty=v.quantity_available+files.qty_received
# 							if files.product_name.type_product != 'track_equipment':
# 								self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,
# 																				'quantity_available':prod_qty,
																				
# 																				})
# 								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})
# 								ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':product_name,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':v.quantity_available,'voucher_number':partner_seq})

# 					elif (files.product_name.batch_type=='non_applicable' or not files.product_name.batch_type):
# 						aaa = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
# 						for v in self.pool.get('product.product').browse(cr,uid,aaa):
# 							qqqty = v.quantity_available
# 							shelf_life = v.shelf_life

# 							prod_qty=v.quantity_available+files.qty_received
# 							if files.product_name.type_product != 'track_equipment':
# 								self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,
# 																				'quantity_available':prod_qty,
																				
# 																				})
# 								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+qty_received,'st':files.price_unit,})
# 								ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':product_name,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':qqqty,'voucher_number':partner_seq})
# 				 if var.delivery_type_others=='internal_delivery' :
# 					stock_transfer_no=var.stn_no.id
# 					stn_search=self.pool.get('branch.stock.transfer').search(cr,uid,[('id','=',stock_transfer_no)])
# 					for res in self.pool.get('branch.stock.transfer').browse(cr,uid,stn_search):
# 						self.pool.get('branch.stock.transfer').write(cr,uid,res.id,{'state':'done'})
# 				indent_id=0
# 				if var.delivery_type_others in ('banned_st','excess_st','inter_branch_st'):
# 					for rec in self.browse(cr,uid,ids):
# 						for ln in rec.receive_indent_line:
# 							form_material_id = ln.id
# 							product_id = ln.product_name
# 							generic_id = ln.generic_id.id
# 							reject = ln.reject
# 							short=ln.short
# 							excess=ln.excess
# 							type_product = product_id.type_product
# 							if ln.short or ln.reject:
# 								if ln.product_qty < ln.short or ln.product_qty < ln.reject or ln.product_qty < ln.reject + ln.short:
# 									raise osv.except_osv(('Alert!'),('Short/Reject Quantity Cannot be greater than the Documented Qty'))	

# 							if type_product == 'track_equipment':

# 									cr.execute('select count(reject_serial_check) from transfer_series where series_line=%s and reject_serial_check = True  and product_name=%s',(form_material_id,ln.product_name.id))
# 									result=cr.fetchone()[0]
# 									cr.execute('select count(short) from transfer_series where series_line=%s and short = True  and product_name=%s',(form_material_id,ln.product_name.id))
# 									result1=cr.fetchone()[0]
# 									cr.execute('select count(excess) from transfer_series where series_line=%s and excess = True  and product_name=%s',(form_material_id,ln.product_name.id))
# 									result2=cr.fetchone()[0]
# 									if result != long(reject):
# 										raise osv.except_osv(('Alert!'),('You cannot reject more or less serial number. You gave reject value = %s for Product = %s .')%(reject,ln.product_name.name))
# 									if result2 != long(excess):
# 										raise osv.except_osv(('Alert!'),('You cannot excess more or less serial number. You gave excess value = %s for Product = %s .')%(excess,ln.product_name.name))
# 									if result1 != long(short):
# 										raise osv.except_osv(('Alert!'),('You cannot short more or less serial number. You gave short value = %s for Product = %s .')%(short,ln.product_name.name))

# 					flag=False
# 					for files in var.receive_indent_line:
# 						cc_date = datetime.now()
# 						c_date=datetime.strftime(cc_date,"%Y-%m-%d %H:%M:%S")
# 						current_date = datetime.now().date()
# 						monthee = current_date.month
# 						year = current_date.year
# 						day = current_date.day
# 						manufacturing_date = files.manufacturing_date
# 						product_code = files.product_code
# 						qty_received = files.qty_received
# 						product_name = files.product_name.id
# 						reject_qty=files.reject
# 						reject_count=0
# 						if files.serial_line:
# 							for reject_serials in files.serial_line:
# 								if reject_serials.reject_serial_check:
# 									reject_count=reject_count+1
# 						if files.product_name.type_product == 'track_equipment' and flag == False:
# 							flag=True
# 							series_main=self.pool.get('product.series.main').create(cr,uid,{'test':var.id,'state':'end'})
# 						if not files.batch:
# 							raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(files.product_name.name_template))
# 						elif files.product_name.batch_type=='applicable' and files.manufacturing_date:
# 							aaa = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
# 							for v in self.pool.get('product.product').browse(cr,uid,aaa):
# 								qqqty = v.quantity_available
# 								shelf_life = v.shelf_life
# 								exp_date = self.add_months(manufacturing_date,shelf_life)
# 								prod_qty=v.quantity_available+files.qty_received
# 								if files.product_name.type_product != 'track_equipment':
# 									self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,
# 																					'quantity_available':prod_qty,
# 																					})
# 									self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})
# 									ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':files.product_name.id,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':v.quantity_available,'serial_check':True,'voucher_number':partner_seq})
# 								if files.product_name.type_product == 'track_equipment':
								
# 									self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,
# 																					'quantity_available':prod_qty,})
# 									self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})
# 									ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':files.product_name.id,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':v.quantity_available,'serial_check':True,'voucher_number':partner_seq})
# 								if files.serial_line:
									
# 									for serial in files.serial_line:
# 										count = count + 1               #feb15
# 										sr_no=count#feb15
# 										#sr_no=serial.sr_no
# 										product_code=serial.product_code
# 										product_name=serial.product_name.id
# 										product_category = serial.product_category.id  #feb15
# 										product_uom=serial.product_uom.id
# 										batch=serial.batch.id
# 										quantity=1
# 										serial_no=serial.serial_name
# 										reject_serial_check=serial.reject_serial_check
# 										short=serial.short
# 										excess=serial.excess
# 										if serial.short:
# 											quantity=0
# 									#feb15	
# 										self.pool.get('product.series').create(cr,uid,{'sr_no':sr_no,'grn_no':grn_no,'line_id':series_main,'excess':excess,'short':short,'product_code':product_code,'generic_id':generic_id,'product_category':product_category,'product_name':product_name,'product_uom':product_uom,
# 'batch':batch,'quantity':quantity,'serial_no':serial_no,'serial_check':True,'reject':reject_serial_check})
# 									#if files.product_name.type_product != 'track_equipment':
										

# 						elif (files.product_name.batch_type=='non_applicable' or not files.product_name.batch_type):
# 							#if files.product_name.type_product != 'track_equipment':
# 							self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+qty_received,'st':files.price_unit,})
# 							#if files.product_name.type_product != 'track_equipment':
# 							ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':files.product_name.id,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':qqqty,'voucher_number':partner_seq})
# 							self.pool.get('product.product')._update_product_quantity(cr,uid,[files.batch.name.id])
# 							if files.serial_line:
# 									for serial in files.serial_line:
# 										count = count + 1  
# 										sr_no=count#feb15
# 										product_code=serial.product_code
# 										product_name=serial.product_name.id
# 										product_uom=serial.product_uom.id
# 										product_category = serial.product_category.id
# 										batch=serial.batch.id
# 										quantity=1
# 										serial_no=serial.serial_name
# 										reject_serial_check=serial.reject_serial_check
# 										short=serial.short
# 										excess=serial.excess
# 										if serial.short:
# 											quantity=0

# 										self.pool.get('product.series').create(cr,uid,{'sr_no':sr_no,'grn_no':grn_no,'line_id':series_main,'short':short,'excess':excess,'generic_id':generic_id,'product_code':product_code,'product_category':product_category,'product_name':product_name,'product_uom':product_uom,'batch':batch,'quantity':quantity,'serial_no':serial_no,
# 'serial_check':True,'reject':reject_serial_check})
						
# 						self.pool.get('receive.indent').write(cr,uid,var.id,{'grn_no':partner_seq,
# 																	 'state':'done',
# 																	 'check_product_serial':'False',
# 																	 'check_attachment':flag,	
# 																	 })
# 					stock_transfer_no=var.stn_no.id
# 					stn_search=self.pool.get('branch.stock.transfer').search(cr,uid,[('id','=',stock_transfer_no)])

# 					stn_remark_search=self.pool.get('branch.stock.transfer.remarks').search(cr,uid,[('branch_stock_transfer_id','=',stock_transfer_no)])
# 					for remark_stn in self.pool.get('branch.stock.transfer.remarks').browse(cr,uid,stn_remark_search):
# 						remark=remark_stn.name
# 						user_name=remark_stn.user_name
# 						date=remark_stn.date
# 						source=remark_stn.source.id
						
# 						receive_remark=self.pool.get('receive.indent.comment.line').search(cr,uid,[('comment_date','=',date),('user_id','=',user_name),('comment','=',remark),('source','=',source)])
# 						if receive_remark:
# 							print 'kk'
# 						else:
# 							self.pool.get('receive.indent.comment.line').create(cr,uid,{'comment_date':date,'user_id':user_name,'comment':remark,'source':source,'receive_indent_id':var.id})

# 					for res in self.pool.get('branch.stock.transfer').browse(cr,uid,stn_search):
# 						self.pool.get('branch.stock.transfer').write(cr,uid,res.id,{'state':'done'})
# 					if var.delivery_type_others in ('banned_st','excess_st','inter_branch_st'):
# 						self.syn_generate_grn_stock_transfer(cr,uid,ids,context=context)

# 		for rec in self.browse(cr,uid,ids):
# 			indent_id=rec.indent_id.id

# 			if rec.delivery_type_others=='direct_delivery':
# 				dict1={}
# 				last_delivery=False
# 				for line in rec.receive_indent_line:
# 					last_delivery=line.last_delivery
# 					dict1[str(line.product_name.id)]=0
# 				for vals in dict1:
# 					add=[x.product_qty for x in rec.receive_indent_line if x.product_name.id==int(vals)]
# 					dict1[vals]=sum(add)
# 				for res in dict1.keys():
# 					dest=int(res)
# 					Value = dict1[res]
# 					indent_search=self.pool.get('res.indent').search(cr,uid,[('id','=',rec.indent_id.id)])
# 					for temp in self.pool.get('res.indent').browse(cr,uid,indent_search):
# 						for var in temp.order_line:	
# 							if var.product_id.id in [dest]:
# 								product_qty=var.product_uom_qty
# 								if (var.received_quantity+Value) >= product_qty or last_delivery:
# 									self.pool.get('indent.order.line').write(cr,uid,var.id,{'state':'received','received_quantity':var.received_quantity+Value})
# 								if (var.received_quantity+Value) < product_qty and not last_delivery:
# 									self.pool.get('indent.order.line').write(cr,uid,var.id,{'state':'partial_received','received_quantity':var.received_quantity+Value})
# 				self.sync_indent_notes_update(cr,uid,ids,context=context)
# 				flag=True
# 				for indent_rec in self.pool.get('res.indent').browse(cr,uid,[rec.indent_id.id]):
# 					for indent_lines in indent_rec.order_line:
# 						if indent_lines.state not in ('received','cancel'):
# 							flag=False

# 				# if flag==True:
# 				# 		self.pool.get('res.indent').write(cr,uid,[indent_id],{'state':'done'})	

# 				indent_no=rec.indent_id.id
# 				indent_search=self.pool.get('res.indent').search(cr,uid,[('id','=',indent_no)])
# 				stn_remark_search=self.pool.get('indent.comment.line').search(cr,uid,[('indent_id','=',indent_no)])
# 				for remark_stn in self.pool.get('indent.comment.line').browse(cr,uid,stn_remark_search):
# 						remark=remark_stn.comment
# 						user_name=remark_stn.user_id
# 						date=remark_stn.comment_date
# 						source=remark_stn.source.id
						
# 						receive_remark=self.pool.get('receive.indent.comment.line').search(cr,uid,[('comment_date','=',date),('user_id','=',user_name),('comment','=',remark),('source','=',source)])
# 						if receive_remark:
# 							print 'kk'
# 						else:
# 							self.pool.get('receive.indent.comment.line').create(cr,uid,{'comment_date':date,'user_id':user_name,'comment':remark,'source':source,'receive_indent_id':rec.id})

			
# 		for delivery_check in self.browse(cr,uid,ids):
# 			if delivery_check.delivery_type_others=='direct_delivery':
# 				self.sync_generate_grn_others_1(cr,uid,ids,context=context)
# 		self.sync_generate_grn_others(cr,uid,ids,context=context)
# 		return True


# 	def nsd_generate_indent_grn(self, cr, uid,ids,vals, context=None):
# 		if context is None : context = {}
# 		exp_date = ''
# 		ccount = ''
# 		account = ''
# 		bcount = ''
# 		qqqty = 0
# 		scount=0
# 		c = 0
# 		qty_received = 0.0
# 		prod_qty = ''
# 		series_main=''
# 		flag=False
# 		search_indent=''
# 		form_material_id = 0
# 		self.material_notes_update(cr,uid,ids,context=context)	
# 		for res in self.browse(cr,uid,ids):
# 			test_id = res.id
# 			srch = self.pool.get('receive.indent').search(cr,uid,[('id','=',test_id)])
# 			for rec in self.pool.get('receive.indent').browse(cr,uid,srch):
# 				order_id = rec.indent_id.order_id
# 				for ln in rec.receive_indent_line:
# 					form_material_id = ln.id
# 					product_id = ln.product_name
# 					reject = ln.reject
# 					short=ln.short
# 					excess=ln.excess
# 					type_product = product_id.type_product

# 					if ln.short or ln.reject:
# 						if ln.product_qty < ln.short or ln.product_qty < ln.reject or ln.product_qty < ln.reject + ln.short:
# 							raise osv.except_osv(('Alert!'),('Short/Reject Quantity Cannot be greater than the Documented Qty'))	

# 					if type_product == 'track_equipment':
# 							cr.execute('select count(reject_serial_check) from transfer_series where series_line=%s and reject_serial_check = True  and product_name=%s',(form_material_id,ln.product_name.id))
# 							result=cr.fetchone()[0]
# 							cr.execute('select count(short) from transfer_series where series_line=%s and short = True  and product_name=%s',(form_material_id,ln.product_name.id))
# 							result1=cr.fetchone()[0]
# 							cr.execute('select count(excess) from transfer_series where series_line=%s and excess = True  and product_name=%s',(form_material_id,ln.product_name.id))
# 							result2=cr.fetchone()[0]
# 							if result != long(reject):
# 								raise osv.except_osv(('Alert!'),('You cannot reject more or less serial number. You gave reject value = %s for Product = %s .')%(reject,ln.product_name.name))		

# 							if result2 != long(excess):
# 								raise osv.except_osv(('Alert!'),('You cannot excess more or less serial number. You gave excess value = %s for Product = %s .')%(excess,ln.product_name.name))	

# 							if result1 != long(short):
# 								raise osv.except_osv(('Alert!'),('You cannot short more or less serial number. You gave short value = %s for Product = %s .')%(short,ln.product_name.name))

# 		form_branch_id = ''
# 		for var in self.browse(cr,uid,ids):
# 				form_branch_id = var.form_branch_id
# 				indent_no=var.indent_no
# 				cc_date = datetime.now()
# 				c_date=datetime.strftime(cc_date,"%Y-%m-%d %H:%M:%S")
# 				current_date = datetime.now().date()
# 				monthee = current_date.month
# 				year = current_date.year
# 				day = current_date.day
# 				#partner_seq=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
# 				year1=current_date.strftime('%y')
# 				month =current_date.strftime('%m')
# 				if int(month) > 3:
# 					 year1 = int(year1)+1
# 				else:
# 					 year1=year1
# 				year1=str(year1)
# 				branch_code=''
# 				grn_id = ''
# 				search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','res.warehouse2')])
# 				for i in self.pool.get('ir.sequence').browse(cr,uid,search):
# 					if i.year != year1:
# 						self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year1,'implementation':'no_gap','number_next':1})
# 				sequence_no=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
# 				company_id=self._get_company(cr,uid,context=None)
# 				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
# 					if comp_id.internal_branch_no:
# 						branch_code=comp_id.internal_branch_no
# 					if comp_id.indent_req_id:
# 						grn_id=comp_id.grn_id
# 				partner_seq = branch_code + grn_id + year1 + sequence_no
# 				#check for track equipment type product:
# 				check='False'
# 				for lines in var.receive_indent_line:
# 					if lines.product_name.type_product=='track_equipment':
# 						check='True'
# 				grn_date=datetime.now()
# 				self.pool.get('receive.indent').write(cr,uid,var.id,{'grn_no':partner_seq,
# 																	 'state':'done',
# 																	 'grn_date':time.strftime('%Y-%m-%d %H:%M:%S'),
# 																	 'check_product_serial':check})
# 				if indent_no:
# 					search_indent=self.pool.get('res.indent').search(cr,uid,[('form_branch_id_seq','=',form_branch_id),('order_id','=',indent_no)])
# 				grn_no = var.grn_no
# 				p_qty = 0   
# 				#if var.delivery_type in ('internal_delivery','external_delivery'):
# 				for files in var.receive_indent_line:
# 					p_qty = files.product_qty 
# 					count_qty = 0
# 					srh = self.pool.get('receive.indent').search(cr,uid,[('indent_no','=',var.indent_no)])
# 					for srh_var in self.pool.get('receive.indent').browse(cr,uid,srh):
# 						for p in srh_var.receive_indent_line:
# 							count_qty = count_qty + p.product_qty
# 					manufacturing_date = files.manufacturing_date
# 					product_code = files.product_code
# 					generic_id = files.generic_id.id
# 					qty_received = files.qty_received
# 					product_name = files.product_name.id
# 					if indent_no:
# 	   				 for indent_rec in self.pool.get('res.indent').browse(cr,uid,search_indent):
# 						for prod_line in indent_rec.order_line:
# 							prod_id=prod_line.product_id.id
# 							if prod_id==product_name:

# 							 received_quantity = prod_line.received_quantity + p_qty
# 							 self.pool.get('indent.order.line').write(cr,uid,prod_line.id,{'received_quantity':received_quantity})
# 							 if received_quantity >= prod_line.product_uom_qty:
# 								self.pool.get('indent.order.line').write(cr,uid,prod_line.id,{'state':'received'})
			
# 					if files.product_name.type_product == 'track_equipment' and flag == False:
# 						flag=True
# 						series_main=self.pool.get('product.series.main').create(cr,uid,{'test':var.id,'state':'end'})
# 					if not files.batch:
# 						raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(files.product_name.name_template))	

# 					elif files.product_name.batch_type=='applicable' and files.manufacturing_date:
# 						aaa = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
# 						for v in self.pool.get('product.product').browse(cr,uid,aaa):
# 							qqqty = v.quantity_available
# 							shelf_life = v.shelf_life
# 							exp_date = self.add_months(manufacturing_date,shelf_life)
# 							prod_qty=v.quantity_available+files.qty_received

# 							ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':product_name,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':v.quantity_available,'serial_check':True,'voucher_number':partner_seq})
# 							if files.product_name.type_product != 'track_equipment':
# 								self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,
# 																				'quantity_available':prod_qty,})
# 								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})

# 							if files.product_name.type_product == 'track_equipment':
								
# 								self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,
# 																				'quantity_available':prod_qty,})
# 								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})
# 							if files.serial_line:
# 								for serial in files.serial_line:
# 									scount=scount+1
# 									sr_no=scount
# 									product_code11=serial.product_name.default_code
# 									product_name=serial.product_name.id
# 									product_uom=serial.product_uom.id
# 									product_category=serial.product_name.categ_id.id
# 									batch=serial.batch.id
# 									quantity=1
# 									serial_no=serial.serial_name
# 									reject=serial.reject_serial_check
# 									short=serial.short
# 									excess=serial.excess
# 									if serial.short:
# 										quantity=0	

# 									self.pool.get('product.series').create(cr,uid,{'sr_no':sr_no,'grn_no':grn_no,'line_id':series_main,'product_category':product_category,'generic_id':generic_id,'product_code':product_code11,'short':short,'excess':excess,'product_code':product_code,'product_name':product_name,'product_uom':product_uom,'batch':batch,'quantity':quantity,'serial_no':serial_no,'serial_check':True,'reject':reject})

# 					elif (files.product_name.batch_type=='non_applicable' or not files.product_name.batch_type):

# 						aaa = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
# 						for v in self.pool.get('product.product').browse(cr,uid,aaa):
# 							qqqty = v.quantity_available
# 							shelf_life = v.shelf_life
# 							#exp_date = self.add_months(manufacturing_date,shelf_life)
# 							prod_qty=v.quantity_available+files.qty_received

# 							ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':product_name,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':qqqty,'voucher_number':partner_seq})
# 						if files.product_name.type_product != 'track_equipment':
# 								self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,
# 																				'quantity_available':prod_qty,})
# 								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})

# 						if files.product_name.type_product == 'track_equipment':
								
# 								self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,
# 																				'quantity_available':prod_qty,})
# 								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})

# 						if files.serial_line:
# 								for serial in files.serial_line:
# 								 #if serial.reject_serial_check == False:  ###babita23								
# 									scount=scount+1
# 									sr_no=scount
# 									product_code11=serial.product_name.default_code
# 									product_name=serial.product_name.id
# 									product_uom=serial.product_uom.id
# 									product_category = serial.product_name.categ_id.id
# 									batch=serial.batch.id
# 									quantity=1
# 									serial_no=serial.serial_name
# 									reject=serial.reject_serial_check
# 									short=serial.short
# 									excess=serial.excess
# 									if serial.short:
# 										quantity=0	

# 									self.pool.get('product.series').create(cr,uid,{'sr_no':sr_no,'grn_no':grn_no,'line_id':series_main,'excess':excess,'short':short,'generic_id':generic_id,'product_code':product_code11,'product_category':product_category,'product_name':product_name,'product_uom':product_uom,'batch':batch,'quantity':quantity,'serial_no':serial_no,'serial_check':True,'reject':reject})
					
# 				indent_id=0
# 		if indent_no:
#   		 for indent_rec in self.pool.get('res.indent').browse(cr,uid,search_indent):
# 			flag=False
# 			for prod_line in indent_rec.order_line: 
# 				if prod_line.state!='received':
# 					flag=True
# 			if not flag:
# 				self.pool.get('res.indent').write(cr,uid,indent_rec.id,{'state':'done'})
# 				###################################If Indent is done delivery order in ready to dispatch state
# 				indent_obj = self.pool.get('res.indent')
# 				stock_transfer_obj = self.pool.get('stock.transfer')
# 				product_transfer_obj = self.pool.get('product.transfer')
# 				material_details_obj =self.pool.get('material.details')
# 				res_indent_id = indent_rec.id
# 				o= self.browse(cr,uid,ids[0])
# 				delivery_challan_no = o.delivery_challan_no
# 				main_grn_id = o.id
# 				new_delivery_type = o.new_delivery_type
# 				if new_delivery_type == 'External Delivery':
# 					delivery_id = indent_obj.browse(cr,uid,res_indent_id).delivery_id.id
# 					if delivery_id:
# 						write_delivery_ref_id =stock_transfer_obj.write(cr,uid,delivery_id,{'delivered_ref_id':delivery_challan_no})
# 						material_search = material_details_obj.search(cr,uid,[('indent_id','=',main_grn_id)])
# 						material_browse = material_details_obj.browse(cr,uid,material_search)
# 						for material_id in material_browse:
# 							material_product_code = material_id.product_code
# 							material_generic_id = material_id.generic_id.id
# 							material_product_name = material_id.product_name.id
# 							batch = material_id.batch.id
# 							manufacturing_date = material_id.manufacturing_date
# 							search_product_transfer = product_transfer_obj.search(cr,uid,[('prod_id','=',delivery_id)])
# 							browse_product_transfer = product_transfer_obj.browse(cr,uid,search_product_transfer)
# 							for browse_id in browse_product_transfer:
# 								main_product_transfer_id = browse_id.id
# 								quantity = browse_id.quantity
# 								product_code = browse_id.product_code
# 								product_name = browse_id.product_name.id
# 								generic_id = browse_id.generic_id.id
# 								qty_indent = browse_id.qty_indent
# 								if product_code == material_product_code and product_name == material_product_name and generic_id == material_generic_id:
# 									product_transfer_obj.write(cr,uid,main_product_transfer_id,{'available_quantity':qty_indent,'batch':batch,'mfg_date':manufacturing_date,'quantity':qty_indent})
# 						stock_transfer_obj.nsd_ready_to_dispatch(cr,uid,[delivery_id],context=context)
# 				##########################################
# 		self.sync_indent_notes_update(cr,uid,ids,context=context)
# 		val_prod_series_srh1 = ''
# 		ci_sync_id = ''
# 		conn_central_flag=False
# 		conn_dispatcher_flag=False		
# 		for i in self.browse(cr, uid, ids):
# 			msg_flag=False
# 			msg_flag_branch=False
# 			msg_flag_stock=False
# 			ci_sync_id = i.ci_sync_id
# 			branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
# 			for branch_id in self.pool.get('res.company').browse(cr,uid,branch_type):

# 				vpn_ip_addr = branch_id.vpn_ip_address
# 				port = branch_id.port
# 				dbname = branch_id.dbname
# 				pwd = branch_id.pwd
# 				user_name = str(branch_id.user_name.login)
# 				username = user_name #the user
# 				pwd = pwd    #the password of the user
# 				dbname = dbname
# 				time_cur = time.strftime("%H%M%S")
# 				date = time.strftime('%Y-%m-%d%H%M%S')
# 				log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
# 				obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
# 				sock_common = xmlrpclib.ServerProxy (log)
# 				try:
# 					raise
# 					uid = sock_common.login(dbname, username, pwd)
# 				except Exception as Err:
# 					#offline_obj=self.pool.get('offline.sync')
# 					#offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
# 					conn_central_flag = True
# 					#if not offline_sync_sequence:
# 					#	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':ids[0],'func_model':'indent_sync_central','error_log':Err,})
# 					#else:
# 					#	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
# 					#	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_central_flag})
					
# ############SQL##########OFFLINE#########SYNC##################################################################################
# 					con_cat = dbname+"-"+branch_id.vpn_ip_address+"-"+'Recieve_Indent-'+str(date)+'_'+str(time_cur)+'.sql'
# 					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
# 					directory_name = str(os.path.expanduser('~')+'/indent_sync/')
# 					sync_str=''
# 					if not os.path.exists(directory_name):
# 						os.makedirs(directory_name)
# 					d = os.path.dirname(directory_name)
# 					ln_ids = ''
# 					count = 0
# 					func_string ="\n\n CREATE OR REPLACE FUNCTION Recieve_Indent() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
# 					declare=" DECLARE \n \t"
# 					var1="""val_prod_series_srh INT;\n remark_srch_id INT; flag1 INT;
#  state1 VARCHAR;
#  flag2 INT;
#  flag3 INT;
#  counter INT;\n \n  BEGIN \n 
#  flag1 =0;
#  flag2 = 0;
#  flag3 =0;
#  counter=0;"""
# 					endif="\n\n END IF; \n"
# 					ret="\n RETURN 1;\n"
# 					elsestr="\n ELSE \n"
# 					final="\nEND; \n $$;\n"
# 					fun_call="\n SELECT Recieve_Indent();\n"
# 					sync_str+= func_string + declare + var1

# 					origin_ids = "(SELECT id FROM stock_picking WHERE ci_sync_id_seq = '"+str(i.ci_sync_id)+"' AND origin = '" +str(i.indent_no) + "')"
					
# 					for ln in i.receive_indent_line:
# 						create_series11 = 0
# 						if ln.product_name.type_product == 'track_equipment':
# 							final_val = "\n UPDATE stock_picking SET test_state = TRUE WHERE id = " + origin_ids + ";"
# 							val_prod_series_srh= "\n val_prod_series_srh = ( SELECT id FROM product_series_main WHERE test= " + origin_ids + ");"
# 							ifstring="\n IF val_prod_series_srh IS NOT NULL THEN \n"
# 							create_series11="\n INSERT INTO product_series_main(test) VALUES ("+origin_ids+");"
# 							val_prod_series_srh1 = "\n val_prod_series_srh = ( SELECT id FROM product_series_main WHERE test= " + origin_ids + ");"
# 							sync_str+= final_val + val_prod_series_srh + ifstring + elsestr + create_series11 + val_prod_series_srh1 + endif

# 							if ln.serial_line:
# 								product_ids = "(SELECT id FROM product_product WHERE name_template ='" + str(ln.generic_id.name.replace("'","''")) + "')"
# 							if ln.generic_id:
# 								generic_ids= "(SELECT id FROM product_generic_name WHERE name = '" +str(ln.generic_id.name) +"')"
# 								for serials in ln.serial_line:
# 									count = count + 1
# 									transporter_create_new=" \n INSERT INTO  product_series ( sr_no, product_code, product_name, generic_id, prod_uom, batch_val, quantity, serial_no, product_category, active_id, serial_check, series_line, reject, short, excess) VALUES ("+ str(count) +",'"+str(ln.product_code) + "'," +product_ids + "," + generic_ids + ",'" + str(ln.product_name.local_uom_id.name) +"','"+ str(ln.batch.batch_no) +"'," +str(serials.quantity) +",'"+ str(serials.serial_name) +"','" + str(serials.product_name.categ_id.name)+"','" + str(serials.active_id) + "','" + str(serials.serial_check) + "',val_prod_series_srh, '" + str(serials.reject_serial_check) + "','" + str(serials.short) + "' , '"+ str(serials.excess) +"');"
# 									sync_str+= transporter_create_new
# 					product_uom_qty = 0
# 					for p in i.receive_indent_line:		
# 						product_ids11="(SELECT id FROM product_product WHERE name_template = '"+ str(p.product_name.name.replace("'","''")) + "')"
# 						stock_val ="( SELECT id FROM stock_move WHERE product_id = " + product_ids11 + " AND picking_id = " + origin_ids +" ORDER BY id LIMIT 1)" 
# 						move_ids= "\n UPDATE stock_move SET  state = 'done' WHERE id = "+stock_val+";"
# 						sync_str += move_ids
# 						if p.notes_one2many:
# 							for material_notes in p.notes_one2many:
# 								user_name=material_notes.user_id
# 								source=material_notes.source.id
# 								comment=material_notes.comment
# 								comment_date=material_notes.comment_date
# 								source_id=0
# 								if material_notes.source:
# 									source_id ="( SELECT id FROM res_company WHERE name='" + str(material_notes.source.name) +"')"
# 								remark_srch_id = "\n remark_srch_id= (SELECT id FROM stock_move_comment_line WHERE  comment = ' "+ str(comment) + "' AND user_id ='"+str(user_name) + "' AND source = "+ source_id + " AND comment_date = '"+ str(comment_date) + "' AND indent_id = " + stock_val + ");"
# 								ifstr="\n IF remark_srch_id IS NOT NULL THEN \n"
# 								remark_srch_del="\n DELETE FROM stock_move_comment_line WHERE id in (remark_srch_id);"
								
# 								msg_flag=True
# 								msg_unread_ids="\n UPDATE stock_move SET msg_check_unread=True,msg_check_read=False WHERE id= "+ stock_val +";"
# 								notes_line_id="\n INSERT INTO stock_move_comment_line (indent_id,user_id,source,comment_date,comment) VALUES ("+ stock_val +",'"+str(user_name)+"',"+source_id+",'"+str(comment_date)+"','"+str(comment)+"');"
# 								sync_str += remark_srch_id + ifstr + remark_srch_del + elsestr + msg_unread_ids + endif + notes_line_id
# 					if i.comment_line:						
# 						for notes_line in i.comment_line:
# 							if notes_line.source:
# 								source_id	="(SELECT id FROM res_company WHERE name='" +str(notes_line.source.name)+"')"
# 								remark_srch_id = "\n remark_srch_id=( SELECT id FROM indent_remark WHERE remark_field ='"+str(notes_line.comment) +"' AND \"user\" ='"+str(notes_line.user_id)+"' AND remark = " + origin_ids+" AND date='"+str(notes_line.comment_date)+ "' AND source = "+ source_id +");"
# 								ifstr="\n IF remark_srch_id IS NOT NULL THEN \n "
# 								notes_line_id="\n UPDATE indent_remark SET \"user\"='"+str(notes_line.user_id if notes_line.user_id else '')+"', source="+ source_id +", date= '"+str(notes_line.comment_date)+ "', remark_field= '"+str(notes_line.comment) +"' WHERE id in (remark_srch_id);"
# 								notes_line_ids="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (" + origin_ids + ",'" + str(notes_line.user_id if notes_line.user_id else '')+ "'," + source_id + ",'" + str(notes_line.comment_date) + "','" + str(notes_line.comment) +"');"
# 								sync_str += remark_srch_id + ifstr + notes_line_id + elsestr + notes_line_ids + endif
								
# 					if msg_flag :
# 						msg_ids="\n UPDATE stock_picking SET msg_check = True WHERE id = " +origin_ids +";"
# 						sync_str += msg_ids
# 					sync_str += '''FOR state1 IN (SELECT state FROM stock_move WHERE picking_id='''+origin_ids+''') 
# LOOP 
# IF state1 != 'done' AND state1 IS NOT NULL THEN
# flag1 =1;
# END IF;
# IF state1 != 'cancel' AND state1 IS NOT NULL THEN
# flag2 =1;
# END IF;
# IF state1 = 'cancel' OR state1 = 'done' THEN
# flag3 =1;
# END IF;
# IF state1 ='draft' OR state1 ='view_order' OR state1 ='waiting' OR state1 ='confirmed' OR state1 ='pending' OR state1 ='assigned' OR state1 ='packlist' OR state1 ='ready' OR state1 ='progress' OR state1 ='partial_received' THEN
# counter = 1;
# END IF;
# END LOOP;
# IF flag1=0 THEN
# UPDATE stock_picking SET state='done' WHERE id='''+origin_ids+''';
# END IF;
# IF flag2=0 THEN
# UPDATE stock_picking SET state='cancel' WHERE id='''+origin_ids+''';
# END IF;
# IF flag2=1 AND counter=0 AND flag1=1 AND flag3 =1 THEN
# UPDATE stock_picking SET state='done' WHERE id='''+origin_ids+''';
# END IF;'''
# 					sync_str +=ret+final+fun_call
# 					with open(filename,'a') as f :
# 						f.write(sync_str)
# 						f.close()
#  ###############################################################################################################################
# 				sock = xmlrpclib.ServerProxy(obj)
# 				if conn_central_flag==False:
# 					ln_ids = ''
# 					count = 0
# 					origin_srch = [('id','=',i.ci_sync_id),('origin', '=', i.indent_no)]
# 					origin_ids = sock.execute(dbname, userid, pwd, 'stock.picking', 'search', origin_srch)
# 					if origin_ids:
# 						for ln in i.receive_indent_line:
# 							create_series11 = 0
# 							if ln.product_name.type_product == 'track_equipment':
# 								button_attrs =  {
# 												    'test_state':True
# 												}
											
# 								final_val = sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids[0], button_attrs)
# 								prod_series_srh = [('test', '=',origin_ids[0])]
# 								val_prod_series_srh = sock.execute(dbname, userid, pwd, 'product.series.main', 'search', prod_series_srh)
# 								if val_prod_series_srh:
# 										create_series11 = val_prod_series_srh[0]
# 								if val_prod_series_srh == []:
# 										product_series_main =  {
# 											'test':origin_ids[0],
# 															    }
# 										val_prod_series_srh1 = sock.execute(dbname, userid, pwd, 'product.series.main', 'create', product_series_main)
# 										create_series11 = val_prod_series_srh1
# 								if ln.serial_line:
# 									product_srch = [('name', '=',ln.product_name.name)]
# 									product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)	
# 								if ln.generic_id:
# 									generic_srch=[('name','=',ln.generic_id.name)]
# 									generic_ids=sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_srch)						
# 									for serials in ln.serial_line:
# 										count = count + 1
# 										series_create = {
# 													    'sr_no':count,
# 													    'product_code':ln.product_code,
# 													    'product_name':product_ids[0],
# 													    'generic_id':generic_ids[0] if generic_ids else False,
# 													    'prod_uom':ln.product_name.local_uom_id.name,
# 													    'batch_val':ln.batch.batch_no,
# 													    'quantity':serials.quantity,
# 													    'serial_no':serials.serial_name,
# 													    'product_category':serials.product_name.categ_id.name,
# 													    'active_id':serials.active_id,
# 													    'serial_check':serials.serial_check,
# 													    'series_line':create_series11,
# 													    'reject':serials.reject_serial_check,
# 													    'short':serials.short,
# 													    'excess':serials.excess,
# 													    }
# 										transporter_create_new = sock.execute(dbname, userid, pwd, 'product.series', 'create', series_create)
# 					product_uom_qty = 0
# 					for p in i.receive_indent_line:
# 							    product_srch = [('name', '=',p.product_name.name)]
# 							    product_ids11 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
# 							    stock_move_srh = [('product_id', '=',product_ids11[0]),('picking_id','=',origin_ids[0])]
# 							    stock_val = sock.execute(dbname, userid, pwd, 'stock.move', 'search', stock_move_srh)
# 							    if stock_val:
# 								    pick_line = {
# 											    'state':'done'
# 											    }
# 								    move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', stock_val[0], pick_line)
# 								    if p.notes_one2many:
# 									    for material_notes in p.notes_one2many:
# 										    user_name=material_notes.user_id
# 										    source=material_notes.source.id
# 										    comment=material_notes.comment
# 										    comment_date=material_notes.comment_date
# 										    source_id=0
# 										    if material_notes.source:
# 											    source_srch = [('name','=',material_notes.source.name)]
# 											    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

# 										    remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',stock_val[0])]
# 										    remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
# 										    if remark_srch_id:
# 										       for test in remark_srch_id:
# 											    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)
# 										    if not remark_srch_id:
# 											    msg_flag=True
# 											    msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
# 												    }
# 											    msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',stock_val,msg_unread)

# 										    notes_line = {
# 												                       	'indent_id':stock_val[0],
# 																	'user_id':user_name if user_name else '',
# 																	'source':source_id[0] if source_id else '',
# 												                       	'comment_date':comment_date,
# 												                       	'comment':comment,
# 												                       }
# 										    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
# 					if i.comment_line:
# 					    for notes_line in i.comment_line:
# 						    if notes_line.source:
# 							    source_srch = [('name','=',notes_line.source.name)]
# 							    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
# 							    remark_srch = [('remark_field','=',notes_line.comment),('user','=',notes_line.user_id),('remark','=',origin_ids[0]),('date','=',notes_line.comment_date),('source','=',source_id[0])]
# 							    remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)	
# 							    if remark_srch_id:
# 								    for k in remark_srch_id:					
# 									    notes_line_dict = {
# 												    'user':notes_line.user_id if notes_line.user_id else '',
# 												    'source':source_id[0] if source_id else '',
# 												    'date':notes_line.comment_date,
# 												    'remark_field':notes_line.comment,
# 												     }
# 									    notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', k , notes_line_dict)
# 							    else:
# 									    msg_flag=True
# 									    create_notes_line = {
# 														    'remark':origin_ids[0],
# 														    'user':notes_line.user_id if notes_line.user_id else '',
# 														    'source':source_id[0] if source_id else '',
# 														    'date':notes_line.comment_date,
# 														    'remark_field':notes_line.comment,
# 														    }
# 									    notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)

# 					if msg_flag:
# 						    msg_line = {
# 											    'msg_check':True
# 										       }
# 						    msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids, msg_line)
# 					self.write(cr,uid,ids,{'sync_central_indent':False})
# 				elif conn_central_flag==True:
# 					self.write(cr,uid,ids,{'sync_central_indent':True})


# 			stock_val=''
# 			vpn_ip_addr = i.source_company.vpn_ip_address
# 			port = i.source_company.port
# 			dbname = i.source_company.dbname
# 			pwd = i.source_company.pwd
# 			user_name = str(i.source_company.user_name.login)

# 			username = user_name #the user
# 			pwd = pwd    #the password of the user
# 			dbname = dbname
# 			time_cur = time.strftime("%H%M%S")
# 			date = time.strftime('%Y-%m-%d%H%M%S')
# 			log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
# 			obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
# 			sock_common = xmlrpclib.ServerProxy (log)
# 			try:
# 				raise
# 				uid = sock_common.login(dbname, username, pwd)
# 			except Exception as Err:
# 				#offline_obj=self.pool.get('offline.sync')
# 				#offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
# 				conn_dispatcher_flag = True
# 				#if not offline_sync_sequence:
# 				#	offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':i.source_company.id,'srch_condn':False,'form_id':ids[0],'func_model':'indent_sync_branch','error_log':Err,})
# 				#else:
# 				#	offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
# 				#	offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_dispatcher_flag})
			        
# 				##########SQL######################OFFLINE#################SYNC##############################################
			
# 				con_cat = dbname+"-"+branch_id.vpn_ip_address+"-"+'Recieve_Indent-'+str(date)+'_'+str(time_cur)+'.sql'
# 				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
# 				directory_name = str(os.path.expanduser('~')+'/indent_sync/')
# 				sync_str=''
# 				if not os.path.exists(directory_name):
# 					os.makedirs(directory_name)
# 				d = os.path.dirname(directory_name)
# 				ln_ids = ''
# 				count = 0
# 				func_string ="\n\n CREATE OR REPLACE FUNCTION Recieve_Indent() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
# 				declare=" DECLARE \n \t"
# 				var1=""" origin_stock_transfer INT;\n remark_srch_id INT; \n flag1 INT;
#  state1 VARCHAR;
#  flag2 INT;
#  flag3 INT;
#  counter INT;\n \n  BEGIN \n 
#  flag1 =0;
#  flag2 = 0;
#  flag3 =0;
#  counter=0;"""
# 				endif="\n\n END IF; \n"
# 				ret="\n RETURN 1;\n"
# 				elsestr="\n ELSE \n"
# 				final="\nEND; \n $$;\n"
# 				fun_call="\n SELECT Recieve_Indent();\n"
# 				sync_str += func_string + declare + var1
# 				origin_ids_qq ="(SELECT id FROM stock_picking WHERE id = "+str(i.stock_id) + " AND origin = '" +str(i.indent_no) + "')" 
# 				product_uom_qty = 0
# 				for p in i.receive_indent_line:
# 					product_ids11 = "(SELECT id FROM product_product WHERE name_template ='" + str(p.product_name.name.replace("'","''")) + "')"
# 					stock_val ="( SELECT id FROM stock_move WHERE product_id = " + product_ids11 + " AND picking_id = " + origin_ids_qq +"order by id LIMIT 1)" 
# 					move_ids= "\n UPDATE stock_move SET  state = 'done' WHERE id = "+stock_val+";"
# 					sync_str += move_ids
# 					if p.notes_one2many:
# 						for material_notes in p.notes_one2many:
# 							user_name=material_notes.user_id
# 							source=material_notes.source.id
# 							comment=material_notes.comment
# 							comment_date=material_notes.comment_date
# 							source_id=0
# 							if material_notes.source:
# 								source_id ="( SELECT id FROM res_company WHERE name='" + str(material_notes.source.name) +"')"
# 							remark_srch_id = "\n remark_srch_id= (SELECT id FROM stock_move_comment_line WHERE  comment = '"+ str(comment) + "' AND user_id ='"+str(user_name) + "' AND source = "+ source_id + " AND comment_date = '"+ str(comment_date) + "' AND indent_id = " + stock_val + ");"
# 							ifstr="\n IF remark_srch_id IS NOT NULL THEN \n"
# 							remark_srch_del="\n DELETE FROM stock_move_comment_line WHERE id in (remark_srch_id);"
							
# 							msg_flag_branch=True
# 							msg_unread_ids="\n UPDATE stock_move SET msg_check_unread=True,msg_check_read=False WHERE id= "+ stock_val +";"
# 							notes_line_id="\n INSERT INTO stock_move_comment_line (indent_id,user_id,source,comment_date,comment) VALUES ("+ stock_val +",'"+str(user_name)+"',"+source_id+",'"+str(comment_date)+"','"+str(comment)+"');"
# 							sync_str += remark_srch_id + ifstr + remark_srch_del + elsestr + msg_unread_ids + endif + notes_line_id
# 				if i.comment_line:						
# 					for notes_line in i.comment_line:
# 						if notes_line.source:
# 							source_id	="(SELECT id FROM res_company WHERE name='" +str(notes_line.source.name)+"')"
# 						remark_srch_id = "\n remark_srch_id=( SELECT id FROM indent_remark WHERE remark_field ='"+str(notes_line.comment) +"' AND \"user\" ='"+str(notes_line.user_id)+"' AND remark = " + origin_ids_qq+" AND date='"+str(notes_line.comment_date)+ "' AND source = "+ source_id +");"
# 						ifstr="\n IF remark_srch_id IS NOT NULL THEN \n "
# 						notes_line_id="\n UPDATE indent_remark SET \"user\"='"+str(notes_line.user_id if notes_line.user_id else '')+"', source="+ source_id +", date= '"+str(notes_line.comment_date)+ "', remark_field= '"+str(notes_line.comment) +"' WHERE id in (remark_srch_id);"
# 						notes_line_ids="\n INSERT INTO indent_remark (remark,\"user\",source,date,remark_field) VALUES (" + origin_ids_qq + ",'" + str(notes_line.user_id if notes_line.user_id else '')+ "'," + source_id + ",'" + str(notes_line.comment_date) + "','" + str(notes_line.comment) +"');"
# 						sync_str += remark_srch_id + ifstr + notes_line_id + elsestr + notes_line_ids + endif
# 				if msg_flag_branch:
# 					msg_ids="\n UPDATE stock_picking SET msg_check = True WHERE id = " +origin_ids_qq +";"
# 					sync_str += msg_ids
# 				origin_stock_transfer ="\n origin_stock_transfer = ( SELECT id FROM stock_transfer WHERE stock_transfer_no ='"+ str(i.order_number) + "' AND origin ='" + str(i.indent_no) + "');"
# 				move_ids=" \n UPDATE stock_transfer SET state ='done' WHERE id= origin_stock_transfer ;"
# 				sync_str += origin_stock_transfer + move_ids
# 				if i.comment_line:
# 					for notes_line in i.comment_line:
# 						if notes_line.source:
# 							source_id="(SELECT id FROM res_company WHERE name='" +str(notes_line.source.name)+"')"
# 						remark_srch_id = "\n remark_srch_id=( SELECT id FROM stock_transfer_remarks WHERE name ='"+str(notes_line.comment) +"' AND user_name ='"+str(notes_line.user_id)+"' AND stock_transfer_id =  origin_stock_transfer AND date='"+str(notes_line.comment_date) +"');"
# 						ifstr="\n IF remark_srch_id IS NOT NULL THEN \n "
# 						notes_line_id="\n UPDATE stock_transfer_remarks SET user_name='"+str(notes_line.user_id if notes_line.user_id else '')+"', source="+ source_id +", date= '"+str(notes_line.comment_date)+ "', name= '"+str(notes_line.comment) +"' WHERE id in (remark_srch_id);"
# 						notes_line_ids="\n INSERT INTO stock_transfer_remarks (stock_transfer_id, user_name, source, date, name) VALUES ( origin_stock_transfer ,'" + str(notes_line.user_id if notes_line.user_id else '')+ "'," + source_id + ",'" + str(notes_line.comment_date) + "','" + str(notes_line.comment) +"');"
# 						sync_str += remark_srch_id + ifstr + notes_line_id + elsestr + notes_line_ids + endif
				
# 				for ln in i.receive_indent_line:
# 					for serials in ln.serial_line:
# 						if serials.reject_serial_check or serials.short:
# 							reject_serial_check = serials.reject_serial_check				
# 							search_val_prod="(SELECT id FROM product_series WHERE serial_no = '"+ str(serials.serial_name) + "')"
# 							search_val22="(SELECT id FROM transfer_series WHERE serial_no ="+ search_val_prod +")"
# 							create_series="\n UPDATE transfer_series SET reject_serial_check = '"+str(serials.reject_serial_check) +", short = '"+str(serials.short) +" WHERE id = "+ search_val22 + ";"
# 							sync_str += create_series
# 					product_ids11 = "(SELECT id FROM product_product WHERE name_template = '" + str(ln.product_name.name.replace("'","''")) + "')"
# 					rec_search_val="(SELECT id FROM product_transfer WHERE product_name = "+ product_ids11 + " AND prod_id =  origin_stock_transfer )"
					
# 					if ln.notes_one2many:
# 						for material_notes in ln.notes_one2many:
# 							user_name=material_notes.user_id
# 							source=material_notes.source.id
# 							comment=material_notes.comment
# 							comment_date=material_notes.comment_date
# 							source_id=''
# 							if material_notes.source:
# 								source_id ="(SELECT id FROM res_company WHERE name = '"+ str(material_notes.source.name) +"')"
# 							remark_srch_id = "\n remark_srch_id= (SELECT id FROM product_transfer_comment_line WHERE  comment = ' "+ str(comment) + "' AND user_id ='"+str(user_name) + "' AND source = "+ source_id + " AND comment_date = '"+ str(comment_date) + "' AND indent_id = " + rec_search_val + ");"
# 							ifstr="\n IF remark_srch_id IS NOT NULL THEN \n"
# 							remark_srch_del="\n DELETE FROM product_transfer_comment_line WHERE id in (remark_srch_id);"
							
# 							msg_flag_stock=True
# 							msg_unread_ids="\n UPDATE product_transfer SET msg_check_unread=True,msg_check_read=False WHERE id= "+ rec_search_val +";"
# 							notes_line_id="\n INSERT INTO product_transfer_comment_line (indent_id,user_id,source,comment_date,comment) VALUES ("+ rec_search_val +",'"+str(user_name)+"',"+source_id+",'"+str(comment_date)+"','"+str(comment)+"');"
# 							sync_str += remark_srch_id + ifstr + remark_srch_del + elsestr + msg_unread_ids + endif + notes_line_id
# 				if msg_flag_stock:
# 					msg_ids="\n UPDATE stock_picking SET msg_check = True WHERE id = " +origin_ids_qq +";"
# 					sync_str += msg_ids
# 				sync_str += '''\n FOR state1 IN (SELECT state FROM stock_move WHERE picking_id='''+origin_ids_qq+''') 
# LOOP 
# IF state1 != 'done' THEN
# flag1 =1;
# END IF;
# IF state1 != 'cancel' THEN
# flag2 =1;
# END IF;
# IF state1 = 'cancel' OR state1 = 'done' THEN
# flag3 =1;
# END IF;
# IF state1 ='draft' OR state1 ='view_order' OR state1 ='waiting' OR state1 ='confirmed' OR state1 ='pending' OR state1 ='assigned' OR state1 ='packlist' OR state1 ='ready' OR state1 ='progress' OR state1 ='partial_received' THEN
# counter = 1;
# END IF;
# END LOOP;
# IF flag1=0 THEN
# UPDATE stock_picking SET state='done' WHERE id='''+origin_ids_qq+''';
# END IF;
# IF flag2=0 THEN
# UPDATE stock_picking SET state='cancel' WHERE id='''+origin_ids_qq+''';
# END IF;
# IF flag2=1 AND counter=0 AND flag1=1 AND flag3 =1 THEN
# UPDATE stock_picking SET state='done' WHERE id='''+origin_ids_qq+''';
# END IF;'''
#   				sync_str += ret + final + fun_call
# 				with open(filename,'a') as f :
# 					f.write(sync_str)
# 					f.close()		
# 				#print Mahesh 
# ##################################################################################################################################
# 			sock = xmlrpclib.ServerProxy(obj)
# 			if conn_dispatcher_flag == False:
# 			    origin_srch_qq = [('id', '=',i.stock_id),('origin', '=',i.indent_no)]
# 			    origin_ids_qq = sock.execute(dbname, userid, pwd,'stock.picking', 'search', origin_srch_qq)
# 			    product_uom_qty = 0
# 			    for p in i.receive_indent_line:
# 				    product_srch = [('name', '=',p.product_name.name)]
# 				    product_ids11 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
# 				    stock_move_srh = [('product_id', '=',product_ids11[0]),('picking_id','=',origin_ids_qq[0])]
# 				    stock_val = sock.execute(dbname, userid, pwd, 'stock.move', 'search', stock_move_srh)
# 				    if stock_val:
# 				          pick_value = {
# 							    'state':'done'
# 							    }
# 				          move_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write', stock_val[0], pick_value)	
# 				          if p.notes_one2many:
# 							    for material_notes in p.notes_one2many:
# 										    user_name=material_notes.user_id
# 										    source=material_notes.source.id
# 										    comment=material_notes.comment
# 										    comment_date=material_notes.comment_date
# 										    source_id=0
# 										    if material_notes.source:
# 											    source_srch = [('name','=',material_notes.source.name)]
# 											    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

# 										    remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',stock_val[0])]
# 										    remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'search', remark_srch)
# 										    if remark_srch_id:
# 										       for test in remark_srch_id:
# 											    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'unlink', test)

# 										    if not remark_srch_id:
# 											    msg_flag_branch=True
# 											    msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
# 												    }
# 											    msg_unread_ids= sock.execute(dbname, userid, pwd, 'stock.move', 'write',stock_val,msg_unread)

# 										    notes_line = {
# 												                        'indent_id':stock_val[0],
# 												                        'user_id':user_name if user_name else '',
# 																	    'source':source_id[0] if source_id else '',
# 												                        'comment_date':comment_date,
# 												                        'comment':comment,
# 												                       }
# 										    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.move.comment.line', 'create', notes_line)
# 			    if i.comment_line:
# 				    for notes_line in i.comment_line:
# 					    if notes_line.source:
# 						    source_srch = [('name','=',notes_line.source.name)]
# 						    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
# 					    remark_srch = [('remark','=',origin_ids_qq),('remark_field','=',notes_line.comment),('user','=',notes_line.user_id),('date','=',notes_line.comment_date),('source','=',source_id[0])]
# 					    remark_srch_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'search', remark_srch)	
# 					    if remark_srch_id:
# 						    for k in remark_srch_id:					
# 							    notes_line = {
# 										    'user':notes_line.user_id if notes_line.user_id else '',
# 										    'source':source_id[0] if source_id else '',
# 										    'date':notes_line.comment_date,
# 										    'remark_field':notes_line.comment,
# 										      }
# 							    notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', k , notes_line)

# 					    else:
# 						    msg_flag_branch
# 						    create_notes_line = {
# 											    'remark':origin_ids_qq[0],
# 											    'user':notes_line.user_id if notes_line.user_id else '',
# 											    'source':source_id[0] if source_id else '',
# 											    'date':notes_line.comment_date,
# 											    'remark_field':notes_line.comment,
# 											    }
# 						    notes_line_ids = sock.execute(dbname, userid, pwd, 'indent.remark', 'create', create_notes_line)

# 			    if msg_flag_branch:
# 				    msg_line = {
# 											    'msg_check':True
# 										       }
# 				    msg_ids= sock.execute(dbname, userid, pwd, 'stock.picking', 'write', origin_ids_qq, msg_line)				
#     #sync for stock transfer of the Dispatcher
# 			    o_srch = [('stock_transfer_no', '=',i.order_number),('origin','=',i.indent_no)]
# 			    origin_stock_transfer = sock.execute(dbname, userid, pwd, 'stock.transfer', 'search', o_srch)
# 			    if origin_stock_transfer:
# 				    pick_line = {
# 								    'state':'done'
# 						      	 			}
# 				    move_ids= sock.execute(dbname, userid, pwd, 'stock.transfer', 'write',origin_stock_transfer[0], pick_line)
# 			    if i.comment_line:
# 				    for notes_line in i.comment_line:
# 					    if notes_line.source:
# 						    source_srch = [('name','=',notes_line.source.name)]
# 					    remark_srch = [('name','=',notes_line.comment),('user_name','=',notes_line.user_id),('stock_transfer_id','=',origin_stock_transfer[0]),('date','=',notes_line.comment_date)]
# 					    remark_srch_id = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'search', remark_srch)			
								
# 					    if remark_srch_id:
# 						    for variable in remark_srch_id:	
# 							    notes_lines = {
# 										    'user_name':notes_line.user_id if notes_line.user_id else '',
# 										    'source':source_id[0] if source_id else '',
# 										    'date':notes_line.comment_date,
# 										    'name':notes_line.comment,
# 										    }
# 							    notes_line_id = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'write', variable, notes_lines)
# 					    else:
# 							    msg_flag_stock=True
# 							    create_notes_line = {
# 												    'stock_transfer_id':origin_stock_transfer[0],
# 												    'user_name':notes_line.user_id if notes_line.user_id else '',
# 												    'source':source_id[0] if source_id else '',
# 												    'date':notes_line.comment_date,
# 												    'name':notes_line.comment,
# 										                           }
# 							    notes_line_ids = sock.execute(dbname, userid, pwd, 'stock.transfer.remarks', 'create', create_notes_line)

# 			    if origin_stock_transfer:
# 				    for ln in i.receive_indent_line:
# 					    for serials in ln.serial_line:
# 						    if serials.reject_serial_check or serials.short:
# 							    reject_serial_check = serials.reject_serial_check
# 							    search_val = [('serial_no', '=',serials.serial_name)]
# 							    search_val_prod = sock.execute(dbname, userid, pwd, 'product.series', 'search', search_val)	
# 							    if search_val_prod:
# 								    search_2 = [('serial_no', '=',search_val_prod[0])]
# 								    search_val22 = sock.execute(dbname, userid, pwd, 'transfer.series', 'search', search_2)
# 								    if search_val22:
# 									    reject_serial_check_val = {'reject_serial_check':serials.reject_serial_check,'short':serials.short}
# 									    create_series = sock.execute(dbname, userid, pwd, 'transfer.series', 'write',search_val22[0], reject_serial_check_val)
# 					    product_srch = [('name', '=',ln.product_name.name)]
# 					    product_ids11 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
# 					    rec_search = [('product_name', '=',product_ids11[0]),('prod_id','=',origin_stock_transfer[0])]
# 					    rec_search_val = sock.execute(dbname, userid, pwd, 'product.transfer', 'search', rec_search)
# 					    if rec_search_val:
# 						    if ln.notes_one2many:
# 							    for material_notes in ln.notes_one2many:
# 									    user_name=material_notes.user_id
# 									    source=material_notes.source.id
# 									    comment=material_notes.comment
# 									    comment_date=material_notes.comment_date
# 									    source_id=0
# 									    if material_notes.source:
# 										    source_srch = [('name','=',material_notes.source.name)]
# 										    source_id = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)

# 									    remark_srch = [('comment','=',comment),('user_id','=',user_name),('source','=',source_id[0]),('comment_date','=',comment_date),('indent_id','=',rec_search_val[0])]
# 									    remark_srch_id = sock.execute(dbname, userid, pwd, 'product.transfer.comment.line', 'search', remark_srch)
# 									    if remark_srch_id:
# 									       for test in remark_srch_id:
# 										    notes_line_id = sock.execute(dbname, userid, pwd, 'product.transfer.comment.line', 'unlink', test)

# 									    if not remark_srch_id:
# 											    msg_flag_stock=True
# 											    msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
# 												    }
# 											    msg_unread_ids= sock.execute(dbname, userid, pwd, 'product.transfer', 'write',rec_search_val,msg_unread)

# 									    notes_line = {
# 															'indent_id':rec_search_val[0],
# 															'user_id':user_name if user_name else '',
# 															'source':source_id[0] if source_id else '',
# 															'comment_date':comment_date,
# 															'comment':comment,
# 										                           }
# 									    notes_line_id = sock.execute(dbname, userid, pwd, 'product.transfer.comment.line', 'create', notes_line)

# 			    if msg_flag_stock:
# 				    msg_line = {
# 											    'msg_check':True
# 										       }
# 				    msg_ids= sock.execute(dbname, userid, pwd, 'stock.transfer', 'write',origin_stock_transfer, msg_line)
# 			    self.write(cr,uid,ids,{'sync_dispatcher_indent':False})									    						    	
# 			elif conn_dispatcher_flag==True:	
# 			    self.write(cr,uid,ids,{'sync_dispatcher_indent':False})				    

# 		return True



	
	# Conversion Original Method havin birdpro concept 
	def nsd_generate_grn(self, cr, uid,ids,vals, context=None):
		for i in self.browse(cr,uid,ids,context):
			if i.delivery_type_others == 'material_return':
				if context is None : context = {} 
				exp_date = ccount = account = bcount = ''
				prod_qty_local = series_main = prod_qty = ''
				transporter_name = godown='' #HHH
				count = qqqty = c = local_qty=godown_stock=0 #MHA
				qty_received = 0.0
				conn_flag=False
				self.material_notes_update(cr,uid,ids,context=context)
				for var_stn in self.browse(cr,uid,ids):
					if not var_stn.receive_indent_line_for_material_ret:
						raise osv.except_osv(('Alert!'),('No Products to generate GRN in Product line'))
				
				for brw_batch in self.browse(cr,uid,ids):
					godown=brw_batch.branch_name.id
					for batch_line in brw_batch.receive_indent_line_for_material_ret:
						product_name = batch_line.product_name.id
						batch = batch_line.batch.id
						if batch_line.product_qty==0:
							raise osv.except_osv(('Alert!'),('Total Ordered Quantity Should be greater than 0.'))
						srch = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',batch),('branch_name','=',godown)])
						for batch_brw in self.pool.get('res.batchnumber').browse(cr,uid,srch):
							if product_name != batch_brw.name.id:
								raise osv.except_osv(('Alert!'),('Please select proper Product Name to assign the batch.'))
							
				for var in self.browse(cr,uid,ids):
					godown=var.branch_name.id
					cc_date = datetime.now()
					c_date=datetime.strftime(cc_date,"%Y-%m-%d %H:%M:%S")
					current_date = datetime.now().date()
					monthee = current_date.month
					current_year = current_date.year
					day = current_date.day
					#partner_seq=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
					grn_number=self._get_grn_no(cr,uid,ids,context=None)
					check='False'
					tag_check= serial_id_check=False
					for lines in var.receive_indent_line_for_material_ret:
						if lines.product_name.type_product=='track_equipment':
							check='True'
						if lines.product_name.product_tag_id:
							tag_check=True
						if lines.product_name.stationary_track_no:
							serial_id_check=True
					grn_date= time.strftime("%Y-%m-%d %H:%M:%S")
					self.pool.get('receive.indent').write(cr,uid,var.id,{
											'grn_no':grn_number,
											'state':'done',
											'grn_date':grn_date,
											'check_product_serial':check,
											'tag_check':tag_check,
											'serial_id_check':serial_id_check,
											'branch_name':godown,})
					print "--------------------------------------------"
					grn_no = var.grn_no
					for files in var.receive_indent_line_for_material_ret:
						manufacturing_date = files.manufacturing_date
						product_code = files.product_code
						qty_received = files.qty_received
						product_name = files.product_name.id
						if not files.batch:
							raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(files.product_name.name_template))
						if files.product_name.batch_type=='applicable' and not files.manufacturing_date:
							raise osv.except_osv(('Alert!'),('Please Enter Manufacturing Date of the Product.'))
						elif files.product_name.batch_type=='applicable' and files.manufacturing_date:
							n_product_srch = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
							for n_brw_product in self.pool.get('product.product').browse(cr,uid,n_product_srch):
								qqqty = n_brw_product.quantity_available
								shelf_life = n_brw_product.shelf_life
								exp_date = self.add_months(manufacturing_date,shelf_life)
								prod_qty=n_brw_product.quantity_available+files.qty_received
								
								if files.product_name.type_product != 'track_equipment':
									self.pool.get('product.product').write(cr,uid,n_brw_product.id,{'check_batch':True,'quantity_available':prod_qty,})
									self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{
												'manufacturing_date':manufacturing_date,
												'exp_date':exp_date,
												'qty':files.batch.qty+files.qty_received,
												'st':files.price_unit,})
	
									n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',godown)])
									godown_stock=0.0
									if n_brw_product.uom_id.id != n_brw_product.local_uom_id.id:
										for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
											godown_stock+=n_batch_ids.local_qty
										godown_stock=(godown_stock-(files.qty_received*files.product_name.local_uom_relation)) if godown_stock else 0
										local_qty=files.qty_received*n_brw_product.local_uom_relation
										# prod_qty_local = files.product_name.quantity_available * files.product_name.local_uom_relation
									elif n_brw_product.uom_id.id == n_brw_product.local_uom_id.id:
										for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
											godown_stock+=n_batch_ids.qty
										godown_stock=(godown_stock-files.qty_received) if godown_stock else 0
										local_qty=files.qty_received
										# prod_qty_local = files.product_name.quantity_available
									ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{
											'ids':files.batch.id,
											'product_id':product_name,
											'date':current_date,
											'day':day,
											'datetime':c_date,
											'received':True,
											'qty':local_qty,
											'year':current_year,
											'month':monthee,
											'product_qty':godown_stock ,
											'branch_name':godown})#HHH
						elif (files.product_name.batch_type=='non_applicable' or not files.product_name.batch_type):
							if files.product_name.type_product != 'track_equipment':
								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+qty_received,'st':files.price_unit,})
								n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',godown)]) 
								# print "  14 current company == ",i.company_id.name
								# n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',i.company_id.id)])
								godown_stock=0.0
	
								if files.product_name.uom_id.id != files.product_name.local_uom_id.id:
									for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
										godown_stock+=n_batch_ids.local_qty
									godown_stock=(godown_stock-(files.qty_received*files.product_name.local_uom_relation)) if godown_stock else 0
									local_qty=files.qty_received*files.product_name.local_uom_relation
									
								elif files.product_name.uom_id.id == files.product_name.local_uom_id.id:
									for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
										godown_stock+=n_batch_ids.qty
									godown_stock=(godown_stock-files.qty_received) if godown_stock else 0
									local_qty=files.qty_received
									
								ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{
												'ids':files.batch.id,
												'product_id':product_name,
												'date':current_date,
												'day':day,
												'datetime':c_date,
												'received':True,
												'qty':local_qty,
												'year':current_year,
												'month':monthee,
												'product_qty':godown_stock ,
												 'branch_name':godown}) #HHH
							self.pool.get('product.product')._update_product_quantity(cr,uid,[files.batch.name.id])
					
				for rec in self.browse(cr,uid,ids):
					for line in rec.receive_indent_line_for_material_ret:
						ret_qty = line.qty_received
						stck_asgn_search=self.pool.get('stock.assignment').search(cr,uid,[('id','=',rec.stock_assign_id.id)])
						for sa in self.pool.get('stock.assignment').browse(cr,uid,stck_asgn_search):
							for stck_asgn_line in sa.stock_assignment_line:
								if line.product_name == stck_asgn_line.product_name:
									self.pool.get('product.assignment').write(cr,uid,[stck_asgn_line.id],{'returned_qty':ret_qty})
									self.pool.get('stock.assignment').write(cr,uid,[sa.id],{'return_bool':True})		
			else:
				if context is None : context = {} 
				exp_date = ccount = account = bcount = ''
				prod_qty_local = series_main = prod_qty = ''
				transporter_name = godown='' #HHH
				count = qqqty = c = local_qty=godown_stock=0 #MHA
				qty_received = 0.0
				conn_flag=False
				self.material_notes_update(cr,uid,ids,context=context)
				for var_stn in self.browse(cr,uid,ids):
					if not var_stn.receive_indent_line:
						raise osv.except_osv(('Alert!'),('Please Add product line before Receive Grn.'))
					if var_stn.delivery_type_others in ('banned_st','excess_st','inter_branch_st'):
						stn_no=var_stn.stn_no.id
						for stn_var in self.pool.get('branch.stock.transfer').browse(cr,uid,[stn_no]):
							state=stn_var.state
							if state=='cancel':
								raise osv.except_osv(('Alert!'),('You can not proceed with cancelled order'))
						for files in var_stn.receive_indent_line:
							manufacturing_date = files.manufacturing_date
							product_code = files.product_code
							qty_received = files.qty_received
							product_name = files.product_name.id
							reject_qty=files.reject
							product_category = files.product_name.categ_id.id
							flag=False
							reject_count=0
							if files.product_name.type_product == 'track_equipment':
								if not files.serial_line:
									search_serial=self.pool.get('transfer.series').search(cr,uid,[('stn_no','=',files.stn_no),('product_name','=',files.product_name.id)])
									for rec in search_serial:
										self.pool.get('transfer.series').write(cr,uid,rec,{'series_line':files.id,'product_category':product_category})
				for brw_batch in self.browse(cr,uid,ids):
					godown=brw_batch.branch_name.id
					for batch_line in brw_batch.receive_indent_line:
						product_name = batch_line.product_name.id
						batch = batch_line.batch.id
						if batch_line.product_qty==0:
							raise osv.except_osv(('Alert!'),('Documented Quantity Should be greater than 0.'))
						if batch_line.short or batch_line.reject:
								if batch_line.product_qty < batch_line.short or batch_line.product_qty < batch_line.reject or batch_line.product_qty < batch_line.reject + batch_line.short:
									raise osv.except_osv(('Alert!'),('Quantity Cannot be greater than the Documented Qty'))	

						srch = self.pool.get('res.batchnumber').search(cr,uid,[('id','=',batch),('branch_name','=',godown)])
						for batch_brw in self.pool.get('res.batchnumber').browse(cr,uid,srch):
							if product_name != batch_brw.name.id:
								raise osv.except_osv(('Alert!'),('Please select proper Product Name to assign the batch.'))
				for var in self.browse(cr,uid,ids):
					godown=var.branch_name.id
					cc_date = datetime.now()
					c_date=datetime.strftime(cc_date,"%Y-%m-%d %H:%M:%S")
					current_date = datetime.now().date()
					monthee = current_date.month
					current_year = current_date.year
					day = current_date.day
					#partner_seq=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
					current_date=cc_date.today()
					year1=current_date.strftime('%y')
					today_date = datetime.now().date()
					year=today_date.strftime('%y')
					month =today_date.strftime('%m')
					if int(month) > 3:
						 year = int(year)+1
					else:
						 year=year
					year=str(year)
					branch_code=grn_id = ''
					search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','res.warehouse2')])
					for i in self.pool.get('ir.sequence').browse(cr,uid,search):
						if i.year != year or i.year==False:
							self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year,'implementation':'no_gap','number_next':1})
					sequence_no=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
					company_id=self._get_company(cr,uid,context=None)
					for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
						if comp_id.internal_branch_no:
							branch_code=comp_id.internal_branch_no
						if comp_id.indent_req_id:
							grn_id=comp_id.grn_id
					partner_seq = branch_code + grn_id + str(year) + sequence_no

					#check for track equipment type product:
					check='False'
					tag_check= serial_id_check=False
					for lines in var.receive_indent_line:
						if lines.product_name.type_product=='track_equipment':
							check='True'
						if lines.product_name.product_tag_id:
							tag_check=True
						if lines.product_name.stationary_track_no:
							serial_id_check=True
					grn_date= time.strftime("%Y-%m-%d %H:%M:%S")
					self.pool.get('receive.indent').write(cr,uid,var.id,{
											'grn_no':partner_seq,
											'state':'done',
											'grn_date':grn_date,
											'check_product_serial':check,
											'tag_check':tag_check,
											'serial_id_check':serial_id_check,
											'branch_name':godown,})
					#self.pool.get('product.tag.main').write(cr,uid,var.id,{'serial_check':serial_id_check})
					grn_no = var.grn_no
					if var.delivery_type_others not in ('banned_st','excess_st','inter_branch_st'):
						for files in var.receive_indent_line:
							manufacturing_date = files.manufacturing_date
							product_code = files.product_code
							qty_received = files.qty_received
							product_name = files.product_name.id
							if not files.batch:
								raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(files.product_name.name_template))
							if files.product_name.batch_type=='applicable' and not files.manufacturing_date:
								raise osv.except_osv(('Alert!'),('Please Enter Manufacturing Date of the Product.'))
							elif files.product_name.batch_type=='applicable' and files.manufacturing_date:
								n_product_srch = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
								for n_brw_product in self.pool.get('product.product').browse(cr,uid,n_product_srch):
									qqqty = n_brw_product.quantity_available
									shelf_life = n_brw_product.shelf_life
									exp_date = self.add_months(manufacturing_date,shelf_life)
									prod_qty=n_brw_product.quantity_available+files.qty_received
									if files.product_name.type_product != 'track_equipment':
										self.pool.get('product.product').write(cr,uid,n_brw_product.id,{'check_batch':True,'quantity_available':prod_qty,})
										self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{
													'manufacturing_date':manufacturing_date,
													'exp_date':exp_date,
													'qty':files.batch.qty+files.qty_received,
													'st':files.price_unit,})

										n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',godown)])
										godown_stock=0.0
										if n_brw_product.uom_id.id != n_brw_product.local_uom_id.id:
											for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
												godown_stock+=n_batch_ids.local_qty
											godown_stock=(godown_stock-(files.qty_received*files.product_name.local_uom_relation)) if godown_stock else 0
											local_qty=files.qty_received*n_brw_product.local_uom_relation
											# prod_qty_local = files.product_name.quantity_available * files.product_name.local_uom_relation
										elif n_brw_product.uom_id.id == n_brw_product.local_uom_id.id:
											for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
												godown_stock+=n_batch_ids.qty
											godown_stock=(godown_stock-files.qty_received) if godown_stock else 0 
											local_qty=files.qty_received
											# prod_qty_local = files.product_name.quantity_available

										ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{
												'ids':files.batch.id,
												'product_id':product_name,
												'date':current_date,
												'day':day,
												'datetime':c_date,
												'received':True,
												'qty':local_qty,
												'year':current_year,
												'month':monthee,
												'product_qty':godown_stock ,
												'branch_name':godown})#HHH

							elif (files.product_name.batch_type=='non_applicable' or not files.product_name.batch_type):
								if files.product_name.type_product != 'track_equipment':
									self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+qty_received,'st':files.price_unit,})
									n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',godown)])
									godown_stock=0.0

									if files.product_name.uom_id.id != files.product_name.local_uom_id.id:
		####################### MAHESH 17 JUL 15 SEPERATE STOCK FOR GODOWN ###############################
										for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
											godown_stock+=n_batch_ids.local_qty
										godown_stock=(godown_stock-(files.qty_received*files.product_name.local_uom_relation)) if godown_stock else 0
										local_qty=files.qty_received*files.product_name.local_uom_relation
										# prod_qty_local = files.product_name.quantity_available * files.product_name.local_uom_relation	
									elif files.product_name.uom_id.id == files.product_name.local_uom_id.id:
		####################### MAHESH 17 JUL 15 SEPERATE STOCK FOR GODOWN ###############################
										for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):
											godown_stock+=n_batch_ids.qty
										godown_stock=(godown_stock-files.qty_received) if godown_stock else 0
										local_qty=files.qty_received
										# prod_qty_local = files.product_name.quantity_available

									ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{
													'ids':files.batch.id,
													'product_id':product_name,
													'date':current_date,
													'day':day,
													'datetime':c_date,
													'received':True,
													'qty':local_qty,
													'year':current_year,
													'month':monthee,
													'product_qty':godown_stock ,
													 'branch_name':godown}) #HHH
								self.pool.get('product.product')._update_product_quantity(cr,uid,[files.batch.name.id])
						indent_id=0

						po_no = ''
						if var.delivery_type_others=='local_purchase':
							po_no = var.po_no
							grn_no = var.grn_no
							grn_date = var.grn_date
							document_value = var.document_value
							# self.pool.get('purchase.indent').write(cr,uid,[var.po_no.id],{'state':'received','grn_no':grn_no,'grn_date':grn_date,'document_value':document_value})
							if var.comment_line:
								for kk in var.comment_line:
									search_notes = self.pool.get('purchase.indent.remarks').search(cr,uid,[('name','=',kk.comment),('date','=',kk.comment_date),('user_name','=',kk.user_id),('source','=',kk.source.id)])
									if not search_notes == []:
										for test in search_notes:
											self.pool.get('purchase.indent.remarks').write(cr,uid,test,{
														'name':kk.comment,
														'date':kk.comment_date,
														'user_name':kk.user_id,
														'source':kk.source.id})
									else:
										aa = self.pool.get('purchase.indent.remarks').create(cr,uid,{
														'name':kk.comment,
														'date':kk.comment_date,
														'user_name':kk.user_id,
														'source':kk.source.id,
														'purchase_indent_id':po_no})

		# for branch stock transfer 
					if var.delivery_type_others in ('banned_st','excess_st','inter_branch_st'):
							for rec in self.browse(cr,uid,ids):
								for ln in rec.receive_indent_line:
									form_material_id = ln.id
									product_id = ln.product_name
									reject = ln.reject
									short=ln.short
									excess=ln.excess
									type_product = product_id.type_product
									if ln.short or ln.reject:
										if ln.product_qty < ln.short or ln.product_qty < ln.reject or ln.product_qty < ln.reject + ln.short:
											raise osv.except_osv(('Alert!'),('Short/Reject Quantity Cannot be greater than the Documented Qty'))	

									if type_product == 'track_equipment':

											cr.execute('select count(reject_serial_check) from transfer_series where series_line=%s and reject_serial_check = True  and product_name=%s',(form_material_id,ln.product_name.id))
											result=cr.fetchone()[0]
											cr.execute('select count(short) from transfer_series where series_line=%s and short = True  and product_name=%s',(form_material_id,ln.product_name.id))
											result1=cr.fetchone()[0]
											cr.execute('select count(excess) from transfer_series where series_line=%s and excess = True  and product_name=%s',(form_material_id,ln.product_name.id))
											result2=cr.fetchone()[0]
											if result != long(reject):
												raise osv.except_osv(('Alert!'),('You cannot reject more or less serial number. You gave reject value = %s for Product = %s .')%(reject,ln.product_name.name))		
											if result2 != long(excess):
												raise osv.except_osv(('Alert!'),('You cannot excess more or less serial number. You gave excess value = %s for Product = %s .')%(excess,ln.product_name.name))	
											if result1 != long(short):
												raise osv.except_osv(('Alert!'),('You cannot short more or less serial number. You gave short value = %s for Product = %s .')%(short,ln.product_name.name))	
							flag=False
							for files in var.receive_indent_line:
								manufacturing_date = files.manufacturing_date
								product_code = files.product_code
								qty_received = files.qty_received
								product_name = files.product_name.id
								reject_qty=files.reject
						
								reject_count=0
								if files.serial_line:
									for reject_serials in files.serial_line:
										if reject_serials.reject_serial_check:
											reject_count=reject_count+1
								if files.product_name.type_product == 'track_equipment' and flag == False:
									flag=True
									series_main=self.pool.get('product.series.main').create(cr,uid,{'test':var.id,'state':'end'})
								if not files.batch:
									raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(files.product_name.name_template))
								elif files.product_name.batch_type=='applicable' and files.manufacturing_date:
									n_product_srch = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
									for n_brw_product in self.pool.get('product.product').browse(cr,uid,n_product_srch):
										qqqty = n_brw_product.quantity_available
										shelf_life = n_brw_product.shelf_life
										exp_date = self.add_months(manufacturing_date,shelf_life)
										prod_qty=n_brw_product.quantity_available+files.qty_received
										if files.product_name.type_product != 'track_equipment':
											self.pool.get('product.product').write(cr,uid,n_brw_product.id,{'check_batch':True,
																							'quantity_available':prod_qty,
																							})
											self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})
											#ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':files.product_name.id,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':v.quantity_available,'serial_check':True})
										if files.product_name.type_product == 'track_equipment':
											self.pool.get('product.product').write(cr,uid,n_brw_product.id,{'check_batch':True,
																							'quantity_available':prod_qty,})
											self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,})
											#ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':files.product_name.id,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':files.qty_received,'year':year,'month':monthee,'product_qty':v.quantity_available,'serial_check':True})
										if files.serial_line:
									
											for serial in files.serial_line:
												count = count + 1               
												sr_no=count
												product_code=serial.product_code
												product_name=serial.product_name.id
												product_uom=serial.product_uom.id
												product_category = serial.product_category.id
												batch=serial.batch.id
												quantity=1
												serial_no=serial.serial_name
												reject_serial_check=serial.reject_serial_check
												short=serial.short
												excess=serial.excess
												if serial.short:
													quantity=0
									
												self.pool.get('product.series').create(cr,uid,{'sr_no':sr_no,'grn_no':grn_no,'line_id':series_main,'excess':excess,'short':short,'product_code':product_code,'product_category':product_category,'product_name':product_name,'product_uom':product_uom,
		'batch':batch,'quantity':quantity,'serial_no':serial_no,'serial_check':True,'reject':reject_serial_check})

										n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',godown)])  ###########
										godown_stock=0.0

										if n_brw_product.uom_id.id != n_brw_product.local_uom_id.id:
											for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):#########
												godown_stock+=n_batch_ids.local_qty ######
											godown_stock=(godown_stock-(files.qty_received*files.product_name.local_uom_relation)) if godown_stock else 0
											local_qty=files.qty_received*n_brw_product.local_uom_relation
											# prod_qty_local = files.product_name.quantity_available * files.product_name.local_uom_relation
										elif n_brw_product.uom_id.id == n_brw_product.local_uom_id.id:
											for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch): ###############
												godown_stock+=n_batch_ids.qty   ############
											godown_stock=(godown_stock-files.qty_received) if godown_stock else 0
											local_qty=files.qty_received
											# prod_qty_local = files.product_name.quantity_available
										ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':product_name,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':local_qty,'year':current_year,'month':monthee,'product_qty':godown_stock,'serial_check':True , 'branch_name':godown})#HHH

								elif (files.product_name.batch_type=='non_applicable' or not files.product_name.batch_type):
									#if files.product_name.type_product != 'track_equipment':
									self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+qty_received,'st':files.price_unit,})
									n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',godown)])  ###########
									godown_stock=0.0

									if files.product_name.uom_id.id != files.product_name.local_uom_id.id:
										for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):#########
											godown_stock+=n_batch_ids.local_qty ######
										godown_stock=(godown_stock-(files.qty_received*files.product_name.local_uom_relation)) if godown_stock else 0
										local_qty=files.qty_received*files.product_name.local_uom_relation
										# prod_qty_local = files.product_name.quantity_available * files.product_name.local_uom_relation	
									elif files.product_name.uom_id.id == files.product_name.local_uom_id.id:
										for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch): ###############
											godown_stock+=n_batch_ids.qty   ############
										godown_stock=(godown_stock-files.qty_received) if godown_stock else 0
										local_qty=files.qty_received
										# prod_qty_local = files.product_name.quantity_available

									ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':product_name,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':local_qty,'year':current_year,'month':monthee,'product_qty':godown_stock , 'branch_name':godown}) #HHH
									self.pool.get('product.product')._update_product_quantity(cr,uid,[files.batch.name.id])
									if files.serial_line:
										for serial in files.serial_line:
											count = count + 1
											sr_no=count
											product_code=serial.product_code
											product_name=serial.product_name.id
											product_uom=serial.product_uom.id
											batch=serial.batch.id
											product_category = serial.product_category.id
											quantity=1
											serial_no=serial.serial_name
											reject_serial_check=serial.reject_serial_check
											short=serial.short
											excess=serial.excess
											if serial.short:
												quantity=0
											self.pool.get('product.series').create(cr,uid,{
															'sr_no':sr_no,
															'grn_no':grn_no,
															'line_id':series_main,
															'short':short,
															'excess':excess,
															'product_code':product_code,
															'product_category':product_category,
															'product_name':product_name,
															'product_uom':product_uom,
															'batch':batch,
															'quantity':quantity,
															'serial_no':serial_no,
															'serial_check':True,
															'reject':reject_serial_check})
								self.pool.get('receive.indent').write(cr,uid,var.id,{'grn_no':partner_seq,
														 'state':'done',
														 'check_product_serial':'False',
														 'check_attachment':flag,
														 })
							stock_transfer_no=var.stn_no.id
							stn_search=self.pool.get('branch.stock.transfer').search(cr,uid,[('id','=',stock_transfer_no)])
							stn_remark_search=self.pool.get('branch.stock.transfer.remarks').search(cr,uid,[('branch_stock_transfer_id','=',stock_transfer_no)])
							for remark_stn in self.pool.get('branch.stock.transfer.remarks').browse(cr,uid,stn_remark_search):
								remark=remark_stn.name
								user_name=remark_stn.user_name
								date=remark_stn.date
								source=remark_stn.source.id
						
								receive_remark=self.pool.get('receive.indent.comment.line').search(cr,uid,[('comment_date','=',date),('user_id','=',user_name),('comment','=',remark),('source','=',source)])
								if receive_remark:
									print 'kk'
								else:
									self.pool.get('receive.indent.comment.line').create(cr,uid,{'comment_date':date,'user_id':user_name,'comment':remark,'source':source,'receive_indent_id':var.id})
						
							for res in self.pool.get('branch.stock.transfer').browse(cr,uid,stn_search):
								self.pool.get('branch.stock.transfer').write(cr,uid,res.id,{'state':'done'})
							self.syn_generate_grn_stock_transfer(cr,uid,ids,context=context)

				for temp in self.browse(cr,uid,ids):
					form_id = temp.id
					po_no=temp.po_no
					grn_no=temp.grn_no
					grn_date=temp.grn_date
					purchase_indent=self.pool.get('purchase.indent').search(cr,uid,[('purchase_no','=',po_no)])
					for res in self.pool.get('purchase.indent').browse(cr,uid,purchase_indent):
						purchase_request_no=res.purchase_order_no
						self.pool.get('purchase.indent').write(cr,uid,res.id,{'grn_no':grn_no,'grn_date':grn_date})
					for kk in temp.receive_indent_line:
						c = c + 1
						product_name = kk.product_name.id
						qty_received = kk.qty_received
						product = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
						for u in self.pool.get('product.product').browse(cr,uid,product):
							if not u.type_product == 'track_equipment': 
								account = 1
							else:
								if qty_received == 0.00:
									bcount = 2
								else:
									ccount = 3
					if account == 1 and not bcount == 2 and not ccount == 3:
						self.pool.get('receive.indent').write(cr,uid,[temp.id],{'test_state':'end'})
					if bcount == 2 and not account == 1 and not ccount == 3:
			
						self.pool.get('receive.indent').write(cr,uid,[temp.id],{'test_state':'end'})
					if account == 1 and bcount == 2 and not ccount == 3:
						self.pool.get('receive.indent').write(cr,uid,[temp.id],{'test_state':'end'})

				for rec in self.browse(cr,uid,ids):
					indent_id=rec.indent_id.id
					if rec.delivery_type_others=='direct_delivery':
						dict1={}
						for line in rec.receive_indent_line:
							dict1[str(line.product_name.id)]=0
						for vals in dict1:
							add=[x.product_qty for x in rec.receive_indent_line if x.product_name.id==int(vals)]
							dict1[vals]=sum(add)
						for res in dict1.keys():
							dest=int(res)
							Value = dict1[res]
							indent_search=self.pool.get('res.indent').search(cr,uid,[('id','=',rec.indent_id.id)])
							for temp in self.pool.get('res.indent').browse(cr,uid,indent_search):
								for var in temp.order_line:	
									if var.product_id.id in [dest]:
										product_qty=var.product_uom_qty
										if (var.received_quantity+Value) >= product_qty:
											self.pool.get('indent.order.line').write(cr,uid,var.id,{'state':'received','received_quantity':var.received_quantity+Value})
										else:
											self.pool.get('indent.order.line').write(cr,uid,var.id,{'state':'partial_received','received_quantity':var.received_quantity+Value})
						flag=True
						for indent_rec in self.pool.get('res.indent').browse(cr,uid,[rec.indent_id.id]):
							for indent_lines in indent_rec.order_line:
								if indent_lines.state not in ('received','cancel'):
									flag=False
						if flag==True:
								self.pool.get('res.indent').write(cr,uid,[indent_id],{'state':'done'})

						indent_no=rec.indent_id.id
						indent_search=self.pool.get('res.indent').search(cr,uid,[('id','=',indent_no)])
						stn_remark_search=self.pool.get('indent.comment.line').search(cr,uid,[('indent_id','=',indent_no)])
						for remark_stn in self.pool.get('indent.comment.line').browse(cr,uid,stn_remark_search):
								remark=remark_stn.comment
								user_name=remark_stn.user_id
								date=remark_stn.comment_date
								source=remark_stn.source.id
						
								receive_remark=self.pool.get('receive.indent.comment.line').search(cr,uid,[('comment_date','=',date),('user_id','=',user_name),('comment','=',remark),('source','=',source)])
								if receive_remark:
									print 'kk'
								else:
									self.pool.get('receive.indent.comment.line').create(cr,uid,{'comment_date':date,'user_id':user_name,'comment':remark,'source':source,'receive_indent_id':rec.id})
						self.sync_indent_notes_update(cr,uid,ids,context=context)

					for test in self.browse(cr,uid,ids):
						msg_flag=False
						if test.delivery_type_others=='local_purchase':
							comment = ''
							generic_id = 0
							con_flag=False
							document_value = test.document_value
							#po_num = test.po_no.purchase_no
							po_num = test.po_no
							branch_type = self.pool.get('res.company').search(cr,uid,[('branch_type','=','central_indents_type')])
							res = ''
							k=[]
							if test.comment_line:
								for tt in test.comment_line:
									comment_line = [ tt.comment]
									res=' , '.join(comment_line)
									k.append(res)
								comment =  ", ".join(["%s" % s for s in k])
							for branch_id in self.pool.get('res.company').browse(cr,uid,branch_type):
										transporter_create_new = []
										vpn_ip_addr = branch_id.vpn_ip_address
										port = branch_id.port
										dbname = branch_id.dbname
										pwd = branch_id.pwd
										time_cur = time.strftime("%H%M%S")
										date = time.strftime('%Y-%m-%d%H%M%S')
										user_name = str(branch_id.user_name.login)
										userid = ''
										username = user_name #the user
										pwd = pwd    #the password of the user
										dbname = dbname
										log = ('http://%s:%s/xmlrpc/common')%(vpn_ip_addr,port)
										obj = ('http://%s:%s/xmlrpc/object')%(vpn_ip_addr,port)
										sock_common = xmlrpclib.ServerProxy (log)
										try:
											raise
											userid = sock_common.login(dbname, username, pwd)
										except Exception as Err:
											offline_obj=self.pool.get('offline.sync')
											offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
											con_flag = True
											if not offline_sync_sequence:
												offline_obj.create(cr,uid,{
													'src_model':self._name,
													'dest_model':False,
													'sync_company_id':branch_id.id,
													'srch_condn':False,
													'form_id':ids[0],
													'func_model':'sync_local_purchase',
													'error_log':Err,})
											else:
												offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
												offline_obj.write(cr, uid, offline_sync_id, {'res_active':con_flag})
			#####################SQL#########OFFLINE##############SYNC################################################################################
											current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key #changes 22jul16
											con_cat = dbname+"-"+branch_id.vpn_ip_address+"-"+str(current_company)+'-Recieve_Indent_local_purchase-'+str(date)+'_'+str(time_cur)+'.sql'
											filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
											directory_name = str(os.path.expanduser('~')+'/indent_sync/')
					
											if not os.path.exists(directory_name):
												os.makedirs(directory_name)
											d = os.path.dirname(directory_name)
											concern_branch_ids=0
											if test.company_id :
												po_date="'" + str(test.po_date) + "'" if test.po_date else 'NULL'
												transporter= str(test.transporter_name.transporter_name) if test.transporter_name else ''
												source = str(test.supplier_name.name) if test.supplier_name else ''
												concern_branch_ids="(SELECT id FROM res_company WHERE name = '"+str(test.company_id.name) + "')"
											final_create="\nINSERT INTO local_central_indent (create_uid,create_date,po_no, po_date, grn_no, grn_date, total_amount, transporter, comment_remark, document_value, source, delivery_type, company_id ) VALUES (1,(now() at time zone 'UTC'),'" + str(test.po_no) + "'," + po_date + ",'" + str(test.grn_no) + "','" + str(test.grn_date) + "'," + str(document_value) + ",'" + transporter + "','" + comment + "'," + str(test.document_value) + ",'" + source + "','" + str(test.delivery_type_others) + "'," + concern_branch_ids + ");"
											with open(filename,'a') as f :
												f.write(final_create)
												f.close()
											if test.receive_indent_line:
												for var1 in test.receive_indent_line:
													if var1.product_name:
														product_name_id= "(SELECT id FROM product_product WHERE name_template = '" + str(var1.product_name.name.replace("'","''")) + "')"
													if var1.generic_id:
														generic_id ="(SELECT id FROM product_generic_name WHERE name = '"+str(var1.generic_id.name) + "')"
													if var1.product_uom:
														uom_id = "(SELECT id FROM product_uom WHERE name = '" + str(var1.product_uom.name) + "')"
													final_srch="(SELECT id FROM local_central_indent WHERE po_no ='"+ str(test.po_no) + "' AND grn_no = '" + str(test.grn_no) +"')"
													manufacturing_date = "'" + str(var1.batch.manufacturing_date) +"'" if var1.batch.manufacturing_date else 'NULL'
													create_purchase1 = "\n INSERT INTO purchase_central_indent (create_uid,create_date,product_code, product_name, generic_id, batch, product_qty, manufacturing_date, short, excess, reject, product_uom, qty_received, price_unit, subtotal, purchase_id ) VALUES (1,(now() at time zone 'UTC'),'" + str(var1.product_code) + "'," + product_name_id + "," + generic_id + ",'" + str(var1.batch.batch_no) + "'," + str(var1.product_qty) + "," + manufacturing_date + "," + str(var1.short) + "," + str(var1.excess) + "," +str(var1.reject) + "," + uom_id + "," +str(var1.qty_received) + "," + str(var1.price_unit) + "," + str(var1.subtotal) + "," + final_srch + ");"
													with open(filename,'a') as f :
														f.write(create_purchase1)
														f.close()
													create_purchase11=" (SELECT id FROM purchase_central_indent WHERE purchase_id="+ final_srch + ")"
													if var1.notes_one2many:
														for line_id in var1.notes_one2many:
															source_ids=''
															if line_id.source:
																source_ids ="(SELECT id FROM res_company where name='"+str(line_id.source.name)+"')"
															msg_flag=True
															msg_unread_ids ="\n UPDATE purchase_central_indent SET write_date=(now() at time zone \'UTC\'),write_uid=1, msg_check_unread=True,msg_check_read=False WHERE id= "+create_purchase11+";"
															create_material_notes = "\n INSERT INTO purchase_central_indent_comment_line( create_uid,create_date,indent_id, user_id,comment,comment_date,source) VALUES(1,(now() at time zone 'UTC'),"+ create_purchase11+",'"+str(line_id.user_id)+"','"+ str(line_id.comment)+ "','" +str(line_id.comment_date)+"',"+ source_ids+");"
															with open(filename,'a') as f:
																f.write(msg_unread_ids)
																f.write(create_material_notes)
																f.close() 
											if test.comment_line:
												for notes_line in test.comment_line:
													user_ids = "(SELECT id FROM res_users WHERE name = '" + str(notes_line.user_id) + "')"
													source_ids ="(SELECT id FROM res_company where name='"+str(notes_line.source.name)+"')"
													msg_flag=True
													user_id=str(notes_line.user_id) if notes_line.user_id else ''
													notes_line_ids = "\n INSERT INTO purchase_local_comment_line (create_uid,create_date,purchase_indent_id, user_id, source, comment_date, comment ) VALUES (1,(now() at time zone 'UTC')," + final_srch + ",'"+user_id +"',"+ source_ids + ",'" + str(notes_line.comment_date) + "','" + str(notes_line.comment) +"');"
													with open(filename,'a') as f :
														f.write(notes_line_ids)
														f.close()
											if msg_flag:			
												msg_ids="\n UPDATE local_central_indent SET write_date=(now() at time zone \'UTC\'),write_uid=1,msg_check=True WHERE id =" + create_purchase11+ ";"
												with open(filename,'a') as f:
													f.write(msg_ids)
													f.close()
											#print Mahesh
			##########################################################################################################################################
										sock = xmlrpclib.ServerProxy(obj)
								
										if con_flag==False:
											concern_branch_ids=0
											if test.company_id :
												concern_branch = [('name','=',test.company_id.name)]
												concern_branch_ids = sock.execute(dbname, userid, pwd,'res.company','search',concern_branch)
	
											final_result = {
												'po_no':test.po_no,
												'po_date':test.po_date if test.po_date else False,
												'grn_no':test.grn_no,
												'grn_date':test.grn_date,
												'total_amount':str(document_value),
												'transporter':test.transporter_name.transporter_name if test.transporter_name else '',
												'comment_remark':comment,
												'document_value':test.document_value,
												'source':test.supplier_name.name if test.supplier_name else '',
												'delivery_type':test.delivery_type_others,
												'company_id':concern_branch_ids[0] if test.company_id else ''
														}
											final_create = sock.execute(dbname, userid, pwd, 'local.central.indent', 'create',final_result )
	
											if test.receive_indent_line:
												for var1 in test.receive_indent_line:
													if var1.product_name:
														 product_name_srch = [('name','=',var1.product_name.name)]
														 product_name_id = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_name_srch)
	
													if var1.generic_id:
														 generic_id_srch = [('name','=',var1.generic_id.name)]
														 generic_id = sock.execute(dbname, userid, pwd, 'product.generic.name', 'search',generic_id_srch)
	
													if var1.product_uom:
														prod_uom_id = [('name', '=', var1.product_uom.name)]
														uom_id = sock.execute(dbname, userid, pwd, 'product.uom', 'search', prod_uom_id)
	
													create_purchase_90 = {'product_code':var1.product_code,
															'product_name':product_name_id[0], 
															'generic_id':generic_id[0] if generic_id else False,
															'batch':var1.batch.batch_no ,
															'product_qty':var1.product_qty,
															'manufacturing_date':var1.batch.manufacturing_date, 
															'short':var1.short, 
															'excess':var1.excess,
															'reject':var1.reject,
															'product_uom':uom_id[0], 
															'qty_received':var1.qty_received, 
															'price_unit':var1.price_unit, 
															'subtotal':var1.subtotal, 
															'purchase_id':final_create,}
	
													create_purchase1 = sock.execute(dbname, userid, pwd, 'purchase.central.indent', 'create', create_purchase_90)
													if var1.notes_one2many:
														for line_id in var1.notes_one2many:
															source_ids=''
															if line_id.source: #Source
																source_srch = [('name', '=',line_id.source.name)]
																source_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
	
															msg_flag=True
															msg_unread = { 'msg_check_unread':True,'msg_check_read':False,
																					}
															msg_unread_ids= sock.execute(dbname, userid, pwd, 'purchase.central.indent', 'write',create_purchase1, msg_unread)
															material_notes = {
																	'indent_id':create_purchase1,
																	'user_id':line_id.user_id,
																	'comment':line_id.comment,
																	'comment_date':line_id.comment_date,
																	'source':source_ids[0] if line_id.source else False,
																	}
															create_material_notes = sock.execute(dbname, userid, pwd, 'purchase.central.indent.comment.line', 'create', material_notes)
											if test.comment_line:
												for notes_line in test.comment_line:
													user_srch = [('name', '=',notes_line.user_id)]
													user_ids = sock.execute(dbname, userid, pwd, 'res.users', 'search', user_srch)
													source_srch = [('name', '=',notes_line.source.name)]
													source_ids = sock.execute(dbname, userid, pwd, 'res.company', 'search', source_srch)
													msg_flag=True
													create_notes_line = {
														'purchase_indent_id':final_create,
														'user_id':notes_line.user_id if notes_line.user_id else '',
														'source':source_ids[0] if notes_line.source else '',
														'comment_date':notes_line.comment_date,
														'comment':notes_line.comment,
														}
													notes_line_ids = sock.execute(dbname, userid, pwd, 'purchase.local.comment.line', 'create', create_notes_line)
	
											if msg_flag:
												msg_line = {'msg_check':True}
												msg_ids= sock.execute(dbname, userid, pwd, 'local.central.indent', 'write', final_create, msg_line)

				for delivery_check in self.browse(cr,uid,ids):
					if delivery_check.delivery_type_others=='direct_delivery':
						self.sync_generate_grn_others_1(cr,uid,ids,context=context)
				self.sync_generate_grn_others(cr,uid,ids,context=context)

		return True

	#Conversion Original Method with Birdpro method.
	def nsd_generate_indent_grn(self, cr, uid,ids,vals, context=None): 
		if context is None: context = {}
		exp_date = account = ccount = bcount = godown = '' #HHH
		qqqty = scount= c = form_material_id = godown_stock=local_qty=0
		qty_received = 0.0
		prod_qty = prod_qty_local = series_main=''
		flag=False
		search_indent= serial_id_check= tag_check=''
		
		self.material_notes_update(cr,uid,ids,context=context)	
		for res in self.browse(cr,uid,ids):
			test_id = res.id
			srch = self.pool.get('receive.indent').search(cr,uid,[('id','=',test_id)])
			for rec in self.pool.get('receive.indent').browse(cr,uid,srch):
				godown=rec.branch_name.id
				#if not godown :
					#raise osv.except_osv(('Alert!'),('Please Select The Godown !'))
				order_id = rec.indent_id.order_id
				for ln in rec.receive_indent_line:
					form_material_id = ln.id
					product_id = ln.product_name
					reject = ln.reject
					short=ln.short
					excess=ln.excess
					type_product = product_id.type_product
					if ln.short or ln.reject:
						if ln.product_qty < ln.short or ln.product_qty < ln.reject or ln.product_qty < ln.reject + ln.short:
							raise osv.except_osv(('Alert!'),('Short/Reject Quantity Cannot be greater than the Documented Qty'))

					if type_product == 'track_equipment':

							cr.execute('select count(reject_serial_check) from transfer_series where series_line=%s and reject_serial_check = True  and product_name=%s',(form_material_id,ln.product_name.id))
							result=cr.fetchone()[0]
							cr.execute('select count(short) from transfer_series where series_line=%s and short = True  and product_name=%s',(form_material_id,ln.product_name.id))
							result1=cr.fetchone()[0]
							cr.execute('select count(excess) from transfer_series where series_line=%s and excess = True  and product_name=%s',(form_material_id,ln.product_name.id))
							result2=cr.fetchone()[0]
							if result != long(reject):
								raise osv.except_osv(('Alert!'),('You cannot reject more or less serial number. You gave reject value = %s for Product = %s .')%(reject,ln.product_name.name))		
							if result2 != long(excess):
								raise osv.except_osv(('Alert!'),('You cannot excess more or less serial number. You gave excess value = %s for Product = %s .')%(excess,ln.product_name.name))	
							if result1 != long(short):
								raise osv.except_osv(('Alert!'),('You cannot short more or less serial number. You gave short value = %s for Product = %s .')%(short,ln.product_name.name))

		form_branch_id = ''
		for var in self.browse(cr,uid,ids):
				form_branch_id = var.form_branch_id
				indent_no=var.indent_no
				cc_date = datetime.now()
				c_date=datetime.strftime(cc_date,"%Y-%m-%d %H:%M:%S")
				current_date = datetime.now().date()
				monthee = current_date.month
				current_year = current_date.year
				day = current_date.day
				#partner_seq=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
				year1=current_date.strftime('%y')
				today_date = datetime.now().date()
				year=today_date.strftime('%y')
				month =today_date.strftime('%m')
				if int(month) > 3:
					 year = int(year)+1
				else:
					 year=year
				year=str(year)	 
				branch_code=''
				grn_id = ''
				search=self.pool.get('ir.sequence').search(cr,uid,[('code','=','res.warehouse2')])
				for i in self.pool.get('ir.sequence').browse(cr,uid,search):
					if i.year != year or i.year==False:
						self.pool.get('ir.sequence').write(cr,uid,i.id,{'year':year,'implementation':'no_gap','number_next':1})
				sequence_no=self.pool.get('ir.sequence').get(cr, uid, 'res.warehouse2')
				company_id=self._get_company(cr,uid,context=None)
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					if comp_id.internal_branch_no:
						branch_code=comp_id.internal_branch_no
					if comp_id.indent_req_id:
						grn_id=comp_id.grn_id
				partner_seq = branch_code + grn_id + str(year) + sequence_no
				#check for track equipment type product:
				check='False'
				for lines in var.receive_indent_line:
					if lines.product_name.type_product=='track_equipment':
						check='True'

					if lines.product_name.product_tag_id:
						tag_check=True

					if lines.product_name.stationary_track_no:
						serial_id_check=True

				grn_date=time.strftime("%Y-%m-%d %H:%M:%S")
				self.pool.get('receive.indent').write(cr,uid,var.id,{'grn_no':partner_seq,
										 'grn_date':grn_date,
										 'state':'done',
										 'check_product_serial':check,
										 'tag_check':tag_check,
										 'serial_id_check':serial_id_check,
										 'branch_name':var.branch_name.id})

				if indent_no:
					search_indent=self.pool.get('res.indent').search(cr,uid,[('form_branch_id_seq','=',form_branch_id),('order_id','=',indent_no)]) ###15 july assign job
				grn_no = var.grn_no
				p_qty = 0   
				#if var.delivery_type in ('internal_delivery','external_delivery'):
				for files in var.receive_indent_line:
					p_qty = files.product_qty 
					count_qty = 0
					srh = self.pool.get('receive.indent').search(cr,uid,[('indent_no','=',var.indent_no)])
					for srh_var in self.pool.get('receive.indent').browse(cr,uid,srh):
						for p in srh_var.receive_indent_line:
							count_qty = count_qty + p.product_qty
					manufacturing_date = files.manufacturing_date
					product_code_new = files.product_name.default_code
					generic_id = files.generic_id.id
					qty_received = files.qty_received
					product_name = files.product_name.id
					product_category = files.product_name.categ_id.id
					
					if indent_no:
						for indent_rec in self.pool.get('res.indent').browse(cr,uid,search_indent):
							for prod_line in indent_rec.order_line:
								prod_id=prod_line.product_id.id
								if prod_id==product_name:
									received_quantity = prod_line.received_quantity + p_qty
									self.pool.get('indent.order.line').write(cr,uid,prod_line.id,{'received_quantity':received_quantity})
									if received_quantity >= prod_line.product_uom_qty:
									   self.pool.get('indent.order.line').write(cr,uid,prod_line.id,{'state':'received'})
							
					if files.product_name.type_product == 'track_equipment' and flag == False:
						flag=True
						series_main=self.pool.get('product.series.main').create(cr,uid,{'test':var.id,'state':'end'})
					if not files.batch:
						raise osv.except_osv(('Alert!'),('Please Assign Batch to Product.\n\n%s.')%(files.product_name.name_template))	
					
					elif files.product_name.batch_type=='applicable' and files.manufacturing_date:
						aaa = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
						for v in self.pool.get('product.product').browse(cr,uid,aaa):
							qqqty = v.quantity_available
							shelf_life = v.shelf_life
							exp_date = self.add_months(manufacturing_date,shelf_life)
							prod_qty=v.quantity_available+files.qty_received
							n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',godown)])  ###########
							godown_stock=0.0
							if v.uom_id.id != v.local_uom_id.id:
								for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):#########
									godown_stock+=n_batch_ids.local_qty ######
								godown_stock=(godown_stock-(files.qty_received*files.product_name.local_uom_relation)) if godown_stock else 0
								local_qty=files.qty_received*v.local_uom_relation
								# prod_qty_local = files.product_name.quantity_available * files.product_name.local_uom_relation
							elif v.uom_id.id == v.local_uom_id.id:
								for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch): ###############
									godown_stock+=n_batch_ids.qty   ############
								godown_stock=(godown_stock-files.qty_received) if godown_stock else 0
								local_qty=files.qty_received
								# prod_qty_local = files.product_name.quantity_available
							ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':product_name,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':local_qty,'year':current_year,'month':monthee,'product_qty':godown_stock,'serial_check':True,'branch_name':godown}) # HHH
							if files.product_name.type_product != 'track_equipment':
								self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,'quantity_available':prod_qty,})
								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,'branch_name':godown,})

							if files.product_name.type_product == 'track_equipment':
								self.pool.get('product.product').write(cr,uid,v.id,{'check_batch':True,'quantity_available':prod_qty,})
								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'manufacturing_date':manufacturing_date,'exp_date':exp_date,'qty':files.batch.qty+files.qty_received,'st':files.price_unit,'branch_name':godown,})
							if files.serial_line:
								for serial in files.serial_line:
									scount=scount+1
									sr_no=scount
									product_code=serial.product_name.default_code
									product_name=serial.product_name.id
									product_uom=serial.product_uom.id
									batch=serial.batch.id
									quantity=1
									serial_no=serial.serial_name
									reject=serial.reject_serial_check
									short=serial.short
									excess=serial.excess
									if serial.short:
										quantity=0	
									self.pool.get('product.series').create(cr,uid,{'sr_no':sr_no,'grn_no':grn_no,'product_category':product_category,'generic_id':generic_id,'product_code':product_code,'line_id':series_main,'short':short,'excess':excess,'product_code':product_code,'product_name':product_name,'product_uom':product_uom,'batch':batch,'quantity':quantity,'serial_no':serial_no,'serial_check':True,'reject':reject})
	
					elif (files.product_name.batch_type=='non_applicable' or not files.product_name.batch_type):

						n_product_srch = self.pool.get('product.product').search(cr,uid,[('id','=',product_name)])
						for n_brw_product in self.pool.get('product.product').browse(cr,uid,n_product_srch):
							qqqty = n_brw_product.quantity_available
							shelf_life = n_brw_product.shelf_life
							#exp_date = self.add_months(manufacturing_date,shelf_life)
							prod_qty=n_brw_product.quantity_available+files.qty_received

							n_batch_srch=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',files.product_name.id),('branch_name','=',godown)])  ###########
							godown_stock=0.0
							if n_brw_product.uom_id.id != n_brw_product.local_uom_id.id:
								for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch):#########
									godown_stock+=n_batch_ids.local_qty ######
								godown_stock=(godown_stock-(files.qty_received*files.product_name.local_uom_relation)) if godown_stock else 0
								local_qty=files.qty_received*n_brw_product.local_uom_relation
								# prod_qty_local = files.product_name.quantity_available * files.product_name.local_uom_relation
							elif n_brw_product.uom_id.id == n_brw_product.local_uom_id.id:
								for n_batch_ids in self.pool.get('res.batchnumber').browse(cr,uid,n_batch_srch): ###############
									godown_stock+=n_batch_ids.qty   ############
								godown_stock=(godown_stock-files.qty_received) if godown_stock else 0
								local_qty=files.qty_received
								# prod_qty_local = files.product_name.quantity_available

							ids_new =  self.pool.get('batchproduct.info').create(cr,uid,{'ids':files.batch.id,'product_id':product_name,'date':current_date,'day':day,'datetime':c_date,'received':True,'qty':local_qty,'year':current_year,'month':monthee,'product_qty':godown_stock ,'branch_name':godown}) #HHH
						if files.product_name.type_product != 'track_equipment':
								self.pool.get('product.product').write(cr,uid,n_brw_product.id,{'check_batch':True,'quantity_available':prod_qty,})
								#if n_batch_srch :
								#	self.pool.get('res.batchnumber').write(cr,uid,[n_batch_srch[0]],{'qty':files.batch.qty+files.qty_received,'st':files.price_unit,'branch_name':godown})
								#else :
								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+files.qty_received,'st':files.price_unit,'branch_name':godown})

						if files.product_name.type_product == 'track_equipment':
								self.pool.get('product.product').write(cr,uid,n_brw_product.id,{'check_batch':True,'quantity_available':prod_qty,})
								#if n_batch_srch :
								#	self.pool.get('res.batchnumber').write(cr,uid,[n_batch_srch[0]],{'qty':files.batch.qty+files.qty_received,'st':files.price_unit,'branch_name':godown})
								#else :
								self.pool.get('res.batchnumber').write(cr,uid,[files.batch.id],{'qty':files.batch.qty+files.qty_received,'st':files.price_unit,'branch_name':godown})

						if files.serial_line:
							for serial in files.serial_line:
								#if serial.reject_serial_check == False:  ###babita23
								scount=scount+1
								sr_no=scount
								product_code=serial.product_name.default_code
								product_name=serial.product_name.id
								product_uom=serial.product_uom.id
								batch=serial.batch.id
								quantity=1
								serial_no=serial.serial_name
								reject=serial.reject_serial_check
								short=serial.short
								excess=serial.excess
								if serial.short:
									quantity=0	
								self.pool.get('product.series').create(cr,uid,{'sr_no':sr_no,'grn_no':grn_no,'product_code':product_code,'generic_id':generic_id,'product_category':product_category,'line_id':series_main,'excess':excess,'short':short,'product_code':product_code,'product_name':product_name,'product_uom':product_uom,'batch':batch,'quantity':quantity,'serial_no':serial_no,'serial_check':True,'reject':reject})
				indent_id=0
		if indent_no:
			for indent_rec in self.pool.get('res.indent').browse(cr,uid,search_indent):
				flag=False
				for prod_line in indent_rec.order_line: 
					if prod_line.state!='received':
						flag=True
				if not flag:
					self.pool.get('res.indent').write(cr,uid,indent_rec.id,{'state':'done'})
					###################################If Indent is done delivery order in ready to dispatch state
					indent_obj = self.pool.get('res.indent')
					stock_transfer_obj = self.pool.get('stock.transfer')
					product_transfer_obj = self.pool.get('product.transfer')
					material_details_obj =self.pool.get('material.details')
					transfer_series_obj =self.pool.get('transfer.series')
					res_indent_id = indent_rec.id
					o= self.browse(cr,uid,ids[0])
					delivery_challan_no = o.delivery_challan_no
					delivery_challan_date = o.delivery_challan_date
					main_grn_id = o.id
					new_delivery_type = o.new_delivery_type
					if new_delivery_type == 'External Delivery':
						delivery_id = indent_obj.browse(cr,uid,res_indent_id).delivery_id.id
						if delivery_id:
							material_detail_search = material_details_obj.search(cr,uid,[('indent_id','=',main_grn_id)])
							material_details_browse = material_details_obj.browse(cr,uid,material_detail_search)
							for material_details_id in material_details_browse:
								main_material_id = material_details_id.id
								transfer_series_search = transfer_series_obj.search(cr,uid,[('series_line','=',main_material_id)])
								transfer_series_browse = transfer_series_obj.browse(cr,uid,transfer_series_search)
								for transfer_series_id in transfer_series_browse:
									main_transfer_series_id = transfer_series_id.id
									transfer_series_obj.write(cr,uid,main_transfer_series_id,{'serial_line_id':delivery_id,'from_date':str(delivery_challan_date)})
							write_delivery_ref_id =stock_transfer_obj.write(cr,uid,delivery_id,{'delivered_ref_id':delivery_challan_no})
							material_search = material_details_obj.search(cr,uid,[('indent_id','=',main_grn_id)])
							material_browse = material_details_obj.browse(cr,uid,material_search)
							for material_id in material_browse:
								material_product_code = material_id.product_code
								material_generic_id = material_id.generic_id.id
								material_product_name = material_id.product_name.id
								batch = material_id.batch.id
								manufacturing_date = material_id.manufacturing_date
								search_product_transfer = product_transfer_obj.search(cr,uid,[('prod_id','=',delivery_id)])
								browse_product_transfer = product_transfer_obj.browse(cr,uid,search_product_transfer)
								for browse_id in browse_product_transfer:
									main_product_transfer_id = browse_id.id
									quantity = browse_id.quantity
									product_code = browse_id.product_code
									product_name = browse_id.product_name.id
									generic_id = browse_id.generic_id.id
									qty_indent = browse_id.qty_indent
									if product_code == material_product_code and product_name == material_product_name and generic_id == material_generic_id:
										product_transfer_obj.write(cr,uid,main_product_transfer_id,{'available_quantity':qty_indent,'batch':batch,'mfg_date':manufacturing_date,'quantity':qty_indent})
							stock_transfer_obj.nsd_ready_to_dispatch(cr,uid,[delivery_id],context=context)
					##########################################
		self.sync_indent_notes_update(cr,uid,ids,context=context)
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
				time_cur = time.strftime("%H%M%S")
				date = time.strftime('%Y-%m-%d%H%M%S')
				user_name = str(branch_id.user_name.login)
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
					offline_obj=self.pool.get('offline.sync')
					offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
					conn_central_flag = True
					if not offline_sync_sequence:
						offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':branch_type[0],'srch_condn':False,'form_id':i,'func_model':'generate_indent_grn_central','error_log':Err,})
					else:
						offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequenceom)])
						offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_central_flag})
############SQL##########OFFLINE#########SYNC##################################################################################
					current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key #changes 22jul16
					con_cat = dbname+"-"+branch_id.vpn_ip_address+"-"+str(current_company)+'-Recieve_Indent-'+str(date)+'_'+str(time_cur)+'.sql'
					filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
					directory_name = str(os.path.expanduser('~')+'/indent_sync/')
					sync_str=''
					if not os.path.exists(directory_name):
						os.makedirs(directory_name)
					d = os.path.dirname(directory_name)
					ln_ids = ''
					count = 0
					func_string ="\n\n CREATE OR REPLACE FUNCTION Recieve_Indent() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
					declare=" DECLARE \n \t"
					var1="""val_prod_series_srh INT;\n remark_srch_id INT; flag1 INT;
							state1 VARCHAR;
							flag2 INT;
							flag3 INT;
							counter INT;\n \n  BEGIN \n 
							flag1 =0;
							flag2 =0;
							flag3 =0;
							counter=0;"""
					endif="\n\n END IF; \n"
					ret="\n RETURN 1;\n"
					elsestr="\n ELSE \n"
					final="\nEND; \n $$;\n"
					fun_call="\n SELECT Recieve_Indent();\n"
					sync_str+= func_string + declare + var1

					origin_ids = "(SELECT id FROM stock_picking WHERE ci_sync_id_seq = '"+str(i.ci_sync_id) + "' AND origin = '" +str(i.indent_no) + "')" ## 15 july job assign
					
					for ln in i.receive_indent_line:
						create_series11 = 0
						if ln.product_name.type_product == 'track_equipment':
							final_val = "\n UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,test_state = TRUE WHERE id = " + origin_ids + ";"
							val_prod_series_srh= "\n val_prod_series_srh = ( SELECT id FROM product_series_main WHERE test= " + origin_ids + ");"
							ifstring="\n IF val_prod_series_srh IS NOT NULL THEN \n"
							create_series11="\n INSERT INTO product_series_main(create_uid,create_date,test) VALUES (1,(now() at time zone 'UTC'),"+origin_ids+");"
							val_prod_series_srh1 = "\n val_prod_series_srh = ( SELECT id FROM product_series_main WHERE test= " + origin_ids + ");"
							sync_str+= final_val + val_prod_series_srh + ifstring + elsestr + create_series11 + val_prod_series_srh1 + endif

							if ln.serial_line:
								product_ids = "(SELECT id FROM product_product WHERE name_template ='" + str(ln.generic_id.name.replace("'","''")) + "')"
							if ln.generic_id:
								generic_ids= "(SELECT id FROM product_generic_name WHERE name = '" +str(ln.generic_id.name) +"')"
								for serials in ln.serial_line:
									count = count + 1
									transporter_create_new=" \n INSERT INTO  product_series (create_uid,create_date, sr_no, product_code, product_name, generic_id, prod_uom, batch_val, quantity, serial_no, product_category, active_id, serial_check, series_line, reject, short, excess) VALUES (1,(now() at time zone 'UTC'),"+ str(count) +",'"+str(ln.product_code) + "'," +product_ids + "," + generic_ids + ",'" + str(ln.product_name.local_uom_id.name) +"','"+ str(ln.batch.batch_no) +"'," +str(serials.quantity) +",'"+ str(serials.serial_name) +"','" + str(serials.product_name.categ_id.name)+"','" + str(serials.active_id) + "','" + str(serials.serial_check) + "',val_prod_series_srh, '" + str(serials.reject_serial_check) + "','" + str(serials.short) + "' , '"+ str(serials.excess) +"');"
									sync_str+= transporter_create_new
					product_uom_qty = 0
					for p in i.receive_indent_line:		
						product_ids11="(SELECT id FROM product_product WHERE name_template = '"+ str(p.product_name.name.replace("'","''")) + "')"
						stock_val ="( SELECT id FROM stock_move WHERE product_id = " + product_ids11 + " AND picking_id = " + origin_ids +" ORDER BY id LIMIT 1)" 
						move_ids= "\n UPDATE stock_move SET write_date=(now() at time zone \'UTC\'),write_uid=1, state = 'done' WHERE id = "+stock_val+";"
						sync_str += move_ids
						if p.notes_one2many:
							for material_notes in p.notes_one2many:
								user_name=material_notes.user_id
								source=material_notes.source.id
								comment=material_notes.comment
								comment_date=material_notes.comment_date
								source_id=0
								if material_notes.source:
									source_id ="( SELECT id FROM res_company WHERE name='" + str(material_notes.source.name) +"')"
								remark_srch_id = "\n remark_srch_id= (SELECT id FROM stock_move_comment_line WHERE  comment = ' "+ str(comment) + "' AND user_id ='"+str(user_name) + "' AND source = "+ source_id + " AND comment_date = '"+ str(comment_date) + "' AND indent_id = " + stock_val + ");"
								ifstr="\n IF remark_srch_id IS NOT NULL THEN \n"
								remark_srch_del="\n DELETE FROM stock_move_comment_line WHERE id in (remark_srch_id);"
								
								msg_flag=True
								msg_unread_ids="\n UPDATE stock_move SET write_date=(now() at time zone \'UTC\'),write_uid=1, msg_check_unread=True,msg_check_read=False WHERE id= "+ stock_val +";"
								notes_line_id="\n INSERT INTO stock_move_comment_line (create_uid,create_date,indent_id,user_id,source,comment_date,comment) VALUES (1,(now() at time zone 'UTC'),"+ stock_val +",'"+str(user_name)+"',"+source_id+",'"+str(comment_date)+"','"+str(comment)+"');"
								sync_str += remark_srch_id + ifstr + remark_srch_del + elsestr + msg_unread_ids + endif + notes_line_id
					if i.comment_line:						
						for notes_line in i.comment_line:
							if notes_line.source:
								source_id	="(SELECT id FROM res_company WHERE name='" +str(notes_line.source.name)+"')"
								remark_srch_id = "\n remark_srch_id=( SELECT id FROM indent_remark WHERE remark_field ='"+str(notes_line.comment) +"' AND \"user\" ='"+str(notes_line.user_id)+"' AND remark = " + origin_ids+" AND date='"+str(notes_line.comment_date)+ "' AND source = "+ source_id +");"
								ifstr="\n IF remark_srch_id IS NOT NULL THEN \n "
								notes_line_id="\n UPDATE indent_remark SET write_date=(now() at time zone \'UTC\'),write_uid=1,\"user\"='"+str(notes_line.user_id if notes_line.user_id else '')+"', source="+ source_id +", date= '"+str(notes_line.comment_date)+ "', remark_field= '"+str(notes_line.comment) +"' WHERE id in (remark_srch_id);"
								notes_line_ids="\n INSERT INTO indent_remark (create_uid,create_date,remark,\"user\",source,date,remark_field) VALUES (1,(now() at time zone 'UTC')," + origin_ids + ",'" + str(notes_line.user_id if notes_line.user_id else '')+ "'," + source_id + ",'" + str(notes_line.comment_date) + "','" + str(notes_line.comment) +"');"
								sync_str += remark_srch_id + ifstr + notes_line_id + elsestr + notes_line_ids + endif
								
					if msg_flag :
						msg_ids="\n UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,msg_check = True WHERE id = " +origin_ids +";"
						sync_str += msg_ids
					sync_str += '''FOR state1 IN (SELECT state FROM stock_move WHERE picking_id='''+origin_ids+''') 
LOOP 
	IF state1 != 'done' AND state1 IS NOT NULL THEN
		flag1 =1;
	END IF;
	IF state1 != 'cancel' AND state1 IS NOT NULL THEN
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
     UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,state='done' WHERE id='''+origin_ids+''';
  END IF;
  IF flag2=0 THEN
	UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,state='cancel' WHERE id='''+origin_ids+''';
  END IF;
  IF flag2=1 AND counter=0 AND flag1=1 AND flag3 =1 THEN
	UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,state='done' WHERE id='''+origin_ids+''';
  END IF;'''
					sync_str +=ret+final+fun_call
					with open(filename,'a') as f :
						f.write(sync_str)
						f.close()
 ###############################################################################################################################
				sock = xmlrpclib.ServerProxy(obj)
				if conn_central_flag==False:
					ln_ids = ''
					count = 0
					origin_srch = [('ci_sync_id_seq','=',i.ci_sync_id),('origin', '=', i.indent_no)] ## 15 july assign job
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
								val_prod_series_srh = sock.execute(dbname, userid, pwd, 'product.series.main', 'search', prod_series_srh)
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
									product_ids = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)	
								if ln.generic_id:
									generic_srch=[('name','=',ln.generic_id.name)]
									generic_ids=sock.execute(dbname, userid, pwd, 'product.generic.name', 'search', generic_srch)						
									for serials in ln.serial_line:
										count = count + 1
										series_create = {
													    'sr_no':count,
													    'product_code':ln.product_code,
													    'product_name':product_ids[0],
													    'generic_id':generic_ids[0] if generic_ids else False,
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
									    notes_line_dict = {
												    'user':notes_line.user_id if notes_line.user_id else '',
												    'source':source_id[0] if source_id else '',
												    'date':notes_line.comment_date,
												    'remark_field':notes_line.comment,
												     }
									    notes_line_id = sock.execute(dbname, userid, pwd, 'indent.remark', 'write', k , notes_line_dict)
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
				raise
				userid = sock_common.login(dbname, username, pwd)
			except Exception as Err:
				offline_obj=self.pool.get('offline.sync')
				offline_sync_sequence = context.get('offline_sync_sync') if context.get('offline_sync_sync') else False
				conn_dispatcher_flag = True
				if not offline_sync_sequence:
					offline_obj.create(cr,uid,{'src_model':self._name,'dest_model':False,'sync_company_id':i.source_company.id,'srch_condn':False,'form_id':ids[0],'func_model':'generate_indent_grn_branch','error_log':Err,})
				else:
					offline_sync_id = offline_obj.search(cr, uid, [('sync_sequence','=',offline_sync_sequence)])
					offline_obj.write(cr, uid, offline_sync_id, {'res_active':conn_dispatcher_flag})
				##########SQL######################OFFLINE#################SYNC##############################################
			
				current_company=self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key #changes 22jul16
				con_cat = dbname+"-"+branch_id.vpn_ip_address+"-"+str(current_company)+'-Recieve_Indent-'+str(date)+'_'+str(time_cur)+'.sql'
				filename = os.path.expanduser('~')+'/indent_sync/'+con_cat
				directory_name = str(os.path.expanduser('~')+'/indent_sync/')
				sync_str=''
				if not os.path.exists(directory_name):
					os.makedirs(directory_name)
				d = os.path.dirname(directory_name)
				ln_ids = ''
				count = 0
				func_string ="\n\n CREATE OR REPLACE FUNCTION Recieve_Indent() RETURNS int LANGUAGE plpgsql AS $$ \n\n"
				declare=" DECLARE \n \t"
				var1=""" origin_stock_transfer INT;\n remark_srch_id INT; \n flag1 INT;
					state1 VARCHAR;
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
				fun_call="\n SELECT Recieve_Indent();\n"
				sync_str += func_string + declare + var1
				origin_ids_qq ="(SELECT id FROM stock_picking WHERE id = "+str(i.stock_id) + " AND origin = '" +str(i.indent_no) + "')" 
				product_uom_qty = 0
				for p in i.receive_indent_line:
					product_ids11 = "(SELECT id FROM product_product WHERE name_template ='" + str(p.product_name.name.replace("'","''")) + "')"
					stock_val ="( SELECT id FROM stock_move WHERE product_id = " + product_ids11 + " AND picking_id = " + origin_ids_qq +"order by id LIMIT 1)" 
					move_ids= "\n UPDATE stock_move SET  write_date=(now() at time zone \'UTC\'),write_uid=1,state = 'done' WHERE id = "+stock_val+";"
					sync_str += move_ids
					if p.notes_one2many:
						for material_notes in p.notes_one2many:
							user_name=material_notes.user_id
							source=material_notes.source.id
							comment=material_notes.comment
							comment_date=material_notes.comment_date
							source_id=0
							if material_notes.source:
								source_id ="( SELECT id FROM res_company WHERE name='" + str(material_notes.source.name) +"')"
							remark_srch_id = "\n remark_srch_id= (SELECT id FROM stock_move_comment_line WHERE  comment = '"+ str(comment) + "' AND user_id ='"+str(user_name) + "' AND source = "+ source_id + " AND comment_date = '"+ str(comment_date) + "' AND indent_id = " + stock_val + ");"
							ifstr="\n IF remark_srch_id IS NOT NULL THEN \n"
							remark_srch_del="\n DELETE FROM stock_move_comment_line WHERE id in (remark_srch_id);"
							
							msg_flag_branch=True
							msg_unread_ids="\n UPDATE stock_move SET write_date=(now() at time zone \'UTC\'),write_uid=1,msg_check_unread=True,msg_check_read=False WHERE id= "+ stock_val +";"
							notes_line_id="\n INSERT INTO stock_move_comment_line (create_uid,create_date,indent_id,user_id,source,comment_date,comment) VALUES (1,(now() at time zone 'UTC'),"+ stock_val +",'"+str(user_name)+"',"+source_id+",'"+str(comment_date)+"','"+str(comment)+"');"
							sync_str += remark_srch_id + ifstr + remark_srch_del + elsestr + msg_unread_ids + endif + notes_line_id
				if i.comment_line:						
					for notes_line in i.comment_line:
						if notes_line.source:
							source_id	="(SELECT id FROM res_company WHERE name='" +str(notes_line.source.name)+"')"
						remark_srch_id = "\n remark_srch_id=( SELECT id FROM indent_remark WHERE remark_field ='"+str(notes_line.comment) +"' AND \"user\" ='"+str(notes_line.user_id)+"' AND remark = " + origin_ids_qq+" AND date='"+str(notes_line.comment_date)+ "' AND source = "+ source_id +");"
						ifstr="\n IF remark_srch_id IS NOT NULL THEN \n "
						notes_line_id="\n UPDATE indent_remark SET write_date=(now() at time zone \'UTC\'),write_uid=1,\"user\"='"+str(notes_line.user_id if notes_line.user_id else '')+"', source="+ source_id +", date= '"+str(notes_line.comment_date)+ "', remark_field= '"+str(notes_line.comment) +"' WHERE id in (remark_srch_id);"
						notes_line_ids="\n INSERT INTO indent_remark (create_uid,create_date,remark,\"user\",source,date,remark_field) VALUES (1,(now() at time zone 'UTC')," + origin_ids_qq + ",'" + str(notes_line.user_id if notes_line.user_id else '')+ "'," + source_id + ",'" + str(notes_line.comment_date) + "','" + str(notes_line.comment) +"');"
						sync_str += remark_srch_id + ifstr + notes_line_id + elsestr + notes_line_ids + endif
				if msg_flag_branch:
					msg_ids="\n UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,msg_check = True WHERE id = " +origin_ids_qq +";"
					sync_str += msg_ids
				origin_stock_transfer ="\n origin_stock_transfer = ( SELECT id FROM stock_transfer WHERE stock_transfer_no ='"+ str(i.order_number) + "' AND origin ='" + str(i.indent_no) + "');"
				move_ids=" \n UPDATE stock_transfer SET write_date=(now() at time zone \'UTC\'),write_uid=1,state ='done' WHERE id= origin_stock_transfer ;"
				sync_str += origin_stock_transfer + move_ids
				################################15 july job assign				
				for p in i.receive_indent_line:
					product_search="\n (select id from product_product where name_template ='"+str(p.product_name.name.replace("'","''"))+"') "
					product_trans_srh ="( select id FROM product_transfer WHERE product_name = " + product_search + " and prod_id = origin_stock_transfer"+" limit 1);" 					
					product_trans_update="update product_transfer set write_date=(now() at time zone \'UTC\'),write_uid=1,state='done' where id="+product_trans_srh
					sync_str += product_trans_update
				#######################################
				if i.comment_line:
					for notes_line in i.comment_line:
						if notes_line.source:
							source_id="(SELECT id FROM res_company WHERE name='" +str(notes_line.source.name)+"')"
						remark_srch_id = "\n remark_srch_id=( SELECT id FROM stock_transfer_remarks WHERE name ='"+str(notes_line.comment) +"' AND user_name ='"+str(notes_line.user_id)+"' AND stock_transfer_id =  origin_stock_transfer AND date='"+str(notes_line.comment_date) +"');"
						ifstr="\n IF remark_srch_id IS NOT NULL THEN \n "
						notes_line_id="\n UPDATE stock_transfer_remarks SET write_date=(now() at time zone \'UTC\'),write_uid=1,user_name='"+str(notes_line.user_id if notes_line.user_id else '')+"', source="+ source_id +", date= '"+str(notes_line.comment_date)+ "', name= '"+str(notes_line.comment) +"' WHERE id in (remark_srch_id);"
						notes_line_ids="\n INSERT INTO stock_transfer_remarks (create_uid,create_date,stock_transfer_id, user_name, source, date, name) VALUES (1,(now() at time zone 'UTC'), origin_stock_transfer ,'" + str(notes_line.user_id if notes_line.user_id else '')+ "'," + source_id + ",'" + str(notes_line.comment_date) + "','" + str(notes_line.comment) +"');"
						sync_str += remark_srch_id + ifstr + notes_line_id + elsestr + notes_line_ids + endif
				
				for ln in i.receive_indent_line:
					for serials in ln.serial_line:
						if serials.reject_serial_check or serials.short:
							reject_serial_check = serials.reject_serial_check				
							search_val_prod="(SELECT id FROM product_series WHERE serial_no = '"+ str(serials.serial_name) + "')"
							search_val22="(SELECT id FROM transfer_series WHERE serial_no ="+ search_val_prod +")"
							create_series="\n UPDATE transfer_series SET write_date=(now() at time zone \'UTC\'),write_uid=1,reject_serial_check = '"+str(serials.reject_serial_check) +", short = '"+str(serials.short) +" WHERE id = "+ search_val22 + ";"
							sync_str += create_series
					product_ids11 = "(SELECT id FROM product_product WHERE name_template = '" + str(ln.product_name.name.replace("'","''")) + "')"
					rec_search_val="(SELECT id FROM product_transfer WHERE product_name = "+ product_ids11 + " AND prod_id =  origin_stock_transfer )"
					
					if ln.notes_one2many:
						for material_notes in ln.notes_one2many:
							user_name=material_notes.user_id
							source=material_notes.source.id
							comment=material_notes.comment
							comment_date=material_notes.comment_date
							source_id=''
							if material_notes.source:
								source_id ="(SELECT id FROM res_company WHERE name = '"+ str(material_notes.source.name) +"')"
							remark_srch_id = "\n remark_srch_id= (SELECT id FROM product_transfer_comment_line WHERE  comment = ' "+ str(comment) + "' AND user_id ='"+str(user_name) + "' AND source = "+ source_id + " AND comment_date = '"+ str(comment_date) + "' AND indent_id = " + rec_search_val + ");"
							ifstr="\n IF remark_srch_id IS NOT NULL THEN \n"
							remark_srch_del="\n DELETE FROM product_transfer_comment_line WHERE id in (remark_srch_id);"
							
							msg_flag_stock=True
							msg_unread_ids="\n UPDATE product_transfer SET write_date=(now() at time zone \'UTC\'),write_uid=1,msg_check_unread=True,msg_check_read=False WHERE id= "+ rec_search_val +";"
							notes_line_id="\n INSERT INTO product_transfer_comment_line (create_uid,create_date,indent_id,user_id,source,comment_date,comment) VALUES (1,(now() at time zone 'UTC'),"+ rec_search_val +",'"+str(user_name)+"',"+source_id+",'"+str(comment_date)+"','"+str(comment)+"');"
							sync_str += remark_srch_id + ifstr + remark_srch_del + elsestr + msg_unread_ids + endif + notes_line_id
				if msg_flag_stock:
					msg_ids="\n UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,msg_check = True WHERE id = " +origin_ids_qq +";"
					sync_str += msg_ids
				sync_str += '''\n FOR state1 IN (SELECT state FROM stock_move WHERE picking_id='''+origin_ids_qq+''') 
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
     UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,state='done' WHERE id='''+origin_ids_qq+''';
  END IF;
  IF flag2=0 THEN
	UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,state='cancel' WHERE id='''+origin_ids_qq+''';
  END IF;
  IF flag2=1 AND counter=0 AND flag1=1 AND flag3 =1 THEN
	UPDATE stock_picking SET write_date=(now() at time zone \'UTC\'),write_uid=1,state='done' WHERE id='''+origin_ids_qq+''';
  END IF;'''
  				sync_str += ret + final + fun_call
				with open(filename,'a') as f :
					f.write(sync_str)
					f.close()		
				#print Mahesh 
##################################################################################################################################
			sock = xmlrpclib.ServerProxy(obj)
			if conn_dispatcher_flag == False:
			    origin_srch_qq = [('id', '=',i.stock_id),('origin', '=',i.indent_no)]
			    origin_ids_qq = sock.execute(dbname, userid, pwd,'stock.picking', 'search', origin_srch_qq)
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
											    'remark_fielserial_nod':notes_line.comment,
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
					###################update product transfer ########################
				    for p in i.receive_indent_line:
						product_srch = [('name', '=',p.product_name.name)]
						product_ids11 = sock.execute(dbname, userid, pwd, 'product.product', 'search', product_srch)
						product_trans_srh = [('product_name', '=',product_ids11[0]),('prod_id','=',origin_stock_transfer[0])]
						product_trans = sock.execute(dbname, userid, pwd, 'product.transfer', 'search', product_trans_srh)
						print '____________________________',product_ids11,product_trans,p.product_name.name
						if product_trans:
							update_state = {
								'state':'done'
								}
							move_ids= sock.execute(dbname, userid, pwd, 'product.transfer', 'write', product_trans[0], update_state)
					
					
					###########################################
					
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
				    msg_line = {  'msg_check':True
										       }
				    msg_ids= sock.execute(dbname, userid, pwd, 'stock.transfer', 'write',origin_stock_transfer, msg_line)

		return True

receive_indent()




class receive_indent_comment_line(osv.osv):
	_inherit="receive.indent.comment.line"
	_columns={
		'user_id':fields.char('User Name',size=64),
	}



# Receive Indent Grid
class material_details(osv.osv):
	_inherit="material.details"


	def _compute_line_total(self, cr, uid, ids,field_name, arg, context=None):
		result = {}
		for r in self.browse(cr, uid, ids):
			result[r.id] = (r.price_unit * r.qty_received)+ r.cst_vat + r.excise_value
		return result

	# _columns={
	# 	'cst_vat':fields.float('CST/VAT',size=64),
	# 	'excise_value':fields.float('Excise Value',size=64),
	# 	'last_delivery':fields.boolean('Last Delivery'),
	# 	'batch': fields.many2one('res.batchnumber','Batch ID',domain="[('name','=',product_name),('branch_name','=',branch_name)]"),
	# 	'delivery_type': fields.selection([('banned_st','Branch Stock Transfer'),
	# 		('excess_st','Excess Stock Transfer'),
	# 		('inter_branch_st','Inter branch Stock Transfer'),
	# 		('direct_delivery','Direct Delivery'),
	# 		('local_purchase','Local Purchase'),
	# 		('internal_delivery','Internal Delivery')],'Delivery Type *'),
	# 	'subtotal': fields.function(_compute_line_total, type='float', obj='materials.details', method=True, store=False, string='Subtotal'),
	# 	'godown': fields.many2one('res.company','Godown'),
	# }


	def default_get(self,cr,uid,fields,context=None):
		if context is None: context = {}
		res = super(material_details, self).default_get(cr, uid, fields, context=context)
		if context.has_key('branch_name'):
			res['godown'] = context.get('branch_name','')
		return res

	def onchange_delivery_type(self,cr,uid,ids,delivery_type_others):
		v={}
		v['delivery_type']=delivery_type_others
		return {'value': v}  	


	def onchange_product_code(self,cr,uid,ids,product_name):
		v={}
		res=self.pool.get('product.product').browse(cr,uid,product_name)
		v['product_code']=res.default_code
		return {'value':v}


	def onchange_generic_name(self,cr,uid,ids,product_name):
		v={}
		res=self.pool.get('product.product').browse(cr,uid,product_name)
		v['generic_id']=res.generic_name.id
		return {'value':v}
		

	# def onchange_batch_manudate(self,cr,uid,ids,batch,delivery_type):
	# 	v={}
	# 	res=self.pool.get('res.batchnumber').browse(cr,uid,batch)
	# 	v['manufacturing_date']=res.manufacturing_date
	# 	if delivery_type == 'local_purchase':
	# 		v['price_unit']=float(res.bom)
	# 	else:
	# 		v['price_unit']=res.st
	# 	return {'value':v}


	def onchange_documented_quantity(self,cr,uid,ids,documented_qty,short,excess,reject):
		val={}
		total_quantity=(documented_qty+excess)-(short+reject)
		if total_quantity < 0:
			val['short']=0
			val['excess']=0
			val['reject']=0
			val['qty_received']=0
			val['subtotal']=0
			raise osv.except_osv(('Alert!'),('Quantity cannot be greater than documented qty')) 
		else:
			val['qty_received']=total_quantity
		return{'value':val}

	def onchange_product_name(self,cr,uid,ids,product_name): 
		v={}
		if product_name:
			res=self.pool.get('product.product').browse(cr,uid,product_name)
			if res.batch_type == 'non_applicable':
				red=self.pool.get('res.batchnumber').search(cr,uid,[('name','=',product_name)])
				for r in self.pool.get('res.batchnumber').browse(cr,uid,red):
					print 'yesssssssssssssssss',r.batch_no
			v['product_uom'] = res.local_uom_id.id	
			v['product_code']=res.default_code
			v['generic_id']=res.generic_name.id
			return {'value': v}

	def psd_series_wizard_others(self,cr,uid,ids,context=None):
		for i in self.browse(cr,uid,ids):
			flag=False
			count=0
			form_id = i.id
			if i.reject>0 or i.short >0 or i.excess>0:

				if i.excess>0:
					for serials in i.serial_line:
						if serials.excess:
							count=count+1
					if i.excess > count:
						flag=True
				self.pool.get('material.details').write(cr,uid,i.id,{'series_check_new':True,'excess_check':flag,'readonly_check':False})
				if not i.serial_line:
					search_serial=self.pool.get('transfer.series').search(cr,uid,[('stn_no','=',i.stn_no),('product_name','=',i.product_name.id)])
					for rec in search_serial:
						self.pool.get('transfer.series').write(cr,uid,rec,{'series_line':form_id})
			else:
				self.pool.get('material.details').write(cr,uid,i.id,{'series_check_new':True,'readonly_check':True})	
				if not i.serial_line:
					search_serial=self.pool.get('transfer.series').search(cr,uid,[('stn_no','=',i.stn_no),('product_name','=',i.product_name.id)])
					for rec in search_serial:
						self.pool.get('transfer.series').write(cr,uid,rec,{'series_line':form_id})	
			return {
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'material.details',
					'res_id': int(form_id),
					'view_id': False,
					'type': 'ir.actions.act_window',
					'target': 'new',
					}
		return True


class stock_material(osv.osv):
	_inherit="stock.material"

	def _total_value(self, cr, uid, ids,field_name, arg, context=None):
		records=self.browse(cr,uid,ids)
		result={}
		for stock in records:
			total=0
			for line in stock.stock_search_line:
				#price=line.st*line.qty
				#price=line.local_qty*line.mrp
				price=line.qty_actual*line.st
				total+=price
			result[stock.id]=total	
		return result

	# def _total_quantity(self, cr, uid, ids,field_name, arg, context=None):
	# 	records=self.browse(cr,uid,ids)
	# 	result={}
	# 	for stock in records:
	# 		total=0
	# 		for line in stock.stock_search_line:
	# 			qty_actual=line.qty_actual
	# 			total+=qty_actual
	# 		result[stock.id]=total	
	# 	return result


	def _total_quantity(self, cr, uid, ids,field_name, arg, context=None):
		records=self.browse(cr,uid,ids)
		result={}
		for stock in records:
			total=0
			for line in stock.stock_search_line:
				local_actual=line.local_qty
				total+=local_actual
			result[stock.id]=total	
		return result

	_columns={
		'total_quantity': fields.function(_total_quantity, type='integer', method=True, store=False, string='Total Quantity'),
		'total_value':fields.function(_total_value,type='float', obj='stock.material',digits=(16,2), method=True, store=False, string='Total Value'),
		}


# class res_batchnumber(osv.osv):
# 	_inherit="res.batchnumber"
	

# 	def default_get(self, cr, uid, ids,fields, context=None):
# 		if context is None: context = {}
# 		mrp_dates_list = []
# 		res = super(res_batchnumber, self).default_get(cr, uid, fields, context=context)
# 		new_browse_id = self.browse(cr,uid,ids[0])
# 		if new_browse_id.batch_no == 'NA':
# 			print "NA Batch"
# 			search_batch_ids = self.search(cr,uid,[('batch_no','=','NA'),('name','=',new_browse_id.name.id)])
# 			if len[search_batch_ids] != 1:
# 				raise osv.except_osv(('Warning !'),('This Product have more than one NA batches'))
# 			else:
# 				browse_data = self.browse(cr,uid,search_batch_ids)
# 				res['st'] = browse_data.st
# 		elif new_browse_id.batch_no == None:
# 			print "None Batch"
# 		else:
# 			print "New Batch"
# 			search_batch_ids = self.search(cr,uid,[('batch_no','=',new_browse_id.batch_no),('name','=',new_browse_id.name.id)])
# 			browse_data = self.browse(cr,uid,search_batch_ids)
# 			for line in browse_data:
# 				mrp_dates_list.append(line.manufacturing_date)
# 			search_update_id = self.search(cr,uid,[('batch_no','=',new_browse_id.batch_no),('manufacturing_date','=',max(mrp_dates_list))])
# 			browse_prices = self.browse(cr,uid,search_update_id[0])
# 			res['mrp'] = browse_prices.mrp
# 			res['export_price'] = browse_prices.export_price
# 			res['distributor'] = browse_prices.distributor
# 		return res
# res_batchnumber()
