# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv,fields
from datetime import datetime

class account_tax(osv.osv):
	_inherit = 'account.tax'

	_columns = {
		'select_tax_type':fields.selection([
			('service_tax','Service Tax'),
			('edu_cess','Edu Cess'),
			('hs_edu_cess','Hs Edu Cess'),
			('swachh_bharat_service','SB Cess'),
			('krishi_kalyan_service','KK Cess'),
			('cgst','CGST'),
			('sgst','SGST'),
			('utgst','UTGST'),
			('igst','IGST'),
			('cess','CESS')
			], 'Tax Type'),
	}

account_tax()

class account_account(osv.osv):
	_inherit = 'account.account'

	_columns = {
		'gst_applied':fields.boolean('GST Applied?'),
		'hsn_sac_code':fields.char('HSN/SAC Code',size=10),
		'rcm_rate': fields.float('Rate'),
		'account_selection':fields.selection([
					('advance','Advance'),
					('advance_against_ref','Advance Against Reference'),
					('against_ref','Against Reference'),
					('bank_charges','Bank Charges'),
					('cash','Cash'),
					('funds_transferred_ho','Funds Transferred to HO'),
					('ho_remmitance','HO Remmitance'),
					('iob_one','Receive in Bank'),
					('iob_two','Pay from Bank'),
					('employee','Employee'),
					('others','Others(CFOB)'),
					('primary_cost_cse','Primary Cost Category(CSE)'), # Emp Name + Amount
					('primary_cost_office','Primary Cost Category(Office)'), # Office Name + Amount
					('primary_cost_phone','Primary Cost Category(Phone/Mobile No.)'), #Phone/MobileNo+EmpName+Amount
					('primary_cost_vehicle','Primary Cost Category(Vehicle)'), #Vehicle No. + Empe Name + Amount
					('primary_cost_service','Primary Cost Category(Service)'), # Service + Amount
					('primary_cost_cse_office','Primary Cost Category(CSE Office)'), # office Name + Employee Name + Amount
					('security_deposit','Security Deposits'),
					('sundry_deposit','Sundry Deposits'),
					('itds','ITDS'),('itds_receipt','ITDS on Contract Receipts'),
					('st_input','ST Input'),
					('excise_input','Excies Input'),
					#('edu_service','Edu Cess'),
					#('service_tax_12.0','service Tax 12.0%'),
					#('service_tax_14.0','service Tax 14.0%'), ## for 14.0 % 
					#('h&s_service','H & S service'),
					#('swachh_bharat_service','SB Cess 0.50% '),
					#('krishi_kalyan_service','KK Cess 0.50%'),
					('tax','Tax'),
					('st_input_tax','ST Input Tax'),
					('expenses','Expenses'),
					],'Selection'),
		'goods_applicable':fields.boolean('Goods Applicable?'),
	}

	_defaults = {
		'gst_applied': False,
		'rcm_rate': 0.0,
		'goods_applicable':False,
	}

account_account()


class gst_rate_master(osv.osv):
	_name = 'gst.rate.master'
	_rec_name = 'rate'
	_order = 'id asc'
	_columns = {
		'gst_rate_name':fields.char('GST Rate',size=10),
		'rate':fields.float('Rate'),
	}

gst_rate_master()

class tax(osv.osv):
	_inherit="tax"
	
	def recr_amount1(self,cr,uid,obj,value,date):
	        obj=self.pool.get('account.tax').browse(cr,uid,obj.id)
		if not obj.parent_id:
			return obj.amount*value
		else:
			if obj.parent_id.effective_from_date <= date and obj.parent_id.effective_to_date > date:
				return obj.amount*self.recr_amount1(cr,uid,obj.parent_id,value,date)
		return 0
		
	def recr_amount(self,obj,value,date):
		if not obj.parent_id:
			if obj.amount==None:
				obj.amount=0.0
			return obj.amount*value
		else:
			if obj.parent_id.effective_from_date <= date and obj.parent_id.effective_to_date > date:
				return obj.amount*self.recr_amount(obj.parent_id,value,date)
		return 0

	def add_tax(self,cr,uid,model_id,model,compare_date=datetime.now().date().strftime("%Y-%m-%d")):		
		val1=0
		qry=if_present=False
		model_id=model_id if isinstance(model_id,(int,long)) else model_id[0]                
		inspection_id=sale_quotation_id=sale_contract_id='Null'
		compare_date = datetime.now().date().strftime("%Y-%m-%d")
		if model_id and model:
			for order in self.pool.get(model).browse(cr,uid,[model_id]):
				val1=round(self.get_total_amount(model,order))
				tax_ids=self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',compare_date),('effective_to_date','>',compare_date),('select_tax_type','!=',False)])
				GST_val=self.pool.get('account.account').search(cr,uid,[('name','=','GST')])
				if GST_val:
					if model=='sale.contract':
						contract_data=self.pool.get('sale.contract').browse(cr,uid,model_id)
						if contract_data.contract_date:
							tax_ids=self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',contract_data.contract_date),('effective_to_date','>',contract_data.contract_date),('select_tax_type','!=',False)])
						Inter_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','igst')])[0]
						union_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','utgst')])[0]
						state_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','sgst')])[0]
						central_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','cgst')])[0]
						if contract_data.gst_contract == True:
							for i in order.contract_line_id12:
								if not i.state_id.id and not i.state_id.name:
									raise osv.except_osv(('Alert'),("State name is blank for customer location, Kindly update state to generate the proper taxes in contract!"))
								if order.branch_id.state_id.name==i.state_id.name:
									if Inter_state_id in tax_ids:
										tax_ids.remove(Inter_state_id)
									if order.branch_id.state_id.union_territory==False:
										if union_state_id in tax_ids:
											tax_ids.remove(union_state_id)
									else:
										if state_gst in tax_ids:
											tax_ids.remove(state_gst)
								else:
									if union_state_id in tax_ids:
										tax_ids.remove(union_state_id)
									if state_gst in tax_ids:
										tax_ids.remove(state_gst)
									if central_gst in tax_ids:
										tax_ids.remove(central_gst)
						else:
							for i in order.contract_line_id:
								if not i.state_id.id and not i.state_id.name:
									raise osv.except_osv(('Alert'),("State name is blank for customer location, Kindly update state to generate the proper taxes in contract!"))
								if order.branch_id.state_id.name==i.state_id.name:
									if Inter_state_id in tax_ids:
										tax_ids.remove(Inter_state_id)
									if order.branch_id.state_id.union_territory==False:
										if union_state_id in tax_ids:
											tax_ids.remove(union_state_id)
									else:
										if state_gst in tax_ids:
											tax_ids.remove(state_gst)
								else:
									if union_state_id in tax_ids:
										tax_ids.remove(union_state_id)
									if state_gst in tax_ids:
										tax_ids.remove(state_gst)
									if central_gst in tax_ids:
										tax_ids.remove(central_gst)
								# if (union_state_id in tax_ids or state_gst in tax_ids or central_gst in tax_ids): 
								# 	tax_ids.remove(union_state_id)
								# 	tax_ids.remove(state_gst)
								# 	tax_ids.remove(central_gst)
					if model=='inspection.costing':
						Inter_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','igst')])[0]
						union_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','utgst')])[0]
						state_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','sgst')])[0]
						central_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','cgst')])[0]

						for i in order.inspection_line:
							if order.company_id.state_id.name==i.state_id.name:
								if Inter_state_id in tax_ids:
									tax_ids.remove(Inter_state_id)
								if order.company_id.state_id.union_territory==False:
									if union_state_id in tax_ids:
										tax_ids.remove(union_state_id)
								else:
									if state_gst in tax_ids:
										tax_ids.remove(state_gst)
							else:
								if union_state_id in tax_ids:
									tax_ids.remove(union_state_id)
								if state_gst in tax_ids:
									tax_ids.remove(state_gst)
								if central_gst in tax_ids:
									tax_ids.remove(central_gst)
								# if (union_state_id in tax_ids or state_gst in tax_ids or central_gst in tax_ids): 
								# 	tax_ids.remove(union_state_id)
								# 	tax_ids.remove(state_gst)
								# 	tax_ids.remove(central_gst)
					if model=='sale.quotation':
						Inter_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','igst')])[0]
						union_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','utgst')])[0]
						state_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','sgst')])[0]
						central_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','cgst')])[0]

						for i in order.quotation_line_id:
							if order.company_id.state_id.name==i.state_id.name:
								if Inter_state_id in tax_ids:
									tax_ids.remove(Inter_state_id)
								if order.company_id.state_id.union_territory==False:
									if union_state_id in tax_ids:
										tax_ids.remove(union_state_id)
								else:
									if state_gst in tax_ids:
										tax_ids.remove(state_gst)
							else:
								if union_state_id in tax_ids:
									tax_ids.remove(union_state_id)
								if state_gst in tax_ids:
									tax_ids.remove(state_gst)
								if central_gst in tax_ids:
									tax_ids.remove(central_gst)
								# if (union_state_id in tax_ids or state_gst in tax_ids or central_gst in tax_ids): 
								# 	tax_ids.remove(union_state_id)
								# 	tax_ids.remove(state_gst)
								# 	tax_ids.remove(central_gst)
				self.delete_tax(cr,model,model_id,tax_ids)
				service_classification_temp=''
				# try:	
				# 	service_classification_temp = order.service_classification
				# except Exception:
				# 	pass
				if model=='sale.contract':
					service_classification_temp = order.service_classification
				# if order.exempted != True or service_classification_temp !='exempted':
				for i in self.pool.get('account.tax').browse(cr,uid,tax_ids): 
					current_tax_amount=self.recr_amount(i,val1,compare_date)
					if model=='inspection.costing':
						inspection_id=model_id
						inspection_costing_line_id=self.pool.get('inspection.costing.line').search(cr,uid,[('inspection_line_id','=',model_id)])
						for j in self.pool.get('inspection.costing.line').browse(cr,uid,inspection_costing_line_id):
							sale_quotation_id=j.quotation_id1.id if j.quotation_id1 else 'Null'
							sale_contract_id=j.contract_id1.id if j.contract_id1 else 'Null'

					if model=='sale.quotation':
						inspection_costing_line_id=self.pool.get('inspection.costing.line').search(cr,uid,[('quotation_id1','=',model_id)])
						for j in self.pool.get('inspection.costing.line').browse(cr,uid,inspection_costing_line_id):
							inspection_id=j.inspection_line_id.id if j.inspection_line_id else 'Null'
							sale_contract_id=j.contract_id1.id if j.contract_id1 else 'Null'
						sale_quotation_id=model_id

					if model=='sale.contract':
						contract_data=self.pool.get('sale.contract').browse(cr,uid,model_id)
						if contract_data.gst_contract == True:
							inspection_costing_line_id=self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id12','=',model_id)])
						else:
							inspection_costing_line_id=self.pool.get('inspection.costing.line').search(cr,uid,[('contract_id1','=',model_id)])
						if contract_data.service_classification=='exempted':
							current_tax_amount=0.00
						for j in self.pool.get('inspection.costing.line').browse(cr,uid,inspection_costing_line_id):
							sale_quotation_id=j.quotation_id1.id if j.quotation_id1 else 'Null'
							inspection_id=j.inspection_line_id.id if j.inspection_line_id else 'Null'
						sale_contract_id=model_id
					print current_tax_amount,'pppppppppp'
					insert_qry='insert into tax(name,amount,inspection_costing_id,sale_quotation_id,sale_contract_id,account_tax_id)values(%s,%s,%s,%s,%s,%s)' %("'"+str(i.name)+"'",str(round(current_tax_amount,2)),str(inspection_id),str(sale_quotation_id),str(sale_contract_id),str(i.id))

					#insert_qry='insert into tax(name,amount,'+self.map_tax_model(model)+',account_tax_id)values(%s,%s,%s,%s)' %("'"+str(i.name)+"'",str(current_tax_amount),str(model_id),str(i.id))
					
					if model=='inspection.costing': 
						qry="select account_tax_id from tax where inspection_costing_id=%s and account_tax_id=%s" %(str(model_id),str(i.id))								
						update_qry="update tax set amount=%s where inspection_costing_id=%s and account_tax_id=%s" %(str(round(current_tax_amount,2)),str(model_id),str(i.id))
						
					if model=='sale.quotation':
						qry="select id,name from tax where inspection_costing_id=(select id from inspection_costing where sequence_id=%s) and account_tax_id=%s" %("'"+str(order.sequence_id)+"'",str(i.id))								
						update_qry="update tax set sale_quotation_id=%s where inspection_costing_id=(select id from inspection_costing where sequence_id=%s) and account_tax_id=%s" %(str(model_id),"'"+str(order.sequence_id)+"'",str(i.id))
					if model=='sale.contract':
						if order.quotation_number:
							qry="select account_tax_id from tax where sale_quotation_id=(select id from sale_quotation where quotation_number=%s) and account_tax_id=%s" %("'"+str(order.quotation_number)+"'",str(i.id))
						else:
							qry="select account_tax_id from tax where sale_contract_id=%s and account_tax_id=%s" %(str(model_id),str(i.id))
						update_qry="update tax set sale_contract_id=%s where sale_quotation_id=(select id from sale_quotation where quotation_number=%s) and account_tax_id=%s" %(str(model_id),"'"+str(order.quotation_number)+"'",str(i.id))
					if qry and current_tax_amount>=0:
						cr.execute(qry)									
						if_present=cr.fetchall()
						if not if_present :
							cr.execute(insert_qry)
							cr.commit()
						else:
							cr.execute(update_qry)
							cr.commit()
				if model=='sale.contract':
					total_tax=amount=round_amount=difference=0.0
					for amt in order.tax_one2many:
						total_tax+=amt.amount
					grand_total_amount=val1+total_tax
					amount=grand_total_amount
					round_amount=round(grand_total_amount)
					difference=round((round_amount-amount),2)
					if order.service_classification in ('exempted','sez'):
						difference=0.0
					cr.execute("update sale_contract set round_off_val=%s where id=%s" %(str(difference),str(order.id)))

		return True

	def get_total_amount(self,model,obj):
		amt=0.0
		if model=='inspection.costing':
			for line in obj.inspection_line:
				if line.quote_calculator:
					amt += line.final_quote_value if line.final_quote_value else line.estimated_contract_cost
				else :
					amt += line.final_quote_value_basic if (line.campaign_disc_amnt or line.disc_amnt) else line.estimated_contract_cost
				
		if model=='sale.quotation':        
			for line in obj.quotation_line_id:
				if line.quote_calculator:
				    amt += line.final_quote_value if line.final_quote_value else line.estimated_contract_cost
				else :
				    amt += line.final_quote_value_basic if (line.campaign_disc_amnt or line.disc_amnt) else line.estimated_contract_cost
		if model=='sale.contract':
			if obj.gst_contract == True:
				for line in obj.contract_line_id12:
					if line.quote_calculator:
					    amt += line.final_quote_value if line.final_quote_value else line.estimated_contract_cost
					else :
					    amt += line.final_quote_value_basic if (line.campaign_disc_amnt or line.disc_amnt) else line.estimated_contract_cost
			else:
				for line in obj.contract_line_id:
					if line.quote_calculator:
					    amt += line.final_quote_value if line.final_quote_value else line.estimated_contract_cost
					else :
					    amt += line.final_quote_value_basic if (line.campaign_disc_amnt or line.disc_amnt) else line.estimated_contract_cost
		return amt
	

	def map_tax_model(self,model_name):	 	
		return {'inspection.costing':'inspection_costing_id',
				'sale.quotation':'sale_quotation_id',
				'sale.contract':'sale_contract_id',
		}.get(model_name,None)
	
	def delete_tax(self,cr,model,model_id,tax_ids):
		
		if model=='inspection.costing':
			cr.execute("select account_tax_id from tax where inspection_costing_id=%s" %(str(model_id)))
			current_ids=cr.fetchall()
			del_ids=[a[0] for a in current_ids]
			if del_ids:
				for j in del_ids:
					cr.execute("delete from tax where account_tax_id=%s and inspection_costing_id=%s" %(str(j),str(model_id)))
		if model=='sale.quotation':
			cr.execute("select account_tax_id from tax where sale_quotation_id=%s" %(str(model_id)))
			current_ids=cr.fetchall()
			del_ids=[a[0] for a in current_ids]
			if del_ids:
				for j in del_ids:
					cr.execute("delete from tax where account_tax_id=%s and sale_quotation_id=%s" %(str(j),str(model_id)))			
		if model=='sale.contract':

			cr.execute("select account_tax_id from tax where sale_contract_id=%s" %(str(model_id)))
			current_ids=cr.fetchall()
			del_ids=[a[0] for a in current_ids]
			if del_ids:
				for j in del_ids:
					cr.execute("delete from tax where account_tax_id=%s and sale_contract_id=%s" %(str(j),str(model_id)))
					
		return True

tax()


class gst_item_master(osv.osv):
	_name="gst.item.master"
	_columns={			
		'name':fields.char('Item Master',size=1000),
		'hsn_code':fields.char('HSN Code',size=20),
		'description':fields.char('Description',size=1000),
        'item_rate':fields.float('Rate',size=10),
		'scrap_product_category':fields.many2one('product.category.master','Product Category'),
		'active': fields.boolean('Status'),		
		'effective_date_from':fields.date('Effective Date From'),
		'new_tax_rate':fields.float('New Tax Rate',size=20),						
		}

	_defaults={
		'active':True,
		'item_rate':0.0,
	}

	def onchange_product_category(self,cr,uid,ids,scrap_product_category,context=None):
		data={}
		if scrap_product_category:
			for x in self.pool.get('product.category.master').browse(cr,uid,[scrap_product_category]):
				hsn_sac_code=x.hsn_sac_code
				data.update(
					{
						'hsn_code': hsn_sac_code
					})
		return {'value':data}

gst_item_master()


class product_category_master(osv.osv):
	_name="product.category.master"
	_columns={			
		'name':fields.char('Product Category',size=1000),
		'hsn_code':fields.char('HSN Code',size=20),
		'active': fields.boolean('Status'),								
		}

	_defaults={
		'active':True,
	}


product_category_master()

class goods_uom(osv.osv):
	_name='goods.uom'
	_order='name asc'
	_columns={
	'name':fields.char('Name',size=100),
	'description':fields.char('Name',size=1000),
	}
goods_uom()