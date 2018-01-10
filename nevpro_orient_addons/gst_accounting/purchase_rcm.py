from osv import osv,fields
from datetime import date,datetime, timedelta
from dateutil.relativedelta import *
from dateutil.relativedelta import relativedelta
import re

class account_purchase_receipts(osv.osv): 
	_name = 'account.purchase.receipts'
	_rec_name = 'receipt_no'
	_order = 'receipt_no desc'
	
	def _get_company(self, cr, uid, context=None):
	### get current comany name
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id
	
	_columns = {
		'customer_name':fields.many2one('res.partner','Supplier Name'),
		'customer_id':fields.related('customer_name','ou_id',type='char',relation='res.partner',string='Supplier ID'),
		'customer_id_invisible':fields.char('Customer ID Invisible',size=124),
		'receipt_no':fields.char('Voucher Number',size=124),
		'receipt_date':fields.date('Voucher Date'),
		'type':fields.selection([
				('debit','Debit(Dr.)'),
				('credit','Credit(Cr.)')],'Type'),
		'account_id':fields.many2one('account.account','Account Name'),
		'state': fields.selection([('draft','Draft'),('done','Done'),('finish','Finish'),('cancel','Cancelled')],'Status'),
		'narration':fields.text('Narration'),
		# 'cancel_boolean':fields.boolean('Cancel'), #dee voucher cancellation
		# 'cancel_reason':fields.char('Reason for Cancel',size=300), #dee voucher cancellation
		# 'cancel_date':fields.date('Cancel Date'), #dee voucher cancellation
		'receipt_amount':fields.float('Receipt Amount'),
		'company_id':fields.many2one('res.company','Company'),
		'from_date':fields.function(lambda *a,**k:{}, method=True, type='date',string="Date From"),
		'to_date':fields.function(lambda *a,**k:{}, method=True, type='date',string="Date To"),
		'purchase_receipt_one2many':fields.one2many('account.purchase.receipts.line','purchase_receipt_id','Purchase Receipt'),
		'voucher_type':fields.char('Voucher Type',size=124),				
		'receipt_type':fields.selection([
				('purchase_receipts','Purchase Receipts'),
				],'Receipt Type'),
		'credit_amount': fields.float('Credit Amount'),
		'debit_amount': fields.float('Debit Amount'),
		'expense_flag':fields.boolean('Expense Flag'),
	}

	_defaults = {
			'state':'draft',
			'receipt_type':'purchase_receipts',
			'company_id':_get_company,
		}

	def customer_name_change(self, cr, uid, ids, customer_name, context=None):
		#function to get supplier id on onchange of supplier name 
		v = {}
		if customer_name:
			srch = self.pool.get('res.partner').search(cr,uid,[('id','=',customer_name)])
			if srch:
				for partner in self.pool.get('res.partner').browse(cr,uid,srch):
					ou_id = partner.ou_id
				v['customer_id'] = ou_id
				v['customer_id_invisible'] = ou_id
		if not	customer_name:
			v['customer_id']=None
			v['customer_id_invisible'] = None

		return {'value':v}

	def add_info(self, cr, uid, ids, context=None):
		#function to add ledgers in the purchase voucher line
		temp = 0.0
		tax_rate = freight_input_rate = 0.0
		check_freight=igst_check=False
		auto_credit_cal = 0.0
		for res in self.browse(cr,uid,ids):
			account_id = res.account_id.id
			account_name = res.account_id.name
			acc_selection = res.account_id.account_selection
			customer_name=res.customer_name.id
			customer_name_char = res.customer_name.name
			customer_state = res.customer_name.state_id.id
			branch_state=res.company_id.state_id.id
			hsn_code = res.account_id.hsn_sac_code
			code = str(res.account_id.code)
			rate = str(res.account_id.rcm_rate)
			types = res.type
			if acc_selection in ('cash','iob_one','iob_two'):
				raise osv.except_osv(('Alert'),('You cannot add Cash/Bank Ledger in Purchase Voucher!'))
			if customer_name:
				if not res.customer_name.state_id:
					raise osv.except_osv(('Alert'),('Kindly update the State of Supplier!'))
				if customer_state!=branch_state:
					igst_check=True
			if acc_selection!='expenses' and rate!='0.0':
				tax_rate = self.pool.get('account.account').browse(cr,uid,account_id).rcm_rate
			if 'Freight Inward-GST' in account_name:
				freight_input_rate = '5'
			if 'Freight Outward-GST' in account_name:
				freight_input_rate = '5'
			if code in ('frin12','frin18','frout12','frout18') and res.type=='debit':
				freight_input_rate = self.pool.get('account.account').browse(cr,uid,account_id).rcm_rate
			auto_credit_cal = auto_debit_cal = auto_credit_total = auto_debit_total = itds_total = temp=0.0
			account_id1=res.account_id
			if res.purchase_receipt_one2many and res.customer_name.gst_no==False or res.customer_name.gst_no=='Unregistered':
				for ln in res.purchase_receipt_one2many:
					if 'Freight Inward-GST' in ln.account_id.name:
						check_freight=True
					if 'Freight Outward-GST' in ln.account_id.name:
						check_freight=True
					if ('Freight Inward' in ln.account_id.name) and ln.account_id.rcm_rate in ('12.0','18.0'):
						check_freight=True
					if ('Freight Outward' in ln.account_id.name) and ln.account_id.rcm_rate in ('12.0','18.0'):
						check_freight=True
			# if check_freight and freight_input_rate not in ('12.0','18.0'):
			# 	if igst_check==False:
			# 		if res.account_id.name in ('IGST - Input') and res.account_id.account_selection=='st_input':
			# 			raise osv.except_osv(('Alert'),("You cannot add 'IGST - Input' Ledger"))
			# if igst_check==False:
			# 	if res.account_id.name in ('IGST - Input') and res.account_id.account_selection=='st_input':
			# 		raise osv.except_osv(('Alert'),("You cannot add 'IGST - Input' Ledger"))
			# if igst_check:
			# 	if res.account_id.name in ('CGST - Input','SGST - Input','UTGST - Input') and res.account_id.account_selection=='st_input':
			# 		raise osv.except_osv(('Alert'),("You cannot add '%s' Ledger!")%(res.account_id.name))
			if check_freight and freight_input_rate=='5':
				# if res.type=='debit' and res.account_id.name in ('IGST - Input') and res.account_id.account_selection=='st_input':
				# 	raise osv.except_osv(('Alert'),("Kindly Update the GST No of Supplier!"))
				if res.type=='debit' and res.account_id.name in ('CGST - Input','SGST - Input','IGST - Input') and res.account_id.account_selection=='st_input':
					raise osv.except_osv(('Alert'),("You cannot add '%s' Ledger!")%(res.account_id.name))
			for i in res.purchase_receipt_one2many:
				if account_id1.id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

				if not account_id:
					raise osv.except_osv(('Alert'),('Please select Account Name.'))
				
				if not types:
					raise osv.except_osv(('Alert'),('Please select Type.'))
				if i.type == 'debit':
					auto_credit_cal += i.debit_amount
			if res.customer_name.gst_type_supplier:
				if res.customer_name.gst_type_supplier.name=='Composition':
					tax_rate=0.0
					freight_input_rate=0.0
			self.pool.get('account.purchase.receipts.line').create(cr,uid,{
					'purchase_receipt_id':res.id,
					'account_id':account_id,
					'customer_name':customer_name,
					'debit_amount':temp,
					# 'credit_amount':auto_credit_cal,
					'type':types,
					'tax_rate':tax_rate,
					'freight_input_rate':freight_input_rate,
					'igst_check':igst_check,
				})
		self.write(cr,uid,res.id,{'account_id':None,'type':None})						
		return True

	def wizard_id_write(self, cr, uid, ids,  context=None):
	### update wizard id
		for res in self.browse(cr,uid,ids):
			for line in res.purchase_receipt_one2many:
				cr.execute("update account_purchase_receipts_line set wizard_id = %s where id=%s",(line.id,res.id))
				#self.pool.get('payment.line').write(cr,uid,line.id,{'wizard_id':line.id})
		return True

	def process(self,cr,uid,ids,context=None):
		#Function to process Purchase voucher
		receipt_date = ''
		account_purchase_receipts_line_obj = self.pool.get('account.purchase.receipts.line')
		account_legal_profession_charges_obj =self.pool.get('account.legal.profession.charges')
		o= self.browse(cr,uid,ids[0])
		main_id = o.id
		legal_bool=expense_bool=freight_bool=tax_rate=py_date=freight_flag=igst_check=False
		cr_total = dr_total = total = iob_total = legal_debit_amount =total_wizard_amount=freight_rate=0.0
		post = legal_list = freight_list_new1=expense_list_new1=[]
		freight_amount=0.0
		for rec in self.browse(cr,uid,ids):
			if not rec.customer_name.gst_type_supplier:
				raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
			if rec.customer_name.gst_type_supplier and (rec.customer_name.gst_no==False or rec.customer_name.gst_no=='' or rec.customer_name.gst_no==None):
				raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
			if rec.customer_name.gst_no==False or rec.customer_name.gst_no=='' or rec.customer_name.gst_no==None:
				raise osv.except_osv(('Alert!'),("Select proper Registration type / GST No for Supplier!"))
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
			if rec.receipt_date:
				check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
				if check_bool:
					if rec.receipt_date != str(today_date):
						raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
				py_date = str(today_date + relativedelta(days=-5))
				if rec.receipt_date < str(py_date) or rec.receipt_date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Receipt Date 5 days earlier from current date.'))
				receipt_date=rec.receipt_date	
			else:				
				receipt_date=datetime.now().date()
		search_lines = account_purchase_receipts_line_obj.search(cr,uid,[('purchase_receipt_id','=',main_id)])
		for browse_lines in account_purchase_receipts_line_obj.browse(cr,uid,search_lines):
			if 'Round-off' not in browse_lines.account_id.name:
				if browse_lines.type == 'credit':
					if browse_lines.credit_amount <= 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				elif browse_lines.type == 'debit':
					if browse_lines.debit_amount <= 0.0:
						raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
				else:
					raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(browse_lines.account_id.name))))
			elif 'Round-off' in browse_lines.account_id.name:
				if browse_lines.type == 'credit':
					if browse_lines.credit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
				elif browse_lines.type == 'debit':
					if browse_lines.debit_amount == 0.0:
						raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
				else:
					raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(browse_lines.account_id.name))))
			cr_total += browse_lines.credit_amount
			dr_total += browse_lines.debit_amount
			account_id = browse_lines.account_id.id
			temp = tuple([account_id])
			post.append(temp)
			for i in range(0,len(post)):
				for j in range(i+1,len(post)):
					if post[i][0]==post[j][0]:
						raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

		if round(dr_total,2) != round(cr_total,2):
			raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

		if dr_total == 0.0 or cr_total == 0.0:
			raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
		for browse_lines in account_purchase_receipts_line_obj.browse(cr,uid,search_lines):
			account_name = browse_lines.account_id.name
			hsn_code = browse_lines.account_id.hsn_sac_code
			acc_selection=browse_lines.account_id.account_selection
			goods_applicable=browse_lines.account_id.goods_applicable
			rate = str(browse_lines.account_id.rcm_rate)
			if browse_lines.account_id.name=='Freight Inward-GST' and browse_lines.type=='debit':
				freight_flag=True
				igst_check=browse_lines.igst_check
				freight_amount=browse_lines.debit_amount
				rate = str(browse_lines.account_id.rcm_rate)
			if browse_lines.account_id.name=='Freight Outward-GST' and browse_lines.type=='debit':
				freight_flag=True
				igst_check=browse_lines.igst_check
				freight_amount=browse_lines.debit_amount
				rate = str(browse_lines.account_id.rcm_rate)
			if 'Freight Inward' in browse_lines.account_id.name and browse_lines.type=='debit' and rate in ('12.0','18.0'):
				freight_flag=True
				igst_check=browse_lines.igst_check
				freight_amount=browse_lines.debit_amount
				rate = str(browse_lines.account_id.rcm_rate)
			if 'Freight Outward' in browse_lines.account_id.name and browse_lines.type=='debit' and rate in ('12.0','18.0'):
				freight_flag=True
				igst_check=browse_lines.igst_check
				freight_amount=browse_lines.debit_amount
				rate = str(browse_lines.account_id.rcm_rate)
			if (rate!='0.0' or hsn_code!=False) and browse_lines.type == 'debit' and acc_selection!='expenses' and freight_flag==False:
				if browse_lines.legal_profession_one2many==[]:
					raise osv.except_osv(('Alert'),("No Bill details to proceed aginst '%s' Ledger")%(account_name))
				else:
					legal_debit_amount=browse_lines.debit_amount
					igst_check=browse_lines.igst_check
					tax_rate=browse_lines.tax_rate
					legal_bool=True
					legal_list=[]
					total_cgst=total_sgst=total_wizard_amount=0.0
					for x in browse_lines.legal_profession_one2many:
						total_cgst=total_cgst+x.cgst_amount
						total_sgst=total_sgst+x.sgst_amount
						# if o.customer_name.gst_no==False or o.customer_name.gst_no=='Unregistered':
						total_wizard_amount=total_wizard_amount+x.bill_value
						# else:
						# 	total_wizard_amount=total_wizard_amount+x.total_amount
						if x.rate!=0.0:
							legal_list.append(int(x.id))
				if round(legal_debit_amount,2)!=round(total_wizard_amount,2):
					raise osv.except_osv(('Alert'),('%s Ledger wizard Amount is not equal to Debit Amount!')%(account_name))
			if browse_lines.type == 'debit' and acc_selection=='expenses' and goods_applicable!=True:
				if browse_lines.purchase_expense_one2many==[]:
					raise osv.except_osv(('Alert'),("No Bill details to proceed aginst '%s' Ledger")%(account_name))
				else:
					legal_debit_amount=browse_lines.debit_amount
					igst_check=browse_lines.igst_check
					tax_rate=browse_lines.tax_rate
					expense_bool=True
					expense_list=[]
					total_cgst=total_sgst=total_igst=total_wizard_amount=0.0
					for x in browse_lines.purchase_expense_one2many:
						if not x.gst_item_master.id:
							# print"please select Item"
							raise osv.except_osv(('Alert'),("Please Select Item"))

						total_cgst=total_cgst+x.cgst_amount
						total_sgst=total_sgst+x.sgst_amount
						total_igst=total_igst+x.igst_amount
						# if o.customer_name.gst_no==False or o.customer_name.gst_no=='Unregistered':
						total_wizard_amount=total_wizard_amount+x.bill_value
						# else:
						# 	total_wizard_amount=total_wizard_amount+x.total_amount
						if x.rate!=0.0:
							expense_list.append(int(x.id))
				expense_list_new1=expense_list
				if round(legal_debit_amount,2)!=round(total_wizard_amount,2):
					raise osv.except_osv(('Alert'),('%s Ledger wizard Amount is not equal to Debit Amount!')%(account_name))
			if browse_lines.type == 'debit' and acc_selection=='expenses' and goods_applicable==True:
				if browse_lines.goods_purchase_expense_one2many==[]:
					raise osv.except_osv(('Alert'),("No Bill details to proceed aginst '%s' Ledger")%(account_name))
				else:
					legal_debit_amount=browse_lines.debit_amount
					igst_check=browse_lines.igst_check
					tax_rate=browse_lines.tax_rate
					expense_bool=True
					expense_list=[]
					total_cgst=total_sgst=total_igst=total_wizard_amount=0.0
					for x in browse_lines.goods_purchase_expense_one2many:
						if not x.gst_item_master.id:
							# print"please select Item"
							raise osv.except_osv(('Alert'),("Please Select Item"))

						total_cgst=total_cgst+x.cgst_amount
						total_sgst=total_sgst+x.sgst_amount
						total_igst=total_igst+x.igst_amount
						# if o.customer_name.gst_no==False or o.customer_name.gst_no=='Unregistered':
						total_wizard_amount=total_wizard_amount+x.bill_value
						# else:
						# 	total_wizard_amount=total_wizard_amount+x.total_amount
						if x.rate!=0.0:
							expense_list.append(int(x.id))
				expense_list_new1=expense_list
				if round(legal_debit_amount,2)!=round(total_wizard_amount,2):
					raise osv.except_osv(('Alert'),('%s Ledger wizard Amount is not equal to Debit Amount!')%(account_name))
			if browse_lines.type == 'debit' and freight_flag==True and acc_selection!='st_input' and freight_amount>750 and rate=='5.0':
				if browse_lines.purchase_freight_one2many==[]:
					raise osv.except_osv(('Alert'),("No Bill details to proceed aginst '%s' Ledger")%(account_name))
				else:
					freight_debit_amount=browse_lines.debit_amount
					tax_rate=browse_lines.tax_rate
					freight_bool=True
					freight_list_new=[]
					total_cgst=total_sgst=total_igst=total_wizard_amount=0.0
					for d in browse_lines.purchase_freight_one2many:
						total_cgst=total_cgst+d.cgst_tax_amount
						total_sgst=total_sgst+d.sgst_tax_amount
						total_igst=total_igst+d.igst_tax_amount
						total_wizard_amount=total_wizard_amount+d.bill_value
						if d.freight_input_rate:
							freight_rate=str(d.freight_input_rate)
							freight_list_new.append(d.id)
				freight_list_new1=freight_list_new
				if round(freight_debit_amount,2)!=round(total_wizard_amount,2):
					raise osv.except_osv(('Alert'),('Freight wizard Amount is not equal to Debit Amount!'))
			if browse_lines.type == 'debit' and freight_flag==True and acc_selection!='st_input' and rate in ('12.0','18.0'):
				if browse_lines.purchase_freight_one2many==[]:
					raise osv.except_osv(('Alert'),("No Bill details to proceed aginst '%s' Ledger")%(account_name))
				else:
					freight_debit_amount=browse_lines.debit_amount
					tax_rate=browse_lines.tax_rate
					freight_bool=True
					freight_list_new=[]
					total_cgst=total_sgst=total_igst=total_wizard_amount=0.0
					for d in browse_lines.purchase_freight_one2many:
						total_cgst=total_cgst+d.cgst_tax_amount
						total_sgst=total_sgst+d.sgst_tax_amount
						total_igst=total_igst+d.igst_tax_amount
						total_wizard_amount=total_wizard_amount+d.bill_value
						if d.freight_input_rate:
							freight_rate=str(d.freight_input_rate)
							freight_list_new.append(d.id)
				freight_list_new1=freight_list_new
				if round(freight_debit_amount,2)!=round(total_wizard_amount,2):
					raise osv.except_osv(('Alert'),('Freight wizard Amount is not equal to Debit Amount!'))
		for rec in self.browse(cr,uid,ids):
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
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
			financial_year = str(year1-1)+str(year1)
			financial_start_date = str(start_year)+'-04-01'
			financial_end_date = str(end_year)+'-03-31'
			company_id=self._get_company(cr,uid,context=None)
			if company_id:
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					if comp_id.purchase_receipt_seq_id:
						purchase_receipt_seq_id = comp_id.purchase_receipt_seq_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
				
			count = 0
			seq_start=1	
			if pcof_key and purchase_receipt_seq_id:
				cr.execute("select cast(count(id) as integer) from account_purchase_receipts where state not in ('draft') and receipt_no is not null  and receipt_date>='2017-07-01' and  receipt_date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + purchase_receipt_seq_id +  str(financial_year) +str(seq).zfill(5)
				existing_value_id = self.pool.get('account.purchase.receipts').search(cr,uid,[('receipt_no','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + purchase_receipt_seq_id +  str(financial_year) +str(seq+1).zfill(5)
			self.write(cr,uid,ids,{'receipt_no':value_id,'receipt_date': receipt_date,'state':'done','debit_amount':dr_total,'credit_amount':cr_total})		
			if legal_bool and legal_list!=[]:
				if rec.customer_name.gst_no==False or rec.customer_name.gst_no=='Unregistered':
					date = receipt_date
					search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
					for var in self.pool.get('account.period').browse(cr,uid,search_date):
						period_id = var.id
					srch_jour_bank = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Purchase Journal')])
					for jour_bank in self.pool.get('account.journal').browse(cr,uid,srch_jour_bank):
						journal_bank = jour_bank.id
					move = self.pool.get('account.move').create(cr,uid,{
								'journal_id':journal_bank,#Confirm from PCIL(JOURNAL ID)
								'state':'posted',
								'date':date,
								'name':value_id,
								'partner_id':rec.customer_name.id,
								'narration':rec.narration if rec.narration else '',
								'voucher_type':'Purchase Receipt',},context=context)
					for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
						for ln in rec.purchase_receipt_one2many:
							wizard_id=ln.wizard_id
							if wizard_id == 0:
								self.wizard_id_write(cr,uid,ids,context=context)
							# if igst_check:
							# 	raise osv.except_osv(('Alert'),("Kindly update the GST Number of Supplier!"))
							if ln.type=='debit' and ln.account_id.name in ('CGST - Input','SGST - Input','IGST - Input') and ln.account_id.account_selection=='st_input':
								raise osv.except_osv(('Alert'),("You cannot select '%s' Ledger as Supplier is not registered!")%(ln.account_id.name))
							self.pool.get('account.purchase.receipts.line').write(cr,uid,ln.id,{'state':'done'})
							if ln.debit_amount:
								self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
								'account_id':ln.account_id.id,
								'debit':ln.debit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_bank,
								'period_id':period_id,
								'partner_id':rec.customer_name.id,
								'date':date,
								'ref':value_id},context=context)
							if ln.credit_amount:
								self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
								'account_id':ln.account_id.id,
								'credit':ln.credit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_bank,
								'period_id':period_id,
								'partner_id':rec.customer_name.id,
								'date':date,
								'ref':value_id},context=context)
					create_id = self.pool.get('account.stat.adjustment').create(cr,uid,{
								'state':'done',
								'date':date,
								'debit_amount':total_cgst+total_sgst,
								'credit_amount':total_cgst+total_sgst,
								'total_credit':total_cgst+total_sgst,
								'total_debit':total_cgst+total_sgst,
								'customer_name':rec.customer_name.id,
								'narration':rec.narration if rec.narration else '',
								'voucher_type':'stat_adjustment',},context=context)
					if create_id:
						if company_id:
							for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
								if comp_id.stat_adjustment_seq_id:
									stat_adjustment_seq_id = comp_id.stat_adjustment_seq_id
								if comp_id.pcof_key:
									pcof_key = comp_id.pcof_key
							
						count = 0
						seq_start=1	
						if pcof_key and stat_adjustment_seq_id:
							cr.execute("select cast(count(id) as integer) from account_stat_adjustment where state not in ('draft') and stat_adjustment_number is not null  and date>='2017-07-01' and  date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
							temp_count=cr.fetchone()
							if temp_count[0]:
								count= temp_count[0]
							seq=int(count+seq_start)
							value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq).zfill(5)
							existing_value_id = self.pool.get('account.stat.adjustment').search(cr,uid,[('stat_adjustment_number','=',value_id)])
							if existing_value_id:
								value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq+1).zfill(5)
						self.pool.get('account.stat.adjustment').write(cr,uid,int(create_id),{'stat_adjustment_number':value_id,'date': receipt_date,'state':'done'})		
						search_tax_on_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','Tax on RCM')])
						if search_tax_on_rcm:
							debit_account_id=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
								'account_stat_adjustment_id':int(create_id),
								'debit_amount':total_cgst+total_sgst,
								'account_id':search_tax_on_rcm[0],
								'type':'debit',
								'state':'done',
								'tax_rate':tax_rate,
								'purchase_flag':True,
								})
							if legal_list:
								for legal in legal_list:
									self.pool.get('account.legal.profession.charges').write(cr,uid,int(legal),{'stat_legal_profession_id':int(debit_account_id)})
						search_cgst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','CGST - RCM')])
						if search_cgst_rcm:
							credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
								'account_stat_adjustment_id':int(create_id),
								'credit_amount':total_cgst,
								'account_id':search_cgst_rcm[0],
								'type':'credit',
								'state':'done',
								})
						search_sgst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','SGST - RCM')])
						if search_sgst_rcm:
							credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
								'account_stat_adjustment_id':int(create_id),
								'credit_amount':total_sgst,
								'account_id':search_sgst_rcm[0],
								'type':'credit',
								'state':'done',
								})
			if expense_bool and expense_list!=[]:
				if rec.customer_name.gst_no==False or rec.customer_name.gst_no=='Unregistered':
					date = receipt_date
					search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
					for var in self.pool.get('account.period').browse(cr,uid,search_date):
						period_id = var.id
					srch_jour_bank = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Purchase Journal')])
					for jour_bank in self.pool.get('account.journal').browse(cr,uid,srch_jour_bank):
						journal_bank = jour_bank.id
					move = self.pool.get('account.move').create(cr,uid,{
								'journal_id':journal_bank,#Confirm from PCIL(JOURNAL ID)
								'state':'posted',
								'date':date,
								'name':value_id,
								'partner_id':rec.customer_name.id,
								'narration':rec.narration if rec.narration else '',
								'voucher_type':'Purchase Receipt',},context=context)
					for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
						for ln in rec.purchase_receipt_one2many:
							wizard_id=ln.wizard_id
							if wizard_id == 0:
								self.wizard_id_write(cr,uid,ids,context=context)
							# if igst_check:
							# 	raise osv.except_osv(('Alert'),("Kindly update the GST Number of Supplier!"))
							if ln.type=='debit' and ln.account_id.name in ('CGST - Input','SGST - Input','IGST - Input') and ln.account_id.account_selection=='st_input':
								raise osv.except_osv(('Alert'),("You cannot select '%s' Ledger as Supplier is not registered!")%(ln.account_id.name))
							self.pool.get('account.purchase.receipts.line').write(cr,uid,ln.id,{'state':'done'})
							if ln.debit_amount:
								self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
								'account_id':ln.account_id.id,
								'debit':ln.debit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_bank,
								'period_id':period_id,
								'partner_id':rec.customer_name.id,
								'date':date,
								'ref':value_id},context=context)
							if ln.credit_amount:
								self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
								'account_id':ln.account_id.id,
								'credit':ln.credit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_bank,
								'period_id':period_id,
								'partner_id':rec.customer_name.id,
								'date':date,
								'ref':value_id},context=context)
					create_id = self.pool.get('account.stat.adjustment').create(cr,uid,{
								'state':'done',
								'date':date,
								'debit_amount':total_cgst+total_sgst+total_igst,
								'credit_amount':total_cgst+total_sgst+total_igst,
								'total_credit':total_cgst+total_sgst+total_igst,
								'total_debit':total_cgst+total_sgst+total_igst,
								'customer_name':rec.customer_name.id,
								'narration':'Tax Liability generated against the voucher no: '+str(rec.receipt_no),
								'voucher_type':'stat_adjustment',},context=context)
					if create_id:
						if company_id:
							for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
								if comp_id.stat_adjustment_seq_id:
									stat_adjustment_seq_id = comp_id.stat_adjustment_seq_id
								if comp_id.pcof_key:
									pcof_key = comp_id.pcof_key
							
						count = 0
						seq_start=1	
						if pcof_key and stat_adjustment_seq_id:
							cr.execute("select cast(count(id) as integer) from account_stat_adjustment where state not in ('draft') and stat_adjustment_number is not null  and date>='2017-07-01' and  date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
							temp_count=cr.fetchone()
							if temp_count[0]:
								count= temp_count[0]
							seq=int(count+seq_start)
							value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq).zfill(5)
							existing_value_id = self.pool.get('account.stat.adjustment').search(cr,uid,[('stat_adjustment_number','=',value_id)])
							if existing_value_id:
								value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq+1).zfill(5)
						self.pool.get('account.stat.adjustment').write(cr,uid,int(create_id),{'stat_adjustment_number':value_id,'date': receipt_date,'state':'done'})		
						search_tax_on_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','Tax on RCM')])
						if search_tax_on_rcm:
							debit_account_id=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
								'account_stat_adjustment_id':int(create_id),
								'debit_amount':total_cgst+total_sgst+total_igst,
								'account_id':search_tax_on_rcm[0],
								'type':'debit',
								'state':'done',
								'tax_rate':tax_rate,
								'expense_flag':True,
								})
							if goods_applicable!=True:
								if expense_list:
									for expense in expense_list:
										self.pool.get('expense.payment').write(cr,uid,int(expense),{'stat_adjustment_line_expense_id':int(debit_account_id)})
							if goods_applicable:
								if expense_list:
									for expense in expense_list:
										self.pool.get('expense.payment').write(cr,uid,int(expense),{'goods_stat_adjustment_line_expense_id':int(debit_account_id)})
						if igst_check==True:
							search_igst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','IGST - RCM')])
							if search_igst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_igst,
									'account_id':search_igst_rcm[0],
									'type':'credit',
									'state':'done',
									})
						else:
							search_cgst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','CGST - RCM')])
							if search_cgst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_cgst,
									'account_id':search_cgst_rcm[0],
									'type':'credit',
									'state':'done',
									})
							search_sgst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','SGST - RCM')])
							if search_sgst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_sgst,
									'account_id':search_sgst_rcm[0],
									'type':'credit',
									'state':'done',
									})
				self.write(cr,uid,rec.id,{'expense_flag':True})
			if freight_bool and freight_list_new!=[]:
				if rec.customer_name.gst_no==False or rec.customer_name.gst_no=='Unregistered':
					# asdkahsdk
					date = receipt_date
					search_date = self.pool.get('account.period').search(cr,uid,[('date_start','<=',date),('date_stop','>=',date)])
					for var in self.pool.get('account.period').browse(cr,uid,search_date):
						period_id = var.id
					srch_jour_bank = self.pool.get('account.journal').search(cr,uid,[('name','ilike','Purchase Journal')])
					for jour_bank in self.pool.get('account.journal').browse(cr,uid,srch_jour_bank):
						journal_bank = jour_bank.id
					move = self.pool.get('account.move').create(cr,uid,{
								'journal_id':journal_bank,#Confirm from PCIL(JOURNAL ID)
								'state':'posted',
								'date':date,
								'name':value_id,
								'partner_id':rec.customer_name.id,
								'narration':rec.narration if rec.narration else '',
								'voucher_type':'Purchase Receipt',},context=context)
					for line1 in self.pool.get('account.move').browse(cr,uid,[move]):
						for ln in rec.purchase_receipt_one2many:
							wizard_id=ln.wizard_id
							if wizard_id == 0:
								self.wizard_id_write(cr,uid,ids,context=context)
							# if igst_check:
							# 	raise osv.except_osv(('Alert'),("Kindly update the GST Number of Supplier!"))
							if freight_rate=='5.0':
								if ln.account_id.name in ('CGST - Input','SGST - Input','IGST - Input') and ln.account_id.account_selection=='st_input':
									raise osv.except_osv(('Alert'),("You cannot select '%s' Ledger!")%(ln.account_id.name))
							self.pool.get('account.purchase.receipts.line').write(cr,uid,ln.id,{'state':'done'})
							if ln.debit_amount:
								self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
								'account_id':ln.account_id.id,
								'debit':ln.debit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_bank,
								'period_id':period_id,
								'partner_id':rec.customer_name.id,
								'date':date,
								'ref':value_id},context=context)
							if ln.credit_amount:
								self.pool.get('account.move.line').create(cr,uid,{'move_id':line1.id,
								'account_id':ln.account_id.id,
								'credit':ln.credit_amount,
								'name':rec.customer_name.name if rec.customer_name.name else '',
								'journal_id':journal_bank,
								'period_id':period_id,
								'partner_id':rec.customer_name.id,
								'date':date,
								'ref':value_id},context=context)
					create_id = self.pool.get('account.stat.adjustment').create(cr,uid,{
								'state':'done',
								'date':date,
								'debit_amount':total_cgst+total_sgst+total_igst,
								'credit_amount':total_cgst+total_sgst+total_igst,
								'total_credit':total_cgst+total_sgst+total_igst,
								'total_debit':total_cgst+total_sgst+total_igst,
								'customer_name':rec.customer_name.id,
								'narration':rec.narration if rec.narration else '',
								'voucher_type':'stat_adjustment',},context=context)
					if create_id:
						if company_id:
							for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
								if comp_id.stat_adjustment_seq_id:
									stat_adjustment_seq_id = comp_id.stat_adjustment_seq_id
								if comp_id.pcof_key:
									pcof_key = comp_id.pcof_key
							
						count = 0
						seq_start=1	
						if pcof_key and stat_adjustment_seq_id:
							cr.execute("select cast(count(id) as integer) from account_stat_adjustment where state not in ('draft') and stat_adjustment_number is not null  and date>='2017-07-01' and  date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
							temp_count=cr.fetchone()
							if temp_count[0]:
								count= temp_count[0]
							seq=int(count+seq_start)
							value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq).zfill(5)
							existing_value_id = self.pool.get('account.stat.adjustment').search(cr,uid,[('stat_adjustment_number','=',value_id)])
							if existing_value_id:
								value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq+1).zfill(5)
						self.pool.get('account.stat.adjustment').write(cr,uid,int(create_id),{'stat_adjustment_number':value_id,'date': receipt_date,'state':'done'})		
						search_tax_on_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','Tax on RCM')])
						if search_tax_on_rcm:
							debit_account_id=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
								'account_stat_adjustment_id':int(create_id),
								'debit_amount':total_cgst+total_sgst+total_igst,
								'account_id':search_tax_on_rcm[0],
								'type':'debit',
								'state':'done',
								'tax_rate':tax_rate,
								'freight_flag':True,
								})
							if freight_list_new:
								for freight in freight_list_new:
									self.pool.get('st.input').write(cr,uid,int(freight),{'stat_freight_id':debit_account_id})
						if igst_check==True:
							search_igst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','IGST - RCM')])
							if search_igst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_igst,
									'account_id':search_igst_rcm[0],
									'type':'credit',
									'state':'done',
									})
						else:
							search_cgst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','CGST - RCM')])
							if search_cgst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_cgst,
									'account_id':search_cgst_rcm[0],
									'type':'credit',
									'state':'done',
									})
							search_sgst_rcm = self.pool.get('account.account').search(cr,uid,[('name','=','SGST - RCM')])
							if search_sgst_rcm:
								credit_account_id_1=self.pool.get('account.stat.adjustment.line').create(cr,uid,{
									'account_stat_adjustment_id':int(create_id),
									'credit_amount':total_sgst,
									'account_id':search_sgst_rcm[0],
									'type':'credit',
									'state':'done',
									})
			check_input_list=[]
			if freight_rate in ('12.0','18.0'):
				for ln in rec.purchase_receipt_one2many:
					if ln.account_id.code!=False or ln.account_id.code!='' or ln.account_id.code!=None:
						check_input_list.append(ln.account_id.code)
				if igst_check and 'igst' not in check_input_list:
					raise osv.except_osv(('Alert'),("Add 'IGST - Input' ledger to process the entry !!"))
				elif igst_check==False and 'cgst' not in check_input_list:
					raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
				elif igst_check==False and 'sgst' not in check_input_list:
					raise osv.except_osv(('Alert'),("Add 'SGST - Input' ledger to process the entry !!"))
				total_cgst_amount=0.0
				total_igst_amount=0.0
				for line in rec.purchase_receipt_one2many:
					total = 0.0
					emp_name = ""
					credit_amount = line.credit_amount
					debit_amount = line.debit_amount
					account_name = line.account_id.name
					acc_selection = line.account_id.account_selection
					gst_applied = line.account_id.gst_applied
					code = line.account_id.code
					if acc_selection == 'st_input' and gst_applied == True:
						total_debit_amount = 0.0
						phone_total = 0.0
						if code == 'igst':
							# pass
							if line.purchase_line_igst_one2many ==[]:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
							else:
								for line1 in line.purchase_line_igst_one2many:
									total_debit_amount = total_debit_amount+line1.igst_tax_amount
							total_igst_amount=total_debit_amount
							if round(total_debit_amount,2) != round(debit_amount,2):
								raise osv.except_osv(('Alert'),('Wizard amount and debit amount should be same!'))
						if code == 'cgst':
							if line.purchase_line_cgst_one2many ==[]:
								raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
							else:
								for line1 in line.purchase_line_cgst_one2many:
									total_debit_amount = total_debit_amount+line1.cgst_tax_amount
							total_cgst_amount=total_debit_amount
							# total_debit_amount=debit_amount
							# total_cgst_amount=total_debit_amount
							if round(total_debit_amount,2) != round(debit_amount,2):
								raise osv.except_osv(('Alert'),('Wizard amount and debit amount should be same'))
			if rec.customer_name.gst_no!='Unregistered':
				input_list=[]
				if rec.customer_name.gst_no!=False:
					input_list=[]
					total_cgst_amount=0.0
					total_igst_amount=0.0
					for line in rec.purchase_receipt_one2many:
						total = 0.0
						emp_name = ""
						credit_amount = line.credit_amount
						debit_amount = line.debit_amount
						account_name = line.account_id.name
						acc_selection = line.account_id.account_selection
						gst_applied = line.account_id.gst_applied
						code = line.account_id.code
						if acc_selection == 'st_input' and gst_applied == True:
							total_debit_amount = 0.0
							phone_total = 0.0
							if code == 'igst':
								# pass
								if line.purchase_line_igst_one2many ==[]:
									raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
								else:
									for line1 in line.purchase_line_igst_one2many:
										total_debit_amount = total_debit_amount+line1.igst_tax_amount
								total_igst_amount=total_debit_amount
								if round(total_debit_amount,2) != round(debit_amount,2):
									raise osv.except_osv(('Alert'),('Wizard amount and debit amount should be same!'))
							if code == 'cgst':
								if line.purchase_line_cgst_one2many ==[]:
									raise osv.except_osv(('Alert'),('Enter Details against "%s" entry to proceed.') % (account_name))
								else:
									for line1 in line.purchase_line_cgst_one2many:
										total_debit_amount = total_debit_amount+line1.cgst_tax_amount
								total_cgst_amount=total_debit_amount
								# total_debit_amount=debit_amount
								# total_cgst_amount=total_debit_amount
								if round(total_debit_amount,2) != round(debit_amount,2):
									raise osv.except_osv(('Alert'),('Wizard amount and debit amount should be same'))
						input_list.append(code)
					if rec.customer_name.gst_type_supplier.name!='Composition':
						if input_list!=[]:
							if 'cgst' in input_list:
								if 'sgst' in input_list:
									pass
								elif 'utgst' in input_list:
									pass
								else:
									raise osv.except_osv(('Alert'),("Add either 'SGST - Input' ledger or 'UTGST - Input' ledger to process the entry!!"))
							elif 'sgst' in input_list:
								 if 'cgst' not in input_list:
								 	raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
							elif 'utgst' in input_list:
								 if 'cgst' not in input_list:
								 	raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
						# if 'igst' not in input_list and igst_check:
						# 	raise osv.except_osv(('Alert'),("Add 'IGST - Input' ledger to process the entry !!"))
						# if not igst_check:
						# 	if expense_list_new1 and expense_bool:
						# 		if 'cgst' not in input_list:
						# 			 raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
						# 		if 'sgst' not in input_list:
						# 			 raise osv.except_osv(('Alert'),("Add 'SGST - Input' ledger to process the entry !!"))
						# 	if freight_list_new1 and freight_bool:
						# 		if 'cgst' not in input_list:
						# 			 raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
						# 		if 'sgst' not in input_list:
						# 			 raise osv.except_osv(('Alert'),("Add 'SGST - Input' ledger to process the entry !!"))
						# 	if legal_list and legal_bool:
						# 		if 'cgst' not in input_list:
						# 			 raise osv.except_osv(('Alert'),("Add 'CGST - Input' ledger to process the entry !!"))
						# 		if 'sgst' not in input_list:
						# 			 raise osv.except_osv(('Alert'),("Add 'SGST - Input' ledger to process the entry !!"))

							# raise osv.except_osv(('Alert'),("Add 'CGST - Input/SGST - Input' ledger to process the entry !!"))
						# if igst_check:
						# 	if 'cgst' in input_list:
						# 		raise osv.except_osv(('Alert'),("You cannot add 'CGST - Input' ledger!!"))
						# 	if 'sgst' in input_list:
						# 		raise osv.except_osv(('Alert'),("You cannot add 'SGST - Input' ledger!!"))
						# 	if 'utgst' in input_list:
						# 		raise osv.except_osv(('Alert'),("You cannot add 'UTGST - Input' ledger!!"))
					for line in rec.purchase_receipt_one2many:
						credit_amount = line.credit_amount
						debit_amount = line.debit_amount
						account_name = line.account_id.name
						acc_selection = line.account_id.account_selection
						gst_applied = line.account_id.gst_applied
						code = line.account_id.code
						if acc_selection == 'st_input' and gst_applied == True:
							if total_cgst_amount!=0.0:
								if code=='sgst':
									if round(debit_amount,2)!=round(total_cgst_amount,2):
										raise osv.except_osv(('Alert'),("SGST-Input ledger value should match with CGST-Input ledger value!!"))
								if code=='utgst':
									if round(debit_amount,2)!=round(total_cgst_amount,2):
										raise osv.except_osv(('Alert'),("UTGST-Input ledger value should match with CGST-Input ledger value!!"))
							if total_igst_amount!=0.0:
								if code=='igst':
									if round(debit_amount,2)!=round(total_igst_amount,2):
										raise osv.except_osv(('Alert'),("IGST-Input ledger value should match with Debit amount!!"))
					cr.execute("update account_purchase_receipts_line set state='done' where purchase_receipt_id in (select id from account_purchase_receipts where state in ('done','finish')) ")
					cr.commit()
					for update in rec.purchase_receipt_one2many:
						self.pool.get('account.purchase.receipts.line').write(cr,uid,update.id,{'state':'done'})
		return True

account_purchase_receipts()


class account_purchase_receipts_line(osv.osv):
	_name = 'account.purchase.receipts.line'
	_rec_name = 'purchase_receipt_id'
	_order = 'id' 
	_columns = {
		'customer_name':fields.many2one('res.partner','Supplier Name'),
		'purchase_receipt_id':fields.many2one('account.purchase.receipts','Purchase Receipt'),
		'account_id':fields.many2one('account.account','Account Name'),
		'type':fields.selection([('credit','Credit'),('debit','Debit')],'Type'),
		'tax_rate':fields.float('Tax Rate'),
		'freight_input_rate':fields.float('Tax Rate'),
		'credit_amount':fields.float('Credit(Cr.)'),
		'debit_amount':fields.float('Debit(Dr.)'),
		'state': fields.selection([
			('draft','Draft'),
			('done','Done'),
			('finish','Finish'),
			],'Status'),
		'legal_profession_one2many': fields.one2many('account.legal.profession.charges','legal_profession_id','Legal Profession Charges'),
		'wizard_id':fields.integer('Wizard Id'),
		'purchase_line_igst_one2many':fields.one2many('st.input','purchase_line_igst_id','ST Input'),
		'purchase_line_cgst_one2many':fields.one2many('st.input','purchase_line_cgst_id','ST Input'),
		'purchase_expense_one2many':fields.one2many('expense.payment','purchase_line_expense_id'),
		'purchase_freight_one2many':fields.one2many('st.input','purchase_freight_id','Freight Entry'),
		'igst_check':fields.boolean('IGST input'),
		'goods_purchase_expense_one2many':fields.one2many('expense.payment','goods_purchase_line_expense_id'),
		}
		

	_defaults = {
			'state':'draft',
		}

	def add(self, cr, uid, ids, context=None): 
		### Purchase voucher line  add button to show respective wizards 
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			credit_amount = res.credit_amount 
			debit_amount = res.debit_amount
			acc_id = res.account_id
			hsn_code = res.account_id.hsn_sac_code
			rate = str(res.account_id.rcm_rate)
			goods_applicable=res.account_id.goods_applicable
			acc_selection = acc_id.account_selection
			code= str(acc_id.code)
			freight_flag=False
			receipt_date=self.browse(cr,uid,res_id).purchase_receipt_id.receipt_date
			receipt_state=self.browse(cr,uid,res_id).purchase_receipt_id.state
			pcof_key=self.browse(cr,uid,res_id).purchase_receipt_id.company_id.pcof_key
			view_name = name_wizard = ''
			if res.account_id.name=='Freight Inward-GST' and res.type=='debit':
				freight_flag=True
			if res.account_id.name=='Freight Outward-GST' and res.type=='debit':
				freight_flag=True
			if code in ('frin12','frin18','frout12','frout18') and res.type=='debit':
				freight_flag=True
			if not acc_id.name:
				raise osv.except_osv(('Alert'),('Please Select Account.'))
			
			if ('Freight Inward-GST' in res.account_id.name) or ('Freight Outward-GST' in res.account_id.name) :
				# print debit_amount,'kkkkkk'
				if debit_amount>750.0:
					view_name = 'purchase_freight_entry_form'
					name_wizard = "Add Freight Details"
				else:
					raise osv.except_osv(('Alert'),('No Information'))
			if code in ('frin12','frin18','frout12','frout18') and rate in ('12.0','18.0'):
				view_name = 'purchase_freight_entry_form'
				name_wizard = "Add Freight Details"
			if (rate!='0.0' or hsn_code!=False) and res.type == 'debit' and acc_selection!='expenses' and freight_flag==False:
				if res.type == 'debit':
					view_name = 'account_purchase_receipts_line_form'
					name_wizard = "Purchase Details"
				else:
					raise osv.except_osv(('Alert'),('No Information'))

			if acc_selection=='expenses' and res.type == 'debit':
			# if res.account_id.name == 'Legal & Professional Charges':
				if goods_applicable==False or goods_applicable==None or goods_applicable=='' and receipt_date=='draft':
					view_name = 'expense_purchase_form'
					name_wizard = "Expenses Details"
				elif receipt_state in ('done','finish'):
					if res.purchase_expense_one2many!=[]:
						view_name = 'expense_purchase_form'
						name_wizard = "Expenses Details"
					if res.goods_purchase_expense_one2many!=[]:
						view_name = 'goods_expense_purchase_form'
						name_wizard = "Goods Expenses Details"
				elif goods_applicable and receipt_state=='draft':
					view_name = 'goods_expense_purchase_form'
					name_wizard = "Goods Expenses Details"
				else:
					raise osv.except_osv(('Alert'),('No Information'))

			if acc_selection == 'st_input' and res.type=='debit':
				if code in ('igst','cgst'):
					if code == 'igst':
						view_name = 'account_purchase_receipts_line_igst_form'
						name_wizard = "Add ST Input Details"
					if code == 'cgst':
						view_name = 'account_purchase_receipts_line_cgst_form'
						name_wizard = "Add ST Input Details"
			if view_name:
				models_data=self.pool.get('ir.model.data')
				form_view=models_data.get_object_reference(cr, uid, 'gst_accounting', view_name)
				return {
					'name': (name_wizard),
					'type': 'ir.actions.act_window',
					'view_id': False,
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'account.purchase.receipts.line',
					'target' : 'new',
					'res_id':int(res_id),
					'views': [(form_view and form_view[1] or False, 'form'),
							  ],
					'domain': '[]',
					'nodestroy': True,
						}
			else:
				raise osv.except_osv(('Alert'),('No Information'))

		return True


	def save_expense_entry(self,cr,uid,ids,context=None):
		#function to save expense entry added in the Expense Ledger wizard
		total_amount_debit = 0.0
		o = self.browse(cr,uid,ids[0])
		main_id = o.id
		igst_check=False
		amount = 0.0
		total_amount = 0.0
		tax_amount = 0.0
		cgst_amount=sgst_amount=round_amount=difference=igst_amount=0.0
		rate = 0.0
		bill_no=[]
		bill_date=[]
		today_date = effective_date_from= ''
		today_date = str(datetime.now().date())
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		account_purchase_receipt_customer=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.gst_no
		account_purchase_receipt_customer_gst_type=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.gst_type_supplier.name
		account_purchase_receipt_customer_id=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.id
		account_purchase_receipt_customer_state=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.state_id.id
		branch_state=self.browse(cr,uid,ids[0]).purchase_receipt_id.company_id.state_id.id
		expense_obj = self.pool.get('expense.payment')
		search_values = expense_obj.search(cr,uid,[('purchase_line_expense_id','=',main_id)])
		browse_values = expense_obj.browse(cr,uid,search_values)
		if account_purchase_receipt_customer_state!=branch_state:
			igst_check=True
		for browse_id in browse_values:
			bn = browse_id.bill_no
			bn = bn.lower()
			bn = bn.strip()
			bn = bn.replace(" ","")
			if len(bn) >16:
				raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
			if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
				raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
			if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
				raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
			if not reg.match(bn):
				raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
			if not browse_id.gst_item_master:
				raise osv.except_osv(('Alert'),('Please select ITEM.'))
			if browse_id.bill_value:
				if account_purchase_receipt_customer_id:
					if account_purchase_receipt_customer_gst_type=="Composition":
						tax_amount=0.0
						amount = browse_id.bill_value
						total_amount =total_amount+amount
						rate=0.0
						cgst_amount=sgst_amount=igst_amount= 0.0
					else:
						if browse_id.gst_item_master.effective_date_from:
							if today_date >= browse_id.gst_item_master.effective_date_from:
								tax_amount = (browse_id.bill_value * float(browse_id.gst_item_master.new_tax_rate))/100
								amount = (browse_id.bill_value*float(browse_id.gst_item_master.new_tax_rate))/100 + browse_id.bill_value
								total_amount =total_amount+amount
								rate=browse_id.gst_item_master.new_tax_rate
							else:
								tax_amount = (browse_id.bill_value * float(browse_id.gst_item_master.item_rate))/100
								amount = (browse_id.bill_value*float(browse_id.gst_item_master.item_rate))/100 + browse_id.bill_value
								total_amount =total_amount+amount
								rate=browse_id.gst_item_master.item_rate
						else:
							tax_amount = (browse_id.bill_value * float(browse_id.gst_item_master.item_rate))/100
							amount = (browse_id.bill_value*float(browse_id.gst_item_master.item_rate))/100 + browse_id.bill_value
							total_amount =total_amount+amount
							rate=browse_id.gst_item_master.item_rate
						if igst_check:
							igst_amount=round(tax_amount,2)
						else:
							cgst_amount=round(tax_amount/2,2)
							sgst_amount=cgst_amount
				round_amount=round(amount)
				difference=round((round_amount-amount),2)
				self.pool.get('expense.payment').write(cr,uid,browse_id.id,
									{'total_amount':round(amount,2),
									 'tax_amount':round(tax_amount,2),
									 'rate':rate,
									 'cgst_amount':cgst_amount,
									 'sgst_amount':sgst_amount,
									 'igst_amount':igst_amount,'round_off':difference})
			total_amount_debit +=browse_id.bill_value
			bill_no.append(browse_id.bill_no)
			bill_date.append(browse_id.bill_date)
		if bill_no!=[]:
			bill_no=list(set(bill_no))
			if len(bill_no)>1:
				raise osv.except_osv(('Alert'),('You cannot add different bill nos and its purchase details!'))
		if bill_date!=[]:
			bill_date=list(set(bill_date))
			if len(bill_date)>1:
				raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
		self.write(cr,uid,main_id,{'debit_amount':round(total_amount_debit,2),'igst_check':igst_check})
		return {'type': 'ir.actions.act_window_close'}

	def save_goods_expense_entry(self,cr,uid,ids,context=None):
		#function to save expense entry added in the Expense Ledger wizard
		total_amount_debit = 0.0
		o = self.browse(cr,uid,ids[0])
		main_id = o.id
		igst_check=False
		amount = 0.0
		bill_value = 0.0
		total_amount = 0.0
		tax_amount = 0.0
		cgst_amount=sgst_amount=round_amount=difference=igst_amount=0.0
		rate = 0.0
		bill_no=[]
		bill_date=[]
		today_date = effective_date_from = ''
		today_date=str(datetime.now().date())
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		account_purchase_receipt_customer=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.gst_no
		account_purchase_receipt_customer_state=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.state_id.id
		account_purchase_receipt_customer_gst_type=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.gst_type_supplier.name
		account_purchase_receipt_customer_id=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.id
		branch_state=self.browse(cr,uid,ids[0]).purchase_receipt_id.company_id.state_id.id
		expense_obj = self.pool.get('expense.payment')
		search_values = expense_obj.search(cr,uid,[('goods_purchase_line_expense_id','=',main_id)])
		browse_values = expense_obj.browse(cr,uid,search_values)
		if account_purchase_receipt_customer_state!=branch_state:
			igst_check=True
		for browse_id in browse_values:
			bn = browse_id.bill_no
			bn = bn.lower()
			bn = bn.strip()
			bn=bn.replace(" ","")
			if len(bn) >16:
				raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
			if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
				raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
			if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
				raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
			if not reg.match(bn):
				raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
			if browse_id.qty==0.0:
				raise osv.except_osv(('Alert'),('Please enter Quantity'))
			if browse_id.goods_rate==0.0:
				raise osv.except_osv(('Alert'),('Please enter Rate'))
			if not browse_id.gst_item_master:
				raise osv.except_osv(('Alert'),('Please select ITEM.'))
			if browse_id.bill_value:
				if account_purchase_receipt_customer_id:
					if account_purchase_receipt_customer_gst_type=="Composition":
						tax_amount=0.0
						amount = round(browse_id.qty*browse_id.goods_rate,2)
						bill_value=amount
						total_amount =total_amount+amount
						rate=0.0
						cgst_amount=sgst_amount=igst_amount= 0.0
					else:
						if browse_id.gst_item_master.effective_date_from:
							if today_date >= browse_id.gst_item_master.effective_date_from:
								tax_amount = (browse_id.qty*browse_id.goods_rate * float(browse_id.gst_item_master.new_tax_rate))/100
								amount = (browse_id.qty*browse_id.goods_rate*float(browse_id.gst_item_master.new_tax_rate))/100 + (browse_id.qty*browse_id.goods_rate)
								total_amount =total_amount+amount
								bill_value=round(browse_id.qty*browse_id.goods_rate,2)
								rate=browse_id.gst_item_master.new_tax_rate
							else:
								tax_amount = (browse_id.qty*browse_id.goods_rate * float(browse_id.gst_item_master.item_rate))/100
								amount = (browse_id.qty*browse_id.goods_rate*float(browse_id.gst_item_master.item_rate))/100 + (browse_id.qty*browse_id.goods_rate)
								total_amount =total_amount+amount
								bill_value=round(browse_id.qty*browse_id.goods_rate,2)
								rate=browse_id.gst_item_master.item_rate
						else:
							tax_amount = (browse_id.qty*browse_id.goods_rate * float(browse_id.gst_item_master.item_rate))/100
							amount = (browse_id.qty*browse_id.goods_rate*float(browse_id.gst_item_master.item_rate))/100 + (browse_id.qty*browse_id.goods_rate)
							total_amount =total_amount+amount
							bill_value=round(browse_id.qty*browse_id.goods_rate,2)
							rate=browse_id.gst_item_master.item_rate
						if igst_check:
							igst_amount=round(tax_amount,2)
						else:
							cgst_amount=round(tax_amount/2,2)
							sgst_amount=cgst_amount
				round_amount=round(amount)
				difference=round((round_amount-amount),2)
				self.pool.get('expense.payment').write(cr,uid,browse_id.id,
									{'total_amount':round(amount,2),
									 'tax_amount':round(tax_amount,2),
									 'rate':rate,
									 'bill_value':round(bill_value,2),
									 'cgst_amount':cgst_amount,
									 'sgst_amount':sgst_amount,
									 'igst_amount':igst_amount,'round_off':difference})
			total_amount_debit +=(browse_id.qty*browse_id.goods_rate)
			bill_no.append(browse_id.bill_no)
			bill_date.append(browse_id.bill_date)
		if bill_no!=[]:
			bill_no=list(set(bill_no))
			if len(bill_no)>1:
				raise osv.except_osv(('Alert'),('You cannot add different bill nos and its purchase details!'))
		if bill_date!=[]:
			bill_date=list(set(bill_date))
			if len(bill_date)>1:
				raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
		self.write(cr,uid,main_id,{'debit_amount':round(total_amount_debit,2),'igst_check':igst_check})
		return {'type': 'ir.actions.act_window_close'}

	def cancel(self, cr, uid, ids, context=None):
		#function to cancel the wizard
		return {'type': 'ir.actions.act_window_close'}

	def save_legal_profession_charges(self,cr,uid,ids,context=None):
		#function to save legal profession charges entry added in the legal profession Ledger wizard
		total_amount_debit = igst_amount=divided_tax_amount=round_amount=difference=0.0
		igst_check=False
		o = self.browse(cr,uid,ids[0])
		main_id = o.id
		bill_no=[]
		bill_date=[]
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		account_purchase_receipt_customer=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.gst_no
		account_legal_profession_charges_obj = self.pool.get('account.legal.profession.charges')
		search_values = account_legal_profession_charges_obj.search(cr,uid,[('legal_profession_id','=',main_id)])
		browse_values = account_legal_profession_charges_obj.browse(cr,uid,search_values)
		account_purchase_receipt_customer_state=self.browse(cr,uid,ids[0]).purchase_receipt_id.customer_name.state_id.id
		branch_state=self.browse(cr,uid,ids[0]).purchase_receipt_id.company_id.state_id.id
		if account_purchase_receipt_customer_state!=branch_state:
			igst_check=True
		for rec in self.browse(cr,uid,ids):
			if rec.legal_profession_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for browse_id in rec.legal_profession_one2many:
				bn = browse_id.bill_no
				bn = bn.lower()
				bn = bn.strip()
				bn=bn.replace(" ","")
				if len(bn) >16:
					raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
				if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
					raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
				if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
					raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
				if not reg.match(bn):
					raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
				tax_amount = (browse_id.bill_value * rec.tax_rate)/100
				divided_tax_amount = tax_amount/2
				total_amount = browse_id.bill_value+tax_amount
				total_amount_debit +=browse_id.bill_value
				if igst_check:
					divided_tax_amount=0.0
					igst_amount=tax_amount
				round_amount=round(total_amount)
				difference=round((round_amount-total_amount),2)
				self.pool.get('account.legal.profession.charges').write(cr,uid,browse_id.id,{
					'cgst_amount': divided_tax_amount,
					'sgst_amount': divided_tax_amount,
					'igst_amount': igst_amount,
					'total_amount': total_amount,
					'rate':rec.tax_rate,'igst_check':igst_check,'round_off':difference})
				bill_no.append(browse_id.bill_no)
				bill_date.append(browse_id.bill_date)
		if bill_no!=[]:
			bill_no=list(set(bill_no))
			if len(bill_no)>1:
				raise osv.except_osv(('Alert'),('You cannot add different bill nos and its purchase details!'))
		if bill_date!=[]:
			bill_date=list(set(bill_date))
			if len(bill_date)>1:
				raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
		self.write(cr,uid,main_id,{'debit_amount':round(total_amount_debit,2)})
		return {'type': 'ir.actions.act_window_close'}

	def save_input_purchase_gst(self, cr, uid, ids, context=None):
		#Function to save the st input wizard value in the ST input ledger wizard
		total_amount = 0.0
		total_cgst_amount=total_igst_amount=0.0
		bill_no=[]
		bill_date=[]
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		for rec in self.browse(cr,uid,ids):
			if rec.purchase_line_cgst_one2many == [] and rec.purchase_line_igst_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.purchase_line_cgst_one2many:
				if line:
					bn = line.bill_no
					bn = bn.lower()
					bn = bn.strip()
					bn = bn.replace(" ","")
					if len(bn) >16:
						raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
					if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if not reg.match(bn):
						raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
					tax_amount = (line.bill_value * line.gst_input_rate.rate)/100
					divided_tax_amount = tax_amount/2
					total_amount=line.bill_value+tax_amount
					total_cgst_amount = total_cgst_amount + divided_tax_amount
					round_amount=round(total_amount)
					difference=round((round_amount-total_amount),2)
					self.pool.get('st.input').write(cr,uid,line.id,{'total_amount':round(total_amount,2),'sgst_tax_amount':round(divided_tax_amount,2),'cgst_tax_amount':round(divided_tax_amount,2),'igst_tax_amount':0.0,'round_off':difference})
					bill_no.append(line.bill_no)
					bill_date.append(line.bill_date)
			for line in rec.purchase_line_igst_one2many:
				if line:
					bn = line.bill_no
					bn = bn.lower()
					bn = bn.strip()
					bn = bn.replace(" ","")
					if len(bn) >16:
						raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
					if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if not reg.match(bn):
						raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
					tax_amount = (line.bill_value * line.gst_input_rate.rate)/100
					total_amount=line.bill_value+tax_amount
					total_cgst_amount = tax_amount
					round_amount=round(total_amount)
					difference=round((round_amount-total_amount),2)
					self.pool.get('st.input').write(cr,uid,line.id,{'total_amount':round(total_amount,2),'sgst_tax_amount':0.0,'cgst_tax_amount':0.0,'igst_tax_amount':round(tax_amount,2),'round_off':difference})
					bill_no.append(line.bill_no)
					bill_date.append(line.bill_date)
			if bill_no!=[]:
				bill_no=list(set(bill_no))
				if len(bill_no)>1:
					raise osv.except_osv(('Alert'),('You cannot add different bill nos and its purchase details!'))
			if bill_date!=[]:
				bill_date=list(set(bill_date))
				if len(bill_date)>1:
					raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':round(total_cgst_amount,2)})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':round(total_cgst_amount,2)})
		return {'type': 'ir.actions.act_window_close'}

	def save_freight_entry(self, cr, uid, ids, context=None):
		#Function to save the Freight input wizard value in the Freight ledger wizard
		amount = 0.0
		total_amount = 0.0
		freight_tax_amount = 0.0
		igst_check = False
		bill_no=[]
		bill_date=[]
		reg=re.compile('^[A-Za-z0-9/\-\\\s]+$')
		for rec in self.browse(cr,uid,ids):
			if rec.purchase_freight_one2many == []:
				raise osv.except_osv(('Alert'),('No line to process!'))
			for line in rec.purchase_freight_one2many:
				if line.bill_value:
					bn = line.bill_no
					bn = bn.lower()
					bn = bn.strip()
					bn = bn.replace(" ","")
					if len(bn) >16:
						raise osv.except_osv(('Alert'),('Bill No cannot exceed 16 characters!'))
					if bn=='na' or bn=='nil' or bn.isalpha() or bn=="" or bn=='0' or bn=='00' or bn=='000' or bn=='0000' or bn=='00000' or bn=='000000' or bn in ('.','/','-','\/'):
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if bn=='0000000' or bn=='00000000' or bn=='000000000' or bn=='0000000000' or bn=='00000000000' or bn=='000000000000' or bn=='0000000000000' or bn=='00000000000000' or bn=='000000000000000' or bn=='0000000000000000':
						raise osv.except_osv(('Alert'),('Please enter valid Bill No'))
					if not reg.match(bn):
						raise osv.except_osv(('Alert'),('Bill No cannot contain special characters'))
					freight_tax_amount = (line.bill_value * float(rec.freight_input_rate))/100
					amount = (line.bill_value*float(rec.freight_input_rate))/100 + line.bill_value
					total_amount =total_amount+line.bill_value
					round_amount=round(amount)
					difference=round((round_amount-amount),2)
					if line.from_state.id!=line.to_state.id:
						self.pool.get('st.input').write(cr,uid,line.id,{'total_amount':amount,'freight_tax_amount':freight_tax_amount,'sgst_tax_amount':0.0,'cgst_tax_amount':0.0,'igst_tax_amount':round(freight_tax_amount,2),'freight_input_rate':rec.freight_input_rate,'round_off':difference})
						igst_check=True
					else:
						self.pool.get('st.input').write(cr,uid,line.id,{'total_amount':amount,'freight_tax_amount':freight_tax_amount,'sgst_tax_amount':round(freight_tax_amount/2,2),'cgst_tax_amount':round(freight_tax_amount/2,2),'igst_tax_amount':0.0,'freight_input_rate':rec.freight_input_rate,'round_off':difference})
					bill_no.append(line.bill_no)
					bill_date.append(line.bill_date)
			if bill_no!=[]:
				bill_no=list(set(bill_no))
				if len(bill_no)>1:
					raise osv.except_osv(('Alert'),('You cannot add different bill nos and its purchase details!'))
			if bill_date!=[]:
				bill_date=list(set(bill_date))
				if len(bill_date)>1:
					raise osv.except_osv(('Alert'),('Bill date cannot be different!'))
			if rec.type=='debit':
				self.write(cr,uid,rec.id,{'debit_amount':round(total_amount,2),'igst_check':igst_check})
			else:
				self.write(cr,uid,rec.id,{'credit_amount':round(total_amount,2),'igst_check':igst_check})
		return {'type': 'ir.actions.act_window_close'}

account_purchase_receipts_line()

class account_legal_profession_charges(osv.osv):
	_name = 'account.legal.profession.charges'
	_columns = {
		'bill_no': fields.char('Bill No',size=16),
		'bill_date': fields.date('Bill Date'),
		'bill_value': fields.float('Bill Value'),
		'rate': fields.float('Rate', size=20),
		'cgst_amount': fields.float('CGST Amount'),
		'sgst_amount': fields.float('SGST/UGST Amount'),
		'igst_amount': fields.float('IGST Amount'),
		'total_amount': fields.float('Total Amount'),
		'legal_profession_id': fields.many2one('account.purchase.receipts.line',''),
		'stat_legal_profession_id': fields.many2one('account.stat.adjustment.line',''),
		'igst_check':fields.boolean('IGST Check'),
		'round_off':fields.float('Round-off'),
		}

	_defaults = {
			'bill_value':0.0,
			'cgst_amount': 0.0,
			'sgst_amount': 0.0,
			'igst_amount': 0.0,
			'total_amount': 0.0,
			'igst_check':False,
		}


	def onchange_bill_value(self, cr, uid, ids, bill_value, rate, igst_check, context=None):
		#Function to get cgst/sgst/igst tax amount based on the inter state/intra state transaction on input of bill value
		data = {}
		igst_amount=0.0
		if bill_value and rate>=0.0:
			tax_amount = (bill_value * rate)/100
			divided_tax_amount = tax_amount/2
			total_amount = bill_value+tax_amount
			round_amount=round(total_amount)
			difference=round((round_amount-total_amount),2)
			if igst_check:
				divided_tax_amount=0.0
				igst_amount=tax_amount
			data.update(
				{
					'cgst_amount': divided_tax_amount,
					'sgst_amount': divided_tax_amount,
					'igst_amount': igst_amount,
					'total_amount': total_amount,
					'round_off':difference,
				})
		else:
			data.update(
				{
					'cgst_amount': 0.00,
					'sgst_amount': 0.00,
					'igst_amount': 0.00,
					'total_amount': 0.00,
					'round_off': 0.00,
				})
		return {'value':data}



account_legal_profession_charges()


class account_stat_adjustment(osv.osv):
	_name = 'account.stat.adjustment'
	_order = 'stat_adjustment_number desc'
	
	def _get_company(self, cr, uid, context=None):
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id
	
	_columns = {
		'cus_new':fields.char('Supllier Name',size=224),
		'stat_adjustment_number': fields.char('Stat Adjustment No.',size=124),
		'date' : fields.date('Date'),
		'type':fields.selection([('debit','By-Debit(Dr.)'),('credit','To-Credit(Cr.)')],'Type'),
		'customer_name':fields.many2one('res.partner','Supplier Name'),
		'account_id':fields.many2one('account.account','Account Name'),
		'narration':fields.text('Narration'),
		'credit_amount':fields.float('Credit(Cr.)'),
		'debit_amount':fields.float('Debit(Dr.)'),
		'stat_adjustment_one2many':fields.one2many('account.stat.adjustment.line','account_stat_adjustment_id','Journal Entries'),
		'from_date':fields.function(lambda *a,**k:{}, method=True, type='date',string="Date From"),
		'to_date':fields.function(lambda *a,**k:{}, method=True, type='date',string="Date To"),
		'state': fields.selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],'Status'),
		'customer_id':fields.related('customer_name','ou_id',type='char',relation='res.partner',string='Supplier ID'),
		'customer_id_invisible':fields.char('Supplier ID Invisible',size=124),
		'voucher_type':fields.char('Voucher Type',size=124),
		'company_id':fields.many2one('res.company','Company'),
		'total_credit':fields.float('for report credit'),#for report total
		'total_debit':fields.float('for report debit'),#for report total
		# 'cancel_bool':fields.boolean('Cancel'),
		# 'cancel_reason':fields.char('Reason for Cancel',size=300),
		
	}
	_defaults = {
		'state':'draft',
		'company_id':_get_company,
		'voucher_type': 'stat_adjustment'
	}

	def customer_name_change(self, cr, uid, ids, customer_name, context=None):
		#function to get supplier id on onchange of supplier name 
		v = {}
		if customer_name:
			srch = self.pool.get('res.partner').search(cr,uid,[('id','=',customer_name)])
			if srch:
				for partner in self.pool.get('res.partner').browse(cr,uid,srch):
					ou_id = partner.ou_id
				v['customer_id'] = ou_id
				v['customer_id_invisible'] = ou_id
		if not	customer_name:
			v['customer_id']=None
			v['customer_id_invisible'] = None

		return {'value':v}

	def add_info(self, cr, uid, ids, context=None):
		#function to add ledgers in the stat adjustment line
		temp = 0.0
		tax_rate = 0.0
		auto_credit_cal = 0.0
		for res in self.browse(cr,uid,ids):
			account_id = res.account_id.id
			account_name = res.account_id.name
			acc_selection = res.account_id.account_selection
			customer_name=res.customer_name.id
			customer_name_char = res.customer_name.name
			types = res.type
			if account_name == 'Tax on RCM':
				tax_rate = self.pool.get('account.account').browse(cr,uid,account_id).rcm_rate
			auto_credit_cal = auto_debit_cal = auto_credit_total = auto_debit_total = itds_total = temp=0.0
			account_id1=res.account_id
			for i in res.stat_adjustment_one2many:
				if account_id1.id==i.account_id.id:
					raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

				if not account_id:
					raise osv.except_osv(('Alert'),('Please select Account Name.'))
				
				if not types:
					raise osv.except_osv(('Alert'),('Please select Type.'))
				if i.type == 'debit':
					auto_credit_cal += i.debit_amount
			self.pool.get('account.stat.adjustment.line').create(cr,uid,{
					'account_stat_adjustment_id':res.id,
					'account_id':account_id,
					'customer_name':customer_name,
					'debit_amount':temp,
					'credit_amount':auto_credit_cal,
					'type':types,
					'tax_rate':tax_rate
				})
		self.write(cr,uid,res.id,{'account_id':None,'type':None})						
		return True

	def process(self,cr,uid,ids,context=None):
		#Function to Stat adjustment voucher
		receipt_date = ''
		account_stat_adjustment_line_obj = self.pool.get('account.stat.adjustment.line')
		account_legal_profession_charges_obj =self.pool.get('account.legal.profession.charges')
		o= self.browse(cr,uid,ids[0])
		main_id = o.id
		legal_bool=tax_rate=py_date=False
		cr_total = dr_total = total = iob_total = legal_debit_amount = 0.0
		post = legal_list = []
		for rec in self.browse(cr,uid,ids):
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
			if rec.date:
				check_bool=self.pool.get('res.users').browse(cr,uid,1).company_id.receipt_check
				if check_bool:
					if rec.date != str(today_date):
						raise osv.except_osv(('Alert'),("Back-Dated Entries are not allowed \n Kindly Select Today's Date "))
				py_date = str(today_date + relativedelta(days=-5))
				if rec.date < str(py_date) or rec.date > str(today_date):
					raise osv.except_osv(('Alert'),('Kindly select Receipt Date 5 days earlier from current date.'))
				receipt_date=rec.date	
			else:				
				receipt_date=datetime.now().date()
		search_lines = account_stat_adjustment_line_obj.search(cr,uid,[('account_stat_adjustment_id','=',main_id)])
		for browse_lines in account_stat_adjustment_line_obj.browse(cr,uid,search_lines):
			if browse_lines.type == 'credit':
				if browse_lines.credit_amount <= 0.0:
					raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
			elif browse_lines.type == 'debit':
				if browse_lines.debit_amount <= 0.0:
					raise osv.except_osv(('Alert'),('Amount should be greater than zero.'))
			else:
				raise osv.except_osv(('Alert'),('Account Type %s cannot be blank' %(str(browse_lines.account_id.name))))
			cr_total += browse_lines.credit_amount
			dr_total += browse_lines.debit_amount
			account_id = browse_lines.account_id.id
			temp = tuple([account_id])
			post.append(temp)
			for i in range(0,len(post)):
				for j in range(i+1,len(post)):
					if post[i][0]==post[j][0]:
						raise osv.except_osv(('Alert!'),('Duplicate account entry is not allowed.'))

		if round(dr_total,2) != round(cr_total,2):
			raise osv.except_osv(('Alert'),('Credit and Debit Amount should be equal.'))

		if dr_total == 0.0 or cr_total == 0.0:
			raise osv.except_osv(('Alert'),('Amount cannot be zero.'))
		for browse_lines in account_stat_adjustment_line_obj.browse(cr,uid,search_lines):
			account_name = browse_lines.account_id.name
			if 'Tax on RCM' in account_name and browse_lines.type == 'debit':
				if browse_lines.stat_legal_profession_one2many==[]:
					raise osv.except_osv(('Alert'),('No Bill details to proceed the Tax on RCM.'))
		for rec in self.browse(cr,uid,ids):
			today_date = datetime.now().date()
			year = today_date.year
			year1=today_date.strftime('%y')
			start_year = end_year = pcof_key = credit_note_id = ''
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
			financial_year = str(year1-1)+str(year1)
			financial_start_date = str(start_year)+'-04-01'
			financial_end_date = str(end_year)+'-03-31'
			company_id=self._get_company(cr,uid,context=None)
			if company_id:
				for comp_id in self.pool.get('res.company').browse(cr,uid,[company_id]):
					if comp_id.stat_adjustment_seq_id:
						stat_adjustment_seq_id = comp_id.stat_adjustment_seq_id
					if comp_id.pcof_key:
						pcof_key = comp_id.pcof_key
			count = 0
			seq_start=1
			if pcof_key and stat_adjustment_seq_id:
				cr.execute("select cast(count(id) as integer) from account_stat_adjustment where state not in ('draft') and stat_adjustment_number is not null  and date>='2017-07-01' and  date between '"+str(financial_start_date)+"' and '"+str(financial_end_date)+"' ");
				temp_count=cr.fetchone()
				if temp_count[0]:
					count= temp_count[0]
				seq=int(count+seq_start)
				value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq).zfill(5)
				existing_value_id = self.pool.get('account.stat.adjustment').search(cr,uid,[('stat_adjustment_number','=',value_id)])
				if existing_value_id:
					value_id = pcof_key + stat_adjustment_seq_id +  str(financial_year) +str(seq+1).zfill(5)
			self.write(cr,uid,ids,{'stat_adjustment_number':value_id,'date': receipt_date,'state':'done'})
			for ln in rec.stat_adjustment_one2many:
				self.pool.get('account.stat.adjustment.line').write(cr,uid,ln.id,{'state':'done'})
						
		return True

account_stat_adjustment()



class account_stat_adjustment_line(osv.osv):
	_name = 'account.stat.adjustment.line'
	_rec_name='credit_amount'
	_columns = {
		'account_stat_adjustment_id':fields.many2one('account.stat.adjustment',''),
		'account_id':fields.many2one('account.account','Account Name'),
		'customer_name':fields.many2one('res.partner','Supplier Name'),
		'cus_new':fields.char('Supplier Name',size=256),
		'type':fields.selection([('debit','By-Debit(Dr.)'),('credit','To-Credit(Cr.)')],'Type'),
		'credit_amount':fields.float('Credit(Cr.)'),
		'debit_amount':fields.float('Debit(Dr.)'),
		'tax_rate':fields.float('Tax Rate'),
		'state':fields.selection([
			('draft','Draft'),
			('done','Done'),
			('cancel','Cancel')],'State'),
		'wizard_id':fields.integer('Wizard Id'),
		'stat_legal_profession_one2many': fields.one2many('account.legal.profession.charges','stat_legal_profession_id','Stat Legal Profession Charges'),
		'stat_adjustment_expense_one2many':fields.one2many('expense.payment','stat_adjustment_line_expense_id'),
		'goods_stat_adjustment_expense_one2many':fields.one2many('expense.payment','goods_stat_adjustment_line_expense_id'),
		'stat_freight_one2many':fields.one2many('st.input','stat_freight_id'),
		'expense_flag':fields.boolean('Expense Flag'),
		'purchase_flag':fields.boolean('Purchase Flag'),
		'freight_flag':fields.boolean('Freight Flag'),
		'freight_input_rate':fields.float('Tax Rate'),
	}
	_defaults = {
		'state':'draft',
		'expense_flag':False,
		'purchase_flag':False,
		'freight_flag':False,
	}

	def add(self, cr, uid, ids, context=None): 
		### Stat adjustment line add button and show the respective wizards based on the ledger 
		for res in self.browse(cr,uid,ids):
			res_id = res.id
			credit_amount = res.credit_amount 
			debit_amount = res.debit_amount
			acc_id = res.account_id
			acc_selection = acc_id.account_selection
			# customer_name = res.customer_name.name
			view_name = name_wizard = ''
			
			if not acc_id.name:
				raise osv.except_osv(('Alert'),('Please Select Account.'))
			
			if res.account_id.name == 'Tax on RCM':
					if res.type == 'debit' and res.purchase_flag==True:
						view_name = 'account_stat_adjustment_line_form'
						name_wizard = "Tax on RCM"
					elif res.type == 'debit' and res.expense_flag==True:
						view_name = 'expense_stat_adjustment_line_form'
						name_wizard = "Tax on RCM"
					elif res.type == 'debit' and res.freight_flag==True:
						view_name = 'freight_input_stat_adjustment_line_form'
						name_wizard = "Tax on RCM"
					else:
						raise osv.except_osv(('Alert'),('No Information'))
					if view_name:
						models_data=self.pool.get('ir.model.data')
						form_view=models_data.get_object_reference(cr, uid, 'gst_accounting', view_name)
						return {
							'name': (name_wizard),
							'type': 'ir.actions.act_window',
							'view_id': False,
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'account.stat.adjustment.line',
							'target' : 'new',
							'res_id':int(res_id),
							'views': [(form_view and form_view[1] or False, 'form'),
									  ],
							'domain': '[]',
							'nodestroy': True,
						}
			else:
				raise osv.except_osv(('Alert'),('No Information'))

		return True

	def save_stat_legal_profession_charges(self,cr,uid,ids,context=None):
		#Function to save legal profession entry details in the wizard
		total_amount_debit = 0.0
		o = self.browse(cr,uid,ids[0])
		main_id = o.id
		account_legal_profession_charges_obj = self.pool.get('account.legal.profession.charges')
		search_values = account_legal_profession_charges_obj.search(cr,uid,[('stat_legal_profession_id','=',main_id)])
		browse_values = account_legal_profession_charges_obj.browse(cr,uid,search_values)
		for browse_id in browse_values:
			total_amount_debit +=browse_id.total_amount
			self.pool.get('account.legal.profession.charges').write(cr,uid,browse_id.id,{'rate':o.tax_rate})
		self.write(cr,uid,main_id,{'debit_amount':round(total_amount_debit,2)})
		return {'type': 'ir.actions.act_window_close'}

account_stat_adjustment_line()


class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
    	'purchase_receipt_seq_id':fields.char('Purchase Request ID',size=20),
    	'stat_adjustment_seq_id':fields.char('Stat Adjustment ID',size=20),
    }

    _defaults ={
    'purchase_receipt_seq_id':'2PR',
    'stat_adjustment_seq_id':'2SA',
    }

res_company()


class st_input(osv.osv):
	_inherit = 'st.input'

	_columns = {
		'purchase_line_igst_id':fields.many2one('account.purchase.receipts.line','Purchase Payment line'),
		'purchase_line_cgst_id':fields.many2one('account.purchase.receipts.line','Purchase Payment line'),
		'purchase_freight_id':fields.many2one('account.purchase.receipts.line','Freight Entry'),
		'stat_freight_id':fields.many2one('account.stat.adjustment.line','Freight Entry'),
		'round_off':fields.float('Round-off'),
	}

st_input()

class expense_payment(osv.osv):
	_inherit = 'expense.payment'

	_columns = {

		'purchase_line_expense_id':fields.many2one('account.purchase.receipts.line','Purchase Expense line'),
		'stat_adjustment_line_expense_id':fields.many2one('account.stat.adjustment.line','Stat Expense line'),
		'cgst_amount': fields.float('CGST Amount'),
		'sgst_amount': fields.float('SGST Amount'),
		'igst_amount': fields.float('IGST Amount'),
		'goods_purchase_line_expense_id':fields.many2one('account.purchase.receipts.line','Purchase Expense line'),
		'goods_stat_adjustment_line_expense_id':fields.many2one('account.stat.adjustment.line','Stat Expense line'),
		'qty':fields.float('Quantity'),
		'goods_rate':fields.float('Rate'),
		'goods_uom':fields.many2one('goods.uom','UOM'),
		'round_off':fields.float('Round-off'),
	}

	def onchange_item_master(self, cr, uid, ids, customer_name, bill_value, gst_item_master, context=None):
		#Function to get cgst/sgst/igst tax amount based on the inter state/intra state transaction on input of bill value,item master
		data = {}
		today_date = effective_date_from = ''
		today_date = str(datetime.now().date())
		if bill_value and gst_item_master:
			customer_state=False
			company_state=False
			# rate=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).item_rate
			effective_date_from = self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).effective_date_from
			if effective_date_from:
				if today_date >= effective_date_from:
					rate=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).new_tax_rate
				else:
					rate=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).item_rate
			else:
				rate=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).item_rate
			hsn_sac_code=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).hsn_code
			if customer_name:
				reg_type=self.pool.get('res.partner').browse(cr,uid,customer_name).gst_type_supplier.name
				customer_state=self.pool.get('res.partner').browse(cr,uid,customer_name).state_id.id
				company_state=self.pool.get('res.users').browse(cr,uid,uid).company_id.state_id.id
				if reg_type=='Composition':
					rate=0.0
			tax_amount = (bill_value * rate)/100
			if customer_state==company_state:
				cgst_amount=tax_amount/2
				sgst_amount=cgst_amount
				igst_amount=0.0
				total_amount = bill_value+tax_amount
				amount=total_amount
				round_amount=round(total_amount)
				difference=round((round_amount-amount),2)
				data.update(
					{
						'rate':rate,
						'hsn_sac_code': hsn_sac_code,
						'cgst_amount':cgst_amount,
						'sgst_amount':sgst_amount,
						'igst_amount':igst_amount,
						'tax_amount': tax_amount,
						'total_amount': total_amount,
						'round_off':difference,
					})
			else:
				cgst_amount=0.0
				sgst_amount=0.0
				igst_amount=tax_amount
				total_amount = bill_value+tax_amount
				amount=total_amount
				round_amount=round(total_amount)
				difference=round((round_amount-amount),2)
				data.update(
					{
						'rate':rate,
						'hsn_sac_code': hsn_sac_code,
						'cgst_amount':cgst_amount,
						'sgst_amount':sgst_amount,
						'igst_amount':igst_amount,
						'tax_amount': tax_amount,
						'total_amount': total_amount,
						'round_off':difference,
					})
		else:
			data.update(
				{
					'rate':0.00,
					'hsn_sac_code': '',
					'tax_amount': 0.00,
					'cgst_amount':0.00,
					'sgst_amount':0.00,
					'igst_amount':0.00,
					'total_amount': 0.00,
					'round_off':0.00,
				})
		return {'value':data}

	def onchange_goods_item_master(self, cr, uid, ids, customer_name,bill_value,qty,goods_rate,gst_item_master, context=None):
		#Function to get cgst/sgst/igst tax amount based on the inter state/intra state transaction on input of bill value,item master
		data = {}
		today_date = effective_date_from = ''
		if qty!=0.0 and goods_rate!=0.0:
			customer_state=False
			company_state=False
			rate=0.0
			hsn_sac_code=False
			today_date = str(datetime.now().date())
			if gst_item_master:
				effective_date_from = self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).effective_date_from
				if effective_date_from:
					if today_date >= effective_date_from:
						rate=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).new_tax_rate
					else:
						rate=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).item_rate
				else:
					rate=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).item_rate
				hsn_sac_code=self.pool.get('gst.item.master').browse(cr,uid,gst_item_master).hsn_code
			if customer_name:
				reg_type=self.pool.get('res.partner').browse(cr,uid,customer_name).gst_type_supplier.name
				customer_state=self.pool.get('res.partner').browse(cr,uid,customer_name).state_id.id
				company_state=self.pool.get('res.users').browse(cr,uid,uid).company_id.state_id.id
				if reg_type=='Composition':
					rate=0.0
			bill_value=round(qty*goods_rate,2)
			tax_amount = (bill_value * rate)/100
			if customer_state==company_state:
				cgst_amount=tax_amount/2
				sgst_amount=cgst_amount
				igst_amount=0.0
				total_amount = bill_value+tax_amount
				amount=total_amount
				round_amount=round(total_amount)
				difference=round((round_amount-amount),2)
				data.update(
					{
						'bill_value':bill_value,
						'rate':rate,
						'hsn_sac_code': hsn_sac_code,
						'cgst_amount':cgst_amount,
						'sgst_amount':sgst_amount,
						'igst_amount':igst_amount,
						'tax_amount': tax_amount,
						'total_amount': total_amount,
						'round_off':difference,
					})
			else:
				cgst_amount=0.0
				sgst_amount=0.0
				igst_amount=tax_amount
				total_amount = bill_value+tax_amount
				amount=total_amount
				round_amount=round(total_amount)
				difference=round((round_amount-amount),2)
				data.update(
					{	'bill_value':bill_value,
						'rate':rate,
						'hsn_sac_code': hsn_sac_code,
						'cgst_amount':cgst_amount,
						'sgst_amount':sgst_amount,
						'igst_amount':igst_amount,
						'tax_amount': tax_amount,
						'total_amount': total_amount,
						'round_off':difference,
					})
		else:
			data.update(
				{
					'bill_value':0.00,
					'rate':0.00,
					'hsn_sac_code': '',
					'tax_amount': 0.00,
					'cgst_amount':0.00,
					'sgst_amount':0.00,
					'igst_amount':0.00,
					'total_amount': 0.00,
					'round_off':0.00,
				})
		return {'value':data}

expense_payment()