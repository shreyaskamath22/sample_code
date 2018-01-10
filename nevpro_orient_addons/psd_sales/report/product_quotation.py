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

import time
from datetime import date
from datetime import datetime
from openerp.report import report_sxw

class psd_sales_product_quotation(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(psd_sales_product_quotation, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'get_my_date': self.get_my_date,
			'get_rate':self.get_rate,
			# 'counter':self.no_of_products
		})

	def get_my_date(self, datec):
		d = datetime.strptime(datec, "%Y-%m-%d").strftime("%d %B,%Y")
		return d


	def get_rate(self,rate):
		rate_v=''
		if rate:
			print format(rate,'.2f')
			rate_v=format(rate,'.2f')
		return rate_v

		
	# def no_of_products(self,):
	# 	count=0
	# 	for sum1 in self.pool.get(psd.sales.product.quotation).browse(cr,uid,):
	# 		count++;
	# 	return count;


report_sxw.report_sxw('report.Sales Quotation', 'psd.sales.product.quotation', 'PSD_branch/addons_branch/psd_sales/report/product_quotation.rml', parser=psd_sales_product_quotation, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

