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
		   	'get_my_date':self.get_my_date
		})


	def get_branch_addr(self,self_id):
		return get_branch_addr(self,self_id)

	def get_my_date(self, datec):
		d = datetime.strptime(datec, "%Y-%m-%d").strftime("%d/%m/%Y")
		return d

report_sxw.report_sxw('report.service.invoice', 'invoice.adhoc.master', 'PSD_branch/addons_branch/psd_accounting/report/service_invoice.rml', header=False,parser=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

