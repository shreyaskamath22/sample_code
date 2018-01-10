# -*- coding: utf-8 -*-
# inspired from de sale_order.py report

import time

from openerp.report import report_sxw

class sale_offer_sheet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(sale_offer_sheet, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            #'so_name': context.get('so_name') or '',
            #'po_name': context.get('po_name') or '',
        })

report_sxw.report_sxw('report.sale.offer.lead',
                    'sale.offer',
                    'addons/zeeva_customs/reports/sale_offer_lead.rml',
                    parser=sale_offer_sheet,
                    header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

