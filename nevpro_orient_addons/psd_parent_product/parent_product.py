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

from osv import fields,osv
import tools
import pooler
import time
from tools.translate import _
import csv

class location_type(osv.osv):
	_name="location.type"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'name': fields.char('Name',size=100),
	}

	_defaults = {
		'company_id': _get_company
	}

location_type()

# class product_group(osv.osv):
#     _name="product.group"
#     _columns = {
#         'name': fields.char('Name',size=100),
#         'product_group_id': fields.one2many('product.group.line','product_line_id','Product Line'),
#     }

# product_group()

class product_generic_name(osv.osv):
	_inherit="product.generic.name"
	_columns={
		'name': fields.char('Generic Name', size=128, required=True, translate=True, select=True),
		'sold_by_psd':fields.boolean('Exclusively Sold by PSD',select=True),
		'amc_product':fields.boolean('AMC Product',select=True),
		'product_group_id': fields.one2many('product.group.line','product_generic_line_id','Product Line'),
		'is_imported':fields.boolean('Imported'),
	}

product_generic_name()


class product_group_line(osv.osv):
	_name="product.group.line"

	def _get_company(self, cr, uid, context=None):
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	def get_precision_tax():
		def change_digit_tax(cr):
			res = pooler.get_pool(cr.dbname).get('decimal.precision').precision_get(cr, 1, 'Account')
			return (16, res+2)
		return change_digit_tax

	_columns = {
		'company_id':fields.many2one('res.company','Company ID'),
		'location_id': fields.many2one('location.type','Location'),
		'tax_name': fields.many2one('account.tax','Tax Name',domain="['|',('description','=','vat'),('description','=','cst'),('active','=',True)]"),
		'name':fields.char('Name',size=100),
		'tax_rate': fields.float('Tax Rate',digits_compute=get_precision_tax()),
		'product_generic_line_id':fields.many2one('product.generic.name','Product Line'),
	}

	_defaults = {
		'company_id': _get_company
	}

	def onchange_tax_name(self,cr,uid,ids,tax_name):
		v={'name':False}
		if tax_name:
			tax_browse_id = self.pool.get('account.tax').browse(cr,uid,tax_name)
			v['tax_rate'] = tax_browse_id.amount
			v['name'] = tax_browse_id.name
		return {'value': v}

product_group_line()

# class product_product(osv.osv):
# 	_inherit="product.product"
# 	_columns={
# 		'sold_by_psd':fields.boolean('Exclusively Sold by PSD'),
#         'product_line_id':fields.many2one('product.group','Product Group'),
# 	}

# product_product()
