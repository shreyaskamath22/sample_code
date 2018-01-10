#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.osv import fields, orm
from datetime import timedelta
import datetime
from datetime import datetime
from time import strftime
from datetime import date
from dateutil.relativedelta import relativedelta

LEAVE_ENCASHED = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

REASON_SELECTION = [
    ('better prospects','Better Prospects'),
    ('health concerns', 'Health Concerns'),
]

class hr_employee(orm.Model):
    _inherit = 'hr.employee'


    def _calculate_tenure_days(self, cr, uid, ids, join_date, relieving_date, arg, context=None):
        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):
            emp_name = ee.name
            emp_status = ee.active
            emp_identification_id = ee.identification_id
            print ee.active, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 
#             print ee.relieving_date, 'fffffffffffffffffffffffffffffffffffffffff'
            if ee.active == False:
                if ee.join_date and ee.relieving_date :
                    date_dt= datetime.strptime(ee.join_date, "%Y-%m-%d").date()
                    date_lt= datetime.strptime(ee.relieving_date, "%Y-%m-%d").date()
                    today = datetime.today().date()
                    tenure = relativedelta(date_lt, date_dt)
                    if tenure.years == 0:
                        res[ee.id] = "{0.months} month(s) {0.days} days ".format(tenure)
                    else:
                        res[ee.id] = "{0.years} years {0.months} month(s) {0.days} days ".format(tenure)
            else:
                if ee.join_date:
                    date_dt= datetime.strptime(ee.join_date, "%Y-%m-%d").date()
                    today = datetime.today().date()
                    tenure = relativedelta(today, date_dt)
                    if tenure.years == 0:
                        res[ee.id] = "{0.months} month(s) {0.days} days ".format(tenure)
                    else:
                        res[ee.id] = "{0.years} years {0.months} month(s) {0.days} days ".format(tenure)
            search_emp_record = self.pool.get('hr.employee').search(cr,uid,[('name','=',emp_name),('identification_id','=',emp_identification_id)], context=context)
            self.write(cr, uid, search_emp_record, {'tenure_till_date': res})
            print 'tenureeeeeeeeeeeeeeeeeeeeeee', res
        return res
	

    _columns = {
        'resignation_letter_date': fields.date('Resignation Letter Date', help="Date of Resignation."),
        'relieving_date': fields.date('Relieving Date'),
		'tenure_till_date': fields.function(_calculate_tenure_days, type='char', method=True, string = 'Tenure'),
        'reason_for_leaving': fields.char('Reason For Leaving'),
        'leave_encashed': fields.selection(LEAVE_ENCASHED, 'Leave Encashed'),
        'encashment_date': fields.date('Encashment Date'),
        'held_on_date': fields.date('Held On Date'),
        'reason_for_resignation': fields.selection(REASON_SELECTION, 'Reason For Resignation'),
        'new_workplace': fields.char('New Workplace'),
        'feedback': fields.text('Feedback'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),

    }
