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
{
    'name' : 'eInvoicing',
    'version' : '1.1',
    'author' : 'OpenERP SA',
    'category' : 'Accounting & Finance',
    'description' : """
Accounting and Financial Management.
====================================

Financial and accounting module that covers:
--------------------------------------------
    * General Accounting
    * Cost/Analytic accounting
    * Third party accounting
    * Taxes management
    * Budgets
    * Customer and Supplier Invoices
    * Bank statements
    * Reconciliation process by partner

Creates a dashboard for accountants that includes:
--------------------------------------------------
    * List of Customer Invoice to Approve
    * Company Analysis
    * Graph of Treasury

The processes like maintaining of general ledger is done through the defined financial Journals (entry move line orgrouping is maintained through journal) 
for a particular financial year and for preparation of vouchers there is a module named account_voucher.
    """,
    'website': 'http://www.openerp.com',
    'images' : [],
    'depends' : ['account','zeeva_ind_dispatch_process'],
    'data': [
        'account_invoice.xml',
        'account_report.xml',
        # 'zeeva_ind_invoice_sequence.xml',
        
    ],
    
   
    'installable': True,
    'auto_install': False,
    'css': ['static/src/css/invoice.css']
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
