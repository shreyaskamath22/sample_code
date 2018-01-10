from osv import osv,fields

class request_search_sales(osv.osv):
	_name = 'request.search.sales'

request_search_sales()

class psd_sales_product_quotation(osv.osv):
	_name = 'psd.sales.product.quotation'

psd_sales_product_quotation()


class psd_sales_product_order(osv.osv):
	_name = 'psd.sales.product.order'

psd_sales_product_order()

class amc_quotation(osv.osv):
	_name = 'amc.quotation'

amc_quotation()
