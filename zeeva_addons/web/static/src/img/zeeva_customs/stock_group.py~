# -*- coding: utf-8 -*-

from osv import fields,osv
import tools
import pooler
from tools.translate import _

#from datetime import datetime,date
from openerp import netsvc
from openerp.tools.amount_to_text_en import amount_to_text
import math
import openerp.addons.decimal_precision as dp


#class stock_group(osv.osv):

    #_description = 'Group partial deliveries'
    #_name = "stock.group"

    #_order = ""
    
    #_columns = {
        
    #}
    
    #_defaults = {
        
    #}

#stock_group()


class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit = 'stock.picking'
    
    def _amount_in_words(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            temp_text = amount_to_text(picking.nb_carton)
            cut = temp_text.find('euro')
            temp_text = temp_text[0:cut]
            temp_text += 'Cartons Only'
            res[picking.id] = temp_text
        return res
    
    _columns = {
        'zeeva_sale_ids': fields.many2many('sale.order', 'sale_order_picking_out_rel', 'picking_id', 'sale_id', 'Related Sales Confirmations',
            help="This is a list of sales orders that has been at the origin of this packing list."),
            
        'invoice_id': fields.many2one('account.invoice', 'Invoice No.'),
        'ship_date': fields.date('Ship Date'),
        'port_of_loading': fields.many2one('stock.port', 'Port of Loading'),
        'port_of_discharge': fields.many2one('stock.port', 'Port of Discharge'),
        'vessel_name': fields.char('Vessel/Freight', size=64, translate=False),
        
        'total_qty': fields.integer('Total number of product'),
        'nb_carton': fields.integer('Total number of carton'),
        'nb_carton_in_words': fields.function(_amount_in_words, string='Number of cartons in words', type='char', size=128),
        'gross_weight': fields.float('Total gross weight', digits_compute=dp.get_precision('Stock Weight')),
        'net_weight': fields.float('Total net weight', digits_compute=dp.get_precision('Stock Weight')),
        'volume_cbm': fields.float('Total volume CBM', digits_compute=dp.get_precision('Product Volume')),
        'volume_cuft': fields.float('Total volume CUFT', digits_compute=dp.get_precision('Product Volume')),
        
        'use_cuft': fields.boolean('Print Volume CUFT'),
    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if view_type == 'form': #and not view_id:
            mod_obj = self.pool.get('ir.model.data')
            if self._name == "stock.picking.in":
                model, view_id = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_in_form')
            if self._name == "stock.picking.out":
                model, view_id = mod_obj.get_object_reference(cr, uid, 'zeeva_customs', 'zeeva_view_picking_out_form')
        return super(stock_picking, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        comment = self._get_comment_invoice(cr, uid, picking)
        invoice_vals = {
            'name': picking.name,
            'picking_id': picking.id,
            'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
            'type': inv_type,
            'account_id': account_id,
            'partner_id': partner.id,
            'comment': comment,
            'payment_term': payment_term,
            'fiscal_position': partner.property_account_position.id,
            'date_invoice': context.get('date_inv', False),
            'company_id': picking.company_id.id,
            'user_id': uid,
        }
        cur_id = self.get_currency_id(cr, uid, picking)
        if cur_id:
            invoice_vals['currency_id'] = cur_id
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        return invoice_vals
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        if group:
            name = (picking.name or '') + '-' + move_line.name
        else:
            name = move_line.name
        origin = move_line.picking_id.name or ''
        if move_line.picking_id.origin:
            origin += ':' + move_line.picking_id.origin

        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
        else:
            account_id = move_line.product_id.property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_expense_categ.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move_line.product_uos and move_line.product_uos.id or False
        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            uos_id = move_line.product_uom.id

        var_name = ''
        if move_line.product_id:
            var_name = '[' + move_line.product_id.default_code + '] '+ move_line.product_id.name
            
            if move_line.product_id.variants:
                var_name += ' - ' + move_line.product_id.variants
                    
        return {
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
            'move_id': move_line.id,
            'uos_id': uos_id,
            'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity': move_line.product_uos_qty or move_line.product_qty,
            'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
            'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
        }
        
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        #picking_obj = self.pool.get('stock.picking')
        
        res = super(stock_picking,self).action_invoice_create( cr, uid, ids, journal_id=journal_id, group=group, type=type, context=context)
        #for order in self.browse(cr, uid, ids, context=context):
            #if order.order_policy == 'picking':
                #picking_obj.write(cr, uid, map(lambda x: x.id, order.picking_ids), {'invoice_state': 'invoiced'})
        print res
        print ids
        return res
        
    #def action_invoice_create(self, cr, uid, ids, journal_id=False,
            #group=False, type='out_invoice', context=None):
        #""" Creates invoice based on the invoice state selected for picking.
        #@param journal_id: Id of journal
        #@param group: Whether to create a group invoice or not
        #@param type: Type invoice to be created
        #@return: Ids of created invoices for the pickings
        #"""
        #if context is None:
            #context = {}

        #invoice_obj = self.pool.get('account.invoice')
        #invoice_line_obj = self.pool.get('account.invoice.line')
        #partner_obj = self.pool.get('res.partner')
        #invoices_group = {}
        #res = {}
        #inv_type = type
        #for picking in self.browse(cr, uid, ids, context=context):
            #if picking.invoice_state != '2binvoiced':
                #continue
            #partner = self._get_partner_to_invoice(cr, uid, picking, context=context)
            #if isinstance(partner, int):
                #partner = partner_obj.browse(cr, uid, [partner], context=context)[0]
            #if not partner:
                #raise osv.except_osv(_('Error, no partner!'),
                    #_('Please put a partner on the picking list if you want to generate invoice.'))

            #if not inv_type:
                #inv_type = self._get_invoice_type(picking)

            #if group and partner.id in invoices_group:
                #invoice_id = invoices_group[partner.id]
                #invoice = invoice_obj.browse(cr, uid, invoice_id)
                #invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
                #invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
            #else:
                #invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
                #invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                #invoices_group[partner.id] = invoice_id
            #res[picking.id] = invoice_id
            #for move_line in picking.move_lines:
                #if move_line.state == 'cancel':
                    #continue
                #if move_line.scrapped:
                    ## do no invoice scrapped products
                    #continue
                #vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
                                #invoice_id, invoice_vals, context=context)
                #if vals:
                    #invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
                    #self._invoice_line_hook(cr, uid, move_line, invoice_line_id)

            #invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    #set_total=(inv_type in ('in_invoice', 'in_refund')))
            #self.write(cr, uid, [picking.id], {
                #'invoice_state': 'invoiced',
                #}, context=context)
            #self._invoice_hook(cr, uid, picking, invoice_id)
        #self.write(cr, uid, res.keys(), {
            #'invoice_state': 'invoiced',
            #}, context=context)
        #return res
    
stock_picking()

class stock_picking_out(osv.osv):
    _name = "stock.picking.out"
    _inherit = ["stock.picking","stock.picking.out"]
    _table = "stock_picking"
    
    _columns = {
        
    }
    
    def force_invoice(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        
        for picking in self.browse(cr, uid, ids, context=context):
            picking.write({'invoice_state': '2binvoiced'})
            
        return True
    
    def compute_lines(self, cr, uid, ids, context=None):
        if not context:
            context = {}
                    
        for picking in self.browse(cr, uid, ids, context=context):
            
            for move in picking.move_lines:
                if not move.pack_export:
                    raise osv.except_osv(_('Warning for product %s' % move.product_id.default_code), _("No quantity per export carton defined!" ))
                    return True
                    
                nb_carton = math.ceil(move.product_qty / move.pack_export)
                net_weight = move.export_net * nb_carton
                gross_weight = move.export_gross * nb_carton
                volume_cbm = move.export_cbm * nb_carton
                volume_cuft = move.export_cuft * nb_carton
                
                move.write({'nb_carton': nb_carton,
                            'net_weight': net_weight,
                            'gross_weight': gross_weight,
                            'volume_cbm': volume_cbm,
                            'volume_cuft': volume_cuft})
                            
        return True
    
    def compute_totals(self, cr, uid, ids, context=None):
        if not context:
            context = {}
                    
        for picking in self.browse(cr, uid, ids, context=context):
            total_qty = 0
            nb_carton = 0
            net_weight = 0.0
            gross_weight = 0.0
            volume_cbm = 0.0
            volume_cuft = 0.0
            
            for move in picking.move_lines:
                total_qty += move.product_qty
                nb_carton += move.nb_carton
                net_weight += move.net_weight
                gross_weight += move.gross_weight
                volume_cbm += move.volume_cbm
                volume_cuft += move.volume_cuft
                
            picking.write({ 'total_qty': total_qty,
                            'nb_carton': nb_carton,
                            'net_weight': net_weight,
                            'gross_weight': gross_weight,
                            'volume_cbm': volume_cbm,
                            'volume_cuft': volume_cuft})
                            
        return True
        
stock_picking_out()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    _columns = {
        'name': fields.char('Description', required=False, select=True),
        
        'sc_origin': fields.char('SC Origin', size=128),
        
        #'exp_nb_carton': fields.related('Number of cartons'),
        #'exp_gross_weight': fields.float('Gross Weight'),
        #'exp_net_weight': fields.float('Net Weight'),
        #'exp_volume': fields.float('Volume'),
        
        'export_l': fields.related('product_id','export_l', string='Export Carton Length', type='float'),
        'export_w': fields.related('product_id','export_w', string='Export Carton Width', type='float'),
        'export_h': fields.related('product_id','export_h', string='Export Carton Height', type='float'),
        'export_gross': fields.related('product_id','export_gross', string='Export Carton Gross Weight', type='float', digits_compute=dp.get_precision('Stock Weight')),
        'export_net': fields.related('product_id','export_net', string='Export Carton Net Weight', type='float', digits_compute=dp.get_precision('Stock Weight')),
        'export_cbm': fields.related('product_id','export_cbm', string='Export Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'export_cuft': fields.related('product_id','export_cuft', string='Export Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),
        'pack_export': fields.related('product_id','pack_export', string='Export Carton Unit/ctn', type='integer'),
        'pack_export_barcode': fields.related('product_id','pack_export_barcode', string='Export Carton Barcode', type='char'),
        
        'nb_carton': fields.integer('Number of cartons'),
        'gross_weight': fields.float('Gross Weight', digits_compute=dp.get_precision('Stock Weight')),
        'net_weight': fields.float('Net Weight', digits_compute=dp.get_precision('Stock Weight')),
        'volume_cbm': fields.float('Volume CBM', digits_compute=dp.get_precision('Product Volume')),
        'volume_cuft': fields.float('Volume CUFT', digits_compute=dp.get_precision('Product Volume')),
    }
    
    #def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        #if view_type == 'form' and not view_id:
            #mod_obj = self.pool.get('ir.model.data')
            #if self._name == "stock.move":
                #model, view_id = mod_obj.get_object_reference(cr, uid, 'stock', 'view_move_picking_form')
        #return super(stock_move, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
    
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        #print 'COUCOU', partial_datas
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s'%(move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s.') % (move.id)
            product_qty = partial_data.get('product_qty',0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom',False)
            product_price = partial_data.get('product_price',0.0)
            product_currency = partial_data.get('product_currency',False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            
            ###
            new_picking_id = partial_data.get('new_picking_id')
            ###
            
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                product = product_obj.browse(cr, uid, move.product_id.id)
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                if qty > 0:
                    new_price = currency_obj.compute(cr, uid, product_currency,
                            move_currency_id, product_price)
                    new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                            product.uom_id.id)
                    if product.qty_available <= 0:
                        new_std_price = new_price
                    else:
                        # Get the standard price
                        amount_unit = product.price_get('standard_price', context=context)[product.id]
                        new_std_price = ((amount_unit * product.qty_available)\
                            + (new_price * qty))/(product.qty_available + qty)

                    product_obj.write(cr, uid, [product.id],{'standard_price': new_std_price})

                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    self.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency,
                                })

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty,
                            #'picking_id' : move.picking_id.id,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            
                            ###
                            #'picking_id': new_picking_id or move.picking_id.id,
                            ###
                            
                            }
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty - product_qty,
                        'product_uos_qty': move.product_qty - product_qty,
                        'prodlot_id': False,
                        'tracking_id': False,
                    })


        for move in too_many:
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty,
                        'product_uos_qty': move.product_qty,
                        
                        #'picking_id': new_picking_id or move.picking_id.id,
                    })
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id],{'prodlot_id': prodlot_ids.get(move.id)})
            if new_picking_id: #assign the move to another picking
                print move
                self.write(cr, uid, [move.id],{'picking_id': new_picking_id, 'sc_origin': move.picking_id.origin + ' > ' + move.picking_id.name})
            #self.action_done(cr, uid, [move.id], context=context)
            
            #save in the rel table
            picking_obj.write(cr,uid,new_picking_id,{'zeeva_sale_ids':[(4,move.sale_line_id.order_id.id)]})
            
            if  move.picking_id.id :
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""",
                            ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking', move.picking_id.id, 'button_done', cr)

        return [move.id for move in complete]

stock_move()


class stock_partial_move(osv.osv_memory):
    _inherit = 'stock.partial.move'
    _columns = {
        
     }

    def do_partial(self, cr, uid, ids, context=None):
        # no call to super!
        assert len(ids) == 1, 'Partial move processing may only be done one form at a time.'
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date' : partial.date
        }
        moves_ids = []
        for move in partial.move_ids:
            if not move.move_id:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            move_id = move.move_id.id
            partial_data['move%s' % (move_id)] = {
                'product_id': move.product_id.id,
                'product_qty': move.quantity,
                'product_uom': move.product_uom.id,
                'prodlot_id': move.prodlot_id.id,
                'new_picking_id': partial.picking_id.id,
            }
            moves_ids.append(move_id)
            if (move.move_id.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                partial_data['move%s' % (move_id)].update(product_price=move.cost,
                                                          product_currency=move.currency.id)
        self.pool.get('stock.move').do_partial(cr, uid, moves_ids, partial_data, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

