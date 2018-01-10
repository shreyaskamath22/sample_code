
from datetime import date,datetime, timedelta
from osv import osv,fields

class service_classification(osv.osv):
	_name = 'service.classification'
	_columns = {
		'name':fields.char('Service Classification',size=100),
		'active': fields.boolean('Active?')
	}

service_classification()