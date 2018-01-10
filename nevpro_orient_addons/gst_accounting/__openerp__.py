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
    'name': 'GST Accounting',
    'version': '1.0',
    'author': 'Orient Technologies',
    'category': 'Accounting',
    'depends': ['base','CCC_branch','account','sales_branch','account_sales_branch','sequence_update'],
    'data': [
        'security/gst_security.xml',
        'security/ir.model.access.csv',
        'acc_report.xml',
        # 'product_view.xml',
        'account_view.xml',
        'customer_request_view.xml',
        'res_partner_view.xml',
        'gst_sale_contract_view.xml',
        'sales_receipts_view.xml',
        'invoice_advance_receipts_view.xml',
        'invoice_adhoc_view.xml',
        'credit_note_view.xml',
        'credit_note_st_view.xml',
        'debit_note_view.xml',
        'cash_payment_view.xml',
        'payment_view.xml',
        'campaign_master.xml',
        'data.xml',
        'scrap_sale_invoice_view.xml',
        'purchase_rcm_view.xml',
        'other_payment_view.xml',
        'service_classification_view.xml',
        'ncs_sync_view.xml',
        'nature_view.xml'
        # 'import_job_csv_view.xml',
    ],
    'demo': [],
    'description': """This is the customized module for GST accounting.""",
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
