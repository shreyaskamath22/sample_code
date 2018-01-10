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

from osv import osv,fields

class account_tax(osv.osv):
	_inherit = 'account.tax'

	_columns = {
		'select_tax_type':fields.selection([
			('service_tax','Service Tax'),
			('edu_cess','Edu Cess'),
			('hs_edu_cess','Hs Edu Cess'),
			('swachh_bharat_service','SB Cess'),
			('krishi_kalyan_service','KK Cess'),
			('cgst','CGST'),
			('sgst','SGST'),
			('utgst','UTGST'),
			('igst','IGST'),
			('cess','CESS')
			], 'Tax Type'),
	}

account_tax()

