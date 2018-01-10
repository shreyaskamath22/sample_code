from osv import osv,fields
from datetime import datetime

class res_company(osv.osv):
	_inherit = 'res.company'

	_columns = {
		'establishment_type': fields.selection([
												('branch', 'Branch'), 
												('base', 'Base'),
												('site', 'Site'), 
												('cost', 'Cost Center'),
												('camp', 'Camp'), 
												('dept', 'Dept'),
												('factory', 'Factory'), 
												('nsd', 'NSD'), 
												('office', 'Office'),
												('r&d', 'R&D'), 
												('rsd', 'RSD'), 
												('tr_center', 'Tr. Center'),
												('psd','PSD'),
												('crm','CRM')], "Establishment Type"), 
	}

	# update res_company set establishment_type='psd' where name ilike 'PSD%'
	# update res_company set establishment_type='crm' where name='CRM'

res_company()