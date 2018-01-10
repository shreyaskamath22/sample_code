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
    'name': 'Zeeva IND Products Dispatch Process',
    'version': '1.0',
    'category': 'Generic Modules',
    'author': 'Ujwala Pawade <ujwala.erp@zeeva.com>',
    'description': """
Accounts Customization
======================
    """,
    
    'depends': [
        'base','stock','sale','zeeva_ind_sales_order','zeeva_ind_delivery_order'
    ],
    'init_xml': [
    ],
    'update_xml': [
        'security/ir.model.access.csv',
        'dispatch.xml',
		'shipment_dispatch_report.xml',
        'dispatch_details_data.xml',
        'dispatch_sequence.xml',
        'wizard/dispatch_process.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
