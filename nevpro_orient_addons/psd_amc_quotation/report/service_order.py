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
from tools.translate import _
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in


class order(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(order, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
		   'get_branch_addr':self.get_branch_addr,
		   'amount_to_text_in': amount_to_text_in,
		   'get_my_date': self.get_my_date,
		   'add_taxes': self.add_taxes
		})


	def get_branch_addr(self,self_id):
		return get_branch_addr(self,self_id)

	def get_my_date(self, datec):
		d = datetime.strptime(datec, "%Y-%m-%d").strftime("%d/%m/%Y")
		return d

	def add_taxes(self,st,sb,kk):
		total_tax = st + sb + kk
		total_tax = format(total_tax,'.2f')
		return total_tax


report_sxw.report_sxw('report.amc.service.order', 'amc.sale.order', 'PSD_branch/addons_branch/psd_amc_quotation/report/service_order.rml', header=False,parser=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

