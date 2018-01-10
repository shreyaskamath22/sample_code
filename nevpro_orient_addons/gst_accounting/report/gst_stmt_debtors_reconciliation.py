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
from report import report_sxw
from tools.translate import _
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in
from corporate_address import *

class gst_statement_debtors_reconciliation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(gst_statement_debtors_reconciliation, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'amount_to_text_in': amount_to_text_in,
            'get_branch_addr':self.get_branch_addr,
            'convert_to_double_precision':convert_to_double_precision,
            'get_current_time':self.get_current_time,
            'dr_cr_sign':self.dr_cr_sign,
        })

    def get_branch_addr(self,self_id):
        return get_branch_addr(self,self_id)
    
    def get_current_time(self):
        return get_current_time(self)

    def dr_cr_sign(self,amount):
        if amount > 0.0: 
                return str("%.2f" % abs(amount))+' Dr'
        elif amount < 0.0 :
                return str("%.2f" % abs(amount))+' Cr'
        
                
report_sxw.report_sxw('report.gst_statement_debtors_reconciliation', 'monthly.report', '/gst_accounting/report/gst_stmt_debtors_reconciliation.rml', parser=gst_statement_debtors_reconciliation, header="False")

