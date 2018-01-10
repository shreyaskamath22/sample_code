
from osv import osv,fields
from tools.translate import _
from datetime import datetime

class invoice_advance_receipts(osv.osv):
	_name = 'invoice.advance.receipts'
	_rec_name = 'invoice_id'

	_columns = {
		# 'receipt_ids':fields.one2many('account.sales.receipts','invoice_advance_id','Advance Sales Receipt'),
		'adv_receipt_line_ids':fields.one2many('invoice.advance.receipts.line','in_adv_rep_id','Advance Receipt Lines'),
		'invoice_id': fields.many2one('invoice.adhoc.master','Invoice')
	}

	def save_advance_receipt_details(self,cr,uid,ids,context=None):
		invoice_adhoc_obj = self.pool.get('invoice.adhoc.master')
		receipt_obj = self.pool.get('account.sales.receipts')
		advance_obj = self.pool.get('advance.invoice.line')
		inv_adv_data = self.browse(cr,uid,ids[0])
		adv_receipt_amount = 0.0
		advance_receipts = ''
		entire_adjustment_amount = 0.0
		inv_vals = {}
		receipt_line_list=[]
		receipt_no=[]
		advance_list=[]
		flag=False
		for adv_receipt_line in inv_adv_data.adv_receipt_line_ids:
			if adv_receipt_line.select_receipt_bool == True:
				if adv_receipt_line.invoice_adjustment_amount == 0:
					raise osv.except_osv(('Alert'),('Enter the adjustment amount for selected receipts!'))
				if adv_receipt_line.invoice_adjustment_amount > adv_receipt_line.advance_pending:
					raise osv.except_osv(('Alert'),('Adjustment amount should be less than advance pending!'))
				entire_adjustment_amount =  entire_adjustment_amount + adv_receipt_line.invoice_adjustment_amount
				if not advance_receipts:
					advance_receipts = adv_receipt_line.receipt_id.receipt_no
				else:
					advance_receipts = advance_receipts+','+adv_receipt_line.receipt_id.receipt_no
				if adv_receipt_line.receipt_id.advance_pending == 0.0:
					advance_pending = adv_receipt_line.receipt_id.credit_amount - adv_receipt_line.invoice_adjustment_amount
				else:
					advance_pending = adv_receipt_line.receipt_id.advance_pending - adv_receipt_line.invoice_adjustment_amount
				
				if adv_receipt_line.receipt_id.id:
					for x in adv_receipt_line.receipt_id.sales_receipts_one2many:
						if x.account_id.account_selection == 'advance':
							receipt_line_list.append(x.id)
							payment_status=self.pool.get('account.sales.receipts.line').browse(cr,uid,x.id).payment_status
							vals =self.pool.get('account.sales.receipts.line').browse(cr,uid,x.id)
							for line in vals.advance_one2many:
								if line.service_classification != inv_adv_data.invoice_id.service_classification:
									raise osv.except_osv(('Alert'),('Service Classification selected in the Invoice is not same as in Advance Receipt!'))
							inv_data=invoice_adhoc_obj.browse(cr,uid,int(inv_adv_data.invoice_id.id))
							advance_id =self.pool.get('advance.invoice.line').create(cr,uid,{
														'advance_invoice_line_id':int(x.id),
														'paid_date':inv_data.invoice_paid_date,
														'invoice_id':inv_data.id,
														'partial_payment_amount':adv_receipt_line.invoice_adjustment_amount,
														# 'invoice_number':inv_data.invoice_number,
														'invoice_amount':inv_data.pending_amount,
														'check_settle':False,
														'service_classification':inv_data.service_classification,
														'payment_method_adv':'partial_payment',
															    })
							receipt_no.append(vals.receipt_id.id)
							advance_list.append(int(advance_id))
							receipt_obj.settle(cr,uid,[int(vals.receipt_id.id)],context=None)
				receipt_obj.write(cr,uid,adv_receipt_line.receipt_id.id,{'advance_pending':advance_pending})
				flag=True
		if flag==False:
			raise osv.except_osv(('Alert!'),('Please select the record from wizard!'))
		if entire_adjustment_amount > inv_adv_data.invoice_id.grand_total_amount:
			raise osv.except_osv(('Alert'),('Total adjustment amount should not exceed invoice gross total!'))
		elif entire_adjustment_amount < inv_adv_data.invoice_id.grand_total_amount:
			partial_payment_amount = invoice_adhoc_obj.browse(cr,uid,inv_adv_data.invoice_id.id).partial_payment_amount
			if partial_payment_amount and partial_payment_amount > 0:
				par_amt = partial_payment_amount + entire_adjustment_amount
			else:
				par_amt = entire_adjustment_amount
			inv_vals.update(
				{
					'status':'open',
					'invoice_paid_date': datetime.now().date(), 
					'pending_amount':round(inv_adv_data.invoice_id.grand_total_amount - entire_adjustment_amount), 
					'partial_payment_amount': par_amt,
					'check_process_invoice': False,

				})
		elif entire_adjustment_amount == inv_adv_data.invoice_id.grand_total_amount:
			inv_vals.update(
				{
					'status': 'paid', 
					'invoice_paid_date': datetime.now().date(),
					'pending_status': 'paid',
					'pending_amount': 0.0, 
					'partial_payment_amount': 0.0,
					'check_process_invoice': True,
				})
		adv_receipt_amount = entire_adjustment_amount
		net_amount_payable = inv_adv_data.invoice_id.grand_total_amount - adv_receipt_amount 
		inv_vals.update(
				{
					'advance_receipts' : advance_receipts,
					'adv_receipt_amount': round(adv_receipt_amount),
					'net_amount_payable': round(net_amount_payable)
				})
		invoice_adhoc_obj.write(cr,uid,inv_adv_data.invoice_id.id,inv_vals)
		res = invoice_adhoc_obj.generate_invoice_main(cr,uid,inv_adv_data.invoice_id.id,context=context)
		
		if res:
			inv_data=invoice_adhoc_obj.browse(cr,uid,int(inv_adv_data.invoice_id.id))
			if advance_list!=[]:
				advance_list=list(set(advance_list))
				for adv in advance_list:
					advance_obj.write(cr,uid,int(adv),{'invoice_number':inv_data.invoice_number,
													   'invoice_date':inv_data.invoice_date,
													   'invoice_amount':inv_data.pending_amount,
													   'cse_char':inv_data.cse_char,
													   'cse':inv_data.cse.id,
													   'tax_rate':inv_data.tax_rate},context=None)
			search_history=self.pool.get('invoice.receipt.history').search(cr,uid,[('invoice_receipt_history_id','=',int(inv_adv_data.invoice_id.id))])
			if search_history!=[]:
				for his in self.pool.get('invoice.receipt.history').browse(cr,uid,search_history):
					self.pool.get('invoice.receipt.history').write(cr,uid,his.id,{'invoice_number':inv_data.invoice_number,'invoice_date':inv_data.invoice_date})
		view = self.pool.get('ir.model.data').get_object_reference(
				cr, uid, 'gst_accounting', 'invoice_adhoc_id_gst_inherit')
		view_id = view and view[1] or False
		return {
				'name': _('Invoice'),
				'view_type': 'form',
				'view_mode': 'form',
				'view_id': view_id or False,
				'res_model': 'invoice.adhoc.master',
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'current',
				'res_id': inv_adv_data.invoice_id.id,
				}

invoice_advance_receipts()


class invoice_advance_receipts_line(osv.osv):
	_name = 'invoice.advance.receipts.line'
	_rec_name = 'receipt_id'

	_columns = {
		# 'receipt_ids':fields.one2many('account.sales.receipts','invoice_advance_id','Advance Sales Receipt'),
		'in_adv_rep_id': fields.many2one('invoice.advance.receipts','Invoice Advance Receipt'),
		'select_receipt_bool': fields.boolean('Select'),
		'receipt_id': fields.many2one('account.sales.receipts','Receipt'),
		'partner_id': fields.many2one('res.partner', 'Customer'),
		'receipt_date': fields.date('Receipt Date'),
		'cse': fields.many2one('hr.employee','CSE'),
		'advance_pending': fields.float('Advance Pending'),
		'invoice_adjustment_amount': fields.float('Adjustment Amount')
	}

invoice_advance_receipts_line()


class invoice_adhoc_receipts(osv.osv):
	_name = 'invoice.adhoc.receipts'
	_rec_name = 'invoice_adhoc_id'

	_columns = {
		'invoice_adhoc_id': fields.integer('Invoice Adhoc'),
		'sales_receipt_id': fields.many2one('account.sales.receipts','Receipt')
	}	

invoice_adhoc_receipts()