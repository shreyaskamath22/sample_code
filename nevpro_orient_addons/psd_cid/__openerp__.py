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
    'name': 'PSD CID',
    'version': '1.0',
    'author': 'Orient Technologies',
    'category': 'Request Management',
    'depends': ['base','account','CCC_branch','sales_branch','web_field_style'],
    'data': [
        'security/psd_cid_security.xml',
        'security/ir.model.access.csv',
        'wizard/phone_number_pop_up_view.xml',
        'wizard/complaint_customer_search_view.xml',
        'wizard/complaint_location_addition_view.xml',
        'wizard/product_customer_search_view.xml',
        'wizard/product_request_submit_view.xml',
        'wizard/product_location_customer_search_view.xml',
        'wizard/information_customer_search_view.xml',
        'ccc_branch_view.xml',
        'product_request_view.xml',
        'complaint_request_view.xml',
        'information_request_view.xml',
        'global_search_view.xml',
        'res_partner_view.xml',
        'configuration_view.xml',
        'sequence.xml',
    ],
    'demo': [],
    'description': """
        This is the customized module for request management.
    """,
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
