
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from datetime import timedelta
import datetime
from datetime import datetime
from time import strftime
from datetime import date
from dateutil.relativedelta import relativedelta
from openerp.osv.fields import _column


class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = ["hr.employee","mail.thread"]
    
    def _calculate_tenure(self, cr, uid, ids, join_date, arg, context=None):
        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):
            if ee.join_date:
                date_dt= datetime.strptime(ee.join_date, "%Y-%m-%d").date()
                today = datetime.today().date()
                tenure = relativedelta(today, date_dt)
                if tenure.years == 0:
                    res[ee.id] = "{0.months} month(s) {0.days} days ".format(tenure)
                else:
                    res[ee.id] = "{0.years} years {0.months} month(s) {0.days} days ".format(tenure)
        return res
    
    def _calculate_date_of_confirmation(self, cr, uid, ids, join_date, arg, context=None):
        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):
            if ee.join_date:
                date_dt= datetime.strptime(ee.join_date, "%Y-%m-%d").date()
                three_months = datetime.strftime(date_dt+relativedelta(months=+3),"%d/%m/%Y")
                res[ee.id] = three_months      
        return res
    
    def _calculate_date_of_one_year_completion(self, cr, uid, ids, join_date, arg, context=None):
        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):
            if ee.join_date:
                date_dt= datetime.strptime(ee.join_date, "%Y-%m-%d").date()
                three_months = datetime.strftime(date_dt+relativedelta(months=+12),"%d/%m/%Y")
                res[ee.id] = three_months      
        return res

    _columns = {
        'current_user':fields.many2one('res.users','Current User',size=32),
        'hro': fields.many2one('res.users','HR Officer',required=True, domain="[('is_hro', '=', True)]" ),
        'join_date': fields.date('Date Of Joining', help="Date of joining the company. It is used for annual leaves calculation."),
        'extension': fields.char('Extension', size=5, help='Internal phone number'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'parent_id2': fields.many2one('hr.employee', 'Reporting Manager2'),
        'parent_id3': fields.many2one('hr.employee', 'Reporting Manager3'),
        #'tenure': fields.function(_calculate_tenure, type='char', method=True, string = 'Tenure'),
        'date_of_confirmation': fields.function(_calculate_date_of_confirmation, type='char', method=True, string='Date Of Confirmation',store=True),
        'one_year_completion': fields.function(_calculate_date_of_one_year_completion, type='char', method=True, string='One Year Completion'),
        'status_of_confirmation': fields.char('Status of Confirmation'),
    }

    _defaults = {
        'current_user': lambda obj, cr, uid, ctx=None: uid,
        }
        
class res_users(osv.osv):
    _name = "res.users"
    _inherit = ["res.users"]
        
    _columns = {
        'is_hro' : fields.boolean('Is a HRO'),        
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
