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
    'name': 'ZEEVA IND Customer Module(CRF)',
    'version': '1.0',
    'author': 'OpenERP SA',
    'category': 'Zeeva Modules',
    'depends': ['base','email_template','mail','product','zeeva_ind_products','hr','hr_emergency_details','zeeva_hr','crm','sale'],
    'data': [
        'security/ir.model.access.csv',
        'zeeva_ind_res_partner_sequence.xml',
        'zeeva_ind_res_partner_view.xml',
    ],
    'css': ['static/src/css/base_css.css'],
    'demo': [],
    'description': """
This is the customized module for managing The Customer Details in OpenERP For Zeeva IND.
    """,
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: