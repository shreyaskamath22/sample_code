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
from tools.translate import _


class credit_note_invoice_pop_up(osv.osv_memory):
	_name = 'credit.note.invoice.pop.up'

	_columns = {
		'name': fields.char('Name',size=50),
		'credit_note_inv_ids':fields.one2many('credit.note.invoice.master','credit_invoice_popup_id','Invoice Lines'),
	}

	_defaults = {
		'name': 'Credit Note Invoice pop-up'
	}


	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		active_ids = context.get('active_ids')
		active_model = context.get('active_model')
		adhoc_master_obj = self.pool.get('invoice.adhoc.master')
		adhoc_line_obj = self.pool.get('invoice.adhoc')
		res = super(credit_note_invoice_pop_up, self).default_get(cr, uid, fields, context=context)
		picking_ids = context.get('active_ids', [])
		if not picking_ids or (not context.get('active_model') == 'invoice.adhoc.master') or len(picking_ids) != 1:
			return res
		picking_id, = picking_ids	
		credit_note_invs = []
		adhoc_master_data = adhoc_master_obj.browse(cr, uid, active_ids[0])
		if adhoc_master_data.product_invoice_lines:
			invoice_lines = adhoc_master_data.product_invoice_lines
		elif adhoc_master_data.service_invoice_lines:
			invoice_lines =  adhoc_master_data.service_invoice_lines
		for invoice_line in invoice_lines:
			adhoc_line_data = adhoc_line_obj.browse(cr, uid, invoice_line.id)
			credit_note_inv_id = {
					'product_id': adhoc_line_data.product_id.id,
					'ordered_quantity': adhoc_line_data.ordered_quantity,
					'product_uom': adhoc_line_data.product_uom.id,
					'batch_id': adhoc_line_data.batch.id, 
					'rate': adhoc_line_data.rate, 
					'discount_amount': adhoc_line_data.discounted_amount, 
					'tax_amount': adhoc_line_data.tax_amount, 
					'total_amount': adhoc_line_data.total_amount, 
					# 'credit_invoice_popup_id': rec.credit_invoice_id.id
				}
			credit_note_invs.append(credit_note_inv_id)
			if 'credit_note_inv_ids' in fields:
				picking = self.pool.get('credit.note.invoice.master').browse(cr, uid, picking_id, context=context)
				moves = [self._partial_move_for(cr, uid, m) for m in credit_note_invs]
				res.update(credit_note_inv_ids=moves)
		return res

	def _partial_move_for(self, cr, uid, move):
		product_id = move.get('product_id')
		ordered_quantity = move.get('ordered_quantity')
		product_uom = move.get('product_uom')
		batch_id = move.get('batch_id')
		rate = move.get('rate')
		discount_amount = move.get('discount_amount')
		tax_amount = move.get('tax_amount')
		total_amount = move.get('total_amount')
		partial_move = {
			'product_id': product_id,
			'ordered_quantity' : ordered_quantity,
			'product_uom' : product_uom,
			'batch_id': batch_id,
			'rate' : rate,
			'discount_amount': discount_amount,
			'tax_amount': tax_amount,
			'total_amount' : total_amount,
			# credit_invoice_popup_id
		}
		return partial_move


	def action_confirm_write_off(self,cr,uid,ids,context=None):
		rec = self.browse(cr, uid, ids[0])	
		final_refund_amount = 0
		batch_quantity_ids = []
		credit_note_line_obj = self.pool.get('credit.note.line')
		batch_quanity_obj = self.pool.get('credit.invoice.batch.quantity')
		adhoc_master_obj = self.pool.get('invoice.adhoc.master')
		if context.get('credit_note_line_id'):
			credit_note_line_id = context.get('credit_note_line_id')
		adhoc_master_ids = adhoc_master_obj.search(cr, uid, [('check_credit_note','=',True),('credit_invoice_id','=',credit_note_line_id)], context=context)	
		for credit_note_inv_id in rec.credit_note_inv_ids:
			refund_amount = credit_note_inv_id.refund_amount
			if refund_amount > credit_note_inv_id.total_amount:
				raise osv.except_osv(_('Warning!'),_("Refund amount not to be exceeded by total amount!"))
			if credit_note_inv_id.refund_quantity > credit_note_inv_id.ordered_quantity:
				raise osv.except_osv(_('Warning!'),_("Refund quantity not to be exceeded by ordered quantity!"))
			final_refund_amount = final_refund_amount + refund_amount
			if credit_note_inv_id.batch_id:
				batch_id = credit_note_inv_id.batch_id.id
				quantity = credit_note_inv_id.refund_quantity
				batch_quantity_id = batch_quanity_obj.create(cr, uid, {'batch_id':batch_id,'quantity':quantity}, context=context)
				batch_quantity_ids.append(batch_quantity_id)
		adhoc_master_obj.write(cr, uid, adhoc_master_ids[0], {
			'writeoff_amount': final_refund_amount,
			'credit_inv_batch_id': [(6, 0, batch_quantity_ids)]}, context=context)
		view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'psd_accounting', 'psd_account_credit_against_ref_form')
		view_id = view and view[1] or False
		return {
			'name': _('Outstanding Invoice'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id,
			'res_model': 'credit.note.line',
			'res_id': credit_note_line_id,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'context': context,                               
		}  

credit_note_invoice_pop_up()


class credit_note_invoice_master(osv.osv_memory):
	_name = 'credit.note.invoice.master'

	_columns = {
		'name': fields.char('Name',size=50),
		'product_id': fields.many2one('product.product', 'Product'),
		'ordered_quantity': fields.integer('Ordered Quantity'),
		'product_uom': fields.many2one('product.uom','UOM'),
		'batch_id': fields.many2one('res.batchnumber','Batch'),
		'rate': fields.float('Rate'),
		'discount_amount': fields.float('Discount Amount'),	
		'tax_amount': fields.float('Tax Amount'),	
		'total_amount': fields.float('Total Amount'),	
		'refund_quantity': fields.integer('Refund Quantity'),
		'refund_amount': fields.float('Refund Amount'),
		'credit_invoice_popup_id': fields.many2one('credit.note.invoice.pop.up', 'Credit Inovice Pop-Up'),
	}

	_defaults = {
		'name': 'Credit Note Invoice pop-up'
	}

credit_note_invoice_master()

class credit_invoice_batch_quantity(osv.osv):
	_name = 'credit.invoice.batch.quantity'

	_columns = {
		'quantity': fields.integer('Quantity'),
		'batch_id': fields.many2one('res.batchnumber','Batch'),
		'invoice_adhoc_id': fields.many2one('invoice.adhoc.master', 'Inovice Adhoc Master'),
	}

credit_invoice_batch_quantity()


