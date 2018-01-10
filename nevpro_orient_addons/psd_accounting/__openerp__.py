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
    'name': 'PSD Accounting',
    'version': '1.0',
    'author': 'Orient Technologies',
    'category': 'Accounting',
    'depends': ['base','account_sales_branch','psd_operations'],
    'data': [
        'security/ir.model.access.csv',
        'psd_configuration_view.xml',
        'psd_reporting_view.xml',
        'psd_account_book_view.xml',
        'psd_account_report.xml',
        'psd_payment_view.xml',
        'psd_contra_view.xml',
        'psd_import_view.xml',
        'psd_journal_voucher_view.xml',
        'psd_credit_note_view.xml',
        'psd_debit_note_view.xml',
        'psd_sales_receipts_view.xml',
        'psd_account_view.xml',
        'search_service_invoice_view.xml',
        'psd_service_invoice_view.xml',
        'invoice_sequence.xml',
        'psd_credit_note_invoice_master_view.xml'
    ],
    'demo': [],
    'description': """This is the customized module for Accounting in OpenERP For All Database.""",
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
