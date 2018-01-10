import time
from datetime import date
from datetime import datetime
from openerp.report import report_sxw
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in


class order(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(order, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'get_branch_addr':self.get_branch_addr,
			'amount_to_text_in': amount_to_text_in,
			'get_serial_no':self.get_serial_no,
			'get_total_amount':self.get_total_amount,
			'get_total_tax':self.get_total_tax,
			'get_my_date':self.get_my_date,
		})


	def get_branch_addr(self,self_id):
		return get_branch_addr(self,self_id)

	# def get_serial_no(self,self_id):
	# 	cr = self.cr
	# 	uid = self.uid
	# 	dic = {
	# 		'serial_name':'',
	# 		'duration':'',
	# 		}
	# 	ser_nm = ''
	# 	for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
	# 		for pay in res.transfer_series_ids:
	# 			if ser_nm == '':
	# 				ser_nm = pay.serial_name
	# 			else:
	# 				ser_nm = ser_nm + ',' +pay.serial_name
	# 			dic['duration'] = pay.duration
	# 		dic['serial_name'] = ser_nm 
	# 		for rec in res.invoice_line_adhoc_11:
	# 			product_desc_search = self.pool.get('product.template').search(cr,uid,[('id','=',rec.pms.product_tmpl_id.id)])
	# 			for desc in self.pool.get('product.template').browse(cr,uid,product_desc_search):
	# 					if desc.product_desc:
	# 						dic['product_desc']=desc.product_desc
	# 	return dic


	def get_serial_no(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = {
			'serial_number':'',
			}
		ser_nm = ''
		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
			for pay in res.product_invoice_lines:
				ser_nm = pay.serial_number
				duration = pay.product_id.warranty_life
				dic['serial_number'] = ser_nm
		return dic

	def get_total_amount(self,self_id):
		cr = self.cr
		uid = self.uid
		dic = {
			'total_amount':0.0,
			}
		total_amount = 0.0
		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
			for line in res.product_invoice_lines:
				total_amount+=line.total_amount
		dic['total_amount'] = format(total_amount,'.2f')
		return dic

	def get_total_tax(self,):
		cr = self.cr
		uid = self.uid
		dic = {
			'total_amount':0.0,
			}
		total_amount = 0.0
		for res in self.pool.get('invoice.adhoc.master').browse(cr,uid,[self_id]):
			for line in res.product_invoice_lines:
				total_amount+=line.total_amount
		dic['total_amount'] = format(total_amount,'.2f')
		return dic

	def get_total_tax(self,total_tax,freight_tax):
		total_tax_amt = total_tax - freight_tax
		total_tax_amt = format(total_tax_amt,'.2f')
		print total_tax_amt,'llll'
		return total_tax_amt

	def get_my_date(self, datec):
		d = datetime.strptime(datec, "%Y-%m-%d").strftime("%d/%m/%Y")
		return d

report_sxw.report_sxw('report.psd.invoice', 'invoice.adhoc.master', 'PSD_branch/addons_branch/psd_accounting/report/psd_print_invoice.rml', header=False,parser=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

