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
    'name': 'PSD Product Configuration',
    'version': '1.0',
    'author': 'Orient Technologies',
    'category': 'Product Configuration',
    'depends': ['base','sk','product'],
    'data': [
        #'security/ir.model.access.csv',
        'parent_product_view.xml',
    ],
    'demo': [],
    'description': """
This is the customized module for Produuct Configuration in OpenERP For All Database.
    """,
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
