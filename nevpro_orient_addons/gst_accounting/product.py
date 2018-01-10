
from osv import osv,fields

class product_product(osv.osv):
	_inherit = 'product.product'

	_columns = {
		'hsn_code': fields.char('HSN Code',size=8),
	}

product_product()