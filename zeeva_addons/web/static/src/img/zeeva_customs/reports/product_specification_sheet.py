# -*- coding: utf-8 -*-
# inspired from de sale_order.py report

import time

from openerp.report import report_sxw


### Spec Sheet for Sales Orders and Purchase Orders
class product_specification_sheet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(product_specification_sheet, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'so_name': context.get('so_name') or '',
            'po_name': context.get('po_name') or '',
        })

report_sxw.report_sxw('report.product.specification.sheet',
                    'product.product',
                    'addons/zeeva_customs/reports/product_specification_sheet.rml',
                    parser=product_specification_sheet,
                    header="external")

### Spec Sheet for Sales Offer Sheet Leads
class product_specification_sheet_lead(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(product_specification_sheet_lead, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'so_name': context.get('so_name') or '',
            'customer_name': context.get('customer_name') or '',
        })

report_sxw.report_sxw('report.product.specification.sheet.lead',
                    'product.template',
                    'addons/zeeva_customs/reports/product_specification_sheet_lead.rml',
                    parser=product_specification_sheet_lead,
                    header="external")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

