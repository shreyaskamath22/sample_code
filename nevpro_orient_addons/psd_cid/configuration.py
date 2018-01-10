from osv import osv,fields

class request_counter(osv.osv):
	_name ='request.counter'

	_columns = {
	    'product_request_counter': fields.integer('Product Request Counter'),
	    'complaint_request_counter': fields.integer('Complaint Request Counter'),
	    'information_request_counter': fields.integer('Information Request Counter')
	}

	_defaults = {
		'product_request_counter': 999,
		'complaint_request_counter': 999,
		'information_request_counter': 999,
	}

request_counter()

class information_request_types(osv.osv):
	_name ='information.request.types'

	_columns = {
	    'name': fields.char('Request Type',size=150)
	}

information_request_types()
