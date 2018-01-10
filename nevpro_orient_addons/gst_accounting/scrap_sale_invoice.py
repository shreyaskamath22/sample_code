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
from datetime import date,datetime, timedelta


from calendar import monthrange
from osv import osv,fields
from datetime import date,datetime, timedelta
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
from dateutil.relativedelta import relativedelta
import calendar
import xmlrpclib
import re
import time
from base.res import res_partner
from datetime import datetime
import decimal_precision as dp
import os
import sys
from lxml import etree
from openerp.osv.orm import setup_modifiers
from tools.translate import _

class invoice_adhoc_master(osv.osv):
	_inherit='invoice.adhoc.master'
	_columns ={

		#'invoice_type':fields.char('Invoice Type',size=100),
		'description':fields.char('Description',size=100),
		'invoice_line_scrap_sale':fields.one2many('invoice.adhoc','invoice_adhoc_scrap_id','invoice scrap sale'),
	}

	_defaults={
		'status':'open',
	}

	def onchange_partner_id(self,cr,uid,ids,partner_id,context=None):
		value={}
		if partner_id:
			for x in self.pool.get('res.partner').browse(cr,uid,[partner_id]):
				cust_name=x.name
				value['cust_name']=cust_name
		return {'value':value}

	def view_scrap_sale_invoice(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			models_data=self.pool.get('ir.model.data')
			form_view=models_data.get_object_reference(cr, uid, 'gst_accounting', 'scrap_sale_invoice_adhoc_id')
			return {
						'type': 'ir.actions.act_window',
						'name':'Scrap Sale Invoice',
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'invoice.adhoc.master',
						'res_id':ids[0],
						'view_id':form_view[1],
						'target':'current',	
						'context': context,
						}

	def scrap_sale_invoice_process(self,cr,uid,ids,context=None):
		if not isinstance(ids,(list,tuple)):
			ids = [ids]
		lst=[]
		l1=[]
		l2=[]
		item_rate=[]
		myString = ''
		today_date = datetime.now().date()
		year = today_date.year
		year1 = today_date.strftime('%y')
		pms_lst = ""
		invoice_date = False
		pcof_key = invoice_id = temp_count = start_year = end_year = total_cp=''
		seq = count = 0
		pcof_key = self.pool.get('res.users').browse(cr,uid,uid).company_id.pcof_key
		invoice_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.invoice_id
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		if month > 3:
			start_year = year
			end_year = year+1
			year1 = int(year1)+1
		else:
			start_year = year-1
			end_year = year
			year1 = int(year1)
		financial_year =str(year1-1)+str(year1) 
		financial_start_date = str(start_year)+'-04-01'
		financial_end_date = str(end_year)+'-03-31'
		seq_start=1	
		if pcof_key and invoice_id:
			cr.execute("select cast(count(id) as integer) from invoice_adhoc_master where invoice_number is not null and invoice_date>='2017-07-01' and invoice_number ilike '%GT%' and import_flag =False and invoice_number not ilike '%/%' and invoice_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' and invoice_number_ncs is null");
			temp_count=cr.fetchone()
			if temp_count[0]:
				count= temp_count[0]
			seq=int(count+seq_start)
			seq_id = pcof_key +invoice_id +str(financial_year) +str(seq).zfill(5)
			existing_invoice_number = self.pool.get('invoice.adhoc.master').search(cr,uid,[('invoice_number','=',seq_id)])
			if existing_invoice_number:
				seq_id = pcof_key +invoice_id +str(financial_year) +str(seq+1).zfill(5)
		inv_data = self.browse(cr,uid,ids[0])
		if inv_data.invoice_line_scrap_sale==[]:
			raise osv.except_osv(('Alert'),('No Invoice Lines to process the Invoice!'))
		for vals in inv_data.invoice_line_scrap_sale:
			if vals.qty==False:
				raise osv.except_osv(('Alert'),('Please Enter Qty!'))
			if vals.rate==False:
				raise osv.except_osv(('Alert'),('Please Enter Rate!'))
		for rec in self.browse(cr,uid,ids):
			cgst_rate = '0.00%'
			cgst_amt = 0.00
			sgst_rate = '0.00%'
			sgst_amt = 0.00
			igst_rate = '0.00%'
			igst_amt = 0.00
			cess_rate = '0.00%'
			cess_amt = 0.00
			amount_new=0.0
			basic_amount = 0.0
			total_tax_amt = 0.0
			grand_total_amount = 0.0
			account_tax_obj = self.pool.get('account.tax')
			today_date = datetime.now().date()
			gst_select_taxes = ['cgst','sgst','utgst','igst','cess']
			gst_taxes = account_tax_obj.search(cr,uid,[('description','=','gst'),('select_tax_type','in',gst_select_taxes)])
			if not gst_taxes:
				raise osv.except_osv(('Alert!'),('GST taxes are not configured !'))
			if rec.invoice_type=='Scrap Sale Invoice':
				if rec.invoice_line_scrap_sale:
					for i in rec.invoice_line_scrap_sale:
						item_rate.append(i.item_master.item_rate)
			item_rate=list(set(item_rate))
			if len(item_rate)>1:
				raise osv.except_osv(('Alert!'),('Kindly select item master of same rates !'))
			if not rec.branch_id.state_id or not rec.partner_id.state_id:
				raise osv.except_osv(('Alert'),("State not defined for either current branch or Supplier!"))
			if rec.invoice_type=='Scrap Sale Invoice':
				if rec.invoice_line_scrap_sale:					
					for i in rec.invoice_line_scrap_sale:
						ln_amount=i.rate*i.qty
						if round(ln_amount,2)!=round(i.total,2):
							raise osv.except_osv(('Alert'),("Total amount in Invoice line is not as per Qty * Rate!"))
						if round(ln_amount,2)!=round(i.amount,2):
							raise osv.except_osv(('Alert'),("Taxable value in Invoice line is not as per Qty * Rate!"))
						if rec.branch_id.state_id.id==rec.partner_id.state_id.id:
							rate=i.item_master.item_rate/2
							cgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','cgst')])
							cgst_data = account_tax_obj.browse(cr,uid,cgst_id[0])
							if cgst_data.effective_from_date and cgst_data.effective_to_date:
								if str(today_date) >= cgst_data.effective_from_date and str(today_date) <= cgst_data.effective_to_date:
									cgst_percent = rate
									cgst_rate = str(cgst_percent)+'%'
									cgst_amt = round((i.total*cgst_percent)/100,2)
							else:
								raise osv.except_osv(('Alert'),("CGST tax not configured!"))
									
							sgst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','sgst')])
							st_data = account_tax_obj.browse(cr,uid,sgst_id[0])
							if st_data.effective_from_date and st_data.effective_to_date:
								if str(today_date) >= st_data.effective_from_date and str(today_date) <= st_data.effective_to_date:
									sgst_percent = rate
									sgst_rate = str(sgst_percent)+'%'
									sgst_amt = round((i.total*sgst_percent)/100,2)
							else:
								raise osv.except_osv(('Alert'),("SGST tax not configured!"))
						else:
							rate=i.item_master.item_rate
							igst_id = account_tax_obj.search(cr,uid,[('select_tax_type','=','igst')])
							igst_data = account_tax_obj.browse(cr,uid,igst_id[0])
							if igst_data.effective_from_date and igst_data.effective_to_date:
								if str(today_date) >= igst_data.effective_from_date and str(today_date) <= igst_data.effective_to_date:								
									igst_percent = rate
									igst_rate = str(igst_percent)+'%'
									igst_amt = round((i.total*igst_percent)/100,2)
							else:
								raise osv.except_osv(('Alert'),("IGST tax not configured!"))
						
							# case: if both states are different
							
						self.pool.get('invoice.adhoc').write(cr,uid,i.id,
							{
								'invoice_adhoc_scrap_id':rec.id,
								'discount': 0,
								'amount':i.total,
								'cgst_rate': cgst_rate,
								'cgst_amt': cgst_amt,
								'sgst_rate': sgst_rate,
								'sgst_amt': sgst_amt,
								'igst_rate': igst_rate,
								'igst_amt': igst_amt,
								'cess_rate': cess_rate,
								'cess_amt': cess_amt,
							})
						basic_amount = basic_amount + i.total
						total_tax_amt = total_tax_amt+ cgst_amt+sgst_amt +igst_amt
			grand_total_amount = basic_amount + total_tax_amt
			inv_vals = {
						'total_tax': total_tax_amt,
						'pending_amount':round(grand_total_amount),
						'basic_amount': round(basic_amount),
						'total_amount':round(basic_amount),
						'grand_total_amount':round(grand_total_amount)
			
			      }
		self.write(cr,uid,inv_data.id,inv_vals)	 
		for res in self.browse(cr,uid,ids):			
			self.pool.get('invoice.tax.rate').add_scrap_sale_invoice_tax(cr,uid,res.id)
			temp_amount = tax_rate = tax_rate_amount = 0.0
			if res.tax_one2many:
				for amt in res.tax_one2many:
					tax_rate_amount +=amt.amount
					tax_rate += float(amt.tax_rate)
			net_amount = res.basic_amount + res.total_tax
			self.write(cr,uid,res.id,{'total_tax':res.total_tax,'tax_rate':str(tax_rate)})
			if res.adv_receipt_amount == 0:
					net_amount_payable = net_amount
					self.write(cr,uid,res.id,{'net_amount_payable': round(net_amount_payable)})
			if res.gst_invoice == False:
				self.write(cr,uid,res.id,{'gst_invoice':True})
			self.write(cr,uid,res.id,{'invoice_number':seq_id,'invoice_date':datetime.now().date()})
		models_data=self.pool.get('ir.model.data')
		form_view=models_data.get_object_reference(cr, uid, 'gst_accounting', 'scrap_sale_invoice_adhoc_id')
		return {	
					'type': 'ir.actions.act_window',
					'name': 'Scrap Sale Invoice',
					'view_mode': 'form',
					'view_type': 'form',
					'view_id': form_view[1],
					'res_id': ids[0],
					'res_model': 'invoice.adhoc.master',
					'target': 'current',
				}

	def scrap_receipt(self, cr, uid, ids, vals, context=None):
		adhoc_obj = self.pool.get('invoice.adhoc')
		result = account_security = account_itds = ''
		account_id = False
		for res in self.browse(cr,uid,ids):
				invoice_number = res.invoice_number
				itds_total = ''
				itds_rate = 0.0
				srch =[]
				if res.check_process_invoice == False:
					self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,
						{
							'invoice_id_receipt':'',
							'check_invoice':False,
							'partial_payment_amount':round(res.pending_amount),
						})
				if invoice_number == False:
					raise osv.except_osv(('Alert'),('There is no Invoice Number for this record.'))
				if res.tax_rate == '0.0':
					raise osv.except_osv(('Alert'),('There is no tax_rate for this record.')) 
				if res.tax_rate:
					acc_query="select id from account_account where account_selection = 'against_ref' and name ilike '%Scrap Sale%' "
					cr.execute(acc_query)
					srch=cr.fetchone()
				else:
					raise osv.except_osv(('Alert'),('There is no tax_rate for this record.')) 
				srch1 = self.pool.get('account.account').search(cr,uid,[('account_selection','=','itds_receipt')])
				srch2 = self.pool.get('account.account').search(cr,uid,[('account_selection','=','security_deposit')])
				if srch:
					srch_id=srch[0] if isinstance(srch,(list,tuple)) else srch
					acc_id =self.pool.get('account.account').browse(cr,uid,srch_id)
					account_id = acc_id.id
				for acc_id in self.pool.get('account.account').browse(cr,uid,srch2):
					account_security = acc_id.id
				for acc_id in self.pool.get('account.account').browse(cr,uid,srch1):
					account_itds = acc_id.id
					itds_rate = acc_id.itds_rate if acc_id.itds_rate else 0.0
				adhoc_ids1 = adhoc_obj.search(cr,uid,[('invoice_adhoc_scrap_id','=',res.id)])
				if adhoc_ids1:
					adhoc_ids = adhoc_ids1
					adhoc_data = adhoc_obj.browse(cr,uid,adhoc_ids[0])
					# address_id = adhoc_data.location.partner_address.id
				
				create_id = self.pool.get('account.sales.receipts').create(cr,uid,
					{
						'customer_name':res.partner_id.id,
						'customer_id_invisible':res.partner_id.ou_id,
						'acc_status':'against_ref',
						'chek_receipt':True,
						'invoice_number':res.invoice_number,
						'account_select_boolean':True,
						# 'billing_location': address_id
					})
				result = self.pool.get('account.sales.receipts.line').create(cr,uid,
					{
						'customer_name':res.partner_id.id,
						'receipt_id':create_id,
						'acc_status':'against_ref',
						'account_id':account_id,
						'type':'credit',
						'credit_amount':res.pending_amount,
						'check_against_ref_status':False
					})
				for adhoc_id in adhoc_ids:
					self.pool.get('invoice.adhoc.receipts').create(cr,uid,
						{
							'sales_receipt_id': create_id,
							'invoice_adhoc_id': adhoc_id,
						})
				if itds_rate: 
					itds_rate_per = itds_rate * 0.01
					itds_total = res.pending_amount * itds_rate_per
				else:
					raise osv.except_osv(('Alert'),('Please give Itds Rate'))
				self.pool.get('invoice.adhoc.master').write(cr,uid,res.id,
					{
						'invoice_id_receipt':result,
						'check_invoice':True
					})
				self.write(cr,uid,res.id,{'check_against_reference':True})
				return {
					'name':'Sales Receipts',
					'view_mode': 'form',
					'view_id': False,
					'view_type': 'form',
					'res_model': 'account.sales.receipts',
					'res_id':create_id,
					'type': 'ir.actions.act_window',
					'target': 'current',
					'domain': '[]',
					'context': context,
					}

invoice_adhoc_master()

class invoice_adhoc(osv.osv):
	_inherit='invoice.adhoc'
	_columns={
		'description':fields.char('Description',size=100),
		'item_master':fields.many2one('gst.item.master','Item Master'),
		'invoice_adhoc_scrap_id':fields.many2one('invoice.adhoc.master','Scrap Sale Invoice'),
		'scrap_unit':fields.selection([('nos','Nos')],'Unit'),
	}
	_defaults={
		'description': 'Scrap Sale',
		'scrap_unit':'nos',
	}

	def onchange_scrap_adhoc_area(self, cr, uid, ids, qty, rate, context=None):
		data = {}
		if qty and rate:
			rateqty = rate*qty
			total = rateqty
			data.update(
				{
					'total': round(total),
					'amount': round(total)
				})
		return {'value':data}

	def onchange_item_master(self, cr, uid, ids, item_master, context=None):
		data={}
		if item_master:
			for x in self.pool.get('gst.item.master').browse(cr,uid,[item_master]):
				hsn_code=x.hsn_code
				data.update(
					{
						'hsn_code': hsn_code
					})
		return {'value':data}

invoice_adhoc()

class invoice_search_master(osv.osv):

	_inherit="invoice.search.master"

	def search_scrap_sale_invoice(self,cr,uid,ids,context=None):
		for temp in self.browse(cr,uid,ids):
			self.write(cr,uid,ids,{'select_all':False})#18Nov2015
			list_id = []
			Sql_Str = ''
			customer_id =''
			try:
				
				if temp.cust_name :
					Sql_Str = Sql_Str + " and IAM.partner_id =" +str(temp.cust_name.id) +""
				if temp.customer_id != False:#a
					Sql_Str = Sql_Str + " and IAM.customer_id ilike '" +"%"+ str(temp.customer_id) + "%'"
				if temp.invoice_number != False:
					Sql_Str = Sql_Str + " and IAM.invoice_number ilike '" +"%"+ str(temp.invoice_number) + "%'"
				if temp.state != False:
					Sql_Str = Sql_Str + " and IAM.status ilike '" +"%"+ str(temp.state) + "%'"
				if temp.date_from != False:
					Sql_Str = Sql_Str + " and IAM.invoice_date >= '" +str(temp.date_from) + "'"
				if temp.date_to != False:
					Sql_Str = Sql_Str + " and IAM.invoice_date <= '" +str(temp.date_to) + "'"

				search_eff = self.pool.get('sync.invoice.adhoc.master').search(cr,uid,[('effective_date','!=',None)])
				a = self.pool.get('sync.invoice.adhoc.master').browse(cr,uid,search_eff)
				for each in a:
					search_eff_date = each.effective_date	
				Sql_Str = Sql_Str + " and (IAM.invoice_date >= '2017-02-28' or IAM.invoice_date is null) "

				Main_Str = "select distinct(IAM.id) from invoice_adhoc_master IAM,invoice_adhoc IA where IAM.id = IA.invoice_adhoc_scrap_id " 

				Main_Str2 = Main_Str + Sql_Str

				update_command = "update invoice_adhoc_master set  search_id ="+str(temp.id)+" ,multiple_check=False where id in ("+Main_Str2+") "

				cr.execute(update_command)
				cr.commit()

				update_command = "update invoice_adhoc_master set  search_id =Null ,multiple_check=False where id not in ("+Main_Str2+")"		

				cr.execute(update_command)
				cr.commit()
				
			except Exception  as exc:
				cr.rollback()
				if exc.__class__.__name__ == 'TransactionRollbackError':
					pass
				else:
					raise


	def clear_invoice(self,cr,uid,ids,context=None):
		for k in self.browse(cr,uid,ids):
			self.write(cr,uid,k.id,{
								'cust_name':None,
								'customer_id':None,
								'state':None,
								'invoice_number':None,
								'date_from':None,
								'date_to':None,
								'select_all':False,
								'order_no':None,
								'delivery_order_no':None,
								'delivery_note_date':None,
								'product_id':None
								})

			for req in k.search_invoice_line:
				self.pool.get('invoice.adhoc.master').write(cr,uid,req.id,{'search_id':None})
		return True

	
	def create_scrap_sale_invoice(self,cr,uid,ids,context=None):
		models_data=self.pool.get('ir.model.data')
		vals={}
		vals.update({'invoice_type':'Scrap Sale Invoice','description':'Scrap Sale','tax_rate':'18.0'})
		create_id=self.pool.get('invoice.adhoc.master').create(cr,uid,vals,context=context)
		form_view=models_data.get_object_reference(cr, uid, 'gst_accounting', 'scrap_sale_invoice_adhoc_id')
		res = self.browse(cr,uid,ids[0])
		return {
					'type': 'ir.actions.act_window',
					'name':'Scrap Sale Invoice',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'invoice.adhoc.master',
					'res_id':int(create_id),
					'view_id':form_view[1],
					'target':'current',
					'context': {},
				}




invoice_search_master()


class invoice_tax_rate(osv.osv):
	_inherit = 'invoice.tax.rate'

	def add_scrap_sale_invoice_tax(self,cr,uid,model_id,use_date=None):
		total_tax=val1=tax_rate=rate=0.0
		todays_date=use_date if use_date else datetime.now().date().strftime("%Y-%m-%d")
		model_id=model_id if isinstance(model_id,(int,long)) else model_id[0]
		for order in self.pool.get('invoice.adhoc.master').browse(cr,uid,[model_id]):
			if not order.branch_id.state_id or not order.partner_id.state_id:
				raise osv.except_osv(('Alert'),("State not defined for either current branch or Supplier!"))
			if order.invoice_type=='Scrap Sale Invoice':
				for line in order.invoice_line_scrap_sale:
					val1 += line.total
					if order.branch_id.state_id.id== order.partner_id.state_id.id:
						rate=line.item_master.item_rate/2
					else:
						rate=line.item_master.item_rate
			acc_tax_ids=[]
			tax_ids=[]
			acc_id=self.search(cr,uid,[('invoice_id','=',order.id)])
			if acc_id:
				for acc_ids in self.browse(cr,uid,acc_id):
				     acc_tax_ids.append(acc_ids.account_tax_id.id)
			tax_ids= self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',todays_date),('effective_to_date','>',todays_date),('select_tax_type','!=',False)])
			GST_val=self.pool.get('account.account').search(cr,uid,[('name','=','GST')])
			if GST_val:
				Inter_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','igst')])[0]
				union_state_id=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','utgst')])[0]
				state_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','sgst')])[0]
				central_gst=self.pool.get('account.tax').search(cr,uid,[('description','=','gst'),('select_tax_type','=','cgst')])[0]
			if order.branch_id.state_id.id== order.partner_id.state_id.id:
				if Inter_state_id in tax_ids:
					tax_ids.remove(Inter_state_id)
				if union_state_id in tax_ids:
					tax_ids.remove(union_state_id)
			else:
				if state_gst in tax_ids:
					tax_ids.remove(state_gst)
				if central_gst in tax_ids:
					tax_ids.remove(central_gst)
				if union_state_id in tax_ids:
					tax_ids.remove(union_state_id)
			# tax_ids_1=self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',todays_date),('effective_to_date','>',todays_date),('description','=','gst'),('select_tax_type','=','sgst')])[0]
			# tax_ids.append(tax_ids_1)
			# tax_ids_2=self.pool.get('account.tax').search(cr,uid,[('effective_from_date','<=',todays_date),('effective_to_date','>',todays_date),('description','=','gst'),('select_tax_type','=','cgst')])[0]
			# tax_ids.append(tax_ids_2)
			for rec in self.pool.get('account.tax').browse(cr,uid,tax_ids):
				tax =1
				# current_tax_amount,tax=self.recr_amount(rec,val1,todays_date,tax)
				current_tax_amount,tax=(val1*rate/100),rate
				acc_id=self.pool.get('account.account').search(cr,uid,[('account_tax_many2one','=',rec.id)])
				if current_tax_amount > 0:
					cr.execute('insert into invoice_tax_rate(name,amount,invoice_id,account_tax_id,tax_rate,account_id)values(%s,%s,%s,%s,%s,%s)' %("'"+str(rec.name)+"'",str(round(current_tax_amount,2)),str(model_id),str(rec.id),str(tax),str(acc_id[0])))
			for amt in order.tax_one2many:
				total_tax+=amt.amount
				tax_rate += float(amt.tax_rate)
			cr.execute("update invoice_adhoc_master set grand_total_amount=%s,tax_rate=%s where id=%s" %(str(round(val1+total_tax)),str(tax_rate),str(order.id)))
		return True

invoice_tax_rate()