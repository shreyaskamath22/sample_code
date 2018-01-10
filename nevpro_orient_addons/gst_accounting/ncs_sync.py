from osv import osv,fields
import time
import decimal_precision as dp
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from urllib import urlopen
import math
import calendar
import datetime as dt
import xmlrpclib
from python_code.dateconversion import *
import python_code.dateconversion as py_date
import re
from lxml import etree
import time
import os
from openerp.osv.orm import setup_modifiers


class sale_contract(osv.osv):
	_inherit = 'sale.contract'
	_columns = {
		'contract_number_ncs': fields.char('Contract Number NCS', size=100)
	}
sale_contract()


class account_journal_voucher(osv.osv):
	_inherit = 'account.journal.voucher'
	_columns = {
		'sr_no_ncs': fields.char('Receipt Number NCS', size=100),
		'from_ncs': fields.boolean('From NCS?'),
	}

account_journal_voucher()