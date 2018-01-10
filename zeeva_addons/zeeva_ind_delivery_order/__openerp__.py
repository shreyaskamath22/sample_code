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
    'name': 'ZEEVA IND Delivery Order Modules',
    'version': '1.0',
    'author': 'Shreyas Kamath <shreyas.erp@zeeva.com>',
    'category': 'Zeeva Modules',
    'depends': ['base','web','product','sale','stock','zeeva_ind_sales_order','zeeva_ind_products'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/zeeva_ind_stock_partial_picking_view.xml',
        'delivery_order_details_data.xml',
        'zeeva_ind_stock_sequence.xml',
        'zeeva_ind_delivery_view.xml',
        'zeeva_ind_delivery_report.xml',
    ],
    'css': [],
    'demo': [],
    'description': """
This is the customized module for managing Delivery Order in OpenERP For Zeeva IND.
    """,
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
