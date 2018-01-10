# -*- coding: utf-8 -*-

from osv import fields,osv
import tools
import pooler
from tools.translate import _

from datetime import datetime,date,timedelta
import time
import math


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    
    _columns = {
        'join_date': fields.date('Employment date', help="Date of joining the company. It is used for annual leaves calculation."),
        'work_phone_ext': fields.char('Work Phone Extension', size=4, readonly=False),
        'mobile_phone': fields.char('Mobile HK', size=32, readonly=False),
        'mobile_phone_cn': fields.char('Mobile China', size=32, readonly=False),
        'mobile_phone_in': fields.char('Mobile India', size=32, readonly=False),
        'skype': fields.char('Skype ID', size=64, readonly=False),
        'init_leaves': fields.selection([
            ('1','Year 1 - 7 days'),
            ('2','Year 2 - 8 days'),
            ('3','Year 3 - 8 days'),
            ('4','Year 4 - 10 days'),
            ('5','Year 5 - 10 days'),
            ('6','Year 6 - 11 days'),
            ('7','Year 7 - 12 days'),
            ('8','Year 8 - 13 days'),
            ('9','Year 9 - 14 days'),
            ], 'Initial leaves'),
        'last_login': fields.related('user_id', 'login_date', type='datetime', string='Latest Connection', readonly=1),
        'image_medium_user': fields.related('user_id', 'image_medium', type='binary', string="User's medium-sized photo", readonly=0),
    }
        
    _defaults = {
        'init_leaves': '1',
    }
    
hr_employee()

class hr_holidays(osv.osv):
    _inherit = 'hr.holidays'
    
    _columns = {
        'join_date': fields.related('employee_id','join_date', string="Employment date", type='date', readonly=True, store=True),
        'init_leaves': fields.related('employee_id','init_leaves', string="Initial leaves", type='selection',
            selection=[ ('1','Year 1 - 7 days'),
                        ('2','Year 2 - 8 days'),
                        ('3','Year 3 - 8 days'),
                        ('4','Year 4 - 10 days'),
                        ('5','Year 5 - 10 days'),
                        ('6','Year 6 - 11 days'),
                        ('7','Year 7 - 12 days'),
                        ('8','Year 8 - 13 days'),
                        ('9','Year 9 - 14 days')], readonly=True, store=True),
        'state': fields.selection([ ('draft', 'To Submit'), 
                                    ('cancel', 'Cancelled'),
                                    ('confirm', 'To Approve'), 
                                    ('refuse', 'Rejected'), 
                                    ('validate1', 'Second Approval'), 
                                    ('validate', 'Approved')], 'Status', readonly=True, track_visibility='onchange',
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
        'year_nb': fields.char('Year #',size=64),
        
        }
        
    _defaults = {
        'date_from': lambda self, cr, uid, ctx: ctx.get('date', fields.date.context_today(self,cr,uid,context=ctx)) + " 01:00:00",
    }
    
    _track = {
        'state': {
            'hr_holidays.mt_holidays_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'validate',
            'hr_holidays.mt_holidays_refused': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'refuse',
            #'hr_holidays.mt_holidays_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
        },
    }
    
    _sql_constraints = [
        #('date_check', "CHECK ( number_of_days_temp < 100 )", "The number of days must be lesser than 100."),
        #('date_check', "CHECK ( number_of_days_temp >= 0 )", "The number of days must be greater than 0."),
    ]
    
    _order = "type desc, date_from desc"
    
    #def message_subscribe_users(self, cr, uid, ids, user_ids=None, subtype_ids=None, context=None):
        #""" Wrapper on message_subscribe, using users. If user_ids is not
            #provided, subscribe uid instead. """
            
        #if user_ids is None:
            #user_ids = [uid]
            
        ##ZEEVA mod start 2013-03-18
            ##TODO auto add bosses by group instead of name to allow future external user to approve a product
        #boss_id = self.pool.get('res.users').search(cr, uid, ['|','|','|','|',('login','=','akshay'),('login','=','nitin'),
                                                                    #('login','=','rita'),('login','=','vincent'),('login','=','admin')])
        #user_ids += boss_id
        ##ZEEVA mod stop 2013-03-18
        
        #partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, uid, user_ids, context=context)]
        #return self.message_subscribe(cr, uid, ids, partner_ids, subtype_ids=subtype_ids, context=context)
    
    def onchange_leave_type(self, cr, uid, ids, holiday_type_id, context=None):
        result = {}
        
        if holiday_type_id:
            holiday_type_obj = self.pool.get('hr.holidays.status').browse(cr, uid, holiday_type_id, context=None)
            name = holiday_type_obj.name
                    
            result = {'value': {'name': name}}
        
        return result
    
    def onchange_employee(self, cr, uid, ids, employee_id, holiday_type_id, context=None):
        # goal: return employee information, suggested nb of annual leaves
        
        result = {}
        join_date = ''  #join date of the selected employee
        init_leaves = ''
        nb_days = 0.0   #number of days for this AL allocation
        year_nb = ''    #description of the current year number (shown on screen as an help for HR officer)
        name = ''       #description of the AL allocation
        
        diff_table = [7, 8, 8, 10, 10, 11, 12, 13, 14]    #this table corresponds to [year1, year2,...year9] used for calculation
        
        if employee_id:
            employee_obj = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=None)
            
            if employee_obj.join_date:
                year_init = int(employee_obj.init_leaves) #initial leaves cursor in the table diff_table
                init_leaves = employee_obj.init_leaves
                join_date = employee_obj.join_date #employed since 
                date_since = datetime.strptime(employee_obj.join_date,'%Y-%m-%d') #convert join date into time format
                date_now = datetime.strptime(fields.date.context_today(self,cr,uid,context=context),'%Y-%m-%d') #date today
                
                year_delta = date_now.year - date_since.year +1 # current year number
                #ex: if employee joined in 2013, and now is 2013, employee is currently in year 1
            
                if holiday_type_id:
                    holiday_type_obj = self.pool.get('hr.holidays.status').browse(cr, uid, holiday_type_id, context=None)
                    name = holiday_type_obj.name + ' for ' + employee_obj.name
                    
                    #Allocation for this year = accumulation of past year, or part of it if year1
                    if holiday_type_obj.name.count(str(date_now.year)):
                        year_nb = 'In %d, %s is in YEAR ' % (date_now.year, employee_obj.name) + str(year_init -1 + year_delta)
                        
                        #new comers
                        if year_delta == 1 and date_since.month >=10: #no alloc
                            raise osv.except_osv(_('Warning!'),_('Employee joined this year on or after October, please allocate the leaves to next year.'))
                        
                        elif year_delta == 1: #year 1: prorata of year_init
                            next_01_01 = "%s-01-01" % int(date_since.year +1)
                            nb_days = round((datetime.strptime(next_01_01,'%Y-%m-%d') - date_since).days * diff_table[year_init-1]/ 365.0 , 1)
                        
                        elif year_init -1 + year_delta -1 < 9:
                            nb_days = diff_table[year_init -1 + year_delta -1]
                            
                        else:
                            nb_days = diff_table[8]
                    
                    #Allocation for next year
                    elif holiday_type_obj.name.count(str(date_now.year +1)):
                        year_nb = 'In %d, %s will be in YEAR ' % (date_now.year +1, employee_obj.name) + str(year_init -1 + year_delta +1)
                        
                        #new comers
                        if year_delta == 1 and date_since.month >=10: #prorata current year + next year
                            next_01_01 = "%s-01-01" % int(date_since.year +1)
                            nb_days = round((datetime.strptime(next_01_01,'%Y-%m-%d') - date_since).days * diff_table[year_init-1]/ 365.0 , 1)
                            
                            nb_days += diff_table[year_init-1 +1]
                            
                        elif year_init-1 + year_delta-1 +1 < 9:
                            nb_days = diff_table[year_init-1 + year_delta-1 +1]
                            
                        else:
                            nb_days = diff_table[8]
                
            else:
                year_nb = 'No employment date defined for this employee.'
                
            result = {'value': {'join_date': join_date,
                                'init_leaves': init_leaves,
                                'number_of_days_temp': nb_days,
                                'year_nb': year_nb,
                                'name': name}}
        
        return result
        
    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 10 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=10)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0

        return result
        
    def holidays_confirm(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        
        for record in self.browse(cr, uid, ids, context=context):
            subscribe_ids = []
            
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                subscribe_ids = record.employee_id.parent_id.user_id.id
                            
            subscribe_ids += self.pool.get('res.users').search(cr, uid, [('login','in',['akshay','nitin','admin','doris'])])
            subscribe_ids.append( record.employee_id.user_id.id)
            
            self.message_subscribe_users(cr, uid, [record.id], user_ids=subscribe_ids, context=context)
            
            if record.type == 'remove':
                message = _("<b>Leave request</b> created and waiting for approval")
                self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            
            if record.type == 'add':
                message = _("<b>Leave Allocation</b> created and waiting for approval")
                self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            
        return self.write(cr, uid, ids, {'state': 'confirm'})
        
        
hr_holidays()

class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    
    _order = "name"
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if not record.limit:
                if record.max_leaves:
                    name = name + ('  ( %.1f / %.1f )' % (record.leaves_taken or 0.0, record.max_leaves or 0.0))
            res.append((record.id, name))
        return res

hr_holidays_status()

class hr_expense_expense(osv.osv):
    
    _inherit = "hr.expense.expense"
    
    _columns = {
        'date_given': fields.date('Check Given Date', select=True, help="Date when the check was given by the accountant."),
        'user_given': fields.many2one('res.users', 'Check Given By'),
        'date_received': fields.date('Check Received Date', select=True, help="Date when the check was received by the employee."),
        'user_received': fields.many2one('res.users', 'Check Received By'),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('accepted', 'Approved'),
            ('check_given','Check given'),
            ('check_received','Check received'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
            ],
            'Status', readonly=True, track_visibility='onchange',
            help='When the expense request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the status is \'Waiting Confirmation\'.\
            \nIf the admin accepts it, the status is \'Accepted\'.\n If the accounting entries are made for the expense request, the status is \'Waiting Payment\'.'),
    }
    #TODO
    
    def expense_confirm(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            user_ids = []
            if expense.employee_id and expense.employee_id.parent_id.user_id:
                user_ids = [expense.employee_id.parent_id.user_id.id]
                
            accountant_id = self.pool.get('res.users').search(cr, uid, [('login','=','vincent')])
            user_ids += accountant_id
            self.message_subscribe_users(cr, uid, [expense.id], user_ids=user_ids)
        return self.write(cr, uid, ids, {'state': 'confirm', 'date_confirm': time.strftime('%Y-%m-%d')}, context=context)

    def expense_accept(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            boss_ids = self.pool.get('res.users').search(cr, uid, [('login','in',['nitin','akshay'])])
            self.message_subscribe_users(cr, uid, [expense.id], user_ids=boss_ids)
        return self.write(cr, uid, ids, {'state': 'accepted', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
        
    def expense_check_given(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'check_given', 'date_given': time.strftime('%Y-%m-%d'), 'user_given': uid}, context=context)
        
    def expense_check_received(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'check_received', 'date_received': time.strftime('%Y-%m-%d'), 'user_received': uid}, context=context)
    
hr_expense_expense()

class hr_expense_line(osv.osv):
    _inherit = "hr.expense.line"
    
    _columns = {
    }
    
    def onchange_date(self, cr, uid, ids, date_value, context=None):
        result = {}
        
        if date_value:
            date_since = datetime.strptime(date_value,'%Y-%m-%d')
            date_now = datetime.strptime(fields.date.context_today(self,cr,uid,context=context),'%Y-%m-%d')
            
            date_delta = (date_now - date_since).days
            
            if (date_delta > 7) and (uid != 1):
                result = {'value': {'date_value': ''},
                          'warning':{
                                        'title': _(' Expense overdue!'),
                                        'message' : _('The selected date is more than 7 days. Please contact your manager to proceed with this expense.')
                                    }
                }
        return result
        
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        res = {}
        
        context = context or {}
        res = super(hr_expense_line, self).onchange_product_id(cr, uid, ids, product_id, context)
        
        if res:
            res['name'] = ''
            res['unit_amount'] = 0.0
        
        return {'value': res}
        
hr_expense_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


