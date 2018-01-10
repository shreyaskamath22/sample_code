from osv import fields,osv

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
##################adding operation id details###################3
        'sale_quotation_id':fields.char('Sale Quotation Id',size=20),
        'sale_order_id':fields.char('Sale Order Id',size=20),
        'service_quotation_id':fields.char('Service Quotation Id',size=20),
        'service_order_id': fields.char('Service Order ID',size=20),
        'product_invoice_id':fields.char('Product Invoice Id',size=20),
        'service_invoice_id': fields.char('Service Invoice ID',size=20),
        'composite_invoice_id': fields.char('Composite Invoice ID',size=20),
    }

    _defaults = {
        'sale_quotation_id':'PQ',
        'sale_order_id':'SO',
        'service_quotation_id':'SQ',
        'service_order_id':'SS',
        'product_invoice_id':'VAT',
        'service_invoice_id':'ST',
        'composite_invoice_id':'BP',
    }

res_company()

